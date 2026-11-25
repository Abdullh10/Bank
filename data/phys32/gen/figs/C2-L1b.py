import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-1 (الأهداف O09–O15): دوائر التوالي والتوازي برموز الكتاب (التسميات قائمة كما يطبعها الفصل 2)،
# ونموذج النهر الجبلي، ومجزّئ الجهد مع المقاومة الضوئية، ومختبر دوائر التوالي والتوازي.
# دوال الدوائر منسوخة من C1-L1b.py مع جعل تسميات الكميات قائمة (غير مائلة) وإضافة رمز المقاومة الضوئية.
import math

METER_FILL = '#e3dff2'; PLUS = '#c0392b'; WATER = '#2e86c1'; ROCK = '#d8cbb3'; LIGHT = '#c0392b'

def _unit(x1, y1, x2, y2):
    d = math.hypot(x2 - x1, y2 - y1); return (x2 - x1) / d, (y2 - y1) / d, d

def seg(x1, y1, x2, y2, comp=None, label=None, side=1, plus='start', lsize=14, ldist=None, extra_label=None):
    """سلك من (x1,y1) إلى (x2,y2) وفي منتصفه عنصر comp: 'R' مقاومة، 'LDR' مقاومة ضوئية (متعرج داخل إطار بيضوي)،
    'bat' بطارية (plus = الطرف الموجب)، 'lamp' مصباح، 'A' أميتر، 'V' فولتمتر، 'Sopen'/'Sclosed' مفتاح.
    label نص قائم بجانب العنصر (side = 1 أو -1)؛ extra_label = (نص، إزاحة على السلك، إزاحة عمودية)."""
    ux, uy, d = _unit(x1, y1, x2, y2); nx, ny = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    half = {'R': 26, 'LDR': 26, 'bat': 13, 'lamp': 14, 'A': 15, 'V': 15, 'Sopen': 20, 'Sclosed': 20, None: 0}[comp]
    if comp is None:
        return L(x1, y1, x2, y2, INK, 2.2)
    b = L(x1, y1, mx - half * ux, my - half * uy, INK, 2.2) + L(mx + half * ux, my + half * uy, x2, y2, INK, 2.2)
    P = lambda s, t: (mx + s * ux + t * nx, my + s * uy + t * ny)
    if comp in ('R', 'LDR'):
        pts = [P(-26, 0)]
        for k in range(6):
            pts.append(P(-26 + (k + 0.5) * 52 / 6, 9 * (1 if k % 2 == 0 else -1)))
        pts.append(P(26, 0))
        b += '<polyline points="' + ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
        if comp == 'LDR':
            ang = math.degrees(math.atan2(uy, ux))
            b += f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="34" ry="19" transform="rotate({ang:.1f} {mx:.1f} {my:.1f})" fill="none" stroke="{INK}" stroke-width="2"/>'
    elif comp == 'bat':
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
    elif comp in ('Sopen', 'Sclosed'):
        a = P(-20, 0); c = P(20, 0)
        b += DOT(a[0], a[1], 3.2) + DOT(c[0], c[1], 3.2)
        e = P(18, -16) if comp == 'Sopen' else P(20, -2)
        b += L(a[0], a[1], e[0], e[1], INK, 2.4)
    if label:
        dist = ldist or (half + 14 if comp not in ('R', 'LDR') else 24)
        if comp == 'bat': dist = ldist or 42
        lp = P(0, -dist * side)
        b += T(lp[0], lp[1] + 5, label, lsize)
    if extra_label:
        t, s, dd = extra_label; lp = P(s, dd); b += T(lp[0], lp[1] + 5, t, lsize)
    return b

def wires(*pts):
    return ''.join(L(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], INK, 2.2) for i in range(len(pts) - 1))

def node(x, y): return DOT(x, y, 4, INK)
def tag(x, y, s, size=15, color=INK, weight='bold'): return T(x, y, s, size, color=color, weight=weight)
def C(name, w, h, body): save(name, svg(w, h, body))

def two_labels(x, y, top, bottom, size=14):
    """تسميتان فوق بعضهما بجانب عنصر: الرمز (مثل R_A) ثم القيمة."""
    return T(x, y, top, size + 1) + T(x, y + 18, bottom, size)

