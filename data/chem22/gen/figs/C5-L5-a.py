# رسوم الدرس 5-5 (أ) — البوليمرات: وحدات بنائية متكررة بين قوسين مع n، ومعادلات بلمرة بالإضافة والتكثف، ونماذج الخرز للمونومرات.
# التشغيل: python3 data/chem22/gen/figs/C5-L5-a.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

P = 'c5-l5a-'
SZ = 22
LAT = 'font-family="Arial,Helvetica,sans-serif" font-weight="bold"'

def cw(ch, size):
    if ch.isdigit(): return 0.556 * size * 0.72
    if ch in '()': return 0.333 * size
    if ch == ' ': return 0.28 * size
    if ch.isupper(): return 0.72 * size
    return 0.56 * size

def tw(s, size=SZ):
    w = 0; prev = ''
    for ch in s:
        w += cw(ch, size) if (ch.isdigit() and prev and (prev.isalpha() or prev == ')')) or not ch.isdigit() else 0.556 * size
        prev = ch
    return w

def ftext(x, yc, s, size=SZ, anchor='start', color=INK):
    """صيغة كيميائية لاتينية (من اليسار إلى اليمين)، والأرقام بعد الحرف أو القوس تُكتب منخفضة. yc = منتصف السطر."""
    out = ''; i = 0; prev = ''; d = size * 0.28
    while i < len(s):
        ch = s[i]
        if ch.isdigit() and prev and (prev.isalpha() or prev == ')'):
            j = i
            while j < len(s) and s[j].isdigit(): j += 1
            out += f'<tspan dy="{d:.1f}" font-size="{size * 0.72:.1f}">{s[i:j]}</tspan><tspan dy="{-d:.1f}">​</tspan>'
            prev = s[j - 1]; i = j; continue
        out += esc(ch); prev = ch; i += 1
    return f'<text x="{x:.1f}" y="{yc + size * 0.36:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" {LAT}>{out}</text>'

def hbond(x1, x2, y, order=1, color=INK):
    offs = {1: [0], 2: [-3.5, 3.5], 3: [-6, 0, 6]}[order]
    return ''.join(L(f'{x1:.1f}', f'{y + o:.1f}', f'{x2:.1f}', f'{y + o:.1f}', color, 2.4) for o in offs)

def vbond(x, y1, y2, order=1, color=INK):
    offs = {1: [0], 2: [-3.5, 3.5], 3: [-6, 0, 6]}[order]
    return ''.join(L(f'{x + o:.1f}', f'{y1:.1f}', f'{x + o:.1f}', f'{y2:.1f}', color, 2.4) for o in offs)

def benzene(cx, cy, r=30):
    pts = [(cx + r * math.cos(math.radians(90 + 60 * k)), cy - r * math.sin(math.radians(90 + 60 * k))) for k in range(6)]
    s = f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    return s + f'<circle cx="{cx}" cy="{cy}" r="{r * 0.58:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>'

def sub(ax, yc, spec, size=SZ):
    """مجموعة فرعية رأسية: spec = (dir, kind, label, order) — dir: 1 أسفل، −1 أعلى."""
    d, kind, lab = spec[0], spec[1], spec[2]
    order = spec[3] if len(spec) > 3 else 1
    h = size * 0.55; gap = 40
    if kind == 'text':
        cy = yc + d * (h + gap + h)
        first = cw(lab[0], size)
        s = vbond(ax, yc + d * (h + 2), cy - d * (h - 2), order)
        return s + ftext(ax - first / 2, cy, lab, size), cy
    if kind == 'cn':  # C≡N رأسية
        c1 = yc + d * (2 * h + gap); c2 = c1 + d * (2 * h + gap - 6)
        s = vbond(ax, yc + d * (h + 2), c1 - d * (h - 2)) + ftext(ax, c1, 'C', size, 'middle')
        s += vbond(ax, c1 + d * (h + 2), c2 - d * (h - 2), 3) + ftext(ax, c2, 'N', size, 'middle')
        return s, c2
    if kind == 'ring':
        r = 30; top = yc + d * (h + 30); cy = top + d * r
        return vbond(ax, yc + d * (h + 2), top) + benzene(ax, cy, r), cy + d * r
    raise ValueError(kind)

