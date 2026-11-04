# رسوم الدرس 2-2 (العوامل المؤثرة في سرعة التفاعل الكيميائي). التشغيل: python3 data/chem22/gen/figs/C2-L2-a.py
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

ORANGE = '#c76a1c'; PURPLE = '#6b4fa0'; GREY = '#9aa3ad'

def path_d(pts):
    return 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts)

def xaxis_label(x, y, s, size=14):
    return T(x, y, s, size, rtl=True)

def ylabel(x, y, s, size=14):
    return f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="bold" {FONT}>{esc(s)}</text>'

# ---------- منحنيات توزيع طاقة الجسيمات ----------
def distribution(name, curves, ea=None, ea_label='طاقة التنشيط', shade=True, note=None, w=520, h=320, extra_ea=()):
    """curves = [(label, kT, color)] بمساحات متساوية؛ ea = قيمة طاقة التنشيط على المحور (0..6)؛
    extra_ea = [(قيمة, نص)] خطوط تنشيط إضافية (مثلًا مع محفز)."""
    X0, Y0, X1, Y1 = 70, h - 50, w - 25, 30
    Emax = 6.0
    def f(E, kT): return math.sqrt(E) * math.exp(-E / kT) / (kT ** 1.5)
    fmax = max(f(kT / 2, kT) for _, kT, _ in curves) * 1.12
    def px(E): return X0 + E / Emax * (X1 - X0)
    def py(v): return Y0 - v / fmax * (Y0 - Y1)
    b = ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1 - 5)
    b += xaxis_label((X0 + X1) / 2, h - 18, 'طاقة التصادم') + ylabel(X0 - 18, (Y0 + Y1) / 2, 'عدد الجسيمات')
    b += T(X0 - 8, Y0 + 5, '0', 13, 'end')
    for lab, kT, col in curves:
        Es = [i * Emax / 300 for i in range(301)]
        pts = [(px(E), py(f(E, kT))) for E in Es]
        if shade and ea is not None:
            sp = [(px(E), py(f(E, kT))) for E in Es if E >= ea]
            poly = [(px(ea), Y0)] + sp + [(px(Emax), Y0)]
            b += f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in poly)}" fill="{col}" fill-opacity="0.25" stroke="none"/>'
        b += f'<path d="{path_d(pts)}" fill="none" stroke="{col}" stroke-width="3"/>'
        pk = kT / 2
        b += T(px(pk) + 4, py(f(pk, kT)) - 10, lab, 15, color=col, weight='bold')
    if ea is not None:
        b += L(px(ea), Y0, px(ea), Y1 + 10, INK, 1.6, '6 5') + T(px(ea) + 6, Y1 + 22, ea_label, 13, 'start', INK, 'bold')
    for val, txt in extra_ea:
        if shade:
            for lab, kT, col in curves:
                Es = [i * Emax / 300 for i in range(301)]
                sp = [(px(E), py(f(E, kT))) for E in Es if E >= val]
                poly = [(px(val), Y0)] + sp + [(px(Emax), Y0)]
                b += f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in poly)}" fill="{GREEN}" fill-opacity="0.15" stroke="none"/>'
        b += L(px(val), Y0, px(val), Y1 + 50, GREEN, 1.6, '6 5') + T(px(val) + 6, Y1 + 62, txt, 13, 'start', GREEN, 'bold')
    if note: b += T(X0 + 140, Y1 + 40, note, 15, 'start', INK, 'bold')
    save(name, svg(w, h, b))

# ---------- مخطط طاقة سير التفاعل (مع محفز أو مثبط) ----------
def profile_curve(R, P, peak, x0, x1, xc=None):
    """منحنى أملس من مستوى R إلى P بقمة عند peak (إحداثيات SVG: القيم الأصغر أعلى)."""
    xc = xc if xc is not None else (x0 + x1) / 2
    sig = (x1 - x0) * 0.11
    def base(x):
        t = min(1, max(0, (x - (xc - 1.2 * sig)) / (2.4 * sig)))
        return R + (P - R) * (3 * t * t - 2 * t ** 3)
    xs = [x0 + i * (x1 - x0) / 400 for i in range(401)]
    lo, hi = 0.0, 2000.0
    for _ in range(60):
        A = (lo + hi) / 2
        top = min(base(x) - A * math.exp(-((x - xc) / sig) ** 2) for x in xs)
        if top > peak: lo = A
        else: hi = A
    return [(x, base(x) - A * math.exp(-((x - xc) / sig) ** 2)) for x in xs]