# ───────────────────────── O09 إضافة أجهزة على التوالي
def o09():
    W = 330; b = ''
    for k, extra in enumerate([False, True]):
        ox = k * W
        b += seg(ox + 50, 230, ox + 50, 70, 'bat', '12.0 V', side=-1, plus='end', ldist=44)
        b += wires((ox + 50, 70), (ox + 90, 70)) + seg(ox + 90, 70, ox + 190, 70, 'R') + T(ox + 140, 50, '20 Ω', 14)
        b += wires((ox + 190, 70), (ox + 270, 70)) + seg(ox + 270, 70, ox + 270, 230, 'R') + T(ox + 305, 155, '40 Ω', 14)
        if extra:
            b += seg(ox + 270, 230, ox + 130, 230, 'R') + T(ox + 200, 262, '60 Ω', 14) + wires((ox + 130, 230), (ox + 50, 230))
        else:
            b += wires((ox + 270, 230), (ox + 50, 230))
        b += T(ox + 170, 24, f'({k + 1})', 17, weight='bold')
    b += L(W, 15, W, 280, GRID, 1.5)
    C('c2l1-o09-add.svg', 2 * W, 285, b)
    # التيار مقابل عدد المصابيح المتماثلة الموصولة على التوالي: أربعة منحنيات مرقمة، تبدأ كلها من 0.60 A لمصباح واحد
    N = [1, 2, 3, 4, 5, 6]
    s1 = [(n, 0.60 / n) for n in N]
    s2 = [(n, 0.60 - 0.10 * (n - 1)) for n in N]
    s3 = [(n, 0.60) for n in N]
    s4 = [(n, 0.60 + 0.10 * (n - 1)) for n in N]
    graph('c2l1-o09-graph.svg', [
        {'pts': s1, 'color': BLUE, 'dots': True, 'label': '(1)', 'at': (6, 0.10), 'dx': 6, 'dy': 4},
        {'pts': s2, 'color': RED, 'dots': True, 'label': '(2)', 'at': (6, 0.10), 'dx': 6, 'dy': 22},
        {'pts': s3, 'color': GREEN, 'dots': True, 'label': '(3)', 'at': (6, 0.60), 'dx': 6, 'dy': 5},
        {'pts': s4, 'color': PURPLE, 'dots': True, 'label': '(4)', 'at': (6, 1.10), 'dx': 6, 'dy': 5}],
        (0, 7), (0, 1.2), 'عدد المصابيح الموصولة على التوالي', 'التيار (A)', xstep=1, ystep=0.2, w=540, h=370)

# ───────────────────────── O10 إضافة أجهزة على التوازي
def o10():
    # بطارية 120 V وفرعان 30 Ω و20 Ω وفرع ثالث 15 Ω فيه مفتاح مفتوح S
    b = seg(50, 260, 50, 60, 'bat', '120 V', side=-1, plus='end', ldist=46)
    b += wires((50, 60), (380, 60)) + wires((50, 260), (380, 260))
    for x, r in [(170, '30 Ω'), (270, '20 Ω')]:
        b += seg(x, 60, x, 260, 'R') + T(x + 36, 165, r, 14) + node(x, 60) + node(x, 260)
    b += seg(380, 60, 380, 150, 'Sopen') + T(412, 110, 'S', 16) + seg(380, 150, 380, 260, 'R') + T(416, 210, '15 Ω', 14)
    C('c2l1-o10-add.svg', 450, 290, b)
    # ثلاثة مصابيح متماثلة على التوازي: L1 دائمًا موصول، وL2 وL3 لكلٍّ منهما مفتاح مفتوح، وأميتر في السلك الرئيس
    b = seg(50, 270, 50, 60, 'bat', None, side=-1, plus='end') + seg(50, 60, 160, 60, 'A') + wires((160, 60), (420, 60))
    b += wires((50, 270), (420, 270))
    b += seg(220, 60, 220, 270, 'lamp') + T(250, 170, 'L_1', 15) + node(220, 60) + node(220, 270)
    for x, s, lb in [(320, 'S_2', 'L_2'), (420, 'S_3', 'L_3')]:
        b += seg(x, 60, x, 150, 'Sopen') + T(x + 30, 112, s, 15) + seg(x, 150, x, 270, 'lamp') + T(x + 30, 216, lb, 15)
        if x == 320: b += node(x, 60) + node(x, 270)
    C('c2l1-o10-lamps.svg', 470, 300, b)
    # مقالي: 60.0 V وفرعان 30.0 Ω و20.0 Ω وفرع ثالث 12.0 Ω فيه مفتاح S، وأميتر في السلك الرئيس
    b = seg(50, 270, 50, 60, 'bat', '60.0 V', side=-1, plus='end', ldist=48) + seg(50, 60, 150, 60, 'A') + wires((150, 60), (430, 60))
    b += wires((50, 270), (430, 270))
    for x, top, val in [(210, 'R_A', '30.0 Ω'), (320, 'R_B', '20.0 Ω')]:
        b += seg(x, 60, x, 270, 'R') + two_labels(x + 40, 160, top, val) + node(x, 60) + node(x, 270)
    b += seg(430, 60, 430, 150, 'Sopen') + T(460, 112, 'S', 16) + seg(430, 150, 430, 270, 'R') + two_labels(472, 205, 'R_C', '12.0 Ω')
    C('c2l1-o10-e3.svg', 520, 300, b)

