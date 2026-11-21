-- =====================================================================
-- ترحيل «تعدد المواد — المرحلة 4» (2026-11-19) لقاعدة الإنتاج: يُنفذ مرة واحدة في SQL Editor بعد subjects-2026-11-15.sql.
-- آمن لإعادة التنفيذ (idempotent). مطابق للقسم الأخير من supabase/schema.sql.
-- 2026-11-19: تعدد المواد — المرحلة 4
--   (1) المراجع العلمي والمشرف التربوي بنطاق مواد: صفوف staff_subjects تقيّده بمقررات هذه المواد في قاعدة البيانات نفسها
--       (السياسات والدوال المحمية عبر _course_ok)؛ ومن لا نطاق له يرى كل شيء كما كان (متوافق مع السابق).
--       المقيَّد لا يرى البرامج المشتركة بلا مادة (التحصيلي) ولا سجل تعديلات المواد والمقررات.
--   (2) الاستبانة تنتمي إلى مقرر (comms.course_id الموجود أصلًا) ومنه إلى مادته: تُرسل لطلاب المقرر المسجلين فيه،
--       وتُعرض عباراتها باسم المادة، وتُصفّى النتائج بالمادة والمقرر. الاستبانات السابقة تُنقل إلى مقرر الكيمياء الذي ينتمي إليه طلابها.
--   (3) الطالب: مادة كل مقرر في get_me (لتبويبات المواد).
--   (4) لوحة مقارنة المواد للمالك: أرقام مجمّعة فقط (admin_compare_subjects).
--   كل ما هنا إضافة أو استبدال لدوال، وآمن لإعادة التنفيذ؛ لا يُحذف شيء من بيانات الطلاب.
-- =====================================================================
create table if not exists public.staff_subjects (
  user_id uuid not null references public.profiles(user_id) on delete cascade,
  subject_id text not null references public.subjects(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (user_id, subject_id)
);
alter table public.staff_subjects enable row level security;
revoke all on public.staff_subjects from anon, authenticated;

-- هل الحساب الحالي مراجع أو مشرف مقيَّد بمواد؟
create or replace function public._staff_scoped() returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select exists (select 1 from public.profiles p join public.staff_subjects s on s.user_id = p.user_id
                 where p.user_id = auth.uid() and p.role in ('reviewer', 'supervisor'))
$$;

-- هل يستطيع الحساب الحالي قراءة هذا المقرر؟ المعلم: مقرراته المسندة الجاهزة. المراجع والمشرف المقيَّدان: مقررات موادهما فقط.
create or replace function public._course_ok(p_course bigint) returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select case (select role from public.profiles where user_id = auth.uid())
    when 'viewer' then exists (select 1 from public.teacher_courses t join public.courses c on c.id = t.course_id
                               where t.teacher_id = auth.uid() and t.course_id = p_course and c.status = 'ready')
    when 'reviewer' then not exists (select 1 from public.staff_subjects s where s.user_id = auth.uid())
      or exists (select 1 from public.courses c join public.staff_subjects s on s.subject_id = c.subject_id and s.user_id = auth.uid() where c.id = p_course)
    when 'supervisor' then not exists (select 1 from public.staff_subjects s where s.user_id = auth.uid())
      or exists (select 1 from public.courses c join public.staff_subjects s on s.subject_id = c.subject_id and s.user_id = auth.uid() where c.id = p_course)
    else true end
$$;
create or replace function public._require_course(p_course bigint) returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if (public.my_role() = 'viewer' or public._staff_scoped()) and (p_course is null or not public._course_ok(p_course)) then
    raise exception 'هذا المقرر غير متاح لحسابك' using errcode = '42501';
  end if;
end $$;

-- سجل التعديلات للمقيَّد: الأسئلة والأهداف والمحتوى المكمّل في مقرراته فقط
create or replace function public._revision_ok(p_entity text, p_id bigint) returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select not public._staff_scoped() or case p_entity
    when 'question' then public._course_ok(public._course_of_question(p_id))
    when 'objective' then public._course_ok(public._course_of_objective(p_id))
    when 'supplement' then public._course_ok(public._course_of_objective(p_id))
    else false end
$$;
drop policy if exists revisions_read on public.revisions;
create policy revisions_read on public.revisions for select to authenticated using (public.is_reviewer() and public._revision_ok(entity, entity_id));

-- ---------- أدوات المراجعة: كل دالة تعمل على عنصر بعينه تتحقق من نطاق مقرره ----------
create or replace function public.review_objective(p_code text, p_action text, p_approved_text text default null, p_note text default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; v_status text; v_text text;
begin
  perform public._require_reviewer();
  select * into o from public.objectives where code = p_code;
  if not found or not public._course_ok(public._course_of_lesson(o.lesson_id)) then raise exception 'الهدف غير موجود'; end if;
  v_status := case p_action when 'approve' then 'approved' when 'return' then 'returned' when 'reset' then 'pending' end;
  if v_status is null then raise exception 'إجراء غير صالح'; end if;
  if p_action = 'return' and coalesce(trim(p_note), '') = '' then raise exception 'اكتب سبب الإعادة للمراجعة'; end if;
  v_text := o.approved_text;
  if p_action = 'approve' then
    -- المراجع يعتمد الصياغة الحالية فقط؛ تغيير الصياغة لمالك المشروع
    v_text := trim(coalesce(case when public.is_admin() then nullif(p_approved_text, '') end, o.approved_text, o.proposed_text, o.original_text));
    if length(v_text) < 8 then raise exception 'الصياغة المعتمدة غير صالحة'; end if;
  end if;
  update public.objectives set review_status = v_status, approved_text = v_text, reviewed_by = auth.uid(), reviewed_at = now() where id = o.id;
  perform public._log('objective', o.id, p_action, jsonb_build_object('reviewStatus', o.review_status, 'approvedText', o.approved_text),
    jsonb_build_object('reviewStatus', v_status, 'approvedText', v_text), p_note);
end $$;

create or replace function public.review_supplement(p_code text, p_action text, p_supplement text default null, p_note text default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; s public.supplements; v_status text; v_text text;
begin
  perform public._require_reviewer();
  select * into o from public.objectives where code = p_code;
  if found and not public._course_ok(public._course_of_lesson(o.lesson_id)) then raise exception 'الهدف غير موجود'; end if;
  select * into s from public.supplements where objective_id = o.id;
  if not found then raise exception 'لا يوجد محتوى مكمّل لهذا الهدف'; end if;
  v_status := case p_action when 'approve' then 'approved' when 'return' then 'returned' when 'reset' then 'pending' end;
  if v_status is null then raise exception 'إجراء غير صالح'; end if;
  if nullif(trim(p_supplement), '') is not null and trim(p_supplement) <> s.supplement and not public.is_admin() then
    raise exception 'تعديل نص المحتوى لمالك المشروع فقط؛ اكتب ملاحظتك بدلًا من ذلك' using errcode = '42501';
  end if;
  v_text := coalesce(nullif(trim(p_supplement), ''), s.supplement);
  update public.supplements set review_status = v_status, supplement = v_text where objective_id = o.id;
  perform public._log('supplement', o.id, p_action, jsonb_build_object('reviewStatus', s.review_status, 'supplement', s.supplement),
    jsonb_build_object('reviewStatus', v_status, 'supplement', v_text), p_note);
end $$;

create or replace function public.set_question_status(p_id bigint, p_status text, p_note text default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare q public.questions; a public.question_answers;
begin
  perform public._require_reviewer();
  select * into q from public.questions where id = p_id;
  if not found or not public._course_ok(public._course_of_objective(q.objective_id)) then raise exception 'السؤال غير موجود'; end if;
  if p_status not in ('generated', 'in_review', 'needs_revision', 'approved') then raise exception 'حالة غير صالحة'; end if;
  if p_status = 'needs_revision' and coalesce(trim(p_note), '') = '' then raise exception 'اكتب ملاحظة توضح المطلوب تعديله'; end if;
  select * into a from public.question_answers where question_id = p_id;
  if p_status = 'approved' and coalesce((a.auto_check->>'passed')::boolean, false) = false then
    raise exception 'لا يمكن الاعتماد قبل اجتياز التحقق الآلي؛ عدّل السؤال أولًا';
  end if;
  update public.questions set status = p_status, reviewed_by = auth.uid(), reviewed_at = now() where id = p_id;
  if coalesce(trim(p_note), '') <> '' then update public.question_answers set reviewer_notes = trim(p_note) where question_id = p_id; end if;
  perform public._log('question', p_id, 'status', jsonb_build_object('status', q.status), jsonb_build_object('status', p_status), p_note);
end $$;

create or replace function public.get_question(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  if not exists (select 1 from questions q where q.id = p_id and public._course_ok(public._course_of_objective(q.objective_id))) then
    raise exception 'السؤال غير موجود' using errcode = 'P0002';
  end if;
  return (select public._q_public(q, a, true) from questions q left join question_answers a on a.question_id = q.id where q.id = p_id);
end $$;

create or replace function public.get_revisions(p_limit int default 100, p_question bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', r.id, 'entity', r.entity, 'entity_id', r.entity_id, 'action', r.action,
      'note', r.note, 'at', r.at, 'user', r.user_name, 'before_json', r.before_json, 'after_json', r.after_json) order by r.id desc), '[]')
    from (select * from revisions where (p_question is null or (entity = 'question' and entity_id = p_question)) and public._revision_ok(entity, entity_id)
          order by id desc limit least(greatest(coalesce(p_limit, 100), 1), 500)) r);
end $$;

create or replace function public.add_note(p_code text, p_entity text, p_body text, p_question bigint default null) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; n public.review_notes;
begin
  perform public._require_reviewer();
  select * into o from public.objectives where code = p_code;
  if not found or not public._course_ok(public._course_of_lesson(o.lesson_id)) then raise exception 'الهدف غير موجود'; end if;
  if p_entity not in ('objective', 'question', 'supplement') then raise exception 'نوع الملاحظة غير صالح'; end if;
  if p_entity = 'question' and not exists (select 1 from public.questions where id = p_question and objective_id = o.id) then raise exception 'السؤال غير موجود في هذا الهدف'; end if;
  if length(trim(coalesce(p_body, ''))) < 3 then raise exception 'اكتب الملاحظة'; end if;
  if length(p_body) > 2000 then raise exception 'الملاحظة طويلة جدًا (2000 حرف كحد أقصى)'; end if;
  insert into public.review_notes (objective_id, question_id, entity, body, author, author_name)
  values (o.id, case when p_entity = 'question' then p_question end, p_entity, trim(p_body), auth.uid(),
    (select display_name from public.profiles where user_id = auth.uid()))
  returning * into n;
  return public._note_json(n);
end $$;

create or replace function public.get_notes(p_code text default null, p_status text default 'open') returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_scoped boolean := public._staff_scoped();
begin
  perform public._require_reviewer();
  return (select coalesce(jsonb_agg(public._note_json(n) order by n.created_at desc), '[]') from (
    select n.* from public.review_notes n join public.objectives o on o.id = n.objective_id
    where (p_code is null or o.code = p_code)
      and (not v_scoped or public._course_ok(public._course_of_lesson(o.lesson_id)))
      and (p_code is not null or coalesce(p_status, 'open') = 'all'
           or (coalesce(p_status, 'open') = 'open' and n.resolved_at is null)
           or (p_status = 'resolved' and n.resolved_at is not null))
    order by n.created_at desc limit 500) n);
end $$;

create or replace function public.delete_note(p_id bigint) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  delete from public.review_notes n where n.id = p_id and (public.is_admin() or (n.author = auth.uid() and n.resolved_at is null) or n.source = 'student')
    and public._course_ok(public._course_of_objective(n.objective_id));
  if not found then raise exception 'لا يمكن حذف هذه الملاحظة' using errcode = '42501'; end if;
end $$;

-- ---------- إدارة النطاق (لمالك المشروع) ----------
-- يستبدل نطاق المراجع أو المشرف: p_subjects فارغة = كل المواد (دون تقييد)
create or replace function public.admin_set_staff_subjects(p_user uuid, p_subjects text[]) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_role text; v_list text[]; v_before text[];
begin
  perform public._require_admin();
  select role into v_role from profiles where user_id = p_user;
  if v_role is null or v_role not in ('reviewer', 'supervisor') then raise exception 'النطاق بالمواد للمراجع العلمي والمشرف التربوي فقط' using errcode = '22023'; end if;
  select coalesce(array_agg(distinct x order by x), '{}') into v_list from unnest(coalesce(p_subjects, '{}')) x where x is not null and x <> '';
  if exists (select 1 from unnest(v_list) x where not exists (select 1 from subjects s where s.id = x)) then raise exception 'مادة غير موجودة' using errcode = '22023'; end if;
  select coalesce(array_agg(subject_id order by subject_id), '{}') into v_before from staff_subjects where user_id = p_user;
  delete from staff_subjects where user_id = p_user and not (subject_id = any(v_list));
  insert into staff_subjects (user_id, subject_id) select p_user, x from unnest(v_list) x on conflict do nothing;
  if v_before is distinct from v_list then
    perform public._log('staff_subjects', 0, 'set', jsonb_build_object('user', p_user, 'subjects', to_jsonb(v_before)), jsonb_build_object('user', p_user, 'subjects', to_jsonb(v_list)),
      'نطاق ' || coalesce((select display_name from profiles where user_id = p_user), '') || ': ' ||
      coalesce((select string_agg(s.name, '، ' order by s.sort_order) from subjects s where s.id = any(v_list)), 'كل المواد'));
  end if;
  return jsonb_build_object('user', p_user, 'subjects', to_jsonb(v_list));
end $$;

-- حسابات الفريق: أُضيف نطاق المواد للمراجع والمشرف
create or replace function public.admin_list_staff() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', pr.user_id, 'username', split_part(u.email, '@', 1), 'name', pr.display_name,
      'role', pr.role, 'createdAt', pr.created_at, 'lastSignIn', u.last_sign_in_at, 'self', pr.user_id = auth.uid(),
      'assignedCourses', case when pr.role = 'viewer' then (select count(*) from teacher_courses t where t.teacher_id = pr.user_id) end,
      'assignedStudents', case when pr.role = 'viewer' then (select count(*) from teacher_students t where t.teacher_id = pr.user_id) end,
      'subjects', case when pr.role in ('reviewer', 'supervisor') then (select coalesce(jsonb_agg(s.subject_id order by s.subject_id), '[]') from staff_subjects s where s.user_id = pr.user_id) end)
      order by case pr.role when 'admin' then 0 when 'reviewer' then 1 when 'supervisor' then 2 when 'principal' then 3 when 'viewer' then 4 else 5 end, pr.display_name), '[]')
    from profiles pr join auth.users u on u.id = pr.user_id
    where pr.role in ('admin', 'reviewer', 'viewer', 'supervisor', 'principal') or (pr.role = 'pending' and (pr.staff or not pr.managed)));
