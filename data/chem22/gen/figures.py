# رسوم أسئلة كيمياء 2-2 (SVG ثابتة في public/qimg/chem22). التشغيل: python3 data/chem22/gen/figures.py
# مكتبة صغيرة: مخطط المحتوى الحراري، ومنحنى التسخين، وتدريج حرارة التكوين. خلفية بيضاء (تظهر كما هي في الوضع الليلي والطباعة).
import os
OUT = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'public', 'qimg', 'chem22')
INK = '#1f2a44'; MUTED = '#5b6676'; BLUE = '#2a6fb0'; RED = '#b03a2e'; GREEN = '#1f7a4d'
FONT = "font-family=\"'IBM Plex Sans Arabic','Noto Naskh Arabic',Tahoma,Arial,sans-serif\""

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def T(x, y, s, size=15, anchor='middle', color=INK, weight='normal', rtl=False):
    # rtl يُطبَّق فقط على النص العربي؛ وanchor يُعطى بالمعنى المرئي (start = الطرف الأيسر) فيُقلب للنص العربي
    import re
    rtl = bool(re.search('[\u0600-\u06FF]', s))
    if rtl and anchor in ('start', 'end'): anchor = 'end' if anchor == 'start' else 'start'
    d = ' direction="rtl"' if rtl else ''
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}" {FONT}{d}>{esc(s)}</text>'
def L(x1, y1, x2, y2, color=INK, w=2, dash=''):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{da}/>'
def ARROW(x1, y1, x2, y2, color=INK, w=2.5):
    import math
    a = math.atan2(y2 - y1, x2 - x1); h = 10
    p1 = (x2 - h * math.cos(a - 0.4), y2 - h * math.sin(a - 0.4)); p2 = (x2 - h * math.cos(a + 0.4), y2 - h * math.sin(a + 0.4))
    return L(x1, y1, x2 - 6 * math.cos(a), y2 - 6 * math.sin(a), color, w) + f'<polygon points="{x2},{y2} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'
