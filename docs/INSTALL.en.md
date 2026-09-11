# Installation and use: English

[Project](../README.en.md) · [中文](INSTALL.zh-CN.md) · [日本語](INSTALL.ja.md)

For **0.1.3-alpha / on-camera 0.1d**. The tested device is an a5100 with firmware 1.10 and Android 2.3.7. Building on macOS and installing over Wi-Fi were exercised; equivalent Windows/Linux instructions have not had the same end-to-end hardware test.

## 0. Install the released APK directly

1. Read [camera compatibility](../README.en.md#compatibility) for your model and intended features.
2. Download **[FujiStyle-0.1.3-alpha-movie.apk](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/download/v0.1.3-alpha/FujiStyle-0.1.3-alpha-movie.apk)** from [Releases → Assets](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/tag/v0.1.3-alpha). The Source code ZIP is not an installer.
3. Download `SHA256SUMS.txt` too. Check the APK with `shasum -a 256` on macOS, `sha256sum` on Linux, or `Get-FileHash -Algorithm SHA256` in PowerShell. A checksum verifies file identity, not permission or compatibility.
4. Install [Android Platform-Tools / adb](https://developer.android.com/tools/releases/platform-tools) on the computer. First-time users follow section 4 to enable Wi-Fi ADB and section 5 to install; if ADB already works, go to section 5.
5. **Installing a released APK requires no Python, Java, Apktool or private signing key.** Sections 1–3 are for people who want to build it themselves.

If the terminal is in the folder containing the downloaded APK:

**IP address and privacy:** `CAMERA_IP` is a placeholder. Replace it with the current IP shown on your own camera in Tweak → Developer; do not type the placeholder literally or copy someone else's address. Keep the `:5555` port. Public instructions use a placeholder; hide or remove actual IP addresses before sharing screenshots or logs.

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r FujiStyle-0.1.3-alpha-movie.apk
```

Replace `CAMERA_IP` with the camera's current address. Wait for `Success`, then open「富士风格」from the camera's app list. The `output/` path in section 5 refers to local build output; use your actual download path when installing a release.

## 1. Prerequisites and rights

An APK and source are provided, without representing a separate Sony or FUJIFILM grant to adapt or redistribute their material. See [license scope](../LICENSING.md). Sections 1–3 below are optional local build instructions; check the rights for your inputs and intended use before building. Original official LUT files and Sony's unmodified base APK are not separately mirrored.

For a local build, prepare:

- An a5100 supporting PlayMemories Camera Apps; other models are unverified.
- A backed-up memory card, adequate battery charge, a USB data cable, and a trusted Wi-Fi network accessible to the camera and computer.
- Python 3.12, NumPy 2.3.5, Git, Java, OpenSSL, [Apktool 2.12.1](https://github.com/iBotPeaches/Apktool/releases/tag/v2.12.1), and [Android Platform-Tools/adb](https://developer.android.com/tools/releases/platform-tools). Java 18 was used locally.
- [Sony-PMCA-RE/pmca-gui](https://github.com/ma1co/Sony-PMCA-RE) and [OpenMemories: Tweak](https://github.com/ma1co/OpenMemories-Tweak) if the camera does not already expose ADB.

Download this repository using Code → Download ZIP, or clone the URL displayed on its project page. Open a terminal in the repository root containing `tools/`. On macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, run `py -3.12 -m venv .venv`, then replace `python` below with `.\.venv\Scripts\python.exe`. This avoids changing execution policies. Java, OpenSSL and adb must be on PATH. Build commands are written on one line for shell portability.

## 2. Local inputs

Store inputs under the Git-ignored `inputs/` directory:

| Path | Required content |
| --- | --- |
| `inputs/base.apk` | A lawfully obtained Ricoh v1.1.4 base APK with the necessary rights for this use; exact SHA-256 below |
| `inputs/apktool.jar` | Apktool 2.12.1 jar |
| `inputs/luts/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2/` | Extracted GFX ETERNA 55 v1.10 LUT package you have permission to use for this purpose |
| `inputs/upstream/` | Pinned upstream source below |

Required base APK SHA-256:

```text
80cb4a541f5f3dd49e8f53ffb1905048097fec17209fc9cb595a00681e65e8ea
```

This is not a universal patch for arbitrary Picture Effect+ APKs. Stop on a hash mismatch. Pin the hook source:

```sh
git clone https://github.com/bonyback1/sony-pmca-ricoh-mod.git inputs/upstream
git -C inputs/upstream checkout 7c565898562c73c5073c54dfc831c8c3df9c24cf
```

The reference package is GFX ETERNA 55 v1.10 from [Fujifilm's download page](https://www.fujifilm-x.com/global/support/download/lut/). The directory must contain `FLog2_to_WDR-709_33grid_V.1.00.cube` and ten film files. Do not substitute F-Log, F-Log2C or 65Grid. Recheck rights and compatibility if the supplier changes the package or terms; do not bypass hashes or use an untrusted mirror.

Check your tools:

```sh
python --version
java -version
openssl version
adb version
java -jar inputs/apktool.jar --version
```

## 3. Build locally

```sh
python tools/fit_luts.py inputs/luts/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2 .
python tools/check_strength.py
python tools/build_apk.py --input inputs/base.apk --apktool inputs/apktool.jar --upstream-hook inputs/upstream/src/smali/RicohHook.smali --work build-local/decoded-013 --movie
python tools/check_build.py
```

The first command generates private local `profiles/`, preview LUTs in `output/`, and fitting metrics in `validation/`. The remaining commands check strengths, build/sign the APK, and verify the result:

```text
output/FujiStyle-0.1.3-alpha-movie.apk
```

The work directory must be absent or empty. Use a new work directory for another build. `--movie` enables the still/video features covered here; omitting it produces the still-only variant.

**Keep `.private/signing.pem` private and backed up.** The first build generates a key; retain it for future updates. Do not upload or share it. Different builders have different signing keys and APK hashes. A locally generated hash identifies your own build. Verify a downloaded release APK against the SHA256SUMS.txt published with that release.

## 4. First-time Wi-Fi ADB setup

Skip this section if ADB already works.

1. Set the camera's USB connection to **MTP** and connect a data cable. An MTP indication does not mean ADB is enabled.
2. Follow the [PMCA App Installer instructions](https://github.com/ma1co/Sony-PMCA-RE#app-installer). In pmca-gui, use **Install app**, select **OpenMemories: Tweak** from the app list, and click **Install selected app**. Firmware-update and service modes are not required for this path.
3. When installation finishes, disconnect USB as directed and open Tweak from the camera's application list.
4. Configure the camera's Wi-Fi access point. In Tweak's **Developer** tab enable **Enable Wifi** and **Enable ADB**; note the IP. Use the same LAN on the computer and allow enough time before camera sleep. See [Tweak's instructions](https://github.com/ma1co/OpenMemories-Tweak#developer).
5. Only ADB is needed here. Do not enable Telnet, disable protection, change region, remove recording limits or modify firmware for this app.

If macOS reports USB contention, close Photos, Image Capture and other software accessing the camera, then reconnect. Refer to PMCA's platform documentation for driver issues.

## 5. Install the APK

Replace every `CAMERA_IP` with the address currently shown by your camera.

```sh
adb connect CAMERA_IP:5555
adb devices
adb -s CAMERA_IP:5555 install -r output/FujiStyle-0.1.3-alpha-movie.apk
```

The target should appear as `device`; installation should finish with `Success`. Open **富士风格** from the camera's application list. Its name and most menu labels are Chinese.

Optional remote launch:

```sh
adb -s CAMERA_IP:5555 shell am start -W -n com.yuki.imaging.app.pictureeffectplus/.PictureEffectPlus
```

The native camera screen may block this command. Open the app manually instead; an `am start` warning alone does not establish installation failure.

pmca-gui also offers **Select an apk → Open apk... → Install selected app** for a local APK. You may try that USB route, but Wi-Fi ADB is the update method verified for this project. Acceptance of every USB installer/signature combination is not guaranteed.

## 6. Controls and first test

1. In still preview or movie standby, press the **center button** to select a look. MENU page 1 also has the「富士风格」entry.
2. MENU page 1 →「滤镜强度」sets 30/50/70/100%. Default 100%; a normal exit saves it. For portraits, compare 30% and 50%.
3. For video, select「拍照／录像模式」→ movie P/A/S/M, then「录像文件格式」and「录像帧率／画质」. Enter movie standby first if these are gray in still mode. MOVIE starts and stops recording.
4. White balance is「白平衡」on MENU page 4. Native Creative Style is fixed to STD in the app; white balance is not forced by the look.
5. Use a disposable test scene. Compare ACROS 100% with 30%: monochrome versus partially retained color. Try PROVIA, save a JPEG, and record a few seconds. Do not switch looks during recording.
6. **In-app playback lists only photographs.** Exit the app and use native playback with the matching XAVC S, AVCHD or MP4 view. Absence from in-app playback does not mean a movie was lost.

## 7. Updates, rollback and troubleshooting

| Symptom | Response |
| --- | --- |
| `offline`, timeout or no device | Check sleep, current IP, same LAN and ADB. Disconnect with `adb disconnect CAMERA_IP:5555`, then reconnect. Check guest-network isolation, VPN and terminal local-network permission |
| MTP works but adb does not | MTP and Wi-Fi ADB are separate; complete section 4 |
| Input hash mismatch | Wrong input revision; do not remove the check |
| Certificate parse / DEXOPT failure | Use the documented build tools. API 10 needs compatible DEX 035 and v1 signing; do not casually re-sign with a modern default signer |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Signing key differs. Rebuild with the original key, or back up and uninstall the old same-package app using camera app management before installing. Uninstalling clears app settings |
| Gray video settings | Select movie P/A/S/M standby; available profiles still depend on format, PAL/NTSC and camera conditions |
| ACROS retains color | Set strength to 100% |
| Unexpected color | Exit normally and restart the camera, then inspect native settings; firmware modifications and factory resets are not troubleshooting steps for this app |

Update same-key builds with `adb install -r`. For rollback, keep your own earlier APK and original key; the tools do not automatically uninstall or downgrade anything. Do not delete card databases to locate movies.

After testing, run `adb disconnect CAMERA_IP:5555`, disable ADB in Tweak, and disable its persistent Wi-Fi when no longer needed. Disconnecting the computer does not stop the camera daemon.

For reports, include model, firmware, app version, still/movie state, format, look and strength. Share only relevant log excerpts; remove usernames, IPs, serials and private media. Do not attach APKs, LUTs or private keys.
