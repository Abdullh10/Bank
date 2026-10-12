// دالة حافة (Edge Function) لإدارة حسابات الطلاب: إنشاء حسابات وإعادة تعيين كلمات المرور.
// تعمل داخل Supabase، ويصلها مفتاح الخدمة تلقائيًا من بيئة Supabase (SUPABASE_SERVICE_ROLE_KEY)؛ لا يوضع في الموقع ولا في المستودع.
// لا تنفذ شيئًا إلا إذا كان المستدعي مسجلًا بدور «admin».
// النشر: Supabase ← Edge Functions ← Deploy a new function ← Via Editor، الاسم: admin-users، والصق هذا الملف كاملًا.
// مكتوب بصيغة JavaScript صالحة داخل TypeScript حتى يُختبر بـ Node دون تحويل.

export const LOGIN_DOMAIN = 'chem21.local';
const ALPHABET = 'abcdefghjkmnpqrstuvwxyz23456789'; // بلا أحرف ملتبسة (l, 1, o, 0, i)

export function randomPassword(len = 8) {
  const bytes = crypto.getRandomValues(new Uint8Array(len));
  return Array.from(bytes, b => ALPHABET[b % ALPHABET.length]).join('');
}
export function randomUsername() {
  const bytes = crypto.getRandomValues(new Uint32Array(1));
  return 'st' + String(10000 + (bytes[0] % 90000));
}
export const cleanUsername = u => String(u || '').trim().toLowerCase();
export const validUsername = u => /^[a-z0-9][a-z0-9._-]{2,29}$/.test(u);

// المنطق مستقل عن Supabase ليُختبر. التحقق من الدور وتحديث ملف الطالب يتمان بتوكن المشرف نفسه (عبر دوال قاعدة البيانات)،
// ومفتاح الخدمة لا يُستخدم إلا لإنشاء الحساب وتغيير كلمة المرور في Supabase Auth.
// deps = { callerRole(jwt) → {role}|{error}, initStudent(jwt, id, {name, section, grade}) → {}|{error}, isStudent(jwt, id) → bool,
//          createUser({email,password,name}) → {id}|{error}, setPassword(id, password) → {}|{error},
//          setEmail(id, email) → {}|{error}, deleteUser(id) → {}|{error} }
export async function handle(body, jwt, deps) {
  if (!jwt) return { status: 401, body: { error: 'يلزم تسجيل الدخول' } };
  const who = await deps.callerRole(jwt);
  if (who.error) return { status: 401, body: { error: 'تعذر التحقق من الحساب: ' + who.error } };
  if (who.role !== 'admin') return { status: 403, body: { error: `للمشرف فقط (دور الحساب الحالي: ${who.role || 'غير معروف'})` } };

  if (body?.action === 'create') {
    const list = Array.isArray(body.students) ? body.students : [];
    if (!list.length) return { status: 400, body: { error: 'لا توجد بيانات طلاب' } };
    if (list.length > 100) return { status: 400, body: { error: 'الحد الأقصى 100 طالب في المرة الواحدة' } };
    const results = [];
    for (const s of list) {
      if (!s || typeof s !== 'object') { results.push({ name: '', ok: false, error: 'سطر غير صالح' }); continue; }
      const name = String(s.name || '').trim();
      const section = String(s.section || '').trim();
      const grade = String(s.grade || '').trim();
      let username = cleanUsername(s.username);
      const password = String(s.password || '') || randomPassword();
      if (name.length < 3) { results.push({ name, ok: false, error: 'الاسم قصير' }); continue; }
      if (username && !validUsername(username)) { results.push({ name, ok: false, error: 'اسم المستخدم: حروف إنجليزية صغيرة وأرقام (3 إلى 30)' }); continue; }
      if (password.length < 8) { results.push({ name, ok: false, error: 'كلمة المرور 8 أحرف على الأقل' }); continue; }
      let created = null, lastErr = '';
      for (let attempt = 0; attempt < (username ? 1 : 5) && !created; attempt++) {
        const u = username || randomUsername();
        const r = await deps.createUser({ email: `${u}@${LOGIN_DOMAIN}`, password, name });
        if (r.id) created = { id: r.id, username: u };
        else lastErr = /already|exists|registered/i.test(r.error || '') ? 'اسم المستخدم مستخدم من قبل' : (r.error || 'تعذر إنشاء الحساب');
      }
      if (!created) { results.push({ name, ok: false, error: lastErr }); continue; }
      const init = await deps.initStudent(jwt, created.id, { name, section, grade });
      if (init?.error) {
        // لا يبقى حساب معلّق بكلمة مرور معروفة: يُحذف الحساب الذي لم يكتمل ضبطه
        await deps.deleteUser(created.id);
        results.push({ name, ok: false, error: 'تعذر ضبط ملف الطالب فأُلغي الحساب: ' + init.error }); continue;
      }
      results.push({ name, grade, section, username: created.username, password, ok: true });
    }
    return { status: 200, body: { results } };
  }

  // حذف دفعة: قائمة معرّفات، ويُتحقق من كل حساب أنه حساب طالب قبل حذفه
  if (body?.action === 'deleteMany') {
    const ids = Array.isArray(body.userIds) ? [...new Set(body.userIds)] : [];
    if (!ids.length) return { status: 400, body: { error: 'لم يُحدد أي حساب' } };
    if (ids.length > 300) return { status: 400, body: { error: 'الحد الأقصى 300 حساب في المرة الواحدة' } };
    let deleted = 0; const failed = [];
    for (const id of ids) {
      if (!(await deps.isStudent(jwt, id))) { failed.push({ id, error: 'ليس حساب طالب' }); continue; }
      const r = await deps.deleteUser(id);
      if (r?.error) failed.push({ id, error: r.error }); else deleted++;
    }
    return { status: 200, body: { deleted, failed } };
  }

  // الإجراءات التالية لحسابات الطلاب فقط
  if (['reset', 'rename', 'delete'].includes(body?.action) && !(await deps.isStudent(jwt, body.userId)))
    return { status: 400, body: { error: 'هذا الإجراء متاح لحسابات الطلاب فقط' } };

  if (body?.action === 'rename') {
    const username = cleanUsername(body.username);
    if (!validUsername(username)) return { status: 400, body: { error: 'اسم المستخدم: حروف إنجليزية صغيرة وأرقام (3 إلى 30) ويبدأ بحرف أو رقم' } };
    const r = await deps.setEmail(body.userId, `${username}@${LOGIN_DOMAIN}`);
    if (r?.error) return { status: 400, body: { error: /already|exists|registered/i.test(r.error) ? 'اسم المستخدم مستخدم من قبل' : r.error } };
    return { status: 200, body: { username } };
  }

  if (body?.action === 'delete') {
    const r = await deps.deleteUser(body.userId);
    if (r?.error) return { status: 400, body: { error: r.error } };
    return { status: 200, body: { ok: true } };
  }

  if (body?.action === 'reset') {
    // كلمة مرور يحددها المشرف، أو تُولَّد تلقائيًا إن تُركت فارغة
    const password = String(body.password || '') || randomPassword();
    if (password.length < 8) return { status: 400, body: { error: 'كلمة المرور 8 أحرف على الأقل' } };
    const r = await deps.setPassword(body.userId, password);
    if (r?.error) return { status: 400, body: { error: r.error } };
    return { status: 200, body: { password } };
  }
  return { status: 400, body: { error: 'إجراء غير معروف' } };
}

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

