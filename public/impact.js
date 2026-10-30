// قسم «قياس الأثر»: دراسات (اختبار قبلي ← استخدام المنصة ← اختبار بعدي) تُدخل درجاتها بملف Excel، فتربطها المنصة باستخدام كل طالب
// بين تاريخي الاختبارين وتحللها (public/impact-stats.js). الأسماء للمالك والمعلم والمراجع؛ المشرف والمدير يريان أرقامًا دون هوية.
import { icon, line } from './icons.js';
import { hijri } from './dates.js';
import { bindTips } from './dashboard.js';
import { loadXlsx, parseCsv, downloadXlsx } from './staff.js';
import { analyzeStudy, effectLabel, gainLabel, pLabel, rLabel, alphaLabel, fmt, MIN_N, MIN_GROUP, PRACTICED } from './impact-stats.js';

const num = n => Number(n || 0).toLocaleString('ar-SA-u-nu-latn');
const PHASES = { pre: 'الاختبار القبلي', post: 'الاختبار البعدي', prior: 'درجة سابقة (اختياري)' };
const BANDS = { low: 'أقل من 50% في القبلي', mid: 'من 50% إلى 75%', high: 'أعلى من 75%' };
const TIERS = ['الثلث الأقل استخدامًا', 'الثلث المتوسط', 'الثلث الأعلى استخدامًا'];
const pc = x => (Number.isFinite(x) ? fmt(x, 1) + '%' : '—');
const signed = (x, d = 1) => (Number.isFinite(x) ? (x > 0 ? '+' : '') + fmt(x, d) : '—');

export async function pageImpact(ctx, arg) {
  if (!arg) return pageList(ctx);
  if (arg === 'new') return pageForm(ctx, null);
  const [id, sub] = String(arg).split(':');
  if (sub === 'edit') return pageForm(ctx, Number(id));
  return pageStudy(ctx, Number(id), sub || 'results');
}

// ---------- قائمة الدراسات ----------
async function pageList(ctx) {
  const { api, esc, $app, state } = ctx;
  const list = await api('/impact');
  const canManage = ['admin', 'viewer'].includes(state.user.role);
  $app.innerHTML = `<div class="crumbs"><a href="#/course">الرئيسية</a> ‹ قياس الأثر</div>
    <div class="hero"><div class="hero-ic">${icon('trophy', 52)}<div><h1>قياس الأثر</h1>
      <p class="muted">هل استفاد الطلاب من المنصة؟ أدخل درجات اختبار قبلي واختبار بعدي، فتربطها المنصة بتدريب كل طالب بين الاختبارين وتحللها تحليلًا إحصائيًا منهجيًا.</p></div></div>
      ${canManage ? `<div class="actions no-print"><a class="btn primary" href="#/impact/new">${line('plus', 17)}دراسة أثر جديدة</a></div>` : ''}</div>
    <section class="card"><ol class="imp-steps">
      <li><b>أنشئ الدراسة</b><span class="small muted">عنوانها، وتاريخ الاختبارين، والدرجة العظمى، وأسئلة الاختبار وأهدافها (اختياري لكنه يقوّي التحليل).</span></li>
      <li><b>أدخل درجات القبلي</b><span class="small muted">نزّل القالب بأسماء طلابك، واملأه، ثم ارفعه.</span></li>
      <li><b>دع الطلاب يتدرّبون</b><span class="small muted">تُحسب إجاباتهم الجادة (3 ثوانٍ فأكثر) بين التاريخين آليًا.</span></li>
      <li><b>أدخل درجات البعدي</b><span class="small muted">فتظهر النتائج: التحسن، وحجم الأثر، وعلاقته بمقدار الاستخدام، والأهداف.</span></li>
    </ol></section>
    ${list.length ? `<div class="grid cards">${list.map(s => `<a class="card imp-card" href="#/impact/${s.id}">
        ${ttl(esc, 'progress', s.title)}
        <p class="small muted">${line('clock', 14)} القبلي ${esc(hijri(s.preDate))}${s.postDate ? ` ← البعدي ${esc(hijri(s.postDate))}` : ' ← البعدي لم يُحدد'}</p>
        <p class="imp-badges">${badge(esc, `القبلي: ${num(s.nPre)}`, s.nPre ? 'ok' : '')}${badge(esc, `البعدي: ${num(s.nPost)}`, s.nPost ? 'ok' : '')}
          ${badge(esc, s.nPaired >= MIN_N ? `جاهزة للتحليل (${num(s.nPaired)})` : 'بانتظار البيانات', s.nPaired >= MIN_N ? 'brand' : 'warn')}
          ${s.items ? badge(esc, `${num(s.items)} سؤالًا`, 'info') : ''}</p></a>`).join('')}</div>`
    : `<div class="empty"><h2>لا توجد دراسات أثر بعد</h2><p>${canManage ? 'ابدأ بإنشاء دراسة وأدخل درجات اختبارك القبلي.' : 'تظهر هنا الدراسات التي ينشئها المعلم أو مالك المشروع.'}</p></div>`}`;
}

