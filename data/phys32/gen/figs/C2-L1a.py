import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-1 (الأهداف O01–O08): دوائر التوالي والتوازي برموز الكتاب (الشكل 1-5).
# رموز الكميات في الفصل 2 قائمة (غير مائلة) كما يطبعها الكتاب: R_A، V_B، I، A_1 ...
# الدوال المساعدة منسوخة من C1-L1b.py (لا يُعدَّل ملف الفصل 1)، والتسميات كلها قائمة.
import math

METER_FILL = '#e3dff2'; PLUS = '#c0392b'

def _unit(x1, y1, x2, y2):
    d = math.hypot(x2 - x1, y2 - y1); return (x2 - x1) / d, (y2 - y1) / d, d

def seg(x1, y1, x2, y2, comp=None, label=None, side=1, plus='start', lsize=14, ldist=None, extra_label=None):
    """سلك من (x1,y1) إلى (x2,y2) وفي منتصفه عنصر comp:
    'R' مقاومة، 'bat' بطارية (plus = الطرف الموجب: 'start' أو 'end')، 'lamp' مصباح، 'A' أميتر، 'V' فولتمتر،
    'Sopen' / 'Sclosed' مفتاح. label نص بجانب العنصر (side = 1 أو -1). extra_label = (نص، إزاحة على السلك، إزاحة عمودية)."""
    ux, uy, d = _unit(x1, y1, x2, y2); nx, ny = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    half = {'R': 26, 'bat': 13, 'lamp': 14, 'A': 15, 'V': 15, 'Sopen': 20, 'Sclosed': 20, None: 0}[comp]
    b = ''
    if comp is None:
        return L(x1, y1, x2, y2, INK, 2.2)
    b += L(x1, y1, mx - half * ux, my - half * uy, INK, 2.2) + L(mx + half * ux, my + half * uy, x2, y2, INK, 2.2)
    P = lambda s, t: (mx + s * ux + t * nx, my + s * uy + t * ny)
    if comp == 'R':
        pts = [P(-26, 0)]
        n = 6
        for k in range(n):
            pts.append(P(-26 + (k + 0.5) * 52 / n, 9 * (1 if k % 2 == 0 else -1)))
        pts.append(P(26, 0))
        b += '<polyline points="' + ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
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
        dist = ldist or (half + 14 if comp != 'R' else 24)
        if comp == 'bat': dist = ldist or 42
        lp = P(0, -dist * side)
        b += T(lp[0], lp[1] + 5, label, lsize)
    if extra_label:
        t, s, dd = extra_label; lp = P(s, dd); b += T(lp[0], lp[1] + 5, t, lsize)
    return b

def wires(*pts):
    return ''.join(L(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], INK, 2.2) for i in range(len(pts) - 1))

def node(x, y): return DOT(x, y, 4, INK)

def tag(x, y, s, size=16): return T(x, y, s, size, weight='bold')

def C(name, w, h, body): save(name, svg(w, h, body))

def bat_left(x, yb, yt, label=None):
    """بطارية على الضلع الأيسر والموجب في الأعلى، وتسميتها يمينها."""
    return seg(x, yb, x, yt, 'bat', label, side=-1, plus='end', ldist=44)

def parallel(x0, xs, yt, yb, comps, top_from=None):
    """فروع رأسية عند الإحداثيات xs بين السلكين yt وyb. comps = [[(kind, label, extra), ...], ...] لكل فرع
    (عنصر أو عنصران مكدّسان رأسيًّا). يرسم السلكين الأفقيين من x0 إلى آخر فرع، ونقاط التوصيل."""
    b = wires((top_from if top_from is not None else x0, yt), (xs[-1], yt)) + wires((x0, yb), (xs[-1], yb))
    for x, cl in zip(xs, comps):
        n = len(cl); hgt = (yb - yt) / n
        for k, (kind, label, extra) in enumerate(cl):
            b += seg(x, yt + k * hgt, x, yt + (k + 1) * hgt, kind, None, side=1, extra_label=extra)
            if label: b += T(x + (16 if kind == 'R' else 20), yt + (k + 0.5) * hgt + 5, label, 14, 'start')
    for x in xs[:-1]: b += node(x, yt) + node(x, yb)
    return b

