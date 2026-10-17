-- اعتماد أسئلة كيمياء 3 بقرار مالك المشروع (2026-10-17) بعد: الفحص البنيوي، والحل الأعمى لأسئلة الاختيار، والمراجعة على الكتاب للأسئلة المعلَّمة، والمراجعة العشوائية (390 سؤالًا).
-- يعتمد الأسئلة الجاهزة (حالتها «مولدة» واجتازت التحقق الآلي) ويسجّل القرار في سجل التعديلات لكل سؤال. آمن للتكرار.
begin;
with upd as (
  update public.questions q
     set status = 'approved', reviewed_at = now(),
         reviewed_by = (select user_id from public.profiles where role = 'admin' order by user_id limit 1)
    from public.objectives o
   where o.id = q.objective_id and o.code like 'K3-%' and q.status = 'generated' and not q.excluded
     and coalesce((select (a.auto_check->>'passed')::boolean from public.question_answers a where a.question_id = q.id), false)
  returning q.id
)
insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_name, at)
select 'question', id, 'status', '{"status":"generated"}'::jsonb, '{"status":"approved"}'::jsonb,
       'مالك المشروع: اعتماد أسئلة كيمياء 3 بعد الفحص الآلي والحل الأعمى والمراجعة العشوائية (2026-10-17)', 'مالك المشروع', now()
  from upd;
commit;

-- تحقق: يجب أن يكون المعتمد 1670
select count(*) filter (where q.status = 'approved') as approved, count(*) as total
  from public.questions q join public.objectives o on o.id = q.objective_id where o.code like 'K3-%';
