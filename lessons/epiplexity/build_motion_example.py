"""Assistant-authored visual explanations, applied to a copy of approved dialogue.

This is the example's storyboard, not a keyword-based substitute for AI planning.
"""
import argparse, copy, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from presentation import validate_presentation

def frame(line,at=0,**kw):return {'line':line,'at':at,**kw}
def element(id,kind,text,x,y,w,h,line=1,color='#e0e8df',**kwargs):
    return {'id':id,'type':kind,'text':text,'color':color,'frames':[frame(line,x=x,y=y,w=w,h=h)],**kwargs}
def appear(e,line,at=0,end=.3):
    f=e['frames'][0];e['frames']=[{**f,'line':line,'at':at,'opacity':0},{**f,'line':line,'at':end,'opacity':1}];return e
def move(e,line,x,y,w=None,h=None):
    f=e['frames'][-1];e['frames'] += [{**f,'line':line,'at':0},{**f,'line':line,'at':.65,'x':x,'y':y,'w':w or f['w'],'h':h or f['h']}];return e
def arrow(id,x,y,w,h,line):
    e=element(id,'arrow','',x,y,w,h,line,color='#f6de7a',points=[[0,.5],[1,.5]])
    e['frames']=[{**e['frames'][0],'progress':0},{**e['frames'][0],'at':.65,'progress':1}];return e
def attach(scene,intent,elements):
    scene['boardAnimation']={'version':1,'author':'AI storyboard','intent':intent,
                             'narration':[l['text'] for l in scene['narration']], 'elements':elements}

def main(source,output):
    if output.exists():raise ValueError('既存ファイルは上書きしません。')
    p=json.loads(source.read_text(encoding='utf-8-sig'));by={s['heading']:s for s in p['scenes']}
    scenes=copy.deepcopy([by[x] for x in ['同じ長さでも、説明は違う','圧縮を2つの箱に分ける','学習曲線で見る直感']])
    s=scenes[0];els=[element('label','text','同じ長さのデータ',0,0,700,40)]
    for i,bit in enumerate('01010101'):
        e=element('repeat'+str(i),'box',bit,25+i*48,65,40,45,color='#a3e9b0')
        move(e,2,500+(i%2)*44,65,38,45);els.append(e)
    els += [appear(element('rule','box','01を4回\n繰り返す',440,120,220,90,color='#a3e9b0'),2,end=.65),arrow('to-rule',340,125,75,30,2)]
    for i,bit in enumerate('10110010'):
        els.append(appear(element('random'+str(i),'box',bit,25+i*48,210,40,45,color='#ffc7cc'),3))
    els.append(appear(element('random-caption','text','乱数の例：結果を個別に伝える',10,165,405,40,color='#ffc7cc',fontSize=20),3))
    attach(s,'反復する8個の数字が「01を繰り返す」という規則へ集まる。下段の乱数例は個々の結果を保持し、ファイル長と説明長を区別する。',els)
    s=scenes[1]
    els=[element('data','box','共通のレシピ＋日ごとの変更',90,0,520,55,color='#f6de7a'),
         appear(element('model','box','共通のレシピ\nモデルの説明',20,130,290,90,color='#a3e9b0'),2),
         appear(element('residual','box','日ごとの変更\n残りの説明',390,130,290,90,color='#ffc7cc'),2),
         appear(element('plus','text','＋',322,150,50,50,color='#f6de7a'),2),
         appear(element('sum','text','2つの説明の合計を短くする',20,235,660,40,color='#f6de7a'),5)]
    for i in range(6):
        e=element('part'+str(i),'dot','',230+i*40,70,24,24,line=2,color='#a3e9b0' if i<3 else '#ffc7cc')
        move(e,3,80+(i%3)*70 if i<3 else 450+(i%3)*70,103);els.append(e)
    attach(s,'1つのデータ説明を、共通部分と日ごとの残りへ色分けして振り分ける。両方の説明コストを足して考えることを動きで示す。',els)
    s=scenes[2]
    els=[element('y','text','予測の損失',0,0,180,35),element('x','text','学習の進行 →',435,211,230,35),
         element('axes','path','',70,40,590,170,points=[[0,0],[0,1],[1,1]]),
         element('note','text','模式図：実測値や指標の面積ではありません',0,248,700,32,color='#f6de7a',fontSize=18)]
    paths=[('simple','すぐ覚える','#a3e9b0',2,[[0,.06],[.07,.35],[.17,.85],[.3,.94],[1,.94]]),
           ('noise','改善しない','#ffc7cc',3,[[0,.05],[.2,.08],[.5,.08],[1,.08]]),
           ('structure','改善が続く','#f6de7a',4,[[0,.04],[.15,.2],[.35,.42],[.55,.59],[.78,.74],[1,.82]])]
    for id,label,color,line,points in paths:
        e=element(id,'path','',72,42,580,162,line=line,color=color,points=points)
        e['frames']=[{**e['frames'][0],'progress':0},{**e['frames'][0],'at':.8,'progress':1}];els.append(e)
        els.append(appear(element(id+'label','text',label,90+(line-2)*195,210,190,35,color=color,fontSize=20),line))
    # Keep x-axis label separate from the legend.
    els[1]['frames'][0].update(x=420,y=0,w=260,h=35)
    attach(s,'同じ軸上で3種類の学習曲線を順に描き、難しさと継続的に学べる構造の違いを比較する。形は理解用の模式図で数値結果は作らない。',els)
    p['scenes']=scenes;p['title']='黒板アニメーション試作：圧縮と学習'
    p['targetMinutes']=0;p['productionBrief']['instructions']+=' 黒板はAIが構成と動きを設計。今回の3場面は動作確認用の抜粋。'
    validate_presentation(p);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('output',type=Path)
    a=parser.parse_args();main(a.source,a.output)
