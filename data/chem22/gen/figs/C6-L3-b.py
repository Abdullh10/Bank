# رسوم الدرس 6-3 (الليبيدات — النصف الثاني): جليسريد ثلاثي مختلط، ومعادلة تصبن بناتج مجهول، وتركيب الليبيد الفوسفوري،
# ومناطق الطبقة الثنائية، وشمع النحل، والكولسترول، وتراص السلاسل المشبعة وغير المشبعة، والرابطة الثنائية سيس،
# وهدرجة حمض البالمتوليك، وحمض اللينولينيك.
# التشغيل: python3 data/chem22/gen/figs/C6-L3-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('l3a', os.path.join(os.path.dirname(__file__), 'C6-L3-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
mol, chain, fatty_acid, single, place, lab_size, U, FS = A.mol, A.chain, A.fatty_acid, A.single, A.place, A.lab_size, A.U, A.FS

P = 'c6-l3b-'

def ester_rows(x0, y0, dy, chains, left_labels=('CH₂', 'CH', 'CH₂')):
    """ثلاثة صفوف –O–C(=O)–R مرتبطة بهيكل الجليسرول (صيغة مكثفة كالكتاب)."""
    body = ''
    for i, ch in enumerate(chains):
        y = y0 + i * dy
        body += T(x0, y, left_labels[i], FS)
        body += L(x0 + 22, y - 6, x0 + 40, y - 6) + T(x0 + 50, y, 'O', FS) + L(x0 + 61, y - 6, x0 + 80, y - 6)
        body += T(x0 + 91, y, 'C', FS) + L(x0 + 88, y - 22, x0 + 88, y - 40) + L(x0 + 94, y - 22, x0 + 94, y - 40) + T(x0 + 91, y - 46, 'O', FS)
        body += L(x0 + 102, y - 6, x0 + 120, y - 6) + T(x0 + 124, y, ch, FS, 'start')
        if i < 2: body += L(x0 - 4, y + 10, x0 - 4, y + dy - 22)
    return body

# ---------------- 1) جليسريد ثلاثي مختلط (بالمتيك، أوليك، ستيريك) ----------------
def mixed_tg():
    body = ester_rows(40, 70, 90, ('(CH₂)₁₄CH₃', '(CH₂)₇CH=CH(CH₂)₇CH₃', '(CH₂)₁₆CH₃'))
    save(P + 'mixed-tg.svg', svg(440, 70 + 180 + 34, body))

# ---------------- 2) معادلة تصبن بناتج مجهول ----------------
def sapon_blank():
    x0, y0, dy = 40, 64, 86
    body = ester_rows(x0, y0, dy, ('(CH₂)₁₀CH₃',) * 3)
    ym = y0 + dy
    body += T(268, ym, '+ 3NaOH', FS, 'start')
    body += ARROW(356, ym - 6, 410, ym - 6)
    gx = 452
    for i in range(3):
        y = y0 + i * dy
        body += T(gx, y, 'CH₂OH' if i != 1 else 'CHOH', FS)
        if i < 2: body += L(gx - 18, y + 10, gx - 18, y + dy - 22)
    body += T(520, ym, '+  3', FS + 2, 'start')
    body += f'<rect x="560" y="{ym - 30}" width="74" height="44" rx="6" fill="#fff" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    body += T(597, ym + 2, '؟', 26, 'middle', RED, 'bold')
    save(P + 'sapon-blank.svg', svg(660, y0 + 2 * dy + 30, body))

