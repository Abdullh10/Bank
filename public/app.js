// واجهة المنصة: تطبيق صفحة واحدة بوحدات ES دون أدوات بناء.
import { pageExam } from './exam.js';
const $app = document.getElementById('app');
const $dlg = document.getElementById('dlg');
const state = { user: null, selection: new Set() };

// ---------- أدوات ----------
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pct = (a, b) => (b ? Math.round((100 * (a || 0)) / b) : 0);
const LETTERS = ['أ', 'ب', 'ج'];

async function api(path, opts = {}) {
  if (state.static) return staticApi(path, opts);
  const { method = 'GET', body } = opts;
  const res = await fetch('api' + path, {
    method, credentials: 'same-origin',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => null);
  // لا يوجد خادم (مثل GitHub Pages): ننتقل إلى نسخة العرض الثابتة.
  if (data === null && path === '/me') { state.static = true; return staticApi(path, opts); }
  if (!res.ok || data === null) throw Object.assign(new Error(data?.error || 'تعذر تنفيذ الطلب'), { errors: data?.errors, status: res.status });
  return data;
}

// ---------- نسخة العرض الثابتة (للقراءة فقط) ----------
const staticCache = new Map();
const staticQuestions = new Map();
async function staticFile(name) {
  if (!staticCache.has(name)) {
    staticCache.set(name, fetch('static/' + name).then(r => {
      if (!r.ok) throw new Error('البيانات غير متاحة في نسخة العرض');
      return r.json();
    }));
  }
  const data = await staticCache.get(name);
  if (Array.isArray(data.questions)) for (const q of data.questions) staticQuestions.set(q.id, q);
  return data;
}
function staticTokens(s) {
  return new Set(String(s ?? '').replace(/[\u064B-\u0652]/g, '').replace(/[^\p{L}\p{N}\s]/gu, ' ').split(/\s+/).filter(w => w.length > 1));
}
function staticSimilarity(a, b) {
  const A = staticTokens(a), B = staticTokens(b);
  let i = 0; for (const w of A) if (B.has(w)) i++;
  return A.size && B.size ? i / (A.size + B.size - i) : 0;
}
async function staticApi(path, { method = 'GET', body } = {}) {
  const [p, query = ''] = path.split('?');
  const f = Object.fromEntries(new URLSearchParams(query));
  if (p === '/me') return { user: null };
  if (p === '/stats') return staticFile('stats.json');
  if (p === '/chapters') return staticFile('chapters.json');
  let m;
  if ((m = p.match(/^\/chapters\/(\d+)$/))) return staticFile(`chapter-${m[1]}.json`);
  if ((m = p.match(/^\/objectives\/([^/]+)$/)) && method === 'GET') {
    const d = await staticFile(`objectives/${decodeURIComponent(m[1])}.json`);
    return { ...d, questions: d.questions.filter(q => !q.excluded) };
  }
  if ((m = p.match(/^\/questions\/(\d+)\/check$/))) {
    const q = staticQuestions.get(Number(m[1]));
    if (!q) throw new Error('السؤال غير موجود');
    const c = Number(body?.choice);
    return { correct: c === q.correctIndex, correctIndex: q.correctIndex, explanation: q.explanation, distractorNote: q.distractorNotes?.[c] || null };
  }
  if (p === '/bank') {
    const all = (await staticFile('bank.json')).questions;
    const rows = all.filter(q => !q.excluded
      && (!f.chapter || q.chapter.number === Number(f.chapter)) && (!f.lesson || q.lesson.number === Number(f.lesson))
      && (!f.type || q.type === f.type) && (!f.level || q.thinkingLevel === f.level)
      && (!f.difficulty || q.difficulty === f.difficulty) && (!f.status || q.status === f.status)
      && (!f.q || q.stem.includes(f.q) || q.options.some(o => o.includes(f.q))));
    if (f.similar === '1') {
      const similar = [];
      for (let i = 0; i < rows.length; i++) for (let j = i + 1; j < rows.length; j++) {
        const sc = staticSimilarity(rows[i].stem, rows[j].stem);
        if (sc >= 0.5) similar.push({ a: rows[i].id, b: rows[j].id, score: Math.round(sc * 100) });
      }
      return { questions: rows, similar };
    }
    return { questions: rows };
  }
  if (p === '/revisions') return [];
  throw new Error('هذا الإجراء غير متاح في نسخة العرض؛ التعديل والاعتماد يتطلبان تشغيل المنصة على الخادم.');
}

function toast(msg, error = false) {
  const t = document.createElement('div');
  t.className = 'toast' + (error ? ' error' : '');
  t.setAttribute('role', error ? 'alert' : 'status');
  t.textContent = msg;
  document.body.append(t);
  setTimeout(() => t.remove(), error ? 6000 : 3000);
}
const fail = e => toast(e.errors?.length ? e.errors.join('، ') : e.message, true);

const isReviewer = () => ['reviewer', 'admin'].includes(state.user?.role);

const OBJ_STATUS = { pending: ['بانتظار المراجعة', ''], approved: ['معتمد', 'ok'], returned: ['أُعيد للتعديل', 'bad'] };
const Q_STATUS = {
  generated: ['مسودة مولدة', 'info'], in_review: ['قيد المراجعة', 'warn'],
  needs_revision: ['يحتاج إلى تعديل', 'bad'], approved: ['معتمد علميًا وتربويًا', 'ok'],
};
const AI_STATUS_KIND = {
  'سليم ويعتمد': 'ok', 'يحتاج إلى تحسين الصياغة': 'warn', 'يحتاج إلى فصل إلى هدفين': 'warn',
  'يحتاج إلى مراجعة علمية': 'bad', 'يحتاج إلى تحقق من المصدر': 'bad',
};
const COVERAGE_KIND = { 'مغطى': 'ok', 'جزئي': 'warn', 'غير موجود': 'bad' };
const badge = (text, kind = '') => `<span class="badge ${kind}">${esc(text)}</span>`;
const objBadge = s => badge(...OBJ_STATUS[s] || [s]);
const qBadge = s => badge(...Q_STATUS[s] || [s]);

function bar(value, total, cls = '') {
  return `<div class="bar ${cls}" role="progressbar" aria-valuenow="${pct(value, total)}" aria-valuemin="0" aria-valuemax="100">
    <span style="width:${pct(value, total)}%"></span></div>`;
}

function stimulusTable(s) {
  if (!s) return '';
  return `<div class="table-wrap"><table class="data-table"><thead><tr>${s.headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead>
    <tbody>${s.rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
const list = (arr, tag = 'ul') => (arr?.length ? `<${tag}>${arr.map(x => `<li>${esc(typeof x === 'string' ? x : x.element ?? x.description)}</li>`).join('')}</${tag}>` : '');

// ---------- الترويسة والجلسة ----------
function renderUserbox() {
  const box = document.getElementById('userbox');
  if (state.user) {
    const roles = { admin: 'مشرف', reviewer: 'مراجع', viewer: 'معلم (اطلاع)' };
    box.innerHTML = `<span class="muted">${esc(state.user.displayName)} · ${roles[state.user.role]}</span>
      <button type="button" id="logout">خروج</button>`;
    box.querySelector('#logout').onclick = async () => { await api('/logout', { method: 'POST' }); state.user = null; renderUserbox(); route(); };
  } else if (state.static) {
    box.innerHTML = `<span class="badge warn" title="البيانات منسوخة من قاعدة البيانات وقت النشر">نسخة عرض للقراءة فقط</span>`;
  } else {
    box.innerHTML = `<a class="btn" href="#/login">تسجيل الدخول</a>`;
  }
}

// ---------- الصفحات ----------
async function pageHome() {
  const s = await api('/stats');
  const o = s.objectives, q = s.questions;
  const chapters = await api('/chapters');
  $app.innerHTML = `
    ${state.static ? `<p class="notice">هذه <strong>نسخة عرض للقراءة فقط</strong> منشورة على GitHub Pages (البيانات بتاريخ ${esc((s.generatedAt || '').slice(0, 10))}). تظهر فيها الإجابات لغرض مراجعة النموذج الأولي؛ <strong>لا تشاركها مع الطلاب</strong>. الاعتماد والتعديل وحفظ البيانات تتطلب تشغيل المنصة على خادم.</p>` : ''}
    <div class="hero">
      <div>
        <h1>${esc(s.course?.title || 'كيمياء 2-1')}</h1>
        <p class="muted">${esc(s.course?.grade)} · الفصل الدراسي ${esc(s.course?.term)} · ${esc(s.course?.country)}</p>
        <p class="small muted">بنية المقرر: ${esc(s.course?.structure_source)}<br>مصدر المحتوى: ${esc(s.course?.content_source)}</p>
      </div>
      <div class="actions no-print">
        <a class="btn primary" href="#/chapters">تصفح الفصول</a>
        <a class="btn" href="#/bank">بنك الأسئلة</a>
      </div>
    </div>
    <div class="grid kpi">
      ${kpi(s.chapters, 'فصول')}${kpi(s.lessons, 'دروس')}${kpi(o.n, 'هدفًا تعليميًا')}
      ${kpi(q.mcq || 0, 'سؤال اختيار من متعدد')}${kpi(q.essay || 0, 'سؤالًا مقاليًا')}
    </div>
    <div class="grid cards" style="margin-top:1rem">
      <div class="card">
        <h2>مؤشرات المراجعة</h2>
        <div class="levels">
          ${progress('الأهداف التي روجعت', o.reviewed, o.n)}
          ${progress('الأهداف المعتمدة', o.approved, o.n, 'ok')}
          ${progress('الأسئلة التي روجعت', q.reviewed, q.n)}
          ${progress('الأسئلة المعتمدة', q.approved, q.n, 'ok')}
        </div>
        <p class="small muted" style="margin-top:.6rem">تُحسب المؤشرات مباشرة من قاعدة البيانات، ولا يدخل في مؤشرات الاعتماد إلا ما اعتمده مراجع بشري.</p>
      </div>
      <div class="card">
        <h2>التغطية التقويمية</h2>
        <div class="levels">
          ${progress('أهداف بلغت العدد المطلوب من الأسئلة (7 + 3)', s.coverage.complete, o.n)}
          ${progress('أهداف اكتملت أسئلتها المعتمدة', s.coverage.approved_complete, o.n, 'ok')}
          ${progress('محتوى مكمّل للمذكرة معتمد', s.supplements.approved, s.supplements.n, 'ok')}
        </div>
        <p class="small muted" style="margin-top:.6rem">اكتمل بنك الأسئلة لجميع الأهداف. اعتُمدت الأسئلة بقرار مالك المشروع دون مراجعة تفصيلية لكل سؤال، والتفاصيل في سجل كل سؤال.</p>
      </div>
    </div>
    <div class="section-title"><h2>الفصول</h2><a href="#/chapters">عرض الكل</a></div>
    <div class="grid cards">${chapters.map(chapterCard).join('')}</div>`;
}
const kpi = (v, l) => `<div class="card"><div class="value">${esc(v ?? 0)}</div><div class="label">${esc(l)}</div></div>`;
const progress = (label, v, t, cls = '') => `<div class="progress-line"><span>${esc(label)}</span>
  <span class="muted small">${v || 0} من ${t || 0} (${pct(v, t)}%)</span>${bar(v, t, cls)}</div>`;

function chapterCard(c) {
  return `<a class="card chapter-card" href="#/chapter/${c.number}">
    <div class="actions"><span class="chapter-num">${c.number}</span><h3 style="margin:0">${esc(c.title)}</h3></div>
    <div class="meta-row">${badge(`${c.lessons} دروس`)}${badge(`${c.objectives} هدفًا`)}${badge(`${c.questions} سؤالًا`, c.questions ? 'brand' : '')}</div>
    <div class="progress-line small"><span>الأهداف المعتمدة</span><span class="muted">${c.approved || 0}/${c.objectives}</span>${bar(c.approved, c.objectives, 'ok')}</div>
  </a>`;
}

async function pageChapters() {
  const chapters = await api('/chapters');
  $app.innerHTML = `<div class="crumbs"><a href="#/">الرئيسية</a> ‹ الفصول</div>
    <h1>فصول المقرر</h1><p class="muted">مرتبة وفق ملف أهداف المقرر المعتمد في المشروع.</p>
    <div class="grid cards">${chapters.map(chapterCard).join('')}</div>`;
}

async function pageChapter(n) {
  const ch = await api('/chapters/' + n);
  $app.innerHTML = `<div class="crumbs"><a href="#/">الرئيسية</a> ‹ <a href="#/chapters">الفصول</a> ‹ الفصل ${ch.number}</div>
    <h1>الفصل ${ch.number}: ${esc(ch.title)}</h1>
    ${ch.lessons.map(l => `
      <section class="card lesson" id="lesson-${l.number}">
        <div class="lesson-head">
          <h2>الدرس ${ch.number}-${l.number}: ${esc(l.title)}</h2>
          <span class="meta-row">${badge(`${l.objectives.length} هدفًا`)}
            ${badge(`${l.objectives.filter(o => o.reviewStatus === 'approved').length} معتمد`, 'ok')}</span>
        </div>
        ${l.source_note ? `<p class="small muted">${esc(l.source_note)}</p>` : ''}
        <ul class="obj-list">${l.objectives.map(o => `
          <li>
            <span class="obj-code">${esc(o.code)}</span>
            <a class="obj-text" href="#/objective/${encodeURIComponent(o.code)}">${esc(o.approvedText || o.originalText)}</a>
            <span class="obj-badges">${objBadge(o.reviewStatus)}
              ${o.mcq + o.essay ? badge(`${o.mcq}/${o.requiredMcq} اختيار · ${o.essay}/${o.requiredEssay} مقالي`,
                o.mcq >= o.requiredMcq && o.essay >= o.requiredEssay ? 'brand' : 'warn') : badge('لا أسئلة بعد')}
              ${o.memoCoverage ? badge('المذكرة: ' + o.memoCoverage, COVERAGE_KIND[o.memoCoverage]) : ''}</span>
          </li>`).join('')}
        </ul>
      </section>`).join('')}`;
}

// ---------- صفحة الهدف ----------
const objState = { mode: 'test', answers: {} };

async function pageObjective(code) {
  const data = await api('/objectives/' + encodeURIComponent(code));
  const { objective: o, supplement: s, questions } = data;
  if (!data.answersIncluded && objState.mode === 'review') objState.mode = 'test';
  const mcq = questions.filter(q => q.type === 'mcq'), essay = questions.filter(q => q.type === 'essay');
  const active = q => !q.excluded;
  const idx = data.lessonNav.indexOf(o.code);
  $app.innerHTML = `
    <div class="crumbs"><a href="#/">الرئيسية</a> ‹ <a href="#/chapter/${o.chapter.number}">الفصل ${o.chapter.number}: ${esc(o.chapter.title)}</a>
      ‹ <a href="#/chapter/${o.chapter.number}">الدرس ${o.chapter.number}-${o.lesson.number}: ${esc(o.lesson.title)}</a></div>
    <div class="print-only"><h2>${esc(o.chapter.title)} — ${esc(o.lesson.title)}</h2></div>
    <div class="hero">
      <div><span class="obj-code">${esc(o.code)}${o.originalCode ? ` (سابقًا ${esc(o.originalCode)})` : ''}</span>
        <h1>${esc(o.approvedText || o.proposedText || o.originalText)}</h1>
        <div class="meta-row">${objBadge(o.reviewStatus)}${o.thinkingLevel ? badge('مستوى التفكير: ' + o.thinkingLevel, 'brand') : ''}
          ${o.memoCoverage ? badge('تغطية المذكرة: ' + o.memoCoverage, COVERAGE_KIND[o.memoCoverage]) : ''}</div></div>
      <div class="actions no-print">
        ${idx > 0 ? `<a class="btn" href="#/objective/${data.lessonNav[idx - 1]}">→ الهدف السابق</a>` : ''}
        ${idx < data.lessonNav.length - 1 ? `<a class="btn" href="#/objective/${data.lessonNav[idx + 1]}">الهدف التالي ←</a>` : ''}
      </div>
    </div>

    <section class="card no-print">
      <h2>معلومات الهدف</h2>
      <div class="text-compare">
        <div class="text-box"><h4>نص الهدف الأصلي (من ملف الأهداف)</h4>${esc(o.originalText)}</div>
        <div class="text-box"><h4>الصياغة المقترحة (مراجعة آلية — غير معتمدة)</h4>${esc(o.proposedText || '—')}
          ${o.splitInto.length ? `<div class="small" style="margin-top:.35rem"><strong>أهداف مقترحة بالفصل:</strong>${list(o.splitInto)}</div>` : ''}</div>
        <div class="text-box"><h4>الصياغة المعتمدة</h4>${o.approvedText ? esc(o.approvedText) : '<span class="muted">لم تُعتمد بعد</span>'}</div>
      </div>
      <dl class="kv" style="margin-top:.85rem">
        <dt>الفصل والدرس</dt><dd>${esc(o.chapter.title)} ‹ ${esc(o.lesson.title)}</dd>
        <dt>حالة المراجعة الآلية</dt><dd>${o.aiReviewStatus ? badge(o.aiReviewStatus, AI_STATUS_KIND[o.aiReviewStatus]) : '—'}
          ${o.revisionType ? `<span class="small muted"> · نوع التعديل: ${esc(o.revisionType)}</span>` : ''}</dd>
        ${o.revisionReason ? `<dt>سبب التعديل</dt><dd>${esc(o.revisionReason)}</dd>` : ''}
        <dt>مستوى التفكير</dt><dd>${esc(o.thinkingLevel || '—')}</dd>
        <dt>نوع المعرفة</dt><dd>${esc(o.knowledgeType || '—')}</dd>
        <dt>المفاهيم المرتبطة</dt><dd>${o.concepts.map(c => badge(c)).join(' ') || '—'}</dd>
        <dt>المرجع في المذكرة</dt><dd>${o.memoPages.length ? 'صفحات PDF: ' + o.memoPages.join('، ') : '—'}${o.memoNote ? `<div class="small muted">${esc(o.memoNote)}</div>` : ''}</dd>
        ${o.duplicateOf ? `<dt>تكرار</dt><dd>${badge('مكرر للهدف ' + o.duplicateOf, 'warn')}</dd>` : ''}
      </dl>
      ${isReviewer() ? reviewPanel(o) : `<p class="small muted" style="margin-top:.6rem">اعتماد الهدف متاح للمراجعين بعد تسجيل الدخول.</p>`}
    </section>

    ${s ? supplementCard(s) : ''}

    <section class="card" id="mcq-section">
      <div class="section-title" style="margin-top:0">
        <h2>أسئلة الاختيار من متعدد <span class="muted small">(${mcq.filter(active).length} من ${o.requiredMcq} مطلوبة)</span></h2>
        <div class="actions no-print">
          <div class="seg" role="group" aria-label="نمط العرض">
            ${modeBtn('test', 'وضع الاختبار')}${modeBtn('practice', 'تدريب فوري')}${data.answersIncluded ? modeBtn('review', 'وضع المراجعة') : ''}
          </div>
          <button type="button" data-print="student">طباعة دون حلول</button>
          ${data.answersIncluded ? `<button type="button" data-print="teacher">طباعة مع الحلول</button>` : ''}
          ${isReviewer() ? `<button type="button" class="primary" data-add="mcq">+ سؤال اختيار</button>` : ''}
        </div>
      </div>
      ${modeHint(data.answersIncluded)}
      <div id="mcq-list">${mcq.length ? mcq.map(q => mcqCard(q, data.answersIncluded)).join('') : '<div class="empty">لا توجد أسئلة اختيار لهذا الهدف بعد.</div>'}</div>
      ${objState.mode === 'test' && mcq.length ? `<div class="actions no-print" style="margin-top:.8rem"><button type="button" class="primary" id="finish-test">إنهاء الاختبار وعرض النتيجة</button><span id="test-result"></span></div>` : ''}
    </section>

    <section class="card" id="essay-section">
      <div class="section-title" style="margin-top:0">
        <h2>الأسئلة المقالية <span class="muted small">(${essay.filter(active).length} من ${o.requiredEssay} مطلوبة)</span></h2>
        ${isReviewer() ? `<button type="button" class="primary no-print" data-add="essay">+ سؤال مقالي</button>` : ''}
      </div>
      ${essay.length ? essay.map(q => essayCard(q, data.answersIncluded)).join('') : '<div class="empty">لا توجد أسئلة مقالية لهذا الهدف بعد.</div>'}
    </section>`;
  bindObjective(o, questions);
}

const modeBtn = (m, label) => `<button type="button" class="${objState.mode === m ? 'on' : ''}" data-mode="${m}">${label}</button>`;
function modeHint(answers) {
  const t = {
    test: 'وضع الاختبار: لا تظهر الإجابات الصحيحة؛ اختر إجاباتك ثم اضغط «إنهاء الاختبار».',
    practice: 'التدريب الفوري: تظهر التغذية الراجعة مباشرة بعد اختيار كل إجابة.',
    review: 'وضع المراجعة: تظهر الإجابات والتفسيرات وأدوات المراجعة.',
  };
  return `<p class="notice info no-print">${t[objState.mode]}${!answers ? ' الإجابات النموذجية للأسئلة المقالية تظهر للمعلمين والمراجعين بعد تسجيل الدخول.' : ''}</p>`;
}

function reviewPanel(o) {
  return `<div class="card" style="margin-top:1rem;background:var(--surface-2)">
    <h3>مراجعة الهدف واعتماده</h3>
    <div class="field"><label for="approved-text">الصياغة التي ستُعتمد</label>
      <textarea id="approved-text">${esc(o.approvedText || o.proposedText || o.originalText)}</textarea></div>
    <div class="form-grid">
      <div class="field"><label for="req-mcq">عدد أسئلة الاختيار المطلوب</label><input id="req-mcq" type="number" min="0" max="30" value="${o.requiredMcq}"></div>
      <div class="field"><label for="req-essay">عدد الأسئلة المقالية المطلوب</label><input id="req-essay" type="number" min="0" max="30" value="${o.requiredEssay}"></div>
    </div>
    <div class="field"><label for="review-note">ملاحظات المراجع (إلزامية عند الإعادة)</label><textarea id="review-note"></textarea></div>
    <div class="actions">
      <button type="button" class="ok" data-review="approve">اعتماد الهدف</button>
      <button type="button" class="danger" data-review="return">إعادة للتعديل</button>
      <button type="button" data-review="reset">إلغاء الاعتماد</button>
      <button type="button" id="save-counts">حفظ الأعداد المطلوبة</button>
    </div></div>`;
}

function supplementCard(s) {
  return `<section class="card no-print">
    <div class="section-title" style="margin-top:0"><h2>المحتوى العلمي المكمّل</h2>
      <span class="meta-row">${objBadge(s.reviewStatus)}${badge(s.confidence === 'high' ? 'ثقة مرتفعة' : 'يحتاج تحققًا من الصياغة', s.confidence === 'high' ? 'brand' : 'warn')}</span></div>
    <p class="notice">هذا المحتوى أكمله الوكيل الكيميائي التربوي (ذكاء اصطناعي) لأن المذكرة تركته فراغًا أو لم تتناوله؛ <strong>ليس من نص المذكرة</strong> ولا يُعد معتمدًا حتى يعتمده مراجع.</p>
    ${s.memoBasis ? `<p><strong>ما تقدمه المذكرة:</strong> ${esc(s.memoBasis)}</p>` : ''}
    <p id="sup-text">${esc(s.supplement)}</p>
    ${s.keyPoints.length ? `<h3>نقاط أساسية</h3>${list(s.keyPoints)}` : ''}
    ${s.misconceptions.length ? `<h3>تصورات خاطئة شائعة</h3>${list(s.misconceptions)}` : ''}
    ${s.scientificNotes ? `<p class="small muted"><strong>ملاحظات علمية:</strong> ${esc(s.scientificNotes)}</p>` : ''}
    ${isReviewer() ? `<div class="actions">
      <button type="button" class="ok" data-sup="approve">اعتماد المحتوى</button>
      <button type="button" data-sup="edit">تعديل</button>
      <button type="button" class="danger" data-sup="return">إعادة للمراجعة</button></div>` : ''}
  </section>`;
}

function qMeta(q) {
  return `<span class="meta-row">${qBadge(q.status)}${q.thinkingLevel ? badge(q.thinkingLevel) : ''}${q.difficulty ? badge(q.difficulty) : ''}
    ${q.questionKind ? badge(q.questionKind) : ''}${q.excluded ? badge('مستبعد', 'bad') : ''}</span>`;
}

function mcqCard(q, answers) {
  const mode = objState.mode, chosen = objState.answers[q.id];
  const showKey = mode === 'review' && answers;
  const opts = q.options.map((op, i) => {
    let cls = 'opt';
    if (showKey && i === q.correctIndex) cls += ' correct';
    if (chosen?.checked) { if (i === chosen.correctIndex) cls += ' correct'; else if (i === chosen.choice) cls += ' wrong'; }
    else if (chosen && chosen.choice === i) cls += ' selected';
    const inner = `<span class="letter">${LETTERS[i]})</span><span>${esc(op)}</span>`;
    return mode === 'review' ? `<li class="${cls}">${inner}</li>`
      : `<li><button type="button" class="${cls}" data-choose="${q.id}:${i}" aria-pressed="${chosen?.choice === i}">${inner}</button></li>`;
  }).join('');
  // الحل يُطبع في نسخة المعلم فقط (يُخفى في نسخة الطالب عبر CSS)
  const key = answers ? `<div class="answer ${showKey ? '' : 'print-only'}">
      <h4>الإجابة الصحيحة: ${LETTERS[q.correctIndex]}) ${esc(q.options[q.correctIndex])}</h4>
      <div>${esc(q.explanation)}</div>
      ${q.distractorNotes?.some(Boolean) ? `<h4>سبب خطأ البدائل الأخرى</h4><ul>${q.distractorNotes.map((n, i) => n ? `<li>${LETTERS[i]}) ${esc(n)}</li>` : '').join('')}</ul>` : ''}
      ${q.sourceRef ? `<div class="small muted">المرجع: ${esc(q.sourceRef)}</div>` : ''}
    </div>` : '';
  const feedback = chosen?.checked && mode === 'practice' ? `<div class="notice ${chosen.correct ? 'ok' : 'bad'}" style="margin-top:.5rem">
      ${chosen.correct ? 'إجابة صحيحة.' : `إجابة غير صحيحة؛ الصحيحة (${LETTERS[chosen.correctIndex]}).`} ${esc(chosen.explanation)}
      ${!chosen.correct && chosen.distractorNote ? `<div class="small">${esc(chosen.distractorNote)}</div>` : ''}</div>` : '';
  return `<article class="q ${q.excluded ? 'excluded' : ''}" id="q-${q.id}">
    <div class="q-head"><span class="q-num">سؤال ${q.number}</span>${mode === 'review' ? qMeta(q) : ''}</div>
    <div class="q-stem">${esc(q.stem)}</div>${stimulusTable(q.stimulus)}
    <ol class="opts">${opts}</ol>${feedback}${key}
    ${showKey ? reviewTools(q) : ''}
  </article>`;
}

function essayCard(q, answers) {
  const body = answers ? `<details class="answer-wrap" ${objState.mode === 'review' ? 'open' : ''}><summary class="no-print btn" style="margin-top:.5rem">الإجابة النموذجية وسلم التصحيح</summary>
    <div class="answer">
      <h4>الإجابة النموذجية</h4><div>${esc(q.modelAnswer)}</div>
      ${q.answerElements?.length ? `<h4>عناصر الإجابة الأساسية</h4>${list(q.answerElements)}` : ''}
      ${q.solutionSteps?.length ? `<h4>خطوات الحل</h4>${list(q.solutionSteps, 'ol')}` : ''}
      ${q.marks?.length ? `<h4>توزيع الدرجات (${q.marks.reduce((a, m) => a + Number(m.marks || 0), 0)} درجات)</h4>
        <ul>${q.marks.map(m => `<li>${esc(m.element)}: ${esc(m.marks)}</li>`).join('')}</ul>` : ''}
      ${q.rubric?.length ? `<h4>سلم التصحيح</h4><div class="table-wrap"><table class="data-table"><tbody>
        ${q.rubric.map(r => `<tr><th>${esc(r.level)}</th><td>${esc(r.description)}</td></tr>`).join('')}</tbody></table></div>` : ''}
      ${q.commonErrors?.length ? `<h4>أخطاء علمية شائعة ينبغي الانتباه إليها</h4>${list(q.commonErrors)}` : ''}
      ${q.sourceRef ? `<div class="small muted">المرجع: ${esc(q.sourceRef)}</div>` : ''}
    </div></details>` : '';
  return `<article class="q ${q.excluded ? 'excluded' : ''}" id="q-${q.id}">
    <div class="q-head"><span class="q-num">سؤال مقالي ${q.number}</span>${answers ? qMeta(q) : ''}</div>
    <div class="q-stem">${esc(q.stem)}</div>${stimulusTable(q.stimulus)}${body}
    ${objState.mode === 'review' && answers ? reviewTools(q) : ''}
  </article>`;
}

function reviewTools(q) {
  const ac = q.autoCheck;
  return `<details class="no-print" style="margin-top:.5rem"><summary class="small muted">التحقق الآلي ${ac ? (ac.passed ? '— اجتاز' : '— يوجد تنبيهات') : ''} وملاحظات المراجع</summary>
      ${ac ? `<ul class="checks">${ac.checks.map(c => `<li class="${c.ok ? '' : 'fail'}">${esc(c.label)}</li>`).join('')}</ul>
      <p class="small muted">التحقق الآلي يفحص البنية فقط ولا يُعد مراجعة علمية بشرية.</p>` : ''}
      ${q.reviewerNotes ? `<p class="small"><strong>ملاحظات المراجع:</strong> ${esc(q.reviewerNotes)}</p>` : ''}
    </details>
    ${isReviewer() ? `<div class="q-tools">
      <button type="button" class="ok" data-qstatus="${q.id}:approved">اعتماد</button>
      <button type="button" data-qstatus="${q.id}:in_review">قيد المراجعة</button>
      <button type="button" class="danger" data-qstatus="${q.id}:needs_revision">يحتاج إلى تعديل</button>
      <button type="button" data-qedit="${q.id}">تعديل</button>
      <button type="button" data-qdup="${q.id}">نسخ</button>
      <button type="button" data-qexclude="${q.id}:${q.excluded ? 0 : 1}">${q.excluded ? 'إرجاع' : 'استبعاد'}</button>
      <button type="button" data-qhist="${q.id}">سجل التعديلات</button>
    </div>` : ''}`;
}

function bindObjective(o, questions) {
  const reload = () => pageObjective(o.code).catch(fail);
  $app.querySelectorAll('[data-mode]').forEach(b => b.onclick = () => { objState.mode = b.dataset.mode; objState.answers = {}; reload(); });
  $app.querySelectorAll('[data-print]').forEach(b => b.onclick = () => printAs(b.dataset.print));
  $app.querySelectorAll('[data-choose]').forEach(b => b.onclick = async () => {
    const [id, i] = b.dataset.choose.split(':').map(Number);
    if (objState.answers[id]?.checked) return;
    if (objState.mode === 'practice') {
      try { objState.answers[id] = { choice: i, checked: true, ...(await api(`/questions/${id}/check`, { method: 'POST', body: { choice: i } })) }; }
      catch (e) { return fail(e); }
    } else objState.answers[id] = { choice: i };
    reload();
  });
  const finish = document.getElementById('finish-test');
  if (finish) finish.onclick = async () => {
    const mcq = questions.filter(q => q.type === 'mcq' && !q.excluded);
    let right = 0;
    try {
      for (const q of mcq) {
        const a = objState.answers[q.id];
        if (!a) continue;
        const r = await api(`/questions/${q.id}/check`, { method: 'POST', body: { choice: a.choice } });
        objState.answers[q.id] = { ...a, ...r, checked: true };
        if (r.correct) right++;
      }
    } catch (e) { return fail(e); }
    objState.mode = 'practice';
    await reload();
    toast(`النتيجة: ${right} من ${mcq.length}`);
  };
  $app.querySelectorAll('[data-review]').forEach(b => b.onclick = async () => {
    try {
      await api(`/objectives/${o.code}/review`, { method: 'POST', body: {
        action: b.dataset.review, approved_text: document.getElementById('approved-text').value, note: document.getElementById('review-note').value } });
      toast('تم حفظ قرار المراجعة'); reload();
    } catch (e) { fail(e); }
  });
  const sc = document.getElementById('save-counts');
  if (sc) sc.onclick = async () => {
    try {
      await api(`/objectives/${o.code}`, { method: 'PATCH', body: {
        required_mcq: Number(document.getElementById('req-mcq').value), required_essay: Number(document.getElementById('req-essay').value) } });
      toast('تم حفظ الأعداد المطلوبة'); reload();
    } catch (e) { fail(e); }
  };
  $app.querySelectorAll('[data-sup]').forEach(b => b.onclick = async () => {
    const action = b.dataset.sup;
    if (action === 'edit') return editSupplement(o.code, document.getElementById('sup-text').textContent, reload);
    let note = '';
    if (action === 'return') { note = prompt('سبب الإعادة للمراجعة:') || ''; if (!note.trim()) return; }
    try { await api(`/objectives/${o.code}/supplement-review`, { method: 'POST', body: { action, note } }); toast('تم الحفظ'); reload(); }
    catch (e) { fail(e); }
  });
  $app.querySelectorAll('[data-qstatus]').forEach(b => b.onclick = async () => {
    const [id, status] = b.dataset.qstatus.split(':');
    let note = null;
    if (status === 'needs_revision') { note = prompt('ما المطلوب تعديله؟') || ''; if (!note.trim()) return; }
    try { await api(`/questions/${id}/status`, { method: 'POST', body: { status, note } }); toast('تم تحديث حالة السؤال'); reload(); }
    catch (e) { fail(e); }
  });
  $app.querySelectorAll('[data-qexclude]').forEach(b => b.onclick = async () => {
    const [id, ex] = b.dataset.qexclude.split(':').map(Number);
    let note = '';
    if (ex) { note = prompt('سبب الاستبعاد (يُحفظ في سجل التعديلات):') || ''; if (!note.trim()) return; }
    try { await api(`/questions/${id}/exclude`, { method: 'POST', body: { excluded: !!ex, note } }); reload(); } catch (e) { fail(e); }
  });
  $app.querySelectorAll('[data-qdup]').forEach(b => b.onclick = async () => {
    try { await api(`/questions/${b.dataset.qdup}/duplicate`, { method: 'POST' }); toast('أُنشئت نسخة من السؤال'); reload(); } catch (e) { fail(e); }
  });
  $app.querySelectorAll('[data-qedit]').forEach(b => b.onclick = () => {
    const q = questions.find(x => x.id === Number(b.dataset.qedit));
    openEditor(q.type, q, async body => { await api(`/questions/${q.id}`, { method: 'PATCH', body }); }, reload);
  });
  $app.querySelectorAll('[data-add]').forEach(b => b.onclick = () =>
    openEditor(b.dataset.add, null, async body => { await api(`/objectives/${o.code}/questions`, { method: 'POST', body: { ...body, type: b.dataset.add } }); }, reload));
  $app.querySelectorAll('[data-qhist]').forEach(b => b.onclick = () => showHistory(Number(b.dataset.qhist)));
}

function printAs(kind) {
  document.body.classList.remove('print-student', 'print-teacher');
  document.body.classList.add('print-' + kind);
  window.print();
}

// ---------- النوافذ ----------
function dialog(title, body, buttons) {
  $dlg.innerHTML = `<div class="dlg-head"><h2 style="margin:0">${esc(title)}</h2><button type="button" data-close aria-label="إغلاق">✕</button></div>
    <div class="dlg-body">${body}</div><div class="dlg-foot">${buttons}<button type="button" data-close>إغلاق</button></div>`;
  $dlg.querySelectorAll('[data-close]').forEach(b => b.onclick = () => $dlg.close());
  $dlg.showModal();
  return $dlg;
}

function editSupplement(code, text, done) {
  const d = dialog('تعديل المحتوى المكمّل', `<label for="sup-edit">النص</label><textarea id="sup-edit" style="min-height:12rem">${esc(text)}</textarea>
    <label for="sup-note" style="margin-top:.6rem">ملاحظة التعديل</label><input id="sup-note">`,
  `<button type="button" class="primary" id="sup-save">حفظ (يبقى بانتظار الاعتماد)</button>`);
  d.querySelector('#sup-save').onclick = async () => {
    try {
      await api(`/objectives/${code}/supplement-review`, { method: 'POST', body: {
        action: 'reset', supplement: d.querySelector('#sup-edit').value, note: d.querySelector('#sup-note').value } });
      d.close(); toast('تم حفظ التعديل'); done();
    } catch (e) { fail(e); }
  };
}

const LEVEL_OPTS = ['تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع'];
const sel = (id, opts, v) => `<select id="${id}"><option value="">—</option>${opts.map(o => `<option ${o === v ? 'selected' : ''}>${o}</option>`).join('')}</select>`;
const lines = a => (a || []).map(x => typeof x === 'string' ? x : '').join('\n');
const pairs = (a, k1, k2) => (a || []).map(x => `${x[k1]} | ${x[k2]}`).join('\n');
const parseLines = v => v.split('\n').map(s => s.trim()).filter(Boolean);
const parsePairs = (v, k1, k2, num) => parseLines(v).map(l => {
  const [a, ...b] = l.split('|');
  return { [k1]: a.trim(), [k2]: num ? Number(b.join('|').trim()) : b.join('|').trim() };
});

function openEditor(type, q, save, done) {
  q = q || { options: ['', '', ''], correctIndex: 0 };
  const common = `
    <div class="field"><label for="e-stem">نص السؤال</label><textarea id="e-stem">${esc(q.stem)}</textarea></div>
    <div class="form-grid">
      <div class="field"><label for="e-level">مستوى التفكير</label>${sel('e-level', LEVEL_OPTS, q.thinkingLevel)}</div>
      <div class="field"><label for="e-diff">درجة الصعوبة</label>${sel('e-diff', ['سهل', 'متوسط', 'صعب'], q.difficulty)}</div>
      <div class="field"><label for="e-kind">نوع السؤال</label><input id="e-kind" value="${esc(q.questionKind)}"></div>
      <div class="field"><label for="e-src">المرجع</label><input id="e-src" value="${esc(q.sourceRef)}"></div>
    </div>`;
  const mcq = `${q.options.map((op, i) => `
      <div class="field"><label for="e-opt${i}">البديل ${LETTERS[i]} ${i === q.correctIndex ? '(الصحيح حاليًا)' : ''}</label>
        <input id="e-opt${i}" value="${esc(op)}"></div>`).join('')}
    <div class="field"><label for="e-correct">الإجابة الصحيحة</label>
      <select id="e-correct">${LETTERS.map((l, i) => `<option value="${i}" ${i === q.correctIndex ? 'selected' : ''}>${l}</option>`).join('')}</select></div>
    <div class="field"><label for="e-expl">تفسير الإجابة الصحيحة</label><textarea id="e-expl">${esc(q.explanation)}</textarea></div>
    <div class="field"><label for="e-dist">سبب خطأ البدائل (سطر لكل بديل بالترتيب، واترك سطر الصحيح فارغًا)</label>
      <textarea id="e-dist">${esc((q.distractorNotes || ['', '', '']).join('\n'))}</textarea></div>`;
  const essay = `
    <div class="field"><label for="e-model">الإجابة النموذجية</label><textarea id="e-model" style="min-height:7rem">${esc(q.modelAnswer)}</textarea></div>
    <div class="field"><label for="e-elems">عناصر الإجابة (سطر لكل عنصر)</label><textarea id="e-elems">${esc(lines(q.answerElements))}</textarea></div>
    <div class="field"><label for="e-steps">خطوات الحل (سطر لكل خطوة)</label><textarea id="e-steps">${esc(lines(q.solutionSteps))}</textarea></div>
    <div class="field"><label for="e-marks">توزيع الدرجات (العنصر | الدرجة)</label><textarea id="e-marks">${esc(pairs(q.marks, 'element', 'marks'))}</textarea></div>
    <div class="field"><label for="e-rubric">سلم التصحيح (المستوى | الوصف)</label><textarea id="e-rubric">${esc(pairs(q.rubric, 'level', 'description'))}</textarea></div>
    <div class="field"><label for="e-errors">الأخطاء الشائعة (سطر لكل خطأ)</label><textarea id="e-errors">${esc(lines(q.commonErrors))}</textarea></div>`;
  const d = dialog(q.id ? `تعديل السؤال ${q.number}` : (type === 'mcq' ? 'سؤال اختيار جديد' : 'سؤال مقالي جديد'),
    `${q.stimulus ? '<p class="notice info">جدول البيانات المرفق بالسؤال يبقى كما هو.</p>' : ''}${common}${type === 'mcq' ? mcq : essay}
     <p class="small muted">أي تعديل على سؤال معتمد يعيده إلى «قيد المراجعة»، ويُحفظ الإصدار السابق في سجل التعديلات.</p>`,
    `<button type="button" class="primary" id="e-save">حفظ</button>`);
  const v = id => d.querySelector('#' + id).value;
  d.querySelector('#e-save').onclick = async () => {
    const body = { stem: v('e-stem'), thinking_level: v('e-level') || null, difficulty: v('e-diff') || null,
      question_kind: v('e-kind'), source_ref: v('e-src'), stimulus: q.stimulus || null };
    if (type === 'mcq') Object.assign(body, { options: [0, 1, 2].map(i => v('e-opt' + i)), correct_index: Number(v('e-correct')),
      explanation: v('e-expl'), distractor_notes: [0, 1, 2].map(i => v('e-dist').split('\n')[i] || '') });
    else Object.assign(body, { model_answer: v('e-model'), answer_elements: parseLines(v('e-elems')), solution_steps: parseLines(v('e-steps')),
      marks: parsePairs(v('e-marks'), 'element', 'marks', true), rubric: parsePairs(v('e-rubric'), 'level', 'description'), common_errors: parseLines(v('e-errors')) });
    try { await save(body); d.close(); toast('تم الحفظ'); done(); } catch (e) { fail(e); }
  };
}

async function showHistory(id) {
  try {
    const rows = await api(`/questions/${id}/revisions`);
    const names = { create: 'إنشاء', edit: 'تعديل', status: 'تغيير الحالة', exclude: 'استبعاد', restore: 'إرجاع', duplicate: 'نسخ' };
    dialog('سجل تعديلات السؤال', rows.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>التاريخ</th><th>المستخدم</th><th>الإجراء</th><th>ملاحظة</th></tr></thead>
      <tbody>${rows.map(r => `<tr><td class="ltr">${esc(r.at)}</td><td>${esc(r.user || 'النظام')}</td><td>${esc(names[r.action] || r.action)}
      ${r.action === 'status' ? `: ${esc(Q_STATUS[r.after_json?.status]?.[0] || '')}` : ''}</td><td>${esc(r.note || '')}</td></tr>`).join('')}</tbody></table></div>`
      : '<div class="empty">لا توجد تعديلات مسجلة؛ السؤال على حالته المولدة.</div>', '');
  } catch (e) { fail(e); }
}

