"""Local, script-driven VOICEVOX + PSD video renderer."""
from pathlib import Path
import argparse, hashlib, io, json, math, subprocess, sys, wave
import numpy as np
import requests
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from psd_tools import PSDImage

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1280, 720, 24
EXPRESSIONS = {'normal': ('*目セット', '*普通眉'), 'happy': ('*にっこり', '*普通眉'),
               'surprised': ('*〇〇', '*上がり眉'), 'thinking': ('*ジト目', '*困り眉1')}
POSES = {'normal': ('*基本', '*基本'), 'wave': ('*手を挙げる', '*基本'),
         'point': ('*指差し', '*基本'), 'think': ('*基本', '*考える')}

def select(group, name):
    if name not in [x.name for x in group]:
        raise ValueError(f'PSD layer missing: {group.name}/{name}')
    for layer in group:
        layer.visible = layer.name == name

def child(group, name):
    return next(x for x in group if x.name == name)

def sprites(scenes):
    dest = ROOT / 'assets' / 'sprites'; dest.mkdir(exist_ok=True)
    psdpath = next((ROOT / 'assets' / 'original').rglob('*.psd'), None)
    if not psdpath:
        raise ValueError('assets/original に坂本アヒル無印2.3のPSDを置いてください。')
    psd = PSDImage.open(psdpath)
    result = {}
    for expression, pose in sorted({(s['expression'], s['pose']) for s in scenes}):
        eyes, brow = EXPRESSIONS[expression]
        right, left = POSES[pose]
        select(child(psd, '!眉'), brow)
        clothes = child(psd, '*服装1')
        select(child(clothes, '!右腕'), right); select(child(clothes, '!左腕'), left)
        for blink in (False, True):
            select(child(psd, '!目'), '*UU' if blink else eyes)
            for mouth in (False, True):
                select(child(psd, '!口'), '*ほあー' if mouth else '*むふ')
                path = dest / f'{expression}-{pose}-{int(blink)}-{int(mouth)}.png'
                if not path.exists():
                    psd.composite(force=True).crop((140, 60, 990, 1620)).save(path)
                result[expression, pose, blink, mouth] = Image.open(path).convert('RGBA').resize((425,780),Image.Resampling.LANCZOS)
    return result

def api(base, route, **kwargs):
    r = requests.post(base + route, timeout=180, **kwargs)
    r.raise_for_status(); return r

def synthesize(project, base, out):
    version = requests.get(base + '/version',timeout=5); version.raise_for_status()
    speakers = requests.get(base + '/speakers',timeout=10); speakers.raise_for_status()
    speaker = next(x for x in speakers.json() if x['name'] == project['speaker'])
    style = next(x for x in speaker['styles'] if x['name'] == project['style'])['id']
    cache = ROOT / 'cache'; cache.mkdir(exist_ok=True)
    all_pcm, timings = [], []; total = 0; sample_rate = 24000
    for index, scene in enumerate(project['scenes']):
        key = hashlib.sha256(json.dumps([scene['text'],style,project['speed'],version.json()],ensure_ascii=False).encode()).hexdigest()
        path = cache / (key + '.wav')
        if not path.exists():
            print(f'Synthesizing {index+1}/{len(project["scenes"])}',flush=True)
            query = api(base,'/audio_query',params={'text':scene['text'],'speaker':style}).json()
            query.update(speedScale=project['speed'],outputSamplingRate=sample_rate,outputStereo=False)
            data = api(base,'/synthesis',params={'speaker':style},json=query).content
            with wave.open(io.BytesIO(data)) as f:
                if f.getnchannels()!=1 or f.getsampwidth()!=2 or f.getframerate()!=sample_rate:
                    raise ValueError('Unexpected VOICEVOX audio format')
            path.write_bytes(data)
        with wave.open(str(path)) as f: pcm=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').copy()
        pcm = np.concatenate([pcm,np.zeros(int(.35*sample_rate),dtype=np.int16)])
        # Quantize scene lengths to video frames, keeping all later scenes aligned.
        frames=math.ceil(len(pcm)/sample_rate*FPS)
        pcm=np.pad(pcm,(0,int(frames*sample_rate/FPS)-len(pcm)))
        timings.append({'start':total/sample_rate,'end':(total+len(pcm))/sample_rate,'frames':frames,'scene':scene})
        total+=len(pcm);all_pcm.append(pcm)
    joined=np.concatenate(all_pcm)
    with wave.open(str(out/'narration.wav'),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sample_rate);f.writeframes(joined.tobytes())
    (out/'timeline.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2),encoding='utf-8')
    return timings,all_pcm,sample_rate

def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/meiryob.ttc',size)

def wrap(text, f, width):
    lines=['']
    for char in text:
        if char=='\n': lines.append('');continue
        if f.getlength(lines[-1]+char)>width: lines.append(char)
        else: lines[-1]+=char
    return lines

def chunks(text):
    import re
    result=[]
    for part in re.findall(r'[^。！？!?]+[。！？!?]?',text):
        while len(part)>36: result.append(part[:36]);part=part[36:]
        if part:result.append(part)
    return result

def scene_base(project, scene, index, count):
    im=Image.new('RGB',(W,H),'#f3f6ed');d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,9),fill='#72b23f')
    d.text((54,32),'ZUNDAMON STUDIO  /  PROTOTYPE 01',font=font(16),fill='#57813d')
    d.text((54,71),project['title'],font=font(35),fill='#203a2a')
    d.rounded_rectangle((50,144,828,528),radius=24,fill='white')
    d.text((80,174),f'{index+1:02d}  /  {count:02d}',font=font(18),fill='#72a34a')
    for n,line in enumerate(wrap(scene['heading'],font(31),715)):
        d.text((80,215+n*43),line,font=font(31),fill='#203a2a')
    for n,point in enumerate(scene.get('points',[])):
        y=305+n*59;d.ellipse((82,y+10,94,y+22),fill='#80b952')
        d.text((112,y),point,font=font(24),fill='#526452')
    d.text((54,691),'VOICEVOX:ずんだもん  /  立ち絵:坂本アヒル（無印2.3）',font=font(13),fill='#57664f')
    return im

def timestamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def render(project, base, out):
    if not project.get('scenes'): raise ValueError('scenes is empty')
    if not .5<=project.get('speed',1)<=2: raise ValueError('speed must be 0.5–2')
    for s in project['scenes']:
        s.setdefault('expression','normal');s.setdefault('pose','normal')
        if s['expression'] not in EXPRESSIONS or s['pose'] not in POSES:raise ValueError('Unknown expression/pose')
        if not s.get('text','').strip():raise ValueError('Empty dialogue')
        if len(s.get('points',[]))>3 or any(font(24).getlength(p)>675 for p in s.get('points',[])):raise ValueError('Use up to 3 short points per scene')
        if len(wrap(s['heading'],font(31),715))>2:raise ValueError('Heading too long')
    out.mkdir(parents=True,exist_ok=True)
    timing,pcm,rate=synthesize(project,base,out)
    print('Preparing PSD expressions...',flush=True);images=sprites(project['scenes'])
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    command=[ffmpeg,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
             '-i',str(out/'narration.wav'),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(out/'demo.mp4')]
    subtitles=[]
    with (out/'render.log').open('w',encoding='utf-8') as log:
        proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
        try:
            for i,(item,audio) in enumerate(zip(timing,pcm)):
                print(f'Rendering scene {i+1}/{len(timing)}',flush=True)
                scene=item['scene'];bg=scene_base(project,scene,i,len(timing));texts=chunks(scene['text']);weights=np.cumsum([len(t) for t in texts]);weights=weights/weights[-1]
                cuts=[0]+[round(float(w)*item['frames']) for w in weights]
                for j,txt in enumerate(texts):
                    subtitles.append(f'{len(subtitles)+1}\n{timestamp(item["start"]+cuts[j]/FPS)} --> {timestamp(item["start"]+cuts[j+1]/FPS)}\n{txt}\n')
                for n in range(item['frames']):
                    t=n/FPS;sample=audio[int(t*rate):int((t+.04)*rate)].astype(float)
                    speaking=bool(len(sample) and np.sqrt(np.mean(sample**2))>450)
                    mouth=speaking and n%6<4;blink=(t+i*.71)%3.4>3.24
                    im=bg.copy();sprite=images[scene['expression'],scene['pose'],blink,mouth]
                    im.paste(sprite,(830,108-int(2*math.sin(t*3))),sprite)
                    d=ImageDraw.Draw(im);d.rounded_rectangle((48,548,1232,678),radius=20,fill='#203b2a')
                    caption=texts[min(len(texts)-1,int(np.searchsorted(cuts[1:],n,side='right')))]
                    lines=wrap(caption,font(32),1100)
                    for j,line in enumerate(lines):
                        d.text(((W-font(32).getlength(line))/2,562+(2-len(lines))*20+j*45),line,font=font(32),fill='white')
                    d.rectangle((50,672,50+int(1180*(i+n/item['frames'])/len(timing)),677),fill='#94d463')
                    if n==min(36,item['frames']-1):im.save(out/f'scene-{i+1}.png')
                    proc.stdin.write(im.tobytes())
        finally:
            proc.stdin.close();proc.wait()
        if proc.returncode:raise RuntimeError(f'FFmpeg failed: see {out / "render.log"}')
    (out/'subtitles.srt').write_text('\n'.join(subtitles),encoding='utf-8-sig')
    print(f'Created {out / "demo.mp4"} ({timing[-1]["end"]:.2f}s)',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('script',nargs='?',default=str(ROOT/'demo.json'));parser.add_argument('--engine',default='http://localhost:50021');parser.add_argument('--output',default=str(ROOT/'output'))
    args=parser.parse_args()
    try:render(json.loads(Path(args.script).read_text(encoding='utf-8-sig')),args.engine,Path(args.output).resolve())
    except requests.ConnectionError:sys.exit('VOICEVOXに接続できません。VOICEVOXを起動して再実行してください。')
