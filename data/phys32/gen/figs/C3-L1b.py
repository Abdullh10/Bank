import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-1 المغانط: الدائمة والمؤقتة — الأهداف O10–O17: قطبا المغناطيس الكهربائي، والمناطق المغناطيسية،
# والمغناطيس الدائم والمؤقت، والحلقة السلكية، وتجربة أورستد، والأرض مغناطيسًا، وخطوط المجال المغلقة.
# اصطلاح الكتاب في الفصل 3: خطوط المجال المغناطيسي خضراء، والمجال الداخل إلى الصفحة × والخارج منها • (أخضر)،
# والتيار I قائم غير مائل، وB قائم غير عريض.
import math, random

C_FIELD = '#1e8449'      # أخضر خطوط المجال (الكتاب)
COPPER = '#b5651d'       # سلك نحاسي
IRON = '#9aa3ad'         # قلب حديدي/مسمار
DOMAIN_BG = '#f4b400'    # خلفية المناطق المغناطيسية (الشكل 14-3 أصفر برتقالي)
MAG_N = '#c0392b'; MAG_S = '#2e5fa8'


def C(name, w, h, body): save(name, svg(w, h, body))


def arc_arrow(cx, cy, r, a0, a1, color=INK, w=2.5, head=11):
    """قوس دائري من الزاوية a0 إلى a1 (بالدرجات، الاتجاه الرياضي مع y لأعلى) ينتهي برأس سهم."""
    n = 24; pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    b = '<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts[:-1]) + f'" fill="none" stroke="{color}" stroke-width="{w}"/>'
    return b + ARROW(pts[-3][0], pts[-3][1], pts[-1][0], pts[-1][1], color, w, head)


def odot(x, y, r=7, color=C_FIELD):
    """رمز • (خارج من الصفحة)."""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.45:.1f}" fill="{color}"/>'


def cross(x, y, r=6, color=C_FIELD, w=2.2):
    """رمز × (داخل إلى الصفحة)."""
    return L(x - r, y - r, x + r, y + r, color, w) + L(x - r, y + r, x + r, y - r, color, w)


def coil(x0, yc, length, r, n, sense, arrows=True, core=None, wire=COPPER):
    """ملف لولبي أفقي. sense = 'down': التيار في اللفات الأمامية من أعلى إلى أسفل (يسري من اليسار إلى اليمين)؛
    'up': من أسفل إلى أعلى (يسري من اليمين إلى اليسار). اللفات الأمامية خط متصل، والخلفية متقطعة باهتة (أو يخفيها القلب).
    يعيد (svg، نقطة الطرف الأيسر العلوية، نقطة الطرف الأيمن السفلية)."""
    p = length / n; b = ''
    for k in range(n - 1):
        b += L(x0 + k * p + p / 2, yc + r, x0 + (k + 1) * p, yc - r, '#c9a27e', 1.8, '4 4')
    if core == 'iron':
        b += RECT(x0 - 14, yc - r + 5, length + 28, 2 * r - 10, '#6d7680', IRON, 1.5)
    for k in range(n):
        xa, ya, xb, yb = x0 + k * p, yc - r, x0 + k * p + p / 2, yc + r
        b += L(xa, ya, xb, yb, wire, 3.2)
        if arrows:
            mx, my = (xa + xb) / 2, (ya + yb) / 2; ux, uy = (xb - xa), (yb - ya); d = math.hypot(ux, uy); ux, uy = ux / d, uy / d
            if sense == 'up': ux, uy = -ux, -uy
            b += ARROW(mx - 7 * ux, my - 7 * uy, mx + 9 * ux, my + 9 * uy, INK, 2, 9)
    return b, (x0, yc - r), (x0 + (n - 1) * p + p / 2, yc + r)


def battery_h(x, y, plus='right'):
    """بطارية أفقية في سلك أفقي: لوح طويل (+) ولوح قصير (−)."""
    xl, xs = (x + 6, x - 6) if plus == 'right' else (x - 6, x + 6)
    b = L(xl, y - 18, xl, y + 18, INK, 2.4) + L(xs, y - 9, xs, y + 9, INK, 4)
    b += T(xl + (14 if plus == 'right' else -14), y - 14, '+', 18, color=MAG_N, weight='bold')
    b += T(xs + (-14 if plus == 'right' else 14), y - 14, '−', 18, color=INK, weight='bold')
    return b, xs if plus == 'right' else xl, xl if plus == 'right' else xs   # (svg، طرف السلك الأيسر، الأيمن)


