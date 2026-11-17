import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 2-2 (الموقع والزمن) — الأهداف O01–O10: النظام الإحداثي، الموقع على خط الأعداد، المتجهات بمقياس رسم، جمع الإزاحات بيانيًا
# متجهات الموقع والإزاحة بالأخضر كما في الكتاب، والمحصلة خط أخضر متقطع.


def icon(kind, x, y):
    """رمز مَعلم صغير قاعدته عند (x, y)."""
    if kind == 'tree':
        return (f'<rect x="{x - 3:.1f}" y="{y - 14:.1f}" width="6" height="14" fill="#8a5a2b"/>'
                f'<polygon points="{x:.1f},{y - 58:.1f} {x - 17:.1f},{y - 12:.1f} {x + 17:.1f},{y - 12:.1f}" fill="#3f8f4f"/>')
    if kind == 'house':
        return (f'<rect x="{x - 18:.1f}" y="{y - 30:.1f}" width="36" height="30" fill="#e9d9c4" stroke="{INK}" stroke-width="1.5"/>'
                f'<polygon points="{x - 23:.1f},{y - 30:.1f} {x:.1f},{y - 50:.1f} {x + 23:.1f},{y - 30:.1f}" fill="#b5523b" stroke="{INK}" stroke-width="1.5"/>'
                f'<rect x="{x - 5:.1f}" y="{y - 16:.1f}" width="10" height="16" fill="#7a5230"/>')
    if kind == 'pole':
        return L(x, y, x, y - 58, '#555', 3) + L(x, y - 58, x + 12, y - 58, '#555', 3) + DOT(x + 13, y - 55, 4, '#c9a400', '#f5d000')
    if kind == 'shop':
        return (f'<rect x="{x - 22:.1f}" y="{y - 32:.1f}" width="44" height="32" fill="#f6e7b0" stroke="{INK}" stroke-width="1.5"/>'
                f'<rect x="{x - 24:.1f}" y="{y - 40:.1f}" width="48" height="9" fill="#d0613c" stroke="{INK}" stroke-width="1.2"/>'
                f'<rect x="{x - 14:.1f}" y="{y - 22:.1f}" width="12" height="22" fill="#8fb3d9"/>')
    if kind == 'school':
        return (f'<rect x="{x - 26:.1f}" y="{y - 34:.1f}" width="52" height="34" fill="#dfe7f2" stroke="{INK}" stroke-width="1.5"/>'
                + ''.join(f'<rect x="{x - 20 + 14 * k:.1f}" y="{y - 27:.1f}" width="9" height="9" fill="#8fb3d9"/>' for k in range(3))
                + L(x, y - 34, x, y - 52, INK, 1.5) + f'<polygon points="{x:.1f},{y - 52:.1f} {x + 13:.1f},{y - 48:.1f} {x:.1f},{y - 44:.1f}" fill="#2e8b57"/>')
    if kind == 'mosque':
        return (f'<rect x="{x - 20:.1f}" y="{y - 26:.1f}" width="40" height="26" fill="#efe9dc" stroke="{INK}" stroke-width="1.5"/>'
                f'<path d="M {x - 12:.1f} {y - 26:.1f} A 12 12 0 0 1 {x + 12:.1f} {y - 26:.1f} Z" fill="#c9b27a" stroke="{INK}" stroke-width="1.2"/>'
                f'<rect x="{x + 22:.1f}" y="{y - 50:.1f}" width="6" height="50" fill="#efe9dc" stroke="{INK}" stroke-width="1.2"/>')
    return ''


