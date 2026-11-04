# رسوم الدرس 2-1 (نظرية التصادم وسرعة التفاعل): مخططات طاقة التفاعل، واتجاه التصادم، ومنحنيات التركيز–الزمن.
# التشغيل: python3 data/chem22/gen/figs/C2-L1-a.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

ORANGE = '#d9822b'; PURPLE = '#6a4c9c'; GRAY = '#3a3a3a'


def circ_num(x, y, n, r=11):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>' + T(x, y + 5, str(n), 13, weight='bold')


def reaction_profile(name, r, p, peak, w=600, h=330, r_label='المتفاعلات', p_label='النواتج',
                     complex_label=None, ea=None, dh=None, rev_ea=None, nums=None, ticks=None,
                     title=None, ox=0, standalone=True, panel_label=None, scale=None, hump=(0.30, 0.48, 0.64)):
    """مخطط طاقة التفاعل مع سير التفاعل. r, p, peak: طاقة المتفاعلات والنواتج وقمة المنحنى (وحدات المحور).
    ea / dh / rev_ea: نص سهم طاقة التنشيط / ΔH / طاقة تنشيط التفاعل العكسي (None = لا سهم).
    nums: قاموس {'r','p','peak','ea','dh'} -> رقم في دائرة بدل التسميات. ticks: قيم تُكتب على محور الطاقة."""
    X0, Y0, X1, Y1 = ox + 70, h - 45, ox + w - 20, 40 if title or panel_label else 25
    lo = min(r, p, 0 if ticks else min(r, p)); hi = peak
    if ticks: lo, hi = min(ticks), max(ticks)
    if scale: lo, hi = scale
    span = hi - lo
    def y(v): return Y0 - 15 - (v - lo) / span * (Y0 - 15 - Y1 - 20)
    yr, yp, yk = y(r), y(p), y(peak)
    xa, xb, xk, xc, xd = X0 + 20, X0 + hump[0] * (X1 - X0), X0 + hump[1] * (X1 - X0), X0 + hump[2] * (X1 - X0), X1 - 10
    xh = xd - 10  # موضع سهم ΔH
    pc = (xc + xh) / 2 - 8  # مركز تسمية النواتج
    b = ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    b += T((X0 + X1) / 2, h - 14, 'سير التفاعل', 14, weight='bold')
    b += f'<text transform="translate({X0 - (48 if ticks else 18)},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT}>{"الطاقة (kJ)" if ticks else "الطاقة"}</text>'
    if ticks:
        for v in ticks:
            b += L(X0 - 5, y(v), X0, y(v)) + T(X0 - 9, y(v) + 5, str(v), 12, 'end') + L(X0, y(v), X1 - 10, y(v), '#d5dae2', 1, '2 4')
    k = 0.55 * (xk - xb)
    b += (f'<path d="M {xa},{yr:.1f} L {xb},{yr:.1f} C {xb + k:.1f},{yr:.1f} {xk - k:.1f},{yk:.1f} {xk},{yk:.1f} '
          f'C {xk + k:.1f},{yk:.1f} {xc - k:.1f},{yp:.1f} {xc},{yp:.1f} L {xd},{yp:.1f}" fill="none" stroke="{GREEN}" stroke-width="3.2"/>')
    nums = nums or {}
    # تسميات المستويات
    if 'r' in nums: b += circ_num((xa + xb) / 2, yr - 16, nums['r'])
    elif r_label: b += T((xa + xb) / 2, yr - 10, r_label, 14)
    if 'p' in nums: b += circ_num(pc, yp - 16, nums['p'])
    elif p_label: b += T(pc, yp - 10, p_label, 14)
    if 'peak' in nums: b += circ_num(xk, yk - 16, nums['peak'])
    elif complex_label: b += T(xk, yk - 10, complex_label, 14)
    # سهم طاقة التنشيط
    if ea is not None or 'ea' in nums:
        b += L(xb, yr, xk + 4, yr, MUTED, 1.2, '4 4') + ARROW(xk, yr - 1, xk, yk + 4, RED, 2.2)
        if 'ea' in nums: b += circ_num(xk + 20, (yr + yk) / 2, nums['ea'])
        else: b += T(xk + 8, (yr + yk) / 2 + 5, ea, 13, 'start', RED, 'bold')
    if rev_ea is not None:
        xr = xk + 0.38 * (xc - xk)
        b += L(xr - 4, yp, xc, yp, MUTED, 1.2, '4 4')
        b += ARROW(xr, yp + (1 if yp > yk else -1), xr, yk + 6, PURPLE, 2.2)
        b += T(xr + 6, (yp + yk) / 2 + 30, rev_ea, 13, 'start', PURPLE, 'bold')
    if dh is not None or 'dh' in nums:
        b += L(xk + 4, yr, xh + 6, yr, MUTED, 1.2, '4 4') if yr != yp else ''
        b += ARROW(xh, yr + (2 if yp > yr else -2), xh, yp + (-3 if yp > yr else 3), BLUE, 2.2)
        if 'dh' in nums: b += circ_num(xh - 20, (yr + yp) / 2, nums['dh'])
        else: b += T(xh - 8, (yr + yp) / 2 + 5, dh, 13, 'end', BLUE, 'bold')
    if title: b += T(ox + w / 2, 22, title, 15, weight='bold')
    if panel_label: b += T(ox + w / 2, 22, panel_label, 16, weight='bold')
    if standalone: save(name, svg(w, h, b))
    return b


