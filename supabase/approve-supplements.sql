-- اعتماد جميع نصوص المحتوى المكمّل بقرار مالك المشروع (2026-10-11). آمن للتكرار: يطبق على النصوص التي ما زالت بانتظار المراجعة فقط.
begin;
with upd as (
  update public.supplements set review_status = 'approved' where review_status = 'pending' returning objective_id
)
insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_name, at)
select 'supplement', objective_id, 'approve', '{"reviewStatus":"pending"}'::jsonb, '{"reviewStatus":"approved"}'::jsonb,
  'مالك المشروع: اعتماد نهائي لجميع نصوص المحتوى المكمّل (111 نصًا) بقرار مالك المشروع دون مراجعة تفصيلية لكل نص. النصوص معتمدة كما كتبها الوكيل الكيميائي التربوي.', 'مالك المشروع', now()
from upd;
commit;
-- التحقق: يجب أن تكون النتيجة 111 معتمدًا
select review_status, count(*) from public.supplements group by 1;
