# Installation and use: English

[Project](../README.en.md) · [中文](INSTALL.zh-CN.md) · [日本語](INSTALL.ja.md)

For **0.2.2-alpha / on-camera 0.2.2**. Tested devices are an a5100 (firmware 1.10, Android 2.3.7) and an a7R II (Android 4.1.2). Building on macOS, installing over Wi-Fi ADB (Method B) and installing with pmca-gui over USB/MTP (Method A) have all been exercised on hardware. The equivalent Windows/Linux command-line builds have not had the same end-to-end hardware test.

**From 0.2.0-alpha the app is renamed to 胶片工坊 / Film Studio while retaining the package and certificate for `install -r` updates. Added Ricoh styles preserve upstream parameters at 100%; all seventeen styles share the four strengths and still/movie menus. The combined build installed and launched on the a5100 with selected parameter-application logs; saved media from this version remain unverified, and older evidence does not validate every new combination.**

## 0. Install the released APK directly

1. Read [camera compatibility](../README.en.md#compatibility) for your model and intended features.
2. Download **[FilmStudio-0.2.2-alpha-movie.apk](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/download/v0.2.2-alpha/FilmStudio-0.2.2-alpha-movie.apk)** (3,789,374 bytes) from [Releases → Assets](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/tag/v0.2.2-alpha). The Source code ZIP is not an installer. The same page carries the white-anchored companion `FilmStudio-0.2.2-alpha-movie-leica-anchor.apk`; the two differ only in the Leica tone output.
3. Check the SHA-256 with `shasum -a 256` on macOS, `sha256sum` on Linux, or `Get-FileHash -Algorithm SHA256` in PowerShell. It must be `72fa73e3a3010a59b841fde15a3f664f5272e826aedd51b1cc280fff7cd5b265`. A checksum verifies file identity, not permission or compatibility.
4. Choose an installation route: **Method A** is a graphical tool that needs no developer mode and suits people who only want to install and use the app; **Method B** is the command line and requires Wi-Fi ADB from section 4.

**Installing a released APK requires no Python, Java, Apktool or private signing key.** Sections 1–3 are for people who want to build it themselves.

### Method A: install with pmca-gui (graphical, no developer mode)

[pmca-gui](https://github.com/ma1co/Sony-PMCA-RE) is the graphical front end of Sony-PMCA-RE. It installs the APK over USB and needs **no on-camera ADB and no command line**. Set the camera's USB connection mode to **MTP** and installing is a matter of a few clicks.

1. Download a prebuilt pmca-gui from [Sony-PMCA-RE Releases](https://github.com/ma1co/Sony-PMCA-RE/releases/latest) (Windows and macOS binaries are provided; on Linux use Python 3 + libusb and run `./pmca-gui.py` from a clone).
2. Connect the camera to the computer with a USB data cable and set the camera's USB connection mode to **MTP**.
3. Open pmca-gui and switch to the **`Install app`** tab.
4. Select the **`Select an apk`** radio button (not `Select an app from the app list`), click **`Open apk...`** and choose the `FilmStudio-0.2.2-alpha-movie.apk` downloaded in step 2.
5. Click **`Install selected app`** and wait for it to finish. Then open 胶片工坊 from the camera's app list as described in section 6.

**Verification status:** with the camera's USB mode set to MTP, a local APK installs straight from the computer — **no OpenMemories: Tweak needed first, and no command line**. This project has exercised that route on hardware, and it is independent of the Wi-Fi ADB route. If you already installed Tweak through pmca-gui in section 4, the same window installs this app by the steps above.

Limits and risk:

- The camera must support **PlayMemories Camera Apps (PMCA)**. See the [device list](https://openmemories.readthedocs.io/devices.html) and this project's [camera compatibility](../README.en.md#compatibility).
- On Windows the operating system's mass storage / MTP drivers are enough. On macOS install Sony's Camera Driver and close Photos, Dropbox, Google Drive or anything else that may hold the USB drivers.
- Installing [OpenMemories: Tweak](https://github.com/ma1co/OpenMemories-Tweak) as well is recommended: it provides on-camera settings and the telnet/adb servers that Method B relies on.
- PMCA-RE is a reverse-engineering experiment whose own documentation states that it **may damage your hardware and accepts no responsibility**. Back up your card, make sure the battery is charged, and judge the risk yourself.

### Method B: Wi-Fi ADB (command line)

First enable on-camera ADB with OpenMemories: Tweak as described in section 4. If the terminal is in the folder containing the downloaded APK:

**IP address and privacy:** `CAMERA_IP` is a placeholder. Replace it with the current IP shown on your own camera in Tweak → Developer; do not type the placeholder literally or copy someone else's address. Keep the `:5555` port. Public instructions use a placeholder; hide or remove actual IP addresses before sharing screenshots or logs.

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r FilmStudio-0.2.2-alpha-movie.apk
```

Replace `CAMERA_IP` with the camera's current address. Wait for `Success`, then open「胶片工坊」from the camera's app list. The `output/` path in section 5 refers to local build output; use your actual download path when installing a release.

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
python tools/fit_luts.py inputs/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2 .
python tools/fit_leica.py "inputs/Leica SL2-S - Leica Look Up Tables (LUT)" .
python tools/build_apk.py --input inputs/base.apk --apktool inputs/apktool.jar --upstream-hook inputs/upstream/src/smali/RicohHook.smali --work build-local/decoded-021 --movie
python tools/check_strength.py
python tools/check_build.py
```

The first command generates private local `profiles/`, preview LUTs in `output/`, and fitting metrics in `validation/`. The remaining commands check strengths, build/sign the APK, and verify the result:

```text
output/FilmStudio-0.2.2-alpha-movie.apk
```

The work directory must be absent or empty. Use a new work directory for another build. `--movie` enables the still/video features covered here; omitting it produces the still-only variant.

**Keep `.private/signing.pem` private and backed up.** The first build generates a key; retain it for future updates. Do not upload or share it. Different builders have different signing keys and APK hashes. A locally generated hash identifies your own build. Verify a downloaded release APK against the SHA-256 listed in section 0.

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
adb -s CAMERA_IP:5555 install -r output/FilmStudio-0.2.2-alpha-movie.apk
```

The target should appear as `device`; installation should finish with `Success`. Open **胶片工坊** from the camera's application list. Its name and most menu labels are Chinese.

Optional remote launch:

```sh
adb -s CAMERA_IP:5555 shell am start -W -n com.yuki.imaging.app.pictureeffectplus/.PictureEffectPlus
```

The native camera screen may block this command. Open the app manually instead; an `am start` warning alone does not establish installation failure.

Updates can also go through Method A: pmca-gui's **Select an apk → Open apk... → Install selected app** is likewise hardware-verified — set the USB mode to MTP and no Wi-Fi is needed. The two routes are independent channels; either one completing is enough.

## 6. Controls and first test

1. In still preview or movie standby, press the **center button** to select a look. MENU page 1 also has the「胶片风格」entry. The seventeen choices use 富士 (Fujifilm), 理光 (Ricoh) and 徕卡 (Leica) prefixes.
2. MENU page 1 →「滤镜强度」sets 30/50/70/100%. Default 70%; a normal exit saves it. For portraits, compare 30% and 70%.
3. For video, select「拍照／录像模式」→ movie P/A/S/M, then「录像文件格式」and「录像帧率／画质」. Enter movie standby first if these are gray in still mode. MOVIE starts and stops recording.
4. White balance is「白平衡」on MENU page 4. Native Creative Style is fixed to STD in the app; white balance is not forced by the look.
5. Use a disposable test scene. Compare ACROS 100% with 30%: both are monochrome (the black-and-white looks never carry colour at any strength), 100% with more contrast and 30% flatter. Try PROVIA, save a JPEG, and record a few seconds. Do not switch looks during recording.
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
| ACROS carries colour | ACROS, High Contrast B&W and Moriyama are neutral grey at every strength; colour means the installed build is not the fixed one |
| Unexpected color | Exit normally and restart the camera, then inspect native settings; firmware modifications and factory resets are not troubleshooting steps for this app |

Before rolling back to 0.1.3, select Fujifilm PROVIA and exit normally so the old app does not encounter an unsupported Ricoh preset ID.

Update same-key builds with `adb install -r`. For rollback, keep your own earlier APK and original key; the tools do not automatically uninstall or downgrade anything. Do not delete card databases to locate movies.

After testing, run `adb disconnect CAMERA_IP:5555`, disable ADB in Tweak, and disable its persistent Wi-Fi when no longer needed. Disconnecting the computer does not stop the camera daemon.

For reports, include model, firmware, app version, still/movie state, format, look and strength. Share only relevant log excerpts; remove usernames, IPs, serials and private media. Do not attach APKs, LUTs or private keys.
