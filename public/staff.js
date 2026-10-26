// صفحات الطاقم للطلاب: لوحة تقدم الطلاب (للمعلمين والمراجعين والمشرف) وإدارة حسابات الطلاب (للمشرف فقط).
import { icon, line } from './icons.js';
import { SITE_URL } from './config.js';
import { ROLE_NAMES, STAFF_ROLES } from './roles.js';
import { hijri } from './dates.js';

const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
const ttl = (ic, html, tag = 'h2', size = 30) => `<${tag} class="ttl">${icon(ic, size)}<span>${html}</span></${tag}>`;
const ROLE = { student: 'نشط', pending: 'موقوف' };

export async function pageTeacherProgress(ctx, section = '') {
  const { esc, $app, api } = ctx;
  const d = await api('/teacher/progress' + (section ? '?section=' + encodeURIComponent(section) : ''));
  // جودة التدريب (قراءة فقط): تُحذف الأعمدة بصمت إن لم تتوفر الدالة بعد في قاعدة البيانات
  const quality = Object.fromEntries(((await api('/teacher/quality').catch(() => [])) || []).map(q => [q.username, q]));
  const QUALITY = { serious: ['متدرب جيد', 'ok'], watch: ['يحتاج متابعة', 'warn'], low: ['تدريب قليل', ''] };
  // من لم يجب عن أي سؤال: «لم يبدأ التدريب»؛ ومن أجاب أقل من 30 إجابة محتسبة: «تدريب قليل»
  const qCell = st => {
    const q = quality[st.username];
    if (!q) return '<td>—</td>';
    if (!(q.attempts > 0) && !(st.answered > 0)) return '<td><span class="badge">لم يبدأ التدريب</span></td>';
    const [t, k] = QUALITY[q.quality] || ['—', ''];
    return `<td><span class="badge ${k}">${t}</span> <span class="small muted">${q.score} نقطة</span></td>`;
  };
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('progress', 52)}<div><h1>تقدم الطلاب</h1><p class="muted">نتائج التدريب الذاتي (لا تدخل في الدرجات).</p></div></div>
      <div class="actions"><label for="tp-sec" class="small">الشعبة</label>
        <select id="tp-sec"><option value="">كل الشعب</option>${d.sections.map(s => `<option ${s === section ? 'selected' : ''}>${esc(s)}</option>`).join('')}</select></div></section>
    <section class="card">${ttl('students', 'الطلاب')}
      ${d.students.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الطالب</th><th>الصف</th><th>الشعبة</th><th>الجلسات</th><th>الأسئلة</th><th>نسبة الصحة</th><th>جودة التدريب</th><th>آخر نشاط</th></tr></thead><tbody>
        ${d.students.map(s => `<tr><td>${esc(s.name)} <span class="small muted ltr">${esc(s.username)}</span></td><td>${esc(s.grade || '—')}</td><td>${esc(s.section || '—')}</td>
          <td>${s.sessions}</td><td>${s.answered}</td><td>${s.answered ? pct(s.correct, s.answered) + '%' : '—'}</td>
          ${qCell(s)}<td class="small">${esc(hijri(s.lastActive))}</td></tr>`).join('')}
      </tbody></table></div>
      <p class="small muted">«جودة التدريب» تقرأ سرعة الإجابات وانتظامها: «متدرب جيد» تدريب منتظم بإجابات متأنية، «يحتاج متابعة» إجابات سريعة جدًا أو نسبة قريبة من التخمين (40% فأقل لأسئلة البدائل الثلاثة، و30% فأقل لأسئلة الأربعة)، «تدريب قليل» أجاب أقل من 30 إجابة محتسبة، و«لم يبدأ التدريب» لم يجب عن أي سؤال بعد.</p>` : `<div class="empty">${ctx.state?.user?.role === 'viewer' ? 'لا يوجد طلاب مسندون لك على هذا المقرر بعد؛ يسندهم لك مالك المشروع.' : 'لا يوجد طلاب بعد.'}</div>`}
    </section>
    <section class="card">${ttl('objectives', 'الأهداف الأضعف')}
      <p class="small muted">أهداف أُجيب عن 5 أسئلة منها على الأقل، مرتبة من الأقل نسبة صحيحة.</p>
      ${d.weakObjectives.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الهدف</th><th>الدرس</th><th>الإجابات</th><th>الصحيحة</th></tr></thead><tbody>
        ${d.weakObjectives.map(o => `<tr><td><a href="#/objective/${encodeURIComponent(o.code)}">${esc(o.text)}</a></td><td>${esc(o.lesson)}</td><td>${o.n}</td><td>${o.pct}%</td></tr>`).join('')}
      </tbody></table></div>` : '<div class="empty">لا توجد بيانات كافية بعد.</div>'}
    </section>`;
  document.getElementById('tp-sec').onchange = e => pageTeacherProgress(ctx, e.target.value).catch(ctx.fail);
}

// رصيد الدرجات: ما استبدله طلاب المعلم المسندون من نقاط التميّز، ليرصدها لهم
// حالة التصفية والفرز تبقى عند إعادة رسم الصفحة (بعد الرصد مثلًا)
const gv = { status: 'pending', grade: '', section: '', q: '', key: 'pending', dir: -1, picked: new Set() };
const SORTS = [['pending', 'الأكثر درجات بانتظار الرصد', -1], ['oldest', 'الأقدم انتظارًا للرصد', 1], ['last', 'آخر استبدال (الأحدث)', -1], ['name', 'الاسم (أبجديًا)', 1],
  ['section', 'الشعبة ثم الاسم', 1], ['recorded', 'الأكثر درجات مرصودة', -1]];
export async function pageTeacherGrades(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const d = await api('/teacher/grades');
  const canWrite = ['admin', 'viewer'].includes(ctx.state?.user?.role);
  const pendingAll = d.reduce((a, x) => a + x.pending, 0), pendingStudents = d.filter(x => x.pending).length, recordedAll = d.reduce((a, x) => a + x.recorded, 0);
  if (!d.some(x => x.pending) && gv.status === 'pending') gv.status = 'all'; // لا شيء ينتظر الرصد: اعرض الكل
  const ST = { pending: ['بانتظار الرصد', 'warn'], recorded: ['مرصودة', 'ok'], cancelled: ['ملغاة', ''] };
  const grades = [...new Set(d.map(x => x.grade).filter(Boolean))].sort();
  const ar = (a, b) => String(a || '').localeCompare(String(b || ''), 'ar');
  const num = x => Number(x || 0);
  const age = at => { const n = Math.floor((Date.now() - new Date(at)) / 86400000); return n <= 0 ? 'اليوم' : n === 1 ? 'منذ يوم' : `منذ ${n} أيام`; };
  const view = () => {
    const kw = gv.q.trim().toLowerCase();
    const rows = d.filter(x => (gv.status === 'all' || (gv.status === 'pending' ? x.pending > 0 : x.recorded > 0 && !x.pending)) && (!gv.grade || x.grade === gv.grade)
      && (!gv.section || x.section === gv.section) && (!kw || `${x.name} ${x.username}`.toLowerCase().includes(kw)));
    const cmp = { pending: (a, b) => num(a.pending) - num(b.pending), recorded: (a, b) => num(a.recorded) - num(b.recorded), name: (a, b) => ar(a.name, b.name),
      section: (a, b) => ar(a.section, b.section) || ar(a.name, b.name), grade: (a, b) => ar(a.grade, b.grade) || ar(a.name, b.name),
      last: (a, b) => new Date(a.lastAt) - new Date(b.lastAt), oldest: (a, b) => (a.oldestPending ? new Date(a.oldestPending) : Infinity) - (b.oldestPending ? new Date(b.oldestPending) : Infinity) }[gv.key];
    return rows.sort((a, b) => gv.dir * (cmp(a, b) || ar(a.name, b.name)));
  };
  const head = (key, label) => `<th><button type="button" class="tg-sort ${gv.key === key ? 'on' : ''}" data-sort="${key}" title="فرز">${label}${gv.key === key ? (gv.dir > 0 ? ' ▲' : ' ▼') : ''}</button></th>`;
  const draw = () => {
    const rows = view();
    const secs = [...new Set(d.filter(x => !gv.grade || x.grade === gv.grade).map(x => x.section).filter(Boolean))].sort();
    if (gv.section && !secs.includes(gv.section)) gv.section = '';
    const shownPending = rows.filter(x => x.pending);
    for (const id of [...gv.picked]) if (!rows.some(x => x.userId === id && x.pending)) gv.picked.delete(id);
    box.innerHTML = `
      <div class="tg-filters">
        <div class="tg-seg" role="group" aria-label="الحالة">${[['pending', `بانتظار الرصد (${pendingStudents})`], ['recorded', 'مرصودة فقط'], ['all', `الكل (${d.length})`]].map(([k, t]) => `<button type="button" data-st="${k}" class="${gv.status === k ? 'on' : ''}">${t}</button>`).join('')}</div>
        <label>الصف <select id="tg-grade"><option value="">كل الصفوف</option>${grades.map(g => `<option ${g === gv.grade ? 'selected' : ''}>${esc(g)}</option>`).join('')}</select></label>
        <label>الشعبة <select id="tg-sec"><option value="">كل الشعب</option>${secs.map(x => `<option ${x === gv.section ? 'selected' : ''}>${esc(x)}</option>`).join('')}</select></label>
        <label>بحث <input id="tg-q" value="${esc(gv.q)}" placeholder="اسم الطالب" style="max-width:11rem"></label>
        <label>الترتيب <select id="tg-sortsel">${SORTS.map(([k, t]) => `<option value="${k}" ${gv.key === k ? 'selected' : ''}>${t}</option>`).join('')}</select></label>
        <button type="button" id="tg-reset">إعادة الضبط</button></div>
      <p class="small muted">يعرض ${rows.length} من ${d.length} طالبًا${shownPending.length ? ` · بانتظار الرصد لدى ${shownPending.length} منهم (${shownPending.reduce((a, x) => a + x.pending, 0)} درجة)` : ''}.</p>
      ${canWrite && shownPending.length ? `<div class="actions tg-bulk"><label class="st-radio"><input type="checkbox" id="tg-pickall" ${gv.picked.size && gv.picked.size === shownPending.length ? 'checked' : ''}> تحديد كل من ينتظر الرصد (${shownPending.length})</label>
        <button type="button" class="primary" id="tg-rec-picked" ${gv.picked.size ? '' : 'disabled'}>تم رصد المحدد (${gv.picked.size})</button>
        <button type="button" id="tg-rec-shown">تم رصد كل المعروضين (${shownPending.length})</button></div>` : ''}
      ${rows.length ? `<div class="table-wrap"><table class="list"><thead><tr>${canWrite ? '<th class="as-chk"></th>' : ''}${head('name', 'الطالب')}${head('grade', 'الصف')}${head('section', 'الشعبة')}${head('pending', 'بانتظار الرصد')}${head('oldest', 'ينتظر منذ')}${head('recorded', 'المرصودة')}${head('last', 'آخر استبدال')}<th></th></tr></thead><tbody>
        ${rows.map(x => `<tr data-id="${x.userId}">${canWrite ? `<td class="as-chk">${x.pending ? `<input type="checkbox" data-pick="${x.userId}" ${gv.picked.has(x.userId) ? 'checked' : ''} aria-label="تحديد ${esc(x.name)}">` : ''}</td>` : ''}
          <td>${esc(x.name)} <span class="small muted ltr">${esc(x.username)}</span></td><td>${esc(x.grade || '—')}</td><td>${esc(x.section || '—')}</td>
          <td>${x.pending ? `<span class="badge warn">${x.pending}</span>` : '0'}</td><td class="small">${x.oldestPending ? esc(age(x.oldestPending)) : '—'}</td><td>${x.recorded}</td><td class="small">${esc(hijri(x.lastAt))}</td>
          <td class="actions">${canWrite && x.pending ? `<button type="button" class="primary" data-rec="${x.userId}">تم الرصد</button>` : ''}
            <details class="small"><summary>السجل</summary><ul class="tg-items">${x.items.map(i => { const [t, k] = ST[i.status] || ['—', '']; return `<li>${esc(hijri(i.at, true))} · ${i.grades} درجة (${i.points} نقطة)
              <span class="badge ${k}">${t}</span>${i.reason ? ` <span class="muted">${esc(i.reason)}</span>` : ''}
              ${canWrite && i.status === 'pending' ? `<button type="button" class="danger" data-cancel="${i.id}">إلغاء</button>` : ''}</li>`; }).join('')}</ul></details></td></tr>`).join('')}
      </tbody></table></div>` : '<div class="empty">لا نتائج بهذه التصفية.</div>'}`;
    const redraw = () => draw();
    box.querySelectorAll('[data-st]').forEach(b => b.onclick = () => { gv.status = b.dataset.st; redraw(); });
    box.querySelector('#tg-grade').onchange = e => { gv.grade = e.target.value; redraw(); };
    box.querySelector('#tg-sec').onchange = e => { gv.section = e.target.value; redraw(); };
    box.querySelector('#tg-q').oninput = e => { gv.q = e.target.value; clearTimeout(draw.t); draw.t = setTimeout(() => { redraw(); const i = box.querySelector('#tg-q'); i.focus(); i.setSelectionRange(i.value.length, i.value.length); }, 250); };
    box.querySelector('#tg-sortsel').onchange = e => { const s = SORTS.find(x => x[0] === e.target.value); gv.key = s[0]; gv.dir = s[2]; redraw(); };
    box.querySelector('#tg-reset').onclick = () => { Object.assign(gv, { status: pendingAll ? 'pending' : 'all', grade: '', section: '', q: '', key: 'pending', dir: -1 }); gv.picked.clear(); redraw(); };
    box.querySelectorAll('[data-sort]').forEach(b => b.onclick = () => { const k = b.dataset.sort; if (gv.key === k) gv.dir = -gv.dir; else { gv.key = k; gv.dir = ['name', 'grade', 'section', 'oldest'].includes(k) ? 1 : -1; } redraw(); });
    box.querySelectorAll('[data-pick]').forEach(c => c.onchange = () => { c.checked ? gv.picked.add(c.dataset.pick) : gv.picked.delete(c.dataset.pick); redraw(); });
    box.querySelector('#tg-pickall')?.addEventListener('change', e => { gv.picked.clear(); if (e.target.checked) shownPending.forEach(x => gv.picked.add(x.userId)); redraw(); });
    const recMany = async ids => { try { const n = await api('/teacher/grades/record-many', { method: 'POST', body: { users: ids } }); gv.picked.clear(); toast(`سُجّل رصد ${n} درجة`); await pageTeacherGrades(ctx); } catch (e) { fail(e); } };
    box.querySelector('#tg-rec-picked')?.addEventListener('click', () => { if (confirm(`ستُعلَّم درجات ${gv.picked.size} طالبًا كمرصودة. هل رصدتها فعلًا؟`)) recMany([...gv.picked]); });
    box.querySelector('#tg-rec-shown')?.addEventListener('click', () => { if (confirm(`ستُعلَّم درجات ${shownPending.length} طالبًا (المعروضين) كمرصودة. هل رصدتها فعلًا؟`)) recMany(shownPending.map(x => x.userId)); });
    box.querySelectorAll('[data-rec]').forEach(b => b.onclick = () => run(() => api('/teacher/grades/record', { method: 'POST', body: { user: b.dataset.rec } }), 'سُجّل الرصد'));
    box.querySelectorAll('[data-cancel]').forEach(b => b.onclick = () => {
      const reason = prompt('سبب الإلغاء (يظهر للطالب):');
      if (reason && reason.trim().length >= 3) run(() => api('/teacher/grades/cancel', { method: 'POST', body: { id: Number(b.dataset.cancel), reason: reason.trim() } }), 'أُلغيت وعادت النقاط للطالب');
      else if (reason !== null) fail(new Error('اكتب سببًا واضحًا للإلغاء'));
    });
  };
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('coin', 52)}<div><h1>رصيد الدرجات</h1>
      <p class="muted">درجات استبدلها طلابك من نقاط التميّز (كل درجة تقابل تدريبًا جادًا منتظمًا). ارصدها في نظام الدرجات ثم اضغط «تم الرصد». يمكنك إلغاء درجة لم تُرصد بعد بسبب مكتوب فتعود نقاط الطالب إليه. استعمل التصفية والفرز لتجد من تريد، وحدّد عدة طلاب لرصدهم دفعة واحدة.</p></div></div>
      <div class="actions"><span class="badge ${pendingAll ? 'warn' : 'ok'}">${pendingAll ? `${pendingAll} درجة بانتظار الرصد لدى ${pendingStudents} طالبًا` : 'لا درجات بانتظار الرصد'}</span>
        <span class="badge">${recordedAll} درجة مرصودة</span>
        ${d.length ? `<button type="button" id="tg-export">${line('download', 17)}تصدير Excel (حسب العرض الحالي)</button>` : ''}</div></section>
    <section class="card">${ttl('students', 'الطلاب')}<div id="tg-box">${d.length ? '' : '<div class="empty">لم يستبدل أي من طلابك نقاطه بعد.</div>'}</div></section>`;
  const box = document.getElementById('tg-box');
  const run = async (fn, msg) => { try { await fn(); toast(msg); await pageTeacherGrades(ctx); } catch (e) { fail(e); } };
  if (d.length) draw();
  if (canWrite) couponsCard(ctx);
  document.getElementById('tg-export')?.addEventListener('click', () => downloadXlsx('itqan-grades-balance', ['الاسم', 'اسم المستخدم', 'الصف', 'الشعبة', 'بانتظار الرصد', 'المرصودة', 'ينتظر منذ', 'آخر استبدال'],
    view().map(x => [x.name, x.username, x.grade || '', x.section || '', x.pending, x.recorded, x.oldestPending ? age(x.oldestPending) : '', hijri(x.lastAt)])));
}

