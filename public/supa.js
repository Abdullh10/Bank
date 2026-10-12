// طبقة الربط مع Supabase: تحوّل مسارات الواجهة البرمجية التي تستخدمها الصفحات إلى استدعاءات دوال قاعدة البيانات،
// فتبقى الصفحات كما هي سواء عملت على الخادم المحلي أو على Supabase.
// كل الكتابة تمر عبر دوال محمية في قاعدة البيانات تتحقق من الدور وتسجل التعديل؛ التحقق هنا لتوضيح الأخطاء مبكرًا فقط.
import { cleanQuestion, cleanObjectiveEdit, autoCheck, similarPairs, ValidationError } from './validate.js';

const SDK = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/+esm';
let client;
let signedOutHandler = null;
export const onSignedOut = fn => { signedOutHandler = fn; };
let loginDomain = '';

export async function initSupabase(cfg) {
  const { createClient } = await import(SDK);
  loginDomain = cfg.loginDomain || '';
  client = createClient(cfg.url, cfg.key, { auth: { persistSession: true, autoRefreshToken: true } });
  // انتهاء الجلسة أو إلغاؤها (مثل فشل تجديد التوكن): تُبلَّغ الواجهة لتعود إلى صفحة الدخول
  client.auth.onAuthStateChange?.(event => { if (event === 'SIGNED_OUT') signedOutHandler?.(); });
  return client;
}

async function rpc(fn, args = {}) {
  const { data, error } = await client.rpc(fn, args);
  if (error) {
    const msg = error.message || 'تعذر تنفيذ الطلب';
    const status = error.code === '28000' || error.code === 'PGRST301' || /JWT expired|invalid JWT/i.test(msg) ? 401 : error.code === '42501' ? 403 : error.code === 'P0002' ? 404 : 400;
    throw Object.assign(new Error(msg), { errors: error.code === '22023' ? msg.split('؛ ') : undefined, status });
  }
  return data;
}

const clean = (fn, ...a) => {
  try { return fn(...a); } catch (e) {
    if (e instanceof ValidationError) throw Object.assign(new Error(e.message), { errors: e.errors, status: 400 });
    throw e;
  }
};

// التحقق الآلي يُحسب بنفس قواعد الخادم المحلي، مع مقارنة نص السؤال بأسئلة الهدف نفسه.
async function computeAutoCheck(q, objectiveCode) {
  const o = await rpc('get_objective', { p_code: objectiveCode });
  return autoCheck(q, o.questions.filter(s => !s.excluded).map(s => ({ id: s.id, stem: s.stem })));
}
async function objectiveCodeOf(questionId) {
  const { data, error } = await client.from('questions').select('objective_id, objectives(code)').eq('id', questionId).single();
  if (error || !data) throw Object.assign(new Error('السؤال غير موجود'), { status: 404 });
  return data.objectives.code;
}

