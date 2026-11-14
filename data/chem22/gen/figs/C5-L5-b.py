# رسوم الدرس 5-5 (ب) — البوليمرات: إعادة التدوير ورموزها، ورسم البوليمر من المونومر والعكس، وتوقع الخواص، والخط الزمني.
# التشغيل: python3 data/chem22/gen/figs/C5-L5-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('c5l5a', os.path.join(os.path.dirname(__file__), 'C5-L5-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
ftext, tw, cw, hbond, vbond, benzene, sub, chain, rarrow = A.ftext, A.tw, A.cw, A.hbond, A.vbond, A.benzene, A.sub, A.chain, A.rarrow
SZ = A.SZ

P = 'c5-l5b-'

def chain(x0, yc, groups, orders=None, size=SZ, bl=30, brackets=False, dots=False, n='n', pre=''):
    """نسخة من chain في C5-L5-a مع إزاحة القوس الأيمن حتى لا يتقاطع مع مجموعة فرعية طويلة."""
    s = ''; x = x0; ext_top = yc - size * 0.6; ext_bot = yc + size * 0.6; sub_right = 0
    orders = orders or [1] * (len(groups) - 1)
    if pre:
        s += ftext(x, yc, pre, size); x += tw(pre, size) + 6
    if dots:
        s += ftext(x, yc, '···', size); x += tw('···', size) + 4
        s += hbond(x, x + bl, yc); x += bl + 4
    if brackets:
        lb = x + 14; s += hbond(x, x + bl + 4, yc); x += bl + 8
    for k, (lab, specs) in enumerate(groups):
        w = tw(lab, size)
        s += ftext(x, yc, lab, size)
        ax = x + cw(lab[0], size) / 2
        for sp in specs:
            t, end = sub(ax, yc, sp, size); s += t
            ext = end + (size * 0.6 if sp[0] > 0 else -size * 0.6)
            if sp[1] == 'ring': ext = end + (6 if sp[0] > 0 else -6)
            if sp[1] == 'text': sub_right = max(sub_right, ax - cw(sp[2][0], size) / 2 + tw(sp[2], size))
            ext_top = min(ext_top, ext); ext_bot = max(ext_bot, ext)
        x += w
        if k < len(groups) - 1:
            s += hbond(x + 4, x + 4 + bl, yc, orders[k]); x += bl + 8
    if brackets:
        rb = max(x + bl - 10, sub_right + 10)
        s += hbond(x + 4, rb + 14, yc)
        top, bot = ext_top - 6, ext_bot + 6
        s += f'<path d="M{lb + 8},{top} L{lb},{top} L{lb},{bot} L{lb + 8},{bot}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
        s += f'<path d="M{rb - 8},{top} L{rb},{top} L{rb},{bot} L{rb - 8},{bot}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
        s += f'<text x="{rb + 5}" y="{bot + 4}" font-size="{size * 0.8:.0f}" fill="{INK}" font-family="Times New Roman,serif" font-style="italic" font-weight="bold">{n}</text>'
        x = rb + 22
    if dots:
        s += hbond(x + 4, x + 4 + bl, yc); x += bl + 8
        s += ftext(x, yc, '···', size); x += tw('···', size)
    return s, x, ext_top, ext_bot

def fig(name, parts, w, h):
    save(name, svg(int(w), int(h), parts))

