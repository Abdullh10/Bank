import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-1 (الأهداف O01–O09): مغانط بقطبين، خطوط مجال خضراء (كالكتاب)، بوصلات، سلك مستقيم ومقطعه (× داخل، • خارج)، ملفات لولبية.
# اصطلاح الكتاب: خطوط المجال المغناطيسي بالأخضر، والتيار I قائم غير مائل، والمجال B قائم غير عريض.
FIELD = '#1e8449'; NRED = '#c0392b'; SBLUE = '#2e6fb5'; GREY = '#b9c0ca'; COPPER = '#c07a45'

def magnet(x, y, w=160, h=40, left='N', right='S', lab=True):
    """قضيب مغناطيسي أفقي يبدأ من (x, y) أعلى يسار. left/right: 'N' أو 'S' أو None (طرف مجهول رمادي) أو نص يُكتب."""
    def half(xx, p):
        fill = NRED if p == 'N' else SBLUE if p == 'S' else GREY
        return RECT(xx, y, w / 2, h, INK, fill, 1.5)
    b = half(x, left) + half(x + w / 2, right)
    if lab:
        for xx, p in ((x + 18, left), (x + w - 18, right)):
            if p: b += T(xx, y + h / 2 + 6, p, 17, color='#fff' if p in ('N', 'S') else INK, weight='bold')
    return b

def vmagnet(x, y, w=40, h=150, top='N', bottom='S', lab=True):
    def half(yy, p):
        fill = NRED if p == 'N' else SBLUE if p == 'S' else GREY
        return RECT(x, yy, w, h / 2, INK, fill, 1.5)
    b = half(y, top) + half(y + h / 2, bottom)
    if lab:
        for yy, p in ((y + 22, top), (y + h - 10, bottom)):
            if p: b += T(x + w / 2, yy, p, 17, color='#fff' if p in ('N', 'S') else INK, weight='bold')
    return b

def compass(x, y, ang=None, r=20):
    """بوصلة: دائرة وإبرة طرفها الشمالي أحمر يشير بالزاوية ang (درجات، 0 = يمين، 90 = أعلى). ang=None بلا إبرة."""
    b = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#f7f4ea" stroke="{INK}" stroke-width="1.8"/>'
    if ang is not None:
        a = math.radians(ang); c, s = math.cos(a), -math.sin(a); px, py = -s, c; L_ = r - 4; wdt = 4.5
        tip = (x + L_ * c, y + L_ * s); tail = (x - L_ * c, y - L_ * s); s1 = (x + wdt * px, y + wdt * py); s2 = (x - wdt * px, y - wdt * py)
        b += f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {s1[0]:.1f},{s1[1]:.1f} {s2[0]:.1f},{s2[1]:.1f}" fill="{NRED}"/>'
        b += f'<polygon points="{tail[0]:.1f},{tail[1]:.1f} {s1[0]:.1f},{s1[1]:.1f} {s2[0]:.1f},{s2[1]:.1f}" fill="#d5d9df" stroke="{MUTED}" stroke-width="0.8"/>'
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{INK}"/>'
    return b

def head(x, y, ang, color=FIELD, size=9):
    """رأس سهم عند (x, y) باتجاه ang (راديان، إحداثيات الشاشة)."""
    p1 = (x - size * math.cos(ang - 0.42), y - size * math.sin(ang - 0.42)); p2 = (x - size * math.cos(ang + 0.42), y - size * math.sin(ang + 0.42))
    return f'<polygon points="{x + 0.4 * size * math.cos(ang):.1f},{y + 0.4 * size * math.sin(ang):.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'

def trace(poles, sx, sy, sgn, box, step=2.0, maxn=4000, sink_r=7):
    """تتبع خط مجال لمجموعة أقطاب [(x, y, q)] (q=+1 شمالي، −1 جنوبي) من (sx, sy)؛ sgn=+1 مع المجال. يعيد قائمة النقاط باتجاه المجال."""
    def B(x, y):
        bx = by = 0.0
        for px, py, q in poles:
            dx, dy = x - px, y - py; r3 = (dx * dx + dy * dy) ** 1.5 + 1e-9
            bx += q * dx / r3; by += q * dy / r3
        return bx, by
    pts = [(sx, sy)]; x, y = sx, sy
    for _ in range(maxn):
        bx, by = B(x, y); m = math.hypot(bx, by) or 1e-9
        x += sgn * step * bx / m; y += sgn * step * by / m; pts.append((x, y))
        if not (box[0] - 30 < x < box[2] + 30 and box[1] - 30 < y < box[3] + 30): break
        if any(q * sgn < 0 and math.hypot(x - px, y - py) < sink_r for px, py, q in poles): break
    return pts if sgn > 0 else pts[::-1]