end $$;

-- تغيير الدور إلى غير المراجع والمشرف يلغي نطاق المواد (فلا يعود نطاق قديم منسي إن أُعيد الدور لاحقًا)
create or replace function public.admin_update_staff(p_id uuid, p_name text, p_role text) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  if p_role not in ('reviewer', 'viewer', 'supervisor', 'principal', 'pending') then raise exception 'الدور غير صالح'; end if;
  if p_id = auth.uid() then raise exception 'لا يمكن تعديل حسابك من هنا'; end if;
  if not exists (select 1 from profiles where user_id = p_id and role <> 'admin' and role <> 'student' and (staff or not managed)) then raise exception 'الحساب ليس حساب فريق'; end if;
  update profiles set display_name = coalesce(nullif(trim(p_name), ''), display_name), role = p_role, staff = true where user_id = p_id;
  if p_role not in ('reviewer', 'supervisor') then delete from staff_subjects where user_id = p_id; end if;
end $$;

-- الحساب الحالي: أُضيفت مادة كل مقرر للطالب (subjectId) ونطاق المواد للمراجع والمشرف (scope؛ فارغ = كل المواد)
create or replace function public.get_me() returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select case when auth.uid() is null then null else
    (select jsonb_build_object('id', user_id, 'username', split_part(coalesce((select u.email from auth.users u where u.id = profiles.user_id), email), '@', 1), 'displayName', display_name, 'role', role,
       'section', section, 'grade', grade, 'profileConfirmed', profile_confirmed,
       -- مقررات الطالب المسندة (الجاهزة) لعرضها في الترويسة
       'courses', (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'code', c.code, 'grade', c.grade, 'term', c.term, 'kind', c.kind, 'subjectId', c.subject_id) order by c.sort_order), '[]')
         from course_enrollments e join courses c on c.id = e.course_id and c.status = 'ready' where e.user_id = profiles.user_id),
       'scope', case when role in ('reviewer', 'supervisor') then (select coalesce(jsonb_agg(s.subject_id order by s.subject_id), '[]') from staff_subjects s where s.user_id = profiles.user_id) end)
     from profiles where user_id = auth.uid()) end
