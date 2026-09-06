"""Build compact selection previews from the same PSD layers as the renderer."""
from studio import ROOT, EXPRESSIONS, POSES, PSDImage, select, child, Image

def build():
    dest=ROOT/'assets'/'previews';dest.mkdir(parents=True,exist_ok=True)
    psd=None
    for expression,(eyes,brow) in EXPRESSIONS.items():
        for pose,(right,left) in POSES.items():
            target=dest/f'{expression}-{pose}.png'
            if target.exists():continue
            cached=ROOT/'assets'/'sprites'/f'{expression}-{pose}-0-0.png'
            if cached.exists():im=Image.open(cached).convert('RGBA')
            else:
                if psd is None:
                    source=next((ROOT/'assets'/'original').rglob('*.psd'),None)
                    if source is None:raise ValueError('立ち絵PSDが見つかりません。')
                    psd=PSDImage.open(source)
                select(child(psd,'!眉'),brow);select(child(psd,'!目'),eyes)
                select(child(psd,'!口'),'*むふ');clothes=child(psd,'*服装1')
                select(child(clothes,'!右腕'),right);select(child(clothes,'!左腕'),left)
                im=psd.composite(force=True).crop((140,60,990,1620))
            im.resize((255,468),Image.Resampling.LANCZOS).save(target)
            print(target.name,flush=True)

if __name__=='__main__':build()
