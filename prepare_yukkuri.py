"""Download the two original Kitsune packages from their author's current page.

Read docs/DIALOGUE_BOARD.md and the current linked terms before running.
Only local ignored assets are written; no generative editing or upscaling.
"""
from pathlib import Path
import argparse, hashlib, html, io, json, re, zipfile
from urllib.parse import unquote, urlparse
import requests

ROOT=Path(__file__).resolve().parent
SOURCE='https://ci-en.net/creator/34363/article/1770577'
TERMS='https://ci-en.net/creator/34363/article/1749040'

def download():
    r=requests.get(SOURCE,timeout=30);r.raise_for_status()
    links=[html.unescape(u) for u in re.findall(r'href="([^"]+)"',r.text)]
    manifest={'source':SOURCE,'terms':TERMS,'files':[]}
    for name,label in [('reimu','れいむ.zip'),('marisa','まりさ.zip')]:
        folder=ROOT/'assets'/'yukkuri'/name;folder.mkdir(parents=True,exist_ok=True)
        archive=folder/'original.zip'
        if not archive.exists():
            url=next((u for u in links if unquote(urlparse(u).path).endswith('/'+label)),None)
            if not url or urlparse(url).hostname!='media.ci-en.jp':raise ValueError('配布元のリンク構成が変わりました。配布ページを確認してください。')
            response=requests.get(url,timeout=60);response.raise_for_status()
            zipfile.ZipFile(io.BytesIO(response.content)).close()
            archive.write_bytes(response.content)
        with zipfile.ZipFile(archive) as z:
            if sum(item.file_size for item in z.infolist())>50_000_000:raise ValueError('想定より大きい素材パッケージです。')
            for item in z.infolist():
                filename=item.filename
                if not item.flag_bits&0x800:
                    try:filename=filename.encode('cp437').decode('cp932')
                    except UnicodeError:pass
                target=(folder/filename).resolve()
                if not target.is_relative_to(folder.resolve()):raise ValueError('素材ZIP内のパスが不正です。')
                if item.is_dir():target.mkdir(parents=True,exist_ok=True)
                elif not target.exists():
                    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(item))
        manifest['files'].append({'character':name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()})
    dest=ROOT/'assets'/'yukkuri'/'SOURCE.json';dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(dest)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--download',action='store_true');args=parser.parse_args()
    if args.download:download()
    else:parser.print_help()
