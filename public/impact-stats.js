// تحليل «قياس الأثر»: اختبار قبلي ← استخدام المنصة ← اختبار بعدي. دوال خالصة (لا DOM) تُختبر في test/impact.test.js.
// المنهجية:
//   1) هل تحسّن الطلاب؟ اختبار t للعينات المرتبطة، وحجم الأثر (d بالانحراف المجمّع للقياسين، مع تصحيح هيدجز وفترة ثقة 95%)،
//      والكسب المعدّل لهاك، ونسبة من تحسّن. هذا وحده لا يفصل أثر المنصة عن التدريس العادي والنضج.
//   2) هل للمنصة دور؟ (أ) الجرعة-الاستجابة: انحدار البعدي على القبلي ومقدار الاستخدام (ANCOVA)، فيُقارن كل طالب بمن كان
//      في مستواه نفسه قبليًا. (ب) داخل الطالب نفسه: كسبه في الأهداف التي تدرّب عليها مقابل التي لم يتدرّب عليها (عند إدخال درجة كل سؤال).
//   3) جودة الاختبار: ثبات ألفا (KR-20 للأسئلة الثنائية)، وصعوبة كل سؤال وتمييزه.
// الاستخدام يُقاس بالإجابات الأولى الجادة (3 ثوانٍ فأكثر) بين تاريخي الاختبارين، لا بالنقاط، فلا يتأثر بالتحايل.

export const MIN_N = 10;          // أقل عدد أزواج لإجراء الاختبارات الإحصائية
export const MIN_GROUP = 5;       // أقل عدد لعرض مجموعة (شعبة أو فئة)
export const PRACTICED = 3;       // الهدف «متدرَّب عليه» إذا أجاب الطالب فيه 3 إجابات جادة فأكثر

const sum = a => a.reduce((s, x) => s + x, 0);
export const mean = a => (a.length ? sum(a) / a.length : NaN);
export function sd(a) {
  if (a.length < 2) return NaN;
  const m = mean(a);
  return Math.sqrt(sum(a.map(x => (x - m) ** 2)) / (a.length - 1));
}
export function pearson(x, y) {
  const n = x.length;
  if (n < 3) return NaN;
  const mx = mean(x), my = mean(y);
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) { const dx = x[i] - mx, dy = y[i] - my; sxy += dx * dy; sxx += dx * dx; syy += dy * dy; }
  return sxx && syy ? sxy / Math.sqrt(sxx * syy) : NaN;
}
const round = (x, d = 2) => (Number.isFinite(x) ? Math.round(x * 10 ** d) / 10 ** d : null);

// ---------- توزيع t: دالة بيتا غير المكتملة المنتظمة (Numerical Recipes) ----------
function lgamma(x) {
  const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
  let y = x, tmp = x + 5.5; tmp -= (x + 0.5) * Math.log(tmp);
  let ser = 1.000000000190015;
  for (const ci of c) ser += ci / ++y;
  return -tmp + Math.log(2.5066282746310005 * ser / x);
}
function betacf(a, b, x) {
  const MAXIT = 300, EPS = 3e-14, FPMIN = 1e-300;
  const qab = a + b, qap = a + 1, qam = a - 1;
  let c = 1, d = 1 - qab * x / qap;
  if (Math.abs(d) < FPMIN) d = FPMIN;
  d = 1 / d; let h = d;
  for (let m = 1; m <= MAXIT; m++) {
    const m2 = 2 * m;
    let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
    d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN;
    c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN;
    d = 1 / d; h *= d * c;
    aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
    d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN;
    c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN;
    d = 1 / d; const del = d * c; h *= del;
    if (Math.abs(del - 1) < EPS) break;
  }
  return h;
}
function ibeta(a, b, x) {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
  return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
}
// قيمة p ثنائية الطرف لإحصاء t بدرجات حرية df
export function tTwoSided(t, df) {
  if (!Number.isFinite(t) || df <= 0) return NaN;
  return ibeta(df / 2, 0.5, df / (df + t * t));
}
// القيمة الحرجة لـ t (95% ثنائي الطرف) بالتنصيف
export function tCrit(df, alpha = 0.05) {
  let lo = 0, hi = 50;
  for (let i = 0; i < 80; i++) { const mid = (lo + hi) / 2; if (tTwoSided(mid, df) > alpha) lo = mid; else hi = mid; }
  return (lo + hi) / 2;
}

