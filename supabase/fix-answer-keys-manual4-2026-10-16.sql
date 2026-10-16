-- إعادة 4 أسئلة إلى نسختها المصححة (2026-10-16): عُدّلت يدويًا فصار مفتاحها أو بدائلها غير صحيح
--   C3-L3-O01 س1، C3-L3-O03 س2 و س6 (أقواس الصيغة انقلبت عند الكتابة)، C3-L3-O05 س7
begin;
create temp table _r (code text, n int, opts jsonb, ci int, notes jsonb) on commit drop;
insert into _r values
  ('C3-L3-O01', 1, '["عدد إلكترونات المستوى الخارجي للذرة المتعادلة", "عدد الإلكترونات التي تفقدها الذرة أو تكتسبها أو تشارك بها", "عدد البروتونات في نواة الذرة"]'::jsonb, 1, '["هذا تعريف إلكترونات التكافؤ؛ عدد التأكسد يعبر عن الإلكترونات المفقودة أو المكتسبة أو المشارَك بها.", "", "عدد البروتونات هو العدد الذري لا عدد التأكسد."]'::jsonb),
  ('C3-L3-O03', 2, '["NH₄(SO₄)₂", "(NH₄)₂SO₄", "NH₄SO₄"]'::jsonb, 1, '["عُكس التبديل؛ هذه الصيغة مجموع شحناتها (+1) + 2(−2) = −3.", "", "NH₄SO₄ مجموع شحناتها (+1) + (−2) = −1، فهي غير متعادلة."]'::jsonb),
  ('C3-L3-O03', 6, '["NH₄(CO₃)₂", "(NH₄)₂CO₃", "NH₄CO₃"]'::jsonb, 1, '["عُكس التبديل؛ هذه الصيغة مجموع شحناتها (+1) + 2(−2) = −3.", "", "NH₄CO₃ مجموع شحناتها (+1) + (−2) = −1."]'::jsonb),
  ('C3-L3-O05', 7, '["كبريت الصوديوم", "كبريتات الصوديوم", "كبريتيد الصوديوم"]'::jsonb, 1, '["«كبريت» اسم العنصر، ولا يسمى به الأيون عديد الذرات.", "", "كبريتيد الصوديوم اسم Na₂S الذي يحتوي على الأيون أحادي الذرة S²⁻."]'::jsonb);
create temp table _rq on commit drop as
  select q.id, r.* from _r r join public.objectives o on o.code = r.code join public.questions q on q.objective_id = o.id and q.type = 'mcq' and q.number = r.n;
insert into public.revisions (entity, entity_id, action, before_json, after_json, note, user_name)
  select 'question', rq.id, 'edit', jsonb_build_object('options', q.options, 'correctIndex', a.correct_index), jsonb_build_object('options', rq.opts, 'correctIndex', rq.ci),
    'إعادة السؤال إلى نسخته المصححة: كان المفتاح أو أحد البدائل غير صحيح بعد تعديل يدوي (2026-10-16)', 'مالك المشروع'
  from _rq rq join public.questions q on q.id = rq.id join public.question_answers a on a.question_id = rq.id
  where q.options is distinct from rq.opts or a.correct_index is distinct from rq.ci;
update public.questions q set options = rq.opts, status = 'approved', reviewed_at = now(), updated_at = now() from _rq rq where q.id = rq.id;
update public.question_answers a set correct_index = rq.ci, distractor_notes = rq.notes from _rq rq where a.question_id = rq.id;
update public.practice_answers p set correct = (p.choice = rq.ci) from _rq rq where p.question_id = rq.id;
update public.practice_sessions s set score = (select count(*) filter (where pa.correct) from public.practice_answers pa where pa.session_id = s.id)
  where s.finished_at is not null and s.id in (select pa.session_id from public.practice_answers pa join _rq rq on rq.id = pa.question_id);
select r.code || ' سؤال ' || r.n as "السؤال", q.options as "البدائل", a.correct_index + 1 as "رقم الإجابة الصحيحة", q.status as "الحالة"
  from _rq r join public.questions q on q.id = r.id join public.question_answers a on a.question_id = r.id order by r.code, r.n;
commit;
