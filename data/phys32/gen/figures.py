# رسوم أسئلة فيزياء 3-2 (SVG ثابتة في public/qimg/phys32). خلفية بيضاء (تظهر كما هي في الوضع الليلي والطباعة).
# مكتبة أساسية: نص/خط/سهم، ومنحنى بياني بمحاور وشبكة، ومخطط الحركة (نموذج الجسيم النقطي)، ومتجهات على شبكة،
# ومخطط الجسم الحر، والسطح المائل. لا تعدّل هذا الملف أثناء الكتابة المتوازية؛ أضف دوالك في data/phys32/gen/figs/<LESSON>.py
import os, re, math
OUT = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'public', 'qimg', 'phys32')
INK = '#1f2a44'; MUTED = '#5b6676'; GRID = '#d9dee7'; BLUE = '#2a6fb0'; RED = '#b03a2e'; GREEN = '#1f7a4d'; ORANGE = '#c46a10'; PURPLE = '#6b3fa0'
SERIES = [BLUE, RED, GREEN, ORANGE, PURPLE]
# ألوان الكتاب الثابتة للمتجهات: القوة أزرق، السرعة أحمر، الإزاحة أخضر، التسارع بنفسجي
C_FORCE = '#1f5fa8'; C_VEL = '#c0392b'; C_DISP = '#1e8449'; C_ACC = '#7d3c98'
FONT = "font-family=\"'IBM Plex Sans Arabic','Noto Naskh Arabic',Tahoma,Arial,sans-serif\""
MATHFONT = "font-family=\"'Times New Roman',Times,serif\""

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def T(x, y, s, size=15, anchor='middle', color=INK, weight='normal', italic=False, rotate=None):
    """نص. anchor بالمعنى المرئي (start = الطرف الأيسر) ويُقلب تلقائيًا للعربي. الرموز اللاتينية تُكتب مائلة إن italic.
    الحروف السفلية: اكتب 'v_i' أو 'F_{g}' فتظهر منخفضة؛ و'^2' مرتفعة."""
    s = str(s); rtl = bool(re.search('[؀-ۿ]', s))
    if rtl and anchor in ('start', 'end'): anchor = 'end' if anchor == 'start' else 'start'
    d = ' direction="rtl"' if rtl else ''
    f = FONT if rtl else MATHFONT
    st = ' font-style="italic"' if italic and not rtl else ''
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ''
    body = ''
    for part in re.split(r'(_\{[^}]*\}|_[A-Za-z0-9]+|\^\{[^}]*\}|\^[0-9+\-−]+)', s):
        if not part: continue
        if part[0] in '_^':
            v = part[2:-1] if part[1] == '{' else part[1:]
            dy = 0.3 if part[0] == '_' else -0.45
            # الحرف السفلي الصغير المفرد (i، f، g) مائل كالكتاب، والكبير (N، T) والكلمة (net، sp) قائمة؛ ولا يُعرَّض
            fs = '' if (len(v) == 1 and v.isalpha() and v.islower()) else ' font-style="normal"'  # كالكتاب: v_i وF_g مائلان، وF_N وF_T قائمان
            body += f'<tspan dy="{dy}em" font-size="{int(size * 0.72)}" font-weight="normal"{fs}>{esc(v)}</tspan><tspan dy="{-dy}em"></tspan>'
        else: body += esc(part)
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}"{st} {f}{d}{tr}>{body}</text>'
def V(x, y, s, color=INK, size=17, anchor='middle'):
    """رمز كمية متجهة كما في الكتاب: خط عريض مائل (F_g، v_i، a). الكميات القياسية استعمل T(..., italic=True) بخط عادي."""
    return T(x, y, s, size, anchor, color, 'bold', True)
def L(x1, y1, x2, y2, color=INK, w=2, dash=''):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{da}/>'
def ARROW(x1, y1, x2, y2, color=INK, w=2.5, head=11):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.38), y2 - head * math.sin(a - 0.38)); p2 = (x2 - head * math.cos(a + 0.38), y2 - head * math.sin(a + 0.38))
    return L(x1, y1, x2 - 0.6 * head * math.cos(a), y2 - 0.6 * head * math.sin(a), color, w) + f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'
