import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 1-2 استخدام الطاقة الكهربائية (الأهداف O01–O09): دوائر بسيطة برموز الكتاب، نقل الطاقة، منحنيات، عداد الطاقة، مخطط سريان الطاقة.

WIRE = INK; GEN_FILL = '#c9d3df'; LRM = '‎'


def resistor_v(x, y1, y2, n=6, amp=10):
    """مقاومة متعرجة رأسية بين y1 وy2 (أسلاك ممتدة من الطرفين)."""
    seg = (y2 - y1) * 0.6; ys = y1 + (y2 - y1 - seg) / 2; ye = ys + seg
    pts = [(x, y1), (x, ys)]
    for k in range(n):
        pts.append((x + (amp if k % 2 == 0 else -amp), ys + (k + 0.5) * seg / n))
    pts += [(x, ye), (x, y2)]
    return f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{WIRE}" stroke-width="2.2" stroke-linejoin="round"/>'


def resistor_h(x1, x2, y, n=6, amp=10):
    seg = (x2 - x1) * 0.6; xs = x1 + (x2 - x1 - seg) / 2; xe = xs + seg
    pts = [(x1, y), (xs, y)]
    for k in range(n):
        pts.append((xs + (k + 0.5) * seg / n, y + (amp if k % 2 == 0 else -amp)))
    pts += [(xe, y), (x2, y)]
    return f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{WIRE}" stroke-width="2.2" stroke-linejoin="round"/>'


def battery_v(x, yc, cells=2):
    """بطارية رأسية (الطرف الموجب أعلى): ألواح طويلة وقصيرة متناوبة كما في الكتاب."""
    b = ''; gap = 8; top = yc - cells * gap
    for k in range(cells):
        y = top + 2 * k * gap
        b += L(x - 16, y, x + 16, y, WIRE, 2.4) + L(x - 8, y + gap, x + 8, y + gap, WIRE, 4)
    b += L(x, yc - 40, x, top, WIRE, 2.2) + L(x, top + (2 * cells - 1) * gap, x, yc + 40, WIRE, 2.2)
    b += T(x - 24, top + 2, '+', 15, color=RED) + T(x - 24, top + (2 * cells - 1) * gap + 10, '−', 16)
    return b


def generator(x, yc, r=18):
    return f'<circle cx="{x}" cy="{yc}" r="{r}" fill="{GEN_FILL}" stroke="{WIRE}" stroke-width="2.2"/>'


def loop(name, src='battery', src_label='', load_label='', load='resistor', w=420, h=260, src_name=None, load_name=None, cur=True):
    """دائرة بسيطة: مصدر في الضلع الأيسر وحمل في الضلع الأيمن وسهم التيار I أسفلها."""
    xl, xr, yt, yb = 90, w - 110, 40, h - 50; yc = (yt + yb) / 2
    b = L(xl, yt, xr, yt) + L(xl, yb, xr, yb)
    if src == 'battery': b += battery_v(xl, yc) + L(xl, yt, xl, yc - 40) + L(xl, yc + 40, xl, yb)
    else: b += generator(xl, yc) + L(xl, yt, xl, yc - 18) + L(xl, yc + 18, xl, yb)
    if src_label: b += T(xl + 26, yc + 5, src_label, 15, 'start')
    if src_name: b += T(xl - 30, yc + 5, src_name, 14, 'end', MUTED)
    b += resistor_v(xr, yt, yb)
    if load_label: b += T(xr - 18, yc + 5, load_label, 15, 'end')
    if load_name: b += T(xr + 18, yc + 5, load_name, 14, 'start', MUTED)
    if cur:
        mx = (xl + xr) / 2; b += ARROW(mx + 30, yb + 18, mx - 30, yb + 18, WIRE, 1.8, 9) + T(mx, yb + 38, 'I', 15, italic=True)
    save(name, svg(w, h, b))


def house(x, yb, wd=70, ht=56):
    return (f'<polygon points="{x},{yb} {x + wd},{yb} {x + wd},{yb - ht} {x + wd / 2},{yb - ht - 30} {x},{yb - ht}" fill="#f4e7c6" stroke="{INK}" stroke-width="2"/>'
            + RECT(x + wd / 2 - 9, yb - 26, 18, 26, INK, '#b9895a', 1.5))