def draw_line(pts, box, arrows=True, color=FIELD, w=1.8, arrow_at=0.5):
    d = 'M ' + ' L '.join(f'{px:.1f} {py:.1f}' for px, py in pts[::2])
    out = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    if arrows and len(pts) > 20:
        inside = [i for i, p in enumerate(pts) if box[0] + 8 < p[0] < box[2] - 8 and box[1] + 8 < p[1] < box[3] - 8]
        if len(inside) > 10:
            k = inside[int(len(inside) * arrow_at)]; k2 = min(k + 2, len(pts) - 1)
            out += head(pts[k][0], pts[k][1], math.atan2(pts[k2][1] - pts[k][1], pts[k2][0] - pts[k][0]), color)
    return out

def field_lines(poles, starts, box, arrows=True, **kw):
    return ''.join(draw_line(trace(poles, sx, sy, sgn, box), box, arrows) for sx, sy, sgn in starts)

def clip(body, w, h, cid='c'):
    return f'<defs><clipPath id="{cid}"><rect x="0" y="0" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#{cid})">{body}</g>'

def bar_field(cx, cy, half=62, n=12, arrows=True, box=None, skip_axis=False):
    """خطوط مجال قضيب مغناطيسي أفقي مركزه (cx, cy)، قطبه الشمالي على اليسار، متناظرة يمينًا ويسارًا."""
    poles = [(cx - half, cy, 1), (cx + half, cy, -1)]; out = ''
    for k in range(n):
        a = math.radians(180 - 170 * (k + 0.5) / n)  # زوايا الانطلاق في النصف العلوي
        for sy_ in (1, -1):
            pts = trace(poles, cx - half + 7 * math.cos(a), cy - sy_ * 7 * math.sin(a), 1, box)
            out += draw_line(pts, box, arrows)
            if math.hypot(pts[-1][0] - (cx + half), pts[-1][1] - cy) > 10:  # خط هارب: أضف صورته المرآتية الداخلة إلى الجنوبي
                out += draw_line([(2 * cx - x, y) for x, y in pts][::-1], box, arrows)
    if not skip_axis:
        out += draw_line([(cx - half - 7 - t, cy) for t in range(0, 400, 2)], box, arrows, arrow_at=0.3)
        out += draw_line([(cx + half + 407 - t, cy) for t in range(0, 400, 2)], box, arrows, arrow_at=0.7)
    return out

def wire_dot(x, y, kind, r=13, fill='#f3e3d3'):
    """مقطع سلك عمودي على الصفحة: kind = 'out' (•) أو 'in' (×) أو None."""
    b = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{COPPER}" stroke-width="2.2"/>'
    if kind == 'out': b += f'<circle cx="{x}" cy="{y}" r="3.6" fill="{INK}"/>'
    if kind == 'in': b += L(x - 6, y - 6, x + 6, y + 6, INK, 2.4) + L(x - 6, y + 6, x + 6, y - 6, INK, 2.4)
    return b

def ring(x, y, r, cw=None, color=FIELD, w=1.8, n=2, phase=0):
    """دائرة مجال حول نقطة، مع أسهم عددها n اتجاهها cw=True مع عقارب الساعة (على الشاشة)."""
    b = f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    if cw is not None:
        for k in range(n):
            a = math.radians(phase + k * 360 / n); px, py = x + r * math.cos(a), y + r * math.sin(a)
            tang = a + (math.pi / 2 if cw else -math.pi / 2)
            b += head(px, py, tang, color, 10)
    return b

def xmark(x, y, s=6, color=FIELD, w=2): return L(x - s, y - s, x + s, y + s, color, w) + L(x - s, y + s, x + s, y - s, color, w)
def omark(x, y, color=FIELD): return f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{color}" stroke-width="1.8"/><circle cx="{x}" cy="{y}" r="2.6" fill="{color}"/>'

