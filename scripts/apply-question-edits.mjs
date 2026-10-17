// يطبّق تعديلات صياغة الأسئلة من ملفات JSON ويولّد ملف تحديث SQL محروسًا (لا يمس سؤالًا عدّله المالك يدويًا):
//   node scripts/apply-question-edits.mjs <out.sql> <edits.json>[:chem3|:21]...
// كل مدخل: {objective,type,number,action:'edit'|'keep',stem,options,stimulus,explanation,model_answer}
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const [out, ...specs] = process.argv.slice(2);
const lit = v => v === null || v === undefined ? 'null' : typeof v === 'number' ? String(v) : `'${String(v).replace(/'/g, "''")}'`;
const js = v => v === null || v === undefined ? 'null' : `${lit(JSON.stringify(v))}::jsonb`;
const stmts = []; const touched = new Set(); let n = 0;
for (const spec of specs) {
  const [file, course] = spec.split(':');
  const dir = path.join(root, course === '21' ? 'data/questions' : 'data/chem3/questions');
  for (const e of JSON.parse(fs.readFileSync(file, 'utf8'))) {
    if (e.action !== 'edit') continue;
    const f = path.join(dir, e.objective + '.json');
    const raw = fs.readFileSync(f, 'utf8'); const d = JSON.parse(raw);
    const q = d[e.type][e.number - 1];
    const old = { stem: q.stem, options: q.options, stimulus: q.stimulus, explanation: q.explanation, model_answer: q.model_answer };
    const upd = {};
    if (e.stem && e.stem !== q.stem) upd.stem = e.stem;
    if (e.options && JSON.stringify(e.options) !== JSON.stringify(q.options)) upd.options = e.options;
    if (e.stimulus && JSON.stringify(e.stimulus) !== JSON.stringify(q.stimulus)) upd.stimulus = e.stimulus;
    if (e.explanation && e.explanation !== q.explanation) upd.explanation = e.explanation;
    if (e.model_answer && e.model_answer !== q.model_answer) upd.model_answer = e.model_answer;
    if (!Object.keys(upd).length) continue;
    Object.assign(q, upd);
    fs.writeFileSync(f, JSON.stringify(d, null, 1) + (raw.endsWith('\n') ? '\n' : ''));
    touched.add(e.objective); n++;
    const qid = `(select q.id from public.questions q join public.objectives o on o.id = q.objective_id where o.code = ${lit(e.objective)} and q.type = ${lit(e.type)} and q.number = ${e.number})`;
    // الشرط: النص القديم كما هو في قاعدة البيانات؛ فإن عدّله المالك يدويًا يُترك
    const qs = [], as = [];
    if ('stem' in upd) qs.push(`stem = ${lit(upd.stem)}`);
    if ('options' in upd) qs.push(`options = ${js(upd.options)}`);
    if ('stimulus' in upd) qs.push(`stimulus = ${js(upd.stimulus)}`);
    if ('explanation' in upd) as.push(`explanation = ${lit(upd.explanation)}`);
    if ('model_answer' in upd) as.push(`model_answer = ${lit(upd.model_answer)}`);
    if (qs.length) {
      const guard = 'stem' in upd ? `stem = ${lit(old.stem)}` : 'options' in upd ? `options = ${js(old.options)}` : `stimulus is not distinct from ${js(old.stimulus)}`;
      stmts.push(`update public.questions set ${qs.join(', ')}, updated_at = now() where id = ${qid} and ${guard};`);
    }
    if (as.length) {
      const g = 'explanation' in upd ? `explanation = ${lit(old.explanation)}` : `model_answer = ${lit(old.model_answer)}`;
      stmts.push(`update public.question_answers set ${as.join(', ')} where question_id = ${qid} and ${g};`);
    }
  }
}
fs.writeFileSync(out, `-- إزالة الإحالات إلى «الكتاب/المذكرة/الشكل» من نص ${n} سؤالًا في كيمياء 3 و2-1. مولّد آليًا بـ scripts/apply-question-edits.mjs.
-- محروس: يعدّل السؤال فقط إن كان نصه الحالي هو النص القديم، فلا يمس سؤالًا عدّلته يدويًا. لا يغيّر الاعتماد ولا المفاتيح. آمن للتكرار.
begin;
${stmts.join('\n')}
commit;
`);
console.log(`${n} سؤالًا في ${touched.size} ملفًا؛ ${stmts.length} أمرًا ←`, path.relative(root, out));
