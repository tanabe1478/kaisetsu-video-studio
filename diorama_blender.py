"""Blender内で実行する3D図解の描画。diorama.pyから呼び出す。

blender -b --factory-startup -P diorama_blender.py -- <spec.json> <出力先> <draft|final> [図のID ...]
"""
import json, math, os, sys, unicodedata
from pathlib import Path
import bpy
from mathutils import Vector

TONES = {'ground': '#E4E8EE', 'slab': '#F8F9FB', 'ink': '#1D2433', 'muted': '#5B6474', 'ghost': '#B9C0CC',
         'blue': '#3466D6', 'teal': '#13907E', 'amber': '#D9921C', 'purple': '#7650C4', 'green': '#2C9A57',
         'red': '#D23F3F', 'pink': '#C2366F', 'ball': '#2B3550', 'white': '#FFFFFF'}
QUALITY = {'draft': {'still': ((1280, 720), 16), 'video': ((960, 540), 8)},
           'final': {'still': ((3840, 2160), 128), 'video': ((2560, 1440), 64)}}
TILT = math.radians(44)
FPS = 24


def font_paths():
    """日本語（太字・標準）とコード用。fonts.pyと同じ候補をPillowなしで探す。"""
    def find(folder, *names):
        folder = Path(folder)
        if not folder.is_dir():
            return None
        files = {unicodedata.normalize('NFC', p.name): p for p in folder.iterdir()}
        return next((str(files[n]) for n in names if n in files), None)
    bold = find('/System/Library/Fonts', 'ヒラギノ角ゴシック W6.ttc') or find('C:/Windows/Fonts', 'meiryob.ttc')
    regular = find('/System/Library/Fonts', 'ヒラギノ角ゴシック W4.ttc') or find('C:/Windows/Fonts', 'meiryo.ttc')
    mono = find('/System/Library/Fonts', 'Menlo.ttc') or find('C:/Windows/Fonts', 'consola.ttf')
    if not (bold and regular and mono):
        raise FileNotFoundError('日本語フォント（ヒラギノ／メイリオ）とコード用フォント（Menlo／Consolas）を確認してください。')
    return bold, regular, mono


BOLD, REGULAR, MONO = font_paths()


def rgba(color, alpha=1.0):
    h = TONES.get(color, color).lstrip('#')
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return (*[c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb], alpha)


_materials = {}


def material(color, rough=.55, emit=0.0, alpha=1.0, unique=False):
    key = (color, rough, emit, alpha)
    if key in _materials and not unique:
        return _materials[key]
    m = bpy.data.materials.new(f'm{len(_materials)}')
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = rgba(color)
    bsdf.inputs['Roughness'].default_value = rough
    if emit:
        bsdf.inputs['Emission Color'].default_value = rgba(color)
        bsdf.inputs['Emission Strength'].default_value = emit
    if alpha < 1:
        bsdf.inputs['Alpha'].default_value = alpha
        if hasattr(m, 'surface_render_method'):
            m.surface_render_method = 'BLENDED'
        else:
            m.blend_method = 'BLEND'
    if not unique:
        _materials[key] = m
    return m


def reset(size, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _materials.clear()
    sc = bpy.context.scene
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.filter_size = 1.15  # 既定1.5pxより細い文字をシャープにする
    sc.render.fps = FPS
    sc.eevee.taa_render_samples = samples
    sc.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new('world')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = rgba('#EEF1F5')
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = .55
    sc.world = world
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(40), math.radians(-25), math.radians(20)))
    bpy.context.object.data.energy = 1.6
    bpy.context.object.data.angle = math.radians(8)
    bpy.ops.object.light_add(type='AREA', location=(0, -14, 18), rotation=(math.radians(35), 0, 0))
    bpy.context.object.data.energy = 900
    bpy.context.object.data.size = 25
    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.data.materials.append(material('ground', rough=.9))
    return sc


def camera(center, ortho, dist=40):
    x, y, z = center
    bpy.ops.object.camera_add(location=(x, y - dist * math.sin(TILT), z + dist * math.cos(TILT)), rotation=(TILT, 0, 0))
    cam = bpy.context.object
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = ortho
    cam.data.clip_end = 500
    bpy.context.scene.camera = cam


