import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-2 (استخدام قوانين نيوتن) — الأهداف O01–O15
import math

XL = 'الزمن (s)'; VL = 'السرعة المتجهة (m/s)'


def plus_arrow(x, y, length=80, label='+y'):
    """سهم الاتجاه الموجب الرأسي إلى أعلى."""
    return ARROW(x, y, x, y - length, INK, 2) + T(x + 8, y - length + 6, label, 15, 'start', italic=True)


def person(cx, feet_y, hgt=150, col='#c9b79c'):
    """شخص مبسط يقف وقدماه عند feet_y."""
    head_r = hgt * 0.09; b = ''
    top = feet_y - hgt
    b += f'<circle cx="{cx}" cy="{top + head_r:.1f}" r="{head_r:.1f}" fill="#e8cfae" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<rect x="{cx - hgt * 0.13:.1f}" y="{top + 2 * head_r + 3:.1f}" width="{hgt * 0.26:.1f}" height="{hgt * 0.40:.1f}" rx="8" fill="{col}" stroke="{INK}" stroke-width="1.5"/>'
    leg_top = top + 2 * head_r + 3 + hgt * 0.40
    b += L(cx - hgt * 0.06, leg_top, cx - hgt * 0.07, feet_y, INK, 5) + L(cx + hgt * 0.06, leg_top, cx + hgt * 0.07, feet_y, INK, 5)
    return b


def scale_box(cx, y, w=70, h=12):
    return RECT(cx - w / 2, y, w, h, INK, '#dfe5ee', 1.6) + L(cx - 12, y + h / 2, cx + 12, y + h / 2, MUTED, 1.2)


def elevator(name, v=None, a=None, a_zero=False, w=360, h=330):
    """مصعد فيه شخص يقف على ميزان. v / a: 'up' أو 'down' أو None. a_zero يكتب a = 0."""
    b = ''; x0, y0, cw, ch = 110, 30, 150, 260
    b += RECT(x0, y0, cw, ch, INK, '#f1f3f7', 2.5)
    b += L(x0 + cw / 2, 8, x0 + cw / 2, y0, MUTED, 2)  # الحبل
    floor = y0 + ch - 8
    b += scale_box(x0 + cw / 2, floor - 12)
    b += person(x0 + cw / 2, floor - 12, 160)
    b += plus_arrow(60, 230, 110)
    # متجها السرعة والتسارع خارج المصعد يمينًا
    cy = 150
    if v:
        s = -1 if v == 'up' else 1
        b += ARROW(295, cy - 45 * s, 295, cy + 45 * s, C_VEL, 3) + V(312, cy + 6, 'v', C_VEL, 18, 'start')
    if a:
        s = -1 if a == 'up' else 1
        b += ARROW(335, cy - 35 * s, 335, cy + 35 * s, C_ACC, 3) + V(345, cy + 6, 'a', C_ACC, 18, 'start')
    if a_zero:
        b += f'<text x="318" y="{cy + 75}" text-anchor="middle" font-size="17" fill="{C_ACC}" {MATHFONT}><tspan font-weight="bold" font-style="italic">a</tspan> = 0</text>'
    save(name, svg(w + 20, h, b))


def fbd_y(name, forces, acc=None, w=330, h=320, body='dot'):
    """مخطط جسم حر رأسي: forces = [(dir 'up'/'down', length, label)]؛ acc = 'up'/'down' سهم تسارع بنفسجي منفصل."""
    cx, cy = 165, 160; b = ''
    b += plus_arrow(45, 240, 100)
    b += DOT(cx, cy, 8, INK) if body == 'dot' else RECT(cx - 22, cy - 18, 44, 36)
    r0 = 0 if body == 'dot' else 18
    for d, ln, lab in forces:
        s = -1 if d == 'up' else 1
        b += ARROW(cx, cy + s * r0, cx, cy + s * (r0 + ln), C_FORCE, 3)
        b += V(cx + 14, cy + s * (r0 + ln * 0.6) + 6, lab, C_FORCE, 18, 'start')
    if acc:
        s = -1 if acc == 'up' else 1
        b += ARROW(270, cy - 30 * s, 270, cy + 30 * s, C_ACC, 3) + V(284, cy + 6, 'a', C_ACC, 18, 'start')
    save(name, svg(w, h, b))


def ball_with_v(name, up):
    w, h = 260, 280; b = ''
    b += f'<circle cx="130" cy="140" r="22" fill="#f3d36b" stroke="{INK}" stroke-width="1.5"/>'
    s = -1 if up else 1
    b += ARROW(175, 140 - 45 * s, 175, 140 + 45 * s, C_VEL, 3) + V(192, 146, 'v', C_VEL, 18, 'start')
    b += plus_arrow(45, 220, 100)
    save(name, svg(w, h, b))


