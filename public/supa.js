// طبقة الربط مع Supabase: تحوّل مسارات الواجهة البرمجية التي تستخدمها الصفحات إلى استدعاءات دوال قاعدة البيانات،
// فتبقى الصفحات كما هي سواء عملت على الخادم المحلي أو على Supabase.
// كل الكتابة تمر عبر دوال محمية في قاعدة البيانات تتحقق من الدور وتسجل التعديل؛ التحقق هنا لتوضيح الأخطاء مبكرًا فقط.
import { cleanQuestion, cleanObjectiveEdit, autoCheck, similarPairs, ValidationError } from './validate.js';

const SDK = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/+esm';
let client;
let signedOutHandler = null;
export const onSignedOut = fn => { signedOutHandler = fn; };
let loginDomain = '';
// المقرر المختار: تُمرَّر قيمته لكل دوال القراءة الخاصة بمقرر (null = المقرر الافتراضي في قاعدة البيانات)
let course = null;
export const setCourse = id => { course = id ?? null; };

export async function initSupabase(cfg) {
  const { createClient } = await import(SDK);
  loginDomain = cfg.loginDomain || '';
  client = createClient(cfg.url, cfg.key, { auth: { persistSession: true, autoRefreshToken: true } });
  // انتهاء الجلسة أو إلغاؤها (مثل فشل تجديد التوكن): تُبلَّغ الواجهة لتعود إلى صفحة الدخول
  client.auth.onAuthStateChange?.(event => { if (event === 'SIGNED_OUT') signedOutHandler?.(); });
  return client;
}

const sleep = ms => new Promise(r => setTimeout(r, ms));
const BUSY = 'المنصة مشغولة الآن بكثرة المستخدمين؛ حاول بعد لحظات (لم يُسجَّل خروجك)';
// أخطاء مؤقتة (ازدحام أو انقطاع شبكة أو تجاوز مهلة): لا تُعدّ انتهاء جلسة فلا يُخرَج الطالب بسببها
const isTransient = e => ['57014', '53300', '53400', '08006', '08001', '08000'].includes(e?.code) || [0, 408, 429, 500, 502, 503, 504, 520, 522, 524].includes(e?.status)
  || /Failed to fetch|NetworkError|Load failed|network|timeout|timed out|rate limit|statement timeout/i.test(e?.message || '');
const isJwtExpired = e => e?.code === 'PGRST301' || /JWT expired|invalid JWT/i.test(e?.message || '');
let refreshing = null;
// تجديد واحد مشترك بين الطلبات المتزامنة (لا يُرسل كل طلب تجديدًا مستقلًا)
const refreshOnce = () => (refreshing ||= Promise.resolve(client.auth.refreshSession?.() ?? { error: null, data: { session: true } })
  .catch(error => ({ error })).finally(() => { refreshing = null; }));

