# BGMと配置の調整

2026-09-06、ユーザーの希望で常時の上下アニメーションを削除し、BGMを追加。
立ち絵は固定位置（830, 108）。口パク・まばたき・場面別ポーズは継続する。

## 使用曲

- 曲名：ほんわかぷっぷー
- 作曲：もっぴーさうんど
- [配布ページ](https://dova-s.jp/bgm/detail/1854)
- [ダウンロードページ](https://dova-s.jp/bgm/detail/1854/download)
- [作者の利用条件](https://dova-s.jp/creator/detail/55)：サイトの音源利用ライセンスに準拠
- [音源利用ライセンス](https://dova-s.jp/help/articles/license/)
- [サイト利用規約](https://dova-s.jp/help/articles/terms/)
- 確認日・取得日：2026-09-06
- 音源SHA256：`b2b2fd0f4b30095e4f354737385733538781ae58115d6e069f010ec201229df8`

今回は解説動画の背景音楽として使用。音源利用ライセンスは背景利用と音量調整・フェード・ループ等の編集を認めている。
音楽単独の公開や再配布は行わない。サイト利用規約にプログラムによる自動収集禁止があるため、音源はユーザーがブラウザーで手動ダウンロードした。
GitHubには音源を含めず、別環境では自身で取得して `assets/bgm/honwaka-puppu.mp3` へ配置する。
本リポジトリは音源を同梱して第三者へ提供するツールではない。

## 音量設定

`lesson.json`のbgm（編集元はbuild_lesson.py）で設定する。
発話区間のRMSに対しBGMを22dB下げる目安で合成し、原曲全体を繰り返す。
冒頭2秒でフェードイン、末尾4秒でフェードアウト。声の音量と字幕時刻は保持する。
この曲は配布元では非ループ素材。曲末と次の開始を含む全曲反復であり、拍に合わせたシームレスループではない。
クレジット文は `output/moonbit/CREDITS.txt` に出力する。

## 再出力

位置変更を反映する初回は動画を再描画する。音量だけの調整は次のコマンドで反映できる。

```powershell
python lessons/moonbit/build_lesson.py
python lessons/moonbit/finalize_video.py
```

生成物：`mixed.wav`、`AUDIO_MIX.json`、`CREDITS.txt`、最終MP4。音源と生成物はGit管理外。