def falling_seq(name):
    """كرة تسقط في أربعة مواضع: القوة المعيقة تزداد مع السرعة، والوزن ثابت."""
    w, h = 600, 330; b = ''; fg = 60
    data = [(15, 12), (32, 26), (48, 40), (60, 50)]   # (F_d بالبكسل، v بالبكسل)
    for i, (fd, vv) in enumerate(data):
        x = 80 + i * 140; y = 70 + i * 45
        b += f'<circle cx="{x}" cy="{y}" r="14" fill="#f3d36b" stroke="{INK}" stroke-width="1.5"/>'
        b += ARROW(x, y + 14, x, y + 14 + fg, C_FORCE, 3) + V(x - 12, y + 14 + fg - 4, 'F_g', C_FORCE, 16, 'end')
        b += ARROW(x, y - 14, x, y - 14 - fd, C_FORCE, 3) + V(x - 12, y - 14 - fd + 4, 'F_d', C_FORCE, 16, 'end')
        b += ARROW(x + 34, y - vv / 2, x + 34, y + vv / 2, C_VEL, 2.6) + V(x + 44, y + 6, 'v', C_VEL, 16, 'start')
        b += T(x, h - 14, str(i + 1), 15, weight='bold')
    save(name, svg(w, h, b))


def terminal_curve(vt=20.0, tau=2.0, tmax=10.0, n=100):
    return [(tmax * k / n, vt * (1 - math.exp(-tmax * k / n / tau))) for k in range(n + 1)]


