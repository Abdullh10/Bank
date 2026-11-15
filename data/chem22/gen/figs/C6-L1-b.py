# رسوم الدرس 6-1 (ب) — البروتينات: منحنى نشاط الإنزيم مع درجة الحرارة، والشكل الحلزوني والصحيفة المطوية،
# ومناطق طي سلسلة بروتين، وببتيد خماسي وسلسلة سداسية لحساب التتابعات، وأحماض أمينية لتصنيف السلاسل الجانبية،
# وبروتين كروي في الماء.
# التشغيل: python3 data/chem22/gen/figs/C6-L1-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('c6l1a', os.path.join(os.path.dirname(__file__), 'C6-L1-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
Mol, backbone, sc_label, sc_chain, sc_val, caption, tag, LAT, GX, GY = (
    A.Mol, A.backbone, A.sc_label, A.sc_chain, A.sc_val, A.caption, A.tag, A.LAT, A.GX, A.GY)

P = 'c6-l1b-'
BROWN = '#8a5a00'


def finish(name, m, w, h, extra=''):
    save(name, svg(w, h, m.body + extra))


# ---------- سلاسل جانبية إضافية ----------
def sc_gln():
    """الجلوتامين: CH2–CH2–C(=O)–NH2"""
    def f(m, c, r):
        k = f'q{c}{r}'
        m.atom(k + '1', c, r - 1, 'CH2', 0); m.atom(k + '2', c, r - 2, 'CH2', 0); m.bond(k + '1', k + '2')
        m.atom(k + 'C', c, r - 3, 'C'); m.bond(k + '2', k + 'C')
        m.atom(k + 'O', c - 0.8, r - 3.8, 'O'); m.bond(k + 'C', k + 'O', 2)
        m.atom(k + 'N', c + 0.8, r - 3.8, 'NH2', 0); m.bond(k + 'C', k + 'N')
        return k + '1'
    return f


def benzene_alt(m, cx, cy, r, start_deg, skip_inner=()):
    """سداسي برؤوس عند start_deg + 60k، مع ثلاث روابط ثنائية داخلية متناوبة. يُعيد قائمة الرؤوس."""
    pts = [(cx + r * math.cos(math.radians(start_deg + 60 * k)), cy + r * math.sin(math.radians(start_deg + 60 * k))) for k in range(6)]
    for k in range(6):
        (x1, y1), (x2, y2) = pts[k], pts[(k + 1) % 6]
        m.body += L(f'{x1:.1f}', f'{y1:.1f}', f'{x2:.1f}', f'{y2:.1f}', INK, 2.4)
        if k % 2 == 0 and k not in skip_inner:
            # خط داخلي موازٍ (مقصّر)
            ix1 = x1 + (cx - x1) * 0.2; iy1 = y1 + (cy - y1) * 0.2
            ix2 = x2 + (cx - x2) * 0.2; iy2 = y2 + (cy - y2) * 0.2
            dx, dy = ix2 - ix1, iy2 - iy1
            ix1 += dx * 0.12; iy1 += dy * 0.12; ix2 -= dx * 0.12; iy2 -= dy * 0.12
            m.body += L(f'{ix1:.1f}', f'{iy1:.1f}', f'{ix2:.1f}', f'{iy2:.1f}', INK, 2.2)
    return pts


def sc_tyr():
    """التيروسين: CH2 ثم حلقة بنزين وفي رأسها العلوي OH"""
    def f(m, c, r):
        k = f't{c}{r}'
        m.atom(k + '1', c, r - 1, 'CH2', 0)
        x, y = m.pos(c, r - 1)
        R = 34; cy = y - 13 - 26 - R
        pts = benzene_alt(m, x, cy, R, 30)   # رأس سفلي عند 90° ورأس علوي عند 270°
        bx, by = pts[1]   # 90°
        m.vertex(k + 'v', bx, by); m.bond(k + '1', k + 'v')
        tx, ty = pts[4]   # 270°
        m.vertex(k + 'top', tx, ty)
        m.atoms[k + 'OH'] = (tx, ty - 46, 6, 30, True)
        m.body += A.ftext(tx - 6 - 7, ty - 46, 'OH', m.size)
        m.bond(k + 'top', k + 'OH')
        return k + '1'
    return f


