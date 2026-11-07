# رسوم الدرس 4-1 (أ) — مقدمة إلى الهيدروكربونات: صيغ بنائية، ونماذج الكرة والعصا والنموذج الفراغي، وسلاسل الكربون، وتكوّن النفط.
# التشغيل: python3 data/chem22/gen/figs/C4-L1-a.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

GRAD = '''<defs>
<radialGradient id="gC" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#8a8f99"/><stop offset="0.55" stop-color="#2b2f36"/><stop offset="1" stop-color="#111316"/></radialGradient>
<radialGradient id="gH" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#ffffff"/><stop offset="0.7" stop-color="#e4e7ec"/><stop offset="1" stop-color="#aab1bc"/></radialGradient>
<radialGradient id="gHb" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#d6e6f7"/><stop offset="0.6" stop-color="#7fa7d4"/><stop offset="1" stop-color="#3f6c9f"/></radialGradient>
<radialGradient id="gCb" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#7d828c"/><stop offset="0.6" stop-color="#33373e"/><stop offset="1" stop-color="#15171a"/></radialGradient>
</defs>'''

def A(x, y, s, size=22, color=INK):
    """رمز ذرة (لاتيني، من اليسار إلى اليمين) متمركز عند (x, y)."""
    return f'<text x="{x}" y="{y + size * 0.36:.1f}" text-anchor="middle" font-size="{size}" fill="{color}" font-family="Arial,Helvetica,sans-serif" font-weight="bold">{esc(s)}</text>'

def bond(p, q, order=1, gap=13, w=2.4, color=INK):
    """رابطة بين مركزي ذرتين مع ترك فراغ حول الرمز؛ ثنائية = خطان متوازيان، ثلاثية = ثلاثة خطوط."""
    (x1, y1), (x2, y2) = p, q
    d = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / d, (y2 - y1) / d
    a = (x1 + ux * gap, y1 + uy * gap); b = (x2 - ux * gap, y2 - uy * gap)
    nx, ny = -uy, ux
    offs = {1: [0], 2: [-3.5, 3.5], 3: [-6, 0, 6]}[order]
    return ''.join(L(f'{a[0] + nx * o:.1f}', f'{a[1] + ny * o:.1f}', f'{b[0] + nx * o:.1f}', f'{b[1] + ny * o:.1f}', color, w) for o in offs)

def structure(atoms, bonds, ox=0, oy=0, size=22):
    """atoms: [(x, y, رمز)]، bonds: [(i, j, رتبة)] — صيغة بنائية كاملة."""
    pts = [(x + ox, y + oy) for x, y, _ in atoms]
    s = ''.join(bond(pts[i], pts[j], o) for i, j, o in bonds)
    s += ''.join(A(px, py, sym, size) for (px, py), (_, _, sym) in zip(pts, atoms))
    return s

def chain_struct(n_c, x0, y0, step=60, orders=None):
    """صيغة بنائية لسلسلة مستقيمة من n_c ذرات كربون مع جميع ذرات الهيدروجين (روابط أحادية فقط إن لم تُعط orders)."""
    atoms, bonds = [], []
    for i in range(n_c):
        atoms.append((x0 + i * step, y0, 'C'))
    for i in range(n_c - 1): bonds.append((i, i + 1, 1))
    for i in range(n_c):
        for dy in (-step, step):
            atoms.append((x0 + i * step, y0 + dy, 'H')); bonds.append((i, len(atoms) - 1, 1))
    atoms.append((x0 - step, y0, 'H')); bonds.append((0, len(atoms) - 1, 1))
    atoms.append((x0 + n_c * step, y0, 'H')); bonds.append((n_c - 1, len(atoms) - 1, 1))
    return atoms, bonds

def ball(x, y, r, kind):
    g = {'C': 'gC', 'H': 'gH', 'Cb': 'gCb', 'Hb': 'gHb'}[kind]
    st = '#6b7280' if kind == 'H' else '#0b0c0e'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="url(#{g})" stroke="{st}" stroke-width="1"/>'

