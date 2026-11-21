import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 6-1 (حركة المقذوف) — الأهداف O10–O17
# كالكتاب (ص163–165): مركّبتا السرعة v_x وv_y حمراوان، والسرعة المحصلة حمراء متقطعة، والتسارع بنفسجي رأسي إلى أسفل فقط.
# لا تُكتب الكمية المطلوبة على الرسم.
import math, re

G = 9.80


class Proj:
    """مشهد مقذوف: إحداثيات عالمية بالمتر (y لأعلى)، s بكسل لكل متر."""
    def __init__(self, w, h, origin, s):
        self.w, self.h, self.o, self.s = w, h, origin, s; self.b = ''

    def P(self, x, y): return (self.o[0] + x * self.s, self.o[1] - y * self.s)

    def path(self, vx, vy, t0=0.0, t1=None, y0=0.0, color=MUTED, dash='7 5', w=2, n=80):
        t1 = 2 * vy / G if t1 is None else t1
        pts = [self.P(vx * t, y0 + vy * t - 0.5 * G * t * t) for t in [t0 + (t1 - t0) * k / n for k in range(n + 1)]]
        self.b += f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}"/>'

    def at(self, vx, vy, t, y0=0.0): return self.P(vx * t, y0 + vy * t - 0.5 * G * t * t)

    def ground(self, x0, x1, y=0.0):
        a, b = self.P(x0, y), self.P(x1, y); self.b += L(a[0], a[1], b[0], b[1], INK, 2.5)

    def raw(self, s): self.b += s

    def save(self, name): save(name, svg(self.w, self.h, self.b))


def comps(px, py, vx, vy, k, lab=True, res=False, size=16, vxl=None, vyl=None):
    """مركّبتا السرعة عند نقطة (بكسل): vx، vy بالـ m/s، k بكسل لكل m/s."""
    b = ''
    if abs(vx) > 1e-9:
        b += ARROW(px, py, px + vx * k, py, C_VEL, 2.6, 10)
        if lab: b += V(px + vx * k + 6, py + 6, vxl or 'v_x', C_VEL, size, 'start')
    if abs(vy) > 1e-9:
        b += ARROW(px, py, px, py - vy * k, C_VEL, 2.6, 10)
        if lab: b += V(px - 8, py - vy * k / 2 + 5, vyl or 'v_y', C_VEL, size, 'end')
    if res: b += L(px, py, px + vx * k, py - vy * k, C_VEL, 1.8, '5 4') + ARROW(px + 0.9 * vx * k, py - 0.9 * vy * k, px + vx * k, py - vy * k, C_VEL, 1.8, 9)
    return b + DOT(px, py, 4.5, INK)


def acc(px, py, n=48, lab=True, dx=0):
    b = ARROW(px + dx, py, px + dx, py + n, C_ACC, 2.6, 10)
    if lab: b += V(px + dx + 8, py + n - 4, 'g', C_ACC, 16, 'start')
    return b


def arc(cx, cy, r, a1, a2, color=INK):
    p1 = (cx + r * math.cos(math.radians(a1)), cy - r * math.sin(math.radians(a1)))
    p2 = (cx + r * math.cos(math.radians(a2)), cy - r * math.sin(math.radians(a2)))
    return f'<path d="M {p1[0]:.1f} {p1[1]:.1f} A {r} {r} 0 0 0 {p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="{color}" stroke-width="1.5"/>'


def dimv(x, y1, y2, label, color=INK, side='end', dx=-8):
    """سهم بعد رأسي برأسين مع تسمية."""
    return ARROW(x, (y1 + y2) / 2, x, y1, color, 1.5, 8) + ARROW(x, (y1 + y2) / 2, x, y2, color, 1.5, 8) + T(x + dx, (y1 + y2) / 2 + 5, label, 15, side, color)


