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
-- نوع المقرر (2026-10-29): مقرر دراسي، أو «الاستعداد للتحصيلي» (فصوله المواد الأربع ودروسه وحداتها، وأسئلته بأربعة بدائل دائمًا)
alter table public.courses add column if not exists kind text not null default 'course';
alter table public.courses drop constraint if exists courses_kind_check;
alter table public.courses add constraint courses_kind_check check (kind in ('course', 'tahsili'));
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
-- صور السؤال (2026-10-28): مصفوفة [{src, alt}] حتى 4 صور، تُعرض بعد نص السؤال.
--   src: مسار ثابت في الموقع (qimg/…) أو ملف في مخزن Supabase «question-media». يُتحقق منه في _validate_question.
alter table public.questions add column if not exists images jsonb;
-- سنة ورود السؤال في اختبار التحصيل الدراسي (2026-10-29): لأسئلة التجميعات، وتظهر للطالب. فارغة إن لم تُعرف السنة.
alter table public.questions add column if not exists exam_year smallint;
alter table public.questions drop constraint if exists questions_exam_year_check;
alter table public.questions add constraint questions_exam_year_check check (exam_year is null or exam_year between 2000 and 2100);
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
  if p ? 'exam_year' and jsonb_typeof(p->'exam_year') not in ('null', 'number') then errs := array_append(errs, 'سنة الورود رقم');
  elsif p ? 'exam_year' and jsonb_typeof(p->'exam_year') = 'number' and (p->>'exam_year')::numeric not between 2000 and 2100 then errs := array_append(errs, 'سنة الورود بين 2000 و2100'); end if;
  -- الصور: مصدر من الموقع نفسه (qimg/) أو من مخزن question-media فقط، ونص بديل قصير
  if p ? 'images' and jsonb_typeof(p->'images') is distinct from 'null' then
    if jsonb_typeof(p->'images') <> 'array' or jsonb_array_length(p->'images') > 4 then errs := array_append(errs, 'الصور قائمة من 4 صور على الأكثر');
    elsif exists (select 1 from jsonb_array_elements(p->'images') x
        where jsonb_typeof(x) <> 'object'
          or coalesce(x->>'src', '') !~ '^(qimg/[A-Za-z0-9._/-]+\.(png|jpe?g|webp|gif|svg)|https://[a-z0-9]+\.supabase\.co/storage/v1/object/public/question-media/[A-Za-z0-9._/-]+\.(png|jpe?g|webp|gif))$'
          or (x->>'src') like '%..%' or length(coalesce(x->>'alt', '')) > 200) then
      errs := array_append(errs, 'مصدر صورة غير مسموح أو وصفها طويل');
    end if;
  end if;
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

