-- شغّله بعد آخر جزء: يجب أن تطابق كل الأعمدة القيم المتوقعة.
select
  (select count(*) from public.chapters) = 7 as chapters_ok,
  (select count(*) from public.lessons) = 28 as lessons_ok,
  (select count(*) from public.objectives) = 258 as objectives_ok,
  (select count(*) from public.supplements) = 111 as supplements_ok,
  (select count(*) from public.questions) = 2580 as questions_ok,
  (select count(*) from public.question_answers) = 2580 as answers_ok;
