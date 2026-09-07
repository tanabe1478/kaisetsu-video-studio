"""Reproduce this lesson's assistant-authored dialogue and storyboard, not a general AI generator."""
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from presentation import validate_presentation
from board_motion import validate_alignment, draw
from studio import caption_lines
from PIL import Image
HERE=Path(__file__).parent
SHA='aa23e784c647d713e775a8adcaf3c219e84f5068'
URL='https://github.com/earendil-works/pi'
GREEN='#a3e9b0'; YELLOW='#f6de7a'; RED='#ffc7cc'

def item(id,text,x,y,w=200,h=70,line=1,kind='box',color=GREEN,points=None):
    e={'id':id,'type':kind,'text':text,'color':color,'fontSize':20,
       'frames':[{'line':line,'at':0,'x':x,'y':y,'w':w,'h':h,'opacity':1,'progress':1}]}
    if points:e['points']=points
    return e
def reveal(e,line):
    f=e['frames'][0];e['frames']=[{**f,'line':line,'at':0,'opacity':0},{**f,'line':line,'at':.4,'opacity':1}];return e
def move(e,line,x,y,at=.7):
    f=e['frames'][-1];e['frames'] += [{**f,'line':line,'at':0},{**f,'line':line,'at':at,'x':x,'y':y}];return e
def link(id,x,y,w,h,line=1,points=None):
    e=item(id,'',x,y,w,h,line,'arrow',YELLOW,points or [[0,.5],[1,.5]])
    f=e['frames'][0];e['frames']=[{**f,'progress':0},{**f,'at':.7,'progress':1}];return e
def note(text):return item('note',text,0,240,700,38,kind='text',color=YELLOW)
def flow(labels,footer):
    es=[item('box'+str(i),label,i*250,55) for i,label in enumerate(labels)]
    es += [link('ab',202,72,45,35,2),link('bc',452,72,45,35,4),note(footer)]
    token=item('token','',25,160,22,22,kind='dot',color=YELLOW)
    move(token,3,275,160);move(token,5,525,160);es.append(token)
    return es
def cycle(labels,footer):
    es=flow(labels,footer)
    es.append(link('return',85,130,520,90,6,[[1,0],[1,1],[0,1],[0,0]]))
    move(es[-2],7,25,160)
    return es

