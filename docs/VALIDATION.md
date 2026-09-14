# 验证范围 / Validation / 検証範囲

[中文](../README.md) · [English](../README.en.md) · [日本語](../README.ja.md)

## 实机记录 / Device evidence / 実機記録

Devices: one Sony a5100 / ILCE-5100 (firmware 1.10, Android 2.3.7 / API 10) and one Sony a7R II / ILCE-7RM2 (Android 4.1.2 / API 16). The a7R II reports no support for the RGB matrix or the extended gamma table, so its imaging runs on the Creative Style + native Picture Effect fallback instead of the fitted parameters. These observations do not establish compatibility with other bodies or firmware.

| Version | 中文 | English | 日本語 |
| --- | --- | --- | --- |
| 0.1.1 / 0.1b | 10 个滤镜切换，照片与一段黑白视频保存验证 | Ten selections applied; JPEGs and one monochrome clip inspected | 10種類の切り替え、JPEG と白黒動画1本を確認 |
| 0.1.2 / 0.1c | 录像格式／画质菜单获用户确认 | User confirmed movie format/quality controls | 動画形式・画質メニューの操作を利用者が確認 |
| 0.1.3 / 0.1d | 安装、启动、默认风格成功；新操作获用户总体确认 | Install, startup and default look verified; general user confirmation of new controls | 導入・起動・初期フィルターを確認。新操作について利用者の総合的確認あり |

**0.1b saved-output measurements / 已保存文件检查 / 保存ファイルの確認：**

- PROVIA JPEG: 6000 × 4000, color present.
- ACROS JPEG: 6000 × 4000, decoded R = G = B at every pixel.
- ACROS movie: XAVC S, H.264, 1920 × 1080, 60000/1001 fps (~59.94), duration 8.5085 s; stereo PCM at 48 kHz.
- Full audio/video decode passed. Nine 1 fps samples, resized to 320 × 180 and decoded as RGB24, were achromatic at every sampled pixel. This does not test every full-resolution frame for neutrality or assess audio quality by listening.

中文：上述视频证明黑白处理进入了保存的视频；不证明色彩精确匹配富士 ACROS。0.1b 的素材结果不能当作 0.1d 所有滤镜、强度、格式组合的逐项验证。应用内回放只列出照片，视频须在原机对应格式的回放模式查看。未公开原始素材、设备日志或私人拍摄信息。

English: The clip demonstrates that monochrome processing reached saved video, not that it matches Fujifilm ACROS accurately. The 0.1b evidence is not an exhaustive 0.1d look/strength/format test. In-app playback lists stills; use the corresponding native movie view for video. Private captures, device logs and personal recording metadata are not published.

日本語：この動画は白黒処理が保存映像に反映された証拠であり、富士フイルム ACROS との正確な一致を示すものではありません。0.1b の結果は、0.1d の全組み合わせを確認したことにはなりません。アプリ内再生は写真のみで、動画は標準の対応形式の再生画面で確認します。個人の素材、機器ログ、撮影情報は公開しません。

## 0.2.0-alpha / 胶片工坊 / Film Studio

`FilmStudio-0.2.0-alpha-movie.apk` — SHA-256:

```text
964b9b4d7038d0f28353b6784be7b27880d2e647c350e81ab17614510722eaa5
```

审查修订 / Review revision（2026-09-13，未实机验证 / not hardware-verified）：上一版实机测试的产物是
`88632d187f75c6560c2b67b64d9de9774226d8a78fd7ba3330270493e8b0ad2a`（已保留在 `build-local/prev-review-apks/`）。
本次修订修了三个缺陷：实时取景降级闸门方向写反（默认构建在报告不支持矩阵的机身上跳过了降级）、
滤镜强度白名单漏掉 100%（选 100% 会被当成 50%）、`resetHook` 把 `setColorMode` 的 `"standard"` 覆盖成 `"off"`；
默认强度为 70%；黑白构在四档强度下均保持中性灰（只变对比度）；滤镜选择界面加了一层深色罩（alpha 0xB0）保证白字可读，实时预览仍可见。上述结论来自静态检查，仍需实机重测。

## 2026-09-14 修订 / 2026-09-14 revision / 2026-09-14 改訂

`FilmStudio-0.2.0-alpha-movie.apk` (release tag `v0.2.1-alpha`) — SHA-256:

```text
2b42cf90b4a5cba1458b1e8865d88c509779a46bb1d4a876c66ab41e049fb120
```

