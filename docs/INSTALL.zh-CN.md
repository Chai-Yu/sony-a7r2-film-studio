# 安装与使用：中文

[项目首页](../README.md) · [English](INSTALL.en.md) · [日本語](INSTALL.ja.md)

本指南对应 **0.2.0-alpha / 机内 0.2a**。实机环境为 a5100 固件1.10、Android 2.3.7；macOS 构建与 Wi-Fi 安装已验证。Windows/Linux 的命令说明未做相同的实机全流程验证。

**0.2.0-alpha 更名为「胶片工坊」，保留旧版包名与签名，可用 `install -r` 覆盖更新。新增理光风格使用上游原参数，100% 不重新调色；四档强度、拍照和录像菜单共用。新合并版已在 a5100 上安装、启动，并有部分滤镜参数应用成功日志；旧版记录不代表本版所有照片／录像组合已验证。**

## 0. 直接安装发行版 APK

1. 先看[机型兼容性](../README.md#compatibility)，确认你的机型和预期功能在说明范围内。
2. 在[Releases](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/tag/v0.2.0-alpha)的 Assets 中下载 **[FilmStudio-0.2.0-alpha-movie.apk](https://github.com/ukiki0718-netizen/sony-a5100-film-studio/releases/download/v0.2.0-alpha/FilmStudio-0.2.0-alpha-movie.apk)**；不要下载 Source code ZIP 当作安装包。
3. 同时下载 `SHA256SUMS.txt`，用 macOS 的 `shasum -a 256`、Linux 的 `sha256sum` 或 PowerShell 的 `Get-FileHash -Algorithm SHA256` 核对 APK。校验的是文件一致性，不是法律许可或兼容保证。
4. 电脑安装 [Android Platform-Tools / adb](https://developer.android.com/tools/releases/platform-tools)。首次连接相机时按第 4 节启用 Wi-Fi ADB，再按第 5 节安装。已能连接 ADB 的用户可直接看第 5 节。
5. **现成 APK 不需要 Python、Java、Apktool 或签名私钥。** 第 1～3 节供希望自行构建的读者使用。

假设终端当前目录就是 APK 所在的下载文件夹，安装命令是：

**IP 与隐私：** `CAMERA_IP` 只是占位符，必须替换为你自己的相机在 Tweak → Developer 中当前显示的 IP；不要原样输入，也不要照抄他人的地址。保留后面的 `:5555` 端口。公开教程使用占位符；分享截图或日志时，请遮住或删除真实 IP。

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r FilmStudio-0.2.0-alpha-movie.apk
```

将 `CAMERA_IP` 换成相机当前地址，安装完成显示 `Success`，然后在机身应用列表打开「胶片工坊」。第 5 节中的 `output/` 路径是本地构建输出目录；直接下载的用户请使用实际下载路径。

## 1. 先准备资料与设备

APK 与源码均提供，但不代表项目取得 Sony 或 FUJIFILM 的独立改编、再分发授权。各部分的权利见[许可范围](../LICENSING.md)。以下第 1～3 节是可选的本地构建步骤；自行构建前仍需确认输入材料与预定用途的相应权利。官方原始 LUT 与 Sony 未修改的基础 APK 不另行镜像。

本地构建需要：

- 支持 PlayMemories Camera Apps 的 a5100；其他机型仅供进一步研究。
- 已备份的存储卡、充足电量、可传输数据的 USB 线，以及电脑和相机都能连接的可信 Wi-Fi。
- Python 3.12、NumPy 2.3.5、Git、Java、OpenSSL、[Apktool 2.12.1](https://github.com/iBotPeaches/Apktool/releases/tag/v2.12.1)、[Android Platform-Tools / adb](https://developer.android.com/tools/releases/platform-tools)。本地验证使用 Java 18。
- 首次开启机内 ADB 所需的 [Sony-PMCA-RE / pmca-gui](https://github.com/ma1co/Sony-PMCA-RE) 与 [OpenMemories: Tweak](https://github.com/ma1co/OpenMemories-Tweak)。

从本项目页面选择 Code → Download ZIP 并解压，或使用页面给出的 Git 克隆地址。终端进入含 `tools/` 的仓库根目录。macOS/Linux：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell 可运行 `py -3.12 -m venv .venv`，之后把本文的 `python` 替换为 `.\.venv\Scripts\python.exe`，无需调整执行策略。确保 Java、OpenSSL、adb 在 PATH 中；构建命令使用单行写法，避免不同终端续行语法混淆。

## 2. 准备本地输入

将以下资料放到被 Git 忽略的 `inputs/`：

| 路径 | 内容与核对 |
| --- | --- |
| `inputs/base.apk` | 已合法取得并获准用于该用途的 Ricoh v1.1.4 基础 APK；必须匹配下方 SHA-256 |
| `inputs/apktool.jar` | Apktool 2.12.1 的 jar 文件 |
| `inputs/luts/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2/` | 经许可使用的 GFX ETERNA 55 v1.10 LUT 包解压后的目录 |
| `inputs/upstream/` | 下方固定版本的上游源码 |

基础 APK 的 SHA-256：

```text
80cb4a541f5f3dd49e8f53ffb1905048097fec17209fc9cb595a00681e65e8ea
```

这不是任意「照片效果+」APK 的通用补丁；哈希不匹配就停止。上游源码：

```sh
git clone https://github.com/bonyback1/sony-pmca-ricoh-mod.git inputs/upstream
git -C inputs/upstream checkout 7c565898562c73c5073c54dfc831c8c3df9c24cf
```

LUT 来源为[富士官方下载页](https://www.fujifilm-x.com/global/support/download/lut/)，选择 GFX ETERNA 55 v1.10。输入目录需要 `FLog2_to_WDR-709_33grid_V.1.00.cube` 和10个风格文件，不要误选 F-Log、F-Log2C 或65Grid。若官网版本或条款变化，请重新核对；不要绕过哈希检查或从不明镜像补文件。

检查工具：

```sh
python --version
java -version
openssl version
adb version
java -jar inputs/apktool.jar --version
```

## 3. 在本地生成 APK

```sh
python tools/fit_luts.py inputs/luts/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2 .
python tools/build_apk.py --input inputs/base.apk --apktool inputs/apktool.jar --upstream-hook inputs/upstream/src/smali/RicohHook.smali --work build-local/decoded-020 --movie
python tools/check_strength.py
python tools/check_build.py
```

第一步生成本地 `profiles/` 参数、`output/` 预览 LUT 和 `validation/` 拟合报告；然后构建、签名并检查 APK。结果为：

```text
output/FilmStudio-0.2.0-alpha-movie.apk
```

`build-local/decoded-020` 必须为空或不存在。重复构建请指定一个新的工作目录。`--movie` 表示启用本指南的拍照和录像功能；省略它会生成仅拍照版本。

**保管 `.private/signing.pem`。** 首次构建会自动生成签名密钥，之后更新必须保留同一密钥。不要上传密钥或把它交给其他使用者。不同人的签名不同，生成 APK 的 SHA-256 也会不同；本地报告中的哈希用于核对自己的构建；下载的发行 APK 应与 Releases 中的 SHA256SUMS.txt 核对。

## 4. 第一次让相机开启 Wi-Fi ADB

若已经可用 ADB 连接，跳到第5节。

1. 相机 USB 连接模式设为 **MTP**，用数据线连接电脑。机身显示 MTP 只表示 USB 已连接，不等于 ADB 已启用。
2. 按 [Sony-PMCA-RE 的 App Installer 说明](https://github.com/ma1co/Sony-PMCA-RE#app-installer)打开 pmca-gui。选择 **Install app** 页，在应用列表里选 **OpenMemories: Tweak**，点击 **Install selected app**。不需要使用固件更新或服务模式。
3. 安装结束后，按相机提示安全断开 USB，在应用程序列表打开 OpenMemories: Tweak。
4. 相机先配置 Wi-Fi 接入点，再在 Tweak 的 **Developer** 页启用 **Enable Wifi** 和 **Enable ADB**，记录显示的 IP。电脑与相机连接同一局域网，适当延长休眠时间。按钮说明见 [Tweak 官方用法](https://github.com/ma1co/OpenMemories-Tweak#developer)。
5. 本应用只需要 ADB。无需开启 Telnet、解除设置保护、修改地区、解除录制时限或更改固件。

macOS 发生 USB 占用时先关闭照片、图像捕捉及会访问相机的同步软件，再重新连接。具体驱动问题以 PMCA 项目的系统说明为准。

## 5. 安装到相机

把所有 `CAMERA_IP` 替换为机身此刻显示的地址，不要照抄他人的 IP。

```sh
adb connect CAMERA_IP:5555
adb devices
adb -s CAMERA_IP:5555 install -r output/FilmStudio-0.2.0-alpha-movie.apk
```

预期 `adb devices` 中目标状态为 `device`，安装末尾显示 `Success`。相机应用程序列表 → **胶片工坊**。安装名称及大部分菜单为中文。

如相机允许远程启动，也可执行：

```sh
adb -s CAMERA_IP:5555 shell am start -W -n com.yuki.imaging.app.pictureeffectplus/.PictureEffectPlus
```

原生拍摄界面可能阻止这条启动命令；这时在机身上手动打开应用即可。不要仅凭 `am start` 提示判断安装失败。

pmca-gui 的「Select an apk → Open apk... → Install selected app」可作为本地 APK 的 USB 安装尝试，但本项目更新路径以 Wi-Fi ADB 为已验证方式；无法保证每个 USB 安装器/签名组合都被接受。

## 6. 相机操作与首次自检

1. 拍照预览或录像待机按**中心键**选择风格。按 MENU 也可从首页进入「胶片风格」。列表包含「富士」与「理光」两组前缀，共 15 项。
2. MENU 首页 →「滤镜强度」选择30/50/70/100%。初始100%，正常退出后保存。人像先对比30%与50%。
3. 录像：MENU 首页 →「拍照／录像模式」→ 动态影像 P/A/S/M，然后设置「录像文件格式」及「录像帧率／画质」。拍照模式中这两项呈灰色时，先切到录像待机。按 MOVIE 开始，再按一次停止。
4. MENU 第4页 →「白平衡」。原机创意风格在应用内固定为 STD，滤镜不会锁定白平衡。
5. 对可丢弃场景试 ACROS 100% 与30%：前者应为黑白，后者应保留部分颜色。再试 PROVIA，并拍一张 JPEG、录一段数秒的视频。录像中不切换滤镜。
6. **应用内回放只显示照片。** 查看视频需退出应用，在原机回放选择对应的 XAVC S、AVCHD 或 MP4 视图；视频不出现在应用回放列表并不代表未保存。

## 7. 更新、回退与排错

| 现象 | 处理 |
| --- | --- |
| `offline`、超时、没有设备 | 确认相机未休眠、IP未变化、同一Wi-Fi且ADB已开启；执行 `adb disconnect CAMERA_IP:5555` 后重新连接。检查访客网络隔离、VPN、终端的本地网络权限 |
| MTP 正常但 adb 找不到 | MTP 与 Wi-Fi ADB 是两条不同连接，按第4节开启 ADB |
| 输入哈希不匹配 | 输入版本不对；不要删除检查，重新核对合法输入 |
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` / `INSTALL_FAILED_DEXOPT` | 检查是否按固定版本工具构建；需要 API10兼容的DEX035与v1签名，不能随意用现代签名器重新签名 |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | 签名与已装版本不同。使用原签名密钥重建；或确认已备份后，在相机应用管理中卸载同包名旧应用再安装。卸载会清除应用设置 |
| 录像设置灰色 | 进入动态影像 P/A/S/M 待机；具体档位取决于格式、当前PAL/NTSC和相机条件 |
| ACROS 不是纯黑白 | 检查强度是否100% |
| 颜色异常 | 正常退出应用并重启相机，再检查原机设置；不要靠修改固件或恢复出厂设置排查本应用 |

从本版回退到 0.1.3 前，先选择「富士 PROVIA」并正常退出，避免旧版读取不支持的理光滤镜 ID。

同一密钥构建的更新使用 `adb install -r`。回退时使用自己保存的旧 APK 与原密钥；不会自动降级或卸载。不要手动删除存储卡的数据库来找视频。

测试完执行 `adb disconnect CAMERA_IP:5555`，并在 Tweak 中关闭 ADB；不再需要时关闭其持续 Wi-Fi。连接命令只断开电脑，不能代替关闭机身守护进程。

反馈问题时说明机型、固件、应用版本、拍照/录像状态、格式、风格和强度。只提供相关日志片段，移除用户名、IP、序列号及私人媒体；不要上传 APK、LUT 或私钥。
