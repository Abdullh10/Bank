import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-2 (الجزء a: الأهداف O01–O04 وO09–O12): قانون لنز، اتجاه التيار الحثي، التيارات الدوامية، القوة الدافعة العكسية، الحث الذاتي.
# اصطلاح الكتاب (الفصلان 3 و4): خطوط المجال وأسهمه ورموزه (× داخل، • خارج) خضراء، والمجال B قائم؛ السرعة سهم أحمر رمزه v مائل؛
# التيار سهم رفيع رمزه I قائم؛ القوة سهم أزرق رمزه F مائل. الأقطاب: N أحمر، S أزرق (كرسوم الفصل الثالث).
import math

FIELD = '#1e8449'; NRED = '#c0392b'; SBLUE = '#2e6fb5'; COPPER = '#c07a45'; COPPER_L = '#dcc0a6'; IRON = '#8d96a3'; IRON_L = '#c9d1dc'

def C(name, w, h, body): save(name, svg(w, h, body))
def lab_I(x, y, s='I', size=17, anchor='middle'): return T(x, y, s, size, anchor, INK, italic=False)
def lab_B(x, y, s='B', size=17, anchor='middle'): return T(x, y, s, size, anchor, FIELD, italic=False)
def lab_F(x, y, s='F', size=18, anchor='middle'): return T(x, y, s, size, anchor, C_FORCE, italic=True)
def lab_v(x, y, s='v', size=18, anchor='middle'): return T(x, y, s, size, anchor, C_VEL, italic=True)
def cross(x, y, s=6, c=FIELD, w=2): return L(x - s, y - s, x + s, y + s, c, w) + L(x - s, y + s, x + s, y - s, c, w)
def fdot(x, y, r=4, c=FIELD): return DOT(x, y, r, c)
def grid(x0, y0, x1, y1, kind, dx=40, dy=40, clear=()):
    b = ''; y = y0
    while y <= y1 + 0.1:
        x = x0
        while x <= x1 + 0.1:
            if not any(a <= x <= c and bb <= y <= d for a, bb, c, d in clear):
                b += cross(x, y) if kind == 'into' else fdot(x, y)
            x += dx
        y += dy
    return b

def magnet(x, y, w=150, h=40, left='N', right='S'):
    b = ''
    for xx, p in ((x, left), (x + w / 2, right)):
        b += RECT(xx, y, w / 2, h, INK, NRED if p == 'N' else SBLUE, 1.5)
    b += T(x + 18, y + h / 2 + 6, left, 17, color='#fff', weight='bold') + T(x + w - 18, y + h / 2 + 6, right, 17, color='#fff', weight='bold')
    return b
def vmagnet(x, y, w=36, h=120, top='S', bottom='N'):
    b = ''
    for yy, p in ((y, top), (y + h / 2, bottom)):
        b += RECT(x, yy, w, h / 2, INK, NRED if p == 'N' else SBLUE, 1.5)
    b += T(x + w / 2, y + 22, top, 16, color='#fff', weight='bold') + T(x + w / 2, y + h - 10, bottom, 16, color='#fff', weight='bold')
    return b

def coil(x0, y, x1, turns, r=34, color=COPPER, w=3):
    pitch = (x1 - x0) / turns; rx = pitch * 0.42; b = ''
    for k in range(turns):
        xc = x0 + (k + 0.5) * pitch
        b += f'<path d="M {xc:.1f} {y - r} A {rx:.1f} {r} 0 0 0 {xc:.1f} {y + r}" fill="none" stroke="{COPPER_L}" stroke-width="{w - 0.8}"/>'
    for k in range(turns):
        xc = x0 + (k + 0.5) * pitch
        end = xc + pitch * 0.5 if k < turns - 1 else xc
        b += f'<path d="M {xc:.1f} {y + r} A {rx:.1f} {r} 0 0 0 {end:.1f} {y - r}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    return b

def galv(x, y, r=20):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="2"/>' + T(x, y + 6, 'G', 17)

def ring_h(cx, cy, rx=60, ry=16, gap=False, color=COPPER, w=5):
    """حلقة أفقية مرسومة بمنظور (قطع ناقص)."""
    if not gap:
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    a1, a2 = math.radians(75), math.radians(105)  # فتحة صغيرة في الجهة الأمامية
    p1 = (cx + rx * math.cos(a1), cy + ry * math.sin(a1)); p2 = (cx + rx * math.cos(a2), cy + ry * math.sin(a2))
    return f'<path d="M {p1[0]:.1f} {p1[1]:.1f} A {rx} {ry} 0 1 0 {p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>'

