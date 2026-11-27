import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-2 القوى الناتجة عن المجالات المغناطيسية — الجزء b (الأهداف O09–O17): تحويل الجلفانومتر إلى أميتر وفولتمتر،
# والمحرك الكهربائي، والجسيمات المشحونة، والسلكان المتوازيان، وأنبوب الأشعة المهبطية، والتخزين المغناطيسي.
# اصطلاحات الفصل 3 كالكتاب: المجال المغناطيسي أخضر (خطوط وأسهم، × داخل الورقة و• خارجها)، القوة زرقاء ورمزها F مائل،
# السرعة حمراء ورمزها v مائل، التيار I قائم، B قائم. رمز الجلفانومتر دائرة فيها G كالشكلين 3-20 و3-32،
# والمقاومتان R مجزئ وR مضاعف كما في الشكل 3-20 (R مائل والحرف السفلي عربي).
import math

C_B = '#1f8a4c'          # أخضر المجال كالكتاب
G_FILL = '#d9d6ee'; PLUS = '#c0392b'

def _u(x1, y1, x2, y2):
    d = math.hypot(x2 - x1, y2 - y1); return (x2 - x1) / d, (y2 - y1) / d, d

def wires(*p): return ''.join(L(p[i][0], p[i][1], p[i + 1][0], p[i + 1][1], INK, 2.2) for i in range(len(p) - 1))
def node(x, y): return DOT(x, y, 4, INK)