def chain(x0, yc, groups, orders=None, size=SZ, bl=30, brackets=False, dots=False, n='n', pre=''):
    """سلسلة أفقية من مجموعات: groups = [(label, [specs])]. orders: رتب الروابط بين المجموعات.
    brackets: قوسان حول الوحدة مع n، والروابط الطرفية تعبر القوسين. dots: نقاط في الطرفين. pre: معامل قبل الصيغة."""
    s = ''; x = x0; ext_top = yc - size * 0.6; ext_bot = yc + size * 0.6
    orders = orders or [1] * (len(groups) - 1)
    if pre:
        s += ftext(x, yc, pre, size); x += tw(pre, size) + 6
    if dots:
        s += ftext(x, yc, '···', size); x += tw('···', size) + 4
        s += hbond(x, x + bl, yc); x += bl + 4
    if brackets:
        lb = x + 14; s += hbond(x, x + bl + 4, yc); x += bl + 8
    subs_draw = []
    for k, (lab, specs) in enumerate(groups):
        w = tw(lab, size)
        s += ftext(x, yc, lab, size)
        ax = x + cw(lab[0], size) / 2
        for sp in specs:
            t, end = sub(ax, yc, sp, size); s += t
            ext = end + (size * 0.6 if sp[0] > 0 else -size * 0.6)
            if sp[1] == 'ring': ext = end + (6 if sp[0] > 0 else -6)
            ext_top = min(ext_top, ext); ext_bot = max(ext_bot, ext)
        x += w
        if k < len(groups) - 1:
            s += hbond(x + 4, x + 4 + bl, yc, orders[k]); x += bl + 8
    if brackets:
        s += hbond(x + 4, x + 4 + bl + 4, yc); rb = x + bl - 10
        top, bot = ext_top - 6, ext_bot + 6
        s += f'<path d="M{lb + 8},{top} L{lb},{top} L{lb},{bot} L{lb + 8},{bot}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
        s += f'<path d="M{rb - 8},{top} L{rb},{top} L{rb},{bot} L{rb - 8},{bot}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
        s += f'<text x="{rb + 5}" y="{bot + 4}" font-size="{size * 0.8:.0f}" fill="{INK}" font-family="Times New Roman,serif" font-style="italic" font-weight="bold">{n}</text>'
        x += bl + 12
    if dots:
        s += hbond(x + 4, x + 4 + bl, yc); x += bl + 8
        s += ftext(x, yc, '···', size); x += tw('···', size)
    return s, x, ext_top, ext_bot

def rarrow(x, yc, l=70): return ARROW(x, yc, x + l, yc, INK, 2.5)

def fig(name, parts, w, h):
    save(name, svg(w, h, parts))

# ---------- الوحدات البنائية ----------
def unit_fig(name, groups, yc=70, w=None, h=None, orders=None):
    b, xe, top, bot = chain(30, yc, groups, orders, brackets=True)
    W = w or int(xe + 30); H = h or int(bot + 30)
    fig(name, b, W, H)

