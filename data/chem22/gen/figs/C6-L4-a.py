# رسوم الدرس 6-4 (الأحماض النووية) — النصف الأول: نيوكليوتيدات بصيغ بنائية، وسكر الرايبوز والديوكسي رايبوز،
# والثايمين واليوراسيل، ومخططات تخطيطية لأشرطة DNA وRNA (سكر خماسي = مخمس، فوسفات = دائرة، قاعدة = مستطيل بحرفها).
# التشغيل: python3 data/chem22/gen/figs/C6-L4-a.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

U = 48          # طول الرابطة بالبكسل
FS = 18
SUB = '₀₁₂₃₄₅₆₇₈₉⁺⁻'
P_ = 'c6-l4a-'

def lab_size(s, fs=FS):
    if not s: return 0, 0
    w = sum(0.40 * fs if ch in SUB else 0.66 * fs for ch in s)
    return w / 2, 0.42 * fs

def mol(nodes, edges, ox=0, oy=0, fs=FS):
    """nodes = {id: (x, y, label)} بوحدات طول الرابطة؛ label فارغ = رأس صيغة خطية. edges = [(a, b, order)]."""
    P = {k: (ox + x * U, oy + y * U, s) for k, (x, y, s) in nodes.items()}
    b = ''
    for a, c, order in edges:
        x1, y1, s1 = P[a]; x2, y2, s2 = P[c]
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
        def trim(s):
            if not s: return 0
            hw, hh = lab_size(s, fs)
            return min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) + 4
        t1, t2 = trim(s1), trim(s2)
        ax, ay, bx, by = x1 + ux * t1, y1 + uy * t1, x2 - ux * t2, y2 - uy * t2
        offs = {1: [0], 2: [-3.5, 3.5]}[order]
        for o in offs:
            b += L(round(ax - uy * o, 1), round(ay + ux * o, 1), round(bx - uy * o, 1), round(by + ux * o, 1), INK, 2)
    xs, ys = [], []
    for k, (x, y, s) in P.items():
        hw, hh = lab_size(s, fs)
        if s: b += T(round(x, 1), round(y + 0.36 * fs, 1), s, fs)
        xs += [x - hw, x + hw]; ys += [y - hh, y + hh]
    return b, (min(xs), min(ys), max(xs), max(ys))

def tag(x, y, s, color=RED):
    return f'<circle cx="{x}" cy="{y}" r="14" fill="#fff" stroke="{color}" stroke-width="2"/>' + T(x, y + 6, s, 16, color=color, weight='bold')

# ---------- البنى ----------
def base_ring(kind, cx, cy, attach='N1'):
    """قاعدة أحادية الحلقة (C سايتوسين، T ثايمين، U يوراسيل) — N1 عند الزاوية 150°."""
    ang = {'N1': 150, 'C2': 210, 'N3': 270, 'C4': 330, 'C5': 30, 'C6': 90}
    V = {k: (cx + math.cos(math.radians(a)), cy + math.sin(math.radians(a))) for k, a in ang.items()}
    out = lambda k, r=1.0: (cx + 2 * math.cos(math.radians(ang[k])) * r if False else V[k][0] + math.cos(math.radians(ang[k])) * r,
                            V[k][1] + math.sin(math.radians(ang[k])) * r)
    n = {'N1': (*V['N1'], 'N'), 'C2': (*V['C2'], ''), 'N3': (*V['N3'], 'N'), 'C4': (*V['C4'], ''), 'C5': (*V['C5'], ''), 'C6': (*V['C6'], '')}
    e = [('N1', 'C2', 1), ('C5', 'C6', 2), ('C6', 'N1', 1)]
    n['O2'] = (*out('C2'), 'O'); e.append(('C2', 'O2', 2))
    n['H6'] = (*out('C6'), 'H'); e.append(('C6', 'H6', 1))
    if kind == 'C':
        e += [('C2', 'N3', 1), ('N3', 'C4', 2), ('C4', 'C5', 1)]
        n['X4'] = (*out('C4'), 'NH₂'); e.append(('C4', 'X4', 1))
        n['X5'] = (*out('C5'), 'H'); e.append(('C5', 'X5', 1))
    else:
        e += [('C2', 'N3', 1), ('N3', 'C4', 1), ('C4', 'C5', 1)]
        n['H3'] = (*out('N3'), 'H'); e.append(('N3', 'H3', 1))
        n['X4'] = (*out('C4'), 'O'); e.append(('C4', 'X4', 2))
        n['X5'] = (*out('C5', 1.15 if kind == 'T' else 1.0), 'CH₃' if kind == 'T' else 'H'); e.append(('C5', 'X5', 1))
    if attach is None:
        n['H1'] = (*out('N1'), 'H'); e.append(('N1', 'H1', 1))
    return n, e

