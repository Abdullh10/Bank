import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 1-2 القياس (الأهداف O12–O22): أهداف الرماية للدقة والضبط، وأعمدة الخطأ مع القيمة المقبولة،
# والمعايرة بالنقطتين، والانحراف مع الزمن، واختلاف زاوية النظر، والمساطر والتدريجات.

WOOD = '#f6e7c1'; METAL = '#eef1f5'


# ---------- أهداف الرماية ----------
def target_panel(cx, cy, pts, label, R=72):
    b = ''
    for k, (r, fill) in enumerate([(R, '#ffffff'), (R * 0.75, '#e9eef6'), (R * 0.5, '#ffffff'), (R * 0.25, '#e9eef6')]):
        b += f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="{fill}" stroke="{INK}" stroke-width="1.6"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R * 0.1:.1f}" fill="{RED}" stroke="{RED}"/>'
    for (x, y) in pts:  # بوحدات نسبية من نصف القطر
        px, py = cx + x * R, cy - y * R
        b += L(px - 5, py - 5, px + 5, py + 5, INK, 2.6) + L(px - 5, py + 5, px + 5, py - 5, INK, 2.6)
    if label: b += T(cx, cy + R + 24, label, 16, weight='bold')
    return b


CL_C = [(0.04, 0.06), (-0.06, 0.02), (0.02, -0.07), (-0.03, -0.04), (0.07, -0.01)]        # متقاربة حول المركز
CL_OFF = [(0.52, 0.50), (0.60, 0.46), (0.55, 0.58), (0.47, 0.55), (0.58, 0.54)]          # متقاربة بعيدة عن المركز
SC_C = [(0.55, 0.15), (-0.45, 0.40), (-0.20, -0.55), (0.35, -0.45), (-0.55, -0.10)]       # متفرقة حول المركز
SC_OFF = [(0.70, 0.10), (-0.10, 0.75), (0.80, 0.55), (0.25, 0.30), (0.45, 0.85)]          # متفرقة بعيدة عن المركز


