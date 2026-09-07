"""Shared local fonts for Windows and macOS rendering."""
from functools import lru_cache
from pathlib import Path
from PIL import ImageFont


@lru_cache(maxsize=64)
def font(size, code=False):
    candidates = ([Path('C:/Windows/Fonts/consola.ttf'), Path('/System/Library/Fonts/Menlo.ttc')]
                  if code else [Path('C:/Windows/Fonts/meiryob.ttc'),
                                *sorted(Path('/System/Library/Fonts').glob('*角*W6.ttc'))])
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    raise FileNotFoundError('日本語フォント（メイリオ／ヒラギノ）、コード用フォント（Consolas／Menlo）を確認してください。')
