const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const id=()=>crypto.randomUUID().replaceAll('-','');
const clone=x=>structuredClone(x);
let token='',projects=[],library=[],p=null,selected={type:'project',id:'project'},collapsed=new Set(),filter='open',search='',drag=null;
let past=[],future=[],editKey='',editTime=0,generation=0,savedGeneration=0,timer=null,saving=null,conflict=false;
function error(e){$('#error').textContent=e.message||String(e);$('#error').hidden=false;}
function clearError(){$('#error').hidden=true;}
function toast(text){$('#toast').textContent=text;$('#toast').hidden=false;setTimeout(()=>$('#toast').hidden=true,3500);}
async function api(url,data,retry=true){const r=await fetch(url,{method:data?'POST':'GET',headers:data?{'Content-Type':'application/json','X-Editor-Token':token}:{},body:data?JSON.stringify(data):undefined});const result=await r.json();if(r.status===403&&data&&retry){const boot=await api('/api/bootstrap');token=boot.token;return api(url,data,false);}if(!r.ok){if(r.status===409&&url==='/api/save')conflict=true;throw new Error(result.error||'保存できませんでした。');}return result;}
function status(text){$('#save-status').textContent=text;}
function checkpoint(key=''){const now=Date.now();if(!key||key!==editKey||now-editTime>1000){past.push(clone(p));if(past.length>80)past.shift();future=[];}editKey=key;editTime=now;}
function changed(){generation++;status('保存待ち…');clearTimeout(timer);timer=setTimeout(()=>save().catch(error),650);renderTree();renderStats();updateUndo();}
function mutate(fn,key=''){if(!p)return;checkpoint(key);fn();changed();}
async function save(){
 if(!p||generation===savedGeneration)return;
 if(conflict)throw new Error('別の画面との更新競合があります。メモ付きバックアップを保存して再読み込みしてください。');
 if(saving){await saving;if(generation!==savedGeneration)return save();return;}
 const snapshot=clone(p),ticket=generation;status('保存中…');
 saving=api('/api/save',{project:snapshot,revision:p.revision}).then(r=>{p.revision=r.revision;p.updatedAt=r.updatedAt;savedGeneration=ticket;projects=projects.map(x=>x.id===p.id?clone(p):x);status('自動保存済み');}).catch(e=>{status('未保存・バックアップ可能');throw e;}).finally(()=>saving=null);
 await saving;if(generation!==savedGeneration)return save();
}
function updateUndo(){$('#undo').disabled=!past.length;$('#redo').disabled=!future.length;}
function restore(from,to){if(!from.length||!p)return;to.push(clone(p));const revision=p.revision;p=from.pop();p.revision=revision;editKey='';ensureSelection();changed();renderAll();}
function allScenes(){return p?p.chapters.flatMap(c=>c.scenes):[];}
function locate(sceneId){for(const c of p.chapters){const s=c.scenes.find(x=>x.id===sceneId);if(s)return {c,s};}return null;}
function current(){return selected.type==='scene'?locate(selected.id):null;}
function ensureSelection(){if(selected.type==='scene'&&!locate(selected.id)||selected.type==='chapter'&&!p.chapters.some(c=>c.id===selected.id))selected={type:'project',id:'project'};}
function activate(project){clearTimeout(timer);$('#note-text').value='';p=clone(project);past=[];future=[];generation=0;savedGeneration=0;conflict=false;editKey='';collapsed=new Set();selected=allScenes().length?{type:'scene',id:allScenes()[0].id}:{type:'project',id:'project'};clearError();status('自動保存済み');renderAll();}
function select(type,itemId){selected={type,id:itemId};editKey='';renderAll();}
function renderStats(){const n=allScenes().reduce((a,s)=>a+s.lines.reduce((b,l)=>b+l.text.length,0),0);$('#stats').textContent=p?`${p.chapters.length}章 / ${allScenes().length}場面 / ${n.toLocaleString()}文字`:'章・場面を並べて考える';}
function hasNote(itemId){return p.feedback.some(n=>n.target===itemId&&n.status==='open');}
function renderTree(){
 if(!p){$('#tree').innerHTML='';return;}
 let number=0;
 $('#tree').innerHTML=p.chapters.map(c=>{
  const scenes=c.scenes.map(s=>({s,n:++number})).filter(({s})=>!search||[c.title,s.data.heading,...s.lines.map(l=>l.text)].some(t=>String(t).toLowerCase().includes(search)));
  if(search&&!scenes.length&&!c.title.toLowerCase().includes(search))return '';
  return `<div class="chapter-row ${selected.id===c.id?'selected':''}" data-drop-chapter="${c.id}" draggable="true" data-drag-chapter="${c.id}"><button data-collapse="${c.id}" aria-label="${collapsed.has(c.id)?'章を展開':'章を折りたたむ'}" aria-expanded="${!collapsed.has(c.id)}">${collapsed.has(c.id)?'▸':'▾'}</button><button class="chapter-title" data-select-chapter="${c.id}">${esc(c.title||'無題の章')}</button>${hasNote(c.id)?'<span class="note-dot">●</span>':''}<span class="chapter-count">${c.scenes.length}</span></div>`+
   (!collapsed.has(c.id)||search?scenes.map(({s,n})=>`<button class="scene-link ${selected.id===s.id?'selected':''}" data-select-scene="${s.id}" data-drop-scene="${s.id}" draggable="true" data-drag-scene="${s.id}" ${selected.id===s.id?'aria-current="true"':''}><span class="number">${String(n).padStart(2,'0')}</span><span class="scene-name">${esc(s.data.heading||'無題の場面')}</span>${hasNote(s.id)||s.lines.some(l=>hasNote(l.id))?'<span class="note-dot">●</span>':''}</button>`).join(''):'');
 }).join('')+`<button class="project-settings-link" data-select-project>⚙ 台本全体の設定</button>`;
}
function options(values,currentValue){return values.map(([v,t])=>`<option value="${esc(v)}" ${v===currentValue?'selected':''}>${esc(t)}</option>`).join('');}
function renderEditor(){
 $('#empty').hidden=!!p;$('#editor').hidden=!p;if(!p)return;
 if(selected.type==='project'){
  $('#editor').innerHTML=`<div class="eyebrow">DOCUMENT</div><h2>台本全体の設定</h2><div class="project-fields"><label>タイトル<input data-field="project-title" value="${esc(p.meta.title)}"></label><label>シリーズ表記<input data-field="project-series" value="${esc(p.meta.series||'')}"></label><div class="settings-grid"><label>話者<input data-field="project-speaker" value="${esc(p.meta.speaker||'ずんだもん')}"></label><label>スタイル<input data-field="project-style" value="${esc(p.meta.style||'ノーマル')}"></label><label>話速<input type="number" min="0.5" max="2" step="0.01" data-field="project-speed" value="${p.meta.speed||1}"></label></div></div><p class="hint">BGMなど、元の台本のその他の設定も書き出し時に保持します。</p><div class="section-label"><h3>章の一覧</h3><button data-action="auto-all">全編の演出を自動提案</button><button data-action="add-chapter">＋ 章を追加</button></div>${p.chapters.map((c,i)=>`<div class="chapter-card"><span class="index">${i+1}</span><div class="card-title" data-select-chapter="${c.id}">${esc(c.title)}<small>${c.scenes.length}場面</small></div><button data-chapter-up="${c.id}" aria-label="章を上へ" ${i===0?'disabled':''}>↑</button><button data-chapter-down="${c.id}" aria-label="章を下へ" ${i===p.chapters.length-1?'disabled':''}>↓</button></div>`).join('')}`;return;
 }
 if(selected.type==='chapter'){
  const c=p.chapters.find(x=>x.id===selected.id),index=p.chapters.indexOf(c);
  $('#editor').innerHTML=`<div class="page-top"><span class="breadcrumb">${esc(p.meta.title)} / 章の編集</span><div class="actions"><button data-chapter-up="${c.id}" ${index===0?'disabled':''}>↑ 上へ</button><button data-chapter-down="${c.id}" ${index===p.chapters.length-1?'disabled':''}>↓ 下へ</button><button data-action="delete-chapter" class="danger">章を削除</button></div></div><label class="sr-only" for="chapter-title">章名</label><input id="chapter-title" class="title-input" data-field="chapter-title" value="${esc(c.title)}"><div class="scene-meta"><span class="pill">CHAPTER ${index+1}</span><span>${c.scenes.length}場面</span></div><div class="section-label"><h3>この章の場面</h3><button data-action="add-scene">＋ 場面を追加</button></div>${c.scenes.map((s,i)=>`<div class="chapter-card"><span class="index">${i+1}</span><div class="card-title" data-select-scene="${s.id}">${esc(s.data.heading||'無題の場面')}<small>${s.lines.length}セリフ</small></div><button data-scene-up="${s.id}" ${i===0?'disabled':''}>↑</button><button data-scene-down="${s.id}" ${i===c.scenes.length-1?'disabled':''}>↓</button></div>`).join('')||'<p class="hint">まだ場面がありません。場面を追加してセリフを書き始めましょう。</p>'}<p class="hint">左の構成ツリーでは、ドラッグして場面を別の章へ移動できます。</p>`;return;
 }
 const {c,s}=current(),index=allScenes().findIndex(x=>x.id===s.id);
 $('#editor').innerHTML=`<div class="page-top"><span class="breadcrumb">${esc(c.title)} / 場面 ${String(index+1).padStart(2,'0')}</span><div class="actions"><button data-action="auto-scene">演出を自動提案</button><button data-action="preview-scene">▶ 場面プレビュー</button><button data-action="duplicate-scene">複製</button><button data-action="delete-scene" class="danger">削除</button></div></div><label class="sr-only" for="scene-title">場面の見出し</label><input id="scene-title" class="title-input" data-field="scene-heading" value="${esc(s.data.heading||'')}"><div class="scene-meta"><span class="pill">SCENE ${String(index+1).padStart(2,'0')}</span><span>${s.lines.length}セリフ</span><select class="move-chapter" data-field="scene-chapter" aria-label="場面の所属章">${p.chapters.map(ch=>`<option value="${ch.id}" ${ch.id===c.id?'selected':''}>${esc(ch.title)}</option>`).join('')}</select><button data-scene-up="${s.id}" title="章内で上へ移動">↑</button><button data-scene-down="${s.id}" title="章内で下へ移動">↓</button></div><div class="section-label"><h3>セリフ</h3><small>一つずつ言葉を整える</small></div>${s.lines.map((line,i)=>`<article class="line-card" data-line="${line.id}"><div class="line-header"><span>${String(i+1).padStart(2,'0')}</span><span class="speaker">${esc(p.meta.speaker||'ずんだもん')}</span><button data-comment-line="${line.id}" title="このセリフにメモ">メモ ${hasNote(line.id)?'●':'＋'}</button><button data-line-up="${line.id}" aria-label="セリフを上へ" ${i===0?'disabled':''}>↑</button><button data-line-down="${line.id}" aria-label="セリフを下へ" ${i===s.lines.length-1?'disabled':''}>↓</button><button data-delete-line="${line.id}" aria-label="セリフを削除">×</button></div><textarea class="caption" rows="3" data-field="line-text" data-line-id="${line.id}" aria-label="セリフ${i+1}">${esc(line.text)}</textarea><details class="reading"><summary>読み上げの表記を調整 ${line.speech!==line.text?'· 指定あり':''}</summary><textarea rows="2" data-field="line-speech" data-line-id="${line.id}" aria-label="セリフ${i+1}の読み上げ表記">${esc(line.speech)}</textarea><p>字幕を変更すると読み上げも同じ文に更新します。固有名詞の読みはここで調整できます。</p></details>${deliveryControls(line,s)}</article>`).join('')}<button class="add-line" data-action="add-line">＋ セリフを追加</button><details class="settings"><summary>画面に表示する内容・演出</summary>${spritePreview(s.data.expression,s.data.pose)}<div class="settings-grid"><label>表情<select data-field="scene-expression">${options([['normal','ふつう'],['happy','笑顔'],['surprised','驚き'],['thinking','考える']],s.data.expression||'normal')}</select></label><label>ポーズ<select data-field="scene-pose">${options([['normal','ふつう'],['wave','手を振る'],['point','指差し'],['think','考える']],s.data.pose||'normal')}</select></label><label>場面のあとの間（秒）<input type="number" min="0" max="30" step="0.1" data-field="scene-pause" value="${s.data.pause??.6}"></label><label class="wide">画面の箇条書き（1行に1項目）<textarea rows="3" data-field="scene-points">${esc((s.data.points||[]).join('\n'))}</textarea></label><label class="wide">画面のコード例<textarea rows="6" class="code" data-field="scene-code">${esc(s.data.code||'')}</textarea></label></div><p class="hint">動画ではコード例があれば箇条書きより優先されます。表示枠の目安：箇条書き3点、コード10行まで。</p></details>`;
}
function targetMap(){const m=new Map([['project','台本全体']]);if(!p)return m;for(const c of p.chapters){m.set(c.id,'章：'+c.title);for(const s of c.scenes){m.set(s.id,'場面：'+(s.data.heading||'無題'));for(const [i,l] of s.lines.entries())m.set(l.id,`セリフ${i+1}：${l.text.slice(0,28)}${l.text.length>28?'…':''}`);}}return m;}
function renderNotes(){
 const m=targetMap(),defaultTarget=selected.type==='project'?'project':selected.id;
 const local=[['project','台本全体']];if(p){const hit=current();const chapter=hit?.c||(selected.type==='chapter'?p.chapters.find(c=>c.id===selected.id):null);if(chapter)local.push([chapter.id,m.get(chapter.id)]);if(hit){local.push([hit.s.id,m.get(hit.s.id)]);hit.s.lines.forEach(l=>local.push([l.id,m.get(l.id)]));}}
 $('#note-target').innerHTML=options(local,defaultTarget);$('#note-count').textContent=p?p.feedback.filter(n=>n.status==='open').length:0;
 $('#add-note').disabled=!p;
 if(!p){$('#notes').innerHTML='<p class="note-empty">台本を開くとメモを残せます。</p>';return;}
 const notes=p.feedback.filter(n=>filter==='all'||n.status===filter);
 $('#notes').innerHTML=notes.map(n=>`<article class="note-card ${n.status==='done'?'done':''}"><div class="target-label">${esc(m.get(n.target)||'削除された項目へのメモ')}</div><p>${esc(n.text)}</p><footer><button data-toggle-note="${n.id}">${n.status==='open'?'✓ 対応済みにする':'未対応に戻す'}</button><button data-jump-note="${n.target}" ${m.has(n.target)?'':'disabled'}>対象へ</button><button data-delete-note="${n.id}" aria-label="メモを削除">×</button></footer></article>`).join('')||'<p class="note-empty">メモはまだありません。<br>気になるところから残しましょう。</p>';
}
function renderAll(){renderTree();renderStats();renderEditor();renderNotes();updateUndo();$('#export').disabled=!p;$('#backup').disabled=!p;$('#project-select').innerHTML=projects.length?projects.map(x=>`<option value="${x.id}" ${p?.id===x.id?'selected':''}>${esc(x.id===p?.id?p.meta.title:x.meta.title)||'無題の台本'}</option>`).join(''):'<option>台本を開く</option>';}
function newLine(){return {id:id(),text:'',speech:''};}
function addChapter(){mutate(()=>{const c={id:id(),title:'新しい章',scenes:[]};p.chapters.push(c);selected={type:'chapter',id:c.id};});renderAll();$('#chapter-title')?.focus();}
function addScene(){mutate(()=>{let c=current()?.c||p.chapters.find(x=>x.id===selected.id)||p.chapters.at(-1);if(!c){c={id:id(),title:'新しい章',scenes:[]};p.chapters.push(c);}const s={id:id(),data:{heading:'新しい場面',expression:'normal',pose:'normal',pause:.6},lines:[newLine()]};c.scenes.push(s);collapsed.delete(c.id);selected={type:'scene',id:s.id};});renderAll();$('#scene-title')?.focus();}
function moveScene(sceneId,delta){const hit=locate(sceneId);if(!hit)return;const i=hit.c.scenes.indexOf(hit.s),j=i+delta;if(j<0||j>=hit.c.scenes.length)return;mutate(()=>{[hit.c.scenes[i],hit.c.scenes[j]]=[hit.c.scenes[j],hit.c.scenes[i]];});renderAll();}
function moveChapter(chapterId,delta){const i=p.chapters.findIndex(c=>c.id===chapterId),j=i+delta;if(i<0||j<0||j>=p.chapters.length)return;mutate(()=>{[p.chapters[i],p.chapters[j]]=[p.chapters[j],p.chapters[i]];});renderAll();}
function toScript(){return {...clone(p.meta),scenes:p.chapters.flatMap(c=>c.scenes.map(s=>({...clone(s.data),chapter:c.title,narration:s.lines.map(({id,...line})=>clone(line))})))};}
function download(data,name){const a=document.createElement('a');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function imported(data){await save();const result=await api('/api/import',data);projects.unshift(result);activate(result);$('#library-dialog').close();toast('編集用コピーを作成しました');}
function openLibrary(){$('#library-list').innerHTML=library.map(x=>`<button data-library="${esc(x.id)}">${esc(x.title)}<small>${esc(x.id)} → 編集用コピー</small></button>`).join('');$('#library-dialog').showModal();}
$('#open-library').onclick=openLibrary;$('#empty-open').onclick=openLibrary;
$('#undo').onclick=()=>restore(past,future);$('#redo').onclick=()=>restore(future,past);
$('#add-chapter').onclick=()=>p?addChapter():openLibrary();$('#add-scene').onclick=()=>p?addScene():openLibrary();
$('#search').oninput=e=>{search=e.target.value.toLowerCase();renderTree();};
$('#project-select').onchange=async e=>{try{await save();activate(projects.find(x=>x.id===e.target.value));}catch(err){error(err);renderAll();}};
$('#file').onchange=async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>5_000_000)throw new Error('5MB以下のJSONを選んでください。');await imported({document:JSON.parse(await file.text()),name:file.name});}catch(err){error(err);}finally{e.target.value='';}};
$('#new-project').onclick=()=>imported({document:{title:'新しい台本',speaker:'ずんだもん',style:'ノーマル',speed:1,scenes:[]},name:'白紙'}).catch(error);
$('#add-note').onclick=()=>{const text=$('#note-text').value.trim();if(!p||!text){$('#note-text').focus();return;}mutate(()=>p.feedback.push({id:id(),target:$('#note-target').value,text,status:'open'}));$('#note-text').value='';renderNotes();toast('編集メモを追加しました');};
$('#export').onclick=async()=>{try{clearError();await save();const result=await api('/api/export',{project:p});$('#handoff-text').value=`次のフォルダーに、編集済みの台本とフィードバックがあります。\n${result.directory}\n\nscript.jsonとfeedback.mdを読み、私が変更した文言・構成を尊重して、未対応のフィードバックを反映した改訂案を作ってください。元ファイルは残してください。`;$('#export-dialog').showModal();}catch(e){error(e);}};
$('#copy-handoff').onclick=async()=>{try{await navigator.clipboard.writeText($('#handoff-text').value);toast('依頼文をコピーしました');}catch{$('#handoff-text').select();toast('文章を選択しました。Ctrl+Cでコピーできます');}};
$('#backup').onclick=()=>download(p,'outline-backup.json');
$('#download-script').onclick=()=>download(toScript(),'script.json');$('#download-backup').onclick=()=>download(p,'outline-backup.json');
document.addEventListener('click',e=>{
 const b=e.target.closest('button,[data-select-chapter],[data-select-scene]');if(!b)return;
 const d=b.dataset;
 if(d.close){$('#'+d.close).close();return;}
 if(d.library){imported({libraryId:d.library}).catch(error);return;}
 if(!p)return;
 if(d.selectChapter){select('chapter',d.selectChapter);return;}
 if(d.selectScene){select('scene',d.selectScene);return;}
 if('selectProject'in d){select('project','project');return;}
 if(d.collapse){collapsed.has(d.collapse)?collapsed.delete(d.collapse):collapsed.add(d.collapse);renderTree();return;}
 if(d.filter){filter=d.filter;document.querySelectorAll('.note-filters button').forEach(b=>b.classList.toggle('active',b.dataset.filter===filter));renderNotes();return;}
 if(d.chapterUp||d.chapterDown){moveChapter(d.chapterUp||d.chapterDown,d.chapterUp?-1:1);return;}
 if(d.sceneUp||d.sceneDown){moveScene(d.sceneUp||d.sceneDown,d.sceneUp?-1:1);return;}
 if(d.commentLine){$('#note-target').value=d.commentLine;$('#note-text').focus();return;}
 if(d.lineUp||d.lineDown){const s=current().s,i=s.lines.findIndex(l=>l.id===(d.lineUp||d.lineDown)),j=i+(d.lineUp?-1:1);if(j>=0&&j<s.lines.length){mutate(()=>[s.lines[i],s.lines[j]]=[s.lines[j],s.lines[i]]);renderAll();}return;}
 if(d.deleteLine){mutate(()=>{const s=current().s;s.lines=s.lines.filter(l=>l.id!==d.deleteLine);});renderAll();toast('セリフを削除しました。「戻す」で復元できます');return;}
 if(d.toggleNote){mutate(()=>{const n=p.feedback.find(n=>n.id===d.toggleNote);n.status=n.status==='open'?'done':'open';});renderNotes();return;}
 if(d.deleteNote){mutate(()=>p.feedback=p.feedback.filter(n=>n.id!==d.deleteNote));renderNotes();return;}
 if(d.jumpNote){if(d.jumpNote==='project')select('project','project');else if(p.chapters.some(c=>c.id===d.jumpNote))select('chapter',d.jumpNote);else{const s=allScenes().find(s=>s.id===d.jumpNote||s.lines.some(l=>l.id===d.jumpNote));if(s){select('scene',s.id);document.querySelector(`[data-line="${d.jumpNote}"]`)?.scrollIntoView({behavior:'smooth',block:'center'});}}return;}
 switch(d.action){
 case 'auto-scene':autoDirection(selected.id).catch(error);break;
 case 'auto-all':autoDirection().catch(error);break;
 case 'preview-scene':previewScene().catch(error);break;
 case 'add-chapter':addChapter();break;
 case 'add-scene':addScene();break;
 case 'add-line':mutate(()=>current().s.lines.push(newLine()));renderAll();document.querySelector('.line-card:last-of-type textarea.caption')?.focus();break;
 case 'delete-scene':{const {c,s}=current();mutate(()=>{c.scenes=c.scenes.filter(x=>x.id!==s.id);selected={type:'chapter',id:c.id};});renderAll();toast('場面を削除しました。「戻す」で復元できます');break;}
 case 'duplicate-scene':{const {c,s}=current();mutate(()=>{const copy=clone(s);copy.id=id();copy.data.heading=(copy.data.heading||'場面')+'（コピー）';copy.lines.forEach(l=>l.id=id());c.scenes.splice(c.scenes.indexOf(s)+1,0,copy);selected={type:'scene',id:copy.id};});renderAll();break;}
 case 'delete-chapter':mutate(()=>{p.chapters=p.chapters.filter(c=>c.id!==selected.id);selected={type:'project',id:'project'};});renderAll();toast('章を削除しました。「戻す」で復元できます');break;
 }
});
document.addEventListener('input',e=>{
 if(e.target.dataset.delivery&&e.target.tagName!=='SELECT'){editDelivery(e.target);return;}
 const field=e.target.dataset.field;if(!field||!p||e.target.tagName==='SELECT')return;
 const value=e.target.value,key=field+':'+(e.target.dataset.lineId||selected.id);
 if(e.target.type==='number'&&(value===''||!Number.isFinite(Number(value))))return;
 mutate(()=>{
  if(field.startsWith('project-')){const k=field.slice(8);p.meta[k]=k==='speed'?Number(value):value;return;}
  if(field==='chapter-title'){p.chapters.find(c=>c.id===selected.id).title=value;return;}
  const s=current()?.s;if(!s)return;
  if(field==='line-text'||field==='line-speech'){const l=s.lines.find(l=>l.id===e.target.dataset.lineId);if(field==='line-text'){l.text=value;l.speech=value;const other=e.target.closest('.line-card').querySelector('[data-field="line-speech"]');other.value=value;}else l.speech=value;}
  else if(field==='scene-points')s.data.points=value.split('\n').filter(x=>x.trim());
  else if(field==='scene-pause')s.data.pause=Number(value);
  else s.data[field.slice(6)]=value;
 },key);
});
document.addEventListener('change',e=>{
 if(e.target.dataset.delivery&&e.target.tagName==='SELECT'){editDelivery(e.target);return;}
 const field=e.target.dataset.field;if(!field||!p||e.target.tagName!=='SELECT')return;
 if(field==='scene-chapter'){const {c,s}=current(),dest=p.chapters.find(x=>x.id===e.target.value);if(dest===c)return;mutate(()=>{c.scenes=c.scenes.filter(x=>x.id!==s.id);dest.scenes.push(s);collapsed.delete(dest.id);});}
 else {mutate(()=>current().s.data[field.slice(6)]=e.target.value);const panel=e.target.closest('.settings');if(panel){panel.querySelector('.sprite-preview').outerHTML=spritePreview(current().s.data.expression,current().s.data.pose);for(const card of document.querySelectorAll('.line-card')){const line=current().s.lines.find(l=>l.id===card.dataset.line),d=line.direction||{};card.querySelector('.sprite-preview').outerHTML=spritePreview(d.expression??current().s.data.expression,d.pose??current().s.data.pose);}return;}}
 renderAll();
});
document.addEventListener('dragstart',e=>{const s=e.target.closest('[data-drag-scene]'),c=e.target.closest('[data-drag-chapter]');if(!s&&!c)return;drag={type:s?'scene':'chapter',id:s?s.dataset.dragScene:c.dataset.dragChapter};e.dataTransfer.setData('text/plain',JSON.stringify(drag));e.dataTransfer.effectAllowed='move';e.target.classList.add('dragging');});
document.addEventListener('dragend',()=>{drag=null;document.querySelectorAll('.dragging,.drop-target').forEach(x=>x.classList.remove('dragging','drop-target'));});
document.addEventListener('dragover',e=>{const t=e.target.closest('[data-drop-scene],[data-drop-chapter]');if(t&&drag){e.preventDefault();document.querySelectorAll('.drop-target').forEach(x=>x.classList.remove('drop-target'));t.classList.add('drop-target');}});
document.addEventListener('drop',e=>{const t=e.target.closest('[data-drop-scene],[data-drop-chapter]');if(!t||!drag||!p)return;e.preventDefault();const destScene=t.dataset.dropScene,chapterId=t.dataset.dropChapter||locate(destScene)?.c.id;if(drag.type==='scene'){const hit=locate(drag.id),dest=p.chapters.find(c=>c.id===chapterId);if(!hit||!dest||destScene===hit.s.id)return;mutate(()=>{hit.c.scenes=hit.c.scenes.filter(s=>s.id!==hit.s.id);const index=destScene?dest.scenes.findIndex(s=>s.id===destScene):dest.scenes.length;dest.scenes.splice(index,0,hit.s);collapsed.delete(dest.id);});}else if(drag.id!==chapterId){const from=p.chapters.find(c=>c.id===drag.id);if(!from)return;mutate(()=>{p.chapters=p.chapters.filter(c=>c.id!==from.id);p.chapters.splice(p.chapters.findIndex(c=>c.id===chapterId),0,from);});}renderAll();});
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();save().then(()=>toast('保存しました')).catch(error);}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'&&!e.isComposing){e.preventDefault();e.shiftKey?restore(future,past):restore(past,future);}});
window.addEventListener('beforeunload',e=>{if(generation!==savedGeneration){e.preventDefault();e.returnValue='';}});

