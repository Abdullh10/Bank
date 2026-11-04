# رسوم أسئلة الدرس 2-1 (الجزء ب: الأهداف O07–O11). التشغيل: python3 data/chem22/gen/figs/C2-L1-b.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *

PURPLE = '#6a4c93'; ORANGE = '#d98c1f'; DARK = '#333a44'; ORED = '#c0392b'; NBLUE = '#3d7cc9'

def TH(x, y, s, size=14, anchor='middle', color=INK, weight='normal'):
    """نص بهالة بيضاء ليبقى مقروءًا فوق الخطوط."""
    t = T(x, y, s, size, anchor, color, weight)
    return t.replace('<text ', '<text stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round" ', 1)

def circ_num(x, y, n, color=INK):
    return f'<circle cx="{x:.0f}" cy="{y:.0f}" r="11" fill="#fff" stroke="{color}" stroke-width="1.8"/>' + T(x, y + 5, str(n), 13, color=color, weight='bold')

def _geom(ox, oy, w, h, vmin, vmax, top=42):
    X0, X1, Yt, Yb = ox + 75, ox + w - 18, oy + top, oy + h - 48
    W = X1 - X0
    def y(v): return Yb - (v - vmin) / (vmax - vmin) * (Yb - Yt)
    return X0, X1, Yt, Yb, W, y

def _path(X0, W, yr, ypk, yp, color=BLUE, width=3.5):
    a, b, pk, c, d = X0 + 0.03 * W, X0 + 0.22 * W, X0 + 0.48 * W, X0 + 0.74 * W, X0 + 0.97 * W
    k = 0.13 * W
    return (f'<path d="M{a:.1f},{yr:.1f} L{b:.1f},{yr:.1f} C{b + k:.1f},{yr:.1f} {pk - k:.1f},{ypk:.1f} {pk:.1f},{ypk:.1f} '
            f'C{pk + k:.1f},{ypk:.1f} {c - k:.1f},{yp:.1f} {c:.1f},{yp:.1f} L{d:.1f},{yp:.1f}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')

def reaction_profile(r, pk, p, vmin=0, vmax=None, ox=0, oy=0, w=520, h=330, react='المتفاعلات', prod='النواتج',
                     complex_='المعقد المنشط', arrows=(), ticks=None, guides=False, axis='الطاقة', xlabel='سير التفاعل', title=None, prod_pos='below', caption=None, react_pos='above'):
    """مخطط طاقة تفاعل من خطوة واحدة (يعيد جسم SVG).
    arrows: [(kind, label, color)] و kind ∈ 'ea' (من المتفاعلات إلى القمة)، 'ear' (من النواتج إلى القمة)، 'dh' (من المتفاعلات إلى النواتج).
    label نص، أو عدد صحيح فيُرسم رقمًا داخل دائرة. ticks: قيم تدريج محور الطاقة (kJ)."""
    if vmax is None: vmax = pk * 1.12
    X0, X1, Yt, Yb, W, y = _geom(ox, oy, w, h, vmin, vmax, 72 if caption else 42)
    yr, ypk, yp = y(r), y(pk), y(p)
    pkx, bx, cx = X0 + 0.48 * W, X0 + 0.22 * W, X0 + 0.74 * W
    b = ARROW(X0, Yb, X0, Yt - 12) + ARROW(X0, Yb, X1, Yb)
    b += f'<text transform="translate({X0 - (48 if ticks else 14)},{(Yt + Yb) / 2}) rotate(-90)" text-anchor="middle" font-size="15" fill="{INK}" font-weight="bold" {FONT}>{esc(axis + (" (kJ)" if ticks else ""))}</text>'
    b += T((X0 + X1) / 2, Yb + 30, xlabel, 14, weight='bold')
    if ticks:
        for t in ticks:
            b += L(X0 - 5, y(t), X0, y(t)) + T(X0 - 9, y(t) + 5, str(t), 12, 'end')
    if guides:
        for v, xe in ((r, bx), (pk, pkx), (p, cx)):
            b += L(X0, y(v), xe, y(v), MUTED, 1, '3 4')
    b += _path(X0, W, yr, ypk, yp)
    b += TH(X0 + 0.04 * W, yr - 10 if react_pos == 'above' else yr + 22, react, 14, 'start')
    b += TH(X0 + 0.86 * W, yp + 22 if prod_pos == 'below' else yp - 10, prod, 14)
    if caption: b += T(ox + w / 2, oy + 42, caption, 14, color=MUTED, weight='bold')
    if complex_: b += TH(pkx, ypk - 12, complex_, 14)
    for kind, lab, col in arrows:
        if kind == 'ea':
            x = pkx - 0.035 * W
            b += L(bx, yr, x + 8, yr, MUTED, 1.2, '4 4') + ARROW(x, yr, x, ypk + 3, col)
            lx, ly, anc = x - 8, (yr + ypk) / 2 + 5, 'end'
        elif kind == 'ear':
            x = pkx + 0.035 * W
            b += L(x - 8, yp, cx, yp, MUTED, 1.2, '4 4') + ARROW(x, yp, x, ypk + 3, col)
            lx, ly, anc = x + 8, (yp + ypk) / 2 + 5, 'start'
        else:
            x = X0 + 0.80 * W
            b += L(bx, yr, x + 10, yr, MUTED, 1.2, '4 4') + ARROW(x, yr, x, yp + (3 if p < r else -3), col)
            lx, ly, anc = x + 8, (yr + yp) / 2 + 5, 'start'
        if isinstance(lab, int):
            b += circ_num(lx + (-12 if anc == 'end' else 12), ly - 5, lab, col)
        else:
            b += TH(lx, ly, lab, 14, anc, col, 'bold')
    if title: b += T(ox + w / 2, oy + 20, title, 16, weight='bold')
    return b

