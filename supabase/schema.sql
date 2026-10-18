-- =====================================================================
-- منصة بنك أسئلة كيمياء 2-1 — هيكل قاعدة البيانات على Supabase
-- يُنفذ مرة واحدة في SQL Editor قبل ملفات البيانات (seed).
-- الأمان: القراءة العامة للبنية والأسئلة دون إجابات؛ الإجابات للمسجلين فقط؛
-- كل التعديلات عبر دوال محمية تتحقق من الدور وتسجل في سجل التعديلات.
-- =====================================================================

-- ---------- الأدوار والملفات الشخصية ----------
create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text not null default '',
  -- كل حساب جديد «بانتظار التفعيل» ولا يرى الإجابات حتى يحدد المشرف دوره (حماية لو بقي التسجيل الذاتي مفعّلًا).
  role text not null default 'pending' check (role in ('admin', 'reviewer', 'viewer', 'supervisor', 'principal', 'student', 'pending')),
  created_at timestamptz not null default now()
);

alter table public.profiles add column if not exists section text;
alter table public.profiles add column if not exists grade text;
-- حساب طالب أنشأه المشرف (لا حساب سجّل نفسه): وحده يظهر في «حسابات الطلاب» ويمكن إدارته
alter table public.profiles add column if not exists managed boolean not null default false;
update public.profiles set managed = true where role = 'student' and not managed;
alter table public.profiles add column if not exists profile_confirmed boolean not null default false;
alter table public.profiles alter column role set default 'pending';
alter table public.profiles drop constraint if exists profiles_role_check;
alter table public.profiles add constraint profiles_role_check check (role in ('admin', 'reviewer', 'viewer', 'supervisor', 'principal', 'student', 'pending'));

-- كل مستخدم جديد في Authentication يحصل على ملف بدور «بانتظار التفعيل».
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  insert into public.profiles (user_id, email, display_name)
  values (new.id, new.email, coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1)))
  on conflict (user_id) do nothing;
  return new;
end $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

create or replace function public.my_role() returns text
language sql stable security definer set search_path = public, pg_temp as $$
  select role from public.profiles where user_id = auth.uid()
$$;
create or replace function public.is_reviewer() returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce((select role in ('reviewer', 'admin') from public.profiles where user_id = auth.uid()), false)
$$;
create or replace function public.is_member() returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select exists (select 1 from public.profiles where user_id = auth.uid() and role in ('viewer', 'reviewer', 'supervisor', 'principal', 'admin'))
$$;
-- الأدوار (2026-10-13):
--   admin      مالك المشروع: كل شيء، وتعديل المحتوى، وإدارة الحسابات.
--   reviewer   مراجع علمي: اعتماد الأهداف والأسئلة وإعادتها، وكتابة الملاحظات؛ لا يعدّل نص المحتوى.
--   viewer     معلم: اطلاع وإنشاء اختبارات ومتابعة تقدم الطلاب.
--   supervisor مشرف تربوي: اطلاع على الأهداف والأسئلة وإنشاء اختبارات ولوحة المؤشرات؛ دون تعديل ولا أسماء طلاب.
--   principal  مدير المدرسة: اطلاع على الأسئلة ولوحة المؤشرات فقط.
create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce((select role = 'admin' from public.profiles where user_id = auth.uid()), false)
$$;

-- ---------- البنية ----------
create table if not exists public.courses (
  id bigint primary key,
  code text not null unique,
  title text not null,
  subject text not null,
  grade text not null,
  term text not null,
  country text not null,
  structure_source text,
  content_source text
);
-- تعدد المقررات (2026-10-13): حالة المقرر وترتيبه في صفحة المقررات
alter table public.courses add column if not exists status text not null default 'ready';
alter table public.courses add column if not exists sort_order int not null default 100;
alter table public.courses add column if not exists eta text;
alter table public.courses drop constraint if exists courses_status_check;
alter table public.courses add constraint courses_status_check check (status in ('ready', 'preparing'));
update public.courses set sort_order = 20 where id = 1 and sort_order = 100;
insert into public.courses (id, code, title, subject, grade, term, country, status, sort_order) values
  (2, 'كيمياء 1', 'الكيمياء 1', 'الكيمياء', 'الأول الثانوي', 'الأول', 'السعودية', 'preparing', 10),
  (3, 'كيمياء 2-2', 'الكيمياء 2-2', 'الكيمياء', 'الثاني الثانوي', 'الثاني', 'السعودية', 'preparing', 30),
  (4, 'كيمياء 3', 'الكيمياء 3', 'الكيمياء', 'الثالث الثانوي', 'الأول', 'السعودية', 'preparing', 40)
on conflict (id) do nothing;

-- المقرر الافتراضي: أول مقرر جاهز في الترتيب (تستعمله الدوال حين لا يُحدد مقرر، فتبقى الواجهة القديمة تعمل)
create or replace function public._default_course() returns bigint
language sql stable security definer set search_path = public, pg_temp as $$
  select id from public.courses order by (status = 'ready') desc, sort_order, id limit 1
$$;

-- إسناد المقررات للطلاب: الطالب يتدرب على المقررات المسندة له فقط
create table if not exists public.course_enrollments (
  user_id uuid not null references public.profiles(user_id) on delete cascade,
  course_id bigint not null references public.courses(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (user_id, course_id)
);
create index if not exists idx_enroll_course on public.course_enrollments(course_id);
alter table public.course_enrollments enable row level security;
revoke all on public.course_enrollments from anon, authenticated;
-- مرة واحدة: الطلاب الحاليون كلهم في كيمياء 2-1 (لا يتكرر بعد أول إسناد)
insert into public.course_enrollments (user_id, course_id)
  select p.user_id, 1 from public.profiles p
  where p.role = 'student' and exists (select 1 from public.courses where id = 1)
    and not exists (select 1 from public.course_enrollments)
on conflict do nothing;

create table if not exists public.chapters (
  id bigint primary key,
  course_id bigint not null references public.courses(id) on delete cascade,
  number int not null,
  title text not null,
  description text,
  unique (course_id, number)
);

create table if not exists public.lessons (
  id bigint primary key,
  chapter_id bigint not null references public.chapters(id) on delete cascade,
  number int not null,
  title text not null,
  summary text,
  source_note text,
  unique (chapter_id, number)
);

-- الهدف الأصلي لا يُعدّل: الصياغة المقترحة والمعتمدة في حقول مستقلة.
create table if not exists public.objectives (
  id bigint primary key,
  lesson_id bigint not null references public.lessons(id) on delete cascade,
  code text not null unique,
  original_code text,
  number int not null,
  original_text text not null,
  proposed_text text,
  split_into jsonb not null default '[]',
  approved_text text,
  revision_reason text,
  revision_type text,
  ai_review_status text,
  thinking_level text,
  knowledge_type text,
  concepts jsonb not null default '[]',
  source_page int,
  memo_pages jsonb not null default '[]',
  memo_coverage text,
  memo_note text,
  duplicate_of text,
  review_status text not null default 'pending' check (review_status in ('pending', 'approved', 'returned')),
  reviewed_by uuid,
  reviewed_at timestamptz,
  required_mcq int not null default 7,
  required_essay int not null default 3
);

create table if not exists public.supplements (
  objective_id bigint primary key references public.objectives(id) on delete cascade,
  memo_basis text,
  supplement text not null,
  key_points jsonb not null default '[]',
  misconceptions jsonb not null default '[]',
  scientific_notes text,
  confidence text,
  origin text not null default 'ai_agent',
  review_status text not null default 'pending' check (review_status in ('pending', 'approved', 'returned'))
);

-- الأسئلة: الحقول العامة هنا، والإجابات في جدول منفصل محمي.
create table if not exists public.questions (
  id bigint generated by default as identity primary key,
  objective_id bigint not null references public.objectives(id) on delete cascade,
  type text not null check (type in ('mcq', 'essay')),
  number int not null,
  stem text not null,
  stimulus jsonb,
  options jsonb,
  thinking_level text,
  question_kind text,
  difficulty text check (difficulty in ('سهل', 'متوسط', 'صعب')),
  source_ref text,
  status text not null default 'generated' check (status in ('generated', 'in_review', 'needs_revision', 'approved')),
  excluded boolean not null default false,
  origin text not null default 'ai_generated',
  reviewed_by uuid,
  reviewed_at timestamptz,
  updated_at timestamptz not null default now()
);
create index if not exists idx_q_obj on public.questions(objective_id);

create table if not exists public.question_answers (
  question_id bigint primary key references public.questions(id) on delete cascade,
  correct_index int,
  explanation text,
  distractor_notes jsonb,
  model_answer text,
  answer_elements jsonb,
  solution_steps jsonb,
  marks jsonb,
  rubric jsonb,
  common_errors jsonb,
  auto_check jsonb,
  reviewer_notes text
);

create table if not exists public.revisions (
  id bigint generated by default as identity primary key,
  entity text not null,
  entity_id bigint not null,
  action text not null,
  before_json jsonb,
  after_json jsonb,
  note text,
  user_id uuid,
  user_name text,
  at timestamptz not null default now()
);
create index if not exists idx_rev_entity on public.revisions(entity, entity_id);

-- ---------- أمان مستوى الصفوف ----------
-- (الوصول للمحتوى كله مقصور على الحسابات المفعّلة: viewer و reviewer و admin)
alter table public.profiles enable row level security;
alter table public.courses enable row level security;
alter table public.chapters enable row level security;
alter table public.lessons enable row level security;
alter table public.objectives enable row level security;
alter table public.supplements enable row level security;
alter table public.questions enable row level security;
alter table public.question_answers enable row level security;
alter table public.revisions enable row level security;

drop policy if exists profiles_self on public.profiles;
create policy profiles_self on public.profiles for select to authenticated using (user_id = auth.uid() or public.is_reviewer());

drop policy if exists courses_read on public.courses;
create policy courses_read on public.courses for select to authenticated using (public.is_member());
drop policy if exists chapters_read on public.chapters;
create policy chapters_read on public.chapters for select to authenticated using (public.is_member());
drop policy if exists lessons_read on public.lessons;
create policy lessons_read on public.lessons for select to authenticated using (public.is_member());
drop policy if exists objectives_read on public.objectives;
create policy objectives_read on public.objectives for select to authenticated using (public.is_member());
drop policy if exists supplements_read on public.supplements;
create policy supplements_read on public.supplements for select to authenticated using (public.is_member());
-- الأسئلة المستبعدة لا يراها إلا المراجع
drop policy if exists questions_read on public.questions;
create policy questions_read on public.questions for select to authenticated using (public.is_member() and (not excluded or public.is_reviewer()));
-- الإجابات للمستخدمين المسجلين فقط (المعلمون والمراجعون)
drop policy if exists answers_read on public.question_answers;
create policy answers_read on public.question_answers for select to authenticated using (public.is_member());
drop policy if exists revisions_read on public.revisions;
create policy revisions_read on public.revisions for select to authenticated using (public.is_reviewer());

-- لا توجد سياسات insert/update/delete: الكتابة المباشرة ممنوعة، وتتم عبر الدوال أدناه فقط.
revoke all on all tables in schema public from anon, authenticated;
grant usage on schema public to anon, authenticated;
-- المنصة مغلقة: لا يقرأ البيانات إلا حساب مفعّل؛ الزائر (anon) لا يملك أي صلاحية قراءة.
grant select on public.courses, public.chapters, public.lessons, public.objectives, public.supplements, public.questions to authenticated;
grant select on public.question_answers, public.revisions, public.profiles to authenticated;

-- ---------- دوال مساعدة ----------
create or replace function public._log(p_entity text, p_id bigint, p_action text, p_before jsonb, p_after jsonb, p_note text)
returns void language sql security definer set search_path = public, pg_temp as $$
  insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_id, user_name)
  values (p_entity, p_id, p_action, p_before, p_after, nullif(trim(coalesce(p_note, '')), ''), auth.uid(),
          (select display_name from public.profiles where user_id = auth.uid()));
