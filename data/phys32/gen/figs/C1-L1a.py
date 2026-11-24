import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 1-1 (الأهداف O01–O10): دوائر كهربائية برموز الكتاب (الشكل 1-5)
import math
FILLC = '#e4e2f3'  # تعبئة دوائر الأميتر والفولتمتر والمصباح والمحرك كما في الكتاب
W = 2.2

def _sym(kind, closed=False):
    """رمز العنصر في إحداثيات محلية: محوره x من -H إلى +H، ويُرسم السلك حتى طرفيه."""
    b = ''
    if kind == 'R':
        xs = [-21 + 7 * k for k in range(7)]
        pts = [(-26, 0), (-21, 0)] + [(-17.5 + 7 * k, -8 if k % 2 == 0 else 8) for k in range(6)] + [(21, 0), (26, 0)]
        b += '<polyline points="' + ' '.join(f'{x},{y}' for x, y in pts) + f'" fill="none" stroke="{INK}" stroke-width="{W}" stroke-linejoin="round"/>'
    elif kind == 'VR':
        b += _sym('R')
        b += L(0, -26, 0, -14, INK, 1.8) + f'<polygon points="0,-9 -4.5,-17 4.5,-17" fill="{INK}"/>' + L(0, -26, 26, -26, INK, 1.8) + L(26, -26, 26, 0, INK, 1.8)
    elif kind == 'B':  # بطارية من خليتين: الخط الأطول (الموجب) أولًا
        b += L(-26, 0, -9, 0, INK, W) + L(9, 0, 26, 0, INK, W)
        for x, ln, w in ((-9, 15, 2.2), (-3, 8, 4), (3, 15, 2.2), (9, 8, 4)):
            b += L(x, -ln, x, ln, INK, w)
    elif kind == 'B1':  # خلية واحدة
        b += L(-26, 0, -4, 0, INK, W) + L(4, 0, 26, 0, INK, W) + L(-4, -15, -4, 15, INK, 2.2) + L(4, -8, 4, 8, INK, 4)
    elif kind in ('A', 'V'):
        b += L(-26, 0, -14, 0, INK, W) + L(14, 0, 26, 0, INK, W) + f'<circle cx="0" cy="0" r="14" fill="{FILLC}" stroke="{INK}" stroke-width="1.8"/>'
    elif kind == 'L':
        b += L(-26, 0, -14, 0, INK, W) + L(14, 0, 26, 0, INK, W) + f'<circle cx="0" cy="0" r="14" fill="{FILLC}" stroke="{INK}" stroke-width="1.8"/>'
        b += f'<path d="M -14 0 L -8 0 C -8 -10 8 -10 8 0 C 8 7 -2 7 -2 0 C -2 -4 4 -4 4 0 M 8 0 L 14 0" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    elif kind == 'M':
        b += L(-26, 0, -14, 0, INK, W) + L(14, 0, 26, 0, INK, W) + f'<circle cx="0" cy="0" r="14" fill="{FILLC}" stroke="{INK}" stroke-width="1.8"/>'
        b += L(-6, -10, -12, -17, INK, 1.8)
    elif kind == 'S':
        b += L(-26, 0, -13, 0, INK, W) + L(13, 0, 26, 0, INK, W) + DOT(-13, 0, 2.6) + DOT(13, 0, 2.6)
        b += L(-13, 0, 15, -4, INK, W) if closed else L(-13, 0, 14, -12, INK, W)  # المغلق: ذراع مائلة قليلًا تستقر على النقطة اليمنى (تمييزًا لها عن نقاط التوصيل)
    elif kind == 'F':
        b += L(-26, 0, -12, 0, INK, W) + L(12, 0, 26, 0, INK, W)
        b += f'<path d="M -12 0 C -12 -13 0 -13 0 0 C 0 13 12 13 12 0" fill="none" stroke="{INK}" stroke-width="{W}"/>'
    elif kind == 'C':
        b += L(-26, 0, -5, 0, INK, W) + L(5, 0, 26, 0, INK, W) + L(-5, -14, -5, 14, INK, 2.4) + L(5, -14, 5, 14, INK, 2.4)
    elif kind == 'COIL':
        b += L(-26, 0, -18, 0, INK, W) + L(18, 0, 26, 0, INK, W)
        d = 'M -18 0 ' + ' '.join(f'A 4.5 7 0 1 1 {-18 + 9 * (k + 1) * 0.8:.1f} 0' for k in range(5))
        b += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.8"/>'
    elif kind == 'GAP':
        b += L(-26, 0, -8, 0, INK, W)
    elif kind == 'W':
        b += L(-26, 0, 26, 0, INK, W)
    return b

