# رسوم الدرس 4-1 (ب) — الهيدروكربونات المشبعة وغير المشبعة، واختبار البروم، وبرج التقطير التجزيئي، والتكسير الحراري،
# ورقم الأوكتان والفرقعة، وفكرة القوة الحيوية.
# التشغيل: python3 data/chem22/gen/figs/C4-L1-b.py
import sys, os, math, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

_spec = importlib.util.spec_from_file_location('c4l1a', os.path.join(os.path.dirname(__file__), 'C4-L1-a.py'))
_a = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_a)
A, bond, structure, box, panel_label = _a.A, _a.bond, _a.structure, _a.box, _a.panel_label

def LT(x, y, s, size=16, anchor='middle', color=INK, weight='normal'):
    """نص لاتيني (صيغ، أرقام، وحدات) من اليسار إلى اليمين."""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{weight}" font-family="Arial,Helvetica,sans-serif">{esc(s)}</text>'

# ---------------------------------------------------------------- صيغ بنائية كاملة لسلاسل مستقيمة
def chain(x0, y0, orders, s=52):
    """سلسلة كربون مستقيمة أفقية مع جميع ذرات H. orders: رتب الروابط C–C (طولها n−1). تُرجع (atoms, bonds)."""
    n = len(orders) + 1
    atoms = [(x0 + i * s, y0, 'C') for i in range(n)]
    bonds = [(i, i + 1, o) for i, o in enumerate(orders)]
    used = [0] * n
    for i, o in enumerate(orders): used[i] += o; used[i + 1] += o
    for i in range(n):
        free = 4 - used[i]
        slots = []
        if i == 0: slots.append((-s, 0))
        if i == n - 1: slots.append((s, 0))
        slots += [(0, -s), (0, s)]
        # ذرة طرفية بروابط مضاعفة: نضع H أفقيًّا أولًا
        for dx, dy in slots[:free]:
            atoms.append((x0 + i * s + dx, y0 + dy, 'H')); bonds.append((i, len(atoms) - 1, 1))
    return atoms, bonds

def fig_sat_unsat():
    """(1) بروبين، (2) بيوتان، (3) بروباين، (4) بروبان — صيغ بنائية كاملة."""
    w, h = 900, 260; s = 50
    b = ''
    specs = [(1, [2, 1], 60), (2, [1, 1, 1], 270), (3, [3, 1], 540), (4, [1, 1], 735)]
    for k, orders, x0 in specs:
        at, bd = chain(x0, 115, orders, s)
        b += structure(at, bd)
    for x, lab in [(110, '(1)'), (345, '(2)'), (595, '(3)'), (785, '(4)')]: b += panel_label(x, 240, lab)
    for x in (205, 480, 680): b += L(x, 25, x, 220, '#d5d9e0', 1, '5 5')
    save('c4-l1b-sat-unsat.svg', svg(w, h, b))

def fig_butane_butene():
    """(1) بيوتان CH3CH2CH2CH3، (2) 1-بيوتين CH2=CHCH2CH3."""
    w, h = 720, 250; s = 52
    b = ''
    at, bd = chain(80, 115, [1, 1, 1], s); b += structure(at, bd)
    at, bd = chain(450, 115, [2, 1, 1], s); b += structure(at, bd)
    b += panel_label(158, 235, '(1)') + panel_label(528, 235, '(2)')
    b += L(360, 25, 360, 215, '#d5d9e0', 1, '5 5')
    save('c4-l1b-butane-butene.svg', svg(w, h, b))

# ---------------------------------------------------------------- اختبار البروم
def tube(x, y, liquid, label, w=56, h=190, level=0.55):
    s = ''
    lh = h * level
    s += f'<path d="M{x},{y + h - lh} L{x},{y + h - w / 2} A{w / 2},{w / 2} 0 0 0 {x + w},{y + h - w / 2} L{x + w},{y + h - lh} Z" fill="{liquid}" stroke="none"/>'
    s += f'<path d="M{x},{y} L{x},{y + h - w / 2} A{w / 2},{w / 2} 0 0 0 {x + w},{y + h - w / 2} L{x + w},{y}" fill="none" stroke="{INK}" stroke-width="2.5"/>'
    s += L(x - 6, y, x + w + 6, y, INK, 2.5)
    s += f'<line x1="{x + 2}" y1="{y + h - lh}" x2="{x + w - 2}" y2="{y + h - lh}" stroke="#7a8392" stroke-width="1.2"/>'
    s += LT(x + w / 2, y + h + 32, label, 22, weight='bold')
    return s