// ---------- انحدار خطي متعدد (المربعات الصغرى) ----------
// X: صفوف المتغيرات المستقلة دون الثابت. يعيد المعاملات (الأول الثابت) وأخطاءها المعيارية وقيم t وp ومعامل التحديد.
export function ols(y, X) {
  const n = y.length, k = (X[0]?.length || 0) + 1;
  if (n <= k + 1) return null;
  const A = X.map(r => [1, ...r]);
  const XtX = Array.from({ length: k }, (_, i) => Array.from({ length: k }, (_, j) => sum(A.map(r => r[i] * r[j]))));
  const Xty = Array.from({ length: k }, (_, i) => sum(A.map((r, t) => r[i] * y[t])));
  const inv = invert(XtX);
  if (!inv) return null;
  const b = inv.map(row => sum(row.map((v, j) => v * Xty[j])));
  const fit = A.map(r => sum(r.map((v, j) => v * b[j])));
  const sse = sum(y.map((v, i) => (v - fit[i]) ** 2));
  const my = mean(y), sst = sum(y.map(v => (v - my) ** 2));
  const df = n - k, s2 = sse / df;
  const se = inv.map((row, i) => Math.sqrt(Math.max(row[i] * s2, 0)));
  const t = b.map((v, i) => v / se[i]);
  return { b, se, t, p: t.map(v => tTwoSided(v, df)), df, r2: sst ? 1 - sse / sst : NaN, n };
}
function invert(M) {
  const n = M.length, A = M.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
    if (Math.abs(A[p][c]) < 1e-12) return null;
    [A[c], A[p]] = [A[p], A[c]];
    const d = A[c][c];
    for (let j = 0; j < 2 * n; j++) A[c][j] /= d;
    for (let r = 0; r < n; r++) if (r !== c) { const f = A[r][c]; for (let j = 0; j < 2 * n; j++) A[r][j] -= f * A[c][j]; }
  }
  return A.map(r => r.slice(n));
}

// ---------- التفسير اللفظي ----------
export function effectLabel(d) {
  if (!Number.isFinite(d)) return '—';
  const a = Math.abs(d), dir = d < 0 ? ' (تراجع)' : '';
  return (a < 0.2 ? 'أثر لا يُذكر' : a < 0.4 ? 'أثر تربوي ملموس' : a < 0.6 ? 'أثر جيد' : 'أثر كبير') + dir;
}
export const gainLabel = g => (!Number.isFinite(g) ? '—' : g < 0 ? 'تراجع' : g < 0.3 ? 'منخفض' : g < 0.7 ? 'متوسط' : 'مرتفع');
export const pLabel = p => (!Number.isFinite(p) ? '—' : p < 0.001 ? 'دال إحصائيًا (p < 0.001)' : p < 0.05 ? `دال إحصائيًا (p = ${p.toFixed(3)})` : `غير دال إحصائيًا (p = ${p.toFixed(2)})`);
export const rLabel = r => (!Number.isFinite(r) ? '—' : Math.abs(r) < 0.1 ? 'لا علاقة تُذكر' : Math.abs(r) < 0.3 ? 'علاقة ضعيفة' : Math.abs(r) < 0.5 ? 'علاقة متوسطة' : 'علاقة قوية');
export const alphaLabel = a => (!Number.isFinite(a) ? '—' : a >= 0.8 ? 'ثبات مرتفع' : a >= 0.7 ? 'ثبات مقبول' : a >= 0.6 ? 'ثبات مقبول بحذر' : 'ثبات منخفض');