const ttl = (esc, ic, text) => `<h3 class="ttl">${icon(ic, 28)}<span>${esc(text)}</span></h3>`;
const badge = (esc, text, kind = '') => `<span class="badge ${kind}">${esc(text)}</span>`;

// ---------- إنشاء دراسة أو تعديلها ----------
async function pageForm(ctx, id) {
  const { api, esc, $app, toast, fail } = ctx;
  const [list, data] = await Promise.all([api('/chapters'), id ? api(`/impact/${id}`) : null]);
  // أهداف المقرر لقائمة الاقتراح (فصلًا فصلًا؛ تفاصيل الفصل تحمل دروسه وأهدافه)
  const chapters = await Promise.all(list.map(c => api('/chapters/' + c.number)));
  const s = data?.study || { title: '', note: '', preDate: '', postDate: '', preMax: 100, postMax: 100, sameTest: true, items: [] };
  const codes = chapters.flatMap(c => c.lessons.flatMap(l => l.objectives.map(o => ({ code: o.code, text: o.approvedText || o.originalText }))));
  const itemRow = (it, i) => `<tr><td>س${i + 1}</td><td><input type="number" min="0.5" step="0.5" class="imp-imax" value="${esc(it.max ?? 1)}" aria-label="درجة السؤال ${i + 1}"></td>
    <td><input list="imp-codes" class="imp-iobj" dir="ltr" value="${esc(it.objective || '')}" placeholder="مثل C1-L2-O03" aria-label="هدف السؤال ${i + 1}"></td></tr>`;
  $app.innerHTML = `<div class="crumbs"><a href="#/course">الرئيسية</a> ‹ <a href="#/impact">قياس الأثر</a> ‹ ${id ? 'تعديل الدراسة' : 'دراسة جديدة'}</div>
    <div class="hero"><div class="hero-ic">${icon('trophy', 52)}<div><h1>${id ? 'تعديل دراسة الأثر' : 'دراسة أثر جديدة'}</h1>
      <p class="muted">البيانات الأساسية للاختبارين. يمكنك تعديلها لاحقًا.</p></div></div></div>
    <form id="imp-form" class="card">
      <div class="field"><label for="imp-title">عنوان الدراسة</label><input id="imp-title" required value="${esc(s.title)}" placeholder="مثل: أثر المنصة في الفصل الأول · كيمياء 2-1"></div>
      <div class="form-grid imp-grid">
        <div class="field"><label for="imp-pre">تاريخ القبلي</label><input id="imp-pre" type="date" required value="${esc(s.preDate || '')}"></div>
        <div class="field"><label for="imp-post">تاريخ البعدي</label><input id="imp-post" type="date" value="${esc(s.postDate || '')}"><span class="small muted imp-hint">يمكن تحديده لاحقًا</span></div>
        <div class="field"><label for="imp-premax">الدرجة العظمى للقبلي</label><input id="imp-premax" type="number" min="1" step="0.5" required value="${esc(s.preMax)}"></div>
        <div class="field"><label for="imp-postmax">الدرجة العظمى للبعدي</label><input id="imp-postmax" type="number" min="1" step="0.5" required value="${esc(s.postMax)}"></div>
      </div>
      <label class="imp-check"><input type="checkbox" id="imp-same" ${s.sameTest ? 'checked' : ''}> البعدي هو الاختبار القبلي نفسه (إن كان صيغة مكافئة بأسئلة مختلفة فأزل العلامة)</label>
      <div class="field"><label for="imp-note">ملاحظات <span class="small muted">(اختياري: طريقة التطبيق، والظروف)</span></label><textarea id="imp-note" rows="2">${esc(s.note || '')}</textarea></div>
      <h3 class="ttl">${icon('mcq', 28)}<span>أسئلة الاختبار (اختياري، ويقوّي التحليل كثيرًا)</span></h3>
      <p class="small muted">إن أدخلت درجة كل سؤال لكل طالب، تحسب المنصة ثبات الاختبار وصعوبة أسئلته، وكسب الطلاب في كل هدف، وهل تحسّن الطالب أكثر في الأهداف التي تدرّب عليها.
        يجب أن يكون للقبلي والبعدي العدد نفسه من الأسئلة وبالترتيب نفسه للأهداف، وأن يساوي مجموع درجات الأسئلة الدرجة العظمى.</p>
      <div class="field imp-count"><label for="imp-n">عدد الأسئلة</label><input id="imp-n" type="number" min="0" max="100" value="${s.items.length}"></div>
      <datalist id="imp-codes">${codes.map(c => `<option value="${esc(c.code)}">${esc(c.text.slice(0, 80))}</option>`).join('')}</datalist>
      <div class="table-wrap"><table class="list imp-items"><thead><tr><th>السؤال</th><th>درجته</th><th>رمز الهدف الذي يقيسه</th></tr></thead>
        <tbody id="imp-items">${s.items.map(itemRow).join('')}</tbody></table></div>
      <p id="imp-sum" class="small muted"></p>
      <div class="actions"><button type="submit" class="primary">${line('check', 17)}${id ? 'حفظ التعديل' : 'إنشاء الدراسة'}</button>
        <a class="btn" href="${id ? `#/impact/${id}` : '#/impact'}">إلغاء</a>
        ${id && data.study.canEdit ? `<button type="button" class="danger" id="imp-del">${line('trash', 17)}حذف الدراسة</button>` : ''}</div>
    </form>`;
  const tbody = document.getElementById('imp-items');
  const readItems = () => [...tbody.querySelectorAll('tr')].map(tr => ({ max: Number(tr.querySelector('.imp-imax').value), objective: tr.querySelector('.imp-iobj').value.trim() }));
  const showSum = () => {
    const items = readItems(), total = items.reduce((t, i) => t + (i.max || 0), 0);
    document.getElementById('imp-sum').textContent = items.length ? `مجموع درجات الأسئلة: ${total}${Math.abs(total - Number(document.getElementById('imp-premax').value)) > 1e-9 ? ' (لا يساوي الدرجة العظمى للقبلي)' : ''}` : '';
  };
  document.getElementById('imp-n').addEventListener('input', e => {
    const n = Math.max(0, Math.min(100, Number(e.target.value) || 0)), cur = readItems();
    tbody.innerHTML = Array.from({ length: n }, (_, i) => itemRow(cur[i] || { max: 1 }, i)).join('');
    showSum();
  });
  tbody.addEventListener('input', showSum);
  showSum();
  document.getElementById('imp-del')?.addEventListener('click', async () => {
    if (!confirm('حذف الدراسة وكل درجاتها نهائيًا؟')) return;
    try { await api(`/impact/${id}/delete`, { method: 'POST' }); toast('حُذفت الدراسة'); location.hash = '#/impact'; } catch (e) { fail(e); }
  });
  document.getElementById('imp-form').addEventListener('submit', async e => {
    e.preventDefault();
    const items = readItems();
    const body = { title: document.getElementById('imp-title').value, note: document.getElementById('imp-note').value,
      preDate: document.getElementById('imp-pre').value, postDate: document.getElementById('imp-post').value,
      preMax: Number(document.getElementById('imp-premax').value), postMax: Number(document.getElementById('imp-postmax').value),
      sameTest: document.getElementById('imp-same').checked, items };
    if (items.length) {
      const total = items.reduce((t, i) => t + i.max, 0);
      if (Math.abs(total - body.preMax) > 1e-9 || Math.abs(total - body.postMax) > 1e-9) return toast('مجموع درجات الأسئلة يجب أن يساوي الدرجة العظمى للاختبارين', true);
    }
    try {
      const r = await api(id ? `/impact/${id}/save` : '/impact/save', { method: 'POST', body });
      toast(id ? 'حُفظ التعديل' : 'أُنشئت الدراسة');
      location.hash = `#/impact/${r.id}:data`;
    } catch (err) { fail(err); }
  });
}

