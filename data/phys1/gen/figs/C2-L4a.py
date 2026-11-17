import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-4 (السرعة المتجهة) — الأهداف O01–O08

XL = 'الزمن (s)'; YL = 'الموقع (m)'

def mapper(xr, yr, w=520, h=360, title=False):
    """نفس تحويل graph() لاستعماله في extra قبل الاستدعاء."""
    L0, R0, T0, B0 = 78, w - 26, 34 if title else 18, h - 52
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    return X, Y

def lines(name, ser, xr, yr, xs, ys, xl=XL, yl=YL, w=520, h=360, dots=True, extra=''):
    graph(name, ser, xr, yr, xl, yl, xs, ys, w=w, h=h, dots=dots, extra=extra)

def S(pts, label=None, color=None, at=None, dx=8, dy=-8, dash=None):
    d = {'pts': pts}
    if label: d['label'] = label
    if color: d['color'] = color
    if at: d['at'] = at
    d['dx'] = dx; d['dy'] = dy
    if dash: d['dash'] = dash
    return d

# ---------- O02 ----------
lines('c2l4-o02-runners.svg', [S([(0, 0), (4, 8)], 'A', BLUE), S([(0, 0), (4, 4)], 'B', RED)], (0, 4), (0, 10), 1, 2)
lines('c2l4-o02-cyclists.svg', [S([(0, 0), (3, 12)], 'C', BLUE, at=(2.5, 10), dx=-18, dy=0), S([(0, 0), (6, 12)], 'D', RED)], (0, 7), (0, 14), 1, 2)
motion_diagram('c2l4-o02-dots.svg', [
    {'label': 'الجسم A', 'xs': [60 + 40 * k for k in range(6)], 'color': BLUE},
    {'label': 'الجسم B', 'xs': [60 + 80 * k for k in range(6)], 'color': RED}], w=560, axis_label='d')
lines('c2l4-o02-essay.svg', [S([(0, 0), (3, 6)], 'A', BLUE), S([(0, 0), (3, 3)], 'B', RED)], (0, 3), (0, 7), 0.5, 1)

# ---------- O03 ----------
X, Y = mapper((0, 6), (0, 14))
tri = (L(X(1), Y(4), X(5), Y(4), MUTED, 2, '6 5') + L(X(5), Y(4), X(5), Y(12), MUTED, 2, '6 5')
       + T((X(1) + X(5)) / 2, Y(4) + 22, 'Δt', 17, color=INK, italic=True)
       + T(X(5) + 14, (Y(4) + Y(12)) / 2 + 5, 'Δ', 17, color=C_DISP, anchor='start') + V(X(5) + 26, (Y(4) + Y(12)) / 2 + 5, 'd', C_DISP, anchor='start'))
lines('c2l4-o03-triangle.svg', [S([(0, 2), (6, 14)], color=BLUE)], (0, 6), (0, 14), 1, 2, dots=False, extra=tri + DOT(X(1), Y(4), 4.5, INK) + DOT(X(5), Y(12), 4.5, INK))
lines('c2l4-o03-negline.svg', [S([(0, 15), (5, 0)], color=BLUE)], (0, 5), (0, 16), 1, 2)
lines('c2l4-o03-essay.svg', [S([(0, 2), (6, 14)], color=BLUE)], (0, 6), (0, 14), 1, 2)
lines('c2l4-o03-parallel.svg', [S([(0, 2), (5, 12)], 'E', BLUE), S([(0, 8), (5, 18)], 'F', RED)], (0, 5), (0, 20), 1, 2)

# ---------- O04 ----------
lines('c2l4-o04-skate.svg', [S([(0, 2), (8, 14)], color=GREEN)], (0, 8), (0, 16), 1, 2)
lines('c2l4-o04-neg.svg', [S([(0, 12), (5, -3)], color=GREEN)], (0, 5), (-4, 12), 1, 2)
lines('c2l4-o04-bike.svg', [S([(0, 0), (40, 24)], color=GREEN)], (0, 40), (0, 24), 5, 4, xl='الزمن (min)', yl='الموقع (km)')
lines('c2l4-o04-piecewise.svg', [S([(0, 0), (2, 6), (5, 6), (6, 9)], color=GREEN)], (0, 6), (0, 10), 1, 1)
lines('c2l4-o04-boat.svg', [S([(0, 30), (6, 0)], color=GREEN)], (0, 6), (0, 30), 1, 5)
lines('c2l4-o04-essay1.svg', [S([(0, 4), (10, 24)], color=GREEN)], (0, 10), (0, 24), 1, 2, w=560)
lines('c2l4-o04-essay2.svg', [S([(0, 0), (4, 8), (6, 8), (10, -4)], color=GREEN)], (0, 10), (-6, 10), 1, 2, w=560)
lines('c2l4-o04-essay3.svg', [S([(0, 6), (5, 16)], color=GREEN)], (0, 5), (0, 18), 1, 2)