def DOT(x, y, r=5, color=INK, fill=None): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill or color}" stroke="{color}" stroke-width="1.5"/>'
def RECT(x, y, w, h, color=INK, fill='#eef2f8', sw=2, rot=None, cx=None, cy=None):
    tr = f' transform="rotate({rot} {cx} {cy})"' if rot is not None else ''
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" fill="{fill}" stroke="{color}" stroke-width="{sw}"{tr}/>'
def svg(w, h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<rect width="{w}" height="{h}" fill="#fff"/>\n{body}\n</svg>\n'
def save(name, s):
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(s); print(name)
def fmt(v):
    s = f'{v:g}'; return s.replace('-', '−')

def graph(name, series, xr, yr, xlabel, ylabel, xstep=None, ystep=None, w=520, h=360, grid=True, title=None,
          marks=(), labels=(), legend=None, dots=False, extra=''):
    """منحنى بياني. series = [ {pts:[(x,y),...], color?, label?, dash?, dots?} ]؛ xr/yr = (min,max) بوحدات المحور.
    marks = [(x, y, text)] نقاط معلّمة؛ labels = [(x, y, text, color)] نصوص بإحداثيات البيانات. المحور الأفقي عند y=0 إن كان ضمن المدى.
    xlabel/ylabel مثل 'الزمن t (s)' و'الموقع d (m)'. يعيد دالة تحويل (px, py) عبر graph.last للاستعمال في extra."""
    L0, R0, T0, B0 = 78, w - 26, 34 if title else 18, h - 52
    X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    graph.last = (X, Y)
    xs = xstep or (xr[1] - xr[0]) / 5; ys = ystep or (yr[1] - yr[0]) / 5
    b = ''
    def ticks(a, b_, st):
        n = round((b_ - a) / st); return [a + i * st for i in range(n + 1)]
    for x in ticks(xr[0], xr[1], xs):
        if grid: b += L(X(x), T0, X(x), B0, GRID, 1)
    for y in ticks(yr[0], yr[1], ys):
        if grid: b += L(L0, Y(y), R0, Y(y), GRID, 1)
    y0 = 0 if yr[0] <= 0 <= yr[1] else yr[0]
    b += ARROW(L0, Y(y0), R0 + 14, Y(y0), INK, 2) + ARROW(L0, B0, L0, T0 - 12, INK, 2)
    for x in ticks(xr[0], xr[1], xs):
        b += L(X(x), Y(y0), X(x), Y(y0) + 5, INK, 1.5) + T(X(x), (Y(y0) + 19) if y0 == yr[0] else B0 + 19, fmt(round(x, 6)), 13, color=MUTED)
    for y in ticks(yr[0], yr[1], ys):
        b += L(L0 - 5, Y(y), L0, Y(y), INK, 1.5) + T(L0 - 9, Y(y) + 4.5, fmt(round(y, 6)), 13, 'end', MUTED)
    b += T((L0 + R0) / 2, h - 12, xlabel, 14)
    b += T(20, (T0 + B0) / 2, ylabel, 14, rotate=-90)
    for k, s in enumerate(series):
        c = s.get('color', SERIES[k % len(SERIES)]); da = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
        pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in s['pts'])
        b += f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{s.get("w", 3)}" stroke-linejoin="round"{da}/>'
        if s.get('dots', dots): b += ''.join(DOT(X(x), Y(y), 4, c) for x, y in s['pts'])
        if s.get('label'):
            lx, ly = s.get('at', s['pts'][-1]); b += T(X(lx) + s.get('dx', 8), Y(ly) + s.get('dy', -8), s['label'], 15, 'start', c, 'bold')
    for x, y, t in marks: b += DOT(X(x), Y(y), 4.5) + (T(X(x) + 8, Y(y) - 8, t, 14, 'start') if t else '')
    for x, y, t, c in labels: b += T(X(x), Y(y), t, 14, 'middle', c, 'bold')
    if title: b += T(w / 2, 20, title, 15, weight='bold')
    save(name, svg(w, h, b + extra))
    return X, Y

