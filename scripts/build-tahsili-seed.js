// يولّد ملفات قسم «الاستعداد للتحصيلي» (المقرر 5) لـ Supabase: supabase/seed-tahsili/*.sql
// المصدر: data/tahsili/units.json (المواد والوحدات والموضوعات) وdata/tahsili/questions/*.json (الأسئلة).
// يفحص كل سؤال أولًا (scripts/tahsili-lib.js) ولا يكتب شيئًا إن وُجد خطأ.
// الأسئلة تُرفع بحالة «مولدة» حتى تُعتمد من المنصة؛ والتنفيذ آمن للتكرار: السؤال الموجود (بالموضوع والرقم) لا يُكرر ولا يُستبدل.
// ترقيم الأسئلة بترتيبها داخل الموضوع: أضف الجديد في آخر الملف ولا تحذف سؤالًا رُفع ولا تعيد ترتيبه.
// التشغيل: node scripts/build-tahsili-seed.js            (التوليد)
//          node scripts/build-tahsili-seed.js --check    (الفحص فقط)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { autoCheck } from '../server/validate.js';
import { COURSE, subjectId, unitId, topicId, topicCode, checkQuestion } from './tahsili-lib.js';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = path.join(root, 'data', 'tahsili');
const out = path.join(root, 'supabase', 'seed-tahsili');
const checkOnly = process.argv.includes('--check');
const structure = JSON.parse(fs.readFileSync(path.join(src, 'units.json'), 'utf8'));

const lit = v => v === null || v === undefined ? 'null' : typeof v === 'number' ? String(v) : `'${String(v).replace(/'/g, "''")}'`;
const js = v => v === null || v === undefined ? 'null' : `${lit(JSON.stringify(v))}::jsonb`;

// ---------- البنية ----------
const units = new Map(); // "s-u" → { s, u, unit }
const head = [];
for (const s of structure.subjects) {
  head.push(`insert into public.chapters (id, course_id, number, title, description) values (${subjectId(s.number)}, ${COURSE}, ${s.number}, ${lit(s.title)}, '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;`);
  for (const u of s.units) {
    if (u.number < 1 || u.number > 99) throw new Error(`رقم الوحدة ${u.number} خارج 1–99 (${s.title})`);
    units.set(`${s.number}-${u.number}`, { s: s.number, u: u.number, unit: u });
    head.push(`insert into public.lessons (id, chapter_id, number, title, summary) values (${unitId(s.number, u.number)}, ${subjectId(s.number)}, ${u.number}, ${lit(u.title)}, ${lit(u.grade ? `الصف ${u.grade}` : null)})
on conflict (id) do update set title = excluded.title, summary = excluded.summary;`);
    for (const t of u.topics) {
      head.push(`insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (${topicId(s.number, u.number, t.number)}, ${unitId(s.number, u.number)}, ${lit(topicCode(s.number, u.number, t.number))}, ${t.number}, ${lit(t.title)}, ${lit(t.title)}, null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;`);
    }
  }
}

// وحدات قديمة لم تعد في units.json تُحذف إن لم يكن فيها أسئلة (مع موضوعاتها)؛ وما فيه أسئلة يبقى ولا يُمس
const keep = [...units.values()].map(x => unitId(x.s, x.u));
head.push(`delete from public.lessons l using public.chapters c
where l.chapter_id = c.id and c.course_id = ${COURSE} and l.id not in (${keep.join(', ')})
  and not exists (select 1 from public.objectives o join public.questions q on q.objective_id = o.id where o.lesson_id = l.id);`);