# ---------- سلسلة تسمح بحلقة بنزين داخل السلسلة الرئيسة ----------
def chain_ring(x0, yc, groups, bl=26, size=SZ, n='n'):
    """مثل chain مع أقواس دائمًا؛ المجموعة 'RING' تُرسم حلقة بنزين أفقية."""
    s = ''; x = x0; top = yc - size * 0.6; bot = yc + size * 0.6; r = 28
    lb = x + 14; s += hbond(x, x + bl + 4, yc); x += bl + 8
    for k, (lab, specs) in enumerate(groups):
        if lab == 'RING':
            cx = x + r * math.cos(math.radians(30)) - 4
            pts = [(cx + r * math.cos(math.radians(60 * j)), yc + r * math.sin(math.radians(60 * j))) for j in range(6)]
            s += f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
            s += f'<circle cx="{cx:.1f}" cy="{yc}" r="{r * 0.58:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
            # الحلقة تبدأ من رأسها الأيسر (cx - r) وتنتهي برأسها الأيمن (cx + r)
            x = cx + r - 4
            top = min(top, yc - r - 4); bot = max(bot, yc + r + 4)
        else:
            s += ftext(x, yc, lab, size)
            ax = x + cw(lab[0], size) / 2
            for sp in specs:
                t, end = sub(ax, yc, sp, size); s += t
                ext = end + (size * 0.6 if sp[0] > 0 else -size * 0.6)
                top = min(top, ext); bot = max(bot, ext)
            x += tw(lab, size)
        if k < len(groups) - 1:
            nxt = groups[k + 1][0]
            gap_end = bl - (4 if nxt == 'RING' else 0)
            s += hbond(x + 4, x + 4 + gap_end, yc); x += gap_end + 8
    s += hbond(x + 4, x + 4 + bl + 4, yc); rb = x + bl - 10
    t2, b2 = top - 6, bot + 6
    s += f'<path d="M{lb + 8},{t2} L{lb},{t2} L{lb},{b2} L{lb + 8},{b2}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    s += f'<path d="M{rb - 8},{t2} L{rb},{t2} L{rb},{b2} L{rb - 8},{b2}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    s += f'<text x="{rb + 5}" y="{b2 + 4}" font-size="{size * 0.8:.0f}" fill="{INK}" font-family="Times New Roman,serif" font-style="italic" font-weight="bold">{n}</text>'
    return s, x + bl + 12, t2, b2

# ---------- رمز إعادة التدوير ----------
def rsym(cx, cy, num, abbr=None, side=78, color=GREEN):
    R = side / math.sqrt(3)
    V = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    s = ''
    for i in range(3):
        (x1, y1), (x2, y2) = V[i], V[(i + 1) % 3]
        a1, a2 = 0.16, 0.80
        p = (x1 + (x2 - x1) * a1, y1 + (y2 - y1) * a1); q = (x1 + (x2 - x1) * a2, y1 + (y2 - y1) * a2)
        s += ARROW(round(p[0], 1), round(p[1], 1), round(q[0], 1), round(q[1], 1), color, 5)
    s += f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" font-size="26" fill="{INK}" font-family="Arial,Helvetica,sans-serif" font-weight="bold">{num}</text>'
    if abbr:
        s += f'<text x="{cx}" y="{cy + R / 2 + 32}" text-anchor="middle" font-size="20" fill="{INK}" font-family="Arial,Helvetica,sans-serif" font-weight="bold">{abbr}</text>'
    return s

def box(cx, cy, label, w=150, h=50, fill='#eef3fa', stroke=BLUE):
    return (f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            + T(cx, cy + 6, label, 16, weight='bold'))

def timeline(name, items, w=760):
    """items = [(السنة، الحرف)] مرتبة زمنيًا؛ الخط من اليمين (الأقدم) إلى اليسار (الأحدث) كما في الكتاب."""
    y = 80; x_r = w - 60; x_l = 60
    s = L(x_l, y, x_r, y, BLUE, 6)
    s += ARROW(x_l + 30, y, x_l - 20, y, BLUE, 6)
    k = len(items)
    for i, (yr, let) in enumerate(items):
        x = x_r - 40 - i * (x_r - x_l - 80) / (k - 1)
        s += f'<circle cx="{x:.1f}" cy="{y}" r="9" fill="{RED}" stroke="#fff" stroke-width="2"/>'
        s += f'<text x="{x:.1f}" y="{y - 22}" text-anchor="middle" font-size="22" fill="{INK}" font-family="Arial,Helvetica,sans-serif" font-weight="bold">{yr}</text>'
        s += L(x, y + 10, x, y + 40, MUTED, 2)
        s += f'<rect x="{x - 34:.1f}" y="{y + 40}" width="68" height="40" rx="8" fill="#fff7e6" stroke="{RED}" stroke-width="2"/>'
        s += T(round(x, 1), y + 68, let, 20, weight='bold')
    s += T(w - 40, 30, 'الأقدم', 15, color=MUTED) + T(60, 30, 'الأحدث', 15, color=MUTED)
    fig(name, s, w, 185)

def lab(x, y, s): return T(x, y, s, 18, weight='bold')

