# رسوم الدرس 4-5 (الهيدروكربونات الأروماتية): حلقة البنزين، مشتقاته، الحلقات الملتحمة، ومركبات أليفاتية للمقارنة.
# التشغيل: python3 data/chem22/gen/figs/C4-L5-a.py
import sys, os, math, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

P = 'c4-l5a-'
R = 46                     # طول الرابطة (ضلع السداسي) ≥ 40 px
LATIN = "font-family=\"Arial,'DejaVu Sans',sans-serif\""

def chem(x, y, s, size=17, anchor='middle', color=INK):
    """نص كيميائي لاتيني (LTR): الأرقام بعد الحروف تُكتب منخفضة."""
    out = ''
    for tok in re.findall(r'[A-Za-z()=\-−]+|\d+', s):
        if tok.isdigit(): out += f'<tspan font-size="{size * 0.68:.0f}" dy="4">{tok}</tspan><tspan dy="-4"></tspan>'
        else: out += esc(tok)
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" {LATIN} direction="ltr">{out}</text>'

def verts(cx, cy, r=R):
    """رؤوس سداسي رأسه للأعلى: 0 أعلى، 1 أعلى يمين، 2 أسفل يمين، 3 أسفل، 4 أسفل يسار، 5 أعلى يسار."""
    return [(cx + r * math.cos(math.radians(-90 + 60 * k)), cy + r * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]

def inner(cx, cy, p, q, f=0.78, sh=0.16):
    """خط داخلي موازٍ للضلع pq (الرابطة الثنائية)."""
    ax, ay = cx + (p[0] - cx) * f, cy + (p[1] - cy) * f
    bx, by = cx + (q[0] - cx) * f, cy + (q[1] - cy) * f
    dx, dy = bx - ax, by - ay
    return L(ax + dx * sh, ay + dy * sh, bx - dx * sh, by - dy * sh, INK, 2.2)

def ring(cx, cy, style='circle', doubles=(), r=R):
    """style: circle (التمثيل الحديث)، kekule (روابط متناوبة)، plain (حلقة مشبعة). doubles: أضلاع ثنائية k بين الرأس k والرأس k+1."""
    v = verts(cx, cy, r)
    b = f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in v)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    if style == 'circle': b += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.58:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
    if style == 'kekule': doubles = (0, 2, 4)
    for k in doubles: b += inner(cx, cy, v[k], v[(k + 1) % 6])
    return b

def sub(cx, cy, k, label, r=R, blen=None, size=17):
    """مجموعة بديلة على الرأس k: رابطة نحو الخارج ثم النص."""
    blen = blen or r * 0.62
    v = verts(cx, cy, r)[k]
    a = math.radians(-90 + 60 * k)
    ex, ey = v[0] + blen * math.cos(a), v[1] + blen * math.sin(a)
    b = L(v[0], v[1], ex, ey, INK, 2.4)
    c = math.cos(a)
    LEFT = {'CH3': 'H3C', 'CH2CH3': 'CH3CH2', 'CH2CH2CH3': 'CH3CH2CH2'}
    if c < -0.1: label = LEFT.get(label, label)
    if abs(c) < 0.1:      # أعلى/أسفل: ذرة C الأولى فوق الرابطة
        yy = ey - 6 if k == 0 else ey + 17
        b += chem(ex, yy, label, size) if len(label) <= 3 else chem(ex - 6, yy, label, size, 'start')
    elif c > 0:
        b += chem(ex + 3, ey + 6 + (4 if k == 2 else -2), label, size, 'start')
    else:
        b += chem(ex - 3, ey + 6 + (4 if k == 4 else -2), label, size, 'end')
    return b

def nums(cx, cy, order, r=R):
    """ترقيم ذرات الحلقة: order[i] = رقم الرأس i (أو None)."""
    b = ''
    for k in range(6):
        a = math.radians(-90 + 60 * k + 22)
        x, y = cx + r * 1.22 * math.cos(a), cy + r * 1.22 * math.sin(a)
        if order[k]: b += T(x, y + 5, str(order[k]), 14, color=RED, weight='bold')
    return b

def hydrogens(cx, cy, r=R):
    b = ''
    for k in range(6): b += sub(cx, cy, k, 'H', r, blen=r * 0.5)
    return b

