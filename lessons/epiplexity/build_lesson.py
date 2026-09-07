"""Build the initial authored manuscript. Never run over a user's edited export."""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from presentation import validate_presentation
from studio import caption_lines

READINGS = {
    'From Entropy to Epiplexity': 'フロム、エントロピー、トゥー、エピプレクシティ',
    'Epiplexity': 'エピプレクシティ', 'Prequential': 'プリクエンシャル',
    'Requential': 'リクエンシャル', 'Rule 15': 'ルールじゅうご',
    'Rule 30': 'ルールさんじゅう', 'Rule 54': 'ルールごじゅうよん',
    'S_T': 'エスティー', 'H_T': 'エイチティー', 'MDL': 'エムディーエル',
    'ADO': 'エーディーオー', 'AI': 'エーアイ',
}

def build():
    brief = {
        'topic': 'From Entropy to Epiplexity: Rethinking Information for Computationally Bounded Intelligence',
        'repository': 'https://arxiv.org/html/2601.03220v2',
        'targetMinutes': 20, 'targetLength': 'long', 'presentationMode': 'yukkuri',
        'boardStyle': 'auto', 'outlineFirst': True, 'focus': '定義と実験まで詳しく',
        'audience': 'AIに関心がある技術系視聴者。情報理論とチェスの予備知識は不要。',
        'style': '霊夢が疑問・誤解を提示し、魔理沙が説明。VOICEVOXの代替音声。',
        'instructions': '論文の主張・実験結果・教材独自の例を区別する。v2参照。',
        'status': 'script_ready', 'outlineApproved': True,
    }
    previous = json.loads((ROOT/'lessons/reverse-linear-sync-engine/lesson.json').read_text(encoding='utf-8'))
    p = {'title': 'Epiplexity：AIはデータから何を学ぶ？', 'series': 'PAPER STUDY / arXiv 2601.03220v2',
         'speed': 1.02, 'speaker': 'ずんだもん', 'style': 'ノーマル',
         'targetMinutes': 20, 'targetLength': 'long', 'productionBrief': brief,
         'presentationMode': 'dialogue', 'bgm': previous['bgm'],
         'references': [{'title': brief['topic'], 'url': brief['repository'], 'version': 'v2', 'checkedAt': '2026-09-07'}],
         'characters': [
             {'id': 'reimu', 'name': '霊夢', 'speaker': '四国めたん', 'style': 'ノーマル',
              'art': 'kitsune:reimu', 'color': '#ffc7cc', 'credit': 'きつね（仮）／東方Project二次創作'},
             {'id': 'marisa', 'name': '魔理沙', 'speaker': 'ずんだもん', 'style': 'ノーマル',
              'art': 'kitsune:marisa', 'color': '#ffe08a', 'credit': 'きつね（仮）／東方Project二次創作'}], 'scenes': []}
    chapter = ''
    sections = {'01':'S1', '02':'S2', '03':'S3', '04':'S4', '05':'S5', '06':'S6.SS1', '07':'S6.SS4', '08':'S8'}
    for raw in (HERE/'dialogue.txt').read_text(encoding='utf-8').splitlines():
        if not raw.strip(): continue
        if raw.startswith('# '): chapter = raw[2:]; continue
        if raw.startswith('## '):
            scene = {'chapter': chapter, 'heading': raw[3:], 'expression': 'normal', 'pose': 'normal',
                     'pause': .5, 'sources': [{'url': brief['repository']+'#'+sections[chapter[:2]],
                                             'note': '論文の確認箇所。日常の例・検証案・確認問題は教材独自。'}], 'narration': []}
            p['scenes'].append(scene); continue
        if ' | ' in raw:
            layout, *nodes = raw.split(' | ')
            scene['board'] = {'layout': layout, 'nodes': [dict(zip(('label', 'detail'), n.split(':', 1))) for n in nodes]}
            continue
        match = re.fullmatch(r'([RM])(\d) (.+)', raw)
        if not match: raise ValueError(raw)
        who, focus, text = match.groups(); focus = int(focus)
        speech = text
        for a, b in READINGS.items(): speech = speech.replace(a, b)
        speech = re.sub(r'(?<![A-Za-z])X(?![A-Za-z])', 'エックス', speech)
        speech = re.sub(r'(?<![A-Za-z])T(?![A-Za-z])', 'ティー', speech)
        seen = max([line['boardStep'] for line in scene['narration']] + [focus])
        expression = 'thinking' if who == 'R' else 'normal'
        if 'こんにちは' in text or 'また次' in text: expression = 'happy'
        line = {'character': 'reimu' if who == 'R' else 'marisa', 'text': text, 'speech': speech,
                'boardStep': seen, 'boardFocus': focus,
                'direction': {'expression': expression, 'pose': 'normal', 'speed': p['speed'],
                              'pause': .18, 'source': 'manual', 'reason': '説明対象に合わせた黒板強調・問いかけ'}}
        if len(caption_lines(text)) > 2: raise ValueError('字幕が長すぎます: '+text)
        scene['narration'].append(line)
    validate_presentation(p)
    (HERE/'lesson.json').write_text(json.dumps(p, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    result = ['# Epiplexity：AIはデータから何を学ぶ？', '',
              '目標20分／霊夢・魔理沙の掛け合い／承認済み構成から作成。VOICEVOX代替音声。',
              '元論文： https://arxiv.org/html/2601.03220v2', '',
              '黒板は説明用の独自図解。定量グラフの再描画ではありません。', '']
    last = ''
    for i, s in enumerate(p['scenes'], 1):
        if s['chapter'] != last: result += ['## '+s['chapter'], '']; last = s['chapter']
        result += [f"### {i:02d} {s['heading']}", '', '**黒板**：'+ ' ／ '.join(n['label']+'（'+n['detail']+'）' for n in s['board']['nodes']), '']
        for line in s['narration']:
            result += [('霊夢' if line['character']=='reimu' else '魔理沙')+'：'+line['text'], '']
    (HERE/'TRANSCRIPT.md').write_text('\n'.join(result), encoding='utf-8')
    print(json.dumps({'scenes': len(p['scenes']), 'lines': sum(len(s['narration']) for s in p['scenes']),
                      'characters': sum(len(l['text']) for s in p['scenes'] for l in s['narration'])}))

if __name__ == '__main__': build()