$$;

-- ---------- الاستبانة لكل مقرر ومادته ----------
-- اسم مادة المقرر (فارغ للبرامج المشتركة)
create or replace function public._course_subject_name(p_course bigint) returns text
language sql stable security definer set search_path = public, pg_temp as $$
  select s.name from public.courses c join public.subjects s on s.id = c.subject_id where c.id = p_course
$$;

-- مرة واحدة: الاستبانات السابقة (أُرسلت قبل ربطها بمقرر) تُنقل إلى مقرر الكيمياء الأكثر تسجيلًا بين من أُرسلت إليهم،
-- وإلا فأول مقرر كيمياء؛ ولا تتغير الإجابات ولا النتائج.
do $$ begin
  if not exists (select 1 from public.schema_flags where key = 'survey_course_2026_11_19') then
    update public.comms c set course_id = coalesce(
        (select e.course_id from public.comm_recipients cr join public.course_enrollments e on e.user_id = cr.student_id
           join public.courses k on k.id = e.course_id and k.subject_id = 'chem'
         where cr.comm_id = c.id group by e.course_id order by count(*) desc, e.course_id limit 1),
        (select k.id from public.courses k where k.subject_id = 'chem' order by (k.status = 'ready') desc, k.sort_order, k.id limit 1))
      where c.kind = 'survey'
        and not exists (select 1 from public.courses k where k.id = c.course_id and k.subject_id is not null)
        and exists (select 1 from public.courses k where k.subject_id = 'chem');
    insert into public.schema_flags (key) values ('survey_course_2026_11_19');
  end if;