# ───────────────────────── مشهد ملف ومغناطيس
def coil_scene(name, side, near, moving, extra_txt=None):
    """side: جهة المغناطيس ('left'/'right')؛ near: القطب المقابل للملف؛ moving: 'toward' أو 'away'."""
    w, h = 560, 250; cy = 160; b = ''
    cx0, cx1 = 215, 345
    b += coil(cx0, cy, cx1, 7)
    # أسلاك إلى الجلفانومتر
    b += L(cx0 + 8, cy - 34, cx0 + 8, 60, INK, 1.8) + L(cx0 + 8, 60, 260, 60, INK, 1.8) + L(300, 60, cx1 - 8, 60, INK, 1.8) + L(cx1 - 8, 60, cx1 - 8, cy - 34, INK, 1.8) + galv(280, 60)
    far = 'S' if near == 'N' else 'N'
    if side == 'left':
        mx = 40; b += magnet(mx, cy - 20, 150, 40, far, near); tip = mx + 150
        if moving == 'toward': b += ARROW(70, cy - 45, 150, cy - 45, C_VEL, 3)
        else: b += ARROW(150, cy - 45, 70, cy - 45, C_VEL, 3)
        b += lab_v(110, cy - 55)
    else:
        mx = 370; b += magnet(mx, cy - 20, 150, 40, near, far)
        if moving == 'toward': b += ARROW(490, cy - 45, 410, cy - 45, C_VEL, 3)
        else: b += ARROW(410, cy - 45, 490, cy - 45, C_VEL, 3)
        b += lab_v(450, cy - 55)
    b += T(280, cy + 62, 'ملف', 14, color=MUTED)
    if extra_txt: b += T(w / 2, h - 8, extra_txt, 13, color=MUTED)
    C(name, w, h, b)

def loop_field(name, kind, trend, ccw_arrows=None):
    """حلقة دائرية في مستوى الورقة داخل مجال منتظم (× أو •) متغير المقدار."""
    w, h = 420, 300; b = ''
    b += grid(40, 40, 380, 240, kind, clear=((120, 80, 300, 210),))
    b += grid(160, 120, 260, 170, kind, dx=50, dy=50)
    b += f'<circle cx="210" cy="145" r="75" fill="none" stroke="{COPPER}" stroke-width="6"/>'
    b += lab_B(395, 30, 'B', 18) + T(210, 280, trend, 15)
    C(name, w, h, b)

def o01():
    coil_scene('c4l2-o01-approach.svg', 'left', 'N', 'toward')

