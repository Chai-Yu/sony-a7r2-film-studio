#!/usr/bin/env python3
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Reproducible local alpha patch of the verified Ricoh v1.1.4 APK.

The input Sony-derived APK is supplied separately. No firmware is modified.
The result uses a separate same-length package name and a private signing key.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from sign_apk import sign_apk, ensure_pem
from movie_menu import LABELS as MOVIE_LABELS, patch_movie_menu
from filter_strength import STRENGTHS, LABELS as STRENGTH_LABELS, blend_profile, patch_strength_menu, strength_methods
from film_profiles import EXPECTED_HOOK, combined_profiles

OLD = 'com.sony.imaging.app.pictureeffectplus'
NEW = 'com.yuki.imaging.app.pictureeffectplus'
HOOK = 'L'+OLD.replace('.','/')+'/shooting/camera/RicohHook;'
CTRL = 'L'+OLD.replace('.','/')+'/shooting/camera/PictureEffectPlusController;'
EXPECTED = '80cb4a541f5f3dd49e8f53ffb1905048097fec17209fc9cb595a00681e65e8ea'
VERSION = '0.2.0-alpha'
ANDROID_VERSION = '0.2a'
APP_NAME = '胶片工坊'

def replace_method(text, signature, replacement):
    pattern = r'^\.method [^\n]*'+re.escape(signature)+r'\n[\s\S]*?^\.end method'
    text, n = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.M)
    if n != 1:
        raise ValueError('Expected exactly one method: '+signature)
    return text

def quote(s):
    return json.dumps(s,ensure_ascii=True)

def lookup_method(name, profiles, kind, movie=False):
    ret = {'gamma':'[B','matrix':'[I','name':'Ljava/lang/String;','guide':'Ljava/lang/String;'}[kind]
    lines=[f'.method public static {name}(Ljava/lang/String;){ret}', '    .locals 2',
           '    if-eqz p0, :none']
    if kind in ('gamma', 'matrix'):
        lines += [f'    invoke-static {{}}, {HOOK}->getStrength()I', '    move-result v1']
    for i,p in enumerate(profiles):
        lines += [f'    const-string v0, {quote(p["id"])}',
                  '    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z',
                  '    move-result v0', f'    if-eqz v0, :next_{i}']
        if kind in ('gamma','matrix'):
            for strength in STRENGTHS[:-1]:
                lines += [f'    const/16 v0, {hex(strength)}',
                          f'    if-ne v1, v0, :strength_{i}_{strength}',
                          f'    sget-object v0, {HOOK}->sFuji{kind}{i}_{strength}:{ret}',
                          '    return-object v0', f'    :strength_{i}_{strength}']
            lines += [f'    sget-object v0, {HOOK}->sFuji{kind}{i}_100:{ret}']
        else:
            value=p['name'] if kind=='name' else p['guide']
            lines += [f'    const-string v0, {quote(value)}']
        lines += ['    return-object v0',f'    :next_{i}']
    if kind in ('name', 'guide'):
        labels_map = {'ApplicationTop': ('胶片风格', '富士参考与理光风格；拍照和录像待机均可切换。')}
        labels_map.update(STRENGTH_LABELS)
        if movie:
            labels_map.update(MOVIE_LABELS)
        for i, (key, labels) in enumerate(labels_map.items()):
            lines += [f'    const-string v0, {quote(key)}',
                      '    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z',
                      '    move-result v0', f'    if-eqz v0, :ui_next_{i}',
                      f'    const-string v0, {quote(labels[0 if kind=="name" else 1])}',
                      '    return-object v0', f'    :ui_next_{i}']
    return '\n'.join(lines+['    :none','    const/4 v0, 0x0','    return-object v0','.end method'])

def make_init(profiles):
    lines=['.method static constructor <clinit>()V','    .locals 2']
    arrays=[]
    for i,p in enumerate(profiles):
        for strength in STRENGTHS:
            blend = blend_profile(p, strength)
            for kind,count,dex_type,values,width in [
                ('matrix',9,'[I',sum(blend['matrix'],[]),4),
                ('gamma',2048,'[B',[b for v in blend['gamma'] for b in (v&255,v>>8)],1)]:
                lines += [f'    const/16 v0, {hex(count)}',f'    new-array v1, v0, {dex_type}',
                          f'    fill-array-data v1, :data_{kind}_{i}_{strength}',
                          f'    sput-object v1, {HOOK}->sFuji{kind}{i}_{strength}:{dex_type}']
                arrays += [f'    :data_{kind}_{i}_{strength}',f'    .array-data {width}']
                arrays += ['        '+(('-0x%x'%-v if v<0 else '0x%x'%v)+('t' if width==1 else '')) for v in values]
                arrays += ['    .end array-data']
    return '\n'.join(lines+['    return-void']+arrays+['.end method'])

