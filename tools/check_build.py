#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Check cube coordinate conventions, profile bounds and APK JAR signatures."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile
import numpy as np
from fit_luts import sample, read_cube, apply_model

ROOT=Path(__file__).resolve().parents[1]

def headers(section):
    section=section.replace(b'\r\n ',b'')
    return dict(line.split(b': ',1) for line in section.split(b'\r\n') if b': ' in line)

def sha1(data):
    return base64.b64encode(hashlib.sha1(data).digest())

def check_signature(apk):
    with zipfile.ZipFile(apk) as z:
        assert z.testzip() is None
        manifest=z.read('META-INF/MANIFEST.MF')
        sf=z.read('META-INF/CERT.SF')
        sf_parts=sf.split(b'\r\n\r\n')
        assert headers(sf_parts[0])[b'SHA1-Digest-Manifest']==sha1(manifest)
        signed={headers(s)[b'Name']:headers(s)[b'SHA1-Digest'] for s in sf_parts[1:] if s}
        manifest_names=[]
        for section in manifest.split(b'\r\n\r\n')[1:]:
            if not section:continue
            fields=headers(section)
            name=fields[b'Name'].decode('utf8')
            assert fields[b'SHA1-Digest']==sha1(z.read(name)),name
            assert signed[fields[b'Name']]==sha1(section+b'\r\n\r\n'),name
            manifest_names.append(name)
        assert set(manifest_names)=={n for n in z.namelist() if not n.startswith('META-INF/')}
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            (tmp/'cert.rsa').write_bytes(z.read('META-INF/CERT.RSA'))
            (tmp/'cert.sf').write_bytes(sf)
            subprocess.run(['openssl','smime','-verify','-inform','DER','-in',str(tmp/'cert.rsa'),
                '-content',str(tmp/'cert.sf'),'-noverify','-out',os.devnull],check=True,capture_output=True)
        return len(manifest_names)

def main():
    # Asymmetric values expose red/blue axis swaps in .cube interpolation.
    n=5
    cube=np.array([[[[r/(n-1),g/(n-1),b/(n-1)] for r in range(n)]
                    for g in range(n)] for b in range(n)])
    points=np.array([[0,0,0],[1,1,1],[.13,.72,.41],[1,0,.4]])
    assert np.allclose(sample(cube,points),points,atol=1e-12)
    data=json.loads((ROOT/'profiles/film_studio.json').read_text())
    assert len(data['presets'])==15 and len({p['id'] for p in data['presets']})==15
    for p in data['presets']:
        m=np.array(p['matrix']);g=np.array(p['gamma'])
        assert m.shape==(3,3) and m.min()>=-2048 and m.max()<=3072
        assert g.shape==(1024,) and g.min()>=0 and g.max()<=1023 and np.all(np.diff(g)>=0)
        if p['family']=='ricoh':
            continue
        assert p['family']=='fujifilm' and np.all(m.sum(1)==1024)
        exported=read_cube(ROOT/'output'/f'SonyProxy_{p["official_film"].replace(".","")}.cube')
        # Grid nodes round-trip exactly, including cube boundaries.
        nodes=np.array([[0,0,0],[1,1,1],[.25,.5,.75]])
        assert np.allclose(sample(exported,nodes),apply_model(nodes,m/1024,g/1023),atol=1e-6)
    apks=list((ROOT/'output').glob('*.apk'))
    assert apks, 'No APK builds found'
    results={apk.name:dict(signed_entries=check_signature(apk),
        sha256=hashlib.sha256(apk.read_bytes()).hexdigest()) for apk in apks}
    report=dict(cube_axis_test='passed',profile_bounds_test='passed',
                exported_cube_grid_roundtrip='passed',apk_signatures=results,
                runtime_report='camera_runtime.json; runtime is not established by this static check')
    (ROOT/'validation/static_checks.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