def fig_bromine_tubes():
    """أنبوبان بعد إضافة محلول البروم: X يبقى بنيًّا محمرًّا، Y عديم اللون."""
    w, h = 460, 300
    b = tube(110, 40, '#c4502a', 'X') + tube(300, 40, '#eef4fb', 'Y')
    b += T(138, 22, 'بنيّ محمرّ', 14, color=MUTED) + T(328, 22, 'عديم اللون', 14, color=MUTED)
    save('c4-l1b-bromine-tubes.svg', svg(w, h, b))

def fig_bromine_bars():
    """مقدار البروم المتفاعل مع كميات متساوية من أربعة هيدروكربونات A–D."""
    w, h = 560, 330
    x0, y0, top = 90, 270, 50
    b = yaxis(x0, top, y0, 'مقدار البروم المتفاعل')
    b += L(x0, y0, w - 30, y0, INK, 2)
    vals = [('A', 0), ('B', 1), ('C', 2), ('D', 0)]
    unit = 90
    for i, (lab, v) in enumerate(vals):
        cx = 160 + i * 105
        if v: b += f'<rect x="{cx - 28}" y="{y0 - v * unit}" width="56" height="{v * unit}" fill="{BLUE}" stroke="{INK}" stroke-width="1.5"/>'
        else: b += LT(cx, y0 - 10, '0', 18, color=RED, weight='bold')
        b += LT(cx, y0 + 28, lab, 20, weight='bold')
    b += T((x0 + w - 30) / 2 + 20, y0 + 56, 'الهيدروكربون (كميات متساوية)', 15)
    save('c4-l1b-bromine-bars.svg', svg(w, h, b))

# ---------------------------------------------------------------- برج التقطير التجزيئي
FRACTIONS = [  # (الاسم، درجة الحرارة، مدى ذرات الكربون)
    ('غازات', 'أقل من 40°C', 'CH₄ – C₄H₁₀'),
    ('الجازولين', '40 – 100°C', 'C₅H₁₂ – C₁₂H₂₆'),
    ('الكيروسين', '105 – 275°C', 'C₁₂H₂₆ – C₁₆H₃₄'),
    ('زيت التسخين', '240 – 300°C', 'C₁₅H₃₂ – C₁₈H₃₈'),
    ('زيت التزييت والتشحيم', 'فوق 300°C', 'C₁₇H₃₆ – C₂₂H₄₆'),
    ('المخلفات', '', ''),
]