def box(loc, size, color, bevel=.12, rough=.5, alpha=1.0, emit=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = size
    # 位置は適用しない。アニメーションで動かす箱のメッシュがずれるため。
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('bevel', 'BEVEL')
        mod.width, mod.segments = bevel, 4
    o.data.materials.append(material(color, rough=rough, alpha=alpha, emit=emit))
    bpy.ops.object.shade_smooth()
    return o


def cylinder(loc, radius, height, color, verts=48, rough=.4):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=height, location=(loc[0], loc[1], loc[2] + height / 2))
    o = bpy.context.object
    mod = o.modifiers.new('bevel', 'BEVEL')
    mod.width, mod.segments = .06, 3
    o.data.materials.append(material(color, rough=rough))
    bpy.ops.object.shade_smooth()
    return o


def sphere(loc, radius, color):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=48, ring_count=24)
    o = bpy.context.object
    o.data.materials.append(material(color, rough=.3, unique=True))
    bpy.ops.object.shade_smooth()
    return o


def text(body, loc, size=.5, color='ink', mono=False, bold=True, align='CENTER', flat=False, emit=0.0):
    path = MONO if mono and all(ord(c) < 0x2000 for c in body) else (BOLD if bold else REGULAR)
    bpy.ops.object.text_add(location=loc)
    o = bpy.context.object
    o.data.body = body
    o.data.font = bpy.data.fonts.load(path, check_existing=True)
    o.data.size = size
    o.data.align_x = align
    o.data.align_y = 'CENTER'
    o.data.space_line = 1.1
    o.rotation_euler = (0, 0, 0) if flat else (TILT, 0, 0)
    o.data.materials.append(material(color, rough=.6, emit=emit))
    return o


def arrow(p0, p1, color='muted', width=.12, head=.38, z=.06):
    p0, p1 = Vector((p0[0], p0[1], 0)), Vector((p1[0], p1[1], 0))
    d = p1 - p0
    angle = math.atan2(d.y, d.x)
    shaft = max(d.length - head, .01)
    mid = p0 + d.normalized() * shaft / 2
    box((mid.x, mid.y, z), (shaft, width, width * .6), color, bevel=.02).rotation_euler = (0, 0, angle)
    tip = p1 - d.normalized() * head / 2
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=head * .6, radius2=0, depth=head, location=(tip.x, tip.y, z))
    bpy.context.object.rotation_euler = (0, math.radians(90), angle)
    bpy.context.object.data.materials.append(material(color))


def tile(x, y, w, label, color='slab', ink='ink', d=1.15, h=.36, size=.4, sub=None, sub_ink='muted', align='CENTER', alpha=1.0, mono=True):
    box((x, y, h / 2), (w, d, h), color, bevel=.1, alpha=alpha)
    tx = x if align == 'CENTER' else x - w / 2 + .35
    if sub:
        text(label, (tx, y + .2, h + .01), size, ink, mono=mono, flat=True, align=align)
        text(sub, (tx, y - .3, h + .01), max(size * .85, .31), sub_ink, flat=True, align=align)
    else:
        text(label, (tx, y, h + .01), size, ink, mono=mono, flat=True, align=align)


def fcurves(owner):
    action = owner.animation_data.action
    if hasattr(action, 'fcurves'):
        return action.fcurves
    from bpy_extras import anim_utils
    return anim_utils.action_get_channelbag_for_slot(action, owner.animation_data.action_slot).fcurves


def key(o, path, frame, value):
    setattr(o, path, value)
    o.keyframe_insert(path, frame=frame)


def visible(o, start, end, size=1.0):
    """startからendまで表示する。表示の切り替えは補間しない。"""
    key(o, 'scale', 0, (0, 0, 0))
    key(o, 'scale', start, (size,) * 3)
    if end is not None:
        key(o, 'scale', end, (0, 0, 0))
    for curve in fcurves(o):
        if curve.data_path == 'scale':
            for point in curve.keyframe_points:
                point.interpolation = 'CONSTANT'


def pop(o, frame):
    key(o, 'scale', 0, (0, 0, 0))
    key(o, 'scale', frame - 1, (0, 0, 0))
    key(o, 'scale', frame + 6, (1, 1, 1))


def heading(fig, x, y):
    if fig.get('heading'):
        text(fig['heading'], (x, y, .5), .62, align='LEFT')
    if fig.get('subheading'):
        text(fig['subheading'], (x, y - 1.0, .5), .4, 'muted', align='LEFT')


# ---------------------------------------------------------------- pipeline
SPACING, BALL_Y, BALL_Z, BIN_Y, STORE_Y, MOVE, HOLD, DROP = 4.9, -.35, 1.04, -5.0, 6.4, 13, 4, 18