def stick(p, q, w=7):
    return f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="#9aa1ab" stroke-width="{w}" stroke-linecap="round"/>' + \
           f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="#c9ced6" stroke-width="{w - 4}" stroke-linecap="round"/>'

# اتجاهات رباعية الأوجه مسقطة على المستوى (dx, dy, عمق)
TET = [(0, -1, 0.2), (-0.94, 0.42, 0.5), (0.94, 0.42, 0.5), (0.05, 0.62, -0.8)]

def methane_bs(cx, cy, L_=62):
    hs = [(cx + dx * L_, cy + dy * L_, z) for dx, dy, z in TET]
    s = ''
    back = [h for h in hs if h[2] < 0]; front = [h for h in hs if h[2] >= 0]
    for h in back: s += stick((cx, cy), h) + ball(h[0], h[1], 15, 'H')
    for h in front: s += stick((cx, cy), h)
    s += ball(cx, cy, 22, 'C')
    for h in front: s += ball(h[0], h[1], 16, 'H')
    return s

def methane_sf(cx, cy):
    s = ball(cx + 4, cy + 30, 30, 'Hb')               # ذرة H خلفية سفلية
    s += ball(cx, cy, 40, 'Cb')
    for dx, dy in [(0, -40), (-36, 18), (36, 18)]: s += ball(cx + dx, cy + dy, 30, 'Hb')
    return s

def panel_label(x, y, s): return T(x, y, s, 17, weight='bold')

def fig_methane_models():
    w, h = 760, 250
    b = GRAD
    # (1) صيغة جزيئية
    b += f'<text x="95" y="128" text-anchor="middle" font-size="30" fill="{INK}" font-family="Arial,sans-serif" font-weight="bold">CH<tspan font-size="20" dy="8">4</tspan></text>'
    # (2) صيغة بنائية
    b += structure([(0, 0, 'C'), (0, -55, 'H'), (0, 55, 'H'), (-55, 0, 'H'), (55, 0, 'H')], [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)], 285, 118)
    # (3) كرة وعصا
    b += methane_bs(475, 120)
    # (4) فراغي
    b += methane_sf(665, 122)
    for x, lab in [(95, '(1)'), (285, '(2)'), (475, '(3)'), (665, '(4)')]: b += panel_label(x, 228, lab)
    for x in (190, 380, 570): b += L(x, 25, x, 210, '#d5d9e0', 1, '5 5')
    save('c4-l1a-methane-models.svg', svg(w, h, b))

def fig_methane_bs():
    b = GRAD + methane_bs(150, 125, 70)
    b += ball(320, 70, 16, 'C') + T(345, 76, 'ذرة كربون', 15, 'start')
    b += ball(320, 120, 13, 'H') + T(345, 126, 'ذرة هيدروجين', 15, 'start')
    save('c4-l1a-methane-bs.svg', svg(470, 240, b))

def fig_ethane_bs():
    b = GRAD
    c1, c2 = (170, 130), (270, 130)
    hs1 = [(c1[0] - 50, c1[1] - 55, 1), (c1[0] - 70, c1[1] + 30, 1), (c1[0] - 10, c1[1] + 70, -1)]
    hs2 = [(c2[0] + 50, c2[1] - 55, 1), (c2[0] + 70, c2[1] + 30, 1), (c2[0] + 10, c2[1] + 70, -1)]
    for c, hs in ((c1, hs1), (c2, hs2)):
        for hx, hy, z in hs:
            if z < 0: b += stick(c, (hx, hy)) + ball(hx, hy, 15, 'H')
    b += stick(c1, c2, 8)
    for c, hs in ((c1, hs1), (c2, hs2)):
        for hx, hy, z in hs:
            if z > 0: b += stick(c, (hx, hy))
        b += ball(c[0], c[1], 22, 'C')
        for hx, hy, z in hs:
            if z > 0: b += ball(hx, hy, 16, 'H')
    b += ball(420, 90, 16, 'C') + T(445, 96, 'ذرة كربون', 15, 'start')
    b += ball(420, 140, 13, 'H') + T(445, 146, 'ذرة هيدروجين', 15, 'start')
    save('c4-l1a-ethane-bs.svg', svg(560, 240, b))

