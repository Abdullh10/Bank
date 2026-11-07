# رسوم الدرس 4-4 (متشكلات الهيدروكربونات) — النصف الثاني (الأهداف O08–O13):
# كتابة المتشكلات البنائية (C₅H₁₂، C₆H₁₄)، رسم سيس/ترانس (مكثفة وهيكلية)، حرية الدوران حول الرابطة الأحادية،
# ذرة الكربون غير المتماثلة في صيغ مرقمة، نموذج الموقع النشط في الإنزيم، وسلاسل دهون سيس/ترانس.
# التشغيل: python3 data/chem22/gen/figs/C4-L4-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('l4a', os.path.join(os.path.dirname(__file__), 'C4-L4-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
mol, chain, branched, alkene, label, tag, divider, bond, chem = A.mol, A.chain, A.branched, A.alkene, A.label, A.tag, A.divider, A.bond, A.chem
SEP = '#dfe3ea'


def hsep(y, w): return L(20, y, w - 20, y, SEP, 1)


def num_circle(x, y, s, color=BLUE):
    return f'<circle cx="{x}" cy="{y}" r="12" fill="#eaf2fb" stroke="{color}" stroke-width="1.5"/>' + T(x, y + 5, s, 14, color=color, weight='bold')


def rows(name, items, w=600, rh=120, top=0, step=84, x0=60, numbers=True):
    """صيغ مكثفة في صفوف: items = [(groups, branches, double_bond_index_or_None)]"""
    b = ''; y = top
    for k, it in enumerate(items):
        groups, br = it[0], it[1]
        up = any(d == 'up' for _, _, d in br); down = any(d == 'down' for _, _, d in br)
        yy = y + (80 if up else 40)
        a, bo = branched(x0, yy, groups, br, step)
        if len(it) > 2 and it[2] is not None: bo[it[2]] = (it[2], it[2] + 1, 2)
        b += mol(a, bo)
        if numbers: b += tag(w - 35, yy + 6, f'({k + 1})')
        hgt = (80 if up else 40) + (75 if down else 35)
        y += hgt
        if k < len(items) - 1: b += hsep(y, w)
    save(name, svg(w, y + 5, b))


def numbered(name, groups, br, dbl=None, step=88, w=None, nb=True):
    """صيغة مكثفة مع ترقيم ذرات السلسلة الرئيسة (دوائر أسفل كل ذرة)."""
    w = w or int(60 + step * (len(groups) - 1) + 60)
    up = any(d == 'up' for _, _, d in br)
    y = 95 if up else 50
    a, bo = branched(60, y, groups, br, step, 66)
    if dbl is not None: bo[dbl] = (dbl, dbl + 1, 2)
    b = mol(a, bo)
    if nb:
        for k in range(len(groups)): b += num_circle(a[k][0], y + 42, str(k + 1))
    save(name, svg(w, y + 65 if nb else y + 40, b))


def skeletal(pts, dbl=(), color=INK, w=2.6):
    b = ''
    for k in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[k], pts[k + 1]
        if k in dbl:
            # خط ثانٍ داخلي أقصر قليلًا
            b += L(x1, y1, x2, y2, color, w)
            dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); nx, ny = -dy / d * 7, dx / d * 7
            # ضع الخط الثاني في جهة مركز السلسلة المحلية
            cxm = sum(p[0] for p in pts) / len(pts); cym = sum(p[1] for p in pts) / len(pts)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            if (cxm - mx) * nx + (cym - my) * ny < 0: nx, ny = -nx, -ny
            b += L(x1 + nx + dx * 0.12, y1 + ny + dy * 0.12, x2 + nx - dx * 0.12, y2 + ny - dy * 0.12, color, w)
        else:
            b += L(x1, y1, x2, y2, color, w)
    return b