def motion_diagram(name, rows, w=560, row_h=70, x0=40, x1=None, axis_label=None, origin=None, vel=False, acc=None, h=None):
    """مخطط الحركة بنموذج الجسيم النقطي. rows = [ {label?, xs:[px,...] (مواقع الصور بالبكسل من اليسار), color?, vel?: bool, acc?: '→'|'←'} ].
    vel يرسم متجهات السرعة بين النقاط المتتالية (طولها يتناسب مع المسافة)، وacc يرسم سهم تسارع فوق الصف."""
    x1 = x1 or w - 30; H = h or (len(rows) * row_h + (65 if axis_label else 40)); b = ''
    for i, r in enumerate(rows):
        y = 60 + i * row_h; c = r.get('color', INK)
        if r.get('label'): b += T(w - 10, y - 18, r['label'], 14, 'end', MUTED)
        for k, x in enumerate(r['xs']):
            b += DOT(x, y, 6, c)
            if (r.get('vel', vel)) and k + 1 < len(r['xs']) and r['xs'][k + 1] != x:
                b += ARROW(x, y - 16, x + 0.85 * (r['xs'][k + 1] - x), y - 16, C_VEL, 2.2, 9)
        if r.get('acc'):
            ax = (min(r['xs']) + max(r['xs'])) / 2; d = 40 if r['acc'] == '→' else -40
            b += ARROW(ax - d / 2, y - 36, ax + d / 2, y - 36, C_ACC, 2.5) + T(ax + d / 2 + (10 if d > 0 else -10), y - 31, 'a', 15, 'start' if d > 0 else 'end', C_ACC, 'bold', True)
    if axis_label:
        ya = H - 22; b += ARROW(x0, ya, x1, ya, INK, 1.8) + T(x1 + 2, ya - 8, axis_label, 14, 'end', italic=True)
        if origin is not None: b += L(origin, ya - 6, origin, ya + 6) + T(origin, ya + 18, '0', 13)
    save(name, svg(w, H, b))

