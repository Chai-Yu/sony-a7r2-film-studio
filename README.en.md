# 胶片工坊 / Film Studio

[中文](README.md) · **English** · [日本語](README.ja.md)

An unofficial film-look experiment for the **Sony a5100 / ILCE-5100 and a7R II / ILCE-7RM2**. It references the hardware color-processing approach in [bonyback1's Ricoh mod](https://github.com/bonyback1/sony-pmca-ricoh-mod) and uses [Fujifilm's publicly available GFX ETERNA 55 LUTs](https://www.fujifilm-x.com/global/support/download/lut/) as color-research references for photographs and experimental video.

**Version: 0.2.1-alpha (release tag `v0.2.1-alpha`; the on-camera version string is still 0.2a); app name: 胶片工坊.** Documentation is available in three languages; the camera UI is currently primarily Chinese.

**Renamed to Film Studio (胶片工坊), combining ten Fujifilm-reference and five upstream Ricoh/street-style presets, fifteen in total.** Menu labels use 富士 / 理光 prefixes. The package and signing certificate are retained for an in-place update from 富士风格. The combined build installed and launched on the a5100, with successful parameter-application logs for selected presets; saved photographs/video from this version remain unverified. The earlier [0.1.3-alpha](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/tag/v0.1.3-alpha) (upstream repository) remains available for rollback.

**This download also contains the 2026-09-14 fix:** pressing MENU on the chooser that the center button opened used to wedge the app's state machine — the layout closed while the menu state stayed on the stack, after which no key responded and only a power cycle recovered the camera. It is fixed and was verified on an a7R II across dozens of round trips. The chooser stays fully transparent so the live preview is not covered.

<a id="compatibility"></a>

## Camera compatibility

**Only the a5100 and the a7R II have been tested by this project. This app does not work with every Sony camera.**

| Model | Status in this project |
| --- | --- |
| **a5100 / ILCE-5100, firmware 1.10** | Tested within the feature/version limits documented below |
| a6000, a6300, a6500 | PMCA candidates listed upstream; this version is untested |
| **a7R II / ILCE-7RM2, Android 4.1.2 / API 16** | Install, startup and the "center button opens the chooser → MENU returns to shooting" round trip were tested (2026-09-14). **This body reports no support for the RGB matrix or the extended gamma table**, so imaging falls back to the camera's own Creative Style + native Picture Effect approximation (see [live-preview notes](docs/LIVE-PREVIEW.zh-CN.md)) rather than this project's fitted Fujifilm/Ricoh parameters. Photograph/video saving and colour were not verified on this model |
| a7, a7R, a7S, a7 II, a7S II | PMCA candidates listed upstream; this version is untested |
| RX100 III/IV/V, RX10 II/III, RX1R II, HX90 | PMCA candidates listed upstream; this version is untested |
| a6400, a6700, a7 III, a7C | Do not support the PlayMemories Camera Apps installation platform required here |
| Other models or firmware | Not assessed; a similar model name does not establish compatibility |

Candidates come from the [upstream model list](https://github.com/bonyback1/sony-pmca-ricoh-mod/blob/7c565898562c73c5073c54dfc831c8c3df9c24cf/README.md), not tests of this project's added video and strength features. PMCA is the on-camera app platform required here; MTP or phone remote control alone does not establish PMCA support.

**The current video menu follows a5100 specifications and includes no 4K choices.** It does not promise every native format, frame rate or bitrate on other models. Successful installation must be followed by separate checks of preview, look selection, JPEG persistence, recording start/stop, saved-video playback and color reset after exit. Actual colors may differ across models. Reports should identify model, firmware, app version and exactly what was tested.

## Download and installation

**[Download APK: 0.2.1-alpha (includes the 2026-09-14 fix)](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/download/v0.2.1-alpha/FilmStudio-0.2.0-alpha-movie.apk)** · [Release notes](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/tag/v0.2.1-alpha)

- File: `FilmStudio-0.2.0-alpha-movie.apk` (3,785,488 bytes)
- SHA-256: `2b42cf90b4a5cba1458b1e8865d88c509779a46bb1d4a876c66ab41e049fb120`

Then follow the [English installation guide](docs/INSTALL.en.md) to install it; no local compilation is required. **If you only want to install and shoot, take "Method A"**: set the camera's USB mode to MTP and install the APK with pmca-gui — no developer mode and no command line. **Code → Download ZIP contains source, not the installer.**

This is an unofficial experimental release with only the a5100 and a7R II evidence described above. The APK contains Sony base-app material and parameters fitted from publicly available Fujifilm LUTs. A separate grant to adapt and redistribute those third-party materials has not been established. Publication does not represent Sony/FUJIFILM permission or guarantee immunity; [license scope](LICENSING.md) distinguishes the rights in each part. Original official LUT files and signing private keys are not distributed.

→ **[Complete English installation guide](docs/INSTALL.en.md)**: inputs → local build → USB (pmca-gui) / Wi-Fi ADB installation → camera controls → updates and troubleshooting.

With your own lawfully built APK and Wi-Fi ADB already enabled:

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r output/FilmStudio-0.2.0-alpha-movie.apk
```

**IP address and privacy:** `CAMERA_IP` is a placeholder. Replace it with the current IP shown on your own camera in Tweak → Developer; do not type the placeholder literally or copy someone else's address. Keep the `:5555` port. Public instructions use a placeholder; hide or remove actual IP addresses before sharing screenshots or logs.

First-time users also need the preparation steps in the guide.

### Does the APK recipient need to compile anything?

**No. A signed APK can be installed through the documented procedure; runtime compatibility still depends on the camera and environment.** Recipients do not need Python, Java, Apktool or the private signing key. The local build chapters are for modifying or generating an APK yourself; doing so does not itself resolve third-party permissions.

## Features

- Ten Fujifilm official-LUT reference looks: PROVIA, Velvia, ASTIA, CLASSIC CHROME, REALA ACE, PRO Neg. Std, CLASSIC Neg., ETERNA, ETERNA BLEACH BYPASS and ACROS.
- Five upstream Ricoh/street styles: GR Positive Film, Negative Film, High Contrast B&W, Moriyama Daido Style and Cross Process. Community presets, not official Ricoh LUTs.
- Press the center button to select a look in still preview or movie standby.
- MENU page 1 「滤镜强度」(filter strength): **30%, 50%, 70%, 100%**. Starts at 70%; shared by stills and video and saved through normal app exit.
- MENU page 1 →「拍照／录像模式」(still/movie mode) → movie P/A/S/M, then「录像文件格式」(format) and「录像帧率／画质」(frame rate/quality). Choices follow the camera's supported XAVC S, AVCHD and MP4 profiles and current PAL/NTSC system.
- MOVIE starts/stops recording. Look and strength stay fixed during recording.
- White balance remains available on MENU page 4. The app uses STD/Standard with contrast, saturation and sharpness at zero as its baseline; native Portrait/Vivid Creative Styles are not stacked in this app.
- Separate package `com.yuki.imaging.app.pictureeffectplus`, allowing coexistence with the original Ricoh mod.

For portraits, compare 30% and 70% first. On colour looks the strength reduces both the colour matrix and the tone curve; it does not detect faces or automatically repair skin tones. **ACROS, Ricoh High Contrast B&W and Moriyama style never carry colour at any strength: the strength only lowers contrast, and 100% is the look's own contrast.**

## Evidence and limits

Hardware testing covers two bodies; neither promises compatibility with other models.

- **a5100 / ILCE-5100, firmware 1.10, Android 2.3.7 / API 10**: the body supports the 3×3 RGB matrix and the extended gamma table, so this project's fitted hardware-colour parameters are used.
- **a7R II / ILCE-7RM2, Android 4.1.2 / API 16**: the body reports no support for either, so imaging automatically falls back to Creative Style + native Picture Effect (see [live-preview notes](docs/LIVE-PREVIEW.zh-CN.md)) instead of the fitted parameters.

- 0.1.1: all ten look selections applied; PROVIA color and ACROS monochrome JPEGs saved; an ACROS XAVC S 1080p59.94 clip saved and fully decoded.
- 0.1.2: the user confirmed format/quality menus were usable. Every encoded format has not been inspected.
- 0.1.3: installation, startup and default-look application verified; the user gave general confirmation of the new controls. Every look/strength/format combination has not been tested in saved media.
- 2026-09-14 (a7R II): installation, startup and dozens of "center button opens the chooser → MENU returns to shooting" round trips all behaved correctly. That path used to wedge the state machine — the layout closed while the menu state stayed on the stack, after which no key responded and only a power cycle recovered the camera; it is now fixed. The fix was not re-tested on the a5100, and saved media and colour remain unverified on both bodies for this version.

**In-app playback currently lists photographs only.** Exit to native playback and choose the appropriate XAVC S, AVCHD or MP4 view to see movies. See [validation notes](docs/VALIDATION.md).

This is not a complete port of Fujifilm's in-camera Film Simulation. F-Log2/F-Gamut LUTs cannot be applied directly to ordinary Sony imagery. The fitting process uses WDR-709 as a proxy neutral reference, producing a 3×3 matrix and a common 1024-point curve. The a5100 has not been color-calibrated for this model; grain and sensor response are not simulated, and some looks have substantial approximation error.

## License, ownership and sources

Original project contributions use **[PolyForm Noncommercial 1.0.0](LICENSE)**. This is noncommercial source-available software, not an OSI open-source license. Commercial use is not granted under this license; its exact scope and exceptions are controlled by the original text. Third-party licenses remain separate and their existing rights are not revoked.

**Official Fujifilm LUTs and associated material belong to Fujifilm and their respective rights holders. Referencing them is not official authorization.** This project does not represent Sony, FUJIFILM or Ricoh. Attribution, noncommercial terms and disclaimers do not replace permission or guarantee immunity.

- [License scope and ownership, three languages](LICENSING.md)
- [Third-party notices and modifications](NOTICE)
- [Sources](docs/SOURCES.md)
- [Rights inquiries](docs/RIGHTS.md)

Except where applicable law requires otherwise, the software is provided as is without promises of compatibility, color accuracy or non-infringement. Back up your card and test with disposable footage. Nothing here excludes liability that cannot lawfully be excluded.
