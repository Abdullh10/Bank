// ملاحظات المراجعة: يكتبها المراجع (ومالك المشروع) على هدف أو سؤال أو محتوى مكمّل دون تعديل المحتوى نفسه،
// ويطّلع عليها مالك المشروع في صفحة «الملاحظات»، فينفذها ثم يغلقها مع رد اختياري.
import { icon, line } from './icons.js';

const dateFmt = d => new Date(d).toLocaleDateString('ar-SA-u-nu-latn', { year: 'numeric', month: 'short', day: 'numeric' });
const qLabel = n => `${n.questionType === 'essay' ? 'سؤال مقالي' : 'سؤال اختيار'} ${n.questionNumber ?? ''}`;
const target = n => (n.entity === 'question' ? qLabel(n) : n.entity === 'supplement' ? 'المحتوى المكمّل' : 'الهدف');

function noteItem(ctx, n, { withObjective = false } = {}) {
  const { esc, can, badge } = ctx;
  const canDelete = can('edit') || (n.mine && !n.resolvedAt);
  return `<li class="note ${n.resolvedAt ? 'done' : ''}" data-note="${n.id}">
    <div class="note-head">${badge(target(n), n.entity === 'question' ? 'brand' : '')}
      ${n.resolvedAt ? badge('نُفذت', 'ok') : badge('مفتوحة', 'warn')}
      ${withObjective ? `<a href="#/objective/${encodeURIComponent(n.objectiveCode)}" class="small">${esc(n.objectiveCode)}</a>` : ''}
      <span class="small muted">${esc(n.author || '')} · ${esc(dateFmt(n.createdAt))}</span></div>
    ${withObjective ? `<div class="small muted note-ctx">${esc(n.objectiveText)}</div>` : ''}
    ${n.questionStem ? `<div class="small note-ctx">«${esc(n.questionStem)}${n.questionStem.length >= 160 ? '…' : ''}»</div>` : ''}
    <div class="note-body">${esc(n.body)}</div>
    ${n.resolvedAt ? `<div class="small note-resp">${line('check', 15)} ${esc(n.resolvedBy || '')} · ${esc(dateFmt(n.resolvedAt))}${n.response ? ` — ${esc(n.response)}` : ''}</div>` : ''}
    <div class="actions note-tools">
      ${can('edit') ? (n.resolvedAt ? `<button type="button" data-nopen="${n.id}">إعادة فتح</button>`
        : `<button type="button" class="ok" data-nresolve="${n.id}">${line('check', 15)}تم التنفيذ</button>`) : ''}
      ${canDelete ? `<button type="button" class="danger" data-ndel="${n.id}">${line('trash', 15)}حذف</button>` : ''}
    </div>
  </li>`;
}

function bindNoteTools(ctx, root, reload) {
  const { api, fail, toast, guard } = ctx;
  root.querySelectorAll('[data-nresolve]').forEach(b => b.onclick = guard(async () => {
    const response = prompt('رد مختصر على المراجع (اختياري):', '');
    if (response === null) return;
    try { await api(`/notes/${b.dataset.nresolve}/resolve`, { method: 'POST', body: { resolved: true, response } }); toast('أُغلقت الملاحظة'); reload(); }
    catch (e) { fail(e); }
  }));
  root.querySelectorAll('[data-nopen]').forEach(b => b.onclick = guard(async () => {
    try { await api(`/notes/${b.dataset.nopen}/resolve`, { method: 'POST', body: { resolved: false } }); reload(); } catch (e) { fail(e); }
  }));
  root.querySelectorAll('[data-ndel]').forEach(b => b.onclick = guard(async () => {
    if (!confirm('حذف هذه الملاحظة نهائيًا؟')) return;
    try { await api(`/notes/${b.dataset.ndel}/delete`, { method: 'POST' }); toast('حُذفت الملاحظة'); reload(); } catch (e) { fail(e); }
  }));
}

