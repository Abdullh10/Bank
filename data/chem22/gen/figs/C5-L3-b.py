# رسوم الدرس 5-3 (مركبات الكربونيل — النصف الثاني): المجموعات الوظيفية، الروابط الهيدروجينية في الأحماض الكربوكسيلية،
# تسمية الإسترات والأميدات، تأين الحمض الكربوكسيلي، الإسترات في النكهات، اليوريا.
# التشغيل: python3 data/chem22/gen/figs/C5-L3-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('c5l3a', os.path.join(os.path.dirname(__file__), 'C5-L3-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
mol, row, single, grid, ring6, U, FS = A.mol, A.row, A.single, A.grid, A.ring6, A.U, A.FS

P = 'c5-l3b-'

def single_extra(name, n, e, extra_fn=None, pad=28):
    """مثل single مع إضافة عناصر (أرقام/دائرة حلقة) بإحداثيات الوحدات بعد الإزاحة."""
    _, bb = mol(n, e)
    ox, oy = pad - bb[0], pad - bb[1]
    bd, _ = mol(n, e, ox, oy)
    W, H = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    if extra_fn: bd += extra_fn(ox, oy)
    save(name, svg(round(W), round(H), bd))

def ring_circle(cx=0, cy=0):
    return lambda ox, oy: f'<circle cx="{ox + cx * U:.1f}" cy="{oy + cy * U:.1f}" r="{0.6 * U:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'

# ---------- O08: المجموعات الوظيفية ----------
def amide_general():
    single(P + 'amide-general.svg', *row([('R',), ('C', '=O'), ('N', 'H'), ('R′',)], dx=1.2))

def aspirin():
    n, e = ring6({})
    n['c1'] = (0, -2.0, 'C'); e.append(('r0', 'c1', 1))
    n['o1'] = (-0.87, -2.5, 'O'); e.append(('c1', 'o1', 2))
    n['oh'] = (0.95, -2.5, 'OH'); e.append(('c1', 'oh', 1))
    n['o2'] = (1.73, -1.0, 'O'); e.append(('r1', 'o2', 1))
    n['c2'] = (2.6, -0.5, 'C'); e.append(('o2', 'c2', 1))
    n['o3'] = (2.6, 0.5, 'O'); e.append(('c2', 'o3', 2))
    n['me'] = (3.75, -1.0, 'CH₃'); e.append(('c2', 'me', 1))
    single_extra(P + 'aspirin.svg', n, e, ring_circle())

def acetaminophen():
    n, e = ring6({3: 'OH'})
    n['n'] = (0, -2.0, 'N'); e.append(('r0', 'n', 1))
    n['nh'] = (-1.0, -2.0, 'H'); e.append(('n', 'nh', 1))
    n['c'] = (0.87, -2.5, 'C'); e.append(('n', 'c', 1))
    n['o'] = (0.87, -3.5, 'O'); e.append(('c', 'o', 2))
    n['me'] = (2.0, -2.0, 'CH₃'); e.append(('c', 'me', 1))
    single_extra(P + 'acetaminophen.svg', n, e, ring_circle())

def ldopa():
    n, e = ring6({2: 'OH', 3: 'OH'})
    n['c1'] = (0, -2.0, 'CH₂'); e.append(('r0', 'c1', 1))
    n['c2'] = (1.5, -2.0, 'CH'); e.append(('c1', 'c2', 1))
    n['nh2'] = (1.5, -3.0, 'NH₂'); e.append(('c2', 'nh2', 1))
    n['c3'] = (2.9, -2.0, 'C'); e.append(('c2', 'c3', 1))
    n['o'] = (2.9, -3.0, 'O'); e.append(('c3', 'o', 2))
    n['oh'] = (4.15, -2.0, 'OH'); e.append(('c3', 'oh', 1))
    single_extra(P + 'ldopa.svg', n, e, ring_circle())