# ---------------- 3) ليبيد فوسفوري (رأس فوسفات + ذيلان هيكليان) مع الحرفين (أ) و(ب) ----------------
def phospholipid():
    nodes = {
        'P': (0, 0, 'P'), 'Po': (0, -1, 'O'), 'Pm': (0, 1, 'O⁻'), 'Pl': (-1.1, 0, '⁻O'),
        'Pr': (1.1, 0, 'O'), 'g1': (2.4, 0, 'CH₂'), 'g2': (2.4, 1.8, 'CH'), 'g3': (2.4, 3.6, 'CH₂'),
        'o2': (3.7, 1.8, 'O'), 'k2': (4.7, 1.8, ''), 'ko2': (4.7, 0.8, 'O'),
        'o3': (3.7, 3.6, 'O'), 'k3': (4.7, 3.6, ''), 'ko3': (4.7, 2.6, 'O'),
    }
    edges = [('P', 'Po', 2), ('P', 'Pm', 1), ('P', 'Pl', 1), ('P', 'Pr', 1), ('Pr', 'g1', 1), ('g1', 'g2', 1), ('g2', 'g3', 1),
             ('g2', 'o2', 1), ('o2', 'k2', 1), ('k2', 'ko2', 2), ('g3', 'o3', 1), ('o3', 'k3', 1), ('k3', 'ko3', 2)]
    chain(nodes, edges, 'k2', 15, 30, prefix='a')
    chain(nodes, edges, 'k3', 15, 30, prefix='b')
    pad = 30
    _, bb = mol(nodes, edges)
    ox, oy = pad - bb[0], pad - bb[1]
    bd, bb2 = mol(nodes, edges, ox, oy)
    W = round(bb2[2] + pad); yb = bb2[3] + 16; H = round(yb + 46)
    def brace(x1, x2, lab):
        return (L(x1, yb, x2, yb, BLUE, 2) + L(x1, yb, x1, yb - 8, BLUE, 2) + L(x2, yb, x2, yb - 8, BLUE, 2)
                + T((x1 + x2) / 2, yb + 28, lab, 19, 'middle', BLUE, 'bold'))
    xP = ox + 1.1 * U  # ذرة O الجسرية
    xk = ox + 4.7 * U
    body = bd + brace(round(bb2[0]), round(xP + 10), '(س)') + brace(round(xk - 6), round(bb2[2]), '(ص)')
    save(P + 'phospholipid.svg', svg(W, H, body))

# ---------------- 4) مناطق الطبقة الثنائية مرقمة 1–4 ----------------
def membrane_regions():
    W, H = 600, 360; x0, n, step = 60, 12, 34
    top, bot = 110, 250
    body = f'<rect x="0" y="0" width="{W}" height="{top - 16}" fill="#e8f2fb"/>' + f'<rect x="0" y="{bot + 16}" width="{W}" height="{H - bot - 16}" fill="#e8f2fb"/>'
    body += T(250, 40, 'خارج الخلية (وسط مائي)', 16, 'middle', INK, 'bold') + T(250, H - 22, 'داخل الخلية (وسط مائي)', 16, 'middle', INK, 'bold')
    for i in range(n):
        x = x0 + i * step
        for (yh, sgn) in ((top, 1), (bot, -1)):
            for dx in (-5, 5):
                pts = [(x + dx + (2.5 if k % 2 else -2.5), yh + sgn * (12 + k * 11)) for k in range(6)]
                body += '<polyline fill="none" stroke="#5b6676" stroke-width="2" points="' + ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in pts) + '"/>'
            body += f'<circle cx="{x}" cy="{yh}" r="12" fill="{BLUE}" stroke="#1d4f80"/>'
    def tag(y, s):
        return L(x0 + n * step - 14, y, W - 64, y, MUTED, 1.5, '4 3') + f'<circle cx="{W - 44}" cy="{y}" r="15" fill="#fff" stroke="{INK}" stroke-width="2"/>' + T(W - 44, y + 6, s, 17, 'middle', INK, 'bold')
    body += tag(54, '1') + tag(top, '2') + tag((top + bot) / 2, '3') + tag(bot, '4')
    save(P + 'membrane-regions.svg', svg(W, H, body))

# ---------------- 5) شمع النحل: إستر حمض البالمتيك مع كحول ذي 30 ذرة كربون ----------------
def beeswax():
    y = 84; x = 24; fs = FS + 2
    body = T(x, y, 'CH₃(CH₂)₁₄', fs, 'start')
    x2 = x + 112
    body += L(x2, y - 7, x2 + 22, y - 7) + T(x2 + 34, y, 'C', fs)
    body += L(x2 + 31, y - 24, x2 + 31, y - 44) + L(x2 + 37, y - 24, x2 + 37, y - 44) + T(x2 + 34, y - 50, 'O', fs)
    body += L(x2 + 46, y - 7, x2 + 68, y - 7) + T(x2 + 80, y, 'O', fs) + L(x2 + 93, y - 7, x2 + 115, y - 7)
    body += T(x2 + 120, y, '(CH₂)₂₉CH₃', fs, 'start')
    yb = y + 22
    def brace(x1, x2_, lab):
        return (L(x1, yb, x2_, yb, BLUE, 2) + L(x1, yb, x1, yb - 8, BLUE, 2) + L(x2_, yb, x2_, yb - 8, BLUE, 2)
                + T((x1 + x2_) / 2, yb + 28, lab, 19, 'middle', BLUE, 'bold'))
    body += brace(x, x2 + 44, '(س)') + brace(x2 + 72, x2 + 238, '(ص)')
    save(P + 'beeswax.svg', svg(400, 160, body))

