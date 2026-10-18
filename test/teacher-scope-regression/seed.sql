update courses set status='ready' where id in (1,2,4);
insert into auth.users (id,email) values
 ('a0000000-0000-0000-0000-00000000000a','ta@x.com'),('b0000000-0000-0000-0000-00000000000b','tb@x.com'),
 ('d0000000-0000-0000-0000-00000000000d','s1@x.com'),('e0000000-0000-0000-0000-00000000000e','s2@x.com'),('f0000000-0000-0000-0000-00000000000f','own@x.com'),
 ('90000000-0000-0000-0000-000000000001','rev@x.com'),('90000000-0000-0000-0000-000000000002','sup@x.com'),('90000000-0000-0000-0000-000000000003','prin@x.com'),
 ('90000000-0000-0000-0000-000000000004','s3@x.com') on conflict do nothing;
update profiles set role='viewer' where email in ('ta@x.com','tb@x.com');
update profiles set role='admin' where email='own@x.com';
update profiles set role='reviewer' where email='rev@x.com';
update profiles set role='supervisor' where email='sup@x.com';
update profiles set role='principal' where email='prin@x.com';
update profiles set role='student', managed=true, display_name='طالب1', section='1', grade='الأول الثانوي', profile_confirmed=true where email='s1@x.com';
update profiles set role='student', managed=true, display_name='طالب2', section='2', grade='الأول الثانوي', profile_confirmed=true where email='s2@x.com';
update profiles set role='student', managed=true, display_name='طالب3', section='1', grade='الثاني الثانوي', profile_confirmed=true where email='s3@x.com';
insert into course_enrollments select user_id, 1 from profiles where email in ('s1@x.com','s2@x.com','s3@x.com') on conflict do nothing;
insert into course_enrollments select user_id, 2 from profiles where email in ('s1@x.com','s2@x.com') on conflict do nothing;
-- practice data
do $$ declare u record; sid bigint; qq record; n int;
begin
  for u in select user_id from profiles where email in ('s1@x.com','s2@x.com','s3@x.com') loop
    for n in 1..3 loop
      insert into practice_sessions (user_id, settings, question_ids, total, score, finished_at, created_at)
        values (u.user_id, '{}', '{}', 5, 3, now(), now() - (n || ' days')::interval) returning id into sid;
      for qq in select q.id, a.correct_index from questions q join question_answers a on a.question_id=q.id join objectives o on o.id=q.objective_id
               join lessons l on l.id=o.lesson_id join chapters c on c.id=l.chapter_id where q.type='mcq' and c.course_id in (1,2) order by random() limit 8 loop
        insert into practice_answers (session_id, question_id, choice, correct, answered_at) values (sid, qq.id, 0, qq.correct_index=0, now()) on conflict do nothing;
      end loop;
    end loop;
  end loop;
end $$;
