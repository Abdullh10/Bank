# رسوم الدرس 4-3 (الألكينات والألكاينات): صيغ بنائية مكثفة وكاملة وهيكلية لتسمية الألكينات والألكاينات وكتابة صيغها.
# التشغيل: python3 data/chem22/gen/figs/C4-L3-a.py
import sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

SZ = 19          # حجم نص الذرات
SX, SY = 84, 60  # المسافة الأفقية والرأسية بين مراكز المجموعات


def _w(s, size):
    """عرض تقريبي لنص كيميائي لاتيني (الأرقام سفلية أصغر)."""
    w = 0
    for ch in s:
        if ch.isdigit(): w += size * 0.45
        elif ch in 'HC': w += size * 0.72
        else: w += size * 0.62
    return w


def chem(x, y, s, size=SZ, color=INK):
    out, low = '', False
    for part in re.findall(r'\d+|[^\d]+', s):
        if part.isdigit():
            out += f'<tspan font-size="{size * 0.7:.1f}" dy="{"0" if low else "5"}">{part}</tspan>'; low = True
        else:
            out += f'<tspan dy="{"-5" if low else "0"}">{esc(part)}</tspan>'; low = False
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="start" font-size="{size}" fill="{color}" '
            f'{FONT} direction="ltr">{out}</text>')


def label(x, y, s, size=SZ, align='l'):
    """قناع أبيض ثم النص. align='l': ذرة C الأولى عند (x, y) والنص يمتد يمينًا؛ 'r': آخر ذرة C عند (x, y)
    والنص يمتد يسارًا (مثل H₃C)؛ 'c': النص في المنتصف."""
    w = _w(s, size)
    if align == 'l': x0 = x - _w(s[0], size) / 2
    elif align == 'r':
        i = s.rfind('C'); x0 = x - _w(s[:i], size) - _w('C', size) / 2
    else: x0 = x - w / 2
    m = f'<rect x="{x0 - 3:.1f}" y="{y - size * 0.62:.1f}" width="{w + 6:.1f}" height="{size * 1.3:.1f}" fill="#fff"/>'
    return m + chem(x0, y + size * 0.36, s, size)


def bond(x1, y1, x2, y2, order=1, w=2.3, gap=4.2):
    if order == 1: return L(x1, y1, x2, y2, INK, w)
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); nx, ny = -dy / d, dx / d
    if order == 2:
        return L(x1 + nx * gap, y1 + ny * gap, x2 + nx * gap, y2 + ny * gap, INK, w) + L(x1 - nx * gap, y1 - ny * gap, x2 - nx * gap, y2 - ny * gap, INK, w)
    g = gap * 1.45
    return L(x1, y1, x2, y2, INK, w) + L(x1 + nx * g, y1 + ny * g, x2 + nx * g, y2 + ny * g, INK, w) + L(x1 - nx * g, y1 - ny * g, x2 - nx * g, y2 - ny * g, INK, w)


def cond(ox, oy, atoms, bonds, sx=SX, sy=SY):
    """صيغة على شبكة: atoms = {key: (col, row, label[, align])}، bonds = [(k1, k2, order)].
    تُرسم الروابط من مركز إلى مركز ثم تُغطّى بقناع النص."""
    P = {k: (ox + v[0] * sx, oy + v[1] * sy) for k, v in atoms.items()}
    b = ''.join(bond(*P[a], *P[c], o) for a, c, o in bonds)
    for k, v in atoms.items():
        if v[2]: b += label(*P[k], v[2], SZ, v[3] if len(v) > 3 else 'l')
    return b


def line_chain(groups, orders):
    """سلسلة أفقية: groups قائمة نصوص، orders رتب الروابط بينها."""
    atoms = {i: (i, 0, g) for i, g in enumerate(groups)}
    bonds = [(i, i + 1, o) for i, o in enumerate(orders)]
    return atoms, bonds


