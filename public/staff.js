// صفحات الطاقم للطلاب: لوحة تقدم الطلاب (للمعلمين والمراجعين والمشرف) وإدارة حسابات الطلاب (للمشرف فقط).
import { icon, line } from './icons.js';

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
      </tbody></table></div>` : '<div class="empty">لا يوجد طلاب بعد.</div>'}
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

const COLS = [
  ['name', /اسم الطالب|^الاسم|^اسم$|name/i],
  ['grade', /الصف|grade/i],
  ['section', /الشعبة|^الفصل|section|class/i],
  ['username', /اسم المستخدم|المستخدم|user/i],
  ['password', /كلمة المرور|password/i],
];
// يحوّل صفوف الجدول إلى طلاب: يتعرف على الأعمدة من عناوينها، وإلا يفترض الترتيب: الاسم، الصف، الشعبة، اسم المستخدم، كلمة المرور.
export function rowsToStudents(rows) {
  rows = rows.map(r => r.map(c => String(c ?? '').trim())).filter(r => r.some(Boolean));
  if (!rows.length) return [];
  const head = rows[0];
  const map = {};
  head.forEach((h, i) => { const hit = COLS.find(([k, re]) => !(k in map) && re.test(h)); if (hit) map[hit[0]] = i; });
  const hasHeader = 'name' in map;
  const idx = hasHeader ? map : { name: 0, grade: 1, section: 2, username: 3, password: 4 };
  return (hasHeader ? rows.slice(1) : rows).map(r => Object.fromEntries(COLS.map(([k]) => [k, idx[k] != null ? r[idx[k]] || '' : ''])))
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
    else if (ch === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
    else if (ch !== '\r') cell += ch;
  }
  row.push(cell); rows.push(row);
  return rows;
}
async function readStudentFile(file) {
  if (/\.csv$/i.test(file.name)) return rowsToStudents(parseCsv(await file.text()));
  const XLSX = await loadXlsx();
  const wb = XLSX.read(await file.arrayBuffer(), { type: 'array' });
  return rowsToStudents(XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' }));
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
    const cell = v => { const t = String(v ?? ''); return /[",\n]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t; };
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

export async function pageAdminStudents(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const all = await api('/admin/students');
  const grades = [...new Set(all.map(s => s.grade).filter(Boolean))].sort();
  const sections = [...new Set(all.filter(s => !adminFilter.grade || s.grade === adminFilter.grade).map(s => s.section).filter(Boolean))].sort();
  const list = all.filter(s => (!adminFilter.grade || s.grade === adminFilter.grade) && (!adminFilter.section || s.section === adminFilter.section)
    && (!adminFilter.q || (s.name + ' ' + s.username).includes(adminFilter.q)));
  let pending = [];
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('students', 52)}<div><h1>حسابات الطلاب</h1><p class="muted">الطالب يرى صفحة التدريب فقط: لا إجابات جماعية ولا مراجعة ولا منشئ اختبارات.</p></div></div></section>
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
      ${list.length ? `<div class="table-wrap"><table class="list as-table"><thead><tr><th>الاسم</th><th>اسم المستخدم</th><th>الصف</th><th>الشعبة</th><th>الحالة</th><th>التدريب</th><th></th></tr></thead><tbody>
        ${list.map(s => `<tr data-id="${s.id}" data-user="${esc(s.username)}">
          <td><input class="as-name" value="${esc(s.name)}" aria-label="الاسم"></td>
          <td><input class="as-user ltr" value="${esc(s.username)}" aria-label="اسم المستخدم" style="max-width:9rem"></td>
          <td><input class="as-grade" value="${esc(s.grade || '')}" aria-label="الصف" style="max-width:8rem"></td>
          <td><input class="as-sec" value="${esc(s.section || '')}" aria-label="الشعبة" style="max-width:5rem"></td>
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
      document.getElementById('as-preview').innerHTML = '';
      document.getElementById('as-result').innerHTML = `
        <p class="notice ${ok.length === results.length ? 'ok' : 'warn'}">أُنشئ ${ok.length} من ${results.length}. احفظ كلمات المرور الآن (Excel أو بطاقات)؛ لا تظهر مرة أخرى.</p>
        <div class="table-wrap"><table class="list" id="as-cards"><thead><tr><th>الاسم</th><th>الصف</th><th>الشعبة</th><th>اسم المستخدم</th><th>كلمة المرور</th></tr></thead><tbody>
        ${results.map(r => r.ok ? `<tr><td>${esc(r.name)}</td><td>${esc(r.grade)}</td><td>${esc(r.section)}</td><td class="ltr"><b>${esc(r.username)}</b></td><td class="ltr"><b>${esc(r.password)}</b></td></tr>`
          : `<tr><td>${esc(r.name)}</td><td colspan="4" class="bad">${esc(r.error)}</td></tr>`).join('')}</tbody></table></div>
        <div class="actions"><button type="button" id="as-cred-xlsx" class="primary">تحميل كلمات المرور Excel</button><button type="button" id="as-print">طباعة بطاقات الدخول</button><button type="button" id="as-refresh">تحديث القائمة</button></div>`;
      document.getElementById('as-cred-xlsx').onclick = () => downloadXlsx('حسابات-الطلاب', ['الاسم', 'الصف', 'الشعبة', 'اسم المستخدم', 'كلمة المرور'],
        ok.map(r => [r.name, r.grade, r.section, r.username, r.password]));
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
  document.getElementById('as-template').onclick = () => downloadXlsx('نموذج-أسماء-الطلاب', ['الاسم', 'الصف', 'الشعبة', 'اسم المستخدم (اختياري)', 'كلمة المرور (اختياري)'],
    [['أحمد محمد علي', 'ثاني ثانوي', '1', '', ''], ['سعد خالد العتيبي', 'ثاني ثانوي', '2', 'saad22', '']]);
  document.getElementById('as-export').onclick = () => downloadXlsx('قائمة-الطلاب', ['الاسم', 'اسم المستخدم', 'الصف', 'الشعبة', 'الحالة', 'الجلسات', 'الأسئلة', 'نسبة الصحيح', 'آخر نشاط'],
    list.map(s => [s.name, s.username, s.grade || '', s.section || '', ROLE[s.role], s.sessions, s.answered, s.answered ? pct(s.correct, s.answered) + '%' : '',
      s.lastActive ? new Date(s.lastActive).toLocaleDateString('ar-SA-u-nu-latn') : '']));
  const refilter = () => pageAdminStudents(ctx).catch(fail);
  document.getElementById('af-grade').onchange = e => { adminFilter.grade = e.target.value; adminFilter.section = ''; refilter(); };
  document.getElementById('af-sec').onchange = e => { adminFilter.section = e.target.value; refilter(); };
  document.getElementById('af-q').onchange = e => { adminFilter.q = e.target.value.trim(); refilter(); };

  $app.querySelectorAll('tr[data-id]').forEach(tr => {
    const id = tr.dataset.id;
    tr.querySelector('.as-save').onclick = async () => {
      try {
        await api('/admin/students/update', { method: 'POST', body: { id, name: tr.querySelector('.as-name').value,
          grade: tr.querySelector('.as-grade').value, section: tr.querySelector('.as-sec').value, role: tr.querySelector('.as-role').value } });
        const user = tr.querySelector('.as-user').value.trim().toLowerCase();
        if (user !== tr.dataset.user) {
          const r = await api('/admin/students/rename', { method: 'POST', body: { userId: id, username: user } });
          tr.dataset.user = r.username; tr.querySelector('.as-user').value = r.username;
        }
        toast('تم الحفظ');
      } catch (err) { fail(err); }
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
// بطاقات دخول للطباعة: اسم الطالب واسم المستخدم وكلمة المرور ورابط الموقع.
function printCards(rows, esc) {
  const w = window.open('', '_blank');
  if (!w) return;
  const url = location.href.split('#')[0];
  w.document.write(`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>بطاقات دخول الطلاب</title>
    <style>body{font-family:system-ui,sans-serif;margin:12mm}.g{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
    .c{border:1px dashed #555;border-radius:8px;padding:5mm;break-inside:avoid}.c h3{margin:0 0 2mm}.l{direction:ltr;text-align:right;font-family:monospace;font-size:14pt}
    small{color:#555}</style></head><body><div class="g">${rows.map(r => `<div class="c"><h3>${esc(r.name)}</h3><small>${r.grade ? 'الصف: ' + esc(r.grade) + ' · ' : ''}الشعبة: ${esc(r.section || '—')}</small>
    <p>اسم المستخدم: <span class="l">${esc(r.username)}</span><br>كلمة المرور: <span class="l">${esc(r.password)}</span></p>
    <small>${esc(url)}</small></div>`).join('')}</div><script>print()</script></body></html>`);
  w.document.close();
}
