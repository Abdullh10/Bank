// عرض الأرقام والصيغ الكيميائية والوحدات داخل النص العربي بترتيبها الصحيح.
// المشكلة: في فقرة من اليمين لليسار يعكس المتصفح ترتيب «0.10 M» فتظهر «M 0.10»، ويفكّك الأسس (10⁻⁴)، ويقلب «25 °C».
// الحل: تحيط الدالة كل مقطع لاتيني/رقمي (أرقام، رموز، وحدات، معادلات) بعازل اتجاه يسار-يمين (LRI … PDI)
// في عُقد النص المعروضة فقط؛ لا يُكتب شيء في قاعدة البيانات ولا يتأثر ما يكتبه المستخدم في الحقول.
const LRI = '⁦', PDI = '⁩';
// بداية المقطع: حرف لاتيني أو إغريقي أو رقم؛ داخله رموز الصيغ والأس والرمز السفلي والفراغ؛ نهايته حرف أو رقم أو ° أو % أو شحنة أو قوس.
const IN = 'A-Za-z0-9\\u0370-\\u03FF\\u00B2\\u00B3\\u00B9⁰-⁹₀-₉.,×·÷()\\[\\]/%°+\\-−=→⇌↔←⇒⇐↑↓⇅<>≈≠≡∝≥≤±⁺⁻₊₋₌√^_|½ ';
const END = 'A-Za-z0-9\\u0370-\\u03FF\\u00B2\\u00B3\\u00B9⁰-⁹₀-₉°%⁺⁻)\\]↑↓⇅|½';
const START = 'A-Za-z0-9\\u0370-\\u03FF\\u00B2\\u00B3\\u00B9⁰-⁹₀-₉°';
// قد يبدأ المقطع الطويل أيضًا بقوس أو جذر أو خط (مثل «(105 ÷ 300)» و«√(4 ÷ 28)» و«[↑↓] 2s»)، لكن المقطع المفرد لا يشمل هذه الرموز.
const START_LONG = `${START}\\[(√|↑↓⇅½`;
const RUN = new RegExp(`[${START_LONG}][${IN}]*[${END}]|[${START}%]`, 'g');
const SKIP = new Set(['INPUT', 'TEXTAREA', 'SELECT', 'OPTION', 'SCRIPT', 'STYLE', 'CODE', 'PRE', 'NOSCRIPT']);
const HAS_RTL = /[֐-ࣿ]/;
const LATIN = /[A-Za-z0-9\u0370-\u03FF]/, SYMBOL = /[^A-Za-z0-9\u0370-\u03FF\s]|\s\S/;

// نص واحد: يلفّ المقاطع التي تجاور حروفًا عربية فقط (النص اللاتيني الخالص يبقى كما هو).
export function isolate(text) {
  if (!text || text.includes(LRI)) return text;
  // عقدة لاتينية خالصة داخل صفحة من اليمين لليسار (مثل خيار «1s [↑↓]  2s [↑]»): يعكس المتصفح ترتيب أجزائها؛ تُعزل كلها وحدة واحدة من اليسار.
  if (!HAS_RTL.test(text)) return LATIN.test(text) && SYMBOL.test(text) ? text.replace(/^(\s*)([\s\S]*?)(\s*)$/, (_, a, b, c) => a + LRI + b + PDI + c) : text;
  return text.replace(RUN, m => wrapRun(m));
}

// قوس فتح أو إغلاق بلا نظيره داخل المقطع (مثل «(20» من «(20 درجة)») يبقى خارج العزل ليُقابَل بنظيره في النص العربي ويُعكس شكله صحيحًا.
function wrapRun(m) {
  const n = (str, ch) => str.split(ch).length - 1;
  let pre = '', post = '', core = m;
  for (let go = true; go;) {
    go = false;
    const a = core[0], z = core[core.length - 1];
    if ((a === '(' && n(core, '(') > n(core, ')')) || (a === '[' && n(core, '[') > n(core, ']'))) { pre += a; core = core.slice(1); go = true; }
    else if ((z === ')' && n(core, ')') > n(core, '(')) || (z === ']' && n(core, ']') > n(core, '['))) { post = z + post; core = core.slice(0, -1); go = true; }
    else if (/^\s/.test(core)) { pre += core[0]; core = core.slice(1); go = true; }
    else if (/\s$/.test(core)) { post = core[core.length - 1] + post; core = core.slice(0, -1); go = true; }
  }
  return core && (LATIN.test(core) || /[↑↓⇅]/.test(core)) ? pre + LRI + core + PDI + post : m;
}

function walk(root) {
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(n) {
      const p = n.parentElement;
      if (!p || SKIP.has(p.tagName) || p.isContentEditable || p.closest('[dir="ltr"], .ltr, [contenteditable="true"]')) return NodeFilter.FILTER_REJECT;
      return n.data.includes(LRI) || !(HAS_RTL.test(n.data) || LATIN.test(n.data)) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
    },
  });
  const nodes = [];
  for (let n = w.nextNode(); n; n = w.nextNode()) nodes.push(n);
  for (const n of nodes) { const t = isolate(n.data); if (t !== n.data) n.data = t; }
}

// يُشغَّل مرة واحدة: يعالج الصفحة الحالية وكل ما يُضاف إليها لاحقًا (دفعة واحدة لكل إطار).
export function startBidi(root = document.body) {
  if (window.__ITQAN_NO_BIDI) return; // مفتاح للاختبارات الآلية التي تقارن النص حرفيًا
  let pending = false;
  const run = () => { pending = false; obs.disconnect(); try { walk(root); } finally { obs.observe(root, { childList: true, subtree: true, characterData: true }); } };
  const obs = new MutationObserver(() => { if (!pending) { pending = true; requestAnimationFrame(run); } });
  run();
}
