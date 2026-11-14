# رسوم الدرس 5-4 (تفاعلات أخرى للمركبات العضوية): مخططات تفاعلات بصيغ بنائية، ومسارات تحويل، ومخطط طاقة لهدرجة بمحفز.
# التشغيل: python3 data/chem22/gen/figs/C5-L4.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

U = 50          # طول الرابطة بالبكسل
FS = 19
SUB = '₀₁₂₃₄₅₆₇₈₉⁺⁻'

def lab_size(s, fs=FS):
    if not s: return 0, 0
    w = sum(0.40 * fs if ch in SUB else 0.66 * fs for ch in s)
    return w / 2, 0.42 * fs

def mol(nodes, edges, ox=0, oy=0, fs=FS):
    """nodes = {id: (x, y, label)} بوحدات طول الرابطة (y للأسفل)، label فارغ = رأس صيغة خطية. edges = [(a, b, order)]."""
    P = {k: (ox + x * U, oy + y * U, s) for k, (x, y, s) in nodes.items()}
    b = ''
    for a, c, order in edges:
        x1, y1, s1 = P[a]; x2, y2, s2 = P[c]
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
        def trim(s):
            if not s: return 0
            hw, hh = lab_size(s, fs)
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
    return b, (min(xs), min(ys), max(xs), max(ys))

# ---------- منشئات البنى ----------
def cond(main, orders=None, branches=(), dx=1.25):
    """صيغة مكثفة أفقية. main = مجموعات، orders = رتب الروابط بينها، branches = [(i, d(-1 أعلى/+1 أسفل), label, order)]."""
    orders = orders or [1] * (len(main) - 1)
    nodes = {f'm{i}': (i * dx, 0, s) for i, s in enumerate(main)}
    edges = [(f'm{i}', f'm{i+1}', orders[i]) for i in range(len(main) - 1)]
    for j, (i, d, lab, o) in enumerate(branches):
        nodes[f'b{j}'] = (i * dx, d * 1.0, lab); edges.append((f'm{i}', f'b{j}', o))
    return nodes, edges

