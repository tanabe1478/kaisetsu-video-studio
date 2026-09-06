import copy, io, tempfile, unittest, wave
from pathlib import Path
from unittest.mock import patch
import server
from direction import suggest, effective
import studio

class DirectionTests(unittest.TestCase):
    def test_manual_and_text_preserved_and_auto_repeatable(self):
        lines=[{'text':'こんにちはなのだ。','speech':'こんにちはなのだ。'},
               {'text':'考えてほしいのだ。'}, {'text':'答えは10なのだ。','direction':{'expression':'surprised','source':'manual'}}]
        before=copy.deepcopy(lines);suggest(lines,{'pause':.6},1)
        self.assertEqual(lines[0]['direction']['expression'],lines[1]['direction']['expression'])
        self.assertEqual(lines[2],before[2])
        self.assertEqual([l['text'] for l in lines],[l['text'] for l in before])
        once=copy.deepcopy(lines);suggest(lines,{'pause':.6},1);self.assertEqual(lines,once)
    def test_quiz_does_not_duplicate_existing_thinking_gap(self):
        lines=[{'text':'予想するのだ。'}];suggest(lines,{'heading':'小問','pause':3},1)
        self.assertEqual(lines[0]['direction']['pause'],0)
        self.assertEqual(effective({}, {}, 1.02),{'speed':1.02,'pause':0,'expression':'normal','pose':'normal'})
    def test_synthesis_uses_line_speed_and_moves_caption_after_gap(self):
        class Response:
            def __init__(self,data=None,content=None):self.data=data;self.content=content
            def json(self):return copy.deepcopy(self.data)
            def raise_for_status(self):pass
        stream=io.BytesIO()
        with wave.open(stream,'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b'\x01\x00'*2400)
        speeds=[]
        def fake_api(base,route,**kwargs):
            if route=='/audio_query':return Response({})
            speeds.append(kwargs['json']['speedScale']);return Response(content=stream.getvalue())
        project={'speaker':'ずんだもん','style':'ノーマル','speed':1,'scenes':[{'pause':.3,'narration':[
            {'text':'前','direction':{'speed':.9,'pause':.25,'expression':'happy'}},
            {'text':'後','direction':{'speed':1.1,'pose':'point'}}]}]}
        with tempfile.TemporaryDirectory() as tmp,patch.object(studio,'ROOT',Path(tmp)),patch.object(studio,'api',side_effect=fake_api),patch.object(studio.requests,'get',side_effect=[Response('test'),Response([{'name':'ずんだもん','styles':[{'name':'ノーマル','id':1}]}])]):
            timing,pcm,rate=studio.synthesize(project,'unused',Path(tmp))
        self.assertEqual(speeds,[.9,1.1]);captions=timing[0]['captions']
        self.assertAlmostEqual(captions[1]['start'],.35)
        self.assertEqual(captions[0]['direction']['expression'],'happy')
        self.assertTrue((pcm[0][2400:8400]==0).all())
        self.assertAlmostEqual(timing[0]['end']*studio.FPS,round(timing[0]['end']*studio.FPS))

if __name__=='__main__':unittest.main()
