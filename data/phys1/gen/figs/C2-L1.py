import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-1 تصوير الحركة — الأهداف O01–O08 (المخطط التوضيحي للحركة ونموذج الجسيم النقطي)

CAR = '#2e86c1'; ROAD = '#e8e8e8'; TREE = '#3d8b4f'; TRUNK = '#8a5a2b'


def car(x, y, op=1.0, color=CAR, sc=1.0):
    """سيارة متجهة يمينًا: x الطرف الأيسر، y مستوى الأرض. الطول 70×sc."""
    if sc != 1.0:
        return f'<g transform="translate({x:.1f} {y:.1f}) scale({sc})">' + car(0, 0, op, color) + '</g>'
    g = f'<g opacity="{op}">'
    g += f'<rect x="{x:.1f}" y="{y - 26:.1f}" width="70" height="16" rx="5" fill="{color}" stroke="{INK}" stroke-width="1.3"/>'
    g += f'<polygon points="{x + 16:.1f},{y - 26:.1f} {x + 24:.1f},{y - 38:.1f} {x + 48:.1f},{y - 38:.1f} {x + 57:.1f},{y - 26:.1f}" fill="{color}" stroke="{INK}" stroke-width="1.3"/>'
    g += f'<polygon points="{x + 27:.1f},{y - 28:.1f} {x + 30:.1f},{y - 35:.1f} {x + 45:.1f},{y - 35:.1f} {x + 50:.1f},{y - 28:.1f}" fill="#dff1fb"/>'
    g += DOT(x + 16, y - 8, 7, INK, '#444') + DOT(x + 54, y - 8, 7, INK, '#444') + '</g>'
    return g


def tree(x, y):
    return RECT(x - 5, y - 45, 10, 45, TRUNK, TRUNK, 1) + f'<circle cx="{x}" cy="{y - 62}" r="26" fill="{TREE}" opacity="0.9"/>'


def runner(x, y, color=INK, phase=0):
    """عدّاء مبسط: x محور الجسم، y مستوى القدمين. phase يبدّل وضع الأطراف."""
    s = 1 if phase % 2 == 0 else -1
    b = f'<circle cx="{x + 3}" cy="{y - 62}" r="8" fill="none" stroke="{color}" stroke-width="2.5"/>'
    b += L(x + 2, y - 54, x, y - 30, color, 3)  # الجذع
    b += L(x + 1, y - 46, x + 12 * s, y - 38, color, 2.5) + L(x + 12 * s, y - 38, x + 16 * s, y - 46, color, 2.5)
    b += L(x + 1, y - 46, x - 10 * s, y - 40, color, 2.5)
    b += L(x, y - 30, x + 12 * s, y - 16, color, 2.5) + L(x + 12 * s, y - 16, x + 10 * s, y, color, 2.5)
    b += L(x, y - 30, x - 8 * s, y - 15, color, 2.5) + L(x - 8 * s, y - 15, x - 16 * s, y - 4, color, 2.5)
    return b


def ruler(x0, x1, y, vmin, vmax, step, label_every=1, unit='cm'):
    P = lambda v: x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)
    b = RECT(x0 - 8, y, x1 - x0 + 16, 26, MUTED, '#fbf3d9', 1.2)
    n = round((vmax - vmin) / step)
    for i in range(n + 1):
        v = vmin + i * step
        b += L(P(v), y, P(v), y + 9, INK, 1.3)
        if i % label_every == 0: b += T(P(v), y + 22, fmt(round(v, 6)), 11, color=INK)
    b += T(x1 + 12, y + 18, unit, 12, 'start', MUTED)
    return b, P