# ---------------------------------------------------------------- O10 قطبا المغناطيس الكهربائي
def o10():
    # (1) ملف أفقي بأسهم التيار على اللفات الأمامية (من أعلى إلى أسفل) وطرفاه X وY
    b, (lx, ly), (rx, ry) = coil(150, 150, 260, 48, 7, 'down')
    b += L(lx, ly, lx, ly - 45, COPPER, 3) + ARROW(lx - 16, ly - 42, lx - 16, ly - 12, INK, 2, 9) + T(lx - 28, ly - 22, 'I', 17, color=INK)
    b += L(rx, ry, rx, ry + 45, COPPER, 3) + ARROW(rx + 16, ry + 10, rx + 16, ry + 40, INK, 2, 9) + T(rx + 28, ry + 32, 'I', 17)
    b += T(105, 158, 'X', 22, weight='bold') + T(470, 158, 'Y', 22, weight='bold')
    C('c3l1-o10-coil.svg', 560, 270, b)

    # (2) مسمار ملفوف عليه سلك موصول ببطارية (الطرف المسطح يسارًا، والمدبب يمينًا) — لا أسهم على اللفات
    yc = 110; x0 = 150; ln = 240; n = 7; r = 30
    b = ''
    b += RECT(x0 - 40, yc - 12, ln + 60, 24, '#6d7680', IRON, 1.5)
    b += RECT(x0 - 52, yc - 34, 12, 68, '#6d7680', IRON, 1.5)
    b += f'<polygon points="{x0 + ln + 20},{yc - 12} {x0 + ln + 75},{yc} {x0 + ln + 20},{yc + 12}" fill="{IRON}" stroke="#6d7680" stroke-width="1.5"/>'
    p = ln / n
    for k in range(n):
        b += L(x0 + k * p, yc - r, x0 + k * p + p / 2, yc + r, COPPER, 3.2)
    xl, yl = x0, yc - r; xr, yr = x0 + (n - 1) * p + p / 2, yc + r
    yb = 250; bx = 320
    bat, wl, wr = battery_h(bx, yb, 'right')
    b += bat
    b += L(xl, yl, xl, yl - 22, COPPER, 3) + L(xl, yl - 22, 30, yl - 22, COPPER, 3) + L(30, yl - 22, 30, yb, COPPER, 3) + L(30, yb, wl, yb, COPPER, 3)
    b += L(xr, yr, xr, yr + 20, COPPER, 3) + L(xr, yr + 20, 470, yr + 20, COPPER, 3) + L(470, yr + 20, 470, yb, COPPER, 3) + L(470, yb, wr, yb, COPPER, 3)
    b += T(x0 - 50, yc + 62, 'الطرف المسطح', 14) + T(x0 + ln + 50, yc - 26, 'الطرف المدبب', 14)
    C('c3l1-o10-nail.svg', 540, 290, b)

    # (3) طرف ملف يواجه الناظر: التيار يدور عكس عقارب الساعة كما تراه
    def endview(name, ccw):
        cx, cy = 180, 150
        b = f'<circle cx="{cx}" cy="{cy}" r="78" fill="#fbf3ea" stroke="{COPPER}" stroke-width="5"/>'
        b += f'<circle cx="{cx}" cy="{cy}" r="66" fill="none" stroke="#d9b48f" stroke-width="2"/>'
        if ccw:
            b += arc_arrow(cx, cy, 100, -60, 30, INK) + arc_arrow(cx, cy, 100, 120, 210, INK)
        else:
            b += arc_arrow(cx, cy, 100, 30, -60, INK) + arc_arrow(cx, cy, 100, 210, 120, INK)
        b += T(cx + 92, cy - 82, 'I', 18) + T(cx - 92, cy + 98, 'I', 18)
        b += T(cx, 285, 'طرف الملف المقابل للناظر', 15)
        C(name, 360, 305, b)
    endview('c3l1-o10-end.svg', True)
    endview('c3l1-o10-end-cw.svg', False)

    # (4) ملفان على محور واحد متقابلان
    b1, (lx, ly), (rx, ry) = coil(50, 80, 170, 40, 5, 'down')
    b2, (lx2, ly2), (rx2, ry2) = coil(330, 80, 170, 40, 5, 'up')
    b = b1 + b2
    b += T(130, 160, 'الملف 1', 15) + T(410, 160, 'الملف 2', 15)
    C('c3l1-o10-pair.svg', 560, 180, b)


