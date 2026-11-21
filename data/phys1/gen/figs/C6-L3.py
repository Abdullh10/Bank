import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 6-3 (السرعة المتجهة النسبية) — الأهداف O01–O05
# متجهات السرعة حمراء C_VEL مرسومة بمقياس رسم (بالدالة vectors)، ولا يُرسم المتجه المحصل حين يكون هو المطلوب.
# الرموز كالكتاب: v بخط عريض مائل وحروفه السفلية مائلة (v_{b/w}، v_{m/b}، v_{t/E})، أو حروف سفلية عربية كالشكل 6-10.
import math


def VS(x, y, sub, color=C_VEL, size=18, anchor='middle'):
    """رمز السرعة المتجهة النسبية كالكتاب: v عريض مائل، وحرف سفلي مائل غير عريض مثل b/w."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" {MATHFONT}>'
            f'<tspan font-weight="bold" font-style="italic">v</tspan>'
            f'<tspan dy="0.3em" font-size="{int(size * 0.68)}" font-style="italic">{esc(sub)}</tspan></text>')


def VA(x, y, sub, color=C_VEL, size=18):
    """v عريض مائل وبعده حرف سفلي عربي (كالشكل 6-10). x = موضع الحرف v."""
    return V(x, y, 'v', color, size) + T(x + 7, y + 6, sub, 11, 'start', color)


def compass(x, y, n=40):
    return (ARROW(x, y, x, y - n, INK, 1.8) + T(x, y - n - 7, 'الشمال', 13) +
            ARROW(x, y, x + n, y, INK, 1.8) + T(x + n + 5, y + 5, 'الشرق', 13, 'start'))


def P(origin, unit, p): return (origin[0] + p[0] * unit, origin[1] - p[1] * unit)


# ---------- O01 ----------
# mcq1: قارب 5.0 m/s شمالًا بالنسبة إلى الماء، وتيار 2.0 m/s شرقًا (رأس بذيل)، دون المحصلة
o, u = (150, 270), 44
vectors('c6l3-o01-boat.svg', [
    {'from': (0, 0), 'to': (0, 5), 'color': C_VEL},
    {'from': (0, 5), 'to': (2, 5), 'color': C_VEL}], w=360, h=310, unit=u, origin=o, grid=False, axes=False,
    extra=VS(o[0] - 34, o[1] - 2.5 * u, 'b/w') + T(o[0] - 34, o[1] - 2.5 * u + 24, '5.0 m/s', 14, color=C_VEL) +
    VS(o[0] + u, o[1] - 5 * u - 16, 'w/E') + T(o[0] + u, o[1] - 5 * u + 22, '2.0 m/s', 14, color=C_VEL) +
    DOT(o[0], o[1], 4, INK) + compass(270, 280, 36))

# mcq4: شبكة، كل مربع 1.0 m/s؛ v_b/w من (0,0) إلى (2,4)، وv_w/E من (2,4) إلى (5,4)
o, u = (60, 250), 44
vectors('c6l3-o01-grid.svg', [
    {'from': (0, 0), 'to': (2, 4), 'color': C_VEL},
    {'from': (2, 4), 'to': (5, 4), 'color': C_VEL}], w=340, h=290, unit=u, origin=o, grid=True, axes=False,
    extra=VS(o[0] + 1 * u - 26, o[1] - 2 * u - 4, 'b/w') + VS(o[0] + 3.5 * u, o[1] - 4 * u - 12, 'w/E') +
    ARROW(o[0], o[1], o[0] + 5.6 * u, o[1], MUTED, 1.4) + ARROW(o[0], o[1], o[0], o[1] - 5.3 * u, MUTED, 1.4) +
    T(o[0] + 5.6 * u, o[1] + 20, '+x', 14, 'end', MUTED, italic=True) + T(o[0] + 8, o[1] - 5.3 * u + 10, '+y', 14, 'start', MUTED, italic=True) +
    DOT(o[0], o[1], 4, INK))

# mcq6: طائرة 220 km/h شرقًا بالنسبة إلى الهواء، ورياح 50.0 km/h نحو الشمال الشرقي (مقياس 1 وحدة = 20 km/h)
o, u = (40, 200), 20
wx, wy = 2.5 * math.cos(math.radians(45)), 2.5 * math.sin(math.radians(45))
vectors('c6l3-o01-wind45.svg', [
    {'from': (0, 0), 'to': (11, 0), 'color': C_VEL},
    {'from': (11, 0), 'to': (11 + wx, wy), 'color': C_VEL}], w=440, h=250, unit=u, origin=o, grid=False, axes=False,
    extra=VA(o[0] + 70, o[1] + 26, 'الطائرة بالنسبة إلى الهواء') + T(o[0] + 110, o[1] - 10, '2.20×10² km/h', 14, color=C_VEL) +
    VA(o[0] + 11 * u + 20, o[1] - wy * u - 22, 'الهواء بالنسبة إلى الأرض') + T(o[0] + 11 * u - 22, o[1] - wy * u / 2 - 6, '50.0 km/h', 14, color=C_VEL) +
    L(o[0] + 11 * u, o[1], o[0] + 11 * u + 50, o[1], MUTED, 1.2, '4 3') +
    f'<path d="M {o[0] + 11 * u + 34:.1f} {o[1]:.1f} A 34 34 0 0 0 {o[0] + 11 * u + 34 * math.cos(math.radians(45)):.1f} {o[1] - 34 * math.sin(math.radians(45)):.1f}" fill="none" stroke="{INK}" stroke-width="1.4"/>' +
    T(o[0] + 11 * u + 50, o[1] - 10, '‎45°', 13, 'start') + DOT(o[0], o[1], 4, INK) + compass(60, 100, 36))

# mcq7: قارب 3.0 m/s شرقًا بالنسبة إلى الماء، وكرة 1.5 m/s شمالًا بالنسبة إلى القارب (رأس بذيل)
o, u = (50, 200), 60
vectors('c6l3-o01-angle.svg', [
    {'from': (0, 0), 'to': (3, 0), 'color': C_VEL},
    {'from': (3, 0), 'to': (3, 1.5), 'color': C_VEL}], w=360, h=250, unit=u, origin=o, grid=False, axes=False,
    extra=VS(o[0] + 1.5 * u, o[1] + 28, 'b/w') + T(o[0] + 1.5 * u, o[1] - 10, '3.0 m/s', 14, color=C_VEL) +
    VS(o[0] + 3 * u + 30, o[1] - 0.75 * u + 2, 'm/b') + T(o[0] + 3 * u + 32, o[1] - 0.75 * u + 24, '1.5 m/s', 14, color=C_VEL) +
    DOT(o[0], o[1], 4, INK) + compass(60, 100, 36))

# essay3: طائرة 180 km/h غربًا بالنسبة إلى الهواء، ورياح 60.0 km/h نحو الجنوب الغربي (1 وحدة = 20 km/h)
o, u = (380, 70), 20
wx, wy = -3 * math.cos(math.radians(45)), -3 * math.sin(math.radians(45))
vectors('c6l3-o01-e3.svg', [
    {'from': (0, 0), 'to': (-9, 0), 'color': C_VEL},
    {'from': (-9, 0), 'to': (-9 + wx, wy), 'color': C_VEL}], w=440, h=200, unit=u, origin=o, grid=False, axes=False,
    extra=VA(o[0] - 150, o[1] - 14, 'الطائرة بالنسبة إلى الهواء') + T(o[0] - 90, o[1] + 22, '1.80×10² km/h', 14, color=C_VEL) +
    VA(o[0] - 9 * u + 6, o[1] + 52, 'الهواء بالنسبة إلى الأرض') + T(o[0] - 9 * u - 52, o[1] + 72, '60.0 km/h', 14, color=C_VEL) +
    L(o[0] - 9 * u, o[1], o[0] - 9 * u - 50, o[1], MUTED, 1.2, '4 3') +
    f'<path d="M {o[0] - 9 * u - 34:.1f} {o[1]:.1f} A 34 34 0 0 0 {o[0] - 9 * u - 34 * math.cos(math.radians(45)):.1f} {o[1] + 34 * math.sin(math.radians(45)):.1f}" fill="none" stroke="{INK}" stroke-width="1.4"/>' +
    T(o[0] - 9 * u - 54, o[1] + 22, '‎45°', 13, 'end') + DOT(o[0], o[1], 4, INK) +
    ARROW(400, 185, 400, 145, INK, 1.8) + T(400, 138, 'الشمال', 13) + ARROW(400, 185, 360, 185, INK, 1.8) + T(355, 190, 'الغرب', 13, 'end'))

# ---------- O02 ----------
# mcq2: أربعة مخططات مرقّمة؛ القارب شرقًا والكرة شمالًا بالنسبة إلى القارب
def panel(ox, oy, kind, u=34):
    b = ''
    A = (ox, oy); B = (ox + 4 * u, oy); C = (ox + 4 * u, oy - 2 * u)
    if kind == 1:   # صحيح: رأس بذيل والمحصلة من الذيل الأول إلى الرأس الأخير
        b += ARROW(*A, *B, C_VEL, 2.6) + ARROW(*B, *C, C_VEL, 2.6) + ARROW(*A, *C, C_VEL, 2.6)
        b += VS(ox + 2 * u, oy + 22, 'b/w', size=15) + VS(ox + 4 * u + 24, oy - u + 4, 'm/b', size=15) + VS(ox + 1.6 * u, oy - 1.3 * u - 6, 'm/w', size=15)
    if kind == 2:   # المحصلة معكوسة
        b += ARROW(*A, *B, C_VEL, 2.6) + ARROW(*B, *C, C_VEL, 2.6) + ARROW(*C, *A, C_VEL, 2.6)
        b += VS(ox + 2 * u, oy + 22, 'b/w', size=15) + VS(ox + 4 * u + 24, oy - u + 4, 'm/b', size=15) + VS(ox + 1.6 * u, oy - 1.3 * u - 6, 'm/w', size=15)
    if kind == 3:   # ذيل بذيل والثالث يصل بين الرأسين (طرح)
        D = (ox, oy - 2 * u)
        b += ARROW(*A, *B, C_VEL, 2.6) + ARROW(*A, *D, C_VEL, 2.6) + ARROW(*D, *B, C_VEL, 2.6)
        b += VS(ox + 2 * u, oy + 22, 'b/w', size=15) + VS(ox - 24, oy - u + 4, 'm/b', size=15) + VS(ox + 2.4 * u, oy - 1.3 * u - 6, 'm/w', size=15)
    if kind == 4:   # سرعة الكرة بالنسبة إلى القارب جنوبًا (اتجاه خاطئ)
        C2 = (ox + 4 * u, oy + 2 * u)
        b += ARROW(*A, *B, C_VEL, 2.6) + ARROW(*B, *C2, C_VEL, 2.6) + ARROW(*A, *C2, C_VEL, 2.6)
        b += VS(ox + 2 * u, oy - 10, 'b/w', size=15) + VS(ox + 4 * u + 24, oy + u + 4, 'm/b', size=15) + VS(ox + 1.6 * u, oy + 1.3 * u + 18, 'm/w', size=15)
    return b

b = ''
for k, (ox, oy) in enumerate([(40, 110), (300, 110), (40, 270), (300, 220)], 1):
    lab_y = 30 if k <= 2 else (190 if k == 3 else 190)
    b += T(ox + 2 * 34, lab_y, f'({k})', 16, weight='bold')
    b += panel(ox, oy, k)
b += L(275, 15, 275, 345, GRID, 1.5) + L(15, 170, 535, 170, GRID, 1.5)
save('c6l3-o02-panels.svg', svg(550, 350, b))

# mcq3: مثلث كالشكل 6-10 بحروف سفلية عربية؛ الضلع الثالث متقطع بلا رمز
o, u = (110, 230), 22
vectors('c6l3-o02-triangle.svg', [
    {'from': (0, 0), 'to': (0, 8), 'color': C_VEL},
    {'from': (0, 8), 'to': (4, 6), 'color': C_VEL},
    {'from': (0, 0), 'to': (4, 6), 'color': C_VEL, 'dash': True}], w=380, h=260, unit=u, origin=o, grid=False, axes=False,
    extra=VA(o[0] - 82, o[1] - 4 * u, 'الطائرة بالنسبة') + T(o[0] - 75, o[1] - 4 * u + 20, 'إلى الهواء', 11, 'start', C_VEL) +
    VA(o[0] + 2 * u + 18, o[1] - 7 * u - 14, 'الهواء بالنسبة إلى الأرض') +
    T(o[0] + 2 * u + 22, o[1] - 3 * u + 14, '؟', 20, 'start', C_VEL, 'bold') + DOT(o[0], o[1], 4, INK) + compass(290, 240, 36) +
    ARROW(o[0] + 3.7 * u, o[1] - 5.55 * u, o[0] + 4 * u, o[1] - 6 * u, C_VEL, 2, 10))

# mcq6: قارب في نهر؛ v_b/w عمودية على الضفة، وv_w/E موازية لها (ذيل بذيل كالشكل 6-14)
b = RECT(0, 0, 420, 18, INK, '#8fb47a', 0) + RECT(0, 222, 420, 18, INK, '#8fb47a', 0) + RECT(0, 18, 420, 204, INK, '#dcecf7', 0)
bx, by = 170, 175
b += f'<ellipse cx="{bx}" cy="{by}" rx="13" ry="30" fill="#c8a06a" stroke="{INK}" stroke-width="1.5"/>'
b += ARROW(bx, by, bx, by - 3 * 40, C_VEL, 3) + VS(bx - 26, by - 70, 'b/w')
b += ARROW(bx, by, bx + 2 * 40, by, C_VEL, 3) + VS(bx + 52, by + 26, 'w/E')
b += ARROW(320, 40, 390, 40, MUTED, 1.6) + T(355, 62, 'اتجاه التيار', 13, color=MUTED)
save('c6l3-o02-river.svg', svg(420, 240, b))

# mcq7: قطار والراكب يمشي نحو مؤخرته (كالشكل 6-9b)؛ الطولان بمقياس 20 m/s و2.0 m/s
b = ''
b += RECT(40, 150, 440, 46, INK, '#dfe6f1', 2) + DOT(120, 205, 9, INK, '#fff') + DOT(400, 205, 9, INK, '#fff')
b += T(260, 180, 'القطار', 14)
b += DOT(300, 135, 6, INK)
b += ARROW(80, 50, 80 + 20 * 15, 50, C_VEL, 3) + VS(80 + 150, 38, 't/E') + T(80 + 300 + 8, 55, '20 m/s', 14, 'start', C_VEL)
b += ARROW(300, 112, 300 - 2 * 15, 112, C_VEL, 3) + VS(285, 98, 'y/t') + T(300 + 8, 117, '2.0 m/s', 14, 'start', C_VEL)
b += L(20, 214, 500, 214, INK, 2) + ARROW(420, 245, 480, 245, MUTED, 1.6) + T(486, 250, '+x', 14, 'start', MUTED, italic=True)
save('c6l3-o02-train.svg', svg(520, 260, b))

# ---------- O04 ----------
# mcq2: ممر متحرك 1.2 m/s إلى اليمين، وشخص يمشي عليه 1.5 m/s إلى اليسار بالنسبة إلى الممر (1 m/s = 80 px)
b = RECT(40, 140, 440, 26, INK, '#e3e7ee', 2)
for xx in range(60, 480, 30): b += L(xx, 143, xx + 12, 163, MUTED, 1)
b += DOT(300, 120, 7, INK) + T(300, 100 - 52, 'الشخص', 13)
b += ARROW(300, 85, 300 - 1.5 * 80, 85, C_VEL, 3) + T(300 - 60, 75, '1.5 m/s', 14, color=C_VEL) + T(300 - 60, 106, 'بالنسبة إلى الممر', 12, color=C_VEL)
b += ARROW(120, 195, 120 + 1.2 * 80, 195, C_VEL, 3) + T(168, 222, '1.2 m/s', 14, color=C_VEL) + T(360, 200, 'الممر المتحرك بالنسبة إلى الأرض', 12, color=C_VEL)
b += ARROW(400, 245, 460, 245, MUTED, 1.6) + T(466, 250, '+x', 14, 'start', MUTED, italic=True)
save('c6l3-o04-walkway.svg', svg(520, 265, b))

def car(x, y, flip=False, label=''):
    s = RECT(x, y, 70, 26, INK, '#eef2f8', 2) + DOT(x + 15, y + 28, 6, INK, '#fff') + DOT(x + 55, y + 28, 6, INK, '#fff')
    if label: s += T(x + 35, y + 18, label, 13)
    return s

# mcq4: سيارتان متعاكستان: A شرقًا 90 km/h، وB غربًا 80 km/h (1 km/h = 1.6 px)
b = RECT(0, 60, 540, 150, INK, '#f1f1ee', 0) + L(0, 135, 540, 135, MUTED, 2, '14 10')
b += car(60, 155, label='A') + ARROW(130, 168, 130 + 90 * 1.6, 168, C_VEL, 3) + T(130 + 72, 158, '90 km/h', 14, color=C_VEL)
b += car(410, 80, label='B') + ARROW(410, 93, 410 - 80 * 1.6, 93, C_VEL, 3) + T(410 - 64, 83, '80 km/h', 14, color=C_VEL)
b += ARROW(470, 245, 520, 245, INK, 1.8) + T(470 - 6, 250, 'الشرق', 13, 'end')
save('c6l3-o04-cars.svg', svg(540, 265, b))

# mcq5: سيارتك 100 km/h والسيارة الأمامية 85 km/h في الاتجاه نفسه (1 km/h = 1.6 px)
b = RECT(0, 40, 560, 110, INK, '#f1f1ee', 0) + L(0, 95, 560, 95, MUTED, 2, '14 10')
b += car(30, 108, label='سيارتك') + ARROW(100, 121, 100 + 100 * 1.6, 121, C_VEL, 3) + T(100 + 80, 112, '100 km/h', 14, color=C_VEL)
b += car(310, 108, label='') + T(345, 172, 'السيارة الأخرى', 13) + ARROW(380, 121, 380 + 85 * 1.6, 121, C_VEL, 3) + T(380 + 68, 112, '85 km/h', 14, color=C_VEL)
b += ARROW(470, 205, 530, 205, MUTED, 1.6) + T(536, 210, '+x', 14, 'start', MUTED, italic=True)
save('c6l3-o04-overtake.svg', svg(560, 225, b))

# ---------- O05 ----------
# mcq2: شبكة كل مربع 1.0 m/s؛ القارب موجه عكس التيار: v_b/w من (0,0) إلى (-2,4)، ثم v_w/E من (-2,4) إلى (0,4)
o, u = (170, 250), 44
vectors('c6l3-o05-grid.svg', [
    {'from': (0, 0), 'to': (-2, 4), 'color': C_VEL},
    {'from': (-2, 4), 'to': (0, 4), 'color': C_VEL}], w=340, h=290, unit=u, origin=o, grid=True, axes=False,
    extra=VS(o[0] - u - 32, o[1] - 2 * u, 'b/w') + VS(o[0] - u, o[1] - 4 * u + 26, 'w/E') +
    ARROW(o[0] - 3.5 * u, o[1], o[0] + 3.5 * u, o[1], MUTED, 1.4) + ARROW(o[0], o[1] + 0.6 * u, o[0], o[1] - 5.3 * u, MUTED, 1.4) +
    T(o[0] + 3.5 * u, o[1] + 20, 'الشرق', 13, 'end', MUTED) + T(o[0] + 8, o[1] - 5.3 * u + 10, 'الشمال', 13, 'start', MUTED) +
    DOT(o[0], o[1], 4, INK) + ARROW(20, 278, 80, 278, MUTED, 1.4) + T(86, 283, 'اتجاه التيار', 12, 'start', MUTED))

# mcq6: رياح نحو الشمال، والمسار المطلوب شرقًا (خط متقطع بلا سهم سرعة)
b = L(60, 170, 420, 170, MUTED, 2, '8 6') + T(240, 192, 'المسار المطلوب', 13) + DOT(60, 170, 5, INK) + T(60, 196, 'المطار', 13) + DOT(420, 170, 5, INK) + T(420, 158, 'الوجهة', 13)
b += ARROW(240, 140, 240, 70, C_VEL, 3) + VA(250, 108, 'الهواء بالنسبة إلى الأرض')
b += compass(70, 90, 36)
save('c6l3-o05-heading.svg', svg(480, 215, b))

# essay1: السرعة بالنسبة إلى الضفة 5.0 m/s شمالًا، والقارب موجه بزاوية 30° غرب الشمال (خط متقطع)
o = (220, 250); u = 40
b = RECT(0, 0, 420, 16, INK, '#8fb47a', 0) + RECT(0, 270, 420, 16, INK, '#8fb47a', 0) + RECT(0, 16, 420, 254, INK, '#dcecf7', 0)
b += ARROW(o[0], o[1], o[0], o[1] - 5 * u, C_VEL, 3) + VS(o[0] + 28, o[1] - 2.5 * u, 'b/E') + T(o[0] + 30, o[1] - 2.5 * u + 22, '5.0 m/s', 14, 'start', C_VEL)
hx, hy = o[0] - 5.4 * u * math.sin(math.radians(30)), o[1] - 5.4 * u * math.cos(math.radians(30))
b += L(o[0], o[1], hx, hy, INK, 1.6, '7 5') + T(hx - 6, hy + 2, 'اتجاه مقدمة القارب', 12, 'end')
b += f'<path d="M {o[0]:.1f} {o[1] - 60:.1f} A 60 60 0 0 0 {o[0] - 60 * math.sin(math.radians(30)):.1f} {o[1] - 60 * math.cos(math.radians(30)):.1f}" fill="none" stroke="{INK}" stroke-width="1.4"/>'
b += T(o[0] - 18, o[1] - 70, '‎30°', 13, 'end') + DOT(o[0], o[1], 4, INK)
b += ARROW(320, 240, 390, 240, MUTED, 1.6) + T(355, 230, 'اتجاه التيار', 12, color=MUTED) + compass(340, 110, 36)
save('c6l3-o05-e1.svg', svg(420, 286, b))
