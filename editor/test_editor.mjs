import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {JSDOM} from 'jsdom';
const html=await readFile(new URL('./static/index.html',import.meta.url),'utf8');
const js=await readFile(new URL('./static/app.js',import.meta.url),'utf8');
const key=n=>n.toString(16).padStart(32,'0');
async function setup(t){
 const p={format:'kaisetsu-outline-v1',id:key(1),revision:0,meta:{title:'教材',bgm:{path:'music.mp3'},repository:{url:'https://github.com/example/repository',commit:'a'.repeat(40)}},updatedAt:'now',feedback:[],chapters:[
 {id:key(2),title:'導入',scenes:[{id:key(3),data:{heading:'最初',code:'let x = 1',sources:[{path:'src/index.ts',startLine:10,endLine:20,note:'処理の入口'}]},lines:[{id:key(4),text:'型の説明',speech:'かたの説明',custom:42}]}]},
 {id:key(5),title:'応用',scenes:[]}]};
 const dom=new JSDOM(html,{url:'http://127.0.0.1:8765',runScripts:'outside-only'}),w=dom.window;
 t.after(()=>w.close());w.structuredClone=structuredClone;w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
 const state={saved:p,conflict:false,downloads:[],exported:null};
 w.URL.createObjectURL=blob=>{state.downloads.push(blob);return 'blob:test';};w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=function(){};
 const registered={};w.document.modelContext={registerTool:tool=>{registered[tool.name]=tool;}};
 w.fetch=async(url,opts)=>{const body=opts.body?JSON.parse(opts.body):null;let status=200,result;
  if(url==='/api/bootstrap')result={token:'test',projects:[state.saved],library:[]};
  else if(url==='/api/save'){if(state.conflict){status=409;result={error:'競合しました'};}else{state.saved=body.project;state.saved.revision++;result={revision:state.saved.revision,updatedAt:'saved'};}}
  else if(url==='/api/export'){state.exported=body.project;result={directory:'C:/exports/test'};}
  else throw Error(url);
  return {ok:status===200,status,json:async()=>structuredClone(result)};
 };
 await w.eval('(async()=>{'+js+'})()');
 const $=s=>w.document.querySelector(s),click=s=>$(s).click();
 const input=(s,value,event='input')=>{const el=$(s);el.value=value;el.dispatchEvent(new w.Event(event,{bubbles:true}));};
 const current=()=>registered.read_script_outline.execute().project;
 const flush=async()=>{w.document.dispatchEvent(new w.KeyboardEvent('keydown',{key:'s',ctrlKey:true,bubbles:true}));await new Promise(r=>setTimeout(r,20));};
 return {w,$,click,input,current,flush,state,registered};
}
test('wording synchronizes narration, undo/redo restores pronunciation, metadata survives export',async t=>{
 const x=await setup(t);x.input('[data-field="line-text"]','<img src=x onerror=alert(1)>改訂');
 assert.equal(x.current().chapters[0].scenes[0].lines[0].speech,'<img src=x onerror=alert(1)>改訂');
 x.click('#undo');assert.equal(x.$('[data-field="line-speech"]').value,'かたの説明');
 x.click('#redo');assert.equal(x.$('#editor img[onerror]'),null);
 await x.flush();assert.equal(x.state.saved.chapters[0].scenes[0].lines[0].custom,42);
 x.click('#export');await new Promise(r=>setTimeout(r,20));assert.equal(x.state.exported.meta.bgm.path,'music.mp3');assert.match(x.$('#handoff-text').value,/C:\/exports\/test/);
});
test('move, duplicate and feedback preserve stable targets',async t=>{
 const x=await setup(t);x.click(`[data-comment-line="${key(4)}"]`);x.input('#note-text','例を追加');x.click('#add-note');
 x.input('[data-field="scene-chapter"]',key(5),'change');
 assert.equal(x.current().chapters[0].scenes.length,0);assert.equal(x.current().feedback[0].target,key(4));
 x.click('[data-action="duplicate-scene"]');const scenes=x.current().chapters[1].scenes;
 assert.equal(scenes.length,2);assert.notEqual(scenes[0].lines[0].id,scenes[1].lines[0].id);
 x.click('[data-toggle-note]');assert.equal(x.current().feedback[0].status,'done');
 await x.flush();assert.equal(x.state.saved.chapters[1].scenes.length,2);
});
test('conflict retains unsaved text and makes offline backup available',async t=>{
 const x=await setup(t);x.state.conflict=true;x.input('[data-field="line-text"]','消したくない修正');await x.flush();
 assert.equal(x.$('#error').hidden,false);assert.match(x.$('#save-status').textContent,/未保存/);
 x.click('#backup');assert.equal(x.state.downloads.length,1);assert.equal(x.current().chapters[0].scenes[0].lines[0].text,'消したくない修正');
});
test('optional agent feedback uses the same state and rejects missing targets',async t=>{
 const x=await setup(t);await x.registered.add_script_feedback.execute({target:key(4),text:'読み方を確認'});
 assert.equal(x.state.saved.feedback[0].text,'読み方を確認');
 await assert.rejects(x.registered.add_script_feedback.execute({target:'missing',text:'x'}));
});
test('manual delivery is saved and invalid numeric edits are rejected',async t=>{
 const x=await setup(t);x.input('[data-delivery="speed"]','0.9');
 x.input('[data-delivery="expression"]','thinking','change');
 x.input('[data-delivery="pause"]','0.4');
 const line=()=>x.current().chapters[0].scenes[0].lines[0];
 assert.equal(line().direction.source,'manual');assert.equal(line().direction.speed,.9);
 x.input('[data-delivery="speed"]','20');assert.equal(line().direction.speed,.9);
 await x.flush();assert.equal(x.state.saved.chapters[0].scenes[0].lines[0].direction.expression,'thinking');
});

test('sprite preview follows line overrides and scene inheritance',async t=>{
 const x=await setup(t);
 assert.match(x.$('.delivery img').src,/normal-normal.png$/);
 x.input('[data-field="scene-expression"]','happy','change');
 assert.match(x.$('.delivery img').src,/happy-normal.png$/);
 x.input('[data-delivery="pose"]','think','change');
 assert.match(x.$('.delivery img').src,/happy-think.png$/);
 x.input('[data-field="scene-expression"]','surprised','change');
 assert.match(x.$('.delivery img').src,/surprised-think.png$/);
 x.input('[data-delivery="expression"]','thinking','change');
 x.input('[data-field="scene-expression"]','happy','change');
 assert.match(x.$('.delivery img').src,/thinking-think.png$/);
 assert.match(x.$('.settings img').src,/happy-normal.png$/);
});
test('repository references are pinned and a URL produces a ChatGPT request',async t=>{
 const x=await setup(t);const link=x.$('.repository-sources li a');
 assert.equal(link.href,'https://github.com/example/repository/blob/'+'a'.repeat(40)+'/src/index.ts#L10-L20');
 x.input('#repository-url','https://github.com/wzhudev/reverse-linear-sync-engine');x.click('#repository-request');
 assert.match(x.$('#repository-prompt').value,/コミットを固定/);
 assert.equal(x.$('#repository-copy').hidden,false);
 x.input('#repository-url','javascript:alert(1)');x.click('#repository-request');assert.equal(x.$('#error').hidden,false);
});
