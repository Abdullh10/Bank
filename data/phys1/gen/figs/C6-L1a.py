import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 6-1 (حركة المقذوف) — الأهداف O01–O09
# الألوان كالكتاب: السرعة ومركّبتاها أحمر، التسارع بنفسجي (رأسي إلى أسفل فقط)، القوى أزرق تبدأ من الجسم.
import math, re


def pol(cx, cy, ang, r):
    a = math.radians(ang); return cx + r * math.cos(a), cy - r * math.sin(a)


def Vd(x, y, s, color=C_FORCE, size=17, anchor='middle'):
    """رمز متجه بحرف سفلي قائم (F_d كما يكتبه الكتاب)."""
    return re.sub(r'(<tspan dy="0.3em" font-size="\d+" font-weight="normal")>', r'\1 font-style="normal">', V(x, y, s, color, size, anchor))


def FA(cx, cy, ang, length, label='', color=C_FORCE, dx=0, dy=0, size=17, lab_r=None, upright=False):
    """سهم متجه يبدأ من (cx, cy) بزاوية ang (0 = يمين، 90 = أعلى)."""
    x2, y2 = pol(cx, cy, ang, length); b = ARROW(cx, cy, x2, y2, color, 3)
    if label:
        lx, ly = pol(cx, cy, ang, lab_r or length + 20); lx += dx; ly += dy + 6
        b += (Vd if upright else V)(lx, ly, label, color, size)
    return b


def DASHARROW(x1, y1, x2, y2, color=C_VEL, w=2.2):
    a = math.atan2(y2 - y1, x2 - x1); head = 10
    p1 = (x2 - head * math.cos(a - 0.4), y2 - head * math.sin(a - 0.4)); p2 = (x2 - head * math.cos(a + 0.4), y2 - head * math.sin(a + 0.4))
    return L(x1, y1, x2 - 0.6 * head * math.cos(a), y2 - 0.6 * head * math.sin(a), color, w, '6 4') + f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'


def ARC(cx, cy, r, a1, a2, color=INK, w=1.5):
    x1, y1 = pol(cx, cy, a1, r); x2, y2 = pol(cx, cy, a2, r)
    large = 1 if (a2 - a1) % 360 > 180 else 0
    return f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 0 {x2:.1f} {y2:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>'


def AXES(x, y, r=46):
    """مؤشر الاتجاهين الموجبين: +x إلى اليمين و+y إلى أعلى."""
    return (ARROW(x, y, x + r, y, MUTED, 1.6, 9) + ARROW(x, y, x, y - r, MUTED, 1.6, 9)
            + T(x + r + 4, y + 5, '+x', 14, 'start', MUTED, italic=True) + T(x, y - r - 6, '+y', 14, 'middle', MUTED, italic=True))


def NUMLAB(x, y, n):
    return T(x, y, f'({n})', 16, color=INK, weight='bold')


def BALL(x, y, r=8):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#f2c94c" stroke="{INK}" stroke-width="1.5"/>'


def PATH(pts, color=INK, w=2, dash='6 5'):
    p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts); da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}"{da} stroke-linejoin="round"/>'


def parab(x0, y0, vx, vy, g, t1, n=60):
    """نقاط مسار (بكسل): x = x0 + vx t، y = y0 − (vy t − g t²/2)."""
    return [(x0 + vx * t1 * k / n, y0 - (vy * t1 * k / n - 0.5 * g * (t1 * k / n) ** 2)) for k in range(n + 1)]