def zigzag(x, y, n, cis_at=(), blen=46, start=-30):
    """نقاط سلسلة متعرجة من n ذرة كربون. cis_at: أرقام الروابط (من 0) التي يكون حولها ترتيب سيس."""
    pts = [(x, y)]; d = start; sign = -1
    for k in range(n - 1):
        if k > 0:
            if (k - 1) in cis_at: pass  # اتجاه الانعطاف نفسه مرة ثانية → سيس حول الرابطة k-1
            else: sign = -sign
            d += sign * 60
        x += blen * math.cos(math.radians(d)); y += blen * math.sin(math.radians(d)); pts.append((x, y))
    return pts


def fit(pts, cx, cy, level=False):
    if level:
        a = math.atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0]); c, sn = math.cos(-a), math.sin(-a)
        pts = [(px * c - py * sn, px * sn + py * c) for px, py in pts]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ox = cx - (min(xs) + max(xs)) / 2; oy = cy - (min(ys) + max(ys)) / 2
    return [(px + ox, py + oy) for px, py in pts]


def hexene_skeletal(name):
    w, h = 640, 380
    # (1) سيس-2-هكسين: الرابطة الثنائية رقم 1 (C2=C3) وترتيب سيس حولها
    # (2) ترانس-2-هكسين، (3) 1-هكسين، (4) ترانس-3-هكسين
    specs = [((1,), (1,)), ((1,), ()), ((0,), ()), ((2,), ())]
    pos = [(160, 95), (480, 95), (160, 280), (480, 280)]
    b = ''
    for k, ((dbl, cis), (x, y)) in enumerate(zip(specs, pos)):
        pts = fit(zigzag(0, 0, 6, cis_at=cis, blen=50), x, y - 8, level=bool(cis))
        b += skeletal(pts, dbl) + tag(x, max(p[1] for p in pts) + 32, f'({k + 1})')
    b += hsep(190, w) + divider(320, 20, h - 15)
    save(name, svg(w, h, b))


def alkene_pair(name, A1, A2, w=780, h=210, gap=None):
    c1, c2 = 205, w - 205
    b = alkene(c1, 95, *A1) + alkene(c2, 95, *A2)
    b += tag(c1, h - 18, '(1)') + tag(c2, h - 18, '(2)') + divider(w / 2, 20, h - 10)
    save(name, svg(w, h, b))


def single_alkene(name, groups, w=520, h=190):
    save(name, svg(w, h, alkene(w / 2, h / 2, *groups)))


def vertical_alkene(name):
    w, h = 420, 250; cx, cy = 210, 125; half = 32; sub = 58
    ax, ay = sub * math.cos(math.radians(30)), sub * math.sin(math.radians(30))
    atoms = [(cx, cy - half, 'C'), (cx, cy + half, 'C'),
             (cx - ax, cy - half - ay, 'CH3', 'r'), (cx + ax, cy - half - ay, 'H', 'l'),
             (cx - ax, cy + half + ay, 'CH2CH3', 'r'), (cx + ax, cy + half + ay, 'H', 'l')]
    save(name, svg(w, h, mol(atoms, [(0, 1, 2), (0, 2, 1), (0, 3, 1), (1, 4, 1), (1, 5, 1)])))


def three_alk(name, items, w=760, h=430):
    p = [(205, 95), (w - 205, 95), (w / 2, 305)]
    b = ''
    for k, ((x, y), it) in enumerate(zip(p, items)):
        b += alkene(x, y, *it) + tag(x, y + 92, f'({k + 1})')
    b += hsep(210, w) + divider(w / 2, 20, 200)
    save(name, svg(w, h, b))