def atom(x, y, kind, r=None):
    col = {'C': GRAY, 'N': BLUE, 'O': RED, 'A': PURPLE, 'B': ORANGE}[kind]
    r = r or (13 if kind in 'CNAB' else 11)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" stroke="#fff" stroke-width="1.5"/>'


def co(x, y, c_first=True):
    """جزيء CO أفقي؛ c_first: ذرة C على اليسار."""
    return (atom(x, y, 'C') + atom(x + 20, y, 'O')) if c_first else (atom(x, y, 'O') + atom(x + 20, y, 'C'))


def no2(x, y, o_left=True):
    """جزيء NO₂: ذرة N وذرتا O. o_left: إحدى ذرتي O تواجه اليسار، وإلا فذرة N هي المواجهة لليسار."""
    if o_left: return atom(x, y, 'O') + atom(x + 19, y + 8, 'N') + atom(x + 38, y, 'O')
    return atom(x, y, 'N') + atom(x + 17, y - 13, 'O') + atom(x + 17, y + 13, 'O')


def collision_orientation(name):
    """لوحتان: (س) ذرة O في CO تواجه ذرة N في NO₂؛ (ص) ذرة C في CO تواجه ذرة O في NO₂."""
    w, h = 560, 250
    b = ''
    for i, (lab, cfirst, oleft) in enumerate([('(س)', False, False), ('(ص)', True, True)]):
        ox = 20 + i * 275
        b += T(ox + 120, 30, lab, 16, weight='bold')
        # CO على اليسار: الذرة اليمنى هي المواجهة لـ NO₂
        b += (atom(ox + 30, 100, 'O') + atom(ox + 51, 100, 'C')) if cfirst else (atom(ox + 30, 100, 'C') + atom(ox + 51, 100, 'O'))
        b += ARROW(ox + 72, 135, ox + 100, 135, INK, 2) + ARROW(ox + 168, 135, ox + 140, 135, INK, 2)
        b += no2(ox + 150, 100, o_left=oleft)
        if i == 0: b += L(272, 20, 272, 175, MUTED, 1, '4 4')
    # مفتاح الألوان
    ly = 205
    for k, (kind, txt) in enumerate([('C', 'كربون'), ('N', 'نيتروجين'), ('O', 'أكسجين')]):
        x = 420 - k * 150
        b += atom(x + 60, ly, kind, 9) + T(x + 45, ly + 5, txt, 13, 'end')
    b += f'<rect x="110" y="{ly - 18}" width="400" height="36" fill="none" stroke="{MUTED}" stroke-width="1" rx="6"/>'
    save(name, svg(w, h, b))


