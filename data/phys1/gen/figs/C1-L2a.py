import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 1-2 القياس (الأهداف O01–O11): مساطر، مخبار مدرج، مقياس حرارة، أميتر بمؤشر، ميزان نابضي، وأشرطة هامش الخطأ.

WOOD = '#f4e7c6'; METAL = '#eef1f5'; LIQ = '#cfe3f5'; THERMO = '#c0392b'; PENCIL = '#e8b730'


def ruler(x0, y0, length, minor, px, labels_every=1, h=48, unit='cm', fill=METAL):
    """مسطرة أفقية: الصفر عند x0، أصغر تدريج minor (بوحدة unit)، px بكسل لكل وحدة. التدريجات تنزل من الحافة العليا."""
    b = RECT(x0 - 16, y0, length * px + 50, h, INK, fill, 1.8)
    n = round(length / minor)
    for k in range(n + 1):
        v = k * minor; x = x0 + v * px
        if abs(v / labels_every - round(v / labels_every)) < 1e-9: ln = 20
        elif minor < 0.5 and abs(v * 2 - round(v * 2)) < 1e-9: ln = 14
        else: ln = 9
        b += L(x, y0, x, y0 + ln, INK, 1.3 if ln < 20 else 1.8)
        if ln == 20: b += T(x, y0 + 37, fmt(round(v, 6)), 14)
    b += T(x0 + length * px + 22, y0 + h - 8, unit, 13, 'middle', MUTED)
    return b


def pencil(x0, y0, length_px, th=16):
    """قلم رصاص أفقي يبدأ عند x0 (طرفه الخلفي) وينتهي رأسه عند x0+length_px. y0 = الحافة السفلى."""
    tip = 26; body = length_px - tip; yc = y0 - th / 2
    b = f'<rect x="{x0:.1f}" y="{y0 - th:.1f}" width="{body:.1f}" height="{th}" fill="{PENCIL}" stroke="{INK}" stroke-width="1.4"/>'
    b += f'<polygon points="{x0 + body:.1f},{y0 - th:.1f} {x0 + length_px:.1f},{yc:.1f} {x0 + body:.1f},{y0:.1f}" fill="#f3d9a8" stroke="{INK}" stroke-width="1.4"/>'
    b += f'<polygon points="{x0 + length_px - 8:.1f},{yc - 3:.1f} {x0 + length_px:.1f},{yc:.1f} {x0 + length_px - 8:.1f},{yc + 3:.1f}" fill="{INK}"/>'
    return b


def single_ruler(name, length, minor, px, obj=None, w=None):
    w = w or int(length * px + 110); x0 = 45
    b = ''
    if obj is not None: b += pencil(x0, 50, obj * px) + L(x0, 50, x0, 62, MUTED, 1, '3 3')
    b += ruler(x0, 62, length, minor, px)
    save(name, svg(w, 130, b))


def two_rulers(name, length, minors, px, obj, tags=('A', 'B')):
    w = int(length * px + 140); x0 = 70; b = ''
    b += T(22, 92, tags[0], 18, weight='bold', color=BLUE) + ruler(x0, 70, length, minors[0], px)
    b += pencil(x0, 60, obj * px)
    b += T(22, 192, tags[1], 18, weight='bold', color=BLUE) + ruler(x0, 170, length, minors[1], px)
    b += pencil(x0, 160, obj * px)
    save(name, svg(w, 240, b))


