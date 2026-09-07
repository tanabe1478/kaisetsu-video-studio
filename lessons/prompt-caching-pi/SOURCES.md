# 出典と検証の境界

確認日：2026-09-08。Pi：[固定コミット b2602be77cb7b0de45dd616407fd210daa48aa75](https://github.com/earendil-works/pi/tree/b2602be77cb7b0de45dd616407fd210daa48aa75)。

ローカル調査用checkout：`cache/repositories/earendil-pi-prompt-caching-20260908`。追跡ファイルの記録：`cache/repositories/prompt-caching-context-20260908.json`。作業ツリーはクリーン。コードを実行せず、入力変換、ツール追加、履歴構成、統計と関連テストを静的に確認した。

## 記事と現行仕様の扱い

- Earendilの記事は問題設定の参考。記事にある特定製品の契約・サブスクリプション事情は教材に採用していない。
- 明示／自動を会社で二分しない。公式資料を読み、現行のAPI・モデル世代で変わることを説明した。
- Piの追加ツール対応をキャッシュ保証と説明しない。ラッパー、API変換に加え、システム指示の再構築も確認した。
- Piのミス推定はトークン同一性やサーバー内部の原因を確定しない。圧縮後のリセットは統計上の扱いであり、実費の免除ではない。

## 場面別の根拠

### 01 ひと言でも、入力はひと言ではない

- **記事の分析**：[参考記事：Prompt Caching In Agents](https://earendil.com/posts/prompt-caching/)。

### 02 3種類の根拠を分けて見る

- **記事の分析**：[参考記事：Prompt Caching In Agents](https://earendil.com/posts/prompt-caching/)。
- **制作記録**：[調査対象コミット](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75)。

### 03 入力を読む段階と、答えを出す段階

- **公式資料**：[Hugging Face公式：How caching works](https://huggingface.co/docs/transformers/main/en/cache_explanation)。

### 04 KVは辞書のキーと値なのか

- **公式資料**：[Hugging Face公式：How caching works](https://huggingface.co/docs/transformers/main/en/cache_explanation)。

### 05 1回の生成から、次のリクエストへ

- **公式資料**：[vLLM公式：Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/prefix_caching/)。

### 06 保存した答えを返すキャッシュとの違い

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 07 共通部分の後ろへ追加する

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 08 途中を変えると、後ろも変わる

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 09 セッション名は一致の証明ではない

- **公式資料**：[OpenAI公式：Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)。

### 10 明示と自動は、会社名だけで分けない

- **公式資料**：[Anthropic公式：Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)。
- **公式資料**：[OpenAI公式：Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)。

### 11 保持時間は、作業時間と比べる

- **公式資料**：[Anthropic公式：Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)。

### 12 読む・書く・新しく処理する

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 13 Piと推論サーバーの境界

- **実装確認・静的解析**：[packages/ai/src/api/openai-responses.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/api/openai-responses.ts#L298-L315)。API送信パラメーター
- **実装確認・静的解析**：[packages/coding-agent/src/core/session-manager.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/session-manager.ts#L461-L469)。保存履歴からモデル向け文脈を構成

### 14 Anthropic向けの変換を追う

- **実装確認・静的解析**：[packages/ai/src/api/anthropic-messages.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/api/anthropic-messages.ts#L50-L79)。保持設定の優先順位と対応判定
- **実装確認・静的解析**：[packages/ai/src/api/anthropic-messages.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/api/anthropic-messages.ts#L1373-L1394)。最後の対応ユーザーブロックへキャッシュ境界を付与

### 15 OpenAI向けも、同じ値を直送しない

- **実装確認・静的解析**：[packages/ai/src/api/openai-responses.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/api/openai-responses.ts#L55-L99)。保持希望と互換性に応じたAPI指定
- **実装確認・静的解析**：[packages/ai/src/api/openai-responses.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/api/openai-responses.ts#L301-L310)。セッションIDをキャッシュキーへ変換

### 16 小さなツール変更が、大きく響く

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 17 Piは追加をツール結果へ記録する

- **実装確認・静的解析**：[packages/coding-agent/src/core/extensions/wrapper.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/extensions/wrapper.ts#L16-L35)。既存ツールを保持した追加をaddedToolNamesに記録

### 18 追加記録を、対応APIの形式へ

- **実装確認・静的解析**：[packages/ai/src/utils/deferred-tools.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/utils/deferred-tools.ts#L7-L39)。対応時にツールの配置を分割、非対応時は通常一覧
- **実装確認・静的解析**：[packages/ai/src/api/anthropic-messages.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/api/anthropic-messages.ts#L1182-L1215)。tool_referenceへ変換
- **実装確認・静的解析**：[packages/ai/src/api/openai-responses-shared.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/ai/src/api/openai-responses-shared.ts#L314-L346)。additional_toolsまたはtool_searchに変換

### 19 setActiveToolsだけでは保証にならない

- **実装確認・静的解析**：[packages/coding-agent/src/core/agent-session.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/agent-session.ts#L964-L988)。有効ツール変更でシステムプロンプトも再構築
- **実装確認・静的解析**：[packages/coding-agent/src/core/system-prompt.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/system-prompt.ts#L27-L46)。選択ツールをプロンプト構成に利用

### 20 ツリーの共通部分だけを見る

- **実装確認・静的解析**：[packages/coding-agent/src/core/session-manager.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/session-manager.ts#L39-L51)。エントリの親参照
- **実装確認・静的解析**：[packages/coding-agent/src/core/session-manager.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/session-manager.ts#L461-L469)。選択経路から文脈を構成

### 21 要約は、新しい文脈への作り替え

- **実装確認・静的解析**：[packages/coding-agent/src/core/cache-stats.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/cache-stats.ts#L107-L125)。圧縮と枝の要約でミス比較をリセット
- **実装確認・静的解析**：[packages/coding-agent/test/cache-stats.test.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/test/cache-stats.test.ts#L75-L87)。圧縮とモデル切替の扱いを示すテスト。今回は未実行

### 22 削る判断は、品質と将来の回数まで

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 23 R・W・CHは何を表すか

- **実装確認・静的解析**：[packages/coding-agent/src/modes/interactive/components/footer.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/modes/interactive/components/footer.ts#L90-L101)。CHの分母は直近のinput+cacheRead+cacheWrite
- **実装確認・静的解析**：[packages/coding-agent/src/modes/interactive/components/footer.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/modes/interactive/components/footer.ts#L130-L136)。RとWは累積、CHは直近の割合

### 24 再請求の推定は、原因の断定ではない

- **実装確認・静的解析**：[packages/coding-agent/src/core/cache-stats.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/cache-stats.ts#L8-L11)。1024トークンのノイズ下限
- **実装確認・静的解析**：[packages/coding-agent/src/core/cache-stats.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/cache-stats.ts#L57-L88)。利用量からミストークンと追加費用を推定
- **実装確認・静的解析**：[packages/coding-agent/src/core/cache-stats.ts](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/src/core/cache-stats.ts#L107-L125)。初回・リセット後等の比較条件

### 25 同じヒット率でも、違う体験になる

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 26 仮の単価で、再利用の効果を計算

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 27 変更を1つずつ比べる

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 28 ミスを見たときの確認順

- **実装確認・静的解析**：[packages/coding-agent/docs/settings.md](https://github.com/earendil-works/pi/blob/b2602be77cb7b0de45dd616407fd210daa48aa75/packages/coding-agent/docs/settings.md#L28-L37)。showCacheMissNoticesは既定false

### 29 3つの問いで振り返る

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

### 30 次のセッションで見るところ

- **教材独自の例**：本教材独自の説明例・診断の整理。模式図。API未実行。性能実測・料金の見積もりではない。

## 算術例の検算

通常処理の仮単価100、書込125、読取10。同じ部分を2回使う例：100+100=200、125+10=135、差65、毎回書込なら125+125=250。いずれも教材独自の仮定。新規入力と出力料金は含まない。

## 第三者コードの扱い

PiはMITライセンス。第三者コード本体はGit管理外のキャッシュへ置き、教材には長いコード転載を行っていない。動画のセリフと図は独自に作成した説明である。
