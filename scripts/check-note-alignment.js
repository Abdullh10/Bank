// يفحص أن ملاحظة كل بديل خاطئ تتحدث عن بديلها لا عن بديل آخر: node scripts/check-note-alignment.js --course chem3
// يقارن تقاطع كلمات الملاحظة i مع البديل i مقابل تقاطعها مع كل بديل آخر، ويعلّم الحالات التي يتفوق فيها بديل آخر بوضوح.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { tokens } from '../public/validate.js';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = process.argv.slice(2);
const ci = args.indexOf('--course');
const dir = path.join(root, 'data', ci >= 0 ? args[ci + 1] : '', 'questions');
let flags = 0, checked = 0;
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.json')).sort()) {
  const d = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  d.mcq.forEach((q, qi) => {
    const optT = q.options.map(o => tokens(o));
    q.distractor_notes.forEach((n, i) => {
      if (i === q.correct_index || !n) return;
      checked++;
      const nt = tokens(n);
      const ov = optT.map(t => { let c = 0; for (const w of nt) if (t.has(w)) c++; return t.size ? c / t.size : 0; });
      const best = Math.max(...ov), own = ov[i];
      if (best >= 0.5 && best - own >= 0.4 && ov.indexOf(best) !== i) {
        flags++;
        console.log(`${d.objective} mcq${qi + 1} ملاحظة ${'أبجد'[i]} أقرب إلى البديل ${'أبجد'[ov.indexOf(best)]} (${Math.round(own * 100)}% مقابل ${Math.round(best * 100)}%)`);
      }
    });
  });
}
console.log(`\nفُحصت ${checked} ملاحظة، ${flags} تنبيهًا`);
