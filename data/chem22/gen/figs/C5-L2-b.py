# رسوم الدرس 5-2 (الكحولات والإيثرات والأمينات) — النصف الثاني: تحديد المجموعات الوظيفية، والروابط الهيدروجينية،
# وتسمية الكحولات والإيثرات والأمينات، ومقارنة درجات الغليان، وذائبية الكحولات وطول السلسلة.
# التشغيل: python3 data/chem22/gen/figs/C5-L2-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('c5l2a', os.path.join(os.path.dirname(__file__), 'C5-L2-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
grid, label, tag, sep_h, sep_v, hexagon, hchain, chem = A.grid, A.label, A.tag, A.sep_h, A.sep_v, A.hexagon, A.hchain, A.chem
HB = A.HB
P = 'c5-l2b-'
S = 58


def row(ox, oy, groups, subs=(), step=S):
    """سلسلة مكثفة أفقية: groups = [label,...] (تُربط متتابعة)، subs = [(index, label, 'down'|'up')]."""
    atoms, bonds = {}, []
    for i, g in enumerate(groups):
        al = 'c'
        if i == 0 and g in ('H2N', 'HO'): al = 'r'
        if i == len(groups) - 1 and g in ('NH2', 'OH'): al = 'l'
        atoms[f'g{i}'] = (i * 1.35, 0, g, al)
        if i: bonds.append((f'g{i-1}', f'g{i}'))
    for k, (i, g, d) in enumerate(subs):
        atoms[f's{k}'] = (i * 1.35, 1.0 if d == 'down' else -1.0, g); bonds.append((f'g{i}', f's{k}'))
    return grid(ox, oy, atoms, bonds, step=step)


def polygon(cx, cy, n, r, rot=90):
    pts = [(cx + r * math.cos(math.radians(rot + 360 / n * k)), cy - r * math.sin(math.radians(rot + 360 / n * k))) for k in range(n)]
    s = f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    return s, pts


def ring_with(n, cx, cy, r, tail, blen=40):
    """حلقة (n أضلاع) برأس علوي يرتبط بسلسلة رأسية tail = [labels] تُرسم إلى الأعلى."""
    s, pts = polygon(cx, cy, n, r)
    x, y = pts[0]
    # رسم بسيط: رابطة من الحلقة إلى أول ذرة، ثم روابط رأسية بين الذرات
    ys = [y - blen - 10 - k * (blen + 14) for k in range(len(tail))]
    s += L(x, y, x, ys[0] + 12, INK, 2.4)
    for k in range(1, len(tail)): s += L(x, ys[k - 1] - 12, x, ys[k] + 12, INK, 2.4)
    for k, lab in enumerate(tail): s += label(x, ys[k], lab, 17)
    return s


# ---------------------------------------------------------------- O08 المجموعات الوظيفية
def o08_ether(name):
    b = row(50, 70, ['CH3', 'CH2', 'O', 'CH2', 'CH2', 'CH2', 'CH3'])
    save(name, svg(640, 130, b))


def o08_amine(name):
    b = row(70, 60, ['CH3', 'CH', 'CH2', 'CH3'], [(1, 'NH2', 'down')])
    save(name, svg(380, 150, b))


def o08_ethanolamine(name):
    b = row(70, 70, ['HO', 'CH2', 'CH2', 'NH2'])
    save(name, svg(390, 130, b))


def o08_four(name):
    b = row(60, 50, ['CH3', 'CH2', 'CH2', 'OH']) + tag(170, 95, '(1)')
    b += row(400, 50, ['CH3', 'CH2', 'O', 'CH2', 'CH3']) + tag(520, 95, '(2)')
    b += sep_h(115, 20, 750) + sep_v(360, 20, 240)
    b += row(60, 170, ['CH3', 'CH2', 'CH2', 'NH2']) + tag(170, 220, '(3)')
    b += row(400, 170, ['CH3', 'CH2', 'CH2', 'Cl']) + tag(510, 220, '(4)')
    save(name, svg(770, 240, b))


def o08_multi(name):
    b = row(60, 70, ['HO', 'CH2', 'CH2', 'O', 'CH2', 'CH2', 'NH2'])
    save(name, svg(640, 130, b))


# ---------------------------------------------------------------- O09 الروابط الهيدروجينية
def mol(ox, oy, atoms, bonds, step=50):
    return grid(ox, oy, atoms, bonds, step=step)


