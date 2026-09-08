from pathlib import Path
import sys,subprocess,json,html
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import imageio_ffmpeg
from verify_video import verify
out=Path(sys.argv[1]).resolve()
if not (out/'demo.mp4').exists():
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-n','-i',str(out/'silent.mp4'),'-i',str(out/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out/'demo.mp4')],check=True)
print(verify(out))
timeline=json.loads((out/'timeline.json').read_text());chapters=[]
for item in timeline:
 name=item['scene']['chapter']
 if not chapters or chapters[-1]['name']!=name:chapters.append({'name':name,'start':item['start']})
seconds=timeline[-1]['end'];duration_label=f'{int(seconds//60)}分{seconds%60:g}秒'
buttons=''.join(f'<button data-time="{c["start"]}">{html.escape(c["name"])}</button>' for c in chapters)
(out/'index.html').write_text('''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>プロンプトキャッシュとPi — 完全版</title><style>body{margin:28px auto;max-width:1200px;padding:0 24px;background:#f6f3e9;color:#173d35;font:17px system-ui}video{width:100%;border-radius:14px;background:#173d35}button{padding:12px;margin:5px;border:1px solid #819c8c;border-radius:8px;background:white;color:#173d35;cursor:pointer;text-align:left}h1{font-size:28px}.chapters{display:grid;grid-template-columns:1fr 1fr}small{color:#50675d}</style><h1>プロンプトキャッシュとPiの設計 — 完全版</h1><p>'''+duration_label+''' · 30場面 · 2人の掛け合い · Remotion / SVG</p><video controls preload="metadata" src="demo.mp4"></video><p id="time">動画を読み込み中…</p><div class="chapters">'''+buttons+'''</div><p><a href="demo.mp4" download>完全版MP4を保存</a> · <a href="subtitles.srt" download>字幕SRT</a></p><small>VOICEVOX：四国めたん・ずんだもん。図は模式図。出典・固定コミットは台本に保持。</small><script>const v=document.querySelector('video');fetch('demo.mp4').then(r=>r.blob()).then(b=>{v.src=URL.createObjectURL(b);document.querySelector('#time').textContent='再生できます'}).catch(e=>document.querySelector('#time').textContent=e.message);document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{v.pause();v.currentTime=Number(b.dataset.time)});v.ontimeupdate=()=>document.querySelector('#time').textContent=Math.floor(v.currentTime/60)+':'+String(Math.floor(v.currentTime)%60).padStart(2,'0')+' / 20:03';</script></html>''')

if (out/'readings.html').exists():
 page=out/'index.html';page.write_text(page.read_text().replace('<p><a href="demo.mp4"','<p><a href="readings.html">修正した読みを短い音声で確認</a> · <a href="script.json" download>改訂台本JSON</a></p><p><a href="demo.mp4"'))