def vectors(name, vecs, w=440, h=360, unit=40, origin=(220, 180), grid=True, axes=True, xl='x', yl='y', extra=''):
    """متجهات على شبكة. vecs = [ {from:(x,y) بوحدات الشبكة, to:(x,y), label, color?, dash?, lpos?:(dx,dy)} ]. المحور y لأعلى."""
    ox, oy = origin; P = lambda p: (ox + p[0] * unit, oy - p[1] * unit); b = ''
    if grid:
        for gx in range(-int(ox // unit), int((w - ox) // unit) + 1): b += L(ox + gx * unit, 0, ox + gx * unit, h, GRID, 1)
        for gy in range(-int(oy // unit), int((h - oy) // unit) + 1): b += L(0, oy + gy * unit, w, oy + gy * unit, GRID, 1)
    if axes: b += ARROW(8, oy, w - 8, oy, MUTED, 1.6) + ARROW(ox, h - 8, ox, 8, MUTED, 1.6) + T(w - 12, oy + 20, xl, 15, italic=True, color=MUTED) + T(ox + 14, 20, yl, 15, italic=True, color=MUTED)
    for v in vecs:
        (x1, y1), (x2, y2) = P(v['from']), P(v['to']); c = v.get('color', C_DISP)
        if v.get('dash'): b += L(x1, y1, x2, y2, c, 2, '6 5')
        else: b += ARROW(x1, y1, x2, y2, c, 3)
        dx, dy = v.get('lpos', (10, -10))
        if v.get('label'): b += T((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, v['label'], 17, 'middle', c, 'bold', True)
    save(name, svg(w, h, b + extra))

def fbd(name, forces, w=380, h=340, body='dot', body_label=None, axes=None, extra=''):
    """مخطط الجسم الحر. forces = [ {angle: درجات (0 = يمين، 90 = أعلى), length: px, label, color?} ]. body: 'dot' أو 'box'."""
    cx, cy = w / 2, h / 2; b = ''
    if axes: b += L(cx - 150, cy, cx + 150, cy, GRID, 1.5, '5 5') + L(cx, cy - 150, cx, cy + 150, GRID, 1.5, '5 5') + T(cx + 150, cy + 18, axes[0], 14, italic=True, color=MUTED) + T(cx + 12, cy - 140, axes[1], 14, 'start', MUTED, italic=True)
    b += RECT(cx - 26, cy - 22, 52, 44) if body == 'box' else DOT(cx, cy, 7)
    if body_label: b += T(cx, cy + 5, body_label, 14)
    for f in forces:
        a = math.radians(f['angle']); r0 = 0 if body == 'dot' else 26
        x1, y1 = cx + r0 * math.cos(a), cy - r0 * math.sin(a); x2, y2 = cx + (r0 + f['length']) * math.cos(a), cy - (r0 + f['length']) * math.sin(a)
        c = f.get('color', C_FORCE); b += ARROW(x1, y1, x2, y2, c, 3)
        lx, ly = cx + (r0 + f['length'] + 22) * math.cos(a), cy - (r0 + f['length'] + 22) * math.sin(a) + 6
        if f.get('label'): b += T(lx, ly, f['label'], 17, 'middle', c, 'bold', True)
    save(name, svg(w, h, b + extra))

def incline(name, angle=30, w=480, h=300, forces=(), angle_label='θ', box=True, extra=''):
    """سطح مائل بزاوية angle مع صندوق اختياري وقوى عليه: forces = [ {dir:'down'|'normal'|'up-slope'|'down-slope'|زاوية مطلقة, length, label, color?} ]."""
    a = math.radians(angle); x0, y0 = 40, h - 40; x1 = w - 40; y1 = y0 - (x1 - x0) * math.tan(a)
    if y1 < 20: y1 = 20; x1 = x0 + (y0 - y1) / math.tan(a)
    b = f'<polygon points="{x0},{y0} {x1:.1f},{y0} {x1:.1f},{y1:.1f}" fill="#f3efe6" stroke="{INK}" stroke-width="2"/>'
    # الزاوية عند القاعدة اليسرى
    b += f'<path d="M {x0 + 55} {y0} A 55 55 0 0 0 {x0 + 55 * math.cos(a):.1f} {y0 - 55 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.5"/>' + T(x0 + 70, y0 - 10, angle_label, 16, italic=True)
    mx, my = x0 + 0.55 * (x1 - x0), y0 - 0.55 * (x1 - x0) * math.tan(a)
    nx, ny = -math.sin(a), -math.cos(a)  # العمودي على السطح للخارج (لأعلى يسارًا)
    cx, cy = mx + 24 * nx, my + 24 * ny
    if box: b += RECT(cx - 28, cy - 24, 56, 48, rot=-angle, cx=cx, cy=cy)
    dirs = {'down': -90, 'normal': 90 + angle, 'up-slope': angle, 'down-slope': 180 + angle}
    for f in forces:
        d = math.radians(dirs.get(f['dir'], f['dir'])); c = f.get('color', C_FORCE)
        x2, y2 = cx + f['length'] * math.cos(d), cy - f['length'] * math.sin(d)
        b += ARROW(cx, cy, x2, y2, c, 3) + T(cx + (f['length'] + 20) * math.cos(d), cy - (f['length'] + 20) * math.sin(d) + 6, f.get('label', ''), 16, 'middle', c, 'bold', True)
    save(name, svg(w, h, b + extra))

if __name__ == '__main__':
    graph('_demo-graph.svg', [{'pts': [(0, 0), (2, 4), (4, 4), (6, 0)], 'label': 'A'}, {'pts': [(0, 6), (6, 2)], 'label': 'B', 'dash': '7 5'}],
          (0, 6), (0, 8), 'الزمن t (s)', 'الموقع d (m)', 1, 2)
    motion_diagram('_demo-motion.svg', [{'label': 'يتسارع', 'xs': [60, 90, 140, 210, 300, 410], 'vel': True, 'acc': '→'}, {'label': 'ساكن', 'xs': [250]}], axis_label='d')
    vectors('_demo-vec.svg', [{'from': (0, 0), 'to': (3, 0), 'label': 'A'}, {'from': (3, 0), 'to': (3, 2), 'label': 'B', 'color': GREEN, 'lpos': (16, 0)}, {'from': (0, 0), 'to': (3, 2), 'label': 'R', 'color': RED, 'lpos': (-14, -12)}], origin=(100, 260))
    fbd('_demo-fbd.svg', [{'angle': 90, 'length': 90, 'label': 'F_N'}, {'angle': -90, 'length': 90, 'label': 'F_g'}, {'angle': 0, 'length': 70, 'label': 'F_{appl}'}, {'angle': 180, 'length': 50, 'label': 'F_f'}], body='dot')
    incline('_demo-incline.svg', 30, forces=[{'dir': 'down', 'length': 90, 'label': 'F_g'}, {'dir': 'normal', 'length': 80, 'label': 'F_N'}, {'dir': 'up-slope', 'length': 60, 'label': 'F_f'}])
