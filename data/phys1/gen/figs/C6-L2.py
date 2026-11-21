import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 6-2 (الحركة الدائرية) — الأهداف O01–O14
# اصطلاح الألوان: السرعة أحمر (مماسية)، التسارع بنفسجي (نحو المركز)، القوى زرقاء تبدأ من الجسم، متجه الموقع r أخضر.
import math


def pol(cx, cy, ang, r):
    a = math.radians(ang); return cx + r * math.cos(a), cy - r * math.sin(a)


def NUM(x, y, n, color=INK):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="#fff" stroke="{color}" stroke-width="1.6"/>' + T(x, y + 5, str(n), 14, color=color, weight='bold')


def CIRC(cx, cy, R, color=INK, w=2, dash='', fill='none'):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>'


def ARC(cx, cy, r, a1, a2, color=INK, w=1.5, arrow=False):
    """قوس من الزاوية a1 إلى a2 (درجات). إن كان a2 > a1 فالقوس عكس عقارب الساعة، وإلا فمع عقارب الساعة. arrow يضع رأس سهم عند a2."""
    x1, y1 = pol(cx, cy, a1, r); x2, y2 = pol(cx, cy, a2, r)
    ccw = a2 > a1; large = 1 if abs(a2 - a1) > 180 else 0; sweep = 0 if ccw else 1
    b = f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} {sweep} {x2:.1f} {y2:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    if arrow:
        d = a2 + (90 if ccw else -90); hx, hy = pol(x2, y2, d, 1)
        th = math.radians(d); head = 10
        p1 = (x2 - head * math.cos(-th - 0.4), y2 - head * math.sin(-th - 0.4)); p2 = (x2 - head * math.cos(-th + 0.4), y2 - head * math.sin(-th + 0.4))
        tip = pol(x2, y2, d, 4)
        b += f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'
    return b


def MOTION(cx, cy, R, a1, a2):
    """سهم منحنٍ رمادي خارج الدائرة يبيّن اتجاه الدوران."""
    return ARC(cx, cy, R + 16, a1, a2, MUTED, 1.8, True)


def AR(x, y, ang, length, color, w=3, head=11):
    x2, y2 = pol(x, y, ang, length); return ARROW(x, y, x2, y2, color, w, head)


def LAB(x, y, ang, dist, s, color, vec=True, size=17, dx=0, dy=0):
    lx, ly = pol(x, y, ang, dist); lx += dx; ly += dy + 6
    return V(lx, ly, s, color, size) if vec else T(lx, ly, s, size - 2, 'middle', color, italic=True)


def AC(x, y, color=C_ACC, size=17):
    """الرمز a_c كما في الكتاب: a مائل عريض والحرف السفلي c قائم."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-size="{size}" fill="{color}" font-weight="bold" font-style="italic" {MATHFONT}>a'
            f'<tspan dy="0.3em" font-size="{int(size * 0.72)}" font-weight="normal" font-style="normal">c</tspan><tspan dy="-0.3em"></tspan></text>')


def CENTER(cx, cy):
    return DOT(cx, cy, 3.5, INK)


def COMPASS(x, y, s=34):
    b = ARROW(x, y + s, x, y - s, MUTED, 1.6, 9) + L(x - s, y, x + s, y, MUTED, 1.6)
    b += T(x, y - s - 8, 'شمال', 13, color=MUTED) + T(x, y + s + 18, 'جنوب', 13, color=MUTED)
    b += T(x + s + 6, y + 5, 'شرق', 13, 'start', MUTED) + T(x - s - 6, y + 5, 'غرب', 13, 'end', MUTED)
    return b


def DASHL(x1, y1, x2, y2, color=INK, w=2.2):
    a = math.atan2(y2 - y1, x2 - x1); head = 10
    p1 = (x2 - head * math.cos(a - 0.4), y2 - head * math.sin(a - 0.4)); p2 = (x2 - head * math.cos(a + 0.4), y2 - head * math.sin(a + 0.4))
    return L(x1, y1, x2 - 0.6 * head * math.cos(a), y2 - 0.6 * head * math.sin(a), color, w, '7 5') + f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'


# ================= O01 =================
def o01_paths():
    w, h = 680, 230; b = ''; R = 58
    centers = [(90, 105), (260, 105), (430, 105), (600, 105)]
    # 1: دائرة ونقاط متساوية التباعد
    cx, cy = centers[0]; b += CIRC(cx, cy, R, GRID, 1.5, '4 4')
    b += ''.join(DOT(*pol(cx, cy, 90 + 36 * k, R), 5) for k in range(10))
    # 2: دائرة ونقاط يتزايد تباعدها
    cx, cy = centers[1]; b += CIRC(cx, cy, R, GRID, 1.5, '4 4'); ang = 90
    for k in range(8):
        b += DOT(*pol(cx, cy, ang, R), 5); ang += 12 + 9 * k
    # 3: حلزون يزداد نصف قطره، والنقاط متساوية التباعد تقريبًا
    cx, cy = centers[2]; ang = 90
    pts = []
    for k in range(11):
        r = 20 + 4.2 * k; pts.append(pol(cx, cy, ang, r)); ang += 34 * 30 / r
    b += ''.join(DOT(x, y, 5) for x, y in pts)
    # 4: خط مستقيم
    cx, cy = centers[3]; b += ''.join(DOT(cx - 60 + 20 * k, cy, 5) for k in range(7))
    for i, (cx, cy) in enumerate(centers): b += NUM(cx, 205, i + 1)
    save('c6l2-o01-paths.svg', svg(w, h, b))


# ================= O02 =================
def o02_dv():
    w, h = 420, 340; cx, cy, R = 200, 190, 120; b = CIRC(cx, cy, R) + CENTER(cx, cy) + T(cx, cy + 22, 'المركز', 13, color=MUTED)
    b += MOTION(cx, cy, R, 150, 120)
    for ang, lab in ((110, 'v_1'), (70, 'v_2')):
        x, y = pol(cx, cy, ang, R); b += DOT(x, y, 6) + AR(x, y, ang - 90, 80, C_VEL) + LAB(x, y, ang - 90, 98, lab, C_VEL)
    save('c6l2-o02-dv.svg', svg(w, h, b))


def o02_panels():
    w, h = 680, 230; b = ''; R = 55; cyc = 100
    kinds = ['in', 'out', 'tan', 'down']
    for i, k in enumerate(kinds):
        cx = 90 + 167 * i; b += CIRC(cx, cyc, R) + CENTER(cx, cyc) + MOTION(cx, cyc, R, 20, 70)
        for ang in (90, 210, 330):
            x, y = pol(cx, cyc, ang, R); b += DOT(x, y, 5)
            d = {'in': ang + 180, 'out': ang, 'tan': ang + 90, 'down': -90}[k]
            b += AR(x, y, d, 34, C_ACC, 2.6, 9)
        b += NUM(cx, 210, i + 1)
    save('c6l2-o02-panels.svg', svg(w, h, b))


def o02_compass():
    w, h = 460, 330; cx, cy, R = 190, 175, 110; b = CIRC(cx, cy, R) + CENTER(cx, cy)
    b += MOTION(cx, cy, R, 30, 70)
    x, y = pol(cx, cy, 90, R); b += DOT(x, y, 7)
    b += COMPASS(390, 80)
    save('c6l2-o02-compass.svg', svg(w, h, b))


def o02_esub():
    w, h = 420, 340; cx, cy, R = 200, 210, 120; b = CIRC(cx, cy, R) + CENTER(cx, cy)
    b += MOTION(cx, cy, R, 20, 45)
    for ang, lab in ((60, 'v_1'), (90, 'v_2')):
        x, y = pol(cx, cy, ang, R); b += DOT(x, y, 6) + AR(x, y, ang + 90, 85, C_VEL) + LAB(x, y, ang + 90, 104, lab, C_VEL)
    for ang, lab in ((60, 'P_1'), (90, 'P_2')):
        x, y = pol(cx, cy, ang, R - 22); b += T(x, y + 5, lab, 14, italic=True)
    save('c6l2-o02-e-sub.svg', svg(w, h, b))


# ================= O03 =================
def tri_pair(name, with_circle):
    w, h = (640, 320) if with_circle else (560, 260); b = ''
    dth = 40
    if with_circle:
        cx, cy, R = 150, 170, 120; b += CIRC(cx, cy, R, INK, 1.6) + CENTER(cx, cy)
        a1, a2 = 70, 30
        p1, p2 = pol(cx, cy, a1, R), pol(cx, cy, a2, R)
        b += ARROW(cx, cy, *p1, C_DISP, 2.6) + ARROW(cx, cy, *p2, C_DISP, 2.6) + ARROW(*p1, *p2, C_DISP, 2.6)
        b += LAB(cx, cy, a1 + 8, R * 0.55, 'r_1', C_DISP) + LAB(cx, cy, a2 - 10, R * 0.55, 'r_2', C_DISP)
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2; b += V(mx + 26, my - 6, 'Δr', C_DISP)
        b += ARC(cx, cy, 34, a2, a1) + T(*pol(cx, cy, 50, 50), 'Δθ', 14, italic=True)
        for (px, py), ang, lab in ((p1, a1, 'v_1'), (p2, a2, 'v_2')):
            b += AR(px, py, ang - 90, 62, C_VEL, 2.6) + LAB(px, py, ang - 90, 80, lab, C_VEL)
        b += MOTION(cx, cy, R, 120, 95)
        ox = 330
    else:
        ox = 40
        # مثلث الموقع
        cx, cy = ox + 20, 200; L1 = 170
        p1, p2 = pol(cx, cy, 20 + dth, L1), pol(cx, cy, 20, L1)
        b += ARROW(cx, cy, *p1, C_DISP, 2.6) + ARROW(cx, cy, *p2, C_DISP, 2.6) + ARROW(*p1, *p2, C_DISP, 2.6)
        b += LAB(cx, cy, 20 + dth + 6, L1 * 0.5, 'r_1', C_DISP, dx=-8) + LAB(cx, cy, 20 - 8, L1 * 0.5, 'r_2', C_DISP, dy=6)
        b += V((p1[0] + p2[0]) / 2 + 24, (p1[1] + p2[1]) / 2 - 2, 'Δr', C_DISP)
        b += ARC(cx, cy, 36, 20, 20 + dth) + T(*pol(cx, cy, 20 + dth / 2, 52), 'Δθ', 14, italic=True)
        ox = 300
    # مثلث السرعة
    cx, cy = ox + 30, (h - 60) if with_circle else 200; L2 = 150
    q1, q2 = pol(cx, cy, 20 + dth, L2), pol(cx, cy, 20, L2)
    if with_circle:  # رسم v_1 وv_2 من نقطة واحدة باتجاهيهما في الدائرة (70−90 = −20، 30−90 = −60)
        q1, q2 = pol(cx, cy + -150, -20, L2), pol(cx, cy - 150, -60, L2); cy = cy - 150
        b += ARROW(cx, cy, *q1, C_VEL, 2.6) + ARROW(cx, cy, *q2, C_VEL, 2.6) + ARROW(*q1, *q2, C_VEL, 2.6)
        b += LAB(cx, cy, -14, L2 * 0.55, 'v_1', C_VEL, dy=-14) + LAB(cx, cy, -66, L2 * 0.5, 'v_2', C_VEL, dx=-16)
        b += V((q1[0] + q2[0]) / 2 + 26, (q1[1] + q2[1]) / 2 + 4, 'Δv', C_VEL)
        b += ARC(cx, cy, 40, -60, -20) + T(*pol(cx, cy, -40, 58), 'Δθ', 14, italic=True)
    else:
        b += ARROW(cx, cy, *q1, C_VEL, 2.6) + ARROW(cx, cy, *q2, C_VEL, 2.6) + ARROW(*q1, *q2, C_VEL, 2.6)
        b += LAB(cx, cy, 20 + dth + 6, L2 * 0.5, 'v_1', C_VEL, dx=-8) + LAB(cx, cy, 20 - 8, L2 * 0.5, 'v_2', C_VEL, dy=6)
        b += V((q1[0] + q2[0]) / 2 + 24, (q1[1] + q2[1]) / 2 - 2, 'Δv', C_VEL)
        b += ARC(cx, cy, 36, 20, 20 + dth) + T(*pol(cx, cy, 20 + dth / 2, 52), 'Δθ', 14, italic=True)
    save(name, svg(w, h, b))


# ================= O04 =================
def o04_ab():
    w, h = 400, 340; cx, cy, R = 180, 185, 115; b = CIRC(cx, cy, R, INK, 2) + CENTER(cx, cy)
    b += MOTION(cx, cy, R, 30, 60)
    for ang, lab, pl in ((0, 'v_A', 'A'), (90, 'v_B', 'B')):
        x, y = pol(cx, cy, ang, R); b += DOT(x, y, 7) + AR(x, y, ang + 90, 80, C_VEL) + LAB(x, y, ang + 90, 96, lab, C_VEL, dx=(22 if ang == 0 else 0), dy=(0 if ang == 0 else -18))
        tx, ty = pol(cx, cy, ang, R - 24); b += T(tx, ty + 5, pl, 16, weight='bold')
    save('c6l2-o04-ab.svg', svg(w, h, b))


def o04_equarter():
    w, h = 440, 360; cx, cy, R = 200, 210, 120; b = CIRC(cx, cy, R) + CENTER(cx, cy) + COMPASS(375, 70, 28)
    b += MOTION(cx, cy, R, 30, 60)
    for ang, lab, pl in ((0, 'v_1', 'P_1'), (90, 'v_2', 'P_2')):
        x, y = pol(cx, cy, ang, R); b += DOT(x, y, 6) + AR(x, y, ang + 90, 80, C_VEL)
        b += LAB(x, y, ang + 90, 98, lab, C_VEL, dx=(24 if ang == 0 else 0), dy=(0 if ang == 0 else -16))
        tx, ty = pol(cx, cy, ang, R - 24); b += T(tx, ty + 5, pl, 14, italic=True)
    b += T(cx + R + 52, cy - 40, '5.0 m/s', 13, color=C_VEL) + T(cx - 50, cy - R - 30, '5.0 m/s', 13, color=C_VEL)
    save('c6l2-o04-e-quarter.svg', svg(w, h, b))


# ================= O05 =================
def o05_graphs():
    w, h = 700, 230; b = ''
    for i in range(4):
        x0, y0 = 30 + 172 * i, 170; W, H = 130, 130
        b += ARROW(x0, y0, x0 + W + 10, y0, INK, 1.8, 9) + ARROW(x0, y0, x0, y0 - H - 10, INK, 1.8, 9)
        b += T(x0 + W + 12, y0 + 18, 'v', 15, italic=True) + AC(x0 + 18, y0 - H - 4, INK, 15)
        if i == 0: pts = [(t, t) for t in (0, 1)]
        elif i == 1: pts = [(t / 20, (t / 20) ** 2) for t in range(21)]
        elif i == 2: pts = [(t / 20, 0.12 / (t / 20)) for t in range(3, 21)]
        else: pts = [(t, 0.55) for t in (0, 1)]
        s = ' '.join(f'{x0 + 8 + x * (W - 14):.1f},{y0 - y * (H - 14) - (0 if i != 2 else 0):.1f}' for x, y in pts)
        b += f'<polyline points="{s}" fill="none" stroke="{C_ACC}" stroke-width="3"/>'
        b += NUM(x0 + W / 2, 210, i + 1)
    save('c6l2-o05-graphs.svg', svg(w, h, b))


def o05_ar():
    pts = [(r / 100, 16 / (r / 100)) for r in range(46, 221, 2)]
    graph('c6l2-o05-ar.svg', [{'pts': pts, 'color': C_ACC, 'dots': False}], (0, 2.5), (0, 40), 'نصف القطر r (m)', 'التسارع المركزي (m/s²)', 0.5, 5,
          w=540, h=380, marks=[(0.5, 32, ''), (1.0, 16, ''), (2.0, 8, '')])


def o05_tracks():
    w, h = 620, 300; b = ''
    for cx, R, lab, pl in ((150, 60, '50 m', 'A'), (430, 120, '100 m', 'B')):
        cy = 160; b += CIRC(cx, cy, R) + CENTER(cx, cy)
        x, y = pol(cx, cy, 0, R); b += L(cx, cy, x, y, C_DISP, 2) + T(cx + R / 2, cy - 8, lab, 14, color=C_DISP)
        b += DOT(*pol(cx, cy, 90, R), 7) + T(pol(cx, cy, 90, R)[0], pol(cx, cy, 90, R)[1] - 14, pl, 16, weight='bold')
    save('c6l2-o05-tracks.svg', svg(w, h, b))


# ================= O06 =================
def o06_inv():
    k = 4 * math.pi ** 2 * 1.00
    xs = [0.25, 0.50, 0.75, 1.00]
    graph('c6l2-o06-inv.svg', [{'pts': [(0, 0), (1.1, k * 1.1)], 'color': C_ACC, 'w': 2.5}], (0, 1.2), (0, 45),
          '1/T² (s⁻²)', 'التسارع المركزي (m/s²)', 0.2, 5, w=540, h=380, marks=[(x, k * x, '') for x in xs])


def o06_station():
    w, h = 420, 380; cx, cy = 210, 190; b = CIRC(cx, cy, 160, INK, 14, fill='none').replace('stroke="#1f2a44"', 'stroke="#c9ced6"')
    b += CIRC(cx, cy, 80, '#c9ced6', 12) + CENTER(cx, cy)
    b += L(cx, cy, cx, cy - 80, C_DISP, 2) + T(cx + 26, cy - 40, '75 m', 14, color=C_DISP)
    x, y = pol(cx, cy, -30, 160); b += L(cx, cy, x, y, C_DISP, 2) + T(cx + 105, cy + 40, '150 m', 14, color=C_DISP)
    b += MOTION(cx, cy, 160, 110, 150)
    save('c6l2-o06-station.svg', svg(w, h, b))


# ================= O07 =================
def o07_net():
    w, h = 680, 230; b = ''; R = 55; cyc = 105
    dirs = [180, 90, 0, 135]
    for i, d in enumerate(dirs):
        cx = 75 + 170 * i; b += CIRC(cx, cyc, R) + CENTER(cx, cyc) + MOTION(cx, cyc, R, 200, 250)
        x, y = pol(cx, cyc, 0, R); b += DOT(x, y, 6) + AR(x, y, d, 44, C_FORCE, 3, 10)
        b += NUM(cx, 205, i + 1)
    save('c6l2-o07-net.svg', svg(w, h, b))


def car_rear(name, labels=True, centre_note=True):
    w, h = 460, 340; cx, cy = 230, 170; b = ''
    b += L(40, 290, 420, 290, INK, 3)
    b += f'<rect x="{cx - 70}" y="{cy - 50}" width="140" height="90" rx="14" fill="#eef2f8" stroke="{INK}" stroke-width="2"/>'
    b += RECT(cx - 62, 260, 26, 30, INK, '#555', 1) + RECT(cx + 36, 260, 26, 30, INK, '#555', 1)
    b += L(cx - 49, 235, cx - 49, 260, INK, 2) + L(cx + 49, 235, cx + 49, 260, INK, 2)
    b += DOT(cx, cy, 6)
    b += AR(cx, cy, 90, 110, C_FORCE) + AR(cx, cy, -90, 110, C_FORCE) + AR(cx, cy, 180, 120, C_FORCE)
    if labels:
        b += V(cx + 26, cy - 100, 'F_N', C_FORCE) + V(cx + 26, cy + 112, 'F_g', C_FORCE) + V(cx - 120, cy - 12, 'f_f', C_FORCE)
    if centre_note:
        b += ARROW(150, 320, 50, 320, MUTED, 1.6, 9) + T(160, 325, 'نحو مركز المنعطف', 13, 'start', MUTED)
    save(name, svg(w, h, b))


# ================= O08 =================
def o08_paths():
    w, h = 460, 380; cx, cy, R = 170, 210, 110; b = CIRC(cx, cy, R) + CENTER(cx, cy)
    b += MOTION(cx, cy, R, 200, 250)
    x, y = pol(cx, cy, 0, R); b += L(cx, cy, x, y, MUTED, 1.5, '4 4') + DOT(x, y, 7)
    # 1: نصف قطري للخارج، 2: منحنٍ يبتعد، 3: مماسي، 4: مائل 45°
    b += DASHL(x, y, x + 150, y) + NUM(x + 168, y, 1)
    path = f'M {x:.1f} {y:.1f} Q {x + 10:.1f} {y - 120:.1f} {x - 90:.1f} {y - 175:.1f}'
    b += f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-dasharray="7 5"/>' + NUM(x - 108, y - 180, 2)
    b += DASHL(x, y, x, y - 175) + NUM(x + 2, y - 192, 3)
    b += DASHL(x, y, x + 120, y - 120) + NUM(x + 132, y - 134, 4)
    save('c6l2-o08-paths.svg', svg(w, h, b))


def o08_compass():
    w, h = 460, 330; cx, cy, R = 180, 160, 110; b = CIRC(cx, cy, R) + CENTER(cx, cy) + MOTION(cx, cy, R, 120, 160)
    x, y = pol(cx, cy, 270, R); b += DOT(x, y, 7) + T(x, y + 26, 'P', 15, italic=True)
    b += COMPASS(390, 80)
    save('c6l2-o08-compass.svg', svg(w, h, b))


def o08_target():
    w, h = 460, 470; cx, cy, R = 200, 330, 100; b = CIRC(cx, cy, R) + CENTER(cx, cy) + MOTION(cx, cy, R, 120, 160)
    for ang, lab, dx, dy in ((0, 'A', 18, 5), (90, 'B', 0, -14), (180, 'C', -18, 5), (270, 'D', 0, 24)):
        x, y = pol(cx, cy, ang, R); b += DOT(x, y, 6) + T(x + dx, y + dy, lab, 16, weight='bold')
    tx, ty = cx + R, 50
    b += CIRC(tx, ty, 22, RED, 3, fill='#fff') + CIRC(tx, ty, 12, RED, 3) + DOT(tx, ty, 3, RED) + T(tx + 34, ty + 5, 'الهدف', 14, 'start')
    b += COMPASS(390, 330, 28)
    save('c6l2-o08-target.svg', svg(w, h, b))


def o08_erelease():
    w, h = 420, 360; cx, cy, R = 210, 200, 115; b = CIRC(cx, cy, R) + CENTER(cx, cy) + MOTION(cx, cy, R, 60, 20)
    x, y = pol(cx, cy, 135, R); b += L(cx, cy, x, y, INK, 1.5) + DOT(x, y, 7) + T(x - 16, y - 10, 'P', 15, italic=True)
    save('c6l2-o08-e-release.svg', svg(w, h, b))


# ================= O09 =================
def o09_hammer():
    w, h = 400, 340; cx, cy, R = 200, 175, 120; b = CIRC(cx, cy, R, INK, 1.6, '6 5', '#eef6ee') + DOT(cx, cy, 8, INK, '#fff')
    x, y = pol(cx, cy, 45, R); b += L(cx, cy, x, y, INK, 2) + DOT(x, y, 9, INK, '#888')
    b += T(cx + 30, cy - 50, '1.5 m', 14) + MOTION(cx, cy, R, 120, 160)
    save('c6l2-o09-hammer.svg', svg(w, h, b))


def o09_force():
    w, h = 400, 330; cx, cy, R = 180, 170, 120; b = CIRC(cx, cy, R) + CENTER(cx, cy) + MOTION(cx, cy, R, 30, 60)
    x, y = pol(cx, cy, 0, R); b += L(cx, cy, x, y, C_DISP, 1.8, '5 4') + T(cx + 55, cy + 22, '1.2 m', 14, color=C_DISP)
    b += DOT(x, y, 8) + AR(x, y, 180, 70, C_FORCE) + T(x - 40, y - 14, '6.0 N', 14, color=C_FORCE) + T(x + 30, y + 5, '0.50 kg', 13, 'start')
    save('c6l2-o09-force.svg', svg(w, h, b))


def o09_stopper():
    w, h = 420, 330; cx, cy, R = 180, 170, 120; b = CIRC(cx, cy, R) + DOT(cx, cy, 5)
    x, y = pol(cx, cy, 0, R); b += L(cx, cy, x, y, C_DISP, 2.2) + T(cx + 60, cy - 10, 'r = 0.75 m', 14, color=C_DISP)
    b += RECT(x - 7, y - 9, 14, 18, INK, '#777', 1.5) + T(x + 16, y + 5, 'm = 20 g', 14, 'start')
    b += MOTION(cx, cy, R, 30, 65) + T(cx, cy + R + 36, 'T = 1.5 s', 14)
    save('c6l2-o09-stopper.svg', svg(w, h, b))


# ================= O10 =================
def o10_rotor():
    w, h = 440, 380; b = ''
    cx = 220; top, bot = 60, 320; Rw = 150
    b += L(cx - Rw, top, cx - Rw, bot, INK, 4) + L(cx + Rw, top, cx + Rw, bot, INK, 4) + L(cx, top - 20, cx, bot + 20, MUTED, 1.5, '8 6')
    b += T(cx + 8, top - 26, 'محور الدوران', 13, 'start', MUTED)
    px, py = cx - Rw + 14, 190; b += DOT(px, py, 7)
    b += AR(px, py, 0, 110, C_FORCE) + V(px + 130, py + 6, 'F_N', C_FORCE)
    b += AR(px, py, 90, 85, C_FORCE) + V(px + 22, py - 80, 'f_f', C_FORCE)
    b += AR(px, py, -90, 85, C_FORCE) + V(px + 24, py + 92, 'F_g', C_FORCE)
    save('c6l2-o10-rotor.svg', svg(w, h, b))


# ================= O11 =================
def car_top(name, paths=True):
    w, h = 480, 400; b = ''
    # طريق ينعطف إلى اليسار (يُرى من أعلى): مستقيم إلى أعلى ثم ينعطف يسارًا حول مركز (cx, cy)
    cx, cy, Rr = 120, 170, 160
    b += f'<path d="M {cx + Rr - 30} 400 L {cx + Rr - 30} {cy} A {Rr - 30} {Rr - 30} 0 0 0 {cx} {cy - Rr + 30}" fill="none" stroke="#c9ced6" stroke-width="2"/>'
    b += f'<path d="M {cx + Rr + 30} 400 L {cx + Rr + 30} {cy} A {Rr + 30} {Rr + 30} 0 0 0 {cx} {cy - Rr - 30}" fill="none" stroke="#c9ced6" stroke-width="2"/>'
    b += f'<path d="M {cx + Rr} 400 L {cx + Rr} {cy} A {Rr} {Rr} 0 0 0 {cx} {cy - Rr}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="10 8"/>'
    x, y = cx + Rr, cy + 20
    b += f'<rect x="{x - 18}" y="{y - 30}" width="36" height="60" rx="8" fill="#f7d774" stroke="{INK}" stroke-width="2"/>'
    b += DOT(x + 8, y - 4, 5)
    if paths:
        b += DASHL(x + 8, y - 4, x + 8, y - 175) + NUM(x + 8, y - 192, 1)
        b += DASHL(x + 8, y - 4, x + 130, y - 4) + NUM(x + 148, y - 4, 2)
        b += NUM(cx + 40, cy - Rr - 4, 3)
        b += DASHL(x + 8, y - 4, x - 90, y - 4) + NUM(x - 108, y - 4, 4)
    b += CENTER(cx, cy) + T(cx, cy + 22, 'مركز المنعطف', 13, color=MUTED)
    save(name, svg(w, h, b))


# ================= O12 =================
def o12_disc():
    w, h = 400, 340; cx, cy, R = 190, 170, 140; b = CIRC(cx, cy, R, INK, 2, '', '#f4f6fa') + DOT(cx, cy, 4) + T(cx - 14, cy + 6, 'O', 15, italic=True)
    xa, ya = pol(cx, cy, 30, 60); xb, yb = pol(cx, cy, 30, 120)
    b += L(cx, cy, xb, yb, MUTED, 1.5) + DOT(xa, ya, 6) + DOT(xb, yb, 6)
    b += T(xa - 6, ya - 12, 'A', 15, weight='bold') + T(xb - 4, yb - 12, 'B', 15, weight='bold')
    b += T(cx + 40, cy + 30, 'OA = 0.10 m', 13) + T(cx + 40, cy + 52, 'OB = 0.20 m', 13)
    b += MOTION(cx, cy, R, 120, 160)
    save('c6l2-o12-disc.svg', svg(w, h, b))


def o12_track():
    w, h = 400, 330; cx, cy, R = 200, 170, 125; b = CIRC(cx, cy, R, '#c9ced6', 16) + CIRC(cx, cy, R, INK, 1.5, '8 6') + CENTER(cx, cy)
    x, y = pol(cx, cy, -35, R); b += L(cx, cy, x, y, C_DISP, 2) + T(cx + 62, cy + 18, '40.0 m', 14, color=C_DISP)
    b += DOT(*pol(cx, cy, 90, R), 7) + MOTION(cx, cy, R + 6, 120, 160)
    save('c6l2-o12-track.svg', svg(w, h, b))


def o12_ewheel():
    w, h = 400, 380; cx, cy, R = 200, 170, 130; b = CIRC(cx, cy, R, INK, 2.5) + DOT(cx, cy, 6)
    for k in range(8):
        x, y = pol(cx, cy, 90 + 45 * k, R); b += L(cx, cy, x, y, '#c9ced6', 1.5) + RECT(x - 9, y - 4, 18, 16, INK, '#f7d774', 1.5)
    b += L(cx, cy, cx - 70, 360, INK, 3) + L(cx, cy, cx + 70, 360, INK, 3) + L(20, 360, 380, 360, INK, 2)
    x, y = pol(cx, cy, 22.5, R); b += L(cx, cy, x, y, C_DISP, 2) + T(cx + 70, cy - 8, '25.0 m', 14, color=C_DISP)
    b += MOTION(cx, cy, R + 8, 150, 190)
    save('c6l2-o12-e-wheel.svg', svg(w, h, b))


# ================= O13 =================
def numbered_arrows(name, ang, ccw, order):
    """order: قائمة الاتجاهات بالترتيب 1..4 من بين 'fwd' (مماسي مع الحركة)، 'in'، 'out'، 'back'."""
    w, h = 440, 380; cx, cy, R = 200, 200, 105; b = CIRC(cx, cy, R) + CENTER(cx, cy)
    b += MOTION(cx, cy, R, ang + (150 if ccw else -150), ang + (190 if ccw else -190))
    x, y = pol(cx, cy, ang, R); b += DOT(x, y, 7)
    tf = ang + (90 if ccw else -90)
    dmap = {'fwd': tf, 'back': tf + 180, 'in': ang + 180, 'out': ang}
    for i, k in enumerate(order):
        d = dmap[k]; b += AR(x, y, d, 78, INK, 2.6); nx, ny = pol(x, y, d, 98); b += NUM(nx, ny, i + 1)
    save(name, svg(w, h, b))


def o13_panels():
    w, h = 690, 240; b = ''; R = 52; cyc = 110
    # (اتجاه v، اتجاه a) للجسم عند الزاوية 0 والدوران عكس عقارب الساعة
    combos = [(90, 0), (90, 180), (180, 90), (90, 90)]
    for i, (dv, da) in enumerate(combos):
        cx = 70 + 172 * i; b += CIRC(cx, cyc, R) + CENTER(cx, cyc) + MOTION(cx, cyc, R, 200, 250)
        x, y = pol(cx, cyc, 0, R); b += DOT(x, y, 6)
        b += AR(x, y, dv, 54, C_VEL, 2.8, 10) + LAB(x, y, dv, 70, 'v', C_VEL, dx=(12 if dv == 90 else 0), dy=(0 if dv == 90 else -14))
        b += AR(x, y, da, 40, C_ACC, 2.8, 10)
        lx, ly = pol(x, y, da, 54); b += AC(lx + (8 if da == 0 else (-6 if da == 180 else -14)), ly + (20 if da in (0, 180) else 6))
        b += NUM(cx + 20, 220, i + 1)
    save('c6l2-o13-panels.svg', svg(w, h, b))


def o13_compass():
    w, h = 470, 330; cx, cy, R = 200, 165, 110; b = CIRC(cx, cy, R) + CENTER(cx, cy) + MOTION(cx, cy, R, 60, 20)
    x, y = pol(cx, cy, 180, R); b += DOT(x, y, 7) + T(x - 18, y - 10, 'Q', 15, italic=True)
    b += COMPASS(400, 80)
    save('c6l2-o13-compass.svg', svg(w, h, b))


def o13_epoints():
    w, h = 420, 380; cx, cy, R = 210, 195, 125; b = CIRC(cx, cy, R) + CENTER(cx, cy) + MOTION(cx, cy, R, 75, 105)
    for ang, lab in ((45, 'A'), (135, 'B'), (225, 'C'), (315, 'D')):
        x, y = pol(cx, cy, ang, R); b += DOT(x, y, 6); tx, ty = pol(cx, cy, ang, R + 22); b += T(tx, ty + 5, lab, 16, weight='bold')
    save('c6l2-o13-e-points.svg', svg(w, h, b))


# ================= O14 =================
def o14_axes():
    w, h = 470, 330; cx, cy, R = 190, 165, 110; b = CIRC(cx, cy, R) + CENTER(cx, cy) + MOTION(cx, cy, R, 120, 160)
    x, y = pol(cx, cy, 0, R); b += DOT(x, y, 7) + T(x + 18, y + 5, 'S', 15, italic=True)
    b += COMPASS(400, 80)
    save('c6l2-o14-axes.svg', svg(w, h, b))


def o14_bottom():
    fbd('c6l2-o14-bottom.svg', [{'angle': 90, 'length': 131, 'label': 'F_T'}, {'angle': -90, 'length': 59, 'label': 'F_g'}], w=360, h=360,
        extra=ARROW(300, 250, 300, 170, MUTED, 1.8, 9) + T(300, 160, '+c', 15, italic=True, color=MUTED))


def o14_table():
    w, h = 400, 330; cx, cy, R = 190, 165, 120; b = CIRC(cx, cy, R, INK, 1.5, '6 5') + DOT(cx, cy, 6, INK, '#fff')
    x, y = pol(cx, cy, 30, R); b += L(cx, cy, x, y, INK, 2) + DOT(x, y, 9, INK, '#aaa')
    b += T(cx + 34, cy - 40, '0.80 m', 14) + MOTION(cx, cy, R, 120, 160)
    save('c6l2-o14-table.svg', svg(w, h, b))


def o14_evert():
    w, h = 380, 400; cx, cy, R = 190, 200, 130; b = CIRC(cx, cy, R, INK, 1.5, '6 5') + DOT(cx, cy, 6, INK, '#fff')
    for ang, lab in ((90, 'العليا'), (270, 'السفلى')):
        x, y = pol(cx, cy, ang, R); b += L(cx, cy, x, y, INK, 2) + DOT(x, y, 10, INK, '#aaa')
        b += T(x + 22, y + 5, 'النقطة ' + lab, 13, 'start')
    b += T(cx - 26, cy - 60, '0.60 m', 14) + MOTION(cx, cy, R, 170, 200)
    save('c6l2-o14-e-vert.svg', svg(w, h, b))


if __name__ == '__main__':
    o01_paths()
    o02_dv(); o02_panels(); o02_compass(); o02_esub()
    tri_pair('c6l2-o03-tri.svg', False); tri_pair('c6l2-o03-e-tri.svg', True)
    o04_ab(); o04_equarter()
    o05_graphs(); o05_ar(); o05_tracks()
    o06_inv(); o06_station()
    o07_net(); car_rear('c6l2-o07-e-car.svg')
    o08_paths(); o08_compass(); o08_target(); o08_erelease()
    o09_hammer(); o09_force(); o09_stopper()
    car_rear('c6l2-o10-car.svg'); o10_rotor()
    car_top('c6l2-o11-car.svg'); car_top('c6l2-o11-e-car.svg', paths=False)
    o12_disc(); o12_track(); o12_ewheel()
    numbered_arrows('c6l2-o13-vel.svg', 45, True, ['out', 'in', 'fwd', 'back'])
    numbered_arrows('c6l2-o13-acc.svg', 200, False, ['fwd', 'out', 'back', 'in'])
    o13_panels(); o13_compass(); o13_epoints()
    o14_axes(); o14_bottom(); o14_table(); o14_evert()