def dot_rows(name, rows, w=600, row_h=62, x0=40, x1=None, scale=None, top=38, label_w=0):
    """صفوف نقاط مرقمة. rows = [ {title, xs (px), color?, vel?, arrow? ('→'/'←' اتجاه الحركة)} ].
    scale = (vmin, vmax, step, unit) لمحور مدرّج أسفل الصفوف."""
    x1 = x1 or w - 30
    H = top + len(rows) * row_h + (60 if scale else 10)
    b = ''
    for i, r in enumerate(rows):
        y = top + i * row_h + 20
        if r.get('title'): b += T(w - 12, y + 5, r['title'], 14, 'end', MUTED, 'bold')
        b += L(x0 - 10, y + 12, x1 + 4, y + 12, GRID, 1)
        for k, x in enumerate(r['xs']):
            b += DOT(x, y, 6, r.get('color', INK))
            if r.get('vel') and k + 1 < len(r['xs']) and r['xs'][k + 1] != x:
                b += ARROW(x, y - 14, x + 0.85 * (r['xs'][k + 1] - x), y - 14, C_VEL, 2.2, 9)
        if r.get('arrow'):
            ax = x0 + 6 if r['arrow'] == '←' else x0 + 6
            d = 36 if r['arrow'] == '→' else -36
            xs0 = x0 if d > 0 else x0 + 36
            b += ARROW(xs0, y - 24, xs0 + d, y - 24, INK, 2) + T(x0 + 44, y - 19, 'اتجاه الحركة', 12, 'start', MUTED)
    if scale:
        vmin, vmax, step, unit = scale
        ya = top + len(rows) * row_h + 14
        P = lambda v: x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)
        b += ARROW(x0 - 12, ya, x1 + 18, ya, INK, 1.6)
        n = round((vmax - vmin) / step)
        for i in range(n + 1):
            v = vmin + i * step
            b += L(P(v), ya - 5, P(v), ya + 5, INK, 1.3) + T(P(v), ya + 20, fmt(round(v, 6)), 12, color=MUTED)
        b += T((x0 + x1) / 2, ya + 40, unit, 13)
    save(name, svg(w, H, b))


def px(vals, vmin, vmax, x0=40, x1=570):
    return [x0 + (v - vmin) / (vmax - vmin) * (x1 - x0) for v in vals]