// ---------- قراءة ملف الدرجات ----------
// الأعمدة: «اسم المستخدم»، و«المجموع» أو «الدرجة»، و«س1…سN» (درجة كل سؤال). الخلية الفارغة = لم يؤدِّ.
export function parseScoreRows(rows, k) {
  const norm = s => String(s ?? '').trim().replace(/\s+/g, ' ');
  const headerAt = rows.findIndex(r => r.some(c => /اسم المستخدم|username/i.test(norm(c))));
  if (headerAt < 0) throw new Error('لم أجد عمود «اسم المستخدم» في الملف؛ استعمل القالب الذي تنزّله المنصة');
  const h = rows[headerAt].map(norm);
  const uCol = h.findIndex(c => /اسم المستخدم|username/i.test(c));
  const tCol = h.findIndex(c => /^(المجموع|الدرجة|الدرجة الكلية|total|score)$/i.test(c));
  const qCols = Array.from({ length: k }, (_, i) => h.findIndex(c => c === `س${i + 1}` || c.toLowerCase() === `q${i + 1}`));
  const hasItems = k > 0 && qCols.every(c => c >= 0);
  if (tCol < 0 && !hasItems) throw new Error(k ? `لم أجد عمود «المجموع» ولا أعمدة الأسئلة س1…س${k}` : 'لم أجد عمود «المجموع» أو «الدرجة»');
  const val = v => { const t = norm(v).replace(',', '.').replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)); return t === '' ? null : Number(t); };
  const out = [], bad = [];
  for (const r of rows.slice(headerAt + 1)) {
    const username = norm(r[uCol]).toLowerCase();
    if (!username) continue;
    const total = tCol >= 0 ? val(r[tCol]) : null;
    const items = hasItems ? qCols.map(c => val(r[c])) : null;
    if ([total, ...(items || [])].some(v => v != null && !Number.isFinite(v))) { bad.push(username); continue; }
    out.push({ username, total, items: items && items.some(v => v != null) ? items : null });
  }
  return { rows: out, bad, hasItems };
}
async function readSheet(file) {
  if (/\.csv$/i.test(file.name)) return parseCsv(await file.text());
  const XLSX = await loadXlsx();
  const wb = XLSX.read(await file.arrayBuffer(), { type: 'array' });
  return XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '', raw: false });
}

