import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 3-3 (أ): استعمال ثوابت الاتزان — حساب تراكيز الاتزان، Ksp، الذائبية المولارية، Qsp، توقع الرواسب.
# التشغيل: python3 data/chem22/gen/figs/C3-L3-a.py
import re, math, random

_save = save
def save(name, s):
    """أسس العشرة بعنصر tspan مرفوع بدل الأرقام العلوية (يظهر الصفر العلوي بخط مختلف في بعض المتصفحات)."""
    sup = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻', '0123456789−')
    s = re.sub('10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: '10<tspan baseline-shift="super" font-size="70%">' + m.group(1).translate(sup) + '</tspan>', s)
    _save(name, s)

ORANGE = '#c26a12'; PURPLE = '#6b3fa0'; GREY = '#8a94a3'

def ylab(x, y, s, size=14):
    rtl = ' direction="rtl"' if re.search('[؀-ۿ]', s) else ''
    return f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="bold" {FONT}{rtl}>{esc(s)}</text>'

def conc_time(name, curves, ymax, yticks, title=None, w=560, h=350, t_eq=0.55, eq_label='بلوغ الاتزان', show_ticks=True):
    """منحنى التركيز مقابل الزمن حتى الاتزان: كل منحنى يبدأ من start ويقترب أُسّيًّا من end ثم يصبح أفقيًّا.
    curves = [dict(start, end, color, label, value)] — value: النص المكتوب عند الخط الأفقي (قيمة الاتزان أو ؟)."""
    X0, Y0 = 80, h - 55; X1 = w - 150; Y1 = 50 if title else 30
    py = lambda y: Y0 - y / ymax * (Y0 - Y1)
    b = ''
    # show_ticks=False: بلا تدريج رقمي حتى لا تُقرأ القيمة المجهولة من الرسم (تُكتب القيم المعلومة بجانب الخطوط فقط)
    if show_ticks:
        for t in yticks: b += L(X0, py(t), X1, py(t), '#e3e7ee', 1)
    b += ARROW(X0, Y0, X1 + 15, Y0) + ARROW(X0, Y0, X0, Y1 - 15)
    if show_ticks:
        for t in yticks: b += L(X0 - 5, py(t), X0, py(t)) + T(X0 - 9, py(t) + 5, f'{t:g}', 13, 'end')
    b += T(X0 - 9, Y0 + 18, '0', 13, 'end')
    b += T((X0 + X1) / 2, h - 15, 'الزمن', 14, weight='bold')
    b += ylab(22, (Y0 + Y1) / 2, 'التركيز (mol/L)')
    xe = X0 + t_eq * (X1 - X0)
    b += L(xe, Y0, xe, Y1, MUTED, 1.3, '5 5') + T(xe, Y0 + 20, eq_label, 13, color=MUTED)
    for c in curves:
        pts = []
        for i in range(161):
            f = i / 160; x = X0 + f * (X1 - X0)
            k = min(f / t_eq, 1.0)
            y = c['end'] + (c['start'] - c['end']) * (math.exp(-5 * k) - math.exp(-5)) / (1 - math.exp(-5))
            pts.append((x, py(y)))
        b += f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{c["color"]}" stroke-width="3.2" stroke-linejoin="round"/>'
        ly = py(c['end']) + c.get('dy', 0)
        b += T(X1 + 10, ly + 5, c['label'], 15, 'start', c['color'], 'bold')
        b += T(X1 + 10 + c.get('lw', 50), ly + 5, c['value'], 14, 'start', c['color'], 'bold')
    if title: b += T(w / 2, 24, title, 16, weight='bold')
    save(name, svg(w, h, b))

def _ions(ox, oy, ww, hh, ions, seed):
    """جسيمات أيونات موزعة عشوائيًّا داخل مستطيل. ions = [(label, count, color)]"""
    rnd = random.Random(seed); placed = []; b = ''
    for lab, n, col in ions:
        for _ in range(n):
            for _try in range(400):
                x = ox + 16 + rnd.random() * (ww - 32); y = oy + 16 + rnd.random() * (hh - 32)
                if all((x - px) ** 2 + (y - py_) ** 2 > 38 ** 2 for px, py_ in placed): break
            placed.append((x, y))
            r = 17 if len(lab) > 3 else 14
            b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" stroke="{col}" stroke-width="2"/>' + T(x, y + 4.5, lab, 10.5 if len(lab) > 3 else 11, color=col, weight='bold')
    return b

def beaker(ox, oy, bw, bh, ions, solid_rows, label=None, seed=1, solid_label=None):
    """كأس فيها محلول وأيونات، وفي قاعها طبقة من المادة الصلبة غير الذائبة (solid_rows صفوف)."""
    b = ''
    lvl = oy + 28
    b += f'<rect x="{ox}" y="{lvl}" width="{bw}" height="{bh - 28}" fill="#e9f3fb"/>'
    sh = 0
    if solid_rows:
        sh = 14 * solid_rows
        rnd = random.Random(seed + 7)
        for r in range(solid_rows):
            yy = oy + bh - 9 - r * 13
            x = ox + 9 + (r % 2) * 6
            while x < ox + bw - 8:
                b += f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="6.2" fill="#d9d4c7" stroke="#8c8471" stroke-width="1"/>'
                x += 12.5
        if solid_label: b += T(ox + bw / 2, oy + bh + 22, solid_label, 13, color=MUTED)
    b += _ions(ox + 4, lvl + 4, bw - 8, bh - 28 - sh - 8, ions, seed)
    b += f'<path d="M{ox - 6},{oy} L{ox},{oy + 6} L{ox},{oy + bh} L{ox + bw},{oy + bh} L{ox + bw},{oy + 6} L{ox + bw + 6},{oy}" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
    b += L(ox, lvl, ox + bw, lvl, BLUE, 1.5)
    if label: b += T(ox + bw / 2, oy - 12, label, 15, weight='bold')
    return b

def saturated(name, ions, eq, ksp=None, solid_label=None, w=460, h=360, seed=3, solid_rows=3):
    """محلول مشبع فوق فائض من المادة الصلبة، مع معادلة الاتزان (وثابت حاصل الذائبية إن أُعطي)."""
    bw, bh = 240, 230; ox = (w - bw) / 2; oy = 40
    b = beaker(ox, oy, bw, bh, ions, solid_rows, seed=seed, solid_label=solid_label)
    b += T(w / 2, oy + bh + 50, eq, 16, weight='bold')
    if ksp: b += T(w / 2, oy + bh + 76, ksp, 15, color=RED, weight='bold')
    save(name, svg(w, h, b))

def two_beakers(name, left, right, w=600, h=380, caption=None):
    """كأسان متجاورتان: left/right = dict(label, ions, solid_rows, solid_label, note)"""
    bw, bh = 220, 220; oy = 45
    b = ''
    for k, p in enumerate((left, right)):
        ox = 50 + k * 290
        b += beaker(ox, oy, bw, bh, p['ions'], p.get('solid_rows', 0), p['label'], seed=11 + k, solid_label=p.get('solid_label'))
        if p.get('note'): b += T(ox + bw / 2, oy + bh + 48, p['note'], 13, color=INK)
    if caption: b += T(w / 2, h - 12, caption, 13, color=MUTED)
    save(name, svg(w, h, b))

def log_points(name, pts, ymin_exp, ymax_exp, ylabel_txt, xlabel_txt=None, line=None, w=520, h=340, title=None, curve=None, xs=None):
    """رسم بمحور رأسي لوغاريتمي (قوى العشرة).
    pts = [(x_label, value, color)] أعمدة/نقاط منفصلة؛ line = (value, text) خط أفقي متقطع (مثل Ksp).
    curve = (list of (x, value), xmax, xticks): منحنى متصل بمحور أفقي عددي."""
    X0, Y0 = 100, h - 60; X1 = w - 30; Y1 = 50 if title else 30
    py = lambda v: Y0 - (math.log10(v) - ymin_exp) / (ymax_exp - ymin_exp) * (Y0 - Y1)
    b = ''
    for e in range(ymin_exp, ymax_exp + 1):
        b += L(X0, py(10 ** e), X1, py(10 ** e), '#e3e7ee', 1) + L(X0 - 5, py(10 ** e), X0, py(10 ** e))
        b += f'<text x="{X0 - 9}" y="{py(10 ** e) + 5:.1f}" text-anchor="end" font-size="13" fill="{INK}" {FONT}>10<tspan dy="-6" font-size="10">{str(e).replace("-", "−")}</tspan></text>'
    b += ARROW(X0, Y0, X1 + 12, Y0) + ARROW(X0, Y0, X0, Y1 - 15)
    b += ylab(24, (Y0 + Y1) / 2, ylabel_txt)
    if xlabel_txt: b += T((X0 + X1) / 2, h - 14, xlabel_txt, 14, weight='bold')
    if pts:
        n = len(pts); step = (X1 - X0) / (n + 0.6)
        for i, (lab, v, col) in enumerate(pts):
            x = X0 + step * (i + 0.8)
            b += f'<rect x="{x - 24:.1f}" y="{py(v):.1f}" width="48" height="{Y0 - py(v):.1f}" fill="{col}" fill-opacity="0.85"/>'
            b += T(x, Y0 + 22, lab, 15, weight='bold')
    if curve:
        cpts, xmax, xticks = curve
        px = lambda x: X0 + x / xmax * (X1 - X0 - 10)
        for t in xticks: b += L(px(t), Y0, px(t), Y0 + 5) + T(px(t), Y0 + 20, f'{t:.2f}', 13)
        b += T(X0, Y0 + 20, '0', 13)
        b += f'<polyline points="{" ".join(f"{px(x):.1f},{py(v):.1f}" for x, v in cpts)}" fill="none" stroke="{BLUE}" stroke-width="3.2" stroke-linejoin="round"/>'
    if line:
        v, txt = line
        b += L(X0, py(v), X1, py(v), RED, 2.2, '8 5') + T(X0 + 8, py(v) - 8, txt, 14, 'start', RED, 'bold')
    if title: b += T(w / 2, 24, title, 15, weight='bold')
    save(name, svg(w, h, b))

def mixing(name, a, bsol, mix, w=640, h=300):
    """خلط محلولين: كأسان (a و b) بحجميهما وتركيزيهما ← كأس الخليط."""
    def cup(ox, oy, cw, ch, fill, lines, color=INK):
        s = f'<rect x="{ox}" y="{oy + 30}" width="{cw}" height="{ch - 30}" fill="{fill}"/>'
        s += f'<path d="M{ox - 5},{oy} L{ox},{oy + 5} L{ox},{oy + ch} L{ox + cw},{oy + ch} L{ox + cw},{oy + 5} L{ox + cw + 5},{oy}" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        for i, ln in enumerate(lines):
            s += T(ox + cw / 2, oy + ch + 24 + i * 22, ln, 14, color=color, weight='bold' if i == 0 else 'normal')
        return s
    b = cup(30, 60, 130, 120, '#e3effa', a)
    b += T(200, 130, '+', 34, weight='bold')
    b += cup(240, 60, 130, 120, '#eef7e6', bsol)
    b += ARROW(395, 120, 455, 120, INK, 3)
    b += cup(475, 40, 140, 140, '#f1ecf8', mix)
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # 1) H₂ + I₂ ⇌ 2HI: [H₂] = [I₂] من 0.500 إلى 0.110، و[HI] من 0 إلى ؟ (0.780)
    conc_time('c3-l3a-hi-conctime.svg',
              [dict(start=0.500, end=0.110, color=BLUE, label='H₂ و I₂', value='0.110 M', lw=62),
               dict(start=0.0, end=0.780, color=RED, label='HI', value='؟', lw=34)],
              0.9, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], title='H₂(g) + I₂(g) ⇌ 2HI(g)', show_ticks=False)
    # 2) N₂O₄ ⇌ 2NO₂: [N₂O₄] من 0.0468 إلى 0.0400، و[NO₂] من 0 إلى ؟ (0.0136)
    conc_time('c3-l3a-n2o4-conctime.svg',
              [dict(start=0.0468, end=0.0400, color=ORANGE, label='N₂O₄', value='0.0400 M', lw=58),
               dict(start=0.0, end=0.0136, color=RED, label='NO₂', value='؟', lw=46)],
              0.05, [0.01, 0.02, 0.03, 0.04, 0.05], title='N₂O₄(g) ⇌ 2NO₂(g)', show_ticks=False)
    # 3) PCl₅ ⇌ PCl₃ + Cl₂: [PCl₅] = 0.200، [PCl₃] = 0.100، [Cl₂] = ؟ (0.0900 لكن الرسم لا يفترض أن Cl₂ = PCl₃)
    conc_time('c3-l3a-pcl5-conctime.svg',
              [dict(start=0.290, end=0.200, color=ORANGE, label='PCl₅', value='0.200 M', lw=50),
               dict(start=0.010, end=0.100, color=BLUE, label='PCl₃', value='0.100 M', lw=50, dy=-4),
               dict(start=0.0, end=0.090, color=GREEN, label='Cl₂', value='؟', lw=40, dy=14)],
              0.35, [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35], title='PCl₅(g) ⇌ PCl₃(g) + Cl₂(g)', show_ticks=False)
    # 4) محلول AgI مشبع فوق راسب
    saturated('c3-l3a-agi-saturated.svg', [('Ag⁺', 3, BLUE), ('I⁻', 3, RED)],
              'AgI(s) ⇌ Ag⁺(aq) + I⁻(aq)', 'Ksp = 8.5 × 10⁻¹⁷ (298 K)', solid_label='AgI(s) غير ذائب')
    # 5) محلول AgCl مشبع
    saturated('c3-l3a-agcl-saturated.svg', [('Ag⁺', 3, BLUE), ('Cl⁻', 3, GREEN)],
              'AgCl(s) ⇌ Ag⁺(aq) + Cl⁻(aq)', 'Ksp = 1.8 × 10⁻¹⁰ (298 K)', solid_label='AgCl(s) غير ذائب', seed=5)
    # 6) محلول PbI₂ مشبع (أيونا I⁻ لكل Pb²⁺) بلا قيمة Ksp
    saturated('c3-l3a-pbi2-saturated.svg', [('Pb²⁺', 2, PURPLE), ('I⁻', 4, RED)],
              'PbI₂(s) ⇌ Pb²⁺(aq) + 2I⁻(aq)', None, solid_label='PbI₂(s) غير ذائب', seed=9, h=330)
    # 7) كأسان: (1) BaCl₂ ذائب كليًّا، (2) BaSO₄ أغلبه صلب
    two_beakers('c3-l3a-ba-beakers.svg',
                dict(label='الكأس (1)', ions=[('Ba²⁺', 5, PURPLE), ('Cl⁻', 10, GREEN)], solid_rows=0, note='المركب ذاب كله'),
                dict(label='الكأس (2)', ions=[('Ba²⁺', 1, PURPLE), ('SO₄²⁻', 1, ORANGE)], solid_rows=4, solid_label='مادة صلبة غير ذائبة', note=''),
                caption='الكتلة نفسها من مركب باريوم في \u200e100 mL من الماء في كل كأس عند \u200e25 °C')
    # 8) تأثير الأيون المشترك: [Ba²⁺] في محلول BaSO₄ مشبع مقابل تركيز Na₂SO₄ (Ksp = 1.1 × 10⁻¹⁰)
    ksp = 1.1e-10; cs = []
    for i in range(0, 201):
        c = 0.10 * i / 200
        s = (-c + math.sqrt(c * c + 4 * ksp)) / 2
        cs.append((c, s))
    log_points('c3-l3a-baso4-common-ion.svg', None, -10, -4, '[Ba²⁺] (mol/L)', 'تركيز Na₂SO₄ المضاف (mol/L)',
               curve=(cs, 0.10, [0.02, 0.04, 0.06, 0.08, 0.10]), title='محلول BaSO₄ مشبع عند \u200e298 K')
    # 9) Qsp لثلاثة خلائط مقارنة بـ Ksp لـ AgCl
    log_points('c3-l3a-q-vs-ksp.svg', [('(1)', 3.6e-12, GREEN), ('(2)', 1.8e-10, BLUE), ('(3)', 2.5e-8, PURPLE)],
               -13, -7, 'الحاصل الأيوني Qsp', 'الخليط', line=(1.8e-10, 'Ksp (AgCl) = 1.8 × 10⁻¹⁰'),
               title='قيم Qsp = [Ag⁺][Cl⁻] لحظة الخلط عند \u200e298 K')
    # 10) خلط Pb(NO₃)₂ مع NaCl
    mixing('c3-l3a-mix-pbcl2.svg', ['50.0 mL', '0.0400 M Pb(NO₃)₂'], ['50.0 mL', '0.0300 M NaCl'],
           ['حجم الخليط \u200e100.0 mL', 'Ksp (PbCl₂) = 1.7 × 10⁻⁵'])
    # 11) خلط AgNO₃ مع NaCl
    mixing('c3-l3a-mix-agcl.svg', ['50.0 mL', '1.0 × 10⁻⁴ M AgNO₃'], ['50.0 mL', '1.0 × 10⁻⁴ M NaCl'],
           ['حجم الخليط \u200e100.0 mL', 'Ksp (AgCl) = 1.8 × 10⁻¹⁰'])
