"""Local, script-driven VOICEVOX + PSD video renderer."""
from pathlib import Path
from functools import lru_cache
import argparse, hashlib, io, json, math, subprocess, sys, wave
import numpy as np
import requests
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from psd_tools import PSDImage
from audio_mix import prepare_audio
from direction import effective
from fonts import font
from presentation import cast, character, voice_style, validate_presentation, local_asset, backdrop, draw_people, credits

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
    dest = ROOT / 'assets' / 'sprites'; dest.mkdir(parents=True,exist_ok=True)
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
    needs_engine=any(not seg.get('audio') for scene in project['scenes'] for seg in (scene.get('narration') or [{}]))
    if needs_engine:
        version = requests.get(base + '/version',timeout=5); version.raise_for_status()
        speakers = requests.get(base + '/speakers',timeout=10); speakers.raise_for_status()
        available=speakers.json();engine_version=version.json()
    else:available=[];engine_version='external-audio'
    cache = ROOT / 'cache'; cache.mkdir(exist_ok=True)
    all_pcm, timings = [], []; total = 0; sample_rate = 24000
    for index, scene in enumerate(project['scenes']):
        print(f'Synthesizing scene {index+1}/{len(project["scenes"])}',flush=True)
        segments=scene.get('narration') or [{'text':t} for t in chunks(scene['text'])]
        parts=[]; captions=[]; offset=0
        for segment in segments:
            spoken=segment.get('speech',segment['text'])
            person=character(project,segment)
            style=voice_style(project,segment,available)
            if style is None and not segment.get('audio'):raise ValueError(f'VOICEVOXの話者・スタイルが見つかりません: {person}')
            delivery=effective(segment,scene,project['speed'])
            key = hashlib.sha256(json.dumps([spoken,style,delivery['speed'],engine_version],ensure_ascii=False).encode()).hexdigest()
            path = cache / (key + '.wav')
            if segment.get('audio'):
                external=local_asset(segment['audio'])
                if external.suffix.lower() not in ('.wav','.mp3','.m4a','.ogg','.flac','.aac'):raise ValueError('外部音声はWAV/MP3/M4A/OGG/FLAC/AACを指定してください。')
                data=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-protocol_whitelist','file,pipe','-i',str(external),'-f','s16le','-ac','1','-ar',str(sample_rate),'-'],capture_output=True,check=True).stdout
                part=np.frombuffer(data,dtype='<i2').copy()
            elif not path.exists():
                query = api(base,'/audio_query',params={'text':spoken,'speaker':style}).json()
                query.update(speedScale=delivery['speed'],outputSamplingRate=sample_rate,outputStereo=False)
                data = api(base,'/synthesis',params={'speaker':style},json=query).content
                with wave.open(io.BytesIO(data)) as f:
                    if f.getnchannels()!=1 or f.getsampwidth()!=2 or f.getframerate()!=sample_rate:
                        raise ValueError('Unexpected VOICEVOX audio format')
                path.write_bytes(data)
            if not segment.get('audio'):
                with wave.open(str(path)) as f: part=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').copy()
            captions.append({'text':segment['text'],'start':offset/sample_rate,'end':(offset+len(part))/sample_rate,'direction':delivery,'character':person['id'],'boardStep':segment.get('boardStep',0),'boardFocus':segment.get('boardFocus',0)})
            offset+=len(part);parts.append(part)
            gap=np.zeros(round(delivery['pause']*sample_rate),dtype=np.int16)
            parts.append(gap);offset+=len(gap)
        pcm = np.concatenate(parts+[np.zeros(int(scene.get('pause',.6)*sample_rate),dtype=np.int16)])
        # Quantize scene lengths to video frames, keeping all later scenes aligned.
        frames=math.ceil(len(pcm)/sample_rate*FPS)
        pcm=np.pad(pcm,(0,int(frames*sample_rate/FPS)-len(pcm)))
        timings.append({'start':total/sample_rate,'end':(total+len(pcm))/sample_rate,'frames':frames,'captions':captions,'scene':scene})
        total+=len(pcm);all_pcm.append(pcm)
    joined=np.concatenate(all_pcm)
    with wave.open(str(out/'narration.wav'),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sample_rate);f.writeframes(joined.tobytes())
    (out/'timeline.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2),encoding='utf-8')
    return timings,all_pcm,sample_rate

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

@lru_cache(maxsize=512)
def caption_lines(text):
    f=font(32)
    lines=wrap(text,f,1100)
    if len(lines)!=2:return lines
    candidates=[]
    for i in range(1,len(text)):
        if text[i] in '、。！？,.!?)]}':continue
        if text[i-1].isascii() and text[i].isascii() and text[i-1].isalpha() and text[i].isalpha():continue
        left,right=text[:i],text[i:]
        a,b=f.getlength(left),f.getlength(right)
        if max(a,b)<=1100:
            score=abs(a-b)-(120 if text[i-1] in '、。 ' else 0)
            candidates.append((score,left,right))
    return list(min(candidates)[1:]) if candidates else lines

def scene_base(project, scene, index, count):
    im=Image.new('RGB',(W,H),'#f3f6ed');d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,9),fill='#72b23f')
    d.text((54,32),project.get('series','ZUNDAMON STUDIO  /  PROTOTYPE 01'),font=font(16),fill='#57813d')
    d.text((54,71),project['title'],font=font(35),fill='#203a2a')
    d.rounded_rectangle((50,144,828,528),radius=24,fill='white')
    d.text((80,174),f'{index+1:02d} / {count:02d}  '+scene.get('chapter',''),font=font(18),fill='#72a34a')
    for n,line in enumerate(wrap(scene['heading'],font(31),715)):
        d.text((80,215+n*43),line,font=font(31),fill='#203a2a')
    if scene.get('code'):
        d.rounded_rectangle((74,272,806,514),radius=12,fill='#182734')
        cf=font(22, code=True)
        for n,line in enumerate(scene['code'].splitlines()):
            d.text((90,281+n*23),line,font=cf,fill='#b9ecc3' if line.lstrip().startswith('//') else '#e4edf6')
    else:
        for n,point in enumerate(scene.get('points',[])):
            y=305+n*59;d.ellipse((82,y+10,94,y+22),fill='#80b952')
            d.text((112,y),point,font=font(24),fill='#526452')
    d.text((54,691),'VOICEVOX:ずんだもん  /  立ち絵:坂本アヒル（無印2.3）',font=font(13),fill='#57664f')
    return im