def svg(w, h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n<rect width="{w}" height="{h}" fill="#fff"/>\n{body}\n</svg>\n'
def save(name, s):
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(s); print(name)

def yaxis(x, top, bottom, label):
    size = 22 if label == '؟' else 15
    return ARROW(x, bottom, x, top) + f'<text transform="translate({x - 16},{(top + bottom) / 2}) rotate(-90)" text-anchor="middle" font-size="{size}" fill="{INK}" font-weight="bold" {FONT}>{esc(label)}</text>'

def enthalpy(name, upper, lower, dh, direction, axis='المحتوى الحراري (H)', heat_note=None, w=500, h=260, title=None):
    """مخطط محتوى حراري: مستويان، وسهم ΔH من المتفاعلات إلى النواتج. direction: 'down' (طارد) أو 'up' (ماص)."""
    x0, top, bot = 60, 40, h - 30
    yu, yl = 80, h - 70
    b = yaxis(x0, top - 10, bot, axis)
    b += L(110, yu, 250, yu, INK, 3) + T(180, yu - 10, upper, 15)
    b += L(250 if direction == 'down' else 110, yl, 390 if direction == 'down' else 250, yl, INK, 3)
    b += T(320 if direction == 'down' else 180, yl + 22, lower, 15)
    if direction == 'down':
        b += L(250, yu, 320, yu, MUTED, 1.2, '4 4') + ARROW(320, yu + 2, 320, yl - 2, RED)
        b += T(332, (yu + yl) / 2 + 5, dh, 15, 'start', RED, 'bold')
    else:
        b += L(250, yu, 390, yu, INK, 3)
        b = b.replace(L(110, yu, 250, yu, INK, 3) + T(180, yu - 10, upper, 15), '')
        b += T(320, yu - 10, upper, 15) + L(110, yl, 250, yl, INK, 3)
        b += L(250, yl, 320, yl, MUTED, 1.2, '4 4') + ARROW(320, yl - 2, 320, yu + 2, BLUE)
        b += T(332, (yu + yl) / 2 + 5, dh, 15, 'start', BLUE, 'bold')
    if heat_note: b += T(110, h - 8, heat_note, 13, 'start', MUTED, rtl=True)
    if title: b += T(w / 2, 22, title, 15, weight='bold', rtl=True)
    save(name, svg(w, h, b))

def levels(name, items, axis='المحتوى الحراري (H)', w=460, h=300, arrows=()):
    """مستويات متعددة: items = [(label, y)]، arrows = [(x, y_from, y_to, text, color)]"""
    b = yaxis(55, 25, h - 20, axis)
    for lab, y in items: b += L(100, y, 260, y, INK, 3) + T(180, y - 9, lab, 15)
    for x, y1, y2, txt, col in arrows:
        b += ARROW(x, y1, x, y2, col) + T(x + 10, (y1 + y2) / 2 + 5, txt, 14, 'start', col, 'bold')
    save(name, svg(w, h, b))

def heating_curve(name, w=480, h=300, numbered=True):
    """منحنى تسخين الماء من −20 إلى 120 °C بمعدل ثابت (الأجزاء الخمسة مرقمة)."""
    X0, Y0, X1, Y1 = 70, h - 45, w - 25, 25
    def ty(t): return Y0 - (t + 30) / 160 * (Y0 - Y1)
    pts = [(X0 + 25, ty(-20)), (X0 + 55, ty(0)), (X0 + 90, ty(0)), (X0 + 185, ty(100)), (X0 + 345, ty(100)), (X0 + 375, ty(120))]
    b = ARROW(X0, Y0, X1, Y0) + ARROW(X0, Y0, X0, Y1)
    b += T((X0 + X1) / 2, h - 10, 'الزمن (بمعدل تسخين ثابت)', 14, rtl=True)
    b += f'<text transform="translate({X0 - 48},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" {FONT}>درجة الحرارة (°C)</text>'
    for t in (-20, 0, 100, 120):
        b += L(X0 - 5, ty(t), X0, ty(t)) + T(X0 - 9, ty(t) + 5, f'{t}'.replace('-', '−'), 13, 'end')
        if t in (0, 100): b += L(X0, ty(t), pts[4][0] if t == 100 else pts[2][0], ty(t), MUTED, 1, '3 4')
    b += f'<polyline points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in pts)}" fill="none" stroke="{BLUE}" stroke-width="3.5" stroke-linejoin="round"/>'
    if numbered:
        for k, ((xa, ya), (xb, yb)) in enumerate(zip(pts, pts[1:]), 1):
            cx, cy = (xa + xb) / 2, (ya + yb) / 2
            dy = -14 if ya == yb else 0; dx = -16 if ya != yb else 0
            b += f'<circle cx="{cx + dx:.0f}" cy="{cy + dy:.0f}" r="10" fill="#fff" stroke="{INK}" stroke-width="1.5"/>' + T(cx + dx, cy + dy + 5, str(k), 13, weight='bold')
    save(name, svg(w, h, b))

def formation(name, items, w=460, h=330, arrows=True, zero_label='العناصر في حالاتها القياسية'):
    """تدريج حرارة التكوين القياسية: خط الصفر للعناصر، والمركبات فوقه أو تحته. items = [(label, value)]"""
    vmax = max(50, max(v for _, v in items)); vmin = min(v for _, v in items)
    top, bot = 40, h - 30
    def y(v): return top + (vmax - v) / (vmax - vmin) * (bot - top)
    b = yaxis(60, top - 15, bot, 'ΔH°f (kJ/mol)')
    b += L(95, y(0), 400, y(0), INK, 2.5) + T(410, y(0) + 5, '0.0', 13, 'start', MUTED) + T(398, y(0) - 8, zero_label, 13, 'end', MUTED)
    xs = [150, 300]
    for k, (lab, v) in enumerate(items):
        x = xs[k % len(xs)]
        b += L(x - 55, y(v), x + 55, y(v), INK, 3)
        b += T(x, y(v) + (20 if v < 0 else -9), f'{lab}  {("+" if v > 0 else "") + str(v).replace("-", "−")}', 14)
        if arrows: b += ARROW(x, y(0), x, y(v), RED if v < 0 else BLUE, 2.2)
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # الدرس 1-2: مخططات المحتوى الحراري
    enthalpy('c1-endo-233.svg', 'النواتج', 'المتفاعلات', 'ΔH = +233 kJ', 'up')
    enthalpy('c1-axis-q.svg', 'المتفاعلات', 'النواتج', 'ΔH', 'down', axis='؟')
    enthalpy('c1-hot-pack.svg', '4Fe(s) + 3O₂(g)', '2Fe₂O₃(s)', 'ΔH = −1625 kJ', 'down', heat_note='الحرارة تنطلق من النظام إلى المحيط')
    levels('c1-water-levels.svg', [('H₂O(g)', 50), ('H₂O(l)', 210), ('H₂O(s)', 255)],
           arrows=[(290, 255, 212, '+6.01 kJ', BLUE), (290, 208, 52, '+40.7 kJ', BLUE)])
    # مخططان (س) و(ص) جنبًا إلى جنب
    def panel(ox, label, direction, val, col):
        b = T(ox + 110, 22, label, 16, weight='bold') + yaxis(ox + 25, 35, 220, 'H')
        yu, yl = 70, 185
        if direction == 'down':
            b += L(ox + 45, yu, ox + 125, yu, INK, 3) + T(ox + 85, yu - 8, 'المتفاعلات', 13) + L(ox + 125, yl, ox + 195, yl, INK, 3) + T(ox + 160, yl + 18, 'النواتج', 13)
            b += ARROW(ox + 160, yu + 2, ox + 160, yl - 2, col) + T(ox + 168, (yu + yl) / 2 + 5, val, 13, 'start', col, 'bold')
        else:
            b += L(ox + 45, yl, ox + 125, yl, INK, 3) + T(ox + 85, yl + 18, 'المتفاعلات', 13) + L(ox + 125, yu, ox + 195, yu, INK, 3) + T(ox + 160, yu - 8, 'النواتج', 13)
            b += ARROW(ox + 160, yl - 2, ox + 160, yu + 2, col) + T(ox + 168, (yu + yl) / 2 + 5, val, 13, 'start', col, 'bold')
        return b
    save('c1-two-diagrams.svg', svg(520, 240, panel(10, '(س)', 'down', '90 kJ', RED) + panel(270, '(ص)', 'up', '30 kJ', BLUE) + L(260, 20, 260, 225, MUTED, 1, '4 4')))
    # الدرس 1-3: منحنى تسخين الماء
    heating_curve('c1-heating-curve.svg')
    # الدرس 1-4: تدريج حرارة التكوين
    formation('c1-formation-no2-so3.svg', [('NO₂(g)', 33.2), ('SO₃(g)', -396)])
    formation('c1-formation-water.svg', [('H₂O(g)', -241.8), ('H₂O(l)', -285.8)], arrows=False, zero_label='H₂(g) + ½O₂(g)')