// ---------- صفحة الدراسة: البيانات والنتائج ----------
async function pageStudy(ctx, id, tab) {
  const { api, esc, $app, toast, fail } = ctx;
  const data = await api(`/impact/${id}`);
  const s = data.study, k = s.items.length;
  const tabs = [['results', 'النتائج'], ...(s.canImport ? [['data', 'إدخال الدرجات']] : [])];
  if (!tabs.some(t => t[0] === tab)) tab = 'results';
  $app.innerHTML = `<div class="crumbs"><a href="#/course">الرئيسية</a> ‹ <a href="#/impact">قياس الأثر</a> ‹ ${esc(s.title)}</div>
    <div class="hero"><div class="hero-ic">${icon('trophy', 52)}<div><h1>${esc(s.title)}</h1>
      <p class="muted">القبلي ${esc(hijri(s.preDate))} (من ${esc(String(s.preMax))}) ← ${s.postDate ? `البعدي ${esc(hijri(s.postDate))} (من ${esc(String(s.postMax))})` : 'البعدي لم يُحدد بعد'}${k ? ` · ${num(k)} سؤالًا` : ''}</p>
      ${s.note ? `<p class="small muted">${esc(s.note)}</p>` : ''}</div></div>
      <div class="actions no-print">${s.canEdit ? `<a class="btn" href="#/impact/${id}:edit">تعديل الدراسة</a>` : ''}
        <button type="button" id="imp-print">${line('print', 17)}طباعة التقرير</button></div></div>
    <div class="seg no-print" role="tablist">${tabs.map(([t, l]) => `<a role="tab" class="btn${t === tab ? ' on' : ''}" aria-selected="${t === tab}" href="#/impact/${id}:${t}">${l}</a>`).join('')}</div>
    <div id="imp-body"></div>`;
  document.getElementById('imp-print').onclick = () => window.print();
  const body = document.getElementById('imp-body');
  if (tab === 'data') return renderData(ctx, data, body, () => pageStudy(ctx, id, 'data').catch(fail));
  renderResults(ctx, data, body);
}

