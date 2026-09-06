# Linear同期エンジンを読む

wzhudev/reverse-linear-sync-engineを題材にした、25場面・8章・99セリフの日本語教材です。コミット `45dc91e78e03300b69cc088057a28c42cee35a41` を参照します。

台本ノートの「台本を開く」から「Linear同期エンジンを読む」を選べます。各場面にコミット固定の出典リンク、テンポと立ち絵の演出案を付けています。

- `lesson.json`：動画生成・エディター用台本。
- `TRANSCRIPT.md`：読みやすい字幕用の全文。
- `SOURCES.md`：場面ごとの根拠と調査の限界。
- `repository.json`：調査時のコミットと追跡ファイル一覧。
- `sync_model.py`：教材独自の簡略化した同期モデル。元のLinearの実装ではありません。

学習例は `python lessons/reverse-linear-sync-engine/sync_model.py` で動かせます。テストは `python -m unittest discover -s lessons/reverse-linear-sync-engine -p 'test_*.py' -v`。

台本は、読み方、データの保存場所、起動・遅延読み込み、操作の送信、変更の受信、rebase、失敗・Undo・同期範囲、理解の確認の順で構成します。

`build_lesson.py` は初稿の作成用です。既存lesson.jsonがある場合は停止し、エディターでの変更を自動上書きしません。改訂は編集済みJSONから別ファイルへ行ってください。
