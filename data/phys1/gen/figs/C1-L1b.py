import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 1-1 (الأهداف O13–O24): خرائط مفاهيم الطريقة العلمية، ورسوم البيانات وخط المواءمة الأفضل.

FULL = ['تحديد المشكلة', 'جمع المعلومات', 'وضع الفرضيات', 'إجراء التجارب لاختبار الفرضية',
        'تسجيل النتائج وتحليلها', 'الاستنتاج', 'النتائج تدعم الفرضية', 'النتائج لا تدعم الفرضية']
ARR = ['تكرار', 'تعديل الفرضية']


def concept_map(name, boxes, arrows=ARR):
    """خريطة مفاهيم الطريقة العلمية. boxes = 8 نصوص (6 في العمود + يسار + يمين)؛ النص الذي يبدأ بـ '#' يُرسم مربعًا فارغًا برقمه.
    arrows = [نص سهم اليسار (إلى المربع 4), نص سهم اليمين (إلى المربع 3)]."""
    w, h = 640, 440; bx, bw, bh = 190, 260, 40; ys = [20 + i * 66 for i in range(6)]; b = ''

    def box(x, y, ww, hh, s):
        if s.startswith('#'):
            return f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" fill="#fff" stroke="{INK}" stroke-width="2" stroke-dasharray="6 4"/>' + T(x + ww / 2, y + hh / 2 + 6, f'( {s[1:]} )', 17, color=BLUE, weight='bold')
        return RECT(x, y, ww, hh) + T(x + ww / 2, y + hh / 2 + 5, s, 14)
    for i in range(6):
        b += box(bx, ys[i], bw, bh, boxes[i])
        if i < 5: b += ARROW(bx + bw / 2, ys[i] + bh, bx + bw / 2, ys[i + 1], RED, 2, 9)
    # الصندوقان الجانبيان
    sw, sh, sy = 150, 56, ys[5] - 8
    lx, rx = 15, w - 15 - sw
    b += box(lx, sy, sw, sh, boxes[6]) + box(rx, sy, sw, sh, boxes[7])
    cy6 = ys[5] + bh / 2
    b += ARROW(bx, cy6, lx + sw, cy6, RED, 2, 9) + ARROW(bx + bw, cy6, rx, cy6, RED, 2, 9)
    # يسار: من الصندوق إلى المربع 4 (تكرار)
    lcx = lx + sw / 2; y4 = ys[3] + bh / 2
    b += L(lcx, sy, lcx, y4, RED, 2) + ARROW(lcx, y4, bx, y4, RED, 2, 9)
    # يمين: من الصندوق إلى المربع 3 (تعديل الفرضية)
    rcx = rx + sw / 2; y3 = ys[2] + bh / 2
    b += L(rcx, sy, rcx, y3, RED, 2) + ARROW(rcx, y3, bx + bw, y3, RED, 2, 9)

    def alabel(x, y, s):
        if s.startswith('#'): return T(x, y, f'( {s[1:]} )', 16, color=BLUE, weight='bold')
        return T(x, y, s, 14, color=RED, weight='bold')
    b += alabel((lcx + bx) / 2 - 8, y4 - 10, arrows[0]) + alabel((rcx + bx + bw) / 2 + 8, y3 - 10, arrows[1])
    save(name, svg(w, h, b))


def scatter_fit(name, pts, line, xr, yr, xl, yl, xs, ys, w=520, h=360):
    """نقاط بيانات مع خط مواءمة (line = [(x,y),(x,y)])."""
    return graph(name, [{'pts': line, 'color': BLUE, 'w': 2.5}, {'pts': pts, 'color': RED, 'w': 0, 'dots': True}],
                 xr, yr, xl, yl, xs, ys, w, h)


