import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-2 (الحركة بتسارع ثابت) — الجزء a: الأهداف O01–O07
# منحنيات (السرعة المتجهة – الزمن) بالأحمر (لون السرعة)، والمماسات/الخطوط المساعدة بلون الحبر، والمساحات (الإزاحة) بالأخضر.

XL = 'الزمن (s)'; VL = 'السرعة المتجهة (m/s)'
TAN = INK

def S(pts, label=None, color=C_VEL, at=None, dx=8, dy=-8, dash=None, dots=False, w=3):
    d = {'pts': pts, 'dx': dx, 'dy': dy, 'color': color, 'dots': dots, 'w': w}
    if label: d['label'] = label
    if at: d['at'] = at
    if dash: d['dash'] = dash
    return d

def curve(f, a, b, n=120):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]

def mapper(xr, yr, w=520, h=360):
    L0, R0, T0, B0 = 78, w - 26, 18, h - 52
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    return X, Y

def vt(name, ser, xr, yr, xs, ys, w=520, h=360, extra_fn=None, labels=(), marks=()):
    X, Y = mapper(xr, yr, w, h)
    extra = extra_fn(X, Y) if extra_fn else ''
    return graph(name, ser, xr, yr, XL, VL, xs, ys, w=w, h=h, dots=False, extra=extra, labels=labels, marks=marks)

def shade(X, Y, pts, color=C_DISP, op=0.22):
    p = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
    return f'<polygon points="{p}" fill="{color}" fill-opacity="{op}" stroke="none"/>'

def tangent_dots(X, Y, pts):
    return ''.join(DOT(X(x), Y(y), 4, TAN) for x, y in pts)

def lab(X, Y, x, y, s, color=INK, size=15, dx=0, dy=0, italic=False, weight='bold'):
    return T(X(x) + dx, Y(y) + dy, s, size, 'middle', color, weight, italic)

# ---------- لوحات صغيرة ----------
def mini(X0, Y0, pw, ph, ser, xr, yr, title):
    L0, R0, T0, B0 = X0 + 40, X0 + pw - 16, Y0 + 34, Y0 + ph - 30
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    b = f'<rect x="{X0 + 3}" y="{Y0 + 3}" width="{pw - 6}" height="{ph - 6}" fill="#fff" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
    b += ARROW(L0, B0, R0 + 8, B0, INK, 1.6, 8) + ARROW(L0, B0, L0, T0 - 10, INK, 1.6, 8)
    b += T(R0 + 2, B0 + 20, 't', 13, 'end', MUTED, italic=True) + T(L0 - 8, T0 - 4, 'v', 13, 'end', MUTED, italic=True)
    for pts in ser:
        p = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
        b += f'<polyline points="{p}" fill="none" stroke="{C_VEL}" stroke-width="3" stroke-linejoin="round"/>'
    b += T(X0 + pw / 2, Y0 + 24, title, 16, 'middle', INK, 'bold')
    return b