# ───────────────────────── O01 وصف دوائر التوالي
def o01():
    # أميترات ثلاثة في دائرة توالٍ فيها مقاومتان
    b = bat_left(60, 230, 60) + seg(60, 60, 190, 60, 'A', extra_label=('A_1', 0, -28)) + seg(190, 60, 330, 60, 'R', 'R_A')
    b += wires((330, 60), (400, 60)) + seg(400, 60, 400, 230, 'A', extra_label=('A_2', 0, -30))
    b += seg(400, 230, 260, 230, 'R', 'R_B', side=1) + seg(260, 230, 140, 230, 'A', extra_label=('A_3', 0, -28)) + wires((140, 230), (60, 230))
    b += T(125, 108, '0.30 A', 14)
    C('c2l1-o01-amps.svg', 460, 280, b)
    # الهبوط في الجهد: فولتمتران بين طرفي R_A وR_B
    b = bat_left(60, 260, 60, '12 V') + wires((60, 60), (150, 60)) + seg(150, 60, 290, 60, 'R', 'R_A', side=1)
    b += wires((290, 60), (380, 60)) + seg(380, 60, 380, 260, 'R', 'R_B', side=-1) + wires((380, 260), (60, 260))
    b += node(150, 60) + node(290, 60) + wires((150, 60), (150, 130), (195, 130)) + seg(195, 130, 245, 130, 'V', extra_label=('V_A', 0, 28)) + wires((245, 130), (290, 130), (290, 60))
    b += node(380, 110) + node(380, 210) + wires((380, 110), (450, 110)) + seg(450, 110, 450, 210, 'V', extra_label=('V_B', 0, -30)) + wires((450, 210), (380, 210))
    C('c2l1-o01-drops.svg', 520, 300, b)
    # ثلاث دوائر لمصباحين: (1) متجاوران على التوالي (2) على التوازي (3) على التوالي في ضلعين متقابلين
    W = 300; b = ''
    ox = 0
    b += bat_left(ox + 50, 230, 80) + wires((ox + 50, 80), (ox + 80, 80)) + seg(ox + 80, 80, ox + 160, 80, 'lamp') + seg(ox + 160, 80, ox + 240, 80, 'lamp')
    b += wires((ox + 240, 80), (ox + 260, 80), (ox + 260, 230), (ox + 50, 230))
    ox = W
    b += bat_left(ox + 50, 230, 80) + wires((ox + 50, 80), (ox + 250, 80)) + seg(ox + 170, 80, ox + 170, 230, 'lamp') + seg(ox + 250, 80, ox + 250, 230, 'lamp')
    b += wires((ox + 250, 230), (ox + 50, 230)) + node(ox + 170, 80) + node(ox + 170, 230)
    ox = 2 * W
    b += bat_left(ox + 50, 230, 80) + wires((ox + 50, 80), (ox + 110, 80)) + seg(ox + 110, 80, ox + 200, 80, 'lamp') + wires((ox + 200, 80), (ox + 260, 80), (ox + 260, 230))
    b += seg(ox + 260, 230, ox + 160, 230, 'lamp') + wires((ox + 160, 230), (ox + 50, 230))
    for k in range(3): b += tag(k * W + 155, 34, f'({k+1})', 17)
    for k in range(1, 3): b += L(k * W, 20, k * W, 260, GRID, 1.5)
    C('c2l1-o01-which.svg', 3 * W, 270, b)
    # مقالي: بطارية 9.0 V ومصباحان مختلفان وثلاثة أميترات وفولتمتر بين طرفي L_1
    b = bat_left(60, 250, 70, '9.0 V') + seg(60, 70, 170, 70, 'A', extra_label=('A_1', 0, -28)) + wires((170, 70), (220, 70)) + seg(220, 70, 320, 70, 'lamp', 'L_1', side=1, ldist=30)
    b += wires((320, 70), (420, 70)) + seg(420, 70, 420, 250, 'A', extra_label=('A_2', 0, -30))
    b += seg(420, 250, 290, 250, 'lamp', 'L_2', side=1, ldist=30) + seg(290, 250, 170, 250, 'A', extra_label=('A_3', 0, -28)) + wires((170, 250), (60, 250))
    b += node(220, 70) + node(320, 70) + wires((220, 70), (220, 140), (245, 140)) + seg(245, 140, 295, 140, 'V') + wires((295, 140), (320, 140), (320, 70))
    b += T(270, 180, '3.0 V', 14)
    C('c2l1-o01-e2.svg', 480, 290, b)

