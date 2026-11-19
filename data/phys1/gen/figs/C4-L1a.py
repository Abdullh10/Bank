import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-1 (القوة والحركة) — الأهداف O01–O13
import math

XL = 'الزمن (s)'; VL = 'السرعة المتجهة (m/s)'; AL = 'التسارع (m/s²)'; FL = 'القوة (N)'


def plus_x(x, y, length=70, label='+x'):
    """سهم الاتجاه الموجب الأفقي (إلى اليمين)."""
    return ARROW(x, y, x + length, y, INK, 2) + T(x + length + 6, y + 5, label, 15, 'start', italic=True)


def plus_y(x, y, length=60, label='+y'):
    return ARROW(x, y, x, y - length, INK, 2) + T(x + 8, y - length + 4, label, 15, 'start', italic=True)


def ground(x1, x2, y):
    b = L(x1, y, x2, y, INK, 2)
    for x in range(int(x1) + 6, int(x2), 14): b += L(x, y, x - 8, y + 9, MUTED, 1.2)
    return b


def force(x1, y1, x2, y2, sym, val=None, lx=None, ly=None, anchor='middle'):
    """سهم قوة أزرق يبدأ من الجسم، مع رمز عريض مائل وقيمة اختيارية بخط قائم."""
    b = ARROW(x1, y1, x2, y2, C_FORCE, 3)
    lx = lx if lx is not None else (x1 + x2) / 2
    ly = ly if ly is not None else (y1 + y2) / 2 - 12
    if val is None:
        b += V(lx, ly, sym, C_FORCE, 17, anchor)
    else:
        # الرمز ثم «= القيمة» في سطر واحد
        b += V(lx - 4, ly, sym, C_FORCE, 17, 'end') + T(lx, ly, '= ' + val, 15, 'start', C_FORCE)
    return b


def dashed_circle(cx, cy, rx, ry=None):
    ry = ry or rx
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 5"/>'


def ball(cx, cy, r=26, fill='#b9c3e6'):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="2"/>'


# ================= O01 =================
def o01_two_arrows():
    w, h = 560, 200; b = ''
    b += ground(20, 540, 150)
    # الصندوق A مع سهم قصير إلى اليمين، والصندوق B مع سهم أطول إلى اليسار
    b += RECT(80, 100, 70, 50) + T(115, 132, 'A', 18, weight='bold')
    b += force(150, 125, 215, 125, 'F_1', lx=183, ly=112)
    b += RECT(400, 100, 70, 50) + T(435, 132, 'B', 18, weight='bold')
    b += force(400, 125, 280, 125, 'F_2', lx=340, ly=112)
    save('c4l1-o01-two-arrows.svg', svg(w, h, b))


# ================= O02 =================
def o02_motion_rows():
    rows = [
        {'label': 'A', 'xs': [60, 130, 200, 270, 340, 410], 'vel': True},
        {'label': 'B', 'xs': [60, 84, 118, 162, 226, 316], 'vel': True},
        {'label': 'C', 'xs': [60, 110, 160, 210, 260, 310], 'vel': True},
        {'label': 'D', 'xs': [250]},
    ]
    motion_diagram('c4l1-o02-motion-rows.svg', rows, w=520, row_h=72)


def o02_vt():
    graph('c4l1-o02-vt.svg', [{'pts': [(0, 4), (2, 4), (5, 10), (8, 10)], 'color': C_VEL}],
          (0, 8), (0, 12), XL, VL, 1, 2)


def o02_kick():
    w, h = 420, 260; b = ''
    cx, cy = 200, 150
    b += ball(cx, cy, 20, '#eceff4')
    b += ARROW(cx + 22, cy, cx + 130, cy, C_VEL, 3) + V(cx + 140, cy + 6, 'v', C_VEL, 18, 'start')
    b += force(cx, cy - 22, cx, cy - 110, 'F', lx=cx + 18, ly=cy - 80, anchor='start')
    b += plus_x(30, 235) + plus_y(30, 230)
    save('c4l1-o02-kick.svg', svg(w, h, b))


# ================= O03 =================
def table(x, y, w=260):
    b = RECT(x, y, w, 14, INK, '#c9a97a') + RECT(x + 14, y + 14, 14, 110, INK, '#c9a97a') + RECT(x + w - 28, y + 14, 14, 110, INK, '#c9a97a')
    return b


