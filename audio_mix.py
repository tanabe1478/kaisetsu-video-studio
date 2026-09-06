"""Mix a locally supplied BGM beneath narration, leaving voice timing intact."""
from pathlib import Path
import json, math, subprocess, wave
import numpy as np
import imageio_ffmpeg

def prepare_audio(project, root, out):
    narration=Path(out)/'narration.wav'
    config=project.get('bgm')
    if not config:return narration
    music=Path(config['path'])
    if not music.is_absolute():music=Path(root)/music
    if not music.is_file():raise ValueError(f'BGMが見つかりません。配布元から手動で保存してください: {music}')
    below=float(config.get('below_voice_db',22))
    if not math.isfinite(below) or not 10<=below<=40:raise ValueError('below_voice_db must be 10–40')
    with wave.open(str(narration)) as f:
        rate=f.getframerate();channels=f.getnchannels()
        if f.getsampwidth()!=2:raise ValueError('Expected 16-bit narration')
        voice=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
        duration=len(voice)/channels/rate
    # Compare speech-active blocks to the original track, rather than file peaks.
    block=max(1,int(rate*channels*.05));usable=len(voice)//block*block
    levels=np.sqrt(np.mean(voice[:usable].reshape(-1,block)**2,axis=1))
    active=levels[levels>.01]
    if not len(active):raise ValueError('Narration has no measurable speech')
    voice_rms=float(np.sqrt(np.mean(active**2)))
    binary=imageio_ffmpeg.get_ffmpeg_exe()
    raw=subprocess.run([binary,'-v','error','-i',str(music),'-t','600','-ac','1','-ar','24000','-f','f32le','-'],capture_output=True,check=True).stdout
    samples=np.frombuffer(raw,dtype='<f4')
    if not len(samples):raise ValueError('BGM is empty')
    music_rms=float(np.sqrt(np.mean(samples**2)))
    if music_rms<1e-6:raise ValueError('BGM is silent')
    gain=min(1.0,voice_rms*10**(-below/20)/music_rms)
    fade_in=min(2,duration/3);fade_out=min(4,duration/3)
    mixed=Path(out)/'mixed.wav'
    filters=(f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v];'
             f'[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={gain:.9f},'
             f'afade=t=in:st=0:d={fade_in},afade=t=out:st={duration-fade_out}:d={fade_out}[m];'
             '[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=false:latency=true[a]')
    subprocess.run([binary,'-v','error','-y','-i',str(narration),'-stream_loop','-1','-i',str(music),
                    '-filter_complex',filters,'-map','[a]','-t',str(duration),'-c:a','pcm_s16le',str(mixed)],check=True)
    report={'title':config.get('title',''),'creator':config.get('creator',''),'source':config.get('source',''),
            'music_gain_db':20*math.log10(gain),'target_below_active_voice_db':below,
            'fade_in_seconds':fade_in,'fade_out_seconds':fade_out,'duration_seconds':duration}
    (Path(out)/'AUDIO_MIX.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'BGM mixed: {report["title"]} ({below:g} dB below active voice)',flush=True)
    return mixed
