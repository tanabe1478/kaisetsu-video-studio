# Kaisetsu Video Studio

ChatGPTと一緒に使う、台本JSONからMP4を作るローカルツールです。
このPCでは必要なPythonライブラリを導入済みです。

制作工程・設計判断・今後の候補は [開発ノート](docs/DEVELOPMENT.md)、変更点は [更新履歴](CHANGELOG.md) に記録します。
このリポジトリには立ち絵や生成動画は含みません。別環境では下記配布先から無印2.3を取得し、PSDと同梱readmeを `assets/original` 以下へ配置してください。

## 使い方

台本を画面で直すには `./start-editor.ps1` を実行し、`http://127.0.0.1:8765/` を開きます。
章・場面・セリフの編集と並べ替え、AIへのメモ、自動保存に対応しています。詳しくは [台本ノートの使い方](editor/README.md)。

ChatGPTに「demo.jsonの台本を○○の説明に変えて、動画を再生成して」と依頼してください。
自分で実行する場合は、このフォルダーでPowerShellから `./render.ps1` を実行します。
VOICEVOXが起動していなければ、既存のインストールからエンジンをバックグラウンド起動します。
別の台本は `./render.ps1 my-script.json`。通常のVOICEVOXアプリを開く場合、先にこのツールが起動したエンジンを終了するか、アプリの起動を先に行ってください。

出力: `output/demo.mp4`（1280×720、24fps、H.264/AAC）、`narration.wav`、`subtitles.srt`、`timeline.json`、各場面のPNG。
同じ出力先への再実行は前回の動画を上書きします。残したい場合は `python studio.py demo.json --output output/take2`。

## 台本の項目

- title: 全体のタイトル
- speaker / style: VOICEVOXの話者名とスタイル名
- speed: 話速（0.5〜2）
- scenes: 場面の配列
- 各場面の text: 読み上げるセリフ。heading: 見出し。points: 短い箇条書き3点以内。
- expression: normal / happy / surprised / thinking
- pose: normal / wave / point / think
- code: 等幅フォントで表示するコード（最大10行）。pointsの代わりに表示。
- chapter: 章名。章一覧の出力に使用。
- narration: `{ "text": "表示字幕", "speech": "読み上げ用表記" }` の配列。speechは省略可。指定するとtextより優先。
- pause: 場面末尾の無音時間（秒、既定0.6）。
- bgm: ローカル音源のpath、title、creator、sourceとbelow_voice_db（既定22）。相対パスはリポジトリのルート基準。

表情・腕・口・目は、実際のPSDレイヤーを切り替えて作成しています。
音量で発話を検出して口を開閉し、定期的にまばたきします。
立ち絵の位置は固定です。上下に揺らす常時アニメーションはありません。
字幕ごとに音声を合成し、各WAVの実長に字幕の表示時刻を合わせます。narration未指定時はtextから短い区間を自動分割します。
長い字幕は2行の長さと句読点を考慮して改行します。音声の各音素へ字幕を逐語同期する方式ではありません。
口パクは開閉の2段階で、母音別の口形・厳密な音素同期は未実装です。
BGMはローカルに用意した音源を繰り返し、発話区間の音量を基準に控えめに混ぜます。冒頭2秒・末尾4秒でフェードします。
below_voice_dbが大きいほどBGMが小さくなります。数値は発話区間と原曲のRMSを比較した目安で、聴感上の音量を保証する値ではありません。
背景画像の挿入、複数人の掛け合い、タイムラインGUIも今後の拡張対象です。
音声キャッシュにより変更のないセリフは再合成しません。
立ち絵PSDや表情マッピングを変更した場合は `assets/sprites` の生成PNGを削除して再生成してください。

## 素材とクレジット

- 立ち絵: 坂本アヒル「ずんだもん立ち絵素材2.3」（無印）。V3.2ではありません。
- 作者掲載ページ: https://seiga.nicovideo.jp/seiga/im10788496
- 作者配布先: https://ux.getuploader.com/s_ahiru/download/37
- 取得日: 2026-09-06。ZIPのMD5: `8d4f880afa74d26e5576259c8f7a51a6`（配布ページの値と一致）。
- 同梱readmeは `assets/original` 内に保持。動画・加工利用可、公式ガイドライン準拠。
- キャラクター利用ガイドライン: https://zunko.jp/guideline.html
- 音声: VOICEVOX:ずんだもん（エンジン0.25.1）
- VOICEVOX規約: https://voicevox.hiroshiba.jp/term/
- 音源利用規約: https://zunko.jp/con_ongen_kiyaku.html

動画内にも音声と立ち絵のクレジットを表示します。素材はローカル利用用です。
素材や音源そのものの再配布を目的としたパッケージではありません。

## 依存関係

Python 3.13、Pillow、psd-tools、NumPy、requests、imageio-ffmpeg。
新しい環境では `python -m pip install -r requirements.txt`。
FFmpegはimageio-ffmpegに同梱された実行ファイルを使用します。
日本語フォントはWindowsのメイリオを使用します。
コード用フォントはWindowsのConsolasです。

## 教材サンプル

[MoonBit言語仕様入門](lessons/moonbit/README.md)：32場面・9章。台本、出典、実行できるコード例、検証手順を収録しています。