def profile_file(name, *a, w=520, h=330, **k):
    save(name, svg(w, h, reaction_profile(*a, w=w, h=h, **k)))

def three_curves(name, r, p, peaks, w=520, h=330, vmax=None):
    """ثلاثة تفاعلات لها مستوى المتفاعلات نفسه ومستوى النواتج نفسه وقمم مختلفة. peaks = [(label, pk, color)]"""
    vmax = vmax or max(v for _, v, _ in peaks) * 1.12
    X0, X1, Yt, Yb, W, y = _geom(0, 0, w, h, 0, vmax)
    b = ARROW(X0, Yb, X0, Yt - 12) + ARROW(X0, Yb, X1, Yb)
    b += f'<text transform="translate({X0 - 14},{(Yt + Yb) / 2}) rotate(-90)" text-anchor="middle" font-size="15" fill="{INK}" font-weight="bold" {FONT}>الطاقة</text>'
    b += T((X0 + X1) / 2, Yb + 30, 'سير التفاعل', 14, weight='bold')
    dashes = ['', '9 5', '3 4']
    for (lab, pk, col), da in zip(peaks, dashes):
        pth = _path(X0, W, y(r), y(pk), y(p), col, 3)
        if da: pth = pth.replace('stroke-linejoin', f'stroke-dasharray="{da}" stroke-linejoin')
        b += pth + TH(X0 + 0.48 * W, y(pk) - 10, lab, 16, color=col, weight='bold')
    b += TH(X0 + 0.125 * W, y(r) - 10, 'المتفاعلات', 14) + TH(X0 + 0.86 * W, y(p) + 22, 'النواتج', 14)
    save(name, svg(w, h, b))

def atom(x, y, el, r=None):
    col = {'C': DARK, 'O': ORED, 'N': NBLUE, 'A': PURPLE, 'B': ORANGE}[el]
    r = r or (13 if el == 'O' else 15)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" stroke="#fff" stroke-width="1.2"/>' + T(x, y + 5, el, 13, color='#fff', weight='bold')

def co(x, y, facing):
    """CO أفقي؛ facing = الذرة المواجهة لليمين (نحو NO₂)."""
    left, right = ('O', 'C') if facing == 'C' else ('C', 'O')
    return atom(x - 11, y, left) + atom(x + 11, y, right)

def no2(x, y, facing):
    """NO₂ منحنٍ؛ facing = 'O' (ذرة أكسجين تواجه اليسار) أو 'N' (ذرة النيتروجين تواجه اليسار)."""
    import math
    angs = (180, 46) if facing == 'O' else (67, -67)
    s = ''
    for a in angs:
        s += atom(x + 24 * math.cos(math.radians(a)), y - 24 * math.sin(math.radians(a)), 'O')
    return s + atom(x, y, 'N')

