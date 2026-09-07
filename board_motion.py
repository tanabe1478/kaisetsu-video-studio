"""Declarative, narration-anchored chalkboard animation authored by the assistant.

No arbitrary code, remote images or generated scientific measurements are executed.
Positions are local to the 700 x 280 teaching area, not the entire video.
"""
import math
from PIL import Image, ImageDraw

FIELDS = {'x':0, 'y':0, 'w':100, 'h':50, 'opacity':1, 'progress':1}

def number(value, low, high):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and low<=value<=high

def validate(animation):
    if animation is None:return
    if not isinstance(animation,dict) or animation.get('version')!=1:raise ValueError('黒板アニメーションのバージョンが不正です。')
    if not isinstance(animation.get('intent'),str) or not 1<=len(animation['intent'])<=500:raise ValueError('黒板の説明意図を記録してください。')
    texts=animation.get('narration')
    if not isinstance(texts,list) or not texts or any(not isinstance(s,str) for s in texts):raise ValueError('演出の起点となるセリフが必要です。')
    elements=animation.get('elements')
    if not isinstance(elements,list) or not 1<=len(elements)<=60:raise ValueError('黒板の要素は1〜60個です。')
    ids=set()
    for e in elements:
        if not isinstance(e,dict) or not isinstance(e.get('id'),str) or e['id'] in ids:raise ValueError('黒板要素のIDが不正です。')
        ids.add(e['id'])
        if e.get('type') not in ('box','text','dot','arrow','path'):raise ValueError('未対応の黒板要素です。')
        if not isinstance(e.get('text',''),str) or len(e.get('text',''))>100:raise ValueError('黒板の文章を短くしてください。')
        import re
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',e.get('color','#e0e8df')):raise ValueError('黒板の色が不正です。')
        if not number(e.get('fontSize',24),12,40):raise ValueError('黒板文字サイズが不正です。')
        if e['type'] in ('arrow','path'):
            points=e.get('points')
            if not isinstance(points,list) or not 2<=len(points)<=100 or any(not isinstance(p,list) or len(p)!=2 or any(not number(v,0,1) for v in p) for p in points):raise ValueError('黒板の線の座標が不正です。')
        frames=e.get('frames')
        if not isinstance(frames,list) or not 1<=len(frames)<=40:raise ValueError('黒板のキーフレームが不正です。')
        last=-1
        for f in frames:
            if not isinstance(f,dict) or not isinstance(f.get('line'),int) or isinstance(f['line'],bool) or not 1<=f['line']<=len(texts) or not number(f.get('at',0),0,1):raise ValueError('黒板とセリフの対応が不正です。')
            pos=f['line']+f.get('at',0)
            if pos<=last:raise ValueError('黒板のキーフレームを時間順にしてください。')
            last=pos
            for k,(low,high) in {'x':(0,700),'y':(0,280),'w':(1,700),'h':(1,280),'opacity':(0,1),'progress':(0,1)}.items():
                if not number(f.get(k,FIELDS[k]),low,high):raise ValueError('黒板の位置・透明度が不正です。')
            if f.get('x',0)+f.get('w',100)>700 or f.get('y',0)+f.get('h',50)>280:raise ValueError('黒板要素が表示領域を超えます。')

def validate_alignment(scene):
    a=scene.get('boardAnimation')
    if a and a['narration'] != [l['text'] for l in scene.get('narration',[])]:
        raise ValueError('台本が変更されています。AIに黒板アニメーションの再調整を依頼してください。')

def state(element, position):
    frames=element['frames']
    keys=[f['line']+f.get('at',0) for f in frames]
    if position<keys[0]:return {**FIELDS,**frames[0],'opacity':0}
    for i in range(len(frames)-1):
        if keys[i]<=position<keys[i+1]:
            t=(position-keys[i])/(keys[i+1]-keys[i]);t=t*t*(3-2*t)
            return {k:frames[i].get(k,v)+(frames[i+1].get(k,v)-frames[i].get(k,v))*t for k,v in FIELDS.items()}
    return {**FIELDS,**frames[-1]}

def partial(points, fraction):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
    left=sum(lengths)*fraction;result=[points[0]]
    for a,b,length in zip(points,points[1:],lengths):
        if left>=length:result.append(b);left-=length
        elif length:
            result.append((a[0]+(b[0]-a[0])*left/length,a[1]+(b[1]-a[1])*left/length));break
    return result

def draw(im, animation, position):
    from presentation import fit_text
    ImageDraw.Draw(im).rectangle((275,215,1005,506),fill='#193f38')
    for e in animation['elements']:
        s=state(e,position)
        if s['opacity']<=0:continue
        layer=Image.new('RGBA',(700,280));d=ImageDraw.Draw(layer)
        x,y,w,h=[s[k] for k in ('x','y','w','h')];color=e.get('color','#e0e8df')
        if e['type']=='box':d.rounded_rectangle((x,y,x+w-1,y+h-1),radius=min(10,h/4),fill='#28534a',outline=color,width=2)
        if e['type']=='dot':d.ellipse((x,y,x+w-1,y+h-1),fill=color)
        if e['type'] in ('box','text') and e.get('text'):
            fit_text(d,e['text'],(x+5,y+5,w-10,h-10),color,e.get('fontSize',24))
        if e['type'] in ('arrow','path'):
            pts=partial([(x+a*w,y+b*h) for a,b in e['points']],s['progress'])
            if len(pts)>1 and s['progress']>0:
                d.line(pts,fill=color,width=3,joint='curve')
                if e['type']=='arrow':
                    a,b=pts[-2:];angle=math.atan2(b[1]-a[1],b[0]-a[0])
                    d.polygon([b,(b[0]-12*math.cos(angle-.5),b[1]-12*math.sin(angle-.5)),(b[0]-12*math.cos(angle+.5),b[1]-12*math.sin(angle+.5))],fill=color)
        if s['opacity']<1:layer.putalpha(layer.getchannel('A').point(lambda a:round(a*s['opacity'])))
        im.paste(layer,(290,220),layer)
