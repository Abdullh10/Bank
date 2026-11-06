# رسوم الدرس 3-3 (ب): ثابت حاصل الذائبية، الذائبية، خلط المحاليل، الأيون المشترك، الفلوريد والأسنان.
# التشغيل: python3 data/chem22/gen/figs/C3-L3-b.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
import math, random, re

LIQ = '#dcebf7'; LIQ_EDGE = '#9cc3e4'; GLASS = '#5b6676'

def ylabel(x, y, s, size=14):
    rtl = ' direction="rtl"' if re.search('[؀-ۿ]', s) else ''
    return f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="bold" {FONT}{rtl}>{esc(s)}</text>'

def pow10(x, y, e, size=13):
    """تسمية 10 مرفوعة لأس (بإزاحة خط الأساس بدل الأرقام العلوية)."""
    return (f'<text x="{x}" y="{y}" text-anchor="end" font-size="{size}" fill="{INK}" {FONT}>10'
            f'<tspan dy="-6" font-size="{size - 3}">{str(e).replace("-", "−")}</tspan></text>')

def beaker(x, y, w, h, fill=0.8):
    """كأس زجاجية: (x, y) الزاوية العليا اليسرى، ومستوى السائل fill من الارتفاع."""
    ly = y + h * (1 - fill)
    b = f'<rect x="{x + 3}" y="{ly:.1f}" width="{w - 6}" height="{y + h - ly - 3:.1f}" fill="{LIQ}" stroke="{LIQ_EDGE}" stroke-width="1"/>'
    b += f'<path d="M{x - 6},{y} L{x},{y + 6} L{x},{y + h - 8} Q{x},{y + h} {x + 8},{y + h} L{x + w - 8},{y + h} Q{x + w},{y + h} {x + w},{y + h - 8} L{x + w},{y + 6} L{x + w + 6},{y}" fill="none" stroke="{GLASS}" stroke-width="3" stroke-linejoin="round"/>'
    return b, ly

def ion(cx, cy, label, color, r=17):
    if len(label) > 4: r = 21
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="#fff" stroke="{color}" stroke-width="2.2"/>'
            + T(cx, cy + 4.5, label, 12 if len(label) <= 4 else 11, color=color, weight='bold'))

def sat_beaker(name, solid_label, ions, caption=None, title=None, w=520, h=330, seed=3, solid_color='#e9c46a'):
    """محلول مشبع فوق مادة صلبة غير مذابة. ions = [(رمز الأيون، العدد، اللون)]. يُرسم وسيلة إيضاح على اليمين."""
    random.seed(seed)
    bx, by, bw, bh = 40, 50 if title else 30, 270, 240
    b, ly = beaker(bx, by, bw, bh, 0.82)
    # المادة الصلبة في القاع
    base = by + bh - 4
    pts = [(bx + 4, base)]
    for i in range(0, 13):
        px_ = bx + 4 + i * (bw - 8) / 12
        pts.append((px_, base - 22 - 9 * math.sin(i * 1.3) ** 2))
    pts.append((bx + bw - 4, base))
    b += f'<polygon points="{" ".join(f"{a:.1f},{c:.1f}" for a, c in pts)}" fill="{solid_color}" stroke="#b08a2e" stroke-width="1.5"/>'
    b += T(bx + bw / 2, base - 8, solid_label, 13, weight='bold')
    # الأيونات في المحلول بمواضع لا تتداخل
    placed = []
    for lab, n, col in ions:
        k = 0
        while k < n:
            cx = random.uniform(bx + 25, bx + bw - 25); cy = random.uniform(ly + 22, base - 52)
            if all((cx - a) ** 2 + (cy - c) ** 2 > 46 ** 2 for a, c in placed):
                placed.append((cx, cy)); b += ion(cx, cy, lab, col); k += 1
    # وسيلة الإيضاح
    lx = bx + bw + 40; yy = by + 40
    b += T(lx + 150, yy - 10, 'المفتاح', 14, 'end', weight='bold')
    for lab, n, col in ions:
        yy += 40; b += ion(lx + 132, yy, lab, col) + T(lx + 105, yy + 5, 'أيون', 14, 'end') + T(lx + 65, yy + 5, lab, 14, 'end', col, 'bold')
    yy += 40
    b += f'<rect x="{lx + 117}" y="{yy - 10}" width="30" height="20" fill="{solid_color}" stroke="#b08a2e"/>' + T(lx + 105, yy + 5, 'مادة صلبة غير مذابة', 14, 'end')
    if caption:
        for i, line in enumerate(caption):
            b += T(lx + 150, yy + 45 + i * 24, line, 14, 'end', BLUE, 'bold')
    if title: b += T(w / 2, 26, title, 15, weight='bold')
    save(name, svg(w, h, b))