def nucleotide(sugar, base):
    """فوسفات – CH₂ – سكر خماسي (deoxy/ribo) – قاعدة أحادية الحلقة."""
    n = {'P': (0, 0, 'P'), 'Od': (0, -1, 'O'), 'HO': (-1.25, 0, 'HO'), 'OH': (0, 1, 'OH'), 'Ob': (1.15, 0, 'O'), 'CH2': (2.35, 0, 'CH₂'),
         'C4': (3.0, 0.9, ''), 'Or': (4.1, 0.35, 'O'), 'C1': (5.2, 0.9, ''), 'C2': (4.8, 2.05, ''), 'C3': (3.4, 2.05, ''),
         'O3': (3.4, 3.05, 'OH'), 'X2': (4.8, 3.05, 'OH' if sugar == 'ribo' else 'H')}
    e = [('P', 'Od', 2), ('P', 'HO', 1), ('P', 'OH', 1), ('P', 'Ob', 1), ('Ob', 'CH2', 1), ('CH2', 'C4', 1),
         ('C4', 'Or', 1), ('Or', 'C1', 1), ('C1', 'C2', 1), ('C2', 'C3', 1), ('C3', 'C4', 1), ('C3', 'O3', 1), ('C2', 'X2', 1)]
    bn, be = base_ring(base, 6.87, -0.2)
    n.update({'b' + k: v for k, v in bn.items()}); e += [('b' + a, 'b' + c, o) for a, c, o in be]
    e.append(('C1', 'bN1', 1))
    return n, e

def fig_nucleotide(name, sugar, base, letters):
    """letters = (للفوسفات، للسكر، للقاعدة) — حروف فقط دون أسماء الأجزاء."""
    n, e = nucleotide(sugar, base)
    ox, oy = 110, 175
    b, bb = mol(n, e, ox, oy)
    px, py = ox + 0 * U, oy + 0 * U
    sx, sy = ox + 4.1 * U, oy + 1.3 * U
    bx, by = ox + 6.87 * U, oy - 0.2 * U
    b += L(px - 30, py + 70, px - 10, py + 22, RED, 1.5) + tag(px - 36, py + 84, letters[0])
    b += L(ox + 2.25 * U, oy + 2.0 * U, ox + 3.1 * U, oy + 1.55 * U, RED, 1.5) + tag(ox + 2.25 * U - 12, oy + 2.0 * U + 8, letters[1])
    b += L(ox + 7.85 * U, by, ox + 9.3 * U, by, RED, 1.5) + tag(ox + 9.3 * U + 14, by, letters[2])
    W = round(ox + 9.3 * U + 50); H = round(oy + 3.05 * U + 40)
    save(name, svg(W, H, b))

