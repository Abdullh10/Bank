# رسوم الدرس 6-3 (الليبيدات — النصف الأول): أحماض دهنية بصيغ هيكلية (مشبعة وغير مشبعة سيس)، والجليسريد الثلاثي،
# وتفاعل التصبن، وجزيء الصابون، والصابون حول قطرة زيت، والطبقة الثنائية، وتركيب الستيرويد، والصيغة العامة للشمع.
# التشغيل: python3 data/chem22/gen/figs/C6-L3-a.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

U = 44          # طول الرابطة بالبكسل
FS = 18
SUB = '₀₁₂₃₄₅₆₇₈₉⁺⁻'
P = 'c6-l3a-'
GREY = '#8a94a3'

def lab_size(s, fs=FS):
    if not s: return 0, 0
    w = sum(0.40 * fs if ch in SUB else 0.66 * fs for ch in s)
    return w / 2, 0.42 * fs

def mol(nodes, edges, ox=0, oy=0, fs=FS):
    """nodes = {id: (x, y, label)} بوحدات U (label فارغ = رأس هيكلي)، edges = [(a, b, order)]."""
    Pp = {k: (ox + x * U, oy + y * U, s) for k, (x, y, s) in nodes.items()}
    nb = {k: [] for k in nodes}
    for a, c, _ in edges: nb[a].append(c); nb[c].append(a)
    b = ''
    for a, c, order in edges:
        x1, y1, s1 = Pp[a]; x2, y2, s2 = Pp[c]
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); ux, uy = dx / d, dy / d
        def trim(s):
            if not s: return 0
            hw, hh = lab_size(s, fs)
            return min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) + 4
        t1, t2 = trim(s1), trim(s2)
        ax, ay, bx, by = x1 + ux * t1, y1 + uy * t1, x2 - ux * t2, y2 - uy * t2
        b += L(round(ax, 1), round(ay, 1), round(bx, 1), round(by, 1), INK, 2)
        if order == 2:
            if s1 and s2 or (s1 or s2):     # رابطة ثنائية مع ذرة مكتوبة: خطان متوازيان متماثلان
                b = b[:b.rfind('<line')]
                for o in (-3.5, 3.5):
                    b += L(round(ax - uy * o, 1), round(ay + ux * o, 1), round(bx - uy * o, 1), round(by + ux * o, 1), INK, 2)
            else:                            # C=C هيكلية: خط داخلي أقصر نحو جهة الجيران
                others = [n for n in nb[a] + nb[c] if n not in (a, c)]
                mx = sum(Pp[n][0] for n in others) / len(others); my = sum(Pp[n][1] for n in others) / len(others)
                nx, ny = -uy, ux
                sg = 1 if (mx - (x1 + x2) / 2) * nx + (my - (y1 + y2) / 2) * ny > 0 else -1
                o = 7 * sg; sh = 0.16 * d
                b += L(round(ax + ux * sh + nx * o, 1), round(ay + uy * sh + ny * o, 1), round(bx - ux * sh + nx * o, 1), round(by - uy * sh + ny * o, 1), INK, 2)
    xs, ys = [], []
    for k, (x, y, s) in Pp.items():
        hw, hh = lab_size(s, fs)
        if s: b += T(round(x, 1), round(y + 0.36 * fs, 1), s, fs)
        xs += [x - hw, x + hw]; ys += [y - hh, y + hh]
    return b, (min(xs), min(ys), max(xs), max(ys))

def chain(nodes, edges, start, n, d0=30, cis=(), prefix='c', first_turn=60):
    """يضيف n ذرة كربون هيكلية بعد الرأس start بسلسلة متعرجة. d0 اتجاه الرابطة الأولى (درجات، y للأسفل).
    cis = مواقع k (ترقيم ذرات السلسلة المضافة بدءًا من 1) تبدأ عندها رابطة ثنائية سيس بين k و k+1."""
    x, y, _ = nodes[start]; d = d0; turn = first_turn; prev = start
    for k in range(1, n + 1):
        x += math.cos(math.radians(d)); y += math.sin(math.radians(d))
        nid = f'{prefix}{k}'; nodes[nid] = (x, y, '')
        edges.append((prev, nid, 2 if (k - 1) in cis and k > 1 else 1)); prev = nid
        # الدوران عند الذرة k: يتناوب، إلا عند الطرف الثاني لرابطة سيس فيكرر الاتجاه نفسه
        if (k - 1) in cis: pass
        else: turn = -turn
        d += turn
    return prev