# ---------- O05 ----------
def segs(name, pts, names, xr, yr, xs, ys, offs):
    X, Y = mapper(xr, yr)
    ex = ''
    for k, nm in enumerate(names):
        (x1, y1), (x2, y2) = pts[k], pts[k + 1]
        ox, oy = offs[k]
        ex += T((X(x1) + X(x2)) / 2 + ox, (Y(y1) + Y(y2)) / 2 + oy, nm, 16, color=RED, weight='bold')
    lines(name, [S(pts, color=BLUE)], xr, yr, xs, ys, extra=ex)
segs('c2l4-o05-segs1.svg', [(0, 0), (2, 8), (5, 8), (7, -4), (10, -1)], 'ABCD', (0, 10), (-6, 10), 1, 2,
     [(-14, -6), (0, -12), (14, 0), (0, -14)])
segs('c2l4-o05-segs2.svg', [(0, 2), (3, 8), (5, 8), (7, 0), (10, 3)], 'ABCD', (0, 10), (0, 10), 1, 2,
     [(-14, -6), (0, -12), (14, 0), (0, -14)])
lines('c2l4-o05-cross.svg', [S([(0, 12), (6, -6)], color=BLUE)], (0, 6), (-8, 12), 1, 2)
lines('c2l4-o05-twoneg.svg', [S([(0, 10), (5, 0)], 'E', BLUE, at=(4.5, 1), dx=10, dy=-6), S([(0, 4), (5, -11)], 'F', RED, at=(4.5, -9.5), dx=10, dy=0)], (0, 5), (-12, 12), 1, 2)
lines('c2l4-o05-essay1.svg', [S([(0, 0), (10, 6), (30, 6), (40, 12), (45, 12), (55, 0)], color=BLUE)], (0, 60), (0, 14), 5, 2, w=600)
lines('c2l4-o05-essay3.svg', [S([(0, -8), (4, -2)], 'G', BLUE), S([(0, 10), (4, 4)], 'H', RED)], (0, 4), (-10, 12), 1, 2)

# ---------- O06 ----------
lines('c2l4-o06-line.svg', [S([(0, 18), (6, 0)], color=BLUE)], (0, 6), (0, 20), 1, 2)
lines('c2l4-o06-essay.svg', [S([(0, 0), (5, -10)], color=BLUE)], (0, 5), (-12, 2), 1, 2)

# ---------- O07 ----------
lines('c2l4-o07-boat.svg', [S([(0, 0), (5, -15)], color=BLUE)], (0, 5), (-16, 2), 1, 2)
lines('c2l4-o07-essay.svg', [S([(0, 0), (4, 12)], 'K', BLUE), S([(0, 20), (4, 8)], 'M', RED)], (0, 4), (0, 20), 1, 2)

# ---------- O08 ----------
lines('c2l4-o08-rank1.svg', [S([(0, 4), (5, 19)], 'A', BLUE), S([(0, 0), (5, 5)], 'B', RED, dy=10), S([(0, 16), (5, 6)], 'C', GREEN, at=(2.5, 11), dx=0, dy=-12), S([(0, 8), (5, 8)], 'D', ORANGE)], (0, 5), (0, 20), 1, 2, w=540)
lines('c2l4-o08-rank2.svg', [S([(0, 0), (6, 18)], 'X', BLUE), S([(0, 6), (8, 18)], 'Y', RED), S([(2, 0), (7, 15)], 'Z', GREEN), S([(0, 10), (8, 14)], 'W', ORANGE)], (0, 8), (0, 20), 1, 2, w=540)
lines('c2l4-o08-rank3.svg', [S([(0, 12), (5, 7)], 'E', BLUE), S([(0, 18), (5, 3)], 'F', RED, dy=12), S([(0, 20), (5, 10)], 'G', GREEN)], (0, 5), (0, 20), 1, 2, w=540)
lines('c2l4-o08-rank5.svg', [S([(0, 12), (5, 12)], 'M', ORANGE, at=(2.5, 12), dx=0, dy=-8), S([(0, 6), (5, 11)], 'N', BLUE, dy=10), S([(0, 18), (5, 13)], 'O', GREEN, at=(2.5, 15.5), dx=0, dy=-10), S([(0, 0), (5, 5)], 'P', RED)], (0, 5), (0, 20), 1, 2, w=540)
lines('c2l4-o08-essay1.svg', [S([(0, 0), (4, 16)], 'A', BLUE), S([(0, 12), (4, 4)], 'B', RED), S([(0, 2), (4, 10)], 'C', GREEN), S([(0, 18), (4, 2)], 'D', ORANGE)], (0, 4), (0, 20), 1, 2, w=540)
lines('c2l4-o08-essay2.svg', [S([(0, 0), (5, 20)], 'Q', BLUE), S([(1, 0), (6, 10)], 'R', RED), S([(0, 20), (5, 0)], 'S', GREEN, at=(4.5, 2), dx=10, dy=0), S([(0, 6), (6, 18)], 'U', ORANGE)], (0, 6), (0, 20), 1, 2, w=540)