def numline(name, vmin, vmax, step, w=640, reverse=False, landmarks=(), dots=(), arrows=(), axis_letter='d',
            unit_label='الموقع (m)', note=None, top=None, h=None, label_every=1, extra=''):
    """خط أعداد للموقع. landmarks = [(v, kind, text)]؛ dots = [(v, text, color)] فوق المحور؛
    arrows = [dict(frm, to, label?, sym?(رمز متجه بخط عريض مائل), color?, dash?, row (0 = أقرب صف للمحور), lab_dy?)]"""
    x0, x1 = 48, w - 48
    P = (lambda v: x1 - (v - vmin) / (vmax - vmin) * (x1 - x0)) if reverse else (lambda v: x0 + (v - vmin) / (vmax - vmin) * (x1 - x0))
    nrows = max([a.get('row', 0) for a in arrows] + [-1]) + 1
    top = top if top is not None else (20 if not note else 40)
    land_h = 70 if landmarks else 0
    ya = top + land_h + 34 + nrows * 34 + (14 if dots else 0)
    H = h or ya + 58
    b = ''
    if note: b += T(w / 2, 22, note, 14, color=MUTED)
    for v, kind, text in landmarks:
        b += icon(kind, P(v), ya - 6) + T(P(v), ya - 6 - (66 if kind in ('tree', 'pole') else 58), text, 13, color=INK, weight='bold')
    # المحور
    if reverse: b += ARROW(x1 + 18, ya, x0 - 24, ya, INK, 2) + T(x0 - 30, ya + 5, axis_letter, 17, 'end', INK, italic=True)
    else: b += ARROW(x0 - 18, ya, x1 + 24, ya, INK, 2) + T(x1 + 30, ya + 5, axis_letter, 17, 'start', INK, italic=True)
    n = round((vmax - vmin) / step)
    for i in range(n + 1):
        v = vmin + i * step
        b += L(P(v), ya - 6, P(v), ya + 6, INK, 1.5)
        if i % label_every == 0: b += T(P(v), ya + 23, fmt(round(v, 6)), 14, color=MUTED)
    b += T(w / 2, ya + 47, unit_label, 14)
    for v, text, c in dots:
        b += DOT(P(v), ya - 14, 6, c)
        if text: b += T(P(v) + 11, ya - 9, text, 14, 'start', c, 'bold')
    for a in arrows:
        r = a.get('row', 0); y = ya - (24 if dots else 14) - 34 * r - (8 if dots else 0)
        c = a.get('color', C_DISP)
        if a.get('dash'): b += L(P(a['frm']), y, P(a['to']), y, c, 3, '8 6') + ARROW(P(a['to']) - (1 if P(a['to']) > P(a['frm']) else -1) * 2, y, P(a['to']), y, c, 3, 12)
        else: b += ARROW(P(a['frm']), y, P(a['to']), y, c, 3, 12)
        b += L(P(a['frm']), y - 5, P(a['frm']), y + 5, c, 2)
        mx = (P(a['frm']) + P(a['to'])) / 2
        if a.get('sym'): b += V(mx, y - 9, a['sym'], c, 16)
        if a.get('label'): b += T(a.get('lx', mx), y - 9 + a.get('lab_dy', 0), a['label'], 14, color=c, weight='bold')
    save(name, svg(w, H, b + extra))
    return P, ya


def grid_panel(ox, oy, cols, rows, unit, vecs, title=None, gl=GRID):
    """شبكة مربعات صغيرة داخل لوحة؛ vecs = [dict(frm:(c,r), to:(c,r), sym?, color?, dash?, lpos?)] بإحداثيات الشبكة (r لأعلى)."""
    gx, gy = ox + 20, oy + (34 if title else 14)
    Pp = lambda p: (gx + p[0] * unit, gy + (rows - p[1]) * unit)
    b = ''
    for i in range(cols + 1): b += L(gx + i * unit, gy, gx + i * unit, gy + rows * unit, gl, 1)
    for j in range(rows + 1): b += L(gx, gy + j * unit, gx + cols * unit, gy + j * unit, gl, 1)
    for v in vecs:
        (xa, ya), (xb, yb) = Pp(v['frm']), Pp(v['to']); c = v.get('color', C_DISP)
        if v.get('dash'):
            ang = math.atan2(yb - ya, xb - xa)
            b += L(xa, ya, xb - 10 * math.cos(ang), yb - 10 * math.sin(ang), c, 2.6, '7 5') + ARROW(xb - 12 * math.cos(ang), yb - 12 * math.sin(ang), xb, yb, c, 2.6, 11)
        else: b += ARROW(xa, ya, xb, yb, c, 3, 12)
        dx, dy = v.get('lpos', (0, -9))
        if v.get('sym'): b += V((xa + xb) / 2 + dx, (ya + yb) / 2 + dy, v['sym'], c, 16)
        if v.get('label'): b += T((xa + xb) / 2 + dx, (ya + yb) / 2 + dy, v['label'], 14, color=c, weight='bold')
    if title: b += T(ox + 20 + cols * unit / 2, oy + 22, title, 14, weight='bold')
    return b


def compass(x, y):
    """سهما الاتجاهين: الشرق يمينًا والشمال لأعلى."""
    return (ARROW(x, y, x + 34, y, MUTED, 1.8, 9) + ARROW(x, y, x, y - 34, MUTED, 1.8, 9)
            + T(x + 40, y + 5, 'شرق', 12, 'start', MUTED) + T(x, y - 42, 'شمال', 12, color=MUTED))


