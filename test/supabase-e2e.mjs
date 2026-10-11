// اختبار وضع Supabase بالمتصفح دون اتصال بالإنترنت: قاعدة PostgreSQL محلية عليها supabase/schema.sql وملفات البيانات،
// ومحاكي بسيط لمكتبة supabase-js ينفّذ كل استدعاء بدور anon أو authenticated كما في Supabase (فتُختبر سياسات RLS والدوال المحمية فعليًا).
// التشغيل: PGURL=postgres://postgres@localhost:54329/sbtest PG_MODULE=<مسار وحدة pg> node test/supabase-e2e.mjs <مجلد الإخراج>
// قبل التشغيل: قاعدة فارغة فيها مخطط auth مبسّط (auth.users و auth.uid()) والدوران anon و authenticated، ثم schema.sql ثم supabase/seed/*.sql.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const pg = createRequire(process.env.PG_MODULE + '/')('pg');
const pool = new pg.Pool({ connectionString: process.env.PGURL });
const OUT = process.argv[2] || '.';
const SDK = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/+esm';

// مستخدمان تجريبيان: مراجع ومعلم (بلا كلمات مرور: المحاكي لا يختبر Supabase Auth نفسه بل الأدوار والسياسات).
await pool.query(`insert into auth.users (id, email) values ('11111111-1111-1111-1111-111111111111','rev@x.com'),('22222222-2222-2222-2222-222222222222','view@x.com') on conflict do nothing`);
await pool.query(`update public.profiles set role='reviewer', display_name='عبدالله حمدي' where email='rev@x.com'`);
await pool.query(`update public.profiles set role='viewer' where email='view@x.com'`);
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
  };
}`;

const browser = await chromium.launch();
const results = [], errors = [];
const ok = (n, v, extra = '') => results.push(`${v ? 'PASS' : 'FAIL'} ${n} ${extra}`);
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'ar', acceptDownloads: true });
await ctx.route(SDK, r => r.fulfill({ contentType: 'text/javascript', body: FAKE_SDK, headers: { 'access-control-allow-origin': '*' } }));
await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
const p = await ctx.newPage();
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error' && !/fonts|ERR_FAILED|404/.test(m.text())) errors.push('console: ' + m.text()); });
const BASE = 'http://localhost:8766/Bank/public/';
const Q2 = sel => p.locator('#mcq-list .q').nth(1).locator(sel);

try {
// الزائر
await p.goto(BASE + '#/'); await p.waitForSelector('.kpi .value');
ok('anon: no read-only banner in Supabase mode', !(await p.locator('text=نسخة عرض للقراءة فقط').count()));
ok('anon: stats show 2580 questions', (await p.locator('main').innerText()).includes('2580') || (await p.locator('main').innerText()).includes('2,580'));
await p.screenshot({ path: `${OUT}/supa-home.png` });
await p.goto(BASE + '#/chapter/4'); await p.waitForSelector('.obj-list');
ok('anon: chapter 4 has 5 lessons', (await p.locator('section.lesson').count()) === 5);
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
ok('anon: 7 mcq + 3 essay', (await p.locator('#mcq-list .q').count()) === 7 && (await p.locator('#essay-section .q').count()) === 3);
ok('anon: answers hidden', (await p.locator('.answer:visible').count()) === 0);
await p.locator('[data-mode="practice"]').click(); await p.waitForTimeout(300);
await Q2('[data-choose]').nth(0).click();
ok('anon: practice check via RPC', await Q2('.notice').waitFor({ timeout: 4000 }).then(() => true, () => false));
await p.goto(BASE + '#/bank'); await p.waitForSelector('.q, .bank-q, table, .empty', { timeout: 15000 });
ok('anon: no export buttons', (await p.locator('[data-export]').count()) === 0);
await p.goto(BASE + '#/exam'); await p.waitForSelector('#x-build', { timeout: 20000 });
await p.click('#x-build'); await p.waitForSelector('.paper');
ok('anon: exam builder builds from Supabase bank', (await p.locator('.set-student .paper').count()) >= 1);

// تسجيل دخول المعلم: يرى الإجابات ولا يرى أدوات المراجعة
await p.goto(BASE + '#/login'); await p.waitForSelector('#l-user');
ok('login form asks for email', (await p.locator('label[for="l-user"]').innerText()).includes('البريد'));
await p.fill('#l-user', 'view@x.com'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]');
await p.waitForSelector('#logout');
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
await p.locator('[data-mode="review"]').click(); await p.waitForTimeout(500);
ok('viewer: sees answers but no review tools', (await p.locator('#mcq-list .answer:visible').count()) === 7 && (await p.locator('.q-tools').count()) === 0);
await p.click('#logout'); await p.waitForTimeout(500);
// حساب جديد لم يفعّله المشرف: لا يرى الإجابات
await p.goto(BASE + '#/login'); await p.waitForSelector('#l-user');
await p.fill('#l-user', 'new@x.com'); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]');
await p.waitForSelector('#logout');
ok('pending account shown as awaiting activation', (await p.locator('#userbox').innerText()).includes('بانتظار التفعيل'));
await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
ok('pending account: no answers', (await p.locator('[data-mode="review"]').count()) === 0);
await p.click('#logout'); await p.waitForTimeout(500);

// المراجع
await p.goto(BASE + '#/login'); await p.waitForSelector('#l-user');
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

} catch (e) { results.push('FAIL exception: ' + e.message.split('\n')[0]); await p.screenshot({ path: `${OUT}/supa-fail.png` }); }
console.log(results.join('\n'));
console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no console errors');
await browser.close(); server.close(); await pool.end();
process.exit(results.some(r => r.startsWith('FAIL')) || errors.length ? 1 : 0);
