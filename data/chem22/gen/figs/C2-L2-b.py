# رسوم الدرس 2-2 (الجزء ب): منحنيات توزيع الطاقة، ومخططات الطاقة لتفاعل محفز وغير محفز،
# ومنحنى السرعة مع درجة الحرارة، ومنحنى عمل الإنزيم مع حرارة الجسم، وصناديق الجسيمات للتركيز.
# التشغيل: python3 data/chem22/gen/figs/C2-L2-b.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

ORANGE = '#c76a1a'; LBLUE = '#9cc3e6'; LRED = '#f2b8ae'


def axes_box(x0, y0, x1, y1, xlabel, ylabel):
    """محوران بسهمين: x0,y0 نقطة الأصل (أسفل يسار)."""
    b = ARROW(x0, y0, x1, y0) + ARROW(x0, y0, x0, y1)
    b += T((x0 + x1) / 2, y0 + 34, xlabel, 14, rtl=True)
    b += f'<text transform="translate({x0 - 22},{(y0 + y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">{esc(ylabel)}</text>'
    return b


def distribution(name, temps, ea_lines, labels=None, colors=None, note=None, shade=True, w=520, h=330, fills=None):
    """منحنى توزيع طاقة الجسيمات: f(E) = E/T² · e^(−E/T) (المساحة نفسها لكل منحنى).
    temps: قيم T النسبية، ea_lines: [(E, نص)]، labels: نص فوق كل منحنى."""
    X0, Y0, X1, Y1 = 70, h - 55, w - 30, 30
    Emax = 7.0
    fmax = max(1 / (math.e * t) for t in temps) * 1.12
    sx = lambda e: X0 + e / Emax * (X1 - X0 - 15)
    sy = lambda f: Y0 - f / fmax * (Y0 - Y1 - 10)
    f = lambda e, t: e / t ** 2 * math.exp(-e / t)
    colors = colors or [BLUE, RED, GREEN]
    fills = fills or [LBLUE, LRED, '#b9dfc9']
    b = ''
    if shade and ea_lines:
        ea = ea_lines[0][0]
        # الأعلى حرارة يُظلَّل أولًا (خلف) لأن ذيله أعلى
        order = sorted(range(len(temps)), key=lambda k: -temps[k])
        for k in order:
            t = temps[k]
            pts = [(sx(ea), sy(0))] + [(sx(ea + i * (Emax - ea) / 80), sy(f(ea + i * (Emax - ea) / 80, t))) for i in range(81)] + [(sx(Emax), sy(0))]
            b += f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fills[k]}" fill-opacity="0.85" stroke="none"/>'
    for k, t in enumerate(temps):
        pts = [(sx(i * Emax / 200), sy(f(i * Emax / 200, t))) for i in range(201)]
        b += f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{colors[k]}" stroke-width="3"/>'
        if labels:
            px, py = sx(t), sy(f(t, t))
            b += T(px, py - 10, labels[k], 15, color=colors[k], weight='bold')
    for e, txt in ea_lines:
        b += L(sx(e), Y1 + 5, sx(e), Y0, INK, 1.6, '6 4') + T(sx(e) + 6, Y1 + 30, txt, 14, 'start', INK, 'bold')
    b += axes_box(X0, Y0, X1, Y1 - 5, 'طاقة التصادم', 'عدد الجسيمات')
    b += T(X0 - 8, Y0 + 5, '0', 13, 'end')
    if note: b += T(X1 - 20, Y1 + 8, note, 15, 'end', INK, 'bold')
    save(name, svg(w, h, b))


