import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-2 (الحركة بتسارع ثابت) — الأهداف O08–O13

XL = 'الزمن (s)'; VL = 'السرعة المتجهة (m/s)'; AL = 'التسارع (m/s²)'; DL = 'الموقع (m)'
SHADE = '#cfe8d8'; SHADE2 = '#8fcca7'; NEG = '#f3d3cf'; TAN = ORANGE

def mapper(xr, yr, w=520, h=360):
    L0, R0, T0, B0 = 78, w - 26, 18, h - 52
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    return X, Y

def poly(X, Y, pts, fill, op=1):
    p = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" opacity="{op}" stroke="none"/>'

def S(pts, color=BLUE, dots=False, dash=None, w=3):
    d = {'pts': pts, 'color': color, 'dots': dots, 'w': w}
    if dash: d['dash'] = dash
    return d

def at_graph(name, segs, xr, yr, xs, ys, w=540, h=380, shade=True):
    """منحنى (التسارع – الزمن) من قطع أفقية: segs = [(t1, t2, a)]؛ تُظلَّل المساحة بين المنحنى ومحور الزمن."""
    X, Y = mapper(xr, yr, w, h); ex = ''
    if shade:
        for t1, t2, a in segs:
            ex = poly(X, Y, [(t1, 0), (t2, 0), (t2, a), (t1, a)], SHADE if a >= 0 else NEG, 0.85) + ex
    graph(name, [S([(t1, a), (t2, a)], C_ACC) for t1, t2, a in segs], xr, yr, XL, AL, xs, ys, w=w, h=h, extra='')
    # إعادة الرسم مع التظليل خلف الخطوط: نبني الملف يدويًا بإدراج التظليل قبل المنحنى
    p = os.path.join(OUT, name); s = open(p, encoding='utf-8').read()
    s = s.replace('fill="#fff"/>\n', 'fill="#fff"/>\n' + ex, 1); open(p, 'w', encoding='utf-8').write(s)

def shaded_graph(name, ser, xr, yr, xs, ys, xl, yl, under=(), w=540, h=380, extra=''):
    """منحنى عام مع تظليل مضلّعات تحت المنحنى قبل رسم الخطوط: under = [(pts, fill)]."""
    X, Y = mapper(xr, yr, w, h)
    ex = ''.join(poly(X, Y, pts, f, 0.9) for pts, f in under)
    graph(name, ser, xr, yr, xl, yl, xs, ys, w=w, h=h, extra=extra)
    p = os.path.join(OUT, name); s = open(p, encoding='utf-8').read()
    s = s.replace('fill="#fff"/>\n', 'fill="#fff"/>\n' + ex, 1); open(p, 'w', encoding='utf-8').write(s)
    return X, Y

def curve(f, t0, t1, n=60): return [(t0 + (t1 - t0) * k / n, f(t0 + (t1 - t0) * k / n)) for k in range(n + 1)]

# ================= O08 (المساحة تحت منحنى التسارع – الزمن) =================
at_graph('c3l2-o08-const2.svg', [(0, 6, 2.0)], (0, 7), (0, 3), 1, 0.5)
at_graph('c3l2-o08-const15.svg', [(0, 4, 1.5)], (0, 5), (0, 2.5), 1, 0.5)
at_graph('c3l2-o08-posneg.svg', [(0, 3, 2.0), (3, 7, -1.0)], (0, 8), (-2, 3), 1, 0.5)
X, Y = mapper((0, 5), (0, 5), 540, 380)
shaded_graph('c3l2-o08-ramp.svg', [S([(0, 0), (4, 4.0)], C_ACC)], (0, 5), (0, 5), 1, 1, XL, AL,
             under=[([(0, 0), (4, 0), (4, 4.0)], SHADE)])
