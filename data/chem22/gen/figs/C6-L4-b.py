# رسوم الدرس 6-4 (الأحماض النووية) — النصف الثاني: زوج قواعد بروابطه الهيدروجينية، وقطعة DNA فيها زوج غير متطابق،
# ونيوكليوتيد جوانين بسكر الرايبوز، ونموذج اللولب المزدوج، وشوكة تضاعف DNA مرقمة.
# التشغيل: python3 data/chem22/gen/figs/C6-L4-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('c6l4a', os.path.join(os.path.dirname(__file__), 'C6-L4-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
mol, U, pent, phos, BASE_COL, DX, tag = A.mol, A.U, A.pent, A.phos, A.BASE_COL, A.DX, A.tag

P_ = 'c6-l4b-'

# ---------- زوج قواعد تخطيطي ----------
def poly(pts, fill, stroke=INK):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'

def hexagon(cx, cy, r):
    return [(cx + r * math.cos(math.radians(30 + 60 * i)), cy + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)]

def fig_pair(name, n_hb):
    """قاعدة ذات حلقتين (يمين) تقابل قاعدة ذات حلقة واحدة (يسار) بعدد n_hb من الروابط الهيدروجينية (خطوط متقطعة)."""
    r = 40
    # الحلقة الواحدة (يسار)
    lx, ly = 150, 120
    b = poly(hexagon(lx, ly, r), '#fde8c8')
    # الحلقتان (يمين): سداسية + خماسية ملتصقة من اليمين
    rx, ry = 330, 120
    hx = hexagon(rx, ry, r)
    b += poly(hx, '#d6e6f5')
    # الضلع الأيمن للسداسية بين الرأسين (30°) و(-30°)
    p1 = (rx + r * math.cos(math.radians(30)), ry + r * math.sin(math.radians(30)))
    p2 = (rx + r * math.cos(math.radians(-30)), ry + r * math.sin(math.radians(-30)))
    s = math.dist(p1, p2); R = s / (2 * math.sin(math.radians(36)))
    cx5 = p1[0] + R * math.cos(math.radians(18)); cy5 = ry
    pent_pts = [(cx5 + R * math.cos(math.radians(180 + 72 * i)), cy5 + R * math.sin(math.radians(180 + 72 * i))) for i in range(5)]
    b += poly(pent_pts, '#d6e6f5')
    # الروابط الهيدروجينية بين الحلقتين
    xa, xb = lx + r * 0.866 + 6, rx - r * 0.866 - 6
    ys = {2: [ry - 14, ry + 14], 3: [ry - 26, ry, ry + 26]}[n_hb]
    for y in ys:
        b += L(round(xa, 1), y, round(xb, 1), y, RED, 2.2, '5 4')
    # السكر (ديوكسي رايبوز) لكل قاعدة
    b += L(lx - r * 0.866, ly + 20, lx - 85, ly + 70, INK, 2) + pent(lx - 95, ly + 80, 16)
    b += T(lx - 95, ly + 118, 'ديوكسي رايبوز', 14)
    b += L(rx, ry + r, rx, ry + r + 30, INK, 2) + pent(rx, ry + r + 42, 16)
    b += T(rx, ry + r + 80, 'ديوكسي رايبوز', 14)
    # مفتاح
    b += L(330, 24, 370, 24, RED, 2.2, '5 4') + T(325, 29, 'رابطة هيدروجينية', 14, 'end')
    save(name, svg(470, 260, b))

# ---------- قطعة DNA مرقمة الأزواج ----------
def fig_numbered_ladder(name, top, bottom):
    x0, ytop = 60, 50
    b = A.ladder_body(x0, ytop, top, bottom)
    yb = ytop + 140
    for i in range(len(top)):
        b += T(x0 + i * DX, yb + 42, f'({i + 1})', 16, weight='bold', color=MUTED)
    W = x0 + DX * (len(top) - 1) + 60
    save(name, svg(W, yb + 58, b))

