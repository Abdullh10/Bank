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

// المنطق مستقل عن Supabase ليُختبر: deps = { callerId(jwt), roleOf(id), createUser({email,password,name}), setProfile(id, fields), setPassword(id, password) }
export async function handle(body, jwt, deps) {
  const caller = jwt ? await deps.callerId(jwt) : null;
  if (!caller) return { status: 401, body: { error: 'يلزم تسجيل الدخول' } };
  if ((await deps.roleOf(caller)) !== 'admin') return { status: 403, body: { error: 'للمشرف فقط' } };

  if (body?.action === 'create') {
    const list = Array.isArray(body.students) ? body.students : [];
    if (!list.length) return { status: 400, body: { error: 'لا توجد بيانات طلاب' } };
    if (list.length > 100) return { status: 400, body: { error: 'الحد الأقصى 100 طالب في المرة الواحدة' } };
    const results = [];
    for (const s of list) {
      const name = String(s.name || '').trim();
      const section = String(s.section || '').trim();
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
      await deps.setProfile(created.id, { role: 'student', display_name: name, section: section || null, profile_confirmed: false });
      results.push({ name, section, username: created.username, password, ok: true });
    }
    return { status: 200, body: { results } };
  }

  if (body?.action === 'reset') {
    const role = await deps.roleOf(body.userId);
    if (!['student', 'pending'].includes(role)) return { status: 400, body: { error: 'إعادة التعيين متاحة لحسابات الطلاب فقط' } };
    const password = randomPassword();
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
  const admin = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'), { auth: { persistSession: false } });
  const deps = {
    callerId: async jwt => (await admin.auth.getUser(jwt)).data?.user?.id || null,
    roleOf: async id => (await admin.from('profiles').select('role').eq('user_id', id).maybeSingle()).data?.role || null,
    createUser: async ({ email, password, name }) => {
      const { data, error } = await admin.auth.admin.createUser({ email, password, email_confirm: true, user_metadata: { display_name: name } });
      return error ? { error: error.message } : { id: data.user.id };
    },
    setProfile: async (id, fields) => { await admin.from('profiles').update(fields).eq('user_id', id); },
    setPassword: async (id, password) => {
      const { error } = await admin.auth.admin.updateUserById(id, { password });
      return error ? { error: error.message } : {};
    },
  };
  Deno.serve(async req => {
    if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });
    const jwt = (req.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
    let body = null;
    try { body = await req.json(); } catch { /* جسم غير صالح */ }
    const out = await handle(body, jwt, deps);
    return new Response(JSON.stringify(out.body), { status: out.status, headers: { ...CORS, 'Content-Type': 'application/json' } });
  });
}
