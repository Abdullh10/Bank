// صفحات الطاقم للطلاب: لوحة تقدم الطلاب (للمعلمين والمراجعين والمشرف) وإدارة حسابات الطلاب (للمشرف فقط).
import { icon, line } from './icons.js';
import { SITE_URL } from './config.js';
import { ROLE_NAMES, STAFF_ROLES } from './roles.js';

const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
const ttl = (ic, html, tag = 'h2', size = 30) => `<${tag} class="ttl">${icon(ic, size)}<span>${html}</span></${tag}>`;
const ROLE = { student: 'نشط', pending: 'موقوف' };

export async function pageTeacherProgress(ctx, section = '') {
  const { esc, $app, api } = ctx;
  const d = await api('/teacher/progress' + (section ? '?section=' + encodeURIComponent(section) : ''));
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('progress', 52)}<div><h1>تقدم الطلاب</h1><p class="muted">نتائج التدريب الذاتي (لا تدخل في الدرجات).</p></div></div>
      <div class="actions"><label for="tp-sec" class="small">الشعبة</label>
        <select id="tp-sec"><option value="">كل الشعب</option>${d.sections.map(s => `<option ${s === section ? 'selected' : ''}>${esc(s)}</option>`).join('')}</select></div></section>
    <section class="card">${ttl('students', 'الطلاب')}
      ${d.students.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الطالب</th><th>الصف</th><th>الشعبة</th><th>الجلسات</th><th>الأسئلة</th><th>الإجابات الصحيحة</th><th>آخر نشاط</th></tr></thead><tbody>
        ${d.students.map(s => `<tr><td>${esc(s.name)} <span class="small muted ltr">${esc(s.username)}</span></td><td>${esc(s.grade || '—')}</td><td>${esc(s.section || '—')}</td>
          <td>${s.sessions}</td><td>${s.answered}</td><td>${s.answered ? pct(s.correct, s.answered) + '%' : '—'}</td>
          <td class="ltr small">${s.lastActive ? esc(new Date(s.lastActive).toLocaleDateString('ar-SA-u-nu-latn')) : '—'}</td></tr>`).join('')}
      </tbody></table></div>` : `<div class="empty">${ctx.state?.user?.role === 'viewer' ? 'لا يوجد طلاب مسندون لك على هذا المقرر بعد؛ يسندهم لك مالك المشروع.' : 'لا يوجد طلاب بعد.'}</div>`}
    </section>
    <section class="card">${ttl('objectives', 'الأهداف الأضعف')}
      <p class="small muted">أهداف أُجيب عن 5 أسئلة منها على الأقل، مرتبة من الأقل نسبة صحيحة.</p>
      ${d.weakObjectives.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الهدف</th><th>الدرس</th><th>الإجابات</th><th>الصحيحة</th></tr></thead><tbody>
        ${d.weakObjectives.map(o => `<tr><td><a href="#/objective/${encodeURIComponent(o.code)}">${esc(o.text)}</a></td><td>${esc(o.lesson)}</td><td>${o.n}</td><td>${o.pct}%</td></tr>`).join('')}
      </tbody></table></div>` : '<div class="empty">لا توجد بيانات كافية بعد.</div>'}
    </section>`;
  document.getElementById('tp-sec').onchange = e => pageTeacherProgress(ctx, e.target.value).catch(ctx.fail);
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
      s.lastActive ? new Date(s.lastActive).toLocaleDateString('ar-SA-u-nu-latn') : '']));
  const refilter = () => pageAdminStudents(ctx).catch(fail);
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
  const fmt = d => (d ? new Date(d).toLocaleDateString('ar-SA-u-nu-latn') : '—');
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
