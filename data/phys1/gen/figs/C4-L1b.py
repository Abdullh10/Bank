import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-1 (القوة والحركة) — الأهداف O14–O26: الاتزان، والاحتكاك، والعمودية، والنابض، والشد
import math

def ground(x1, x2, y):
    b = L(x1, y, x2, y, INK, 2)
    for x in range(int(x1) + 6, int(x2), 14): b += L(x, y, x - 8, y + 9, MUTED, 1.2)
    return b

def wall(x, y1, y2, side='left'):
    """جدار رأسي؛ التظليل خلفه."""
    b = L(x, y1, x, y2, INK, 2.5)
    for y in range(int(y1) + 6, int(y2), 14):
        b += L(x, y, x - 9, y + 8, MUTED, 1.2) if side == 'left' else L(x, y, x + 9, y + 8, MUTED, 1.2)
    return b

def ceiling(x1, x2, y):
    b = L(x1, y, x2, y, INK, 2.5)
    for x in range(int(x1) + 4, int(x2), 14): b += L(x, y, x + 8, y - 9, MUTED, 1.2)
    return b

def pol(cx, cy, ang, r):
    a = math.radians(ang); return cx + r * math.cos(a), cy - r * math.sin(a)

def cand(cx, cy, ang, length, label, r0=0, color=C_FORCE):
    """سهم قوة مرشّح يبدأ من الجسم، ورقمه عند رأسه."""
    x1, y1 = pol(cx, cy, ang, r0); x2, y2 = pol(cx, cy, ang, r0 + length); lx, ly = pol(cx, cy, ang, r0 + length + 17)
    return ARROW(x1, y1, x2, y2, color, 3) + T(lx, ly + 6, label, 17, weight='bold')

def force(cx, cy, ang, length, label, r0=0, dx=0, dy=0, color=C_FORCE):
    x1, y1 = pol(cx, cy, ang, r0); x2, y2 = pol(cx, cy, ang, r0 + length); lx, ly = pol(cx, cy, ang, r0 + length + 22)
    return ARROW(x1, y1, x2, y2, color, 3) + (V(lx + dx, ly + 6 + dy, label, color) if label != '?' else T(lx + dx, ly + 7 + dy, '?', 20, weight='bold', color=color))

def plusx(x, y, length=55):
    return ARROW(x, y, x + length, y, INK, 2) + T(x + length + 4, y + 5, '+x', 15, 'start', italic=True)

def plusy(x, y, length=55):
    return ARROW(x, y, x, y - length, INK, 2) + T(x + 6, y - length + 4, '+y', 15, 'start', italic=True)

def spring_path(x1, y1, x2, y2, coils=8, amp=9):
    """نابض متعرّج بين نقطتين."""
    dx, dy = x2 - x1, y2 - y1; Ln = math.hypot(dx, dy); ux, uy = dx / Ln, dy / Ln; px, py = -uy, ux
    lead = 12; pts = [(x1, y1), (x1 + ux * lead, y1 + uy * lead)]
    n = coils * 2; seg = (Ln - 2 * lead) / n
    for k in range(n):
        s = lead + seg * (k + 0.5); sgn = 1 if k % 2 == 0 else -1
        pts.append((x1 + ux * s + px * amp * sgn, y1 + uy * s + py * amp * sgn))
    pts += [(x2 - ux * lead, y2 - uy * lead), (x2, y2)]
    return f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2"/>'

# ================= O14: أربعة مخططات جسم حر =================
def o14_fbds():
    W, H = 760, 270; b = ''; k = 2.0
    panels = [
        [(0, 30), (180, 30), (90, 20), (270, 20)],
        [(0, 40), (180, 20), (90, 20), (270, 20)],
        [(90, 30), (270, 20)],
        [(0, 30), (180, 30), (90, 20), (270, 30)],
    ]
    for i, fs in enumerate(panels):
        x0 = i * 190; cx, cy = x0 + 95, 140
        if i: b += L(x0, 15, x0, H - 15, GRID, 1.5)
        b += T(cx, 26, f'({i + 1})', 16, weight='bold')
        b += DOT(cx, cy, 6)
        for ang, mag in fs:
            x2, y2 = pol(cx, cy, ang, mag * k)
            b += ARROW(cx, cy, x2, y2, C_FORCE, 3)
            lx, ly = pol(cx, cy, ang, mag * k + 10)
            if ang == 0: b += T(x2 - 4, cy - 10, f'{mag} N', 13, 'end')
            elif ang == 180: b += T(x2 + 4, cy - 10, f'{mag} N', 13, 'start')
            elif ang == 90: b += T(cx + 8, y2 + 12, f'{mag} N', 13, 'start')
            else: b += T(cx + 8, y2 - 4, f'{mag} N', 13, 'start')
        b += plusx(x0 + 14, H - 22, 40) + plusy(x0 + 14, H - 22, 40)
    save('c4l1-o14-fbds.svg', svg(W, H, b))

