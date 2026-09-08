import unittest
from pronunciation import validate_reading,check_query

class PronunciationTests(unittest.TestCase):
    def test_context_is_explicit_not_a_global_dictionary(self):
        for line,kana in [('その理解で十分','ソノリカイデジュウブン'),('十分待つ','ジュップンマツ'),('一日の始まり','イチニチノハジマリ'),('一日に開催','ツイタチニカイサイ'),('人気がある','ニンキガアル'),('人気がない路地','ヒトケガナイロジ')]:
            s={'text':line,'expectedKana':kana}
            self.assertEqual(check_query(s,{'kana':kana})['status'],'matched')
    def test_unreviewed_and_empty_readings_fail(self):
        for s in [{'text':'十分だ'},{'text':'こんにちは','expectedKana':''}]:
            with self.assertRaises(ValueError):validate_reading(s)
    def test_engine_misreading_and_partial_match_fail(self):
        s={'text':'その理解で十分','speech':'その理解でじゅうぶん','expectedKana':'ソノリカイデジュウブン'}
        for actual in ['ソノリカイデジュップン','ジュウブン','ソノリカイデジュウブンジュップン']:
            with self.assertRaises(ValueError):check_query(s,{'kana':actual})
    def test_moras_are_used_and_accent_marks_do_not_change_reading(self):
        s={'text':'十分','expectedKana':"ジュ'ウブン/"}
        q={'accent_phrases':[{'moras':[{'text':x} for x in ['ジュ','ウ','ブ','ン']]}]}
        self.assertEqual(check_query(s,q)['actualKana'],'ジュウブン')
    def test_existing_plain_lines_and_external_audio_remain_supported(self):
        self.assertIsNone(validate_reading({'text':'こんにちは'}))
        self.assertIsNone(validate_reading({'text':'十分','audio':'assets/user.wav'}))

    def test_cached_audio_cannot_bypass_query_verification(self):
        import copy,io,tempfile,wave
        from pathlib import Path
        from unittest.mock import patch
        import studio
        class Response:
            def __init__(self,data=None,content=None):self.data=data;self.content=content
            def json(self):return copy.deepcopy(self.data)
            def raise_for_status(self):pass
        buf=io.BytesIO()
        with wave.open(buf,'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b'\x01\x00'*2400)
        readings=iter(['ジュウブン','ジュウブン','ジュップン']);calls=[]
        def api(base,route,**kw):
            calls.append(route)
            if route=='/audio_query':return Response({'kana':next(readings)})
            return Response(content=buf.getvalue())
        project={'speaker':'ずんだもん','style':'ノーマル','speed':1,'scenes':[{'pause':0,'narration':[{'text':'十分','speech':'じゅうぶん','expectedKana':'ジュウブン'}]}]}
        get=[Response('test'),Response([{'name':'ずんだもん','styles':[{'name':'ノーマル','id':3}]}])]*3
        with tempfile.TemporaryDirectory() as tmp,patch.object(studio,'ROOT',Path(tmp)),patch.object(studio,'api',side_effect=api),patch.object(studio.requests,'get',side_effect=get):
            for _ in range(2):studio.synthesize(project,'unused',Path(tmp))
            with self.assertRaisesRegex(ValueError,'読み照合'):studio.synthesize(project,'unused',Path(tmp))
            self.assertIn('failed',(Path(tmp)/'pronunciation-report.json').read_text())
        self.assertEqual(calls.count('/audio_query'),3)
        self.assertEqual(calls.count('/synthesis'),1)
