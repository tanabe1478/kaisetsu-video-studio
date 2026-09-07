# Epiplexityの掛け合い教材

承認された「長め20分・霊夢と魔理沙・定義と実験を詳しく」の構成から作った初稿。

8章・29場面・208セリフ、字幕6,505文字。VOICEVOXで全セリフを合成し、設定した間とフレーム丸めを含めて**19分59.7秒**。これは動画化前の音声タイムラインの実測で、発音の試聴は未実施。台本ノートへ別の編集用コピーとして取り込み済み。

- `lesson.json`：台本ノートへ読み込める台本。セリフ別の話者・読み・表情・黒板表示と強調を含む。
- `TRANSCRIPT.md`：読みやすい通し台本。
- `SOURCES.md`：版を固定した出典、教材独自の例、主張の確認事項。
- `VALIDATION.json`：字幕・黒板描画・編集形式の往復・音声キャッシュによる尺の確認結果。
- `dialogue.txt` / `build_lesson.py`：初稿の著作用素材。ユーザー編集後は、そのエクスポートを改訂の起点にし、ビルダーで上書きしない。

`python lessons/epiplexity/verify_lesson.py`で現在のJSONを検証できる。静止画はGit管理外の`output/epiplexity-script-check/`へ出力する。

音声合成による尺確認は行うが、台本承認段階では全編MP4を生成しない。発音を人が試聴したかどうかは検証記録の`listened`で明示する。生成時は台本ノートで保存・エクスポートした最新内容を使う。

## 承認後の全編動画（2026-09-07）

ユーザー指定のエクスポートを確認したコピーから、全編動画を生成した。完成尺19分59.67秒、1280×720・24fps、8チャプター、BGM「ほんわかぷっぷー」。ファイルはGit管理外の`output/epiplexity-20260907-final/epiplexity.mp4`。

`finalize_video.py OUTPUT SCRIPT`は生成した動画にチャプターを付け、映像・音声の全編デコード、元台本と字幕・話者・図解タイミングの一致を確認する。今回の記録は`VIDEO_VALIDATION.json`。完成MP4の冒頭・中盤・終盤の抽出画像を目視確認した。発音の試聴は未実施。

## ゆっくり音声差し替え版

2026-09-07、ユーザーの希望によりAquesTalkPlayer公式同梱の「れいむ」「まりさ」（AquesTalk1 f1/f2、標準話速100）で全208セリフを生成。元台本の文章・章順・図解・間は維持した。完成尺は19分34.58秒。元のVOICEVOX版も保持。

差し替え版：`output/epiplexity-20260907-yukkuri/epiplexity.mp4`。検証：`YUKKURI_VIDEO_VALIDATION.json`。台本ノートには「ゆっくり音声版」として別コピーを取り込んだ。音声再生成はルートの`prepare_yukkuri_audio.py`を使う。外部WAVの再生成に関する注意は`docs/DIALOGUE_BOARD.md`を参照。

## AIによる黒板アニメーションの試作

3場面を抜粋し、反復データの集約、共通部分と残りの振り分け、学習曲線の描画を設計。`output/epiplexity-motion-final/demo.mp4`（1分56.375秒）で確認できる。台本ノートでは「黒板アニメーション試作：圧縮と学習」。元の20分動画は更新していない。

`build_motion_example.py`はこの題材のAI作成絵コンテ。新しい台本の生成器ではなく、新しい内容については会話のAIが別途設計する。再生形式は`docs/BOARD_ANIMATION.md`、検証記録は`MOTION_VALIDATION.json`。
