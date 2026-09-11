# A5100 Film Studio

[中文](README.md) · **English** · [日本語](README.ja.md)

An unofficial film-look experiment for the **Sony a5100 / ILCE-5100**. It references the hardware color-processing approach in [bonyback1's Ricoh mod](https://github.com/bonyback1/sony-pmca-ricoh-mod) and uses [Fujifilm's publicly available GFX ETERNA 55 LUTs](https://www.fujifilm-x.com/global/support/download/lut/) as color-research references for photographs and experimental video.

**Version: 0.1.3-alpha; on-camera version: 0.1d; app name: 富士风格.** Documentation is available in three languages; the camera UI is currently primarily Chinese.

## Download and installation

This repository distributes source, patch generators and documentation. **It does not distribute APKs, official Fujifilm LUTs or fitted parameter tables.** Permission to modify and redistribute those third-party materials has not been established. Check the rights for your inputs and intended use before building locally; owning a camera or downloading a file for free does not establish those permissions.

→ **[Complete English installation guide](docs/INSTALL.en.md)**: inputs → local build → first-time connection → Wi-Fi ADB installation → camera controls → updates and troubleshooting.

With your own lawfully built APK and Wi-Fi ADB already enabled:

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r output/FujiStyle-0.1.3-alpha-movie.apk
```

Replace `CAMERA_IP` with the camera's actual address. First-time users also need the preparation steps in the guide.

## Features

- Ten official-LUT reference looks: PROVIA, Velvia, ASTIA, CLASSIC CHROME, REALA ACE, PRO Neg. Std, CLASSIC Neg., ETERNA, ETERNA BLEACH BYPASS and ACROS.
- Press the center button to select a look in still preview or movie standby.
- MENU page 1 →「滤镜强度」(filter strength): **30%, 50%, 70%, 100%**. Starts at 100%; shared by stills and video and saved through normal app exit.
- MENU page 1 →「拍照／录像模式」(still/movie mode) → movie P/A/S/M, then「录像文件格式」(format) and「录像帧率／画质」(frame rate/quality). Choices follow the camera's supported XAVC S, AVCHD and MP4 profiles and current PAL/NTSC system.
- MOVIE starts/stops recording. Look and strength stay fixed during recording.
- White balance remains available on MENU page 4. The app uses STD/Standard with contrast, saturation and sharpness at zero as its baseline; native Portrait/Vivid Creative Styles are not stacked in this app.
- Separate package `com.yuki.imaging.app.pictureeffectplus`, allowing coexistence with the original Ricoh mod.

For portraits, compare 30% and 50% first. Strength reduces both the color matrix and tone curve; it does not detect faces or automatically repair skin tones. **ACROS below 100% retains some color. Use 100% for monochrome.**

## Evidence and limits

Tested on one **a5100, firmware 1.10, Android 2.3.7 / API 10**. Other models are not promised to work.

- 0.1.1: all ten look selections applied; PROVIA color and ACROS monochrome JPEGs saved; an ACROS XAVC S 1080p59.94 clip saved and fully decoded.
- 0.1.2: the user confirmed format/quality menus were usable. Every encoded format has not been inspected.
- 0.1.3: installation, startup and default-look application verified; the user gave general confirmation of the new controls. Every look/strength/format combination has not been tested in saved media.

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
