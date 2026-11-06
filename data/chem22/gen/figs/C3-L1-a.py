# رسوم الدرس 3-1 (حالة الاتزان الديناميكي): منحنيات التركيز–الزمن حتى الاتزان، وسرعتا التفاعلين الأمامي والعكسي،
# ورسوم الجسيمات لحساب Keq، والاتزان غير المتجانس في دورق مغلق.
# التشغيل: python3 data/chem22/gen/figs/C3-L1-a.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *

ORANGE = '#d9822b'; PURPLE = '#6a4c9c'; GRAY = '#3a3a3a'


def ease(c0, c1, t, teq):
    """تركيز يتغير من c0 إلى c1 ويثبت تمامًا عند t ≥ teq (تناقص سرعة التغير تدريجيًّا)."""
    if t >= teq: return c1
    return c1 + (c0 - c1) * (1 - t / teq) ** 2


def graph(name, curves, xmax, ymax=1.0, yticks=None, xticks=None, marks=(), xlabel='الزمن', ylabel='التركيز (mol/L)',
          w=560, h=340, ox=0, standalone=True, panel_label=None, ydec=2, rpad=95, label_dy=None, grid=True):
    """curves = [(label, f(t), color)]؛ yticks: قيم عددية على المحور الرأسي (None = بلا أرقام)؛
    xticks: قيم عددية على المحور الأفقي (None = بلا أرقام)؛ marks = [(t, 'نص')] خطوط رأسية متقطعة مسماة."""
    X0, Y0, X1, Y1 = ox + 78, h - 50, ox + w - rpad, 40 if panel_label else 25
    def px(t): return X0 + t / xmax * (X1 - X0 - 10)
    def py(c): return Y0 - c / ymax * (Y0 - Y1 - 15)
    b = ''
    if yticks:
        for v in yticks:
            if grid: b += L(X0, py(v), px(xmax), py(v), '#dfe3ea', 1)
            b += L(X0 - 5, py(v), X0, py(v)) + T(X0 - 8, py(v) + 5, f'{v:.{ydec}f}', 12, 'end')
    if xticks:
        for v in xticks:
            if grid: b += L(px(v), Y0, px(v), py(ymax), '#dfe3ea', 1)
            b += T(px(v), Y0 + 18, f'{v:g}', 12)
    for t, lab in marks:
        b += L(px(t), Y0, px(t), py(ymax) - 2, MUTED, 1.3, '5 4') + T(px(t), Y0 + 18, lab, 14, weight='bold')
    b += ARROW(X0, Y0, X1 + 15, Y0) + ARROW(X0, Y0, X0, Y1 - 5)
    b += T((X0 + X1) / 2, h - 8, xlabel, 14, weight='bold')
    b += f'<text transform="translate({X0 - (55 if yticks else 22)},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT}>{esc(ylabel)}</text>'
    for k, (lab, f, col) in enumerate(curves):
        n = 120
        pts = ' '.join(f'{px(xmax * i / n):.1f},{py(f(xmax * i / n)):.1f}' for i in range(n + 1))
        b += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3" stroke-linejoin="round"/>'
        dy = (label_dy or {}).get(lab, 0)
        b += T(px(xmax) + 8, py(f(xmax)) + 5 + dy, lab, 14, 'start', col, 'bold')
    if panel_label: b += T(ox + w / 2, 22, panel_label, 16, weight='bold')
    if standalone: save(name, svg(w, h, b))
    return b


def molecule(x, y, kinds, r=9):
    """جزيء ثنائي الذرة أفقي: kinds = ('H','I') ..."""
    col = {'H': '#9fc5e8', 'I': PURPLE, 'A': RED, 'B': BLUE}
    s = ''
    for k, kd in enumerate(kinds):
        rr = r if kd != 'H' else r - 2
        s += f'<circle cx="{x + k * (r + rr - 3):.1f}" cy="{y:.1f}" r="{rr}" fill="{col[kd]}" stroke="{INK}" stroke-width="1"/>'
    return s


