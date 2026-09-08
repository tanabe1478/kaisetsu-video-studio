"""Verify a rendered full video before marking delivery complete."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math, re, subprocess
import imageio_ffmpeg
import numpy as np


def verify(output):
    out=Path(output).resolve();manifest=out/'delivery.json'
    # A previous result must not survive a failed verification of a new render.
    if manifest.exists():manifest.unlink()
    video=out/'demo.mp4'
    for name in ('demo.mp4','timeline.json','subtitles.srt','chapters.txt','CREDITS.txt'):
        if not (out/name).is_file() or not (out/name).stat().st_size:
            raise ValueError(f'成果物がありません: {name}')
    timeline=json.loads((out/'timeline.json').read_text());expected=0;captions=0;expected_subtitles=[];expected_chapters=[]
    for scene in timeline:
        if abs(scene['start']-expected)>1/24 or scene['end']<=scene['start']:
            raise ValueError('場面の時間が連続していません。')
        previous=0
        for caption in scene['captions']:
            if not 0<=previous<=caption['start']<caption['end']<=scene['end']-scene['start']+1/24:
                raise ValueError('字幕の時間が不正です。')
            previous=caption['end'];captions+=1
            expected_subtitles.append((scene['start']+caption['start'],scene['start']+caption['end']))
        name=scene.get('scene',{}).get('chapter',scene.get('scene',{}).get('heading'))
        if name and (not expected_chapters or expected_chapters[-1][1]!=name):expected_chapters.append((scene['start'],name))
        expected=scene['end']
    if not timeline or not captions:raise ValueError('本編または字幕が空です。')
    subs=(out/'subtitles.srt').read_text(encoding='utf-8-sig')
    if subs.count(' --> ')!=captions:raise ValueError('字幕数がタイムラインと一致しません。')
    def seconds(stamp):
        h,m,s,ms=map(int,re.split('[:,]',stamp));return h*3600+m*60+s+ms/1000
    entries=re.findall(r'^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})$',subs,re.M)
    if len(entries)!=captions or any(abs(seconds(a)-x)>.002 or abs(seconds(b)-y)>.002 for (a,b),(x,y) in zip(entries,expected_subtitles)):
        raise ValueError('SRTの字幕時刻がタイムラインと一致しません。')
    chapter_lines=(out/'chapters.txt').read_text().splitlines()
    if expected_chapters:
        def chapter_stamp(t):
            n=round(t*1000)//1000;return f'{n//3600:02}:{n//60%60:02}:{n%60:02}'
        if chapter_lines!=[f'{chapter_stamp(t)} {name}' for t,name in expected_chapters]:raise ValueError('章の開始時刻がタイムラインと一致しません。')
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    decoded=subprocess.run([ffmpeg,'-hide_banner','-xerror','-i',str(video),'-map','0:v:0','-map','0:a:0','-progress','pipe:1','-nostats','-f','null','-'],capture_output=True,text=True)
    (out/'decode.log').write_text(decoded.stderr)
    if decoded.returncode:raise ValueError('映像・音声の全編デコードに失敗しました。decode.logを確認してください。')
    times=re.findall(r'^out_time_us=(\d+)$',decoded.stdout,re.M)
    if not times:raise ValueError('完成尺を読み取れません。')
    actual=int(times[-1])/1_000_000
    if abs(actual-expected)>.3:raise ValueError(f'映像が台本の最後までありません: {actual:.3f}s / {expected:.3f}s')
    frames=re.findall(r'^frame=\s*(\d+)$',decoded.stdout,re.M)
    if not frames or int(frames[-1])!=sum(s['frames'] for s in timeline):
        raise ValueError('本編の映像フレーム数がタイムラインと一致しません。')
    raw=subprocess.run([ffmpeg,'-v','error','-i',str(video),'-map','0:a:0','-ac','1','-ar','8000','-f','s16le','-'],capture_output=True,check=True).stdout
    samples=np.frombuffer(raw,dtype='<i2').astype(float)/32768
    if abs(len(samples)/8000-expected)>.3:raise ValueError('本編の音声がタイムラインの最後までありません。')
    rms=float(np.sqrt(np.mean(samples*samples))) if len(samples) else 0
    if rms<1e-5:raise ValueError('本編の音声が無音です。')
    digest=hashlib.sha256(video.read_bytes()).hexdigest()
    result=dict(status='verified',video=str(video),bytes=video.stat().st_size,sha256=digest,seconds=actual,timelineSeconds=expected,scenes=len(timeline),captions=captions,chapters=len(chapter_lines),audioRmsDb=20*math.log10(rms),checks=['video_and_audio_full_decode','duration_matches_timeline','video_frame_count','audio_duration','caption_times','caption_count','chapter_times','non_silent_audio','credits_present'],visualListeningReview='別途記録。自動検証では発音や図の意味を判定しない。')
    result['verifiedAt']=datetime.now(timezone.utc).isoformat()
    if (out/'script.json').is_file():result['scriptSha256']=hashlib.sha256((out/'script.json').read_bytes()).hexdigest()
    manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output');args=parser.parse_args()
    print(json.dumps(verify(args.output),ensure_ascii=False,indent=2))
