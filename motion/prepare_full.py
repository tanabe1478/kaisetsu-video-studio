"""Preserve the full approved script and audio for the Remotion edition."""
from pathlib import Path
import json,sys,shutil,hashlib
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]).resolve();source=root/'output/prompt-caching-pi-full-20260908'
if out.exists():raise FileExistsError('Use a new output directory')
project=json.loads((source/'script.json').read_text());timeline=json.loads((source/'timeline.json').read_text())
saved=json.loads((root/'editor/workspace/bb6a10341df34c94ae18c51d23e344ab.json').read_text());scenes=[s for c in saved['chapters'] for s in c['scenes']]
assert len(scenes)==len(timeline)==30
for current,item in zip(scenes,timeline):
 expected=item['scene']['narration'];assert len(current['lines'])==len(expected)
 for a,b in zip(current['lines'],expected):
  assert all(a.get(k)==b.get(k) for k in ['text','speech','character','direction']), 'Saved narration changed; regenerate audio first'
out.mkdir(parents=True)
for name in ['narration.wav','timeline.json','subtitles.srt','chapters.txt']:
 shutil.copyfile(source/name,out/name)
project['productionBrief']['instructions']='全30場面をRemotionで再制作し、音声付き完全版MP4を生成・検証して渡す。試作で完了しない。'
project['renderBackend']='remotion';project['motionComposition']='PromptCachingFull'
(out/'script.json').write_text(json.dumps(project,ensure_ascii=False,indent=2))
(out/'source-outline.json').write_text(json.dumps(saved,ensure_ascii=False,indent=2))
(out/'input.json').write_text(json.dumps({'timeline':timeline,'durationInFrames':sum(s['frames'] for s in timeline),'fps':24},ensure_ascii=False,indent=2))
(out/'CREDITS.txt').write_text('VOICEVOX:四国めたん\nVOICEVOX:ずんだもん\n図・話者アイコン：React/SVGによる自作')
(out/'source.json').write_text(json.dumps({'source':str(source),'sourceScriptSha256':hashlib.sha256((source/'script.json').read_bytes()).hexdigest(),'scope':'全30場面・180セリフ・10章をRemotionで再制作した完全版'},ensure_ascii=False,indent=2))
print(out, timeline[-1]['end'])
