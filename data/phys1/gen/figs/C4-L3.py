import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *
# رسوم الدرس 4-3 (قوى التأثير المتبادل) — الأهداف O01–O13
import math

ARFONT = FONT


def FS(x, y, sub, color=C_FORCE, size=17, anchor='middle', tail=''):
    """رمز قوة كالكتاب: F عريض مائل وتحته حرف سفلي (قد يكون «A في B»)؛ النص من اليسار لليمين كما يظهر في الكتاب."""
    rtl_sub = bool(re.search('[؀-ۿ]', sub))
    sf = ARFONT if rtl_sub else MATHFONT
    t = f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{color}" direction="ltr" {MATHFONT}>'
    t += f'<tspan font-weight="bold" font-style="italic">F</tspan>'
    t += f'<tspan dy="0.32em" font-size="{int(size * 0.66)}" {sf}>{esc(sub)}</tspan>'
    if tail: t += f'<tspan dy="-0.32em" font-size="{int(size * 0.9)}">{esc(tail)}</tspan>'
    return t + '</text>'


def NUM(x, y, n, color=INK):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#fff" stroke="{color}" stroke-width="1.5"/>' + T(x, y + 5, str(n), 14, color=color)


def plus_arrow(x, y, length=70, label='+y'):
    return ARROW(x, y, x, y - length, INK, 2) + T(x + 8, y - length + 6, label, 15, 'start', italic=True)


def plus_x(x, y, length=70, label='+x'):
    return ARROW(x, y, x + length, y, INK, 2) + T(x + length + 4, y + 5, label, 15, 'start', italic=True)


def person(cx, feet_y, hgt=130, col='#c9b79c', face=1):
    head_r = hgt * 0.09; b = ''
    top = feet_y - hgt
    b += f'<circle cx="{cx}" cy="{top + head_r:.1f}" r="{head_r:.1f}" fill="#e8cfae" stroke="{INK}" stroke-width="1.5"/>'
    b += f'<rect x="{cx - hgt * 0.12:.1f}" y="{top + 2 * head_r + 3:.1f}" width="{hgt * 0.24:.1f}" height="{hgt * 0.42:.1f}" rx="8" fill="{col}" stroke="{INK}" stroke-width="1.5"/>'
    leg_top = top + 2 * head_r + 3 + hgt * 0.42
    b += L(cx - hgt * 0.05, leg_top, cx - hgt * 0.08, feet_y, INK, 5) + L(cx + hgt * 0.05, leg_top, cx + hgt * 0.08, feet_y, INK, 5)
    return b


def bucket(cx, top, w=56, h=52, fill='#cfe0ef'):
    """دلو: حافته العلوية عند top، ومقبضه فوقها."""
    b = f'<path d="M {cx - w / 2} {top} L {cx + w / 2} {top} L {cx + w / 2 - 8} {top + h} L {cx - w / 2 + 8} {top + h} Z" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
    b += f'<path d="M {cx - w / 2 + 2} {top} Q {cx} {top - 34} {cx + w / 2 - 2} {top}" fill="none" stroke="{INK}" stroke-width="2"/>'
    return b


