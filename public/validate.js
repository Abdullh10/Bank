// التحقق من البيانات قبل الحفظ + التحقق الآلي من بنية الأسئلة.
// التحقق الآلي لا يعني اعتمادًا علميًا: الاعتماد قرار بشري يُسجل في status.

const DIFFICULTY = ['سهل', 'متوسط', 'صعب'];
const LEVELS = ['تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع'];

const norm = s => String(s ?? '').replace(/\s+/g, ' ').trim();

export class ValidationError extends Error {
  constructor(errors) { super(errors.join('؛ ')); this.errors = errors; this.status = 400; }
}

// يتحقق من حقول السؤال المرسلة من الواجهة ويرجع كائنًا نظيفًا.
export function cleanQuestion(input, type) {
  const e = [];
  const q = {
    stem: norm(input.stem),
    thinking_level: input.thinking_level || null,
    question_kind: norm(input.question_kind) || null,
    difficulty: input.difficulty || null,
    source_ref: norm(input.source_ref) || null,
    reviewer_notes: input.reviewer_notes != null ? String(input.reviewer_notes).trim() : undefined,
    stimulus: input.stimulus ?? null,
  };
  if (q.stem.length < 8) e.push('نص السؤال قصير جدًا');
  if (q.difficulty && !DIFFICULTY.includes(q.difficulty)) e.push('درجة الصعوبة غير صالحة');
  if (q.thinking_level && !LEVELS.includes(q.thinking_level)) e.push('مستوى التفكير غير صالح');
  if (q.stimulus) {
    const s = q.stimulus;
    if (!Array.isArray(s.headers) || !Array.isArray(s.rows)) e.push('جدول البيانات غير صالح');
  }
  if (type === 'mcq') {
    q.options = Array.isArray(input.options) ? input.options.map(norm) : [];
    q.correct_index = Number(input.correct_index);
    q.explanation = norm(input.explanation);
    q.distractor_notes = Array.isArray(input.distractor_notes) ? input.distractor_notes.map(norm) : [];
    // ثلاثة بدائل (أ ب ج) أو أربعة (أ ب ج د)، حسب المقرر
    if (q.options.length !== 3 && q.options.length !== 4) e.push('يجب أن يكون لسؤال الاختيار ثلاثة بدائل أو أربعة');
    if (q.options.some(o => !o)) e.push('لا يجوز ترك بديل فارغ');
    if (!(q.correct_index >= 0 && q.correct_index < q.options.length)) e.push('حدد الإجابة الصحيحة');
    if (q.distractor_notes.length > q.options.length) q.distractor_notes = q.distractor_notes.slice(0, q.options.length);
    if (!q.explanation) e.push('تفسير الإجابة الصحيحة مطلوب');
  } else {
    q.model_answer = String(input.model_answer ?? '').trim();
    for (const k of ['answer_elements', 'solution_steps', 'marks', 'rubric', 'common_errors'])
      q[k] = Array.isArray(input[k]) ? input[k] : [];
    if (!q.model_answer) e.push('الإجابة النموذجية مطلوبة');
    if (!q.marks.length) e.push('توزيع الدرجات مطلوب');
    if (!q.rubric.length) e.push('سلم التصحيح مطلوب');
  }
  if (e.length) throw new ValidationError(e);
  return q;
}

