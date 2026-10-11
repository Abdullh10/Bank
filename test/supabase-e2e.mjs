// اختبار وضع Supabase بالمتصفح دون اتصال بالإنترنت: قاعدة PostgreSQL محلية عليها supabase/schema.sql وملفات البيانات،
// ومحاكي بسيط لمكتبة supabase-js ينفّذ كل استدعاء بدور anon أو authenticated كما في Supabase (فتُختبر سياسات RLS والدوال المحمية فعليًا).
// التشغيل: PGURL=postgres://postgres@localhost:54329/sbtest PG_MODULE=<مسار وحدة pg> node test/supabase-e2e.mjs <مجلد الإخراج>
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
  isStudent: async (jwt, id) => (await asRole(jwt, 'select to_jsonb(public.admin_is_student($1)) r', [id])).data === true,
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
await pool.query(`insert into auth.users (id, email) values ('55555555-5555-5555-5555-555555555555','owner@chem21.local') on conflict do nothing`);
await pool.query(`update public.profiles set role='admin', display_name='مالك المشروع' where email='owner@chem21.local'`);
await pool.query(`delete from auth.users where email in ('st2test@chem21.local', 'deltest@chem21.local', 'deltest2@chem21.local') or email like 'st_____@chem21.local' or email like 'bulk_@chem21.local'`);
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

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.json': 'application/json' };
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
      if (!/^[a-z_]+$/.test(fn) || fn.startsWith('_')) out = { error: { message: 'not found', code: '42883' } };
      else {
        const meta = await pool.query(`select unnest(proargnames) n, unnest(proargtypes::regtype[]::text[]) t from pg_proc where proname = $1 and pronamespace = 'public'::regnamespace`, [fn]);
        const names = Object.keys(b);
        const args = names.map((n, i) => `${n} => $${i + 1}::${meta.rows.find(r => r.n === n)?.t || 'text'}`);
        out = await asRole(uid, `select to_jsonb(public.${fn}(${args.join(', ')})) r`,
          names.map(n => b[n] !== null && typeof b[n] === 'object' ? JSON.stringify(b[n]) : b[n]));
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
const M = 'http://localhost:8766/mock';
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
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'ar', acceptDownloads: true });
await ctx.route('https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js', r => r.fulfill({ contentType: 'text/javascript', body: fs.readFileSync(process.env.XLSX_MODULE + '/xlsx/dist/xlsx.full.min.js', 'utf8') }));
await ctx.route(SDK, r => r.fulfill({ contentType: 'text/javascript', body: FAKE_SDK, headers: { 'access-control-allow-origin': '*' } }));
await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
const p = await ctx.newPage();
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error' && !/fonts|ERR_FAILED|404/.test(m.text())) errors.push('console: ' + m.text()); });
const BASE = 'http://localhost:8766/Bank/public/';
const Q2 = sel => p.locator('#mcq-list .q').nth(1).locator(sel);

