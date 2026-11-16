import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-1 (التسارع) — الأهداف O01–O12

XL = 'الزمن t (s)'; VL = 'السرعة المتجهة v (m/s)'; DL = 'الموقع d (m)'
VIOLET = PURPLE

def mapper(xr, yr, w=520, h=360, title=False):
    L0, R0, T0, B0 = 78, w - 26, 34 if title else 18, h - 52
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    return X, Y

def S(pts, label=None, color=None, at=None, dx=8, dy=-8, dash=None, dots=None):
    d = {'pts': pts, 'dx': dx, 'dy': dy}
    if label: d['label'] = label
    if color: d['color'] = color
    if at: d['at'] = at
    if dash: d['dash'] = dash
    if dots is not None: d['dots'] = dots
    return d

def vt(name, ser, xr, yr, xs, ys, w=520, h=360, dots=True, yl=VL, extra=''):
    return graph(name, ser, xr, yr, XL, yl, xs, ys, w=w, h=h, dots=dots, extra=extra)

def pm(name, rows, w=600, row_h=78, plus=True, top=44):
    """نموذج الجسيم النقطي: rows = [{xs:[px], label?, vel?:bool, acc?:'→'|'←', start?:bool, color?}].
    plus يرسم محور الاتجاه الموجب (+x) نحو اليمين أسفل الشكل."""
    H = top + len(rows) * row_h + (46 if plus else 10); b = ''
    for i, r in enumerate(rows):
        y = top + 30 + i * row_h; c = r.get('color', INK); xs = r['xs']
        if r.get('label'): b += T(w - 12, y + 5, r['label'], 15, 'end', MUTED, 'bold')
        for k, x in enumerate(xs):
            b += DOT(x, y, 5.5, c)
            if r.get('vel') and k + 1 < len(xs) and xs[k + 1] != x:
                b += ARROW(x, y - 14, x + 0.86 * (xs[k + 1] - x), y - 14, RED, 2.2, 9)
        if r.get('start'):
            b += T(xs[0], y + 26, 'البداية', 13, color=MUTED)
        if r.get('times'):
            for k, x in enumerate(xs): b += T(x, y + 24, r['times'][k], 12, color=MUTED)
        if r.get('acc'):
            ax = sum(xs) / len(xs); d = 44 if r['acc'] == '→' else -44
            b += ARROW(ax - d / 2, y - 40, ax + d / 2, y - 40, VIOLET, 2.6) + T(ax + d / 2 + (12 if d > 0 else -12), y - 35, 'a', 16, 'start' if d > 0 else 'end', VIOLET, 'bold', True)
    if plus:
        ya = H - 18; b += ARROW(30, ya, 150, ya, INK, 1.8) + T(160, ya + 5, '+x', 15, 'start', italic=True)
    save(name, svg(w, H, b))

def hv(name, rows, unit=34, cols=14, w=None, scale_val='1 m/s', x0=1, extra=''):
    """متجهات أفقية على شبكة: rows = [(label, start_col, length_cols, color)] (الطول سالب = نحو اليسار)."""
    w = w or (cols * unit + 40); nrows = len(rows); h = nrows * unit * 2 + unit + 56
    ox, oy = 20, 20; b = ''
    for gx in range(cols + 1): b += L(ox + gx * unit, oy, ox + gx * unit, oy + (nrows * 2 + 1) * unit, GRID, 1)
    for gy in range(nrows * 2 + 2): b += L(ox, oy + gy * unit, ox + cols * unit, oy + gy * unit, GRID, 1)
    for i, (lab, s, ln, c) in enumerate(rows):
        y = oy + (2 * i + 1) * unit + unit / 2 - unit / 2 + unit / 2
        y = oy + (2 * i + 1) * unit
        x1, x2 = ox + s * unit, ox + (s + ln) * unit
        b += ARROW(x1, y, x2, y, c, 3.2, 13)
        lx = (x1 + x2) / 2
        b += f'<rect x="{lx - 26:.1f}" y="{y - 30:.1f}" width="52" height="22" fill="#fff" opacity="0.85"/>'
        b += T(lx, y - 13, lab, 18, 'middle', c, 'bold', True)
    yb = oy + (nrows * 2 + 1) * unit + 26
    b += T(ox + cols * unit, yb, 'كل مربع يمثل', 14, 'end', MUTED) + T(ox + cols * unit - 92, yb, scale_val, 14, 'end', INK)
    b += ARROW(ox, yb - 5, ox + 90, yb - 5, INK, 1.8) + T(ox + 98, yb, '+x', 14, 'start', italic=True)
    save(name, svg(w, h, b + extra))

