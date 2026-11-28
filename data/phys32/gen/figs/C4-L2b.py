import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-2 (الأهداف O05–O08 وO13): المحول الكهربائي كما يرسمه الكتاب (الشكلان 15-4 و22-4 ومثال 2):
# قلب حديدي رمادي على شكل إطار، وملف ابتدائي على الضلع الأيسر وملف ثانوي على الضلع الأيمن. الرموز قائمة (V_p، I_s، N_p).
import math

CORE = '#9aa5b1'; CORE_EDGE = '#5f6b78'; COPPER = '#b8692e'; WIRE = INK; PLUS = '#c0392b'


def coil(x0, x1, ytop, ybot, n):
    """لفات ملف حول ضلع رأسي للقلب بين x0 وx1: خطوط مائلة نحاسية (الوجه الأمامي) كما في رسوم الكتاب."""
    b = ''; step = (ybot - ytop) / n
    for k in range(n):
        y = ytop + (k + 0.5) * step
        b += f'<path d="M {x0 - 5:.1f} {y + step * 0.35:.1f} L {x1 + 5:.1f} {y - step * 0.35:.1f}" stroke="{COPPER}" stroke-width="3.2" fill="none" stroke-linecap="round"/>'
    return b


def transformer(cx, cy, w=200, h=170, t=34, np_=5, ns=12, lead=60, core_label=None):
    """إطار القلب الحديدي وملفان. يعيد (الجسم، أطراف الملف الابتدائي [(x,y) أعلى، أسفل]، أطراف الثانوي)."""
    x0, y0 = cx - w / 2, cy - h / 2
    b = f'<path d="M {x0} {y0} h {w} v {h} h {-w} Z M {x0 + t} {y0 + t} v {h - 2 * t} h {w - 2 * t} v {-(h - 2 * t)} Z" fill="{CORE}" stroke="{CORE_EDGE}" stroke-width="2" fill-rule="evenodd"/>'
    ya, yb = y0 + t + 10, y0 + h - t - 10
    b += coil(x0, x0 + t, ya, yb, np_) + coil(x0 + w - t, x0 + w, ya, yb, ns)
    # أطراف الملفين
    pa, pb = (x0 - 5, ya + 2), (x0 - 5, yb - 2)
    sa, sb = (x0 + w + 5, ya + 2), (x0 + w + 5, yb - 2)
    b += L(pa[0], pa[1], pa[0] - lead, pa[1], WIRE, 2) + L(pb[0], pb[1], pb[0] - lead, pb[1], WIRE, 2)
    b += L(sa[0], sa[1], sa[0] + lead, sa[1], WIRE, 2) + L(sb[0], sb[1], sb[0] + lead, sb[1], WIRE, 2)
    if core_label: b += T(cx, y0 + h - 10, core_label, 13, color='#fff', weight='bold')
    return b, ((pa[0] - lead, pa[1]), (pb[0] - lead, pb[1])), ((sa[0] + lead, sa[1]), (sb[0] + lead, sb[1]))


def ac_source(x, y, r=17):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{WIRE}" stroke-width="2.2"/>'
            f'<path d="M {x - 10} {y} q 5 -9 10 0 q 5 9 10 0" fill="none" stroke="{WIRE}" stroke-width="2"/>')


def lamp(x, y, r=15):
    return (f'<g transform="rotate(90 {x} {y})"><circle cx="{x}" cy="{y}" r="{r}" fill="#fff8d8" stroke="{WIRE}" stroke-width="2.2"/>'
            f'<path d="M {x - r} {y} L {x - 6} {y} C {x - 4} {y - 9} {x + 4} {y - 9} {x} {y} C {x - 6} {y + 6} {x + 6} {y + 6} {x + 6} {y} L {x + r} {y}" fill="none" stroke="{WIRE}" stroke-width="1.8"/></g>')


def battery_v(x, yc):
    """بطارية رأسية من خليتين، الطرف الموجب (الخط الطويل) أعلى."""
    b = ''
    for k, y in enumerate([yc - 12, yc + 4]):
        b += L(x - 16, y, x + 16, y, WIRE, 2.4) + L(x - 8, y + 8, x + 8, y + 8, WIRE, 4)
    b += T(x - 26, yc - 8, '+', 15, color=PLUS, weight='bold') + T(x - 26, yc + 18, '−', 16, weight='bold')
    return b


