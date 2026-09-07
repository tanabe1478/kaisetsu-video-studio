"""Render two silent storyboard clips from the saved lesson; never synthesize speech."""
from pathlib import Path
import json,subprocess,sys
from PIL import ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import imageio_ffmpeg
from presentation import backdrop,draw_people,character
from direction import effective
from studio import caption_frame
from fonts import font

def main():
    project=json.loads((Path(__file__).parent/'lesson.json').read_text())
    dest=ROOT/'output/prompt-caching-pi-20260908';dest.mkdir(parents=True,exist_ok=True)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    for idx,name in [(7,'prefix-change'),(20,'compaction')]:
        target=dest/(name+'.mp4')
        if target.exists():raise FileExistsError(f'既存のプレビューを保持します: {target}')
        scene=project['scenes'][idx];fps=12;seconds=30
        with (dest/(name+'-render.log')).open('w') as log:
            proc=subprocess.Popen([ffmpeg,'-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],stdin=subprocess.PIPE,stderr=log)
            try:
                for n in range(seconds*fps):
                    t=n/fps;line_index=min(5,int(t/5));fraction=(t-line_index*5)/5
                    line=scene['narration'][line_index]
                    im=backdrop(project,scene,idx,len(project['scenes']),line,motion_position=line_index+1+fraction)
                    draw_people(im,project,line['character'],effective(line,scene,1),False,False)
                    caption_frame(im,line['text'],character(project,line)['color'])
                    draw=ImageDraw.Draw(im)
                    draw.rectangle((700,80,1270,119),fill='#f3f2e7')
                    draw.text((715,88),'無音・動き確認用／音声タイミング未確定',font=font(18),fill='#8c3e24')
                    draw.rectangle((0,687,1280,720),fill='#f3f2e7')
                    draw.text((35,694),'画像：台本ノート内蔵イラスト ／ このプレビューに音声はありません',font=font(14),fill='#52665b')
                    proc.stdin.write(im.tobytes())
                    if n in (0,180,359):im.save(dest/f'{name}-{n:03}.png')
            finally:proc.stdin.close()
            if proc.wait():raise RuntimeError('FFmpeg failed; see render log')
        subprocess.run([ffmpeg,'-v','error','-i',str(target),'-f','null','-'],check=True)
        print(target,flush=True)
    (dest/'preview-info.json').write_text(json.dumps(dict(clips=['prefix-change.mp4','compaction.mp4'],secondsEach=30,fps=12,audio=False,timing='各セリフ5秒に割り当てた絵コンテ確認用。音声タイミング・完成尺の測定ではない。',fullVideoGenerated=False),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