def butane_rot(name, w=640, h=230):
    """البيوتان حول الرابطة الأحادية C2–C3: (1) مجموعتا CH₃ في الأعلى، (2) إحداهما في الأعلى والأخرى في الأسفل."""
    def one(cx, cy, right_up, right_down):
        xa, xb = cx - 34, cx + 34; s = 58
        ax, ay = s * math.cos(math.radians(60)), s * math.sin(math.radians(60))
        atoms = [(xa, cy, 'C'), (xb, cy, 'C'), (xa - ax, cy - ay, 'CH3', 'r'), (xa - ax, cy + ay, 'H', 'r'), (xa - s, cy, 'H', 'r'),
                 (xb + ax, cy - ay, right_up, 'l'), (xb + ax, cy + ay, right_down, 'l'), (xb + s, cy, 'H', 'l')]
        return mol(atoms, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 5, 1), (1, 6, 1), (1, 7, 1)])
    b = one(165, 100, 'CH3', 'H') + one(w - 165, 100, 'H', 'CH3')
    b += tag(165, h - 15, '(1)') + tag(w - 165, h - 15, '(2)') + divider(w / 2, 20, h - 10)
    save(name, svg(w, h, b))


def ethane_ethene(name, w=640, h=240):
    b = ''
    # (1) الإيثان: صيغة بنائية كاملة
    cx, cy = 165, 105; xa, xb = cx - 34, cx + 34; s = 52
    ax, ay = s * math.cos(math.radians(60)), s * math.sin(math.radians(60))
    atoms = [(xa, cy, 'C'), (xb, cy, 'C'), (xa - ax, cy - ay, 'H'), (xa - ax, cy + ay, 'H'), (xa - s, cy, 'H'),
             (xb + ax, cy - ay, 'H'), (xb + ax, cy + ay, 'H'), (xb + s, cy, 'H')]
    b += mol(atoms, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 5, 1), (1, 6, 1), (1, 7, 1)])
    # (2) الإيثين
    b += alkene(w - 165, 105, 'H', 'H', 'H', 'H', sub=52)
    # سهم دوران منحنٍ حول ذرة الكربون اليمنى في كل جزيء (محاولة تدوير)
    for x in (xb, w - 165 + 32):
        b += (f'<path d="M {x + 62} {cy - 52} A 30 62 0 0 1 {x + 62} {cy + 52}" fill="none" stroke="{ORANGE}" stroke-width="2.2"/>'
              f'<polygon points="{x + 62},{cy + 52} {x + 72},{cy + 42} {x + 60},{cy + 40}" fill="{ORANGE}"/>')
    b += tag(165, h - 18, '(1)') + tag(w - 165, h - 18, '(2)') + divider(w / 2, 20, h - 10)
    save(name, svg(w, h, b))


ORANGE = '#d9822b'


def hexene_bonds(name, w=600, h=150):
    a, bo = chain(60, 60, ['CH3', 'CH', 'CH', 'CH2', 'CH2', 'CH3'], 96)
    bo[1] = (1, 2, 2)
    b = mol(a, bo)
    for k in range(5):
        b += num_circle((a[k][0] + a[k + 1][0]) / 2, 100, str(k + 1), RED)
    save(name, svg(w, h, b))