def o02():
    coil_scene('c4l2-o02-a.svg', 'right', 'S', 'toward')
    coil_scene('c4l2-o02-b.svg', 'left', 'N', 'away')
    loop_field('c4l2-o02-c.svg', 'out', 'مقدار المجال B يتزايد')
    loop_field('c4l2-o02-d.svg', 'into', 'مقدار المجال B يتزايد')
    # e: حلقة مربعة تُسحب خارج منطقة مجال داخل في الورقة
    w, h = 520, 270; b = f'<rect x="20" y="30" width="270" height="210" fill="#f1f8f3" stroke="{FIELD}" stroke-width="1.5" stroke-dasharray="6 5"/>'
    b += grid(45, 55, 285, 215, 'into', clear=((215, 85, 300, 185),))
    b += f'<rect x="230" y="85" width="120" height="100" fill="none" stroke="{COPPER}" stroke-width="6"/>'
    b += grid(255, 115, 285, 155, 'into', dx=30, dy=40)
    b += ARROW(365, 135, 440, 135, C_VEL, 3) + lab_v(402, 122) + lab_B(40, 22, 'B', 18)
    b += T(155, 262, 'منطقة المجال', 13, color=MUTED) + T(420, 230, 'لا مجال هنا', 13, color=MUTED)
    C('c4l2-o02-e.svg', w, h, b)
    # f: ملف بقلب حديدي موصول ببطارية ومفتاح، وحلقة ألومنيوم على امتداد محوره
    w, h = 560, 270; cy = 110; b = ''
    b += RECT(90, cy - 14, 330, 28, INK, IRON_L, 1.5)
    b += coil(120, cy, 320, 9, 40)
    b += f'<ellipse cx="390" cy="{cy}" rx="12" ry="46" fill="none" stroke="#9aa3ad" stroke-width="7"/>'
    b += T(390, cy - 58, 'حلقة ألومنيوم', 13, color=MUTED) + T(220, cy - 54, 'ملف', 13, color=MUTED) + T(470, cy + 5, 'قلب حديدي', 13, color=MUTED)
    # دائرة البطارية والمفتاح
    yb = 220
    b += L(128, cy + 40, 128, yb, INK, 1.8) + L(312, cy + 40, 312, yb, INK, 1.8)
    b += L(128, yb, 190, yb, INK, 1.8) + L(190, yb - 14, 190, yb + 14, INK, 3) + L(200, yb - 7, 200, yb + 7, INK, 5) + L(200, yb, 245, yb, INK, 1.8)
    b += DOT(245, yb, 3.5) + L(245, yb, 280, yb - 18, INK, 2) + DOT(285, yb, 3.5) + L(285, yb, 312, yb, INK, 1.8)
    b += T(195, yb + 34, 'بطارية', 13, color=MUTED) + T(265, yb + 34, 'مفتاح', 13, color=MUTED)
    C('c4l2-o02-f.svg', w, h, b)
    # g: مغناطيس يسقط رأسيًّا عبر حلقة أفقية (مرحلتان)
    w, h = 520, 330; b = ''
    for k, (ox, above) in enumerate(((130, True), (390, False))):
        ry = 170
        b += T(ox, 22, f'({k + 1})', 16, weight='bold')
        if above:
            b += vmagnet(ox - 18, 35, 36, 110, 'S', 'N') + ring_h(ox, ry + 15) + ARROW(ox + 40, 60, ox + 40, 120, C_VEL, 3) + lab_v(ox + 54, 95)
        else:
            b += ring_h(ox, 90) + vmagnet(ox - 18, 170, 36, 110, 'S', 'N') + ARROW(ox + 40, 195, ox + 40, 255, C_VEL, 3) + lab_v(ox + 54, 230)
    b += T(130, 230, 'المغناطيس فوق الحلقة', 13, color=MUTED) + T(390, 305, 'المغناطيس أسفل الحلقة', 13, color=MUTED)
    b += L(260, 30, 260, 310, GRID, 1.5)
    C('c4l2-o02-g.svg', w, h, b)
    # path: حلقة تعبر منطقة مجال خارج من الورقة بسرعة ثابتة (ثلاثة مواضع)
    w, h = 620, 260; x0, x1 = 200, 420
    b = f'<rect x="{x0}" y="40" width="{x1 - x0}" height="180" fill="#f1f8f3" stroke="{FIELD}" stroke-width="1.5" stroke-dasharray="6 5"/>'
    b += ''.join(fdot(x, y) for y in (55, 80, 130, 180, 205) for x in (222, 255, 310, 365, 398))
    for k, cx in enumerate((x0, 310, x1)):
        b += f'<rect x="{cx - 40}" y="100" width="80" height="60" fill="none" stroke="{COPPER}" stroke-width="5"/>' + T(cx, 240, str(k + 1), 16, weight='bold')
    b += ARROW(470, 130, 540, 130, C_VEL, 3) + lab_v(505, 118) + lab_B(x1 - 12, 32, 'B', 18)
    b += T(130, 60, 'منطقة المجال', 13, color=MUTED) + L(150, 66, 198, 80, MUTED, 1)
    C('c4l2-o02-path.svg', w, h, b)