# ───────────────────────── O11 نموذج النهر الجبلي
def river_steps(name, falls, labels, total_label, w=560, h=330, x0=70, ledge=None):
    """مقطع جانبي لنهر ينحدر في مجرى واحد عبر شلالات متتالية. falls ارتفاعات الشلالات (m)، labels نصوصها."""
    H = sum(falls); top, bot = 70, h - 60; sc = (bot - top) / H
    n = len(falls); ledge = ledge or (w - x0 - 40) / (n + 1)
    pts = [(x0, top)]; x, y = x0, top
    for f in falls:
        x += ledge; pts.append((x, y)); y += f * sc; pts.append((x, y))
    pts.append((x + ledge, y))
    ground = pts + [(pts[-1][0], h - 20), (x0, h - 20)]
    b = '<polygon points="' + ' '.join(f'{px:.1f},{py:.1f}' for px, py in [(p[0], p[1] + 7) for p in pts] + [(pts[-1][0], h - 20), (x0, h - 20)]) + f'" fill="{ROCK}" stroke="none"/>'
    b += '<polyline points="' + ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts) + f'" fill="none" stroke="{WATER}" stroke-width="7" stroke-linejoin="round"/>'
    # أسهم اتجاه الجريان على المصاطب
    for i in range(0, len(pts) - 1, 2):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        mx = (ax + bx) / 2; b += ARROW(mx - 18, ay - 14, mx + 18, ay - 14, WATER, 2, 8)
    # تسميات الشلالات
    for k in range(n):
        (fx, fy1), (_, fy2) = pts[2 * k + 1], pts[2 * k + 2]
        b += L(fx + 14, fy1, fx + 14, fy2, MUTED, 1.2, '4 3') + T(fx + 22, (fy1 + fy2) / 2 + 5, labels[k], 15, 'start')
    # الارتفاع الكلي على اليسار
    b += ARROW(x0 - 30, (top + bot) / 2, x0 - 30, top, INK, 1.5, 8) + ARROW(x0 - 30, (top + bot) / 2, x0 - 30, bot, INK, 1.5, 8)
    b += L(x0 - 40, top, x0 - 10, top, INK, 1.2) + L(x0 - 40, bot, pts[-1][0], bot, MUTED, 1.2, '4 3')
    b += T(x0 - 38, (top + bot) / 2 + 5, total_label, 15, 'end')
    b += T(x0 + 10, top - 36, 'قمة الجبل', 13, 'start', MUTED) + T(pts[-1][0] - 4, bot + 30, 'سفح الجبل', 13, 'end', MUTED)
    C(name, w, h, b)