def collisions(name):
    w, h = 560, 420
    b = ''
    panels = [('(1)', 'O', 'O', True), ('(2)', 'C', 'N', True), ('(3)', 'C', 'O', True), ('(4)', 'C', 'O', False)]
    for i, (lab, cf, nf, high) in enumerate(panels):
        ox, oy = 10 + (i % 2) * 275, 10 + (i // 2) * 200
        b += f'<rect x="{ox}" y="{oy}" width="265" height="190" rx="10" fill="#f7f9fc" stroke="#c9d2de"/>'
        b += T(ox + 132, oy + 24, lab, 16, weight='bold')
        my = oy + 85
        nx = ox + 185 if nf == 'O' else ox + 175
        b += co(ox + 70, my, cf) + no2(nx, my, nf)
        L1 = 50 if high else 24
        b += ARROW(ox + 50, my + 42, ox + 50 + L1, my + 42, INK, 2.5) + ARROW(ox + 205, my + 42, ox + 205 - L1, my + 42, INK, 2.5)
        b += T(ox + 132, oy + 172, 'طاقة التصادم أكبر من Ea' if high else 'طاقة التصادم أقل من Ea', 14, color=GREEN if high else RED, weight='bold')
    save(name, svg(w, h, b))

def a2b2(name):
    w, h = 560, 170
    y = 75
    b = atom(40, y - 15, 'A') + atom(40, y + 15, 'A') + T(100, y + 6, '+', 22)
    b += atom(150, y - 13, 'B', 13) + atom(150, y + 13, 'B', 13)
    b += ARROW(185, y, 235, y)
    # لحظة التصادم
    import math
    pts = ' '.join(f'{290 + (46 if k % 2 == 0 else 26) * math.cos(math.pi * k / 8):.1f},{y + (46 if k % 2 == 0 else 26) * math.sin(math.pi * k / 8):.1f}' for k in range(16))
    b += f'<polygon points="{pts}" fill="#ffe08a" stroke="#e0a800" stroke-width="1.5"/>'
    b += atom(277, y - 15, 'A') + atom(277, y + 15, 'A') + atom(303, y - 13, 'B', 13) + atom(303, y + 13, 'B', 13)
    b += ARROW(345, y, 395, y)
    b += atom(425, y, 'A') + atom(451, y, 'B', 13) + T(483, y + 6, '+', 22) + atom(510, y, 'A') + atom(536, y, 'B', 13)
    b += T(40, 140, 'A₂', 16, weight='bold') + T(150, 140, 'B₂', 16, weight='bold') + T(290, 140, 'تصادم', 15, weight='bold') + T(480, 140, '2AB', 16, weight='bold')
    save(name, svg(w, h, b))

def conc_time(name, series, tmax=40, cmax=0.200, w=520, h=330, ticks=(0, 0.050, 0.100, 0.150, 0.200), notes=()):
    """منحنيات التركيز مع الزمن. series = [(label, [(t, c)...], color)]. notes = [(t, c, text, dx, dy)]"""
    X0, X1, Yt, Yb = 85, w - 25, 30, h - 50
    def X(t): return X0 + t / tmax * (X1 - X0)
    def Y(c): return Yb - c / cmax * (Yb - Yt)
    b = ARROW(X0, Yb, X0, Yt - 12) + ARROW(X0, Yb, X1 + 12, Yb)
    b += f'<text transform="translate({X0 - 58},{(Yt + Yb) / 2}) rotate(-90)" text-anchor="middle" font-size="15" fill="{INK}" font-weight="bold" {FONT}>التركيز (M)</text>'
    b += T((X0 + X1) / 2, Yb + 38, 'الزمن (s)', 14, weight='bold')
    for c in ticks:
        b += L(X0 - 5, Y(c), X0, Y(c)) + T(X0 - 9, Y(c) + 5, f'{c:.3f}', 12, 'end')
        if c: b += L(X0, Y(c), X1, Y(c), '#e3e7ee', 1)
    for t in range(0, tmax + 1, 10):
        b += L(X(t), Yb, X(t), Yb + 5) + T(X(t), Yb + 20, str(t), 12)
        if t: b += L(X(t), Yt, X(t), Yb, '#e3e7ee', 1)
    for lab, pts, col in series:
        # منحنى أملس عبر النقاط (Catmull-Rom)
        P = [(X(t), Y(c)) for t, c in pts]
        d = f'M{P[0][0]:.1f},{P[0][1]:.1f}'
        for i in range(len(P) - 1):
            p0 = P[i - 1] if i else P[i]; p1, p2 = P[i], P[i + 1]; p3 = P[i + 2] if i + 2 < len(P) else P[i + 1]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6); c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
        b += f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.2"/>'
        for x, yy in P: b += f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="4" fill="{col}"/>'
        b += circ_num(P[-1][0] - 4, P[-1][1] - 20, lab, col)
    for t, c, txt, dx, dy in notes:
        b += TH(X(t) + dx, Y(c) + dy, txt, 12, 'start', INK, 'bold')
    save(name, svg(w, h, b))