def resistor_v(x, y1, y2, n=6, amp=9):
    seg = (y2 - y1) * 0.6; ys = y1 + (y2 - y1 - seg) / 2; ye = ys + seg
    pts = [(x, y1), (x, ys)] + [(x + (amp if k % 2 == 0 else -amp), ys + (k + 0.5) * seg / n) for k in range(n)] + [(x, ye), (x, y2)]
    return f'<polyline points="{" ".join(f"{a:.1f},{c:.1f}" for a, c in pts)}" fill="none" stroke="{WIRE}" stroke-width="2.2" stroke-linejoin="round"/>'


def num(x, y, n):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="#fff" stroke="{INK}" stroke-width="1.5"/>' + T(x, y + 5, str(n), 14, weight='bold')


def close_left(P, xs, comp):
    """يغلق دائرة الملف الابتدائي بعنصر رأسي عند x = xs."""
    (xa, ya), (xb, yb) = P; ym = (ya + yb) / 2
    return L(xa, ya, xs, ya, WIRE, 2) + L(xa, yb, xs, yb, WIRE, 2) + L(xs, ya, xs, ym - 18, WIRE, 2) + L(xs, ym + 18, xs, yb, WIRE, 2) + comp(xs, ym)


def close_right(S, xs, comp):
    (xa, ya), (xb, yb) = S; ym = (ya + yb) / 2
    return L(xa, ya, xs, ya, WIRE, 2) + L(xa, yb, xs, yb, WIRE, 2) + L(xs, ya, xs, ym - 15, WIRE, 2) + L(xs, ym + 15, xs, yb, WIRE, 2) + comp(xs, ym)


# ───────── O05 تركيب المحول ومبدأ عمله
def o05():
    b, P, S = transformer(260, 140, np_=6, ns=9, lead=50)
    b += close_left(P, P[0][0] - 10, ac_source) + close_right(S, S[0][0] + 10, lamp)
    b += num(260, 52, 1) + num(150, 140, 2) + num(370, 140, 3)
    b += L(260, 64, 260, 90, MUTED, 1.2) + L(162, 140, 175, 140, MUTED, 1.2) + L(358, 140, 345, 140, MUTED, 1.2)
    b += T(P[0][0] - 10, 245, 'مصدر جهد متناوب', 13, color=MUTED) + T(S[0][0] + 10, 245, 'مصباح', 13, color=MUTED)
    save('c4l2-o05-parts.svg', svg(520, 265, b))

    # الشكل 22-4: بطارية ومفتاح في دائرة الابتدائي ومصباح في دائرة الثانوي
    b, P, S = transformer(260, 140, np_=7, ns=7, lead=50)
    (xa, ya), (xb, yb) = P; xs = xa - 30
    b += L(xa, ya, xa - 6, ya, WIRE, 2)
    # مفتاح مفتوح على السلك العلوي
    b += DOT(xa - 6, ya, 3.2) + DOT(xa - 46, ya, 3.2) + L(xa - 6, ya, xa - 42, ya - 16, WIRE, 2.4) + L(xa - 46, ya, xs, ya, WIRE, 2)
    b += L(xb, yb, xs, yb, WIRE, 2) + L(xs, ya, xs, (ya + yb) / 2 - 16, WIRE, 2) + L(xs, (ya + yb) / 2 + 20, xs, yb, WIRE, 2) + battery_v(xs, (ya + yb) / 2)
    b += close_right(S, S[0][0] + 10, lamp)
    b += T(165, 250, 'ابتدائي', 14) + T(355, 250, 'ثانوي', 14) + T(xa - 26, ya - 22, 'مفتاح', 12, color=MUTED)
    save('c4l2-o05-dc.svg', svg(520, 265, b))