def enzyme(name, w=660, h=330):
    """نموذج مبسط: موقع نشط فيه ثلاث فجوات (دائرة، مربع، مثلث) وجزيئان كل منهما صورة مرآة للآخر."""
    GR = '#c9d3df'; G1 = '#2a6fb0'; G2 = '#1f7a4d'; G3 = '#b03a2e'

    def site(cx, y):
        # كتلة الإنزيم مع ثلاث فجوات في حافتها العليا: يسار دائرة، وسط مربع، يمين مثلث
        p = (f'M {cx - 130} {y} L {cx - 88} {y} A 22 22 0 0 0 {cx - 44} {y} L {cx - 22} {y} L {cx - 22} {y + 40} L {cx + 22} {y + 40} '
             f'L {cx + 22} {y} L {cx + 44} {y} L {cx + 66} {y + 38} L {cx + 88} {y} L {cx + 130} {y} L {cx + 130} {y + 95} L {cx - 130} {y + 95} Z')
        return f'<path d="{p}" fill="{GR}" stroke="{INK}" stroke-width="2"/>' + T(cx, y + 78, 'الموقع النشط في الإنزيم', 14, weight='bold')

    def molecule(cx, y, order):
        # ذرة مركزية ومجموعتان جانبيتان ومجموعة وسطى إلى الأسفل، ومجموعة رابعة إلى الأعلى
        b = L(cx, y, cx, y - 34, INK, 2.2) + f'<circle cx="{cx}" cy="{y - 40}" r="8" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        shapes = {'c': lambda x, yy, c: f'<circle cx="{x}" cy="{yy}" r="18" fill="{c}"/>',
                  's': lambda x, yy, c: f'<rect x="{x - 18}" y="{yy - 18}" width="36" height="36" fill="{c}"/>',
                  't': lambda x, yy, c: f'<polygon points="{x - 20},{yy - 14} {x + 20},{yy - 14} {x},{yy + 22}" fill="{c}"/>'}
        cols = {'c': G1, 's': G2, 't': G3}
        xs = [cx - 66, cx, cx + 66]; ys = [y + 14, y + 26, y + 14]
        for x, yy, sh in zip(xs, ys, order):
            b += L(cx, y, x, yy, INK, 2.2)
        for x, yy, sh in zip(xs, ys, order):
            b += shapes[sh](x, yy, cols[sh])
        b += f'<circle cx="{cx}" cy="{y}" r="10" fill="{INK}"/>'
        return b

    b = molecule(170, 105, 'cst') + site(170, 175) + tag(170, 40, '(1)')
    b += molecule(w - 170, 105, 'tsc') + site(w - 170, 175) + tag(w - 170, 40, '(2)')
    b += divider(w / 2, 20, h - 20)
    save(name, svg(w, h, b))


def fatty(name, w=700, h=330):
    """سلسلتان كربونيتان بـ 14 ذرة كربون، في كل منهما رابطة ثنائية واحدة في الوسط وفي طرفها COOH."""
    b = ''
    for k, (cis, y) in enumerate([((6,), 95), ((), 250)]):
        pts = zigzag(0, 0, 14, cis_at=cis, blen=40)
        pts = fit(pts, 330, y, level=bool(cis))
        b += skeletal(pts, (6,))
        x, yy = pts[-1]
        b += label(x + 26, yy, 'COOH', 16, 'l') + L(x, yy, x + 22, yy, INK, 2.6)
        b += tag(40, y + 6, f'({k + 1})')
    b += hsep(170, w)
    save(name, svg(w, h, b))