def main():
    os.makedirs(OUT, exist_ok=True)
    unit_fig(P + 'pe.svg', [('CH2', []), ('CH2', [])], yc=45)
    unit_fig(P + 'cf2.svg', [('CF2', []), ('CF2', [])], yc=45)
    unit_fig(P + 'pp.svg', [('CH2', []), ('CH', [(1, 'text', 'CH3')])], yc=45)
    unit_fig(P + 'ps.svg', [('CH2', []), ('CH', [(1, 'ring', '')])], yc=45)
    unit_fig(P + 'pan.svg', [('CH2', []), ('CH', [(1, 'cn', '')])], yc=45)
    unit_fig(P + 'pvdc.svg', [('CH2', []), ('C', [(-1, 'text', 'Cl'), (1, 'text', 'Cl')])], yc=100)

    # قطعة من سلسلة PVC بلا أقواس
    b, xe, top, bot = chain(20, 45, [('CH2', []), ('CH', [(1, 'text', 'Cl')]), ('CH2', []), ('CH', [(1, 'text', 'Cl')]),
                                     ('CH2', []), ('CH', [(1, 'text', 'Cl')])], dots=True)
    fig(P + 'pvc-chain.svg', b, int(xe + 20), int(bot + 25))

    # بلمرة الإيثين: n CH2=CH2 → [CH2–CH2]n
    b, xe, _, _ = chain(20, 50, [('CH2', []), ('CH2', [])], [2], pre='n')
    b += rarrow(xe + 18, 50); b2, xe2, top, bot = chain(xe + 100, 50, [('CH2', []), ('CH2', [])], brackets=True)
    fig(P + 'ethene-pe.svg', b + b2, int(xe2 + 20), int(bot + 25))

    # بلمرة الأكريلونيتريل
    b, xe, _, _ = chain(20, 45, [('CH2', []), ('CH', [(1, 'cn', '')])], [2], pre='n')
    b += rarrow(xe + 18, 45); b2, xe2, top, bot = chain(xe + 100, 45, [('CH2', []), ('CH', [(1, 'cn', '')])], brackets=True)
    fig(P + 'pan-eq.svg', b + b2, int(xe2 + 20), int(bot + 25))

    # نايلون 6,6 (سطران)
    r1 = ftext(20, 40, 'nHOOC–(CH2)4–COOH  +  nH2N–(CH2)6–NH2', 22)
    y2 = 145
    b = rarrow(20, y2, 60)
    b2, xe, top, bot = chain(95, y2, [('C', [(-1, 'text', 'O', 2)]), ('(CH2)4', []), ('C', [(-1, 'text', 'O', 2)]), ('NH', []),
                                      ('(CH2)6', []), ('NH', [])], bl=22, brackets=True)
    b2 += ftext(xe + 8, y2, '+  2nH2O', 22)
    fig(P + 'nylon66.svg', r1 + b + b2, int(xe + 130), int(bot + 25))

    # مونومران: (I) CH2=CHCl و(II) H2N–CH2–CH2–C(=O)–OH
    b, xe, _, bot1 = chain(70, 50, [('CH2', []), ('CH', [(1, 'text', 'Cl')])], [2])
    b += T(30, 57, '(I)', 18, weight='bold')
    b2, xe2, _, bot2 = chain(70, 230, [('H2N', []), ('CH2', []), ('CH2', []), ('C', [(-1, 'text', 'O', 2)]), ('OH', [])], bl=26)
    b2 += T(30, 237, '(II)', 18, weight='bold')
    fig(P + 'monomers-1-2.svg', b + b2, int(max(xe, xe2) + 25), 270)

    # مونومرا السؤال المقالي: (a) CHCl=CHCl و(b) H2N–CH2CH2–C(=O)–OH
    b, xe, _, _ = chain(70, 45, [('CH', [(1, 'text', 'Cl')]), ('CH', [(1, 'text', 'Cl')])], [2])
    b += T(30, 52, '(a)', 18, weight='bold')
    b2, xe2, _, _ = chain(70, 225, [('H2N', []), ('CH2CH2', []), ('C', [(-1, 'text', 'O', 2)]), ('OH', [])], bl=26)
    b2 += T(30, 232, '(b)', 18, weight='bold')
    fig(P + 'monomers-a-b.svg', b + b2, int(max(xe, xe2) + 25), 265)

    # بوليمران للمقارنة: (I) [CH2–CH2]n و(II) [CH2–CH(OH)]n
    b, xe, _, _ = chain(70, 45, [('CH2', []), ('CH2', [])], brackets=True)
    b += T(30, 52, '(I)', 18, weight='bold')
    b2, xe2, _, bot = chain(70, 160, [('CH2', []), ('CH', [(1, 'text', 'OH')])], brackets=True)
    b2 += T(30, 167, '(II)', 18, weight='bold')
    fig(P + 'pe-vs-oh.svg', b + b2, int(max(xe, xe2) + 25), int(bot + 25))

    # (أ) PP و(ب) PVC
    b, xe, _, _ = chain(70, 45, [('CH2', []), ('CH', [(1, 'text', 'CH3')])], brackets=True)
    b += T(32, 52, '(أ)', 18, weight='bold')
    b2, xe2, _, bot = chain(70, 185, [('CH2', []), ('CH', [(1, 'text', 'Cl')])], brackets=True)
    b2 += T(32, 192, '(ب)', 18, weight='bold')
    fig(P + 'pp-pvc.svg', b + b2, int(max(xe, xe2) + 25), int(bot + 25))

    # نموذج الخرز: مونومرات منفصلة ← سلسلة طويلة
    RED_ = '#c0392b'; GREY = '#7f8a99'
    def bead(x, y, c, r=11):
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="#333" stroke-width="1.2"/>'
    b = ''
    import random
    random.seed(4)
    for k in range(12):
        b += bead(30 + (k % 4) * 34 + random.randint(-5, 5), 50 + (k // 4) * 40 + random.randint(-5, 5), RED_)
    b += ARROW(175, 90, 245, 90)
    pts = [(270 + 26 * i, 90 + (12 if i % 2 else -12) * 0) for i in range(12)]
    pts = []
    for i in range(14):
        x = 270 + 25 * (i if i < 7 else 13 - i) ; y = 60 if i < 7 else 120
        pts.append((x, y))
    path = ' '.join(f'{x},{y}' for x, y in pts[:7]) + f' {pts[6][0] + 18},{90} ' + ' '.join(f'{x},{y}' for x, y in pts[7:])
    b += f'<polyline points="{path}" fill="none" stroke="#333" stroke-width="3"/>'
    for x, y in pts: b += bead(x, y, RED_)
    b += bead(pts[6][0] + 18, 90, RED_)
    fig(P + 'beads.svg', b, 470, 165)

    # نموذج الخرز لثلاث سلاسل: (أ) من المونومر الأول، (ب) من الثاني، (ج) من الاثنين بالتناوب
    b = ''
    rows = [('(أ)', [RED_] * 10), ('(ب)', [GREY] * 10), ('(ج)', [RED_, GREY] * 5)]
    for r, (lab, cols) in enumerate(rows):
        y = 40 + r * 55
        b += T(40, y + 6, lab, 18, weight='bold')
        b += L(80, y, 80 + 30 * 9, y, '#333', 3)
        for i, c in enumerate(cols): b += bead(80 + 30 * i, y, c)
    yl = 40 + 3 * 55
    b += bead(420, yl - 2, RED_) + T(405, yl + 4, 'المونومر الأول', 15, 'end')
    b += bead(225, yl - 2, GREY) + T(210, yl + 4, 'المونومر الثاني', 15, 'end')
    fig(P + 'beads-three.svg', b, 450, yl + 25)

if __name__ == '__main__':
    main()