def panels(name, pts, lines, xr=(0, 7), yr=(0, 20)):
    """أربع لوحات صغيرة: النقاط نفسها وخط مختلف في كل لوحة (lines: قائمة من 4 قوائم نقاط)."""
    W, H = 640, 470; pw, ph = 300, 215; b = ''
    for k, ln in enumerate(lines):
        ox = 15 + (k % 2) * 320; oy = 10 + (k // 2) * 235
        L0, R0, T0, B0 = ox + 40, ox + pw - 10, oy + 30, oy + ph - 25
        X = lambda x: L0 + (x - xr[0]) / (xr[1] - xr[0]) * (R0 - L0)
        Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
        b += f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="none" stroke="{GRID}" stroke-width="1.5"/>'
        for gx in range(xr[0], xr[1] + 1): b += L(X(gx), T0, X(gx), B0, GRID, 1)
        for gy in range(yr[0], yr[1] + 1, 4): b += L(L0, Y(gy), R0, Y(gy), GRID, 1)
        b += ARROW(L0, B0, R0 + 8, B0, INK, 1.6, 8) + ARROW(L0, B0, L0, T0 - 8, INK, 1.6, 8)
        for gx in range(0, xr[1] + 1, 2): b += T(X(gx), B0 + 15, str(gx), 11, color=MUTED)
        for gy in range(0, yr[1] + 1, 4): b += T(L0 - 6, Y(gy) + 4, str(gy), 11, 'end', MUTED)
        b += T(R0 + 2, B0 - 6, 'x', 13, 'end', MUTED, italic=True) + T(L0 + 10, T0 - 2, 'y', 13, 'start', MUTED, italic=True)
        poly = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in ln)
        b += f'<polyline points="{poly}" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-linejoin="round"/>'
        b += ''.join(DOT(X(x), Y(y), 4, RED) for x, y in pts)
        b += T(ox + pw - 18, oy + 22, f'({k + 1})', 15, weight='bold')
    save(name, svg(W, H, b))


if __name__ == '__main__':
    # ---- O20 خرائط الطريقة العلمية ----
    m = FULL[:]; m[3] = '#1'; concept_map('c1l1-map-step4.svg', m)
    m = FULL[:]; m[4] = '#1'; concept_map('c1l1-map-step5.svg', m)
    m = FULL[:]; m[6] = '#2'; m[7] = '#1'; concept_map('c1l1-map-rightbox.svg', m)
    concept_map('c1l1-map-repeat.svg', FULL, ['#1', 'تعديل الفرضية'])
    m = FULL[:]; m[0] = '#1'; concept_map('c1l1-map-step1.svg', m)
    m = FULL[:]; m[1] = '#1'; m[3] = '#2'; m[4] = '#3'; m[6] = '#4'; m[7] = '#5'; concept_map('c1l1-map-blank5.svg', m)
    # خريطة طالب فيها خطآن: تبديل المربعين 3 و4، وتبديل الصندوقين الجانبيين
    m = FULL[:]; m[2], m[3] = m[3], m[2]; m[6], m[7] = m[7], m[6]; concept_map('c1l1-map-errors.svg', m)
    # ---- O24 التمثيل البياني وخط المواءمة الأفضل ----
    scatter_fit('c1l1-fit-slope.svg', [(5, 26), (10, 49), (15, 76), (20, 99), (25, 126), (30, 150)], [(0, 0), (30, 150)],
                (0, 30), (0, 160), 'القوة F (N)', 'المسافة d (cm)', 5, 20)
    scatter_fit('c1l1-fit-spring.svg', [(50, 14.6), (100, 17.0), (150, 19.4), (200, 22.1), (250, 24.4)], [(0, 12.0), (250, 24.5)],
                (0, 250), (0, 28), 'الكتلة المعلّقة m (g)', 'طول النابض L (cm)', 50, 4)
    scatter_fit('c1l1-fit-volume.svg', [(10, 78), (20, 162), (30, 238), (40, 322), (50, 398)], [(0, 0), (50, 400)],
                (0, 50), (0, 400), 'الحجم V (cm^3)', 'الكتلة m (g)', 10, 40)
    scatter_fit('c1l1-fit-temp.svg', [(0, 20.0), (1, 24.2), (2, 27.8), (3, 32.1), (4, 35.9), (5, 40.0)], [(0, 20.0), (5, 40.0)],
                (0, 6), (0, 50), 'الزمن t (min)', 'درجة الحرارة T (°C)', 1, 5)
    P = [(1, 2.6), (2, 5.6), (3, 6.6), (4, 9.6), (5, 10.6), (6, 13.4)]
    panels('c1l1-fit-panels.svg', P, [P, [(0, 0.87), (6.6, 14.44)], [(0, 0), (6.4, 17.92)], [(1.3, 0.24), (6.6, 15.08)]])