// مقارنة قبلي/بعدي لعينة مرتبطة (نسب مئوية)
export function pairedCompare(pre, post) {
  const n = pre.length;
  const diff = post.map((v, i) => v - pre[i]);
  const mPre = mean(pre), mPost = mean(post), sPre = sd(pre), sPost = sd(post), mD = mean(diff), sD = sd(diff);
  const r = pearson(pre, post);
  const t = n >= 2 && sD > 0 ? mD / (sD / Math.sqrt(n)) : NaN;
  const p = n >= 2 ? (sD > 0 ? tTwoSided(t, n - 1) : (mD !== 0 ? 0 : 1)) : NaN;
  // d بالانحراف المجمّع للقياسين (لا بانحراف الفروق حتى لا يتضخم)، وتصحيح هيدجز، وتباينه لتصميم قبلي-بعدي (Borenstein وآخرون 2009)
  const sW = Math.sqrt(((sPre ** 2) + (sPost ** 2)) / 2);
  const d = sW > 0 ? mD / sW : NaN;
  const J = n > 2 ? 1 - 3 / (4 * (n - 1) - 1) : 1;
  const g = d * J;
  const rr = Number.isFinite(r) ? r : 0;
  const v = (1 / n + (d * d) / (2 * n)) * 2 * (1 - rr);
  const se = Math.sqrt(Math.max(v, 0)) * J, z = 1.96;
  return {
    n, mPre, mPost, sPre, sPost, mDiff: mD, sDiff: sD, r, t, df: n - 1, p, d, g, ciLow: g - z * se, ciHigh: g + z * se,
    improved: diff.filter(x => x > 0).length, same: diff.filter(x => x === 0).length, declined: diff.filter(x => x < 0).length,
    // الكسب المعدّل للمجموعة <g> = (متوسط البعدي − متوسط القبلي) ÷ (100 − متوسط القبلي)
    hake: mPre < 100 ? (mPost - mPre) / (100 - mPre) : NaN,
  };
}

const pct = (v, max) => (v == null || !Number.isFinite(Number(v)) ? null : 100 * Number(v) / max);
const lg = u => Math.log(1 + u);

// ثلث القيم: يعيد حدّي التقسيم (بعد الترتيب)
function tercileCuts(values) {
  const s = [...values].sort((a, b) => a - b), n = s.length;
  return [s[Math.floor(n / 3)], s[Math.floor((2 * n) / 3)]];
}

// ثبات ألفا كرونباخ (يساوي KR-20 للأسئلة الثنائية) ومؤشرات الأسئلة
export function itemAnalysis(matrix, maxes) {
  const rows = matrix.filter(r => r.every(v => v != null));
  const n = rows.length, k = maxes.length;
  if (n < MIN_N || k < 2) return null;
  const totals = rows.map(r => sum(r));
  const varT = sd(totals) ** 2;
  const items = maxes.map((m, j) => {
    const col = rows.map(r => r[j]);
    const rest = rows.map((r, i) => totals[i] - r[j]);
    return { n: j + 1, max: m, difficulty: mean(col) / m, discrimination: pearson(col, rest), variance: sd(col) ** 2 };
  });
  const alpha = varT > 0 ? (k / (k - 1)) * (1 - sum(items.map(i => i.variance)) / varT) : NaN;
  return { n, alpha, items };
}

/**
 * التحليل الكامل لدراسة أثر.
 * @param {{study: object, rows: object[], objectives?: object}} data ناتج impact_get
 */
