#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Fit bounded matrix + common 10-bit curve approximations to paired Fuji LUTs.

The official neutral WDR-709 LUT is a PROXY for Sony Standard, not a measured
Sony camera profile. Errors are numerical approximation errors under that proxy.
Neither this fitting model nor its order has been calibrated to the Sony ISP.
No F-Log LUT is applied directly to display-referred Sony RGB.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np

FILMS = [
    ("PROVIA", "pop-color", "PROVIA 标准"),
    ("Velvia", "fuji-velvia", "Velvia 鲜艳"),
    ("ASTIA", "fuji-astia", "ASTIA 柔和"),
    ("CLASSIC-CHROME", "fuji-chrome", "经典正片"),
    ("REALA-ACE", "fuji-reala", "REALA ACE"),
    ("PRO-Neg.Std", "fuji-proneg", "PRO Neg. Std"),
    ("CLASSIC-Neg.", "fuji-negative", "经典负片"),
    ("ETERNA", "fuji-eterna", "ETERNA 电影"),
    ("ETERNA-BB", "fuji-bleach", "ETERNA 漂白"),
    ("ACROS", "fuji-acros", "ACROS 黑白"),
]

def read_cube(path):
    size = None
    rows = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        words = line.split()
        if not words or words[0].startswith('#'):
            continue
        if words[0] == 'LUT_3D_SIZE':
            size = int(words[1])
        elif words[0] in ('TITLE', 'DOMAIN_MIN', 'DOMAIN_MAX'):
            if words[0].startswith('DOMAIN_'):
                expected = 0 if words[0] == 'DOMAIN_MIN' else 1
                if any(float(x) != expected for x in words[1:]):
                    raise ValueError('Only unit-domain LUTs are supported')
        else:
            rows.append([float(x) for x in words])
    values = np.asarray(rows, dtype=np.float64)
    assert size and values.shape == (size**3, 3) and np.isfinite(values).all()
    # .cube ordering: red varies fastest, then green, then blue.
    return values.reshape(size, size, size, 3)

def sample(cube, rgb):
    n = cube.shape[0]
    p = np.clip(np.asarray(rgb), 0, 1) * (n-1)
    lo = np.minimum(p.astype(int), n-2)
    f = p-lo
    out = np.zeros_like(p, dtype=np.float64)
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                weight = ((f[:,0] if dr else 1-f[:,0]) *
                          (f[:,1] if dg else 1-f[:,1]) *
                          (f[:,2] if db else 1-f[:,2]))
                out += weight[:,None] * cube[lo[:,2]+db, lo[:,1]+dg, lo[:,0]+dr]
    return out

def apply_model(rgb, matrix, curve):
    x = np.clip(np.asarray(rgb) @ np.asarray(matrix).T, 0, 1)
    return np.interp(x, np.linspace(0,1,len(curve)), curve)

def write_cube(path, matrix, curve, title):
    n = 33
    grid = np.array([(r,g,b) for b in np.linspace(0,1,n)
                     for g in np.linspace(0,1,n) for r in np.linspace(0,1,n)])
    result = apply_model(grid, matrix, curve)
    with Path(path).open('w',encoding='utf-8') as f:
        f.write('# Sony Standard / Rec.709 proxy input, FULL range. Experimental approximation.\n')
        f.write('# Not an official Fujifilm LUT; do not apply to F-Log footage.\n')
        f.write(f'TITLE "{title} - Sony proxy approximation"\nLUT_3D_SIZE {n}\n')
        np.savetxt(f, result, fmt='%.7f')