# ───────── O06 الرافع والخافض
def o06():
    b = ''
    for ox, lab, n1, n2, d1, d2 in [(0, 'المحول A', '40 لفة', '160 لفة', 3, 12), (330, 'المحول B', '60 لفة', '15 لفة', 12, 3)]:
        body, P, S = transformer(ox + 165, 150, w=170, h=160, t=32, np_=d1, ns=d2, lead=34)
        b += body + T(ox + 165, 40, lab, 16, weight='bold')
        b += T(ox + 112, 62, 'ابتدائي', 13) + T(ox + 218, 62, 'ثانوي', 13)
        b += T(ox + 165, 128, n1 + ' (ابتدائي)', 12) + T(ox + 165, 176, n2 + ' (ثانوي)', 12)
    save('c4l2-o06-two.svg', svg(660, 250, b))

    body, P, S = transformer(240, 135, w=190, h=170, t=34, np_=12, ns=3, lead=45)
    b = body + T(P[0][0] + 22, 40, 'الملف X', 15, weight='bold') + T(S[0][0] - 22, 40, 'الملف Y', 15, weight='bold')
    b += T(105, 140, '400 لفة', 14, 'end') + T(375, 140, '100 لفة', 14, 'start')
    for (x, y) in P + S: b += DOT(x, y, 4)
    save('c4l2-o06-reverse.svg', svg(480, 240, b))


# ───────── O07 الاستعمالات: نقل الطاقة الكهربائية
def mini_tr(cx, cy, n):
    body, P, S = transformer(cx, cy, w=70, h=64, t=14, np_=4, ns=4, lead=8)
    return body + num(cx, cy - 48, n), P, S


def o07():
    b = ''
    # محطة التوليد
    b += RECT(20, 110, 90, 70, INK, '#dfe6ee', 2) + f'<polygon points="30,110 50,80 70,110" fill="#c9d3df" stroke="{INK}" stroke-width="2"/>' + RECT(78, 70, 14, 40, INK, '#c9d3df', 2)
    b += T(65, 205, 'محطة التوليد', 13)
    t1, P1, S1 = mini_tr(170, 140, 1); b += t1
    b += L(110, 128, P1[0][0], P1[0][1], WIRE, 2) + L(110, 152, P1[1][0], P1[1][1], WIRE, 2)
    # خطوط نقل طويلة وأبراج
    b += L(S1[0][0], S1[0][1], 470, S1[0][1], WIRE, 2) + L(S1[1][0], S1[1][1], 470, S1[1][1], WIRE, 2)
    for x in (270, 360):
        b += f'<polygon points="{x - 14},190 {x},92 {x + 14},190" fill="none" stroke="{MUTED}" stroke-width="1.6"/>'
    b += T(315, 75, 'خطوط نقل طويلة', 13, color=MUTED)
    t2, P2, S2 = mini_tr(510, 140, 2); b += t2
    b += L(470, S1[0][1], P2[0][0], P2[0][1], WIRE, 2) + L(470, S1[1][1], P2[1][0], P2[1][1], WIRE, 2)
    xh = 590
    b += L(S2[0][0], S2[0][1], xh + 10, S2[0][1], WIRE, 2) + L(S2[1][0], S2[1][1], xh + 10, S2[1][1], WIRE, 2)
    b += (f'<polygon points="{xh},180 {xh + 70},180 {xh + 70},125 {xh + 35},95 {xh},125" fill="#f4e7c6" stroke="{INK}" stroke-width="2"/>'
          + RECT(xh + 26, 154, 18, 26, INK, '#b9895a', 1.5))
    b += T(xh + 35, 205, 'المنازل', 13)
    save('c4l2-o07-grid.svg', svg(680, 220, b))


