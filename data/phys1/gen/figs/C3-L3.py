import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-3 (السقوط الحر) — الأهداف O01–O08
import math

XL = 'الزمن (s)'; VL = 'السرعة المتجهة (m/s)'; DL = 'الموقع (m)'

def plus_arrow(x, y, up=True, length=70, label='+y'):
    """سهم الاتجاه الموجب الرأسي."""
    if up: return ARROW(x, y, x, y - length, INK, 2) + T(x + 8, y - length + 4, label, 15, 'start', italic=True)
    return ARROW(x, y, x, y + length, INK, 2) + T(x + 8, y + length + 2, label, 15, 'start', italic=True)

def ground(x1, x2, y):
    b = L(x1, y, x2, y, INK, 2)
    for x in range(int(x1) + 6, int(x2), 14): b += L(x, y, x - 8, y + 9, MUTED, 1.2)
    return b

# ================= O01: جسمان يسقطان (A سقوط حر، B مسافات ثابتة في آخره) =================
def two_drops():
    w, h = 360, 400; b = ''; top = 40; k = 6.5
    ya = [top + k * (n * n - 1) for n in range(1, 8)]    # المسافات تزداد بانتظام
    yb = [top + k * (n * n - 1) for n in range(1, 5)]
    for n in range(5, 10): yb.append(yb[-1] + 60)        # بعد ذلك مسافات متساوية
    yb = [y for y in yb if y <= top + 330]
    for x, ys, lab in ((110, ya, 'A'), (250, yb, 'B')):
        for y in ys: b += DOT(x, y, 6, INK)
        b += T(x, 24, lab, 18, weight='bold')
    b += ground(40, 330, top + 345)
    save('c3l3-o01-two-drops.svg', svg(w, h, b))

# ================= O02: (v–t) لحجر يسقط، الموجب لأسفل =================
def o02_vt():
    graph('c3l3-o02-vt-stone.svg', [{'pts': [(0, 0), (1, 9.8), (2, 19.6), (3, 29.4)], 'color': C_VEL, 'dots': True}],
          (0, 3.5), (0, 39.2), XL, VL, 0.5, 9.8)

# ================= O03 =================
def o03_axis_up():
    w, h = 300, 300; b = ''
    b += DOT(150, 90, 14, INK, '#d6dbe4')
    b += ARROW(150, 112, 150, 180, C_VEL, 3) + V(166, 160, 'v', C_VEL, 18, 'start')
    b += ground(40, 260, 260)
    b += plus_arrow(60, 200, True, 90)
    save('c3l3-o03-axis-up.svg', svg(w, h, b))

def o03_egg():
    w, h = 300, 400; b = ''; top = 40
    ys = [top + 9 * n * n for n in range(2, 7)]
    for y in ys: b += f'<ellipse cx="150" cy="{y}" rx="11" ry="14" fill="#fbf3dc" stroke="{INK}" stroke-width="1.5"/>'
    b += plus_arrow(60, 60, False, 110)
    save('c3l3-o03-egg-strobe.svg', svg(w, h, b))

def o03_vt():
    graph('c3l3-o03-vt-updown.svg', [{'pts': [(0, 14.7), (3, -14.7)], 'color': C_VEL}],
          (0, 3.5), (-19.6, 19.6), XL, VL, 0.5, 4.9)

# ================= O04 =================
def o04_motion():
    w, h = 300, 420; b = ''; top = 40; k = 6.5
    ys = [top + k * n * n for n in range(1, 8)]
    for i, y in enumerate(ys):
        b += DOT(130, y, 6, INK)
    for i in range(0, 6):
        L_ = 10 * (i + 1)   # أطوال متزايدة بمقادير متساوية
        b += ARROW(165, ys[i], 165, ys[i] + L_, C_VEL, 2.4, 8)
    b += V(190, ys[3] + 12, 'v', C_VEL, 18, 'start')
    save('c3l3-o04-motion.svg', svg(w, h, b))

def mini(X0, Y0, pw, ph, pts, xr, yr, yt, title):
    L0, R0, T0, B0 = X0 + 62, X0 + pw - 18, Y0 + 34, Y0 + ph - 30
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    b = f'<rect x="{X0 + 3}" y="{Y0 + 3}" width="{pw - 6}" height="{ph - 6}" fill="#fff" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
    for y in yt: b += L(L0, Y(y), R0, Y(y), GRID, 1)
    b += ARROW(L0, Y(0), R0 + 8, Y(0), INK, 1.6, 8) + ARROW(L0, B0, L0, T0 - 10, INK, 1.6, 8)
    for y in yt: b += L(L0 - 4, Y(y), L0, Y(y), INK, 1.2) + T(L0 - 7, Y(y) + 4, fmt(y), 12, 'end', MUTED)
    b += T(R0 + 4, Y(0) + 18, 'الزمن (s)', 12, 'end', MUTED) + T(L0 + 6, T0 - 14, 'التسارع (m/s²)', 12, 'start', MUTED)
    p = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
    b += f'<polyline points="{p}" fill="none" stroke="{C_ACC}" stroke-width="3" stroke-linejoin="round"/>'
    b += T(X0 + pw - 16, Y0 + 24, title, 16, 'end', INK, 'bold')
    return b