def refine_row(x, target, curve, initial):
    """Minimize output-domain error with damped two-variable Gauss-Newton."""
    design = x[:,:2]-x[:,2:3]
    q = np.linspace(0,1,len(curve))
    derivative = np.gradient(curve,q)
    ab = initial[:2].copy()
    for _ in range(50):
        linear = x[:,2]+design@ab
        pred = np.interp(linear,q,curve)
        slope = np.interp(linear,q,derivative)*(linear>0)*(linear<1)
        jac = design*slope[:,None]
        delta = np.linalg.solve(jac.T@jac+np.eye(2)*.01, jac.T@(pred-target))
        before = np.mean((pred-target)**2)
        accepted = False
        for scale in (1,.5,.25,.125,.0625):
            candidate = ab-scale*delta
            row = np.r_[candidate,1-candidate.sum()]
            if row.min() < -1.8 or row.max() > 2.8:
                continue
            after = np.mean((np.interp(x[:,2]+design@candidate,q,curve)-target)**2)
            if after < before-1e-10:
                ab = candidate
                accepted = True
                break
        if not accepted:
            break
    return np.r_[ab,1-ab.sum()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lut_dir', type=Path)
    ap.add_argument('project_dir', type=Path)
    args = ap.parse_args()
    root = args.project_dir
    for folder in ('profiles', 'output', 'validation'):
        (root/folder).mkdir(parents=True, exist_ok=True)
    neutral_path = args.lut_dir / 'FLog2_to_WDR-709_33grid_V.1.00.cube'
    neutral = read_cube(neutral_path)
    rng = np.random.default_rng(5100)
    # Training and validation use independent random source points.
    # Log inputs are sampled only as coordinates of two official LUTs.
    train_log = rng.uniform(0.05,0.85,(100000,3))
    valid_log = rng.uniform(0.05,0.85,(30000,3))
    train_x, valid_x = sample(neutral,train_log), sample(neutral,valid_log)
    train_mask = (train_x.min(1)>.015)&(train_x.max(1)<.985)
    valid_mask = (valid_x.min(1)>.015)&(valid_x.max(1)<.985)
    train_log, train_x = train_log[train_mask], train_x[train_mask]
    valid_log, valid_x = valid_log[valid_mask], valid_x[valid_mask]
    gray_log = np.repeat(np.linspace(0,1,4096)[:,None],3,axis=1)
    neutral_gray = sample(neutral,gray_log).mean(1)
    keep = np.r_[True,np.diff(neutral_gray)>1e-7]
    gx = neutral_gray[keep]
    q = np.linspace(0,1,1024)
    profiles = []
    metrics = []
    for token,slot,label in FILMS:
        source = args.lut_dir / f'FLog2_to_{token}_33grid_V.1.00.cube'
        lut = read_cube(source)
        target = sample(lut,train_log)
        valid_y = sample(lut,valid_log)
        gray_y = np.maximum.accumulate(sample(lut,gray_log).mean(1)[keep])
        curve = np.clip(np.interp(q,gx,gray_y),0,1)
        # Invert the common monotonic curve before constrained matrix fitting.
        cy, ids = np.unique(curve, return_index=True)
        linear_target = np.interp(target,cy,q[ids])
        # Enforce row sum one: the neutral axis remains neutral.
        design = train_x[:,:2]-train_x[:,2:3]
        matrix = np.empty((3,3))
        for c in range(3):
            coeff = np.linalg.lstsq(design,linear_target[:,c]-train_x[:,2],rcond=None)[0]
            matrix[c] = [coeff[0],coeff[1],1-coeff.sum()]
            matrix[c] = refine_row(train_x,target[:,c],curve,matrix[c])
        if token == 'ACROS':
            matrix[:] = refine_row(train_x,target.mean(1),curve,matrix.mean(0))
        matrix_i = np.rint(matrix*1024).astype(int)
        matrix_i[:,2] = 1024-matrix_i[:,:2].sum(1)
        assert matrix_i.min() >= -2048 and matrix_i.max() <= 3072
        curve_i = np.rint(curve*1023).astype(int)
        assert np.all(np.diff(curve_i)>=0)
        pred = apply_model(valid_x,matrix_i/1024,curve_i/1023)
        error = np.abs(pred-valid_y)
        metric = dict(film=token,samples=len(valid_y),rgb_mae=float(error.mean()),
                      rgb_p95=float(np.quantile(error,.95)),rgb_max=float(error.max()),
                      max_gray_chroma=float(np.ptp(sample(lut,gray_log),axis=1).max()))
        metrics.append(metric)
        profiles.append(dict(id=slot,name=label,official_film=token,
            source_file=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            matrix=matrix_i.tolist(),gamma=curve_i.tolist()))
        write_cube(root/'output'/f'SonyProxy_{token.replace(".","")}.cube',
                   matrix_i/1024,curve_i/1023,token)
        print(token,'MAE',round(metric['rgb_mae'],4),'p95',round(metric['rgb_p95'],4))
    data = dict(schema=1,version='0.1.0-alpha',source_url='https://dl.fujifilm-x.com/support/lut/gfx-eterna-55-3d-lut-v110.zip',
        neutral_proxy=neutral_path.name,
        limitations=['Sony Standard is not calibrated to the official WDR-709 neutral reference.',
          '3x3 matrix + common curve cannot reproduce the full nonlinear hue-dependent LUT.',
          'Camera ISP matrix/curve order and transfer functions require hardware measurement.',
          'Grain, sensor response, highlight recovery and Fujifilm camera behavior are not reproduced.'],
        presets=profiles)
    (root/'profiles'/'fuji_official_approx.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (root/'validation'/'fit_metrics.json').write_text(json.dumps(dict(
        domain='Unclipped official WDR-709 proxy RGB; not a camera accuracy measurement',
        train_samples=len(train_x),seed=5100,metrics=metrics),indent=2),encoding='utf-8')

if __name__ == '__main__':
    main()
