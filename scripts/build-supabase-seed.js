// يولّد ملفات بيانات Supabase (supabase/seed/*.sql) من نفس مصدر الاستيراد المحلي (server/seed.js)
// حتى تطابق البيانات المنشورة البنك المحلي تمامًا، بما فيه قرار الاعتماد الموثق في data/approvals.json.
// كل ملف أصغر من ~900KB ليُلصق في SQL Editor، وكل ملف قابل لإعادة التنفيذ دون تكرار (on conflict do nothing).
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'chem21-sb-'));
process.env.DB_PATH = path.join(tmp, 'seed.db');
const { seed } = await import('../server/seed.js');
const { getDb } = await import('../server/db.js');
seed({ log: () => {} });
const db = getDb();

const MAX = 900 * 1024;
const outDir = path.join(root, 'supabase', 'seed');
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

const lit = v => v === null || v === undefined ? 'null'
  : typeof v === 'number' ? String(v)
  : `'${String(v).replace(/'/g, "''")}'`;
const jsonLit = v => v === null || v === undefined ? 'null' : `${lit(v)}::jsonb`;

const TABLES = [
  { name: 'courses', cols: ['id', 'code', 'title', 'subject', 'grade', 'term', 'country', 'structure_source', 'content_source'] },
  { name: 'chapters', cols: ['id', 'course_id', 'number', 'title', 'description'] },
  { name: 'lessons', cols: ['id', 'chapter_id', 'number', 'title', 'summary', 'source_note'] },
  { name: 'objectives', cols: ['id', 'lesson_id', 'code', 'original_code', 'number', 'original_text', 'proposed_text', 'split_into', 'approved_text',
      'revision_reason', 'revision_type', 'ai_review_status', 'thinking_level', 'knowledge_type', 'concepts', 'source_page', 'memo_pages',
      'memo_coverage', 'memo_note', 'duplicate_of', 'review_status', 'required_mcq', 'required_essay'],
    json: ['split_into', 'concepts', 'memo_pages'] },
  { name: 'supplements', cols: ['objective_id', 'memo_basis', 'supplement', 'key_points', 'misconceptions', 'scientific_notes', 'confidence', 'origin', 'review_status'],
    json: ['key_points', 'misconceptions'] },
  { name: 'questions', cols: ['id', 'objective_id', 'type', 'number', 'stem', 'stimulus', 'options', 'thinking_level', 'question_kind', 'difficulty',
      'source_ref', 'status', 'excluded', 'origin', 'reviewed_at'],
    json: ['stimulus', 'options'], bool: ['excluded'] },
  { name: 'question_answers', from: 'questions', cols: ['id:question_id', 'correct_index', 'explanation', 'distractor_notes', 'model_answer', 'answer_elements',
      'solution_steps', 'marks', 'rubric', 'common_errors', 'auto_check', 'reviewer_notes'],
    json: ['distractor_notes', 'answer_elements', 'solution_steps', 'marks', 'rubric', 'common_errors', 'auto_check'] },
];

const statements = [];
for (const t of TABLES) {
  const cols = t.cols.map(c => c.split(':'));
  const rows = db.prepare(`SELECT ${cols.map(([s]) => s).join(', ')} FROM ${t.from || t.name} ORDER BY 1`).all();
  const head = `insert into public.${t.name} (${cols.map(([s, d]) => d || s).join(', ')}) values\n`;
  let batch = [];
  let size = 0;
  const flush = () => {
    if (batch.length) statements.push(head + batch.join(',\n') + '\non conflict do nothing;\n');
    batch = []; size = 0;
  };
  for (const r of rows) {
    const vals = cols.map(([s]) => {
      const v = r[s];
      if (t.json?.includes(s)) return jsonLit(v);
      if (t.bool?.includes(s)) return v ? 'true' : 'false';
      if (s === 'reviewed_at') return v ? `${lit(v)}::timestamptz` : 'null';
      return lit(v);
    });
    const row = `(${vals.join(', ')})`;
    if (size + row.length > 120 * 1024) flush();
    batch.push(row); size += row.length;
  }
  flush();
}

// سجل قرار الاعتماد: سطر لكل سؤال معتمد، يُولّد في قاعدة البيانات بدل تكرار النص آلاف المرات.
const approvals = JSON.parse(fs.readFileSync(path.join(root, 'data', 'approvals.json'), 'utf8'));
const dec = approvals.decision;
statements.push(`insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_name, at)
select 'question', q.id, 'status', '{"status":"generated"}'::jsonb, '{"status":"approved"}'::jsonb, ${lit(`${dec.by}: ${dec.note}`)}, ${lit(dec.by)}, ${lit(dec.date)}::timestamptz
from public.questions q
where q.status = 'approved' and q.origin = 'ai_generated'
  and not exists (select 1 from public.revisions r where r.entity = 'question' and r.entity_id = q.id and r.action = 'status');
select setval(pg_get_serial_sequence('public.questions', 'id'), (select max(id) from public.questions));
`);

// تجميع الأوامر في ملفات بحجم مناسب للصق.
const parts = [];
let cur = '';
for (const s of statements) {
  if (cur && Buffer.byteLength(cur + s) > MAX) { parts.push(cur); cur = ''; }
  cur += s + '\n';
}
if (cur) parts.push(cur);

const counts = Object.fromEntries(TABLES.map(t => [t.name, db.prepare(`SELECT COUNT(*) n FROM ${t.from || t.name}`).get().n]));
parts.forEach((p, i) => {
  const name = `${String(i + 1).padStart(2, '0')}.sql`;
  const header = `-- بيانات منصة كيمياء 2-1 — الجزء ${i + 1} من ${parts.length}. نفّذ الأجزاء بالترتيب بعد schema.sql.\n-- مولّد آليًا بواسطة scripts/build-supabase-seed.js — لا تعدّله يدويًا.\nbegin;\n`;
  fs.writeFileSync(path.join(outDir, name), header + p + 'commit;\n');
});
// تحقق نهائي: الأعداد المتوقعة بعد تنفيذ كل الأجزاء.
fs.writeFileSync(path.join(outDir, 'verify.sql'), `-- شغّله بعد آخر جزء: يجب أن تطابق كل الأعمدة القيم المتوقعة.
select
  (select count(*) from public.chapters) = ${counts.chapters} as chapters_ok,
  (select count(*) from public.lessons) = ${counts.lessons} as lessons_ok,
  (select count(*) from public.objectives) = ${counts.objectives} as objectives_ok,
  (select count(*) from public.supplements) = ${counts.supplements} as supplements_ok,
  (select count(*) from public.questions) = ${counts.questions} as questions_ok,
  (select count(*) from public.question_answers) = ${counts.question_answers} as answers_ok;
`);
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`${parts.length} أجزاء في supabase/seed`, counts);
for (const f of fs.readdirSync(outDir)) console.log(f, Math.round(fs.statSync(path.join(outDir, f)).size / 1024) + 'KB');
