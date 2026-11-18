import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-2 الموقع والزمن (الأهداف O11–O19): الفترة الزمنية وساعات الإيقاف، المسافة والإزاحة على خط الأعداد،
# متجهات الإزاحة على نموذج الجسيم النقطي (أخضر)، طرح المتجهات، نقل المتجه، المحصلة على الرسم، أثر اختيار النظام الإحداثي.

LIGHT = '#eef2f8'


def numline(lo, hi, step, x0, x1, y, every=1, letter='d', unit='(m)', minor=None):
    """محور الموقع الأفقي مع تدريج. يعيد (svg, P) حيث P تحوّل القيمة إلى بكسل."""
    P = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = ARROW(x0 - 14, y, x1 + 26, y, INK, 1.8)
    if minor:
        n = round((hi - lo) / minor)
        for i in range(n + 1): b += L(P(lo + i * minor), y - 4, P(lo + i * minor), y + 4, INK, 1)
    n = round((hi - lo) / step)
    for i in range(n + 1):
        v = round(lo + i * step, 6)
        b += L(P(v), y - 7, P(v), y + 7, INK, 1.6)
        if i % every == 0: b += T(P(v), y + 24, fmt(v), 14, color=INK)
    b += T(x1 + 34, y - 10, letter, 17, 'start', italic=True) + T(x1 + 34, y + 24, unit, 13, 'start', MUTED)
    return b, P


def stopwatch(cx, cy, reading, label=None, sub=None):
    b = f'<rect x="{cx - 9}" y="{cy - 44}" width="18" height="10" rx="2" fill="#c9d1dd" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<rect x="{cx - 62}" y="{cy - 34}" width="124" height="62" rx="14" fill="{LIGHT}" stroke="{INK}" stroke-width="2"/>'
    b += f'<rect x="{cx - 48}" y="{cy - 22}" width="96" height="38" rx="5" fill="#dfe9d8" stroke="{INK}" stroke-width="1.5"/>'
    b += T(cx, cy + 6, reading, 20, weight='bold')
    if label: b += T(cx, cy + 50, label, 14, weight='bold')
    if sub: b += T(cx, cy + 70, sub, 14, color=MUTED, italic=True)
    return b


def grid(x0, y0, cols, rows, u):
    b = ''
    for i in range(cols + 1): b += L(x0 + i * u, y0, x0 + i * u, y0 + rows * u, GRID, 1)
    for j in range(rows + 1): b += L(x0, y0 + j * u, x0 + cols * u, y0 + j * u, GRID, 1)
    return b


def gvec(G, p, q, label=None, color=C_DISP, dash=False, lpos=(0, -12), w=3, size=18):
    """متجه على شبكة: G تحوّل (x, y) بوحدات الشبكة (y لأعلى) إلى بكسل."""
    (x1, y1), (x2, y2) = G(p), G(q)
    if dash:
        a = math.atan2(y2 - y1, x2 - x1)
        b = L(x1, y1, x2 - 8 * math.cos(a), y2 - 8 * math.sin(a), color, 2.4, '7 5')
        b += f'<polygon points="{x2:.1f},{y2:.1f} {x2 - 12 * math.cos(a - 0.38):.1f},{y2 - 12 * math.sin(a - 0.38):.1f} {x2 - 12 * math.cos(a + 0.38):.1f},{y2 - 12 * math.sin(a + 0.38):.1f}" fill="{color}"/>'
    else:
        b = ARROW(x1, y1, x2, y2, color, w, 12)
    if label: b += V((x1 + x2) / 2 + lpos[0], (y1 + y2) / 2 + lpos[1], label, color, size)
    return b


def scale_note(x, y, num, label='ضلع المربع يمثل'):
    """مقياس الرسم: الرقم والوحدة يسارًا ثم النص العربي يمينه (حتى لا ينقلب الترتيب)."""
    return T(x, y, num, 14, 'start', MUTED) + T(x + 9 * len(num) + 8, y, label, 14, 'start', MUTED)


def gmap(ox, oy, u): return lambda p: (ox + p[0] * u, oy - p[1] * u)


def north(x, y):
    return ARROW(x, y + 18, x, y - 22, INK, 2, 9) + T(x, y - 30, 'شمال', 13, weight='bold')