try {
// الزائر: لا يرى إلا صفحة الدخول، وقاعدة البيانات ترفض طلباته مباشرة
await p.goto(BASE + '#/'); await p.waitForSelector('#l-user');
ok('anon: login page first, header hidden', !(await p.locator('.topbar').isVisible()) && !(await p.locator('.kpi').count()));
ok('login form: username + password + logo', (await p.locator('label[for="l-user"]').innerText()).includes('اسم المستخدم') && await p.locator('.login-logo').evaluate(i => i.complete && i.naturalWidth > 0));
ok('footer: copyright', (await p.locator('.footer').innerText()).includes('برمجة وتطوير الأستاذ عبدالله حمدي'));
await p.screenshot({ path: `${OUT}/supa-login.png` });
await p.goto(BASE + '#/bank'); await p.waitForSelector('#l-user');
ok('anon: deep link still shows login only', !(await p.locator('.q').count()));
const direct = await p.evaluate(async () => Promise.all(['get_bank', 'get_stats', 'get_chapters'].map(fn =>
  fetch('http://localhost:8766/mock/rpc/' + fn, { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{}' }).then(r => r.json()))));
ok('anon: database refuses direct reads', direct.every(r => r.error && !r.data), JSON.stringify(direct.map(r => r.error?.code)));

// حساب جديد لم يفعّله المشرف: رسالة انتظار فقط
await p.fill('#l-user', 'new@x.com'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]');
ok('pending: awaiting activation page', await p.locator('h1', { hasText: 'بانتظار التفعيل' }).waitFor({ timeout: 5000 }).then(() => true, () => false));
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForTimeout(800);
ok('pending: no content', !(await p.locator('.q').count()) && !(await p.locator('.topbar').isVisible()));
await p.click('#p-out'); await p.waitForSelector('#l-user');

// المعلم: يرى المحتوى والإجابات ولا يرى أدوات المراجعة
await p.fill('#l-user', 'view'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]');
await p.waitForSelector('.kpi .value');
ok('viewer: header visible after login', await p.locator('.topbar').isVisible());
ok('term: textbook, not memo (home)', !/مذكر/.test(await p.locator('main').innerText()));
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
await p.locator('[data-mode="review"]').click(); await p.waitForTimeout(500);
ok('viewer: sees answers but no review tools', (await p.locator('#mcq-list .answer:visible').count()) === 7 && (await p.locator('.q-tools').count()) === 0);
{ const t = await p.locator('main').innerText(); ok('refs: no page numbers or worksheet labels', !/ص\s*\d|ورقة/.test(t) && t.includes('المرجع: الكتاب المدرسي —'), (t.match(/المرجع:[^\n]*/) || [''])[0]); }
await p.goto(BASE + '#/bank'); await p.waitForSelector('.q, table, .empty', { timeout: 15000 });
ok('viewer: no export buttons', (await p.locator('[data-export]').count()) === 0);
await p.goto(BASE + '#/exam'); await p.waitForSelector('#x-build', { timeout: 20000 });
await p.click('#x-build'); await p.waitForSelector('.paper');
ok('viewer: exam builder builds from Supabase bank', (await p.locator('.set-student .paper').count()) >= 1);
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
ok('reviewer: questions approved by owner decision', (await p.locator('#mcq-list .badge.ok').count()) === 7);
await p.locator('[data-qedit]').nth(1).click(); await p.waitForSelector('#e-stem');
await p.fill('#e-stem', 'ما وحدة قياس طاقة الفوتون في النظام الدولي للوحدات؟');
await p.click('#e-save');
ok('edit saved through RPC', await Q2('.q-stem', { hasText: 'في النظام الدولي للوحدات' }).waitFor({ timeout: 4000 }).then(() => true, () => false));
ok('edit moved approved -> in_review', await Q2('.badge.warn', { hasText: 'قيد المراجعة' }).waitFor({ timeout: 4000 }).then(() => true, () => false));
await p.locator('[data-qhist]').nth(1).click(); await p.waitForSelector('dialog[open] table');
const hist = await p.locator('dialog[open] table').innerText();
ok('history shows edit by reviewer + owner approval', hist.includes('تعديل') && hist.includes('عبدالله حمدي') && hist.includes('مالك المشروع'));
await p.keyboard.press('Escape');
await p.locator('[data-qstatus$=":approved"]').nth(1).click(); await p.waitForTimeout(800);
ok('re-approve after passing auto-check', (await Q2('.badge.ok').count()) >= 1);
await p.click('[data-review="approve"]'); await p.waitForTimeout(800);
ok('objective approved', (await p.locator('.hero .badge.ok', { hasText: 'معتمد' }).count()) === 1);
await p.goto(BASE + '#/reports'); await p.waitForSelector('#revs table', { timeout: 8000 });
ok('reports: revisions list', (await p.locator('#revs tbody tr').count()) >= 3);
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
await p.goto(BASE + '#/students'); await p.waitForSelector('#as-file');
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
await p.selectOption('#af-grade', 'دفعة اختبار'); await p.waitForSelector('#as-all');
ok('bulk: filtered batch of 3', (await p.locator('tr[data-id]').count()) === 3);
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
const blocked = await p.evaluate(async () => (await fetch('http://localhost:8766/mock/rpc/get_bank', { method: 'POST', headers: { 'content-type': 'application/json', authorization: localStorage.getItem('mocktok') }, body: '{}' })).json());
ok('student: database refuses teacher reads', !!blocked.error);
await p.screenshot({ path: `${OUT}/student-setup.png`, fullPage: true });
await p.locator('details.st-ch').first().locator('summary').click();
await p.locator('[data-lesson]').first().check();
await p.selectOption('#s-count', '5'); await p.check('#s-timed');
await p.click('#s-start'); await p.waitForSelector('.st-opt');
ok('student: session started with timer', (await p.locator('.st-top').innerText()).includes('سؤال 1 من 5') && await p.locator('#st-timer').isVisible());
ok('student: no answer marked before answering', (await p.locator('.st-opt.ok, .st-opt.bad').count()) === 0);
for (let i = 0; i < 5; i++) {
  await p.locator('.st-opt').first().click(); await p.waitForSelector('.st-fb');
  if (i === 0) { ok('student: immediate feedback with explanation', (await p.locator('.st-fb').innerText()).includes('التفسير')); await p.screenshot({ path: `${OUT}/student-feedback.png` }); }
  await p.click('#st-next');
}
await p.waitForSelector('.st-result');
const res = await p.locator('.st-score').innerText();
ok('student: result shown', /من 5/.test(res), res);
await p.screenshot({ path: `${OUT}/student-result.png`, fullPage: true });
if (await p.locator('#st-retry').count()) {
  await p.click('#st-retry'); await p.waitForSelector('.st-opt');
  ok('student: retry mistakes session', (await p.locator('.st-top').innerText()).includes('إعادة الأخطاء'));
  await p.click('#st-end'); p.once('dialog', d => d.accept());
}
await p.goto(BASE + '#/history'); await p.waitForSelector('.hero');
await p.waitForTimeout(500);
ok('student: history lists sessions', (await p.locator('main').innerText()).includes('آخر الجلسات') && (await p.locator('main tbody tr').count()) >= 1);
await p.click('#logout'); await p.waitForSelector('#l-user');
// المعلم يرى التقدم
await p.fill('#l-user', 'view'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
await p.goto(BASE + '#/progress'); await p.waitForSelector('#tp-sec');
ok('teacher: progress lists student', (await p.locator('main').innerText()).includes('طالب ثان تجريبي'));
ok('teacher (viewer): no students admin link', !(await p.locator('[data-nav="students"]').isVisible()));

} catch (e) { results.push('FAIL exception: ' + e.message.split('\n')[0]); await p.screenshot({ path: `${OUT}/supa-fail.png` }); }
console.log(results.join('\n'));
console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no console errors');
await browser.close(); server.close(); await pool.end();
process.exit(results.some(r => r.startsWith('FAIL')) || errors.length ? 1 : 0);
