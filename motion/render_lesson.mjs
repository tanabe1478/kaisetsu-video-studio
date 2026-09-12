import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill,openBrowser} from '@remotion/renderer';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),out=path.resolve(process.argv[2]);
const inputProps=JSON.parse(readFileSync(path.join(out,'input.json')));
const serveUrl=await bundle({entryPoint:path.join(here,'src/slop.tsx'),outDir:path.join(out,'bundle')});
const browser=await openBrowser('chrome');
try{
 const composition=await selectComposition({serveUrl,id:'SlopCodeBench',inputProps,puppeteerInstance:browser});
 let offset=0;const checks=[];
 for(const [index,item] of inputProps.timeline.entries()){
  for(const line of [1,3,5]){
   const c=item.captions[line],local=Math.round((c.start+(c.end-c.start)*.65)*24),frame=offset+local;
   const name=`scene-${String(index+1).padStart(2,'0')}-line-${line+1}.png`;
   await renderStill({serveUrl,composition,inputProps,frame,output:path.join(out,name),puppeteerInstance:browser});checks.push({scene:index+1,line:line+1,frame,file:name});
  }
  offset+=item.frames;console.log('Scene checks',index+1,'/'+inputProps.timeline.length);
 }
 writeFileSync(path.join(out,'checkpoints.json'),JSON.stringify(checks,null,2));
 if(process.argv.includes('--stills-only'))process.exitCode=0;
 else if(process.argv.some(a=>a.startsWith('--preview-scene='))){
  const index=Number(process.argv.find(a=>a.startsWith('--preview-scene=')).split('=')[1])-1;
  const item=inputProps.timeline[index];if(!item)throw Error('Invalid scene');
  const start=inputProps.timeline.slice(0,index).reduce((n,s)=>n+s.frames,0);
  await renderMedia({serveUrl,composition,inputProps,codec:'h264',outputLocation:path.join(out,'preview-silent.mp4'),frameRange:[start,start+item.frames-1],concurrency:4,puppeteerInstance:browser});
  execFileSync(path.join(here,'../.venv/bin/python'),['-c',`import imageio_ffmpeg,subprocess;subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-i',r'${path.join(out,'preview-silent.mp4')}','-ss','${start/24}','-i',r'${path.join(out,'narration.wav')}','-t','${item.frames/24}','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-movflags','+faststart',r'${path.join(out,'preview.mp4')}'],check=True)`],{stdio:'inherit'});
 }
 else{
  const target=path.join(out,'silent.mp4');if(existsSync(target))throw Error('Use a new output directory');
  let last=-1;await renderMedia({serveUrl,composition,inputProps,codec:'h264',outputLocation:target,concurrency:4,puppeteerInstance:browser,onProgress:({progress})=>{const n=Math.floor(progress*100);if(n!==last){last=n;console.log('Full render',n+'%')}}});
  writeFileSync(path.join(out,'render-backend.json'),JSON.stringify({engine:'Remotion',version:'4.0.522',composition:'SlopCodeBench',frames:offset,scenes:inputProps.timeline.length},null,2));
  execFileSync(path.join(here,'../.venv/bin/python'),[path.join(here,'finish_lesson.py'),out],{stdio:'inherit'});
 }
}finally{await browser.close({silent:true});}