def tower(name, labels, show_bottom_temp=True, gradient=True, furnace_label=True, w=860, h=600):
    """برج تجزئة: عمود رأسي، وأطباق، وفرن على اليمين، ومخارج على اليسار (من الأعلى إلى الأسفل).
    labels: قائمة من 6 عناصر، كل عنصر قائمة أسطر نصية تُكتب بجوار المخرج (أو [] للا شيء)."""
    cx, cw = 470, 120              # يسار العمود وعرضه
    ytop, ybot = 50, 520
    b = '<defs><linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dbe9f7"/><stop offset="1" stop-color="#f6c08a"/></linearGradient></defs>'
    fill = 'url(#tg)' if gradient else '#eef1f5'
    b += f'<rect x="{cx}" y="{ytop}" width="{cw}" height="{ybot - ytop}" rx="14" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
    outs = [ytop + 30, 145, 225, 305, 385, ybot - 25]
    for y in outs[1:5]:
        y2 = y + 22
        b += L(cx + 8, y2, cx + cw - 30, y2, '#7a8392', 2) + L(cx + 30, y2 + 20, cx + cw - 8, y2 + 20, '#7a8392', 2)
    for i, y in enumerate(outs):
        b += f'<rect x="{cx - 70}" y="{y - 7}" width="70" height="14" fill="#c9ced6" stroke="{INK}" stroke-width="1.5"/>'
        b += ARROW(cx - 72, y, cx - 115, y, RED, 2.5)
        lines = labels[i]
        for j, t in enumerate(lines):
            yy = y - (len(lines) - 1) * 10 + j * 20 + 5
            if any('؀' <= ch <= 'ۿ' for ch in t): b += T(cx - 125, yy, t, 15, 'end', weight='bold' if j == 0 else 'normal')
            else: b += LT(cx - 125, yy, t, 15, 'end')
    if show_bottom_temp: b += LT(cx + cw / 2, ybot - 60, '400°C', 16, weight='bold', color=RED)
    # الفرن والأنبوب الناقل للبخار
    fx, fy, fw, fh = 680, 330, 130, 150
    b += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="10" fill="#f3e3d3" stroke="{INK}" stroke-width="2.5"/>'
    b += f'<path d="M{fx + 20},{fy + fh - 20} q15,-25 30,0 t30,0 t30,0" fill="none" stroke="{RED}" stroke-width="3"/>'
    b += f'<path d="M{fx + 30},{fy + fh - 45} l8,-22 l8,22 M{fx + 62},{fy + fh - 45} l8,-22 l8,22" fill="none" stroke="#d9822b" stroke-width="2.5"/>'
    b += f'<path d="M{fx + fw / 2},{fy} L{fx + fw / 2},{fy - 40} L{cx + cw + 6},{fy - 40} L{cx + cw + 6},{ybot - 95}" fill="none" stroke="#9a6a3a" stroke-width="10"/>'
    b += f'<path d="M{cx + cw + 6},{ybot - 95} L{cx + cw - 2},{ybot - 95}" stroke="#9a6a3a" stroke-width="10"/>'
    b += ARROW(fx + fw + 45, fy + fh - 30, fx + fw + 4, fy + fh - 30, INK, 2.5)
    if furnace_label:
        b += T(fx + fw / 2, fy + fh + 26, 'فرن', 16, weight='bold')
        b += T(fx + fw + 22, fy + fh - 42, 'نفط خام', 14)
    b += L(cx - 20, ybot + 2, w - 20, ybot + 2, MUTED, 1.5)
    save(name, svg(w, h, b))

def fig_towers():
    full = [[n, t, r] if t else [n] for n, t, r in FRACTIONS]
    full[5] = ['المخلفات']
    tower('c4-l1b-tower-full.svg', full)
    tower('c4-l1b-tower-numbered.svg', [[f'({i + 1})'] for i in range(6)], show_bottom_temp=False, gradient=False)

# ---------------------------------------------------------------- منحنى درجة الغليان وعدد ذرات الكربون
def fig_bp_graph():
    data = [(1, -161.7, 'ميثان'), (3, -42.1, 'بروبان'), (4, -0.5, 'بيوتان'), (6, 68.7, 'هكسان'), (8, 125.7, 'أوكتان')]
    w, h = 620, 420
    X0, Y0, X1, Y1 = 90, 350, 590, 40
    tmin, tmax = -200, 150
    def px(n): return X0 + (n - 0) / 9 * (X1 - X0)
    def py(t): return Y0 - (t - tmin) / (tmax - tmin) * (Y0 - Y1)
    b = ''
    for t in range(-200, 151, 50):
        b += L(X0, py(t), X1, py(t), '#e3e7ee', 1) + LT(X0 - 8, py(t) + 5, str(t), 13, 'end', MUTED)
    for n in range(0, 10):
        b += L(px(n), Y0, px(n), Y0 + 6, INK, 1.5) + LT(px(n), Y0 + 24, str(n), 14)
    b += L(X0, Y0, X1, Y0, INK, 2) + L(X0, Y0, X0, Y1, INK, 2)
    b += L(X0, py(0), X1, py(0), MUTED, 1.2, '6 4')
    pts = ' '.join(f'{px(n):.1f},{py(t):.1f}' for n, t, _ in data)
    b += f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>'
    for n, t, lab in data:
        b += f'<circle cx="{px(n):.1f}" cy="{py(t):.1f}" r="6" fill="{BLUE}" stroke="{INK}"/>'
        b += T(px(n) - 10, py(t) - 12, lab, 13, 'end')
    b += T((X0 + X1) / 2, Y0 + 52, 'عدد ذرات الكربون في الجزيء', 15, weight='bold')
    b += f'<text transform="translate({X0 - 58},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="15" fill="{INK}" font-weight="bold" {FONT}>درجة الغليان (°C)</text>'
    save('c4-l1b-bp-graph.svg', svg(w, h, b))

