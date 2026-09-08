"""Extract reviewed lines from the actual narration track for listening."""
from pathlib import Path
import json,sys,wave,html
out=Path(sys.argv[1]).resolve();timeline=json.loads((out/'timeline.json').read_text());blocks=[]
with wave.open(str(out/'narration.wav')) as source:
 rate=source.getframerate();params=source.getparams()
 for i,item in enumerate(timeline):
  for j,line in enumerate(item['scene']['narration']):
   if not line.get('expectedKana'):continue
   caption=item['captions'][j];source.setpos(round((item['start']+caption['start'])*rate))
   data=source.readframes(round((caption['end']-caption['start'])*rate));name=f'reading-{i+1:02d}-{j+1:02d}.wav'
   with wave.open(str(out/name),'wb') as target:target.setparams(params);target.writeframes(data)
   blocks.append(f'<h2>場面{i+1}・セリフ{j+1}</h2><p>{html.escape(line["text"])}</p><audio controls src="{name}"></audio><p>照合した読み：{html.escape(line["expectedKana"])}</p>')
(out/'readings.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><title>修正した読みの確認</title><style>body{max-width:900px;margin:40px auto;padding:20px;font:18px system-ui;background:#f6f3e9;color:#173d35}audio{width:100%}p{line-height:1.8;overflow-wrap:anywhere}</style><h1>完全版の修正音声</h1><p>本編の音声トラックから該当セリフを切り出しています。カナ照合済み。聴感確認は別工程です。</p>'+''.join(blocks)+'<p><a href="./">完全版へ戻る</a></p></html>')