end $$;

-- الإرسال: الاستبانة كالمهمة تتطلب مقررًا متاحًا لحساب المرسل، وتصل لطلابه المسجلين في ذلك المقرر فقط
create or replace function public.staff_send_comm(p jsonb) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare g public.grade_settings; v_role text := public.my_role(); v_course bigint := coalesce(nullif(p->>'course', '')::bigint, public._default_course());
  v_kind text := p->>'kind'; v_title text := trim(coalesce(p->>'title', '')); v_body text := nullif(trim(coalesce(p->>'body', '')), '');
  v_mode text := coalesce(p#>>'{target,mode}', 'all'); v_section text := nullif(trim(coalesce(p#>>'{target,section}', '')), ''); v_grade text := nullif(trim(coalesce(p#>>'{target,grade}', '')), '');
  v_list uuid[] := '{}'; v_ids uuid[]; v_n int; v_lesson bigint; v_nq int; v_acc int; v_due timestamptz; v_max int; v_today timestamptz; v_aud jsonb; v_busy int; v_id bigint; v_reward int := 0; v_week timestamptz; v_used int; v_cap int;
  v_scoped boolean := v_kind in ('task', 'survey');
  bad constant text := '[\x01-\x08\x0b\x0c\x0e-\x1f‪-‮⁦-⁩]';
begin
  perform public._require_comm_staff();
  if v_scoped then
    perform public._require_course(v_course);
    if v_course is null or not exists (select 1 from courses where id = v_course) then raise exception 'اختر المقرر أولًا'; end if;
  else v_course := coalesce(v_course, 0); end if;
  select * into g from grade_settings where id = 1;
  if v_kind not in ('message', 'task', 'survey') then raise exception 'نوع غير صالح'; end if;
  if length(v_title) < 2 or length(v_title) > 80 then raise exception 'العنوان بين 2 و80 حرفًا'; end if;
  if length(coalesce(v_body, '')) > 500 then raise exception 'النص طويل (500 حرف كحد أقصى)'; end if;
  if v_title ~ bad or coalesce(v_body, '') ~ bad then raise exception 'النص يحوي رموزًا غير مسموحة'; end if;
  v_max := case when v_role = 'admin' then 1000 else g.comm_max_recipients end;
  v_today := date_trunc('day', now() at time zone 'Asia/Riyadh') at time zone 'Asia/Riyadh';
  if v_role = 'viewer' and (select count(*) from comms where sender_id = auth.uid() and created_at >= v_today) >= g.comm_daily_limit then
    raise exception 'بلغت الحد اليومي للإرسال (% في اليوم)', g.comm_daily_limit;
  end if;
  if v_mode not in ('all', 'section', 'students') then raise exception 'المستلمون غير صالحين'; end if;
  if v_mode = 'section' and v_section is null then raise exception 'اختر الشعبة'; end if;
  if v_mode = 'students' then
    select coalesce(array_agg(x::uuid), '{}') into v_list from jsonb_array_elements_text(coalesce(p#>'{target,students}', '[]')) x;
    if cardinality(v_list) = 0 then raise exception 'اختر طالبًا واحدًا على الأقل'; end if;
  end if;
  select array_agg(pr.user_id) into v_ids from profiles pr
    where pr.role = 'student' and pr.managed and public._visible_student(pr.user_id)
      and (not v_scoped or exists (select 1 from course_enrollments e where e.user_id = pr.user_id and e.course_id = v_course))
      and (v_grade is null or pr.grade = v_grade) and (v_section is null or pr.section = v_section)
      and (v_mode in ('all', 'section') or (v_mode = 'students' and pr.user_id = any(v_list)));
  v_n := coalesce(cardinality(v_ids), 0);
  if v_n = 0 then raise exception '%', case when v_kind = 'task' then 'لا يوجد طلاب مطابقون مسجلون في مقرر هذا الدرس'
    when v_kind = 'survey' then 'لا يوجد طلاب مطابقون مسجلون في هذا المقرر' else 'لا يوجد طلاب مطابقون؛ تأكد من إسناد الطلاب لك من «حسابات الفريق»' end; end if;
  if v_mode = 'students' and v_n <> cardinality(v_list) then raise exception '%', case when v_kind = 'task' then 'بعض الطلاب المحددين ليسوا من طلابك أو غير مسجلين في مقرر هذا الدرس'
    when v_kind = 'survey' then 'بعض الطلاب المحددين ليسوا من طلابك أو غير مسجلين في هذا المقرر' else 'بعض الطلاب المحددين ليسوا من طلابك' end; end if;
  if v_n > v_max then raise exception 'عدد المستلمين % يتجاوز الحد (%)', v_n, v_max; end if;
  if v_kind = 'message' and v_body is null and length(v_title) < 3 then raise exception 'اكتب الرسالة'; end if;
  if v_kind = 'task' then
    v_lesson := nullif(p->>'lesson', '')::bigint; v_nq := nullif(p->>'n', '')::int; v_acc := coalesce(nullif(p->>'minAccuracy', '')::int, 0); v_due := nullif(p->>'due', '')::timestamptz;
    if v_lesson is null or not exists (select 1 from lessons l join chapters ch on ch.id = l.chapter_id where l.id = v_lesson and ch.course_id = v_course) then raise exception 'اختر درسًا من هذا المقرر'; end if;
    if v_nq is null or v_nq < 5 or v_nq > 200 then raise exception 'عدد الأسئلة بين 5 و200'; end if;
    if v_acc < 0 or v_acc > 100 then raise exception 'نسبة الصحة بين 0 و100'; end if;
    if v_due is null or v_due < now() + interval '1 hour' or v_due > now() + interval '60 days' then raise exception 'الموعد بعد ساعة على الأقل وخلال 60 يومًا'; end if;
    v_reward := coalesce(nullif(p->>'reward', '')::int, 0);
    v_cap := case when v_role = 'admin' then 500 else g.teacher_coupon_max end;
    if v_reward < 0 or v_reward > v_cap then raise exception 'مكافأة المهمة بين 0 و% نقطة للطالب', v_cap; end if;
    if v_reward > 0 then
      -- مكافأة مرتبطة بإنجاز حقيقي لا بتخمين: 10 أسئلة على الأقل وصحة 50% فأكثر
      if v_nq < 10 or v_acc < 50 then raise exception 'المهمة ذات المكافأة تتطلب 10 أسئلة على الأقل ونسبة صحة 50%% فأكثر'; end if;
      if v_role = 'viewer' then
        v_week := (date_trunc('week', (now() at time zone 'Asia/Riyadh') + interval '1 day') - interval '1 day') at time zone 'Asia/Riyadh';
        v_used := public._quota_used(auth.uid(), v_week);
        if v_used + v_reward * v_n > g.teacher_weekly_quota then
          raise exception 'مكافآت المهمة (% نقطة) تتجاوز حصتك الأسبوعية (استهلكت % من %)', v_reward * v_n, v_used, g.teacher_weekly_quota;
        end if;
      end if;
    end if;
    select count(*) into v_busy from unnest(v_ids) u(id) where (select count(*) from comm_recipients cr join comms c on c.id = cr.comm_id
      where cr.student_id = u.id and cr.status = 'open' and c.kind = 'task' and c.status = 'active' and c.due_at > now()) >= g.comm_active_tasks;
    if v_busy > 0 then raise exception 'لدى % من الطلاب % مهام نشطة بالفعل؛ انتظر إنجازها أو ألغِ مهمة', v_busy, g.comm_active_tasks; end if;
  end if;
  v_aud := jsonb_build_object('mode', v_mode, 'grade', v_grade, 'section', v_section, 'n', v_n);
  if exists (select 1 from comms where sender_id = auth.uid() and title = v_title and coalesce(body, '') = coalesce(v_body, '') and audience = v_aud
             and status = 'active' and created_at > now() - interval '1 hour') then
    raise exception 'أرسلت الرسالة نفسها للمستلمين أنفسهم قبل قليل';
  end if;
  -- الاستبانة: مفتوحة من 3 إلى 30 يومًا (10 افتراضيًا) ثم تُغلق وتختفي من صندوق الطالب
  if v_kind = 'survey' and coalesce(nullif(p->>'days', '')::int, 10) not between 3 and 30 then raise exception 'مدة الاستبانة بين 3 و30 يومًا'; end if;
  insert into comms (kind, sender_id, sender_name, course_id, title, body, audience, n_recipients, lesson_id, n_questions, min_accuracy, due_at, reward_points, expires_at)
  values (v_kind, auth.uid(), (select display_name from profiles where user_id = auth.uid()), v_course, v_title, v_body,
    case when v_mode = 'students' then v_aud || jsonb_build_object('students', to_jsonb(v_list)) else v_aud end, v_n, v_lesson, v_nq, v_acc, v_due, v_reward,
    case when v_kind = 'survey' then now() + make_interval(days => coalesce(nullif(p->>'days', '')::int, 10)) else now() + interval '60 days' end)
  returning id into v_id;
  insert into comm_recipients (comm_id, student_id) select v_id, u from unnest(v_ids) u;
  return jsonb_build_object('id', v_id, 'n', v_n);
end $$;

-- المُرسَل: أُضيف مقرر كل رسالة ومادتها، والتصفية p_filter = {subject, course, kind}. (p_course يبقى للتوافق ولا يُصفّي)
drop function if exists public.staff_list_comms(bigint);
create or replace function public.staff_list_comms(p_course bigint default null, p_filter jsonb default '{}') returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_role text := public.my_role(); v_subj text := nullif(p_filter->>'subject', ''); v_crs bigint := nullif(p_filter->>'course', '')::bigint; v_kind text := nullif(p_filter->>'kind', '');
begin
  perform public._require_comm_staff();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'kind', c.kind, 'title', c.title, 'body', c.body, 'sender', c.sender_name, 'mine', c.sender_id = auth.uid(),
      'createdAt', c.created_at, 'status', c.status, 'n', c.n_recipients, 'audience', c.audience,
      'courseId', nullif(c.course_id, 0), 'course', k.code, 'subjectId', k.subject_id, 'subject', s.name,
      'read', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.read_at is not null),
      'help', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.reply_code = 2),
      'ack', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.reply_code = 1),
      'task', case when c.kind = 'task' then jsonb_build_object('lesson', (select l.title from lessons l where l.id = c.lesson_id), 'n', c.n_questions, 'minAccuracy', c.min_accuracy, 'dueAt', c.due_at, 'reward', c.reward_points,
         'done', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status = 'done'),
         'open', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status = 'open'),
         'missed', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status = 'missed')) end,
      'survey', case when c.kind = 'survey' then jsonb_build_object('closesAt', c.expires_at, 'open', c.expires_at > now(),
         'responses', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status = 'done')) end)
    order by c.created_at desc), '[]')
    from (select * from comms x where (v_role = 'admin' or x.sender_id = auth.uid())
            and (v_kind is null or x.kind = v_kind) and (v_crs is null or x.course_id = v_crs)
            and (v_subj is null or exists (select 1 from courses k2 where k2.id = x.course_id and k2.subject_id = v_subj))
          order by x.created_at desc limit 50) c
      left join courses k on k.id = c.course_id left join subjects s on s.id = k.subject_id);
