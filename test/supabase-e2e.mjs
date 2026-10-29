// اختبار وضع Supabase بالمتصفح دون اتصال بالإنترنت: قاعدة PostgreSQL محلية عليها supabase/schema.sql وملفات البيانات،
// ومحاكي بسيط لمكتبة supabase-js ينفّذ كل استدعاء بدور anon أو authenticated كما في Supabase (فتُختبر سياسات RLS والدوال المحمية فعليًا).
// التشغيل: PGURL=postgres://postgres@localhost:54329/sbtest PG_MODULE=<مسار وحدة pg> node test/supabase-e2e.mjs <مجلد الإخراج>
// (ومعها XLSX_MODULE=<مجلد فيه حزمة xlsx>، وKATEX_DIR=<مجلد dist لحزمة katex> إن لم تكن katex بجوار وحدة pg)
// قبل التشغيل: قاعدة فارغة فيها مخطط auth مبسّط (auth.users و auth.uid()) والدوران anon و authenticated، ثم schema.sql ثم supabase/seed/*.sql.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const pg = createRequire(process.env.PG_MODULE + '/')('pg');
const pool = new pg.Pool({ connectionString: process.env.PGURL });
const OUT = process.argv[2] || '.';
// دالة الحافة admin-users تُختبر بمنطقها الحقيقي مع بدائل محلية لعمليات Supabase Auth.
const fnTmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'fn-')), 'admin-users.mjs');
fs.copyFileSync(path.join(root, 'supabase/functions/admin-users/index.ts'), fnTmp);
const adminUsers = await import(fnTmp);
// بدائل محلية: ما يمر بتوكن المستدعي يُنفذ بدوره الحقيقي (asRole) كما في Supabase.
const fnDeps = {
  setEmail: async (id, email) => {
    if ((await pool.query('select 1 from auth.users where email = $1', [email])).rowCount) return { error: 'User already registered' };
    await pool.query('update auth.users set email = $2 where id = $1', [id, email]); return {};
  },
  deleteUser: async id => { await pool.query('delete from auth.users where id = $1', [id]); return {}; },
  callerRole: async jwt => { const r = await asRole(jwt, 'select to_jsonb(public.get_me()) r'); return r.error ? { error: r.error.message } : { role: r.data?.role || null }; },
  initStudent: async (jwt, id, { name, section, grade }) => { const r = await asRole(jwt, 'select to_jsonb(public.admin_init_student($1, $2, $3, $4)) r', [id, name, section || null, grade || null]); return r.error ? { error: r.error.message } : {}; },
  initStaff: async (jwt, id, { name, role }) => { const r = await asRole(jwt, 'select to_jsonb(public.admin_init_staff($1, $2, $3)) r', [id, name, role]); return r.error ? { error: r.error.message } : {}; },
  canManage: async (jwt, id) => (await asRole(jwt, 'select to_jsonb(public.admin_can_manage($1)) r', [id])).data === true,
  createUser: async ({ email }) => {
    if ((await pool.query('select 1 from auth.users where email = $1', [email])).rowCount) return { error: 'User already registered' };
    return { id: (await pool.query('insert into auth.users (email) values ($1) returning id', [email])).rows[0].id };
  },
  setPassword: async () => ({}),
};
const SDK = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/+esm';

// مستخدمان تجريبيان: مراجع ومعلم (بلا كلمات مرور: المحاكي لا يختبر Supabase Auth نفسه بل الأدوار والسياسات).
await pool.query(`insert into auth.users (id, email) values ('11111111-1111-1111-1111-111111111111','rev@x.com'),('22222222-2222-2222-2222-222222222222','view@chem21.local') on conflict do nothing`);
await pool.query(`update public.profiles set role='reviewer', display_name='عبدالله حمدي' where email='rev@x.com'`);
await pool.query(`update public.profiles set role='viewer' where email='view@chem21.local'`);
await pool.query(`delete from public.teacher_courses; delete from public.teacher_students`);
await pool.query(`insert into public.teacher_courses (teacher_id, course_id) select user_id, 1 from public.profiles where email='view@chem21.local'`);
await pool.query(`insert into auth.users (id, email) values ('55555555-5555-5555-5555-555555555555','owner@chem21.local') on conflict do nothing`);
await pool.query(`update public.profiles set role='admin', display_name='مالك المشروع' where email='owner@chem21.local'`);
await pool.query(`delete from auth.users where email in ('st2test@chem21.local', 'deltest@chem21.local', 'deltest2@chem21.local') or email like 'st_____@chem21.local' or email like 'bulk_@chem21.local'`);
await pool.query('delete from public.review_notes');
await pool.query(`insert into auth.users (id, email) values ('33333333-3333-3333-3333-333333333333','new@x.com') on conflict do nothing`);

async function asRole(uid, sql, params) {
  const c = await pool.connect();
  try {
    await c.query('begin');
    await c.query(`set local role ${uid ? 'authenticated' : 'anon'}`);
    await c.query(`select set_config('request.jwt.claim.sub', $1, true)`, [uid || '']);
    const r = await c.query(sql, params);
    await c.query('commit');
    return { data: r.rows[0]?.r ?? null, error: null };
  } catch (e) {
    await c.query('rollback');
    return { data: null, error: { message: e.message, code: e.code } };
  } finally { c.release(); }
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json' };
const FAIL = {}; // حقن أخطاء مؤقتة (ازدحام) لاختبار أن الطالب لا يُخرَج
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname.startsWith('/mock/')) {
    let body = ''; for await (const ch of req) body += ch;
    const b = body ? JSON.parse(body) : {};
    const uid = req.headers.authorization || null;
    let out;
    if (url.pathname === '/mock/login') {
      const r = await pool.query('select id from auth.users where email = $1', [b.email]);
      out = r.rows[0] ? { uid: r.rows[0].id } : { error: { message: 'Invalid login credentials' } };
    } else if (url.pathname.startsWith('/mock/functions/')) {
      out = await adminUsers.handle(b, uid, fnDeps);
    } else if (url.pathname === '/mock/q') {
      out = await asRole(uid, `select jsonb_build_object('objective_id', q.objective_id, 'objectives', jsonb_build_object('code', o.code)) r
        from public.questions q join public.objectives o on o.id = q.objective_id where q.id = $1`, [b.v]);
    } else {
      const fn = url.pathname.slice('/mock/rpc/'.length);
      if (FAIL[fn] > 0) { FAIL[fn]--; out = { error: { message: 'canceling statement due to statement timeout', code: '57014' } }; }
      else if (!/^[a-z_]+$/.test(fn) || fn.startsWith('_')) out = { error: { message: 'not found', code: '42883' } };
      else {
        const meta = await pool.query(`select unnest(proargnames) n, unnest(proargtypes::regtype[]::text[]) t from pg_proc where proname = $1 and pronamespace = 'public'::regnamespace`, [fn]);
        const names = Object.keys(b);
        const args = names.map((n, i) => `${n} => $${i + 1}::${meta.rows.find(r => r.n === n)?.t || 'text'}`);
        // مصفوفات PostgreSQL (uuid[] و text[]) تُمرَّر مصفوفة كما يفعل PostgREST؛ وبقية الكائنات JSON
        const isArr = n => /\[\]$/.test(meta.rows.find(r => r.n === n)?.t || '');
        out = await asRole(uid, `select to_jsonb(public.${fn}(${args.join(', ')})) r`,
          names.map(n => b[n] !== null && typeof b[n] === 'object' && !isArr(n) ? JSON.stringify(b[n]) : b[n]));
      }
    }
    res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify(out)); return;
  }
  // الملفات الثابتة كما على GitHub Pages: لا يوجد api/ فتنتقل الواجهة إلى Supabase.
  const file = path.join(root, decodeURIComponent(url.pathname.replace(/^\/Bank\//, '/')));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    const idx = path.join(file, 'index.html');
    if (fs.existsSync(idx)) { res.writeHead(200, { 'content-type': 'text/html' }); res.end(fs.readFileSync(idx)); return; }
    res.writeHead(404, { 'content-type': 'text/html' }); res.end('<h1>404</h1>'); return;
  }
  res.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream' }); res.end(fs.readFileSync(file));
}).listen(8766);

const FAKE_SDK = `
const M = location.origin + '/mock';
export function createClient() {
  let token = localStorage.getItem('mocktok');
  const post = (p, b) => fetch(M + p, { method: 'POST', headers: { 'content-type': 'application/json', ...(token ? { authorization: token } : {}) }, body: JSON.stringify(b || {}) }).then(r => r.json());
  return {
    rpc: (fn, args) => post('/rpc/' + fn, args),
    auth: {
      signInWithPassword: async ({ email }) => { const r = await post('/login', { email }); if (r.error) return { error: r.error }; token = r.uid; localStorage.setItem('mocktok', token); return { data: {} }; },
      signOut: async () => { token = null; localStorage.removeItem('mocktok'); return {}; },
    },
    from: t => ({ select: () => ({ eq: (c, v) => ({ single: () => post('/q', { t, c, v }) }) }) }),
    functions: { invoke: async (name, { body }) => { const r = await post('/functions/' + name, body);
      return r.status >= 400 ? { data: null, error: { message: 'FunctionsHttpError', context: { json: async () => r.body } } } : { data: r.body, error: null }; } },
  };
}`;

