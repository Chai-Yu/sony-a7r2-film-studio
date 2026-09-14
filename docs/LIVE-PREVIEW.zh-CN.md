# 实时取景效果（a7R II 等机型）/ Live view fallback

## 问题

本项目的“硬件色”做法是向相机 ISP 写入 **3×3 RGB 矩阵 + 1024 点扩展 Gamma 表**。
有些机型（实测 Sony a7R II / `ScalarA`）对 `CameraEx$ParametersModifier` 的两个能力查询都返回 `false`：

```
caps before-sets  matrix=false gamma=false
caps before-matrix matrix=false gamma=false
```

写入本身不会报错（`write()` 返回 2048 字节、`setExtendedGammaTable()` 无异常、钩子还打印 "applied successfully"）。

**2026-09-14 订正：早前“机身静默丢弃”的判断是错的。** 那个结论只来自实时取景，没有对照过拍出来的照片。
实机对照证实：a7R II 确实**会执行** RGB 矩阵写入 —— **徕卡 自然**（矩阵 + `standard` + 无效果）
明显偏蓝绿，而**理光 GR 正片**（同一组机身风格/效果、不同的矩阵）正常；两者在机身风格这一层完全相同，
所以差异只能来自矩阵。退出应用后颜色恢复正常，也说明写入确实生效了。

根因是：**矩阵只有配上它拟合时所依据的那条曲线，才是那个 look。**模型是 `out = curve(matrix · in)`，
而这类机身对扩展 Gamma 表的查询返回 `false`，曲线会被跳过，**只剩下半个 look 的矩阵被单独应用**。
单独应用的矩阵不会渲染 look，只会让饱和色发生色相旋转（天空偏青、阳光下的暖色墙面偏绿）。
上游理光的曲线本来就接近恒等（相对恒等的 rms 只有 0.011–0.033），少掉它几乎没损失；
富士/徕卡家族的曲线偏差是它的 2–10 倍，少掉曲线就只剩失衡的矩阵。

所以现在的规则是：**矩阵与曲线要么一起写，要么都不写。**
机身报告不支持 RGB 矩阵时，只使用相机自己的 Creative Style + Picture Effect（即本页接下来的内容），
不再写入矩阵；支持矩阵的机身（如 a5100）行为完全不变。

在这类机身上，相机自己能渲染的只有两样东西：

1. **Creative Style**（`ParametersModifier.setColorMode`，如 `standard` / `vivid` / `mono`）
2. **原生 Picture Effect**（`ParametersModifier.setPictureEffect`，如 `retro-photo` / `richtone-mono`）

所以在这类机身上，用这两者做“近似实时效果”是**唯一**能进取景器的途径。

## 实现

* 构建脚本始终生成 `RicohHook.applyNative(ParametersModifier, String)`：
  按滤镜 id 查表，写入一组 `(Creative Style, Picture Effect)`。
* `applyHook` 在提交矩阵之前向机身提问：

  ```smali
  invoke-static {v2}, ...RicohHook;->needsNative(...)Z
  move-result v4
  if-eqz v4, :skip_native      # needsNative()==0：机身报告支持矩阵 → 保持硬件色
  invoke-static {v2, p2}, ...RicohHook;->applyNative(...)V
  :skip_native
  invoke-static {v2}, ...RicohHook;->needsNative(...)Z
  move-result v4
  if-eqz v4, :skip_native_matrix   # same answer: no matrix without its curve
  invoke-virtual {v2, v3}, ...ParametersModifier;->setRGBMatrix([I)V
  :skip_native_matrix
  ```

  即**默认自动降级**：支持矩阵的机身（如 a5100）行为完全不变；不支持矩阵的机身自动走原生近似。
  `needsNative()` 的返回值是「**需要原生近似**」，只在机身**报告不支持**矩阵时为真（不支持矩阵才是会静默丢弃写入的机身）。
  `needsNative()` 自身带 try/catch：能力查询抛异常时返回 false，宁可保留硬件色，也不会因为一个未知 HAL 就把画面切走。
  `--native-preview` 用于机身“报告支持但实际不显示”的情况，强制走原生近似（产物名带 `-native-forced`）。
* `applyNative()` 的名称对照表是**内联**生成的，不调用同类辅助方法：辅助调用一旦失败会被外层 catch 吞掉，取景器就会静默地什么都不变。
* `applyNative()` 的**每个**分支都会写入 Picture Effect，包含 `"off"`：只写风格的分支会把上一个滤镜的
  效果留在屏幕上，而那个效果自带的色偏会被当成新选中滤镜的颜色。
* `resetHook` 现在会额外写入 `setPictureEffect("off")`，否则退出应用后机身会保留那个原生效果。
* 映射表在 `tools/film_profiles.py:NATIVE_LOOK`，只使用**这一代机身**的取值：
  * 风格 token 取自 base APK 的 `CreativeStyleController` 常量；
  * 效果 token 取自 base APK `assets/MenuData.xml` 的 `ItemId`。

| 滤镜 | Creative Style | Picture Effect |
| --- | --- | --- |
| 富士 PROVIA 标准 / REALA ACE / 理光 GR 正片 | `standard` | – |
| 富士 Velvia 鲜艳 / 理光正负逆冲 | `vivid` | `pop-color` |
| 富士 ASTIA 柔和 / 理光负片 | `portrait` | – / `retro-photo` |
| 富士 Classic Chrome / PRO Neg Std / ETERNA | `neutral` | – |
| 富士 Classic Negative / ETERNA 漂白 | `neutral` | `retro-photo` |
| 富士 ACROS 黑白 / 理光高反差黑白 | `mono` | `richtone-mono` |
| 理光森山风 | `mono` | `rough-mono` |

