# رسوم الدرس 3-1 (ب): الطبيعة الديناميكية للاتزان، ومنحنيات التركيز مع الزمن، وثبات Keq، وحذف المواد الصلبة والسوائل النقية.
# التشغيل: python3 data/chem22/gen/figs/C3-L1-b.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
import re, math, random

PURPLE = '#6b3fa0'; ORANGE = '#c26a12'; GREY = '#8a94a3'

def ylab(x, y, s, size=14):
    rtl = ' direction="rtl"' if re.search('[؀-ۿ]', s) else ''
    return f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="bold" {FONT}{rtl}>{esc(s)}</text>'

def approach(c0, cf, k):
    return lambda t: cf + (c0 - cf) * math.exp(-k * t)

def graph_panel(ox, oy, w, h, series, xmax, ymax, xlabel='الزمن', ylabel='التركيز (mol/L)', yticks=(), tick_fmt=str,
                tmarks=(), title=None, label_dx=22):
    """لوحة منحنيات (تركيز أو سرعة) مع الزمن تعيد نص SVG. series = [dict(f, color, label, dy, dash)]،
    tmarks = [(t, 'نص')]: خطوط رأسية متقطعة عند أزمنة محددة."""
    X0, Y0 = ox + (78 if yticks else 50), oy + h - 45
    X1, Y1 = ox + w - 84, oy + (40 if title else 18)
    px = lambda t: X0 + t / xmax * (X1 - X0)
    py = lambda c: Y0 - c / ymax * (Y0 - Y1)
    b = ''
    for t in yticks: b += L(X0, py(t), X1, py(t), '#e6e9ef', 1)
    b += ARROW(X0, Y0, X1 + 14, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    for t in yticks: b += L(X0 - 5, py(t), X0, py(t)) + T(X0 - 8, py(t) + 5, tick_fmt(t), 12, 'end')
    if yticks: b += T(X0 - 8, Y0 + 5, '0', 12, 'end')
    b += T((X0 + X1) / 2, oy + h - 12, xlabel, 14, weight='bold')
    b += ylab(ox + (20 if yticks else 22), (Y0 + Y1) / 2, ylabel)
    for t, lab in tmarks:
        b += L(px(t), Y0, px(t), Y1, MUTED, 1.3, '5 4') + T(px(t), Y0 + 18, lab, 14, weight='bold', color=MUTED)
    for s in series:
        pts = [(xmax * i / 240, s['f'](xmax * i / 240)) for i in range(241)]
        da = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
        b += f'<polyline points="{" ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in pts)}" fill="none" stroke="{s["color"]}" stroke-width="3" stroke-linejoin="round"{da}/>'
        if s.get('label'):
            b += T(X1 + label_dx, py(pts[-1][1]) + 5 + s.get('dy', 0), s['label'], 14, 'start', s['color'], 'bold')
    if title: b += T(ox + w / 2, oy + 22, title, 15, weight='bold')
    return b

def conc_graph(name, series, xmax, ymax, w=540, h=330, **kw):
    save(name, svg(w, h, graph_panel(0, 0, w, h, series, xmax, ymax, **kw)))

# ---------- جسيمات ----------
def dot(x, y, col, r=6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" stroke="{INK}" stroke-width="1"/>'

def scatter(rng, n, inside, r=7, taken=None):
    """نقاط عشوائية غير متداخلة داخل منطقة تحددها الدالة inside(x, y) ضمن مستطيل مرفق."""
    pts = taken if taken is not None else []
    out = []
    box = inside.box
    tries = 0
    while len(out) < n and tries < 20000:
        tries += 1
        x = rng.uniform(box[0], box[2]); y = rng.uniform(box[1], box[3])
        if not inside(x, y): continue
        if any((x - a) ** 2 + (y - b) ** 2 < (2.3 * r) ** 2 for a, b in pts): continue
        pts.append((x, y)); out.append((x, y))
    return out

def region(box, f):
    f.box = box; return f

def flask(cx, cy, R, gas, solid, seed, valve_side=None):
    """دورق كروي: gas وsolid قوائم ألوان الجسيمات في الحالة الغازية والصلبة."""
    rng = random.Random(seed)
    b = f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#f7f9fc" stroke="{INK}" stroke-width="2.5"/>'
    # الطبقة الصلبة: قطعة دائرية في الأسفل
    hs = R * 0.5; yc = cy + R - hs
    half = math.sqrt(R * R - (yc - cy) ** 2)
    b += f'<path d="M {cx - half:.1f} {yc:.1f} A {R} {R} 0 0 0 {cx + half:.1f} {yc:.1f} Z" fill="#e3ddd2" stroke="none"/>'
    b += L(cx - half, yc, cx + half, yc, MUTED, 1.2)
    taken = []
    sol = region((cx - R, yc + 4, cx + R, cy + R - 4), lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < (R - 8) ** 2 and y > yc + 7)
    gasr = region((cx - R, cy - R, cx + R, yc - 6), lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < (R - 9) ** 2 and y < yc - 8)
    sp = scatter(rng, len(solid), sol, 5.2, taken)
    gp = scatter(rng, len(gas), gasr, 7.5, taken)
    for (x, y), c in zip(sp, solid): b += dot(x, y, c, 5.5)
    for (x, y), c in zip(gp, gas): b += dot(x, y, c, 5.5)
    return b

def iodine_flasks(name, w=600, h=430):
    R = 70
    def pair(oy, open_, tag, seed):
        b = T(30, oy + 20, tag, 16, weight='bold')
        lx, rx, cy = 175, 425, oy + 100
        # الأنبوب والمحبس
        b += f'<rect x="{lx + R - 4}" y="{cy - 9}" width="{rx - lx - 2 * R + 8}" height="18" fill="#f7f9fc" stroke="{INK}" stroke-width="2"/>'
        vx = (lx + rx) / 2
        b += f'<rect x="{vx - 14}" y="{cy - 20}" width="28" height="40" rx="5" fill="{"#d9efe2" if open_ else "#f3d6d2"}" stroke="{INK}" stroke-width="2"/>'
        b += L(vx - 10, cy, vx + 10, cy, INK, 3) if open_ else L(vx, cy - 14, vx, cy + 14, INK, 3)
        b += T(vx, cy - 28, 'المحبس مفتوح' if open_ else 'المحبس مغلق', 13, color=GREEN if open_ else RED, weight='bold')
        if open_:
            gl = [GREY] * 5 + [RED] * 3; sl = [GREY] * 10 + [RED] * 5
            gr = [RED] * 5 + [GREY] * 3; sr = [RED] * 10 + [GREY] * 5
            readl = readr = 'عداد الإشعاع: إشعاع'
        else:
            gl, sl, gr, sr = [GREY] * 8, [GREY] * 15, [RED] * 8, [RED] * 15
            readl, readr = 'عداد الإشعاع: لا إشعاع', 'عداد الإشعاع: إشعاع'
        b += flask(lx, cy, R, gl, sl, seed) + flask(rx, cy, R, gr, sr, seed + 7)
        b += T(lx, cy + R + 22, readl, 13, color=MUTED) + T(rx, cy + R + 22, readr, 13, color=MUTED)
        return b
    b = pair(0, False, '(أ)', 3) + L(20, 205, w - 20, 205, '#d0d5dd', 1, '5 5') + pair(205, True, '(ب)', 11)
    b += dot(470, h - 14, GREY) + T(458, h - 9, 'I-127', 14, 'end') + T(410, h - 9, 'يود غير مشع', 14, 'end')
    b += dot(230, h - 14, RED) + T(218, h - 9, 'I-131', 14, 'end') + T(170, h - 9, 'يود مشع', 14, 'end')
    save(name, svg(w, h + 2, b))

# ---------- الإيثانول في دورق مغلق ----------
def ethanol_flask(name, w=440, h=330):
    rng = random.Random(5)
    cx, cy, R = 180, 200, 105
    b = f'<rect x="{cx - 22}" y="{cy - R - 70}" width="44" height="78" fill="#f7f9fc" stroke="{INK}" stroke-width="2.5"/>'
    b += f'<rect x="{cx - 28}" y="{cy - R - 92}" width="56" height="26" rx="4" fill="#a7774a" stroke="{INK}" stroke-width="2"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#f7f9fc" stroke="{INK}" stroke-width="2.5"/>'
    b += f'<rect x="{cx - 20.5}" y="{cy - R - 6}" width="41" height="14" fill="#f7f9fc"/>'
    yl = cy + 30; half = math.sqrt(R * R - (yl - cy) ** 2)
    b += f'<path d="M {cx - half:.1f} {yl} A {R} {R} 0 0 0 {cx + half:.1f} {yl} Z" fill="#cfe3f5"/>' + L(cx - half, yl, cx + half, yl, BLUE, 2)
    gas = region((cx - R, cy - R - 60, cx + R, yl - 8), lambda x, y: ((x - cx) ** 2 + (y - cy) ** 2 < (R - 10) ** 2 or abs(x - cx) < 12) and y < yl - 10)
    taken = []
    for x, y in scatter(rng, 9, gas, 8, taken): b += dot(x, y, ORANGE, 6)
    liq = region((cx - R, yl + 6, cx + R, cy + R), lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < (R - 10) ** 2 and y > yl + 9)
    for x, y in scatter(rng, 22, liq, 6.5, taken): b += dot(x, y, ORANGE, 5)
    b += ARROW(cx - 40, yl + 14, cx - 40, yl - 30, GREEN, 2.2) + ARROW(cx + 40, yl - 30, cx + 40, yl + 14, RED, 2.2)
    b += T(305, 95, 'C₂H₅OH(g)', 15, 'start', weight='bold') + L(300, 92, cx + 45, 120, MUTED, 1)
    b += T(305, 268, 'C₂H₅OH(l)', 15, 'start', weight='bold') + L(300, 263, cx + 70, 255, MUTED, 1)
    b += T(cx - 48, yl - 4, 'تبخر', 14, 'end', GREEN, 'bold') + T(cx + 48, yl - 4, 'تكثف', 14, 'start', RED, 'bold')
    save(name, svg(w, h, b))

# ---------- حاويتان مغلقتان فيهما كمية مختلفة من مادة صلبة ----------
def solid_boxes(name, items, gas_col, solid_col, legend, w=560, h=300, seed=2):
    """items = [(tag, n_gas, n_solid_rows)] حاويات متساوية الحجم عند درجة الحرارة نفسها."""
    rng = random.Random(seed)
    bw, bh, gap = 200, 200, 60
    x0 = (w - (len(items) * bw + (len(items) - 1) * gap)) / 2
    b = ''
    for k, (tag, ng, rows) in enumerate(items):
        x = x0 + k * (bw + gap); y = 40
        b += T(x + bw / 2, 26, tag, 16, weight='bold')
        b += f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="#f7f9fc" stroke="{INK}" stroke-width="2.5"/>'
        # الطبقة الصلبة: صفوف متراصة
        for r in range(rows):
            for c in range(14):
                b += f'<circle cx="{x + 9 + c * 14 + (7 if r % 2 else 0):.1f}" cy="{y + bh - 9 - r * 12:.1f}" r="6" fill="{solid_col}" stroke="{INK}" stroke-width="0.8"/>' if 9 + c * 14 + (7 if r % 2 else 0) < bw - 6 else ''
        top = y + bh - 9 - rows * 12
        reg = region((x + 10, y + 10, x + bw - 10, top - 6), lambda a, c_: True)
        for a, c_ in scatter(rng, ng, reg, 9, []): b += dot(a, c_, gas_col, 6.5)
    b += dot(w / 2 - 90, h - 22, gas_col, 6.5) + T(w / 2 - 78, h - 17, 'I₂(g)', 14, 'start')
    b += f'<circle cx="{w / 2 + 40}" cy="{h - 22}" r="6" fill="{solid_col}" stroke="{INK}" stroke-width="0.8"/><circle cx="{w / 2 + 52}" cy="{h - 22}" r="6" fill="{solid_col}" stroke="{INK}" stroke-width="0.8"/>' + T(w / 2 + 64, h - 17, 'I₂(s)', 14, 'start')
    save(name, svg(w, h, b))

# ---------- صناديق جسيمات A₂ + B₂ ⇌ 2AB ----------
def mol(x, y, cols, r=7):
    if len(cols) == 1: return dot(x, y, cols[0], r)
    return dot(x - r * 0.7, y, cols[0], r) + dot(x + r * 0.7, y, cols[1], r)

def ab_boxes(name, boxes, w=640, h=300):
    """boxes = [(tag, nA2, nB2, nAB)]"""
    A, B = BLUE, '#e0a526'
    bw, bh = 180, 190; gap = (w - len(boxes) * bw) / (len(boxes) + 1)
    b = ''
    for k, (tag, na, nb, nab) in enumerate(boxes):
        rng = random.Random(10 + k)
        x = gap + k * (bw + gap); y = 38
        b += T(x + bw / 2, 26, tag, 16, weight='bold')
        b += f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="#f7f9fc" stroke="{INK}" stroke-width="2.5"/>'
        reg = region((x + 18, y + 16, x + bw - 18, y + bh - 16), lambda a, c: True)
        pts = scatter(rng, na + nb + nab, reg, 13, [])
        kinds = [(A, A)] * na + [(B, B)] * nb + [(A, B)] * nab
        rng.shuffle(kinds)
        for (px_, py_), kd in zip(pts, kinds): b += mol(px_, py_, kd)
    ly = h - 30
    b += mol(130, ly, (A, A)) + T(146, ly + 5, 'A₂', 14, 'start')
    b += mol(300, ly, (B, B)) + T(316, ly + 5, 'B₂', 14, 'start')
    b += mol(470, ly, (A, B)) + T(486, ly + 5, 'AB', 14, 'start')
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    k = 0.11
    # 1) تجربة نظيري اليود: (أ) قبل فتح المحبس، (ب) بعد فتحه بمدة
    iodine_flasks('c3-l1b-iodine-flasks.svg')
    # 2) سرعتا التفاعلين الأمامي والعكسي مع الزمن تتساويان عند t₁
    conc_graph('c3-l1b-rates.svg',
               [dict(f=approach(9.0, 3.6, 0.12), color=BLUE, label='الأمامي', dy=-12),
                dict(f=approach(0.0, 3.6, 0.12), color=RED, label='العكسي', dy=12)],
               60, 10, ylabel='سرعة التفاعل', tmarks=[(38, 't₁')])
    # 3) N₂ + 3H₂ ⇌ 2NH₃ بتراكيز مرقمة: N₂ 1.00→0.60، H₂ 3.00→1.80، NH₃ 0→0.80
    conc_graph('c3-l1b-nh3-conc.svg',
               [dict(f=approach(3.0, 1.8, k), color=BLUE, label='H₂'),
                dict(f=approach(1.0, 0.6, k), color=RED, label='N₂', dy=6),
                dict(f=approach(0.0, 0.8, k), color=PURPLE, label='NH₃', dy=-4)],
               60, 3.2, yticks=[0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2], tick_fmt=lambda v: f'{v:.1f}', tmarks=[(40, 't₁')])
    # 4) N₂O₄ ⇌ 2NO₂ بلا أسماء: (س) من 0.0500 إلى 0.0185، (ص) من 0 إلى 0.0630
    conc_graph('c3-l1b-xy-n2o4.svg',
               [dict(f=approach(0.0500, 0.0185, k), color=BLUE, label='(س)'),
                dict(f=approach(0.0, 0.0630, k), color=RED, label='(ص)')],
               60, 0.07, yticks=[0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07], tick_fmt=lambda v: f'{v:.2f}')
    # 5) تقاطع المنحنيين عند t₁ ثم ثبات التراكيز بعد t₂
    conc_graph('c3-l1b-crossing.svg',
               [dict(f=approach(1.0, 0.25, 0.10), color=BLUE, label='المتفاعل'),
                dict(f=approach(0.0, 0.75, 0.10), color=RED, label='الناتج')],
               60, 1.1, tmarks=[(math.log(3) / 0.10, 't₁'), (42, 't₂')])
    # 6) لوحتان: (أ) تفاعل يكتمل، (ب) تفاعل يصل إلى الاتزان
    b = graph_panel(340, 0, 330, 300, [dict(f=approach(1.0, 0.0, 0.11), color=BLUE, label='المتفاعل'),
                                     dict(f=approach(0.0, 1.0, 0.11), color=RED, label='الناتج')], 60, 1.15, title='(أ)')
    b += graph_panel(0, 0, 330, 300, [dict(f=approach(1.0, 0.35, 0.11), color=BLUE, label='المتفاعل'),
                                        dict(f=approach(0.0, 0.65, 0.11), color=RED, label='الناتج')], 60, 1.15, title='(ب)')
    save('c3-l1b-complete-vs-eq.svg', svg(670, 300, b + L(335, 10, 335, 290, '#d0d5dd', 1, '5 5')))
    # 7) الاختبار المقنن: A يتناقص، وB وC يتزايدان (بلا أرقام)
    conc_graph('c3-l1b-abc.svg',
               [dict(f=approach(1.0, 0.18, 0.12), color=BLUE, label='A'),
                dict(f=approach(0.0, 0.82, 0.12), color=GREEN, label='C'),
                dict(f=approach(0.0, 0.41, 0.12), color=RED, label='B')],
               60, 1.1)
    # 8) H₂ + I₂ ⇌ 2HI عند 731 K: محاولتان بتراكيز ابتدائية مختلفة (الجدول 3-1)
    fmt2 = lambda v: f'{v:.1f}'
    yt = [1, 2, 3, 4, 5]
    b = graph_panel(350, 0, 340, 330, [dict(f=approach(2.0, 1.0659, k), color=PURPLE, label='I₂', dy=-8),
                                     dict(f=approach(0.0, 1.8682, k), color=RED, label='HI', dy=-6),
                                     dict(f=approach(1.0, 0.06587, k), color=BLUE, label='H₂', dy=2)],
                    60, 5.5, yticks=yt, tick_fmt=str, title='المحاولة 1')
    b += graph_panel(0, 0, 340, 330, [dict(f=approach(5.0, 3.8950, k), color=RED, label='HI'),
                                        dict(f=approach(0.0, 0.5525, k), color=BLUE, label='H₂, I₂')],
                     60, 5.5, yticks=yt, tick_fmt=str, title='المحاولة 2')
    save('c3-l1b-hi-trials.svg', svg(690, 330, b + L(345, 10, 345, 320, '#d0d5dd', 1, '5 5')))
    # 9) A₂ + B₂ ⇌ 2AB في ثلاث حاويات متساوية الحجم عند درجة الحرارة نفسها
    ab_boxes('c3-l1b-ab-boxes.svg', [('(1)', 2, 2, 4), ('(2)', 1, 4, 4), ('(3)', 3, 3, 2)])
    # 10) الإيثانول السائل وبخاره في دورق مغلق
    ethanol_flask('c3-l1b-ethanol-flask.svg')
    # 11) حاويتان فيهما كميتان مختلفتان من اليود الصلب، وعدد جزيئات I₂(g) نفسه
    solid_boxes('c3-l1b-iodine-amounts.svg', [('(1)', 6, 7), ('(2)', 6, 2)], PURPLE, '#4a3566',
                'الحاويتان متساويتان في الحجم ودرجة الحرارة؛ الدوائر المتراصة في القاع: I₂(s)، والدوائر المتفرقة: جزيئات I₂(g)')
