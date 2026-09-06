# MoonBit 言語仕様入門

ずんだもんによる32場面・9章の教材です。変数と関数を少し知っている人を想定しています。
公式ドキュメントを根拠に、25個の短いコード例と小問で解説します。

- [台本](TRANSCRIPT.md)
- [出典と検証環境](SOURCES.md)
- [実行検証記録](VALIDATION.json)
- [BGM・配置調整と音源の準備](BGM.md)
- `lesson.json`: 動画生成の入力
- `build_lesson.py`: 台本・読み上げ表記・コード例の編集元
- `examples/*.mbtx`: 場面番号に対応する独立実行用コード
- `checks`: 意味と期待値を検証するテストパッケージ

例題の表示部分が定義の一部だけの場合、`.mbtx`には必要な型定義と入口を補っています。
場面28のtestブロックは`checks`にも収録して`moon test`で実行します。`moon run`だけではtestの成功を主張しません。

## 再生成

リポジトリのルートで以下を実行します。動画生成にはVOICEVOXと立ち絵が必要です。
BGM「ほんわかぷっぷー」も配布元から手動で取得し、`assets/bgm/honwaka-puppu.mp3` に配置してください。

```powershell
python lessons/moonbit/build_lesson.py
python studio.py lessons/moonbit/lesson.json --output output/moonbit
python lessons/moonbit/finalize_video.py
```

最終動画は `output/moonbit/moonbit-language-introduction.mp4`。
章のメタデータを埋め込みます。対応プレーヤーでは章を選んで移動できます。
`output/moonbit/chapters.txt` と `subtitles.srt` も利用できます。
動画・立ち絵・合成音声・ツールチェーンはGit管理外です。

## コードの検証

MoonBitツールチェーンの`moon`をPATHから使える状態にして実行します。

```powershell
python lessons/moonbit/verify_examples.py
```

このPCでは検証用ツールチェーンを `cache/moon-toolchain` に配置しています。
ユーザー共通のPATHを変更していないため、利用するシェル内で設定します。

```powershell
$env:MOON_HOME = (Resolve-Path cache/moon-toolchain).Path
$env:PATH = "$env:MOON_HOME\bin;$env:PATH"
python lessons/moonbit/verify_examples.py
```

## 制作上の改善

- コード用の等幅フォントと最大10行の表示枠。
- 1文ごとに音声を合成し、字幕の表示区間をそのWAVの実長に同期。
- 表示する英語表記と、音声用のカタカナ表記を分離。
- 小問のあとに考える間を挿入。
- 章一覧とMP4章メタデータを出力。
- 立ち絵を固定位置に配置。BGMを小音量で追加。

口パクは音量ベースの2段階です。音素別の口形には未対応です。
