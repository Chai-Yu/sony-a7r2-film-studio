# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Original additions only; underlying third-party rights remain separate. See LICENSING.md and NOTICE.
"""Expose the a5100's native movie settings without inventing recorder profiles."""
import copy
import xml.etree.ElementTree as ET

CONTROLLER = 'com.sony.imaging.app.base.shooting.camera.MovieFormatController'
FORMATS = [('XAVC_S', 'XAVC S'), ('AVCHD', 'AVCHD'), ('MP4', 'MP4')]
# Sony ILCE-5100 Help Guide, Record Setting (movie), TP0000301880.
# The controller filters these by format, PAL/NTSC and actual device support.
PROFILES = [(f'XAVC_50M_{rate}p', f'1080/{rate}p 50M')
            for rate in (60, 50, 30, 25, 24)]
PROFILES += [(f'PS_{rate}p', f'1080/{rate}p 28M (PS)') for rate in (60, 50)]
PROFILES += [(f'{quality}_{rate}{scan}', f'1080/{rate}{scan} {bitrate}M ({quality})')
             for rate, scan in ((60, 'i'), (50, 'i'), (24, 'p'), (25, 'p'))
             for quality, bitrate in (('FX', 24), ('FH', 17))]
PROFILES += [('MP4_1080', '1440x1080 12M'), ('MP4_VGA', 'VGA 3M')]

ID_FORMAT = 'FujiMovieFormat'
ID_QUALITY = 'FujiMovieQuality'
GUIDE = '先在拍照／录像模式中选择动态影像 P/A/S/M，再设置录像参数。'
LABELS = {
    'ExposureMode': ('拍照／录像模式', '选择拍照 P/A/S/M，或动态影像 P/A/S/M 进入录像待机。'),
    ID_FORMAT: ('录像文件格式', GUIDE),
    ID_QUALITY: ('录像帧率／画质', GUIDE),
}
for key, rows in ((ID_FORMAT, FORMATS), (ID_QUALITY, PROFILES)):
    for value, name in rows:
        LABELS[key+'_'+value] = (name, '选择相机当前支持的录像设置；M 表示 Mbps。')
LABELS[ID_QUALITY+'_MP4_1080'] = ('1440x1080 12M', 'MP4：1440x1080，约 12 Mbps；NTSC 约 30p，PAL 约 25p。')
LABELS[ID_QUALITY+'_MP4_VGA'] = ('VGA 3M', 'MP4：640x480，约 3 Mbps；NTSC 约 30p，PAL 约 25p。')


def patch_movie_menu(base):
    path = base/'assets/MenuData.xml'
    tree = ET.parse(path)
    root = tree.getroot()
    page1 = next(e for e in root if e.get('ItemId') == 'Page1')
    page2 = next(e for e in root if e.get('ItemId') == 'Page2')
    exposure = next(e for e in page2 if e.get('ItemId') == 'ExposureMode')
    page2.remove(exposure)
    # Replace the upstream empty ApplicationSettings slot; keep five pages.
    for child in list(page1):
        if child.get('ItemId') == 'ApplicationSettings':
            page1.remove(child)
    page1.append(exposure)
    source = next(e for e in root.iter() if e.get('ItemId') == 'Still_ImageSize')
    icon = next(e for e in root.iter()
                if e.get('ItemId') == 'ExposureMode_movie_ProgramAuto').get('IconRes')
    for key, tag, rows in ((ID_FORMAT, 'movie_format_menu', FORMATS),
                           (ID_QUALITY, 'record_setting', PROFILES)):
        menu = copy.deepcopy(source)
        for child in list(menu):
            menu.remove(child)
        for attr in list(menu.attrib):
            if attr.startswith('Fn') or attr in ('UpdateTag', 'CustomStartLayoutID'):
                del menu.attrib[attr]
        menu.attrib.update(ItemId=key, Value=tag, ConfigClass=CONTROLLER,
                           CautionID='CAUTION_ID_INVALID_THIS_FUNCTION',
                           IconRes=icon, SelectedIconRes=icon)
        for value, name in rows:
            attrs = dict(menu.attrib)
            attrs.update(ItemId=key+'_'+value, Value=value, ExecType='SET_VALUE', NextMenuID='')
            ET.SubElement(menu, 'Layer2', attrs)
        page1.append(menu)
    tree.write(path, encoding='utf-8', xml_declaration=True)
