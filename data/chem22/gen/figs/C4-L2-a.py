# رسوم الدرس 4-2 (الألكانات): صيغ بنائية كاملة ومكثفة وحلقية، وبرج تقطير مبسط، وطبقتا ماء وهكسان، ومنحنى درجات الغليان.
# التشغيل: python3 data/chem22/gen/figs/C4-L2-a.py
import sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

U = 50          # طول الرابطة (بين مراكز الذرات) بالبكسل
FS = 19         # حجم خط رموز الذرات
SUB = '₀₁₂₃₄₅₆₇₈₉'

def lab_size(s, fs=FS):
    """نصف العرض ونصف الارتفاع التقريبيان لنص رمز/مجموعة ذرية."""
    if not s: return 0, 0
    w = sum(0.40 * fs if ch in SUB else 0.66 * fs for ch in s)
    return w / 2, 0.42 * fs

def mol(nodes, edges, ox=0, oy=0, fs=FS, marks=()):
    """يرسم جزيئًا. nodes = {id: (x, y, label)} بوحدات طول الرابطة (y للأسفل)، label فارغ = رأس في الصيغة الخطية.
    edges = [(a, b, order)]. marks = [(x, y, text, color, size)] بوحدات الطول (أرقام الترقيم مثلًا).
    يعيد (body, (xmin, ymin, xmax, ymax)) بالبكسل بعد الإزاحة ox, oy."""
    P = {k: (ox + x * U, oy + y * U, s) for k, (x, y, s) in nodes.items()}
    b = ''
    for a, c, order in edges:
        x1, y1, s1 = P[a]; x2, y2, s2 = P[c]
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
        def trim(s):
            hw, hh = lab_size(s, fs)
            if not s: return 0
            return min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) + 4
        t1, t2 = trim(s1), trim(s2)
        ax, ay, bx, by = x1 + ux * t1, y1 + uy * t1, x2 - ux * t2, y2 - uy * t2
        offs = {1: [0], 2: [-3.5, 3.5], 3: [-5, 0, 5]}[order]
        for o in offs:
            b += L(round(ax - uy * o, 1), round(ay + ux * o, 1), round(bx - uy * o, 1), round(by + ux * o, 1), INK, 2)
    xs, ys = [], []
    for k, (x, y, s) in P.items():
        hw, hh = lab_size(s, fs)
        if s: b += T(round(x, 1), round(y + 0.36 * fs, 1), s, fs)
        xs += [x - hw, x + hw]; ys += [y - hh, y + hh]
    for (x, y, s, col, size) in marks:
        X, Y = ox + x * U, oy + y * U
        b += T(round(X, 1), round(Y + 0.36 * size, 1), s, size, color=col, weight='bold')
        xs += [X - 8, X + 8]; ys += [Y - 8, Y + 8]
    return b, (min(xs), min(ys), max(xs), max(ys))

def shift(nodes, edges, dx, dy):
    return {k: (x + dx, y + dy, s) for k, (x, y, s) in nodes.items()}, edges

# ---------- منشئات البنى ----------
def cond(main, branches=(), dx=1.3):
    """صيغة بنائية مكثفة: main قائمة مجموعات أفقية، branches = [(index, dir(-1 أعلى/+1 أسفل), [labels...])]."""
    nodes = {f'm{i}': (i * dx, 0, s) for i, s in enumerate(main)}
    edges = [(f'm{i}', f'm{i+1}', 1) for i in range(len(main) - 1)]
    for j, (i, d, labs) in enumerate(branches):
        prev = f'm{i}'
        for k, s in enumerate(labs, 1):
            nid = f'b{j}_{k}'; nodes[nid] = (i * dx, d * k, s); edges.append((prev, nid, 1)); prev = nid
    return nodes, edges

