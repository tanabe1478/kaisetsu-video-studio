# 出典と確認範囲

対象：[wzhudev/reverse-linear-sync-engine](https://github.com/wzhudev/reverse-linear-sync-engine)
コミット：`45dc91e78e03300b69cc088057a28c42cee35a41`
確認日：2026-09-06。取得したコミットの作業ツリーに変更なし。

## 資料の性質

作者の調査記事と注釈付きブラウザーバンドルを静的に読んだ教材です。公式ソース一式や、現在のLinearの実装を保証するものではありません。コード内の注釈・推定されたクラス名と、実際の処理を区別して参照しました。
確認した追跡ファイル一覧にはpackage.jsonや独立した同期サーバー、LICENSEファイルはありません。Root.jsのimport先には同梱されていないファイルがあります。元コードの起動・パッケージのインストール・サービスへの接続は行っていません。
元記事・画像・コードの大規模な転載はせず、日本語の説明と学習用モデルはこの教材用に作成しました。第三者の取得物はGit管理外のcacheに置いています。

## 独自の学習例と限界

同期位置100〜102、担当者の変更、sync_model.pyは説明のための簡略化です。sync_model.pyは確定した値と未完了操作を別に保持する独自モデルで、元実装のrebase関数の忠実な移植ではありません。ネットワーク、IndexedDB、権限、実データの依存関係、Undoの実装は含みません。
6件のテストで、受信と送信応答の順序、未完了操作の保持、拒否、古い通知を確認しました。元実装の正しさをテストした結果ではありません。

## 場面ごとの根拠

### 01 速い画面と同期の両立

- [README.md:18–60](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L18-L60)：調査の目的と位置付け

### 02 公式ソース一式ではない

- [README.md:50–62](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L50-L62)：作者による調査方法・非公式性の説明
- [code/Root.js:1–5](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/Root.js#L1-L5)：同梱されていないバンドルへのimportがある

### 03 読む順番を決める

- [SUMMARY.md:1–7](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/SUMMARY.md#L1-L7)：要約の位置付け
- [code/html.js:7052–7088](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L7052-L7088)：モデル登録の実装例

### 04 3つの場所を区別する

- [README.md:1080–1088](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1080-L1088)：送信待ち操作の永続化
- [README.md:1203–1207](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1203-L1207)：モデル表と楽観的変更の区別

### 05 モデルに振る舞いの情報を付ける

- [code/html.js:7052–7088](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L7052-L7088)：ModelRegistryの登録と参照
- [README.md:199–230](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L199-L230)：プロパティのメタデータ

### 06 画面は先に更新できる

- [README.md:1024–1053](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1024-L1053)：変更記録からUpdateTransaction生成まで
- [code/html.js:81006–81009](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81006-L81009)：changeSnapshot取得

### 07 起動時はローカルの状態を見る

- [code/html.js:79926–79951](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L79926-L79951)：requiredBootstrapの分岐

### 08 読み込むことと実体化は別

- [README.md:680–723](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L680-L723)：HydrationとObject Poolの説明

### 09 空と未取得を見分ける

- [README.md:859–879](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L859-L879)：部分インデックスと追加取得の判断

### 10 変更をスナップショットにする

- [code/html.js:81000–81039](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81000-L81039)：更新操作の生成・送信・直列化

### 11 送信待ちにも段階がある

- [README.md:1065–1124](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1065-L1124)：キューの構造
- [code/html.js:81330–81359](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81330-L81359)：サイズ制限と独立性の確認

### 12 オフラインでは操作を残す

- [code/html.js:81162–81166](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81162-L81166)：保存操作の読み出し
- [code/html.js:81361–81370](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81361-L81370)：オフライン時のキュー復帰
- [README.md:1084–1088](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1084-L1088)：操作のIndexedDBへの記録

### 13 送信成功と同期完了は違う

- [code/html.js:81375–81384](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81375-L81384)：completedButUnsyncedTransactionsへの保持

### 14 同期位置で待ち合わせる

- [code/html.js:81396–81415](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81396-L81415)：WaitSyncQueueの閾値比較
- [code/html.js:83253–83260](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L83253-L83260)：lastSyncId更新と待機解除

### 15 変更通知を順序立てて適用する

- [README.md:1246–1285](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1246-L1285)：接続についての調査
- [code/html.js:83072–83105](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L83072-L83105)：更新ロックと依存取得
- [code/html.js:83253–83260](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L83253-L83260)：末尾での同期位置更新

### 16 担当者の変更が交差したら

- [code/html.js:81019–81029](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81019-L81029)：更新操作のrebase
- [code/html.js:81147–81159](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81147-L81159)：再適用する未完了操作の選択

### 17 rebaseで手元の変更を重ねる

- [code/html.js:81019–81029](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81019-L81029)：original更新とsetSerializedValue
- [code/html.js:81147–81159](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81147-L81159)：対象モデルのUpdateTransactionのみ再適用

### 18 万能なマージとは考えない

- [code/html.js:81019–81029](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81019-L81029)：プロパティごとの再設定
- [README.md:18–39](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L18-L39)：作者による設計比較。一般的な優劣の断定はしない

### 19 拒否された変更をどう戻すか

- [README.md:1203–1207](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1203-L1207)：操作の完了待ちと拒否時の扱い

### 20 Undoも新しい操作になる

- [code/html.js:81042–81049](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81042-L81049)：undoTransactionからsyncClient.update
- [README.md:1482–1509](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1482-L1509)：UndoとRedoの調査

### 21 全データを全員へ配らない

- [code/html.js:83084–83093](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L83084-L83093)：グループ変更の処理
- [README.md:1415–1421](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L1415-L1421)：モデル更新とグループ離脱についての分析

### 22 小問：返事が来たら消してよい？

- [code/html.js:81375–81384](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81375-L81384)：受信完了まで操作を保持する条件

### 23 答え：対応する同期位置まで待つ

- [code/html.js:81375–81384](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81375-L81384)：保存記録削除と受信待ち
- [code/html.js:81151–81159](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81151-L81159)：同期位置に応じた再適用対象の整理

### 24 自分のツールへ持ち帰る視点

- [code/html.js:81396–81415](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81396-L81415)：待機の考え方
- [code/html.js:81019–81029](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81019-L81029)：未完了更新の重ね合わせ

### 25 今回確認したことと次の一歩

- [README.md:50–62](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/README.md#L50-L62)：調査の位置付け
- [code/html.js:81069–81090](https://github.com/wzhudev/reverse-linear-sync-engine/blob/45dc91e78e03300b69cc088057a28c42cee35a41/code/html.js#L81069-L81090)：操作管理の入口