$$;

create or replace function public._require_reviewer() returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if auth.uid() is null then raise exception 'يلزم تسجيل الدخول' using errcode = '28000'; end if;
  if not public.is_reviewer() then raise exception 'لا تملك صلاحية تنفيذ هذا الإجراء' using errcode = '42501'; end if;
end $$;

create or replace function public._require_admin() returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if auth.uid() is null then raise exception 'يلزم تسجيل الدخول' using errcode = '28000'; end if;
  if not public.is_admin() then raise exception 'تعديل المحتوى لمالك المشروع فقط؛ اكتب ملاحظتك بدلًا من ذلك' using errcode = '42501'; end if;
end $$;

create or replace function public._require_member() returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if auth.uid() is null then raise exception 'يلزم تسجيل الدخول' using errcode = '28000'; end if;
  if not public.is_member() then raise exception 'حسابك بانتظار التفعيل من المشرف' using errcode = '42501'; end if;
end $$;

-- ---------- التدريب الفوري: تصحيح إجابة دون كشف بقية الإجابات ----------
create or replace function public.check_answer(p_question bigint, p_choice int) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare r record;
begin
  perform public._require_member();
  if p_choice is null or p_choice < 0 or p_choice > 3 then raise exception 'اختيار غير صالح'; end if;
  select q.id, a.correct_index, a.explanation, a.distractor_notes into r
    from public.questions q join public.question_answers a on a.question_id = q.id
    where q.id = p_question and q.type = 'mcq' and not q.excluded and p_choice < jsonb_array_length(q.options);
  if not found then raise exception 'السؤال غير موجود أو الاختيار غير صالح'; end if;
  return jsonb_build_object('correct', p_choice = r.correct_index, 'correctIndex', r.correct_index,
    'explanation', r.explanation, 'distractorNote', nullif(r.distractor_notes->>p_choice, ''));
end $$;

