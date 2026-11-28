import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-1 التيار الكهربائي الناتج عن تغير المجالات المغناطيسية (الأهداف O01–O07).
# اصطلاح الكتاب في الفصل الرابع: خطوط المجال وأسهمه خضراء، و(×) مجال داخل في الورقة و(•) خارج منها (أخضر)؛
# السرعة سهم أحمر رمزه v مائل، والتيار سهم أسود رفيع رمزه I قائم، والمجال B قائم غير عريض، وEMF قائمة.
# اتجاه التيار الحثي محسوب بالقاعدة الرابعة لليد اليمنى (الإبهام v، الأصابع B، العمودي على باطن الكف I) = اتجاه v × B.
import math

C_FIELD = '#1e8449'; WIRE = '#c8794a'; WIRE_D = '#9c5530'; MAG = '#c9d1dc'; MAG_D = '#5b6676'

def C(name, w, h, body): save(name, svg(w, h, body))
def lab_I(x, y, s='I', size=17, anchor='middle'): return T(x, y, s, size, anchor, INK, italic=False)
def lab_B(x, y, s='B', size=17, anchor='middle'): return T(x, y, s, size, anchor, C_FIELD, italic=False)
def lab_v(x, y, s='v', size=18, anchor='middle'): return T(x, y, s, size, anchor, C_VEL, italic=True)
def cross(x, y, s=6, c=C_FIELD, w=2): return L(x - s, y - s, x + s, y + s, c, w) + L(x - s, y + s, x + s, y - s, c, w)
def fdot(x, y, r=4, c=C_FIELD): return DOT(x, y, r, c)
def grid(x0, y0, x1, y1, kind='into', dx=44, dy=44, clear=()):
    b = ''; y = y0
    while y <= y1 + 0.1:
        x = x0
        while x <= x1 + 0.1:
            if not any(a - 8 <= x <= c + 8 and bb - 8 <= y <= d + 8 for a, bb, c, d in clear):
                b += cross(x, y) if kind == 'into' else fdot(x, y)
            x += dx
        y += dy
    return b
def hfield(x0, x1, ys, direction=1, w=2, at=0.5, arrows=True):
    b = ''
    for y in ys:
        b += L(x0, y, x1, y, C_FIELD, w)
        if arrows:
            mx = x0 + (x1 - x0) * at
            b += ARROW(mx - 12 * direction, y, mx + 12 * direction, y, C_FIELD, w, 12)
    return b
def vfield(y0, y1, xs, direction=1, w=2, at=0.5, arrows=True):
    b = ''
    for x in xs:
        b += L(x, y0, x, y1, C_FIELD, w)
        if arrows:
            my = y0 + (y1 - y0) * at
            b += ARROW(x, my - 12 * direction, x, my + 12 * direction, C_FIELD, w, 12)
    return b
def wire(x1, y1, x2, y2, w=7): return L(x1, y1, x2, y2, WIRE, w)
def wire_end(x, y, r=13):
    """مقطع سلك عمودي على الورقة (من غير بيان اتجاه التيار)."""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f6dcc8" stroke="{WIRE_D}" stroke-width="2.5"/>'
def cur(x1, y1, x2, y2): return ARROW(x1, y1, x2, y2, INK, 2, 10)
def magnet(x, y, w, h, letter):
    return RECT(x, y, w, h, MAG_D, MAG, 2) + (T(x + w / 2, y + h / 2 + 8, letter, 24, color=INK, weight='bold') if letter else '')
