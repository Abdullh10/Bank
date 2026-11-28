-- اعتماد مالك المشروع لأسئلة فيزياء 3-2 — الفصول 1–3 (2026-11-28): 870 سؤالًا (290، 240، 340)
-- يعتمد فقط المولّد غير المستبعد الذي اجتاز التحقق الآلي، ويسجّل كل اعتماد في سجل التعديلات. آمن للتكرار.
-- المقرر 104 ما زال «قيد الإعداد»؛ الاعتماد لا يتيحه للمعلمين والطلاب.
with done as (
  update public.questions q set status = 'approved', reviewed_at = now(),
         reviewed_by = (select user_id from public.profiles where role = 'admin' order by user_id limit 1)
  from public.question_answers a, public.objectives o, public.lessons l, public.chapters ch
  where a.question_id = q.id and o.id = q.objective_id and l.id = o.lesson_id and ch.id = l.chapter_id
    and ch.course_id = 104 and ch.number in (1, 2, 3) and q.status = 'generated' and not q.excluded
    and coalesce((a.auto_check->>'passed')::boolean, false)
  returning q.id)
insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_id, user_name)
select 'question', d.id, 'status', '{"status": "generated"}'::jsonb, '{"status": "approved"}'::jsonb,
       'اعتماد مالك المشروع لأسئلة فيزياء 3-2 (الفصول 1–3) بعد التحقق المستقل (2026-11-28)',
       p.user_id, p.display_name
from done d left join lateral (select user_id, display_name from public.profiles where role = 'admin' order by user_id limit 1) p on true;

-- التحقق: يجب أن يكون الناتج approved في الفصول 1–3: 290، 240، 340، ولا generated
select ch.number as chapter, q.status, count(*) from public.questions q join public.objectives o on o.id = q.objective_id
  join public.lessons l on l.id = o.lesson_id join public.chapters ch on ch.id = l.chapter_id
where ch.course_id = 104 group by 1, 2 order by 1, 2;
