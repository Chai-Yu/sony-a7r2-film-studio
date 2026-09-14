#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Correct the fitted Fujifilm chroma for the domain the camera actually feeds.

The fit maps `flat neutral rendering -> film look`, because the official neutral
LUT is the only reference Fujifilm publishes. A camera never produces that flat
rendering: it hands the RGB matrix its own Standard rendering, which is more
chromatic. A matrix's chroma gain barely depends on the input's chroma, so the
gain fitted against the flat reference lands on top of an already more
saturated input and overshoots by that ratio.

  camera Standard chroma                         0.1023
  official PROVIA chroma (the target)            0.1305
  model, raw matrix, at 100%                     0.1843   (= 1.8016 x 0.1023)
  -> the chroma response has to come down by      0.1305 / 0.1843 = 0.708

The criterion is the direct one: at 100% strength a filter should render the
reference look, so its output chroma has to equal the official LUT's on the same
scene. The factor is not the naive chroma ratio, because the shared tone curve is
nonlinear and the Q10 rounding of the matrix adds a small floor. Measured on the
same triple, the 100% gain over the camera Standard comes out as:

  factor 0.600 -> 1.1327      factor 0.680 -> 1.2756   <- target 1.2757
  factor 0.640 -> 1.2048      factor 0.700 -> 1.3115
  factor 0.660 -> 1.2407      factor 0.760 -> 1.4156

so 0.680 is the value that lands on the target; it is essentially linear in the
neighbourhood (1.768 per unit factor).

Measured on an a7R II, three aligned shots of one scene, with the scene code
recovered by inverting the neutral LUT - 99.7% of pixels invert to below 2e-3,
median 5.3e-4, so the camera's flat rendering is consistent with the official
neutral. See docs/VALIDATION.md, 2026-09-14.

The response is scaled through the neutral projector, not by blending towards
the identity. Blending would move a desaturating look the wrong way and would
turn ACROS - whose matrix is zero on the chroma plane - back into colour.
Writing `A` for the projector onto the neutral direction (every row 1/3):

  M' = A + factor * (M - A)

keeps every row sum at 1 (so the neutral axis still maps to itself) and scales
`M c` by `factor` for every chroma `c`, which is exactly what the excess input
chroma does - uniformly, whether the look adds colour or removes it.

This is a correction for one measured camera, applied to the Fujifilm family,
whose baseline is Fujifilm's own flat reference. The Ricoh family is left alone
because those parameters come from upstream and were tuned against real bodies.

Re-running is safe: the tool always recomputes from the uncalibrated matrices it
keeps in the file.
"""
from pathlib import Path
import argparse
import json

# Measured 2026-09-14 on an a7R II; see the module docstring and VALIDATION.md.
CAMERA_STANDARD_OVER_FLAT = 1.260        # chroma, three independent measurements
REFERENCE_GAIN_OVER_STANDARD = 1.2757    # sat(official PROVIA) / sat(camera Standard)
FITTED_GAIN_OVER_STANDARD = 1.8016       # the model at 100%, verified against the camera
TARGET_GAIN_OVER_STANDARD = REFERENCE_GAIN_OVER_STANDARD
# Solved, not computed: gain = 1.768 * factor + 0.07, so the naive chroma ratio
# 1.2757 / 1.8016 = 0.708 overshoots. 0.680 lands the 100% gain on 1.2756.
DEFAULT_FACTOR = 0.680
NEUTRAL_ROW = [1024 / 3] * 3


def blend(matrix, factor):
    """A + factor * (matrix - A), rounded to Q10, rows still summing to 1024."""
    row_out = []
    for row in matrix:
        scaled = [round(neutral + factor * (value - neutral))
                  for value, neutral in zip(row, NEUTRAL_ROW)]
        scaled[2] = 1024 - scaled[0] - scaled[1]
        row_out.append(scaled)
    return row_out


def chroma_gain(matrix, samples):
    """How much chroma the matrix adds, averaged over a set of directions."""
    import numpy as np
    m = np.asarray(matrix, dtype=float) / 1024
    out = samples @ m.T
    return float((out.max(1) - out.min(1)).mean() / (samples.max(1) - samples.min(1)).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir', type=Path)
    ap.add_argument('--factor', type=float, default=DEFAULT_FACTOR,
                    help=f'Scale applied to each matrix\'s chroma response. '
                         f'Default {DEFAULT_FACTOR:.3f}, solved so that at 100% strength '
                         f'the output chroma equals the official look\'s on the measured '
                         f'scene (target gain {REFERENCE_GAIN_OVER_STANDARD} over the '
                         f'camera Standard; raw model gives {FITTED_GAIN_OVER_STANDARD}).')
    ap.add_argument('--clear', action='store_true',
                    help='Remove the calibration and restore the raw fitted matrices')
    args = ap.parse_args()
    path = args.project_dir / 'profiles/fuji_official_approx.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    presets = data['presets']

    print(f'chroma factor {args.factor:.4f}')
    print(f'{"film":16s} {"fit":>8s} {"shipped":>9s} {"change":>8s}')
    for preset in presets:
        raw = preset.get('matrix_fit') or preset['matrix']
        preset['matrix_fit'] = [row[:] for row in raw]
        if args.clear:
            preset['matrix'] = [row[:] for row in raw]
            continue
        preset['matrix'] = blend(raw, args.factor)

    if args.clear:
        data.pop('domain_calibration', None)
    else:
        data['domain_calibration'] = dict(
            reason='the fit baseline is a flat reference, the camera feeds a rendered '
                   'Standard image that is more chromatic',
            measured_on='Sony a7R II, 2026-09-14, three shots of one scene',
            camera_standard_over_flat_chroma=CAMERA_STANDARD_OVER_FLAT,
            reference_gain_over_standard_chroma=REFERENCE_GAIN_OVER_STANDARD,
            fitted_gain_over_standard_chroma=FITTED_GAIN_OVER_STANDARD,
            target_gain_over_standard_chroma=round(TARGET_GAIN_OVER_STANDARD, 4),
            chroma_factor=round(args.factor, 6),
            applies_to='fujifilm (the Leica family uses a constructed baseline and has '
                       'not been measured this way; Ricoh comes from upstream)',
            detail='docs/VALIDATION.md, 2026-09-14')

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    import numpy as np
    rng = np.random.default_rng(4)
    level = rng.uniform(0.2, 0.9, (20000, 1))
    direction = rng.normal(0, 1, (20000, 3))
    direction -= direction.mean(1, keepdims=True)
    direction /= np.abs(direction).max(1, keepdims=True)
    samples = np.clip(level * (1 + 0.08 * direction), 0.01, 1.0)

    for preset in presets:
        gain_fit = chroma_gain(preset['matrix_fit'], samples)
        gain_shipped = chroma_gain(preset['matrix'], samples)
        print(f'{preset["id"]:16s} {gain_fit:8.3f} {gain_shipped:9.3f} '
              f'{gain_shipped - gain_fit:+8.3f}')
    print(f'wrote {path.relative_to(args.project_dir)}')


if __name__ == '__main__':
    main()