function renderData(ctx, data, body, reload) {
  const { api, esc, toast, fail } = ctx;
  const s = data.study, k = s.items.length, rows = data.rows;
  const counts = ph => rows.filter(r => r[ph] != null).length;
  body.innerHTML = `<div class="grid cards">${['pre', 'post', 'prior'].map(ph => `<section class="card imp-phase">
      ${ttl(esc, ph === 'prior' ? 'history' : 'upload', PHASES[ph])}
      <p><b class="d-big">${num(counts(ph))}</b> طالبًا من ${num(rows.length)}</p>
      ${ph === 'prior' ? '<p class="small muted">درجة الطالب في اختبار سابق للمبادرة (مثل نهاية الفصل الماضي) من 100. تضبط المقارنة بمستوى الطالب الأصلي، وتُستخدم في التحليل إذا أُدخلت لكل الطلاب.</p>'
        : `<p class="small muted">${k && ph !== 'prior' ? `اكتب درجة كل سؤال (س1…س${k}) ويُحسب المجموع آليًا، أو المجموع وحده.` : 'اكتب مجموع درجة الطالب.'} اترك الخلية فارغة لمن لم يؤدِّ الاختبار، ولا تكتب له صفرًا.</p>`}
      <div class="actions"><button type="button" data-tpl="${ph}">${line('download', 17)}تنزيل القالب</button>
        <label class="btn primary">${line('plus', 17)}رفع الملف<input type="file" accept=".xlsx,.xls,.csv" data-up="${ph}" hidden></label></div>
      <div class="imp-result" data-res="${ph}"></div></section>`).join('')}</div>
    <section class="card">${ttl(esc, 'students', 'الطلاب ودرجاتهم')}
      <p class="small muted">طلاب المقرر الذين تتابعهم. «الإجابات الجادة» هي الإجابات الأولى على أسئلة لم يجب عنها الطالب من قبل، واستغرقت 3 ثوانٍ فأكثر، بين تاريخي الاختبارين.</p>
      <div class="table-wrap"><table class="list"><thead><tr><th>الطالب</th><th>الشعبة</th><th>القبلي</th><th>البعدي</th><th>سابق</th><th>الإجابات الجادة</th><th>أيام النشاط</th></tr></thead>
      <tbody>${rows.map(r => `<tr><td>${esc(r.name || '—')} <span class="small muted" dir="ltr">${esc(r.username || '')}</span></td><td>${esc(r.section || '—')}</td>
        <td>${r.pre ?? '<span class="muted">—</span>'}</td><td>${r.post ?? '<span class="muted">—</span>'}</td><td>${r.prior ?? '<span class="muted">—</span>'}</td>
        <td>${num(r.usage.valid)}</td><td>${num(r.usage.days)}</td></tr>`).join('')}</tbody></table></div></section>`;

  body.querySelectorAll('[data-tpl]').forEach(b => b.addEventListener('click', () => {
    const ph = b.dataset.tpl, items = ph !== 'prior' && k ? s.items.map((_, i) => `س${i + 1}`) : [];
    downloadXlsx(`itqan-impact-${s.id}-${ph}`, ['الاسم', 'اسم المستخدم', 'الشعبة', ...items, 'المجموع'],
      rows.map(r => [r.name || '', r.username || '', r.section || '', ...items.map((_, i) => r[ph + 'Items']?.[i] ?? ''), r[ph] ?? '']), PHASES[ph].slice(0, 30));
  }));
  body.querySelectorAll('[data-up]').forEach(inp => inp.addEventListener('change', async () => {
    const ph = inp.dataset.up, file = inp.files[0], res = body.querySelector(`[data-res="${ph}"]`);
    if (!file) return;
    try {
      const parsed = parseScoreRows(await readSheet(file), ph === 'prior' ? 0 : k);
      if (!parsed.rows.length) throw new Error('لم أجد صفوف طلاب في الملف');
      const r = await api(`/impact/${s.id}/import`, { method: 'POST', body: { phase: ph, rows: parsed.rows } });
      const issues = [...(parsed.bad.length ? [`قيم غير رقمية: ${parsed.bad.join('، ')}`] : []),
        ...(r.unknown.length ? [`أسماء مستخدمين غير معروفة أو لطلاب لا تتابعهم: ${r.unknown.join('، ')}`] : []), ...r.errors];
      toast(`حُفظت درجات ${num(r.saved)} طالبًا`);
      if (issues.length) {
        reload();
        setTimeout(() => {
          const el = document.querySelector(`[data-res="${ph}"]`);
          if (el) el.innerHTML = `<div class="notice warn"><b>صفوف لم تُحفظ:</b><ul>${issues.map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>`;
        }, 400);
      } else reload();
    } catch (e) { res.innerHTML = `<div class="notice bad">${esc(e.message)}</div>`; if (e.status && e.status !== 400) fail(e); }
    inp.value = '';
  }));
}

// رسم «قبل ← بعد» لكل مجموعة: دائرة مفرغة للقبلي ومصمتة للبعدي على محور 0–100%
function dumbbell(esc, groups, label) {
  return `<div class="imp-db" role="list">${groups.map(g => {
    const a = g.mPre, b = g.mPost, lo = Math.min(a, b), hi = Math.max(a, b);
    return Number.isFinite(a) ? `<div class="imp-db-row" role="listitem" tabindex="0" data-tip="${esc(`${label(g)}: القبلي ${pc(a)} ← البعدي ${pc(b)} (${num(g.n)} طالبًا)`)}">
      <span class="imp-db-lab">${esc(label(g))} <span class="small muted">(${num(g.n)})</span></span>
      <span class="imp-db-track"><span class="imp-db-line ${b < a ? 'down' : ''}" style="inset-inline-start:${lo}%;width:${hi - lo}%"></span>
        <span class="imp-db-dot pre" style="inset-inline-start:${a}%"></span><span class="imp-db-dot post" style="inset-inline-start:${b}%"></span></span>
      <span class="imp-db-val">${signed(b - a)}</span></div>`
      : `<div class="imp-db-row" role="listitem"><span class="imp-db-lab">${esc(label(g))} <span class="small muted">(${num(g.n)})</span></span><span class="small muted">عيّنة صغيرة (أقل من ${MIN_GROUP})</span><span></span></div>`;
  }).join('')}</div>
  <p class="imp-legend small muted"><span class="imp-db-dot pre"></span> القبلي <span class="imp-db-dot post"></span> البعدي · الرقم: التغير بالنقاط المئوية</p>`;
}

