// لوحة المؤشرات: أرقام مجمّعة من قاعدة البيانات (لا أسماء طلاب) لكل حسابات الفريق، ومنها مدير المدرسة والمشرف التربوي.
// الرسوم من HTML وCSS فقط: سلسلة واحدة بلون المنصة، وقيمة مكتوبة على كل عمود، وتلميح عند المرور أو التركيز.
import { icon, line } from './icons.js';

const pct = (a, b) => (b ? Math.round((100 * (a || 0)) / b) : 0);
const num = n => Number(n || 0).toLocaleString('ar-SA-u-nu-latn');
const GROUPS = [['basic', 'تذكر وفهم'], ['apply', 'تطبيق'], ['higher', 'تفكير عليا (تحليل وتقويم وإبداع)']];

const tile = (esc, value, label, ic, sub = '') => `<div class="card">${icon(ic, 46)}<div class="value">${esc(value)}</div>
  <div class="label">${esc(label)}${sub ? `<span class="small muted d-sub">${esc(sub)}</span>` : ''}</div></div>`;

// أعمدة رأسية (النشاط الأسبوعي)
function columns(esc, rows, { value, label, tip }) {
  const max = Math.max(1, ...rows.map(value));
  return `<div class="d-cols" role="list">${rows.map(r => {
    const v = value(r), h = v ? Math.max(3, Math.round((100 * v) / max)) : 0;
    return `<div class="d-col" role="listitem" tabindex="0" data-tip="${esc(tip(r))}">
      <span class="d-val">${v ? num(v) : '—'}</span>
      <span class="d-track"><span class="d-fill" style="height:${h}%"></span></span>
      <span class="d-lab">${esc(label(r))}</span></div>`;
  }).join('')}</div>`;
}

// أشرطة أفقية بنسبة مئوية (المشاركة، الإجابات الصحيحة)
function hbars(esc, rows, { label, value, text, tip }) {
  return `<div class="d-bars" role="list">${rows.map(r => {
    const v = value(r);
    return `<div class="d-bar" role="listitem" tabindex="0" data-tip="${esc(tip(r))}">
      <span class="d-blab">${esc(label(r))}</span>
      <span class="d-btrack"><span class="d-bfill" style="width:${v == null ? 0 : Math.max(v ? 2 : 0, v)}%"></span></span>
      <span class="d-bval">${esc(text(r))}</span></div>`;
  }).join('')}</div>`;
}

// شريط مكدّس 100% لمستويات التفكير (ترتيبية: درجات لون واحد من الفاتح إلى الداكن) مع مفتاح يذكر العدد والنسبة
function stack(esc, parts, total) {
  return `<div class="d-stack" role="img" aria-label="${esc(parts.map(p => `${p.label}: ${pct(p.n, total)}%`).join('، '))}">
      ${parts.filter(p => p.n).map((p, i) => `<span class="d-seg d-seq-${p.i}" style="flex-grow:${p.n}" tabindex="0" data-tip="${esc(`${p.label}: ${num(p.n)} سؤالًا (${pct(p.n, total)}%)`)}"></span>`).join('')}
    </div>
    <ul class="d-legend">${parts.map(p => `<li><span class="d-sw d-seq-${p.i}"></span>${esc(p.label)} <b>${pct(p.n, total)}%</b> <span class="muted small">(${num(p.n)})</span></li>`).join('')}</ul>`;
}

let tipEl = null;
function bindTips(root) {
  tipEl ||= Object.assign(document.createElement('div'), { className: 'd-tip', role: 'tooltip' });
  if (!tipEl.isConnected) document.body.append(tipEl);
  const show = el => {
    tipEl.textContent = el.dataset.tip; tipEl.hidden = false;
    const r = el.getBoundingClientRect(), t = tipEl.getBoundingClientRect();
    const x = Math.min(window.innerWidth - t.width - 8, Math.max(8, r.left + r.width / 2 - t.width / 2));
    const y = r.top - t.height - 8 < 8 ? r.bottom + 8 : r.top - t.height - 8;
    tipEl.style.left = x + 'px'; tipEl.style.top = y + 'px';
  };
  const hide = () => { tipEl.hidden = true; };
  hide();
  root.querySelectorAll('[data-tip]').forEach(el => {
    el.addEventListener('pointerenter', () => show(el));
    el.addEventListener('pointerleave', hide);
    el.addEventListener('focus', () => show(el));
    el.addEventListener('blur', hide);
  });
  window.addEventListener('scroll', hide, { passive: true, once: true });
}