def particle_box(name):
    """خليط اتزان H₂ + I₂ ⇌ 2HI في وعاء حجمه 1.0 L: جزيئان H₂، وجزيئان I₂، وثمانية جزيئات HI؛ كل جزيء يمثل 0.10 mol."""
    w, h = 560, 300
    b = f'<rect x="30" y="30" width="270" height="230" fill="#f7f9fc" stroke="{INK}" stroke-width="2.5" rx="6"/>'
    hh = [(70, 70), (230, 200)]
    ii = [(200, 80), (80, 215)]
    hi = [(130, 60), (250, 120), (60, 140), (150, 130), (210, 160), (120, 190), (160, 235), (240, 240)]
    for x, y in hh: b += molecule(x, y, 'HH')
    for x, y in ii: b += molecule(x, y, 'II')
    for x, y in hi: b += molecule(x, y, 'HI')
    b += T(170, 285, 'حجم الوعاء:', 14, 'end') + T(176, 285, '1.0 L', 14, 'start')
    # المفتاح
    kx = 330
    b += f'<rect x="{kx}" y="40" width="210" height="190" fill="none" stroke="{MUTED}" stroke-width="1" rx="6"/>'
    b += T(kx + 105, 64, 'المفتاح', 14, weight='bold')
    for k, (kinds, lab) in enumerate([('HH', 'H₂'), ('II', 'I₂'), ('HI', 'HI')]):
        y = 100 + k * 38
        b += molecule(kx + 40, y, kinds) + T(kx + 110, y + 5, lab, 15, 'start')
    b += T(kx + 150, 212, 'كل جزيء يمثل', 13, 'end') + T(kx + 156, 212, '0.10 mol', 13, 'start')
    save(name, svg(w, h, b))


