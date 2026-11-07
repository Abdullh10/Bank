# رسوم الدرس 4-2 (الألكانات) — النصف الثاني (O08–O13): هياكل كربونية، ومجموعات ألكيل، وصيغ مكثفة لتسمية الألكانات المتفرعة وكتابتها،
# ورسم جزيئي للروابط الهيدروجينية بين جزيئات الماء، ومخطط أعمدة لدرجتي الغليان والانصهار للماء والميثان.
# التشغيل: python3 data/chem22/gen/figs/C4-L2-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

# استيراد أدوات الرسم من ملف النصف الأول دون تعديله
_spec = importlib.util.spec_from_file_location('c4l2a', os.path.join(os.path.dirname(__file__), 'C4-L2-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
mol, cond, full, single, grid_panels, panels, U = A.mol, A.cond, A.full, A.single, A.grid_panels, A.panels, A.U


def skel(carbons, bonds):
    """هيكل كربوني (ذرات C فقط دون H) على شبكة: carbons = {id: (x, y)}، bonds = [(a, b)]."""
    return {k: (x, y, 'C') for k, (x, y) in carbons.items()}, [(a, b, 1) for a, b in bonds]


def chain_skel(n, branches, dx=1.2, dy=1.1):
    """سلسلة أفقية من n ذرة C، وفروع رأسية: branches = [(index, dir, length)]."""
    c = {f'm{i}': (i * dx, 0) for i in range(n)}
    b = [(f'm{i}', f'm{i+1}') for i in range(n - 1)]
    for j, (i, d, ln) in enumerate(branches):
        prev = f'm{i}'
        for k in range(1, ln + 1):
            nid = f'b{j}_{k}'; c[nid] = (i * dx, d * k * dy); b.append((prev, nid)); prev = nid
    return skel(c, b)


def alkyl(carbons, cbonds, free):
    """صيغة بنائية كاملة لمجموعة ألكيل: free = (carbon id, (dx, dy)) اتجاه الرابطة الحرة (تحل محل ذرة H هناك)."""
    k, (dx, dy) = free
    x, y = carbons[k]
    nodes, edges = full(carbons, cbonds)
    h = [n for n, (hx, hy, s) in nodes.items() if s == 'H' and (hx, hy) == (x + dx, y + dy)][0]
    nodes[h] = (x + dx * 0.75, y + dy * 0.75, '')
    return nodes, edges


def numbered_cond(main, branches, nums, dy=-0.62):
    """صيغة مكثفة مع أرقام حمراء فوق ذرات السلسلة الأفقية: nums = ['1', '2', ...] بترتيب المجموعات من اليسار."""
    nodes, edges = cond(main, branches)
    marks = [(i * 1.3, dy, s, RED, 15) for i, s in enumerate(nums) if s]
    return nodes, edges, marks


def water_mol(cx, cy, ang, s=34):
    """جزيء ماء منحنٍ: O في (cx, cy)، والمحور باتجاه ang (راديان)، زاوية H–O–H نحو 105°."""
    b = ''; Hs = []
    for da in (-0.92, 0.92):
        a = ang + da
        hx, hy = cx + s * math.cos(a), cy + s * math.sin(a)
        b += L(round(cx + 14 * math.cos(a), 1), round(cy + 14 * math.sin(a), 1), round(hx - 10 * math.cos(a), 1), round(hy - 10 * math.sin(a), 1), INK, 2)
        b += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="10" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>' + T(round(hx, 1), round(hy + 5, 1), 'H', 14, weight='bold')
        Hs.append((hx, hy))
    b += f'<circle cx="{cx}" cy="{cy}" r="14" fill="#f6d5d1" stroke="{RED}" stroke-width="1.8"/>' + T(cx, cy + 6, 'O', 17, color=RED, weight='bold')
    return b, Hs


def methane_mol(cx, cy, s=30):
    b = ''
    for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
        a2 = a + math.pi / 4
        hx, hy = cx + s * math.cos(a2), cy + s * math.sin(a2)
        b += L(round(cx + 14 * math.cos(a2), 1), round(cy + 14 * math.sin(a2), 1), round(hx - 10 * math.cos(a2), 1), round(hy - 10 * math.sin(a2), 1), INK, 2)
        b += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="10" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>' + T(round(hx, 1), round(hy + 5, 1), 'H', 14, weight='bold')
    b += f'<circle cx="{cx}" cy="{cy}" r="14" fill="#dde3ea" stroke="{INK}" stroke-width="1.8"/>' + T(cx, cy + 6, 'C', 17, weight='bold')
    return b


def hbond(name):
    """(أ) أربعة جزيئات ماء، كل جزيء يتجه أحد ذرتي H فيه نحو ذرة O في جزيء مجاور، وبينهما خط متقطع (رابطة هيدروجينية)؛
    (ب) أربعة جزيئات ميثان متباعدة دون أي خطوط بينها."""
    W, H = 760, 400
    b = L(400, 20, 400, 360, MUTED, 1, '4 4')
    Os = [(75, 85), (305, 70), (90, 300), (320, 290)]
    target = {0: 1, 1: 3, 3: 2, 2: 0}
    for i, (cx, cy) in enumerate(Os):
        tx, ty = Os[target[i]]
        d = math.atan2(ty - cy, tx - cx)
        bd, Hs = water_mol(cx, cy, d + 0.92, s=54); b += bd
        hx, hy = Hs[0]
        dd = math.hypot(tx - hx, ty - hy); ux, uy = (tx - hx) / dd, (ty - hy) / dd
        b += L(round(hx + ux * 11, 1), round(hy + uy * 11, 1), round(tx - ux * 15, 1), round(ty - uy * 15, 1), BLUE, 2.5, '6 5')
    for cx, cy in [(490, 95), (670, 115), (505, 280), (680, 290)]:
        b += methane_mol(cx, cy, s=46)
    b += T(195, 388, '(أ) الماء', 17, weight='bold') + T(585, 388, '(ب) الميثان', 17, weight='bold')
    save(name, svg(W, H, b))
    return target


def bars(name):
    """مخطط أعمدة: درجة الغليان ودرجة الانصهار للماء والميثان (°C)."""
    W, H = 520, 400
    X0, X1 = 90, 500
    top, bot = 40, 350
    vmin, vmax = -200, 120
    def y(v): return top + (vmax - v) / (vmax - vmin) * (bot - top)
    b = ''
    for t in range(-200, 121, 40):
        b += L(X0, round(y(t), 1), X1, round(y(t), 1), '#e3e7ec', 1) + T(X0 - 8, round(y(t) + 5, 1), str(t).replace('-', '−'), 13, 'end')
    b += L(X0, round(y(0), 1), X1, round(y(0), 1), INK, 1.5) + L(X0, top - 8, X0, bot, INK, 1.5)
    b += f'<text transform="translate({X0 - 52},{(top + bot) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">درجة الحرارة (°C)</text>'
    data = [('الماء H₂O', 100, 0, 200), ('الميثان CH₄', -162, -182, 380)]
    for lab, bp, mp, cx in data:
        for v, dx, col in ((bp, -32, RED), (mp, 32, BLUE)):
            x = cx + dx - 26; y0, y1 = sorted((y(0), y(v)))
            h = max(y1 - y0, 3)
            b += f'<rect x="{x}" y="{y0:.1f}" width="52" height="{h:.1f}" fill="{col}" opacity="0.85"/>'
            vy = y(v) - 8 if v >= 0 else y(v) + 20
            b += T(cx + dx, round(vy, 1), (str(v).replace('-', '−')) + '°C', 13, weight='bold')
        b += T(cx, round(y(vmax) - 6 + 0, 1) if False else 30, '', 1)
    # أسماء المواد أسفل المخطط
    b += T(200, bot + 28, 'الماء H₂O', 15, weight='bold') + T(380, bot + 28, 'الميثان CH₄', 15, weight='bold')
    # مفتاح
    b += f'<rect x="300" y="52" width="16" height="12" fill="{RED}" opacity="0.85"/>' + T(325, 63, 'درجة الغليان', 13, 'start')
    b += f'<rect x="300" y="74" width="16" height="12" fill="{BLUE}" opacity="0.85"/>' + T(325, 85, 'درجة الانصهار', 13, 'start')
    save(name, svg(W, H + 10, b))


def shapes(name):
    """جزيء الماء المنحني وجزيء الميثان (صيغة بنائية)."""
    W, H = 520, 230
    b = ''
    # الماء
    ox, oy = 140, 95
    for a in (math.radians(180 - 52.5 + 90), math.radians(52.5 + 90 - 90 + 0)):
        pass
    for sgn in (-1, 1):
        a = math.radians(90 + sgn * 52.5)
        hx, hy = ox + 60 * math.cos(a), oy + 60 * math.sin(a)
        b += L(round(ox + 14 * math.cos(a), 1), round(oy + 14 * math.sin(a), 1), round(hx - 10 * math.cos(a), 1), round(hy - 10 * math.sin(a), 1), INK, 2.2)
        b += T(round(hx, 1), round(hy + 7, 1), 'H', 20)
    b += T(ox, oy + 7, 'O', 20)
    b += T(140, 210, 'الماء', 16, weight='bold')
    # الميثان
    cx, cy = 380, 100
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        b += L(cx + dx * 14, cy + dy * 14, cx + dx * 50, cy + dy * 50, INK, 2.2) + T(cx + dx * 62, cy + dy * 62 + 7, 'H', 20)
    b += T(cx, cy + 7, 'C', 20)
    b += T(380, 210, 'الميثان', 16, weight='bold')
    b += L(260, 20, 260, 215, MUTED, 1, '4 4')
    save(name, svg(W, H, b))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    P = 'c4-l2b-'
    # ===== O08 =====
    single(P + 'skel-234tmh.svg', *chain_skel(6, [(1, -1, 1), (2, 1, 1), (3, -1, 1)]))
    single(P + 'skel-4e22dmh.svg', *chain_skel(6, [(1, -1, 1), (1, 1, 1), (3, -1, 2)]))

    # ===== O09 =====
    eth = A.full({'c1': (0, 0), 'c2': (1, 0)}, [('c1', 'c2')])
    pro = A.full({f'c{i}': (i, 0) for i in range(3)}, [(f'c{i}', f'c{i+1}') for i in range(2)])
    but = A.full({f'c{i}': (i, 0) for i in range(4)}, [(f'c{i}', f'c{i+1}') for i in range(3)])
    panels(P + 'c2c3c4.svg', [('(أ) إيثان',) + eth + ([],), ('(ب) بروبان',) + pro + ([],), ('(ج) بيوتان',) + but + ([],)], gap=60)

    # ===== O10 =====
    ethyl = alkyl({'a': (0, 0), 'b': (0, 1)}, [('a', 'b')], ('b', (1, 0)))
    propyl = alkyl({'a': (0, 0), 'b': (0, 1), 'c': (0, 2)}, [('a', 'b'), ('b', 'c')], ('c', (1, 0)))
    isoprop = alkyl({'a': (0, 0), 'b': (0, 1), 'c': (0, 2)}, [('a', 'b'), ('b', 'c')], ('b', (1, 0)))
    butyl = alkyl({'a': (0, 0), 'b': (0, 1), 'c': (0, 2), 'd': (0, 3)}, [('a', 'b'), ('b', 'c'), ('c', 'd')], ('d', (1, 0)))
    grid_panels(P + 'alkyl-four.svg', [('(أ)',) + propyl + ([],), ('(ب)',) + butyl + ([],), ('(ج)',) + isoprop + ([],), ('(د)',) + ethyl + ([],)], cols=4, gapx=50)
    single(P + 'bent-24dmhep.svg', *cond(['CH₃', 'CH', 'CH₂', 'CH', 'CH₃'], [(1, -1, ['CH₂', 'CH₂', 'CH₃']), (3, 1, ['CH₃'])]))
    n_, e_ = cond(['CH₃', 'CH', 'CH₂', 'CH', 'CH₂', 'CH₂', 'CH₃'], [(1, 1, ['CH₃']), (3, -1, ['CH'])])
    n_['ip1'] = (3 * 1.3 - 1.3, -1, 'CH₃'); n_['ip2'] = (3 * 1.3 + 1.3, -1, 'CH₃')
    e_ += [('b1_1', 'ip1', 1), ('b1_1', 'ip2', 1)]
    single(P + '4ip2mhep.svg', n_, e_)

    # ===== O11 =====
    o_a = cond(['CH₃', 'CH', 'CH', 'CH₂', 'CH₂', 'CH₂', 'CH₃'], [(1, 1, ['CH₃']), (2, -1, ['CH₃'])])          # 2،3-ثنائي ميثيل هبتان
    o_b = cond(['CH₃', 'CH₂', 'CH', 'CH', 'CH₂', 'CH₃'], [(2, 1, ['CH₃']), (3, -1, ['CH₃'])])                 # 3،4-ثنائي ميثيل هكسان
    o_c = cond(['CH₃', 'CH₂', 'CH', 'CH', 'CH₂', 'CH₂', 'CH₃'], [(2, 1, ['CH₃']), (3, -1, ['CH₃'])])          # 3،4-ثنائي ميثيل هبتان ✓
    o_d = cond(['CH₃', 'CH₂', 'CH', 'CH₂', 'CH', 'CH₂', 'CH₃'], [(2, 1, ['CH₃']), (4, -1, ['CH₃'])])          # 3،5-ثنائي ميثيل هبتان
    grid_panels(P + '34dmhep-four.svg', [('(أ)',) + o_a + ([],), ('(ب)',) + o_b + ([],), ('(ج)',) + o_c + ([],), ('(د)',) + o_d + ([],)], cols=1, gapy=6, label_gap=26)
    s_a = chain_skel(5, [(1, 1, 1)])               # 2-ميثيل بنتان
    s_b = chain_skel(6, [(1, -1, 1)])              # 2-ميثيل هكسان ✓
    s_c = chain_skel(6, [(0, -1, 1)])              # «ميثيل على الذرة 1» = هبتان
    s_d = chain_skel(6, [(2, 1, 1)])               # 3-ميثيل هكسان
    grid_panels(P + '2mhex-skel-four.svg', [('(أ)',) + s_a + ([],), ('(ب)',) + s_b + ([],), ('(ج)',) + s_c + ([],), ('(د)',) + s_d + ([],)], cols=2)
    dmb = A.full({'c0': (0, 0), 'c1': (1, 0), 'c2': (2, 0), 'c3': (3, 0), 'm1': (1, -2), 'm2': (1, 2)},
                 [('c0', 'c1'), ('c1', 'c2'), ('c2', 'c3'), ('c1', 'm1'), ('c1', 'm2')])
    single(P + '22dmb-full.svg', *dmb)

    # ===== O12 =====
    single(P + '3mhex-wrongnum.svg', *numbered_cond(['CH₃', 'CH₂', 'CH₂', 'CH', 'CH₂', 'CH₃'], [(3, 1, ['CH₃'])], ['1', '2', '3', '4', '5', '6']))
    single(P + 'bent-24dmhex.svg', *cond(['CH₃', 'CH', 'CH₂', 'CH', 'CH₃'], [(1, 1, ['CH₃']), (3, -1, ['CH₂', 'CH₃'])]))
    single(P + '4e2mhep.svg', *cond(['CH₃', 'CH₂', 'CH₂', 'CH', 'CH₂', 'CH', 'CH₃'], [(3, -1, ['CH₂', 'CH₃']), (5, 1, ['CH₃'])]))
    eb = A.full({'c0': (0, 0), 'c1': (1, 0), 'c2': (2, 0), 'c3': (3, 0), 'e1': (1, 2), 'e2': (1, 3)},
                [('c0', 'c1'), ('c1', 'c2'), ('c2', 'c3'), ('c1', 'e1'), ('e1', 'e2')])
    single(P + '2ebutane-full.svg', *eb)

    # ===== O13 =====
    print('hbonds', hbond(P + 'hbond.svg'))
    bars(P + 'bars.svg')
    shapes(P + 'shapes.svg')
