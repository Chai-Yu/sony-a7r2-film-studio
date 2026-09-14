#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Inspect explicitly selected camera test captures, without modifying originals.

Grayscale evidence establishes that a color transform reached the saved output;
it does not establish an exact match to Fujifilm ACROS or validate other looks.
"""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image


def chroma_metrics(rgb):
    # Equal R/G/B values are achromatic in the decoded output. Allow a small
    # difference when assessing JPEG/video quantization or conversion noise.
    spread=rgb.max(axis=-1).astype(np.int16)-rgb.min(axis=-1).astype(np.int16)
    return dict(mean_channel_spread=float(spread.mean()),
                p99_channel_spread=float(np.percentile(spread,99)),
                max_channel_spread=int(spread.max()),
                fraction_spread_over_3=float((spread>3).mean()))


def inspect_jpeg(path):
    with Image.open(path) as im:
        exif=im.getexif()
        rgb=np.asarray(im.convert('RGB'))
        return dict(file=path.name,bytes=path.stat().st_size,width=im.width,
                    height=im.height,make=str(exif.get(271,'')),
                    model=str(exif.get(272,'')),date_time=str(exif.get(306,'')),
                    chroma=chroma_metrics(rgb))


def inspect_movie(path,ffmpeg,ffprobe,preview_dir):
    probe=subprocess.run([ffprobe,'-v','error','-show_entries',
        'format=duration,size:stream=index,codec_type,codec_name,width,height,pix_fmt,r_frame_rate,sample_rate,channels',
        '-of','json',str(path)],capture_output=True,text=True,check=True)
    meta=json.loads(probe.stdout)
    # Decode all video and audio packets. Success means more than a valid header.
    subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(path),
        '-map','0:v:0','-map','0:a?','-f','null','-'],capture_output=True,check=True)
    v=next(s for s in meta['streams'] if s['codec_type']=='video')
    w=320;h=2*round(v['height']*w/v['width']/2)
    raw=subprocess.run([ffmpeg,'-v','error','-i',str(path),'-an','-vf',
        f'fps=1,scale={w}:{h}','-f','rawvideo','-pix_fmt','rgb24','-'],
        capture_output=True,check=True).stdout
    frames=np.frombuffer(raw,dtype=np.uint8).reshape((-1,h,w,3))
    result=dict(file=path.name,full_decode='passed',metadata=meta,
                sample_frame_count=len(frames),
                frame_chroma=[chroma_metrics(frame) for frame in frames])
    if preview_dir:
        preview_dir.mkdir(parents=True,exist_ok=True)
        out=preview_dir/'ACROS-video-frame.png'
        subprocess.run([ffmpeg,'-v','error','-y','-ss','2','-i',str(path),
            '-frames:v','1','-vf','scale=1280:-2',str(out)],capture_output=True,check=True)
        result['preview']=str(out.resolve())
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--provia',type=Path,required=True)
    ap.add_argument('--acros',type=Path,required=True)
    ap.add_argument('--movie',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--preview-dir',type=Path)
    ap.add_argument('--ffmpeg',default='ffmpeg')
    ap.add_argument('--ffprobe',default='ffprobe')
    a=ap.parse_args()
    result={'provia_jpeg':inspect_jpeg(a.provia),'acros_jpeg':inspect_jpeg(a.acros),
            'acros_movie':inspect_movie(a.movie,a.ffmpeg,a.ffprobe,a.preview_dir),
            'scope':'Output persistence and achromatic ACROS check; not a colorimetric Fuji matching test.'}
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