// ---------- بنك الأسئلة ----------
const bankFilter = {};
async function pageBank() {
  const chapters = await api('/chapters');
  const lessons = bankFilter.chapter ? (await api('/chapters/' + bankFilter.chapter)).lessons : [];
  const qs = new URLSearchParams(Object.entries(bankFilter).filter(([, v]) => v));
  const res = await api('/bank?' + qs.toString());
  const answers = !!state.user;
  const f = (k, label, opts) => `<div><label for="f-${k}">${label}</label><select id="f-${k}" data-f="${k}"><option value="">الكل</option>
    ${opts.map(([v, t]) => `<option value="${esc(v)}" ${String(bankFilter[k] || '') === String(v) ? 'selected' : ''}>${esc(t)}</option>`).join('')}</select></div>`;
  $app.innerHTML = `<div class="crumbs no-print"><a href="#/">الرئيسية</a> ‹ بنك الأسئلة</div>
    <div class="hero no-print"><div><h1>بنك الأسئلة</h1><p class="muted">بحث وتصفية وإنشاء أوراق أسئلة لهدف أو درس أو فصل أو اختبار شامل.</p></div>
      <div class="actions">${isReviewer() ? `<a class="btn" href="api/export/questions.csv">تصدير الأسئلة CSV</a><a class="btn" href="api/export/objectives.csv">تصدير الأهداف CSV</a>` : ''}</div></div>
    <section class="card no-print">
      <div class="filters">
        ${f('chapter', 'الفصل', chapters.map(c => [c.number, `${c.number}. ${c.title}`]))}
        ${f('lesson', 'الدرس', lessons.map(l => [l.number, `${l.number}. ${l.title}`]))}
        ${f('type', 'نوع السؤال', [['mcq', 'اختيار من متعدد'], ['essay', 'مقالي']])}
        ${f('level', 'مستوى التفكير', LEVEL_OPTS.map(l => [l, l]))}
        ${f('difficulty', 'الصعوبة', [['سهل', 'سهل'], ['متوسط', 'متوسط'], ['صعب', 'صعب']])}
        ${f('status', 'حالة المراجعة', Object.entries(Q_STATUS).map(([k, [t]]) => [k, t]))}
        <div><label for="f-q">بحث بالكلمات</label><input id="f-q" value="${esc(bankFilter.q || '')}" placeholder="مثال: الفوتون"></div>
        <div class="actions"><button type="button" class="primary" id="f-apply">بحث</button><button type="button" id="f-clear">مسح</button></div>
      </div>
    </section>
    <div class="section-title no-print"><h2>${res.questions.length} سؤالًا ${state.selection.size ? `· المحدد للاختبار: ${state.selection.size}` : ''}</h2>
      <div class="actions">
        <button type="button" id="sel-all">تحديد نتائج البحث</button><button type="button" id="sel-none">إلغاء التحديد</button>
        <button type="button" data-sheet="student">ورقة الطالب</button>
        ${answers ? `<button type="button" data-sheet="teacher">نسخة المعلم (مع الإجابات)</button>` : ''}
        <button type="button" id="similar">اكتشاف المتشابهة</button>
      </div></div>
    <p class="small muted no-print">الورقة تُنشأ من الأسئلة المحددة، وإن لم تحدد شيئًا فمن نتائج البحث الحالية. لإنشاء ورقة هدف أو درس أو فصل اختر التصفية المناسبة.</p>
    <div id="similar-out"></div>
    <div id="bank-list">${res.questions.length ? res.questions.map(q => bankRow(q)).join('') : '<div class="empty">لا توجد أسئلة مطابقة.</div>'}</div>`;
  $app.querySelectorAll('[data-f]').forEach(s => s.onchange = () => {
    bankFilter[s.dataset.f] = s.value; if (s.dataset.f === 'chapter') delete bankFilter.lesson; pageBank().catch(fail);
  });
  document.getElementById('f-apply').onclick = () => { bankFilter.q = document.getElementById('f-q').value.trim(); pageBank().catch(fail); };
  document.getElementById('f-q').onkeydown = e => { if (e.key === 'Enter') document.getElementById('f-apply').click(); };
  document.getElementById('f-clear').onclick = () => { for (const k in bankFilter) delete bankFilter[k]; pageBank().catch(fail); };
  document.getElementById('sel-all').onclick = () => { res.questions.forEach(q => state.selection.add(q.id)); pageBank().catch(fail); };
  document.getElementById('sel-none').onclick = () => { state.selection.clear(); pageBank().catch(fail); };
  $app.querySelectorAll('[data-pick]').forEach(c => c.onchange = () => {
    const id = Number(c.dataset.pick); c.checked ? state.selection.add(id) : state.selection.delete(id);
  });
  $app.querySelectorAll('[data-sheet]').forEach(b => b.onclick = () => buildSheet(b.dataset.sheet, res.questions));
  document.getElementById('similar').onclick = async () => {
    try {
      const r = await api('/bank?' + new URLSearchParams({ ...Object.fromEntries(qs), similar: '1' }).toString());
      document.getElementById('similar-out').innerHTML = `<div class="notice ${r.similar.length ? '' : 'ok'}">${r.similar.length
        ? 'أزواج متشابهة للمراجعة: ' + r.similar.map(p => `#${p.a} و#${p.b} (${p.score}%)`).join('، ')
        : 'لا توجد أسئلة متشابهة بدرجة مرتفعة ضمن النتائج.'}</div>`;
    } catch (e) { fail(e); }
  };
}

function bankRow(q) {
  return `<article class="q" id="q-${q.id}">
    <div class="q-head"><label class="actions" style="margin:0;color:var(--ink)"><input type="checkbox" style="width:auto" data-pick="${q.id}" ${state.selection.has(q.id) ? 'checked' : ''}>
      <span class="q-num">#${q.id} · ${q.type === 'mcq' ? 'اختيار' : 'مقالي'}</span></label>${qMeta(q)}</div>
    <div class="small muted">الفصل ${q.chapter.number} ‹ ${esc(q.lesson.title)} ‹ <a href="#/objective/${q.objectiveCode}">${esc(q.objectiveCode)}</a>: ${esc(q.objectiveText)}</div>
    <div class="q-stem">${esc(q.stem)}</div>${stimulusTable(q.stimulus)}
    ${q.type === 'mcq' ? `<ol class="opts">${q.options.map((o, i) => `<li class="opt ${state.user && i === q.correctIndex ? 'correct' : ''}"><span class="letter">${LETTERS[i]})</span><span>${esc(o)}</span></li>`).join('')}</ol>` : ''}
  </article>`;
}

function buildSheet(kind, current) {
  const picked = state.selection.size ? current.filter(q => state.selection.has(q.id)) : current;
  if (state.selection.size && picked.length < state.selection.size) toast('بعض الأسئلة المحددة خارج نتائج البحث الحالية ولن تظهر؛ امسح التصفية لإظهارها.', true);
  if (!picked.length) return toast('لا توجد أسئلة لإنشاء الورقة', true);
  const teacher = kind === 'teacher';
  const mcq = picked.filter(q => q.type === 'mcq'), essay = picked.filter(q => q.type === 'essay');
  const title = prompt('عنوان الورقة:', 'اختبار كيمياء 2-1') ?? 'اختبار كيمياء 2-1';
  const w = `<div class="card"><h1>${esc(title)}</h1><p>${teacher ? 'نسخة المعلم — مع الإجابات ومفتاح التصحيح' : 'الاسم: ........................ الصف: ........'}</p></div>
    ${mcq.length ? `<h2 style="margin-top:1rem">أولًا: اختر الإجابة الصحيحة</h2>${mcq.map((q, n) => `<div class="q"><div class="q-stem">${n + 1}. ${esc(q.stem)}</div>${stimulusTable(q.stimulus)}
      <ol class="opts">${q.options.map((o, i) => `<li class="opt ${teacher && i === q.correctIndex ? 'correct' : ''}"><span class="letter">${LETTERS[i]})</span><span>${esc(o)}</span></li>`).join('')}</ol>
      ${teacher ? `<div class="answer"><strong>الإجابة: ${LETTERS[q.correctIndex]}</strong> — ${esc(q.explanation)}</div>` : ''}</div>`).join('')}` : ''}
    ${essay.length ? `<h2 style="margin-top:1rem">ثانيًا: الأسئلة المقالية</h2>${essay.map((q, n) => `<div class="q"><div class="q-stem">${n + 1}. ${esc(q.stem)}</div>${stimulusTable(q.stimulus)}
      ${teacher ? `<div class="answer"><h4>الإجابة النموذجية</h4>${esc(q.modelAnswer)}
        ${q.marks?.length ? `<h4>توزيع الدرجات</h4><ul>${q.marks.map(m => `<li>${esc(m.element)}: ${esc(m.marks)}</li>`).join('')}</ul>` : ''}</div>`
        : '<div style="height:7rem;border-bottom:1px dashed var(--line)"></div>'}</div>`).join('')}` : ''}
    ${teacher && mcq.length ? `<div class="card" style="margin-top:1rem"><h2>مفتاح الإجابات</h2><p>${mcq.map((q, n) => `${n + 1}) ${LETTERS[q.correctIndex]}`).join(' — ')}</p></div>` : ''}`;
  $app.innerHTML = `<div class="actions no-print" style="margin-bottom:1rem"><button type="button" class="primary" id="do-print">طباعة</button>
    <button type="button" id="back">رجوع إلى البنك</button></div>${w}`;
  document.getElementById('do-print').onclick = () => printAs(teacher ? 'teacher' : 'student');
  document.getElementById('back').onclick = () => pageBank().catch(fail);
}

// ---------- التقارير ----------
async function pageReports() {
  const s = await api('/stats');
  const o = s.objectives, q = s.questions;
  const maxLevel = Math.max(1, ...s.levels.map(l => l.n));
  const maxCh = Math.max(1, ...s.byChapter.map(c => c.questions));
  $app.innerHTML = `<div class="crumbs"><a href="#/">الرئيسية</a> ‹ التقارير</div><h1>التقارير والمؤشرات</h1>
    <p class="muted">تُحسب كل الأرقام لحظيًا من قاعدة البيانات.</p>
    <div class="grid kpi">${kpi(o.n, 'إجمالي الأهداف')}${kpi(o.reviewed || 0, 'أهداف روجعت')}${kpi(o.approved || 0, 'أهداف معتمدة')}
      ${kpi(o.returned || 0, 'أهداف تحتاج إلى تعديل')}${kpi(q.mcq || 0, 'أسئلة اختيار')}${kpi(q.essay || 0, 'أسئلة مقالية')}
      ${kpi(q.approved || 0, 'أسئلة معتمدة')}${kpi((q.n || 0) - (q.approved || 0), 'أسئلة تحتاج إلى مراجعة')}</div>
    <div class="grid cards" style="margin-top:1rem">
      <section class="card"><h2>توزيع الأهداف حسب مستوى التفكير</h2><p class="small muted">تصنيف مقترح آليًا حتى يعتمده المراجع.</p>
        <div class="levels">${s.levels.map(l => `<div class="progress-line"><span>${esc(l.level)}</span><span class="muted small">${l.n}</span>${bar(l.n, maxLevel)}</div>`).join('')}</div></section>
      <section class="card"><h2>توزيع الأسئلة حسب الفصول</h2>
        <div class="levels">${s.byChapter.map(c => `<div class="progress-line"><span>${c.number}. ${esc(c.title)}</span><span class="muted small">${c.questions}</span>${bar(c.questions, maxCh)}</div>`).join('')}</div></section>
      <section class="card"><h2>اكتمال التغطية التقويمية</h2><div class="levels">
        ${progress('أهداف لها العدد المطلوب من الأسئلة', s.coverage.complete, o.n)}
        ${progress('أهداف بدأ إنتاج أسئلتها', s.coverage.started, o.n)}
        ${progress('أهداف اكتملت أسئلتها المعتمدة', s.coverage.approved_complete, o.n, 'ok')}</div></section>
    </div>
    ${isReviewer() ? `<section class="card" style="margin-top:1rem"><h2>آخر التعديلات</h2><div id="revs" class="table-wrap">جارٍ التحميل…</div></section>` : ''}`;
  if (isReviewer()) {
    const rows = await api('/revisions?limit=50');
    document.getElementById('revs').innerHTML = rows.length ? `<table class="list"><thead><tr><th>التاريخ</th><th>المستخدم</th><th>العنصر</th><th>الإجراء</th><th>ملاحظة</th></tr></thead>
      <tbody>${rows.map(r => `<tr><td class="ltr">${esc(r.at)}</td><td>${esc(r.user || '')}</td><td>${esc(r.entity)} #${r.entity_id}</td><td>${esc(r.action)}</td><td>${esc(r.note || '')}</td></tr>`).join('')}</tbody></table>`
      : '<div class="empty">لا توجد تعديلات بعد.</div>';
  }
}

// ---------- تسجيل الدخول ----------
function pageLogin() {
  if (state.static) { $app.innerHTML = '<div class="notice">تسجيل الدخول غير متاح في نسخة العرض؛ يلزم تشغيل المنصة على خادم.</div>'; return; }
  $app.innerHTML = `<div class="card" style="max-width:420px;margin:2rem auto">
    <h1>تسجيل الدخول</h1><p class="muted small">حسابات المراجعين والمعلمين ينشئها المشرف من الخادم.</p>
    <form id="login-form">
      <div class="field"><label for="l-user">اسم المستخدم</label><input id="l-user" autocomplete="username" required></div>
      <div class="field"><label for="l-pass">كلمة المرور</label><input id="l-pass" type="password" autocomplete="current-password" required></div>
      <button class="primary" type="submit">دخول</button>
    </form></div>`;
  document.getElementById('login-form').onsubmit = async e => {
    e.preventDefault();
    try {
      const r = await api('/login', { method: 'POST', body: { username: document.getElementById('l-user').value, password: document.getElementById('l-pass').value } });
      state.user = r.user; renderUserbox(); toast('مرحبًا ' + r.user.displayName); location.hash = '#/';
    } catch (err) { fail(err); }
  };
}

// ---------- الموجّه ----------
async function route() {
  const hash = location.hash.replace(/^#/, '') || '/';
  const [, page, arg] = hash.split('/');
  document.querySelectorAll('[data-nav]').forEach(a => a.classList.toggle('active',
    a.dataset.nav === (page || 'home') || (a.dataset.nav === 'chapters' && ['chapter', 'objective'].includes(page))));
  document.body.classList.remove('print-student', 'print-teacher', 'exam-printing', 'xprint-student', 'xprint-key', 'xprint-all');
  try {
    if (!page) await pageHome();
    else if (page === 'chapters') await pageChapters();
    else if (page === 'chapter') await pageChapter(arg);
    else if (page === 'objective') { objState.answers = {}; await pageObjective(decodeURIComponent(arg)); }
    else if (page === 'bank') await pageBank();
    else if (page === 'reports') await pageReports();
    else if (page === 'exam') await pageExam({ api, esc, fail, toast, $app });
    else if (page === 'login') pageLogin();
    else $app.innerHTML = '<div class="empty">الصفحة غير موجودة.</div>';
  } catch (e) {
    $app.innerHTML = `<div class="notice bad">${esc(e.message)}</div>`;
  }
  window.scrollTo(0, 0);
}

window.addEventListener('hashchange', route);
window.addEventListener('afterprint', () => document.body.classList.remove('print-student', 'print-teacher'));
api('/me').then(r => { state.user = r.user; renderUserbox(); route(); }).catch(() => { renderUserbox(); route(); });