function download(name, rows) {
  const cell = v => {
    const s = v == null ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const blob = new Blob(['﻿' + rows.map(r => r.map(cell).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: name });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

export async function exportCsv(kind) {
  if (kind === 'questions') {
    const rows = await rpc('get_bank', { f: { excluded: '1' } });
    download('questions.csv', [
      ['الفصل', 'الدرس', 'الهدف', 'النوع', 'رقم السؤال', 'نص السؤال', 'البديل 1', 'البديل 2', 'البديل 3', 'الإجابة الصحيحة',
        'التفسير', 'الإجابة النموذجية', 'مستوى التفكير', 'نوع السؤال', 'الصعوبة', 'المرجع', 'الحالة', 'مستبعد', 'ملاحظات المراجع'],
      ...rows.map(r => [r.chapter.number, r.lesson.number, r.objectiveCode, r.type === 'mcq' ? 'اختيار من متعدد' : 'مقالي', r.number, r.stem,
        r.options[0] ?? '', r.options[1] ?? '', r.options[2] ?? '', r.type === 'mcq' ? r.correctIndex + 1 : '', r.explanation, r.modelAnswer,
        r.thinkingLevel, r.questionKind, r.difficulty, r.sourceRef, r.status, r.excluded ? 'نعم' : 'لا', r.reviewerNotes])]);
  } else {
    const chapters = await rpc('get_chapters');
    const all = [];
    for (const c of chapters) {
      const ch = await rpc('get_chapter', { p_number: c.number });
      for (const l of ch.lessons) for (const o of l.objectives) all.push([o.code, o.originalCode, `${ch.number} ${ch.title}`, `${l.number} ${l.title}`,
        o.originalText, o.proposedText, (o.splitInto || []).join(' | '), o.approvedText, o.revisionReason, o.revisionType, o.aiReviewStatus,
        o.thinkingLevel, o.knowledgeType, (o.concepts || []).join('، '), (o.memoPages || []).join('، '), o.memoCoverage, o.reviewStatus]);
    }
    download('objectives.csv', [['رمز الهدف', 'الرمز السابق', 'الفصل', 'الدرس', 'الهدف الأصلي', 'الصياغة المقترحة', 'أهداف مقترحة بالفصل',
      'الصياغة المعتمدة', 'سبب التعديل', 'نوع التعديل', 'حالة المراجعة الآلية', 'مستوى التفكير', 'نوع المعرفة', 'المفاهيم', 'صفحات المذكرة',
      'تغطية المذكرة', 'حالة الاعتماد'], ...all]);
  }
}

// إنشاء الحسابات وإعادة تعيين كلمات المرور عبر دالة الحافة admin-users (تعمل داخل Supabase بمفتاح الخدمة).
async function adminUsers(body) {
  // إنشاء الحسابات على دفعات صغيرة: طلب واحد ضخم قد يتجاوز مهلة الدالة ويضيع كلمات المرور
  if (body.action === 'create' && body.students.length > 25) {
    const results = [];
    for (let i = 0; i < body.students.length; i += 25)
      results.push(...(await adminUsers({ action: 'create', students: body.students.slice(i, i + 25) })).results);
    return { results };
  }
  const { data, error } = await client.functions.invoke('admin-users', { body });
  if (!error) return data;
  let msg = error.message || '', status = error.context?.status;
  try { const j = await error.context?.json?.(); if (j?.error) msg = j.error; } catch { /* ليس JSON */ }
  if (status === 404 && !/[\u0600-\u06FF]/.test(msg))
    msg = 'دالة إنشاء الحسابات (admin-users) غير منشورة في Supabase بعد؛ راجع خطوات النشر في docs/supabase-setup.md';
  else if (/Failed to send|FunctionsFetchError|NetworkError|Load failed/i.test(msg))
    msg = 'تعذر الاتصال بدالة إنشاء الحسابات؛ تحقق من الإنترنت ثم أعد المحاولة (راجع القائمة أولًا: قد يكون بعض الحسابات أُنشئ)';
  throw Object.assign(new Error(msg), { status: status === 401 ? 401 : 400 });
}

export async function supaApi(path, { method = 'GET', body = {} } = {}) {
  const [p, query = ''] = path.split('?');
  const f = Object.fromEntries([...new URLSearchParams(query)].filter(([, v]) => v !== ''));
  let m;

  if (p === '/me') return { user: await rpc('get_me') };
  if (p === '/login') {
    // المعرّف بلا @ يُكمَّل بالنطاق الشكلي؛ ويبقى الدخول بالبريد الكامل ممكنًا.
    const id = String(body.username || '').trim().toLowerCase();
    const email = id.includes('@') || !loginDomain ? id : `${id}@${loginDomain}`;
    const { error } = await client.auth.signInWithPassword({ email, password: body.password || '' });
    if (error) throw Object.assign(new Error('اسم المستخدم أو كلمة المرور غير صحيحة'), { status: 401 });
    const user = await rpc('get_me');
    if (!user) throw new Error('الحساب غير مرتبط بملف مستخدم؛ تواصل مع المشرف');
    return { user };
  }
  if (p === '/logout') { await client.auth.signOut({ scope: 'local' }); return { ok: true }; } // الخروج من هذا الجهاز فقط
  if (p === '/stats') return rpc('get_stats');
  if (p === '/chapters') return rpc('get_chapters');
  if ((m = p.match(/^\/chapters\/(\d+)$/))) return rpc('get_chapter', { p_number: Number(m[1]) });

  if ((m = p.match(/^\/objectives\/([^/]+)$/))) {
    const code = decodeURIComponent(m[1]);
    if (method === 'GET') return rpc('get_objective', { p_code: code });
    await rpc('patch_objective', { p_code: code, p: clean(cleanObjectiveEdit, body) });
    return { ok: true };
  }
  if ((m = p.match(/^\/objectives\/([^/]+)\/review$/))) {
    await rpc('review_objective', { p_code: decodeURIComponent(m[1]), p_action: body.action, p_approved_text: body.approved_text ?? null, p_note: body.note ?? null });
    return { ok: true };
  }
  if ((m = p.match(/^\/objectives\/([^/]+)\/supplement-review$/))) {
    await rpc('review_supplement', { p_code: decodeURIComponent(m[1]), p_action: body.action, p_supplement: body.supplement ?? null, p_note: body.note ?? null });
    return { ok: true };
  }
  if ((m = p.match(/^\/objectives\/([^/]+)\/questions$/))) {
    const code = decodeURIComponent(m[1]);
    const type = body.type === 'essay' ? 'essay' : 'mcq';
    const q = clean(cleanQuestion, body, type);
    const id = await rpc('create_question', { p_code: code, p_type: type, p: q, p_auto_check: null });
    const ac = await computeAutoCheck({ ...q, id, type }, code);
    await rpc('set_auto_check', { p_id: id, p_auto_check: ac });
    return { id, autoCheck: ac };
  }

  if ((m = p.match(/^\/questions\/(\d+)\/check$/))) return rpc('check_answer', { p_question: Number(m[1]), p_choice: Number(body.choice) });
  if ((m = p.match(/^\/questions\/(\d+)\/status$/))) {
    await rpc('set_question_status', { p_id: Number(m[1]), p_status: body.status, p_note: body.note ?? null });
    return { ok: true };
  }
  if ((m = p.match(/^\/questions\/(\d+)\/exclude$/))) {
    await rpc('exclude_question', { p_id: Number(m[1]), p_excluded: !!body.excluded, p_note: body.note ?? null });
    return { ok: true };
  }
  if ((m = p.match(/^\/questions\/(\d+)\/duplicate$/))) {
    const id = await rpc('duplicate_question', { p_id: Number(m[1]), p_auto_check: null });
    const q = await rpc('get_question', { p_id: id });
    const code = await objectiveCodeOf(id);
    const ac = await computeAutoCheck({ ...q, correct_index: q.correctIndex, model_answer: q.modelAnswer }, code);
    await rpc('set_auto_check', { p_id: id, p_auto_check: ac });
    return { id, autoCheck: ac };
  }
  if ((m = p.match(/^\/questions\/(\d+)\/revisions$/))) return rpc('get_revisions', { p_limit: 500, p_question: Number(m[1]) });
  if ((m = p.match(/^\/questions\/(\d+)$/))) {
    const id = Number(m[1]);
    if (method === 'GET') return rpc('get_question', { p_id: id });
    const cur = await rpc('get_question', { p_id: id });
    const q = clean(cleanQuestion, body, cur.type);
    const ac = await computeAutoCheck({ ...q, id, type: cur.type }, await objectiveCodeOf(id));
    await rpc('update_question', { p_id: id, p: q, p_auto_check: ac });
    return { ok: true, autoCheck: ac };
  }

  if (p === '/bank') {
    const questions = await rpc('get_bank', { f });
    if (f.similar === '1') {
      if (questions.length > 900) throw Object.assign(new Error('اختر فصلًا أو درسًا أولًا: اكتشاف المتشابهة يعمل على 900 سؤال كحد أقصى'), { status: 400 });
      return { questions, similar: similarPairs(questions) };
    }
    return { questions };
  }
  if (p === '/revisions') return rpc('get_revisions', { p_limit: Number(f.limit) || 100 });
  // ---------- الطالب ----------
  if (p === '/student/catalog') return rpc('student_catalog');
  if (p === '/student/confirm') { await rpc('student_confirm_profile', { p_name: body.name, p_section: body.section }); return { ok: true }; }
  if (p === '/student/start') return rpc('student_start', { p: body });
  if (p === '/student/answer') return rpc('student_answer', { p_session: body.session, p_question: body.question, p_choice: body.choice });
  if (p === '/student/finish') return rpc('student_finish', { p_session: body.session });
  if (p === '/student/history') return rpc('student_history');
  // ---------- المعلم والمشرف ----------
  if (p === '/teacher/progress') return rpc('teacher_progress', { p_section: f.section || null });
  if (p === '/admin/students') return rpc('admin_list_students');
  if (p === '/admin/students/update') {
    await rpc('admin_update_student', { p_id: body.id, p_name: body.name, p_section: body.section, p_role: body.role, p_grade: body.grade ?? null });
    return { ok: true };
  }
  if (p === '/admin/students/create') return adminUsers({ action: 'create', students: body.students });
  if (p === '/admin/students/reset') return adminUsers({ action: 'reset', userId: body.userId, password: body.password || '' });
  if (p === '/admin/students/rename') return adminUsers({ action: 'rename', userId: body.userId, username: body.username });
  if (p === '/admin/students/delete') return adminUsers({ action: 'delete', userId: body.userId });
  if (p === '/admin/students/delete-many') return adminUsers({ action: 'deleteMany', userIds: body.userIds });
  throw new Error('مسار غير معروف: ' + p);
}