def dimh(x1, x2, y, label, color=INK):
    return ARROW((x1 + x2) / 2, y, x1, y, color, 1.5, 8) + ARROW((x1 + x2) / 2, y, x2, y, color, 1.5, 8) + L(x1, y - 7, x1, y + 7, color, 1.5) + L(x2, y - 7, x2, y + 7, color, 1.5) + T((x1 + x2) / 2, y + 22, label, 15, 'middle', color)


def axes_xy(x, y, n=44):
    return (ARROW(x, y, x + n, y, MUTED, 1.6, 8) + ARROW(x, y, x, y - n, MUTED, 1.6, 8) +
            T(x + n + 4, y + 5, '+x', 14, 'start', MUTED, italic=True) + T(x, y - n - 6, '+y', 14, 'middle', MUTED, italic=True))


def EQ(x, y, sym, rest, color=INK, size=14, anchor='start', vec=True):
    """رمز (متجه: عريض مائل، أو قياسي: مائل) يتبعه نص قائم (= قيمة ووحدة)."""
    t = T(0, 0, sym, size, 'start', color, 'bold' if vec else 'normal', True)
    inner = re.search(r'>(.*)</text>$', t, re.S).group(1)
    w = 'bold' if vec else 'normal'
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" {MATHFONT}>'
            f'<tspan font-weight="{w}" font-style="italic">{inner}</tspan><tspan font-weight="normal" font-style="normal">{esc(rest)}</tspan></text>')


def letter(px, py, s, dx=0, dy=-12): return T(px + dx, py + dy, s, 16, 'middle', INK, 'bold')


# ---------- O10 ----------
def o10():
    vx, vy = 12.0, 14.0; Tf = 2 * vy / G
    sc = Proj(560, 300, (50, 250), 14.0); sc.ground(-1, 37); sc.path(vx, vy)
    for t, s, d in [(0, 'A', (-10, -10)), (0.45, 'B', (-14, -6)), (vy / G, 'C', (0, -14)), (Tf - 0.45, 'D', (14, -6)), (Tf, 'E', (10, -10))]:
        x, y = sc.at(vx, vy, t); sc.raw(DOT(x, y, 6, INK) + letter(x, y, s, *d))
    sc.raw(axes_xy(470, 120)); sc.save('c6l1-o10-points.svg')

    sc = Proj(600, 330, (60, 285), 14.0); sc.ground(-1, 38); sc.path(vx, vy); k = 4.0
    for t, s in [(0, 'A'), (0.55, 'B'), (vy / G, 'C'), (Tf - 0.55, 'D'), (Tf, 'E')]:
        x, y = sc.at(vx, vy, t); vyt = vy - G * t
        if s == 'C': sc.raw(DOT(x, y, 5, INK) + T(x, y - 14, 'C ?', 16, 'middle', INK, 'bold'))
        else: sc.raw(comps(x, y, vx, vyt, k, lab=(s == 'A')) + letter(x, y, s, -14 if s in 'AB' else 14, (22 if s == 'A' else 10) if s in 'AB' else -8))
    sc.raw(axes_xy(520, 140)); sc.save('c6l1-o10-components.svg')

    # مساران بالسرعة نفسها 20.0 m/s بزاويتين 30.0° و60.0°
    sc = Proj(560, 300, (50, 255), 6.6); sc.ground(-1, 76)
    for th, c, d in [(30.0, INK, '7 5'), (60.0, ORANGE, '3 4')]:
        vx, vy = 20 * math.cos(math.radians(th)), 20 * math.sin(math.radians(th)); sc.path(vx, vy, color=c, dash=d, w=2.4)
    x0, y0 = sc.P(0, 0)
    sc.raw(arc(x0, y0, 60, 0, 30) + T(x0 + 66, y0 - 7, '30.0°', 13, 'start') + arc(x0, y0, 26, 0, 60) + L(x0 + 8, y0 - 24, x0 - 6, y0 - 38, INK, 1) + T(x0 - 8, y0 - 40, '60.0°', 13, 'end'))
    sc.raw(T(250, 90, 'المسار (2): الزاوية ‎60.0°‎', 14, 'start', ORANGE) + T(300, 205, 'المسار (1): الزاوية ‎30.0°‎', 14, 'start', INK))
    sc.raw(T(280, 285, 'مقدار السرعة الابتدائية في المسارين ‎20.0 m/s', 14, 'middle', INK))
    sc.save('c6l1-o10-two-angles.svg')

    # أعلى المسار: مركّبة السرعة الأفقية فقط
    vx, vy = 12.0, 12.0
    sc = Proj(460, 260, (40, 225), 13.0); sc.ground(-1, 31); sc.path(vx, vy)
    x, y = sc.at(vx, vy, vy / G); sc.raw(comps(x, y, vx, 0, 4.5) + letter(x, y, 'C', -14, -8)); sc.raw(axes_xy(390, 120))
    sc.save('c6l1-o10-top.svg')