if (typeof Deno !== 'undefined') {
  const { createClient } = await import('https://esm.sh/@supabase/supabase-js@2.45.4');
  const URL_ = Deno.env.get('SUPABASE_URL');
  const admin = createClient(URL_, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'), { auth: { persistSession: false } });
  // عميل بصلاحيات المستدعي نفسه: كل ما يمر به يخضع لسياسات قاعدة البيانات كما في الموقع.
  // المفتاح العام: نفس مفتاح الموقع المرسل مع الطلب (apikey)، وإلا مفتاح anon من بيئة Supabase.
  const makeDeps = apikey => {
  const asCaller = jwt => createClient(URL_, apikey || Deno.env.get('SUPABASE_ANON_KEY'), {
    auth: { persistSession: false }, global: { headers: { Authorization: `Bearer ${jwt}` } } });
  return {
    callerRole: async jwt => {
      const { data, error } = await asCaller(jwt).rpc('get_me');
      return error ? { error: error.message } : { role: data?.role || null };
    },
    initStudent: async (jwt, id, { name, section, grade }) => {
      const { error } = await asCaller(jwt).rpc('admin_init_student', { p_id: id, p_name: name, p_section: section || null, p_grade: grade || null });
      return error ? { error: error.message } : {};
    },
    isStudent: async (jwt, id) => (await asCaller(jwt).rpc('admin_is_student', { p_id: id })).data === true,
    createUser: async ({ email, password, name }) => {
      const { data, error } = await admin.auth.admin.createUser({ email, password, email_confirm: true, user_metadata: { display_name: name } });
      return error ? { error: error.message } : { id: data.user.id };
    },
    setPassword: async (id, password) => {
      const { error } = await admin.auth.admin.updateUserById(id, { password });
      return error ? { error: error.message } : {};
    },
    setEmail: async (id, email) => {
      const { error } = await admin.auth.admin.updateUserById(id, { email, email_confirm: true });
      return error ? { error: error.message } : {};
    },
    deleteUser: async id => {
      const { error } = await admin.auth.admin.deleteUser(id);
      return error ? { error: error.message } : {};
    },
  };
  };
  Deno.serve(async req => {
    if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });
    const jwt = (req.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
    let body = null;
    try { body = await req.json(); } catch { /* جسم غير صالح */ }
    const out = await handle(body, jwt, makeDeps(req.headers.get('apikey')));
    return new Response(JSON.stringify(out.body), { status: out.status, headers: { ...CORS, 'Content-Type': 'application/json' } });
  });
}