def o04():
    # الميزان الحساس: ذراع ونهايته صفيحة فلزية بين قطبي مغناطيس
    w, h = 520, 260; b = ''
    b += f'<polygon points="200,200 230,120 260,200" fill="{IRON_L}" stroke="{INK}" stroke-width="1.5"/>' + RECT(150, 200, 160, 14, INK, IRON_L, 1.5)
    b += L(70, 115, 400, 115, INK, 5) + DOT(230, 117, 5)
    b += L(70, 115, 70, 150, INK, 1.5) + f'<path d="M 30 150 L 110 150 L 100 162 L 40 162 Z" fill="{IRON_L}" stroke="{INK}" stroke-width="1.5"/>' + T(70, 185, 'الكفة', 13, color=MUTED)
    b += RECT(400, 95, 10, 50, INK, '#b0b7c1', 1.5)
    b += RECT(355, 60, 40, 30, INK, NRED, 1.5) + T(375, 81, 'N', 15, color='#fff', weight='bold')
    b += RECT(355, 150, 40, 30, INK, SBLUE, 1.5) + T(375, 171, 'S', 15, color='#fff', weight='bold')
    b += ARROW(440, 90, 440, 150, FIELD, 2) + lab_B(458, 125)
    b += T(470, 60, 'صفيحة فلزية', 13, color=MUTED) + L(440, 64, 412, 100, MUTED, 1)
    C('c4l2-o04-balance.svg', w, h, b)
    # حلقتان من الألومنيوم على قلب حديدي لملف يمر فيه تيار متناوب
    w, h = 520, 300; b = ''
    for k, (ox, gap) in enumerate(((140, False), (380, True))):
        b += RECT(ox - 14, 40, 28, 220, INK, IRON_L, 1.5)
        b += f'<rect x="{ox - 46}" y="170" width="92" height="90" fill="#e8d3bf" stroke="{COPPER}" stroke-width="2"/>'
        for j in range(8): b += L(ox - 46, 176 + j * 11, ox + 46, 176 + j * 11, COPPER, 2)
        b += ring_h(ox, 150, 40, 11, gap, '#9aa3ad', 6)
        b += T(ox, 25, f'({k + 1})', 16, weight='bold') + T(ox, 288, 'إلى مصدر AC', 13, color=MUTED)
    b += T(200, 154, 'حلقة كاملة', 13, 'start', MUTED) + T(440, 154, 'حلقة مقطوعة', 13, 'start', MUTED)
    C('c4l2-o04-ring.svg', w, h, b)
    # مغناطيسان متماثلان يسقطان في أنبوبين رأسيين: نحاسي وبلاستيكي
    w, h = 460, 320; b = ''
    for ox, fill, stroke, lab in ((130, '#e9c3a3', COPPER, 'أنبوب نحاسي'), (330, '#eef1f5', '#9aa3ad', 'أنبوب بلاستيكي')):
        b += f'<rect x="{ox - 30}" y="40" width="60" height="240" fill="{fill}" stroke="{stroke}" stroke-width="2" opacity="0.9"/>'
        b += vmagnet(ox - 14, 60, 28, 60, 'S', 'N') + ARROW(ox + 48, 70, ox + 48, 120, C_VEL, 3) + lab_v(ox + 62, 100)
        b += T(ox, 305, lab, 14, color=MUTED)
    C('c4l2-o04-tube.svg', w, h, b)

def o09():
    # قلب حديدي مصمت وقلب من شرائح معزولة
    w, h = 560, 260; b = ''
    b += T(140, 25, '(a)', 16, weight='bold') + T(420, 25, '(b)', 16, weight='bold')
    b += RECT(60, 50, 160, 160, INK, IRON_L, 2)
    for r in (60, 40, 20):
        b += f'<circle cx="140" cy="130" r="{r}" fill="none" stroke="{C_VEL}" stroke-width="1.8" stroke-dasharray="5 4"/>'
    b += T(140, 238, 'قلب حديدي مصمت', 13, color=MUTED)
    for k in range(8):
        x = 340 + k * 20
        b += RECT(x, 50, 15, 160, INK, IRON_L, 1.5) + (RECT(x + 15, 50, 5, 160, '#d4b06a', '#f2e2b8', 0.8) if k < 7 else '')
    b += T(420, 238, 'شرائح حديدية رقيقة بينها عازل', 13, color=MUTED)
    C('c4l2-o09-cores.svg', w, h, b)
    # بندولان صفيحتاهما مصمتة ومشقوقة يتأرجحان داخل مجال مغناطيسي
    w, h = 560, 300; b = ''
    for k, (ox, slots) in enumerate(((140, False), (420, True))):
        b += f'<rect x="{ox - 90}" y="150" width="180" height="120" fill="#f1f8f3" stroke="{FIELD}" stroke-width="1.2" stroke-dasharray="6 5"/>'
        b += grid(ox - 70, 165, ox + 70, 255, 'into', dx=35, dy=30, clear=((ox - 45, 175, ox + 45, 255), (ox - 10, 150, ox + 10, 180)))
        b += L(ox - 40, 30, ox + 40, 30, INK, 3) + L(ox, 30, ox, 180, INK, 2)
        b += f'<rect x="{ox - 40}" y="180" width="80" height="70" fill="#d7dce3" stroke="{INK}" stroke-width="1.8"/>'
        if slots:
            for j in range(4): b += RECT(ox - 31 + j * 18, 196, 8, 54, '#d7dce3', '#fff', 1)
        b += T(ox, 22, f'({k + 1})', 16, weight='bold')
    b += lab_B(540, 145, 'B', 18) + T(140, 292, 'صفيحة مصمتة', 13, color=MUTED) + T(420, 292, 'صفيحة مشقوقة', 13, color=MUTED)
    C('c4l2-o09-pendulum.svg', w, h, b)

