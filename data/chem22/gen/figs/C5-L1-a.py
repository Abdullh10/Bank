# رسوم الدرس 5-1 (هاليدات الألكيل وهاليدات الأريل) — النصف الأول: المجموعات الوظيفية، والصيغ العامة، والتسمية،
# والخواص الفيزيائية، والاستعمالات. التشغيل: python3 data/chem22/gen/figs/C5-L1-a.py
import sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

P = 'c5-l1a-'
U = 50          # طول الرابطة بالبكسل
FS = 19
SUB = '₀₁₂₃₄₅₆₇₈₉'
LATIN = "font-family=\"Arial,'DejaVu Sans',sans-serif\""

def TL(x, y, s, size=FS, color=INK, anchor='middle'):
    """نص كيميائي لاتيني (LTR). رمز اليود I وحده يُكتب بخط ذي زوائد كي لا يُشبه خط الرابطة."""
    if s == 'I':
        return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-family="\'DejaVu Serif\',\'Times New Roman\',serif" direction="ltr">I</text>'
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" {LATIN} direction="ltr">{esc(s)}</text>'

def lab_size(s, fs=FS):
    if not s: return 0, 0
    w = sum(0.40 * fs if ch in SUB else 0.30 * fs if ch in 'lIi' else 0.66 * fs for ch in s)
    return w / 2, 0.42 * fs

def mol(m, ox=0, oy=0, fs=FS):
    """m = dict(nodes={id:(x,y,label)}, edges=[(a,b,order)], circles=[(cx,cy,r)], marks=[(x,y,text,color,size)]) بوحدات U.
    يعيد (body, bbox)."""
    nodes, edges = m['nodes'], m['edges']
    Pp = {k: (ox + x * U, oy + y * U, s) for k, (x, y, s) in nodes.items()}
    b = ''
    for a, c, order in edges:
        x1, y1, s1 = Pp[a]; x2, y2, s2 = Pp[c]
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
        def trim(s):
            if not s: return 0
            hw, hh = lab_size(s, fs)
            return min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) + 4
        t1, t2 = trim(s1), trim(s2)
        ax, ay, bx, by = x1 + ux * t1, y1 + uy * t1, x2 - ux * t2, y2 - uy * t2
        offs = {1: [0], 2: [-3.5, 3.5], 3: [-5, 0, 5]}[order]
        for o in offs:
            b += L(round(ax - uy * o, 1), round(ay + ux * o, 1), round(bx - uy * o, 1), round(by + ux * o, 1), INK, 2.2)
    xs, ys = [], []
    for cx, cy, r in m.get('circles', []):
        X, Y = ox + cx * U, oy + cy * U
        b += f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r * U:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
    for k, (x, y, s) in Pp.items():
        hw, hh = lab_size(s, fs)
        if s: b += TL(x, y + 0.36 * fs, s, fs)
        xs += [x - hw, x + hw]; ys += [y - hh, y + hh]
    for (x, y, s, col, size) in m.get('marks', []):
        X, Y = ox + x * U, oy + y * U
        b += T(round(X, 1), round(Y + 0.36 * size, 1), s, size, color=col, weight='bold')
        xs += [X - 8, X + 8]; ys += [Y - 8, Y + 8]
    return b, (min(xs), min(ys), max(xs), max(ys))

def M(nodes, edges, circles=(), marks=()):
    return dict(nodes=nodes, edges=edges, circles=list(circles), marks=list(marks))

def full(carbons, cbonds, subs=None, extra_nodes=None, extra_edges=()):
    """صيغة بنائية كاملة على شبكة. subs = {(x, y): 'Cl'} يستبدل ذرة H في ذلك الموقع بذرة أخرى.
    extra_nodes/extra_edges لذرات غير الكربون في السلسلة (مثل O)."""
    subs = subs or {}; extra_nodes = extra_nodes or {}
    nodes = {k: (x, y, 'C') for k, (x, y) in carbons.items()}
    for k, (x, y, s) in extra_nodes.items(): nodes[k] = (x, y, s)
    edges = [(a, b, 1) for a, b in cbonds] + list(extra_edges)
    occ = {(x, y) for x, y, _ in nodes.values()}
    nb = {k: set() for k in carbons}
    sg = lambda v: (v > 0) - (v < 0)
    for a, b_, _o in edges:
        if a in carbons:
            xa, ya = nodes[a][:2]; xb, yb = nodes[b_][:2]; nb[a].add((sg(xb - xa), sg(yb - ya)))
        if b_ in carbons:
            xa, ya = nodes[b_][:2]; xb, yb = nodes[a][:2]; nb[b_].add((sg(xb - xa), sg(yb - ya)))
    n = 0
    for k, (x, y) in carbons.items():
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if d in nb[k]: continue
            p = (x + d[0], y + d[1])
            assert p not in occ, f'تصادم عند {p}'
            occ.add(p); n += 1
            nodes[f'h{n}'] = (p[0], p[1], subs.get(p, 'H')); edges.append((k, f'h{n}', 1))
    used = {(x, y) for x, y, _ in nodes.values()}
    for p in subs: assert p in used, f'موقع البديل {p} ليس موقع H'
    return M(nodes, edges)