const browser = await chromium.launch();
const results = [], errors = [];
const ok = (n, v, extra = '') => results.push(`${v ? 'PASS' : 'FAIL'} ${n} ${extra}`);
const ctx = await browser.newContext({ viewport: { width: Number(process.env.E2E_WIDTH || 1280), height: 900 }, locale: 'ar', acceptDownloads: true, deviceScaleFactor: Number(process.env.SHOT_SCALE || 1), colorScheme: process.env.E2E_DARK ? 'dark' : 'light' });
await ctx.route('https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js', r => r.fulfill({ contentType: 'text/javascript', body: fs.readFileSync(process.env.XLSX_MODULE + '/xlsx/dist/xlsx.full.min.js', 'utf8') }));
// KaTeX (لأسئلة التحصيلي ذات الصيغ) من نسخة محلية: KATEX_DIR أو حزمة katex بجوار وحدة pg
const KATEX_DIR = process.env.KATEX_DIR || path.join(path.dirname(createRequire(process.env.PG_MODULE + '/').resolve('katex/package.json')), 'dist');
await ctx.route('https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/**', r => r.fulfill({ path: path.join(KATEX_DIR, r.request().url().split('/dist/')[1]), headers: { 'access-control-allow-origin': '*' } }));
await ctx.route(SDK, r => r.fulfill({ contentType: 'text/javascript', body: FAKE_SDK, headers: { 'access-control-allow-origin': '*' } }));
if (!process.env.ALLOW_FONTS) await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
// عزل الاتجاه (public/bidi.js) يضيف علامات غير مرئية داخل النص؛ تُعطَّل هنا لأن الاختبار يقارن النص حرفيًا
await ctx.addInitScript(() => { window.__ITQAN_NO_BIDI = true; });
const p = await ctx.newPage();
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error' && !/fonts|ERR_FAILED|404/.test(m.text())) errors.push('console: ' + m.text()); });
const BASE = `http://${process.env.E2E_HOST || 'localhost'}:8766/Bank/public/`;
const Q2 = sel => p.locator('#mcq-list .q').nth(1).locator(sel);

