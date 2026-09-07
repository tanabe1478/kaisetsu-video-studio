"""Use the official AquesTalkPlayer CLI, keeping its binaries outside Git."""
import argparse, hashlib, json, subprocess, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def prepare(source, output, player):
    source, output, player = source.resolve(), output.resolve(), player.resolve()
    if source == output: raise ValueError('元台本とは別の出力先を指定してください。')
    p = json.loads(source.read_text(encoding='utf-8-sig'))
    if output.exists(): raise ValueError('既存の改訂版は上書きしません。別の出力先を指定してください。')
    people = p.get('characters',[])
    mapping = {'霊夢':'れいむ','魔理沙':'まりさ'}
    if len(people)!=2 or any(c['name'] not in mapping for c in people):
        raise ValueError('霊夢・魔理沙の2話者台本を指定してください。')
    if any(l.get('audio') for s in p['scenes'] for l in s['narration']):
        raise ValueError('既存の外部音声があります。意図を確認してから別の台本を用意してください。')
    signature = hashlib.sha256(player.read_bytes()+(player.parent/'AquesTalkPlayer.preset').read_bytes()).hexdigest()
    audio_dir = ROOT/'assets/audio/aquestalk'; audio_dir.mkdir(parents=True,exist_ok=True)
    identities = {c['id']:mapping[c['name']] for c in people}
    records = []
    for si,s in enumerate(p['scenes'],1):
        print(f'AquesTalk scene {si}/{len(p["scenes"])}',flush=True)
        for li,l in enumerate(s['narration'],1):
            text = l.get('speech',l['text']); preset = identities[l['character']]
            key = hashlib.sha256(json.dumps([text,preset,signature],ensure_ascii=False).encode()).hexdigest()
            dest = audio_dir/(key+'.wav')
            if not dest.exists():
                subprocess.run([str(player),'/T',text,'/P',preset,'/W',str(dest)],cwd=player.parent,
                               timeout=60,check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            with wave.open(str(dest)) as w:
                seconds = w.getnframes()/w.getframerate()
                if seconds<=0 or w.getsampwidth()!=2: raise ValueError('音声出力が不正です。')
            l['audio'] = dest.relative_to(ROOT).as_posix()
            l['audioSource'] = {'engine':'AquesTalk1','preset':preset,'sourceSpeech':text,'signature':signature}
            records.append({'scene':si,'line':li,'preset':preset,'seconds':seconds,'path':l['audio']})
    for c in people:
        c['audioCredit'] = 'AquesTalk1:'+identities[c['id']]
    p['productionBrief']['style'] = '霊夢・魔理沙の掛け合い。AquesTalkPlayer公式同梱のれいむ・まりさプリセット。'
    p['audioProduction'] = {'tool':'AquesTalkPlayer','source':'https://www.a-quest.com/products/aquestalkplayer.html',
                            'sourceScriptSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                            'note':'外部WAV使用。direction.speedによる再伸縮はしない。字幕変更後は音声も再生成する。'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    output.with_suffix('.audio-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Created',output)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--player',type=Path,required=True)
    args=parser.parse_args();prepare(args.source,args.output,args.player)