def o09_candidates(name):
    """أربعة أزواج من الجزيئات وبين كل زوج خط متقطع بين ذرتين مختلفتين."""
    b = ''
    st = 50
    # (1) ميثانول··· ميثانول: H (من OH) ··· O
    b += mol(40, 60, {'c': (0, 0, 'CH3'), 'o': (1.3, 0, 'O'), 'h': (2.3, 0, 'H')}, [('c', 'o'), ('o', 'h')], st)
    b += L(40 + 2.3 * st + 8, 68, 40 + 3.4 * st - 6, 110, HB, 2.4, '5 5')
    b += mol(40 + 3.4 * st, 120, {'o': (0, 0, 'O'), 'h': (0, 1.0, 'H'), 'c': (1.3, 0, 'CH3')}, [('o', 'h'), ('o', 'c')], st)
    b += tag(170, 215, '(1)')
    # (2) ميثانول··· ميثانول: H (من CH3 مكتوبًا كاملًا) ··· O
    ox = 400
    b += mol(ox, 60, {'h1': (0, 0, 'H'), 'c': (1, 0, 'C'), 'ha': (1, -1, 'H'), 'hb': (1, 1, 'H'), 'o': (2, 0, 'O'), 'h': (3, 0, 'H')},
             [('h1', 'c'), ('c', 'ha'), ('c', 'hb'), ('c', 'o'), ('o', 'h')], 46)
    b += L(ox + 46 + 2, 60 + 46 + 12, ox + 46 + 50 - 6, 165 - 13, HB, 2.4, '5 5')
    b += mol(ox + 46 + 50, 165, {'o': (0, 0, 'O'), 'h': (-1, 0, 'H'), 'c': (1.3, 0, 'CH3')}, [('o', 'h'), ('o', 'c')], 46)
    b += tag(530, 215, '(2)')
    b += sep_h(235, 20, 740) + sep_v(370, 20, 450)
    # (3) ثنائي ميثيل إيثر··· ثنائي ميثيل إيثر: O ··· O
    b += mol(50, 290, {'a': (0, 0, 'CH3'), 'o': (1.3, 0, 'O'), 'c': (2.6, 0, 'CH3')}, [('a', 'o'), ('o', 'c')], st)
    b += L(50 + 1.3 * st, 304, 50 + 1.3 * st, 366, HB, 2.4, '5 5')
    b += mol(50, 380, {'a': (0, 0, 'CH3'), 'o': (1.3, 0, 'O'), 'c': (2.6, 0, 'CH3')}, [('a', 'o'), ('o', 'c')], st)
    b += tag(170, 435, '(3)')
    # (4) ميثانول ··· ميثانول: H (من OH) ··· H (من OH)
    ox = 420
    b += mol(ox, 290, {'c': (0, 0, 'CH3'), 'o': (1.3, 0, 'O'), 'h': (2.3, 0, 'H')}, [('c', 'o'), ('o', 'h')], st)
    b += L(ox + 2.3 * st, 302, ox + 2.3 * st, 368, HB, 2.4, '5 5')
    b += mol(ox, 380, {'c': (0, 0, 'CH3'), 'o': (1.3, 0, 'O'), 'h': (2.3, 0, 'H')}, [('c', 'o'), ('o', 'h')], st)
    b += tag(530, 435, '(4)')
    save(name, svg(760, 455, b))


def o09_methylamine(name):
    st = 52
    b = mol(60, 80, {'c': (0, 0, 'CH3'), 'n': (1.3, 0, 'N'), 'h1': (2.3, 0, 'H'), 'h2': (1.3, -1, 'H')},
            [('c', 'n'), ('n', 'h1'), ('n', 'h2')], st)
    nx, ny = 60 + 3.5 * st, 170
    b += L(60 + 2.3 * st + 8, 90, nx - 8, ny - 12, HB, 2.4, '5 5')
    b += mol(nx, ny, {'n': (0, 0, 'N'), 'h1': (0, 1, 'H'), 'h2': (-1, 0.6, 'H'), 'c': (1.3, 0, 'CH3')},
             [('n', 'h1'), ('n', 'h2'), ('n', 'c')], st)
    save(name, svg(430, 250, b))