中文：**本条含实机验证记录（a7R II / ILCE-7RM2，Android 4.1.2 / API 16）。** 修了一个外表像整机死机、
只能关机的缺陷：`PictureEffectPlusOptionMenuLayout.pushedMenuKey()` 在**没有菜单历史**时（用相机确认键从拍摄界面
直接调出滤镜选择菜单；`getLastStoredValues()` 因 bundle 无菜单数据而提前返回，`mLastItemId` 保持 null）
直接调 `closeLayout()` 销毁界面，却绕过了 `BaseMenuLayout.closeMenuLayout()` 里的 `mListener.onClosed()`，
于是菜单状态永远留在状态栈上、界面却已消失：相机随后对任何按键都不再响应，而系统本身（adb、日志、
输入分发队列、应用线程）完全正常。修复把该分支的 `closeLayout()` 换成 `openPreviousMenu()`：
`closeLayout()` 仍只执行一次（效果提交行为不变），但补上了缺失的 `onClosed()`。
另把滤镜选择界面的背景改回**完全透明**（`--menu-scrim` 默认 `0x00`），实时预览不再被罩层染色；上一版 0xB0 深色罩的说法作废。
实机复测：原复现路径（确认键开菜单 → 按 MENU）连续往返数十次均正常退回拍摄界面，不再复现；
从 MENU 进入的路径同样正常。机上安装文件的 sha256 与本地产物逐字节一致。静态检查（685 条项、菜单与查表映射、强度端点）仍由 `check_strength.py` / `check_build.py` / `check_combined.py` 复查通过。

English: **This entry includes hardware verification (a7R II / ILCE-7RM2, Android 4.1.2 / API 16).** It fixes a
defect that looked like a whole-camera hang and forced a power cycle: with no menu history — the chooser opened by
the camera's center key from the shooting screen, where `getLastStoredValues()` returns early because the bundle
carries no menu data and `mLastItemId` stays null — `PictureEffectPlusOptionMenuLayout.pushedMenuKey()` called
`closeLayout()` directly and bypassed the `mListener.onClosed()` notification inside
`BaseMenuLayout.closeMenuLayout()`. The menu state stayed on the stack with no layout behind it, after which the
camera answered no key at all while the system itself (adb, logs, input dispatcher queues, app threads) remained
healthy. The fix reaches the same teardown through `openPreviousMenu()`, so `closeLayout()` still runs exactly once
(effect commit unchanged) and the missing `onClosed()` is delivered. The chooser background is transparent again
(`--menu-scrim` defaults to `0x00`), so the live preview is no longer tinted; the earlier 0xB0 scrim no longer applies.
On the camera the original repro (center key opens the chooser, then MENU) returned to the shooting screen every time
across dozens of round trips, and the MENU-entry path still works. The installed file is byte-identical to the local
artifact by sha256. Static checks (684 signed entries, menu and lookup maps, strength endpoints) still pass under
`check_strength.py` / `check_build.py` / `check_combined.py`.

日本語：**本項は実機検証（a7R II / ILCE-7RM2、Android 4.1.2 / API 16）を含みます。** 全体がハングしたように見え、
電源再投入が必要だった不具合を修正しました。メニュー履歴がない場合（撮影画面でカメラの確定キーから
フィルター選択メニューを開いた場合、bundle にメニューデータが無いため `getLastStoredValues()` が早期に戻り、
`mLastItemId` が null のまま）に `PictureEffectPlusOptionMenuLayout.pushedMenuKey()` が `closeLayout()` を直接
呼び、`BaseMenuLayout.closeMenuLayout()` 内の `mListener.onClosed()` を迂回していました。その結果メニュー状態が
スタックに残ったまま画面だけが消え、以降カメラはどのキーにも反応しませんでした（システム自体、adb、ログ、
入力ディスパッチャ、アプリのスレッドはすべて正常）。修正は同じ後処理を `openPreviousMenu()` 経由で行うため、
`closeLayout()` は従来どおり一度だけ実行され（効果の確定は不変）、欠けていた `onClosed()` が通知されます。
フィルター選択画面の背景は再び**完全透明**（`--menu-scrim` 既定 `0x00`）となり、ライブプレビューは色を
被りません。実機では元の再現手順（確定キーでメニューを開き MENU を押す）を数十回往復しても撮影画面に
戻り、MENU からの経路も正常です。インストール済みファイルの sha256 はローカル成果物と一致します。
静的検証（684 署名エントリ、メニューと参照マップ、強度端点）は `check_strength.py` / `check_build.py` /
`check_combined.py` で引き続き合格しています。

