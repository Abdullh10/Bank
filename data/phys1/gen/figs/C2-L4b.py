import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-4 (السرعة المتجهة) — الأهداف O09–O16

XL = 'الزمن (s)'; YL = 'الموقع (m)'

def S(pts, label=None, color=None, at=None, dx=8, dy=-8, dash=None):
    d = {'pts': pts, 'dx': dx, 'dy': dy}
    if label: d['label'] = label
    if color: d['color'] = color
    if at: d['at'] = at
    if dash: d['dash'] = dash
    return d

def lines(name, ser, xr, yr, xs, ys, w=520, h=360, dots=True, extra=''):
    return graph(name, ser, xr, yr, XL, YL, xs, ys, w=w, h=h, dots=dots, extra=extra)

# ---------- O09 ----------
lines('c2l4-o09-rank1.svg', [S([(0, 2), (5, 17)], 'A', BLUE), S([(0, 18), (5, 3)], 'B', RED, dy=14),
                             S([(0, 4), (5, 9)], 'C', GREEN), S([(0, 14), (5, 4)], 'D', ORANGE, dy=-4)], (0, 5), (0, 20), 1, 2, w=540)
lines('c2l4-o09-equal.svg', [S([(0, 0), (5, 10)], 'E', BLUE, dy=12), S([(0, 16), (5, 6)], 'F', RED, dy=-2),
                             S([(0, 6), (5, 16)], 'G', GREEN), S([(0, 6), (5, 11)], 'H', ORANGE, dy=-2)], (0, 5), (0, 18), 1, 2, w=540)
lines('c2l4-o09-steep.svg', [S([(0, 4), (4, 8)], 'K', BLUE), S([(0, 18), (4, 2)], 'L', RED), S([(0, 0), (4, 12)], 'M', GREEN)], (0, 4), (0, 20), 1, 2, w=540)
lines('c2l4-o09-late.svg', [S([(0, 0), (2, 10)], 'P', BLUE, dx=-22, dy=-4), S([(1, 20), (5, 0)], 'Q', RED, dy=-2),
                            S([(0, 10), (8, 18)], 'R', GREEN, dx=-18, dy=-10), S([(2, 0), (6, 12)], 'S', ORANGE)], (0, 8), (0, 20), 1, 2, w=560)
lines('c2l4-o09-essay1.svg', [S([(0, 12), (4, -4)], 'A', BLUE, dy=14), S([(0, -2), (4, 14)], 'B', RED),
                              S([(0, 6), (6, -6)], 'C', GREEN, dy=14), S([(0, -4), (6, 8)], 'D', ORANGE)], (0, 6), (-8, 16), 1, 2, w=560, h=420)
lines('c2l4-o09-essay3.svg', [S([(0, 10), (5, 18)], 'M', BLUE), S([(0, 16), (5, 1)], 'N', RED, dy=6), S([(0, 0), (5, 10)], 'O', GREEN, dy=10)], (0, 5), (0, 20), 1, 2, w=540)

# ---------- O10 ----------
lines('c2l4-o10-piece.svg', [S([(0, 0), (4, 12), (8, 12), (10, 2)], color=GREEN)], (0, 10), (0, 14), 1, 2, w=560)
lines('c2l4-o10-essay2.svg', [S([(0, 0), (3, 9), (6, 9), (10, 1)], color=GREEN)], (0, 10), (0, 10), 1, 1, w=560)

# ---------- O11 ----------
motion_diagram('c2l4-o11-dots.svg', [
    {'label': 'A', 'xs': [60 + 70 * k for k in range(6)]},
    {'label': 'B', 'xs': [60, 75, 105, 150, 210, 285]},
    {'label': 'C', 'xs': [60, 140, 205, 255, 290, 310]},
    {'label': 'D', 'xs': [60, 130, 200, 270, 270, 270]}], w=520, axis_label='d')