# ---------------------------------------------------------------- O11/O12/O16 المناطق المغناطيسية
def domain_panel(x, y, size, mode, seed=3, rows=6, cols=5, label=None, frac=0.0):
    """مربع أصفر فيه أسهم خضراء تمثل اتجاهات مجالات المناطق: mode = 'random' | 'aligned' | 'partial'."""
    rnd = random.Random(seed)
    b = RECT(x, y, size, size, '#c98f00', DOMAIN_BG, 1.5)
    dx, dy = size / cols, size / rows
    for i in range(rows):
        for j in range(cols):
            cx, cy = x + (j + 0.5) * dx, y + (i + 0.5) * dy
            if mode == 'aligned': a = 0
            elif mode == 'partial': a = rnd.uniform(-35, 35) if rnd.random() < frac else rnd.uniform(0, 360)
            else: a = rnd.uniform(0, 360)
            ar = math.radians(a); hl = min(dx, dy) * 0.36
            b += ARROW(cx - hl * math.cos(ar), cy + hl * math.sin(ar), cx + hl * math.cos(ar), cy - hl * math.sin(ar), C_FIELD, 2.2, 8)
    if label: b += T(x + size / 2, y + size + 24, label, 16, weight='bold')
    return b


def o11():
    b = domain_panel(30, 20, 200, 'random', 7, label='(a)') + domain_panel(270, 20, 200, 'aligned', label='(b)')
    C('c3l1-o11-domains.svg', 500, 260, b)


def o12():
    b = T(250, 24, 'بعد إبعاد المغناطيس عن العينتين', 15, weight='bold')
    b += domain_panel(30, 42, 190, 'random', 11, label='العينة 1') + domain_panel(280, 42, 190, 'aligned', label='العينة 2')
    C('c3l1-o12-after.svg', 500, 275, b)


def o16b():
    b = ''
    for yy in (40, 250):
        b += ARROW(40, yy, 500, yy, C_FIELD, 2.5)
    b += T(520, 45, 'B', 19, color=C_FIELD) + T(270, 28, 'المجال المغناطيسي الخارجي', 14, color=C_FIELD)
    x, y, w, h = 150, 85, 240, 130
    b += RECT(x, y, w, h, '#c98f00', DOMAIN_BG, 1.5)
    for i in range(4):
        for j in range(6):
            cx, cy = x + (j + 0.5) * w / 6, y + (i + 0.5) * h / 4
            b += ARROW(cx - 13, cy, cx + 13, cy, C_FIELD, 2.2, 8)
    b += T(x - 22, y + h / 2 + 7, 'P', 22, weight='bold') + T(x + w + 22, y + h / 2 + 7, 'Q', 22, weight='bold')
    C('c3l1-o16-field.svg', 560, 275, b)


def o16c():
    b = domain_panel(20, 20, 170, 'random', 21, label='1') + domain_panel(215, 20, 170, 'partial', 5, label='2', frac=0.6) + domain_panel(410, 20, 170, 'aligned', label='3')
    C('c3l1-o16-three.svg', 600, 230, b)


# ---------------------------------------------------------------- O13 الحلقة السلكية
def loop_base(cx, cy, R, ccw=None, leads=True):
    g = 10
    a0 = math.degrees(math.asin(g / R))
    # حلقة بفتحة صغيرة أسفلها، وطرفا التوصيل نازلان
    pts = []
    for k in range(121):
        a = math.radians(-90 + a0 + (360 - 2 * a0) * k / 120)
        pts.append((cx + R * math.cos(a), cy - R * math.sin(a)))
    b = '<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" stroke="{COPPER}" stroke-width="4"/>'
    if leads:
        b += L(cx + g, cy + R - 1, cx + g, cy + R + 55, COPPER, 4) + L(cx - g, cy + R - 1, cx - g, cy + R + 55, COPPER, 4)
    if ccw is not None:
        if ccw:
            b += arc_arrow(cx, cy, R + 22, 10, 70, INK) + arc_arrow(cx, cy, R + 22, 190, 250, INK)
            b += ARROW(cx + g + 16, cy + R + 50, cx + g + 16, cy + R + 14, INK, 2, 9) + ARROW(cx - g - 16, cy + R + 14, cx - g - 16, cy + R + 50, INK, 2, 9)
        else:
            b += arc_arrow(cx, cy, R + 22, 70, 10, INK) + arc_arrow(cx, cy, R + 22, 250, 190, INK)
            b += ARROW(cx + g + 16, cy + R + 14, cx + g + 16, cy + R + 50, INK, 2, 9) + ARROW(cx - g - 16, cy + R + 50, cx - g - 16, cy + R + 14, INK, 2, 9)
        b += T(cx + R + 32, cy - R + 18, 'I', 18) + T(cx + g + 30, cy + R + 40, 'I', 17)
    return b


