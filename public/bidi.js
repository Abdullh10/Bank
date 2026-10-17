// عرض الأرقام والصيغ الكيميائية والوحدات داخل النص العربي بترتيبها الصحيح.
// المشكلة: في فقرة من اليمين لليسار يعكس المتصفح ترتيب «0.10 M» فتظهر «M 0.10»، ويفكّك الأسس (10⁻⁴)، ويقلب «25 °C».
// الحل: تحيط الدالة كل مقطع لاتيني/رقمي (أرقام، رموز، وحدات، معادلات) بعازل اتجاه يسار-يمين (LRI … PDI)
// في عُقد النص المعروضة فقط؛ لا يُكتب شيء في قاعدة البيانات ولا يتأثر ما يكتبه المستخدم في الحقول.
const LRI = '⁦', PDI = '⁩';
// بداية المقطع: حرف لاتيني أو إغريقي أو رقم؛ داخله رموز الصيغ والأس والرمز السفلي والفراغ؛ نهايته حرف أو رقم أو ° أو % أو شحنة أو قوس.
const IN = 'A-Za-z0-9\\u0370-\\u03FF\\u00B2\\u00B3\\u00B9⁰-⁹₀-₉.,×·()\\[\\]/%°+\\-−=→⇌↔<>≈≥≤±⁺⁻ ';
const END = 'A-Za-z0-9\\u0370-\\u03FF\\u00B2\\u00B3\\u00B9⁰-⁹₀-₉°%⁺⁻)\\]';
const START = 'A-Za-z0-9\\u0370-\\u03FF\\u00B2\\u00B3\\u00B9⁰-⁹₀-₉°';
const RUN = new RegExp(`[${START}][${IN}]*[${END}]|[${START}%]`, 'g');
const SKIP = new Set(['INPUT', 'TEXTAREA', 'SELECT', 'OPTION', 'SCRIPT', 'STYLE', 'CODE', 'PRE', 'NOSCRIPT']);
const HAS_RTL = /[֐-ࣿ]/;

// نص واحد: يلفّ المقاطع التي تجاور حروفًا عربية فقط (النص اللاتيني الخالص يبقى كما هو).
export function isolate(text) {
  if (!text || text.includes(LRI) || !HAS_RTL.test(text)) return text;
  return text.replace(RUN, m => LRI + m + PDI);
}

function walk(root) {
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(n) {
      const p = n.parentElement;
      if (!p || SKIP.has(p.tagName) || p.isContentEditable || p.closest('[dir="ltr"], .ltr, [contenteditable="true"]')) return NodeFilter.FILTER_REJECT;
      return n.data.includes(LRI) || !HAS_RTL.test(n.data) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
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
