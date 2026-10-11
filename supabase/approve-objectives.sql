-- اعتماد جميع الأهداف بقرار مالك المشروع (2026-10-11). آمن للتكرار: يطبق على الأهداف التي ما زالت بانتظار المراجعة فقط.
-- الصياغة المعتمدة = الصياغة المقترحة، وللأهداف المقترح فصلها تُضم الصياغتان بفاصلة منقوطة.
begin;
with pending as (
  select id, coalesce(proposed_text, original_text) ||
    coalesce((select string_agg('؛ ' || x, '' order by ord) from jsonb_array_elements_text(split_into) with ordinality as t(x, ord)), '') as txt
  from public.objectives where review_status = 'pending'
), upd as (
  update public.objectives o set review_status = 'approved', approved_text = p.txt, reviewed_at = '2026-10-11'::timestamptz
  from pending p where o.id = p.id returning o.id, o.approved_text
)
insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_name, at)
select 'objective', id, 'approve', '{"reviewStatus":"pending","approvedText":null}'::jsonb,
  jsonb_build_object('reviewStatus', 'approved', 'approvedText', approved_text), 'مالك المشروع: اعتماد نهائي لجميع الأهداف بقرار مالك المشروع دون مراجعة تفصيلية لكل هدف. الصياغة المعتمدة هي الصياغة المقترحة، وللأهداف المقترح فصلها تُضم الصياغتان في نص واحد بفاصلة منقوطة.', 'مالك المشروع', now()
from upd;
commit;
-- التحقق: يجب أن تكون النتيجة 258 معتمدًا و0 بانتظار المراجعة
select review_status, count(*) from public.objectives group by 1;
