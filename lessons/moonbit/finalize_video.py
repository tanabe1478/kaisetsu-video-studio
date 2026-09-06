"""Embed chapters and fully decode the final MP4 to verify its streams."""
from pathlib import Path
import json,subprocess,wave
import imageio_ffmpeg

root=Path(__file__).resolve().parents[2]
out=root/'output'/'moonbit'
timeline=json.loads((out/'timeline.json').read_text(encoding='utf-8'))
chapters=[]
for item in timeline:
    chapter=item['scene']['chapter']
    if not chapters or chapters[-1]['name']!=chapter:chapters.append({'name':chapter,'start':item['start']})
for i,c in enumerate(chapters):c['end']=chapters[i+1]['start'] if i+1<len(chapters) else timeline[-1]['end']
metadata=[';FFMETADATA1','title=MoonBit 言語仕様入門']
for c in chapters:
    metadata.extend(['[CHAPTER]','TIMEBASE=1/1000',f'START={round(c["start"]*1000)}',f'END={round(c["end"]*1000)}',f'title={c["name"]}'])
(out/'chapters.ffmeta').write_text('\n'.join(metadata)+'\n',encoding='utf-8')
binary=imageio_ffmpeg.get_ffmpeg_exe()
final=out/'moonbit-language-introduction.mp4'
subprocess.run([binary,'-v','error','-y','-i',str(out/'demo.mp4'),'-i',str(out/'chapters.ffmeta'),'-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart',str(final)],check=True)
subprocess.run([binary,'-v','error','-i',str(final),'-f','null','-'],check=True)
with wave.open(str(out/'narration.wav')) as audio:duration=audio.getnframes()/audio.getframerate()
assert abs(duration-timeline[-1]['end'])<1/24
previous=0
for item in timeline:
    assert abs(item['start']-previous)<1e-6
    assert abs(item['frames']/24-(item['end']-item['start']))<1e-6
    last=0
    for c in item['captions']:
        assert 0<=last<=c['start']<c['end']<=item['end']-item['start']
        last=c['end']
    previous=item['end']
report={'duration_seconds':duration,'scenes':len(timeline),'chapters':len(chapters),'caption_segments':sum(len(i['captions']) for i in timeline),'bytes':final.stat().st_size,'full_av_decode':'passed','caption_and_scene_timeline':'passed','audio_listening_review':'not performed'}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