def preset_ids(profiles):
    lines=['.method public static getPresetIds()Ljava/util/List;','    .locals 2',
           '    new-instance v0, Ljava/util/ArrayList;',
           '    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V']
    for p in profiles:
        lines += [f'    const-string v1, {quote(p["id"])}',
                  '    invoke-virtual {v0, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z']
    return '\n'.join(lines+['    return-object v0','.end method'])

def movie_hook():
    return f'''.method public static ensureForMovie()Z
    .locals 4
    :try_start
    invoke-static {{}}, {CTRL}->getInstance(){CTRL}
    move-result-object v0
    if-eqz v0, :failed
    invoke-virtual {{v0}}, {CTRL}->getBackupEffectValue()Ljava/lang/String;
    move-result-object v1
    const/4 v2, 0x0
    invoke-static {{v0, v2, v1}}, {HOOK}->applyHook({CTRL}Landroid/util/Pair;Ljava/lang/String;)Z
    move-result v2
    if-eqz v2, :failed
    const-string v0, "FujiHook"
    const-string v1, "Movie pre-start: selected filter applied; encoded output still needs verification"
    invoke-static {{v0, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    const/4 v0, 0x1
    return v0
    :try_end
    .catch Ljava/lang/Throwable; {{:try_start .. :try_end}} :catch
    :catch
    move-exception v0
    :failed
    const-string v0, "FujiHook"
    const-string v1, "Movie filter application failed; recording cancelled"
    invoke-static {{v0, v1}}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    const/4 v0, 0x0
    return v0
.end method'''

def movie_settings_log():
    controller='Lcom/sony/imaging/app/base/shooting/camera/MovieFormatController;'
    lines=['.method public static logMovieSettings()V', '    .locals 4', '    :try_start',
           f'    invoke-static {{}}, {controller}->getInstance(){controller}',
           '    move-result-object v0', '    new-instance v1, Ljava/lang/StringBuilder;',
           '    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V']
    for tag in ('movie_format_menu', 'record_setting'):
        lines += [f'    const-string v2, "{tag}="',
                  '    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;',
                  f'    const-string v2, "{tag}"',
                  f'    invoke-virtual {{v0, v2}}, {controller}->getValue(Ljava/lang/String;)Ljava/lang/String;',
                  '    move-result-object v2',
                  '    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;',
                  '    const-string v2, "; "',
                  '    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;']
    lines += ['    const-string v2, "strength="',
              '    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;',
              f'    invoke-static {{}}, {HOOK}->getStrengthValue()Ljava/lang/String;',
              '    move-result-object v2',
              '    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;',
              '    const-string v2, "FujiMovieSettings"',
              '    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;',
              '    move-result-object v3',
              '    invoke-static {v2, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I',
              '    :try_end', '    .catch Ljava/lang/Throwable; {:try_start .. :try_end} :catch',
              '    return-void', '    :catch', '    move-exception v0', '    return-void', '.end method']
    return '\n'.join(lines)