def mix(name, left, right, mixed_label, w=600, h=275, mixed_note=None):
    """خلط محلولين: left/right = (الحجم، التركيز والصيغة)؛ والكأس الثالثة الخليط."""
    b = ''
    def one(x, vol, line2, fill):
        bb, ly = beaker(x, 60, 120, 140, fill)
        return bb + T(x + 60, 225, vol, 15, weight='bold') + T(x + 60, 250, line2, 14, color=BLUE, weight='bold')
    b += one(30, *left, 0.5) + T(180, 140, '+', 30, weight='bold')
    b += one(210, *right, 0.5)
    b += ARROW(350, 130, 420, 130, INK, 3)
    bb, ly = beaker(450, 60, 120, 140, 0.9)
    b += bb + T(510, 225, 'الخليط', 15, weight='bold') + T(510, 250, mixed_label, 15, weight='bold')
    if mixed_note: b += T(510, 270, mixed_note, 14, color=MUTED)
    b += T(w / 2, 30, 'خلط محلولين', 15, weight='bold')
    save(name, svg(w, h, b))

def common_ion_graph(name, ksp=2.3e-13, w=560, h=360):
    """ذائبية PbCrO₄ مقابل تركيز K₂CrO₄ (مقياس لوغاريتمي رأسي)."""
    X0, Y0, X1, Y1 = 110, h - 65, w - 40, 30
    xmax = 0.100; ylo, yhi = -13, -6
    px = lambda x: X0 + x / xmax * (X1 - X0)
    py = lambda lg: Y0 - (lg - ylo) / (yhi - ylo) * (Y0 - Y1)
    b = ''
    for e in range(ylo, yhi + 1): b += L(X0, py(e), X1, py(e), '#e3e7ee', 1)
    for t in (0.020, 0.040, 0.060, 0.080, 0.100): b += L(px(t), Y0, px(t), Y1, '#e3e7ee', 1)
    b += ARROW(X0, Y0, X1 + 14, Y0) + ARROW(X0, Y0, X0, Y1 - 14)
    for e in range(ylo, yhi + 1): b += L(X0 - 5, py(e), X0, py(e)) + pow10(X0 - 9, py(e) + 5, e)
    for t in (0, 0.020, 0.040, 0.060, 0.080, 0.100): b += L(px(t), Y0, px(t), Y0 + 5) + T(px(t), Y0 + 20, f'{t:.3f}' if t else '0', 13)
    b += T((X0 + X1) / 2, h - 18, 'تركيز K₂CrO₄ (mol/L)', 14, weight='bold')
    b += ylabel(28, (Y0 + Y1) / 2, 'ذائبية PbCrO₄ (mol/L)')
    pts = []
    for i in range(0, 401):
        c = xmax * (i / 400) ** 2
        s = (-c + math.sqrt(c * c + 4 * ksp)) / 2
        pts.append((px(c), py(math.log10(s))))
    b += f'<polyline points="{" ".join(f"{a:.1f},{c:.1f}" for a, c in pts)}" fill="none" stroke="{RED}" stroke-width="3.2" stroke-linejoin="round"/>'
    s0 = math.sqrt(ksp); s1 = (-0.1 + math.sqrt(0.01 + 4 * ksp)) / 2
    b += f'<circle cx="{px(0):.1f}" cy="{py(math.log10(s0)):.1f}" r="6" fill="{RED}" stroke="#fff" stroke-width="1.5"/>'
    b += f'<circle cx="{px(0.1):.1f}" cy="{py(math.log10(s1)):.1f}" r="6" fill="{RED}" stroke="#fff" stroke-width="1.5"/>'
    b += T(px(0) + 14, py(math.log10(s0)) + 2, 'ماء نقي', 13, 'start', RED, 'bold') + T(px(0) + 14, py(math.log10(s0)) + 20, '4.8 × 10⁻⁷ mol/L', 13, 'start', RED, 'bold')
    b += T(px(0.1) - 4, py(math.log10(s1)) - 14, '0.100 M K₂CrO₄: 2.3 × 10⁻¹² mol/L', 13, 'end', RED, 'bold')
    save(name, svg(w, h, b))

def tube(x, y, w, h, solid_h, label, solid_color='#e9b949'):
    r = w / 2; bot = y + h
    b = f'<path d="M{x},{y} L{x},{bot - r} A{r},{r} 0 0 0 {x + w},{bot - r} L{x + w},{y} Z" fill="#f4e7a1" stroke="none"/>'
    b += f'<path d="M{x},{bot - solid_h} L{x},{bot - r} A{r},{r} 0 0 0 {x + w},{bot - r} L{x + w},{bot - solid_h} Z" fill="{solid_color}" stroke="#a87a17" stroke-width="1"/>'
    b += f'<rect x="{x}" y="{y - 40}" width="{w}" height="40" fill="#fff"/>'
    b += f'<path d="M{x - 5},{y - 40} L{x},{y - 34} L{x},{bot - r} A{r},{r} 0 0 0 {x + w},{bot - r} L{x + w},{y - 34} L{x + w + 5},{y - 40}" fill="none" stroke="{GLASS}" stroke-width="3"/>'
    return b + T(x + w / 2, bot + 28, label, 16, weight='bold')

