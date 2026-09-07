"""Package a rendered snapshot with chapters; verify the actual final streams."""
import argparse, hashlib, json, subprocess, wave
from pathlib import Path
import imageio_ffmpeg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('script', type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    project = json.loads(args.script.read_text(encoding='utf-8-sig'))
    timeline = json.loads((out/'timeline.json').read_text(encoding='utf-8'))
    assert len(timeline) == len(project['scenes'])
    chapters = []
    previous = 0
    for item, scene in zip(timeline, project['scenes']):
        assert item['scene']['narration'] == scene['narration']
        assert item['scene']['board'] == scene['board']
        assert abs(item['start']-previous) < 1e-6
        assert abs(item['frames']/24-(item['end']-item['start'])) < 1e-6
        last = 0
        for c, line in zip(item['captions'],scene['narration']):
            assert 0 <= last <= c['start'] < c['end'] <= item['end']-item['start']
            assert c['text'] == line['text'] and c['character'] == line['character']
            assert c['boardStep'] == line['boardStep'] and c['boardFocus'] == line['boardFocus']
            last = c['end']
        assert len(item['captions']) == len(scene['narration'])
        previous = item['end']
        if not chapters or chapters[-1]['name'] != scene['chapter']:
            chapters.append({'name':scene['chapter'],'start':item['start']})
    for i,c in enumerate(chapters):
        c['end'] = chapters[i+1]['start'] if i+1<len(chapters) else timeline[-1]['end']
    def escape(s):
        return s.replace('\\','\\\\').replace('=','\\=').replace(';','\\;').replace('#','\\#').replace('\n',' ')
    metadata = [';FFMETADATA1','title='+escape(project['title']),
                'comment='+escape('東方Project二次創作 / '+project['references'][0]['url'])]
    for c in chapters:
        metadata += ['[CHAPTER]','TIMEBASE=1/1000',f"START={round(c['start']*1000)}",
                     f"END={round(c['end']*1000)}",'title='+escape(c['name'])]
    (out/'chapters.ffmeta').write_text('\n'.join(metadata)+'\n',encoding='utf-8')
    binary = imageio_ffmpeg.get_ffmpeg_exe()
    final = out/'epiplexity.mp4'
    subprocess.run([binary,'-v','error','-y','-i',str(out/'demo.mp4'),'-i',str(out/'chapters.ffmeta'),
                    '-map','0:v:0','-map','0:a:0','-map_metadata','1','-map_chapters','1',
                    '-c','copy','-movflags','+faststart',str(final)],check=True)
    decoded = subprocess.run([binary,'-v','error','-xerror','-i',str(final),'-map','0:v:0','-map','0:a:0',
                              '-f','null','-'],capture_output=True,text=True,check=True)
    assert not decoded.stderr.strip(), decoded.stderr
    with wave.open(str(out/'narration.wav')) as w:
        duration = w.getnframes()/w.getframerate()
    assert abs(duration-timeline[-1]['end']) < 1/24
    reader = imageio_ffmpeg.read_frames(str(final))
    stream = next(reader); reader.close()
    assert stream['size'] == (1280,720) and abs(stream['fps']-24)<.01
    assert abs(stream['duration']-duration) < .1
    (out/'script.json').write_bytes(args.script.read_bytes())
    report = {'duration_seconds':duration,'container_duration_seconds':stream['duration'],
              'resolution':stream['size'],'fps':stream['fps'],'scenes':len(timeline),'chapters':chapters,
              'caption_segments':sum(len(s['captions']) for s in timeline),'bytes':final.stat().st_size,
              'full_av_decode':'passed','caption_and_scene_timeline':'passed',
              'script_sha256':hashlib.sha256(args.script.read_bytes()).hexdigest(),
              'bgm':project['bgm']['title'],'audio_listening_review':'not performed'}
    (out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
