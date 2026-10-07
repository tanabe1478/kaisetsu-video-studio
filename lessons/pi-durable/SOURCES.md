# Pi Durable 解説の出典

## 参考動画

Luis Catacora「What is Pi Durable?」（[X の投稿](https://x.com/lucataco/status/2106953813907091579)、2026-10-05、2分58秒）。図の章立て（理由、ハーネス、ストレージ、クラッシュ耐性、会話の分岐、拡張、マルチプレイヤー）はこの動画に合わせた。

- 2026-10-07 に `x-twitter-video-helper` の yt-dlp で保存し、mlx_whisper（whisper-large-v3-turbo）で文字起こしした。
- Whisper の下書きは、動画に焼き込まれた字幕と照合して直した（Arendelle → Earendil、SQLI → SQLite、JSON-L → JSONL、01:06 の重複した行を削除）。
- 動画と文字起こしはこのリポジトリに含めない。保存先は `x-twitter-video-helper/pi-durable/`（`video.mp4`、`transcript-en.md`、`transcript-ja.md`）。

## リポジトリ

対象は [earendil-works/pi の packages/durable](https://github.com/earendil-works/pi/tree/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable)。2026-10-07 に取得し、コミット `eb326d265ae0b88489a6d10319307780df827cdf` に固定した。package.json のバージョンは `1.0.4`。最新の main 一般についての保証ではない。取得時の記録は `cache/repositories/pi-durable-context-20261007.json`。

| 図 | 内容 | 固定コミットの一次資料 |
|---|---|---|
| why | 「コミット済みの状態だけが観測できる」という中心の規則、不変条件 | [docs/spec.md L40–70](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/docs/spec.md#L40-L70) |
| harness | ハーネス・会話・タスク・実行環境の概念、1 回の入力の記録順 | [README の Concepts](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#concepts) / [Environment](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#environment) |
| storage | 同梱のストレージ 4 種、WAL の注意、プロセス間ロックなし、適合テスト | [README の Storage](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#storage) / [src/storage](https://github.com/earendil-works/pi/tree/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/storage) |
| storage | Storage インターフェース | [src/types.ts L1015 以降](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/types.ts#L1015) |
| storage | アイドルの会話の文脈を外す `contextRetentionMs` | [src/harness/scheduler.ts L192](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/harness/scheduler.ts#L192) / [L430–433](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/harness/scheduler.ts#L430-L433) |
| recovery | ツールのチェックポイント（意図の記録）と、復旧時の再実行の判断 | [src/harness/tool.ts L34–38](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/harness/tool.ts#L34-L38) / [L84–111](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/harness/tool.ts#L84-L111) |
| recovery | `requestId` による重複投入の防止 | [src/harness/submissions.ts L155–163](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/harness/submissions.ts#L155-L163) |
| recovery | 途中経過のコミット間隔の既定値 100 ms | [src/harness/agent.ts L34–35](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/harness/agent.ts#L34-L35) |
| fork | フォークは親の記録を分岐点まで辿る（コピーしない） | [docs/spec.md L259–265](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/docs/spec.md#L259-L265) |
| fork | サブエージェントの所有と中断、`background` タスク | [README の Abort and Subagents](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#abort-and-subagents) |
| extensions | 拡張機能の中身、同名の install による差し替え | [README の Extensions](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#extensions) / [Reload](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#reload) / [src/harness/registry.ts L73–86](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/harness/registry.ts#L73-L86) |
| extensions | `defineDoc()` の状態、コンパクション | [README の Your Own State](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#your-own-state) / [Compaction](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#compaction) |
| multiplayer | `watch()`、途中参加、未配信フレームの上限 100 | [README の Watching a Conversation](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#watching-a-conversation) / [src/session/observation.ts L15](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/session/observation.ts#L15) / [L224](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/src/session/observation.ts#L224) |
| multiplayer | steer と follow-up | [README の Busy Conversations](https://github.com/earendil-works/pi/blob/eb326d265ae0b88489a6d10319307780df827cdf/packages/durable/README.md#busy-conversations) |

## 動画とコードの差

- 動画は Cloudflare Durable Object を「この上にも作れる」例として挙げるが、固定コミットでは `src/storage/sqlite/cloudflare.ts` の `openDurableObjectSqliteStorage` が同梱されている。Postgres とキー・バリュー型ストアのアダプターは `packages/durable` にない（`grep -ri postgres` で該当なし）。
- 動画は「TypeScript で約 1 万 5000 行」とする。固定コミットで `find src -name '*.ts'` を `wc -l` で数えると、`src/testing` を除いて 17,594 行、含めると 20,404 行（空行・コメントを含む）。動画の数え方は未確認。

## 実装・教材例・実行結果の区別

- 図の説明は上記ソースを静的に読んで作った。Pi Durable のコードは実行していない。依存パッケージもインストールしていない。
- 図の中の会話の並び（user / asst の数）、ツール名 `search_issues`・`deploy`・`triage`、ToDo の値 `ship v2`、実行環境の例は、動画の画面を参考にした説明用の例で、実際の実行記録ではない。
- 第三者のソースは `cache/repositories/pi-durable-20261007` にだけ置き、この教材には転載しない。原リポジトリのライセンスは MIT。
