"""Extract actual encoded frames for visual review, without changing the movie."""
from pathlib import Path
import json,subprocess,sys
from PIL import Image,ImageDraw
import imageio_ffmpeg
out=Path(sys.argv[1]).resolve();timeline=json.loads((out/'timeline.json').read_text())
checks=json.loads((out/'checkpoints.json').read_text())
# Every scene's conclusion, plus the middle of meaningful transitions.
selected=[c for c in checks if c['line']==6]
for scene,line,delta in [(4,4,.2),(4,4,.6),(4,4,1.2),(17,2,.4),(20,4,.1),(13,4,1),(22,4,1)]:
 item=timeline[scene-1];frame=round((item['start']+item['captions'][line-1]['start']+delta)*24)
 selected.append({'scene':scene,'line':line,'frame':frame})
for i,c in enumerate(selected):
 name=f'actual-{i+1:02d}.png';c['file']=name
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-ss',str(c['frame']/24),'-i',str(out/'demo.mp4'),'-frames:v','1',str(out/name)],check=True)
(out/'actual-checkpoints.json').write_text(json.dumps(selected,indent=2))
for page in range((len(selected)+5)//6):
 canvas=Image.new('RGB',(1280,1170),'#f6f3e9');draw=ImageDraw.Draw(canvas)
 for j,c in enumerate(selected[page*6:(page+1)*6]):
  x=(j%2)*640;y=(j//2)*390
  im=Image.open(out/c['file']).resize((640,360));canvas.paste(im,(x,y+30))
  draw.text((x+12,y+6),f"Scene {c['scene']:02d} / Line {c['line']} / Frame {c['frame']}",fill='#173d35')
 canvas.save(out/f'actual-contact-{page+1}.png')
print(f'Extracted {len(selected)} encoded frames')