def mini(X0, Y0, pw, ph, ser, xr, yr, xt, yt, title, color=BLUE, xl='t (s)', yl='v (m/s)'):
    """رسم صغير داخل لوحة: ser = [[(x,y),...], ...]."""
    L0, R0, T0, B0 = X0 + 46, X0 + pw - 14, Y0 + 30, Y0 + ph - 34
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    b = f'<rect x="{X0 + 2}" y="{Y0 + 2}" width="{pw - 4}" height="{ph - 4}" fill="#fff" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
    for x in xt: b += L(X(x), T0, X(x), B0, GRID, 1)
    for y in yt: b += L(L0, Y(y), R0, Y(y), GRID, 1)
    y0 = 0 if yr[0] <= 0 <= yr[1] else yr[0]
    b += ARROW(L0, Y(y0), R0 + 8, Y(y0), INK, 1.6, 8) + ARROW(L0, B0, L0, T0 - 8, INK, 1.6, 8)
    for x in xt: b += T(X(x), B0 + 15, fmt(x), 11, color=MUTED)
    for y in yt: b += T(L0 - 6, Y(y) + 4, fmt(y), 11, 'end', MUTED)
    b += T(R0 - 2, B0 + 29, xl, 11, 'end', MUTED, italic=True) + T(L0 + 4, T0 - 12, yl, 11, 'start', MUTED, italic=True)
    for pts in ser:
        p = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
        b += f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="2.6" stroke-linejoin="round"/>'
    b += T(X0 + pw - 16, Y0 + 22, title, 15, 'end', INK, 'bold')
    return b