-- ---------- الأهداف ----------
create or replace function public.review_objective(p_code text, p_action text, p_approved_text text default null, p_note text default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; v_status text; v_text text;
begin
  perform public._require_reviewer();
  select * into o from public.objectives where code = p_code;
  if not found then raise exception 'الهدف غير موجود'; end if;
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

create or replace function public.patch_objective(p_code text, p jsonb)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; v_text text;
begin
  perform public._require_admin();
  select * into o from public.objectives where code = p_code;
  if not found then raise exception 'الهدف غير موجود'; end if;
  if p ? 'approved_text' then
    v_text := regexp_replace(trim(coalesce(p->>'approved_text', '')), '\s+', ' ', 'g');
    if length(v_text) < 8 then raise exception 'صياغة الهدف قصيرة جدًا'; end if;
  end if;
  if p->>'thinking_level' is not null and p->>'thinking_level' not in ('تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع') then raise exception 'مستوى التفكير غير صالح'; end if;
  if (p ? 'required_mcq' and coalesce((p->>'required_mcq')::int, -1) not between 0 and 30)
     or (p ? 'required_essay' and coalesce((p->>'required_essay')::int, -1) not between 0 and 30) then raise exception 'العدد المطلوب من الأسئلة غير صالح'; end if;
  update public.objectives set
    approved_text = case when p ? 'approved_text' then v_text else approved_text end,
    thinking_level = case when p ? 'thinking_level' then p->>'thinking_level' else thinking_level end,
    knowledge_type = case when p ? 'knowledge_type' then p->>'knowledge_type' else knowledge_type end,
    concepts = case when jsonb_typeof(p->'concepts') = 'array' then p->'concepts' else concepts end,
    required_mcq = coalesce((p->>'required_mcq')::int, required_mcq),
    required_essay = coalesce((p->>'required_essay')::int, required_essay)
  where id = o.id;
  perform public._log('objective', o.id, 'edit', public._objective_json(o), p, null);
end $$;

create or replace function public.review_supplement(p_code text, p_action text, p_supplement text default null, p_note text default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; s public.supplements; v_status text; v_text text;
begin
  perform public._require_reviewer();
  select * into o from public.objectives where code = p_code;
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

-- ---------- الأسئلة ----------
-- التحقق من الحقول قبل الحفظ (نفس قواعد الخادم).
create or replace function public._validate_question(p_type text, p jsonb) returns void
language plpgsql immutable as $$
declare errs text[] := '{}';
begin
  if length(trim(coalesce(p->>'stem', ''))) < 8 then errs := array_append(errs, 'نص السؤال قصير جدًا'); end if;
  if p ? 'difficulty' and p->>'difficulty' is not null and p->>'difficulty' not in ('سهل', 'متوسط', 'صعب') then errs := array_append(errs, 'درجة الصعوبة غير صالحة'); end if;
  if p ? 'thinking_level' and p->>'thinking_level' is not null and p->>'thinking_level' not in ('تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع') then errs := array_append(errs, 'مستوى التفكير غير صالح'); end if;
  if p_type = 'mcq' then
    -- ثلاثة بدائل (أ ب ج) أو أربعة (أ ب ج د) حسب المقرر
    if jsonb_typeof(p->'options') is distinct from 'array' or jsonb_array_length(p->'options') not in (3, 4) then errs := array_append(errs, 'يجب أن يكون لسؤال الاختيار ثلاثة بدائل أو أربعة');
    elsif exists (select 1 from jsonb_array_elements_text(p->'options') x where trim(x) = '') then errs := array_append(errs, 'لا يجوز ترك بديل فارغ'); end if;
    if coalesce((p->>'correct_index')::int, -1) < 0 or coalesce((p->>'correct_index')::int, -1) >= coalesce(jsonb_array_length(case when jsonb_typeof(p->'options') = 'array' then p->'options' end), 3) then errs := array_append(errs, 'حدد الإجابة الصحيحة'); end if;
    if trim(coalesce(p->>'explanation', '')) = '' then errs := array_append(errs, 'تفسير الإجابة الصحيحة مطلوب'); end if;
  else
    if trim(coalesce(p->>'model_answer', '')) = '' then errs := array_append(errs, 'الإجابة النموذجية مطلوبة'); end if;
    if coalesce(jsonb_array_length(case when jsonb_typeof(p->'marks') = 'array' then p->'marks' end), 0) = 0 then errs := array_append(errs, 'توزيع الدرجات مطلوب'); end if;
    if coalesce(jsonb_array_length(case when jsonb_typeof(p->'rubric') = 'array' then p->'rubric' end), 0) = 0 then errs := array_append(errs, 'سلم التصحيح مطلوب'); end if;
  end if;
  if array_length(errs, 1) > 0 then raise exception '%', array_to_string(errs, '؛ ') using errcode = '22023'; end if;
end $$;

create or replace function public._question_json(p_id bigint) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select to_jsonb(q) || coalesce(to_jsonb(a) - 'question_id', '{}'::jsonb)
  from public.questions q left join public.question_answers a on a.question_id = q.id where q.id = p_id
$$;

create or replace function public.update_question(p_id bigint, p jsonb, p_auto_check jsonb default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare q public.questions; v_before jsonb;
begin
  perform public._require_admin();
  select * into q from public.questions where id = p_id;
  if not found then raise exception 'السؤال غير موجود'; end if;
  perform public._validate_question(q.type, p);
  v_before := public._question_json(p_id);
  -- أي تعديل بشري ينقل السؤال إلى «قيد المراجعة»
  update public.questions set stem = trim(p->>'stem'), stimulus = nullif(p->'stimulus', 'null'::jsonb),
    options = case when q.type = 'mcq' then p->'options' else options end,
    thinking_level = p->>'thinking_level', question_kind = p->>'question_kind', difficulty = p->>'difficulty',
    source_ref = p->>'source_ref',
    status = case when status in ('approved', 'generated') then 'in_review' else status end, updated_at = now()
  where id = p_id;
  update public.question_answers set
    correct_index = case when q.type = 'mcq' then (p->>'correct_index')::int else correct_index end,
    explanation = case when q.type = 'mcq' then p->>'explanation' else explanation end,
    distractor_notes = case when q.type = 'mcq' then p->'distractor_notes' else distractor_notes end,
    model_answer = case when q.type = 'essay' then p->>'model_answer' else model_answer end,
    answer_elements = case when q.type = 'essay' then p->'answer_elements' else answer_elements end,
    solution_steps = case when q.type = 'essay' then p->'solution_steps' else solution_steps end,
    marks = case when q.type = 'essay' then p->'marks' else marks end,
    rubric = case when q.type = 'essay' then p->'rubric' else rubric end,
    common_errors = case when q.type = 'essay' then p->'common_errors' else common_errors end,
    auto_check = coalesce(p_auto_check, auto_check),
    reviewer_notes = case when p ? 'reviewer_notes' then p->>'reviewer_notes' else reviewer_notes end
  where question_id = p_id;
  perform public._log('question', p_id, 'edit', v_before, p, null);
end $$;

create or replace function public.create_question(p_code text, p_type text, p jsonb, p_auto_check jsonb default null)
returns bigint language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; v_id bigint; v_num int;
begin
  perform public._require_admin();
  select * into o from public.objectives where code = p_code;
  if not found then raise exception 'الهدف غير موجود'; end if;
  if p_type not in ('mcq', 'essay') then raise exception 'نوع غير صالح'; end if;
  perform public._validate_question(p_type, p);
  select coalesce(max(number), 0) + 1 into v_num from public.questions where objective_id = o.id and type = p_type;
  insert into public.questions (objective_id, type, number, stem, stimulus, options, thinking_level, question_kind, difficulty, source_ref, status, origin)
  values (o.id, p_type, v_num, trim(p->>'stem'), nullif(p->'stimulus', 'null'::jsonb), case when p_type = 'mcq' then p->'options' end,
    p->>'thinking_level', p->>'question_kind', p->>'difficulty', p->>'source_ref', 'in_review', 'human')
  returning id into v_id;
  insert into public.question_answers (question_id, correct_index, explanation, distractor_notes, model_answer, answer_elements, solution_steps, marks, rubric, common_errors, auto_check)
  values (v_id, (p->>'correct_index')::int, p->>'explanation', p->'distractor_notes', p->>'model_answer', p->'answer_elements',
    p->'solution_steps', p->'marks', p->'rubric', p->'common_errors', p_auto_check);
  perform public._log('question', v_id, 'create', null, p, null);
  return v_id;
end $$;

create or replace function public.set_question_status(p_id bigint, p_status text, p_note text default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare q public.questions; a public.question_answers;
begin
  perform public._require_reviewer();
  select * into q from public.questions where id = p_id;
  if not found then raise exception 'السؤال غير موجود'; end if;
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

create or replace function public.exclude_question(p_id bigint, p_excluded boolean, p_note text default null)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare q public.questions;
begin
  perform public._require_admin();
  select * into q from public.questions where id = p_id;
  if not found then raise exception 'السؤال غير موجود'; end if;
  if p_excluded and coalesce(trim(p_note), '') = '' then raise exception 'اكتب سبب الاستبعاد'; end if;
  update public.questions set excluded = p_excluded where id = p_id;
  perform public._log('question', p_id, case when p_excluded then 'exclude' else 'restore' end,
    jsonb_build_object('excluded', q.excluded), jsonb_build_object('excluded', p_excluded), p_note);
end $$;

create or replace function public.duplicate_question(p_id bigint, p_auto_check jsonb default null)
returns bigint language plpgsql security definer set search_path = public, pg_temp as $$
declare q public.questions; v_id bigint; v_num int;
begin
  perform public._require_admin();
  select * into q from public.questions where id = p_id;
  if not found then raise exception 'السؤال غير موجود'; end if;
  select max(number) + 1 into v_num from public.questions where objective_id = q.objective_id and type = q.type;
  insert into public.questions (objective_id, type, number, stem, stimulus, options, thinking_level, question_kind, difficulty, source_ref, status, origin)
  select objective_id, type, v_num, stem, stimulus, options, thinking_level, question_kind, difficulty, source_ref, 'in_review', 'human'
    from public.questions where id = p_id returning id into v_id;
  insert into public.question_answers (question_id, correct_index, explanation, distractor_notes, model_answer, answer_elements, solution_steps, marks, rubric, common_errors, auto_check)
  select v_id, correct_index, explanation, distractor_notes, model_answer, answer_elements, solution_steps, marks, rubric, common_errors, p_auto_check
    from public.question_answers where question_id = p_id;
  perform public._log('question', v_id, 'duplicate', null, jsonb_build_object('from', p_id), null);
  return v_id;
end $$;

-- ---------- المؤشرات (تُحسب من البيانات الفعلية) ----------
drop function if exists public._stats_data();
create or replace function public._stats_data(p_course bigint default null) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  with crs as (select coalesce(p_course, public._default_course()) id),
  ch as (select * from public.chapters where course_id = (select id from crs)),
  ls as (select * from public.lessons where chapter_id in (select id from ch)),
  o as (select * from public.objectives where lesson_id in (select id from ls)),
  q as (select * from public.questions where not excluded and objective_id in (select id from o)),
  cov as (
    select ob.id, ob.required_mcq, ob.required_essay,
      count(qq.id) filter (where qq.type = 'mcq') mcq, count(qq.id) filter (where qq.type = 'essay') essay,
      count(qq.id) filter (where qq.type = 'mcq' and qq.status = 'approved') amcq,
      count(qq.id) filter (where qq.type = 'essay' and qq.status = 'approved') aessay
    from o ob left join q qq on qq.objective_id = ob.id group by ob.id, ob.required_mcq, ob.required_essay)
  select jsonb_build_object(
    'course', (select to_jsonb(c) from public.courses c where c.id = (select id from crs)),
    'chapters', (select count(*) from ch),
    'lessons', (select count(*) from ls),
    'objectives', (select jsonb_build_object('n', count(*), 'reviewed', count(*) filter (where review_status <> 'pending'),
        'approved', count(*) filter (where review_status = 'approved'), 'returned', count(*) filter (where review_status = 'returned')) from o),
    'questions', (select jsonb_build_object('mcq', count(*) filter (where type = 'mcq'), 'essay', count(*) filter (where type = 'essay'),
        'reviewed', count(*) filter (where status <> 'generated'), 'approved', count(*) filter (where status = 'approved'),
        'needs_revision', count(*) filter (where status = 'needs_revision'), 'n', count(*)) from q),
    'levels', (select coalesce(jsonb_agg(jsonb_build_object('level', level, 'n', n) order by n desc), '[]') from
        (select coalesce(thinking_level, 'غير مصنف') level, count(*) n from o group by 1) t),
    'coverage', (select jsonb_build_object('complete', count(*) filter (where mcq >= required_mcq and essay >= required_essay),
        'approved_complete', count(*) filter (where amcq >= required_mcq and aessay >= required_essay),
        'started', count(*) filter (where mcq + essay > 0)) from cov),
    'byChapter', (select coalesce(jsonb_agg(jsonb_build_object('number', c.number, 'title', c.title, 'questions',
        (select count(*) from q join o ob on ob.id = q.objective_id join ls l2 on l2.id = ob.lesson_id where l2.chapter_id = c.id)) order by c.number), '[]')
        from ch c),
    'supplements', (select jsonb_build_object('n', count(*), 'approved', count(*) filter (where review_status = 'approved'))
        from public.supplements where objective_id in (select id from o))
  )
$$;

grant execute on function public.my_role(), public.is_reviewer(), public.is_member(),
  public.review_objective(text, text, text, text), public.patch_objective(text, jsonb),
  public.review_supplement(text, text, text, text), public.update_question(bigint, jsonb, jsonb),
  public.create_question(text, text, jsonb, jsonb), public.set_question_status(bigint, text, text),
  public.exclude_question(bigint, boolean, text), public.duplicate_question(bigint, jsonb) to authenticated;
revoke execute on function public._log(text, bigint, text, jsonb, jsonb, text), public._require_reviewer(),
  public._question_json(bigint), public.handle_new_user() from anon, authenticated, public;

-- =====================================================================
-- دوال القراءة: ترجع نفس شكل JSON الذي كانت ترجعه الواجهة البرمجية المحلية.
-- الإجابات تُضمَّن فقط للمستخدم المسجل (is_member)، والمستبعد لا يظهر إلا للمراجع.
-- =====================================================================
create or replace function public._objective_json(o public.objectives) returns jsonb
language sql stable as $$
  select jsonb_build_object('id', o.id, 'code', o.code, 'originalCode', o.original_code, 'number', o.number,
    'originalText', o.original_text, 'proposedText', o.proposed_text, 'splitInto', o.split_into,
    'approvedText', o.approved_text, 'revisionReason', o.revision_reason, 'revisionType', o.revision_type,
    'aiReviewStatus', o.ai_review_status, 'thinkingLevel', o.thinking_level, 'knowledgeType', o.knowledge_type,
    'concepts', o.concepts, 'memoPages', o.memo_pages, 'memoCoverage', o.memo_coverage, 'memoNote', o.memo_note,
    'duplicateOf', o.duplicate_of, 'reviewStatus', o.review_status, 'reviewedAt', o.reviewed_at,
    'requiredMcq', o.required_mcq, 'requiredEssay', o.required_essay)
$$;

create or replace function public._q_public(q public.questions, a public.question_answers, p_answers boolean) returns jsonb
language sql stable as $$
  select jsonb_build_object('id', q.id, 'objectiveId', q.objective_id, 'type', q.type, 'number', q.number, 'stem', q.stem,
    'stimulus', q.stimulus, 'options', coalesce(q.options, '[]'), 'thinkingLevel', q.thinking_level,
    'questionKind', q.question_kind, 'difficulty', q.difficulty, 'sourceRef', q.source_ref,
    'status', q.status, 'excluded', q.excluded, 'origin', q.origin)
  || case when p_answers then jsonb_build_object('correctIndex', a.correct_index, 'explanation', a.explanation,
    'distractorNotes', coalesce(a.distractor_notes, '[]'), 'modelAnswer', a.model_answer,
    'answerElements', coalesce(a.answer_elements, '[]'), 'solutionSteps', coalesce(a.solution_steps, '[]'),
    'marks', coalesce(a.marks, '[]'), 'rubric', coalesce(a.rubric, '[]'), 'commonErrors', coalesce(a.common_errors, '[]'),
    'autoCheck', a.auto_check, 'reviewerNotes', a.reviewer_notes, 'reviewedAt', q.reviewed_at, 'updatedAt', q.updated_at)
  else '{}'::jsonb end
$$;

drop function if exists public._chapters_data();
create or replace function public._chapters_data(p_course bigint default null) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce(jsonb_agg(to_jsonb(c) || jsonb_build_object(
    'lessons', (select count(*) from lessons l where l.chapter_id = c.id),
    'objectives', (select count(*) from objectives o join lessons l on l.id = o.lesson_id where l.chapter_id = c.id),
    'approved', (select count(*) filter (where o.review_status = 'approved') from objectives o join lessons l on l.id = o.lesson_id where l.chapter_id = c.id),
    'reviewed', (select count(*) filter (where o.review_status <> 'pending') from objectives o join lessons l on l.id = o.lesson_id where l.chapter_id = c.id),
    'questions', (select count(*) from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id
       where l.chapter_id = c.id and not q.excluded)) order by c.number), '[]')
  from chapters c where c.course_id = coalesce(p_course, public._default_course())
$$;

drop function if exists public.get_chapter(int);
create or replace function public.get_chapter(p_number int, p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare c public.chapters;
begin
  perform public._require_member();
  select * into c from chapters where number = p_number and course_id = coalesce(p_course, public._default_course());
  if not found then raise exception 'الفصل غير موجود' using errcode = 'P0002'; end if;
  return to_jsonb(c) || jsonb_build_object('lessons', (select coalesce(jsonb_agg(to_jsonb(l) || jsonb_build_object('objectives',
    (select coalesce(jsonb_agg(public._objective_json(o) || jsonb_build_object(
        'mcq', (select count(*) from questions q where q.objective_id = o.id and q.type = 'mcq' and not q.excluded),
        'essay', (select count(*) from questions q where q.objective_id = o.id and q.type = 'essay' and not q.excluded)) order by o.number), '[]')
     from objectives o where o.lesson_id = l.id)) order by l.number), '[]') from lessons l where l.chapter_id = c.id));
end $$;

create or replace function public.get_objective(p_code text) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
-- المعلم لا يرى الإجابات في صفحة الهدف؛ يصله مفتاح الإجابة مع الاختبار الذي ينشئه (get_exam_answers)
declare o public.objectives; l public.lessons; c public.chapters; s public.supplements;
  v_ans boolean := public.is_member() and coalesce(public.my_role(), '') <> 'viewer'; v_rev boolean := public.is_reviewer();
begin
  perform public._require_member();
  select * into o from objectives where code = p_code;
  if not found then raise exception 'الهدف غير موجود' using errcode = 'P0002'; end if;
  select * into l from lessons where id = o.lesson_id;
  select * into c from chapters where id = l.chapter_id;
  select * into s from supplements where objective_id = o.id;
  return jsonb_build_object(
    'objective', public._objective_json(o) || jsonb_build_object('lesson', jsonb_build_object('number', l.number, 'title', l.title),
       'chapter', jsonb_build_object('number', c.number, 'title', c.title), 'courseId', c.course_id),
    'supplement', case when s.objective_id is null then null else jsonb_build_object('memoBasis', s.memo_basis, 'supplement', s.supplement,
       'keyPoints', s.key_points, 'misconceptions', s.misconceptions, 'scientificNotes', s.scientific_notes,
       'confidence', s.confidence, 'origin', s.origin, 'reviewStatus', s.review_status) end,
    'questions', (select coalesce(jsonb_agg(public._q_public(q, a, v_ans) order by q.type desc, q.number), '[]')
       from questions q left join question_answers a on a.question_id = q.id where q.objective_id = o.id and (v_rev or not q.excluded)),
    'lessonNav', (select jsonb_agg(code order by number) from objectives where lesson_id = o.lesson_id),
    'answersIncluded', v_ans);
end $$;

-- بنك الأسئلة مع التصفية؛ الفلاتر اختيارية: chapter, lesson, objective, type, level, difficulty, status, q, excluded
create or replace function public.get_bank(f jsonb default '{}') returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_ans boolean := public.is_member() and not public._restricted(); v_rev boolean := public.is_reviewer();
begin
  perform public._require_member();
  -- البنك كاملًا بإجاباته لمالك المشروع والمراجع فقط؛ غيرهما يستلم الأسئلة دون إجابات
  return (select coalesce(jsonb_agg(public._q_public(q, a, v_ans) || jsonb_build_object('objectiveCode', o.code,
      'objectiveText', coalesce(o.approved_text, o.original_text),
      'lesson', jsonb_build_object('number', l.number, 'title', l.title),
      'chapter', jsonb_build_object('number', c.number, 'title', c.title))
      order by c.number, l.number, o.number, q.type desc, q.number), '[]')
    from questions q left join question_answers a on a.question_id = q.id
      join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id join chapters c on c.id = l.chapter_id
    where c.course_id = coalesce((f->>'course')::bigint, public._default_course())
      and (f->>'chapter' is null or c.number = (f->>'chapter')::int)
      and (f->>'lesson' is null or l.number = (f->>'lesson')::int)
      and (f->>'objective' is null or o.code = f->>'objective')
      and (f->>'type' is null or q.type = f->>'type')
      and (f->>'level' is null or q.thinking_level = f->>'level')
      and (f->>'difficulty' is null or q.difficulty = f->>'difficulty')
      and (f->>'status' is null or q.status = f->>'status')
      and (f->>'q' is null or position(f->>'q' in q.stem) > 0 or position(f->>'q' in coalesce(q.options::text, '')) > 0)
      and (not q.excluded or (v_rev and f->>'excluded' = '1')));
end $$;

create or replace function public.get_question(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  return (select public._q_public(q, a, true) from questions q left join question_answers a on a.question_id = q.id where q.id = p_id);
end $$;

create or replace function public.get_revisions(p_limit int default 100, p_question bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', r.id, 'entity', r.entity, 'entity_id', r.entity_id, 'action', r.action,
      'note', r.note, 'at', r.at, 'user', r.user_name, 'before_json', r.before_json, 'after_json', r.after_json) order by r.id desc), '[]')
    from (select * from revisions where p_question is null or (entity = 'question' and entity_id = p_question)
          order by id desc limit least(greatest(coalesce(p_limit, 100), 1), 500)) r);
end $$;

create or replace function public.get_me() returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select case when auth.uid() is null then null else
    (select jsonb_build_object('id', user_id, 'username', split_part(coalesce((select u.email from auth.users u where u.id = profiles.user_id), email), '@', 1), 'displayName', display_name, 'role', role,
       'section', section, 'grade', grade, 'profileConfirmed', profile_confirmed,
       -- مقررات الطالب المسندة (الجاهزة) لعرضها في الترويسة
       'courses', (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'code', c.code, 'grade', c.grade, 'term', c.term) order by c.sort_order), '[]')
         from course_enrollments e join courses c on c.id = e.course_id and c.status = 'ready' where e.user_id = profiles.user_id))
     from profiles where user_id = auth.uid()) end