def sc_trp():
    """التريبتوفان: CH2 ثم حلقة خماسية فيها NH ملتحمة بحلقة بنزين (كما في الشكل 6-24)."""
    def f(m, c, r):
        k = f'w{c}{r}'
        m.atom(k + '1', c, r - 1, 'CH2', 0)
        x, y = m.pos(c, r - 1)
        rp = 36
        C3 = (x, y - 13 - 30)                       # رأس الخماسي السفلي
        cx, cy = C3[0], C3[1] - rp
        ang = [90, 162, 234, 306, 18]               # C3, C3a, C7a, N1, C2
        V = [(cx + rp * math.cos(math.radians(a)), cy + rp * math.sin(math.radians(a))) for a in ang]
        C3, C3a, C7a, N1, C2 = V
        # روابط الخماسي (عدا C3a–C7a التي يرسمها البنزين)
        def ln(p, q, w=2.4): m.body += L(f'{p[0]:.1f}', f'{p[1]:.1f}', f'{q[0]:.1f}', f'{q[1]:.1f}', INK, w)
        def short(p, q, t=0.0, s=0.0):
            dx, dy = q[0] - p[0], q[1] - p[1]
            return (p[0] + dx * t, p[1] + dy * t), (q[0] - dx * s, q[1] - dy * s)
        ln(C3, C3a)
        a, b = short(C7a, N1, 0, 0.32); ln(a, b)
        a, b = short(N1, C2, 0.32, 0); ln(a, b)
        ln(C2, C3)
        # رابطة ثنائية C2=C3 (خط داخلي)
        ix1 = C2[0] + (cx - C2[0]) * 0.22; iy1 = C2[1] + (cy - C2[1]) * 0.22
        ix2 = C3[0] + (cx - C3[0]) * 0.22; iy2 = C3[1] + (cy - C3[1]) * 0.22
        ln((ix1 + (ix2 - ix1) * 0.12, iy1 + (iy2 - iy1) * 0.12), (ix2 - (ix2 - ix1) * 0.12, iy2 - (iy2 - iy1) * 0.12), 2.2)
        m.body += A.ftext(N1[0] - 7, N1[1], 'NH', m.size)
        # البنزين على الضلع C3a–C7a من الجهة اليسرى
        mx, my = (C3a[0] + C7a[0]) / 2, (C3a[1] + C7a[1]) / 2
        e = math.hypot(C7a[0] - C3a[0], C7a[1] - C3a[1])
        nx, ny = mx - cx, my - cy; nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
        hx, hy = mx + nx * e * math.sqrt(3) / 2, my + ny * e * math.sqrt(3) / 2
        st = math.degrees(math.atan2(C3a[1] - hy, C3a[0] - hx))
        # الرأس 0 = C3a، الرأس 5 = C7a (الضلع 5 هو المشترك)
        pts = [(hx + e * math.cos(math.radians(st + 60 * j)), hy + e * math.sin(math.radians(st + 60 * j))) for j in range(6)]
        if math.hypot(pts[1][0] - C7a[0], pts[1][1] - C7a[1]) < 1:  # الاتجاه المعاكس
            pts = [(hx + e * math.cos(math.radians(st - 60 * j)), hy + e * math.sin(math.radians(st - 60 * j))) for j in range(6)]
        for j in range(6):
            p, q = pts[j], pts[(j + 1) % 6]; ln(p, q)
        # روابط ثنائية داخلية على الأضلاع 0–1، 2–3، 4–5
        for j in (0, 2, 4):
            p, q = pts[j], pts[(j + 1) % 6]
            i1 = (p[0] + (hx - p[0]) * 0.2, p[1] + (hy - p[1]) * 0.2); i2 = (q[0] + (hx - q[0]) * 0.2, q[1] + (hy - q[1]) * 0.2)
            d = (i2[0] - i1[0], i2[1] - i1[1])
            ln((i1[0] + d[0] * 0.12, i1[1] + d[1] * 0.12), (i2[0] - d[0] * 0.12, i2[1] - d[1] * 0.12), 2.2)
        m.vertex(k + 'v', C3[0], C3[1]); m.bond(k + '1', k + 'v')
        return k + '1'
    return f