def sugar_ring(kind):
    n = {'C4': (-1.2, 0.5, ''), 'O': (0, -0.1, 'O'), 'C1': (1.2, 0.5, ''), 'C2': (0.75, 1.7, ''), 'C3': (-0.75, 1.7, ''),
         'C5': (-2.2, -0.1, 'HOCH₂'), 'O1': (2.25, -0.05, 'OH'), 'O3': (-0.75, 2.75, 'OH'), 'X2': (0.75, 2.75, 'OH' if kind == 'ribo' else 'H')}
    e = [('C4', 'O', 1), ('O', 'C1', 1), ('C1', 'C2', 1), ('C2', 'C3', 1), ('C3', 'C4', 1), ('C4', 'C5', 1), ('C1', 'O1', 1),
         ('C3', 'O3', 1), ('C2', 'X2', 1)]
    return n, e

def two_panels(name, left, right, caps, note=None):
    """left/right = (nodes, edges)؛ caps = (عنوان الأيمن، عنوان الأيسر)."""
    parts = []
    for ne in (left, right):
        _, bb = mol(*ne); parts.append(bb)
    hmax = max(bb[3] - bb[1] for bb in parts)
    pad, gap = 30, 90; top = pad
    x = pad; body = ''; centers = []
    for ne, bb in zip((left, right), parts):
        w = bb[2] - bb[0]
        bd, _ = mol(*ne, x - bb[0], top + (hmax - (bb[3] - bb[1])) / 2 - bb[1]); body += bd
        centers.append(x + w / 2); x += w + gap
    W = x - gap + pad
    yc = top + hmax + 38
    body += T(round(centers[0], 1), yc, caps[1], 18, weight='bold') + T(round(centers[1], 1), yc, caps[0], 18, weight='bold')
    body += L(round((centers[0] + centers[1]) / 2, 1), 15, round((centers[0] + centers[1]) / 2, 1), yc + 5, MUTED, 1, '4 4')
    H = yc + 20
    if note: body += T(round(W / 2, 1), H + 8, note, 14, color=MUTED); H += 26
    save(name, svg(round(W), round(H), body))

# ---------- مخطط تخطيطي للأشرطة ----------
BASE_COL = {'A': '#2e8b57', 'T': '#c0392b', 'G': '#2a6fb0', 'C': '#d68910', 'U': '#7d3c98', '؟': '#9aa3ad'}
DX = 64

def pent(cx, cy, r=13, fill='#f4d35e'):
    pts = ' '.join(f'{cx + r * math.cos(math.radians(-90 + 72 * i)):.1f},{cy + r * math.sin(math.radians(-90 + 72 * i)):.1f}' for i in range(5))
    return f'<polygon points="{pts}" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>'

def phos(cx, cy, r=9):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#a8d5a2" stroke="{INK}" stroke-width="1.5"/>'

def strand(x0, y, seq, down=True, hb=None, gap_to=None):
    """شريط: سكريات (مخمسات) عند y، تتعاقب مع الفوسفات بينها، والقواعد مستطيلات تتجه للأسفل (down) أو للأعلى."""
    b = ''
    xs = [x0 + i * DX for i in range(len(seq))]
    b += L(xs[0] - DX / 2, y, xs[-1] + DX / 2, y, INK, 2.5)
    for i, x in enumerate(xs):
        b += pent(x, y)
        b += phos(x + DX / 2, y)
    b += phos(xs[0] - DX / 2, y)
    for x, s in zip(xs, seq):
        y1, y2 = (y + 13, y + 63) if down else (y - 63, y - 13)
        col = BASE_COL.get(s, '#9aa3ad')
        b += f'<rect x="{x - 15}" y="{y1}" width="30" height="{y2 - y1}" rx="4" fill="{col}" fill-opacity="0.22" stroke="{col}" stroke-width="2"/>'
        b += T(x, (y1 + y2) / 2 + 7, s, 19, color=INK, weight='bold')
    return b

def ladder_body(x0, ytop, top, bottom, hb=True):
    b = strand(x0, ytop, top, True)
    if bottom is not None:
        yb = ytop + 140
        b += strand(x0, yb, bottom, False)
        if hb:
            for i in range(len(top)):
                x = x0 + i * DX
                b += L(x - 7, ytop + 66, x - 7, yb - 66, MUTED, 1.4, '3 3') + L(x + 7, ytop + 66, x + 7, yb - 66, MUTED, 1.4, '3 3')
    return b

