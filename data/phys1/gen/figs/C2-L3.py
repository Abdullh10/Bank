import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-3 منحنى (الموقع – الزمن)

TL = 'الزمن (s)'; DL = 'الموقع (m)'


def mini_graph(ox, oy, w, h, series, xr, yr, xs, ys, xlabel=TL, ylabel=DL, title=None, pts_only=False):
    """منحنى صغير داخل لوحة: (ox, oy) الزاوية العليا اليسرى للوحة كاملة."""
    L0, R0, T0, B0 = ox + 62, ox + w - 18, oy + (34 if title else 14), oy + h - 46
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    b = ''
    nx = round((xr[1] - xr[0]) / xs); ny = round((yr[1] - yr[0]) / ys)
    for i in range(nx + 1):
        x = xr[0] + i * xs; b += L(X(x), T0, X(x), B0, GRID, 1)
    for i in range(ny + 1):
        y = yr[0] + i * ys; b += L(L0, Y(y), R0, Y(y), GRID, 1)
    y0 = 0 if yr[0] <= 0 <= yr[1] else yr[0]
    b += ARROW(L0, Y(y0), R0 + 12, Y(y0), INK, 1.8, 9) + ARROW(L0, B0, L0, T0 - 10, INK, 1.8, 9)
    for i in range(nx + 1):
        x = xr[0] + i * xs; b += T(X(x), B0 + 17, fmt(round(x, 6)), 12, color=MUTED)
    for i in range(ny + 1):
        y = yr[0] + i * ys; b += T(L0 - 7, Y(y) + 4, fmt(round(y, 6)), 12, 'end', MUTED)
    b += T((L0 + R0) / 2, oy + h - 10, xlabel, 13)
    b += T(ox + 16, (T0 + B0) / 2, ylabel, 13, rotate=-90)
    for k, s in enumerate(series):
        c = s.get('color', SERIES[k % len(SERIES)])
        if not pts_only:
            pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in s['pts'])
            da = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
            b += f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="3" stroke-linejoin="round"{da}/>'
        if pts_only or s.get('dots'):
            b += ''.join(DOT(X(x), Y(y), 4.5, c) for x, y in s['pts'])
    if title: b += T(ox + w / 2, oy + 20, title, 15, weight='bold')
    return b


