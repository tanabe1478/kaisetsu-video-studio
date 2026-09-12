"""Mux and verify the full lesson, then create a local chapter player."""
from pathlib import Path
import sys, subprocess, json, html
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
import imageio_ffmpeg
from verify_video import verify

out = Path(sys.argv[1]).resolve()
if not (out / 'demo.mp4').exists():
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-n',
                    '-i', str(out / 'silent.mp4'), '-i', str(out / 'narration.wav'),
                    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
                    str(out / 'demo.mp4')], check=True)
print(verify(out))
timeline = json.loads((out / 'timeline.json').read_text())
script = json.loads((out / 'script.json').read_text())
chapters = []
for item in timeline:
    name = item['scene']['chapter']
    if not chapters or chapters[-1]['name'] != name:
        chapters.append({'name': name, 'start': item['start']})
seconds = round(timeline[-1]['end'])
duration = f'{seconds // 60}:{seconds % 60:02}'
title = html.escape(script['title'])
buttons = ''.join(f'<button data-time="{c["start"]}">{html.escape(c["name"])}</button>' for c in chapters)
page = '''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>__TITLE__</title>
<style>body{margin:28px auto;max-width:1200px;padding:0 24px;background:#f6f3e9;color:#173d35;font:17px system-ui}video{width:100%;border-radius:14px;background:#173d35}button{padding:12px;margin:5px;border:1px solid #819c8c;border-radius:8px;background:white;color:#173d35;cursor:pointer;text-align:left}h1{font-size:28px}.chapters{display:grid;grid-template-columns:1fr 1fr}small{color:#50675d}</style>
<h1>__TITLE__</h1><p>音声付き完全版 · __DURATION__ · __SCENES__場面 · 2人の掛け合い</p>
<video controls preload="metadata" src="demo.mp4"></video><p id="time">動画を読み込み中…</p><div class="chapters">__BUTTONS__</div>
<p><a href="demo.mp4" download>完全版MP4</a> · <a href="script.json" download>台本JSON</a> · <a href="subtitles.srt" download>字幕SRT</a> · <a href="SOURCES.md">出典と確認範囲</a> · <a href="preview.mp4">計算例の短い場面</a></p>
<small>VOICEVOX：四国めたん・ずんだもん。論文報告値と独自の模式図を画面で区別しています。</small>
<script>const v=document.querySelector('video'),status=document.querySelector('#time');fetch('demo.mp4').then(r=>{if(!r.ok)throw Error('動画の取得に失敗しました');return r.blob()}).then(b=>{v.src=URL.createObjectURL(b);status.textContent='再生できます'}).catch(e=>status.textContent=e.message);document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{v.pause();v.currentTime=Number(b.dataset.time)});v.ontimeupdate=()=>status.textContent=Math.floor(v.currentTime/60)+':'+String(Math.floor(v.currentTime)%60).padStart(2,'0')+' / __DURATION__';</script></html>'''
for old, new in [('__TITLE__', title), ('__DURATION__', duration), ('__SCENES__', str(len(timeline))), ('__BUTTONS__', buttons)]:
    page = page.replace(old, new)
(out / 'index.html').write_text(page)