def tubes_common(name, w=520, h=370):
    b = tube(110, 130, 70, 180, 40, '(أ)') + tube(340, 130, 70, 180, 85, '(ب)')
    b += T(145, 30, 'محلول مشبع فوق', 14, weight='bold') + T(145, 50, 'مادة صلبة', 14, weight='bold')
    b += T(145, 72, 'PbCrO₄', 15, color=BLUE, weight='bold')
    b += T(375, 30, 'المحلول نفسه', 14, weight='bold') + T(375, 50, 'بعد إضافة محلول', 14, weight='bold')
    b += T(375, 72, 'Pb(NO₃)₂', 15, color=BLUE, weight='bold')
    b += ARROW(205, 220, 315, 220, INK, 3)
    b += T(260, 210, 'إضافة', 13, color=MUTED)
    save(name, svg(w, h, b))

def ksp_ladder(name, items, w=520, h=360, lo=-65, hi=-30):
    """تدريج لوغاريتمي رأسي لقيم Ksp. items = [(النص، القيمة، اللون)]"""
    X = 120; Y0, Y1 = h - 30, 35
    py = lambda lg: Y0 - (lg - lo) / (hi - lo) * (Y0 - Y1)
    b = L(X, Y0, X, Y1 - 5, INK, 2.5)
    for e in range(lo, hi + 1, 5): b += L(X - 6, py(e), X + 6, py(e)) + pow10(X - 12, py(e) + 5, e)
    b += ylabel(30, (Y0 + Y1) / 2, 'Ksp (مقياس لوغاريتمي)')
    for lab, val, kv, col in items:
        y = py(math.log10(val))
        b += f'<circle cx="{X}" cy="{y:.1f}" r="7" fill="{col}"/>' + L(X + 8, y, X + 40, y, col, 2)
        m, e = kv
        b += T(X + 48, y - 4, lab, 14, 'start', col, 'bold')
        b += (f'<text x="{X + 48}" y="{y + 18:.1f}" font-size="13" fill="{col}" {FONT}>Ksp = {m} × 10'
              f'<tspan dy="-6" font-size="10">{str(e).replace("-", "−")}</tspan></text>')
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # 1) محلول Mg(OH)₂ المشبع: Mg²⁺ إلى OH⁻ بنسبة 1:2
    sat_beaker('c3-l3b-sat-mgoh2.svg', 'Mg(OH)₂(s)', [('Mg²⁺', 4, GREEN), ('OH⁻', 8, BLUE)], seed=5)
    # 2) محلول مشبع لمركب مجهول: A³⁺ إلى B⁻ بنسبة 1:3
    sat_beaker('c3-l3b-sat-unknown.svg', 'مادة صلبة', [('A³⁺', 3, RED), ('B⁻', 9, BLUE)], seed=11)
    # 3) محلول مشبع من Ag₂CrO₄: Ag⁺ إلى CrO₄²⁻ بنسبة 2:1
    sat_beaker('c3-l3b-sat-ag2cro4.svg', 'Ag₂CrO₄(s)', [('Ag⁺', 8, MUTED), ('CrO₄²⁻', 4, RED)], seed=7, solid_color='#c9734a')
    # 4) محلول CaF₂ المشبع مع تركيز Ca²⁺ المقيس
    sat_beaker('c3-l3b-sat-caf2.svg', 'CaF₂(s)', [('Ca²⁺', 3, GREEN), ('F⁻', 6, BLUE)], seed=9, solid_color='#e6e6e6',
               caption=['[Ca²⁺] = 2.1 × 10⁻⁴ mol/L', 'عند 298 K'])
    # 5) الأيون المشترك: ذائبية PbCrO₄ مقابل [K₂CrO₄]
    common_ion_graph('c3-l3b-common-ion.svg')
    # 6) أنبوبا اختبار قبل إضافة Pb(NO₃)₂ وبعدها
    tubes_common('c3-l3b-tubes-pbcro4.svg')
    # 7) خلط محاليل
    mix('c3-l3b-mix-pbcl2.svg', ('50.0 mL', '0.040 M Pb(NO₃)₂'), ('50.0 mL', '0.020 M NaCl'), '100.0 mL')
    mix('c3-l3b-mix-baso4.svg', ('100.0 mL', '0.0020 M BaCl₂'), ('100.0 mL', '0.0010 M Na₂SO₄'), '200.0 mL')
    mix('c3-l3b-mix-unequal.svg', ('75.0 mL', '0.080 M AgNO₃'), ('25.0 mL', '0.040 M NaCl'), '100.0 mL')
    mix('c3-l3b-mix-caso4.svg', ('25.0 mL', '0.020 M CaCl₂'), ('25.0 mL', '0.020 M Na₂SO₄'), '50.0 mL')
    # 8) الفلوريد والأسنان: قيمتا Ksp على تدريج لوغاريتمي
    ksp_ladder('c3-l3b-apatite-ksp.svg', [('هيدروكسي الأباتيت Ca₅(PO₄)₃OH', 6.8e-37, ('6.8', -37), BLUE),
                                          ('الفلوروأباتيت Ca₅(PO₄)₃F', 1e-60, ('1', -60), GREEN)])
