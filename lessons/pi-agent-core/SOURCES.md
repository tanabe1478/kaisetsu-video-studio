# pi-agent-core 解説の出典

対象は [earendil-works/pi の packages/agent](https://github.com/earendil-works/pi/tree/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent)。2026-09-07に取得し、コミット `aa23e784c647d713e775a8adcaf3c219e84f5068` に固定した。package.jsonのバージョンは `0.85.1`。最新のmain一般についての保証ではない。

## 説明と根拠

| 内容 | 固定コミットの一次資料 |
|---|---|
| 利用例、streamFn、メッセージの変換、SQLiteの別パッケージ | [README](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/README.md) |
| 版、依存関係、公開入口 | [package.json](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/package.json) / [index.ts](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/index.ts) |
| prompt、追加指示、abort、reset、実行中の制約 | [agent.ts L280–390](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/agent.ts#L280-L390) |
| 文脈スナップショット、実行ライフサイクル、イベントでの状態更新 | [agent.ts L408以降](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/agent.ts#L408) |
| ターンと外側の反復、追加指示を取り出す順、長さ上限で切れたツール要求 | [agent-loop.ts L156–276](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/agent-loop.ts#L156-L276) |
| 文脈加工→形式変換→ストリームの更新 | [agent-loop.ts L279–378](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/agent-loop.ts#L279-L378) |
| 直列を選ぶ条件、事前検査、並列実行、完了通知と結果メッセージの順 | [agent-loop.ts L409–566](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/agent-loop.ts#L409-L566) |
| terminateの全件判定、引数検証、事前フック | [agent-loop.ts L589–677](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/agent-loop.ts#L589-L677) |
| execute、途中の更新、実行例外、afterToolCall | [agent-loop.ts L677以降](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/agent-loop.ts#L677) |
| Harnessとlaneの公開インターフェース | [agent-harness.ts L518以降](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/harness/agent-harness.ts#L518) |
| Harnessがlaneを管理する実装 | [runtime/harness.ts](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/harness/runtime/harness.ts) |
| エントリの親、圧縮の要約と末尾、ブランチ、保存の抽象化 | [session/types.ts](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/harness/session/types.ts) / [session/session.ts](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/harness/session/session.ts) |
| Node.jsのファイル・プロセス操作 | [env/nodejs.ts](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/harness/env/nodejs.ts) |
| 読み書きなどの組み込みツール | [harness/tools](https://github.com/earendil-works/pi/tree/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/src/harness/tools) |
| 模擬ストリームによるテストの設計 | [agent-loop.test.ts](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/packages/agent/test/agent-loop.test.ts) |

## 実装・教材例・実行結果の区別

- 台本は上記ソースを静的に確認して作成した。2ファイルを比較する依頼、A/Bの所要時間、移動する点、枝A/Bは教材独自の模式例。実際のLLMセッションの再現や性能測定ではない。
- `cache/repositories/earendil-pi` に調査用コピーを取得した。第三者のソースと依存パッケージはこの教材へ同梱しない。原リポジトリのライセンスは [MIT](https://github.com/earendil-works/pi/blob/aa23e784c647d713e775a8adcaf3c219e84f5068/LICENSE)。
- 依存の取得は `npm ci --ignore-scripts --no-audit --no-fund`。ライフサイクルスクリプトは実行していない。
- `packages/agent` を作業ディレクトリにして `node ../../node_modules/vitest/dist/cli.js --run test/agent-loop.test.ts test/agent.test.ts` を実行した。
- 結果は **2スイートとも収集時に失敗し、テスト本体は未実行**。`@earendil-works/pi-ai/utils/uuid` の解決失敗と、生成済みモデルカタログ `providers/data/amazon-bedrock.json` の不足を確認した。成功扱いにしない。これを元実装の機能不良と断定もしない。
- 実LLMへの問い合わせやE2Eテストは行っていない。今回の「動作確認」は主に、台本→AquesTalk→AI黒板アニメーション→完成動画の制作フローである。

## 動画素材

霊夢・魔理沙：きつね（仮）の東方新ゆっくり系。音声：AquesTalkPlayer公式同梱「れいむ」「まりさ」（AquesTalk1、標準話速100）。BGM：もっぴーさうんど「ほんわかぷっぷー」。素材本体はGit管理外。取得元・利用条件は [対応形式の記録](../../docs/DIALOGUE_BOARD.md) と完成動画の `CREDITS.txt` を参照。個人学習用として制作した。