def o09_ethanol_water(name):
    """إيثانول في الوسط، وجزيء ماء (أ) يمنح H لأكسجين الإيثانول، وجزيء ماء (ب) يستقبل H مجموعة OH."""
    st = 52
    ox, oy = 60, 150
    b = mol(ox, oy, {'a': (0, 0, 'CH3'), 'b': (1.3, 0, 'CH2'), 'o': (2.6, 0, 'O'), 'h': (3.6, 0, 'H')},
            [('a', 'b'), ('b', 'o'), ('o', 'h')], st)
    Ox = ox + 2.6 * st
    # ماء فوق أكسجين الإيثانول: H متجه إلى الأسفل
    b += L(Ox, oy - 14, Ox, oy - 58, HB, 2.4, '5 5')
    b += mol(Ox, oy - 72, {'h': (0, 0, 'H'), 'o': (0, -1, 'O'), 'h2': (1, -1, 'H')}, [('h', 'o'), ('o', 'h2')], st)
    b += tag(Ox - 50, oy - 110, '(أ)')
    # ماء يمين H الإيثانول
    Hx = ox + 3.6 * st
    b += L(Hx + 9, oy, Hx + 62, oy, HB, 2.4, '5 5')
    b += mol(Hx + 76, oy, {'o': (0, 0, 'O'), 'h1': (0.8, -0.8, 'H'), 'h2': (0.8, 0.8, 'H')}, [('o', 'h1'), ('o', 'h2')], st)
    b += tag(Hx + 90, oy + 85, '(ب)')
    save(name, svg(470, 250, b))


# ---------------------------------------------------------------- O10 تسمية الكحولات
def o10_pentanol(name):
    atoms, bonds = hchain(5, 0, 0, extra={(4, 1): 'OH'})
    atoms['HR'] = (6, 0, 'H'); bonds.append(('C4', 'HR'))
    save(name, svg(430, 175, grid(55, 80, atoms, bonds, step=52)))


def o10_cyclopentanol(name):
    s = ring_with(5, 130, 150, 50, ['OH'])
    save(name, svg(260, 230, s))


def o10_ethanediol(name):
    atoms, bonds = hchain(2, 0, 0, extra={(1, 1): 'OH', (2, 1): 'OH'})
    atoms['HR'] = (3, 0, 'H'); bonds.append(('C1', 'HR'))
    save(name, svg(270, 175, grid(55, 75, atoms, bonds, step=52)))


def o10_propanediol(name):
    b = row(70, 60, ['CH3', 'CH', 'CH2', 'OH'], [(1, 'OH', 'down')])
    save(name, svg(370, 150, b))


def o10_essay(name):
    b = row(60, 55, ['CH3', 'CH2', 'CH', 'CH2', 'CH3'], [(2, 'OH', 'down')]) + tag(560, 62, '(أ)')
    b += sep_h(140, 20, 620)
    b += row(60, 185, ['CH3', 'CH', 'CH', 'CH3'], [(1, 'OH', 'down'), (2, 'CH3', 'down')]) + tag(560, 192, '(ب)')
    b += sep_h(270, 20, 620)
    b += row(80, 315, ['HO', 'CH2', 'CH2', 'CH2', 'OH']) + tag(560, 322, '(ج)')
    save(name, svg(640, 350, b))


# ---------------------------------------------------------------- O11 تسمية الإيثرات
def o11_methylpropyl(name):
    save(name, svg(450, 120, row(55, 60, ['CH3', 'O', 'CH2', 'CH2', 'CH3'])))


def o11_diethyl(name):
    at = {'H0': (0, 0, 'H'), 'C0': (1, 0, 'C'), 'a': (1, -1, 'H'), 'b': (1, 1, 'H'),
          'C1': (2, 0, 'C'), 'c': (2, -1, 'H'), 'd': (2, 1, 'H'), 'O': (3, 0, 'O'),
          'C2': (4, 0, 'C'), 'e': (4, -1, 'H'), 'f': (4, 1, 'H'),
          'C3': (5, 0, 'C'), 'g': (5, -1, 'H'), 'h': (5, 1, 'H'), 'H1': (6, 0, 'H')}
    bd = [('H0', 'C0'), ('C0', 'a'), ('C0', 'b'), ('C0', 'C1'), ('C1', 'c'), ('C1', 'd'), ('C1', 'O'), ('O', 'C2'),
          ('C2', 'e'), ('C2', 'f'), ('C2', 'C3'), ('C3', 'g'), ('C3', 'h'), ('C3', 'H1')]
    save(name, svg(420, 175, grid(55, 85, at, bd, step=52)))