# ---------- نيوكليوتيد جوانين ----------
def purine_G(ox, oy):
    """الجوانين؛ N9 عند (ox, oy) بوحدات طول الرابطة."""
    R5 = 0.8507
    c4 = (0, 0); c5 = (0, -1)
    cen5 = (-0.688, -0.5)
    v = lambda a: (cen5[0] + R5 * math.cos(math.radians(a)), cen5[1] + R5 * math.sin(math.radians(a)))
    n9, c8, n7 = v(108), v(180), v(252)
    hexc = (0.866, -0.5)
    c6 = (0.866, -1.5); n1 = (1.732, -1); c2 = (1.732, 0); n3 = (0.866, 0.5)
    pts = {'C4': c4, 'C5': c5, 'N9': n9, 'C8': c8, 'N7': n7, 'C6': c6, 'N1': n1, 'C2': c2, 'N3': n3,
           'O6': (0.866, -2.5), 'H1': (2.598, -1.5), 'N2': (2.598, 0.5), 'H8': (c8[0] - 1, c8[1])}
    lab = {'C4': '', 'C5': '', 'N9': 'N', 'C8': '', 'N7': 'N', 'C6': '', 'N1': 'N', 'C2': '', 'N3': 'N',
           'O6': 'O', 'H1': 'H', 'N2': 'NH₂', 'H8': 'H'}
    dx, dy = ox - n9[0], oy - n9[1]
    n = {k: (x + dx, y + dy, lab[k]) for k, (x, y) in pts.items()}
    e = [('N1', 'C2', 1), ('C2', 'N3', 2), ('N3', 'C4', 1), ('C4', 'C5', 2), ('C5', 'C6', 1), ('C6', 'N1', 1), ('C6', 'O6', 2),
         ('N1', 'H1', 1), ('C2', 'N2', 1), ('C5', 'N7', 1), ('N7', 'C8', 2), ('C8', 'N9', 1), ('N9', 'C4', 1), ('C8', 'H8', 1)]
    return n, e

def fig_g_ribonucleotide(name):
    n = {'P': (0, 0, 'P'), 'Od': (0, -1, 'O'), 'HO': (-1.25, 0, 'HO'), 'OH': (0, 1, 'OH'), 'Ob': (1.15, 0, 'O'), 'CH2': (2.35, 0, 'CH₂'),
         'C4': (3.0, 0.9, ''), 'Or': (4.1, 0.35, 'O'), 'C1': (5.2, 0.9, ''), 'C2': (4.8, 2.05, ''), 'C3': (3.4, 2.05, ''),
         'O3': (3.4, 3.05, 'OH'), 'X2': (4.8, 3.05, 'OH')}
    e = [('P', 'Od', 2), ('P', 'HO', 1), ('P', 'OH', 1), ('P', 'Ob', 1), ('Ob', 'CH2', 1), ('CH2', 'C4', 1),
         ('C4', 'Or', 1), ('Or', 'C1', 1), ('C1', 'C2', 1), ('C2', 'C3', 1), ('C3', 'C4', 1), ('C3', 'O3', 1), ('C2', 'X2', 1)]
    gn, ge = purine_G(5.75, 0.05)
    n.update({'g' + k: v for k, v in gn.items()}); e += [('g' + a, 'g' + c, o) for a, c, o in ge]
    e.append(('C1', 'gN9', 1))
    ox, oy = 90, 200
    b, bb = mol(n, e, ox, oy)
    W = round(bb[2] + 30); H = round(bb[3] + 25)
    b = b.replace('<g>', '')
    save(name, svg(W, H, b))
    return bb

# ---------- اللولب المزدوج ----------
def fig_helix(name):
    W, H = 300, 470
    cx, amp, top, bot = 150, 85, 30, 440
    per = 205
    def xa(y, ph): return cx + amp * math.sin(2 * math.pi * (y - top) / per + ph)
    b = ''
    cols = ['#2e8b57', '#c0392b', '#2a6fb0', '#d68910']
    pairs = []
    y = top + 12
    k = 0
    while y < bot - 5:
        x1, x2 = xa(y, 0), xa(y, math.pi)
        if abs(x1 - x2) > 22:
            m = (x1 + x2) / 2
            c1, c2 = (cols[k % 4], cols[(k % 4) ^ 1])
            b += L(round(x1, 1), round(y, 1), round(m, 1), round(y, 1), c1, 7) + L(round(m, 1), round(y, 1), round(x2, 1), round(y, 1), c2, 7)
            k += 1
        y += 16
    for ph, col in ((0, '#7f8c9d'), (math.pi, '#5d6d7e')):
        pts = ' '.join(f'{xa(yy, ph):.1f},{yy}' for yy in range(top, bot + 1, 4))
        b += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="11" stroke-linecap="round"/>'
    save(name, svg(W, H, b))

