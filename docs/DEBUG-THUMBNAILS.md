# 缩略图不显示 / 显示异常：排查指南

面向「a5100 正常、其他机型（如 a7R II）异常」这一类现象。本页只描述本仓库代码中可验证的部分，不以未实测机型推断兼容性。

## 1. 缩略图来自哪里

| 位置 | 来源 | 是否被本项目修改 |
| --- | --- | --- |
| 相机应用列表里的应用图标 | 基础 APK 的 `AndroidManifest.xml` / `AppIconView.setIcon(...)` | 否（随基础 APK 打包） |
| 滤镜选择菜单里的缩略图 | `PictureEffectPlusOptionMenuLayout.initializeIconMap()` 写入的 `mItemIconMap`（itemId → drawable 资源 ID） | 是 |
| MENU 列表项的图标 | `assets/MenuData.xml` 中每个 `Layer2` 的 `IconRes` / `SelectedIconRes`（资源名字，不是数字 ID） | 是（新增项继承模板项） |

`mItemIconMap` 里存的是**数值资源 ID**（如 `0x7f020054`）。数值资源 ID 只在它所来自的那份 `resources.arsc` 内有效。同一个 ID 在另一份基础 APK 里可能指向别的 drawable，或者根本不存在。

## 1.5 实测主因：`long` 配置下全是 1×1 占位图（已修复）

a7R II 通过 adb 读取的配置是 `sw288dp w384dp h263dp smll **long** land`（a5100 为 `notlong`），而基础包中：

| 目录 | 内容 |
| --- | --- |
| `res/drawable-long-nodpi/` | 180 张 **1×1 全黑 PNG（67 字节）** |
| `res/drawable-notlong-nodpi/` | 180 张真实图片：70×60 菜单图标、280×480 预览图、72×96 应用图标 |

Android 只会从两者中选一个：屏幕被判为 `long` 的机身拿到占位图，于是**应用图标、滤镜缩略图、滤镜预览图全部为空**；`notlong` 的 a5100 拿到真图，一切正常。占位图来自基础 APK，与本项目补丁无关。

修复：构建时用 `drawable-notlong-nodpi` 下的同名真实图片覆盖其他目录里的 1×1 占位图（`restore_stub_drawables()`），APK 由 2.85 MB 增至 3.79 MB；`check_combined.py` 断言 `placeholder_drawables == 0`。a7R II 实测：修复前左栏是空橙框，修复后出现缩略图、顶部应用图标与右侧彩色预览图。

## 2. 0.2.x 的已知脆弱点（已修复）

1. **硬编码 `0x7f020054`**：全部预设都指向这一个写死的 ID。它取自制作 a5100 版本时所用基础包；换基础包后可能为空或指向错误资源。
2. **整表覆盖**：`initializeIconMap()` 被整段替换，基础包原有的 itemId → 图标映射被丢弃。菜单里其他键（如强度、录像项）会失去原图标。
3. **继承模板图标**：每个新菜单项都直接复制基础包 `ApplicationTop` 第一项的 `IconRes`，若该项没有该属性，新增项就没有图标名可解析。

现在的构建行为：

- 构建时**从基础 APK 自己的 `initializeIconMap()` 读出真实图标 ID**，不再写死。
- 生成的新映射 = **基础包原有条目 + 每个预设一条**，原行为保持不变。
- 每个预设按其类型取图标：彩色取 `pop-color`，ACROS 取 `richtone-mono`，理光 5 款分别对应 `pop-color` / `retro-photo` / `richtone-mono` / `rough-mono` / `watercolor`；取不到时回退到该基础包里存在的第一个来源，并打印警告。
- 读不到任何图标 ID 时**直接终止构建**，而不是静默生成坏 ID。
- `tools/check_combined.py` 增加校验：每个预设都必须有非零缩略图，菜单项必须带 `IconRes` 与 `SelectedIconRes`。

## 3. 在相机上取证

先确认两边装的是**同一个 APK**（用 `Get-FileHash -Algorithm SHA256` 对比），并记录系统版本：

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 shell getprop ro.build.version.release
adb -s CAMERA_IP:5555 shell getprop ro.build.version.sdk
adb -s CAMERA_IP:5555 shell getprop ro.product.model
```

打开应用并进入滤镜菜单，然后抓日志：

```sh
adb -s CAMERA_IP:5555 logcat -d | Select-String -Pattern "ResourceType|AssetManager|Resources|FujiHook|AppIconView"
```

关注：

- `Failure getting entry for 0x7f...` / `Resources$NotFoundException`：资源 ID 或资源表问题。
- `Failed to mmap` / `Failed opening .apk` / `Unable to open ... arsc`：资源表读取问题。
- `NoSuchMethodError` / `ClassNotFoundException`：机型（Gen1/Gen2）框架差异。
- `FujiHook` 日志正常但无图标：说明只是 UI 资源，不影响滤镜逻辑。

再确认安装包本身：

```sh
adb -s CAMERA_IP:5555 shell dumpsys package com.yuki.imaging.app.pictureeffectplus
```

## 4. 在电脑上核对资源

对**自己构建的 APK**（`output/FilmStudio-*.apk`）执行：

```sh
# 1) 反编译回来，核对图标映射与数组
java -jar inputs/apktool.jar d -r output/FilmStudio-0.2.2-alpha-movie.apk -o build-local/verify
python tools/check_combined.py --decoded build-local/verify --input-apk inputs/base.apk \
    --upstream-hook inputs/upstream/src/smali/RicohHook.smali