if __name__ == '__main__':
    P = 'c4-l4b-'
    # O08
    rows(P + 'c6h14-same.svg', [
        (['CH3', 'CH', 'CH2', 'CH2', 'CH3'], [(1, 'CH3', 'up')]),
        (['CH3', 'CH2', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'up')]),
        (['CH3', 'CH2', 'CH2', 'CH', 'CH3'], [(3, 'CH3', 'down')]),
        (['CH3', 'C', 'CH2', 'CH3'], [(1, 'CH3', 'up'), (1, 'CH3', 'down')])])
    rows(P + 'c6h14-missing.svg', [
        (['CH3', 'CH2', 'CH2', 'CH2', 'CH2', 'CH3'], []),
        (['CH3', 'CH', 'CH2', 'CH2', 'CH3'], [(1, 'CH3', 'up')]),
        (['CH3', 'CH2', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'up')]),
        (['CH3', 'C', 'CH2', 'CH3'], [(1, 'CH3', 'up'), (1, 'CH3', 'down')])])
    rows(P + 'c5h12-drawings.svg', [
        (['CH3', 'CH2', 'CH2', 'CH2', 'CH3'], []),
        (['CH3', 'CH2', 'CH2', 'CH2'], [(3, 'CH3', 'down')]),
        (['CH3', 'CH', 'CH2', 'CH3'], [(1, 'CH3', 'up')]),
        (['CH3', 'CH2', 'CH', 'CH3'], [(2, 'CH3', 'down')])], w=540)
    rows(P + 'skeletons.svg', [
        (['C', 'C', 'C', 'C', 'C'], [(1, 'C', 'up')]),
        (['C', 'C', 'C', 'C'], [(1, 'C', 'up'), (2, 'C', 'up')]),
        (['C', 'C', 'C', 'C', 'C', 'C'], [(2, 'C', 'up')]),
        (['C', 'C', 'C', 'C'], [(1, 'C', 'up'), (1, 'C', 'down')])], step=70, w=520)
    rows(P + 'student-list.svg', [
        (['CH3', 'CH2', 'CH2', 'CH2', 'CH2', 'CH3'], []),
        (['CH3', 'CH2', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'up')]),
        (['CH3', 'CH', 'CH', 'CH3'], [(1, 'CH3', 'up'), (2, 'CH3', 'up')]),
        (['CH3', 'CH2', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'down')]),
        (['CH3', 'C', 'CH2', 'CH2', 'CH3'], [(1, 'CH3', 'up'), (1, 'CH3', 'down')])])
    # O09
    alkene_pair(P + '4-octene.svg', ('CH3CH2CH2', 'H', 'CH2CH2CH3', 'H'), ('CH3CH2CH2', 'H', 'H', 'CH2CH2CH3'))
    hexene_skeletal(P + 'hexene-skeletal.svg')
    single_alkene(P + 'complete-trans.svg', ('CH3', 'H', 'X', 'Y'))
    vertical_alkene(P + 'vertical.svg')
    three_alk(P + 'q71.svg', [('CH3', 'CH3', 'CH3', 'CH2CH2CH3'), ('CH3', 'CH3CH2', 'CH2CH3', 'CH3'), ('CH3', 'CH3CH2', 'CH3', 'CH2CH3')])
    single_alkene(P + 'trans-2-hexene.svg', ('CH3', 'H', 'H', 'CH2CH2CH3'))
    # O10
    butane_rot(P + 'butane-rot.svg')
    ethane_ethene(P + 'ethane-ethene.svg')
    hexene_bonds(P + 'hexene-bonds.svg')
    # O11
    numbered(P + 'dmp-numbered.svg', ['CH3', 'CH', 'CH', 'CH2', 'CH3'], [(1, 'CH3', 'up'), (2, 'CH3', 'up')])
    numbered(P + 'methylpentene.svg', ['CH2', 'CH', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'up')], dbl=0)
    numbered(P + 'dmh.svg', ['CH3', 'CH2', 'CH', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'up'), (3, 'CH3', 'up')], nb=False)
    numbered(P + 'decane.svg', ['CH3', 'CH2', 'CH', 'CH2', 'CH', 'CH2', 'CH', 'CH2', 'CH2', 'CH3'],
             [(2, 'CH3', 'up'), (4, 'CH2CH3', 'up'), (6, 'CH3', 'up')], step=74, nb=False)
    numbered(P + '23dmh.svg', ['CH3', 'CH', 'CH', 'CH2', 'CH2', 'CH3'], [(1, 'CH3', 'up'), (2, 'CH3', 'up')], nb=False)
    rows(P + 'c6h14-five.svg', [
        (['CH3', 'CH2', 'CH2', 'CH2', 'CH2', 'CH3'], []),
        (['CH3', 'CH', 'CH2', 'CH2', 'CH3'], [(1, 'CH3', 'up')]),
        (['CH3', 'CH2', 'CH', 'CH2', 'CH3'], [(2, 'CH3', 'up')]),
        (['CH3', 'C', 'CH2', 'CH3'], [(1, 'CH3', 'up'), (1, 'CH3', 'down')]),
        (['CH3', 'CH', 'CH', 'CH3'], [(1, 'CH3', 'up'), (2, 'CH3', 'up')])])
    numbered(P + 'ethylmethylhexane.svg', ['CH3', 'CH', 'CH2', 'CH', 'CH2', 'CH3'], [(1, 'CH3', 'up'), (3, 'CH2CH3', 'up')], nb=False)
    # O12
    enzyme(P + 'enzyme.svg')
    # O13
    fatty(P + 'fatty.svg')