// ---------- الأسئلة ----------
const errors = [], blocks = [];
let total = 0;
const files = fs.existsSync(path.join(src, 'questions')) ? fs.readdirSync(path.join(src, 'questions')).filter(f => f.endsWith('.json')).sort() : [];
for (const f of files) {
  const m = f.match(/^(\d)-(\d{1,2})\.json$/);
  if (!m) { errors.push(`${f}: اسم الملف <المادة>-<الوحدة>.json (مثل 2-11.json)`); continue; }
  const key = `${Number(m[1])}-${Number(m[2])}`;
  const unit = units.get(key);
  if (!unit) { errors.push(`${f}: الوحدة غير موجودة في units.json`); continue; }
  const data = JSON.parse(fs.readFileSync(path.join(src, 'questions', f), 'utf8'));
  const topics = unit.unit.topics.map(t => t.number);
  const byTopic = new Map();
  (data.questions || []).forEach((q, i) => {
    const e = checkQuestion(q, { topics, publicDir: path.join(root, 'public') });
    if (e.length) errors.push(`${f} السؤال ${i + 1}: ${e.join('؛ ')}`);
    const t = q.topic ?? 1;
    if (!byTopic.has(t)) byTopic.set(t, []);
    byTopic.get(t).push(q);
  });
  for (const [t, qs] of byTopic) {
    const obj = topicId(unit.s, unit.u, t);
    const rows = qs.map((q, i) => ({ n: i + 1, q, ac: autoCheck({ ...q, type: 'mcq' }, []) }));
    total += rows.length;
    blocks.push(`-- ${f} · الموضوع ${t} (${rows.length} سؤالًا)
insert into public.questions (objective_id, type, number, stem, stimulus, images, options, thinking_level, question_kind, difficulty, source_ref, status, origin)
select ${obj}, 'mcq', v.number, v.stem, null, v.images::jsonb, v.options::jsonb, v.tl, v.qk, v.diff, v.src, 'generated', 'tahsili_collection'
from (values\n${rows.map(({ n, q }) => `(${[n, lit(q.stem.trim()), js(q.images?.length ? q.images : null), js(q.options), lit(q.thinking_level), lit(q.question_kind ?? null), lit(q.difficulty), lit(q.source_ref ?? data.meta?.source ?? null)].join(', ')})`).join(',\n')}
) as v(number, stem, images, options, tl, qk, diff, src)
where not exists (select 1 from public.questions x where x.objective_id = ${obj} and x.type = 'mcq' and x.number = v.number);
insert into public.question_answers (question_id, correct_index, explanation, distractor_notes, auto_check)
select x.id, v.ci, v.ex, v.dn::jsonb, v.ac::jsonb
from (values\n${rows.map(({ n, q, ac }) => `(${[n, q.correct_index, lit(q.explanation), js(q.distractor_notes), js(ac)].join(', ')})`).join(',\n')}
) as v(number, ci, ex, dn, ac)
join public.questions x on x.objective_id = ${obj} and x.type = 'mcq' and x.number = v.number
on conflict (question_id) do nothing;`);
  }
}

if (errors.length) {
  console.error(`أخطاء في ${errors.length} موضع؛ لم يُكتب شيء:\n` + errors.map(e => '  - ' + e).join('\n'));
  process.exit(1);
}
console.log(`البنية: ${structure.subjects.length} مواد و${units.size} وحدة؛ الأسئلة: ${total} في ${files.length} ملف.`);
if (checkOnly) process.exit(0);

// ملفات أصغر من ~900KB لتُلصق في SQL Editor
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });
const parts = [head.join('\n')];
for (const b of blocks) {
  if (Buffer.byteLength(parts[parts.length - 1]) + Buffer.byteLength(b) > 900_000) parts.push(b);
  else parts[parts.length - 1] += '\n\n' + b;
}
parts.forEach((p, i) => fs.writeFileSync(path.join(out, `${String(i + 1).padStart(2, '0')}.sql`),
  `-- قسم «الاستعداد للتحصيلي» (${i + 1}/${parts.length}) — يولَّد بـ node scripts/build-tahsili-seed.js؛ لا تعدّله يدويًا.\n-- يتطلب تنفيذ supabase/schema.sql أولًا. آمن للتكرار.\nbegin;\n${p}\ncommit;\n`));
console.log(`كُتب ${parts.length} ملف في supabase/seed-tahsili/`);