def patch_hook(path,profiles,upstream_hook,movie=False):
    text=path.read_text()
    fields='\n'.join(f'.field private static sFuji{k}{i}_{strength}:{t}' for i in range(len(profiles))
                     for strength in STRENGTHS
                     for k,t in [('matrix','[I'),('gamma','[B')])
    text=text.replace('# static fields','# static fields\n'+fields)
    text=replace_method(text,'<clinit>()V',make_init(profiles))
    for method,kind in [('getGammaBytes','gamma'),('getRGBMatrix','matrix'),
                        ('getFilterName','name'),('getFilterGuide','guide')]:
        ret={'gamma':'[B','matrix':'[I','name':'Ljava/lang/String;','guide':'Ljava/lang/String;'}[kind]
        text=replace_method(text,method+'(Ljava/lang/String;)'+ret,lookup_method(method,profiles,kind,movie))
    original=upstream_hook.read_text()
    apply=re.search(r'^\.method public static applyHook\([\s\S]*?^\.end method',original,re.M).group()
    # Fail closed if matrix/gamma handles are unavailable, instead of reporting success.
    apply=apply.replace('if-eqz v2, :cond_4','if-eqz v2, :fuji_failed')
    apply=apply.replace('if-eqz v2, :cond_5','if-eqz v2, :fuji_failed')
    apply=apply.replace('if-eqz v3, :cond_5','if-eqz v3, :fuji_failed')
    apply=apply.replace('    :catch_0\n','    :fuji_failed\n    const/4 v0, 0x0\n    return v0\n\n    :catch_0\n')
    text=replace_method(text,'applyHook('+CTRL+'Landroid/util/Pair;Ljava/lang/String;)Z',apply)
    text+='\n'+preset_ids(profiles)+'\n'+movie_hook()+'\n'+strength_methods(HOOK,CTRL)+'\n'
    if movie:
        text+='\n'+movie_settings_log()+'\n'
    text=text.replace('"RicohHook"','"FujiHook"').replace('Ricoh preset','Fuji approximation')
    path.write_text(text)

def patch_menu(base,profiles):
    path=base/'assets/MenuData.xml'
    tree=ET.parse(path)
    parent=next(x for x in tree.iter() if x.get('ItemId')=='ApplicationTop')
    template=copy.deepcopy(parent[0])
    for child in list(parent):parent.remove(child)
    for p in profiles:
        item=copy.deepcopy(template)
        for child in list(item):item.remove(child)
        item.attrib.update(ItemId=p['id'],Value=p['id'],Title=p['name'],DisplayName=p['name'],
                           ExecType='SET_VALUE',NextMenuID='')
        parent.append(item)
    tree.write(path,encoding='utf-8',xml_declaration=True)
    patch_strength_menu(base, OLD+'.shooting.camera.PictureEffectPlusController')
    ctrl=base/'smali'/OLD.replace('.','/')/'shooting/camera/PictureEffectPlusController.smali'
    text=ctrl.read_text()
    for name in ('getSupportedValue','getAvailableValue'):
        sig=name+'(Ljava/lang/String;)Ljava/util/List;'
        method=f'''.method public {sig}
    .locals 1
    const-string v0, "FujiStrength"
    invoke-virtual {{v0, p1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :not_strength
    invoke-static {{}}, {HOOK}->getStrengthValues()Ljava/util/List;
    move-result-object v0
    return-object v0
    :not_strength
    const-string v0, "ApplicationTop"
    invoke-virtual {{v0, p1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :film_list
    const-string v0, "PictureEffect"
    invoke-virtual {{v0, p1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :film_list
    invoke-super {{p0, p1}}, Lcom/sony/imaging/app/base/shooting/camera/PictureEffectController;->{sig}
    move-result-object v0
    return-object v0
    :film_list
    invoke-static {{}}, {HOOK}->getPresetIds()Ljava/util/List;
    move-result-object v0
    return-object v0
.end method'''
        text=replace_method(text,sig,method)
    # Native PictureEffect availability can be false for RAW or movie mode.
    # Our matrix/gamma presets do not use that native effect. Keep their menu
    # available while idle, but do not allow changes during video recording.
    for name, result in [('isAvailable', 'available'),
                         ('isUnavailableSceneFactor', 'scene')]:
        sig=name+'(Ljava/lang/String;)Z'
        custom_return = '''    invoke-static {}, Lcom/sony/imaging/app/base/shooting/movie/MovieShootingExecutor;->isMovieRecording()Z
    move-result v0
    xor-int/lit8 v0, v0, 0x1
    return v0''' if result == 'available' else '''    const/4 v0, 0x0
    return v0'''
        text=replace_method(text,sig,f'''.method public {sig}
    .locals 1
    const-string v0, "FujiStrength"
    invoke-virtual {{v0, p1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :fuji_menu
    const-string v0, "ApplicationTop"
    invoke-virtual {{v0, p1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :fuji_menu
    const-string v0, "PictureEffect"
    invoke-virtual {{v0, p1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :fuji_menu
    invoke-static {{p1}}, {HOOK}->isRicohPreset(Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :fuji_menu
    invoke-super {{p0, p1}}, Lcom/sony/imaging/app/base/shooting/camera/PictureEffectController;->{sig}
    move-result v0
    return v0
    :fuji_menu
{custom_return}
.end method''')
    # Handle the independent strength setting before the upstream effect logic.
    for name, signature, body in (
        ('getValue', 'getValue(Ljava/lang/String;)Ljava/lang/String;', f'''    invoke-static {{}}, {HOOK}->getStrengthValue()Ljava/lang/String;
    move-result-object v0
    return-object v0'''),
        ('setValue', 'setValue(Ljava/lang/String;Ljava/lang/String;)V', f'''    invoke-static {{p0, p2}}, {HOOK}->setStrengthValue({CTRL}Ljava/lang/String;)V
    return-void'''),
    ):
        method=re.search(r'^\.method public '+re.escape(signature)+r'\n[\s\S]*?^\.end method',text,re.M).group()
        prefix=f'''    const-string v0, "FujiStrength"
    invoke-virtual {{v0, p1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :fuji_original
{body}
    :fuji_original
'''
        assert method.count('    .prologue\n') == 1
        method=method.replace('    .prologue\n', '    .prologue\n'+prefix)
        text=replace_method(text,signature,method)
    ctrl.write_text(text)
    layout=base/'smali'/OLD.replace('.','/')/'shooting/layout/PictureEffectPlusOptionMenuLayout.smali'
    cls='L'+OLD.replace('.','/')+'/shooting/layout/PictureEffectPlusOptionMenuLayout;'
    lines=['.method private initializeIconMap()V','    .locals 3',
           '    new-instance v0, Ljava/util/HashMap;',
           '    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V',
           f'    sput-object v0, {cls}->mItemIconMap:Ljava/util/HashMap;']
    for p in profiles:
        lines += [f'    const-string v1, {quote(p["id"])}',
                  '    const v2, 0x7f020054',
                  '    invoke-static {v2}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;',
                  '    move-result-object v2',
                  '    invoke-virtual {v0, v1, v2}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;']
    layout.write_text(replace_method(layout.read_text(),'initializeIconMap()V',
                                     '\n'.join(lines+['    return-void','.end method'])))