def salicylic_aspirin():
    """حمض السلسليك (1) في اليمين والأسبرين (2) في اليسار، مع دائرة في كل حلقة."""
    n1, e1 = ring6({})
    n1['c1'] = (0, -2.0, 'C'); e1.append(('r0', 'c1', 1))
    n1['o1'] = (-0.87, -2.5, 'O'); e1.append(('c1', 'o1', 2))
    n1['oh'] = (0.95, -2.5, 'OH'); e1.append(('c1', 'oh', 1))
    n1['oh2'] = (1.85, -1.07, 'OH'); e1.append(('r1', 'oh2', 1))
    n2, e2 = ring6({})
    n2['c1'] = (0, -2.0, 'C'); e2.append(('r0', 'c1', 1))
    n2['o1'] = (-0.87, -2.5, 'O'); e2.append(('c1', 'o1', 2))
    n2['oh'] = (0.95, -2.5, 'OH'); e2.append(('c1', 'oh', 1))
    n2['o2'] = (1.73, -1.0, 'O'); e2.append(('r1', 'o2', 1))
    n2['c2'] = (2.6, -0.5, 'C'); e2.append(('o2', 'c2', 1))
    n2['o3'] = (2.6, 0.5, 'O'); e2.append(('c2', 'o3', 2))
    n2['me'] = (3.75, -1.0, 'CH₃'); e2.append(('c2', 'me', 1))
    _, b1 = mol(n1, e1); _, b2 = mol(n2, e2)
    pad, gap = 30, 90
    h = max(b1[3] - b1[1], b2[3] - b2[1])
    x2 = pad; x1 = pad + (b2[2] - b2[0]) + gap
    d2, _ = mol(n2, e2, x2 - b2[0], pad - b2[1]); d1, _ = mol(n1, e1, x1 - b1[0], pad - b1[1])
    body = d1 + d2
    for (ox, oy) in ((x1 - b1[0], pad - b1[1]), (x2 - b2[0], pad - b2[1])):
        body += f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{0.6 * U:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
    W = x1 + (b1[2] - b1[0]) + pad
    body += T(round(x1 + (b1[2] - b1[0]) / 2, 1), round(pad + h + 34, 1), '(1)', 17, weight='bold')
    body += T(round(x2 + (b2[2] - b2[0]) / 2, 1), round(pad + h + 34, 1), '(2)', 17, weight='bold')
    body += L(round(x1 - gap / 2), pad, round(x1 - gap / 2), round(pad + h + 40), MUTED, 1, '4 4')
    save(P + 'salicylic-aspirin.svg', svg(round(W), round(pad + h + 40 + pad), body))

# ---------- O09: الروابط الهيدروجينية ----------
def acid_dimer():
    n = {
        'ma': (-1.45, 0, 'CH₃'), 'ca': (0, 0, 'C'), 'o1a': (0.7, -1.0, 'O'), 'o2a': (0.7, 1.0, 'O'), 'ha': (1.6, 1.0, 'H'),
        'mb': (4.65, 0, 'CH₃'), 'cb': (3.2, 0, 'C'), 'o1b': (2.5, 1.0, 'O'), 'o2b': (2.5, -1.0, 'O'), 'hb': (1.6, -1.0, 'H'),
    }
    e = [('ma', 'ca', 1), ('ca', 'o1a', 2), ('ca', 'o2a', 1), ('o2a', 'ha', 1),
         ('mb', 'cb', 1), ('cb', 'o1b', 2), ('cb', 'o2b', 1), ('o2b', 'hb', 1),
         ('ha', 'o1b', 'h'), ('hb', 'o1a', 'h')]
    single(P + 'acid-dimer.svg', n, e)

def acid_water():
    n = {
        'm': (-1.45, 0, 'CH₃'), 'c': (0, 0, 'C'), 'o1': (0.7, -1.0, 'O'), 'o2': (0.7, 1.0, 'O'), 'h': (1.6, 1.0, 'H'),
        'w1o': (2.85, 1.0, 'O'), 'w1h1': (3.45, 0.25, 'H'), 'w1h2': (3.45, 1.75, 'H'),
        'w2h': (1.75, -1.55, 'H'), 'w2o': (2.75, -1.95, 'O'), 'w2h2': (2.75, -2.95, 'H'),
    }
    e = [('m', 'c', 1), ('c', 'o1', 2), ('c', 'o2', 1), ('o2', 'h', 1),
         ('w1o', 'w1h1', 1), ('w1o', 'w1h2', 1), ('w2o', 'w2h', 1), ('w2o', 'w2h2', 1),
         ('h', 'w1o', 'h'), ('w2h', 'o1', 'h')]
    single(P + 'acid-water.svg', n, e)

def numbered_extra(points):
    """points = [(x, y, '1')] بوحدات U: أرقام حمراء داخل أقواس."""
    def f(ox, oy):
        return ''.join(T(round(ox + x * U, 1), round(oy + y * U + 6, 1), f'({k})', 15, color=RED, weight='bold') for x, y, k in points)
    return f

def propanoic_numbered():
    n, e = row([('H',), ('C', 'H', 'H'), ('C', 'H', 'H'), ('C', '=O'), ('O',), ('H',)], dx=1.15)
    # تحديد مواقع الذرات المرقمة
    xs = {k: v[0] for k, v in n.items()}
    pts = [(xs['m0'], -0.55, '1'), (xs['m1'] + 0.42, -1.0, '2'), (xs['m2'] + 0.42, 1.0, '3'), (xs['m5'], -0.55, '4')]
    single_extra(P + 'propanoic-numbered.svg', n, e, numbered_extra(pts), pad=34)

# ---------- O10: الإسترات ----------
def methyl_propanoate():
    single(P + 'methyl-propanoate.svg', *row([('CH₃',), ('CH₂',), ('C', '=O'), ('O',), ('CH₃',)]))

def ethyl_methanoate():
    single(P + 'ethyl-methanoate.svg', *row([('H',), ('C', '=O'), ('O',), ('CH₂',), ('CH₃',)]))

def ethyl_propanoate_rev():
    single(P + 'ethyl-propanoate-rev.svg', *row([('CH₃',), ('CH₂',), ('O',), ('C', '=O'), ('CH₂',), ('CH₃',)]))

def esters_c6():
    grid(P + 'esters-c6.svg', [
        ('(1)',) + row([('CH₃',), ('C', '=O'), ('O',), ('CH₂CH₂CH₂CH₃',)]),
        ('(2)',) + row([('CH₃CH₂',), ('C', '=O'), ('O',), ('CH₂CH₂CH₃',)]),
        ('(3)',) + row([('CH₃CH₂CH₂',), ('C', '=O'), ('O',), ('CH₂CH₃',)]),
        ('(4)',) + row([('CH₃CH₂CH₂CH₂',), ('C', '=O'), ('O',), ('CH₃',)]),
    ], gapx=50)

def esters_name4():
    grid(P + 'esters-name4.svg', [
        ('(1)',) + row([('CH₃',), ('C', '=O'), ('O',), ('CH₃',)]),
        ('(2)',) + row([('H',), ('C', '=O'), ('O',), ('CH₂CH₂CH₂CH₃',)]),
        ('(3)',) + row([('CH₃CH₂CH₂CH₂',), ('C', '=O'), ('O',), ('CH₂CH₃',)]),
        ('(4)',) + row([('CH₃CH₂',), ('C', '=O'), ('O',), ('CH₂CH₂CH₂CH₃',)]),
    ], gapx=50)

# ---------- O11: الأميدات ----------
def propanamide():
    single(P + 'propanamide.svg', *row([('CH₃',), ('CH₂',), ('C', '=O'), ('NH₂',)]))

def hexanamide():
    single(P + 'hexanamide.svg', *row([('CH₃(CH₂)₄',), ('C', '=O'), ('NH₂',)]))

def ethanamide_full():
    single(P + 'ethanamide-full.svg', *row([('H',), ('C', 'H', 'H'), ('C', '=O'), ('N', None, 'H'), ('H',)], dx=1.15))

def amides_c5():
    grid(P + 'amides-c5.svg', [
        ('(1)',) + row([('CH₃CH₂CH₂CH₂',), ('C', '=O'), ('NH₂',)]),
        ('(2)',) + row([('CH₃CH₂CH₂CH₂CH₂',), ('NH₂',)]),
        ('(3)',) + row([('CH₃CH₂CH₂',), ('C', '=O'), ('NH₂',)]),
        ('(4)',) + row([('CH₃CH₂CH₂CH₂CH₂',), ('C', '=O'), ('NH₂',)]),
    ], gapx=50)

def amides_name4():
    grid(P + 'amides-name4.svg', [
        ('(1)',) + row([('H',), ('C', '=O'), ('NH₂',)], dx=1.2),
        ('(2)',) + row([('CH₃',), ('CH₂',), ('C', '=O'), ('NH₂',)]),
        ('(3)',) + row([('CH₃(CH₂)₅',), ('C', '=O'), ('NH₂',)]),
        ('(4)',) + row([('CH₃(CH₂)₆',), ('C', '=O'), ('NH₂',)]),
    ], gapx=50)

# ---------- O12: التأين ----------
def ionization_scheme():
    n, e = row([('CH₃',), ('C', '=O'), ('O',), ('H',)])
    _, bb = mol(n, e)
    pad = 26
    ox, oy = pad - bb[0], pad - bb[1]
    bd, _ = mol(n, e, ox, oy)
    yb = oy + 0.36 * FS  # خط القاعدة لرموز السلسلة
    x = ox + bb[2] + 30
    def txt(s, size=FS):
        nonlocal bd, x
        w = A.lab_size(s, size)[0] * 2
        bd += T(round(x + w / 2, 1), round(yb, 1), s, size); x += w + 22
    txt('+'); txt('H₂O')
    # سهم الاتزان ⇌
    bd += L(round(x), round(oy - 4), round(x + 56), round(oy - 4), INK, 2) + f'<polygon points="{x + 56},{oy - 4} {x + 47},{oy - 9} {x + 47},{oy - 4}" fill="{INK}"/>'
    bd += L(round(x), round(oy + 4), round(x + 56), round(oy + 4), INK, 2) + f'<polygon points="{x},{oy + 4} {x + 9},{oy + 9} {x + 9},{oy + 4}" fill="{INK}"/>'
    x += 56 + 22
    # مربع علامة الاستفهام
    bd += f'<rect x="{x:.1f}" y="{oy - 22:.1f}" width="56" height="44" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>'
    bd += T(round(x + 28, 1), round(oy + 9, 1), '؟', 26, color=RED, weight='bold'); x += 56 + 22
    txt('+'); txt('H₃O⁺')
    W = x - 22 + pad; H = bb[3] - bb[1] + 2 * pad
    save(P + 'ionization-scheme.svg', svg(round(W), round(H), bd))

# ---------- O13 / O14 ----------
def methyl_hexanoate():
    single(P + 'methyl-hexanoate.svg', *row([('CH₃(CH₂)₄',), ('C', '=O'), ('O',), ('CH₃',)]))

def urea():
    single(P + 'urea.svg', *row([('H₂N',), ('C', '=O'), ('NH₂',)], dx=1.3))

if __name__ == '__main__':
    amide_general(); aspirin(); acetaminophen(); ldopa(); salicylic_aspirin()
    acid_dimer(); acid_water(); propanoic_numbered()
    methyl_propanoate(); ethyl_methanoate(); ethyl_propanoate_rev(); esters_c6(); esters_name4()
    propanamide(); hexanamide(); ethanamide_full(); amides_c5(); amides_name4()
    ionization_scheme(); methyl_hexanoate(); urea()