def hand(x, y, facing='right'):
    """يد مبسطة: مستطيل مستدير الأطراف مع ذراع."""
    if facing == 'right':
        return (f'<rect x="{x - 70}" y="{y - 9}" width="60" height="18" rx="8" fill="#e8c4a0" stroke="{INK}" stroke-width="1.5"/>'
                f'<rect x="{x - 18}" y="{y - 14}" width="22" height="28" rx="9" fill="#e8c4a0" stroke="{INK}" stroke-width="1.5"/>')
    return (f'<rect x="{x + 10}" y="{y - 9}" width="60" height="18" rx="8" fill="#e8c4a0" stroke="{INK}" stroke-width="1.5"/>'
            f'<rect x="{x - 4}" y="{y - 14}" width="22" height="28" rx="9" fill="#e8c4a0" stroke="{INK}" stroke-width="1.5"/>')


def o03_book_hand():
    w, h = 460, 270; b = ''
    b += table(110, 130, 280) + ground(20, 440, 254)
    b += RECT(200, 106, 110, 24, INK, '#7fa7d6')          # الكتاب
    b += hand(198, 118, 'right')
    b += dashed_circle(255, 118, 78, 34)
    b += L(300, 86, 340, 50, MUTED, 1.2) + T(345, 46, 'النظام', 15, 'start')
    b += T(150, 82, 'اليد', 14, color=MUTED)
    b += T(250, 170, 'الطاولة', 14, color=MUTED)
    save('c4l1-o03-book-hand.svg', svg(w, h, b))


def o03_ball_rope():
    w, h = 360, 300; b = ''
    b += RECT(100, 20, 160, 16, INK, '#c8ccd4')
    b += L(180, 36, 180, 150, '#8a6d3b', 3)
    b += ball(180, 176, 26)
    b += dashed_circle(180, 176, 44)
    b += T(250, 100, 'الحبل', 14, color=MUTED) + L(225, 100, 186, 100, MUTED, 1)
    save('c4l1-o03-ball-rope.svg', svg(w, h, b))


def o03_stack():
    w, h = 420, 260; b = ''
    b += table(80, 150, 260) + ground(20, 400, 274)
    b += RECT(170, 100, 90, 50, INK, '#e7d7b7') + T(215, 131, 'P', 18, weight='bold')
    b += RECT(185, 60, 60, 40, INK, '#cfe0f2') + T(215, 86, 'Q', 18, weight='bold')
    b += dashed_circle(215, 80, 48, 30)
    save('c4l1-o03-stack.svg', svg(w, 290, b))


# ================= O04 =================
def o04_ball_hand_fbd():
    w, h = 300, 300; b = ''
    cx, cy = 150, 150
    b += DOT(cx, cy, 7)
    b += force(cx, cy, cx, cy - 100, 'F_1', lx=cx + 14, ly=cy - 70, anchor='start')
    b += force(cx, cy, cx, cy + 100, 'F_2', lx=cx + 14, ly=cy + 80, anchor='start')
    b += plus_y(50, 120)
    save('c4l1-o04-ball-hand-fbd.svg', svg(w, h, b))


def o04_cart_rope():
    w, h = 520, 210; b = ''
    b += ground(20, 500, 160)
    b += RECT(150, 100, 110, 46, INK, '#dfe6ef')
    b += f'<circle cx="175" cy="150" r="10" fill="#fff" stroke="{INK}" stroke-width="2"/><circle cx="235" cy="150" r="10" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    b += L(260, 123, 380, 123, '#8a6d3b', 3)
    b += T(330, 110, 'حبل', 14, color=MUTED)
    # مغناطيس أمام العربة على مسافة (لا يلامسها)
    b += RECT(40, 105, 30, 40, INK, '#d9534f') + RECT(70, 105, 30, 40, INK, '#5b7dbd')
    b += T(55, 131, 'N', 14, color='#fff', weight='bold') + T(85, 131, 'S', 14, color='#fff', weight='bold')
    b += T(70, 95, 'مغناطيس', 13, color=MUTED)
    save('c4l1-o04-cart-rope.svg', svg(w, h, b))


