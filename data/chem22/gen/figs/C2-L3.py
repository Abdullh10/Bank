# رسوم الدرس 2-3 (قوانين سرعة التفاعل): منحنيات السرعة الابتدائية مقابل التركيز.
# التشغيل: python3 data/chem22/gen/figs/C2-L3.py
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
import re

def ylabel(x, y, s, size=14):
    rtl = ' direction="rtl"' if re.search('[؀-ۿ]', s) else ''
    return f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="bold" {FONT}{rtl}>{esc(s)}</text>'

def fmt(v):
    s = f'{v:g}' if isinstance(v, (int, float)) else v
    return s

def rate_graph(name, series, xlabel, ylabel_txt, xmax, ymax, xticks=(), yticks=(), w=520, h=340,
               title=None, grid=True, guides=(), tick_fmt=None):
    """منحنى السرعة مقابل التركيز. series = [dict(f=دالة أو pts=[(x,y)], color, width, label, label_at=(x,y) بوحدات البيانات,
    markers=[x...], dash)]. guides = [(x, y)]: خطوط إرشادية متقطعة من النقطة إلى المحورين."""
    X0, Y0 = 95, h - 62; X1, Y1 = w - 30, 45 if title else 25
    px = lambda x: X0 + x / xmax * (X1 - X0)
    py = lambda y: Y0 - y / ymax * (Y0 - Y1)
    tf = tick_fmt or (lambda v: f'{v:.2f}' if isinstance(v, float) else str(v))
    b = ''
    if grid:
        for t in xticks: b += L(px(t), Y0, px(t), Y1, '#e3e7ee', 1)
        for t in yticks: b += L(X0, py(t), X1, py(t), '#e3e7ee', 1)
    b += ARROW(X0, Y0, X1 + 12, Y0) + ARROW(X0, Y0, X0, Y1 - 12)
    for t in xticks: b += L(px(t), Y0, px(t), Y0 + 5) + T(px(t), Y0 + 20, tf(t), 13)
    for t in yticks: b += L(X0 - 5, py(t), X0, py(t)) + T(X0 - 9, py(t) + 5, tf(t), 13, 'end')
    b += T(X0 - 9, Y0 + 18, '0', 13, 'end')
    b += T((X0 + X1) / 2, h - 12, xlabel, 14, weight='bold')
    b += ylabel(24, (Y0 + Y1) / 2, ylabel_txt)
    for gx, gy in guides:
        b += L(px(gx), py(gy), px(gx), Y0, MUTED, 1.2, '4 4') + L(px(gx), py(gy), X0, py(gy), MUTED, 1.2, '4 4')
    for s in series:
        if 'f' in s:
            pts = [(xmax * i / 200, s['f'](xmax * i / 200)) for i in range(201)]
            pts = [(x, y) for x, y in pts if y <= ymax * 1.0001]
        else:
            pts = s['pts']
        da = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
        if s.get('line', True):
            b += f'<polyline points="{" ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in pts)}" fill="none" stroke="{s.get("color", BLUE)}" stroke-width="{s.get("width", 3)}" stroke-linejoin="round"{da}/>'
        for mx in s.get('markers', []):
            my = s['f'](mx) if 'f' in s else dict(pts)[mx]
            b += f'<circle cx="{px(mx):.1f}" cy="{py(my):.1f}" r="5" fill="{s.get("color", BLUE)}" stroke="#fff" stroke-width="1.5"/>'
        if s.get('label'):
            lx, ly = s['label_at']
            b += T(px(lx), py(ly), s['label'], 15, s.get('anchor', 'middle'), s.get('color', BLUE), 'bold')
    if title: b += T(w / 2, 24, title, 15, weight='bold')
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # 1) تحلل H₂O₂ (رتبة أولى): خط مستقيم يمر بنقطة الأصل، k = 2.0×10⁻⁶ s⁻¹ (القيم الرأسية بوحدة 10⁻⁶ mol/L·s)
    rate_graph('c2-l3-h2o2-line.svg',
               [dict(f=lambda x: 2.0 * x, color=BLUE, markers=[0.5, 1.0, 1.5, 2.0, 2.5])],
               '[H₂O₂] (mol/L)', 'R (× 10⁻⁶ mol/L·s)', 3.0, 6.0,
               xticks=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0], yticks=[1, 2, 3, 4, 5, 6],
               tick_fmt=lambda v: f'{v:.1f}' if isinstance(v, float) else str(v))
    # 2) ثلاثة منحنيات بلا أرقام: (س) رتبة صفرية، (ص) رتبة أولى، (ع) رتبة ثانية
    rate_graph('c2-l3-three-curves.svg',
               [dict(f=lambda x: 1.2, color=GREEN, label='(س)', label_at=(9.3, 1.75)),
                dict(f=lambda x: 0.55 * x, color=BLUE, label='(ص)', label_at=(9.4, 4.0)),
                dict(f=lambda x: 0.085 * x * x, color=RED, label='(ع)', label_at=(8.4, 7.9))],
               '[A] (mol/L)', 'السرعة الابتدائية R', 10, 9, grid=False)
    # 3) نقاط تجريبية لتفاعل رتبته الثانية: R = k[A]²، k = 0.10 L/mol·s (القيم الرأسية بوحدة 10⁻³ mol/L·s)
    rate_graph('c2-l3-square-points.svg',
               [dict(f=lambda x: 100 * x * x, color=RED, markers=[0.10, 0.20, 0.30])],
               '[A] (mol/L)', 'R (× 10⁻³ mol/L·s)', 0.35, 10,
               xticks=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35], yticks=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
               guides=[(0.10, 1.0), (0.20, 4.0), (0.30, 9.0)])
    # 4) تفاعل واحد عند درجتي حرارة: T₂ > T₁ (المستقيم الأشد ميلًا عند T₂)
    rate_graph('c2-l3-k-temp.svg',
               [dict(f=lambda x: 0.35 * x, color=BLUE, label='T₁', label_at=(9.5, 2.3)),
                dict(f=lambda x: 0.80 * x, color=RED, label='T₂', label_at=(9.0, 8.0))],
               '[A] (mol/L)', 'السرعة الابتدائية R', 10, 9, grid=False)
    # 5) مستقيم يمر بالأصل للمادة A مع نقطتين مرقّمتين بقيمهما (رتبة أولى)، k = 0.040 s⁻¹
    rate_graph('c2-l3-first-k.svg',
               [dict(f=lambda x: 40 * x, color=BLUE, markers=[0.050, 0.150])],
               '[A] (mol/L)', 'R (× 10⁻³ mol/L·s)', 0.20, 8,
               xticks=[0.05, 0.10, 0.15, 0.20], yticks=[1, 2, 3, 4, 5, 6, 7, 8],
               guides=[(0.050, 2.0), (0.150, 6.0)])