$$;

grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.get_question(bigint), public.get_revisions(int, bigint) to authenticated;

-- حفظ نتيجة التحقق الآلي فقط (بعد الإنشاء أو النسخ)؛ لا يغير محتوى السؤال ولا حالته.
create or replace function public.set_auto_check(p_id bigint, p_auto_check jsonb) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  if jsonb_typeof(p_auto_check->'passed') is distinct from 'boolean' then raise exception 'نتيجة تحقق غير صالحة'; end if;
  update public.question_answers set auto_check = p_auto_check where question_id = p_id;
end $$;
grant execute on function public.set_auto_check(bigint, jsonb) to authenticated;

-- =====================================================================
-- إغلاق المنصة: المحتوى للحسابات المفعّلة فقط.
-- =====================================================================
drop function if exists public.get_stats();
create or replace function public.get_stats(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  return public._stats_data(p_course);
end $$;

drop function if exists public.get_chapters();
create or replace function public.get_chapters(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  return public._chapters_data(p_course);
end $$;

-- سحب أي صلاحية سابقة من الزائر (Supabase يمنح anon تنفيذ الدوال الجديدة افتراضيًا).
revoke select on all tables in schema public from anon;
revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.check_answer(bigint, int), public.get_stats(bigint), public.get_chapters(bigint), public.get_chapter(int, bigint),
  public.get_objective(text), public.get_bank(jsonb) to authenticated;
-- الدوال الداخلية لا تُستدعى من الواجهة
revoke execute on function public._stats_data(bigint), public._chapters_data(bigint), public._default_course(), public._require_member(), public._require_reviewer(),
  public._log(text, bigint, text, jsonb, jsonb, text), public._question_json(bigint), public.handle_new_user() from authenticated;

-- =====================================================================
-- حساب الطالب: تدريب فقط. الطالب لا يمر بـ is_member فلا يصل إلى أي دالة للمعلمين،
-- ويرى السؤال دون إجابته حتى يجيب، سؤالًا سؤالًا، داخل جلسة تدريب مسجلة باسمه.
-- =====================================================================
create or replace function public.is_student() returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce((select role = 'student' from public.profiles where user_id = auth.uid()), false)
$$;
create or replace function public._require_student() returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if auth.uid() is null then raise exception 'يلزم تسجيل الدخول' using errcode = '28000'; end if;
  if not public.is_student() then raise exception 'هذه الصفحة لحسابات الطلاب' using errcode = '42501'; end if;
end $$;
create or replace function public._level_group(p text) returns text
language sql immutable as $$
  select case when p in ('تذكر', 'فهم') then 'basic' when p = 'تطبيق' then 'apply' else 'higher' end
$$;

create table if not exists public.practice_sessions (
  id bigint generated by default as identity primary key,
  user_id uuid not null references public.profiles(user_id) on delete cascade,
  created_at timestamptz not null default now(),
  finished_at timestamptz,
  settings jsonb not null default '{}',
  question_ids bigint[] not null,
  time_limit_sec int,
  score int,
  total int not null
);
create index if not exists idx_ps_user on public.practice_sessions(user_id, created_at desc);
create table if not exists public.practice_answers (
  session_id bigint not null references public.practice_sessions(id) on delete cascade,
  question_id bigint not null references public.questions(id) on delete cascade,
  choice int not null,
  correct boolean not null,
  answered_at timestamptz not null default now(),
  primary key (session_id, question_id)
);
alter table public.practice_sessions enable row level security;
alter table public.practice_answers enable row level security;
-- لا قراءة ولا كتابة مباشرة؛ كل شيء عبر الدوال أدناه.
revoke all on public.practice_sessions, public.practice_answers from anon, authenticated;

-- الطالب يؤكد اسمه وشعبته مرة واحدة عند أول دخول؛ بعدها يعدّلهما المشرف فقط.
create or replace function public.student_confirm_profile(p_name text, p_section text) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
declare pr public.profiles;
begin
  perform public._require_student();
  select * into pr from public.profiles where user_id = auth.uid();
  if pr.profile_confirmed then raise exception 'البيانات مثبتة؛ تواصل مع المشرف لتعديلها'; end if;
  if length(trim(coalesce(p_name, ''))) < 3 then raise exception 'اكتب اسمك كاملًا'; end if;
  if pr.section is null and length(trim(coalesce(p_section, ''))) < 1 then raise exception 'اكتب الشعبة'; end if;
  -- الشعبة التي حددها المشرف تبقى كما هي؛ يكتبها الطالب فقط إن لم تُحدد
  update public.profiles set display_name = trim(p_name), section = coalesce(section, trim(p_section)), profile_confirmed = true where user_id = auth.uid();
end $$;

-- الدروس المتاحة للتدريب مع عدد أسئلة الاختيار المعتمدة في كل مجموعة مستوى.
create or replace function public.student_catalog() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_student();
  -- فصول المقررات المسندة للطالب فقط (والجاهزة)، مرتبة حسب المقرر ثم الفصل
  return (select coalesce(jsonb_agg(jsonb_build_object('number', c.number, 'title', c.title, 'course', cr.code, 'courseId', cr.id, 'lessons',
    (select coalesce(jsonb_agg(jsonb_build_object('id', l.id, 'number', l.number, 'title', l.title,
        'basic', (select count(*) from questions q join objectives o on o.id = q.objective_id where o.lesson_id = l.id and q.type = 'mcq' and q.status = 'approved' and not q.excluded and public._level_group(q.thinking_level) = 'basic'),
        'apply', (select count(*) from questions q join objectives o on o.id = q.objective_id where o.lesson_id = l.id and q.type = 'mcq' and q.status = 'approved' and not q.excluded and public._level_group(q.thinking_level) = 'apply'),
        'higher', (select count(*) from questions q join objectives o on o.id = q.objective_id where o.lesson_id = l.id and q.type = 'mcq' and q.status = 'approved' and not q.excluded and public._level_group(q.thinking_level) = 'higher'),
        'answered', (select count(*) from practice_answers a join practice_sessions s on s.id = a.session_id join questions q on q.id = a.question_id join objectives o on o.id = q.objective_id
                     where s.user_id = auth.uid() and o.lesson_id = l.id),
        'correct', (select count(*) filter (where a.correct) from practice_answers a join practice_sessions s on s.id = a.session_id join questions q on q.id = a.question_id join objectives o on o.id = q.objective_id
                     where s.user_id = auth.uid() and o.lesson_id = l.id)) order by l.number), '[]')
     from lessons l where l.chapter_id = c.id)) order by cr.sort_order, c.number), '[]')
    from chapters c join courses cr on cr.id = c.course_id and cr.status = 'ready'
    where exists (select 1 from course_enrollments e where e.user_id = auth.uid() and e.course_id = c.course_id));
end $$;

-- السؤال كما يراه الطالب: دون الإجابة ولا التفسير ولا أي بيانات مراجعة.
create or replace function public._student_q(q public.questions) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select jsonb_build_object('id', q.id, 'stem', q.stem, 'stimulus', q.stimulus, 'options', q.options,
    'group', public._level_group(q.thinking_level), 'difficulty', q.difficulty,
    'lesson', (select l.title from objectives o join lessons l on l.id = o.lesson_id where o.id = q.objective_id))
$$;

-- بدء جلسة: p = {lessons:[id], count, levels:'graded'|'basic'|'apply'|'higher', timed:bool, retry:session_id}
create or replace function public.student_start(p jsonb) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_count int; v_levels text; v_ids bigint[] := '{}'; v_lessons bigint[]; v_retry bigint; v_limit int; v_sid bigint; v_today int;
  v_wrong bigint[]; v_alts bigint[] := '{}'; v_alt bigint; w record; v_timed boolean := coalesce((p->>'timed')::boolean, false);
  v_basic int; v_apply int; v_higher int;
begin
  perform public._require_student();
  -- قفل لكل طالب حتى لا تتجاوز الطلبات المتزامنة الحد اليومي
  perform pg_advisory_xact_lock(hashtext('practice:' || auth.uid()::text));
  select count(*) into v_today from practice_sessions where user_id = auth.uid() and created_at > now() - interval '1 day';
  if v_today >= 40 then raise exception 'وصلت إلى الحد اليومي للتدريب (40 جلسة)؛ عد غدًا'; end if;
  v_retry := nullif(p->>'retry', '')::bigint;
  if v_retry is not null then
    -- «أعد الأخطاء»: سؤال آخر من الهدف نفسه لكل خطأ (دون تكرار)، ثم الأسئلة الأصلية نفسها في آخر الجلسة.
    if not exists (select 1 from practice_sessions where id = v_retry and user_id = auth.uid()) then raise exception 'الجلسة غير موجودة'; end if;
    select coalesce(array_agg(a.question_id order by random()), '{}') into v_wrong
      from practice_answers a join questions q on q.id = a.question_id
      where a.session_id = v_retry and not a.correct and q.status = 'approved' and not q.excluded;
    if cardinality(v_wrong) = 0 then raise exception 'لا توجد أخطاء في هذه الجلسة'; end if;
    for w in select q.id, q.objective_id from questions q where q.id = any(v_wrong) loop
      select q2.id into v_alt from questions q2
        where q2.objective_id = w.objective_id and q2.type = 'mcq' and q2.status = 'approved' and not q2.excluded
          and not (q2.id = any(v_wrong)) and not (q2.id = any(v_alts))
        order by random() limit 1;
      if v_alt is not null then v_alts := v_alts || v_alt; end if;
      v_alt := null;
    end loop;
    v_ids := v_alts || v_wrong;
  else
    v_count := least(greatest(coalesce((p->>'count')::int, 10), 3), 30);
    v_levels := coalesce(p->>'levels', 'graded');
    if v_levels not in ('graded', 'basic', 'apply', 'higher') then v_levels := 'graded'; end if;
    -- الدروس من المقررات المسندة للطالب فقط
    select array_agg(distinct l.id) into v_lessons from jsonb_array_elements_text(coalesce(p->'lessons', '[]')) x
      join lessons l on l.id = x::bigint join chapters c on c.id = l.chapter_id
      join course_enrollments e on e.course_id = c.course_id and e.user_id = auth.uid();
    if coalesce(array_length(v_lessons, 1), 0) = 0 then raise exception 'اختر درسًا واحدًا على الأقل'; end if;
    -- متدرّج: 40% تطبيق و20% تفكير عليا (مقربة للأسفل) والباقي أساسي، ويُكمل النقص من بقية المجموعات
    v_apply := floor(v_count * .4); v_higher := floor(v_count * .2); v_basic := v_count - v_apply - v_higher;
    with pool as (
      select q.id, public._level_group(q.thinking_level) g,
        case q.difficulty when 'سهل' then 1 when 'متوسط' then 2 else 3 end d, random() r
      from questions q join objectives o on o.id = q.objective_id
      where o.lesson_id = any(v_lessons) and q.type = 'mcq' and q.status = 'approved' and not q.excluded
        and (v_levels = 'graded' or public._level_group(q.thinking_level) = v_levels)),
    ranked as (select *, row_number() over (partition by g order by r) rn from pool),
    quota as (select * from ranked where v_levels <> 'graded'
              or (g = 'basic' and rn <= v_basic) or (g = 'apply' and rn <= v_apply) or (g = 'higher' and rn <= v_higher)),
    picked as (
      (select id, d, r, 0 pri from quota order by r limit v_count)
      union all
      (select id, d, r, 1 from pool where id not in (select id from quota) order by r limit v_count)),
    final as (select id, d, r from picked order by pri, r limit v_count)
    -- الترتيب من السهل إلى الأصعب ليبني الثقة ثم يرفع التحدي
    select coalesce(array_agg(id order by d, r), '{}') into v_ids from final;
    if coalesce(array_length(v_ids, 1), 0) = 0 then raise exception 'لا توجد أسئلة بهذه الاختيارات؛ غيّر الدروس أو المستوى'; end if;
  end if;
  if v_timed then
    select sum(case when public._level_group(thinking_level) = 'basic' then 60 else 105 end) into v_limit from questions where id = any(v_ids);
  end if;
  -- تُخزن الإعدادات المعروفة فقط (لا يُحفظ جسم الطلب كما هو)
  insert into practice_sessions (user_id, settings, question_ids, time_limit_sec, total)
  values (auth.uid(), jsonb_build_object('lessons', to_jsonb(v_lessons), 'count', v_count, 'levels', v_levels, 'timed', v_timed, 'retry', v_retry),
    v_ids, v_limit, cardinality(v_ids)) returning id into v_sid;
  return jsonb_build_object('id', v_sid, 'timeLimit', v_limit, 'retry', v_retry is not null,
    'questions', (select jsonb_agg(public._student_q(q) order by array_position(v_ids, q.id)) from questions q where q.id = any(v_ids)));
end $$;

-- الإجابة على سؤال واحد: تُسجل مرة واحدة، وتُرجع التصحيح والتفسير لهذا السؤال فقط.
create or replace function public.student_answer(p_session bigint, p_question bigint, p_choice int) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare s public.practice_sessions; a public.question_answers; v_ok boolean;
begin
  perform public._require_student();
  select * into s from practice_sessions where id = p_session and user_id = auth.uid();
  if not found then raise exception 'الجلسة غير موجودة'; end if;
  if s.finished_at is not null then raise exception 'انتهت هذه الجلسة'; end if;
  if not (p_question = any(s.question_ids)) then raise exception 'السؤال ليس من هذه الجلسة'; end if;
  if p_choice is null or p_choice < 0 or p_choice >= (select jsonb_array_length(options) from questions where id = p_question) then raise exception 'اختيار غير صالح'; end if;
  if exists (select 1 from practice_answers where session_id = p_session and question_id = p_question) then raise exception 'أجبت عن هذا السؤال'; end if;
  -- حد يومي للإجابات يمنع جمع مفاتيح الإجابة آليًا
  if (select count(*) from practice_answers pa join practice_sessions ps on ps.id = pa.session_id
      where ps.user_id = auth.uid() and pa.answered_at > now() - interval '1 day') >= 400 then
    raise exception 'وصلت إلى الحد اليومي للإجابات (400)؛ عد غدًا';
  end if;
  select * into a from question_answers where question_id = p_question;
  v_ok := p_choice = a.correct_index;
  insert into practice_answers (session_id, question_id, choice, correct) values (p_session, p_question, p_choice, v_ok);
  return jsonb_build_object('correct', v_ok, 'correctIndex', a.correct_index, 'explanation', a.explanation,
    'distractorNotes', coalesce(a.distractor_notes, '[]'));
end $$;

-- إنهاء الجلسة: النتيجة وتحليلها حسب الدرس ومجموعة المستوى.
create or replace function public.student_finish(p_session bigint) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare s public.practice_sessions; v_score int;
begin
  perform public._require_student();
  select * into s from practice_sessions where id = p_session and user_id = auth.uid();
  if not found then raise exception 'الجلسة غير موجودة'; end if;
  select count(*) filter (where correct) into v_score from practice_answers where session_id = p_session;
  if s.finished_at is null then update practice_sessions set finished_at = now(), score = v_score where id = p_session; end if;
  return public._session_summary(p_session);
end $$;

create or replace function public._session_summary(p_session bigint) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select jsonb_build_object('id', s.id, 'createdAt', s.created_at, 'finishedAt', s.finished_at, 'total', s.total,
    'answered', (select count(*) from practice_answers where session_id = s.id),
    'score', (select count(*) filter (where correct) from practice_answers where session_id = s.id),
    'wrong', (select count(*) filter (where not correct) from practice_answers where session_id = s.id),
    'byLesson', (select coalesce(jsonb_agg(jsonb_build_object('lesson', t.title, 'n', t.n, 'correct', t.c) order by t.title), '[]') from
       (select l.title, count(*) n, count(*) filter (where a.correct) c from practice_answers a join questions q on q.id = a.question_id
          join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id where a.session_id = s.id group by l.id, l.title) t),
    'byGroup', (select coalesce(jsonb_agg(jsonb_build_object('group', t.g, 'n', t.n, 'correct', t.c)), '[]') from
       (select public._level_group(q.thinking_level) g, count(*) n, count(*) filter (where a.correct) c from practice_answers a
          join questions q on q.id = a.question_id where a.session_id = s.id group by 1) t))
  from practice_sessions s where s.id = p_session
$$;

create or replace function public.student_history() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_student();
  return (select coalesce(jsonb_agg(public._session_summary(id) order by created_at desc), '[]')
          from (select id, created_at from practice_sessions where user_id = auth.uid() order by created_at desc limit 30) t);
end $$;

-- =====================================================================
-- لوحة المعلم: تقدم الطلاب حسب الشعبة (للمعلم والمراجع والمشرف). لا يرى الطلاب بيانات بعضهم.
-- =====================================================================
drop function if exists public.teacher_progress(text);
create or replace function public.teacher_progress(p_section text default null, p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  if public.my_role() not in ('admin', 'viewer', 'reviewer') then raise exception 'تقدم الطلاب بالأسماء للمعلم ومالك المشروع؛ المؤشرات العامة في «لوحة المؤشرات»' using errcode = '42501'; end if;
  -- طلاب المقرر المختار، وإجاباتهم على أسئلة هذا المقرر فقط
  return (with en as (select user_id from course_enrollments where course_id = v_course),
    cq as (select q.id, q.objective_id from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id
           join chapters c on c.id = l.chapter_id where c.course_id = v_course),
    ans as (select ps.user_id, ps.id session_id, ps.created_at, a.question_id, a.correct, cq.objective_id
            from practice_sessions ps join practice_answers a on a.session_id = ps.id join cq on cq.id = a.question_id)
  select jsonb_build_object(
    'sections', (select coalesce(jsonb_agg(distinct p.section), '[]') from profiles p join en on en.user_id = p.user_id where p.role = 'student' and p.section is not null),
    'students', (with st as (
        select user_id, count(distinct session_id) sessions, count(*) answered, count(*) filter (where correct) correct, max(created_at) last_active
        from ans group by user_id)
      select coalesce(jsonb_agg(jsonb_build_object('name', pr.display_name, 'username', split_part(u.email, '@', 1), 'section', pr.section, 'grade', pr.grade,
        'sessions', coalesce(st.sessions, 0), 'answered', coalesce(st.answered, 0), 'correct', coalesce(st.correct, 0), 'lastActive', st.last_active)
        order by pr.section, pr.display_name), '[]')
      from profiles pr join en on en.user_id = pr.user_id join auth.users u on u.id = pr.user_id left join st on st.user_id = pr.user_id
      where pr.role = 'student' and (p_section is null or pr.section = p_section)),
    -- الأهداف الأضعف في الشعبة (5 إجابات على الأقل لكل هدف) — تكشف المفاهيم البديلة
    'weakObjectives', (select coalesce(jsonb_agg(jsonb_build_object('code', o.code, 'text', coalesce(o.approved_text, o.original_text), 'lesson', l.title,
        'n', t.n, 'pct', t.pct) order by t.pct, t.n desc), '[]')
      from (select ans.objective_id, count(*) n, round(100.0 * count(*) filter (where ans.correct) / count(*)) pct
            from ans join profiles pr on pr.user_id = ans.user_id
            where pr.role = 'student' and (p_section is null or pr.section = p_section)
            group by ans.objective_id having count(*) >= 5 order by 3, 2 desc limit 15) t
      join objectives o on o.id = t.objective_id join lessons l on l.id = o.lesson_id)));
end $$;

-- إدارة الطلاب للمشرف: عرض وتعديل الاسم والشعبة والدور (إنشاء الحساب نفسه عبر دالة الحافة admin-users).
create or replace function public.admin_list_students() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if not exists (select 1 from profiles where user_id = auth.uid() and role = 'admin') then raise exception 'للمشرف فقط' using errcode = '42501'; end if;
  return (with st as (
      select ps.user_id, count(distinct ps.id) sessions, count(a.question_id) answered, count(*) filter (where a.correct) correct, max(ps.created_at) last_active
      from practice_sessions ps left join practice_answers a on a.session_id = ps.id group by ps.user_id)
    select coalesce(jsonb_agg(jsonb_build_object('id', pr.user_id, 'username', split_part(u.email, '@', 1), 'name', pr.display_name,
      'grade', pr.grade, 'section', pr.section, 'role', pr.role, 'confirmed', pr.profile_confirmed, 'createdAt', pr.created_at,
      'sessions', coalesce(st.sessions, 0), 'answered', coalesce(st.answered, 0), 'correct', coalesce(st.correct, 0), 'lastActive', st.last_active)
      order by pr.grade nulls last, pr.section nulls last, pr.display_name), '[]')
    from profiles pr join auth.users u on u.id = pr.user_id left join st on st.user_id = pr.user_id
    where pr.managed and pr.role in ('student', 'pending'));
end $$;

drop function if exists public.admin_update_student(uuid, text, text, text);
create or replace function public.admin_update_student(p_id uuid, p_name text, p_section text, p_role text, p_grade text default null) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if not exists (select 1 from profiles where user_id = auth.uid() and role = 'admin') then raise exception 'للمشرف فقط' using errcode = '42501'; end if;
  if p_role not in ('student', 'pending') then raise exception 'الدور غير صالح'; end if;
  if not exists (select 1 from profiles where user_id = p_id and managed and role in ('student', 'pending')) then raise exception 'الحساب ليس حساب طالب'; end if;
  update profiles set display_name = coalesce(nullif(trim(p_name), ''), display_name), section = nullif(trim(p_section), ''),
    grade = nullif(trim(p_grade), ''), role = p_role where user_id = p_id;
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.is_student(), public.student_confirm_profile(text, text), public.student_catalog(), public.student_start(jsonb),
  public.student_answer(bigint, bigint, int), public.student_finish(bigint), public.student_history(),
  public.teacher_progress(text, bigint), public.admin_list_students(), public.admin_update_student(uuid, text, text, text, text) to authenticated;
revoke execute on function public._require_student(), public._student_q(public.questions), public._session_summary(bigint) from authenticated;

-- تستدعيها دالة الحافة admin-users بتوكن المشرف نفسه (لا بمفتاح الخدمة) بعد إنشاء حساب الطالب.
drop function if exists public.admin_init_student(uuid, text, text);
create or replace function public.admin_init_student(p_id uuid, p_name text, p_section text, p_grade text default null) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if not exists (select 1 from profiles where user_id = auth.uid() and role = 'admin') then raise exception 'للمشرف فقط' using errcode = '42501'; end if;
  if not exists (select 1 from profiles where user_id = p_id and role in ('pending', 'student')) then raise exception 'الحساب ليس حساب طالب جديد'; end if;
  update profiles set role = 'student', managed = true, display_name = coalesce(nullif(trim(p_name), ''), display_name),
    section = nullif(trim(p_section), ''), grade = nullif(trim(p_grade), ''), profile_confirmed = false where user_id = p_id;
end $$;
create or replace function public.admin_is_student(p_id uuid) returns boolean
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if not exists (select 1 from profiles where user_id = auth.uid() and role = 'admin') then raise exception 'للمشرف فقط' using errcode = '42501'; end if;
  return exists (select 1 from profiles where user_id = p_id and managed and role in ('pending', 'student'));
end $$;
revoke execute on function public.admin_init_student(uuid, text, text, text), public.admin_is_student(uuid) from anon, public;
grant execute on function public.admin_init_student(uuid, text, text, text), public.admin_is_student(uuid) to authenticated;

-- فهارس وتشديد إضافي
create index if not exists idx_pa_question on public.practice_answers(question_id);
create index if not exists idx_pa_session_time on public.practice_answers(session_id, answered_at);
revoke all on all sequences in schema public from anon, authenticated;

-- 2026-10-12: لا يُستخدم مصطلح «مسارات» في المنصة
update public.courses set grade = trim(regexp_replace(grade, '\s*\(?مسارات\)?', '', 'g')) where grade like '%مسارات%';

-- =====================================================================
-- 2026-10-13: حسابات الفريق بأدوار مختلفة، وملاحظات المراجعة، ولوحة المؤشرات
-- =====================================================================
-- حساب فريق أنشأه مالك المشروع (مراجع، معلم، مشرف تربوي، مدير مدرسة) يُميَّز عن حسابات الطلاب
alter table public.profiles add column if not exists staff boolean not null default false;

-- ---------- ملاحظات المراجعة: يكتبها المراجع على هدف أو سؤال أو محتوى مكمّل دون تعديل المحتوى نفسه ----------
create table if not exists public.review_notes (
  id bigint generated by default as identity primary key,
  objective_id bigint not null references public.objectives(id) on delete cascade,
  question_id bigint references public.questions(id) on delete cascade,
  entity text not null check (entity in ('objective', 'question', 'supplement')),
  body text not null,
  author uuid,
  author_name text,
  created_at timestamptz not null default now(),
  resolved_at timestamptz,
  resolved_by_name text,
  response text
);
create index if not exists idx_notes_obj on public.review_notes(objective_id);
create index if not exists idx_notes_open on public.review_notes(created_at desc) where resolved_at is null;
alter table public.review_notes enable row level security;
revoke all on public.review_notes from anon, authenticated;

create or replace function public._note_json(n public.review_notes) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select jsonb_build_object('id', n.id, 'entity', n.entity, 'body', n.body, 'author', n.author_name, 'mine', n.author = auth.uid(),
    'createdAt', n.created_at, 'resolvedAt', n.resolved_at, 'resolvedBy', n.resolved_by_name, 'response', n.response,
    'objectiveCode', o.code, 'objectiveText', coalesce(o.approved_text, o.original_text),
    'questionId', n.question_id, 'questionType', q.type, 'questionNumber', q.number, 'questionStem', left(q.stem, 160))
  from public.objectives o left join public.questions q on q.id = n.question_id where o.id = n.objective_id
$$;

create or replace function public.add_note(p_code text, p_entity text, p_body text, p_question bigint default null) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare o public.objectives; n public.review_notes;
begin
  perform public._require_reviewer();
  select * into o from public.objectives where code = p_code;
  if not found then raise exception 'الهدف غير موجود'; end if;
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

-- p_code: ملاحظات هدف واحد (كلها)، أو بدونه: كل الملاحظات حسب الحالة open | resolved | all
create or replace function public.get_notes(p_code text default null, p_status text default 'open') returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  return (select coalesce(jsonb_agg(public._note_json(n) order by n.created_at desc), '[]') from (
    select n.* from public.review_notes n join public.objectives o on o.id = n.objective_id
    where (p_code is null or o.code = p_code)
      and (p_code is not null or coalesce(p_status, 'open') = 'all'
           or (coalesce(p_status, 'open') = 'open' and n.resolved_at is null)
           or (p_status = 'resolved' and n.resolved_at is not null))
    order by n.created_at desc limit 500) n);
end $$;

-- مالك المشروع يغلق الملاحظة (بعد تنفيذها أو مع رد) أو يعيد فتحها
create or replace function public.resolve_note(p_id bigint, p_resolved boolean, p_response text default null) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if auth.uid() is null then raise exception 'يلزم تسجيل الدخول' using errcode = '28000'; end if;
  if not public.is_admin() then raise exception 'إغلاق الملاحظات لمالك المشروع' using errcode = '42501'; end if;
  update public.review_notes set
    resolved_at = case when p_resolved then now() end,
    resolved_by_name = case when p_resolved then (select display_name from public.profiles where user_id = auth.uid()) end,
    response = coalesce(nullif(trim(p_response), ''), response)
  where id = p_id;
  if not found then raise exception 'الملاحظة غير موجودة'; end if;
end $$;

-- يحذف كاتب الملاحظة ملاحظته ما دامت مفتوحة، ومالك المشروع أي ملاحظة
create or replace function public.delete_note(p_id bigint) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  delete from public.review_notes where id = p_id and (public.is_admin() or (author = auth.uid() and resolved_at is null));
  if not found then raise exception 'لا يمكن حذف هذه الملاحظة' using errcode = '42501'; end if;
end $$;

-- ---------- لوحة المؤشرات: أرقام مجمّعة فقط (لا أسماء طلاب) لكل الحسابات المفعّلة من الفريق ----------
drop function if exists public.get_dashboard();
create or replace function public.get_dashboard(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_now timestamptz := now(); v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  -- كل الأرقام للمقرر المختار: طلابه المسندون، وإجاباتهم على أسئلته
  return (with cq as (select q.id, q.thinking_level, l.chapter_id from questions q join objectives o on o.id = q.objective_id
              join lessons l on l.id = o.lesson_id join chapters c on c.id = l.chapter_id where c.course_id = v_course),
    stu as (select p.* from profiles p join course_enrollments e on e.user_id = p.user_id and e.course_id = v_course where p.role = 'student'),
    ans as (select s.user_id, s.id session_id, s.created_at, a.answered_at, a.correct, cq.thinking_level, cq.chapter_id
            from practice_answers a join practice_sessions s on s.id = a.session_id join cq on cq.id = a.question_id
            where s.user_id in (select user_id from stu))
  select jsonb_build_object(
    'generatedAt', v_now,
    'bank', public._stats_data(v_course),
    'questionLevels', (select coalesce(jsonb_agg(jsonb_build_object('group', g, 'n', n)), '[]') from
       (select public._level_group(q.thinking_level) g, count(*) n from questions q join cq on cq.id = q.id where not q.excluded group by 1) t),
    'students', (select jsonb_build_object('n', count(*), 'confirmed', count(*) filter (where profile_confirmed),
       'active', count(*) filter (where exists (select 1 from ans where ans.user_id = stu.user_id)),
       'active7', count(*) filter (where exists (select 1 from ans where ans.user_id = stu.user_id and ans.answered_at > v_now - interval '7 days')))
       from stu),
    'practice', (select jsonb_build_object('sessions', count(distinct session_id), 'answers', count(*), 'correct', count(*) filter (where correct),
       'answers7', count(*) filter (where answered_at > v_now - interval '7 days')) from ans),
    'bySection', (select coalesce(jsonb_agg(jsonb_build_object('section', t.section, 'students', t.students, 'active', t.active,
         'active7', t.active7, 'answers', t.answers, 'correct', t.correct) order by t.section), '[]') from (
       select coalesce(stu.section, 'بدون شعبة') section, count(distinct stu.user_id) students,
         count(distinct ans.user_id) active,
         count(distinct ans.user_id) filter (where ans.answered_at > v_now - interval '7 days') active7,
         count(ans.user_id) answers, count(ans.user_id) filter (where ans.correct) correct
       from stu left join ans on ans.user_id = stu.user_id group by 1) t),
    -- آخر 8 أسابيع (بتوقيت الرياض): عدد الإجابات والطلاب النشطين
    'weekly', (select coalesce(jsonb_agg(jsonb_build_object('week', to_char(w.wk, 'YYYY-MM-DD'), 'answers', coalesce(x.answers, 0),
         'students', coalesce(x.students, 0), 'correct', coalesce(x.correct, 0)) order by w.wk), '[]')
       from generate_series(date_trunc('week', (v_now at time zone 'Asia/Riyadh')) - interval '7 weeks',
                            date_trunc('week', (v_now at time zone 'Asia/Riyadh')), interval '1 week') w(wk)
       left join (select date_trunc('week', answered_at at time zone 'Asia/Riyadh') wk, count(*) answers,
                    count(*) filter (where correct) correct, count(distinct user_id) students
                  from ans where answered_at > v_now - interval '9 weeks' group by 1) x on x.wk = w.wk),
    'byChapter', (select coalesce(jsonb_agg(jsonb_build_object('number', c.number, 'title', c.title, 'answers', coalesce(x.n, 0), 'correct', coalesce(x.c, 0)) order by c.number), '[]')
       from chapters c left join (select chapter_id, count(*) n, count(*) filter (where correct) c from ans group by chapter_id) x on x.chapter_id = c.id
       where c.course_id = v_course),
    'byGroup', (select coalesce(jsonb_agg(jsonb_build_object('group', g, 'answers', n, 'correct', c)), '[]') from
       (select public._level_group(thinking_level) g, count(*) n, count(*) filter (where correct) c from ans group by 1) t),
    'notes', case when public.is_reviewer() then (select jsonb_build_object('open', count(*) filter (where n.resolved_at is null), 'n', count(*))
       from review_notes n join objectives o on o.id = n.objective_id join lessons l on l.id = o.lesson_id join chapters c on c.id = l.chapter_id
       where c.course_id = v_course) end
  ));
end $$;

-- ---------- حسابات الفريق (لمالك المشروع) ----------
create or replace function public.admin_list_staff() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', pr.user_id, 'username', split_part(u.email, '@', 1), 'name', pr.display_name,
      'role', pr.role, 'createdAt', pr.created_at, 'lastSignIn', u.last_sign_in_at, 'self', pr.user_id = auth.uid())
      order by case pr.role when 'admin' then 0 when 'reviewer' then 1 when 'supervisor' then 2 when 'principal' then 3 when 'viewer' then 4 else 5 end, pr.display_name), '[]')
    from profiles pr join auth.users u on u.id = pr.user_id
    where pr.role in ('admin', 'reviewer', 'viewer', 'supervisor', 'principal') or (pr.role = 'pending' and (pr.staff or not pr.managed)));
