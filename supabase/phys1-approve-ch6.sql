-- اعتماد مالك المشروع لأسئلة فيزياء 1 — الفصل 6 (2026-11-21): 360 سؤالًا
-- يعتمد فقط المولّد غير المستبعد الذي اجتاز التحقق الآلي، ويسجّل كل اعتماد في سجل التعديلات. آمن للتكرار.
-- المقرر متاح: تظهر الأسئلة المعتمدة للمعلم المسند إليه، وللطلاب المسجلين فيه فقط.
with done as (
  update public.questions q set status = 'approved', reviewed_at = now(),
         reviewed_by = (select user_id from public.profiles where role = 'admin' order by user_id limit 1)
  from public.question_answers a, public.objectives o, public.lessons l, public.chapters ch
  where a.question_id = q.id and o.id = q.objective_id and l.id = o.lesson_id and ch.id = l.chapter_id
    and ch.course_id = 101 and ch.number in (6) and q.status = 'generated' and not q.excluded
    and coalesce((a.auto_check->>'passed')::boolean, false)
  returning q.id)
insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_id, user_name)
select 'question', d.id, 'status', '{"status": "generated"}'::jsonb, '{"status": "approved"}'::jsonb,
       'اعتماد مالك المشروع لأسئلة فيزياء 1 (الفصل 6) بعد التحقق المستقل (2026-11-21)',
       p.user_id, p.display_name
from done d left join lateral (select user_id, display_name from public.profiles where role = 'admin' order by user_id limit 1) p on true;

-- التحقق: يجب أن يكون الناتج approved في الفصول 1–6: 460، 530، 330، 650، 300، 360، ولا generated
select ch.number as chapter, q.status, count(*) from public.questions q join public.objectives o on o.id = q.objective_id
  join public.lessons l on l.id = o.lesson_id join public.chapters ch on ch.id = l.chapter_id
where ch.course_id = 101 group by 1, 2 order by 1, 2;