end $$;

-- صندوق الطالب: أُضيف اسم مادة الاستبانة (تُعرض عباراتها به)
create or replace function public.student_inbox() returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare r record;
begin
  perform public._require_student();
  for r in select cr.comm_id from comm_recipients cr join comms c on c.id = cr.comm_id
           where cr.student_id = auth.uid() and cr.status = 'open' and c.kind = 'task' and c.status = 'active' and c.expires_at > now() loop
    perform public._comm_refresh(r.comm_id, auth.uid());
  end loop;
  return jsonb_build_object(
    'unread', (select count(*) from comm_recipients cr join comms c on c.id = cr.comm_id where cr.student_id = auth.uid() and cr.read_at is null and c.status = 'active' and c.expires_at > now()),
    'items', (select coalesce(jsonb_agg(x.j order by x.at desc), '[]') from (
      select c.created_at at, jsonb_build_object('id', c.id, 'kind', c.kind, 'title', c.title, 'body', c.body, 'sender', c.sender_name, 'createdAt', c.created_at,
        'read', cr.read_at is not null, 'reply', cr.reply_code,
        'task', case when c.kind = 'task' then jsonb_build_object('lessonId', c.lesson_id, 'lesson', (select l.title from lessons l where l.id = c.lesson_id),
          'n', c.n_questions, 'minAccuracy', c.min_accuracy, 'dueAt', c.due_at, 'status', cr.status, 'valid', cr.valid_cnt, 'correct', cr.correct_cnt,
          'reward', c.reward_points, 'rewardGot', cr.reward_pts) end,
        'survey', case when c.kind = 'survey' then jsonb_build_object('done', cr.status = 'done', 'closesAt', c.expires_at,
          'subject', public._course_subject_name(c.course_id), 'course', (select k.code from courses k where k.id = c.course_id)) end) j
      from comm_recipients cr join comms c on c.id = cr.comm_id
      where cr.student_id = auth.uid() and c.status = 'active' and c.expires_at > now()
      order by c.created_at desc limit 50) x));
