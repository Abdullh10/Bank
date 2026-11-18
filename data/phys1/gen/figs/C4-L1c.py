import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-1 (القوة والحركة) — الأهداف O27–O37: الدفع، الجاذبية الأرضية، مخطط الجسم الحر، التصنيف، العلاقة العكسية، مختبر القوة والكتلة
import math

AL = 'التسارع (m/s^2)'; FL = 'القوة (N)'
GRAY = '#9aa3b0'; SKIN = '#e8c9a6'; WOOD = '#b98a5a'


def FA(x, y, sub, color=C_FORCE, size=17, anchor='middle'):
    """رمز قوة بخط عريض مائل مع حرف سفلي عربي كما في الكتاب (مثل F_المحصلة، F_الهواء)."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" direction="ltr" font-size="{size}" fill="{color}">'
            f'<tspan font-weight="bold" font-style="italic" {MATHFONT}>F</tspan>'
            f'<tspan dy="0.32em" font-size="{int(size * 0.62)}" {FONT}>{esc(sub)}</tspan></text>')


def LBL(x, y, lab, color=C_FORCE, size=17):
    if lab is None or lab == '': return ''
    if isinstance(lab, tuple): return FA(x, y, lab[1], color, size)
    if lab.isdigit(): return T(x, y, lab, 16, 'middle', INK, 'bold')
    return V(x, y, lab, color, size)


def forces_at(cx, cy, forces, dot=True):
    """أسهم قوى تبدأ من الجسم (نقطة) وتتجه بعيدًا عنه. force: (زاوية بالدرجات، طول px، تسمية، خيارات)
    خيار toward=True يرسم السهم متجهًا نحو الجسم (خطأ شائع)."""
    b = DOT(cx, cy, 6, INK) if dot else ''
    for f in forces:
        ang, ln, lab = f[0], f[1], f[2]
        o = f[3] if len(f) > 3 else {}
        a = math.radians(ang); c = o.get('color', C_FORCE)
        ux, uy = math.cos(a), -math.sin(a)
        cx0, cy0 = cx, cy; cx = cx + o.get('ox', 0); cy = cy + o.get('oy', 0)
        if o.get('toward'):
            b += ARROW(cx + (ln + 8) * ux, cy + (ln + 8) * uy, cx + 8 * ux, cy + 8 * uy, c, 3)
            tip = ln + 8
        else:
            b += ARROW(cx, cy, cx + ln * ux, cy + ln * uy, c, 3); tip = ln
        d = o.get('ld', 24)
        lx, ly = cx + (tip + d) * ux + o.get('dx', 0), cy + (tip + d) * uy + 6 + o.get('dy', 0)
        b += LBL(lx, ly, lab, c)
        cx, cy = cx0, cy0
    return b


def plus(x, y, axis='y', ln=48):
    if axis == 'y': return ARROW(x, y, x, y - ln, INK, 1.8, 9) + T(x + 6, y - ln + 4, '+y', 14, 'start', italic=True)
    return ARROW(x, y, x + ln, y, INK, 1.8, 9) + T(x + ln + 4, y + 5, '+x', 14, 'start', italic=True)


def frame(x, y, w, h, num=None):
    b = f'<rect x="{x + 3}" y="{y + 3}" width="{w - 6}" height="{h - 6}" fill="#fff" stroke="{GRID}" stroke-width="1.5" rx="6"/>'
    if num is not None: b += T(x + w - 16, y + 26, f'({num})', 15, 'end', INK, 'bold')
    return b


def panels(name, items, pw=180, ph=280, cy=None, axis='y', extras=None):
    """صف من مخططات الجسم الحر المرقّمة: items = [forces,...]؛ extras = {رقم اللوحة: دالة(cx, cy) تعيد svg إضافيًا}"""
    b = ''; cy = cy or ph / 2 + 6
    for k, fs in enumerate(items):
        x0 = k * pw; cx = x0 + pw / 2 + 8
        b += frame(x0, 0, pw, ph, k + 1)
        b += forces_at(cx, cy, fs)
        if extras and (k + 1) in extras: b += extras[k + 1](cx, cy)
        b += plus(x0 + 22, ph - 30, 'y', 40)
    save(name, svg(pw * len(items), ph, b))


NET = ('F', 'المحصلة'); AIR = ('F', 'الهواء')


def ground(x1, x2, y):
    b = L(x1, y, x2, y, INK, 2)
    for x in range(int(x1) + 6, int(x2), 14): b += L(x, y, x - 8, y + 9, MUTED, 1.2)
    return b


def ceiling(x1, x2, y):
    b = L(x1, y, x2, y, INK, 2)
    for x in range(int(x1) + 6, int(x2), 14): b += L(x, y, x - 8, y - 9, MUTED, 1.2)
    return b


def rocket(cx, top, h=120, w=30, flame=True):
    b = f'<polygon points="{cx},{top} {cx - w / 2},{top + 30} {cx + w / 2},{top + 30}" fill="#c9d3e0" stroke="{INK}" stroke-width="2"/>'
    b += RECT(cx - w / 2, top + 30, w, h - 30, INK, '#e9eef5')
    b += f'<polygon points="{cx - w / 2},{top + h - 30} {cx - w / 2 - 14},{top + h + 4} {cx - w / 2},{top + h}" fill="#c9d3e0" stroke="{INK}" stroke-width="2"/>'
    b += f'<polygon points="{cx + w / 2},{top + h - 30} {cx + w / 2 + 14},{top + h + 4} {cx + w / 2},{top + h}" fill="#c9d3e0" stroke="{INK}" stroke-width="2"/>'
    if flame: b += f'<path d="M {cx - 10} {top + h} Q {cx} {top + h + 50} {cx + 10} {top + h} Z" fill="#f2a541" stroke="#c46a10" stroke-width="1.5"/>'
    return b


def table_book(x, y):
    """طاولة سطحها عند y يبدأ من x، وكتاب عليها. يعيد (svg، مركز الكتاب)."""
    b = RECT(x, y, 170, 12, INK, WOOD) + RECT(x + 12, y + 12, 10, 90, INK, WOOD) + RECT(x + 148, y + 12, 10, 90, INK, WOOD)
    b += RECT(x + 50, y - 22, 80, 22, INK, '#7aa6d6')
    return b, (x + 90, y - 11)


def hand_left(x, y):
    """يد بسيطة تلامس جسمًا من اليسار عند (x, y)."""
    return f'<path d="M {x - 46} {y - 9} L {x - 4} {y - 9} Q {x + 2} {y} {x - 4} {y + 9} L {x - 46} {y + 9} Z" fill="{SKIN}" stroke="{INK}" stroke-width="1.6"/>'


def ball_hand(cx, cy, r=26):
    b = f'<path d="M {cx - 60} {cy + r + 6} Q {cx} {cy + r + 40} {cx + 58} {cy + r - 4} L {cx + 60} {cy + r + 10} Q {cx} {cy + r + 58} {cx - 62} {cy + r + 22} Z" fill="{SKIN}" stroke="{INK}" stroke-width="1.6"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#b8c4e6" stroke="{INK}" stroke-width="2"/>'
    return b


def sys_circle(cx, cy, r):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 5"/>'


def bucket(cx, top, w=56, h=50):
    return f'<polygon points="{cx - w / 2},{top} {cx + w / 2},{top} {cx + w / 2 - 8},{top + h} {cx - w / 2 + 8},{top + h}" fill="#d5dbe3" stroke="{INK}" stroke-width="2"/>' + \
        f'<path d="M {cx - w / 2} {top} Q {cx} {top - 34} {cx + w / 2} {top}" fill="none" stroke="{INK}" stroke-width="1.6"/>'


def motion_row(xs, y, w, start_label=True, start_idx=0, plus_x=True, h=150):
    b = ''
    for k, x in enumerate(xs):
        b += DOT(x, y, 6, INK)
    order = xs if start_idx == 0 else list(reversed(xs))
    for k in range(len(order) - 1):
        x1, x2 = order[k], order[k + 1]
        b += ARROW(x1, y - 18, x1 + 0.85 * (x2 - x1), y - 18, C_VEL, 2.4, 9)
    b += V(order[1] + (12 if order[1] > order[0] else -12), y - 32, 'v', C_VEL, 17)
    if start_label: b += T(order[0], y + 26, 'البداية', 13, color=MUTED)
    if plus_x: b += plus(30, h - 22, 'x', 70)
    return b


# ============ O27 ============
def o27():
    w, h = 400, 320; b = rocket(100, 40)
    b += ARROW(160, 150, 160, 90, C_VEL, 3) + V(176, 116, 'v', C_VEL, 17)
    b += T(100, 300, 'صاروخ ينطلق إلى أعلى', 13, color=MUTED)
    b += forces_at(290, 160, [(90, 110, '1'), (-90, 60, '2')])
    b += plus(350, 270)
    save('c4l1-o27-rocket-arrows.svg', svg(w, h, b))




# ============ O28 ============
def o28():
    w, h = 420, 320; b = rocket(90, 40)
    b += ARROW(150, 170, 150, 110, C_ACC, 3) + V(166, 140, 'a', C_ACC, 17)
    b += T(90, 300, 'صاروخ يتسارع إلى أعلى', 13, color=MUTED)
    b += forces_at(300, 160, [(90, 80, '1', {'ld': 18}), (0, 80, '2', {'ld': 18}), (-90, 80, '3', {'ld': 18}), (180, 80, '4', {'ld': 18})])
    save('c4l1-o28-rocket-dirs.svg', svg(w, h, b))

    # مركبة تتحرك نحو +x وتتباطأ
    w, h = 600, 150; xs = [50]
    for d in (130, 105, 80, 55, 30): xs.append(xs[-1] + d)
    save('c4l1-o28-slowing-md.svg', svg(w, h, motion_row(xs, 70, w, h=h)))

    panels('c4l1-o28-rocket-fbds.svg', [
        [(90, 60, 'F_{thrust}'), (-90, 90, 'F_g')],
        [(90, 100, 'F_{thrust}'), (-90, 50, 'F_g')],
        [(0, 70, 'F_{thrust}', {'ld': -34, 'dy': -24}), (-90, 70, 'F_g')],
        [(-90, 100, 'F_{thrust}', {'ox': 10, 'dx': 30, 'dy': -30}), (-90, 50, 'F_g', {'ox': -10, 'dx': -24, 'dy': -30})],
    ], pw=170, ph=300)

    # تتسارع نحو −x، البداية على اليمين
    w, h = 600, 150; xs = [560]
    for d in (30, 55, 80, 105, 130): xs.append(xs[-1] - d)
    save('c4l1-o28-essay-md.svg', svg(w, h, motion_row(sorted(xs), 70, w, start_idx=1, h=h)))


# ============ O29 ============
def plane(x, y):
    b = f'<path d="M {x} {y} Q {x + 10} {y - 14} {x + 40} {y - 14} L {x + 150} {y - 14} Q {x + 172} {y - 8} {x + 150} {y} Z" fill="#e9eef5" stroke="{INK}" stroke-width="2"/>'
    b += f'<polygon points="{x + 70},{y - 6} {x + 110},{y - 6} {x + 80},{y + 18} {x + 60},{y + 18}" fill="#c9d3e0" stroke="{INK}" stroke-width="1.6"/>'
    b += f'<polygon points="{x + 2},{y - 8} {x + 22},{y - 14} {x + 6},{y - 40} {x - 6},{y - 40}" fill="#c9d3e0" stroke="{INK}" stroke-width="1.6"/>'
    b += L(x + 60, y, x + 60, y + 20, INK, 2) + L(x + 130, y, x + 130, y + 20, INK, 2)
    b += f'<circle cx="{x + 60}" cy="{y + 24}" r="7" fill="{INK}"/><circle cx="{x + 130}" cy="{y + 24}" r="7" fill="{INK}"/>'
    return b


def o29():
    w, h = 400, 320; b = rocket(100, 40)
    b += ARROW(160, 150, 160, 90, C_VEL, 3) + V(176, 116, 'v', C_VEL, 17)
    b += T(100, 300, 'صاروخ ينطلق إلى أعلى', 13, color=MUTED)
    b += forces_at(290, 160, [(90, 110, '1'), (-90, 60, 'F_g')])
    b += plus(350, 270)
    save('c4l1-o29-rocket-label.svg', svg(w, h, b))

    w, h = 640, 300; b = plane(40, 150) + ground(20, 260, 181)
    b += ARROW(70, 225, 160, 225, C_VEL, 3) + V(178, 231, 'v', C_VEL, 17, 'start')
    b += T(130, 280, 'طائرة تتسارع على المدرج', 13, color=MUTED)
    b += forces_at(470, 150, [(0, 120, '1'), (180, 50, '2'), (90, 80, '3'), (-90, 80, '4')])
    b += plus(320, 280, 'x', 46) + plus(320, 280, 'y', 46)
    save('c4l1-o29-plane-arrows.svg', svg(w, h, b))


# ============ O30 ============
def apple(x, y): return f'<circle cx="{x}" cy="{y}" r="16" fill="#9bc96b" stroke="{INK}" stroke-width="2"/>' + L(x, y - 16, x + 3, y - 24, INK, 2)


def o30():
    w, h = 460, 300; tb, (bx, by) = table_book(20, 150)
    b = tb + hand_left(bx - 40, by)
    b += T(105, 285, 'يد تدفع كتابًا على طاولة', 13, color=MUTED)
    b += forces_at(340, 140, [(90, 75, '1'), (0, 55, '2'), (-90, 75, '3')])
    save('c4l1-o30-book-table.svg', svg(w, h, b))

    w, h = 460, 300; b = frame(0, 0, 230, h, 'a') + frame(230, 0, 230, h, 'b')
    b += f'<path d="M 20 50 Q 120 36 200 56" fill="none" stroke="{WOOD}" stroke-width="9" stroke-linecap="round"/>'
    b += L(115, 44, 115, 82, INK, 2) + apple(115, 104)
    b += f'<path d="M 250 50 Q 350 36 430 56" fill="none" stroke="{WOOD}" stroke-width="9" stroke-linecap="round"/>'
    b += apple(345, 170) + ARROW(385, 150, 385, 210, C_VEL, 3) + V(401, 186, 'v', C_VEL, 17)
    b += ground(14, 216, 262) + ground(244, 446, 262)
    save('c4l1-o30-apple.svg', svg(w, h, b))


# ============ O31 ============
def earth_panel(x0, y0, kind, num):
    pw, ph = 190, 210; b = frame(x0, y0, pw, ph, num)
    cx, cy, R = x0 + pw / 2, y0 + ph / 2 + 8, 52
    b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#d8ead2" stroke="{INK}" stroke-width="2"/>' + DOT(cx, cy, 2.5, MUTED)
    for ang in (90, 0, 225):
        a = math.radians(ang); px, py = cx + (R + 5) * math.cos(a), cy - (R + 5) * math.sin(a)
        d = {'center': ang + 180, 'down': -90, 'out': ang, 'tangent': ang + 90}[kind]
        r = math.radians(d); ln = 28
        b += ARROW(px, py, px + ln * math.cos(r), py - ln * math.sin(r), C_FORCE, 2.6, 9) + DOT(px, py, 4.5, INK)
    return b


def o31():
    b = ''
    for k, kind in enumerate(['down', 'out', 'center', 'tangent']):
        b += earth_panel((k % 2) * 190, (k // 2) * 210, kind, k + 1)
    save('c4l1-o31-earth-panels.svg', svg(380, 420, b))

    w, h = 460, 320; ang = 30; a = math.radians(ang)
    x0, y0, x1 = 30, 290, 440; y1 = y0 - (x1 - x0) * math.tan(a)
    b = f'<polygon points="{x0},{y0} {x1},{y0} {x1},{y1:.1f}" fill="#f3efe6" stroke="{INK}" stroke-width="2"/>'
    mx, my = x0 + 0.5 * (x1 - x0), y0 - 0.5 * (x1 - x0) * math.tan(a)
    nx, ny = -math.sin(a), -math.cos(a); cx, cy = mx + 26 * nx, my + 26 * ny
    b += RECT(cx - 30, cy - 26, 60, 52, INK, '#eef2f8', 2, -ang, cx, cy)
    b += forces_at(cx, cy, [(-90, 85, '1', {'ld': 16}), (-90 + ang, 85, '2', {'ld': 16}), (180 + ang, 85, '3', {'ld': 16}), (90 + ang, 85, '4', {'ld': 16})])
    b += f'<path d="M {x0 + 60} {y0} A 60 60 0 0 0 {x0 + 60 * math.cos(a):.1f} {y0 - 60 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.5"/>' + T(x0 + 80, y0 - 10, '‎30°', 14)
    save('c4l1-o31-incline-dirs.svg', svg(w, h, b))

    w, h = 420, 400; cx, cy, R = 210, 200, 120
    b = f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#d8ead2" stroke="{INK}" stroke-width="2"/>' + DOT(cx, cy, 3, MUTED) + T(cx, cy + 20, 'مركز الأرض', 12, color=MUTED)
    for ang, lab in ((90, 'A'), (0, 'B'), (-90, 'C')):
        r = math.radians(ang); px, py = cx + (R + 9) * math.cos(r), cy - (R + 9) * math.sin(r)
        b += DOT(px, py, 7, '#c46a10')
        lx, ly = cx + (R + 34) * math.cos(r), cy - (R + 34) * math.sin(r) + 6
        b += T(lx + (12 if ang != 0 else 0), ly, lab, 17, weight='bold')
    save('c4l1-o31-earth-people.svg', svg(w, h, b))


# ============ O32 ============
def hanging(cx, top, ln=110, r=22):
    return ceiling(cx - 50, cx + 50, top) + L(cx, top, cx, top + ln, INK, 2) + f'<circle cx="{cx}" cy="{top + ln + r}" r="{r}" fill="#b8c4e6" stroke="{INK}" stroke-width="2"/>'


def o32():
    w, h = 400, 320; b = hanging(100, 30)
    b += T(100, 230, 'كرة معلقة ساكنة', 13, color=MUTED)
    b += forces_at(280, 160, [(90, 80, 'F_T'), (-90, 80, '2')])
    b += plus(350, 270)
    save('c4l1-o32-hanging-ball.svg', svg(w, h, b))

    w, h = 460, 300; tb, _ = table_book(20, 160)
    b = tb + T(105, 290, 'كتاب ساكن على طاولة', 13, color=MUTED)
    b += forces_at(330, 145, [(90, 80, 'F_N'), (-90, 80, 'F_g')])
    b += plus(410, 270)
    save('c4l1-o32-book-fbd.svg', svg(w, h, b))

    w, h = 420, 340; b = L(100, 20, 100, 134, INK, 2) + bucket(100, 150)
    b += ARROW(170, 200, 170, 140, C_VEL, 3) + V(186, 172, 'v', C_VEL, 17)
    b += T(100, 240, 'دلو يُرفع بحبل', 13, color=MUTED)
    b += forces_at(300, 170, [(90, 80, '1'), (-90, 80, '2')])
    b += plus(370, 300)
    save('c4l1-o32-bucket.svg', svg(w, h, b))


# ============ O33 ============
def o33():
    w, h = 400, 320; cx, cy = 90, 120
    b = f'<circle cx="{cx}" cy="{cy}" r="24" fill="#c8a07a" stroke="{INK}" stroke-width="2"/>' + sys_circle(cx, cy, 40)
    b += T(cx, 66, 'النظام', 13, color=MUTED)
    b += ARROW(160, 90, 160, 160, C_VEL, 3) + V(176, 130, 'v', C_VEL, 17)
    b += ARROW(200, 100, 200, 150, C_ACC, 3) + V(216, 130, 'a', C_ACC, 17)
    b += forces_at(310, 100, [(-90, 110, 'F_g')])
    b += plus(370, 290)
    b += T(110, 290, 'كرة تسقط سقوطًا حرًا', 13, color=MUTED)
    save('c4l1-o33-freefall.svg', svg(w, h, b))


# ============ O34 ============
def o34():
    # أصيص يسقط سقوطًا حرًا: (1) قوة عمودية زائدة (2) سهم نحو الجسم (3) صحيح (4) القوة المحصلة مرسومة سهمًا إضافيًا
    panels('c4l1-o34-pot-fbds.svg', [
        [(-90, 80, 'F_g'), (90, 80, 'F_N')],
        [(90, 80, 'F_g', {'toward': True})],
        [(-90, 80, 'F_g')],
        [(-90, 80, 'F_g', {'ox': -10, 'dx': -22}), (-90, 80, NET, {'ox': 10, 'dx': 34})],
    ], pw=170, ph=280)

    # مظلي يهبط بسرعة منتظمة: (1) قوة ناقصة (2) صحيح (3) أطوال خاطئة (4) اتجاه قوة الهواء خاطئ
    panels('c4l1-o34-parachute-fbds.svg', [
        [(-90, 80, 'F_g')],
        [(90, 80, AIR), (-90, 80, 'F_g')],
        [(90, 40, AIR), (-90, 100, 'F_g')],
        [(-90, 80, 'F_g', {'ox': -10, 'dx': -22}), (-90, 80, AIR, {'ox': 10, 'dx': 36})],
    ], pw=170, ph=300)

    # صندوق يسحبه سلك بسرعة منتظمة نحو اليمين: (1) احتكاك ناقص (2) احتكاك باتجاه الحركة (3) F_N أقصر من F_g (4) صحيح
    def box_items(kind):
        v = [(90, 70, 'F_N'), (-90, 70, 'F_g')]
        if kind == 3: v = [(90, 35, 'F_N'), (-90, 70, 'F_g')]
        h = [(0, 60, 'F_T', {'ld': 20, 'dy': -18})]
        if kind in (3, 4): h.append((180, 60, 'f_f', {'ld': 20, 'dy': -18}))
        return v + h
    pw, ph = 200, 260; b = ''
    for k in range(4):
        x0 = k * pw; cx, cy = x0 + pw / 2 + 4, ph / 2 + 4
        b += frame(x0, 0, pw, ph, k + 1)
        if k + 1 == 2:
            b += forces_at(cx, cy, [(90, 70, 'F_N'), (-90, 70, 'F_g'), (0, 62, 'F_T', {'ld': 18, 'oy': -6, 'dy': -10}), (0, 62, 'f_f', {'ld': 18, 'oy': 6, 'dy': 12})])
        else:
            b += forces_at(cx, cy, box_items(k + 1))
        b += plus(x0 + 20, ph - 22, 'x', 34) + plus(x0 + 20, ph - 22, 'y', 34)
    save('c4l1-o34-box-fbds.svg', svg(4 * pw, ph, b))

    # دلو يُرفع بسرعة متناقصة: (1) صحيح F_T < F_g (2) متساويتان (3) F_T > F_g (4) القوة المحصلة مرسومة
    panels('c4l1-o34-bucket-fbds.svg', [
        [(90, 55, 'F_T'), (-90, 90, 'F_g')],
        [(90, 80, 'F_T'), (-90, 80, 'F_g')],
        [(90, 100, 'F_T'), (-90, 55, 'F_g')],
        [(90, 55, 'F_T'), (-90, 90, 'F_g', {'ox': -10, 'dx': -22}), (-90, 35, NET, {'ox': 10, 'dx': 36})],
    ], pw=170, ph=300)

    # مخطط خاطئ لكرة معلقة: سهم الشد مرسوم نحو الجسم
    w, h = 400, 320; b = hanging(100, 30) + T(100, 230, 'كرة معلقة ساكنة', 13, color=MUTED)
    b += forces_at(280, 160, [(90, 80, 'F_T', {'toward': True, 'dx': 26, 'dy': 30}), (-90, 80, 'F_g')])
    b += plus(350, 280)
    save('c4l1-o34-ball-wrong.svg', svg(w, h, b))

    # مخطط خاطئ لسيارة تسير بسرعة منتظمة: F_N ناقصة، f_f نحو الجسم، القوة المحصلة مرسومة
    w, h = 640, 300
    b = RECT(40, 120, 170, 40, INK, '#f0d9a8') + RECT(80, 90, 90, 32, INK, '#f0d9a8')
    b += f'<circle cx="80" cy="162" r="15" fill="{INK}"/><circle cx="175" cy="162" r="15" fill="{INK}"/>' + ground(20, 260, 177)
    b += ARROW(80, 220, 170, 220, C_VEL, 3) + V(186, 226, 'v', C_VEL, 17, 'start')
    b += T(130, 270, 'سيارة تسير بسرعة متجهة ثابتة', 13, color=MUTED)
    cx, cy = 450, 140
    b += forces_at(cx, cy, [(0, 90, 'F_{thrust}', {'ld': 40, 'dy': -20}), (-90, 80, 'F_g'),
                            (180, 90, 'f_f', {'toward': True, 'ld': 18, 'dy': -22})])
    b += ARROW(cx + 10, cy + 40, cx + 70, cy + 40, C_FORCE, 3) + FA(cx + 102, cy + 46, 'المحصلة')
    b += plus(300, 280, 'x', 46) + plus(300, 280, 'y', 46)
    save('c4l1-o34-car-wrong.svg', svg(w, h, b))


# ============ O35 ============
def o35():
    w, h = 420, 340; b = ceiling(50, 150, 30) + L(100, 30, 100, 150, INK, 2)
    b += f'<circle cx="100" cy="174" r="24" fill="#b8c4e6" stroke="{INK}" stroke-width="2"/>' + sys_circle(100, 174, 42)
    b += T(100, 250, 'النظام: الكرة', 13, color=MUTED)
    b += forces_at(300, 170, [(90, 85, 'F_T'), (-90, 85, 'F_g')])
    b += plus(370, 300)
    save('c4l1-o35-hanging-system.svg', svg(w, h, b))

    w, h = 420, 320; b = ball_hand(100, 130) + sys_circle(100, 130, 42)
    b += T(100, 270, 'كرة ساكنة على راحة اليد', 13, color=MUTED)
    b += forces_at(300, 160, [(90, 85, '1'), (-90, 85, '2')])
    b += plus(370, 290)
    save('c4l1-o35-ball-hand.svg', svg(w, h, b))


# ============ O36 ============
def o36():
    graph('c4l1-o36-three-lines.svg', [
        {'pts': [(0, 0), (3, 6)], 'color': INK, 'label': 'A', 'at': (2.6, 5.2), 'dx': -22, 'dy': -4},
        {'pts': [(0, 0), (3, 3)], 'color': ORANGE, 'label': 'B', 'at': (3, 3), 'dx': -14, 'dy': -12},
        {'pts': [(0, 0), (3, 2)], 'color': GREEN, 'label': 'C', 'at': (3, 2), 'dx': -14, 'dy': 22},
    ], (0, 3.2), (0, 6.4), FL, AL, 0.5, 1)

    graph('c4l1-o36-one-line.svg', [{'pts': [(0, 0), (4, 2)], 'color': ORANGE}], (0, 4.5), (0, 2.5), FL, AL, 0.5, 0.25,
          marks=[(1, 0.5, ''), (2, 1, ''), (3, 1.5, ''), (4, 2, '')])

    # أشكال العلاقة بين التسارع والكتلة عند ثبات القوة
    def mini(x0, kind, num):
        pw, ph = 190, 200; b = frame(x0, 0, pw, ph, num)
        L0, B0, R0, T0 = x0 + 40, ph - 36, x0 + pw - 20, 44
        b += ARROW(L0, B0, R0, B0, INK, 1.6, 8) + ARROW(L0, B0, L0, T0 - 6, INK, 1.6, 8)
        b += T(R0 - 2, B0 + 20, 'm', 15, 'end', italic=True) + V(L0 - 14, T0 + 6, 'a', INK, 15)
        X = lambda u: L0 + u * (R0 - L0 - 10); Y = lambda v: B0 - v * (B0 - T0 - 8)
        if kind == 'hyper': pts = [(u / 20, min(1, 0.12 / (u / 20))) for u in range(2, 21)]
        elif kind == 'up': pts = [(0, 0), (1, 1)]
        elif kind == 'down': pts = [(0.05, 1), (0.95, 0.05)]
        else: pts = [(0.05, 0.55), (1, 0.55)]
        p = ' '.join(f'{X(u):.1f},{Y(v):.1f}' for u, v in pts)
        return b + f'<polyline points="{p}" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linejoin="round"/>'
    b = mini(0, 'up', 1) + mini(190, 'hyper', 2) + mini(380, 'flat', 3) + mini(570, 'down', 4)
    save('c4l1-o36-shapes.svg', svg(760, 200, b))

    graph('c4l1-o36-a-invm.svg', [{'pts': [(0, 0), (2, 12)], 'color': ORANGE}], (0, 2.2), (0, 13), 'مقلوب الكتلة (kg^-1)', AL, 0.5, 2,
          marks=[(0.5, 3, ''), (1, 6, ''), (1.5, 9, ''), (2, 12, '')])

    graph('c4l1-o36-carts-essay.svg', [
        {'pts': [(0, 0), (1.5, 6)], 'color': INK, 'label': 'عربة', 'at': (1.5, 6), 'dx': -40, 'dy': -2},
        {'pts': [(0, 0), (1.5, 3)], 'color': ORANGE, 'label': 'عربتان', 'at': (1.5, 3), 'dx': -50, 'dy': -12},
        {'pts': [(0, 0), (1.5, 2)], 'color': GREEN, 'label': 'ثلاث عربات', 'at': (1.5, 2), 'dx': -60, 'dy': 34},
    ], (0, 1.6), (0, 6.4), FL, AL, 0.25, 1, marks=[(1.5, 6, ''), (1.5, 3, ''), (1.5, 2, '')])


# ============ O37 ============
def o37():
    graph('c4l1-o37-fm-graph.svg', [{'pts': [(0, 0), (2.2, 3.3)], 'color': ORANGE}], (0, 2.4), (0, 3.6), 'الكتلة (kg)', 'مقدار القوة المحصلة (N)', 0.4, 0.6,
          marks=[(0.5, 0.76, ''), (1.0, 1.48, ''), (1.5, 2.27, ''), (2.0, 2.97, '')])
    graph('c4l1-o37-fm-slope.svg', [{'pts': [(0, 0), (1.8, 3.6)], 'color': ORANGE}], (0, 2.0), (0, 4.0), 'الكتلة (kg)', 'مقدار القوة المحصلة (N)', 0.4, 0.8,
          marks=[(0.4, 0.81, ''), (0.8, 1.58, ''), (1.2, 2.42, ''), (1.6, 3.19, '')])


if __name__ == '__main__':
    o27(); o28(); o29(); o30(); o31(); o32(); o33(); o34(); o35(); o36(); o37()
