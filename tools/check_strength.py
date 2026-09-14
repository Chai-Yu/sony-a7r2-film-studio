#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Verify strength endpoints, neutral preservation and curve safety."""
import json
from pathlib import Path
from film_profiles import PRESET_COUNT
from filter_strength import blend_profile, is_monochrome, STRENGTHS

ROOT = Path(__file__).resolve().parents[1]


def main():
    profiles = json.loads((ROOT/'profiles/film_studio.json').read_text(encoding='utf-8'))['presets']
    assert len(profiles) == PRESET_COUNT
    for p in profiles:
        assert blend_profile(p, 100) == {k: p[k] for k in ('matrix', 'gamma')}, p['id']
        identity = {'matrix': [[1024, 0, 0], [0, 1024, 0], [0, 0, 1024]],
                    'gamma': list(range(1024))}
        if is_monochrome(p):
            # The matrix of a black-and-white look is not interpolated, so 0%
            # keeps it and only the tone curve becomes the identity.
            assert blend_profile(p, 0) == {'matrix': p['matrix'],
                                           'gamma': identity['gamma']}, p['id']
        else:
            assert blend_profile(p, 0) == identity, p['id']
        mono = is_monochrome(p)
        previous_distance = -1
        for strength in STRENGTHS:
            b = blend_profile(p, strength)
            if mono:
                # A black-and-white look keeps its matrix at every strength, so
                # no strength can put colour back into it.
                assert b['matrix'] == p['matrix'], (p['id'], strength)
                assert is_monochrome(dict(matrix=b['matrix'])), (p['id'], strength)
            for original, blended in zip(p['matrix'], b['matrix']):
                if sum(original) == 1024:
                    assert sum(blended) == 1024
                else:
                    expected_sum = 1024 + (sum(original)-1024)*strength/100
                    assert abs(sum(blended)-expected_sum) <= 1.5
            assert len(b['gamma']) == 1024 and 0 <= min(b['gamma']) <= max(b['gamma']) <= 1023
            assert all(a <= z for a, z in zip(b['gamma'], b['gamma'][1:]))
            distance = sum(abs(value-i) for i, value in enumerate(b['gamma']))
            for i in range(3):
                for j in range(3):
                    neutral = 1024 if i == j else 0
                    if not mono:
                        expected = neutral+(p['matrix'][i][j]-neutral)*strength/100
                        assert abs(b['matrix'][i][j]-expected) <= 1.00001
                    distance += abs(b['matrix'][i][j]-neutral)
            assert distance >= previous_distance
            previous_distance = distance
    report = dict(profiles=len(profiles), strengths=list(STRENGTHS), checks=[
        '100% bit-identical to previous full-strength profile', '0% mathematical identity endpoint',
        'neutral rows preserved; intentional upstream tints interpolated',
        'black-and-white looks stay achromatic at every strength (curve only)',
        'curves monotonic and within 10-bit bounds',
        'interpolation within quantization tolerance', 'parameter distance from identity increases with strength',
    ], runtime_verified=False)
    (ROOT/'validation/strength-static.json').write_text(json.dumps(report, indent=2),encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