def o13():
    cx, cy, R = 200, 150, 95
    b = loop_base(cx, cy, R, ccw=True)
    b += DOT(cx - 20, cy - 10, 4.5) + T(cx - 4, cy - 14, 'P', 18, weight='bold')
    b += DOT(cx + R + 55, cy + 40, 4.5) + T(cx + R + 71, cy + 36, 'Q', 18, weight='bold')
    C('c3l1-o13-loop.svg', 420, 320, b)

    # المجال حول حلقة كما يرسمه الكتاب: • داخلها و× خارجها، دون أسهم التيار
    b = loop_base(cx, cy, R, ccw=None)
    for (dx, dy) in [(-40, -35), (0, -50), (40, -35), (-50, 5), (0, 0), (50, 5), (-30, 45), (30, 45)]:
        b += odot(cx + dx, cy + dy, 14)
    for k in range(12):
        a = math.radians(15 + 30 * k)
        x, y = cx + (R + 38) * math.cos(a), cy - (R + 38) * math.sin(a)
        if y < cy + R + 10 or abs(x - cx) > 40: b += cross(x, y, 6)
    C('c3l1-o13-field.svg', 420, 320, b)

    # منظر جانبي لحلقة عمودية على الصفحة: الأعلى تيار خارج (•)، والأسفل تيار داخل (×)
    cx, cy = 220, 175
    b = L(cx, cy - 80, cx, cy + 80, '#c9a27e', 2, '6 5')
    for yy, out in ((cy - 80, True), (cy + 80, False)):
        b += f'<circle cx="{cx}" cy="{yy}" r="15" fill="#fbf3ea" stroke="{COPPER}" stroke-width="3"/>'
        b += (f'<circle cx="{cx}" cy="{yy}" r="4" fill="{INK}"/>' if out else L(cx - 8, yy - 8, cx + 8, yy + 8, INK, 2.4) + L(cx - 8, yy + 8, cx + 8, yy - 8, INK, 2.4))
        b += T(cx + 30, yy + 6, 'I', 18)
    b += DOT(cx + 1, cy, 4.5) + T(cx + 18, cy + 6, 'P', 18, weight='bold')
    b += DOT(cx, cy - 150, 4.5) + T(cx + 18, cy - 144, 'R', 18, weight='bold')
    for k, out in enumerate((True, False)):
        lx, ly = 110 + k * 200, cy + 128
        b += f'<circle cx="{lx}" cy="{ly}" r="9" fill="#fbf3ea" stroke="{COPPER}" stroke-width="2"/>'
        b += (f'<circle cx="{lx}" cy="{ly}" r="2.6" fill="{INK}"/>' if out else L(lx - 5, ly - 5, lx + 5, ly + 5, INK, 1.8) + L(lx - 5, ly + 5, lx + 5, ly - 5, INK, 1.8))
        b += T(lx + 16, ly + 5, 'تيار خارج من الصفحة' if out else 'تيار داخل إلى الصفحة', 13, 'start')
    C('c3l1-o13-side.svg', 470, 320, b)