def o11():
    river_steps('c2l1-o11-series.svg', [40, 35, 25], ['40 m', '؟', '25 m'], '100 m', w=640, x0=110)
    river_steps('c2l1-o11-two.svg', [30, 20], ['الشلال A', 'الشلال B'], '50 m', w=600, x0=100)
    # منظر علوي: نهر يتفرع إلى ثلاثة مجارٍ حول جزيرتين ثم يلتقي
    w, h = 640, 300; b = ''
    yc = 150; xs, xe = 170, 470
    b += f'<rect x="20" y="{yc-16}" width="{xs-20}" height="32" fill="{WATER}" opacity="0.85"/>'
    b += f'<rect x="{xe}" y="{yc-16}" width="{w-20-xe}" height="32" fill="{WATER}" opacity="0.85"/>'
    for yy in (40, 150, 260):
        b += f'<path d="M {xs} {yc} C {xs+60} {yc}, {xs+40} {yy}, {xs+100} {yy} L {xe-100} {yy} C {xe-40} {yy}, {xe-60} {yc}, {xe} {yc}" fill="none" stroke="{WATER}" stroke-width="14" opacity="0.85"/>'
    for yy in (95, 205):
        b += f'<ellipse cx="{(xs+xe)/2}" cy="{yy}" rx="95" ry="22" fill="#cfe3c4" stroke="#7aa36a" stroke-width="1.5"/>'
    b += T((xs + xe) / 2, 99, 'جزيرة', 13, color='#4d7a3e') + T((xs + xe) / 2, 209, 'جزيرة', 13, color='#4d7a3e')
    for yy, q in [(40, '2.0 m³/s'), (150, '3.0 m³/s'), (260, '5.0 m³/s')]:
        b += T((xs + xe) / 2, yy - 13, q, 14)
    b += ARROW(40, yc - 30, 110, yc - 30, INK, 1.8, 9) + T(75, yc - 40, 'الجريان', 13)
    b += T(w - 75, yc - 30, '؟', 18, weight='bold') + ARROW(w - 110, yc + 30, w - 40, yc + 30, INK, 1.8, 9)
    C('c2l1-o11-branch.svg', w, 300, b)

# ───────────────────────── O12 مجزّئ الجهد والمقاومة الضوئية
def o12():
    # مجزّئ جهد: بطارية 12.0 V، R_A = 200 Ω أعلى وR_B = 400 Ω أسفل، وفولتمتر بين طرفي R_B
    b = seg(60, 280, 60, 50, 'bat', '12.0 V', side=-1, plus='end', ldist=46)
    b += wires((60, 50), (230, 50)) + seg(230, 50, 230, 160, 'R') + two_labels(270, 100, 'R_A', '200 Ω')
    b += seg(230, 160, 230, 280, 'R') + two_labels(270, 216, 'R_B', '400 Ω') + wires((230, 280), (60, 280))
    b += node(230, 160) + node(230, 280) + wires((230, 160), (340, 160)) + seg(340, 160, 340, 280, 'V') + wires((340, 280), (230, 280))
    C('c2l1-o12-div.svg', 400, 310, b)
    # مقياس الضوء: مقاومة ضبط الحساسية R_A أعلى، ومجسّ المقاومة الضوئية أسفل، وفولتمتر بين طرفي المجسّ، وأسهم الضوء
    def meter(name, bat, ra):
        b = seg(60, 290, 60, 50, 'bat', bat, side=-1, plus='end', ldist=46)
        b += wires((60, 50), (240, 50)) + seg(240, 50, 240, 160, 'R')
        b += two_labels(282, 92, 'R_A', ra) if ra else T(276, 110, 'R_A', 15)
        b += seg(240, 160, 240, 290, 'LDR') + wires((240, 290), (60, 290)) + T(284, 278, 'مقاومة ضوئية', 13, 'start')
        b += node(240, 160) + node(240, 290) + wires((240, 160), (150, 160)) + seg(150, 160, 150, 290, 'V') + wires((150, 290), (240, 290))
        for k in range(4):
            yy = 196 + k * 16; b += ARROW(345, yy, 282, yy, LIGHT, 2, 9)
        b += T(314, 184, 'ضوء', 13, 'middle', LIGHT)
        C(name, 410, 320, b)
    meter('c2l1-o12-meter.svg', None, None)
    meter('c2l1-o12-e3.svg', '9.0 V', '10 kΩ')

# ───────────────────────── O13 سطوع المصابيح
def o13():
    # L1 في فرع، وL2 وL3 على التوالي في فرع آخر، والفرعان على التوازي مع البطارية (المصابيح متماثلة)
    b = seg(60, 280, 60, 60, 'bat', None, side=-1, plus='end') + wires((60, 60), (330, 60)) + wires((60, 280), (330, 280))
    b += seg(200, 60, 200, 280, 'lamp') + T(228, 175, 'L_1', 15) + node(200, 60) + node(200, 280)
    b += seg(330, 60, 330, 170, 'lamp') + T(358, 120, 'L_2', 15) + seg(330, 170, 330, 280, 'lamp') + T(358, 230, 'L_3', 15)
    C('c2l1-o13-mix.svg', 400, 310, b)