def fatty_acid(nC, cis_db=(), prefix=''):
    """حمض دهني هيكلي: C1 (الكربوكسيل) في اليسار، cis_db = مواقع الروابط الثنائية بترقيم C1 = ذرة الكربوكسيل."""
    nodes = {prefix + 'C1': (0, 0, ''), prefix + 'O1': (0, -1, 'O'),
             prefix + 'O2': (math.cos(math.radians(150)), math.sin(math.radians(150)), 'HO')}
    edges = [(prefix + 'C1', prefix + 'O1', 2), (prefix + 'C1', prefix + 'O2', 1)]
    # ذرات السلسلة k = 1..nC-1 تقابل C2..C_nC؛ رابطة بين Cm و Cm+1 تقابل k = m-1
    chain(nodes, edges, prefix + 'C1', nC - 1, 30, cis=[m - 1 for m in cis_db], prefix=prefix + 'c', first_turn=60)
    return nodes, edges

def place(nodes, edges, x0, y0):
    _, bb = mol(nodes, edges)
    body, bb2 = mol(nodes, edges, x0 - bb[0], y0 - bb[1])
    return body, bb2

def single(name, nodes, edges, pad=24):
    _, bb = mol(nodes, edges)
    bd, _ = mol(nodes, edges, pad - bb[0], pad - bb[1])
    save(name, svg(round(bb[2] - bb[0] + 2 * pad), round(bb[3] - bb[1] + 2 * pad), bd))

def stacked(name, items, pad=24, gap=34, cap_w=48):
    """items = [(caption, nodes, edges)] بعضها تحت بعض، والتسمية (1) و(2) في اليمين."""
    body = ''; y = pad; wmax = 0; parts = []
    for cap, n, e in items:
        _, bb = mol(n, e); parts.append((cap, n, e, bb)); wmax = max(wmax, bb[2] - bb[0])
    W = round(wmax + 2 * pad + cap_w)
    for cap, n, e, bb in parts:
        bd, bb2 = place(n, e, pad, y)
        body += bd + T(W - pad, round((bb2[1] + bb2[3]) / 2 + 7), cap, 20, 'end', INK, 'bold')
        y = bb2[3] + gap
    save(name, svg(W, round(y - gap + pad), body))

# ---------------- 1) حمضان دهنيان: (1) الأوليك سيس-9 (غير مشبع)، (2) الستيريك (مشبع) ----------------
def fa_pair():
    n1, e1 = fatty_acid(18, cis_db=[9])
    n2, e2 = fatty_acid(18)
    stacked(P + 'fa-pair.svg', [('(1)', n1, e1), ('(2)', n2, e2)])

# ---------------- 2) حمض اللينوليك (18 ذرة كربون، رابطتان ثنائيتان سيس 9 و12) ----------------
def linoleic():
    n, e = fatty_acid(18, cis_db=[9, 12])
    single(P + 'linoleic.svg', n, e)

# ---------------- 3) جليسريد ثلاثي (ثلاثي ستيارات) بصيغة مكثفة كالكتاب ----------------
def tg_condensed(name, chains=('(CH₂)₁₆–CH₃',) * 3, w=330):
    body = ''
    x0, y0, dy = 40, 82, 92
    for i, ch in enumerate(chains):
        y = y0 + i * dy
        lab = 'CH₂' if i != 1 else 'CH'
        body += T(x0, y, lab, FS)
        body += L(x0 + 22, y - 6, x0 + 44, y - 6) + T(x0 + 56, y, 'O', FS) + L(x0 + 68, y - 6, x0 + 92, y - 6)
        body += T(x0 + 104, y, 'C', FS) + L(x0 + 101, y - 22, x0 + 101, y - 42) + L(x0 + 107, y - 22, x0 + 107, y - 42)
        body += T(x0 + 104, y - 48, 'O', FS) + L(x0 + 117, y - 6, x0 + 141, y - 6)
        body += T(x0 + 145, y, ch, FS, 'start')
        if i < 2: body += L(x0 - 4, y + 10, x0 - 4, y + dy - 22)
    save(name, svg(w, y0 + 2 * dy + 34, body))

