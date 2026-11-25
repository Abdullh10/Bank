import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-2 تطبيقات الدوائر الكهربائية (الأهداف O01–O09): أدوات السلامة، والدوائر المركّبة، والأميتر والفولتمتر،
# ودوائر المنازل. رموز الدوائر منسوخة من data/phys32/gen/figs/C1-L1b.py (رموز الكتاب ص 19)، مع إضافة رمز المنصهر الكهربائي
# كما يطبعه الكتاب (منحنى على شكل S). رموز الكميات قائمة (غير مائلة) كما يطبعها الفصل الثاني: R_A، V، I.
import math

METER_FILL = '#e3dff2'; PLUS = '#c0392b'

def _unit(x1, y1, x2, y2):
    d = math.hypot(x2 - x1, y2 - y1); return (x2 - x1) / d, (y2 - y1) / d, d

def seg(x1, y1, x2, y2, comp=None, label=None, side=1, plus='start', lsize=14, ldist=None, extra_label=None, mlabel=None):
    """سلك من (x1,y1) إلى (x2,y2) وفي منتصفه عنصر comp:
    'R' مقاومة، 'bat' بطارية (plus = الطرف الموجب)، 'lamp' مصباح، 'A' أميتر، 'V' فولتمتر، 'X' جهاز قياس بحرف mlabel،
    'F' منصهر كهربائي، 'Sopen' / 'Sclosed' مفتاح. label نص قائم بجانب العنصر (side = 1 أو -1)."""
    ux, uy, d = _unit(x1, y1, x2, y2); nx, ny = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    half = {'R': 26, 'bat': 13, 'lamp': 14, 'A': 15, 'V': 15, 'X': 15, 'F': 16, 'Sopen': 20, 'Sclosed': 20, None: 0}[comp]
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
    elif comp == 'F':
        # رمز المنصهر في الكتاب: نصف دائرة إلى جهة ثم نصف دائرة إلى الجهة الأخرى (شكل S ممدود)
        a = P(-16, 0); m = P(0, 0); c = P(16, 0)
        sw1 = 1; sw2 = 0
        b += f'<path d="M {a[0]:.1f} {a[1]:.1f} A 8 8 0 0 {sw1} {m[0]:.1f} {m[1]:.1f} A 8 8 0 0 {sw2} {c[0]:.1f} {c[1]:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
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
    elif comp in ('A', 'V', 'X'):
        b += f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="15" fill="{METER_FILL}" stroke="{INK}" stroke-width="2"/>' + T(mx, my + 5.5, mlabel or comp, 16, color=INK)
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
def tag(x, y, s, size=15, color=INK, weight='bold'): return T(x, y, s, size, color=color, weight=weight)
def C(name, w, h, body): save(name, svg(w, h, body))

def mains(x, ytop, ybot, label='120 V'):
    """مصدر جهد المنزل كما في الكتاب: طرفا سلكين مفتوحان على اليسار وبينهما قيمة الجهد."""
    return (L(x, ytop, x, ytop + 38, INK, 2.2) + L(x, ybot, x, ybot - 38, INK, 2.2)
            + L(x - 22, ytop + 38, x, ytop + 38, INK, 2.2) + L(x - 22, ybot - 38, x, ybot - 38, INK, 2.2)
            + T(x - 8, (ytop + ybot) / 2 + 5, label, 15, 'end'))

def iarrow(x, y, direction, label='I', length=34, side=-1):
    dx, dy = {'right': (1, 0), 'left': (-1, 0), 'up': (0, -1), 'down': (0, 1)}[direction]
    x1, y1 = x - dx * length / 2, y - dy * length / 2; x2, y2 = x + dx * length / 2, y + dy * length / 2
    b = ARROW(x1, y1, x2, y2, INK, 1.8, 9)
    if label:
        if dy == 0: b += T(x, y - 8 if side < 0 else y + 18, label, 15)
        else: b += T(x + (14 if side > 0 else -14), y + 5, label, 15)
    return b