// فحوص آلية بنيوية/لغوية — تُعرض للمراجع كتنبيهات، ولا تُغني عن المراجعة البشرية.
export function autoCheck(q, siblings = []) {
  const checks = [];
  const add = (ok, label) => checks.push({ ok, label });
  if (q.type === 'mcq') {
    const opts = q.options || [];
    add(opts.length === 3 || opts.length === 4, 'ثلاثة بدائل أو أربعة');
    add(new Set(opts.map(norm)).size === opts.length, 'البدائل غير مكررة');
    add(q.correct_index >= 0 && q.correct_index < opts.length, 'إجابة صحيحة واحدة محددة');
    const lens = opts.map(o => norm(o).length).filter(Boolean);
    const ratio = lens.length ? Math.max(...lens) / Math.max(1, Math.min(...lens)) : 99;
    add(ratio <= 2.5, 'أطوال البدائل متقاربة');
    add(!opts.some(o => /جميع ما (سبق|ذكر)|لا شيء مما|كل ما سبق/.test(o)), 'لا توجد بدائل من نوع «جميع ما سبق»');
    add(!!norm(q.explanation), 'تفسير الإجابة موجود');
  } else {
    add(!!String(q.model_answer || '').trim(), 'إجابة نموذجية موجودة');
    const total = (q.marks || []).reduce((s, m) => s + Number(m.marks || 0), 0);
    add(total > 0, `توزيع الدرجات (${total} درجة)`);
    add((q.rubric || []).length >= 2, 'سلم تصحيح بمستويين على الأقل');
  }
  // تكرار غير مبرر: تشابه نص السؤال مع أسئلة الهدف نفسه.
  const sim = siblings.filter(s => s.id !== q.id).map(s => similarity(q.stem, s.stem));
  const maxSim = sim.length ? Math.max(...sim) : 0;
  add(maxSim < 0.75, `لا يوجد تشابه مرتفع مع أسئلة الهدف (${Math.round(maxSim * 100)}%)`);
  return { passed: checks.every(c => c.ok), checks, at: new Date().toISOString() };
}

// تشابه جاكارد على مستوى الكلمات (بعد إزالة التشكيل وأدوات شائعة).
const STOP = new Set(['في', 'من', 'على', 'إلى', 'الى', 'عن', 'ما', 'هو', 'هي', 'أي', 'التالي', 'التالية', 'ان', 'أن']);
export function tokens(s) {
  return new Set(norm(s).replace(/[ً-ْ]/g, '').replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .split(' ').filter(w => w.length > 1 && !STOP.has(w)));
}
// أزواج الأسئلة المتشابهة: تُقطَّع كل جملة مرة واحدة ثم تُقارن المجموعات (أسرع بكثير من similarity لكل زوج).
export function similarPairs(items, threshold = 0.5) {
  const toks = items.map(q => tokens(q.stem));
  const out = [];
  for (let i = 0; i < items.length; i++) {
    const A = toks[i]; if (!A.size) continue;
    for (let j = i + 1; j < items.length; j++) {
      const B = toks[j]; if (!B.size) continue;
      // الحد الأعلى الممكن للتشابه = الأصغر/الأكبر؛ يُتجاوز الزوج إن كان دون العتبة
      if (Math.min(A.size, B.size) / Math.max(A.size, B.size) < threshold) continue;
      let inter = 0; for (const w of A) if (B.has(w)) inter++;
      const sc = inter / (A.size + B.size - inter);
      if (sc >= threshold) out.push({ a: items[i].id, b: items[j].id, score: Math.round(sc * 100) });
    }
  }
  return out;
}
export function similarity(a, b) {
  const A = tokens(a), B = tokens(b);
  if (!A.size || !B.size) return 0;
  let inter = 0;
  for (const w of A) if (B.has(w)) inter++;
  return inter / (A.size + B.size - inter);
}

export function cleanObjectiveEdit(input) {
  const e = [];
  const o = {
    approved_text: input.approved_text != null ? norm(input.approved_text) : undefined,
    thinking_level: input.thinking_level,
    knowledge_type: input.knowledge_type,
    concepts: Array.isArray(input.concepts) ? input.concepts.map(norm).filter(Boolean) : undefined,
    required_mcq: input.required_mcq != null ? Number(input.required_mcq) : undefined,
    required_essay: input.required_essay != null ? Number(input.required_essay) : undefined,
  };
  if (o.approved_text !== undefined && o.approved_text.length < 8) e.push('صياغة الهدف قصيرة جدًا');
  if (o.thinking_level && !LEVELS.includes(o.thinking_level)) e.push('مستوى التفكير غير صالح');
  for (const k of ['required_mcq', 'required_essay'])
    if (o[k] !== undefined && !(Number.isInteger(o[k]) && o[k] >= 0 && o[k] <= 30)) e.push('العدد المطلوب من الأسئلة غير صالح');
  if (e.length) throw new ValidationError(e);
  return o;
}
