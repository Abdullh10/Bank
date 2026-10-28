import express from 'express';
import { getDb, tx, J } from './db.js';
import { login, logout, requireRole } from './auth.js';
import { cleanQuestion, autoCheck, cleanObjectiveEdit, ValidationError, similarPairs } from './validate.js';

export const api = express.Router();
const db = () => getDb();

const isReviewer = req => req.user && ['reviewer', 'admin'].includes(req.user.role);
// الإجابات والحلول تُرسل للمستخدمين المسجلين فقط (المعلمون والمراجعون)؛ الزائر يرى الأسئلة دون حلول.
const canSeeAnswers = req => !!req.user;

function logRevision(entity, entityId, action, before, after, userId, note = null) {
  db().prepare(`INSERT INTO revisions (entity, entity_id, action, before_json, after_json, note, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)`).run(entity, entityId, action, J.str(before), J.str(after), note, userId ?? null);
}

// ---------- الجلسة ----------
api.get('/me', (req, res) => res.json({ user: req.user || null }));
api.post('/login', (req, res) => {
  const u = login(res, req.body?.username, req.body?.password);
  if (!u) return res.status(401).json({ error: 'اسم المستخدم أو كلمة المرور غير صحيحة' });
  res.json({ user: u });
});
api.post('/logout', (req, res) => { logout(req, res); res.json({ ok: true }); });

// ---------- تحويل الصفوف ----------
function objectiveRow(o) {
  return {
    id: o.id, code: o.code, originalCode: o.original_code, number: o.number,
    originalText: o.original_text, proposedText: o.proposed_text, splitInto: J.parse(o.split_into, []),
    approvedText: o.approved_text, revisionReason: o.revision_reason, revisionType: o.revision_type,
    aiReviewStatus: o.ai_review_status, thinkingLevel: o.thinking_level, knowledgeType: o.knowledge_type,
    concepts: J.parse(o.concepts, []), memoPages: J.parse(o.memo_pages, []), memoCoverage: o.memo_coverage,
    memoNote: o.memo_note, duplicateOf: o.duplicate_of, reviewStatus: o.review_status,
    reviewedAt: o.reviewed_at, requiredMcq: o.required_mcq, requiredEssay: o.required_essay,
  };
}

function questionRow(q, withAnswers) {
  const base = {
    id: q.id, objectiveId: q.objective_id, type: q.type, number: q.number, stem: q.stem,
    stimulus: J.parse(q.stimulus), images: J.parse(q.images), options: J.parse(q.options, []), thinkingLevel: q.thinking_level,
    questionKind: q.question_kind, difficulty: q.difficulty, sourceRef: q.source_ref,
    status: q.status, excluded: !!q.excluded, origin: q.origin,
  };
  if (!withAnswers) return base;
  return {
    ...base, correctIndex: q.correct_index, explanation: q.explanation,
    distractorNotes: J.parse(q.distractor_notes, []), modelAnswer: q.model_answer,
    answerElements: J.parse(q.answer_elements, []), solutionSteps: J.parse(q.solution_steps, []),
    marks: J.parse(q.marks, []), rubric: J.parse(q.rubric, []), commonErrors: J.parse(q.common_errors, []),
    autoCheck: J.parse(q.auto_check), reviewerNotes: q.reviewer_notes, reviewedAt: q.reviewed_at,
    updatedAt: q.updated_at,
  };
}

