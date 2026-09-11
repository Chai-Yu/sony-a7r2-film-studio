# 参考来源 / Sources / 出典

[中文](../README.md) · [English](../README.en.md) · [日本語](../README.ja.md)

查阅日期 / Reviewed / 確認日：2026-09-11

## 上游代码 / Upstream code / 上流コード

**[bonyback1/sony-pmca-ricoh-mod](https://github.com/bonyback1/sony-pmca-ricoh-mod)**

- Pinned revision: [`7c565898562c73c5073c54dfc831c8c3df9c24cf`](https://github.com/bonyback1/sony-pmca-ricoh-mod/tree/7c565898562c73c5073c54dfc831c8c3df9c24cf).
- License: [actual LICENSE at that revision](https://github.com/bonyback1/sony-pmca-ricoh-mod/blob/7c565898562c73c5073c54dfc831c8c3df9c24cf/LICENSE), Apache-2.0; copy in [LICENSES](../LICENSES/Apache-2.0.txt). No separate upstream NOTICE was found at that revision.
- `src/smali/RicohHook.smali` SHA-256: `2db88c8e42311c587ca8304c2c8ed7d70592ee988ee154327ed5503b107723ae`.

中文：参考硬件颜色矩阵、共同 Gamma 曲线与菜单挂钩方法。仓库包含经修改的 `tools/sign_apk.py`，改动为 API 10 所需的显式 SHA-1 签名和 JAR 清单折行；该文件保持 Apache-2.0。其他新增逻辑负责 LUT 拟合、录像菜单、中心键和强度。构建在本地读取上游 hook，Git 源码树不包含基础 APK；Releases 中的 APK 包含改制后的基础应用内容。

English: The reference supplies the hardware color-matrix/common-gamma approach and hook interfaces. The included signer is adapted for explicit SHA-1 and folded JAR headers and remains Apache-2.0. Additional logic covers fitting, movie menus, center-button access and strength. The build reads an independently supplied upstream hook locally; the Git source tree excludes the base APK, while the release APK contains modified base-app material.

日本語：ハードウェア色行列、共通 Gamma カーブ、メニュー連携を参考にしています。同梱の署名ツールには SHA-1 の明示と JAR ヘッダー折り返しを追加し、Apache-2.0 を維持します。近似処理、動画メニュー、中央ボタン、強度は追加処理です。上流 hook は利用者がローカルで用意し、Git のソースツリーに基礎 APK は含みませんが、公開 APK には改変した基礎アプリを含みます。

## 理光参考风格 / Ricoh-reference styles / リコー参照スタイル

From 0.2.0-alpha, [the pinned upstream hook](https://github.com/bonyback1/sony-pmca-ricoh-mod/blob/7c565898562c73c5073c54dfc831c8c3df9c24cf/src/smali/RicohHook.smali) supplies five additional presets:

| App ID | Style | Upstream array suffix |
| --- | --- | --- |
| `ricoh-positive` | GR Positive Film / GR 正片 / GR ポジフィルム | `pos` |
| `ricoh-negative` | Negative Film / 负片 / ネガフィルム | `neg` |
| `ricoh-hcbw` | High Contrast B&W / 高反差黑白 / ハイコントラスト白黒 | `hcbw` |
| `ricoh-daido` | Moriyama Daido Style / 森山风 / 森山風 | `daido` |
| `ricoh-cross` | Cross Process / 正负逆冲 / クロスプロセス | `xpro` |

中文：本地构建直接读取上游的矩阵和 1024 点 Gamma，不重新拟合、不读取上游 `.CUB` 文件。100% 保留上游参数；30%／50%／70% 向恒等变换插值，保留负片、逆冲原有的中性偏色设计。原有富士参数与四档强度保持不变。理光组是社区参考风格，并非理光官方 LUT，也未经真机色彩匹配验证。上游参数保留 Apache-2.0；新增提取逻辑的许可见文件头。

English: Local builds extract the upstream matrix and 1024-point gamma arrays without refitting or reading upstream `.CUB` files. 100% preserves the exact upstream parameters; 30/50/70% interpolate toward identity, including the original neutral tint in Negative Film and Cross Process. Existing Fujifilm parameters and all four strengths are unchanged. These are community Ricoh-reference styles, not official Ricoh LUTs or verified camera matches. Upstream parameters remain Apache-2.0; see the file header for the new extraction logic.

日本語：上流の行列と1024点 Gamma 配列を直接抽出し、再近似や `.CUB` の読み込みは行いません。100%は上流と完全に同じパラメータで、30/50/70%は恒等変換へ補間します。ネガとクロスプロセスの中性色への色付けも維持します。既存の富士参照パラメータと4段階の強度は変更しません。リコー公式 LUT や実機の色再現を検証したものではなく、コミュニティの参照スタイルです。上流パラメータは Apache-2.0 を維持し、新規抽出処理のライセンスはファイル冒頭に示します。

## 富士色彩资料 / Fujifilm color reference / 富士フイルム色彩資料

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

中文：F-Log2 输入只用于配对采样；不把 F-Log2 LUT 直接套在索尼普通画面上。WDR-709 是替代中性参考，未被证明等于索尼 STD。不分发官方原始 LUT 或独立输出 LUT；拟合参数已编入发行 APK，但不作为 Git 中的预计算表发布。版权及用途限制见 [许可范围](../LICENSING.md)和[富士条款](https://global.fujifilm.com/en/terms)。

English: F-Log2 coordinates are used to sample paired LUTs, not to apply a log transform directly to ordinary Sony images. WDR-709 is an uncalibrated proxy for Sony STD. Original official LUT files and standalone output LUTs are not distributed. Fitted parameters are compiled into the release APK, rather than published as precomputed tables in Git. See [license scope](../LICENSING.md) and [Fujifilm terms](https://global.fujifilm.com/en/terms).

日本語：F-Log2 の同一座標で2つの LUT を参照し、ソニーの通常映像へ Log 用 LUT を直接適用する方法ではありません。WDR-709 は未校正の代替基準です。公式の元 LUT と単独の出力 LUT は配布しません。近似パラメータは公開 APK に内蔵し、Git に事前計算表として掲載しません。[権利関係](../LICENSING.md)と[富士フイルムの利用条件](https://global.fujifilm.com/en/terms)も参照してください。

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
