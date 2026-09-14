# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original extraction/merge logic only; upstream preset data retains Apache-2.0.
"""Read the pinned upstream's exact matrix/curve arrays without executing it."""
import copy
import hashlib
import json
from pathlib import Path
import re

EXPECTED_HOOK = '2db88c8e42311c587ca8304c2c8ed7d70592ee988ee154327ed5503b107723ae'
UPSTREAM_REVISION = '7c565898562c73c5073c54dfc831c8c3df9c24cf'
RICOH = (
    ('pos', 'ricoh-positive', '理光 GR 正片', 'Positive Film'),
    ('neg', 'ricoh-negative', '理光 负片', 'Negative Film'),
    ('hcbw', 'ricoh-hcbw', '理光 高反差黑白', 'High Contrast B&W'),
    ('daido', 'ricoh-daido', '理光 森山风', 'Moriyama Daido Style'),
    ('xpro', 'ricoh-cross', '理光 正负逆冲', 'Cross Process'),
)


def read_array(text, label, width, count):
    pattern = (r'^\s*:' + re.escape(label) + r'\s*\n\s*\.array-data '
               + str(width) + r'\s*\n(.*?)^\s*\.end array-data')
    found = re.findall(pattern, text, re.M | re.S)
    if len(found) != 1:
        raise ValueError('Expected one array: ' + label)
    words = re.sub(r'#[^\n]*', '', found[0]).split()
    if not all(re.fullmatch(r'-?0x[0-9a-fA-F]+t?' if width == 1
                            else r'-?0x[0-9a-fA-F]+', word) for word in words):
        raise ValueError('Unexpected array data: ' + label)
    values = [int(word.removesuffix('t'), 16) for word in words]
    if len(values) != count:
        raise ValueError('Wrong array length: ' + label)
    return values


def ricoh_profiles(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_HOOK:
        raise ValueError('Hook hash mismatch: use the pinned upstream revision')
    text = data.decode('utf-8')
    profiles = []
    for token, preset_id, name, reference in RICOH:
        values = read_array(text, f'array_{token}_matrix', 4, 9)
        raw = read_array(text, f'array_gamma_{token}', 1, 2048)
        if not all(0 <= b <= 255 for b in raw):
            raise ValueError('Invalid gamma byte: ' + token)
        gamma = [raw[i] | raw[i+1] << 8 for i in range(0, 2048, 2)]
        if not all(0 <= v <= 1023 for v in gamma) or any(a > b for a, b in zip(gamma, gamma[1:])):
            raise ValueError('Invalid gamma curve: ' + token)
        profiles.append(dict(
            id=preset_id, name=name, family='ricoh', reference_name=reference,
            guide=reference + ' / 上游理光风格；100%保留原参数，非理光官方LUT。',
            matrix=[values[i:i+3] for i in range(0, 9, 3)], gamma=gamma,
            source='bonyback1/sony-pmca-ricoh-mod', source_revision=UPSTREAM_REVISION,
            source_sha256=EXPECTED_HOOK, source_license='Apache-2.0',
        ))
    return profiles


# The live view is rendered by the camera itself, and the camera renders two
# things live: its Creative Style and its own Picture Effect. The RGB matrix
# plus extended gamma table *is* the film look, but some bodies answer both
# capability queries with false and then drop those writes silently, leaving
# the viewfinder untouched. On those bodies applyNative falls back to the two
# looks the camera owns, so every preset needs a pair here.
#
# Both halves are the tokens this app generation already ships:
#   * modes  -> CreativeStyleController constants in the base APK
#   * effects-> picture-effect ItemIds in the base APK's assets/MenuData.xml
# Only the styles and effects of this camera generation are used, so a body
# that predates the newer Creative Look names still accepts them. The result is
# an approximation by construction: it is what the camera can draw live.
NATIVE_LOOK = {
    'pop-color': ('standard', None),
    'fuji-velvia': ('vivid', 'pop-color'),
    'fuji-astia': ('portrait', None),
    'fuji-chrome': ('neutral', None),
    'fuji-reala': ('standard', None),
    'fuji-proneg': ('neutral', None),
    'fuji-negative': ('neutral', 'retro-photo'),
    'fuji-eterna': ('neutral', None),
    'fuji-bleach': ('neutral', 'retro-photo'),
    'fuji-acros': ('mono', 'richtone-mono'),
    'ricoh-positive': ('standard', None),
    'ricoh-negative': ('portrait', 'retro-photo'),
    'ricoh-hcbw': ('mono', 'richtone-mono'),
    'ricoh-daido': ('mono', 'rough-mono'),
    'ricoh-cross': ('vivid', 'pop-color'),
    # Leica looks. Only this camera generation's tokens can be used, so several
    # presets necessarily share one live-view look: leica-natural joins the
    # standard-style group and leica-classic the neutral + retro-photo group.
    'leica-classic': ('neutral', 'retro-photo'),
    'leica-natural': ('standard', None),
}
NATIVE_MODES = {'standard', 'vivid', 'neutral', 'portrait', 'mono'}
NATIVE_EFFECTS = {'pop-color', 'retro-photo', 'richtone-mono', 'rough-mono'}


def native_look(preset_id):
    """(Creative Style token, Picture Effect token or None) for one preset."""
    mode, effect = NATIVE_LOOK[preset_id]
    if mode not in NATIVE_MODES:
        raise ValueError('Unsupported creative style token: ' + mode)
    if effect is not None and effect not in NATIVE_EFFECTS:
        raise ValueError('Unsupported picture effect token: ' + str(effect))
    return mode, effect


FUJIFILM_PRESETS = 10
RICOH_PRESETS = 5
LEICA_PRESETS = 2
# Every preset needs an id and a live-view look, and the total is derived so a
# new family cannot leave a stale count behind in this file or in the checks.
PRESET_COUNT = FUJIFILM_PRESETS + RICOH_PRESETS + LEICA_PRESETS
LEICA_FILE = 'profiles/leica_look_approx.json'


def leica_profiles(path, white):
    """The fitted Leica looks for one white-point treatment.

    The package ships no neutral reference, so the fit is against a baseline this
    project constructs; the two treatments differ only in the fitted tone
    curve's output scale (see tools/fit_leica.py).
    """
    if white not in ('faithful', 'anchor'):
        raise ValueError('Unknown Leica white-point treatment: ' + str(white))
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    presets = copy.deepcopy(data['variants'][white])
    if len(presets) != LEICA_PRESETS:
        raise ValueError(f'Expected {LEICA_PRESETS} Leica presets, found {len(presets)}')
    return presets


def combined_profiles(fuji, upstream_hook, leica=None):
    if len(fuji) != FUJIFILM_PRESETS:
        raise ValueError('Expected the existing ten Fujifilm-reference profiles')
    profiles = copy.deepcopy(fuji)
    for p in profiles:
        p['family'] = 'fujifilm'
        p['name'] = '富士 ' + p['name']
        p['guide'] = p['official_film'] + ' / 富士官方LUT近似；需实拍校准。'
    profiles += ricoh_profiles(upstream_hook)
    profiles += leica or []
    if len({p['id'] for p in profiles}) != PRESET_COUNT:
        raise ValueError('Preset IDs must be unique; keep existing preset IDs for upgrades')
    if {p['id'] for p in profiles} != set(NATIVE_LOOK):
        raise ValueError('Every preset needs a live-view fallback look')
    for p in profiles:
        mode, effect = native_look(p['id'])
        p['native'] = {'mode': mode, 'picture_effect': effect}
    return profiles