// ---------- المؤشرات (تُحسب من البيانات الفعلية) ----------
api.get('/stats', (_req, res) => {
  const d = db();
  const one = (sql, ...p) => d.prepare(sql).get(...p);
  const objectives = one(`SELECT COUNT(*) n,
      SUM(review_status <> 'pending') reviewed, SUM(review_status = 'approved') approved,
      SUM(review_status = 'returned') returned FROM objectives`);
  const q = one(`SELECT SUM(type='mcq') mcq, SUM(type='essay') essay,
      SUM(status <> 'generated') reviewed, SUM(status = 'approved') approved,
      SUM(status = 'needs_revision') needs_revision, COUNT(*) n FROM questions WHERE excluded = 0`);
  const course = one('SELECT * FROM courses LIMIT 1');
  const levels = d.prepare(`SELECT COALESCE(thinking_level,'غير مصنف') level, COUNT(*) n
      FROM objectives GROUP BY 1 ORDER BY n DESC`).all();
  const coverage = one(`SELECT
      SUM(mcq >= required_mcq AND essay >= required_essay) complete,
      SUM(amcq >= required_mcq AND aessay >= required_essay) approved_complete,
      SUM(mcq + essay > 0) started
    FROM (SELECT o.required_mcq, o.required_essay,
      SUM(q.type='mcq' AND q.excluded=0) mcq, SUM(q.type='essay' AND q.excluded=0) essay,
      SUM(q.type='mcq' AND q.excluded=0 AND q.status='approved') amcq,
      SUM(q.type='essay' AND q.excluded=0 AND q.status='approved') aessay
      FROM objectives o LEFT JOIN questions q ON q.objective_id = o.id GROUP BY o.id)`);
  const byChapter = d.prepare(`SELECT c.number, c.title,
      (SELECT COUNT(*) FROM questions q JOIN objectives o ON o.id=q.objective_id JOIN lessons l ON l.id=o.lesson_id
        WHERE l.chapter_id=c.id AND q.excluded=0) questions
      FROM chapters c ORDER BY c.number`).all();
  res.json({
    course,
    chapters: one('SELECT COUNT(*) n FROM chapters').n,
    lessons: one('SELECT COUNT(*) n FROM lessons').n,
    objectives, questions: q, levels, coverage, byChapter,
    supplements: one(`SELECT COUNT(*) n, SUM(review_status='approved') approved FROM supplements`),
  });
});

// ---------- الفصول والدروس ----------
api.get('/chapters', (_req, res) => {
  res.json(db().prepare(`SELECT c.*,
      (SELECT COUNT(*) FROM lessons l WHERE l.chapter_id=c.id) lessons,
      (SELECT COUNT(*) FROM objectives o JOIN lessons l ON l.id=o.lesson_id WHERE l.chapter_id=c.id) objectives,
      (SELECT SUM(o.review_status='approved') FROM objectives o JOIN lessons l ON l.id=o.lesson_id WHERE l.chapter_id=c.id) approved,
      (SELECT SUM(o.review_status<>'pending') FROM objectives o JOIN lessons l ON l.id=o.lesson_id WHERE l.chapter_id=c.id) reviewed,
      (SELECT COUNT(*) FROM questions q JOIN objectives o ON o.id=q.objective_id JOIN lessons l ON l.id=o.lesson_id
         WHERE l.chapter_id=c.id AND q.excluded=0) questions
    FROM chapters c ORDER BY c.number`).all());
});

api.get('/chapters/:number', (req, res) => {
  const d = db();
  const ch = d.prepare('SELECT * FROM chapters WHERE number = ?').get(Number(req.params.number));
  if (!ch) return res.status(404).json({ error: 'الفصل غير موجود' });
  const lessons = d.prepare('SELECT * FROM lessons WHERE chapter_id = ? ORDER BY number').all(ch.id);
  const objs = d.prepare(`SELECT o.*,
      (SELECT COUNT(*) FROM questions q WHERE q.objective_id=o.id AND q.type='mcq' AND q.excluded=0) mcq,
      (SELECT COUNT(*) FROM questions q WHERE q.objective_id=o.id AND q.type='essay' AND q.excluded=0) essay
    FROM objectives o JOIN lessons l ON l.id=o.lesson_id WHERE l.chapter_id=? ORDER BY o.number`).all(ch.id);
  res.json({
    ...ch,
    lessons: lessons.map(l => ({
      ...l,
      objectives: objs.filter(o => o.lesson_id === l.id).map(o => ({ ...objectiveRow(o), mcq: o.mcq, essay: o.essay })),
    })),
  });
});