def build():
    # O01: الوزن مقابل الكتلة لمكانين
    graph('c4l2-o01-weight-mass-lines.svg', [
        {'pts': [(0, 0), (10, 98)], 'color': C_FORCE, 'label': 'A', 'at': (10, 98), 'dx': -22, 'dy': 4},
        {'pts': [(0, 0), (10, 16.2)], 'color': ORANGE, 'label': 'B', 'at': (10, 16.2), 'dx': -22, 'dy': -8}],
        (0, 10), (0, 100), 'الكتلة (kg)', 'الوزن (N)', 2, 20)
    # O03: صندوق يرفعه حبل بتسارع إلى أعلى
    fbd_y('c4l2-o03-fbd-rope-up.svg', [('up', 105, 'F_T'), ('down', 85, 'F_g')], acc='up', body='box')
    # O03: رافعة تنزل صندوقًا بتسارع إلى أسفل
    fbd_y('c4l2-o03-fbd-crane-down.svg', [('up', 72, 'F_T'), ('down', 85, 'F_g')], acc='down', body='box')
    # O03 مقالي: ميزانان نابضيان ومكعب وكرة
    w, h = 300, 400; b = L(60, 20, 240, 20, INK, 4)
    for x in range(70, 240, 14): b += L(x, 20, x - 8, 11, MUTED, 1.2)
    def sp_scale(cx, y, lab):
        s = L(cx, y, cx, y + 16, INK, 2) + RECT(cx - 16, y + 16, 32, 58, INK, '#dfe5ee', 1.8)
        for k in range(5): s += L(cx - 7, y + 26 + 9 * k, cx + 7, y + 26 + 9 * k, MUTED, 1.2)
        s += L(cx, y + 74, cx, y + 92, INK, 2) + T(cx + 26, y + 50, lab, 14, 'start')
        return s
    b += sp_scale(150, 20, 'الميزان العلوي')
    b += RECT(125, 112, 50, 44, INK, '#e7c79a', 2) + T(150, 140, '1.2 kg', 13)
    b += sp_scale(150, 156, 'الميزان السفلي')
    b += f'<circle cx="150" cy="282" r="34" fill="#c4d3e6" stroke="{INK}" stroke-width="2"/>' + T(150, 287, '3.0 kg', 13)
    save('c4l2-o03-two-scales.svg', svg(w, 340, b))
    # O04: مخطط جسم حر لشخص على ميزان في مصعد متسارع
    fbd_y('c4l2-o04-fbd-elev.svg', [('up', 100, 'F_{sp}'), ('down', 80, 'F_g')], acc='up')
    # O05: قوة الميزان أصغر من الوزن
    fbd_y('c4l2-o05-fbd-compare.svg', [('up', 60, 'F_{sp}'), ('down', 95, 'F_g')])
    # O06: حالات المصعد
    elevator('c4l2-o06-elev-vup-aup.svg', v='up', a='up')
    elevator('c4l2-o06-elev-vup-adown.svg', v='up', a='down')
    elevator('c4l2-o06-elev-vdown-const.svg', v='down', a_zero=True)
    elevator('c4l2-o06-elev-vdown-aup.svg', v='down', a='up')
    graph('c4l2-o06-vt-elevator.svg', [{'pts': [(0, 0), (2, 2), (8, 2), (10, 0)], 'color': C_VEL}],
          (0, 12), (0, 3), XL, VL, 1, 0.5)
    graph('c4l2-o06-vt-down.svg', [{'pts': [(0, 0), (3, -3), (9, -3), (12, 0)], 'color': C_VEL}],
          (0, 12), (-4, 1), XL, VL, 1, 1)
    # O08: تسلسل السقوط والقوة المعيقة مقابل السرعة
    falling_seq('c4l2-o08-falling-seq.svg')
    graph('c4l2-o08-drag-speed.svg', [{'pts': [(v, 0.01 * v * v) for v in range(0, 21)], 'color': C_FORCE}],
          (0, 20), (0, 4), 'السرعة المتجهة (m/s)', 'القوة المعيقة (N)', 5, 1, marks=[(10, 1.0, ''), (20, 4.0, '')])
    # O11
    ball_with_v('c4l2-o11-ball-down.svg', up=False)
    ball_with_v('c4l2-o11-ball-up.svg', up=True)
    fbd_y('c4l2-o11-fbd-fd-up.svg', [('up', 50, 'F_d'), ('down', 95, 'F_g')])
    # O12
    graph('c4l2-o12-vt-plateau.svg', [{'pts': terminal_curve(20, 2.0, 10), 'color': C_VEL}],
          (0, 10), (0, 25), XL, VL, 1, 5)
    graph('c4l2-o12-vt-essay.svg', [{'pts': terminal_curve(9, 0.9, 5, 100), 'color': C_VEL}],
          (0, 5), (0, 10), XL, VL, 0.5, 1)
    # O13
    elevator('c4l2-o13-elev-53-up.svg', v='up', a='up')
    elevator('c4l2-o13-elev-75-down.svg', v='down', a='down')
    elevator('c4l2-o13-elev-60-slow.svg', v='down', a='up')
    graph('c4l2-o13-scale-graph.svg', [{'pts': [(0, 590), (2, 590), (2, 490), (6, 490), (6, 390), (8, 390)], 'color': C_FORCE}],
          (0, 8), (0, 700), XL, 'قراءة الميزان (N)', 1, 100)
    # ميزان نابضي معلّق في سقف مصعد يحمل جسمًا
    w, h = 380, 330; b = RECT(110, 30, 150, 260, INK, '#f1f3f7', 2.5) + L(185, 8, 185, 30, MUTED, 2)
    b += L(185, 30, 185, 48, INK, 2) + RECT(169, 48, 32, 60, INK, '#dfe5ee', 1.8)
    for k in range(5): b += L(178, 58 + 9 * k, 192, 58 + 9 * k, MUTED, 1.2)
    b += L(185, 108, 185, 135, INK, 2) + RECT(160, 135, 50, 42, INK, '#e7c79a', 2)
    b += plus_arrow(60, 230, 110)
    b += ARROW(315, 185, 315, 115, C_ACC, 3) + V(325, 156, 'a', C_ACC, 18, 'start')
    save('c4l2-o13-hang-scale.svg', svg(w, h, b))
    # O14
    fbd_y('c4l2-o14-fbd-scale.svg', [('up', 90, 'F_{sp}'), ('down', 90, 'F_g')])
    # O15
    pts = terminal_curve(20, 2.0, 10)
    v = lambda t: 20 * (1 - math.exp(-t / 2.0))
    graph('c4l2-o15-vt-points.svg', [{'pts': pts, 'color': C_VEL}], (0, 10), (0, 25), XL, VL, 1, 5,
          marks=[(1, v(1), 'A'), (3, v(3), 'B'), (9, v(9), 'C')])
    graph('c4l2-o15-vt-accel.svg', [{'pts': pts, 'color': C_VEL}], (0, 10), (0, 25), XL, VL, 1, 5,
          marks=[(0.5, v(0.5), 'K'), (4, v(4), 'M'), (8, v(8), 'N')])
    fbd_y('c4l2-o15-fbd-terminal.svg', [('up', 85, 'F_d'), ('down', 85, 'F_g')])


if __name__ == '__main__':
    build()
