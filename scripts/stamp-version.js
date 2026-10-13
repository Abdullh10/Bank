// ختم إصدار الموقع: رقم مشتق من محتوى ملفات public/*.js و styles.css يُضاف إلى روابطها في index.html
// (خريطة استيراد importmap)، ويُكتب في public/version.json. فيجلب المتصفح الملفات الجديدة فور النشر
// بدل نسخته المحفوظة، ولا يخلط ملفات قديمة بجديدة.
// التشغيل بعد أي تعديل على الواجهة: node scripts/stamp-version.js   (والتحقق فقط: --check)
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const pub = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public');
const mods = fs.readdirSync(pub).filter(f => f.endsWith('.js')).sort();
const hash = crypto.createHash('sha256');
for (const f of [...mods, 'styles.css']) hash.update(f + '\0').update(fs.readFileSync(path.join(pub, f)));
const v = hash.digest('hex').slice(0, 10);

const imports = Object.fromEntries(mods.map(f => [`./${f}`, `./${f}?v=${v}`]));
const block = `<!-- version:start (يُولَّد بـ scripts/stamp-version.js؛ لا تعدّله يدويًا) -->
  <meta name="itqan-version" content="${v}">
  <script type="importmap">${JSON.stringify({ imports })}</script>
  <link rel="stylesheet" href="styles.css?v=${v}">
  <script type="module" src="app.js?v=${v}"></script>
  <!-- version:end -->`;

const htmlPath = path.join(pub, 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const re = /<!-- version:start[\s\S]*?<!-- version:end -->/;
if (!re.test(html)) throw new Error('index.html: لا توجد علامتا version:start و version:end');
const next = html.replace(re, block);
const verPath = path.join(pub, 'version.json');
const verJson = JSON.stringify({ v }) + '\n';

if (process.argv.includes('--check')) {
  const ok = next === html && fs.existsSync(verPath) && fs.readFileSync(verPath, 'utf8') === verJson;
  if (!ok) { console.error(`الإصدار غير مختوم: شغّل node scripts/stamp-version.js (المتوقع ${v})`); process.exit(1); }
  console.log('الإصدار مختوم:', v);
} else {
  fs.writeFileSync(htmlPath, next);
  fs.writeFileSync(verPath, verJson);
  console.log('خُتم الإصدار:', v);
}