// ---------- الهدف ----------
function loadObjective(code) {
  return db().prepare(`SELECT o.*, l.number lesson_number, l.title lesson_title, c.number chapter_number, c.title chapter_title
    FROM objectives o JOIN lessons l ON l.id=o.lesson_id JOIN chapters c ON c.id=l.chapter_id WHERE o.code = ?`).get(code);
}

api.get('/objectives/:code', (req, res) => {
  const o = loadObjective(req.params.code);
  if (!o) return res.status(404).json({ error: 'الهدف غير موجود' });
  const d = db();
  const withAnswers = canSeeAnswers(req);
  const sup = d.prepare('SELECT * FROM supplements WHERE objective_id = ?').get(o.id);
  const qs = d.prepare(`SELECT * FROM questions WHERE objective_id = ? ${isReviewer(req) ? '' : 'AND excluded = 0'}
    ORDER BY type DESC, number`).all(o.id);
  const nav = d.prepare(`SELECT code FROM objectives WHERE lesson_id = ? ORDER BY number`).all(o.lesson_id).map(r => r.code);
  res.json({
    objective: { ...objectiveRow(o), lesson: { number: o.lesson_number, title: o.lesson_title },
      chapter: { number: o.chapter_number, title: o.chapter_title } },
    supplement: sup && {
      memoBasis: sup.memo_basis, supplement: sup.supplement, keyPoints: J.parse(sup.key_points, []),
      misconceptions: J.parse(sup.misconceptions, []), scientificNotes: sup.scientific_notes,
      confidence: sup.confidence, origin: sup.origin, reviewStatus: sup.review_status,
    },
    questions: qs.map(q => questionRow(q, withAnswers)),
    lessonNav: nav,
    answersIncluded: withAnswers,
  });
});

// تدريب فوري: يرجع صحة الإجابة وتفسيرها بعد أن يجيب المستخدم.
api.post('/questions/:id/check', (req, res) => {
  const q = db().prepare('SELECT * FROM questions WHERE id = ? AND type = ? AND excluded = 0').get(Number(req.params.id), 'mcq');
  if (!q) return res.status(404).json({ error: 'السؤال غير موجود' });
  const choice = Number(req.body?.choice);
  if (!(choice >= 0 && choice <= 2)) return res.status(400).json({ error: 'اختيار غير صالح' });
  res.json({ correct: choice === q.correct_index, correctIndex: q.correct_index, explanation: q.explanation,
    distractorNote: J.parse(q.distractor_notes, [])[choice] || null });
});

api.patch('/objectives/:code', requireRole('admin'), (req, res) => {
  const o = loadObjective(req.params.code);
  if (!o) return res.status(404).json({ error: 'الهدف غير موجود' });
  const v = cleanObjectiveEdit(req.body || {});
  const sets = [], vals = [];
  for (const [k, val] of Object.entries(v)) {
    if (val === undefined) continue;
    sets.push(`${k} = ?`); vals.push(k === 'concepts' ? J.str(val) : val);
  }
  if (!sets.length) return res.status(400).json({ error: 'لا توجد تعديلات' });
  tx(d => {
    d.prepare(`UPDATE objectives SET ${sets.join(', ')} WHERE id = ?`).run(...vals, o.id);
    logRevision('objective', o.id, 'edit', objectiveRow(o), v, req.user.id);
  });
  res.json({ ok: true });
});

