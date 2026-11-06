# رسوم الدرس 3-2 (العوامل المؤثرة في الاتزان الكيميائي — مبدأ لوتشاتلييه).
# التشغيل: python3 data/chem22/gen/figs/C3-L2.py
import sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

ORANGE = '#c76a1c'; PURPLE = '#6b4fa0'; BROWN = '#8a3b12'

def ylabel(x, y, s, size=14):
    rtl = ' direction="rtl"' if re.search('[؀-ۿ]', s) else ''
    return f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="bold" {FONT}{rtl}>{esc(s)}</text>'

def bisect(g, lo, hi, n=200):
    """جذر g في [lo, hi] بالتنصيف."""
    glo = g(lo)
    for _ in range(n):
        mid = (lo + hi) / 2
        if (g(mid) > 0) == (glo > 0): lo, glo = mid, g(mid)
        else: hi = mid
    return (lo + hi) / 2

def piece(before, jump, after, t1, tau, tmax, n=240):
    """نقاط منحنى تركيز: ثابت (before) حتى t1، ثم قفزة مفاجئة إلى jump، ثم اقتراب أسي من after."""
    pts = [(0, before), (t1, before)]
    for i in range(n + 1):
        t = t1 + (tmax - t1) * i / n
        pts.append((t, after + (jump - after) * math.exp(-(t - t1) / tau)))
    return pts

def graph(name, series, xlabel, ylabel_txt, xmax, ymax, events=(), w=540, h=340, yticks=(), legend_right=True, title=None, right=95):
    """رسم بياني عام: series = [dict(pts, color, label, dash, width, label_dy)]؛ events = [(t, نص)] خطوط رأسية متقطعة."""
    X0, Y0 = 80, h - 52; X1 = w - (right if legend_right else 25); Y1 = 42 if title else 22
    px = lambda x: X0 + x / xmax * (X1 - X0)
    py = lambda y: Y0 - y / ymax * (Y0 - Y1)
    b = ''
    for t in yticks: b += L(X0, py(t), X1, py(t), '#e3e7ee', 1) + L(X0 - 5, py(t), X0, py(t)) + T(X0 - 9, py(t) + 5, f'{t:g}', 12, 'end')
    b += ARROW(X0, Y0, X1 + 14, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    b += T((X0 + X1) / 2, h - 14, xlabel, 14, weight='bold')
    b += ylabel(26, (Y0 + Y1) / 2, ylabel_txt)
    for t, txt in events:
        b += L(px(t), Y0, px(t), Y1, MUTED, 1.3, '5 5') + T(px(t), Y0 + 20, txt, 14, weight='bold', color=MUTED)
    for s in series:
        pts = s['pts']
        da = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
        b += f'<polyline points="{" ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in pts)}" fill="none" stroke="{s["color"]}" stroke-width="{s.get("width", 3)}" stroke-linejoin="round"{da}/>'
        if s.get('label'):
            lx, ly = pts[-1]
            b += T(px(lx) + 8, py(ly) + 5 + s.get('label_dy', 0), s['label'], 14, 'start', s['color'], 'bold')
    if title: b += T(w / 2, 24, title, 15, weight='bold')
    save(name, svg(w, h, b))

# ---------- النظام العام A(g) + B(g) ⇌ C(g)، Keq = 5.0 ----------
K1 = 5.0
A0, B0 = 0.40, 0.30; C0 = K1 * A0 * B0          # 0.60
TM, T1, TAU = 10, 4, 1.1

def shift(a, b_, c):
    """حل الاتزان الجديد بعد القفزة: x موجبة = إزاحة نحو اليمين."""
    g = lambda x: (c + x) - K1 * (a - x) * (b_ - x)
    lo = -c + 1e-9; hi = min(a, b_) - 1e-9
    x = bisect(g, lo, hi)
    return a - x, b_ - x, c + x

def abc(name, a_j, b_j, c_j, ymax=1.0):
    a, b_, c = shift(a_j, b_j, c_j)
    S = [dict(pts=piece(A0, a_j, a, T1, TAU, TM), color=BLUE, label='[A]'),
         dict(pts=piece(B0, b_j, b_, T1, TAU, TM), color=GREEN, label='[B]'),
         dict(pts=piece(C0, c_j, c, T1, TAU, TM), color=RED, label='[C]')]
    # إبعاد التسميات المتقاربة
    ends = sorted([(s['pts'][-1][1], i) for i, s in enumerate(S)])
    for k in range(1, 3):
        (y0, i0), (y1, i1) = ends[k - 1], ends[k]
        if (y1 - y0) / ymax * 266 < 18: S[i1]['label_dy'] = -10; S[i0]['label_dy'] = 8
    graph(name, S, 'الزمن', 'التركيز (mol/L)', TM, ymax, events=[(T1, 't₁')], yticks=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2][: int(ymax / 0.2 + 0.01)])
    return a, b_, c

