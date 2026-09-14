# インストールと使い方：日本語

[プロジェクト](../README.ja.md) · [中文](INSTALL.zh-CN.md) · [English](INSTALL.en.md)

対象は **0.2.2-alpha／カメラ内表示0.2.2**。実機は a5100（ファームウェア1.10、Android 2.3.7）と a7R II（Android 4.1.2）です。macOS でのビルド、Wi-Fi ADB での導入（方法 B）、pmca-gui による USB／MTP 導入（方法 A）はいずれも実機で確認しました。Windows/Linux のコマンドラインによるビルドは、同じ実機で全工程を検証していません。

**0.2.0-alpha では「胶片工坊 / Film Studio」に改名し、同じパッケージと署名で `install -r` 更新ができます。追加したリコー風は100%で上流の値を維持し、17種類すべてが4段階の強度と写真／動画メニューを共有します。統合版は a5100 で導入・起動と一部の適用ログを確認しました。本版の保存ファイルは未検証で、旧版の記録は新しい全組み合わせの検証を意味しません。**

## 0. 公開 APK をそのまま導入する

1. [対応機種](../README.ja.md#compatibility)で機種と利用予定の機能を確認します。
2. [Releases の Assets](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/tag/v0.2.2-alpha)から **[FilmStudio-0.2.2-alpha-movie.apk](https://github.com/Chai-Yu/sony-a7r2-film-studio/releases/download/v0.2.2-alpha/FilmStudio-0.2.2-alpha-movie.apk)**（3,789,785 バイト）をダウンロードします。Source code ZIP はインストーラーではありません。
3. APK の SHA-256 を確認します（macOS は `shasum -a 256`、Linux は `sha256sum`、PowerShell は `Get-FileHash -Algorithm SHA256`）。値は `c4df639f1f7250d302aac3f4ad617b61c484bc579da61422acde5585a7a57d94` です。確認できるのはファイルの一致で、許諾や互換性ではありません。
4. 導入方法を選びます：**方法 A** は GUI で開発者モード不要、入れて使うだけの人向けです。**方法 B** はコマンドラインで、第4節の Wi-Fi ADB が必要です。

**公開 APK の導入だけなら Python、Java、Apktool、署名秘密鍵は不要です。** 第1～3節は自分でビルドしたい人向けです。

### 方法 A：pmca-gui で導入する（GUI・開発者モード不要）

[pmca-gui](https://github.com/ma1co/Sony-PMCA-RE) は Sony-PMCA-RE の GUI です。USB 経由で APK を導入でき、**機内 ADB もコマンド操作も不要**です。カメラの USB 接続モードを **MTP** にすれば、導入は数回のクリックで済みます。

1. [Sony-PMCA-RE Releases](https://github.com/ma1co/Sony-PMCA-RE/releases/latest) から pmca-gui のビルド済み版を入手します（Windows／macOS はバイナリあり。Linux は Python 3 + libusb で、クローン後に `./pmca-gui.py` を実行）。
2. USB ケーブルでカメラと PC を接続し、カメラの USB 接続モードを **MTP** にします。
3. pmca-gui を起動し、**`Install app`** タブに切り替えます。
4. **`Select an apk`** のラジオボタンを選び（`Select an app from the app list` ではありません）、**`Open apk...`** を押して手順 2 でダウンロードした `FilmStudio-0.2.2-alpha-movie.apk` を選びます。
5. **`Install selected app`** を押して完了を待ちます。その後、第6節のとおりカメラのアプリ一覧から「胶片工坊」を開きます。

**検証状況：** カメラの USB モードを MTP にして PC とつなげば、ローカル APK をそのまま導入できます。**OpenMemories: Tweak を先に入れる必要も、コマンド操作も不要**です。本プロジェクトは実機でこの経路を確認しており、Wi-Fi ADB の経路とは独立しています。第4節で pmca-gui から Tweak を入れた場合も、同じ画面で上記の手順により本アプリを導入できます。

制限とリスク：

- カメラが **PlayMemories Camera Apps（PMCA）** に対応している必要があります。対応機種は[デバイス一覧](https://openmemories.readthedocs.io/devices.html)と本プロジェクトの[対応機種](../README.ja.md#compatibility)を参照してください。
- Windows は OS 標準の大容量ストレージ／MTP ドライバーで動作します。macOS は Sony の Camera Driver が必要で、写真アプリ、Dropbox、Google Drive など USB ドライバーを掴むアプリを終了しておきます。
- [OpenMemories: Tweak](https://github.com/ma1co/OpenMemories-Tweak) も導入することを推奨します。機内設定の調整と、方法 B が使う telnet／adb サーバーを提供します。
- PMCA-RE はリバースエンジニアリングの実験的なツールで、公式説明に**ハードウェアを破損する可能性があり責任を負わない**と明記されています。カードをバックアップし、電池を十分にして、リスクは自己判断でお願いします。

### 方法 B：Wi-Fi ADB（コマンドライン）

第4節のとおり OpenMemories: Tweak で機内 ADB を有効にします。ダウンロードした APK のフォルダーでターミナルを開いた場合：

**IP アドレスとプライバシー：** `CAMERA_IP` は仮の表記です。Tweak → Developer で自分のカメラに現在表示されている IP アドレスに置き換えてください。仮の表記をそのまま入力したり、他人のアドレスをコピーしたりしないでください。末尾のポート `:5555` はそのままにします。公開手順には仮の表記を使い、スクリーンショットやログを共有する際は実際の IP アドレスを隠すか削除してください。

```sh
adb connect CAMERA_IP:5555
adb -s CAMERA_IP:5555 install -r FilmStudio-0.2.2-alpha-movie.apk
```

`CAMERA_IP` をカメラの現在のアドレスに置き換えます。`Success` を確認し、カメラのアプリ一覧から「胶片工坊」を開きます。第5節の `output/` はローカルビルドの出力先なので、直接ダウンロードした場合は実際の保存先を指定してください。

## 1. 事前準備と権利の確認

APK とソースを提供しますが、Sony または FUJIFILM から改変・再配布の個別許諾を得たことを示すものではありません。[権利関係](../LICENSING.md)を参照してください。以下の第1～3節は任意のローカルビルド手順です。入力資料と予定用途の権利は別途確認してください。公式の元 LUT と Sony の未改変の基礎 APK は別途ミラー配布しません。

ローカルビルドに必要なもの：

- PlayMemories Camera Apps 対応の a5100。他機種は未検証です。
- バックアップ済みカード、十分な電池残量、データ通信対応 USB ケーブル、カメラとPCが接続できる信頼できる Wi-Fi。
- Python3.12、NumPy2.3.5、Git、Java、OpenSSL、[Apktool2.12.1](https://github.com/iBotPeaches/Apktool/releases/tag/v2.12.1)、[Android Platform-Tools / adb](https://developer.android.com/tools/releases/platform-tools)。ローカル確認では Java18 を使用しました。
- 初回の ADB 設定に [Sony-PMCA-RE / pmca-gui](https://github.com/ma1co/Sony-PMCA-RE) と [OpenMemories: Tweak](https://github.com/ma1co/OpenMemories-Tweak)。

プロジェクトページで Code → Download ZIP を選んで展開するか、表示された Git URL をクローンします。`tools/` があるルートディレクトリでターミナルを開きます。macOS/Linux：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell では `py -3.12 -m venv .venv` を実行し、以降の `python` を `.\.venv\Scripts\python.exe` に置き換えます。実行ポリシーの変更は不要です。Java、OpenSSL、adb を PATH に登録します。ビルドコマンドはシェルごとの継続行の違いを避けるため1行で記載しています。

## 2. ローカル入力を用意

Git 管理対象外の `inputs/` に配置します。

| パス | 内容 |
| --- | --- |
| `inputs/base.apk` | 適法に入手し、本用途に必要な権利を確認した Ricoh v1.1.4 APK。下記 SHA-256 と完全一致するもの |
| `inputs/apktool.jar` | Apktool2.12.1 の jar |
| `inputs/luts/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2/` | 本用途の許諾を確認した GFX ETERNA55 v1.10 LUT の展開先 |
| `inputs/upstream/` | 下記リビジョンの上流ソース |

基礎 APK の SHA-256：

```text
80cb4a541f5f3dd49e8f53ffb1905048097fec17209fc9cb595a00681e65e8ea
```

任意の「ピクチャーエフェクト+」APK に使える汎用パッチではありません。不一致なら中止します。上流ソースを固定します。

```sh
git clone https://github.com/bonyback1/sony-pmca-ricoh-mod.git inputs/upstream
git -C inputs/upstream checkout 7c565898562c73c5073c54dfc831c8c3df9c24cf
```

参照パッケージは[富士フイルムの公式ページ](https://www.fujifilm-x.com/global/support/download/lut/)の GFX ETERNA55 v1.10 です。`FLog2_to_WDR-709_33grid_V.1.00.cube` と10種類のファイルが必要です。F-Log、F-Log2C、65Grid と取り違えないでください。配布元の版や条件が変更された場合は再確認し、ハッシュ確認を外したり不明なミラーを使用したりしないでください。

ツールを確認します。

```sh
python --version
java -version
openssl version
adb version
java -jar inputs/apktool.jar --version
```

## 3. ローカルビルド

```sh
python tools/fit_luts.py inputs/gfx-eterna-55-3d-lut-v110/33Grid/F-Log2 .
python tools/fit_leica.py "inputs/Leica SL2-S - Leica Look Up Tables (LUT)" .
python tools/build_apk.py --input inputs/base.apk --apktool inputs/apktool.jar --upstream-hook inputs/upstream/src/smali/RicohHook.smali --work build-local/decoded-021 --movie
python tools/check_strength.py
python tools/check_build.py
```

最初のコマンドで `profiles/`、`output/` のプレビュー LUT、`validation/` の数値評価を生成します。続いて強度の検査、APK のビルド・署名・検証を実行します。生成先：

```text
output/FilmStudio-0.2.2-alpha-movie.apk
```

作業ディレクトリは未作成か空である必要があります。再ビルドでは新しい作業先を指定します。`--movie` は本書の写真・動画機能を有効にします。省略すると写真用の版になります。

**`.private/signing.pem` を非公開のまま保管・バックアップしてください。** 初回に生成され、更新時も同じ鍵が必要です。共有やアップロードはしないでください。ビルドする人ごとに鍵と APK のハッシュが異なります。ローカルの検証レポートは自分のビルドの照合用です。ダウンロードした公開 APK は、第0節に記載した SHA-256 と照合してください。

## 4. 初回の Wi-Fi ADB 設定

すでに ADB 接続できる場合は第5節へ進みます。

1. カメラの USB 接続を **MTP** に設定してPCへつなぎます。MTP 表示だけでは ADB は有効になりません。
2. [PMCA の App Installer 手順](https://github.com/ma1co/Sony-PMCA-RE#app-installer)に従います。pmca-gui の **Install app** で **OpenMemories: Tweak** を選択し、**Install selected app** を押します。この手順にファームウェア更新モードやサービスモードは不要です。
3. 完了後、指示に従って USB を外し、カメラのアプリ一覧から Tweak を起動します。
4. Wi-Fi 接続先を設定し、Tweak の **Developer** ページで **Enable Wifi** と **Enable ADB** を有効にして IP を控えます。PC も同一 LAN に接続し、カメラの省電力移行までの時間を十分に確保します。[Tweak の説明](https://github.com/ma1co/OpenMemories-Tweak#developer)も参照してください。
5. 必要なのは ADB のみです。Telnet、保護解除、地域変更、録画制限解除、ファームウェア変更は本アプリの導入に不要です。

macOS で USB が使用中になる場合は、写真、イメージキャプチャ、カメラにアクセスする同期ソフトを閉じて再接続します。ドライバーの詳細は PMCA の各OS向け説明に従います。

## 5. カメラにインストール

`CAMERA_IP` は現在カメラに表示されるアドレスにすべて置き換えます。

```sh
adb connect CAMERA_IP:5555
adb devices
adb -s CAMERA_IP:5555 install -r output/FilmStudio-0.2.2-alpha-movie.apk
```

対象が `device` と表示され、最後に `Success` が出ればインストール完了です。カメラのアプリ一覧から **胶片工坊** を起動します。名称と大部分のメニューは中国語です。

任意でリモート起動もできます。

```sh
adb -s CAMERA_IP:5555 shell am start -W -n com.yuki.imaging.app.pictureeffectplus/.PictureEffectPlus
```

標準の撮影画面が起動要求を拒否する場合は、カメラで手動起動してください。この警告だけでインストール失敗とは判断できません。

更新は方法 A でも行えます。pmca-gui の **Select an apk → Open apk... → Install selected app** も実機で確認済みで、USB モードを MTP にすれば Wi-Fi は不要です。2 つは独立した経路で、どちらか一方が完了すれば成功です。

## 6. 操作と最初の確認

1. 写真プレビュー／動画待機中に**中央ボタン**でフィルターを選びます。MENU 1ページ目の「胶片风格」からも開けます。「富士」「理光」「ライカ」の接頭辞が付いた17項目を選べます。
2. 「滤镜强度」で30/50/70/100%を選択。初期値70%、通常終了時に保存します。人物では30%と70%を比較してください。
3. 動画は「拍照／录像模式」→ 動画 P/A/S/M を選んでから「录像文件格式」と「录像帧率／画质」を設定します。写真モードでグレーの場合は先に動画待機へ切り替えます。MOVIE で開始／停止します。
4. ホワイトバランスは MENU 4ページ目の「白平衡」。アプリ内のクリエイティブスタイルは STD 固定ですが、ホワイトバランスは固定しません。
5. 失っても困らない被写体で ACROS100% と30%を比較します。どちらも白黒です（白黒系フィルターはどの強度でも色を持ちません）。100%はコントラストが高く、30%は平坦になります。PROVIA でも JPEG1枚と数秒の動画を保存します。録画中にフィルターは変更しません。
6. **アプリ内再生は写真のみです。** 動画はアプリを終了し、標準再生で XAVC S / AVCHD / MP4 の対応する表示モードを選びます。アプリ一覧に動画が出なくても未保存とは限りません。

## 7. 更新・戻し方・トラブル対応

| 症状 | 対応 |
| --- | --- |
| offline／タイムアウト／機器なし | スリープ、IP、同一LAN、ADBを確認。`adb disconnect CAMERA_IP:5555` の後に再接続。ゲストネットワーク分離、VPN、PCのローカルネットワーク権限も確認 |
| MTP では認識するが adb で見えない | 別の接続方式です。第4節で Wi-Fi ADB を設定 |
| 入力ハッシュ不一致 | 入力版が異なります。確認処理を削除しないでください |
| 署名解析／DEXOPT エラー | 指定ツールを使用。API10互換DEX035とv1署名が必要です。現代的な署名ツールの既定値で再署名しないでください |
| INSTALL_FAILED_UPDATE_INCOMPATIBLE | 鍵が異なります。元の鍵で再ビルドするか、バックアップ後にカメラのアプリ管理で旧版を削除してから導入します。削除するとアプリ設定は失われます |
| 動画設定がグレー | 動画 P/A/S/M の待機へ。形式、PAL/NTSC、機種条件により選択肢は異なります |
| ACROS に色が残る | ACROS・ハイコントラスト白黒・森山風はどの強度でも中立グレーです。色が出る場合は修正済みでないビルドです |
| 色がおかしい | 通常終了してカメラを再起動し、標準設定を確認。本アプリの排障にファームウェア変更や初期化は行いません |

0.1.3へ戻す前に「富士 PROVIA」を選び、通常終了してください。旧版が未対応のリコー ID を読み込むことを防ぎます。

同じ鍵の更新は `adb install -r` を使用します。戻す場合は自分で保存した旧 APK と元の鍵を使います。自動削除や自動ダウングレードはしません。動画を探すためにカードのデータベースを削除しないでください。

終了後は `adb disconnect CAMERA_IP:5555` を実行し、Tweak で ADB を無効にします。不要なら継続 Wi-Fi も解除します。PC の切断だけではカメラ側の ADB は停止しません。

不具合報告には機種、ファームウェア、アプリ版、写真／動画状態、形式、フィルター、強度を添えます。ログは該当部分だけとし、ユーザー名、IP、シリアル番号、私的画像を除いてください。APK、LUT、秘密鍵は添付しないでください。
