-- قسم «الاستعداد للتحصيلي» (1/1) — يولَّد بـ node scripts/build-tahsili-seed.js؛ لا تعدّله يدويًا.
-- يتطلب تنفيذ supabase/schema.sql أولًا. آمن للتكرار.
begin;
insert into public.chapters (id, course_id, number, title, description) values (501, 5, 1, 'الأحياء والبيئة', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50199, 501, 99, 'كل الصفوف · مراجعة شاملة', 'الصف كل الصفوف')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5019901, 50199, 'T-S1-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.chapters (id, course_id, number, title, description) values (502, 5, 2, 'الكيمياء', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50201, 502, 1, 'أول ثانوي · مقدمة في علم الكيمياء', 'الصف أول ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020101, 50201, 'T-S2-U01-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50202, 502, 2, 'أول ثانوي · الخواص والتغيرات والمخاليط', 'الصف أول ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020201, 50202, 'T-S2-U02-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50203, 502, 3, 'أول ثانوي · تركيب الذرة', 'الصف أول ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020301, 50203, 'T-S2-U03-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50204, 502, 4, 'أول ثانوي · العنصر والمركب والتفاعلات الكيميائية', 'الصف أول ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020401, 50204, 'T-S2-U04-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50205, 502, 5, 'أول ثانوي · الحسابات الكيميائية', 'الصف أول ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020501, 50205, 'T-S2-U05-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50206, 502, 6, 'ثاني ثانوي · الضوء والكم والذرة ومستوياتها', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020601, 50206, 'T-S2-U06-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50207, 502, 7, 'ثاني ثانوي · التوزيع الإلكتروني', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020701, 50207, 'T-S2-U07-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50208, 502, 8, 'ثاني ثانوي · الجدول الدوري الحديث', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020801, 50208, 'T-S2-U08-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50209, 502, 9, 'ثاني ثانوي · تصنيف العناصر وتدرج خواصها', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5020901, 50209, 'T-S2-U09-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50210, 502, 10, 'ثاني ثانوي · الروابط والمركبات الأيونية', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021001, 50210, 'T-S2-U10-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50211, 502, 11, 'ثاني ثانوي · الرابطة الفلزية والتساهمية', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021101, 50211, 'T-S2-U11-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50212, 502, 12, 'ثاني ثانوي · تراكيب لويس وأشكال الجزيئات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021201, 50212, 'T-S2-U12-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50213, 502, 13, 'ثاني ثانوي · الكهروسالبية والقوى بين الجزيئات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021301, 50213, 'T-S2-U13-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50214, 502, 14, 'ثاني ثانوي · المادة الغازية', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021401, 50214, 'T-S2-U14-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50215, 502, 15, 'ثاني ثانوي · المواد السائلة والصلبة', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021501, 50215, 'T-S2-U15-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50216, 502, 16, 'ثاني ثانوي · تغيرات الحالة الفيزيائية', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021601, 50216, 'T-S2-U16-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50217, 502, 17, 'ثاني ثانوي · الطاقة والكيمياء الحرارية', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021701, 50217, 'T-S2-U17-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50218, 502, 18, 'ثاني ثانوي · سرعة التفاعلات الكيميائية', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021801, 50218, 'T-S2-U18-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50219, 502, 19, 'ثاني ثانوي · الاتزان الكيميائي', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5021901, 50219, 'T-S2-U19-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50220, 502, 20, 'ثاني ثانوي · الهيدروكربونات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022001, 50220, 'T-S2-U20-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50221, 502, 21, 'ثاني ثانوي · متشكلات الهيدروكربونات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022101, 50221, 'T-S2-U21-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50222, 502, 22, 'ثاني ثانوي · مشتقات الهيدروكربونات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022201, 50222, 'T-S2-U22-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50223, 502, 23, 'ثاني ثانوي · تفاعلات المشتقات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022301, 50223, 'T-S2-U23-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50224, 502, 24, 'ثاني ثانوي · البوليمرات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022401, 50224, 'T-S2-U24-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50225, 502, 25, 'ثاني ثانوي · الكيمياء الحيوية', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022501, 50225, 'T-S2-U25-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50226, 502, 26, 'ثاني ثانوي · قوانين وحسابات الغازات', 'الصف ثاني ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022601, 50226, 'T-S2-U26-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50227, 502, 27, 'ثالث ثانوي · المخاليط وتركيز المحلول', 'الصف ثالث ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022701, 50227, 'T-S2-U27-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50228, 502, 28, 'ثالث ثانوي · الذوبان والخواص الجامعة للمحاليل', 'الصف ثالث ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022801, 50228, 'T-S2-U28-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50229, 502, 29, 'ثالث ثانوي · الأحماض والقواعد', 'الصف ثالث ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5022901, 50229, 'T-S2-U29-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50230, 502, 30, 'ثالث ثانوي · الأكسدة والاختزال', 'الصف ثالث ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5023001, 50230, 'T-S2-U30-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50231, 502, 31, 'ثالث ثانوي · الكيمياء الكهربائية', 'الصف ثالث ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5023101, 50231, 'T-S2-U31-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50232, 502, 32, 'ثالث ثانوي · البطاريات والتحليل الكهربائي', 'الصف ثالث ثانوي')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5023201, 50232, 'T-S2-U32-T01', 1, 'أسئلة الوحدة', 'أسئلة الوحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.lessons (id, chapter_id, number, title, summary) values (50299, 502, 99, 'كل الصفوف · مراجعة شاملة', 'الصف كل الصفوف')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5029901, 50299, 'T-S2-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.chapters (id, course_id, number, title, description) values (503, 5, 3, 'الفيزياء', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50399, 503, 99, 'كل الصفوف · مراجعة شاملة', 'الصف كل الصفوف')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5039901, 50399, 'T-S3-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
insert into public.chapters (id, course_id, number, title, description) values (504, 5, 4, 'الرياضيات', '25% من أسئلة الاختبار')
on conflict (id) do update set title = excluded.title;
insert into public.lessons (id, chapter_id, number, title, summary) values (50499, 504, 99, 'كل الصفوف · مراجعة شاملة', 'الصف كل الصفوف')
on conflict (id) do update set title = excluded.title, summary = excluded.summary;
insert into public.objectives (id, lesson_id, code, number, original_text, approved_text, thinking_level, review_status)
values (5049901, 50499, 'T-S4-U99-T01', 1, 'أسئلة متنوعة لم تُصنَّف في وحدة', 'أسئلة متنوعة لم تُصنَّف في وحدة', null, 'approved')
on conflict (id) do update set original_text = excluded.original_text, approved_text = excluded.approved_text;
delete from public.lessons l using public.chapters c
where l.chapter_id = c.id and c.course_id = 5 and l.id not in (50199, 50201, 50202, 50203, 50204, 50205, 50206, 50207, 50208, 50209, 50210, 50211, 50212, 50213, 50214, 50215, 50216, 50217, 50218, 50219, 50220, 50221, 50222, 50223, 50224, 50225, 50226, 50227, 50228, 50229, 50230, 50231, 50232, 50299, 50399, 50499)
  and not exists (select 1 from public.objectives o join public.questions q on q.objective_id = o.id where o.lesson_id = l.id);
commit;
