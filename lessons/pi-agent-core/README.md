# pi-agent-core を読む

約20分、霊夢と魔理沙のゆっくり音声による掛け合い。ユーザーの「同じ条件で、台本・動画まで進める」に基づき制作した。全24場面の黒板は、この題材の説明に合わせてAIが図と動きを設計している。

`lesson.json` は音声を付ける前の編集可能な台本。`dialogue.txt` は文章の元データ、`build_lesson.py` はこの具体的な台本と絵コンテを再現するスクリプトであり、任意のリポジトリを自動解説するAIではない。既存の `lesson.json` がある場合は上書きを拒否する。ユーザーが編集した台本は、その編集版を起点に別ファイルへ改訂する。

## 構成と時間配分

| 章 | ねらい | 合成音声からの見込み |
|---|---|---:|
| 1 エージェントの全体像 | モデル通信・会話制御・アプリを分ける | 2:17 |
| 2 入力と状態 | prompt、履歴、実行中の制約を理解する | 2:21 |
| 3 モデルへ届くまで | 文脈変換とストリームを追う | 2:27 |
| 4 ツール実行の往復 | ターン、検証、失敗の戻り道を追う | 2:21 |
| 5 並列実行と順序 | 完了順と履歴順、直列化の条件を分ける | 2:27 |
| 6 途中の指示と停止 | steer、followUp、停止の境界を分ける | 2:26 |
| 7 セッションを支える実行基盤 | Harness、履歴の木、保存・実行環境を位置づける | 2:33 |
| 8 読み方と検証 | 読む順番と検証の範囲を整理する | 2:44 |

完成時の正確なチャプターと尺は `VALIDATION.md` と出力フォルダーの `VERIFICATION.json` に記録する。長い無音や音声の引き伸ばしで目標に合わせていない。

## 黒板の動き

文脈の選別、応答の追加、ツール結果の返却、A/Bの完了と並べ直し、追加指示の挿入、停止位置、履歴の枝分かれ、要約と末尾への集約を描く。各場面の `boardAnimation.intent` に理解目標を保存した。座標や秒数をユーザーへ求めず、セリフとその進行率へ動きを結びつけている。

## 再生成

リポジトリルートから実行する。素材とAquesTalkPlayerはローカルに準備済みであることが必要。新しい出力先を使う。

```powershell
python prepare_yukkuri_audio.py lessons/pi-agent-core/lesson.json editor/workspace/exports/pi-agent-core-new/script.json --player assets/tools/aquestalkplayer/aquestalkplayer/AquesTalkPlayer.exe
python lessons/pi-agent-core/check_storyboard.py editor/workspace/exports/pi-agent-core-new/script.json
python studio.py editor/workspace/exports/pi-agent-core-new/script.json --output output/pi-agent-core-new
python lessons/pi-agent-core/finalize_video.py output/pi-agent-core-new editor/workspace/exports/pi-agent-core-new/script.json
```

`check_storyboard.py` は全場面をセリフの1/4刻みで描画し、文字枠を検査する。`finalize_video.py` はMP4へチャプターを埋め込み、全編の映像・音声をデコードして、台本とのタイムライン一致を確認する。実コードの検証結果は [SOURCES.md](SOURCES.md) に別途記載した。