function renderResults(ctx, data, body) {
  const { esc } = ctx;
  const a = analyzeStudy(data), s = data.study, o = a.overall, c = a.counts;
  if (!o || !a.ready) {
    body.innerHTML = `<div class="grid kpi">${kpi(esc, num(c.pre), 'أدّوا القبلي', 'upload')}${kpi(esc, num(c.post), 'أدّوا البعدي', 'upload')}${kpi(esc, num(c.paired), 'لهم الاختباران', 'students')}</div>
      <div class="empty"><h2>تظهر النتائج بعد إدخال الاختبارين</h2><p>يلزم ${MIN_N} طلاب على الأقل لهم درجة قبلية وبعدية.${s.canImport ? ' أدخل الدرجات من تبويب «إدخال الدرجات».' : ''}</p></div>`;
    return;
  }
  const lvl = { strong: 'ok', moderate: 'ok', initial: 'info', none: 'warn', insufficient: 'warn' }[a.evidence.level];
  const sig = o.p < 0.05;
  body.innerHTML = `
    <div class="notice ${lvl} imp-verdict"><b>${esc(a.evidence.label)}:</b> ${esc(a.evidence.text)}</div>
    ${a.warnings.map(w => `<div class="notice warn">${esc(w)}</div>`).join('')}

    <h2 class="d-h">${icon('progress', 30)}هل تحسّن الطلاب؟</h2>
    <div class="grid kpi">
      ${kpi(esc, pc(o.mPre), 'متوسط القبلي', 'history', `الانحراف المعياري ${fmt(o.sPre)}`)}
      ${kpi(esc, pc(o.mPost), 'متوسط البعدي', 'check', `الانحراف المعياري ${fmt(o.sPost)}`)}
      ${kpi(esc, signed(o.mDiff) + ' نقطة', 'متوسط التغير', 'progress', pLabel(o.p))}
      ${kpi(esc, fmt(o.g, 2), 'حجم الأثر (هيدجز g)', 'trophy', `${effectLabel(o.g)} · فترة الثقة 95%: ${fmt(o.ciLow, 2)} إلى ${fmt(o.ciHigh, 2)}`)}
      ${kpi(esc, fmt(o.hake, 2), 'الكسب المعدّل (هاك)', 'spark', gainLabel(o.hake))}
      ${kpi(esc, Math.round((100 * o.improved) / o.n) + '%', 'نسبة من تحسّن', 'students', `${num(o.improved)} تحسّن · ${num(o.same)} ثبت · ${num(o.declined)} تراجع`)}
    </div>
    <p class="small muted">العينة: ${num(o.n)} طالبًا لهم الاختباران${c.preOnly ? `، و${num(c.preOnly)} أدّوا القبلي فقط` : ''}${c.postOnly ? `، و${num(c.postOnly)} أدّوا البعدي فقط` : ''}.
      اختبار t للعينات المرتبطة: t(${o.df}) = ${fmt(o.t, 2)}، ${esc(pLabel(o.p))}. الارتباط بين القبلي والبعدي r = ${fmt(o.r, 2)}.</p>
    ${a.attrition ? `<p class="small muted">من أدّى القبلي فقط متوسطه القبلي ${pc(a.attrition.missingPre)} مقابل ${pc(a.attrition.completedPre)} لمن أكمل الاختبارين${Math.abs(a.attrition.diff) >= 10 ? ' (فرق كبير: قد يكون الغياب غير عشوائي)' : ''}.</p>` : ''}

    <div class="grid cards d-grid">
      <section class="card">${ttl(esc, 'students', 'حسب الشعبة')}${dumbbell(esc, a.sections, g => 'شعبة ' + g.key)}</section>
      <section class="card">${ttl(esc, 'objectives', 'حسب المستوى في القبلي')}
        <div class="table-wrap"><table class="list"><thead><tr><th>الفئة</th><th>العدد</th><th>القبلي</th><th>البعدي</th><th>التغير</th><th>حجم الأثر</th></tr></thead>
        <tbody>${a.bands.map(b => `<tr><td>${esc(BANDS[b.key])}</td><td>${num(b.n)}</td>${b.n >= MIN_GROUP ? `<td>${pc(b.mPre)}</td><td>${pc(b.mPost)}</td><td>${signed(b.mDiff)}</td><td>${fmt(b.g, 2)}</td>`
          : `<td colspan="4" class="small muted">عيّنة صغيرة</td>`}</tr>`).join('')}</tbody></table></div>
        <p class="small muted">تنبيه: الفئة الأضعف تبدو أكثر تحسنًا جزئيًا بسبب «الارتداد نحو المتوسط»، والأقوى يحدّها سقف الدرجة؛ لذلك يعتمد الحكم على أثر المنصة على التحليل التالي.</p></section>
    </div>

    <h2 class="d-h">${icon('practice', 30)}هل للمنصة دور في التحسن؟</h2>
    ${a.tiers ? `<div class="grid cards d-grid">
      <section class="card">${ttl(esc, 'progress', 'التحسن حسب مقدار الاستخدام')}
        <p class="small muted">قُسّم الطلاب ثلاث مجموعات متساوية تقريبًا بعدد إجاباتهم الجادة في المنصة بين الاختبارين.</p>
        ${dumbbell(esc, a.tiers.map(t => ({ ...t, key: t.tier })), t => `${TIERS[t.tier]} (${num(t.minUse)}–${num(t.maxUse)} إجابة)`)}</section>
      <section class="card">${ttl(esc, 'trophy', 'بعد ضبط المستوى القبلي')}
        ${a.dose ? `<p class="d-big">${signed(a.dose.adjDiff)} نقطة</p>
          <p>الفرق المتوقع في البعدي بين طالبين <b>متساويين في القبلي</b>، أحدهما في الثلث الأعلى استخدامًا والآخر في الأدنى${a.dose.withPrior ? ' (مع ضبط الدرجة السابقة أيضًا)' : ''}.
            يعادل ${fmt(a.dose.adjD, 2)} انحرافًا معياريًا (${esc(effectLabel(a.dose.adjD))})، ${esc(pLabel(a.dose.p))}.</p>
          <p class="small muted">تحليل التغاير (ANCOVA): البعدي = ثابت + ب₁×القبلي + ب₂×لوغاريتم(1 + الاستخدام)${a.dose.withPrior ? ' + ب₃×الدرجة السابقة' : ''}.
            الارتباط الجزئي للاستخدام مع البعدي r = ${fmt(a.dose.partialR, 2)} (${esc(rLabel(a.dose.partialR))})، وR² للنموذج = ${fmt(a.dose.r2, 2)}.</p>` : '<p class="muted">تعذر حساب النموذج.</p>'}
      </section></div>` : `<div class="notice info">يلزم ${MIN_N} طلاب على الأقل باستخدام متفاوت لتحليل علاقة الاستخدام بالتحسن.</div>`}
    <p class="small muted">مقدار الاستخدام: ${num(a.usage.total)} إجابة جادة بين الاختبارين، الوسيط ${num(a.usage.median)} للطالب، و${num(a.usage.none)} طالبًا لم يتدرّبوا.
      ${a.usage.rushedHeavy ? `${num(a.usage.rushedHeavy)} طالبًا أكثر من 40% من إجاباتهم متسرعة (أقل من 3 ثوانٍ)؛ إجاباتهم المتسرعة لا تُحتسب استخدامًا.` : ''}</p>

    ${a.within ? `<section class="card">${ttl(esc, 'objectives', 'داخل الطالب نفسه: الأهداف المتدرَّب عليها مقابل غيرها')}
      <p>كسب الطالب في الأهداف التي تدرّب عليها (${PRACTICED} إجابات جادة فأكثر): <b>${signed(a.within.gainPracticed)}</b> نقطة،
        وفي الأهداف التي لم يتدرّب عليها: <b>${signed(a.within.gainNot)}</b> نقطة. الفرق ${signed(a.within.diff)} نقطة، ${esc(pLabel(a.within.p))} (${num(a.within.n)} طالبًا).</p>
      <p class="small muted">كل طالب هنا يُقارن بنفسه، فيُلغى أثر الفروق بين الطلاب في الذكاء والدافعية والمعلم. هذا أقوى دليل تتيحه البيانات دون مجموعة ضابطة.</p></section>` : ''}

    ${a.objectives ? `<h2 class="d-h">${icon('objectives', 30)}حسب الأهداف</h2>
    <section class="card"><div class="table-wrap"><table class="list"><thead><tr><th>الهدف</th><th>الأسئلة</th><th>القبلي</th><th>البعدي</th><th>التغير</th><th>متوسط التدريب</th><th>تدرّب عليه</th></tr></thead>
      <tbody>${a.objectives.map(ob => `<tr><td><span dir="ltr" class="small">${esc(ob.code)}</span> ${esc(ob.text)}</td><td>${num(ob.items)}</td><td>${pc(ob.mPre)}</td><td>${pc(ob.mPost)}</td>
        <td><b class="${ob.gain < 0 ? 'imp-neg' : ''}">${signed(ob.gain)}</b></td><td>${fmt(ob.practice, 1)}</td><td>${Math.round(ob.practicedPct)}%</td></tr>`).join('')}</tbody></table></div>
      ${Number.isFinite(a.objCorrelation) ? `<p class="small muted">الارتباط بين متوسط التدريب على الهدف وكسب الطلاب فيه: r = ${fmt(a.objCorrelation, 2)} (${esc(rLabel(a.objCorrelation))}).</p>` : ''}</section>` : ''}

    ${a.quality && (a.quality.pre || a.quality.post) ? `<h2 class="d-h">${icon('shield', 30)}جودة الاختبار</h2>
    <div class="grid cards d-grid">${['pre', 'post'].filter(p => a.quality[p]).map(p => {
      const q = a.quality[p];
      return `<section class="card">${ttl(esc, 'mcq', PHASES[p])}
        <p>الثبات (ألفا كرونباخ / KR-20): <b>${fmt(q.alpha, 2)}</b> · ${esc(alphaLabel(q.alpha))} <span class="small muted">(${num(q.n)} طالبًا)</span></p>
        <div class="table-wrap"><table class="list"><thead><tr><th>السؤال</th><th>الصعوبة</th><th>التمييز</th><th></th></tr></thead>
        <tbody>${q.items.map(it => {
          const flags = [it.difficulty > 0.9 ? 'سهل جدًا' : '', it.difficulty < 0.2 ? 'صعب جدًا' : '', Number.isFinite(it.discrimination) && it.discrimination < 0.2 ? 'تمييز ضعيف' : ''].filter(Boolean);
          return `<tr><td>س${it.n}</td><td>${fmt(it.difficulty, 2)}</td><td>${fmt(it.discrimination, 2)}</td><td>${flags.map(f => badge(esc, f, 'warn')).join(' ')}</td></tr>`;
        }).join('')}</tbody></table></div></section>`;
    }).join('')}</div>
    <p class="small muted">الصعوبة: نسبة ما حصّله الطلاب من درجة السؤال (الأفضل بين 0.3 و0.8). التمييز: ارتباط السؤال بباقي الاختبار (0.2 فأكثر مقبول، و0.3 فأكثر جيد).</p>` : ''}

    <section class="card imp-method">${ttl(esc, 'notes', 'المنهجية وحدود الدراسة')}
      <ul>
        <li><b>التصميم:</b> قبلي-بعدي لمجموعة واحدة دون مجموعة ضابطة، مع تحليل «الجرعة-الاستجابة» (علاقة مقدار الاستخدام بالتحسن بعد ضبط المستوى القبلي)${a.within ? '، ومقارنة داخل الطالب نفسه بين الأهداف التي تدرّب عليها والتي لم يتدرّب عليها' : ''}.</li>
        <li><b>المؤشرات:</b> اختبار t للعينات المرتبطة؛ حجم الأثر هيدجز g محسوبًا بالانحراف المعياري المجمّع للقياسين (لا بانحراف الفروق حتى لا يتضخم)، مع فترة ثقة 95%؛ الكسب المعدّل لهاك = (البعدي − القبلي) ÷ (100 − القبلي).</li>
        <li><b>تفسير حجم الأثر:</b> أقل من 0.2 لا يُذكر، 0.2–0.4 ملموس، 0.4–0.6 جيد، أكثر من 0.6 كبير. متوسط أثر التدخلات التربوية قرابة 0.4.</li>
        <li><b>الاستخدام:</b> عدد الإجابات الأولى الجادة (3 ثوانٍ فأكثر) على أسئلة المقرر بين تاريخي الاختبارين، لا النقاط؛ فلا يتأثر بالتحايل أو بتكرار الأسئلة.</li>
        <li><b>الحدود:</b> التحسن بين الاختبارين يشمل أثر التدريس العادي والنضج${s.sameTest ? ' وتذكّر أسئلة الاختبار نفسه' : ' واحتمال اختلاف صعوبة الصيغتين'}. والطلاب الأكثر استخدامًا قد يختلفون في دافعيتهم؛ ضبط المستوى القبلي يخفف ذلك ولا يلغيه.
          لذلك تُقرأ النتائج «ارتباطًا» لا «سببية مؤكدة».</li>
      </ul>
      <p class="small muted">أُعدّ التقرير في ${esc(hijri(new Date().toISOString(), true))} · منصة إتقان · رمز الدراسة ${s.id}</p></section>`;
  bindTips(body);
}

const kpi = (esc, v, l, ic, sub = '') => `<div class="card">${icon(ic, 46)}<div class="value">${esc(v)}</div>
  <div class="label">${esc(l)}${sub ? `<span class="small muted d-sub">${esc(sub)}</span>` : ''}</div></div>`;
