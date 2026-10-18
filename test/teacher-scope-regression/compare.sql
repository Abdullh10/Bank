\pset tuples_only on
create temp table roles(n text, uid text);
insert into roles select 'admin', user_id::text from profiles where email='own@x.com'
 union all select 'reviewer', user_id::text from profiles where email='rev@x.com'
 union all select 'supervisor', user_id::text from profiles where email='sup@x.com'
 union all select 'principal', user_id::text from profiles where email='prin@x.com'
 union all select 'student1', user_id::text from profiles where email='s1@x.com'
 union all select 'student3', user_id::text from profiles where email='s3@x.com'
 union all select 'teacherA', user_id::text from profiles where email='ta@x.com'
 union all select 'teacherB', user_id::text from profiles where email='tb@x.com';
create temp table calls(c text);
insert into calls values
 ($$select get_stats(1)::text$$),($$select get_stats(2)::text$$),($$select get_chapters(1)::text$$),($$select get_chapters()::text$$),
 ($$select get_chapter(1,1)::text$$),($$select get_chapter(1,2)::text$$),
 ($$select get_bank('{"course":1}')::text$$),($$select get_bank('{"course":2,"chapter":1}')::text$$),($$select get_bank('{}')::text$$),
 ($$select get_objective('K1-C1-L1-O01')::text$$),($$select get_objective('C1-L1-O14')::text$$),
 ($$select (get_dashboard(1)-'generatedAt')::text$$),($$select (get_dashboard(2)-'generatedAt')::text$$),($$select (get_dashboard()-'generatedAt')::text$$),
 ($$select teacher_progress(null,1)::text$$),($$select teacher_progress(null,2)::text$$),($$select teacher_progress('1',2)::text$$),($$select teacher_progress()::text$$),
 ($$select student_catalog()::text$$),($$select student_history()::text$$),
 ($$select get_courses()::text$$),
 ($$select (select jsonb_agg(x->>'id' order by x->>'id') from jsonb_array_elements(get_exam_answers((select array_agg(id) from (select id from questions order by id limit 40) z))) x)::text$$),
 ($$select check_answer((select id from questions q where type='mcq' order by id limit 1),0)::text$$),
 ($$select count(*)::text||'/'||count(distinct objective_id)::text from questions$$),
 ($$select count(*)::text from question_answers$$),($$select count(*)::text from chapters$$),($$select count(*)::text from courses$$),
 ($$select count(*)::text from objectives$$),($$select count(*)::text from lessons$$),($$select count(*)::text from supplements$$);
select r.n||' | '||left(c.c,62)||' | '||tt.h(r.uid, c.c) from roles r cross join calls c order by r.n, c.c;