def ring(ox, oy, n, r, dbl=(), subs=(), start=-90):
    """حلقة هيكلية منتظمة n رؤوس. dbl: أزواج رؤوس بينها رابطة ثنائية (خط داخلي)؛ subs: [(رأس, نص)] مجموعات خارج الحلقة."""
    pts = [(ox + r * math.cos(math.radians(start + 360 * k / n)), oy + r * math.sin(math.radians(start + 360 * k / n))) for k in range(n)]
    b = f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.3" stroke-linejoin="round"/>'
    for i, j in dbl:
        (x1, y1), (x2, y2) = pts[i], pts[j]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2; vx, vy = ox - mx, oy - my; d = math.hypot(vx, vy)
        off = 7; sh = 0.18
        ax, ay = x1 + (x2 - x1) * sh + vx / d * off, y1 + (y2 - y1) * sh + vy / d * off
        bx, by = x2 - (x2 - x1) * sh + vx / d * off, y2 - (y2 - y1) * sh + vy / d * off
        b += L(ax, ay, bx, by, INK, 2.3)
    for k, s in subs:
        x, y = pts[k]; vx, vy = x - ox, y - oy; d = math.hypot(vx, vy)
        ex, ey = x + vx / d * 52, y + vy / d * 52
        b += L(x, y, ex, ey, INK, 2.3) + label(ex + (8 if vx > 5 else -8 if vx < -5 else 0), ey, s, SZ, 'l' if vx > 5 else 'r' if vx < -5 else 'c')
    return b


def tag(x, y, s, size=17):
    return T(x, y, s, size, weight='bold', color=BLUE)