def profile(name, react, prod, peaks, labels, colors=None, ticks=True, side_labels=('المتفاعلات', 'النواتج'), w=540, h=340, vmax=None):
    """مخطط طاقة لسير التفاعل بمسار أو أكثر (قيم بوحدة kJ). peaks: قمة كل مسار، labels: اسم كل مسار."""
    X0, Y0, X1, Y1 = 90, h - 50, w - 30, 25
    vmax = vmax or (max(peaks) + 40)
    vmin = 0
    sy = lambda v: Y0 - (v - vmin) / (vmax - vmin) * (Y0 - Y1 - 15)
    xa, xb = X0 + 25, X0 + 115          # مستوى المتفاعلات
    xc, xd = X1 - 125, X1 - 20          # مستوى النواتج
    xm = (xb + xc) / 2
    colors = colors or [RED, BLUE, GREEN]
    b = ''
    if ticks:
        step = 50
        for v in range(0, int(vmax) + 1, step):
            b += L(X0 - 5, sy(v), X0, sy(v)) + T(X0 - 9, sy(v) + 5, str(v), 13, 'end')
            if v: b += L(X0, sy(v), X1 - 10, sy(v), '#e3e7ee', 1)
    for k, pk in enumerate(peaks):
        # منحنى سلس: مستوى أفقي ثم قمة ثم مستوى
        hw = 70
        d = (f'M{xa},{sy(react):.1f} L{xb},{sy(react):.1f} '
             f'C{xb + 45},{sy(react):.1f} {xm - hw + 10},{sy(pk):.1f} {xm},{sy(pk):.1f} '
             f'C{xm + hw - 10},{sy(pk):.1f} {xc - 45},{sy(prod):.1f} {xc},{sy(prod):.1f} L{xd},{sy(prod):.1f}')
        b += f'<path d="{d}" fill="none" stroke="{colors[k]}" stroke-width="3.2"/>'
        ly = sy(pk) - 10 if k == 0 else sy(pk) + 24
        b += T(xm, ly, labels[k], 14, 'middle', colors[k], 'bold')
    b += T((xa + xb) / 2, sy(react) + (20 if react >= prod else -10), side_labels[0], 14)
    b += T((xc + xd) / 2, sy(prod) + (20 if prod > react else -10) if prod > react else sy(prod) + 20, side_labels[1], 14)
    b += ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1 - 5)
    b += T((X0 + X1) / 2, Y0 + 32, 'سير التفاعل', 14, rtl=True)
    b += f'<text transform="translate({X0 - 48},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">{esc("الطاقة (kJ)" if ticks else "الطاقة")}</text>'
    save(name, svg(w, h, b))


def rate_temp(name, pts, shown, w=500, h=330):
    """منحنى السرعة النسبية مع درجة الحرارة (K) تتضاعف كل 10 K. shown: النقاط التي تكتب إحداثياتها."""
    X0, Y0, X1, Y1 = 75, h - 55, w - 25, 25
    tmin, tmax, rmax = 280, 335, 36
    sx = lambda t: X0 + (t - tmin) / (tmax - tmin) * (X1 - X0 - 10)
    sy = lambda r: Y0 - r / rmax * (Y0 - Y1 - 10)
    b = ''
    for r in range(5, 36, 5):
        b += L(X0 - 5, sy(r), X0, sy(r)) + T(X0 - 9, sy(r) + 5, str(r), 13, 'end') + L(X0, sy(r), X1 - 10, sy(r), '#e3e7ee', 1)
    for t in range(280, 331, 10):
        b += L(sx(t), Y0, sx(t), Y0 + 5) + T(sx(t), Y0 + 20, str(t), 13)
        if t > 280: b += L(sx(t), Y0, sx(t), Y1 + 10, '#e3e7ee', 1)
    curve = [(sx(t), sy(2 * 2 ** ((t - 290) / 10))) for t in [283 + i * 0.5 for i in range(95)]]
    b += f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in curve)}" fill="none" stroke="{BLUE}" stroke-width="3"/>'
    for t, r in pts:
        b += f'<circle cx="{sx(t):.1f}" cy="{sy(r):.1f}" r="5" fill="{INK}"/>'
        if (t, r) in shown:
            b += T(sx(t) - 10, sy(r) - 10, f'({t} K, {r})', 13, 'end', INK, 'bold')
    b += ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1)
    b += T((X0 + X1) / 2, Y0 + 42, 'درجة الحرارة (K)', 14, rtl=True)
    b += f'<text transform="translate({X0 - 42},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">سرعة التفاعل النسبية</text>'
    save(name, svg(w, h, b))


def enzyme(name, w=500, h=320):
    """منحنى سرعة تفاعل إنزيمي مع درجة الحرارة (0–60 °C)، أعلى قيمة قرب 37–40 °C."""
    X0, Y0, X1, Y1 = 70, h - 55, w - 25, 25
    sx = lambda t: X0 + t / 62 * (X1 - X0 - 10)
    sy = lambda r: Y0 - r * (Y0 - Y1 - 20)
    def r(t):
        if t <= 37: return 1 - 0.92 * (1 - t / 37) ** 2
        return max(0.0, 1 - ((t - 37) / 23) ** 2)
    b = ''
    for t in range(0, 61, 10):
        b += L(sx(t), Y0, sx(t), Y0 + 5) + T(sx(t), Y0 + 20, str(t), 13)
    curve = [(sx(t), sy(r(t))) for t in [i * 0.25 for i in range(241)]]
    b += f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in curve)}" fill="none" stroke="{BLUE}" stroke-width="3"/>'
    b += L(sx(37), sy(r(37)), sx(37), Y0, MUTED, 1.4, '5 4') + T(sx(37), sy(r(37)) - 12, '37 °C', 13, color=MUTED, weight='bold')
    b += ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1)
    b += T((X0 + X1) / 2, Y0 + 42, 'درجة الحرارة (\u200e°C\u200e)', 14, rtl=True)
    b += f'<text transform="translate({X0 - 25},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">سرعة التفاعل</text>'
    save(name, svg(w, h, b))