def vscale(x, ybot, vmin, vmax, minor, major, ppu, side='left', size=13):
    """تدريج رأسي: x موضع الخط، ybot موضع vmin، ppu بكسل لكل وحدة. side جهة الأرقام."""
    b = ''; n = round((vmax - vmin) / minor); sgn = -1 if side == 'left' else 1
    for k in range(n + 1):
        v = vmin + k * minor; y = ybot - (v - vmin) * ppu
        maj = abs((v - vmin) / major - round((v - vmin) / major)) < 1e-9
        half = (not maj) and abs((v - vmin) / (major / 2) - round((v - vmin) / (major / 2))) < 1e-9 and (major / minor) % 2 == 0
        ln = 18 if maj else (12 if half else 8)
        b += L(x, y, x + sgn * ln, y, INK, 1.6 if maj else 1.1)
        if maj: b += T(x + sgn * (ln + 6), y + 4.5, fmt(round(v, 6)), size, 'end' if side == 'left' else 'start')
    return b


def cylinder(name, vmax, minor, major, level, unit='mL'):
    w, h = 260, 400; cx = 150; cw = 70; ybot = 350; ppu = 280 / vmax
    b = f'<path d="M {cx - cw / 2} 40 L {cx - cw / 2} {ybot} Q {cx - cw / 2} {ybot + 10} {cx - cw / 2 + 10} {ybot + 10} L {cx + cw / 2 - 10} {ybot + 10} Q {cx + cw / 2} {ybot + 10} {cx + cw / 2} {ybot} L {cx + cw / 2} 40" fill="#fafcff" stroke="{INK}" stroke-width="2"/>'
    yl = ybot - level * ppu
    b += f'<rect x="{cx - cw / 2 + 1.5}" y="{yl:.1f}" width="{cw - 3}" height="{ybot + 8 - yl:.1f}" fill="{LIQ}"/>'
    b += f'<path d="M {cx - cw / 2 + 1.5} {yl - 5:.1f} Q {cx} {yl + 7:.1f} {cx + cw / 2 - 1.5} {yl - 5:.1f}" fill="{LIQ}" stroke="{BLUE}" stroke-width="1.6"/>'
    b += f'<rect x="{cx - cw / 2 - 25}" y="{ybot + 10}" width="{cw + 50}" height="12" fill="#dfe5ee" stroke="{INK}" stroke-width="1.6"/>'
    b += vscale(cx - cw / 2, ybot, 0, vmax, minor, major, ppu, 'left')
    b += T(cx, 30, unit, 15, italic=False)
    save(name, svg(w, h, b))


def thermometer(name, vmin, vmax, minor, major, value, unit='°C'):
    w, h = 220, 420; cx = 120; ybot = 330; ppu = 270 / (vmax - vmin)
    b = f'<rect x="{cx - 11}" y="35" width="22" height="{ybot - 25}" rx="11" fill="#fafcff" stroke="{INK}" stroke-width="2"/>'
    b += f'<circle cx="{cx}" cy="{ybot + 30}" r="20" fill="{THERMO}" stroke="{INK}" stroke-width="2"/>'
    yv = ybot - (value - vmin) * ppu
    b += f'<rect x="{cx - 4}" y="{yv:.1f}" width="8" height="{ybot + 14 - yv:.1f}" fill="{THERMO}"/>'
    b += vscale(cx + 11, ybot, vmin, vmax, minor, major, ppu, 'right')
    b += T(cx + 52, 28, '‎' + unit, 15)
    save(name, svg(w, h, b))


def two_thermometers(name, vmin, vmax, minors, major, value, tags=('A', 'B')):
    w, h = 420, 420; b = ''; ybot = 330; ppu = 270 / (vmax - vmin)
    for i, cx in enumerate((110, 300)):
        b += f'<rect x="{cx - 11}" y="35" width="22" height="{ybot - 25}" rx="11" fill="#fafcff" stroke="{INK}" stroke-width="2"/>'
        b += f'<circle cx="{cx}" cy="{ybot + 30}" r="20" fill="{THERMO}" stroke="{INK}" stroke-width="2"/>'
        yv = ybot - (value - vmin) * ppu
        b += f'<rect x="{cx - 4}" y="{yv:.1f}" width="8" height="{ybot + 14 - yv:.1f}" fill="{THERMO}"/>'
        b += vscale(cx + 11, ybot, vmin, vmax, minors[i], major, ppu, 'right')
        b += T(cx - 45, 60, tags[i], 20, weight='bold', color=BLUE) + T(cx + 50, 28, '‎°C', 14)
    save(name, svg(w, h, b))


