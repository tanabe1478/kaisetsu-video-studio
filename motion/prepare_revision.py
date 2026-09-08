"""Synthesize a revised script into a NEW directory for the full Remotion renderer."""
from pathlib import Path
import sys,json,shutil
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from studio import synthesize,timestamp
source=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
if out.exists():raise FileExistsError('既存成果物を保持するため、新しい出力先を指定してください。')
project=json.loads(source.read_text())
if project.get('motionComposition')!='PromptCachingFull' or len(project['scenes'])!=30 or any(len(s.get('narration',[]))!=6 for s in project['scenes']):
 raise ValueError('この生成経路はPromptCachingFullの30場面・各6セリフ専用です。')
out.mkdir(parents=True)
shutil.copyfile(source,out/'script.json')
timeline,_,_=synthesize(project,'http://127.0.0.1:50021',out)
(out/'input.json').write_text(json.dumps({'timeline':timeline,'durationInFrames':sum(s['frames'] for s in timeline),'fps':24},ensure_ascii=False,indent=2))
subtitles=[];chapters=[];last=None
for item in timeline:
 for c in item['captions']:
  subtitles.append(f'{len(subtitles)+1}\n{timestamp(item["start"]+c["start"])} --> {timestamp(item["start"]+c["end"])}\n{c["text"]}\n')
 name=item['scene'].get('chapter','')
 if name!=last:
  seconds=round(item['start']*1000)//1000;chapters.append(f'{seconds//3600:02d}:{seconds//60%60:02d}:{seconds%60:02d} {name}');last=name
(out/'subtitles.srt').write_text('\n'.join(subtitles),encoding='utf-8-sig')
(out/'chapters.txt').write_text('\n'.join(chapters))
(out/'CREDITS.txt').write_text('VOICEVOX:四国めたん\nVOICEVOX:ずんだもん\n図・話者アイコン：React/SVGによる自作')
print('Revised duration',timeline[-1]['end'])
