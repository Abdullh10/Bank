// فحوص تعدد المواد — المرحلة 4 (2026-11-19): نطاق المراجع بالمواد، والاستبانة لكل مقرر ومادته، وتبويبات المواد للطالب،
// ولوحة مقارنة المواد. يستدعيها test/supabase-e2e.mjs بعد فحوص المرحلتين 2 و3 (والصور في SHOTS_DIR إن حُدد، وإلا في مجلد الإخراج).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const OWNER = '55555555-5555-5555-5555-555555555555', VIEW = '22222222-2222-2222-2222-222222222222', REV = '11111111-1111-1111-1111-111111111111';
const MIGRATION = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'supabase', 'subjects-phase4-2026-11-19.sql');

export async function subjectsP4Steps({ p, ok, pool, asRole, BASE, OUT }) {
  const SHOTS = process.env.SHOTS_DIR || OUT;
  fs.mkdirSync(SHOTS, { recursive: true });
  const shot = async (name, full = true) => { await p.evaluate(() => document.querySelectorAll('.toast').forEach(t => t.remove())); await p.waitForTimeout(300); await p.screenshot({ path: `${SHOTS}/${name}.png`, fullPage: full }); };
  // لقطة الشاشة نفسها بأربعة أوضاع: 1280 و390 فاتحًا، و1280 و390 ليليًا. prep يعيد بناء الصفحة في كل وضع
  const shots4 = async (name, prep, full = true) => {
    for (const [scheme, tag] of [['light', ''], ['dark', '-dark']]) {
      await p.emulateMedia({ colorScheme: scheme });
      for (const w of [1280, 390]) { await p.setViewportSize({ width: w, height: w === 390 ? 844 : 900 }); await prep(); await shot(`${name}-${w}${tag}`, full); }
    }
    await p.emulateMedia({ colorScheme: 'light' }); await p.setViewportSize({ width: 1280, height: 900 });
  };
  const noHScroll = () => p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1);
  const login = async user => {
    await p.goto(BASE + '#/'); await p.waitForSelector('#l-user, #logout');
    if (await p.locator('#logout').count()) { await p.click('#logout'); await p.waitForSelector('#l-user'); }
    await p.fill('#l-user', user); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
  };
  const cleanup = async () => {
    await pool.query(`delete from public.comms where course_id in (select id from public.courses where subject_id = 'phys')`);
    await pool.query(`delete from public.practice_sessions where user_id in (select id from auth.users where email like 'p4%@chem21.local')`);
    await pool.query(`delete from auth.users where email like 'p4%@chem21.local'`);
    await pool.query(`delete from public.staff_subjects`);
    await pool.query(`delete from public.questions where id between 990001 and 990009`);
    await pool.query(`delete from public.courses where subject_id = 'phys'`);
    await pool.query(`delete from public.subjects where id = 'phys'`);
  };
  await cleanup();

  // ---------- بيانات: مادة الفيزياء بمقرر متاح فيه ثلاثة أسئلة معتمدة ----------
  await pool.query(`insert into public.subjects (id, name, icon, color, sort_order) values ('phys', 'الفيزياء', 'atom', 'indigo', 20)`);
  await pool.query(`insert into public.courses (id, code, title, subject, subject_id, grade, term, country, status, sort_order, kind)
    values (101, 'فيزياء 1', 'فيزياء 1', 'الفيزياء', 'phys', 'الأول الثانوي', 'الأول', 'السعودية', 'ready', 111, 'course')`);
  await pool.query(`insert into public.chapters (id, course_id, number, title) values (990001, 101, 1, 'الحركة في خط مستقيم')`);
  await pool.query(`insert into public.lessons (id, chapter_id, number, title) values (990001, 990001, 1, 'السرعة المتوسطة')`);
  await pool.query(`insert into public.objectives (id, lesson_id, code, number, original_text, review_status) values (990001, 990001, 'P1-C1-L1-O01', 1, 'يحسب السرعة المتوسطة لجسم متحرك', 'approved')`);
  for (const [i, stem, lvl] of [[1, 'قطعت سيارة 100 m في 5 s. ما سرعتها المتوسطة؟', 'تذكر'], [2, 'عدّاء سرعته 4 m/s. كم مترًا يقطع في 10 s؟', 'فهم'], [3, 'أي الكميات الآتية متجهة؟', 'تحليل']]) {
    await pool.query(`insert into public.questions (id, objective_id, type, number, stem, status, options, thinking_level, difficulty) values ($1, 990001, 'mcq', $2, $3, 'approved', $4, $5, 'سهل')`,
      [990000 + i, i, stem, JSON.stringify(i === 3 ? ['الإزاحة', 'المسافة', 'الزمن', 'الكتلة'] : i === 1 ? ['20 m/s', '500 m/s', '5 m/s', '0.05 m/s'] : ['40 m', '2.5 m', '14 m', '0.4 m']), lvl]);
    await pool.query(`insert into public.question_answers (question_id, correct_index, explanation) values ($1, 0, 'تفسير')`, [990000 + i]);
  }
  const mk = async (email, role, name, extra = {}) => {
    const { rows: [u] } = await pool.query(`insert into auth.users (email) values ($1) returning id`, [email]);
    await pool.query(`update public.profiles set role = $2, display_name = $3, managed = $4, staff = $5, profile_confirmed = true, grade = $6, section = $7 where user_id = $1`,
      [u.id, role, name, role === 'student', role !== 'student', extra.grade || null, extra.section || null]);
    return u.id;
  };
  const RP = await mk('p4rev@chem21.local', 'reviewer', 'مراجعة الفيزياء');
  const ST = await mk('p4st1@chem21.local', 'student', 'سارة الفيزيائية', { grade: 'ثاني ثانوي', section: 'م4' });
  const ST2 = await mk('p4st2@chem21.local', 'student', 'طالب مادة واحدة', { grade: 'ثاني ثانوي', section: 'م4' });
  await pool.query(`insert into public.course_enrollments (user_id, course_id) values ($1, 1), ($1, 101), ($2, 1)`, [ST, ST2]);
  const chemQ = (await pool.query(`select q.id, o.code from public.questions q join public.objectives o on o.id = q.objective_id join public.lessons l on l.id = o.lesson_id
    join public.chapters c on c.id = l.chapter_id where c.course_id = 1 order by q.id limit 1`)).rows[0];

  // ================= (1) المراجع بنطاق مادة =================
  const setScope = (uid, subs) => asRole(uid, 'select public.admin_set_staff_subjects($1, $2::text[]) r', [RP, subs]);
  ok('scope: reviewer cannot set scopes (owner only)', (await setScope(REV, ['phys'])).error?.code === '42501');
  ok('scope: subject scope refused for a teacher account', /للمراجع العلمي والمشرف/.test((await asRole(OWNER, 'select public.admin_set_staff_subjects($1, $2::text[]) r', [VIEW, ['phys']])).error?.message || ''));
  const set1 = await setScope(OWNER, ['phys']);
  ok('scope: owner scopes the reviewer to physics', JSON.stringify(set1.data?.subjects) === '["phys"]', JSON.stringify(set1));
  const call = (fn, args = '') => asRole(RP, `select to_jsonb(public.${fn}(${args})) r`);
  const crs = await call('get_courses');
  ok('scoped reviewer: get_courses lists only physics courses', JSON.stringify(crs.data?.map(c => c.id)) === '[101]', JSON.stringify(crs.data?.map(c => c.id)));
  const me = await call('get_me');
  ok('scoped reviewer: get_me reports the scope', JSON.stringify(me.data?.scope) === '["phys"]');
  const denied = [await call('get_bank', `'{"course":1}'::jsonb`), await call('get_chapters', '1'), await call('get_stats', '1'), await call('get_objective', `'${chemQ.code}'`),
    await call('get_question', String(chemQ.id)), await call('set_question_status', `${chemQ.id}, 'in_review'`), await call('add_note', `'${chemQ.code}', 'objective', 'ملاحظة خارج النطاق'`),
    await call('review_objective', `'${chemQ.code}', 'approve'`), await call('get_dashboard', '1'), await call('teacher_progress', 'null, 1')];
  ok('scoped reviewer: cannot read or review another subject\'s questions (bank, chapters, stats, objective, question, status, note, approve, dashboard, progress)',
    denied.every(r => !!r.error), JSON.stringify(denied.map(r => r.error?.code || 'OK')));
  ok('scoped reviewer: nothing written by refused calls', (await pool.query(`select status from public.questions where id = $1`, [chemQ.id])).rows[0].status === 'approved'
    && (await pool.query(`select count(*)::int n from public.review_notes where body = 'ملاحظة خارج النطاق'`)).rows[0].n === 0);
  const direct = await asRole(RP, `select jsonb_build_object('q', (select count(*) from public.questions), 'o', (select count(*) from public.objectives), 'a', (select count(*) from public.question_answers),
    'r', (select count(*) from public.revisions where entity in ('question', 'objective') and entity_id < 990000)) r`);
  ok('scoped reviewer: direct table reads (RLS) limited to physics, revisions of other subjects hidden', direct.data?.q === 3 && direct.data.o === 1 && direct.data.a === 3 && direct.data.r === 0, JSON.stringify(direct.data));
  const phBank = await call('get_bank', `'{"course":101}'::jsonb`);
  ok('scoped reviewer: physics bank with answers', phBank.data?.length === 3 && 'correctIndex' in phBank.data[0], JSON.stringify(phBank.error));
  const st1 = await call('set_question_status', `990002, 'in_review'`);
  ok('scoped reviewer: can review physics questions', !st1.error && (await pool.query('select status from public.questions where id = 990002')).rows[0].status === 'in_review', JSON.stringify(st1.error));
  await call('set_question_status', `990002, 'approved'`);
  await pool.query(`update public.question_answers set auto_check = '{"passed": true}' where question_id between 990001 and 990003`);
  await call('set_question_status', `990002, 'approved'`);
  await pool.query(`insert into public.review_notes (objective_id, entity, body, author_name) select o.id, 'objective', 'ملاحظة على الكيمياء', 'المالك' from public.objectives o where o.code = $1`, [chemQ.code]);
  const nn = await call('add_note', `'P1-C1-L1-O01', 'objective', 'ملاحظة على الفيزياء'`);
  const notes = (await call('get_notes', `null, 'all'`)).data || [];
  ok('scoped reviewer: notes list only physics notes', notes.length >= 1 && notes.every(n => n.objectiveCode.startsWith('P1-')) && !nn.error, JSON.stringify(notes.map(n => n.objectiveCode)));
  const revs = (await call('get_revisions', '500')).data || [];
  ok('scoped reviewer: revisions log limited to physics items', revs.length >= 1 && revs.every(r => ['question', 'objective', 'supplement'].includes(r.entity) && Number(r.entity_id) >= 990000), JSON.stringify(revs.map(r => r.entity + r.entity_id)).slice(0, 200));
  const unscoped = await asRole(REV, `select jsonb_build_object('bank', jsonb_array_length(public.get_bank('{"course":1}'::jsonb)), 'courses', (select jsonb_agg(x->'id') from jsonb_array_elements(public.get_courses()) x)) r`);
  ok('unscoped reviewer keeps seeing everything (backward compatible)', unscoped.data?.bank === 2580 && unscoped.data.courses.includes(1) && unscoped.data.courses.includes(101), JSON.stringify(unscoped));
  // الواجهة: المراجعة المقيَّدة لا ترى إلا مقرر الفيزياء
  await p.evaluate(() => { try { localStorage.removeItem('itqan-course'); } catch { /* */ } });
  await login('p4rev');
  await p.goto(BASE + '#/'); await p.waitForSelector('.course-card');
  ok('scoped reviewer UI: courses page shows only فيزياء 1', JSON.stringify(await p.$$eval('.course-card h2', hs => hs.map(h => h.textContent.trim()))) === '["فيزياء 1"]');
  await p.goto(BASE + '#/bank'); await p.waitForSelector('#bank-count');
  ok('scoped reviewer UI: bank opens on the physics course', /^3/.test((await p.locator('#bank-count').first().innerText()).trim()));
  // المالك: صفحة حسابات الفريق — نطاق المواد
  await setScope(OWNER, []);
  ok('scope: empty scope = all subjects again', (await call('get_courses')).data?.some(c => c.id === 1));
  await login('owner');
  await p.goto(BASE + '#/team'); await p.waitForSelector(`tr[data-id="${RP}"] .tm-scope-btn`);
  ok('team page: reviewer row shows «يرى كل المواد»', (await p.locator(`tr[data-id="${RP}"] .tm-scope`).innerText()).includes('يرى كل المواد'));
  await p.click(`tr[data-id="${RP}"] .tm-scope-btn`); await p.click('.tm-assign [data-sc="phys"]');
  await shot('team-scope-1280', false);
  await p.click('.tm-ssave'); await p.waitForSelector('.toast');
  ok('team page: scope saved from the accounts page', (await pool.query('select array_agg(subject_id)::text a from public.staff_subjects where user_id = $1', [RP])).rows[0].a === '{phys}'
    && (await p.locator(`tr[data-id="${RP}"] .tm-scope`).innerText()).includes('الفيزياء'));
  await shots4('team-scope', async () => {
    await p.goto(BASE + '#/team'); await p.waitForSelector(`tr[data-id="${RP}"] .tm-scope-btn`);
    await p.click(`tr[data-id="${RP}"] .tm-scope-btn`); await p.waitForSelector('.tm-ssave');
    await p.locator('.tm-assign').scrollIntoViewIfNeeded();
  }, false);
  // صفحة المادة ← المعلمون: قسم المراجعين والمشرفين
  await p.goto(BASE + '#/subject/phys'); await p.waitForSelector('.stabs');
  await p.click('.stabs [data-tab="teachers"]');
  ok('subject page: reviewers section lists the scoped reviewer and the unscoped one', (await p.locator(`[data-pane="teachers"] tr[data-staff="${RP}"] [data-sremove]`).count()) === 1
    && (await p.locator(`[data-pane="teachers"] tr[data-staff="${REV}"] [data-sadd]`).innerText()).includes('قصر على الفيزياء'));
  await p.click(`tr[data-staff="${REV}"] [data-sadd]`); await p.waitForFunction(id => document.querySelector(`tr[data-staff="${id}"] [data-sremove]`), REV);
  ok('subject page: «قصر على الفيزياء» scopes the reviewer', (await pool.query('select count(*)::int n from public.staff_subjects where user_id = $1 and subject_id = $2', [REV, 'phys'])).rows[0].n === 1);
  await shots4('subject-reviewers', async () => {
    await p.goto(BASE + '#/subject/phys'); await p.waitForSelector('.stabs'); await p.click('.stabs [data-tab="teachers"]');
    await p.locator('.tab-sub').scrollIntoViewIfNeeded();
  }, false);
  p.once('dialog', d => d.accept());
  await p.click(`tr[data-staff="${REV}"] [data-sremove]`); await p.waitForFunction(id => document.querySelector(`tr[data-staff="${id}"] [data-sadd]`), REV);
  ok('subject page: removing the only subject returns the reviewer to all subjects', (await pool.query('select count(*)::int n from public.staff_subjects where user_id = $1', [REV])).rows[0].n === 0);
  await asRole(OWNER, 'select public.admin_update_staff($1, null, $2) r', [RP, 'principal']);
  ok('scope: changing the role away from reviewer clears the scope', (await pool.query('select count(*)::int n from public.staff_subjects where user_id = $1', [RP])).rows[0].n === 0);

  // ================= (2) الاستبانة لكل مقرر ومادته =================
  await p.evaluate(() => { try { localStorage.setItem('itqan-course', '101'); } catch { /* */ } });
  await login('owner');
  await p.goto(BASE + '#/comms'); await p.waitForSelector('#cm-send');
  await p.check('[name=cm-kind][value=survey]');
  ok('survey UI: physics course — notice and items use the subject name', (await p.locator('.sv-for').innerText()).includes('فيزياء 1') && (await p.locator('.sv-preview').textContent()).includes('فهم دروس الفيزياء'));
  ok('survey UI: recipients counted from the course enrolment only', /\(1\)/.test(await p.locator('#cm-mode option').first().innerText()));
  await p.evaluate(() => document.querySelector('.sv-preview').open = true);
  await shot('comms-survey-physics-1280');
  await p.click('#cm-send'); await p.waitForSelector('.toast');
  const phSv = (await pool.query(`select id, course_id, n_recipients from public.comms where kind = 'survey' and course_id = 101 order by id desc limit 1`)).rows[0];
  ok('survey: sent for the physics course to its enrolled students only', phSv?.n_recipients === 1, JSON.stringify(phSv));
  const listAll = (await asRole(OWNER, `select public.staff_list_comms(null, '{}'::jsonb) r`)).data;
  const listPh = (await asRole(OWNER, `select public.staff_list_comms(null, '{"subject":"phys"}'::jsonb) r`)).data;
  const listCh = (await asRole(OWNER, `select public.staff_list_comms(null, '{"subject":"chem","kind":"survey"}'::jsonb) r`)).data;
  ok('survey reports: filter by subject (physics only / chemistry surveys keep their results)', listPh.length >= 1 && listPh.every(c => c.subjectId === 'phys')
    && listCh.length >= 1 && listCh.every(c => c.subjectId === 'chem' && c.kind === 'survey') && listAll.some(c => c.subject === 'الفيزياء'), JSON.stringify([listPh.length, listCh.length]));
  const res = (await asRole(OWNER, 'select public.survey_results($1) r', [phSv.id])).data;
  ok('survey results carry the course and subject', res.subject === 'الفيزياء' && res.course === 'فيزياء 1');
  await p.click('[data-cmf-subj="phys"]'); await p.waitForSelector('[data-cmf-subj="phys"].on');
  ok('survey UI: sent list filtered by subject chip', (await p.locator('.cm-item').count()) >= 1 && (await p.locator('.cm-item .cm-course').allInnerTexts()).every(t => t.includes('فيزياء')));
  await shots4('comms-filter-physics', async () => {
    await p.goto(BASE + '#/comms'); await p.waitForSelector('#cm-send'); await p.check('[name=cm-kind][value=survey]');
    await p.locator('.cm-filter').scrollIntoViewIfNeeded();
  }, false);
  await p.click('[data-cmf-subj=""]'); await p.waitForSelector('[data-cmf-subj=""].on');
  // الترحيل: استبانة قديمة بلا مقرر تُنقل إلى مقرر الكيمياء الذي ينتمي إليه طلابها، ويُعاد تنفيذ الملف دون خطأ
  const { rows: [old] } = await pool.query(`insert into public.comms (kind, sender_id, course_id, title, n_recipients) values ('survey', $1, 0, 'استبانة قديمة', 1) returning id`, [OWNER]);
  await pool.query('insert into public.comm_recipients (comm_id, student_id) values ($1, $2)', [old.id, ST2]);
  await pool.query(`delete from public.schema_flags where key = 'survey_course_2026_11_19'`);
  let migErr = null;
  try { await pool.query(fs.readFileSync(MIGRATION, 'utf8')); await pool.query(fs.readFileSync(MIGRATION, 'utf8')); } catch (e) { migErr = e.message; }
  ok('migration file applies and is re-runnable; old survey moved to its chemistry course', !migErr && (await pool.query('select course_id from public.comms where id = $1', [old.id])).rows[0].course_id === 1, migErr);
  ok('migration keeps the physics survey on its course', (await pool.query('select course_id from public.comms where id = $1', [phSv.id])).rows[0].course_id === 101);
  await pool.query('delete from public.comms where id = $1', [old.id]);

  // ================= (3) تبويبات المواد للطالب =================
  await p.evaluate(() => { try { localStorage.removeItem('itqan.student.subject.v1'); } catch { /* */ } });
  await login('p4st1');
  await p.waitForSelector('.st-subjects');
  ok('student tabs: two subject tabs (chemistry first) for a student in two subjects', JSON.stringify(await p.$$eval('.st-subj', bs => bs.map(b => b.textContent.trim()))) === '["الكيمياء","الفيزياء"]'
    && (await p.locator('.st-subj.on').innerText()).includes('الكيمياء'));
  ok('student tabs: chemistry tab shows only chemistry chapters', (await p.locator('details.st-ch').count()) === 7);
  await p.click('.st-subj[data-st-subj="phys"]'); await p.waitForSelector('.st-subj.on[data-st-subj="phys"]');
  ok('student tabs: physics tab shows physics lessons and header course', (await p.locator('details.st-ch').count()) === 1 && (await p.locator('details.st-ch').innerText()).includes('الحركة')
    && (await p.locator('#brand-sub').innerText()).includes('فيزياء 1'));
  await p.goto(BASE + '#/rank'); await p.waitForSelector('.st-subjects');
  ok('student tabs: the choice is kept on the excellence page', (await p.locator('.st-subj.on').innerText()).includes('الفيزياء'));
  await p.goto(BASE + '#/inbox'); await p.waitForSelector('[data-survey]');
  await p.click('[data-survey]'); await p.click('#sv-go'); await p.waitForSelector('.sv-item legend');
  ok('student survey: items read «فهم دروس الفيزياء»', (await p.locator('.sv-item legend').first().innerText()).includes('فهم دروس الفيزياء'));
  await shots4('student-survey-physics', async () => { await p.goto(BASE + '#/inbox'); await p.waitForSelector('[data-survey]'); await p.click('[data-survey]'); await p.click('#sv-go'); await p.waitForSelector('.sv-item'); });
  // جلسة تدريب في الفيزياء (تغذي لوحة المقارنة)
  await p.goto(BASE + '#/'); await p.waitForSelector('.st-subj.on[data-st-subj="phys"]');
  await p.locator('details.st-ch summary').first().click(); await p.locator('[data-lesson]').first().check();
  await p.selectOption('#s-count', '5'); await p.click('#s-start'); await p.waitForSelector('.st-opt');
  await p.waitForTimeout(3200); await p.locator('.st-opt').first().click(); await p.waitForSelector('.st-fb');
  ok('student tabs: a practice session in physics uses physics questions', (await pool.query(`select count(*)::int n from public.practice_answers a join public.practice_sessions s on s.id = a.session_id where s.user_id = $1 and a.question_id between 990001 and 990003`, [ST])).rows[0].n === 1);
  p.once('dialog', d => d.accept()); await p.click('#st-end'); await p.waitForTimeout(800);
  await shots4('student-tabs', async () => { await p.goto(BASE + '#/rank'); await p.goto(BASE + '#/'); await p.waitForSelector('.st-subjects'); await p.waitForTimeout(500); });
  await p.setViewportSize({ width: 390, height: 844 }); await p.goto(BASE + '#/'); await p.waitForSelector('.st-subjects');
  ok('phone: student home without horizontal scroll', await noHScroll());
  await p.setViewportSize({ width: 1280, height: 900 });
  await login('p4st2');
  await p.waitForSelector('details.st-ch');
  ok('student tabs: one subject → no tabs (unchanged look)', (await p.locator('.st-subjects').count()) === 0);

  // ================= (4) لوحة مقارنة المواد =================
  const cmp = await asRole(OWNER, 'select public.admin_compare_subjects() r');
  const ch = cmp.data?.find(r => r.id === 'chem'), ph = cmp.data?.find(r => r.id === 'phys');
  ok('compare RPC: chemistry and physics side by side with aggregates', ch && ph && ch.questions >= 2500 && ph.questions === 3 && ph.courses === 1 && ph.students === 1 && ph.answers7 === 1 && ph.active7 === 1
    && ph.surveys?.n === 1 && cmp.data.some(r => r.shared), JSON.stringify(ph));
  ok('compare RPC: no per-student fields', !/user_id|username|displayName|"name":"سارة/.test(JSON.stringify(cmp.data)));
  const refusedCmp = [];
  for (const uid of [VIEW, REV, ST]) refusedCmp.push((await asRole(uid, 'select public.admin_compare_subjects() r')).error?.code === '42501');
  ok('compare RPC: owner only (teacher, reviewer and student refused)', refusedCmp.every(Boolean), JSON.stringify(refusedCmp));
  await login('owner');
  await p.goto(BASE + '#/'); await p.waitForSelector('a[href="#/compare"]');
  await p.click('a[href="#/compare"]'); await p.waitForSelector('table.cmp');
  ok('compare page: linked from «المواد», one column per subject plus shared programmes', JSON.stringify(await p.$$eval('table.cmp thead th.cmp-h', hs => hs.map(h => h.textContent.trim()))) === '["الكيمياء","الفيزياء","برامج مشتركة"]');
  await shots4('compare', async () => { await p.goto(BASE + '#/compare'); await p.waitForSelector('table.cmp'); });
  await p.setViewportSize({ width: 390, height: 844 }); await p.goto(BASE + '#/compare'); await p.waitForSelector('table.cmp');
  ok('phone: compare page without horizontal page scroll', await noHScroll());
  await p.setViewportSize({ width: 1280, height: 900 });
  await shots4('owner-home-compare-link', async () => { await p.goto(BASE + '#/'); await p.waitForSelector('.scard'); }, false);

  await p.evaluate(() => { try { localStorage.setItem('itqan-course', '1'); localStorage.removeItem('itqan.student.subject.v1'); } catch { /* */ } });
  await cleanup();
}