def dial(name, vmax, minor, major, value, unit='A'):
    w, h = 400, 260; cx, cy, R = 200, 215, 160; a0, a1 = 150, 30; b = ''
    b += f'<rect x="10" y="10" width="{w - 20}" height="{h - 20}" rx="10" fill="#f7f8fb" stroke="{INK}" stroke-width="2"/>'
    ang = lambda v: math.radians(a0 + (a1 - a0) * v / vmax)
    b += f'<path d="M {cx + R * math.cos(math.radians(a0)):.1f} {cy - R * math.sin(math.radians(a0)):.1f} A {R} {R} 0 0 1 {cx + R * math.cos(math.radians(a1)):.1f} {cy - R * math.sin(math.radians(a1)):.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
    n = round(vmax / minor)
    for k in range(n + 1):
        v = k * minor; a = ang(v); maj = abs(v / major - round(v / major)) < 1e-9
        ln = 18 if maj else 9
        b += L(cx + R * math.cos(a), cy - R * math.sin(a), cx + (R - ln) * math.cos(a), cy - (R - ln) * math.sin(a), INK, 1.8 if maj else 1.1)
        if maj: b += T(cx + (R + 16) * math.cos(a), cy - (R + 16) * math.sin(a) + 5, fmt(round(v, 6)), 15)
    a = ang(value)
    b += L(cx, cy, cx + (R - 8) * math.cos(a), cy - (R - 8) * math.sin(a), RED, 2.5) + DOT(cx, cy, 8, INK)
    b += T(cx, cy - 55, unit, 22)
    save(name, svg(w, h, b))


def spring_balance(name, vmax, minor, major, value, unit='N'):
    w, h = 220, 420; x0, top, ppu = 70, 60, 280 / vmax; b = ''
    b += L(110, 10, 110, 40, INK, 2) + f'<circle cx="110" cy="10" r="0" />'
    b += f'<rect x="{x0}" y="40" width="80" height="330" rx="10" fill="#f7f8fb" stroke="{INK}" stroke-width="2"/>'
    b += f'<rect x="104" y="{top - 6}" width="12" height="{vmax * ppu + 12:.1f}" fill="#d6dbe3" stroke="{INK}" stroke-width="1"/>'
    # التدريج يزداد إلى أسفل
    nmin = round(vmax / minor)
    for k in range(nmin + 1):
        v = k * minor; y = top + v * ppu; maj = abs(v / major - round(v / major)) < 1e-9
        half = (not maj) and abs(v / (major / 2) - round(v / (major / 2))) < 1e-9 and round(major / minor) % 2 == 0
        ln = 16 if maj else (11 if half else 7)
        b += L(104, y, 104 - ln, y, INK, 1.6 if maj else 1)
        if maj: b += T(104 - ln - 5, y + 4.5, fmt(round(v, 6)), 13, 'end')
    yp = top + value * ppu
    b += f'<polygon points="104,{yp:.1f} 128,{yp - 6:.1f} 128,{yp + 6:.1f}" fill="{RED}"/>' + L(128, yp, 142, yp, RED, 2)
    b += T(134, 62, unit, 16) + L(110, 370, 110, 392, INK, 2) + L(110, 392, 102, 402, INK, 2)
    save(name, svg(w, h, b))