# ───────────────────────── O02 وصف دوائر التوازي
def o02():
    # ثلاثة فروع فيها أميترات بقراءاتها، وأميتر رئيس مجهول القراءة
    b = bat_left(60, 270, 50) + seg(60, 50, 160, 50, 'A', extra_label=('؟', 0, -28))
    b += parallel(60, [200, 300, 400], 50, 270, [[('A', None, ('0.50 A', 0, -42)), ('R', None, None)],
                                                [('A', None, ('1.2 A', 0, -40)), ('R', None, None)],
                                                [('A', None, ('0.30 A', 0, -42)), ('R', None, None)]], top_from=160)
    C('c2l1-o02-amps.svg', 470, 300, b)
    # 9.0 V وثلاث مقاومات على التوازي وفولتمتر بين طرفي 30 Ω
    b = bat_left(60, 240, 60, '9.0 V') + parallel(60, [180, 270, 360], 60, 240, [[('R', '10 Ω', None)], [('R', '20 Ω', None)], [('R', '30 Ω', None)]])
    b += node(360, 60) + node(360, 240) + wires((360, 60), (440, 60)) + seg(440, 60, 440, 240, 'V') + wires((440, 240), (360, 240))
    C('c2l1-o02-volts.svg', 490, 280, b)
    # R_A في السلك الرئيس، ثم R_B وR_C
    b = bat_left(60, 240, 60) + seg(60, 60, 200, 60, 'R', 'R_A', side=1) + parallel(200, [260, 360], 60, 240, [[('R', 'R_B', None)], [('R', 'R_C', None)]])
    b += wires((200, 240), (60, 240)) + node(260, 60) + node(260, 240)
    C('c2l1-o02-mixed.svg', 430, 280, b)
    # مقالي: ثلاثة فروع وقراءات الأميترات وفولتمتر بين طرفي R_A
    b = bat_left(60, 290, 60) + seg(60, 60, 170, 60, 'A')
    b += parallel(60, [220, 320, 420], 60, 290, [[('A', None, ('3.0 A', 0, -40)), ('R', 'R_A', None)],
                                                [('A', None, ('2.0 A', 0, -40)), ('R', 'R_B', None)],
                                                [('A', None, ('1.0 A', 0, -40)), ('R', 'R_C', None)]], top_from=170)
    b += node(220, 185) + node(220, 280 - 20) + wires((220, 185), (170, 185)) + seg(170, 185, 170, 260, 'V', extra_label=('12 V', 0, 40)) + wires((170, 260), (220, 260))
    C('c2l1-o02-e2.svg', 490, 320, b)

