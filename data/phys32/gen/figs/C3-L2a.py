import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-2 القوى الناتجة عن المجالات المغناطيسية (الأهداف O01–O08).
# اصطلاح الكتاب في الفصل الثالث: خطوط المجال المغناطيسي وأسهمه خضراء، والرمز (×) مجال داخل في الورقة و(•) خارج منها (أخضر)؛
# القوة سهم أزرق رمزه F مائل غير عريض، والسرعة سهم أحمر رمزه v مائل، والتيار سهم رفيع رمزه I قائم، والمجال B قائم غير عريض.
import math

C_FIELD = '#1e8449'; WIRE = '#c8794a'; WIRE_D = '#9c5530'; MAG = '#c9d1dc'; MAG_D = '#5b6676'; PLUS = '#c0392b'

def C(name, w, h, body): save(name, svg(w, h, body))
def lab_I(x, y, s='I', size=17, anchor='middle'): return T(x, y, s, size, anchor, INK, italic=False)
def lab_B(x, y, s='B', size=17, anchor='middle'): return T(x, y, s, size, anchor, C_FIELD, italic=False)
def lab_F(x, y, s='F', size=18, anchor='middle'): return T(x, y, s, size, anchor, C_FORCE, italic=True)
def lab_v(x, y, s='v', size=18, anchor='middle'): return T(x, y, s, size, anchor, C_VEL, italic=True)

def cross(x, y, s=6, c=C_FIELD, w=2):
    return L(x - s, y - s, x + s, y + s, c, w) + L(x - s, y + s, x + s, y - s, c, w)
def fdot(x, y, r=4, c=C_FIELD): return DOT(x, y, r, c)
def grid(x0, y0, x1, y1, kind='into', dx=44, dy=44, skip=(), clear=()):
    """شبكة رموز المجال: (×) داخل في الورقة أو (•) خارج منها. clear: مستطيلات (x0,y0,x1,y1) تُترك خالية للأسهم والتسميات."""
    b = ''; y = y0
    while y <= y1 + 0.1:
        x = x0
        while x <= x1 + 0.1:
            hid = any(abs(x - sx) < dx / 2 and abs(y - sy) < dy / 2 for sx, sy in skip)
            hid = hid or any(a - 8 <= x <= c + 8 and bb - 8 <= y <= d + 8 for a, bb, c, d in clear)
            if not hid: b += cross(x, y) if kind == 'into' else fdot(x, y)
            x += dx
        y += dy
    return b
def hfield(x0, x1, ys, direction=1, w=2, at=0.5):
    """خطوط مجال أفقية خضراء، وعلى كل خط رأس سهم عند الكسر at من طوله (direction=1 إلى اليمين)."""
    b = ''
    for y in ys:
        b += L(x0, y, x1, y, C_FIELD, w)
        mx = x0 + (x1 - x0) * at
        b += ARROW(mx - 12 * direction, y, mx + 12 * direction, y, C_FIELD, w, 12)
    return b
def vfield(y0, y1, xs, direction=1, w=2, at=0.5):
    """خطوط مجال رأسية (direction=1 إلى الأسفل)، ورأس السهم عند الكسر at من طولها."""
    b = ''
    for x in xs:
        b += L(x, y0, x, y1, C_FIELD, w)
        my = y0 + (y1 - y0) * at
        b += ARROW(x, my - 12 * direction, x, my + 12 * direction, C_FIELD, w, 12)
    return b
def wire(x1, y1, x2, y2, w=7): return L(x1, y1, x2, y2, WIRE, w)
def wire_end(x, y, kind, r=14):
    """مقطع سلك عمودي على الورقة: (×) التيار داخل في الورقة، (•) خارج منها."""
    b = f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f6dcc8" stroke="{WIRE_D}" stroke-width="2.5"/>'
    b += (L(x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55, INK, 2.4) + L(x - r * 0.55, y + r * 0.55, x + r * 0.55, y - r * 0.55, INK, 2.4)) if kind == 'into' else DOT(x, y, 3.6, INK)
    return b
def cur(x1, y1, x2, y2, label='I', lx=None, ly=None):
    b = ARROW(x1, y1, x2, y2, INK, 2, 10)
    if label: b += lab_I(lx if lx is not None else (x1 + x2) / 2, ly if ly is not None else (y1 + y2) / 2 - 10)
    return b