# ---------------- 6) الكولسترول بصيغة هيكلية ----------------
def cholesterol():
    s = U; h = s * math.sqrt(3) / 2
    def hexv(cx, cy): return [(cx + s * math.cos(math.radians(30 + 60 * k)), cy + s * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    cA = (0, 0); cB = (2 * h, 0); cC = (3 * h, -1.5 * s)
    Av, Bv, Cv = hexv(*cA), hexv(*cB), hexv(*cC)
    C = {}
    C[1], C[2], C[3], C[4], C[5], C[10] = Av[4], Av[3], Av[2], Av[1], Av[0], Av[5]
    C[6], C[7], C[8], C[9] = Bv[1], Bv[0], Bv[5], Bv[4]
    C[11], C[12], C[13], C[14] = Cv[3], Cv[4], Cv[5], Cv[0]
    p13, p14 = C[13], C[14]
    mx, my = (p13[0] + p14[0]) / 2, (p13[1] + p14[1]) / 2
    R5 = s / (2 * math.sin(math.pi / 5)); a5 = R5 * math.cos(math.pi / 5)
    cD = (mx + a5, my)
    b14 = math.atan2(p14[1] - cD[1], p14[0] - cD[0]); b13 = math.atan2(p13[1] - cD[1], p13[0] - cD[0])
    step = 2 * math.pi / 5
    # من C14 مبتعدًا عن C13: C15، C16، C17
    sgn = 1 if abs(((b14 + step) - b13 + math.pi) % (2 * math.pi) - math.pi) > 0.1 else -1
    for j, k in zip((15, 16, 17), (1, 2, 3)):
        a = b14 + sgn * k * step; C[j] = (cD[0] + R5 * math.cos(a), cD[1] + R5 * math.sin(a))
    bonds = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 10), (10, 1), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10),
             (9, 11), (11, 12), (12, 13), (13, 14), (14, 8), (14, 15), (15, 16), (16, 17), (17, 13)]
    def add(p, ang, L_=s): return (p[0] + L_ * math.cos(math.radians(ang)), p[1] + L_ * math.sin(math.radians(ang)))
    C[18] = add(C[13], -90); C[19] = add(C[10], -90)
    bonds += [(13, 18), (10, 19)]
    # السلسلة الجانبية عند C17
    out = math.degrees(math.atan2(C[17][1] - cD[1], C[17][0] - cD[0]))
    C[20] = add(C[17], out)
    C[21] = add(C[20], out - 60)
    C[22] = add(C[20], out + 60 - 60 + 0)  # يمتد أفقيًّا تقريبًا
    d = math.degrees(math.atan2(C[22][1] - C[20][1], C[22][0] - C[20][0]))
    C[22] = add(C[20], out + 60)
    seq = [22, 23, 24, 25]; ang = out + 60; turn = -60
    for a_, b_ in zip(seq, seq[1:]):
        ang += turn; turn = -turn; C[b_] = add(C[a_], ang)
    C[26] = add(C[25], ang + turn); C[27] = add(C[25], ang - turn + (0 if False else 0))
    C[27] = add(C[25], ang + turn - 120)
    bonds += [(17, 20), (20, 21), (20, 22), (22, 23), (23, 24), (24, 25), (25, 26), (25, 27)]
    nodes = {f'C{k}': (v[0] / s, v[1] / s, '') for k, v in C.items()}
    oh = add(C[3], 210)
    nodes['OH'] = (oh[0] / s, oh[1] / s, 'HO')
    edges = [(f'C{a}', f'C{b}', 2 if (a, b) == (5, 6) else 1) for a, b in bonds] + [('C3', 'OH', 1)]
    single(P + 'cholesterol.svg', nodes, edges, pad=26)

# ---------------- 7) تراص السلاسل: (1) مشبعة مستقيمة، (2) غير مشبعة بانثناءات سيس ----------------
def zig(x, y, n, ang, amp=7, seg=13):
    """سلسلة متعرجة تبدأ من (x, y) باتجاه ang (درجات)، تعيد النقاط."""
    pts = [(x, y)]; ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang)); nx, ny = -uy, ux
    for k in range(1, n + 1):
        o = amp if k % 2 else -amp
        pts.append((x + ux * seg * k + nx * o * (1 if k < n else 1), y + uy * seg * k + ny * o))
    return pts

def poly(pts, col='#1f2a44', w=2.2):
    return f'<polyline fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round" points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + '"/>'

