import copy,json,os,re,subprocess,sys,tempfile,unittest
from pathlib import Path
import brief
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import diorama

SAMPLE=json.loads((ROOT/'lessons'/'diorama-sample'/'spec.json').read_text(encoding='utf-8'))

class DioramaSpecTests(unittest.TestCase):
    def test_sample_is_valid(self):
        diorama.validate(copy.deepcopy(SAMPLE))
    def test_tones_match_blender_palette(self):
        source=(ROOT/'diorama_blender.py').read_text(encoding='utf-8')
        block=source[source.index('TONES = {'):source.index('}',source.index('TONES = {'))]
        self.assertEqual(set(re.findall(r"'(\w+)':",block)),diorama.TONES)
    def test_rejects_broken_definitions(self):
        def broken(change):
            spec=copy.deepcopy(SAMPLE);change(spec)
            with self.assertRaises(ValueError):diorama.validate(spec)
        flow=lambda s:s['figures'][0]  # noqa: E731
        broken(lambda s:flow(s)['scenarios'][1].update(stopAt=5))  # 失敗させる工程にerrorがない
        broken(lambda s:flow(s)['scenarios'][0]['effects'].append({'at':4,'record':'queue'}))  # topicにrecordは置けない
        broken(lambda s:flow(s)['scenarios'][0]['effects'].append({'at':6,'tag':'X'}))  # stopAtより後
        broken(lambda s:flow(s)['stations'][0].update(tone='orange'))
        broken(lambda s:s['figures'][1]['columns'][0]['rows'].append({'key':'dup','row':2}))  # 行の重なり
        broken(lambda s:s['figures'][2]['items'].append({'type':'arrow','from':[0],'to':[1,1]}))
        broken(lambda s:s['figures'].append(copy.deepcopy(s['figures'][2])))  # idの重複
        broken(lambda s:s['figures'][0].update(kind='chart'))
    def test_page_escapes_text_and_marks_code(self):
        spec=copy.deepcopy(SAMPLE);spec['figures'][2]['body']=['<script>x</script> と `a<b`']
        report={'figures':[{'id':'flow','kind':'pipeline','video':'flow.mp4','width':1,'height':1},
                           {'id':'events','kind':'columns','width':1,'height':1},{'id':'rule','kind':'board','width':1,'height':1}]}
        page=diorama.page(spec,report)
        self.assertNotIn('<script>x',page);self.assertIn('&lt;script&gt;x',page);self.assertIn('<code>a&lt;b</code>',page)
        for name in ('"flow.mp4"','"flow-poster.webp"','"events.webp"','"rule.webp"'):self.assertIn(name,page)

class DioramaBriefTests(unittest.TestCase):
    def test_diorama_prompt_has_no_voice_or_board_requirements(self):
        p=brief.prompt({'topic':'変更点の説明','presentationMode':'diorama','boardStyle':'auto','targetMinutes':10})
        self.assertIn('python diorama.py',p);self.assertIn('docs/DIORAMA.md',p);self.assertIn('Git管理外',p)
        for word in ('音声付き本編MP4','黒板','目標時間'):self.assertNotIn(word,p)
        self.assertIn('定義JSONのみ',brief.prompt({'topic':'x','presentationMode':'diorama','deliverable':'script'}))
        self.assertIn('私の確認を待って',brief.prompt({'topic':'x','presentationMode':'diorama','outlineFirst':True}))
    def test_character_modes_keep_existing_prompt(self):
        p=brief.prompt({'topic':'x','presentationMode':'solo'})
        self.assertIn('1人解説（ずんだもん）',p);self.assertIn('音声付き本編MP4',p)
        with self.assertRaises(ValueError):brief.validate({'presentationMode':'unknown'})
    def test_interview_save_matches_gui_storage(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=Path(tmp);b={'topic':'x','presentationMode':'diorama','outlineFirst':False}
            brief.save_draft(b,store);text,dest=brief.save_snapshot(b,store)
            self.assertEqual(json.loads((store/'draft.json').read_text(encoding='utf-8')),b)
            self.assertEqual(json.loads((dest/'brief.json').read_text(encoding='utf-8')),b)
            self.assertEqual((dest/'prompt.md').read_text(encoding='utf-8'),text)
    def test_save_command_rejects_invalid_brief(self):
        result=subprocess.run([sys.executable,str(ROOT/'editor'/'brief.py'),'save'],input='{"topic":"x","presentationMode":"bad"}',
                              capture_output=True,text=True,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        self.assertNotEqual(result.returncode,0);self.assertIn('解説形式',result.stderr)

@unittest.skipUnless(os.environ.get('DIORAMA_RENDER_TEST'),'Blenderでの描画は数分かかるため、DIORAMA_RENDER_TEST=1のときだけ実行する')
class DioramaRenderTests(unittest.TestCase):
    def test_draft_render_is_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            delivery=diorama.build(ROOT/'lessons'/'diorama-sample'/'spec.json',tmp,draft=True)
            self.assertEqual(delivery['status'],'verified');self.assertIn('flow.mp4',delivery['files'])

if __name__=='__main__':unittest.main()
