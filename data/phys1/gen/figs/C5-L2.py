import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 5-2 (الاحتكاك) — الأهداف O01–O11
import math

LINE = INK          # خطوط المنحنيات البيانية بلون محايد (ليست قوى)
LINE2 = ORANGE
LINE3 = GREEN


def SYM(x, y, base, sub='', color=C_FORCE, size=17, anchor='middle', bold=True, tail=''):
    """رمز كالكتاب: الحرف الأساسي مائل (عريض إن كان متجهًا) والحرف السفلي قائم (k، s، N، أو كلمة عربية كـ«الدفع»)."""
    rtl_sub = bool(re.search('[؀-ۿ]', sub))
    sf = FONT if rtl_sub else MATHFONT
    t = f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" direction="ltr" {MATHFONT}>'
    t += f'<tspan font-weight="{"bold" if bold else "normal"}" font-style="italic">{esc(base)}</tspan>'
    if sub: t += f'<tspan dy="0.32em" font-size="{int(size * 0.68)}" font-style="normal" font-weight="normal" {sf}>{esc(sub)}</tspan>'
    if tail: t += f'<tspan dy="-0.32em" font-size="{int(size * 0.9)}" font-weight="normal">{esc(tail)}</tspan>'
    return t + '</text>'


def plus_x(x, y, length=60, label='+x'):
    return ARROW(x, y, x + length, y, INK, 2) + T(x + length + 4, y + 5, label, 15, 'start', italic=True)


def plus_y(x, y, length=55, label='+y'):
    return ARROW(x, y, x, y - length, INK, 2) + T(x + 6, y - length + 4, label, 15, 'start', italic=True)


def ground(x1, x2, y, fill='#e9e2d0'):
    b = RECT(x1, y, x2 - x1, 14, INK, fill, 1.5)
    return b


def BOX(cx, cy, w, h, label='', fill='#eef2f8', size=16):
    return RECT(cx - w / 2, cy - h / 2, w, h, INK, fill, 2) + (T(cx, cy + 6, label, size) if label else '')


def NUM(x, y, n, color=INK):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="#fff" stroke="{color}" stroke-width="1.5"/>' + T(x, y + 5, str(n), 14, color=color)


def force(x1, y1, x2, y2, base, sub='', val=None, lx=None, ly=None, anchor='middle'):
    """سهم قوة أزرق يبدأ من الجسم، مع رمزها وقيمتها (اختياريًا)."""
    b = ARROW(x1, y1, x2, y2, C_FORCE, 3)
    lx = x2 if lx is None else lx; ly = y2 if ly is None else ly
    b += SYM(lx, ly, base, sub, C_FORCE, 17, anchor)
    if val: b += f'<text x="{lx:.1f}" y="{ly + 20:.1f}" text-anchor="{anchor}" font-size="15" fill="{C_FORCE}" direction="ltr" {MATHFONT}>{esc(val)}</text>'
    return b


def slope_block(x0, y0, x1, ang):
    """سطح مائل (مثلث) بزاوية ang عند القاعدة اليسرى؛ يعيد الرسم ونقطة منتصف الوتر."""
    a = math.radians(ang); y1 = y0 - (x1 - x0) * math.tan(a)
    b = f'<polygon points="{x0},{y0} {x1:.1f},{y0} {x1:.1f},{y1:.1f}" fill="#f3efe6" stroke="{INK}" stroke-width="2"/>'
    return b, y1


def incline_box(name, ang, angle_text, w=500, h=300, vel=None):
    a = math.radians(ang); x0, y0, x1 = 40, h - 40, w - 40
    b, y1 = slope_block(x0, y0, x1, ang)
    b += f'<path d="M {x0 + 60} {y0} A 60 60 0 0 0 {x0 + 60 * math.cos(a):.1f} {y0 - 60 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<text x="{x0 + 98:.1f}" y="{y0 - 10:.1f}" text-anchor="middle" font-size="16" fill="{INK}" direction="ltr" {MATHFONT}>{esc(angle_text)}</text>'
    mx = x0 + 0.55 * (x1 - x0); my = y0 - 0.55 * (x1 - x0) * math.tan(a)
    nx, ny = -math.sin(a), -math.cos(a)
    cx, cy = mx + 26 * nx, my + 26 * ny
    b += RECT(cx - 32, cy - 26, 64, 52, rot=-ang, cx=cx, cy=cy)
    if vel:
        ux, uy = math.cos(a), -math.sin(a)
        sx, sy = cx + 52 * nx - 30 * ux, cy + 52 * ny - 30 * uy
        sgn = 1 if vel == 'up' else -1
        ex, ey = sx + sgn * 80 * ux, sy + sgn * 80 * uy
        if sgn < 0: sx, sy, ex, ey = sx + 60 * ux, sy + 60 * uy, sx + 60 * ux - 80 * ux, sy + 60 * uy - 80 * uy
        b += ARROW(sx, sy, ex, ey, C_VEL, 3) + T(ex + 4, ey - 10, 'v', 18, 'start', C_VEL, 'bold', True)
    save(name, svg(w, h, b))