// بطاقة الملاحظات أسفل صفحة الهدف: كل ملاحظات الهدف وأسئلته، ونموذج لإضافة ملاحظة
export async function notesCard(ctx, el, o, questions, supplement) {
  const { api, esc, fail, toast, ttl, guard } = ctx;
  if (!el) return;
  const reload = () => notesCard(ctx, el, o, questions, supplement);
  let notes;
  try { notes = await api('/notes?code=' + encodeURIComponent(o.code), { keep: true }); }
  catch (e) { el.innerHTML = `<div class="notice bad">${esc(e.message)}</div>`; return; }
  if (!el.isConnected) return;
  const open = notes.filter(n => !n.resolvedAt).length;
  const opts = [['objective:', 'الهدف (الصياغة، المستوى، التصنيف…)'], ...(supplement ? [['supplement:', 'المحتوى المكمّل']] : []),
    ...questions.map(q => [`question:${q.id}`, `${q.type === 'essay' ? 'سؤال مقالي' : 'سؤال اختيار'} ${q.number}: ${q.stem.slice(0, 60)}${q.stem.length > 60 ? '…' : ''}`])];
  el.innerHTML = `
    <div class="section-title" style="margin-top:0">${ttl('notes', `ملاحظات المراجعة <span class="muted small">(${open} مفتوحة من ${notes.length})</span>`)}</div>
    <p class="small muted">الملاحظة لا تغيّر المحتوى؛ يطّلع عليها مالك المشروع وينفذها ثم يغلقها.</p>
    <div class="note-add">
      <div class="field"><label for="n-target">الملاحظة على</label>
        <select id="n-target">${opts.map(([v, t]) => `<option value="${v}">${esc(t)}</option>`).join('')}</select></div>
      <div class="field"><label for="n-body">الملاحظة</label><textarea dir="auto" id="n-body" maxlength="2000" placeholder="مثال: البديل (ب) صحيح أيضًا لأن…"></textarea></div>
      <div class="actions"><button type="button" class="primary" id="n-save">${line('plus', 16)}إضافة الملاحظة</button></div>
    </div>
    ${notes.length ? `<ul class="notes">${notes.map(n => noteItem(ctx, n)).join('')}</ul>` : ''}`;
  el.querySelector('#n-save').onclick = guard(async () => {
    const [entity, qid] = el.querySelector('#n-target').value.split(':');
    const body = el.querySelector('#n-body').value;
    if (body.trim().length < 3) return toast('اكتب الملاحظة', true);
    try {
      await api('/notes', { method: 'POST', body: { code: o.code, entity, question: qid ? Number(qid) : null, body }, keep: true });
      toast('أُضيفت الملاحظة'); reload();
    } catch (e) { fail(e); }
  });
  bindNoteTools(ctx, el, reload);
}

// نافذة ملاحظة سريعة من زر «ملاحظة» على السؤال
export function noteDialog(ctx, { code, entity, question }, done) {
  const { api, esc, fail, toast, dialog, guard } = ctx;
  const d = dialog(`ملاحظة على ${question ? `${question.type === 'essay' ? 'السؤال المقالي' : 'سؤال الاختيار'} ${question.number}` : 'الهدف'}`,
    `${question ? `<p class="small muted">${esc(question.stem)}</p>` : ''}
     <label for="nd-body">الملاحظة</label><textarea dir="auto" id="nd-body" maxlength="2000" style="min-height:8rem"></textarea>
     <p class="small muted">لا تغيّر الملاحظة السؤال؛ تظهر لمالك المشروع في صفحة «الملاحظات».</p>`,
    `<button type="button" class="primary" id="nd-save">حفظ الملاحظة</button>`);
  d.querySelector('#nd-body').focus();
  d.querySelector('#nd-save').onclick = guard(async () => {
    const body = d.querySelector('#nd-body').value;
    if (body.trim().length < 3) return toast('اكتب الملاحظة', true);
    try {
      await api('/notes', { method: 'POST', body: { code, entity, question: question?.id ?? null, body }, keep: true });
      d.close(); toast('حُفظت الملاحظة'); done?.();
    } catch (e) { fail(e); }
  });
}

const notesFilter = { status: 'open' };
export async function pageNotes(ctx) {
  const { api, $app, can } = ctx;
  const notes = await api('/notes?status=' + notesFilter.status);
  const seg = (v, t) => `<button type="button" class="${notesFilter.status === v ? 'on' : ''}" data-nstatus="${v}">${t}</button>`;
  $app.innerHTML = `<div class="crumbs"><a href="#/course">الرئيسية</a> ‹ الملاحظات</div>
    <div class="hero"><div class="hero-ic">${icon('notes', 52)}<div><h1>ملاحظات المراجعة</h1>
      <p class="muted">${can('edit') ? 'ملاحظات المراجعين على الأهداف والأسئلة. افتح الهدف لتنفيذ التعديل، ثم اضغط «تم التنفيذ».'
        : 'ملاحظاتك وملاحظات بقية المراجعين. ينفذها مالك المشروع ويغلقها.'}</p></div></div>
      <div class="actions"><div class="seg" role="group" aria-label="حالة الملاحظات">${seg('open', 'المفتوحة')}${seg('resolved', 'المنفذة')}${seg('all', 'الكل')}</div></div></div>
    <section class="card">${notes.length ? `<ul class="notes">${notes.map(n => noteItem(ctx, n, { withObjective: true })).join('')}</ul>`
      : `<div class="empty">${notesFilter.status === 'open' ? 'لا توجد ملاحظات مفتوحة.' : 'لا توجد ملاحظات.'}</div>`}</section>`;
  const reload = () => pageNotes(ctx).catch(ctx.fail);
  $app.querySelectorAll('[data-nstatus]').forEach(b => b.onclick = () => { notesFilter.status = b.dataset.nstatus; reload(); });
  bindNoteTools(ctx, $app, reload);
}
export const resetNotesState = () => { notesFilter.status = 'open'; };
