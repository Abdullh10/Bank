# رسوم الدرس 5-2 (الكحولات والإيثرات والأمينات) — النصف الأول: صيغ بنائية للكحولات والإيثرات والأمينات،
# وتصنيف الأمينات، والروابط الهيدروجينية بين الجزيئات ومع الماء.
# التشغيل: python3 data/chem22/gen/figs/C5-L2-a.py
import sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

P = 'c5-l2a-'
HB = '#2a6fb0'   # لون خط الرابطة الهيدروجينية


def _w(s, size):
    w = 0
    for ch in s:
        if ch.isdigit(): w += size * 0.42
        elif ch in 'Hm': w += size * 0.72
        elif ch in 'CNO': w += size * 0.70
        else: w += size * 0.6
    return w


def chem(x, y, s, size=17, color=INK, anchor='middle', weight='normal'):
    out, low = '', False
    for part in re.findall(r'\d+|[^\d]+', s):
        if part.isdigit():
            out += f'<tspan font-size="{size * 0.7:.1f}" dy="{"0" if low else "5"}">{part}</tspan>'; low = True
        else:
            out += f'<tspan dy="{"-5" if low else "0"}">{esc(part)}</tspan>'; low = False
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'{FONT} direction="ltr">{out}</text>')


def label(x, y, s, size=17, align='c', color=INK):
    """align: c وسط، l النص يمتد يمينًا من الذرة الأولى، r يمتد يسارًا وتبقى الذرة الأخيرة على الموقع."""
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
    return L(x1 + nx, y1 + ny, x2 + nx, y2 + ny, color, w) + L(x1 - nx, y1 - ny, x2 - nx, y2 - ny, color, w)


def grid(ox, oy, atoms, bonds, step=52, size=17):
    """atoms = {key: (col, row, label, align)} في شبكة؛ bonds = [(k1, k2)]. تُرسم الروابط أولًا ثم الذرات فوقها."""
    pos = {k: (ox + c * step, oy + r * step) for k, (c, r, *_) in atoms.items()}
    b = ''.join(bond(*pos[a], *pos[c]) for a, c in bonds)
    for k, (c, r, lab, *al) in atoms.items():
        b += label(*pos[k], lab, size, al[0] if al else 'c')
    return b


def tag(x, y, s, size=16, color=INK):
    return T(x, y, s, size, color=color, weight='bold')


def sep_h(y, x1, x2): return L(x1, y, x2, y, '#dfe3ea', 1)
def sep_v(x, y1, y2): return L(x, y1, x, y2, MUTED, 1.2, '6 5')


def hchain(n, ox, oy, step=52, extra=None):
    """سلسلة كربون أفقية بصيغة بنائية كاملة (H فوق وتحت كل C)؛ extra = {(col,row): label} يستبدل H في موقع."""
    atoms, bonds = {}, []
    extra = extra or {}
    for i in range(n):
        c = 1 + i
        atoms[f'C{i}'] = (c, 0, 'C')
        for r in (-1, 1):
            atoms[f'H{i}{r}'] = (c, r, extra.get((c, r), 'H')); bonds.append((f'C{i}', f'H{i}{r}'))
        if i: bonds.append((f'C{i-1}', f'C{i}'))
    atoms['HL'] = (0, 0, extra.get((0, 0), 'H')); bonds.append(('HL', 'C0'))
    return atoms, bonds


# ---------------------------------------------------------------- الرسوم
def ethanol_full(name):
    """الإيثانول بصيغة بنائية كاملة: H–C–C–O–H."""
    atoms, bonds = hchain(2, 0, 0)
    atoms['O'] = (3, 0, 'O'); atoms['HO'] = (4, 0, 'H'); bonds += [('C1', 'O'), ('O', 'HO')]
    save(name, svg(320, 160, grid(55, 80, atoms, bonds)))


