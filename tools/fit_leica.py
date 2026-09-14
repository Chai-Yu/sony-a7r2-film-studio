#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Fit bounded matrix + common 10-bit curve approximations to the Leica Look LUTs.

Unlike the Fujifilm family, the Leica package ships no neutral reference, so the
baseline is constructed here instead of read from a second official LUT:

  scene            LSR, linear scene reflection, from the L-Log curve that Leica
                   publishes in its L-Log reference manual (verified below
                   against the manual's own LSR/DV table)
  baseline         BT.709 OETF of LSR clamped to diffuse white

Which display encoding sits under the LUT was not assumed: BT.709 OETF, gamma
2.4, gamma 2.2 and plain linear were each tested as the baseline, and the
criterion was that a look deviates from its neutral by a roughly constant
factor. BT.709 OETF keeps that factor within 1.34x over the whole range; every
other candidate swings 3.6-5.1x, which is the signature of the wrong curve.

The LUTs render diffuse white (LSR 1.0) at about 0.75, reserving roughly a
quarter of the display range for headroom above it. That is a property of a
LUT built for log footage, not of the look, and it cannot be reproduced on a
camera whose signal is already clipped at diffuse white. Both treatments are
therefore produced and emitted, and the caller picks one:

  faithful   keep the LUT's own tone mapping; the filter darkens the image
  anchor     scale the target by its own white so input 1.0 maps to 1.0 and only
             the look's colour and mid-tone character survive

Neither is Leica's own reference rendering; both are this project's construction
and are labelled as such in docs/SOURCES.md and docs/VALIDATION.md.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np

from fit_luts import apply_model, refine_row, sample, read_cube, write_cube

# L-Log, LSR <-> code, from Leica's L-Log reference manual section 3.1/3.2.
A, B, C, D, E, F = 8.0, 0.09, 0.27, 1.3, 0.0115, 0.6

LOOKS = [
    ('Classic', 'leica-classic', '徕卡 经典', 'Leica Look Classic (Film V6.3)'),
    ('Natural', 'leica-natural', '徕卡 自然', 'Leica Look Natural (Modern V6.2)'),
]

# The manual's table 1, LSR -> 10-bit digital value. The implementation below is
# only trusted because it reproduces every one of these to within a code value.
MANUAL_TABLE = ((0.00, 92), (0.02, 220), (0.18, 445), (0.90, 634),
                (4.07, 814), (23.30, 1023))


def lsr_to_code(lsr):
    lsr = np.asarray(lsr, dtype=np.float64)
    toe = A * lsr + B
    log = C * np.log10(D * lsr + E) + F
    return np.where(lsr <= 0.006, toe, log)


def code_to_lsr(code):
    code = np.asarray(code, dtype=np.float64)
    toe = (code - B) / A
    log = (10.0 ** ((code - F) / C) - E) / D
    return np.where(code <= 0.1380, toe, log)


def bt709_oetf(x):
    x = np.clip(x, 0, 1)
    return np.where(x < 0.018, 4.5 * x, 1.099 * x ** 0.45 - 0.099)


def baseline(v):
    """This project's constructed neutral: BT.709 tone curve of scene light."""
    return bt709_oetf(np.clip(code_to_lsr(v), 0, 1))


def verify_curve():
    """Refuse to fit unless the L-Log implementation matches Leica's own table."""
    worst = 0.0
    for lsr, dv in MANUAL_TABLE:
        worst = max(worst, abs(lsr_to_code(lsr) * 1023 - dv))
    assert worst < 2.0, f'L-Log implementation disagrees with the manual by {worst:.1f} DV'
    return worst


def fit(lut, base_x, target):
    """Curve first, then the matrix, exactly as the Fujifilm family is fitted."""
    q = np.linspace(0, 1, 1024)
    grey_v = np.linspace(0.1380, 0.6320, 4096)
    grey_base = baseline(grey_v)
    keep = np.r_[True, np.diff(grey_base) > 1e-9]
    grey_y = np.maximum.accumulate(sample(lut, np.repeat(grey_v[:, None], 3, axis=1)).mean(1))[keep]
    curve = np.clip(np.interp(q, grey_base[keep], grey_y), 0, 1)
    cy, ids = np.unique(curve, return_index=True)
    linear_target = np.interp(target, cy, q[ids])
    design = base_x[:, :2] - base_x[:, 2:3]
    matrix = np.empty((3, 3))
    for c in range(3):
        coeff = np.linalg.lstsq(design, linear_target[:, c] - base_x[:, 2], rcond=None)[0]
        matrix[c] = [coeff[0], coeff[1], 1 - coeff.sum()]
        matrix[c] = refine_row(base_x, target[:, c], curve, matrix[c])
    matrix_i = np.rint(matrix * 1024).astype(int)
    matrix_i[:, 2] = 1024 - matrix_i[:, :2].sum(1)
    assert matrix_i.min() >= -2048 and matrix_i.max() <= 3072, 'matrix out of bounds'
    curve_i = np.rint(curve * 1023).astype(int)
    assert np.all(np.diff(curve_i) >= 0), 'curve is not monotonic'
    return matrix_i, curve_i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lut_dir', type=Path, help='Folder with the Leica Look .cube files')
    ap.add_argument('project_dir', type=Path)
    args = ap.parse_args()
    root = args.project_dir
    (root / 'profiles').mkdir(parents=True, exist_ok=True)

    print(f'L-Log curve vs the manual table: worst deviation {verify_curve():.2f} DV')

    rng = np.random.default_rng(5101)
    lo_v, hi_v = 0.1500, 0.6250                  # inside (LSR = 0, diffuse white)
    v = rng.uniform(lo_v, hi_v, (120000, 3))
    x = baseline(v)
    mask = (x.min(1) > 0.015) & (x.max(1) < 0.985)
    v, x = v[mask], x[mask]
    cut = int(len(v) * 0.8)
    train_v, valid_v = v[:cut], v[cut:]
    train_x, valid_x = x[:cut], x[cut:]
    print(f'train {len(train_x)}  validation {len(valid_x)} samples')

    variants = {}
    metrics = []
    for token, preset_id, name, reference in LOOKS:
        source = args.lut_dir / token / f'{token}_Rec709.cube'
        cube = read_cube(source)
        target = sample(cube, train_v)
        valid_y = sample(cube, valid_v)
        matrix_i, curve_i = fit(cube, train_x, target)
        pred = apply_model(valid_x, matrix_i / 1024, curve_i / 1023)
        error = np.abs(pred - valid_y)
        metrics.append(dict(family='leica', look=token, samples=len(valid_y),
                            rgb_mae=float(error.mean()),
                            rgb_p95=float(np.quantile(error, .95)),
                            response_at_white=float(curve_i[-1] / 1023)))
        print(f'  faithful {token:8s} MAE {error.mean():.4f}  p95 {np.quantile(error, .95):.4f}'
              f'  white at {curve_i[-1] / 1023:.3f}')
        # 'anchor' is the same fit with one deliberate change: the tone curve's
        # output is normalised so the model maps input 1.0 to 1.0. Scaling the
        # target before fitting instead (the obvious approach) distorts the
        # relationship and costs about 3x accuracy, so the matrix is kept as
        # fitted and only the curve is rescaled.
        anchored = np.clip(np.rint(curve_i * (1023 / curve_i[-1])).astype(int), 0, 1023)
        assert np.all(np.diff(anchored) >= 0), 'anchored curve is not monotonic'
        assert anchored[-1] == 1023
        gain = 1023 / curve_i[-1]
        variants['faithful'] = variants.get('faithful', []) + [dict(
            id=preset_id, name=name, family='leica', official_film=token,
            reference_name=reference, white_point='faithful',
            guide=reference + ' / 由官方 L-Log LUT 拟合；非徕卡官方预设，需实拍校准。',
            source_file=source.name,
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            matrix=matrix_i.tolist(), gamma=curve_i.tolist())]
        variants['anchor'] = variants.get('anchor', []) + [dict(
            id=preset_id, name=name, family='leica', official_film=token,
            reference_name=reference, white_point='anchor',
            guide=reference + ' / 保留白点的变体（色调输出归一化）；非徕卡官方预设。',
            source_file=source.name,
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            matrix=matrix_i.tolist(), gamma=anchored.tolist())]
        print(f'  anchor   {token:8s} same matrix, curve output scaled x{gain:.3f} '
              f'so input 1.0 -> 1.0')

    out = dict(
        schema=1,
        family='leica',
        source='Leica SL2-S Leica Look Up Tables (LUT), Rec709 variant',
        log_curve='L-Log, Leica L-Log Reference Manual V1.6 sections 3.1 and 3.2',
        baseline='constructed: BT.709 OETF of L-Log-decoded scene reflection, clamped at LSR 1',
        baseline_is_leica_reference=False,
        source_colour_space='ITU-R BT.2020 (L-Log) -> ITU-R BT.709 (LUT output)',
        limitations=[
            'The baseline is this project\'s construction, not a Leica reference rendering.',
            'The LUTs are video LUTs fitted for L-Log footage of another sensor family.',
            'The highlight headroom mapping above diffuse white cannot be reproduced on a camera signal that is already clipped there.',
            '3x3 matrix + common curve cannot reproduce the full nonlinear hue-dependent LUT.',
            'Grain, sensor response and Leica camera behaviour are not reproduced.'],
        variants=variants)
    (root / 'profiles' / 'leica_look_approx.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    (root / 'validation' / 'leica_fit_metrics.json').write_text(json.dumps(dict(
        domain='L-Log domain sampled inside LSR 0..1; not a colourimetric accuracy measurement',
        seed=5101, train_samples=len(train_x), metrics=metrics), indent=2), encoding='utf-8')
    # No preview .cube is written for this family: the shared writer labels its
    # output as a Fujifilm approximation, which would be wrong here.
    print('wrote profiles/leica_look_approx.json')


if __name__ == '__main__':
    main()
