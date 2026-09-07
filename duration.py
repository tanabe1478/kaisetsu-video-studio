"""Estimate duration without synthesizing; reuse exact cached VOICEVOX WAVs."""
import hashlib, json, math, wave, time, urllib.request
from pathlib import Path
from direction import effective
from presentation import voice_style, local_asset

_engine=None
_checked=0
def engine_info():
    global _engine,_checked
    if time.monotonic()-_checked<30:return _engine
    _checked=time.monotonic()
    try:
        def get(route):
            with urllib.request.urlopen('http://127.0.0.1:50021/'+route,timeout=1) as r:return json.load(r)
        _engine=(get('version'),get('speakers'))
    except Exception:_engine=None
    return _engine

def estimate(project,cache,engine=None):
    if engine:version,speakers=engine
    seconds=0;known=0;count=0;estimated_seconds=0;pause_seconds=0;characters=0
    for scene in project.get('scenes',[]):
        scene_seconds=0
        for line in scene.get('narration',[]) or ([{'text':scene['text']}] if scene.get('text') else []):
            if not line.get('text','').strip():continue
            count+=1;characters+=len(line['text']);d=effective(line,scene,project.get('speed',1));length=None
            style=voice_style(project,line,engine[1]) if engine else None
            if line.get('audio'):
                try:
                    with wave.open(str(local_asset(line['audio']))) as f:length=f.getnframes()/f.getframerate()
                    known+=1
                except (ValueError,OSError,wave.Error,EOFError):pass
            if style is not None and not line.get('audio'):
                key=hashlib.sha256(json.dumps([line.get('speech',line['text']),style,d['speed'],version],ensure_ascii=False).encode()).hexdigest()
                path=Path(cache)/(key+'.wav')
                if path.is_file():
                    try:
                        with wave.open(str(path)) as f:length=f.getnframes()/f.getframerate()
                        known+=1
                    except (OSError,wave.Error,EOFError):pass
            if length is None:
                length=len(line['text'])/(5.5*d['speed'])+.25
                estimated_seconds+=length
            scene_seconds+=length+d['pause'];pause_seconds+=d['pause']
        gap=scene.get('pause',.6);scene_seconds+=gap;pause_seconds+=gap
        seconds+=math.ceil(scene_seconds*24)/24
    target=project.get('targetMinutes',0)*60
    spoken=max(0,seconds-pause_seconds)
    budget=round(characters*max(0,target-pause_seconds)/spoken) if target and spoken else None
    return {'seconds':seconds,'lowerSeconds':max(0,seconds-estimated_seconds*.25),'upperSeconds':seconds+estimated_seconds*.25,
            'cachedLines':known,'totalLines':count,'exact':count>0 and count==known,
            'pauseSeconds':pause_seconds,'characters':characters,'targetSeconds':target,'suggestedCharacters':budget}