try {
// الزائر: لا يرى إلا صفحة الدخول، وقاعدة البيانات ترفض طلباته مباشرة
await p.goto(BASE + '#/'); await p.waitForSelector('#l-user');
ok('anon: login page first, header hidden', !(await p.locator('.topbar').isVisible()) && !(await p.locator('.kpi').count()));
ok('login form: username + password + logo', (await p.locator('label[for="l-user"]').innerText()).includes('اسم المستخدم') && await p.locator('.login-logo:visible').first().evaluate(i => i.complete && i.naturalWidth > 0));
ok('footer: copyright', (await p.locator('.footer').innerText()).includes('برمجة وتطوير الأستاذ عبدالله حمدي'));
await p.screenshot({ path: `${OUT}/supa-login.png` });
await p.goto(BASE + '#/bank'); await p.waitForSelector('#l-user');
ok('anon: deep link still shows login only', !(await p.locator('.q').count()));
const direct = await p.evaluate(async () => Promise.all(['get_bank', 'get_stats', 'get_chapters'].map(fn =>
  fetch(location.origin + '/mock/rpc/' + fn, { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{}' }).then(r => r.json()))));
ok('anon: database refuses direct reads', direct.every(r => r.error && !r.data), JSON.stringify(direct.map(r => r.error?.code)));

// حساب جديد لم يفعّله المشرف: رسالة انتظار فقط
await p.fill('#l-user', 'new@x.com'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]');
ok('pending: awaiting activation page', await p.locator('h1', { hasText: 'بانتظار التفعيل' }).waitFor({ timeout: 5000 }).then(() => true, () => false));
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForTimeout(800);
ok('pending: no content', !(await p.locator('.q').count()) && !(await p.locator('.topbar').isVisible()));
await p.click('#p-out'); await p.waitForSelector('#l-user');

// المعلم: يرى المحتوى والإجابات ولا يرى أدوات المراجعة
await p.fill('#l-user', 'view'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]');
// الصفحة الأولى: المقررات الأربعة، كيمياء 2-1 متاح والبقية قيد الإعداد (لا تُفتح لغير المالك)
await p.waitForSelector('.course-card');
ok('viewer: header visible after login', await p.locator('.topbar').isVisible());
const courseCards = await p.$$eval('.course-card', cs => cs.map(c => c.querySelector('h2').textContent + ':' + (c.classList.contains('preparing') ? 'p' : 'r') + ':' + (c.querySelector('[data-course]') ? 'open' : 'locked')));
ok('courses: scoped teacher sees only the assigned ready course (2-1)', JSON.stringify(courseCards) === JSON.stringify(['كيمياء 2-1:r:open']), JSON.stringify(courseCards));
ok('courses: header line shows chosen course', (await p.locator('#brand-sub').innerText()).includes('كيمياء 2-1 · الصف الثاني الثانوي · الفصل الدراسي الأول'));
await p.screenshot({ path: `${OUT}/courses.png`, fullPage: true });
await p.locator('.course-card [data-course="1"]').first().click();
await p.waitForSelector('.kpi .value');
ok('courses: card opens course home', (await p.evaluate(() => location.hash)) === '#/course');
ok('term: textbook, not memo (home)', !/مذكر/.test(await p.locator('main').innerText()));
ok('no «مسارات» on home', !/مسارات/.test(await p.locator('main').innerText()));
ok('home: term 1448', (await p.locator('main').innerText()).includes('الفصل الدراسي الأول 1448هـ'));
ok('viewer: stats show 2580 questions', /2580|2,580/.test(await p.locator('main').innerText()));
await p.screenshot({ path: `${OUT}/supa-home.png` });
await p.goto(BASE + '#/chapter/4'); await p.waitForSelector('.obj-list');
ok('viewer: chapter 4 has 5 lessons', (await p.locator('section.lesson').count()) === 5);
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
ok('term: textbook, not memo (objective page)', !/مذكر/.test(await p.locator('main').innerText()) && (await p.locator('main').innerText()).includes('الكتاب المدرسي'));
ok('viewer: 7 mcq + 3 essay', (await p.locator('#mcq-list .q').count()) === 7 && (await p.locator('#essay-section .q').count()) === 3);
await p.locator('[data-mode="practice"]').click(); await p.waitForTimeout(300);
await Q2('[data-choose]').nth(0).click();
ok('viewer: practice check via RPC', await Q2('.notice').waitFor({ timeout: 4000 }).then(() => true, () => false));
// المعلم (الخيار ب): الأهداف وأسئلتها دون إجابات، ولا وضع مراجعة، ولا صفحة بنك
ok('viewer: neutral wording on the objective page (no AI/draft/auto-review labels)', !/مولد|ذكاء اصطناعي|مراجعة آلية|المراجعة الآلية|بشري/.test(await p.locator('main').innerText()));
ok('viewer: objective page without answers or review mode', (await p.locator('[data-mode="review"], .answer, .q-tools, [data-print]').count()) === 0);
const vObj = await p.evaluate(async () => (await fetch(location.origin + '/mock/rpc/get_objective', { method: 'POST',
  headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: JSON.stringify({ p_code: 'C1-L1-O14' }) })).json());
ok('viewer: database withholds objective answers', vObj.data?.answersIncluded === false && !vObj.data.questions.some(q => 'correctIndex' in q || 'modelAnswer' in q));
ok('viewer: no bank in menu', !(await p.locator('[data-nav="bank"]').isVisible()));
await p.goto(BASE + '#/bank'); await p.waitForTimeout(600);
ok('viewer: bank page unavailable', (await p.locator('main').innerText()).includes('غير متاحة لدورك'));
const vBank = await p.evaluate(async () => (await fetch(location.origin + '/mock/rpc/get_bank', { method: 'POST',
  headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: '{}' })).json());
ok('viewer: database returns the bank without answers', vBank.data?.length === 2580 && !vBank.data.some(q => 'correctIndex' in q || 'modelAnswer' in q));
{ const call = (fn, body) => p.evaluate(async ([fn, body]) => (await fetch(location.origin + '/mock/rpc/' + fn, { method: 'POST',
    headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: JSON.stringify(body) })).json(), [fn, body]);
  const [c4, b4, o4, s4] = [await call('get_chapters', { p_course: 4 }), await call('get_bank', { f: { course: 4 } }), await call('get_objective', { p_code: 'K3-C1-L1-O01' }), await call('get_stats', { p_course: 4 })];
  ok('scoped teacher: database refuses other courses (chapters, bank, objective, stats)', [c4, b4, s4].every(r => r.error && /غير متاح/.test(r.error.message)) && !!o4.error, JSON.stringify([c4.error?.code, b4.error?.code, o4.error?.code, s4.error?.code]));
  const crs = await call('get_courses', {});
  ok('scoped teacher: get_courses lists only the assigned course', crs.data?.length === 1 && crs.data[0].id === 1, JSON.stringify(crs.data?.map(c => c.id))); }
await p.goto(BASE + '#/exam'); await p.waitForSelector('#x-build', { timeout: 20000 });
await p.click('#x-build'); await p.waitForSelector('.paper');
{ const opts = await p.$$eval('#x-setup select, select', ss => ss.flatMap(s => [...s.options].map(o => o.textContent)));
  ok('exam lists: no «مسارات», no third term, three secondary grades', !opts.some(t => /مسارات|الفصل الدراسي الثالث|السنة المشتركة/.test(t))
    && ['الأول الثانوي', 'الثاني الثانوي', 'الثالث الثانوي'].every(g => opts.includes(g))); }
ok('viewer: exam builder builds from Supabase bank', (await p.locator('.set-student .paper').count()) >= 1);
ok('viewer: answer key fetched for the exam questions only', /[أبج]/.test(await p.locator('.set-key .answer-grid.key').first().innerText())
  && !(await p.locator('.set-key .answer-grid.key').first().innerText()).includes('؟'));
await p.click('#logout'); await p.waitForSelector('#l-user');
ok('logout returns to login', !(await p.locator('.topbar').isVisible()));

// المراجع
await p.fill('#l-user', 'nobody@x.com'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]');
ok('wrong login rejected', await p.locator('.toast.error').waitFor({ timeout: 3000 }).then(() => true, () => false));
await p.fill('#l-user', 'rev@x.com'); await p.click('button[type=submit]');
await p.waitForSelector('#logout');
ok('reviewer: name shown', (await p.locator('#userbox').innerText()).includes('عبدالله حمدي'));
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
await p.locator('[data-mode="review"]').click(); await p.waitForSelector('.q-tools');
ok('reviewer: answers visible', (await p.locator('#mcq-list .answer:visible').count()) === 7);
{ const t = await p.locator('main').innerText(); ok('refs: no page numbers or worksheet labels', !/ص\s*\d|ورقة/.test(t) && t.includes('المرجع: الكتاب المدرسي —'), (t.match(/المرجع:[^\n]*/) || [''])[0]); }
ok('reviewer: questions approved by owner decision', (await p.locator('#mcq-list .badge.ok').count()) === 7);
// المراجع العلمي: يعتمد ويعيد ويكتب ملاحظات، ولا يعدّل نص المحتوى
ok('reviewer: no edit/duplicate/exclude/add buttons', (await p.locator('[data-qedit], [data-qdup], [data-qexclude], [data-add], #approved-text, #save-counts').count()) === 0);
const revEdit = await p.evaluate(async () => (await fetch(location.origin + '/mock/rpc/exclude_question', { method: 'POST',
  headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: JSON.stringify({ p_id: 1, p_excluded: true, p_note: 'x' }) })).json());
ok('reviewer: database rejects content edits', !!revEdit.error && /لمالك المشروع/.test(revEdit.error.message || ''), JSON.stringify(revEdit).slice(0, 160));
await p.locator('[data-qnote]').nth(1).click(); await p.waitForSelector('#nd-body');
await p.fill('#nd-body', 'البديل الثاني يحتاج صياغة أدق للوحدة');
await p.click('#nd-save');
ok('reviewer: note on question saved', await p.locator('#notes-card .note', { hasText: 'صياغة أدق للوحدة' }).waitFor({ timeout: 5000 }).then(() => true, () => false));
await p.selectOption('#n-target', 'objective:'); await p.fill('#n-body', 'يقترح المراجع تحديد السلوك في صياغة الهدف');
await p.click('#n-save');
ok('reviewer: note on objective saved', await p.locator('#notes-card .note', { hasText: 'تحديد السلوك' }).waitFor({ timeout: 5000 }).then(() => true, () => false));
await p.locator('[data-qstatus$=":in_review"]').nth(1).click();
ok('reviewer: status -> in_review', await Q2('.badge.warn', { hasText: 'قيد المراجعة' }).waitFor({ timeout: 4000 }).then(() => true, () => false));
await p.locator('[data-qstatus$=":approved"]').nth(1).click(); await p.waitForTimeout(800);
ok('reviewer: re-approve', (await Q2('.badge.ok').count()) >= 1);
await p.click('[data-review="approve"]'); await p.waitForTimeout(800);
ok('objective approved', (await p.locator('.hero .badge.ok', { hasText: 'معتمد' }).count()) === 1);
await p.goto(BASE + '#/reports'); await p.waitForSelector('#revs table', { timeout: 8000 });
ok('dashboard (reviewer): revisions list + open notes', (await p.locator('#revs tbody tr').count()) >= 3 && (await p.locator('.d-big').innerText()).trim() === '2');
ok('dashboard: bank charts rendered', (await p.locator('.d-stack .d-seg').count()) === 3 && (await p.locator('.d-bars').count()) >= 1);
await p.screenshot({ path: `${OUT}/dashboard.png`, fullPage: true });
await p.goto(BASE + '#/notes'); await p.waitForSelector('.notes .note');
ok('reviewer: notes page lists open notes, no resolve button', (await p.locator('.notes .note').count()) === 2 && (await p.locator('[data-nresolve]').count()) === 0);
await p.goto(BASE + '#/bank'); await p.waitForSelector('[data-export]', { timeout: 15000 });
const [dl] = await Promise.all([p.waitForEvent('download'), p.click('[data-export="questions"]')]);
const csv = fs.readFileSync(await dl.path(), 'utf8');
ok('export questions CSV (client-side, BOM, 2581 lines)', csv.charCodeAt(0) === 0xfeff && csv.trim().split('\r\n').length === 2581, `lines=${csv.trim().split('\r\n').length}`);
const [dl2] = await Promise.all([p.waitForEvent('download'), p.click('[data-export="objectives"]')]);
ok('export objectives CSV', fs.readFileSync(await dl2.path(), 'utf8').trim().split('\r\n').length === 259);

// ---------- حساب الطالب ----------
await p.click('#logout'); await p.waitForSelector('#l-user');
await p.fill('#l-user', 'owner'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
ok('admin: students nav visible', await p.locator('[data-nav="students"]').isVisible());
// مالك المشروع: يفتح المقرر «قيد الإعداد» ليتابعه، والتبديل بين المقررات يغيّر البنك والترويسة
await p.goto(BASE + '#/'); await p.waitForSelector('.course-card');
await p.goto(BASE + '#/');  await p.waitForSelector('.course-card');
// قيد الإعداد: كيمياء 1 و2-2 و3 و«الاستعداد للتحصيلي»
ok('owner: preparing courses openable', (await p.locator('.course-card.preparing [data-course]').count()) === 4);
await p.locator('[data-course="3"]').click(); await p.waitForSelector('.notice.warn');
ok('owner: 2-2 home shows preparing notice + header', (await p.locator('main').innerText()).includes('قيد الإعداد') && (await p.locator('#brand-sub').innerText()).includes('كيمياء 2-2 · الصف الثاني الثانوي · الفصل الدراسي الثاني'));
await p.goto(BASE + '#/bank'); await p.waitForSelector('#bank-count');
ok('owner: 2-2 bank is empty', (await p.locator('#bank-count').innerText()).trim().startsWith('0'));
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
ok('objective link switches back to its course', (await p.locator('#brand-sub').innerText()).includes('كيمياء 2-1'));
// التحصيلي اختيار من متعدد فقط: لا قسم مقالي ولا عدد مطلوب له ولا مرشح «مقالي» في البنك، وقاعدة البيانات ترفض السؤال المقالي
await p.goto(BASE + '#/objective/T-S2-U03-T01'); await p.locator('main', { hasText: 'T-S2-U03-T01' }).waitFor(); await p.waitForSelector('#mcq-list .q');
ok('tahsili: topic page has no essay section', !(await p.locator('#essay-section').count()) && !(await p.locator('[data-add="essay"]').count()));
await p.goto(BASE + '#/bank'); await p.waitForSelector('#bank-count');
ok('tahsili: bank has no question-type filter', !(await p.locator('#f-type').count()) && !(await p.locator('#bank-count').innerText()).trim().startsWith('0'));
const essayTahsili = await asRole('55555555-5555-5555-5555-555555555555', `select public.create_question('T-S2-U03-T01', 'essay', '{"stem":"اشرح تركيب الذرة بالتفصيل","model_answer":"…","thinking_level":"فهم","difficulty":"سهل"}'::jsonb) r`);
ok('tahsili: database refuses essay questions', String(essayTahsili.error?.message || '').includes('اختيار من متعدد فقط'), essayTahsili.error?.message);
ok('tahsili: topics require no essays', (await pool.query(`select count(*)::int n from public.objectives where id between 5000000 and 5999999 and required_essay <> 0`)).rows[0].n === 0);
// مالك المشروع: يعدّل المحتوى ويغلق الملاحظات
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
await p.locator('[data-mode="review"]').click(); await p.waitForSelector('.q-tools');
await p.locator('[data-qedit]').nth(1).click(); await p.waitForSelector('#e-stem');
await p.fill('#e-stem', 'ما وحدة قياس طاقة الفوتون في النظام الدولي للوحدات؟');
// اتجاه الكتابة يتبع النص: الصيغة الكيميائية تُكتب من اليسار، والنص العربي من اليمين (لا تنقلب الأقواس)
{ const v0 = await p.inputValue('#e-opt0'); await p.fill('#e-opt0', '(NH₄)₂SO₄');
  ok('editor: formula typed left-to-right, Arabic right-to-left', await p.$eval('#e-opt0', el => el.matches(':dir(ltr)'))
    && await p.$eval('#e-stem', el => el.matches(':dir(rtl)')));
  await p.fill('#e-opt0', v0); }
await p.click('#e-save');
ok('owner: edit saved through RPC', await Q2('.q-stem', { hasText: 'في النظام الدولي للوحدات' }).waitFor({ timeout: 4000 }).then(() => true, () => false));
ok('owner: edit moved approved -> in_review', await Q2('.badge.warn', { hasText: 'قيد المراجعة' }).waitFor({ timeout: 4000 }).then(() => true, () => false));
// أربعة بدائل (لمقرر كيمياء 3): إنشاء سؤال بأربعة بدائل والإجابة «د»، وعرضه والتحقق منه
await pool.query(`delete from public.questions where stem like 'سؤال تجريبي بأربعة بدائل%'`);
await p.click('[data-add="mcq"]'); await p.waitForSelector('#e-n');
ok('editor: new question in a 3-option objective defaults to 3 options, «د» hidden', await p.inputValue('#e-n') === '3' && !(await p.locator('[data-optfield="3"]').isVisible()));
await p.selectOption('#e-n', '4');
await p.fill('#e-stem', 'سؤال تجريبي بأربعة بدائل: أي الآتي غاز نبيل؟');
for (const [i, t] of ['الأكسجين', 'النيتروجين', 'الكلور', 'الأرجون'].entries()) await p.fill('#e-opt' + i, t);
await p.selectOption('#e-correct', '3'); await p.fill('#e-expl', 'الأرجون من الغازات النبيلة في المجموعة 18.');
await p.fill('#e-dist', 'الأكسجين من المجموعة 16\nالنيتروجين من المجموعة 15\nالكلور من الهالوجينات\n');
await p.click('#e-save');
const q4 = p.locator('#mcq-list .q', { hasText: 'سؤال تجريبي بأربعة بدائل' });
ok('owner: 4-option question saved and shown with «د» as the key', await q4.waitFor({ timeout: 5000 }).then(() => true, () => false)
  && (await q4.locator('.opt').count()) === 4 && (await q4.locator('.answer h4').first().innerText()).includes('د) الأرجون'));
const q4id = (await pool.query(`select id from public.questions where stem like 'سؤال تجريبي بأربعة بدائل%'`)).rows[0]?.id;
const chk4 = await p.evaluate(async id => (await fetch(location.origin + '/mock/rpc/check_answer', { method: 'POST',
  headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: JSON.stringify({ p_question: id, p_choice: 3 }) })).json(), q4id);
const chk3 = await p.evaluate(async id => (await fetch(location.origin + '/mock/rpc/check_answer', { method: 'POST',
  headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: JSON.stringify({ p_question: id, p_choice: 3 }) })).json(),
  (await pool.query(`select q.id from public.questions q join public.objectives o on o.id = q.objective_id where o.code = 'C1-L1-O14' and q.type = 'mcq' and q.number = 1`)).rows[0].id);
ok('database: choice «د» correct on a 4-option question, refused on a 3-option one', chk4.data?.correct === true && !!chk3.error);
await pool.query(`delete from public.questions where stem like 'سؤال تجريبي بأربعة بدائل%'`);
await p.reload(); await p.waitForSelector('#mcq-list .q'); await p.locator('[data-mode="review"]').click(); await p.waitForSelector('.q-tools');
await p.locator('[data-qhist]').nth(1).click(); await p.waitForSelector('dialog[open] table');
const hist = await p.locator('dialog[open] table').innerText();
ok('history shows reviewer status change + owner edit', hist.includes('تعديل') && hist.includes('عبدالله حمدي') && hist.includes('مالك المشروع'));
await p.keyboard.press('Escape');
await p.locator('[data-qstatus$=":approved"]').nth(1).click(); await p.waitForTimeout(800);
await p.goto(BASE + '#/notes'); await p.waitForSelector('[data-nresolve]');
p.once('dialog', d => d.accept('عُدّلت الصياغة'));
await p.locator('[data-nresolve]').first().click();
await p.waitForTimeout(900);
ok('owner: note resolved', (await p.locator('.notes .note').count()) === 1);
await p.locator('[data-nstatus="resolved"]').click(); await p.waitForTimeout(600);
ok('owner: resolved tab shows response', (await p.locator('.note.done .note-resp').innerText()).includes('عُدّلت الصياغة'));
// حسابات الفريق: إنشاء مدير مدرسة ومشرف تربوي
await p.goto(BASE + '#/team'); await p.waitForSelector('#tm-form');
await pool.query(`delete from auth.users where email in ('principal1@chem21.local', 'super1@chem21.local')`);
await p.fill('#tm-name', 'مدير المدرسة التجريبي'); await p.selectOption('#tm-role', 'principal'); await p.fill('#tm-user', 'principal1'); await p.fill('#tm-pass', 'Prin-Pass-1');
await p.click('#tm-create'); await p.waitForSelector('#tm-result .notice.ok');
await p.fill('#tm-name', 'مشرف تربوي تجريبي'); await p.selectOption('#tm-role', 'supervisor'); await p.fill('#tm-user', 'super1');
await p.click('#tm-create'); await p.locator('#tm-result .notice.ok', { hasText: 'super1' }).waitFor();
const teamRows = await p.$$eval('tr[data-user]', trs => trs.map(tr => tr.dataset.user + ':' + tr.querySelector('.tm-r').value));
ok('owner: team accounts created with roles', teamRows.includes('principal1:principal') && teamRows.includes('super1:supervisor'), JSON.stringify(teamRows));
await p.screenshot({ path: `${OUT}/team.png`, fullPage: true });
await p.goto(BASE + '#/students'); await p.waitForSelector('#as-file');
ok('owner: team accounts not listed as students', !(await p.locator('.as-table').count()) || !(await p.locator('.as-table').innerText()).includes('مدير المدرسة التجريبي'));
await p.goto(BASE + '#/students'); await p.waitForSelector('#as-file');
ok('owner: new-term card on the students page shows when the term started', await p.locator('#rank-term-info', { hasText: 'بدأ احتساب' }).waitFor({ timeout: 5000 }).then(() => true, () => false) && await p.locator('#rank-new-term').isVisible());
// ملف Excel حقيقي بعناوين عربية
const XL = createRequire(process.env.XLSX_MODULE + '/')('xlsx');
const wb = XL.utils.book_new();
XL.utils.book_append_sheet(wb, XL.utils.aoa_to_sheet([['الاسم', 'الصف', 'الشعبة', 'اسم المستخدم'],
  ['طالب أول تجريبي', 'ثاني ثانوي', '1', ''], ['طالب ثان تجريبي', 'ثاني ثانوي', '2', 'st2test'], ['مكرر', 'ثاني ثانوي', '2', 'st2test'], ['طالب حذف', 'ثالث ثانوي', '1', 'deltest']]), 'S');
const xlFile = path.join(os.tmpdir(), 'students-test.xlsx'); XL.writeFile(wb, xlFile);
await p.setInputFiles('#as-file', xlFile); await p.waitForSelector('#as-create');
ok('admin: excel preview parsed 4 rows with grade/section', (await p.locator('#as-preview tbody tr').count()) === 4 && (await p.locator('#as-preview').innerText()).includes('ثاني ثانوي'));
await p.click('#as-create'); await p.waitForSelector('#as-cards');
const cards = await p.$$eval('#as-cards tbody tr', trs => trs.map(tr => [...tr.cells].map(td => td.textContent.trim()).join('|')));
ok('admin: 3 accounts created, duplicate rejected', cards.filter(t => /\|st\d+\||st2test|deltest/.test(t)).length === 3 && cards.some(t => t.includes('مستخدم من قبل')), JSON.stringify(cards));
const st = cards.find(t => t.includes('st2test')).split('|');
const [dlc] = await Promise.all([p.waitForEvent('download'), p.click('#as-cred-xlsx')]);
const credWb = XL.readFile(await dlc.path()); const credRows = XL.utils.sheet_to_json(credWb.Sheets[credWb.SheetNames[0]], { header: 1 });
ok('admin: credentials Excel downloaded with site link', credRows.length === 4 && credRows[0].includes('كلمة المرور') && credRows[1].includes('https://itqanchem.com'), JSON.stringify(credRows[1]));
await p.click('#as-refresh'); await p.waitForSelector('tr[data-id]');
ok('admin: list shows grade', (await p.locator('.as-table').innerText()).length > 0 && (await p.inputValue('tr[data-user="st2test"] .as-grade')) === 'ثاني ثانوي');
ok('admin: new accounts assigned to current course', (await p.locator('tr[data-user="st2test"]').innerText()).includes('كيمياء 2-1'));
await p.locator('tr[data-user="st2test"] .as-pick').check();
await p.selectOption('#as-enroll-course', '3'); p.once('dialog', d => d.accept());
await p.click('#as-enroll-set'); await p.waitForTimeout(900);
ok('admin: move student to another course', (await p.locator('tr[data-user="st2test"]').innerText()).includes('كيمياء 2-2') && !(await p.locator('tr[data-user="st2test"]').innerText()).includes('كيمياء 2-1'));
await p.locator('tr[data-user="st2test"] .as-pick').check();
await p.selectOption('#as-enroll-course', '1'); p.once('dialog', d => d.accept());
await p.click('#as-enroll-set'); await p.waitForTimeout(900);
ok('admin: move back to 2-1', (await p.locator('tr[data-user="st2test"]').innerText()).includes('كيمياء 2-1'));
await p.screenshot({ path: `${OUT}/admin-students.png`, fullPage: true });
await p.selectOption('#af-grade', 'ثالث ثانوي'); await p.waitForTimeout(600);
ok('admin: filter by grade', (await p.locator('tr[data-id]').count()) === 1);
// تعديل اسم المستخدم وكلمة المرور ثم الحذف
await p.fill('tr[data-user="deltest"] .as-user', 'deltest2'); await p.click('tr[data-user="deltest"] .as-save'); await p.waitForTimeout(800);
ok('admin: username renamed', (await pool.query("select 1 from auth.users where email='deltest2@chem21.local'")).rowCount === 1);
const answers = ['Strong-Pass-99', null];
p.on('dialog', async d => { if (d.type() === 'prompt') { const a = answers.shift(); a === null ? await d.dismiss() : await d.accept(a); } else await d.accept(); });
await p.click('tr[data-user="deltest2"] .as-reset'); await p.waitForTimeout(800);
ok('admin: custom password accepted', answers.length === 0);
await p.click('tr[data-user="deltest2"] .as-del'); await p.waitForTimeout(1000);
ok('admin: account deleted', (await pool.query("select 1 from auth.users where email='deltest2@chem21.local'")).rowCount === 0 && !(await p.locator('tr[data-user="deltest2"]').count()));
await p.selectOption('#af-grade', ''); await p.waitForTimeout(500);
const [dle] = await Promise.all([p.waitForEvent('download'), p.click('#as-export')]);
ok('admin: export list to Excel', XL.utils.sheet_to_json(XL.readFile(await dle.path()).Sheets['الطلاب'], { header: 1 })[0].includes('الصف'));
p.removeAllListeners('dialog');
// حذف دفعة كاملة
await p.fill('#as-lines', 'دفعة أولى، دفعة اختبار، 9، bulk1\nدفعة ثانية، دفعة اختبار، 9، bulk2\nدفعة ثالثة، دفعة اختبار، 9، bulk3');
await p.click('#as-read-lines'); await p.click('#as-create'); await p.waitForSelector('#as-cards');
await p.click('#as-refresh'); await p.waitForSelector('#af-grade');
await p.selectOption('#af-grade', 'دفعة اختبار');
ok('bulk: filtered batch of 3', await p.waitForFunction(() => document.querySelectorAll('tr[data-id]').length === 3, null, { timeout: 8000 }).then(() => true, () => false));
await p.check('#as-all');
ok('bulk: select all shows count', (await p.locator('#as-del-many').innerText()).includes('(3)'));
p.on('dialog', d => d.accept());
await p.click('#as-del-many'); await p.waitForTimeout(1500);
ok('bulk: batch deleted in one go', (await pool.query("select count(*)::int n from auth.users where email like 'bulk_@chem21.local'")).rows[0].n === 0);
p.removeAllListeners('dialog');
await p.selectOption('#af-grade', ''); await p.waitForTimeout(400);
await p.click('#logout'); await p.waitForSelector('#l-user');
// دخول الطالب: تأكيد البيانات مرة واحدة
await p.fill('#l-user', 'st2test'); await p.fill('#l-pass', st[3] || 'x'); await p.click('button[type=submit]');
await p.waitForSelector('#c-form');
ok('student: confirm page prefilled', (await p.inputValue('#c-name')) === 'طالب ثان تجريبي' && (await p.inputValue('#c-sec')) === '2' && (await p.locator('#c-form').innerText()).includes('ثاني ثانوي'));
await p.click('#c-form button[type=submit]'); await p.waitForSelector('#s-start');
ok('student: nav shows only practice + history', await p.locator('[data-nav="history"]').isVisible() && !(await p.locator('[data-nav="bank"]').isVisible()) && !(await p.locator('[data-nav="exam"]').isVisible()));
await p.goto(BASE + '#/bank'); await p.waitForSelector('#s-start');
ok('student: teacher pages redirect to practice', !(await p.locator('#bank-list, .kpi').count()));
const blocked = await p.evaluate(async () => (await fetch(location.origin + '/mock/rpc/get_bank', { method: 'POST', headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: '{}' })).json());
ok('student: database refuses teacher reads', !!blocked.error);
await p.locator('.toast').first().waitFor({ state: 'detached', timeout: 8000 }).catch(() => {});
await p.screenshot({ path: `${OUT}/student-setup.png`, fullPage: true });
await p.locator('details.st-ch').first().locator('summary').click();
await p.locator('[data-lesson]').first().check();
await p.selectOption('#s-count', '5'); await p.check('#s-timed');
await p.click('#s-start'); await p.waitForSelector('.st-opt');
ok('student: session started with timer', (await p.locator('.st-top').innerText()).includes('سؤال 1 من 5') && await p.locator('#st-timer').isVisible());
ok('student: no answer marked before answering', (await p.locator('.st-opt.ok, .st-opt.bad').count()) === 0);
ok('student: report-a-problem button on the question', await p.locator('#st-report').isVisible());
await p.click('#st-report'); await p.waitForSelector('dialog.bal-dlg[open]');
await p.screenshot({ path: `${OUT}/student-report.png` });
await p.check('input[name=rr][value=other]'); await p.click('#rr-send');
ok('student: «other» requires a description', await p.locator('#rr-err').isVisible());
await p.check('input[name=rr][value=answer]'); await p.fill('#rr-body', 'أظن أن البديل ب صحيح أيضًا'); await p.click('#rr-send');
await p.waitForSelector('dialog.bal-dlg', { state: 'detached' });
const rep = await pool.query("select body, author_name, source from public.review_notes where source = 'student'");
ok('student: report saved as a student note without the student name', rep.rowCount === 1 && rep.rows[0].author_name === 'طالب' && rep.rows[0].body.includes('أظن أن البديل ب'));
await p.click('#st-report'); await p.waitForSelector('dialog.bal-dlg[open]'); await p.click('#rr-send'); await p.locator('#rr-err').waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
ok('student: second open report on the same question refused', (await p.locator('#rr-err').innerText()).includes('سبق أن أبلغت'));
await p.click('dialog.bal-dlg button[value="no"]'); await p.waitForSelector('dialog.bal-dlg', { state: 'detached' });
const stId = (await pool.query("select id from auth.users where email = 'st2test@chem21.local'")).rows[0].id;
ok('student: cannot read the notes list', !!(await asRole(stId, "select to_jsonb(public.get_notes(null, 'open')) r")).error);
ok('reviewer: sees the student report (source student, no student name)', (await asRole('11111111-1111-1111-1111-111111111111', "select to_jsonb(public.get_notes(null, 'open')) r")).data.some(n => n.source === 'student' && n.author === 'طالب'));
ok('teacher: cannot read the notes', !!(await asRole('22222222-2222-2222-2222-222222222222', "select to_jsonb(public.get_notes(null, 'open')) r")).error);
for (let i = 0; i < 5; i++) {
  await p.locator('.st-opt').first().click(); await p.waitForSelector('.st-fb');
  if (i === 0) { ok('student: immediate feedback with explanation', (await p.locator('.st-fb').innerText()).includes('التفسير')); await p.locator('.toast').first().waitFor({ state: 'detached', timeout: 8000 }).catch(() => {});
await p.screenshot({ path: `${OUT}/student-feedback.png` }); }
  await p.click('#st-next');
}
await p.waitForSelector('.st-result');
const res = await p.locator('.st-score').innerText();
ok('student: result shown', /من 5/.test(res), res);
await p.locator('.toast').first().waitFor({ state: 'detached', timeout: 8000 }).catch(() => {});
await p.screenshot({ path: `${OUT}/student-result.png`, fullPage: true });
if (await p.locator('#st-retry').count()) {
  await p.click('#st-retry'); await p.waitForSelector('.st-opt');
  ok('student: retry mistakes session', (await p.locator('.st-top').innerText()).includes('إعادة الأخطاء'));
  p.once('dialog', d => d.accept()); await p.click('#st-end'); await p.waitForTimeout(500);
}
await p.goto(BASE + '#/history'); await p.waitForSelector('.hero');
await p.waitForTimeout(500);
await p.screenshot({ path: `${OUT}/student-history.png`, fullPage: true });
ok('student: history lists sessions', (await p.locator('main').innerText()).includes('آخر الجلسات') && (await p.locator('main tbody tr').count()) >= 1);
ok('student: «التميّز» in the menu', await p.locator('[data-nav="rank"]').isVisible());
await p.goto(BASE + '#/rank'); await p.waitForSelector('.rank-rules');
ok('student: rank page explains the points and the entry conditions', (await p.locator('main').innerText()).includes('كيف تُحسب نقاطي؟') && (await p.locator('main').innerText()).includes('لم تدخل الترتيب بعد'));
ok('student: rank page shows progress toward the 30 answers / 3 days', (await p.locator('.bar').count()) === 2);
await p.screenshot({ path: `${OUT}/student-rank.png`, fullPage: true });
const rk = await p.evaluate(async () => (await fetch(location.origin + '/mock/rpc/student_leaderboard', { method: 'POST', headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: '{}' })).json());
ok('student: leaderboard RPC exposes no other student details', rk.data && !JSON.stringify(rk.data).includes('username') && rk.data.top.every(t => Object.keys(t).sort().join() === 'me,name,rank,score'), JSON.stringify(Object.keys(rk.data || {})));
// الرصيد: غير مؤهل أولًا، ثم نمنحه تدريبًا جادًا (بيانات تجريبية تُحذف بعد اختبار المعلم) ويستبدل نقاطه بدرجة
ok('student: «الرصيد» in the menu', await p.locator('[data-nav="balance"]').isVisible());
await p.goto(BASE + '#/balance'); await p.waitForSelector('.bal-main');
await p.screenshot({ path: `${OUT}/student-balance-empty.png`, fullPage: true });
ok('student: balance page shows no redeem button before enough points, and the weekly keep-up bonus', (await p.locator('main').innerText()).includes('حافظ على تميّزك') && !(await p.locator('[data-redeem]').count()));
const sid = (await pool.query("select id from auth.users where email = 'st2test@chem21.local'")).rows[0].id;
await pool.query(`update public.rank_terms set started_at = now() - interval '30 days'`);
await pool.query(`do $$ declare sid2 bigint; qq record; n int; k int; t timestamptz; begin
  for n in 1..5 loop
    t := date_trunc('day', now()) - ((n - 1) || ' days')::interval + interval '3 hours';
    insert into public.practice_sessions (user_id, settings, question_ids, total, score, finished_at, created_at) values ('${sid}', '{"e2e":true}', '{}', 12, 0, t, t) returning id into sid2;
    k := 0;
    for qq in select q.id from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id
              where q.type = 'mcq' and c.course_id = 1 order by q.id offset 100 + n * 12 limit 12 loop
      k := k + 1;
      insert into public.practice_answers (session_id, question_id, choice, correct, answered_at) values (sid2, qq.id, 0, k <> 3, t + (k * 10 || ' seconds')::interval);
    end loop;
  end loop; end $$`);
await p.goto(BASE + '#/rank'); await p.waitForSelector('.rank-rules'); await p.waitForTimeout(300); await p.screenshot({ path: `${OUT}/student-rank-eligible.png`, fullPage: true });
await p.goto(BASE + '#/'); await p.waitForSelector('#st-bal:not([hidden])');
await p.waitForTimeout(500); await p.screenshot({ path: `${OUT}/student-home.png`, fullPage: true });
ok('student: home shows the balance strip', (await p.locator('#st-bal').innerText()).includes('درجة جاهزة'));
await p.goto(BASE + '#/balance'); await p.waitForSelector('[data-redeem]');
ok('student: balance shows a ready grade, streak and the mission done', (await p.locator('main').innerText()).includes('درجة جاهزة للاستبدال') && (await p.locator('.bal-mission.ok').count()) === 1);
ok('student: weekly keep-up status shows the real accuracy', (await p.locator('.bal-week').innerText()).includes('صحتك هذا الأسبوع'));
ok('student: badges use icons, not emoji', (await p.locator('.bal-badges li svg').count()) === 3 && !(await p.locator('.bal-badges').innerText()).includes('🏅'));
await p.screenshot({ path: `${OUT}/student-balance.png`, fullPage: true });
await p.locator('[data-redeem="1"]').click(); await p.waitForSelector('dialog.bal-dlg[open]');
ok('student: confirmation says how many points remain', (await p.locator('dialog.bal-dlg').innerText()).includes('ويبقى لك'));
await p.locator('dialog.bal-dlg button[value="ok"]').click(); await p.waitForSelector('.bal-cele');
ok('student: celebration after the exchange', (await p.locator('.bal-cele').innerText()).includes('مبروك'));
await p.screenshot({ path: `${OUT}/student-balance-cele.png` });
await p.locator('.bal-cele button').click();
await p.waitForSelector('.bal-gbox b');
await p.screenshot({ path: `${OUT}/student-balance-after.png`, fullPage: true });
ok('student: grade pending the teacher, points deducted, ranking score untouched', (await p.locator('.bal-gbox b').first().innerText()).trim() === '1' && (await p.locator('main tbody tr').count()) === 1
  && (await p.locator('main').innerText()).includes('بانتظار رصد المعلم'));
const dbBal = await pool.query(`select (select count(*) from public.grade_redemptions where user_id = '${sid}' and status = 'pending')::int pend, (select count(*) from public.practice_answers a join public.practice_sessions s on s.id = a.session_id where s.user_id = '${sid}' and s.settings @> '{"e2e":true}')::int ans`);
ok('database: one pending redemption, practice answers untouched', dbBal.rows[0].pend === 1 && dbBal.rows[0].ans === 60);
const ownCoupon = (await asRole('55555555-5555-5555-5555-555555555555', "select to_jsonb(public.staff_create_coupon(40, 'جائزة اختبار', 7)) r")).data;
ok('owner: coupon issued with an XXXX-XXXX code', /^[A-Z2-9]{4}-[A-Z2-9]{4}$/.test(ownCoupon?.code || ''), JSON.stringify(ownCoupon));
const scoreBefore = (await asRole(sid, 'select to_jsonb(public.student_leaderboard()) r')).data.me.score;
await p.goto(BASE + '#/balance'); await p.waitForSelector('#cp-code');
await p.fill('#cp-code', 'AAAA-AAAA'); await p.click('#cp-go'); await p.locator('#cp-err').waitFor({ state: 'visible', timeout: 5000 });
ok('student: wrong coupon code refused with a generic message', (await p.locator('#cp-err').innerText()).includes('غير صحيح'));
await p.fill('#cp-code', ownCoupon.code.toLowerCase()); await p.click('#cp-go'); await p.waitForSelector('.bal-cele');
ok('student: coupon redeemed with a celebration', (await p.locator('.bal-cele').innerText()).includes('40 نقطة'));
await p.locator('.bal-cele button').click();
const cpDb = await pool.query("select status from public.point_coupons where code = $1", [ownCoupon.code]);
FAIL.get_me = 2; await p.reload();
ok('busy server at start: waits and retries, student stays signed in (no login page)', await p.waitForSelector('#logout', { timeout: 20000 }).then(() => true, () => false) && !(await p.locator('#l-user').count()));
FAIL.get_me = 50; await p.reload();
ok('persistent overload at start: «busy» screen with retry, not the login page', await p.waitForSelector('#busy-retry', { timeout: 30000 }).then(() => true, () => false) && !(await p.locator('#l-user').count()));
FAIL.get_me = 0; await p.reload(); await p.waitForSelector('#logout', { timeout: 20000 });
await p.goto(BASE + '#/balance'); await p.waitForSelector('#cp-code');
ok('database: coupon marked redeemed', cpDb.rows[0].status === 'redeemed');
ok('coupon points do not enter the excellence score', (await asRole(sid, 'select to_jsonb(public.student_leaderboard()) r')).data.me.score === scoreBefore);
ok('coupon is single-use', (await asRole(sid, 'select to_jsonb(public.student_redeem_coupon($1)) r', [ownCoupon.code])).data.ok === false);
// رسائل ومهام المعلم: المالك يرسل للطالب، والطالب يقرأ ويرد، والمهمة تُحتسب من تدريبه
const OWNER = '55555555-5555-5555-5555-555555555555';
const taskLesson = (await pool.query("select o.lesson_id from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id where c.course_id = 1 and q.type = 'mcq' group by 1 order by count(*) desc limit 1")).rows[0].lesson_id;
const due = new Date(Date.now() + 3 * 86400000).toISOString();
const m1 = await asRole(OWNER, 'select to_jsonb(public.staff_send_comm($1::jsonb)) r', [JSON.stringify({ kind: 'message', title: 'راجع الدرس <b>الآن</b>', body: 'حل التدريبات قبل الحصة', target: { mode: 'students', students: [sid] } })]);
const m2 = await asRole(OWNER, 'select to_jsonb(public.staff_send_comm($1::jsonb)) r', [JSON.stringify({ kind: 'task', title: 'مهمة الدرس', lesson: taskLesson, n: 10, minAccuracy: 50, reward: 25, due, target: { mode: 'students', students: [sid] } })]);
ok('owner: message and task sent to one student', m1.data?.n === 1 && m2.data?.n === 1, JSON.stringify([m1.error, m2.error]));
await p.goto(BASE + '#/'); await p.waitForSelector('#st-task:not([hidden])');
ok('student: home shows the current task card', (await p.locator('#st-task').innerText()).includes('مهمة الدرس'));
await p.locator('[data-nav="inbox"]').click(); await p.waitForSelector('.in-item');
ok('student: inbox lists the message and the task, title escaped (no HTML injected)', (await p.locator('.in-item').count()) === 2 && (await p.locator('.in-item b >> text=<b>الآن</b>').count()) === 1);
ok('student: task shows lesson, required count and progress bar', (await p.locator('.is-task').innerText()).includes('10 سؤالًا') && (await p.locator('.is-task').innerText()).includes('مكافأة 25 نقطة') && (await p.locator('.is-task .bar').count()) === 1);
await p.click('[data-reply^="2:"]'); await p.waitForSelector('.in-reply .badge.warn');
ok('student: «needs help» reply recorded', (await pool.query("select 1 from public.comm_recipients where reply_code = 2 and student_id = $1", [sid])).rowCount === 1);
ok('student: free-text reply is impossible (only codes 1 and 2)', !!(await asRole(sid, 'select public.student_comm_reply($1, 9)', [m1.data.id])).error);
await pool.query(`do $$ declare sid2 bigint; qq record; k int := 0; t timestamptz := now() + interval '2 minutes'; begin
  insert into public.practice_sessions (user_id, settings, question_ids, total, score, finished_at, created_at) values ('${sid}', '{"e2e":true}', '{}', 6, 0, t, t) returning id into sid2;
  for qq in select q.id from public.questions q join public.objectives o on o.id = q.objective_id where o.lesson_id = ${taskLesson} and q.type = 'mcq' order by q.id limit 12 loop
    k := k + 1; insert into public.practice_answers (session_id, question_id, choice, correct, answered_at) values (sid2, qq.id, 0, k <> 2, t + (k * 10 || ' seconds')::interval);
  end loop; end $$`);
await p.reload(); await p.waitForSelector('.in-item');
const balAfter = (await asRole(sid, 'select to_jsonb(public.student_balance()) r')).data;
ok('student: task reward (25) credited to the spendable balance bonus', balAfter.bonus >= 25, JSON.stringify(balAfter.bonus));
ok('student: reward shown in the inbox as received', (await p.locator('.is-task .in-reward.got').innerText()).includes('25'));
ok('student: the task is completed automatically from practice (done, frozen)', (await p.locator('.is-task').innerText()).includes('أنجزتها') && (await pool.query("select 1 from public.comm_recipients cr join public.comms c on c.id = cr.comm_id where c.kind = 'task' and cr.status = 'done'")).rowCount === 1);
ok('non-student accounts cannot open a student inbox', (await asRole('33333333-3333-3333-3333-333333333333', 'select to_jsonb(public.student_inbox()) r')).error !== null);
await p.screenshot({ path: `${OUT}/student-inbox.png`, fullPage: true });
ok('student cannot send comms', !!(await asRole(sid, "select to_jsonb(public.staff_send_comm('{}'::jsonb)) r")).error);
await pool.query(`delete from public.practice_sessions where settings @> '{"e2e":true}'`);
await p.click('#logout'); await p.waitForSelector('#l-user');
// مالك المشروع يسند للمعلم طالبًا واحدًا من «حسابات الفريق»
await p.fill('#l-user', 'owner'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
await p.goto(BASE + '#/notes'); await p.waitForSelector('.notes .note');
ok('owner: student report shown in notes with its badge and resolve/delete tools', (await p.locator('.notes .note', { hasText: 'بلاغ طالب' }).count()) === 1 && await p.locator('.notes .note [data-nresolve]').first().isVisible() && await p.locator('.notes .note [data-ndel]').first().isVisible());
// منشئ الاختبارات: فصل كامل أو دروس منه
await p.goto(BASE + '#/exam'); await p.waitForSelector('#x-build .ex-ch, .ex-ch');
const totalMcq = Number(await p.locator('#av-mcq').innerText());
ok('exam builder: chapters list their lessons, all selected by default', (await p.locator('.ex-ch').count()) >= 2 && (await p.locator('[data-ls]').count()) > (await p.locator('.ex-ch').count()) && (await p.locator('[data-ls]:not(:checked)').count()) === 0);
await p.click('#ex-none');
ok('exam builder: «clear all» empties the pool', (await p.locator('#av-mcq').innerText()) === '0');
await p.click('#x-build');
ok('exam builder: building with nothing selected is refused', await p.locator('.toast', { hasText: 'اختر فصلًا أو درسًا' }).waitFor({ timeout: 5000 }).then(() => true, () => false));
await p.locator('.ex-ch').first().locator('.ex-ch-count').click(); // العدّاد/السهم يفتح الفصل، واسم الفصل يحدّده
await p.locator('.ex-ch').first().locator('[data-ls]').first().check();
const oneLesson = Number(await p.locator('#av-mcq').innerText());
ok('exam builder: one lesson narrows the available questions', oneLesson > 0 && oneLesson < totalMcq);
ok('exam builder: partial chapter shows an indeterminate state and its count', (await p.locator('.ex-ch').first().locator('[data-ch]').evaluate(e => e.indeterminate || e.checked)) && (await p.locator('.ex-ch-count').first().innerText()).startsWith('1 من'));
await p.screenshot({ path: `${OUT}/exam-lessons.png`, fullPage: false });
await p.fill('#x-mcq', '5'); await p.fill('#x-essay', '0'); await p.click('#x-build'); await p.waitForSelector('.paper');
const paperIds = await p.$$eval('.paper .pq[data-swap^="mcq:"]', els => [...new Set(els.map(e => Number(e.dataset.swap.split(':')[1])))]);
const lessonsUsed = (await pool.query('select distinct l.id from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id where q.id = any($1)', [paperIds])).rowCount;
ok('exam builder: the paper has questions only from the chosen lesson, count capped by availability', paperIds.length === Math.min(5, oneLesson) && lessonsUsed === 1, `${paperIds.length} ${lessonsUsed}`);
await p.goto(BASE + '#/exam'); await p.waitForSelector('.ex-ch'); await p.click('#ex-all');
ok('exam builder: «select all» restores the full pool', Number(await p.locator('#av-mcq').innerText()) === totalMcq);
const repId = (await pool.query("select id from public.review_notes where source = 'student'")).rows[0].id;
const delRes = await asRole('11111111-1111-1111-1111-111111111111', 'select public.delete_note($1) r', [repId]);
ok('reviewer: can delete a wrong student report', !delRes.error && (await pool.query("select 1 from public.review_notes where source = 'student'")).rowCount === 0, JSON.stringify(delRes));
await p.goto(BASE + '#/team'); await p.waitForSelector('tr[data-user="view"] .tm-assign-btn');
ok('team: teacher row shows assignment summary', (await p.locator('tr[data-user="view"] .tm-sum').innerText()).includes('1 مقرر · 0 طالب'));
await p.locator('tr[data-user="view"] .tm-assign-btn').click(); await p.waitForSelector('.tm-assign .tm-pick .tm-chk');
ok('team: assign panel lists courses (2-1 checked) and students unchecked', (await p.locator('.tm-assign .tm-c:checked').count()) === 1 && (await p.locator('.tm-assign .tm-s').count()) >= 2 && (await p.locator('.tm-assign .tm-s:checked').count()) === 0);
await p.fill('.tm-assign .tm-fq', 'ثان تجريبي');
ok('team: student search narrows the list', (await p.locator('.tm-assign .tm-s').count()) === 1);
await p.click('.tm-assign .tm-all');
ok('team: select shown sets the counter', (await p.locator('.tm-assign .tm-count').innerText()).trim() === '1');
await p.screenshot({ path: `${OUT}/team-assign.png`, fullPage: true });
await p.click('.tm-asave'); await p.waitForSelector('.tm-assign', { state: 'detached' });
ok('team: assignment saved and summary updated', (await p.locator('tr[data-user="view"] .tm-sum').innerText()).includes('1 مقرر · 1 طالب'));
await p.click('#logout'); await p.waitForSelector('#l-user');
// المعلم يرى التقدم
await p.fill('#l-user', 'view'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
await p.goto(BASE + '#/progress'); await p.waitForSelector('#tp-sec');
ok('teacher: last activity in hijri order (day month yearهـ)', /\d{1,2} \S+( \S+)? \d{4}هـ/.test(await p.locator('main tbody').first().innerText()));
ok('teacher: training-quality column on the progress page', (await p.locator('main').innerText()).includes('جودة التدريب'));
ok('teacher: progress lists only the assigned student', (await p.locator('main').innerText()).includes('طالب ثان تجريبي') && !(await p.locator('main').innerText()).includes('طالب أول تجريبي'));
ok('teacher: «رسائل ومهام» in the menu, reviewer-style roles excluded', await p.locator('[data-nav="comms"]').isVisible());
await p.goto(BASE + '#/comms'); await p.waitForSelector('#cm-send');
await p.selectOption('#cm-mode', 'students'); await p.waitForTimeout(300);
await p.screenshot({ path: `${OUT}/teacher-comms-students.png` });
ok('teacher: «selected students» lists his students by name', (await p.locator('[data-stu]').count()) >= 1 && (await p.locator('.cm-students').innerText()).includes('طالب ثان تجريبي'));
await p.selectOption('#cm-grade', { index: 1 });
ok('comms: grade filter narrows the section list and the count', (await p.locator('#cm-sec option').count()) >= 2 && (await p.locator('#cm-mode option').first().innerText()).includes('(1)'));
await p.selectOption('#cm-sec', { index: 1 });
ok('comms: grade then section filter keeps the matching student visible', await p.locator('[data-stu]').first().isVisible());
await p.selectOption('#cm-grade', ''); await p.selectOption('#cm-sec', '');
await p.selectOption('#cm-mode', 'all');
const otherCourse = (await asRole('22222222-2222-2222-2222-222222222222', 'select to_jsonb(public.staff_my_students(3)) r')).data;
ok('comms: students list does not depend on the selected course (flagged not enrolled there)', otherCourse.length >= 1 && otherCourse[0].enrolled === false && otherCourse[0].name);
const msgOther = await asRole('22222222-2222-2222-2222-222222222222', "select to_jsonb(public.staff_send_comm($1::jsonb)) r", [JSON.stringify({ kind: 'message', title: 'رسالة عامة', course: 3, target: { mode: 'all' } })]);
ok('comms: a message reaches his students even when another course is selected', msgOther.data?.n >= 1, JSON.stringify(msgOther.error));
await p.click('[data-tpl="0"]'); await p.click('#cm-send');
await p.waitForSelector('.cm-item');
ok('teacher: template message sent to his students and listed with read stats', (await p.locator('.cm-item').first().innerText()).includes('قرأها 0 من 1'));
const tComm = (await pool.query("select id from public.comms where sender_id = (select id from auth.users where email = 'view@chem21.local') order by id desc limit 1")).rows[0].id;
await asRole(sid, 'select public.student_comm_reply($1, 2) r', [tComm]);
await p.reload(); await p.waitForSelector('.cm-item');
ok('teacher: sees that a student needs help', (await p.locator('.cm-item').first().innerText()).includes('يحتاج مساعدة'));
await p.click('[data-detail]'); await p.waitForSelector('.cm-detail table');
ok('teacher: detail lists the recipient and the reply', (await p.locator('.cm-detail table').innerText()).includes('يحتاج مساعدة'));
await p.click('input[name=cm-kind][value=task]'); await p.fill('#cm-title', 'مهمة جديدة'); await p.fill('#cm-n', '3'); await p.click('#cm-send');
ok('teacher: task with fewer than 5 questions refused', await p.locator('.toast', { hasText: 'بين 5 و200' }).waitFor({ timeout: 5000 }).then(() => true, () => false));
await p.fill('#cm-n', '10'); await p.fill('#cm-acc', '60'); await p.fill('#cm-reward', '10'); await p.click('#cm-send'); await p.waitForFunction(() => document.querySelectorAll('.cm-item').length >= 3, null, { timeout: 8000 });
ok('teacher: task sent (auto-checked) with its reward shown', (await p.locator('.cm-item').first().innerText()).includes('مهمة') && (await p.locator('.cm-item').first().innerText()).includes('مكافأة 10 نقطة'));
const otherStu = (await asRole('22222222-2222-2222-2222-222222222222', "select to_jsonb(public.staff_send_comm($1::jsonb)) r", [JSON.stringify({ kind: 'message', title: 'رسالة', target: { mode: 'students', students: ['33333333-3333-3333-3333-333333333333'] } })]));
ok('teacher cannot message a student outside his assignment', !!otherStu.error);
await p.screenshot({ path: `${OUT}/teacher-comms.png`, fullPage: true });
await pool.query('delete from public.comms');
ok('teacher: «رصيد الدرجات» in the menu', await p.locator('[data-nav="grades"]').isVisible());
await p.goto(BASE + '#/grades'); await p.waitForSelector('tr[data-id]');
ok('teacher: grade balance lists the assigned student with 1 pending', (await p.locator('tr[data-id]').first().innerText()).includes('طالب ثان تجريبي') && (await p.locator('.hero .badge.warn').innerText()).includes('1 درجة'));
await p.screenshot({ path: `${OUT}/teacher-grades.png`, fullPage: true });
ok('grades: filters and sorting controls shown, «pending» is the default view', (await p.locator('.tg-seg button.on').innerText()).includes('بانتظار الرصد') && await p.locator('#tg-sortsel').isVisible() && await p.locator('#tg-grade').isVisible() && await p.locator('#tg-sec').isVisible());
await p.fill('#tg-q', 'لا يوجد هذا الاسم'); await p.waitForSelector('.empty');
ok('grades: search with no match shows an empty state', (await p.locator('#tg-box .empty').innerText()).includes('لا نتائج'));
await p.fill('#tg-q', ''); await p.waitForSelector('tr[data-id]');
await p.click('.tg-seg button[data-st="recorded"]');
ok('grades: «recorded only» hides students who still have pending grades', (await p.locator('tr[data-id]').count()) === 0);
await p.click('.tg-seg button[data-st="pending"]'); await p.waitForSelector('tr[data-id]');
await p.selectOption('#tg-sortsel', 'name');
ok('grades: sort changes the header marker', (await p.locator('.tg-sort.on').innerText()).includes('الطالب'));
await p.click('[data-sort="pending"]');
ok('grades: clicking a header sorts by it', (await p.locator('.tg-sort.on').innerText()).includes('بانتظار الرصد'));
ok('grades: bulk bar offers «record picked» (disabled until a pick)', await p.locator('#tg-rec-picked').isDisabled());
await p.check('[data-pick]');
p.once('dialog', d => d.accept());
await p.click('#tg-rec-picked'); await p.waitForFunction(() => !document.querySelector('[data-pick]'), null, { timeout: 8000 });
ok('teacher: recorded — nothing pending', (await pool.query("select count(*)::int n from public.grade_redemptions where status = 'recorded'")).rows[0].n === 1);
await p.goto(BASE + '#/grades'); await p.waitForSelector('#cp-card #cp-make');
await p.fill('#cp-pts', '500'); await p.fill('#cp-note', 'مبالغ فيه'); await p.click('#cp-make');
ok('teacher: coupon above the teacher limit refused', await p.locator('.toast', { hasText: 'الحد الأقصى لكوبون المعلم' }).waitFor({ timeout: 5000 }).then(() => true, () => false));
await p.fill('#cp-pts', '50'); await p.fill('#cp-note', 'مشاركة متميزة'); await p.click('#cp-make'); await p.waitForSelector('#cp-fresh');
const tCode = (await p.locator('#cp-fresh .cp-code').innerText()).trim();
ok('teacher: coupon issued, code shown with a copy button', /^[A-Z2-9]{4}-[A-Z2-9]{4}$/.test(tCode) && await p.locator('#cp-copy').isVisible());
await p.screenshot({ path: `${OUT}/teacher-coupons.png`, fullPage: true });
ok('teacher coupon redeemable by the teacher\'s assigned student', (await asRole(sid, 'select to_jsonb(public.student_redeem_coupon($1)) r', [tCode])).data.ok === true);
await pool.query(`delete from public.grade_redemptions; delete from public.practice_sessions where settings @> '{"e2e":true}'`);
await pool.query('delete from public.point_coupons');
ok('teacher (viewer): no students admin link', !(await p.locator('[data-nav="students"]').isVisible()));
// مدير المدرسة: الأسئلة ولوحة المؤشرات فقط
await p.click('#logout'); await p.waitForSelector('#l-user');
await p.fill('#l-user', 'principal1'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
const navOf = async () => p.$$eval('.nav a', as => as.filter(a => !a.hidden).map(a => a.dataset.nav));
ok('principal: role label', (await p.locator('#userbox').innerText()).includes('مدير المدرسة'));
ok('principal: nav = home, chapters, bank, dashboard', JSON.stringify(await navOf()) === JSON.stringify(['home', 'chapters', 'bank', 'reports']), JSON.stringify(await navOf()));
await p.goto(BASE + '#/reports'); await p.waitForSelector('.d-cols');
ok('principal: dashboard with weekly + section charts, no revisions/notes', (await p.locator('.d-col').count()) === 8 && (await p.locator('.d-bars').count()) >= 4 && !(await p.locator('#revs').count()));
await p.screenshot({ path: `${OUT}/dashboard-principal.png`, fullPage: true });
ok('principal: dashboard shows no student names', !(await p.locator('main').innerText()).includes('طالب ثان تجريبي'));
await p.goto(BASE + '#/progress'); await p.waitForTimeout(600);
ok('principal: progress page blocked', (await p.locator('main').innerText()).includes('غير متاحة لدورك'));
const prinProg = await p.evaluate(async () => (await fetch(location.origin + '/mock/rpc/teacher_progress', { method: 'POST',
  headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: '{}' })).json());
ok('principal: database rejects student names', !!prinProg.error);
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
ok('principal: questions readable, no review tools', (await p.locator('.review-panel, [data-add], #notes-card').count()) === 0);
// المشرف التربوي: اطلاع + منشئ الاختبارات + لوحة المؤشرات، دون تعديل
await p.click('#logout'); await p.waitForSelector('#l-user');
await p.fill('#l-user', 'super1'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
ok('supervisor: nav includes exam builder + dashboard, no progress/notes/accounts', JSON.stringify(await navOf()) === JSON.stringify(['home', 'chapters', 'bank', 'exam', 'reports']), JSON.stringify(await navOf()));
await p.goto(BASE + '#/exam'); await p.waitForSelector('#x-build', { timeout: 20000 });
await p.click('#x-build'); await p.waitForSelector('.set-key .answer-grid.key');
ok('supervisor: exam built with its answer key', /[أبج]/.test(await p.locator('.set-key .answer-grid.key').first().innerText()));
const supExam = await p.evaluate(async () => (await fetch(location.origin + '/mock/rpc/get_exam_answers', { method: 'POST',
  headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: JSON.stringify({ p_ids: Array.from({ length: 101 }, (_, i) => i + 1) }) })).json());
ok('database: one exam key request is capped at 100 questions', !!supExam.error);
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
await p.locator('[data-mode="review"]').click(); await p.waitForTimeout(500);
await p.goto(BASE + '#/bank'); await p.waitForSelector('#bank-count', { timeout: 15000 });
ok('supervisor: bank visible without answers or sheets', (await p.locator('[data-sheet], [data-pick], [data-export], #bank-list .opt.correct').count()) === 0, JSON.stringify(await Promise.all(['[data-sheet]', '[data-pick]', '[data-export]', '#bank-list .opt.correct'].map(s => p.locator(s).count()))));
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
await p.locator('[data-mode="review"]').click(); await p.waitForTimeout(500);
ok('supervisor: answers visible, no edit/review tools', (await p.locator('#mcq-list .answer:visible').count()) === 7 && (await p.locator('.q-tools, .review-panel, [data-add]').count()) === 0);

} catch (e) { results.push('FAIL exception: ' + e.message.split('\n')[0]); await p.screenshot({ path: `${OUT}/supa-fail.png` }); }
console.log(results.join('\n'));
console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no console errors');
await browser.close(); server.close(); await pool.end();
process.exit(results.some(r => r.startsWith('FAIL')) || errors.length ? 1 : 0);