end $$;

-- نتائج الاستبانة: أُضيف مقررها ومادتها (تُعرض العبارات باسم المادة)
create or replace function public.survey_results(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare c public.comms; v_n int; v_show boolean;
begin
  perform public._require_comm_staff();
  select * into c from comms where id = p_id and kind = 'survey' and (sender_id = auth.uid() or public.my_role() = 'admin');
  if not found then raise exception 'الاستبانة غير موجودة'; end if;
  select count(*) into v_n from survey_responses where comm_id = p_id;
  v_show := v_n >= 5 and not (c.status = 'active' and c.expires_at > now());
  return jsonb_build_object('id', c.id, 'title', c.title, 'createdAt', c.created_at, 'closesAt', c.expires_at, 'open', c.status = 'active' and c.expires_at > now(),
    'sent', c.n_recipients, 'responses', v_n,
    'courseId', nullif(c.course_id, 0), 'course', (select k.code from courses k where k.id = c.course_id), 'subject', public._course_subject_name(c.course_id),
    'sectionsSent', (select coalesce(jsonb_object_agg(t.section, t.n), '{}') from (select coalesce(p.section, '—') section, count(*) n from comm_recipients cr
       join profiles p on p.user_id = cr.student_id where cr.comm_id = p_id group by 1) t),
    'rows', case when v_show then (select coalesce(jsonb_agg(jsonb_build_object('a', to_jsonb(r.answers), 'd', r.duration_s,
        's', case when (select count(*) from survey_responses r2 join profiles p2 on p2.user_id = r2.student_id where r2.comm_id = p_id and p2.section is not distinct from pr.section) >= 5 then pr.section end)
        order by random()), '[]') from survey_responses r join profiles pr on pr.user_id = r.student_id where r.comm_id = p_id) else '[]' end,
    'open1', case when v_show then (select coalesce(jsonb_agg(open1 order by random()), '[]') from survey_responses where comm_id = p_id and open1 is not null) else '[]' end,
    'open2', case when v_show then (select coalesce(jsonb_agg(open2 order by random()), '[]') from survey_responses where comm_id = p_id and open2 is not null) else '[]' end);
end $$;

-- قائمة الاستبانات للربط بقياس الأثر (للمالك): أُضيف مقررها ومادتها
create or replace function public.impact_survey_list() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  if public.my_role() <> 'admin' then return '[]'; end if;
  return (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'title', c.title, 'createdAt', c.created_at,
      'courseId', nullif(c.course_id, 0), 'course', k.code, 'subjectId', k.subject_id, 'subject', s.name,
      'responses', (select count(*) from survey_responses r where r.comm_id = c.id)) order by c.created_at desc), '[]')
    from comms c left join courses k on k.id = c.course_id left join subjects s on s.id = k.subject_id where c.kind = 'survey');