end $$;

-- تستدعيها دالة الحافة admin-users بتوكن مالك المشروع بعد إنشاء حساب الفريق
create or replace function public.admin_init_staff(p_id uuid, p_name text, p_role text) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  if p_role not in ('reviewer', 'viewer', 'supervisor', 'principal') then raise exception 'الدور غير صالح'; end if;
  if not exists (select 1 from profiles where user_id = p_id and role = 'pending' and not managed) then raise exception 'الحساب ليس حسابًا جديدًا'; end if;
  update profiles set role = p_role, staff = true, display_name = coalesce(nullif(trim(p_name), ''), display_name) where user_id = p_id;
end $$;

-- تغيير الاسم أو الدور (أو الإيقاف بدور pending). لا يُمنح دور المالك من الواجهة، ولا يُعدَّل حساب مالك.
create or replace function public.admin_update_staff(p_id uuid, p_name text, p_role text) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  if p_role not in ('reviewer', 'viewer', 'supervisor', 'principal', 'pending') then raise exception 'الدور غير صالح'; end if;
  if p_id = auth.uid() then raise exception 'لا يمكن تعديل حسابك من هنا'; end if;
  if not exists (select 1 from profiles where user_id = p_id and role <> 'admin' and role <> 'student' and (staff or not managed)) then raise exception 'الحساب ليس حساب فريق'; end if;
  update profiles set display_name = coalesce(nullif(trim(p_name), ''), display_name), role = p_role, staff = true where user_id = p_id;
