// صفحات الطاقم للطلاب: لوحة تقدم الطلاب (للمعلمين والمراجعين والمشرف) وإدارة حسابات الطلاب (للمشرف فقط).
const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
const ROLE = { student: 'نشط', pending: 'موقوف' };

export async function pageTeacherProgress(ctx, section = '') {
  const { esc, $app, api } = ctx;
  const d = await api('/teacher/progress' + (section ? '?section=' + encodeURIComponent(section) : ''));
  $app.innerHTML = `
    <section class="hero"><div><h1>تقدم الطلاب</h1><p class="muted">نتائج التدريب الذاتي (لا تدخل في الدرجات).</p></div>
      <div class="actions"><label for="tp-sec" class="small">الشعبة</label>
        <select id="tp-sec"><option value="">كل الشعب</option>${d.sections.map(s => `<option ${s === section ? 'selected' : ''}>${esc(s)}</option>`).join('')}</select></div></section>
    <section class="card"><h2>الطلاب</h2>
      ${d.students.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الطالب</th><th>الشعبة</th><th>الجلسات</th><th>الأسئلة</th><th>الإجابات الصحيحة</th><th>آخر نشاط</th></tr></thead><tbody>
        ${d.students.map(s => `<tr><td>${esc(s.name)} <span class="small muted ltr">${esc(s.username)}</span></td><td>${esc(s.section || '—')}</td>
          <td>${s.sessions}</td><td>${s.answered}</td><td>${s.answered ? pct(s.correct, s.answered) + '%' : '—'}</td>
          <td class="ltr small">${s.lastActive ? esc(new Date(s.lastActive).toLocaleDateString('ar-SA-u-nu-latn')) : '—'}</td></tr>`).join('')}
      </tbody></table></div>` : '<div class="empty">لا يوجد طلاب بعد.</div>'}
    </section>
    <section class="card"><h2>الأهداف الأضعف</h2>
      <p class="small muted">أهداف أُجيب عن 5 أسئلة منها على الأقل، مرتبة من الأقل نسبة صحيحة.</p>
      ${d.weakObjectives.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الهدف</th><th>الدرس</th><th>الإجابات</th><th>الصحيحة</th></tr></thead><tbody>
        ${d.weakObjectives.map(o => `<tr><td><a href="#/objective/${encodeURIComponent(o.code)}">${esc(o.text)}</a></td><td>${esc(o.lesson)}</td><td>${o.n}</td><td>${o.pct}%</td></tr>`).join('')}
      </tbody></table></div>` : '<div class="empty">لا توجد بيانات كافية بعد.</div>'}
    </section>`;
  document.getElementById('tp-sec').onchange = e => pageTeacherProgress(ctx, e.target.value).catch(ctx.fail);
}

// سطر لكل طالب: «الاسم، الشعبة» أو «الاسم، الشعبة، اسم المستخدم». الفاصل فاصلة عربية أو إنجليزية أو Tab.
export function parseStudentLines(text) {
  return String(text || '').split(/\r?\n/).map(l => l.trim()).filter(Boolean)
    .map(l => { const [name = '', section = '', username = ''] = l.split(/\s*[,،\t]\s*/); return { name, section, username }; });
}