def axes(x0, y0, x1, y1):
    return ARROW(x0, y0, x1, y0) + ARROW(x0, y0, x0, y1)


def main():
    os.makedirs(OUT, exist_ok=True)

    # 1) سرعة التفاعل المحفز بإنزيم مقابل درجة الحرارة (0–60 °C)، مع مناطق A وB وC
    x0, y0, W, H = 90, 300, 520, 230
    def X(t): return x0 + t / 60 * W
    def Y(v): return y0 - v * H
    s = axes(x0, y0, x0 + W + 30, y0 - H - 30)
    for t in range(0, 61, 10):
        s += L(X(t), y0, X(t), y0 + 6, INK, 1.5) + T(X(t), y0 + 26, str(t), 16)
    s += T(x0 + W / 2, y0 + 56, 'درجة الحرارة (\u2066°C\u2069)', 18, weight='bold')
    s += f'<text transform="translate({x0 - 30},{y0 - H / 2}) rotate(-90)" text-anchor="middle" font-size="18" fill="{INK}" font-weight="bold" {FONT}>سرعة التفاعل</text>'
    pts = []
    for i in range(0, 121):
        t = i * 0.5
        if t <= 38: v = 0.06 + 0.94 * (math.sin(math.pi / 2 * t / 38) ** 1.6)
        else: v = math.cos(math.pi / 2 * (t - 38) / 22) ** 1.3 if t < 60 else 0
        pts.append((X(t), Y(v)))
    s += '<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" stroke="{BLUE}" stroke-width="4"/>'
    s += L(X(38), Y(1), X(38), y0, MUTED, 1.5, '5 4')
    s += tag(X(18), Y(0.62) - 30, 'A', INK) + tag(X(38), Y(1) - 26, 'B', INK) + tag(X(53) + 30, Y(0.45) - 10, 'C', INK)
    save(P + 'enzyme-temp.svg', svg(680, 380, s))

    # 2) الشكل الحلزوني: لولب (الجزء الخلفي فاتح) مع روابط هيدروجينية متقطعة بين لفات متتالية
    s = ''
    n = 4.5; x0 = 80; Lh = 540; amp = 70; cy = 150; per = Lh / n
    N = 600
    def hp(i):
        ph = 2 * math.pi * n * i / N
        return (x0 + Lh * i / N + 48 * math.sin(ph), cy + amp * math.cos(ph)), ph
    runs = []   # مقاطع متصلة: (أمامي؟، نقاط)
    for i in range(N + 1):
        p, ph = hp(i); front = math.sin(ph) >= 0
        if runs and runs[-1][0] == front: runs[-1][1].append(p)
        else:
            if runs: runs[-1][1].append(p)
            runs.append((front, [p]))
    def pl(pts, col, w): return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
    for front, pts in runs:
        if not front: s += pl(pts, '#eab3ac', 9)
    for k in range(int(n)):
        ph0 = 2 * math.pi * (k + (0.18 if k % 2 == 0 else 0.32))
        i0 = ph0 / (2 * math.pi * n) * N
        (xa, ya), _ = hp(i0); (xb, yb), _ = hp(i0 + N / n)
        s += L(f'{xa + 8:.1f}', f'{ya:.1f}', f'{xb - 8:.1f}', f'{yb:.1f}', BLUE, 2.2, '4 4')
    for front, pts in runs:
        if front: s += pl(pts, '#fff', 16) + pl(pts, RED, 10)
    save(P + 'helix.svg', svg(700, 300, s))

    # 3) الصحيفة المطوية بالذرات: ثلاثة أجزاء متجاورة من السلسلة نفسها، تتصل بانعطافين، وروابط هيدروجينية N–H···O=C
    m = Mol(0, 0, 20)
    s = ''
    rows = [90, 250, 410]; NI = 12; dx = 62; xL = 120
    # نرمز إلى Cα بـ 'C ' لتمييزه عن الكربون الكربونيلي ثم نضيف R يدويًا
    def strand2(ri, up_even, order):
        for i in range(NI):
            x = xL + i * dx; up = (i % 2 == 0) == up_even
            y = rows[ri] + (-14 if up else 14)
            key = f'r{ri}a{i}'; kind = order[i % 3]
            m.atoms[key] = (x, y, 8, 8, True)
            m.body += A.ftext(x - (8 if kind == 'N' else 7), y, 'N' if kind == 'N' else 'C', 20)
            if i: m.bond(f'r{ri}a{i - 1}', key)
            dy = -44 if up else 44; sk = key + 's'
            if kind == 'N':
                m.atoms[sk] = (x, y + dy, 8, 8, True); m.body += A.ftext(x - 7, y + dy, 'H', 20); m.bond(key, sk)
            elif kind == 'CO':
                m.atoms[sk] = (x, y + dy, 8, 8, True); m.body += A.ftext(x - 8, y + dy, 'O', 20); m.bond(key, sk, 2)
            else:
                m.atoms[sk] = (x, y + dy, 8, 8, True); m.body += A.ftext(x - 7, y + dy, 'R', 20, BROWN); m.bond(key, sk, 1, BROWN, 2)
    strand2(0, True, ['N', 'CA', 'CO'])
    strand2(1, False, ['CO', 'CA', 'N'])
    strand2(2, True, ['N', 'CA', 'CO'])
    # روابط هيدروجينية بين الصفين 0 و1 (المواقع الفردية) وبين الصفين 1 و2 (المواقع الزوجية)
    for ra, rb, par in ((0, 1, 1), (1, 2, 0)):
        for i in range(par, NI, 2):
            ka, kb = f'r{ra}a{i}s', f'r{rb}a{i}s'
            xa_, ya_ = m.atoms[ka][:2]; xb_, yb_ = m.atoms[kb][:2]
            # فقط أزواج N–H···O=C (نتجاوز أزواج R)
            if (i % 3) == 1: continue
            s += L(f'{xa_:.1f}', f'{ya_ + 13:.1f}', f'{xb_:.1f}', f'{yb_ - 13:.1f}', BLUE, 2.2, '4 4')
    xr = xL + (NI - 1) * dx
    s += f'<path d="M{xr + 12},{rows[0] + 14} C{xr + 110},{rows[0] + 14} {xr + 110},{rows[1] - 14} {xr + 12},{rows[1] - 14}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    s += f'<path d="M{xL - 12},{rows[1] + 14} C{xL - 110},{rows[1] + 14} {xL - 110},{rows[2] - 14} {xL - 12},{rows[2] - 14}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    s += L(xL - 70, rows[0] - 14, xL - 12, rows[0] - 14, INK, 2.4)
    s += ARROW(xr + 12, rows[2] + 14, xr + 75, rows[2] + 14, INK, 2.4)
    finish(P + 'sheet.svg', m, xr + 140, 500, s)

    # 4) سلسلة بروتين فيها مناطق مرقمة: (1) حلزونان، (2) صحيفة مطوية، (3) لفّة غير منتظمة
    s = ''
    def coil(xa, ya, xb, yb, turns=4, amp=22, col=RED):
        out = []
        for i in range(161):
            t = i / 160; ph = 2 * math.pi * turns * t
            x = xa + (xb - xa) * t; y = ya + (yb - ya) * t
            dx, dy = xb - xa, yb - ya; ln = math.hypot(dx, dy); nx, ny = -dy / ln, dx / ln
            out.append((x + nx * amp * math.sin(ph) + dx / ln * 8 * math.cos(ph), y + ny * amp * math.sin(ph) + dy / ln * 8 * math.cos(ph)))
        return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in out)}" fill="none" stroke="{col}" stroke-width="6" stroke-linejoin="round"/>'
    def broad(xa, y, xb, col=BROWN):
        d = 1 if xb > xa else -1; hw = 11; head = 26
        xs_ = xb - d * head
        return (f'<polygon points="{xa},{y - hw} {xs_},{y - hw} {xs_},{y - hw - 9} {xb},{y} {xs_},{y + hw + 9} {xs_},{y + hw} {xa},{y + hw}" '
                f'fill="#e3c08a" stroke="{col}" stroke-width="2.2"/>')
    # المسار: بداية ← حلزون 1 ← وصلة ← صحيفة (3 أشرطة) ← لفة غير منتظمة ← حلزون 2 ← نهاية
    s += f'<path d="M40,250 L70,250" stroke="{INK}" stroke-width="4" fill="none"/>'
    s += coil(70, 250, 250, 250, 4.5)
    s += f'<path d="M250,250 C268,250 266,200 266,165 S285,120 330,120" stroke="{INK}" stroke-width="4" fill="none"/>'
    s += broad(330, 120, 520)
    s += f'<path d="M520,120 C560,120 560,170 520,170" stroke="{INK}" stroke-width="4" fill="none"/>'
    s += broad(520, 170, 330)
    s += f'<path d="M330,170 C290,170 290,220 330,220" stroke="{INK}" stroke-width="4" fill="none"/>'
    s += broad(330, 220, 520)
    for yy in (132, 182):
        for xx in range(355, 500, 30):
            s += L(xx, yy + 1, xx, yy + 25, BLUE, 1.8, '3 3')
    s += (f'<path d="M520,220 C600,220 560,300 620,320 S700,250 660,220 S600,330 700,360 C740,372 760,330 780,330" '
          f'stroke="{INK}" stroke-width="4" fill="none" stroke-linejoin="round"/>')
    s += coil(780, 330, 950, 210, 4)
    s += f'<path d="M950,210 L985,190" stroke="{INK}" stroke-width="4" fill="none"/>'
    s += caption(160, 320, '(1)', 22) + caption(425, 88, '(2)', 22) + caption(640, 395, '(3)', 22) + caption(965, 285, '(1)', 22)
    save(P + 'regions.svg', svg(1020, 420, s))

    # 5) ببتيد خماسي: Val–Gly–Ser–Ala–Cys
    m = Mol(55, 200)
    backbone(m, 0, 0, pre='a', cterm=False, side=sc_val())
    backbone(m, 3, 0, pre='b', nleft='HN', cterm=False, side=sc_label('H'))
    backbone(m, 6, 0, pre='c', nleft='HN', cterm=False, side=sc_chain(['CH2', 'OH']))
    backbone(m, 9, 0, pre='d', nleft='HN', cterm=False, side=sc_label('CH3', 0))
    backbone(m, 12, 0, pre='e', nleft='HN', cterm=True, side=sc_chain(['CH2', 'SH']))
    m.bond('aC', 'bN'); m.bond('bC', 'cN'); m.bond('cC', 'dN'); m.bond('dC', 'eN')
    finish(P + 'pentapeptide.svg', m, 1100, 290)

    # 6) سلسلة من ستة مواقع فارغة «؟» بين طرفي الأمين والكربوكسيل
    s = ''
    xs6 = [170 + i * 95 for i in range(6)]
    for a, b in zip(xs6, xs6[1:]): s += L(a + 32, 100, b - 32, 100, INK, 3)
    for x in xs6:
        s += f'<circle cx="{x}" cy="100" r="32" fill="#eef3fa" stroke="{BLUE}" stroke-width="2.5"/>'
        s += f'<text x="{x}" y="111" text-anchor="middle" font-size="30" fill="{BLUE}" {LAT}>?</text>'
    s += L(xs6[0] - 32, 100, xs6[0] - 58, 100, INK, 3) + A.ftext(55, 100, 'H2N', 24)
    s += L(xs6[-1] + 32, 100, xs6[-1] + 58, 100, INK, 3) + A.ftext(xs6[-1] + 64, 100, 'COOH', 24)
    save(P + 'beads6.svg', svg(860, 190, s))

    # 7) الجلوتامين، 8) التيروسين، 9) التريبتوفان (كلٌّ وحده، دون اسم)
    for nm, side, oy, h in [('glutamine', sc_gln(), 290, 390), ('tyrosine', sc_tyr(), 290, 390), ('tryptophan', sc_trp(), 290, 390)]:
        m = Mol(60, oy); backbone(m, 0, 0, side=side)
        finish(P + nm + '.svg', m, 340, h)

    # 10) أربعة أحماض أمينية مرقمة: ألانين، سيستين، جلوتامين، لايسين
    m = Mol(0, 0); parts = ''
    specs = [('(1)', sc_label('CH3', 0)), ('(2)', sc_chain(['CH2', 'SH'])), ('(3)', sc_gln()),
             ('(4)', sc_chain(['CH2', 'CH2', 'CH2', 'CH2', 'NH2']))]
    for i, (lab, side) in enumerate(specs):
        m.ox = 55 + i * 290; m.oy = 370
        backbone(m, 0, 0, pre=f'a{i}', side=side)
        x, y = m.pos(1.5, 0)
        parts += caption(x, y + 110, lab, 22)
    finish(P + 'aa-four.svg', m, 1170, 510, parts)

    # 11) بروتين كروي في الماء: سلسلة مطوية، سلاسل جانبية ● متجهة إلى الداخل و○ على السطح، وجزيئات ماء حوله
    s = ''
    cx, cy = 300, 230
    s += f'<ellipse cx="{cx}" cy="{cy}" rx="165" ry="140" fill="#fbf3e4" stroke="#e3c08a" stroke-width="2" stroke-dasharray="6 4"/>'
    way = [(150, 170), (215, 115), (300, 100), (385, 118), (440, 180), (440, 260), (395, 325), (310, 350), (225, 330),
           (165, 280), (215, 230), (270, 180), (340, 175), (375, 235), (330, 290), (265, 280), (255, 230)]
    def catmull(p):
        d = f'M{p[0][0]},{p[0][1]}'
        for i in range(len(p) - 1):
            p0 = p[i - 1] if i else p[i]; p1 = p[i]; p2 = p[i + 1]; p3 = p[i + 2] if i + 2 < len(p) else p[i + 1]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]},{p2[1]}'
        return d
    # الخارج: من نقاط الحلقة الخارجية (0–9) إلى الخارج
    for (x, y) in way[:10]:
        ux, uy = x - cx, y - cy; l = math.hypot(ux, uy); ux, uy = ux / l, uy / l
        ex, ey = x + ux * 34, y + uy * 34
        s += L(x, y, f'{ex:.1f}', f'{ey:.1f}', INK, 2.5)
        s += f'<circle cx="{ex + ux * 10:.1f}" cy="{ey + uy * 10:.1f}" r="11" fill="#fff" stroke="{INK}" stroke-width="2.5"/>'
    # الداخل: من النقاط الداخلية (10–16) نحو المركز
    for (x, y) in way[10:]:
        ux, uy = cx - x, cy - y; l = math.hypot(ux, uy) or 1; ux, uy = ux / l, uy / l
        ex, ey = x + ux * 22, y + uy * 22
        s += L(x, y, f'{ex:.1f}', f'{ey:.1f}', INK, 2.5)
        s += f'<circle cx="{ex + ux * 8:.1f}" cy="{ey + uy * 8:.1f}" r="10" fill="{INK}"/>'
    s += f'<path d="{catmull(way)}" fill="none" stroke="{BLUE}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
    for k in range(12):
        a = 2 * math.pi * k / 12 + 0.25
        x = cx + 235 * math.cos(a); y = cy + 200 * math.sin(a)
        s += A.ftext(x - 22, y, 'H2O', 18, MUTED)
    # مفتاح
    s += f'<circle cx="790" cy="170" r="10" fill="{INK}"/>' + T(768, 177, 'سلسلة جانبية من النوع X', 18, anchor='end')
    s += f'<circle cx="790" cy="230" r="11" fill="#fff" stroke="{INK}" stroke-width="2.5"/>' + T(768, 237, 'سلسلة جانبية من النوع Y', 18, anchor='end')
    s += L(770, 290, 810, 290, BLUE, 6) + T(752, 297, 'سلسلة عديد الببتيد', 18, anchor='end')
    save(P + 'globular.svg', svg(830, 470, s))

if __name__ == '__main__':
    main()