def comp(kind, cx, cy, vertical=False, flip=False, closed=False, text=''):
    """عنصر مركزه (cx, cy) وطوله 52 px. vertical: من أعلى إلى أسفل؛ flip يعكس الاتجاه (لجعل الموجب في الأعلى مثلًا)."""
    tr = f'translate({cx:.1f} {cy:.1f})' + (' rotate(90)' if vertical else '') + (' scale(-1 1)' if flip else '')
    g = f'<g transform="{tr}">{_sym(kind, closed)}</g>'
    if kind in ('A', 'V'): g += T(cx, cy + 5.5, kind, 15, color=INK)
    return g

def edge(p, q, kinds, **kw):
    """يقسم السلك من p إلى q قطعًا متساوية، ويضع في منتصف كل قطعة عنصرًا (None = سلك فقط). يعيد المراكز."""
    (x1, y1), (x2, y2) = p, q; n = len(kinds); b = ''; centers = []
    vertical = abs(x2 - x1) < 1e-6
    flip = (y2 < y1) if vertical else (x2 < x1)
    for k, kind in enumerate(kinds):
        ax, ay = x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n
        bx, by = x1 + (x2 - x1) * (k + 1) / n, y1 + (y2 - y1) * (k + 1) / n
        cx, cy = (ax + bx) / 2, (ay + by) / 2; centers.append((cx, cy))
        if kind is None or kind == 'W': b += L(ax, ay, bx, by, INK, W); continue
        if kind == 'GAP':
            ext = 26
            # سلك ينقطع قبل الوصول: يرسم نصفه الأول فقط
            b += L(ax, ay, cx - (ext if not vertical else 0) * (1 if not flip else -1), cy - (ext if vertical else 0) * (1 if not flip else -1), INK, W)
            continue
        if vertical: b += L(ax, ay, cx, cy - 26 if not flip else cy + 26, INK, W) + L(cx, cy + 26 if not flip else cy - 26, bx, by, INK, W)
        else: b += L(ax, ay, cx - 26 if not flip else cx + 26, cy, INK, W) + L(cx + 26 if not flip else cx - 26, cy, bx, by, INK, W)
        b += comp(kind, cx, cy, vertical, flip, kw.get('closed', False))
    return b, centers

def battery_left(x, y1, y2, kind='B', label=None, plus=True):
    """بطارية على الضلع الأيسر، الموجب (الخط الأطول) في الأعلى كما في الكتاب."""
    b, c = edge((x, y1), (x, y2), [None, kind, None]); cx, cy = c[1]
    if plus: b += T(cx + 13, cy - 16, '+', 15, color=RED) + T(cx + 13, cy + 27, '−', 15, color=INK)
    if label: b += T(cx + 22, cy + 5, label, 15, 'start')
    return b, (cx, cy)

def cur_arrow(x1, y, x2, label='I'):
    # يُستدعى بـ y = Y1 + 18؛ يُرسم السهم داخل الدائرة فوق السلك السفلي (كالشكل 1-3) حتى لا يلامس الحرفُ السلك
    y -= 36
    return ARROW(x1, y, x2, y, INK, 1.6, 9) + T((x1 + x2) / 2, y - 9, label, 15, italic=True)

