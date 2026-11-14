# رسوم الدرس 5-1 (هاليدات الألكيل وهاليدات الأريل) — النصف الثاني: تفاعلات الاستبدال والهلجنة، ومقارنة التراكيب،
# ودرجات الغليان، وCFCs/HFCs. التشغيل: python3 data/chem22/gen/figs/C5-L1-b.py
# يستورد أدوات رسم البنى من C5-L1-a.py (دون تعديله).
import sys, os, importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from figures import *
_spec = importlib.util.spec_from_file_location('c5l1a', os.path.join(os.path.dirname(__file__), 'C5-L1-a.py'))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)
mol, M, full, chain, cond, ring, single, grid, TL, U = A.mol, A.M, A.full, A.chain, A.cond, A.ring, A.single, A.grid, A.TL, A.U

P = 'c5-l1b-'

def scheme(name, items, pad=24, gap=22, arrow_len=110):
    """مخطط تفاعل أفقي من اليسار إلى اليمين. items: ('m', mol) أو ('t', نص لاتيني) أو ('a', تسمية فوق السهم)."""
    parts = []
    for kind, v in items:
        if kind == 'm':
            _, bb = mol(v); parts.append((kind, v, bb[2] - bb[0], bb[3] - bb[1], bb))
        elif kind == 't':
            w = A.lab_size(v, 22)[0] * 2 + 6; parts.append((kind, v, w, 24, None))
        else:
            parts.append((kind, v, arrow_len, 20, None))
    H = max(p[3] for p in parts) + 2 * pad + 20
    W = sum(p[2] for p in parts) + gap * (len(parts) - 1) + 2 * pad
    cy = H / 2 + 6
    x = pad; b = ''
    for kind, v, w, h, bb in parts:
        if kind == 'm':
            bd, _ = mol(v, x - bb[0], cy - (bb[1] + bb[3]) / 2); b += bd
        elif kind == 't':
            b += TL(x + w / 2, cy + 8, v, 22)
        else:
            b += ARROW(x + 4, cy, x + w - 4, cy)
            if v: b += TL(x + w / 2, cy - 12, v, 18)
        x += w + gap
    save(name, svg(round(W), round(H), b))

def naphthalene(subs=None):
    """النفثالين: حلقتا بنزين ملتحمتان (سداسيان رأساهما إلى أعلى يشتركان في ضلع رأسي)، ودائرة في كل حلقة.
    subs = {i: X} على رؤوس الحلقة اليسرى غير المشتركة: 0 أعلى (الموقع 1)، 5 أعلى اليسار، 4 أسفل اليسار، 3 أسفل."""
    import math as _m
    subs = subs or {}
    V = [(_m.cos(-_m.pi / 2 + _m.pi / 3 * i), _m.sin(-_m.pi / 2 + _m.pi / 3 * i)) for i in range(6)]
    dx = _m.sqrt(3)
    nodes = {f'a{i}': (x, y, '') for i, (x, y) in enumerate(V)}
    right = {0: 'b0', 1: 'b1', 2: 'b2', 3: 'b3', 4: 'a2', 5: 'a1'}
    for i in range(4):
        x, y = V[i]; nodes[f'b{i}'] = (x + dx, y, '')
    edges = [(f'a{i}', f'a{(i + 1) % 6}', 1) for i in range(6)]
    edges += [(right[i], right[(i + 1) % 6], 1) for i in range(6) if {right[i], right[(i + 1) % 6]} != {'a1', 'a2'}]
    for i, s in subs.items():
        x, y = V[i]; d = _m.hypot(x, y); ux, uy = x / d, y / d
        hw, hh = A.lab_size(s)
        t = min(hw / abs(ux) if abs(ux) > 1e-6 else 1e9, hh / abs(uy) if abs(uy) > 1e-6 else 1e9) / U
        nodes[f's{i}'] = (x + ux * (0.72 + t), y + uy * (0.72 + t), s); edges.append((f'a{i}', f's{i}', 1))
    return M(nodes, edges, [(0, 0, 0.6), (dx, 0, 0.6)])