def board(index):
    plans=[
      (['利用者の依頼','モデルの判断','ツールと結果'],'説明用の例：2つのファイルを比較'),
      (['アプリ\n画面と方針','agent-core\n状態と反復','pi-ai\nモデルとの通信'],'対象：0.85.1 / aa23e784'),
      (['Agent\n基本の往復','AgentHarness\n実行基盤','アプリ\n使い方を組む'],'小さい反復から、外側の仕組みへ'),
      (['モデル・指示','Agent','streamFn\n応答を取得'],'通信の入口を差し替えられる'),
      (['文章の入力','userメッセージ','ループの文脈'],'役割と内容を持つ形へ整える'),
      (['prompt\n新規開始','実行中\n重複開始を拒否','追加指示\n専用の待ち行列'],'実行中かどうかで入口を使い分ける'),
      (['アプリの履歴','文脈の加工','モデル用の形式'],'transformContext → convertToLlm'),
      (['user','assistant','toolResult'],'独自の通知は、変換または除外する'),
      (['開始','途中の更新','確定した応答'],'ストリームの状態をイベントで通知'),
      (['モデルの応答','ツール実行','結果を文脈へ'],'応答とツール処理で1ターン'),
      (['名前と引数','検証・事前フック','実行本体'],'不正・拒否の場合はエラー結果へ'),
      (['ツールの処理','事後フック','結果と終了通知'],'不完全なツール要求は実行しない'),
      (['事前検査','実行A','実行B'],'順序の説明用：所要時間の実測ではありません'),
      (['呼び出し A → B','完了 B → A','履歴 A → B'],'完了イベントと会話履歴の順序を分ける'),
      (['並列の設定','直列の指定','Aの次にB'],'いずれかのツールが要求すればバッチ全体を直列に'),
      (['進行中のターン','指示を取り出す','次の判断'],'steer：進行中の仕事に補足を届ける'),
      (['今の仕事','終了前の確認','次の仕事'],'followUp：一区切りした後に取り出す'),
      (['中止の信号','ターン終了後','結果全件の終了'],'止める位置と条件を区別する'),
      (['セッション','AgentHarness','lane'],'実行・待ち行列・設定を管理する'),
      (['共通の履歴','枝A','枝B'],'エントリの親と、枝の先端を持つ'),
      (['過去の文脈','要約＋末尾','次の判断'],'保存先・モデル・実行環境は別の役割'),
      (['README','agent.ts','agent-loop.ts'],'疑問に応じてtypes.tsやHarnessへ戻る'),
      (['ソース確認','上流テスト\n起動時に失敗','動画の検証'],'静的確認と実行結果を混同しない'),
      (['入力と文脈','実行と反復','結果と状態'],'イベントの流れと履歴を並べて読む'),
    ]
    labels,footer=plans[index];es=cycle(labels,footer) if index in (0,9,16,23) else flow(labels,footer)
    if index==0:
        es[-1]=link('return',335,130,270,90,6,[[1,0],[1,1],[0,1],[0,0]])
        es[-2]['frames'][-1]['x']=275
    if index in (1,2,18):
        es=[item('outer','',5,5,690,225,color=YELLOW),note(footer)]
        for i,label in enumerate(labels):es.append(reveal(item('layer'+str(i),label,30+i*215,70,205,100),i*2+1))
        e=item('request','',55,192,20,20,kind='dot',color=RED)
        move(e,4,270,192);move(e,6,485,192);es.append(e)
    if index==18:
        es=[note(footer),item('manager','',210,5,480,225,color=YELLOW),
            item('title','AgentHarness',240,15,410,45,kind='text',color=YELLOW),
            item('session','セッション',0,85,190,80),
            reveal(item('laneA','lane A',245,90,195,80),3),reveal(item('laneB','lane B',460,90,195,80),6),
            link('enter',191,104,49,30,3)]
        token=item('task','',50,190,20,20,kind='dot',color=RED)
        move(token,4,270,190);move(token,7,500,190);es.append(token)
    if index in (6,7):
        es=[item('history','履歴',0,0,180,45,kind='text'),item('gate','変換・選別',225,60,225,100),item('model','送信する文脈',480,0,215,45,kind='text'),note(footer)]
        for j,(text,color) in enumerate([('依頼',GREEN),('結果',YELLOW),('通知',RED)]):
            e=item('msg'+str(j),text,25,j*60+50,140,45,color=color)
            move(e,3+j,510 if j<2 else 260,j*60+50 if j<2 else 180);es.append(e)
    if index==8:
        es=[note(footer),item('message','応答メッセージ',150,5,400,45,kind='text')]
        for j,label in enumerate(['文字1','文字2','文字3']):
            e=item('delta'+str(j),label,15+j*230,160,180,55,line=j+2)
            move(e,j+3,65+j*220,75);es.append(e)
        es.append(reveal(item('complete','確定',270,175,160,50,color=YELLOW),7))
    if index==10:
        es[-1]['frames'][-1].update(x=400,y=158)
        rejection=link('reject',280,128,50,50,5,[[0,0],[0,1],[1,1]])
        rejection['color']=RED;es.append(rejection)
        es.append(reveal(item('error','エラー結果',345,175,245,45,color=RED),5))
    if index in (12,13,14):
        es=[note(footer),item('a','A',20,45,110,55),item('b','B',20,135,110,55,color=RED),
            link('routeA',140,55,380,30,2),link('routeB',140,145,380,30,2),
            item('destination','結果',540,0,140,38,kind='text',color=YELLOW)]
        a=item('movingA','A',165,40,65,50,line=3);b=item('movingB','B',165,130,65,50,line=3,color=RED)
        if index==12:
            move(b,5,580,130);move(a,7,580,40)
        elif index==13:
            a['frames'][0]['line']=1;b['frames'][0]['line']=1
            move(b,2,580,130);move(a,3,580,40)
            move(a,4,270,185);move(b,4,370,185)
            es.append(item('order','履歴：',150,188,115,40,line=4,kind='text',color=YELLOW))
            es.append(reveal(item('completion','完了通知：B → A',190,0,340,38,kind='text',color=YELLOW),3))
        else:
            move(a,4,580,40);move(b,6,165,40);move(b,7,580,130)
            es.append(reveal(item('rule','Aの終了後にBを開始',190,190,390,40,color=YELLOW),4))
        es += [a,b]
    if index in (15,16):
        es=[item('current','今のターン',0,120),item('boundary','',250,120),item('boundaryLabel','次の判断' if index==15 else '終了前',250,72,200,38,kind='text'),item('next','次の処理',500,120),note(footer),
            link('one',202,133,45,35,2),link('two',452,133,45,35,4)]
        e=item('queued','補足' if index==15 else '次の依頼',25,10,145,60,line=2,color=RED)
        move(e,5,275,125);es.append(e)
        es.append(link('queue',175,20,160,50,4,[[0,0],[1,0],[1,1]]))
    if index==17:
        es=[note(footer)]
        for j,label in enumerate(labels):
            es += [item('condition'+str(j),label,j*235,20,225,60),link('stop'+str(j),j*235+100,100,30,90,j*2+2,[[.5,0],[.5,1]]),reveal(item('end'+str(j),'停止',j*235+30,190,160,45,color=RED),j*2+2)]
    if index==19:
        es=[note(footer),item('root','依頼',15,95,120,60),item('shared','共通',190,95,120,60),link('trunk',137,110,48,30,2),
            link('upper',312,30,185,95,3,[[0,1],[1,0]]),link('lower',312,125,185,95,4,[[0,0],[1,1]]),
            reveal(item('branchA','枝A',500,5,180,55),3),reveal(item('branchB','枝B',500,180,180,55,color=RED),4)]
        tip=item('tip','先端',510,65,130,45,line=5,color=YELLOW);move(tip,6,510,125);es.append(tip)
    if index==20:
        es=[item('summary','要約',290,25,190,90,color=YELLOW),item('tail','残す末尾',500,25,190,90),note(footer)]
        for j in range(5):
            e=item('past'+str(j),str(j+1),j*48,145,42,50)
            move(e,3,295+j*58 if j<3 else 510+(j-3)*70,145);es.append(e)
        es.append(reveal(item('context','次の判断に使う文脈',285,200,405,40,kind='text'),5))
    return es,footer