def caption_frame(im,text,color='white',progress=0):
    d=ImageDraw.Draw(im);d.rounded_rectangle((48,548,1232,678),radius=20,fill='#203b2a')
    lines=caption_lines(text)
    if len(lines)>2:raise ValueError('Caption exceeds two lines')
    for j,line in enumerate(lines):
        d.text(((W-font(32).getlength(line))/2,562+(2-len(lines))*20+j*45),line,font=font(32),fill=color)
    d.rectangle((50,672,50+int(1180*progress),677),fill='#94d463')

def timestamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def render(project, base, out):
    validate_presentation(project)
    project.setdefault('speed',1)
    if not project.get('scenes'): raise ValueError('scenes is empty')
    if not .5<=project.get('speed',1)<=2: raise ValueError('speed must be 0.5–2')
    for s in project['scenes']:
        from board_motion import validate_alignment
        validate_alignment(s)
        s.setdefault('expression','normal');s.setdefault('pose','normal')
        if s['expression'] not in EXPRESSIONS or s['pose'] not in POSES:raise ValueError('Unknown expression/pose')
        if s.get('narration'):
            s['text']=''.join(x['text'] for x in s['narration'])
            if any(not x['text'].strip() or not x.get('speech',x['text']).strip() for x in s['narration']):raise ValueError('Empty narration segment')
        if not s.get('text','').strip():raise ValueError('Empty dialogue')
        for seg in s.get('narration',[]):
            effective(seg,s,project.get('speed',1))
            if len(wrap(seg['text'],font(32),1100))>2:raise ValueError('Caption exceeds two lines')
        if s.get('code') and not s.get('board'):
            cf=font(22, code=True)
            if len(s['code'].splitlines())>10 or any(cf.getlength(line)>696 for line in s['code'].splitlines()):raise ValueError('Code exceeds panel size')
        if not s.get('board') and (len(s.get('points',[]))>3 or any(font(24).getlength(p)>675 for p in s.get('points',[]))):raise ValueError('Use up to 3 short points per scene')
        if len(wrap(s['heading'],font(31),715))>2:raise ValueError('Heading too long')
    out.mkdir(parents=True,exist_ok=True)
    if (out/'delivery.json').exists():(out/'delivery.json').unlink()
    timing,pcm,rate=synthesize(project,base,out)
    audio_path=prepare_audio(project,ROOT,out)
    print('Preparing PSD expressions...',flush=True);images=sprites([{'expression':'normal','pose':'normal'}]+[effective(seg,s,project['speed']) for s in project['scenes'] for seg in (s.get('narration') or [{}])]) if any(c.get('art')=='zundamon' for c in cast(project)) else {}
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    command=[ffmpeg,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
             '-i',str(audio_path),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(out/'demo.mp4')]
    subtitles=[]
    with (out/'render.log').open('w',encoding='utf-8') as log:
        proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
        try:
            for i,(item,audio) in enumerate(zip(timing,pcm)):
                print(f'Rendering scene {i+1}/{len(timing)}',flush=True)
                scene=item['scene'];modern=bool(scene.get('boardAnimation') or scene.get('board') or project.get('presentationMode')=='dialogue' or project.get('characters'));bg=scene_base(project,scene,i,len(timing));captions=item['captions'];boards={}
                for caption in captions:
                    subtitles.append(f'{len(subtitles)+1}\n{timestamp(item["start"]+caption["start"])} --> {timestamp(item["start"]+caption["end"])}\n{caption["text"]}\n')
                for n in range(item['frames']):
                    t=n/FPS;sample=audio[int(t*rate):int((t+.04)*rate)].astype(float)
                    speaking=bool(len(sample) and np.sqrt(np.mean(sample**2))>450)
                    mouth=speaking and n%6<4;blink=(t+i*.71)%3.4>3.24
                    delivery=next((c['direction'] for c in reversed(captions) if c['start']<=t),captions[0]['direction'])
                    active=next((c for c in reversed(captions) if c['start']<=t),captions[0])
                    if modern:
                        boardkey=(active['boardStep'],active['boardFocus'])
                        if scene.get('boardAnimation'):
                            position=captions.index(active)+1+min(1,max(0,(t-active['start'])/(active['end']-active['start'])))
                            im=backdrop(project,scene,i,len(timing),active,motion_position=position)
                        else:
                            if boardkey not in boards:boards[boardkey]=backdrop(project,scene,i,len(timing),active)
                            im=boards[boardkey].copy()
                        draw_people(im,project,active['character'],delivery,mouth,blink,images)
                    else:
                        im=bg.copy();sprite=images[delivery['expression'],delivery['pose'],blink,mouth]
                        im.paste(sprite,(830,108),sprite)
                    caption=next((c['text'] for c in captions if c['start']<=t<c['end']),'')
                    caption_frame(im,caption,character(project,active).get('color','#ffffff') if modern else 'white',(i+n/item['frames'])/len(timing))
                    if n==min(36,item['frames']-1):im.save(out/f'scene-{i+1}.png')
                    proc.stdin.write(im.tobytes())
        finally:
            proc.stdin.close();proc.wait()
        if proc.returncode:raise RuntimeError(f'FFmpeg failed: see {out / "render.log"}')
    (out/'subtitles.srt').write_text('\n'.join(subtitles),encoding='utf-8-sig')
    chapters=[];last=None
    for item in timing:
        name=item['scene'].get('chapter',item['scene']['heading'])
        if name!=last:
            chapters.append(f'{timestamp(item["start"]).split(",")[0]} {name}');last=name
    (out/'chapters.txt').write_text('\n'.join(chapters),encoding='utf-8')
    credit_lines=credits(project)
    if any(c.get('art','').startswith('kitsune:') for c in cast(project)):
        credit_lines += ['素材配布元: https://ci-en.net/creator/34363/article/1770577',
                         '素材規約: https://ci-en.net/creator/34363/article/1749040',
                         '東方Project二次創作: https://touhou-project.news/guideline/']
    if project.get('bgm'):
        music=project['bgm'];credit_lines.append('BGM: '+music.get('title','')+' / '+music.get('creator','')+' / '+music.get('source',''))
    (out/'CREDITS.txt').write_text('\n'.join(credit_lines),encoding='utf-8')
    from verify_video import verify
    delivery=verify(out)
    print(f'Verified {out / "demo.mp4"} ({delivery["seconds"]:.2f}s)',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('script',nargs='?',default=str(ROOT/'demo.json'));parser.add_argument('--engine',default='http://localhost:50021');parser.add_argument('--output',default=str(ROOT/'output'))
    args=parser.parse_args()
    try:render(json.loads(Path(args.script).read_text(encoding='utf-8-sig')),args.engine,Path(args.output).resolve())
    except requests.ConnectionError:sys.exit('VOICEVOXに接続できません。VOICEVOXを起動して再実行してください。')