# ================= O01 أنواع الحركة بحسب المسار =================
def paths_panel(name):
    pw, ph = 280, 190; b = ''
    for i in range(4):
        ox, oy = (i % 2) * pw, (i // 2) * ph
        b += f'<rect x="{ox + 3}" y="{oy + 3}" width="{pw - 6}" height="{ph - 6}" fill="none" stroke="{GRID}" stroke-width="1.5"/>'
        b += T(ox + pw - 22, oy + 26, f'({i + 1})', 15, weight='bold')
    # (1) منحنى: كرة تُركل فوق سياج
    ox, oy = 0, 0
    b += L(ox + 20, oy + 160, ox + 260, oy + 160, INK, 2)
    b += RECT(ox + 132, oy + 110, 8, 50, MUTED, '#c9b38a', 1)
    pts = [(ox + 30 + t * 22, oy + 155 - (t * (10 - t)) * 4.8) for t in range(0, 11)]
    b += '<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 5"/>'
    for t in (0, 3, 7, 10): b += DOT(*pts[t], 7, INK, '#fff')
    # (2) خط مستقيم
    ox, oy = pw, 0
    b += RECT(ox + 20, oy + 120, 240, 34, MUTED, ROAD, 1) + L(ox + 26, oy + 137, ox + 254, oy + 137, '#fff', 2, '12 10')
    b += car(ox + 40, oy + 150) + ARROW(ox + 120, oy + 95, ox + 240, oy + 95, MUTED, 2)
    # (3) اهتزاز (تأرجح): بندول
    ox, oy = 0, ph
    cx, cy = ox + 140, oy + 40
    b += L(cx - 50, cy, cx + 50, cy, INK, 3)
    for a, op in ((-35, 0.35), (0, 1), (35, 0.35)):
        r = math.radians(a); x2, y2 = cx + 105 * math.sin(r), cy + 105 * math.cos(r)
        b += f'<g opacity="{op}">' + L(cx, cy, x2, y2, INK, 1.8) + DOT(x2, y2, 10, INK, '#ddd') + '</g>'
    b += f'<path d="M {cx - 72:.1f} {cy + 98:.1f} A 125 125 0 0 0 {cx + 72:.1f} {cy + 98:.1f}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5 4"/>'
    b += ARROW(cx + 52, cy + 113, cx + 72, cy + 98, MUTED, 2, 9) + ARROW(cx - 52, cy + 113, cx - 72, cy + 98, MUTED, 2, 9)
    # (4) دائرة: مضمار دائري من أعلى
    ox, oy = pw, ph
    cx, cy = ox + 140, oy + 100
    b += f'<circle cx="{cx}" cy="{cy}" r="62" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 5"/>'
    b += DOT(cx + 62, cy, 8, INK, '#fff') + ARROW(cx + 62, cy, cx + 62, cy - 38, MUTED, 2, 9)
    b += DOT(cx, cy, 3, MUTED)
    save(name, svg(2 * pw, 2 * ph, b))


paths_panel('c2l1-o01-paths.svg')


def ball_arc(name):
    w, h = 560, 260; b = ''
    b += L(20, 220, 540, 220, INK, 2)
    # منزل وسياج
    b += RECT(300, 150, 60, 70, MUTED, '#f1e2c6', 1.2) + T(330, 245, 'سياج', 13, color=MUTED)
    pts = [(60 + t * 44, 212 - (t * (10 - t)) * 7.2) for t in range(0, 11)]
    b += '<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 5"/>'
    for t in range(0, 11, 2): b += DOT(*pts[t], 8, INK, '#fff')
    b += runner(40, 220, INK, 0)
    save(name, svg(w, h, b))


ball_arc('c2l1-o01-ball.svg')

# ================= O02 المكان والزمان =================
def road_positions(name, times=None):
    w, h = 600, 200; b = ''
    b += RECT(20, 110, 560, 46, MUTED, ROAD, 1) + L(26, 133, 574, 133, '#fff', 2, '14 10')
    r, P = ruler(50, 550, 162, 0, 100, 10, 1, 'm')
    b += r
    b += car(P(20) - 35, 150, 0.4) + car(P(60) - 35, 150, 1.0)
    b += L(P(20), 150, P(20), 162, INK, 1.2, '3 3') + L(P(60), 150, P(60), 162, INK, 1.2, '3 3')
    if times:
        b += T(P(20), 92, times[0], 15, color=INK) + T(P(60), 92, times[1], 15, color=INK)
    else:
        b += T(P(20), 92, 'الموقع الأول', 14, color=MUTED) + T(P(60), 92, 'الموقع الثاني', 14, color=MUTED)
    save(name, svg(w, h, b))


road_positions('c2l1-o02-positions.svg')
road_positions('c2l1-o02-times.svg', ('t = 0.0 s', 't = 4.0 s'))


def two_snapshots(name):
    """لقطتان لمشهد واحد بلا أزمنة: شجرة ثابتة وعدّاء في موقعين."""
    pw, ph = 280, 190; b = ''
    for i, (rx, lab) in enumerate(((90, 'اللقطة (1)'), (190, 'اللقطة (2)'))):
        ox = i * (pw + 20)
        b += f'<rect x="{ox + 3}" y="3" width="{pw}" height="{ph - 6}" fill="#f7fbff" stroke="{MUTED}" stroke-width="1.5"/>'
        b += L(ox + 3, 150, ox + pw + 3, 150, TREE, 3) + tree(ox + 150, 150) + runner(ox + rx, 150, INK, i)
        b += T(ox + pw / 2, 176, lab, 14, color=MUTED, weight='bold')
    save(name, svg(2 * pw + 26, ph, b))


two_snapshots('c2l1-o02-snapshots.svg')

# ================= O03 المقصود بالمخطط التوضيحي =================
def car_diagram(name, xs, light=True, w=600, h=170, times=None, opac=True):
    b = RECT(10, 120, w - 20, 34, MUTED, ROAD, 1) + L(14, 137, w - 14, 137, '#fff', 2, '14 10')
    if light:
        b += RECT(w - 46, 40, 14, 80, INK, '#444', 1) + DOT(w - 39, 52, 5, '#c0392b', '#e74c3c') + DOT(w - 39, 70, 5, '#777', '#999') + DOT(w - 39, 88, 5, '#777', '#999')
    n = len(xs)
    for k, x in enumerate(xs):
        op = (0.3 + 0.7 * k / (n - 1)) if opac else 1
        b += car(x, 150, op)
        if times: b += T(x + 35, 105, times[k], 13, color=MUTED)
    return b


save('c2l1-o03-cars.svg', svg(600, 170, car_diagram('', [30, 150, 270, 390], light=False) + tree(520, 120)))


def four_reps(name):
    """أربع صور مرقمة: (1) صورة واحدة بخلفية ضبابية، (2) منحنى بياني، (3) صور سيارة متتابعة في صورة واحدة، (4) خريطة طريق."""
    pw, ph = 290, 180; b = ''
    for i in range(4):
        ox, oy = (i % 2) * pw, (i // 2) * ph
        b += f'<rect x="{ox + 3}" y="{oy + 3}" width="{pw - 6}" height="{ph - 6}" fill="none" stroke="{GRID}" stroke-width="1.5"/>'
        b += T(ox + pw - 22, oy + 24, f'({i + 1})', 15, weight='bold')
    # (1) صورة واحدة بخلفية مموهة
    ox, oy = 0, 0
    for k in range(9): b += RECT(ox + 20 + k * 28, oy + 40, 18, 90, '#bcd', '#d6e2ee', 0)
    b += car(ox + 110, oy + 150)
    # (2) منحنى
    ox, oy = pw, 0
    b += ARROW(ox + 40, oy + 150, ox + 260, oy + 150, INK, 1.6, 8) + ARROW(ox + 40, oy + 150, ox + 40, oy + 35, INK, 1.6, 8)
    b += L(ox + 40, oy + 150, ox + 240, oy + 60, BLUE, 3)
    b += T(ox + 150, oy + 170, 'الزمن (s)', 12) + T(ox + 22, oy + 95, 'الموقع (m)', 12, rotate=-90)
    # (3) صور متتابعة في صورة واحدة
    ox, oy = 0, ph
    b += RECT(ox + 12, oy + 120, pw - 24, 30, MUTED, ROAD, 1)
    b += tree(ox + 150, oy + 120)
    for k, x in enumerate((18, 78, 138, 198)): b += car(ox + x, oy + 146, 0.3 + 0.7 * k / 3, sc=0.75)
    # (4) خريطة
    ox, oy = pw, ph
    b += RECT(ox + 20, oy + 35, pw - 40, 125, MUTED, '#f4f1e8', 1)
    b += f'<path d="M {ox + 40} {oy + 140} C {ox + 90} {oy + 60}, {ox + 160} {oy + 160}, {ox + 250} {oy + 60}" fill="none" stroke="{ORANGE}" stroke-width="5"/>'
    b += DOT(ox + 40, oy + 140, 6, INK, '#fff') + DOT(ox + 250, oy + 60, 6, INK, INK)
    save(name, svg(2 * pw, 2 * ph, b))


four_reps('c2l1-o03-reps.svg')

# ================= O04 نموذج الجسيم النقطي =================
def cars_with_dots(name, xs):
    b = car_diagram('', xs, light=False, h=210)
    for x in xs: b += DOT(x + 35, 190, 6, INK)
    save(name, svg(600, 210, b))


cars_with_dots('c2l1-o04-cardots.svg', [30, 120, 230, 360])


def runner_points(name):
    w, h = 360, 250; b = L(40, 220, 320, 220, TREE, 3)
    x, y = 180, 220
    # عدّاء كبير
    s = 2.6
    def LL(a, c, d, e): return L(x + a * s, y + c * s, x + d * s, y + e * s, INK, 4)
    b += f'<circle cx="{x + 3 * s}" cy="{y - 62 * s}" r="{8 * s}" fill="none" stroke="{INK}" stroke-width="3.5"/>'
    b += LL(2, -54, 0, -30) + LL(1, -46, 12, -38) + LL(12, -38, 16, -46) + LL(1, -46, -10, -40)
    b += LL(0, -30, 12, -16) + LL(12, -16, 10, 0) + LL(0, -30, -8, -15) + LL(-8, -15, -16, -4)
    pts = {'A': (x + 3 * s, y - 62 * s), 'B': (x + 1 * s, y - 40 * s), 'C': (x + 16 * s, y - 46 * s), 'D': (x + 10 * s, y)}
    off = {'A': (-30, 6), 'B': (-30, 6), 'C': (24, 6), 'D': (24, 2)}
    for k, (px_, py_) in pts.items():
        b += DOT(px_, py_, 6, RED) + T(px_ + off[k][0], py_ + off[k][1], k, 17, weight='bold', color=RED)
    save(name, svg(w, h, b))


runner_points('c2l1-o04-points.svg')

# ================= O05 رسم نموذج الجسيم النقطي =================
eq = px([0, 1, 2, 3, 4, 5], 0, 5, 50, 500)
inc = px([0, 0.4, 1.2, 2.4, 4.0, 6.0], 0, 6, 50, 500)
dec = px([0, 2.0, 3.6, 4.8, 5.6, 6.0], 0, 6, 50, 500)
one = [300]
R = lambda i, xs: {'title': f'({i})', 'xs': xs}
# صفوف لسيارة تقترب من إشارة وتتوقف (يمينًا)
dot_rows('c2l1-o05-rows-stop.svg', [R(1, inc), R(2, eq), R(3, one), R(4, dec)], w=600)
# صفوف لدراج بسرعة ثابتة
dot_rows('c2l1-o05-rows-bike.svg', [R(1, dec), R(2, inc), R(3, eq), R(4, one)], w=600)
# سيارة تبدأ ببطء ثم تتسارع (الصف الصحيح: تزايد)، مع بديل تناقص وبديل متساوٍ وبديل تزايد ثم تناقص
mix = px([0, 0.4, 1.2, 2.4, 3.4, 3.8], 0, 6, 50, 500)
dot_rows('c2l1-o05-rows-speedup.svg', [R(1, eq), R(2, dec), R(3, mix), R(4, inc)], w=600)

# نموذج من جدول بيانات (cm) بمقياس مدرج
data_inc = [0, 2, 6, 12, 20, 30]
cand = [data_inc, [0, 10, 18, 24, 28, 30], [0, 6, 12, 18, 24, 30], [0, 2, 6, 12, 20, 22]]
order = [1, 3, 0, 2]  # الصف (3) هو الصحيح
dot_rows('c2l1-o05-table.svg', [R(i + 1, px(cand[order[i]], 0, 30, 50, 550)) for i in range(4)], w=600, scale=(0, 30, 5, 'الموقع (cm)'))

# ================= O06 وصف الحالة من تباعد النقاط =================
plane = px([0, 0.3, 0.9, 1.8, 3.0, 4.5, 6.3], 0, 6.3, 50, 550)
dot_rows('c2l1-o06-plane.svg', [{'xs': plane, 'arrow': '→'}], w=600, top=46)
# حركة نحو اليسار مع متجهات السرعة: التباعد يتناقص في اتجاه الحركة
left = px([6.0, 4.0, 2.4, 1.2, 0.4, 0.0], 0, 6, 70, 540)
dot_rows('c2l1-o06-left.svg', [{'xs': left, 'arrow': '←'}], w=600, top=46)
# متجهات سرعة يمينًا متزايدة (للمقالي)
right_vel = px([0, 0.5, 1.4, 2.7, 4.4, 6.5], 0, 6.5, 50, 520)
dot_rows('c2l1-o06-right-vel.svg', [{'xs': right_vel, 'vel': True}], w=600, top=36)
# جسمان A وB
dot_rows('c2l1-o06-two.svg', [{'title': 'الجسم A', 'xs': px([0, 1, 2, 3, 4, 5], 0, 10, 50, 550), 'color': BLUE},
                              {'title': 'الجسم B', 'xs': px([0, 2, 4, 6, 8, 10], 0, 10, 50, 550), 'color': RED}], w=600, row_h=70)
# تزايد ثم ثبات ثم تناقص
mixed = px([0, 0.5, 1.5, 3, 4.5, 6, 7.5, 8.5, 9.0], 0, 9, 40, 560)
dot_rows('c2l1-o06-mixed.svg', [{'xs': mixed, 'arrow': '→'}], w=600, top=46)


def tire_marks(name):
    w, h = 600, 170; b = RECT(10, 50, 580, 80, MUTED, '#d5d5d5', 1)
    xs = px([0, 2.0, 3.6, 4.8, 5.6, 6.0], 0, 6, 60, 520)
    for x in xs: b += RECT(x - 6, 66, 12, 14, INK, '#333', 0) + RECT(x - 6, 102, 12, 14, INK, '#333', 0)
    b += ARROW(60, 30, 140, 30, INK, 2) + T(150, 35, 'اتجاه حركة السيارة', 13, 'start', MUTED)
    b += T(300, 155, 'آثار العجلات على الطريق (منظر من أعلى)', 13, color=MUTED)
    save(name, svg(w, h, b))


tire_marks('c2l1-o06-tire.svg')
# للمقالي: نقاط بمقياس متري (cm) — فترة 0.1 s
ess = [0, 4, 8, 12, 15, 17, 18]
dot_rows('c2l1-o06-essay.svg', [{'xs': px(ess, 0, 20, 50, 550), 'arrow': '→'}], w=600, top=46, scale=(0, 20, 2, 'الموقع (cm)'))

# ================= O07 إنشاء المخطط التوضيحي من صور متتابعة =================
def frames(name, positions, times, vmax=100, step=10, w=600):
    """إطارات (صور) متتابعة كل منها صف: سيارة فوق مسطرة، مع زمن اللقطة."""
    fh = 92; b = ''
    for i, (p, t) in enumerate(zip(positions, times)):
        oy = i * fh
        b += f'<rect x="4" y="{oy + 4}" width="{w - 8}" height="{fh - 8}" fill="#fcfcfc" stroke="{MUTED}" stroke-width="1.3"/>'
        r, P = ruler(110, w - 50, oy + 52, 0, vmax, step, 1, 'cm')
        b += r + car(P(p) - 35, oy + 50, 1.0)
        b += L(P(p), oy + 46, P(p), oy + 58, RED, 2)
        b += T(56, oy + 30, f'اللقطة {i + 1}', 13, color=INK, weight='bold') + T(56, oy + 54, t, 13, color=MUTED)
    save(name, svg(w, fh * len(positions) + 4, b))


frames('c2l1-o07-frames.svg', [10, 30, 50, 70], ['t = 0.0 s', 't = 0.1 s', 't = 0.2 s', 't = 0.3 s'])
frames('c2l1-o07-unequal.svg', [10, 25, 55, 70], ['t = 0.0 s', 't = 0.1 s', 't = 0.3 s', 't = 0.4 s'])


def runner_frames(name):
    """أربع صور متتابعة لعدّاء أمام شجرة ثابتة (كل صورة إطار منفصل)."""
    pw, ph = 145, 150; b = ''
    xs = [30, 55, 80, 105]
    for i, rx in enumerate(xs):
        ox = i * (pw + 4)
        b += f'<rect x="{ox + 2}" y="2" width="{pw}" height="{ph - 26}" fill="#f7fbff" stroke="{MUTED}" stroke-width="1.3"/>'
        b += L(ox + 2, 112, ox + pw + 2, 112, TREE, 3) + tree(ox + 75, 112) + runner(ox + rx, 112, INK, i)
        b += T(ox + pw / 2 + 2, ph - 6, f'الصورة {i + 1}', 13, color=MUTED, weight='bold')
    save(name, svg(4 * (pw + 4), ph, b))


runner_frames('c2l1-o07-runner-frames.svg')


def combined_candidates(name):
    """أربعة مخططات مرشحة (1)–(4) لصور سيارة مجمعة في صورة واحدة، مع مسطرة cm."""
    rh = 96; w = 600; b = ''
    sets = {1: [10, 30, 50, 70], 2: [10, 20, 40, 70], 3: [10, 40, 60, 70], 4: [10, 25, 40, 55]}
    order = [2, 4, 1, 3]
    for i, k in enumerate(order):
        oy = i * rh
        b += f'<rect x="4" y="{oy + 4}" width="{w - 8}" height="{rh - 8}" fill="#fff" stroke="{GRID}" stroke-width="1.3"/>'
        b += T(40, oy + 52, f'({i + 1})', 15, weight='bold')
        r, P = ruler(90, w - 50, oy + 56, 0, 80, 10, 1, 'cm')
        b += r
        for j, p in enumerate(sets[k]): b += car(P(p) - 24.5, oy + 54, 0.35 + 0.65 * j / 3, sc=0.7) + L(P(p), oy + 50, P(p), oy + 62, RED, 2)
    save(name, svg(w, rh * 4 + 4, b))


combined_candidates('c2l1-o07-candidates.svg')

# ================= O08 شرط استخدام النموذج =================
def two_scenes(name):
    pw, ph = 290, 180; b = ''
    for i in range(2):
        ox = i * pw
        b += f'<rect x="{ox + 3}" y="3" width="{pw - 6}" height="{ph - 6}" fill="none" stroke="{GRID}" stroke-width="1.5"/>'
        b += T(ox + pw - 22, 26, f'({i + 1})', 15, weight='bold')
    # (1) سيارة تدخل مرآبًا طوله 6 m
    b += RECT(130, 60, 140, 80, MUTED, '#efe7d6', 1.5) + L(130, 60, 130, 140, '#fff', 3)
    b += car(150, 136) + L(20, 136, 280, 136, INK, 1.5)
    b += ARROW(130, 160, 270, 160, MUTED, 1.5, 8) + ARROW(270, 160, 130, 160, MUTED, 1.5, 8) + T(200, 155, '6 m', 13, color=INK)
    b += T(65, 125, 'مرآب', 13, color=MUTED)
    # (2) سيارة على طريق بين مدينتين 400 km
    ox = pw
    b += DOT(ox + 40, 110, 9, INK, '#fff') + DOT(ox + 250, 110, 9, INK, '#fff')
    b += L(ox + 49, 110, ox + 241, 110, ORANGE, 4)
    b += T(ox + 145, 90, '400 km', 14, color=INK)
    b += T(ox + 40, 138, 'مدينة', 12, color=MUTED) + T(ox + 250, 138, 'مدينة', 12, color=MUTED)
    save(name, svg(2 * pw, ph, b))


two_scenes('c2l1-o08-scenes.svg')
