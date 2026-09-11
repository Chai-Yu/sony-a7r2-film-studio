#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Verify strength endpoints, neutral preservation and curve safety."""
import json
from pathlib import Path
from filter_strength import blend_profile, STRENGTHS

ROOT = Path(__file__).resolve().parents[1]


def main():
    profiles = json.loads((ROOT/'profiles/fuji_official_approx.json').read_text())['presets']
    for p in profiles:
        assert blend_profile(p, 100) == {k: p[k] for k in ('matrix', 'gamma')}, p['id']
        assert blend_profile(p, 0) == {
            'matrix': [[1024, 0, 0], [0, 1024, 0], [0, 0, 1024]],
            'gamma': list(range(1024)),
        }
        previous_distance = -1
        for strength in STRENGTHS:
            b = blend_profile(p, strength)
            assert all(sum(row) == 1024 for row in b['matrix'])
            assert len(b['gamma']) == 1024 and 0 <= min(b['gamma']) <= max(b['gamma']) <= 1023
            assert all(a <= z for a, z in zip(b['gamma'], b['gamma'][1:]))
            distance = sum(abs(value-i) for i, value in enumerate(b['gamma']))
            for i in range(3):
                for j in range(3):
                    neutral = 1024 if i == j else 0
                    expected = neutral+(p['matrix'][i][j]-neutral)*strength/100
                    assert abs(b['matrix'][i][j]-expected) <= 1.00001
                    distance += abs(b['matrix'][i][j]-neutral)
            assert distance >= previous_distance
            previous_distance = distance
    report = dict(profiles=len(profiles), strengths=list(STRENGTHS), checks=[
        '100% bit-identical to previous full-strength profile', '0% mathematical identity endpoint',
        'neutral-preserving matrix rows', 'curves monotonic and within 10-bit bounds',
        'interpolation within quantization tolerance', 'parameter distance from identity increases with strength',
    ], runtime_verified=False)
    (ROOT/'validation/strength-static.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