def profile(name, R, P, paths, w=540, h=340, title=None, ea_arrows=(), dh_arrow=None, labels=True, axis='الطاقة'):
    """paths = [(peak_y, color, label, label_xy)]؛ ea_arrows = [(x, y_top, text, color, side)]؛ dh_arrow = (x, text)"""
    X0, Y0, X1, Y1 = 70, h - 45, w - 20, 25
    b = ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1)
    b += xaxis_label((X0 + X1) / 2, h - 14, 'سير التفاعل') + ylabel(X0 - 18, (Y0 + Y1) / 2, axis)
    for peak, col, lab, (lx, ly) in paths:
        pts = profile_curve(R, P, peak, X0 + 15, X1 - 10)
        b += f'<path d="{path_d(pts)}" fill="none" stroke="{col}" stroke-width="3"/>'
        if lab: b += T(lx, ly, lab, 14, color=col, weight='bold')
    if labels:
        b += T(X0 + 50, R - 10, 'المتفاعلات', 14) + T(X1 - 60, P + 22, 'النواتج', 14)
    b += L(X0 + 15, R, X1 - 10, R, MUTED, 1, '4 4')
    for x, ytop, txt, col, side in ea_arrows:
        b += ARROW(x, R - 2, x, ytop + 3, col, 2)
        b += L(x - 8, ytop, x + 8, ytop, col, 1.5) + L(x, ytop, (X0 + X1) / 2 + 2, ytop, col, 1, '3 4')
        b += T(x + (8 if side == 'start' else -8), (R + ytop) / 2 + 5, txt, 13, side, col, 'bold')
    if dh_arrow:
        x, txt = dh_arrow
        b += ARROW(x, R + 2, x, P - 3, RED, 2) + T(x + 8, (R + P) / 2 + 5, txt, 13, 'start', RED, 'bold')
    if title: b += T(w / 2, 18, title, 15, weight='bold', rtl=True)
    save(name, svg(w, h, b))