中文：本版把应用名改为「胶片工坊」，合并 10 个富士参考风格与 5 个上游理光／街头风格。对最终签名 APK 重新反编译后，核对了全部 120 组数组（15 风格 × 4 强度 × 矩阵／Gamma）、菜单与查询映射。与 0.1.3 比较，原有 80 组富士数组逐项一致；新增理光 100% 参数与固定版本上游一致。曲线边界、强度端点、684 个签名条目、同一签名证书及包内许可检查通过。相机内版本名为 `0.2a`，包名不变。**实机覆盖安装显示 Success，启动成功，已安装版本读回为 0.2a。运行日志观察到原有富士风格及理光正片、负片、高反差黑白、森山风的参数应用成功；正负逆冲仅有静态检查。尚未验证本版照片／录像保存、全部强度或录像待机下的全部切换，也未做新色彩校准。**

English: The app is renamed 胶片工坊 / Film Studio and combines ten Fujifilm-reference with five upstream Ricoh/street presets. Round-trip decompilation of the final signed APK verified all 120 arrays (15 looks × 4 strengths × matrix/gamma), menu IDs and lookups. All 80 existing Fujifilm arrays match 0.1.3 exactly; Ricoh at 100% matches the pinned upstream. Curve bounds, strength endpoints, 684 signed entries, the retained certificate and bundled legal files passed. The on-camera version is `0.2a`; the package is unchanged. **The in-place camera update returned Success, the app launched, and the installed version read back as 0.2a. Runtime logs showed successful application of existing Fujifilm profiles and Ricoh Positive, Negative, High Contrast B&W and Moriyama; Cross Process has only static checks. Saved photographs/video, all strengths and all movie-standby transitions remain unverified for this version. No new color calibration was performed.**

日本語：アプリ名を「胶片工坊 / Film Studio」に変更し、富士参照10種と上流リコー／ストリート風5種を統合。最終署名 APK を再展開し、120配列（15種類 × 4強度 × 行列／Gamma）、メニューと参照処理を確認しました。既存の富士80配列は0.1.3と完全一致し、リコー100%も指定版の上流と一致します。カーブ範囲、強度端点、684署名項目、継続する署名証明書、同梱ライセンスを確認。カメラ内表示は `0.2a`、パッケージ名は維持しています。**実機の上書き更新は Success、起動成功、インストール済み版は0.2aと確認しました。既存の富士参照と、リコーのポジ・ネガ・高反差白黒・森山風で適用成功ログを確認。クロスプロセスは静的検証のみです。本版の写真／動画保存、全強度、動画待機中の全切り替えは未検証で、新たな色彩校正も行っていません。**

## 0.1.3-alpha 发布 APK / Previous release / 旧公開 APK

`FujiStyle-0.1.3-alpha-movie.apk` — SHA-256:

```text
5757a59a5ce9983a2294a18bf120235c43a490a1eda1b1345d112a3369b1a1ef
```

中文：发行打包只新增 `assets/legal/` 下的4份许可／来源文件。与原先实机验证的 APK 比较，全部原有代码、资源与其他非签名条目字节一致，签名证书相同；684个条目的完整性、清单摘要及 APK 签名验证通过。此补充许可证后的文件没有再次安装到相机，因此不把它描述为新的全流程实机验证。Releases 附有 `RELEASE-VERIFICATION.json` 和 `SHA256SUMS.txt`。

English: Release packaging adds four license/attribution files under `assets/legal/`. All original code, resources and other non-signature entries are byte-identical to the previously camera-tested APK, and the signing certificate is unchanged. Integrity, manifest digests and signature checks passed for 684 entries. This repacked file was not reinstalled on the camera, so it is not a new end-to-end hardware test. Releases include `RELEASE-VERIFICATION.json` and `SHA256SUMS.txt`.

日本語：公開用のパッケージには `assets/legal/` のライセンス・出典4ファイルだけを追加しています。実機確認済み APK の既存コード、リソース、その他の非署名エントリーはすべてバイト単位で一致し、署名証明書も同じです。684エントリーの整合性、マニフェストのダイジェスト、署名を検証しました。この再梱包ファイルは実機へ再インストールしていないため、新たな実機全工程検証とは扱いません。Releases に `RELEASE-VERIFICATION.json` と `SHA256SUMS.txt` を添付します。

## 数值近似 / Numerical approximation / 数値的な近似

The fit uses paired official LUT samples with an uncalibrated WDR-709 neutral proxy. Fixed random seed: 5100. Training points after clipping exclusions: 75,866; independent validation points: 22,760. Errors below are pooled absolute RGB-channel errors on a normalized 0–1 output scale, **not ΔE, a percentage match, or measured a5100 color accuracy**.