def pipeline_timeline(fig):
    """シナリオごとの開始フレームと長さ。diorama.pyの検証と同じ計算。"""
    spans, start = [], 1
    for s in fig['scenarios']:
        travel = 6 + s['stopAt'] * (MOVE + HOLD) + (0 if s['result'] == 'ok' else DROP)
        length = travel + s.get('holdFrames', 40)
        spans.append((start, length))
        start += length + 5
    return spans


def pipeline(fig):
    stations, n = fig['stations'], len(fig['stations'])
    xs = [(i - (n - 1) / 2) * SPACING for i in range(n)]
    camera((0, 2.6, 0), n * SPACING + 2.3)
    left = xs[0] - 2.0
    if fig.get('heading'):
        text(fig['heading'], (left, 12.5, 2.2), .62, align='LEFT')
    for i, st in enumerate(stations):
        x = xs[i]
        box((x, 0, .3), (3.9, 2.8, .6), 'slab', bevel=.15)
        box((x, 0, .62), (3.9, 2.8, .06), st.get('tone', 'blue'), bevel=.03, rough=.4)
        text(st['title'], (x, 1.1, 3.0), .6)
        if st.get('sub'):
            text(st['sub'], (x, 1.1, 1.95), .29, 'muted', mono=True)
        if i < n - 1:
            arrow((x + 2.05, 0), (xs[i + 1] - 2.05, 0), 'muted', width=.1, head=.32, z=.08)
        if st.get('error'):
            box((x, -2.6, .04), (.5, 1.4, .06), 'red', bevel=.02, alpha=.55)
            cylinder((x, BIN_Y, 0), 1.15, .5, 'red', rough=.5)
            cylinder((x, BIN_Y, .5), .95, .06, '#F3D4D4')
            text(st['error']['code'], (x, BIN_Y - 1.75, .2), .62, 'red')
            text(st['error'].get('label', ''), (x, BIN_Y - 2.75, .2), .36)
    stores = {}
    for store in fig.get('stores', []):
        x = xs[store['at']]
        tone = store.get('tone', 'purple' if store['kind'] == 'records' else 'pink')
        side = store.get('side', 'left' if store['kind'] == 'records' else 'right')
        if store['kind'] == 'records':
            cylinder((x, STORE_Y, 0), 1.5, .35, tone, rough=.5)
        else:
            cylinder((x, STORE_Y, 0), 1.35, 2.2, tone, verts=6, rough=.35)
        lx, align = (x - 2.0, 'RIGHT') if side == 'left' else (x + 1.9, 'LEFT')
        text(store['title'], (lx, STORE_Y + .3, 1.6), .5, tone, align=align)
        if store.get('sub'):
            text(store['sub'], (lx, STORE_Y + .3, .6), .3, 'muted', align=align)
        stores[store['id']] = {'x': x, 'tone': tone, 'records': 0}

    def record(store, frame):
        st = stores[store]
        disc = cylinder((st['x'], STORE_Y, .35 + st['records'] * .32), 1.2, .26, '#9C82DA')
        st['records'] += 1
        pop(disc, frame)

    def send(store, origin, frame):
        st = stores[store]
        env = box((origin, BALL_Y, BALL_Z), (1.0, .7, .14), '#F7C6D9', bevel=.04, rough=.3)
        key(env, 'scale', 0, (0, 0, 0))
        key(env, 'scale', frame - 1, (0, 0, 0))
        key(env, 'scale', frame + 2, (1, 1, 1))
        key(env, 'location', frame, (origin, BALL_Y, BALL_Z + .4))
        key(env, 'location', frame + 9, ((origin + st['x']) / 2, 2.6, 4.2))
        key(env, 'location', frame + 18, (st['x'], STORE_Y, 2.8))
        key(env, 'scale', frame + 17, (1, 1, 1))
        key(env, 'scale', frame + 21, (0, 0, 0))

    def tag(body, x, start, end):
        visible(text(body, (x, .75, .67), .36, 'white', mono=True, flat=True, emit=.6), start, end)

    for (start, length), sc in zip(pipeline_timeline(fig), fig['scenarios']):
        end = start + length
        ball = sphere((xs[0], BALL_Y, BALL_Z), .5, 'ball')
        color = ball.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color']
        visible(ball, start, end)

        def paint(frame, tone):
            color.default_value = rgba(tone)
            color.keyframe_insert('default_value', frame=frame)
        key(ball, 'location', start, (xs[0], BALL_Y, BALL_Z))
        paint(start, 'ball')
        frame = start + 6
        key(ball, 'location', frame, (xs[0], BALL_Y, BALL_Z))
        for i in range(1, sc['stopAt'] + 1):
            frame += MOVE
            key(ball, 'location', frame, (xs[i], BALL_Y, BALL_Z))
            for effect in sc.get('effects', []):
                if effect['at'] != i:
                    continue
                if 'record' in effect:
                    record(effect['record'], frame)
                if 'send' in effect:
                    send(effect['send'], xs[i], frame)
                if 'tag' in effect:
                    tag(effect['tag'], xs[i], frame, frame + effect.get('frames', 45))
            frame += HOLD
            key(ball, 'location', frame, (xs[i], BALL_Y, BALL_Z))
        if sc['result'] == 'ok':
            paint(frame - HOLD, 'ball')
            paint(frame + 2, 'white')
        else:
            paint(frame, 'ball')
            paint(frame + 4, 'red')
            x = xs[sc['stopAt']]
            key(ball, 'location', frame + 8, (x, -2.6, 1.4))
            key(ball, 'location', frame + DROP, (x, BIN_Y, .95))
        visible(text(sc['caption'], (left, 12.5, .9), .64, align='LEFT'), start, end)
        for note in sc.get('notes', []):
            st = stores[note['store']]
            visible(text(note['text'], (st['x'], STORE_Y + .2, 3.4), .44, note.get('tone', 'ink')), start + 6 + sc['stopAt'] * (MOVE + HOLD), end)
    spans = pipeline_timeline(fig)
    return spans[-1][0] + spans[-1][1]


