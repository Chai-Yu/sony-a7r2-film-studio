"""Correct the Fujifilm matrices for the domain the camera actually feeds them.

The fits in tools/fit_luts.py map the official *flat* neutral rendering onto each
look. The camera does not output that: it hands the hook its own rendered Standard
image, which is about 26% more chromatic. The matrix's chroma response barely
depends on how chromatic its input already is, so that gain stacks on an input
that is already saturated and every look over-delivers.

Two ways to correct it, both driven by triples shot on an a7R II - camera
Neutral, camera STD, and the app's own output - with the scene recovered by
inverting the official neutral LUT (99.7 / 98.9 / 97.2 / 99.0 / 99.8% of pixels
over five scenes invert to below 2e-3, median residual 5.3e-4, so the camera's
flat rendering is consistent with the official neutral; it is not proof, the LUT
is many-to-one):

  --factor X      what ships. Scale each matrix's chroma response,
                  M' = A + X (M - A) with A the projector onto the neutral
                  direction. X = 0.75.
  --scenes FILE   refit the matrix against the input the camera really supplies.
                  Only the matrix moves: the tone curve comes from the grey axis
                  and the two renderings agree on greys, so the domain mismatch
                  does not touch it. KEPT BUT NOT SHIPPED - see below.

BLENDING TOWARD THE IDENTITY IS WRONG: it raises the gain of the desaturating
looks and turns ACROS into colour (measured 0.000 -> 0.347). The projector form
moves every look the same way, but it still cannot be right everywhere. It is
wrong per scene (0.68 to 0.90) and wrong per look - it damages REALA ACE, whose
chroma error goes from 26% to 51% against 45% at 0.75.

THE REFIT WAS REJECTED OUT OF SAMPLE. It minimises RGB error, which is dominated
by the many near-neutral pixels, and it buys that by pulling chroma 15-20% too
low. Measured on 1403 and 1406 - shot at 100% afterwards and never fitted on -
delivered over official chroma came out as:

  raw            1.312  1.209        the camera today, 21-31% over
  raw + 0.75     1.026  0.930        what ships
  refit          0.835  0.720        10-28% under
  refit + 1.15   0.946  0.821

The parameter was chosen on the three fitting scenes (1394/1397/1400), where
0.75 gives a mean |ratio-1| of 8.17% against 28.06% raw and 13.35% for the
refit, and then confirmed on the two held-out scenes (7.51% / 27.47% worst).
Error there is the mean and worst relative deviation of a delivered chroma from
the official look's, over five chroma definitions; RGB error is the pooled
absolute RGB difference on a 0-1 scale - not a delta-E, not a similarity score.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_luts import read_cube, sample, refine_row, apply_model, FILMS  # noqa: E402

CAMERA_STANDARD_OVER_FLAT = 1.260        # chroma, three independent measurements
REFERENCE_GAIN_OVER_STANDARD = 1.2757    # sat(official PROVIA) / sat(camera Standard)
FITTED_GAIN_OVER_STANDARD = 1.8016       # the model at 100%, verified against the camera
TARGET_GAIN_OVER_STANDARD = REFERENCE_GAIN_OVER_STANDARD
# Solved on 1394/1397/1400, then confirmed on 1403/1406 shot at 100% afterwards:
# 0.75 beats 0.68 on both (8.17% against 8.98% mean |ratio-1| on the fitting
# scenes, 7.51% against 10.52% on the held-out ones).
DEFAULT_FACTOR = 0.75
DEFAULT_LUT_DIR = 'inputs/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2'
NEUTRAL_ROW = [1024 / 3] * 3
Q = np.linspace(0, 1, 1024)

# Five ways of asking "how chromatic is this image", so no conclusion rests on one.
METRICS = (
    ('mean(max-min)', lambda v: float((v.max(1) - v.min(1)).mean())),
    ('median(max-min)', lambda v: float(np.median(v.max(1) - v.min(1)))),
    ('mean sd(RGB)', lambda v: float(v.std(1).mean())),
    ('mean(1-min/max)', lambda v: float((1 - v.min(1) / np.maximum(v.max(1), 1e-3)).mean())),
    ('mean opponent', lambda v: float(np.hypot(v[:, 0] - v[:, 1],
                                               (v[:, 0] + v[:, 1]) / 2 - v[:, 2]).mean())),
)


def blend(matrix, factor):
    """A + factor * (matrix - A), rounded to Q10, rows still summing to 1024."""
    row_out = []
    for row in matrix:
        scaled = [round(neutral + factor * (value - neutral))
                  for value, neutral in zip(row, NEUTRAL_ROW)]
        scaled[2] = 1024 - scaled[0] - scaled[1]
        row_out.append(scaled)
    return row_out


def probe_samples(seed=3, count=20000):
    """Slightly chromatic samples about the neutral axis, to summarise a matrix."""
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(count, 3))
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)
    levels = rng.uniform(0.2, 0.9, (count, 1))
    return np.clip(levels * (1 + 0.08 * directions), 0, 1)


PROBE = probe_samples()


def chroma_gain(matrix, samples):
    """How much chroma the matrix adds, averaged over a set of directions."""
    m = np.asarray(matrix, dtype=float) / 1024
    out = samples @ m.T
    return float((out.max(1) - out.min(1)).mean() / (samples.max(1) - samples.min(1)).mean())


def render(matrix, curve, source):
    return apply_model(source, np.asarray(matrix, float) / 1024.0,
                       np.asarray(curve, float) / 1023.0)


def is_monochrome(matrix):
    """An ACROS-style matrix has three identical rows, so its output is always grey.

    There is no chroma to correct, and scaling does not leave such a matrix alone:
    it moves the grey weights, which is the only thing the matrix does. Measured on
    a spread of saturated colours, scaling to 0.75 shifts the rendered grey by 0.85%
    on average and up to 3.6%. Leave-one-scene-out says the untouched matrix is also
    the more accurate one (RGB error 0.0681 / 0.0860 / 0.0317 against 0.0680 / 0.0861
    / 0.0334 for 0.75), so this is skipped rather than corrected.
    """
    return all(list(row) == list(matrix[0]) for row in matrix)


def fit_matrix(source, target, curve, token):
    """Fit one matrix to a real scene state, with the film's own curve held fixed.

    Row sums stay at one so the neutral axis stays neutral. The same Gauss-Newton
    polish fit_luts.py uses is applied afterwards.
    """
    curve01 = np.asarray(curve, float) / 1023.0
    unique, ids = np.unique(curve01, return_index=True)
    linear_target = np.interp(target, unique, Q[ids])
    design = source[:, :2] - source[:, 2:3]
    matrix = np.empty((3, 3))
    for channel in range(3):
        coeff = np.linalg.lstsq(design, linear_target[:, channel] - source[:, 2],
                                rcond=None)[0]
        matrix[channel] = [coeff[0], coeff[1], 1 - coeff.sum()]
        matrix[channel] = refine_row(source, target[:, channel], curve01, matrix[channel])
    if token == 'ACROS':
        # Monochrome: fit the mean channel and replicate the row.
        matrix[:] = refine_row(source, target.mean(1), curve01, matrix.mean(0))
    quantised = np.rint(matrix * 1024).astype(int)
    quantised[:, 2] = 1024 - quantised[:, :2].sum(1)
    assert quantised.min() >= -2048 and quantised.max() <= 3072
    return quantised


def load_scenes(path):
    """Scene pixel sets written by the measuring step: camera STD pixels and the
    recovered scene code, on identical pixels."""
    data = np.load(path)
    suffix = '_l_code'
    names = sorted(key[:-len(suffix)] for key in data.files if key.endswith(suffix))
    if not names:
        raise SystemExit(f'{path} holds no "<scene>{suffix}" arrays')
    return {name: dict(code=data[f'{name}{suffix}'], c_std=data[f'{name}_std'])
            for name in names}


def refit(scenes, lut_dir, presets):
    """Refit every Fujifilm matrix, and score the result leave-one-scene-out."""
    curve_of = {preset['id']: preset['gamma'] for preset in presets}
    raw_of = {preset['id']: preset.get('matrix_fit') or preset['matrix']
              for preset in presets}
    targets = {}
    for token, slot, _ in FILMS:
        lut = read_cube(lut_dir / f'FLog2_to_{token}_33grid_V.1.00.cube')
        targets[slot] = {name: sample(lut, scene['code']) for name, scene in scenes.items()}

    names = list(scenes)
    methods = ('raw', f'factor {DEFAULT_FACTOR:.2f}', 'factor 0.75', 'refit')
    scores = {method: dict(rgb=[], chroma=[]) for method in methods}
    print('  leave-one-scene-out: fit on the other scenes, measure on this one')
    print(f'  {"film":15s} {"scene":>8s} | ' +
          ' '.join(f'{method:>13s}' for method in methods) + '   (RGB error / chroma)')

    for token, slot, _ in FILMS:
        curve, raw = curve_of[slot], np.asarray(raw_of[slot], float)
        monochrome = token == 'ACROS'
        for held in names:
            others = [name for name in names if name != held]
            source = np.vstack([scenes[name]['c_std'] for name in others])
            target = np.vstack([targets[slot][name] for name in others])
            candidates = {'raw': raw,
                          f'factor {DEFAULT_FACTOR:.2f}': np.asarray(blend(raw, DEFAULT_FACTOR)),
                          'factor 0.75': np.asarray(blend(raw, 0.75)),
                          'refit': fit_matrix(source, target, curve, token)}
            c_std, official = scenes[held]['c_std'], targets[slot][held]
            line = []
            for method, matrix in candidates.items():
                rendered = render(matrix, curve, c_std)
                rgb = float(np.abs(rendered - official).mean())
                scores[method]['rgb'].append(rgb)
                if monochrome:
                    chroma = 0.0
                else:
                    chroma = max(abs(metric(rendered) / metric(c_std) /
                                     (metric(official) / metric(c_std)) - 1)
                                 for _, metric in METRICS)
                    scores[method]['chroma'].append(chroma)
                line.append(f'{rgb:6.4f} {chroma:6.1%}')
            print(f'  {slot:15s} {held:>8s} | ' +
                  ' '.join(f'{value:>13s}' for value in line))

    print()
    print(f'  {"method":>13s}  {"RGB mean":>9s} {"RGB p90":>8s} {"RGB worst":>10s}   '
          f'{"chroma RMS":>11s} {"chroma worst":>13s}')
    summary = {}
    for method in methods:
        rgb = np.array(scores[method]['rgb'])
        chroma = np.array(scores[method]['chroma'])
        summary[method] = dict(rgb_mean=float(rgb.mean()),
                               rgb_p90=float(np.quantile(rgb, 0.9)),
                               rgb_worst=float(rgb.max()),
                               chroma_rms=float(np.sqrt((chroma ** 2).mean())),
                               chroma_worst=float(chroma.max()))
        print(f'  {method:>13s}  {summary[method]["rgb_mean"]:9.4f} '
              f'{summary[method]["rgb_p90"]:8.4f} {summary[method]["rgb_worst"]:10.4f}   '
              f'{summary[method]["chroma_rms"]:11.2%} '
              f'{summary[method]["chroma_worst"]:13.2%}')

    # The matrices that ship are fitted on every scene that is available.
    final = {}
    for token, slot, _ in FILMS:
        if is_monochrome(raw_of[slot]):
            final[slot] = [row[:] for row in raw_of[slot]]
            continue
        source = np.vstack([scene['c_std'] for scene in scenes.values()])
        target = np.vstack([targets[slot][name] for name in names])
        final[slot] = fit_matrix(source, target, curve_of[slot], token)
    return final, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir', type=Path)
    ap.add_argument('--scenes', type=Path,
                    help='paired scene data (.npz) from the measuring step; refits the '
                         'matrices in the camera\'s own domain')
    ap.add_argument('--lut-dir', type=Path,
                    help=f'Official LUT folder (default {DEFAULT_LUT_DIR})')
    ap.add_argument('--factor', type=float, default=DEFAULT_FACTOR,
                    help=f'One-parameter alternative to --scenes: scale each matrix\'s '
                         f'chroma response. Default {DEFAULT_FACTOR:.3f}.')
    ap.add_argument('--clear', action='store_true',
                    help='Remove the correction and restore the raw fitted matrices')
    args = ap.parse_args()

    path = args.project_dir / 'profiles/fuji_official_approx.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    presets = data['presets']
    for preset in presets:
        raw = preset.get('matrix_fit') or preset['matrix']
        preset['matrix_fit'] = [row[:] for row in raw]
    by_id = {preset['id']: preset for preset in presets}

    if args.clear:
        for preset in presets:
            preset['matrix'] = [row[:] for row in preset['matrix_fit']]
        data.pop('domain_calibration', None)
        print('restored the raw fitted matrices')
    elif args.scenes:
        lut_dir = args.lut_dir or (args.project_dir / DEFAULT_LUT_DIR)
        scenes = load_scenes(args.scenes)
        print(f'refitting in the camera\'s domain, from {len(scenes)} scenes: '
              f'{", ".join(scenes)}')
        print()
        fitted, summary = refit(scenes, lut_dir, presets)
        print()
        print(f'  {"film":15s} {"fitted":>9s} {"refit":>9s}')
        for token, slot, _ in FILMS:
            if is_monochrome(by_id[slot]['matrix_fit']):
                print(f'  {slot:15s}      (monochrome, left alone)')
                by_id[slot]['matrix'] = [row[:] for row in by_id[slot]['matrix_fit']]
                continue
            before = chroma_gain(by_id[slot]['matrix_fit'], PROBE)
            after = chroma_gain(fitted[slot], PROBE)
            print(f'  {slot:15s} {before:9.3f} {after:9.3f}')
            by_id[slot]['matrix'] = fitted[slot].tolist()
        data['domain_calibration'] = dict(
            method='domain refit: fitted against the camera\'s Standard rendering, '
                   'which is what the hook actually receives',
            reason='the fitted matrices map the official flat neutral rendering; the '
                   'camera feeds its own Standard rendering, about 26% more chromatic',
            measured_on=f'Sony a7R II, 2026-09-14, {len(scenes)} scenes, each with a '
                        f'camera Neutral, a camera STD and an app shot',
            scenes=list(scenes),
            validation='leave-one-scene-out over every film and scene',
            camera_standard_over_flat_chroma=CAMERA_STANDARD_OVER_FLAT,
            reference_gain_over_standard_chroma=REFERENCE_GAIN_OVER_STANDARD,
            fitted_gain_over_standard_chroma=FITTED_GAIN_OVER_STANDARD,
            scores={name: {key: round(value, 4) for key, value in values.items()}
                    for name, values in summary.items()},
            applies_to='fujifilm (the Leica family uses a constructed baseline and has '
                       'not been measured this way; Ricoh comes from upstream)',
            monochrome='left unchanged: an ACROS-style matrix has three identical rows, '
                       'so it carries no chroma to correct',
            detail='docs/VALIDATION.md, 2026-09-14')
    else:
        print(f'chroma factor {args.factor:.4f}')
        print(f'{"film":16s} {"fit":>8s} {"shipped":>9s} {"change":>8s}')
        for preset in presets:
            before = chroma_gain(preset['matrix_fit'], PROBE)
            if is_monochrome(preset['matrix_fit']):
                preset['matrix'] = [row[:] for row in preset['matrix_fit']]
                print(f'{preset["id"]:16s} {before:8.3f}     (monochrome, left alone)')
                continue
            preset['matrix'] = blend(preset['matrix_fit'], args.factor)
            after = chroma_gain(preset['matrix'], PROBE)
            print(f'{preset["id"]:16s} {before:8.3f} {after:9.3f} {after - before:+8.3f}')
        data['domain_calibration'] = dict(
            method=f'scalar chroma response scaling, M\' = A + {args.factor:.3f} (M - A)',
            reason='the fit baseline is a flat reference, the camera feeds a rendered '
                   'Standard image that is more chromatic',
            measured_on='Sony a7R II, 2026-09-14, five scenes, each with a camera '
                        'Neutral, a camera STD and an app shot',
            camera_standard_over_flat_chroma=CAMERA_STANDARD_OVER_FLAT,
            reference_gain_over_standard_chroma=REFERENCE_GAIN_OVER_STANDARD,
            fitted_gain_over_standard_chroma=FITTED_GAIN_OVER_STANDARD,
            target_gain_over_standard_chroma=round(TARGET_GAIN_OVER_STANDARD, 4),
            chroma_factor=round(args.factor, 6),
            chosen_on='1394 / 1397 / 1400 (mean chroma error 8.17% at 0.75, 28.06% raw)',
            held_out='1403 / 1406, shot at 100% afterwards (7.51% mean, 27.47% worst '
                     'at 0.75; the domain refit gives 22.22% and is not shipped)',
            known_limitation='still wrong per look: it exaggerates the correction for '
                             'the desaturating looks, REALA ACE above all',
            monochrome='left unchanged: an ACROS-style matrix has three identical rows, '
                       'so it carries no chroma to correct and scaling it would only '
                       'move the grey weights',
            applies_to='fujifilm (the Leica family uses a constructed baseline and has '
                       'not been measured this way; Ricoh comes from upstream)',
            detail='docs/VALIDATION.md, 2026-09-14')

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {path.relative_to(args.project_dir)}')


if __name__ == '__main__':
    main()
