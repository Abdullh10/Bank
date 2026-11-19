import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 5-3 (القوة والحركة في بعدين) — الأهداف O01–O08
import math


def NUM(x, y, n, color=INK):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="#fff" stroke="{color}" stroke-width="1.6"/>' + T(x, y + 5, str(n), 14, color=color, weight='bold')


def pol(cx, cy, ang, r):
    a = math.radians(ang); return cx + r * math.cos(a), cy - r * math.sin(a)


def FA(cx, cy, ang, length, label='', color=C_FORCE, lab_r=None, dx=0, dy=0, size=17, w=3, vec=True):
    """سهم قوة يبدأ من (cx, cy) بزاوية ang (درجات، 0 = يمين، 90 = أعلى) وطول length، مع تسمية عند رأسه."""
    x2, y2 = pol(cx, cy, ang, length); b = ARROW(cx, cy, x2, y2, color, w)
    if label:
        lx, ly = pol(cx, cy, ang, (lab_r or length + 22)); lx += dx; ly += dy + 6
        b += (V(lx, ly, label, color, size) if vec else T(lx, ly, label, size - 2, 'middle', color))
    return b


def DASHARROW(x1, y1, x2, y2, color=C_FORCE, w=2.2):
    a = math.atan2(y2 - y1, x2 - x1); head = 10
    p1 = (x2 - head * math.cos(a - 0.4), y2 - head * math.sin(a - 0.4)); p2 = (x2 - head * math.cos(a + 0.4), y2 - head * math.sin(a + 0.4))
    return L(x1, y1, x2 - 0.6 * head * math.cos(a), y2 - 0.6 * head * math.sin(a), color, w, '6 4') + f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'


