# رسوم الدرس 6-2 — الكربوهيدرات: حلقات هاورث للجلوكوز والجلاكتوز والفركتوز، والسكريات الثنائية (السكروز واللاكتوز والمالتوز)
# بالرابطة الإيثرية C–O–C، والسلاسل المفتوحة (مجموعة الكربونيل ظاهرة)، ومخططات السكريات عديدة التسكر.
# التشغيل: python3 data/chem22/gen/figs/C6-L2.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

P = 'c6-l2-'
SZ = 20
LAT = 'font-family="Arial,Helvetica,sans-serif" font-weight="bold"'
HL = '#fde8c8'   # تظليل H وOH في معادلة التكثف


def ftext(x, yc, s, size=SZ, anchor='middle', color=INK):
    """صيغة لاتينية من اليسار إلى اليمين، والأرقام بعد الحرف أو القوس منخفضة. yc = منتصف السطر."""
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


def line(x1, y1, x2, y2, w=2.4, color=INK):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'


def label_at(x, y, lab, d, anchor='middle', size=SZ):
    """نص طرف رابطة رأسية: d = −1 أعلى، 1 أسفل."""
    if not lab: return ''
    yc = y + d * (size * 0.55)
    return ftext(x, yc, lab, size, anchor)


def ring(verts, oxy_index, front):
    """حلقة هاورث: verts قائمة رؤوس، oxy_index رأس الأكسجين، front أزواج الأضلاع الأمامية السميكة."""
    s = ''; n = len(verts)
    for k in range(n):
        a, b = verts[k], verts[(k + 1) % n]
        # قص الضلع عند ذرة الأكسجين
        def cut(p, q, r=11):
            dx, dy = q[0] - p[0], q[1] - p[1]; L_ = math.hypot(dx, dy)
            return (p[0] + dx * r / L_, p[1] + dy * r / L_)
        p, q = a, b
        if k == oxy_index: p = cut(a, b)
        if (k + 1) % n == oxy_index: q = cut(b, a)
        w = 6 if (k, (k + 1) % n) in front else 2.6
        s += line(p[0], p[1], q[0], q[1], w)
    ox, oy = verts[oxy_index]
    s += ftext(ox, oy, 'O', SZ)
    return s


def subst(x, y, up, down, lu=34, ld=34, au='middle', ad='middle'):
    s = ''
    if up:
        s += line(x, y, x, y - lu) + label_at(x + (0 if au == 'middle' else (10 if au == 'end' else -10)), y - lu, up, -1, au)
    if down:
        s += line(x, y, x, y + ld) + label_at(x + (0 if ad == 'middle' else (10 if ad == 'end' else -10)), y + ld, down, 1, ad)
    return s


def pyranose(cx, cy, subs, skip=()):
    """حلقة سداسية (هاورث). subs: dict رقم الكربون → (أعلى، أسفل). الرؤوس: C1 يمين، C2 أمام-يمين، C3 أمام-يسار، C4 يسار، C5 خلف-يسار، O خلف-يمين."""
    V = {1: (cx + 72, cy), 2: (cx + 38, cy + 30), 3: (cx - 38, cy + 30), 4: (cx - 72, cy), 5: (cx - 38, cy - 30), 'O': (cx + 38, cy - 30)}
    verts = [V[5], V['O'], V[1], V[2], V[3], V[4]]
    s = ring(verts, 1, {(2, 3), (3, 4), (4, 5)})
    for c, (u, d) in subs.items():
        if c in skip: continue
        x, y = V[c]
        lu = 22 if c in (2, 3) else 34
        s += subst(x, y, u, d, lu=lu)
    return s, V