// رسائل ومهام المعلم لطلابه: رسالة (قراءة فقط) أو مهمة تُحتسب تلقائيًا من تدريب الطالب
const COMM_TEMPLATES = [
  ['تذكير بالمراجعة', 'راجعوا الدرس قبل الحصة القادمة', 'حاولوا حل بعض أسئلة التدريب في المنصة قبل الحصة.'],
  ['أحسنت', 'أحسنت، واصل تميّزك', 'لاحظت التزامك بالتدريب، استمر على هذا المستوى.'],
  ['اختبار قريب', 'اختبار قريب', 'استعدوا للاختبار القادم بالتدريب على الدروس المقررة.'],
  ['ابدأ هذا الدرس', 'ابدأ بهذا الدرس', 'ابدأ بالتدريب على الدرس الذي شرحناه اليوم.'],
];
export async function pageTeacherComms(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const [list, students, chapters] = await Promise.all([api('/staff/comms'), api('/staff/students'), api('/staff/lessons')]);
  const grades = [...new Set(students.map(s => s.grade).filter(Boolean))].sort();
  const owner = ctx.state?.user?.role === 'admin';
  const defDue = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('mail', 52)}<div><h1>رسائل ومهام</h1>
      <p class="muted">أرسل لطلابك رسالة أو مهمة. المهمة تُحتسب تلقائيًا من تدريب الطالب (أول إجابة لكل سؤال في الدرس، والإجابة الأسرع من 3 ثوانٍ لا تُحتسب). الطالب يقرأ ويرد بزر «فهمت» أو «أحتاج مساعدة» فقط.${owner ? ' (أنت المالك: ترى رسائل كل المعلمين.)' : ' يطّلع مالك المشروع على الرسائل المرسلة.'}</p></div></div></section>
    <section class="card">${ttl('mail', 'إرسال جديد')}
      <div class="cm-form">
        <div class="cm-row"><label class="st-radio"><input type="radio" name="cm-kind" value="message" checked> رسالة</label>
          <label class="st-radio"><input type="radio" name="cm-kind" value="task"> مهمة (حل أسئلة في درس)</label></div>
        <div class="cm-chips" id="cm-tpl"><span class="small muted">قوالب:</span>${COMM_TEMPLATES.map((t, i) => `<button type="button" data-tpl="${i}">${esc(t[0])}</button>`).join('')}</div>
        <div class="field"><label for="cm-title">العنوان (80 حرفًا)</label><input id="cm-title" maxlength="80"></div>
        <div class="field"><label for="cm-body">النص (اختياري، 500 حرف)</label><textarea id="cm-body" dir="auto" maxlength="500" rows="3"></textarea>
          <span class="small muted">لا تكتب أسماء طلاب أو درجاتهم في النص؛ الرسالة تصل لكل المستلمين.</span></div>
        <div class="cm-row" id="cm-task" hidden>
          <label>الدرس <select id="cm-lesson">${chapters.map(c => `<optgroup label="${esc(c.number + '. ' + c.title)}">${c.lessons.map(l => `<option value="${l.id}">${esc(l.number + '. ' + l.title)}</option>`).join('')}</optgroup>`).join('')}</select></label>
          <label>عدد الأسئلة <input type="number" id="cm-n" min="5" max="200" value="20" style="max-width:6rem"></label>
          <label>نسبة الصحة المطلوبة % <input type="number" id="cm-acc" min="0" max="100" value="70" style="max-width:6rem"></label>
          <label>آخر موعد <input type="date" id="cm-due" value="${defDue}"></label>
          <label>مكافأة الإنجاز (نقاط لكل طالب) <input type="number" id="cm-reward" min="0" max="500" value="0" style="max-width:6rem"></label>
          <span class="small muted" style="flex-basis:100%">المكافأة اختيارية: تُضاف لرصيد من يُنجز المهمة قبل الموعد (لا تدخل نقاط الترتيب)، وتُخصم من حصتك الأسبوعية (النقاط × عدد الطلاب) وتعود حصة من لم ينجز. تتطلب 10 أسئلة على الأقل وصحة 50% فأكثر.</span></div>
        <div class="cm-row"><label>المرحلة (الصف) <select id="cm-grade"><option value="">كل المراحل</option>${grades.map(g => `<option>${esc(g)}</option>`).join('')}</select></label>
          <label>الشعبة <select id="cm-sec"><option value="">كل الشعب</option></select></label>
          <label>إلى <select id="cm-mode"><option value="all"></option><option value="students">طلاب محددين من القائمة</option></select></label></div>
        <div class="cm-students" id="cm-stu" hidden>${students.length ? '' : `<p class="notice warn small">${owner ? 'لا توجد حسابات طلاب بعد.' : 'لا يوجد طلاب مسندون لك بعد؛ يسندهم لك مالك المشروع من «حسابات الفريق».'}</p>`}
          <label class="chk" id="cm-stu-all-w"><input type="checkbox" id="cm-stu-all"> <b>تحديد كل المعروضين</b></label>${students.map(s => `<label class="chk" data-row="${esc(s.grade || '')}|${esc(s.section || '')}"><input type="checkbox" data-stu="${s.id}"> ${esc(s.name)} <span class="small muted">(${esc(s.grade || '—')} · ${esc(s.section || '—')})</span></label>`).join('')}</div>
        <div class="actions"><button type="button" class="primary" id="cm-send">إرسال</button></div>
      </div></section>
    <section class="card">${ttl('mail', 'المُرسَل')}
      ${list.length ? `<ul class="cm-list">${list.map(c => {
        const t = c.task, off = c.status === 'cancelled';
        return `<li class="cm-item ${off ? 'off' : ''}" data-comm="${c.id}"><div class="in-head"><b>${esc(c.title)}</b>
          <span class="badge ${c.kind === 'task' ? 'brand' : ''}">${c.kind === 'task' ? 'مهمة' : 'رسالة'}</span>${off ? '<span class="badge">ملغاة</span>' : ''}
          <span class="small muted">${esc(c.sender || '')} · ${esc(hijri(c.createdAt))} · إلى ${c.n} طالبًا</span></div>
          ${c.body ? `<div class="small in-body">${esc(c.body)}</div>` : ''}
          <div class="small muted">قرأها ${c.read} من ${c.n}${c.help ? ` · يحتاج مساعدة: <b>${c.help}</b>` : ''}${c.ack ? ` · فهموا: ${c.ack}` : ''}${t ? ` · ${esc(t.lesson || '')}: ${t.n} سؤالًا${t.minAccuracy ? ` بصحة ${t.minAccuracy}%` : ''}${t.reward ? ` · مكافأة ${t.reward} نقطة` : ''} قبل ${esc(hijri(t.dueAt))} — أنجز ${t.done}، جارية ${t.open}، انتهى موعدها ${t.missed}` : ''}</div>
          <div class="actions"><button type="button" data-detail="${c.id}">التفاصيل</button>${off ? '' : `<button type="button" class="danger" data-cancel="${c.id}">إلغاء</button>`}</div>
          <div class="cm-detail" id="cmd-${c.id}"></div></li>`; }).join('')}</ul>` : '<div class="empty">لم ترسل شيئًا بعد.</div>'}</section>`;
  const q = s => $app.querySelector(s);
  const kind = () => $app.querySelector('[name=cm-kind]:checked').value;
  $app.querySelectorAll('[name=cm-kind]').forEach(r => r.onchange = () => { q('#cm-task').hidden = kind() !== 'task'; q('#cm-tpl').hidden = kind() !== 'message'; });
  $app.querySelectorAll('[data-tpl]').forEach(b => b.onclick = () => { const t = COMM_TEMPLATES[Number(b.dataset.tpl)]; q('#cm-title').value = t[1]; q('#cm-body').value = t[2]; });
  // التصفية: المرحلة ثم الشعبة (الشعب المعروضة تتبع المرحلة)، وتنطبق على «الكل» وعلى قائمة الطلاب المحددين
  const matching = () => students.filter(s => (!q('#cm-grade').value || s.grade === q('#cm-grade').value) && (!q('#cm-sec').value || s.section === q('#cm-sec').value));
  const refreshFilter = () => {
    const g = q('#cm-grade').value, cur = q('#cm-sec').value;
    const secs = [...new Set(students.filter(s => !g || s.grade === g).map(s => s.section).filter(Boolean))].sort();
    q('#cm-sec').innerHTML = `<option value="">كل الشعب</option>${secs.map(x => `<option ${x === cur ? 'selected' : ''}>${esc(x)}</option>`).join('')}`;
    const m = matching();
    q('#cm-mode').options[0].textContent = `${owner ? 'كل الطلاب' : 'كل طلابي'} حسب التصفية (${m.length})`;
    const ids = new Set(m.map(s => s.id));
    $app.querySelectorAll('[data-stu]').forEach(b => { const row = b.closest('label'); row.hidden = !ids.has(b.dataset.stu); if (row.hidden) b.checked = false; });
    q('#cm-stu-all-w').hidden = !m.length;
  };
  q('#cm-grade').onchange = refreshFilter; q('#cm-sec').onchange = refreshFilter;
  q('#cm-stu-all').onchange = e => { $app.querySelectorAll('[data-stu]').forEach(b => { if (!b.closest('label').hidden) b.checked = e.target.checked; }); };
  q('#cm-mode').onchange = e => { q('#cm-stu').hidden = e.target.value !== 'students'; };
  refreshFilter();
  q('#cm-send').onclick = async e => {
    const b = e.currentTarget, mode = q('#cm-mode').value;
    const body = { kind: kind(), title: q('#cm-title').value, body: q('#cm-body').value,
      target: { mode, grade: q('#cm-grade').value || null, section: q('#cm-sec').value || null, students: mode === 'students' ? [...$app.querySelectorAll('[data-stu]:checked')].map(i => i.dataset.stu) : [] } };
    if (body.kind === 'task') Object.assign(body, { lesson: q('#cm-lesson').value, n: q('#cm-n').value, minAccuracy: q('#cm-acc').value, reward: q('#cm-reward').value || 0, due: `${q('#cm-due').value}T23:59:00+03:00` });
    b.disabled = true;
    try { const r = await api('/staff/comms', { method: 'POST', body }); toast(`أُرسلت إلى ${r.n} طالبًا`); await pageTeacherComms(ctx); }
    catch (err) { b.disabled = false; fail(err); }
  };
  $app.querySelectorAll('[data-cancel]').forEach(b => b.onclick = async () => {
    if (!confirm('إلغاء هذه الرسالة؟ ستختفي من صناديق الطلاب.')) return;
    try { await api('/staff/comms/cancel', { method: 'POST', body: { id: Number(b.dataset.cancel) } }); toast('أُلغيت'); await pageTeacherComms(ctx); } catch (err) { fail(err); }
  });
  const ST = { open: 'جارية', done: 'أنجز', missed: 'انتهى الموعد' };
  $app.querySelectorAll('[data-detail]').forEach(b => b.onclick = async () => {
    const box = document.getElementById('cmd-' + b.dataset.detail);
    if (box.innerHTML) { box.innerHTML = ''; return; }
    try {
      const rows = await api('/staff/comms/detail?id=' + b.dataset.detail);
      const isTask = list.find(c => String(c.id) === b.dataset.detail)?.kind === 'task';
      box.innerHTML = `<div class="table-wrap"><table class="list"><thead><tr><th>الطالب</th><th>الشعبة</th><th>قرأها</th><th>رده</th>${isTask ? '<th>الحالة</th><th>التقدم</th>' : ''}</tr></thead><tbody>
        ${rows.map(r => `<tr><td>${esc(r.name)} <span class="small muted ltr">${esc(r.username)}</span></td><td>${esc(r.section || '—')}</td><td>${r.read ? '✓' : '—'}</td>
          <td>${r.reply === 2 ? '<span class="badge warn">يحتاج مساعدة</span>' : r.reply === 1 ? 'فهمت' : '—'}</td>
          ${isTask ? `<td>${ST[r.status]}</td><td>${r.valid} سؤالًا${r.valid ? ` · ${pct(r.correct, r.valid)}%` : ''}</td>` : ''}</tr>`).join('')}</tbody></table></div>`;
    } catch (err) { fail(err); }
  });
}

// كوبونات النقاط: يصدرها المعلم أو المالك فيدخلها الطالب في «الرصيد» (مرة واحدة، ولا تدخل الترتيب)
async function couponsCard(ctx, fresh = null) {
  const { esc, $app, api, fail, toast } = ctx;
  let d;
  try { d = await api('/staff/coupons'); } catch { return; }
  if (!$app.isConnected) return;
  let box = document.getElementById('cp-card');
  if (!box) { box = document.createElement('section'); box.className = 'card'; box.id = 'cp-card'; $app.append(box); }
  const ST = { active: ['فعّال', 'ok'], redeemed: ['استُخدم', 'brand'], expired: ['منتهي', ''], cancelled: ['ملغى', ''] };
  box.innerHTML = `${ttl('coin', 'كوبونات النقاط')}
    <p class="small muted">أصدر كودًا بقيمة نقاط يعطيه الطالب لنفسه من «الرصيد». الكود لمرة واحدة، يستخدمه أي طالب من طلابك المسندين، ولا يدخل نقاطه في الترتيب. الحد الأقصى للكوبون <b>${d.max}</b> نقطة${d.quota != null ? `، واستخدمت <b>${d.used}</b> من حصتك الأسبوعية <b>${d.quota}</b>` : ''}.</p>
    <div class="cp-form"><label>النقاط <input type="number" id="cp-pts" min="1" max="${d.max}" value="${Math.min(50, d.max)}"></label>
      <label>سبب المكافأة (يراه الطالب) <input id="cp-note" maxlength="120" placeholder="مثال: مشاركة متميزة في الحصة"></label>
      <label>الصلاحية <select id="cp-days"><option value="3">3 أيام</option><option value="7" selected>7 أيام</option><option value="14">14 يومًا</option><option value="30">30 يومًا</option></select></label>
      <button type="button" class="primary" id="cp-make">إصدار كوبون</button></div>
    ${fresh ? `<div class="notice ok" id="cp-fresh"><b>تم الإصدار:</b> <span class="cp-code ltr">${esc(fresh.code)}</span> · ${fresh.points} نقطة
      <button type="button" id="cp-copy">نسخ الكود</button></div>` : ''}
    ${d.items.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الكود</th><th>النقاط</th><th>السبب</th><th>الحالة</th><th>ينتهي</th><th></th></tr></thead><tbody>
      ${d.items.map(c => { const [t, k] = ST[c.status] || ['—', '']; return `<tr><td class="cp-code ltr">${esc(c.code)}</td><td>${c.points}</td><td>${esc(c.note || '')}</td>
        <td><span class="badge ${k}">${t}</span>${c.redeemedBy ? ` <span class="small muted">${esc(c.redeemedBy)} · ${esc(hijri(c.redeemedAt))}</span>` : ''}</td>
        <td class="small">${esc(hijri(c.expiresAt))}</td><td>${c.status === 'active' ? `<button type="button" class="danger" data-cpcancel="${c.id}">إلغاء</button>` : ''}</td></tr>`; }).join('')}
    </tbody></table></div>` : '<div class="empty">لم تُصدر كوبونات بعد.</div>'}`;
  document.getElementById('cp-make').onclick = async e => {
    const b = e.currentTarget; b.disabled = true;
    try {
      const c = await api('/staff/coupons', { method: 'POST', body: { points: document.getElementById('cp-pts').value, note: document.getElementById('cp-note').value, days: document.getElementById('cp-days').value } });
      toast('صدر الكوبون'); await couponsCard(ctx, c);
    } catch (err) { fail(err); b.disabled = false; }
  };
  document.getElementById('cp-copy')?.addEventListener('click', () => { navigator.clipboard?.writeText(fresh.code).then(() => toast('نُسخ الكود'), () => {}); });
  box.querySelectorAll('[data-cpcancel]').forEach(b => b.onclick = async () => {
    if (!confirm('إلغاء هذا الكوبون؟ لن يعمل بعد الآن.')) return;
    try { await api('/staff/coupons/cancel', { method: 'POST', body: { id: Number(b.dataset.cpcancel) } }); toast('أُلغي الكوبون'); await couponsCard(ctx); } catch (err) { fail(err); }
  });
}