def panels(name, items, xr, yr, xt, yt, pw=300, ph=210):
    b = ''
    for k, ser in enumerate(items):
        X0 = (k % 2) * pw; Y0 = (k // 2) * ph
        b += mini(X0, Y0, pw, ph, ser, xr, yr, xt, yt, f'({k + 1})')
    save(name, svg(2 * pw, ph * ((len(items) + 1) // 2), b))

# ================= O02 =================
vt('c3l1-unit-slope.svg', [S([(0, 0), (4, 12)], color=BLUE)], (0, 5), (0, 15), 1, 3)

# ================= O03 =================
vt('c3l1-rel-train-car.svg', [S([(0, 25), (5, 25)], 'A', BLUE, at=(4.4, 25), dx=0, dy=-10), S([(0, 0), (5, 10)], 'B', RED, at=(4.4, 8.8), dx=0, dy=-12)], (0, 5), (0, 30), 1, 5)

# ================= O04 =================
pm('c3l1-sign-left-speedup.svg', [{'xs': [530, 495, 440, 365, 270, 155][::-1][::-1], 'vel': True}], row_h=70)
s = ''
s += ARROW(80, 70, 260, 70, RED, 3.2, 13) + T(170, 55, 'v', 19, color=RED, weight='bold', italic=True)
s += ARROW(220, 130, 130, 130, PURPLE, 3.2, 13) + T(175, 115, 'a', 19, color=PURPLE, weight='bold', italic=True)
s += ARROW(30, 185, 140, 185, INK, 1.8) + T(150, 190, '+x', 15, 'start', italic=True)
save('c3l1-sign-vectors.svg', svg(320, 210, s))
vt('c3l1-sign-vt-cross.svg', [S([(0, -6), (6, 6)], color=BLUE)], (0, 6), (-8, 8), 1, 2)
pm('c3l1-sign-four-models.svg', [
    {'label': '(1)', 'xs': [40, 60, 100, 160, 240, 340], 'vel': True, 'start': True},
    {'label': '(2)', 'xs': [40, 140, 220, 280, 320, 340], 'vel': True, 'start': True},
    {'label': '(3)', 'xs': [340, 320, 280, 220, 140, 40], 'vel': True, 'start': True},
    {'label': '(4)', 'xs': [340, 240, 160, 100, 60, 40], 'vel': True, 'start': True}], w=430, row_h=84)

# ================= O05 =================
pm('c3l1-unif-rows.svg', [
    {'label': '(1)', 'xs': [40, 60, 100, 160, 240, 340]},
    {'label': '(2)', 'xs': [40, 100, 160, 220, 280, 340]},
    {'label': '(3)', 'xs': [40, 140, 220, 280, 320, 340]}], w=430, row_h=60, plus=False, top=10)
vt('c3l1-unif-dt.svg', [S([(0, 0), (5, 20)], 'A', BLUE, at=(4.5, 18), dx=-22, dy=-4, dots=False),
                        S([(t / 10, 0.8 * (t / 10) ** 2) for t in range(0, 51)], 'B', RED, at=(4.5, 16.2), dx=10, dy=12, dots=False)],
   (0, 5), (0, 20), 1, 4, dots=False, yl=DL)
s = ''
for i, (lab, xs) in enumerate([('السيارة 1', [40 + 50 * k for k in range(9)]), ('السيارة 2', [40, 50, 64, 82, 104, 130, 160, 194, 232, 274, 320, 370, 424])]):
    y = 50 + i * 90
    s += RECT(30, y - 22, 440, 44, MUTED, '#fbf8ef', 1.5)
    for x in xs: s += DOT(x, y, 3.5)
    s += T(560, y + 5, lab, 15, 'end', INK, 'bold')
save('c3l1-unif-tapes.svg', svg(580, 210, s))

# ================= O06 =================
hv('c3l1-pm-vec-speedup.svg', [('v_i', 1, 3, RED), ('v_f', 1, 5, RED)], cols=9)
pm('c3l1-pm-cat-models.svg', [
    {'label': '(1)', 'xs': [40, 140, 220, 280, 320, 340], 'vel': True, 'acc': '←'},
    {'label': '(2)', 'xs': [40, 140, 220, 280, 320, 340], 'vel': True, 'acc': '→'},
    {'label': '(3)', 'xs': [40, 60, 100, 160, 240, 340], 'vel': True, 'acc': '←'},
    {'label': '(4)', 'xs': [40, 100, 160, 220, 280, 340], 'vel': True, 'acc': '←'}], w=430, row_h=84)
hv('c3l1-pm-vec-slow.svg', [('v_i', 1, 6, RED), ('v_f', 1, 2, RED)], cols=9)
s = ''; X = lambda m: 40 + m * 50
s += L(X(0), 90, X(10), 90, INK, 2)
for m in range(11): s += L(X(m), 84, X(m), 96, INK, 1.5) + T(X(m), 114, str(m), 13, color=MUTED)
s += T(X(10) + 30, 114, 'd (m)', 13, 'start', MUTED, italic=True)
for k, m in enumerate([0, 1, 3, 6, 10]): s += DOT(X(m), 70, 6, BLUE) + T(X(m), 48, f't = {k} s', 13, color=INK)
s += ARROW(30, 150, 140, 150, INK, 1.8) + T(150, 155, '+x', 15, 'start', italic=True)
save('c3l1-pm-ruler.svg', svg(620, 170, s))
hv('c3l1-pm-vec-essay.svg', [('v_i', 1, 2, RED), ('v_f', 1, 6, RED)], cols=9)
vt('c3l1-pm-vt-trip.svg', [S([(0, 12), (2, 12), (3, 6), (5, 6), (6, 0), (7, 0), (8, 15), (10, 15)], color=BLUE)], (0, 10), (0, 16), 1, 2, w=560)

# ================= O07 =================
s = DOT(300, 50, 6) + ARROW(30, 100, 140, 100, INK, 1.8) + T(150, 105, '+x', 15, 'start', italic=True)
save('c3l1-state-one.svg', svg(600, 125, s))
pm('c3l1-state-equal.svg', [{'xs': [60 + 90 * k for k in range(6)], 'start': True}], row_h=70)
pm('c3l1-state-speed.svg', [{'xs': [60, 80, 120, 180, 260, 360, 480], 'start': True}], row_h=70)
pm('c3l1-state-slow.svg', [{'xs': [540, 420, 320, 240, 180, 140, 120][::1], 'start': True}], row_h=70)
pm('c3l1-state-vec-left.svg', [{'xs': [540, 520, 480, 420, 340, 240], 'vel': True, 'start': True}], row_h=70)
pm('c3l1-state-two-stage.svg', [{'xs': [50, 130, 210, 290, 370, 440, 495, 535, 560], 'start': True}], row_h=70)
pm('c3l1-state-four.svg', [
    {'label': 'A', 'xs': [40, 140, 220, 280, 320, 340], 'start': True},
    {'label': 'B', 'xs': [190]},
    {'label': 'C', 'xs': [40, 60, 100, 160, 240, 340], 'start': True},
    {'label': 'D', 'xs': [40, 100, 160, 220, 280, 340], 'start': True}], w=430, row_h=72)
pm('c3l1-state-incline.svg', [
    {'label': 'المرحلة 1', 'xs': [40, 140, 220, 280, 320, 340], 'vel': True, 'start': True},
    {'label': 'المرحلة 2', 'xs': [340, 320, 280, 220, 140, 40], 'vel': True}], w=470, row_h=84)

# ================= O08 =================
vt('c3l1-vt-read.svg', [S([(0, 4), (6, 16)], color=BLUE)], (0, 6), (0, 18), 1, 2)
vt('c3l1-vt-time.svg', [S([(0, 20), (8, 4)], color=BLUE)], (0, 8), (0, 24), 1, 4)
vt('c3l1-vt-negative.svg', [S([(0, -5), (6, -5)], color=BLUE)], (0, 6), (-8, 8), 1, 2)

# ================= O09 =================
panels('c3l1-draw-panels.svg', [[[(0, 0), (4, 20)]], [[(0, 5), (4, 5)]], [[(0, 0), (4, 10)]], [[(0, 20), (4, 0)]]],
       (0, 4), (0, 20), [0, 1, 2, 3, 4], [0, 5, 10, 15, 20])
panels('c3l1-draw-panels-ew.svg', [[[(0, 20), (50, 20)], [(50, -20), (100, -20)]], [[(0, 20), (100, 20)]],
                                   [[(0, -20), (50, -20)], [(50, 20), (100, 20)]], [[(0, 20), (100, -20)]]],
       (0, 100), (-20, 20), [0, 25, 50, 75, 100], [-20, -10, 0, 10, 20])
vt('c3l1-draw-student.svg', [S([(0, 2), (1, 5), (2, 8), (3, 13), (4, 14)], color=BLUE)], (0, 4), (0, 16), 1, 2)

# ================= O10 =================
vt('c3l1-slope-a.svg', [S([(0, 2), (6, 14)], color=BLUE)], (0, 6), (0, 16), 1, 2)
vt('c3l1-slope-three.svg', [S([(0, 0), (5, 20)], 'A', BLUE, at=(2, 8), dx=-22, dy=-4), S([(0, 10), (5, 20)], 'B', RED, at=(1, 12), dx=0, dy=-12),
                            S([(0, 5), (5, 10)], 'C', GREEN, at=(4, 9), dx=0, dy=-12)], (0, 5), (0, 24), 1, 4)
vt('c3l1-slope-neg.svg', [S([(0, 12), (4, 0)], color=BLUE)], (0, 5), (0, 14), 1, 2)
vt('c3l1-slope-trip.svg', [S([(0, 0), (4, 20), (8, 20), (12, 12), (16, 12), (20, 0)], color=BLUE)], (0, 20), (0, 24), 2, 4, w=560)
vt('c3l1-slope-essay.svg', [S([(0, 3), (5, 18)], color=BLUE)], (0, 5), (0, 20), 1, 2)
vt('c3l1-slope-segments.svg', [S([(0, 0), (3, 12), (7, 12), (9, 4), (13, 0)], color=BLUE)], (0, 14), (0, 14), 1, 2, w=580)

# ================= O11 =================
import math as _m
vt('c3l1-desc-runner.svg', [S([(t / 10, 10 * (1 - _m.exp(-t / 10 / 1.2))) for t in range(0, 101)], color=RED, dots=False)], (0, 10), (0, 12), 1, 2, dots=False)
trn = [(0, 0), (4, 12), (12, 12), (16, 4), (28, 4), (36, 0)]
vt('c3l1-desc-train.svg', [S(trn, color=BLUE)], (0, 40), (0, 14), 4, 2, w=580)
vt('c3l1-desc-train2.svg', [S(trn, color=BLUE)], (0, 40), (0, 14), 4, 2, w=580)
vt('c3l1-desc-runners.svg', [S([(0, 8), (10, 8)], 'A', BLUE, at=(9, 8), dx=0, dy=-10, dots=False),
                             S([(0, 0), (10, 6)], 'B', GREEN, at=(9, 5.4), dx=0, dy=-12, dots=False),
                             S([(0, 7), (4, 0)], 'C', RED, at=(1, 5.25), dx=14, dy=0, dots=False),
                             S([(0, -4), (10, 4)], 'D', ORANGE, at=(9, 3.2), dx=0, dy=20, dots=False),
                             S([(0, -6), (10, -6)], 'E', PURPLE, at=(9, -6), dx=0, dy=-10, dots=False)], (0, 10), (-8, 10), 1, 2, dots=False)
vt('c3l1-desc-reverse.svg', [S([(0, 8), (4, 8), (8, 0), (12, -8)], color=BLUE)], (0, 12), (-10, 10), 1, 2, w=560)
vt('c3l1-desc-concave.svg', [S([(t / 10, 0.5 * (t / 10) ** 2) for t in range(0, 61)], color=RED, dots=False)], (0, 6), (0, 20), 1, 2, dots=False)
vt('c3l1-desc-stop.svg', [S([(0, 10), (3, 10), (7, 0), (10, 0)], color=BLUE)], (0, 10), (0, 12), 1, 2)
vt('c3l1-desc-elevator.svg', [S([(0, 0), (2, 3), (8, 3), (10, 0), (12, -3), (16, -3), (18, 0)], color=BLUE)], (0, 18), (-4, 4), 2, 1, w=580)
vt('c3l1-desc-runners-essay.svg', [S([(0, 6), (10, 6)], 'P', BLUE, at=(1, 6), dx=0, dy=-10, dots=False),
                                   S([(0, 2), (10, 8)], 'Q', GREEN, at=(9, 7.4), dx=0, dy=-12, dots=False),
                                   S([(0, 9), (10, 1)], 'R', RED, at=(9, 1.8), dx=0, dy=-12, dots=False),
                                   S([(0, -8), (10, -2)], 'S', ORANGE, at=(9, -2.6), dx=0, dy=-12, dots=False)], (0, 10), (-10, 10), 1, 2, dots=False)
vt('c3l1-desc-redlight.svg', [S([(0, 15), (4, 15), (10, 0), (14, 0), (20, 9)], color=BLUE)], (0, 20), (0, 16), 2, 2, w=580)

# ================= O12 =================
hv('c3l1-dir-vectors.svg', [('v_i', 5, 4, RED), ('v_f', 9, -4, RED)], cols=12)
vt('c3l1-dir-vt.svg', [S([(0, 6), (4, -6)], color=BLUE)], (0, 4), (-8, 8), 1, 2)
s = RECT(520, 20, 26, 170, INK, '#d8d2c4', 2) + T(533, 210, 'الجدار', 14)
s += ARROW(120, 70, 420, 70, RED, 3.2, 13) + T(270, 55, 'قبل الارتداد', 15, color=RED, weight='bold') + T(270, 92, '3.0 m/s', 15, color=RED)
s += ARROW(420, 140, 120, 140, RED, 3.2, 13) + T(270, 125, 'بعد الارتداد', 15, color=RED, weight='bold') + T(270, 162, '3.0 m/s', 15, color=RED)
s += ARROW(30, 205, 140, 205, INK, 1.8) + T(150, 210, '+x', 15, 'start', italic=True)
save('c3l1-dir-wall.svg', svg(580, 225, s))
