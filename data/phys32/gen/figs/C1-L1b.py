import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 1-1 (الأهداف O11–O20): دوائر كهربائية برموز الكتاب، ومنحنيات التيار–الجهد، ومختبر الجهد والتيار والمقاومة.
import math

METER_FILL = '#e3dff2'; PLUS = '#c0392b'

def _unit(x1, y1, x2, y2):
    d = math.hypot(x2 - x1, y2 - y1); return (x2 - x1) / d, (y2 - y1) / d, d

def seg(x1, y1, x2, y2, comp=None, label=None, side=1, plus='start', lsize=14, ldist=None, extra_label=None):
    """سلك من (x1,y1) إلى (x2,y2) وفي منتصفه عنصر comp:
    'R' مقاومة ثابتة، 'VR' مقاومة متغيرة، 'bat' بطارية (plus = الطرف الموجب: 'start' أو 'end')، 'lamp' مصباح،
    'A' أميتر، 'V' فولتمتر، 'M' محرك، 'Sopen' / 'Sclosed' مفتاح. label نص بجانب العنصر (side = 1 أو -1)."""
    ux, uy, d = _unit(x1, y1, x2, y2); nx, ny = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    half = {'R': 26, 'VR': 26, 'bat': 13, 'lamp': 14, 'A': 15, 'V': 15, 'M': 16, 'Sopen': 20, 'Sclosed': 20, None: 0}[comp]
    b = ''
    if comp is None:
        return L(x1, y1, x2, y2, INK, 2.2)
    b += L(x1, y1, mx - half * ux, my - half * uy, INK, 2.2) + L(mx + half * ux, my + half * uy, x2, y2, INK, 2.2)
    P = lambda s, t: (mx + s * ux + t * nx, my + s * uy + t * ny)
    if comp in ('R', 'VR'):
        pts = [P(-26, 0)]
        n = 6
        for k in range(n):
            pts.append(P(-26 + (k + 0.5) * 52 / n, 9 * (1 if k % 2 == 0 else -1)))
        pts.append(P(26, 0))
        b += '<polyline points="' + ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
        if comp == 'VR':
            # رمز الكتاب (الشكل 1-5): ذراع منزلقة موازية للمقاومة تنعطف ويُشير سهمها عموديًّا إلى منتصف الخط المتعرج
            a0 = P(26, 24); a1 = P(0, 24); a2 = P(0, 11)
            b += L(a0[0], a0[1], a1[0], a1[1], INK, 1.8) + ARROW(a1[0], a1[1], a2[0], a2[1], INK, 1.8, 8)
    elif comp == 'bat':
        # خليتان: طويل/قصير/طويل/قصير، والخط الطويل هو الموجب
        offs = [-9, -3, 3, 9]; lens = [16, 8, 16, 8]
        if plus == 'end': offs = offs[::-1]
        for o, ln in zip(offs, lens):
            a, c = P(o, -ln), P(o, ln)
            b += L(a[0], a[1], c[0], c[1], INK, 2.6 if ln == 16 else 3.2)
        sg = -1 if plus == 'start' else 1
        pp = P(offs[0] + 6 * sg, -22); mm = P(offs[-1] - 6 * sg, -22)
        b += T(pp[0], pp[1] + 5, '+', 15, color=PLUS, weight='bold') + T(mm[0], mm[1] + 5, '−', 15, weight='bold')
    elif comp == 'lamp':
        b += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="14" fill="#fff" stroke="{INK}" stroke-width="2.2"/>'
        a = P(-14, 0); c = P(14, 0); l1 = P(-4, -9); l2 = P(4, -9); q1 = P(-6, 6); q2 = P(6, 6)
        b += f'<path d="M {a[0]:.1f} {a[1]:.1f} L {P(-6,0)[0]:.1f} {P(-6,0)[1]:.1f} C {l1[0]:.1f} {l1[1]:.1f} {l2[0]:.1f} {l2[1]:.1f} {P(0,0)[0]:.1f} {P(0,0)[1]:.1f} C {q1[0]:.1f} {q1[1]:.1f} {q2[0]:.1f} {q2[1]:.1f} {P(6,0)[0]:.1f} {P(6,0)[1]:.1f} L {c[0]:.1f} {c[1]:.1f}" fill="none" stroke="{INK}" stroke-width="1.8"/>'
    elif comp in ('A', 'V'):
        b += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="15" fill="{METER_FILL}" stroke="{INK}" stroke-width="2"/>' + T(mx, my + 5.5, comp, 16, color=INK)
    elif comp == 'M':
        b += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="16" fill="#d9d5ee" stroke="{INK}" stroke-width="2"/>'
        a = P(-7, 12); c = P(7, 20)
        b += L(a[0], a[1], c[0], c[1], INK, 2)
    elif comp in ('Sopen', 'Sclosed'):
        a = P(-20, 0); c = P(20, 0)
        b += DOT(a[0], a[1], 3.2) + DOT(c[0], c[1], 3.2)
        e = P(18, -16) if comp == 'Sopen' else P(20, -2)
        b += L(a[0], a[1], e[0], e[1], INK, 2.4)
    if label:
        dist = ldist or (half + 14 if comp not in ('R', 'VR') else 24)
        if comp == 'bat': dist = ldist or 42
        lp = P(0, -dist * side)
        b += T(lp[0], lp[1] + 5, label, lsize)
    if extra_label:
        t, s, dd = extra_label; lp = P(s, dd); b += T(lp[0], lp[1] + 5, t, lsize)
    return b