async function rpc(fn, args = {}, retried = false) {
  const { data, error } = await client.rpc(fn, args);
  if (error && !retried && isJwtExpired(error)) {
    // انتهى التوكن (مثل تبويب بقي في الخلفية): نجدده ونعيد الطلب مرة واحدة بدل إخراج الطالب
    const r = await refreshOnce();
    if (!r.error) return rpc(fn, args, true);
    throw Object.assign(new Error(isTransient(r.error) ? BUSY : 'انتهت الجلسة؛ سجّل الدخول مرة أخرى'), { status: isTransient(r.error) ? 503 : 401 });
  }
  if (error && isTransient(error)) throw Object.assign(new Error(BUSY), { status: 503 });
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
    const rows = await rpc('get_bank', { f: { excluded: '1', course } });
    download('questions.csv', [
      ['الفصل', 'الدرس', 'الهدف', 'النوع', 'رقم السؤال', 'نص السؤال', 'البديل 1', 'البديل 2', 'البديل 3', 'البديل 4', 'الإجابة الصحيحة',
        'التفسير', 'الإجابة النموذجية', 'مستوى التفكير', 'نوع السؤال', 'الصعوبة', 'المرجع', 'الحالة', 'مستبعد', 'ملاحظات المراجع'],
      ...rows.map(r => [r.chapter.number, r.lesson.number, r.objectiveCode, r.type === 'mcq' ? 'اختيار من متعدد' : 'مقالي', r.number, r.stem,
        r.options[0] ?? '', r.options[1] ?? '', r.options[2] ?? '', r.options[3] ?? '', r.type === 'mcq' ? r.correctIndex + 1 : '', r.explanation, r.modelAnswer,
        r.thinkingLevel, r.questionKind, r.difficulty, r.sourceRef, r.status, r.excluded ? 'نعم' : 'لا', r.reviewerNotes])]);
  } else {
    const chapters = await rpc('get_chapters', { p_course: course });
    const all = [];
    for (const c of chapters) {
      const ch = await rpc('get_chapter', { p_number: c.number, p_course: course });
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
    // دخول عدد كبير من الطلاب معًا (من شبكة واحدة) قد يبلغ حد الدخول في Supabase: نعيد المحاولة بتأخير عشوائي
    // ونفرّق بين «ازدحام» و«بيانات خاطئة» حتى لا يظن الطالب أن كلمته خطأ
    let error = null;
    for (let i = 0; i < 4; i++) {
      ({ error } = await client.auth.signInWithPassword({ email, password: body.password || '' }));
      if (!error || !isTransient(error)) break;
      await sleep(1500 * (i + 1) + Math.random() * 2000);
    }
    if (error && isTransient(error)) throw Object.assign(new Error('المنصة مشغولة بكثرة الدخول الآن؛ انتظر دقيقة ثم أعد المحاولة'), { status: 503 });
    if (error) throw Object.assign(new Error('اسم المستخدم أو كلمة المرور غير صحيحة'), { status: 401 });
    const user = await rpc('get_me');
    if (!user) throw new Error('الحساب غير مرتبط بملف مستخدم؛ تواصل مع المشرف');
    return { user };
  }
  if (p === '/logout') { await client.auth.signOut({ scope: 'local' }); return { ok: true }; } // الخروج من هذا الجهاز فقط
  if (p === '/courses') return rpc('get_courses');
  if (p === '/stats') return rpc('get_stats', { p_course: course });
  if (p === '/chapters') return rpc('get_chapters', { p_course: course });
  if ((m = p.match(/^\/chapters\/(\d+)$/))) return rpc('get_chapter', { p_number: Number(m[1]), p_course: course });

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
    const questions = await rpc('get_bank', { f: { ...f, course } });
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
  if (p === '/student/rank') return rpc('student_leaderboard', { p_course: f.course ? Number(f.course) : null });
  if (p === '/student/report') { await rpc('student_report_question', { p_question: body.question, p_reason: body.reason, p_body: body.body ?? null }); return { ok: true }; }
  if (p === '/student/coupon') return rpc('student_redeem_coupon', { p_code: body.code, p_course: body.course ? Number(body.course) : null });
  if (p === '/student/inbox') return rpc('student_inbox');
  if (p === '/student/comms/summary') return rpc('student_comm_summary');
  if (p === '/student/comms/read') { await rpc('student_comms_mark_read'); return { ok: true }; }
  if (p === '/student/comms/reply') { await rpc('student_comm_reply', { p_id: body.id, p_code: body.code }); return { ok: true }; }
  if (p === '/student/balance') return rpc('student_balance', { p_course: f.course ? Number(f.course) : null });
  if (p === '/student/redeem') return rpc('student_redeem', { p_grades: Number(body.grades) || 1, p_course: body.course ? Number(body.course) : null });
  // ---------- المعلم والمشرف ----------
  if (p === '/staff/comms') return method === 'GET' ? rpc('staff_list_comms', { p_course: course }) : rpc('staff_send_comm', { p: { ...body, course } });
  if (p === '/staff/comms/detail') return rpc('staff_comm_detail', { p_id: Number(f.id) });
  if (p === '/staff/comms/cancel') { await rpc('staff_cancel_comm', { p_id: body.id }); return { ok: true }; }
  if (p === '/staff/lessons') return rpc('staff_course_lessons', { p_course: course });
  if (p === '/staff/students') return rpc('staff_my_students', { p_course: course });
  if (p === '/admin/comms/settings') return method === 'GET' ? rpc('admin_get_comm_settings') : rpc('admin_set_comm_settings', { p_daily: Number(body.daily), p_active: Number(body.activeTasks), p_max: Number(body.maxRecipients) });
  if (p === '/staff/coupons') return method === 'GET' ? rpc('staff_list_coupons') : rpc('staff_create_coupon', { p_points: Number(body.points), p_note: body.note, p_days: Number(body.days) || 7 });
  if (p === '/staff/coupons/cancel') { await rpc('staff_cancel_coupon', { p_id: body.id }); return { ok: true }; }
  if (p === '/teacher/grades') return rpc('teacher_grade_balances', { p_course: course });
  if (p === '/teacher/grades/record-many') return rpc('teacher_record_grades_many', { p_users: body.users || [], p_course: course });
  if (p === '/teacher/grades/record') return rpc('teacher_record_grades', { p_user: body.user || null, p_course: course });
  if (p === '/teacher/grades/cancel') { await rpc('teacher_cancel_redemption', { p_id: body.id, p_reason: body.reason }); return { ok: true }; }
  if (p === '/admin/grades/settings') return method === 'GET' ? rpc('admin_get_grade_settings')
    : rpc('admin_set_grade_settings', { p_rate: Number(body.rate), p_weekly: Number(body.weekly), p_enabled: !!body.enabled, p_reason: body.reason ?? null,
      p_coupon_max: body.couponMax ? Number(body.couponMax) : null, p_coupon_quota: body.couponQuota !== undefined && body.couponQuota !== '' ? Number(body.couponQuota) : null });
  if (p === '/teacher/progress') return rpc('teacher_progress', { p_section: f.section || null, p_course: course });
  if (p === '/teacher/quality') return rpc('teacher_training_quality', { p_course: course });
  if (p === '/admin/rank/term') return method === 'GET' ? rpc('admin_get_rank_term') : rpc('admin_start_new_term', { p_note: body.note ?? null });
  if (p === '/admin/students') return rpc('admin_list_students');
  if (p === '/admin/students/update') {
    await rpc('admin_update_student', { p_id: body.id, p_name: body.name, p_section: body.section, p_role: body.role, p_grade: body.grade ?? null });
    return { ok: true };
  }
  if (p === '/admin/students/create') return adminUsers({ action: 'create', students: body.students });
  if (p === '/admin/students/reset') return adminUsers({ action: 'reset', userId: body.userId, password: body.password || '' });
  if (p === '/admin/students/rename') return adminUsers({ action: 'rename', userId: body.userId, username: body.username });
  if (p === '/admin/students/delete') return adminUsers({ action: 'delete', userId: body.userId });
  if (p === '/admin/students/enroll') return { n: await rpc('admin_enroll', { p_ids: body.ids, p_course: body.course, p_mode: body.mode || 'add' }) };
  if (p === '/admin/students/enroll-usernames') return { n: await rpc('admin_enroll_usernames', { p_usernames: body.usernames, p_course: body.course }) };
  if (p === '/admin/students/delete-many') return adminUsers({ action: 'deleteMany', userIds: body.userIds });
  // ---------- حسابات الفريق ----------
  if (p === '/admin/team') return rpc('admin_list_staff');
  if (p === '/admin/team/create') return adminUsers({ action: 'create', role: body.role, students: [{ name: body.name, username: body.username, password: body.password || '' }] });
  if (p === '/admin/team/teacher') {
    if (method === 'GET') return rpc('admin_get_teacher', { p_id: f.id });
    return rpc('admin_set_teacher', { p_id: body.id, p_courses: body.courses || [], p_students: body.students || [] });
  }
  if (p === '/admin/team/update') { await rpc('admin_update_staff', { p_id: body.id, p_name: body.name, p_role: body.role }); return { ok: true }; }
  // ---------- الملاحظات ولوحة المؤشرات ----------
  if (p === '/dashboard') return rpc('get_dashboard', { p_course: course });
  if (p === '/exam/answers') return rpc('get_exam_answers', { p_ids: body.ids });
  if (p === '/notes') {
    if (method === 'GET') return rpc('get_notes', { p_code: f.code || null, p_status: f.status || 'open' });
    return rpc('add_note', { p_code: body.code, p_entity: body.entity, p_body: body.body, p_question: body.question ?? null });
  }
  if ((m = p.match(/^\/notes\/(\d+)\/resolve$/))) { await rpc('resolve_note', { p_id: Number(m[1]), p_resolved: !!body.resolved, p_response: body.response || null }); return { ok: true }; }
  if ((m = p.match(/^\/notes\/(\d+)\/delete$/))) { await rpc('delete_note', { p_id: Number(m[1]) }); return { ok: true }; }
  throw new Error('مسار غير معروف: ' + p);
}
