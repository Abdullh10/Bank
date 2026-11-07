# رسوم الدرس 4-4 (متشكلات الهيدروكربونات): متشكلات بنائية (C₅H₁₂ و C₄H₁₀)، متشكلات سيس/ترانس،
# صيغ إسقاط حول ذرة كربون غير متماثلة، ومخطط مبسط لمرور الضوء المستقطب خلال محلول متشكل ضوئي.
# التشغيل: python3 data/chem22/gen/figs/C4-L4-a.py
import sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

ORANGE = '#d9822b'; PURPLE = '#6a4c9c'


def _w(s, size):
    """عرض تقريبي لنص كيميائي لاتيني (الأرقام منخفضة وأصغر)."""
    w = 0
    for ch in s:
        if ch.isdigit(): w += size * 0.42
        elif ch in 'Hm': w += size * 0.72
        elif ch in 'CNO': w += size * 0.70
        else: w += size * 0.6
    return w


def chem(x, y, s, size=17, color=INK, anchor='middle', weight='normal'):
    """نص كيميائي لاتيني (LTR) والأرقام فيه سفلية: CH3CH2 → CH₃CH₂."""
    out, low = '', False
    for part in re.findall(r'\d+|[^\d]+', s):
        if part.isdigit():
            out += f'<tspan font-size="{size * 0.7:.1f}" dy="{"0" if low else "5"}">{part}</tspan>'; low = True
        else:
            out += f'<tspan dy="{"-5" if low else "0"}">{esc(part)}</tspan>'; low = False
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'{FONT} direction="ltr">{out}</text>')


def label(x, y, s, size=17, align='c', color=INK):
    """قناع أبيض + نص ذرة/مجموعة مركزه (x, y). align: c وسط، l يمتد يمينًا من الذرة، r يمتد يسارًا منها."""
    w = _w(s, size); first = _w(s[:2] if len(s) > 1 and s[1].isdigit() else s[:1], size)
    if align == 'c': x0 = x - w / 2
    elif align == 'l': x0 = x - first / 2 - 2
    else:
        last = _w(re.findall(r'[A-Z][a-z]?\d*$', s)[0], size)
        x0 = x + last / 2 + 2 - w
    m = f'<rect x="{x0 - 3:.1f}" y="{y - size * 0.62:.1f}" width="{w + 6:.1f}" height="{size * 1.25 + 4:.1f}" fill="#fff"/>'
    return m + chem(f'{x0:.1f}', f'{y + size * 0.36:.1f}', s, size, color, 'start')


def bond(x1, y1, x2, y2, order=1, color=INK, w=2.2, gap=4.5):
    if order == 1: return L(x1, y1, x2, y2, color, w)
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); nx, ny = -dy / d * gap, dx / d * gap
    if order == 2:
        return L(x1 + nx, y1 + ny, x2 + nx, y2 + ny, color, w) + L(x1 - nx, y1 - ny, x2 - nx, y2 - ny, color, w)
    return L(x1, y1, x2, y2, color, w) + bond(x1, y1, x2, y2, 2, color, w, gap * 1.5)


def mol(atoms, bonds, size=17):
    """atoms = [(x, y, label, align)] (label '' = رأس في صيغة هيكلية)؛ bonds = [(i, j, order)]."""
    b = ''.join(bond(atoms[i][0], atoms[i][1], atoms[j][0], atoms[j][1], o) for i, j, o in bonds)
    for a in atoms:
        if a[2]: b += label(a[0], a[1], a[2], size, a[3] if len(a) > 3 else 'c')
    return b


def tag(x, y, s, size=16, color=INK):
    return T(x, y, s, size, color=color, weight='bold')


def chain(x0, y, groups, step=88):
    """سلسلة أفقية مكثفة: groups = قائمة نصوص؛ يعيد (atoms, bonds)."""
    atoms = [(x0 + k * step, y, g, 'c') for k, g in enumerate(groups)]
    bonds = [(k, k + 1, 1) for k in range(len(groups) - 1)]
    return atoms, bonds


def branched(x0, y, groups, branches, step=88, blen=62):
    """branches = [(index, label, 'up'|'down')]"""
    atoms, bonds = chain(x0, y, groups, step)
    for i, lab, d in branches:
        atoms.append((atoms[i][0], y + (-blen if d == 'up' else blen), lab, 'c')); bonds.append((i, len(atoms) - 1, 1))
    return atoms, bonds