def panels(name, items, pw=330, ph=250):
    """أربع لوحات 2×2 مرقمة (1)…(4). items = [dict(series, xr, yr, xs, ys, xlabel?, ylabel?)]"""
    b = ''
    for i, it in enumerate(items):
        ox, oy = (i % 2) * pw, (i // 2) * ph
        b += mini_graph(ox, oy, pw, ph, it['series'], it['xr'], it['yr'], it['xs'], it['ys'], it.get('xlabel', TL), it.get('ylabel', DL), title=f'المنحنى ({i + 1})')
        b += f'<rect x="{ox + 2}" y="{oy + 2}" width="{pw - 4}" height="{ph - 4}" fill="none" stroke="{GRID}" stroke-width="1.5"/>'
    save(name, svg(pw * 2, ph * ((len(items) + 1) // 2), b))


def dots_axis(name, values, vmin, vmax, vstep, unit_label, w=600, start_end=False, reverse_labels=False, note=None, h=130, extra_rows=None):
    """نموذج الجسيم النقطي فوق محور مدرّج بالقيم. values: مواقع النقاط بوحدات المحور."""
    x0, x1 = 50, w - 40
    P = lambda v: x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)
    yd, ya = 50, 82
    b = ''
    for v in values: b += DOT(P(v), yd, 7, BLUE)
    b += ARROW(x0 - 15, ya, x1 + 22, ya, INK, 1.8)
    n = round((vmax - vmin) / vstep)
    for i in range(n + 1):
        v = vmin + i * vstep; b += L(P(v), ya - 6, P(v), ya + 6, INK, 1.5) + T(P(v), ya + 22, fmt(round(v, 6)), 13, color=MUTED)
    b += T((x0 + x1) / 2, ya + 44, unit_label, 14)
    if start_end:
        a, z = values[0], values[-1]
        b += T(P(a), yd - 18, 'البداية', 13, color=GREEN, weight='bold') + T(P(z), yd - 18, 'النهاية', 13, color=RED, weight='bold')
    if note: b += T(w / 2, 18, note, 13, color=MUTED)
    save(name, svg(w, h + 10, b))


# ---------- O01
graph('c2l3-o01-start.svg', [{'pts': [(0, 20), (6, 50)]}], (0, 6), (0, 60), TL, DL, 1, 10)

# ---------- O02
panels('c2l3-o02-panels.svg', [
    dict(series=[{'pts': [(0, 30), (4, 10)]}], xr=(0, 4), yr=(0, 40), xs=1, ys=10),
    dict(series=[{'pts': [(0, 10), (4, 30)]}], xr=(0, 4), yr=(0, 40), xs=1, ys=10),
    dict(series=[{'pts': [(10, 0), (30, 4)]}], xr=(0, 40), yr=(0, 4), xs=10, ys=1, xlabel=DL, ylabel=TL),
    dict(series=[{'pts': [(0, 0), (4, 20)]}], xr=(0, 4), yr=(0, 40), xs=1, ys=10),
])

def bestfit():
    pts = [(1, 2.5), (2, 12.5), (3, 14), (4, 22), (5, 26.5), (6, 27.5)]
    X, Y = graph('c2l3-o02-bestfit.svg', [
        {'pts': [(0, 0), (6, 30)], 'color': BLUE, 'w': 2.5},
        {'pts': pts, 'color': ORANGE, 'w': 2.5, 'dash': '2 4'},
        {'pts': [(0, 10), (6, 20)], 'color': GREEN, 'w': 2.5},
        {'pts': [(0, 0), (4.5, 36)], 'color': PURPLE, 'w': 2.5, 'dash': '9 5'},
    ], (0, 6), (0, 40), TL, DL, 1, 5, w=560, h=380)
    # النقاط والأرقام
    ex = ''.join(DOT(X(x), Y(y), 5, INK) for x, y in pts)
    lab = [(6, 30, '1', BLUE, 14, -2), (5.5, 21.5, '3', GREEN, 6, 14), (4.5, 36, '4', PURPLE, 14, 0), (4, 22, '2', ORANGE, -6, -20)]
    for x, y, t, c, dx, dy in lab:
        ex += f'<circle cx="{X(x) + dx:.1f}" cy="{Y(y) + dy:.1f}" r="11" fill="#fff" stroke="{c}" stroke-width="2"/>' + T(X(x) + dx, Y(y) + dy + 5, t, 14, color=c, weight='bold')
    graph('c2l3-o02-bestfit.svg', [
        {'pts': [(0, 0), (6, 30)], 'color': BLUE, 'w': 2.5},
        {'pts': pts, 'color': ORANGE, 'w': 2.5, 'dash': '2 4'},
        {'pts': [(0, 10), (6, 20)], 'color': GREEN, 'w': 2.5},
        {'pts': [(0, 0), (4.5, 36)], 'color': PURPLE, 'w': 2.5, 'dash': '9 5'},
    ], (0, 6), (0, 40), TL, DL, 1, 5, w=560, h=380, extra=ex)
bestfit()

dots_axis('c2l3-o02-crawl.svg', [0, 20, 40, 60, 80, 100, 120, 140, 160], 0, 160, 20, 'الموقع (cm)')

def misplot():
    s = '<g/>'
    b = mini_graph(0, 0, 520, 360, [{'pts': [(0, 0), (1, 6), (2, 12), (3, 21), (4, 24), (5, 30)], 'color': BLUE}], (0, 5), (0, 36), 1, 3, pts_only=True)
    save('c2l3-o02-misplot.svg', svg(520, 360, b))
misplot()

dots_axis('c2l3-o02-e2.svg', [0, 3, 6, 9, 12, 15], 0, 15, 3, 'الموقع (m)')

# ---------- O03
graph('c2l3-o03-e1.svg', [{'pts': [(0, 0), (5, 40)]}], (0, 5), (0, 40), TL, DL, 0.5, 5)

# ---------- O04
for n in ('a1', 'a2'):
    graph(f'c2l3-o04-{n}.svg', [{'pts': [(0, 10), (8, 50)]}], (0, 8), (0, 60), TL, DL, 1, 10)
for n in ('b1', 'b2'):
    graph(f'c2l3-o04-{n}.svg', [{'pts': [(0, 120), (8, -40)]}], (0, 8), (-60, 140), TL, DL, 1, 20)
C = [(0, 0), (10, 8), (20, 8), (30, 16), (40, 0)]
for n in ('c1', 'c2', 'e2'):
    graph(f'c2l3-o04-{n}.svg', [{'pts': C}], (0, 40), (0, 18), TL, DL, 5, 2)
graph('c2l3-o04-d.svg', [{'pts': [(0, -30), (6, 30)]}], (0, 6), (-40, 40), TL, DL, 1, 10)
graph('c2l3-o04-e1.svg', [{'pts': [(0, 0), (2.5, 10)]}], (0, 2.5), (0, 12), 'الزمن (h)', 'الموقع (km)', 0.5, 1)

# ---------- O05
graph('c2l3-o05-rest.svg', [{'pts': [(0, 30), (6, 30)]}], (0, 6), (0, 40), TL, DL, 1, 10)
graph('c2l3-o05-toward.svg', [{'pts': [(0, 120), (6, 0)]}], (0, 6), (0, 140), TL, DL, 1, 20)
graph('c2l3-o05-ab.svg', [{'pts': [(0, -40), (10, 40)], 'label': 'A', 'color': BLUE, 'at': (10, 40), 'dx': -22, 'dy': -6},
                          {'pts': [(0, 60), (10, -20)], 'label': 'B', 'color': RED, 'at': (10, -20), 'dx': -22, 'dy': -8}],
      (0, 10), (-60, 80), TL, DL, 1, 20)
graph('c2l3-o05-return.svg', [{'pts': [(0, 0), (4, 20), (8, 20), (12, 0)]}], (0, 12), (0, 30), TL, DL, 1, 5)
graph('c2l3-o05-steep.svg', [{'pts': [(0, 0), (4, 8), (6, 28), (10, 36)]}], (0, 10), (0, 40), TL, DL, 1, 4)
graph('c2l3-o05-e1.svg', [{'pts': [(0, 0), (10, 10), (25, 10), (35, 20), (40, 20), (55, 5), (60, 5), (65, 0)]}], (0, 70), (0, 25), TL, DL, 5, 5, w=600)
graph('c2l3-o05-e3.svg', [{'pts': [(0, 0), (3, 3)]}], (0, 3), (0, 3), TL, DL, 0.5, 0.5)

# ---------- O06
dots_axis('c2l3-o06-dots.svg', [0, 5, 10, 15, 20], 0, 20, 5, DL, start_end=True)
graph('c2l3-o06-graph.svg', [{'pts': [(0, 0), (3, 12), (6, 12)]}], (0, 6), (0, 16), TL, DL, 1, 2)
panels('c2l3-o06-panels.svg', [
    dict(series=[{'pts': [(0, 0), (2, 20), (4, 20)]}], xr=(0, 4), yr=(0, 40), xs=1, ys=10),
    dict(series=[{'pts': [(0, 20), (2, 20), (4, 0)]}], xr=(0, 4), yr=(0, 40), xs=1, ys=10),
    dict(series=[{'pts': [(0, 20), (4, 40)]}], xr=(0, 4), yr=(0, 40), xs=1, ys=10),
    dict(series=[{'pts': [(0, 20), (2, 20), (4, 40)]}], xr=(0, 4), yr=(0, 40), xs=1, ys=10),
])
dots_axis('c2l3-o06-left.svg', [40, 30, 20, 10, 0], 0, 40, 10, DL, start_end=True)

def compare():
    w = 560
    x0, x1 = 60, w - 50; P = lambda v: x0 + v / 14 * (x1 - x0)
    b = T(w / 2, 22, 'نموذج الجسيم النقطي: الفترة الزمنية بين كل نقطتين متتاليتين ثانيتان', 13, color=MUTED)
    for v in [0, 2, 4, 6, 8, 10, 12]: b += DOT(P(v), 50, 7, BLUE)
    b += ARROW(x0 - 15, 80, x1 + 22, 80, INK, 1.8)
    for v in range(0, 15, 2): b += L(P(v), 74, P(v), 86, INK, 1.5) + T(P(v), 102, str(v), 13, color=MUTED)
    b += T((x0 + x1) / 2, 124, DL, 13)
    b += L(10, 140, w - 10, 140, GRID, 1.5)
    b += mini_graph(70, 150, 420, 300, [{'pts': [(0, 0), (3, 12)]}], (0, 4), (0, 16), 1, 2, title='منحنى (الموقع – الزمن)')
    save('c2l3-o06-compare.svg', svg(w, 460, b))
compare()
dots_axis('c2l3-o06-e1.svg', [0, 1.5, 3, 4.5, 6, 7.5, 9], 0, 9, 1.5, DL, start_end=True)
graph('c2l3-o06-e3.svg', [{'pts': [(0, 0), (2, 6), (4, 6), (6, 0)]}], (0, 6), (0, 8), TL, DL, 1, 1)

# ---------- O07
def three(name, ts, ds, ystep, ymax):
    w = 760
    b = ''
    # جدول
    tx, ty, cw, rh = 20, 30, 80, 30
    b += T(tx + cw, 20, 'جدول البيانات', 14, weight='bold')
    b += RECT(tx, ty, cw, rh, fill='#e3ecf6') + RECT(tx + cw, ty, cw, rh, fill='#e3ecf6')
    b += T(tx + cw / 2, ty + 20, 'الزمن (s)', 13) + T(tx + cw * 1.5, ty + 20, 'الموقع (m)', 13)
    for i, (t, d) in enumerate(zip(ts, ds)):
        yy = ty + rh * (i + 1)
        b += RECT(tx, yy, cw, rh, fill='#fff') + RECT(tx + cw, yy, cw, rh, fill='#fff')
        b += T(tx + cw / 2, yy + 20, f'{t:.1f}', 14) + T(tx + cw * 1.5, yy + 20, f'{d:.1f}', 14)
    # منحنى
    b += mini_graph(200, 0, 330, 270, [{'pts': list(zip(ts, ds))}], (0, ts[-1]), (0, ymax), 1, ystep, title='منحنى (الموقع – الزمن)')
    # نموذج الجسيم
    x0, x1 = 560, 740; P = lambda v: x0 + v / ymax * (x1 - x0)
    b += T(650, 20, 'نموذج الجسيم النقطي', 14, weight='bold')
    for d in ds: b += DOT(P(d), 130, 6, BLUE)
    b += ARROW(x0 - 8, 160, x1 + 14, 160, INK, 1.6)
    for v in range(0, int(ymax) + 1, int(ystep * 2)): b += L(P(v), 154, P(v), 166, INK, 1.3) + T(P(v), 182, str(v), 12, color=MUTED)
    b += T(650, 204, DL, 13)
    b += T(650, 228, 'الفترة بين كل نقطتين: ثانية واحدة', 12, color=MUTED)
    save(name, svg(w, 280, b))
three('c2l3-o07-three.svg', [0, 1, 2, 3, 4], [0, 4, 8, 12, 16], 2, 16)
three('c2l3-o07-e2.svg', [0, 1, 2, 3, 4], [2, 5, 8, 11, 14], 2, 16)

# ---------- O08
AB = [{'pts': [(0, 0), (30, 90)], 'label': 'A', 'color': BLUE, 'at': (30, 90), 'dx': -20, 'dy': 18},
      {'pts': [(0, -40), (30, 110)], 'label': 'B', 'color': RED, 'at': (30, 110), 'dx': -22, 'dy': -4}]
for n in ('1', '2', '3', '4'):
    graph(f'c2l3-o08-ab{n}.svg', AB, (0, 30), (-40, 120), TL, DL, 5, 10, w=540, h=420)
HK = [{'pts': [(0, 0), (2.5, 10)], 'label': 'أحمد', 'color': BLUE, 'at': (2.5, 10), 'dx': -10, 'dy': 22},
      {'pts': [(0.5, 0), (2.5, 12)], 'label': 'نبيل', 'color': RED, 'at': (2.0, 9), 'dx': -50, 'dy': -6}]
for n in ('1', '2'):
    graph(f'c2l3-o08-hike{n}.svg', HK, (0, 2.5), (0, 12), 'الزمن (h)', 'الموقع (km)', 0.5, 1, w=540, h=400)
graph('c2l3-o08-e1.svg', [{'pts': [(0, 0), (30, 150)], 'label': 'A', 'color': BLUE, 'at': (30, 150), 'dx': -20, 'dy': -6},
                          {'pts': [(0, 300), (30, 0)], 'label': 'B', 'color': RED, 'at': (3, 270), 'dx': 14, 'dy': 4}],
      (0, 30), (0, 300), TL, DL, 5, 50, w=540, h=400)
graph('c2l3-o08-e3.svg', [{'pts': [(0, 0), (20, 80)], 'label': 'A', 'color': BLUE, 'at': (20, 80), 'dx': -4, 'dy': 22},
                          {'pts': [(0, 30), (10, 30), (20, 90)], 'label': 'B', 'color': RED, 'at': (20, 90), 'dx': -24, 'dy': -4}],
      (0, 20), (0, 100), TL, DL, 2.5, 10, w=560, h=420)

# ---------- O09
graph('c2l3-o09-puck.svg', [{'pts': [(0, 0), (6, 90)]}], (0, 6), (0, 100), TL, DL, 1, 10)
graph('c2l3-o09-neg.svg', [{'pts': [(0, 60), (6, -30)]}], (0, 6), (-40, 70), TL, DL, 1, 10, h=380)
graph('c2l3-o09-trip.svg', [{'pts': [(0, 5), (4, 25), (6, 25), (10, 15)]}], (0, 10), (0, 30), TL, DL, 1, 5)
graph('c2l3-o09-flat.svg', [{'pts': [(0, 0), (3, 30), (7, 30), (10, 60)]}], (0, 10), (0, 70), TL, DL, 1, 10)
graph('c2l3-o09-cross.svg', [{'pts': [(0, -20), (5, 30)]}], (0, 5), (-30, 40), TL, DL, 1, 10)
graph('c2l3-o09-two.svg', [{'pts': [(0, 0), (4, 40)], 'label': 'A', 'color': BLUE, 'at': (4, 40), 'dx': -4, 'dy': 20},
                           {'pts': [(0, 20), (4, 60)], 'label': 'B', 'color': RED, 'at': (4, 60), 'dx': -24, 'dy': -2}],
      (0, 4), (0, 70), TL, DL, 1, 10)
graph('c2l3-o09-e1.svg', [{'pts': [(0, 0), (10, 40), (20, 40), (30, 10), (40, 10)]}], (0, 40), (0, 50), TL, DL, 5, 10)
graph('c2l3-o09-e2.svg', [{'pts': [(0, 100), (6, -50)]}], (0, 6), (-60, 120), TL, DL, 1, 20, h=380)
graph('c2l3-o09-e3.svg', [{'pts': [(0, 15), (8, 55)]}], (0, 8), (0, 60), TL, DL, 1, 5, h=380)

# ---------- O10
graph('c2l3-o10-hill.svg', [{'pts': [(0, 0), (5, 50), (10, 0)]}], (0, 10), (0, 60), TL, DL, 1, 10)
graph('c2l3-o10-cross.svg', [{'pts': [(0, 0), (30, 90)], 'label': 'A', 'color': BLUE, 'at': (30, 90), 'dx': -4, 'dy': 22},
                             {'pts': [(0, 20), (30, 80)], 'label': 'B', 'color': RED, 'at': (30, 80), 'dx': -4, 'dy': 24}],
      (0, 30), (0, 100), TL, DL, 5, 10)
graph('c2l3-o10-e2.svg', [{'pts': [(0, 0), (30, 45)], 'label': 'A', 'color': BLUE, 'at': (30, 45), 'dx': -24, 'dy': -2},
                          {'pts': [(0, 50), (30, 20)], 'label': 'B', 'color': RED, 'at': (30, 20), 'dx': -24, 'dy': 20}],
      (0, 30), (0, 50), TL, DL, 5, 5)
