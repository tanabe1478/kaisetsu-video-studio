"""Preproduction instructions shared with ChatGPT by the user."""
import math

FIELDS={'topic':'テーマ','repository':'参考URL・リポジトリ','audience':'想定視聴者・前提知識',
        'structure':'希望する構成','focus':'詳しく扱うこと','avoid':'扱わないこと',
        'style':'口調・説明スタイル','instructions':'その他の事前プロンプト',
        'presentationMode':'解説形式','boardStyle':'黒板の図解'}

def validate(b):
    if not isinstance(b,dict):raise ValueError('制作条件が不正です。')
    for k in FIELDS:
        if not isinstance(b.get(k,''),str) or len(b.get(k,''))>20000:raise ValueError('各入力は2万文字以内にしてください。')
    n=b.get('targetMinutes',0)
    if isinstance(n,bool) or not isinstance(n,(float,int)) or not math.isfinite(n) or not 0<=n<=120:raise ValueError('目標時間は0〜120分です。')
    if not isinstance(b.get('outlineFirst',False),bool):raise ValueError('構成案確認の指定が不正です。')
    if b.get('deliverable','video') not in ('video','script'):raise ValueError('成果物は動画または台本を選んでください。')
    return b

def prompt(b):
    validate(b)
    if not b.get('topic','').strip():raise ValueError('テーマを入力してください。')
    lines=['次の制作条件で解説動画を作りたいです。','']
    target=b.get('targetMinutes',0)
    lines.append(f'目標時間：{target:g}分（完成尺の目安）' if target else '目標時間：未指定。内容に応じて提案してください。')
    for k,label in FIELDS.items():
        if b.get(k,'').strip():
            value=b[k].strip()
            if k=='presentationMode':value={'solo':'1人解説（ずんだもん）','dialogue':'2人の掛け合い','yukkuri':'霊夢・魔理沙の掛け合い'}.get(value,value)
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
