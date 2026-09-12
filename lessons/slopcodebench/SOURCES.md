# SlopCodeBench — 出典と調査範囲

調査日：2026-09-12。約30分・2人の掛け合い・音声付き本編まで、という承認済み条件を採用。完成尺は音声の実測から決め、自然な速度を保持する。

## 資料の版を混ぜない

- [ユーザーのCosenseノート](https://scrapbox.io/tanabe-paper-reading/SlopCodeBench：長期反復タスクでコーディングエージェントのコード劣化を測る)：cosense CLIで取得。pageId `497315136bbdc05e152836aa`、commitId `6aa521c2feeb5ad1204cbfc1`。参照先は論文v1。
- [論文v1](https://arxiv.org/html/2603.24755v1)：20問題・93チェックポイント・11モデル。
- [論文v2](https://arxiv.org/html/2603.24755v2)：2026-05-07版、36問題・196チェックポイント・15モデル。本動画の数式・報告値は原則こちら。
- [現行サイト](https://www.scbench.ai/)：随時更新されるランキング。調査時19モデル。論文の基本プロンプトの表と条件を確認せず合算しない。GPT-5.4のISOは論文Table 1で23.5%、サイトで25.5%。同名モデルでも条件の照合が必要、という例に限って用いた。サイト値の差の原因を断定していない。

## 固定した実装

- [実行基盤](https://github.com/SprocketLab/slop-code-bench/tree/06b5c0687d4c05ee502e9696a4d0c22fc1eec5e0) — `06b5c0687d4c05ee502e9696a4d0c22fc1eec5e0`
- [問題定義](https://github.com/gabeorlanski/scb-problems/tree/ef6a9dd13911566b6b01075ca121758c9f7b5c5f) — `ef6a9dd13911566b6b01075ca121758c9f7b5c5f`
- [code_search checkpoint 1](https://github.com/gabeorlanski/scb-problems/blob/ef6a9dd13911566b6b01075ca121758c9f7b5c5f/code_search/checkpoint_1.md) — 入出力、exact/regex、Pythonの検索。
- [checkpoint 3](https://github.com/gabeorlanski/scb-problems/blob/ef6a9dd13911566b6b01075ca121758c9f7b5c5f/code_search/checkpoint_3.md) — 構文パターンとメタ変数。
- [checkpoint 3のテスト](https://github.com/gabeorlanski/scb-problems/blob/ef6a9dd13911566b6b01075ca121758c9f7b5c5f/code_search/tests/test_checkpoint_3.py) — 外部コマンドの出力、captureの文字列と範囲を照合。内部関数の名前への依存とは異なる。
- [品質集計driver](https://github.com/SprocketLab/slop-code-bench/blob/06b5c0687d4c05ee502e9696a4d0c22fc1eec5e0/src/slop_code/metrics/checkpoint/driver.py#L24) — scb-check 0.1.3を固定してuvxで呼ぶ。JSONのerosion/verbosity等を読み、版を記録。実行・読込失敗は警告と欠測であり、品質ゼロの成功と解釈しない。
- [評価report](https://github.com/SprocketLab/slop-code-bench/blob/06b5c0687d4c05ee502e9696a4d0c22fc1eec5e0/src/slop_code/evaluation/report.py) — passes_policy等の内部名を、そのまま論文のStrictと同一視しない。

第三者リポジトリは静的に読んだ。正式ベンチマーク、エージェントの課題実行、scb-check自体の再実験は実施していない。論文の測定式と現在のscb-check検出ルール全体の一致までは検証していない。コードと取得資料の原本はGit管理外のcacheに保持し、転載しない。

## 場面と根拠

| 場面 | 内容 | 根拠・区別 |
|---|---|---|
| 1–3 | 問い、版、根拠 | v1/v2 Abstract、サイト、Cosense。独自の導入 |
| 4–6 | 持ち越すコード、外部契約、課題作成 | v2 §2、Appendixの実験設定。会話はリセット、作業ディレクトリは持ち越す。採点結果は与えない |
| 7–10 | コード検索の仕様の進化 | 固定したcode_search checkpoint 1–5、tests。print(total + 1)の図は独自例 |
| 11–15 | 設計、回帰、Strict/ISO/CORE、欠測 | v2 §2.4 / Table 1。9/10テストと段階合格の比較、後半3段階欠測は独自例 |
| 16–18 | massと構造的侵食 | v2 §2の式。A/B/Cは独自例。CC×√SLOC、CC>10のmass/全mass。小分けすれば保守性が改善するとは限らない |
| 19–21 | 冗長性と独立した指標 | v2 §2 / §3.2。137ルール。100行、検出20行、clone30行、共通10行は独自例 |
| 22 | 正しさの報告値 | v2 Table 1、GPT-5.5: Strict14.8 / ISO28.1 / CORE66.8%。段階の合格率 |
| 23 | 費用 | v2 §3.1、開始から最終へ平均2.2倍。独自実測ではない |
| 24 | 悪化した軌跡の割合 | v2 §3.2、侵食77%、冗長性75.5%。コード行や関数の割合ではない |
| 25–26 | 人間との比較 | v2 §3.3。473 Pythonリポジトリ、最大30ソース変更コミット、計13,667時点。同じ課題を割り付けた対照実験ではない |
| 27–29 | プロンプト介入と例外 | v2 §3.4 / Table 3。3モデル、just-solve/anti-slop/plan-first。GPT-5.4 anti-slopの開始→最終の改善例外を保持。GPT-5.5 Strict14.8/9.2/8.2 |
| 30 | 外的妥当性 | v2 Limitations / 実験設定。Python、隠れた採点結果、モデルとハーネス |
| 31–33 | 公開実装の経路 | 固定した2リポジトリ、README、テスト、driver。静的確認のみ |
| 34–36 | 読み方、実務への提案、復習 | 論文とサイトの条件照合。実務の運用案は本動画の提案であり実証済み手法ではない |

v2本文§3.1のCORE最高モデルの記述とTable 1にモデル名の不一致があるため、その最高モデル名は教材で断定していない。数値は表を参照した。人間との比や改善効果を因果関係と断定しない。

## 素材・音声

図・アバターはReact/SVGの自作。第三者の立ち絵を使わない。音声はVOICEVOX四国めたん／ずんだもんのノーマル。字幕とspeechを分け、英語の専門語は読み用表記に変換。論文図の画像転載ではなく、論文の定義・報告値を出典付きで独自描画した。arXiv論文の表示ライセンスはCC BY 4.0。

成果物：`output/slopcodebench-full-20260912-v3/`。本編、台本、字幕、章、出典、代表場面、検証結果を同梱。検証結果と視覚確認はREVIEW.mdに分けて記録する。