def east_mark(x, y):
    return ARROW(x - 20, y, x + 22, y, INK, 2, 9) + T(x + 30, y + 5, 'شرق', 13, 'start', weight='bold')


# ======================= O11 / O12 الفترة الزمنية =======================
def fig_o11():
    w, h = 640, 250; b = ''
    lb, P = numline(0, 30, 5, 50, 560, 200)
    b += lb
    for v, lab in [(5, '1'), (25, '2')]:
        b += DOT(P(v), 170, 7, INK) + T(P(v), 154, lab, 16, weight='bold')
        b += L(P(v), 140, P(v), 120, MUTED, 1.2, '4 4')
    b += stopwatch(P(5), 70, '2.0 s', None) + T(P(5) + 78, 70, 't_i', 18, 'start', italic=True)
    b += stopwatch(P(25), 70, '7.5 s', None) + T(P(25) + 78, 70, 't_f', 18, 'start', italic=True)
    save('c2l2-o11-stopwatches.svg', svg(w, h, b))


def fig_o12_watch():
    w, h = 520, 170; b = ''
    b += stopwatch(140, 70, '3.4 s', 'عند خط البداية')
    b += stopwatch(380, 70, '9.1 s', 'عند خط النهاية')
    b += ARROW(225, 70, 295, 70, MUTED, 2, 10)
    save('c2l2-o12-stopwatch.svg', svg(w, h, b))


def fig_o12_dots():
    w, h = 620, 120; b = ''
    xs = [50, 80, 120, 170, 230, 300, 380, 470]
    b += L(30, 70, 590, 70, GRID, 1.5)
    for k, x in enumerate(xs):
        b += DOT(x, 70, 7, INK)
    b += T(xs[1], 48, 'A', 17, weight='bold', italic=True) + T(xs[6], 48, 'B', 17, weight='bold', italic=True)
    b += ARROW(500, 100, 590, 100, MUTED, 1.8, 9) + T(495, 105, 'اتجاه الحركة', 13, 'end', MUTED)
    save('c2l2-o12-dots.svg', svg(w, h, b))


def fig_o12_graph():
    graph('c2l2-o12-graph.svg', [{'pts': [(0, 0), (7, 140)], 'color': C_DISP}], (0, 7), (0, 140), 'الزمن (s)', 'الموقع (m)', 1, 20)


# ======================= O13 / O14 المسافة والإزاحة =======================
def path_figure(name, lo, hi, step, every, pts, labels, w=640, minor=None):
    """مسار جسم ذهابًا وإيابًا فوق محور الموقع: أسهم المسار سوداء على مستويات مختلفة (لا تمثل الإزاحة)."""
    h = 150 + 32 * (len(pts) - 1); ya = h - 50; b = ''
    lb, P = numline(lo, hi, step, 50, w - 80, ya, every, minor=minor); b += lb
    for v, lab in zip(pts, labels):
        b += DOT(P(v), ya, 7, INK)
    # تسميات النقاط
    used = {}
    for v, lab in zip(pts, labels):
        k = used.get(v, 0); used[v] = k + 1
        b += T(P(v), ya - 16 - 18 * k, lab, 15, weight='bold')
    for k in range(len(pts) - 1):
        yy = ya - 70 - 32 * k
        b += L(P(pts[k]), ya - 10 if k == 0 else yy + 32, P(pts[k]), yy, MUTED, 1.2, '3 4')
        b += ARROW(P(pts[k]), yy, P(pts[k + 1]), yy, INK, 2.4, 10)
        b += L(P(pts[k + 1]), yy, P(pts[k + 1]), ya - 10, MUTED, 1.2, '3 4')
    save(name, svg(w, h, b))


def fig_o13_backforth():
    path_figure('c2l2-o13-backforth.svg', 0, 10, 1, 1, [2, 9, 5], ['البداية', '', 'النهاية'])


def fig_o14_numline():
    path_figure('c2l2-o14-numline.svg', -30, 50, 10, 1, [30, 40, -20], ['A', 'B', 'C'], minor=5)


