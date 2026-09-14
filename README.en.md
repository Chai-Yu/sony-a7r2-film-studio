# 胶片工坊 / Film Studio

[中文](README.md) · **English** · [日本語](README.ja.md)

An unofficial film-look experiment for the **Sony a5100 / ILCE-5100 and a7R II / ILCE-7RM2**. It references the hardware color-processing approach in [bonyback1's Ricoh mod](https://github.com/bonyback1/sony-pmca-ricoh-mod) and uses [Fujifilm's publicly available GFX ETERNA 55 LUTs](https://www.fujifilm-x.com/global/support/download/lut/) as color-research references for photographs and experimental video.

## Version

- **Current version: `0.2.2-alpha`** - release tag `v0.2.2-alpha`, on-camera version string `0.2.2` (`0.2.2a` for the white-anchored variant). App name: 胶片工坊.
- **Seventeen looks** in all: ten Fujifilm official-LUT reference styles, five upstream Ricoh/street styles and two Leica Look reference styles. Menu labels use 富士 / 理光 / 徕卡 prefixes.
- The package and signing certificate are retained, so this updates in place. The earlier [0.1.3-alpha](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/tag/v0.1.3-alpha) (upstream repository) remains available for rollback.

The measurements behind each version are in the [validation notes](docs/VALIDATION.md).

<a id="compatibility"></a>

## Camera compatibility

**Only the a5100 and the a7R II have been tested by this project. This app does not work with every Sony camera.**

| Model | Status in this project |
| --- | --- |
| **a5100 / ILCE-5100, firmware 1.10** | Tested; see "Evidence and limits" below for the feature and version range |
| **a7R II / ILCE-7RM2, Android 4.1.2 / API 16** | Install, startup and the "centre button opens the chooser → MENU returns to shooting" round trip were tested (2026-09-14). The body's `isRGBMatrixSupported()` and `isExtendedGammaTableSupported()` both return false, but measurement shows **both are honoured**; the app therefore writes the RGB matrix and the extended gamma table **unconditionally**, as the upstream Ricoh mod does. It does **not** accept `setColorMode()` or `setPictureEffect()` writes, so `applyNative()`, which asks the camera to apply its own style, has no effect on this body. Photograph/video saving and colour were not verified item by item on this model |
| a6000, a6300, a6500 | PMCA candidates listed upstream; this version is untested |
| a7, a7R, a7S, a7 II, a7S II | PMCA candidates listed upstream; this version is untested |
| RX100 III/IV/V, RX10 II/III, RX1R II, HX90 | PMCA candidates listed upstream; this version is untested |
| a6400, a6700, a7 III, a7C | Do not support the PlayMemories Camera Apps installation platform required here |
| Other models or firmware | Not assessed; a similar model name does not establish compatibility |

Candidates come from the [upstream model list](https://github.com/bonyback1/sony-pmca-ricoh-mod/blob/7c565898562c73c5073c54dfc831c8c3df9c24cf/README.md), not tests of this project's added video and strength features. PMCA is the on-camera app platform required here; MTP or phone remote control alone does not establish PMCA support.

**The current video menu follows a5100 specifications and includes no 4K choices.** It does not promise every native format, frame rate or bitrate on other models. Successful installation must be followed by separate checks of preview, look selection, JPEG persistence, recording start/stop, saved-video playback and color reset after exit. Actual colors may differ across models. Reports should identify model, firmware, app version and exactly what was tested.

## Download and installation

**[Download APK: 0.2.2-alpha (adds the Leica styles)](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/download/v0.2.2-alpha/FilmStudio-0.2.2-alpha-movie.apk)** · [Release notes](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/tag/v0.2.2-alpha)

- File: `FilmStudio-0.2.2-alpha-movie.apk` (3,789,781 bytes) - the default `faithful` tone treatment
- SHA-256: `5a6417043e9fe9bba470f7d10d61440c1227a10ba835734748b325e43c752ad3`
- White-anchored companion: `FilmStudio-0.2.2-alpha-movie-leica-anchor.apk` (3,790,896 bytes, SHA-256 `c5ebc6799258dfbc091657902bbb593e01ad7d1d737738d9a469a211e7e2f0c2`) - keeps white at white instead of darkening globally. **The two differ only in the Leica tone output**; they share one matrix, so which to use is a judgement on real footage.

Then follow the [English installation guide](docs/INSTALL.en.md) to install it; no local compilation is required. **If you only want to install and shoot, take "Method A"**: set the camera's USB mode to MTP and install the APK with pmca-gui - no developer mode and no command line. **Code → Download ZIP contains source, not the installer.**

This is an unofficial experimental release with only the a5100 and a7R II evidence described above. The APK contains Sony base-app material and parameters fitted from publicly available Fujifilm LUTs. A separate grant to adapt and redistribute those third-party materials has not been established. Publication does not represent Sony/FUJIFILM permission or guarantee immunity; [license scope](LICENSING.md) distinguishes the rights in each part. Original official LUT files and signing private keys are not distributed.

With your own lawfully built APK and Wi-Fi ADB already enabled:

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r output/FilmStudio-0.2.2-alpha-movie.apk
```

**IP address and privacy:** `CAMERA_IP` is a placeholder. Replace it with the current IP shown on your own camera in Tweak → Developer; do not type the placeholder literally or copy someone else's address. Keep the `:5555` port. Public instructions use a placeholder; hide or remove actual IP addresses before sharing screenshots or logs.

The full procedure is in the [English installation guide](docs/INSTALL.en.md): inputs → local build → USB (pmca-gui) / Wi-Fi ADB installation → camera controls → updates and troubleshooting. First-time users also need the preparation steps in that guide.

### Does the APK recipient need to compile anything?

**No. A signed APK can be installed through the documented procedure; runtime compatibility still depends on the camera and environment.** Recipients do not need Python, Java, Apktool or the private signing key. The local build chapters are for modifying or generating an APK yourself; doing so does not itself resolve third-party permissions.

## Features

- Ten Fujifilm official-LUT reference looks: PROVIA, Velvia, ASTIA, CLASSIC CHROME, REALA ACE, PRO Neg. Std, CLASSIC Neg., ETERNA, ETERNA BLEACH BYPASS and ACROS.
- Five upstream Ricoh/street styles: GR Positive Film, Negative Film, High Contrast B&W, Moriyama Daido Style and Cross Process. Community presets, not official Ricoh LUTs.
- Two Leica Look reference styles: Classic and Natural, fitted from Leica's official SL2-S L-Log LUTs. **Leica publishes no neutral reference LUT**, so the baseline rendering is constructed by this project from the L-Log specification rather than taken from Leica.
- Press the centre button to select a look in still preview or movie standby.
- MENU page 1 「滤镜强度」 (filter strength): **30%, 50%, 70%, 100%**. Starts at 70%; shared by stills and video, saved through normal app exit. **100% is the look's own full strength**; lower settings reduce colour and tone together.
- MENU page 1 →「拍照／录像模式」 (still/movie mode) → movie P/A/S/M, then 「录像文件格式」 (format) and 「录像帧率／画质」 (frame rate/quality). Choices follow the camera's supported XAVC S, AVCHD and MP4 profiles and the current PAL/NTSC system.
- MOVIE starts/stops recording. Look and strength stay fixed during recording.
- White balance remains available on MENU page 4. The app uses STD/Standard with contrast, saturation and sharpness at zero as its baseline; native Portrait/Vivid Creative Styles are not stacked in this app.
- Separate package `com.yuki.imaging.app.pictureeffectplus`, allowing coexistence with the original Ricoh mod.

For portraits, compare 30% and 70% first. On colour looks the strength reduces both the colour matrix and the tone curve; it does not detect faces or automatically repair skin tones.

**ACROS, Ricoh High Contrast B&W and Moriyama style never carry colour at any strength**: the strength only lowers contrast, and 100% is the look's own contrast.

## Colour mechanism

- Each look is **one 3×3 colour matrix plus a 1024-point tone curve**, written into the camera's RGB matrix and extended gamma table. **The two only work as a pair**: the matrix is calibrated against the curve it was fitted with, and applying it alone does not reproduce the look.
- The parameters are fitted from Fujifilm's published LUTs. Those LUTs take F-Log2 / F-Gamut input, which cannot be applied to ordinary Sony imagery, so **WDR-709 serves as a substitute neutral reference** and the matrix and curve are fitted for ordinary footage.
- The Fujifilm **chroma** response is calibrated separately against real a7R II shots: five scenes, each shot three times (camera Neutral, camera STD, app output), which corrects the matrix's chroma response so that 100% strength sits closer to the official look.
- Leica publishes look LUTs with no neutral reference, so its baseline rendering is constructed by this project from the L-Log specification. The Ricoh parameters come from the upstream project and are unchanged.

## Evidence and limits

Hardware testing covers two bodies; neither promises compatibility with other models.

- **a5100 / ILCE-5100, firmware 1.10, Android 2.3.7 / API 10**: the body supports the 3×3 RGB matrix and the extended gamma table, so this project's fitted hardware-colour parameters are used.
- **a7R II / ILCE-7RM2, Android 4.1.2 / API 16**: the body's capability query reports no support for either, but measurement shows both are honoured, so the fitted parameters are used here too. The Creative Style and Picture Effect writes are not accepted - see the [live-preview notes](docs/LIVE-PREVIEW.zh-CN.md).

Version history:

- 0.1.1: all ten look selections applied; PROVIA color and ACROS monochrome JPEGs saved; an ACROS XAVC S 1080p59.94 clip saved and fully decoded.
- 0.1.2: the user confirmed the format/quality menus were usable. Every encoded format has not been inspected.
- 0.1.3: installation, startup and default-look application verified; the user gave general confirmation of the new controls. Every look/strength/format combination has not been tested in saved media.
- 0.2.2 (a7R II, 2026-09-14): installation, startup and dozens of "centre button opens the chooser → MENU returns to shooting" round trips all behaved correctly. The Fujifilm chroma calibration was completed the same day from five shot triples. The a5100 has not been re-tested item by item, and saved media and colour remain unverified on both bodies for this version.

**In-app playback currently lists photographs only.** Exit to native playback and choose the appropriate XAVC S, AVCHD or MP4 view to see movies.

**Where the approximation stops:** this is not a complete port of Fujifilm's in-camera Film Simulation, and grain or sensor response is not simulated. The a5100 has not had the same real-shot chroma calibration as the a7R II; individual looks deviate from the official LUT more visibly than others.

## License, ownership and sources

Original project contributions use **[PolyForm Noncommercial 1.0.0](LICENSE)**. This is noncommercial source-available software, not an OSI open-source license. Commercial use is not granted under this license; its exact scope and exceptions are controlled by the original text. Third-party licenses remain separate and their existing rights are not revoked.

**Official Fujifilm LUTs and associated material belong to Fujifilm and their respective rights holders. Referencing them is not official authorization.** This project does not represent Sony, FUJIFILM or Ricoh. Attribution, noncommercial terms and disclaimers do not replace permission or guarantee immunity.

- [License scope and ownership, three languages](LICENSING.md)
- [Third-party notices and modifications](NOTICE)
- [Sources](docs/SOURCES.md)
- [Rights inquiries](docs/RIGHTS.md)

Except where applicable law requires otherwise, the software is provided as is without promises of compatibility, color accuracy or non-infringement. Back up your card and test with disposable footage. Nothing here excludes liability that cannot lawfully be excluded.