def errorbars(name, data, yr, ystep, ylabel, xlabel='الطالب', accepted=None, w=460, h=340):
    """data = [(tag, mean, err)]. أشرطة هامش الخطأ كما في الكتاب (حمراء)، وخط القيمة المقبولة اختياري."""
    L0, R0, T0, B0 = 82, w - 20, 22, h - 56
    Y = lambda y: B0 - (y - yr[0]) / (yr[1] - yr[0]) * (B0 - T0)
    b = ''; n = round((yr[1] - yr[0]) / ystep)
    for k in range(n + 1):
        y = yr[0] + k * ystep
        b += L(L0, Y(y), R0, Y(y), GRID, 1) + L(L0 - 5, Y(y), L0, Y(y), INK, 1.5) + T(L0 - 9, Y(y) + 4.5, f'{y:.1f}', 13, 'end', MUTED)
    b += L(L0, B0, R0, B0, INK, 2) + L(L0, B0, L0, T0, INK, 2)
    m = len(data); step = (R0 - L0) / (m + 1)
    if accepted is not None:
        b += L(L0, Y(accepted), R0, Y(accepted), C_DISP, 2, '8 5')
    for i, (tag, mean, err) in enumerate(data):
        x = L0 + (i + 1) * step
        b += L(x, Y(mean - err), x, Y(mean + err), RED, 2.5) + L(x - 12, Y(mean + err), x + 12, Y(mean + err), RED, 2.5) + L(x - 12, Y(mean - err), x + 12, Y(mean - err), RED, 2.5)
        b += L(x - 20, Y(mean), x + 20, Y(mean), INK, 2.5)
        b += T(x, B0 + 20, tag, 15, weight='bold')
    b += T((L0 + R0) / 2, h - 10, xlabel, 14)
    b += T(20, (T0 + B0) / 2, ylabel, 14, rotate=-90)
    if accepted is not None:
        b += T(L0 + 6, Y(accepted) - 7, 'القيمة المقبولة', 13, 'start', C_DISP, 'bold')
    save(name, svg(w, h, b))


if __name__ == '__main__':
    # O08: ماذا يمثل طول شريط هامش الخطأ؟
    errorbars('c1l2-o08-errorbars.svg', [('1', 30.4, 0.4), ('2', 30.2, 0.1)], (29.6, 31.0), 0.2, 'طول الطاولة (cm)')
    # O09: مسطرتان مختلفتا التدريج تقيسان القلم نفسه
    two_rulers('c1l2-o09-two-rulers.svg', 6, (0.1, 0.5), 80, 4.6)
    # O09 مقالي: مقياسا حرارة
    two_thermometers('c1l2-o09-thermometers.svg', 0, 50, (1, 5), 10, 27)
    # O10
    single_ruler('c1l2-o10-ruler-mm.svg', 6, 0.1, 80, obj=4.3)
    single_ruler('c1l2-o10-ruler-half.svg', 6, 0.5, 80, obj=4.3)
    cylinder('c1l2-o10-cylinder.svg', 100, 2, 10, 64)
    thermometer('c1l2-o10-thermometer.svg', 20, 40, 0.5, 5, 31.5)
    dial('c1l2-o10-ammeter.svg', 5, 0.2, 1, 3.4)
    spring_balance('c1l2-o10-spring-balance.svg', 5, 0.1, 1, 2.7)
    two_rulers('c1l2-o10-two-rulers.svg', 6, (1, 0.1), 80, 4.6)
    # O11
    errorbars('c1l2-o11-errorbars4.svg', [('1', 25.4, 0.3), ('2', 25.1, 0.1), ('3', 25.6, 0.5), ('4', 24.8, 0.2)], (24.4, 26.2), 0.2, 'طول النابض (cm)', w=500)
    errorbars('c1l2-o11-accepted.svg', [('1', 9.62, 0.06), ('2', 9.80, 0.30), ('3', 9.72, 0.18)], (9.4, 10.2), 0.1, 'تسارع السقوط (m/s²)', accepted=9.80, w=480)
    errorbars('c1l2-o11-errorbars3.svg', [('1', 20.4, 0.3), ('2', 20.7, 0.2), ('3', 20.1, 0.4)], (19.6, 21.0), 0.2, 'طول الخيط (cm)')
