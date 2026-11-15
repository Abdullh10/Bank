// تعدد المواد: رئيسية مالك المشروع («المواد»)، وصفحة المادة، ومبدّل السياق في الترويسة، وخطوات إضافة مادة ومقرر
// وإسناد المعلمين والشعب. الهرمية: المادة ← الصف ← الفصل الدراسي ← المقرر.
// المادة مشتقة دائمًا من «المقرر الحالي» (لا حالة عامة ثانية)، ولونها لون مميز فقط (شريط وأيقونة وشارة) لا يعيد تلوين الواجهة.
import { icon, line } from './icons.js';

// القوائم نفسها في admin_save_subject بقاعدة البيانات
export const SUBJECT_ICONS = [['flask', 'دورق'], ['atom', 'ذرة'], ['leaf', 'ورقة نبات'], ['sigma', 'رياضيات'], ['globe', 'كرة أرضية'], ['book', 'كتاب'], ['dna', 'حمض نووي'], ['calc', 'آلة حاسبة']];
export const SUBJECT_COLORS = [['teal', 'فيروزي'], ['indigo', 'نيلي'], ['green', 'أخضر'], ['amber', 'كهرماني'], ['rose', 'وردي'], ['violet', 'بنفسجي']];
export const GRADES = ['الأول الثانوي', 'الثاني الثانوي', 'الثالث الثانوي'];
export const TERMS = ['الأول', 'الثاني', 'الثالث'];
// رموز مقترحة لأسماء المواد الشائعة (يكتبها المالك إن لم يُقترح شيء)
const SLUGS = { 'الفيزياء': 'phys', 'الأحياء': 'bio', 'الرياضيات': 'math', 'العلوم': 'sci', 'علم البيئة': 'env', 'علوم الأرض والفضاء': 'earth',
  'اللغة الإنجليزية': 'eng', 'اللغة العربية': 'arb', 'الحاسب': 'cs', 'التقنية الرقمية': 'tech', 'الكيمياء': 'chem' };
const ICON_GUESS = { 'الفيزياء': 'atom', 'الأحياء': 'leaf', 'الرياضيات': 'sigma', 'علوم الأرض والفضاء': 'globe', 'علم البيئة': 'leaf', 'الكيمياء': 'flask' };

const num = n => Number(n || 0).toLocaleString('ar-SA-u-nu-latn');
const pct = (a, b) => (b ? Math.round((100 * (a || 0)) / b) : 0);
const escA = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const plural = (n, one, two, few, many) => (n === 1 ? one : n === 2 ? two : n >= 3 && n <= 10 ? `${num(n)} ${few}` : `${num(n)} ${many}`);
const nCourses = n => (n === 0 ? 'لا مقررات بعد' : plural(n, 'مقرر واحد', 'مقرران', 'مقررات', 'مقررًا'));
const nTeachers = n => (n === 0 ? 'لا معلمين' : plural(n, 'معلم واحد', 'معلمان', 'معلمين', 'معلمًا'));
const shortName = name => String(name || '').replace(/^ال(?=\S{3,})/, '');
const gradeNo = g => GRADES.indexOf(g) + 1;
export const suggestCode = (subject, grade, term) => (subject && grade && term ? `${shortName(subject.name)} ${gradeNo(grade)}-${TERMS.indexOf(term) + 1}` : '');

/** بلاطة المادة: أيقونتها البيضاء على لونها */
export const sIcon = (s, size = '') => `<span class="sicon ${size} s-${escA(s?.color || 'teal')}" aria-hidden="true">${line(s?.icon || 'book', size === 'sm' ? 15 : size === 'lg' ? 32 : 24)}</span>`;
export const subjectOf = (c, subjects) => (c?.subjectId && subjects?.find(s => s.id === c.subjectId)) || null;
// خطأ قراءة اختيارية يُهمل (تُعرض الصفحة دونها)، إلا الانتقال إلى صفحة أخرى فيوقف الرسم
const soft = v => e => { if (e?.stale) throw e; return v; };
const statusBadge = c => (c.status === 'ready' ? `<span class="badge ok">${line('check', 13)} متاح</span>` : `<span class="badge warn">${line('clock', 13)} قيد الإعداد</span>`);

// ---------- آخر المقررات المفتوحة (لهذا الجهاز؛ مفتاح جديد لا يغيّر مفتاح المقرر المختار) ----------
const RECENT = 'itqan-recent-courses';
export function pushRecent(id) {
  try {
    const a = [id, ...JSON.parse(localStorage.getItem(RECENT) || '[]').filter(x => x !== id)].slice(0, 4);
    localStorage.setItem(RECENT, JSON.stringify(a));
  } catch { /* التخزين غير متاح */ }
}
const recents = () => { try { return JSON.parse(localStorage.getItem(RECENT) || '[]'); } catch { return []; } };