def panels(name, items, xr=(0, 10), yr=(0, 10), pw=250, ph=190, cols=4):
    b = ''
    for k, (title, ser) in enumerate(items):
        b += mini((k % cols) * pw, (k // cols) * ph, pw, ph, ser, xr, yr, title)
    rows = (len(items) + cols - 1) // cols
    save(name, svg(cols * pw, rows * ph, b))

if __name__ == '__main__':
    # ================= O01 =================
    panels('c3l2-o01-shapes.svg', [
        ('A', [curve(lambda t: 9 * (1 - math.exp(-t / 2.5)), 0, 9.5)]),
        ('B', [[(0, 5), (9.5, 5)]]),
        ('C', [[(0, 8.5), (9, 1.5)]]),
        ('D', [curve(lambda t: 1 + 7.5 * math.exp(-t / 2.5), 0, 9.5)]),
    ], pw=230, ph=180, cols=4)

    # ================= O03 =================
    f = lambda t: 10 * t - t * t          # P عند t = 2 s، v = 16 m/s، ميل المماس 6
    def o03(X, Y):
        b = ''
        b += L(X(0), Y(4), X(4.5), Y(31), TAN, 2, '7 5')          # 1 مماس: v = 4 + 6t
        b += L(X(0), Y(0), X(3.4), Y(27.2), MUTED, 2, '3 4')        # 2 من الأصل إلى P: v = 8t
        b += L(X(0), Y(16), X(6), Y(16), GREEN, 2, '10 4 2 4')    # 3 أفقي
        b += L(X(2), Y(16), X(5), Y(25), ORANGE, 2.2)              # 4 وتر من P إلى Q
        b += DOT(X(2), Y(16), 5, INK) + T(X(2) + 12, Y(16) + 18, 'P', 15, 'start', INK, 'bold', True)
        b += DOT(X(5), Y(25), 4.5, ORANGE)
        b += T(X(4.5) + 10, Y(31) + 4, '1', 15, 'start', TAN, 'bold')
        b += T(X(3.4) + 8, Y(27.2) + 10, '2', 15, 'start', MUTED, 'bold')
        b += T(X(6) - 8, Y(16) - 8, '3', 15, 'end', GREEN, 'bold')
        b += T(X(5) + 10, Y(25) + 18, '4', 15, 'start', ORANGE, 'bold')
        return b
    vt('c3l2-o03-lines.svg', [S(curve(f, 0, 5))], (0, 6), (0, 32), 1, 4, extra_fn=o03)

    # ================= O04 =================
    # Q1: v = 6t - 0.5t² ؛ المماس عند t = 2 s: v = 2 + 4t يمر بـ (0, 2) و(4, 18)
    f1 = lambda t: 6 * t - 0.5 * t * t
    vt('c3l2-o04-tan-rise.svg', [S(curve(f1, 0, 6)), S([(0, 2), (4.5, 20)], color=TAN, dash='7 5', w=2)], (0, 6), (0, 20), 1, 2,
       extra_fn=lambda X, Y: tangent_dots(X, Y, [(0, 2), (4, 18)]) + DOT(X(2), Y(10), 5, C_VEL))
    # Q2: v = 18 - 0.5t² ؛ المماس عند t = 2 s: v = 20 - 2t يمر بـ (0, 20) و(4, 12)
    f2 = lambda t: 18 - 0.5 * t * t
    vt('c3l2-o04-tan-brake.svg', [S(curve(f2, 0, 6)), S([(0, 20), (7, 6)], color=TAN, dash='7 5', w=2)], (0, 7), (0, 22), 1, 2,
       extra_fn=lambda X, Y: tangent_dots(X, Y, [(0, 20), (4, 12)]) + DOT(X(2), Y(16), 5, C_VEL))
    # Q4: منحنى بقمة ثم هبوط ثم ثبات، ونقاط A..D
    def f4(t):
        if t <= 3: return 2 + 10 * math.sin(math.pi * t / 6)
        if t <= 7: return 7 + 5 * math.cos(math.pi * (t - 3) / 4)
        return 2
    pts4 = [(1.5, f4(1.5), 'A'), (3, f4(3), 'B'), (5, f4(5), 'C'), (8.5, f4(8.5), 'D')]
    vt('c3l2-o04-points.svg', [S(curve(f4, 0, 10, 200))], (0, 10), (0, 14), 1, 2,
       extra_fn=lambda X, Y: ''.join(DOT(X(x), Y(y), 5, INK) + T(X(x) + (12 if k != 1 else 0), Y(y) - (10 if k != 1 else 14), s, 15, 'start' if k != 1 else 'middle', INK, 'bold', True)
                                     for k, (x, y, s) in enumerate(pts4)))
    # Q6: v = 10t - t² ؛ مماسان: عند 2 s (v = 4 + 6t) وعند 4 s (v = 16 + 2t)
    f6 = lambda t: 10 * t - t * t
    vt('c3l2-o04-two-tan.svg', [S(curve(f6, 0, 5)), S([(0, 4), (4.3, 29.8)], color=TAN, dash='7 5', w=2), S([(0, 16), (6, 28)], color=TAN, dash='7 5', w=2)],
       (0, 6), (0, 32), 1, 4,
       extra_fn=lambda X, Y: tangent_dots(X, Y, [(0, 4), (4, 28), (0, 16), (6, 28)]) + DOT(X(2), Y(16), 5, C_VEL) + DOT(X(4), Y(24), 5, C_VEL)
       + T(X(2) + 10, Y(16) + 18, '2.0 s', 13, 'start', MUTED) + T(X(4) + 4, Y(24) + 20, '4.0 s', 13, 'start', MUTED))
    # Q7: v = 0.5t² ؛ المماس عند 4 s: v = 4t - 8 يقطع محور الزمن عند 2 s ويمر بـ (6, 16)
    f7 = lambda t: 0.5 * t * t
    vt('c3l2-o04-tan-axis.svg', [S(curve(f7, 0, 6)), S([(2, 0), (6.5, 18)], color=TAN, dash='7 5', w=2)], (0, 7), (0, 20), 1, 2,
       extra_fn=lambda X, Y: tangent_dots(X, Y, [(2, 0), (6, 16)]) + DOT(X(4), Y(8), 5, C_VEL))
    # Q7 (بعد المراجعة): v = 2 + 6t - 0.5t² ؛ المماس عند 4 s: v = 10 + 2t يمر بنقطتي الشبكة (0, 10) و(5, 20) دون تعليمهما
    f8 = lambda t: 2 + 6 * t - 0.5 * t * t
    vt('c3l2-o04-tan-read.svg', [S(curve(f8, 0, 6)), S([(0, 10), (6.5, 23)], color=TAN, dash='7 5', w=2)], (0, 7), (0, 24), 1, 2,
       extra_fn=lambda X, Y: DOT(X(4), Y(18), 5, C_VEL))
    # E1: عدّاء v = 3t - 0.25t² حتى 6 s ثم 9 m/s ثابتة ؛ المماس عند 2 s: v = 1 + 2t ، وعند 7 s أفقي
    fe1 = lambda t: 3 * t - 0.25 * t * t if t <= 6 else 9
    vt('c3l2-o04-essay-runner.svg', [S(curve(fe1, 0, 9, 180)), S([(0, 1), (4.5, 10)], color=TAN, dash='7 5', w=2)], (0, 9), (0, 10), 1, 1,
       extra_fn=lambda X, Y: tangent_dots(X, Y, [(0, 1), (4, 9)]) + DOT(X(2), Y(5), 5, C_VEL) + DOT(X(7), Y(9), 5, C_VEL))
    # E3: فرملة v = 18 - 6t + 0.5t² حتى التوقف عند 6 s ؛ مماس عند 2 s: v = 16 - 4t ، وعند 4 s: v = 10 - 2t
    fe3 = lambda t: 18 - 6 * t + 0.5 * t * t
    vt('c3l2-o04-essay-brake.svg', [S(curve(fe3, 0, 6)), S([(0, 16), (4, 0)], color=TAN, dash='7 5', w=2), S([(0, 10), (5, 0)], color=TAN, dash='7 5', w=2)],
       (0, 7), (0, 20), 1, 2,
       extra_fn=lambda X, Y: tangent_dots(X, Y, [(0, 16), (4, 0), (0, 10), (5, 0)]) + DOT(X(2), Y(8), 5, C_VEL) + DOT(X(4), Y(2), 5, C_VEL))

    # ================= O05 =================
    vt('c3l2-o05-trip.svg', [S([(0, 0), (4, 20), (10, 20), (16, 8), (20, 8), (24, 0)])], (0, 26), (0, 24), 2, 4, w=560)
    vt('c3l2-o05-interval.svg', [S([(0, 4), (4, 16), (10, 16), (14, 0)])], (0, 16), (0, 20), 2, 4)
    vt('c3l2-o05-essay.svg', [S([(0, 0), (6, 15), (12, 15), (18, 6), (20, 6)])], (0, 20), (0, 18), 2, 3, w=560)

    # ================= O06 =================
    vt('c3l2-o06-equal.svg', [S([(0, 6), (4, 6)], 'A', C_VEL, at=(4, 6), dx=12, dy=5), S([(0, 0), (4, 12)], 'B', '#8a5a2b', at=(4, 12), dx=12, dy=5)],
       (0, 5), (0, 14), 1, 2)
    vt('c3l2-o06-cancel.svg', [S([(0, 0), (2, 8), (4, 0), (6, -8), (8, 0)])], (0, 9), (-10, 10), 1, 2)
    vt('c3l2-o06-rank.svg', [S([(0, 4), (6, 4)], 'A', C_VEL, at=(6, 4), dx=12, dy=5), S([(0, 0), (6, 10)], 'B', '#8a5a2b', at=(6, 10), dx=12, dy=5),
                             S([(0, 10), (4, 0), (6, 0)], 'C', GREEN, at=(1, 7.5), dx=10, dy=6, dash='9 5')],
       (0, 7), (0, 12), 1, 2)
    vt('c3l2-o06-catch.svg', [S([(0, 10), (5, 10)], 'A', C_VEL, at=(5, 10), dx=12, dy=5), S([(0, 0), (5, 25)], 'B', '#8a5a2b', at=(5, 25), dx=12, dy=5)],
       (0, 6), (0, 26), 1, 2, h=400)

    # ================= O07 =================
    vt('c3l2-o07-const.svg', [S([(0, 15), (8, 15)])], (0, 8), (0, 20), 1, 2)
    vt('c3l2-o07-rest.svg', [S([(0, 0), (6, 12)])], (0, 7), (0, 14), 1, 2)
    vt('c3l2-o07-trap.svg', [S([(0, 4), (6, 10)])], (0, 7), (0, 12), 1, 2)
    vt('c3l2-o07-trip.svg', [S([(0, 0), (5, 20), (10, 20), (15, 10), (20, 10), (25, 0)])], (0, 30), (0, 25), 5, 5, w=560)
    vt('c3l2-o07-north.svg', [S([(0, 15), (10, 15), (20, -15), (25, -15)])], (0, 30), (-20, 20), 5, 5, w=560, h=380)
    vt('c3l2-o07-stop.svg', [S([(0, 18), (6, 0)])], (0, 7), (0, 20), 1, 2)
    vt('c3l2-o07-cross.svg', [S([(0, 8), (6, -4)])], (0, 7), (-6, 10), 1, 2)
    vt('c3l2-o07-essay-trip.svg', [S([(0, 0), (4, 16), (9, 16), (13, 0)])], (0, 14), (0, 20), 1, 2, w=560)
    vt('c3l2-o07-essay-lift.svg', [S([(0, 0), (2, 4), (8, 4), (10, 0)])], (0, 11), (0, 5), 1, 1)
