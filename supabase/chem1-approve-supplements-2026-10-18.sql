-- اعتماد نصوص المحتوى المكمّل لكيمياء 1 (5 نصوص) بقرار مالك المشروع (2026-10-18). آمن للتكرار: يطبق على النصوص التي ما زالت بانتظار المراجعة فقط.
begin;
with upd as (
  update public.supplements s set review_status = 'approved'
    from public.objectives o
   where o.id = s.objective_id and o.code like 'K1-%' and s.review_status = 'pending'
  returning s.objective_id
)
insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_name, at)
select 'supplement', objective_id, 'approve', '{"reviewStatus":"pending"}'::jsonb, '{"reviewStatus":"approved"}'::jsonb,
  'مالك المشروع: اعتماد نصوص المحتوى المكمّل لكيمياء 1 (2026-10-18)', 'مالك المشروع', now()
from upd;
commit;

-- تحقق: يجب أن تكون النتيجة 5 معتمدة
select s.review_status, count(*) from public.supplements s join public.objectives o on o.id = s.objective_id
 where o.code like 'K1-%' group by 1;