def num(x, y, n): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#fff" stroke="{MUTED}" stroke-width="1.3"/>' + T(x, y + 5, str(n), 14, color=INK, weight='bold')
def junction(x, y): return DOT(x, y, 4)

# ---------------- O02 ----------------
def o02_numbered():
    # 1 بطارية، 2 مفتاح، 3 مقاومة متغيرة، 4 محرك (كالشكل 1-11)
    X0, X1, Y0, Y1 = 70, 330, 50, 250; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1, plus=True); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'M', None]); b += s; mx, my = c[1]
    s, c = edge((X1, Y0), (X1, Y1), [None, 'VR', None]); b += s; rx, ry = c[1]
    s, c = edge((X1, Y1), (X0, Y1), [None, 'S', None]); b += s; sx, sy = c[1]
    b += num(bx - 34, by, 1) + num(sx, sy + 30, 2) + num(rx + 50, ry, 3) + num(mx, my - 34, 4)
    save('c1l1-o02-numbered.svg', svg(400, 300, b))

def o02_lamp():
    # 1 بطارية، 2 منصهر، 3 مصباح، 4 مفتاح مفتوح
    X0, X1, Y0, Y1 = 70, 350, 50, 240; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'F', 'L', None]); b += s; (fx, fy), (lx, ly) = c[1], c[2]
    s, c = edge((X1, Y0), (X1, Y1), [None]); b += s
    s, c = edge((X1, Y1), (X0, Y1), [None, 'S', None]); b += s; sx, sy = c[1]
    b += num(bx - 34, by, 1) + num(fx, fy - 34, 2) + num(lx, ly - 34, 3) + num(sx, sy + 30, 4)
    save('c1l1-o02-lamp.svg', svg(420, 290, b))

# ---------------- O03 ----------------
def o03_lamp_meters():
    X0, X1, Y0, Y1 = 80, 380, 120, 290; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1, label='6.0 V'); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'L', None]); b += s; lx, ly = c[1]
    s, c = edge((X1, Y0), (X1, Y1), [None, 'A', None]); b += s; ax, ay = c[1]
    s, c = edge((X1, Y1), (X0, Y1), [None]); b += s
    # فولتمتر بين طرفي المصباح
    j1, j2 = lx - 60, lx + 60
    s, c = edge((j1, Y0), (j1, 50), [None]); b += s
    s, c = edge((j1, 50), (j2, 50), [None, 'V', None]); b += s; vx, vy = c[1]
    s, c = edge((j2, 50), (j2, Y0), [None]); b += s
    b += junction(j1, Y0) + junction(j2, Y0)
    b += T(vx, vy - 22, '6.0 V', 15) + T(ax - 24, ay + 5, '0.25 A', 15, 'end') + T(lx, ly + 34, 'مصباح', 14, color=MUTED)
    b += cur_arrow(250, Y1 + 18, 200)
    save('c1l1-o03-lamp-meters.svg', svg(460, 330, b))

def o03_cells():
    X0, X1, Y0, Y1 = 60, 470, 60, 220; b = ''
    s, c = edge((X0, Y0), (X1, Y0), [None, 'B1', 'B1', 'B1', 'B1', None]); b += s
    for cx, cy in c[1:5]: b += T(cx, cy - 24, '1.5 V', 14)
    s, c = edge((X1, Y0), (X1, Y1), [None, 'A', None]); b += s; ax, ay = c[1]
    s, c = edge((X1, Y1), (X0, Y1), [None, 'L', None]); b += s; lx, ly = c[1]
    s, c = edge((X0, Y1), (X0, Y0), [None]); b += s
    b += T(ax - 24, ay + 5, '0.40 A', 15, 'end') + T(lx, ly + 34, 'مصباح', 14, color=MUTED)
    save('c1l1-o03-cells.svg', svg(530, 270, b))