def o14_vt():
    graph('c4l1-o14-vt.svg', [{'pts': [(0, 0), (2, 4), (5, 4), (7, 0)], 'color': C_VEL}], (0, 8), (0, 5),
          'الزمن (s)', 'السرعة المتجهة (m/s)', 1, 1)

# ================= O15: كرة تتدحرج على سطحين =================
def o15_surfaces():
    xa = [40]; xb = [40]; va, vb = 92, 92
    for _ in range(7): va -= 6; xa.append(xa[-1] + va)
    for st in (84, 60, 38, 22): xb.append(xb[-1] + st)
    motion_diagram('c4l1-o15-surfaces.svg', [{'label': 'A', 'xs': xa}, {'label': 'B', 'xs': xb}], w=640, row_h=80)

# ================= O16 =================
def box_on_floor(cx, cy, w=80, h=56):
    return RECT(cx - w / 2, cy - h / 2, w, h)

def o16_floor():
    W, H = 460, 320; cx, cy = 230, 190; b = ground(30, 430, cy + 28)
    b += box_on_floor(cx, cy)
    b += ARROW(cx - 150, cy - 120, cx - 70, cy - 120, C_VEL, 3) + V(cx - 56, cy - 114, 'v', C_VEL)
    b += cand(cx, cy, 0, 60, '1', 40) + cand(cx, cy, 180, 60, '2', 40) + cand(cx, cy, 90, 50, '3', 28)
    b += ARROW(cx, cy + 28, cx, cy + 80, C_FORCE, 3) + T(cx + 16, cy + 84, '4', 17, weight='bold')
    save('c4l1-o16-floor.svg', svg(W, H, b))

def incline_base(W, H, ang, x0=40, base_y=None):
    base_y = base_y or H - 30; x1 = W - 40; y1 = base_y - (x1 - x0) * math.tan(math.radians(ang))
    b = f'<polygon points="{x0},{base_y} {x1:.1f},{base_y} {x1:.1f},{y1:.1f}" fill="#f3efe6" stroke="{INK}" stroke-width="2"/>'
    a = math.radians(ang)
    b += f'<path d="M {x0 + 55} {base_y} A 55 55 0 0 0 {x0 + 55 * math.cos(a):.1f} {base_y - 55 * math.sin(a):.1f}" fill="none" stroke="{INK}" stroke-width="1.5"/>'
    b += T(x0 + 75, base_y - 9, f'{ang}', 15) + T(x0 + 88, base_y - 15, '°', 13)
    return b, x0, base_y, x1, y1

def box_on_incline(x0, y0, ang, frac_x, size=52):
    a = math.radians(ang); mx = x0 + frac_x; my = y0 - frac_x * math.tan(a)
    nx, ny = -math.sin(a), -math.cos(a); cx, cy = mx + size / 2 * nx, my + size / 2 * ny
    return RECT(cx - size / 2, cy - size / 2, size, size, rot=-ang, cx=round(cx, 1), cy=round(cy, 1)), cx, cy

def o16_incline():
    W, H = 520, 340; ang = 30; b, x0, y0, x1, y1 = incline_base(W, H, ang)
    r, cx, cy = box_on_incline(x0, y0, ang, 240); b += r
    vx1, vy1 = pol(cx, cy, 90 + ang, 72); b += ARROW(vx1 - 35 * math.cos(math.radians(ang)), vy1 + 35 * math.sin(math.radians(ang)), vx1 + 40 * math.cos(math.radians(ang)), vy1 - 40 * math.sin(math.radians(ang)), C_VEL, 3)
    b += V(vx1 + 54 * math.cos(math.radians(ang)), vy1 - 54 * math.sin(math.radians(ang)) + 4, 'v', C_VEL)
    b += cand(cx, cy, ang, 55, '1', 32) + cand(cx, cy, 180 + ang, 55, '2', 32) + cand(cx, cy, 90 + ang, 48, '3', 30) + cand(cx, cy, 270, 70, '4', 0)
    save('c4l1-o16-incline.svg', svg(W, H, b))