def full(carbons, cbonds):
    """صيغة بنائية كاملة على شبكة: carbons = {id: (col, row)} أعداد صحيحة، cbonds = [(a, b)] بين ذرات متجاورة.
    تُضاف ذرات H في كل اتجاه شاغر من الاتجاهات الأربعة."""
    nodes = {k: (x, y, 'C') for k, (x, y) in carbons.items()}
    edges = [(a, b, 1) for a, b in cbonds]
    occ = {(x, y) for x, y in carbons.values()}
    nb = {k: set() for k in carbons}
    for a, b in cbonds:
        (xa, ya), (xb, yb) = carbons[a], carbons[b]
        sg = lambda v: (v > 0) - (v < 0)
        nb[a].add((sg(xb - xa), sg(yb - ya))); nb[b].add((sg(xa - xb), sg(ya - yb)))
    hpos = set(); n = 0
    for k, (x, y) in carbons.items():
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if d in nb[k]: continue
            p = (x + d[0], y + d[1])
            assert p not in occ and p not in hpos, f'تصادم ذرة H عند {p}'
            hpos.add(p); n += 1; hid = f'h{n}'
            nodes[hid] = (p[0], p[1], 'H'); edges.append((k, hid, 1))
    return nodes, edges

def zigzag(n):
    """رؤوس سلسلة خطية متعرجة (صيغة هيكلية خطية)."""
    return [(i * 0.866, 0 if i % 2 == 0 else -0.5) for i in range(n)]