# ================= O05 =================
def o05_magnet():
    w, h = 460, 200; b = ''
    b += RECT(40, 80, 60, 50, INK, '#d9534f') + RECT(100, 80, 60, 50, INK, '#5b7dbd')
    b += T(70, 111, 'N', 16, color='#fff', weight='bold') + T(130, 111, 'S', 16, color='#fff', weight='bold')
    # كرة حديدية صغيرة على مسافة
    b += ball(330, 105, 16, '#a7adb7')
    b += force(314, 105, 240, 105, 'F', lx=275, ly=92)
    b += L(162, 160, 312, 160, MUTED, 1.2, '5 4') + T(237, 182, 'مسافة (لا تلامس)', 13, color=MUTED)
    save('c4l1-o05-magnet.svg', svg(w, h, b))


def o05_fall_fbd():
    w, h = 300, 300; b = ''
    cx, cy = 150, 120
    b += DOT(cx, cy, 7)
    b += force(cx, cy, cx, cy + 120, 'F', lx=cx + 14, ly=cy + 90, anchor='start')
    b += plus_y(60, 120)
    save('c4l1-o05-fall-fbd.svg', svg(w, h, b))


# ================= O06 =================
def o06_aF_line():
    graph('c4l1-o06-aF-line.svg', [{'pts': [(0, 0), (4, 1.6)], 'color': INK}], (0, 4), (0, 1.6), FL, AL, 1, 0.4,
          marks=[(1, 0.4, ''), (2, 0.8, ''), (3, 1.2, ''), (4, 1.6, '')])