def collision_stages(name):
    """A₂ + B₂ ← (1) قبل التصادم، (2) تجمع مؤقت للذرات الأربع، (3) 2AB."""
    w, h = 580, 210
    b = ''
    # المرحلة 1
    b += atom(60, 80, 'A') + atom(60, 106, 'A') + T(95, 98, '+', 18) + atom(130, 80, 'B') + atom(130, 106, 'B')
    b += ARROW(170, 93, 215, 93, INK, 2.2)
    # المرحلة 2: نجمة + تجمع رباعي
    import math
    pts = ' '.join(f'{290 + (48 if j % 2 == 0 else 26) * math.cos(j * math.pi / 8):.1f},{93 + (48 if j % 2 == 0 else 26) * math.sin(j * math.pi / 8):.1f}' for j in range(16))
    b += f'<polygon points="{pts}" fill="#fde9b8" stroke="#e8b84a" stroke-width="1.2"/>'
    b += atom(277, 80, 'A') + atom(277, 106, 'A') + atom(303, 80, 'B') + atom(303, 106, 'B')
    b += ARROW(355, 93, 400, 93, INK, 2.2)
    # المرحلة 3
    b += atom(430, 93, 'A') + atom(454, 93, 'B') + T(487, 99, '+', 18) + atom(515, 93, 'A') + atom(539, 93, 'B')
    for x, n in [(95, 1), (290, 2), (485, 3)]: b += circ_num(x, 165, n, 13)
    b += T(95, 40, 'A₂ + B₂', 15) + T(485, 40, '2AB', 15)
    save(name, svg(w, h, b))


