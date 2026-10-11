// اختبار منشئ الاختبارات بالمتصفح على نسخة العرض: خادم ملفات ثابتة على المنفذ 8765 يقدّم المستودع تحت /Bank/، ثم: node test/exam-e2e.mjs <مجلد الإخراج>
import { createRequire } from 'node:module'; import { execSync } from 'node:child_process';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const OUT = process.argv[2]; const b = await chromium.launch(); const errs = []; const res = [];
const ok = (n, v) => res.push((v ? 'PASS ' : 'FAIL ') + n);
const p = await b.newPage({ viewport: { width: 1280, height: 1000 } });
p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error' && !/fonts/.test(m.text())) errs.push(m.text()); });
await p.goto('http://localhost:8765/Bank/public/#/exam'); await p.waitForSelector('#x-build', { timeout: 15000 });
// الفصلان 1 و2 فقط، 15 اختيار و3 مقالي، نموذجان
for (const c of [3, 4, 5, 6, 7]) await p.uncheck(`[data-ch="${c}"]`);
await p.fill('#x-mcq', '15'); await p.fill('#x-essay', '3'); await p.selectOption('#x-models', '2'); await p.fill('#x-seed', '1234');
await p.click('#x-build'); await p.waitForSelector('.paper');
ok('2 student papers', (await p.locator('.set-student .paper').count()) === 2);
ok('2 key papers', (await p.locator('.set-key .paper').count()) === 2);
ok('15 mcq in model A', (await p.locator('.set-student .paper:first-child .paper-mcq > li').count()) === 15);
ok('3 essays in model A', (await p.locator('.set-student .paper:first-child .paper-essay > li').count()) === 3);
const chs = await p.evaluate(() => [...document.querySelectorAll('.set-student .paper:first-child .pq')].length);
ok('logo loaded', await p.evaluate(() => { const i = document.querySelector('.ph-logo img'); return i.complete && i.naturalWidth > 0; }));
const keyA = await p.locator('.set-key .paper:nth-child(1) .answer-grid.key td').allInnerTexts();
const keyB = await p.locator('.set-key .paper:nth-child(2) .answer-grid.key td').allInnerTexts();
ok('keys complete', keyA.length === 15 && keyA.every(x => ['أ','ب','ج'].includes(x.trim())));
ok('model B differs', keyA.join() !== keyB.join());
// تحقق من صحة المفتاح: الإجابة في النموذج ب تطابق نص البديل الصحيح
const consistent = await p.evaluate(() => {
  const st = [...document.querySelectorAll('.set-student .paper:nth-child(2) .paper-mcq > li')];
  const kl = [...document.querySelectorAll('.set-key .paper:nth-child(2) .key-list li')];
  return st.every((li, i) => { const letter = kl[i].querySelector('b').textContent.trim()[0]; const k = ['أ','ب','ج'].indexOf(letter);
    const optText = li.querySelectorAll('.pq-opts span')[k].textContent.replace(/^[أبج]\)\s*/, '').trim();
    return kl[i].querySelector('b').textContent.includes(optText); });
});
ok('model B key matches shuffled options', consistent);
await p.screenshot({ path: `${OUT}/exam-preview.png`, fullPage: false });
// تصدير PDF
await p.evaluate(() => document.body.classList.add('exam-printing', 'xprint-student'));
await p.emulateMedia({ media: 'print' });
ok('print hides setup', !(await p.locator('#x-build').isVisible()));
await p.pdf({ path: `${OUT}/exam-student.pdf`, format: 'A4', printBackground: true, preferCSSPageSize: true });
await p.evaluate(() => { document.body.classList.remove('xprint-student'); document.body.classList.add('exam-printing', 'xprint-key'); });
await p.pdf({ path: `${OUT}/exam-key.pdf`, format: 'A4', printBackground: true, preferCSSPageSize: true });
await p.emulateMedia({ media: 'screen' });
// الاستبدال
await p.evaluate(() => document.body.classList.remove('exam-printing', 'xprint-key'));
const first = await p.locator('.set-student .paper:first-child .paper-mcq > li').first().innerText();
await p.locator('.set-student .paper:first-child .paper-mcq > li').first().click(); await p.waitForTimeout(300);
const after = await p.locator('.set-student .paper:first-child .paper-mcq > li').first().innerText();
ok('swap replaces question', first !== after);
// جوال
const m = await b.newPage({ viewport: { width: 390, height: 844 } });
await m.goto('http://localhost:8765/Bank/public/#/exam'); await m.waitForSelector('#x-build');
await m.click('#x-build'); await m.waitForSelector('.paper');
ok('mobile no h-scroll', await m.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
await m.screenshot({ path: `${OUT}/exam-mobile.png` });
await b.close(); console.log(res.join('\n')); console.log('ERRORS:', errs.join(' | ') || 'none');
