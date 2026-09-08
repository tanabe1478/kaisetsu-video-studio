# Remotionによる解説動画

Remotion 4.0.522 / React 19.1.1 / SVG。既存の場面8（39.75秒、6セリフ）の文言・読み・音声・間を保持し、黒板を再設計した。その後、全30場面を再設計し、20分2.75秒の完全版へ展開した。台本ノートの描画エンジン置換はまだ行っていない。

## 完全版

最新版は `output/prompt-caching-remotion-full-20260908-v3/demo.mp4`（20分2.875秒）。「十分」の読み2箇所を修正した。[読みの確認記録](../docs/PRONUNCIATION_REVIEW.md)。30場面・180セリフ・10章。元の音声・字幕・台本の文言と間を保持する。全編の演出は `src/full.tsx`、先頭一致の比較は `src/prefix.tsx` を共用する。

```sh
.venv/bin/python motion/prepare_full.py output/full-new
node motion/render_full.mjs output/full-new
.venv/bin/python motion/review_full.py output/full-new
```

各場面の2・4・6番目のセリフで90枚のPNGを生成し、同じコンポーネントから本編を描画する。`finish_full.py` が既存音声を結合し、全編検証後に章移動付きの `index.html` を作る。`review_full.py` は完成MP4から全30場面の終盤と7つの確認時点を抽出する。画像を見るのはAI自身の工程であり、このスクリプトが意味の正しさを判定するわけではない。

制作条件・出典・元の編集内容は別ファイルに保持し、既存成果物を上書きしない。保存済み台本と生成済み音声のセリフが一致しなければ準備時点で停止する。全編の演出と確認範囲は [FULL_REMOTION.md](../lessons/prompt-caching-pi/FULL_REMOTION.md) を参照。

## 先頭一致の試作を再生成

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
- `src/index.tsx` / `src/prefix.tsx`：試作用の登録と図・字幕・話者アイコン。同じコンポーネントを静止画と動画に使う。
- `src/example.json`：保存済み音声に対応する6字幕と時刻。内容を変える場合は音声・演出も再調整する。
- `prepare.py`：編集の上書きをせず、承認済み音声を場面単位で抽出する。
- `finish.py`：音声を結合し、既存の`verify_video.py`で検証する。

音声はVOICEVOX:四国めたん／ずんだもん。模式図であり、実API測定値ではない。出典は`lessons/prompt-caching-pi/SOURCES.md`と生成元スナップショットを引き継ぐ。このソースコードをエディターに入力された任意コードとして実行する経路は追加していない。

2026-09-08に確認した資料：[Remotion renderMedia](https://www.remotion.dev/docs/renderer/render-media)、[renderStill](https://www.remotion.dev/docs/renderer/render-still)、[ライセンス](https://www.remotion.dev/license)。今回の個人利用はFree Licenseの対象。npmのlockfileでバージョンを固定し、Remotionランタイム・Chromium・生成動画はGit管理外に置く。

## 音声用表記を改訂する場合

元の編集データを残して改訂台本JSONを作り、次の経路で音声とタイムラインから再生成する。旧音声を固定して使う `prepare_full.py` とは区別する。

```sh
.venv/bin/python motion/prepare_revision.py output/revised-script.json output/revised-full
.venv/bin/python motion/reading_samples.py output/revised-full
node motion/render_full.mjs output/revised-full
```