def magnet(x, y, w, h, letter):
    return RECT(x, y, w, h, MAG_D, MAG, 2) + T(x + w / 2, y + h / 2 + 8, letter, 24, color=INK, weight='bold')
def panel_tag(x, y, s): return T(x, y, s, 17, color=INK, weight='bold')
def qmark(x, y, color=C_FORCE): return T(x, y, '؟', 24, color=color, weight='bold')

def battery(x, y, vertical=True, plus_top=True, label=None):
    """رمز البطارية كما في الكتاب: خطوط طويلة ورفيعة (الموجب) وقصيرة وسميكة متناوبة."""
    b = ''
    offs = [-9, -3, 3, 9]; lens = [16, 8, 16, 8]
    if not plus_top: offs = offs[::-1]
    for o, ln in zip(offs, lens):
        if vertical: b += L(x - ln, y + o, x + ln, y + o, INK, 2.6 if ln == 16 else 3.4)
        else: b += L(x + o, y - ln, x + o, y + ln, INK, 2.6 if ln == 16 else 3.4)
    if vertical:
        b += T(x + 26, y + offs[0] + 5, '+', 16, color=PLUS, weight='bold') + T(x + 26, y + offs[-1] + 6, '−', 16, weight='bold')
        if label: b += T(x - 26, y + 6, label, 15, 'end')
    return b
