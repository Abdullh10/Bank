// اختبار منشئ الاختبارات بالمتصفح على الخادم المحلي (المنفذ 3123، بيانات كاملة npm run seed، ومستخدم reviewer1): node test/exam-header-e2e.mjs <مجلد الإخراج>
import { createRequire } from 'node:module'; import { execSync } from 'node:child_process';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const BASE = process.env.BASE || 'http://localhost:3123';
// المنصة مغلقة: كل اختبار يبدأ بتسجيل الدخول (خادم محلي بمستخدم reviewer1 / Test-Pass-12345).
async function login(pg) {
  await pg.goto(BASE + '/#/'); await pg.waitForSelector('#l-user');
  await pg.fill('#l-user', process.env.E2E_USER || 'reviewer1'); await pg.fill('#l-pass', process.env.E2E_PASS || 'Test-Pass-12345');
  await pg.click('button[type=submit]'); await pg.waitForSelector('#logout');
}
const b = await chromium.launch(); const res = []; const errs = [];
const ok = (n, v) => res.push((v ? 'PASS ' : 'FAIL ') + n);
for (const vp of [{ width: 1280, height: 1100 }, { width: 390, height: 844 }]) {
  const p = await b.newPage({ viewport: vp }); p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(() => { window.__ITQAN_NO_BIDI = true; }); // عزل الاتجاه يضيف علامات غير مرئية والاختبار يقارن النص حرفيًا
  await login(p); await p.goto(BASE + '/#/exam'); await p.waitForSelector('#x-build');
  await p.selectOption('[data-hsel="title"]', 'اختبار منتصف الفصل الدراسي');
  await p.selectOption('[data-hsel="duration"]', 'ساعة ونصف');
  await p.selectOption('[data-hsel="grade"]', '__other');
  ok(`${vp.width} other input shown`, await p.locator('[data-hother="grade"]').isVisible());
  await p.fill('[data-hother="grade"]', 'الثاني الثانوي – علمي');
  await p.click('#h-today');
  ok(`${vp.width} today preview (year/month/day then هـ)`, /1448\/\d+\/\d+هـ/.test(await p.locator('#h-date-preview').innerText()));
  await p.selectOption('[data-hd="dateFormat"]', 'name');
  const prev = await p.locator('#h-date-preview').innerText();
  ok(`${vp.width} month name preview`, /ربيع|جمادى|محرم|صفر|رجب|شعبان|رمضان|شوال|ذو/.test(prev));
  await p.click('#x-build'); await p.waitForSelector('.paper');
  const head = await p.locator('.set-student .paper:first-child').innerText();
  ok(`${vp.width} title in paper`, head.includes('اختبار منتصف الفصل الدراسي'));
  ok(`${vp.width} duration in paper`, head.includes('ساعة ونصف'));
  ok(`${vp.width} custom grade in paper`, head.includes('الثاني الثانوي – علمي'));
  ok(`${vp.width} date in paper`, head.includes(prev.replace('سيُطبع: ', '')));
  ok(`${vp.width} no h-scroll`, await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
  // يحفظ الاختيارات بعد إعادة التحميل
  await p.reload(); await p.waitForSelector('#x-build');
  ok(`${vp.width} persisted title`, (await p.locator('[data-hsel="title"]').inputValue()) === 'اختبار منتصف الفصل الدراسي');
  ok(`${vp.width} persisted other`, (await p.locator('[data-hother="grade"]').inputValue()) === 'الثاني الثانوي – علمي');
  if (vp.width === 1280) await p.screenshot({ path: process.argv[2] + '/exam-header-form.png', clip: { x: 0, y: 150, width: 1280, height: 950 } });
  await p.close();
}
await b.close(); console.log(res.join('\n')); console.log('ERRORS:', errs.join(' | ') || 'none');