def o03_motor():
    X0, X1, Y0, Y1 = 80, 360, 50, 230; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1, label='9.0 V'); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'A', None]); b += s; ax, ay = c[1]
    s, c = edge((X1, Y0), (X1, Y1), [None, 'M', None]); b += s; mx, my = c[1]
    s, c = edge((X1, Y1), (X0, Y1), [None]); b += s
    b += T(ax, ay - 22, '0.30 A', 15) + T(mx + 24, my + 5, 'محرك', 14, 'start', MUTED)
    b += cur_arrow(240, Y1 + 18, 190)
    save('c1l1-o03-motor.svg', svg(440, 270, b))

# ---------------- O05 ----------------
def o05_meters():
    X0, X1, Y0, Y1 = 80, 380, 120, 290; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'R', None]); b += s; rx, ry = c[1]
    s, c = edge((X1, Y0), (X1, Y1), [None, 'A', None]); b += s; ax, ay = c[1]
    s, c = edge((X1, Y1), (X0, Y1), [None]); b += s
    j1, j2 = rx - 60, rx + 60
    b += edge((j1, Y0), (j1, 50), [None])[0] + edge((j2, 50), (j2, Y0), [None])[0]
    s, c = edge((j1, 50), (j2, 50), [None, 'V', None]); b += s; vx, vy = c[1]
    b += junction(j1, Y0) + junction(j2, Y0)
    b += T(vx, vy - 22, '9.0 V', 15) + T(ax - 24, ay + 5, '0.60 A', 15, 'end') + T(rx, ry + 30, 'R', 16, italic=True)
    b += cur_arrow(250, Y1 + 18, 200)
    save('c1l1-o05-meters.svg', svg(460, 330, b))

def o05_e1():
    X0, X1, Y0, Y1 = 80, 300, 50, 250; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1, label='30 V'); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'A', None]); b += s
    s, c = edge((X1, Y0), (X1, Y1), [None, 'R', None]); b += s; rx, ry = c[1]
    s, c = edge((X1, Y1), (X0, Y1), [None]); b += s
    b += T(rx - 22, ry + 5, '12 Ω', 15, 'end')
    # فولتمتر موصول بين طرفي المقاومة
    XV = 400
    b += edge((X1, Y0), (XV, Y0), [None])[0] + edge((XV, Y1), (X1, Y1), [None])[0]
    b += edge((XV, Y0), (XV, Y1), [None, 'V', None])[0] + junction(X1, Y0) + junction(X1, Y1)
    b += cur_arrow(210, Y1 + 18, 160)
    save('c1l1-o05-e1.svg', svg(460, 290, b))

def o05_e3():
    X0, X1, Y0, Y1 = 80, 380, 50, 220; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1, label='12 V'); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'L', None, 'R', None]); b += s; (lx, ly), (rx, ry) = c[1], c[3]
    s, c = edge((X1, Y0), (X1, Y1), [None, 'A', None]); b += s
    b += edge((X1, Y1), (X0, Y1), [None])[0]
    b += T(lx, ly - 24, '40 Ω', 15) + T(lx, ly + 34, 'مصباح', 14, color=MUTED) + T(rx, ry - 20, 'R', 16, italic=True)
    b += cur_arrow(250, Y1 + 18, 200)
    save('c1l1-o05-e3.svg', svg(460, 260, b))

# ---------------- O06 ----------------
def wire_rod(x, y, length, d, label, color='#b87333'):
    r = d / 2
    return (f'<rect x="{x}" y="{y - r}" width="{length}" height="{d}" rx="{r}" fill="{color}" stroke="#6e4220" stroke-width="1.2"/>'
            + T(x - 14, y + 5, label, 17, 'end', italic=True))

