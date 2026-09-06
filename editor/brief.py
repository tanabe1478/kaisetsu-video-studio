"""Preproduction instructions shared with ChatGPT by the user."""
import math

FIELDS={'topic':'テーマ','repository':'参考URL・リポジトリ','audience':'想定視聴者・前提知識',
        'structure':'希望する構成','focus':'詳しく扱うこと','avoid':'扱わないこと',
        'style':'口調・説明スタイル','instructions':'その他の事前プロンプト'}

def validate(b):
    if not isinstance(b,dict):raise ValueError('制作条件が不正です。')
    for k in FIELDS:
        if not isinstance(b.get(k,''),str) or len(b.get(k,''))>20000:raise ValueError('各入力は2万文字以内にしてください。')
    n=b.get('targetMinutes',0)
    if isinstance(n,bool) or not isinstance(n,(float,int)) or not math.isfinite(n) or not 0<=n<=120:raise ValueError('目標時間は0〜120分です。')
    if not isinstance(b.get('outlineFirst',True),bool):raise ValueError('構成案確認の指定が不正です。')
    return b

def prompt(b):
    validate(b)
    if not b.get('topic','').strip():raise ValueError('テーマを入力してください。')
    lines=['次の制作条件で解説動画を作りたいです。','']
    target=b.get('targetMinutes',0)
    lines.append(f'目標時間：{target:g}分（完成尺の目安）' if target else '目標時間：未指定。内容に応じて提案してください。')
    for k,label in FIELDS.items():
        if b.get(k,'').strip():lines += ['',f'【{label}】',b[k].strip()]
    lines += ['','【進め方】']
    if b.get('outlineFirst',True):
        lines += ['まず章立て・各章の時間配分・扱う要点を提案し、私の確認を待ってください。この段階では台本や動画は生成しないでください。']
    else:lines += ['構成を決めたうえで、台本ノートに読み込める台本JSONまで作成してください。動画生成は別途依頼します。']
    lines += ['目標時間には導入・まとめ・問いかけの待ち時間を含め、章の時間配分の合計を確認してください。',
              '尺は説明の量と構成で調整してください。極端な早口や長い無音で合わせないでください。',
              '指定内容と目標時間が両立しにくい場合は、省略・分割の案を示してください。',
              '台本作成時はmetaではなく台本JSONのトップレベルにtargetMinutesを保存し、制作条件もproductionBriefに保持してください。',
              'このプロジェクトの台本表記Skillを使い、リポジトリ題材ならdocs/REPOSITORY_LESSONS.mdに従って出典を残してください。',
              '既存の台本や編集内容は上書きしないでください。']
    return '\n'.join(lines)
