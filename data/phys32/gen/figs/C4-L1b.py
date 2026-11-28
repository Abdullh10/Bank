import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-1 (الأهداف O08–O13): المولد الكهربائي، ومنحنيات التيار والجهد والقدرة المتناوبة مع الزمن (كالشكل 4-8)،
# ودوران حلقة المولد في المجال (كالشكلين 4-6 و4-7)، وتجربة المحرك والمولد.
# اصطلاح الكتاب في الفصل الرابع: خطوط المجال خضراء، والتيار I قائم، والمجال B قائم، والسرعة v مائلة حمراء؛
# الحروف السفلية للقيم الفعّالة والعظمى عربية كما في الكتاب ص113 (I عظمى، I فعّال، P متوسطة).
import math

C_FIELD = '#1e8449'; WIRE = '#c8794a'; WIRE_D = '#9c5530'; MAG = '#c9d1dc'; MAG_D = '#5b6676'; CURVE = '#c0392b'

def C(name, w, h, body): save(name, svg(w, h, body))
def magnet(x, y, w, h, letter):
    return RECT(x, y, w, h, MAG_D, MAG, 2) + T(x + w / 2, y + h / 2 + 9, letter, 26, color=INK, weight='bold')
def num(x, y, n, lx, ly):
    return L(x, y, lx, ly, MUTED, 1.3) + f'<circle cx="{lx}" cy="{ly}" r="13" fill="#fff" stroke="{INK}" stroke-width="1.6"/>' + T(lx, ly + 5, str(n), 15, weight='bold')
def lamp(x, y, r=17):
    b = f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff7d6" stroke="{INK}" stroke-width="2"/>'
    b += f'<path d="M {x - r * 0.7} {y + r * 0.2} q {r * 0.35} {-r * 0.9} {r * 0.7} 0 q {r * 0.35} {r * 0.9} {r * 0.7} 0" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    return b

def axes(x0, y0, w, hup, hdown, xlab, ylab, size=14):
    """محوران: الأفقي (الزمن) عند y0 والرأسي من y0+hdown إلى y0-hup."""
    b = ARROW(x0, y0, x0 + w + 14, y0, INK, 2) + ARROW(x0, y0 + hdown, x0, y0 - hup - 12, INK, 2)
    b += T(x0 + w + 6, y0 + (hdown + 18 if hdown > 30 else 24), xlab, size) + T(x0 - 8, y0 - hup - 18, ylab, size, 'start')
    return b
def curve(fn, x0, x1, t0, t1, n=240, color=CURVE, w=3):
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        pts.append(f'{x0 + (x1 - x0) * i / n:.1f},{fn(t):.1f}')
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"/>'

