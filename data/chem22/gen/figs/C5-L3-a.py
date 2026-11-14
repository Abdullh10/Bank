# رسوم الدرس 5-3 (مركبات الكربونيل — النصف الأول): الصيغ العامة، وصيغ بنائية للألدهيدات والكيتونات والأحماض الكربوكسيلية
# والإسترات والأميدات، وروابط هيدروجينية مع الماء.
# التشغيل: python3 data/chem22/gen/figs/C5-L3-a.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

U = 50          # وحدة الطول (بين مراكز الذرات) بالبكسل
FS = 19         # حجم خط رموز الذرات
SUB = '₀₁₂₃₄₅₆₇₈₉'
P = 'c5-l3a-'

def lab_size(s, fs=FS):
    if not s: return 0, 0
    w = sum(0.40 * fs if ch in SUB else (0.35 * fs if ch in '′' else 0.66 * fs) for ch in s)
    return w / 2, 0.42 * fs

def mol(nodes, edges, ox=0, oy=0, fs=FS, extra=()):
    """nodes = {id: (x, y, label)} بوحدات U، edges = [(a, b, order)] أو (a, b, 'h') لرابطة هيدروجينية متقطعة.
    extra = [(x1, y1, x2, y2)] خطوط إضافية. يعيد (body, bbox)."""
    Pp = {k: (ox + x * U, oy + y * U, s) for k, (x, y, s) in nodes.items()}
    b = ''
    for a, c, order in edges:
        x1, y1, s1 = Pp[a]; x2, y2, s2 = Pp[c]
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
        def trim(s):
            hw, hh = lab_size(s, fs)
            if not s: return 0
            return min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) + 4
        t1, t2 = trim(s1), trim(s2)
        ax, ay, bx, by = x1 + ux * t1, y1 + uy * t1, x2 - ux * t2, y2 - uy * t2
        if order == 'h':
            b += L(round(ax, 1), round(ay, 1), round(bx, 1), round(by, 1), BLUE, 2.2, '5 5'); continue
        offs = {1: [0], 2: [-3.5, 3.5], 3: [-5, 0, 5]}[order]
        for o in offs:
            b += L(round(ax - uy * o, 1), round(ay + ux * o, 1), round(bx - uy * o, 1), round(by + ux * o, 1), INK, 2)
    xs, ys = [], []
    for k, (x, y, s) in Pp.items():
        hw, hh = lab_size(s, fs)
        if s: b += T(round(x, 1), round(y + 0.36 * fs, 1), s, fs)
        xs += [x - hw, x + hw]; ys += [y - hh, y + hh]
    return b, (min(xs), min(ys), max(xs), max(ys))

# ---------- منشئ صيغة أفقية ----------
def row(items, dx=1.5, orders=None):
    """items: قائمة (label, up, down)؛ up/down = None أو 'X' (رابطة أحادية) أو '=X' (رابطة ثنائية) أو قائمة لسلسلة فرعية.
    orders: رتب الروابط الأفقية بين العناصر المتتالية."""
    nodes, edges = {}, []
    x = 0
    for i, it in enumerate(items):
        lab, up, down = (it + (None, None))[:3] if isinstance(it, tuple) else (it, None, None)
        nodes[f'm{i}'] = (x, 0, lab)
        for d, sub in ((-1, up), (1, down)):
            if not sub: continue
            subs = sub if isinstance(sub, list) else [sub]
            prev = f'm{i}'
            for k, s in enumerate(subs, 1):
                order = 1
                if s.startswith('='): order = 2; s = s[1:]
                nid = f'{i}_{d}_{k}'; nodes[nid] = (x, d * k, s); edges.append((prev, nid, order)); prev = nid
        if i < len(items) - 1:
            edges.append((f'm{i}', f'm{i+1}', (orders or [1] * len(items))[i]))
            nxt = items[i + 1][0] if isinstance(items[i + 1], tuple) else items[i + 1]
            base = dx if (len(lab) > 1 or len(nxt) > 1) else 1.15
            x += max(base, (lab_size(lab)[0] + lab_size(nxt)[0] + 38) / U)
    return nodes, edges

def place(nodes, edges, x0, y0, extra_body=''):
    _, bb = mol(nodes, edges)
    body, bb2 = mol(nodes, edges, x0 - bb[0], y0 - bb[1])
    return body, (bb2[2] - bb2[0], bb2[3] - bb2[1])

def single(name, nodes, edges, pad=26):
    _, bb = mol(nodes, edges)
    bd, _ = mol(nodes, edges, pad - bb[0], pad - bb[1])
    save(name, svg(round(bb[2] - bb[0] + 2 * pad), round(bb[3] - bb[1] + 2 * pad), bd))