# ---------------- 4) تفاعل التصبن (جليسريد ثلاثي + 3NaOH → جليسرول + 3 صابون) ----------------
def saponification():
    body = ''
    x0, y0, dy = 40, 64, 86
    for i in range(3):
        y = y0 + i * dy
        body += T(x0, y, 'CH₂' if i != 1 else 'CH', FS)
        body += L(x0 + 22, y - 6, x0 + 40, y - 6) + T(x0 + 50, y, 'O', FS) + L(x0 + 61, y - 6, x0 + 80, y - 6)
        body += T(x0 + 91, y, 'C', FS) + L(x0 + 88, y - 22, x0 + 88, y - 40) + L(x0 + 94, y - 22, x0 + 94, y - 40) + T(x0 + 91, y - 46, 'O', FS)
        body += L(x0 + 102, y - 6, x0 + 120, y - 6) + T(x0 + 124, y, '(CH₂)₁₄CH₃', FS, 'start')
        if i < 2: body += L(x0 - 4, y + 10, x0 - 4, y + dy - 22)
    ym = y0 + dy
    body += T(300, ym, '+ 3NaOH', FS, 'start')
    body += ARROW(388, ym - 6, 446, ym - 6)
    gx = 486
    for i in range(3):
        y = y0 + i * dy
        body += T(gx, y, 'CH₂OH' if i != 1 else 'CHOH', FS)
        if i < 2: body += L(gx - 18, y + 10, gx - 18, y + dy - 22)
    cx = 704
    body += T(cx - 26, ym, '+ 3CH₃(CH₂)₁₄', FS, 'end') + L(cx - 24, ym - 6, cx - 11, ym - 6) + T(cx, ym, 'C', FS)
    body += L(cx - 3, ym - 22, cx - 3, ym - 40) + L(cx + 3, ym - 22, cx + 3, ym - 40) + T(cx, ym - 46, 'O', FS)
    body += L(cx + 11, ym - 6, cx + 29, ym - 6) + T(cx + 33, ym, 'O⁻ Na⁺', FS, 'start')
    save(P + 'saponification.svg', svg(800, y0 + 2 * dy + 30, body))

# ---------------- 5) جزيء صابون (بالميتات الصوديوم) هيكليًا مع جزأين (أ) و(ب) ----------------
def soap():
    nodes = {'C1': (0, 0, ''), 'O1': (0, -1, 'O'), 'O2': (math.cos(math.radians(150)), math.sin(math.radians(150)), 'O⁻ Na⁺')}
    edges = [('C1', 'O1', 2), ('C1', 'O2', 1)]
    chain(nodes, edges, 'C1', 15, 30, prefix='c')
    pad = 30
    _, bb = mol(nodes, edges)
    ox, oy = pad - bb[0], pad + 10 - bb[1]
    bd, bb2 = mol(nodes, edges, ox, oy)
    W = round(bb2[2] + pad); H = round(bb2[3] + 70)
    c1x = ox
    yb = bb2[3] + 14
    # قوس للجزء (ب): رأس الكربوكسيلات، وقوس للجزء (أ): السلسلة الهيدروكربونية
    def brace(x1, x2, lab):
        return (L(x1, yb, x2, yb, BLUE, 2) + L(x1, yb, x1, yb - 8, BLUE, 2) + L(x2, yb, x2, yb - 8, BLUE, 2)
                + T((x1 + x2) / 2, yb + 26, lab, 18, 'middle', BLUE, 'bold'))
    body = bd + brace(round(bb2[0]), round(c1x + 8), '(ص)') + brace(round(c1x + 22), round(bb2[2]), '(س)')
    save(P + 'soap.svg', svg(W, H, body))

# ---------------- 6) جزيئات صابون حول قطرة زيت في الماء ----------------
def micelle():
    W, H = 460, 380; cx, cy, r = 230, 190, 70
    body = f'<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="14" fill="#e8f2fb" stroke="#9cc3e6"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#f3d98b" stroke="#c9a640" stroke-width="2"/>'
    body += T(cx, cy + 6, 'زيت أو أوساخ', 16, 'middle', INK, 'bold')
    n = 12
    for i in range(n):
        a = 2 * math.pi * i / n + 0.2
        hx, hy = cx + (r + 52) * math.cos(a), cy + (r + 52) * math.sin(a)
        # ذيل متعرج من الرأس نحو داخل القطرة
        pts = []
        for k in range(7):
            t = k / 6; rr = r + 42 - t * 56
            px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
            off = (5 if k % 2 else -5) if 0 < k < 6 else 0
            pts.append((px - off * math.sin(a), py + off * math.cos(a)))
        body += '<polyline fill="none" stroke="#1f2a44" stroke-width="2" points="' + ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in pts) + '"/>'
        body += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="9" fill="{RED}"/>'
    body += T(W - 26, 40, 'ماء', 18, 'end', BLUE, 'bold')
    # مفتاح الرموز
    body += f'<circle cx="{W-40}" cy="{H-58}" r="8" fill="{RED}"/>' + T(W - 56, H - 52, '(1)', 16, 'end', INK, 'bold')
    body += '<polyline fill="none" stroke="#1f2a44" stroke-width="2" points="' + f'{W-52},{H-28} {W-46},{H-34} {W-40},{H-28} {W-34},{H-34} {W-28},{H-28}' + '"/>' + T(W - 60, H - 24, '(2)', 16, 'end', INK, 'bold')
    save(P + 'micelle.svg', svg(W, H, body))