def coil(x0, y, x1, turns, r=34, color=COPPER, w=3):
    """ملف لولبي أفقي من x0 إلى x1: كل لفة قطع ناقص؛ نصفه الخلفي (الأيسر) باهت والأمامي (الأيمن) داكن."""
    pitch = (x1 - x0) / turns; rx = pitch * 0.42; b = ''
    for k in range(turns):
        xc = x0 + (k + 0.5) * pitch
        b += f'<path d="M {xc:.1f} {y - r} A {rx:.1f} {r} 0 0 0 {xc:.1f} {y + r}" fill="none" stroke="#dcc0a6" stroke-width="{w - 0.8}"/>'
    for k in range(turns):
        xc = x0 + (k + 0.5) * pitch
        b += f'<path d="M {xc:.1f} {y + r} A {rx:.1f} {r} 0 0 0 {xc + pitch * 0.5:.1f} {y - r}" fill="none" stroke="{color}" stroke-width="{w}"/>' if k < turns - 1 else f'<path d="M {xc:.1f} {y + r} A {rx:.1f} {r} 0 0 0 {xc:.1f} {y - r}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    return b

# ───────────────────────── O01 خصائص المغانط
def o01():
    # مغناطيس معلّق ومغناطيس يقرّب منه (الأقطاب الشمالية متقابلة)
    b = L(150, 20, 150, 62, MUTED, 1.5) + L(90, 62, 210, 62, MUTED, 1.5) + L(90, 62, 90, 80, MUTED, 1.5) + L(210, 62, 210, 80, MUTED, 1.5)
    b += magnet(70, 80, 160, 40, 'S', 'N') + T(150, 150, 'مغناطيس معلّق بخيط', 13, color=MUTED)
    b += magnet(310, 80, 160, 40, 'N', 'S') + ARROW(390, 140, 335, 140, INK, 2) + T(400, 166, 'يُقرَّب', 13, color=MUTED)
    save('c3l1-o01-hang.svg', svg(520, 185, b))
    # أقراص مغناطيسية مثقوبة طافية على ساق
    b = RECT(146, 20, 8, 300, '#8a6d3b', '#d8b46a', 1)
    ys = [60, 120, 180, 240, 290]
    for k, yy in enumerate(ys):
        b += f'<rect x="100" y="{yy}" width="100" height="20" rx="3" fill="#59606b" stroke="{INK}" stroke-width="1.5"/>' + RECT(146, yy, 8, 20, '#8a6d3b', '#d8b46a', 1)
        b += T(225, yy + 15, str(k + 1), 15, 'start', weight='bold')
    b += T(150, 54, 'N', 15, color=NRED, weight='bold') + T(205, 54, '(الوجه العلوي للقرص 1)', 11, 'start', MUTED)
    save('c3l1-o01-rings.svg', svg(400, 330, b))
    # مقالي: مغناطيسان أطرافهما مرقّمة
    b = magnet(30, 60, 170, 44, 'N', None, lab=False) + T(48, 89, 'N', 17, color='#fff', weight='bold') + T(185, 50, '2', 15, weight='bold')
    b += T(48, 50, '1', 15, weight='bold')
    b += RECT(260, 60, 85, 44, INK, GREY, 1.5) + RECT(345, 60, 85, 44, INK, GREY, 1.5) + T(275, 50, '3', 15, weight='bold') + T(415, 50, '4', 15, weight='bold')
    b += RECT(115, 60, 85, 44, INK, GREY, 1.5)
    b += T(115, 140, 'المغناطيس الأول', 13, color=MUTED) + T(345, 140, 'المغناطيس الثاني', 13, color=MUTED)
    save('c3l1-o01-e-pair.svg', svg(460, 160, b))

# ───────────────────────── O02 المغانط المؤقتة
def o02():
    # مغناطيس دائم يلامس رأس مسمار حديدي، والطرف السفلي A
    b = magnet(60, 40, 260, 36, 'S', 'N') + T(190, 26, 'مغناطيس دائم', 13, color=MUTED)
    b += RECT(273, 76, 10, 150, INK, '#a7adb5', 1.5) + RECT(262, 76, 32, 7, INK, '#a7adb5', 1.2)
    b += f'<polygon points="273,226 283,226 278,244" fill="#a7adb5" stroke="{INK}" stroke-width="1.2"/>'
    b += T(300, 240, 'A', 16, 'start', weight='bold', italic=True) + T(310, 150, 'مسمار حديدي', 13, 'start', MUTED)
    save('c3l1-o02-nail.svg', svg(420, 260, b))
    # مقالي: قطب جنوبي يلامس رأس مسمار، ودبوس صغير معلّق بطرف المسمار
    b = vmagnet(150, 10, 40, 140, 'N', 'S')
    b += RECT(165, 150, 10, 120, INK, '#a7adb5', 1.5) + f'<polygon points="165,270 175,270 170,286" fill="#a7adb5" stroke="{INK}" stroke-width="1.2"/>'
    b += RECT(167, 288, 6, 70, INK, '#cfd4da', 1.2)
    b += T(196, 162, 'P', 15, 'start', weight='bold', italic=True) + T(196, 282, 'Q', 15, 'start', weight='bold', italic=True) + T(186, 352, 'R', 15, 'start', weight='bold', italic=True)
    b += T(132, 220, 'مسمار', 13, 'end', MUTED) + T(150, 330, 'دبوس', 13, 'end', MUTED)
    save('c3l1-o02-chain.svg', svg(300, 370, b))

