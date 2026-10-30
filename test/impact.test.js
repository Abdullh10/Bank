// قياس الأثر: صحة الحسابات الإحصائية مقابل قيم مرجعية معروفة، وسلوك التحليل على بيانات مصطنعة.
import test from 'node:test';
import assert from 'node:assert/strict';
import { tTwoSided, tCrit, ols, pairedCompare, itemAnalysis, analyzeStudy, effectLabel, gainLabel, mean, sd } from '../public/impact-stats.js';

const near = (a, b, eps = 1e-3) => assert.ok(Math.abs(a - b) < eps, `${a} ≉ ${b}`);

test('توزيع t: قيم p والقيم الحرجة المرجعية', () => {
  near(tTwoSided(2.228, 10), 0.05, 5e-4);
  near(tTwoSided(1.96, 1e6), 0.05, 5e-4);
  near(tTwoSided(2.0, 10), 0.0734, 5e-4);
  near(tTwoSided(0, 5), 1);
  near(tCrit(10), 2.228, 2e-3);
  near(tCrit(30), 2.042, 2e-3);
});

test('الانحدار المتعدد: يسترجع المعاملات الدقيقة ويحسب أخطاءها', () => {
  const X = [[1, 2], [2, 1], [3, 4], [4, 3], [5, 6], [6, 5], [7, 9], [8, 7]];
  const y = X.map(([a, b]) => 3 + 2 * a - 0.5 * b);
  const f = ols(y, X);
  near(f.b[0], 3); near(f.b[1], 2); near(f.b[2], -0.5); near(f.r2, 1);
  // بيانات بضوضاء ومتغير واحد: يطابق صيغة الميل المستقلة (التغاير ÷ التباين)
  const y2 = [5.1, 6.9, 9.2, 10.8, 13.1, 15.2, 16.4, 19.3], x = X.map(r => r[0]);
  const g = ols(y2, x.map(v => [v]));
  const mx = mean(x), my = mean(y2);
  const slope = x.reduce((s, v, i) => s + (v - mx) * (y2[i] - my), 0) / x.reduce((s, v) => s + (v - mx) ** 2, 0);
  near(g.b[1], slope); near(g.b[0], my - slope * mx);
});

test('المقارنة المرتبطة: t والدلالة وحجم الأثر والكسب المعدّل', () => {
  const pre = [40, 50, 60, 45, 55, 35, 65, 50, 42, 58];
  const post = pre.map((v, i) => v + 10 + (i % 3) - 1);
  const c = pairedCompare(pre, post);
  near(c.mDiff, 10 + (mean([0, 1, 2, 0, 1, 2, 0, 1, 2, 0]) - 1));
  assert.ok(c.p < 0.001 && c.t > 10);
  const sW = Math.sqrt((sd(pre) ** 2 + sd(post) ** 2) / 2);
  near(c.d, c.mDiff / sW);
  assert.ok(c.g < c.d && c.ciLow < c.g && c.g < c.ciHigh);
  near(c.hake, (c.mPost - c.mPre) / (100 - c.mPre));
  assert.equal(c.improved, 10);
  assert.equal(effectLabel(0.1), 'أثر لا يُذكر');
  assert.equal(effectLabel(0.5), 'أثر جيد');
  assert.equal(gainLabel(0.45), 'متوسط');
});

test('ثبات ألفا (KR-20) للأسئلة الثنائية', () => {
  // مثال محسوب يدويًا: 10 طلاب × 4 أسئلة
  const m = [[1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [1, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 0], [1, 1, 1, 0]];
  const a = itemAnalysis(m, [1, 1, 1, 1]);
  const totals = m.map(r => r.reduce((s, x) => s + x, 0));
  const vi = [0, 1, 2, 3].map(j => sd(m.map(r => r[j])) ** 2);
  near(a.alpha, (4 / 3) * (1 - vi.reduce((s, x) => s + x, 0) / sd(totals) ** 2));
  near(a.items[0].difficulty, 0.8);
});

// بيانات مصطنعة: التحسن يزيد مع الاستخدام، وفي الأهداف المتدرَّب عليها
function synth({ dose = true, n = 60 } = {}) {
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const items = [{ max: 5, objective: 'A' }, { max: 5, objective: 'A' }, { max: 5, objective: 'B' }, { max: 5, objective: 'B' }];
  const rows = Array.from({ length: n }, (_, i) => {
    const use = Math.floor(rnd() * 200), skill = rnd();
    const practA = rnd() < 0.5 ? 6 : 0, practB = practA ? 0 : 6;
    const it = j => Math.min(5, Math.round(5 * skill * 0.6 + rnd()));
    const pre = items.map((_, j) => it(j));
    const post = pre.map((v, j) => {
      const practiced = (j < 2 ? practA : practB) > 0;
      return Math.min(5, v + (dose ? Math.round(use / 100) : 0) + (dose && practiced ? 1 : 0) + (rnd() < 0.3 ? 1 : 0));
    });
    return { key: String(i), section: i % 2 ? '2/1' : '2/2', pre: pre.reduce((s, x) => s + x, 0), post: post.reduce((s, x) => s + x, 0),
      preItems: pre, postItems: post, usage: { valid: use, attempts: use, rushed: 0 }, objUsage: { A: practA, B: practB } };
  });
  return { study: { preMax: 20, postMax: 20, sameTest: true, items }, rows, objectives: { A: 'هدف أ', B: 'هدف ب' } };
}

test('التحليل الكامل: أثر مع جرعة وأهداف متدرَّب عليها = دليل قوي', () => {
  const r = analyzeStudy(synth());
  assert.equal(r.counts.paired, 60);
  assert.ok(r.overall.p < 0.05 && r.overall.mDiff > 0);
  assert.ok(r.dose.b > 0 && r.dose.p < 0.05, JSON.stringify(r.dose));
  assert.ok(r.within.diff > 0 && r.within.p < 0.05, JSON.stringify(r.within));
  assert.equal(r.evidence.level, 'strong');
  assert.equal(r.tiers.length, 3);
  assert.ok(r.quality.pre && Number.isFinite(r.quality.pre.alpha));
  assert.equal(r.objectives.length, 2);
});

test('التحليل: عينة صغيرة = بيانات غير كافية، والغائبون يُحصَون', () => {
  const d = synth({ n: 8 });
  d.rows[0].post = null;
  const r = analyzeStudy(d);
  assert.equal(r.evidence.level, 'insufficient');
  assert.equal(r.counts.preOnly, 1);
});

test('التحليل: تحسن دون علاقة بالاستخدام = دليل أولي', () => {
  const r = analyzeStudy(synth({ dose: false, n: 80 }));
  if (r.overall.p < 0.05 && r.overall.mDiff > 0) assert.ok(['initial', 'moderate'].includes(r.evidence.level));
  assert.ok(!(r.dose.p < 0.05 && r.dose.b > 0.5));
});
