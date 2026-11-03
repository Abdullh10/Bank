// استبانة الطلاب: التنظيف والثبات والمستويات والارتباط مقابل قيم مرجعية.
import test from 'node:test';
import assert from 'node:assert/strict';
import { ITEMS, ATT, clean, cronbach, level, analyzeSurvey, spearman, dimScore, scored } from '../public/survey.js';

const near = (a, b, eps = 1e-3) => assert.ok(Math.abs(a - b) < eps, `${a} ≉ ${b}`);
const resp = (v, d = 200) => { const a = ITEMS.map(() => v); a[ATT] = 2; return { a, d }; };

test('الأداة: 16 عبارة + عبارة انتباه في الموضع العاشر، وعبارتان عكسيتان', () => {
  assert.equal(ITEMS.length, 17);
  assert.equal(ATT, 9);
  assert.equal(ITEMS.filter(i => i.rev).length, 2);
});

test('التنظيف: الانتباه والإجابة الموحّدة والسرعة', () => {
  const ok = resp(4); ok.a[0] = 5;
  const att = resp(4); att.a[0] = 5; att.a[ATT] = 4;
  const straight = resp(3);
  const fast = resp(4, 30); fast.a[1] = 2;
  const c = clean([ok, att, straight, fast]);
  assert.equal(c.kept.length, 1); assert.equal(c.attention, 1); assert.equal(c.straight, 1); assert.equal(c.speed, 1);
});

test('ألفا كرونباخ مقابل قيمة مرجعية', () => {
  // مثال مرجعي: 5 أفراد × 3 عبارات، ألفا = 0.8 (محسوبة يدويًا)
  const m = [[1, 2, 2], [2, 2, 3], [3, 3, 3], [4, 4, 5], [5, 4, 4]];
  const k = 3, v = j => { const x = m.map(r => r[j]), mu = x.reduce((s, y) => s + y, 0) / x.length; return x.reduce((s, y) => s + (y - mu) ** 2, 0) / (x.length - 1); };
  const t = m.map(r => r[0] + r[1] + r[2]), mt = t.reduce((s, y) => s + y, 0) / t.length, vt = t.reduce((s, y) => s + (y - mt) ** 2, 0) / (t.length - 1);
  near(cronbach(m), (k / (k - 1)) * (1 - (v(0) + v(1) + v(2)) / vt));
  near(cronbach(m), 0.9375);
});

test('مستويات المتوسط (فئات 0.80)', () => {
  assert.equal(level(1.8), 'منخفض جدًا'); assert.equal(level(2.6), 'منخفض'); assert.equal(level(3.4), 'متوسط'); assert.equal(level(3.41), 'مرتفع'); assert.equal(level(4.5), 'مرتفع جدًا');
});

test('العبارة العكسية تُعاد ترميزها في درجة البعد', () => {
  const r = resp(5); // يوافق بشدة على كل شيء، ومنها العكسية «لا أظن أن مستواي تغيّر»
  assert.equal(scored(r.a, 7), 1);
  near(dimScore(r.a, 'B'), (5 + 5 + 5 + 1) / 4);
});

test('سبيرمان: تام للعلاقة الرتيبة، وفترة الثقة تحيط بالقيمة', () => {
  const x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], y = x.map(v => v ** 3);
  near(spearman(x, y).rho, 1);
  const s = spearman([1, 2, 3, 4, 5, 6, 7, 8], [2, 1, 4, 3, 6, 5, 8, 7]);
  near(s.rho, 0.9048, 1e-3); assert.ok(s.lo < s.rho && s.rho < s.hi);
});

test('التحليل: أبعاد بمتوسطاتها، والثبات لا يُحسب تحت 30 إجابة', () => {
  const rows = Array.from({ length: 12 }, (_, i) => { const r = resp(3 + (i % 3)); r.a[0] = 1 + (i % 5); return r; });
  const a = analyzeSurvey(rows);
  assert.equal(a.dims.length, 4); assert.equal(a.items.length, 16);
  assert.ok(!Number.isFinite(a.dims[0].alpha));
});

test('عرض النتائج: مخفية أثناء فتح الاستبانة، وتُعرض بعد إغلاقها', async () => {
  const { surveyResultsHtml } = await import('../public/survey.js');
  const esc = s => String(s);
  assert.match(surveyResultsHtml(esc, { open: true, sent: 10, responses: 6, closesAt: '2026-11-10T00:00:00Z' }), /بعد إغلاق الاستبانة/);
  const rows = Array.from({ length: 8 }, (_, k) => ({ a: ITEMS.map((it, i) => (i === ATT ? 2 : 1 + ((i + k) % 5))), d: 200, s: null }));
  const html = surveyResultsHtml(esc, { open: false, sent: 10, responses: 8, rows, open1: ['أ'], open2: [], sectionsSent: { س: 10 } });
  assert.match(html, /الفائدة المدركة/); assert.match(html, /التحليل على/);
});