# ---------- سرعة التفاعل ودرجة الحرارة ----------
def rate_temp(name, pts, w=480, h=330, labels=True, curve=True, tmin=280, tmax=335, rmax=35):
    X0, Y0, X1, Y1 = 75, h - 55, w - 25, 25
    def px(t): return X0 + (t - tmin) / (tmax - tmin) * (X1 - X0)
    def py(r): return Y0 - r / rmax * (Y0 - Y1)
    b = ''
    for r in range(5, rmax + 1, 5):
        b += L(X0, py(r), X1, py(r), '#e3e7ec', 1) + T(X0 - 8, py(r) + 5, str(r), 12, 'end', MUTED)
    for t in range(tmin, tmax + 1, 10):
        b += L(px(t), Y0, px(t), Y1, '#e3e7ec', 1) + T(px(t), Y0 + 18, str(t), 12, color=MUTED)
    b += ARROW(X0, Y0, X1 + 5, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    b += xaxis_label((X0 + X1) / 2, h - 12, 'درجة الحرارة (K)') + ylabel(X0 - 40, (Y0 + Y1) / 2, 'سرعة التفاعل النسبية')
    if curve:
        cs = [(px(t), py(2 * 2 ** ((t - 290) / 10))) for t in [tmin + i * (tmax - tmin) / 200 for i in range(201)] if 2 * 2 ** ((t - 290) / 10) <= rmax + 0.5]
        b += f'<path d="{path_d(cs)}" fill="none" stroke="{BLUE}" stroke-width="3"/>'
    for t, r in pts:
        b += f'<circle cx="{px(t):.1f}" cy="{py(r):.1f}" r="5" fill="{INK}"/>'
        if labels: b += T(px(t) - 8, py(r) - 9, f'({t} K, {r})', 12, 'end', INK)
    save(name, svg(w, h, b))

# ---------- سرعة التفاعل الإنزيمي ودرجة حرارة الجسم ----------
def enzyme_curve(name, w=480, h=320):
    X0, Y0, X1, Y1 = 70, h - 55, w - 25, 25
    def px(t): return X0 + t / 60 * (X1 - X0)
    b = ''
    for t in range(0, 61, 10):
        b += L(px(t), Y0, px(t), Y0 + 5) + T(px(t), Y0 + 20, str(t), 12, color=MUTED)
    b += ARROW(X0, Y0, X1 + 5, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    b += xaxis_label((X0 + X1) / 2, h - 12, 'درجة الحرارة (°C)') + ylabel(X0 - 18, (Y0 + Y1) / 2, 'سرعة التفاعل')
    pts = []
    for i in range(241):
        t = i * 60 / 240
        if t <= 40: v = 0.12 + 0.88 * math.sin(t / 40 * math.pi / 2) ** 1.6
        else: v = math.cos((t - 40) / 20 * math.pi / 2) ** 0.9
        pts.append((px(t), Y0 - v * (Y0 - Y1 - 20)))
    b += f'<path d="{path_d(pts)}" fill="none" stroke="{BLUE}" stroke-width="3"/>'
    b += L(px(37), Y0, px(37), Y1 + 15, MUTED, 1.2, '4 4') + T(px(37) - 6, Y1 + 12, '37 °C', 12, 'end', MUTED)
    save(name, svg(w, h, b))

# ---------- مكعب كامل مقابل مكعبات صغيرة ----------
def cube(x, y, s, fill='#d9e6f2'):
    d = s * 0.45
    front = f'<polygon points="{x},{y} {x+s},{y} {x+s},{y+s} {x},{y+s}" fill="{fill}" stroke="{INK}" stroke-width="1.6"/>'
    top = f'<polygon points="{x},{y} {x+d},{y-d} {x+s+d},{y-d} {x+s},{y}" fill="#eef4fa" stroke="{INK}" stroke-width="1.6"/>'
    side = f'<polygon points="{x+s},{y} {x+s+d},{y-d} {x+s+d},{y+s-d} {x+s},{y+s}" fill="#b9cfe4" stroke="{INK}" stroke-width="1.6"/>'
    return front + top + side

def cubes2(name, w=640, h=270, big='2 cm', small='1 cm'):
    b = T(135, 26, '(س) قطعة واحدة', 15, weight='bold') + T(455, 26, '(ص) ثماني قطع منفصلة', 15, weight='bold')
    b += cube(80, 100, 110) + T(135, 245, f'طول الضلع \u2066{big}\u2069', 14, rtl=True)
    s = 55
    pos = [(300 + 80 * i, 80 + 88 * j) for j in range(2) for i in range(4)]
    for x, y in pos: b += cube(x, y, s)
    b += T(455, 245, f'طول ضلع كل قطعة \u2066{small}\u2069', 14, rtl=True)
    b += L(270, 40, 270, 250, MUTED, 1, '4 4')
    save(name, svg(w, h, b))

# ---------- كأسان: شريط فلز في محلول نترات الفضة ----------
def beakers(name, a_label, b_label, a_dots, b_dots, w=520, h=290, caption='AgNO₃ 0.05 M', strip_cols=('#c9d3db', '#c9d3db')):
    random.seed(7)
    b = ''
    for k, (lab, n, scol) in enumerate([(a_label, a_dots, strip_cols[0]), (b_label, b_dots, strip_cols[1])]):
        ox = 60 + k * 240
        b += f'<path d="M {ox},60 L {ox},240 Q {ox},252 {ox+12},252 L {ox+148},252 Q {ox+160},252 {ox+160},240 L {ox+160},60" fill="none" stroke="{INK}" stroke-width="2.5"/>'
        b += f'<rect x="{ox+2}" y="110" width="156" height="140" fill="#e4f0fa"/>'
        b += L(ox + 2, 110, ox + 158, 110, BLUE, 1.5)
        b += f'<rect x="{ox+65}" y="35" width="30" height="190" fill="{scol}" stroke="{INK}" stroke-width="1.5"/>'
        for i in range(n):
            x = ox + 62 + random.random() * 36; y = 118 + random.random() * 105
            if random.random() < 0.5: x = ox + 60 + random.random() * 6 if random.random() < .5 else ox + 94 + random.random() * 6
            b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2 + random.random()*1.5:.1f}" fill="#7d8790"/>'
        b += T(ox + 80, 28, lab, 15, weight='bold')
        b += T(ox + 80, 275, caption, 13, color=MUTED)
    save(name, svg(w, h, b))

# ---------- صندوقا جسيمات (التركيز) ----------
def particle_boxes(name, na1, nb1, na2, nb2, w=520, h=250):
    random.seed(3)
    b = ''
    for k, (lab, na, nb) in enumerate([('(1)', na1, nb1), ('(2)', na2, nb2)]):
        ox = 40 + k * 250
        b += f'<rect x="{ox}" y="40" width="200" height="170" fill="#fff" stroke="{INK}" stroke-width="2.5" rx="6"/>'
        placed = []
        for col, n in ((BLUE, na), (RED, nb)):
            for _ in range(n):
                for _try in range(200):
                    x = ox + 18 + random.random() * 164; y = 58 + random.random() * 134
                    if all((x - a) ** 2 + (y - c) ** 2 > 26 ** 2 for a, c in placed): break
                placed.append((x, y))
                b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{col}" fill-opacity="0.85" stroke="{INK}" stroke-width="1"/>'
        b += T(ox + 100, 30, lab, 15, weight='bold')
    # مفتاح
    b += f'<circle cx="170" cy="232" r="7" fill="{BLUE}" stroke="{INK}" stroke-width="1"/>' + T(160, 237, 'جسيم من المادة A', 13, 'end', rtl=True)
    b += f'<circle cx="400" cy="232" r="7" fill="{RED}" stroke="{INK}" stroke-width="1"/>' + T(390, 237, 'جسيم من المادة B', 13, 'end', rtl=True)
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # توزيع طاقة الجسيمات عند درجتي حرارة
    distribution('c2-l2a-dist-T1T2.svg', [('T₁', 0.75, BLUE), ('T₂', 1.4, RED)], ea=3.4, note='T₂ > T₁')
    distribution('c2-l2a-dist-xy.svg', [('(س)', 0.75, BLUE), ('(ص)', 1.4, RED)], ea=3.4)
    # توزيع عند درجة حرارة واحدة مع طاقتي تنشيط (بمحفز ومن دونه)
    distribution('c2-l2a-dist-cat.svg', [('', 0.9, BLUE)], ea=3.8, ea_label='Ea دون محفز', extra_ea=[(2.2, 'Ea مع محفز')])
    # مخطط الطاقة: تفاعل طارد بمحفز ومن دونه
    R, P = 200, 265
    profile('c2-l2a-cat-profile.svg', R, P, [(60, RED, 'تفاعل غير محفز', (300, 50)), (125, BLUE, 'تفاعل محفز', (408, 145))],
            ea_arrows=[(172, 60, 'Ea غير محفز', RED, 'end'), (468, 125, 'Ea محفز', BLUE, 'start')])
    profile('c2-l2a-cat-12.svg', R, P, [(60, RED, '(1)', (300, 50)), (125, BLUE, '(2)', (300, 116))])
    profile('c2-l2a-cat-dh.svg', R, P, [(60, RED, 'دون محفز', (300, 50)), (125, BLUE, 'مع محفز', (408, 145))], dh_arrow=(470, 'ΔH'))
    # مثبط يرفع طاقة التنشيط
    profile('c2-l2a-inhib-profile.svg', 200, 265, [(125, BLUE, '(1)', (300, 116)), (55, PURPLE, '(2)', (300, 45))])
    # سرعة التفاعل ودرجة الحرارة
    rate_temp('c2-l2a-rate-temp.svg', [(290, 2), (310, 8), (320, 16), (330, 32)])
    rate_temp('c2-l2a-rate-temp-q.svg', [(290, 2), (300, 4), (310, 8), (320, 16)], labels=True, curve=False)
    # الإنزيمات ودرجة حرارة الجسم
    enzyme_curve('c2-l2a-enzyme-temp.svg')
    # مساحة السطح
    cubes2('c2-l2a-cubes.svg')
    # نشاط الفلزات مع نترات الفضة
    beakers('c2-l2a-beakers-xy.svg', '(س)', '(ص)', 14, 70)
    beakers('c2-l2a-beakers-zncu.svg', 'Zn', 'Cu', 70, 14, strip_cols=('#c9d3db', '#d88a4e'))
    # التركيز
    particle_boxes('c2-l2a-particles.svg', 4, 3, 4, 9)