def patch_movie(base):
    patch_movie_menu(base)
    # Movie standby has a separate handler from still shooting. Open the same
    # effect chooser from center/enter without changing the recording handler.
    handler='Lcom/sony/imaging/app/base/shooting/movie/trigger/MovieRecStandbyStateKeyHandler;'
    path=base/'smali'/handler[1:-1]
    path=path.with_suffix('.smali')
    text=path.read_text()
    assert '.method public pushedCenterKey()I' not in text
    text+=f'''
.method public pushedCenterKey()I
    .locals 3
    invoke-static {{}}, Lcom/sony/imaging/app/base/shooting/movie/MovieShootingExecutor;->isMovieRecording()Z
    move-result v0
    if-nez v0, :done
    new-instance v0, Landroid/os/Bundle;
    invoke-direct {{v0}}, Landroid/os/Bundle;-><init>()V
    const-string v1, "ItemId"
    const-string v2, "ApplicationTop"
    invoke-virtual {{v0, v1, v2}}, Landroid/os/Bundle;->putString(Ljava/lang/String;Ljava/lang/String;)V
    invoke-virtual {{p0, v0}}, {handler}->openMenu(Landroid/os/Bundle;)V
    const-string v0, "FujiMovieShortcut"
    const-string v1, "Movie standby center: opening filter menu"
    invoke-static {{v0, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :done
    const/4 v0, 0x1
    return v0
.end method
'''
    for name in ('pushedEnter5WayFuncKey', 'pushedEnterJoyStickFuncKey'):
        assert f'.method public {name}()I' not in text
        text+=f'''
.method public {name}()I
    .locals 1
    invoke-virtual {{p0}}, {handler}->pushedCenterKey()I
    move-result v0
    return v0
.end method
'''
    path.write_text(text)
    app=base/'smali'/OLD.replace('.','/')/'PictureEffectPlus.smali'
    app.write_text(replace_method(app.read_text(),'getSupportingRecMode()I',
        '.method public getSupportingRecMode()I\n    .locals 1\n    const/4 v0, 0x3\n    return v0\n.end method'))
    # Use Sony's existing mode-aware exposure controller when movie mode is enabled.
    exposure=base/'smali'/OLD.replace('.','/')/'shooting/camera/PictureEffectPlusExposureModeController.smali'
    text=exposure.read_text()
    for name in ('getSupportedValue','getAvailableValue'):
        sig=name+'(Ljava/lang/String;)Ljava/util/List;'
        text=replace_method(text,sig,f'''.method public {sig}
    .locals 1
    invoke-super {{p0, p1}}, Lcom/sony/imaging/app/base/shooting/camera/ExposureModeController;->{sig}
    move-result-object v0
    return-object v0
.end method''')
    for signature, target in (
        ('getCautionId()I', 'getCautionId()I'),
        ('isValidDialPosition()Z', 'isValidDialPosition()Z'),
        ('isValidExpoMode(Ljava/lang/String;)Z', 'isValidValue(Ljava/lang/String;)Z'),
    ):
        args = 'p0, p1' if 'String' in signature else 'p0'
        text=replace_method(text,signature,f'''.method public {signature}
    .locals 1
    invoke-super {{{args}}}, Lcom/sony/imaging/app/base/shooting/camera/ExposureModeController;->{target}
    move-result v0
    return v0
.end method''')
    text=replace_method(text,'isValidDialPosition(I)Z','''.method public isValidDialPosition(I)Z
    .locals 1
    invoke-static {p1}, Lcom/sony/imaging/app/base/shooting/camera/ExposureModeController;->scancode2Value(I)Ljava/lang/String;
    move-result-object v0
    if-eqz v0, :invalid
    invoke-super {p0, v0}, Lcom/sony/imaging/app/base/shooting/camera/ExposureModeController;->isValidValue(Ljava/lang/String;)Z
    move-result v0
    return v0
    :invalid
    const/4 v0, 0x0
    return v0
.end method''')
    exposure.write_text(text)
    path=base/'smali/com/sony/imaging/app/base/shooting/movie/MovieShootingExecutor$MovieRecStartRunnable.smali'
    text=path.read_text()
    needle='    sget-object v2, Lcom/sony/imaging/app/base/shooting/movie/MovieShootingExecutor;->sMediaRecorder:Lcom/sony/scalar/media/MediaRecorder;'
    assert text.count(needle)==1
    prefix=f'''    invoke-static {{}}, {HOOK}->logMovieSettings()V
    invoke-static {{}}, {HOOK}->ensureForMovie()Z
    move-result v2
    if-nez v2, :fuji_movie_ready
    new-instance v2, Ljava/lang/IllegalStateException;
    const-string v3, "Film filter was not applied"
    invoke-direct {{v2, v3}}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V
    throw v2
    :fuji_movie_ready
'''
    path.write_text(text.replace(needle,prefix+needle))
    # The upstream callback logs "MovieRecError" even when error == 0.
    # Record the actual nonzero code so it cannot be confused with failure.
    path=base/'smali/com/sony/imaging/app/base/shooting/movie/MovieShootingExecutor$MovieRecErrorRunnable.smali'
    text=path.read_text()
    needle='    .line 465\n'
    assert text.count(needle)==1
    diagnostic='''    iget v1, p0, Lcom/sony/imaging/app/base/shooting/movie/MovieShootingExecutor$MovieRecErrorRunnable;->mError:I
    if-eqz v1, :fuji_error_checked
    const-string v2, "FujiMovieErrorCode"
    invoke-static {v1}, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v3
    invoke-static {v2, v3}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :fuji_error_checked
'''
    path.write_text(text.replace(needle,diagnostic+needle))
    # Read back recorder parameters after a menu change; never alter them here.
    path=base/'smali/com/sony/imaging/app/base/shooting/camera/MovieFormatController.smali'
    text=path.read_text()
    sig='setValue(Ljava/lang/String;Ljava/lang/String;)V'
    method=re.search(r'^\.method public '+re.escape(sig)+r'\n[\s\S]*?^\.end method',text,re.M).group()
    method=method.replace('    return-void',f'    invoke-static {{}}, {HOOK}->logMovieSettings()V\n    return-void')
    path.write_text(replace_method(text,sig,method))