// Optional agent tools share the editor's state and persistence path.
function registerTools(){const context=document.modelContext;if(!context?.registerTool)return;const lifecycle=new AbortController();for(const tool of [
 {name:'read_script_outline',title:'編集中の台本を読む',description:'Read the current edited script and its feedback without changing it.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,untrustedContentHint:true},execute:()=>({project:p?clone(p):null})},
 {name:'add_script_feedback',title:'台本に編集メモを追加',description:'Add an open feedback note to an existing target and save it locally.',inputSchema:{type:'object',properties:{target:{type:'string'},text:{type:'string'}},required:['target','text'],additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:true},execute:async input=>{if(!p||!input||typeof input.text!=='string'||!input.text.trim()||!targetMap().has(input.target))throw new Error('有効な対象とメモが必要です');const noteId=id();mutate(()=>p.feedback.push({id:noteId,target:input.target,text:input.text,status:'open'}));renderNotes();await save();return {id:noteId,saved:true};}}
 ]){try{Promise.resolve(context.registerTool(tool,{signal:lifecycle.signal})).catch(()=>{});}catch{}}window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});}
try{const boot=await api('/api/bootstrap');token=boot.token;projects=boot.projects;library=boot.library;if(projects.length)activate(projects[0]);else if(library.length){const initial=library.find(x=>x.id.includes('moonbit'))||library[0];await imported({libraryId:initial.id});}else renderAll();registerTools();}catch(e){error(e);status('接続できません');}