def seg(x1, y1, x2, y2, comp=None, half=None):
    """سلك وفي منتصفه عنصر: 'R' مقاومة، 'G' جلفانومتر، 'bat' بطارية، 'lamp' مصباح، 'A' أميتر، 'V' فولتمتر."""
    if comp is None: return L(x1, y1, x2, y2, INK, 2.2)
    ux, uy, d = _u(x1, y1, x2, y2); nx, ny = -uy, ux; mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    h = half or {'R': 26, 'G': 17, 'bat': 13, 'lamp': 14, 'A': 15, 'V': 15}[comp]
    b = L(x1, y1, mx - h * ux, my - h * uy, INK, 2.2) + L(mx + h * ux, my + h * uy, x2, y2, INK, 2.2)
    P = lambda s, t: (mx + s * ux + t * nx, my + s * uy + t * ny)
    if comp == 'R':
        pts = [P(-h, 0)] + [P(-h + (k + 0.5) * 2 * h / 6, 9 * (1 if k % 2 == 0 else -1)) for k in range(6)] + [P(h, 0)]
        b += '<polyline points="' + ' '.join(f'{a:.1f},{c:.1f}' for a, c in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
    elif comp in ('G', 'A', 'V'):
        b += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{h}" fill="{G_FILL}" stroke="{INK}" stroke-width="2"/>' + T(mx, my + 6, comp, 17)
    elif comp == 'bat':
        for o, ln in zip([-9, -3, 3, 9], [16, 8, 16, 8]):
            a, c = P(o, -ln), P(o, ln); b += L(a[0], a[1], c[0], c[1], INK, 2.6 if ln == 16 else 3.2)
    elif comp == 'lamp':
        b += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="14" fill="#fff6d8" stroke="{INK}" stroke-width="2.2"/>'
        q = lambda s, t: '{:.1f} {:.1f}'.format(*P(s, t))
        b += (f'<path d="M {q(-14, 0)} C {q(-14, -15)} {q(-2, -14)} {q(1.8, 4)} C {q(3.5, 9.5)} {q(-3.5, 9.5)} {q(-1.8, 4)} '
              f'C {q(2, -14)} {q(14, -15)} {q(14, 0)}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    return b

def iarrow(x1, y1, x2, y2, lab='I', sub=None, dx=0, dy=-10):
    s = lab + (f'_{sub}' if sub else '')
    return ARROW(x1, y1, x2, y2, INK, 1.8, 9) + T((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, s, 16)

def Rlab(x, y, word, size=17, anchor='middle'):
    """R مائل وحرفه السفلي العربي (مجزئ/مضاعف) كالشكل 3-20."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{INK}" {MATHFONT} font-style="italic">R'
            f'<tspan dy="0.35em" font-size="{int(size * 0.72)}" font-style="normal" {FONT}>{word}</tspan></text>')

def term(x, y, sign):
    return DOT(x, y, 4.5, INK) + T(x + (-14 if sign == '+' else 14), y + 6, sign, 17, color=PLUS if sign == '+' else INK, weight='bold')

def cross(x, y, s=6, c=C_B): return L(x - s, y - s, x + s, y + s, c, 2.2) + L(x - s, y + s, x + s, y - s, c, 2.2)
def dot_out(x, y, c=C_B): return DOT(x, y, 4.2, c)
def field_grid(x0, y0, nx_, ny_, step, kind):
    return ''.join((cross if kind == 'in' else dot_out)(x0 + i * step, y0 + j * step) for i in range(nx_) for j in range(ny_))
def particle(x, y, sign, r=11):
    fill = '#f6d5d0' if sign == '+' else '#d5e3f6'
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="1.8"/>' + T(x, y + 5.5, '+' if sign == '+' else '−', 17, weight='bold')
def C(name, w, h, body): save(name, svg(w, h, body))

# ───────── O09 الأميتر
def o09():
    # الجلفانومتر مع مجزئ التيار على التوازي (كالشكل 3-20a)
    b = term(70, 250, '+') + term(330, 250, '−')
    b += wires((70, 250), (70, 70), (165, 70)) + seg(165, 70, 235, 70, 'G') + wires((235, 70), (330, 70), (330, 250))
    b += node(70, 160) + node(330, 160) + wires((70, 160), (160, 160)) + seg(160, 160, 240, 160, 'R') + wires((240, 160), (330, 160))
    b += Rlab(200, 140, 'مجزئ')
    b += iarrow(90, 95, 135, 95, 'I', 'm', 0, 22) + iarrow(90, 185, 135, 185, 'I', 's', 0, 22)
    C('c3l2-o09-ammeter.svg', 400, 290, b)
    # أربعة توصيلات للجلفانومتر مع مقاومة
    W = 230; b = ''
    cases = [('series', '0.05 Ω'), ('parallel', '50 kΩ'), ('parallel', '0.05 Ω'), ('series', '50 kΩ')]
    for k, (kind, val) in enumerate(cases):
        ox = k * W; b += T(ox + W / 2, 30, f'({k + 1})', 17, weight='bold')
        if kind == 'series':
            b += wires((ox + 25, 110), (ox + 45, 110)) + seg(ox + 45, 110, ox + 105, 110, 'G') + seg(ox + 105, 110, ox + 195, 110, 'R') + wires((ox + 195, 110), (ox + 210, 110))
            b += T(ox + 150, 145, val, 15)
            b += node(ox + 25, 110) + node(ox + 210, 110)
        else:
            b += wires((ox + 25, 115), (ox + 45, 115), (ox + 45, 75), (ox + 85, 75)) + seg(ox + 85, 75, ox + 145, 75, 'G') + wires((ox + 145, 75), (ox + 185, 75), (ox + 185, 115), (ox + 210, 115))
            b += wires((ox + 45, 115), (ox + 45, 155), (ox + 70, 155)) + seg(ox + 70, 155, ox + 160, 155, 'R') + wires((ox + 160, 155), (ox + 185, 155), (ox + 185, 115))
            b += T(ox + 115, 185, val, 15) + node(ox + 45, 115) + node(ox + 185, 115) + node(ox + 25, 115) + node(ox + 210, 115)
    for k in range(1, 4): b += L(k * W, 15, k * W, 195, GRID, 1.5)
    C('c3l2-o09-four.svg', 4 * W, 205, b)

# ───────── O10 الفولتمتر
def o10():
    # الجلفانومتر مع المضاعف على التوالي (كالشكل 3-20b)
    b = term(70, 250, '+') + term(300, 250, '−')
    b += wires((300, 250), (300, 70), (235, 70)) + seg(235, 70, 165, 70, 'G') + wires((165, 70), (70, 70)) + seg(70, 70, 70, 250, 'R', 34)
    b += Rlab(100, 168, 'مضاعف', anchor='start') + iarrow(90, 130, 90, 95, 'I', None, 14, 4)
    C('c3l2-o10-voltmeter.svg', 370, 290, b)
    # مخطط تحويل (كالشكل 3-33): G ثم مقاومة على التوالي
    b = wires((60, 70), (60, 105)) + seg(60, 105, 60, 155, 'G') + wires((60, 155), (60, 200), (230, 200))
    b += wires((60, 70), (110, 70)) + seg(110, 70, 190, 70, 'R') + wires((190, 70), (230, 70))
    b += ARROW(215, 70, 240, 70, INK, 2, 9) + ARROW(215, 200, 240, 200, INK, 2, 9)
    C('c3l2-o10-device.svg', 270, 240, b)
    # دائرة: بطارية ومصباح، وفولتمتر بين طرفي المصباح
    b = seg(60, 230, 60, 70, 'bat') + T(30, 160, '12 V', 15, 'end' if False else 'middle') + wires((60, 70), (260, 70), (260, 100))
    b += seg(260, 100, 260, 200, 'lamp') + wires((260, 200), (260, 230), (60, 230)) + node(260, 100) + node(260, 200)
    b += wires((260, 100), (360, 100)) + seg(360, 100, 360, 200, 'V') + wires((360, 200), (260, 200))
    C('c3l2-o10-circuit.svg', 420, 260, b)

# ───────── O11 المحرك
def magnet_block(x, y, w, h, label, fill):
    return RECT(x, y, w, h, INK, fill, 2) + T(x + w / 2, y + h / 2 + 8, label, 24, weight='bold')

def o11():
    # مخطط المحرك بأجزاء مرقّمة: 1 قطبا المغناطيس، 2 الملف، 3 الحلقة المقسومة، 4 الفرشاة
    b = magnet_block(30, 60, 90, 150, 'N', '#d6dde8') + magnet_block(400, 60, 90, 150, 'S', '#d6dde8')
    for yy in (90, 120, 150, 180): b += ARROW(122, yy, 396, yy, C_B, 1.6, 8)
    b += T(368, 82, 'B', 17, color=C_B)
    # الملف (مستطيل) ومحور الدوران
    b += f'<rect x="185" y="95" width="150" height="80" fill="none" stroke="#b5651d" stroke-width="5"/>'
    b += L(260, 175, 260, 255, MUTED, 2.5, '6 4')
    # الحلقة المقسومة (نصفان) والفرشاتان
    b += f'<path d="M 247 225 A 13 13 0 0 1 257 212" fill="none" stroke="#7a7f8a" stroke-width="7"/>'
    b += f'<path d="M 263 212 A 13 13 0 0 1 273 225 A 13 13 0 0 1 263 238" fill="none" stroke="#7a7f8a" stroke-width="7"/>'
    b += f'<path d="M 257 238 A 13 13 0 0 1 247 225" fill="none" stroke="#7a7f8a" stroke-width="7"/>'
    b += L(250, 175, 252, 212, '#b5651d', 3) + L(270, 175, 268, 212, '#b5651d', 3)
    b += RECT(222, 218, 14, 14, INK, '#444', 1) + RECT(284, 218, 14, 14, INK, '#444', 1)
    b += wires((222, 225), (170, 225), (170, 300), (230, 300)) + seg(230, 300, 290, 300, 'bat') + wires((290, 300), (350, 300), (350, 225), (298, 225))
    def num(x, y, n, lx, ly):
        return L(x, y, lx, ly, MUTED, 1.2) + f'<circle cx="{lx}" cy="{ly}" r="12" fill="#fff" stroke="{INK}" stroke-width="1.5"/>' + T(lx, ly + 5, str(n), 15, weight='bold')
    b += num(75, 210, 1, 75, 245) + num(335, 120, 2, 380, 250) + num(273, 228, 3, 300, 262) + num(229, 232, 4, 200, 262)
    C('c3l2-o11-motor.svg', 520, 330, b)
    # منظر جانبي للملف في وضعين: (a) أفقي، (b) رأسي
    b = ''
    for k, ang in enumerate((0, 90)):
        ox = k * 300; cx, cy = ox + 150, 165
        b += T(cx, 30, '(a)' if k == 0 else '(b)', 17, weight='bold')
        for yy in (70, 260): b += ARROW(ox + 25, yy, ox + 275, yy, C_B, 1.6, 8)
        b += T(ox + 262, 58, 'B', 16, color=C_B)
        a = math.radians(ang); r = 70
        x1, y1 = cx - r * math.cos(a), cy + r * math.sin(a); x2, y2 = cx + r * math.cos(a), cy - r * math.sin(a)
        b += L(x1, y1, x2, y2, '#b5651d', 4, '7 5') + DOT(cx, cy, 3.5, MUTED)
        # الضلع الأيسر/السفلي: تيار خارج الورقة، والآخر داخلها
        b += f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="11" fill="#fff" stroke="{INK}" stroke-width="2"/>' + DOT(x1, y1, 3.2, INK)
        b += f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="11" fill="#fff" stroke="{INK}" stroke-width="2"/>' + L(x2 - 5, y2 - 5, x2 + 5, y2 + 5, INK, 2) + L(x2 - 5, y2 + 5, x2 + 5, y2 - 5, INK, 2)
        # القوة على تيار خارج الورقة في مجال نحو اليمين: لأعلى؛ وعلى تيار داخل الورقة: لأسفل
        o = 0 if ang == 0 else 22
        b += ARROW(x1 + o, y1 - 13, x1 + o, y1 - 58, C_FORCE, 2.6) + T(x1 + o + 13, y1 - 45, 'F', 17, color=C_FORCE, italic=True)
        b += ARROW(x2 + o, y2 + 13, x2 + o, y2 + 58, C_FORCE, 2.6) + T(x2 + o + 13, y2 + 50, 'F', 17, color=C_FORCE, italic=True)
    b += L(300, 20, 300, 290, GRID, 1.5)
    C('c3l2-o11-sides.svg', 600, 300, b)

# ───────── O12 العوامل (زوايا السرعة مع المجال)
def o12():
    b = ''
    for yy in (40, 120, 200, 280): b += ARROW(20, yy, 660, yy, C_B, 1.5, 8)
    b += T(645, 30, 'B', 17, color=C_B)
    pts = [(90, 80, 0, '1'), (250, 240, 90, '2'), (420, 80, 30, '3'), (590, 240, 180, '4')]
    for x, y, ang, n in pts:
        a = math.radians(ang); b += particle(x, y, '+')
        b += ARROW(x + 13 * math.cos(a), y - 13 * math.sin(a), x + 75 * math.cos(a), y - 75 * math.sin(a), C_VEL, 2.6)
        lx, ly = x + 88 * math.cos(a), y - 88 * math.sin(a); b += T(lx + (0 if ang == 90 else 0), ly + 6, 'v', 17, color=C_VEL, italic=True)
        b += T(x - 22, y + 30, f'({n})', 15, weight='bold')
    b += f'<path d="M 450 80 A 30 30 0 0 0 {420 + 30 * math.cos(math.radians(30)):.1f} {80 - 30 * math.sin(math.radians(30)):.1f}" fill="none" stroke="{INK}" stroke-width="1.3"/>' + T(462, 72, '30°', 13)
    C('c3l2-o12-angles.svg', 680, 300, b)

# ───────── O13 اتجاه القوة على جسيم مشحون
def o13():
    # بروتون يتحرك نحو اليمين في مجال داخل الورقة
    b = field_grid(40, 40, 7, 5, 50, 'in') + T(368, 36, 'B', 17, color=C_B)
    b += particle(115, 115, '+') + ARROW(128, 115, 215, 115, C_VEL, 2.8) + T(228, 121, 'v', 18, color=C_VEL, italic=True)
    C('c3l2-o13-proton.svg', 400, 280, b)
    # إلكترون يتحرك إلى أعلى في مجال خارج الورقة
    b = field_grid(40, 40, 7, 5, 50, 'out') + T(368, 36, 'B', 17, color=C_B)
    b += particle(165, 215, '-') + ARROW(165, 202, 165, 112, C_VEL, 2.8) + T(181, 122, 'v', 18, color=C_VEL, italic=True)
    C('c3l2-o13-electron.svg', 400, 280, b)
    # بروتون وإلكترون يدخلان المجال نفسه بالسرعة نفسها نحو اليمين
    b = field_grid(230, 40, 6, 6, 46, 'in') + T(500, 32, 'B', 17, color=C_B)
    b += particle(60, 90, '+') + ARROW(73, 90, 150, 90, C_VEL, 2.8) + T(162, 96, 'v', 18, color=C_VEL, italic=True) + T(60, 122, 'بروتون', 14)
    b += particle(60, 230, '-') + ARROW(73, 230, 150, 230, C_VEL, 2.8) + T(162, 236, 'v', 18, color=C_VEL, italic=True) + T(60, 262, 'إلكترون', 14)
    b += L(215, 25, 215, 290, MUTED, 1.2, '5 4')
    C('c3l2-o13-pair.svg', 520, 300, b)

# ───────── O14 السلكان المتوازيان
def wire_v(x, y1, y2, up, lab):
    b = f'<rect x="{x - 5}" y="{y1}" width="10" height="{y2 - y1}" fill="#d9a07a" stroke="#9c5b34" stroke-width="1.2"/>'
    ya, yb = (y2 - 20, y2 - 70) if up else (y2 - 70, y2 - 20)
    b += ARROW(x - 20, ya, x - 20, yb, INK, 2, 9) + T(x - 33, (ya + yb) / 2 + 5, 'I', 16)
    b += T(x, y1 - 10, lab, 15, weight='bold')
    return b

def o14():
    b = wire_v(120, 40, 280, True, '(1)') + wire_v(300, 40, 280, True, '(2)')
    b += L(130, 160, 290, 160, MUTED, 1.2, '5 4') + T(210, 152, 'd', 16, italic=True)
    C('c3l2-o14-same.svg', 400, 300, b)
    b = wire_v(120, 40, 280, True, '(1)') + wire_v(300, 40, 280, False, '(2)')
    b += L(130, 160, 290, 160, MUTED, 1.2, '5 4') + T(210, 152, 'd', 16, italic=True)
    C('c3l2-o14-opp.svg', 400, 300, b)
    # ثلاثة أسلاك متوازية متساوية التباعد تيارات متساوية في الاتجاه نفسه
    b = wire_v(90, 40, 260, True, '(1)') + wire_v(220, 40, 260, True, '(2)') + wire_v(350, 40, 260, True, '(3)')
    b += L(100, 150, 210, 150, MUTED, 1.2, '5 4') + T(155, 142, 'd', 16, italic=True) + L(230, 150, 340, 150, MUTED, 1.2, '5 4') + T(285, 142, 'd', 16, italic=True)
    C('c3l2-o14-three.svg', 420, 280, b)

# ───────── O15 أنبوب الأشعة المهبطية
def o15():
    b = ''
    # غلاف الأنبوب: عنق ثم قمع ثم شاشة
    b += f'<path d="M 40 130 L 230 130 L 470 40 L 470 300 L 230 210 L 40 210 Z" fill="#eef2f6" stroke="{INK}" stroke-width="2"/>'
    b += RECT(470, 30, 16, 280, INK, '#bfe3c8', 2)        # الشاشة المطلية بطبقة فوسفورية
    b += RECT(55, 150, 22, 40, INK, '#9aa3b2', 1.5)        # الكاثود
    b += RECT(110, 145, 10, 50, INK, '#9aa3b2', 1.5) + RECT(135, 145, 10, 50, INK, '#9aa3b2', 1.5)  # الأنود
    b += f'<ellipse cx="250" cy="113" rx="26" ry="11" fill="#c9a26b" stroke="{INK}" stroke-width="1.5"/>' + f'<ellipse cx="250" cy="227" rx="26" ry="11" fill="#c9a26b" stroke="{INK}" stroke-width="1.5"/>'
    b += L(78, 170, 250, 170, C_VEL, 2.2) + ARROW(250, 170, 468, 95, C_VEL, 2.2)
    def num(x, y, n, lx, ly):
        return L(x, y, lx, ly, MUTED, 1.2) + f'<circle cx="{lx}" cy="{ly}" r="12" fill="#fff" stroke="{INK}" stroke-width="1.5"/>' + T(lx, ly + 5, str(n), 15, weight='bold')
    b += num(66, 190, 1, 66, 270) + num(140, 145, 2, 140, 75) + num(250, 238, 3, 250, 300) + num(486, 250, 4, 525, 250)
    C('c3l2-o15-crt.svg', 560, 330, b)
    # منظر الشاشة من الأمام: القطب الشمالي أعلى والجنوبي أسفل، والحزمة خارجة نحو الناظر
    b = RECT(110, 70, 240, 200, INK, '#e9f4ec', 2)
    b += magnet_block(170, 15, 120, 45, 'N', '#d6dde8') + magnet_block(170, 280, 120, 45, 'S', '#d6dde8')
    b += f'<circle cx="230" cy="170" r="12" fill="#fff" stroke="{C_VEL}" stroke-width="2.2"/>' + DOT(230, 170, 3.5, C_VEL)
    b += T(268, 176, 'v', 17, color=C_VEL, italic=True, anchor='start')
    b += T(40, 176, 'يسار', 14) + T(420, 176, 'يمين', 14)
    C('c3l2-o15-poles.svg', 460, 340, b)

# ───────── O16 التخزين المغناطيسي
def bands(name, dirs, groups=True, w=None):
    n = len(dirs); bw = 70; x0 = 30; W = w or (x0 * 2 + n * bw); b = ''
    for i, d in enumerate(dirs):
        x = x0 + i * bw; b += RECT(x, 40, bw, 70, INK, '#f6e6cc', 1.5)
        a, c = (x + 14, x + bw - 14) if d == '→' else (x + bw - 14, x + 14)
        b += ARROW(a, 62, c, 62, C_B, 2.2, 8) + ARROW(a, 88, c, 88, C_B, 2.2, 8)
    if groups:
        for k in range(n // 2):
            xa = x0 + 2 * k * bw + 6; xb = xa + 2 * bw - 12
            b += L(xa, 125, xb, 125, INK, 1.6) + L(xa, 118, xa, 125, INK, 1.6) + L(xb, 118, xb, 125, INK, 1.6)
            b += T((xa + xb) / 2, 148, f'bit {k + 1}', 14)
    C(name, W, 165, b)

def o16():
    bands('c3l2-o16-bands.svg', ['→', '→', '←', '→', '←', '→', '←', '←'])
    bands('c3l2-o16-bands2.svg', ['←', '→', '←', '←', '→', '←', '→', '→'])

# ───────── O17 قيم المسائل
def o17():
    # أميتر: جلفانومتر 1.0 mA و50 Ω، ومجزئ مجهول
    b = term(70, 230, '+') + term(330, 230, '−')
    b += wires((70, 230), (70, 70), (165, 70)) + seg(165, 70, 235, 70, 'G') + wires((235, 70), (330, 70), (330, 230))
    b += node(70, 150) + node(330, 150) + wires((70, 150), (160, 150)) + seg(160, 150, 240, 150, 'R') + wires((240, 150), (330, 150))
    b += Rlab(200, 132, 'مجزئ')
    C('c3l2-o17-shunt.svg', 400, 260, b)
    b = term(70, 230, '+') + term(330, 230, '−')
    b += wires((330, 230), (330, 70), (235, 70)) + seg(235, 70, 165, 70, 'G') + wires((165, 70), (70, 70)) + seg(70, 70, 70, 230, 'R', 34)
    b += Rlab(100, 156, 'مضاعف', anchor='start')
    C('c3l2-o17-mult.svg', 400, 260, b)

if __name__ == '__main__':
    o09(); o10(); o11(); o12(); o13(); o14(); o15(); o16(); o17()
