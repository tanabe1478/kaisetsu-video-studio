"""図の定義JSONから、Blenderの3D図解（静止画・動画）と解説ページを作る。

python diorama.py lessons/diorama-sample/spec.json --output output/diorama-sample [--draft]
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, glob, hashlib, html, json, os, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parent
# diorama_blender.pyのTONESと同じ名前。test_diorama.pyで一致を確認する。
TONES = {'ground', 'slab', 'ink', 'muted', 'ghost', 'blue', 'teal', 'amber', 'purple', 'green', 'red', 'pink', 'ball', 'white'}
KINDS = ('pipeline', 'columns', 'board')


def _tone(value, where):
    if value is not None and value not in TONES and not re.fullmatch(r'#[0-9A-Fa-f]{6}', str(value)):
        raise ValueError(f'{where}: 色はTONESの名前か#RRGGBBで指定してください: {value}')


def _text(value, where, required=True, limit=400):
    if value is None and not required:
        return
    if not isinstance(value, str) or (required and not value.strip()) or len(value) > limit:
        raise ValueError(f'{where}: {limit}文字以内の文字列を指定してください。')


def _number(item, name, where):
    if isinstance(item.get(name), bool) or not isinstance(item.get(name), (int, float)):
        raise ValueError(f'{where}.{name}: 数値を指定してください。')


def validate(spec):
    """描画前に定義を検証する。Blender側は検証済みの定義だけを受け取る。"""
    if not isinstance(spec, dict):
        raise ValueError('図の定義はJSONオブジェクトです。')
    _text(spec.get('title'), 'title', limit=120)
    _text(spec.get('lead'), 'lead', required=False, limit=2000)
    figures = spec.get('figures')
    if not isinstance(figures, list) or not figures:
        raise ValueError('figuresに1つ以上の図を指定してください。')
    ids = set()
    for n, fig in enumerate(figures):
        where = f'figures[{n}]'
        if not isinstance(fig, dict) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,40}', str(fig.get('id', ''))):
            raise ValueError(f'{where}.id: 英小文字・数字・ハイフンで指定してください。')
        if fig['id'] in ids:
            raise ValueError(f'{where}.id: 重複しています: {fig["id"]}')
        ids.add(fig['id'])
        if fig.get('kind') not in KINDS:
            raise ValueError(f'{where}.kind: {" / ".join(KINDS)} のいずれかです。')
        _text(fig.get('title'), f'{where}.title', limit=120)
        for key in ('heading', 'subheading', 'caption'):
            _text(fig.get(key), f'{where}.{key}', required=False)
        for i, p in enumerate(fig.get('body', [])):
            _text(p, f'{where}.body[{i}]', limit=2000)
        for i, p in enumerate(fig.get('points', [])):
            if not isinstance(p, dict):
                raise ValueError(f'{where}.points[{i}]: tagとtextを持つオブジェクトです。')
            _text(p.get('tag'), f'{where}.points[{i}].tag', required=False, limit=20)
            _text(p.get('text'), f'{where}.points[{i}].text', limit=2000)
        {'pipeline': _pipeline, 'columns': _columns, 'board': _board}[fig['kind']](fig, where)
    return spec


def _pipeline(fig, where):
    stations = fig.get('stations')
    if not isinstance(stations, list) or not 2 <= len(stations) <= 10:
        raise ValueError(f'{where}.stations: 2〜10個の工程を指定してください。')
    for i, st in enumerate(stations):
        _text(st.get('title'), f'{where}.stations[{i}].title', limit=24)
        _text(st.get('sub'), f'{where}.stations[{i}].sub', required=False, limit=80)
        _tone(st.get('tone'), f'{where}.stations[{i}].tone')
        if 'error' in st:
            _text(st['error'].get('code'), f'{where}.stations[{i}].error.code', limit=8)
            _text(st['error'].get('label'), f'{where}.stations[{i}].error.label', limit=24)
    stores = {}
    for i, store in enumerate(fig.get('stores', [])):
        w = f'{where}.stores[{i}]'
        if store.get('kind') not in ('records', 'topic'):
            raise ValueError(f'{w}.kind: records / topic のいずれかです。')
        if not isinstance(store.get('at'), int) or not 0 <= store['at'] < len(stations):
            raise ValueError(f'{w}.at: 工程の番号（0始まり）を指定してください。')
        _text(store.get('id'), f'{w}.id', limit=40)
        _text(store.get('title'), f'{w}.title', limit=40)
        _text(store.get('sub'), f'{w}.sub', required=False, limit=80)
        _tone(store.get('tone'), f'{w}.tone')
        stores[store['id']] = store['kind']
    scenarios = fig.get('scenarios')
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 6:
        raise ValueError(f'{where}.scenarios: 1〜6個の流れを指定してください。')
    for i, sc in enumerate(scenarios):
        w = f'{where}.scenarios[{i}]'
        _text(sc.get('caption'), f'{w}.caption', limit=80)
        stop = sc.get('stopAt')
        if not isinstance(stop, int) or not 1 <= stop < len(stations):
            raise ValueError(f'{w}.stopAt: 1〜{len(stations) - 1}の工程番号です。')
        if sc.get('result') not in ('ok', 'error'):
            raise ValueError(f'{w}.result: ok / error のいずれかです。')
        if sc['result'] == 'error' and 'error' not in stations[stop]:
            raise ValueError(f'{w}: 工程{stop}にerrorがないため、そこで失敗させられません。')
        for j, effect in enumerate(sc.get('effects', [])):
            e = f'{w}.effects[{j}]'
            if not isinstance(effect.get('at'), int) or not 1 <= effect['at'] <= stop:
                raise ValueError(f'{e}.at: 1〜stopAtの工程番号です。')
            if 'record' in effect and stores.get(effect['record']) != 'records':
                raise ValueError(f'{e}.record: kindがrecordsのstoreを指定してください。')
            if 'send' in effect and stores.get(effect['send']) != 'topic':
                raise ValueError(f'{e}.send: kindがtopicのstoreを指定してください。')
            if 'tag' in effect:
                _text(effect['tag'], f'{e}.tag', limit=24)
            if not {'record', 'send', 'tag'} & effect.keys():
                raise ValueError(f'{e}: record / send / tag のいずれかを指定してください。')
        for j, note in enumerate(sc.get('notes', [])):
            if note.get('store') not in stores:
                raise ValueError(f'{w}.notes[{j}].store: storesのidを指定してください。')
            _text(note.get('text'), f'{w}.notes[{j}].text', limit=24)
            _tone(note.get('tone'), f'{w}.notes[{j}].tone')


def _columns(fig, where):
    cols = fig.get('columns')
    if not isinstance(cols, list) or len(cols) != 2:
        raise ValueError(f'{where}.columns: 2列を指定してください。')
    for c, col in enumerate(cols):
        w = f'{where}.columns[{c}]'
        _text(col.get('title'), f'{w}.title', limit=48)
        _text(col.get('sub'), f'{w}.sub', required=False, limit=80)
        used = set()
        for r, row in enumerate(col.get('rows', [])):
            _text(row.get('key'), f'{w}.rows[{r}].key', limit=28)
            span = row.get('span', 1)
            if not isinstance(row.get('row'), int) or row['row'] < 0 or not isinstance(span, int) or span < 1:
                raise ValueError(f'{w}.rows[{r}]: rowは0以上、spanは1以上の整数です。')
            cells = set(range(row['row'], row['row'] + span))
            if cells & used or max(cells) > 11:
                raise ValueError(f'{w}.rows[{r}]: 行が重なっているか、12行を超えています。')
            used |= cells
            _tone(row.get('tone'), f'{w}.rows[{r}].tone')
        if not used:
            raise ValueError(f'{w}.rows: 1行以上を指定してください。')


def _board(fig, where):
    items = fig.get('items')
    if not isinstance(items, list) or not items:
        raise ValueError(f'{where}.items: 1つ以上の要素を指定してください。')
    for i, item in enumerate(items):
        w = f'{where}.items[{i}]'
        kind = item.get('type')
        if kind in ('panel', 'tile'):
            for name in ('x', 'y', 'w') + (('d',) if kind == 'panel' else ()):
                _number(item, name, w)
            _text(item.get('label'), f'{w}.label', required=kind == 'tile', limit=80)
        elif kind == 'arrow':
            for name in ('from', 'to'):
                if not (isinstance(item.get(name), list) and len(item[name]) == 2 and all(isinstance(v, (int, float)) for v in item[name])):
                    raise ValueError(f'{w}.{name}: [x, y] で指定してください。')
        elif kind == 'text':
            _number(item, 'x', w); _number(item, 'y', w)
            _text(item.get('text'), f'{w}.text', limit=200)
        else:
            raise ValueError(f'{w}.type: panel / tile / arrow / text のいずれかです。')
        _tone(item.get('tone'), f'{w}.tone')


def find_blender():
    """BLENDER環境変数、PATH、macOS / Windowsの標準インストール先の順に探す。"""
    candidates = [os.environ.get('BLENDER'), shutil.which('blender'), '/Applications/Blender.app/Contents/MacOS/Blender',
                  *sorted(glob.glob('C:/Program Files/Blender Foundation/Blender */blender.exe'), reverse=True)]
    for path in candidates:
        if path and Path(path).is_file():
            return path
    raise FileNotFoundError('Blenderが見つかりません。インストールするか、環境変数BLENDERに実行ファイルを指定してください。')


def _inline(value):
    """`code`だけを書式として扱い、それ以外はエスケープする。"""
    parts = re.split(r'`([^`]+)`', value)
    return ''.join(f'<code>{html.escape(p)}</code>' if i % 2 else html.escape(p) for i, p in enumerate(parts))


PAGE_STYLE = '''
:root{--bg:#eef1f5;--surface:#fff;--ink:#1d2433;--muted:#5b6474;--line:#d5dbe4;--accent:#13907e;--code:#e3e8ef;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#141922;--surface:#1c2330;--ink:#e4e8ef;--muted:#9aa4b5;--line:#2e3747;--accent:#3cc4ae;--code:#262f3e;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 "Hiragino Sans","Meiryo",system-ui,sans-serif;padding:40px 16px 72px}
main{max-width:1080px;margin:0 auto;display:grid;gap:56px}header,section{display:grid;gap:16px}h1{font-size:clamp(24px,4vw,32px);line-height:1.35;margin:0}
h2{font-size:21px;margin:0}p{margin:0;max-width:72ch}.meta{font:12.5px/1.6 Menlo,Consolas,monospace;color:var(--muted);display:flex;flex-wrap:wrap;gap:4px 18px}
code{font:.88em Menlo,Consolas,monospace;background:var(--code);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
img,video{width:100%;height:auto;display:block;border-radius:10px;border:1px solid var(--line);background:#eef1f5}img{cursor:zoom-in}
figcaption{font-size:12.5px;color:var(--muted)}figure{margin:0;display:grid;gap:8px}
ul{margin:0;padding:0;list-style:none;display:grid;gap:10px}li{padding:10px 14px;background:var(--surface);border:1px solid var(--line);border-radius:8px}
.tag{display:inline-block;font-size:11px;padding:0 7px;border-radius:99px;margin-right:6px;border:1px solid currentColor;color:var(--accent)}
dialog{border:0;padding:0;background:transparent;max-width:96vw}dialog::backdrop{background:rgb(10 14 20/.8)}dialog img{max-height:92vh;cursor:zoom-out}
'''
PAGE_SCRIPT = '''
const d=document.querySelector('dialog'),z=d.querySelector('img');
document.querySelectorAll('figure img').forEach(i=>i.onclick=()=>{z.src=i.src;z.alt=i.alt;d.showModal()});d.onclick=()=>d.close();
const v=document.querySelector('video');if(v&&!matchMedia('(prefers-reduced-motion: reduce)').matches){v.play().catch(()=>{})}
'''


def page(spec, report):
    """出力フォルダー内のファイルだけを参照する解説ページ。"""
    figures = {f['id']: f for f in report['figures']}
    parts = [f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
             f'<title>{html.escape(spec["title"])}</title><style>{PAGE_STYLE}</style></head><body><main><header>']
    if spec.get('meta'):
        parts.append('<div class="meta">' + ''.join(f'<span>{_inline(m)}</span>' for m in spec['meta']) + '</div>')
    parts.append(f'<h1>{html.escape(spec["title"])}</h1>')
    if spec.get('lead'):
        parts.append(f'<p>{_inline(spec["lead"])}</p>')
    parts.append('</header>')
    for fig in spec['figures']:
        out = figures[fig['id']]
        parts.append(f'<section id="{fig["id"]}"><h2>{_inline(fig["title"])}</h2><figure>')
        if fig['kind'] == 'pipeline':
            parts.append(f'<video src="{out["video"]}" poster="{fig["id"]}-poster.webp" controls muted loop playsinline preload="metadata"></video>')
        else:
            parts.append(f'<img src="{fig["id"]}.webp" alt="{html.escape(fig.get("caption") or fig["title"])}" width="{out["width"]}" height="{out["height"]}">')
        if fig.get('caption'):
            parts.append(f'<figcaption>{_inline(fig["caption"])}</figcaption>')
        parts.append('</figure>')
        parts += [f'<p>{_inline(p)}</p>' for p in fig.get('body', [])]
        if fig.get('points'):
            parts.append('<ul>' + ''.join(f'<li>{"<span class=tag>" + html.escape(p["tag"]) + "</span>" if p.get("tag") else ""}{_inline(p["text"])}</li>'
                                          for p in fig['points']) + '</ul>')
        parts.append('</section>')
    parts.append(f'</main><dialog aria-label="拡大表示"><img alt=""></dialog><script>{PAGE_SCRIPT}</script></body></html>')
    return '\n'.join(parts)


def verify(out, spec):
    """成果物の存在・寸法・動画の全編デコードを確認する。図の意味は判定しない。"""
    import imageio_ffmpeg
    from PIL import Image
    out = Path(out)
    manifest = out / 'delivery.json'
    if manifest.exists():
        manifest.unlink()
    report = json.loads((out / 'render.json').read_text(encoding='utf-8'))
    if [f['id'] for f in report['figures']] != [f['id'] for f in spec['figures']]:
        raise ValueError('描画結果の図が定義と一致しません。')
    files = ['index.html']
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for fig in report['figures']:
        images = [f'{fig["id"]}-poster.webp'] if fig['kind'] == 'pipeline' else [f'{fig["id"]}.webp']
        for name in images:
            with Image.open(out / name) as im:
                if im.size != (fig['width'], fig['height']):
                    raise ValueError(f'{name}の寸法が描画設定と一致しません: {im.size}')
        files += images
        if fig['kind'] == 'pipeline':
            video = out / fig['video']
            decoded = subprocess.run([ffmpeg, '-hide_banner', '-xerror', '-i', str(video), '-map', '0:v:0', '-progress', 'pipe:1', '-nostats', '-f', 'null', '-'],
                                     capture_output=True, text=True)
            (out / f'{fig["id"]}-decode.log').write_text(decoded.stderr, encoding='utf-8')
            if decoded.returncode:
                raise ValueError(f'{fig["video"]}の全編デコードに失敗しました。')
            frames = re.findall(r'^frame=\s*(\d+)$', decoded.stdout, re.M)
            if not frames or int(frames[-1]) != fig['frames']:
                raise ValueError(f'{fig["video"]}のフレーム数が描画設定と一致しません。')
            if f'{fig["width"]}x{fig["height"]}' not in decoded.stderr:
                raise ValueError(f'{fig["video"]}の解像度が描画設定と一致しません。')
            files.append(fig['video'])
    index = (out / 'index.html').read_text(encoding='utf-8')
    missing = [name for name in files[1:] if f'"{name}"' not in index]
    if missing:
        raise ValueError(f'解説ページが参照していない成果物があります: {missing}')
    result = {'status': 'verified', 'quality': report['quality'], 'blender': report['blender'],
              'files': {name: {'bytes': (out / name).stat().st_size, 'sha256': hashlib.sha256((out / name).read_bytes()).hexdigest()} for name in files},
              'checks': ['figures_match_spec', 'image_dimensions', 'video_full_decode', 'video_frame_count', 'video_resolution', 'page_references'],
              'visualReview': '別途記録。自動検証では図の意味・文字の重なりを判定しない。',
              'verifiedAt': datetime.now(timezone.utc).isoformat()}
    manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def build(spec_path, out, draft=False):
    from PIL import Image
    spec = validate(json.loads(Path(spec_path).read_text(encoding='utf-8-sig')))
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'delivery.json').unlink(missing_ok=True)
    source = out / 'spec.json'
    source.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')
    with (out / 'render.log').open('w', encoding='utf-8') as log:
        result = subprocess.run([find_blender(), '-b', '--factory-startup', '-P', str(ROOT / 'diorama_blender.py'), '--',
                                 str(source), str(out), 'draft' if draft else 'final'], stdout=log, stderr=subprocess.STDOUT)
    if result.returncode or not (out / 'render.json').is_file():
        raise RuntimeError(f'Blenderの描画に失敗しました。{out / "render.log"} を確認してください。')
    report = json.loads((out / 'render.json').read_text(encoding='utf-8'))
    for fig in report['figures']:
        png = out / (fig['poster'] if fig['kind'] == 'pipeline' else fig['image'])
        with Image.open(png) as im:
            im.convert('RGB').save(png.with_suffix('.webp'), 'WEBP', lossless=True, method=6)
        png.unlink()
    (out / 'index.html').write_text(page(spec, report), encoding='utf-8')
    return verify(out, spec)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('spec')
    parser.add_argument('--output', required=True)
    parser.add_argument('--draft', action='store_true', help='低解像度・少サンプルで確認用に描画する')
    args = parser.parse_args()
    try:
        delivery = build(args.spec, args.output, args.draft)
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        sys.exit(str(exc))
    print(f'Verified {Path(args.output).resolve() / "index.html"}', flush=True)
