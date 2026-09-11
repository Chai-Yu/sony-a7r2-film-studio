# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Four strengths, interpolating the custom matrix/curve toward identity.

This is parameter interpolation, not a per-pixel opacity blend. Keep the 100%
endpoint bit-identical, including upstream presets with intentional neutral tint.
"""
import copy
import xml.etree.ElementTree as ET

STRENGTHS = (30, 50, 70, 100)
TAG = 'FujiStrength'
KEY = 'ID_FUJI_FILTER_STRENGTH'
LABELS = {TAG: ('滤镜强度', '30% 较淡，100% 为完整效果；拍照和录像共用，记住上次选择。')}
LABELS.update({f'{TAG}_{s}': (f'{s}%', '同时减弱色彩变化和明暗曲线；100% 保持原有效果。')
               for s in STRENGTHS})


def blend_profile(profile, strength):
    if not 0 <= strength <= 100:
        raise ValueError('Strength outside 0–100')
    matrix = []
    for row, values in enumerate(profile['matrix']):
        blended = [round(((1024 if column == row else 0) * (100-strength)
                          + value * strength) / 100)
                   for column, value in enumerate(values)]
        # Preserve the existing Fuji rounding exactly. Do not normalize tinted
        # upstream Ricoh rows: that would change even their 100% endpoint.
        if sum(values) == 1024:
            blended[row] = 1024 - sum(v for column, v in enumerate(blended) if column != row)
        matrix.append(blended)
    gamma = [round((i * (100-strength) + value * strength) / 100)
             for i, value in enumerate(profile['gamma'])]
    return dict(matrix=matrix, gamma=gamma)


def patch_strength_menu(base, controller):
    path = base/'assets/MenuData.xml'
    tree = ET.parse(path)
    root = tree.getroot()
    page1 = next(e for e in root if e.get('ItemId') == 'Page1')
    source = next(e for e in root.iter() if e.get('ItemId') == 'Still_ImageSize')
    menu = copy.deepcopy(source)
    for child in list(menu):
        menu.remove(child)
    for attr in list(menu.attrib):
        if attr.startswith('Fn') or attr in ('UpdateTag', 'CustomStartLayoutID'):
            del menu.attrib[attr]
    menu.attrib.update(ItemId=TAG, Value=TAG, ConfigClass=controller,
                       CautionID='CAUTION_ID_INVALID_THIS_FUNCTION',
                       IconRes='drawable/s_16_dd_parts_bm_appsettings',
                       SelectedIconRes='drawable/s_16_dd_parts_bm_appsettings')
    for s in STRENGTHS:
        attrs = dict(menu.attrib)
        attrs.update(ItemId=f'{TAG}_{s}', Value=str(s), ExecType='SET_VALUE', NextMenuID='')
        ET.SubElement(menu, 'Layer2', attrs)
    page1.insert(2, menu)
    tree.write(path, encoding='utf-8', xml_declaration=True)


def strength_methods(hook, controller):
    backup = 'Lcom/sony/imaging/app/util/BackUpUtil;'
    lines = ['.method public static getStrengthValues()Ljava/util/List;', '    .locals 2',
             '    new-instance v0, Ljava/util/ArrayList;',
             '    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V']
    for s in STRENGTHS:
        lines += [f'    const-string v1, "{s}"',
                  '    invoke-virtual {v0, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z']
    lines += ['    return-object v0', '.end method']
    lines += [f'''
.method public static getStrength()I
    .locals 3
    :try_start
    invoke-static {{}}, {backup}->getInstance(){backup}
    move-result-object v0
    const-string v1, "{KEY}"
    const/16 v2, 0x64
    invoke-virtual {{v0, v1, v2}}, {backup}->getPreferenceInt(Ljava/lang/String;I)I
    move-result v0
    :try_end
    .catch Ljava/lang/Throwable; {{:try_start .. :try_end}} :catch
    const/16 v1, 0x1e
    if-eq v0, v1, :valid
    const/16 v1, 0x32
    if-eq v0, v1, :valid
    const/16 v1, 0x46
    if-eq v0, v1, :valid
    const/16 v0, 0x64
    :valid
    return v0
    :catch
    move-exception v0
    const/16 v0, 0x64
    return v0
.end method

.method public static getStrengthValue()Ljava/lang/String;
    .locals 1
    invoke-static {{}}, {hook}->getStrength()I
    move-result v0
    invoke-static {{v0}}, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method

.method public static setStrengthValue({controller}Ljava/lang/String;)V
    .locals 7
    invoke-static {{}}, Lcom/sony/imaging/app/base/shooting/movie/MovieShootingExecutor;->isMovieRecording()Z
    move-result v0
    if-nez v0, :done
    invoke-static {{}}, {hook}->getStrengthValues()Ljava/util/List;
    move-result-object v0
    invoke-interface {{v0, p1}}, Ljava/util/List;->contains(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :done
    invoke-static {{}}, {hook}->getStrength()I
    move-result v1
    invoke-static {{p1}}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I
    move-result v2
    invoke-static {{}}, {backup}->getInstance(){backup}
    move-result-object v3
    const-string v4, "{KEY}"
    invoke-static {{v2}}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    invoke-virtual {{v3, v4, v5}}, {backup}->setPreference(Ljava/lang/String;Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :done
    invoke-virtual {{p0}}, {controller}->getBackupEffectValue()Ljava/lang/String;
    move-result-object v5
    const/4 v6, 0x0
    invoke-static {{p0, v6, v5}}, {hook}->applyHook({controller}Landroid/util/Pair;Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :success
    # Restore the previous selection and hardware if applying the new one fails.
    invoke-static {{v1}}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    invoke-virtual {{v3, v4, v0}}, {backup}->setPreference(Ljava/lang/String;Ljava/lang/Object;)Z
    invoke-static {{p0, v6, v5}}, {hook}->applyHook({controller}Landroid/util/Pair;Ljava/lang/String;)Z
    const-string v0, "FujiStrength"
    const-string v1, "Apply failed; previous preference restored; hardware restore attempted"
    invoke-static {{v0, v1}}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    return-void
    :success
    const-string v0, "FujiStrength"
    invoke-static {{v0, p1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :done
    return-void
.end method
''']
    return '\n'.join(lines)