# ================= O17: مخطط جسم حر لصندوق يُسحب أفقيًا =================
def o17_fbd():
    W, H = 400, 320; cx, cy = 200, 160; b = DOT(cx, cy, 7)
    b += force(cx, cy, 90, 85, 'F_{N‍}') + force(cx, cy, 270, 85, 'F_g') + force(cx, cy, 0, 95, 'F_{T‍}') + force(cx, cy, 180, 60, '?')
    b += plusx(30, 290) + plusy(30, 290)
    save('c4l1-o17-fbd.svg', svg(W, H, b))

# ================= O19 =================
def o19_incline():
    W, H = 520, 360; ang = 30; b, x0, y0, x1, y1 = incline_base(W, H, ang)
    r, cx, cy = box_on_incline(x0, y0, ang, 250); b += r
    b += cand(cx, cy, 90, 62, '1', 30) + cand(cx, cy, 90 + ang, 62, '2', 30) + cand(cx, cy, ang, 60, '3', 32) + cand(cx, cy, 180, 62, '4', 30)
    save('c4l1-o19-incline.svg', svg(W, H, b))

def o19_wall():
    W, H = 460, 300; wx = 80; b = wall(wx, 30, 270)
    cx, cy = wx + 40, 150; b += RECT(cx - 40, cy - 30, 80, 60)
    # دفع اليد أفقيًا نحو الجدار
    b += ARROW(cx + 180, cy + 16, cx + 42, cy + 16, MUTED, 3) + T(cx + 130, cy + 40, 'دفع اليد', 14, color=MUTED)
    b += cand(cx, cy - 16, 0, 62, '1', 42) + cand(cx, cy, 90, 55, '2', 32) + cand(cx, cy, 270, 55, '3', 32)
    b += ARROW(cx - 20, cy + 18, wx - 40, cy + 18, C_FORCE, 3) + T(wx - 52, cy + 24, '4', 17, weight='bold')
    save('c4l1-o19-wall.svg', svg(W, H, b))

def o19_bowl():
    W, H = 480, 360; ox, oy, R = 240, 60, 250; b = ''
    # وعاء: قوس من دائرة مركزها O
    a1, a2 = math.radians(-150), math.radians(-30)
    p1 = (ox + R * math.cos(a1), oy - R * math.sin(a1)); p2 = (ox + R * math.cos(a2), oy - R * math.sin(a2))
    b += f'<path d="M {p1[0]:.1f} {p1[1]:.1f} A {R} {R} 0 0 0 {p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="{INK}" stroke-width="4"/>'
    b += DOT(ox, oy, 4, MUTED) + T(ox, oy - 10, 'O', 15, italic=True, color=MUTED) + L(ox, oy, ox, oy + R, GRID, 1.2, '5 5')
    th = -90 + 32; r = 16
    bx, by = ox + (R - r - 2) * math.cos(math.radians(th)), oy - (R - r - 2) * math.sin(math.radians(th))
    b += DOT(bx, by, r, INK, '#d6dbe4')
    toO = math.degrees(math.atan2(-(oy - by), ox - bx))
    b += cand(bx, by, 90, 60, '1', r) + cand(bx, by, toO, 60, '2', r) + cand(bx, by, toO - 90, 60, '3', r) + cand(bx, by, 270, 55, '4', r)
    save('c4l1-o19-bowl.svg', svg(W, H, b))

# ================= O20 =================
def o20_fbd():
    W, H = 420, 340; cx, cy = 210, 170; ang = 25; b = DOT(cx, cy, 7)
    b += force(cx, cy, 270, 95, 'F_g') + force(cx, cy, ang, 40, 'f_f', dy=-4) + force(cx, cy, 90 + ang, 86, '?')
    b += L(cx - 150 * math.cos(math.radians(ang)), cy + 150 * math.sin(math.radians(ang)) + 40, cx + 150 * math.cos(math.radians(ang)), cy - 150 * math.sin(math.radians(ang)) + 40, GRID, 1.5, '6 5')
    b += T(cx + 120, cy - 10 + 90, 'سطح المنحدر', 13, color=MUTED)
    b += plusy(30, 320) + ARROW(30, 320, 85, 320, INK, 2) + T(89, 325, '+x', 15, 'start', italic=True)
    save('c4l1-o20-fbd.svg', svg(W, H, b))

