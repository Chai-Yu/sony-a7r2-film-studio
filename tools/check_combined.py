#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original verification logic only; third-party rights remain separate.
"""Check arrays and menu IDs after round-trip decompilation of the built APK."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from film_profiles import read_array, ricoh_profiles
from filter_strength import STRENGTHS, blend_profile

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = 'smali/com/yuki/imaging/app/pictureeffectplus/shooting/camera/RicohHook.smali'


def fields(text):
    links = re.findall(
        r'fill-array-data v1, :(\w+)\s+sput-object v1, [^\n]+->(sFuji\w+):(\[[IB])', text)
    result = {}
    for label, name, kind in links:
        data = read_array(text, label, 1 if kind == '[B' else 4, 2048 if kind == '[B' else 9)
        result[name] = [v & 255 for v in data] if kind == '[B' else data
    if len(result) != len(links):
        raise ValueError('Duplicate initialized fields')
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--decoded', type=Path, required=True,
                    help='Fresh apktool d -r output from the final signed APK')
    ap.add_argument('--upstream-hook', type=Path, required=True)
    ap.add_argument('--previous-decoded', type=Path,
                    help='Optional decoded 0.1.3 build, to compare existing arrays')
    args = ap.parse_args()
    profiles = json.loads((ROOT/'profiles/film_studio.json').read_text())['presets']
    hook = (args.decoded/HOOK_PATH).read_text()
    arrays = fields(hook)
    assert len(profiles) == 15 and len(arrays) == 120
    for i, p in enumerate(profiles):
        for strength in STRENGTHS:
            expected = blend_profile(p, strength)
            assert arrays[f'sFujimatrix{i}_{strength}'] == sum(expected['matrix'], [])
            raw = [b for v in expected['gamma'] for b in (v & 255, v >> 8)]
            assert arrays[f'sFujigamma{i}_{strength}'] == raw
    # Independent upstream input: verify both tinted and neutral presets retain
    # exact original values in the built DEX at the 100% endpoint.
    for i, p in enumerate(ricoh_profiles(args.upstream_hook), 10):
        assert profiles[i]['id'] == p['id']
        assert arrays[f'sFujimatrix{i}_100'] == sum(p['matrix'], [])
        assert arrays[f'sFujigamma{i}_100'] == [b for v in p['gamma'] for b in (v & 255, v >> 8)]
    menu = ET.parse(args.decoded/'assets/MenuData.xml')
    top = next(e for e in menu.iter() if e.get('ItemId') == 'ApplicationTop')
    ids = [p['id'] for p in profiles]
    assert [e.get('ItemId') for e in top] == ids
    assert [e.get('Value') for e in top] == ids
    for method in ['getPresetIds', 'getRGBMatrix', 'getGammaBytes', 'getFilterName', 'getFilterGuide']:
        body = re.search(r'^\.method [^\n]* ' + method + r'\([^\n]*\n(.*?)^\.end method', hook, re.M | re.S)
        assert body, method
        for preset_id in ids:
            assert '"' + preset_id + '"' in body[1], (method, preset_id)
    movie = (args.decoded/'smali/com/sony/imaging/app/base/shooting/movie/trigger/MovieRecStandbyStateKeyHandler.smali').read_text()
    assert 'pushedCenterKey()I' in movie and '"ApplicationTop"' in movie
    assert '->isMovieRecording()Z' in movie
    assert '->isMovieRecording()Z' in hook
    resources = (args.decoded/'resources.arsc').read_bytes()
    assert '胶片工坊'.encode() in resources
    for old in ['理光相机', '富士风格']:
        assert old.encode() not in resources and old.encode('utf-16-le') not in resources
    previous_count = None
    if args.previous_decoded:
        previous = fields((args.previous_decoded/HOOK_PATH).read_text())
        assert len(previous) == 80
        for field, values in previous.items():
            assert arrays[field] == values, field
        previous_count = len(previous)
    report = dict(
        profiles=15, strengths=list(STRENGTHS), compiled_arrays_checked=len(arrays),
        upstream_ricoh_full_strength_exact=True, previous_fuji_arrays_unchanged=previous_count,
        menu_and_lookup_ids_match=True, renamed_resources=True,
        movie_standby_shortcut_present=True, hardware_verified=False,
    )
    (ROOT/'validation/combined-static.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
