-- شغّله بعد آخر جزء: يجب أن تكون كل الأعمدة true.
select
  (select count(*) from public.chapters where course_id = 4) = 4 as chapters_ok,
  (select count(*) from public.lessons l join public.chapters c on c.id = l.chapter_id where c.course_id = 4) = 13 as lessons_ok,
  (select count(*) from public.objectives o join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id where c.course_id = 4) = 167 as objectives_ok,
  (select count(*) from public.supplements s join public.objectives o on o.id = s.objective_id join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id where c.course_id = 4) = 6 as supplements_ok,
  (select count(*) from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id where c.course_id = 4) = 0 as questions_ok,
  (select count(*) from public.question_answers a join public.questions q on q.id = a.question_id join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id join public.chapters c on c.id = l.chapter_id where c.course_id = 4) = 0 as answers_ok,
  (select status from public.courses where id = 4) = 'preparing' as still_preparing;