# ---------------------------------------------------------------- O14 تجربة أورستد
def compass(cx, cy, R=58, needle=None, face=True):
    """بوصلة من أعلى: needle = زاوية القطب الشمالي للإبرة (90 = نحو N أعلى الشكل) أو None. face=False: الإبرة وحدها."""
    if not face: b = ''
    else: b = f'<circle cx="{cx}" cy="{cy}" r="{R + 7}" fill="#d9b44a" stroke="#9c7b1f" stroke-width="2"/>'
    if face: b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#e8f3fb" stroke="#7a8b99" stroke-width="1.5"/>'
    for s, (dx, dy) in {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}.items():
        if face: b += T(cx + dx * (R - 13), cy + dy * (R - 13) + 5, s, 13, color=MUTED, weight='bold')
    if needle is not None:
        a = math.radians(needle); ux, uy = math.cos(a), -math.sin(a); nx, ny = -uy, ux; ln = R - 20
        tip = (cx + ln * ux, cy + ln * uy); tail = (cx - ln * ux, cy - ln * uy)
        b += f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {cx + 6 * nx:.1f},{cy + 6 * ny:.1f} {cx - 6 * nx:.1f},{cy - 6 * ny:.1f}" fill="{MAG_N}"/>'
        b += f'<polygon points="{tail[0]:.1f},{tail[1]:.1f} {cx + 6 * nx:.1f},{cy + 6 * ny:.1f} {cx - 6 * nx:.1f},{cy - 6 * ny:.1f}" fill="#f4f4f4" stroke="#7a8b99" stroke-width="1"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{INK}"/>'
    return b


def o14():
    b = ''
    for k, (on, ang, lab) in enumerate(((False, 90, '(a)'), (True, 0, '(b)'))):
        ox = 20 + k * 290
        cx, cy = ox + 110, 175
        b += compass(cx, cy, 58, ang)
        # مصدر القدرة
        b += RECT(ox + 170, 40, 90, 64, '#7a8b99', '#eef2f8', 1.5) + T(ox + 215, 30, 'مصدر القدرة', 13)
        b += RECT(ox + 190, 58, 50, 16, '#7a8b99', '#fff', 1.2) + RECT(ox + (217 if on else 192), 60, 21, 12, INK, '#2a6fb0', 1)
        b += T(ox + 186, 92, 'OFF', 11, color=MUTED) + T(ox + 244, 92, 'ON', 11, color=MUTED)
        # السلك فوق محور البوصلة
        b += f'<line x1="{cx}" y1="{cy - 95}" x2="{cx}" y2="{cy + 95}" stroke="#333" stroke-width="2.6" stroke-opacity="0.55"/>' + L(cx, cy - 95, ox + 170, cy - 95, '#333', 2.2)
        b += L(cx, cy + 95, ox + 235, cy + 95, '#333', 2.2) + L(ox + 235, cy + 95, ox + 235, 104, '#333', 2.2)
        b += T(cx, 300, lab, 16, weight='bold')
    b += T(130, 18, 'السلك فوق البوصلة', 13, color=MUTED)
    C('c3l1-o14-oersted.svg', 600, 315, b)

    # سلك أفقي على الورقة باتجاه الشمال فوق بوصلة (التيار نحو الشمال)، الإبرة مخفية
    cx, cy = 170, 160
    b = compass(cx, cy, 70, None)
    b += f'<line x1="{cx}" y1="{cy - 125}" x2="{cx}" y2="{cy + 125}" stroke="#333" stroke-width="3.5" stroke-opacity="0.6"/>' + ARROW(cx + 22, cy + 40, cx + 22, cy - 40, INK, 2.2, 10) + T(cx + 36, cy + 4, 'I', 18)
    b += T(cx, 312, 'السلك فوق البوصلة، والتيار نحو الشمال', 14)
    C('c3l1-o14-predict.svg', 340, 325, b)