-- أسئلة «الاستعداد للتحصيلي» بأربعة بدائل دائمًا كالاختبار الحقيقي (2026-10-29)
create or replace function public._check_tahsili_options(p_objective bigint, p_type text, p jsonb) returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if not exists (select 1 from objectives o join lessons l on l.id = o.lesson_id join chapters ch on ch.id = l.chapter_id
                 join courses c on c.id = ch.course_id where o.id = p_objective and c.kind = 'tahsili') then return; end if;
  -- اختبار التحصيلي اختيار من متعدد فقط: لا أسئلة مقالية في قسمه
  if p_type <> 'mcq' then
    raise exception 'أسئلة التحصيلي اختيار من متعدد فقط (لا مقالي فيه)' using errcode = '22023';
  end if;
  if jsonb_typeof(p->'options') = 'array' and jsonb_array_length(p->'options') <> 4 then
    raise exception 'أسئلة التحصيلي بأربعة بدائل (أ ب ج د)' using errcode = '22023';
  end if;
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
  perform public._check_tahsili_options(q.objective_id, q.type, p);
  v_before := public._question_json(p_id);
  -- أي تعديل بشري ينقل السؤال إلى «قيد المراجعة»
  update public.questions set stem = trim(p->>'stem'), stimulus = nullif(p->'stimulus', 'null'::jsonb),
    images = case when p ? 'images' then nullif(nullif(p->'images', 'null'::jsonb), '[]'::jsonb) else images end,
    exam_year = case when p ? 'exam_year' then (p->>'exam_year')::smallint else exam_year end,
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
  perform public._check_tahsili_options(o.id, p_type, p);
  perform public._validate_question(p_type, p);
  select coalesce(max(number), 0) + 1 into v_num from public.questions where objective_id = o.id and type = p_type;
  insert into public.questions (objective_id, type, number, stem, stimulus, images, exam_year, options, thinking_level, question_kind, difficulty, source_ref, status, origin)
  values (o.id, p_type, v_num, trim(p->>'stem'), nullif(p->'stimulus', 'null'::jsonb), nullif(nullif(p->'images', 'null'::jsonb), '[]'::jsonb), (p->>'exam_year')::smallint,
    case when p_type = 'mcq' then p->'options' end,
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
  insert into public.questions (objective_id, type, number, stem, stimulus, images, exam_year, options, thinking_level, question_kind, difficulty, source_ref, status, origin)
  select objective_id, type, v_num, stem, stimulus, images, exam_year, options, thinking_level, question_kind, difficulty, source_ref, 'in_review', 'human'
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
    'stimulus', q.stimulus, 'images', q.images, 'examYear', q.exam_year, 'options', coalesce(q.options, '[]'), 'thinkingLevel', q.thinking_level,
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
       'courses', (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'code', c.code, 'grade', c.grade, 'term', c.term, 'kind', c.kind) order by c.sort_order), '[]')
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
  return (select coalesce(jsonb_agg(jsonb_build_object('number', c.number, 'title', c.title, 'course', cr.code, 'courseId', cr.id, 'kind', cr.kind, 'lessons',
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
  select jsonb_build_object('id', q.id, 'stem', q.stem, 'stimulus', q.stimulus, 'images', q.images, 'examYear', q.exam_year, 'options', q.options,
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
      -- السؤال البديل: ما لم يُجب عنه الطالب من قبل أولًا
      select q2.id into v_alt from questions q2
        where q2.objective_id = w.objective_id and q2.type = 'mcq' and q2.status = 'approved' and not q2.excluded
          and not (q2.id = any(v_wrong)) and not (q2.id = any(v_alts))
        order by exists (select 1 from practice_answers a join practice_sessions ps on ps.id = a.session_id
                         where ps.user_id = auth.uid() and a.question_id = q2.id), random() limit 1;
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
    -- الأسئلة التي لم يُجب عنها الطالب من قبل أولًا (s = 0)، ثم المكررة؛ ونسب المستويات محفوظة داخل كل منهما
    v_apply := floor(v_count * .4); v_higher := floor(v_count * .2); v_basic := v_count - v_apply - v_higher;
    with seen as (select distinct a.question_id from practice_answers a join practice_sessions ps on ps.id = a.session_id where ps.user_id = auth.uid()),
    pool as (
      select q.id, public._level_group(q.thinking_level) g,
        case q.difficulty when 'سهل' then 1 when 'متوسط' then 2 else 3 end d, random() r,
        (q.id in (select question_id from seen))::int s
      from questions q join objectives o on o.id = q.objective_id
      where o.lesson_id = any(v_lessons) and q.type = 'mcq' and q.status = 'approved' and not q.excluded
        and (v_levels = 'graded' or public._level_group(q.thinking_level) = v_levels)),
    ranked as (select *, row_number() over (partition by g order by s, r) rn from pool),
    quota as (select * from ranked where v_levels <> 'graded'
              or (g = 'basic' and rn <= v_basic) or (g = 'apply' and rn <= v_apply) or (g = 'higher' and rn <= v_higher)),
    picked as (
      (select id, d, r, s, 0 pri from quota order by s, r limit v_count)
      union all
      (select id, d, r, s, 1 from pool where id not in (select id from quota) order by s, r limit v_count)),
    final as (select id, d, r from picked order by s, pri, r limit v_count)
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
declare s public.practice_sessions; v_score int; r record;
begin
  perform public._require_student();
  select * into s from practice_sessions where id = p_session and user_id = auth.uid();
  if not found then raise exception 'الجلسة غير موجودة'; end if;
  select count(*) filter (where correct) into v_score from practice_answers where session_id = p_session;
  if s.finished_at is null then update practice_sessions set finished_at = now(), score = v_score where id = p_session; end if;
  -- مهام المعلم المفتوحة: تُحتسب فور انتهاء الجلسة (لتصل مكافأة المهمة المنجزة إلى رصيد الطالب دون انتظار فتح الصندوق)
  for r in select cr.comm_id from comm_recipients cr join comms c on c.id = cr.comm_id
           where cr.student_id = auth.uid() and cr.status = 'open' and c.kind = 'task' and c.status = 'active' loop
    perform public._comm_refresh(r.comm_id, auth.uid());
  end loop;
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
-- source: staff = ملاحظة فريق، student = بلاغ طالب عن مشكلة في سؤال (لا يُعرض اسم الطالب)
alter table public.review_notes add column if not exists source text not null default 'staff';
create index if not exists idx_notes_obj on public.review_notes(objective_id);
create index if not exists idx_notes_open on public.review_notes(created_at desc) where resolved_at is null;
alter table public.review_notes enable row level security;
revoke all on public.review_notes from anon, authenticated;

create or replace function public._note_json(n public.review_notes) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select jsonb_build_object('id', n.id, 'entity', n.entity, 'body', n.body, 'author', n.author_name, 'mine', n.author = auth.uid(),
    'source', n.source, 'createdAt', n.created_at, 'resolvedAt', n.resolved_at, 'resolvedBy', n.resolved_by_name, 'response', n.response,
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

-- يحذف كاتب الملاحظة ملاحظته ما دامت مفتوحة، ومالك المشروع أي ملاحظة، والمراجع بلاغات الطلاب غير الصحيحة
create or replace function public.delete_note(p_id bigint) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_reviewer();
  delete from public.review_notes where id = p_id and (public.is_admin() or (author = auth.uid() and resolved_at is null) or source = 'student');
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
      'status', c.status, 'eta', c.eta, 'sortOrder', c.sort_order, 'kind', c.kind,
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

-- =====================================================================
-- 2026-10-18: نطاق المعلم — يرى مقرراته الجاهزة وطلابه المسندين له فقط
--   المعلم (دور viewer) وحده يتقيّد: المقررات التي يسندها له مالك المشروع (الجاهزة فقط)، وتقدم طلابه المسندين وحدهم.
--   كل الأدوار الأخرى (المالك، المراجع، المشرف التربوي، المدير، الطالب) لا يتغير شيء في ما ترى ولا في سلوكها.
--   لا يُحذف ولا يُعدَّل أي شيء من جلسات التدريب وإجابات الطلاب ونتائجهم؛ كل الإضافات قراءة وتقييد فقط.
--   الإغلاق في قاعدة البيانات نفسها (السياسات والدوال) لا في الواجهة فقط.
-- =====================================================================
create table if not exists public.teacher_courses (
  teacher_id uuid not null references public.profiles(user_id) on delete cascade,
  course_id bigint not null references public.courses(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (teacher_id, course_id)
);
create table if not exists public.teacher_students (
  teacher_id uuid not null references public.profiles(user_id) on delete cascade,
  student_id uuid not null references public.profiles(user_id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (teacher_id, student_id)
);
create index if not exists idx_teacher_students_student on public.teacher_students(student_id);
alter table public.teacher_courses enable row level security;
alter table public.teacher_students enable row level security;
revoke all on public.teacher_courses, public.teacher_students from anon, authenticated;

-- علامات التنفيذ لمرة واحدة (تبقى الترقية آمنة عند إعادة تنفيذ schema.sql)
create table if not exists public.schema_flags (key text primary key, at timestamptz not null default now());
alter table public.schema_flags enable row level security;
revoke all on public.schema_flags from anon, authenticated;
-- مرة واحدة: كل معلم حالي يبقى يرى ما كان يراه قبل التقييد تمامًا (كل المقررات الجاهزة وكل الطلاب المسجلين في أي مقرر)،
-- فلا يتغير شيء عليه حتى يضيّق المالك الإسناد من «حسابات الفريق». المعلم الجديد لاحقًا يبدأ بلا إسناد.
do $$ begin
  if not exists (select 1 from public.schema_flags where key = 'teacher_scope_2026_10_18') then
    insert into public.teacher_courses (teacher_id, course_id)
      select p.user_id, c.id from public.profiles p cross join public.courses c where p.role = 'viewer' and c.status = 'ready' on conflict do nothing;
    insert into public.teacher_students (teacher_id, student_id)
      select t.user_id, s.user_id from public.profiles t cross join public.profiles s
       where t.role = 'viewer' and s.role = 'student'
         and exists (select 1 from public.course_enrollments e where e.user_id = s.user_id) on conflict do nothing;
    insert into public.schema_flags (key) values ('teacher_scope_2026_10_18');
  end if;
end $$;

-- هل يستطيع الحساب الحالي قراءة هذا المقرر؟ المعلم وحده مقيّد بما أُسند له (الجاهز فقط)؛ غيره كما كان.
create or replace function public._course_ok(p_course bigint) returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select case when (select role from public.profiles where user_id = auth.uid()) = 'viewer'
    then exists (select 1 from public.teacher_courses t join public.courses c on c.id = t.course_id
                 where t.teacher_id = auth.uid() and t.course_id = p_course and c.status = 'ready')
    else true end
$$;
create or replace function public._require_course(p_course bigint) returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  if public.my_role() = 'viewer' and (p_course is null or not public._course_ok(p_course)) then
    raise exception 'هذا المقرر غير متاح لحسابك' using errcode = '42501';
  end if;
end $$;
-- المقرر الافتراضي لكل حساب: أول مقرر متاح له (الجاهز أولًا)؛ لا شيء إن لم يُسند له مقرر
create or replace function public._default_course() returns bigint
language sql stable security definer set search_path = public, pg_temp as $$
  select c.id from public.courses c where public._course_ok(c.id) order by (c.status = 'ready') desc, c.sort_order, c.id limit 1
$$;
-- مقرر الصف/الهدف/السؤال (للسياسات)
create or replace function public._course_of_lesson(p_lesson bigint) returns bigint
language sql stable security definer set search_path = public, pg_temp as $$
  select c.course_id from public.lessons l join public.chapters c on c.id = l.chapter_id where l.id = p_lesson
$$;
create or replace function public._course_of_objective(p_obj bigint) returns bigint
language sql stable security definer set search_path = public, pg_temp as $$
  select c.course_id from public.objectives o join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id where o.id = p_obj
$$;
create or replace function public._course_of_question(p_q bigint) returns bigint
language sql stable security definer set search_path = public, pg_temp as $$
  select c.course_id from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id
    join public.chapters c on c.id = l.chapter_id where q.id = p_q
$$;
-- الطلاب الذين يراهم الحساب الحالي: المعلم طلابه المسندون فقط، وغيره من الطاقم كل الطلاب
create or replace function public._visible_student(p_student uuid) returns boolean
language sql stable security definer set search_path = public, pg_temp as $$
  select case when (select role from public.profiles where user_id = auth.uid()) = 'viewer'
    then exists (select 1 from public.teacher_students ts where ts.teacher_id = auth.uid() and ts.student_id = p_student)
    else true end
$$;

-- سياسات القراءة المباشرة للجداول: تُقيَّد بالمقررات المتاحة للحساب
drop policy if exists courses_read on public.courses;
create policy courses_read on public.courses for select to authenticated
  using (public.is_member() and public._course_ok(id));
drop policy if exists chapters_read on public.chapters;
create policy chapters_read on public.chapters for select to authenticated using (public.is_member() and public._course_ok(course_id));
drop policy if exists lessons_read on public.lessons;
create policy lessons_read on public.lessons for select to authenticated using (public.is_member() and public._course_ok(public._course_of_lesson(id)));
drop policy if exists objectives_read on public.objectives;
create policy objectives_read on public.objectives for select to authenticated using (public.is_member() and public._course_ok(public._course_of_lesson(lesson_id)));
drop policy if exists supplements_read on public.supplements;
create policy supplements_read on public.supplements for select to authenticated using (public.is_member() and public._course_ok(public._course_of_objective(objective_id)));
drop policy if exists questions_read on public.questions;
create policy questions_read on public.questions for select to authenticated
  using (public.is_member() and (not excluded or public.is_reviewer()) and public._course_ok(public._course_of_objective(objective_id)));
drop policy if exists answers_read on public.question_answers;
create policy answers_read on public.question_answers for select to authenticated using (public.is_member() and public._course_ok(public._course_of_question(question_id)));

-- المقررات في الصفحة الأولى: المعلم يرى مقرراته المسندة فقط، وأعداد طلابه هو
create or replace function public.get_courses() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'code', c.code, 'title', c.title, 'grade', c.grade, 'term', c.term,
      'status', c.status, 'eta', c.eta, 'sortOrder', c.sort_order, 'kind', c.kind,
      'chapters', (select count(*) from chapters ch where ch.course_id = c.id),
      'objectives', (select count(*) from objectives o join lessons l on l.id = o.lesson_id join chapters ch on ch.id = l.chapter_id where ch.course_id = c.id),
      'questions', (select count(*) from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id join chapters ch on ch.id = l.chapter_id
                    where ch.course_id = c.id and not q.excluded),
      'approved', (select count(*) from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id join chapters ch on ch.id = l.chapter_id
                    where ch.course_id = c.id and not q.excluded and q.status = 'approved'),
      'students', (select count(*) from course_enrollments e join profiles p on p.user_id = e.user_id
                    where e.course_id = c.id and p.role = 'student' and public._visible_student(e.user_id)))
    order by c.sort_order, c.id), '[]')
    from courses c where public._course_ok(c.id));
end $$;

create or replace function public.get_stats(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  perform public._require_course(v_course);
  return public._stats_data(v_course);
end $$;

create or replace function public.get_chapters(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  perform public._require_course(v_course);
  return public._chapters_data(v_course);
end $$;

create or replace function public.get_chapter(p_number int, p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare c public.chapters; v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  perform public._require_course(v_course);
  select * into c from chapters where number = p_number and course_id = v_course;
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
  if not public._course_ok(c.course_id) then raise exception 'الهدف غير موجود' using errcode = 'P0002'; end if;
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

create or replace function public.get_bank(f jsonb default '{}') returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_ans boolean := public.is_member() and not public._restricted(); v_rev boolean := public.is_reviewer();
  v_course bigint := coalesce((f->>'course')::bigint, public._default_course());
begin
  perform public._require_member();
  perform public._require_course(v_course);
  -- البنك كاملًا بإجاباته لمالك المشروع والمراجع فقط؛ غيرهما يستلم الأسئلة دون إجابات
  return (select coalesce(jsonb_agg(public._q_public(q, a, v_ans) || jsonb_build_object('objectiveCode', o.code,
      'objectiveText', coalesce(o.approved_text, o.original_text),
      'lesson', jsonb_build_object('number', l.number, 'title', l.title),
      'chapter', jsonb_build_object('number', c.number, 'title', c.title))
      order by c.number, l.number, o.number, q.type desc, q.number), '[]')
    from questions q left join question_answers a on a.question_id = q.id
      join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id join chapters c on c.id = l.chapter_id
    where c.course_id = v_course
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
    from questions q join question_answers a on a.question_id = q.id
    where q.id = any(v_ids) and not q.excluded and public._course_ok(public._course_of_objective(q.objective_id)));
end $$;

create or replace function public.check_answer(p_question bigint, p_choice int) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare r record;
begin
  perform public._require_member();
  if p_choice is null or p_choice < 0 or p_choice > 3 then raise exception 'اختيار غير صالح'; end if;
  select q.id, a.correct_index, a.explanation, a.distractor_notes into r
    from public.questions q join public.question_answers a on a.question_id = q.id
    where q.id = p_question and q.type = 'mcq' and not q.excluded and p_choice < jsonb_array_length(q.options)
      and public._course_ok(public._course_of_objective(q.objective_id));
  if not found then raise exception 'السؤال غير موجود أو الاختيار غير صالح'; end if;
  return jsonb_build_object('correct', p_choice = r.correct_index, 'correctIndex', r.correct_index,
    'explanation', r.explanation, 'distractorNote', nullif(r.distractor_notes->>p_choice, ''));
end $$;

-- تقدم الطلاب: المعلم يرى طلابه المسندين فقط وعلى مقرر متاح له
create or replace function public.teacher_progress(p_section text default null, p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  perform public._require_course(v_course);
  if public.my_role() not in ('admin', 'viewer', 'reviewer') then raise exception 'تقدم الطلاب بالأسماء للمعلم ومالك المشروع؛ المؤشرات العامة في «لوحة المؤشرات»' using errcode = '42501'; end if;
  -- طلاب المقرر المختار، وإجاباتهم على أسئلة هذا المقرر فقط
  return (with en as (select e.user_id from course_enrollments e where e.course_id = v_course and public._visible_student(e.user_id)),
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
            from ans join profiles pr on pr.user_id = ans.user_id join en on en.user_id = ans.user_id
            where pr.role = 'student' and (p_section is null or pr.section = p_section)
            group by ans.objective_id having count(*) >= 5 order by 3, 2 desc limit 15) t
      join objectives o on o.id = t.objective_id join lessons l on l.id = o.lesson_id)));
end $$;

-- لوحة المؤشرات: مقرر متاح للحساب، وطلاب المعلم المسندون فقط في الأرقام
create or replace function public.get_dashboard(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_now timestamptz := now(); v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  perform public._require_course(v_course);
  -- كل الأرقام للمقرر المختار: طلابه المسندون، وإجاباتهم على أسئلته
  return (with cq as (select q.id, q.thinking_level, l.chapter_id from questions q join objectives o on o.id = q.objective_id
              join lessons l on l.id = o.lesson_id join chapters c on c.id = l.chapter_id where c.course_id = v_course),
    stu as (select p.* from profiles p join course_enrollments e on e.user_id = p.user_id and e.course_id = v_course where p.role = 'student' and public._visible_student(p.user_id)),
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

-- ---------- إسناد المقررات والطلاب للمعلم (لمالك المشروع) ----------
create or replace function public.admin_list_staff() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', pr.user_id, 'username', split_part(u.email, '@', 1), 'name', pr.display_name,
      'role', pr.role, 'createdAt', pr.created_at, 'lastSignIn', u.last_sign_in_at, 'self', pr.user_id = auth.uid(),
      'assignedCourses', case when pr.role = 'viewer' then (select count(*) from teacher_courses t where t.teacher_id = pr.user_id) end,
      'assignedStudents', case when pr.role = 'viewer' then (select count(*) from teacher_students t where t.teacher_id = pr.user_id) end)
      order by case pr.role when 'admin' then 0 when 'reviewer' then 1 when 'supervisor' then 2 when 'principal' then 3 when 'viewer' then 4 else 5 end, pr.display_name), '[]')
    from profiles pr join auth.users u on u.id = pr.user_id
    where pr.role in ('admin', 'reviewer', 'viewer', 'supervisor', 'principal') or (pr.role = 'pending' and (pr.staff or not pr.managed)));
end $$;

create or replace function public.admin_get_teacher(p_id uuid) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  if not exists (select 1 from profiles where user_id = p_id and role = 'viewer') then raise exception 'الحساب ليس حساب معلم'; end if;
  return jsonb_build_object(
    'courses', (select coalesce(jsonb_agg(course_id order by course_id), '[]') from teacher_courses where teacher_id = p_id),
    'students', (select coalesce(jsonb_agg(student_id), '[]') from teacher_students where teacher_id = p_id));
end $$;

-- يستبدل إسناد المعلم كاملًا: المقررات والطلاب. الطلاب المسندون حسابات طلاب مُدارة فقط.
create or replace function public.admin_set_teacher(p_id uuid, p_courses bigint[], p_students uuid[]) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_c int; v_s int;
begin
  perform public._require_admin();
  if not exists (select 1 from profiles where user_id = p_id and role = 'viewer') then raise exception 'الحساب ليس حساب معلم'; end if;
  p_courses := coalesce(p_courses, '{}'); p_students := coalesce(p_students, '{}');
  if cardinality(p_students) > 2000 then raise exception 'عدد الطلاب كبير'; end if;
  delete from teacher_courses where teacher_id = p_id;
  insert into teacher_courses (teacher_id, course_id) select p_id, c.id from courses c where c.id = any(p_courses);
  get diagnostics v_c = row_count;
  delete from teacher_students where teacher_id = p_id;
  insert into teacher_students (teacher_id, student_id)
    select p_id, p.user_id from profiles p where p.user_id = any(p_students) and p.role = 'student' and p.managed and not p.staff;
  get diagnostics v_s = row_count;
  return jsonb_build_object('courses', v_c, 'students', v_s);
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.admin_get_teacher(uuid), public.admin_set_teacher(uuid, bigint[], uuid[]), public.admin_list_staff() to authenticated;
-- سياسات RLS تستدعي هذه الدوال بدور المستخدم: تُمنح للمستخدم المسجل (تكشف له فقط أن المقرر متاح أم لا ورقم مقرر السؤال)
grant execute on function public._course_ok(bigint), public._course_of_lesson(bigint), public._course_of_objective(bigint), public._course_of_question(bigint) to authenticated;
-- الدوال الداخلية الأخرى لا تُستدعى من الواجهة
revoke execute on function public._require_course(bigint), public._default_course(), public._visible_student(uuid) from authenticated;

-- =====================================================================
-- 2026-10-18: قائمة التميّز — ترتيب المتدربين في الشعبة
--   النقاط تكافئ التدريب الجاد والمنتظم لا التخمين: صافي الإجابات (+1 صحيحة، −1/(عدد البدائل − 1) خاطئة: −½ لثلاثة بدائل و−⅓ لأربعة، 2026-10-26، مضروبًا في معامل المستوى: أساسي ×1، تطبيق ×1.1، تفكير عليا ×1.2)،
--   إجابات أسرع من 3 ثوانٍ لا تُحسب، وأول 50 إجابة صالحة في اليوم فقط، و+3 لكل يوم تدريب جاد (حتى 20)،
--   والمحاولة الثانية لسؤال سبق أن أجاب عنه: +½ صحيحة و−½ خاطئة (بلا معامل مستوى، وما بعدها لا يُحتسب؛ 2026-10-26 بدل +1 لتصحيح الخطأ).
--   شرط دخول الترتيب: 30 إجابة صالحة في 3 أيام على الأقل.
--   إضافات قراءة فقط: لا تعدّل ولا تحذف أي شيء من جلسات التدريب وإجابات الطلاب.
-- =====================================================================
alter table public.profiles add column if not exists rank_since timestamptz;
create table if not exists public.rank_terms (
  id bigint generated by default as identity primary key,
  started_at timestamptz not null,
  started_by uuid,
  note text
);
alter table public.rank_terms enable row level security;
revoke all on public.rank_terms from anon, authenticated;
-- بداية أول فصل: من أول جلسة تدريب موجودة (فلا يضيع شيء مما تدرّب عليه الطلاب)
insert into public.rank_terms (started_at, note)
  select coalesce((select min(created_at) from public.practice_sessions), now()), 'بداية احتساب نقاط التميّز'
  where not exists (select 1 from public.rank_terms);

-- حد «قريب من التخمين» للمقرر بالنسبة المئوية: 1.2 × احتمال الإصابة عشوائيًا (2026-10-26)
--   ثلاثة بدائل (كيمياء 2-1) → 40%، وأربعة بدائل (كيمياء 1 و3) → 30% كما كان
create or replace function public._guess_floor(p_course bigint) returns numeric
language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce(round(120 * avg(1.0 / jsonb_array_length(q.options))), 30)
  from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id
  join public.chapters c on c.id = l.chapter_id
  where c.course_id = p_course and q.type = 'mcq' and jsonb_array_length(q.options) > 1
$$;
revoke execute on function public._guess_floor(bigint) from anon, public;

-- نقاط كل طالب في المقرر (داخلية): تُستدعى من الدوال المحمية أدناه فقط
drop function if exists public._rank_rows(bigint, uuid[]);
create or replace function public._rank_rows(p_course bigint, p_ids uuid[])
returns table (user_id uuid, attempts int, valid int, correct int, rushed int, days_any int, days_active int, repeats int, net numeric, score numeric, weeks_kept int, repeat_net numeric)
language sql stable security definer set search_path = public, pg_temp as $$
  with term as (select max(started_at) s from public.rank_terms),
  gf as (select public._guess_floor(p_course) f),
  cq as (select q.id, public._level_group(q.thinking_level) g, jsonb_array_length(q.options) k from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id
         join public.chapters c on c.id = l.chapter_id where c.course_id = p_course),
  raw as (
    select s.user_id, a.session_id, a.question_id, a.correct, a.answered_at, cq.g, cq.k,
      extract(epoch from (a.answered_at - coalesce(lag(a.answered_at) over (partition by a.session_id order by a.answered_at), s.created_at))) as secs
    from public.practice_answers a join public.practice_sessions s on s.id = a.session_id join cq on cq.id = a.question_id
    where s.user_id = any(p_ids)),
  win as (select r.* from raw r join public.profiles p on p.user_id = r.user_id
          where r.answered_at >= greatest((select s from term), coalesce(p.rank_since, '-infinity'::timestamptz))),
  ranked as (select w.*, row_number() over (partition by w.user_id, w.question_id order by w.answered_at) rn from win w),
  first as (select * from ranked where rn = 1),
  valid as (select f.*, (f.answered_at at time zone 'Asia/Riyadh')::date d,
              row_number() over (partition by f.user_id, (f.answered_at at time zone 'Asia/Riyadh')::date order by f.answered_at) dn
            from first f where f.secs >= 3),
  -- المحاولة الثانية لكل سؤال فقط (والأسرع من 3 ثوانٍ لا تُحتسب): +½ صحيحة و−½ خاطئة
  rep as (select r.user_id, count(*)::int n, sum(case when r.correct then 0.5 else -0.5 end) net from ranked r
          where r.rn = 2 and r.secs >= 3 group by 1),
  wk as (select v.user_id, (date_trunc('week', v.d + 1) - interval '1 day')::date w, count(*) n, count(distinct v.d) dys, count(*) filter (where v.correct) c
         from valid v group by 1, 2),
  -- تجميعات لكل طالب بمرور واحد على كل مجموعة (بدل استعلامات فرعية مترابطة لكل طالب فتتضاعف التكلفة مع عدد الطلاب)
  fa as (select f.user_id, count(*)::int attempts, (count(*) filter (where f.secs < 3))::int rushed from first f group by 1),
  va as (select v.user_id, count(*)::int valid, (count(*) filter (where v.correct))::int correct, count(distinct v.d)::int days_any,
           coalesce(sum((case v.g when 'higher' then 1.2 when 'apply' then 1.1 else 1.0 end) * (case when v.correct then 1 else -1.0 / greatest(v.k - 1, 1) end)) filter (where v.dn <= 50), 0) net
         from valid v group by 1),
  da as (select z.user_id, count(*)::int n from (select v.user_id, v.d from valid v group by v.user_id, v.d
           having count(*) >= 10 and 2 * count(*) filter (where v.correct) >= count(*)) z group by 1),
  wc as (select wk.user_id, count(*)::int n from wk where wk.n >= 30 and wk.dys >= 3 and 100.0 * wk.c / wk.n > (select f from gf) group by 1),
  agg as (
    select u.user_id, coalesce(wc.n, 0) weeks_kept, coalesce(fa.attempts, 0) attempts, coalesce(va.valid, 0) valid, coalesce(va.correct, 0) correct,
      coalesce(fa.rushed, 0) rushed, coalesce(va.days_any, 0) days_any, coalesce(da.n, 0) days_active, coalesce(rep.n, 0) repeats, coalesce(rep.net, 0) repeat_net, coalesce(va.net, 0) net
    from unnest(p_ids) as u(user_id)
      left join fa on fa.user_id = u.user_id left join va on va.user_id = u.user_id left join da on da.user_id = u.user_id
      left join wc on wc.user_id = u.user_id left join rep on rep.user_id = u.user_id)
  select user_id, attempts, valid, correct, rushed, days_any, days_active, repeats, round(net, 1),
    round(greatest(net + 3 * least(days_active, 20) + repeat_net + 2 * weeks_kept, 0), 1), weeks_kept, repeat_net
  from agg
$$;

-- قائمة التميّز للطالب: أفضل 5 في شعبته (بالاسم كاملًا) وترتيبه هو
create or replace function public.student_leaderboard(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare me public.profiles; v_course bigint; v_ids uuid[]; v_res jsonb;
  v_rules jsonb := jsonb_build_object('minValid', 30, 'minDays', 3, 'rushSecs', 3, 'dailyCap', 50, 'dayBonus', 3, 'dayCap', 20, 'dayMin', 10, 'dayAcc', 50, 'weekBonus', 2, 'weekValid', 30, 'weekDays', 3, 'repeatPts', 0.5, 'rushMaxPct', 40);
begin
  perform public._require_student();
  select * into me from profiles where user_id = auth.uid();
  select c.id into v_course from course_enrollments e join courses c on c.id = e.course_id and c.status = 'ready'
    where e.user_id = auth.uid() and (p_course is null or c.id = p_course) order by c.sort_order, c.id limit 1;
  if v_course is not null then v_rules := v_rules || jsonb_build_object('guessFloor', public._guess_floor(v_course)); end if;
  if v_course is null or coalesce(trim(me.section), '') = '' then
    return jsonb_build_object('available', false, 'reason', case when v_course is null then 'course' else 'section' end, 'rules', v_rules);
  end if;
  select array_agg(p.user_id) into v_ids from profiles p join course_enrollments e on e.user_id = p.user_id and e.course_id = v_course
    where p.role = 'student' and p.section = me.section;
  with rws as materialized (
    select r.*, p.display_name nm,
      (r.valid >= 30 and r.days_any >= 3 and (r.attempts = 0 or 100.0 * r.rushed / r.attempts <= 40)) elig
    from public._rank_rows(v_course, v_ids) r join public.profiles p on p.user_id = r.user_id),
  ranked as materialized (
    select w.*, case when w.elig then row_number() over (partition by w.elig order by w.score desc, (w.correct::numeric / nullif(w.valid, 0)) desc nulls last, w.days_any desc, w.user_id) end rnk
    from rws w),
  st as (select count(*) filter (where elig)::int n from ranked),
  med as (select score from ranked, st where elig and rnk = ceil(st.n / 2.0)::int),
  mine as (select m.*, case when m.rnk is null then null when m.rnk <= ceil(st.n / 2.0) then 'top' when m.rnk <= ceil(st.n * 0.75) then 'q3' else 'q4' end band
           from ranked m, st where m.user_id = auth.uid())
  select jsonb_build_object('available', true, 'courseId', v_course, 'section', me.section, 'rules', v_rules,
    'n', (select n from st), 'classSize', cardinality(v_ids),
    'me', jsonb_build_object('eligible', coalesce((select elig from mine), false), 'rank', (select case when band = 'top' then rnk end from mine), 'band', (select band from mine),
      'score', coalesce((select score from mine), 0), 'net', coalesce((select net from mine), 0), 'valid', coalesce((select valid from mine), 0),
      'attempts', coalesce((select attempts from mine), 0), 'correct', coalesce((select correct from mine), 0), 'activeDays', coalesce((select days_any from mine), 0),
      'repeats', coalesce((select repeats from mine), 0), 'repeatNet', coalesce((select repeat_net from mine), 0),
      'fast', coalesce((select attempts >= 10 and 100.0 * rushed / nullif(attempts, 0) > 40 from mine), false),
      'needValid', greatest(0, 30 - coalesce((select valid from mine), 0)), 'needDays', greatest(0, 3 - coalesce((select days_any from mine), 0)),
      'pointsToMedian', (select case when band in ('q3', 'q4') then greatest(0.1, round((select score from med) - mine.score + 0.1, 1)) end from mine)),
    'top', (select coalesce(jsonb_agg(jsonb_build_object('rank', t.rnk, 'name', t.nm, 'score', t.score, 'me', t.user_id = auth.uid()) order by t.rnk), '[]')
      from (select x.rnk, x.score, x.user_id,
              trim(regexp_replace(x.nm, '\s+', ' ', 'g')) nm
            from ranked x where x.elig and x.rnk <= 5) t))
  into v_res;
  return v_res;
end $$;

-- جودة التدريب للمعلم والمالك والمراجع: طلاب المعلم المسندون فقط
create or replace function public.teacher_training_quality(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course()); v_ids uuid[];
begin
  perform public._require_member();
  perform public._require_course(v_course);
  if public.my_role() not in ('admin', 'viewer', 'reviewer') then raise exception 'للمعلم ومالك المشروع' using errcode = '42501'; end if;
  select array_agg(e.user_id) into v_ids from course_enrollments e join profiles p on p.user_id = e.user_id
    where e.course_id = v_course and p.role = 'student' and public._visible_student(e.user_id);
  return (select coalesce(jsonb_agg(jsonb_build_object('username', split_part(u.email, '@', 1), 'score', r.score, 'valid', r.valid, 'attempts', r.attempts,
      'accuracy', case when r.valid > 0 then round(100.0 * r.correct / r.valid) end, 'fastPct', case when r.attempts > 0 then round(100.0 * r.rushed / r.attempts) end,
      'activeDays', r.days_any,
      -- يحتاج متابعة: إجابات سريعة جدًا، أو نسبة صحة قريبة من التخمين (_guess_floor: 40% لثلاثة بدائل، 30% لأربعة)
      'quality', case when r.attempts >= 10 and 100.0 * r.rushed / r.attempts > 40 then 'watch'
                      when r.valid >= 30 and 100.0 * r.correct / r.valid <= public._guess_floor(v_course) then 'watch'
                      when r.valid >= 30 then 'serious' else 'low' end)), '[]')
    from public._rank_rows(v_course, coalesce(v_ids, '{}')) r join auth.users u on u.id = r.user_id);
end $$;

-- بدء فصل دراسي جديد: تُصفَّر النقاط (لا يُحذف شيء من سجل التدريب)
create or replace function public.admin_get_rank_term() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  return jsonb_build_object('startedAt', (select max(started_at) from rank_terms), 'terms', (select count(*) from rank_terms));
end $$;
create or replace function public.admin_start_new_term(p_note text default null) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  insert into rank_terms (started_at, started_by, note) values (now(), auth.uid(), nullif(trim(coalesce(p_note, '')), ''));
  return public.admin_get_rank_term();
end $$;

-- نقل الطالب إلى صف آخر يصفّر نقاطه (يبدأ احتسابه من لحظة النقل)؛ باقي السلوك كما كان
create or replace function public.admin_update_student(p_id uuid, p_name text, p_section text, p_role text, p_grade text default null) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if not exists (select 1 from profiles where user_id = auth.uid() and role = 'admin') then raise exception 'للمشرف فقط' using errcode = '42501'; end if;
  if p_role not in ('student', 'pending') then raise exception 'الدور غير صالح'; end if;
  if not exists (select 1 from profiles where user_id = p_id and managed and role in ('student', 'pending')) then raise exception 'الحساب ليس حساب طالب'; end if;
  update profiles set display_name = coalesce(nullif(trim(p_name), ''), display_name), section = nullif(trim(p_section), ''),
    rank_since = case when grade is not null and nullif(trim(p_grade), '') is not null and grade is distinct from nullif(trim(p_grade), '') then now() else rank_since end,
    grade = nullif(trim(p_grade), ''), role = p_role where user_id = p_id;
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.student_leaderboard(bigint), public.teacher_training_quality(bigint), public.admin_get_rank_term(),
  public.admin_start_new_term(text), public.admin_update_student(uuid, text, text, text, text) to authenticated;
revoke execute on function public._rank_rows(bigint, uuid[]) from authenticated;

-- =====================================================================
-- 2026-10-19: الرصيد — استبدال نقاط التميّز بدرجات
--   كل 50 نقطة (يضبطها المالك) = درجة تُضاف إلى رصيد الطالب ويرصدها المعلم.
--   نقاط الترتيب لا تنقص أبدًا: «المتاح» = نقاط الفصل − ما استُبدل منها في الفصل نفسه.
--   شروط: ألا يكون «يحتاج متابعة»، وسقف أسبوعي (افتراضيًا درجتان)، ومفتاح إيقاف بسبب.
--   مكافأة «يوم تدريب جاد» (+3) تشترط الآن صحة 50% فأكثر في ذلك اليوم حتى لا تُنال بالتخمين.
--   إضافات فقط: لا تعدّل ولا تحذف شيئًا من جلسات التدريب وإجابات الطلاب.
-- =====================================================================
create table if not exists public.grade_settings (
  id int primary key default 1 check (id = 1),
  points_per_grade int not null default 50 check (points_per_grade between 1 and 10000),
  weekly_cap int not null default 2 check (weekly_cap between 0 and 50),
  enabled boolean not null default true,
  disabled_reason text,
  updated_at timestamptz not null default now(),
  updated_by uuid
);
alter table public.grade_settings add column if not exists teacher_coupon_max int not null default 200 check (teacher_coupon_max between 1 and 500);
alter table public.grade_settings add column if not exists teacher_weekly_quota int not null default 300 check (teacher_weekly_quota between 0 and 100000);
insert into public.grade_settings (id) values (1) on conflict (id) do nothing;
create table if not exists public.grade_redemptions (
  id bigint generated by default as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  course_id bigint not null,
  grades int not null check (grades > 0),
  points int not null check (points > 0),
  status text not null default 'pending' check (status in ('pending', 'recorded', 'cancelled')),
  created_at timestamptz not null default now(),
  recorded_at timestamptz, recorded_by uuid,
  cancelled_at timestamptz, cancelled_by uuid, cancel_reason text
);
create index if not exists grade_redemptions_user_idx on public.grade_redemptions (user_id, created_at);
create index if not exists grade_redemptions_course_idx on public.grade_redemptions (course_id, status);
-- كوبونات النقاط: يصدرها المعلم أو المالك، ويدخل الطالب الكود فتزيد نقاطه المتاحة (لا تدخل في نقاط الترتيب)
create table if not exists public.point_coupons (
  id bigint generated by default as identity primary key,
  code text not null unique,
  points int not null check (points between 1 and 500),
  note text,
  created_by uuid not null,
  created_by_name text,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  status text not null default 'active' check (status in ('active', 'redeemed', 'cancelled')),
  redeemed_by uuid, redeemed_course bigint, redeemed_at timestamptz,
  cancelled_at timestamptz
);
create index if not exists point_coupons_user_idx on public.point_coupons (redeemed_by, redeemed_at);
create table if not exists public.coupon_attempts (id bigint generated by default as identity primary key, user_id uuid not null, at timestamptz not null default now());
create index if not exists coupon_attempts_idx on public.coupon_attempts (user_id, at);
alter table public.point_coupons enable row level security;
alter table public.coupon_attempts enable row level security;
revoke all on public.point_coupons, public.coupon_attempts from anon, authenticated;
alter table public.grade_settings enable row level security;
alter table public.grade_redemptions enable row level security;
revoke all on public.grade_settings, public.grade_redemptions from anon, authenticated;

-- أيام التدريب الصالحة لطالب في نافذة الفصل الحالية (نفس قواعد _rank_rows)
create or replace function public._rank_days(p_course bigint, p_user uuid)
returns table (d date, valid int, correct int)
language sql stable security definer set search_path = public, pg_temp as $$
  with term as (select max(started_at) s from public.rank_terms),
  cq as (select q.id from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id
         join public.chapters c on c.id = l.chapter_id where c.course_id = p_course),
  raw as (
    select a.question_id, a.correct, a.answered_at,
      extract(epoch from (a.answered_at - coalesce(lag(a.answered_at) over (partition by a.session_id order by a.answered_at), s.created_at))) as secs
    from public.practice_answers a join public.practice_sessions s on s.id = a.session_id
    where s.user_id = p_user and a.question_id in (select id from cq)),
  win as (select r.* from raw r join public.profiles p on p.user_id = p_user
          where r.answered_at >= greatest((select s from term), coalesce(p.rank_since, '-infinity'::timestamptz))),
  first as (select * from (select w.*, row_number() over (partition by w.question_id order by w.answered_at) rn from win w) x where rn = 1)
  select (f.answered_at at time zone 'Asia/Riyadh')::date, count(*)::int, (count(*) filter (where f.correct))::int
  from first f where f.secs >= 3 group by 1
$$;

-- حالة رصيد الطالب (داخلية)
drop function if exists public._grade_state(uuid, bigint);
create or replace function public._grade_state(p_user uuid, p_course bigint)
returns table (score numeric, valid int, attempts int, correct int, rushed int, days_any int, elig boolean, watch boolean, spent int, week_used int, weeks_kept int, bonus int)
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare r record; v_since timestamptz; v_week timestamptz;
begin
  select * into r from public._rank_rows(p_course, array[p_user]);
  select greatest((select max(started_at) from rank_terms), coalesce(p.rank_since, '-infinity'::timestamptz)) into v_since from profiles p where p.user_id = p_user;
  v_week := (date_trunc('week', (now() at time zone 'Asia/Riyadh') + interval '1 day') - interval '1 day') at time zone 'Asia/Riyadh';
  score := coalesce(r.score, 0); valid := coalesce(r.valid, 0); attempts := coalesce(r.attempts, 0); correct := coalesce(r.correct, 0);
  rushed := coalesce(r.rushed, 0); days_any := coalesce(r.days_any, 0); weeks_kept := coalesce(r.weeks_kept, 0);
  elig := valid >= 30 and days_any >= 3 and (attempts = 0 or 100.0 * rushed / attempts <= 40);
  watch := (attempts >= 10 and 100.0 * rushed / attempts > 40) or (valid >= 30 and 100.0 * correct / valid <= public._guess_floor(p_course));
  select coalesce(sum(g.points), 0)::int into spent from grade_redemptions g
    where g.user_id = p_user and g.course_id = p_course and g.status <> 'cancelled' and g.created_at >= v_since;
  select coalesce(sum(c.points), 0)::int into bonus from point_coupons c
    where c.redeemed_by = p_user and c.redeemed_course = p_course and c.status = 'redeemed' and c.redeemed_at >= v_since;
  -- مكافآت المهام المنجزة في الموعد (لا تدخل نقاط الترتيب، كالكوبونات)
  bonus := bonus + coalesce((select sum(cr.reward_pts) from comm_recipients cr join comms cm on cm.id = cr.comm_id
    where cr.student_id = p_user and cr.status = 'done' and cr.reward_pts > 0 and cm.course_id = p_course and cr.done_at >= v_since), 0)::int;
  select coalesce(sum(g.grades), 0)::int into week_used from grade_redemptions g
    where g.user_id = p_user and g.status <> 'cancelled' and g.created_at >= v_week;
  return next;
end $$;

create or replace function public._student_course(p_course bigint) returns bigint
language sql stable security definer set search_path = public, pg_temp as $$
  select c.id from course_enrollments e join courses c on c.id = e.course_id and c.status = 'ready'
  where e.user_id = auth.uid() and (p_course is null or c.id = p_course) order by c.sort_order, c.id limit 1
$$;

-- رصيد الطالب: النقاط المتاحة والدرجات وسجل الاستبدال
create or replace function public.student_balance(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint; s record; g public.grade_settings; v_pending int; v_recorded int; v_streak int := 0;
  v_today date := (now() at time zone 'Asia/Riyadh')::date; v_wstart date; v_wv int := 0; v_wd int := 0; v_wc int := 0; v_tv int := 0; v_tc int := 0; v_avail numeric; v_blocked text; v_ready int; v_left int;
begin
  perform public._require_student();
  v_course := public._student_course(p_course);
  select * into g from grade_settings where id = 1;
  if v_course is null then return jsonb_build_object('available', false, 'reason', 'course'); end if;
  select * into s from public._grade_state(auth.uid(), v_course);
  v_avail := greatest(s.score + s.bonus - s.spent, 0);
  v_ready := floor(v_avail / g.points_per_grade)::int;
  v_left := greatest(g.weekly_cap - s.week_used, 0);
  v_blocked := case when not g.enabled then 'disabled' when s.watch then 'watch'
    when v_left = 0 then 'weeklyCap' when v_ready < 1 then 'insufficient' end;
  select coalesce(sum(grades) filter (where status = 'pending'), 0), coalesce(sum(grades) filter (where status = 'recorded'), 0)
    into v_pending, v_recorded from grade_redemptions where user_id = auth.uid() and course_id = v_course;
  v_wstart := (date_trunc('week', v_today + 1) - interval '1 day')::date;
  select coalesce(sum(valid), 0), coalesce(sum(correct), 0) into v_tv, v_tc from public._rank_days(v_course, auth.uid()) where d = v_today;
  select coalesce(sum(valid), 0), count(*), coalesce(sum(correct), 0) into v_wv, v_wd, v_wc from public._rank_days(v_course, auth.uid()) where d >= v_wstart;
  select coalesce(max(n) filter (where last_d >= v_today - 1), 0) into v_streak from (
    select max(d) last_d, count(*)::int n from (
      select d, d - (row_number() over (order by d))::int grp from public._rank_days(v_course, auth.uid()) where valid >= 10 and 2 * correct >= valid) z group by grp) y;
  return jsonb_build_object('available', true, 'courseId', v_course,
    'settings', jsonb_build_object('rate', g.points_per_grade, 'weeklyCap', g.weekly_cap, 'enabled', g.enabled, 'reason', g.disabled_reason),
    'points', round(v_avail, 1), 'score', s.score, 'spent', s.spent, 'bonus', s.bonus, 'ready', v_ready,
    'toNext', round(g.points_per_grade - (v_avail - v_ready * g.points_per_grade), 1),
    'pending', v_pending, 'recorded', v_recorded, 'weekUsed', s.week_used, 'weekLeft', v_left,
    'eligible', s.elig, 'blocked', v_blocked, 'needValid', greatest(0, 30 - s.valid), 'needDays', greatest(0, 3 - s.days_any),
    'streak', v_streak, 'weeksKept', s.weeks_kept,
    'week', jsonb_build_object('valid', v_wv, 'days', v_wd, 'accuracy', round(100.0 * v_wc / nullif(v_wv, 0)), 'floor', public._guess_floor(v_course), 'kept', v_wv >= 30 and v_wd >= 3 and coalesce(100.0 * v_wc / nullif(v_wv, 0) > public._guess_floor(v_course), false)), 'today', jsonb_build_object('valid', v_tv, 'correct', v_tc, 'done', v_tv >= 10 and 2 * v_tc >= v_tv),
    'history', (select coalesce(jsonb_agg(jsonb_build_object('id', h.id, 'grades', h.grades, 'points', h.points, 'status', h.status, 'at', h.created_at,
        'recordedAt', h.recorded_at, 'reason', h.cancel_reason) order by h.created_at desc), '[]')
      from (select * from grade_redemptions where user_id = auth.uid() order by created_at desc limit 30) h));
end $$;

-- استبدال النقاط بدرجات: خصم فوري، وللمعلم حق الإلغاء بسبب
create or replace function public.student_redeem(p_grades int default 1, p_course bigint default null) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_course bigint; s record; g public.grade_settings; v_cost int; v_avail numeric;
begin
  perform public._require_student();
  if p_grades is null or p_grades < 1 or p_grades > 10 then raise exception 'عدد الدرجات غير صالح'; end if;
  v_course := public._student_course(p_course);
  if v_course is null then raise exception 'لم يُسند لك مقرر جاهز بعد'; end if;
  perform pg_advisory_xact_lock(hashtextextended('grade:' || auth.uid()::text, 0));
  select * into g from grade_settings where id = 1;
  if not g.enabled then raise exception 'الاستبدال متوقف مؤقتًا%', case when coalesce(g.disabled_reason, '') <> '' then ': ' || g.disabled_reason else '' end; end if;
  select * into s from public._grade_state(auth.uid(), v_course);
  if s.watch then raise exception 'تدريبك يحتاج متابعة؛ تأنَّ في الإجابة ثم عاود الاستبدال'; end if;
  if s.week_used + p_grades > g.weekly_cap then raise exception 'سقف الاستبدال هذا الأسبوع % درجات (استبدلت %)', g.weekly_cap, s.week_used; end if;
  v_cost := p_grades * g.points_per_grade;
  v_avail := greatest(s.score + s.bonus - s.spent, 0);
  if v_avail < v_cost then raise exception 'نقاطك المتاحة % لا تكفي (المطلوب %)', v_avail, v_cost; end if;
  insert into grade_redemptions (user_id, course_id, grades, points) values (auth.uid(), v_course, p_grades, v_cost);
  return public.student_balance(v_course);
end $$;

-- المعلم: رصيد درجات طلابه المسندين
create or replace function public._require_grade_staff(p_write boolean) returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  if public.my_role() not in ('admin', 'viewer') and (p_write or public.my_role() <> 'reviewer') then raise exception 'للمعلم ومالك المشروع' using errcode = '42501'; end if;
end $$;

create or replace function public.teacher_grade_balances(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_grade_staff(false);
  perform public._require_course(v_course);
  return (select coalesce(jsonb_agg(x order by (x->>'pending')::int desc, x->>'name'), '[]') from (
    select jsonb_build_object('userId', p.user_id, 'username', split_part(u.email, '@', 1), 'name', p.display_name, 'grade', p.grade, 'section', p.section,
      'pending', coalesce(sum(g.grades) filter (where g.status = 'pending'), 0), 'recorded', coalesce(sum(g.grades) filter (where g.status = 'recorded'), 0),
      'lastAt', max(g.created_at), 'oldestPending', min(g.created_at) filter (where g.status = 'pending'),
      'items', (select coalesce(jsonb_agg(jsonb_build_object('id', h.id, 'grades', h.grades, 'points', h.points, 'status', h.status, 'at', h.created_at,
          'recordedAt', h.recorded_at, 'reason', h.cancel_reason) order by h.created_at desc), '[]')
        from (select * from grade_redemptions h2 where h2.user_id = p.user_id and h2.course_id = v_course order by h2.created_at desc limit 20) h)) x
    from grade_redemptions g join profiles p on p.user_id = g.user_id join auth.users u on u.id = g.user_id
    where g.course_id = v_course and g.status <> 'cancelled' and public._visible_student(g.user_id)
    group by p.user_id, u.email, p.display_name, p.grade, p.section) q);
end $$;

-- رصد درجات عدة طلاب دفعة واحدة (المعروضون بعد التصفية): pending → recorded، لطلاب المعلم المسندين فقط
create or replace function public.teacher_record_grades_many(p_users uuid[], p_course bigint default null) returns int
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course()); v_n int;
begin
  perform public._require_grade_staff(true);
  perform public._require_course(v_course);
  if p_users is null or cardinality(p_users) = 0 then return 0; end if;
  update grade_redemptions g set status = 'recorded', recorded_at = now(), recorded_by = auth.uid()
    where g.status = 'pending' and g.course_id = v_course and g.user_id = any(p_users) and public._visible_student(g.user_id);
  get diagnostics v_n = row_count;
  return v_n;
end $$;

-- رصد درجات طالب (أو كل طلابه إن لم يُحدَّد): pending → recorded
create or replace function public.teacher_record_grades(p_user uuid default null, p_course bigint default null) returns int
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course()); v_n int;
begin
  perform public._require_grade_staff(true);
  perform public._require_course(v_course);
  update grade_redemptions g set status = 'recorded', recorded_at = now(), recorded_by = auth.uid()
    where g.status = 'pending' and g.course_id = v_course and (p_user is null or g.user_id = p_user) and public._visible_student(g.user_id);
  get diagnostics v_n = row_count;
  return v_n;
end $$;

-- إلغاء استبدال لم يُرصد بعد مع ذكر السبب؛ تعود النقاط للطالب
create or replace function public.teacher_cancel_redemption(p_id bigint, p_reason text) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
declare g public.grade_redemptions;
begin
  perform public._require_grade_staff(true);
  if length(trim(coalesce(p_reason, ''))) < 3 then raise exception 'اكتب سبب الإلغاء'; end if;
  select * into g from grade_redemptions where id = p_id for update;
  if not found or not public._visible_student(g.user_id) then raise exception 'الاستبدال غير موجود'; end if;
  if g.status <> 'pending' then raise exception 'لا يمكن إلغاء درجة رُصدت أو أُلغيت سابقًا'; end if;
  update grade_redemptions set status = 'cancelled', cancelled_at = now(), cancelled_by = auth.uid(), cancel_reason = trim(p_reason) where id = p_id;
end $$;

-- إعدادات المالك: عدد النقاط للدرجة، السقف الأسبوعي، الإيقاف المؤقت بسببه
create or replace function public.admin_get_grade_settings() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  return (select jsonb_build_object('rate', points_per_grade, 'weeklyCap', weekly_cap, 'enabled', enabled, 'reason', disabled_reason,
    'couponMax', teacher_coupon_max, 'couponQuota', teacher_weekly_quota) from grade_settings where id = 1);
end $$;
drop function if exists public.admin_set_grade_settings(int, int, boolean, text);
create or replace function public.admin_set_grade_settings(p_rate int, p_weekly int, p_enabled boolean, p_reason text default null, p_coupon_max int default null, p_coupon_quota int default null) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  if p_rate is null or p_rate < 1 then raise exception 'عدد النقاط غير صالح'; end if;
  if p_weekly is null or p_weekly < 0 then raise exception 'السقف الأسبوعي غير صالح'; end if;
  if not p_enabled and length(trim(coalesce(p_reason, ''))) < 3 then raise exception 'اكتب سبب إيقاف الاستبدال'; end if;
  if p_coupon_max is not null and (p_coupon_max < 1 or p_coupon_max > 500) then raise exception 'حد كوبون المعلم بين 1 و500'; end if;
  if p_coupon_quota is not null and p_coupon_quota < 0 then raise exception 'حصة المعلم الأسبوعية غير صالحة'; end if;
  update grade_settings set teacher_coupon_max = coalesce(p_coupon_max, teacher_coupon_max), teacher_weekly_quota = coalesce(p_coupon_quota, teacher_weekly_quota),
    points_per_grade = p_rate, weekly_cap = p_weekly, enabled = p_enabled,
    disabled_reason = case when p_enabled then null else trim(p_reason) end, updated_at = now(), updated_by = auth.uid() where id = 1;
  return public.admin_get_grade_settings();
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.student_balance(bigint), public.student_redeem(int, bigint), public.teacher_grade_balances(bigint),
  public.teacher_record_grades(uuid, bigint), public.teacher_record_grades_many(uuid[], bigint), public.teacher_cancel_redemption(bigint, text),
  public.admin_get_grade_settings(), public.admin_set_grade_settings(int, int, boolean, text, int, int) to authenticated;
revoke execute on function public._rank_days(bigint, uuid), public._grade_state(uuid, bigint), public._student_course(bigint), public._require_grade_staff(boolean) from authenticated;

-- =====================================================================
-- 2026-10-19: الإبلاغ عن مشكلة في سؤال (من الطالب إلى مالك المشروع والمراجع العلمي فقط)
--   يصل البلاغ إلى «الملاحظات» (source = 'student') دون اسم الطالب. للمالك تعديل السؤال وإغلاق الملاحظة، وله وللمراجع حذف البلاغ الخاطئ.
--   حماية: بلاغ واحد مفتوح لكل طالب على السؤال الواحد، و20 بلاغًا كحد أقصى في اليوم.
-- =====================================================================
create or replace function public.student_report_question(p_question bigint, p_reason text, p_body text default null) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
declare q public.questions; o public.objectives; v_label text; v_detail text := nullif(trim(coalesce(p_body, '')), '');
begin
  perform public._require_student();
  v_label := case p_reason when 'answer' then 'الإجابة الصحيحة غير صحيحة' when 'wording' then 'خطأ في صياغة السؤال أو البدائل'
    when 'figure' then 'خطأ في الجدول أو الشكل' when 'other' then 'مشكلة أخرى' end;
  if v_label is null then raise exception 'اختر نوع المشكلة'; end if;
  if v_detail is null and p_reason = 'other' then raise exception 'اكتب وصف المشكلة'; end if;
  if length(coalesce(v_detail, '')) > 500 then raise exception 'الوصف طويل (500 حرف كحد أقصى)'; end if;
  select * into q from questions where id = p_question;
  if not found then raise exception 'السؤال غير موجود'; end if;
  if not exists (select 1 from course_enrollments e where e.user_id = auth.uid() and e.course_id = public._course_of_question(p_question)) then
    raise exception 'السؤال خارج مقرراتك';
  end if;
  if exists (select 1 from review_notes where author = auth.uid() and source = 'student' and question_id = p_question and resolved_at is null) then
    raise exception 'سبق أن أبلغت عن هذا السؤال؛ شكرًا لك، وهو قيد المراجعة';
  end if;
  if (select count(*) from review_notes where author = auth.uid() and source = 'student' and created_at > now() - interval '1 day') >= 20 then
    raise exception 'بلغت الحد اليومي للبلاغات';
  end if;
  select * into o from objectives where id = q.objective_id;
  insert into review_notes (objective_id, question_id, entity, body, author, author_name, source)
  values (o.id, q.id, 'question', 'بلاغ طالب: ' || v_label || coalesce(' — ' || v_detail, ''), auth.uid(), 'طالب', 'student');
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.student_report_question(bigint, text, text) to authenticated;

-- =====================================================================
-- 2026-10-19: كوبونات النقاط
--   يصدر المعلم أو المالك كودًا بقيمة نقاط (حتى 500 للمالك، وحتى حد المعلم المضبوط، وللمعلم حصة أسبوعية).
--   الكود عام لطلاب مُصدِره فقط (طلاب المعلم المسندون)، ويُستخدم مرة واحدة، وله صلاحية. النقاط تزيد «المتاح للاستبدال» ولا تدخل الترتيب.
--   إدخال الكود: بعد 5 محاولات خاطئة يُقفل الإدخال 15 دقيقة. كل شيء يُسجَّل (المُصدِر والمستخدم والوقت).
-- =====================================================================
create or replace function public._coupon_code() returns text
language plpgsql volatile set search_path = public, pg_temp as $$
declare a constant text := 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'; b bytea := uuid_send(gen_random_uuid()); r text := ''; i int;
begin
  for i in 0..7 loop r := r || substr(a, (get_byte(b, i) % 31) + 1, 1); end loop;
  return substr(r, 1, 4) || '-' || substr(r, 5, 4);
end $$;

create or replace function public._coupon_json(c public.point_coupons) returns jsonb
language sql stable security definer set search_path = public, pg_temp as $$
  select jsonb_build_object('id', c.id, 'code', c.code, 'points', c.points, 'note', c.note, 'createdAt', c.created_at, 'expiresAt', c.expires_at,
    'status', case when c.status = 'active' and c.expires_at <= now() then 'expired' else c.status end,
    'redeemedAt', c.redeemed_at, 'redeemedBy', (select p.display_name from profiles p where p.user_id = c.redeemed_by), 'createdBy', c.created_by_name)
$$;

create or replace function public.staff_create_coupon(p_points int, p_note text, p_days int default 7) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare g public.grade_settings; v_role text := public.my_role(); v_week timestamptz; v_used int; c public.point_coupons; v_code text; i int := 0;
begin
  perform public._require_member();
  if v_role not in ('admin', 'viewer') then raise exception 'للمعلم ومالك المشروع' using errcode = '42501'; end if;
  select * into g from grade_settings where id = 1;
  if p_points is null or p_points < 1 or p_points > 500 then raise exception 'قيمة الكوبون بين 1 و500 نقطة'; end if;
  if length(trim(coalesce(p_note, ''))) < 3 then raise exception 'اكتب سبب المكافأة (يراه الطالب)'; end if;
  if length(p_note) > 120 then raise exception 'السبب طويل (120 حرفًا كحد أقصى)'; end if;
  if p_days is null or p_days < 1 or p_days > 30 then raise exception 'الصلاحية من 1 إلى 30 يومًا'; end if;
  if v_role = 'viewer' then
    if p_points > g.teacher_coupon_max then raise exception 'الحد الأقصى لكوبون المعلم % نقطة', g.teacher_coupon_max; end if;
    v_week := (date_trunc('week', (now() at time zone 'Asia/Riyadh') + interval '1 day') - interval '1 day') at time zone 'Asia/Riyadh';
    v_used := public._quota_used(auth.uid(), v_week);
    if v_used + p_points > g.teacher_weekly_quota then raise exception 'تجاوزت حصتك الأسبوعية (% من % نقطة)', v_used, g.teacher_weekly_quota; end if;
  end if;
  loop
    v_code := public._coupon_code(); i := i + 1;
    begin
      insert into point_coupons (code, points, note, created_by, created_by_name, expires_at)
      values (v_code, p_points, trim(p_note), auth.uid(), (select display_name from profiles where user_id = auth.uid()), now() + make_interval(days => p_days))
      returning * into c;
      exit;
    exception when unique_violation then if i > 5 then raise; end if;
    end;
  end loop;
  return public._coupon_json(c);
end $$;

create or replace function public.staff_list_coupons() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare g public.grade_settings; v_role text := public.my_role(); v_week timestamptz; v_used int;
begin
  perform public._require_member();
  if v_role not in ('admin', 'viewer') then raise exception 'للمعلم ومالك المشروع' using errcode = '42501'; end if;
  select * into g from grade_settings where id = 1;
  v_week := (date_trunc('week', (now() at time zone 'Asia/Riyadh') + interval '1 day') - interval '1 day') at time zone 'Asia/Riyadh';
  v_used := public._quota_used(auth.uid(), v_week);
  return jsonb_build_object('max', case when v_role = 'admin' then 500 else g.teacher_coupon_max end,
    'quota', case when v_role = 'admin' then null else g.teacher_weekly_quota end, 'used', v_used,
    'items', (select coalesce(jsonb_agg(public._coupon_json(c) order by c.created_at desc), '[]')
      from (select * from point_coupons where (v_role = 'admin' or created_by = auth.uid()) order by created_at desc limit 100) c));
end $$;

create or replace function public.staff_cancel_coupon(p_id bigint) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  if public.my_role() not in ('admin', 'viewer') then raise exception 'للمعلم ومالك المشروع' using errcode = '42501'; end if;
  update point_coupons set status = 'cancelled', cancelled_at = now()
    where id = p_id and status = 'active' and (created_by = auth.uid() or public.my_role() = 'admin');
  if not found then raise exception 'لا يمكن إلغاء هذا الكوبون'; end if;
end $$;

-- الطالب يدخل الكود: يرجع ok=false برسالة عامة عند الخطأ (لا يُكشف سبب الرفض)، ويسجَّل الفشل للقفل المؤقت
create or replace function public.student_redeem_coupon(p_code text, p_course bigint default null) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_course bigint; v_code text; c public.point_coupons; v_ok boolean := false; v_bal jsonb;
begin
  perform public._require_student();
  v_course := public._student_course(p_course);
  if v_course is null then raise exception 'لم يُسند لك مقرر جاهز بعد'; end if;
  perform pg_advisory_xact_lock(hashtextextended('coupon:' || auth.uid()::text, 0));
  if (select count(*) from coupon_attempts where user_id = auth.uid() and at > now() - interval '15 minutes') >= 5 then
    return jsonb_build_object('ok', false, 'locked', true, 'error', 'محاولات كثيرة خاطئة؛ حاول بعد 15 دقيقة');
  end if;
  v_code := upper(regexp_replace(coalesce(p_code, ''), '[^A-Za-z0-9]', '', 'g'));
  if length(v_code) = 8 then v_code := substr(v_code, 1, 4) || '-' || substr(v_code, 5, 4); end if;
  select * into c from point_coupons where code = v_code for update;
  if found and c.status = 'active' and c.expires_at > now() then
    -- كوبون المعلم لطلابه المسندين فقط؛ كوبون المالك لأي طالب
    v_ok := coalesce((select p.role = 'admin' from profiles p where p.user_id = c.created_by), false)
      or exists (select 1 from teacher_students ts where ts.teacher_id = c.created_by and ts.student_id = auth.uid());
  end if;
  if not v_ok then
    insert into coupon_attempts (user_id) values (auth.uid());
    return jsonb_build_object('ok', false, 'error', 'الكود غير صحيح أو منتهي أو مستخدم');
  end if;
  update point_coupons set status = 'redeemed', redeemed_by = auth.uid(), redeemed_course = v_course, redeemed_at = now() where id = c.id;
  v_bal := public.student_balance(v_course);
  return jsonb_build_object('ok', true, 'points', c.points, 'note', c.note, 'balance', v_bal);
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.staff_create_coupon(int, text, int), public.staff_list_coupons(), public.staff_cancel_coupon(bigint),
  public.student_redeem_coupon(text, bigint) to authenticated;
revoke execute on function public._coupon_code(), public._coupon_json(public.point_coupons) from authenticated;

-- =====================================================================
-- 2026-10-20: رسائل ومهام المعلم للطالب
--   المعلم (طلابه المسندون فقط) أو المالك يرسل «رسالة» أو «مهمة» (حل N سؤالًا في درس بصحة P% قبل موعد).
--   الطالب يقرأ فقط ويرد بزر جاهز («فهمت» / «أحتاج مساعدة»)؛ لا نص حر منه. إنجاز المهمة يُحسب من تدريبه
--   بنفس قواعد نقاط التميّز (أول إجابة لكل سؤال، وما أسرع من 3 ثوانٍ لا يُحتسب) ويُجمَّد عند الإكمال أو انتهاء الموعد.
--   الرسائل غير قابلة للتعديل (إلغاء فقط) وتبقى سجلًّا يراه المالك. الحدود قابلة للضبط من المالك.
-- =====================================================================
alter table public.grade_settings add column if not exists comm_daily_limit int not null default 20 check (comm_daily_limit between 1 and 500);
alter table public.grade_settings add column if not exists comm_active_tasks int not null default 3 check (comm_active_tasks between 1 and 20);
alter table public.grade_settings add column if not exists comm_max_recipients int not null default 300 check (comm_max_recipients between 1 and 1000);

create table if not exists public.comms (
  id bigint generated by default as identity primary key,
  kind text not null check (kind in ('message', 'task')),
  sender_id uuid not null,
  sender_name text,
  course_id bigint not null,
  title text not null,
  body text,
  audience jsonb not null default '{}',
  n_recipients int not null default 0,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '60 days'),
  status text not null default 'active' check (status in ('active', 'cancelled')),
  cancelled_by uuid, cancelled_at timestamptz,
  lesson_id bigint, n_questions int, min_accuracy int, due_at timestamptz
);
alter table public.comms add column if not exists reward_points int not null default 0 check (reward_points between 0 and 500);
create index if not exists comms_sender_idx on public.comms (sender_id, created_at desc);
create table if not exists public.comm_recipients (
  comm_id bigint not null references public.comms(id) on delete cascade,
  student_id uuid not null references auth.users(id) on delete cascade,
  read_at timestamptz,
  reply_code smallint check (reply_code in (1, 2)),
  valid_cnt int not null default 0, correct_cnt int not null default 0,
  status text not null default 'open' check (status in ('open', 'done', 'missed')),
  done_at timestamptz,
  primary key (comm_id, student_id)
);
alter table public.comm_recipients add column if not exists reward_pts int not null default 0;
create index if not exists comm_rec_student_idx on public.comm_recipients (student_id, comm_id desc);
create index if not exists comm_rec_unread_idx on public.comm_recipients (student_id) where read_at is null;
alter table public.comms enable row level security;
alter table public.comm_recipients enable row level security;
revoke all on public.comms, public.comm_recipients from anon, authenticated;

-- تقدم مهمة لطالب: أول إجابة لكل سؤال من الدرس داخل نافذة المهمة، وما أسرع من 3 ثوانٍ لا يُحتسب (كنقاط التميّز)
create or replace function public._task_progress(p_user uuid, p_lesson bigint, p_from timestamptz, p_to timestamptz)
returns table (valid int, correct int)
language sql stable security definer set search_path = public, pg_temp as $$
  with raw as (
    select a.question_id, a.correct, a.answered_at,
      extract(epoch from (a.answered_at - coalesce(lag(a.answered_at) over (partition by a.session_id order by a.answered_at), s.created_at))) secs
    from public.practice_sessions s join public.practice_answers a on a.session_id = s.id
    where s.user_id = p_user and s.created_at >= p_from - interval '1 day' and s.created_at <= p_to),
  win as (select r.* from raw r where r.answered_at >= p_from and r.answered_at <= p_to
          and r.question_id in (select q.id from public.questions q join public.objectives o on o.id = q.objective_id where o.lesson_id = p_lesson)),
  first as (select * from (select w.*, row_number() over (partition by w.question_id order by w.answered_at) rn from win w) x where rn = 1)
  select (count(*) filter (where secs >= 3))::int, (count(*) filter (where secs >= 3 and correct))::int from first
$$;

-- يحسب مهمة مفتوحة ويجمّد نتيجتها: إنجاز، أو انتهاء الموعد (لطالب واحد أو لكل المستلمين المفتوحين)
create or replace function public._comm_refresh(p_comm bigint, p_student uuid default null) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
declare c public.comms; r record; pr record;
begin
  select * into c from comms where id = p_comm and kind = 'task' and status = 'active';
  if not found then return; end if;
  for r in select student_id from comm_recipients where comm_id = p_comm and status = 'open' and (p_student is null or student_id = p_student) loop
    select * into pr from public._task_progress(r.student_id, c.lesson_id, c.created_at, c.due_at);
    if pr.valid >= c.n_questions and coalesce(100.0 * pr.correct / nullif(pr.valid, 0), 0) >= coalesce(c.min_accuracy, 0) then
      update comm_recipients set status = 'done', done_at = now(), valid_cnt = pr.valid, correct_cnt = pr.correct, reward_pts = coalesce(c.reward_points, 0) where comm_id = p_comm and student_id = r.student_id;
    elsif now() > c.due_at then
      update comm_recipients set status = 'missed', valid_cnt = pr.valid, correct_cnt = pr.correct where comm_id = p_comm and student_id = r.student_id;
    else
      update comm_recipients set valid_cnt = pr.valid, correct_cnt = pr.correct where comm_id = p_comm and student_id = r.student_id;
    end if;
  end loop;
end $$;

-- ما استهلكه المرسِل من حصته الأسبوعية (كوبونات + مكافآت مهامه المحتملة؛ ما فات موعده دون إنجاز يعود للحصة)
create or replace function public._quota_used(p_user uuid, p_since timestamptz) returns int
language sql stable security definer set search_path = public, pg_temp as $$
  select (coalesce((select sum(points) from point_coupons where created_by = p_user and status <> 'cancelled' and created_at >= p_since), 0)
    + coalesce((select sum(c.reward_points * (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status <> 'missed'))
                from comms c where c.sender_id = p_user and c.kind = 'task' and c.status = 'active' and c.reward_points > 0 and c.created_at >= p_since), 0))::int
$$;

-- ---------- الطالب ----------
create or replace function public.student_comm_summary() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_student();
  return jsonb_build_object(
    'unread', (select count(*) from comm_recipients cr join comms c on c.id = cr.comm_id where cr.student_id = auth.uid() and cr.read_at is null and c.status = 'active' and c.expires_at > now()),
    'task', (select jsonb_build_object('id', c.id, 'title', c.title, 'dueAt', c.due_at, 'n', c.n_questions, 'lessonId', c.lesson_id)
             from comm_recipients cr join comms c on c.id = cr.comm_id
             where cr.student_id = auth.uid() and cr.status = 'open' and c.kind = 'task' and c.status = 'active' and c.due_at > now()
             order by c.due_at limit 1));
end $$;

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
          'reward', c.reward_points, 'rewardGot', cr.reward_pts) end) j
      from comm_recipients cr join comms c on c.id = cr.comm_id
      where cr.student_id = auth.uid() and c.status = 'active' and c.expires_at > now()
      order by c.created_at desc limit 50) x));