def fig_propane_struct():
    atoms, bonds = chain_struct(3, 110, 110)
    save('c4-l1a-propane-struct.svg', svg(400, 220, structure(atoms, bonds)))

def dots(cx, cy, pairs, color):
    """نقاط إلكترونات: pairs قائمة إزاحات (dx, dy)."""
    return ''.join(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="3.6" fill="{color}"/>' for dx, dy in pairs)

def fig_bonds():
    """ثلاثة أزواج C–C: بنقاط لويس وبالخطوط، مرقمة (1) (2) (3)، دون كتابة اسم نوع الرابطة."""
    w, h = 640, 270
    b = ''
    for k, (ox, n) in enumerate([(110, 1), (320, 2), (530, 3)]):
        # لويس: ذرتا C بينهما n أزواج مشتركة (أسود: إلكترونات ذرة، أزرق: إلكترونات الذرة الأخرى)
        y = 70
        b += A(ox - 35, y, 'C', 26) + A(ox + 35, y, 'C', 26)
        for i in range(n):
            dy = (i - (n - 1) / 2) * 12
            b += dots(ox, y - 1, [(-5, dy)], INK) + dots(ox, y - 1, [(5, dy)], BLUE)
        # إلكترونات غير مشتركة في الرابطة (تُشارك مع ذرات أخرى) — 4 − n لكل ذرة
        rest = 4 - n
        outer = [(-21, 0), (0, -21), (0, 21)][:rest] if rest != 2 else [(0, -21), (0, 21)]
        b += dots(ox - 35, y - 1, outer, INK)
        b += dots(ox + 35, y - 1, [(-dx, dy) for dx, dy in outer], BLUE)
        # تمثيل بالخطوط
        y2 = 175
        pts = [(ox - 35, y2), (ox + 35, y2)]
        b += bond(pts[0], pts[1], n, 14) + A(pts[0][0], y2, 'C', 26) + A(pts[1][0], y2, 'C', 26)
        stubs = {1: [(-1, 0), (0, -1), (0, 1)], 2: [(-0.8, -0.8), (-0.8, 0.8)], 3: [(-1, 0)]}[n]
        for sx, sy in stubs:
            b += L(f'{ox - 35 + sx * 15:.1f}', f'{y2 + sy * 15:.1f}', f'{ox - 35 + sx * 42:.1f}', f'{y2 + sy * 42:.1f}', INK, 2.4)
            b += L(f'{ox + 35 - sx * 15:.1f}', f'{y2 + sy * 15:.1f}', f'{ox + 35 - sx * 42:.1f}', f'{y2 + sy * 42:.1f}', INK, 2.4)
        b += panel_label(ox, 252, f'({k + 1})')
    b += L(215, 20, 215, 235, '#d5d9e0', 1, '5 5') + L(425, 20, 425, 235, '#d5d9e0', 1, '5 5')
    save('c4-l1a-bonds.svg', svg(w, h, b))

def fig_chains():
    """هياكل كربونية: سلسلة مستقيمة، سلسلة متفرعة، حلقة (ذرات الكربون فقط والروابط بينها)."""
    w, h = 700, 250
    b = ''
    # (1) مستقيمة
    pts = [(40 + i * 45, 110) for i in range(5)]
    b += ''.join(bond(pts[i], pts[i + 1], 1, 12) for i in range(4)) + ''.join(A(x, y, 'C') for x, y in pts)
    # (2) متفرعة
    main = [(290 + i * 45, 120) for i in range(4)]
    br = [(335, 60), (380, 180)]
    b += ''.join(bond(main[i], main[i + 1], 1, 12) for i in range(3)) + bond(main[1], br[0], 1, 12) + bond(main[2], br[1], 1, 12)
    b += ''.join(A(x, y, 'C') for x, y in main + br)
    # (3) حلقة سداسية
    cx, cy, r = 590, 115, 55
    ring = [(cx + r * math.cos(math.radians(90 + 60 * i)), cy + r * math.sin(math.radians(90 + 60 * i))) for i in range(6)]
    b += ''.join(bond(ring[i], ring[(i + 1) % 6], 1, 12) for i in range(6)) + ''.join(A(x, y, 'C') for x, y in ring)
    for x, lab in [(130, '(1)'), (357, '(2)'), (590, '(3)')]: b += panel_label(x, 230, lab)
    b += L(245, 25, 245, 210, '#d5d9e0', 1, '5 5') + L(480, 25, 480, 210, '#d5d9e0', 1, '5 5')
    b += T(w / 2, 22, 'ذرات الهيدروجين غير مرسومة', 13, color=MUTED)
    save('c4-l1a-chains.svg', svg(w, h, b))

def fig_four_molecules():
    """أربعة جزيئات بصيغ بنائية مرقمة: (1) إيثان، (2) ميثانول، (3) إيثين، (4) كلوروميثان."""
    w, h = 820, 250
    s = 50
    b = ''
    # (1) إيثان
    at, bd = chain_struct(2, 80, 110, s)
    b += structure(at, bd)
    # (2) ميثانول H3C–O–H
    x0 = 300
    at = [(x0, 110, 'C'), (x0, 110 - s, 'H'), (x0, 110 + s, 'H'), (x0 - s, 110, 'H'), (x0 + s, 110, 'O'), (x0 + 2 * s, 110, 'H')]
    b += structure(at, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (4, 5, 1)])
    # (3) إيثين H2C=CH2
    x0 = 500; y = 110
    at = [(x0, y, 'C'), (x0 + s + 10, y, 'C'), (x0 - 35, y - 40, 'H'), (x0 - 35, y + 40, 'H'), (x0 + s + 45, y - 40, 'H'), (x0 + s + 45, y + 40, 'H')]
    b += structure(at, [(0, 1, 2), (0, 2, 1), (0, 3, 1), (1, 4, 1), (1, 5, 1)])
    # (4) كلوروميثان
    x0 = 720
    at = [(x0, 110, 'C'), (x0, 110 - s, 'H'), (x0, 110 + s, 'H'), (x0 - s, 110, 'H'), (x0 + s + 5, 110, 'Cl')]
    b += structure(at, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)])
    for x, lab in [(105, '(1)'), (325, '(2)'), (530, '(3)'), (725, '(4)')]: b += panel_label(x, 232, lab)
    for x in (205, 420, 630): b += L(x, 25, x, 210, '#d5d9e0', 1, '5 5')
    save('c4-l1a-four-molecules.svg', svg(w, h, b))

