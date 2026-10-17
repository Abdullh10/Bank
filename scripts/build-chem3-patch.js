// يولّد ملف تحديث SQL لأسئلة كيمياء 3 التي تغيّرت بعد رفعها: node scripts/build-chem3-patch.js <commit-الأساس> [ملف-الإخراج]
// يقارن data/chem3/questions عند الالتزام الأساسي (النسخة المرفوعة) بالحالية، ويكتب UPDATE لكل سؤال تغيّر (بمفتاح: رمز الهدف + النوع + الرقم).
// لا يمس حالة الاعتماد ولا مراجعات المالك. آمن للتكرار.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { autoCheck } from '../server/validate.js';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const base = process.argv[2];
if (!base) { console.error('الاستعمال: node scripts/build-chem3-patch.js <commit> [out.sql]'); process.exit(1); }
const compact = process.argv.includes('--compact');
const out = process.argv.filter(a => !a.startsWith('--'))[3] || path.join(root, 'supabase', `chem3-patch-${new Date().toISOString().slice(0, 10)}.sql`);
const dir = 'data/chem3/questions';
const lit = v => v === null || v === undefined ? 'null' : typeof v === 'number' ? String(v) : `'${String(v).replace(/'/g, "''")}'`;
const js = v => v === null || v === undefined ? 'null' : `${lit(JSON.stringify(v))}::jsonb`;
const old = f => { try { return JSON.parse(execFileSync('git', ['show', `${base}:${dir}/${f}`], { cwd: root, encoding: 'utf8', maxBuffer: 1 << 26 })); } catch { return null; } };

const stmts = []; let changed = 0, files = 0;
for (const f of fs.readdirSync(path.join(root, dir)).filter(f => f.endsWith('.json')).sort()) {
  const now = JSON.parse(fs.readFileSync(path.join(root, dir, f), 'utf8')), was = old(f);
  if (!was) continue;
  const all = [...now.mcq.map(q => ({ ...q, type: 'mcq' })), ...now.essay.map(q => ({ ...q, type: 'essay' }))];
  let touched = false;
  for (const [type, list, oldList] of [['mcq', now.mcq, was.mcq], ['essay', now.essay, was.essay]]) {
    list.forEach((q, i) => {
      if (JSON.stringify(q) === JSON.stringify(oldList[i])) return;
      touched = true; changed++;
      const ac = autoCheck({ ...q, type, id: -1 }, all.map((s, j) => ({ id: j, stem: s.stem })).filter(s => s.stem !== q.stem));
      const obj = `(select id from public.objectives where code = ${lit(now.objective)})`;
      const qid = `(select id from public.questions where objective_id = ${obj} and type = ${lit(type)} and number = ${i + 1})`;
      if (compact) {
        const o = oldList[i], col = { stem: lit, stimulus: js, options: js, thinking_level: lit, question_kind: lit, difficulty: lit, source_ref: lit };
        const acol = { correct_index: v => v ?? 'null', explanation: v => lit(v ?? null), distractor_notes: js, model_answer: v => lit(v ?? null), answer_elements: js, solution_steps: js, marks: js, rubric: js, common_errors: js };
        const diff = (cols) => Object.entries(cols).filter(([k]) => JSON.stringify(q[k] ?? null) !== JSON.stringify(o[k] ?? null)).map(([k, fn]) => `${k} = ${fn(q[k] ?? null)}`);
        const qs = diff(col), as = diff(acol);
        if (qs.length) stmts.push(`update public.questions set ${qs.join(', ')}, updated_at = now() where id = ${qid};`);
        if (as.length) stmts.push(`update public.question_answers set ${as.join(', ')} where question_id = ${qid};`);
        return;
      }
      stmts.push(`update public.questions set stem = ${lit(q.stem)}, stimulus = ${js(q.stimulus || null)}, options = ${js(q.options || null)},
  thinking_level = ${lit(q.thinking_level)}, question_kind = ${lit(q.question_kind)}, difficulty = ${lit(q.difficulty)}, source_ref = ${lit(q.source_ref)}, updated_at = now()
where id = ${qid};
update public.question_answers set correct_index = ${q.correct_index ?? 'null'}, explanation = ${lit(q.explanation ?? null)}, distractor_notes = ${js(q.distractor_notes || null)},
  model_answer = ${lit(q.model_answer ?? null)}, answer_elements = ${js(q.answer_elements || null)}, solution_steps = ${js(q.solution_steps || null)},
  marks = ${js(q.marks || null)}, rubric = ${js(q.rubric || null)}, common_errors = ${js(q.common_errors || null)}, auto_check = ${js(ac)}
where question_id = ${qid};`);
    });
  }
  if (touched) files++;
}
fs.writeFileSync(out, `-- تحديث أسئلة كيمياء 3 التي عُدّلت بعد الرفع (${changed} سؤالًا في ${files} هدفًا). مولّد آليًا بـ scripts/build-chem3-patch.js — لا تعدّله يدويًا.
-- لا يغيّر حالة الاعتماد. آمن للتكرار. إن لم تكن نفّذت ملفات seed-chem3 بعد فلا حاجة إليه (ملفات seed محدّثة).
begin;
${stmts.join('\n')}
commit;
`);
console.log(`${changed} سؤالًا في ${files} هدفًا ←`, path.relative(root, out), Math.round(fs.statSync(out).size / 1024) + 'KB');