def fig_ladder(name, top, bottom, side=None, extra=''):
    """side = (نص الشريط العلوي، نص الشريط السفلي) يُكتب يمين الشكل."""
    x0 = 60; ytop = 50
    W = x0 + DX * (len(top) - 1) + 60 + (120 if side else 0)
    H = ytop + (140 if bottom is not None else 63) + 35
    b = ladder_body(x0, ytop, top, bottom)
    if side:
        xs = x0 + DX * (len(top) - 1) + 55
        b += T(xs, ytop + 6, side[0], 16, 'start', weight='bold')
        if bottom is not None: b += T(xs, ytop + 146, side[1], 16, 'start', weight='bold')
    b += extra
    save(name, svg(W, H, b))

def fig_dna_parts(name):
    top, bottom = 'ATGCAT', 'TACGTA'
    x0, ytop = 110, 55; yb = ytop + 140
    b = ladder_body(x0, ytop, top, bottom)
    W = x0 + DX * 5 + 70; H = yb + 60
    # 1: العمود الفقري (العلوي والسفلي)، 2: أزواج القواعد في الداخل
    b += L(x0 - 50, ytop - 10, x0 - DX / 2 - 9, ytop, RED, 1.5) + tag(x0 - 62, ytop - 16, '1')
    b += L(x0 - 50, yb + 10, x0 - DX / 2 - 9, yb, RED, 1.5) + tag(x0 - 62, yb + 16, '1')
    b += L(x0 - 50, (ytop + yb) / 2, x0 - 16, (ytop + yb) / 2, RED, 1.5) + tag(x0 - 64, (ytop + yb) / 2, '2')
    save(name, svg(W, H, b))

def fig_xy(name):
    """جزيئان: X شريطان (مع T)، وY شريط مفرد (مع U)."""
    x0 = 60
    bx = ladder_body(x0, 50, 'ATGC', 'TACG')
    yy = 50
    by = strand(x0 + DX * 4 + 120, yy, 'AUGC', True)
    W = x0 + DX * 4 + 120 + DX * 3 + 60
    b = bx + by
    b += T(x0 + DX * 1.5, 280, '(X)', 20, weight='bold') + T(x0 + DX * 4 + 120 + DX * 1.5, 280, '(Y)', 20, weight='bold')
    b += L(x0 + DX * 3 + 60, 20, x0 + DX * 3 + 60, 285, MUTED, 1, '4 4')
    save(name, svg(W, 300, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_nucleotide(P_ + 'nt-deoxy-c.svg', 'deoxy', 'C', ('A', 'B', 'C'))
    fig_nucleotide(P_ + 'nt-ribo-u.svg', 'ribo', 'U', ('X', 'Y', 'Z'))
    two_panels(P_ + 'sugars.svg', sugar_ring('deoxy'), sugar_ring('ribo'), ('(1)', '(2)'))
    two_panels(P_ + 'bases-tu.svg', base_ring('U', 0, 0, attach=None), base_ring('T', 0, 0, attach=None), ('(X)', '(Y)'))
    fig_dna_parts(P_ + 'dna-parts.svg')
    fig_ladder(P_ + 'dna-unknown.svg', 'TAGCGA', 'ATC؟CT')
    fig_ladder(P_ + 'rna-strand.svg', 'AUGCUAG', None)
    fig_xy(P_ + 'xy-strands.svg')
    fig_ladder(P_ + 'template.svg', 'ATCGGT', '؟؟؟؟؟؟', side=('الشريط القالب', 'الشريط الجديد'))
    fig_ladder(P_ + 'replication.svg', 'ATCGGT', 'TAGCCA')
    fig_ladder(P_ + 'transcribe.svg', 'TACGGA', '؟؟؟؟؟؟', side=('شريط DNA', 'شريط RNA'))
