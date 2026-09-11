# 验证范围 / Validation / 検証範囲

[中文](../README.md) · [English](../README.en.md) · [日本語](../README.ja.md)

## 实机记录 / Device evidence / 実機記録

Device: one Sony a5100 / ILCE-5100, firmware 1.10, Android 2.3.7 / API 10. These observations do not establish compatibility with other bodies or firmware.

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

## 发布 APK / Released APK / 公開 APK

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

After completing the rights and input steps in the [installation guide](INSTALL.en.md):

```sh
python tools/check_strength.py
python tools/check_build.py
```

These checks require locally fitted profiles; the APK check also requires a local build. They do not connect to the camera. They verify:

- Ten profiles, four supported strengths, 3×3 dimensions, neutral-preserving row sums, 1024-point monotonic curves and 10-bit bounds.
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