def tag(x, y, s): return T(x, y, s, 16, weight='bold', color=BLUE)

def single(name, items, w=300, h=260, cx=None, cy=None, style='circle', numbers=None, extra=''):
    cx = cx or w / 2; cy = cy or h / 2
    b = ring(cx, cy, style)
    for k, lab in items: b += sub(cx, cy, k, lab)
    if numbers: b += nums(cx, cy, numbers)
    save(P + name, svg(w, h, b + extra))

def fused(name, centers, w, h, dx=0, dy=0, label=None):
    d = R * math.sqrt(3)
    b = ''
    for i, j in centers:  # إحداثيات شبكية: i على المحور الأفقي، j بزاوية −60°
        x = dx + i * d + j * d / 2; y = dy - j * d * math.sqrt(3) / 2
        b += ring(x, y, 'circle')
    if label: b += T(w / 2, h - 12, label, 15, rtl=True)
    save(P + name, svg(w, h, b))

def zigzag(x0, y0, n, step=40, amp=24, doubles=()):
    pts = [(x0 + i * step, y0 + (0 if i % 2 == 0 else -amp)) for i in range(n)]
    b = f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    for k in doubles:
        (ax, ay), (bx, by) = pts[k], pts[k + 1]
        nx, ny = -(by - ay), (bx - ax); ln = math.hypot(nx, ny); nx, ny = nx / ln * 6, ny / ln * 6
        if ny < 0: nx, ny = -nx, -ny
        b += L(ax + nx + (bx - ax) * 0.12, ay + ny + (by - ay) * 0.12, bx + nx - (bx - ax) * 0.12, by + ny - (by - ay) * 0.12, INK, 2.2)
    return b

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # --- البنزين ---
    save(P + 'kekule-h.svg', svg(280, 280, ring(140, 140, 'kekule') + hydrogens(140, 140)))
    save(P + 'benzene-circle.svg', svg(220, 200, ring(110, 100, 'circle')))
    save(P + 'kekule.svg', svg(220, 200, ring(110, 100, 'kekule')))
    # تمثيلان للبنزين جنبًا إلى جنب: (1) كيكولي (2) الدائرة
    save(P + 'two-reps.svg', svg(460, 240, ring(120, 115, 'kekule') + hydrogens(120, 115) + ring(340, 115, 'circle')
         + tag(120, 228, '(1)') + tag(340, 228, '(2)')))
    # أربع حلقات سداسية: (1) هكسان حلقي (2) هكسين حلقي (3) بنزين (4) 1،3-هكسادايين حلقي
    b = ''
    for i, (st, db) in enumerate([('plain', ()), ('plain', (0,)), ('circle', ()), ('plain', (0, 2))]):
        x = 75 + i * 150
        b += ring(x, 90, st, db) + tag(x, 175, f'({i + 1})')
    save(P + 'four-rings.svg', svg(600, 195, b))
    # أربعة مركبات للتصنيف: (1) هكسان حلقي (2) إيثيل بنزين (3) هكسان (4) 1-هكسين
    b = ring(80, 105, 'plain') + tag(80, 215, '(1)')
    b += ring(225, 115, 'circle') + sub(225, 115, 1, 'CH2CH3') + tag(245, 215, '(2)')
    b += zigzag(370, 120, 6, 32, 22) + tag(450, 215, '(3)')
    b += zigzag(560, 120, 6, 32, 22, doubles=(0,)) + tag(640, 215, '(4)')
    save(P + 'classify4.svg', svg(740, 235, b))
    # الصيغة المقترحة عام 1860م (سلسلة) مقابل حلقة كيكولي
    # --- مشتقات البنزين المفردة ---
    single('toluene.svg', [(0, 'CH3')], 240, 240, cy=135)
    single('ethylbenzene.svg', [(1, 'CH2CH3')], 320, 220, cx=120, cy=120)
    single('propylbenzene.svg', [(1, 'CH2CH2CH3')], 340, 220, cx=110, cy=120)
    single('p-xylene.svg', [(0, 'CH3'), (3, 'CH3')], 240, 300)
    single('o-xylene.svg', [(0, 'CH3'), (1, 'CH3')], 280, 250, cx=125, cy=140)
    single('m-diethyl.svg', [(0, 'CH2CH3'), (2, 'CH2CH3')], 340, 280, cx=130, cy=145)
    single('o-ethylmethyl.svg', [(0, 'CH3'), (1, 'CH2CH3')], 320, 250, cx=120, cy=140)
    single('p-ethylpropyl.svg', [(0, 'CH2CH2CH3'), (3, 'CH2CH3')], 260, 320)
    single('ethyl-35-dimethyl.svg', [(0, 'CH3'), (2, 'CH3'), (4, 'CH3CH2')], 360, 280, cx=190, cy=140)
    single('124-trimethyl.svg', [(0, 'CH3'), (1, 'CH3'), (3, 'CH3')], 280, 310, cx=125, cy=150)
    single('4-ethyl-12-dimethyl.svg', [(0, 'CH3'), (1, 'CH3'), (3, 'CH2CH3')], 290, 310, cx=125, cy=150)
    single('2-ethyl-13-dimethyl.svg', [(0, 'CH2CH3'), (1, 'CH3'), (5, 'CH3')], 360, 260, cx=170, cy=150)
    single('135-triethyl.svg', [(0, 'CH2CH3'), (2, 'CH2CH3'), (4, 'CH3CH2')], 380, 280, cx=190, cy=140)
    # 1،3-ثنائي بروبيل بنزين مع ترقيمين: (1) صحيح 1و3، (2) 1و5
    def dipropyl(cx, cy, order):
        return ring(cx, cy, 'circle') + sub(cx, cy, 0, 'CH2CH2CH3') + sub(cx, cy, 2, 'CH2CH2CH3') + nums(cx, cy, order)
    save(P + 'dipropyl-two-numberings.svg', svg(620, 280, dipropyl(130, 140, [1, 2, 3, 4, 5, 6]) + dipropyl(430, 140, [5, 6, 1, 2, 3, 4])
         + tag(130, 268, '(1)') + tag(430, 268, '(2)')))
    # أربعة ثلاثي ميثيل بنزين للاختيار
    b = ''
    sets = [((0, 'CH3'), (1, 'CH3'), (3, 'CH3')), ((0, 'CH3'), (2, 'CH3'), (4, 'H3C')), ((0, 'CH3'), (1, 'CH3'), (2, 'CH3')), ((0, 'CH3'), (1, 'CH3'), (3, 'CH2CH3'))]
    for i, ks in enumerate(sets):
        x = 85 + i * 185
        b += ring(x, 135, 'circle')
        for k, lab in ks: b += sub(x, 135, k, lab)
        b += tag(x, 265, f'({i + 1})')
    save(P + 'trimethyl4.svg', svg(760, 285, b))
    # --- الحلقات الملتحمة ---
    d = R * math.sqrt(3)
    fused('naphthalene.svg', [(0, 0), (1, 0)], 260, 170, dx=130 - d / 2, dy=85)
    fused('anthracene.svg', [(0, 0), (1, 0), (2, 0)], 340, 170, dx=170 - d, dy=85)
    fused('phenanthrene.svg', [(0, 0), (1, 0), (1, 1)], 300, 250, dx=150 - d * 0.75, dy=165)
    fused('benzopyrene.svg', [(0, 0), (1, 0), (0, 1), (1, -1), (0, 2)], 320, 360, dx=160 - d * 0.5, dy=240)
    # ثلاث حلقات ملتحمة للمقارنة: (1) نفثالين (2) أنثراسين (3) فينانثرين
    def at(ox, oy, cs):
        out = ''
        for i, j in cs: out += ring(ox + i * d + j * d / 2, oy - j * d * math.sqrt(3) / 2, 'circle')
        return out
    px = ring(780, 135, 'circle') + sub(780, 135, 0, 'CH3') + sub(780, 135, 3, 'CH3')
    save(P + 'fused3.svg', svg(880, 290, at(70, 150, [(0, 0), (1, 0)]) + tag(110, 275, '(1)')
         + at(260, 150, [(0, 0), (1, 0), (2, 0)]) + tag(340, 275, '(2)')
         + at(510, 175, [(0, 0), (1, 0), (1, 1)]) + tag(590, 275, '(3)')
         + px + tag(780, 275, '(4)')))
