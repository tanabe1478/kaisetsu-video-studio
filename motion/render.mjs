import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.resolve(process.argv[2]);
const inputProps=JSON.parse(readFileSync(path.join(out,'input.json')));
const serveUrl=await bundle({entryPoint:path.join(here,'src/index.tsx'),outDir:path.join(out,'bundle')});
const composition=await selectComposition({serveUrl,id:'PrefixChange',inputProps});
const points=[0,2.4,2.8,4,8,12,17.25,18.5,22,28.7,30,32.5,37];
for(const t of points){await renderStill({serveUrl,composition,inputProps,frame:Math.round(t*24),output:path.join(out,`check-${t}.png`)});console.log('Checked frame',t);}
const target=path.join(out,'silent.mp4');
if(existsSync(target))throw Error('Use a new output directory to preserve renders');
let last=-1;
await renderMedia({serveUrl,composition,inputProps,codec:'h264',outputLocation:target,concurrency:2,onProgress:({progress})=>{const n=Math.floor(progress*10);if(n!==last){last=n;console.log('Render',n*10+'%');}}});
writeFileSync(path.join(out,'render-backend.json'),JSON.stringify({engine:'Remotion',version:'4.0.522',composition:'PrefixChange',frames:954,checkpointSeconds:points},null,2));

execFileSync(path.join(here,'../.venv/bin/python'),[path.join(here,'finish.py'),out],{stdio:'inherit'});