# ───────────────────────── O03 التدفق المغناطيسي
def o03():
    W, H = 560, 330; cx, cy = 280, 175
    b = bar_field(cx, cy, 62, 7, True, (0, 0, W, H))
    b = clip(b, W, H, 'o3') + magnet(cx - 80, cy - 20, 160, 40, 'N', 'S')
    # سطحان متساويان (يُريان من الحافة) عند X قرب القطب وعند Y بعيدًا
    b += L(cx - 100, cy - 40, cx - 100, cy + 40, '#7a4b00', 5) + T(cx - 116, cy - 44, 'X', 17, weight='bold', italic=True)
    b += L(cx + 120, cy - 130, cx + 200, cy - 130, '#7a4b00', 5) + T(cx + 160, cy - 140, 'Y', 17, weight='bold', italic=True)
    save('c3l1-o03-flux.svg', svg(W, H, b))

# ───────────────────────── O04 اتجاه خطوط المجال حول المغناطيس الدائم
def o04():
    # بوصلة فوق منتصف مغناطيس (N يسار)
    b = magnet(160, 150, 200, 44, 'N', 'S') + compass(260, 80, None, 24) + T(300, 70, 'P', 16, 'start', weight='bold', italic=True)
    save('c3l1-o04-above.svg', svg(520, 230, b))
    # بوصلتان عند طرفي مغناطيس مجهول القطبين، إبرتاهما تشيران لليسار
    W, H = 560, 220; cx, cy = 280, 110
    fl = clip(bar_field(cx, cy, 62, 6, False, (0, 0, W, H)), W, H, 'o4b')
    b = fl + magnet(cx - 80, cy - 20, 160, 40, None, None, lab=False) + T(cx - 64, cy + 6, 'X', 17, weight='bold', italic=True) + T(cx + 64, cy + 6, 'Y', 17, weight='bold', italic=True)
    b += compass(60, cy, 180, 26) + compass(500, cy, 180, 26)
    save('c3l1-o04-two.svg', svg(W, H, b))
    # خطوط مجال بأسهم حول مغناطيس أطرافه مرقمة (الشمالي على اليمين)
    W, H = 560, 300; cx, cy = 280, 150
    fl = bar_field(cx, cy, 62, 7, True, (0, 0, W, H))
    fl = f'<g transform="translate({2 * cx} 0) scale(-1 1)">{fl}</g>'  # الشمالي إلى اليمين
    b = clip(fl, W, H, 'o4c') + magnet(cx - 80, cy - 20, 160, 40, None, None, lab=False)
    b += T(cx - 64, cy + 6, '1', 17, weight='bold') + T(cx + 64, cy + 6, '2', 17, weight='bold')
    save('c3l1-o04-arrows.svg', svg(W, H, b))
    # قطبان مختلفان متقابلان وبوصلة في المنتصف
    b = magnet(20, 80, 180, 44, 'S', 'N') + magnet(320, 80, 180, 44, 'S', 'N', lab=False)
    b += T(338, 109, 'S', 17, color='#fff', weight='bold') + T(482, 109, 'N', 17, color='#fff', weight='bold')
    b += compass(260, 102, None, 24) + T(260, 150, 'P', 16, weight='bold', italic=True)
    save('c3l1-o04-gap.svg', svg(520, 170, b))
    # أربعة مواضع للبوصلة حول مغناطيس (الشمالي على اليمين)
    b = magnet(180, 130, 200, 44, 'S', 'N')
    for x, y, lab in ((110, 152, 'A'), (280, 70, 'B'), (450, 152, 'C'), (280, 236, 'D')):
        b += compass(x, y, None, 22) + T(x + (0 if lab in 'BD' else 0), y + (-32 if lab in 'AC' else (-32 if lab == 'B' else 42)), lab, 16, weight='bold', italic=True)
    save('c3l1-o04-four.svg', svg(560, 290, b))
    # مقالي: زوجان من المغانط (قطبان جنوبيان متقابلان، وقطبان مختلفان متقابلان)
    b = T(260, 22, '(a)', 15) + magnet(30, 40, 180, 40, 'N', 'S') + magnet(310, 40, 180, 40, 'S', 'N')
    b += T(260, 122, '(b)', 15) + magnet(30, 140, 180, 40, 'S', 'N') + magnet(310, 140, 180, 40, 'S', 'N')
    save('c3l1-o04-e-pairs.svg', svg(520, 200, b))