def flask(name):
    """دورق مغلق فيه إيثانول سائل وبخاره، وسهمان: التبخر (لأعلى) والتكثف (لأسفل)."""
    w, h = 460, 330
    b = ''
    # جسم الدورق: عنق + كرة
    b += f'<path d="M 200 40 L 200 120 C 120 140 90 190 90 230 C 90 290 150 315 230 315 C 310 315 370 290 370 230 C 370 190 340 140 260 120 L 260 40 Z" fill="#fbfcfe" stroke="{INK}" stroke-width="2.5"/>'
    b += f'<rect x="192" y="22" width="76" height="22" fill="#b07a4a" stroke="{INK}" stroke-width="1.5" rx="3"/>'
    # السائل
    b += f'<path d="M 96 250 L 364 250 C 358 292 305 312 230 312 C 155 312 102 292 96 250 Z" fill="#cfe2f3" stroke="none"/>'
    b += L(96, 250, 364, 250, BLUE, 2)
    # جزيئات البخار
    for x, y in [(170, 160), (230, 140), (290, 170), (150, 205), (250, 200), (320, 215), (205, 180)]:
        b += f'<circle cx="{x}" cy="{y}" r="7" fill="{ORANGE}" stroke="{INK}" stroke-width="1"/>'
    for x, y in [(130, 270), (170, 285), (215, 268), (260, 288), (300, 268), (335, 280), (190, 300), (240, 300), (285, 298)]:
        b += f'<circle cx="{x}" cy="{y}" r="7" fill="{ORANGE}" stroke="{INK}" stroke-width="1" opacity="0.9"/>'
    b += ARROW(130, 248, 130, 200, RED, 2.4) + ARROW(335, 200, 335, 246, BLUE, 2.4)
    b += T(112, 215, 'تبخر', 13, 'end', RED, 'bold') + T(355, 215, 'تكثف', 13, 'start', BLUE, 'bold')
    b += T(400, 170, 'C₂H₅OH(g)', 14, 'start') + L(330, 175, 395, 168, MUTED, 1)
    b += T(400, 290, 'C₂H₅OH(l)', 14, 'start') + L(360, 280, 395, 286, MUTED, 1)
    save(name, svg(w + 70, h, b))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    TEQ = 6.0
    # 1) N₂ + 3H₂ ⇌ 2NH₃ (نوعي): [N₂] 1.0→0.6، [H₂] 3.0→1.8، [NH₃] 0→0.8؛ وثلاث علامات زمنية
    graph('c3-l1a-conc-nh3.svg',
          [('[H₂]', lambda t: ease(3.0, 1.8, t, TEQ), BLUE), ('[NH₃]', lambda t: ease(0.0, 0.8, t, TEQ), PURPLE),
           ('[N₂]', lambda t: ease(1.0, 0.6, t, TEQ), RED)],
          xmax=10, ymax=3.2, marks=[(2.5, 't₁'), (TEQ, 't₂'), (9, 't₃')], label_dy={'[NH₃]': -6, '[N₂]': 8})
    # 2) سرعتا التفاعلين الأمامي والعكسي حتى الاتزان (مسماتان)
    graph('c3-l1a-rates.svg',
          [('الأمامي', lambda t: ease(1.0, 0.45, t, TEQ), RED), ('العكسي', lambda t: ease(0.0, 0.45, t, TEQ), BLUE)],
          xmax=10, ymax=1.1, marks=[(2.5, 't₁'), (TEQ, 't₂')], ylabel='سرعة التفاعل', label_dy={'الأمامي': -12, 'العكسي': 12})
    # 3) المنحنيان نفساهما دون تسمية (س) و(ص)
    graph('c3-l1a-rates-xy.svg',
          [('(س)', lambda t: ease(0.0, 0.45, t, TEQ), BLUE), ('(ص)', lambda t: ease(1.0, 0.45, t, TEQ), RED)],
          xmax=10, ymax=1.1, marks=[(TEQ, 't₂')], ylabel='سرعة التفاعل', label_dy={'(س)': 12, '(ص)': -12})
    # 4) N₂O₄ ⇌ 2NO₂ بقيم عددية: [N₂O₄] 0.100→0.040، [NO₂] 0→0.120، الاتزان عند 60 s
    graph('c3-l1a-conc-n2o4.svg',
          [('[NO₂]', lambda t: ease(0.0, 0.120, t, 60), BLUE), ('[N₂O₄]', lambda t: ease(0.100, 0.040, t, 60), RED)],
          xmax=100, ymax=0.14, yticks=[0.02 * k for k in range(8)], xticks=[0, 20, 40, 60, 80, 100], ydec=3,
          xlabel='الزمن (s)', w=580)
    # 5) A ⇌ B: منحنيان يتقاطعان قبل الاتزان (t₁ التقاطع، t₂ ما زال يتغير، t₃ ثابت)
    graph('c3-l1a-conc-cross.svg',
          [('[A]', lambda t: ease(1.0, 0.3, t, TEQ), RED), ('[B]', lambda t: ease(0.0, 0.7, t, TEQ), BLUE)],
          xmax=10, ymax=1.1, yticks=[0.1 * k for k in range(11)], ydec=1,
          marks=[(6 * (1 - math.sqrt(2 / 7)), 't₁'), (4.5, 't₂'), (8.5, 't₃')], grid=True)
    # 6) لوحتان (س) و(ص) لتفاعلين من النوع A ⇌ B عند درجة الحرارة نفسها
    b = graph('', [('[B]', lambda t: ease(0.0, 0.8, t, TEQ), BLUE), ('[A]', lambda t: ease(1.0, 0.2, t, TEQ), RED)],
              xmax=10, ymax=1.1, yticks=[0.2 * k for k in range(6)], ydec=1, w=400, h=300, standalone=False, panel_label='(س)', rpad=55)
    b += graph('', [('[A]', lambda t: ease(1.0, 0.75, t, TEQ), RED), ('[B]', lambda t: ease(0.0, 0.25, t, TEQ), BLUE)],
               xmax=10, ymax=1.1, yticks=[0.2 * k for k in range(6)], ydec=1, w=400, h=300, ox=400, standalone=False, panel_label='(ص)', rpad=55)
    b += L(400, 10, 400, 290, MUTED, 1, '4 4')
    save('c3-l1a-two-eq.svg', svg(800, 300, b))
    # 7) رسم الجسيمات لخليط الاتزان H₂ + I₂ ⇌ 2HI
    particle_box('c3-l1a-particles-hi.svg')
    # 8) دورق الإيثانول المغلق (اتزان غير متجانس)
    flask('c3-l1a-flask-ethanol.svg')
