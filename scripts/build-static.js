// يبني نسخة عرض ثابتة (للقراءة فقط) تعمل على GitHub Pages دون خادم:
// يشغّل الخادم على قاعدة بيانات مؤقتة مبنية من data/ ويحفظ ردود الواجهة البرمجية نفسها في public/static/.
// التشغيل: npm run build-static
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'chem21-static-'));
process.env.DB_PATH = path.join(tmp, 'static.db');

// نسخة العرض تتضمن فقط ملفات الأسئلة التي تجتاز الفاحص البنيوي (الملفات قيد الكتابة تُستبعد).
import { execFileSync } from 'node:child_process';
const qsrc = path.join(root, 'data', 'questions');
const qtmp = path.join(tmp, 'questions');
fs.mkdirSync(qtmp);
let checkOut = '';
try {
  checkOut = execFileSync(process.execPath, ['--disable-warning=ExperimentalWarning', path.join(root, 'scripts', 'check-questions.js')], { encoding: 'utf8' });
} catch (e) { checkOut = e.stdout || ''; }
const valid = checkOut.split('\n').filter(l => l.startsWith('✓ ')).map(l => l.slice(2).trim());
for (const id of valid) fs.copyFileSync(path.join(qsrc, id + '.json'), path.join(qtmp, id + '.json'));
process.env.QUESTIONS_DIR = qtmp;
console.log(`ملفات أسئلة سليمة مضمنة: ${valid.length}`);

const { createApp } = await import('../server/index.js');
const { seed } = await import('../server/seed.js');
const { createUser } = await import('../server/auth.js');
const crypto = await import('node:crypto');

seed({ log: () => {} });
// مستخدم اطلاع مؤقت لجلب الإجابات (يُحذف مع القاعدة المؤقتة).
const password = crypto.randomBytes(18).toString('hex');
createUser({ username: 'static_export', role: 'viewer', displayName: 'تصدير', password });

const server = createApp().listen(0);
const base = `http://127.0.0.1:${server.address().port}/api`;
const login = await fetch(base + '/login', { method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'static_export', password }) });
const cookie = login.headers.get('set-cookie').split(';')[0];
const get = async p => {
  const r = await fetch(base + p, { headers: { Cookie: cookie } });
  if (!r.ok) throw new Error(`${p}: ${r.status}`);
  return r.json();
};

const out = path.join(root, 'public', 'static');
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(path.join(out, 'objectives'), { recursive: true });
const save = (name, data) => fs.writeFileSync(path.join(out, name), JSON.stringify(data));

try {
  const stats = await get('/stats');
  stats.generatedAt = new Date().toISOString();
  save('stats.json', stats);
  const chapters = await get('/chapters');
  save('chapters.json', chapters);
  let n = 0;
  for (const c of chapters) {
    const ch = await get('/chapters/' + c.number);
    save(`chapter-${c.number}.json`, ch);
    for (const l of ch.lessons) for (const o of l.objectives) {
      save(`objectives/${o.code}.json`, await get('/objectives/' + encodeURIComponent(o.code)));
      n++;
    }
  }
  save('bank.json', await get('/bank'));
  console.log(`نسخة العرض جاهزة في public/static: ${chapters.length} فصول، ${n} هدفًا`);
} finally {
  server.close();
  fs.rmSync(tmp, { recursive: true, force: true });
}