end $$;

create or replace function public.student_comms_mark_read() returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_student();
  update comm_recipients set read_at = now() where student_id = auth.uid() and read_at is null;
end $$;

create or replace function public.student_comm_reply(p_id bigint, p_code int) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_student();
  if p_code not in (1, 2) then raise exception 'رد غير صالح'; end if;
  update comm_recipients cr set reply_code = p_code, read_at = coalesce(cr.read_at, now())
    where cr.comm_id = p_id and cr.student_id = auth.uid() and exists (select 1 from comms c where c.id = p_id and c.status = 'active');
  if not found then raise exception 'الرسالة غير موجودة'; end if;
end $$;

-- ---------- المعلم والمالك ----------
create or replace function public._require_comm_staff() returns void
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_member();
  if public.my_role() not in ('admin', 'viewer') then raise exception 'للمعلم ومالك المشروع' using errcode = '42501'; end if;
end $$;

create or replace function public.staff_course_lessons(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_comm_staff();
  perform public._require_course(v_course);
  return (select coalesce(jsonb_agg(jsonb_build_object('number', c.number, 'title', c.title, 'lessons',
      (select coalesce(jsonb_agg(jsonb_build_object('id', l.id, 'number', l.number, 'title', l.title) order by l.number), '[]') from lessons l where l.chapter_id = c.id)) order by c.number), '[]')
    from chapters c where c.course_id = v_course);
end $$;

create or replace function public.staff_my_students(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_comm_staff();
  -- الرسائل لا ترتبط بمقرر: كل طلاب المعلم المسندين (وللمالك كل الطلاب)؛ والمهمة وحدها تشترط تسجيل الطالب في مقرر الدرس
  return (select coalesce(jsonb_agg(jsonb_build_object('id', p.user_id, 'name', coalesce(nullif(trim(p.display_name), ''), split_part(u.email, '@', 1)), 'section', p.section, 'grade', p.grade,
      'enrolled', exists (select 1 from course_enrollments e where e.user_id = p.user_id and e.course_id = v_course)) order by p.section, p.display_name), '[]')
    from profiles p join auth.users u on u.id = p.user_id
    where p.role = 'student' and p.managed and public._visible_student(p.user_id));
end $$;

-- p = {kind, title, body, course, target:{mode:'all'|'section'|'students', section, students:[uuid]}, lesson, n, minAccuracy, due}
create or replace function public.staff_send_comm(p jsonb) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare g public.grade_settings; v_role text := public.my_role(); v_course bigint := coalesce(nullif(p->>'course', '')::bigint, public._default_course());
  v_kind text := p->>'kind'; v_title text := trim(coalesce(p->>'title', '')); v_body text := nullif(trim(coalesce(p->>'body', '')), '');
  v_mode text := coalesce(p#>>'{target,mode}', 'all'); v_section text := nullif(trim(coalesce(p#>>'{target,section}', '')), ''); v_grade text := nullif(trim(coalesce(p#>>'{target,grade}', '')), '');
  v_list uuid[] := '{}'; v_ids uuid[]; v_n int; v_lesson bigint; v_nq int; v_acc int; v_due timestamptz; v_max int; v_today timestamptz; v_aud jsonb; v_busy int; v_id bigint; v_reward int := 0; v_week timestamptz; v_used int; v_cap int;
  bad constant text := '[\x01-\x08\x0b\x0c\x0e-\x1f‪-‮⁦-⁩]';
begin
  perform public._require_comm_staff();
  if v_kind = 'task' then perform public._require_course(v_course); else v_course := coalesce(v_course, 0); end if;
  select * into g from grade_settings where id = 1;
  if v_kind not in ('message', 'task') then raise exception 'نوع غير صالح'; end if;
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
      and (v_kind = 'message' or exists (select 1 from course_enrollments e where e.user_id = pr.user_id and e.course_id = v_course))
      and (v_grade is null or pr.grade = v_grade) and (v_section is null or pr.section = v_section)
      and (v_mode in ('all', 'section') or (v_mode = 'students' and pr.user_id = any(v_list)));
  v_n := coalesce(cardinality(v_ids), 0);
  if v_n = 0 then raise exception '%', case when v_kind = 'task' then 'لا يوجد طلاب مطابقون مسجلون في مقرر هذا الدرس' else 'لا يوجد طلاب مطابقون؛ تأكد من إسناد الطلاب لك من «حسابات الفريق»' end; end if;
  if v_mode = 'students' and v_n <> cardinality(v_list) then raise exception '%', case when v_kind = 'task' then 'بعض الطلاب المحددين ليسوا من طلابك أو غير مسجلين في مقرر هذا الدرس' else 'بعض الطلاب المحددين ليسوا من طلابك' end; end if;
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
  insert into comms (kind, sender_id, sender_name, course_id, title, body, audience, n_recipients, lesson_id, n_questions, min_accuracy, due_at, reward_points)
  values (v_kind, auth.uid(), (select display_name from profiles where user_id = auth.uid()), v_course, v_title, v_body,
    case when v_mode = 'students' then v_aud || jsonb_build_object('students', to_jsonb(v_list)) else v_aud end, v_n, v_lesson, v_nq, v_acc, v_due, v_reward)
  returning id into v_id;
  insert into comm_recipients (comm_id, student_id) select v_id, u from unnest(v_ids) u;
  return jsonb_build_object('id', v_id, 'n', v_n);
end $$;

create or replace function public.staff_list_comms(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_role text := public.my_role();
begin
  perform public._require_comm_staff();
  return (select coalesce(jsonb_agg(jsonb_build_object('id', c.id, 'kind', c.kind, 'title', c.title, 'body', c.body, 'sender', c.sender_name, 'mine', c.sender_id = auth.uid(),
      'createdAt', c.created_at, 'status', c.status, 'n', c.n_recipients, 'audience', c.audience,
      'read', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.read_at is not null),
      'help', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.reply_code = 2),
      'ack', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.reply_code = 1),
      'task', case when c.kind = 'task' then jsonb_build_object('lesson', (select l.title from lessons l where l.id = c.lesson_id), 'n', c.n_questions, 'minAccuracy', c.min_accuracy, 'dueAt', c.due_at, 'reward', c.reward_points,
         'done', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status = 'done'),
         'open', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status = 'open'),
         'missed', (select count(*) from comm_recipients cr where cr.comm_id = c.id and cr.status = 'missed')) end)
    order by c.created_at desc), '[]')
    from (select * from comms where (v_role = 'admin' or sender_id = auth.uid()) order by created_at desc limit 50) c);
