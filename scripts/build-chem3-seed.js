// يولّد ملفات بيانات مقرر كيمياء 3 (المقرر 4) لـ Supabase: supabase/seed-chem3/*.sql
// المصدر: data/chem3 (البنية، ومراجعة الأهداف واعتمادها، والمحتوى المكمّل، وملفات الأسئلة).
// المقرر يبقى «قيد الإعداد» (يراه مالك المشروع وحده)؛ والأسئلة تُرفع بحالة «مولدة» حتى يعتمدها.
// كل ملف أصغر من ~900KB ليُلصق في SQL Editor، وقابل لإعادة التنفيذ دون تكرار.
// التشغيل: node scripts/build-chem3-seed.js
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { autoCheck } from '../server/validate.js';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = path.join(root, 'data', 'chem3');
const read = f => JSON.parse(fs.readFileSync(path.join(src, f), 'utf8'));
const structure = read('objectives_original.json');
const reviewsFile = read('objective_reviews.json');
const reviews = Object.fromEntries(reviewsFile.items.map(r => [r.id, r]));
const sups = Object.fromEntries(read('supplements.json').items.map(s => [s.id, s]));
const COURSE = 4;
// معرفات ثابتة لا تتقاطع مع كيمياء 2-1 (الفصول 1–7، الدروس 1–28، الأهداف 1–258)
const chId = c => COURSE * 100 + c;                       // 401…
const lsId = (c, l) => COURSE * 1000 + c * 10 + l;        // 4011…
const objId = (c, l, o) => COURSE * 100000 + c * 1000 + l * 100 + o; // 401101…

const lit = v => v === null || v === undefined ? 'null'
  : typeof v === 'number' ? String(v)
  : `'${String(v).replace(/'/g, "''")}'`;
const js = v => v === null || v === undefined ? 'null' : `${lit(JSON.stringify(v))}::jsonb`;

const approval = reviewsFile.meta.approval, addedApproval = reviewsFile.meta.added?.approval;
const statements = [];
const counts = { chapters: 0, lessons: 0, objectives: 0, supplements: 0, questions: 0 };

statements.push(`update public.courses set structure_source = ${lit(structure.source.structure_basis)},
  content_source = ${lit('الكتاب المدرسي كيمياء 3 (طبعة 1448)')} where id = ${COURSE};`);

const objRows = [], supRows = [];
for (const ch of structure.chapters) {
  statements.push(`insert into public.chapters (id, course_id, number, title) values (${chId(ch.number)}, ${COURSE}, ${ch.number}, ${lit(ch.title)}) on conflict do nothing;`);
  counts.chapters++;
  for (const ls of ch.lessons) {
    statements.push(`insert into public.lessons (id, chapter_id, number, title) values (${lsId(ch.number, ls.number)}, ${chId(ch.number)}, ${ls.number}, ${lit(ls.title)}) on conflict do nothing;`);
    counts.lessons++;
    ls.objectives.forEach((o, i) => {
      const r = reviews[o.id];
      if (!r) throw new Error(`لا مراجعة للهدف ${o.id}`);
      const approved = r.added_from_textbook ? addedApproval?.status === 'approved' : approval?.status === 'approved';
      const id = objId(ch.number, ls.number, i + 1);
      const note = (r.added_from_textbook ? 'هدف مضاف من الكتاب المدرسي (لا يرد في ملف الأهداف الرسمي). ' : '') + (r.coverage?.basis || '');
      objRows.push(`(${[id, lsId(ch.number, ls.number), lit(o.id), 'null', i + 1, lit(o.text.trim()), lit(r.proposed), js(r.split_into || []),
        approved ? lit(r.proposed) : 'null', lit(r.revision_reason), lit(r.revision_type), lit(r.status), lit(r.thinking_level), lit(r.knowledge_type),
        js(r.concepts || []), 'null', js(r.coverage?.book_pages || []), lit(r.coverage?.label), lit(note), 'null',
        lit(approved ? 'approved' : 'pending'), approved ? `${lit((r.added_from_textbook ? addedApproval : approval).date)}::timestamptz` : 'null'].join(', ')})`);
      counts.objectives++;
      const s = sups[o.id];
      if (s) {
        supRows.push(`(${[id, lit(s.memo_basis), lit(s.supplement), js(s.key_points), js(s.common_misconceptions), lit(s.scientific_notes), lit(s.confidence)].join(', ')})`);
        counts.supplements++;
      }
    });
  }
}
statements.push(`insert into public.objectives (id, lesson_id, code, original_code, number, original_text, proposed_text, split_into, approved_text,
  revision_reason, revision_type, ai_review_status, thinking_level, knowledge_type, concepts, source_page, memo_pages, memo_coverage, memo_note,
  duplicate_of, review_status, reviewed_at) values\n${objRows.join(',\n')}\non conflict do nothing;`);
if (supRows.length) statements.push(`insert into public.supplements (objective_id, memo_basis, supplement, key_points, misconceptions, scientific_notes, confidence) values\n${supRows.join(',\n')}\non conflict do nothing;`);
for (const [a, label] of [[approval, false], [addedApproval, true]]) {
  if (a?.status !== 'approved') continue;
  statements.push(`insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_name, at)
select 'objective', o.id, 'approve', '{"reviewStatus":"pending","approvedText":null}'::jsonb, jsonb_build_object('reviewStatus', 'approved', 'approvedText', o.approved_text),
  ${lit(`${a.by}: ${label ? 'اعتماد الأهداف المضافة من الكتاب المدرسي' : 'اعتماد مراجعة الأهداف الرسمية'}`)}, ${lit(a.by)}, ${lit(a.date)}::timestamptz
from public.objectives o where o.code like 'K3-%' and o.review_status = 'approved'
  and (o.memo_note like 'هدف مضاف من الكتاب%') = ${label}
  and not exists (select 1 from public.revisions r where r.entity = 'objective' and r.entity_id = o.id and r.action = 'approve');`);
}