def rename_package(base):
    assert len(OLD)==len(NEW)
    for path in base.rglob('*'):
        if not path.is_file():continue
        if path.suffix in ('.smali','.xml','.arsc'):
            data=path.read_bytes()
            for old,new in [(OLD,NEW),(OLD.replace('.','/'),NEW.replace('.','/')),
                            ('理光相机',APP_NAME)]:
                for encoding in ('utf-8','utf-16le'):
                    a,b=old.encode(encoding),new.encode(encoding)
                    assert len(a)==len(b)
                    data=data.replace(a,b)
            if path.suffix=='.smali':
                data=data.replace(b'\\u7406\\u5149\\u76f8\\u673a',APP_NAME.encode('unicode_escape'))
            if path.name=='AndroidManifest.xml' and path.parent==base:
                for encoding in ('utf-8','utf-16le'):
                    data=data.replace('1.31'.encode(encoding),ANDROID_VERSION.encode(encoding))
            path.write_bytes(data)
    source=base/'smali'/OLD.replace('.','/')
    dest=base/'smali'/NEW.replace('.','/')
    dest.parent.mkdir(parents=True,exist_ok=True)
    source.rename(dest)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--apktool',type=Path,required=True)
    ap.add_argument('--upstream-hook',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--movie',action='store_true',help='Enable experimental Sony movie path')
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    if hashlib.sha256(args.input.read_bytes()).hexdigest()!=EXPECTED:
        raise SystemExit('Input hash mismatch: this patch requires the tested upstream v1.1.4 APK')
    if hashlib.sha256(args.upstream_hook.read_bytes()).hexdigest()!=EXPECTED_HOOK:
        raise SystemExit('Hook hash mismatch: use the pinned upstream revision in the installation guide')
    if args.work.exists() and any(args.work.iterdir()):
        raise SystemExit('Work directory is not empty. Choose a fresh directory; no existing files were removed.')
    for folder in ('profiles', 'output', 'validation'):
        (root/folder).mkdir(parents=True, exist_ok=True)
    if not (root/'profiles/fuji_official_approx.json').exists():
        raise SystemExit('No local profiles. Follow the rights/input checks and fit_luts.py step in docs/INSTALL.en.md.')
    fuji=json.loads((root/'profiles/fuji_official_approx.json').read_text())['presets']
    profiles=combined_profiles(fuji,args.upstream_hook)
    subprocess.run(['java','-jar',str(args.apktool),'d','-r','-f',str(args.input),'-o',str(args.work)],check=True)
    patch_hook(args.work/'smali'/OLD.replace('.','/')/'shooting/camera/RicohHook.smali',profiles,args.upstream_hook,args.movie)
    patch_menu(args.work,profiles)
    if args.movie:patch_movie(args.work)
    rename_package(args.work)
    # Keep attribution and license scope with the installable artifact itself.
    legal=args.work/'assets/legal'
    legal.mkdir(parents=True,exist_ok=True)
    for source,name in (
        ('LICENSE','LICENSE-PolyForm-Noncommercial-1.0.0.txt'),
        ('LICENSES/Apache-2.0.txt','LICENSE-Apache-2.0.txt'),
        ('NOTICE','NOTICE.txt'),
        ('LICENSING.md','LICENSING.md'),
    ):
        shutil.copyfile(root/source,legal/name)
    unsigned=args.work.parent/'film-studio-unsigned.apk'
    subprocess.run(['java','-jar',str(args.apktool),'b',str(args.work),'-o',str(unsigned)],check=True)
    key=root/'.private/signing.pem'
    key.parent.mkdir(exist_ok=True)
    if not key.exists():
        generated,_=ensure_pem()
        shutil.move(generated,key)
        key.chmod(0o600)
    output=root/'output'/('FilmStudio-'+VERSION+('-movie.apk' if args.movie else '-photo.apk'))
    sign_apk(str(unsigned),str(output),str(key))
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert z.read('classes.dex')[:8]==b'dex\n035\0'
    metadata=dict(file=output.name,package=NEW,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  version=VERSION,movie_enabled=args.movie,
                  camera_tested=False,encoded_video_filter_verified=False,
                  source_apk_sha256=EXPECTED,profiles=len(profiles),
                  app_name=APP_NAME,android_version=ANDROID_VERSION,
                  profile_families={'fujifilm':10,'ricoh':5})
    (root/'profiles/film_studio.json').write_text(json.dumps(dict(
        version=VERSION,presets=profiles),ensure_ascii=False,indent=2))
    (root/'validation'/(output.stem+'.json')).write_text(json.dumps(metadata,indent=2))
    print('Built:',output)

if __name__=='__main__':main()