# 2) 该 ID 到底是什么（需要 Android build-tools 的 aapt2；仅本地检查）
aapt2 dump resources output/FilmStudio-0.2.2-alpha-movie.apk | findstr /i "drawable"
aapt2 dump resources output/FilmStudio-0.2.2-alpha-movie.apk | findstr /i "0x7f020054"

# 3) 对齐与压缩（Android 4.1 机型建议核对）
zipalign -c -v 4 output/FilmStudio-0.2.2-alpha-movie.apk
```

用 `aapt2` 找到该 ID 的**资源名与密度配置**：若只有低密度版本，较新机型上可能被拉伸成异常外观。

## 4.1 本次构建已经改掉的两处

**（1）对齐。** 基础包本身是 `resources.arsc` 未压缩 + 4 字节对齐；旧流程用普通 `zipfile` 按文件名排序重打包，把 `resources.arsc` 推到文件末尾（偏移不再被 4 整除）。现在签名器保留原条目顺序并补对齐（等价 `zipalign`），`tools/check_build.py` 会断言该偏移可被 4 整除。

**（2）缩略图映射。** 不再写死 `0x7f020054`，改为从基础包自身的图标表读出：保留原有 12 条，再补 15 条预设，共 27 条。实测映射：

| 预设 | 缩略图 ID |
| --- | --- |
| 富士彩色 8 款 | `0x7f020054`（原 pop-color） |
| 富士 ACROS | `0x7f020057`（原 richtone-mono） |
| 理光 GR 正片 / 负片 / 高反差黑白 / 森山风 / 正负逆冲 | `0x7f020054` / `0x7f020056` / `0x7f020057` / `0x7f020050` / `0x7f02005b` |

**（3）应用图标不在本项目改动范围内。** 基础包里是硬编码的 `AppIconView.setIcon(0x7f02004d, 0x7f02001d)`。若只有应用图标异常而滤镜缩略图正常，应查基础 APK 或该机型的 `AppIconView` 实现，而不是本补丁。

## 4.2 applyHook 的静默失败（已修复）

`patch_hook()` 曾把上游的优雅降级改成「直接失败」：

| 上游行为 | 旧补丁行为 |
| --- | --- |
| `ParametersModifier` / `CameraEx` / `GammaTable` 为空时，只跳过该可选步骤 | 立即 `return 0`，**整个滤镜不再写入硬件** |

调用点忽略这个返回值（`invoke-static … applyHook(…)Z` 后面紧跟 `const/4 v1, 0x1`），所以「失败」只会静默丢掉效果：在缺少 DMA gamma 通路的机型上表现为**滤镜不生效、取景器没有实时预览**；同时每次调整强度都会被判为失败并回滚。现已恢复上游的降级逻辑：矩阵照常写入，gamma 不可用则跳过。

## 4.3 设备侧诊断版（`--debug`）

```sh
python tools/build_apk.py --input inputs/base.apk --apktool inputs/apktool.jar \
  --upstream-hook inputs/upstream/src/smali/RicohHook.smali \
  --work build-local/decoded-debug --movie --debug
```

产出 `output/FilmStudio-0.2.2-alpha-movie-debug.apk`：行为与正式版完全一致，只多打日志。装到相机后打开应用、按中心键进一次滤镜菜单、逐项切换，然后：

```sh
adb -s CAMERA_IP:5555 logcat -c
# 在相机上重复上述操作
adb -s CAMERA_IP:5555 logcat -d | Select-String "FujiDiag|FujiHook"
```

| 日志 | 含义 |
| --- | --- |
| `diag icon fuji-velvia -> 2130837588 sdk=… model=…` | 缩略图 ID 已从映射取出；若随后仍画不出，说明是资源绘制而非映射问题 |
| `diag <preset-id> sdk=… model=…` | applyHook 走到成功路径 |
| `caps matrixSupported=true/false` | 硬件是否报告支持 RGB 矩阵 |
| `diag applyHook: matrix=null` | 该 ID 没取到矩阵（ID 不匹配） |
| `diag applyHook: cameraSetting=null` | 控制器没拿到 `CameraSetting` |
| `diag applyHook: params=null` | 传入的参数对为空 |
| `FujiHook … applied successfully` | 参数已提交到硬件 |

## 5. 结果判读

| 现象 | 更可能的原因 | 处理 |
| --- | --- | --- |
| 重建后图标恢复正常 | 原硬编码 ID 与基础包不匹配 | 使用本次修复后的构建流程 |
| 日志里 `Failure getting entry` / `NotFoundException` | `resources.arsc` 与代码引用的 ID 不一致 | 重新构建；核对镜像/输入哈希 |
| `res/drawable` 只有一种低密度 | 资源密度与机型屏幕不匹配 | 在 `res/` 中补充对应密度图标（需保留 `resources.arsc` 的策略另议） |
| `NoSuchMethodError` / `ClassNotFoundException` | PMCA Gen1 与 Gen2 框架差异 | 见上游的防御式反射/降级做法，不属于本项目修改范围 |
| 只有应用图标缺失、滤镜缩略图正常 | 基础 APK 的 manifest/`AppIconView` 图标 | 与本项目改动无关，需检查基础 APK |

## 6. 注意

- 本项目的机型验证范围只有 a5100；未实机验证的机型不要写成「兼容」。
- 分享日志前删除 IP、序列号、文件名等个人信息。