# ---------- N₂O₄(g) ⇌ 2NO₂(g) عند تقليل الحجم إلى النصف ----------
def volume_fig(name):
    K = 0.20 ** 2 / 0.40          # 0.10
    n0, d0 = 0.40, 0.20
    nj, dj = 2 * n0, 2 * d0
    x = bisect(lambda x: (dj - 2 * x) ** 2 - K * (nj + x), 0, dj / 2 - 1e-9)
    n1, d1 = nj + x, dj - 2 * x
    S = [dict(pts=piece(n0, nj, n1, T1, TAU, TM), color=BLUE, label='[N₂O₄]'),
         dict(pts=piece(d0, dj, d1, T1, TAU, TM), color=BROWN, label='[NO₂]')]
    graph(name, S, 'الزمن', 'التركيز (mol/L)', TM, 1.0, events=[(T1, 't₁')], yticks=[0.2, 0.4, 0.6, 0.8, 1.0], w=560)
    return n1, d1

# ---------- المحفز: تركيز الناتج مع الزمن ----------
def catalyst_fig(name):
    f = lambda t, tau: 0.60 * (1 - math.exp(-t / tau))
    S = [dict(pts=[(10 * i / 200, f(10 * i / 200, 2.4)) for i in range(201)], color=BLUE, label='دون محفز', label_dy=14),
         dict(pts=[(10 * i / 200, f(10 * i / 200, 0.7)) for i in range(201)], color=RED, dash='7 5', label='مع محفز', label_dy=-10)]
    graph(name, S, 'الزمن', 'تركيز الناتج (mol/L)', 10, 0.8, yticks=[0.2, 0.4, 0.6, 0.8], w=560)

# ---------- سرعتا التفاعلين الأمامي والعكسي ----------
def rates_fig(name):
    te, t1, tm = 3.0, 5.5, 10
    def fwd(t):
        if t < t1: return 2.0 + 4.0 * math.exp(-t / 0.9)
        return 2.8 + (4.6 - 2.8) * math.exp(-(t - t1) / 0.9)
    def rev(t):
        if t < t1: return 2.0 * (1 - math.exp(-t / 0.9))
        return 2.8 - (2.8 - 2.0) * math.exp(-(t - t1) / 0.9)
    ts = [tm * i / 300 for i in range(301)]
    fp = [(t, fwd(t)) for t in ts if t < t1] + [(t1, fwd(t1 - 1e-9)), (t1, fwd(t1))] + [(t, fwd(t)) for t in ts if t > t1]
    rp = [(t, rev(t)) for t in ts if t < t1] + [(t1, rev(t1))] + [(t, rev(t)) for t in ts if t > t1]
    S = [dict(pts=fp, color=BLUE, label='السرعة الأمامية', label_dy=-12), dict(pts=rp, color=RED, dash='7 5', label='السرعة العكسية', label_dy=14)]
    graph(name, S, 'الزمن', 'سرعة التفاعل', tm, 6.5, events=[(t1, 't₁')], w=640, right=150)