## 这是近似，不是 LUT

* 原生风格/效果只有有限几档，**无法**复现富士/理光的精确曲线与矩阵；它只是让取景器**看得见**变化。
* 在不支持矩阵的机身上，它同时会进入 JPEG（因为那就是机身唯一的成像路径）。
* 支持矩阵的机身（a5100）不会走这条路径，硬件色不受影响。

## 切换界面也要实时（默认开启，已在 a7R II 上确认）

滤镜选择界面原本把预览画面遮了两层：

1. 布局根部自己画了 `@android:color/black`（Activity 主题本身是 `Theme.Transparent`，所以预览就在窗口后面）；
2. 上面再盖一张 base APK 自带的静态样张
   （`getBackgroundDrawable` → `mBackgroundImageView.setBackgroundResource`）。

两层都清掉（`patch_option_menu_live()`：`onCreateView` 里对 `mCurrentView` 调 `setBackgroundColor(0)`，
两处图片资源改成 `0`）之后，实时画面就在选择界面里直接可见，切换滤镜时立刻变化。
若要恢复原生样张，用 `--keep-sample-image` 构建。

本地断言：`check_combined.py --live-menu on` 要求反编译后的布局里两处
`getBackgroundDrawable` 的返回值都被 `const/4 v1, 0x0` 覆盖，且 `onCreateView` 里必须清掉根部背景。

## a7R II 实测记录（2026-09-13，adb）

机身 `ScalarA`，Android 4.1.2 / SDK 16，`192.168.2.22:5555`。

```
caps before-sets matrix=false gamma=false      # 两个能力查询都是 false
caps before-matrix matrix=false gamma=false
native enter=pop-color / native preset=pop-color
native style=standard   native readback=standard
native style=mono       native readback=mono     # --probe-look mono:richtone-mono
native style=vivid      native readback=vivid    # 拨到富士 Velvia
gammaWrite=2048 / gammaCommit                    # LUT 路径仍在同一原子提交里
```

结论：

* 降级闸门在这台机身上正确触发（`matrix=false` → 走原生近似）。
* `setColorMode("standard"/"mono"/"vivid")` 与 `setPictureEffect("richtone-mono"/"pop-color")` 均未抛异常
  （回读行出现在 setPictureEffect 之后，说明效果写入也没被机身拒绝）。
* 全程没有 `native error` 行。
* 修复过一个真实缺陷（2026-09-13 复审）：`needsNative()` 的返回方向写反了（它直接返回 `isRGBMatrixSupported()`），
  而调用点是 `if-eqz v4, :skip_native`；两者叠加的结果是**不支持矩阵的机身跳过降级、支持矩阵的机身反而被写入原生风格**，
  与设计完全相反。默认（auto）构建在这台 a7R II 上因此等于没有实时预览，当时只有 `--native-preview` 产物能看到效果。
  现在 `needsNative()` 只在机身**报告不支持**矩阵时返回真：默认构建即走降级，a5100 不受影响。
  该修复改变了默认构建的行为，需要重新实机确认（下表之外的验收方式不变）。

adb 无法覆盖的部分（需要人眼看相机屏幕）：

* 取景器在硬件 overlay 上合成，`screencap` 抓不到预览画面；`service call SurfaceFlinger` 需要更高权限。
* 存储卡是 FuFsys（应用私有），`adb shell` 读不到 `FilmStudioDiag.txt` 和 DCIM 里的照片。
* 相机屏幕非触摸，`input tap/keyevent` 驱动不了拨轮，应用只在“切换滤镜”时才调用钩子。
* 屏幕录制/截图看不到预览 overlay，只能看到应用自己画的内容：清除样张后该区域截图变为黑色，这正是预期。

因此“取景器是否真的变了”由下列方式确认：用拨轮切到 **富士 ACROS 黑白**（应为黑白）、
**Velvia / 正负逆冲**（应更艳）、**理光森山风**（应为高反差黑白）。

## 验证

本地（不连相机）：

```sh
python tools/build_apk.py --input inputs/base.apk --apktool inputs/apktool.jar \
    --upstream-hook inputs/upstream/src/smali/RicohHook.smali \
    --work build-local/decoded-check --movie
java -jar inputs/apktool.jar d -r output/FilmStudio-0.2.2-alpha-movie.apk -o build-local/verify-check
python tools/check_combined.py --decoded build-local/verify-check --input-apk inputs/base.apk \
    --upstream-hook inputs/upstream/src/smali/RicohHook.smali --native-fallback auto
```

`check_combined.py` 会断言：17 个滤镜在编译后的 `applyNative` 里各有风格（和效果）token、
token 必须真实存在于输入 APK、`resetHook` 会清除原生效果、自动降级必须带能力查询。

机身上（需要有人在相机前切换滤镜，相机屏幕不是触摸屏，adb 无法模拟其拨轮）：

1. 安装 `*-debug.apk`，`adb logcat -c`，进入应用，用拨轮切换滤镜。
2. `adb logcat -d | grep FujiDiag` 关注：

   ```
   native enter=<滤镜>
   native style=<风格>          # 我们写入的风格
   native readback=<风格>       # 机身回读；与写入不一致说明该 token 被拒绝
   native error=...             # 写入抛异常时的真实原因
   ```

3. 同屏观察取景器：切换“富士 ACROS 黑白”应立刻变黑白，“Velvia/正负逆冲”应明显更艳，
   “森山风”应变成高反差黑白。
4. 退出应用后取景器应恢复普通成像（`resetHook`）。