// =====================================================================
// رئيسية مالك المشروع: المواد
// =====================================================================
export async function pageSubjects(ctx) {
  const { esc, $app, state, api, select } = ctx;
  const subjects = state.subjects || [], courses = state.courses || [], cur = state.course;
  const totals = await api('/admin/totals').catch(soft(null));
  const programs = courses.filter(c => c.kind === 'tahsili');
  const sum = k => subjects.reduce((a, s) => a + (s[k] || 0), 0);
  const subjCourses = courses.filter(c => c.subjectId);
  const ready = subjects.filter(s => s.ready > 0).length, q = sum('questions'), ap = sum('approved');
  const gradesOf = s => {
    const gs = [...new Set(courses.filter(c => c.subjectId === s.id).map(c => c.grade))];
    return gs.length === 3 ? 'الصفوف الثلاثة' : gs.length ? gs.map(g => 'الصف ' + g).join('، ') : '';
  };
  const card = s => {
    const empty = !s.courses;
    const status = s.ready ? `<span class="badge ok">${line('check', 13)} ${num(s.ready)} ${s.ready === 1 ? 'متاح' : 'متاحة'}</span>`
      : empty ? '<span class="badge brand">جديدة</span>' : `<span class="badge warn">${line('clock', 13)} قيد الإعداد</span>`;
    return `<article class="scard s-${escA(s.color)}" data-subject="${escA(s.id)}">
      <div class="sh">${sIcon(s)}<div><h2>${esc(s.name)}</h2><p>${empty ? 'أُضيفت حديثًا' : `${nCourses(s.courses)}${gradesOf(s) ? ' · ' + gradesOf(s) : ''}`}</p></div></div>
      ${empty ? '<p class="empty-note">لا مقررات بعد. لا تظهر المادة لأي معلم أو طالب حتى يُتاح أول مقرر فيها.</p>'
        : `<dl><div><dt>أسئلة</dt><dd>${num(s.questions)}</dd></div><div><dt>طلاب</dt><dd>${num(s.students)}</dd></div><div><dt>معلمون</dt><dd>${num(s.teachers)}</dd></div></dl>
        <div class="prog"><div class="row"><span>الأسئلة المعتمدة</span><b>${pct(s.approved, s.questions)}%</b></div><div class="bar sbar"><span style="width:${pct(s.approved, s.questions)}%"></span></div></div>`}
      <div class="foot">${status}${empty ? `<button type="button" class="primary" data-add-course="${escA(s.id)}">${line('plus', 16)}إضافة مقرر</button>`
        : `<a class="btn ${s.ready ? 'primary' : ''}" href="#/subject/${encodeURIComponent(s.id)}">فتح المادة</a>`}</div>
    </article>`;
  };
  $app.innerHTML = `
    <div class="page-head">
      <div><h1>المواد</h1><p class="muted">اختر المادة لإدارة مقرراتها، أو أكمل من حيث توقفت.</p></div>
      <div class="actions no-print">${cur ? `<button type="button" id="sj-resume" data-course="${cur.id}">${line('next', 16)}متابعة ${esc(cur.code)}</button>` : ''}
        <button type="button" class="primary" id="sj-add">${line('plus', 16)}إضافة مادة</button></div>
    </div>
    <div class="totals">
      <div class="total"><b>${num(subjects.length)}</b><span>${subjects.length === 1 ? 'مادة' : 'مواد'} (${num(ready)} ${ready === 1 ? 'جاهزة' : 'جاهزة'})</span></div>
      <div class="total"><b>${num(subjCourses.length + programs.length)}</b><span>مقررات (${num(courses.filter(c => c.status === 'ready').length)} متاحة للطلاب)</span></div>
      <div class="total"><b>${num(q)}</b><span>سؤالًا · ${pct(ap, q)}% معتمدة</span></div>
      <div class="total"><b>${num(totals?.students ?? sum('students'))}</b><span>طالبًا · ${nTeachers(totals?.teachers ?? sum('teachers'))}</span></div>
    </div>
    <div class="subjects">${subjects.map(card).join('')}
      <button type="button" class="scard add" id="sj-add2"><span class="plus">${line('plus', 22)}</span><b>إضافة مادة</b><span class="small">الفيزياء، الأحياء… اسم ولون وأيقونة، ثم مقرراتها</span></button>
    </div>
    ${programs.length ? `<div class="section-sub"><h2>برامج مشتركة بين المواد</h2><span>ليست تحت مادة واحدة</span></div>
      ${programs.map(c => `<div class="program"><span class="dots" aria-hidden="true"><i class="s-green"></i><i class="s-teal"></i><i class="s-indigo"></i><i class="s-amber"></i></span>
        <div class="grow"><h3>${esc(c.title || c.code)}</h3><p>الأحياء والكيمياء والفيزياء والرياضيات · 25% لكل مادة</p></div>
        ${statusBadge(c)}<button type="button" data-course="${c.id}">${c.status === 'ready' ? 'دخول' : 'متابعة الإعداد'}</button></div>`).join('')}` : ''}`;
  $app.querySelectorAll('[data-course]').forEach(b => b.onclick = () => select(Number(b.dataset.course), true));
  $app.querySelectorAll('#sj-add, #sj-add2').forEach(b => b.onclick = () => subjectDialog(ctx));
  $app.querySelectorAll('[data-add-course]').forEach(b => b.onclick = () => courseDialog(ctx, { subjectId: b.dataset.addCourse }));
}