# ---------- O11 ----------
def o11():
    vx, vy = 12.0, 14.0; Tf = 2 * vy / G; R = vx * Tf; H = vy * vy / (2 * G)
    sc = Proj(560, 330, (60, 250), 13.0); sc.ground(-2, 37); sc.path(vx, vy, color=INK, dash='', w=2)
    x0, y0 = sc.P(0, 0); xt, yt = sc.at(vx, vy, vy / G); xr, _ = sc.P(R, 0)
    sc.raw(ARROW(x0, y0, x0 + 55, y0 - 55 * vy / vx, C_VEL, 2.6) + V(x0 + 34, y0 - 72, 'v_i', C_VEL, 16, 'end'))
    sc.raw(arc(x0, y0, 30, 0, math.degrees(math.atan2(vy, vx))) + T(x0 + 44, y0 - 12, '(1)', 14, 'start'))
    sc.raw(L(xt, yt, xt, y0, MUTED, 1.5, '5 4') + dimv(xt + 16, yt, y0, '(2)', INK, 'start', 8))
    sc.raw(dimh(x0, xr, y0 + 26, '(3)'))
    sc.save('c6l1-o11-marked.svg')

    # تحقق من رسم المركّبات: الخطأ عند C (المركّبة الرأسية نحو الأعلى بعد القمة)
    sc = Proj(600, 330, (60, 290), 14.0); sc.ground(-1, 38); sc.path(vx, vy); k = 4.0
    for t, s, wrong in [(0.45, 'A', False), (vy / G, 'B', False), (Tf - 0.7, 'C', True), (Tf - 0.1, 'D', False)]:
        x, y = sc.at(vx, vy, t); vyt = vy - G * t
        if wrong: vyt = -vyt
        sc.raw(comps(x, y, vx, vyt, k, lab=False) + letter(x, y, s, -14 if s == 'A' else (0 if s == 'B' else 16), -12 if s != 'D' else -14))
    sc.raw(T(300, 318, 'الأسهم الحمراء: المركّبتان الأفقية والرأسية للسرعة المتجهة', 13, 'middle', C_VEL))
    sc.raw(axes_xy(530, 120)); sc.save('c6l1-o11-check.svg')

    sc = Proj(560, 300, (50, 255), 14.0); sc.ground(-1, 37); sc.path(vx, vy)
    for t, s, d in [(0.5, 'A', (-14, -6)), (vy / G, 'B', (0, -14)), (Tf - 0.5, 'C', (14, -6))]:
        x, y = sc.at(vx, vy, t); sc.raw(DOT(x, y, 6, INK) + letter(x, y, s, *d))
    sc.raw(axes_xy(470, 120)); sc.save('c6l1-o11-accel.svg')

    # نقطة P وحدها بمركّبتين: أفقية إلى اليمين ورأسية إلى أسفل
    b = comps(150, 110, 1, -0.7, 110, lab=True, size=17) + letter(150, 110, 'P', -14, -6) + axes_xy(300, 200)
    save('c6l1-o11-point.svg', svg(380, 240, b))

    # رسم طالب فيه أخطاء
    sc = Proj(620, 340, (60, 280), 14.0); sc.ground(-1, 38); sc.path(vx, vy); k = 4.0
    for t, s in [(0.45, 'A'), (vy / G, 'B'), (Tf - 0.45, 'C')]:
        x, y = sc.at(vx, vy, t); vyt = vy - G * t
        if s == 'A':
            sc.raw(comps(x, y, vx, vyt, k, lab=True) + letter(x, y, s, 12, 20))
            sc.raw(ARROW(x, y, x + 30, y - 30 * vyt / vx, C_ACC, 2.6) + V(x + 22, y - 30 * vyt / vx - 6, 'a', C_ACC, 16, 'end'))
        elif s == 'B':
            sc.raw(DOT(x, y, 5, INK) + letter(x, y, s, 0, -14) + T(x + 12, y + 22, 'v = 0', 15, 'start', C_VEL, italic=True))
            sc.raw(T(x + 12, y + 42, 'a = 0', 15, 'start', C_ACC, italic=True))
        else:
            sc.raw(comps(x, y, vx * 0.45, vyt, k, lab=False) + letter(x, y, s, 16, -8))
            sc.raw(ARROW(x, y, x + 30, y - 30 * vyt / vx, C_ACC, 2.6) + V(x + 34, y - 30 * vyt / vx + 14, 'a', C_ACC, 16, 'start'))
    sc.raw(axes_xy(550, 120)); sc.save('c6l1-o11-student.svg')