def o20_map():
    W, H = 560, 260; b = ''
    def node(x, y, t, sym=False):
        s = f'<ellipse cx="{x}" cy="{y}" rx="78" ry="28" fill="#e9f2e4" stroke="{INK}" stroke-width="1.6"/>'
        return s + (V(x, y + 6, t, C_FORCE) if sym else T(x, y + 6, t, 16, weight='bold'))
    top = (280, 40); mids = [(100, 130), (280, 130), (460, 130)]; bots = [(100, 220), (280, 220), (460, 220)]
    for m in mids: b += L(top[0], top[1] + 28, m[0], m[1] - 28, INK, 1.5)
    for m, n in zip(mids, bots): b += L(m[0], m[1] + 28, n[0], n[1] - 28, INK, 1.5)
    b += node(*top, 'القوة') + node(*mids[0], 'الشد') + node(*mids[1], '؟') + node(*mids[2], 'الجاذبية')
    b += node(*bots[0], '') + node(*bots[1], 'F_{N‍}', True) + node(*bots[2], '')
    save('c4l1-o20-map.svg', svg(W, H, b))

# ================= O22 =================
def spring_block(W, H, nat_x, blk_x, wall_x=50, floor_y=None, bw=70, bh=56):
    fy = floor_y or H - 50; b = wall(wall_x, fy - 120, fy) + ground(wall_x, W - 20, fy)
    cy = fy - bh / 2; b += spring_path(wall_x, cy, blk_x, cy, 9, 10) + RECT(blk_x, fy - bh, bw, bh)
    b += L(nat_x, fy - bh - 30, nat_x, fy + 4, MUTED, 1.5, '6 5') + T(nat_x, fy - bh - 38, 'طرف النابض وهو غير مشدود', 13, color=MUTED)
    return b, cy, fy

def o22_stretch():
    W, H = 560, 320; nat, blk = 220, 330; b, cy, fy = spring_block(W, H, nat, blk)
    bx = blk + 35
    b += ARROW(nat, fy + 22, blk, fy + 22, C_DISP, 3) + V((nat + blk) / 2, fy + 42, 'd', C_DISP)
    hy = fy - 47
    b += cand(bx, hy, 0, 55, '1', 36) + cand(bx, hy, 180, 55, '2', 36) + cand(bx, cy, 90, 50, '3', 28)
    b += ARROW(bx, fy, bx, fy + 50, C_FORCE, 3) + T(bx + 16, fy + 54, '4', 17, weight='bold')
    save('c4l1-o22-stretch.svg', svg(W, H + 34, b))

def o22_osc():
    W, H = 560, 300; nat, blk = 220, 300; b, cy, fy = spring_block(W, H, nat, blk)
    b += ARROW(blk + 60, cy - 50, blk - 10, cy - 50, C_VEL, 3) + V(blk - 24, cy - 44, 'v', C_VEL)
    save('c4l1-o22-osc.svg', svg(W, H, b))

def o22_two():
    W, H = 560, 420; b = ''
    for row, (blk, lab) in enumerate(((330, '(a)'), (140, '(b)'))):
        oy = row * 200; nat = 220; fy = oy + 170; bw, bh = 70, 56; cy = fy - bh / 2
        b += wall(50, fy - 110, fy) + ground(50, W - 20, fy) + spring_path(50, cy, blk, cy, 9, 10) + RECT(blk, fy - bh, bw, bh)
        b += L(nat, fy - bh - 26, nat, fy + 4, MUTED, 1.5, '6 5') + T(nat, fy - bh - 34, 'طرف النابض وهو غير مشدود', 13, color=MUTED)
        b += T(W - 30, oy + 40, lab, 16, weight='bold')
    save('c4l1-o22-two.svg', svg(W, H, b))

# ================= O23 =================
def o23_fbd():
    W, H = 360, 330; cx, cy = 180, 165; b = DOT(cx, cy, 7)
    b += force(cx, cy, 270, 100, 'F_g') + force(cx, cy, 90, 100, '?')
    b += plusy(40, 300)
    save('c4l1-o23-fbd.svg', svg(W, H, b))

