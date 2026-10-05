---
name: brief-interview
description: 解説コンテンツの制作ブリーフを、台本ノートのGUIの代わりにAskUserQuestionで聞き取って保存し、そのまま制作に進む。ユーザーが「インタビューで決めたい」「質問しながら条件を決めて」と言ったとき、またはブリーフが未入力のまま動画・3D図解の制作を頼まれ、GUIを使わずに進める場合に使う。
---

# 制作ブリーフのインタビュー

GUIの「制作ブリーフ」と同じ項目を、AskUserQuestionで聞き取る。保存先と形式はGUIと同じにし、以降の制作は[content-production](../../../.agents/skills/content-production/SKILL.md)に従う。GUIで作った依頼文と、このインタビューで作った依頼文は同じものとして扱う。

## 1. 聞く前に確認する

- `editor/workspace/briefs/draft.json`と、この会話で回答済みの条件を読む。回答済みの項目は聞き直さない。
- 他の題材の下書きを、今回の条件として流用しない。題材が違えば、前回の値は候補として示すだけにする。

## 2. 1回目の質問（形式と大枠）

AskUserQuestionの1回の呼び出しに、次の4問をまとめる。各問の選択肢は2〜4個。自由記述は選択肢外の入力（Other）で受ける。

| 質問 | 選択肢の例 | 保存するキー |
|---|---|---|
| 解説形式 | 1人解説（ずんだもん）／2人の掛け合い／霊夢・魔理沙の掛け合い／3D図解と解説ページ（Blender） | `presentationMode`: `solo` / `dialogue` / `yukkuri` / `diorama` |
| テーマ | 会話から読み取れる候補を2〜3個。なければ「自由に入力する」 | `topic` |
| 想定視聴者・前提知識 | 題材に合わせた2〜3段階＋「指定なし」 | `audience` |
| 最終成果物 | 形式に応じて下表 | `deliverable` |

最終成果物の選択肢は形式で変える。キャラクター系は「音声付き本編動画と台本JSON」（`video`）／「台本JSONのみ」（`script`）。3D図解は「動画・静止画・解説ページ」（`video`）／「図の定義JSONのみ」（`script`）。

## 3. 2回目の質問（形式ごとの詳細）

形式の回答で分岐し、もう1回だけAskUserQuestionを呼ぶ。

キャラクター系（`solo` / `dialogue` / `yukkuri`）:

| 質問 | 選択肢 | 保存するキー |
|---|---|---|
| 動画の長さ | 短め（5分）／標準（10分）／長め（20分）／カスタム | `targetLength`: `short` / `standard` / `long` / `custom`、`targetMinutes`: 5 / 10 / 20 / 入力値 |
| 黒板の図解 | お任せ／AIが図解・アニメーションを設計／使わない／流れ・手順 | `boardStyle`: `""` / `auto` / `none` / `flow` |
| 口調・説明スタイル | 題材に合う2〜3案＋「指定なし」 | `style` |
| 構成案を先に確認するか | 先に構成案を確認する／確認せず最後まで作る | `outlineFirst`: true / false |

3D図解（`diorama`）:

| 質問 | 選択肢 | 保存するキー |
|---|---|---|
| 使う図（複数選択） | 処理の流れの動画／2列の比較／箱と矢印の配置／お任せ | `structure` に文章で残す |
| 題材の公開範囲 | 公開してよい（lessons/に置ける）／非公開（private/に置く） | `instructions` に文章で残す |
| 詳しく扱うこと | 題材に合う2〜3案＋「指定なし」 | `focus` |
| 構成案を先に確認するか | 先に図の一覧を確認する／確認せず最後まで作る | `outlineFirst`: true / false |

3D図解では`targetMinutes`は0、`boardStyle`は空にする。動画は処理の流れの1本で、尺は流すリクエストの数で決まる。

参考URL・扱わないこと・その他の指示は、聞く必要がある場合だけ、どちらかの回の空き枠で「指定なし」を含む選択肢として聞く。質問は合計2回までにし、残りは「指定なし」として扱う。

## 4. 保存して制作に進む

回答をGUIと同じキーのJSONにまとめ、標準入力から保存する。

```sh
.venv/bin/python editor/brief.py save <<'JSON'
{"topic": "...", "presentationMode": "diorama", "deliverable": "video", "outlineFirst": false, "targetMinutes": 0}
JSON
```

macOS以外では`.venv/bin/python`を環境のPythonに読み替える。`draft.json`の上書きと、ID別フォルダーへのスナップショット（`brief.json`と`prompt.md`）の作成を行い、依頼文と保存先を出力する。検証に失敗したら、その内容を伝えて該当の質問だけ聞き直す。

出力された依頼文を、ユーザーからの制作依頼として扱う。採用した前提（「指定なし」にした項目など）を短く伝え、content-productionの手順に進む。`outlineFirst`がtrueなら、構成案を示して回答を待つ。