// ---------- Excel ----------
// SheetJS من cdnjs (إصدار مثبت)، يُحمَّل عند الحاجة فقط. ملفات CSV تُقرأ دونه.
const XLSX_URL = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
let xlsxLoading = null;
function loadXlsx() {
  if (window.XLSX) return Promise.resolve(window.XLSX);
  xlsxLoading ||= new Promise((resolve, reject) => {
    const sc = Object.assign(document.createElement('script'), { src: XLSX_URL, onload: () => resolve(window.XLSX),
      onerror: () => { xlsxLoading = null; reject(new Error('تعذر تحميل مكتبة Excel؛ تحقق من الإنترنت أو احفظ الملف بصيغة CSV')); } });
    document.head.append(sc);
  });
  return xlsxLoading;
}

// الترتيب مهم: «اسم المستخدم» يُفحص قبل «الاسم» حتى لا يُعدّ عمود المستخدم عمود الاسم.
const COLS = [
  ['username', /اسم المستخدم|المستخدم|^user\s*name$|^username$|^user$|^login$/i],
  ['password', /كلمة المرور|^password$/i],
  ['name', /اسم الطالب|^الاسم|^اسم$|^name$|^student\s*name$|^full\s*name$/i],
  ['grade', /الصف|^grade$/i],
  ['section', /الشعبة|^الفصل|^section$|^class$/i],
];
const OUT_COLS = ['name', 'grade', 'section', 'username', 'password'];
// يحوّل صفوف الجدول إلى طلاب: يتعرف على الأعمدة من عناوينها، وإلا يفترض الترتيب: الاسم، الصف، الشعبة، اسم المستخدم، كلمة المرور.
export function rowsToStudents(rows) {
  rows = rows.map(r => r.map(c => String(c ?? '').trim())).filter(r => r.some(Boolean));
  if (!rows.length) return [];
  // صف العناوين قد يسبقه عنوان للملف: يُبحث عنه في أول 5 صفوف
  let headAt = -1, map = {};
  for (let h = 0; h < Math.min(5, rows.length) && headAt < 0; h++) {
    const m = {};
    rows[h].forEach((cell, i) => { const hit = COLS.find(([k, re]) => !(k in m) && re.test(cell)); if (hit) m[hit[0]] = i; });
    if ('name' in m) { headAt = h; map = m; }
  }
  const idx = headAt >= 0 ? map : { name: 0, grade: 1, section: 2, username: 3, password: 4 };
  return rows.slice(headAt + 1).map(r => Object.fromEntries(OUT_COLS.map(k => [k, idx[k] != null ? r[idx[k]] || '' : ''])))
    .filter(s => s.name);
}
function parseCsv(text) {
  const rows = []; let row = [], cell = '', q = false;
  text = text.replace(/^﻿/, '');
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (ch === '"') q = false; else cell += ch; }
    else if (ch === '"') q = true;
    else if (ch === ',' || ch === ';' || ch === '\t') { row.push(cell); cell = ''; }
    else if (ch === '\n' || ch === '\r') { if (ch === '\r' && text[i + 1] === '\n') i++; row.push(cell); rows.push(row); row = []; cell = ''; }
    else cell += ch;
  }
  row.push(cell); rows.push(row);
  return rows;
}
async function readStudentFile(file) {
  if (/\.csv$/i.test(file.name)) return rowsToStudents(parseCsv(await file.text()));
  const XLSX = await loadXlsx();
  const wb = XLSX.read(await file.arrayBuffer(), { type: 'array' });
  return rowsToStudents(XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '', raw: false }));
}
async function downloadXlsx(name, header, rows) {
  try {
    const XLSX = await loadXlsx();
    const ws = XLSX.utils.aoa_to_sheet([header, ...rows]);
    ws['!cols'] = header.map((_, i) => ({ wch: Math.max(12, ...rows.map(r => String(r[i] ?? '').length + 2)) }));
    const wb = XLSX.utils.book_new(); wb.Workbook = { Views: [{ RTL: true }] };
    XLSX.utils.book_append_sheet(wb, ws, 'الطلاب');
    XLSX.writeFile(wb, name + '.xlsx');
  } catch {
    // بديل دون المكتبة: CSV يفتحه Excel مباشرة
    // خلية تبدأ بـ = + - @ تُسبق بفاصلة عليا حتى لا ينفذها Excel كمعادلة
    const cell = v => { let t = String(v ?? ''); if (/^[=+\-@]/.test(t)) t = "'" + t; return /[",\n]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t; };
    const blob = new Blob(['﻿' + [header, ...rows].map(r => r.map(cell).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: name + '.csv' });
    document.body.append(a); a.click(); a.remove();
  }
}

// سطر لكل طالب: «الاسم، الشعبة» أو «الاسم، الصف، الشعبة» أو «الاسم، الصف، الشعبة، اسم المستخدم».
export function parseStudentLines(text) {
  return String(text || '').split(/\r?\n/).map(l => l.trim()).filter(Boolean).map(l => {
    const p = l.split(/\s*[,،\t]\s*/);
    return p.length <= 2 ? { name: p[0] || '', grade: '', section: p[1] || '', username: '' }
      : { name: p[0], grade: p[1] || '', section: p[2] || '', username: p[3] || '', password: p[4] || '' };
  });
}

const adminFilter = { grade: '', section: '', q: '' };
export const resetStaffState = () => Object.assign(adminFilter, { grade: '', section: '', q: '' });

export async function pageAdminStudents(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const all = await api('/admin/students');
  // المقررات (على Supabase): عمود «المقرر» وإسناد دفعة، ومقرر الحسابات الجديدة
  const courses = ctx.state?.supabase ? (ctx.state.courses || []) : [];
  const cur = ctx.state?.course;
  const courseName = id => courses.find(c => c.id === id)?.code || '';
  const courseOpts = sel => courses.map(c => `<option value="${c.id}" ${c.id === sel ? 'selected' : ''}>${esc(c.code)}${c.status === 'ready' ? '' : ' (قيد الإعداد)'}</option>`).join('');
  const grades = [...new Set(all.map(s => s.grade).filter(Boolean))].sort();
  if (adminFilter.grade && !grades.includes(adminFilter.grade)) adminFilter.grade = '';
  const sections = [...new Set(all.filter(s => !adminFilter.grade || s.grade === adminFilter.grade).map(s => s.section).filter(Boolean))].sort();
  if (adminFilter.section && !sections.includes(adminFilter.section)) adminFilter.section = '';
  const list = all.filter(s => (!adminFilter.grade || s.grade === adminFilter.grade) && (!adminFilter.section || s.section === adminFilter.section)
    && (!adminFilter.q || (s.name + ' ' + s.username).includes(adminFilter.q)));
  let pending = [];
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('students', 52)}<div><h1>حسابات الطلاب</h1><p class="muted">الطالب يرى صفحة التدريب فقط: لا إجابات جماعية ولا مراجعة ولا منشئ اختبارات.</p></div></div>
      ${accountTabs('students', ctx)}</section>
    ${ctx.state?.supabase ? `<section class="card" id="rank-term-card">${ttl('trophy', 'الفصل الدراسي ونقاط التميّز', 'h2', 30)}
      <p class="small muted">قائمة التميّز تحسب نقاط الطلاب من بداية الفصل الحالي. عند انتهاء الفصل ابدأ فصلًا جديدًا لتُصفَّر النقاط؛ سجل التدريب نفسه لا يُمسّ. وتُصفَّر نقاط الطالب تلقائيًا عند نقله إلى صف آخر.</p>
      <p id="rank-term-info" class="small">جارٍ التحميل…</p>
      <div class="actions"><button type="button" id="rank-new-term" class="danger">بدء فصل دراسي جديد (تصفير نقاط التميّز)</button></div></section>` : ''}
    ${ctx.state?.supabase ? `<section class="card" id="comm-set-card">${ttl('mail', 'رسائل ومهام المعلمين: الحدود', 'h2', 30)}
      <p class="small muted">يرسل المعلمون لطلابهم المسندين رسائل ومهامًا من «رسائل ومهام». تضبط هنا حدودهم (لا تُطبَّق عليك أنت).</p>
      <div class="gs-form"><label>الحد اليومي للمعلم (إرسالات) <input type="number" id="cs-daily" min="1" max="500"></label>
        <label>أقصى مهام نشطة لكل طالب <input type="number" id="cs-active" min="1" max="20"></label>
        <label>أقصى مستلمين في الإرسال الواحد <input type="number" id="cs-max" min="1" max="1000"></label>
        <button type="button" class="primary" id="cs-save">حفظ</button></div></section>` : ''}
    ${ctx.state?.supabase ? `<section class="card" id="grade-set-card">${ttl('coin', 'الرصيد: استبدال النقاط بدرجات', 'h2', 30)}
      <p class="small muted">يستبدل الطالب نقاط التميّز بدرجات يرصدها المعلم. غيّر القيم هنا متى شئت؛ التغيير يسري على الاستبدالات القادمة فقط.</p>
      <div class="gs-form"><label>نقاط الدرجة الواحدة <input type="number" id="gs-rate" min="1" max="10000"></label>
        <label>السقف الأسبوعي (درجات) <input type="number" id="gs-weekly" min="0" max="50"></label>
        <label>أقصى كوبون للمعلم (نقطة) <input type="number" id="gs-cmax" min="1" max="500"></label>
        <label>حصة المعلم الأسبوعية (نقطة) <input type="number" id="gs-cquota" min="0"></label>
        <label class="st-radio"><input type="checkbox" id="gs-on"> الاستبدال مفعّل</label>
        <label>سبب الإيقاف (يراه الطلاب) <input id="gs-reason" maxlength="120" placeholder="مثال: فترة الاختبارات"></label>
        <button type="button" class="primary" id="gs-save">حفظ</button></div><p id="gs-info" class="small"></p></section>` : ''}
    <section class="card">${ttl('students', 'إضافة طلاب', 'h2', 30)}
      <div class="as-add">
        <div>
          <h3>${icon('upload', 26, 'green')}من ملف Excel</h3>
          <p class="small muted">أعمدة: <b>الاسم، الصف، الشعبة</b>، واختياريًا: اسم المستخدم، كلمة المرور. الصف الأول عناوين الأعمدة.</p>
          <input type="file" id="as-file" accept=".xlsx,.xls,.csv">
          <div class="actions"><button type="button" id="as-template">${line('download', 17)}تحميل نموذج Excel</button></div>
        </div>
        <div>
          <h3>${icon('essay', 26)}أو بالكتابة</h3>
          <p class="small muted">سطر لكل طالب: <b>الاسم، الصف، الشعبة</b>.</p>
          <textarea id="as-lines" rows="4" placeholder="أحمد محمد علي، ثاني ثانوي، 1&#10;سعد خالد، ثاني ثانوي، 2"></textarea>
          <div class="actions"><button type="button" id="as-read-lines">معاينة</button></div>
        </div>
      </div>
      ${courses.length ? `<div class="field as-course"><label for="as-new-course">مقرر الحسابات الجديدة</label>
        <select id="as-new-course">${courseOpts(cur?.id)}</select></div>` : ''}
      <div id="as-preview"></div>
      <div id="as-result"></div>
    </section>
    <section class="card"><div class="as-listhead">${ttl('students', `الطلاب (${list.length}${list.length !== all.length ? ` من ${all.length}` : ''})`)}
      <div class="actions">
        <select id="af-grade" aria-label="الصف"><option value="">كل الصفوف</option>${grades.map(g => `<option ${g === adminFilter.grade ? 'selected' : ''}>${esc(g)}</option>`).join('')}</select>
        <select id="af-sec" aria-label="الشعبة"><option value="">كل الشعب</option>${sections.map(g => `<option ${g === adminFilter.section ? 'selected' : ''}>${esc(g)}</option>`).join('')}</select>
        <input id="af-q" placeholder="بحث بالاسم" value="${esc(adminFilter.q)}" style="max-width:11rem">
        <button type="button" id="as-export">${line('download', 17)}تصدير Excel</button>
      </div></div>
      ${list.length ? `<div class="as-bulk" id="as-bulk">
        <label class="st-radio"><input type="checkbox" id="as-all"> تحديد الكل المعروض (${list.length})</label>
        <span id="as-count" class="muted small">لم يُحدد أحد</span>
        ${courses.length ? `<span class="as-enroll"><select id="as-enroll-course" aria-label="المقرر">${courseOpts(cur?.id)}</select>
          <button type="button" id="as-enroll-add" disabled>إسناد المقرر</button>
          <button type="button" id="as-enroll-set" disabled title="يصبح هذا مقررهم الوحيد؛ سجل تدريبهم السابق يبقى">نقل إليه</button></span>` : ''}
        <button type="button" id="as-del-many" class="danger" disabled>${line('trash', 16)}حذف المحدد</button>
      </div>
      <div class="table-wrap"><table class="list as-table"><thead><tr><th class="as-chk"></th><th>الاسم</th><th>اسم المستخدم</th><th>الصف</th><th>الشعبة</th>${courses.length ? '<th>المقرر</th>' : ''}<th>الحالة</th><th>التدريب</th><th></th></tr></thead><tbody>
        ${list.map(s => `<tr data-id="${s.id}" data-user="${esc(s.username)}">
          <td class="as-chk"><input type="checkbox" class="as-pick" aria-label="تحديد ${esc(s.name)}"></td>
          <td><input class="as-name" value="${esc(s.name)}" aria-label="الاسم"></td>
          <td><input class="as-user ltr" value="${esc(s.username)}" aria-label="اسم المستخدم" style="max-width:9rem"></td>
          <td><input class="as-grade" value="${esc(s.grade || '')}" aria-label="الصف" style="max-width:8rem"></td>
          <td><input class="as-sec" value="${esc(s.section || '')}" aria-label="الشعبة" style="max-width:5rem"></td>
          ${courses.length ? `<td class="small">${(s.courses || []).map(courseName).filter(Boolean).map(esc).join('، ') || '<span class="bad">بلا مقرر</span>'}</td>` : ''}
          <td><select class="as-role" aria-label="الحالة">${Object.entries(ROLE).map(([v, t]) => `<option value="${v}" ${v === s.role ? 'selected' : ''}>${t}</option>`).join('')}</select></td>
          <td class="small">${s.sessions ? `${s.sessions} جلسة · ${pct(s.correct, s.answered)}%` : '—'}</td>
          <td class="actions as-acts"><button type="button" class="as-save">حفظ</button><button type="button" class="as-reset">كلمة المرور</button><button type="button" class="as-del danger">حذف</button></td></tr>`).join('')}
      </tbody></table></div>` : '<div class="empty">لا يوجد طلاب.</div>'}
    </section>`;

  const showPreview = rows => {
    pending = rows;
    const el = document.getElementById('as-preview');
    if (!rows.length) { el.innerHTML = '<p class="notice bad">لم يُعثر على أسماء. تأكد أن العمود الأول للاسم أو أن عنوانه «الاسم».</p>'; return; }
    el.innerHTML = `<h3>معاينة (${rows.length} طالبًا)</h3><div class="table-wrap as-prev"><table class="list"><thead><tr><th>#</th><th>الاسم</th><th>الصف</th><th>الشعبة</th><th>اسم المستخدم</th></tr></thead><tbody>
      ${rows.map((r, i) => `<tr><td>${i + 1}</td><td>${esc(r.name)}</td><td>${esc(r.grade)}</td><td>${esc(r.section)}</td><td class="ltr">${esc(r.username) || '<span class="muted">تلقائي</span>'}</td></tr>`).join('')}
      </tbody></table></div><div class="actions"><button class="primary" id="as-create" type="button">إنشاء ${rows.length} حسابًا</button><button type="button" id="as-cancel">إلغاء</button></div>`;
    document.getElementById('as-cancel').onclick = () => { pending = []; el.innerHTML = ''; };
    document.getElementById('as-create').onclick = e => createAll(e.target);
  };
  const createAll = async btn => {
    if (pending.length > 100) return fail(new Error('الحد الأقصى 100 طالب في المرة الواحدة؛ قسّم الملف'));
    btn.disabled = true; btn.textContent = 'جارٍ الإنشاء…';
    try {
      const { results } = await api('/admin/students/create', { method: 'POST', body: { students: pending } });
      const ok = results.filter(r => r.ok);
      const newCourse = Number(document.getElementById('as-new-course')?.value) || null;
      if (newCourse && ok.length) {
        try { await api('/admin/students/enroll-usernames', { method: 'POST', body: { usernames: ok.map(r => r.username), course: newCourse } }); }
        catch (err) { toast('أُنشئت الحسابات لكن تعذر إسناد المقرر؛ أسنده من القائمة: ' + err.message, true); }
      }
      document.getElementById('as-preview').innerHTML = '';
      document.getElementById('as-result').innerHTML = `
        <p class="notice ${ok.length === results.length ? 'ok' : 'warn'}">أُنشئ ${ok.length} من ${results.length}. احفظ كلمات المرور الآن (Excel أو بطاقات)؛ لا تظهر مرة أخرى.</p>
        <div class="table-wrap"><table class="list" id="as-cards"><thead><tr><th>الاسم</th><th>الصف</th><th>الشعبة</th><th>اسم المستخدم</th><th>كلمة المرور</th></tr></thead><tbody>
        ${results.map(r => r.ok ? `<tr><td>${esc(r.name)}</td><td>${esc(r.grade)}</td><td>${esc(r.section)}</td><td class="ltr"><b>${esc(r.username)}</b></td><td class="ltr"><b>${esc(r.password)}</b></td></tr>`
          : `<tr><td>${esc(r.name)}</td><td colspan="4" class="bad">${esc(r.error)}</td></tr>`).join('')}</tbody></table></div>
        <div class="actions"><button type="button" id="as-cred-xlsx" class="primary">تحميل كلمات المرور Excel</button><button type="button" id="as-print">طباعة بطاقات الدخول</button><button type="button" id="as-refresh">تحديث القائمة</button></div>`;
      document.getElementById('as-cred-xlsx').onclick = () => downloadXlsx('itqan-student-accounts', ['الاسم', 'الصف', 'الشعبة', 'اسم المستخدم', 'كلمة المرور', 'رابط المنصة'],
        ok.map(r => [r.name, r.grade, r.section, r.username, r.password, SITE_URL]));
      document.getElementById('as-print').onclick = () => printCards(ok, esc);
      document.getElementById('as-refresh').onclick = () => pageAdminStudents(ctx).catch(fail);
      document.getElementById('as-lines').value = '';
      document.getElementById('as-file').value = '';
      pending = [];
    } catch (err) { fail(err); btn.disabled = false; btn.textContent = `إنشاء ${pending.length} حسابًا`; }
  };

  document.getElementById('as-file').onchange = async e => {
    const f = e.target.files[0]; if (!f) return;
    try { showPreview(await readStudentFile(f)); } catch (err) { fail(err); }
  };
  document.getElementById('as-read-lines').onclick = () => showPreview(parseStudentLines(document.getElementById('as-lines').value));
  document.getElementById('as-template').onclick = () => downloadXlsx('itqan-students-template', ['الاسم', 'الصف', 'الشعبة', 'اسم المستخدم (اختياري)', 'كلمة المرور (اختياري)'],
    [['أحمد محمد علي', 'ثاني ثانوي', '1', '', ''], ['سعد خالد العتيبي', 'ثاني ثانوي', '2', 'saad22', '']]);
  document.getElementById('as-export').onclick = () => downloadXlsx('itqan-students-list', ['الاسم', 'اسم المستخدم', 'الصف', 'الشعبة', 'الحالة', 'الجلسات', 'الأسئلة', 'نسبة الصحيح', 'آخر نشاط'],
    list.map(s => [s.name, s.username, s.grade || '', s.section || '', ROLE[s.role], s.sessions, s.answered, s.answered ? pct(s.correct, s.answered) + '%' : '',
      s.lastActive ? hijri(s.lastActive) : '']));
  const refilter = () => pageAdminStudents(ctx).catch(fail);
  if (ctx.state?.supabase) {
    const fmtD = d => hijri(d);
    const info = document.getElementById('rank-term-info');
    api('/admin/rank/term').then(t => { info.textContent = `الفصل الحالي بدأ احتساب نقاطه في ${fmtD(t.startedAt)}.`; }).catch(() => { info.textContent = 'يتطلب تحديث قاعدة البيانات (schema.sql).'; });
    const csv = x => { document.getElementById('cs-daily').value = x.daily; document.getElementById('cs-active').value = x.activeTasks; document.getElementById('cs-max').value = x.maxRecipients; };
    api('/admin/comms/settings').then(csv).catch(() => {});
    document.getElementById('cs-save').onclick = async e => {
      const b = e.currentTarget; b.disabled = true;
      try { csv(await api('/admin/comms/settings', { method: 'POST', body: { daily: document.getElementById('cs-daily').value, activeTasks: document.getElementById('cs-active').value, maxRecipients: document.getElementById('cs-max').value } })); toast('حُفظت الحدود'); }
      catch (err) { fail(err); } finally { b.disabled = false; }
    };
    const gi = document.getElementById('gs-info'), gv = x => { document.getElementById('gs-rate').value = x.rate; document.getElementById('gs-weekly').value = x.weeklyCap; document.getElementById('gs-cmax').value = x.couponMax; document.getElementById('gs-cquota').value = x.couponQuota;
      document.getElementById('gs-on').checked = x.enabled; document.getElementById('gs-reason').value = x.reason || ''; };
    api('/admin/grades/settings').then(gv).catch(() => { gi.textContent = 'يتطلب تحديث قاعدة البيانات (schema.sql).'; });
    document.getElementById('gs-save').onclick = async e => {
      const b = e.currentTarget; b.disabled = true;
      try {
        gv(await api('/admin/grades/settings', { method: 'POST', body: { rate: document.getElementById('gs-rate').value, weekly: document.getElementById('gs-weekly').value,
          enabled: document.getElementById('gs-on').checked, reason: document.getElementById('gs-reason').value,
          couponMax: document.getElementById('gs-cmax').value, couponQuota: document.getElementById('gs-cquota').value } }));
        toast('حُفظت إعدادات الرصيد'); gi.textContent = '';
      } catch (err) { fail(err); } finally { b.disabled = false; }
    };
    document.getElementById('rank-new-term').onclick = async e => {
      if (!confirm('ستُصفَّر نقاط التميّز لكل الطلاب ويبدأ احتسابها من الآن. لا يُحذف أي سجل تدريب. هل تريد المتابعة؟')) return;
      const b = e.currentTarget; b.disabled = true;
      try { const t = await api('/admin/rank/term', { method: 'POST', body: {} }); info.textContent = `بدأ فصل جديد في ${fmtD(t.startedAt)}.`; toast('بدأ فصل دراسي جديد'); } catch (err) { fail(err); } finally { b.disabled = false; }
    };
  }
  document.getElementById('af-grade').onchange = e => { adminFilter.grade = e.target.value; adminFilter.section = ''; refilter(); };
  document.getElementById('af-sec').onchange = e => { adminFilter.section = e.target.value; refilter(); };
  document.getElementById('af-q').onchange = e => { adminFilter.q = e.target.value.trim(); refilter(); };

  // تحديد دفعة وحذفها مرة واحدة (التحديد يشمل القائمة المعروضة بعد التصفية فقط)
  const picks = [...$app.querySelectorAll('.as-pick')];
  const allBox = document.getElementById('as-all');
  const syncBulk = () => {
    const n = picks.filter(c => c.checked).length;
    const delBtn = document.getElementById('as-del-many');
    if (!delBtn) return;
    delBtn.disabled = !n;
    ['as-enroll-add', 'as-enroll-set'].forEach(id => { const b = document.getElementById(id); if (b) b.disabled = !n; });
    delBtn.lastChild.textContent = n ? `حذف المحدد (${n})` : 'حذف المحدد';
    document.getElementById('as-count').textContent = n ? `حُدد ${n} من ${picks.length}` : 'لم يُحدد أحد';
    allBox.checked = n === picks.length && n > 0; allBox.indeterminate = n > 0 && n < picks.length;
    picks.forEach(c => c.closest('tr').classList.toggle('picked', c.checked));
  };
  picks.forEach(c => c.onchange = syncBulk);
  if (allBox) {
    allBox.onchange = () => { picks.forEach(c => { c.checked = allBox.checked; }); syncBulk(); };
    const enroll = mode => async e => {
      const btn = e.currentTarget;
      const ids = picks.filter(c => c.checked).map(c => c.closest('tr').dataset.id);
      const course = Number(document.getElementById('as-enroll-course').value);
      if (!ids.length || !course) return;
      if (mode === 'set' && !confirm(`نقل ${ids.length} طالبًا إلى ${courseName(course)} وإلغاء مقرراتهم الأخرى؟ سجل تدريبهم السابق يبقى محفوظًا.`)) return;
      btn.disabled = true;
      try {
        await api('/admin/students/enroll', { method: 'POST', body: { ids, course, mode } });
        toast(`${mode === 'set' ? 'نُقل' : 'أُسند المقرر إلى'} ${ids.length} طالبًا`); refilter();
      } catch (err) { fail(err); btn.disabled = false; }
    };
    const ea = document.getElementById('as-enroll-add'), es = document.getElementById('as-enroll-set');
    if (ea) ea.onclick = enroll('add');
    if (es) es.onclick = enroll('set');
    document.getElementById('as-del-many').onclick = async e => {
      const btn = e.currentTarget;
      const ids = picks.filter(c => c.checked).map(c => c.closest('tr').dataset.id);
      if (!ids.length) return;
      if (!confirm(`حذف ${ids.length} حسابًا نهائيًا مع سجل تدريبهم؟ لا يمكن التراجع.`)) return;
      if (ids.length >= 10 && prompt(`للتأكيد اكتب العدد: ${ids.length}`) !== String(ids.length)) return toast('أُلغي الحذف', true);
      btn.disabled = true;
      try {
        const r = await api('/admin/students/delete-many', { method: 'POST', body: { userIds: ids } });
        toast(`حُذف ${r.deleted} حسابًا` + (r.failed?.length ? `، وتعذر ${r.failed.length}` : ''), !!r.failed?.length);
        refilter();
      } catch (err) { fail(err); btn.disabled = false; }
    };
  }

  $app.querySelectorAll('tr[data-id]').forEach(tr => {
    const id = tr.dataset.id;
    tr.querySelector('.as-save').onclick = async e => {
      const btn = e.currentTarget; if (btn.disabled) return; btn.disabled = true;
      try {
        await api('/admin/students/update', { method: 'POST', body: { id, name: tr.querySelector('.as-name').value,
          grade: tr.querySelector('.as-grade').value, section: tr.querySelector('.as-sec').value, role: tr.querySelector('.as-role').value } });
        const user = tr.querySelector('.as-user').value.trim().toLowerCase();
        if (user !== tr.dataset.user) {
          const r = await api('/admin/students/rename', { method: 'POST', body: { userId: id, username: user } });
          tr.dataset.user = r.username; tr.querySelector('.as-user').value = r.username;
        }
        toast('تم الحفظ');
      } catch (err) { fail(err); } finally { btn.disabled = false; }
    };
    tr.querySelector('.as-reset').onclick = async () => {
      const pw = prompt('اكتب كلمة المرور الجديدة (8 أحرف على الأقل)، أو اتركها فارغة لتوليدها تلقائيًا:', '');
      if (pw === null) return;
      try {
        const { password } = await api('/admin/students/reset', { method: 'POST', body: { userId: id, password: pw.trim() } });
        prompt(`كلمة المرور الجديدة للطالب ${tr.querySelector('.as-name').value} (انسخها الآن):`, password);
      } catch (err) { fail(err); }
    };
    tr.querySelector('.as-del').onclick = async () => {
      const name = tr.querySelector('.as-name').value;
      if (!confirm(`حذف حساب «${name}» نهائيًا مع سجل تدريبه؟ لا يمكن التراجع.`)) return;
      try { await api('/admin/students/delete', { method: 'POST', body: { userId: id } }); toast('حُذف الحساب'); refilter(); } catch (err) { fail(err); }
    };
  });
}
// تبويبا صفحة الحسابات: الطلاب | الفريق (الفريق على Supabase فقط)
const accountTabs = (cur, ctx) => (ctx.state?.supabase ? `<div class="seg no-print" role="tablist" aria-label="نوع الحسابات">
  <a class="btn ${cur === 'students' ? 'on' : ''}" href="#/students" role="tab" aria-selected="${cur === 'students'}">${icon('students', 22)}الطلاب</a>
  <a class="btn ${cur === 'team' ? 'on' : ''}" href="#/team" role="tab" aria-selected="${cur === 'team'}">${icon('team', 22)}الفريق</a></div>` : '');

// ---------- حسابات الفريق: مراجع علمي، مشرف تربوي، مدير المدرسة، معلم ----------
export async function pageAdminTeam(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const all = await api('/admin/team');
  const roleOpts = (cur, withPending = true) => [...STAFF_ROLES.map(([v, t]) => [v, t]), ...(withPending ? [['pending', 'موقوف']] : [])]
    .map(([v, t]) => `<option value="${v}" ${v === cur ? 'selected' : ''}>${t}</option>`).join('');
  const fmt = d => hijri(d);
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('team', 52)}<div><h1>حسابات الفريق</h1><p class="muted">حسابات للمراجعة والاطلاع بأدوار محددة. كل دور يرى ما يخصه فقط، وقاعدة البيانات ترفض ما سواه.</p></div></div>
      ${accountTabs('team', ctx)}</section>
    <section class="card">${ttl('team', 'الأدوار وصلاحياتها')}
      <div class="table-wrap"><table class="list tm-roles"><thead><tr><th>الدور</th><th>ماذا يستطيع</th></tr></thead><tbody>
        <tr><td><b>مالك المشروع</b></td><td>كل شيء: تعديل المحتوى واعتماده، وتنفيذ الملاحظات، وإدارة الحسابات.</td></tr>
        ${STAFF_ROLES.map(([, t, d]) => `<tr><td><b>${t}</b></td><td>${d}</td></tr>`).join('')}
      </tbody></table></div></section>
    <section class="card">${ttl('students', 'إضافة حساب')}
      <form id="tm-form" class="tm-form" novalidate>
        <div class="field"><label for="tm-name">الاسم الظاهر</label><input id="tm-name" required placeholder="مثال: أ. خالد السبيعي"></div>
        <div class="field"><label for="tm-role">الدور</label><select id="tm-role">${roleOpts('reviewer', false)}</select></div>
        <div class="field"><label for="tm-user">اسم المستخدم</label><input id="tm-user" class="ltr" required autocapitalize="none" spellcheck="false" placeholder="مثال: khaled.rev"></div>
        <div class="field"><label for="tm-pass">كلمة المرور (اختياري)</label><input id="tm-pass" class="ltr" placeholder="تُولَّد تلقائيًا إن تُركت فارغة"></div>
        <p class="small muted tm-desc" id="tm-desc"></p>
        <div class="actions"><button type="submit" class="primary" id="tm-create">إنشاء الحساب</button></div>
      </form>
      <div id="tm-result"></div></section>
    <section class="card">${ttl('team', `الحسابات (${all.length})`)}
      <div class="table-wrap"><table class="list"><thead><tr><th>الاسم</th><th>اسم المستخدم</th><th>الدور</th><th>آخر دخول</th><th></th></tr></thead><tbody>
      ${all.map(u => (u.role === 'admin' || u.self) ? `<tr><td>${esc(u.name)}</td><td class="ltr">${esc(u.username)}</td><td>${esc(ROLE_NAMES[u.role])}</td><td class="small">${fmt(u.lastSignIn)}</td><td class="small muted">${u.self ? 'حسابك' : ''}</td></tr>`
        : `<tr data-id="${u.id}" data-user="${esc(u.username)}">
          <td><input class="tm-n" value="${esc(u.name)}" aria-label="الاسم">${u.role === 'viewer' ? `<div class="small muted tm-sum">${u.assignedCourses || 0} مقرر · ${u.assignedStudents || 0} طالب مسند</div>` : ''}</td>
          <td><input class="tm-u ltr" value="${esc(u.username)}" aria-label="اسم المستخدم" style="max-width:10rem"></td>
          <td><select class="tm-r" aria-label="الدور">${roleOpts(u.role)}</select></td>
          <td class="small">${fmt(u.lastSignIn)}</td>
          <td class="actions as-acts"><button type="button" class="tm-save">حفظ</button>${u.role === 'viewer' ? '<button type="button" class="tm-assign-btn" aria-expanded="false">الإسناد</button>' : ''}<button type="button" class="tm-reset">كلمة المرور</button><button type="button" class="tm-del danger">حذف</button></td></tr>`).join('')}
      </tbody></table></div>
      <p class="small muted">«موقوف» يمنع الحساب من رؤية أي محتوى دون حذفه. لا يمكن منح دور «مالك المشروع» من هنا.</p></section>`;
  const reload = () => pageAdminTeam(ctx).catch(fail);
  const desc = () => { document.getElementById('tm-desc').textContent = STAFF_ROLES.find(r => r[0] === document.getElementById('tm-role').value)?.[2] || ''; };
  document.getElementById('tm-role').onchange = desc; desc();
  document.getElementById('tm-form').onsubmit = async e => {
    e.preventDefault();
    const btn = document.getElementById('tm-create'); if (btn.disabled) return;
    const body = { name: document.getElementById('tm-name').value.trim(), role: document.getElementById('tm-role').value,
      username: document.getElementById('tm-user').value.trim().toLowerCase(), password: document.getElementById('tm-pass').value.trim() };
    if (body.name.length < 3) return toast('اكتب الاسم', true);
    if (!body.username) return toast('اكتب اسم المستخدم', true);
    btn.disabled = true;
    try {
      const { results } = await api('/admin/team/create', { method: 'POST', body });
      const r = results[0];
      if (!r?.ok) throw new Error(r?.error || 'تعذر إنشاء الحساب');
      await reload();
      document.getElementById('tm-result').innerHTML = `<div class="notice ok">أُنشئ حساب <b>${esc(r.name)}</b> بدور «${esc(ROLE_NAMES[r.role])}».
        اسم المستخدم: <b class="ltr">${esc(r.username)}</b> · كلمة المرور: <b class="ltr">${esc(r.password)}</b> · الرابط: <span class="ltr">${esc(SITE_URL)}</span>
        <div class="small">احفظ كلمة المرور الآن؛ لا تظهر مرة أخرى.</div></div>`;
    } catch (err) { fail(err); btn.disabled = false; }
  };
  // إسناد المعلم: المقررات التي يراها وطلابه الذين يتابع تقدمهم (يستبدل الإسناد السابق كاملًا)
  async function openAssign(tr, id, btn) {
    const next = tr.nextElementSibling;
    if (next?.classList.contains('tm-assign')) { next.remove(); btn.setAttribute('aria-expanded', 'false'); return; }
    btn.disabled = true;
    let cur, courses, students;
    try { [cur, courses, students] = await Promise.all([api('/admin/team/teacher?id=' + encodeURIComponent(id)), api('/courses'), api('/admin/students')]); }
    finally { btn.disabled = false; }
    students = students.filter(x => x.role === 'student');
    const selC = new Set(cur.courses), selS = new Set(cur.students);
    const grades = [...new Set(students.map(x => x.grade).filter(Boolean))].sort(), sections = [...new Set(students.map(x => x.section).filter(Boolean))].sort();
    const row = document.createElement('tr'); row.className = 'tm-assign';
    row.innerHTML = `<td colspan="5"><div class="tm-assign-box">
      <h3>إسناد «${esc(tr.querySelector('.tm-n').value)}»</h3>
      <fieldset class="tm-courses"><legend>المقررات التي يراها المعلم</legend>
        ${courses.map(c => `<label class="tm-chk"><input type="checkbox" class="tm-c" value="${c.id}" ${selC.has(c.id) ? 'checked' : ''}> ${esc(c.code)}${c.status === 'ready' ? '' : ' <span class="small muted">(قيد الإعداد: لا يظهر له حتى يصير متاحًا)</span>'}</label>`).join('')}
      </fieldset>
      <fieldset class="tm-studs"><legend>الطلاب الذين يتابع تقدمهم (<span class="tm-count">0</span> مسندًا)</legend>
        <div class="as-filters">
          <select class="tm-fg" aria-label="الصف"><option value="">كل الصفوف</option>${grades.map(g => `<option>${esc(g)}</option>`).join('')}</select>
          <select class="tm-fs" aria-label="الشعبة"><option value="">كل الشعب</option>${sections.map(g => `<option>${esc(g)}</option>`).join('')}</select>
          <select class="tm-fc" aria-label="المقرر"><option value="">كل المقررات</option>${courses.map(c => `<option value="${c.id}">${esc(c.code)}</option>`).join('')}</select>
          <input class="tm-fq" type="search" placeholder="بحث بالاسم أو اسم المستخدم" aria-label="بحث">
          <button type="button" class="tm-all">تحديد المعروض</button><button type="button" class="tm-none">إلغاء تحديد المعروض</button></div>
        <div class="tm-pick" role="group" aria-label="الطلاب"></div>
      </fieldset>
      <div class="actions"><button type="button" class="primary tm-asave">حفظ الإسناد</button><button type="button" class="tm-acancel">إغلاق</button></div>
      <p class="small muted">المعلم يرى مقرراته الجاهزة فقط، وتقدم طلابه المسندين له على تلك المقررات فقط. التغيير يسري عند دخوله التالي.</p></div></td>`;
    tr.after(row); btn.setAttribute('aria-expanded', 'true');
    const $ = q => row.querySelector(q);
    const shown = () => {
      const g = $('.tm-fg').value, sec = $('.tm-fs').value, c = Number($('.tm-fc').value) || 0, q = $('.tm-fq').value.trim().toLowerCase();
      return students.filter(x => (!g || x.grade === g) && (!sec || x.section === sec) && (!c || (x.courses || []).includes(c))
        && (!q || x.name.toLowerCase().includes(q) || x.username.toLowerCase().includes(q)));
    };
    const draw = () => {
      const list = shown();
      $('.tm-pick').innerHTML = list.length ? list.map(x => `<label class="tm-chk"><input type="checkbox" class="tm-s" value="${x.id}" ${selS.has(x.id) ? 'checked' : ''}>
        ${esc(x.name)} <span class="small muted">${esc([x.grade, x.section].filter(Boolean).join(' · '))}</span> <span class="small muted ltr">${esc(x.username)}</span></label>`).join('')
        : '<div class="empty">لا يوجد طلاب مطابقون.</div>';
      $('.tm-count').textContent = selS.size;
    };
    row.addEventListener('change', e => {
      if (e.target.classList.contains('tm-s')) { e.target.checked ? selS.add(e.target.value) : selS.delete(e.target.value); $('.tm-count').textContent = selS.size; }
      else if (e.target.classList.contains('tm-c')) { const v = Number(e.target.value); e.target.checked ? selC.add(v) : selC.delete(v); }
      else if (e.target.matches('.tm-fg, .tm-fs, .tm-fc')) draw();
    });
    $('.tm-fq').oninput = draw;
    $('.tm-all').onclick = () => { shown().forEach(x => selS.add(x.id)); draw(); };
    $('.tm-none').onclick = () => { shown().forEach(x => selS.delete(x.id)); draw(); };
    $('.tm-acancel').onclick = () => { row.remove(); btn.setAttribute('aria-expanded', 'false'); };
    $('.tm-asave').onclick = async e => {
      const b = e.currentTarget; if (b.disabled) return; b.disabled = true;
      try {
        const r = await api('/admin/team/teacher', { method: 'POST', body: { id, courses: [...selC], students: [...selS] } });
        tr.querySelector('.tm-sum').textContent = `${r.courses} مقرر · ${r.students} طالب مسند`;
        toast('تم حفظ الإسناد'); row.remove(); btn.setAttribute('aria-expanded', 'false');
      } catch (err) { fail(err); b.disabled = false; }
    };
    draw();
  }
  $app.querySelectorAll('tr[data-id]').forEach(tr => {
    const id = tr.dataset.id;
    tr.querySelector('.tm-save').onclick = async e => {
      const btn = e.currentTarget; if (btn.disabled) return; btn.disabled = true;
      try {
        await api('/admin/team/update', { method: 'POST', body: { id, name: tr.querySelector('.tm-n').value, role: tr.querySelector('.tm-r').value } });
        const user = tr.querySelector('.tm-u').value.trim().toLowerCase();
        if (user !== tr.dataset.user) {
          const r = await api('/admin/students/rename', { method: 'POST', body: { userId: id, username: user } });
          tr.dataset.user = r.username; tr.querySelector('.tm-u').value = r.username;
        }
        toast('تم الحفظ');
      } catch (err) { fail(err); } finally { btn.disabled = false; }
    };
    tr.querySelector('.tm-assign-btn')?.addEventListener('click', e => openAssign(tr, id, e.currentTarget).catch(fail));
    tr.querySelector('.tm-reset').onclick = async () => {
      const pw = prompt('اكتب كلمة المرور الجديدة (8 أحرف على الأقل)، أو اتركها فارغة لتوليدها تلقائيًا:', '');
      if (pw === null) return;
      try {
        const { password } = await api('/admin/students/reset', { method: 'POST', body: { userId: id, password: pw.trim() } });
        prompt(`كلمة المرور الجديدة لـ ${tr.querySelector('.tm-n').value} (انسخها الآن):`, password);
      } catch (err) { fail(err); }
    };
    tr.querySelector('.tm-del').onclick = async () => {
      if (!confirm(`حذف حساب «${tr.querySelector('.tm-n').value}» نهائيًا؟ تبقى ملاحظاته وتعديلاته محفوظة باسمه.`)) return;
      try { await api('/admin/students/delete', { method: 'POST', body: { userId: id } }); toast('حُذف الحساب'); reload(); } catch (err) { fail(err); }
    };
  });
}

// بطاقات دخول للطباعة: اسم الطالب واسم المستخدم وكلمة المرور ورابط الموقع.
function printCards(rows, esc) {
  const w = window.open('', '_blank');
  if (!w) { alert('تعذر فتح نافذة الطباعة: اسمح بالنوافذ المنبثقة لهذا الموقع ثم أعد المحاولة، أو حمّل ملف Excel.'); return; }
  const url = SITE_URL;
  w.document.write(`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>بطاقات دخول الطلاب</title>
    <style>body{font-family:system-ui,sans-serif;margin:12mm}.g{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
    .c{border:1px dashed #555;border-radius:8px;padding:5mm;break-inside:avoid}.c h3{margin:0 0 2mm}.l{direction:ltr;text-align:right;font-family:monospace;font-size:14pt}
    small{color:#555}</style></head><body><div class="g">${rows.map(r => `<div class="c"><h3>${esc(r.name)}</h3><small>${r.grade ? 'الصف: ' + esc(r.grade) + ' · ' : ''}الشعبة: ${esc(r.section || '—')}</small>
    <p>اسم المستخدم: <span class="l">${esc(r.username)}</span><br>كلمة المرور: <span class="l">${esc(r.password)}</span></p>
    <small>${esc(url)}</small></div>`).join('')}</div><script>print()</script></body></html>`);
  w.document.close();
}