// =====================================================================
// صفحة المادة: مقرراتها حسب الصف والفصل، ومعلموها، وطلابها وشعبها
// =====================================================================
const subjTab = { tab: 'courses' };
export async function pageSubject(ctx, id) {
  const { esc, $app, state, api, fail, select } = ctx;
  const s = state.subjects?.find(x => x.id === id);
  if (!s) { $app.innerHTML = '<div class="empty">المادة غير موجودة.</div>'; return; }
  const list = (state.courses || []).filter(c => c.subjectId === id);
  const ids = new Set(list.map(c => c.id));
  const teachers = await api('/admin/teachers').catch(soft([]));
  const subjTeachers = teachers.filter(t => t.courses.some(c => ids.has(c)));
  // قائمة الطلاب أثقل: تُقرأ عند فتح تبويب «الطلاب والشعب» أو خطوات الإسناد فقط
  let students = null;
  const loadStudents = async () => (students ||= await api('/admin/students'));
  if (subjTab.id !== id) Object.assign(subjTab, { id, tab: 'courses' });
  const cur = state.course;
  const row = c => `<div class="crow ${cur?.id === c.id ? 'cur' : ''}" data-row="${c.id}">
      <div class="term"><b>الفصل ${esc(c.term)}</b></div>
      <div class="name"><b>${esc(c.code)}</b>${statusBadge(c)}${cur?.id === c.id ? '<span class="badge brand">الحالي</span>' : ''}</div>
      <div class="qs"><span><b class="num">${num(c.questions)}</b> سؤالًا · ${pct(c.approved, c.questions)}% معتمدة</span><div class="bar sbar"><span style="width:${pct(c.approved, c.questions)}%"></span></div></div>
      <div class="stat st1"><b class="num">${num(c.students)}</b>طلاب</div><div class="stat st2"><b class="num">${num(c.teachers)}</b>معلمون</div>
      <button type="button" class="go ${cur?.id === c.id ? 'primary' : ''}" data-course="${c.id}">دخول</button></div>`;
  const slot = (g, t) => `<div class="crow slot"><div class="term"><b>الفصل ${t}</b></div>
      <button type="button" class="slotbtn" data-slot="${escA(g)}|${t}">${line('plus', 15)}إضافة مقرر (مثل ${esc(suggestCode(s, g, t))})</button></div>`;
  const grades = GRADES.map(g => {
    const cs = list.filter(c => c.grade === g);
    const terms = [...new Set(['الأول', 'الثاني', ...cs.map(c => c.term)])].sort((a, b) => TERMS.indexOf(a) - TERMS.indexOf(b));
    return `<section class="grade"><header><h3>الصف ${esc(g)}</h3><span>${cs.length ? `${num(cs.reduce((a, c) => a + (c.students || 0), 0))} طالبًا` : 'لا مقررات'}</span></header>
      ${terms.map(t => { const c = cs.find(x => x.term === t); return c ? row(c) : slot(g, t); }).join('')}</section>`;
  }).join('');
  const courseName = cid => list.find(c => c.id === cid)?.code || '';
  const teachersTab = `<div class="tab-head"><p class="muted small">المعلم يرى المقررات <b>المتاحة</b> المسندة له فقط؛ المقرر «قيد الإعداد» لا يظهر له حتى يُتاح.</p>
      <button type="button" class="primary" id="sj-assign">${line('plus', 16)}إسناد معلم</button></div>
    ${subjTeachers.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>المعلم</th><th>مقررات المادة المسندة</th><th></th></tr></thead><tbody>
      ${subjTeachers.map(t => { const mine = t.courses.filter(c => ids.has(c)); return `<tr data-teacher="${escA(t.id)}"><td><b>${esc(t.name)}</b><div class="small muted ltr">${esc(t.username)}</div></td>
        <td>${mine.length === list.length ? '<span class="badge brand">كل مقررات المادة</span> ' : ''}${mine.map(c => `<span class="badge">${esc(courseName(c))}</span>`).join(' ')}</td>
        <td class="actions as-acts"><button type="button" data-tedit="${escA(t.id)}">تعديل</button><button type="button" class="danger" data-tremove="${escA(t.id)}">إلغاء الإسناد</button></td></tr>`; }).join('')}
      </tbody></table></div>` : `<div class="empty"><h3>لا معلمين مسندين لهذه المادة بعد</h3><p>أسند معلمًا لكل مقررات المادة بضغطة واحدة، أو لمقررات محددة.</p></div>`}`;
  const secRows = enrolled => list.map(c => {
    const st = enrolled.filter(x => x.courses.includes(c.id));
    const bySec = {};
    st.forEach(x => { const k = [x.grade, x.section].filter(Boolean).join(' · ') || 'بلا شعبة'; bySec[k] = (bySec[k] || 0) + 1; });
    return `<tr><td><b>${esc(c.code)}</b> ${statusBadge(c)}</td><td>${Object.entries(bySec).sort().map(([k, n]) => `<span class="badge">${esc(k)} <b>${num(n)}</b></span>`).join(' ') || '<span class="muted small">لا طلاب مسندون</span>'}</td><td class="num">${num(st.length)}</td></tr>`;
  }).join('');
  const studentsTab = `<div class="tab-head"><p class="muted small">الطالب يتدرب على مقرراته المسندة <b>المتاحة</b> فقط. أسند الشعبة كاملة للمقرر بخطوات قصيرة.</p>
      <button type="button" class="primary" id="sj-enroll">${line('plus', 16)}إسناد شعبة لمقرر</button></div>
    <div id="sj-st">${list.length ? '<p class="muted small">جارٍ التحميل…</p>' : '<div class="empty"><h3>لا مقررات في المادة بعد</h3><p>أضف مقررًا أولًا ثم أسند له الشعب.</p></div>'}</div>`;
  const fillStudents = async () => {
    if (!list.length || students) return;
    try {
      const all = await loadStudents();
      const enrolled = all.filter(x => x.role === 'student' && (x.courses || []).some(c => ids.has(c)));
      const el = document.getElementById('sj-st');
      if (el) el.innerHTML = `<div class="table-wrap"><table class="list"><thead><tr><th>المقرر</th><th>الشعب (عدد الطلاب)</th><th>المجموع</th></tr></thead><tbody>${secRows(enrolled)}</tbody></table></div>`;
    } catch (e) { if (!e?.stale) fail(e); }
  };
  const tabs = [['courses', 'المقررات', list.length], ['teachers', 'المعلمون', subjTeachers.length], ['students', 'الطلاب والشعب', s.students]];
  $app.innerHTML = `
    <div class="crumbs"><a href="#/">المواد</a> ‹ ${esc(s.name)}</div>
    <div class="subj-hero s-${escA(s.color)}"><div class="l">${sIcon(s, 'lg')}<div><h1>${esc(s.name)}</h1>
      <p>${nCourses(list.length)} · ${num(s.questions)} سؤالًا · ${num(s.students)} طالبًا · ${nTeachers(s.teachers)}</p></div></div>
      <div class="actions no-print"><button type="button" id="sj-edit">إعدادات المادة</button><button type="button" class="primary" id="sj-addc">${line('plus', 16)}إضافة مقرر</button></div></div>
    ${s.ready ? '' : '<p class="notice info">هذه المادة لا تظهر لأي معلم أو طالب حتى يُتاح أول مقرر فيها.</p>'}
    <div class="stabs s-${escA(s.color)}" role="tablist">${tabs.map(([k, t, n]) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${subjTab.tab === k}" class="${subjTab.tab === k ? 'on' : ''}">${t}<span class="c">${num(n)}</span></button>`).join('')}</div>
    <div class="tabpane" data-pane="courses" ${subjTab.tab === 'courses' ? '' : 'hidden'}>${grades}</div>
    <div class="tabpane" data-pane="teachers" ${subjTab.tab === 'teachers' ? '' : 'hidden'}>${teachersTab}</div>
    <div class="tabpane" data-pane="students" ${subjTab.tab === 'students' ? '' : 'hidden'}>${studentsTab}</div>`;
  $app.querySelectorAll('[data-tab]').forEach(b => b.onclick = () => {
    subjTab.tab = b.dataset.tab;
    $app.querySelectorAll('[data-tab]').forEach(x => { x.classList.toggle('on', x === b); x.setAttribute('aria-selected', String(x === b)); });
    $app.querySelectorAll('[data-pane]').forEach(p => { p.hidden = p.dataset.pane !== subjTab.tab; });
    if (subjTab.tab === 'students') fillStudents();
  });
  if (subjTab.tab === 'students') fillStudents();
  $app.querySelectorAll('[data-course]').forEach(b => b.onclick = () => select(Number(b.dataset.course), true));
  $app.querySelectorAll('[data-slot]').forEach(b => b.onclick = () => { const [grade, term] = b.dataset.slot.split('|'); courseDialog(ctx, { subjectId: id, grade, term }); });
  document.getElementById('sj-addc').onclick = () => courseDialog(ctx, { subjectId: id });
  document.getElementById('sj-edit').onclick = () => subjectDialog(ctx, s);
  document.getElementById('sj-assign').onclick = () => teacherDialog(ctx, s, teachers, list);
  document.getElementById('sj-enroll').onclick = async e => {
    const b = e.currentTarget; b.disabled = true;
    try { enrollDialog(ctx, { subjectId: id, students: await loadStudents() }); } catch (err) { if (!err?.stale) fail(err); } finally { b.disabled = false; }
  };
  $app.querySelectorAll('[data-tedit]').forEach(b => b.onclick = () => teacherDialog(ctx, s, teachers, list, b.dataset.tedit));
  $app.querySelectorAll('[data-tremove]').forEach(b => b.onclick = async () => {
    const t = teachers.find(x => x.id === b.dataset.tremove);
    if (!confirm(`إلغاء إسناد كل مقررات ${s.name} للمعلم «${t?.name}»؟`)) return;
    b.disabled = true;
    try { await api('/admin/subjects/teacher', { method: 'POST', body: { teacher: t.id, subject: id, mode: 'remove' } }); ctx.toast('أُلغي الإسناد'); await ctx.refresh(); }
    catch (e) { fail(e); b.disabled = false; }
  });
}

// =====================================================================
// النوافذ: هيكل مشترك بخطوات قصيرة ومعاينة جانبية
// =====================================================================
function flowDialog({ title, steps, aside = true }) {
  const $dlg = document.getElementById('dlg');
  $dlg.className = 'flow-dlg';
  $dlg.innerHTML = `<div class="dlg-head"><h2>${title}</h2><button type="button" data-close aria-label="إغلاق">${line('close', 18)}</button></div>
    ${steps ? `<ol class="steps">${steps.map((t, i) => `<li data-step="${i}"><i>${i + 1}</i><span>${t}</span></li>`).join('')}</ol>` : ''}
    <div class="flow ${aside ? '' : 'noaside'}"><div class="step-body" id="fl-body"></div>${aside ? '<aside class="preview" id="fl-aside"></aside>' : ''}</div>
    <div class="dlg-foot"><button type="button" id="fl-prev">${line('prev', 16)}السابق</button><span class="grow"></span><button type="button" data-close>إلغاء</button><button type="button" class="primary" id="fl-next">التالي${line('next', 16)}</button></div>`;
  $dlg.querySelectorAll('[data-close]').forEach(b => b.onclick = () => $dlg.close());
  $dlg.addEventListener('close', () => { $dlg.className = ''; }, { once: true });
  if (!$dlg.open) $dlg.showModal();
  return $dlg;
}
const setSteps = (d, at) => d.querySelectorAll('.steps li').forEach((li, i) => { li.className = i < at ? 'done' : i === at ? 'on' : ''; li.querySelector('i').innerHTML = i < at ? line('check', 14) : String(i + 1); });
const chips = (name, items, sel, disabled = () => false) => `<div class="chips" role="radiogroup">${items.map(([v, t, small]) => `<button type="button" class="chip ${v === sel ? 'on' : ''}" role="radio" aria-checked="${v === sel}"
  data-${name}="${escA(v)}" ${disabled(v) ? 'disabled' : ''}>${t}${small ? `<small>${small}</small>` : ''}</button>`).join('')}</div>`;

// ---------- إضافة مادة / إعداداتها ----------
export function subjectDialog(ctx, edit = null) {
  const { esc, api, fail, toast } = ctx;
  const v = edit ? { id: edit.id, name: edit.name, icon: edit.icon || 'book', color: edit.color || 'teal', sort: edit.sort ?? 100, slugTouched: true }
    : { id: '', name: '', icon: 'book', color: SUBJECT_COLORS[(ctx.state.subjects?.length || 0) % SUBJECT_COLORS.length][0], sort: ((ctx.state.subjects?.length || 0) + 1) * 10 + 10, slugTouched: false };
  const d = flowDialog({ title: edit ? `إعدادات المادة: ${esc(edit.name)}` : 'إضافة مادة' });
  d.querySelector('#fl-prev').hidden = true;
  const body = d.querySelector('#fl-body'), aside = d.querySelector('#fl-aside'), next = d.querySelector('#fl-next');
  next.innerHTML = edit ? 'حفظ' : `${line('plus', 16)}إنشاء المادة`;
  body.innerHTML = `
    <div class="fq two"><div><label for="sb-name">اسم المادة</label><input id="sb-name" maxlength="40" placeholder="مثال: الفيزياء" value="${escA(v.name)}"></div>
      <div><label for="sb-id">الرمز (بالإنجليزية)</label><input id="sb-id" class="ltr" maxlength="31" placeholder="phys" value="${escA(v.id)}" ${edit ? 'disabled' : ''} autocapitalize="none" spellcheck="false">
      <span class="hint">${edit ? 'لا يتغير الرمز بعد الإنشاء.' : 'حروف إنجليزية صغيرة، يُستعمل داخليًا فقط.'}</span></div></div>
    <div class="fq"><label>الأيقونة</label><div class="icon-pick" role="radiogroup">${SUBJECT_ICONS.map(([k, t]) => `<button type="button" class="ipick" data-icon="${k}" role="radio" aria-label="${t}" title="${t}">${line(k, 22)}</button>`).join('')}</div></div>
    <div class="fq"><label>اللون</label><div class="swatches" role="radiogroup">${SUBJECT_COLORS.map(([k, t]) => `<button type="button" class="swatch s-${k}" data-color="${k}" role="radio" aria-label="${t}" title="${t}"></button>`).join('')}</div>
      <span class="hint">لون مميز للمادة فقط (شريط البطاقة وأيقونتها وشارتها)؛ لا تتغير ألوان المنصة.</span></div>
    <div class="fq"><label for="sb-sort">الترتيب في صفحة المواد</label><input id="sb-sort" type="number" min="0" max="999" value="${escA(v.sort)}" class="narrow"></div>`;
  const draw = () => {
    body.querySelectorAll('[data-icon]').forEach(b => { const on = b.dataset.icon === v.icon; b.classList.toggle('on', on); b.setAttribute('aria-checked', String(on)); });
    body.querySelectorAll('[data-color]').forEach(b => { const on = b.dataset.color === v.color; b.classList.toggle('on', on); b.setAttribute('aria-checked', String(on)); });
    body.querySelectorAll('.ipick').forEach(b => { b.className = `ipick s-${v.color}${b.dataset.icon === v.icon ? ' on' : ''}`; });
    aside.innerHTML = `<span class="cap">هكذا ستظهر في صفحة المواد</span>
      <div class="pv-card s-${v.color}"><div class="sh">${sIcon(v)}<div><b>${esc(v.name || 'اسم المادة')}</b><span class="meta">${edit ? nCourses(edit.courses) : 'أُضيفت حديثًا'}</span></div></div>
        <span class="badge ${edit?.ready ? 'ok' : 'brand'}">${edit?.ready ? 'متاحة' : 'جديدة'}</span></div>
      <div class="checklist"><b>بعد الإنشاء</b><div>أضف مقررات المادة (الصف والفصل)</div><div>أسند المعلمين والشعب</div><div>لا يراها أحد غيرك حتى يُتاح أول مقرر فيها</div></div>`;
  };
  body.querySelector('#sb-name').oninput = e => {
    v.name = e.target.value;
    const k = e.target.value.trim();
    if (!edit && !v.slugTouched) { body.querySelector('#sb-id').value = v.id = SLUGS[k] || ''; }
    if (!edit && ICON_GUESS[k] && !v.iconTouched) v.icon = ICON_GUESS[k];
    draw();
  };
  body.querySelector('#sb-id').oninput = e => { v.id = e.target.value.trim().toLowerCase(); v.slugTouched = true; };
  body.querySelectorAll('[data-icon]').forEach(b => b.onclick = () => { v.icon = b.dataset.icon; v.iconTouched = true; draw(); });
  body.querySelectorAll('[data-color]').forEach(b => b.onclick = () => { v.color = b.dataset.color; draw(); });
  next.onclick = async () => {
    const p = { mode: edit ? 'update' : 'create', id: v.id || body.querySelector('#sb-id').value.trim().toLowerCase(), name: body.querySelector('#sb-name').value.trim(),
      icon: v.icon, color: v.color, sort: Number(body.querySelector('#sb-sort').value) || 0 };
    if (p.name.length < 2) return toast('اكتب اسم المادة', true);
    if (!/^[a-z][a-z0-9-]{1,30}$/.test(p.id)) return toast('الرمز: حروف إنجليزية صغيرة (مثل phys)', true);
    next.disabled = true;
    try {
      await api('/admin/subjects/save', { method: 'POST', body: p });
      d.close(); toast(edit ? 'حُفظت إعدادات المادة' : `أُنشئت مادة ${p.name}`);
      await ctx.refresh(edit ? null : '#/subject/' + p.id);
    } catch (e) { fail(e); next.disabled = false; }
  };
  draw();
  body.querySelector('#sb-name').focus();
}

// ---------- إضافة مقرر: 4 خطوات ----------
export function courseDialog(ctx, pre = {}) {
  const { esc, api, fail, toast, state } = ctx;
  const subjects = state.subjects || [];
  const v = { subjectId: pre.subjectId || subjects[0]?.id || '', grade: pre.grade || '', term: pre.term || '', code: '', codeTouched: false, src: '' };
  let at = pre.subjectId ? 1 : 0;
  const subj = () => subjects.find(s => s.id === v.subjectId);
  const taken = (g, t) => (state.courses || []).some(c => c.subjectId === v.subjectId && c.grade === g && c.term === t);
  const d = flowDialog({ title: 'إضافة مقرر', steps: ['المادة', 'الصف والفصل', 'الاسم والمصدر', 'المراجعة والحفظ'] });
  const body = d.querySelector('#fl-body'), aside = d.querySelector('#fl-aside'), next = d.querySelector('#fl-next'), prev = d.querySelector('#fl-prev');
  const sync = () => { if (!v.codeTouched) v.code = suggestCode(subj(), v.grade, v.term); };
  const preview = () => {
    const s = subj();
    aside.innerHTML = `<span class="cap">${s ? `هكذا سيظهر في صفحة ${esc(s.name)}` : 'المعاينة'}</span>
      <div class="pv-card s-${escA(s?.color || 'teal')}"><div class="sh">${sIcon(s)}<div><b>${esc(v.code || 'اسم المقرر')}</b>
        <span class="meta">${v.grade ? esc(v.grade) : 'الصف —'} · ${v.term ? 'الفصل ' + esc(v.term) : 'الفصل —'}</span></div></div>
        <span class="badge warn">${line('clock', 13)} قيد الإعداد</span></div>
      <div class="checklist"><b>الخطوات التالية بعد الحفظ</b><div>رفع ملف الأهداف وبناء الفصول والدروس</div><div>إسناد المعلمين (دفعة لكل معلمي المادة)</div><div>إسناد الشعب للمقرر</div><div>«إتاحة» المقرر للطلاب عند اكتماله</div></div>`;
  };
  const draw = () => {
    setSteps(d, at);
    prev.hidden = at === 0;
    next.innerHTML = at === 3 ? `${line('check', 16)}حفظ المقرر (قيد الإعداد)` : `التالي${line('next', 16)}`;
    const s = subj();
    if (at === 0) {
      body.innerHTML = `<div class="fq"><label>المادة</label><span class="hint">المقرر الجديد يُضاف تحت هذه المادة.</span>
        ${subjects.length ? `<div class="chips">${subjects.map(x => `<button type="button" class="chip subj-chip ${x.id === v.subjectId ? 'on' : ''}" data-subj="${escA(x.id)}" role="radio" aria-checked="${x.id === v.subjectId}">${sIcon(x, 'sm')}${esc(x.name)}</button>`).join('')}</div>`
          : '<p class="notice">أضف مادة أولًا.</p>'}</div>`;
      body.querySelectorAll('[data-subj]').forEach(b => b.onclick = () => { v.subjectId = b.dataset.subj; if (v.grade && v.term && taken(v.grade, v.term)) v.term = ''; sync(); draw(); });
    } else if (at === 1) {
      const gHas = g => (state.courses || []).filter(c => c.subjectId === v.subjectId && c.grade === g).map(c => c.code);
      body.innerHTML = `<div class="fq"><label>الصف</label>${chips('grade', GRADES.map(g => [g, g, gHas(g).length ? `(فيه ${gHas(g).join('، ')})` : '']), v.grade)}</div>
        <div class="fq"><label>الفصل الدراسي</label><span class="hint">الفصل الذي له مقرر في هذا الصف يظهر معطّلًا، فلا يتكرر المقرر.</span>
          ${chips('term', TERMS.map(t => [t, `الفصل ${t}`, t === 'الثالث' ? '(نظام 3 فصول)' : '']), v.term, t => !v.grade || taken(v.grade, t))}</div>
        ${v.grade && v.term ? `<p class="small muted">في الخطوة التالية يُقترح الاسم <b>${esc(suggestCode(s, v.grade, v.term))}</b> ويمكن تعديله.</p>` : ''}`;
      body.querySelectorAll('[data-grade]').forEach(b => b.onclick = () => { v.grade = b.dataset.grade; if (v.term && taken(v.grade, v.term)) v.term = ''; sync(); draw(); });
      body.querySelectorAll('[data-term]').forEach(b => b.onclick = () => { v.term = b.dataset.term; sync(); draw(); });
    } else if (at === 2) {
      body.innerHTML = `<div class="fq"><label for="cr-code">اسم المقرر</label><span class="hint">يظهر في المبدّل والبطاقات وأوراق الاختبار.</span>
          <div class="input-auto"><input id="cr-code" maxlength="40" value="${escA(v.code)}">${v.codeTouched ? '' : '<span class="auto">مقترح</span>'}</div></div>
        <div class="fq"><label for="cr-src">مصدر المحتوى <span class="small muted">(اختياري)</span></label>
          <textarea id="cr-src" rows="2" maxlength="300" placeholder="مثال: الكتاب المدرسي — ${escA(v.code || 'فيزياء 2-1')}، الصف ${escA(v.grade)}، الفصل الدراسي ${escA(v.term)}">${escA(v.src)}</textarea></div>`;
      body.querySelector('#cr-code').oninput = e => { v.code = e.target.value; v.codeTouched = true; body.querySelector('.auto')?.remove(); preview(); };
      body.querySelector('#cr-src').oninput = e => { v.src = e.target.value; };
    } else {
      body.innerHTML = `<dl class="review">
          <div><dt>المادة</dt><dd>${sIcon(s, 'sm')} ${esc(s?.name)}</dd></div><div><dt>الصف</dt><dd>${esc(v.grade)}</dd></div>
          <div><dt>الفصل الدراسي</dt><dd>${esc(v.term)}</dd></div><div><dt>الاسم</dt><dd><b>${esc(v.code)}</b></dd></div>
          <div><dt>مصدر المحتوى</dt><dd>${esc(v.src || '—')}</dd></div><div><dt>الحالة</dt><dd><span class="badge warn">${line('clock', 13)} قيد الإعداد</span></dd></div></dl>
        <p class="notice info">يُنشأ المقرر «قيد الإعداد»: يراه مالك المشروع فقط، ولا يظهر لأي معلم أو طالب حتى يُتاح.</p>`;
    }
    preview();
  };
  prev.onclick = () => { at = Math.max(0, at - 1); draw(); };
  next.onclick = async () => {
    if (at === 0 && !v.subjectId) return toast('اختر المادة', true);
    if (at === 1 && (!v.grade || !v.term)) return toast('اختر الصف والفصل الدراسي', true);
    if (at === 2 && v.code.trim().length < 2) return toast('اكتب اسم المقرر', true);
    if (at < 3) { at++; return draw(); }
    next.disabled = true;
    try {
      const r = await api('/admin/courses/save', { method: 'POST', body: { subjectId: v.subjectId, grade: v.grade, term: v.term, code: v.code.trim(), contentSource: v.src.trim() } });
      d.close(); toast(`أُضيف ${r.code} (قيد الإعداد)`);
      await ctx.refresh('#/subject/' + v.subjectId);
    } catch (e) { fail(e); next.disabled = false; }
  };
  sync(); draw();
}

// ---------- إسناد معلم للمادة: كل مقرراتها أو مقررات محددة ----------
function teacherDialog(ctx, s, teachers, list, teacherId = '') {
  const { esc, api, fail, toast } = ctx;
  const ids = new Set(list.map(c => c.id));
  const v = { teacher: teacherId, mode: 'all', picked: new Set() };
  const d = flowDialog({ title: `إسناد معلم: ${esc(s.name)}`, aside: false });
  const body = d.querySelector('#fl-body'), next = d.querySelector('#fl-next');
  d.querySelector('#fl-prev').hidden = true;
  next.innerHTML = `${line('check', 16)}حفظ الإسناد`;
  const loadPicked = () => { const t = teachers.find(x => x.id === v.teacher); v.picked = new Set((t?.courses || []).filter(c => ids.has(c))); v.mode = !t || v.picked.size === list.length || !v.picked.size ? 'all' : 'some'; };
  const draw = () => {
    body.innerHTML = teachers.length ? `<div class="fq"><label for="ta-t">المعلم</label><select id="ta-t"><option value="">اختر المعلم…</option>${teachers.map(t => `<option value="${escA(t.id)}" ${t.id === v.teacher ? 'selected' : ''}>${esc(t.name)} (${esc(t.username)})</option>`).join('')}</select></div>
      <div class="fq"><label>المقررات</label>${chips('tmode', [['all', `كل مقررات ${esc(s.name)}`, `(${num(list.length)})`], ['some', 'مقررات محددة']], v.mode)}
        ${v.mode === 'some' ? `<div class="pick-list">${list.map(c => `<label class="tm-chk"><input type="checkbox" value="${c.id}" ${v.picked.has(c.id) ? 'checked' : ''}> ${esc(c.code)} ${c.status === 'ready' ? '' : '<span class="small muted">(قيد الإعداد: لا يظهر له حتى يُتاح)</span>'}</label>`).join('')}</div>` : ''}</div>
      <p class="small muted">${v.mode === 'all' ? 'يُسند له كل مقرر موجود الآن في المادة؛ المقرر الذي يُضاف لاحقًا يُسند من هنا مرة أخرى.' : 'تبقى مقرراته في المواد الأخرى وطلابه المسندون كما هي.'}</p>`
      : '<div class="empty"><h3>لا يوجد حساب معلم بعد</h3><p>أنشئ حساب معلم من «الحسابات ← الفريق» أولًا.</p></div>';
    body.querySelector('#ta-t')?.addEventListener('change', e => { v.teacher = e.target.value; loadPicked(); draw(); });
    body.querySelectorAll('[data-tmode]').forEach(b => b.onclick = () => { v.mode = b.dataset.tmode; draw(); });
    body.querySelectorAll('.pick-list input').forEach(i => i.onchange = () => { const n = Number(i.value); i.checked ? v.picked.add(n) : v.picked.delete(n); });
  };
  next.onclick = async () => {
    if (!v.teacher) return toast('اختر المعلم', true);
    next.disabled = true;
    try {
      if (v.mode === 'all') await api('/admin/subjects/teacher', { method: 'POST', body: { teacher: v.teacher, subject: s.id, mode: 'add' } });
      else {
        const cur = await api('/admin/team/teacher?id=' + encodeURIComponent(v.teacher));
        const courses = [...cur.courses.filter(c => !ids.has(c)), ...v.picked];
        await api('/admin/team/teacher', { method: 'POST', body: { id: v.teacher, courses, students: cur.students } });
      }
      d.close(); toast('تم حفظ الإسناد'); await ctx.refresh();
    } catch (e) { fail(e); next.disabled = false; }
  };
  if (teacherId) loadPicked();
  draw();
}

// ---------- إسناد شعبة لمقرر: الطلاب ← المادة ← المقرر ← التأكيد (admin_enroll) ----------
export function enrollDialog(ctx, pre = {}) {
  const { esc, api, fail, toast, state } = ctx;
  const subjects = state.subjects || [];
  const students = (pre.students || []).filter(x => x.role === 'student' || x.role === 'pending');
  const v = { grade: '', section: '', subjectId: pre.subjectId || subjects[0]?.id || '', course: 0, mode: 'add' };
  let at = 0;
  const d = flowDialog({ title: 'إسناد شعبة لمقرر', steps: ['الطلاب', 'المادة', 'المقرر', 'التأكيد'], aside: false });
  const body = d.querySelector('#fl-body'), next = d.querySelector('#fl-next'), prev = d.querySelector('#fl-prev');
  const grades = [...new Set(students.map(x => x.grade).filter(Boolean))].sort();
  const picked = () => students.filter(x => (!v.grade || x.grade === v.grade) && (!v.section || x.section === v.section));
  const courseOf = () => (state.courses || []).find(c => c.id === v.course);
  const draw = () => {
    setSteps(d, at);
    prev.hidden = at === 0;
    next.innerHTML = at === 3 ? `${line('check', 16)}${v.mode === 'set' ? 'نقل' : 'إسناد'} ${num(picked().length)} طالبًا` : `التالي${line('next', 16)}`;
    if (at === 0) {
      const secs = [...new Set(students.filter(x => !v.grade || x.grade === v.grade).map(x => x.section).filter(Boolean))].sort();
      body.innerHTML = `<div class="fq two"><div><label for="en-g">الصف</label><select id="en-g"><option value="">كل الصفوف</option>${grades.map(g => `<option ${g === v.grade ? 'selected' : ''}>${esc(g)}</option>`).join('')}</select></div>
        <div><label for="en-s">الشعبة</label><select id="en-s"><option value="">كل الشعب</option>${secs.map(x => `<option ${x === v.section ? 'selected' : ''}>${esc(x)}</option>`).join('')}</select></div></div>
        <p class="notice info">المحدد: <b>${num(picked().length)}</b> طالبًا${v.grade || v.section ? ` (${esc([v.grade, v.section && 'شعبة ' + v.section].filter(Boolean).join(' · '))})` : ' (كل الطلاب)'}.</p>`;
      body.querySelector('#en-g').onchange = e => { v.grade = e.target.value; v.section = ''; draw(); };
      body.querySelector('#en-s').onchange = e => { v.section = e.target.value; draw(); };
    } else if (at === 1) {
      body.innerHTML = `<div class="fq"><label>المادة</label><div class="chips">${subjects.map(x => `<button type="button" class="chip subj-chip ${x.id === v.subjectId ? 'on' : ''}" data-subj="${escA(x.id)}">${sIcon(x, 'sm')}${esc(x.name)}</button>`).join('')}</div></div>`;
      body.querySelectorAll('[data-subj]').forEach(b => b.onclick = () => { v.subjectId = b.dataset.subj; v.course = 0; draw(); });
    } else if (at === 2) {
      const cs = (state.courses || []).filter(c => c.subjectId === v.subjectId);
      body.innerHTML = `<div class="fq"><label>المقرر</label>${cs.length ? chips('course', cs.map(c => [String(c.id), esc(c.code), c.status === 'ready' ? '' : '(قيد الإعداد)']), String(v.course)) : '<p class="notice">لا مقررات في هذه المادة بعد.</p>'}
        <span class="hint">الطالب لا يرى المقرر «قيد الإعداد» حتى يُتاح؛ يمكن إسناده مسبقًا.</span></div>`;
      body.querySelectorAll('[data-course]').forEach(b => b.onclick = () => { v.course = Number(b.dataset.course); draw(); });
    } else {
      body.innerHTML = `<div class="fq"><label>طريقة الإسناد</label>${chips('mode', [['add', 'إضافة المقرر', '(تبقى مقرراتهم الأخرى)'], ['set', 'نقل إليه', '(يصبح مقررهم الوحيد)']], v.mode)}</div>
        <p class="notice ${v.mode === 'set' ? 'warn' : 'info'}">${v.mode === 'set' ? 'نقل' : 'إسناد'} <b>${num(picked().length)}</b> طالبًا إلى <b>${esc(courseOf()?.code)}</b>.
        ${v.mode === 'set' ? 'تُلغى مقرراتهم الأخرى؛ سجل تدريبهم السابق يبقى محفوظًا.' : ''}</p>`;
      body.querySelectorAll('[data-mode]').forEach(b => b.onclick = () => { v.mode = b.dataset.mode; draw(); });
    }
  };
  prev.onclick = () => { at = Math.max(0, at - 1); draw(); };
  next.onclick = async () => {
    if (at === 0 && !picked().length) return toast('لا يوجد طلاب في هذا الاختيار', true);
    if (at === 1 && !v.subjectId) return toast('اختر المادة', true);
    if (at === 2 && !v.course) return toast('اختر المقرر', true);
    if (at < 3) { at++; return draw(); }
    next.disabled = true;
    try {
      await api('/admin/students/enroll', { method: 'POST', body: { ids: picked().map(x => x.id), course: v.course, mode: v.mode } });
      d.close(); toast(`${v.mode === 'set' ? 'نُقل' : 'أُسند المقرر إلى'} ${num(picked().length)} طالبًا`); await ctx.refresh();
    } catch (e) { fail(e); next.disabled = false; }
  };
  draw();
}

// =====================================================================
// مبدّل السياق في الترويسة: «[أيقونة] المادة › المقرر ▾»
// =====================================================================
export function renderContext(ctx) {
  const { esc, state, isOwner, choose } = ctx;
  const $ctx = document.getElementById('ctx');
  if (!$ctx) return;
  const c = state.course, courses = state.courses || [];
  const show = !!(state.user && state.user.role !== 'student' && state.user.role !== 'pending' && c && courses.length);
  $ctx.hidden = !show;
  document.body.classList.toggle('has-ctx', show);
  if (!show) { $ctx.innerHTML = ''; return; }
  const subjects = state.subjects || [];
  const s = subjectOf(c, subjects);
  const seg = c.kind === 'tahsili' ? `<span class="seg subj s-amber">${sIcon({ icon: 'sigma', color: 'amber' }, 'sm')}برنامج مشترك</span><span class="sep">‹</span>`
    : s ? `<span class="seg subj s-${escA(s.color)}">${sIcon(s, 'sm')}${esc(s.name)}</span><span class="sep">‹</span>` : '';
  const open = $ctx.querySelector('.ctx-pop:not([hidden])');
  $ctx.innerHTML = `<button type="button" class="ctx-btn" id="ctx-btn" aria-haspopup="dialog" aria-expanded="false" aria-controls="ctx-pop" title="تبديل المقرر">
      ${seg}<span class="seg crs">${esc(c.code)}</span><span class="chev">${line('chev', 16)}</span></button>
    <div class="ctx-pop" id="ctx-pop" role="dialog" aria-label="تبديل المقرر" hidden></div>`;
  const btn = $ctx.querySelector('#ctx-btn'), pop = $ctx.querySelector('#ctx-pop');
  // عمود المواد: للمالك، أو لمن تتوزع مقرراته على أكثر من مادة
  const usedSubjects = subjects.filter(x => courses.some(k => k.subjectId === x.id));
  const programs = courses.filter(k => !k.subjectId);
  const showCol = isOwner || usedSubjects.length + (programs.length ? 1 : 0) > 1;
  let pick = c.subjectId || (c.kind === 'tahsili' ? '_prog' : usedSubjects[0]?.id || '_prog'), query = '';
  const item = k => `<button type="button" class="c ${k.id === c.id ? 'on' : ''}" data-pick="${k.id}" role="option" aria-selected="${k.id === c.id}">
      <span class="t1">${esc(k.code)}</span><span class="t">${k.kind === 'tahsili' ? 'للمرحلة الثانوية' : 'الفصل ' + esc(k.term)}</span>
      ${k.status === 'ready' ? '' : '<span class="badge warn">قيد الإعداد</span>'}${k.id === c.id ? `<span class="ok-mark">${line('check', 15)}</span>` : ''}</button>`;
  const drawPop = () => {
    const q = query.trim();
    let right;
    if (q) {
      const hits = courses.filter(k => (k.code + ' ' + (k.title || '') + ' ' + (subjectOf(k, subjects)?.name || '')).includes(q));
      right = hits.length ? hits.map(item).join('') : '<p class="small muted sw-none">لا نتائج</p>';
    } else {
      const mine = pick === '_prog' ? programs : courses.filter(k => k.subjectId === pick);
      right = pick === '_prog' ? mine.map(item).join('')
        : GRADES.map(g => { const gs = mine.filter(k => k.grade === g).sort((a, b) => TERMS.indexOf(a.term) - TERMS.indexOf(b.term)); return gs.length ? `<h6>${esc(g)}</h6>${gs.map(item).join('')}` : ''; }).join('')
          || '<p class="small muted sw-none">لا مقررات في هذه المادة بعد</p>';
    }
    const rec = recents().map(id => courses.find(k => k.id === id)).filter(Boolean).filter(k => k.id !== c.id).slice(0, 3);
    pop.innerHTML = `<div class="sw-search">${line('search', 17)}<input type="search" id="ctx-q" placeholder="ابحث عن مقرر… (مثل: ${esc(c.code)})" aria-label="ابحث عن مقرر" value="${escA(query)}"></div>
      <div class="sw-cols ${showCol ? '' : 'one'}">
        ${showCol ? `<div class="sw-subj" role="tablist">${(isOwner ? subjects : usedSubjects).map(x => `<button type="button" class="it ${x.id === pick && !q ? 'on' : ''}" data-subj="${escA(x.id)}" role="tab">${sIcon(x, 'sm')}<span>${esc(x.name)}</span><small>${num(courses.filter(k => k.subjectId === x.id).length)}</small></button>`).join('')}
          ${programs.length ? `<hr><button type="button" class="it ${pick === '_prog' && !q ? 'on' : ''}" data-subj="_prog">${sIcon({ icon: 'sigma', color: 'amber' }, 'sm')}<span>برامج مشتركة</span><small>${num(programs.length)}</small></button>` : ''}</div>` : ''}
        <div class="sw-courses" role="listbox">${right}</div></div>
      <div class="sw-foot"><span>${rec.length ? `الأخيرة: ${rec.map(k => `<button type="button" class="linkish" data-pick="${k.id}">${esc(k.code)}</button>`).join(' · ')}` : ''}</span>
        ${isOwner ? `<a href="#/" class="linkish">كل المواد ${line('next', 14)}</a>` : ''}</div>`;
    const qi = pop.querySelector('#ctx-q');
    qi.oninput = () => { query = qi.value; const at = qi.selectionStart; drawPop(); const n = pop.querySelector('#ctx-q'); n.focus(); n.setSelectionRange(at, at); };
    qi.onkeydown = e => { if (e.key === 'Enter') { const f = pop.querySelector('.sw-courses [data-pick]'); if (f) f.click(); } };
    pop.querySelectorAll('[data-subj]').forEach(b => b.onclick = () => { pick = b.dataset.subj; query = ''; drawPop(); });
    pop.querySelectorAll('[data-pick]').forEach(b => b.onclick = () => { setOpen(false); choose(Number(b.dataset.pick)); });
    pop.querySelector('a[href="#/"]')?.addEventListener('click', () => setOpen(false));
  };
  const outside = e => { if (!$ctx.contains(e.target)) setOpen(false); };
  const esc2 = e => { if (e.key === 'Escape') { setOpen(false); btn.focus(); } };
  function setOpen(on) {
    pop.hidden = !on; btn.setAttribute('aria-expanded', String(on)); $ctx.classList.toggle('open', on);
    if (on) { drawPop(); pop.querySelector('#ctx-q')?.focus({ preventScroll: true }); document.addEventListener('pointerdown', outside); document.addEventListener('keydown', esc2); }
    else { document.removeEventListener('pointerdown', outside); document.removeEventListener('keydown', esc2); }
  }
  btn.onclick = () => setOpen(pop.hidden);
  if (open) setOpen(true);
}

// ---------- قوائم المقررات مجمّعة حسب المادة (<optgroup>) لصفحات الحسابات ----------
export function groupCourses(courses, subjects) {
  const groups = (subjects || []).map(s => [s.name, courses.filter(c => c.subjectId === s.id)]).filter(([, cs]) => cs.length);
  const rest = courses.filter(c => !c.subjectId || !(subjects || []).some(s => s.id === c.subjectId));
  if (!groups.length) return [['', rest]];
  if (rest.length) groups.push(['برامج مشتركة', rest]);
  return groups;
}
export function courseOptions(courses, subjects, sel, esc, { status = true } = {}) {
  const opt = c => `<option value="${c.id}" ${c.id === sel ? 'selected' : ''}>${esc(c.code)}${status && c.status !== 'ready' ? ' (قيد الإعداد)' : ''}</option>`;
  return groupCourses(courses, subjects).map(([name, cs]) => (name ? `<optgroup label="${escA(name)}">${cs.map(opt).join('')}</optgroup>` : cs.map(opt).join(''))).join('');
}