# ================= O01 النظام الإحداثي =================
# نظامان للطريق نفسه: (1) نقطة الأصل عند المنزل والقيم تتزايد يمينًا؛ (2) نقطة الأصل عند عمود الإنارة والقيم تتزايد يسارًا.
def two_systems():
    w = 640; x0, x1 = 60, w - 60
    # المنزل عند 0 والعمود عند 30 في النظام (1)
    P1 = lambda v: x0 + v / 30 * (x1 - x0)
    b = icon('house', P1(0), 100) + T(P1(0), 40, 'المنزل', 13, weight='bold') + icon('tree', P1(12), 100) + T(P1(12), 34, 'الشجرة', 13, weight='bold')
    b += icon('pole', P1(30), 100) + T(P1(30), 34, 'عمود الإنارة', 13, weight='bold')
    b += L(20, 100, w - 20, 100, '#9aa3ad', 6)
    for k, (ya, rev, lab) in enumerate([(160, False, 'النظام (1)'), (250, True, 'النظام (2)')]):
        P = (lambda v: x0 + v / 30 * (x1 - x0)) if not rev else (lambda v: x1 - v / 30 * (x1 - x0))
        b += T(w / 2, ya - 26, lab, 14, weight='bold', color=MUTED)
        if rev: b += ARROW(x1 + 16, ya, x0 - 26, ya, INK, 2) + T(x0 - 32, ya + 5, 'd', 17, 'end', italic=True)
        else: b += ARROW(x0 - 16, ya, x1 + 26, ya, INK, 2) + T(x1 + 32, ya + 5, 'd', 17, 'start', italic=True)
        for v in range(0, 31, 5): b += L(P(v), ya - 6, P(v), ya + 6, INK, 1.5) + T(P(v), ya + 23, fmt(v), 14, color=MUTED)
    b += T(w / 2, 300, 'الموقع (m)', 14)
    save('c2l2-o01-two-systems.svg', svg(w, 316, b))
two_systems()

# محور قيمه تتزايد نحو اليسار، ونقطة الأصل عند الشجرة (يمين الرسم)
numline('c2l2-o01-axis.svg', 0, 40, 5, reverse=True, landmarks=[(0, 'tree', 'الشجرة'), (25, 'house', 'المنزل')])

# ================= O02 نقطة الأصل =================
numline('c2l2-o02-origin.svg', -20, 60, 10, landmarks=[(-20, 'house', 'المنزل'), (0, 'mosque', 'المسجد'), (30, 'shop', 'البقالة'), (60, 'school', 'المدرسة')], w=660)

# ================= O03 الموقع =================
numline('c2l2-o03-negative.svg', -10, 30, 5, landmarks=[(4, 'tree', 'الشجرة')], dots=[(-5, 'الكرة', RED)])
numline('c2l2-o03-arrows.svg', 0, 30, 5, dots=[(20, 'العدّاء', RED)], arrows=[
    dict(frm=20, to=0, label='(1)', row=0), dict(frm=10, to=20, label='(2)', row=1),
    dict(frm=0, to=20, label='(3)', row=2), dict(frm=0, to=30, label='(4)', row=3)], w=620)
numline('c2l2-o03-essay.svg', -15, 25, 5, dots=[(-10, 'B', RED), (15, 'A', BLUE)], landmarks=[(0, 'pole', 'عمود الإنارة')])

# ================= O06 تمثيل المتجهات بالرسم =================
def scale_arrow():
    cols, rows, u = 10, 3, 40
    b = grid_panel(0, 0, cols, rows, u, [dict(frm=(2, 1.5), to=(8, 1.5))])
    b += compass(470, 120)
    save('c2l2-o06-scale.svg', svg(560, 150, b))
scale_arrow()

def choose_arrow():
    cols, rows, u = 9, 9, 36
    vecs = [dict(frm=(1, 8), to=(4, 8), label='(1)', lpos=(0, -10)), dict(frm=(7, 6), to=(1, 6), label='(2)', lpos=(0, -10)),
            dict(frm=(5, 4), to=(2, 4), label='(3)', lpos=(0, -10)), dict(frm=(6, 2), to=(1, 2), label='(4)', lpos=(0, -10))]
    b = grid_panel(0, 0, cols, rows, u, vecs) + compass(380, 300)
    save('c2l2-o06-choose.svg', svg(470, 360, b))
choose_arrow()

def compare_ab():
    cols, rows, u = 10, 4, 36
    vecs = [dict(frm=(1, 3), to=(7, 3), sym='A'), dict(frm=(5, 1), to=(2, 1), sym='B')]
    save('c2l2-o06-compare.svg', svg(420, 180, grid_panel(0, 0, cols, rows, u, vecs)))
compare_ab()

# ================= O07 الإزاحة =================
numline('c2l2-o07-disp.svg', 0, 30, 5, dots=[(5, '1', INK), (25, '2', INK)], arrows=[
    dict(frm=25, to=5, label='(1)', row=0), dict(frm=0, to=25, label='(2)', row=1),
    dict(frm=5, to=25, label='(3)', row=2), dict(frm=0, to=5, label='(4)', row=3)], w=620)