end $$;

-- يُسمح بإعادة كلمة المرور وتغيير اسم المستخدم والحذف لأي حساب عدا حسابات المالك
create or replace function public.admin_can_manage(p_id uuid) returns boolean
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  return exists (select 1 from profiles where user_id = p_id and role <> 'admin' and user_id <> auth.uid());
end $$;

-- الطلاب: حسابات الفريق الموقوفة لا تظهر في قائمة الطلاب
create or replace function public.admin_list_students() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if not exists (select 1 from profiles where user_id = auth.uid() and role = 'admin') then raise exception 'للمشرف فقط' using errcode = '42501'; end if;
  return (with st as (
      select ps.user_id, count(distinct ps.id) sessions, count(a.question_id) answered, count(*) filter (where a.correct) correct, max(ps.created_at) last_active
      from practice_sessions ps left join practice_answers a on a.session_id = ps.id group by ps.user_id)
    select coalesce(jsonb_agg(jsonb_build_object('id', pr.user_id, 'username', split_part(u.email, '@', 1), 'name', pr.display_name,
      'grade', pr.grade, 'section', pr.section, 'role', pr.role, 'confirmed', pr.profile_confirmed, 'createdAt', pr.created_at,
      'sessions', coalesce(st.sessions, 0), 'answered', coalesce(st.answered, 0), 'correct', coalesce(st.correct, 0), 'lastActive', st.last_active,
      'courses', (select coalesce(jsonb_agg(e.course_id order by e.course_id), '[]') from course_enrollments e where e.user_id = pr.user_id))
      order by pr.grade nulls last, pr.section nulls last, pr.display_name), '[]')
    from profiles pr join auth.users u on u.id = pr.user_id left join st on st.user_id = pr.user_id
    where pr.managed and not pr.staff and pr.role in ('student', 'pending'));
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.is_admin(), public.add_note(text, text, text, bigint), public.get_notes(text, text),
  public.resolve_note(bigint, boolean, text), public.delete_note(bigint), public.get_dashboard(bigint),
  public.admin_list_staff(), public.admin_init_staff(uuid, text, text), public.admin_update_staff(uuid, text, text),
  public.admin_can_manage(uuid) to authenticated;