# ---------------------------------------------------------------- columns
def columns(fig):
    cols = fig['columns']
    rows = max(r['row'] + r.get('span', 1) for c in cols for r in c['rows'])
    step, width = 1.45, 6.6
    top = (rows - 1) * step / 2 + .3
    y = lambda row: top - row * step  # noqa: E731
    sink_y = y(rows - 1) - 3.7 if fig.get('sink') else y(rows - 1) - 1.0
    head_y = top + 6.0
    camera((0, (head_y + sink_y) / 2 - 1.2, 0), fig.get('ortho', 31))
    heading(fig, -15.0, head_y)
    xs = [-6.2, 6.2]
    for x, col in zip(xs, cols):
        text(col['title'], (x, top + 2.9, .3), .42 if len(col['title']) < 34 else .38, col.get('tone', 'ink'), mono=True)
        if col.get('sub'):
            text(col['sub'], (x, top + 2.1, .3), .32, col.get('tone', 'muted'))
        for r in col['rows']:
            span = r.get('span', 1)
            cy = (y(r['row']) + y(r['row'] + span - 1)) / 2
            tone = r.get('tone', 'amber' if r.get('highlight') else 'slab')
            ink = 'white' if tone != 'slab' else 'ink'
            box((x, cy, .18), (width, 1.15 + (span - 1) * step, .36), tone, bevel=.1)
            label_y = cy + (.25 if r.get('sub') else 0)
            text(r['key'], (x - width / 2 + .35, label_y, .37), .4, ink, mono=True, flat=True, align='LEFT')
            if r.get('sub'):
                text(r['sub'], (x - width / 2 + .35, cy - .4, .37), .3, ink, flat=True, align='LEFT')
            if r.get('value'):
                text(r['value'], (x + width / 2 - .35, cy, .37), .34, r.get('valueTone', 'muted'), mono=True, flat=True, align='RIGHT')
    left = {r['key']: r['row'] for r in cols[0]['rows']}
    for r in cols[1]['rows']:
        if left.get(r['key']) == r['row'] and fig.get('link', True):
            box((0, y(r['row']), .1), (xs[1] - xs[0] - width - .4, .08, .06), 'ghost', bevel=0)
            text('=', (0, y(r['row']) + .32, .12), .34, 'muted', flat=True)
    for note in fig.get('notes', []):
        x = xs[note['column']]
        span = note.get('span', 1)
        cy = (y(note['row']) + y(note['row'] + span - 1)) / 2
        right = note.get('side', 'right' if note['column'] else 'left') == 'right'
        edge = x + (width / 2 + .3 if right else -width / 2 - .3)
        if span > 1:
            box((edge, cy, .2), (.08, (span - 1) * step + .9, .06), note.get('tone', 'red'), bevel=0)
        text(note['text'], (edge + (.3 if right else -.3), cy, .3), .36, note.get('textTone', 'ink'), flat=True, align='LEFT' if right else 'RIGHT')
    if fig.get('sink'):
        sink = fig['sink']
        cylinder((0, sink_y, 0), 1.2, 1.6, sink.get('tone', 'pink'), verts=6)
        text(sink['title'], (1.8, sink_y - .8, .3), .42, sink.get('tone', 'pink'), align='LEFT')
        for x, col in zip(xs, cols):
            arrow((x, y(rows - 1) - .9), (x * .21, sink_y + .6), col.get('arrowTone', 'muted'))
    if fig.get('footnote'):
        text(fig['footnote'], (xs[1] + width / 2, y(rows - 1) - 1.0, .1), .32, 'muted', flat=True, align='RIGHT')