def furanose(cx, cy, subs, skip=(), flipped=False):
    """حلقة خماسية (هاورث) للفركتوز: O خلف-وسط، C2 يمين، C3 أمام-يمين، C4 أمام-يسار، C5 يسار.
    flipped: الفركتوز مقلوبًا (دوران 180° حول محور العمق) كما يُرسم في السكروز: C2 يسار، C5 يمين، ويتبادل أعلى/أسفل في subs."""
    sg = -1 if flipped else 1
    V = {'O': (cx, cy - 38), 2: (cx + sg * 60, cy - 6), 3: (cx + sg * 36, cy + 34), 4: (cx - sg * 36, cy + 34), 5: (cx - sg * 60, cy - 6)}
    verts = [V['O'], V[2], V[3], V[4], V[5]]
    s = ring(verts, 0, {(1, 2), (2, 3), (3, 4)})
    right = lambda c: V[c][0] > cx
    for c, (u, d) in subs.items():
        if c in skip: continue
        x, y = V[c]
        if c in (3, 4):   # الكربونان الأماميان: النص العلوي داخل الحلقة مائلًا نحو المركز
            s += subst(x, y, u, d, lu=24, ld=30, au='end' if right(c) else 'start')
        else:             # الكربونان الجانبيان: الرابطة السفلية أطول والنص نحو الخارج
            s += subst(x, y, u, d, lu=34, ld=48, ad='start' if right(c) else 'end')
    return s, V


def furanose_flipped(cx, cy, subs, skip=()):
    return furanose(cx, cy, subs, skip, flipped=True)


GLU = {1: (None, 'OH'), 2: (None, 'OH'), 3: ('OH', None), 4: (None, 'HO'), 5: ('CH2OH', None)}
GAL = {1: (None, 'OH'), 2: (None, 'OH'), 3: ('OH', None), 4: ('HO', None), 5: ('CH2OH', None)}
GAL_B = {1: ('OH', None), 2: (None, 'OH'), 3: ('OH', None), 4: ('HO', None), 5: ('CH2OH', None)}
FRU = {2: ('OH', 'CH2OH'), 3: ('OH', None), 4: (None, 'OH'), 5: ('CH2OH', None)}
FRU_FLIP = {2: ('CH2OH', None), 3: (None, 'OH'), 4: ('OH', None), 5: (None, 'CH2OH')}


def tag(x, y, s, size=17):
    return T(x, y, s, size, weight='bold', color=MUTED)


def plus(x, y): return ftext(x, y, '+', 26)


# ---------- السلاسل المفتوحة (إسقاط فيشر مبسط) ----------
def fischer(cx, top, rows, step=46):
    """rows: قائمة صفوف؛ كل صف (يسار، مركز، يمين، رابطة_يمين) — مركز 'C' أو نص طرفي مثل 'CH2OH'. يُرجع الرسم وآخر y."""
    s = ''; y = top; prev = None
    for k, (lft, ctr, rgt, order) in enumerate(rows):
        if prev is not None:
            s += line(cx, prev + 13, cx, y - 13)
        s += ftext(cx, y, ctr, SZ)
        hw = 9 if ctr == 'C' else 0
        if lft:
            s += line(cx - hw - 4, y, cx - 40, y) + ftext(cx - 44, y, lft, SZ, 'end')
        if rgt:
            if order == 2:
                s += line(cx + hw + 4, y - 3.5, cx + 40, y - 3.5) + line(cx + hw + 4, y + 3.5, cx + 40, y + 3.5)
            else:
                s += line(cx + hw + 4, y, cx + 40, y)
            s += ftext(cx + 44, y, rgt, SZ, 'start')
        prev = y; y += step
    return s, prev


GLU_OPEN = [('H', 'C', 'O', 2), ('H', 'C', 'OH', 1), ('HO', 'C', 'H', 1), ('H', 'C', 'OH', 1), ('H', 'C', 'OH', 1), (None, 'CH2OH', None, 1)]
GAL_OPEN = [('H', 'C', 'O', 2), ('H', 'C', 'OH', 1), ('HO', 'C', 'H', 1), ('HO', 'C', 'H', 1), ('H', 'C', 'OH', 1), (None, 'CH2OH', None, 1)]
FRU_OPEN = [(None, 'CH2OH', None, 1), (None, 'C', 'O', 2), ('HO', 'C', 'H', 1), ('H', 'C', 'OH', 1), ('H', 'C', 'OH', 1), (None, 'CH2OH', None, 1)]