api.post('/objectives/:code/review', requireRole('reviewer'), (req, res) => {
  const o = loadObjective(req.params.code);
  if (!o) return res.status(404).json({ error: 'الهدف غير موجود' });
  const { action, note } = req.body || {};
  const map = { approve: 'approved', return: 'returned', reset: 'pending' };
  if (!map[action]) return res.status(400).json({ error: 'إجراء غير صالح' });
  if (action === 'return' && !String(note || '').trim()) return res.status(400).json({ error: 'اكتب سبب الإعادة للمراجعة' });
  let approvedText = o.approved_text;
  if (action === 'approve') {
    // المراجع يعتمد الصياغة الحالية فقط؛ تغيير الصياغة لمالك المشروع
    const asked = req.user.role === 'admin' ? req.body.approved_text : null;
    approvedText = String(asked || o.approved_text || o.proposed_text || o.original_text).trim();
    if (approvedText.length < 8) return res.status(400).json({ error: 'الصياغة المعتمدة غير صالحة' });
  }
  tx(d => {
    d.prepare(`UPDATE objectives SET review_status = ?, approved_text = ?, reviewed_by = ?, reviewed_at = datetime('now') WHERE id = ?`)
      .run(map[action], action === 'approve' ? approvedText : o.approved_text, req.user.id, o.id);
    logRevision('objective', o.id, action, { reviewStatus: o.review_status, approvedText: o.approved_text },
      { reviewStatus: map[action], approvedText }, req.user.id, note || null);
  });
  res.json({ ok: true });
});

api.post('/objectives/:code/supplement-review', requireRole('reviewer'), (req, res) => {
  const o = loadObjective(req.params.code);
  const s = o && db().prepare('SELECT * FROM supplements WHERE objective_id = ?').get(o.id);
  if (!s) return res.status(404).json({ error: 'لا يوجد محتوى مكمّل لهذا الهدف' });
  const { action, note, supplement } = req.body || {};
  const map = { approve: 'approved', return: 'returned', reset: 'pending' };
  if (!map[action]) return res.status(400).json({ error: 'إجراء غير صالح' });
  const text = supplement != null ? String(supplement).trim() : s.supplement;
  if (text !== s.supplement && req.user.role !== 'admin') return res.status(403).json({ error: 'تعديل نص المحتوى لمالك المشروع فقط' });
  if (!text) return res.status(400).json({ error: 'نص المحتوى المكمّل فارغ' });
  tx(d => {
    d.prepare('UPDATE supplements SET review_status = ?, supplement = ? WHERE objective_id = ?').run(map[action], text, o.id);
    logRevision('supplement', o.id, action, { reviewStatus: s.review_status, supplement: s.supplement },
      { reviewStatus: map[action], supplement: text }, req.user.id, note || null);
  });
  res.json({ ok: true });
});

// ---------- الأسئلة ----------
function siblingsOf(objectiveId) {
  return db().prepare('SELECT id, stem FROM questions WHERE objective_id = ? AND excluded = 0').all(objectiveId);
}

function saveAutoCheck(id) {
  const q = db().prepare('SELECT * FROM questions WHERE id = ?').get(id);
  const ac = autoCheck({ ...q, options: J.parse(q.options, []), marks: J.parse(q.marks, []), rubric: J.parse(q.rubric, []) },
    siblingsOf(q.objective_id));
  db().prepare('UPDATE questions SET auto_check = ? WHERE id = ?').run(J.str(ac), id);
  return ac;
}

const Q_COLS = ['stem', 'stimulus', 'images', 'options', 'correct_index', 'explanation', 'distractor_notes', 'model_answer',
  'answer_elements', 'solution_steps', 'marks', 'rubric', 'common_errors', 'thinking_level', 'question_kind',
  'difficulty', 'source_ref', 'reviewer_notes'];
const JSON_COLS = new Set(['stimulus', 'images', 'options', 'distractor_notes', 'answer_elements', 'solution_steps', 'marks', 'rubric', 'common_errors']);