def panels(name, curves):
    """أربعة منحنيات صغيرة (الموقع – الزمن) مرقمة 1–4. curves: قائمة دوال f(u) لـ u من 0 إلى 1 تعيد ارتفاعًا بين 0 و1."""
    W, H = 460, 360; b = ''
    for k, f in enumerate(curves):
        ox, oy = 50 + (k % 2) * 220, 150 + (k // 2) * 175
        b += ARROW(ox, oy, ox + 170, oy, INK, 1.8) + ARROW(ox, oy, ox, oy - 125, INK, 1.8)
        b += T(ox + 165, oy + 18, 't', 14, italic=True) + T(ox - 12, oy - 112, 'd', 14, italic=True)
        pts = ' '.join(f'{ox + 6 + 150 * u:.1f},{oy - 6 - 100 * f(u):.1f}' for u in [i / 60 for i in range(61)])
        b += f'<polyline points="{pts}" fill="none" stroke="{GREEN}" stroke-width="3"/>'
        b += T(ox + 85, oy + 22, f'({k + 1})', 15, weight='bold')
    save(name, svg(W, H, b))
panels('c2l4-o11-panels.svg', [lambda u: 0.95 - 0.85 * u, lambda u: 0.05 + 0.9 * u * u,
                               lambda u: (0.1 + 1.2 * u) if u < 0.4 else (0.58 if u < 0.7 else 0.58 + 1.2 * (u - 0.7)),
                               lambda u: 0.1 + 1.6 * u if u < 0.5 else 0.9 - 1.6 * (u - 0.5)])

# ---------- مساعد: نموذج الجسيم النقطي على مسطرة مترية ----------
def ruler_dots(name, pos, xmax, step, w=600, vecs=None, label=None, x_left=0, dot_color=INK, extra_fn=None):
    """نقاط عند مواقع pos (m) فوق محور مدرّج من x_left إلى xmax. vecs: [(x_from, length_m)] أسهم سرعة حمراء فوق النقاط."""
    L0, R0 = 40, w - 40; X = lambda x: L0 + (x - x_left) / (xmax - x_left) * (R0 - L0)
    H = 150; ya = 110; yd = 70; b = ''
    b += ARROW(L0 - 10, ya, R0 + 22, ya, INK, 1.8) + T(R0 + 26, ya - 10, 'd (m)', 14, 'end', italic=True)
    x = x_left
    while x <= xmax + 1e-9:
        b += L(X(x), ya - 5, X(x), ya + 5, INK, 1.5) + T(X(x), ya + 22, fmt(round(x, 6)), 13, color=MUTED); x += step
    for p in pos: b += DOT(X(p), yd, 6.5, dot_color)
    for (x0, ln) in (vecs or []):
        if ln: b += ARROW(X(x0), yd - 22, X(x0 + ln), yd - 22, C_VEL, 2.6, 10)
    if label: b += T(w / 2, 24, label, 15, color=MUTED, italic=True)
    if extra_fn: b += extra_fn(X)
    save(name, svg(w, H, b))

# ---------- O12 ----------
lines('c2l4-o12-line1.svg', [S([(0, 6), (5, 16)], color=GREEN)], (0, 5), (0, 18), 1, 2)
lines('c2l4-o12-line2.svg', [S([(0, 15), (5, -5)], color=GREEN)], (0, 5), (-6, 16), 1, 2, h=380)
ruler_dots('c2l4-o12-dots.svg', [2, 5, 8, 11, 14], 16, 1, w=620, label='Δt = 1.0 s')
lines('c2l4-o12-essay2.svg', [S([(0, -6), (6, 12)], color=GREEN)], (0, 6), (-8, 14), 1, 2, h=380)
ruler_dots('c2l4-o12-essay3.svg', [24, 20, 16, 12, 8, 4], 28, 2, w=620, label='Δt = 0.50 s')

# ---------- O13 ----------
lines('c2l4-o13-line.svg', [S([(0, 4), (4, 16)], color=GREEN)], (0, 4), (0, 18), 1, 2)
lines('c2l4-o13-essay3.svg', [S([(0, -10), (5, 10)], color=GREEN)], (0, 5), (-12, 12), 1, 2, h=380)

# ---------- O14 ----------
def vec_rows(name, rows, w=560, row_h=62):
    """صفوف مرقمة من النقاط وأسهم السرعة. rows: [{label, xs:[px], arrows:[(x, len_px)]}]"""
    b = ''
    for i, r in enumerate(rows):
        y = 52 + i * row_h
        b += T(w - 16, y + 5, r['label'], 15, 'end', INK, 'bold')
        for x in r['xs']: b += DOT(x, y, 5.5)
        for x, ln in r.get('arrows', []): b += ARROW(x, y - 17, x + ln, y - 17, C_VEL, 2.4, 9)
    save(name, svg(w, 30 + len(rows) * row_h, b))
vec_rows('c2l4-o14-choices.svg', [
    {'label': '(1)', 'xs': [40, 110, 180, 250, 320, 390], 'arrows': [(40 + 70 * k, 56) for k in range(5)]},
    {'label': '(2)', 'xs': [40, 110, 180, 250, 320, 390], 'arrows': [(40 + 70 * k, 20 + 11 * k) for k in range(5)]},
    {'label': '(3)', 'xs': [40, 110, 180, 250, 320, 390], 'arrows': [(110 + 70 * k, -56) for k in range(5)]},
    {'label': '(4)', 'xs': [40, 110, 180, 250, 320, 390], 'arrows': [(40 + 70 * k, 64 - 11 * k) for k in range(5)]}])
motion_diagram('c2l4-o14-twocars.svg', [
    {'label': 'السيارة A', 'xs': [50 + 40 * k for k in range(6)], 'color': BLUE},
    {'label': 'السيارة B', 'xs': [50 + 80 * k for k in range(6)], 'color': RED}], w=520)
vec_rows('c2l4-o14-wrong.svg', [{'label': '', 'xs': [40, 70, 120, 190, 280, 390], 'arrows': [(x, 24) for x in [40, 70, 120, 190, 280]]}], w=460)
ruler_dots('c2l4-o14-essay1.svg', [0, 3, 6, 9, 12], 14, 1, w=600, label='Δt = 0.50 s')
ruler_dots('c2l4-o14-essay3.svg', [0, 8, 14, 18, 20, 20], 22, 2, w=600, label='Δt = 1.0 s')

# ---------- O15 ----------
lines('c2l4-o15-line1.svg', [S([(0, 8), (5, 18)], color=GREEN)], (0, 5), (0, 20), 1, 2)
lines('c2l4-o15-line2.svg', [S([(0, -6), (4, 10)], color=GREEN)], (0, 4), (-8, 12), 1, 2, h=380)
lines('c2l4-o15-rank.svg', [S([(0, 12), (5, 2)], 'A', BLUE), S([(0, -4), (5, 16)], 'B', RED),
                            S([(0, 6), (5, 11)], 'C', GREEN), S([(0, -10), (5, 0)], 'D', ORANGE, dy=14)], (0, 5), (-12, 18), 1, 2, w=540, h=440)
lines('c2l4-o15-runners.svg', [S([(0, 6), (6, 12)], 'A', BLUE, dash='8 6'), S([(0, 0), (6, 18)], 'B', RED)], (0, 6), (0, 20), 1, 2)
lines('c2l4-o15-segment.svg', [S([(2, 10), (6, 22)], color=GREEN)], (0, 6), (0, 24), 1, 2, h=380)
lines('c2l4-o15-essay1.svg', [S([(0, 10), (5, 20)], 'P', BLUE), S([(0, -14), (5, 6)], 'Q', RED), S([(0, -2), (5, -12)], 'R', GREEN)],
      (0, 5), (-14, 20), 1, 2, w=540, h=460)
lines('c2l4-o15-essay2.svg', [S([(0, -12), (6, 6)], color=GREEN)], (0, 6), (-14, 8), 1, 2, h=380)

# ---------- O16 ----------
def sketch(name, student_m):
    w, h = 640, 210; L0, R0 = 70, 570; X = lambda m: L0 + m / 600 * (R0 - L0); b = ''
    b += RECT(L0 - 34, 48, 52, 42, INK, '#f3efe6') + f'<polygon points="{L0 - 40},{48} {L0 - 8},{22} {L0 + 24},{48}" fill="#d9c7a3" stroke="{INK}" stroke-width="2"/>'
    b += T(L0 - 8, 112, 'المنزل', 14)
    b += RECT(R0 - 30, 34, 70, 56, INK, '#e7eef8') + T(R0 + 5, 112, 'المدرسة', 14)
    b += L(20, 128, w - 20, 128, MUTED, 2)
    b += ARROW(L0, 165, R0 + 50, 165, INK, 1.8) + T(R0 + 54, 158, '+x', 15, 'end', italic=True)
    for m in range(0, 601, 100):
        b += L(X(m), 160, X(m), 170, INK, 1.5) + T(X(m), 190, str(m), 13, color=MUTED)
    b += T(w - 18, 202, '(m)', 13, 'end', MUTED)
    b += DOT(X(student_m), 118, 7, BLUE) + T(X(student_m), 100, 'الطالب', 13, color=BLUE)
    save(name, svg(w, h, b))
sketch('c2l4-o16-sketch1.svg', 200)
sketch('c2l4-o16-sketch2.svg', 450)