# ---------- رموز مبسطة للوحدات (سداسي صغير) ----------
def hexa(cx, cy, r=13, fill='#d8e8f6'):
    pts = [(cx + r * math.cos(math.radians(30 + 60 * k)), cy + r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" stroke="{BLUE}" stroke-width="2"/>'


def hchain(x0, y, n, gap=34, dots=False):
    s = ''
    for k in range(n):
        x = x0 + k * gap
        if k: s += line(x - gap + 13, y, x - 13, y, 2.2, BLUE)
        s += hexa(x, y)
    if dots:
        xe = x0 + (n - 1) * gap
        s += line(xe + 13, y, xe + 24, y, 2.2, BLUE) + T(xe + 36, y + 6, '…', 18, color=BLUE)
    return s


def main():
    os.makedirs(OUT, exist_ok=True)

    # 1) الجلوكوز الحلقي وحده
    b, _ = pyranose(150, 105, GLU)
    save(P + 'glucose-ring.svg', svg(300, 205, b))

    # 2) ثلاثة سكريات أحادية حلقية بلا أسماء: (أ) جلوكوز (ب) فركتوز (ج) جلاكتوز
    b1, _ = pyranose(130, 115, GLU); b2, _ = furanose(400, 115, FRU); b3, _ = pyranose(650, 115, GAL)
    b = b1 + b2 + b3 + tag(130, 215, '(أ)') + tag(400, 215, '(ب)') + tag(650, 215, '(ج)')
    save(P + 'three-rings.svg', svg(780, 230, b))

    # 3) الجلوكوز والجلاكتوز الحلقيان جنبًا إلى جنب (س، ص)
    b1, _ = pyranose(140, 110, GLU); b2, _ = pyranose(440, 110, GAL)
    b = b1 + b2 + tag(140, 210, '(س)') + tag(440, 210, '(ص)') + line(290, 20, 290, 200, 1, MUTED)
    save(P + 'glu-gal-rings.svg', svg(580, 225, b))

    # 4) السلاسل المفتوحة الثلاث (أ، ب، ج) — جلوكوز، جلاكتوز، فركتوز
    s1, yb = fischer(110, 40, GLU_OPEN); s2, _ = fischer(330, 40, GAL_OPEN); s3, _ = fischer(550, 40, FRU_OPEN)
    b = s1 + s2 + s3 + tag(110, yb + 40, '(أ)') + tag(330, yb + 40, '(ب)') + tag(550, yb + 40, '(ج)')
    save(P + 'open-three.svg', svg(660, yb + 55, b))

    # 5) الجلوكوز والفركتوز مفتوحا السلسلة (س، ص)
    s1, yb = fischer(120, 40, GLU_OPEN); s2, _ = fischer(360, 40, FRU_OPEN)
    b = s1 + s2 + tag(120, yb + 40, '(س)') + tag(360, yb + 40, '(ص)')
    save(P + 'open-glu-fru.svg', svg(480, yb + 55, b))

    # 6) الجلوكوز مفتوح السلسلة وحده
    s1, yb = fischer(120, 40, GLU_OPEN)
    save(P + 'glucose-open.svg', svg(240, yb + 30, s1))

    # 7) سكر ثنائي: جلوكوز – O – فركتوز (السكروز) بلا اسم
    def sucrose(gx, gy):
        g, V = pyranose(gx, gy, GLU, skip=(1,))
        x1, y1 = V[1]
        f, W = furanose_flipped(x1 + 130, gy + 6, FRU_FLIP)
        x2, y2 = W[2]
        ox, oy = (x1 + x2) / 2, y1 + 22
        return g + f + line(x1, y1, ox - 11, oy - 4) + ftext(ox, oy, 'O') + line(ox + 11, oy - 4, x2, y2), W[5][0] + 70
    b, _ = sucrose(110, 110)
    save(P + 'sucrose.svg', svg(520, 215, b))

    # 8) معادلة تكوين السكروز في سطرين: جلوكوز + فركتوز ← (سهم لأسفل) سكروز + H2O (OH وH مظللتان)
    def hl(x, y, w): return f'<rect x="{x - w / 2:.1f}" y="{y - 14:.1f}" width="{w}" height="28" rx="5" fill="{HL}"/>'
    g, V = pyranose(105, 110, GLU, skip=(1,))
    x1, y1 = V[1]
    g += line(x1, y1, x1 + 18, y1) + hl(x1 + 36, y1, 40) + ftext(x1 + 21, y1, 'OH', anchor='start')
    f, W = furanose_flipped(x1 + 205, 116, FRU_FLIP, skip=(2,))
    x2, y2 = W[2]
    f += line(x2 - 18, y2, x2, y2) + hl(x2 - 37, y2, 22) + ftext(x2 - 21, y2, 'HO', anchor='end')
    react = g + plus(x1 + 74, 110) + f
    mid = 280
    def row2(prod):
        return ARROW(mid, 215, mid, 275) + prod
    b_prod, xe = sucrose(105, 375)
    eq = react + row2(b_prod) + plus(xe + 15, 375) + ftext(xe + 65, 375, 'H2O')
    save(P + 'sucrose-eq.svg', svg(560, 480, eq))

    # 9) المعادلة نفسها مع ناتج مجهول (؟)
    box = f'<rect x="{mid - 110}" y="335" width="140" height="80" rx="8" fill="#fff" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 5"/>' + T(mid - 40, 388, '؟', 36, weight='bold')
    eq_q = react + row2(box) + plus(mid + 65, 375) + ftext(mid + 120, 375, 'H2O')
    save(P + 'sucrose-eq-q.svg', svg(560, 440, eq_q))

    # 10) سكر ثنائي (جلاكتوز – O – جلوكوز) = اللاكتوز، بلا اسم
    def disacch(name, left_subs, w=520):
        a, V = pyranose(120, 110, left_subs, skip=(1,))
        c, W = pyranose(390, 110, GLU, skip=(4,))
        xa, ya = V[1]; xb, yb = W[4]
        ox, oy = (xa + xb) / 2, ya + 22
        bb = a + c + line(xa, ya, ox - 11, oy - 4) + ftext(ox, oy, 'O') + line(ox + 11, oy - 4, xb, yb)
        save(name, svg(w, 215, bb))
    disacch(P + 'lactose.svg', GAL_B)
    disacch(P + 'maltose.svg', GLU)

    # 11) نماذج السكريات عديدة التسكر: (أ) سلاسل مستقيمة متوازية متقاطعة، (ب) سلسلة كثيرة التفرع
    b = ''
    for r in range(3):
        y = 50 + r * 55
        b += hchain(40, y, 8)
        if r < 2:
            for k in (1, 3, 5, 7):
                b += line(40 + k * 34, y + 13, 40 + k * 34, y + 42, 1.6, MUTED).replace('stroke-linecap="round"', 'stroke-dasharray="4 4"')
    b += tag(160, 210, '(أ)')
    # كثيرة التفرع
    bx = 380
    b += hchain(bx, 70, 6)
    b += line(bx + 68, 83, bx + 90, 105, 2.2, BLUE) + hchain(bx + 100, 115, 5)
    b += line(bx + 34, 83, bx + 34, 145, 2.2, BLUE).replace(f'y2="145.0"', 'y2="146"') + hchain(bx + 34, 158, 3)
    b += line(bx + 168, 128, bx + 190, 150, 2.2, BLUE) + hchain(bx + 200, 162, 4)
    b += line(bx + 134, 57, bx + 156, 35, 2.2, BLUE) + hchain(bx + 166, 25, 3)
    b += tag(510, 210, '(ب)')
    b += line(340, 15, 340, 200, 1, MUTED)
    save(P + 'poly-models.svg', svg(730, 225, b))

    # 12) عدد الوحدات: (س) وحدة واحدة، (ص) وحدتان، (ع) سلسلة طويلة
    b = hexa(70, 60, 18) + tag(70, 125, '(س)')
    b += hexa(190, 60, 18) + line(208, 60, 232, 60, 2.2, BLUE) + hexa(250, 60, 18) + tag(220, 125, '(ص)')
    b += hchain(340, 60, 14, gap=30) + tag(535, 125, '(ع)')
    b += line(130, 20, 130, 135, 1, MUTED) + line(305, 20, 305, 135, 1, MUTED)
    save(P + 'unit-counts.svg', svg(760, 145, b))

    # 13) الفركتوز الحلقي وحده
    b, _ = furanose(150, 110, FRU)
    save(P + 'fructose-ring.svg', svg(300, 205, b))

    # 14) الحلقة والسلسلة المفتوحة للجلوكوز (س ⇌ ص)
    r, _ = pyranose(130, 150, GLU)
    s1, yb = fischer(430, 40, GLU_OPEN)
    b = r + tag(130, 260, '(س)') + s1 + tag(430, yb + 40, '(ص)') + T(280, 158, '⇌', 34, weight='bold')
    save(P + 'glu-ring-open.svg', svg(540, yb + 55, b))


if __name__ == '__main__':
    main()
