import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 5-1 (المتجهات) — الأهداف O01–O11
# المتجهات العامة A وB وR زرقاء كالكتاب (ص132، 134–135)، والإزاحة خضراء (ص133، 137)، والقوة زرقاء، والسرعة حمراء.
# لا يُرسم المتجه المحصل أبدًا حين يكون هو المطلوب.
import math

C_GEN = C_FORCE  # المتجهات العامة في الكتاب زرقاء


class Scene:
    """مشهد بإحداثيات عالمية (y لأعلى) على شبكة اختيارية."""
    def __init__(self, w, h, unit, origin, grid=True):
        self.w, self.h, self.u, self.o = w, h, unit, origin
        self.b = ''
        if grid:
            ox, oy = origin
            for gx in range(-int(ox // unit), int((w - ox) // unit) + 1): self.b += L(ox + gx * unit, 0, ox + gx * unit, h, GRID, 1)
            for gy in range(-int(oy // unit), int((h - oy) // unit) + 1): self.b += L(0, oy + gy * unit, w, oy + gy * unit, GRID, 1)

    def P(self, p): return (self.o[0] + p[0] * self.u, self.o[1] - p[1] * self.u)

    def axes(self, xl='+x', yl='+y', xmin=None, xmax=None, ymin=None, ymax=None):
        ox, oy = self.o
        x0 = 10 if xmin is None else self.P((xmin, 0))[0]; x1 = self.w - 12 if xmax is None else self.P((xmax, 0))[0]
        y0 = self.h - 10 if ymin is None else self.P((0, ymin))[1]; y1 = 14 if ymax is None else self.P((0, ymax))[1]
        self.b += ARROW(x0, oy, x1, oy, MUTED, 1.6) + ARROW(ox, y0, ox, y1, MUTED, 1.6)
        if xl: self.b += T(x1 - 2, oy + 20, xl, 15, 'end', MUTED, italic=True)
        if yl: self.b += T(ox + 8, y1 + 10, yl, 15, 'start', MUTED, italic=True)

    def vec(self, a, b, color=C_GEN, label=None, lpos=(10, -10), dash=False, val=None, vpos=None, w=3):
        (x1, y1), (x2, y2) = self.P(a), self.P(b)
        if dash: self.b += L(x1, y1, x2, y2, color, 2, '6 5') + ARROW(x2 - 0.01 * (x2 - x1), y2 - 0.01 * (y2 - y1), x2, y2, color, 2, 10)
        else: self.b += ARROW(x1, y1, x2, y2, color, w)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if label: self.b += V(mx + lpos[0], my + lpos[1], label, color, 18)
        if val:
            vx, vy = vpos if vpos else (lpos[0], lpos[1] + 20)
            self.b += T(mx + vx, my + vy, val, 14, 'middle', color)

    def arc(self, c, r, a1, a2, label=None, lr=None, color=INK, size=14, dash=False, la=None):
        """قوس زاوية من a1 إلى a2 (درجات، عكس عقارب الساعة) نصف قطره r بالبكسل."""
        cx, cy = self.P(c)
        p1 = (cx + r * math.cos(math.radians(a1)), cy - r * math.sin(math.radians(a1)))
        p2 = (cx + r * math.cos(math.radians(a2)), cy - r * math.sin(math.radians(a2)))
        large = 1 if (a2 - a1) % 360 > 180 else 0
        da = ' stroke-dasharray="4 3"' if dash else ''
        self.b += f'<path d="M {p1[0]:.1f} {p1[1]:.1f} A {r} {r} 0 {large} 0 {p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="{color}" stroke-width="1.5"{da}/>'
        if label:
            am = math.radians(la if la is not None else (a1 + a2) / 2); rr = lr or r + 16
            self.b += T(cx + rr * math.cos(am), cy - rr * math.sin(am) + 5, label, size, 'middle', color)

    def text(self, p, s, size=14, anchor='middle', color=INK, italic=False, weight='normal', dx=0, dy=0):
        x, y = self.P(p); self.b += T(x + dx, y + dy, s, size, anchor, color, weight, italic)

    def bold(self, p, s, color=INK, dx=0, dy=0, size=18):
        x, y = self.P(p); self.b += V(x + dx, y + dy, s, color, size)

    def dot(self, p, r=6, color=INK, fill=None):
        x, y = self.P(p); self.b += DOT(x, y, r, color, fill)

    def line(self, a, b, color=MUTED, w=1.5, dash='5 4'):
        (x1, y1), (x2, y2) = self.P(a), self.P(b); self.b += L(x1, y1, x2, y2, color, w, dash)

    def raw(self, s): self.b += s

    def save(self, name): save(name, svg(self.w, self.h, self.b))


def compass(x, y, n=48):
    """سهما الشمال والشرق (بكسل)."""
    return (ARROW(x, y, x, y - n, INK, 2) + T(x, y - n - 8, 'الشمال', 13) +
            ARROW(x, y, x + n, y, INK, 2) + T(x + n + 6, y + 5, 'الشرق', 13, 'start'))


def polar(r, deg): return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)))


def add(p, q): return (p[0] + q[0], p[1] + q[1])


def triangle(name, A, B, theta, la, lb, color, angle_label, w=520, h=300, unit=None, origin=(60, 250), dirA=0, extra_labels=True):
    """متجهان رأسًا لذيل: A ثم B، والزاوية الداخلية بينهما theta معلَّمة عند الرأس المشترك. لا يُرسم المحصل."""
    u = unit or 1
    s = Scene(w, h, u, origin, grid=False)
    pA = polar(A, dirA); dB = dirA + 180 - theta; pB = add(pA, polar(B, dB))
    s.vec((0, 0), pA, color, 'A', lpos=(0, 26), val=la, vpos=(0, 46))
    nx, ny = math.sin(math.radians(dB)), math.cos(math.radians(dB))  # يمين المتجه B على الشاشة
    s.vec(pA, pB, color, 'B', lpos=(22 * nx, 22 * ny + 6), val=lb, vpos=(22 * nx + 34 * abs(nx) + 4, 22 * ny + 24))
    s.arc(pA, 34, dB, dirA + 180, angle_label, lr=58)
    s.save(name)


# ================= O01 =================
def o01():
    # إزاحتان متعامدتان 9.0 km شرقًا ثم 12.0 km شمالًا (كل مربع 3.0 km)
    s = Scene(420, 350, 22, (70, 290))
    s.vec((0, 0), (9, 0), C_DISP, 'A', lpos=(0, 24), val='9.0 km', vpos=(0, 44))
    s.vec((9, 0), (9, 12), C_DISP, 'B', lpos=(20, 0), val='12.0 km', vpos=(52, 20))
    s.dot((0, 0), 4)
    s.raw(compass(320, 120)); s.save('c5l1-o01-perp.svg')

    # قوتان متعامدتان في حلقة
    s = Scene(400, 330, 1, (120, 230), grid=False)
    s.axes('+x', '+y', -80, 260, -80, 210)
    s.vec((0, 0), (160, 0), C_FORCE, 'F_1', lpos=(0, 28), val='40.0 N', vpos=(0, 48))
    s.vec((0, 0), (0, 120), C_FORCE, 'F_2', lpos=(-30, 0), val='30.0 N', vpos=(-46, 22))
    s.dot((0, 0), 8, INK, '#fff'); s.save('c5l1-o01-forces.svg')

    # قانون الجيب: إزاحتان 30.0 m و20.0 m والزاوية الداخلية 110.0°
    triangle('c5l1-o01-sine.svg', 300, 200, 110, '30.0 m', '20.0 m', C_DISP, '110.0°', w=470, h=280, origin=(50, 215))

    # طائرة 200 km/h شمالًا وريح 50 km/h شرقًا
    s = Scene(420, 330, 1, (150, 270), grid=False)
    s.vec((0, 0), (0, 230), C_VEL, 'v_1', lpos=(-26, 0), val='200 km/h', vpos=(-60, 22))
    s.vec((0, 0), (58, 0), C_VEL, 'v_2', lpos=(0, 24), val='50 km/h', vpos=(0, 44))
    s.dot((0, 0), 6); s.raw(compass(330, 120)); s.save('c5l1-o01-plane.svg')

    # السؤال المقالي: 40.0 m و30.0 m بزاوية داخلية 100.0°
    triangle('c5l1-o01-e2.svg', 300, 225, 100, '40.0 m', '30.0 m', C_DISP, '100.0°', w=470, h=320, origin=(50, 255))


# ================= O02 =================
def o02():
    # مثلث الجمع مع ترقيم الزوايا الثلاث (دون كتابة θ)
    s = Scene(460, 300, 1, (50, 260), grid=False)
    pA = polar(220, 52); pB = add(pA, polar(200, -18))
    s.vec((0, 0), pA, C_GEN, 'A', lpos=(-20, -4))
    s.vec(pA, pB, C_GEN, 'B', lpos=(4, -18))
    s.vec((0, 0), pB, C_GEN, 'R', lpos=(4, 24), dash=True)
    s.arc(pA, 30, 232, 342, '2', lr=46)
    rang = math.degrees(math.atan2(pB[1], pB[0]))
    s.arc((0, 0), 40, rang, 52, '1', lr=58)
    s.arc(pB, 40, 162, 180 + rang, '3', lr=58)
    s.save('c5l1-o02-triangle.svg')

    # متجهان P وQ رأسًا لذيل والمحصل S والزاوية φ بينهما
    s = Scene(460, 280, 1, (50, 240), grid=False)
    pP = polar(240, 20); pQ = add(pP, polar(150, 85))
    s.vec((0, 0), pP, C_GEN, 'P', lpos=(6, 22))
    s.vec(pP, pQ, C_GEN, 'Q', lpos=(18, 0))
    s.vec((0, 0), pQ, C_GEN, 'S', lpos=(-14, -14), dash=True)
    s.arc(pP, 30, 85, 200, 'φ', lr=46, size=16)
    s.save('c5l1-o02-pqs.svg')


# ================= O03 =================
def o03():
    w, h = 640, 230; b = ''
    u = 18
    panels = [((30, 150), (4, 0), polar(4, 60)),
              ((190, 150), (4, 0), (0, 4)),
              ((350, 150), (4, 0), polar(4, 125)),
              ((500, 150), polar(4, 30), polar(3.5, 150))]
    for k, ((ox, oy), a, bb) in enumerate(panels):
        s = Scene(150, 200, u, (20, 160))
        pa = a; pb = add(a, bb)
        s.vec((0, 0), pa, C_GEN, 'A', lpos=(0, 22))
        s.vec(pa, pb, C_GEN, 'B', lpos=(16, 0))
        b += f'<g transform="translate({ox - 20},{0})">' + s.b + f'<rect x="0" y="0" width="150" height="200" fill="none" stroke="{MUTED}" stroke-width="1"/>' + T(75, 222, f'الرسم {k + 1}', 14) + '</g>'
    save('c5l1-o03-pairs.svg', svg(w, h, b))

    # قارب يعبر النهر عموديًّا على التيار
    w, h = 460, 300; b = ''
    b += f'<rect x="0" y="40" width="{w}" height="220" fill="#e8f1fa"/>' + L(0, 40, w, 40, INK, 2) + L(0, 260, w, 260, INK, 2)
    b += T(w - 20, 30, 'الضفة', 13, 'end', MUTED) + T(w - 20, 285, 'الضفة', 13, 'end', MUTED)
    cx, cy = 170, 220
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="14" ry="26" fill="#d9c8a8" stroke="{INK}" stroke-width="2"/>'
    b += ARROW(cx, cy - 28, cx, cy - 150, C_VEL, 3) + V(cx - 14, cy - 100, 'v_b', C_VEL, 18, 'end') + T(cx - 14, cy - 78, '4.0 m/s', 14, 'end', C_VEL)
    b += ARROW(cx + 16, cy, cx + 128, cy, C_VEL, 3) + V(cx + 74, cy - 12, 'v_w', C_VEL, 18) + T(cx + 74, cy + 22, '3.0 m/s', 14, 'middle', C_VEL)
    b += ARROW(330, 90, 420, 90, MUTED, 1.6) + T(375, 80, 'اتجاه التيار', 13, 'middle', MUTED)
    save('c5l1-o03-boat.svg', svg(w, h, b))


# ================= O04 =================
def o04():
    triangle('c5l1-o04-tri135.svg', 225, 150, 135, '15.0 m', '10.0 m', C_DISP, '135.0°', w=440, h=240, origin=(50, 180))

    # قوتان من حلقة بينهما 60.0° (الذيلان معًا)
    s = Scene(420, 300, 1, (110, 240), grid=False)
    s.vec((0, 0), (160, 0), C_FORCE, 'F_1', lpos=(0, 26), val='20.0 N', vpos=(0, 46))
    s.vec((0, 0), polar(200, 60), C_FORCE, 'F_2', lpos=(-24, -6), val='30.0 N', vpos=(-50, 16))
    s.arc((0, 0), 46, 0, 60, '60.0°', lr=70)
    s.dot((0, 0), 8, INK, '#fff'); s.save('c5l1-o04-ring60.svg')

    # جذع يسحبه حبلان بقوة 600 N لكل منهما والزاوية بينهما 20.0°
    s = Scene(560, 240, 1, (200, 120), grid=False)
    s.raw(f'<rect x="20" y="104" width="180" height="32" rx="14" fill="#c9a77c" stroke="{INK}" stroke-width="2"/>')
    s.line((0, 0), (105, 0), MUTED, 1.4, '6 5')
    s.vec((0, 0), polar(300, 10), C_FORCE, 'F_1', lpos=(0, -18), val='600 N', vpos=(150, -40))
    s.vec((0, 0), polar(300, -10), C_FORCE, 'F_2', lpos=(0, 30), val='600 N', vpos=(150, 52))
    s.arc((0, 0), 120, -10, 10, '20.0°', lr=150)
    s.save('c5l1-o04-ropes.svg')

    s = Scene(420, 300, 1, (110, 250), grid=False)
    s.vec((0, 0), (180, 0), C_FORCE, 'F_1', lpos=(0, 26), val='45.0 N', vpos=(0, 46))
    s.vec((0, 0), polar(210, 50), C_FORCE, 'F_2', lpos=(-24, -6), val='60.0 N', vpos=(-52, 16))
    s.arc((0, 0), 46, 0, 50, '50.0°', lr=72)
    s.dot((0, 0), 8, INK, '#fff'); s.save('c5l1-o04-e2.svg')


# ================= O05 =================
def o05():
    s = Scene(400, 360, 40, (60, 320))
    s.axes('+x', '+y')
    A = (2, 1); B = (3, 2); C = (-1, 3)
    p1 = A; p2 = add(p1, B); p3 = add(p2, C)
    s.vec((0, 0), p1, C_GEN, 'A', lpos=(-4, -16))
    s.vec(p1, p2, C_GEN, 'B', lpos=(-6, -16))
    s.vec(p2, p3, C_GEN, 'C', lpos=(18, 4))
    s.text((5.4, -0.5), 'ضلع المربع = \u20661.0 m\u2069', 13, 'end', MUTED)
    s.save('c5l1-o05-grid3.svg')

    s = Scene(360, 300, 50, (60, 260))
    s.axes('+x', '+y')
    A = (4, 1); B = (-1, 3)
    s.vec((0, 0), A, C_GEN, 'A', lpos=(0, 22))
    s.vec(A, add(A, B), C_GEN, 'B', lpos=(18, 0))
    s.text((5.4, -0.6), 'ضلع المربع = \u20661.0 m\u2069', 13, 'end', MUTED)
    s.save('c5l1-o05-e2.svg')


# ================= O06 =================
def o06():
    s = Scene(460, 330, 1, (230, 250), grid=False)
    s.axes('+x', '+y', -210, 210, -60, 230)
    s.vec((0, 0), (90, 0), C_FORCE, 'F_1', lpos=(0, 26), val='50.0 N', vpos=(0, 46))
    s.vec((0, 0), polar(200, 60), C_FORCE, 'F_2', lpos=(26, 6), val='120.0 N', vpos=(62, 26))
    s.vec((0, 0), (-160, 0), C_FORCE, 'F_3', lpos=(0, 26), val='90.0 N', vpos=(0, 46))
    s.arc((0, 0), 40, 0, 60, '60.0°', lr=62)
    s.dot((0, 0), 8, INK, '#fff'); s.save('c5l1-o06-forces3.svg')

    # أرجوحة: حبلان يميلان 15.0° عن الرأسي، الشد في كل منهما 3.10 N
    s = Scene(420, 320, 1, (210, 270), grid=False)
    s.raw(f'<rect x="140" y="270" width="140" height="14" fill="#c9a77c" stroke="{INK}" stroke-width="2"/>')
    s.line((0, 0), (0, 240), MUTED, 1.4, '6 5')
    s.vec((0, 0), polar(220, 105), C_FORCE, 'F_1', lpos=(-24, 0), val='3.10 N', vpos=(-60, 22))
    s.vec((0, 0), polar(220, 75), C_FORCE, 'F_2', lpos=(26, 0), val='3.10 N', vpos=(62, 22))
    s.arc((0, 0), 120, 90, 105, '15.0°', lr=140, size=13)
    s.arc((0, 0), 120, 75, 90, '15.0°', lr=140, size=13)
    s.dot((0, 0), 6); s.save('c5l1-o06-swing.svg')

    s = Scene(420, 420, 40, (100, 220))
    s.axes('+x', '+y')
    A = (4, 3); B = (1, -5); C = (-2, -2)
    p1 = A; p2 = add(p1, B); p3 = add(p2, C)
    s.vec((0, 0), p1, C_DISP, 'A', lpos=(-10, -14))
    s.vec(p1, p2, C_DISP, 'B', lpos=(20, 0))
    s.vec(p2, p3, C_DISP, 'C', lpos=(16, 12))
    s.text((7.5, -4.6), 'ضلع المربع = \u20661.0 m\u2069', 13, 'end', MUTED)
    s.save('c5l1-o06-grid.svg')

    s = Scene(460, 340, 1, (230, 200), grid=False)
    s.axes('+x', '+y', -210, 210, -130, 190)
    s.vec((0, 0), polar(170, 125), C_FORCE, 'F_1', lpos=(-24, -8), val='24.0 N', vpos=(-60, 14))
    s.vec((0, 0), polar(150, 55), C_FORCE, 'F_2', lpos=(26, -6), val='21.0 N', vpos=(60, 14))
    s.vec((0, 0), (0, -100), C_FORCE, 'F_g', lpos=(24, 0), val='20.0 N', vpos=(52, 22))
    s.arc((0, 0), 36, 0, 55, '55.0°', lr=58, size=13)
    s.arc((0, 0), 26, 0, 125, '125.0°', lr=64, size=13, la=112)
    s.dot((0, 0), 5); s.save('c5l1-o06-e2.svg')


# ================= O07 =================
def o07():
    # الرسوم الأربعة لمحاولة جمع A وB (A = (4,0)، B = (1,3))
    w, h = 660, 260; b = ''
    u = 20
    A = (4, 0); Bv = (1, 3)
    cases = [
        ('tip', False), ('tip', True), ('tail', False), ('rot', False)]
    for k, (mode, rev) in enumerate(cases):
        s = Scene(150, 200, u, (8, 170))
        if mode == 'tip':
            s.vec((0, 0), A, C_GEN, 'A', lpos=(0, 22)); s.vec(A, add(A, Bv), C_GEN, 'B', lpos=(16, 0))
            if rev: s.vec(add(A, Bv), (0, 0), C_GEN, 'R', lpos=(-14, -10), dash=True)
            else: s.vec((0, 0), add(A, Bv), C_GEN, 'R', lpos=(-14, -10), dash=True)
        elif mode == 'tail':
            s.vec((0, 0), A, C_GEN, 'A', lpos=(0, 22)); s.vec((0, 0), Bv, C_GEN, 'B', lpos=(-14, 0))
            s.vec(A, Bv, C_GEN, 'R', lpos=(16, -6), dash=True)
        else:
            Br = (3, 1)
            s.vec((0, 0), A, C_GEN, 'A', lpos=(0, 22)); s.vec(A, add(A, Br), C_GEN, 'B', lpos=(4, -14))
            s.vec((0, 0), add(A, Br), C_GEN, 'R', lpos=(-10, -12), dash=True)
        b += f'<g transform="translate({10 + k * 162},10)">' + s.b + f'<rect x="0" y="0" width="150" height="200" fill="none" stroke="{MUTED}" stroke-width="1"/>' + T(75, 226, f'الرسم {k + 1}', 14) + '</g>'
    save('c5l1-o07-panels.svg', svg(w, h, b))
    # المتجهان المطلوب جمعهما
    s = Scene(320, 150, 26, (30, 120))
    s.vec((0, 0), A, C_GEN, 'A', lpos=(0, 22)); s.vec((6, -0.5), add((6, -0.5), Bv), C_GEN, 'B', lpos=(16, 0))
    s.save('c5l1-o07-given.svg')

    # قياس المحصل على شبكة: A = 5 مربعات شرقًا، B من (5,0) إلى (3,4)
    s = Scene(380, 300, 44, (60, 250))
    s.vec((0, 0), (5, 0), C_DISP, 'A', lpos=(0, 22))
    s.vec((5, 0), (3, 4), C_DISP, 'B', lpos=(20, 4))
    s.dot((0, 0), 4)
    s.text((7.0, 4.8), 'ضلع المربع = \u206610 m\u2069', 13, 'end', MUTED)
    s.save('c5l1-o07-measure.svg')

    # المنقلة: A = (2,0)، B من (2,0) إلى (−2,3)
    s = Scene(380, 300, 44, (220, 250))
    s.axes('+x', '+y')
    s.vec((0, 0), (2, 0), C_GEN, 'A', lpos=(0, 22))
    s.vec((2, 0), (-2, 3), C_GEN, 'B', lpos=(16, 14))
    s.save('c5l1-o07-protractor.svg')

    # ثلاثة متجهات متفرقة، ضلع المربع 2.0 m
    s = Scene(460, 300, 36, (30, 270))
    s.vec((0.5, 1), (3.5, 2), C_DISP, 'A', lpos=(0, 22))
    s.vec((6, 1), (5, 4), C_DISP, 'B', lpos=(-18, 0))
    s.vec((8.5, 4), (10.5, 3), C_DISP, 'C', lpos=(4, -14))
    s.text((11.8, 6.6), 'ضلع المربع = \u20662.0 m\u2069', 13, 'end', MUTED)
    s.save('c5l1-o07-e3.svg')


# ================= O08 =================
def o08():
    s = Scene(380, 280, 1, (60, 240), grid=False)
    s.axes('+x', '+y', -40, 300, -30, 210)
    p = polar(260, 30)
    s.vec((0, 0), p, C_DISP, 'A', lpos=(-10, -16), val='12.0 m', vpos=(-10, -38))
    s.line((p[0], 0), p, C_DISP, 1.6)
    s.line((0, 0), (p[0], 0), C_DISP, 1.6)
    s.arc((0, 0), 60, 0, 30, '30.0°', lr=86)
    s.save('c5l1-o08-angle.svg')

    s = Scene(360, 320, 1, (150, 270), grid=False)
    s.axes('+x', '+y', -120, 190, -30, 250)
    p = polar(220, 65)
    s.vec((0, 0), p, C_FORCE, 'F', lpos=(18, 0), val='40.0 N', vpos=(50, 20))
    s.arc((0, 0), 90, 65, 90, '25.0°', lr=112)
    s.dot((0, 0), 6); s.save('c5l1-o08-vertical.svg')

    s = Scene(380, 290, 1, (80, 250), grid=False)
    s.axes('+x', '+y', -50, 280, -25, 220)
    p = polar(220, 50)
    s.vec((0, 0), p, C_VEL, 'v', lpos=(-14, -10), val='18.0 m/s', vpos=(-50, 4))
    s.arc((0, 0), 56, 0, 50, '50.0°', lr=80)
    s.raw(DOT(80, 250, 10, INK, '#eceff4')); s.save('c5l1-o08-velocity.svg')


# ================= O09 =================
def o09():
    s = Scene(380, 280, 1, (60, 240), grid=False)
    s.axes('+x', '+y', -40, 300, -30, 210)
    p = polar(250, 36)
    s.vec((0, 0), p, C_GEN, 'A', lpos=(-12, -14))
    s.vec((0, 0), (p[0], 0), C_GEN, None, dash=True)
    s.vec((p[0], 0), p, C_GEN, None, dash=True)
    s.text((p[0] / 2, 0), '(1)', 15, dy=24); s.text((p[0], p[1] / 2), '(2)', 15, 'start', dx=12)
    s.arc((0, 0), 50, 0, 36, 'θ', lr=70, size=16)
    s.save('c5l1-o09-labels.svg')

    s = Scene(340, 280, 50, (50, 230))
    s.axes('+x', '+y')
    s.vec((0, 0), (4, 3), C_GEN, 'A', lpos=(-12, -14))
    s.text((5.6, -0.6), 'ضلع المربع = \u20661.0 m\u2069', 13, 'end', MUTED)
    s.save('c5l1-o09-e2.svg')


# ================= O10 =================
def o10():
    s = Scene(380, 340, 1, (190, 170), grid=False)
    s.axes('+x', '+y')
    for lab, deg in (('P', 50), ('Q', 140), ('S', 220), ('T', 310)):
        p = polar(120, deg); s.vec((0, 0), p, C_GEN, None)
        q = polar(142, deg); s.bold(q, lab, C_GEN, dy=6)
    s.save('c5l1-o10-quadrants.svg')

    s = Scene(380, 280, 1, (230, 200), grid=False)
    s.axes('+x', '+y', -210, 130, -60, 180)
    p = polar(200, 150)
    s.vec((0, 0), p, C_DISP, 'd', lpos=(10, -16), val='8.0 km', vpos=(14, -38))
    s.arc((0, 0), 40, 0, 150, '150.0°', lr=60, size=13)
    s.save('c5l1-o10-150.svg')


# ================= O11 =================
def o11():
    s = Scene(400, 300, 1, (250, 200), grid=False)
    s.axes('', '', -230, 130, -80, 170)
    s.raw(T(372, 222, 'الشرق', 13) + T(250, 22, 'الشمال', 13) + T(26, 222, 'الغرب', 13) + T(250, 292, 'الجنوب', 13))
    p = polar(190, 140)
    s.vec((0, 0), p, C_DISP, 'd', lpos=(12, -16))
    s.arc((0, 0), 60, 140, 180, '40.0°', lr=84)
    s.save('c5l1-o11-nw.svg')

    s = Scene(380, 320, 1, (210, 140), grid=False)
    s.axes('+x', '+y')
    p = polar(180, 215)
    s.vec((0, 0), p, C_GEN, 'A', lpos=(18, 10))
    s.arc((0, 0), 66, 180, 215, '35.0°', lr=92)
    s.save('c5l1-o11-third.svg')

    s = Scene(420, 260, 1, (60, 220), grid=False)
    s.line((-40, 0), (330, 0), MUTED, 1.4, '6 5')
    s.raw(T(400, 240, 'الأفقي', 13, 'end', MUTED))
    p = polar(330, 30); s.raw(ARROW(*s.P((0, 0)), *s.P(p), INK, 2)); s.text(p, '+x', 15, 'start', italic=True, dx=6, dy=4)
    s.arc((0, 0), 90, 0, 30, '30°', lr=112)
    s.dot((0, 0), 4)
    s.save('c5l1-o11-tilted.svg')


if __name__ == '__main__':
    for f in (o01, o02, o03, o04, o05, o06, o07, o08, o09, o10, o11): f()