if __name__ == '__main__':
    # O07: الشكل A₂ + B₂ → 2AB
    a2b2('c2-l1b-a2b2.svg')
    # O08: أربعة احتمالات لتصادم CO مع NO₂
    collisions('c2-l1b-collisions.svg')
    # O09: تفاعلان بطاقتي تنشيط مختلفتين
    save('c2-l1b-two-ea.svg', svg(620, 330,
         reaction_profile(50, 80, 20, vmin=-12, vmax=155, ox=0, w=310, h=330, complex_='', title='التفاعل (أ)', caption='Ea = 30 kJ', react_pos='below', arrows=[('ea', 'Ea', RED)])
         + reaction_profile(50, 140, 20, vmin=-12, vmax=155, ox=310, w=310, h=330, complex_='', title='التفاعل (ب)', caption='Ea = 90 kJ', react_pos='below', arrows=[('ea', 'Ea', RED)])
         + L(310, 10, 310, 320, MUTED, 1, '4 4')))
    three_curves('c2-l1b-three-ea.svg', 40, 20, [('X', 150, RED), ('Y', 90, GREEN), ('Z', 120, BLUE)])
    save('c2-l1b-ea-vs-dh.svg', svg(640, 360,
         reaction_profile(170, 290, 20, vmin=-25, vmax=330, ox=0, w=320, h=360, complex_='', title='التفاعل (أ)', caption='Ea = 120 kJ ، ΔH = −150 kJ',
                          arrows=[('ea', 'Ea', RED), ('dh', 'ΔH', BLUE)])
         + reaction_profile(170, 205, 150, vmin=-25, vmax=330, ox=320, w=320, h=360, complex_='', title='التفاعل (ب)', caption='Ea = 35 kJ ، ΔH = −20 kJ',
                            arrows=[('ea', 'Ea', RED), ('dh', 'ΔH', BLUE)])
         + L(320, 10, 320, 350, MUTED, 1, '4 4')))
    # O10: التركيز مع الزمن للتفاعل CO + NO₂ → CO₂ + NO
    conc_time('c2-l1b-conc-time.svg',
              [(1, [(0, 0.200), (10, 0.160), (20, 0.140), (30, 0.128), (40, 0.120)], RED),
               (2, [(0, 0.000), (10, 0.040), (20, 0.060), (30, 0.072), (40, 0.080)], BLUE)],
              notes=[(0, 0.200, '0.200', 10, 16), (20, 0.140, '0.140', 4, -12), (40, 0.120, '0.120', -40, 22),
                     (20, 0.060, '0.060', 4, 22), (40, 0.080, '0.080', -40, 24)])
    # O11: مخططات الطاقة للتفاعلين الأمامي والعكسي
    profile_file('c2-l1b-co-no2.svg', 110, 250, 30, vmin=-15, vmax=300, react='CO(g) + NO₂(g)', prod='CO₂(g) + NO(g)',
                 arrows=[('ea', 'طاقة التنشيط', RED), ('dh', 'ΔH', BLUE)])
    profile_file('c2-l1b-numbered.svg', 110, 250, 30, vmin=-15, vmax=300, complex_='',
                 arrows=[('ea', 1, RED), ('ear', 2, GREEN), ('dh', 3, BLUE)])
    profile_file('c2-l1b-exo-values.svg', 60, 160, 20, vmax=180, ticks=list(range(0, 181, 20)), guides=True, prod_pos='above')
    profile_file('c2-l1b-endo-values.svg', 30, 150, 110, vmax=180, ticks=list(range(0, 181, 20)), guides=True)