api.post('/objectives/:code/questions', requireRole('admin'), (req, res) => {
  const o = loadObjective(req.params.code);
  if (!o) return res.status(404).json({ error: 'الهدف غير موجود' });
  const type = req.body?.type === 'essay' ? 'essay' : 'mcq';
  const v = cleanQuestion(req.body || {}, type);
  const number = (db().prepare('SELECT MAX(number) m FROM questions WHERE objective_id = ? AND type = ?').get(o.id, type).m || 0) + 1;
  const cols = Q_COLS.filter(c => v[c] !== undefined);
  const id = tx(d => {
    const r = d.prepare(`INSERT INTO questions (objective_id, type, number, origin, status, ${cols.join(', ')})
      VALUES (?, ?, ?, 'human', 'in_review', ${cols.map(() => '?').join(', ')})`)
      .run(o.id, type, number, ...cols.map(c => JSON_COLS.has(c) ? J.str(v[c]) : v[c]));
    const qid = Number(r.lastInsertRowid);
    logRevision('question', qid, 'create', null, v, req.user.id);
    return qid;
  });
  res.json({ id, autoCheck: saveAutoCheck(id) });
});

api.get('/questions/:id', requireRole('reviewer'), (req, res) => {
  const q = db().prepare('SELECT * FROM questions WHERE id = ?').get(Number(req.params.id));
  if (!q) return res.status(404).json({ error: 'السؤال غير موجود' });
  res.json(questionRow(q, true));
});

api.patch('/questions/:id', requireRole('admin'), (req, res) => {
  const q = db().prepare('SELECT * FROM questions WHERE id = ?').get(Number(req.params.id));
  if (!q) return res.status(404).json({ error: 'السؤال غير موجود' });
  const v = cleanQuestion(req.body || {}, q.type);
  const cols = Q_COLS.filter(c => v[c] !== undefined);
  tx(d => {
    // أي تعديل بشري ينقل السؤال إلى «قيد المراجعة»: المعتمد لا يبقى معتمدًا بعد تغييره، والمولد لم يعد مسودة آلية خالصة.
    d.prepare(`UPDATE questions SET ${cols.map(c => `${c} = ?`).join(', ')},
      status = CASE WHEN status IN ('approved','generated') THEN 'in_review' ELSE status END, updated_at = datetime('now') WHERE id = ?`)
      .run(...cols.map(c => JSON_COLS.has(c) ? J.str(v[c]) : v[c]), q.id);
    logRevision('question', q.id, 'edit', questionRow(q, true), v, req.user.id);
  });
  res.json({ ok: true, autoCheck: saveAutoCheck(q.id) });
});

api.post('/questions/:id/status', requireRole('reviewer'), (req, res) => {
  const q = db().prepare('SELECT * FROM questions WHERE id = ?').get(Number(req.params.id));
  if (!q) return res.status(404).json({ error: 'السؤال غير موجود' });
  const { status, note } = req.body || {};
  if (!['generated', 'in_review', 'needs_revision', 'approved'].includes(status)) return res.status(400).json({ error: 'حالة غير صالحة' });
  if (status === 'needs_revision' && !String(note || '').trim()) return res.status(400).json({ error: 'اكتب ملاحظة توضح المطلوب تعديله' });
  if (status === 'approved') {
    const ac = J.parse(q.auto_check);
    if (!ac?.passed) return res.status(400).json({ error: 'لا يمكن الاعتماد قبل اجتياز التحقق الآلي؛ عدّل السؤال أولًا' });
  }
  tx(d => {
    d.prepare(`UPDATE questions SET status = ?, reviewer_notes = COALESCE(?, reviewer_notes), reviewed_by = ?, reviewed_at = datetime('now') WHERE id = ?`)
      .run(status, note ? String(note).trim() : null, req.user.id, q.id);
    logRevision('question', q.id, 'status', { status: q.status }, { status }, req.user.id, note || null);
  });
  res.json({ ok: true });
});

api.post('/questions/:id/exclude', requireRole('admin'), (req, res) => {
  const q = db().prepare('SELECT * FROM questions WHERE id = ?').get(Number(req.params.id));
  if (!q) return res.status(404).json({ error: 'السؤال غير موجود' });
  const excluded = req.body?.excluded ? 1 : 0;
  const note = String(req.body?.note || '').trim();
  if (excluded && !note) return res.status(400).json({ error: 'اكتب سبب الاستبعاد' });
  tx(d => {
    d.prepare('UPDATE questions SET excluded = ? WHERE id = ?').run(excluded, q.id);
    logRevision('question', q.id, excluded ? 'exclude' : 'restore', { excluded: q.excluded }, { excluded }, req.user.id, note || null);
  });
  res.json({ ok: true });
});

