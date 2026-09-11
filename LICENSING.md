# 许可范围 / License scope / ライセンスの適用範囲

[中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

## 中文

本仓库的默认许可为未经改写的 **[PolyForm Noncommercial 1.0.0](LICENSE)**，适用于贡献者有权许可的原创新增代码与文档。版权由各贡献者就其各自享有著作权的内容持有；“A5100 Film Studio contributors”是署名集合，不表示成立了公司或独立法人。

本许可不授予商业用途；个人爱好、研究和部分机构用途的准确许可范围，以许可证原文为准，包括其明确列出的机构例外及法定权利。分发适用内容时应保留许可及 [NOTICE](NOTICE) 的必要通知。它属于非商用源码公开许可，不符合 [OSI 开源定义](https://opensource.org/osd) 中不得限制商业领域的要求。

| 内容 | 权利与许可 |
| --- | --- |
| 本项目原创工具、补丁生成逻辑、测试和文档 | PolyForm Noncommercial 1.0.0，限贡献者有权授予的部分 |
| `tools/sign_apk.py`，含本项目对它的修改 | 来源于 bonyback1 的项目，整个文件保留 [Apache-2.0](LICENSES/Apache-2.0.txt)；修改说明见文件开头及 NOTICE |
| 其他可能包含的上游表达 | 上游权利和 Apache-2.0 条件继续有效；本仓库不能撤销既有许可 |
| 富士官方 LUT、相关说明及其权利 | 归 FUJIFILM 及相应权利人所有；不分发官方原始 LUT 文件；APK 内嵌拟合参数。本项目不授予这些第三方材料的使用、改编或再分发许可 |
| Sony 基础应用、库、固件和商标 | 归各自权利人所有；发行 APK 包含改制后的 Sony 基础应用内容；不提供固件，不因打包、参考 API 或结构而取得其权利 |

**Releases 中的 APK 是混合来源的二进制文件，不能将整个 APK 的第三方内容一并视为本项目原创或全部适用 PolyForm。** 包内 `assets/legal/` 保留许可和来源通知。第三方改编、再分发授权未获独立确认，发布不是授权证明。

上游 Apache 许可不能被本项目的“非商用”要求覆盖。因此，本项目不能禁止第三方依据 Apache 许可独立使用上游代码。许可证文件本身保留其原有地位，也不被重新许可。

本工具参考富士公开的 GFX ETERNA 55 LUT；**公开下载不等于公开授权改编或再分发**。[富士网站条款](https://global.fujifilm.com/en/terms)有下载用途和改动限制，当前未确认针对本工具用途的独立授权。这是核对许可的起点，不是对具体地区法律适用的最终结论。自行构建前，也须确认基础 APK 和 LUT 的相应用途获准。

项目名称和风格名称仅用于识别参考来源及兼容性。Sony、FUJIFILM、Ricoh 及产品名称的商标权属于各自权利人。本项目未经这些公司认证、赞助或背书。

软件按现状提供；在法律允许的范围内，不保证兼容性、色彩准确性、适销性、特定用途适用性或不侵权。非商用、署名、免责声明以及在 GitHub 发布，均不构成第三方授权或保证免责；依法不可排除的责任不因此被排除。英文许可证是许可条款原文，本页是范围说明，不是法律意见。

## English

The default license is the unmodified **[PolyForm Noncommercial 1.0.0](LICENSE)**, covering original additions that contributors have the right to license. Each contributor retains any copyright in their own contributions. “A5100 Film Studio contributors” is a collective attribution, not a claim that a company or separate legal entity exists.

Commercial use is not granted by that license. Its text controls the permitted purposes, including its listed organizational exceptions and statutory rights. Keep the license and required [NOTICE](NOTICE) lines when distributing covered content. This is noncommercial source-available software, not [OSI-defined open source](https://opensource.org/osd).

| Material | Scope |
| --- | --- |
| Original tools, patch-generation logic, tests and documentation | PolyForm Noncommercial 1.0.0, only to the extent contributors can grant rights |
| `tools/sign_apk.py`, including our modifications | Adapted from bonyback1's project; the whole file remains [Apache-2.0](LICENSES/Apache-2.0.txt), with modification notices |
| Any other underlying upstream expression | Its existing rights and Apache-2.0 conditions remain applicable |
| Official Fujifilm LUTs and associated material | Owned by FUJIFILM and respective rights holders. Original LUT files are not distributed; fitted parameters are embedded in the APK. No third-party rights are granted here |
| Sony base app, libraries, firmware and trademarks | Respective third-party rights. The release APK contains modified Sony base-app material, not firmware. Packaging does not grant ownership or additional rights |

**The release APK combines material from multiple sources; its third-party contents are not all original project work or automatically covered by PolyForm.** Licenses and attribution are included under `assets/legal/`. Third-party adaptation/redistribution permission has not been independently established; publication is not proof of permission.

Our noncommercial terms cannot revoke the permissions already granted for upstream Apache-licensed material. The license texts themselves retain their existing status.

The color reference is Fujifilm's publicly downloadable GFX ETERNA 55 package. Public access is not a grant to adapt or redistribute it. [Fujifilm's website terms](https://global.fujifilm.com/en/terms) include restrictions on downloads and alterations; a separate grant for this project's use has not been established. Check the applicable rights for both the base APK and LUTs before building. This is not a jurisdiction-specific legal conclusion.

Brand and film names identify compatibility and references. All trademarks remain with their owners. Sony, FUJIFILM and Ricoh have not certified, sponsored or endorsed this project.

As far as applicable law permits, the software is provided as is without warranties of compatibility, color accuracy, merchantability, fitness or non-infringement. Noncommercial terms, attribution, disclaimers and publication on GitHub do not confer third-party permission or guarantee immunity. Liability that cannot legally be excluded is not excluded. The English license texts control; this page explains scope and is not legal advice.

## 日本語

本プロジェクト独自の追加部分には、変更していない **[PolyForm Noncommercial 1.0.0](LICENSE)** を適用します。適用は、各貢献者が許諾できる権利の範囲に限ります。各自の著作権は各貢献者に帰属します。「A5100 Film Studio contributors」は共同の帰属表記であり、会社や独立した法人の存在を意味しません。

このライセンスは商用利用を許諾しません。明示された組織利用の例外や法定の権利を含め、正確な範囲は原文に従います。対象物を配布する場合はライセンスと [NOTICE](NOTICE) の必要な通知を保持してください。非商用のソース公開であり、[OSI の定義](https://opensource.org/osd)によるオープンソースではありません。

| 対象 | 権利と適用範囲 |
| --- | --- |
| 独自のツール、パッチ生成処理、テスト、説明書 | 貢献者が許諾できる範囲で PolyForm Noncommercial 1.0.0 |
| `tools/sign_apk.py` と本プロジェクトによる同ファイルの変更 | bonyback1 のプロジェクトに由来し、ファイル全体を [Apache-2.0](LICENSES/Apache-2.0.txt) として維持。変更点を明記 |
| その他の上流由来の表現 | 元の権利と Apache-2.0 の条件を維持 |
| 富士フイルム公式 LUT と関連資料 | FUJIFILM および各権利者に帰属。公式の元 LUT は配布せず、近似パラメータは APK に内蔵します。第三者の権利は許諾しません |
| Sony の基礎アプリ、ライブラリ、ファームウェア、商標 | 各権利者に帰属。公開 APK には改変した Sony 基礎アプリを含みますが、ファームウェアは配布しません。パッケージ化によって権利を取得するものではありません |

**公開 APK は複数の出典を持つバイナリです。第三者の内容をすべて本プロジェクト独自の著作物、または PolyForm の対象とみなすことはできません。** `assets/legal/` にライセンスと出典通知を収録します。第三者資料の改変・再配布許諾は個別に確認できておらず、公開は許諾の証明ではありません。

本プロジェクトの非商用条件によって、上流の Apache ライセンスで既に認められた権利を取り消すことはできません。ライセンス原文自体の権利関係も変更しません。

色彩の参照元は公開ダウンロード可能な GFX ETERNA 55 LUT です。ただし、公開されていることと改変・再配布の許諾は別です。[富士フイルムのサイト利用条件](https://global.fujifilm.com/en/terms)にはダウンロード用途や改変の制限があり、本ツールの用途に対する個別の許諾は未確認です。ビルド前に、基礎 APK と LUT の利用に必要な権利を確認してください。特定地域の法律について最終判断を示すものではありません。

企業名・製品名・フィルム名は互換性と参照元の説明に使用します。商標は各権利者に帰属し、本プロジェクトは Sony、FUJIFILM、Ricoh の認証・支援・推奨を受けていません。

適用法が認める範囲で現状有姿で提供し、互換性、色の正確性、商品性、特定目的への適合性、非侵害を保証しません。非商用条件、帰属表示、免責文、GitHub での公開によって第三者の許諾が得られたり、責任を完全に免れたりすることはありません。法令上除外できない責任は排除しません。ライセンスの英語原文が基準です。本ページは適用範囲の説明であり、法律上の助言ではありません。