def o06_four_graphs():
    pw, ph = 260, 200; b = ''
    shapes = {
        'A': [(0, 0), (4, 3.2)],
        'B': [(0, 2), (4, 2)],
        'C': [(0, 3.2), (4, 0)],
        'D': [(x / 4, 3.2 * math.sqrt(x / 16)) for x in range(0, 17)],
    }
    for k, (lab, pts) in enumerate(shapes.items()):
        X0, Y0 = (k % 2) * pw, (k // 2) * ph
        L0, R0, T0, B0 = X0 + 40, X0 + pw - 20, Y0 + 30, Y0 + ph - 34
        X = lambda x: L0 + x / 4 * (R0 - L0)
        Y = lambda y: B0 - y / 4 * (B0 - T0)
        b += f'<rect x="{X0 + 4}" y="{Y0 + 4}" width="{pw - 8}" height="{ph - 8}" fill="#fff" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
        b += ARROW(L0, B0, R0 + 8, B0, INK, 1.6, 8) + ARROW(L0, B0, L0, T0 - 12, INK, 1.6, 8)
        b += T(L0 - 4, B0 + 16, '0', 12, color=MUTED)
        b += T((L0 + R0) / 2, B0 + 24, 'القوة', 13, color=MUTED) + T(L0 - 22, (T0 + B0) / 2, 'التسارع', 13, color=MUTED, rotate=-90)
        p = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
        b += f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        b += T(X0 + pw - 22, Y0 + 26, lab, 18, 'end', INK, 'bold')
    save('c4l1-o06-four-graphs.svg', svg(2 * pw, 2 * ph, b))


def o06_vt_bands():
    graph('c4l1-o06-vt-bands.svg', [
        {'pts': [(0, 0), (4, 1.6)], 'color': C_VEL, 'label': 'A', 'at': (4, 1.6)},
        {'pts': [(0, 0), (4, 3.2)], 'color': C_VEL, 'label': 'B', 'at': (4, 3.2), 'dash': '8 5'},
    ], (0, 4.5), (0, 3.6), XL, VL, 0.5, 0.4)


# ================= O08 =================
def o08_same_dir():
    w, h = 520, 210; cx, cy = 200, 100; b = ''
    b += RECT(cx - 26, cy - 22, 52, 44)
    b += force(cx + 26, cy - 10, cx + 26 + 150, cy - 10, 'F_1', '120 N', lx=cx + 95, ly=cy - 22)
    b += force(cx + 26, cy + 12, cx + 26 + 100, cy + 12, 'F_2', '80 N', lx=cx + 80, ly=cy + 38)
    b += plus_x(30, h - 22)
    save('c4l1-o08-same-dir.svg', svg(w, h, b))


def o08_opposite():
    w, h = 560, 200; cx, cy = 280, 95; b = ''
    b += RECT(cx - 26, cy - 22, 52, 44)
    b += force(cx + 26, cy, cx + 26 + 165, cy, 'F_1', '150 N', lx=cx + 105, ly=cy - 14)
    b += force(cx - 26, cy, cx - 26 - 99, cy, 'F_2', '90 N', lx=cx - 100, ly=cy - 14)
    b += plus_x(30, h - 22)
    save('c4l1-o08-opposite.svg', svg(w, h, b))


def o08_three():
    w, h = 580, 220; cx, cy = 300, 100; b = ''
    b += RECT(cx - 26, cy - 22, 52, 44)
    b += force(cx + 26, cy, cx + 26 + 154, cy, 'F_3', '70 N', lx=cx + 110, ly=cy - 14)
    b += force(cx - 26, cy - 10, cx - 26 - 88, cy - 10, 'F_1', '40 N', lx=cx - 75, ly=cy - 22)
    b += force(cx - 26, cy + 12, cx - 26 - 55, cy + 12, 'F_2', '25 N', lx=cx - 60, ly=cy + 38)
    b += plus_x(30, h - 22)
    save('c4l1-o08-three.svg', svg(w, h, b))


def o08_tug():
    w, h = 600, 220; cx, cy = 300, 100; b = ''
    b += DOT(cx, cy, 7)
    b += force(cx, cy - 10, cx + 130, cy - 10, 'F_1', '260 N', lx=cx + 80, ly=cy - 22)
    b += force(cx, cy + 12, cx + 100, cy + 12, 'F_2', '200 N', lx=cx + 60, ly=cy + 38)
    b += force(cx, cy - 10, cx - 140, cy - 10, 'F_3', '280 N', lx=cx - 90, ly=cy - 22)
    b += force(cx, cy + 12, cx - 90, cy + 12, 'F_4', '?', lx=cx - 55, ly=cy + 38)
    b += plus_x(30, h - 22)
    save('c4l1-o08-tug.svg', svg(w, h, b))


# ================= O10 =================
def o10_fbd_box():
    w, h = 520, 200; cx, cy = 260, 95; b = ''
    b += RECT(cx - 30, cy - 24, 60, 48) + T(cx, cy + 6, '8.0 kg', 13)
    b += force(cx + 30, cy, cx + 30 + 150, cy, 'F_1', '60 N', lx=cx + 105, ly=cy - 14)
    b += force(cx - 30, cy, cx - 30 - 50, cy, 'F_2', '20 N', lx=cx - 112, ly=cy - 14)
    b += plus_x(30, h - 22)
    save('c4l1-o10-fbd-box.svg', svg(w, h, b))


def o10_vt():
    graph('c4l1-o10-vt.svg', [{'pts': [(0, 0), (6, 12)], 'color': C_VEL}], (0, 6), (0, 14), XL, VL, 1, 2)


def o10_find_mass():
    w, h = 520, 200; cx, cy = 260, 95; b = ''
    b += RECT(cx - 30, cy - 24, 60, 48) + T(cx, cy + 6, 'm = ?', 13, italic=True)
    b += force(cx + 30, cy, cx + 30 + 120, cy, 'F_1', '45 N', lx=cx + 90, ly=cy - 14)
    b += force(cx - 30, cy, cx - 30 - 40, cy, 'F_2', '15 N', lx=cx - 106, ly=cy - 14)
    b += ARROW(cx - 20, cy - 56, cx + 30, cy - 56, C_ACC, 2.5) + V(cx + 44, cy - 51, 'a', C_ACC, 16, 'start') + T(cx + 60, cy - 51, '= 2.5 m/s²', 14, 'start', C_ACC)
    b += plus_x(30, h - 22)
    save('c4l1-o10-find-mass.svg', svg(w, h, b))


def o10_brake_vt():
    graph('c4l1-o10-brake-vt.svg', [{'pts': [(0, 20), (4, 8)], 'color': C_VEL}], (0, 5), (0, 24), XL, VL, 1, 4)


# ================= O11 =================
def o11_puck():
    motion_diagram('c4l1-o11-puck.svg', [{'xs': [60, 130, 200, 270, 340, 410, 480], 'vel': True}], w=540, row_h=70, axis_label='d', origin=60)


def o11_balanced():
    fbd('c4l1-o11-balanced.svg', [
        {'angle': 90, 'length': 80, 'label': 'F_1'}, {'angle': -90, 'length': 80, 'label': 'F_2'},
        {'angle': 0, 'length': 70, 'label': 'F_3'}, {'angle': 180, 'length': 70, 'label': 'F_4'}],
        w=360, h=320, body='dot',
        extra=plus_x(24, 300, 60) + plus_y(24, 290, 60))


def o11_rows():
    rows = [
        {'label': 'A', 'xs': [60, 150, 225, 285, 330, 360], 'vel': True},
        {'label': 'B', 'xs': [60, 120, 180, 240, 300, 360], 'vel': True},
        {'label': 'C', 'xs': [60, 82, 112, 152, 206, 276], 'vel': True},
    ]
    motion_diagram('c4l1-o11-rows.svg', rows, w=460, row_h=72)


# ================= O13 =================
def o13_bus_ball():
    w, h = 560, 260; b = ''
    b += ground(20, 540, 200)
    b += f'<rect x="100" y="60" width="330" height="120" rx="14" fill="#f5efe0" stroke="{INK}" stroke-width="2"/>'
    for x in (130, 200, 270, 340): b += RECT(x, 78, 50, 36, INK, '#dbe9f6', 1.5)
    b += f'<circle cx="160" cy="190" r="16" fill="#fff" stroke="{INK}" stroke-width="2"/><circle cx="370" cy="190" r="16" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    b += ball(265, 165, 12, '#e07a5f')
    b += T(440, 120, 'الأمام', 13, 'start', MUTED) + ARROW(440, 130, 490, 130, MUTED, 1.6, 8)
    b += ARROW(150, 36, 270, 36, C_VEL, 3) + V(282, 42, 'v', C_VEL, 18, 'start')
    b += ARROW(480, 36, 400, 36, C_ACC, 3) + V(390, 42, 'a', C_ACC, 18, 'end')
    save('c4l1-o13-bus-ball.svg', svg(w, h, b))


def o13_car_pendulum():
    w, h = 520, 260; b = ''
    b += ground(20, 500, 210)
    b += f'<rect x="110" y="70" width="300" height="120" rx="16" fill="#eef2f8" stroke="{INK}" stroke-width="2"/>'
    b += f'<circle cx="170" cy="198" r="16" fill="#fff" stroke="{INK}" stroke-width="2"/><circle cx="350" cy="198" r="16" fill="#fff" stroke="{INK}" stroke-width="2"/>'
    b += L(260, 70, 260, 140, MUTED, 2) + ball(260, 150, 10, '#e07a5f')
    b += ARROW(200, 40, 300, 40, C_ACC, 3) + V(312, 46, 'a', C_ACC, 18, 'start')
    b += T(440, 140, 'الأمام', 13, 'start', MUTED) + ARROW(440, 150, 490, 150, MUTED, 1.6, 8)
    save('c4l1-o13-car-pendulum.svg', svg(w, h, b))


def o13_coin_card():
    w, h = 460, 260; b = ''
    b += ground(20, 440, 230)
    # كوب
    b += f'<path d="M 170 130 L 185 230 L 275 230 L 290 130 Z" fill="#e6f0fa" stroke="{INK}" stroke-width="2"/>'
    b += RECT(140, 122, 180, 8, INK, '#f0d9a8', 1.5)           # البطاقة
    b += f'<ellipse cx="230" cy="114" rx="20" ry="7" fill="#d4a017" stroke="{INK}" stroke-width="1.5"/>'  # قطعة النقود
    b += force(320, 126, 410, 126, 'F', lx=365, ly=112)
    b += T(110, 112, 'بطاقة', 13, color=MUTED) + T(230, 92, 'قطعة نقود', 13, color=MUTED)
    save('c4l1-o13-coin-card.svg', svg(w, h, b))


if __name__ == '__main__':
    only = sys.argv[1:]
    for fn in [o01_two_arrows, o02_motion_rows, o02_vt, o02_kick, o03_book_hand, o03_ball_rope, o03_stack,
               o04_ball_hand_fbd, o04_cart_rope, o05_magnet, o05_fall_fbd, o06_aF_line, o06_four_graphs, o06_vt_bands,
               o08_same_dir, o08_opposite, o08_three, o08_tug, o10_fbd_box, o10_vt, o10_find_mass, o10_brake_vt,
               o11_puck, o11_balanced, o11_rows, o13_bus_ball, o13_car_pendulum, o13_coin_card]:
        if not only or fn.__name__ in only: fn()