# ---------------------------------------------------------------- O15 الأرض مغناطيس عملاق
def earth(name, magnet_labels=('S', 'N'), points=False, w=480, h=320):
    cx, cy, R = w / 2, h / 2 + 5, 82
    b = ''
    # خطوط المجال: خطوط ثنائي القطب r = k sin²θ (θ من محور القطبين) خارج الأرض فقط
    for k in (1.3, 1.8, 2.5):
        for side in (1, -1):
            pts = []
            for i in range(0, 181):
                th = math.radians(i)
                rr = k * R * math.sin(th) ** 2
                if rr >= R:
                    pts.append((cx + side * rr * math.sin(th), cy - rr * math.cos(th)))
            b += '<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" stroke="{C_FIELD}" stroke-width="2.2"/>'
            xe = cx + side * k * R
            b += ARROW(xe, cy + 9, xe, cy - 9, C_FIELD, 2.2, 11)
    b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#cfe3f5" stroke="#2a6fb0" stroke-width="2"/>'
    # المغناطيس داخل الأرض: الطرف الأعلى (قرب الشمال الجغرافي) والأسفل
    neutral = magnet_labels[0] == '1'
    b += RECT(cx - 13, cy - 55, 26, 55, '#555', '#d5d8dc' if neutral else '#f2f2f2', 1.5) + RECT(cx - 13, cy, 26, 55, '#555', '#d5d8dc' if neutral else '#d9534f', 1.5)
    b += T(cx, cy - 22, magnet_labels[0], 16, weight='bold') + T(cx, cy + 34, magnet_labels[1], 16, weight='bold', color='#fff' if magnet_labels[1] in ('N',) else INK)
    b += L(cx, cy - R - 30, cx, cy - R, MUTED, 1.5, '4 3') + L(cx, cy + R, cx, cy + R + 30, MUTED, 1.5, '4 3')
    b += T(cx, cy - R - 38, 'القطب الشمالي الجغرافي', 14) + T(cx, cy + R + 50, 'القطب الجنوبي الجغرافي', 14)
    if points:
        ax, ay = cx + R * math.sin(math.radians(18)), cy - R * math.cos(math.radians(18)); b += DOT(ax, ay, 5) + T(ax + 16, ay - 6, 'A', 18, weight='bold')
        b += DOT(cx + R, cy, 5) + T(cx + R + 26, cy + 18, 'B', 18, weight='bold')
    C(name, w, h, b)


def o15():
    earth('c3l1-o15-earth.svg', points=True)
    earth('c3l1-o15-earth-q.svg', magnet_labels=('1', '2'))


# ---------------------------------------------------------------- O17 خطوط مغلقة ولا أقطاب مفردة
def o17():
    cx, cy, hw, hh = 270, 170, 90, 24
    b = ''
    xN, xS = cx - hw, cx + hw
    for hgt in (60, 105, 150):
        for s in (1, -1):
            b += f'<path d="M {xN} {cy - s * 8} C {xN - hgt * 0.9} {cy - s * hgt * 1.15}, {xS + hgt * 0.9} {cy - s * hgt * 1.15}, {xS} {cy - s * 8}" fill="none" stroke="{C_FIELD}" stroke-width="2.2"/>'
            ytop = cy - s * (0.75 * hgt * 1.15 + 0.25 * 8) * 1.0
            b += ARROW(cx - 8, ytop, cx + 10, ytop, C_FIELD, 2.2, 11)
    # الخط المحوري: يخرج يسارًا من N ويدخل S من اليمين
    b += L(30, cy, xN, cy, C_FIELD, 2.2) + ARROW(xN - 40, cy, xN - 75, cy, C_FIELD, 2.2, 11)
    b += L(xS, cy, 510, cy, C_FIELD, 2.2) + ARROW(xS + 75, cy, xS + 40, cy, C_FIELD, 2.2, 11)
    b += RECT(xN, cy - hh, 2 * hw, 2 * hh, '#666', '#c8c8c8', 1.5)
    b += L(xN, cy, xS, cy, C_FIELD, 2, '6 5')
    b += T(xN + 18, cy + 6, 'N', 18, weight='bold') + T(xS - 18, cy + 6, 'S', 18, weight='bold')
    b += DOT(cx, cy, 4.5) + T(cx, cy - 8, 'P', 17, weight='bold')
    C('c3l1-o17-bar.svg', 540, 340, b)

    # مغناطيس كُسر نصفين
    b = T(270, 24, 'قبل الكسر', 14, color=MUTED)
    b += RECT(130, 40, 140, 40, '#555', MAG_N, 1.5) + RECT(270, 40, 140, 40, '#555', MAG_S, 1.5)
    b += T(150, 67, 'N', 18, color='#fff', weight='bold') + T(390, 67, 'S', 18, color='#fff', weight='bold')
    b += T(270, 120, 'بعد الكسر', 14, color=MUTED)
    b += RECT(100, 140, 140, 40, '#555', '#c8c8c8', 1.5) + RECT(300, 140, 140, 40, '#555', '#c8c8c8', 1.5)
    b += f'<polyline points="240,140 233,152 241,162 234,172 240,180" fill="none" stroke="#555" stroke-width="1.5"/>'
    for x, s in ((118, '1'), (222, '2'), (318, '3'), (422, '4')):
        b += T(x, 167, s, 18, weight='bold')
    C('c3l1-o17-broken.svg', 540, 200, b)


if __name__ == '__main__':
    o10(); o11(); o12(); o16b(); o16c(); o13(); o14(); o15(); o17()