def o04_panels():
    pw, ph = 280, 200; b = ''
    items = [('A', [(0, 9.8), (3, 9.8)]), ('B', [(0, 0), (3, 9.8)]), ('C', [(0, 0), (3, 0)]), ('D', [(0, -9.8), (3, -9.8)])]
    for k, (t, pts) in enumerate(items):
        b += mini((k % 2) * pw, (k // 2) * ph, pw, ph, pts, (0, 3.3), (-12, 12), [-9.8, 0, 9.8], t)
    save('c3l3-o04-at-panels.svg', svg(2 * pw, 2 * ph, b))

# ================= O05: أنبوب فيه هواء: قطعة نقدية وريشة =================
def o05_tube():
    w, h = 340, 420; b = ''; top = 50
    b += f'<rect x="90" y="30" width="160" height="350" rx="16" fill="#f4f8fc" stroke="{INK}" stroke-width="2"/>'
    coin = [top + 8 * (n * n - 1) for n in range(1, 8)]          # 50..374 → نقصرها
    coin = [y for y in coin if y <= 360]
    feather = [top + 20 * n for n in range(6)]          # مسافات صغيرة متقاربة
    for y in coin: b += f'<ellipse cx="135" cy="{y}" rx="12" ry="4.5" fill="#d9a441" stroke="{INK}" stroke-width="1.3"/>'
    for y in feather: b += f'<path d="M 195 {y} q 12 -5 24 0 q -12 5 -24 0 z" fill="#ffffff" stroke="{INK}" stroke-width="1.3"/>' + L(192, y, 222, y, INK, 1)
    b += T(135, 404, 'قطعة نقدية', 14) + T(209, 404, 'ريشة', 14)
    b += T(170, 20, 'أنبوب فيه هواء', 14, color=MUTED, weight='bold')
    save('c3l3-o05-tube.svg', svg(w, h, b))

# ================= O06: كرة تُقذف لأسفل من نافذة =================
def o06_window():
    w, h = 380, 330; b = ''
    b += RECT(40, 30, 150, 260, INK, '#efe9dd')
    b += RECT(130, 70, 60, 50, INK, '#dbe9f6')
    b += DOT(214, 95, 11, INK, '#d6dbe4')
    b += ARROW(214, 110, 214, 160, C_VEL, 3) + V(230, 145, 'v_i', C_VEL, 18, 'start')
    b += ground(20, 360, 290)
    b += L(300, 95, 300, 290, INK, 1.5) + L(290, 95, 310, 95, INK, 1.5) + L(290, 290, 310, 290, INK, 1.5)
    b += L(225, 95, 290, 95, MUTED, 1, '4 4')
    b += T(312, 200, '2.5 m', 15, 'start')
    b += T(115, 315, 'رصيف المشاة', 14, color=MUTED)
    save('c3l3-o06-window.svg', svg(w, h, b))

# ================= O07 =================
def o07_vt():
    graph('c3l3-o07-vt-top.svg', [{'pts': [(0, 24.5), (5, -24.5)], 'color': C_VEL}],
          (0, 5.5), (-29.4, 29.4), XL, VL, 0.5, 4.9, h=400)

def o07_path():
    w, h = 340, 380; b = ''
    x1, x2, ytop, ybot = 140, 200, 70, 320
    b += f'<path d="M {x1} {ybot} L {x1} {ytop + 20} Q {x1} {ytop} {(x1 + x2) / 2} {ytop} Q {x2} {ytop} {x2} {ytop + 20} L {x2} {ybot}" fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-dasharray="6 5"/>'
    b += DOT(x1, 210, 7, INK) + T(x1 - 16, 215, '1', 16, 'end', weight='bold')
    b += DOT((x1 + x2) / 2, ytop, 7, INK) + T((x1 + x2) / 2, ytop - 16, '2', 16, weight='bold')
    b += DOT(x2, 210, 7, INK) + T(x2 + 16, 215, '3', 16, 'start', weight='bold')
    b += T(x1 - 16, 240, 'صاعدة', 13, 'end', MUTED) + T(x2 + 16, 240, 'هابطة', 13, 'start', MUTED)
    b += ground(40, 300, ybot + 10)
    b += plus_arrow(60, 200, True, 80)
    save('c3l3-o07-path.svg', svg(w, h, b))

def o07_dt():
    pts = [(t / 20, 19.6 * t / 20 - 4.9 * (t / 20) ** 2) for t in range(0, 81)]
    graph('c3l3-o07-dt.svg', [{'pts': pts, 'color': C_DISP}], (0, 4.5), (0, 24), XL, DL, 0.5, 4,
          marks=[(2.0, 19.6, '(2.0, 19.6)')])

def o07_essay_vt():
    graph('c3l3-o07-essay-vt.svg', [{'pts': [(0, 19.6), (4, -19.6)], 'color': C_VEL}],
          (0, 4.5), (-24.5, 24.5), XL, VL, 0.5, 4.9, h=400)

# ================= O08 =================
YL8 = ' '
def ylab8(h=360):
    # عنوان المحور الرأسي: d_f متجه (عريض مائل)، t_f قياسي (مائل)، الوحدة قائمة
    cy = (18 + h - 52) / 2
    sub = lambda c: f'<tspan dy="0.3em" font-size="10" font-style="italic">{c}</tspan><tspan dy="-0.3em"></tspan>'
    return (f'<text x="20" y="{cy:.1f}" text-anchor="middle" font-size="14" fill="{INK}" {MATHFONT} transform="rotate(-90 20 {cy:.1f})">'
            f'<tspan font-weight="bold" font-style="italic">d</tspan>{sub("f")}<tspan> / </tspan><tspan font-style="italic">t</tspan>{sub("f")}<tspan> (m/s)</tspan></text>')
def o08_graph1():
    data = [(0.10, 1.00), (0.15, 1.20), (0.20, 1.48), (0.25, 1.73), (0.30, 1.94), (0.35, 2.21)]
    X, Y = graph('c3l3-o08-fit1.svg', [{'pts': [(0, 0.50), (0.40, 2.44)], 'color': INK, 'w': 2.5}], (0, 0.45), (0, 3.0), XL, YL8, 0.05, 0.5,
                 marks=[(0, 0.50, '(0, 0.50)'), (0.40, 2.44, '')],
                 extra='')
    # إعادة الرسم مع النقاط المقيسة وتسمية النقطة الثانية
    extra = ''.join(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="#fff" stroke="{INK}" stroke-width="1.6"/>' for x, y in data)
    extra += T(X(0.40) - 8, Y(2.44) - 12, '(0.40, 2.44)', 14, 'end')
    graph('c3l3-o08-fit1.svg', [{'pts': [(0, 0.50), (0.40, 2.44)], 'color': INK, 'w': 2.5}], (0, 0.45), (0, 3.0), XL, YL8, 0.05, 0.5,
          marks=[(0, 0.50, ''), (0.40, 2.44, '')], extra=extra + T(X(0) + 12, Y(0.50) + 20, '(0, 0.50)', 14, 'start') + ylab8())

def o08_tape():
    w, h = 640, 135; b = ''
    b += f'<rect x="10" y="40" width="620" height="50" fill="#fffdf6" stroke="{INK}" stroke-width="1.5"/>'
    gaps = [14, 24, 34, 44, 54, 64, 40, 24, 16]
    x = 40; xs = [x]
    for g_ in gaps: x += g_ * 1.42; xs.append(x)
    for i, x in enumerate(xs):
        b += DOT(x, 65, 3.5, INK) + T(x, 115, str(i), 14)
    save('c3l3-o08-tape.svg', svg(w, h, b))

def o08_essay_graph():
    data = [(0.10, 0.80), (0.20, 1.23), (0.30, 1.76), (0.40, 2.20), (0.50, 2.69)]
    X, Y = graph('c3l3-o08-fit2.svg', [{'pts': [(0, 0.30), (0.50, 2.70)], 'color': INK, 'w': 2.5}], (0, 0.55), (0, 3.0), XL, YL8, 0.05, 0.3)
    extra = ''.join(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="#fff" stroke="{INK}" stroke-width="1.6"/>' for x, y in data)
    graph('c3l3-o08-fit2.svg', [{'pts': [(0, 0.30), (0.50, 2.70)], 'color': INK, 'w': 2.5}], (0, 0.55), (0, 3.0), XL, YL8, 0.05, 0.3, extra=extra + ylab8())

if __name__ == '__main__':
    two_drops(); o02_vt(); o03_axis_up(); o03_egg(); o03_vt(); o04_motion(); o04_panels(); o05_tube(); o06_window()
    o07_vt(); o07_path(); o07_dt(); o07_essay_vt(); o08_graph1(); o08_tape(); o08_essay_graph()
