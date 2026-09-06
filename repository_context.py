"""Inspect an existing Git checkout for a repository lesson; never run its code."""
import argparse, datetime, json, subprocess
from pathlib import Path

def inspect(checkout):
    checkout=Path(checkout).resolve()
    def git(*args):
        return subprocess.check_output(['git','-C',str(checkout),*args],text=True,encoding='utf-8').strip()
    files=git('ls-files','-z').split('\0')
    inventory=[]
    for name in files:
        if not name:continue
        p=checkout/name
        if p.is_symlink() or not p.is_file():continue
        inventory.append({'path':name,'bytes':p.stat().st_size})
    return {'url':git('remote','get-url','origin'),'commit':git('rev-parse','HEAD'),
            'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'workingTreeDirty':bool(git('status','--porcelain')),
            'files':inventory,'executed':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('checkout');ap.add_argument('--output',required=True)
    args=ap.parse_args();dest=Path(args.output)
    if dest.exists():ap.error('出力先が存在します。別のファイル名を指定してください。')
    result=inspect(args.checkout);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(dest.resolve())
