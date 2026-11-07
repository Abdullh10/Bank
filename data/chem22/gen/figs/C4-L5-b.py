# رسوم الدرس 4-5 (النصف الثاني): ثبات البنزين، رفض الصيغ القديمة، المواد المسرطنة، الحلقات الملتحمة، ومقارنة الأروماتية بالأليفاتية.
# التشغيل: python3 data/chem22/gen/figs/C4-L5-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *
_spec = importlib.util.spec_from_file_location('l5a', os.path.join(os.path.dirname(__file__), 'C4-L5-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
ring, sub, verts, chem, tag, zigzag, R = A.ring, A.sub, A.verts, A.chem, A.tag, A.zigzag, A.R

P = 'c4-l5b-'
CLOUD = '#8fbbe6'

def atom(x, y, s, r=15, fill='#fff', size=16):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{INK}" stroke-width="2"/>' + chem(x, y + size * 0.36, s, size)

def dbl(x1, y1, x2, y2, gap=4, w=2.4):
    dx, dy = x2 - x1, y2 - y1; ln = math.hypot(dx, dy); nx, ny = -dy / ln * gap, dx / ln * gap
    return L(x1 + nx, y1 + ny, x2 + nx, y2 + ny, INK, w) + L(x1 - nx, y1 - ny, x2 - nx, y2 - ny, INK, w)

def trip(x1, y1, x2, y2, gap=6, w=2.2):
    return L(x1, y1, x2, y2, INK, w) + dbl(x1, y1, x2, y2, gap, w)

def lattice(cs, ox, oy, style='circle'):
    d = R * math.sqrt(3); out = ''
    for i, j in cs: out += ring(ox + i * d + j * d / 2, oy - j * d * math.sqrt(3) / 2, style)
    return out

def formula(cs):
    """عدد ذرات C و H لنظام حلقات بنزين ملتحمة (للتحقق)."""
    d = R * math.sqrt(3); cnt = {}
    for i, j in cs:
        for v in verts(i * d + j * d / 2, -j * d * math.sqrt(3) / 2):
            k = (round(v[0], 1), round(v[1], 1)); cnt[k] = cnt.get(k, 0) + 1
    return len(cnt), sum(1 for n in cnt.values() if n == 1)

def electron_rings():
    cx, cy, rx, ry = 260, 150, 120, 42
    th = [math.radians(a) for a in range(0, 360, 60)]
    C = [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in th]
    H = [(cx + 1.62 * rx * math.cos(t), cy + 1.62 * ry * math.sin(t)) for t in th]
    band = lambda yy, op: f'<ellipse cx="{cx}" cy="{yy}" rx="{rx}" ry="{ry}" fill="none" stroke="{CLOUD}" stroke-width="13" opacity="{op}"/>'
    b = band(cy + 40, 0.8)
    for k in range(6):
        b += L(*C[k], *C[(k + 1) % 6], INK, 3) + L(*C[k], *H[k], INK, 2)
    for k in range(6): b += atom(*H[k], 'H', 11, '#f3f3f3', 13)
    for k in range(6): b += atom(*C[k], 'C', 15, '#d9d9d9')
    b += band(cy - 40, 0.6)
    save(P + 'electron-rings.svg', svg(520, 300, b))

def local_vs_deloc():
    # (1) الإيثين: سحابة حول ذرتي الكربون فقط
    x1, x2, y = 90, 170, 130
    b = f'<ellipse cx="{(x1 + x2) / 2}" cy="{y}" rx="62" ry="26" fill="{CLOUD}" opacity="0.55"/>'
    b += dbl(x1, y, x2, y, 4)
    for (hx, hy, cx) in [(x1 - 42, y - 38, x1), (x1 - 42, y + 38, x1), (x2 + 42, y - 38, x2), (x2 + 42, y + 38, x2)]:
        b += L(cx, y, hx, hy, INK, 2.2) + atom(hx, hy, 'H', 11, '#f3f3f3', 13)
    b += atom(x1, y, 'C') + atom(x2, y, 'C') + tag(130, 250, '(1)')
    # (2) البنزين: سحابة حلقية تشمل ذرات الكربون الست
    cx, cy = 400, 130
    b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{CLOUD}" stroke-width="26" opacity="0.55"/>'
    v = verts(cx, cy, R)
    b += f'<polygon points="{" ".join(f"{x:.1f},{y_:.1f}" for x, y_ in v)}" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    for k in range(6):
        a = math.radians(-90 + 60 * k); hx, hy = v[k][0] + 34 * math.cos(a), v[k][1] + 34 * math.sin(a)
        b += L(*v[k], hx, hy, INK, 2) + atom(hx, hy, 'H', 10, '#f3f3f3', 12)
    for k in range(6): b += atom(*v[k], 'C', 12, '#fff', 14)
    b += tag(400, 250, '(2)')
    save(P + 'local-vs-deloc.svg', svg(530, 270, b))

def chain1860(x0=70, y=120, step=64, name='chain1860.svg', w=470, h=230, body_only=False):
    xs = [x0 + i * step for i in range(6)]
    b = ''
    kinds = ['d', 'd', 's', 'd', 'd']
    for i in range(5):
        a, c = xs[i] + 14, xs[i + 1] - 14
        b += dbl(a, y, c, y, 4) if kinds[i] == 'd' else L(a, y, c, y, INK, 2.4)
    Hs = [(xs[0] - 40, y - 40, xs[0]), (xs[0] - 40, y + 40, xs[0]), (xs[2], y - 55, xs[2]), (xs[3], y - 55, xs[3]),
          (xs[5] + 40, y - 40, xs[5]), (xs[5] + 40, y + 40, xs[5])]
    for hx, hy, cx in Hs: b += L(cx, y, hx, hy, INK, 2.2) + atom(hx, hy, 'H', 11, '#f3f3f3', 13)
    for x in xs: b += atom(x, y, 'C', 14)
    if body_only: return b
    save(P + name, svg(w, h, b))

def three_models():
    b = chain1860(200, 90, 64, body_only=True) + tag(360, 175, '(1)')
    b += ring(240, 270, 'kekule') + tag(240, 360, '(2)')
    b += ring(480, 270, 'circle') + tag(480, 360, '(3)')
    save(P + 'three-models.svg', svg(720, 380, b))

BAP = [(0, 0), (1, 0), (0, 1), (1, -1), (0, 2)]   # البنزوبايرين: البايرين + حلقة على الرابطة a

def benzopyrene():
    d = R * math.sqrt(3)
    save(P + 'benzopyrene.svg', svg(320, 360, lattice(BAP, 160 - d / 2, 245)))

def fused_or_not():
    d = R * math.sqrt(3)
    # (1) حلقتا بنزين متصلتان برابطة أحادية (عموديًّا)
    b = ring(100, 70, 'circle') + L(100, 70 + R, 100, 70 + R + 34, INK, 2.4) + ring(100, 70 + 2 * R + 34, 'circle') + tag(100, 300, '(1)')
    # (2) نفثالين
    b += lattice([(0, 0), (1, 0)], 300 - d / 2, 150) + tag(300, 300, '(2)')
    # (3) 1، 4-ثنائي ميثيل بنزين
    b += ring(500, 150, 'circle') + sub(500, 150, 0, 'CH3') + sub(500, 150, 3, 'CH3') + tag(500, 300, '(3)')
    # (4) حلقة بنزين متصلة برابطة أحادية بحلقة سداسية مشبعة
    b += ring(690, 70, 'circle') + L(690, 70 + R, 690, 70 + R + 34, INK, 2.4) + ring(690, 70 + 2 * R + 34, 'plain') + tag(690, 300, '(4)')
    save(P + 'fused-or-not.svg', svg(790, 320, b))

def cyclohexene_benzene():
    b = ring(120, 110, 'plain', (0,)) + tag(120, 210, '(1)') + ring(330, 110, 'circle') + tag(330, 210, '(2)')
    save(P + 'cyclohexene-benzene.svg', svg(450, 230, b))

def four_reactivity():
    b = zigzag(30, 130, 6, 32, 22, doubles=(0,)) + tag(110, 235, '(1)')
    b += ring(285, 125, 'plain', (0,)) + tag(285, 235, '(2)')
    b += ring(450, 135, 'circle') + sub(450, 135, 1, 'CH2CH3') + tag(470, 235, '(3)')
    x, y = 610, 130
    pts = [(x, y), (x + 40, y), (x + 80, y), (x + 112, y - 22), (x + 144, y), (x + 176, y - 22)]
    b += trip(*pts[0], *pts[1]) + L(*pts[1], *pts[2], INK, 2.4)
    b += f'<polyline points="{" ".join(f"{a:.1f},{c:.1f}" for a, c in pts[2:])}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
    b += tag(698, 235, '(4)')
    save(P + 'four-reactivity.svg', svg(820, 255, b))

def anth_phen():
    d = R * math.sqrt(3)
    b = lattice([(0, 0), (1, 0), (2, 0)], 70, 130) + tag(70 + d, 250, '(1)')
    b += lattice([(0, 0), (1, 0), (1, 1)], 400, 160) + tag(400 + d * 0.75, 250, '(2)')
    save(P + 'anth-phen.svg', svg(640, 270, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    electron_rings(); local_vs_deloc(); chain1860(); three_models(); benzopyrene()
    fused_or_not(); cyclohexene_benzene(); four_reactivity(); anth_phen()
    for nm, cs in [('naphthalene', [(0, 0), (1, 0)]), ('anthracene', [(0, 0), (1, 0), (2, 0)]),
                   ('phenanthrene', [(0, 0), (1, 0), (1, 1)]), ('benzopyrene', BAP)]:
        print(nm, 'C%dH%d' % formula(cs))