api.post('/questions/:id/duplicate', requireRole('admin'), (req, res) => {
  const q = db().prepare('SELECT * FROM questions WHERE id = ?').get(Number(req.params.id));
  if (!q) return res.status(404).json({ error: 'السؤال غير موجود' });
  const id = tx(d => {
    const number = d.prepare('SELECT MAX(number) m FROM questions WHERE objective_id = ? AND type = ?').get(q.objective_id, q.type).m + 1;
    const r = d.prepare(`INSERT INTO questions (objective_id, type, number, origin, status, ${Q_COLS.join(', ')})
      SELECT objective_id, type, ?, 'human', 'in_review', ${Q_COLS.join(', ')} FROM questions WHERE id = ?`).run(number, q.id);
    const nid = Number(r.lastInsertRowid);
    logRevision('question', nid, 'duplicate', null, { from: q.id }, req.user.id);
    return nid;
  });
  res.json({ id, autoCheck: saveAutoCheck(id) });
});

api.get('/questions/:id/revisions', requireRole('reviewer'), (req, res) => {
  res.json(db().prepare(`SELECT r.*, u.display_name user FROM revisions r LEFT JOIN users u ON u.id=r.user_id
    WHERE r.entity='question' AND r.entity_id=? ORDER BY r.id DESC`).all(Number(req.params.id))
    .map(r => ({ ...r, before_json: J.parse(r.before_json), after_json: J.parse(r.after_json) })));
});

// ---------- بنك الأسئلة ----------
api.get('/bank', (req, res) => {
  const f = req.query, where = [], p = [];
  const withAnswers = canSeeAnswers(req);
  if (f.chapter) { where.push('c.number = ?'); p.push(Number(f.chapter)); }
  if (f.lesson) { where.push('l.number = ?'); p.push(Number(f.lesson)); }
  if (f.objective) { where.push('o.code = ?'); p.push(String(f.objective)); }
  if (f.type) { where.push('q.type = ?'); p.push(String(f.type)); }
  if (f.level) { where.push('q.thinking_level = ?'); p.push(String(f.level)); }
  if (f.difficulty) { where.push('q.difficulty = ?'); p.push(String(f.difficulty)); }
  if (f.status) { where.push('q.status = ?'); p.push(String(f.status)); }
  if (f.q) { where.push('(q.stem LIKE ? OR q.options LIKE ?)'); p.push(`%${f.q}%`, `%${f.q}%`); }
  if (!(isReviewer(req) && f.excluded === '1')) where.push('q.excluded = 0');
  const rows = db().prepare(`SELECT q.*, o.code objective_code, COALESCE(o.approved_text, o.original_text) objective_text,
      l.number lesson_number, l.title lesson_title, c.number chapter_number, c.title chapter_title
    FROM questions q JOIN objectives o ON o.id=q.objective_id JOIN lessons l ON l.id=o.lesson_id JOIN chapters c ON c.id=l.chapter_id
    ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
    ORDER BY c.number, l.number, o.number, q.type DESC, q.number`).all(...p);
  const out = rows.map(r => ({ ...questionRow(r, withAnswers), objectiveCode: r.objective_code, objectiveText: r.objective_text,
    lesson: { number: r.lesson_number, title: r.lesson_title }, chapter: { number: r.chapter_number, title: r.chapter_title } }));
  // اكتشاف الأسئلة المتشابهة داخل النتائج (للمراجعة).
  if (f.similar === '1') {
    if (out.length > 900) return res.status(400).json({ error: 'اختر فصلًا أو درسًا أولًا: اكتشاف المتشابهة يعمل على 900 سؤال كحد أقصى' });
    return res.json({ questions: out, similar: similarPairs(out) });
  }
  res.json({ questions: out });
});