revoke execute on function public._require_admin(), public._note_json(public.review_notes) from authenticated;

-- =====================================================================
-- 2026-10-13: تعدد المقررات (المرحلة 0) — صفحة المقررات وإسنادها للطلاب
-- =====================================================================
-- المقررات كما تظهر في الصفحة الأولى، مع أرقام كل مقرر
create or replace function public.get_courses() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'code', c.code, 'title', c.title, 'grade', c.grade, 'term', c.term,
      'status', c.status, 'eta', c.eta, 'sortOrder', c.sort_order,
      'chapters', (select count(*) from chapters ch where ch.course_id = c.id),
      'objectives', (select count(*) from objectives o join lessons l on l.id = o.lesson_id join chapters ch on ch.id = l.chapter_id where ch.course_id = c.id),
      'questions', (select count(*) from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id join chapters ch on ch.id = l.chapter_id
                    where ch.course_id = c.id and not q.excluded),
      'approved', (select count(*) from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id join chapters ch on ch.id = l.chapter_id
                    where ch.course_id = c.id and not q.excluded and q.status = 'approved'),
      'students', (select count(*) from course_enrollments e join profiles p on p.user_id = e.user_id where e.course_id = c.id and p.role = 'student'))
    order by c.sort_order, c.id), '[]') from courses c);