# ───────────────────────── O03 الحساب في دوائر التوالي
def o03():
    b = bat_left(60, 230, 60, '24.0 V') + seg(60, 60, 190, 60, 'A') + seg(190, 60, 340, 60, 'R', 'R_A = 33.0 Ω', ldist=26)
    b += wires((340, 60), (380, 60)) + seg(380, 60, 380, 230, 'R', 'R_B = 47.0 Ω', side=1, ldist=62) + wires((380, 230), (60, 230))
    C('c2l1-o03-circ.svg', 500, 270, b)
    b = bat_left(60, 250, 70) + wires((60, 70), (150, 70)) + seg(150, 70, 290, 70, 'R', 'R_A = 120 Ω', side=-1, ldist=26)
    b += wires((290, 70), (370, 70)) + seg(370, 70, 370, 250, 'R', 'R_B = 180 Ω', side=1, ldist=60) + wires((370, 250), (60, 250))
    b += node(150, 70) + node(290, 70) + wires((150, 70), (150, 150), (195, 150)) + seg(195, 150, 245, 150, 'V') + wires((245, 150), (290, 150), (290, 70))
    b += T(220, 190, '6.0 V', 14)
    C('c2l1-o03-meters.svg', 480, 290, b)
    b = bat_left(60, 260, 60, '24.0 V') + seg(60, 60, 170, 60, 'A') + seg(170, 60, 330, 60, 'R', 'R_A = 15.0 Ω', ldist=26)
    b += wires((330, 60), (400, 60)) + seg(400, 60, 400, 260, 'R', 'R_B = 25.0 Ω', side=1, ldist=60) + seg(400, 260, 200, 260, 'R', 'R_C = 40.0 Ω', side=1, ldist=26) + wires((200, 260), (60, 260))
    C('c2l1-o03-e1.svg', 520, 300, b)
    b = bat_left(60, 250, 70, '9.0 V') + seg(60, 70, 150, 70, 'A') + wires((150, 70), (180, 70)) + seg(180, 70, 310, 70, 'R', 'R_A = 180 Ω', side=-1, ldist=26)
    b += wires((310, 70), (380, 70)) + seg(380, 70, 380, 250, 'R', 'R_B', side=1, ldist=30) + wires((380, 250), (60, 250))
    b += node(180, 70) + node(310, 70) + wires((180, 70), (180, 150), (220, 150)) + seg(220, 150, 270, 150, 'V') + wires((270, 150), (310, 150), (310, 70))
    b += T(245, 190, '3.6 V', 14)
    C('c2l1-o03-e2.svg', 450, 290, b)

# ───────────────────────── O04 الحساب في دوائر التوازي
def o04():
    b = bat_left(60, 240, 60, '18.0 V') + seg(60, 60, 170, 60, 'A')
    b += parallel(60, [220, 320, 420], 60, 240, [[('R', '6.0 Ω', None)], [('R', '9.0 Ω', None)], [('R', '18.0 Ω', None)]], top_from=170)
    C('c2l1-o04-three.svg', 500, 280, b)
    b = bat_left(60, 280, 60) + seg(60, 60, 170, 60, 'A', extra_label=('1.50 A', 0, -28))
    b += parallel(60, [240, 380], 60, 280, [[('A', None, ('0.60 A', 0, -42)), ('R', 'R_A = 20.0 Ω', None)], [('R', 'R_B', None)]], top_from=170)
    C('c2l1-o04-find.svg', 470, 310, b)
    b = bat_left(60, 280, 60, '24.0 V') + seg(60, 60, 170, 60, 'A')
    b += parallel(60, [220, 330, 440], 60, 280, [[('A', None, ('I_A', 0, -30)), ('R', 'R_A = 40.0 Ω', None)],
                                                [('A', None, ('I_B', 0, -30)), ('R', 'R_B = 60.0 Ω', None)],
                                                [('A', None, ('I_C', 0, -30)), ('R', 'R_C = 24.0 Ω', None)]], top_from=170)
    C('c2l1-o04-e1.svg', 560, 310, b)
    b = bat_left(60, 260, 60, 'V') + wires((60, 60), (420, 60)) + wires((60, 260), (120, 260)) + seg(120, 260, 220, 260, 'A', extra_label=('A_1', 0, 28)) + wires((220, 260), (420, 260))
    for x, a, r in [(240, 'A_2', '30.0 Ω'), (330, 'A_3', '15.0 Ω'), (420, 'A_4', '10.0 Ω')]:
        b += seg(x, 60, x, 150, 'A', extra_label=(a, 0, -28)) + seg(x, 150, x, 260, 'R', r, side=-1, ldist=34)
    b += node(240, 60) + node(330, 60) + node(240, 260) + node(330, 260)
    C('c2l1-o04-e2.svg', 480, 300, b)