// ---------- التصدير ----------
const csvCell = v => {
  const s = v == null ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
function sendCsv(res, name, headers, rows) {
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename="${name}"`);
  res.send('﻿' + [headers, ...rows].map(r => r.map(csvCell).join(',')).join('\r\n'));
}

api.get('/export/questions.csv', requireRole('reviewer'), (_req, res) => {
  const rows = db().prepare(`SELECT q.*, o.code oc, c.number cn, l.number ln FROM questions q
    JOIN objectives o ON o.id=q.objective_id JOIN lessons l ON l.id=o.lesson_id JOIN chapters c ON c.id=l.chapter_id
    ORDER BY c.number, l.number, o.number, q.type DESC, q.number`).all();
  const opt = (r, i) => (J.parse(r.options, [])[i] ?? '');
  sendCsv(res, 'questions.csv',
    ['الفصل', 'الدرس', 'الهدف', 'النوع', 'رقم السؤال', 'نص السؤال', 'البديل 1', 'البديل 2', 'البديل 3', 'الإجابة الصحيحة',
      'التفسير', 'الإجابة النموذجية', 'مستوى التفكير', 'نوع السؤال', 'الصعوبة', 'المرجع', 'الحالة', 'مستبعد', 'ملاحظات المراجع'],
    rows.map(r => [r.cn, r.ln, r.oc, r.type === 'mcq' ? 'اختيار من متعدد' : 'مقالي', r.number, r.stem, opt(r, 0), opt(r, 1), opt(r, 2),
      r.type === 'mcq' ? r.correct_index + 1 : '', r.explanation, r.model_answer, r.thinking_level, r.question_kind,
      r.difficulty, r.source_ref, r.status, r.excluded ? 'نعم' : 'لا', r.reviewer_notes]));
});

api.get('/export/objectives.csv', requireRole('reviewer'), (_req, res) => {
  const rows = db().prepare(`SELECT o.*, c.number cn, c.title ct, l.number ln, l.title lt FROM objectives o
    JOIN lessons l ON l.id=o.lesson_id JOIN chapters c ON c.id=l.chapter_id ORDER BY c.number, l.number, o.number`).all();
  sendCsv(res, 'objectives.csv',
    ['رمز الهدف', 'الرمز السابق', 'الفصل', 'الدرس', 'الهدف الأصلي', 'الصياغة المقترحة', 'أهداف مقترحة بالفصل', 'الصياغة المعتمدة', 'سبب التعديل',
      'نوع التعديل', 'حالة المراجعة الآلية', 'مستوى التفكير', 'نوع المعرفة', 'المفاهيم', 'صفحات المذكرة', 'تغطية المذكرة', 'حالة الاعتماد'],
    rows.map(r => [r.code, r.original_code, `${r.cn} ${r.ct}`, `${r.ln} ${r.lt}`, r.original_text, r.proposed_text,
      J.parse(r.split_into, []).join(' | '), r.approved_text, r.revision_reason, r.revision_type, r.ai_review_status,
      r.thinking_level, r.knowledge_type, J.parse(r.concepts, []).join('، '), J.parse(r.memo_pages, []).join('، '),
      r.memo_coverage, r.review_status]));
});

// ---------- سجل التعديلات ----------
api.get('/revisions', requireRole('reviewer'), (req, res) => {
  res.json(db().prepare(`SELECT r.id, r.entity, r.entity_id, r.action, r.note, r.at, u.display_name user
    FROM revisions r LEFT JOIN users u ON u.id=r.user_id ORDER BY r.id DESC LIMIT ?`).all(Math.min(500, Number(req.query.limit) || 100)));
});

// معالجة الأخطاء بوضوح
api.use((err, _req, res, _next) => {
  if (err instanceof ValidationError) return res.status(400).json({ error: err.message, errors: err.errors });
  console.error(err);
  res.status(500).json({ error: 'حدث خطأ غير متوقع في الخادم' });
});
