-- قسم «الاستعداد للتحصيلي» (1/1) — يولَّد بـ node scripts/build-tahsili-seed.js؛ لا تعدّله يدويًا.
-- يتطلب تنفيذ supabase/schema.sql أولًا. آمن للتكرار.
begin;
insert into public.chapters (id, course_id, number, title, description) values (501, 5, 1, 'الأحياء والبيئة', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50199, 501, 99, 'مراجعة شاملة', null)
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5019901, 50199, 'T-S1-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.chapters (id, course_id, number, title, description) values (502, 5, 2, 'الكيمياء', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50201, 502, 1, 'كيمياء 1 · مقدمة في علم الكيمياء', 'الصف الأول الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020101, 50201, 'T-S2-U01-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50202, 502, 2, 'كيمياء 1 · المادة – الخواص والتغيرات', 'الصف الأول الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020201, 50202, 'T-S2-U02-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50203, 502, 3, 'كيمياء 1 · تركيب الذرة', 'الصف الأول الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020301, 50203, 'T-S2-U03-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50204, 502, 4, 'كيمياء 1 · التفاعلات الكيميائية', 'الصف الأول الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020401, 50204, 'T-S2-U04-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50205, 502, 5, 'كيمياء 1 · المول', 'الصف الأول الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020501, 50205, 'T-S2-U05-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50211, 502, 11, 'كيمياء 2-1 · الإلكترونات في الذرة', 'الصف الثاني الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021101, 50211, 'T-S2-U11-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50212, 502, 12, 'كيمياء 2-1 · الجدول الدوري والتدرج في خواص العناصر', 'الصف الثاني الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021201, 50212, 'T-S2-U12-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50213, 502, 13, 'كيمياء 2-1 · المركبات الأيونية والفلزات', 'الصف الثاني الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021301, 50213, 'T-S2-U13-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50214, 502, 14, 'كيمياء 2-1 · الروابط التساهمية', 'الصف الثاني الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021401, 50214, 'T-S2-U14-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50215, 502, 15, 'كيمياء 2-1 · الحسابات الكيميائية', 'الصف الثاني الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021501, 50215, 'T-S2-U15-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50216, 502, 16, 'كيمياء 2-1 · حالات المادة', 'الصف الثاني الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021601, 50216, 'T-S2-U16-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50217, 502, 17, 'كيمياء 2-1 · الغازات', 'الصف الثاني الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021701, 50217, 'T-S2-U17-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50231, 502, 31, 'كيمياء 3 · المخاليط والمحاليل', 'الصف الثالث الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5023101, 50231, 'T-S2-U31-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50232, 502, 32, 'كيمياء 3 · الأحماض والقواعد', 'الصف الثالث الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5023201, 50232, 'T-S2-U32-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50233, 502, 33, 'كيمياء 3 · تفاعلات الأكسدة والاختزال', 'الصف الثالث الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5023301, 50233, 'T-S2-U33-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50234, 502, 34, 'كيمياء 3 · الكيمياء الكهربائية', 'الصف الثالث الثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5023401, 50234, 'T-S2-U34-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50299, 502, 99, 'مراجعة شاملة', null)
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5029901, 50299, 'T-S2-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.chapters (id, course_id, number, title, description) values (503, 5, 3, 'الفيزياء', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50399, 503, 99, 'مراجعة شاملة', null)
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5039901, 50399, 'T-S3-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.chapters (id, course_id, number, title, description) values (504, 5, 4, 'الرياضيات', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50499, 504, 99, 'مراجعة شاملة', null)
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5049901, 50499, 'T-S4-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
commit;
