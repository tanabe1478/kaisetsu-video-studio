import copy, hashlib, io, json, tempfile, unittest, wave
from pathlib import Path
from unittest.mock import patch
from PIL import ImageChops
import server, studio, presentation
from duration import estimate


def fixture():
    return {'title':'検証','speed':1,'presentationMode':'dialogue','characters':[
        {'id':'a','name':'説明役','speaker':'A','style':'ノーマル','art':'avatar','color':'#aaddaa'},
        {'id':'b','name':'質問役','speaker':'B','style':'ノーマル','art':'avatar','color':'#ffeeaa'}],
        'scenes':[{'heading':'流れ','pause':0,'board':{'layout':'flow','nodes':[{'label':'入力'},{'label':'出力'}]},
                   'narration':[{'text':'同じ文章','character':'a','boardStep':1},
                                {'text':'同じ文章','character':'b','boardStep':2,'boardFocus':2}]}]}


class PresentationTests(unittest.TestCase):
    def test_round_trip_preserves_identity_diagram_and_old_documents(self):
        raw=fixture();raw['scenes'][0]['chapter']='検証'
        for line in raw['scenes'][0]['narration']:line['speech']=line['text']
        self.assertEqual(server.script(server.import_script(raw)),raw)
        old={'title':'旧台本','speaker':'ずんだもん','scenes':[{'heading':'題','narration':[{'text':'文'}]}]}
        p=server.import_script(old);result=server.script(p)
        self.assertNotIn('characters',result);self.assertNotIn('board',result['scenes'][0])
        self.assertEqual(presentation.character(result,{})['speaker'],'ずんだもん')

    def test_voice_caches_distinguish_identical_text_by_speaker(self):
        class Response:
            def __init__(self,data=None,content=None):self.data=data;self.content=content
            def json(self):return copy.deepcopy(self.data)
            def raise_for_status(self):pass
        voices=[{'name':'A','styles':[{'name':'ノーマル','id':10}]},{'name':'B','styles':[{'name':'ノーマル','id':20}]}]
        used=[]
        def api(base,route,**kwargs):
            if route=='/audio_query':return Response({})
            style=kwargs['params']['speaker'];used.append(style);buf=io.BytesIO()
            with wave.open(buf,'wb') as f:
                f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b'\1\0'*(2400 if style==10 else 4800))
            return Response(content=buf.getvalue())
        with tempfile.TemporaryDirectory() as tmp,patch.object(studio,'ROOT',Path(tmp)),patch.object(studio,'api',side_effect=api),patch.object(studio.requests,'get',side_effect=[Response('v'),Response(voices)]):
            timings,pcm,rate=studio.synthesize(fixture(),'unused',Path(tmp))
            r=estimate(fixture(),Path(tmp)/'cache',('v',voices))
            self.assertEqual(used,[10,20]);self.assertEqual(len(list((Path(tmp)/'cache').glob('*.wav'))),2)
            self.assertTrue(r['exact']);self.assertEqual(r['seconds'],timings[0]['end'])
            a,b=timings[0]['captions'];self.assertAlmostEqual(b['start'],.1)
            self.assertEqual((a['character'],b['character']),('a','b'));self.assertEqual(b['boardFocus'],2)

    def test_external_wav_needs_no_voicevox_and_uses_actual_length(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(presentation,'ROOT',Path(tmp)),patch.object(studio,'ROOT',Path(tmp)),patch.object(studio.requests,'get',side_effect=AssertionError('network must not be used')):
            assets=Path(tmp)/'assets';assets.mkdir();out=Path(tmp)/'out';out.mkdir()
            with wave.open(str(assets/'voice.wav'),'wb') as f:
                f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b'\1\0'*12000)
            raw=fixture();raw['scenes'][0]['narration']=raw['scenes'][0]['narration'][:1];raw['scenes'][0]['narration'][0]['audio']='assets/voice.wav'
            timing,_,_=studio.synthesize(raw,'unused',out)
            self.assertEqual(timing[0]['end'],.5);self.assertEqual(estimate(raw,Path(tmp)/'cache')['seconds'],.5)

    def test_reveal_and_highlight_change_only_board_region(self):
        raw=fixture();scene=raw['scenes'][0]
        a=presentation.backdrop(raw,scene,line={'boardStep':1})
        b=presentation.backdrop(raw,scene,line={'boardStep':2})
        diff=ImageChops.difference(a,b).getbbox();self.assertIsNotNone(diff)
        self.assertGreaterEqual(diff[0],249);self.assertLessEqual(diff[2],1032)
        c=presentation.backdrop(raw,scene,line={'boardStep':2,'boardFocus':2})
        self.assertIsNotNone(ImageChops.difference(b,c).getbbox())

    def test_rejects_unknown_speakers_and_outside_assets(self):
        raw=fixture();raw['scenes'][0]['narration'][0]['character']='missing'
        with self.assertRaises(ValueError):presentation.validate_presentation(raw)
        with self.assertRaises(ValueError):presentation.local_asset('../outside.png')
        with self.assertRaises(ValueError):presentation.validate_board({'layout':'flow','nodes':[{'label':'x'}]*5})
        raw=fixture();raw['scenes'][0]['narration'][0]['boardStep']=-1
        with self.assertRaises(ValueError):presentation.validate_presentation(raw)


if __name__=='__main__':unittest.main()