def ARC(cx, cy, r, a1, a2, color=INK, w=1.5):
    """قوس من الزاوية a1 إلى a2 (درجات، عكس عقارب الساعة)."""
    x1, y1 = pol(cx, cy, a1, r); x2, y2 = pol(cx, cy, a2, r)
    large = 1 if (a2 - a1) % 360 > 180 else 0
    return f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 0 {x2:.1f} {y2:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>'


def axes_straight(cx, cy, r=130, xl='+x', yl='+y'):
    return (L(cx - r, cy, cx + r, cy, GRID, 1.5, '5 5') + L(cx, cy - r, cx, cy + r, GRID, 1.5, '5 5')
            + ARROW(cx + r - 4, cy, cx + r + 12, cy, MUTED, 1.5, 9) + ARROW(cx, cy - r + 4, cx, cy - r - 12, MUTED, 1.5, 9)
            + T(cx + r + 14, cy + 20, xl, 15, italic=True, color=MUTED) + T(cx + 12, cy - r - 4, yl, 15, 'start', MUTED, italic=True))


def axes_tilted(cx, cy, ang, r=120, rneg=None, color=MUTED, lab=True):
    """محوران مائلان: +x موازٍ للسطح إلى أعلاه (بزاوية ang)، و+y عمودي على السطح للخارج."""
    rn = rneg if rneg is not None else r; b = ''
    for a, l in ((ang, '+x'), (ang + 90, '+y')):
        x1, y1 = pol(cx, cy, a + 180, rn); x2, y2 = pol(cx, cy, a, r)
        b += L(x1, y1, x2, y2, GRID if color == MUTED else color, 1.5, '5 5') + ARROW(*pol(cx, cy, a, r - 14), x2, y2, color, 1.5, 9)
        if lab:
            lx, ly = pol(cx, cy, a, r + 16); b += T(lx, ly + 5, l, 15, color=color, italic=True)
    return b


def inc_geom(angle, w, h):
    a = math.radians(angle); x0, y0 = 40, h - 40; x1 = w - 40; y1 = y0 - (x1 - x0) * math.tan(a)
    if y1 < 20: y1 = 20; x1 = x0 + (y0 - y1) / math.tan(a)
    mx, my = x0 + 0.55 * (x1 - x0), y0 - 0.55 * (x1 - x0) * math.tan(a)
    nx, ny = -math.sin(a), -math.cos(a)
    return (mx + 24 * nx, my + 24 * ny), (x0, y0, x1, y1)


# ================= O01 =================
def o01_ring3():
    w, h = 420, 360; cx, cy = 210, 175; b = axes_straight(cx, cy, 140)
    b += FA(cx, cy, 0, 90, '30.0 N', vec=False, dy=-14, lab_r=100)
    b += FA(cx, cy, 90, 120, '40.0 N', vec=False, dx=34, lab_r=105)
    b += FA(cx, cy, 233.13, 150, '50.0 N', vec=False, dx=-30, lab_r=120)
    b += ARC(cx, cy, 48, 180, 233.13) + T(cx - 78, cy + 30, '53.1°', 14)
    b += f'<circle cx="{cx}" cy="{cy}" r="9" fill="#fff" stroke="{INK}" stroke-width="3"/>'
    save('c5l3-o01-ring3.svg', svg(w, h, b))


def o01_dots():
    motion_diagram('c5l3-o01-dots.svg', [{'xs': [50 + 80 * k for k in range(7)], 'vel': True}], w=600, axis_label='d', origin=50)


def o01_light():
    w, h = 520, 300; b = ''
    b += RECT(30, 40, 16, 240, INK, '#c9ced6', 1.5) + RECT(474, 40, 16, 240, INK, '#c9ced6', 1.5)
    px, py = 260, 40 + 214 * math.tan(math.radians(30)) * 0 + 123.6
    # الحبلان من أعلى العمودين إلى نقطة التعليق بزاوية 30.0° مع الأفقي
    py = 50 + 214 * math.tan(math.radians(30))
    b += L(46, 50, px, py, INK, 2.5) + L(474, 50, px, py, INK, 2.5)
    b += L(px - 90, py, px + 90, py, MUTED, 1.2, '5 4')
    b += ARC(px, py, 60, 0, 30) + T(px + 82, py - 14, '30.0°', 14) + ARC(px, py, 60, 150, 180) + T(px - 82, py - 14, '30.0°', 14)
    b += L(px, py, px, py + 22, INK, 2.5) + RECT(px - 22, py + 22, 44, 70, INK, '#3b3f46', 2)
    for k, c in enumerate(('#e74c3c', '#f1c40f', '#2ecc71')): b += f'<circle cx="{px}" cy="{py + 36 + 21 * k}" r="8" fill="{c}"/>'
    b += T(px + 70, py + 64, '10.0 kg', 15)
    save('c5l3-o01-light.svg', svg(w, h, b))


# ================= O02 =================
def o02_candidates():
    w, h = 600, 320; b = ''
    cx, cy = 130, 190
    b += FA(cx, cy, 0, 120, 'A', lab_r=140) + FA(cx, cy, 90, 90, 'B', lab_r=110, dx=-16) + DOT(cx, cy, 6)
    b += L(265, 20, 265, 300, GRID, 1.5)
    R = 150; ang = math.degrees(math.atan2(90, 120))
    spots = [(360, 95, ang), (515, 95, 180), (360, 235, 180 + ang), (515, 235, 180 + 90 - ang)]
    lens = [R, 120, R, R]
    for k, ((x, y, a), ln) in enumerate(zip(spots, lens)):
        x0, y0 = pol(x, y, a, -ln / 2); x1, y1 = pol(x, y, a, ln / 2)
        b += ARROW(x0, y0, x1, y1, C_FORCE, 3) + NUM(*pol(x, y, a + 90, 26), k + 1)
    save('c5l3-o02-candidates.svg', svg(w, h, b))


def o02_triangle():
    w, h = 420, 300; b = ''
    O = (70, 240); A = (300, 240); Bp = (360, 70)
    b += ARROW(*O, *A, C_FORCE, 3) + V(185, 266, 'A', C_FORCE)
    b += ARROW(*A, *Bp, C_FORCE, 3) + V(352, 165, 'B', C_FORCE)
    b += DASHARROW(*O, *Bp, C_FORCE, 2.4) + V(195, 130, 'R', C_FORCE)
    save('c5l3-o02-triangle.svg', svg(w, h, b))


def o02_two_forces():
    w, h = 400, 280; cx, cy = 120, 200; b = ''
    b += FA(cx, cy, 0, 200, 'A', lab_r=220) + FA(cx, cy, 60, 150, 'B', lab_r=172) + DOT(cx, cy, 6)
    b += ARC(cx, cy, 45, 0, 60) + T(cx + 62, cy - 16, '60°', 14)
    save('c5l3-o02-two-forces.svg', svg(w, h, b))


def o02_rope():
    w, h = 560, 260; b = ''
    b += RECT(20, 70, 110, 60, INK, '#b9cbe0', 2) + f'<circle cx="45" cy="135" r="14" fill="#555"/><circle cx="105" cy="135" r="14" fill="#555"/>' + T(75, 60, 'السيارة', 14, color=MUTED)
    b += RECT(470, 60, 26, 130, INK, '#a07a52', 2) + f'<circle cx="483" cy="56" r="40" fill="#7fb77e" stroke="{INK}" stroke-width="1.5"/>' + T(483, 215, 'الشجرة', 14, color=MUTED)
    mx, my = 300, 140
    b += L(130, 100, mx, my, INK, 3) + L(mx, my, 470, 100, INK, 3)
    b += L(130, 100, 470, 100, MUTED, 1.2, '5 4')
    b += ARROW(mx, my, mx, my + 80, C_FORCE, 3.5) + V(mx + 22, my + 78, 'F', C_FORCE)
    b += T(mx + 20, my - 46, 'نقطة المنتصف', 13, color=MUTED) + L(mx + 8, my - 40, mx + 2, my - 6, MUTED, 1)
    save('c5l3-o02-rope.svg', svg(w, h, b))


def o02_frames():
    w, h = 560, 230; b = ''
    for k, (x0, apex) in enumerate(((30, 70), (300, 30))):
        b += RECT(x0, 80, 230, 130, INK, '#e9dcc0', 3) + RECT(x0 + 14, 94, 202, 102, INK, '#cdb48a', 1)
        b += L(x0 + 4, 100, x0 + 115, apex, INK, 2) + L(x0 + 115, apex, x0 + 226, 100, INK, 2) + DOT(x0 + 115, apex, 4)
        b += NUM(x0 + 115, 225 - 10, k + 1)
    save('c5l3-o02-frames.svg', svg(w, h + 10, b))


# ================= O03 =================
def o03_polygons():
    w, h = 600, 470; b = ''
    def chain(ox, oy, pts, close=None):
        s = ''; x, y = ox, oy
        for dx, dy in pts:
            s += ARROW(x, y, x + dx, y - dy, C_FORCE, 3); x, y = x + dx, y - dy
        return s
    # 1: مثلث فيه فجوة
    b += chain(60, 190, [(170, 0), (-40, 120), (-110, -100)]) + NUM(150, 222, 1)
    # 2: الضلع الثالث في الاتجاه المعاكس (ليس رأسًا لذيل)
    b += ARROW(340, 190, 510, 190, C_FORCE, 3) + ARROW(510, 190, 470, 70, C_FORCE, 3) + ARROW(340, 190, 470, 70, C_FORCE, 3) + NUM(425, 222, 2)
    # 3: رباعي مغلق رأسًا لذيل
    b += chain(70, 420, [(160, 20), (20, 130), (-110, 20), (-70, -170)]) + NUM(150, 455, 3)
    # 4: ثلاثة متجهات مفتوحة
    b += chain(340, 430, [(90, 90), (110, -20), (-30, 120)]) + NUM(425, 455, 4)
    b += L(300, 20, 300, 450, GRID, 1.5) + L(20, 240, 580, 240, GRID, 1.5)
    save('c5l3-o03-polygons.svg', svg(w, h, b))


def o03_closed4():
    w, h = 440, 320; b = ''
    P = [(60, 260), (260, 280), (380, 140), (200, 40)]
    labs = [('F_1', 0, 26), ('F_2', 26, 0), ('F_3', 10, -18), ('F_4', -26, 0)]
    for k in range(4):
        x1, y1 = P[k]; x2, y2 = P[(k + 1) % 4]
        b += ARROW(x1, y1, x2, y2, C_FORCE, 3)
        lab, dx, dy = labs[k]; b += V((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, lab, C_FORCE)
    save('c5l3-o03-closed4.svg', svg(w, h, b))


def o03_check():
    w, h = 460, 330; cx, cy = 230, 170; b = axes_straight(cx, cy, 150)
    b += FA(cx, cy, 30, 120, '40.0 N', vec=False, lab_r=150)
    b += FA(cx, cy, 150, 120, '40.0 N', vec=False, lab_r=150)
    b += FA(cx, cy, 270, 90, '30.0 N', vec=False, dx=36, lab_r=80)
    b += ARC(cx, cy, 55, 0, 30) + T(cx + 82, cy - 12, '30.0°', 14) + ARC(cx, cy, 55, 150, 180) + T(cx - 82, cy - 12, '30.0°', 14)
    b += DOT(cx, cy, 7)
    save('c5l3-o03-check.svg', svg(w, h, b))


# ================= O04 =================
def o04_perp():
    w, h = 380, 300; cx, cy = 150, 180; b = axes_straight(cx, cy, 120)
    b += FA(cx, cy, 0, 105, '12.0 N', vec=False, dy=-18, lab_r=55) + FA(cx, cy, 90, 140, '16.0 N', vec=False, dx=-36, lab_r=75) + DOT(cx, cy, 7)
    save('c5l3-o04-perp.svg', svg(w, h, b))


def o04_ring():
    w, h = 480, 320; cx, cy = 250, 190; b = axes_straight(cx, cy, 170)
    b += FA(cx, cy, 180, 160, '128 N', vec=False, dy=-18, lab_r=120)
    b += FA(cx, cy, 0, 80, '64.0 N', vec=False, dy=24, lab_r=50)
    b += FA(cx, cy, 30, 152, '122 N', vec=False, dy=-22, dx=-14, lab_r=150)
    b += ARC(cx, cy, 60, 0, 30) + T(cx + 92, cy - 12, '30.0°', 14)
    b += f'<circle cx="{cx}" cy="{cy}" r="9" fill="#fff" stroke="{INK}" stroke-width="3"/>'
    save('c5l3-o04-ring.svg', svg(w, h, b))


def o04_scale():
    w, h = 420, 400; cx, cy = 210, 150; b = ''
    b += L(150, 20, 270, 20, INK, 4) + L(210, 20, 210, 40, INK, 3)
    b += f'<circle cx="210" cy="80" r="38" fill="#f6f1e3" stroke="{INK}" stroke-width="3"/>' + L(210, 80, 222, 58, INK, 2)
    for k in range(12): b += L(*pol(210, 80, k * 30, 30), *pol(210, 80, k * 30, 35), INK, 1.2)
    b += L(210, 118, cx, cy, INK, 2.5) + DOT(cx, cy, 6)
    b += FA(cx, cy, 270 - 27, 190, '75.0 N', vec=False, lab_r=215, dx=-10)
    b += FA(cx, cy, 270 + 27, 190, '75.0 N', vec=False, lab_r=215, dx=10)
    b += FA(cx, cy, 270, 200, '150.0 N', vec=False, lab_r=222)
    b += L(cx, cy, cx, cy + 205, MUTED, 1, '4 4')
    b += ARC(cx, cy, 70, 243, 270) + T(cx - 62, cy + 62, '27.0°', 13) + ARC(cx, cy, 70, 270, 297) + T(cx + 62, cy + 62, '27.0°', 13)
    save('c5l3-o04-scale.svg', svg(w, h, b))


def o04_q65():
    w, h = 420, 320; cx, cy = 170, 210; b = axes_straight(cx, cy, 150)
    b += FA(cx, cy, 90, 120, '33.0 N', vec=False, dx=-38, lab_r=80)
    b += FA(cx, cy, 60, 160, '44.0 N', vec=False, dx=30, lab_r=150)
    b += ARC(cx, cy, 55, 0, 60) + T(cx + 76, cy - 30, '60.0°', 14)
    b += DOT(cx, cy, 7)
    save('c5l3-o04-q65.svg', svg(w, h, b))


# ================= O05 =================
def note(x, y, s, size=15): return T(x, y, s, size, 'start')


def MU(x, y, val, sub='k'):
    return T(x, y, f'μ_{sub}', 17, 'start', italic=True) + T(x + 24, y, f'= {val}', 16, 'start')


def ALAB(angle, h, s):
    x0, y0 = 40, h - 40
    return T(x0 + 64 + (34 if angle < 20 else 0), y0 - 7, s, 14, 'start')


def inc(name, angle, w, h, s, extra=''):
    incline(name, angle, w=w, h=h, angle_label='', extra=ALAB(angle, h, s) + extra)


def o05_smooth():
    inc('c5l3-o05-smooth.svg', 30, 480, 290, '30.0°', note(60, 40, 'سطح أملس'))


def o05_skier():
    (cx, cy), _ = inc_geom(30, 480, 290)
    ex = T(cx, cy + 5, '55 kg', 13) + MU(110, 50, '0.12') + axes_tilted(cx, cy, 30, 95, 0)
    inc('c5l3-o05-skier.svg', 30, 480, 290, '30.0°', ex)


def o05_pull():
    (cx, cy), _ = inc_geom(14, 520, 230)
    ex = T(cx, cy + 5, '63 kg', 13) + MU(80, 50, '0.27')
    x2, y2 = pol(cx, cy, 14, 170); ex += ARROW(*pol(cx, cy, 14, 30), x2, y2, C_FORCE, 3) + V(x2 - 30, y2 - 18, 'F_T', C_FORCE) + T(x2 + 8, y2 - 34, '512 N', 14, color=C_FORCE)
    inc('c5l3-o05-pull.svg', 14, 520, 230, '14.0°', ex)


# ================= O06 =================
def o06_components():
    ang = 30; (cx, cy), _ = inc_geom(ang, 520, 340)
    L0 = 130; gx, gy = cx, cy + L0
    par = L0 * math.sin(math.radians(ang)); per = L0 * math.cos(math.radians(ang))
    p1 = pol(cx, cy, 180 + ang, par); p2 = pol(cx, cy, 270 + ang, per)
    ex = ARROW(cx, cy, gx, gy, C_FORCE, 3) + V(gx + 22, gy, 'F_g', C_FORCE)
    ex += DASHARROW(cx, cy, *p1) + NUM(p1[0] - 4, p1[1] - 26, 1) + DASHARROW(cx, cy, *p2) + NUM(p2[0] + 22, p2[1] - 4, 2)
    ex += L(*p1, gx, gy, MUTED, 1, '3 3') + L(*p2, gx, gy, MUTED, 1, '3 3')
    incline('c5l3-o06-components.svg', ang, w=520, h=340, angle_label='θ', extra=ex)


def o06_box650():
    (cx, cy), _ = inc_geom(40, 460, 330)
    ex = FA(cx, cy, 270, 110, '', ) + V(cx + 26, cy + 112, 'F_g', C_FORCE) + T(cx + 40, cy + 117, '= 650 N', 14, 'start')
    inc('c5l3-o06-box650.svg', 40, 460, 330, '40.0°', ex)


def o06_proof():
    w, h = 480, 380; cx, cy = 230, 170; ang = 25; b = ''
    # خط السطح المائل تحت النقطة
    b += axes_tilted(cx, cy, ang, 150, 150)
    b += FA(cx, cy, 270, 170, 'F_g', dx=18, lab_r=170)
    b += ARC(cx, cy, 60, 270, 270 + ang, INK, 1.6) + T(*[v + d for v, d in zip(pol(cx, cy, 270 + ang / 2, 78), (0, 5))], 'α', 17, italic=True)
    b += DOT(cx, cy, 6)
    # زاوية ميل السطح للمقارنة
    b += L(40, 350, 200, 350, INK, 1.6) + L(40, 350, *pol(40, 350, ang, 175), INK, 1.6) + ARC(40, 350, 50, 0, ang) + T(108, 342, 'θ', 16, italic=True)
    b += T(120, 375, 'السطح المائل', 13, color=MUTED)
    save('c5l3-o06-proof.svg', svg(w, h + 10, b))


# ================= O07 =================
def mini(cx, cy, ang, forces, num):
    b = L(*pol(cx, cy + 0, 180 + ang, 95), *pol(cx, cy, ang, 95), MUTED, 1.4, '6 4')
    for a, ln, lab in forces:
        b += FA(cx, cy, a, ln, lab, size=15, lab_r=ln + 17)
    return b + DOT(cx, cy, 6) + NUM(cx - 100, cy - 90, num)


def o07_choices():
    w, h = 600, 520; ang = 25; b = ''
    up, down, nrm = ang, 180 + ang, 90 + ang
    b += mini(150, 130, ang, [(270, 100, 'F_g'), (nrm, 90, 'F_N'), (down, 55, 'f_k')], 1)
    b += mini(450, 130, ang, [(270, 100, 'F_g'), (nrm, 90, 'F_N'), (up, 55, 'f_k')], 2)
    b += mini(150, 390, ang, [(270, 100, 'F_g'), (90, 100, 'F_N'), (up, 55, 'f_k')], 3)
    b += mini(450, 390, ang, [(270, 100, 'F_g'), (nrm, 90, 'F_N'), (up, 55, 'f_k'), (down, 75, 'F')], 4)
    b += L(300, 15, 300, 505, GRID, 1.5) + L(15, 260, 585, 260, GRID, 1.5)
    save('c5l3-o07-choices.svg', svg(w, h, b))


def o07_pull_up():
    (cx, cy), _ = inc_geom(20, 500, 260)
    x2, y2 = pol(cx, cy, 20, 150)
    ex = ARROW(*pol(cx, cy, 20, 30), x2, y2, C_FORCE, 3) + V(x2 - 4, y2 - 18, 'F_T', C_FORCE)
    vx, vy = pol(cx, cy, 110, 60); ex += ARROW(vx - 30, vy - 4, *pol(vx - 30, vy - 4, 20, 60), C_VEL, 2.6) + V(vx - 46, vy - 2, 'v', C_VEL)
    ex += T(70, 40, 'سطح خشن', 15, 'start')
    incline('c5l3-o07-pull-up.svg', 20, w=500, h=260, angle_label='θ', extra=ex)


def o07_wrong():
    (cx, cy), _ = inc_geom(30, 480, 320)
    ex = FA(cx, cy, 270, 100, 'F_g', dx=22, lab_r=95) + FA(cx, cy, 90, 100, 'F_N', dx=24, lab_r=95)
    ex += T(80, 40, 'الصندوق ساكن', 15, 'start')
    incline('c5l3-o07-wrong.svg', 30, w=480, h=320, angle_label='θ', extra=ex)


def o07_scene():
    incline('c5l3-o07-scene.svg', 25, w=480, h=280, angle_label='θ', extra=T(70, 40, 'سطح خشن، والصندوق ينزلق إلى أسفل', 15, 'start'))


# ================= O08 =================
def o08_slide():
    (cx, cy), _ = inc_geom(35, 460, 320)
    inc('c5l3-o08-slide.svg', 35, 460, 320, '35°', T(cx, cy + 5, '43 kg', 13))


def o08_graph():
    pts = [(t, 98.0 * math.cos(math.radians(t))) for t in range(0, 91, 2)]
    graph('c5l3-o08-graph.svg', [{'pts': pts, 'color': C_FORCE}], (0, 90), (0, 100), 'زاوية الميل (°)', 'القوة العمودية (N)', 10, 10, w=560, h=380)


def o08_two():
    w, h = 600, 260; b = ''
    b += RECT(30, 200, 220, 16, INK, '#f3efe6', 2) + RECT(110, 152, 60, 48) + T(140, 181, '5.00 kg', 13) + NUM(140, 240, 1)
    a = math.radians(30); x0, y0 = 300, 216; x1 = 580; y1 = y0 - (x1 - x0) * math.tan(a)
    b += f'<polygon points="{x0},{y0} {x1},{y0} {x1},{y1:.1f}" fill="#f3efe6" stroke="{INK}" stroke-width="2"/>'
    mx, my = x0 + 0.55 * (x1 - x0), y0 - 0.55 * (x1 - x0) * math.tan(a); cx, cy = mx - 24 * math.sin(a), my - 24 * math.cos(a)
    b += RECT(cx - 30, cy - 24, 60, 48, rot=-30, cx=cx, cy=cy) + T(cx, cy + 5, '5.00 kg', 13)
    b += ARC(x0, y0, 50, 0, 30) + T(x0 + 70, y0 - 8, '30.0°', 14) + NUM(440, 240, 2)
    save('c5l3-o08-two.svg', svg(w, h, b))


if __name__ == '__main__':
    o01_ring3(); o01_dots(); o01_light()
    o02_candidates(); o02_triangle(); o02_two_forces(); o02_rope(); o02_frames()
    o03_polygons(); o03_closed4(); o03_check()
    o04_perp(); o04_ring(); o04_scale(); o04_q65()
    o05_smooth(); o05_skier(); o05_pull()
    o06_components(); o06_box650(); o06_proof()
    o07_choices(); o07_pull_up(); o07_wrong(); o07_scene()
    o08_slide(); o08_graph(); o08_two()