def fig_o13_track():
    w, h = 420, 300; cx, cy, r = 210, 150, 105; b = ''
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="{r + 60}" ry="{r}" fill="#f3efe6" stroke="{INK}" stroke-width="2"/>'
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="{r + 30}" ry="{r - 30}" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    sx, sy = cx, cy + r - 15
    b += L(sx, cy + r - 30, sx, cy + r, INK, 3)
    b += DOT(sx, sy, 7, C_VEL) + T(sx, cy + r + 22, 'البداية والنهاية', 14, weight='bold')
    # سهم اتجاه الجري (عكس عقارب الساعة) على المسار
    a1, a2 = math.radians(20), math.radians(70)
    rx, ry = r + 45, r - 15
    px = [cx + rx * math.cos(a) for a in (a1, a2)]; py = [cy - ry * math.sin(a) for a in (a1, a2)]
    b += f'<path d="M {px[0]:.1f} {py[0]:.1f} A {rx} {ry} 0 0 0 {px[1]:.1f} {py[1]:.1f}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    b += ARROW(px[1] + 8, py[1] - 3, px[1] - 4, py[1] - 7, INK, 2.4, 11)
    save('c2l2-o13-track.svg', svg(w, h, b))


def fig_o14_maze():
    u = 26; ox, oy = 90, 330; G = gmap(ox, oy, u); b = ''
    b += grid(ox - 2 * u, oy - 12 * u, 11, 13, u)
    path = [(0, 0), (0, 10), (3, 10), (3, 2), (7, 2)]
    for p, q in zip(path, path[1:]): b += gvec(G, p, q, None, INK, w=3)
    b += DOT(*G((0, 0)), 6, INK) + T(G((0, 0))[0], G((0, 0))[1] + 22, 'البداية', 14, weight='bold')
    b += DOT(*G((7, 2)), 6, INK) + T(G((7, 2))[0], G((7, 2))[1] + 22, 'النهاية', 14, weight='bold')
    b += north(420, 60) + east_mark(400, 120)
    b += T(430, 175, 'طول ضلع المربع', 13, color=MUTED) + T(430, 195, '0.1 m', 14, color=MUTED)
    save('c2l2-o14-maze.svg', svg(500, 380, b))


# ======================= O15 متجهات الإزاحة على نموذج الجسيم النقطي =======================
def fig_o15_car():
    w = 620; xs = [60, 100, 160, 240, 340, 460]; yd = 50; b = ''
    b += L(40, yd, 580, yd, GRID, 1.5)
    for k, x in enumerate(xs):
        b += DOT(x, yd, 7, INK) + L(x, yd + 12, x, 300, GRID, 1.2, '3 4')
    b += T(xs[0], yd - 18, 'البداية', 14, weight='bold')
    rows = [(0, 3), (3, 0), (0, 2), (0, 5)]
    for k, (i, j) in enumerate(rows):
        y = 100 + 52 * k
        b += ARROW(xs[i], y, xs[j], y, C_DISP, 3.2, 12) + T(600, y + 5, f'({k + 1})', 15, 'end', weight='bold')
    save('c2l2-o15-car.svg', svg(w, 310, b))


def fig_o15_student():
    w, h = 640, 150; xs = [70, 190, 310, 430, 550]; yd = 95; b = ''
    b += L(50, yd, 590, yd, GRID, 1.5)
    for x in xs: b += DOT(x, yd, 7, INK)
    b += T(xs[0], yd + 30, 'البيت', 15, weight='bold') + T(xs[-1], yd + 30, 'المدرسة', 15, weight='bold')
    for k in range(4):
        a, c = (xs[k] + 10, xs[k + 1] - 10) if k != 2 else (xs[k + 1] - 10, xs[k] + 10)
        b += ARROW(a, yd - 22, c, yd - 22, C_DISP, 3, 11) + T((xs[k] + xs[k + 1]) / 2, yd - 36, f'({k + 1})', 15, weight='bold')
    save('c2l2-o15-student.svg', svg(w, h, b))


def fig_o15_essay():
    w, h = 660, 140; b = ''
    lb, P = numline(0, 100, 10, 50, 570, 95, 1); b += lb
    for v, lab in zip([0, 10, 30, 60, 100], ['1', '2', '3', '4', '5']):
        b += DOT(P(v), 60, 7, INK) + T(P(v), 38, lab, 15, weight='bold')
    save('c2l2-o15-essay.svg', svg(w, h, b))


