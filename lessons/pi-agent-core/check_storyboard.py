"""Validate and sample every narrated scene before rendering the full video."""
import json, sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from presentation import backdrop, draw_people
from studio import caption_frame

p=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
out=ROOT/'output/pi-agent-core-storyboard';out.mkdir(parents=True,exist_ok=True)
for page in range(4):
    montage=Image.new('RGB',(1280,1080),'white')
    for k in range(6):
        i=page*6+k;s=p['scenes'][i];line=s['narration'][5]
        # Check all integer and intermediate positions for text fit during motion.
        for n in range(len(s['narration'])*4):
            backdrop(p,s,i,len(p['scenes']),line,motion_position=1+n/4)
        im=backdrop(p,s,i,len(p['scenes']),line,motion_position=6.75)
        draw_people(im,p,line['character'],line['direction'])
        caption_frame(im,line['text'],'#f6de7a',i/24)
        im.save(out/f'scene-{i+1:02}.png')
        montage.paste(im.resize((640,360)),((k%2)*640,(k//2)*360))
    montage.save(out/f'contact-{page+1}.png')
print('All 24 scenes sampled at 32 positions; contact sheets:',out)
