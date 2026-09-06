# Kaisetsu Video Studio

ChatGPTと一緒に使う、台本JSONからMP4を作るローカルツールです。
このPCでは必要なPythonライブラリを導入済みです。

制作工程・設計判断・今後の候補は [開発ノート](docs/DEVELOPMENT.md)、変更点は [更新履歴](CHANGELOG.md) に記録します。
このリポジトリには立ち絵や生成動画は含みません。別環境では下記配布先から無印2.3を取得し、PSDと同梱readmeを `assets/original` 以下へ配置してください。

## 使い方

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

表情・腕・口・目は、実際のPSDレイヤーを切り替えて作成しています。
音量で発話を検出して口を開閉し、定期的にまばたきします。
字幕の場面境界は音声と同期していますが、場面内の字幕分割は文字数による概算です。
口パクは開閉の2段階で、母音別の口形・厳密な音素同期は未実装です。
背景画像の挿入、BGM、複数人の掛け合い、タイムラインGUIも今後の拡張対象です。
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
