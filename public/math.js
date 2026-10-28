// الرموز الرياضية في نصوص الأسئلة: ‎$…$‎ داخل السطر و‎$$…$$‎ في سطر مستقل (صيغة LaTeX)، و‎\$‎ لعلامة الدولار نفسها.
// مثل bidi.js: تُعالَج عقد النص المعروضة فقط (لا يُكتب شيء في قاعدة البيانات، ولا تُمس الحقول التي يكتب فيها المستخدم)،
// فتعمل في كل الصفحات: التدريب، وصفحة الهدف، والبنك، ومنشئ الاختبارات، والطباعة.
// مكتبة KaTeX تُحمَّل عند أول نص فيه رموز فقط؛ وإن تعذر تحميلها يظهر نص الصيغة كما هو في اتجاه من اليسار لليمين.
const KATEX = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.mjs';
const KATEX_CSS = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css';
const SKIP = new Set(['INPUT', 'TEXTAREA', 'SELECT', 'OPTION', 'SCRIPT', 'STYLE', 'CODE', 'PRE', 'NOSCRIPT']);
const PAIR = /\$\$[\s\S]+?\$\$|(?<!\\)\$[^$\n]+?(?<!\\)\$/;

// هل في النص صيغة رياضية مكتملة (زوج من علامات الدولار)؟
export const hasMath = s => !!s && s.includes('$') && PAIR.test(s);

// تقسيم النص إلى مقاطع: نص عادي، أو صيغة (display: في سطر مستقل)
export function tokenize(s) {
  const out = [];
  let buf = '', i = 0;
  const flush = () => { if (buf) out.push({ math: false, v: buf }); buf = ''; };
  while (i < s.length) {
    if (s[i] === '\\' && s[i + 1] === '$') { buf += '$'; i += 2; continue; }
    if (s[i] === '$') {
      const display = s[i + 1] === '$';
      const open = display ? 2 : 1;
      let j = i + open, end = -1;
      while (j < s.length) {
        if (s[j] === '\\') { j += 2; continue; }
        if (display ? s.startsWith('$$', j) : s[j] === '$') { end = j; break; }
        if (!display && s[j] === '\n') break;
        j++;
      }
      const tex = end > 0 ? s.slice(i + open, end) : '';
      if (end > 0 && tex.trim()) { flush(); out.push({ math: true, v: tex.trim(), display }); i = end + open; continue; }
    }
    buf += s[i]; i++;
  }
  flush();
  return out;
}