# ---------- أنبوبا N₂O₄/NO₂ في حمامين مائيين ----------
def tubes_fig(name):
    w, h = 520, 340
    b = ''
    def setup(cx, bath_col, bath_lab, tube_col, num):
        s = ''
        # الكأس والماء
        s += f'<rect x="{cx - 85}" y="{150}" width="170" height="130" rx="8" fill="{bath_col}" stroke="none"/>'
        s += f'<path d="M {cx - 90} 110 L {cx - 90} 282 Q {cx - 90} 292 {cx - 80} 292 L {cx + 80} 292 Q {cx + 90} 292 {cx + 90} 282 L {cx + 90} 110" fill="none" stroke="{INK}" stroke-width="2.5"/>'
        # الأنبوب
        s += f'<rect x="{cx - 17}" y="60" width="34" height="200" rx="16" fill="{tube_col}" stroke="{INK}" stroke-width="2"/>'
        s += f'<rect x="{cx - 21}" y="46" width="42" height="18" rx="3" fill="#7a7f87" stroke="{INK}" stroke-width="1.5"/>'
        s += T(cx, 34, f'الأنبوب ({num})', 15, weight='bold')
        s += T(cx, 308, bath_lab[0], 14, weight='bold') + T(cx, 326, bath_lab[1], 14, weight='bold')
        return s
    b += setup(140, '#d6ecfa', ('حمام ماء مثلج', '0 °C'), '#efe3c4', 1)
    b += setup(380, '#fbd9cf', ('حمام ماء ساخن', '80 °C'), '#7a3110', 2)
    save(name, svg(w, h, b))

# ---------- صندوقا جسيمات N₂O₄ وNO₂ ----------
def boxes_fig(name):
    w, h = 560, 330
    def no2(x, y):
        return f'<circle cx="{x}" cy="{y}" r="9" fill="{BROWN}" stroke="{INK}" stroke-width="1"/>'
    def n2o4(x, y):
        return f'<circle cx="{x - 8}" cy="{y}" r="9" fill="#fff" stroke="{INK}" stroke-width="1.5"/><circle cx="{x + 8}" cy="{y}" r="9" fill="#fff" stroke="{INK}" stroke-width="1.5"/>'
    def box(ox, lab, dimers, monos):
        s = f'<rect x="{ox}" y="40" width="220" height="200" rx="6" fill="#fafbfd" stroke="{INK}" stroke-width="2.5"/>' + T(ox + 110, 28, lab, 16, weight='bold')
        for x, y in dimers: s += n2o4(ox + x, 40 + y)
        for x, y in monos: s += no2(ox + x, 40 + y)
        return s
    b = box(20, '(س)', [(40, 35), (150, 30), (90, 90), (180, 110), (45, 150), (140, 165)], [(110, 140), (190, 60)])
    b += box(320, '(ص)', [(60, 60), (150, 150)], [(30, 25), (120, 30), (190, 35), (100, 95), (180, 95), (35, 115), (40, 175), (105, 175), (190, 175), (150, 75)])
    # مفتاح الرموز
    b += n2o4(330, 278) + T(352, 283, 'جزيء N₂O₄ (عديم اللون)', 14, 'start')
    b += no2(90, 278) + T(108, 283, 'جزيء NO₂ (بني)', 14, 'start')
    save(name, svg(w, h, b))