def fig_carbon_compounds():
    """(1) O=C=O، (2) ميثانول CH3OH، (3) CaCO3 (صيغة)، (4) اليوريا."""
    w, h = 820, 250
    s = 50
    b = ''
    # (1) ثاني أكسيد الكربون
    b += structure([(55, 115, 'O'), (115, 115, 'C'), (175, 115, 'O')], [(0, 1, 2), (1, 2, 2)])
    # (2) ميثانول
    x0 = 300
    at = [(x0, 115, 'C'), (x0, 115 - s, 'H'), (x0, 115 + s, 'H'), (x0 - s, 115, 'H'), (x0 + s, 115, 'O'), (x0 + 2 * s, 115, 'H')]
    b += structure(at, [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (4, 5, 1)])
    # (3) كربونات الكالسيوم (مركب أيوني: يكتب بالصيغة)
    b += f'<text x="525" y="125" text-anchor="middle" font-size="26" fill="{INK}" font-family="Arial,sans-serif" font-weight="bold">CaCO<tspan font-size="18" dy="7">3</tspan></text>'
    # (4) اليوريا H2N–C(=O)–NH2
    x0 = 720
    at = [(x0, 130, 'C'), (x0, 75, 'O'), (x0 - 62, 160, 'NH₂'), (x0 + 62, 160, 'NH₂')]
    pts = [(x, y) for x, y, _ in at]
    b += bond(pts[0], pts[1], 2, 14) + bond(pts[0], pts[2], 1, 20) + bond(pts[0], pts[3], 1, 20)
    b += A(x0, 130, 'C') + A(x0, 75, 'O')
    b += f'<text x="{x0 - 62}" y="168" text-anchor="middle" font-size="22" fill="{INK}" font-family="Arial,sans-serif" font-weight="bold">H<tspan font-size="15" dy="6">2</tspan><tspan dy="-6">N</tspan></text>'
    b += f'<text x="{x0 + 62}" y="168" text-anchor="middle" font-size="22" fill="{INK}" font-family="Arial,sans-serif" font-weight="bold">NH<tspan font-size="15" dy="6">2</tspan></text>'
    for x, lab in [(115, '(1)'), (325, '(2)'), (525, '(3)'), (720, '(4)')]: b += panel_label(x, 232, lab)
    for x in (215, 425, 625): b += L(x, 25, x, 210, '#d5d9e0', 1, '5 5')
    save('c4-l1a-carbon-compounds.svg', svg(w, h, b))