SOURCES=[('README.md',1,90),('package.json',1,75),('src/index.ts',1,120),
 ('README.md',8,65),('src/agent.ts',395,459),('src/agent.ts',280,390),
 ('src/agent-loop.ts',279,325),('src/types.ts',150,205),('src/agent-loop.ts',325,378),
 ('src/agent-loop.ts',156,276),('src/agent-loop.ts',593,677),('src/agent-loop.ts',208,244),
 ('src/agent-loop.ts',487,566),('src/agent-loop.ts',487,566),('src/agent-loop.ts',409,485),
 ('src/agent.ts',280,315),('src/agent-loop.ts',250,276),('src/agent-loop.ts',240,265),
 ('src/harness/agent-harness.ts',518,622),('src/harness/session/types.ts',15,66),('src/harness/session/types.ts',30,48),
 ('src/agent.ts',408,459),('test/agent-loop.test.ts',1,70),('src/agent-loop.ts',156,276)]
READINGS={'@earendil-works/pi-agent-core':'パイ、エージェントコア','agent-core':'エージェントコア',
 'AgentHarness':'エージェントハーネス','transformContext':'トランスフォームコンテキスト','convertToLlm':'コンバートトゥーエルエルエム',
 'shouldStopAfterTurn':'シュッドストップアフターターン','AbortController':'アボートコントローラー',
 'beforeToolCall':'ビフォアツールコール','afterToolCall':'アフターツールコール','Promise.all':'プロミスオール',
 'waitForIdle':'ウェイトフォーアイドル','streamSimple':'ストリームシンプル','streamFn':'ストリームファンクション',
 'message_start':'メッセージスタート','message_update':'メッセージアップデート','message_end':'メッセージエンド',
 'agent-loop.ts':'エージェントループ、ティーエス','agent.ts':'エージェント、ティーエス','types.ts':'タイプス、ティーエス',
 'toolResult':'ツールリザルト','toolCall':'ツールコール','followUp':'フォローアップ','sequential':'シーケンシャル',
 'terminate':'ターミネイト','assistant':'アシスタント','Harness':'ハーネス','README':'リードミー','SQLite':'エスキューライト',
 'Node.js':'ノードジェイエス','0.85.1':'ゼロ、はちじゅうご、いち','pi-ai':'パイエーアイ','Agent':'エージェント',
 'prompt':'プロンプト','steer':'ステア','abort':'アボート','reset':'リセット','user':'ユーザー','lane':'レーン','pi':'パイ',
 'AI':'エーアイ','B':'ビー','A':'エー'}

