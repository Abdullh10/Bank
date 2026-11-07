# رسوم الدرس 4-3 (الألكينات والألكاينات) — النصف الثاني: صيغ الألكاينات من أسمائها، وخواصها، ومقارنة النشاط،
# والصيغ العامة، وتسمية الدايينات والترايينات، والإيثين.
# التشغيل: python3 data/chem22/gen/figs/C4-L3-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

# مساعدات الرسم من ملف النصف الأول (استيراد بالمسار دون تعديله)
_spec = importlib.util.spec_from_file_location('c4l3a', os.path.join(os.path.dirname(__file__), 'C4-L3-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
cond, line_chain, tag, bond = A.cond, A.line_chain, A.tag, A.bond


def nums(ox, oy, n, sx=A.SX, start=1, step=1):
    """أرقام صغيرة فوق مجموعات سلسلة أفقية."""
    return ''.join(T(ox + i * sx, oy, str(start + i * step), 13, color=RED) for i in range(n))


def full(ox, oy, carbons, orders, ups, downs, sx=56, sy=50):
    """صيغة بنائية كاملة أفقية: carbons عدد ذرات الكربون، orders رتب الروابط C–C، ups/downs عدد ذرات H فوق/تحت كل كربون،
    وتُضاف H طرفية أفقية لذرتي الطرفين."""
    at = {f'c{i}': (i + 1, 0, 'C', 'c') for i in range(carbons)}
    bd = [(f'c{i}', f'c{i + 1}', o) for i, o in enumerate(orders)]
    at['hl'] = (0, 0, 'H', 'c'); bd.append(('hl', 'c0', 1))
    at['hr'] = (carbons + 1, 0, 'H', 'c'); bd.append((f'c{carbons - 1}', 'hr', 1))
    for i in range(carbons):
        if ups[i]: at[f'u{i}'] = (i + 1, -1, 'H', 'c'); bd.append((f'c{i}', f'u{i}', 1))
        if downs[i]: at[f'd{i}'] = (i + 1, 1, 'H', 'c'); bd.append((f'c{i}', f'd{i}', 1))
    return cond(ox, oy, at, bd, sx=sx, sy=sy)


def ball(x, y, r, kind):
    g = 'gC' if kind == 'C' else 'gH'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="url(#{g})" stroke="#444" stroke-width="1.2"/>'


GRAD = ('<defs><radialGradient id="gC" cx="35%" cy="35%" r="65%"><stop offset="0" stop-color="#9aa0a8"/><stop offset="1" stop-color="#2f3338"/></radialGradient>'
        '<radialGradient id="gH" cx="35%" cy="35%" r="65%"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#b9bec6"/></radialGradient></defs>')


def sticks(x1, y1, x2, y2, order):
    return bond(x1, y1, x2, y2, order, w=4, gap=6).replace(INK, '#777')


def main():
    # O07 س3: أربع صيغ بنائية كاملة رباعية الكربون (الصحيحة لـ 2-بيوتاين رقم 3)
    b = full(30, 85, 4, [3, 1, 1], [0, 0, 1, 1], [0, 0, 1, 1])          # 1-بيوتاين
    b += full(390, 85, 4, [1, 2, 1], [1, 1, 1, 1], [1, 0, 0, 1])        # 2-بيوتين
    b += full(30, 255, 4, [1, 3, 1], [1, 0, 0, 1], [1, 0, 0, 1])        # 2-بيوتاين ✓
    b += full(390, 255, 4, [1, 3, 1], [1, 1, 1, 1], [1, 0, 0, 1])       # بنية غير ممكنة (خمس روابط)
    b += tag(170, 22, '(1)') + tag(530, 22, '(2)') + tag(170, 192, '(3)') + tag(530, 192, '(4)')
    b += L(365, 10, 365, 330, MUTED, 1, '4 4') + L(15, 172, 715, 172, MUTED, 1, '4 4')
    save('c4-l3b-o7-c4-full.svg', svg(730, 335, b))

    # O07 س5: رسم طالب لـ 4-ميثيل-2-هكساين وفيه ذرة كربون خماسية الروابط
    at, bd = line_chain(['CH3', 'C', 'CH', 'CH', 'CH2', 'CH3'], [1, 3, 1, 1, 1]); at['m'] = (3, 1, 'CH3'); bd.append((3, 'm', 1))
    save('c4-l3b-o7-student.svg', svg(490, 130, nums(30, 22, 6, 82) + cond(30, 50, at, bd, sx=82)))

    # O08 س1: الإيثاين: صيغة بنائية ونموذج الكرة والعصا
    b = cond(30, 60, *line_chain(['H', 'C', 'C', 'H'], [1, 3, 1]), sx=70) + GRAD
    xs = [300, 370, 450, 520]
    b += sticks(xs[0], 60, xs[1], 60, 1) + sticks(xs[1], 60, xs[2], 60, 3) + sticks(xs[2], 60, xs[3], 60, 1)
    b += ball(xs[0], 60, 13, 'H') + ball(xs[1], 60, 22, 'C') + ball(xs[2], 60, 22, 'C') + ball(xs[3], 60, 13, 'H')
    b += L(265, 15, 265, 105, MUTED, 1, '4 4')
    save('c4-l3b-ethyne-models.svg', svg(560, 115, b))

    # O09 س2: الإيثان والإيثين والإيثاين (صيغ بنائية كاملة)
    b = full(20, 95, 2, [1], [1, 1], [1, 1], sx=52)
    b += full(250, 95, 2, [2], [1, 1], [0, 0], sx=52)
    b += cond(470, 95, *line_chain(['H', 'C', 'C', 'H'], [1, 3, 1]), sx=52)
    b += tag(98, 25, '(أ)') + tag(328, 25, '(ب)') + tag(548, 25, '(ج)')
    b += L(225, 15, 225, 160, MUTED, 1, '4 4') + L(450, 15, 450, 160, MUTED, 1, '4 4')
    save('c4-l3b-c2-three.svg', svg(660, 165, b))

    # O09 مقالي 1: البروبان والبروبين والبروباين (صيغ مكثفة)
    b = cond(40, 55, *line_chain(['CH3', 'CH2', 'CH3'], [1, 1]), sx=78)
    b += cond(40, 135, *line_chain(['CH2', 'CH', 'CH3'], [2, 1]), sx=78)
    b += cond(40, 215, *line_chain(['CH', 'C', 'CH3'], [3, 1]), sx=78)
    b += T(330, 60, '(أ)', 17, weight='bold', color=BLUE) + T(330, 140, '(ب)', 17, weight='bold', color=BLUE) + T(330, 220, '(ج)', 17, weight='bold', color=BLUE)
    save('c4-l3b-c3-three.svg', svg(370, 245, b))

    # O10 س4: 3-ميثيل-1-هكساين CH≡CCH(CH3)CH2CH2CH3
    at, bd = line_chain(['CH', 'C', 'CH', 'CH2', 'CH2', 'CH3'], [3, 1, 1, 1, 1]); at['m'] = (2, -1, 'CH3'); bd.append((2, 'm', 1))
    save('c4-l3b-3m1hexyne.svg', svg(490, 125, cond(30, 90, at, bd, sx=82)))

    # O11 س1: CH3CH=CHCH2CH=CH2 (1،4-هكسادايين)
    save('c4-l3b-14hexadiene.svg', svg(490, 70, cond(30, 35, *line_chain(['CH3', 'CH', 'CH', 'CH2', 'CH', 'CH2'], [1, 2, 1, 1, 2]), sx=82)))

    # O11 س3: 1،3،5-هكساترايين
    save('c4-l3b-135hexatriene.svg', svg(490, 70, cond(30, 35, *line_chain(['CH2', 'CH', 'CH', 'CH', 'CH', 'CH2'], [2, 1, 2, 1, 2]), sx=82)))

    # O11 س4: CH3CH2CH=CHCH2CH=CHCH3 (2،5-أوكتادايين)
    save('c4-l3b-25octadiene.svg', svg(640, 70, cond(30, 35, *line_chain(['CH3', 'CH2', 'CH', 'CH', 'CH2', 'CH', 'CH', 'CH3'], [1, 1, 2, 1, 1, 2, 1]), sx=82)))

    # O11 س5: CH3C(CH3)=CHCH=CH2 (4-ميثيل-1،3-بنتادايين)
    at, bd = line_chain(['CH3', 'C', 'CH', 'CH', 'CH2'], [1, 2, 1, 2]); at['m'] = (1, -1, 'CH3'); bd.append((1, 'm', 1))
    save('c4-l3b-4m13pentadiene.svg', svg(410, 120, cond(30, 90, at, bd, sx=82)))

    # O11 س7: CH2=C(CH3)CH2CH=C(CH3)CH3 (2،5-ثنائي ميثيل-1،4-هكسادايين)
    at, bd = line_chain(['CH2', 'C', 'CH2', 'CH', 'C', 'CH3'], [2, 1, 1, 2, 1])
    at.update({'m1': (1, 1, 'CH3'), 'm2': (4, 1, 'CH3')}); bd += [(1, 'm1', 1), (4, 'm2', 1)]
    save('c4-l3b-25dm14hexadiene.svg', svg(490, 120, cond(30, 35, at, bd, sx=82)))

    # O11 مقالي 1: CH3CH=C(CH3)CH=CH2 (3-ميثيل-1،3-بنتادايين)
    at, bd = line_chain(['CH3', 'CH', 'C', 'CH', 'CH2'], [1, 2, 1, 2]); at['m'] = (2, 1, 'CH3'); bd.append((2, 'm', 1))
    save('c4-l3b-3m13pentadiene.svg', svg(410, 120, cond(30, 35, at, bd, sx=82)))

    # O11 مقالي 2: (أ) 1،3،5-هبتاترايين (ب) 1،5-هكسادايين
    b = cond(30, 45, *line_chain(['CH2', 'CH', 'CH', 'CH', 'CH', 'CH', 'CH3'], [2, 1, 2, 1, 2, 1]), sx=80)
    b += cond(30, 150, *line_chain(['CH2', 'CH', 'CH2', 'CH2', 'CH', 'CH2'], [2, 1, 1, 1, 2]), sx=80)
    b += T(578, 50, '(أ)', 17, weight='bold', color=BLUE) + T(578, 155, '(ب)', 17, weight='bold', color=BLUE) + L(10, 97, 590, 97, MUTED, 1, '4 4')
    save('c4-l3b-two-polyenes.svg', svg(610, 185, b))

    # O12 س5: الإيثين: صيغة بنائية كاملة ونموذج الكرة والعصا
    b = cond(70, 80, {'c1': (0, 0, 'C', 'c'), 'c2': (1.2, 0, 'C', 'c'), 'h1': (-0.7, -0.8, 'H', 'c'), 'h2': (-0.7, 0.8, 'H', 'c'),
                      'h3': (1.9, -0.8, 'H', 'c'), 'h4': (1.9, 0.8, 'H', 'c')},
             [('c1', 'c2', 2), ('c1', 'h1', 1), ('c1', 'h2', 1), ('c2', 'h3', 1), ('c2', 'h4', 1)], sx=56, sy=56)
    b += GRAD
    c1, c2 = (380, 80), (460, 80)
    hs = [(c1, (c1[0] - 40, c1[1] - 46)), (c1, (c1[0] - 40, c1[1] + 46)), (c2, (c2[0] + 40, c2[1] - 46)), (c2, (c2[0] + 40, c2[1] + 46))]
    b += sticks(*c1, *c2, 2) + ''.join(sticks(*c, *h, 1) for c, h in hs)
    b += ''.join(ball(*h, 13, 'H') for _, h in hs) + ball(*c1, 22, 'C') + ball(*c2, 22, 'C')
    b += L(290, 15, 290, 145, MUTED, 1, '4 4')
    save('c4-l3b-ethene-model.svg', svg(560, 160, b))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    main()
