# 3D図解と解説ページ（Blender）

キャラクターと音声を使わず、Blenderで描いた3D図解と、それをまとめた解説ページを作る。制作ブリーフの解説形式で「3D図解と解説ページ（Blender）」（`presentationMode: diorama`）を選んだときの制作方式。コードの変更点やシステムの処理の流れを、レビューや共有のために説明する用途を想定している。

## 実行

```sh
.venv/bin/python diorama.py lessons/diorama-sample/spec.json --output output/diorama-sample
```

- `--draft`を付けると低解像度・少サンプルで描く。配置の確認に使う。サンプル全体で約2分（M系Mac）。
- 既定（final）は静止画3840×2160・128サンプル、動画2560×1440・64サンプル・24fps。動画は1本で数十分かかる。
- 出力：`index.html`（解説ページ）、図ごとの`<id>.webp`（可逆圧縮）、`<id>.mp4`と`<id>-poster.webp`、`spec.json`、`render.json`、`render.log`、`delivery.json`。
- Blenderは環境変数`BLENDER`、PATH上の`blender`、macOS / Windowsの標準インストール先の順に探す。macOSでは`brew install --cask blender`で導入できる。5.2.2で確認した。
- フォントは`fonts.py`と同じく、ヒラギノ／メイリオ、Menlo／Consolasを使う。Windowsでの描画は未確認。

`delivery.json`は検証に通ったときだけ作られる。確認するのは、描画結果が定義の図と一致すること、画像の寸法、動画の全編デコード・フレーム数・解像度、解説ページがすべての成果物を参照していること。図の意味や文字の重なりは判定しないので、静止画と動画の重要なコマを別途目で確認する。

## 公開してよい題材かを先に決める

業務のコードや非公開の仕様を題材にする場合、定義JSONと成果物をGitへ登録しない。`private/`（Git管理外）か`output/`に置く。リポジトリに含めるサンプルは架空の題材にする。

## 定義JSON

最上位は`title`（ページの見出し）、`lead`（導入文）、`meta`（見出し上の小さな文字列の配列）、`figures`（図の配列）。各図に共通の項目：

| 項目 | 内容 |
|---|---|
| `id` | ファイル名に使う。英小文字・数字・ハイフン |
| `kind` | `pipeline` / `columns` / `board` |
| `title` | ページ上の節の見出し |
| `heading` / `subheading` | 図の中に描く見出し |
| `caption` | 図の下の説明。画像の代替テキストにも使う |
| `body` | 図の後に置く段落の配列 |
| `points` | `{"tag": "確認", "text": "..."}`の配列。レビューで見る点など |

文章中の`` `code` ``はページ上でコード書式になる。それ以外のHTMLはエスケープする。色（`tone`）は`blue` `teal` `amber` `purple` `green` `red` `pink` `slab`（白） `ghost`（灰） `ink` `muted`、または`#RRGGBB`。

### pipeline：処理の流れの動画

工程を左から右に並べ、リクエストを表す玉を流す。工程ごとに失敗時の受け皿を置け、どこで失敗したか、途中で何が保存・送信されたかを見せる。

- `stations`：2〜10個。`title`、`sub`（等幅の補足。`\n`で改行）、`tone`、`error`（`{"code": "409", "label": "コード重複"}`。その工程で失敗し得る場合）。
- `stores`：工程の奥に置く保存先。`kind`は`records`（レコードが積み上がる）か`topic`（封筒が飛んでいく）。`at`は工程の番号（0始まり）。
- `scenarios`：1〜6個。順に流す。`stopAt`（止まる工程）、`result`（`ok` / `error`。`error`なら`stopAt`の工程に`error`が必要）、`caption`（画面上部の説明）、`effects`（`{"at": 3, "record": "db"}` / `{"at": 4, "send": "topic"}` / `{"at": 4, "tag": "PUBLISHED"}`）、`notes`（保存先の上に出す短い注記）。
- `posterFrame`：ページで再生前に表示するフレーム。既定は98。

動画の長さは、シナリオごとに「6 + 止まる工程の番号×17 + 失敗時の落下18 + 停止40」フレームで、シナリオの間に5フレーム空く。

### columns：2列の比較

2つの構造（イベントのpayload、APIの項目など）を並べ、共通の項目と違う項目を見せる。

- `columns`：2列。`title`、`sub`、`tone`、`rows`。
- `rows`：`key`、`row`（0始まりの行）、`span`（複数行にまたがる場合）、`highlight`（違う項目。`tone`で色を変えられる）、`sub`、`value`（右端の例示値）、`valueTone`。
- 両列で同じ行に同じ`key`があれば、`=`の線で結ぶ。`link: false`で消せる。
- `notes`：`{"column": 1, "row": 3, "span": 2, "text": "...", "side": "right"}`。
- `sink`：2列の下に置く送り先（`{"title": "イベントキュー"}`）。`footnote`：右下の注記。

### board：箱と矢印の配置

型の移動、責務の集約など、決まった形に収まらない図。座標は図の中心を原点とする床面の単位で、x：-15〜15、y：-8〜8 程度に収める（既定のカメラ）。`camera`（`{"center": [0, 0.3], "ortho": 31}`）で変えられる。

- `panel`：床に置く区画（`x` `y` `w` `d` `label`）。
- `tile`：箱（`x` `y` `w` `label`、任意で`d` `h` `sub` `size` `tone` `ink` `alpha` `mono` `align`）。`h`を1前後にすると目立つ塊になる。
- `arrow`：`from`と`to`（`[x, y]`）。
- `text`：床に書く文字（`x` `y` `text` `size` `tone` `align`）。

## 構成の決め方

図は「何を理解させるか」から選ぶ。処理の順序と失敗時の後始末なら`pipeline`、2つの形の違いなら`columns`、物の移動や依存の向きなら`board`。1つの図に要素を詰め込まず、図ごとに説明を1つに絞る。動画の各シナリオは、正常系と、設計判断が効く失敗のケースに限る。