def fig_o15_scale():
    """نموذج جسيم نقطي فوق محور مع متجهي إزاحة مرسومين بين نقاط متتالية (لسؤال القراءة)."""
    w, h = 640, 170; b = ''
    lb, P = numline(0, 60, 10, 50, 560, 125, 1, minor=5); b += lb
    vals = [5, 15, 30, 50]
    for v, lab in zip(vals, ['1', '2', '3', '4']):
        b += DOT(P(v), 90, 7, INK) + T(P(v), 115 - 50, lab, 15, weight='bold')
    b += ARROW(P(5), 40, P(50), 40, C_DISP, 3.2, 12)
    save('c2l2-o15-scale.svg', svg(w, h, b))


# ======================= O16 طرح المتجهات =======================
def fig_o16_AB(name, A, B, scale_note_txt):
    """متجهان أفقيان مرسومان منفصلين على شبكة. A وB بالمربعات (موجب = شرق)."""
    u = 34; cols = 12; b = ''; ox, oy = 40, 40
    b += grid(ox, oy, cols, 4, u)
    G = gmap(ox, oy + 4 * u, u)
    a0 = 1; b += gvec(G, (a0, 3), (a0 + A, 3), 'A', lpos=(0, -12))
    b0 = 1 if B > 0 else 1 - B; b += gvec(G, (b0, 1), (b0 + B, 1), 'B', lpos=(0, -12))
    b += east_mark(ox + cols * u - 50, oy + 4 * u + 30)
    b += scale_note(ox, oy + 4 * u + 35, scale_note_txt)
    save(name, svg(ox * 2 + cols * u, oy + 4 * u + 60, b))


