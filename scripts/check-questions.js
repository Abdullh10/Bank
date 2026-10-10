// فاحص بنيوي لملفات data/questions: node scripts/check-questions.js [رموز الأهداف...]
// يتحقق من العدد والحقول والبدائل وتشابه الأسئلة داخل الهدف. لا يغني عن المراجعة العلمية البشرية.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { autoCheck, similarity } from '../server/validate.js';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const dir = path.join(root, 'data', 'questions');
const objectives = new Set(JSON.parse(fs.readFileSync(path.join(root, 'data', 'objectives_original.json'), 'utf8'))
  .chapters.flatMap(c => c.lessons.flatMap(l => l.objectives.map(o => o.id))));
const ids = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(dir).filter(f => f.endsWith('.json')).map(f => f.slice(0, -5));
const LEVELS = ['تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع'], DIFF = ['سهل', 'متوسط', 'صعب'];
let bad = 0;
const positions = [0, 0, 0];
for (const id of ids) {
  const errs = [];
  const file = path.join(dir, id + '.json');
  if (!fs.existsSync(file)) { console.log(`✗ ${id}: الملف غير موجود`); bad++; continue; }
  let d;
  try { d = JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { console.log(`✗ ${id}: JSON غير صالح — ${e.message}`); bad++; continue; }
  if (d.objective !== id) errs.push('حقل objective لا يطابق اسم الملف');
  if (!objectives.has(id)) errs.push('رمز الهدف غير موجود في البنية');
  if ((d.mcq || []).length !== 7) errs.push(`عدد أسئلة الاختيار ${(d.mcq || []).length} (المطلوب 7)`);
  if ((d.essay || []).length !== 3) errs.push(`عدد الأسئلة المقالية ${(d.essay || []).length} (المطلوب 3)`);
  const all = [...(d.mcq || []).map(q => ({ ...q, type: 'mcq' })), ...(d.essay || []).map(q => ({ ...q, type: 'essay' }))];
  all.forEach((q, i) => {
    const tag = `${q.type === 'mcq' ? 'اختيار' : 'مقالي'} ${q.type === 'mcq' ? i + 1 : i - 6}`;
    if (!q.stem || q.stem.length < 8) errs.push(`${tag}: نص السؤال ناقص`);
    if (!LEVELS.includes(q.thinking_level)) errs.push(`${tag}: مستوى التفكير غير صالح`);
    if (!DIFF.includes(q.difficulty)) errs.push(`${tag}: الصعوبة غير صالحة`);
    if (!q.source_ref) errs.push(`${tag}: المرجع مفقود`);
    if (q.stimulus && (!Array.isArray(q.stimulus.headers) || !Array.isArray(q.stimulus.rows))) errs.push(`${tag}: جدول غير صالح`);
    if (q.type === 'mcq') {
      if (!Array.isArray(q.distractor_notes) || q.distractor_notes.length !== 3) errs.push(`${tag}: distractor_notes يجب أن يكون 3 عناصر`);
      if (Number.isInteger(q.correct_index)) positions[q.correct_index]++;
    } else {
      for (const k of ['answer_elements', 'solution_steps', 'marks', 'rubric', 'common_errors'])
        if (!Array.isArray(q[k])) errs.push(`${tag}: ${k} يجب أن يكون مصفوفة`);
      if ((q.marks || []).some(m => typeof m.marks !== 'number' || !m.element)) errs.push(`${tag}: عناصر marks يجب أن تكون {element, marks:رقم}`);
      if ((q.rubric || []).some(r => !r.level || !r.description)) errs.push(`${tag}: عناصر rubric يجب أن تكون {level, description}`);
    }
    const ac = autoCheck({ ...q, id: i }, all.map((s, j) => ({ id: j, stem: s.stem })));
    for (const c of ac.checks) if (!c.ok) errs.push(`${tag}: ${c.label}`);
  });
  if (errs.length) { bad++; console.log(`✗ ${id}\n  - ${errs.join('\n  - ')}`); }
  else console.log(`✓ ${id}`);
}
const total = positions.reduce((a, b) => a + b, 0);
if (total) console.log(`توزيع موضع الإجابة الصحيحة: أ=${positions[0]} ب=${positions[1]} ج=${positions[2]}`);
console.log(bad ? `${bad} ملفًا فيه أخطاء` : `كل الملفات (${ids.length}) سليمة بنيويًا`);
process.exit(bad ? 1 : 0);