def wires(*pts):
    return ''.join(L(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], INK, 2.2) for i in range(len(pts) - 1))

def node(x, y): return DOT(x, y, 4, INK)

def iarrow(x, y, direction, label='I', length=34, side=-1):
    """سهم التيار الاصطلاحي بجانب سلك: direction ∈ right/left/up/down."""
    dx, dy = {'right': (1, 0), 'left': (-1, 0), 'up': (0, -1), 'down': (0, 1)}[direction]
    x1, y1 = x - dx * length / 2, y - dy * length / 2; x2, y2 = x + dx * length / 2, y + dy * length / 2
    b = ARROW(x1, y1, x2, y2, INK, 1.8, 9)
    if label:
        if dy == 0: b += T(x, y - 8 if side < 0 else y + 18, label, 15, italic=True)
        else: b += T(x + (12 if side > 0 else -12), y + 5, label, 15, italic=True)
    return b

def tag(x, y, s, size=15, color=INK, weight='bold'): return T(x, y, s, size, color=color, weight=weight)

def C(name, w, h, body): save(name, svg(w, h, body))

# ───────────────────────── O11 التوصيل على التوازي والتوالي
def o11():
    # بطارية وأميتر ومصباح وفولتمتر بين طرفي المصباح
    b = seg(60, 210, 60, 60, 'bat', '12 V', side=-1, plus='end', ldist=40)
    b += wires((60, 60), (130, 60)) + seg(130, 60, 230, 60, 'A') + wires((230, 60), (330, 60), (330, 100))
    b += seg(330, 100, 330, 170, 'lamp') + wires((330, 170), (330, 210), (60, 210))
    b += node(330, 100) + node(330, 170) + wires((330, 100), (410, 100)) + seg(410, 100, 410, 170, 'V') + wires((410, 170), (330, 170))
    C('c1l1-o11-mix.svg', 460, 250, b)
    # دائرة ذات مسار واحد: بطارية وأميتر ومقاومة
    b = seg(60, 200, 60, 60, 'bat', '6.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (120, 60)) + seg(120, 60, 220, 60, 'A')
    b += wires((220, 60), (300, 60)) + seg(300, 60, 300, 200, 'R', '20 Ω', side=-1) + wires((300, 200), (60, 200))
    C('c1l1-o11-single.svg', 380, 240, b)
    # مصباحان يتفرع بينهما التيار، والنقطتان X وY
    b = seg(60, 210, 60, 60, 'bat', '9.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (220, 60), (220, 90))
    b += wires((220, 90), (180, 90)) + seg(180, 90, 180, 180, 'lamp', 'L_1', side=-1) + wires((180, 180), (220, 180))
    b += wires((220, 90), (300, 90)) + seg(300, 90, 300, 180, 'lamp', 'L_2', side=1) + wires((300, 180), (220, 180))
    b += wires((220, 180), (220, 210), (60, 210)) + node(220, 90) + node(220, 180)
    b += tag(232, 82, 'X') + tag(232, 200, 'Y')
    C('c1l1-o11-two.svg', 380, 250, b)
    # مقالي: بطارية، أميتر، مصباح ومقاومة في مسار واحد، وفولتمتر بين طرفي المقاومة
    b = seg(60, 220, 60, 60, 'bat', '12 V', side=-1, plus='end', ldist=40) + seg(60, 60, 180, 60, 'A') + seg(180, 60, 320, 60, 'lamp', 'L')
    b += wires((320, 60), (360, 60), (360, 100)) + seg(360, 100, 360, 180, 'R', 'R', side=-1) + wires((360, 180), (360, 220), (60, 220))
    b += node(360, 100) + node(360, 180) + wires((360, 100), (440, 100)) + seg(440, 100, 440, 180, 'V') + wires((440, 180), (360, 180))
    C('c1l1-o11-net.svg', 490, 260, b)

# ───────────────────────── O12 حفظ الشحنة وحفظ الطاقة
def o12():
    b = seg(60, 200, 60, 60, 'bat', '6.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (100, 60)) + seg(100, 60, 180, 60, 'A', extra_label=('A_1', 0, -28))
    b += seg(180, 60, 280, 60, 'lamp') + seg(280, 60, 360, 60, 'A', extra_label=('A_2', 0, -28)) + wires((360, 60), (400, 60), (400, 200), (60, 200))
    b += T(140, 108, '0.40 A', 14)
    C('c1l1-o12-amps.svg', 440, 240, b)
    b = seg(60, 220, 60, 60, 'bat', '9.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (130, 60)) + seg(130, 60, 250, 60, 'R', 'R_1')
    b += wires((250, 60), (330, 60)) + seg(330, 60, 330, 220, 'R', 'R_2', side=-1) + wires((330, 220), (60, 220))
    b += node(130, 60) + node(250, 60) + wires((130, 60), (130, 130), (160, 130)) + seg(160, 130, 220, 130, 'V') + wires((220, 130), (250, 130), (250, 60))
    b += T(190, 168, '6.0 V', 14)
    C('c1l1-o12-loop.svg', 400, 260, b)
    # مقالي: ثلاثة أميترات في مواضع مختلفة من دائرة ذات مسار واحد
    b =seg(60, 220, 60, 60, 'bat', '12 V', side=-1, plus='end', ldist=40) + seg(60, 60, 170, 60, 'A', extra_label=('A_1', 0, -28))
    b += seg(170, 60, 290, 60, 'lamp') + wires((290, 60), (380, 60)) + seg(380, 60, 380, 220, 'R', side=-1)
    b += seg(380, 220, 280, 220, 'A', extra_label=('A_2', 0, 28)) + seg(280, 220, 160, 220, 'A', extra_label=('A_3', 0, 28)) + wires((160, 220), (60, 220))
    b += T(115, 108, '0.25 A', 14)
    C('c1l1-o12-three.svg', 430, 270, b)

# ───────────────────────── O13 المقاومة الكهربائية (منحنى موصلين)
def o13():
    graph('c1l1-o13-graph.svg', [
        {'pts': [(0, 0), (6, 0.60)], 'color': BLUE, 'label': 'X', 'at': (6, 0.60), 'dx': -4, 'dy': -8},
        {'pts': [(0, 0), (6, 0.20)], 'color': RED, 'label': 'Y', 'at': (6, 0.20), 'dx': -4, 'dy': -10}],
        (0, 6), (0, 0.7), 'فرق الجهد (V)', 'التيار (A)', xstep=1, ystep=0.1, w=500, h=340)

# ───────────────────────── O14 التيار الاصطلاحي
def o14():
    # لوحان موصلان A وB يصل بينهما سلك C (جهد B أكبر)
    b = RECT(90, 40, 220, 18, INK, '#dfe6ee') + RECT(90, 200, 220, 18, INK, '#dfe6ee')
    b += f'<rect x="132" y="58" width="12" height="142" fill="#c9d3de" stroke="{INK}" stroke-width="1.5"/>'
    b += T(75, 55, 'B', 17, weight='bold') + T(75, 215, 'A', 17, weight='bold') + T(162, 135, 'C', 17, weight='bold')
    C('c1l1-o14-plates.svg', 340, 250, b)
    # دائرة: بطارية (1) ومفتاح مغلق (2) ومقاومة (3) ومحرك (4)
    b = seg(60, 230, 60, 60, 'bat', None, side=1, plus='end') + wires((60, 60), (130, 60)) + seg(130, 60, 250, 60, 'M', 'محرك')
    b += wires((250, 60), (330, 60)) + seg(330, 60, 330, 230, 'R', 'مقاومة', side=1, ldist=40) + seg(330, 230, 60, 230, 'Sclosed', 'مفتاح مغلق', side=1, ldist=22)
    b += DOT(150, 60, 4.5) + DOT(230, 60, 4.5) + T(150, 46, 'K', 16, weight='bold') + T(230, 46, 'N', 16, weight='bold')
    C('c1l1-o14-motor.svg', 400, 270, b)
    # بطارية مقلوبة (الموجب أسفل) والنقطة P على السلك العلوي
    b = seg(60, 210, 60, 60, 'bat', None, side=1, plus='start') + wires((60, 60), (330, 60)) + seg(330, 60, 330, 210, 'lamp')
    b += wires((330, 210), (60, 210)) + DOT(195, 60, 4.5) + tag(195, 45, 'P')
    C('c1l1-o14-flip.svg', 390, 250, b)
    # مقالي: نقاط a وb وc وd على دائرة فيها بطارية ومصباح ومقاومة
    b = seg(60, 220, 60, 60, 'bat', '6.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (120, 60)) + seg(120, 60, 260, 60, 'lamp')
    b += wires((260, 60), (340, 60)) + seg(340, 60, 340, 220, 'R', side=-1) + wires((340, 220), (60, 220))
    for x, y, s in [(95, 60, 'a'), (300, 60, 'b'), (340, 140 + 40, 'c'), (200, 220, 'd')]:
        b += DOT(x, y, 4.5)
    b += T(95, 46, 'a', 16, italic=True) + T(300, 46, 'b', 16, italic=True) + T(356, 190, 'c', 16, italic=True) + T(200, 242, 'd', 16, italic=True)
    C('c1l1-o14-points.svg', 400, 260, b)

# ───────────────────────── O15 شروط سريان التيار (بطارية وسلك ومصباح حقيقيان)
def cell(x, y):
    """بطارية جافة رأسية: النتوء المعدني الموجب أعلى عند (x, y)، والقرص المعدني السالب أسفل."""
    return (f'<rect x="{x-22}" y="{y+8}" width="44" height="86" rx="4" fill="#2f4f86" stroke="{INK}" stroke-width="1.6"/>'
            f'<rect x="{x-7}" y="{y}" width="14" height="9" fill="#b9bec7" stroke="{INK}" stroke-width="1.4"/>'
            f'<rect x="{x-20}" y="{y+92}" width="40" height="6" fill="#b9bec7" stroke="{INK}" stroke-width="1.4"/>'
            + T(x, y + 40, '+', 18, color='#fff', weight='bold') + T(x, y + 80, '−', 18, color='#fff', weight='bold'))

def bulb(x, y, rot=0):
    """مصباح: طرف التلامس السفلي (النقطة) عند (x, y)، وفوقه القاعدة المعدنية (الطرف الجانبي) ثم الزجاجة؛ rot دوران حول (x, y)."""
    return (f'<g transform="rotate({rot} {x} {y})">'
         f'<circle cx="{x}" cy="{y-46}" r="20" fill="#fdf6d8" stroke="{INK}" stroke-width="1.6"/>'
         f'<path d="M {x-6} {y-30} L {x-3} {y-48} Q {x} {y-54} {x+3} {y-48} L {x+6} {y-30}" fill="none" stroke="{ORANGE}" stroke-width="1.4"/>'
         f'<rect x="{x-11}" y="{y-29}" width="22" height="22" fill="#c7ccd4" stroke="{INK}" stroke-width="1.5"/>'
         f'<line x1="{x-11}" y1="{y-22}" x2="{x+11}" y2="{y-19}" stroke="{INK}" stroke-width="1"/><line x1="{x-11}" y1="{y-15}" x2="{x+11}" y2="{y-12}" stroke="{INK}" stroke-width="1"/>'
         f'<rect x="{x-6}" y="{y-7}" width="12" height="4" fill="#fff" stroke="{INK}" stroke-width="1"/>'
         f'<circle cx="{x}" cy="{y-1}" r="3.2" fill="#8a8f99" stroke="{INK}" stroke-width="1"/></g>')

def wire_path(d): return f'<path d="{d}" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>'

def o15():
    W = 190; b = ''; top = 120
    # (1) طرف المصباح السفلي على النتوء الموجب، وسلك من القاعدة المعدنية الجانبية إلى القرص السالب ← مسار مغلق
    cx = 70
    b += cell(cx, top) + bulb(cx, top + 1) + wire_path(f'M {cx+11} 100 C {cx+70} 95, {cx+70} 225, {cx+20} {top+95}')
    # (2) سلك من القرص السالب إلى طرف المصباح السفلي فقط، والقاعدة الجانبية لا تلمس شيئًا
    cx = W + 60
    b += cell(cx, top) + bulb(cx + 75, 105) + wire_path(f'M {cx+20} {top+95} C {cx+85} 225, {cx+95} 150, {cx+75} 105')
    # (3) سلك يصل النتوء الموجب بالقرص السالب مباشرة، والمصباح بعيد يلمس السلك بطرفه السفلي فقط
    cx = 2 * W + 35
    b += cell(cx, top) + wire_path(f'M {cx} {top} C {cx+70} 100, {cx+80} 225, {cx+20} {top+95}') + bulb(cx + 61, 163, 90)
    # (4) سلك واحد يصل النتوء الموجب بالقاعدة الجانبية للمصباح فقط، والنقطة السفلية لا تلمس شيئًا، والقرص السالب حر
    cx = 3 * W + 60
    b += cell(cx, top) + bulb(cx + 80, 112) + wire_path(f'M {cx} {top} C {cx+5} 82, {cx+40} 92, {cx+69} {112-18}')
    for k in range(4): b += T(k * W + 95, 30, f'({k+1})', 17, weight='bold')
    for k in range(1, 4): b += L(k * W, 20, k * W, 250, GRID, 1.5)
    C('c1l1-o15-ways.svg', 4 * W, 260, b)
    # دائرة فيها مفتاح مفتوح
    b = seg(60, 200, 60, 60, 'bat', '6.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (120, 60)) + seg(120, 60, 240, 60, 'Sopen', 'مفتاح', ldist=28)
    b += wires((240, 60), (320, 60)) + seg(320, 60, 320, 200, 'lamp') + wires((320, 200), (60, 200))
    C('c1l1-o15-switch.svg', 380, 240, b)

# ───────────────────────── O16 الموصل الأومي والجهاز غير الأومي
def o16():
    graph('c1l1-o16-line.svg', [{'pts': [(0, 0), (8, 0.40)], 'color': BLUE, 'dots': False}],
          (0, 8), (0, 0.5), 'فرق الجهد (V)', 'التيار (A)', xstep=1, ystep=0.1, w=500, h=330,
          marks=[(2, 0.10, ''), (4, 0.20, ''), (6, 0.30, ''), (8, 0.40, '')])
    # دايود: تيار مهمل حتى نحو 0.4 V ثم يرتفع بسرعة؛ نقاط مقروءة: (0.60, 0.005) و(0.70, 0.020)
    pts = [(0, 0), (0.3, 0), (0.4, 0.0002), (0.45, 0.0006), (0.5, 0.0012), (0.55, 0.0028), (0.6, 0.005), (0.65, 0.010), (0.7, 0.020), (0.73, 0.030)]
    graph('c1l1-o16-diode.svg', [{'pts': pts, 'color': RED}], (0, 0.8), (0, 0.03), 'فرق الجهد (V)', 'التيار (A)',
          xstep=0.1, ystep=0.005, w=520, h=360, marks=[(0.6, 0.005, ''), (0.7, 0.020, '')])
    # موصل X (خط مستقيم) ومصباح Y (منحنٍ يميل نحو المحور الأفقي)
    lamp = [(v, 0.075 * v / (1 + 0.2083 * v)) for v in [k * 0.2 for k in range(31)]]  # ميل ابتدائي محدود (مقاومة الفتيل البارد) ويقطع X قرب 2.4 V
    graph('c1l1-o16-two.svg', [{'pts': [(0, 0), (6, 0.30)], 'color': BLUE, 'label': 'X', 'at': (6, 0.30), 'dx': -4, 'dy': -8},
                               {'pts': lamp, 'color': RED, 'label': 'Y', 'at': (6, 0.2), 'dx': -4, 'dy': 20}],
          (0, 6), (0, 0.35), 'فرق الجهد (V)', 'التيار (A)', xstep=1, ystep=0.05, w=500, h=340)
    # مصباح بقيم مقروءة: (2.0, 0.20) (4.0, 0.30) (6.0, 0.36) — نقاط معلَّمة
    lp = [(0, 0), (0.5, 0.07), (1.0, 0.12), (2.0, 0.20), (3.0, 0.255), (4.0, 0.30), (5.0, 0.335), (6.0, 0.36)]
    graph('c1l1-o16-lamp.svg', [{'pts': lp, 'color': RED}], (0, 6), (0, 0.4), 'فرق الجهد (V)', 'التيار (A)',
          xstep=1, ystep=0.05, w=500, h=340, marks=[(2, 0.20, ''), (4, 0.30, ''), (6, 0.36, '')])

# ───────────────────────── O17 توصيل الأميتر والفولتمتر
def panel(ox, kind):
    """لوحة صغيرة: بطارية يسار، ومقاومة R يمين، ومواضع الأميتر والفولتمتر حسب kind."""
    b = ''; x1, x2, y1, y2 = ox + 40, ox + 190, 70, 210
    b += seg(x1, y2, x1, y1, 'bat', None, plus='end')
    if kind == 1:   # صحيح: أميتر على التوالي في السلك العلوي، وفولتمتر على التوازي مع R
        b += seg(x1, y1, x2, y1, 'A') + seg(x2, y1, x2, y2, 'R') + wires((x2, y2), (x1, y2))
        b += node(x2, 105) + node(x2, 175) + wires((x2, 105), (x2 + 45, 105)) + seg(x2 + 45, 105, x2 + 45, 175, 'V') + wires((x2 + 45, 175), (x2, 175))
    if kind == 2:   # الأميتر على التوازي مع R والفولتمتر على التوالي
        b += seg(x1, y1, x2, y1, 'V') + seg(x2, y1, x2, y2, 'R') + wires((x2, y2), (x1, y2))
        b += node(x2, 105) + node(x2, 175) + wires((x2, 105), (x2 + 45, 105)) + seg(x2 + 45, 105, x2 + 45, 175, 'A') + wires((x2 + 45, 175), (x2, 175))
    if kind == 3:   # الجهازان على التوالي
        b += seg(x1, y1, x2, y1, 'A') + seg(x2, y1, x2, y2, 'R') + seg(x2, y2, x1, y2, 'V')
    if kind == 4:   # الجهازان على التوازي مع R
        b += wires((x1, y1), (x2, y1)) + seg(x2, y1, x2, y2, 'R') + wires((x2, y2), (x1, y2))
        b += node(x2, 90) + node(x2, 190) + wires((x2, 90), (x2 + 40, 90)) + seg(x2 + 40, 90, x2 + 40, 190, 'V') + wires((x2 + 40, 190), (x2, 190))
        b += wires((x2 + 40, 90), (x2 + 80, 90)) + seg(x2 + 80, 90, x2 + 80, 190, 'A') + wires((x2 + 80, 190), (x2 + 40, 190)) + node(x2 + 40, 90) + node(x2 + 40, 190)
    b += T(x2 + 22, 146, 'R', 15, italic=True) if kind != 4 else T(x2 - 18, 146, 'R', 15, italic=True)
    b += T(ox + 140, 36, f'({kind})', 17, weight='bold')
    return b

def o17():
    W = 290; b = ''
    for k in range(4): b += panel(k * W, k + 1)
    for k in range(1, 4): b += L(k * W, 20, k * W, 240, GRID, 1.5)
    C('c1l1-o17-panels.svg', 4 * W, 250, b)
    # بطارية ومفتاح ومقاومة متغيرة ومحرك ونقاط مرقّمة
    b = seg(60, 230, 60, 60, 'bat', '12 V', side=-1, plus='end', ldist=40) + wires((60, 60), (110, 60)) + seg(110, 60, 270, 60, 'M', 'محرك', ldist=30)
    b += wires((270, 60), (340, 60)) + seg(340, 60, 340, 230, 'VR', 'مقاومة متغيرة', side=1, ldist=70) + seg(340, 230, 60, 230, 'Sclosed', 'مفتاح', side=1, ldist=22)
    for x, y, s in [(110, 60, 'P'), (270, 60, 'Q')]: b += DOT(x, y, 4.5) + T(x, y - 14, s, 16, weight='bold')
    C('c1l1-o17-motor.svg', 470, 270, b)
    # فولتمتر بين طرفي مقاومة: النقطتان P (الأقرب إلى القطب الموجب) وQ، وطرفا الفولتمتر X وY
    b = seg(60, 220, 60, 60, 'bat', '9.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (300, 60), (300, 90)) + seg(300, 90, 300, 190, 'R', 'R', side=-1)
    b += wires((300, 190), (300, 220), (60, 220)) + DOT(300, 90, 4.5) + DOT(300, 190, 4.5) + T(286, 96, 'P', 16, weight='bold') + T(286, 196, 'Q', 16, weight='bold')
    b += f'<circle cx="420" cy="140" r="30" fill="{METER_FILL}" stroke="{INK}" stroke-width="2"/>' + T(420, 148, 'V', 22)
    b += DOT(420, 104, 4) + DOT(420, 176, 4) + L(420, 104, 420, 110, INK, 2) + L(420, 170, 420, 176, INK, 2)
    b += T(440, 102, 'X', 15, weight='bold') + T(440, 186, 'Y', 15, weight='bold')
    C('c1l1-o17-term.svg', 480, 250, b)

# ───────────────────────── O18 تحولات الطاقة (أجزاء مرقمة كالأسئلة 36–39)
def o18():
    b = seg(60, 230, 60, 60, 'bat', None, side=1, plus='end') + wires((60, 60), (130, 60)) + seg(130, 60, 250, 60, 'M')
    b += wires((250, 60), (330, 60)) + seg(330, 60, 330, 230, 'VR') + seg(330, 230, 60, 230, 'Sclosed')
    b += T(32, 150, '1', 17, weight='bold') + T(190, 105, '4', 17, weight='bold') + T(362, 150, '3', 17, weight='bold') + T(195, 255, '2', 17, weight='bold')
    C('c1l1-o18-num.svg', 400, 275, b)

# ───────────────────────── O19 القدرة والطاقة
def o19():
    b = seg(60, 210, 60, 60, 'bat', '9.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (110, 60)) + seg(110, 60, 230, 60, 'A')
    b += T(170, 105, '0.40 A', 14) + wires((230, 60), (320, 60)) + seg(320, 60, 320, 210, 'M', 'محرك', side=1, ldist=44) + wires((320, 210), (60, 210))
    C('c1l1-o19-circ.svg', 400, 250, b)

# ───────────────────────── O20 مختبر الجهد والتيار والمقاومة
def o20():
    pts = [(10, 150), (20, 75), (30, 50), (40, 37.5)]
    curve = [(r / 2, 3000 / r) for r in range(18, 85)]
    graph('c1l1-o20-ir.svg', [{'pts': curve, 'color': BLUE}], (0, 45), (0, 175), 'المقاومة (kΩ)', 'التيار (μA)',
          xstep=5, ystep=25, w=520, h=350, marks=[(x, y, '') for x, y in pts])
    # الجزء B بمقاومة الكتاب 10 kΩ وثلاث بطاريات (450 μA ضمن تدريج الأميتر 500 μA)
    graph('c1l1-o20-iv.svg', [{'pts': [(0, 0), (4.5, 450)], 'color': BLUE}], (0, 5), (0, 500), 'الجهد (V)', 'التيار (μA)',
          xstep=1, ystep=50, w=520, h=370, marks=[(1.5, 150, ''), (3.0, 300, ''), (4.5, 450, '')])

if __name__ == '__main__':
    o11(); o12(); o13(); o14(); o15(); o16(); o17(); o18(); o19(); o20()