export async function pageDashboard(ctx) {
  const { api, esc, $app, can, ttl } = ctx;
  const d = await api('/dashboard');
  const b = d.bank, o = b.objectives, q = b.questions, st = d.students, pr = d.practice;
  const levels = GROUPS.map(([g, label], i) => ({ i: i + 1, label, n: d.questionLevels.find(x => x.group === g)?.n || 0 }));
  const lvTotal = levels.reduce((s, x) => s + x.n, 0);
  const wkLabel = w => { const [, m, day] = w.week.split('-'); return `${Number(day)}/${Number(m)}`; };
  const hasPractice = pr.answers > 0;

  $app.innerHTML = `<div class="crumbs"><a href="#/">الرئيسية</a> ‹ لوحة المؤشرات</div>
    <div class="hero"><div class="hero-ic">${icon('reports', 52)}<div><h1>لوحة المؤشرات</h1>
      <p class="muted">أرقام مجمّعة تُحسب لحظيًا من قاعدة البيانات، دون أسماء الطلاب. آخر تحديث: ${esc(new Date(d.generatedAt).toLocaleString('ar-SA-u-nu-latn', { dateStyle: 'medium', timeStyle: 'short' }))}</p></div></div>
      <div class="actions no-print"><button type="button" id="d-refresh">${line('clock', 17)}تحديث</button><button type="button" id="d-print">${line('print', 17)}طباعة</button></div></div>

    <h2 class="d-h">${icon('bank', 30)}بنك الأسئلة</h2>
    <div class="grid kpi">
      ${tile(esc, num(q.n), 'سؤالًا في البنك', 'bank', `${num(q.mcq)} اختيار · ${num(q.essay)} مقالي`)}
      ${tile(esc, pct(q.approved, q.n) + '%', 'من الأسئلة معتمدة', 'check', `${num(q.approved)} سؤالًا`)}
      ${tile(esc, num(o.n), 'هدفًا تعليميًا', 'objectives', `${pct(o.approved, o.n)}% معتمدة`)}
      ${tile(esc, `${b.chapters} / ${b.lessons}`, 'فصول / دروس', 'chapters')}
    </div>
    <div class="grid cards d-grid">
      <section class="card">${ttl('pie', 'مستويات التفكير في الأسئلة', 'h3', 28)}
        <p class="small muted">توزيع أسئلة البنك على مستويات التفكير.</p>${stack(esc, levels, lvTotal)}</section>
      <section class="card">${ttl('shield', 'اكتمال المراجعة والاعتماد', 'h3', 28)}
        ${hbars(esc, [
          { l: 'الأهداف المعتمدة', a: o.approved, t: o.n },
          { l: 'الأسئلة المعتمدة', a: q.approved, t: q.n },
          { l: 'المحتوى المكمّل المعتمد', a: b.supplements.approved, t: b.supplements.n },
          { l: 'أهداف اكتملت أسئلتها', a: b.coverage.complete, t: o.n },
        ], { label: r => r.l, value: r => pct(r.a, r.t), text: r => pct(r.a, r.t) + '%', tip: r => `${r.l}: ${num(r.a)} من ${num(r.t)}` })}
      </section>
    </div>

    <h2 class="d-h">${icon('students', 30)}التدريب الذاتي للطلاب</h2>
    <div class="grid kpi">
      ${tile(esc, num(st.n), 'حساب طالب', 'students', `${num(st.confirmed)} أكّدوا بياناتهم`)}
      ${tile(esc, pct(st.active, st.n) + '%', 'تدرّبوا مرة على الأقل', 'practice', `${num(st.active)} طالبًا`)}
      ${tile(esc, num(st.active7), 'طالبًا نشطًا هذا الأسبوع', 'progress', `${num(pr.answers7)} إجابة في 7 أيام`)}
      ${tile(esc, num(pr.answers), 'إجابة بتغذية راجعة فورية', 'mcq', `${num(pr.sessions)} جلسة تدريب`)}
      ${tile(esc, hasPractice ? pct(pr.correct, pr.answers) + '%' : '—', 'نسبة الإجابات الصحيحة', 'trophy')}
    </div>
    ${hasPractice || st.n ? `<div class="grid cards d-grid">
      <section class="card d-wide">${ttl('history', 'النشاط الأسبوعي: عدد الإجابات', 'h3', 28)}
        <p class="small muted">آخر 8 أسابيع (يبدأ الأسبوع يوم الاثنين). مرّر على العمود لعدد الطلاب ونسبة الصحيح.</p>
        ${columns(esc, d.weekly, { value: r => r.answers, label: wkLabel,
          tip: r => `أسبوع ${wkLabel(r)}: ${num(r.answers)} إجابة من ${num(r.students)} طالبًا${r.answers ? ` · الصحيح ${pct(r.correct, r.answers)}%` : ''}` })}</section>
      <section class="card d-wide">${ttl('objectives', 'الإجابات الصحيحة حسب الفصل', 'h3', 28)}
        <p class="small muted">نسبة الإجابات الصحيحة في تدريب الطلاب على أسئلة كل فصل.</p>
        ${hbars(esc, d.byChapter, { label: r => `${r.number}. ${r.title}`, value: r => (r.answers ? pct(r.correct, r.answers) : null),
          text: r => (r.answers ? pct(r.correct, r.answers) + '%' : '—'),
          tip: r => (r.answers ? `${r.title}: ${num(r.correct)} صحيحة من ${num(r.answers)}` : `${r.title}: لم يتدرب عليه الطلاب بعد`) })}</section>
      <section class="card">${ttl('students', 'المشاركة حسب الشعبة', 'h3', 28)}
        <p class="small muted">نسبة طلاب الشعبة الذين تدرّبوا مرة على الأقل.</p>
        ${d.bySection.length ? hbars(esc, d.bySection, { label: r => 'شعبة ' + r.section, value: r => pct(r.active, r.students),
          text: r => `${num(r.active)} من ${num(r.students)}`,
          tip: r => `شعبة ${r.section}: ${pct(r.active, r.students)}% تدرّبوا · ${num(r.active7)} نشطون هذا الأسبوع · ${num(r.answers)} إجابة${r.answers ? ` · الصحيح ${pct(r.correct, r.answers)}%` : ''}` })
          : '<div class="empty">لا توجد شعب بعد.</div>'}</section>
      <section class="card">${ttl('trophy', 'الإجابات الصحيحة حسب مستوى التفكير', 'h3', 28)}
        <p class="small muted">هل يتقن الطلاب أسئلة التطبيق والتفكير العليا كما يتقنون التذكر؟</p>
        ${hbars(esc, GROUPS.map(([g, l]) => ({ l, ...(d.byGroup.find(x => x.group === g) || { answers: 0, correct: 0 }) })),
          { label: r => r.l, value: r => (r.answers ? pct(r.correct, r.answers) : null), text: r => (r.answers ? pct(r.correct, r.answers) + '%' : '—'),
            tip: r => `${r.l}: ${num(r.correct)} صحيحة من ${num(r.answers)}` })}</section>
    </div>` : '<div class="empty">لا توجد حسابات طلاب بعد.</div>'}

    ${can('review') ? `<h2 class="d-h">${icon('shield', 30)}المراجعة</h2>
    <div class="grid cards d-grid">
      ${d.notes ? `<section class="card">${ttl('notes', 'ملاحظات المراجعة', 'h3', 28)}
        <p><b class="d-big">${num(d.notes.open)}</b> ملاحظة مفتوحة من ${num(d.notes.n)}</p>
        <a class="btn" href="#/notes">عرض الملاحظات</a></section>` : ''}
      <section class="card d-wide">${ttl('history', 'آخر التعديلات', 'h3', 28)}<div id="revs" class="table-wrap">جارٍ التحميل…</div></section>
    </div>` : ''}`;

  bindTips($app);
  document.getElementById('d-refresh').onclick = () => pageDashboard(ctx).catch(ctx.fail);
  document.getElementById('d-print').onclick = () => window.print();
  if (can('review')) {
    const NAMES = { create: 'إنشاء', edit: 'تعديل', status: 'تغيير الحالة', exclude: 'استبعاد', restore: 'إرجاع', duplicate: 'نسخ', approve: 'اعتماد', return: 'إعادة', reset: 'إلغاء الاعتماد' };
    const ENT = { question: 'سؤال', objective: 'هدف', supplement: 'محتوى مكمّل' };
    try {
      const rows = await api('/revisions?limit=30');
      const el = document.getElementById('revs');
      if (el) el.innerHTML = rows.length ? `<table class="list"><thead><tr><th>التاريخ</th><th>المستخدم</th><th>العنصر</th><th>الإجراء</th><th>ملاحظة</th></tr></thead>
        <tbody>${rows.map(r => `<tr><td class="ltr small">${esc(new Date(r.at).toLocaleString('ar-SA-u-nu-latn', { dateStyle: 'short', timeStyle: 'short' }))}</td><td>${esc(r.user || '')}</td>
        <td>${esc(ENT[r.entity] || r.entity)} #${r.entity_id}</td><td>${esc(NAMES[r.action] || r.action)}</td><td>${esc(r.note || '')}</td></tr>`).join('')}</tbody></table>`
        : '<div class="empty">لا توجد تعديلات بعد.</div>';
    } catch (e) { if (!e?.stale) ctx.fail(e); }
  }
}