export function analyzeStudy(data) {
  const { study, rows } = data;
  const items = study.items || [];
  const out = { study, warnings: [] };
  const all = rows.map(r => ({ ...r, prePct: pct(r.pre, study.preMax), postPct: pct(r.post, study.postMax), priorPct: r.prior == null ? null : Number(r.prior) }));
  const paired = all.filter(r => r.prePct != null && r.postPct != null);
  const preOnly = all.filter(r => r.prePct != null && r.postPct == null);
  const postOnly = all.filter(r => r.prePct == null && r.postPct != null);
  out.counts = { students: all.length, pre: all.filter(r => r.prePct != null).length, post: all.filter(r => r.postPct != null).length,
    paired: paired.length, preOnly: preOnly.length, postOnly: postOnly.length };
  out.ready = paired.length >= MIN_N;
  if (!paired.length) return out;

  // 1) القبلي والبعدي
  out.overall = pairedCompare(paired.map(r => r.prePct), paired.map(r => r.postPct));
  // متوسط الكسب المعدّل الفردي (يُستبعد من درجته القبلية 100%)
  const indiv = paired.filter(r => r.prePct < 100).map(r => (r.postPct - r.prePct) / (100 - r.prePct));
  out.overall.hakeIndividual = mean(indiv);
  // الفقد: هل يختلف من غاب عن البعدي عمن أكمل؟
  if (preOnly.length >= 3) {
    const a = preOnly.map(r => r.prePct), b = paired.map(r => r.prePct);
    out.attrition = { n: preOnly.length, missingPre: mean(a), completedPre: mean(b), diff: mean(a) - mean(b) };
    if (preOnly.length / (preOnly.length + paired.length) > 0.15) out.warnings.push('غاب عن البعدي أكثر من 15% ممن أدّوا القبلي؛ قد لا تمثل النتائج الدفعة كاملة.');
  }
  if (!study.sameTest) out.warnings.push('الاختباران صيغتان مختلفتان: يُفترض أنهما متكافئتان في الصعوبة؛ أي فرق في صعوبتهما يدخل في الكسب.');

  // 2) الشعب والفئات حسب المستوى القبلي
  const groupBy = (list, keyFn) => {
    const m = new Map();
    for (const r of list) { const k = keyFn(r); if (k == null) continue; if (!m.has(k)) m.set(k, []); m.get(k).push(r); }
    return [...m].map(([key, rs]) => ({ key, n: rs.length, ...(rs.length >= MIN_GROUP ? pairedCompare(rs.map(r => r.prePct), rs.map(r => r.postPct)) : {}) }));
  };
  out.sections = groupBy(paired, r => r.section || 'دون شعبة').sort((a, b) => String(a.key).localeCompare(String(b.key), 'ar', { numeric: true }));
  const band = v => (v < 50 ? 'low' : v < 75 ? 'mid' : 'high');
  const order = { low: 0, mid: 1, high: 2 };
  out.bands = groupBy(paired, r => band(r.prePct)).sort((a, b) => order[a.key] - order[b.key]);

  // 3) الجرعة-الاستجابة
  const used = paired.map(r => r.usage?.valid || 0);
  out.usage = { total: sum(used), median: [...used].sort((a, b) => a - b)[Math.floor(used.length / 2)], none: used.filter(u => u === 0).length,
    // جدية التدريب: إجابات متسرعة كثيرة تُضعف القياس فتُعرض للمتابعة
    rushedHeavy: paired.filter(r => (r.usage?.attempts || 0) >= 10 && r.usage.rushed / r.usage.attempts > 0.4).length };
  if (paired.length >= MIN_N && new Set(used).size > 2) {
    const [c1, c2] = tercileCuts(used);
    const tier = u => (u <= c1 ? 0 : u <= c2 ? 1 : 2);
    out.tiers = [0, 1, 2].map(t => {
      const rs = paired.filter(r => tier(r.usage?.valid || 0) === t);
      return { tier: t, n: rs.length, minUse: rs.length ? Math.min(...rs.map(r => r.usage.valid)) : null, maxUse: rs.length ? Math.max(...rs.map(r => r.usage.valid)) : null,
        mPre: mean(rs.map(r => r.prePct)), mPost: mean(rs.map(r => r.postPct)), gain: mean(rs.map(r => r.postPct - r.prePct)) };
    });
    // ANCOVA: البعدي = ثابت + ب1×القبلي + ب2×log(1+الاستخدام) [+ ب3×الدرجة السابقة إن أُدخلت للجميع]
    const withPrior = paired.every(r => r.priorPct != null);
    const X = paired.map(r => [r.prePct, lg(r.usage?.valid || 0), ...(withPrior ? [r.priorPct] : [])]);
    const fit = ols(paired.map(r => r.postPct), X);
    if (fit) {
      const lgs = used.map(lg);
      const hi = mean(lgs.filter((_, i) => tier(used[i]) === 2)), lo = mean(lgs.filter((_, i) => tier(used[i]) === 0));
      const adjDiff = fit.b[2] * (hi - lo);
      out.dose = { b: fit.b[2], se: fit.se[2], p: fit.p[2], r2: fit.r2, withPrior, df: fit.df,
        // الفرق المتوقع في البعدي بين الثلث الأعلى استخدامًا والأدنى لطالبين متساويين في القبلي، ثم بوحدة الانحراف المعياري
        adjDiff, adjD: adjDiff / sd(paired.map(r => r.postPct)),
        // الارتباط الجزئي للاستخدام مع البعدي بعد ضبط القبلي
        partialR: Math.sign(fit.t[2]) * Math.sqrt((fit.t[2] ** 2) / ((fit.t[2] ** 2) + fit.df)) };
    }
  }

  // 4) الأهداف وجودة الاختبار (عند إدخال درجة كل سؤال)
  if (items.length) {
    const maxes = items.map(i => Number(i.max));
    const ok = (arr) => Array.isArray(arr) && arr.length === items.length;
    out.quality = {
      pre: itemAnalysis(all.filter(r => ok(r.preItems)).map(r => r.preItems.map(v => (v == null ? null : Number(v)))), maxes),
      post: itemAnalysis(all.filter(r => ok(r.postItems)).map(r => r.postItems.map(v => (v == null ? null : Number(v)))), maxes),
    };
    const codes = [...new Set(items.map(i => i.objective).filter(Boolean))];
    const both = paired.filter(r => ok(r.preItems) && ok(r.postItems));
    if (codes.length && both.length) {
      const objPct = (r, key, code) => {
        let got = 0, max = 0;
        items.forEach((it, j) => { if (it.objective === code) { got += Number(r[key][j] ?? 0); max += Number(it.max); } });
        return max ? (100 * got) / max : null;
      };
      out.objectives = codes.map(code => {
        const pre = both.map(r => objPct(r, 'preItems', code)), post = both.map(r => objPct(r, 'postItems', code));
        const prac = both.map(r => (r.objUsage?.[code] || 0));
        return { code, text: data.objectives?.[code] || '', n: both.length, items: items.filter(i => i.objective === code).length,
          mPre: mean(pre), mPost: mean(post), gain: mean(post) - mean(pre), practice: mean(prac), practicedPct: (100 * prac.filter(x => x >= PRACTICED).length) / both.length };
      }).sort((a, b) => b.gain - a.gain);
      // داخل الطالب: كسبه في الأهداف التي تدرّب عليها مقابل التي لم يتدرّب عليها (كل طالب ضابط لنفسه)
      const within = [];
      for (const r of both) {
        const g = { yes: [], no: [] };
        for (const code of codes) {
          const a = objPct(r, 'preItems', code), b = objPct(r, 'postItems', code);
          if (a == null || b == null) continue;
          ((r.objUsage?.[code] || 0) >= PRACTICED ? g.yes : g.no).push(b - a);
        }
        if (g.yes.length && g.no.length) within.push({ yes: mean(g.yes), no: mean(g.no) });
      }
      if (within.length >= MIN_N) {
        const cmp = pairedCompare(within.map(w => w.no), within.map(w => w.yes));
        out.within = { n: within.length, gainPracticed: cmp.mPost, gainNot: cmp.mPre, diff: cmp.mDiff, t: cmp.t, p: cmp.p, d: cmp.g };
      }
      if (codes.length >= 5) out.objCorrelation = pearson(out.objectives.map(o => o.practice), out.objectives.map(o => o.gain));
    }
  }

  // 5) الحكم على مستوى الدليل
  const o = out.overall;
  const improved = out.ready && o.p < 0.05 && o.mDiff > 0;
  const doseOk = out.dose && out.dose.p < 0.05 && out.dose.b > 0;
  const withinOk = out.within && out.within.p < 0.05 && out.within.diff > 0;
  out.evidence = !out.ready ? { level: 'insufficient', label: 'بيانات غير كافية', text: `يلزم ${MIN_N} طلاب على الأقل لهم اختبار قبلي وبعدي.` }
    : !improved ? { level: 'none', label: 'لم يظهر تحسن دال', text: 'لم يتحسن متوسط الطلاب تحسنًا دالًا إحصائيًا بين الاختبارين.' }
    : doseOk && withinOk ? { level: 'strong', label: 'دليل قوي', text: 'تحسّن الطلاب، وكان التحسن أكبر عند الأكثر استخدامًا بعد ضبط مستواهم القبلي، وفي الأهداف التي تدرّبوا عليها مقارنة بغيرها لدى الطالب نفسه.' }
    : doseOk || withinOk ? { level: 'moderate', label: 'دليل متوسط', text: doseOk ? 'تحسّن الطلاب، وكان التحسن أكبر عند الأكثر استخدامًا للمنصة بعد ضبط مستواهم القبلي.' : 'تحسّن الطلاب، وكان تحسنهم أكبر في الأهداف التي تدرّبوا عليها في المنصة مقارنة بغيرها.' }
    : { level: 'initial', label: 'دليل أولي', text: 'تحسّن الطلاب تحسنًا دالًا، لكن لم تظهر علاقة دالة بين مقدار الاستخدام ومقدار التحسن؛ فقد يعود التحسن إلى التدريس والنضج.' };
  return out;
}

export const fmt = (x, d = 1) => (Number.isFinite(x) ? x.toFixed(d) : '—');
export { round };