at_graph('c3l2-o08-essay2.svg', [(0, 2, 3.0), (2, 5, 0.0), (5, 7, -2.0)], (0, 8), (-3, 4), 1, 1)
graph('c3l2-o08-essay3.svg', [S([(0, 4), (6, 16)], BLUE, True)], (0, 7), (0, 18), XL, VL, 1, 2, w=540, h=380)

# ================= O09 (v_f = v_i + ā Δt) =================
graph('c3l2-o09-line.svg', [S([(0, 6), (4, 18)], BLUE, True)], (0, 5), (0, 20), XL, VL, 1, 2, w=540, h=380)

# ================= O10 (تطبيق المعادلات) =================
def axis_obj(name):
    w, h = 680, 190; X = lambda m: 40 + (m + 30) * 9.333; b = ''
    yb = 120
    b += ARROW(X(-30) - 10, yb, X(30) + 22, yb, INK, 2)
    for m in range(-30, 31, 10):
        b += L(X(m), yb - 7, X(m), yb + 7, INK, 1.6) + T(X(m), yb + 26, fmt(m), 13, color=MUTED)
    for m in range(-30, 31, 5): b += L(X(m), yb - 4, X(m), yb + 4, INK, 1)
    b += T(X(30) + 26, yb + 26, 'd (m)', 13, 'start', MUTED, italic=True)
    b += DOT(X(-20), yb - 18, 8, INK, '#eef2f8')
    b += ARROW(X(-20), yb - 50, X(-20) + 90, yb - 50, C_VEL, 3, 12) + V(X(-20) + 104, yb - 45, 'v_i', C_VEL, 17, 'start')
    b += ARROW(X(-20), yb - 80, X(-20) + 60, yb - 80, C_ACC, 3, 12) + V(X(-20) + 74, yb - 75, 'a', C_ACC, 17, 'start')
    b += ARROW(40, 172, 150, 172, INK, 1.8) + T(160, 177, '+x', 15, 'start', italic=True)
    save(name, svg(w, h, b))
axis_obj('c3l2-o10-axis.svg')

# ================= O11 (منحنى الموقع – الزمن والمماسات) =================
def mini(X0, Y0, pw, ph, pts, title, xl='t (s)', yl='d (m)'):
    L0, R0, T0, B0 = X0 + 40, X0 + pw - 16, Y0 + 34, Y0 + ph - 26
    xr, yr = (0, 4), (0, 16)
    Xm = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Ym = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    b = f'<rect x="{X0 + 2}" y="{Y0 + 2}" width="{pw - 4}" height="{ph - 4}" fill="#fff" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
    b += ARROW(L0, B0, R0 + 8, B0, INK, 1.6, 8) + ARROW(L0, B0, L0, T0 - 10, INK, 1.6, 8)
    b += T(R0 + 4, B0 + 18, xl, 12, 'end', MUTED, italic=True) + T(L0 + 6, T0 - 12, yl, 12, 'start', MUTED, italic=True)
    p = ' '.join(f'{Xm(x):.1f},{Ym(y):.1f}' for x, y in pts)
    b += f'<polyline points="{p}" fill="none" stroke="{BLUE}" stroke-width="2.8" stroke-linejoin="round"/>'
    b += T(X0 + pw - 14, Y0 + 24, title, 15, 'end', INK, 'bold')
    return b

