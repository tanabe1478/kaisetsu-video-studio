"""Deterministic, editable delivery suggestions. No remote AI calls."""
import math

EXPRESSIONS = ('normal', 'happy', 'surprised', 'thinking')
POSES = ('normal', 'wave', 'point', 'think')

def validate_direction(d):
    if not isinstance(d, dict): raise ValueError('演出はオブジェクトにしてください。')
    for key, low, high in [('speed', .5, 2), ('pause', 0, 10)]:
        if key in d and (isinstance(d[key], bool) or not isinstance(d[key], (int, float)) or not math.isfinite(d[key]) or not low <= d[key] <= high):
            raise ValueError(f'{key}は{low}〜{high}にしてください。')
    if d.get('expression', 'normal') not in EXPRESSIONS or d.get('pose', 'normal') not in POSES:
        raise ValueError('未対応の表情またはポーズです。')
    return d

def effective(segment, scene, speed):
    d=validate_direction(segment.get('direction', {}))
    return {'speed':d.get('speed',speed), 'pause':d.get('pause',0),
            'expression':d.get('expression',scene.get('expression','normal')),
            'pose':d.get('pose',scene.get('pose','normal'))}

def suggest(lines, scene, speed=1):
    """Preserve explicit directions; maintain a pose for at least two lines."""
    previous=(scene.get('expression','normal'),scene.get('pose','normal'));held=2
    for index,line in enumerate(lines):
        existing=line.get('direction')
        if existing and existing.get('source')!='auto':
            d=effective(line,scene,speed);previous=(d['expression'],d['pose']);held=1
            continue
        text=line['text'];last=index==len(lines)-1
        expression,pose='normal','normal';pause=.18;pace=speed;reason='通常の説明'
        if scene.get('code'):
            pace=speed*.96;pose='point';reason='コード説明を少しゆっくり'
        if any(x in text for x in ('予想','考えてほしい','考えてみ','でしょうか','？','小問')):
            expression,pose='thinking','think';pace=speed*.94;reason='問いかけ'
        elif any(x in text for x in ('答えは','こんにちは','ここまでなのだ','できた')):
            expression,pose='happy','wave';reason='挨拶・答え'
        elif any(x in text for x in ('注意','ただし','大切','重要','混同')):
            pose='point';pace=speed*.94;pause=.3;reason='注意点・要点'
        if last:
            # Scene pause remains authoritative; do not double a quiz's thinking time.
            pause=max(0,(2.5 if '小問' in scene.get('heading','') else .6)-scene.get('pause',.6))
            reason+='／場面末尾の間を考慮'
        candidate=(expression,pose)
        if candidate!=previous and held<2:
            expression,pose=previous;held+=1;reason+='／差分を保持'
        elif candidate!=previous:previous=candidate;held=1
        else:held+=1
        line['direction']={'expression':expression,'pose':pose,'speed':round(max(.5,min(2,pace)),2),
                           'pause':round(pause,2),'source':'auto','reason':reason}