def particle_boxes(name, boxes, w=560, h=230):
    """صناديق جسيمات A (دوائر زرقاء) وB (دوائر حمراء) في الحجم نفسه. boxes: [(label, nA, nB)]"""
    import random
    rnd = random.Random(7)
    n = len(boxes); bw = 150; gap = (w - n * bw) / (n + 1)
    b = ''
    for k, (lab, na, nb) in enumerate(boxes):
        x = gap + k * (bw + gap); y = 20
        b += f'<rect x="{x:.0f}" y="{y}" width="{bw}" height="150" fill="#fff" stroke="{INK}" stroke-width="2" rx="4"/>'
        placed = []
        for kind, cnt in (('A', na), ('B', nb)):
            for _ in range(cnt):
                for _try in range(400):
                    px = x + 20 + rnd.random() * (bw - 40); py = y + 20 + rnd.random() * 110
                    if all((px - qx) ** 2 + (py - qy) ** 2 > 34 ** 2 for qx, qy in placed): break
                placed.append((px, py))
                col = BLUE if kind == 'A' else RED
                b += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="13" fill="{col}" fill-opacity="0.9"/>' + T(px, py + 5, kind, 13, color='#fff', weight='bold')
        b += T(x + bw / 2, y + 180, lab, 16, weight='bold')
    b += T(w / 2, h - 6, 'الأوعية الثلاثة متساوية في الحجم ودرجة الحرارة', 13, color=MUTED)
    save(name, svg(w, h, b))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # توزيع الطاقة عند T1 وT2 (مثل الشكل 2-10)
    distribution('c2-l2b-dist-t1t2.svg', [1.0, 1.6], [(3.6, 'طاقة التنشيط')], labels=['T₁', 'T₂'], note='T₂ > T₁')
    # منحنيان (أ) و(ب) دون ذكر أيهما الأعلى حرارة
    distribution('c2-l2b-dist-ab.svg', [1.0, 1.6], [(3.6, 'Ea')], labels=['(أ)', '(ب)'], colors=[GREEN, ORANGE], fills=['#b9dfc9', '#f6cfa6'])
    # منحنى واحد وطاقتا تنشيط لتفاعلين X وY عند درجة الحرارة نفسها
    distribution('c2-l2b-dist-xy.svg', [1.2], [(2.4, 'Ea(X)'), (4.8, 'Ea(Y)')], labels=['T'], shade=False)
    # مخطط تفاعل طارد محفز وغير محفز بقيم
    profile('c2-l2b-cat-exo.svg', 100, 40, [250, 170], ['غير محفَّز', 'محفَّز'], vmax=280)
    # المساران (1) و(2) دون تسمية
    profile('c2-l2b-cat-12.svg', 100, 40, [250, 170], ['المسار (1)', 'المسار (2)'], colors=[GREEN, ORANGE], vmax=280)
    # تفاعل واحد دون محفز وبمحفزين A وB
    profile('c2-l2b-cat-ab.svg', 100, 40, [250, 190, 150], ['دون محفز', 'المحفز A', 'المحفز B'], vmax=280)
    # تفاعل ماص محفز وغير محفز
    profile('c2-l2b-cat-endo.svg', 50, 120, [230, 160], ['غير محفَّز', 'محفَّز'], vmax=260)
    # السرعة النسبية مع درجة الحرارة (نقاط الشكل 2-10)
    rate_temp('c2-l2b-rate-temp.svg', [(290, 2), (300, 4), (310, 8), (320, 16), (330, 32)], shown=[(290, 2), (300, 4), (310, 8)])
    # سرعة التفاعل الإنزيمي مع حرارة الجسم
    enzyme('c2-l2b-enzyme.svg')
    # صناديق الجسيمات للتركيز
    particle_boxes('c2-l2b-boxes.svg', [('(1)', 2, 2), ('(2)', 4, 2), ('(3)', 4, 4)])
