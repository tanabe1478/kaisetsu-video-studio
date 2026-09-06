"""Storage and HTTP regression tests; always use a temporary workspace."""
import copy, json, tempfile, threading, unittest, urllib.request, urllib.error
from pathlib import Path
import server

class EditorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.previous=server.STORE;server.STORE=Path(self.tmp.name)
        self.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        self.worker=threading.Thread(target=self.http.serve_forever,daemon=True);self.worker.start()
        self.base=f'http://127.0.0.1:{self.http.server_port}'
        self.raw={'title':'教材','bgm':{'path':'assets/bgm/test.mp3'},'scenes':[
            {'chapter':'導入','heading':'例','code':'let x = 1','narration':[{'text':'型','speech':'かた','custom':42}]},
            {'chapter':'応用','heading':'次','text':'まとめ'}]}
    def tearDown(self):
        self.http.shutdown();self.http.server_close();self.worker.join()
        server.STORE=self.previous;self.tmp.cleanup()
    def request(self,path,data=None,token=True,origin=None):
        headers={'Content-Type':'application/json'}
        if token:headers['X-Editor-Token']=server.TOKEN
        if origin:headers['Origin']=origin
        req=urllib.request.Request(self.base+path,data=server.encoded(data) if data is not None else None,headers=headers)
        try:r=urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:r=e
        with r:
            body=r.read()
            return r.status,json.loads(body) if 'application/json' in r.headers.get('Content-Type','') else body
    def test_roundtrip_and_feedback_after_move(self):
        p=server.import_script(self.raw)
        first=p['chapters'][0]['scenes'].pop();p['chapters'][1]['scenes'].append(first)
        p['feedback']=[{'id':server.uid(),'target':first['lines'][0]['id'],'text':'具体例を追加','status':'open'}]
        out=server.script(p)
        self.assertEqual(out['bgm'],self.raw['bgm'])
        self.assertEqual(out['scenes'][1]['code'],'let x = 1')
        self.assertEqual(out['scenes'][1]['narration'][0],{'text':'型','speech':'かた','custom':42})
        self.assertIn('応用 / 例',server.feedback_markdown(p))
        imported=server.import_script(p)
        self.assertNotEqual(p['id'],imported['id'])
        self.assertEqual(p['feedback'],imported['feedback'])
    def test_http_save_conflict_and_export(self):
        status,p=self.request('/api/import',{'document':self.raw});self.assertEqual(status,200)
        p['meta']['title']='編集済み'
        self.assertEqual(self.request('/api/save',{'project':p,'revision':0})[0],200)
        self.assertEqual(self.request('/api/save',{'project':p,'revision':0})[0],409)
        stored=json.loads(server.project_path(p['id']).read_text(encoding='utf-8'))
        self.assertEqual(stored['revision'],1)
        status,export=self.request('/api/export',{'project':stored});self.assertEqual(status,200)
        self.assertEqual(json.loads(Path(export['script']).read_text(encoding='utf-8'))['title'],'編集済み')
        self.assertTrue((Path(export['directory'])/'outline.json').exists())
        self.assertEqual(self.raw['title'],'教材')
    def test_api_boundaries(self):
        self.assertEqual(self.request('/api/import',{'document':self.raw},token=False)[0],403)
        self.assertEqual(self.request('/api/import',{'document':self.raw},origin='https://example.com')[0],403)
        self.assertEqual(self.request('/api/import',{'libraryId':'../README.md'})[0],400)
        self.assertEqual(self.request('/../server.py')[0],404)
        self.assertEqual(self.request('/')[0],200)
        p=server.import_script(self.raw);p['id']='../outside'
        self.assertEqual(self.request('/api/save',{'project':p,'revision':0})[0],400)
    def test_real_lesson_preserves_all_render_data(self):
        raw=json.loads((server.ROOT/'lessons/moonbit/lesson.json').read_text(encoding='utf-8'))
        self.assertEqual(server.script(server.import_script(raw)),raw)
    def test_invalid_duplicate_ids_and_nonfinite_values(self):
        for kind in ['duplicate','nan','note']:
            p=server.import_script(self.raw)
            if kind=='duplicate':p['chapters'][1]['id']=p['chapters'][0]['id']
            elif kind=='nan':p['meta']['speed']=float('nan')
            else:p['feedback']=[{'id':'bad','target':'project','text':'x','status':'open'}]
            with self.assertRaises(ValueError):server.validate(p)
    def test_bootstrap_ignores_auxiliary_json_without_losing_projects(self):
        p=server.import_script(self.raw);server.write(p)
        (server.STORE/'preview-check.json').write_text('{"status":"done"}',encoding='utf-8')
        (server.STORE/'unrelated.json').write_text('not json',encoding='utf-8')
        status,boot=self.request('/api/bootstrap')
        self.assertEqual(status,200)
        self.assertEqual([x['id'] for x in boot['projects']],[p['id']])
        self.assertTrue((server.STORE/'preview-check.json').exists())
    def test_direction_api_is_a_proposal_and_keeps_manual_settings(self):
        status,p=self.request('/api/import',{'document':self.raw})
        line=p['chapters'][0]['scenes'][0]['lines'][0]
        line['direction']={'speed':.87,'source':'manual'}
        status,result=self.request('/api/direction',{'project':p})
        self.assertEqual(status,200)
        self.assertEqual(result['chapters'][0]['scenes'][0]['lines'][0],line)
        self.assertEqual(result['chapters'][1]['scenes'][0]['lines'][0]['direction']['source'],'auto')
        stored=json.loads(server.project_path(p['id']).read_text(encoding='utf-8'))
        self.assertNotIn('direction',stored['chapters'][1]['scenes'][0]['lines'][0])
    def test_brief_is_persisted_separately_and_exported(self):
        b={'topic':'同期の解説','targetMinutes':10,'outlineFirst':True,'structure':'導入→例→まとめ'}
        self.assertEqual(self.request('/api/brief',{'brief':b})[0],200)
        self.assertEqual(self.request('/api/brief')[1],b)
        status,result=self.request('/api/brief/export',{'brief':b});self.assertEqual(status,200)
        self.assertTrue((Path(result['directory'])/'brief.json').is_file())
        self.assertIn('10分',result['prompt'])
        self.assertEqual(self.request('/api/bootstrap')[1]['projects'],[])

if __name__=='__main__':unittest.main()