# ───────────────────────── O14 القدرة المستنفدة والقيم الآمنة
def o14():
    b = seg(60, 230, 60, 60, 'bat', None, side=-1, plus='end') + seg(60, 60, 170, 60, 'A') + T(115, 100, '0.30 A', 14)
    b += wires((170, 60), (200, 60)) + seg(200, 60, 320, 60, 'R') + T(260, 36, '18 Ω', 14) + wires((320, 60), (360, 60))
    b += seg(360, 60, 360, 230, 'R') + T(396, 150, '12 Ω', 14) + wires((360, 230), (60, 230))
    C('c2l1-o14-series.svg', 440, 260, b)
    b = seg(60, 230, 60, 60, 'bat', '24.0 V', side=-1, plus='end', ldist=48) + wires((60, 60), (130, 60)) + seg(130, 60, 270, 60, 'R')
    b += two_labels(200, 28, 'R_A', '20.0 Ω') + wires((270, 60), (340, 60)) + seg(340, 60, 340, 230, 'R') + two_labels(386, 140, 'R_B', '60.0 Ω') + wires((340, 230), (60, 230))
    C('c2l1-o14-e1.svg', 450, 260, b)
    # ثلاث مقاومات على التوالي بين طرفين (كالشكل 2-21) مع قدرة كل منها
    b = DOT(30, 90, 4) + wires((30, 90), (60, 90))
    xs = [60, 180, 300, 420]
    for i, (r, p) in enumerate([('100 Ω', '2.0 W'), ('200 Ω', '2.0 W'), ('400 Ω', '2.0 W')]):
        b += seg(xs[i], 90, xs[i + 1], 90, 'R') + T((xs[i] + xs[i + 1]) / 2, 58, r, 14) + T((xs[i] + xs[i + 1]) / 2, 126, p, 13, color=MUTED)
    b += wires((420, 90), (450, 90)) + DOT(450, 90, 4)
    C('c2l1-o14-safe.svg', 480, 150, b)

# ───────────────────────── O15 مختبر دوائر التوالي والتوازي
def o15():
    # التوالي: مصدر قدرة، أميتر، مصباحان L1 وL2، وفولتمتر بين طرفي L1
    b = seg(60, 250, 60, 70, 'bat', 'مصدر قدرة', side=-1, plus='end', ldist=58) + seg(60, 70, 170, 70, 'A') + wires((170, 70), (200, 70))
    b += seg(200, 70, 300, 70, 'lamp') + T(250, 46, 'L_1', 15) + wires((300, 70), (380, 70)) + seg(380, 70, 380, 250, 'lamp') + T(410, 165, 'L_2', 15)
    b += wires((380, 250), (60, 250)) + node(200, 70) + node(300, 70) + wires((200, 70), (200, 140), (215, 140)) + seg(215, 140, 285, 140, 'V') + wires((285, 140), (300, 140), (300, 70))
    C('c2l1-o15-series.svg', 450, 280, b)
    # التوازي: مصدر قدرة، أميتر في السلك الرئيس، L1 وL2 على التوازي، وفولتمتر بين طرفي L1
    b = seg(60, 260, 60, 60, 'bat', 'مصدر قدرة', side=-1, plus='end', ldist=58) + seg(60, 60, 170, 60, 'A') + wires((170, 60), (380, 60)) + wires((60, 260), (380, 260))
    b += seg(250, 60, 250, 260, 'lamp') + T(222, 165, 'L_1', 15) + node(250, 60) + node(250, 260)
    b += seg(380, 60, 380, 260, 'lamp') + T(408, 165, 'L_2', 15)
    b += node(250, 110) + node(250, 210) + wires((250, 110), (310, 110)) + seg(310, 110, 310, 210, 'V') + wires((310, 210), (250, 210))
    C('c2l1-o15-parallel.svg', 450, 290, b)

if __name__ == '__main__':
    o09(); o10(); o11(); o12(); o13(); o14(); o15()