def tag(x, y, s, size=16): return T(x, y, s, size, color=INK, weight='bold')
def qmark(x, y, color=INK, size=24): return T(x, y, '؟', size, color=color, weight='bold')
def resistor(x, y1, y2, vertical=True):
    n = 6; pts = [(x, y1)]
    for k in range(n): pts.append((x + (9 if k % 2 == 0 else -9), y1 + (k + 0.5) * (y2 - y1) / n))
    pts.append((x, y2))
    return '<polyline points="' + ' '.join(f'{a:.1f},{c:.1f}' for a, c in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
def galv(x, y, r=17):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="2.2"/>' + T(x, y + 6, 'G', 16)

# ───────────────────────── O01
def o01():
    # MCQ: سلك عمودي على الورقة بين قطبين، وأربع حركات ممكنة (1) أعلى (2) يمين (3) أسفل (4) يسار
    b = magnet(20, 40, 70, 220, 'N') + magnet(450, 40, 70, 220, 'S')
    b += hfield(90, 450, [70, 115, 205, 250], 1, at=0.14) + L(90, 160, 205, 160, C_FIELD, 2) + L(335, 160, 450, 160, C_FIELD, 2)
    b += ARROW(130, 160, 154, 160, C_FIELD, 2, 12)
    b += wire_end(270, 160)
    b += ARROW(270, 145, 270, 88, C_VEL, 2.6, 11) + tag(270, 78, '(1)', 15)
    b += ARROW(285, 160, 330, 160, C_VEL, 2.6, 11) + tag(352, 147, '(2)', 15)
    b += ARROW(270, 175, 270, 232, C_VEL, 2.6, 11) + tag(270, 252, '(3)', 15) if False else ARROW(270, 175, 270, 232, C_VEL, 2.6, 11) + tag(296, 226, '(3)', 15)
    b += ARROW(255, 160, 210, 160, C_VEL, 2.6, 11) + tag(188, 147, '(4)', 15)
    b += lab_B(470, 30) + T(270, 290, 'سلك عمودي على الورقة', 14, color=MUTED)
    C('c4l1-o01-motions.svg', 540, 300, b)

    # مقالي: سلك رأسي داخل مجال منتظم داخل في الورقة، موصول بجلفانومتر خارج المجال
    b = RECT(110, 30, 260, 220, C_FIELD, '#eef7f1', 1.5)
    b += grid(134, 52, 350, 230, 'into', 43, 44, clear=[(222, 40, 258, 240)])
    b += wire(240, 20, 240, 260, 6)
    b += L(240, 20, 470, 20, INK, 2) + L(240, 260, 470, 260, INK, 2) + L(470, 20, 470, 123, INK, 2) + L(470, 157, 470, 260, INK, 2) + galv(470, 140)
    b += lab_B(388, 46) + T(240, 288, 'السلك المتحرك', 14, color=MUTED)
    C('c4l1-o01-e3.svg', 520, 300, b)

# ───────────────────────── O02
def o02():
    # ثلاثة اتجاهات متعامدة كما في القاعدة الرابعة لليد اليمنى
    ox, oy = 170, 200
    b = ARROW(ox, oy, ox + 190, oy, C_VEL, 3, 13) + lab_v(ox + 205, oy + 6) + T(ox + 150, oy + 30, 'الإبهام', 14, color=MUTED)
    b += ARROW(ox, oy, ox + 110, oy - 95, C_FIELD, 3, 13) + lab_B(ox + 124, oy - 102) + T(ox + 160, oy - 70, 'الأصابع', 14, color=MUTED)
    b += ARROW(ox, oy, ox, oy - 160, INK, 3, 13) + qmark(ox - 20, oy - 150) + T(ox - 30, oy - 110, 'العمودي على باطن الكف', 14, 'end', MUTED)
    b += L(ox - 4, oy - 18, ox + 14, oy - 18, MUTED, 1.4) + L(ox + 14, oy - 18, ox + 14, oy, MUTED, 1.4)
    b += DOT(ox, oy, 4, INK)
    C('c4l1-o02-rule.svg', 420, 240, b)

# ───────────────────────── O03
def o03():
    # منحنى التيار مع الزمن (جيبي) دون أرقام
    x0, x1, y0, A = 70, 470, 140, 85
    b = ARROW(x0, y0, x1 + 20, y0, INK, 2) + ARROW(x0, 250, x0, 30, INK, 2)
    pts = ' '.join(f'{x0 + t:.1f},{y0 - A * math.sin(2 * math.pi * t / 200):.1f}' for t in range(0, 401, 4))
    b += f'<polyline points="{pts}" fill="none" stroke="{C_VEL}" stroke-width="3"/>'
    b += L(x0, y0 - A, x0 + 50, y0 - A, MUTED, 1.2, '5 4') + L(x0, y0 + A, x0 + 150, y0 + A, MUTED, 1.2, '5 4')
    b += T(x0 - 8, y0 - A + 5, 'I_{عظمى}', 15, 'end') + T(x0 - 8, y0 + A + 5, '−I_{عظمى}', 15, 'end') + T(x0 - 10, y0 + 5, '0', 14, 'end', MUTED)
    b += T(x1 + 4, y0 + 24, 'الزمن', 14) + T(x0, 20, 'التيار', 14)
    C('c4l1-o03-ac.svg', 520, 260, b)

# ───────────────────────── O04
def o04():
    # ثلاثة أسلاك متماثلة عمودية على الورقة تتحرك بالسرعة نفسها في مجال أفقي منتظم باتجاهات مختلفة
    b = hfield(20, 620, [40, 260], 1, at=0.5) + lab_B(630, 34)
    for k, (ang, lab) in enumerate([(90, '(1)'), (30, '(2)'), (0, '(3)')]):
        cx, cy = 110 + k * 200, 180
        b += wire_end(cx, cy)
        a = math.radians(ang); ln = 95
        b += ARROW(cx + 15 * math.cos(a), cy - 15 * math.sin(a), cx + ln * math.cos(a), cy - ln * math.sin(a), C_VEL, 3, 12)
        b += lab_v(cx + (ln + 14) * math.cos(a) + (12 if ang == 90 else 0), cy - (ln + 14) * math.sin(a) + 6)
        if ang == 30:
            b += L(cx, cy, cx + 80, cy, MUTED, 1.2, '4 3') + f'<path d="M {cx + 48:.1f} {cy:.1f} A 48 48 0 0 0 {cx + 48 * math.cos(a):.1f} {cy - 48 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.5"/>' + T(cx + 66, cy - 12, '‎30°', 14)
        b += tag(cx, cy + 50, lab)
    C('c4l1-o04-angles.svg', 650, 280, b)

    # MCQ: سلك طويل جزء منه فقط داخل منطقة المجال
    b = RECT(200, 30, 140, 170, C_FIELD, '#eef7f1', 1.5) + grid(222, 54, 318, 180, 'out', 32, 42, clear=[(212, 100, 330, 130)])
    b += wire(40, 115, 520, 115, 6) + ARROW(470, 80, 470, 40, C_VEL, 3, 12) + lab_v(488, 52)
    b += L(200, 220, 340, 220, INK, 1.4) + L(200, 213, 200, 227, INK, 1.4) + L(340, 213, 340, 227, INK, 1.4) + T(270, 243, '0.20 m', 15)
    b += L(40, 268, 520, 268, INK, 1.4) + L(40, 261, 40, 275, INK, 1.4) + L(520, 261, 520, 275, INK, 1.4) + T(280, 291, '1.20 m', 15)
    b += lab_B(355, 30) + T(270, 22, 'منطقة المجال', 13, color=C_FIELD)
    C('c4l1-o04-part.svg', 560, 300, b)

# ───────────────────────── O05
def mic(name, labels):
    b = ''
    # موجات صوتية
    for r in (26, 46, 66):
        b += f'<path d="M {64 - r * 0.25:.0f} {170 - r} Q {64 - r:.0f} 170 {64 - r * 0.25:.0f} {170 + r}" fill="none" stroke="{MUTED}" stroke-width="1.6"/>'
    # الغشاء الرقيق
    b += f'<path d="M 110 60 Q 125 170 110 280" fill="none" stroke="#8a96a8" stroke-width="5"/>'
    # المغناطيس (مقطع): قطب مركزي N وقطبان خارجيان S
    b += RECT(240, 60, 150, 40, MAG_D, MAG, 2) + RECT(240, 240, 150, 40, MAG_D, MAG, 2) + RECT(350, 60, 40, 220, MAG_D, MAG, 2)
    b += RECT(220, 140, 170, 60, MAG_D, MAG, 2)
    b += T(262, 90, 'S', 18, weight='bold') + T(262, 270, 'S', 18, weight='bold') + T(250, 178, 'N', 18, weight='bold')
    # الملف حول القطب المركزي ومتصل بالغشاء
    b += RECT(150, 128, 58, 84, WIRE_D, '#f6dcc8', 2)
    for y in range(132, 210, 8): b += L(153, y, 205, y + 4, WIRE_D, 2)
    b += L(118, 140, 150, 140, INK, 2) + L(118, 200, 150, 200, INK, 2)
    # أسلاك التوصيل
    b += f'<path d="M 190 212 C 200 300 300 300 430 310" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    b += f'<path d="M 175 212 C 185 315 300 318 430 322" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    (l1, l2, l3, l4) = labels
    b += L(112, 70, 150, 30, INK, 1.1) + T(155, 28, l1, 14, 'start', weight='bold')
    b += L(180, 128, 205, 40, INK, 1.1) + T(208, 36, l2, 14, 'start', weight='bold') if False else L(185, 128, 230, 30, INK, 1.1) + T(234, 28, l2, 14, 'start', weight='bold')
    b += L(390, 120, 430, 110, INK, 1.1) + T(434, 114, l3, 14, 'start', weight='bold')
    b += L(400, 312, 430, 290, INK, 1.1) + T(434, 290, l4, 14, 'start', weight='bold')
    C(name, 560, 340, b)

def o05():
    mic('c4l1-o05-mic.svg', ('(1)', '(2)', '(3)', '(4)'))
    mic('c4l1-o05-e1.svg', ('غشاء رقيق', 'ملف', 'مغناطيس', 'أسلاك توصيل'))

# ───────────────────────── قضيب على سكتين
def rails(name, kind, R_lab, rod_x, vdir, L_lab=None, vlab='v', ends=None, B_lab='B', extra=''):
    """دائرة مستطيلة: مقاومة في الضلع الأيسر وسكتان أفقيتان وقضيب رأسي متحرك عند rod_x، في مجال (into/out)."""
    xl, xr, yt, yb = 60, 460, 50, 230
    b = grid(100, 80, 440, 200, kind, 48, 40, clear=[(rod_x - 18, 60, rod_x + 18, 220), (rod_x + (10 if vdir > 0 else -100), 112, rod_x + (100 if vdir > 0 else -10), 148)] if True else [])
    b += L(xl, yt, xr, yt, INK, 2.4) + L(xl, yb, xr, yb, INK, 2.4) + L(xl, yt, xl, 110, INK, 2.4) + L(xl, 170, xl, yb, INK, 2.4) + resistor(xl, 110, 170)
    if R_lab: b += T(xl + 18, 146, R_lab, 15, 'start')
    b += wire(rod_x, yt - 14, rod_x, yb + 14, 7)
    b += ARROW(rod_x + 14 * vdir, 130, rod_x + 80 * vdir, 130, C_VEL, 3, 12) + lab_v(rod_x + 90 * vdir + (6 if vdir > 0 else -6), 124, vlab, 16, 'start' if vdir > 0 else 'end')
    if L_lab:
        b += L(rod_x + 28 * (-vdir), yt, rod_x + 28 * (-vdir), yb, INK, 1.2) + L(rod_x + 28 * (-vdir) - 6, yt, rod_x + 28 * (-vdir) + 6, yt, INK, 1.2) + L(rod_x + 28 * (-vdir) - 6, yb, rod_x + 28 * (-vdir) + 6, yb, INK, 1.2)
        b += T(rod_x + 34 * (-vdir), 186, L_lab, 15, 'end' if vdir > 0 else 'start')
    if ends:
        b += T(rod_x + 16, yt - 8, ends[0], 16, 'start', weight='bold') + T(rod_x + 16, yb + 22, ends[1], 16, 'start', weight='bold')
    b += lab_B(486, 262, B_lab, 16, 'end') if B_lab else ''
    C(name, 520, 275, b + extra)

# ───────────────────────── O06
def o06():
    rails('c4l1-o06-rails.svg', 'out', 'R = 2.0 Ω', 330, 1, 'L = 0.40 m', 'v = 3.0 m/s', B_lab='B = 0.50 T')
    # سلك عمودي على الورقة سرعته تصنع زاوية 60° مع مجال أفقي
    b = hfield(20, 460, [40, 100, 220, 280], 1) + L(20, 160, 150, 160, C_FIELD, 2) + L(270, 160, 460, 160, C_FIELD, 2) + ARROW(340, 160, 364, 160, C_FIELD, 2, 12)
    cx, cy = 170, 160; a = math.radians(60)
    b += wire_end(cx, cy) + ARROW(cx + 15 * math.cos(a), cy - 15 * math.sin(a), cx + 120 * math.cos(a), cy - 120 * math.sin(a), C_VEL, 3, 12) + lab_v(cx + 134 * math.cos(a) + 6, cy - 134 * math.sin(a) + 8)
    b += L(cx + 13, cy, cx + 85, cy, INK, 1.2, '4 3') + f'<path d="M {cx + 50:.1f} {cy:.1f} A 50 50 0 0 0 {cx + 50 * math.cos(a):.1f} {cy - 50 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.5"/>' + T(cx + 64, cy - 26, '‎60°', 14)
    b += lab_B(470, 34)
    C('c4l1-o06-angle.svg', 490, 300, b)

# ───────────────────────── O07
def o07():
    # (a) سلك رأسي في مجال خارج من الورقة يتحرك إلى اليمين
    b = grid(40, 40, 320, 216, 'out', 47, 44, clear=[(158, 30, 182, 240), (186, 110, 270, 150)]) + wire(170, 20, 170, 240) + ARROW(184, 130, 260, 130, C_VEL, 3, 12) + lab_v(270, 124, anchor='start') + lab_B(340, 250, anchor='end')
    C('c4l1-o07-a.svg', 360, 262, b)
    # (b) قضيب على سكتين في مجال داخل في الورقة يتحرك إلى اليسار
    rails('c4l1-o07-rails.svg', 'into', 'R', 350, -1)
    # (c) سلك عمودي على الورقة بين قطبين N (يسار) وS (يمين) يتحرك إلى أسفل
    b = magnet(20, 40, 70, 220, 'N') + magnet(410, 40, 70, 220, 'S') + hfield(90, 410, [70, 115, 160, 250], 1, at=0.15)
    b += L(90, 205, 220, 205, C_FIELD, 2) + L(280, 205, 410, 205, C_FIELD, 2) + ARROW(128, 205, 152, 205, C_FIELD, 2, 12)
    b += f'<rect x="232" y="100" width="36" height="40" fill="#fff"/>' + wire_end(250, 120) + ARROW(250, 135, 250, 196, C_VEL, 3, 12) + lab_v(266, 186, anchor='start') + lab_B(430, 30)
    C('c4l1-o07-end.svg', 500, 280, b)
    # (d) قطبان مجهولان وخطوط مجال رأسية دون أسهم؛ سلك أفقي يتحرك نحو الناظر والتيار فيه من اليمين إلى اليسار
    b = RECT(110, 20, 300, 50, MAG_D, MAG, 2) + qmark(260, 56) + RECT(110, 250, 300, 50, MAG_D, MAG, 2) + qmark(260, 286)
    b += vfield(70, 250, [140, 190, 330, 380], arrows=False)
    b += wire(60, 160, 460, 160, 7) + ARROW(320, 140, 230, 140, INK, 2, 10) + lab_I(275, 130)
    b += f'<circle cx="260" cy="200" r="11" fill="#fff" stroke="{C_VEL}" stroke-width="2.4"/>' + DOT(260, 200, 3.4, C_VEL) + lab_v(282, 206, anchor='start')
    b += T(440, 50, 'قطب', 13, color=MUTED) + T(440, 280, 'قطب', 13, color=MUTED)
    C('c4l1-o07-poles.svg', 500, 315, b)
    # (e) أربع حالات لسلك رأسي
    b = ''
    cases = [('out', 1), ('out', -1), ('into', -1), ('into', 'up')]
    for k, (kind, d) in enumerate(cases):
        ox = k * 190
        b += grid(ox + 30, 60, ox + 160, 236, kind, 43, 44, clear=[(ox + 85, 40, ox + 105, 260)] + ([(ox + 112, 108, ox + 178, 150)] if d == 1 else [(ox + 14, 108, ox + 80, 150)] if d == -1 else [(ox + 108, 90, ox + 150, 200)]))
        b += wire(ox + 95, 50, ox + 95, 250, 6)
        if d == 1: b += ARROW(ox + 108, 130, ox + 165, 130, C_VEL, 3, 12) + lab_v(ox + 150, 116)
        elif d == -1: b += ARROW(ox + 82, 130, ox + 25, 130, C_VEL, 3, 12) + lab_v(ox + 40, 116)
        else: b += ARROW(ox + 122, 190, ox + 122, 105, C_VEL, 3, 12) + lab_v(ox + 140, 120)
        b += tag(ox + 95, 32, f'({k + 1})')
        if k: b += L(ox, 15, ox, 265, GRID, 1.5)
    b += lab_B(752, 270, anchor='end')
    C('c4l1-o07-panels.svg', 760, 280, b)
    # مقالي 1: قضيب على سكتين في مجال خارج من الورقة يتحرك إلى اليمين، طرفاه P (أعلى) وQ (أسفل)
    rails('c4l1-o07-e1.svg', 'out', 'R', 330, 1, ends=('P', 'Q'))
    # مقالي 2: سلك عمودي على الورقة في مجال أفقي إلى اليمين، وثلاث حركات
    b = hfield(20, 540, [40, 100, 230, 290], 1, at=0.12) + L(20, 165, 210, 165, C_FIELD, 2) + L(390, 165, 540, 165, C_FIELD, 2) + ARROW(470, 165, 494, 165, C_FIELD, 2, 12)
    cx, cy = 270, 165
    b += wire_end(cx, cy)
    b += ARROW(cx, cy - 15, cx, cy - 105, C_VEL, 3, 12) + tag(cx - 22, cy - 92, '(1)', 15)
    b += ARROW(cx + 15, cy, cx + 110, cy, C_VEL, 3, 12) + tag(cx + 128, cy + 22, '(2)', 15)
    a = math.radians(30)
    b += ARROW(cx + 15 * math.cos(a), cy - 15 * math.sin(a), cx + 110 * math.cos(a), cy - 110 * math.sin(a), C_VEL, 3, 12) + tag(cx + 126 * math.cos(a) + 10, cy - 126 * math.sin(a), '(3)', 15)
    b += f'<path d="M {cx + 50:.1f} {cy:.1f} A 50 50 0 0 0 {cx + 50 * math.cos(a):.1f} {cy - 50 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.5"/>' + T(cx + 70, cy - 10, '‎30°', 13)
    b += lab_B(545, 30, anchor='end')
    C('c4l1-o07-e2.svg', 560, 310, b)
    # مقالي 3: سلك رأسي في مجال داخل في الورقة يتحرك إلى اليمين
    b = grid(40, 40, 320, 216, 'into', 47, 44, clear=[(158, 30, 182, 240), (186, 110, 270, 150)]) + wire(170, 20, 170, 240) + ARROW(184, 130, 260, 130, C_VEL, 3, 12) + lab_v(270, 124, anchor='start') + lab_B(340, 250, anchor='end')
    C('c4l1-o07-e3.svg', 360, 262, b)

if __name__ == '__main__':
    o01(); o02(); o03(); o04(); o05(); o06(); o07()
