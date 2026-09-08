"""Extract the approved scene audio without changing its words or timing."""
import json,sys,wave,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from studio import timestamp
source=root/'output/prompt-caching-pi-full-20260908';out=Path(sys.argv[1]).resolve()
if out.exists():raise FileExistsError('Use a new output directory')
out.mkdir(parents=True)
project=json.loads((source/'script.json').read_text());item=json.loads((source/'timeline.json').read_text())[7];duration=item['end']-item['start']
# Do not silently apply timings to edited wording.
saved=json.loads((root/'editor/workspace/bb6a10341df34c94ae18c51d23e344ab.json').read_text())
lines=[s for c in saved['chapters'] for s in c['scenes']][7]['lines']
assert [(l['text'],l.get('speech',l['text'])) for l in lines]==[(l['text'],l.get('speech',l['text'])) for l in item['scene']['narration']], 'Saved wording changed; regenerate audio first'
with wave.open(str(source/'narration.wav')) as w:
 rate=w.getframerate();w.setpos(round(item['start']*rate));pcm=w.readframes(round(duration*rate))
with wave.open(str(out/'narration.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm)
local={**item,'start':0,'end':duration}
(out/'timeline.json').write_text(json.dumps([local],ensure_ascii=False,indent=2))
(out/'subtitles.srt').write_text('\n'.join(f"{i+1}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(item['captions'])),encoding='utf-8-sig')
(out/'chapters.txt').write_text('00:00:00 '+item['scene']['chapter'])
(out/'CREDITS.txt').write_text('VOICEVOX:四国めたん\nVOICEVOX:ずんだもん\n図・話者アイコン：React/SVGによる自作')
(out/'source-script.json').write_text((source/'script.json').read_text())
(out/'input.json').write_text(json.dumps({'durationInFrames':item['frames'],'fps':24,'captions':item['captions']},ensure_ascii=False,indent=2))
(out/'source.json').write_text(json.dumps({'source':str(source),'sceneIndex':7,'sourceScriptSha256':hashlib.sha256((source/'script.json').read_bytes()).hexdigest(),'scope':'先頭一致の1場面を再設計した音声付き試作。全編の改訂ではない。'},ensure_ascii=False,indent=2))
print(out,duration)
