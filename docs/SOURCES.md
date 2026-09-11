# 参考来源 / Sources / 出典

[中文](../README.md) · [English](../README.en.md) · [日本語](../README.ja.md)

查阅日期 / Reviewed / 確認日：2026-09-11

## 上游代码 / Upstream code / 上流コード

**[bonyback1/sony-pmca-ricoh-mod](https://github.com/bonyback1/sony-pmca-ricoh-mod)**

- Pinned revision: [`7c565898562c73c5073c54dfc831c8c3df9c24cf`](https://github.com/bonyback1/sony-pmca-ricoh-mod/tree/7c565898562c73c5073c54dfc831c8c3df9c24cf).
- License: [actual LICENSE at that revision](https://github.com/bonyback1/sony-pmca-ricoh-mod/blob/7c565898562c73c5073c54dfc831c8c3df9c24cf/LICENSE), Apache-2.0; copy in [LICENSES](../LICENSES/Apache-2.0.txt). No separate upstream NOTICE was found at that revision.
- `src/smali/RicohHook.smali` SHA-256: `2db88c8e42311c587ca8304c2c8ed7d70592ee988ee154327ed5503b107723ae`.

中文：参考硬件颜色矩阵、共同 Gamma 曲线与菜单挂钩方法。仓库包含经修改的 `tools/sign_apk.py`，改动为 API 10 所需的显式 SHA-1 签名和 JAR 清单折行；该文件保持 Apache-2.0。其他新增逻辑负责 LUT 拟合、录像菜单、中心键和强度。构建在本地读取上游 hook，不随本仓库打包分发原应用。

English: The reference supplies the hardware color-matrix/common-gamma approach and hook interfaces. The included signer is adapted for explicit SHA-1 and folded JAR headers and remains Apache-2.0. Additional logic covers fitting, movie menus, center-button access and strength. The build reads an independently supplied upstream hook locally; the original camera app is not bundled.

日本語：ハードウェア色行列、共通 Gamma カーブ、メニュー連携を参考にしています。同梱の署名ツールには SHA-1 の明示と JAR ヘッダー折り返しを追加し、Apache-2.0 を維持します。近似処理、動画メニュー、中央ボタン、強度は追加処理です。上流 hook は利用者がローカルで用意し、元のカメラアプリは同梱しません。

## 色彩资料 / Color reference / 色彩資料

**[FUJIFILM LUT download](https://www.fujifilm-x.com/global/support/download/lut/)** — GFX ETERNA 55 3D LUT v1.10, `33Grid/F-Log2`.

Reference pair: `FLog2_to_WDR-709_33grid_V.1.00.cube` → corresponding film LUT, with the same F-Log2 input coordinates.

| Official filename token | Display name |
| --- | --- |
| PROVIA | PROVIA |
| Velvia | Velvia |
| ASTIA | ASTIA |
| CLASSIC-CHROME | CLASSIC CHROME |
| REALA-ACE | REALA ACE |
| PRO-Neg.Std | PRO Neg. Std |
| CLASSIC-Neg. | CLASSIC Neg. |
| ETERNA | ETERNA |
| ETERNA-BB | ETERNA BLEACH BYPASS |
| ACROS | ACROS |

中文：F-Log2 输入只用于配对采样；不把 F-Log2 LUT 直接套在索尼普通画面上。WDR-709 是替代中性参考，未被证明等于索尼 STD。官方 LUT、拟合参数和输出 LUT 均未包含在公开文件中。版权及用途限制见 [许可范围](../LICENSING.md)和[富士条款](https://global.fujifilm.com/en/terms)。

English: F-Log2 coordinates are used to sample paired LUTs, not to apply a log transform directly to ordinary Sony images. WDR-709 is an uncalibrated proxy for Sony STD. Neither official LUTs nor fitted parameters or output LUTs are included. See [license scope](../LICENSING.md) and [Fujifilm terms](https://global.fujifilm.com/en/terms).

日本語：F-Log2 の同一座標で2つの LUT を参照し、ソニーの通常映像へ Log 用 LUT を直接適用する方法ではありません。WDR-709 は未校正の代替基準です。公式 LUT、近似パラメータ、出力 LUT は公開内容に含みません。[権利関係](../LICENSING.md)と[富士フイルムの利用条件](https://global.fujifilm.com/en/terms)も参照してください。

## 安装与开发资料 / Tools and references / 導入・開発資料

These are external tools or reference documents, not bundled dependencies.

| Source | 中文 / English / 日本語 |
| --- | --- |
| [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE#app-installer) | 应用安装 / app installation / アプリ導入 |
| [OpenMemories: Tweak](https://github.com/ma1co/OpenMemories-Tweak#developer) | Wi-Fi 与 ADB / Wi-Fi and ADB / Wi-Fi・ADB |
| [OpenMemories Framework](https://github.com/ma1co/OpenMemories-Framework) | 相机 API 参考 / camera API reference / カメラ API 参照 |
| [Apktool 2.12.1](https://github.com/iBotPeaches/Apktool/releases/tag/v2.12.1) | 本地 APK 拆解与重建 / local APK decode/build / ローカル APK 展開・再構築 |
| [Android Platform-Tools](https://developer.android.com/tools/releases/platform-tools) | adb 工具 / adb tool / adb ツール |
| [Sony a5100 Help Guide](https://helpguide.sony.net/ilc/1430/v1/en/index.html) | 原机设置与媒体限制 / native settings and media limits / 標準設定・記録媒体の制限 |
| [NumPy](https://numpy.org/doc/stable/) | 数值计算 / numerical computation / 数値計算 |

第三方工具各自的许可独立适用。 / Each external tool has its own license. / 各外部ツールのライセンスはそれぞれ独立して適用されます。
