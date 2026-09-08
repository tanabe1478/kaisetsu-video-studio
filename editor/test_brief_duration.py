import hashlib,json,tempfile,unittest,wave
from pathlib import Path
import brief
from duration import estimate

class BriefDurationTests(unittest.TestCase):
    def test_brief_preserves_conditions_and_plan_gate(self):
        b={'topic':'同期処理','targetMinutes':5,'structure':'導入1分、具体例3分、まとめ1分','avoid':'API一覧','outlineFirst':True}
        p=brief.prompt(b)
        self.assertIn('目標時間：5分',p);self.assertIn(b['structure'],p);self.assertIn('確認を待って',p)
        b['outlineFirst']=False;self.assertNotIn('確認を待って',brief.prompt(b))
        self.assertIn('音声付き本編MP4まで',brief.prompt(b))
        self.assertNotIn('動画生成は別途',brief.prompt(b))
        b['deliverable']='script'
        self.assertIn('台本JSONまで',brief.prompt(b))
        self.assertNotIn('MP4まで生成',brief.prompt(b))
    def test_default_finishes_with_video_and_explicit_outline_still_waits(self):
        p=brief.prompt({'topic':'検証'})
        self.assertIn('全編デコード',p);self.assertNotIn('確認を待って',p)
        p=brief.prompt({'topic':'検証','outlineFirst':True})
        self.assertIn('確認を待って',p);self.assertIn('構成の承認後',p)
        with self.assertRaises(ValueError):brief.validate({'deliverable':'unknown'})
    def test_invalid_conditions(self):
        for value in [-1,121,float('nan'),True,'5']:
            with self.assertRaises(ValueError):brief.validate({'targetMinutes':value})
        with self.assertRaises(ValueError):brief.prompt({'topic':''})
    def test_cached_duration_matches_frame_alignment_and_gaps(self):
        text='例';engine=('v1',[{'name':'ずんだもん','styles':[{'name':'ノーマル','id':3}]}])
        with tempfile.TemporaryDirectory() as tmp:
            key=hashlib.sha256(json.dumps([text,3,1,'v1'],ensure_ascii=False).encode()).hexdigest()
            with wave.open(str(Path(tmp)/(key+'.wav')),'wb') as f:
                f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b'\0\0'*24000)
            p={'scenes':[{'pause':.5,'narration':[{'text':text,'direction':{'pause':.25}}]}],'targetMinutes':1}
            r=estimate(p,tmp,engine)
            self.assertEqual(r['seconds'],1.75);self.assertTrue(r['exact']);self.assertEqual(r['cachedLines'],1)
            self.assertEqual(r['lowerSeconds'],r['upperSeconds'])
    def test_missing_cache_has_uncertainty_and_respects_speed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p={'scenes':[{'pause':0,'narration':[{'text':'説明'*50}]}]}
            slow=estimate(p,tmp);p['speed']=2;fast=estimate(p,tmp)
            self.assertGreater(slow['seconds'],fast['seconds']);self.assertFalse(fast['exact'])
            self.assertGreater(fast['upperSeconds'],fast['lowerSeconds'])

if __name__=='__main__':unittest.main()