def chain(n, subs=None):
    """سلسلة أفقية مستقيمة من n ذرات كربون بصيغة كاملة، subs = {(x, y): X}."""
    return full({f'c{i}': (i, 0) for i in range(n)}, [(f'c{i}', f'c{i+1}') for i in range(n - 1)], subs)

def cond(main, branches=(), dx=1.35):
    """صيغة بنائية مكثفة: main مجموعات أفقية، branches = [(index, dir(-1 أعلى/+1 أسفل), [labels...])]."""
    nodes = {f'm{i}': (i * dx, 0, s) for i, s in enumerate(main)}
    edges = [(f'm{i}', f'm{i+1}', 1) for i in range(len(main) - 1)]
    for j, (i, d, labs) in enumerate(branches):
        prev = f'm{i}'
        for k, s in enumerate(labs, 1):
            nid = f'b{j}_{k}'; nodes[nid] = (i * dx, d * k * 0.95, s); edges.append((prev, nid, 1)); prev = nid
    return M(nodes, edges)

def ring(n, subs=None, numbers=None, arom=False):
    """حلقة بصيغة خطية (ضلع = 1)، الرأس 0 في الأعلى ثم مع عقارب الساعة. arom: دائرة داخل السداسي (حلقة البنزين)."""
    subs = subs or {}; numbers = numbers or {}
    R = 0.5 / math.sin(math.pi / n)
    rot = -math.pi / 2
    if n == 4: rot = -math.pi * 3 / 4
    V = [(R * math.cos(rot + 2 * math.pi * i / n), R * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    nodes = {f'r{i}': (x, y, '') for i, (x, y) in enumerate(V)}
    edges = [(f'r{i}', f'r{(i + 1) % n}', 1) for i in range(n)]
    marks = []
    for i, s in subs.items():
        x, y = V[i]; d = math.hypot(x, y); ux, uy = x / d, y / d
        hw, hh = lab_size(s)
        t = min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) / U
        nodes[f's{i}'] = (x + ux * (0.72 + t), y + uy * (0.72 + t), s)
        edges.append((f'r{i}', f's{i}', 1))
    for i, s in numbers.items():
        x, y = V[i]; d = math.hypot(x, y)
        marks.append((x - x / d * 0.3, y - y / d * 0.3, s, RED, 15))
    circles = [(0, 0, R * 0.6)] if arom else []
    return M(nodes, edges, circles, marks)

def single(name, m, pad=26, caption=None):
    _, bb = mol(m)
    extra = 34 if caption else 0
    bd, _ = mol(m, pad - bb[0], pad - bb[1])
    W = round(bb[2] - bb[0] + 2 * pad); H = round(bb[3] - bb[1] + 2 * pad + extra)
    if caption: bd += TL(W / 2, H - pad + 4, caption, 16, MUTED)
    save(name, svg(W, H, bd))

def grid(name, items, cols=2, pad=24, gapx=60, gapy=26, label_gap=32):
    """عدة بنى في شبكة، (أ) في أعلى اليمين ثم إلى اليسار. items = [(caption, m)]."""
    parts = [(cap, m, mol(m)[1]) for cap, m in items]
    cw = max(bb[2] - bb[0] for *_, bb in parts); ch = max(bb[3] - bb[1] for *_, bb in parts)
    rows = (len(parts) + cols - 1) // cols
    body = ''
    for k, (cap, m, bb) in enumerate(parts):
        r, c = divmod(k, cols); c = cols - 1 - c
        x0 = pad + c * (cw + gapx); y0 = pad + r * (ch + label_gap + 14 + gapy)
        w = bb[2] - bb[0]; h = bb[3] - bb[1]
        bd, _ = mol(m, x0 + (cw - w) / 2 - bb[0], y0 + (ch - h) / 2 - bb[1])
        body += bd + T(round(x0 + cw / 2, 1), round(y0 + ch + label_gap, 1), cap, 17, weight='bold')
    W = pad * 2 + cols * cw + (cols - 1) * gapx; H = pad * 2 + rows * (ch + label_gap + 14) + (rows - 1) * gapy
    for c in range(1, cols):
        xl = pad + c * (cw + gapx) - gapx / 2
        body += L(round(xl, 1), pad, round(xl, 1), round(H - pad, 1), MUTED, 1, '4 4')
    save(name, svg(round(W), round(H), body))

def bars(name, data, w=600, h=360, ymax=180, step=30):
    """أعمدة درجات الغليان: data = [(label, value)]."""
    X0, Y0, X1, Y1 = 80, h - 70, w - 20, 30
    def py(v): return Y0 - v / ymax * (Y0 - Y1)
    b = ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1 - 10)
    for v in range(0, ymax + 1, step):
        b += L(X0 - 5, py(v), X0, py(v)) + T(X0 - 9, py(v) + 5, str(v), 13, 'end')
        if v: b += L(X0, py(v), X1 - 10, py(v), '#d5dbe3', 1)
    n = len(data); slot = (X1 - X0 - 20) / n
    for i, (lab, v) in enumerate(data):
        cx = X0 + 10 + slot * (i + 0.5); bw = slot * 0.5
        b += f'<rect x="{cx - bw / 2:.1f}" y="{py(v):.1f}" width="{bw:.1f}" height="{Y0 - py(v):.1f}" fill="{BLUE}"/>'
        b += TL(cx, py(v) - 7, f'{v:g}', 14, INK)
        b += TL(cx, Y0 + 22, lab, 15, INK)
    b += f'<text transform="translate({X0 - 50},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">درجة الغليان</text>'
    b += TL(X0 + 8, Y1 - 4, '°C', 14, INK, 'start')
    b += T((X0 + X1) / 2, h - 14, 'المركب', 14, weight='bold')
    save(name, svg(w, h, b))