def fig_o16_panels():
    u = 30; pw, ph = 260, 200; b = ''
    # المتجهان الأصليان في الأعلى
    top = 90; G0 = gmap(40, top - 10, u)
    b += T(270, 24, 'المتجهان الأصليان', 15, weight='bold', color=MUTED)
    b += gvec(G0, (1, 0), (5, 0), 'A', lpos=(0, -12)) + gvec(G0, (9, -1), (9, 1), 'B', lpos=(16, 4))
    cons = [
        [((0, 0), (4, 0), 'A', (0, -12)), ((4, 0), (4, -2), '−B', (22, 4)), 'R', ((0, 0), (4, -2))],
        [((0, 0), (4, 0), 'A', (0, 22)), ((4, 0), (4, 2), 'B', (16, 4)), 'R', ((0, 0), (4, 2))],
        [((4, 0), (0, 0), '−A', (0, 22)), ((0, 0), (0, 2), 'B', (-16, 4)), 'R', ((4, 0), (0, 2))],
        [((0, 0), (4, 0), 'A', (0, -12)), ((0, 0), (0, -2), '−B', (-24, 4)), 'R', ((4, 0), (0, -2))],
    ]
    for k, c in enumerate(cons):
        px, py = 10 + (k % 2) * (pw + 10), top + 20 + (k // 2) * (ph + 10)
        b += f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
        b += T(px + 20, py + 24, f'({k + 1})', 15, weight='bold')
        G = gmap(px + 70, py + 105, u)
        for (p, q, lab, lp) in c[:2]: b += gvec(G, p, q, lab, lpos=lp)
        b += gvec(G, c[3][0], c[3][1], None, dash=True)
    save('c2l2-o16-panels.svg', svg(560, top + 20 + 2 * ph + 20, b))


def fig_o16_dfdi():
    w, h = 640, 190; b = ''
    lb, P = numline(0, 12, 1, 50, 560, 150, 1); b += lb
    b += DOT(P(0), 150, 5, INK) + T(P(0), 128, 'نقطة الأصل', 13, color=MUTED)
    b += ARROW(P(0), 95, P(4), 95, C_DISP, 3, 12) + V(P(2), 82, 'd_i', C_DISP)
    b += ARROW(P(0), 55, P(10), 55, C_DISP, 3, 12) + V(P(5), 42, 'd_f', C_DISP)
    b += DOT(P(4), 150, 6, INK) + DOT(P(10), 150, 6, INK)
    save('c2l2-o16-dfdi.svg', svg(w, h, b))


# ======================= O17 نقل المتجه =======================
def fig_o17_copies():
    u = 30; ox, oy = 20, 20; cols, rows = 18, 9; b = grid(ox, oy, cols, rows, u)
    G = gmap(ox, oy + rows * u, u)
    b += gvec(G, (1, 3), (4, 5), 'A', lpos=(-14, -10))
    b += gvec(G, (6, 6), (9, 8), None) + T(*G((7.2, 7.8)), '(1)', 15, weight='bold')
    b += gvec(G, (6, 1), (10.5, 4)) + T(*G((7.6, 3.5)), '(2)', 15, weight='bold')
    b += gvec(G, (12, 4), (14, 7)) + T(*G((12.2, 6.3)), '(3)', 15, weight='bold')
    b += gvec(G, (16, 3), (13, 1)) + T(*G((15.3, 1.0)), '(4)', 15, weight='bold')
    save('c2l2-o17-copies.svg', svg(ox * 2 + cols * u, oy * 2 + rows * u, b))


def fig_o17_wrong():
    u = 32; b = ''
    b += T(150, 24, 'المتجهان الأصليان', 14, weight='bold', color=MUTED)
    b += T(470, 24, 'رسم الطالب', 14, weight='bold', color=MUTED)
    G1 = gmap(40, 200, u); b += grid(40, 200 - 5 * u, 7, 5, u)
    b += gvec(G1, (0.5, 1), (4.5, 1), 'A', lpos=(0, 20)) + gvec(G1, (5.5, 0.5), (5.5, 3.5), 'B', lpos=(16, 4))
    G2 = gmap(320, 200, u); b += grid(320, 200 - 5 * u, 9, 5, u)
    b += gvec(G2, (0.5, 2), (4.5, 2), 'A', lpos=(0, -12)) + gvec(G2, (4.5, 2), (7.5, 2), 'B', lpos=(0, -12))
    b += gvec(G2, (0.5, 1), (7.5, 1), 'R', dash=True, lpos=(0, 22))
    save('c2l2-o17-wrong.svg', svg(640, 230, b))


# ======================= O18 المحصلة على الرسم =======================
def fig_o18_panels():
    u = 26; pw, ph = 250, 180; b = ''
    O, Pp, Q = (0, 0), (4, 0), (4, 3)
    for k in range(4):
        px, py = 10 + (k % 2) * (pw + 10), 10 + (k // 2) * (ph + 10)
        b += f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
        b += T(px + 22, py + 24, f'({k + 1})', 15, weight='bold')
        G = gmap(px + 50, py + ph - 40, u)
        if k < 3:
            b += gvec(G, O, Pp, 'A', lpos=(0, 22) if k < 2 else (0, -10)) + gvec(G, Pp, Q, 'B', lpos=(16, 4))
            cand = [(O, Q), (Q, O), ((0, -0.7), (7, -0.7))][k]
            b += gvec(G, cand[0], cand[1], None, dash=True)
        else:
            b += gvec(G, O, Pp, 'A', lpos=(0, 22)) + gvec(G, O, (0, 3), 'B', lpos=(-16, 4))
            b += gvec(G, Pp, (0, 3), None, dash=True)
    save('c2l2-o18-panels.svg', svg(540, 2 * ph + 30, b))


def fig_o18_scale1d():
    u = 40; cols = 11; ox, oy = 30, 30; b = grid(ox, oy, cols, 2, u)
    G = gmap(ox, oy + 2 * u, u)
    b += gvec(G, (1, 1), (7, 1), 'A', lpos=(0, -12)) + gvec(G, (7, 1), (10, 1), 'B', lpos=(0, -12))
    b += east_mark(ox + cols * u - 60, oy + 2 * u + 30)
    b += scale_note(ox, oy + 2 * u + 35, '0.1 km')
    save('c2l2-o18-scale1d.svg', svg(ox * 2 + cols * u, oy + 2 * u + 55, b))


def fig_o18_opposite():
    u = 40; cols = 9; ox, oy = 30, 30; b = grid(ox, oy, cols, 3, u)
    G = gmap(ox, oy + 3 * u, u)
    b += gvec(G, (1, 2), (7, 2), 'A', lpos=(0, -12)) + gvec(G, (7, 1), (5, 1), 'B', lpos=(0, 22))
    b += L(*G((7, 2)), *G((7, 1)), MUTED, 1.4, '4 4')
    b += east_mark(ox + cols * u - 60, oy + 3 * u + 30)
    b += scale_note(ox, oy + 3 * u + 35, '5 m')
    save('c2l2-o18-opposite.svg', svg(ox * 2 + cols * u, oy + 3 * u + 55, b))


def fig_o18_2d():
    u = 40; ox, oy = 40, 30; cols, rows = 6, 5; b = grid(ox, oy, cols, rows, u)
    G = gmap(ox, oy + rows * u, u)
    O, Pp, Q = (1, 0.5), (4, 0.5), (4, 4.5)
    b += gvec(G, O, Pp, 'A', lpos=(0, 22)) + gvec(G, Pp, Q, 'B', lpos=(18, 4))
    for p, lab, d in [(O, 'O', (-16, 6)), (Pp, 'P', (16, 18)), (Q, 'Q', (16, -6))]:
        x, y = G(p); b += DOT(x, y, 4, INK) + T(x + d[0], y + d[1], lab, 16, weight='bold', italic=True)
    b += north(ox + cols * u + 50, oy + 50) + east_mark(ox + cols * u + 40, oy + 120)
    save('c2l2-o18-2d.svg', svg(ox + cols * u + 110, oy * 2 + rows * u, b))


def fig_o18_essay():
    u = 40; ox, oy = 40, 30; cols, rows = 6, 4; b = grid(ox, oy, cols, rows, u)
    G = gmap(ox, oy + rows * u, u)
    pts = [(1, 0.5), (5, 0.5), (5, 3.5), (3, 3.5)]
    for (p, q), lab, lp in zip(zip(pts, pts[1:]), ['A', 'B', 'C'], [(0, 22), (18, 4), (0, -12)]):
        b += gvec(G, p, q, lab, lpos=lp)
    b += north(ox + cols * u + 50, oy + 40) + east_mark(ox + cols * u + 40, oy + 110)
    save('c2l2-o18-essay.svg', svg(ox + cols * u + 110, oy * 2 + rows * u, b))


# ======================= O19 أثر اختيار النظام الإحداثي =======================
def fig_o19_two():
    w, h = 640, 250; b = ''
    b += T(20, 30, '(a)', 15, 'start', weight='bold')
    la, Pa = numline(0, 30, 5, 60, 540, 85, 1); b += la
    b += T(20, 160, '(b)', 15, 'start', weight='bold')
    lb_, Pb = numline(-30, 0, 5, 60, 540, 215, 1); b += lb_
    for v, lab in [(5, '1'), (25, '2')]:
        x = Pa(v); b += DOT(x, 55, 7, INK) + T(x, 37, lab, 15, weight='bold')
        b += DOT(x, 185, 7, INK) + T(x, 167, lab, 15, weight='bold')
    b += T(Pa(0), 125, 'نقطة الأصل', 12, color=MUTED)
    save('c2l2-o19-two.svg', svg(w, h, b))


def fig_o19_mid():
    w, h = 640, 130; b = ''
    lb, P = numline(-10, 10, 2, 50, 560, 90, 1); b += lb
    b += DOT(P(-6), 60, 7, INK) + T(P(-6), 42, 'A', 16, weight='bold', italic=True)
    b += DOT(P(4), 60, 7, INK) + T(P(4), 42, 'B', 16, weight='bold', italic=True)
    save('c2l2-o19-mid.svg', svg(w, h, b))


if __name__ == '__main__':
    fig_o11(); fig_o12_watch(); fig_o12_dots(); fig_o12_graph()
    fig_o13_backforth(); fig_o14_numline(); fig_o13_track(); fig_o14_maze()
    fig_o15_car(); fig_o15_student(); fig_o15_essay(); fig_o15_scale()
    fig_o16_AB('c2l2-o16-AB.svg', 5, 2, '1 m')
    fig_o16_AB('c2l2-o16-west.svg', 3, -2, '10 m')
    fig_o16_panels(); fig_o16_dfdi()
    fig_o17_copies(); fig_o17_wrong()
    fig_o18_panels(); fig_o18_scale1d(); fig_o18_opposite(); fig_o18_2d(); fig_o18_essay()
    fig_o19_two(); fig_o19_mid()