def ring(n, double=(), subs=None, rot=None):
    """حلقة بصيغة خطية؛ double = أرقام الأضلاع الثنائية (الضلع i بين الرأسين i و i+1)."""
    subs = subs or {}
    R = 0.5 / math.sin(math.pi / n)
    rot = -math.pi / 2 if rot is None else rot
    V = [(R * math.cos(rot + 2 * math.pi * i / n), R * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    nodes = {f'r{i}': (x, y, '') for i, (x, y) in enumerate(V)}
    edges = [(f'r{i}', f'r{(i + 1) % n}', 2 if i in double else 1) for i in range(n)]
    for i, s in subs.items():
        x, y = V[i]; d = math.hypot(x, y); ux, uy = x / d, y / d
        nodes[f's{i}'] = (x + ux * 1.2, y + uy * 1.2, s); edges.append((f'r{i}', f's{i}', 1))
    return nodes, edges

def place(nodes, edges, x, ycenter):
    """يضع البنية بحيث يبدأ طرفها الأيسر عند x ومركزها الرأسي عند ycenter؛ يعيد (body, bbox)."""
    _, bb = mol(nodes, edges)
    ox = x - bb[0]; oy = ycenter - (bb[1] + bb[3]) / 2
    return mol(nodes, edges, ox, oy)

# ---------- مخطط تفاعل أفقي ----------
def scheme(name, items, gap=26, pad=24, cap_gap=34, H0=None):
    """items: ('m', nodes, edges, caption) | ('t', text) | ('a', above, below, length)."""
    sizes = []
    for it in items:
        if it[0] == 'm':
            _, bb = mol(it[1], it[2]); sizes.append((bb[2] - bb[0], bb[3] - bb[1]))
        elif it[0] == 't': sizes.append((lab_size(it[1], 24)[0] * 2, 24))
        else: sizes.append((it[3] if len(it) > 3 else 90, 20))
    hmax = max(h for w, h in sizes)
    has_cap = any(it[0] == 'm' and it[3] for it in items)
    has_above = any(it[0] == 'a' and it[1] for it in items)
    top = pad + (26 if has_above else 0)
    yc = top + hmax / 2
    x = pad; body = ''
    for it, (w, h) in zip(items, sizes):
        if it[0] == 'm':
            bd, bb = place(it[1], it[2], x, yc); body += bd
            if it[3]: body += T(round(x + w / 2, 1), round(top + hmax + cap_gap, 1), it[3], 15, color=MUTED, weight='bold')
        elif it[0] == 't':
            body += T(round(x + w / 2, 1), round(yc + 8, 1), it[1], 24)
        else:
            body += ARROW(x, yc, x + w, yc)
            if it[1]: body += T(round(x + w / 2, 1), round(yc - 12, 1), it[1], 15, color=BLUE, weight='bold')
            if it[2]: body += T(round(x + w / 2, 1), round(yc + 26, 1), it[2], 15, color=BLUE, weight='bold')
        x += w + gap
    W = x - gap + pad
    H = top + hmax + (cap_gap + 12 if has_cap else 0) + pad
    if H0: H = max(H, H0)
    save(name, svg(round(W), round(H), body))

def panels(name, items, gap=70, pad=24, cap_gap=34):
    """بنى جنبًا إلى جنب تحت كل منها عنوانها. items = [(caption, nodes, edges)] من اليمين إلى اليسار."""
    items = list(reversed(items))
    parts = [(cap, n, e, mol(n, e)[1]) for cap, n, e in items]
    hmax = max(bb[3] - bb[1] for *_, bb in parts)
    yc = pad + hmax / 2; x = pad; body = ''
    for cap, n, e, bb in parts:
        w = bb[2] - bb[0]
        bd, _ = place(n, e, x, yc); body += bd
        body += T(round(x + w / 2, 1), round(pad + hmax + cap_gap, 1), cap, 17, weight='bold')
        x += w + gap
    save(name, svg(round(x - gap + pad), round(pad + hmax + cap_gap + 12 + pad), body))

# ---------- بنى جاهزة ----------
def ethane_full():
    return ({'c1': (0, 0, 'C'), 'c2': (1, 0, 'C'), 'h1': (-1, 0, 'H'), 'h2': (0, -1, 'H'), 'h3': (0, 1, 'H'),
             'h4': (2, 0, 'H'), 'h5': (1, -1, 'H'), 'h6': (1, 1, 'H')},
            [('c1', 'c2', 1), ('c1', 'h1', 1), ('c1', 'h2', 1), ('c1', 'h3', 1), ('c2', 'h4', 1), ('c2', 'h5', 1), ('c2', 'h6', 1)])

def ethene_full():
    return ({'a': (0, 0, 'C'), 'b': (1.2, 0, 'C'), 'h1': (-0.7, -0.7, 'H'), 'h2': (-0.7, 0.7, 'H'), 'h3': (1.9, -0.7, 'H'), 'h4': (1.9, 0.7, 'H')},
            [('a', 'b', 2), ('a', 'h1', 1), ('a', 'h2', 1), ('b', 'h3', 1), ('b', 'h4', 1)])

def ethanol_full():
    return ({'c1': (0, 0, 'C'), 'c2': (1, 0, 'C'), 'o': (2, 0, 'O'), 'ho': (3, 0, 'H'), 'h1': (-1, 0, 'H'), 'h2': (0, -1, 'H'), 'h3': (0, 1, 'H'),
             'h5': (1, -1, 'H'), 'h6': (1, 1, 'H')},
            [('c1', 'c2', 1), ('c2', 'o', 1), ('o', 'ho', 1), ('c1', 'h1', 1), ('c1', 'h2', 1), ('c1', 'h3', 1), ('c2', 'h5', 1), ('c2', 'h6', 1)])

def water():
    return ({'h1': (0, 0, 'H'), 'o': (1, 0, 'O'), 'h2': (2, 0, 'H')}, [('h1', 'o', 1), ('o', 'h2', 1)])

def but2ene_full():
    n = {'c1': (0, 0, 'C'), 'c2': (1, 0, 'C'), 'c3': (2.2, 0, 'C'), 'c4': (3.2, 0, 'C'),
         'h1': (-1, 0, 'H'), 'h2': (0, -1, 'H'), 'h3': (0, 1, 'H'), 'h4': (1, -1, 'H'), 'h5': (2.2, -1, 'H'),
         'h6': (4.2, 0, 'H'), 'h7': (3.2, -1, 'H'), 'h8': (3.2, 1, 'H')}
    e = [('c1', 'c2', 1), ('c2', 'c3', 2), ('c3', 'c4', 1), ('c1', 'h1', 1), ('c1', 'h2', 1), ('c1', 'h3', 1),
         ('c2', 'h4', 1), ('c3', 'h5', 1), ('c4', 'h6', 1), ('c4', 'h7', 1), ('c4', 'h8', 1)]
    return n, e

def single(name, nodes, edges, pad=26):
    _, bb = mol(nodes, edges)
    bd, _ = mol(nodes, edges, pad - bb[0], pad - bb[1])
    save(name, svg(round(bb[2] - bb[0] + 2 * pad), round(bb[3] - bb[1] + 2 * pad), bd))

# ---------- مخطط مسار تحويل عام (عقد نصية وأسهم مرقمة) ----------
def box_mol(nodes, edges, cx, cy):
    _, bb = mol(nodes, edges)
    return mol(nodes, edges, cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2)

def numlabel(x, y, s):
    return f'<circle cx="{x}" cy="{y}" r="13" fill="#fff" stroke="{RED}" stroke-width="2"/>' + T(x, y + 6, s, 15, color=RED, weight='bold')

def fig_cycle(name):
    """إيثان ⇄ إيثين ⇄ إيثانول بأسهم مرقمة 1–4."""
    W, H = 900, 270
    b = ''
    xs = [130, 450, 770]; yc = 135
    for (n, e), x in zip([ethane_full(), ethene_full(), ethanol_full()], xs):
        bd, bb = box_mol(n, e, x, yc); b += bd
    b += T(130, 240, 'إيثان', 16, weight='bold') + T(450, 240, 'إيثين', 16, weight='bold') + T(770, 240, 'إيثانول', 16, weight='bold')
    # أسهم: علوي من اليسار إلى اليمين، سفلي من اليمين إلى اليسار
    for (x1, x2, n_top, n_bot) in [(225, 375, '1', '2'), (520, 645, '3', '4')]:
        b += ARROW(x1, yc - 22, x2, yc - 22, BLUE) + numlabel((x1 + x2) / 2, yc - 46, n_top)
        b += ARROW(x2, yc + 22, x1, yc + 22, GREEN) + numlabel((x1 + x2) / 2, yc + 46, n_bot)
    save(name, svg(W, H, b))

def fig_route(name):
    """2-برومو بروبان ومسارات تحويل مرقمة 1–4."""
    W, H = 900, 400
    b = ''
    def put(n, e, cx, cy, cap):
        bd, bb = box_mol(n, e, cx, cy)
        return bd + T(cx, bb[3] + 28, cap, 15, color=MUTED, weight='bold'), bb
    brp = cond(['CH₃', 'CH', 'CH₃'], branches=[(1, 1, 'Br', 1)])
    pro = cond(['CH₂', 'CH', 'CH₃'], orders=[2, 1])
    pra = cond(['CH₃', 'CH₂', 'CH₃'])
    p2ol = cond(['CH₃', 'CH', 'CH₃'], branches=[(1, 1, 'OH', 1)])
    p2one = cond(['CH₃', 'C', 'CH₃'], branches=[(1, -1, 'O', 2)])
    s, bb0 = put(*brp, 450, 70, '2-برومو بروبان'); b += s
    s, _ = put(*pro, 220, 210, 'بروبين'); b += s
    s, _ = put(*pra, 110, 340, 'بروبان'); b += s
    s, _ = put(*p2ol, 680, 200, '2-بروبانول'); b += s
    s, _ = put(*p2one, 790, 330, '2-بروبانون'); b += s
    b += ARROW(385, 95, 285, 180, BLUE) + numlabel(318, 125, '1')
    b += ARROW(185, 240, 135, 315, BLUE) + numlabel(140, 270, '2')
    b += ARROW(515, 95, 625, 165, BLUE) + numlabel(585, 115, '3')
    b += ARROW(705, 265, 760, 300, BLUE) + numlabel(758, 265, '4')
    b += T(172, 300, '+ H₂', 15, 'start', BLUE)
    b += T(562, 158, '+ OH⁻', 15, 'end', BLUE)
    b += T(700, 300, '+ (O)', 15, 'end', BLUE)
    save(name, svg(W, H, b))

def fig_profile(name):
    """منحنيا طاقة لتفاعل هدرجة طارد للحرارة بدون محفز (1) وبوجود محفز (2)."""
    W, H = 560, 360
    X0, Y0, X1, Y1 = 80, 310, 530, 30
    b = ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1)
    b += f'<text transform="translate({X0 - 22},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="15" fill="{INK}" font-weight="bold" {FONT} direction="rtl">الطاقة الكامنة</text>'
    b += T((X0 + X1) / 2, Y0 + 32, 'سير التفاعل', 15, weight='bold')
    yR, yP = 200, 255
    def curve(peak, color, dash=''):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        return (f'<path d="M100 {yR} L170 {yR} C230 {yR} 240 {peak} 300 {peak} C360 {peak} 370 {yP} 430 {yP} L510 {yP}" '
                f'fill="none" stroke="{color}" stroke-width="3"{da}/>')
    b += curve(60, RED, '8 6') + curve(150, BLUE)
    b += numlabel(300, 44, '1') + numlabel(300, 134, '2')
    b += T(135, yR - 12, 'المتفاعلات', 14, color=MUTED, weight='bold') + T(470, yP - 12, 'النواتج', 14, color=MUTED, weight='bold')
    b += T(135, yR + 24, 'زيت + H₂', 14) + T(470, yP + 24, 'دهن مشبع', 14)
    save(name, svg(W, H, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    P = 'c5-l4-'
    # O01-M1: هدرجة 2-بنتين
    scheme(P + 'pentene-h2.svg', [
        ('m',) + cond(['CH₃', 'CH', 'CH', 'CH₂', 'CH₃'], [1, 2, 1, 1]) + ('',), ('t', '+'),
        ('m', {'a': (0, 0, 'H'), 'b': (1, 0, 'H')}, [('a', 'b', 1)], ''), ('a', '', '', 70),
        ('m',) + cond(['CH₃', 'CH₂', 'CH₂', 'CH₂', 'CH₃']) + ('',)])
    # O01-M3: حمض الإيثانويك + ميثانول → إيثانوات الميثيل + ماء
    acid = cond(['CH₃', 'C', 'OH'], branches=[(1, -1, 'O', 2)])
    meoh = cond(['CH₃', 'OH'])
    ester = cond(['CH₃', 'C', 'O', 'CH₃'], branches=[(1, -1, 'O', 2)])
    scheme(P + 'ester-methyl.svg', [('m',) + acid + ('حمض الإيثانويك',), ('t', '+'), ('m',) + meoh + ('ميثانول',), ('a', '', '', 70),
                                    ('m',) + ester + ('إيثانوات الميثيل',), ('t', '+'), ('m',) + water() + ('ماء',)])
    # O02-M3: حمض البروبانويك + إيثانول → ؟
    pacid = cond(['CH₃', 'CH₂', 'C', 'OH'], branches=[(2, -1, 'O', 2)])
    etoh = cond(['CH₃', 'CH₂', 'OH'])
    scheme(P + 'propanoic-ethanol.svg', [('m',) + pacid + ('حمض البروبانويك',), ('t', '+'), ('m',) + etoh + ('إيثانول',), ('a', '', '', 70), ('t', '؟')])
    # O02-E3: 2-بيوتين
    single(P + '2-butene.svg', *but2ene_full())
    # O03-M1: بنتين حلقي + HBr → ؟
    cp = ring(5, double=(2,))
    scheme(P + 'cyclopentene-hbr.svg', [('m',) + cp + ('بنتين حلقي',), ('t', '+'), ('m', {'a': (0, 0, 'HBr')}, [], 'بروميد الهيدروجين'), ('a', '', '', 70), ('t', '؟')])
    # O03-M3: 2-كلورو بيوتان + OH⁻ → ؟
    clb = cond(['CH₃', 'CH₂', 'CH', 'CH₃'], branches=[(2, 1, 'Cl', 1)])
    scheme(P + '2-chlorobutane-oh.svg', [('m',) + clb + ('',), ('t', '+'), ('m', {'a': (0, 0, 'OH⁻')}, [], ''), ('a', '', '', 70), ('t', '؟')])
    # O03-M5: 1-بيوتين + ماء
    b1 = cond(['CH₂', 'CH', 'CH₂', 'CH₃'], [2, 1, 1])
    scheme(P + '1-butene-water.svg', [('m',) + b1 + ('1-بيوتين',), ('t', '+'), ('m', {'a': (0, 0, 'H₂O')}, [], 'ماء'), ('a', '', '', 70), ('t', '؟')])
    # O03-E2: 1-بيوتين و2-بيوتين
    b2 = cond(['CH₃', 'CH', 'CH', 'CH₃'], [1, 2, 1])
    panels(P + 'butenes.svg', [('1-بيوتين',) + b1, ('2-بيوتين',) + b2])
    # O04-M2: إيثانول → إيثين + ماء
    scheme(P + 'ethanol-ethene.svg', [('m',) + ethanol_full() + ('',), ('a', '', '', 70), ('m',) + ethene_full() + ('',), ('t', '+'), ('m',) + water() + ('',)])
    # O04-M3: إيثين + ماء → إيثانول
    scheme(P + 'ethene-water.svg', [('m',) + ethene_full() + ('',), ('t', '+'), ('m',) + water() + ('',), ('a', '', '', 70), ('m',) + ethanol_full() + ('',)])
    # O04-M6
    fig_cycle(P + 'cycle.svg')
    # O05-M1: 2-بروبانول + (O) → ؟
    p2ol = cond(['CH₃', 'CH', 'CH₃'], branches=[(1, -1, 'OH', 1)])
    scheme(P + '2-propanol-ox.svg', [('m',) + p2ol + ('',), ('t', '+'), ('m', {'a': (0, 0, '(O)')}, [], ''), ('a', '', '', 70), ('t', '؟')])
    # O05-M2: 1-بروبانول → A → B
    p1ol = cond(['CH₃', 'CH₂', 'CH₂', 'OH'])
    scheme(P + 'propanol-ab.svg', [('m',) + p1ol + ('1-بروبانول',), ('a', 'أكسدة', '', 90), ('t', 'A'), ('a', 'أكسدة', '', 90), ('t', 'B')])
    # O05-M7: (1) و(2)
    b1ol = cond(['CH₃', 'CH₂', 'CH₂', 'CH₂', 'OH'])
    b2ol = cond(['CH₃', 'CH₂', 'CH', 'CH₃'], branches=[(2, -1, 'OH', 1)])
    panels(P + 'butanols.svg', [('(1)',) + b1ol, ('(2)',) + b2ol])
    # O06-M1: هكسين حلقي → هكسان حلقي
    scheme(P + 'cyclohexene-q.svg', [('m',) + ring(6, double=(1,)) + ('هكسين حلقي',), ('a', '؟', '', 90), ('m',) + ring(6) + ('هكسان حلقي',)])
    # O06-M6: إيثانول → إيثانال
    scheme(P + 'ethanol-ethanal.svg', [('m',) + cond(['CH₃', 'CH₂', 'OH']) + ('إيثانول',), ('a', '؟', '', 90),
                                       ('m',) + cond(['CH₃', 'C', 'H'], branches=[(1, -1, 'O', 2)]) + ('إيثانال',)])
    # O06-E3
    fig_route(P + 'route.svg')
    # O07
    fig_profile(P + 'cat-profile.svg')
