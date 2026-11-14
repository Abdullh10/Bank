# رسوم الدرس 6-1 (أ) — البروتينات: التركيب العام للحمض الأميني، وأحماض أمينية من الجدول 6-1، وتكوين الرابطة الببتيدية،
# وببتيدات، وسلسلة بروتين، وتغير الخواص الطبيعية، والشكل الحلزوني والصحيفة المطوية، وعمل الإنزيم.
# التشغيل: python3 data/chem22/gen/figs/C6-L1-a.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

P = 'c6-l1a-'
SZ = 22
GX = 62   # المسافة الأفقية بين ذرتين متجاورتين
GY = 60   # المسافة الرأسية
LAT = 'font-family="Arial,Helvetica,sans-serif" font-weight="bold"'

def cw(ch, size, subs=False):
    if subs: return 0.556 * size * 0.72
    if ch.isdigit(): return 0.556 * size
    if ch in '()': return 0.333 * size
    if ch == ' ': return 0.28 * size
    if ch in 'HNOCSR': return 0.72 * size
    if ch.isupper(): return 0.70 * size
    return 0.56 * size

def chars(s):
    """قائمة (حرف، منخفض؟) — الرقم بعد حرف أو قوس يُكتب منخفضًا."""
    out = []; prev = ''
    for ch in s:
        sub = ch.isdigit() and prev != '' and (prev.isalpha() or prev == ')' or (prev.isdigit() and out and out[-1][1]))
        out.append((ch, sub)); prev = ch
    return out

def ftext(x, yc, s, size=SZ, color=INK):
    """نص لاتيني يبدأ من x (الطرف الأيسر)، yc = منتصف السطر."""
    out = ''; d = size * 0.28; cs = chars(s); i = 0
    while i < len(cs):
        ch, sb = cs[i]
        if sb:
            j = i
            while j < len(cs) and cs[j][1]: j += 1
            out += f'<tspan dy="{d:.1f}" font-size="{size * 0.72:.1f}">{"".join(c for c, _ in cs[i:j])}</tspan><tspan dy="{-d:.1f}">​</tspan>'
            i = j; continue
        out += esc(ch); i += 1
    return f'<text x="{x:.1f}" y="{yc + size * 0.36:.1f}" font-size="{size}" fill="{color}" {LAT}>{out}</text>'