# ───────────────────────── O01
def o01():
    # أربع دوائر: (1) توالٍ، (2) توازٍ، (3) مركّبة، (4) توالٍ مع أميتر
    W = 250; b = ''
    for k in range(4):
        ox = k * W; x1, x2, y1, y2 = ox + 40, ox + 200, 70, 220
        b += seg(x1, y2, x1, y1, 'bat', None, plus='end')
        if k == 0:
            b += seg(x1, y1, x1 + 80, y1, 'R') + seg(x1 + 80, y1, x2, y1, 'R') + seg(x2, y1, x2, y2, 'R') + wires((x2, y2), (x1, y2))
        if k == 1:
            b += wires((x1, y1), (x2, y1)) + wires((x1, y2), (x2, y2))
            for xx in (x1 + 60, x1 + 110, x2): b += seg(xx, y1, xx, y2, 'R')
            b += node(x1 + 60, y1) + node(x1 + 110, y1) + node(x1 + 60, y2) + node(x1 + 110, y2)
        if k == 2:
            b += seg(x1, y1, x1 + 90, y1, 'R') + wires((x1 + 90, y1), (x2, y1)) + wires((x1, y2), (x2, y2))
            for xx in (x1 + 110, x2): b += seg(xx, y1, xx, y2, 'R')
            b += node(x1 + 110, y1) + node(x1 + 110, y2)
        if k == 3:
            b += seg(x1, y1, x1 + 80, y1, 'A') + seg(x1 + 80, y1, x2, y1, 'R') + seg(x2, y1, x2, y2, 'R') + wires((x2, y2), (x1, y2))
        b += T(ox + 125, 36, f'({k+1})', 17, weight='bold')
    for k in range(1, 4): b += L(k * W, 20, k * W, 245, GRID, 1.5)
    C('c2l2-o01-kinds.svg', 4 * W, 255, b)
    # دائرة قصر: سلك XY يصل طرفي المصباح مباشرة
    b = seg(60, 230, 60, 60, 'bat', '6.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (300, 60), (300, 90))
    b += seg(300, 90, 300, 200, 'lamp') + wires((300, 200), (300, 230), (60, 230)) + node(300, 90) + node(300, 200)
    b += wires((300, 90), (390, 90), (390, 200), (300, 200)) + tag(312, 82, 'X') + tag(312, 218, 'Y')
    C('c2l2-o01-short.svg', 450, 270, b)

# ───────────────────────── O02 قاطع التفريغ الأرضي الخاطئ
def o02():
    b = ''
    # السلكان: الحي (أعلى) والمتعادل (أسفل) يمران خلال حلقة المحوّل
    b += L(40, 110, 610, 110, INK, 3) + L(40, 170, 610, 170, INK, 3)
    b += f'<ellipse cx="200" cy="140" rx="26" ry="62" fill="none" stroke="#6f86a8" stroke-width="12" opacity="0.75"/>'
    b += T(200, 230, 'المحوّل', 15, color=MUTED)
    b += T(590, 98, 'السلك الحي', 14, 'end', MUTED) + T(590, 194, 'السلك المتعادل', 14, 'end', MUTED)
    b += T(40, 140, 'المصدر', 14, 'start', MUTED) + RECT(610, 95, 70, 90, INK, '#f3efe6') + T(645, 145, 'الجهاز', 14)
    b += ARROW(330, 96, 400, 96, C_FORCE if False else INK, 2.2) + T(365, 82, '2.500 A', 15)
    b += ARROW(400, 184, 330, 184, INK, 2.2) + T(365, 206, '2.495 A', 15)
    C('c2l2-o02-gfci.svg', 700, 250, b)

# ───────────────────────── O03 موضع المنصهر
def house(name, lab_fuse=None, devices=('', '', ''), points=False, fuse_where='main', w=520, h=290, dev_labels=None, source='120 V'):
    """دائرة منزلية: مصدر 120 V، وثلاثة أجهزة (مقاومات) على التوازي؛ fuse_where: 'main' أو 'none' أو 'parallel' (بين السلكين قبل الأجهزة) أو 'branch1'."""
    y1, y2 = 60, 240; x0 = 70
    b = mains(x0, y1, y2, source)
    xs = [270, 360, 450]
    if fuse_where == 'main':
        b += wires((x0, y1), (130, y1)) + seg(130, y1, 210, y1, 'F') + wires((210, y1), (xs[-1], y1))
        if lab_fuse: b += T(166, y1 - 18, lab_fuse, 14, 'end') + T(174, y1 - 18, 'منصهر', 14, 'start')
    elif fuse_where == 'parallel':
        b += wires((x0, y1), (xs[-1], y1)) + node(170, y1) + node(170, y2) + seg(170, y1, 170, y2, 'F') + T(186, 155, 'منصهر', 13, 'start')
    else:
        b += wires((x0, y1), (xs[-1], y1))
    b += wires((x0, y2), (xs[-1], y2))
    for i, xx in enumerate(xs):
        if fuse_where == 'branch1' and i == 0:
            b += seg(xx, y1, xx, 120, 'F') + T(xx - 16, 95, 'منصهر', 13, 'end') + seg(xx, 120, xx, y2, 'R')
        else:
            b += seg(xx, y1, xx, y2, 'R')
        if i < 2: b += node(xx, y1) + node(xx, y2)
        if dev_labels: b += T(xx + 14, 160, dev_labels[i], 13, 'start')
    if points:
        for (x, y, s) in [(110, y1, 'P'), (315, y1, 'Q'), (450, 105, 'S'), (315, y2, 'T')]:
            b += DOT(x, y, 5, ORANGE) + tag(x + (14 if s == 'S' else 0), y - 12 if s != 'T' else y + 24, s)
    C(name, w, h, b)

def o03():
    house('c2l2-o03-points.svg', points=True, fuse_where='none', dev_labels=['تلفاز', 'مكواة', 'مصباح'])
    house('c2l2-o03-e1.svg', lab_fuse='15 A', dev_labels=['تلفاز', 'مكواة', 'مجفف'])
    house('c2l2-o03-wrong.svg', fuse_where='parallel', dev_labels=['تلفاز', 'مكواة', 'مصباح'])
    house('c2l2-o03-branch.svg', fuse_where='branch1', dev_labels=['مكواة', 'تلفاز', 'مصباح'])

# ───────────────────────── O04 الأميتر والفولتمتر
def o04():
    # جهازا قياس X وY: X على التوالي في السلك الرئيس، وY بين طرفي R_B
    b = seg(60, 240, 60, 60, 'bat', '12 V', side=-1, plus='end', ldist=40) + seg(60, 60, 180, 60, 'X', mlabel='X')
    b += seg(180, 60, 320, 60, 'R', 'R_A') + wires((320, 60), (360, 60), (360, 100)) + seg(360, 100, 360, 200, 'R', 'R_B', side=-1)
    b += wires((360, 200), (360, 240), (60, 240)) + node(360, 100) + node(360, 200)
    b += wires((360, 100), (440, 100)) + seg(440, 100, 440, 200, 'X', mlabel='Y') + wires((440, 200), (360, 200))
    C('c2l2-o04-xy.svg', 490, 280, b)
    # نقاط a b c d على دائرة توالٍ فيها R_1 وR_2
    b = seg(60, 240, 60, 60, 'bat', '9.0 V', side=-1, plus='end', ldist=40) + wires((60, 60), (110, 60)) + seg(110, 60, 250, 60, 'R', 'R_1')
    b += wires((250, 60), (340, 60)) + seg(340, 60, 340, 240, 'R', 'R_2', side=-1) + wires((340, 240), (60, 240))
    for x, y, s, dx, dy in [(110, 60, 'a', 0, -14), (250, 60, 'b', 0, -14), (340, 105, 'c', 16, 5), (340, 195, 'd', 16, 5)]:
        b += DOT(x, y, 4.5) + tag(x + dx, y + dy, s, 16, weight='normal')
    C('c2l2-o04-points.svg', 400, 280, b)
    # تبديل الجهازين: فولتمتر على التوالي مع المصباح، وأميتر بين طرفي المصباح
    b = seg(60, 240, 60, 60, 'bat', '6.0 V', side=-1, plus='end', ldist=40) + seg(60, 60, 200, 60, 'V')
    b += wires((200, 60), (320, 60), (320, 100)) + seg(320, 100, 320, 200, 'lamp') + wires((320, 200), (320, 240), (60, 240))
    b += node(320, 100) + node(320, 200) + wires((320, 100), (400, 100)) + seg(400, 100, 400, 200, 'A') + wires((400, 200), (320, 200))
    C('c2l2-o04-swap.svg', 450, 280, b)

# ───────────────────────── O05 الدوائر المركّبة
def vres(x, y1, y2, name=None, val=None, left=False):
    """مقاومة رأسية واسمها وقيمتها بجانبها (يمينًا افتراضيًّا)."""
    m = (y1 + y2) / 2; dx = -16 if left else 16; an = 'end' if left else 'start'
    b = seg(x, y1, x, y2, 'R')
    if name and val: b += T(x + dx, m - 4, name, 14, an) + T(x + dx, m + 16, val, 14, an)
    elif name or val: b += T(x + dx, m + 5, name or val, 14, an)
    return b

def o05():
    # (a) 24.0 V، R_A = 4.0 Ω على التوالي مع R_B = 6.0 Ω || R_C = 12.0 Ω
    b = seg(60, 240, 60, 60, 'bat', '24.0 V', side=-1, plus='end', ldist=46) + wires((60, 60), (90, 60)) + seg(90, 60, 230, 60, 'R', 'R_A', extra_label=('4.0 Ω', 0, 26))
    b += wires((230, 60), (400, 60)) + wires((60, 240), (400, 240)) + node(280, 60) + node(280, 240)
    b += vres(280, 60, 240, 'R_B', '6.0 Ω') + vres(400, 60, 240, 'R_C', '12.0 Ω')
    C('c2l2-o05-a.svg', 480, 280, b)
    # (b) 36.0 V، R_1 = 12.0 Ω ثم فرعان: (8.0 + 16.0) و(12.0 + 12.0)
    b = seg(60, 280, 60, 60, 'bat', '36.0 V', side=-1, plus='end', ldist=46) + wires((60, 60), (90, 60)) + seg(90, 60, 230, 60, 'R', 'R_1', extra_label=('12.0 Ω', 0, 26))
    b += wires((230, 60), (420, 60)) + wires((60, 280), (420, 280)) + node(300, 60) + node(300, 280)
    b += vres(300, 60, 170, val='8.0 Ω') + vres(300, 170, 280, val='16.0 Ω') + vres(420, 60, 170, val='12.0 Ω') + vres(420, 170, 280, val='12.0 Ω')
    C('c2l2-o05-b.svg', 500, 320, b)
    # (c) 18 V، R_1 = 6.0 Ω على التوالي مع [R_2 = 12 Ω || (R_3 = 4.0 Ω + R_4 = 8.0 Ω)]
    b = seg(60, 280, 60, 60, 'bat', '18 V', side=-1, plus='end', ldist=44) + wires((60, 60), (90, 60)) + seg(90, 60, 230, 60, 'R', 'R_1', extra_label=('6.0 Ω', 0, 26))
    b += wires((230, 60), (420, 60)) + wires((60, 280), (420, 280)) + node(300, 60) + node(300, 280)
    b += vres(300, 60, 280, 'R_2', '12 Ω') + vres(420, 60, 170, 'R_3', '4.0 Ω') + vres(420, 170, 280, 'R_4', '8.0 Ω')
    C('c2l2-o05-c.svg', 500, 320, b)
    # (e1) 60.0 V، R_A = 10.0 Ω على التوالي مع R_B = 20.0 || R_C = 30.0 || R_D = 60.0
    b = seg(60, 240, 60, 60, 'bat', '60.0 V', side=-1, plus='end', ldist=46) + wires((60, 60), (90, 60)) + seg(90, 60, 220, 60, 'R', 'R_A', extra_label=('10.0 Ω', 0, 26))
    b += wires((220, 60), (520, 60)) + wires((60, 240), (520, 240))
    for xx, lb, v in [(280, 'R_B', '20.0 Ω'), (400, 'R_C', '30.0 Ω'), (520, 'R_D', '60.0 Ω')]:
        b += vres(xx, 60, 240, lb, v)
    b += node(280, 60) + node(280, 240) + node(400, 60) + node(400, 240)
    C('c2l2-o05-e1.svg', 600, 280, b)

# ───────────────────────── O06 مقاومة الأميتر
def o06():
    b = seg(60, 240, 60, 60, 'bat', '9.00 V', side=-1, plus='end', ldist=46) + seg(60, 60, 180, 60, 'A')
    b += seg(180, 60, 330, 60, 'R', 'R_A', extra_label=('3.00 Ω', 0, 26)) + wires((330, 60), (380, 60))
    b += vres(380, 60, 240, 'R_B', '6.00 Ω') + wires((380, 240), (60, 240))
    C('c2l2-o06-amm.svg', 460, 280, b)

# ───────────────────────── O07 مقاومة الفولتمتر
def o07():
    def vm(name, volt, ra, rb):
        b = seg(60, 260, 60, 60, 'bat', volt, side=-1, plus='end', ldist=46) + wires((60, 60), (240, 60))
        b += vres(240, 60, 150, 'R_A', ra, left=True) + vres(240, 150, 260, 'R_B', rb, left=True) + wires((240, 260), (60, 260))
        b += node(240, 150) + node(240, 260) + wires((240, 150), (360, 150)) + seg(360, 150, 360, 260, 'V') + wires((360, 260), (240, 260))
        C(name, 420, 300, b)
    vm('c2l2-o07-vm.svg', '12.0 V', '20.0 Ω', '20.0 Ω')
    vm('c2l2-o07-e2.svg', '9.0 V', '1.0 kΩ', '1.0 kΩ')


# ───────────────────────── O08 تيار المنصهر في دائرة المنزل
def appliances(name, lab_fuse, devs, w=590, h=300):
    y1, y2 = 60, 250; x0 = 70
    b = mains(x0, y1, y2) + wires((x0, y1), (120, y1)) + seg(120, y1, 200, y1, 'F') + T(156, y1 - 18, lab_fuse, 14, 'end') + T(164, y1 - 18, 'منصهر', 14, 'start')
    xs = [270, 370, 470][:len(devs)]
    b += wires((200, y1), (xs[-1], y1)) + wires((x0, y2), (xs[-1], y2))
    for i, (xx, (nm, pw)) in enumerate(zip(xs, devs)):
        b += seg(xx, y1, xx, y2, 'R') + T(xx + 16, 150, nm, 13, 'start') + T(xx + 16, 172, pw, 13, 'start')
        if i < len(xs) - 1: b += node(xx, y1) + node(xx, y2)
    C(name, w, h, b)

def o08():
    appliances('c2l2-o08-house.svg', '15 A', [('تلفاز', '120 W'), ('مكواة', '960 W'), ('غلاية', '1200 W')])
    appliances('c2l2-o08-e1.svg', '15 A', [('تلفاز', '180 W'), ('مكواة', '1080 W'), ('مجفف شعر', '600 W')])

# ───────────────────────── O09 ضعف الإضاءة
def o09():
    # نوعي: مصدر 120 V، منصهر، مقاومة أسلاك صغيرة على التوالي، مصباح، ومجفف شعر بمفتاح S
    y1, y2 = 60, 260; x0 = 70
    def base(lab_wire, lamp_lab, dry_lab):
        b = mains(x0, y1, y2) + wires((x0, y1), (110, y1)) + seg(110, y1, 170, y1, 'F') + seg(170, y1, 300, y1, 'R') + T(235, y1 + 34, lab_wire, 13)
        b += wires((300, y1), (460, y1)) + wires((x0, y2), (460, y2)) + node(340, y1) + node(340, y2)
        b += seg(340, y1, 340, y2, 'lamp') + T(318, 165, lamp_lab, 13, 'end')
        b += seg(460, y1, 460, 150, 'Sopen') + T(476, 110, 'S', 15, 'start') + seg(460, 150, 460, y2, 'R') + T(478, 210, dry_lab, 13, 'start')
        return b
    C('c2l2-o09-house.svg', 600, 300, base('مقاومة أسلاك التمديدات', 'مصباح', 'مجفف شعر'))
    b = mains(x0, y1, y2) + wires((x0, y1), (140, y1)) + seg(140, y1, 280, y1, 'R') + T(210, y1 - 22, '1.6 Ω', 14) + T(210, y1 + 36, 'مقاومة الأسلاك', 13)
    b += wires((280, y1), (460, y1)) + wires((x0, y2), (460, y2)) + node(340, y1) + node(340, y2)
    b += seg(340, y1, 340, y2, 'lamp') + T(318, 155, 'مصباح', 13, 'end') + T(318, 177, '144 Ω', 13, 'end')
    b += seg(460, y1, 460, 150, 'Sopen') + T(476, 110, 'S', 15, 'start') + seg(460, 150, 460, y2, 'R') + T(478, 200, 'مجفف شعر', 13, 'start') + T(478, 222, '16.0 Ω', 13, 'start')
    C('c2l2-o09-calc.svg', 600, 300, b)
    # مقالي: سلكان مقاومة كل منهما 0.30 Ω يصلان مصباحًا 200 Ω، ومأخذ لجهاز آخر
    b = mains(x0, y1, y2) + wires((x0, y1), (120, y1)) + seg(120, y1, 240, y1, 'R') + T(180, y1 - 22, '0.30 Ω', 14)
    b += wires((x0, y2), (120, y2)) + seg(120, y2, 240, y2, 'R') + T(180, y2 + 32, '0.30 Ω', 14)
    b += wires((240, y1), (440, y1)) + wires((240, y2), (440, y2)) + node(320, y1) + node(320, y2)
    b += seg(320, y1, 320, y2, 'lamp') + T(298, 155, 'مصباح', 13, 'end') + T(298, 177, '200 Ω', 13, 'end')
    b += seg(440, y1, 440, 150, 'Sopen') + T(456, 110, 'S', 15, 'start') + seg(440, 150, 440, y2, 'R') + T(458, 200, 'مدفأة', 13, 'start') + T(458, 222, '12.0 Ω', 13, 'start')
    C('c2l2-o09-e3.svg', 560, 300, b)

if __name__ == '__main__':
    o01(); o02(); o03(); o04(); o05(); o06(); o07(); o08(); o09()