// الأسئلة: بحالة «مولدة» دون معرف ثابت (معرف تلقائي)، وإجاباتها في question_answers بالربط على (الهدف، النوع، الرقم)
const qdir = path.join(src, 'questions');
const codes = new Set(structure.chapters.flatMap(c => c.lessons.flatMap(l => l.objectives.map(o => o.id))));
for (const f of fs.existsSync(qdir) ? fs.readdirSync(qdir).filter(f => f.endsWith('.json')).sort() : []) {
  const set = JSON.parse(fs.readFileSync(path.join(qdir, f), 'utf8'));
  if (!codes.has(set.objective)) throw new Error(`هدف غير موجود في ${f}: ${set.objective}`);
  const all = [...set.mcq.map(q => ({ ...q, type: 'mcq' })), ...set.essay.map(q => ({ ...q, type: 'essay' }))];
  const rows = [];
  for (const [type, list] of [['mcq', set.mcq], ['essay', set.essay]]) {
    list.forEach((q, i) => {
      const ac = autoCheck({ ...q, type, id: `${type}${i}` }, all.map((s, j) => ({ id: `${s.type}${s.type === 'mcq' ? j : j - set.mcq.length}`, stem: s.stem })));
      rows.push({ type, n: i + 1, q, ac });
      counts.questions++;
    });
  }
  const obj = `(select id from public.objectives where code = ${lit(set.objective)})`;
  statements.push(`insert into public.questions (objective_id, type, number, stem, stimulus, options, thinking_level, question_kind, difficulty, source_ref, status, origin)
select ${obj}, v.type, v.number, v.stem, v.stimulus::jsonb, v.options::jsonb, v.tl, v.qk, v.diff, v.src, 'generated', 'ai_generated'
from (values\n${rows.map(({ type, n, q }) => `(${[lit(type), n, lit(q.stem), js(q.stimulus || null), js(q.options || null), lit(q.thinking_level), lit(q.question_kind), lit(q.difficulty), lit(q.source_ref)].join(', ')})`).join(',\n')}
) as v(type, number, stem, stimulus, options, tl, qk, diff, src)
where not exists (select 1 from public.questions x where x.objective_id = ${obj} and x.type = v.type and x.number = v.number);
insert into public.question_answers (question_id, correct_index, explanation, distractor_notes, model_answer, answer_elements, solution_steps, marks, rubric, common_errors, auto_check)
select x.id, v.ci::int, v.ex::text, v.dn::jsonb, v.ma::text, v.ae::jsonb, v.ss::jsonb, v.mk::jsonb, v.rb::jsonb, v.ce::jsonb, v.ac::jsonb
from (values\n${rows.map(({ type, n, q, ac }) => `(${[lit(type), n, q.correct_index ?? 'null::int', lit(q.explanation ?? null), js(q.distractor_notes || null), lit(q.model_answer ?? null),
    js(q.answer_elements || null), js(q.solution_steps || null), js(q.marks || null), js(q.rubric || null), js(q.common_errors || null), js(ac)].join(', ')})`).join(',\n')}
) as v(type, number, ci, ex, dn, ma, ae, ss, mk, rb, ce, ac)
join public.questions x on x.objective_id = ${obj} and x.type = v.type and x.number = v.number
on conflict (question_id) do nothing;`);
}

const MAX = 900 * 1024;
const outDir = path.join(root, 'supabase', 'seed-chem3');
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });
const parts = [];
let cur = '';
for (const s of statements) {
  if (cur && Buffer.byteLength(cur + s) > MAX) { parts.push(cur); cur = ''; }
  cur += s + '\n\n';
}
if (cur) parts.push(cur);
parts.forEach((p, i) => {
  const header = `-- بيانات مقرر كيمياء 3 (المقرر 4، قيد الإعداد) — الجزء ${i + 1} من ${parts.length}. نفّذ الأجزاء بالترتيب.\n-- مولّد آليًا بواسطة scripts/build-chem3-seed.js — لا تعدّله يدويًا.\nbegin;\n`;
  fs.writeFileSync(path.join(outDir, `${String(i + 1).padStart(2, '0')}.sql`), header + p + 'commit;\n');
});
const inCourse = `join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id where c.course_id = ${COURSE}`;
fs.writeFileSync(path.join(outDir, 'verify.sql'), `-- شغّله بعد آخر جزء: يجب أن تكون كل الأعمدة true.
select
  (select count(*) from public.chapters where course_id = ${COURSE}) = ${counts.chapters} as chapters_ok,
  (select count(*) from public.lessons l join public.chapters c on c.id = l.chapter_id where c.course_id = ${COURSE}) = ${counts.lessons} as lessons_ok,
  (select count(*) from public.objectives o ${inCourse}) = ${counts.objectives} as objectives_ok,
  (select count(*) from public.supplements s join public.objectives o on o.id = s.objective_id ${inCourse}) = ${counts.supplements} as supplements_ok,
  (select count(*) from public.questions q join public.objectives o on o.id = q.objective_id ${inCourse}) = ${counts.questions} as questions_ok,
  (select count(*) from public.question_answers a join public.questions q on q.id = a.question_id join public.objectives o on o.id = q.objective_id ${inCourse}) = ${counts.questions} as answers_ok,
  (select status from public.courses where id = ${COURSE}) = 'preparing' as still_preparing;
`);
console.log(`${parts.length} أجزاء في supabase/seed-chem3`, counts);
for (const f of fs.readdirSync(outDir)) console.log(f, Math.round(fs.statSync(path.join(outDir, f)).size / 1024) + 'KB');