# ---------------- O03: مخطط حركة قرص ينزلق ويتباطأ (دون سهم تسارع) ----------------
def o03_puck_motion():
    w, h = 560, 150; b = ''
    xs = [50, 160, 255, 335, 400, 450, 485, 505]
    y = 80
    b += L(30, y + 26, 530, y + 26, MUTED, 1.5)
    for k, x in enumerate(xs):
        b += DOT(x, y, 7, INK)
        if k + 1 < len(xs):
            b += ARROW(x, y - 20, x + 0.85 * (xs[k + 1] - x), y - 20, C_VEL, 2.4, 9)
    b += T(50, y + 50, 'البداية', 13, color=MUTED)
    b += plus_x(40, 30, 60)
    save('c5l2-o03-puck-motion.svg', svg(w, h, b))


# ---------------- O04 ----------------
XL_N = 'القوة العمودية (N)'; YL_K = 'قوة الاحتكاك الحركي (N)'


def o04_slope_points():
    pts = [(10, 3), (20, 6), (30, 9), (40, 12)]
    graph('c5l2-o04-slope-points.svg', [{'pts': [(0, 0), (50, 15)], 'color': LINE, 'w': 2.5}], (0, 50), (0, 16), XL_N, YL_K, 10, 2,
          marks=[(x, y, '') for x, y in pts])


def o04_three_lines():
    X, Y = None, None
    series = [{'pts': [(0, 0), (50, 30)], 'color': LINE, 'label': 'A', 'dx': -18, 'dy': 4},
              {'pts': [(0, 0), (50, 20)], 'color': LINE2, 'label': 'B', 'dx': 6, 'dy': 6},
              {'pts': [(0, 0), (50, 7.5)], 'color': LINE3, 'label': 'C', 'dx': 6, 'dy': 6}]
    graph('c5l2-o04-three-lines.svg', series, (0, 50), (0, 30), XL_N, YL_K, 10, 5)


def o04_line_b():
    series = [{'pts': [(0, 0), (40, 20)], 'color': LINE, 'label': 'A', 'dx': 6, 'dy': 4},
              {'pts': [(0, 0), (50, 12.5)], 'color': LINE2, 'label': 'B', 'dx': 6, 'dy': 6}]
    graph('c5l2-o04-line-b.svg', series, (0, 50), (0, 25), XL_N, YL_K, 10, 5, marks=[(40, 20, ''), (40, 10, '')])


def o04_essay_two():
    series = [{'pts': [(0, 0), (40, 24)], 'color': LINE, 'label': 'ورق صنفرة', 'at': (30, 18), 'dx': -100, 'dy': -6},
              {'pts': [(0, 0), (50, 7.5)], 'color': LINE2, 'label': 'سطح طاولة أملس', 'at': (50, 7.5), 'dx': -120, 'dy': -14}]
    graph('c5l2-o04-essay-two.svg', series, (0, 50), (0, 25), XL_N, YL_K, 10, 5, marks=[(20, 12, ''), (40, 6, '')])


# ---------------- O07 / O10: قوة الاحتكاك – القوة المؤثرة ----------------
XL_A = 'القوة الأفقية المؤثرة (N)'; YL_S = 'قوة الاحتكاك السكوني (N)'


def static_graph(name, xmax, ymax, xs, ys, start):
    """منحنى الاحتكاك السكوني مقابل القوة المؤثرة كما تعلّمه صور الأريكة: يساويها حتى قيمته القصوى ثم تبدأ الحركة (لا يُرسم ما بعدها)."""
    s = [{'pts': [(0, 0), (start, start)], 'color': LINE, 'w': 2.8}]
    X, Y = graph(name, s, (0, xmax), (0, ymax), XL_A, YL_S, xs, ys, w=540)
    ex = L(X(start), Y(0), X(start), Y(ymax) + 4, MUTED, 1.8, '6 5') + DOT(X(start), Y(start), 5, LINE)
    ex += T(X(start) + 8, Y(ymax) + 16, 'تبدأ الحركة', 14, 'start', MUTED)
    graph(name, s, (0, xmax), (0, ymax), XL_A, YL_S, xs, ys, w=540, extra=ex)


def o07_graph_mcq():
    static_graph('c5l2-o07-graph-mcq.svg', 60, 50, 10, 10, 40)


def o07_graph_essay():
    static_graph('c5l2-o07-graph-essay.svg', 100, 70, 20, 10, 60)


def o07_fbd_rest():
    w, h = 420, 340; cx, cy = 210, 170; b = ''
    b += DOT(cx, cy, 7)
    b += force(cx, cy, cx, cy - 110, 'F', 'N', lx=cx + 12, ly=cy - 100, anchor='start')
    b += force(cx, cy, cx, cy + 110, 'F', 'g', lx=cx + 12, ly=cy + 110, anchor='start')
    b += force(cx, cy, cx + 95, cy, 'F', 'الدفع', lx=cx + 100, ly=cy - 14, anchor='start')
    b += force(cx, cy, cx - 95, cy, 'f', 's', lx=cx - 100, ly=cy - 14, anchor='end')
    b += plus_x(40, 300) + plus_y(40, 300)
    save('c5l2-o07-fbd-rest.svg', svg(w, h, b))


