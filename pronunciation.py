"""Explicit per-line readings; never infer a heteronym by global replacement."""
import re
import unicodedata

AMBIGUOUS_WORDS = ('十分', '一日', '人気')

def normalize_kana(value):
    if not isinstance(value,str):raise ValueError('expectedKanaは読みを示す文字列で指定してください。')
    value=unicodedata.normalize('NFKC',value)
    value=''.join(chr(ord(c)+0x60) if 'ぁ'<=c<='ゖ' else c for c in value)
    # VOICEVOX kana includes accent marks, separators and devoicing markers.
    return re.sub(r"[^ァ-ヶー]",'',value)

def validate_reading(segment):
    expected=segment.get('expectedKana')
    spoken=segment.get('speech',segment['text'])
    candidates=[w for w in AMBIGUOUS_WORDS if w in segment['text'] or w in spoken]
    if expected is not None and (not isinstance(expected,str) or not re.fullmatch(r"[ぁ-ゖァ-ヺー\s、。？！?!,./_'’・]+",unicodedata.normalize('NFKC',expected)) or not normalize_kana(expected)):
        raise ValueError('expectedKanaにセリフ全体のカナ読みを指定してください。')
    if candidates and not expected and not segment.get('audio'):
        raise ValueError(f'読みの確認が必要です: {", ".join(candidates)}。文脈に合わせてspeechを補正し、セリフ全体のexpectedKanaを指定してください。')
    return expected

def check_query(segment,query):
    expected=validate_reading(segment)
    if not expected:return None
    actual=''.join(m['text'] for phrase in query.get('accent_phrases',[]) for m in phrase.get('moras',[]))
    if not actual:actual=query.get('kana','')
    if normalize_kana(actual)!=normalize_kana(expected):
        raise ValueError(f'音声合成前の読み照合に失敗: 期待={expected} / 実際={actual}')
    return {'text':segment['text'],'speech':segment.get('speech',segment['text']),
            'expectedKana':expected,'actualKana':actual,'status':'matched'}