end $$;

-- إسناد مقرر لطلاب: add يضيف، set يجعله مقررهم الوحيد (نقل)، remove يلغيه. السجل السابق لا يُحذف أبدًا.
create or replace function public.admin_enroll(p_ids uuid[], p_course bigint, p_mode text default 'add') returns int
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_n int;
begin
  perform public._require_admin();
  if p_mode not in ('add', 'set', 'remove') then raise exception 'إجراء غير صالح'; end if;
  if not exists (select 1 from courses where id = p_course) then raise exception 'المقرر غير موجود'; end if;
  if coalesce(array_length(p_ids, 1), 0) = 0 then raise exception 'لم يُحدد أي طالب'; end if;
  if p_mode = 'remove' then
    delete from course_enrollments where course_id = p_course and user_id = any(p_ids);
    get diagnostics v_n = row_count; return v_n;
  end if;
  if p_mode = 'set' then delete from course_enrollments where user_id = any(p_ids) and course_id <> p_course; end if;
  insert into course_enrollments (user_id, course_id)
    select user_id, p_course from profiles where user_id = any(p_ids) and role in ('student', 'pending') and managed and not staff
  on conflict do nothing;
  get diagnostics v_n = row_count;
  return (select count(*) from course_enrollments where course_id = p_course and user_id = any(p_ids));
end $$;

-- بعد إنشاء حسابات جديدة: إسنادها بأسماء المستخدمين (دالة الإنشاء لا تُرجع المعرّفات)
create or replace function public.admin_enroll_usernames(p_usernames text[], p_course bigint) returns int
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_ids uuid[];
begin
  perform public._require_admin();
  select coalesce(array_agg(u.id), '{}') into v_ids from auth.users u
    where split_part(u.email, '@', 1) = any(select lower(trim(x)) from unnest(p_usernames) x);
  if cardinality(v_ids) = 0 then return 0; end if;
  return public.admin_enroll(v_ids, p_course, 'add');
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.get_courses(), public.admin_enroll(uuid[], bigint, text), public.admin_enroll_usernames(text[], bigint) to authenticated;
revoke execute on function public._default_course() from authenticated;

-- =====================================================================
-- 2026-10-16: حماية البنك من النسخ والنشر (المعلم والمشرف التربوي والمدير)
--   البنك كاملًا بإجاباته لمالك المشروع والمراجع فقط. غيرهما يستلم الأسئلة دون إجابات (get_bank)،
--   والإجابات في صفحة الهدف الواحد، ومفتاح الاختبار لأسئلة الاختبار المختارة فقط (get_exam_answers).
-- =====================================================================
create or replace function public._restricted() returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce((select role in ('viewer', 'supervisor', 'principal') from public.profiles where user_id = auth.uid()), false)
$$;

create or replace function public.get_exam_answers(p_ids bigint[]) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_ids bigint[];
begin
  perform public._require_member();
  if public.my_role() = 'principal' then raise exception 'منشئ الاختبارات غير متاح لهذا الحساب' using errcode = '42501'; end if;
  select coalesce(array_agg(distinct x), '{}') into v_ids from unnest(p_ids) x;
  if cardinality(v_ids) > 100 then raise exception 'الاختبار الواحد 100 سؤال كحد أقصى'; end if;
  return (select coalesce(jsonb_agg(jsonb_build_object('id', q.id, 'correctIndex', a.correct_index, 'explanation', a.explanation,
      'distractorNotes', coalesce(a.distractor_notes, '[]'), 'modelAnswer', a.model_answer, 'answerElements', coalesce(a.answer_elements, '[]'),
      'solutionSteps', coalesce(a.solution_steps, '[]'), 'marks', coalesce(a.marks, '[]'), 'rubric', coalesce(a.rubric, '[]'),
      'commonErrors', coalesce(a.common_errors, '[]'))), '[]')
    from questions q join question_answers a on a.question_id = q.id where q.id = any(v_ids) and not q.excluded);
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.get_exam_answers(bigint[]) to authenticated;
revoke execute on function public._restricted() from authenticated;