def grid(name, items, cols=2, pad=24, gapx=60, gapy=26, label_gap=32):
    """items = [(caption, nodes, edges)] بترتيب (1) في اليمين ثم اليسار."""
    parts = []
    for cap, n, e in items:
        _, bb = mol(n, e); parts.append((cap, n, e, bb))
    cw = max(bb[2] - bb[0] for *_, bb in parts); ch = max(bb[3] - bb[1] for *_, bb in parts)
    rows = (len(parts) + cols - 1) // cols
    body = ''
    for k, (cap, n, e, bb) in enumerate(parts):
        r, c = divmod(k, cols); c = cols - 1 - c
        x0 = pad + c * (cw + gapx); y0 = pad + r * (ch + label_gap + 14 + gapy)
        w = bb[2] - bb[0]; h = bb[3] - bb[1]
        bd, _ = mol(n, e, x0 + (cw - w) / 2 - bb[0], y0 + (ch - h) / 2 - bb[1])
        body += bd + T(round(x0 + cw / 2, 1), round(y0 + ch + label_gap, 1), cap, 17, weight='bold')
    W = pad * 2 + cols * cw + (cols - 1) * gapx; H = pad * 2 + rows * (ch + label_gap + 14) + (rows - 1) * gapy
    for c in range(1, cols):
        xl = pad + c * (cw + gapx) - gapx / 2; body += L(round(xl, 1), pad, round(xl, 1), round(H - pad, 1), MUTED, 1, '4 4')
    for r in range(1, rows):
        yl = pad + r * (ch + label_gap + 14 + gapy) - gapy / 2; body += L(pad, round(yl, 1), round(W - pad, 1), round(yl, 1), MUTED, 1, '4 4')
    save(name, svg(round(W), round(H), body))