# ---------------------------------------------------------------- التكسير الحراري
def carbon_row(x0, y, n, r=11, gap=26, double_at=None):
    s = ''
    for i in range(n - 1):
        xa, xb = x0 + i * gap, x0 + (i + 1) * gap
        if double_at == i:
            s += L(xa, y - 4, xb, y - 4, INK, 2.2) + L(xa, y + 4, xb, y + 4, INK, 2.2)
        else:
            s += L(xa, y, xb, y, INK, 2.2)
    for i in range(n):
        s += f'<circle cx="{x0 + i * gap}" cy="{y}" r="{r}" fill="#3a3f47" stroke="#111" stroke-width="1"/>'
    return s

def fig_cracking(name, arrow_text):
    w, h = 880, 250
    b = ''
    b += carbon_row(40, 110, 16)
    b += LT(40 + 7.5 * 26, 160, 'C₁₆H₃₄', 20, weight='bold')
    ax0, ax1 = 455, 560
    b += ARROW(ax0, 110, ax1, 110, INK, 3)
    for j, t in enumerate(arrow_text):
        b += T((ax0 + ax1) / 2, 84 - (len(arrow_text) - 1 - j) * 20, t, 14 if t != '؟' else 26, weight='bold')
    b += carbon_row(600, 75, 8) + LT(600 + 3.5 * 26, 118, 'C₈H₁₈', 20, weight='bold')
    b += carbon_row(600, 165, 8, double_at=0) + LT(600 + 3.5 * 26, 208, 'C₈H₁₆', 20, weight='bold')
    b += LT(600 + 7 * 26 + 40, 125, '+', 26, weight='bold') if False else ''
    b += T(w / 2, 238, 'الكرات تمثل ذرات الكربون فقط (ذرات الهيدروجين غير مرسومة)', 13, color=MUTED)
    save(name, svg(w, h, b))

# ---------------------------------------------------------------- رقم الأوكتان
def fig_octane_scale():
    w, h = 820, 240
    X0, X1, Y = 60, 780, 130
    vmin, vmax = 85, 112
    def px(v): return X0 + (v - vmin) / (vmax - vmin) * (X1 - X0)
    b = ARROW(X0, Y, X1 + 20, Y, INK, 2.5)
    for v in range(85, 112, 5):
        b += L(px(v), Y - 6, px(v), Y + 6, MUTED, 1.5) + LT(px(v), Y + 26, str(v), 13, color=MUTED)
    marks = [(89, 'جازولين متوسط الدرجة', 'up'), (91, 'جازولين', 'down'), (95, 'جازولين', 'down2'), (100, 'وقود الطائرات', 'up'), (110, 'وقود سيارات السباق', 'up')]
    for v, lab, pos in marks:
        x = px(v)
        b += f'<circle cx="{x:.1f}" cy="{Y}" r="8" fill="{BLUE}" stroke="{INK}"/>'
        if pos == 'up':
            b += L(x, Y - 10, x, Y - 45, BLUE, 1.5) + LT(x, Y - 52, str(v), 18, weight='bold') + T(x, Y - 76, lab, 14)
        else:
            dy = 62 if pos == 'down' else 62
            b += L(x, Y + 10, x, Y + 40, BLUE, 1.5) + LT(x, Y + 60, str(v), 18, weight='bold')
    b += T((px(91) + px(95)) / 2, Y + 88, 'نوعا الجازولين في المملكة العربية السعودية', 14)
    b += T(X1 - 10, Y + 44, 'رقم الأوكتان', 15, 'end', weight='bold')
    save('c4-l1b-octane-scale.svg', svg(w, h, b))