def line_fig(name, r_each, cur_label, left='محطة التوليد', right='المنزل', w=600, h=250, dist=None):
    """محطة توليد وسلكا نقل (ذهاب وإياب) في كل منهما مقاومة، والحمل (منزل) في الطرف الآخر."""
    x0, x1, yt, yb = 120, 470, 70, 170
    b = RECT(30, 80, 80, 80, INK, '#dde5ef', 2) + generator(70, 120, 20) + T(70, 190, left, 14)
    b += L(110, yt + 30, 110, yt) + L(110, yt, x0, yt) + L(110, yb - 30, 110, yb) + L(110, yb, x0, yb)
    b += L(x0, yt, 220, yt) + resistor_h(220, 340, yt) + L(340, yt, x1, yt)
    b += L(x0, yb, 220, yb) + resistor_h(220, 340, yb) + L(340, yb, x1, yb)
    b += T(280, yt - 18, r_each, 15) + T(280, yb + 30, r_each, 15)
    b += L(x1, yt, 500, yt) + L(500, yt, 500, 100) + L(x1, yb, 500, yb) + L(500, yb, 500, 150)
    b += house(500, 160) + T(535, 190, right, 14)
    if cur_label: b += ARROW(380, yt - 14, 440, yt - 14, WIRE, 1.8, 9) + T(396, yt - 24, 'I', 15, 'end', italic=True) + T(400, yt - 24, '= ' + cur_label, 15, 'start')
    if dist:
        b += ARROW(160, 222, 470, 222, MUTED, 1.4, 8) + ARROW(470, 222, 160, 222, MUTED, 1.4, 8) + T(315, 240, dist, 14, color=MUTED)
    save(name, svg(w, h + (20 if dist else 0), b))


def chain(name):
    """مراحل نقل الطاقة من محطة التوليد إلى المنزل، مع جهد كل مرحلة ومقاطع مرقّمة."""
    w, h = 700, 250
    boxes = [(20, 'محطة التوليد', '13.8 kV'), (190, 'محطة محولات', 'رفع الجهد'), (360, 'محول توزيع', 'خفض الجهد'), (530, 'محول داخل الحي', 'خفض الجهد')]
    b = ''
    for x, t1, t2 in boxes:
        b += RECT(x, 60, 140, 64, INK, '#eef2f8', 2) + T(x + 70, 88, t1, 14, weight='bold') + T(x + 70, 110, t2, 13, color=MUTED)
    segs = [(160, 190, '1'), (330, 360, '2'), (500, 530, '3')]
    labels = ['13.8 kV', '132 kV', '13.8 kV']
    for (a, c, n), v in zip(segs, labels):
        b += ARROW(a, 92, c, 92, INK, 2.2, 8)
    # أسلاك المقاطع تحت المربعات
    b += L(90, 124, 90, 170) + L(90, 170, 260, 170) + L(260, 124, 260, 170)
    b += L(260, 170, 430, 170) + L(430, 124, 430, 170)
    b += L(430, 170, 600, 170) + L(600, 124, 600, 170)
    b += L(600, 170, 600, 205) + L(600, 205, 650, 205)
    b += house(650, 235, 40, 34)
    b += T(175, 160, '(1)', 14, weight='bold') + T(175, 192, '13.8 kV', 13)
    b += T(345, 160, '(2)', 14, weight='bold') + T(345, 192, '132 kV', 13)
    b += T(515, 160, '(3)', 14, weight='bold') + T(515, 192, '13.8 kV', 13)
    b += T(625, 228, '(4)', 14, weight='bold') + T(560, 228, '230/400 V', 13)
    b += T(670, 254, 'المنزل', 12)
    b += T(350, 30, 'نقل الطاقة الكهربائية من محطة التوليد إلى المنزل', 15, weight='bold')
    save(name, svg(w, h + 10, b))


def rt_graph(name):
    pts = [(0, 0), (90, 0), (90, 6), (300, 20)]
    graph(name, [{'pts': pts, 'color': BLUE}], (0, 300), (0, 25), 'درجة الحرارة (K)', 'المقاومة (mΩ)', 50, 5)