# ───────────────────────── O05 المقارنة بين التوالي والتوازي
def o05():
    W = 330; b = ''
    b += bat_left(50, 240, 80, '6.0 V') + wires((50, 80), (110, 80)) + seg(110, 80, 200, 80, 'R', '10 Ω') + seg(200, 80, 290, 80, 'R', '10 Ω') + wires((290, 80), (300, 80), (300, 240), (50, 240))
    ox = W
    b += bat_left(ox + 50, 240, 80, '6.0 V') + parallel(ox + 50, [ox + 180, ox + 280], 80, 240, [[('R', '10 Ω', None)], [('R', '10 Ω', None)]])
    b += tag(170, 36, 'X', 18) + tag(W + 170, 36, 'Y', 18) + L(W, 20, W, 270, GRID, 1.5)
    C('c2l1-o05-pair.svg', 2 * W, 280, b)
    b = ''
    b += bat_left(50, 240, 80, '12 V') + wires((50, 80), (90, 80)) + seg(90, 80, 190, 80, 'R', '20 Ω') + seg(190, 80, 290, 80, 'R', '30 Ω') + wires((290, 80), (300, 80), (300, 240), (50, 240))
    ox = W
    b += bat_left(ox + 50, 240, 80, '12 V') + parallel(ox + 50, [ox + 180, ox + 280], 80, 240, [[('R', '20 Ω', None)], [('R', '30 Ω', None)]])
    b += tag(170, 36, '(a)', 17) + tag(W + 170, 36, '(b)', 17) + L(W, 20, W, 270, GRID, 1.5)
    C('c2l1-o05-e2.svg', 2 * W, 280, b)

# ───────────────────────── O06 مجزئ الجهد والمقاومة المكافئة
def o06():
    # كالشكل 2-4: البطارية V ومقاومتان على التوالي وفولتمتر بين طرفي R_B
    b = bat_left(60, 270, 50, 'V') + wires((60, 50), (240, 50)) + seg(240, 50, 240, 160, 'R', 'R_A', side=1, ldist=26)
    b += seg(240, 160, 240, 270, 'R', 'R_B', side=1, ldist=26) + wires((240, 270), (60, 270)) + node(240, 160) + node(240, 270)
    b += wires((240, 160), (330, 160)) + seg(330, 160, 330, 270, 'V', extra_label=('V_B', 0, -30)) + wires((330, 270), (240, 270))
    b += ARROW(170, 90, 170, 230, INK, 1.8, 9) + T(155, 165, 'I', 15)
    C('c2l1-o06-div.svg', 400, 300, b)
    # (1) مقاومتان على التوالي، (2) مقاومة مفردة R تعطي التيار نفسه
    W = 330; b = ''
    b += bat_left(50, 240, 80, '12 V') + seg(50, 80, 150, 80, 'A', extra_label=('1.0 A', 0, -28)) + seg(150, 80, 280, 80, 'R', 'R_A = 4.0 Ω', ldist=26)
    b += wires((280, 80), (290, 80)) + seg(290, 80, 290, 240, 'R', 'R_B = 8.0 Ω', side=-1, ldist=58) + wires((290, 240), (50, 240))
    ox = W
    b += bat_left(ox + 50, 240, 80, '12 V') + seg(ox + 50, 80, ox + 150, 80, 'A', extra_label=('1.0 A', 0, -28)) + wires((ox + 150, 80), (ox + 270, 80))
    b += seg(ox + 270, 80, ox + 270, 240, 'R', 'R', side=-1, ldist=28) + wires((ox + 270, 240), (ox + 50, 240))
    b += tag(170, 36, '(1)', 17) + tag(W + 170, 36, '(2)', 17) + L(W, 20, W, 270, GRID, 1.5)
    C('c2l1-o06-eq.svg', 2 * W, 280, b)