def ring6(subs, double_sub=None, circle=False):
    """حلقة سداسية خطية (الرأس 0 في الأعلى ثم مع عقارب الساعة)، subs = {vertex: label}؛ double_sub رأس ترتبط به المجموعة برابطة ثنائية."""
    n = 6; R = 1.0
    V = [(R * math.cos(-math.pi / 2 + 2 * math.pi * i / n), R * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
    nodes = {f'r{i}': (x, y, '') for i, (x, y) in enumerate(V)}
    edges = [(f'r{i}', f'r{(i + 1) % n}', 1) for i in range(n)]
    for i, s in subs.items():
        x, y = V[i]; ux, uy = x / R, y / R
        hw, hh = lab_size(s)
        t = min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) / U
        nodes[f's{i}'] = (x + ux * (0.8 + t), y + uy * (0.8 + t), s)
        edges.append((f'r{i}', f's{i}', 2 if i == double_sub else 1))
    return nodes, edges

# ---------- رسوم ----------
def gen4():
    grid(P + 'gen4.svg', [
        ('(1)',) + row([('R',), ('C', '=O'), ('R′',)], dx=1.2),
        ('(2)',) + row([('R',), ('C', '=O'), ('H',)], dx=1.2),
        ('(3)',) + row([('R',), ('C', '=O'), ('OH',)], dx=1.2),
        ('(4)',) + row([('R',), ('C', '=O'), ('O',), ('R′',)], dx=1.2),
    ])

def gen_aldehyde():
    single(P + 'gen-aldehyde.svg', *row([('R',), ('C', '=O'), ('H',)], dx=1.2))

def butanal():
    single(P + 'butanal.svg', *row([('CH₃',), ('CH₂',), ('CH₂',), ('C', '=O'), ('H',)]))

def pentanone2():
    single(P + 'pentan-2-one.svg', *row([('CH₃',), ('C', '=O'), ('CH₂',), ('CH₂',), ('CH₃',)]))

def hexanoic():
    single(P + 'hexanoic.svg', *row([('CH₃',), ('CH₂',), ('CH₂',), ('CH₂',), ('CH₂',), ('C', '=O'), ('OH',)], dx=1.45))

def methylbutanal():
    single(P + 'methylbutanal.svg', *row([('CH₃',), ('CH', None, 'CH₃'), ('CH₂',), ('C', '=O'), ('H',)]))

def acetone_full():
    single(P + 'acetone-full.svg', *row([('H',), ('C', 'H', 'H'), ('C', '=O'), ('C', 'H', 'H'), ('H',)], dx=1.15))

def name4():
    grid(P + 'name4.svg', [
        ('(1)',) + row([('CH₃',), ('CH₂',), ('C', '=O'), ('H',)]),
        ('(2)',) + row([('CH₃',), ('C', '=O'), ('CH₂',), ('CH₃',)]),
        ('(3)',) + row([('CH₃',), ('CH₂',), ('CH₂',), ('CH₂',), ('C', '=O'), ('OH',)], dx=1.4),
        ('(4)',) + row([('CH₃',), ('CH', None, 'CH₃'), ('C', '=O'), ('H',)]),
    ], gapx=50)

def classes4():
    grid(P + 'classes4.svg', [
        ('(1)',) + row([('CH₃',), ('CH₂',), ('OH',)]),
        ('(2)',) + row([('CH₃',), ('C', '=O'), ('CH₃',)]),
        ('(3)',) + row([('CH₃',), ('O',), ('CH₃',)]),
        ('(4)',) + row([('CH₃',), ('C', '=O'), ('H',)]),
    ])

def q13():
    """أربع مركبات كربونيل مختلفة الأنواع (إستر، أميد، كيتون حلقي، ألدهيد)."""
    ester = row([('CH₃',), ('CH₂',), ('O',), ('C', '=O'), ('CH₃',)])
    amide = row([('CH₃',), ('CH₂',), ('CH₂',), ('C', '=O'), ('NH₂',)])
    keto = ring6({0: 'O'}, double_sub=0)
    ald = row([('CH₃',), ('CH₂',), ('CH₂',), ('C', '=O'), ('H',)])
    grid(P + 'q13.svg', [('(1)',) + ester, ('(2)',) + amide, ('(3)',) + keto, ('(4)',) + ald], gapx=50)

def butanoic_full():
    single(P + 'butanoic-full.svg', *row([('H',), ('C', 'H', 'H'), ('C', 'H', 'H'), ('C', 'H', 'H'), ('C', '=O'), ('OH',)], dx=1.25))

def butanamide():
    single(P + 'butanamide.svg', *row([('NH₂',), ('C', '=O'), ('CH₂',), ('CH₂',), ('CH₃',)]))

def propyl_ethanoate():
    single(P + 'propyl-ethanoate.svg', *row([('CH₃',), ('C', '=O'), ('O',), ('CH₂',), ('CH₂',), ('CH₃',)]))

def ethyl_butanoate():
    single(P + 'ethyl-butanoate.svg', *row([('CH₃',), ('CH₂',), ('CH₂',), ('C', '=O'), ('O',), ('CH₂',), ('CH₃',)]))

def methanal():
    single(P + 'methanal.svg', *row([('H',), ('C', '=O'), ('H',)], dx=1.2))

def vanillin():
    n, e = ring6({2: 'O', 3: 'OH'})
    # مجموعة الألدهيد على الرأس 0: C ثم O (رابطة ثنائية) وH
    n['c'] = (0, -1.0 - 1.0, 'C'); e.append(('r0', 'c', 1))
    n['o'] = (-0.87, -2.5, 'O'); e.append(('c', 'o', 2))
    n['h'] = (0.87, -2.5, 'H'); e.append(('c', 'h', 1))
    # مجموعة الميثوكسي: O على الرأس 2 ثم CH₃
    x2, y2, _ = n['s2']; n['me'] = (x2 + 1.2, y2, 'CH₃'); e.append(('s2', 'me', 1))
    body, bb = mol(n, e)
    pad = 26
    bd, _ = mol(n, e, pad - bb[0], pad - bb[1])
    cx, cy = pad - bb[0], pad - bb[1]
    bd += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.6 * U:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
    save(P + 'vanillin.svg', svg(round(bb[2] - bb[0] + 2 * pad), round(bb[3] - bb[1] + 2 * pad), bd))

def acetone_water():
    """جزيء أسيتون (2-بروبانون) وجزيئا ماء مرتبطان بروابط هيدروجينية مع أكسجين الكربونيل."""
    n, e = row([('CH₃',), ('C', '=O'), ('CH₃',)])
    # O عند (1.5, -1)
    a = math.radians(52)
    for k, (hx, sign) in enumerate(((0.55, -1), (2.45, 1))):
        # H المرتبطة بالأكسجين ثم أكسجين الماء ثم H الثانية
        hy = -1.9
        n[f'wh{k}'] = (hx, hy, 'H'); e.append(('1_-1_1', f'wh{k}', 'h'))
        ox_, oy_ = hx + sign * 0.55, hy - 0.75
        n[f'wo{k}'] = (ox_, oy_, 'O'); e.append((f'wo{k}', f'wh{k}', 1))
        n[f'wh2{k}'] = (ox_ + sign * 0.95, oy_ + 0.05, 'H'); e.append((f'wo{k}', f'wh2{k}', 1))
    single(P + 'acetone-water.svg', n, e)

def ethanal_ethanol():
    grid(P + 'ethanal-ethanol.svg', [
        ('(1)',) + row([('H',), ('C', 'H', 'H'), ('C', '=O'), ('H',)], dx=1.15),
        ('(2)',) + row([('H',), ('C', 'H', 'H'), ('C', 'H', 'H'), ('O',), ('H',)], dx=1.15),
    ], gapx=70)

def lactic_propanoic():
    grid(P + 'lactic-propanoic.svg', [
        ('(1)',) + row([('CH₃',), ('CH₂',), ('C', '=O'), ('OH',)]),
        ('(2)',) + row([('CH₃',), ('CH', None, 'OH'), ('C', '=O'), ('OH',)]),
    ], gapx=70)

def fruit_esters():
    grid(P + 'fruit-esters.svg', [
        ('(1)',) + row([('CH₃(CH₂)₄',), ('C', '=O'), ('O',), ('CH₃',)], dx=1.5),
        ('(2)',) + row([('CH₃CH₂CH₂',), ('C', '=O'), ('O',), ('CH₂CH₃',)], dx=1.5),
    ], cols=1, gapy=20)

if __name__ == '__main__':
    gen4(); gen_aldehyde(); butanal(); pentanone2(); hexanoic(); methylbutanal(); acetone_full(); name4()
    classes4(); q13(); butanoic_full(); butanamide(); propyl_ethanoate(); ethyl_butanoate(); methanal(); vanillin()
    acetone_water(); ethanal_ethanol(); lactic_propanoic(); fruit_esters()