def p_panels(name):
    """أربعة منحنيات صغيرة للقدرة P مقابل التيار I، معنونة A–D."""
    w, h = 640, 210; b = ''
    shapes = {
        'A': [(t, t) for t in [0, 1]],
        'B': [(t / 20, (t / 20) ** 2) for t in range(21)],
        'C': [(0, 0.55), (1, 0.55)],
        'D': [(t / 20, 1 - (t / 20) ** 0.5 * 0.9) for t in range(21)],
    }
    for k, key in enumerate('ABCD'):
        ox = 30 + k * 155; oy = 160; W, H = 120, 120
        b += ARROW(ox, oy, ox + W + 10, oy, INK, 1.8, 8) + ARROW(ox, oy, ox, oy - H - 10, INK, 1.8, 8)
        b += T(ox + W + 6, oy + 20, 'I', 15, italic=True) + T(ox - 12, oy - H + 4, 'P', 15, italic=True)
        pts = ' '.join(f'{ox + x * W:.1f},{oy - y * H:.1f}' for x, y in shapes[key])
        b += f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="3"/>'
        b += T(ox + W / 2, oy + 40, f'({key})', 16, weight='bold')
    save(name, svg(w, h, b))


def iv_hyper(name):
    pts = [(v, 4400 / v) for v in range(110, 252, 2)]
    graph(name, [{'pts': pts, 'color': BLUE}], (100, 250), (0, 50), 'الجهد (V)', 'التيار (A)', 25, 10,
          marks=[(127, 4400 / 127, ''), (220, 20, '')])


def meter(name, r1, r2):
    w, h = 560, 170; b = ''
    for k, (lab, r) in enumerate([('القراءة في نهاية الشهر', r2), ('القراءة في بداية الشهر', r1)]):
        x = 30 + k * 270
        b += RECT(x, 30, 230, 110, INK, '#eef2f8', 2) + T(x + 115, 58, lab, 14, weight='bold')
        b += RECT(x + 30, 75, 170, 44, INK, '#1f2a44', 1.5)
        b += f'<text x="{x + 115}" y="106" text-anchor="middle" font-size="26" fill="#7cf29a" {MATHFONT} letter-spacing="3">{r}</text>'
        b += T(x + 115, 136, 'kWh', 13, color=MUTED)
    save(name, svg(w, h, b))


def sankey(name, inp, dev='محرك كهربائي', out1='طاقة ميكانيكية مفيدة', out2='طاقة حرارية'):
    w, h = 600, 230; b = ''
    b += f'<polygon points="20,85 170,85 170,70 205,110 170,150 170,135 20,135" fill="#f6d6a8" stroke="{ORANGE}" stroke-width="1.5"/>'
    b += T(95, 60, 'طاقة كهربائية داخلة', 14, weight='bold') + T(95, 108, inp, 15) + T(95, 128, 'كل ثانية', 13)
    b += RECT(215, 75, 130, 70, INK, '#eef2f8', 2) + T(280, 116, dev, 14, weight='bold')
    b += f'<polygon points="355,80 520,80 520,66 560,95 520,124 520,110 355,110" fill="#cfe6d6" stroke="{GREEN}" stroke-width="1.5"/>'
    b += T(450, 56, out1, 14, weight='bold') + T(450, 101, '؟', 16)
    b += f'<path d="M 355 120 L 380 120 Q 420 120 420 160 L 420 180 L 432 180 L 410 210 L 388 180 L 400 180 L 400 160 Q 400 140 380 140 L 355 140 Z" fill="#f5c9c2" stroke="{RED}" stroke-width="1.5"/>'
    b += T(470, 196, out2, 14, weight='bold') + T(470, 218, '؟', 16)
    save(name, svg(w, h, b))


if __name__ == '__main__':
    loop('c1l2-o01-heater.svg', 'gen', '120 V', '24.0 Ω')
    loop('c1l2-o01-battery.svg', 'battery', '12 V', '8.0 Ω')
    loop('c1l2-o01-cooker.svg', 'gen', '220 V', '22 Ω', load_name='عنصر التسخين', w=470)
    rt_graph('c1l2-o02-rt.svg')
    chain('c1l2-o03-chain.svg')
    loop('c1l2-o05-oven.svg', 'battery', '220 V', '11 Ω', load_name='عنصر الفرن', w=470)
    meter('c1l2-o05-meter.svg', '24365', '24965')
    p_panels('c1l2-o06-p-i.svg')
    line_fig('c1l2-o07-line.svg', '0.80 Ω', '50 A')
    line_fig('c1l2-o07-rural.svg', '', '', dist='4.0 km')
    iv_hyper('c1l2-o08-i-v.svg')
    sankey('c1l2-o09-motor.svg', '1200 J')