class Mol:
    """جزيء على شبكة: ذرات بإحداثيات (عمود، صف) ورموز، وروابط تُقصَّر عند حدود الرموز."""
    def __init__(self, ox, oy, size=SZ):
        self.ox, self.oy, self.size = ox, oy, size
        self.atoms = {}; self.body = ''

    def pos(self, c, r): return self.ox + c * GX, self.oy + r * GY

    def atom(self, key, c, r, label, attach=None, color=INK):
        x, y = self.pos(c, r)
        cs = chars(label)
        ws = [cw(ch, self.size, sb) for ch, sb in cs]
        if attach is None: attach = 0
        left = sum(ws[:attach]) + ws[attach] / 2
        right = sum(ws) - left
        self.atoms[key] = (x, y, left, right, bool(label))
        if label: self.body += ftext(x - left, y, label, self.size, color)
        return self

    def vertex(self, key, x, y):
        self.atoms[key] = (x, y, 0, 0, False); return self

    def _gap(self, a, dx, dy):
        x, y, left, right, has = self.atoms[a]
        if not has: return 0
        hx = (right if dx > 0 else left) + 4
        hy = self.size * 0.5 + 3
        ts = []
        if abs(dx) > 1e-6: ts.append(hx / abs(dx))
        if abs(dy) > 1e-6: ts.append(hy / abs(dy))
        return min(ts)

    def bond(self, a, b, order=1, color=INK, w=2.4):
        x1, y1 = self.atoms[a][:2]; x2, y2 = self.atoms[b][:2]
        L0 = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L0, (y2 - y1) / L0
        g1 = self._gap(a, ux, uy); g2 = self._gap(b, -ux, -uy)
        sx, sy = x1 + ux * g1, y1 + uy * g1; ex, ey = x2 - ux * g2, y2 - uy * g2
        nx, ny = -uy, ux
        offs = {1: [0], 2: [-3.5, 3.5], 3: [-6, 0, 6]}[order]
        for o in offs:
            self.body += L(f'{sx + nx * o:.1f}', f'{sy + ny * o:.1f}', f'{ex + nx * o:.1f}', f'{ey + ny * o:.1f}', color, w)
        return self

    def ring(self, key_attach, cx, cy, r=30, att_angle=-90):
        """حلقة بنزين بدائرة؛ تُعيد رأس الارتباط (زاوية att_angle بالدرجات، −90 = أسفل في إحداثيات الشاشة... نستعمل 90 للأسفل)."""
        pts = [(cx + r * math.cos(math.radians(30 + 60 * k)), cy + r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
        self.body += f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
        self.body += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.58:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
        ax = cx + r * math.cos(math.radians(att_angle)); ay = cy + r * math.sin(math.radians(att_angle))
        self.vertex(key_attach, ax, ay)
        return self

# ---------- لبنات الحمض الأميني ----------
def backbone(m, c, r, pre='', nleft='H2N', cterm=True, side=None, nH_up=False, n_key=None):
    """هيكل حمض أميني يبدأ عند N في العمود c: N — Cα — C(=O) — [OH].
    side: دالة ترسم السلسلة الجانبية فوق Cα وتُعيد مفتاح أول ذرة فيها."""
    k = pre
    if nleft == 'H2N':
        m.atom(k + 'N', c, r, 'H2N', attach=2)
    elif nleft == 'HN':  # N ببتيدية: H فوقها
        m.atom(k + 'N', c, r, 'N'); m.atom(k + 'NH', c, r - 1, 'H'); m.bond(k + 'N', k + 'NH')
    m.atom(k + 'Ca', c + 1, r, 'C'); m.bond(k + 'N', k + 'Ca')
    m.atom(k + 'Ha', c + 1, r + 1, 'H'); m.bond(k + 'Ca', k + 'Ha')
    m.atom(k + 'C', c + 2, r, 'C'); m.bond(k + 'Ca', k + 'C')
    m.atom(k + 'O', c + 2, r + 1, 'O'); m.bond(k + 'C', k + 'O', 2)
    if cterm:
        m.atom(k + 'OH', c + 3, r, 'OH', attach=0); m.bond(k + 'C', k + 'OH')
    if side: m.bond(k + 'Ca', side(m, c + 1, r))
    return m

def sc_label(lab, attach=None):
    def f(m, c, r, _l=lab):
        key = f'sc{c}{r}{_l}'; m.atom(key, c, r - 1, _l, attach); return key
    return f

def sc_chain(labels):
    """سلسلة جانبية رأسية: labels من الأسفل إلى الأعلى."""
    def f(m, c, r):
        keys = []
        for i, lab in enumerate(labels):
            key = f'sc{c}{r}_{i}'; m.atom(key, c, r - 1 - i, lab, 0 if len(lab) > 1 and lab[0] in 'CS' else None)
            keys.append(key)
            if i: m.bond(keys[i - 1], key)
        return keys[0]
    return f

def sc_val():
    def f(m, c, r):
        k = f'v{c}{r}'
        m.atom(k + 'CH', c, r - 1, 'CH', 0)
        m.atom(k + 'L', c - 0.8, r - 1.8, 'H3C', 2); m.atom(k + 'R', c + 0.8, r - 1.8, 'CH3', 0)
        m.bond(k + 'CH', k + 'L'); m.bond(k + 'CH', k + 'R')
        return k + 'CH'
    return f

def sc_glu():
    def f(m, c, r):
        k = f'g{c}{r}'
        m.atom(k + '1', c, r - 1, 'CH2', 0); m.atom(k + '2', c, r - 2, 'CH2', 0); m.bond(k + '1', k + '2')
        m.atom(k + 'C', c, r - 3, 'C'); m.bond(k + '2', k + 'C')
        m.atom(k + 'O', c - 0.8, r - 3.8, 'O'); m.bond(k + 'C', k + 'O', 2)
        m.atom(k + 'OH', c + 0.8, r - 3.8, 'OH', 0); m.bond(k + 'C', k + 'OH')
        return k + '1'
    return f

def sc_phe():
    def f(m, c, r):
        k = f'p{c}{r}'
        m.atom(k + '1', c, r - 1, 'CH2', 0)
        x, y = m.pos(c, r - 1)
        m.ring(k + 'v', x, y - 13 - 22 - 30, 30, 90)
        m.bond(k + '1', k + 'v')
        return k + '1'
    return f

def finish(name, m, w, h, extra=''):
    save(name, svg(w, h, m.body + extra))

def box(x, y, w, h, color):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="{color}" fill-opacity="0.13" stroke="{color}" stroke-width="1.8" stroke-dasharray="5 3"/>'

def tag(x, y, s, color=INK):
    return f'<circle cx="{x}" cy="{y}" r="15" fill="#fff" stroke="{color}" stroke-width="2"/>' + \
           f'<text x="{x}" y="{y + 6}" text-anchor="middle" font-size="17" fill="{color}" {LAT}>{s}</text>'

def caption(x, y, s, size=18):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{INK}" {LAT}>{esc(s)}</text>'

def main():
    os.makedirs(OUT, exist_ok=True)

    # 1) التركيب العام بحروف A–D (دون أسماء)
    m = Mol(70, 120)
    m.atom('R', 2, -1, 'R'); m.atom('N', 1, 0, 'H2N', 2); m.atom('Ca', 2, 0, 'C'); m.atom('H', 2, 1, 'H')
    m.atom('C', 3, 0, 'C'); m.atom('O', 3, 1, 'O'); m.atom('OH', 4, 0, 'OH', 0)
    m.bond('R', 'Ca'); m.bond('N', 'Ca'); m.bond('Ca', 'H'); m.bond('Ca', 'C'); m.bond('C', 'O', 2); m.bond('C', 'OH')
    x0, y0 = m.pos(0, 0)
    ex = box(x0 + GX - 46, y0 - 22, 62, 44, BLUE) + tag(x0 + GX - 30, y0 - 48, 'A', BLUE)
    cx, cy = m.pos(3, 0)
    ex += box(cx - 18, cy - 22, GX + 52, GY + 46, RED) + tag(cx + GX + 50, cy - 30, 'B', RED)
    hx, hy = m.pos(2, 1)
    ex += box(hx - 18, hy - 20, 36, 40, GREEN) + tag(hx - 40, hy + 8, 'C', GREEN)
    rx, ry = m.pos(2, -1)
    ex += box(rx - 18, ry - 20, 36, 40, '#8a5a00') + tag(rx - 40, ry, 'D', '#8a5a00')
    finish(P + 'aa-general.svg', m, 400, 220, ex)

    # 2) الجلايسين، 3) السيرين، 4) السيستين (كلٌّ وحده، دون اسم)
    for nm, side, oy, h in [('glycine', sc_label('H'), 110, 210), ('serine', sc_chain(['CH2', 'OH']), 170, 270),
                            ('cysteine', sc_chain(['CH2', 'SH']), 170, 270)]:
        m = Mol(60, oy); backbone(m, 0, 0, side=side)
        finish(P + nm + '.svg', m, 330, h)

    # 5) أربعة أحماض أمينية مرقمة: فالين، لايسين، حمض الجلوتاميك، فينيل ألانين
    W = 0; parts = ''
    specs = [('(1)', sc_val()), ('(2)', sc_chain(['CH2', 'CH2', 'CH2', 'CH2', 'NH2'])), ('(3)', sc_glu()), ('(4)', sc_phe())]
    m = Mol(0, 0); oy = 370
    for i, (lab, side) in enumerate(specs):
        m.ox = 55 + i * 290; m.oy = oy
        backbone(m, 0, 0, pre=f'a{i}', side=side)
        x, y = m.pos(1.5, 0)
        parts += caption(x, y + 110, lab, 22)
    finish(P + 'aa-four.svg', m, 1170, 510, parts)

    # 6) تفاعل تكوين ثنائي الببتيد (سطران)
    m = Mol(60, 130)
    backbone(m, 0, 0, pre='p', side=sc_label('R1'))
    x, y = m.pos(4, 0); plus = caption(x + 10, y + 8, '+', 30)
    m.ox = 60 + 5 * GX
    m.atom('qHl', 0, 0, 'H'); m.atom('qN', 1, 0, 'N'); m.atom('qNH', 1, -1, 'H'); m.bond('qHl', 'qN'); m.bond('qN', 'qNH')
    m.atom('qCa', 2, 0, 'C'); m.bond('qN', 'qCa'); m.atom('qHa', 2, 1, 'H'); m.bond('qCa', 'qHa')
    m.atom('qR', 2, -1, 'R2'); m.bond('qCa', 'qR')
    m.atom('qC', 3, 0, 'C'); m.bond('qCa', 'qC'); m.atom('qO', 3, 1, 'O'); m.bond('qC', 'qO', 2)
    m.atom('qOH', 4, 0, 'OH', 0); m.bond('qC', 'qOH')
    m.ox = 150; m.oy = 340
    arr = ARROW(25, 340, 90, 340, INK, 2.5)
    backbone(m, 0, 0, pre='d', cterm=False, side=sc_label('R1'))
    backbone(m, 3, 0, pre='e', nleft='HN', side=sc_label('R2'))
    m.bond('dC', 'eN')
    x, y = m.pos(7, 0); plus2 = caption(x - 4, y + 8, '+', 30)
    m.atom('w', 7.6, 0, 'H2O', 0)
    finish(P + 'peptide-rxn.svg', m, 740, 420, plus + arr + plus2)

    # 7) ببتيد رباعي: Gly–Ser–Val–Cys
    m = Mol(50, 200)
    backbone(m, 0, 0, pre='a', cterm=False, side=sc_label('H'))
    backbone(m, 3, 0, pre='b', nleft='HN', cterm=False, side=sc_chain(['CH2', 'OH']))
    backbone(m, 6, 0, pre='c', nleft='HN', cterm=False, side=sc_val())
    backbone(m, 9, 0, pre='d', nleft='HN', cterm=True, side=sc_chain(['CH2', 'SH']))
    m.bond('aC', 'bN'); m.bond('bC', 'cN'); m.bond('cC', 'dN')
    finish(P + 'tetrapeptide.svg', m, 900, 290)

    # 8) Gly–Phe و Phe–Gly (أحدهما فوق الآخر)
    m = Mol(70, 190)
    backbone(m, 0, 0, pre='a', cterm=False, side=sc_label('H'))
    backbone(m, 3, 0, pre='b', nleft='HN', side=sc_phe())
    m.bond('aC', 'bN')
    x, _ = m.pos(3, 0); cap = caption(x, 300, '(1)', 22)
    m.oy = 520
    backbone(m, 0, 0, pre='c', cterm=False, side=sc_phe())
    backbone(m, 3, 0, pre='d', nleft='HN', side=sc_label('H'))
    m.bond('cC', 'dN')
    cap += caption(x, 630, '(2)', 22)
    cap += L(20, 330, 520, 330, MUTED, 1.5, '6 5')
    finish(P + 'glyphe.svg', m, 540, 650, cap)

    # 9) سلسلة بروتين من خرزات
    s = ''; pts = []
    for i in range(12):
        x = 85 + i * 52; y = 90 + 38 * math.sin(i * 0.9)
        pts.append((x, y))
    cols = ['#2a6fb0', '#b03a2e', '#1f7a4d', '#8a5a00', '#6b3fa0', '#2a6fb0', '#1f7a4d', '#b03a2e', '#8a5a00', '#6b3fa0', '#1f7a4d', '#2a6fb0']
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]): s += L(f'{x1:.1f}', f'{y1:.1f}', f'{x2:.1f}', f'{y2:.1f}', INK, 3)
    for (x, y), c in zip(pts, cols):
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{c}" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<text x="{pts[0][0] - 62:.0f}" y="{pts[0][1] + 6:.0f}" font-size="26" fill="{INK}" {LAT}>···</text>'
    s += f'<text x="{pts[-1][0] + 26:.0f}" y="{pts[-1][1] + 6:.0f}" font-size="26" fill="{INK}" {LAT}>···</text>'
    save(P + 'chain.svg', svg(760, 180, s))

    # 10) تغير الخواص الطبيعية: بروتين مطوي ← تسخين ← سلسلة منبسطة
    s = ''
    d = 'M60,120 C40,60 120,40 130,90 S70,150 110,170 S200,150 170,110 S110,60 160,50 S230,70 210,130 S150,190 200,200'
    s += f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="6" stroke-linecap="round"/>'
    s += ARROW(260, 125, 380, 125, INK, 3) + T(320, 110, 'تسخين', 18, weight='bold')
    pts = ' '.join(f'{410 + i * 6},{125 + 14 * math.sin(i * 0.55):.1f}' for i in range(52))
    s += f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="6" stroke-linecap="round"/>'
    save(P + 'denature.svg', svg(740, 240, s))

    # 11) الشكل الحلزوني (1) والصحيفة المطوية (2)
    s = ''
    back, front = [], []
    for i in range(0, 241):
        t = i / 240 * 5 * 2 * math.pi
        x = 50 + i * 1.1 + 22 * math.sin(t); y = 120 + 45 * math.cos(t)
        (front if math.sin(t) > -0.05 and math.cos(t) > -1.1 and math.sin(t) >= 0 else back).append((x, y))
    pts = [(50 + i * 1.1 + 22 * math.sin(i / 240 * 10 * math.pi), 120 + 45 * math.cos(i / 240 * 10 * math.pi)) for i in range(241)]
    s += '<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" stroke="{RED}" stroke-width="5" stroke-linejoin="round"/>'
    for k in range(4):
        x = 50 + (k * 48 + 24) * 1.1 + 10
        s += L(x, 82, x + 6, 160, MUTED, 1.6, '4 3')
    s += caption(185, 215, '(1)', 22)
    for j in range(3):
        y0 = 70 + j * 55
        zz = ' '.join(f'{400 + i * 24},{y0 + (10 if i % 2 else -10)}' for i in range(12))
        s += f'<polyline points="{zz}" fill="none" stroke="#8a5a00" stroke-width="5" stroke-linejoin="round"/>'
        s += ARROW(400 + 11 * 24, y0 + 10, 400 + 11 * 24 + 22, y0, '#8a5a00', 4) if j != 1 else ARROW(400, y0 - 10, 380, y0, '#8a5a00', 4)
        if j < 2:
            for i in range(1, 12, 2):
                s += L(400 + i * 24, y0 + 14, 400 + i * 24, y0 + 55 - 14, MUTED, 1.6, '4 3')
    s += caption(540, 215, '(2)', 22)
    save(P + 'helix-sheet.svg', svg(720, 235, s))

    # 12) عمل الإنزيم: X الموقع النشط، Y المادة الخاضعة، Z المعقد
    def enzyme(ox, oy, closed=0):
        nx = 30 - closed * 6
        return (f'<path d="M{ox - 90},{oy} C{ox - 95},{oy + 70} {ox + 95},{oy + 70} {ox + 90},{oy} '
                f'L{ox + 55},{oy - 10} L{ox + nx},{oy - 10} L{ox + nx - 8},{oy + 28} L{ox - nx + 8},{oy + 28} L{ox - nx},{oy - 10} '
                f'L{ox - 55},{oy - 10} Z" fill="#e3c08a" stroke="{INK}" stroke-width="2.2"/>')
    def substrate(ox, oy, split=0):
        a = f'<path d="M{ox - 22 - split},{oy} L{ox - 30 - split},{oy - 38} L{ox - 1 - split},{oy - 38} L{ox - 1 - split},{oy} Z" fill="#7fb3d9" stroke="{INK}" stroke-width="2"/>'
        b = f'<path d="M{ox + 1 + split},{oy} L{ox + 1 + split},{oy - 38} L{ox + 30 + split},{oy - 38} L{ox + 22 + split},{oy} Z" fill="#7fb3d9" stroke="{INK}" stroke-width="2"/>'
        return a + b
    s = ''
    s += enzyme(130, 170) + substrate(130, 90)
    s += ARROW(250, 150, 320, 150, INK, 3)
    s += enzyme(440, 170, 1) + substrate(440, 198)
    s += ARROW(560, 150, 630, 150, INK, 3)
    s += enzyme(750, 170) + substrate(750, 80, 22)
    s += L(130, 175, 60, 215, MUTED, 1.5) + tag(48, 222, 'X', INK)
    s += L(160, 72, 205, 50, MUTED, 1.5) + tag(220, 44, 'Y', INK)
    s += f'<path d="M365,250 Q440,275 515,250" fill="none" stroke="{MUTED}" stroke-width="1.5"/>' + tag(440, 280, 'Z', INK)
    save(P + 'enzyme.svg', svg(880, 310, s))

if __name__ == '__main__':
    main()