def o11_cyhex_methyl(name):
    save(name, svg(260, 290, ring_with(6, 130, 225, 48, ['O', 'CH3'])))


def o11_cypent_ethyl(name):
    save(name, svg(260, 350, ring_with(5, 130, 290, 50, ['O', 'CH2', 'CH3'])))


def o11_essay(name):
    b = row(200, 50, ['CH3', 'O', 'CH3']) + tag(570, 57, '(أ)')
    b += sep_h(95, 20, 620)
    b += row(60, 140, ['CH3', 'CH2', 'CH2', 'O', 'CH2', 'CH3']) + tag(570, 147, '(ب)')
    b += sep_h(185, 20, 620)
    b += row(60, 230, ['CH3', 'CH2', 'CH2', 'CH2', 'O', 'CH3']) + tag(570, 237, '(ج)')
    save(name, svg(640, 265, b))


# ---------------------------------------------------------------- O12 تسمية الأمينات
def o12_aminopentane(name):
    save(name, svg(450, 150, row(55, 60, ['CH3', 'CH2', 'CH2', 'CH', 'CH3'], [(3, 'NH2', 'down')])))


def o12_cyclopentylamine(name):
    save(name, svg(260, 230, ring_with(5, 130, 150, 50, ['NH2'])))


def o12_butanediamine(name):
    save(name, svg(560, 120, row(70, 60, ['H2N', 'CH2', 'CH2', 'CH2', 'CH2', 'NH2'])))


def o12_triamine(name):
    save(name, svg(470, 150, row(70, 60, ['H2N', 'CH2', 'CH', 'CH2', 'NH2'], [(2, 'NH2', 'down')])))


def o12_essay(name):
    b = row(140, 50, ['H2N', 'CH2', 'CH2', 'NH2']) + tag(600, 57, '(أ)')
    b += sep_h(95, 20, 660)
    b += row(50, 140, ['CH3', 'CH', 'CH2', 'CH2', 'CH', 'CH3'], [(1, 'NH2', 'down'), (4, 'NH2', 'down')]) + tag(600, 147, '(ب)')
    b += sep_h(225, 20, 660)
    b += row(170, 270, ['CH3', 'CH2', 'NH2']) + tag(600, 277, '(ج)')
    save(name, svg(680, 305, b))


# ---------------------------------------------------------------- O13 مخطط أعمدة لدرجات الغليان
def o13_bp_chart(name):
    data = [('C₂H₆O', 'الإيثانول', 78, 'ثنائي ميثيل إيثر', -25),
            ('C₃H₈O', '1-بروبانول', 97, 'إيثيل ميثيل إيثر', 7),
            ('C₄H₁₀O', '1-بيوتانول', 118, 'ثنائي إيثيل إيثر', 35)]
    W, H = 640, 480
    X0, X1 = 90, 600
    def y(v): return 300 - v * 2.0          # 0 عند y=300؛ 120 عند y=60
    b = L(X0, y(130), X0, y(-40), INK, 2)
    for v in (-40, -20, 0, 20, 40, 60, 80, 100, 120):
        b += L(X0 - 5, y(v), X0, y(v)) + T(X0 - 9, y(v) + 5, str(v).replace('-', '−'), 13, 'end')
        b += L(X0, y(v), X1, y(v), '#e6e9ef', 1)
    b += L(X0, y(0), X1, y(0), INK, 1.6)
    b += f'<text transform="translate({X0 - 52},{y(45)}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" {FONT}>درجة الغليان (°C)</text>'
    gw = (X1 - X0) / 3
    for k, (f, a, va, e, ve) in enumerate(data):
        cx = X0 + gw * (k + 0.5)
        for dx, v, col in ((-34, va, BLUE), (34, ve, RED)):
            top, bot = (y(v), y(0)) if v >= 0 else (y(0), y(v))
            b += f'<rect x="{cx + dx - 26}" y="{top}" width="52" height="{bot - top}" fill="{col}" opacity="0.85"/>'
            ty = y(v) - 7 if v >= 0 else y(v) + 18
            b += T(cx + dx, ty, (str(v).replace('-', '−')), 14, color=INK, weight='bold')
        b += T(cx, y(-40) + 26, f, 15, weight='bold')
    # مفتاح الألوان
    b += f'<rect x="440" y="{H - 52}" width="18" height="14" fill="{BLUE}"/>' + T(432, H - 40, 'الكحول ذو السلسلة غير المتفرعة', 13, 'end', rtl=True)
    b += f'<rect x="440" y="{H - 28}" width="18" height="14" fill="{RED}"/>' + T(432, H - 16, 'الإيثر الذي له الصيغة الجزيئية نفسها', 13, 'end', rtl=True)
    save(name, svg(W, H, b))