def ring(n, subs=None, numbers=None, cx=0, cy=0, rot=None, rev_left=True):
    """حلقة بصيغة خطية (مضلع منتظم طول ضلعه 1). subs = {vertex: label}، numbers = {vertex: '1'} أرقام داخل الحلقة.
    الرأس 0 في الأعلى ثم مع عقارب الساعة."""
    subs = subs or {}; numbers = numbers or {}
    R = 0.5 / math.sin(math.pi / n)
    rot = -math.pi / 2 if rot is None else rot
    if n == 4 and rot == -math.pi / 2: rot = -math.pi * 3 / 4   # المربع قائم الأضلاع
    V = [(cx + R * math.cos(rot + 2 * math.pi * i / n), cy + R * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    nodes = {f'r{i}': (x, y, '') for i, (x, y) in enumerate(V)}
    edges = [(f'r{i}', f'r{(i + 1) % n}', 1) for i in range(n)]
    marks = []
    for i, s in subs.items():
        x, y = V[i]; ux, uy = x - cx, y - cy; d = math.hypot(ux, uy); ux, uy = ux / d, uy / d
        if rev_left and ux < -0.3 and s.startswith('CH₂') and len(s) > 3:   # يُكتب CH₃CH₂ على الجهة اليسرى
            parts = re.findall(r'CH[₂₃]?', s); s = ''.join(reversed(parts))
        hw, hh = lab_size(s)
        t = min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) / U
        L0 = 0.75
        nodes[f's{i}'] = (x + ux * (L0 + t), y + uy * (L0 + t), s)
        edges.append((f'r{i}', f's{i}', 1))
    for i, s in numbers.items():
        x, y = V[i]; ux, uy = cx - x, cy - y; d = math.hypot(ux, uy)
        marks.append((x + ux / d * 0.32, y + uy / d * 0.32, s, RED, 15))
    # الرابطة إلى المجموعة البديلة تبدأ من الرأس نفسه (لا تقص عند الرأس)
    return nodes, edges, marks

def panels(name, items, gap=50, label_gap=34, pad=22, title=None):
    """عدة بنى جنبًا إلى جنب، تحت كل منها عنوانها. items = [(caption, nodes, edges, marks)]."""
    parts = []
    for cap, nodes, edges, marks in items:
        _, bb = mol(nodes, edges, 0, 0, marks=marks)
        parts.append((cap, nodes, edges, marks, bb))
    hmax = max(bb[3] - bb[1] for *_, bb in parts)
    top = pad + (30 if title else 0)
    x = pad; body = ''
    for cap, nodes, edges, marks, bb in parts:
        w = bb[2] - bb[0]; h = bb[3] - bb[1]
        oy = top + (hmax - h) / 2 - bb[1]
        bd, bb2 = mol(nodes, edges, x - bb[0], oy, marks=marks)
        body += bd
        if cap: body += T(round(x + w / 2, 1), round(top + hmax + label_gap, 1), cap, 17, weight='bold')
        x += w + gap
    W = x - gap + pad; H = top + hmax + (label_gap + 14 if any(p[0] for p in parts) else 0) + pad
    if title: body = T(W / 2, pad + 6, title, 16, weight='bold') + body
    save(name, svg(round(W), round(H), body))

def grid_panels(name, items, cols=2, pad=22, gapx=60, gapy=30, label_gap=30):
    """مثل panels لكن في شبكة صفوف وأعمدة."""
    parts = []
    for cap, nodes, edges, marks in items:
        _, bb = mol(nodes, edges, 0, 0, marks=marks); parts.append((cap, nodes, edges, marks, bb))
    cw = max(bb[2] - bb[0] for *_, bb in parts); ch = max(bb[3] - bb[1] for *_, bb in parts)
    rows = (len(parts) + cols - 1) // cols
    body = ''
    for k, (cap, nodes, edges, marks, bb) in enumerate(parts):
        r, c = divmod(k, cols)
        c = cols - 1 - c                      # الترتيب من اليمين إلى اليسار (أ في اليمين)
        x0 = pad + c * (cw + gapx); y0 = pad + r * (ch + label_gap + 14 + gapy)
        w = bb[2] - bb[0]; h = bb[3] - bb[1]
        bd, _ = mol(nodes, edges, x0 + (cw - w) / 2 - bb[0], y0 + (ch - h) / 2 - bb[1], marks=marks)
        body += bd + T(round(x0 + cw / 2, 1), round(y0 + ch + label_gap, 1), cap, 17, weight='bold')
    W = pad * 2 + cols * cw + (cols - 1) * gapx; H = pad * 2 + rows * (ch + label_gap + 14) + (rows - 1) * gapy
    if cols > 1:
        for c in range(1, cols):
            xl = pad + c * (cw + gapx) - gapx / 2; body += L(round(xl, 1), pad, round(xl, 1), round(H - pad, 1), MUTED, 1, '4 4')
    save(name, svg(round(W), round(H), body))

def single(name, nodes, edges, marks=(), pad=24):
    _, bb = mol(nodes, edges, 0, 0, marks=marks)
    bd, _ = mol(nodes, edges, pad - bb[0], pad - bb[1], marks=marks)
    save(name, svg(round(bb[2] - bb[0] + 2 * pad), round(bb[3] - bb[1] + 2 * pad), bd))

def R(n, subs=None, numbers=None, **kw):
    nodes, edges, marks = ring(n, subs, numbers, **kw); return nodes, edges, marks

# ---------- رسوم خاصة ----------
def tower(name):
    """برج تقطير تجزيئي مبسط: أربع مشتقات مرمزة (أ–د) بمدى درجات حرارة تكثفها، والنفط الخام يدخل من الأسفل."""
    W, H = 560, 420
    b = f'<rect x="230" y="40" width="110" height="330" rx="10" fill="#eef3f8" stroke="{INK}" stroke-width="2.5"/>'
    for y in (110, 180, 250, 320): b += L(232, y, 338, y, MUTED, 1.2, '5 4')
    b += T(285, 30, 'أعلى البرج: أبرد', 13, color=BLUE) + T(285, 392, 'أسفل البرج: الأسخن', 13, color=RED)
    # النفط الخام
    b += ARROW(120, 345, 228, 345, '#8a3b12') + T(115, 340, 'بخار النفط الخام', 14, 'end')
    # (د) مخرج زيت التزييت «فوق 300°C» بدل مدى زيت التسخين 240–300°C الذي يتداخل في الكتاب مع مدى الكيروسين
    rows = [(75, '(أ)', None), (145, '(ب)', '40 – 100°C'), (215, '(ج)', '105 – 275°C'), (285, '(د)', 'over')]
    for y, lab, rng in rows:
        b += ARROW(340, y, 420, y, BLUE) + T(430, y + 6, lab, 17, 'start', INK, 'bold')
        if rng is None: b += T(470, y + 6, '40°C', 14, 'start', MUTED) + T(552, y + 6, 'أقل من', 14, 'end', MUTED)
        elif rng == 'over': b += T(470, y + 6, '300°C', 14, 'start', MUTED) + T(552, y + 6, 'فوق', 14, 'end', MUTED)
        else: b += T(470, y + 6, rng, 14, 'start', MUTED)
    b += ARROW(340, 355, 420, 355, MUTED) + T(430, 361, 'المخلفات', 14, 'start', MUTED)
    save(name, svg(W, H, b))

def layers(name):
    """كأس فيها طبقتان: هكسان (أعلى) وماء (أسفل)."""
    W, H = 360, 300
    b = f'<path d="M110 40 L110 250 Q110 270 130 270 L230 270 Q250 270 250 250 L250 40" fill="none" stroke="{INK}" stroke-width="3"/>'
    b += f'<rect x="112" y="170" width="136" height="98" fill="#cfe3f5"/>' + f'<rect x="112" y="110" width="136" height="60" fill="#fbefc4"/>'
    b += L(112, 170, 248, 170, INK, 1.5)
    b += L(250, 140, 280, 140, MUTED, 1) + T(285, 145, 'هكسان', 15, 'start')
    b += L(250, 220, 280, 220, MUTED, 1) + T(285, 225, 'ماء', 15, 'start')
    # إعادة رسم الحواف فوق التعبئة
    b += f'<path d="M110 40 L110 250 Q110 270 130 270 L230 270 Q250 270 250 250 L250 40" fill="none" stroke="{INK}" stroke-width="3"/>'
    save(name, svg(W, H, b))

def bp_graph(name, pts):
    """منحنى درجة الغليان مقابل عدد ذرات الكربون للألكانات المستقيمة."""
    W, H = 540, 360
    X0, Y0, X1, Y1 = 90, 300, 510, 30
    def px(n): return X0 + (n - 0) / 9 * (X1 - X0 - 20)
    def py(t): return Y0 - (t + 200) / 350 * (Y0 - Y1)
    b = ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1)
    for t in (-200, -150, -100, -50, 0, 50, 100, 150):
        b += L(X0 - 5, py(t), X0, py(t)) + T(X0 - 9, py(t) + 5, str(t).replace('-', '−'), 13, 'end')
        if t == 0: b += L(X0, py(0), X1 - 10, py(0), MUTED, 1, '4 4')
    for n in range(1, 9):
        b += L(px(n), Y0, px(n), Y0 + 5) + T(px(n), Y0 + 21, str(n), 13)
    b += T((X0 + X1) / 2, H - 8, 'عدد ذرات الكربون في الجزيء', 14, weight='bold')
    b += f'<text transform="translate({X0 - 55},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">درجة الغليان</text>' + T(X0 + 8, Y1 + 5, '°C', 13, 'start', INK, 'bold')
    b += f'<polyline points="{" ".join(f"{px(n):.1f},{py(t):.1f}" for n, t, _ in pts)}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>'
    for n, t, lab in pts:
        b += f'<circle cx="{px(n):.1f}" cy="{py(t):.1f}" r="5" fill="{BLUE}"/>'
        X = px(n) + (45 if n == 1 else -42)
        b += T(round(X, 1), round(py(t) - 20, 1), lab, 13, 'middle', INK) + T(round(X, 1), round(py(t) - 4, 1), str(t).replace('-', '−') + '°C', 13, 'middle', MUTED)
    save(name, svg(W, H, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    P = 'c4-l2a-'
    # ===== O01: برج التقطير =====
    tower(P + 'tower.svg')

    # ===== O02: أيّها ألكان؟ =====
    ethene = ({'a': (0, 0, 'C'), 'b': (1.2, 0, 'C'), 'h1': (-0.7, -0.7, 'H'), 'h2': (-0.7, 0.7, 'H'), 'h3': (1.9, -0.7, 'H'), 'h4': (1.9, 0.7, 'H')},
              [('a', 'b', 2), ('a', 'h1', 1), ('a', 'h2', 1), ('b', 'h3', 1), ('b', 'h4', 1)], [])
    propane = full({'c1': (0, 0), 'c2': (1, 0), 'c3': (2, 0)}, [('c1', 'c2'), ('c2', 'c3')]) + ([],)
    ethyne = ({'h1': (-1, 0, 'H'), 'a': (0, 0, 'C'), 'b': (1.2, 0, 'C'), 'h2': (2.2, 0, 'H')}, [('h1', 'a', 1), ('a', 'b', 3), ('b', 'h2', 1)], [])
    methanol = ({'c': (0, 0, 'C'), 'o': (1, 0, 'O'), 'ho': (2, 0, 'H'), 'h1': (-1, 0, 'H'), 'h2': (0, -1, 'H'), 'h3': (0, 1, 'H')},
                [('c', 'o', 1), ('o', 'ho', 1), ('c', 'h1', 1), ('c', 'h2', 1), ('c', 'h3', 1)], [])
    grid_panels(P + 'which-alkane.svg', [('(أ)',) + ethene, ('(ب)',) + propane, ('(ج)',) + ethyne, ('(د)',) + methanol], cols=2)

    # ===== O03 =====
    pent = full({f'c{i}': (i, 0) for i in range(5)}, [(f'c{i}', f'c{i+1}') for i in range(4)])
    single(P + 'pentane-full.svg', *pent)
    mb = full({'c0': (0, 0), 'c1': (1, 0), 'c2': (2, 0), 'c3': (3, 0), 'm': (1, 2)}, [('c0', 'c1'), ('c1', 'c2'), ('c2', 'c3'), ('c1', 'm')])
    single(P + 'methylbutane-full.svg', *mb)
    # أربع صيغ مقترحة للبروبان: (أ) ذرة طرفية بذرتي H فقط، (ب) صحيحة، (ج) ذرة وسطى بخمس روابط، (د) الإيثان
    pr_ok = full({'c1': (0, 0), 'c2': (1, 0), 'c3': (2, 0)}, [('c1', 'c2'), ('c2', 'c3')])
    pr_a = (dict(pr_ok[0]), list(pr_ok[1]))
    # احذف H الأيسر للذرة c1 (يصبح الكربون بثلاث روابط)
    hl = [k for k, (x, y, s) in pr_a[0].items() if s == 'H' and (x, y) == (-1, 0)][0]
    del pr_a[0][hl]; pr_a = (pr_a[0], [e for e in pr_a[1] if hl not in e])
    pr_c = (dict(pr_ok[0]), list(pr_ok[1]))
    pr_c[0]['hx'] = (1.5, -0.8, 'H'); pr_c[1].append(('c2', 'hx', 1))
    eth = full({'c1': (0, 0), 'c2': (1, 0)}, [('c1', 'c2')])
    grid_panels(P + 'propane-four.svg', [('(أ)',) + pr_a + ([],), ('(ب)',) + pr_ok + ([],), ('(ج)',) + pr_c + ([],), ('(د)',) + eth + ([],)], cols=2)
    mp = full({'c0': (0, 0), 'c1': (1, 0), 'c2': (2, 0), 'c3': (3, 0), 'c4': (4, 0), 'm': (1, -2)},
              [('c0', 'c1'), ('c1', 'c2'), ('c2', 'c3'), ('c3', 'c4'), ('c1', 'm')])
    single(P + 'methylpentane-full.svg', *mp)

    # ===== O04: تسمية الألكانات =====
    single(P + 'dmb22.svg', *cond(['CH₃', 'C', 'CH₂', 'CH₃'], [(1, -1, ['CH₃']), (1, 1, ['CH₃'])]))
    single(P + 'dmhep25.svg', *cond(['CH₃', 'CH', 'CH₂', 'CH₂', 'CH', 'CH₂', 'CH₃'], [(1, 1, ['CH₃']), (4, -1, ['CH₃'])]))
    single(P + 'bent-chain.svg', *cond(['CH₃', 'CH', 'CH₂', 'CH₂', 'CH₃'], [(1, -1, ['CH₂', 'CH₂', 'CH₃'])]))
    single(P + 'e4m2hex.svg', *cond(['CH₃', 'CH', 'CH₂', 'CH', 'CH₂', 'CH₃'], [(1, 1, ['CH₃']), (3, -1, ['CH₂', 'CH₃'])]))
    dmp = full({'c0': (0, 0), 'c1': (1, 0), 'c2': (2, 0), 'c3': (3, 0), 'c4': (4, 0), 'm1': (1, -2), 'm2': (2, 2)},
               [('c0', 'c1'), ('c1', 'c2'), ('c2', 'c3'), ('c3', 'c4'), ('c1', 'm1'), ('c2', 'm2')])
    single(P + 'dmp23-full.svg', *dmp)
    single(P + 'butylpentane.svg', *cond(['CH₃', 'CH₂', 'CH', 'CH₂', 'CH₃'], [(2, -1, ['CH₂', 'CH₂', 'CH₂', 'CH₃'])]))
    single(P + 'e4dm25hep.svg', *cond(['CH₃', 'CH', 'CH₂', 'CH', 'CH', 'CH₂', 'CH₃'], [(1, 1, ['CH₃']), (3, -1, ['CH₂', 'CH₃']), (4, 1, ['CH₃'])]))
    single(P + 'wrong-ethyl.svg', *cond(['CH₃', 'CH', 'CH', 'CH₂', 'CH₃'], [(1, -1, ['CH₂', 'CH₃']), (2, 1, ['CH₃'])]))
    a = cond(['CH₃', 'CH₂', 'CH₂', 'CH₂', 'CH₃'])
    bb_ = cond(['CH₃', 'CH₂', 'CH', 'CH₂', 'CH₃'], [(2, -1, ['CH₃'])])
    c_ = cond(['CH₃', 'C', 'CH₂', 'CH', 'CH₃'], [(1, -1, ['CH₃']), (1, 1, ['CH₃']), (3, 1, ['CH₃'])])
    grid_panels(P + 'three-alkanes.svg', [('(أ)',) + a + ([],), ('(ب)',) + bb_ + ([],), ('(ج)',) + c_ + ([],)], cols=1, gapy=10)

    # ===== O05: تسمية الألكانات الحلقية =====
    single(P + 'mcp.svg', *R(5, {1: 'CH₃'}))
    single(P + 'ecb.svg', *R(4, {1: 'CH₂CH₃'}))
    single(P + 'dmcp12.svg', *R(5, {0: 'CH₃', 1: 'CH₃'}))
    single(P + 'dmch13.svg', *R(6, {1: 'CH₃', 5: 'CH₃'}))
    single(P + 'tmcp124.svg', *R(5, {0: 'CH₃', 1: 'CH₃', 3: 'CH₃'}))
    single(P + 'e1m3ch.svg', *R(6, {1: 'CH₂CH₃', 3: 'CH₃'}))
    # 1،1،3: مجموعتا ميثيل على رأس واحد
    n6, e6, m6 = R(6, {3: 'CH₃'})
    import copy
    V1 = n6['r1']; cx, cy = 0, 0
    # مجموعتان على الرأس 1 بزاويتين ±30° حول الاتجاه الخارجي
    ux, uy = V1[0] - cx, V1[1] - cy; d = math.hypot(ux, uy); ux, uy = ux / d, uy / d
    for k, ang in (('p', -0.55), ('q', 0.55)):
        vx, vy = ux * math.cos(ang) - uy * math.sin(ang), ux * math.sin(ang) + uy * math.cos(ang)
        hw, hh = lab_size('CH₃'); t = min(hw / abs(vx) if abs(vx) > 1e-6 else 1e9, hh / abs(vy) if abs(vy) > 1e-6 else 1e9) / U
        n6['g' + k] = (V1[0] + vx * (0.75 + t), V1[1] + vy * (0.75 + t), 'CH₃'); e6.append(('r1', 'g' + k, 1))
    single(P + 'tmch113.svg', n6, e6, m6)
    # تصحيح ترقيم خاطئ: حلقة خماسية ومجموعتا ميثيل على الرأسين 0 و2، والترقيم المعروض يبدأ من الرأس 1
    single(P + 'wrongnum.svg', *R(5, {0: 'CH₃', 2: 'CH₃'}, {1: '1', 2: '2', 3: '3', 4: '4', 0: '5'}))

    # ===== O06: البنية من الاسم =====
    def gem(n, v, others, extra_label='CH₃'):
        """حلقة n فيها مجموعتان على الرأس v، ومجموعات أخرى others = {vertex: label}."""
        nn, ee, mm = R(n, others)
        V = nn[f'r{v}']; ux, uy = V[0], V[1]; d = math.hypot(ux, uy); ux, uy = ux / d, uy / d
        for k, ang in (('p', -0.6), ('q', 0.6)):
            vx, vy = ux * math.cos(ang) - uy * math.sin(ang), ux * math.sin(ang) + uy * math.cos(ang)
            hw, hh = lab_size(extra_label); t = min(hw / abs(vx) if abs(vx) > 1e-6 else 1e9, hh / abs(vy) if abs(vy) > 1e-6 else 1e9) / U
            nn['g' + k] = (V[0] + vx * (0.75 + t), V[1] + vy * (0.75 + t), extra_label); ee.append((f'r{v}', 'g' + k, 1))
        return nn, ee, mm
    grid_panels(P + 'cp-four.svg', [('(أ)',) + gem(3, 1, {}), ('(ب)',) + R(3, {1: 'CH₃', 2: 'CH₃'}),
                                     ('(ج)',) + R(4, {1: 'CH₃', 2: 'CH₃'}), ('(د)',) + R(3, {1: 'CH₂CH₃'})], cols=2)
    grid_panels(P + 'ch-four.svg', [('(أ)',) + R(6, {1: 'CH₃', 2: 'CH₃'}), ('(ب)',) + R(6, {1: 'CH₃', 4: 'CH₃'}),
                                     ('(ج)',) + R(6, {1: 'CH₃', 3: 'CH₃'}), ('(د)',) + R(5, {1: 'CH₃', 3: 'CH₃'})], cols=2)
    grid_panels(P + 'cb-four.svg', [('(أ)',) + R(4, {1: 'CH₂CH₃', 3: 'CH₃'}), ('(ب)',) + R(4, {1: 'CH₂CH₃', 2: 'CH₂CH₃'}),
                                     ('(ج)',) + R(5, {1: 'CH₂CH₃', 2: 'CH₃'}), ('(د)',) + R(4, {1: 'CH₂CH₃', 2: 'CH₃'})], cols=2)
    grid_panels(P + 'tm-four.svg', [('(أ)',) + gem(4, 1, {3: 'CH₃'}), ('(ب)',) + R(4, {0: 'CH₃', 1: 'CH₃', 2: 'CH₃'}),
                                     ('(ج)',) + gem(4, 1, {2: 'CH₃'}), ('(د)',) + gem(5, 1, {2: 'CH₃'})], cols=2)

    # ===== O07 =====
    layers(P + 'layers.svg')
    bp_graph(P + 'bp-graph.svg', [(1, -162, 'ميثان'), (3, -42, 'بروبان'), (4, -1, 'بيوتان'), (6, 69, 'هكسان'), (8, 126, 'أوكتان')])
