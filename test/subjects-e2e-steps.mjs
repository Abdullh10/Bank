// فحوص تعدد المواد (2026-11-15): رئيسية «المواد»، وصفحة المادة، ومبدّل السياق، وإضافة مادة ومقرر، وإسناد المعلم والشعب،
// ورفض دوال الإدارة لغير المالك. يستدعيها test/supabase-e2e.mjs في نهايته (والصور في SHOTS_DIR إن حُدد، وإلا في مجلد الإخراج).
import fs from 'node:fs';

const OWNER = '55555555-5555-5555-5555-555555555555', VIEW = '22222222-2222-2222-2222-222222222222', REV = '11111111-1111-1111-1111-111111111111';

export async function subjectsSteps({ p, ok, pool, asRole, BASE, OUT }) {
  const SHOTS = process.env.SHOTS_DIR || OUT;
  fs.mkdirSync(SHOTS, { recursive: true });
  const shot = async (name, full = true) => { await p.evaluate(() => document.querySelectorAll('.toast').forEach(t => t.remove())); await p.waitForTimeout(250); await p.screenshot({ path: `${SHOTS}/${name}.png`, fullPage: full }); };
  const login = async user => {
    await p.goto(BASE + '#/'); await p.waitForSelector('#l-user, #logout');
    if (await p.locator('#logout').count()) { await p.click('#logout'); await p.waitForSelector('#l-user'); }
    await p.fill('#l-user', user); await p.fill('#l-pass', 'x'); await p.click('button[type=submit]'); await p.waitForSelector('#logout');
  };
  const cleanup = async () => {
    await pool.query(`delete from public.course_enrollments where course_id in (select id from public.courses where subject_id = 'phys')`);
    await pool.query(`delete from public.teacher_courses where course_id in (select id from public.courses where subject_id = 'phys')`);
    await pool.query(`delete from public.courses where subject_id = 'phys'`);
    await pool.query(`delete from public.subjects where id = 'phys'`);
    await pool.query(`delete from auth.users where email like 'msub_@chem21.local'`);
  };
  await cleanup();
  // اختيار مقرر 2-1 حتى تبدأ الحالة من نقطة معروفة
  await p.evaluate(() => { try { localStorage.setItem('itqan-course', '1'); localStorage.removeItem('itqan-recent-courses'); } catch { /* */ } });

  // ---------- رئيسية المالك: المواد ----------
  await login('owner');
  await p.goto(BASE + '#/'); await p.waitForSelector('.scard[data-subject="chem"]');
  const home = await p.locator('main').innerText();
  ok('subjects: owner home is «المواد» with the chemistry card', (await p.locator('main h1').first().innerText()).trim() === 'المواد'
    && (await p.locator('.scard[data-subject="chem"] h2').innerText()).includes('الكيمياء') && (await p.locator('.scard.add').count()) === 1);
  ok('subjects: totals row + shared programmes strip (التحصيلي)', (await p.locator('.totals .total').count()) === 4
    && (await p.locator('.program', { hasText: 'الاستعداد للتحصيلي' }).count()) === 1 && /2,580|2580/.test(home));
  ok('subjects: resume button for the current course', (await p.locator('#sj-resume').innerText()).includes('كيمياء 2-1'));
  ok('subjects: header context pill «الكيمياء › كيمياء 2-1»', /الكيمياء\s*‹\s*كيمياء 2-1/.test(await p.locator('#ctx-btn').innerText()));
  await shot('owner-home-1280');

  // ---------- صفحة المادة ----------
  await p.click('.scard[data-subject="chem"] a[href="#/subject/chem"]'); await p.waitForSelector('.grade');
  const grades = await p.$$eval('.grade', gs => gs.map(g => [g.querySelector('h3').textContent.trim(), [...g.querySelectorAll('.crow:not(.slot) .name > b')].map(b => b.textContent.trim()), g.querySelectorAll('.slotbtn').length]));
  ok('subject page: courses grouped by grade then term (+ empty-slot buttons)', JSON.stringify(grades) === JSON.stringify([
    ['الصف الأول الثانوي', ['كيمياء 1'], 1], ['الصف الثاني الثانوي', ['كيمياء 2-1', 'كيمياء 2-2'], 0], ['الصف الثالث الثانوي', ['كيمياء 3'], 1]]), JSON.stringify(grades));
  ok('subject page: preparing courses openable by the owner', (await p.locator('.crow:has(.badge.warn) [data-course]').count()) === 3);
  ok('subject page: three tabs', (await p.locator('.stabs [data-tab]').count()) === 3);
  await shot('subject-page-1280');

  // ---------- مبدّل السياق: يغيّر المقرر ويبقى في الصفحة ----------
  await p.goto(BASE + '#/bank'); await p.waitForSelector('#bank-count');
  await p.click('#ctx-btn'); await p.waitForSelector('#ctx-pop:not([hidden]) .sw-courses');
  ok('switcher: subjects column + courses grouped by grade', (await p.locator('#ctx-pop .sw-subj .it').count()) >= 2 && (await p.locator('#ctx-pop .sw-courses h6').count()) === 3);
  await shot('switcher-open-1280', false);
  await p.fill('#ctx-q', '2-2');
  ok('switcher: search filters courses', (await p.locator('#ctx-pop .sw-courses [data-pick]').count()) === 1);
  await p.locator('#ctx-pop .sw-courses [data-pick="3"]').click();
  await p.locator('#bank-count').first().waitFor();
  await p.waitForFunction(() => document.querySelector('#ctx-btn')?.textContent.includes('كيمياء 2-2'));
  ok('switcher: changes the course and stays on the same page', (await p.evaluate(() => location.hash)) === '#/bank'
    && (await p.locator('#brand-sub').innerText()).includes('كيمياء 2-2') && (await p.evaluate(() => localStorage.getItem('itqan-course'))) === '3');
  await p.waitForFunction(() => /^0/.test(document.querySelector('#bank-count')?.textContent.trim() || ''));
  ok('switcher: bank now shows the new course (2-2 is empty)', true);
  await p.click('#ctx-btn'); await p.waitForSelector('#ctx-pop:not([hidden])');
  ok('switcher: recent courses listed', (await p.locator('#ctx-pop .sw-foot [data-pick="1"]').count()) === 1);
  await p.locator('#ctx-pop .sw-foot [data-pick="1"]').click();
  await p.waitForFunction(() => document.querySelector('#ctx-btn')?.textContent.includes('كيمياء 2-1'));
  await p.goto(BASE + '#/objective/C1-L1-O14'); await p.waitForSelector('#mcq-list .q');
  await p.click('#ctx-btn'); await p.locator('#ctx-pop .sw-courses [data-pick="3"]').click();
  await p.waitForFunction(() => location.hash === '#/chapters');
  ok('switcher: on an item page of the old course it goes to that list in the new course', true);
  await p.click('#ctx-btn'); await p.locator('#ctx-pop .sw-courses [data-pick="1"]').click();
  await p.waitForFunction(() => document.querySelector('#ctx-btn')?.textContent.includes('كيمياء 2-1'));

  // ---------- إضافة مادة ----------
  await p.goto(BASE + '#/'); await p.waitForSelector('#sj-add');
  await p.click('#sj-add'); await p.waitForSelector('#sb-name');
  await p.fill('#sb-name', 'الفيزياء');
  ok('add subject: slug and icon suggested from the name', (await p.inputValue('#sb-id')) === 'phys' && (await p.locator('.ipick.on[data-icon="atom"]').count()) === 1);
  await p.click('[data-color="indigo"]');
  await shot('add-subject-1280', false);
  await p.click('#fl-next'); await p.waitForFunction(() => location.hash === '#/subject/phys'); await p.waitForSelector('.grade');
  const ps = (await pool.query(`select name, icon, color from public.subjects where id = 'phys'`)).rows[0];
  ok('add subject: created (name, icon, colour) and its page opens with empty slots', ps?.name === 'الفيزياء' && ps.icon === 'atom' && ps.color === 'indigo'
    && (await p.locator('.slotbtn').count()) === 6 && (await p.locator('.notice.info', { hasText: 'لا تظهر لأي معلم' }).count()) === 1, JSON.stringify(ps));

  // ---------- إضافة مقرر: 4 خطوات ----------
  await p.click('#sj-addc'); await p.waitForSelector('[data-grade]');
  ok('add course: opened from the subject page starts at step 2 (subject preselected)', (await p.locator('.steps li.done').count()) === 1 && (await p.locator('.steps li.on').innerText()).includes('الصف'));
  await p.click('[data-grade="الثاني الثانوي"]'); await p.click('[data-term="الأول"]');
  await shot('add-course-step2-1280', false);
  await p.click('#fl-next'); await p.waitForSelector('#cr-code');
  ok('add course: name suggested «فيزياء 2-1»', (await p.inputValue('#cr-code')) === 'فيزياء 2-1');
  await p.fill('#cr-src', 'الكتاب المدرسي — فيزياء 2-1');
  await p.click('#fl-next'); await p.waitForSelector('dl.review');
  ok('add course: review shows the preview card and next-steps checklist', (await p.locator('.pv-card', { hasText: 'فيزياء 2-1' }).count()) === 1 && (await p.locator('.checklist div').count()) === 4);
  await shot('add-course-step4-1280', false);
  await p.click('#fl-next'); await p.waitForSelector('.crow:not(.slot) .name >> text=فيزياء 2-1');
  const pc = (await pool.query(`select id, status, subject_id, subject, grade, term, content_source from public.courses where code = 'فيزياء 2-1'`)).rows[0];
  ok('add course: created «قيد الإعداد» in the physics subject', pc?.status === 'preparing' && pc.subject_id === 'phys' && pc.subject === 'الفيزياء' && pc.grade === 'الثاني الثانوي' && pc.term === 'الأول' && pc.id > 100, JSON.stringify(pc));
  await p.click('#sj-addc'); await p.waitForSelector('[data-grade]');
  await p.click('[data-grade="الثاني الثانوي"]');
  ok('add course: a taken grade/term slot is disabled', await p.locator('[data-term="الأول"]').isDisabled() && !(await p.locator('[data-term="الثاني"]').isDisabled()));
  await p.keyboard.press('Escape');
  const dup = await asRole(OWNER, `select public.admin_save_course('{"subjectId":"phys","grade":"الثاني الثانوي","term":"الأول","code":"فيزياء أخرى"}'::jsonb) r`);
  ok('add course: database refuses a duplicate grade/term slot', /يوجد مقرر/.test(dup.error?.message || ''), dup.error?.message);
  const bad = await asRole(OWNER, `select public.admin_save_subject('{"id":"Phys!","name":"x","icon":"atom","color":"teal"}'::jsonb) r`);
  ok('add subject: database validates the slug', bad.error?.code === '22023', bad.error?.message);

  // ---------- إسناد معلم للمادة ----------
  await p.click('.stabs [data-tab="teachers"]'); await p.click('#sj-assign'); await p.waitForSelector('#ta-t');
  await p.selectOption('#ta-t', VIEW); await p.click('#fl-next');
  await p.waitForSelector('[data-pane="teachers"] tr[data-teacher]');
  const tc = (await pool.query(`select count(*)::int n from public.teacher_courses t join public.courses c on c.id = t.course_id where t.teacher_id = $1 and c.subject_id = 'phys'`, [VIEW])).rows[0].n;
  ok('assign teacher by subject: expands into teacher_courses', tc === 1, String(tc));
  ok('assign teacher by subject: listed in the subject Teachers tab', (await p.locator('[data-pane="teachers"]').innerText()).includes('كل مقررات المادة'));
  const v1 = await asRole(VIEW, 'select public.get_courses() r'), v2 = await asRole(VIEW, 'select public.get_subjects() r');
  ok('preparing course invisible to its (assigned) teacher', !v1.data.some(c => c.subjectId === 'phys') && !v2.data.some(s => s.id === 'phys') && v2.data.some(s => s.id === 'chem'),
    JSON.stringify([v1.data.map(c => c.id), v2.data.map(s => s.id)]));
  const r1 = await asRole(REV, 'select public.get_courses() r'), r2 = await asRole(REV, 'select public.get_subjects() r');
  ok('new subject invisible to the rest of the team until it has a ready course', !r1.data.some(c => c.subjectId === 'phys') && !r2.data.some(s => s.id === 'phys'));

  // ---------- إسناد شعبة لمقرر ----------
  const stIds = [];
  for (let i = 1; i <= 3; i++) {
    const { rows: [u] } = await pool.query(`insert into auth.users (email) values ($1) returning id`, [`msub${i}@chem21.local`]);
    await pool.query(`update public.profiles set role = 'student', managed = true, profile_confirmed = true, grade = 'ثاني ثانوي', section = $2, display_name = $3 where user_id = $1`, [u.id, i < 3 ? 'م1' : 'م2', 'طالب مواد ' + i]);
    stIds.push(u.id);
  }
  await p.reload(); await p.waitForSelector('.stabs');
  await p.click('.stabs [data-tab="students"]'); await p.click('#sj-enroll'); await p.waitForSelector('#en-g');
  await p.selectOption('#en-g', 'ثاني ثانوي'); await p.selectOption('#en-s', 'م1');
  ok('enrol sections: filter by grade/section counts students', (await p.locator('#fl-body .notice').innerText()).includes('2'));
  await p.click('#fl-next'); await p.click('[data-subj="phys"]'); await p.click('#fl-next');
  await p.click(`#fl-body [data-course="${pc.id}"]`); await p.click('#fl-next'); await p.waitForSelector('[data-mode="add"]');
  await p.click('#fl-next'); await p.waitForSelector('.toast');
  const en = (await pool.query(`select count(*)::int n from public.course_enrollments where course_id = $1`, [pc.id])).rows[0].n;
  ok('enrol sections: section enrolled into the course (admin_enroll)', en === 2, String(en));
  const st = await asRole(stIds[0], 'select public.get_subjects() r'), sc = await asRole(stIds[0], 'select public.get_me() r');
  ok('preparing course invisible to an enrolled student', !st.data?.some(s => s.id === 'phys') && !sc.data?.courses?.some(c => c.id === pc.id), JSON.stringify([st.error?.message, st.data, sc.data?.courses]));

  // ---------- رفض دوال الإدارة لغير المالك ----------
  const calls = [`public.admin_save_subject('{"mode":"create","id":"bio","name":"الأحياء","icon":"leaf","color":"green"}'::jsonb)`,
    `public.admin_save_course('{"subjectId":"phys","grade":"الأول الثانوي","term":"الأول","code":"فيزياء 1"}'::jsonb)`,
    `public.admin_assign_teacher_subject('${VIEW}', 'phys', 'add')`, 'public.admin_list_teachers()', 'public.admin_platform_totals()'];
  const refused = [];
  for (const uid of [VIEW, REV, stIds[0]]) for (const c of calls) { const r = await asRole(uid, `select to_jsonb(${c}) r`); refused.push(r.error?.code === '42501'); }
  ok('admin RPCs refused for teacher, reviewer and student', refused.every(Boolean), JSON.stringify(refused));
  ok('nothing written by refused calls', (await pool.query(`select count(*)::int n from public.subjects where id = 'bio'`)).rows[0].n === 0);

  // ---------- المعلم: مبدّل بلا عمود المواد (كل مقرراته في مادة واحدة) ----------
  await login('view');
  await p.goto(BASE + '#/course'); await p.waitForSelector('#ctx-btn');
  await p.click('#ctx-btn'); await p.waitForSelector('#ctx-pop:not([hidden])');
  ok('switcher (teacher, one subject): no subjects column', (await p.locator('#ctx-pop .sw-subj').count()) === 0 && (await p.locator('#ctx-pop [data-pick]').count()) === 1);
  ok('teacher keeps the courses home (no «المواد»)', await p.goto(BASE + '#/').then(() => p.waitForSelector('.course-card')).then(() => true, () => false));

  // ---------- لقطات الهاتف والوضع الليلي ----------
  await login('owner');
  for (const [scheme, tag] of [['light', ''], ['dark', '-dark']]) {
    await p.emulateMedia({ colorScheme: scheme });
    for (const w of [1280, 390]) {
      await p.setViewportSize({ width: w, height: w === 390 ? 844 : 900 });
      await p.goto(BASE + '#/'); await p.waitForSelector('.scard'); if (w === 390 || tag) await shot(`owner-home-${w}${tag}`);
      await p.goto(BASE + '#/subject/chem'); await p.waitForSelector('.grade'); if (w === 390 || tag) await shot(`subject-page-${w}${tag}`);
      await p.click('#ctx-btn'); await p.waitForSelector('#ctx-pop:not([hidden])'); if (w === 390 || tag) await shot(`switcher-open-${w}${tag}`, false);
      await p.keyboard.press('Escape');
      await p.goto(BASE + '#/subject/phys'); await p.waitForSelector('.grade');
      await p.click('#sj-addc'); await p.waitForSelector('[data-grade]'); await p.click('[data-grade="الأول الثانوي"]'); await p.click('[data-term="الأول"]');
      if (w === 390 || tag) await shot(`add-course-step2-${w}${tag}`, false);
      await p.keyboard.press('Escape');
      await p.goto(BASE + '#/'); await p.waitForSelector('#sj-add'); await p.click('#sj-add'); await p.waitForSelector('#sb-name'); await p.fill('#sb-name', 'الأحياء');
      if (w === 390 || tag) await shot(`add-subject-${w}${tag}`, false);
      await p.keyboard.press('Escape');
    }
  }
  await p.emulateMedia({ colorScheme: 'light' }); await p.setViewportSize({ width: 1280, height: 900 });
  ok('phone/dark screenshots taken', true);
  // لا يبقى أفقي زائد في الهاتف
  await p.setViewportSize({ width: 390, height: 844 });
  await p.goto(BASE + '#/subject/chem'); await p.waitForSelector('.grade');
  ok('phone: no horizontal page scroll on the subject page', await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
  await p.setViewportSize({ width: 1280, height: 900 });
  await cleanup();
}