def packing():
    W, H = 640, 330
    body = ''
    # اللوحة (1)
    px = 30
    body += f'<rect x="{px - 14}" y="20" width="270" height="270" rx="10" fill="#f6f8fb" stroke="#c9d2de"/>'
    for i in range(8):
        x = px + 22 + i * 30
        pts = zig(x, 64, 15, 90)
        body += f'<circle cx="{x}" cy="54" r="9" fill="{RED}"/>' + poly(pts)
    body += T(px + 121, 318, '(1)', 20, 'middle', INK, 'bold')
    # اللوحة (2)
    qx = 352
    body += f'<rect x="{qx - 14}" y="20" width="270" height="270" rx="10" fill="#f6f8fb" stroke="#c9d2de"/>'
    specs = [(0, 0, 7, 30), (46, 12, 9, 34), (92, -4, 6, 28), (138, 8, 8, 32), (184, 2, 7, 30)]
    for dx, dy, nk, a in specs:
        x = qx + 10 + dx; y0 = 64 + dy
        p1 = zig(x, y0, nk, 90)
        ex, ey = p1[-1]
        p2 = zig(ex, ey, 14 - nk, 90 - a)[1:]
        body += f'<circle cx="{x}" cy="{y0 - 10}" r="9" fill="{RED}"/>' + poly(p1 + p2)
    body += T(qx + 121, 318, '(2)', 20, 'middle', INK, 'bold')
    save(P + 'packing.svg', svg(W, H, body))

# ---------------- 8) رابطة ثنائية سيس داخل سلسلة حمض دهني ----------------
def cis_bond():
    nodes = {'Ca': (0, 0, 'C'), 'Cb': (1.3, 0, 'C'), 'Ha': (-0.65, -1.0, 'H'), 'Hb': (1.95, -1.0, 'H'),
             'La': (-0.75, 1.15, 'CH₂'), 'Lb': (2.05, 1.15, 'CH₂')}
    edges = [('Ca', 'Cb', 2), ('Ca', 'Ha', 1), ('Cb', 'Hb', 1), ('Ca', 'La', 1), ('Cb', 'Lb', 1)]
    _, bb = mol(nodes, edges)
    pad = 60; ox, oy = 150 - bb[0], 40 - bb[1]
    bd, bb2 = mol(nodes, edges, ox, oy)
    la = (ox + -0.75 * U, oy + 1.15 * U); lb = (ox + 2.05 * U, oy + 1.15 * U)
    ex1 = poly(zig(la[0] - 16, la[1] + 14, 7, 125, amp=6, seg=15), MUTED)
    ex2 = poly(zig(lb[0] + 16, lb[1] + 14, 7, 55, amp=6, seg=15), MUTED)
    body = bd + ex1 + ex2
    body += T(la[0] - 92, la[1] + 120, '… COOH', 16, 'middle', MUTED) + T(lb[0] + 92, lb[1] + 120, 'CH₃ …', 16, 'middle', MUTED)
    save(P + 'cis-bond.svg', svg(420, 300, body))

# ---------------- 9) هدرجة حمض البالمتوليك (16 ذرة كربون، سيس-9) ----------------
def palmitoleic_h2():
    n, e = fatty_acid(16, cis_db=[9])
    _, bb = mol(n, e)
    pad = 24
    bd, bb2 = mol(n, e, pad - bb[0], pad + 6 - bb[1])
    x = bb2[2] + 16; ym = (bb2[1] + bb2[3]) / 2 + 6
    body = bd + T(x, ym + 6, '+  H₂', FS + 2, 'start')
    body += ARROW(x + 66, ym, x + 120, ym) + T(x + 93, ym - 12, 'Pt', 14, 'middle', MUTED)
    body += f'<rect x="{x + 132}" y="{ym - 24}" width="64" height="44" rx="6" fill="#fff" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    body += T(x + 164, ym + 8, '؟', 26, 'middle', RED, 'bold')
    save(P + 'palmitoleic-h2.svg', svg(round(x + 216), round(bb2[3] + pad), body))

# ---------------- 10) حمض اللينولينيك (18 ذرة كربون، سيس 9 و12 و15) ----------------
def linolenic():
    n, e = fatty_acid(18, cis_db=[9, 12, 15])
    single(P + 'linolenic.svg', n, e)

if __name__ == '__main__':
    mixed_tg(); sapon_blank(); phospholipid(); membrane_regions(); beeswax(); cholesterol(); packing(); cis_bond(); palmitoleic_h2(); linolenic()