# ---------- O12 ----------
def o12():
    vx, vy = 15 * math.cos(math.radians(30)), 15 * math.sin(math.radians(30)); Tf = 2 * vy / G
    sc = Proj(520, 240, (50, 195), 21.0); sc.ground(-1, 21.5); sc.path(vx, vy)
    x0, y0 = sc.P(0, 0)
    sc.raw(ARROW(x0, y0, x0 + 90 * math.cos(math.radians(30)), y0 - 90 * math.sin(math.radians(30)), C_VEL, 2.8) + V(x0 + 60, y0 - 60, 'v_i', C_VEL, 17, 'end'))
    sc.raw(T(x0 + 92, y0 - 62, '15.0 m/s', 14, 'start', C_VEL))
    sc.raw(arc(x0, y0, 44, 0, 30) + T(x0 + 50, y0 - 6, '30.0°', 13, 'start'))
    xe, ye = sc.at(vx, vy, Tf); sc.raw(DOT(xe, ye, 5, INK)); sc.raw(axes_xy(440, 90))
    sc.save('c6l1-o12-given.svg')

    vy = math.sqrt(2 * G * 5.0); vx = 6.0; Tf = 2 * vy / G
    sc = Proj(460, 260, (40, 225), 15.0); sc.ground(-1, 13.5); sc.path(vx, vy)
    xt, yt = sc.at(vx, vy, vy / G); _, y0 = sc.P(0, 0)
    sc.raw(L(xt, yt, xt, y0, MUTED, 1.5, '5 4') + dimv(xt + 16, yt, y0, '5.0 m', INK, 'start', 8))
    sc.raw(DOT(*sc.P(0, 0), 5, INK)); sc.raw(axes_xy(380, 110)); sc.save('c6l1-o12-ymax.svg')

    # جرف 30.0 m وكرة بسرعة 12.0 m/s بزاوية 40.0°
    vx, vy = 12 * math.cos(math.radians(40)), 12 * math.sin(math.radians(40))
    a, bq, c = -0.5 * G, vy, 30.0; t = (-bq - math.sqrt(bq * bq - 4 * a * c)) / (2 * a)
    sc = Proj(560, 330, (90, 110), 6.4)
    x0, y0 = sc.P(0, 0); _, yb = sc.P(0, -30)
    sc.raw(RECT(10, y0, x0 - 10, yb - y0, INK, '#efe9dd'))
    sc.ground(-12, 72, -30); sc.path(vx, vy, t1=t)
    sc.raw(ARROW(x0, y0, x0 + 70 * math.cos(math.radians(40)), y0 - 70 * math.sin(math.radians(40)), C_VEL, 2.8) + V(x0 + 30, y0 - 50, 'v_i', C_VEL, 17, 'end'))
    sc.raw(T(x0 + 60, y0 - 52, '12.0 m/s', 14, 'start', C_VEL) + arc(x0, y0, 36, 0, 40) + T(x0 + 42, y0 - 4, '40.0°', 13, 'start'))
    sc.raw(dimv(x0 - 22, y0, yb, '30.0 m', INK, 'end', -8))
    sc.raw(axes_xy(470, 120)); sc.save('c6l1-o12-cliff.svg')

    # سهم يُطلق بسرعة 45.0 m/s بزاوية 25.0° نحو هدف على ارتفاع الإطلاق نفسه
    vx, vy = 45 * math.cos(math.radians(25)), 45 * math.sin(math.radians(25)); Tf = 2 * vy / G
    sc = Proj(560, 230, (40, 185), 2.95); sc.ground(-1, 172); sc.path(vx, vy)
    x0, y0 = sc.P(0, 0); xr, _ = sc.P(vx * Tf, 0)
    sc.raw(ARROW(x0, y0, x0 + 80 * math.cos(math.radians(25)), y0 - 80 * math.sin(math.radians(25)), C_VEL, 2.8) + V(x0 + 40, y0 - 40, 'v_i', C_VEL, 17, 'end'))
    sc.raw(T(x0 + 40, y0 - 62, '45.0 m/s', 14, 'start', C_VEL) + arc(x0, y0, 40, 0, 25) + T(x0 + 46, y0 - 4, '25.0°', 13, 'start'))
    sc.raw(RECT(xr - 4, y0 - 34, 8, 34, INK, '#d35400', 1) + T(xr, y0 + 20, 'الهدف', 13))
    sc.raw(axes_xy(470, 70)); sc.save('c6l1-o12-arrow.svg')