# ================= O09 جمع إزاحتين بيانيًا =================
def arrange():
    # المتجهان A (4 مربعات شرقًا) وB (2 مربع شرقًا) ثم أربعة ترتيبات
    u = 30; pw, ph = 300, 120
    b = grid_panel(0, 0, 9, 2, u, [dict(frm=(0.5, 1), to=(4.5, 1), sym='A'), dict(frm=(6, 1), to=(8, 1), sym='B')], title='المتجهان')
    lay = [
        [dict(frm=(0.5, 0.6), to=(4.5, 0.6), sym='A', lpos=(0, 22)), dict(frm=(0.5, 1.4), to=(2.5, 1.4), sym='B', lpos=(0, -8))],   # (1) الذيلان معًا
        [dict(frm=(0.5, 1), to=(4.5, 1), sym='A'), dict(frm=(6.5, 1), to=(4.5, 1), sym='B')],                      # (2) الرأسان متلامسان
        [dict(frm=(0.5, 1), to=(4.5, 1), sym='A'), dict(frm=(4.5, 1), to=(6.5, 1), sym='B')],                      # (3) رأس A عند ذيل B (صحيح)
        [dict(frm=(0.5, 1), to=(4.5, 1), sym='A'), dict(frm=(4.5, 1), to=(8.5, 1), sym='B')],                      # (4) طول B تغيّر
    ]
    titles = ['(1)', '(2)', '(3)', '(4)']
    for i, vs in enumerate(lay):
        ox, oy = (i % 2) * pw, 110 + (i // 2) * ph
        b += grid_panel(ox, oy, 9, 2, u, vs, title=titles[i])
    save('c2l2-o09-arrange.svg', svg(2 * pw, 110 + 2 * ph, b))
arrange()

def east_west():
    u = 34
    vecs = [dict(frm=(1, 3), to=(6, 3), sym='A'), dict(frm=(9, 1), to=(6, 1), sym='B')]
    b = grid_panel(0, 0, 11, 4, u, vecs) + compass(430, 120)
    save('c2l2-o09-ew.svg', svg(520, 170, b))
east_west()

def essay_grid():
    u = 34
    vecs = [dict(frm=(1, 2), to=(4, 2), sym='A'), dict(frm=(6, 2), to=(11, 2), sym='B')]
    b = grid_panel(0, 0, 12, 3, u, vecs) + compass(470, 125)
    save('c2l2-o09-essay.svg', svg(560, 150, b))
essay_grid()

def maze():
    # مسار المتاهة بمقياس: كل مربع = 0.1 m. البداية (1,1): 1.0 m شمالًا، 0.3 m شرقًا، 0.8 m جنوبًا، 0.4 m شرقًا
    u = 30; cols, rows = 11, 12
    pts = [(1, 1), (1, 11), (4, 11), (4, 3), (8, 3)]
    vecs = [dict(frm=pts[k], to=pts[k + 1]) for k in range(4)]
    b = grid_panel(0, 0, cols, rows, u, vecs)
    gx, gy = 20, 14
    Pp = lambda p: (gx + p[0] * u, gy + (rows - p[1]) * u)
    sx, sy = Pp(pts[0]); ex, ey = Pp(pts[-1])
    b += DOT(sx, sy, 5, INK) + T(sx - 4, sy + 22, 'البداية', 13, weight='bold') + DOT(ex, ey, 5, INK) + T(ex, ey + 22, 'النهاية', 13, weight='bold')
    b += compass(390, 330)
    save('c2l2-o09-maze.svg', svg(470, 400, b))
maze()

# ================= O10 المحصلة =================
def which_resultant():
    u = 40; cols, rows = 8, 6
    vecs = [dict(frm=(1, 1), to=(5, 1), sym='A', lpos=(0, 20)), dict(frm=(5, 1), to=(5, 4), sym='B', lpos=(14, 0)),
            dict(frm=(1, 4), to=(5, 1), dash=True, color=MUTED),
            dict(frm=(1, 1), to=(5, 4), dash=True, color=MUTED),
            dict(frm=(1, 4), to=(5, 4), dash=True, label='(3)', lpos=(0, -9), color=MUTED),
            dict(frm=(1, 1), to=(1, 4), dash=True, label='(4)', lpos=(-16, 0), color=MUTED)]
    tag = lambda x, y, t: f'<rect x="{x - 15}" y="{y - 13}" width="30" height="19" fill="#fff"/>' + T(x, y + 1, t, 14, color=MUTED, weight='bold')
    save('c2l2-o10-which.svg', svg(380, 280, grid_panel(0, 0, cols, rows, u, vecs) + tag(108, 130, '(1)') + tag(108, 182, '(2)')))
which_resultant()