end $$;

create or replace function public.staff_comm_detail(p_id bigint) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare c public.comms;
begin
  perform public._require_comm_staff();
  select * into c from comms where id = p_id and (sender_id = auth.uid() or public.my_role() = 'admin');
  if not found then raise exception 'الرسالة غير موجودة'; end if;
  perform public._comm_refresh(p_id);
  return (select coalesce(jsonb_agg(jsonb_build_object('name', p.display_name, 'username', split_part(u.email, '@', 1), 'section', p.section,
      'read', cr.read_at is not null, 'reply', cr.reply_code, 'status', cr.status, 'valid', cr.valid_cnt, 'correct', cr.correct_cnt) order by p.section, p.display_name), '[]')
    from comm_recipients cr join profiles p on p.user_id = cr.student_id join auth.users u on u.id = cr.student_id where cr.comm_id = p_id);
end $$;

create or replace function public.staff_cancel_comm(p_id bigint) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_comm_staff();
  update comms set status = 'cancelled', cancelled_by = auth.uid(), cancelled_at = now()
    where id = p_id and status = 'active' and (sender_id = auth.uid() or public.my_role() = 'admin');
  if not found then raise exception 'لا يمكن إلغاء هذه الرسالة'; end if;
end $$;

create or replace function public.admin_get_comm_settings() returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  return (select jsonb_build_object('daily', comm_daily_limit, 'activeTasks', comm_active_tasks, 'maxRecipients', comm_max_recipients) from grade_settings where id = 1);
end $$;
create or replace function public.admin_set_comm_settings(p_daily int, p_active int, p_max int) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._require_admin();
  if p_daily is null or p_daily < 1 or p_daily > 500 then raise exception 'الحد اليومي بين 1 و500'; end if;
  if p_active is null or p_active < 1 or p_active > 20 then raise exception 'عدد المهام النشطة بين 1 و20'; end if;
  if p_max is null or p_max < 1 or p_max > 1000 then raise exception 'عدد المستلمين بين 1 و1000'; end if;
  update grade_settings set comm_daily_limit = p_daily, comm_active_tasks = p_active, comm_max_recipients = p_max, updated_at = now(), updated_by = auth.uid() where id = 1;
  return public.admin_get_comm_settings();
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.student_comm_summary(), public.student_inbox(), public.student_comms_mark_read(), public.student_comm_reply(bigint, int),
  public.staff_course_lessons(bigint), public.staff_my_students(bigint), public.staff_send_comm(jsonb), public.staff_list_comms(bigint),
  public.staff_comm_detail(bigint), public.staff_cancel_comm(bigint), public.admin_get_comm_settings(), public.admin_set_comm_settings(int, int, int) to authenticated;