function deliveryControls(line,scene){const d=line.direction||{};return `<details class="delivery"><summary>テンポ・立ち絵 ${d.source==='auto'?'· 自動提案':line.direction?'· 手動設定':'· 場面設定を継承'}</summary>${spritePreview(d.expression??scene.data.expression,d.pose??scene.data.pose)}<div class="settings-grid"><label>話速<input type="number" min="0.5" max="2" step="0.01" data-delivery="speed" data-line-id="${line.id}" value="${d.speed??p.meta.speed??1}"></label><label>セリフ後の追加の間（秒）<input type="number" min="0" max="10" step="0.05" data-delivery="pause" data-line-id="${line.id}" value="${d.pause??0}"></label><label>表情<select data-delivery="expression" data-line-id="${line.id}">${options([['normal','ふつう'],['happy','笑顔'],['surprised','驚き'],['thinking','考える']],d.expression??scene.data.expression??'normal')}</select></label><label>ポーズ<select data-delivery="pose" data-line-id="${line.id}">${options([['normal','ふつう'],['wave','手を挙げる'],['point','指差し'],['think','考える']],d.pose??scene.data.pose??'normal')}</select></label></div><small>${esc(d.reason||'未指定項目は台本・場面の設定を使います。')} ／変更したセリフは自動提案で上書きしません。</small></details>`;}
function editDelivery(el){if(!p||!current())return;const key=el.dataset.delivery,numeric=['speed','pause'].includes(key);if(numeric&&(el.value===''||!el.checkValidity()))return;const line=current().s.lines.find(l=>l.id===el.dataset.lineId);if(!line)return;mutate(()=>{line.direction={...line.direction,[key]:numeric?Number(el.value):el.value,source:'manual'};delete line.direction.reason;},'delivery:'+line.id+key);el.closest('details').querySelector('summary').textContent='テンポ・立ち絵 · 手動設定';const preview=el.closest('details').querySelector('.sprite-preview');preview.outerHTML=spritePreview(line.direction.expression??current().s.data.expression,line.direction.pose??current().s.data.pose);}
async function autoDirection(sceneId){const ticket=generation,projectId=p.id;const result=await api('/api/direction',{project:clone(p),sceneId});if(p.id!==projectId||ticket!==generation)throw Error('提案中に編集が入りました。もう一度実行してください。');mutate(()=>{p.chapters=result.chapters;});renderAll();toast('演出案を適用しました。各セリフで調整でき、「戻す」で取り消せます');}
let previewTimer;
async function previewScene(){if(!current())return;await save();const job=await api('/api/preview',{project:clone(p),sceneId:selected.id});$('#preview-dialog').showModal();$('#preview-video').hidden=true;$('#preview-video').removeAttribute('src');$('#preview-status').textContent=job.heading+'：生成中…（数分かかる場合があります）';clearTimeout(previewTimer);watchPreview(job.id);}
async function watchPreview(jobId){try{const job=await api('/api/preview/'+jobId);if(job.status==='running'){previewTimer=setTimeout(()=>watchPreview(jobId),2000);return;}if(job.status==='error'){$('#preview-status').textContent='生成に失敗しました。VOICEVOXの起動と台本を確認してください。 '+job.error;return;}$('#preview-status').textContent=job.heading+'：生成時点の台本です。編集後は再生成してください。';$('#preview-video').src=job.url;$('#preview-video').hidden=false;}catch(e){$('#preview-status').textContent='状態を取得できません：'+e.message;}}

$("#preview-dialog").addEventListener("close",()=>$("#preview-video").pause());

function spritePreview(expression='normal',pose='normal'){const expressions={normal:'ふつう',happy:'笑顔',surprised:'驚き',thinking:'考える'},poses={normal:'ふつう',wave:'手を挙げる',point:'指差し',think:'考える'};return `<figure class="sprite-preview"><img src="/sprites/${encodeURIComponent(expression)}-${encodeURIComponent(pose)}.png" alt="立ち絵：${esc(expressions[expression])}・${esc(poses[pose])}" loading="lazy" width="128" height="234"><figcaption><strong>${esc(expressions[expression])} × ${esc(poses[pose])}</strong><span>選択するとすぐに切り替わります</span><small>動画と同じ立ち絵差分（目・口は静止）</small></figcaption></figure>`;}
document.addEventListener('error',e=>{if(e.target.matches?.('.sprite-preview img')){e.target.hidden=true;const caption=e.target.parentElement.querySelector('figcaption');caption.textContent='立ち絵プレビューを読み込めません。素材の準備状況を確認してください。';}},true);