def o23_scale():
    W, H = 340, 380; b = ceiling(100, 240, 30); cx = 170
    b += L(cx, 30, cx, 55, INK, 2) + RECT(cx - 34, 55, 68, 150, fill='#f4f6fa')
    b += spring_path(cx, 62, cx, 140, 7, 12)
    b += RECT(cx - 28, 150, 56, 30, fill='#1f2a44') + T(cx, 171, '24.5 N', 15, color='#e8f0ff')
    b += L(cx, 205, cx, 245, INK, 2) + RECT(cx - 32, 245, 64, 56, fill='#d6dbe4')
    save('c4l1-o23-scale.svg', svg(W, H - 50, b))

# ================= O25 =================
def o25_angle():
    W, H = 520, 320; fy = 250; cx, cy = 160, fy - 30; b = ground(30, 490, fy) + RECT(cx - 50, fy - 60, 100, 60)
    ax, ay = cx + 50, fy - 45; ang = 30
    hx, hy = pol(ax, ay, ang, 230); b += L(ax, ay, hx, hy, '#8a6d3b', 3) + DOT(hx, hy, 6, MUTED) + T(hx + 10, hy + 2, 'يد', 13, 'start', MUTED)
    b += DOT(ax, ay, 4)
    b += cand(ax, ay, ang, 70, '1', 0) + cand(ax, ay, 0, 70, '2', 0) + cand(ax, ay, 90, 70, '3', 0) + cand(ax, ay, 180 + ang, 55, '4', 0)
    save('c4l1-o25-angle.svg', svg(W, H, b))

def o25_pendulum():
    W, H = 440, 380; px, py = 160, 40; b = ceiling(90, 260, py); Lr = 230; th = 28
    bx, by = px + Lr * math.sin(math.radians(th)), py + Lr * math.cos(math.radians(th))
    b += L(px, py, bx, by, '#8a6d3b', 2.5) + L(px, py, px, py + Lr + 10, GRID, 1.2, '5 5') + DOT(bx, by, 18, INK, '#d6dbe4')
    up = math.degrees(math.atan2(by - py, px - bx))  # نحو نقطة التعليق
    b += cand(bx, by, 90, 55, '1', 18) + cand(bx, by, 0, 55, '3', 18) + cand(bx, by, up + 180, 55, '4', 18)
    # السهم 2 على امتداد الخيط نحو نقطة التعليق، مزاح قليلًا كي لا يختفي تحت الخيط
    sx, sy = pol(bx, by, up - 90, 9); b += cand(sx, sy, up, 62, '2', 20)
    save('c4l1-o25-pendulum.svg', svg(W, H, b))

def blocks_train(name, labels=False):
    W, H = 600, 200; fy = 150; b = ground(20, 580, fy)
    specs = [(40, 70, 50, 'm_1', '2.0 kg'), (210, 90, 62, 'm_2', '4.0 kg'), (400, 110, 76, 'm_3', '6.0 kg')]
    for x, w, h, m, kg in specs:
        b += RECT(x, fy - h, w, h) + T(x + w / 2, fy - h / 2 + 6, m, 16, italic=True) + T(x + w / 2, fy - h - 10, kg, 14)
    ys = fy - 22
    b += L(110, ys, 210, ys, '#8a6d3b', 3) + L(300, ys, 400, ys, '#8a6d3b', 3)
    if labels:
        b += T(160, ys - 12, 'الخيط 1', 13, color=MUTED) + T(350, ys - 12, 'الخيط 2', 13, color=MUTED)
    b += ARROW(510, fy - 38, 575, fy - 38, C_FORCE, 3) + V(560, fy - 50, 'F', C_FORCE)
    save(name, svg(W, H, b))

# ================= O26 =================
def o26_fbd():
    W, H = 360, 330; cx, cy = 180, 165; b = DOT(cx, cy, 7)
    b += force(cx, cy, 270, 90, 'F_g') + force(cx, cy, 90, 90, '?')
    b += plusy(40, 300)
    save('c4l1-o26-fbd.svg', svg(W, H, b))

if __name__ == '__main__':
    o14_fbds(); o14_vt(); o15_surfaces(); o16_floor(); o16_incline(); o17_fbd(); o19_incline(); o19_wall(); o19_bowl()
    o20_fbd(); o20_map(); o22_stretch(); o22_osc(); o22_two(); o23_fbd(); o23_scale(); o25_angle(); o25_pendulum()
    blocks_train('c4l1-o25-blocks.svg', True); o26_fbd()