revoke execute on function public._task_progress(uuid, bigint, timestamptz, timestamptz), public._comm_refresh(bigint, uuid), public._require_comm_staff(), public._quota_used(uuid, timestamptz) from authenticated;

-- =====================================================================
-- 2026-10-28: مخزن صور الأسئلة (Supabase Storage)
--   القراءة عامة (الصور تُعرض داخل المنصة المغلقة بأسماء عشوائية لا تُخمَّن)، والرفع والحذف لمالك المشروع فقط.
--   صيغ مسموحة: PNG وJPEG وWebP وGIF (لا SVG في الرفع؛ SVG للصور الثابتة في qimg/ فقط) بحد 1 ميغابايت.
--   يُتخطى هذا الجزء في قاعدة لا يوجد فيها مخطط storage (مثل بيئة الاختبار المحلية).
-- =====================================================================
do $$
begin
  if not exists (select 1 from information_schema.schemata where schema_name = 'storage') then return; end if;
  insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  values ('question-media', 'question-media', true, 1048576, array['image/png', 'image/jpeg', 'image/webp', 'image/gif'])
  on conflict (id) do update set public = true, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;
  drop policy if exists "question-media admin insert" on storage.objects;
  drop policy if exists "question-media admin update" on storage.objects;
  drop policy if exists "question-media admin delete" on storage.objects;
  create policy "question-media admin insert" on storage.objects for insert to authenticated
    with check (bucket_id = 'question-media' and public.is_admin());
  create policy "question-media admin update" on storage.objects for update to authenticated
    using (bucket_id = 'question-media' and public.is_admin()) with check (bucket_id = 'question-media' and public.is_admin());
  create policy "question-media admin delete" on storage.objects for delete to authenticated
    using (bucket_id = 'question-media' and public.is_admin());