# ───────── O08 مسائل معادلة المحول (رسم المثال 2)
def labelled(name, vals, w=520, h=240):
    """vals = dict: Ip, Vp, Np, Ns, Is, Vs → نص القيمة (أو '?')."""
    body, P, S = transformer(260, 120, w=170, h=150, t=30, np_=6, ns=6, lead=80)
    b = body
    (pa, pb), (sa, sb) = P, S
    if vals.get('Ip'): b += ARROW(pa[0] + 10, pa[1] - 12, pa[0] + 50, pa[1] - 12, WIRE, 1.8, 8) + T(pa[0] + 30, pa[1] - 20, 'I_p = ' + vals['Ip'], 14)
    b += T(pa[0] + 36, (pa[1] + pb[1]) / 2 + 5, 'V_p = ' + vals['Vp'], 14)
    if vals.get('Is'): b += ARROW(sb[0] - 50, sa[1] - 12, sb[0] - 10, sa[1] - 12, WIRE, 1.8, 8) + T(sa[0] - 30, sa[1] - 20, 'I_s = ' + vals['Is'], 14)
    b += T(sa[0] - 36, (sa[1] + sb[1]) / 2 + 5, 'V_s = ' + vals['Vs'], 14)
    if vals.get('Np'): b += T(260, 102, 'N_p = ' + vals['Np'], 13) + T(260, 142, 'N_s = ' + vals['Ns'], 13)
    b += T(170, 215, 'ابتدائي', 13) + T(350, 215, 'ثانوي', 13)
    save(name, svg(w, h, b))


def o08():
    labelled('c4l2-o08-ex.svg', dict(Ip='?', Vp='240 V', Is='5.0 A', Vs='12 V'))
    labelled('c4l2-o08-crt.svg', dict(Vp='120 V', Np='?', Ns='25000', Vs='15 kV'))
    labelled('c4l2-o08-e1.svg', dict(Ip='?', Vp='60.0 V', Np='250', Ns='5000', Is='0.50 A', Vs='?'))


# ───────── O13 الكفاءة والقدرة الضائعة
def meters(name, vp, ip, vs, is_):
    body, P, S = transformer(260, 125, w=170, h=150, t=30, np_=7, ns=4, lead=90)
    b = body
    for (pts, side, v, i) in [(P, -1, vp, ip), (S, 1, vs, is_)]:
        (xa, ya), (xb, yb) = pts
        b += T(xa - side * 42, (ya + yb) / 2 + 5, v, 14) + T(xa - side * 35, ya - 12, i, 14)
    b += ARROW(P[0][0] + 12, P[0][1] - 30, P[0][0] + 52, P[0][1] - 30, WIRE, 1.6, 8) + ARROW(S[0][0] - 52, S[0][1] - 30, S[0][0] - 12, S[0][1] - 30, WIRE, 1.6, 8)
    b += T(170, 225, 'ابتدائي', 13) + T(350, 225, 'ثانوي', 13)
    save(name, svg(520, 245, b))


def o13():
    meters('c4l2-o13-meters.svg', 'V_p = 230 V', 'I_p = 0.500 A', 'V_s = 20.0 V', 'I_s = 5.00 A')
    meters('c4l2-o13-e3.svg', 'V_p = 240 V', 'I_p = 2.50 A', 'V_s = 48.0 V', 'I_s = 11.5 A')
    # سلسلة: مصدر 2.4 kV ← T1 (1:5) ← أسلاك ← T2 ← حمل
    b = ''
    t1, P1, S1 = transformer(170, 120, w=90, h=90, t=18, np_=3, ns=8, lead=20); b += t1
    t2, P2, S2 = transformer(400, 120, w=90, h=90, t=18, np_=8, ns=3, lead=20); b += t2
    b += close_left(P1, P1[0][0] - 20, ac_source) + T(P1[0][0] - 20, 185, '2.4 kV', 14)
    b += L(S1[0][0], S1[0][1], P2[0][0], P2[0][1], WIRE, 2) + L(S1[1][0], S1[1][1], P2[1][0], P2[1][1], WIRE, 2)
    xr = S2[0][0] + 30
    b += L(S2[0][0], S2[0][1], xr, S2[0][1], WIRE, 2) + L(S2[1][0], S2[1][1], xr, S2[1][1], WIRE, 2) + resistor_v(xr, S2[0][1], S2[1][1])
    b += T(xr + 18, 125, 'حمل', 13, 'start') + T(xr + 18, 145, '240 V', 13, 'start')
    b += T(170, 50, 'T_1', 16) + T(400, 50, 'T_2', 16) + T(170, 190, '1 : 5', 13) + T(400, 190, 'الكفاءة', 13) + T(400, 207, '96.0%', 13)
    b += T(285, 100, 'أسلاك', 12, color=MUTED)
    save('c4l2-o13-chain.svg', svg(560, 220, b))


if __name__ == '__main__':
    o05(); o06(); o07(); o08(); o13()