def sine_graph(name, amp, yr, ystep, ylabel, tmax, tstep, tlabel='الزمن (ms)', period=20, extra_marks=(), dash_at=None, t_end=None, w=560, h=330):
    """منحنى جيبي x(t) = amp sin(2πt/period) بمحاور مرقّمة."""
    X, Y = None, None
    L0, R0, T0, B0 = 82, w - 30, 24, h - 46
    X = lambda t: L0 + t / tmax * (R0 - L0)
    Y = lambda v: B0 - (v - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    b = ''
    n = round((yr[1] - yr[0]) / ystep)
    for i in range(n + 1):
        v = yr[0] + i * ystep
        b += L(L0, Y(v), R0, Y(v), GRID, 1) + L(L0 - 5, Y(v), L0, Y(v), INK, 1.5) + T(L0 - 9, Y(v) + 4.5, fmt(round(v, 6)), 13, 'end', MUTED)
    m = round(tmax / tstep)
    for i in range(m + 1):
        t = i * tstep
        b += L(X(t), T0, X(t), B0, GRID, 1)
        if i: b += L(X(t), Y(0) - 4, X(t), Y(0) + 4, INK, 1.5) + T(X(t), Y(0) + 19 if yr[0] == 0 else B0 + 19, fmt(t), 13, color=MUTED)
    b += T(L0 - 9, Y(0) + 4.5 if yr[0] == 0 else Y(0) + 4.5, '', 13)
    b += ARROW(L0, Y(0), R0 + 16, Y(0), INK, 2) + ARROW(L0, B0, L0, T0 - 12, INK, 2)
    b += T(R0 - 10, h - 10, tlabel, 14) + T(22, (T0 + B0) / 2, ylabel, 14, rotate=-90)
    te = t_end if t_end is not None else tmax
    fn = lambda t: Y(amp(t) if callable(amp) else amp * math.sin(2 * math.pi * t / period))
    b += curve(fn, L0, X(te), 0, te)
    if dash_at is not None:
        v, lab = dash_at
        b += L(L0, Y(v), R0, Y(v), MUTED, 1.6, '7 5') + T(R0 - 4, Y(v) - 7, lab, 14, 'end', INK, 'bold')
    for t, v, s in extra_marks:
        b += DOT(X(t), Y(v), 5, INK) + T(X(t) + 10, Y(v) - 10 if v >= 0 else Y(v) + 22, s, 16, 'start', INK, 'bold')
    C(name, w, h, b)

# ───────── O08 مولد التيار المتناوب بأجزاء مرقّمة
def o08():
    b = magnet(30, 50, 110, 170, 'N') + magnet(420, 50, 110, 170, 'S')
    for yy in (75, 115, 155, 195):
        b += L(140, yy, 420, yy, C_FIELD, 1.8) + ARROW(380, yy, 400, yy, C_FIELD, 1.8, 10)
    b += T(398, 66, 'B', 17, color=C_FIELD)
    # الملف (حلقة مستطيلة) ومحور الدوران الرأسي
    b += f'<rect x="215" y="70" width="130" height="130" fill="none" stroke="{WIRE}" stroke-width="6"/>'
    b += L(280, 35, 280, 70, MUTED, 2, '6 4')
    # طرفا الملف ينزلان إلى الحلقتين
    b += L(268, 200, 268, 248, WIRE, 4) + L(292, 200, 292, 288, WIRE, 4)
    b += L(280, 200, 280, 330, MUTED, 3)  # المحور
    for yy in (250, 290):
        b += f'<ellipse cx="280" cy="{yy}" rx="30" ry="9" fill="#e6e9ee" stroke="#6d7480" stroke-width="5"/>'
    # الفرشاتان تلامسان الحلقتين من الجانبين
    b += RECT(226, 243, 22, 14, INK, '#3d3d3d', 1) + RECT(312, 283, 22, 14, INK, '#3d3d3d', 1)
    # الدائرة الخارجية والمصباح
    b += L(226, 250, 160, 250, INK, 2.2) + L(160, 250, 160, 360, INK, 2.2) + L(160, 360, 262, 360, INK, 2.2)
    b += lamp(280, 360) + L(298, 360, 400, 360, INK, 2.2) + L(400, 360, 400, 290, INK, 2.2) + L(400, 290, 334, 290, INK, 2.2)
    b += num(85, 220, 1, 85, 262) + num(345, 140, 2, 380, 240) + num(250, 290, 3, 210, 318) + num(237, 243, 4, 200, 215)
    C('c4l1-o08-generator.svg', 560, 400, b)

# ───────── O09 منحنيا التيار والجهد المتناوبين
def o09():
    sine_graph('c4l1-o09-igraph.svg', 4.0, (-6, 6), 2, 'التيار (A)', 40, 5)
    sine_graph('c4l1-o09-vgraph.svg', 325, (-400, 400), 100, 'الجهد (V)', 40, 5, dash_at=(325, '325'))

# ───────── O10 منحنى القدرة، ومنحنيا التيار والقدرة معًا
def o10():
    sine_graph('c4l1-o10-pgraph.svg', lambda t: 800 * math.sin(2 * math.pi * t / 20) ** 2, (0, 1000), 200, 'القدرة (W)', 40, 5)
    # منحنيان متراكبان بلا أرقام: التيار مع الزمن، والقدرة مع الزمن
    b = ''; x0, x1 = 70, 520
    for k, (y0, up, dn, lab, fn) in enumerate(((100, 65, 65, 'التيار', lambda t: math.sin(t)), (330, 110, 10, 'القدرة', lambda t: math.sin(t) ** 2))):
        b += axes(x0, y0, x1 - x0, up, dn, 'الزمن', lab)
        amp = 60 if k == 0 else 100
        b += curve(lambda t, y0=y0, fn=fn, amp=amp: y0 - amp * fn(t), x0, x1, 0, 4 * math.pi)
        b += T(x0 - 10, y0 + 5, '0', 13, 'end', MUTED)
    C('c4l1-o10-ivp.svg', 600, 370, b)

# ───────── O11 تجربة المحرك والمولد: محرك DC بمقبض يدوي موصول بمصباح وأميتر
def o11():
    b = f'<circle cx="150" cy="150" r="55" fill="#e6e9ee" stroke="{INK}" stroke-width="2.5"/>' + T(150, 156, 'محرك DC', 15, weight='bold')
    # المقبض اليدوي
    b += L(150, 150, 150, 150) + L(95, 150, 55, 150, INK, 5) + L(55, 150, 55, 115, INK, 5) + f'<circle cx="55" cy="108" r="8" fill="#8a5a2b" stroke="{INK}" stroke-width="1.5"/>'
    b += T(55, 85, 'مقبض', 14)
    # أسلاك الدائرة
    b += L(150, 95, 150, 50, INK, 2.2) + L(150, 50, 470, 50, INK, 2.2) + L(470, 50, 470, 250, INK, 2.2)
    b += L(150, 205, 150, 250, INK, 2.2) + L(150, 250, 300, 250, INK, 2.2)
    b += f'<circle cx="320" cy="250" r="18" fill="#fff" stroke="{INK}" stroke-width="2"/>' + T(320, 256, 'A', 17, italic=False)
    b += L(338, 250, 470, 250, INK, 2.2) + lamp(470, 150, 20)
    b = b.replace(L(470, 50, 470, 250, INK, 2.2), L(470, 50, 470, 130, INK, 2.2) + L(470, 170, 470, 250, INK, 2.2))
    b += T(510, 155, 'مصباح', 14, 'start')
    C('c4l1-o11-lab.svg', 580, 290, b)

# ───────── O12 دوران الحلقة
def o12():
    # (a) و(b) منظر علوي: الحلقة بين القطبين، مستواها موازٍ للمجال ثم عمودي عليه
    b = ''
    for k in range(2):
        ox = k * 330
        b += T(ox + 165, 26, '(a)' if k == 0 else '(b)', 17, weight='bold')
        b += magnet(ox + 15, 50, 60, 120, 'N') + magnet(ox + 255, 50, 60, 120, 'S')
        for yy in (70, 95, 125, 150): b += L(ox + 75, yy, ox + 255, yy, C_FIELD, 1.6) + ARROW(ox + 225, yy, ox + 240, yy, C_FIELD, 1.6, 9)
        cx, cy = ox + 165, 110
        if k == 0:
            b += f'<rect x="{cx - 55}" y="{cy - 7}" width="110" height="14" rx="6" fill="none" stroke="{WIRE}" stroke-width="5"/>'
        else:
            b += f'<rect x="{cx - 7}" y="{cy - 55}" width="14" height="110" rx="6" fill="none" stroke="{WIRE}" stroke-width="5"/>'
        b += DOT(cx, cy, 3, MUTED)
    b += T(330, 200, 'منظر علوي (المحور عمودي على الصفحة)', 14, color=MUTED)
    b += L(330, 15, 330, 180, GRID, 1.5)
    C('c4l1-o12-views.svg', 660, 215, b)
    # منحنى التيار مع الزمن ونقاط معلّمة
    A = 3.0
    sine_graph('c4l1-o12-points.svg', A, (-4, 4), 1, 'التيار (A)', 20, 2.5,
               extra_marks=((5, A, 'K'), (10, 0, 'M'), (15, -A, 'N'), (17.5, A * math.sin(2 * math.pi * 17.5 / 20), 'L')))
    # نصف دورة فقط من 0 إلى 10 ms، والمحور حتى 20 ms
    sine_graph('c4l1-o12-time.svg', 2.0, (-3, 3), 1, 'التيار (A)', 20, 2.5, t_end=10)
    # الحلقة abcd بين القطبين (كالشكل 4-7): الضلعان الطويلان ad وbc عموديان على الصفحة (منظر جانبي مقطعي)
    b = magnet(20, 60, 90, 200, 'N') + magnet(470, 60, 90, 200, 'S')
    for yy in (85, 125, 165, 205, 245): b += L(110, yy, 470, yy, C_FIELD, 1.6) + ARROW(430, yy, 448, yy, C_FIELD, 1.6, 9)
    b += T(452, 76, 'B', 17, color=C_FIELD)
    cx, cy = 290, 165; ang = math.radians(60); half = 85; thick = 22
    ux, uy = math.cos(ang), -math.sin(ang)          # اتجاه الضلع القصير (من المحور إلى أعلى يمين)
    px, py = -uy, ux                                # عمودي عليه (عرض الحلقة في المنظور)
    P = lambda s, t: (cx + s * half * ux + t * thick * px, cy + s * half * uy + t * thick * py)
    a_, b_, c_, d_ = P(-1, -1), P(1, -1), P(1, 1), P(-1, 1)
    b += f'<polygon points="{a_[0]:.1f},{a_[1]:.1f} {b_[0]:.1f},{b_[1]:.1f} {c_[0]:.1f},{c_[1]:.1f} {d_[0]:.1f},{d_[1]:.1f}" fill="none" stroke="{WIRE}" stroke-width="5"/>'
    b += DOT(cx, cy, 4, MUTED) + T(cx + 30, cy + 22, 'محور', 13, color=MUTED)
    for (x, y), s, dx, dy in ((b_, 'b', -14, -6), (c_, 'c', 12, -6), (a_, 'a', -14, 16), (d_, 'd', 14, 16)):
        b += T(x + dx, y + dy, s, 17, italic=False, weight='bold')
    C('c4l1-o12-loop.svg', 580, 300, b)

if __name__ == '__main__':
    o08(); o09(); o10(); o11(); o12()