def conc_time(name, series, xmax, ymax, xstep, ystep, xlabel='الزمن (s)', ylabel='التركيز (mol/L)',
              w=520, h=330, ydec=2, show_vals=False, rpad=30):
    """منحنيات تركيز–زمن. series = [(label, [(t, c), ...], color)]؛ النقاط تقع على خطوط الشبكة."""
    X0, Y0, X1, Y1 = 80, h - 50, w - rpad, 25
    def px(t): return X0 + t / xmax * (X1 - X0 - 15)
    def py(c): return Y0 - c / ymax * (Y0 - Y1 - 15)
    b = ''
    n = 0
    while n * ystep <= ymax + 1e-9:
        v = n * ystep
        b += L(X0, py(v), px(xmax), py(v), '#dfe3ea', 1) + T(X0 - 8, py(v) + 5, f'{v:.{ydec}f}', 12, 'end')
        n += 1
    n = 0
    while n * xstep <= xmax + 1e-9:
        v = n * xstep
        b += L(px(v), Y0, px(v), py(ymax), '#dfe3ea', 1) + T(px(v), Y0 + 18, f'{v:g}', 12)
        n += 1
    b += ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1)
    b += T((X0 + X1) / 2, h - 8, xlabel, 14, weight='bold')
    b += f'<text transform="translate({X0 - 58},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT}>{esc(ylabel)}</text>'
    for lab, pts, col in series:
        b += f'<polyline points="{" ".join(f"{px(t):.1f},{py(c):.1f}" for t, c in pts)}" fill="none" stroke="{col}" stroke-width="2.8" stroke-linejoin="round"/>'
        for t, c in pts:
            b += f'<circle cx="{px(t):.1f}" cy="{py(c):.1f}" r="4.5" fill="{col}"/>'
            if show_vals: b += T(px(t) + 7, py(c) - 8, f'{c}', 11, 'start', col)
        t, c = pts[-1]
        b += T(px(t) + 8, py(c) + 5, lab, 14, 'start', col, 'bold')
    save(name, svg(w, h, b))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # مخطط طارد بالصيغ (CO + NO₂)
    reaction_profile('c2-l1a-profile-exo-co.svg', 60, 15, 100, r_label='CO(g) + NO₂(g)', p_label='CO₂(g) + NO(g)',
                     complex_label='المعقد المنشط', ea='Ea', dh='ΔH')
    # مخطط ماص (التفاعل العكسي) بالصيغ
    reaction_profile('c2-l1a-profile-endo-co2.svg', 15, 60, 100, r_label='CO₂(g) + NO(g)', p_label='CO(g) + NO₂(g)',
                     complex_label='المعقد المنشط', ea='Ea', dh='ΔH')
    # مخطط ماص مرقّم (1 سهم طاقة التنشيط، 2 المتفاعلات، 3 القمة، 4 النواتج)
    reaction_profile('c2-l1a-profile-numbered-endo.svg', 15, 45, 100, nums={'ea': 1, 'r': 2, 'peak': 3, 'p': 4})
    # مخطط طارد مرقّم (1 القمة، 2 سهم Ea، 3 سهم ΔH، 4 النواتج)
    reaction_profile('c2-l1a-profile-numbered-exo.svg', 60, 15, 100, nums={'peak': 1, 'ea': 2, 'dh': 3, 'p': 4})
    # مخططات بقيم عددية
    reaction_profile('c2-l1a-profile-values-exo.svg', 150, 40, 210, r_label='المتفاعلات', p_label='النواتج',
                     ticks=[0, 40, 150, 210])
    reaction_profile('c2-l1a-profile-values-endo.svg', 50, 125, 225, ticks=[0, 50, 125, 225])
    # لوحتان: (س) ماص، (ص) طارد — دون أسهم
    b = reaction_profile('', 20, 60, 100, w=380, h=260, standalone=False, panel_label='(س)', scale=(10, 100), hump=(0.20, 0.45, 0.70))
    b += reaction_profile('', 60, 15, 100, w=380, h=260, ox=380, standalone=False, panel_label='(ص)', scale=(10, 100), hump=(0.20, 0.45, 0.70))
    b += L(380, 15, 380, 250, MUTED, 1, '4 4')
    save('c2-l1a-profile-two.svg', svg(760, 260, b))
    # لوحتان لتفاعلين طاردين: (س) قمة عالية، (ص) قمة منخفضة، والمتفاعلات والنواتج متساوية المستوى
    b = reaction_profile('', 50, 20, 110, w=380, h=260, standalone=False, panel_label='(س)', ea='Ea', scale=(15, 110), hump=(0.20, 0.45, 0.70))
    b += reaction_profile('', 50, 20, 82, w=380, h=260, ox=380, standalone=False, panel_label='(ص)', ea='Ea', scale=(15, 110), hump=(0.20, 0.45, 0.70))
    b += L(380, 15, 380, 250, MUTED, 1, '4 4')
    save('c2-l1a-profile-ea-compare.svg', svg(760, 260, b))
    # اتجاه التصادم ومراحله
    collision_orientation('c2-l1a-collision-orient.svg')
    collision_stages('c2-l1a-collision-stages.svg')
    # تركيز–زمن: A → B
    conc_time('c2-l1a-conc-ab.svg', [('[A]', [(0, 0.80), (10, 0.50), (20, 0.30), (30, 0.20), (40, 0.15)], RED),
                                 ('[B]', [(0, 0.0), (10, 0.30), (20, 0.50), (30, 0.60), (40, 0.65)], BLUE)],
              xmax=40, ymax=0.80, xstep=10, ystep=0.10)
    # منحنيان غير مسميين (س) و(ص) لتفاعل A → B
    conc_time('c2-l1a-conc-two-curves.svg', [('(س)', [(0, 0.0), (10, 0.30), (20, 0.50), (30, 0.60), (40, 0.65)], BLUE),
                                         ('(ص)', [(0, 0.80), (10, 0.50), (20, 0.30), (30, 0.20), (40, 0.15)], RED)],
              xmax=40, ymax=0.80, xstep=10, ystep=0.10)
    # تحلل N₂O₅ (بيانات مختبر حل المشكلات)
    conc_time('c2-l1a-conc-n2o5.svg', [('[N₂O₅]', [(0, 0.01756), (20, 0.00933), (40, 0.00531), (60, 0.00295), (80, 0.00167), (100, 0.00094)], RED)],
              xmax=100, ymax=0.020, xstep=20, ystep=0.004, xlabel='الزمن (min)', ydec=3, show_vals=True, w=620, rpad=90)
