"""Validate actual captions, every board state, cast and editor round-trip."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(ROOT), str(ROOT/'editor')]
from PIL import Image, ImageDraw
import server
from presentation import backdrop, draw_people, character, validate_presentation
from direction import effective
from studio import caption_frame, caption_lines, font
from duration import estimate, engine_info

p = json.loads((HERE/'lesson.json').read_text(encoding='utf-8'))
validate_presentation(p)
assert server.script(server.import_script(p)) == p
out = ROOT/'output/epiplexity-script-check'
out.mkdir(parents=True, exist_ok=True)
last_frames = []
for i, scene in enumerate(p['scenes']):
    for line in scene['narration']:
        assert 1 <= line['boardFocus'] <= line['boardStep'] <= len(scene['board']['nodes'])
        assert len(caption_lines(line['text'])) <= 2
        im = backdrop(p, scene, i, len(p['scenes']), line)
        draw_people(im, p, character(p,line)['id'], effective(line,scene,p['speed']))
        caption_frame(im, line['text'], character(p,line)['color'])
    im.save(out/f'board-{i+1:02}.png')
    last_frames.append(im.resize((640,360)))
for start in range(0, len(last_frames), 6):
    frames = last_frames[start:start+6]
    sheet = Image.new('RGB', (1280, 360*((len(frames)+1)//2)), 'white')
    for n, im in enumerate(frames): sheet.paste(im, (n%2*640,n//2*360))
    sheet.save(out/f'contact-{start//6+1}.jpg', quality=90)
d = estimate(p, ROOT/'cache', engine_info())
report = {'date':'2026-09-07','scenes':len(p['scenes']),
          'lines':sum(len(s['narration']) for s in p['scenes']),
          'checks': ['presentation schema','all caption layouts','all board states render','editor lossless round-trip'],
          'duration':d, 'listened':False, 'fullVideoRendered':False, 'paperExperimentsReproduced':False}
(HERE/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