# ---------------------------------------------------------------- board
def board(fig):
    cam = fig.get('camera', {})
    camera((*cam.get('center', [0, .3]), 0), cam.get('ortho', 31))
    heading(fig, -15.0, 10.9)
    for item in fig['items']:
        kind = item['type']
        if kind == 'panel':
            box((item['x'], item['y'], .05), (item['w'], item['d'], .1), item.get('tone', '#D9DEE6'), bevel=.05)
            if item.get('label'):
                text(item['label'], (item['x'] - item['w'] / 2 + .4, item['y'] + item['d'] / 2 - .45, .11), .4,
                     item.get('labelTone', 'muted'), mono=item.get('mono', False), flat=True, align='LEFT')
        elif kind == 'tile':
            tile(item['x'], item['y'], item['w'], item['label'], item.get('tone', 'slab'),
                 item.get('ink', 'white' if item.get('tone', 'slab') not in ('slab', 'ghost') else 'ink'),
                 d=item.get('d', 1.15), h=item.get('h', .36), size=item.get('size', .4), sub=item.get('sub'),
                 sub_ink=item.get('subInk', 'white' if item.get('tone', 'slab') not in ('slab', 'ghost') else 'muted'),
                 align=item.get('align', 'CENTER'), alpha=item.get('alpha', 1.0), mono=item.get('mono', True))
        elif kind == 'arrow':
            arrow(item['from'], item['to'], item.get('tone', 'muted'), width=item.get('width', .12), head=item.get('head', .4), z=.15)
        elif kind == 'text':
            text(item['text'], (item['x'], item['y'], .1), item.get('size', .36), item.get('tone', 'ink'),
                 mono=item.get('mono', False), bold=item.get('bold', True), align=item.get('align', 'LEFT'), flat=True)


def render_still(path):
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    spec = json.loads(Path(args[0]).read_text(encoding='utf-8-sig'))
    out, quality, only = Path(args[1]), QUALITY[args[2]], set(args[3:])
    out.mkdir(parents=True, exist_ok=True)
    report = []
    for fig in spec['figures']:
        if only and fig['id'] not in only:
            continue
        if fig['kind'] == 'pipeline':
            size, samples = quality['video']
            sc = reset(size, samples)
            frames = pipeline(fig)
            sc.frame_start, sc.frame_end = 1, frames
            sc.frame_set(fig.get('posterFrame', min(frames, 98)))
            render_still(out / f"{fig['id']}-poster.png")
            if hasattr(sc.render.image_settings, 'media_type'):
                sc.render.image_settings.media_type = 'VIDEO'
            sc.render.image_settings.file_format = 'FFMPEG'
            sc.render.ffmpeg.format, sc.render.ffmpeg.codec = 'MPEG4', 'H264'
            sc.render.ffmpeg.constant_rate_factor = 'HIGH' if args[2] == 'draft' else 'PERC_LOSSLESS'
            sc.render.ffmpeg.ffmpeg_preset = 'GOOD' if args[2] == 'draft' else 'BEST'
            sc.render.filepath = str(out / f"{fig['id']}.mp4")
            bpy.ops.render.render(animation=True)
            report.append({'id': fig['id'], 'kind': 'pipeline', 'video': f"{fig['id']}.mp4", 'poster': f"{fig['id']}-poster.png",
                           'frames': frames, 'fps': FPS, 'width': size[0], 'height': size[1]})
        else:
            size, samples = quality['still']
            reset(size, samples)
            (columns if fig['kind'] == 'columns' else board)(fig)
            render_still(out / f"{fig['id']}.png")
            report.append({'id': fig['id'], 'kind': fig['kind'], 'image': f"{fig['id']}.png", 'width': size[0], 'height': size[1]})
        print(f"diorama: rendered {fig['id']}", flush=True)
    (out / 'render.json').write_text(json.dumps({'blender': bpy.app.version_string, 'quality': args[2], 'figures': report},
                                                ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