def fig_urea():
    w, h = 360, 220
    x0 = 180
    b = bond((x0, 125), (x0, 65), 2, 14) + bond((x0, 125), (x0 - 70, 160), 1, 22) + bond((x0, 125), (x0 + 70, 160), 1, 22)
    b += A(x0, 125, 'C', 26) + A(x0, 65, 'O', 26)
    b += f'<text x="{x0 - 72}" y="170" text-anchor="middle" font-size="26" fill="{INK}" font-family="Arial,sans-serif" font-weight="bold">H<tspan font-size="17" dy="7">2</tspan><tspan dy="-7">N</tspan></text>'
    b += f'<text x="{x0 + 72}" y="170" text-anchor="middle" font-size="26" fill="{INK}" font-family="Arial,sans-serif" font-weight="bold">NH<tspan font-size="17" dy="7">2</tspan></text>'
    save('c4-l1a-urea.svg', svg(w, h, b))

def box(x, y, w, h, lines, fill='#eef3fa', stroke=BLUE, size=15):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    n = len(lines); y0 = y + h / 2 - (n - 1) * (size + 6) / 2 + size * 0.35
    for i, t in enumerate(lines): s += T(x + w / 2, y0 + i * (size + 6), t, size, weight='bold' if t == '؟' else 'normal')
    return s

def fig_oil_formation():
    """مخطط تتابعي (من اليمين إلى اليسار) لتكوّن النفط، والمرحلة الثالثة مجهولة (؟)."""
    w, h = 860, 180
    bw, bh, gap = 170, 100, 40
    xs = [w - 20 - bw - i * (bw + gap) for i in range(4)]
    texts = [['بقايا مخلوقات حية', 'عاشت في المحيطات'], ['تُدفن في قاع المحيط', 'تحت طبقات سميكة', 'من رواسب شبه طينية'], ['؟'], ['ينفذ النفط عبر صخور', 'ذات مسامات ويتجمع', 'في برك بالقشرة الأرضية']]
    b = ''
    for i, (x, t) in enumerate(zip(xs, texts)):
        b += box(x, 40, bw, bh, t, '#fdf3e7' if t == ['؟'] else '#eef3fa', '#c76a1c' if t == ['؟'] else BLUE, 26 if t == ['؟'] else 15)
        if i < 3: b += ARROW(x - 4, 90, x - gap + 4, 90, INK)
    b += T(w / 2, 22, 'مراحل تكوّن النفط عبر ملايين السنين', 15, weight='bold')
    save('c4-l1a-oil-formation.svg', svg(w, h, b))

if __name__ == '__main__':
    fig_methane_models(); fig_methane_bs(); fig_ethane_bs(); fig_propane_struct(); fig_bonds(); fig_chains()
    fig_four_molecules(); fig_carbon_compounds(); fig_urea(); fig_oil_formation()