def ptfe(name):
    """الوحدة المتكررة في رباعي فلورو بولي إيثين بين قوسين."""
    m = M({'c': (0, 0, 'C'), 'f1': (0, -1, 'F'), 'f2': (0, 1, 'F'), 'l': (-1.1, 0, ''), 'r': (1.1, 0, '')},
          [('c', 'f1', 1), ('c', 'f2', 1), ('l', 'c', 1), ('c', 'r', 1)])
    bd, bb = mol(m, 170, 100)
    b = bd
    # قوسان مربعان
    for x, s in ((170 - 0.75 * U, 1), (170 + 0.75 * U, -1)):
        b += f'<polyline points="{x + 10 * s:.1f},{100 - 70} {x:.1f},{100 - 70} {x:.1f},{100 + 70} {x + 10 * s:.1f},{100 + 70}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    b += TL(170 + 0.75 * U + 12, 178, 'n', 20, INK, 'start')
    b += TL(170 - 1.1 * U - 18, 106, '···', 20) + TL(170 + 1.1 * U + 18, 106, '···', 20)
    save(name, svg(340, 200, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # ===== O01: المجموعة الوظيفية =====
    # 1-بروبانول بصيغة كاملة: H على c2 في الموقع (3,0) يُستبدل بـ O ثم O–H
    prop = full({'c0': (0, 0), 'c1': (1, 0), 'c2': (2, 0)}, [('c0', 'c1'), ('c1', 'c2')],
                extra_nodes={'o': (3, 0, 'O'), 'ho': (4, 0, 'H')}, extra_edges=[('c2', 'o', 1), ('o', 'ho', 1)])
    single(P + 'propanol.svg', prop)
    # حمض الإيثانويك: CH₃–C(=O)–OH
    acid = M({'a': (0, 0, 'CH₃'), 'c': (1.35, 0, 'C'), 'o': (1.35, -1, 'O'), 'oh': (2.6, 0, 'OH')},
             [('a', 'c', 1), ('c', 'o', 2), ('c', 'oh', 1)])
    single(P + 'acid.svg', acid)
    # إستر: CH₃–C(=O)–O–CH₂CH₃
    ester = M({'a': (0, 0, 'CH₃'), 'c': (1.35, 0, 'C'), 'o': (1.35, -1, 'O'), 'o2': (2.5, 0, 'O'), 'e': (3.85, 0, 'CH₂CH₃')},
              [('a', 'c', 1), ('c', 'o', 2), ('c', 'o2', 1), ('o2', 'e', 1)])
    single(P + 'ester.svg', ester)
    # أربع صيغ: (أ) كحول (ب) أمين (ج) أميد (د) هاليد ألكيل
    alc = cond(['CH₃', 'CH₂', 'OH'])
    amine = cond(['CH₃', 'CH₂', 'NH₂'])
    amide = M({'a': (0, 0, 'CH₃'), 'c': (1.35, 0, 'C'), 'o': (1.35, -1, 'O'), 'n': (2.6, 0, 'NH₂')},
              [('a', 'c', 1), ('c', 'o', 2), ('c', 'n', 1)])
    rx = cond(['CH₃', 'CH₂', 'Cl'])
    grid(P + 'fg-four.svg', [('(أ)', alc), ('(ب)', amide), ('(ج)', amine), ('(د)', rx)])
    # مركب فيه مجموعتان وظيفيتان: Cl–CH₂–CH₂–OH (لسؤال تحديد المجموعات)
    single(P + 'clethanol.svg', full({'c0': (0, 0), 'c1': (1, 0)}, [('c0', 'c1')], subs={(-1, 0): 'Cl'},
                                       extra_nodes={'o': (2, 0, 'O'), 'ho': (3, 0, 'H')}, extra_edges=[('c1', 'o', 1), ('o', 'ho', 1)]))

    # ===== O02: الصيغ العامة =====
    grid(P + 'which-aryl.svg', [('(أ)', ring(6, {1: 'Cl'})), ('(ب)', cond(['CH₃', 'CH₂', 'Cl'])),
                                ('(ج)', ring(6, {1: 'Cl'}, arom=True)), ('(د)', ring(6, {1: 'CH₃'}, arom=True))])
    single(P + 'aryl-general.svg', ring(6, {0: 'X'}, arom=True), caption='X = F, Cl, Br, I')
    single(P + 'bromoethane.svg', chain(2, {(2, 0): 'Br'}))
    # أربعة مركبات للتصنيف إلى هاليد ألكيل/أريل: (أ) برومو بنزين (ب) 2-كلورو بروبان مكثف (ج) أيودو ميثان كامل (د) 1، 4-ثنائي كلورو بنزين
    grid(P + 'classify4.svg', [('(أ)', ring(6, {1: 'Br'}, arom=True)), ('(ب)', cond(['CH₃', 'CH', 'CH₃'], [(1, -1, ['Cl'])])),
                               ('(ج)', full({'c': (0, 0)}, [], subs={(1, 0): 'I'})), ('(د)', ring(6, {0: 'Cl', 3: 'Cl'}, arom=True))])

    # ===== O03: التسمية =====
    single(P + 'n-2clpropane.svg', chain(3, {(1, -1): 'Cl'}))
    single(P + 'n-1br2clbutane.svg', chain(4, {(-1, 0): 'Br', (1, -1): 'Cl'}))
    single(P + 'n-2br5clhexane.svg', cond(['CH₃', 'CH', 'CH₂', 'CH₂', 'CH', 'CH₃'], [(1, -1, ['Br']), (4, -1, ['Cl'])]))
    single(P + 'n-111tcethane.svg', chain(2, {(-1, 0): 'Cl', (0, -1): 'Cl', (0, 1): 'Cl'}))
    single(P + 'n-1br3clbenzene.svg', ring(6, {0: 'Br', 2: 'Cl'}, arom=True))
    single(P + 'n-bromocyclohexane.svg', ring(6, {1: 'Br'}))
    single(P + 'n-23difluorobutane.svg', chain(4, {(1, -1): 'F', (2, -1): 'F'}))
    grid(P + 'n-essay3.svg', [('(أ)', cond(['CH₃', 'CH', 'CH₂', 'CH₃'], [(1, -1, ['I'])])), ('(ب)', ring(5, {0: 'Cl'})),
                              ('(ج)', ring(6, {0: 'F', 1: 'Cl'}, arom=True))], cols=3)

    # ===== O04: الخواص الفيزيائية =====
    bars(P + 'bp-bars.svg', [('C₅H₁₂', 36), ('C₅H₁₁F', 62.8), ('C₅H₁₁Cl', 108), ('C₅H₁₁Br', 130), ('C₅H₁₁I', 155)])

    # ===== O05: الاستعمالات =====
    ptfe(P + 'ptfe.svg')
    single(P + 'cfc12.svg', full({'c': (0, 0)}, [], subs={(-1, 0): 'Cl', (1, 0): 'Cl', (0, -1): 'F', (0, 1): 'F'}))
    single(P + 'hfc134a.svg', chain(2, {(-1, 0): 'F', (0, -1): 'F', (0, 1): 'F', (2, 0): 'F'}))