# ---------------- 7) طبقة ثنائية من الليبيدات الفوسفورية ----------------
def bilayer():
    W, H = 560, 300; x0, n, step = 70, 12, 34
    body = T(W / 2, 30, 'خارج الخلية', 17, 'middle', INK, 'bold') + T(W / 2, H - 14, 'داخل الخلية', 17, 'middle', INK, 'bold')
    top, bot = 70, 230
    for i in range(n):
        x = x0 + i * step
        for (yh, sgn) in ((top, 1), (bot, -1)):
            for dx in (-5, 5):
                pts = []
                for k in range(6):
                    yy = yh + sgn * (12 + k * 11)
                    pts.append((x + dx + (2.5 if k % 2 else -2.5), yy))
                body += '<polyline fill="none" stroke="#5b6676" stroke-width="2" points="' + ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in pts) + '"/>'
            body += f'<circle cx="{x}" cy="{yh}" r="12" fill="{BLUE}" stroke="#1d4f80"/>'
    save(P + 'bilayer.svg', svg(W, H, body))

# ---------------- 8) التركيب الأساسي للستيرويد (أربع حلقات) ----------------
def steroid():
    s = 46; h = s * math.sqrt(3) / 2
    def hexagon(cx, cy):
        return [(cx + s * math.cos(math.radians(30 + 60 * k)), cy + s * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    A = hexagon(80, 160); B = hexagon(80 + 2 * h, 160); C = hexagon(80 + 3 * h, 160 - 1.5 * s)
    # الحلقة الخماسية ملتحمة بالحلقة C على الضلع الأيمن
    p1, p2 = C[0], C[5]   # الرأسان الأيمنان للحلقة C
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    R5 = s / (2 * math.sin(math.pi / 5)); a5 = R5 * math.cos(math.pi / 5)
    cxp, cyp = mx + a5, my
    base = math.atan2(p1[1] - cyp, p1[0] - cxp)
    D = [(cxp + R5 * math.cos(base + 2 * math.pi * k / 5), cyp + R5 * math.sin(base + 2 * math.pi * k / 5)) for k in range(5)]
    body = ''
    for poly in (A, B, C, D):
        body += '<polygon fill="none" stroke="#1f2a44" stroke-width="2.4" points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in poly) + '"/>'
    xs = [p[0] for q in (A, B, C, D) for p in q]; ys = [p[1] for q in (A, B, C, D) for p in q]
    pad = 24
    body = f'<g transform="translate({pad - min(xs):.1f},{pad - min(ys):.1f})">{body}</g>'
    save(P + 'steroid.svg', svg(round(max(xs) - min(xs) + 2 * pad), round(max(ys) - min(ys) + 2 * pad), body))

# ---------------- 9) الصيغة العامة للشمع ----------------
def wax():
    y = 74; x = 30
    body = T(x, y, 'CH₃(CH₂)ₓ', FS + 2, 'start')
    x2 = x + 98
    body += L(x2, y - 7, x2 + 22, y - 7) + T(x2 + 34, y, 'C', FS + 2)
    body += L(x2 + 31, y - 24, x2 + 31, y - 44) + L(x2 + 37, y - 24, x2 + 37, y - 44) + T(x2 + 34, y - 50, 'O', FS + 2)
    body += L(x2 + 46, y - 7, x2 + 68, y - 7) + T(x2 + 80, y, 'O', FS + 2) + L(x2 + 93, y - 7, x2 + 115, y - 7)
    body += T(x2 + 120, y, '(CH₂)ᵧCH₃', FS + 2, 'start')
    save(P + 'wax.svg', svg(390, 100, body))

# ---------------- 10) جليسريدان ثلاثيان هيكليًا: (1) أحماض مشبعة، (2) أحماض غير مشبعة سيس ----------------
def tg_skeletal(cis):
    nodes, edges = {}, []
    for i in range(3):
        y = i * 1.9
        nodes[f'g{i}'] = (0, y, 'CH₂' if i != 1 else 'CH')
        nodes[f'o{i}'] = (1.25, y, 'O')
        nodes[f'k{i}'] = (2.25, y, '')
        nodes[f'ko{i}'] = (2.25, y - 1, 'O')
        edges += [(f'g{i}', f'o{i}', 1), (f'o{i}', f'k{i}', 1), (f'k{i}', f'ko{i}', 2)]
        if i: edges.append((f'g{i-1}', f'g{i}', 1))
        chain(nodes, edges, f'k{i}', 17, 30, cis=([8] if cis else []), prefix=f'c{i}_')
    return nodes, edges

def tg_pair():
    n1, e1 = tg_skeletal(False); n2, e2 = tg_skeletal(True)
    stacked(P + 'tg-pair.svg', [('(1)', n1, e1), ('(2)', n2, e2)], gap=40)

if __name__ == '__main__':
    fa_pair(); linoleic(); tg_condensed(P + 'triglyceride.svg'); saponification(); soap(); micelle(); bilayer(); steroid(); wax(); tg_pair()