# ---------------- الرسوم ----------------
def main():
    # O01 س3: أربعة مركبات ثلاثية الكربون
    a1 = cond(60, 70, *line_chain(['CH3', 'CH2', 'CH3'], [1, 1]))
    a2 = cond(330, 70, *line_chain(['CH', 'C', 'CH3'], [3, 1]))
    a3 = ring(150, 225, 3, 42, start=-90)
    a4 = cond(330, 225, *line_chain(['CH2', 'CH', 'CH3'], [2, 1]))
    body = a1 + a2 + a3 + a4 + tag(140, 30, '(1)') + tag(410, 30, '(2)') + tag(150, 160, '(3)') + tag(410, 160, '(4)')
    body += L(270, 15, 270, 290, MUTED, 1, '4 4') + L(20, 140, 580, 140, MUTED, 1, '4 4')
    save('c4-l3a-o1-four.svg', svg(600, 295, body))

    # O01 مقالي 3: 1-بيوتين، بيوتان حلقي، بيوتان
    b = cond(40, 70, *line_chain(['CH2', 'CH', 'CH2', 'CH3'], [2, 1, 1]), sx=78)
    b += ring(130, 210, 4, 46, start=-45)
    b += cond(260, 210, *line_chain(['CH3', 'CH2', 'CH2', 'CH3'], [1, 1, 1]), sx=78)
    b += tag(160, 28, '(أ)') + tag(130, 145, '(ب)') + tag(380, 145, '(ج)') + L(225, 150, 225, 265, MUTED, 1, '4 4') + L(20, 115, 560, 115, MUTED, 1, '4 4')
    save('c4-l3a-o1-c4.svg', svg(560, 270, b))

    # O02 س1: 1-بيوتين مكتوبًا من اليمين CH3CH2CH=CH2
    save('c4-l3a-1-butene.svg', svg(330, 70, cond(30, 35, *line_chain(['CH3', 'CH2', 'CH', 'CH2'], [1, 1, 2]), sx=82)))

    # O02 س2: 4-ميثيل-2-بنتين
    at, bd = line_chain(['CH3', 'CH', 'CH', 'CH', 'CH3'], [1, 2, 1, 1]); at['m'] = (3, 1, 'CH3'); bd.append((3, 'm', 1))
    save('c4-l3a-4m2pentene.svg', svg(410, 120, cond(30, 35, at, bd)))

    # O02 س3: 2،2،6-ثلاثي ميثيل-3-أوكتين (مرسوم بسلسلة سفلية سباعية وتفرع إيثيل)
    at, bd = line_chain(['CH3', 'CH', 'CH2', 'CH', 'CH', 'C', 'CH3'], [1, 1, 1, 2, 1, 1])
    at.update({'e1': (1, -1, 'CH2'), 'e2': (1, -2, 'CH3'), 'm1': (5, -1, 'CH3'), 'm2': (5, 1, 'CH3')})
    bd += [(1, 'e1', 1), ('e1', 'e2', 1), (5, 'm1', 1), (5, 'm2', 1)]
    save('c4-l3a-226tm3octene.svg', svg(570, 210, cond(30, 135, at, bd, sx=82)))

    # O02 س4: 3-ميثيل هكسين حلقي (هيكلية)
    save('c4-l3a-3mcyclohexene.svg', svg(300, 220, ring(130, 120, 6, 50, dbl=[(0, 1)], subs=[(5, 'CH3')], start=-90)))

    # O02 س5: 1،3-بنتادايين
    save('c4-l3a-13pentadiene.svg', svg(410, 70, cond(30, 35, *line_chain(['CH2', 'CH', 'CH', 'CH', 'CH3'], [2, 1, 2, 1]))))

    # O02 س7: 2-إيثيل-1-هكسين
    at, bd = line_chain(['CH2', 'C', 'CH2', 'CH2', 'CH2', 'CH3'], [2, 1, 1, 1, 1])
    at.update({'e1': (1, -1, 'CH2'), 'e2': (1, -2, 'CH3')}); bd += [(1, 'e1', 1), ('e1', 'e2', 1)]
    save('c4-l3a-2e1hexene.svg', svg(490, 170, cond(30, 140, at, bd, sx=82)))

    # O02 مقالي 1: 2،4-ثنائي ميثيل-3-هكسين CH3CH2C(CH3)=CHCH(CH3)CH3
    at, bd = line_chain(['CH3', 'CH2', 'C', 'CH', 'CH', 'CH3'], [1, 1, 2, 1, 1])
    at.update({'m1': (2, 1, 'CH3'), 'm2': (4, 1, 'CH3')}); bd += [(2, 'm1', 1), (4, 'm2', 1)]
    save('c4-l3a-24dm3hexene.svg', svg(490, 120, cond(30, 35, at, bd, sx=82)))

    # O02 مقالي 2: (أ) 2-ميثيل-2-بيوتين (ب) 2-ميثيل-1،3-بيوتادايين
    at, bd = line_chain(['CH3', 'C', 'CH', 'CH3'], [1, 2, 1]); at['m'] = (1, -1, 'CH3'); bd.append((1, 'm', 1))
    b = cond(40, 110, at, bd, sx=80)
    at, bd = line_chain(['CH2', 'C', 'CH', 'CH2'], [2, 1, 2]); at['m'] = (1, -1, 'CH3'); bd.append((1, 'm', 1))
    b += cond(370, 110, at, bd, sx=80) + tag(155, 25, '(أ)') + tag(485, 25, '(ب)') + L(335, 15, 335, 135, MUTED, 1, '4 4')
    save('c4-l3a-two-alkenes.svg', svg(650, 140, b))

    # O02 مقالي 3: 4-ميثيل-2-هكسين مرسومًا بتفرع إيثيل
    at, bd = line_chain(['CH3', 'CH', 'CH', 'CH', 'CH3'], [1, 2, 1, 1])
    at.update({'e1': (3, 1, 'CH2'), 'e2': (3, 2, 'CH3')}); bd += [(3, 'e1', 1), ('e1', 'e2', 1)]
    save('c4-l3a-4m2hexene.svg', svg(410, 175, cond(30, 35, at, bd)))

    # O03 س5: أربع صيغ مرشحة لـ 2،4-ثنائي ميثيل-2-بنتين (الصحيحة رقم 3)
    def cand(ox, oy, groups, orders, br):
        at, bd = line_chain(groups, orders)
        for k, (i, d) in enumerate(br): at[f'b{k}'] = (i, d, 'CH3'); bd.append((i, f'b{k}', 1))
        return cond(ox, oy, at, bd, sx=74)
    b = cand(30, 75, ['CH2', 'C', 'CH2', 'CH', 'CH3'], [2, 1, 1, 1], [(1, -1), (3, 1)])      # 2,4-ثنائي ميثيل-1-بنتين
    b += cand(390, 75, ['CH3', 'CH', 'C', 'CH', 'CH3'], [1, 2, 1, 1], [(2, -1), (3, 1)])     # 3,4-ثنائي ميثيل-2-بنتين
    b += cand(30, 245, ['CH3', 'C', 'CH', 'CH', 'CH3'], [1, 2, 1, 1], [(1, -1), (3, 1)])     # 2,4-ثنائي ميثيل-2-بنتين ✓
    b += cand(390, 245, ['CH3', 'C', 'CH', 'CH2', 'CH3'], [1, 2, 1, 1], [(1, -1)])           # 2-ميثيل-2-بنتين
    b += tag(270, 22, '(1)') + tag(630, 22, '(2)') + tag(270, 192, '(3)') + tag(630, 192, '(4)')
    b += L(365, 10, 365, 325, MUTED, 1, '4 4') + L(15, 170, 715, 170, MUTED, 1, '4 4')
    save('c4-l3a-o3-four.svg', svg(730, 330, b))

    # O03 س6: رسم طالب لـ "1،3-بنتادايين" (وهو في الحقيقة 1،4)
    save('c4-l3a-14pentadiene.svg', svg(410, 70, cond(30, 35, *line_chain(['CH2', 'CH', 'CH2', 'CH', 'CH2'], [2, 1, 1, 2]))))

    # O04 س3: الإيثان والإيثين (صيغ بنائية كاملة)
    s = 56
    ethane = {'c1': (0, 0, 'C', 'c'), 'c2': (1, 0, 'C', 'c'), 'h1': (-1, 0, 'H', 'c'), 'h2': (0, -1, 'H', 'c'), 'h3': (0, 1, 'H', 'c'),
              'h4': (2, 0, 'H', 'c'), 'h5': (1, -1, 'H', 'c'), 'h6': (1, 1, 'H', 'c')}
    eb = [('c1', 'c2', 1)] + [(c, h, 1) for c, h in [('c1', 'h1'), ('c1', 'h2'), ('c1', 'h3'), ('c2', 'h4'), ('c2', 'h5'), ('c2', 'h6')]]
    b = cond(90, 110, ethane, eb, sx=s, sy=s)
    ethene = {'c1': (0, 0, 'C', 'c'), 'c2': (1.2, 0, 'C', 'c'), 'h1': (-0.7, -0.8, 'H', 'c'), 'h2': (-0.7, 0.8, 'H', 'c'),
              'h3': (1.9, -0.8, 'H', 'c'), 'h4': (1.9, 0.8, 'H', 'c')}
    nb = [('c1', 'c2', 2), ('c1', 'h1', 1), ('c1', 'h2', 1), ('c2', 'h3', 1), ('c2', 'h4', 1)]
    b += cond(410, 110, ethene, nb, sx=s, sy=s)
    b += tag(118, 25, '(أ)') + tag(443, 25, '(ب)') + L(300, 15, 300, 190, MUTED, 1, '4 4')
    save('c4-l3a-ethane-ethene.svg', svg(580, 200, b))

    # O05 س4: الإيثاين H–C≡C–H
    save('c4-l3a-ethyne.svg', svg(330, 70, cond(40, 35, *line_chain(['H', 'C', 'C', 'H'], [1, 3, 1]), sx=80)))

    # O05 س5: أربعة مركبات رباعية الكربون (الألكاين رقم 2)
    b = cond(30, 70, *line_chain(['CH3', 'CH', 'CH', 'CH3'], [1, 2, 1]), sx=76)
    b += cond(380, 70, *line_chain(['CH3', 'C', 'C', 'CH3'], [1, 3, 1]), sx=76)
    b += cond(30, 190, *line_chain(['CH3', 'CH2', 'CH2', 'CH3'], [1, 1, 1]), sx=76)
    b += cond(380, 190, *line_chain(['CH2', 'CH', 'CH', 'CH2'], [2, 1, 2]), sx=76)
    b += tag(155, 30, '(1)') + tag(505, 30, '(2)') + tag(155, 150, '(3)') + tag(505, 150, '(4)')
    b += L(350, 10, 350, 220, MUTED, 1, '4 4') + L(15, 125, 685, 125, MUTED, 1, '4 4')
    save('c4-l3a-o5-four.svg', svg(700, 225, b))

    # O05 مقالي 3: ثلاث مركبات C5H8
    b = cond(40, 65, *line_chain(['CH', 'C', 'CH2', 'CH2', 'CH3'], [3, 1, 1, 1]), sx=76)
    b += ring(130, 210, 5, 48, dbl=[(1, 2)], start=-90)
    b += cond(300, 210, *line_chain(['CH3', 'C', 'C', 'CH2', 'CH3'], [1, 3, 1, 1]), sx=72)
    b += tag(200, 25, '(أ)') + tag(130, 140, '(ب)') + tag(440, 140, '(ج)') + L(260, 130, 260, 265, MUTED, 1, '4 4') + L(15, 110, 645, 110, MUTED, 1, '4 4')
    save('c4-l3a-c5h8.svg', svg(660, 275, b))

    # O06 س1: 1-بنتاين مكتوبًا من اليمين CH3CH2CH2C≡CH
    save('c4-l3a-1pentyne.svg', svg(410, 70, cond(30, 35, *line_chain(['CH3', 'CH2', 'CH2', 'C', 'CH'], [1, 1, 1, 3]))))

    # O06 س2: 4-ميثيل-2-بنتاين CH3C≡CCH(CH3)CH3
    at, bd = line_chain(['CH3', 'C', 'C', 'CH', 'CH3'], [1, 3, 1, 1]); at['m'] = (3, 1, 'CH3'); bd.append((3, 'm', 1))
    save('c4-l3a-4m2pentyne.svg', svg(410, 120, cond(30, 35, at, bd)))

    # O06 س3: 3-ميثيل-1-بيوتاين CH≡CCH(CH3)CH3
    at, bd = line_chain(['CH', 'C', 'CH', 'CH3'], [3, 1, 1]); at['m'] = (2, -1, 'CH3'); bd.append((2, 'm', 1))
    save('c4-l3a-3m1butyne.svg', svg(330, 120, cond(30, 90, at, bd)))

    # O06 س4: 2،2-ثنائي ميثيل-3-هكساين
    at, bd = line_chain(['CH3', 'C', 'C', 'C', 'CH2', 'CH3'], [1, 1, 3, 1, 1])
    at.update({'m1': (1, -1, 'CH3'), 'm2': (1, 1, 'CH3')}); bd += [(1, 'm1', 1), (1, 'm2', 1)]
    save('c4-l3a-22dm3hexyne.svg', svg(490, 160, cond(30, 80, at, bd, sx=82)))

    # O06 س7: 4-ميثيل-1-هكساين مرسومًا بتفرع إيثيل CH≡CCH2CH(C2H5)CH3
    at, bd = line_chain(['CH', 'C', 'CH2', 'CH', 'CH3'], [3, 1, 1, 1])
    at.update({'e1': (3, 1, 'CH2'), 'e2': (3, 2, 'CH3')}); bd += [(3, 'e1', 1), ('e1', 'e2', 1)]
    save('c4-l3a-4m1hexyne.svg', svg(410, 175, cond(30, 35, at, bd)))

    # O06 مقالي 1: (أ) 2-بنتاين (ب) 5-ميثيل-2-هكساين
    b = cond(30, 45, *line_chain(['CH3', 'CH2', 'C', 'C', 'CH3'], [1, 1, 3, 1]), sx=80)
    at, bd = line_chain(['CH3', 'C', 'C', 'CH2', 'CH', 'CH3'], [1, 3, 1, 1, 1]); at['m'] = (4, 1, 'CH3'); bd.append((4, 'm', 1))
    b += cond(30, 170, at, bd, sx=80)
    b += T(530, 50, '(أ)', 17, weight='bold', color=BLUE) + T(530, 175, '(ب)', 17, weight='bold', color=BLUE) + L(10, 100, 550, 100, MUTED, 1, '4 4')
    save('c4-l3a-two-alkynes.svg', svg(560, 245, b))

    # O06 مقالي 2: 2،5-ثنائي ميثيل-3-هبتاين
    at, bd = line_chain(['CH3', 'CH', 'C', 'C', 'CH', 'CH2', 'CH3'], [1, 1, 3, 1, 1, 1])
    at.update({'m1': (1, 1, 'CH3'), 'm2': (4, 1, 'CH3')}); bd += [(1, 'm1', 1), (4, 'm2', 1)]
    save('c4-l3a-25dm3heptyne.svg', svg(570, 120, cond(30, 35, at, bd, sx=82)))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    main()