# ───────────────────────── O07 الغرض من التوصيل على التوالي
def o07():
    b = bat_left(60, 230, 60, '9.0 V') + wires((60, 60), (130, 60)) + seg(130, 60, 290, 60, 'R', 'R', ldist=26)
    b += wires((290, 60), (360, 60)) + seg(360, 60, 360, 230, 'lamp', 'مصباح', side=1, ldist=44) + T(404, 166, '6.0 V', 14) + wires((360, 230), (60, 230))
    C('c2l1-o07-lamp.svg', 480, 270, b)
    W = 300; b = ''
    for k in range(3):
        ox = k * W
        b += bat_left(ox + 50, 230, 80)
        if k == 0:
            b += wires((ox + 50, 80), (ox + 230, 80)) + seg(ox + 230, 80, ox + 230, 230, 'lamp') + wires((ox + 230, 230), (ox + 50, 230))
        if k == 1:
            b += wires((ox + 50, 80), (ox + 100, 80)) + seg(ox + 100, 80, ox + 200, 80, 'R', 'R') + wires((ox + 200, 80), (ox + 230, 80))
            b += seg(ox + 230, 80, ox + 230, 230, 'lamp') + wires((ox + 230, 230), (ox + 50, 230))
        if k == 2:
            b += parallel(ox + 50, [ox + 170, ox + 250], 80, 230, [[('lamp', None, None)], [('R', 'R', None)]])
        b += tag(ox + 150, 36, f'({k+1})', 17)
    for k in range(1, 3): b += L(k * W, 20, k * W, 260, GRID, 1.5)
    C('c2l1-o07-choose.svg', 3 * W, 270, b)

# ───────────────────────── O08 الغرض من التوصيل على التوازي
def o08():
    # دائرة منزلية: مصدر 120 V وثلاثة أجهزة على التوازي، لكل منها مفتاح؛ مفتاح الغلاية مفتوح
    b = bat_left(60, 290, 50, '120 V')
    xs = [200, 330, 460]
    b += wires((60, 50), (460, 50)) + wires((60, 290), (460, 290))
    for x, comp_, name, sw in [(200, 'lamp', 'مصباح', 'Sclosed'), (330, 'R', 'غلاية', 'Sopen'), (460, 'R', 'تلفاز', 'Sclosed')]:
        b += seg(x, 50, x, 150, sw) + seg(x, 150, x, 290, comp_, name, side=-1, ldist=40 if comp_ == 'R' else 46)
    b += node(200, 50) + node(330, 50) + node(200, 290) + node(330, 290)
    C('c2l1-o08-house.svg', 540, 320, b)
    W = 330; b = ''
    b += bat_left(50, 240, 80, '12 V') + wires((50, 80), (70, 80)) + seg(70, 80, 150, 80, 'lamp') + seg(150, 80, 230, 80, 'lamp') + seg(230, 80, 300, 80, 'lamp') + wires((300, 80), (300, 240), (50, 240))
    ox = W
    b += bat_left(ox + 50, 240, 80, '12 V') + parallel(ox + 50, [ox + 150, ox + 220, ox + 290], 80, 240, [[('lamp', None, None)], [('lamp', None, None)], [('lamp', None, None)]])
    b += tag(170, 36, 'X', 18) + tag(W + 170, 36, 'Y', 18) + L(W, 20, W, 270, GRID, 1.5)
    C('c2l1-o08-lamps.svg', 2 * W, 280, b)

if __name__ == '__main__':
    o01(); o02(); o03(); o04(); o05(); o06(); o07(); o08()
