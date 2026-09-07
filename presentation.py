"""Shared dialogue identities, local assets and deterministic chalkboard diagrams."""
from pathlib import Path
import math, re
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageOps
from fonts import font

ROOT=Path(__file__).resolve().parent

def local_asset(value):
    if not isinstance(value,str) or not value:raise ValueError('素材の相対パスを指定してください。')
    path=(ROOT/value).resolve()
    if not path.is_relative_to((ROOT/'assets').resolve()):raise ValueError('素材はassets内に置いてください。')
    if not path.is_file():raise ValueError(f'素材が見つかりません: {value}')
    return path

def cast(project):
    default={'id':'host','name':project.get('speaker','ずんだもん'),'speaker':project.get('speaker','ずんだもん'),
             'style':project.get('style','ノーマル'),'art':'zundamon','color':'#bce88a'}
    return project.get('characters') or [default]

def character(project,line):
    people=cast(project);identifier=line.get('character') or people[0]['id']
    found=next((c for c in people if c['id']==identifier),None)
    if found is None:raise ValueError(f'話者が見つかりません: {identifier}')
    return found

def voice_style(project,line,speakers):
    c=character(project,line)
    return next((s['id'] for p in speakers if p['name']==c.get('speaker','ずんだもん')
                 for s in p['styles'] if s['name']==c.get('style','ノーマル')),None)

def validate_board(board):
    if board is None:return
    if not isinstance(board,dict) or board.get('layout') not in ('flow','comparison','relation'):raise ValueError('黒板はflow/comparison/relationを指定してください。')
    nodes=board.get('nodes')
    if not isinstance(nodes,list) or not 1<=len(nodes)<=4:raise ValueError('黒板の項目は1〜4個にしてください。')
    for n in nodes:
        if not isinstance(n,dict):raise ValueError('黒板の項目が不正です。')
        for k,limit in [('label',24),('detail',60)]:
            if not isinstance(n.get(k,''),str) or len(n.get(k,''))>limit:raise ValueError(f'黒板の{k}は{limit}文字以内です。')
        if not n.get('label','').strip():raise ValueError('黒板の見出しを入力してください。')

def validate_presentation(project):
    if project.get('presentationMode','solo') not in ('solo','dialogue'):raise ValueError('解説形式が不正です。')
    people=cast(project)
    if not isinstance(people,list) or not 1<=len(people)<=2:raise ValueError('話者は1〜2人にしてください。')
    ids=set()
    for c in people:
        if not isinstance(c,dict):raise ValueError('話者設定が不正です。')
        if not isinstance(c.get('id'),str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,40}',c['id']) or c['id'] in ids:raise ValueError('話者IDが不正・重複しています。')
        ids.add(c['id'])
        for k in ('name','speaker','style','art','credit','mouthArt','audioCredit'):
            if not isinstance(c.get(k,''),str) or len(c.get(k,''))>300:raise ValueError('話者設定は300文字以内の文字列です。')
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',c.get('color','#bce88a')):raise ValueError('字幕色は#RRGGBBです。')
    for scene in project.get('scenes',[]):
        from board_motion import validate as validate_motion
        validate_motion(scene.get('boardAnimation'))
        validate_board(scene.get('board'))
        for line in scene.get('narration',[]):
            character(project,line)
            if 'audio' in line and (not isinstance(line['audio'],str) or len(line['audio'])>300):raise ValueError('音声パスが不正です。')
            for k in ('boardStep','boardFocus'):
                v=line.get(k,0)
                if isinstance(v,bool) or not isinstance(v,int) or not 0<=v<=4:raise ValueError('黒板の表示数・強調は0〜4です。')
    return project