def panels(name, items, pw=280, ph=190):
    b = ''
    for k, pts in enumerate(items):
        b += mini((k % 2) * pw, (k // 2) * ph, pw, ph, pts, f'({k + 1})')
    save(name, svg(2 * pw, ph * ((len(items) + 1) // 2), b))

panels('c3l2-o11-shapes.svg', [
    [(0, 0), (4, 14)],
    curve(lambda t: 0.875 * t * t, 0, 4),
    curve(lambda t: 7 * t - 0.875 * t * t, 0, 4),
    [(0, 9), (4, 9)]])

# مماس عند t = 2 s للمنحنى d = 1.5 t²
graph('c3l2-o11-tan2.svg', [S(curve(lambda t: 1.5 * t * t, 0, 4), BLUE),
                            S([(1, 0), (3, 12)], TAN, False, '8 5', 2.4)],
      (0, 4), (0, 24), XL, DL, 0.5, 2, w=540, h=400,
      marks=[(2, 6, ''), (1, 0, ''), (3, 12, '')])

graph('c3l2-o11-slowing.svg', [S(curve(lambda t: 12 * t - 1.5 * t * t, 0, 4), BLUE),
                               S([(4, 24), (5, 24)], BLUE)], (0, 5), (0, 28), XL, DL, 1, 4, w=540, h=380)

# مماسان عند t = 1 s و t = 3 s للمنحنى d = 2.0 t² (إحداثيات النقاط في نص السؤال)
graph('c3l2-o11-twotan.svg', [S(curve(lambda t: 2 * t * t, 0, 4), BLUE),
                              S([(0.5, 0), (2, 6)], TAN, False, '8 5', 2.4), S([(1.5, 0), (4, 30)], TAN, False, '8 5', 2.4)],
      (0, 4), (0, 32), XL, DL, 0.5, 4, w=560, h=420,
      marks=[(1, 2, ''), (3, 18, ''), (0.5, 0, ''), (2, 6, ''), (1.5, 0, ''), (4, 30, '')])

graph('c3l2-o11-negfast.svg', [S(curve(lambda t: 20 - 1.25 * t * t, 0, 4), BLUE)], (0, 4), (0, 24), XL, DL, 1, 4, w=540, h=380)

# المقالي 1: d = 1.5 t² مع مماسين عند 2 s و 4 s
graph('c3l2-o11-essay1.svg', [S(curve(lambda t: 1.5 * t * t, 0, 5), BLUE),
                              S([(1, 0), (3, 12)], TAN, False, '8 5', 2.4), S([(3, 12), (5, 36)], TAN, False, '8 5', 2.4)],
      (0, 5), (0, 40), XL, DL, 0.5, 4, w=580, h=440,
      marks=[(0, 0, ''), (1, 1.5, ''), (2, 6, ''), (3, 13.5, ''), (4, 24, ''), (5, 37.5, ''), (1, 0, ''), (3, 12, ''), (5, 36, '')])

# المقالي 2: عدّاء (تسارع ثم سرعة منتظمة ثم تباطؤ ثم وقوف)
def runner(t):
    if t <= 4: return 0.75 * t * t
    if t <= 10: return 12 + 6 * (t - 4)
    if t <= 14: u = t - 10; return 48 + 6 * u - 0.75 * u * u
    return 60
graph('c3l2-o11-essay2.svg', [S(curve(runner, 0, 16, 160), BLUE)], (0, 16), (0, 64), XL, DL, 2, 8, w=600, h=400,
      marks=[(4, 12, ''), (10, 48, ''), (14, 60, '')])

# ================= O12 (اشتقاق المعادلات من المساحة) =================
def area_generic(name, tlabel='t', show_nums=False):
    w, h = 540, 360; L0, B0, R0, T0 = 90, 300, 480, 40
    tx = 430; vi_y = 220; vf_y = 80; b = ''
    b += f'<polygon points="{L0},{B0} {tx},{B0} {tx},{vi_y} {L0},{vi_y}" fill="{SHADE}"/>'
    b += f'<polygon points="{L0},{vi_y} {tx},{vi_y} {tx},{vf_y}" fill="{SHADE2}"/>'
    b += ARROW(L0, B0, R0 + 20, B0, INK, 2) + ARROW(L0, B0, L0, T0 - 10, INK, 2)
    b += L(L0, vf_y, tx, vf_y, MUTED, 1.2, '5 4') + L(tx, B0, tx, vf_y, MUTED, 1.2, '5 4')
    b += L(L0, vi_y, R0 - 20, vi_y, MUTED, 1.2, '5 4')
    b += L(L0, vi_y, tx, vf_y, BLUE, 3)
    b += V(L0 - 12, vi_y + 6, 'v_i', C_VEL, 17, 'end') + V(L0 - 12, vf_y + 6, 'v_f', C_VEL, 17, 'end')
    b += T(L0, B0 + 22, '0', 14, color=MUTED) + T(tx, B0 + 24, tlabel, 17, italic=True)
    b += T((L0 + tx) / 2, (B0 + vi_y) / 2 + 6, '(1)', 17, weight='bold') + T(tx - 70, vi_y - 24, '(2)', 17, weight='bold')
    b += T((L0 + R0) / 2, h - 10, XL, 14) + T(24, (T0 + B0) / 2, VL, 14, rotate=-90)
    save(name, svg(w, h, b))
area_generic('c3l2-o12-areas.svg')
area_generic('c3l2-o12-essay1.svg')
shaded_graph('c3l2-o12-num.svg', [S([(0, 2), (5, 12)], BLUE, True)], (0, 6), (0, 14), 1, 2, XL, VL,
             under=[([(0, 0), (5, 0), (5, 2), (0, 2)], SHADE), ([(0, 2), (5, 2), (5, 12)], SHADE2)],
             extra='')

# ================= O13 (الاستجابة والفرملة) =================
def two_phase(name, w=660, h=200):
    xs = [50, 120, 190, 260, 330, 390, 438, 474, 498, 510]; y = 100; b = ''
    for k, x in enumerate(xs):
        b += DOT(x, y, 6)
        if k + 1 < len(xs): b += ARROW(x, y - 18, x + 0.85 * (xs[k + 1] - x), y - 18, C_VEL, 2.2, 8)
    b += L(260, 40, 260, 140, MUTED, 1.4, '6 5')
    b += T(155, 152, 'المرحلة الأولى', 14, color=MUTED) + T(385, 152, 'المرحلة الثانية', 14, color=MUTED)
    b += ARROW(450, 50, 380, 50, C_ACC, 2.8, 11) + V(368, 56, 'a', C_ACC, 17, 'end')
    b += ARROW(40, 182, 150, 182, INK, 1.8) + T(160, 187, '+x', 15, 'start', italic=True)
    save(name, svg(w, h, b))
two_phase('c3l2-o13-phases.svg')

def stop_road(name, w=680, h=240):
    b = ''; y = 110
    b += RECT(30, y - 30, 620, 60, MUTED, '#e7e9ee', 1.5)
    for x in range(50, 640, 50): b += L(x, y, x + 24, y, '#fff', 3)
    xs = [60, 140, 220, 300, 380, 450, 506, 548, 576, 590]
    b += L(380, 60, 380, 172, MUTED, 1.4, '6 5') + L(590, 60, 590, 172, MUTED, 1.4, '6 5') + L(60, 60, 60, 172, MUTED, 1.4, '6 5')
    for k, x in enumerate(xs):
        b += DOT(x, y, 5.5)
        if k + 1 < len(xs): b += ARROW(x, y - 16, x + 0.85 * (xs[k + 1] - x), y - 16, C_VEL, 2, 8)
    b += T(220, 70, 'الاستجابة', 14, color=INK, weight='bold') + T(485, 70, 'الفرملة', 14, color=INK, weight='bold')
    b += T(60, 190, 'رؤية الطفل', 13, color=MUTED) + T(380, 190, 'بدء الضغط على الفرامل', 13, color=MUTED) + T(600, 190, 'التوقف', 13, color=MUTED)
    b += ARROW(540, 220, 470, 220, C_ACC, 2.8, 11) + V(458, 226, 'a', C_ACC, 17, 'end')
    b += ARROW(30, 222, 130, 222, INK, 1.8) + T(140, 227, '+x', 15, 'start', italic=True)
    save(name, svg(w, h, b))
stop_road('c3l2-o13-essay1.svg')