def bars_q(name, data, w=620, h=380, ymin=-20, ymax=160, step=20):
    """أعمدة درجات الغليان مع خط الصفر؛ القيمة None تعني عمودًا مجهولًا يُرسم مكانه «؟»."""
    X0, Y0, X1, Y1 = 80, h - 70, w - 20, 30
    def py(v): return Y0 - (v - ymin) / (ymax - ymin) * (Y0 - Y1)
    b = ARROW(X0, Y0, X0, Y1 - 10)
    for v in range(ymin, ymax + 1, step):
        b += L(X0 - 5, py(v), X0, py(v)) + T(X0 - 9, py(v) + 5, str(v).replace('-', '−'), 13, 'end')
        if v: b += L(X0, py(v), X1 - 10, py(v), '#d5dbe3', 1)
    b += L(X0, py(0), X1 - 10, py(0), INK, 2)
    n = len(data); slot = (X1 - X0 - 20) / n
    for i, (lab, v) in enumerate(data):
        cx = X0 + 10 + slot * (i + 0.5); bw = slot * 0.5
        if v is None:
            b += T(cx, py(0) - 12, '؟', 30, color=RED, weight='bold')
        else:
            top, bot = (py(v), py(0)) if v >= 0 else (py(0), py(v))
            b += f'<rect x="{cx - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{max(bot - top, 2):.1f}" fill="{BLUE}"/>'
            b += TL(cx, min(top, py(0)) - 7, f'{v:g}'.replace('-', '−'), 14, INK)
        b += TL(cx, Y0 + 24, lab, 15, INK)
    b += f'<text transform="translate({X0 - 50},{(Y0 + Y1) / 2}) rotate(-90)" text-anchor="middle" font-size="14" fill="{INK}" font-weight="bold" {FONT} direction="rtl">درجة الغليان</text>'
    b += TL(X0 + 8, Y1 - 4, '°C', 14, INK, 'start')
    b += T((X0 + X1) / 2, h - 12, 'المركب', 14, weight='bold')
    save(name, svg(w, h, b))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # ===== O06: معادلات الاستبدال =====
    scheme(P + 'bromobutane-oh.svg', [('m', chain(4, {(4, 0): 'Br'})), ('t', '+'), ('t', 'OH⁻'), ('a', ''), ('t', '?')])
    scheme(P + 'bromopropane-nh3.svg', [('m', chain(3, {(1, -1): 'Br'})), ('t', '+'), ('t', 'NH₃'), ('a', ''), ('t', '?')])
    scheme(P + 'methane-route.svg', [('t', 'CH₄'), ('a', 'Br₂'), ('t', 'A'), ('a', 'OH⁻'), ('t', 'B')], arrow_len=100)
    # ===== O07: مقارنة التراكيب =====
    # (أ) 4-كلورو تولوين: الكلور على الحلقة؛ (ب) C₆H₅CH₂Cl: الكلور على CH₂ خارج الحلقة — الصيغة نفسها C₇H₇Cl
    bz = ring(6, {0: 'CH₂'}, arom=True)
    x0, y0, _ = bz['nodes']['s0']
    bz['nodes']['cl'] = (x0, y0 - 1.1, 'Cl'); bz['edges'].append(('s0', 'cl', 1))
    grid(P + 'c7h7cl-pair.svg', [('(أ)', ring(6, {0: 'CH₃', 3: 'Cl'}, arom=True)), ('(ب)', bz)])
    mx = ring(6, {0: 'CH₂', 3: 'Br'}, arom=True)
    x0, y0, _ = mx['nodes']['s0']
    mx['nodes']['cl'] = (x0, y0 - 1.1, 'Cl'); mx['edges'].append(('s0', 'cl', 1))
    single(P + 'mixed-halide.svg', mx)
    single(P + 'bromonaphthalene.svg', naphthalene({0: 'Br'}))
    # ===== O08: درجات الغليان =====
    bars_q(P + 'butyl-bars.svg', [('C₄H₁₀', -0.5), ('C₄H₉F', 32), ('C₄H₉Cl', 78), ('C₄H₉Br', None), ('C₄H₉I', 131)])
    # ===== O09: الهلجنة =====
    single(P + 'propane.svg', chain(3))
    single(P + 'pentane.svg', chain(5))
    # ===== O10: CFCs وHFCs =====
    one = lambda subs: full({'c': (0, 0)}, [], subs=subs)
    grid(P + 'which-hfc.svg', [('(أ)', one({(-1, 0): 'Cl', (1, 0): 'Cl', (0, -1): 'Cl', (0, 1): 'F'})),
                               ('(ب)', one({(-1, 0): 'Cl', (1, 0): 'Cl'})),
                               ('(ج)', chain(2, {(2, 0): 'F', (1, -1): 'F'})),
                               ('(د)', chain(2, {(-1, 0): 'Cl', (0, -1): 'F', (0, 1): 'F', (2, 0): 'Cl', (1, -1): 'F', (1, 1): 'F'}))])
    grid(P + 'classify-cfc.svg', [('(أ)', one({(-1, 0): 'Cl', (1, 0): 'F', (0, -1): 'F', (0, 1): 'F'})),
                                  ('(ب)', one({(-1, 0): 'F', (1, 0): 'F'})),
                                  ('(ج)', one({(-1, 0): 'Cl', (1, 0): 'Cl', (0, -1): 'Cl'})),
                                  ('(د)', chain(2, {(2, 0): 'F', (1, -1): 'F', (1, 1): 'F'}))])
