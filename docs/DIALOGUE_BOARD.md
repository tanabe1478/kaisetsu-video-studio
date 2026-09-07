# 掛け合いと黒板図解

## 台本ノートでの操作

1. 「台本全体の設定」→「解説形式・話者」で1人解説／2人の掛け合いを選ぶ。
2. 「霊夢・魔理沙に設定」で導入済みのきつね素材を選べる。既存のセリフは書き換えず、話者IDも保持する。
3. セリフごとの「このセリフの話者」で発言者を指定。話者設定では表示名・VOICEVOX話者・スタイル・字幕色・画像・クレジットを変更できる。
4. 場面の「黒板の図解」で流れ／比較／関係を選び、「見出し | 説明」を1行ずつ入力する。最大4項目。
5. 各セリフの「黒板に表示する項目数」「黒板の強調」で説明の進行に合わせる。0は全部表示／強調なし。指定はそのセリフの開始時に切り替わり、次のセリフまで保持される。
6. 「プレビューするセリフ」または「このセリフの画面を見る」で静止画、「場面プレビュー」で音声付き動画を確認する。

黒板図解はコード・箇条書きより優先される。図解を無効にすると元のコード・箇条書きを利用する。黒板プレビューは動画と同じ描画関数を使用する。口パクや音声の確認は場面動画で行う。
図の内容は編集可能な構造データであり、画像生成AIへ送信しない。意味に沿った項目分解や図の選択は、制作依頼を受けたAIが行う。

## 台本JSON

```json
{
  "presentationMode": "dialogue",
  "characters": [
    {"id":"host","name":"霊夢","speaker":"四国めたん","style":"ノーマル","art":"kitsune:reimu","color":"#ffc7cc","credit":"きつね（仮）／東方Project二次創作"},
    {"id":"guest","name":"魔理沙","speaker":"ずんだもん","style":"ノーマル","art":"kitsune:marisa","color":"#ffe08a","credit":"きつね（仮）／東方Project二次創作"}
  ],
  "scenes": [{
    "heading":"入力から出力へ",
    "board":{"layout":"flow","nodes":[{"label":"入力","detail":"台本と設定"},{"label":"出力","detail":"音声と図解"}]},
    "narration":[
      {"character":"host","text":"まず入力を確認しましょう。","boardStep":1,"boardFocus":1},
      {"character":"guest","text":"次に出力を確認するのだ。","boardStep":2,"boardFocus":2}
    ]
  }]
}
```

上記は既存台本のtitle/speed等に追加するフィールド例。`presentationMode`は`solo`または`dialogue`。
`characters`がない旧台本は従来のspeaker/styleとずんだもん立ち絵を継承する。セリフのcharacter省略時は先頭話者。
`solo`は発言中の1人、`dialogue`は登録した2人を左右に表示する。

`art`は`zundamon`、`avatar`（内蔵の簡易イラスト）、`kitsune:reimu`、`kitsune:marisa`、または`assets/`内の画像相対パス。
任意画像は`mouthArt`で口開き画像も指定可能。きつね素材はnormal/happy/surprised/thinkingの表情と目・口パクに対応。ずんだもん用の腕のポーズは頭部素材には適用されない。

`board.layout`は`flow`（左から右へ矢印）、`comparison`（左右比較、3〜4項目は2段）、`relation`（左右の関係）。各項目はlabelが24文字、detailが60文字以内。文字が表示枠を超えるとプレビュー・生成時にエラーを示すので短くする。
`boardStep`/`boardFocus`は並び順を基準にする。項目やセリフの並べ替え後に図の意図を確認する。

## 画像素材と音声

2026-09-07に配布元を確認。霊夢・魔理沙は**きつね（仮）の「東方新ゆっくり系」**を使用。

- 配布元：<https://ci-en.net/creator/34363/article/1770577>
- 現行利用規約（2026-05-16掲載）：<https://ci-en.net/creator/34363/article/1749040>
- 東方Project二次創作ガイドライン：<https://touhou-project.news/guideline/>

規約は非商用利用を無償で許諾している。個人向け収益化の特例はあるが、受託案件や法人利用等は別条件なので「無条件に商用無料」と扱わない。再配布、AI学習・新規画像生成、無許諾の高画質化、政治的主張への利用、指定されたプラットフォームへの公開等に制約がある。用途変更や公開時は現行規約を確認する。

素材はGit管理外の`assets/yukkuri/reimu/れいむ`と`assets/yukkuri/marisa/まりさ`へ配置する。規約確認後の取得コマンドは`python prepare_yukkuri.py --download`。既存ファイルは上書きしない。元ZIPと取得元・SHA256をローカル保存する。Python/Pillowで原寸パーツを重ね、動画表示用に縮小する。素材のAI生成・アップスケールは行わない。

**画像のキャラクターと音声エンジンは別設定。** 霊夢・魔理沙プリセットの初期音声はVOICEVOX:四国めたん／ずんだもんで、AquesTalkのゆっくり音声ではない。
VOICEVOXの話者・スタイル名はインストール済みエンジンの名前を指定する。存在しない組み合わせは生成前にエラーになる。

ゆっくり音声はセリフの`audio:"assets/audio/xxx.wav"`で用意済みのWAVを使用できる。この場合speechの再合成やspeedによる音声伸縮はしない。画像の口パクと字幕時間は実音声に合わせる。WAV以外もFFmpegが読める音声は使用可能だが、長さの事前計算で正確な値を得るにはWAVを推奨する。全セリフが外部音声ならVOICEVOXを起動する必要はない。

AquesTalkは個人・非営利の無償利用と営利利用のライセンスを区別する。開発用ライブラリをこのリポジトリへ同梱しない。
公式条件：<https://www.a-quest.com/licence_free.html> / <https://www.a-quest.com/licence.html>

## 検証

`python -m unittest discover -s editor -p "test_*.py"`と`npm --prefix editor test`。
実動画は`output/dialogue-board-check/demo.mp4`（3種類・2話者）と`output/solo-board-check/demo.mp4`（ずんだもん単独）を使った。
元の教材の台本や動画には適用せず、検証用サンプルとして台本ノートに別途読み込んでいる。