def main():
    scenes=[]
    for block in HERE.joinpath('dialogue.txt').read_text(encoding='utf-8').split('## ')[1:]:
        lines=block.strip().splitlines();chapter,heading=lines[0].split(' | ')
        narration=[]
        for i,line in enumerate(lines[1:]):
            who,text=line.split(' ',1);speech=text
            for a,b in sorted(READINGS.items(),key=lambda x:-len(x[0])):speech=speech.replace(a,b)
            narration.append({'character':'reimu' if who=='R' else 'marisa','text':text,'speech':speech,
              'boardStep':0,'boardFocus':0,'direction':{'expression':'thinking' if who=='R' else ('happy' if i==7 else 'normal'),
              'pose':'normal','speed':1.02,'pause':.18,'source':'manual','reason':'AIが掛け合いの意味に合わせて設計'}})
        index=len(scenes);path,start,end=SOURCES[index];elements,intent=board(index)
        s={'chapter':chapter,'heading':heading,'expression':'normal','pose':'normal','pause':.5,
          'board':{'layout':'flow','nodes':[{'label':heading,'detail':''}]},
          'sources':[{'path':'packages/agent/'+path,'startLine':start,'endLine':end,'note':'固定コミットの実装。図の依頼・ファイル名は教材独自の例。'}],
          'narration':narration,'boardAnimation':{'version':1,'author':'AI storyboard','intent':intent,
          'narration':[l['text'] for l in narration],'elements':elements}}
        scenes.append(s)
    p={'title':'pi-agent-coreの中身：会話・ツール・実行基盤','series':'コードを読むゆっくり解説',
       'speed':1.02,'speaker':'ずんだもん','style':'ノーマル','targetMinutes':20,'targetLength':'long',
       'productionBrief':{'topic':'@earendil-works/pi-agent-core の実装解説','repositoryURL':URL,'targetMinutes':20,'targetLength':'long',
         'presentationMode':'yukkuri','boardStyle':'auto','outlineFirst':False,'audience':'TypeScriptの基本を知り、エージェントの実装を学びたい人',
         'style':'霊夢・魔理沙のゆっくり音声による掛け合い','instructions':'台本・動画まで制作。AIが黒板アニメーションを設計。自然な標準話速で約20分。',
         'structure':'全体像、入力と状態、文脈とストリーム、ツール往復、並列と順序、追加指示と停止、実行基盤、検証とまとめ'},
       'presentationMode':'dialogue','characters':[
          {'id':'reimu','name':'霊夢','speaker':'四国めたん','style':'ノーマル','art':'kitsune:reimu','color':RED,'credit':'きつね（仮）／東方Project二次創作'},
          {'id':'marisa','name':'魔理沙','speaker':'ずんだもん','style':'ノーマル','art':'kitsune:marisa','color':YELLOW,'credit':'きつね（仮）／東方Project二次創作'}],
       'bgm':{'path':'assets/bgm/honwaka-puppu.mp3','title':'ほんわかぷっぷー','creator':'もっぴーさうんど','source':'https://dova-s.jp/bgm/detail/1854','below_voice_db':22},
       'repository':{'url':URL,'commit':SHA,'checkedAt':'2026-09-07','kind':'静的解析。上流テストは依存不足で未実行。'},
       'references':[{'title':'pi / packages/agent (固定コミット)','url':URL+'/tree/'+SHA+'/packages/agent'}], 'scenes':scenes}
    validate_presentation(p)
    for s in scenes:
        validate_alignment(s)
        for line in s['narration']:caption_lines(line['text'])
        for pos in [1,2.5,4.75,6.75,8.9]:
            try:draw(Image.new('RGB',(1280,720)),s['boardAnimation'],pos)
            except Exception as e:raise ValueError(s['heading']+' / '+str(pos)) from e
    dest=HERE/'lesson.json'
    if dest.exists():raise ValueError('既存の台本は上書きしません。新規の出力先にしてください。')
    dest.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('scenes',len(scenes),'lines',sum(len(s['narration']) for s in scenes),'characters',sum(len(l['text']) for s in scenes for l in s['narration']))
if __name__=='__main__':main()