# ───────────────────────── O05 شكل المجال حول سلك مستقيم
def o05():
    # سلك رأسي يخترق لوحًا أفقيًا وحوله أربع بوصلات (بلا إبر)
    b = RECT(255, 160, 10, 110, INK, '#e3a87a', 1.2)
    b += f'<polygon points="60,200 380,200 460,120 140,120" fill="#eef2f8" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<ellipse cx="260" cy="160" rx="5" ry="2.5" fill="#e3a87a"/>' + RECT(255, 20, 10, 140, INK, '#e3a87a', 1.2)
    for x, y in ((165, 160), (355, 160), (300, 134), (220, 186)):
        b += f'<ellipse cx="{x}" cy="{y}" rx="18" ry="9" fill="#f7f4ea" stroke="{INK}" stroke-width="1.5"/>'
    b += ARROW(280, 110, 280, 50, INK, 2) + T(292, 82, 'I', 17, 'start')
    b += T(420, 220, 'لوح كرتون أفقي', 13, color=MUTED)
    save('c3l1-o05-card.svg', svg(500, 280, b))
    # مقطع سلك تيار خارج الصفحة ودوائر مجال ونقطة P
    W, H = 360, 300; cx, cy = 180, 150
    b = ring(cx, cy, 45) + ring(cx, cy, 85) + ring(cx, cy, 125) + wire_dot(cx, cy, 'out')
    b += L(cx, cy, cx + 85 * math.cos(math.radians(-35)), cy + 85 * math.sin(math.radians(-35)), MUTED, 1.4, '5 4')
    b += DOT(cx + 85 * math.cos(math.radians(-35)), cy + 85 * math.sin(math.radians(-35)), 4.5, INK) + T(cx + 85 * math.cos(math.radians(-35)) + 14, cy + 85 * math.sin(math.radians(-35)) - 6, 'P', 16, 'start', weight='bold', italic=True)
    save('c3l1-o05-tangent.svg', svg(W, H, b))
    # مقالي: مقطع سلك تيار خارج الصفحة (لا خطوط)
    b = wire_dot(150, 110, 'out', 22) + T(150, 175, 'التيار خارج من الصفحة', 13, color=MUTED)
    save('c3l1-o05-e-out.svg', svg(300, 200, b))

# ───────────────────────── O06 شدة المجال حول سلك مستقيم
def o06():
    W, H = 520, 200; cx, cy = 80, 100
    b = wire_dot(cx, cy, 'in', 15)
    for k, lab in ((1, 'P'), (2, 'Q'), (3, 'R')):
        x = cx + 130 * k; b += DOT(x, cy, 5, INK) + T(x, cy - 14, lab, 16, weight='bold', italic=True)
    for k, lab in ((1, 'r'), (2, '2r'), (3, '3r')):
        yy = cy + 40 + 22 * (k - 1); x2 = cx + 130 * k
        b += L(cx, yy, x2, yy, MUTED, 1.3) + L(cx, yy - 5, cx, yy + 5, MUTED, 1.3) + L(x2, yy - 5, x2, yy + 5, MUTED, 1.3) + T(x2 + 8, yy + 5, lab, 14, 'start', MUTED, italic=True)
    save('c3l1-o06-points.svg', svg(W, H, b))
    # منحنى B مقابل d
    pts = [(1, 60), (1.5, 40), (2, 30), (3, 20), (4, 15), (6, 10)]
    curve = [(x / 10, 60 / (x / 10)) for x in range(10, 61)]
    graph('c3l1-o06-graph.svg', [{'pts': curve, 'color': FIELD}], (0, 6), (0, 70), 'البعد عن السلك (cm)', 'المجال المغناطيسي (µT)', 1, 10,
          marks=[(x, y, '') for x, y in pts], w=520, h=360)