export async function pageAdminStudents(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const list = await api('/admin/students');
  $app.innerHTML = `
    <section class="hero"><div><h1>حسابات الطلاب</h1><p class="muted">الطالب يرى صفحة التدريب فقط: لا إجابات جماعية ولا مراجعة ولا منشئ اختبارات.</p></div></section>
    <section class="card"><h2>إضافة طلاب</h2>
      <p class="small muted">سطر لكل طالب: <b>الاسم، الشعبة</b>. يمكن إضافة اسم مستخدم ثالثًا (حروف إنجليزية صغيرة وأرقام)، وإلا يُولَّد تلقائيًا. كلمات المرور تُولَّد وتظهر مرة واحدة فقط.</p>
      <textarea id="as-lines" rows="5" placeholder="أحمد محمد علي، 2/1&#10;سعد خالد، 2/2، saad22"></textarea>
      <div class="actions"><button class="primary" id="as-create" type="button">إنشاء الحسابات</button></div>
      <div id="as-result"></div>
    </section>
    <section class="card"><h2>الطلاب (${list.length})</h2>
      ${list.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>الاسم</th><th>اسم المستخدم</th><th>الشعبة</th><th>الحالة</th><th></th></tr></thead><tbody>
        ${list.map(s => `<tr data-id="${s.id}">
          <td><input class="as-name" value="${esc(s.name)}" aria-label="الاسم"></td>
          <td class="ltr">${esc(s.username)}</td>
          <td><input class="as-sec" value="${esc(s.section || '')}" aria-label="الشعبة" style="max-width:7rem"></td>
          <td><select class="as-role" aria-label="الحالة">${Object.entries(ROLE).map(([v, t]) => `<option value="${v}" ${v === s.role ? 'selected' : ''}>${t}</option>`).join('')}</select></td>
          <td class="actions"><button type="button" class="as-save">حفظ</button><button type="button" class="as-reset">كلمة مرور جديدة</button></td></tr>`).join('')}
      </tbody></table></div>` : '<div class="empty">لا يوجد طلاب بعد.</div>'}
    </section>`;

  document.getElementById('as-create').onclick = async e => {
    const students = parseStudentLines(document.getElementById('as-lines').value);
    if (!students.length) return fail(new Error('اكتب سطرًا واحدًا على الأقل'));
    e.target.disabled = true; e.target.textContent = 'جارٍ الإنشاء…';
    try {
      const { results } = await api('/admin/students/create', { method: 'POST', body: { students } });
      const ok = results.filter(r => r.ok);
      document.getElementById('as-result').innerHTML = `
        <p class="notice ${ok.length === results.length ? 'ok' : 'warn'}">أُنشئ ${ok.length} من ${results.length}. احفظ كلمات المرور الآن؛ لا تظهر مرة أخرى.</p>
        <div class="table-wrap"><table class="list" id="as-cards"><thead><tr><th>الاسم</th><th>الشعبة</th><th>اسم المستخدم</th><th>كلمة المرور</th></tr></thead><tbody>
        ${results.map(r => r.ok ? `<tr><td>${esc(r.name)}</td><td>${esc(r.section)}</td><td class="ltr"><b>${esc(r.username)}</b></td><td class="ltr"><b>${esc(r.password)}</b></td></tr>`
          : `<tr><td>${esc(r.name)}</td><td colspan="3" class="bad">${esc(r.error)}</td></tr>`).join('')}</tbody></table></div>
        <div class="actions"><button type="button" id="as-print">طباعة بطاقات الدخول</button></div>`;
      document.getElementById('as-print').onclick = () => printCards(ok, esc);
      document.getElementById('as-lines').value = '';
    } catch (err) { fail(err); } finally { e.target.disabled = false; e.target.textContent = 'إنشاء الحسابات'; }
  };
  $app.querySelectorAll('tr[data-id]').forEach(tr => {
    tr.querySelector('.as-save').onclick = async () => {
      try {
        await api('/admin/students/update', { method: 'POST', body: { id: tr.dataset.id, name: tr.querySelector('.as-name').value,
          section: tr.querySelector('.as-sec').value, role: tr.querySelector('.as-role').value } });
        toast('تم الحفظ');
      } catch (err) { fail(err); }
    };
    tr.querySelector('.as-reset').onclick = async () => {
      if (!confirm('إنشاء كلمة مرور جديدة لهذا الطالب؟ تتوقف كلمة المرور القديمة.')) return;
      try {
        const { password } = await api('/admin/students/reset', { method: 'POST', body: { userId: tr.dataset.id } });
        prompt('كلمة المرور الجديدة (انسخها الآن):', password);
      } catch (err) { fail(err); }
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
    small{color:#555}</style></head><body><div class="g">${rows.map(r => `<div class="c"><h3>${esc(r.name)}</h3><small>الشعبة: ${esc(r.section || '—')}</small>
    <p>اسم المستخدم: <span class="l">${esc(r.username)}</span><br>كلمة المرور: <span class="l">${esc(r.password)}</span></p>
    <small>${esc(url)}</small></div>`).join('')}</div><script>print()</script></body></html>`);
  w.document.close();
}