def alkene(cx, cy, tl, bl, tr, br, cc=64, sub=58, size=17):
    """رابطة ثنائية أفقية C=C مركزها (cx, cy) والمجموعات الأربع بزاوية 120°."""
    xa, xb = cx - cc / 2, cx + cc / 2
    ax, ay = sub * math.cos(math.radians(60)), sub * math.sin(math.radians(60))
    atoms = [(xa, cy, 'C'), (xb, cy, 'C'),
             (xa - ax, cy - ay, tl, 'r'), (xa - ax, cy + ay, bl, 'r'),
             (xb + ax, cy - ay, tr, 'l'), (xb + ax, cy + ay, br, 'l')]
    return mol(atoms, [(0, 1, 2), (0, 2, 1), (0, 3, 1), (1, 4, 1), (1, 5, 1)], size)


def cross(cx, cy, top, left, right, bottom, arm=56, size=17, center='C'):
    """صيغة إسقاط: ذرة الكربون في الوسط وأربع مجموعات حولها."""
    atoms = [(cx, cy, center), (cx, cy - arm, top), (cx - arm - 6, cy, left, 'r'), (cx + arm + 6, cy, right, 'l'), (cx, cy + arm, bottom)]
    return mol(atoms, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)], size)


def divider(x, y1, y2):
    return L(x, y1, x, y2, MUTED, 1.2, '6 5')


# ---------------------------------------------------------------- الرسوم
def pentane_isomers(name, bp=True):
    h = 470; b = ''
    a, bo = chain(70, 70, ['CH3', 'CH2', 'CH2', 'CH2', 'CH3']); b += mol(a, bo) + tag(520, 76, '(1)')
    a, bo = branched(70, 215, ['CH3', 'CH', 'CH2', 'CH3'], [(1, 'CH3', 'up')]); b += mol(a, bo) + tag(520, 221, '(2)')
    a, bo = branched(70, 375, ['CH3', 'C', 'CH3'], [(1, 'CH3', 'up'), (1, 'CH3', 'down')]); b += mol(a, bo) + tag(520, 381, '(3)')
    if bp:
        b += T(470, 112, 'درجة الغليان = \u202a36°C\u202c', 14, 'end', MUTED)
        b += T(470, 257, 'درجة الغليان = \u202a28°C\u202c', 14, 'end', MUTED)
        b += T(470, 417, 'درجة الغليان = \u202a9°C\u202c', 14, 'end', MUTED)
    b += L(20, 135, 540, 135, '#dfe3ea', 1) + L(20, 290, 540, 290, '#dfe3ea', 1)
    save(name, svg(560, h, b))


def butane_pair(name):
    b = ''
    a, bo = chain(60, 90, ['CH3', 'CH2', 'CH2', 'CH3'], 80); b += mol(a, bo) + tag(180, 165, '(1)')
    a, bo = branched(400, 120, ['CH3', 'CH', 'CH3'], [(1, 'CH3', 'up')], 80); b += mol(a, bo) + tag(480, 165, '(2)')
    b += divider(340, 25, 175)
    save(name, svg(620, 190, b))


def cyclo_vs_chain(name):
    b = ''
    # (1) بنتان حلقي: خماسي منتظم بصيغة هيكلية
    r = 52; cx, cy = 150, 95
    pts = [(cx + r * math.sin(math.radians(72 * k)), cy - r * math.cos(math.radians(72 * k))) for k in range(5)]
    b += f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    b += tag(cx, 190, '(1)')
    # (2) بنتان: سلسلة متعرجة
    z = [(330 + 52 * k, 110 if k % 2 == 0 else 80) for k in range(5)]
    b += f'<polyline points="{" ".join(f"{x},{y}" for x, y in z)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    b += tag(434, 190, '(2)') + divider(270, 25, 200)
    save(name, svg(560, 210, b))


def two_alkenes(name, A, B, labels=('(1)', '(2)'), w=620, h=210):
    b = alkene(150, 95, *A) + alkene(w - 150, 95, *B)
    b += tag(150, h - 18, labels[0]) + tag(w - 150, h - 18, labels[1]) + divider(w / 2, 20, h - 10)
    save(name, svg(w, h, b))