# ---------- شوكة التضاعف ----------
NEW_SUGAR = '#9ecbff'

def unit(x, y, base, down, sugar_fill='#f4d35e'):
    b = pent(x, y, fill=sugar_fill)
    y1, y2 = (y + 13, y + 63) if down else (y - 63, y - 13)
    col = BASE_COL.get(base, '#9aa3ad')
    b += f'<rect x="{x - 15}" y="{y1}" width="30" height="{y2 - y1}" rx="4" fill="{col}" fill-opacity="0.22" stroke="{col}" stroke-width="2"/>'
    b += T(x, (y1 + y2) / 2 + 7, base, 19, color=INK, weight='bold')
    return b

def backbone(pts, color=INK):
    b = f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{color}" stroke-width="2.5"/>'
    for (xa_, ya), (xb, yb) in zip(pts, pts[1:]):
        b += phos((xa_ + xb) / 2, (ya + yb) / 2)
    return b

def fig_fork(name):
    top = 'GATCCATG'
    comp = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    bot = ''.join(comp[c] for c in top)
    x0 = 110; N = len(top)
    xs = [x0 + i * DX for i in range(N)]
    yt, yb1, yb2, yn = 40, 180, 445, 300
    b = ''
    # الشريط الأصلي العلوي (كامل)
    b += backbone([(xs[0] - DX / 2, yt)] + [(x, yt) for x in xs] + [(xs[-1] + DX / 2, yt)])
    for x, s in zip(xs, top): b += unit(x, yt, s, True)
    # الشريط الأصلي السفلي: مزدوج مع العلوي في الأعمدة 0–2 ثم ينفصل إلى الأسفل
    ybot = [yb1] * 3 + [yb2] * 5
    b += backbone([(xs[0] - DX / 2, yb1)] + [(x, yb1) for x in xs[:3]] + [(xs[3] - DX / 2, yb2)] + [(x, yb2) for x in xs[3:]] + [(xs[-1] + DX / 2, yb2)])
    for x, y, s in zip(xs, ybot, bot): b += unit(x, y, s, False)
    for i in range(3):
        x = xs[i]
        b += L(x - 7, yt + 66, x - 7, yb1 - 66, MUTED, 1.4, '3 3') + L(x + 7, yt + 66, x + 7, yb1 - 66, MUTED, 1.4, '3 3')
    # شريط جديد يُبنى مقابل الشريط السفلي المنفصل (الأعمدة 5–7)
    b += backbone([(xs[5], yn), (xs[6], yn), (xs[7], yn), (xs[7] + DX / 2, yn)], BLUE)
    for i in (5, 6, 7):
        b += unit(xs[i], yn, top[i], True, NEW_SUGAR)
        x = xs[i]
        b += L(x - 7, yn + 66, x - 7, yb2 - 66, MUTED, 1.4, '3 3') + L(x + 7, yn + 66, x + 7, yb2 - 66, MUTED, 1.4, '3 3')
    # نيوكليوتيدات حرة غير مرتبطة بعد قرب القواعد المكشوفة في الشريط العلوي
    for i in (4, 6):
        x = xs[i] - 10; y = 215
        b += unit(x, y, comp[top[i]], False, NEW_SUGAR) + L(x + 13, y, x + 24, y, BLUE, 2) + phos(x + 32, y)
    # الأرقام
    b += tag(x0 - 70, (yt + yb1) / 2, '1')
    b += tag(xs[3], 150, '2')
    b += tag(xs[-1] + DX / 2 + 32, yn, '3')
    # مفتاح
    ky = 500
    b += pent(x0 - 40, ky, fill='#f4d35e') + T(x0 - 20, ky + 5, 'نيوكليوتيدات الشريطين الأصليين', 14, 'start')
    b += pent(x0 + 270, ky, fill=NEW_SUGAR) + T(x0 + 290, ky + 5, 'نيوكليوتيدات حرة أو جديدة', 14, 'start')
    W = xs[-1] + DX / 2 + 60
    save(name, svg(round(W), 520, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig_pair(P_ + 'pair3.svg', 3)
    fig_numbered_ladder(P_ + 'mismatch.svg', 'GACTCA', 'CTGCGT')
    fig_g_ribonucleotide(P_ + 'g-ribo-nt.svg')
    fig_helix(P_ + 'helix.svg')
    fig_fork(P_ + 'fork.svg')