# ───────────────────────── O07 القاعدة الأولى لليد اليمنى
def o07():
    # سلك رأسي تياره لأعلى وحلقة أفقية (منظور)
    b = RECT(195, 30, 10, 230, INK, '#e3a87a', 1.2) + ARROW(225, 120, 225, 50, INK, 2) + T(236, 88, 'I', 17, 'start')
    b += f'<ellipse cx="200" cy="180" rx="110" ry="34" fill="none" stroke="{FIELD}" stroke-width="2"/>' + RECT(195, 180, 10, 80, INK, '#e3a87a', 1.2)
    b += T(330, 200, 'خط مجال', 13, 'start', MUTED)
    save('c3l1-o07-up.svg', svg(420, 280, b))
    # مقطع سلك تياره داخل الصفحة ونقطة Q على يمينه
    b = wire_dot(150, 130, 'in', 15) + DOT(270, 130, 5, INK) + T(270, 116, 'Q', 16, weight='bold', italic=True) + L(165, 130, 265, 130, MUTED, 1.2, '5 4')
    b += T(150, 175, 'التيار داخل في الصفحة', 13, color=MUTED)
    save('c3l1-o07-q.svg', svg(340, 200, b))
    # منظر علوي: أربع بوصلات حول سلك عمودي على الصفحة، إبرها مماسية مع عقارب الساعة
    W, H = 360, 320; cx, cy = 180, 160; r = 95
    b = wire_dot(cx, cy, None, 14)
    for k in range(4):
        a = math.radians(k * 90)  # 0: يمين، 90: أسفل (شاشة)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        # مع عقارب الساعة على الشاشة: المماس = a + 90° (شاشة) → زاوية رياضية = −(a + 90°)
        b += compass(x, y, -math.degrees(a) - 90, 24)
    save('c3l1-o07-card.svg', svg(W, H, b))
    # مقالي: سلك أفقي في مستوى الصفحة تياره لليمين ونقطتان A فوقه وB تحته
    b = RECT(40, 115, 380, 10, INK, '#e3a87a', 1.2) + ARROW(180, 100, 280, 100, INK, 2) + T(232, 90, 'I', 17)
    b += DOT(230, 45, 5) + T(244, 50, 'A', 16, 'start', weight='bold', italic=True) + DOT(230, 190, 5) + T(244, 195, 'B', 16, 'start', weight='bold', italic=True)
    save('c3l1-o07-e-ab.svg', svg(460, 230, b))

# ───────────────────────── O08 العوامل المؤثرة في مجال الملف
def o08():
    W, H = 600, 210; b = ''
    for k, (lab, n, cur) in enumerate((('A', 5, '2 A'), ('B', 10, '2 A'), ('C', 10, '4 A'))):
        x0 = 30 + k * 195; b += coil(x0, 80, x0 + 150, n, 30)
        b += T(x0 + 75, 30, lab, 17, weight='bold', italic=True)
        b += T(x0 + 75, 145, f'عدد اللفات: {n * 10}', 13) + T(x0 + 75, 170, f'التيار: \u200e{cur}', 13)
    b += T(W / 2, 200, 'الملفات الثلاثة متساوية الطول وبلا قلب حديدي', 12, color=MUTED)
    save('c3l1-o08-coils.svg', svg(W, H, b))

# ───────────────────────── O09 القاعدة الثانية لليد اليمنى
def o09():
    b = coil(120, 110, 360, 8, 40)
    b += f'<path d="M 243 52 A 16 58 0 0 1 243 168" fill="none" stroke="{PURPLE}" stroke-width="2.6"/>' + head(246, 166, math.radians(100), PURPLE, 12)
    b += T(240, 205, 'اتجاه دوران الأصابع', 13, color=PURPLE)
    b += ARROW(240, 30, 400, 30, ORANGE, 3) + T(232, 35, 'اتجاه الإبهام', 13, 'end', ORANGE) + T(420, 116, 'X', 17, weight='bold', italic=True) + T(98, 116, 'Y', 17, weight='bold', italic=True)
    save('c3l1-o09-hand.svg', svg(500, 225, b))

if __name__ == '__main__':
    o01(); o02(); o03(); o04(); o05(); o06(); o07(); o08(); o09()
