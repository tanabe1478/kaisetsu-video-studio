"""Preproduction instructions shared with ChatGPT by the user.

GUIの制作ブリーフと、AskUserQuestionによるインタビュー（brief-interview Skill）の両方から使う。
python editor/brief.py save < brief.json で、GUIと同じ場所へ下書きとスナップショットを保存する。
"""
from pathlib import Path
import json, math, os, sys, uuid

FIELDS={'topic':'テーマ','repository':'参考URL・リポジトリ','audience':'想定視聴者・前提知識',
        'structure':'希望する構成','focus':'詳しく扱うこと','avoid':'扱わないこと',
        'style':'口調・説明スタイル','instructions':'その他の事前プロンプト',
        'presentationMode':'解説形式','boardStyle':'黒板の図解'}
MODES={'solo':'1人解説（ずんだもん）','dialogue':'2人の掛け合い','yukkuri':'霊夢・魔理沙の掛け合い',
       'diorama':'3D図解と解説ページ（Blender・キャラクターなし）'}
STORE=Path(__file__).resolve().parent/'workspace'/'briefs'

def validate(b):
    if not isinstance(b,dict):raise ValueError('制作条件が不正です。')
    for k in FIELDS:
        if not isinstance(b.get(k,''),str) or len(b.get(k,''))>20000:raise ValueError('各入力は2万文字以内にしてください。')
    n=b.get('targetMinutes',0)
    if isinstance(n,bool) or not isinstance(n,(float,int)) or not math.isfinite(n) or not 0<=n<=120:raise ValueError('目標時間は0〜120分です。')
    if not isinstance(b.get('outlineFirst',False),bool):raise ValueError('構成案確認の指定が不正です。')
    if b.get('deliverable','video') not in ('video','script'):raise ValueError('成果物は動画または台本を選んでください。')
    if b.get('presentationMode','') not in ('',*MODES):raise ValueError('解説形式が不正です。')
    return b

def diorama_prompt(b):
    """3D図解の依頼文。音声・立ち絵・黒板の指示は含めない。"""
    lines=['次の制作条件で、Blenderの3D図解と解説ページを作りたいです。音声とキャラクターは使いません。']
    for k,label in FIELDS.items():
        if k not in ('presentationMode','boardStyle') and b.get(k,'').strip():lines += ['',f'【{label}】',b[k].strip()]
    pages=b.get('deliverable','video')=='video'
    lines += ['','【進め方】','最終成果物：処理の流れの動画と静止画の3D図解、それをまとめた解説ページ（index.html）、図の定義JSON。' if pages else '最終成果物：図の定義JSONのみ（描画しない）。']
    if b.get('outlineFirst',False):lines += ['まず扱う図の一覧と、それぞれで理解させたいことを提案し、私の確認を待ってください。この段階では定義JSONや描画を作らないでください。']
    lines += ['docs/DIORAMA.mdの形式で図の定義JSONを作り、図の種類（pipeline / columns / board）は説明する内容に合わせて選んでください。']
    if pages:lines += ['python diorama.py <定義JSON> --output <出力先> で描画し、delivery.jsonの検証が通るまで完了扱いにしないでください。',
                       '検証とは別に、静止画と動画の重要なコマを自分で見て、文字の重なり・はみ出し・図の意味を確認してください。']
    lines += ['題材が非公開の情報なら、定義JSONと成果物をGit管理外（private/ または output/）に置いてください。',
              '既存の定義や成果物は上書きしないでください。']
    return '\n'.join(lines)

def prompt(b):
    validate(b)
    if not b.get('topic','').strip():raise ValueError('テーマを入力してください。')
    if b.get('presentationMode')=='diorama':return diorama_prompt(b)
    lines=['次の制作条件で解説動画を作りたいです。','']
    target=b.get('targetMinutes',0)
    lines.append(f'目標時間：{target:g}分（完成尺の目安）' if target else '目標時間：未指定。内容に応じて提案してください。')
    for k,label in FIELDS.items():
        if b.get(k,'').strip():
            value=b[k].strip()
            if k=='presentationMode':value=MODES.get(value,value)
            if k=='boardStyle':value={'none':'使わない','auto':'AIが内容に合わせて図解・アニメーションを設計','flow':'流れ・手順','comparison':'比較','relation':'関係'}.get(value,value)
            lines += ['',f'【{label}】',value]
    if b.get('boardStyle')!='none':
        lines += ['','黒板の内容・配置・動きはAIが台本から設計してください。私による項目ごとの指定は不要です。',
                  'docs/BOARD_ANIMATION.mdに沿って、分類・移動・圧縮・状態変化など、説明対象が理解できるアニメーションを作ってください。',
                  '短い場面プレビューで確認できるようにし、模式図と実測値を区別してください。']
    lines += ['','【進め方】']
    video=b.get('deliverable','video')=='video'
    lines += ['最終成果物：音声付き本編MP4と台本JSON。' if video else '最終成果物：台本JSON（動画生成なし）。']
    if b.get('outlineFirst',False):
        lines += ['まず章立て・各章の時間配分・扱う要点を提案し、私の確認を待ってください。この段階では台本や動画は生成しないでください。']
        if video:lines += ['構成の承認後は、台本・音声・本編動画の生成と検証まで進めてください。']
    elif video:lines += ['構成を決めたうえで、台本JSON、音声、音声付き本編MP4まで生成してください。']
    else:lines += ['構成を決めたうえで、台本ノートに読み込める台本JSONまで作成してください。']
    if video:lines += ['本編の映像・音声を全編デコードして検証し、再生できる動画へのリンクと完成尺を渡すまで完了扱いにしないでください。台本、無音プレビュー、生成スクリプトのみでは動画制作の完了にしないでください。']
    lines += ['目標時間には導入・まとめ・問いかけの待ち時間を含め、章の時間配分の合計を確認してください。',
              '尺は説明の量と構成で調整してください。極端な早口や長い無音で合わせないでください。',
              '指定内容と目標時間が両立しにくい場合は、省略・分割の案を示してください。',
              '台本作成時はmetaではなく台本JSONのトップレベルにtargetMinutesを保存し、制作条件もproductionBriefに保持してください。',
              'このプロジェクトの台本表記Skillを使い、リポジトリ題材ならdocs/REPOSITORY_LESSONS.mdに従って出典を残してください。',
              '掛け合い・黒板の指定はdocs/DIALOGUE_BOARD.mdの形式で保存してください。話者ごとの音声・画像、セリフごとの図の表示数・強調を設定し、音声の種類も明記してください。',
              '既存の台本や編集内容は上書きしないでください。']
    return '\n'.join(lines)

def save_draft(b,store=STORE):
    b=validate(b);store.mkdir(parents=True,exist_ok=True)
    tmp=store/'draft.tmp';tmp.write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,store/'draft.json')

def save_snapshot(b,store=STORE):
    """依頼文を作った時点の条件を、ID別のフォルダーに残す。"""
    text=prompt(b);dest=store/uuid.uuid4().hex;dest.mkdir(parents=True)
    (dest/'brief.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf-8');(dest/'prompt.md').write_text(text,encoding='utf-8')
    return text,dest

if __name__=='__main__':
    if sys.argv[1:]!=['save']:sys.exit('使い方: python editor/brief.py save < brief.json')
    try:
        b=json.loads(sys.stdin.read());save_draft(b);text,dest=save_snapshot(b)
    except (ValueError,json.JSONDecodeError) as exc:sys.exit(str(exc))
    print(text+'\n\n制作条件の保存先：'+str(dest))