def three_classes(name):
    """(1) CH3–O–CH2–CH3، (2) CH3–CH2–CH2–NH2، (3) CH3–CH(OH)–CH3 بصيغ مكثفة."""
    b = ''
    b += grid(70, 60, {'a': (0, 0, 'CH3'), 'o': (1.4, 0, 'O'), 'b': (2.8, 0, 'CH2'), 'c': (4.2, 0, 'CH3')},
              [('a', 'o'), ('o', 'b'), ('b', 'c')], step=58) + tag(470, 66, '(1)')
    b += sep_h(105, 20, 520)
    b += grid(70, 150, {'a': (0, 0, 'CH3'), 'b': (1.4, 0, 'CH2'), 'c': (2.8, 0, 'CH2'), 'n': (4.2, 0, 'NH2', 'l')},
              [('a', 'b'), ('b', 'c'), ('c', 'n')], step=58) + tag(470, 156, '(2)')
    b += sep_h(195, 20, 520)
    b += grid(110, 240, {'a': (0, 0, 'CH3'), 'b': (1.4, 0, 'CH'), 'c': (2.8, 0, 'CH3'), 'o': (1.4, 1.1, 'OH')},
              [('a', 'b'), ('b', 'c'), ('b', 'o')], step=58) + tag(470, 246, '(3)')
    save(name, svg(540, 320, b))


def c3_candidates(name):
    """أربع صيغ مكثفة مرقمة: 1-بروبانول، 2-بروبانول، إيثيل ميثيل إيثر، بروبيل أمين (بلا أسماء)."""
    b = ''
    S = 56
    b += grid(50, 60, {'a': (0, 0, 'CH3'), 'b': (1.4, 0, 'CH2'), 'c': (2.8, 0, 'CH2'), 'o': (4.1, 0, 'OH', 'l')},
              [('a', 'b'), ('b', 'c'), ('c', 'o')], step=S) + tag(160, 125, '(1)')
    b += grid(390, 50, {'a': (0, 0, 'CH3'), 'b': (1.4, 0, 'CH'), 'c': (2.8, 0, 'CH3'), 'o': (1.4, 1.0, 'OH')},
              [('a', 'b'), ('b', 'c'), ('b', 'o')], step=S) + tag(468, 140, '(2)')
    b += sep_h(160, 20, 640) + sep_v(330, 20, 330)
    b += grid(40, 220, {'a': (0, 0, 'CH3'), 'o': (1.3, 0, 'O'), 'b': (2.6, 0, 'CH2'), 'c': (3.9, 0, 'CH3')},
              [('a', 'o'), ('o', 'b'), ('b', 'c')], step=S) + tag(160, 290, '(3)')
    b += grid(370, 220, {'a': (0, 0, 'CH3'), 'b': (1.4, 0, 'CH2'), 'c': (2.8, 0, 'CH2'), 'n': (4.1, 0, 'NH2', 'l')},
              [('a', 'b'), ('b', 'c'), ('c', 'n')], step=S) + tag(490, 290, '(4)')
    save(name, svg(660, 320, b))


def diamine_candidates(name):
    """أربع صيغ: (1) H2N–CH2–CH2–CH2–NH2، (2) CH3–CH(NH2)–CH2–NH2، (3) CH3–CH2–CH(NH2)–NH2، (4) H2N–CH2–CH2–NH2."""
    b = ''; S = 56
    b += grid(45, 60, {'n1': (0, 0, 'H2N', 'r'), 'a': (1.3, 0, 'CH2'), 'b': (2.6, 0, 'CH2'), 'c': (3.9, 0, 'CH2'), 'n2': (5.2, 0, 'NH2', 'l')},
              [('n1', 'a'), ('a', 'b'), ('b', 'c'), ('c', 'n2')], step=S) + tag(225, 135, '(1)')
    b += grid(420, 50, {'a': (0, 0, 'CH3'), 'b': (1.3, 0, 'CH'), 'c': (2.6, 0, 'CH2'), 'n2': (3.9, 0, 'NH2', 'l'), 'n1': (1.3, 1.0, 'NH2')},
              [('a', 'b'), ('b', 'c'), ('c', 'n2'), ('b', 'n1')], step=S) + tag(530, 140, '(2)')
    b += sep_h(160, 20, 700) + sep_v(385, 20, 330)
    b += grid(45, 215, {'a': (0, 0, 'CH3'), 'b': (1.3, 0, 'CH2'), 'c': (2.6, 0, 'CH'), 'n2': (3.9, 0, 'NH2', 'l'), 'n1': (2.6, 1.0, 'NH2')},
              [('a', 'b'), ('b', 'c'), ('c', 'n2'), ('c', 'n1')], step=S) + tag(225, 305, '(3)')
    b += grid(440, 225, {'n1': (0, 0, 'H2N', 'r'), 'a': (1.3, 0, 'CH2'), 'b': (2.6, 0, 'CH2'), 'n2': (3.9, 0, 'NH2', 'l')},
              [('n1', 'a'), ('a', 'b'), ('b', 'n2')], step=S) + tag(555, 305, '(4)')
    save(name, svg(720, 330, b))