def three_alkenes(name, items, w=640, h=420):
    b = alkene(160, 95, *items[0]) + tag(160, 185, '(1)')
    b += alkene(470, 95, *items[1]) + tag(470, 185, '(2)')
    b += alkene(315, 300, *items[2]) + tag(315, 395, '(3)')
    b += L(20, 210, w - 20, 210, '#dfe3ea', 1) + divider(315, 20, 195)
    save(name, svg(w, h, b))


def four_alkenes(name, items, w=640, h=420):
    pos = [(160, 95), (470, 95), (160, 300), (470, 300)]
    b = ''
    for k, ((x, y), it) in enumerate(zip(pos, items)):
        b += alkene(x, y, *it) + tag(x, y + 88, f'({k + 1})')
    b += L(20, 205, w - 20, 205, '#dfe3ea', 1) + divider(315, 20, h - 15)
    save(name, svg(w, h, b))


def wxyz(name):
    b = cross(150, 110, 'W', 'Z', 'X', 'Y') + cross(410, 110, 'W', 'Z', 'Y', 'X')
    b += tag(150, 205, '(1)') + tag(410, 205, '(2)') + divider(280, 25, 215)
    save(name, svg(560, 230, b))


def alanine(name):
    b = cross(150, 115, 'COOH', 'H2N', 'H', 'CH3') + cross(430, 115, 'COOH', 'H', 'NH2', 'CH3')
    b += tag(150, 215, '(1)') + tag(430, 215, '(2)')
    b += L(290, 25, 290, 200, BLUE, 2, '8 5') + T(290, 222, 'مرآة', 14, color=BLUE, weight='bold')
    save(name, svg(580, 240, b))


def numbered_chain(name):
    """3-ميثيل هكسان مع ترقيم ذرات الكربون للسؤال (الرقم 7 لمجموعة الميثيل الفرعية)."""
    a, bo = branched(55, 150, ['CH3', 'CH2', 'CH', 'CH2', 'CH2', 'CH3'], [(2, 'CH3', 'up')], 92, 70)
    b = mol(a, bo)
    nums = [(a[k][0], 190, str(k + 1)) for k in range(6)] + [(a[6][0] + 38, a[6][1], '7')]
    for x, y, s in nums:
        b += f'<circle cx="{x}" cy="{y}" r="12" fill="#eaf2fb" stroke="{BLUE}" stroke-width="1.5"/>' + T(x, y + 5, s, 14, color=BLUE, weight='bold')
    save(name, svg(580, 215, b))


def methylpentane(name):
    """3-ميثيل بنتان بصيغة بنائية مكثفة (دون ترقيم)."""
    a, bo = branched(60, 120, ['CH3', 'CH2', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'up')], 92, 70)
    save(name, svg(500, 160, mol(a, bo)))


def four_centers(name):
    items = [('H', 'CH3', 'CH2CH3', 'H'), ('H', 'CH3', 'CH2CH2CH3', 'CH2CH3'),
             ('CH3', 'CH3', 'CH2CH3', 'H'), ('H', 'CH2CH3', 'CH2CH3', 'CH3')]
    pos = [(150, 95), (450, 95), (150, 290), (450, 290)]
    b = ''
    for k, ((x, y), (t, l, r, bt)) in enumerate(zip(pos, items)):
        b += cross(x, y, t, l, r, bt, arm=50) + tag(x, y + 92, f'({k + 1})')
    b += L(20, 200, 620, 200, '#dfe3ea', 1) + divider(300, 20, 395)
    save(name, svg(640, 405, b))


