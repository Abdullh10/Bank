// اختبار واجهة شامل بالمتصفح (Playwright). التشغيل: خادم على المنفذ 3123 بقاعدة بيانات تجريبية ومستخدم reviewer1، ثم: node test/ui-e2e.mjs <مجلد الصور>
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const OUT = process.argv[2], BASE = 'http://localhost:3123';
async function login(pg) {
  await pg.goto(BASE + '/#/'); await pg.waitForSelector('#l-user');
  check('login page first, header hidden', !(await pg.locator('.topbar').isVisible()));
  await pg.fill('#l-user', 'reviewer1'); await pg.fill('#l-pass', 'Test-Pass-12345'); await pg.click('button[type=submit]');
  await pg.waitForSelector('#logout');
}
const browser = await chromium.launch();
const errors = [];
const results = [];
const check = (name, ok, extra = '') => { results.push(`${ok ? 'PASS' : 'FAIL'} ${name} ${extra}`); };
async function page(vp) {
  const ctx = await browser.newContext({ viewport: vp, locale: 'ar' });
  const p = await ctx.newPage();
  p.on('pageerror', e => errors.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' && !/fonts\.g/.test(m.text())) errors.push('console: ' + m.text()); });
  return p;
}
const noHScroll = p => p.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);

for (const [name, vp] of [['desktop', { width: 1366, height: 900 }], ['ipad', { width: 820, height: 1180 }], ['mobile', { width: 390, height: 844 }]]) {
  const p = await page(vp);
  await login(p);
  await p.goto(BASE + '/#/'); await p.waitForSelector('.kpi .value');
  check(`${name}: RTL`, await p.evaluate(() => getComputedStyle(document.body).direction === 'rtl'));
  check(`${name}: no horizontal scroll (home)`, await noHScroll(p));
  await p.screenshot({ path: `${OUT}/${name}-home.png`, fullPage: true });
  await p.goto(BASE + '/#/chapter/4'); await p.waitForSelector('.obj-list');
  check(`${name}: chapter 4 has 5 lessons`, (await p.locator('section.lesson').count()) === 5);
  check(`${name}: no horizontal scroll (chapter)`, await noHScroll(p));
  await p.goto(BASE + '/#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
  check(`${name}: no horizontal scroll (objective)`, await noHScroll(p));
  await p.screenshot({ path: `${OUT}/${name}-objective.png`, fullPage: true });
  await p.context().close();
}

// الاختبار والتدريب الفوري (بعد الدخول)
const p = await page({ width: 1280, height: 900 });
await login(p);
await p.goto(BASE + '/#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
check('anon: answers hidden in test mode', (await p.locator('.answer:visible').count()) === 0);
check('anon: 7 mcq + 3 essay cards', (await p.locator('#mcq-list .q').count()) === 7 && (await p.locator('#essay-section .q').count()) === 3);
await p.locator('[data-choose]').nth(0).click(); await p.waitForTimeout(200);
await p.locator('#finish-test').click(); await p.waitForTimeout(500);
check('anon: test finished shows feedback', (await p.locator('.notice.ok, .notice.bad').count()) >= 1);
await p.locator('[data-mode="practice"]').click(); await p.waitForTimeout(300);
await p.locator('#q-2 [data-choose]').nth(1).click(); await p.waitForTimeout(400);
check('anon: practice feedback wrong answer', (await p.locator('#q-2 .notice.bad').count()) === 1);
await p.screenshot({ path: `${OUT}/practice.png`, fullPage: false });
// تسجيل الدخول والمراجعة
await p.goto(BASE + '/#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
await p.locator('[data-mode="review"]').click(); await p.waitForSelector('.q-tools');
check('review: answers visible', (await p.locator('#mcq-list .answer:visible').count()) === 7);
check('review: essay model answers open', (await p.locator('#essay-section details[open]').count()) === 3);
await p.screenshot({ path: `${OUT}/review.png`, fullPage: true });
// اعتماد سؤال
await p.locator('[data-qstatus$=":approved"]').first().click(); await p.waitForTimeout(500);
check('review: approve question -> badge', (await p.locator('#mcq-list .badge.ok').count()) >= 1);
// تعديل سؤال عبر النافذة
await p.locator('[data-qedit]').nth(1).click(); await p.waitForSelector('#e-stem');
await p.fill('#e-stem', 'ما وحدة قياس طاقة الفوتون في النظام الدولي للوحدات؟');
await p.click('#e-save');
check('edit: saved stem shown', await p.locator('#q-2 .q-stem', { hasText: 'في النظام الدولي للوحدات' }).waitFor({ timeout: 3000 }).then(() => true, () => false));
check('edit: status moved to in_review', await p.locator('#q-2 .badge.warn', { hasText: 'قيد المراجعة' }).waitFor({ timeout: 3000 }).then(() => true, () => false));
await p.locator('[data-qhist]').nth(1).click(); await p.waitForSelector('dialog[open] table');
check('history: edit row present', (await p.locator('dialog[open] td', { hasText: 'تعديل' }).count()) >= 1);
await p.keyboard.press('Escape');
// اعتماد الهدف
await p.click('[data-review="approve"]'); await p.waitForTimeout(500);
check('objective approved badge', (await p.locator('.hero .badge.ok', { hasText: 'معتمد' }).count()) === 1);
// الطباعة: نسخة الطالب تخفي الحلول
await p.evaluate(() => { document.body.classList.add('print-student'); });
await p.emulateMedia({ media: 'print' });
check('print student hides answers', (await p.locator('.answer:visible').count()) === 0);
await p.pdf({ path: `${OUT}/student.pdf` });
await p.evaluate(() => { document.body.classList.replace('print-student', 'print-teacher'); });
check('print teacher shows answers', (await p.locator('.answer:visible').count()) >= 7);
await p.pdf({ path: `${OUT}/teacher.pdf` });
await p.emulateMedia({ media: 'screen' });
// البنك
await p.goto(BASE + '/#/bank'); await p.waitForSelector('#bank-list .q');
check('bank: 10 questions', (await p.locator('#bank-list .q').count()) === 10);
await p.selectOption('#f-type', 'essay'); await p.waitForTimeout(400);
check('bank: filter essay -> 3', (await p.locator('#bank-list .q').count()) === 3);
await p.click('#f-clear'); await p.waitForTimeout(300);
await p.fill('#f-q', 'الميكروويف'); await p.click('#f-apply'); await p.waitForTimeout(300);
check('bank: search', (await p.locator('#bank-list .q').count()) >= 1);
await p.click('#f-clear'); await p.waitForTimeout(300);
p.once('dialog', d => d.accept('اختبار قصير'));
await p.click('[data-sheet="teacher"]'); await p.waitForSelector('#do-print');
check('bank: teacher sheet with key', (await p.getByText('مفتاح الإجابات').count()) === 1);
await p.screenshot({ path: `${OUT}/sheet.png`, fullPage: true });
await p.goto(BASE + '/#/reports'); await p.waitForSelector('#revs table');
check('reports: revisions table', true);
await p.screenshot({ path: `${OUT}/reports.png`, fullPage: true });
await browser.close();
console.log(results.join('\n'));
console.log('ERRORS:', errors.length ? errors.join('\n') : 'none');