// الصيغة نصًا مقروءًا (لملف Word وما لا تُعرض فيه الصيغ): \frac{a}{b} ← (a)/(b)، \sqrt{x} ← √(x)، x^{2} ← x², …
const SUP = { 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹', '+': '⁺', '-': '⁻', n: 'ⁿ', '°': '°' };
const SUB = { 0: '₀', 1: '₁', 2: '₂', 3: '₃', 4: '₄', 5: '₅', 6: '₆', 7: '₇', 8: '₈', 9: '₉', '+': '₊', '-': '₋' };
const SYM = {
  times: '×', div: '÷', cdot: '·', pm: '±', mp: '∓', le: '≤', leq: '≤', ge: '≥', geq: '≥', ne: '≠', neq: '≠', approx: '≈', equiv: '≡',
  to: '→', rightarrow: '→', leftarrow: '←', Rightarrow: '⇒', rightleftharpoons: '⇌', infty: '∞', degree: '°', circ: '°', propto: '∝',
  int: '∫', sum: 'Σ', prod: 'Π', partial: '∂', nabla: '∇', angle: '∠', perp: '⊥', parallel: '∥', in: '∈', cup: '∪', cap: '∩',
  alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', Delta: 'Δ', epsilon: 'ε', theta: 'θ', lambda: 'λ', mu: 'μ', nu: 'ν', pi: 'π',
  rho: 'ρ', sigma: 'σ', Sigma: 'Σ', tau: 'τ', phi: 'φ', omega: 'ω', Omega: 'Ω', ldots: '…', cdots: '⋯',
  sin: 'sin', cos: 'cos', tan: 'tan', log: 'log', ln: 'ln', lim: 'lim', quad: ' ', qquad: '  ',
};
export function texToText(tex) {
  let t = String(tex);
  const arg = '\\{((?:[^{}]|\\{[^{}]*\\})*)\\}';
  for (let k = 0; k < 4; k++) {
    t = t.replace(new RegExp(`\\\\[dt]?frac${arg}${arg}`, 'g'), (_, a, b) => `(${a})/(${b})`)
      .replace(new RegExp(`\\\\sqrt\\[([^\\]]+)\\]${arg}`, 'g'), (_, n, a) => `${n}√(${a})`)
      .replace(new RegExp(`\\\\sqrt${arg}`, 'g'), (_, a) => `√(${a})`)
      .replace(new RegExp(`\\\\(?:text|mathrm|mathbf|operatorname)${arg}`, 'g'), (_, a) => a);
  }
  const conv = (m, map) => ([...m].every(c => map[c]) ? [...m].map(c => map[c]).join('') : null);
  // الأوامر أولًا (حتى يصير ^\circ رمزًا قبل معالجة الأس)
  t = t.replace(/\\left|\\right|\\!/g, '').replace(/\\[,;:]|~/g, ' ')
    .replace(/\\([A-Za-z]+)/g, (m, w) => SYM[w] ?? w)
    .replace(/\^\{([^{}]*)\}|\^(.)/g, (_, a, b) => { const v = a ?? b; return conv(v, SUP) ?? `^(${v})`; })
    .replace(/_\{([^{}]*)\}|_(.)/g, (_, a, b) => { const v = a ?? b; return conv(v, SUB) ?? `_(${v})`; })
    .replace(/\\\{|\\\}/g, m => m[1])
    .replace(/[{}]/g, '')
    .replace(/\s+/g, ' ');
  return t.trim();
}

// النص كاملًا بصيغه المحوّلة إلى نص مقروء
export const plainMath = s => (hasMath(s) || String(s ?? '').includes('\\$') ? tokenize(String(s)).map(x => (x.math ? texToText(x.v) : x.v)).join('') : String(s ?? ''));

let katex = null, loading = null;
function loadKatex() {
  if (!loading) {
    if (!document.querySelector('link[data-katex]')) {
      const l = document.createElement('link');
      Object.assign(l, { rel: 'stylesheet', href: KATEX_CSS, crossOrigin: 'anonymous' });
      l.dataset.katex = '';
      document.head.appendChild(l);
    }
    loading = import(KATEX).then(m => { katex = m.default || m; }).catch(() => { katex = null; });
  }
  return loading;
}

// نقطة الضرب «·» يكتبها المعلمون في الوحدات (J/(kg·°C)): KaTeX يرفضها داخل \text، فتُكتب \cdot خارج النص
export const normTex = tex => tex
  .replace(/\\text\{([^{}]*)\}/g, (m, inner) => (inner.includes('·') ? `\\text{${inner.replace(/·/g, '}\\cdot\\text{')}}` : m))
  .replace(/·/g, '\\cdot ');

function mathNode(tok) {
  const el = document.createElement(tok.display ? 'div' : 'span');
  el.className = tok.display ? 'math math-block' : 'math';
  el.dir = 'ltr';
  el.dataset.tex = tok.v;
  if (katex) {
    try { katex.render(normTex(tok.v), el, { displayMode: tok.display, throwOnError: false, strict: 'ignore', trust: false, output: 'htmlAndMathml' }); return el; } catch { /* يظهر نص الصيغة */ }
  }
  el.textContent = tok.v;
  el.classList.add('math-raw');
  return el;
}

function candidates(root) {
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(n) {
      const p = n.parentElement;
      if (!p || SKIP.has(p.tagName) || p.isContentEditable || p.closest('.math, [data-no-math]')) return NodeFilter.FILTER_REJECT;
      return hasMath(n.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    },
  });
  const nodes = [];
  for (let n = w.nextNode(); n; n = w.nextNode()) nodes.push(n);
  return nodes;
}

export async function renderMath(root) {
  const nodes = candidates(root);
  if (!nodes.length) return;
  await loadKatex();
  for (const n of nodes) {
    if (!n.parentNode || !hasMath(n.data)) continue;
    const frag = document.createDocumentFragment();
    for (const tok of tokenize(n.data)) frag.appendChild(tok.math ? mathNode(tok) : document.createTextNode(tok.v));
    n.parentNode.replaceChild(frag, n);
  }
}

// يُشغَّل مرة واحدة: الصفحة الحالية وكل ما يُضاف إليها لاحقًا
export function startMath(root = document.body) {
  let pending = false;
  const run = () => { pending = false; renderMath(root); };
  new MutationObserver(() => { if (!pending) { pending = true; requestAnimationFrame(run); } })
    .observe(root, { childList: true, subtree: true, characterData: true });
  run();
}