# ---------- الضغط الجزئي للأكسجين مقابل الارتفاع ----------
def altitude_fig(name):
    f = lambda km: 159 * math.exp(-km / 7.6)
    S = [dict(pts=[(9 * i / 90, f(9 * i / 90)) for i in range(91)], color=BLUE)]
    w, h = 520, 330
    X0, Y0, X1, Y1 = 80, h - 52, w - 30, 22
    px = lambda x: X0 + x / 10 * (X1 - X0); py = lambda y: Y0 - y / 180 * (Y0 - Y1)
    b = ''
    for t in (20, 40, 60, 80, 100, 120, 140, 160): b += L(X0, py(t), X1, py(t), '#e3e7ee', 1) + L(X0 - 5, py(t), X0, py(t)) + T(X0 - 9, py(t) + 5, str(t), 12, 'end')
    for t in (2, 4, 6, 8, 10): b += L(px(t), Y0, px(t), Y0 + 5) + T(px(t), Y0 + 19, str(t), 12)
    b += T(X0 - 9, Y0 + 18, '0', 12, 'end')
    b += ARROW(X0, Y0, X1 + 12, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    b += T((X0 + X1) / 2, h - 10, 'الارتفاع عن سطح البحر (km)', 14, weight='bold')
    b += ylabel(24, (Y0 + Y1) / 2, 'الضغط الجزئي للأكسجين (mmHg)')
    pts = S[0]['pts']
    b += f'<polyline points="{" ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in pts)}" fill="none" stroke="{BLUE}" stroke-width="3"/>'
    for km, lab, dx, anc in ((0, 'مستوى سطح البحر', 10, 'start'), (8.8, 'قمة إفرست', -6, 'end')):
        b += f'<circle cx="{px(km):.1f}" cy="{py(f(km)):.1f}" r="5" fill="{RED}"/>' + T(px(km) + dx, py(f(km)) + (24 if km else -10), lab, 13, anc, RED, 'bold')
    save(name, svg(w, h, b))
    return f(0), f(8.8)

# ---------- Keq مقابل درجة الحرارة ----------
def keq_t_fig(name, data):
    w, h = 520, 320
    X0, Y0, X1, Y1 = 80, h - 52, w - 30, 22
    tmin, tmax, kmax = 250, 650, 10
    px = lambda x: X0 + (x - tmin) / (tmax - tmin) * (X1 - X0); py = lambda y: Y0 - y / kmax * (Y0 - Y1)
    b = ''
    for t in (2, 4, 6, 8, 10): b += L(X0, py(t), X1, py(t), '#e3e7ee', 1) + L(X0 - 5, py(t), X0, py(t)) + T(X0 - 9, py(t) + 5, str(t), 12, 'end')
    for t, _ in data: b += L(px(t), Y0, px(t), Y0 + 5) + T(px(t), Y0 + 19, str(t), 12)
    b += ARROW(X0, Y0, X1 + 12, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    b += T((X0 + X1) / 2, h - 10, 'درجة الحرارة (K)', 14, weight='bold')
    b += ylabel(30, (Y0 + Y1) / 2, 'Keq')
    b += f'<polyline points="{" ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in data)}" fill="none" stroke="{PURPLE}" stroke-width="3"/>'
    for x, y in data: b += f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="5.5" fill="{PURPLE}" stroke="#fff" stroke-width="1.5"/>' + T(px(x) + 9, py(y) - 9, f'{y:g}', 13, 'start', PURPLE, 'bold')
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    print('add A ->', abc('c3-l2-add-a.svg', 0.80, B0, C0))
    print('remove C ->', abc('c3-l2-remove-c.svg', A0, B0, 0.20))
    print('add C ->', abc('c3-l2-add-c.svg', A0, B0, 1.10, ymax=1.2))
    print('remove A ->', abc('c3-l2-remove-a.svg', 0.15, B0, C0))
    # تغير تدريجي دون قفزة (رفع درجة الحرارة لتفاعل طارد): يقل Keq إلى 2.0
    K2 = 2.0
    x = bisect(lambda x: (C0 - x) - K2 * (A0 + x) * (B0 + x), 0, C0)
    S = [dict(pts=piece(A0, A0, A0 + x, T1, 1.4, TM), color=BLUE, label='[A]', label_dy=-12),
         dict(pts=piece(B0, B0, B0 + x, T1, 1.4, TM), color=GREEN, label='[B]', label_dy=12),
         dict(pts=piece(C0, C0, C0 - x, T1, 1.4, TM), color=RED, label='[C]', label_dy=-3)]
    graph('c3-l2-temp.svg', S, 'الزمن', 'التركيز (mol/L)', TM, 1.0, events=[(T1, 't₁')], yticks=[0.2, 0.4, 0.6, 0.8, 1.0])
    print('temp ->', A0 + x, B0 + x, C0 - x)
    print('volume ->', volume_fig('c3-l2-volume.svg'))
    catalyst_fig('c3-l2-catalyst.svg')
    rates_fig('c3-l2-rates.svg')
    tubes_fig('c3-l2-tubes.svg')
    boxes_fig('c3-l2-boxes.svg')
    print('altitude ->', altitude_fig('c3-l2-altitude.svg'))
    keq_t_fig('c3-l2-keq-t.svg', [(300, 8.6), (400, 3.9), (500, 2.0), (600, 1.1)])