def main():
    os.makedirs(OUT, exist_ok=True)

    # 1) دورة حياة المنتج البلاستيكي وإعادة تدويره
    xs = [740, 540, 340, 130]; y1 = 60; y2 = 220
    s = ''
    names = ['(1) الوقود الأحفوري', '(2) المواد الأولية', '(3) تصنيع البوليمر', '(4) المنتج البلاستيكي']
    for x, nme in zip(xs, names): s += box(x, y1, nme, 165)
    for i in range(3): s += ARROW(xs[i] - 84, y1, xs[i + 1] + 86, y1)
    b2 = [(130, '(5) النفايات البلاستيكية'), (360, '(6) الفرز'), (560, '(7) إعادة التدوير')]
    for x, nme in b2: s += box(x, y2, nme, 175 if x == 130 else 150, fill='#eef8f1', stroke=GREEN)
    s += ARROW(130, y1 + 26, 130, y2 - 27)
    s += ARROW(219, y2, 283, y2) + ARROW(437, y2, 483, y2)
    s += f'<path d="M560,{y2 - 26} L560,{(y1 + y2) / 2} L175,{(y1 + y2) / 2} L175,{y1 + 32}" fill="none" stroke="{GREEN}" stroke-width="3" stroke-dasharray="8 5"/>'
    s += f'<polygon points="175,{y1 + 26} 169,{y1 + 38} 181,{y1 + 38}" fill="{GREEN}"/>'
    fig(P + 'recycle-cycle.svg', s, 840, 260)

    # 2) رموز إعادة التدوير
    fig(P + 'code-1.svg', rsym(90, 75, '1', 'PETE'), 180, 160)
    fig(P + 'code-5.svg', rsym(90, 75, '5', 'PP'), 180, 160)
    fig(P + 'codes-2-4.svg', rsym(260, 75, '2', 'HDPE') + lab(330, 40, '(أ)') + rsym(90, 75, '4', 'LDPE') + lab(160, 40, '(ب)'), 360, 160)
    s = rsym(430, 75, '2', 'HDPE') + lab(500, 40, '(أ)') + rsym(260, 75, '3', 'V') + lab(330, 40, '(ب)') + rsym(90, 75, '6', 'PS') + lab(160, 40, '(ج)')
    fig(P + 'codes-2-3-6.svg', s, 530, 160)
    b, xe, top, bot = chain(30, 45, [('CH2', []), ('CH', [(1, 'text', 'Cl')])], brackets=True)
    fig(P + 'pvc.svg', b, xe + 30, bot + 30)

    # 3) رسم البوليمر من المونومر والعكس
    b, xe, _, bot = chain(20, 50, [('CF2', []), ('CF2', [])], [2], pre='n')
    b += rarrow(xe + 18, 50) + ftext(xe + 105, 50, '?', 30)
    fig(P + 'tfe.svg', b, xe + 140, 100)
    b, xe, _, bot = chain(20, 45, [('CH2', []), ('CH', [(1, 'ring', '')])], [2], pre='n')
    b += rarrow(xe + 18, 45) + ftext(xe + 105, 45, '?', 30)
    fig(P + 'styrene.svg', b, xe + 140, bot + 20)
    b, xe, top, bot = chain(30, 110, [('CH2', []), ('C', [(-1, 'text', 'COOCH3'), (1, 'text', 'CH3')])], brackets=True)
    fig(P + 'pmma.svg', b, xe + 100, bot + 25)
    b, xe, top, bot = chain_ring(20, 75, [('O', []), ('C', [(-1, 'text', 'O', 2)]), ('RING', []), ('C', [(-1, 'text', 'O', 2)]),
                                          ('O', []), ('CH2', []), ('CH2', [])])
    fig(P + 'pete.svg', b, xe + 25, bot + 25)
    b, xe, top, bot = chain(20, 45, [('CH2', []), ('CH', [(1, 'text', 'Br')]), ('CH2', []), ('CH', [(1, 'text', 'Br')]),
                                     ('CH2', []), ('CH', [(1, 'text', 'Br')])], dots=True)
    fig(P + 'pvbr-chain.svg', b, xe + 20, bot + 25)
    b, xe, top, bot = chain(20, 90, [('HO', []), ('CH2', []), ('CH2', []), ('C', [(-1, 'text', 'O', 2)]), ('OH', [])], bl=28)
    fig(P + 'hydroxyacid.svg', b, xe + 20, 125)
    b, xe, top, bot = chain(20, 90, [('H2N', []), ('(CH2)5', []), ('C', [(-1, 'text', 'O', 2)]), ('OH', [])], bl=28)
    fig(P + 'aminoacid.svg', b, xe + 20, 125)
    b, xe, _, _ = chain(70, 45, [('CH2', []), ('CHF', [])], [2])
    b += lab(35, 52, '(a)')
    b2, xe2, _, bot = chain(70, 165, [('CH2', []), ('C', [(-1, 'text', 'CH3'), (1, 'text', 'CH3')])], [2])
    b2 += lab(35, 172, '(b)')
    fig(P + 'monomers-e1.svg', b + b2, max(xe, xe2) + 40, bot + 25)
    # الوحدتان (I) و(II)
    b, xe, _, bot1 = chain(70, 50, [('CH2', []), ('CF2', [])], brackets=True)
    b += lab(35, 57, '(I)')
    b2, xe2, _, bot = chain(70, 190, [('NH', []), ('(CH2)6', []), ('NH', []), ('C', [(-1, 'text', 'O', 2)]), ('(CH2)8', []),
                                      ('C', [(-1, 'text', 'O', 2)])], bl=22, brackets=True)
    b2 += lab(35, 197, '(II)')
    fig(P + 'units-e2.svg', b + b2, max(xe, xe2) + 25, bot + 25)

    # 4) توقع الخواص
    b, xe, _, _ = chain(70, 45, [('CH2', []), ('CH', [(1, 'text', 'CH3')])], brackets=True)
    b += lab(35, 52, '(I)')
    b2, xe2, _, bot = chain(70, 190, [('CH2', []), ('CH', [(1, 'text', 'COOH')])], brackets=True)
    b2 += lab(35, 197, '(II)')
    fig(P + 'pp-vs-cooh.svg', b + b2, max(xe, xe2) + 40, bot + 25)
    s = ''; xe_max = 0; ys = [45, 190, 335]; bot = 0
    units = [[('CH2', []), ('CH2', [])], [('CH2', []), ('CH', [(1, 'text', 'OCH3')])], [('CH2', []), ('CH', [(1, 'text', 'OH')])]]
    for lb_, y, u in zip(['(A)', '(B)', '(C)'], ys, units):
        b, xe, _, bt = chain(70, y, u, brackets=True); s += b + lab(35, y + 7, lb_); xe_max = max(xe_max, xe); bot = bt
    fig(P + 'three-polymers.svg', s, xe_max + 60, bot + 25)
    b, xe, top, bot = chain(30, 100, [('C', [(-1, 'text', 'F'), (1, 'text', 'F')]), ('C', [(-1, 'text', 'F'), (1, 'text', 'F')])], brackets=True)
    fig(P + 'ptfe.svg', b, xe + 30, bot + 25)
    # ثلاثة بوليمرات للسؤال المقالي
    s = ''
    b, xe1, _, _ = chain(70, 100, [('C', [(-1, 'text', 'F'), (1, 'text', 'F')]), ('C', [(-1, 'text', 'F'), (1, 'text', 'F')])], brackets=True)
    s += b + lab(35, 107, '(أ)')
    b, xe2, _, _ = chain(70, 260, [('CH2', []), ('CH', [(1, 'text', 'COOH')])], brackets=True)
    s += b + lab(35, 267, '(ب)')
    b, xe3, _, bot = chain(70, 450, [('NH', []), ('(CH2)6', []), ('NH', []), ('C', [(-1, 'text', 'O', 2)]), ('(CH2)4', []),
                                     ('C', [(-1, 'text', 'O', 2)])], bl=22, brackets=True)
    s += b + lab(35, 457, '(ج)')
    fig(P + 'three-b.svg', s, max(xe1, xe2, xe3) + 25, bot + 25)

    # 5) الخط الزمني
    timeline(P + 'timeline.svg', [('1909', '(أ)'), ('1931', '(ب)'), ('1946', '(ج)'), ('1988', '(د)')])
    timeline(P + 'timeline-2.svg', [('1909', '(أ)'), ('1939–1945', '(ب)'), ('1959', '(ج)'), ('2006', '(د)')])

if __name__ == '__main__':
    main()