def hexagon(cx, cy, r=44, circle=False, rot=90):
    pts = [(cx + r * math.cos(math.radians(rot + 60 * k)), cy - r * math.sin(math.radians(rot + 60 * k))) for k in range(6)]
    s = f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    if circle: s += f'<circle cx="{cx}" cy="{cy}" r="{r * 0.58:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
    return s, pts


def ring_sub(cx, cy, lab, circle=False, r=44, blen=40):
    """حلقة سداسية (رأس علوي) ومجموعة مرتبطة بالرأس العلوي."""
    s, pts = hexagon(cx, cy, r, circle)
    tx, ty = pts[0]
    return s + L(tx, ty, tx, ty - blen, INK, 2.4) + label(tx, ty - blen - 10, lab, 17)


def rings(name):
    """(1) هكسانول حلقي، (2) أنيلين، (3) هكسيل حلقي أمين، (4) هكسيل حلقي إيثر — صيغ هيكلية بلا أسماء."""
    b = ''
    b += ring_sub(110, 130, 'OH') + tag(110, 210, '(1)')
    b += ring_sub(270, 130, 'NH2', circle=True) + tag(270, 210, '(2)')
    b += ring_sub(430, 130, 'NH2') + tag(430, 210, '(3)')
    b += sep_v(190, 20, 220) + sep_v(350, 20, 220) + sep_v(510, 20, 220)
    # (4) حلقتان يصل بينهما O
    s1, p1 = hexagon(580, 130, 40, rot=0); s2, p2 = hexagon(780, 130, 40, rot=0)
    b += s1 + s2 + L(p1[0][0], p1[0][1], 680, 130, INK, 2.4) + L(680, 130, p2[3][0], p2[3][1], INK, 2.4) + label(680, 130, 'O')
    b += tag(680, 210, '(4)')
    save(name, svg(850, 230, b))


def glycerol(name):
    """1، 2، 3-بروبان ترايول (الجليسرول) بصيغة بنائية كاملة كما يرسمها الكتاب (OH أسفل كل ذرة كربون)."""
    atoms, bonds = hchain(3, 0, 0, extra={(1, 1): 'OH', (2, 1): 'OH', (3, 1): 'OH'})
    atoms['HR'] = (4, 0, 'H'); bonds.append(('C2', 'HR'))
    save(name, svg(330, 175, grid(55, 75, atoms, bonds)))


def amine_classes(name):
    """أربعة أمينات: (1) CH3–CH2–NH2، (2) CH3–NH–CH3، (3) N(CH3)3، (4) (CH3)3C–NH2."""
    b = ''; S = 56
    b += grid(70, 80, {'a': (0, 0, 'CH3'), 'b': (1.4, 0, 'CH2'), 'n': (2.8, 0, 'NH2', 'l')}, [('a', 'b'), ('b', 'n')], step=S) + tag(150, 150, '(1)')
    b += grid(410, 80, {'a': (0, 0, 'CH3'), 'n': (1.3, 0, 'N'), 'c': (2.6, 0, 'CH3'), 'h': (1.3, -1.0, 'H')},
              [('a', 'n'), ('n', 'c'), ('n', 'h')], step=S) + tag(483, 150, '(2)')
    b += sep_h(175, 20, 660) + sep_v(340, 20, 380)
    b += grid(80, 270, {'a': (0, 0, 'CH3'), 'n': (1.3, 0, 'N'), 'c': (2.6, 0, 'CH3'), 'd': (1.3, 1.0, 'CH3')},
              [('a', 'n'), ('n', 'c'), ('n', 'd')], step=S) + tag(153, 370, '(3)')
    b += grid(400, 270, {'a': (0, 0, 'CH3'), 'c': (1.3, 0, 'C'), 'b': (2.6, 0, 'CH3'), 'u': (1.3, -1.0, 'CH3'), 'n': (1.3, 1.0, 'NH2')},
              [('a', 'c'), ('c', 'b'), ('c', 'u'), ('c', 'n')], step=S) + tag(473, 370, '(4)')
    save(name, svg(680, 385, b))