def o06_length():
    b = wire_rod(70, 60, 360, 10, 'X') + wire_rod(70, 140, 180, 10, 'Y')
    b += L(70, 85, 430, 85, MUTED, 1) + L(70, 80, 70, 90, MUTED, 1) + L(430, 80, 430, 90, MUTED, 1) + T(250, 104, '2.0 m', 14, color=MUTED)
    b += L(70, 165, 250, 165, MUTED, 1) + L(70, 160, 70, 170, MUTED, 1) + L(250, 160, 250, 170, MUTED, 1) + T(160, 184, '1.0 m', 14, color=MUTED)
    save('c1l1-o06-length.svg', svg(470, 200, b))

def o06_four():
    b = ''
    rows = [('X', 1.0, 14), ('Y', 2.0, 6), ('Z', 1.0, 6), ('W', 2.0, 14)]
    for k, (lab, ln, d) in enumerate(rows):
        y = 50 + k * 62; px = 160 * ln
        b += wire_rod(70, y, px, d, lab) + T(70 + px + 12, y + 5, f'{ln:.1f} m', 14, 'start', MUTED)
    save('c1l1-o06-four.svg', svg(470, 270, b))

# ---------------- O07 ----------------
def simple_loop(name, vlabel, rlabel, areading=None, w=380, h=260, title=None, ox=0, oy=0, out=True):
    X0, X1, Y0, Y1 = 70 + ox, 300 + ox, 50 + oy, 220 + oy; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1, label=vlabel); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'A', None]); b += s; ax, ay = c[1]
    s, c = edge((X1, Y0), (X1, Y1), [None, 'R', None]); b += s; rx, ry = c[1]
    b += edge((X1, Y1), (X0, Y1), [None])[0]
    b += T(rx - 22, ry + 5, rlabel, 15, 'end')
    if areading: b += T(ax, ay - 22, areading, 15)
    b += cur_arrow((X0 + X1) / 2 + 25, Y1 + 18, (X0 + X1) / 2 - 25)
    if title: b += T((X0 + X1) / 2, Y0 - 24, title, 15, weight='bold')
    if out: save(name, svg(w, h, b))
    return b

def o07_three():
    b = simple_loop('', '9.0 V', '30 Ω', title='الدائرة 1', ox=-20, oy=20, out=False)
    b += simple_loop('', '9.0 V', '15 Ω', title='الدائرة 2', ox=270, oy=20, out=False)
    b += simple_loop('', '18 V', '30 Ω', title='الدائرة 3', ox=560, oy=20, out=False)
    save('c1l1-o07-three.svg', svg(880, 290, b))

# ---------------- O08 ----------------
def o08_dimmer():
    X0, X1, Y0, Y1 = 80, 380, 50, 230; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'S', None, 'L', None]); b += s; (sx, sy), (lx, ly) = c[1], c[3]
    b += edge((X1, Y0), (X1, Y1), [None])[0]
    s, c = edge((X1, Y1), (X0, Y1), [None, 'VR', None]); b += s; vx, vy = c[1]
    b += T(lx, ly - 24, 'مصباح', 14, color=MUTED) + T(sx, sy - 24, 'مفتاح', 14, color=MUTED)
    save('c1l1-o08-dimmer.svg', svg(460, 270, b))

def o08_motor():
    X0, X1, Y0, Y1 = 80, 360, 50, 230; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1, label='24 V'); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'M', None]); b += s; mx, my = c[1]
    s, c = edge((X1, Y0), (X1, Y1), [None, 'A', None]); b += s
    s, c = edge((X1, Y1), (X0, Y1), [None, 'VR', None]); b += s
    b += T(mx, my - 24, 'محرك', 14, color=MUTED)
    save('c1l1-o08-motor.svg', svg(440, 270, b))

# ---------------- O10 ----------------
def o10_symbols():
    b = ''
    for k, kind in enumerate(['F', 'VR', 'C', 'COIL']):
        x = 70 + k * 110; b += comp(kind, x, 80) + num(x, 140, k + 1)
    save('c1l1-o10-symbols.svg', svg(450, 170, b))