end $$;

-- =====================================================================
-- 2026-10-29: قسم «الاستعداد للتحصيلي» (البنية)
--   مقرر من نوع tahsili: فصوله المواد الأربع بالنسب الرسمية (25% لكل مادة)، ودروسه الوحدات، وأهدافه الموضوعات.
--   يبقى «قيد الإعداد» حتى يكتمل محتواه؛ ويُسند للطلاب من «الحسابات» كأي مقرر. نقاطه منفصلة عن المقرر الدراسي.
--   المعرفات: الفصول 501–504، والوحدات 50000 + 100×المادة + الوحدة، والموضوعات 5000000 + 10000×المادة + 100×الوحدة + الموضوع
--   (لا تتقاطع مع المقررات الأخرى، وتتسع لـ 99 وحدة لكل مادة). المحتوى من data/tahsili عبر scripts/build-tahsili-seed.js.
-- =====================================================================
insert into public.courses (id, code, title, subject, grade, term, country, status, sort_order, kind) values
  (5, 'التحصيلي', 'الاستعداد للتحصيلي', 'الأحياء والكيمياء والفيزياء والرياضيات', 'الثالث الثانوي', 'الأول', 'السعودية', 'preparing', 90, 'tahsili')
on conflict (id) do update set kind = 'tahsili';
insert into public.chapters (id, course_id, number, title, description) values
  (501, 5, 1, 'الأحياء والبيئة', '25% من أسئلة الاختبار'),
  (502, 5, 2, 'الكيمياء', '25% من أسئلة الاختبار'),
  (503, 5, 3, 'الفيزياء', '25% من أسئلة الاختبار'),
  (504, 5, 4, 'الرياضيات', '25% من أسئلة الاختبار')