def targets(name, sets, labels):
    n = len(sets); cols = 2 if n == 4 else n; rows = (n + cols - 1) // cols
    w, h = cols * 200 + 20, rows * 200 + 10; b = ''
    for k, (pts, lab) in enumerate(zip(sets, labels)):
        cx = 110 + (k % cols) * 200; cy = 90 + (k // cols) * 200
        b += target_panel(cx, cy, pts, lab)
    save(name, svg(w, h, b))


# ---------- أعمدة الخطأ مع القيمة المقبولة ----------
def errbars(name, items, yr, ystep, ylabel, xlabel, accepted=None, acc_label='القيمة المقبولة', w=520, h=360):
    """items = [(اسم, قيمة, خطأ)]؛ accepted يرسم خطًّا أفقيًّا متقطعًا."""
    n = len(items)
    args = ([], (0, n + 1), yr, xlabel, ylabel, 1, ystep, w, h)
    X, Y = graph(name, *args)
    b = ''
    if accepted is not None:
        b += L(X(0), Y(accepted), X(n + 1), Y(accepted), GREEN, 2.2, '8 5') + T(X(0) + 6, Y(accepted) - 8, acc_label, 13, 'start', GREEN, 'bold')
    for k, (lab, v, e) in enumerate(items):
        x = X(k + 1)
        b += L(x, Y(v - e), x, Y(v + e), RED, 2.4) + L(x - 12, Y(v - e), x + 12, Y(v - e), RED, 2.4) + L(x - 12, Y(v + e), x + 12, Y(v + e), RED, 2.4)
        b += L(x - 18, Y(v), x + 18, Y(v), INK, 2.6)
        b += T(x, Y(yr[0]) + 38, lab, 14, weight='bold', color=INK) if False else ''
    # تسميات الأعمدة بدل أرقام المحور الأفقي: نغطي الأرقام بمستطيل أبيض ونكتب الأسماء
    b += f'<rect x="{X(0) - 8}" y="{Y(yr[0]) + 6}" width="{X(n + 1) - X(0) + 16}" height="20" fill="#fff"/>'
    for k, (lab, v, e) in enumerate(items): b += T(X(k + 1), Y(yr[0]) + 21, lab, 14, weight='bold')
    graph(name, *args, extra=b)


# ---------- ميزان رقمي ----------
def balance(cx, base_y, reading, mass_label=None, caption=None):
    b = ''
    b += f'<rect x="{cx - 95}" y="{base_y - 70}" width="190" height="70" rx="10" fill="{METAL}" stroke="{INK}" stroke-width="2"/>'
    b += f'<rect x="{cx - 62}" y="{base_y - 52}" width="124" height="34" rx="4" fill="#dfe9d8" stroke="{INK}" stroke-width="1.5"/>'
    b += T(cx, base_y - 28, reading, 20, color=INK, weight='bold')
    b += f'<rect x="{cx - 80}" y="{base_y - 84}" width="160" height="10" rx="3" fill="#d7dce4" stroke="{INK}" stroke-width="1.6"/>'
    b += L(cx, base_y - 74, cx, base_y - 70, INK, 4)
    if mass_label:
        b += f'<rect x="{cx - 26}" y="{base_y - 140}" width="52" height="56" rx="6" fill="#d9b44a" stroke="{INK}" stroke-width="1.8"/>'
        b += f'<rect x="{cx - 12}" y="{base_y - 154}" width="24" height="14" rx="3" fill="#d9b44a" stroke="{INK}" stroke-width="1.5"/>'
        b += T(cx, base_y - 106, mass_label, 13, weight='bold')
    if caption: b += T(cx, base_y + 26, caption, 14, color=MUTED)
    return b


# ---------- اختلاف زاوية النظر ----------
EYE_COL = '#3b4a63'


def eye(x, y, toward):
    """عين بسيطة تنظر نحو النقطة toward."""
    a = math.degrees(math.atan2(toward[1] - y, toward[0] - x))
    return (f'<g transform="rotate({a:.1f} {x:.1f} {y:.1f})"><path d="M {x - 16:.1f} {y:.1f} Q {x:.1f} {y - 12:.1f} {x + 16:.1f} {y:.1f} Q {x:.1f} {y + 12:.1f} {x - 16:.1f} {y:.1f} Z" fill="#fff" stroke="{EYE_COL}" stroke-width="2"/>'
            f'<circle cx="{x + 4:.1f}" cy="{y:.1f}" r="5" fill="{EYE_COL}"/></g>')


def parallax(name, eyes, pointer=3.0, lo=1, hi=5, gap=46, lines=True, w=620, h=380, note='منظر جانبي: مؤشر مثبّت فوق تدريج بالسنتيمتر'):
    """منظر جانبي: تدريج أفقي (cm) ومؤشر فوقه بمسافة gap؛ eyes = [(x بوحدات التدريج, ارتفاع px فوق المؤشر, تسمية)]."""
    ppc = 100; x0 = 60 - (lo - 0.5) * ppc + 0; sy = h - 80
    X = lambda v: 60 + (v - (lo - 0.5)) * ppc
    b = f'<rect x="{X(lo - 0.5):.1f}" y="{sy}" width="{(hi - lo + 1) * ppc}" height="34" fill="{WOOD}" stroke="{INK}" stroke-width="2"/>'
    v = lo - 0.5; k = 0
    while v <= hi + 0.5 + 1e-9:
        major = abs(v - round(v)) < 1e-9; half = abs(v * 2 - round(v * 2)) < 1e-9
        ln = 16 if major else (11 if half else 7)
        b += L(X(v), sy, X(v), sy + ln, INK, 1.6 if major else 1.1)
        if major: b += T(X(v), sy + 30, fmt(round(v)), 14)
        v = round(v + 0.1, 6)
    b += T(X(hi + 0.5) + 6, sy + 24, 'cm', 14, 'start', MUTED)
    tip = (X(pointer), sy - gap)
    b += L(tip[0], sy - gap - 70, tip[0], sy - gap, INK, 3) + f'<polygon points="{tip[0] - 6},{tip[1] - 10} {tip[0] + 6},{tip[1] - 10} {tip[0]},{tip[1] + 2}" fill="{INK}"/>'
    for (ex, eh, lab) in eyes:
        e = (X(ex), tip[1] - eh)
        if lines:
            # امتداد خط النظر من العين عبر طرف المؤشر حتى التدريج
            t = (sy - e[1]) / (tip[1] - e[1]); hx = e[0] + t * (tip[0] - e[0])
            b += L(e[0], e[1], hx, sy, MUTED, 1.5, '6 5')
        b += eye(e[0], e[1], tip)
        if lab: b += T(e[0] + (0 if abs(ex - pointer) < 0.05 else (-26 if ex < pointer else 26)), e[1] - 20, lab, 16, weight='bold', color=BLUE)
    if note: b += T(w / 2, 22, note, 14, color=MUTED)
    save(name, svg(w, h, b))


# ---------- مسطرة ----------
def ruler(name, lo, hi, minor, ppc=100, obj=None, zero_offset=0.0, edge_len=None, w=None, label_every=1, note=None, h=200, obj_label=None):
    """مسطرة بالسنتيمتر: تدريج أصغر minor (0.1 أو 0.5). obj = (بداية, نهاية) بوحدات التدريج يُرسم قلمًا فوقها.
    zero_offset: المسافة بين حافة المسطرة وصفرها (cm)، تُرسم الحافة قبل الصفر."""
    left = 40; X = lambda v: left + (zero_offset + v - lo) * ppc
    W = w or int(X(hi) + 70); ry = 110
    rx0 = left - (14 if zero_offset == 0 else 0); rx1 = X(hi) + 44
    b = f'<rect x="{rx0}" y="{ry}" width="{rx1 - rx0:.1f}" height="56" fill="{WOOD}" stroke="{INK}" stroke-width="2"/>'
    n = round((hi - lo) / minor)
    for i in range(n + 1):
        v = round(lo + i * minor, 6)
        major = abs(v - round(v)) < 1e-9; half = abs(v * 2 - round(v * 2)) < 1e-9
        ln = 22 if major else (15 if half else 9)
        b += L(X(v), ry, X(v), ry + ln, INK, 1.6 if major else 1.1)
        if major and round(v) % label_every == 0: b += T(X(v), ry + 40, fmt(round(v)), 15)
    b += T(rx1 - 6, ry + 50, 'cm', 13, 'end', MUTED)
    if obj:
        a, z = obj; y0 = ry - 34
        x1, x2 = X(a) if zero_offset == 0 or a != 'edge' else rx0, X(z)
        if obj[0] == 'edge': x1 = rx0
        tipw = 26
        b += f'<rect x="{x1:.1f}" y="{y0}" width="{x2 - x1 - tipw:.1f}" height="24" fill="#f2c94c" stroke="{INK}" stroke-width="1.8"/>'
        b += f'<polygon points="{x2 - tipw:.1f},{y0} {x2:.1f},{y0 + 12} {x2 - tipw:.1f},{y0 + 24}" fill="#f5deb3" stroke="{INK}" stroke-width="1.8"/>'
        b += L(x2, y0 + 12, x2, ry, MUTED, 1, '3 3') + L(x1, y0, x1, ry, MUTED, 1, '3 3')
        if obj_label: b += T((x1 + x2) / 2, y0 - 12, obj_label, 14)
    if note: b += T(W / 2, 24, note, 14, color=MUTED)
    save(name, svg(W, h, b))


# ---------- عداد بمؤشر (أميتر) ----------
def dial(name, lo, hi, minor, value, unit='A', w=460, h=300):
    cx, cy, R = w / 2, h - 50, 190; a0, a1 = 140, 40
    ang = lambda v: math.radians(a0 + (v - lo) / (hi - lo) * (a1 - a0))
    b = f'<rect x="10" y="10" width="{w - 20}" height="{h - 20}" rx="12" fill="{METAL}" stroke="{INK}" stroke-width="2"/>'
    b += f'<path d="M {cx + R * math.cos(math.radians(a0)):.1f} {cy - R * math.sin(math.radians(a0)):.1f} A {R} {R} 0 0 1 {cx + R * math.cos(math.radians(a1)):.1f} {cy - R * math.sin(math.radians(a1)):.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
    n = round((hi - lo) / minor)
    for i in range(n + 1):
        v = round(lo + i * minor, 6); t = ang(v); major = abs(v - round(v)) < 1e-9; half = abs(v * 2 - round(v * 2)) < 1e-9
        ln = 20 if major else (14 if half else 9)
        b += L(cx + R * math.cos(t), cy - R * math.sin(t), cx + (R - ln) * math.cos(t), cy - (R - ln) * math.sin(t), INK, 1.8 if major else 1.2)
        if major: b += T(cx + (R + 16) * math.cos(t), cy - (R + 16) * math.sin(t) + 5, fmt(round(v)), 15)
    t = ang(value)
    b += L(cx, cy, cx + (R - 6) * math.cos(t), cy - (R - 6) * math.sin(t), RED, 2.5) + DOT(cx, cy, 9, INK)
    b += T(cx, cy - 60, unit, 22, weight='bold')
    save(name, svg(w, h, b))


# ---------- ميزان نابضي رأسي ----------
def spring_scale(name, hi, minor, value, unit='N', w=260, h=440):
    top, bot = 60, 380; Y = lambda v: top + v / hi * (bot - top); cx = w / 2
    b = f'<rect x="{cx - 70}" y="{top - 40}" width="140" height="{bot - top + 80}" rx="14" fill="{METAL}" stroke="{INK}" stroke-width="2"/>'
    b += L(cx, 4, cx, top - 40, INK, 3) + T(cx + 40, top - 14, unit, 16, weight='bold')
    n = round(hi / minor)
    for i in range(n + 1):
        v = round(i * minor, 6); major = abs(v - round(v)) < 1e-9
        ln = 22 if major else 13
        b += L(cx - 10, Y(v), cx - 10 + ln, Y(v), INK, 1.6 if major else 1.1)
        if major: b += T(cx - 18, Y(v) + 5, fmt(round(v)), 14, 'end')
    b += f'<rect x="{cx - 8}" y="{top - 20}" width="6" height="{Y(value) - top + 20:.1f}" fill="#9aa5b5"/>'
    b += f'<polygon points="{cx - 14},{Y(value):.1f} {cx + 18},{Y(value) - 5:.1f} {cx + 18},{Y(value) + 5:.1f}" fill="{RED}"/>'
    b += L(cx - 5, bot + 40, cx - 5, h - 10, INK, 3) + f'<path d="M {cx - 15} {h - 18} Q {cx - 5} {h - 2} {cx + 5} {h - 18}" fill="none" stroke="{INK}" stroke-width="3"/>'
    save(name, svg(w, h, b))


if __name__ == '__main__':
    # O19 / O12: أربعة أهداف
    targets('c1l2-tgt-four.svg', [SC_OFF, CL_OFF, SC_C, CL_C], ['الهدف 1', 'الهدف 2', 'الهدف 3', 'الهدف 4'])
    targets('c1l2-tgt-order.svg', [CL_OFF, CL_C, SC_OFF, SC_C], ['الهدف 1', 'الهدف 2', 'الهدف 3', 'الهدف 4'])
    targets('c1l2-tgt-single.svg', [CL_OFF], [''])
    targets('c1l2-tgt-scatter.svg', [SC_C], [''])
    # O17: مجموعات تقيس g مع القيمة المقبولة
    errbars('c1l2-eb-g.svg', [('A', 9.62, 0.03), ('B', 9.79, 0.04), ('C', 9.92, 0.02), ('D', 9.70, 0.25)], (9.4, 10.1), 0.1,
            'g (m/s²)', 'المجموعة', accepted=9.80)
    # O19: زمن دورة بندول، القيمة المقبولة 2.00 s
    errbars('c1l2-eb-pend.svg', [('A', 2.10, 0.01), ('B', 1.99, 0.08), ('C', 2.01, 0.02)], (1.80, 2.20), 0.05,
            'زمن الدورة (s)', 'الطالب', accepted=2.00)
    # O12: نتائج أربعة طلاب لكتلة مقبولة 50.0 g
    errbars('c1l2-eb-mass.svg', [('A', 48.6, 0.2), ('B', 50.1, 0.2), ('C', 51.2, 0.2), ('D', 49.0, 0.2)], (47.5, 52.0), 0.5,
            'الكتلة (g)', 'الطالب', accepted=50.0)
    # O14: المعايرة بالنقطتين
    b = balance(150, 230, '0.0 g', caption='الخطوة الأولى: الكفة فارغة') + balance(430, 230, '200.0 g', '200.0 g', caption='الخطوة الثانية: كتلة معيارية')
    save('c1l2-cal-steps.svg', svg(580, 280, b))
    save('c1l2-cal-zero.svg', svg(300, 280, balance(150, 230, '2.5 g', caption='الكفة فارغة')))
    save('c1l2-cal-std.svg', svg(300, 280, balance(150, 230, '497.0 g', '500.0 g', caption='كتلة معيارية')))
    save('c1l2-cal-o12.svg', svg(580, 280, balance(150, 230, '100.0 g', '100.0 g', caption='الميزان 1') + balance(430, 230, '103.4 g', '100.0 g', caption='الميزان 2')))
    # O15: انحراف قراءة الميزان لكتلة معيارية 100.0 g مع الزمن
    graph('c1l2-cal-drift.svg', [{'pts': [(0, 100.0), (1, 100.4), (2, 100.9), (3, 101.3), (4, 101.8)], 'color': BLUE, 'dots': True},
                                 {'pts': [(0, 100.0), (4, 100.0)], 'color': GREEN, 'dash': '8 5', 'w': 2, 'label': 'القيمة المعتمدة', 'at': (2.4, 100.0), 'dy': 20}],
          (0, 4), (99.5, 102.0), 'الزمن منذ آخر معايرة (شهر)', 'قراءة الميزان (g)', 1, 0.5)
    # O18 / O16: اختلاف زاوية النظر
    parallax('c1l2-plx-eyes.svg', [(2.0, 115, '1'), (3.0, 140, '2'), (4.0, 115, '3')])
    parallax('c1l2-plx-left.svg', [(2.0, 115, '')])
    parallax('c1l2-plx-o16.svg', [(3.0, 140, '1'), (4.0, 115, '2')])
    # O17 / O16: مسطرة صفرها بعد حافتها بـ 0.5 cm
    ruler('c1l2-rul-edge.svg', 0, 6, 0.5, ppc=80, obj=('edge', 4.0), zero_offset=0.5, h=190)
    # O20: مساطر للتعبير عن نتيجة القياس مع خطئه
    ruler('c1l2-rul-mm.svg', 0, 5, 0.1, ppc=100, obj=(0, 3.65), h=190)
    ruler('c1l2-rul-half.svg', 0, 6, 0.5, ppc=80, obj=(0, 3.5), h=190)
    ruler('c1l2-rul-mm2.svg', 0, 5, 0.1, ppc=100, obj=(0, 4.25), h=190)
    dial('c1l2-dial-amm.svg', 0, 5, 0.2, 3.6)
    spring_scale('c1l2-spring-n.svg', 5, 0.5, 3.5)