def mini(kind_top, kind_right, kind_bottom, ox, oy, n, closed=True):
    X0, X1, Y0, Y1 = ox + 30, ox + 200, oy + 40, oy + 170; b = ''
    s, _ = battery_left(X0, Y0, Y1); b += s
    b += edge((X0, Y0), (X1, Y0), [None, kind_top, None])[0]
    b += edge((X1, Y0), (X1, Y1), [None, kind_right, None])[0]
    b += edge((X1, Y1), (X0, Y1), [None, kind_bottom, None], closed=closed)[0]
    b += T(ox + 115, oy + 205, f'المخطط {n}', 15, weight='bold')
    return b

def o10_choose():
    b = mini('L', 'A', 'S', 0, 0, 1, closed=True) + mini('L', 'V', 'S', 250, 0, 2, closed=True)
    b += mini('L', 'A', 'S', 0, 230, 3, closed=False) + mini('R', 'A', 'S', 250, 230, 4, closed=True)
    save('c1l1-o10-choose.svg', svg(500, 450, b))

def o10_gap():
    X0, X1, Y0, Y1 = 80, 360, 50, 230; b = ''
    s, _ = battery_left(X0, Y0, Y1); b += s
    b += edge((X0, Y0), (X1, Y0), [None, 'S', None], closed=True)[0]
    b += edge((X1, Y0), (X1, Y1), [None, 'L', None])[0]
    # السلك السفلي يتوقف قبل الوصول إلى الطرف السالب
    b += L(X1, Y1, X0 + 70, Y1, INK, W)
    save('c1l1-o10-gap.svg', svg(440, 270, b))

def o10_wrong():
    X0, X1, Y0, Y1 = 80, 380, 50, 230; b = ''
    s, (bx, by) = battery_left(X0, Y0, Y1); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'S', None, 'M', None], closed=True); b += s
    b += edge((X1, Y0), (X1, Y1), [None])[0]
    b += edge((X1, Y1), (X0, Y1), [None, 'R', None])[0]
    save('c1l1-o10-wrong.svg', svg(460, 270, b))

def o10_junctions():
    # بطارية ومصباح وأميتر، وفولتمتر بين طرفي المصباح دون رسم نقاط التوصيل
    X0, X1, Y0, Y1 = 80, 380, 120, 290; b = ''
    s, _ = battery_left(X0, Y0, Y1); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'L', None]); b += s; lx, ly = c[1]
    b += edge((X1, Y0), (X1, Y1), [None, 'A', None])[0] + edge((X1, Y1), (X0, Y1), [None])[0]
    j1, j2 = lx - 60, lx + 60
    b += edge((j1, Y0), (j1, 50), [None])[0] + edge((j1, 50), (j2, 50), [None, 'V', None])[0] + edge((j2, 50), (j2, Y0), [None])[0]
    save('c1l1-o10-junctions.svg', svg(460, 320, b))

def o10_e3():
    X0, X1, Y0, Y1 = 80, 380, 50, 230; b = ''
    s, _ = battery_left(X0, Y0, Y1, label='9.0 V'); b += s
    s, c = edge((X0, Y0), (X1, Y0), [None, 'S', None, 'L', None], closed=True); b += s
    b += edge((X1, Y0), (X1, Y1), [None, 'A', None])[0] + edge((X1, Y1), (X0, Y1), [None])[0]
    save('c1l1-o10-e3.svg', svg(460, 270, b))

if __name__ == '__main__':
    o02_numbered(); o02_lamp()
    o03_lamp_meters(); o03_cells(); o03_motor()
    o05_meters(); o05_e1(); o05_e3()
    o06_length(); o06_four()
    simple_loop('c1l1-o07-base.svg', '6.0 V', '30 Ω', '0.20 A')
    o07_three()
    simple_loop('c1l1-o07-e2.svg', '12 V', '40 Ω')
    o08_dimmer(); o08_motor()
    o10_symbols(); o10_choose(); o10_gap(); o10_wrong(); o10_junctions(); o10_e3()
