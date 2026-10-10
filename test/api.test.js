// اختبارات تقنية للواجهة البرمجية: الصلاحيات، والتحقق، والحفظ والاسترجاع، وسجل التعديلات، والتصدير.
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'chem21-'));
process.env.DB_PATH = path.join(dir, 'test.db');
// الاختبارات تعمل على أسئلة الهدف النموذجي فقط حتى تكون نتائجها ثابتة مهما زاد البنك.
fs.mkdirSync(path.join(dir, 'questions'));
fs.copyFileSync(new URL('../data/questions/C1-L1-O14.json', import.meta.url), path.join(dir, 'questions', 'C1-L1-O14.json'));
process.env.QUESTIONS_DIR = path.join(dir, 'questions');
process.env.APPROVALS_FILE = path.join(dir, 'no-approvals.json');

const { createApp } = await import('../server/index.js');
const { seed } = await import('../server/seed.js');
const { createUser } = await import('../server/auth.js');

let server, base;
const cookies = {};

before(async () => {
  seed({ log: () => {} });
  createUser({ username: 'rev', role: 'reviewer', displayName: 'مراجع', password: 'reviewer-pass-1' });
  createUser({ username: 'view', role: 'viewer', displayName: 'معلم', password: 'viewer-pass-12' });
  server = createApp().listen(0);
  base = `http://127.0.0.1:${server.address().port}/api`;
  for (const [u, p] of [['rev', 'reviewer-pass-1'], ['view', 'viewer-pass-12']]) {
    const r = await fetch(base + '/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: u, password: p }) });
    assert.equal(r.status, 200);
    cookies[u] = r.headers.get('set-cookie').split(';')[0];
  }
});
after(() => { server.close(); fs.rmSync(dir, { recursive: true, force: true }); });

async function call(p, { method = 'GET', body, as } = {}) {
  const r = await fetch(base + p, {
    method, headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(as ? { Cookie: cookies[as] } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const type = r.headers.get('content-type') || '';
  return { status: r.status, body: type.includes('json') ? await r.json() : await r.text() };
}

test('البنية مستوردة كاملة: 7 فصول و28 درسًا و258 هدفًا', async () => {
  const s = await call('/stats');
  assert.equal(s.body.chapters, 7);
  assert.equal(s.body.lessons, 28);
  assert.equal(s.body.objectives.n, 258);
  assert.equal(s.body.objectives.approved, 0);
  const ch4 = await call('/chapters/4');
  assert.deepEqual(ch4.body.lessons.map(l => l.title),
    ['الرابطة التساهمية', 'تسمية الجزيئات', 'التراكيب الجزيئية', 'أشكال الجزيئات', 'الكهروسالبية والقطبية']);
});

test('الأهداف الأصلية محفوظة حرفيًا ولا تُستبدل بالمقترحة', async () => {
  const o = await call('/objectives/C1-L2-O06');
  assert.equal(o.body.objective.originalText, 'أن يذكر الطالب مبدا هايزنبرك للشك');
  assert.equal(o.body.objective.reviewStatus, 'pending');
  assert.equal(o.body.objective.approvedText, null);
});

test('الزائر لا يستلم الإجابات، والمعلم المسجل يستلمها', async () => {
  const anon = await call('/objectives/C1-L1-O14');
  assert.equal(anon.body.questions.length, 10);
  assert.ok(anon.body.questions.every(q => q.correctIndex === undefined && q.modelAnswer === undefined));
  const t = await call('/objectives/C1-L1-O14', { as: 'view' });
  assert.ok(t.body.questions.filter(q => q.type === 'mcq').every(q => Number.isInteger(q.correctIndex)));
});

test('أسئلة النموذج الأولي: 7 اختيار بثلاثة بدائل و3 مقالية، وكلها مسودة مولدة اجتازت التحقق الآلي', async () => {
  const { body } = await call('/objectives/C1-L1-O14', { as: 'view' });
  const mcq = body.questions.filter(q => q.type === 'mcq'), essay = body.questions.filter(q => q.type === 'essay');
  assert.equal(mcq.length, 7);
  assert.equal(essay.length, 3);
  assert.ok(mcq.every(q => q.options.length === 3 && new Set(q.options).size === 3));
  assert.ok(body.questions.every(q => q.status === 'generated' && q.autoCheck.passed));
  assert.ok(essay.every(q => q.rubric.length >= 2 && q.marks.length && q.modelAnswer));
});

test('التدريب الفوري يتحقق من الإجابة دون كشف بقية الأسئلة', async () => {
  const { body } = await call('/objectives/C1-L1-O14');
  const q = body.questions.find(x => x.type === 'mcq');
  const r = await call(`/questions/${q.id}/check`, { method: 'POST', body: { choice: 0 } });
  assert.equal(r.status, 200);
  assert.equal(typeof r.body.correct, 'boolean');
  const bad = await call(`/questions/${q.id}/check`, { method: 'POST', body: { choice: 7 } });
  assert.equal(bad.status, 400);
});

test('الصلاحيات: الزائر 401 والمعلم 403 عند الاعتماد', async () => {
  assert.equal((await call('/objectives/C1-L1-O14/review', { method: 'POST', body: { action: 'approve' } })).status, 401);
  assert.equal((await call('/objectives/C1-L1-O14/review', { method: 'POST', body: { action: 'approve' }, as: 'view' })).status, 403);
  assert.equal((await call('/export/questions.csv', { as: 'view' })).status, 403);
});

test('اعتماد الهدف وإعادته للمراجعة مع سجل التعديلات', async () => {
  const noNote = await call('/objectives/C1-L1-O14/review', { method: 'POST', body: { action: 'return' }, as: 'rev' });
  assert.equal(noNote.status, 400);
  const ok = await call('/objectives/C1-L1-O14/review', { method: 'POST', body: { action: 'approve', approved_text: 'أن يحسب الطالب طاقة الفوتون' }, as: 'rev' });
  assert.equal(ok.status, 200);
  const o = await call('/objectives/C1-L1-O14');
  assert.equal(o.body.objective.reviewStatus, 'approved');
  assert.equal(o.body.objective.approvedText, 'أن يحسب الطالب طاقة الفوتون');
  const s = await call('/stats');
  assert.equal(s.body.objectives.approved, 1);
  const revs = await call('/revisions', { as: 'rev' });
  assert.ok(revs.body.some(r => r.entity === 'objective' && r.action === 'approve'));
});

test('التحقق من بيانات السؤال قبل الحفظ', async () => {
  const r = await call('/objectives/C1-L1-O14/questions', { method: 'POST', as: 'rev',
    body: { type: 'mcq', stem: 'سؤال تجريبي عن الفوتون؟', options: ['أ', 'ب'], correct_index: 5 } });
  assert.equal(r.status, 400);
  assert.ok(r.body.errors.length >= 2);
});

test('تعديل سؤال معتمد يعيده إلى قيد المراجعة ويحفظ الإصدار السابق', async () => {
  const { body } = await call('/objectives/C1-L1-O14', { as: 'rev' });
  const q = body.questions.find(x => x.type === 'mcq' && x.number === 1);
  assert.equal((await call(`/questions/${q.id}/status`, { method: 'POST', body: { status: 'approved' }, as: 'rev' })).status, 200);
  const edit = await call(`/questions/${q.id}`, { method: 'PATCH', as: 'rev', body: {
    stem: q.stem + ' (معدل)', options: q.options, correct_index: q.correctIndex, explanation: q.explanation,
    distractor_notes: q.distractorNotes, thinking_level: q.thinkingLevel, difficulty: q.difficulty } });
  assert.equal(edit.status, 200);
  const after = await call(`/questions/${q.id}`, { as: 'rev' });
  assert.equal(after.body.status, 'in_review');
  assert.ok(after.body.stem.endsWith('(معدل)'));
  const hist = await call(`/questions/${q.id}/revisions`, { as: 'rev' });
  assert.ok(hist.body.some(h => h.action === 'edit' && h.before_json.stem === q.stem));
});

test('الاستبعاد يتطلب سببًا ويُخفي السؤال عن الزائر مع بقائه في السجل', async () => {
  const { body } = await call('/objectives/C1-L1-O14', { as: 'rev' });
  const q = body.questions.find(x => x.type === 'mcq' && x.number === 7);
  assert.equal((await call(`/questions/${q.id}/exclude`, { method: 'POST', body: { excluded: true }, as: 'rev' })).status, 400);
  assert.equal((await call(`/questions/${q.id}/exclude`, { method: 'POST', body: { excluded: true, note: 'اختبار' }, as: 'rev' })).status, 200);
  const anon = await call('/objectives/C1-L1-O14');
  assert.ok(!anon.body.questions.some(x => x.id === q.id));
  await call(`/questions/${q.id}/exclude`, { method: 'POST', body: { excluded: false }, as: 'rev' });
});

test('النسخ والبحث والتصفية واكتشاف المتشابه', async () => {
  const { body } = await call('/objectives/C1-L1-O14', { as: 'rev' });
  const q = body.questions.find(x => x.type === 'mcq' && x.number === 3);
  const dup = await call(`/questions/${q.id}/duplicate`, { method: 'POST', as: 'rev' });
  assert.equal(dup.status, 200);
  assert.equal(dup.body.autoCheck.passed, false, 'النسخة المطابقة يجب أن تُنبه للتشابه');
  const sim = await call('/bank?chapter=1&similar=1', { as: 'rev' });
  assert.ok(sim.body.similar.some(p => p.score === 100));
  const search = await call('/bank?q=' + encodeURIComponent('الميكروويف'));
  assert.ok(search.body.questions.length >= 1);
  const essays = await call('/bank?type=essay');
  assert.equal(essays.body.questions.length, 3);
});

test('التصدير CSV بترميز UTF-8 مع BOM', async () => {
  const raw = await fetch(base + '/export/questions.csv', { headers: { Cookie: cookies.rev } });
  assert.equal(raw.status, 200);
  const bytes = new Uint8Array(await raw.arrayBuffer());
  assert.deepEqual([...bytes.slice(0, 3)], [0xef, 0xbb, 0xbf]);
  const r = { body: new TextDecoder().decode(bytes) };
  assert.ok(r.body.includes('طاقة الفوتون'));
  const o = await call('/export/objectives.csv', { as: 'rev' });
  assert.equal(o.body.trim().split('\r\n').length, 259);
});

test('كلمة مرور خاطئة ترفض، والخروج ينهي الجلسة', async () => {
  const bad = await call('/login', { method: 'POST', body: { username: 'rev', password: 'wrong-password' } });
  assert.equal(bad.status, 401);
  const me = await call('/me', { as: 'view' });
  assert.equal(me.body.user.role, 'viewer');
  await call('/logout', { method: 'POST', as: 'view' });
  assert.equal((await call('/me', { as: 'view' })).body.user, null);
});

test('الخادم لا يقدّم ملفات نسخة العرض الثابتة (التي تتضمن الإجابات)', async () => {
  const r = await fetch(base.replace('/api', '') + '/static/bank.json');
  assert.equal(r.status, 404);
});