# ---------------- O08: مخطط جسم حر بقيم ----------------
def o08_fbd_numbers():
    w, h = 460, 340; cx, cy = 230, 170; b = ''
    b += DOT(cx, cy, 7)
    b += force(cx, cy, cx, cy - 110, 'F', 'N', '50 N', lx=cx + 12, ly=cy - 100, anchor='start')
    b += force(cx, cy, cx, cy + 110, 'F', 'g', '50 N', lx=cx + 12, ly=cy + 110, anchor='start')
    b += force(cx, cy, cx + 120, cy, 'F', 'الدفع', '30 N', lx=cx + 60, ly=cy - 38, anchor='middle')
    b += force(cx, cy, cx - 80, cy, 'f', 'k', '20 N', lx=cx - 45, ly=cy - 38, anchor='middle')
    b += plus_x(40, 310) + plus_y(40, 310)
    save('c5l2-o08-fbd-numbers.svg', svg(w, h, b))


# ---------------- O09 ----------------
def o09_brick_faces():
    w, h = 560, 210; b = ''
    b += ground(20, 540, 160)
    # الحالة 1: الوجه الكبير
    b += BOX(140, 135, 160, 50, '', '#d98c6a')
    b += L(220, 135, 262, 135, INK, 1.8) + RECT(262, 125, 26, 20, INK, '#f5f5f5', 1.5)
    b += T(140, 196, 'الحالة (1)', 14)
    # الحالة 2: الوجه الصغير
    b += BOX(400, 120, 60, 80, '', '#d98c6a')
    b += L(430, 135, 472, 135, INK, 1.8) + RECT(472, 125, 26, 20, INK, '#f5f5f5', 1.5)
    b += T(400, 196, 'الحالة (2)', 14)
    b += T(280, 40, 'القطعة نفسها تُسحب بميزان نابضي أفقيًا بسرعة منتظمة', 14, color=MUTED)
    save('c5l2-o09-brick-faces.svg', svg(w, h, b))


def o09_press_down():
    w, h = 460, 400; cx, cy = 230, 200; b = ''
    b += DOT(cx, cy, 7)
    b += force(cx, cy, cx, cy - 156, 'F', 'N', lx=cx + 12, ly=cy - 140, anchor='start')
    b += force(cx, cy, cx, cy + 130, 'F', 'g', '100 N', lx=cx - 12, ly=cy + 125, anchor='end')
    b += L(cx, cy, cx + 18, cy, C_FORCE, 2) + force(cx + 18, cy, cx + 18, cy + 26, 'F', '', '20 N', lx=cx + 28, ly=cy + 28, anchor='start')
    b += force(cx, cy, cx + 100, cy, 'F', 'الدفع', lx=cx + 104, ly=cy - 14, anchor='start')
    b += force(cx, cy, cx - 90, cy, 'f', 'k', lx=cx - 95, ly=cy - 14, anchor='end')
    b += plus_x(40, 370) + plus_y(40, 370)
    save('c5l2-o09-press-down.svg', svg(w, h, b))


# ---------------- O11 ----------------
def o11_setup():
    w, h = 560, 220; b = ''
    b += ground(20, 540, 150)
    b += BOX(140, 125, 110, 50, 'قطعة خشبية', '#d9c7a6', 13)
    # الخيط والميزان النابضي
    b += L(195, 125, 300, 125, INK, 1.8)
    b += RECT(300, 113, 110, 24, INK, '#f1f3f7', 1.8)
    for k in range(8): b += L(312 + k * 11, 113, 312 + k * 11, 120, MUTED, 1.2)
    b += L(410, 125, 470, 125, INK, 3) + f'<circle cx="478" cy="125" r="8" fill="none" stroke="{INK}" stroke-width="2.5"/>'
    b += T(355, 102, 'ميزان نابضي', 13, color=MUTED)
    b += T(280, 196, 'سطح خشبي أفقي', 14, color=MUTED)
    save('c5l2-o11-setup.svg', svg(w, h, b))


if __name__ == '__main__':
    incline_box('c5l2-o02-incline-rest.svg', 25, 'θ')
    o03_puck_motion()
    o04_slope_points(); o04_three_lines(); o04_line_b(); o04_essay_two()
    o07_graph_mcq(); o07_graph_essay(); o07_fbd_rest()
    o08_fbd_numbers()
    o09_brick_faces(); o09_press_down()
    o11_setup()
    incline_box('c5l2-o11-incline-22.svg', 22, '22°')
    incline_box('c5l2-o11-incline-26.svg', 26, '26.0°')
