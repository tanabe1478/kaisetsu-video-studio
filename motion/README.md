# Remotionによる先頭一致の音声付き試作

Remotion 4.0.522 / React 19.1.1 / SVG。既存の場面8（39.75秒、6セリフ）の文言・読み・音声・間を保持し、黒板を再設計した。20分版全体の改訂や台本ノートの描画エンジン置換はまだ行っていない。

## 再生成

リポジトリのルートで以下を実行する。`prepare.py`はこの教材の保存済み台本・既存音声専用。入力の文言が変わった場合は停止する。新しい出力先を指定し、既存成果物を保持する。

```sh
npm --prefix motion ci
.venv/bin/python motion/prepare.py output/prefix-new
node motion/render.mjs output/prefix-new
npm --prefix motion test
```

`render.mjs`は指定フレームのPNG、Remotionによる映像、既存音声を結合した`demo.mp4`、検証済みの`delivery.json`、時刻ボタン付きの確認ページ`index.html`まで生成する。FFmpegはPython環境のimageio-ffmpegを使う。音声なしの中間ファイルを完成成果物として渡さない。

確認ページは `.venv/bin/python -m http.server 8766 --bind 127.0.0.1 --directory output/prefix-new` で開ける。

`npm --prefix motion run studio`は図のライブプレビュー。既定の6セリフを表示するが、音声は本編への結合時に付く。音声と合わせた確認には完成MP4を使う。Windows/macOSのフォント差は未検証。今回の確認環境はMacのHiragino Sans。

## 意図と確認

| 瞬間 | 期待する状態 |
|---|---|
| 2.4秒 | 上下ともA/B/C。同じ列の入力が対応する |
| 2.8〜4秒 | 下段のBだけが同じ位置でXに変化。AとCは移動しない |
| 8〜12秒 | A/BとA/Xの文脈を括弧で比較。Cの文字の一致だけでは再利用できない理由を示す |
| 18.5〜22秒 | Aを再利用候補として緑、XとCを再処理として橙。色だけでなくラベルと境界線を付ける |
| 28.7〜30秒 | 日付を入れる空間を先頭に開けてから日付を表示。要素が交差しない |
| 32.5〜37秒 | 固定の説明・会話の履歴・今回の情報を順に並べる |

初回ではBからXへの変更が即時だったため、同じ位置での0.5秒の文字切替を追加。日付挿入では移動中に箱が重なる設計を修正し、空間が開いてから日付を表示するようにした。v1/v2はローカルで保持。

最終出力：`output/prompt-caching-remotion-20260908-v3/demo.mp4`。39.75秒、1280×720、24fps。映像・音声の全編デコード、954フレーム、6字幕、1章の時刻を検証した。意味上の状態と時刻に関する2件のテストも成功。

AI自身が描画画像に加え、完成MP4から抽出した14時点の画像を目視し、上記の対応・範囲・文字の収まりを確認した。抽出画像一覧は`actual-contact.png`。連続再生での全編の動きと、音声の聴感レビューは未実施であり、画像の確認と区別する。ユーザーは`index.html`の時刻ボタンと動画コントロールで同じ瞬間を確認できる。実ブラウザーで22秒へのシークと表示を確認した。ページは約1.2MBの動画をBlobとして読み込み、簡易HTTPサーバーでもシークできる。

## 構造と制限

- `src/state.mjs`：説明上の状態。SVGと状態テストで共用する。
- `src/index.tsx`：図・字幕・話者アイコン。同じコンポーネントを静止画と動画に使う。
- `src/example.json`：保存済み音声に対応する6字幕と時刻。内容を変える場合は音声・演出も再調整する。
- `prepare.py`：編集の上書きをせず、承認済み音声を場面単位で抽出する。
- `finish.py`：音声を結合し、既存の`verify_video.py`で検証する。

音声はVOICEVOX:四国めたん／ずんだもん。模式図であり、実API測定値ではない。出典は`lessons/prompt-caching-pi/SOURCES.md`と生成元スナップショットを引き継ぐ。このソースコードをエディターに入力された任意コードとして実行する経路は追加していない。

2026-09-08に確認した資料：[Remotion renderMedia](https://www.remotion.dev/docs/renderer/render-media)、[renderStill](https://www.remotion.dev/docs/renderer/render-still)、[ライセンス](https://www.remotion.dev/license)。今回の個人利用はFree Licenseの対象。npmのlockfileでバージョンを固定し、Remotionランタイム・Chromium・生成動画はGit管理外に置く。