def GROUND(x1, x2, y):
    b = L(x1, y, x2, y, INK, 2)
    for k in range(int((x2 - x1) // 14)):
        b += L(x1 + 6 + k * 14, y, x1 + k * 14, y + 7, MUTED, 1)
    return b


def DIM_V(x, y1, y2, label, side='end'):
    """بُعد رأسي بسهمين وتسمية."""
    b = ARROW(x, (y1 + y2) / 2, x, y1 + 1, INK, 1.4, 8) + ARROW(x, (y1 + y2) / 2, x, y2 - 1, INK, 1.4, 8)
    b += L(x - 7, y1, x + 7, y1, INK, 1.4) + L(x - 7, y2, x + 7, y2, INK, 1.4)
    return b + T(x - 10 if side == 'end' else x + 10, (y1 + y2) / 2 + 5, label, 15, side)


def DIM_H(x1, x2, y, label, italic=False):
    b = ARROW((x1 + x2) / 2, y, x1 + 1, y, INK, 1.4, 8) + ARROW((x1 + x2) / 2, y, x2 - 1, y, INK, 1.4, 8)
    b += L(x1, y - 7, x1, y + 7, INK, 1.4) + L(x2, y - 7, x2, y + 7, INK, 1.4)
    return b + T((x1 + x2) / 2, y + 22, label, 15, italic=italic)


# ================= O01 =================
def o01_table_stages():
    w, h = 560, 330; b = ''
    ty = 130; gy = 300
    b += RECT(30, ty, 220, 14, INK, '#d8c3a5') + RECT(44, ty + 14, 12, gy - ty - 14, INK, '#d8c3a5') + RECT(224, ty + 14, 12, gy - ty - 14, INK, '#d8c3a5')
    b += GROUND(20, 540, gy)
    # المسار بعد الحافة
    vx, g = 120, 260; t1 = math.sqrt(2 * (gy - 8 - (ty - 8)) / g)
    pts = parab(250, ty - 8, vx, 0, g, t1); b += PATH(pts)
    lx = pts[-1][0]
    b += PATH([(lx, gy - 8), (lx + 90, gy - 8)])
    p1 = (130, ty - 8); p2 = pts[8]; p3 = pts[38]; p4 = (lx + 80, gy - 8)
    for (x, y), n, dx, dy in ((p1, 1, 0, -22), (p2, 2, 6, -22), (p3, 3, 24, -4), (p4, 4, 0, -22)):
        b += BALL(x, y) + NUMLAB(x + dx, y + dy, n)
    b += ARROW(150, ty - 8, 196, ty - 8, C_VEL, 2.5, 10) + V(174, ty - 22, 'v', C_VEL, 16)
    save('c6l1-o01-table-stages.svg', svg(w, h, b))


# ================= O02 =================
def o02_top():
    w, h = 480, 300; b = GROUND(20, 460, 260)
    pts = parab(50, 252, 150, 260, 190, 2 * 260 / 190); b += PATH(pts)
    top = pts[30]; b += BALL(*top) + ARROW(top[0] + 10, top[1], top[0] + 70, top[1], C_VEL, 2.8) + V(top[0] + 80, top[1] + 6, 'v', C_VEL, 17, 'start')
    b += T(top[0], top[1] - 22, 'أعلى نقطة', 14, color=MUTED)
    b += AXES(60, 90)
    save('c6l1-o02-top.svg', svg(w, h, b))


def o02_three():
    w, h = 540, 320; b = GROUND(20, 520, 280)
    vx, vy, g = 160, 270, 190; t1 = 2 * vy / g
    pts = parab(50, 272, vx, vy, g, t1); b += PATH(pts)
    for k, lab in ((12, 'A'), (30, 'B'), (50, 'C')):
        t = t1 * k / 60; x, y = pts[k]; vyt = vy - g * t; sc = 0.28
        b += BALL(x, y) + ARROW(x, y, x + vx * sc, y - vyt * sc, C_VEL, 2.6, 10)
        b += T(x - 16, y + 24 if lab != 'B' else y - 16, lab, 16, weight='bold', italic=True)
    b += AXES(450, 80)
    save('c6l1-o02-three.svg', svg(w, h, b))


# ================= O03 =================
def fbd_panels(name, panels, w=720, h=240, extra=''):
    """لوحات مخطط الجسم الحر مرقمة. panels = [ [ (ang, len, label), ... ], ... ]."""
    n = len(panels); pw = (w - 90) / n; b = AXES(w - 70, 200, 36) + L(w - 90, 12, w - 90, h - 12, GRID, 1.5)
    for i, forces in enumerate(panels):
        cx = pw * i + pw / 2; cy = 130
        b += NUMLAB(cx, 26, i + 1)
        if i: b += L(pw * i, 12, pw * i, h - 12, GRID, 1.5)
        b += DOT(cx, cy, 7)
        for ang, ln, lab in forces:
            up = lab in ('F_d',)
            dx = 18 if ang in (90, -90, 270) else 0
            b += FA(cx, cy, ang, ln, lab, dx=dx, lab_r=(ln - 10 if ang in (90, -90, 270) else None), upright=up)
    save(name, svg(w, h, b + extra))


def o03_figs():
    G = (-90, 80, 'F_g')
    fbd_panels('c6l1-o03-flight-fbds.svg', [[G], [G, (40, 70, 'F')], [], [G, (0, 60, 'F')]])
    fbd_panels('c6l1-o03-top-fbds.svg', [[G, (90, 80, 'F')], [(0, 70, 'F')], [G], []])
    fbd_panels('c6l1-o03-ice-fbds.svg', [[G, (90, 80, 'F_N')], [G, (0, 70, 'F')], [G, (90, 45, 'F_N')], [G]])
    fbd_panels('c6l1-o03-air-fbds.svg', [[G, (40, 50, 'F_d')], [G], [G, (180, 50, 'F_d')], [G, (220, 50, 'F_d')]])
    # رسم طالب: الكرة عند أعلى نقطة
    w, h = 320, 260; cx, cy = 150, 125
    b = DOT(cx, cy, 7) + FA(cx, cy, -90, 80, 'F_g', dx=18, lab_r=70) + FA(cx, cy, 0, 80, 'F', dy=-18, lab_r=88)
    b += AXES(250, 230, 36)
    save('c6l1-o03-student-fbd.svg', svg(w, h, b))


# ================= O04 =================
def o04_paths_ground():
    w, h = 640, 210; b = ''; pw = w / 4; gy = 180
    for i in range(4):
        x0 = pw * i + 18; b += NUMLAB(pw * i + pw / 2, 22, i + 1)
        if i: b += L(pw * i, 10, pw * i, h - 10, GRID, 1.5)
        b += GROUND(pw * i + 8, pw * (i + 1) - 8, gy)
        if i == 0: pts = [(x0, gy), (x0 + 125, gy - 130)]
        elif i == 1: pts = [(x0, gy), (x0 + 62, gy - 120), (x0 + 124, gy)]
        elif i == 2: pts = parab(x0, gy, 50, 150, 120, 2.5)
        else: pts = [(x0, gy), (x0 + 50, gy - 120), (x0 + 110, gy - 120), (x0 + 110, gy)]
        b += PATH(pts, INK, 2.4, '') + BALL(x0, gy - 7, 7)
    save('c6l1-o04-paths-ground.svg', svg(w, h, b))


def o04_paths_cliff():
    w, h = 640, 220; b = ''; pw = w / 4; gy = 196; top = 60
    for i in range(4):
        x0 = pw * i + 10; b += NUMLAB(pw * i + pw / 2, 22, i + 1)
        if i: b += L(pw * i, 10, pw * i, h - 10, GRID, 1.5)
        b += RECT(x0, top, 34, gy - top, INK, '#d9d2c3', 1.5) + GROUND(pw * i + 8, pw * (i + 1) - 8, gy)
        sx, sy = x0 + 34, top - 7
        if i == 0: pts = [(sx, sy), (sx + 105, gy)]
        elif i == 1: pts = [(sx, sy), (sx + 85, sy), (sx + 85, gy)]
        elif i == 2: pts = parab(sx, sy, 105, 0, 2 * (gy - sy), 1.0)
        else: pts = parab(sx, sy, 50, 60, 2 * 60 * 60 / 50, 2.2)
        pts = [(x, min(y, gy)) for x, y in pts]
        b += PATH(pts, INK, 2.4, '') + BALL(sx - 8, sy, 7)
    save('c6l1-o04-paths-cliff.svg', svg(w, h, b))


# ================= O05 =================
def o05_strobe():
    w, h = 520, 330; b = ''; u = 40
    for gx in range(0, w // u + 1): b += L(20 + gx * u, 20, 20 + gx * u, 300, GRID, 1)
    for gy in range(0, 8): b += L(20, 20 + gy * u, 500, 20 + gy * u, GRID, 1)
    x0, y0 = 60, 40; dx = 80
    for k in range(6):
        t = k * 0.1; b += BALL(x0 + dx * k, y0 + 4.9 * t * t * 100 * 1.0, 9)
    b += T(260, 322, 'الصور ملتقطة كل \u202a0.1 s\u202c', 14, color=MUTED)
    save('c6l1-o05-strobe.svg', svg(w, h, b))


def o05_vx_graphs():
    w, h = 640, 230; b = ''; pw = w / 4
    for i in range(4):
        L0 = pw * i + 40; R0 = pw * (i + 1) - 14; T0 = 50; B0 = 180
        b += NUMLAB(pw * i + pw / 2, 24, i + 1)
        if i: b += L(pw * i, 10, pw * i, h - 10, GRID, 1.5)
        b += ARROW(L0, B0, R0, B0, INK, 1.8, 9) + ARROW(L0, B0, L0, T0 - 6, INK, 1.8, 9)
        b += T(R0 - 2, B0 + 18, 't (s)', 13, 'end', MUTED, italic=True)
        b += V(L0 - 6, T0 + 4, 'v_x', C_VEL, 14, 'end')
        if i == 0: pts = [(L0, T0 + 20), (R0 - 14, B0 - 20)]
        elif i == 1: pts = [(L0, B0 - 50), (R0 - 14, B0 - 50)]
        elif i == 2: pts = [(L0, B0 - 30), (R0 - 14, T0 + 10)]
        else: pts = [(L0, B0 - 1.5), (R0 - 14, B0 - 1.5)]
        b += PATH(pts, C_VEL, 3, '')
    b += T(w / 2, h - 8, 'المحور الرأسي: المركّبة الأفقية للسرعة المتجهة (m/s)، والمحور الأفقي: الزمن (s)', 13, color=MUTED)
    save('c6l1-o05-vx-graphs.svg', svg(w, h, b))


# ================= O06 =================
def cliff_fig(name, kind, hlab, vlab=None, xlab=None, pool=None, w=560, h=330, axes=True, xr=200):
    """جرف/بناية/طاولة يُقذف من حافتها جسم أفقيًا. pool = (x1_px, x2_px, land_px, lab1, lab2) بالبكسل من الحافة."""
    gy = h - 50; top = 70; b = ''; X0 = 110
    if kind == 'table':
        b += RECT(X0, top, 170, 14, INK, '#d8c3a5') + RECT(X0 + 14, top + 14, 12, gy - top - 14, INK, '#d8c3a5') + RECT(X0 + 156, top + 14, 12, gy - top - 14, INK, '#d8c3a5')
        ex = X0 + 170; ob = RECT(ex - 45, top - 22, 40, 16, INK, '#e07b39', 1.5) + DOT(ex - 36, top - 5, 4.5, INK, '#333') + DOT(ex - 14, top - 5, 4.5, INK, '#333')
        sx, sy = ex, top - 8
    else:
        b += RECT(X0, top, 140, gy - top, INK, '#d9d2c3' if kind == 'cliff' else '#dfe5ee', 1.8)
        if kind == 'building':
            for r in range(5):
                for c in range(3): b += RECT(X0 + 18 + c * 40, top + 18 + r * 40, 22, 22, MUTED, '#fff', 1)
        ex = X0 + 140; ob = ''; sx, sy = ex + 2, top - 9
    b += GROUND(20, w - 20, gy)
    if pool: xr = pool[2]
    pts = parab(sx, sy, xr, 0, 2 * (gy - sy - 8), 1.0, 50); b += PATH(pts)
    if kind != 'table': b += BALL(sx, sy)
    b += ob
    if vlab: b += ARROW(sx + 10, sy - 18, sx + 70, sy - 18, C_VEL, 2.8) + (V(sx + 78, sy - 12, vlab, C_VEL, 16, 'start') if vlab == 'v' else T(sx + 76, sy - 13, vlab, 15, 'start', C_VEL))
    b += DIM_V(X0 - 24, top, gy, '') + T(X0 - 32, (top + gy) / 2 + 5, hlab, 15, 'end')
    if xlab: b += DIM_H(ex, pts[-1][0], gy + 24, xlab, italic=(xlab == 'x'))
    if pool:
        x1, x2 = ex + pool[0], ex + pool[1]
        b += f'<ellipse cx="{(x1 + x2) / 2:.1f}" cy="{gy:.1f}" rx="{(x2 - x1) / 2:.1f}" ry="9" fill="#9cc9ea" stroke="{INK}" stroke-width="1.5"/>'
        b += DIM_H(ex, x1, gy + 24, pool[3]) + DIM_H(ex, x2, gy + 50, pool[4])
    if axes: b += AXES(w - 80, 120)
    save(name, svg(w, h + (30 if pool else 0), b))


def o06_figs():
    cliff_fig('c6l1-o06-cliff.svg', 'cliff', '44.1 m', '7.0 m/s')
    cliff_fig('c6l1-o06-building.svg', 'building', '45.0 m', '8.00 m/s', 'x')
    cliff_fig('c6l1-o06-table-fall.svg', 'table', '0.784 m', 'v', xr=90)
    cliff_fig('c6l1-o06-table-car.svg', 'table', '1.10 m', None, '0.500 m', xr=100)
    # المقياس 4.4 px/m: 30.0 m → 132، 50.0 m → 220، نقطة الهبوط 51.4 m → 226
    cliff_fig('c6l1-o06-pool.svg', 'building', '40.0 m', '18.0 m/s', None, pool=(132, 220, 226, '30.0 m', '50.0 m'))


# ================= O07 =================
def row_diagram(b, y, xs, lens, x_end=None):
    for x, ln in zip(xs, lens):
        b += DOT(x, y, 5)
        if ln > 0: b += ARROW(x, y, x + ln, y, C_VEL, 2.4, 9)
    return b


def o07_horiz_rows():
    w, h = 600, 300; b = ''
    rows = {
        1: ([40, 140, 225, 295, 350, 390], [80, 70, 55, 42, 30, 20]),
        2: ([40, 80, 135, 205, 290, 390], [30, 42, 55, 70, 82, 95]),
        3: ([40, 125, 210, 295, 380, 465], [70] * 6),
        4: ([40, 130, 195, 230, 265, 330, 420], [75, 50, 22, 0, 22, 50, 75]),
    }
    for k in range(1, 5):
        y = 50 + (k - 1) * 66; b += NUMLAB(w - 30, y + 5, k)
        b = row_diagram(b, y, *rows[k])
    b += T(300, h - 12, 'الصور متتالية على فترات زمنية متساوية، والحركة من اليسار إلى اليمين', 13, color=MUTED)
    save('c6l1-o07-horiz-rows.svg', svg(w, h, b))


def col_diagram(x, top, ups, downs, gap=14):
    """عمود صعود (أسهم إلى أعلى) بجانبه عمود نزول (أسهم إلى أسفل). ups/downs = [(y, len)]."""
    b = ''
    for y, ln in ups:
        b += DOT(x, y, 4.5)
        if ln > 0: b += ARROW(x, y, x, y - ln, C_VEL, 2.3, 8)
    for y, ln in downs:
        b += DOT(x + gap, y, 4.5)
        if ln > 0: b += ARROW(x + gap, y, x + gap, y + ln, C_VEL, 2.3, 8)
    return b


def o07_vert_cols():
    w, h = 600, 420; b = ''; pw = w / 4
    ys = [330, 250, 190, 150, 130]          # مواقع الصعود (المسافات تتناقص)
    good_up = [(ys[0], 75), (ys[1], 56), (ys[2], 38), (ys[3], 19), (ys[4], 0)]
    good_dn = [(ys[3], 19), (ys[2], 38), (ys[1], 56), (ys[0], 75)]
    const_up = [(330, 55), (270, 55), (210, 55), (150, 55), (90, 0)]
    const_dn = [(150, 55), (210, 55), (270, 55), (330, 55)]
    stop_up = good_up; stop_dn = [(ys[3], 19), (ys[2], 19), (ys[1], 19), (ys[0], 19)]
    inc_up = [(330, 20), (290, 38), (230, 56), (150, 75), (60, 0)]
    inc_dn = [(150, 75), (230, 56), (290, 38), (330, 20)]
    sets = [(const_up, const_dn), (stop_up, stop_dn), (inc_up, inc_dn), (good_up, good_dn)]
    for i, (u, d) in enumerate(sets):
        x = pw * i + pw / 2 - 7; b += NUMLAB(pw * i + pw / 2, 26, i + 1)
        if i: b += L(pw * i, 12, pw * i, h - 12, GRID, 1.5)
        b += col_diagram(x, 0, u, d)
    save('c6l1-o07-vert-cols.svg', svg(w, h, b))


def o07_combined():
    w, h = 540, 330; b = GROUND(20, 520, 300)
    vx, vy, g = 100, 200, 100; t1 = 2 * vy / g; x0, y0 = 50, 292
    pts = parab(x0, y0, vx, vy, g, t1, 80); b += PATH(pts, MUTED, 1.6)
    sc = 0.42
    for k in (0, 14, 28):
        t = t1 * k / 80; x, y = pts[k]; vyt = vy - g * t
        b += DOT(x, y, 4.5) + ARROW(x, y, x + vx * sc, y, C_VEL, 2.6, 9) + ARROW(x, y, x, y - vyt * sc, C_VEL, 2.6, 9)
        b += DASHARROW(x, y, x + vx * sc, y - vyt * sc)
        if k == 0:
            b += V(x + vx * sc / 2, y + 22, 'v_x', C_VEL, 16) + V(x - 16, y - vyt * sc / 2, 'v_y', C_VEL, 16)
    b += AXES(440, 110)
    save('c6l1-o07-combined.svg', svg(w, h, b))


def o07_separate():
    w, h = 560, 440; b = ''
    # الحركة الأفقية: صف أعلى
    y = 50; xs = [70 + 52 * k for k in range(9)]
    for x in xs: b += DOT(x, y, 4.5) + ARROW(x, y, x + 40, y, C_VEL, 2.3, 8)
    b += V(250, y + 26, 'v_x', C_VEL, 16) + T(250, y + 50, 'a_x = 0', 15, italic=True, color=C_ACC)
    # الحركة الرأسية: عمود يسار
    ys = [350, 250, 175, 125, 100]
    ups = [(ys[0], 70), (ys[1], 52), (ys[2], 35), (ys[3], 18), (ys[4], 0)]
    dns = [(ys[3], 18), (ys[2], 35), (ys[1], 52), (ys[0], 70)]
    b += col_diagram(60, 0, ups, dns, 14)
    b += V(40, 240, 'v_y', C_VEL, 16, 'end')
    b += ARROW(130, 200, 130, 250, C_ACC, 2.8) + V(142, 232, 'a_y', C_ACC, 16, 'start')
    b += AXES(380, 300)
    save('c6l1-o07-separate.svg', svg(w, h, b))


# ================= O08 =================
def o08_paths4():
    w, h = 640, 230; b = ''; pw = w / 4; gy = 200
    for i in range(4):
        x0 = pw * i + 20; b += NUMLAB(pw * i + pw / 2, 22, i + 1)
        if i: b += L(pw * i, 10, pw * i, h - 10, GRID, 1.5)
        b += GROUND(pw * i + 8, pw * (i + 1) - 8, gy)
        if i == 0:   # يُدحرج عن طاولة
            b += RECT(x0, 100, 60, 10, INK, '#d8c3a5') + RECT(x0 + 50, 110, 8, gy - 110, INK, '#d8c3a5')
            pts = parab(x0 + 60, 92, 70, 0, 2 * (gy - 100), 1.0); b += PATH(pts, INK, 2.2, '') + BALL(x0 + 44, 92, 7)
            b += ARROW(x0 + 30, 78, x0 + 64, 78, C_VEL, 2.4, 9)
        elif i == 1:   # يسقط من السكون
            b += RECT(x0, 60, 60, 10, INK, '#d8c3a5')
            b += PATH([(x0 + 80, 64), (x0 + 80, gy)], INK, 2.2, '') + BALL(x0 + 80, 58, 7)
        elif i == 2:   # يُقذف من الأرض بزاوية
            pts = parab(x0, gy - 7, 60, 140, 140, 2.0); b += PATH(pts, INK, 2.2, '') + BALL(x0, gy - 7, 7)
            b += ARROW(x0 + 2, gy - 12, x0 + 30, gy - 68, C_VEL, 2.4, 9)
        else:   # يُقذف رأسيًا إلى أعلى
            b += PATH([(x0 + 60, gy - 7), (x0 + 60, 50)], INK, 2.2, '') + PATH([(x0 + 72, 50), (x0 + 72, gy - 7)], INK, 2.2, '4 4')
            b += BALL(x0 + 60, gy - 7, 7) + ARROW(x0 + 40, gy - 20, x0 + 40, gy - 76, C_VEL, 2.4, 9)
    save('c6l1-o08-paths4.svg', svg(w, h, b))


# ================= O09 =================
def o09_launch():
    w, h = 380, 280; ox, oy = 70, 230; b = GROUND(20, 360, oy + 8)
    b += L(ox, oy, ox + 250, oy, GRID, 1.5, '5 5') + L(ox, oy, ox, oy - 200, GRID, 1.5, '5 5')
    b += FA(ox, oy, 40, 200, '', C_VEL) + T(ox + 112, oy - 120, '15.0 m/s', 15, 'end', C_VEL)
    b += V(ox + 172, oy - 132, 'v_i', C_VEL, 17, 'start')
    b += ARC(ox, oy, 52, 0, 40) + T(ox + 82, oy - 14, '40.0°', 14)
    b += BALL(ox, oy, 7) + AXES(290, 120)
    save('c6l1-o09-launch.svg', svg(w, h, b))


def o09_points():
    w, h = 520, 310; b = GROUND(20, 500, 270)
    vx, vy, g = 160, 260, 180; t1 = 2 * vy / g
    pts = parab(50, 262, vx, vy, g, t1); b += PATH(pts)
    for k, lab, dy in ((12, 'A', 26), (48, 'C', -16)):
        x, y = pts[k]; b += BALL(x, y) + T(x + (-18 if lab == 'A' else 20), y + (6 if lab == 'A' else -8), lab, 17, weight='bold', italic=True)
    # سهم اتجاه الحركة على المسار
    x1, y1 = pts[22]; x2, y2 = pts[25]; b += ARROW(x1, y1 - 18, x2 + 4, y2 - 20, MUTED, 1.6, 8)
    b += T((x1 + x2) / 2, y1 - 34, 'اتجاه الحركة', 13, color=MUTED)
    b += AXES(430, 110)
    save('c6l1-o09-points.svg', svg(w, h, b))


def o09_acc4():
    w, h = 640, 220; b = ''; pw = w / 4; gy = 190
    for i in range(4):
        x0 = pw * i + 20; b += NUMLAB(pw * i + pw / 2, 22, i + 1)
        if i: b += L(pw * i, 10, pw * i, h - 10, GRID, 1.5)
        vx, vy, g = 48, 125, 100; t1 = 2 * vy / g; pts = parab(x0, gy, vx, vy, g, t1, 60); b += PATH(pts, MUTED, 1.6)
        for k in (10, 30, 50):
            t = t1 * k / 60; x, y = pts[k]; b += DOT(x, y, 4)
            vyt = vy - g * t
            if i == 0: ang = -90; ln = 40
            elif i == 1:   # مماسي
                ang = math.degrees(math.atan2(vyt, vx)); ln = 40
            elif i == 2:   # إلى أسفل وإلى الأمام (له مركّبة أفقية)
                ang = -55; ln = 40
            else:          # إلى أعلى في الصعود وإلى أسفل في النزول
                ang = 90 if k < 30 else -90; ln = 0 if k == 30 else 36
            if ln: b += FA(x, y, ang, ln, '', C_ACC)
    save('c6l1-o09-acc4.svg', svg(w, h, b))


def o09_student():
    w, h = 560, 330; b = GROUND(20, 540, 300)
    vx, vy, g = 170, 260, 170; t1 = 2 * vy / g
    pts = parab(50, 292, vx, vy, g, t1); b += PATH(pts, MUTED, 1.6)
    sc = 0.3
    for k, lab, vxs in ((10, 'A', 1.0), (30, 'B', 0.6), (50, 'C', 0.3)):
        t = t1 * k / 60; x, y = pts[k]; vyt = vy - g * t
        b += DOT(x, y, 4.5) + ARROW(x, y, x + vx * sc * vxs, y, C_VEL, 2.6, 9)
        if abs(vyt) > 1: b += ARROW(x, y, x, y - vyt * sc, C_VEL, 2.6, 9)
        b += FA(x, y, -60, 46, '', C_ACC)
        b += T(x - 16, y - 8, lab, 16, weight='bold', italic=True)
    x, y = pts[10]
    b += V(x + vx * sc / 2, y - 10, 'v_x', C_VEL, 15) + V(x - 14, y - 40, 'v_y', C_VEL, 15, 'end') + V(x + 32, y + 40, 'a', C_ACC, 15, 'start')
    b += AXES(450, 110)
    save('c6l1-o09-student.svg', svg(w, h, b))


if __name__ == '__main__':
    o01_table_stages(); o02_top(); o02_three(); o03_figs(); o04_paths_ground(); o04_paths_cliff()
    o05_strobe(); o05_vx_graphs(); o06_figs(); o07_horiz_rows(); o07_vert_cols(); o07_combined(); o07_separate()
    o08_paths4(); o09_launch(); o09_points(); o09_acc4(); o09_student()