# ---------- O13 ----------
def o13():
    sc = Proj(560, 300, (50, 250), 13.0); sc.ground(-1, 37)
    vx, vy = 12.0, 14.0; sc.path(vx, vy, color=MUTED, dash='7 5', w=2.4)
    # مسار مع مقاومة الهواء (نموذج نوعي: تخميد خطي)
    k = 0.35; pts = []
    for i in range(400):
        t = i * 0.01; x = vx / k * (1 - math.exp(-k * t)); y = (vy + G / k) / k * (1 - math.exp(-k * t)) - G / k * t
        if y < 0 and t > 0.1: break
        pts.append(sc.P(x, y))
    sc.raw(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{ORANGE}" stroke-width="2.4"/>')
    xa, ya = sc.at(vx, vy, 2.3); sc.raw(T(xa + 16, ya - 6, '(1)', 15, 'start', MUTED, 'bold'))
    xb, yb = pts[len(pts) * 3 // 4]; sc.raw(T(xb - 34, yb + 4, '(2)', 15, 'end', ORANGE, 'bold'))
    x0, y0 = sc.P(0, 0); sc.raw(DOT(x0, y0, 5, INK))
    sc.raw(T(280, 286, 'الكرة نفسها أُطلقت بالسرعة الابتدائية نفسها في الحالتين', 13, 'middle', INK))
    sc.save('c6l1-o13-paths.svg')


# ---------- O14 ----------
def o14():
    # صور متتالية بفترات زمنية متساوية: A تسقط من السكون، وB تُقذف أفقيًا
    w, h = 460, 480; b = ''; x0, y0 = 90, 50
    for i in range(6):
        y = y0 + 16.0 * i * i
        b += L(30, y, w - 20, y, GRID, 1.2, '4 4') + DOT(x0, y, 6.5, INK, '#cfd8e3') + DOT(x0 + 55 + i * 55, y, 6.5, '#b9770e', '#f4d03f')
    b += T(x0, h - 10, 'A', 16, 'middle', INK, 'bold') + T(x0 + 55, y0 - 18, 'B', 16, 'middle', INK, 'bold')
    b += ARROW(x0 + 70, y0 - 18, x0 + 120, y0 - 18, C_VEL, 2.4) + V(x0 + 126, y0 - 13, 'v_x', C_VEL, 15, 'start')
    save('c6l1-o14-strobe.svg', svg(w, h, b))

    # كرة تُقذف أفقيًا: مواقعها كل 0.10 s على شبكة (0.10 m لكل مربع)
    w, h = 470, 350; ox, oy = 70, 50; b = ''
    # شبكة بسيطة: خطوط كل 0.10 m أفقيًا وكل 0.10 m رأسيًا
    sx = 360  # بكسل لكل متر
    for i in range(0, 11): b += L(ox + i * 0.1 * sx, oy, ox + i * 0.1 * sx, oy + 0.6 * sx, GRID, 1) if ox + i * 0.1 * sx < w else ''
    for j in range(0, 7): b += L(ox, oy + j * 0.1 * sx, w - 10, oy + j * 0.1 * sx, GRID, 1)
    vxx = 3.0
    for i in range(4):
        t = 0.1 * i; x = ox + vxx * t * sx; y = oy + 0.5 * G * t * t * sx
        b += DOT(x, y, 7, '#b9770e', '#f4d03f') + T(x, oy - 10, f'{vxx * t:.2f}', 13) + T(x + 11, y + 19, f'({i + 1})', 12, 'start', MUTED)
    b += T(ox - 12, oy + 5, 'B', 15, 'end', INK, 'bold')
    b += T(ox - 8, oy - 26, 'x (m)', 13, 'start', MUTED, italic=True)
    b += T(w / 2, h - 30, 'الفترة الزمنية بين كل صورتين متتاليتين ‎0.10 s', 14, 'middle', INK) + T(w / 2, h - 10, 'طول ضلع المربع في الشبكة ‎0.10 m', 14, 'middle', INK)
    save('c6l1-o14-grid.svg', svg(w, h, b))

    # طاولة وكرتان تتدحرجان عن حافتها
    # طاولتان متماثلتان ارتفاع كل منهما 1.22 m
    w, h = 560, 280; b = L(20, 244, w - 20, 244, INK, 2.5)
    for dx, lab, fill, edge, v, n in [(0, 'A', '#cfd8e3', INK, '1.0 m/s', 40), (270, 'B', '#f4d03f', '#b9770e', '2.0 m/s', 80)]:
        b += RECT(30 + dx, 110, 150, 14, INK, '#c8a97e') + RECT(46 + dx, 124, 12, 120, INK, '#c8a97e') + RECT(156 + dx, 124, 12, 120, INK, '#c8a97e')
        b += DOT(166 + dx, 98, 11, edge, fill) + ARROW(180 + dx, 98, 180 + dx + n, 98, C_VEL, 2.4) + T(180 + dx + n / 2, 88, v, 13, 'middle', C_VEL) + T(150 + dx, 92, lab, 15, 'end', INK, 'bold')
        b += dimv(196 + dx, 124, 244, '1.22 m', INK, 'start', 8)
    b += T(w / 2, 270, 'تغادر الكرتان حافتي الطاولتين في اللحظة نفسها', 13, 'middle', INK)
    save('c6l1-o14-table.svg', svg(w, h, b))


# ---------- O15 ----------
def o15():
    vx, vy = 12.0, 14.0
    sc = Proj(520, 280, (50, 240), 12.5); sc.ground(-1, 37); sc.path(vx, vy, color=INK, dash='', w=2.2)
    xa, ya = sc.at(vx, vy, 2.2); sc.raw(ARROW(xa + 60, ya - 40, xa + 6, ya - 4, INK, 1.6, 9) + T(xa + 66, ya - 42, '؟', 18, 'start', INK, 'bold'))
    sc.raw(DOT(*sc.P(0, 0), 5, INK)); sc.save('c6l1-o15-name.svg')

    Tf = 2 * vy / G; R = vx * Tf
    sc = Proj(560, 320, (60, 245), 12.5); sc.ground(-2, 39); sc.path(vx, vy, color=INK, dash='', w=2.2)
    x0, y0 = sc.P(0, 0); xr, _ = sc.P(R, 0)
    xa, ya = sc.at(vx, vy, 0.9); sc.raw(ARROW(xa - 50, ya - 30, xa - 6, ya - 4, INK, 1.6, 9) + T(xa - 56, ya - 32, '(1)', 15, 'end', INK, 'bold'))
    sc.raw(dimh(x0, xr, y0 + 26, '(2)'))
    sc.raw(EQ(x0 - 8, y0 - 10, 't', ' = 0 s', MUTED, 13, 'end', vec=False) + EQ(xr + 8, y0 - 10, 't', ' = 2.9 s', MUTED, 13, vec=False))
    sc.raw(DOT(x0, y0, 5, INK) + DOT(xr, y0, 5, INK)); sc.save('c6l1-o15-blanks.svg')


# ---------- O16 ----------
def o16():
    vx, vy = 8.0, 12.0; Tf = 2 * vy / G; k = 7.0
    sc = Proj(600, 330, (70, 300), 24.0); sc.ground(-1, 21); sc.path(vx, vy)
    ta = (vy - 6.0) / G; xa, ya = sc.at(vx, vy, ta); xe, ye = sc.at(vx, vy, Tf - ta)
    sc.raw(L(xa - 30, ya, xe + 30, ye, MUTED, 1.2, '3 4'))
    sc.raw(comps(xa, ya, vx, 6.0, k, lab=False) + letter(xa, ya, 'A', -14, 18))
    sc.raw(EQ(xa + vx * k + 6, ya + 20, 'v_x', ' = 8.0 m/s', C_VEL) + EQ(xa - 8, ya - 3 * k - 4, 'v_y', ' = 6.0 m/s', C_VEL, anchor='end'))
    sc.raw(DOT(xe, ye, 6, INK) + letter(xe, ye, 'E', 14, -8)); sc.raw(axes_xy(520, 90)); sc.save('c6l1-o16-AE.svg')

    vx, vy = 10.0, 13.72
    sc = Proj(520, 260, (50, 220), 11.0); sc.ground(-1, 40); sc.path(vx, vy)
    xt, yt = sc.at(vx, vy, vy / G); sc.raw(DOT(xt, yt, 5, INK) + EQ(xt, yt - 12, 't', ' = 1.4 s', INK, anchor='middle', vec=False))
    x0, y0 = sc.P(0, 0); sc.raw(DOT(x0, y0, 5, INK) + EQ(x0 + 4, y0 + 20, 't', ' = 0 s', INK, anchor='middle', vec=False))
    sc.save('c6l1-o16-times.svg')

    vx, vy = 6.0, 14.7; k = 3.2
    sc = Proj(600, 340, (110, 300), 18.0); sc.ground(-3, 20); sc.path(vx, vy)
    pts = [(0.0, 'A', '+14.7 m/s'), (0.5, 'B', '+9.8 m/s'), (1.5, 'C', '0 m/s'), (2.5, 'D', '?'), (3.0, 'E', '?')]
    for t, s, lab in pts:
        x, y = sc.at(vx, vy, t); vyt = vy - G * t
        if s in 'AB': sc.raw(ARROW(x, y, x, y - vyt * k, C_VEL, 2.4, 9) + T(x - 8, y - vyt * k / 2, lab, 13, 'end', C_VEL))
        elif s == 'C': sc.raw(EQ(x, y - 30, 'v_y', ' = ' + lab, C_VEL, 13, 'middle'))
        else: sc.raw(EQ(x + 12, y - (4 if s == 'D' else 24), 'v_y', ' = ?', C_VEL, 13))
        sc.raw(DOT(x, y, 5, INK) + letter(x, y, s, 12 if s in 'AB' else (0 if s == 'C' else -12), 18 if s != 'C' else -12))
    sc.raw(L(*sc.at(vx, vy, 0.5), *sc.at(vx, vy, 2.5), MUTED, 1.2, '3 4'))
    sc.raw(axes_xy(530, 90)); sc.save('c6l1-o16-heights.svg')


# ---------- O17 ----------
def plane(x, y):
    return (f'<path d="M {x - 50} {y} L {x + 40} {y} Q {x + 55} {y} {x + 50} {y + 8} L {x - 45} {y + 8} Z" fill="#d6dbe3" stroke="{INK}" stroke-width="1.5"/>'
            f'<path d="M {x - 50} {y} L {x - 58} {y - 16} L {x - 42} {y} Z" fill="#d6dbe3" stroke="{INK}" stroke-width="1.5"/>'
            f'<path d="M {x - 5} {y + 4} L {x - 20} {y + 20} L {x + 8} {y + 4} Z" fill="#c2c8d2" stroke="{INK}" stroke-width="1.2"/>')


def o17():
    w, h = 560, 330; b = plane(120, 50) + ARROW(185, 54, 245, 54, C_VEL, 2.6) + V(250, 60, 'v', C_VEL, 16, 'start')
    b += L(20, 300, w - 20, 300, INK, 2.5); x0, y0 = 120, 66
    b += DOT(x0, y0, 5, '#8e5b2a', '#c39b6a')
    b += L(x0, y0 + 6, x0, 298, INK, 2, '6 4') + T(x0 + 10, 250, '(1)', 15, 'start', INK, 'bold')
    pts = [(x0 + 330 * (i / 40), y0 + 232 * (i / 40) ** 2) for i in range(41)]
    b += f'<polyline points="{" ".join(f"{a:.1f},{c:.1f}" for a, c in pts)}" fill="none" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="7 5"/>' + T(x0 + 310, 250, '(2)', 15, 'end', ORANGE, 'bold')
    pts = [(x0 - 90 * (i / 40), y0 + 232 * (i / 40) ** 2) for i in range(41)]
    b += f'<polyline points="{" ".join(f"{a:.1f},{c:.1f}" for a, c in pts)}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="2 4"/>' + T(x0 - 96, 250, '(3)', 15, 'end', MUTED, 'bold')
    save('c6l1-o17-plane.svg', svg(w, h, b))

    # حافلة تتحرك بسرعة ثابتة وراكب يقذف كرة رأسيًا إلى أعلى
    w, h = 520, 260; b = L(20, 225, w - 20, 225, INK, 2.5)
    b += RECT(90, 110, 230, 95, INK, '#f6e7b4') + f'<circle cx="135" cy="210" r="15" fill="#555"/><circle cx="275" cy="210" r="15" fill="#555"/>'
    for xx in (110, 165, 220, 270): b += RECT(xx, 125, 36, 30, MUTED, '#dbe9f6', 1.2)
    b += DOT(205, 170, 8, '#b9770e', '#f4d03f') + ARROW(205, 160, 205, 118, C_VEL, 2.4) + T(205, 100, 'سرعة الكرة بالنسبة إلى الراكب', 12, 'middle', C_VEL)
    b += ARROW(330, 150, 410, 150, C_VEL, 2.6) + V(414, 156, 'v', C_VEL, 16, 'start') + T(370, 175, 'سرعة الحافلة', 12, 'middle', C_VEL)
    b += T(455, 248, 'مراقب على الرصيف', 12, 'middle', INK) + f'<circle cx="470" cy="160" r="7" fill="none" stroke="{INK}" stroke-width="1.5"/>' + L(470, 167, 470, 195, INK, 1.5) + L(470, 195, 462, 205, INK, 1.5) + L(470, 195, 478, 205, INK, 1.5)
    save('c6l1-o17-bus.svg', svg(w, h, b))


if __name__ == '__main__':
    o10(); o11(); o12(); o13(); o14(); o15(); o16(); o17()