def polarimeter(name, w=680, h=260):
    b = ''
    # مصدر الضوء
    b += f'<circle cx="60" cy="130" r="22" fill="#fff6c9" stroke="{ORANGE}" stroke-width="2.5"/>'
    b += L(52, 152, 68, 152, INK, 3) + T(60, 190, 'مصدر', 14) + T(60, 208, 'ضوء عادي', 14)
    # ضوء عادي: اهتزازات في مستويات عدة
    for ang in (0, 45, 90, 135):
        c, s = math.cos(math.radians(ang)) * 24, math.sin(math.radians(ang)) * 24
        b += L(135 - c, 130 - s, 135 + c, 130 + s, ORANGE, 2.2)
    b += ARROW(88, 130, 105, 130, ORANGE, 2) + ARROW(165, 130, 192, 130, ORANGE, 2)
    # المرشح
    b += f'<rect x="198" y="72" width="26" height="116" fill="#eef1f5" stroke="{INK}" stroke-width="2"/>'
    for k in range(9): b += L(203 + k * 2.2, 78, 203 + k * 2.2, 182, MUTED, 0.9)
    b += T(211, 60, 'مرشح استقطاب', 14, weight='bold')
    # ضوء مستقطب: مستوى رأسي واحد
    b += ARROW(268, 108, 268, 152, PURPLE, 2.5) + ARROW(268, 152, 268, 108, PURPLE, 2.5)
    b += ARROW(232, 130, 290, 130, PURPLE, 2) + T(268, 206, 'ضوء مستقطب', 14, color=PURPLE)
    # أنبوب العينة
    b += f'<rect x="305" y="105" width="170" height="50" rx="10" fill="#e6f1f8" stroke="{BLUE}" stroke-width="2.5"/>'
    b += f'<ellipse cx="305" cy="130" rx="8" ry="25" fill="#d4e7f4" stroke="{BLUE}" stroke-width="2"/>'
    b += T(390, 90, 'أنبوب العينة', 14, weight='bold') + T(390, 182, 'محلول متشكل ضوئي', 14)
    b += ARROW(485, 130, 525, 130, PURPLE, 2)
    # المستوى بعد الخروج: مائل بزاوية عن الرأسي
    cx, cy, R = 590, 130, 40
    b += L(cx, cy - R - 8, cx, cy + R + 8, MUTED, 1.4, '5 4')
    t = math.radians(30)
    b += ARROW(cx - R * math.sin(t), cy + R * math.cos(t), cx + R * math.sin(t), cy - R * math.cos(t), PURPLE, 2.5)
    b += ARROW(cx + R * math.sin(t), cy - R * math.cos(t), cx - R * math.sin(t), cy + R * math.cos(t), PURPLE, 2.5)
    b += f'<path d="M {cx} {cy - 30} A 30 30 0 0 1 {cx + 30 * math.sin(t):.1f} {cy - 30 * math.cos(t):.1f}" fill="none" stroke="{RED}" stroke-width="2"/>'
    b += T(cx, 74, 'زاوية الدوران', 14, color=RED, weight='bold') + T(cx, 206, 'مستوى الاستقطاب', 14) + T(cx, 224, 'بعد خروج الضوء', 14)
    save(name, svg(w, h, b))


if __name__ == '__main__':
    P = 'c4-l4a-'
    pentane_isomers(P + 'c5h12-bp.svg', bp=True)
    pentane_isomers(P + 'c5h12.svg', bp=False)
    butane_pair(P + 'c4h10-pair.svg')
    cyclo_vs_chain(P + 'cyclo-vs-chain.svg')
    # (tl, bl, tr, br)
    two_alkenes(P + '2-butene.svg', ('CH3', 'H', 'CH3', 'H'), ('CH3', 'H', 'H', 'CH3'))
    two_alkenes(P + '3-hexene.svg', ('CH3CH2', 'H', 'H', 'CH2CH3'), ('CH3CH2', 'H', 'CH2CH3', 'H'))
    two_alkenes(P + 'same-cis.svg', ('CH3', 'H', 'CH3', 'H'), ('H', 'CH3', 'H', 'CH3'))
    three_alkenes(P + 'c5h10-three.svg', [('CH3', 'H', 'CH2CH3', 'H'), ('CH3', 'H', 'H', 'CH2CH3'), ('H', 'H', 'CH2CH2CH3', 'H')])
    four_alkenes(P + 'which-cistrans.svg', [('H', 'H', 'CH2CH3', 'H'), ('H', 'H', 'CH3', 'CH3'),
                                             ('CH3', 'CH3', 'CH3', 'H'), ('CH3', 'H', 'H', 'CH2CH3')])
    wxyz(P + 'wxyz.svg')
    alanine(P + 'alanine.svg')
    numbered_chain(P + 'numbered-chain.svg')
    methylpentane(P + 'methylpentane.svg')
    four_centers(P + 'four-centers.svg')
    polarimeter(P + 'polarimeter.svg')