def fit_text(draw,text,box,color,max_size=28):
    x,y,w,h=box
    for size in range(max_size,11,-1):
        f=font(size);lines=['']
        for ch in text:
            if ch=='\n':lines.append('')
            elif f.getlength(lines[-1]+ch)>w:lines.append(ch)
            else:lines[-1]+=ch
        if len(lines)*(size+7)<=h:break
    if len(lines)*(size+7)>h:raise ValueError('黒板の文字が枠を超えます。文章を短くしてください。')
    for i,line in enumerate(lines):draw.text((x+(w-f.getlength(line))/2,y+i*(size+7)),line,font=f,fill=color)

def draw_board(im,board,heading,step=0,focus=0):
    """Fixed central board leaves both side columns free for characters."""
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((249,128,1031,533),radius=12,fill='#98754d',outline='#674c30',width=3)
    d.rectangle((261,140,1019,521),fill='#193f38')
    fit_text(d,heading,(282,154,716,55),'#f3f2d6',28)
    nodes=board['nodes'];count=len(nodes);visible=count if not step else min(step,count)
    if board['layout']=='flow':
        gap=34;w=(700-gap*(count-1))/count
        boxes=[(290+i*(w+gap),255,w,178) for i in range(count)]
    else:
        cols=min(2,count);w=330;h=124 if count>2 else 222
        boxes=[(290+(i%cols)*370,225+(i//cols)*140,w,h) for i in range(count)]
        if count==1:boxes=[(420,236,440,230)]
    for i,(x,y,w,h) in enumerate(boxes[:visible]):
        highlight=focus==i+1;color='#f6de7a' if highlight else '#d9eee1'
        d.rounded_rectangle((x,y,x+w,y+h),radius=8,outline=color,width=4 if highlight else 2,fill='#28534a' if highlight else '#1b453c')
        title_h=40 if h<150 else 60
        fit_text(d,nodes[i]['label'],(x+12,y+10,w-24,title_h),color,26)
        if nodes[i].get('detail'):fit_text(d,nodes[i]['detail'],(x+12,y+title_h+18,w-24,h-title_h-28),'#e0e8df',21)
        if i and board['layout']=='flow':
            mid=y+h/2;d.line((x-30,mid,x-6,mid),fill='#f6de7a',width=3);d.polygon([(x-6,mid),(x-14,mid-6),(x-14,mid+6)],fill='#f6de7a')
    if board['layout']=='relation' and visible>=2:
        fit_text(d,'↔',(620,280,40,45),'#f6de7a',28)
    d.line((279,514,323,514),fill='#ece8c4',width=4)

def backdrop(project,scene,index=0,count=1,line=None,motion_position=1.75):
    im=Image.new('RGB',(1280,720),'#f3f2e7');d=ImageDraw.Draw(im)
    d.rectangle((0,0,1280,7),fill='#264b40')
    fit_text(d,project.get('title','解説'),(40,23,1200,50),'#273d34',32)
    d.text((43,87),f'{index+1:02d}/{count:02d}  '+scene.get('chapter',''),font=font(16),fill='#557368')
    board=scene.get('board') or {'layout':'flow','nodes':[{'label':scene.get('heading','解説'),'detail':'\n'.join(scene.get('points',[]))[:60]}]}
    draw_board(im,board,scene.get('heading',''),(line or {}).get('boardStep',0),(line or {}).get('boardFocus',0))
    if scene.get('boardAnimation'):
        from board_motion import draw, validate_alignment
        validate_alignment(scene)
        draw(im,scene['boardAnimation'],motion_position)
    elif not scene.get('board'):
        d.rectangle((275,216,1005,499),fill='#193f38')
        if scene.get('code'):
            f=font(22, code=True)
            for i,text in enumerate(scene['code'].splitlines()):d.text((291,229+i*24),text,font=f,fill='#e0eee5')
        else:fit_text(d,'\n'.join(scene.get('points',[])),(295,240,690,244),'#e0eee5',26)
    return im

@lru_cache(maxsize=64)
def asset_image(path,mtime):return Image.open(path).convert('RGBA')

@lru_cache(maxsize=32)
def kitsune_image(name,expression,mouth,blink):
    if name not in ('reimu','marisa'):raise ValueError('不明なきつね素材です。')
    folder=ROOT/'assets'/'yukkuri'/name/('れいむ' if name=='reimu' else 'まりさ')
    eyes='29' if blink else {'normal':'00','happy':'31','surprised':'05','thinking':'02'}[expression]
    im=Image.new('RGBA',(400,320))
    for group,file in [('体','00'),('髪','00'),('眉','00'),('目',eyes),('口','00c' if mouth else '00')]:
        path=folder/group/(file+'.png')
        if not path.is_file():raise ValueError('きつね素材をassets/yukkuriに準備してください。docs/DIALOGUE_BOARD.md参照。')
        im.alpha_composite(asset_image(str(path),path.stat().st_mtime_ns))
    return im

def artwork(c,delivery,mouth=False,blink=False,images=None):
    art=c.get('art','avatar')
    if art.startswith('kitsune:'):return kitsune_image(art.split(':',1)[1],delivery['expression'],mouth,blink)
    if art=='zundamon':
        if images is not None:return images[delivery['expression'],delivery['pose'],blink,mouth]
        path=ROOT/'assets'/'previews'/f"{delivery['expression']}-{delivery['pose']}.png"
        return asset_image(str(path),path.stat().st_mtime_ns)
    if art and art!='avatar':
        path=local_asset(c.get('mouthArt') if mouth and c.get('mouthArt') else art)
        return asset_image(str(path),path.stat().st_mtime_ns)
    im=Image.new('RGBA',(210,260));d=ImageDraw.Draw(im)
    d.ellipse((28,12,182,168),fill=c.get('color','#bce88a'),outline='#294b42',width=4)
    d.ellipse((65,72,75,84),fill='#294b42');d.ellipse((135,72,145,84),fill='#294b42')
    d.ellipse((91,110,119,132 if mouth else 116),fill='#294b42')
    d.rounded_rectangle((15,175,195,258),radius=30,fill=c.get('color','#bce88a'))
    return im

def draw_people(im,project,active,delivery,mouth=False,blink=False,images=None):
    people=cast(project)
    if project.get('presentationMode')!='dialogue':people=[next(c for c in people if c['id']==active)]
    for i,c in enumerate(people):
        talking=c['id']==active
        sprite=artwork(c,delivery if talking else {'expression':'normal','pose':'normal'},mouth and talking,blink,images)
        sprite=ImageOps.contain(sprite,(225,365),Image.Resampling.LANCZOS)
        x=12 if len(people)>1 and i==0 else 1043;y=490-sprite.height
        im.paste(sprite,(x+(225-sprite.width)//2,y),sprite)
        d=ImageDraw.Draw(im);color=c.get('color','#bce88a') if talking else '#d5dacf'
        d.rounded_rectangle((x,499,x+225,535),radius=8,fill=color)
        fit_text(d,c.get('name',c['id']),(x+5,501,215,32),'#203b2a',19)
    fit_text(ImageDraw.Draw(im),' / '.join(credits(project)),(35,691,1210,26),'#52665b',13)

def credits(project):
    result=[]
    for c in cast(project):
        lines=[l for s in project.get('scenes',[]) for l in (s.get('narration') or [{}]) if character(project,l)['id']==c['id']]
        if any(not l.get('audio') for l in lines):result.append('VOICEVOX:'+c.get('speaker','ずんだもん'))
        if any(l.get('audio') for l in lines):result.append(c.get('audioCredit') or '外部音声:'+c.get('name',c['id']))
        if c.get('art')=='zundamon':result.append('立ち絵:坂本アヒル')
        if c.get('art','').startswith('kitsune:'):result.append('立ち絵:きつね（仮）／東方Project二次創作')
        elif c.get('credit'):result.append(c['credit'])
    return list(dict.fromkeys(result))