def o10():
    # مصدر AC يغذي مصباحًا ومحركًا موصولين على التوازي، وللمحرك مفتاح
    w, h = 520, 260; b = ''
    b += f'<circle cx="70" cy="140" r="26" fill="#fff" stroke="{INK}" stroke-width="2"/>' + f'<path d="M 54 140 Q 62 124 70 140 T 86 140" fill="none" stroke="{INK}" stroke-width="2"/>'
    b += L(70, 114, 70, 50, INK, 2) + L(70, 50, 420, 50, INK, 2) + L(70, 166, 70, 230, INK, 2) + L(70, 230, 420, 230, INK, 2)
    # المصباح
    b += L(250, 50, 250, 115, INK, 2) + f'<circle cx="250" cy="140" r="22" fill="#fff8d8" stroke="{INK}" stroke-width="2"/>' + L(235, 125, 265, 155, INK, 1.6) + L(235, 155, 265, 125, INK, 1.6) + L(250, 162, 250, 230, INK, 2)
    # المحرك ومفتاحه
    b += L(420, 50, 420, 72, INK, 2) + DOT(420, 72, 3.5) + L(420, 72, 404, 100, INK, 2) + DOT(420, 104, 3.5) + L(420, 104, 420, 118, INK, 2)
    b += f'<circle cx="420" cy="140" r="22" fill="#fff" stroke="{INK}" stroke-width="2"/>' + T(420, 146, 'M', 17) + L(420, 162, 420, 230, INK, 2)
    b += T(82, 200, 'مصدر AC', 13, 'start', MUTED) + T(262, 190, 'مصباح', 13, 'start', MUTED) + T(470, 146, 'محرك', 13, color=MUTED) + T(470, 92, 'مفتاح', 13, color=MUTED)
    C('c4l2-o10-lamps.svg', w, h, b)

def o11():
    # سلك يتحرك إلى أعلى في مجال داخل في الورقة، والتيار الحثي فيه إلى اليسار
    w, h = 460, 300; b = ''
    b += grid(40, 40, 420, 260, 'into', clear=((70, 120, 400, 205),))
    b += L(80, 165, 380, 165, COPPER, 8)
    b += ARROW(330, 150, 330, 90, C_VEL, 3) + lab_v(346, 112)
    b += ARROW(200, 190, 120, 190, INK, 2, 10) + lab_I(160, 210)
    b += lab_B(430, 28, 'B', 18) + T(80, 145, 'سلك', 13, color=MUTED)
    C('c4l2-o11-wire.svg', w, h, b)
    # مولد يدوي موصول بثلاثة مصابيح على التوازي، لكل منها مفتاح
    w, h = 560, 260; b = '<g transform="translate(25,0)">'
    b += RECT(30, 90, 110, 90, INK, '#e3e8ef', 2) + T(85, 140, 'مولد', 15)
    b += L(30, 135, 5, 135, INK, 4) + L(5, 135, 5, 105, INK, 4) + DOT(5, 105, 6, INK) + T(40, 82, 'مقبض', 13, color=MUTED)
    b += L(140, 110, 500, 110, INK, 2) + L(140, 160, 160, 160, INK, 2) + L(160, 160, 160, 230, INK, 2) + L(160, 230, 500, 230, INK, 2)
    for k, x in enumerate((240, 370, 500)):
        b += L(x, 110, x, 125, INK, 2) + DOT(x, 125, 3.5) + L(x, 125, x - 16, 150, INK, 2) + DOT(x, 154, 3.5) + L(x, 154, x, 165, INK, 2)
        b += f'<circle cx="{x}" cy="185" r="18" fill="#fff8d8" stroke="{INK}" stroke-width="2"/>' + L(x - 12, 173, x + 12, 197, INK, 1.5) + L(x - 12, 197, x + 12, 173, INK, 1.5) + L(x, 203, x, 230, INK, 2)
        b += T(x + 28, 145, f'S{k + 1}', 14, 'start')
    C('c4l2-o11-gen.svg', w + 30, h, b + '</g>')

def o12():
    graph('c4l2-o12-graph.svg', [{'pts': [(0, 0), (2, 2), (3, 6), (5, 6), (8, 0)], 'color': BLUE, 'dots': True}],
          (0, 9), (0, 8), 'الزمن t (s)', 'التيار I (A)', 1, 1)
    graph('c4l2-o12-graph2.svg', [{'pts': [(0, 0), (4, 4), (6, 4), (7, 0), (9, 0)], 'color': BLUE, 'dots': True}],
          (0, 9), (0, 6), 'الزمن t (s)', 'التيار I (A)', 1, 1,
          labels=[(2, 3.4, 'A', INK), (5, 4.6, 'B', INK), (6.8, 2.6, 'C', INK), (8, 0.6, 'D', INK)])

if __name__ == '__main__':
    o01(); o02(); o04(); o09(); o10(); o11(); o12()