def cylinder(x, y, piston_frac, spark, flame, label, sub):
    """أسطوانة محرك: x,y أعلى اليسار. piston_frac: موضع المكبس (0 أعلى، 1 أسفل)."""
    cw, ch = 140, 230
    s = f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="#f7f8fa" stroke="{INK}" stroke-width="3"/>'
    # شمعة الاحتراق
    s += f'<rect x="{x + cw / 2 - 9}" y="{y - 40}" width="18" height="40" fill="#c9ced6" stroke="{INK}" stroke-width="2"/>'
    s += L(x + cw / 2, y, x + cw / 2, y + 12, INK, 3)
    if spark:
        for a in range(0, 360, 45):
            r1, r2 = 6, 16
            s += L(f'{x + cw / 2 + r1 * math.cos(math.radians(a)):.1f}', f'{y + 18 + r1 * math.sin(math.radians(a)):.1f}',
                   f'{x + cw / 2 + r2 * math.cos(math.radians(a)):.1f}', f'{y + 18 + r2 * math.sin(math.radians(a)):.1f}', '#e0a100', 2.5)
    py_ = y + 40 + piston_frac * 120
    if flame:
        fx, fy = flame
        s += f'<path d="M{x + fx},{y + fy - 26} l9,16 l14,-6 l-6,14 l16,6 l-16,6 l6,14 l-14,-6 l-9,16 l-9,-16 l-14,6 l6,-14 l-16,-6 l16,-6 l-6,-14 l14,6 Z" fill="#f28c28" stroke="#b03a2e" stroke-width="1.5"/>'
    s += f'<rect x="{x + 4}" y="{py_}" width="{cw - 8}" height="46" fill="#9aa1ab" stroke="{INK}" stroke-width="2"/>'
    s += L(x + cw / 2, py_ + 46, x + cw / 2, y + ch + 30, INK, 6)
    s += ARROW(x + cw + 26, py_ + 40, x + cw + 26, py_ - 10, BLUE, 2.5)
    s += panel_label(x + cw / 2, y + ch + 58, label)
    for j, t in enumerate(sub): s += T(x + cw / 2, y + ch + 84 + j * 20, t, 14)
    return s

def fig_knock():
    w, h = 640, 420
    b = cylinder(100, 60, 0.95, False, (70, 70), '(1)', ['يشتعل الخليط والمكبس ما زال', 'في أسفل الأسطوانة، قبل الشرارة'])
    b += cylinder(400, 60, 0.05, True, None, '(2)', ['يشتعل الخليط بالشرارة', 'والمكبس في أعلى موضعه'])
    b += T(w / 2, 26, 'السهم الأزرق: اتجاه حركة المكبس', 13, color=MUTED)
    save('c4-l1b-knock.svg', svg(w, h, b))

# ---------------------------------------------------------------- القوة الحيوية
def fig_vitalism():
    w, h = 900, 200
    bw, bh, gap = 190, 110, 32
    xs = [w - 20 - bw - i * (bw + gap) for i in range(4)]
    texts = [['مركبات تُستخلص من', 'المخلوقات الحية فقط،', 'فسُمّيت «عضوية»'],
             ['عجز العلماء عن', 'تحضيرها في المختبر'],
             ['؟'],
             ['تحضير مركبات عضوية', 'في المختبر من مواد', 'غير عضوية']]
    b = ''
    for i, (x, t) in enumerate(zip(xs, texts)):
        q = t == ['؟']
        b += box(x, 50, bw, bh, t, '#fdf3e7' if q else '#eef3fa', '#c76a1c' if q else BLUE, 26 if q else 15)
        if i < 3: b += ARROW(x - 4, 105, x - gap + 4, 105, INK)
    b += T(w / 2, 28, 'تطوّر فهم العلماء للمركبات العضوية في القرن التاسع عشر', 15, weight='bold')
    save('c4-l1b-vitalism.svg', svg(w, h, b))

if __name__ == '__main__':
    fig_sat_unsat(); fig_butane_butene(); fig_bromine_tubes(); fig_bromine_bars(); fig_towers(); fig_bp_graph()
    fig_cracking('c4-l1b-cracking-q.svg', ['؟'])
    fig_cracking('c4-l1b-cracking.svg', ['حرارة + عامل مساعد', 'دون أكسجين'])
    fig_octane_scale(); fig_knock(); fig_vitalism()