def o13_c3h8o(name):
    atoms, bonds = hchain(3, 0, 0)
    atoms['O'] = (4, 0, 'O'); atoms['HO'] = (5, 0, 'H'); bonds += [('C2', 'O'), ('O', 'HO')]
    b = grid(40, 80, atoms, bonds, step=48) + tag(160, 170, '(1)')
    at2 = {'H0': (0, 0, 'H'), 'C0': (1, 0, 'C'), 'a': (1, -1, 'H'), 'b': (1, 1, 'H'), 'O': (2, 0, 'O'),
           'C1': (3, 0, 'C'), 'c': (3, -1, 'H'), 'd': (3, 1, 'H'), 'C2': (4, 0, 'C'), 'e': (4, -1, 'H'), 'f': (4, 1, 'H'), 'H1': (5, 0, 'H')}
    b += grid(370, 80, at2, [('H0', 'C0'), ('C0', 'a'), ('C0', 'b'), ('C0', 'O'), ('O', 'C1'), ('C1', 'c'), ('C1', 'd'),
                            ('C1', 'C2'), ('C2', 'e'), ('C2', 'f'), ('C2', 'H1')], step=48) + tag(490, 170, '(2)')
    b += sep_v(335, 20, 185)
    save(name, svg(660, 190, b))


# ---------------------------------------------------------------- O14 طول السلسلة
def o14_chain(name):
    def r(oy, groups, t):
        n = len(groups)
        x0 = 60
        x_oh = x0 + (n - 1) * 1.35 * 52
        s = f'<rect x="{x0 - 30}" y="{oy - 22}" width="{x_oh - x0 - 1.35 * 52 + 60:.0f}" height="44" rx="10" fill="#eef1f5" stroke="{MUTED}" stroke-dasharray="5 4"/>'
        s += f'<rect x="{x_oh - 26:.0f}" y="{oy - 22}" width="52" height="44" rx="10" fill="#fdecea" stroke="{RED}"/>'
        s += row(x0, oy, groups, step=52) + tag(660, oy + 6, t)
        return s
    b = r(50, ['CH3', 'OH'], '(1)')
    b += r(130, ['CH3', 'CH2', 'CH2', 'CH2', 'OH'], '(2)')
    b += r(210, ['CH3', 'CH2', 'CH2', 'CH2', 'CH2', 'CH2', 'CH2', 'OH'], '(3)')
    save(name, svg(700, 250, b))


if __name__ == '__main__':
    o08_ether(P + 'o08-ether.svg'); o08_amine(P + 'o08-amine.svg'); o08_ethanolamine(P + 'o08-ethanolamine.svg')
    o08_four(P + 'o08-four.svg'); o08_multi(P + 'o08-multi.svg')
    o09_candidates(P + 'o09-candidates.svg'); o09_methylamine(P + 'o09-methylamine.svg'); o09_ethanol_water(P + 'o09-ethanol-water.svg')
    o10_pentanol(P + 'o10-pentanol.svg'); o10_cyclopentanol(P + 'o10-cyclopentanol.svg'); o10_ethanediol(P + 'o10-ethanediol.svg')
    o10_propanediol(P + 'o10-propanediol.svg'); o10_essay(P + 'o10-essay.svg')
    o11_methylpropyl(P + 'o11-methylpropyl.svg'); o11_diethyl(P + 'o11-diethyl.svg'); o11_cyhex_methyl(P + 'o11-cyhex-methyl.svg')
    o11_cypent_ethyl(P + 'o11-cypent-ethyl.svg'); o11_essay(P + 'o11-essay.svg')
    o12_aminopentane(P + 'o12-aminopentane.svg'); o12_cyclopentylamine(P + 'o12-cyclopentylamine.svg')
    o12_butanediamine(P + 'o12-butanediamine.svg'); o12_triamine(P + 'o12-triamine.svg'); o12_essay(P + 'o12-essay.svg')
    o13_bp_chart(P + 'o13-bp-chart.svg'); o13_c3h8o(P + 'o13-c3h8o.svg')
    o14_chain(P + 'o14-chain.svg')
