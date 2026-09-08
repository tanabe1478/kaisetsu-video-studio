import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill,openBrowser} from '@remotion/renderer';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),out=path.resolve(process.argv[2]);
const inputProps=JSON.parse(readFileSync(path.join(out,'input.json')));
const serveUrl=await bundle({entryPoint:path.join(here,'src/full.tsx'),outDir:path.join(out,'bundle')});
const browser=await openBrowser('chrome');
try{
 const composition=await selectComposition({serveUrl,id:'PromptCachingFull',inputProps,puppeteerInstance:browser});
 let offset=0;const checks=[];
 for(const [index,item] of inputProps.timeline.entries()){
  for(const line of [1,3,5]){
   const c=item.captions[line],local=Math.round((c.start+(c.end-c.start)*.65)*24),frame=offset+local;
   const name=`scene-${String(index+1).padStart(2,'0')}-line-${line+1}.png`;
   await renderStill({serveUrl,composition,inputProps,frame,output:path.join(out,name),puppeteerInstance:browser});checks.push({scene:index+1,line:line+1,frame,file:name});
  }
  offset+=item.frames;console.log('Scene checks',index+1,'/30');
 }
 writeFileSync(path.join(out,'checkpoints.json'),JSON.stringify(checks,null,2));
 if(process.argv.includes('--stills-only'))process.exitCode=0;
 else{
  const target=path.join(out,'silent.mp4');if(existsSync(target))throw Error('Use a new output directory');
  let last=-1;await renderMedia({serveUrl,composition,inputProps,codec:'h264',outputLocation:target,concurrency:4,puppeteerInstance:browser,onProgress:({progress})=>{const n=Math.floor(progress*100);if(n!==last){last=n;console.log('Full render',n+'%')}}});
  writeFileSync(path.join(out,'render-backend.json'),JSON.stringify({engine:'Remotion',version:'4.0.522',composition:'PromptCachingFull',frames:offset,scenes:30},null,2));
  execFileSync(path.join(here,'../.venv/bin/python'),[path.join(here,'finish_full.py'),out],{stdio:'inherit'});
 }
}finally{await browser.close({silent:true});}