on conflict (id) do nothing;

-- =====================================================================
-- 2026-10-30: قسم «قياس الأثر»
--   دراسة أثر = اختبار قبلي (ورقي أو غيره) ← فترة استخدام المنصة ← اختبار بعدي، تُدخل درجاتهما بملف Excel.
--   المنصة تربط كل طالب باستخدامه الفعلي بين تاريخي الاختبارين (من سجل التدريب)، ويُحسب التحليل في الواجهة (public/impact-stats.js).
--   الإنشاء والإدخال: مالك المشروع والمعلم (لطلابه المسندين). القراءة: المراجع والمشرف والمدير أيضًا، دون أسماء.
-- =====================================================================
create table if not exists public.impact_studies (
  id bigint generated by default as identity primary key,
  course_id bigint not null references public.courses(id) on delete cascade,
  title text not null,
  note text,
  pre_date date not null,
  post_date date,
  pre_max numeric not null default 100 check (pre_max > 0),
  post_max numeric not null default 100 check (post_max > 0),
  same_test boolean not null default true,
  -- أسئلة الاختبار (اختياري): [{max, objective}] بالترتيب نفسه في القبلي والبعدي، لتحليل الأهداف وجودة الاختبار
  items jsonb not null default '[]',
  created_by uuid references public.profiles(user_id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.impact_scores (
  study_id bigint not null references public.impact_studies(id) on delete cascade,
  user_id uuid not null references public.profiles(user_id) on delete cascade,
  pre numeric, post numeric, prior numeric,
  pre_items numeric[], post_items numeric[],
  updated_at timestamptz not null default now(),
  primary key (study_id, user_id)
);
alter table public.impact_studies enable row level security;
alter table public.impact_scores enable row level security;
revoke all on public.impact_studies, public.impact_scores from anon, authenticated;

create or replace function public._impact_study(p_id bigint, p_manage boolean) returns public.impact_studies
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare s public.impact_studies; r text := public.my_role();
begin
  perform public._require_member();
  select * into s from impact_studies where id = p_id;
  if not found then raise exception 'الدراسة غير موجودة' using errcode = 'P0002'; end if;
  perform public._require_course(s.course_id);
  if p_manage and r not in ('admin', 'viewer') then raise exception 'إدخال بيانات قياس الأثر لمالك المشروع والمعلم' using errcode = '42501'; end if;
  if not p_manage and r not in ('admin', 'viewer', 'reviewer', 'supervisor', 'principal') then raise exception 'لا تملك صلاحية عرض قياس الأثر' using errcode = '42501'; end if;
  return s;
end $$;

create or replace function public.impact_list(p_course bigint default null) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare v_course bigint := coalesce(p_course, public._default_course());
begin
  perform public._require_member();
  perform public._require_course(v_course);
  if public.my_role() not in ('admin', 'viewer', 'reviewer', 'supervisor', 'principal') then raise exception 'لا تملك صلاحية عرض قياس الأثر' using errcode = '42501'; end if;
  return (select coalesce(jsonb_agg(jsonb_build_object('id', s.id, 'title', s.title, 'preDate', s.pre_date, 'postDate', s.post_date,
      'items', jsonb_array_length(s.items), 'updatedAt', s.updated_at,
      'mine', s.created_by = auth.uid(),
      'nPre', (select count(*) from impact_scores x where x.study_id = s.id and x.pre is not null and public._visible_student(x.user_id)),
      'nPost', (select count(*) from impact_scores x where x.study_id = s.id and x.post is not null and public._visible_student(x.user_id)),
      'nPaired', (select count(*) from impact_scores x where x.study_id = s.id and x.pre is not null and x.post is not null and public._visible_student(x.user_id)))
    order by s.pre_date desc, s.id desc), '[]')
    from impact_studies s where s.course_id = v_course);
end $$;

-- إنشاء دراسة أو تعديلها (p_id = null للإنشاء). المعلم يعدّل دراساته فقط.
create or replace function public.impact_save(p_id bigint, p jsonb, p_course bigint default null) returns bigint
language plpgsql security definer set search_path = public, pg_temp as $$
declare v_course bigint; v_id bigint; v_items jsonb := coalesce(p->'items', '[]'::jsonb); it jsonb; v_bad text[];
begin
  perform public._require_member();
  if public.my_role() not in ('admin', 'viewer') then raise exception 'إنشاء دراسات الأثر لمالك المشروع والمعلم' using errcode = '42501'; end if;
  if p_id is not null then
    select course_id into v_course from impact_studies where id = p_id;
    if v_course is null then raise exception 'الدراسة غير موجودة' using errcode = 'P0002'; end if;
    if public.my_role() = 'viewer' and not exists (select 1 from impact_studies where id = p_id and created_by = auth.uid()) then
      raise exception 'يعدّل الدراسة من أنشأها أو مالك المشروع' using errcode = '42501'; end if;
  else v_course := coalesce(p_course, public._default_course()); end if;
  perform public._require_course(v_course);
  if coalesce(trim(p->>'title'), '') = '' then raise exception 'اكتب عنوان الدراسة' using errcode = '22023'; end if;
  if nullif(p->>'preDate', '') is null then raise exception 'تاريخ الاختبار القبلي مطلوب' using errcode = '22023'; end if;
  if nullif(p->>'postDate', '') is not null and (p->>'postDate')::date <= (p->>'preDate')::date then
    raise exception 'تاريخ البعدي بعد تاريخ القبلي' using errcode = '22023'; end if;
  if coalesce((p->>'preMax')::numeric, 0) <= 0 or coalesce((p->>'postMax')::numeric, 0) <= 0 then
    raise exception 'الدرجة العظمى لكل اختبار أكبر من صفر' using errcode = '22023'; end if;
  if jsonb_typeof(v_items) <> 'array' or jsonb_array_length(v_items) > 100 then raise exception 'أسئلة الاختبار 100 على الأكثر' using errcode = '22023'; end if;
  for it in select * from jsonb_array_elements(v_items) loop
    if coalesce((it->>'max')::numeric, 0) <= 0 then raise exception 'درجة كل سؤال أكبر من صفر' using errcode = '22023'; end if;
    if nullif(trim(it->>'objective'), '') is not null and not exists (
        select 1 from objectives o join lessons l on l.id = o.lesson_id join chapters c on c.id = l.chapter_id
        where c.course_id = v_course and o.code = trim(it->>'objective')) then
      v_bad := v_bad || trim(it->>'objective'); end if;
  end loop;
  if v_bad is not null then raise exception 'رموز أهداف غير موجودة في المقرر: %', array_to_string(v_bad, '، ') using errcode = '22023'; end if;
  v_items := (select coalesce(jsonb_agg(jsonb_build_object('max', (e->>'max')::numeric, 'objective', nullif(trim(e->>'objective'), ''))), '[]')
              from jsonb_array_elements(v_items) e);
  if p_id is null then
    insert into impact_studies (course_id, title, note, pre_date, post_date, pre_max, post_max, same_test, items, created_by)
    values (v_course, trim(p->>'title'), nullif(trim(p->>'note'), ''), (p->>'preDate')::date, nullif(p->>'postDate', '')::date,
      (p->>'preMax')::numeric, (p->>'postMax')::numeric, coalesce((p->>'sameTest')::boolean, true), v_items, auth.uid())
    returning id into v_id;
  else
    -- تغيير عدد الأسئلة يُبطل درجات الأسئلة المدخلة سابقًا (تبقى المجاميع)
    update impact_scores set pre_items = null, post_items = null
      where study_id = p_id and jsonb_array_length(v_items) <> (select jsonb_array_length(items) from impact_studies where id = p_id);
    update impact_studies set title = trim(p->>'title'), note = nullif(trim(p->>'note'), ''), pre_date = (p->>'preDate')::date,
      post_date = nullif(p->>'postDate', '')::date, pre_max = (p->>'preMax')::numeric, post_max = (p->>'postMax')::numeric,
      same_test = coalesce((p->>'sameTest')::boolean, true), items = v_items, updated_at = now() where id = p_id;
    v_id := p_id;
  end if;
  return v_id;
end $$;

create or replace function public.impact_delete(p_id bigint) returns void
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform public._impact_study(p_id, true);
  if public.my_role() = 'viewer' and not exists (select 1 from impact_studies where id = p_id and created_by = auth.uid()) then
    raise exception 'يحذف الدراسة من أنشأها أو مالك المشروع' using errcode = '42501'; end if;
  delete from impact_studies where id = p_id;
end $$;

-- إدخال درجات مرحلة (pre أو post أو prior) من ملف: [{username, total, items: [..]}]. الصف الذي درجته فارغة يمسح درجة تلك المرحلة.
-- يُقبل طلاب المقرر الذين يراهم الحساب فقط، ويُعاد من لم يُعرف.
create or replace function public.impact_import(p_id bigint, p_phase text, p_rows jsonb) returns jsonb
language plpgsql security definer set search_path = public, pg_temp as $$
declare s public.impact_studies; r jsonb; v_user uuid; v_items numeric[]; v_total numeric; v_max numeric; n int := 0; v_unknown text[] := '{}'; v_errors text[] := '{}';
  v_k int; i int; v_name text;
begin
  s := public._impact_study(p_id, true);
  if p_phase not in ('pre', 'post', 'prior') then raise exception 'المرحلة غير صالحة' using errcode = '22023'; end if;
  if jsonb_typeof(p_rows) <> 'array' or jsonb_array_length(p_rows) > 2000 then raise exception 'الملف 2000 صف على الأكثر' using errcode = '22023'; end if;
  v_max := case p_phase when 'pre' then s.pre_max when 'post' then s.post_max else 100 end;
  v_k := jsonb_array_length(s.items);
  for r in select * from jsonb_array_elements(p_rows) loop
    v_name := lower(trim(coalesce(r->>'username', '')));
    if v_name = '' then continue; end if;
    select u.id into v_user from auth.users u join profiles p on p.user_id = u.id
      join course_enrollments e on e.user_id = u.id and e.course_id = s.course_id
      where split_part(u.email, '@', 1) = v_name and p.role = 'student' and public._visible_student(u.id);
    if v_user is null then v_unknown := v_unknown || v_name; continue; end if;
    v_items := null; v_total := nullif(r->>'total', '')::numeric;
    if p_phase <> 'prior' and v_k > 0 and jsonb_typeof(r->'items') = 'array' and jsonb_array_length(r->'items') > 0 then
      if jsonb_array_length(r->'items') <> v_k then v_errors := v_errors || (v_name || ': عدد الأسئلة ' || jsonb_array_length(r->'items') || ' والمطلوب ' || v_k); continue; end if;
      select array_agg(nullif(x, '')::numeric order by o) into v_items from jsonb_array_elements_text(r->'items') with ordinality t(x, o);
      for i in 1..v_k loop
        if v_items[i] is not null and (v_items[i] < 0 or v_items[i] > (s.items->(i - 1)->>'max')::numeric) then
          v_errors := v_errors || (v_name || ': درجة السؤال ' || i || ' خارج المدى'); v_items := null; exit; end if;
      end loop;
      if v_items is null then continue; end if;
      -- كل الأسئلة فارغة = غائب
      if (select bool_and(x is null) from unnest(v_items) x) then v_items := null; v_total := null;
      elsif v_total is null then v_total := (select sum(coalesce(x, 0)) from unnest(v_items) x);
      elsif abs(v_total - (select sum(coalesce(x, 0)) from unnest(v_items) x)) > 0.001 then
        v_errors := v_errors || (v_name || ': المجموع لا يساوي مجموع درجات الأسئلة'); continue; end if;
    end if;
    if v_total is not null and (v_total < 0 or v_total > v_max) then v_errors := v_errors || (v_name || ': الدرجة خارج المدى 0–' || v_max); continue; end if;
    insert into impact_scores (study_id, user_id) values (p_id, v_user) on conflict do nothing;
    update impact_scores set
      pre = case when p_phase = 'pre' then v_total else pre end, pre_items = case when p_phase = 'pre' then v_items else pre_items end,
      post = case when p_phase = 'post' then v_total else post end, post_items = case when p_phase = 'post' then v_items else post_items end,
      prior = case when p_phase = 'prior' then v_total else prior end, updated_at = now()
      where study_id = p_id and user_id = v_user;
    n := n + 1;
  end loop;
  delete from impact_scores where study_id = p_id and pre is null and post is null and prior is null;
  update impact_studies set updated_at = now() where id = p_id;
  return jsonb_build_object('saved', n, 'unknown', to_jsonb(v_unknown), 'errors', to_jsonb(v_errors));
end $$;

-- بيانات الدراسة كاملة للتحليل: كل طلاب المقرر الذين يراهم الحساب (من له درجات ومن ليس له)، مع استخدامهم للمنصة
-- بين تاريخي الاختبارين وقبله. الأسماء لمالك المشروع والمعلم والمراجع فقط؛ المشرف والمدير يستلمان أرقامًا دون هوية.
create or replace function public.impact_get(p_id bigint) returns jsonb
language plpgsql stable security definer set search_path = public, pg_temp as $$
declare s public.impact_studies; v_named boolean; v_from timestamptz; v_to timestamptz;
begin
  s := public._impact_study(p_id, false);
  v_named := public.my_role() in ('admin', 'viewer', 'reviewer');
  v_from := (s.pre_date::timestamp at time zone 'Asia/Riyadh');
  v_to := coalesce((s.post_date::timestamp at time zone 'Asia/Riyadh'), now());
  return (with stu as (
      select p.user_id, p.display_name, p.section, split_part(u.email, '@', 1) username
      from course_enrollments e join profiles p on p.user_id = e.user_id and p.role = 'student' join auth.users u on u.id = p.user_id
      where e.course_id = s.course_id and public._visible_student(p.user_id)
      union
      select p.user_id, p.display_name, p.section, split_part(u.email, '@', 1)
      from impact_scores x join profiles p on p.user_id = x.user_id join auth.users u on u.id = p.user_id
      where x.study_id = p_id and public._visible_student(p.user_id)),
    cq as (select q.id, o.code from questions q join objectives o on o.id = q.objective_id join lessons l on l.id = o.lesson_id
           join chapters c on c.id = l.chapter_id where c.course_id = s.course_id),
    raw as (select ps.user_id, a.question_id, cq.code, a.correct, a.answered_at,
              extract(epoch from (a.answered_at - coalesce(lag(a.answered_at) over (partition by a.session_id order by a.answered_at), ps.created_at))) secs
            from practice_answers a join practice_sessions ps on ps.id = a.session_id join cq on cq.id = a.question_id
            where ps.user_id in (select user_id from stu)),
    first as (select * from (select r.*, row_number() over (partition by r.user_id, r.question_id order by r.answered_at) rn from raw r) z where rn = 1),
    win as (select f.*, f.answered_at >= v_from and f.answered_at < v_to inw, f.answered_at < v_from bef from first f),
    us as (select w.user_id,
             count(*) filter (where w.inw)::int attempts,
             count(*) filter (where w.inw and w.secs >= 3)::int valid,
             count(*) filter (where w.inw and w.secs >= 3 and w.correct)::int correct,
             count(*) filter (where w.inw and w.secs < 3)::int rushed,
             count(distinct (w.answered_at at time zone 'Asia/Riyadh')::date) filter (where w.inw and w.secs >= 3)::int days,
             count(*) filter (where w.bef and w.secs >= 3)::int before
           from win w group by 1),
    ob as (select w.user_id, jsonb_object_agg(w.code, w.n) m from (select user_id, code, count(*) n from win where inw and secs >= 3
                 and code in (select e->>'objective' from jsonb_array_elements(s.items) e) group by 1, 2) w group by 1)
    select jsonb_build_object(
      'study', jsonb_build_object('id', s.id, 'courseId', s.course_id, 'title', s.title, 'note', s.note, 'preDate', s.pre_date, 'postDate', s.post_date,
        'preMax', s.pre_max, 'postMax', s.post_max, 'sameTest', s.same_test, 'items', s.items,
        'mine', s.created_by = auth.uid(), 'canEdit', public.my_role() = 'admin' or (public.my_role() = 'viewer' and s.created_by = auth.uid()),
        'canImport', public.my_role() in ('admin', 'viewer'), 'named', v_named, 'usageTo', v_to),
      'objectives', (select coalesce(jsonb_object_agg(o.code, coalesce(o.approved_text, o.original_text)), '{}') from objectives o
                     where o.code in (select e->>'objective' from jsonb_array_elements(s.items) e)),
      'rows', (select coalesce(jsonb_agg(jsonb_build_object(
          'key', md5(s.id::text || st.user_id::text),
          'name', case when v_named then st.display_name end, 'username', case when v_named then st.username end,
          'section', st.section, 'pre', x.pre, 'post', x.post, 'prior', x.prior, 'preItems', to_jsonb(x.pre_items), 'postItems', to_jsonb(x.post_items),
          'usage', jsonb_build_object('attempts', coalesce(us.attempts, 0), 'valid', coalesce(us.valid, 0), 'correct', coalesce(us.correct, 0),
            'rushed', coalesce(us.rushed, 0), 'days', coalesce(us.days, 0), 'before', coalesce(us.before, 0)),
          'objUsage', coalesce(ob.m, '{}'))
        order by st.section nulls last, st.display_name), '[]')
        from stu st left join impact_scores x on x.study_id = p_id and x.user_id = st.user_id
          left join us on us.user_id = st.user_id left join ob on ob.user_id = st.user_id)));
end $$;

revoke execute on all functions in schema public from anon, public;
grant execute on function public.get_me() to anon, authenticated;
grant execute on function public.impact_list(bigint), public.impact_save(bigint, jsonb, bigint), public.impact_delete(bigint),
  public.impact_import(bigint, text, jsonb), public.impact_get(bigint) to authenticated;
revoke execute on function public._impact_study(bigint, boolean) from authenticated;
