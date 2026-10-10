// استيراد البيانات من ملفات data/ إلى قاعدة البيانات.
// آمن للتكرار: يضيف ما ليس موجودًا فقط ولا يمس تعديلات المراجعين أو قرارات الاعتماد.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';
import { getDb, tx, J } from './db.js';
import { autoCheck } from './validate.js';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const read = f => JSON.parse(fs.readFileSync(path.join(root, 'data', f), 'utf8'));

export function seed({ log = console.log } = {}) {
  const db = getDb();
  const src = read('objectives_original.json');
  const reviews = Object.fromEntries(read('objective_reviews.json').items.map(r => [r.id, r]));
  const sups = Object.fromEntries(read('supplements.json').items.map(s => [s.id, s]));
  const stats = { objectives: 0, supplements: 0, questions: 0 };

  tx(() => {
    const c = src.course;
    db.prepare(`INSERT OR IGNORE INTO courses (code, title, subject, grade, term, country, structure_source, content_source)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)`).run(c.code, `${c.subject} ${c.code.replace('كيمياء ', '')}`, c.subject, c.grade, c.term,
      c.country, src.source.structure_basis, src.source.content_basis);
    const courseId = db.prepare('SELECT id FROM courses WHERE code = ?').get(c.code).id;

    for (const ch of src.chapters) {
      db.prepare('INSERT OR IGNORE INTO chapters (course_id, number, title) VALUES (?, ?, ?)').run(courseId, ch.number, ch.title);
      const chId = db.prepare('SELECT id FROM chapters WHERE course_id = ? AND number = ?').get(courseId, ch.number).id;
      for (const ls of ch.lessons) {
        db.prepare('INSERT OR IGNORE INTO lessons (chapter_id, number, title, source_note) VALUES (?, ?, ?, ?)')
          .run(chId, ls.number, ls.title, ls.source_note || null);
        const lsId = db.prepare('SELECT id FROM lessons WHERE chapter_id = ? AND number = ?').get(chId, ls.number).id;
        ls.objectives.forEach((o, i) => {
          const r = reviews[o.id] || {};
          const mc = o.memo_coverage || {};
          const res = db.prepare(`INSERT OR IGNORE INTO objectives (lesson_id, code, original_code, number, original_text,
              proposed_text, split_into, revision_reason, revision_type, ai_review_status, thinking_level, knowledge_type,
              concepts, source_page, memo_pages, memo_coverage, memo_note, duplicate_of)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(
            lsId, o.id, o.original_id || null, i + 1, o.text.trim(), r.proposed || null, J.str(r.split_into || []),
            r.revision_reason || null, r.revision_type || null, r.status || null, r.thinking_level || null,
            r.knowledge_type || null, J.str(r.concepts || []), o.src_page, J.str(mc.memo_pdf_pages || []),
            mc.label || null, mc.note || null, o.duplicate_of || null);
          stats.objectives += Number(res.changes);
          const s = sups[o.id];
          if (s) {
            const objId = db.prepare('SELECT id FROM objectives WHERE code = ?').get(o.id).id;
            const rs = db.prepare(`INSERT OR IGNORE INTO supplements (objective_id, memo_basis, supplement, key_points,
                misconceptions, scientific_notes, confidence) VALUES (?, ?, ?, ?, ?, ?, ?)`).run(
              objId, s.memo_basis, s.supplement, J.str(s.key_points), J.str(s.common_misconceptions), s.scientific_notes, s.confidence);
            stats.supplements += Number(rs.changes);
          }
        });
      }
    }

    const qdir = process.env.QUESTIONS_DIR || path.join(root, 'data', 'questions');
    // قرارات الاعتماد الموثقة: تُطبق فقط إذا طابقت بصمة الملف بصمته وقت الاعتماد.
    const approvalsFile = process.env.APPROVALS_FILE || path.join(root, 'data', 'approvals.json');
    const approvals = fs.existsSync(approvalsFile) ? JSON.parse(fs.readFileSync(approvalsFile, 'utf8')) : null;
    for (const f of fs.existsSync(qdir) ? fs.readdirSync(qdir).filter(f => f.endsWith('.json')).sort() : []) {
      const set = JSON.parse(fs.readFileSync(path.join(qdir, f), 'utf8'));
      const obj = db.prepare('SELECT id FROM objectives WHERE code = ?').get(set.objective);
      if (!obj) throw new Error(`هدف غير موجود في ${f}: ${set.objective}`);
      for (const [type, list] of [['mcq', set.mcq || []], ['essay', set.essay || []]]) {
        list.forEach((q, i) => {
          const exists = db.prepare('SELECT 1 FROM questions WHERE objective_id = ? AND type = ? AND number = ?').get(obj.id, type, i + 1);
          if (exists) return;
          db.prepare(`INSERT INTO questions (objective_id, type, number, stem, stimulus, options, correct_index, explanation,
              distractor_notes, model_answer, answer_elements, solution_steps, marks, rubric, common_errors, thinking_level,
              question_kind, difficulty, source_ref, status, origin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'generated', 'ai_generated')`).run(
            obj.id, type, i + 1, q.stem, J.str(q.stimulus || null), J.str(q.options || null), q.correct_index ?? null,
            q.explanation || null, J.str(q.distractor_notes || null), q.model_answer || null, J.str(q.answer_elements || null),
            J.str(q.solution_steps || null), J.str(q.marks || null), J.str(q.rubric || null), J.str(q.common_errors || null),
            q.thinking_level || null, q.question_kind || null, q.difficulty || null, q.source_ref || null);
          stats.questions++;
        });
      }
      const fileHash = crypto.createHash('sha256').update(fs.readFileSync(path.join(qdir, f))).digest('hex');
      if (approvals && approvals.files?.[set.objective] === fileHash) {
        const dec = approvals.decision;
        const pending = db.prepare(`SELECT id FROM questions WHERE objective_id = ? AND status = 'generated' AND origin = 'ai_generated'`).all(obj.id);
        for (const q of pending) {
          db.prepare(`UPDATE questions SET status = 'approved', reviewer_notes = ?, reviewed_at = ? WHERE id = ?`).run(dec.note, dec.date, q.id);
          db.prepare(`INSERT INTO revisions (entity, entity_id, action, before_json, after_json, note) VALUES ('question', ?, 'status', ?, ?, ?)`)
            .run(q.id, J.str({ status: 'generated' }), J.str({ status: 'approved' }), `${dec.by}: ${dec.note}`);
          stats.approved = (stats.approved || 0) + 1;
        }
      }
      // التحقق الآلي لكل أسئلة الهدف بعد إدراجها
      const sib = db.prepare('SELECT id, stem FROM questions WHERE objective_id = ? AND excluded = 0').all(obj.id);
      for (const q of db.prepare('SELECT * FROM questions WHERE objective_id = ?').all(obj.id)) {
        const ac = autoCheck({ ...q, options: J.parse(q.options, []), marks: J.parse(q.marks, []), rubric: J.parse(q.rubric, []) }, sib);
        db.prepare('UPDATE questions SET auto_check = ? WHERE id = ?').run(J.str(ac), q.id);
      }
    }
  });
  log(`أُضيف: ${stats.objectives} هدفًا، ${stats.supplements} محتوى مكمّلًا، ${stats.questions} سؤالًا، واعتُمد ${stats.approved || 0} سؤالًا بقرار موثق`);
  return stats;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) seed();