def ceiling(x1, x2, y):
    b = RECT(x1, y - 12, x2 - x1, 12, INK, '#d5d9e0', 1.5)
    for k in range(int((x2 - x1) // 16)):
        b += L(x1 + 6 + k * 16, y - 12, x1 + k * 16 - 2, y - 20, MUTED, 1.2)
    return b


def ground(x1, x2, y, fill='#e9e2d0'):
    return RECT(x1, y, x2 - x1, 16, INK, fill, 1.5)


def BOX(cx, cy, w, h, label='', fill='#eef2f8', size=16):
    return RECT(cx - w / 2, cy - h / 2, w, h, INK, fill, 2) + (T(cx, cy + 6, label, size) if label else '')


# ---------------- O02: المتزلجان مرسومان منفصلين ----------------
def skaters():
    w, h = 520, 250; b = ''
    b += ground(20, 500, 200)
    b += person(170, 200, 140, '#9fb3c8') + person(350, 200, 140, '#d7b8b8')
    b += T(170, 228, 'A', 17, italic=True) + T(350, 228, 'B', 17, italic=True)
    # القوة في B من A إلى اليمين، والقوة في A من B إلى اليسار (متساويتان)
    b += ARROW(350, 110, 460, 110, C_FORCE, 3.5) + FS(420, 95, 'A في B')
    b += ARROW(170, 110, 60, 110, C_FORCE, 3.5) + FS(100, 95, 'B في A')
    b += DOT(350, 110, 4, C_FORCE) + DOT(170, 110, 4, C_FORCE)
    save('c4l3-o02-skaters.svg', svg(w, h, b))


# ---------------- O03: جسمان منفصلان، والقوة في A مجهولة ----------------
def pair_unknown():
    w, h = 520, 210; b = ''
    b += ground(20, 500, 150)
    b += BOX(160, 115, 90, 70, 'A') + BOX(360, 115, 90, 70, 'B')
    b += ARROW(405, 115, 485, 115, C_FORCE, 3.5) + FS(445, 62, 'A في B', tail=' = 24 N')
    b += T(85, 120, '?', 26, color=C_FORCE, weight='bold')
    b += plus_x(30, 190, 60)
    save('c4l3-o03-pair.svg', svg(w, h, b))


# ---------------- O04: كرة على طاولة على الأرض، كل جسم منفصل مع أسهم مرقمة ----------------
def ball_table_numbered():
    w, h = 520, 400; b = ''
    # الكرة
    bx, by = 260, 90
    b += f'<circle cx="{bx}" cy="{by}" r="22" fill="#f3d36b" stroke="{INK}" stroke-width="1.8"/>' + T(330, by + 5, 'الكرة', 15, color=MUTED)
    b += ARROW(bx, by - 22, bx, by - 70, C_FORCE, 3) + NUM(bx - 24, by - 55, 1)
    b += ARROW(bx, by + 22, bx, by + 75, C_FORCE, 3) + NUM(bx - 24, by + 62, 2)
    # الطاولة
    ty = 235
    b += RECT(170, ty - 10, 180, 16, INK, '#d8c3a5', 2) + RECT(185, ty + 6, 12, 70, INK, '#d8c3a5', 2) + RECT(323, ty + 6, 12, 70, INK, '#d8c3a5', 2)
    b += T(410, ty + 5, 'الطاولة', 15, color=MUTED)
    b += ARROW(260, ty - 10, 260, ty + 50, C_FORCE, 3) + NUM(282, ty + 34, 3)
    b += ARROW(180, ty - 10, 180, ty - 65, C_FORCE, 3) + NUM(158, ty - 50, 4)
    b += ARROW(340, ty + 6, 340, ty + 75, C_FORCE, 3) + NUM(362, ty + 60, 5)
    # الأرض
    b += f'<path d="M 60 390 Q 260 330 460 390 Z" fill="#cfe3d2" stroke="{INK}" stroke-width="1.8"/>' + T(260, 382, 'الأرض', 15, color=MUTED)
    save('c4l3-o04-ball-table.svg', svg(w, h, b))


# ---------------- O05: مكعبان متراكبان على طاولة ----------------
def cubes():
    w, h = 360, 280; b = ''
    b += RECT(60, 220, 240, 14, INK, '#d8c3a5', 2) + RECT(75, 234, 12, 40, INK, '#d8c3a5', 2) + RECT(273, 234, 12, 40, INK, '#d8c3a5', 2)
    b += BOX(180, 175, 90, 90, '7.0 kg', '#dfe5ee') + BOX(180, 100, 60, 60, '6.0 kg', '#c9d3df', 14)
    b += plus_arrow(30, 200, 70)
    save('c4l3-o05-cubes.svg', svg(w, h, b))


def two_boxes_push():
    w, h = 520, 200; b = ''
    b += ground(20, 500, 150)
    b += BOX(230, 115, 90, 70, '4.3 kg') + BOX(325, 115, 100, 70, '5.4 kg')
    b += ARROW(100, 115, 183, 115, C_FORCE, 3.5) + T(140, 100, '22.5 N', 15, color=C_FORCE)
    b += plus_x(400, 185, 60)
    b += T(260, 185, 'سطح أفقي مهمل الاحتكاك', 14, color=MUTED)
    save('c4l3-o05-push.svg', svg(w, h, b))


# ---------------- O06: حبل أفقي يُسحب من طرفيه ونقاط عليه ----------------
def rope_points():
    w, h = 540, 170; b = ''
    y = 85
    b += L(110, y, 430, y, '#8a6d3b', 5)
    for x, n in ((170, 'P'), (270, 'Q'), (370, 'R')):
        b += DOT(x, y, 5, INK) + T(x, y - 14, n, 16, italic=True)
    b += ARROW(110, y, 30, y, C_FORCE, 3.5) + T(70, y + 26, '400 N', 15, color=C_FORCE)
    b += ARROW(430, y, 510, y, C_FORCE, 3.5) + T(470, y + 26, '400 N', 15, color=C_FORCE)
    b += T(270, 150, 'الحبل ساكن ومهمل الكتلة', 14, color=MUTED)
    save('c4l3-o06-rope-points.svg', svg(w, h, b))


def hanging_points():
    w, h = 300, 330; b = ''
    b += ceiling(60, 240, 30)
    b += L(150, 30, 150, 246, '#8a6d3b', 3.5)
    for yy, n in ((70, 'X'), (140, 'Y'), (210, 'Z')):
        b += DOT(150, yy, 5, INK) + T(168, yy + 5, n, 16, 'start', italic=True)
    b += bucket(150, 262)
    b += T(205, 300, 'الوزن:', 14, 'start', MUTED) + T(230, 320, '120 N', 14, color=MUTED)
    save('c4l3-o06-hanging.svg', svg(w, h, b))


# ---------------- O07: أربعة مخططات للدلو الساكن ----------------
def bucket_fbds():
    w, h = 600, 260; b = ''
    sets = [(70, 70), (70, 40), (40, 70), (0, 70)]  # (F_T, F_g) بالبكسل
    for i, (ft, fg) in enumerate(sets):
        cx, cy = 75 + i * 150, 120
        b += DOT(cx, cy, 7)
        if ft: b += ARROW(cx, cy, cx, cy - ft, C_FORCE, 3) + V(cx + 12, cy - ft * 0.6, 'F_{T}', C_FORCE, 16, 'start')
        b += ARROW(cx, cy, cx, cy + fg, C_FORCE, 3) + V(cx + 12, cy + fg * 0.7, 'F_{g}', C_FORCE, 16, 'start')
        b += T(cx, 240, f'({i + 1})', 16)
        if i: b += L(cx - 75, 20, cx - 75, 230, GRID, 1.5)
    b += plus_arrow(18, 120, 60)
    save('c4l3-o07-bucket-fbds.svg', svg(w, h, b))


# ---------------- O09: قطعتا طوب معلقتان بحبلين ----------------
def bricks():
    w, h = 340, 360; b = ''
    b += ceiling(80, 260, 30)
    b += L(170, 30, 170, 120, '#8a6d3b', 3.5) + T(185, 80, 'الحبل العلوي', 14, 'start', MUTED)
    b += RECT(130, 120, 80, 50, INK, '#c97a5a', 2) + T(170, 151, '5.0 kg', 14, color='#fff')
    b += L(170, 170, 170, 250, '#8a6d3b', 3.5) + T(185, 215, 'الحبل السفلي', 14, 'start', MUTED)
    b += RECT(130, 250, 80, 50, INK, '#c97a5a', 2) + T(170, 281, '5.0 kg', 14, color='#fff')
    b += plus_arrow(50, 300, 70)
    save('c4l3-o09-bricks.svg', svg(w, h, b))


def bucket_up():
    w, h = 340, 340; b = ''
    b += L(150, 10, 150, 194, '#8a6d3b', 3.5)
    b += bucket(150, 210, 70, 64, '#bfe3c6')
    b += T(150, 250, '50.0 kg', 14)
    b += ARROW(240, 220, 240, 130, C_VEL, 3) + V(256, 175, 'v', C_VEL, 18, 'start')
    b += ARROW(290, 210, 290, 150, C_ACC, 3) + V(304, 185, 'a', C_ACC, 18, 'start')
    b += f'<text x="265" y="255" text-anchor="middle" font-size="15" fill="{INK}" {MATHFONT}><tspan font-style="italic">a</tspan> = 1.5 m/s<tspan dy="-0.45em" font-size="10">2</tspan></text>'
    b += plus_arrow(45, 300, 80)
    save('c4l3-o09-bucket-up.svg', svg(w, h, b))


# ---------------- O10: سلم على جدار أملس، وكرة في مجرى على شكل V ----------------
def ladder():
    w, h = 420, 340; b = ''
    b += ground(20, 400, 300)
    b += RECT(300, 20, 24, 280, INK, '#dcd6c8', 2)  # الجدار على اليمين
    x1, y1, x2, y2 = 130, 300, 300, 130   # السلم من الأرض إلى الجدار
    b += L(x1, y1, x2, y2, '#8a6d3b', 7) + L(x1 + 14, y1, x2 + 0, y2 + 17, '#8a6d3b', 0)
    cx, cy = 300, 130
    b += DOT(cx, cy, 5, INK)
    arrows = [(180, 1), (90, 2), (math.degrees(math.atan2(y1 - y2, -(x1 - x2))) + 180, 3), (270, 4)]
    # 1: أفقي بعيدًا عن الجدار (يسار)، 2: رأسي لأعلى، 3: على امتداد السلم إلى أسفل، 4: رأسي لأسفل
    nl = math.hypot(x1 - x2, y1 - y2)
    dirs = [(-1, 0), (0, -1), (-(y1 - y2) / nl, (x1 - x2) / nl), (0, 1)]
    for (dx, dy), n in zip(dirs, (1, 2, 3, 4)):
        ln = 70
        b += ARROW(cx, cy, cx + dx * ln, cy + dy * ln, C_FORCE, 3) + NUM(cx + dx * (ln + 20), cy + dy * (ln + 20), n)
    b += T(312, 330, 'جدار', 14, color=MUTED)
    save('c4l3-o10-ladder.svg', svg(w, h, b))


def vgroove():
    w, h = 440, 330; b = ''
    # جداران مائلان بزاوية 45° يلتقيان في الأسفل
    bx, by = 220, 290
    b += f'<polygon points="{bx},{by} {bx - 170},{by - 170} {bx - 190},{by - 170} {bx - 190},{by + 20} {bx + 190},{by + 20} {bx + 190},{by - 170} {bx + 170},{by - 170}" fill="#e9e2d0" stroke="{INK}" stroke-width="2"/>'
    r = 60; cx, cy = bx, by - r * math.sqrt(2)
    b += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="#f3d36b" fill-opacity="0.55" stroke="{INK}" stroke-width="1.8"/>'
    # نقطة التلامس مع الجدار الأيمن
    px, py = cx + r / math.sqrt(2), cy + r / math.sqrt(2)
    b += DOT(px, py, 5, INK)
    s2 = 1 / math.sqrt(2)
    dirs = [((0, -1), 1), ((-s2, -s2), 2), ((s2, -s2), 3), ((-1, 0), 4)]
    for (dx, dy), n in dirs:
        ln = 75
        b += ARROW(px, py, px + dx * ln, py + dy * ln, C_FORCE, 3) + NUM(px + dx * (ln + 20), py + dy * (ln + 20), n)
    b += T(bx + 120, by + 2, '45°', 15) + T(bx - 120, by + 2, '45°', 15)
    save('c4l3-o10-vgroove.svg', svg(w, h, b))


# ---------------- O11: صندوق في ثلاث حالات (الشكل 4-18 بأرقام جديدة) ----------------
def three_boxes():
    w, h = 600, 300; b = ''
    for i, case in enumerate(('none', 'pull', 'push')):
        cx = 100 + i * 200; top = 140
        b += ground(cx - 85, cx + 85, 230)
        b += BOX(cx, 190, 90, 80, '', '#e3cfa8')
        b += T(cx, 285, f'({i + 1})', 16)
        if case == 'pull':
            b += L(cx, 150, cx, 70, '#8a6d3b', 2.5) + ARROW(cx + 30, 110, cx + 30, 55, C_FORCE, 3) + T(cx + 38, 80, '30.0 N', 14, 'start', C_FORCE) + T(cx - 10, 62, 'خيط', 13, 'end', MUTED)
        if case == 'push':
            b += ARROW(cx + 30, 70, cx + 30, 140, C_FORCE, 3) + T(cx + 38, 100, '30.0 N', 14, 'start', C_FORCE) + T(cx - 10, 100, 'يد تضغط', 13, 'end', MUTED)
        b += T(cx, 195, '10.0 kg', 14)
        if i: b += L(cx - 100, 20, cx - 100, 270, GRID, 1.5)
    save('c4l3-o11-three.svg', svg(w, h, b))


def rank_four():
    w, h = 640, 270; b = ''
    for i in range(4):
        cx = 85 + i * 157
        b += ground(cx - 65, cx + 65, 220)
        b += BOX(cx, 185, 70, 70, '', '#9fb7d6')
        b += T(cx, 262, f'({i + 1})', 16)
        if i == 1:   # خيط يسحب إلى أعلى بقوة 20 N
            b += L(cx, 150, cx, 40, '#8a6d3b', 2.5) + ARROW(cx + 22, 120, cx + 22, 70, C_FORCE, 3) + T(cx + 28, 90, '20 N', 14, 'start', C_FORCE)
        if i == 2:   # ثقل 20 N فوقه
            b += RECT(cx - 20, 125, 40, 25, INK, '#f0c419', 1.8) + T(cx, 118, '20 N', 13)
        if i == 3:   # خيط يسحب بقوة 40 N
            b += L(cx, 150, cx, 40, '#8a6d3b', 2.5) + ARROW(cx + 22, 120, cx + 22, 70, C_FORCE, 3) + T(cx + 28, 90, '40 N', 14, 'start', C_FORCE)
        b += T(cx, 190, '60 N', 14)
        if i: b += L(cx - 78, 20, cx - 78, 245, GRID, 1.5)
    save('c4l3-o11-rank.svg', svg(w, h, b))


# ---------------- O12: كتاب على طاولة — مخططا الجسم الحر لكل منهما ----------------
def book_table_fbds():
    w, h = 560, 340; b = ''
    # الكتاب (يسار)
    cx, cy = 140, 165
    b += RECT(cx - 40, cy - 12, 80, 24, INK, '#c0504d', 2) + T(cx, 300, 'الكتاب', 15, color=MUTED)
    b += ARROW(cx, cy - 12, cx, cy - 92, C_FORCE, 3) + NUM(cx + 24, cy - 70, 1)
    b += ARROW(cx, cy + 12, cx, cy + 92, C_FORCE, 3) + NUM(cx + 24, cy + 70, 2)
    b += L(280, 20, 280, 310, GRID, 1.5)
    # الطاولة (يمين)
    tx, ty = 420, 150
    b += RECT(tx - 90, ty, 180, 16, INK, '#d8c3a5', 2) + RECT(tx - 78, ty + 16, 12, 70, INK, '#d8c3a5', 2) + RECT(tx + 66, ty + 16, 12, 70, INK, '#d8c3a5', 2)
    b += T(tx - 10, 310, 'الطاولة', 15, color=MUTED)
    b += ARROW(tx, ty, tx, ty + 70, C_FORCE, 3) + NUM(tx + 22, ty + 55, 3)
    b += ARROW(tx - 70, ty, tx - 70, ty - 90, C_FORCE, 3) + NUM(tx - 92, ty - 70, 4)
    b += ARROW(tx + 72, ty + 86, tx + 72, ty + 136, C_FORCE, 3) + NUM(tx + 50, ty + 125, 5)
    save('c4l3-o12-book-table.svg', svg(w, h, b))


# ---------------- O13: الكرة والأرض كنظامين (مثال تسارع الأرض) ----------------
def ball_earth():
    w, h = 440, 350; b = ''
    b += f'<circle cx="150" cy="260" r="85" fill="#7fb2d9" stroke="{INK}" stroke-width="2"/>' + T(150, 266, 'الأرض', 16)
    b += T(150, 320, '6.0 × 10^{24} kg', 13)
    b += f'<circle cx="150" cy="30" r="14" fill="#f3f3f3" stroke="{INK}" stroke-width="1.8"/>' + T(190, 36, 'الكرة', 14, 'start') + T(255, 36, '0.18 kg', 14, 'start')
    b += ARROW(150, 44, 150, 94, C_FORCE, 3) + T(126, 78, '1', 15, color=C_FORCE, weight='bold')
    b += ARROW(150, 175, 150, 125, C_FORCE, 3) + T(126, 150, '2', 15, color=C_FORCE, weight='bold')
    b += f'<path d="M 140 70 Q 90 110 140 150" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    b += plus_arrow(330, 160, 80)
    save('c4l3-o13-ball-earth.svg', svg(w, h, b))


if __name__ == '__main__':
    skaters(); pair_unknown(); ball_table_numbered(); cubes(); two_boxes_push(); rope_points(); hanging_points()
    bucket_fbds(); bricks(); bucket_up(); ladder(); vgroove(); three_boxes(); rank_four(); book_table_fbds(); ball_earth()