def resistor(x1, y, x2):
    pts = [(x1, y)]; n = 6
    for k in range(n): pts.append((x1 + (k + 0.5) * (x2 - x1) / n, y + (9 if k % 2 == 0 else -9)))
    pts.append((x2, y))
    return '<polyline points="' + ' '.join(f'{a:.1f},{c:.1f}' for a, c in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
def switch_open(x1, y, x2):
    return DOT(x1, y, 3.2) + DOT(x2, y, 3.2) + L(x1, y, x2 - 3, y - 18, INK, 2.4)

# ───────────────────────── O01
def o01():
    # MCQ: عكس اتجاه التيار — الحالة (1) القوة إلى أعلى، الحالة (2) التيار معكوس والقوة مجهولة
    b = ''
    for k, (dirn, force) in enumerate([(1, True), (-1, False)]):
        ox = k * 300
        b += grid(ox + 40, 70, ox + 260, 202, 'into', clear=[(ox + 105, 96, ox + 175, 124), (ox + 222, 60, ox + 252, 130), (ox + 255, 215, ox + 270, 240)])
        b += wire(ox + 20, 136, ox + 280, 136)
        if dirn == 1: b += cur(ox + 110, 116, ox + 170, 116, None) + lab_I(ox + 140, 108)
        else: b += cur(ox + 170, 116, ox + 110, 116, None) + lab_I(ox + 140, 108)
        if force: b += ARROW(ox + 230, 136, ox + 230, 70, C_FORCE, 3, 13) + lab_F(ox + 246, 84)
        else: b += qmark(ox + 236, 104)
        b += panel_tag(ox + 150, 34, f'({k + 1})')
        b += lab_B(ox + 262, 230)
    b += L(300, 20, 300, 240, GRID, 1.5)
    C('c3l2-o01-reverse.svg', 600, 250, b)

    # مقالي: سلك أفقي بين قطبين (N أعلى، S أسفل) موصول ببطارية ومفتاح مفتوح
    b = magnet(170, 30, 200, 56, 'N') + magnet(170, 214, 200, 56, 'S')
    b += vfield(92, 208, [195, 235, 275, 315, 355], 1, at=0.25)
    b += lab_B(392, 125)
    b += wire(90, 150, 450, 150, 6)
    b += L(90, 150, 60, 150, INK, 2.2) + L(450, 150, 500, 150, INK, 2.2)
    b += L(60, 150, 60, 330, INK, 2.2) + L(500, 150, 500, 330, INK, 2.2)
    b += L(60, 330, 200, 330, INK, 2.2) + battery(230, 330, vertical=False) + L(239, 330, 330, 330, INK, 2.2)
    b += switch_open(330, 330, 380) + L(380, 330, 500, 330, INK, 2.2)
    b += T(230, 312, '+', 16, color=PLUS, weight='bold') if False else ''
    b += T(212, 366, 'بطارية', 14, color=MUTED) + T(355, 366, 'مفتاح', 14, color=MUTED) + T(470, 140, 'سلك', 14, color=MUTED)
    C('c3l2-o01-e1.svg', 560, 385, b)

# ───────────────────────── O02
def o02():
    # MCQ: سلك طويل جزء منه فقط داخل المجال المنتظم (×)
    b = RECT(150, 40, 220, 150, C_FIELD, '#eef7f1', 1.5)
    b += grid(172, 62, 348, 170, 'into', 44, 36)
    b += wire(30, 115, 490, 115)
    b += cur(70, 98, 120, 98, None) + lab_I(95, 90)
    b += L(150, 205, 370, 205, INK, 1.5) + L(150, 198, 150, 212, INK, 1.5) + L(370, 198, 370, 212, INK, 1.5) + T(260, 228, '0.30 m', 15)
    b += L(30, 255, 490, 255, INK, 1.5) + L(30, 248, 30, 262, INK, 1.5) + L(490, 248, 490, 262, INK, 1.5) + T(260, 278, '1.20 m', 15)
    b += lab_B(388, 58) + T(260, 30, 'منطقة المجال', 14, color=C_FIELD)
    C('c3l2-o02-inside.svg', 520, 290, b)

    # مقالي: ثلاثة أسلاك في مجال منتظم أفقي: 1 عمودي، 2 بزاوية 30°، 3 موازٍ
    b = hfield(30, 590, [50, 110, 170, 230], 1) + lab_B(600, 44)
    b += wire(110, 40, 110, 240, 6) + T(110, 268, '1', 18, weight='bold')
    a = math.radians(30); cx, cy, ln = 300, 140, 110
    x1, y1, x2, y2 = cx - ln * math.cos(a), cy + ln * math.sin(a), cx + ln * math.cos(a), cy - ln * math.sin(a)
    b += wire(x1, y1, x2, y2, 6) + T(cx, 268, '2', 18, weight='bold')
    b += f'<path d="M {cx + 46:.1f} {cy:.1f} A 46 46 0 0 0 {cx + 46 * math.cos(a):.1f} {cy - 46 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    b += L(cx, cy, cx + 70, cy, INK, 1.2, '4 3') + T(cx + 64, cy - 12, '‎30°', 14)
    b += wire(440, 140, 580, 140, 6) + T(510, 268, '3', 18, weight='bold')
    C('c3l2-o02-angles.svg', 620, 280, b)

# ───────────────────────── O03
def o03():
    # MCQ: الحالة (1) I إلى اليمين وB خارج من الورقة والقوة إلى أسفل، الحالة (2) عكس I وB معًا
    b = ''
    for k in range(2):
        ox = k * 300
        b += grid(ox + 40, 70, ox + 260, 202, 'out' if k == 0 else 'into', clear=[(ox + 105, 96, ox + 175, 124), (ox + 222, 142, ox + 252, 210), (ox + 255, 215, ox + 270, 240)])
        b += wire(ox + 20, 136, ox + 280, 136)
        if k == 0: b += cur(ox + 110, 116, ox + 170, 116, None) + lab_I(ox + 140, 108) + ARROW(ox + 230, 136, ox + 230, 202, C_FORCE, 3, 13) + lab_F(ox + 246, 196)
        else: b += cur(ox + 170, 116, ox + 110, 116, None) + lab_I(ox + 140, 108) + qmark(ox + 236, 172)
        b += panel_tag(ox + 150, 34, f'({k + 1})') + lab_B(ox + 262, 230)
    b += L(300, 20, 300, 240, GRID, 1.5)
    C('c3l2-o03-reverse.svg', 600, 250, b)

    # مقالي: سلك يسري فيه تيار إلى اليمين في مجال داخل في الورقة (لتقويم طريقة طالب)
    b = grid(50, 50, 330, 182, 'into', clear=[(145, 74, 235, 102)]) + wire(20, 116, 360, 116) + cur(150, 96, 230, 96, None) + lab_I(190, 88) + lab_B(345, 210)
    C('c3l2-o03-case.svg', 380, 222, b)

# ───────────────────────── O04
def o04():
    # MCQ: سلك يصنع زاوية 30° مع خطوط مجال منتظم أفقي
    b = hfield(30, 470, [50, 105, 160, 215], 1) + lab_B(480, 44)
    a = math.radians(30); cx, cy, ln = 240, 135, 150
    x1, y1, x2, y2 = cx - ln * math.cos(a), cy + ln * math.sin(a), cx + ln * math.cos(a), cy - ln * math.sin(a)
    b += wire(x1, y1, x2, y2, 6)
    b += ARROW(cx + 40 * math.cos(a) - 18, cy - 40 * math.sin(a) - 30, cx + 100 * math.cos(a) - 18, cy - 100 * math.sin(a) - 30, INK, 2, 10)
    b += lab_I(cx + 70 * math.cos(a) - 34, cy - 70 * math.sin(a) - 40)
    b += f'<path d="M {cx + 58:.1f} {cy:.1f} A 58 58 0 0 0 {cx + 58 * math.cos(a):.1f} {cy - 58 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    b += L(cx, cy, cx + 90, cy, INK, 1.2, '4 3') + T(cx + 80, cy - 12, '‎30°', 15)
    C('c3l2-o04-angle.svg', 500, 260, b)

    # MCQ: سلك أفقي معلّق في مجال داخل في الورقة؛ القوة المغناطيسية إلى أعلى توازن الوزن
    b = grid(70, 60, 370, 216, 'into', 44, 52, clear=[(240, 50, 290, 230), (105, 150, 185, 190)]) + wire(30, 138, 410, 138)
    b += cur(110, 158, 180, 158, None) + lab_I(145, 180)
    b += ARROW(250, 138, 250, 62, C_FORCE, 3, 13) + lab_F(266, 76)
    b += ARROW(250, 138, 250, 214, C_FORCE, 3, 13) + T(272, 214, 'F_g', 18, color=C_FORCE, italic=True)
    b += lab_B(392, 250)
    C('c3l2-o04-balance.svg', 440, 262, b)

    # مقالي: دائرة فيها بطارية 12 V ومقاومة 6.0 Ω ومفتاح، وجزء من السلك طوله 8.0 cm داخل مجال منتظم 1.5 T داخل في الورقة
    b = RECT(170, 30, 200, 110, C_FIELD, '#eef7f1', 1.5) + grid(192, 52, 348, 118, 'into', 39, 66)
    b += wire(120, 85, 420, 85, 6)
    b += L(120, 85, 60, 85, INK, 2.2) + L(420, 85, 480, 85, INK, 2.2)
    b += L(170, 160, 370, 160, INK, 1.4) + L(170, 153, 170, 167, INK, 1.4) + L(370, 153, 370, 167, INK, 1.4) + T(270, 182, '8.0 cm', 15)
    b += L(60, 85, 60, 205, INK, 2.2) + battery(60, 220, True, True) + L(60, 229, 60, 300, INK, 2.2)
    b += T(30, 225, '12 V', 15, 'end')
    b += L(60, 300, 200, 300, INK, 2.2) + switch_open(200, 300, 250) + L(250, 300, 300, 300, INK, 2.2)
    b += resistor(300, 300, 360) + T(330, 330, '6.0 Ω', 15) + L(360, 300, 480, 300, INK, 2.2) + L(480, 85, 480, 300, INK, 2.2)
    b += T(225, 330, 'مفتاح', 14, color=MUTED) + lab_B(270, 22, 'B = 1.5 T', 16)
    C('c3l2-o04-e2.svg', 520, 345, b)

# ───────────────────────── O05
def o05():
    # MCQ: إلكترون يتحرك عموديًّا على مجال داخل في الورقة
    b = grid(40, 40, 360, 196, 'into', 40, 39, clear=[(100, 105, 262, 165)])
    b += DOT(120, 118, 7, '#1f2a44', '#5b8fd6') + T(120, 150, 'إلكترون', 14)
    b += ARROW(128, 118, 240, 118, C_VEL, 3, 13) + lab_v(250, 110)
    b += lab_B(378, 220)
    C('c3l2-o05-beam.svg', 400, 232, b)

    # MCQ: بروتون سرعته تصنع زاوية 30° مع خطوط مجال أفقي
    b = hfield(30, 450, [50, 110, 170, 230], 1) + lab_B(460, 44)
    a = math.radians(30); cx, cy = 170, 170
    b += DOT(cx, cy, 8, '#1f2a44', '#e7a29a') + T(cx - 22, cy + 6, '+', 16, color=PLUS, weight='bold')
    b += ARROW(cx + 8, cy - 4, cx + 150 * math.cos(a), cy - 150 * math.sin(a), C_VEL, 3, 13) + lab_v(cx + 160 * math.cos(a) + 8, cy - 160 * math.sin(a) - 4)
    b += f'<path d="M {cx + 60:.1f} {cy:.1f} A 60 60 0 0 0 {cx + 60 * math.cos(a):.1f} {cy - 60 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    b += T(cx + 84, cy - 18, '‎30°', 15)
    C('c3l2-o05-angle.svg', 490, 260, b)

# ───────────────────────── O06
def o06():
    # (a) سلك تياره إلى اليمين في مجال داخل في الورقة
    b = grid(50, 40, 330, 172, 'into', clear=[(145, 64, 235, 92)]) + wire(20, 106, 360, 106) + cur(150, 86, 230, 86, None) + lab_I(190, 78) + lab_B(350, 200)
    C('c3l2-o06-a.svg', 380, 212, b)
    # (b) سلك رأسي تياره إلى أعلى في مجال خارج من الورقة
    b = grid(40, 40, 260, 260, 'out', clear=[(162, 112, 200, 198)]) + wire(150, 20, 150, 280) + cur(172, 190, 172, 120, None) + lab_I(188, 160) + lab_B(282, 280)
    C('c3l2-o06-b.svg', 300, 296, b)
    # (c) سلك عمودي على الورقة تياره خارج منها في مجال أفقي إلى اليسار
    b = hfield(30, 370, [50, 110, 230, 290], -1) + L(30, 170, 175, 170, C_FIELD, 2) + L(225, 170, 370, 170, C_FIELD, 2)
    b += ARROW(110, 170, 86, 170, C_FIELD, 2, 12) + ARROW(310, 170, 286, 170, C_FIELD, 2, 12)
    b += wire_end(200, 170, 'out') + lab_I(226, 156) + lab_B(20, 40)
    C('c3l2-o06-c.svg', 400, 310, b)
    # (d) سلك أفقي تياره إلى اليمين بين قطبين: N أعلى وS أسفل
    b = magnet(110, 20, 220, 50, 'N') + magnet(110, 210, 220, 50, 'S') + vfield(76, 204, [140, 180, 260, 300], 1, at=0.25)
    b += wire(30, 140, 410, 140) + cur(60, 120, 110, 120, None) + lab_I(85, 112)
    C('c3l2-o06-d.svg', 440, 275, b)
    # (e) بروتون يتحرك إلى أعلى الصفحة في مجال داخل فيها
    b = grid(40, 40, 260, 260, 'into', 44, 44, clear=[(118, 84, 182, 262)]) + DOT(150, 216, 8, '#1f2a44', '#e7a29a') + T(132, 222, '+', 16, color=PLUS, weight='bold')
    b += ARROW(150, 208, 150, 92, C_VEL, 3, 13) + lab_v(168, 100) + T(150, 252, 'بروتون', 14) + lab_B(282, 282)
    C('c3l2-o06-e.svg', 300, 296, b)
    # (f) سلك رأسي تياره إلى أسفل الصفحة في مجال أفقي يتجه إلى اليسار
    b = hfield(30, 330, [60, 120, 180, 240], -1, at=0.2) + wire(200, 30, 200, 270) + cur(222, 115, 222, 185, None) + lab_I(238, 156, anchor='start') + lab_B(20, 52)
    C('c3l2-o06-f.svg', 360, 290, b)
    # (g) سلك تياره إلى اليمين والقوة المؤثرة فيه إلى أعلى؛ المجال مجهول
    b = wire(20, 150, 360, 150) + cur(90, 170, 170, 170, None) + lab_I(130, 192) + ARROW(250, 150, 250, 60, C_FORCE, 3, 13) + lab_F(268, 74)
    b += T(250, 220, 'اتجاه المجال المغناطيسي B ؟', 15, color=C_FIELD)
    C('c3l2-o06-g.svg', 380, 240, b)
    # مقالي: حلقة مستطيلة بين قطبين N (يسار) وS (يمين)، التيار في الضلع القريب من N إلى أعلى وفي الضلع الآخر إلى أسفل؛ المنظر من الأعلى
    b = magnet(20, 50, 70, 220, 'N') + magnet(470, 50, 70, 220, 'S') + hfield(90, 470, [95, 135, 185, 225], 1, at=0.11)
    b += f'<rect x="170" y="70" width="220" height="180" fill="none" stroke="{WIRE}" stroke-width="6"/>'
    b += cur(192, 200, 192, 130, None) + lab_I(206, 168, anchor='start')
    b += cur(368, 130, 368, 200, None) + lab_I(354, 168, anchor='end')
    b += cur(250, 54, 310, 54, None) + cur(310, 268, 250, 268, None)
    b += T(150, 296, 'الضلع (1)', 15, weight='bold') + T(410, 296, 'الضلع (2)', 15, weight='bold') + lab_B(280, 166)
    C('c3l2-o06-e2.svg', 560, 305, b)
    # مقالي: ثلاث حالات
    b = ''
    # (1) سلك تياره إلى اليسار في مجال خارج من الورقة
    b += grid(30, 70, 200, 202, 'out', 42, 44, clear=[(75, 92, 145, 124)]) + wire(14, 136, 216, 136) + cur(140, 116, 80, 116, None) + lab_I(110, 106) + panel_tag(115, 36, '(1)')
    # (2) سلك رأسي تياره إلى أسفل في مجال أفقي إلى اليمين
    ox = 240
    b += hfield(ox + 14, ox + 216, [80, 130, 180], 1) + wire(ox + 115, 60, ox + 115, 210) + cur(ox + 136, 105, ox + 136, 165, None) + lab_I(ox + 150, 140, anchor='start') + panel_tag(ox + 115, 36, '(2)')
    # (3) بروتون يتحرك إلى اليسار في مجال رأسي إلى أعلى
    ox = 480
    b += vfield(60, 215, [ox + 30, ox + 75, ox + 205], -1, at=0.8)
    b += DOT(ox + 165, 140, 8, '#1f2a44', '#e7a29a') + T(ox + 165, 170, 'بروتون', 13)
    b += ARROW(ox + 157, 140, ox + 50, 140, C_VEL, 3, 13) + lab_v(ox + 60, 128) + panel_tag(ox + 115, 36, '(3)')
    b += lab_B(222, 222) + lab_B(240 + 222, 70) + lab_B(ox + 222, 76)
    b += L(230, 20, 230, 230, GRID, 1.5) + L(470, 20, 470, 230, GRID, 1.5)
    C('c3l2-o06-e3.svg', 720, 240, b)

# ───────────────────────── O07
def o07():
    # مكبر الصوت: مخروط ورقي (1)، ملف (2)، مغناطيس دائم (3)
    b = ''
    b += f'<polygon points="90,40 250,120 250,200 90,280" fill="#eceff3" stroke="{INK}" stroke-width="2"/>'
    b += RECT(250, 110, 60, 100, INK, '#f6dcc8', 2)
    for y in range(116, 206, 9): b += L(254, y, 306, y + 4, WIRE_D, 2)
    b += RECT(300, 80, 40, 160, MAG_D, '#a55a4a', 2) + RECT(280, 80, 30, 26, MAG_D, '#a55a4a', 2) + RECT(280, 214, 30, 26, MAG_D, '#a55a4a', 2)
    for r in (30, 52, 74):
        b += f'<path d="M {70 - r * 0.3:.0f} {160 - r} Q {70 - r:.0f} 160 {70 - r * 0.3:.0f} {160 + r}" fill="none" stroke="{MUTED}" stroke-width="1.6"/>'
    b += L(150, 90, 190, 30, INK, 1.2) + T(196, 26, '(1)', 15, 'start', weight='bold')
    b += L(280, 160, 380, 160, INK, 1.2) + T(386, 165, '(2)', 15, 'start', weight='bold')
    b += L(338, 100, 380, 60, INK, 1.2) + T(386, 60, '(3)', 15, 'start', weight='bold')
    b += L(310, 200, 340, 290, INK, 2) + L(300, 205, 320, 290, INK, 2) + T(330, 312, 'إلى المضخم', 14, color=MUTED)
    C('c3l2-o07-spk.svg', 440, 325, b)

# ───────────────────────── O08
def o08():
    # جلفانومتر: قطبا مغناطيس على شكل حرف U، ملف حول قلب حديدي، نابض، مؤشر وتدريج
    b = f'<path d="M 40 60 L 140 60 L 140 150 A 70 70 0 0 0 140 290 L 140 330 L 40 330 Z" fill="{MAG}" stroke="{MAG_D}" stroke-width="2"/>'
    b += f'<path d="M 460 60 L 360 60 L 360 150 A 70 70 0 0 1 360 290 L 360 330 L 460 330 Z" fill="{MAG}" stroke="{MAG_D}" stroke-width="2"/>'
    b += RECT(40, 330, 420, 40, MAG_D, MAG, 2)
    b += T(100, 230, 'N', 26, weight='bold') + T(400, 230, 'S', 26, weight='bold')
    b += f'<circle cx="250" cy="220" r="52" fill="#8a8f98" stroke="{INK}" stroke-width="2"/>'
    b += f'<rect x="214" y="168" width="72" height="104" rx="8" fill="#e0a070" stroke="{WIRE_D}" stroke-width="2" transform="rotate(25 250 220)"/>'
    b += f'<circle cx="250" cy="220" r="10" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
    b += f'<path d="M 250 210 q 8 -4 4 -10 q -6 -8 6 -12" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    b += L(250, 220, 250 + 145 * math.cos(math.radians(78)), 220 - 145 * math.sin(math.radians(78)), '#c0392b', 3)
    a1, a2 = math.radians(125), math.radians(55)
    b += f'<path d="M {250 + 150 * math.cos(a1):.1f} {220 - 150 * math.sin(a1):.1f} A 150 150 0 0 1 {250 + 150 * math.cos(a2):.1f} {220 - 150 * math.sin(a2):.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
    for k in range(11):
        t = math.radians(125 - k * 7); x0, y0 = 250 + 150 * math.cos(t), 220 - 150 * math.sin(t)
        b += L(x0, y0, 250 + 160 * math.cos(t), 220 - 160 * math.sin(t), INK, 1.4)
    b += L(220, 260, 220, 380, WIRE, 3) + L(280, 260, 280, 380, WIRE, 3)
    b += ARROW(170, 392, 215, 392, INK, 1.8, 9) + lab_I(192, 410) + ARROW(285, 392, 330, 392, INK, 1.8, 9)
    b += L(268, 200, 330, 130, INK, 1.1) + T(338, 130, 'نابض', 13, 'start')
    b += L(232, 250, 165, 300, INK, 1.1) + T(162, 304, 'ملف', 13, 'end')
    C('c3l2-o08-galv.svg', 500, 420, b)

    # محرك بسيط: حلقة بين قطبين، حلقة دائرية مقسومة (عاكس التيار)، فرشاتان، بطارية
    b = magnet(20, 60, 80, 160, 'N') + magnet(420, 60, 80, 160, 'S') + hfield(100, 420, [75, 120, 160, 205], 1, at=0.12)
    b += f'<polyline points="250,190 200,190 200,90 320,90 320,190 270,190" fill="none" stroke="{WIRE}" stroke-width="6" stroke-linejoin="round"/>'
    b += L(250, 190, 250, 250, WIRE, 5) + L(270, 190, 270, 250, WIRE, 5)
    b += f'<path d="M 256 250 A 22 22 0 0 0 256 294" fill="none" stroke="{INK}" stroke-width="6"/>'
    b += f'<path d="M 264 250 A 22 22 0 0 1 264 294" fill="none" stroke="{INK}" stroke-width="6"/>'
    b += RECT(212, 262, 14, 22, INK, '#555', 1) + RECT(294, 262, 14, 22, INK, '#555', 1)
    b += L(212, 273, 160, 273, INK, 2.2) + L(160, 273, 160, 340, INK, 2.2) + L(160, 340, 240, 340, INK, 2.2)
    b += battery(260, 340, vertical=False) + L(269, 340, 360, 340, INK, 2.2) + L(360, 340, 360, 273, INK, 2.2) + L(360, 273, 308, 273, INK, 2.2)
    b += L(285, 300, 330, 316, INK, 1.1) + T(334, 320, 'حلقة دائرية مقسومة', 13, 'start')
    b += L(219, 286, 190, 312, INK, 1.1) + T(186, 316, 'فرشاة', 13, 'end')
    C('c3l2-o08-motor.svg', 520, 360, b)

if __name__ == '__main__':
    o01(); o02(); o03(); o04(); o05(); o06(); o07(); o08()