def aniline_set(name):
    """حلقة بنزين ترتبط بـ (1) NH2، (2) NH–CH3، (3) N(CH3)2."""
    b = ''
    def ph(cx, cy, tail):
        s, pts = hexagon(cx, cy, 42, circle=True)
        tx, ty = pts[0]
        return s + L(tx, ty, tx, ty - 38, INK, 2.4) + tail(tx, ty - 50)
    b += ph(110, 175, lambda x, y: label(x, y, 'NH2')) + tag(110, 250, '(1)')
    b += ph(330, 175, lambda x, y: grid(x, y, {'n': (0, 0, 'N'), 'h': (-1, 0, 'H'), 'c': (1.1, 0, 'CH3')}, [('n', 'h'), ('n', 'c')], step=44)) + tag(330, 250, '(2)')
    b += ph(560, 175, lambda x, y: grid(x, y, {'n': (0, 0, 'N'), 'h': (-1.15, 0, 'CH3'), 'c': (1.15, 0, 'CH3')}, [('n', 'h'), ('n', 'c')], step=44)) + tag(560, 250, '(3)')
    b += sep_v(215, 20, 260) + sep_v(445, 20, 260)
    save(name, svg(670, 270, b))


def hbond_alcohol(name):
    """جزيئان من الإيثانول بينهما خط متقطع من H في مجموعة OH لأحدهما إلى O في الآخر."""
    b = grid(60, 70, {'a': (0, 0, 'CH3'), 'b': (1.3, 0, 'CH2'), 'o': (2.6, 0, 'O'), 'h': (3.6, 0, 'H')},
             [('a', 'b'), ('b', 'o'), ('o', 'h')], step=56)
    # الجزيء الثاني: O أسفل يمين H الأول
    ox, oy = 60 + 4.9 * 56, 150
    b += L(60 + 3.6 * 56 + 8, 80, ox - 8, oy - 12, HB, 2.4, '5 5')
    b += grid(ox, oy, {'o': (0, 0, 'O'), 'h': (0, 1.0, 'H'), 'b': (1.3, 0, 'CH2'), 'a': (2.6, 0, 'CH3')},
              [('o', 'h'), ('o', 'b'), ('b', 'a')], step=56)
    save(name, svg(560, 230, b))


def ether_water(name):
    """جزيء ثنائي ميثيل إيثر وجزيء ماء، وخط متقطع من H في الماء إلى O في الإيثر."""
    b = grid(70, 70, {'a': (0, 0, 'CH3'), 'o': (1.3, 0, 'O'), 'c': (2.6, 0, 'CH3')}, [('a', 'o'), ('o', 'c')], step=56)
    ox = 70 + 1.3 * 56
    b += L(ox, 84, ox, 132, HB, 2.4, '5 5')
    b += grid(ox, 150, {'h': (0, 0, 'H'), 'o': (0, 1.0, 'O'), 'h2': (1.0, 1.0, 'H')}, [('h', 'o'), ('o', 'h2')], step=56)
    save(name, svg(330, 240, b))


def c2h6o_pair(name):
    """(1) الإيثانول و(2) ثنائي ميثيل إيثر بصيغة بنائية كاملة (C2H6O لكليهما)."""
    atoms, bonds = hchain(2, 0, 0)
    atoms['O'] = (3, 0, 'O'); atoms['HO'] = (4, 0, 'H'); bonds += [('C1', 'O'), ('O', 'HO')]
    b = grid(40, 80, atoms, bonds, step=50) + tag(140, 175, '(1)')
    at2 = {'H0': (0, 0, 'H'), 'C0': (1, 0, 'C'), 'a': (1, -1, 'H'), 'b': (1, 1, 'H'), 'O': (2, 0, 'O'),
           'C1': (3, 0, 'C'), 'c': (3, -1, 'H'), 'd': (3, 1, 'H'), 'H1': (4, 0, 'H')}
    b += grid(330, 80, at2, [('H0', 'C0'), ('C0', 'a'), ('C0', 'b'), ('C0', 'O'), ('O', 'C1'), ('C1', 'c'), ('C1', 'd'), ('C1', 'H1')], step=50) + tag(430, 175, '(2)')
    b += sep_v(290, 20, 185)
    save(name, svg(570, 195, b))


if __name__ == '__main__':
    ethanol_full(P + 'ethanol.svg')
    three_classes(P + 'three-classes.svg')
    c3_candidates(P + 'c3-candidates.svg')
    diamine_candidates(P + 'diamines.svg')
    rings(P + 'rings.svg')
    glycerol(P + 'glycerol.svg')
    amine_classes(P + 'amine-classes.svg')
    aniline_set(P + 'aniline-set.svg')
    hbond_alcohol(P + 'hbond-ethanol.svg')
    ether_water(P + 'ether-water.svg')
    c2h6o_pair(P + 'c2h6o-pair.svg')