end $$;

-- ---------- لوحة مقارنة المواد (لمالك المشروع، أرقام مجمّعة فقط) ----------
create index if not exists idx_pa_answered on public.practice_answers (answered_at);
create or replace function public.admin_compare_subjects() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_now timestamptz := now();
begin
  perform public._require_admin();
  return (with cs as (select c.id, coalesce(c.subject_id, '') sid, c.status from courses c where c.subject_id is not null or c.kind <> 'course'),
    qmap as (select q.id, cs.sid, q.status, q.excluded from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id
             join chapters ch on ch.id = l.chapter_id join cs on cs.id = ch.course_id),
    qs as (select sid, count(*) filter (where not excluded) n, count(*) filter (where not excluded and status = 'approved') a from qmap group by 1),
    st as (select cs.sid, count(distinct e.user_id) n from course_enrollments e join profiles p on p.user_id = e.user_id and p.role = 'student' join cs on cs.id = e.course_id group by 1),
    tc as (select cs.sid, count(distinct t.teacher_id) n from teacher_courses t join profiles p on p.user_id = t.teacher_id and p.role = 'viewer' join cs on cs.id = t.course_id group by 1),
    sec as (select cs.sid, count(distinct coalesce(p.grade, '') || '|' || coalesce(p.section, '')) n from course_enrollments e join profiles p on p.user_id = e.user_id and p.role = 'student'
            join cs on cs.id = e.course_id where p.section is not null group by 1),
    ans as (select qmap.sid, s.user_id, a.correct, a.answered_at from practice_answers a join practice_sessions s on s.id = a.session_id join qmap on qmap.id = a.question_id),
    act as (select sid, count(*) all_n, count(*) filter (where correct) all_c,
              count(*) filter (where answered_at > v_now - interval '30 days') n30, count(*) filter (where answered_at > v_now - interval '30 days' and correct) c30,
              count(*) filter (where answered_at > v_now - interval '7 days') n7,
              count(distinct user_id) filter (where answered_at > v_now - interval '30 days') u30,
              count(distinct user_id) filter (where answered_at > v_now - interval '7 days') u7,
              count(distinct user_id) uall from ans group by 1),
    imp as (select cs.sid, count(distinct i.id) studies,
              count(*) filter (where x.pre is not null and x.post is not null) paired,
              avg(100.0 * x.pre / i.pre_max) filter (where x.pre is not null and x.post is not null) pre,
              avg(100.0 * x.post / i.post_max) filter (where x.pre is not null and x.post is not null) post
            from impact_studies i join cs on cs.id = i.course_id left join impact_scores x on x.study_id = i.id group by 1),
    sv as (select cs.sid, count(distinct c.id) n, count(r.comm_id) responses
           from comms c join cs on cs.id = c.course_id left join survey_responses r on r.comm_id = c.id where c.kind = 'survey' group by 1),
    svs as (select cs.sid, sum(c.n_recipients) sent from comms c join cs on cs.id = c.course_id where c.kind = 'survey' group by 1),
    crs as (select sid, count(*) n, count(*) filter (where status = 'ready') r from cs group by 1),
    rows as (
      select s.id sid, s.name, s.icon, s.color, s.sort_order so from subjects s
      union all select '', 'برامج مشتركة', null, null, 10000 where exists (select 1 from cs where sid = ''))
    select coalesce(jsonb_agg(jsonb_build_object('id', nullif(r.sid, ''), 'name', r.name, 'icon', r.icon, 'color', r.color, 'shared', r.sid = '',
        'courses', coalesce(crs.n, 0), 'ready', coalesce(crs.r, 0),
        'questions', coalesce(qs.n, 0), 'approved', coalesce(qs.a, 0),
        'students', coalesce(st.n, 0), 'teachers', coalesce(tc.n, 0), 'sections', coalesce(sec.n, 0),
        'answers7', coalesce(act.n7, 0), 'answers30', coalesce(act.n30, 0), 'answersAll', coalesce(act.all_n, 0),
        'active7', coalesce(act.u7, 0), 'active30', coalesce(act.u30, 0), 'activeAll', coalesce(act.uall, 0),
        'accuracy30', round(100.0 * act.c30 / nullif(act.n30, 0), 1), 'accuracyAll', round(100.0 * act.all_c / nullif(act.all_n, 0), 1),
        'impact', case when imp.studies > 0 then jsonb_build_object('studies', imp.studies, 'paired', imp.paired,
            'pre', round(imp.pre, 1), 'post', round(imp.post, 1), 'gain', round(imp.post - imp.pre, 1)) end,
        'surveys', case when sv.n > 0 then jsonb_build_object('n', sv.n, 'responses', sv.responses, 'sent', coalesce(svs.sent, 0)) end)
        order by r.so, r.name), '[]')
    from rows r left join crs on crs.sid = r.sid left join qs on qs.sid = r.sid left join st on st.sid = r.sid left join tc on tc.sid = r.sid
      left join sec on sec.sid = r.sid left join act on act.sid = r.sid left join imp on imp.sid = r.sid left join sv on sv.sid = r.sid left join svs on svs.sid = r.sid);
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.review_objective(text, text, text, text), public.review_supplement(text, text, text, text),
  public.set_question_status(bigint, text, text), public.get_question(bigint), public.get_revisions(int, bigint),
  public.add_note(text, text, text, bigint), public.get_notes(text, text), public.delete_note(bigint),
  public.admin_set_staff_subjects(uuid, text[]), public.admin_list_staff(), public.admin_update_staff(uuid, text, text),
  public.staff_send_comm(jsonb), public.staff_list_comms(bigint, jsonb), public.student_inbox(), public.survey_results(bigint),
  public.impact_survey_list(), public.admin_compare_subjects() to authenticated;
-- سياسات RLS تستدعي هذه الدوال بدور المستخدم
grant execute on function public._course_ok(bigint), public._revision_ok(text, bigint) to authenticated;
revoke execute on function public._staff_scoped(), public._require_course(bigint), public._course_subject_name(bigint) from authenticated;