| Look | Mean absolute error | 95th percentile absolute error |
| --- | ---: | ---: |
| PROVIA | 0.0650 | 0.2278 |
| Velvia | 0.0629 | 0.2373 |
| ASTIA | 0.0663 | 0.2333 |
| CLASSIC CHROME | 0.0811 | 0.2287 |
| REALA ACE | 0.1254 | 0.3185 |
| PRO Neg. Std | 0.0726 | 0.2223 |
| CLASSIC Neg. | 0.0802 | 0.2514 |
| ETERNA | 0.0784 | 0.2074 |
| ETERNA BLEACH BYPASS | 0.0808 | 0.2068 |
| ACROS | 0.1037 | 0.2548 |

中文：训练和验证样本相互独立，均取自官方中性 LUT 的未剪裁区间。误差是在 0–1 的 RGB 数值上计算的绝对误差，不是“相似度百分比”或实拍 ΔE。部分颜色误差明显，REALA ACE 的平均误差尤其较大。3×3 行列与共同明暗曲线无法完整表达复杂 LUT；索尼处理顺序和传递函数也未做实测标定。

English: Independent training and validation use the unclipped region of the neutral LUT. Some colors have substantial errors, particularly the mean error for REALA ACE. A 3×3 matrix and one common tone curve cannot reproduce the complete nonlinear LUT. Sony's processing order and transfer functions have not been measured and calibrated.

日本語：学習と検証には独立した標本を用い、中性 LUT のクリップされていない領域を評価しています。表は 0–1 の RGB 絶対誤差であり、一致率や実写の ΔE ではありません。特に REALA ACE の平均誤差など、無視できない差があります。3×3 行列と共通カーブでは複雑な LUT を完全には表現できず、ソニー側の処理順序や伝達特性も未校正です。

## 本地检查 / Local checks / ローカル検査

Optional compiled-payload regression check after decompiling the signed APK:

```sh
java -jar inputs/apktool.jar d -r output/FilmStudio-0.2.0-alpha-movie.apk -o build-local/verify-020
python tools/check_combined.py --decoded build-local/verify-020 --input-apk inputs/base.apk \
    --upstream-hook inputs/upstream/src/smali/RicohHook.smali
```

The `--input-apk` file is the unmodified base APK. The patch rewrites the picture effect list in `assets/MenuData.xml`, so the live-view fallback's effect IDs can only be checked against the input, not against the built APK.

Use a fresh verification directory. To compare all forty previous Fujifilm look/strength combinations, add `--previous-decoded PATH_TO_DECODED_013`. This option reads the previous build; it does not connect to the camera.


After completing the rights and input steps in the [installation guide](INSTALL.en.md):

```sh
python tools/check_strength.py
python tools/check_build.py
```

Run these after a local build, which creates `profiles/film_studio.json` from the existing fitted profiles and pinned upstream hook. They do not connect to the camera. They verify:

- Fifteen profiles, four strengths, 3×3 dimensions, 1024-point monotonic curves and 10-bit bounds. Neutral rows remain neutral; intentional Ricoh tints retain their original row sums at 100%.
- A bit-identical 100% endpoint and mathematical 0% identity endpoint; 0% is not an app menu choice.
- `.cube` red/green/blue ordering and exported-grid round trips.
- APK archive integrity, file and manifest digests, and the detached signature against the embedded certificate. This is integrity checking, not trust in the signer or proof of device compatibility.

中文：参数强度检查保证 100% 保持原值、数学上的 0% 为恒等变换、曲线单调且不超界。APK 校验检查归档与签名完整性，不证明签名者可信、应用安全或能在其他相机运行。

日本語：強度検査では100%の一致、数学上の0%の恒等変換、カーブの単調性と範囲を確認します。APK 検査はアーカイブ・署名の整合性を調べるもので、署名者の信頼性、安全性、他機種での動作を保証しません。

For optional inspection of your own selected captures, install `requirements-media.txt` and separately install FFmpeg/ffprobe. The capture checker reads only the files you specify:

```sh
python -m pip install -r requirements-media.txt
python tools/verify_capture.py --provia YOUR_PROVIA.JPG --acros YOUR_ACROS.JPG --movie YOUR_ACROS.MP4 --output validation/my-capture-check.json
```

中文：将示例文件名替换为自己选定的测试素材。生成的报告可能含文件名和 EXIF 时间；仅供本地检查，公开前须去除私人信息。需要 Pillow、FFmpeg 和 ffprobe，这些不是构建 APK 的必需工具。

日本語：ファイル名を自分で選んだテスト素材に置き換えてください。レポートにはファイル名や EXIF 時刻が含まれるため、公開前に個人情報を削除します。Pillow、FFmpeg、ffprobe は素材検査用で、APK のビルドには不要です。

Still unverified / 尚未验证 / 未検証：all encoded format × look × strength combinations; other camera models; long recording reliability; RAW image-data changes; colorimetric matching; thermal and battery behavior under extended use. Re-test your intended settings before important shooting.
