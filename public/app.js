// واجهة المنصة: تطبيق صفحة واحدة بوحدات ES دون أدوات بناء.
import { pageExam, resetExam } from './exam.js';
import { SUPABASE } from './config.js';
import { similarPairs } from './validate.js';
import { pageStudentHome, pageStudentHistory, pageStudentConfirm, resetStudentSession } from './student.js';
import { pageTeacherProgress, pageAdminStudents, pageAdminTeam, resetStaffState } from './staff.js';
import { pageDashboard } from './dashboard.js';
import { pageNotes, notesCard, noteDialog, resetNotesState } from './notes.js';
import { PERMS, ROLE_NAMES } from './roles.js';
import { pageCourses, pickCourse, rememberCourse, courseLine } from './courses.js';
import { icon, line, hydrateIcons, CHAPTER_ICONS } from './icons.js';
const $app = document.getElementById('app');
const $dlg = document.getElementById('dlg');
const state = { user: null, selection: new Set(), courses: null, course: null };

// ---------- لمسات العرض ----------
hydrateIcons(document);
// سياسة أمان المحتوى في الخادم المحلي تمنع سمة style المضمّنة؛ تُطبَّق قيمها عبر CSSOM (مسموح) حتى تظهر أشرطة التقدم بنسبها الصحيحة.
// والحالات الفارغة تُزيَّن بأيقونة. لا يتغير أي سلوك.
function decorate(root) {
  if (!root.querySelectorAll) return;
  const styled = root.matches?.('[style]') ? [root, ...root.querySelectorAll('[style]')] : root.querySelectorAll('[style]');
  for (const el of styled) { const css = el.getAttribute('style'); if (css && el.style.cssText !== css && !el.style.cssText) el.style.cssText = css; }
  const empties = root.matches?.('.empty') ? [root] : root.querySelectorAll('.empty');
  for (const el of empties) if (!el.querySelector(':scope > .ic')) el.insertAdjacentHTML('afterbegin', icon('empty', 44));
}
new MutationObserver(list => { for (const m of list) m.addedNodes.forEach(n => n.nodeType === 1 && decorate(n)); })
  .observe(document.body, { childList: true, subtree: true });
// ارتفاع الترويسة الثابتة: يستعمله شريط أزرار التصدير في منشئ الاختبارات ليلتصق تحتها
const $top = document.querySelector('.topbar');
const syncTop = () => document.documentElement.style.setProperty('--tb-h',
  $top && getComputedStyle($top).position === 'sticky' && $top.offsetHeight ? $top.offsetHeight + 'px' : '0px');
if (window.ResizeObserver && $top) new ResizeObserver(syncTop).observe($top);
window.addEventListener('resize', syncTop);
const ttl = (ic, html, tag = 'h2', size = 30) => `<${tag} class="ttl">${icon(ic, size)}<span>${html}</span></${tag}>`;

// ---------- أدوات ----------
// المصطلح المعتمد للمصدر: «الكتاب المدرسي». البيانات المخزنة تقول «المذكرة»، ويُستبدل المصطلح عند العرض فقط
// حتى لا تتغير ملفات الأسئلة (تغييرها يلغي قرار الاعتماد المرتبط ببصمة كل ملف).
const term = s => String(s ?? '').replace(/\s*[–-]?\s*\(مسارات\)|\s*[–-]\s*مسارات|مسارات\s*/g, '').replace(/للمذكرة/g, 'للكتاب المدرسي').replace(/المذكرة/g, 'الكتاب المدرسي').replace(/مذكرة/g, 'الكتاب المدرسي');
// مراجع المصدر تُعرض دون أرقام صفحات ولا «ورقة عمل»: الأرقام المخزنة لصفحات المذكرة ولا تطابق صفحات الكتاب المدرسي.
const cleanRef = s => {
  const t = term(s);
  if (/^محتوى مكمّل/.test(t)) return 'محتوى مكمّل (غير موجود في الكتاب المدرسي)';
  return t
    .replace(/(الصفحات|صفحات|ص)\s*\.?\s*\d+(\s*(?:[–\-،,]|و)\s*(?:ص\s*)?\d+)*/g, '')
    .replace(/(تابع\s+)?ورقة(\s+عمل)?\s*\d*\s*:?\s*/g, '')
    .replace(/\(\s*\)/g, '').replace(/\(\s+/g, '(').replace(/\s+\)/g, ')')
    .replace(/\s*—\s*/g, ' — ').replace(/(\s—\s*)+$/g, '').replace(/^\s*—\s*/, '')
    .replace(/(\s—\s){2,}/g, ' — ').replace(/\s+([؛،.)])/g, '$1').replace(/\s{2,}/g, ' ').trim();
};
const escRaw = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
// للعرض: المصطلح المعتمد؛ وفي حقول التحرير يُستخدم escRaw حتى لا يتغير النص المخزن عند الحفظ.
const esc = s => term(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pct = (a, b) => (b ? Math.round((100 * (a || 0)) / b) : 0);
const LETTERS = ['أ', 'ب', 'ج'];

// أوضاع التشغيل: خادم محلي (api/) ← Supabase (إن ضُبط config.js). لا توجد نسخة عامة: المحتوى للحسابات المفعّلة فقط.
let supa = null;
async function useSupabase() {
  if (!SUPABASE?.url || !SUPABASE?.key) return false;
  try {
    supa = await import('./supa.js');
    supa.onSignedOut(() => { if (state.user) { toast('انتهت الجلسة؛ سجّل الدخول مرة أخرى', true); signedOut(); } });
    await supa.initSupabase(SUPABASE);
    state.supabase = true;
    return true;
  } catch (e) { console.warn('تعذر الاتصال بـ Supabase', e); supa = null; return false; }
}

// القراءة التي تصل بعد انتقال المستخدم إلى صفحة أخرى تُهمل حتى لا تكتب الصفحة القديمة فوق الجديدة.
let routeSeq = 0;
const STALE = Object.assign(new Error('stale'), { stale: true });
// البنك كاملًا يُحمَّل مرة واحدة ويُحفظ في الذاكرة (بنك الأسئلة ومنشئ الاختبارات وأوراق الأسئلة)،
// ويُمسح بعد أي كتابة أو عند الخروج حتى لا يُعرض محتوى قديم.
let bankCache = null;
async function api(path, opts = {}) {
  const seq = routeSeq;
  const write = opts.method && opts.method !== 'GET';
  if (write) bankCache = null;
  let data;
  if (path === '/bank' && !write) data = await (bankCache ||= apiRaw('/bank').catch(e => { bankCache = null; throw e; }));
  else data = await apiRaw(path, opts);
  if (write) bankCache = null;
  // قراءة أو كتابة انتهت بعد انتقال المستخدم: لا تُرسم الصفحة القديمة فوق الجديدة (الكتابة نفسها تمت)
  // keep: الطلبات التي يجب حفظ نتيجتها حتى لو انتقل المستخدم (مثل إجابة الطالب)
  if (seq !== routeSeq && !opts.keep) throw STALE;
  return data;
}

async function apiRaw(path, opts = {}) {
  if (state.supabase) return supa.supaApi(path, opts);
  if (state.offline) throw new Error('تعذر الاتصال بقاعدة البيانات؛ تحقق من الإنترنت ثم أعد تحميل الصفحة.');
  const { method = 'GET', body } = opts;
  const res = await fetch('api' + path, {
    method, credentials: 'same-origin',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => null);
  // لا يوجد خادم (مثل GitHub Pages): ننتقل إلى نسخة العرض الثابتة.
  if (data === null && path === '/me') {
    if (await useSupabase()) {
      try { return await supa.supaApi(path, opts); } catch (e) { console.warn(e); state.supabase = false; }
    }
    state.offline = true; return { user: null };
  }
  if (!res.ok || data === null) throw Object.assign(new Error(data?.error || 'تعذر تنفيذ الطلب'), { errors: data?.errors, status: res.status });
  return data;
}

function toast(msg, error = false) {
  const t = document.createElement('div');
  t.className = 'toast' + (error ? ' error' : '');
  t.setAttribute('role', error ? 'alert' : 'status');
  t.textContent = msg;
  document.body.append(t);
  setTimeout(() => t.remove(), error ? 6000 : 3000);
}
// يمنع النقر المزدوج: الزر يُعطَّل حتى ينتهي الطلب (فلا يُنشأ سؤال أو نسخة مرتين)
const guard = fn => async function (e) {
  const b = e?.currentTarget;
  if (b?.dataset.busy) return;
  if (b) { b.dataset.busy = '1'; b.disabled = true; }
  try { await fn.call(this, e); } finally { if (b) { delete b.dataset.busy; b.disabled = false; } }
};

const fail = e => {
  if (e?.stale) return;
  if (e?.status === 401 && state.user) { toast('انتهت الجلسة؛ سجّل الدخول مرة أخرى', true); return signedOut(); }
  toast(e.errors?.length ? e.errors.join('، ') : e.message, true);
};

// الصلاحيات حسب الدور (roles.js)، وقاعدة البيانات تفرض الشيء نفسه في دوالها المحمية.
const can = perm => !!PERMS[state.user?.role]?.includes(perm);
const isReviewer = () => can('review');

// ---------- المقرر المختار ----------
const $brandSub = document.getElementById('brand-sub');
const BRAND_DEFAULT = $brandSub?.textContent || '';
function showCourseLine() {
  const c = state.user?.role === 'student' ? state.user.courses?.[0] : state.course;
  if ($brandSub) $brandSub.textContent = c ? courseLine(c) : BRAND_DEFAULT;
}
// قائمة المقررات (مرة بعد الدخول). الخادم المحلي القديم لا يعرف المقررات: مقرر واحد من /stats.
async function ensureCourses() {
  if (!state.courses) {
    try { if (!state.supabase) throw 0; state.courses = await apiRaw('/courses'); }
    catch {
      const s = await apiRaw('/stats');
      state.courses = [{ id: s.course?.id || 1, code: s.course?.code || 'كيمياء 2-1', title: s.course?.title, grade: s.course?.grade || 'الثاني الثانوي',
        term: s.course?.term || 'الأول', status: 'ready', objectives: s.objectives?.n, questions: s.questions?.n, approved: s.questions?.approved, students: 0 }];
    }
  }
  if (!state.course) setCourse(pickCourse(state.courses, null, can('edit'))?.id, false);
}
// تغيير المقرر: كل ما يخص المقرر السابق يُمسح (البنك المحفوظ، التحديد، الاختبار قيد الإعداد)
function setCourse(id, go) {
  const c = state.courses?.find(x => x.id === id);
  if (!c) return;
  if (state.course?.id !== c.id) {
    state.course = c; bankCache = null; state.selection.clear(); resetExam();
    for (const k in bankFilter) delete bankFilter[k];
    supa?.setCourse(c.id); rememberCourse(c.id);
  }
  showCourseLine();
  if (go) { if (location.hash === '#/course') route(); else location.hash = '#/course'; }
}

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
  showCourseLine();
  const box = document.getElementById('userbox');
  if (state.user) {
    box.innerHTML = `<span class="avatar" aria-hidden="true">${esc((state.user.displayName || '؟').trim().charAt(0))}</span>
      <span class="who"><b>${esc(state.user.displayName)}</b><span>${ROLE_NAMES[state.user.role] || ''}</span></span>
      <button type="button" id="logout" title="تسجيل الخروج">${line('logout', 17)}<span>خروج</span></button>`;
    box.querySelector('#logout').onclick = async () => { state.user = null; await apiRaw('/logout', { method: 'POST' }).catch(() => {}); signedOut(); };
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
    <div class="hero banner">
      <div class="hero-ic">
        <img class="banner-mark" src="assets/itqan-mark.png" alt="" width="74" height="74">
        <div>
          <span class="eyebrow">${icon('spark', 18)} إتقان · بنك أسئلة الكيمياء</span>
          <h1>${esc(s.course?.title || 'كيمياء 2-1')}</h1>
          <p class="muted">${esc(s.course?.grade)} · الفصل الدراسي ${esc(s.course?.term)} · ${esc(s.course?.country)}</p>
          ${s.course?.id === 1 ? `<p class="small muted">بنية المقرر: ${esc(s.course?.structure_source)}<br>مصدر المحتوى: الكتاب المدرسي — كيمياء 2-1، الصف الثاني الثانوي، الفصل الدراسي الأول 1448هـ</p>` : ''}
        </div>
      </div>
      <div class="actions no-print">
        <a class="btn primary" href="#/chapters">${icon('chapters', 22, 'navy')}تصفح الفصول</a>
        <a class="btn" href="#/bank">بنك الأسئلة</a>
        <a class="btn" href="#/">${line('prev', 16)}كل المقررات</a>
      </div>
    </div>
    ${s.course?.status === 'preparing' ? `<p class="notice warn">هذا المقرر <b>قيد الإعداد</b> ولا يظهر لغير مالك المشروع. تُضاف أهدافه وأسئلته في مرحلة المحتوى.</p>` : ''}
    <div class="grid kpi">
      ${kpi(s.chapters, 'فصول', 'chapters')}${kpi(s.lessons, 'دروس', 'lessons')}${kpi(o.n, 'هدفًا تعليميًا', 'objectives')}
      ${kpi(q.mcq || 0, 'سؤال اختيار من متعدد', 'mcq')}${kpi(q.essay || 0, 'سؤالًا مقاليًا', 'essay')}
    </div>
    <div class="grid cards" style="margin-top:1rem">
      <div class="card">
        ${ttl('shield', 'مؤشرات المراجعة')}
        <div class="levels">
          ${progress('الأهداف التي روجعت', o.reviewed, o.n)}
          ${progress('الأهداف المعتمدة', o.approved, o.n, 'ok')}
          ${progress('الأسئلة التي روجعت', q.reviewed, q.n)}
          ${progress('الأسئلة المعتمدة', q.approved, q.n, 'ok')}
        </div>
        <p class="small muted" style="margin-top:.6rem">تُحسب المؤشرات مباشرة من قاعدة البيانات، ولا يدخل في مؤشرات الاعتماد إلا ما اعتمده مراجع بشري.</p>
      </div>
      <div class="card">
        ${ttl('pie', 'التغطية التقويمية')}
        <div class="levels">
          ${progress('أهداف بلغت العدد المطلوب من الأسئلة (7 + 3)', s.coverage.complete, o.n)}
          ${progress('أهداف اكتملت أسئلتها المعتمدة', s.coverage.approved_complete, o.n, 'ok')}
          ${progress('محتوى مكمّل للكتاب المدرسي معتمد', s.supplements.approved, s.supplements.n, 'ok')}
        </div>
        <p class="small muted" style="margin-top:.6rem">اكتمل بنك الأسئلة لجميع الأهداف. اعتُمدت الأسئلة بقرار مالك المشروع دون مراجعة تفصيلية لكل سؤال، والتفاصيل في سجل كل سؤال.</p>
      </div>
    </div>
    <div class="section-title">${ttl('chapters', 'الفصول')}<a class="see-all" href="#/chapters">عرض الكل ${line('next', 16)}</a></div>
    <div class="grid cards">${chapters.map(chapterCard).join('')}</div>`;
}
const kpi = (v, l, ic = 'reports', tone) => `<div class="card">${icon(ic, 46, tone)}<div class="value">${esc(v ?? 0)}</div><div class="label">${esc(l)}</div></div>`;
const progress = (label, v, t, cls = '') => `<div class="progress-line"><span>${esc(label)}</span>
  <span class="muted small">${v || 0} من ${t || 0} (${pct(v, t)}%)</span>${bar(v, t, cls)}</div>`;

function chapterCard(c) {
  return `<a class="card chapter-card" href="#/chapter/${c.number}">
    <div class="ch-head"><span class="ch-ic">${icon(CHAPTER_ICONS[c.number] || 'practice', 50)}<span class="chapter-num">${c.number}</span></span>
      <div><span class="ch-kicker">الفصل ${c.number}</span><h3>${esc(c.title)}</h3></div></div>
    <div class="meta-row">${badge(`${c.lessons} دروس`)}${badge(`${c.objectives} هدفًا`)}${badge(`${c.questions} سؤالًا`, c.questions ? 'brand' : '')}</div>
    <div class="progress-line small"><span>الأهداف المعتمدة</span><span class="muted">${c.approved || 0}/${c.objectives}</span>${bar(c.approved, c.objectives, 'ok')}</div>
  </a>`;
}

async function pageChapters() {
  const chapters = await api('/chapters');
  $app.innerHTML = `<div class="crumbs"><a href="#/course">الرئيسية</a> ‹ الفصول</div>
    <div class="hero"><div class="hero-ic">${icon('chapters', 52)}<div><h1>فصول المقرر</h1><p class="muted">مرتبة وفق ملف أهداف المقرر المعتمد في المشروع.</p></div></div></div>
    <div class="grid cards">${chapters.map(chapterCard).join('')}</div>`;
}

async function pageChapter(n) {
  const ch = await api('/chapters/' + n);
  $app.innerHTML = `<div class="crumbs"><a href="#/course">الرئيسية</a> ‹ <a href="#/chapters">الفصول</a> ‹ الفصل ${ch.number}</div>
    <div class="hero"><div class="hero-ic">${icon(CHAPTER_ICONS[ch.number] || 'chapters', 52)}<div><h1>الفصل ${ch.number}: ${esc(ch.title)}</h1></div></div></div>
    ${ch.lessons.map(l => `
      <section class="card lesson" id="lesson-${l.number}">
        <div class="lesson-head">
          ${ttl('lessons', `الدرس ${ch.number}-${l.number}: ${esc(l.title)}`, 'h2', 32)}
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
              ${o.memoCoverage ? badge('الكتاب المدرسي: ' + o.memoCoverage, COVERAGE_KIND[o.memoCoverage]) : ''}</span>
          </li>`).join('')}
        </ul>
      </section>`).join('')}`;
}

// ---------- صفحة الهدف ----------
const objState = { mode: 'test', answers: {} };

// الخروج (أو انتهاء الجلسة): تُمسح كل حالة المستخدم السابق من الجهاز قبل عرض صفحة الدخول.
function signedOut() {
  resetStudentSession(); resetExam(); resetStaffState(); resetNotesState(); bankCache = null;
  for (const k in bankFilter) delete bankFilter[k];
  state.selection.clear();
  Object.assign(objState, { mode: 'test', answers: {} });
  if ($dlg.open) $dlg.close();
  state.user = null; state.courses = null; state.course = null; supa?.setCourse(null); showCourseLine(); renderUserbox();
  if (location.hash && location.hash !== '#/') location.hash = '#/'; else route();
}

async function pageObjective(code) {
  const data = await api('/objectives/' + encodeURIComponent(code));
  const { objective: o, supplement: s, questions } = data;
  // رابط هدف من مقرر آخر: يصبح مقرره هو المختار
  if (o.courseId && state.course && o.courseId !== state.course.id) setCourse(o.courseId, false);
  if (!data.answersIncluded && objState.mode === 'review') objState.mode = 'test';
  const mcq = questions.filter(q => q.type === 'mcq'), essay = questions.filter(q => q.type === 'essay');
  const active = q => !q.excluded;
  const idx = data.lessonNav.indexOf(o.code);
  $app.innerHTML = `
    <div class="crumbs"><a href="#/course">الرئيسية</a> ‹ <a href="#/chapter/${o.chapter.number}">الفصل ${o.chapter.number}: ${esc(o.chapter.title)}</a>
      ‹ <a href="#/chapter/${o.chapter.number}">الدرس ${o.chapter.number}-${o.lesson.number}: ${esc(o.lesson.title)}</a></div>
    <div class="print-only"><h2>${esc(o.chapter.title)} — ${esc(o.lesson.title)}</h2></div>
    <div class="hero">
      <div><span class="obj-code">${esc(o.code)}${o.originalCode ? ` (سابقًا ${esc(o.originalCode)})` : ''}</span>
        <h1>${esc(o.approvedText || o.proposedText || o.originalText)}</h1>
        <div class="meta-row">${objBadge(o.reviewStatus)}${o.thinkingLevel ? badge('مستوى التفكير: ' + o.thinkingLevel, 'brand') : ''}
          ${o.memoCoverage ? badge('تغطية الكتاب المدرسي: ' + o.memoCoverage, COVERAGE_KIND[o.memoCoverage]) : ''}</div></div>
      <div class="actions no-print">
        ${idx > 0 ? `<a class="btn" href="#/objective/${data.lessonNav[idx - 1]}">→ الهدف السابق</a>` : ''}
        ${idx < data.lessonNav.length - 1 ? `<a class="btn" href="#/objective/${data.lessonNav[idx + 1]}">الهدف التالي ←</a>` : ''}
      </div>
    </div>

    <section class="card no-print">
      ${ttl('objectives', 'معلومات الهدف')}
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
        <dt>المرجع في الكتاب المدرسي</dt><dd>${o.memoNote ? esc(cleanRef(o.memoNote)) : '—'}</dd>
        ${o.duplicateOf ? `<dt>تكرار</dt><dd>${badge('مكرر للهدف ' + o.duplicateOf, 'warn')}</dd>` : ''}
      </dl>
      ${isReviewer() ? reviewPanel(o) : ''}
    </section>

    ${s ? supplementCard(s) : ''}

    <section class="card" id="mcq-section">
      <div class="section-title" style="margin-top:0">
        ${ttl('mcq', `أسئلة الاختيار من متعدد <span class="muted small">(${mcq.filter(active).length} من ${o.requiredMcq} مطلوبة)</span>`)}
        <div class="actions no-print">
          <div class="seg" role="group" aria-label="نمط العرض">
            ${modeBtn('test', 'وضع الاختبار')}${modeBtn('practice', 'تدريب فوري')}${data.answersIncluded ? modeBtn('review', 'وضع المراجعة') : ''}
          </div>
          <button type="button" data-print="student">${line('print', 17)}طباعة دون حلول</button>
          ${data.answersIncluded ? `<button type="button" data-print="teacher">${line('print', 17)}طباعة مع الحلول</button>` : ''}
          ${can('edit') ? `<button type="button" class="primary" data-add="mcq">+ سؤال اختيار</button>` : ''}
        </div>
      </div>
      ${modeHint(data.answersIncluded)}
      <div id="mcq-list">${mcq.length ? mcq.map(q => mcqCard(q, data.answersIncluded)).join('') : '<div class="empty">لا توجد أسئلة اختيار لهذا الهدف بعد.</div>'}</div>
      ${objState.mode === 'test' && mcq.length ? `<div class="actions no-print" style="margin-top:.8rem"><button type="button" class="primary" id="finish-test">إنهاء الاختبار وعرض النتيجة</button><span id="test-result"></span></div>` : ''}
    </section>

    <section class="card" id="essay-section">
      <div class="section-title" style="margin-top:0">
        ${ttl('essay', `الأسئلة المقالية <span class="muted small">(${essay.filter(active).length} من ${o.requiredEssay} مطلوبة)</span>`)}
        ${can('edit') ? `<button type="button" class="primary no-print" data-add="essay">+ سؤال مقالي</button>` : ''}
      </div>
      ${essay.length ? essay.map(q => essayCard(q, data.answersIncluded)).join('') : '<div class="empty">لا توجد أسئلة مقالية لهذا الهدف بعد.</div>'}
    </section>
    ${can('notes') && state.supabase ? '<section class="card no-print" id="notes-card"></section>' : ''}`;
  bindObjective(o, questions, s);
  if (can('notes') && state.supabase) notesCard(nctx(), document.getElementById('notes-card'), o, questions, s);
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
  const owner = can('edit');
  return `<div class="card review-panel">
    ${ttl('shield', 'مراجعة الهدف واعتماده', 'h3', 28)}
    ${owner ? `<div class="field"><label for="approved-text">الصياغة التي ستُعتمد</label>
      <textarea id="approved-text">${esc(o.approvedText || o.proposedText || o.originalText)}</textarea></div>
    <div class="form-grid">
      <div class="field"><label for="req-mcq">عدد أسئلة الاختيار المطلوب</label><input id="req-mcq" type="number" min="0" max="30" value="${o.requiredMcq}"></div>
      <div class="field"><label for="req-essay">عدد الأسئلة المقالية المطلوب</label><input id="req-essay" type="number" min="0" max="30" value="${o.requiredEssay}"></div>
    </div>` : `<p class="small muted">يُعتمد الهدف بصياغته الحالية. لاقتراح صياغة أخرى اكتب «ملاحظة» في أسفل الصفحة، ويطّلع عليها مالك المشروع.</p>`}
    <div class="field"><label for="review-note">سبب القرار (إلزامي عند الإعادة)</label><textarea id="review-note"></textarea></div>
    <div class="actions">
      <button type="button" class="ok" data-review="approve">اعتماد الهدف</button>
      <button type="button" class="danger" data-review="return">إعادة للتعديل</button>
      <button type="button" data-review="reset">إلغاء الاعتماد</button>
      ${owner ? '<button type="button" id="save-counts">حفظ الأعداد المطلوبة</button>' : ''}
    </div></div>`;
}

function supplementCard(s) {
  return `<section class="card no-print">
    <div class="section-title" style="margin-top:0">${ttl('spark', 'المحتوى العلمي المكمّل')}
      <span class="meta-row">${objBadge(s.reviewStatus)}${badge(s.confidence === 'high' ? 'ثقة مرتفعة' : 'يحتاج تحققًا من الصياغة', s.confidence === 'high' ? 'brand' : 'warn')}</span></div>
    <p class="notice">هذا المحتوى أكمله الوكيل الكيميائي التربوي (ذكاء اصطناعي) لأن الكتاب المدرسي تركته فراغًا أو لم تتناوله؛ <strong>ليس من نص الكتاب المدرسي</strong> ولا يُعد معتمدًا حتى يعتمده مراجع.</p>
    ${s.memoBasis ? `<p><strong>ما يقدمه الكتاب المدرسي:</strong> ${esc(cleanRef(s.memoBasis))}</p>` : ''}
    <p id="sup-text">${esc(cleanRef(s.supplement))}</p>
    ${s.keyPoints.length ? `<h3>نقاط أساسية</h3>${list(s.keyPoints)}` : ''}
    ${s.misconceptions.length ? `<h3>تصورات خاطئة شائعة</h3>${list(s.misconceptions)}` : ''}
    ${s.scientificNotes ? `<p class="small muted"><strong>ملاحظات علمية:</strong> ${esc(cleanRef(s.scientificNotes))}</p>` : ''}
    ${isReviewer() ? `<div class="actions">
      <button type="button" class="ok" data-sup="approve">اعتماد المحتوى</button>
      ${can('edit') ? '<button type="button" data-sup="edit">تعديل</button>' : ''}
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
      ${q.sourceRef ? `<div class="small muted">المرجع: ${esc(cleanRef(q.sourceRef))}</div>` : ''}
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
      ${q.sourceRef ? `<div class="small muted">المرجع: ${esc(cleanRef(q.sourceRef))}</div>` : ''}
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
      ${can('notes') && state.supabase ? `<button type="button" data-qnote="${q.id}">${line('plus', 15)}ملاحظة</button>` : ''}
      ${can('edit') ? `<button type="button" data-qedit="${q.id}">تعديل</button>
      <button type="button" data-qdup="${q.id}">نسخ</button>
      <button type="button" data-qexclude="${q.id}:${q.excluded ? 0 : 1}">${q.excluded ? 'إرجاع' : 'استبعاد'}</button>` : ''}
      <button type="button" data-qhist="${q.id}">سجل التعديلات</button>
    </div>` : ''}`;
}

function bindObjective(o, questions, s) {
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
  $app.querySelectorAll('[data-review]').forEach(b => b.onclick = guard(async () => {
    try {
      await api(`/objectives/${o.code}/review`, { method: 'POST', body: {
        action: b.dataset.review, approved_text: document.getElementById('approved-text')?.value ?? null, note: document.getElementById('review-note').value } });
      toast('تم حفظ قرار المراجعة'); reload();
    } catch (e) { fail(e); }
  }));
  const sc = document.getElementById('save-counts');
  if (sc) sc.onclick = guard(async () => {
    try {
      await api(`/objectives/${o.code}`, { method: 'PATCH', body: {
        required_mcq: Number(document.getElementById('req-mcq').value), required_essay: Number(document.getElementById('req-essay').value) } });
      toast('تم حفظ الأعداد المطلوبة'); reload();
    } catch (e) { fail(e); }
  });
  $app.querySelectorAll('[data-sup]').forEach(b => b.onclick = guard(async () => {
    const action = b.dataset.sup;
    if (action === 'edit') return editSupplement(o.code, s?.supplement || '', reload);
    let note = '';
    if (action === 'return') { note = prompt('سبب الإعادة للمراجعة:') || ''; if (!note.trim()) return; }
    try { await api(`/objectives/${o.code}/supplement-review`, { method: 'POST', body: { action, note } }); toast('تم الحفظ'); reload(); }
    catch (e) { fail(e); }
  }));
  $app.querySelectorAll('[data-qstatus]').forEach(b => b.onclick = guard(async () => {
    const [id, status] = b.dataset.qstatus.split(':');
    let note = null;
    if (status === 'needs_revision') { note = prompt('ما المطلوب تعديله؟') || ''; if (!note.trim()) return; }
    try { await api(`/questions/${id}/status`, { method: 'POST', body: { status, note } }); toast('تم تحديث حالة السؤال'); reload(); }
    catch (e) { fail(e); }
  }));
  $app.querySelectorAll('[data-qexclude]').forEach(b => b.onclick = guard(async () => {
    const [id, ex] = b.dataset.qexclude.split(':').map(Number);
    let note = '';
    if (ex) { note = prompt('سبب الاستبعاد (يُحفظ في سجل التعديلات):') || ''; if (!note.trim()) return; }
    try { await api(`/questions/${id}/exclude`, { method: 'POST', body: { excluded: !!ex, note } }); reload(); } catch (e) { fail(e); }
  }));
  $app.querySelectorAll('[data-qdup]').forEach(b => b.onclick = guard(async () => {
    try { await api(`/questions/${b.dataset.qdup}/duplicate`, { method: 'POST' }); toast('أُنشئت نسخة من السؤال'); reload(); } catch (e) { fail(e); }
  }));
  $app.querySelectorAll('[data-qedit]').forEach(b => b.onclick = () => {
    const q = questions.find(x => x.id === Number(b.dataset.qedit));
    openEditor(q.type, q, async body => { await api(`/questions/${q.id}`, { method: 'PATCH', body }); }, reload);
  });
  $app.querySelectorAll('[data-add]').forEach(b => b.onclick = () =>
    openEditor(b.dataset.add, null, async body => { await api(`/objectives/${o.code}/questions`, { method: 'POST', body: { ...body, type: b.dataset.add } }); }, reload));
  $app.querySelectorAll('[data-qhist]').forEach(b => b.onclick = () => showHistory(Number(b.dataset.qhist)));
  $app.querySelectorAll('[data-qnote]').forEach(b => b.onclick = () => {
    const q = questions.find(x => x.id === Number(b.dataset.qnote));
    noteDialog(nctx(), { code: o.code, entity: 'question', question: q }, reload);
  });
}
// سياق صفحات الملاحظات ولوحة المؤشرات
const nctx = () => ({ api, esc, fail, toast, $app, state, can, dialog, guard, badge, ttl, course: state.course, done: () => route() });

function printAs(kind) {
  document.body.classList.remove('print-student', 'print-teacher');
  document.body.classList.add('print-' + kind);
  window.print();
}

// ---------- النوافذ ----------
function dialog(title, body, buttons) {
  $dlg.innerHTML = `<div class="dlg-head"><h2 style="margin:0">${esc(title)}</h2><button type="button" data-close aria-label="إغلاق">${line('close', 18)}</button></div>
    <div class="dlg-body">${body}</div><div class="dlg-foot">${buttons}<button type="button" data-close>إغلاق</button></div>`;
  $dlg.querySelectorAll('[data-close]').forEach(b => b.onclick = () => $dlg.close());
  $dlg.showModal();
  return $dlg;
}

function editSupplement(code, text, done) {
  const d = dialog('تعديل المحتوى المكمّل', `<label for="sup-edit">النص</label><textarea id="sup-edit" style="min-height:12rem">${escRaw(text)}</textarea>
    <label for="sup-note" style="margin-top:.6rem">ملاحظة التعديل</label><input id="sup-note">`,
  `<button type="button" class="primary" id="sup-save">حفظ (يبقى بانتظار الاعتماد)</button>`);
  d.querySelector('#sup-save').onclick = guard(async () => {
    try {
      await api(`/objectives/${code}/supplement-review`, { method: 'POST', body: {
        action: 'reset', supplement: d.querySelector('#sup-edit').value, note: d.querySelector('#sup-note').value } });
      d.close(); toast('تم حفظ التعديل'); done();
    } catch (e) { fail(e); }
  });
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
    <div class="field"><label for="e-stem">نص السؤال</label><textarea id="e-stem">${escRaw(q.stem)}</textarea></div>
    <div class="form-grid">
      <div class="field"><label for="e-level">مستوى التفكير</label>${sel('e-level', LEVEL_OPTS, q.thinkingLevel)}</div>
      <div class="field"><label for="e-diff">درجة الصعوبة</label>${sel('e-diff', ['سهل', 'متوسط', 'صعب'], q.difficulty)}</div>
      <div class="field"><label for="e-kind">نوع السؤال</label><input id="e-kind" value="${escRaw(q.questionKind)}"></div>
      <div class="field"><label for="e-src">المرجع</label><input id="e-src" value="${escRaw(q.sourceRef)}"></div>
    </div>`;
  const mcq = `${q.options.map((op, i) => `
      <div class="field"><label for="e-opt${i}">البديل ${LETTERS[i]} ${i === q.correctIndex ? '(الصحيح حاليًا)' : ''}</label>
        <input id="e-opt${i}" value="${escRaw(op)}"></div>`).join('')}
    <div class="field"><label for="e-correct">الإجابة الصحيحة</label>
      <select id="e-correct">${LETTERS.map((l, i) => `<option value="${i}" ${i === q.correctIndex ? 'selected' : ''}>${l}</option>`).join('')}</select></div>
    <div class="field"><label for="e-expl">تفسير الإجابة الصحيحة</label><textarea id="e-expl">${escRaw(q.explanation)}</textarea></div>
    <div class="field"><label for="e-dist">سبب خطأ البدائل (سطر لكل بديل بالترتيب، واترك سطر الصحيح فارغًا)</label>
      <textarea id="e-dist">${escRaw((q.distractorNotes || ['', '', '']).join('\n'))}</textarea></div>`;
  const essay = `
    <div class="field"><label for="e-model">الإجابة النموذجية</label><textarea id="e-model" style="min-height:7rem">${escRaw(q.modelAnswer)}</textarea></div>
    <div class="field"><label for="e-elems">عناصر الإجابة (سطر لكل عنصر)</label><textarea id="e-elems">${escRaw(lines(q.answerElements))}</textarea></div>
    <div class="field"><label for="e-steps">خطوات الحل (سطر لكل خطوة)</label><textarea id="e-steps">${escRaw(lines(q.solutionSteps))}</textarea></div>
    <div class="field"><label for="e-marks">توزيع الدرجات (العنصر | الدرجة)</label><textarea id="e-marks">${escRaw(pairs(q.marks, 'element', 'marks'))}</textarea></div>
    <div class="field"><label for="e-rubric">سلم التصحيح (المستوى | الوصف)</label><textarea id="e-rubric">${escRaw(pairs(q.rubric, 'level', 'description'))}</textarea></div>
    <div class="field"><label for="e-errors">الأخطاء الشائعة (سطر لكل خطأ)</label><textarea id="e-errors">${escRaw(lines(q.commonErrors))}</textarea></div>`;
  const d = dialog(q.id ? `تعديل السؤال ${q.number}` : (type === 'mcq' ? 'سؤال اختيار جديد' : 'سؤال مقالي جديد'),
    `${q.stimulus ? '<p class="notice info">جدول البيانات المرفق بالسؤال يبقى كما هو.</p>' : ''}${common}${type === 'mcq' ? mcq : essay}
     <p class="small muted">أي تعديل على سؤال معتمد يعيده إلى «قيد المراجعة»، ويُحفظ الإصدار السابق في سجل التعديلات.</p>`,
    `<button type="button" class="primary" id="e-save">حفظ</button>`);
  const v = id => d.querySelector('#' + id).value;
  d.querySelector('#e-save').onclick = guard(async () => {
    const body = { stem: v('e-stem'), thinking_level: v('e-level') || null, difficulty: v('e-diff') || null,
      question_kind: v('e-kind'), source_ref: v('e-src'), stimulus: q.stimulus || null };
    if (type === 'mcq') Object.assign(body, { options: [0, 1, 2].map(i => v('e-opt' + i)), correct_index: Number(v('e-correct')),
      explanation: v('e-expl'), distractor_notes: [0, 1, 2].map(i => v('e-dist').split('\n')[i] || '') });
    else Object.assign(body, { model_answer: v('e-model'), answer_elements: parseLines(v('e-elems')), solution_steps: parseLines(v('e-steps')),
      marks: parsePairs(v('e-marks'), 'element', 'marks', true), rubric: parsePairs(v('e-rubric'), 'level', 'description'), common_errors: parseLines(v('e-errors')) });
    try { await save(body); d.close(); toast('تم الحفظ'); done(); } catch (e) { fail(e); }
  });
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
const BANK_CHUNK = 60;
// التصفية في المتصفح على البنك المحفوظ (نفس قواعد الخادم): لا طلب جديد عند تغيير أي مرشح.
function filterBank(all, f) {
  const q = (f.q || '').trim();
  return all.filter(x => (!f.chapter || x.chapter.number === Number(f.chapter)) && (!f.lesson || x.lesson.number === Number(f.lesson))
    && (!f.objective || x.objectiveCode === f.objective) && (!f.type || x.type === f.type) && (!f.level || x.thinkingLevel === f.level)
    && (!f.difficulty || x.difficulty === f.difficulty) && (!f.status || x.status === f.status)
    && (!q || x.stem.includes(q) || (x.options || []).some(o => String(o).includes(q))));
}
async function pageBank() {
  const [chapters, bank] = await Promise.all([api('/chapters'), api('/bank')]);
  const lessons = bankFilter.chapter
    ? [...new Map(bank.questions.filter(x => x.chapter.number === Number(bankFilter.chapter)).map(x => [x.lesson.number, x.lesson])).values()].sort((a, b) => a.number - b.number)
    : [];
  const res = { questions: filterBank(bank.questions, bankFilter) };
  const answers = !!state.user;
  const f = (k, label, opts) => `<div><label for="f-${k}">${label}</label><select id="f-${k}" data-f="${k}"><option value="">الكل</option>
    ${opts.map(([v, t]) => `<option value="${esc(v)}" ${String(bankFilter[k] || '') === String(v) ? 'selected' : ''}>${esc(t)}</option>`).join('')}</select></div>`;
  const countText = () => `${res.questions.length} سؤالًا ${state.selection.size ? `· المحدد للاختبار: ${state.selection.size}` : ''}`;
  $app.innerHTML = `<div class="crumbs no-print"><a href="#/course">الرئيسية</a> ‹ بنك الأسئلة</div>
    <div class="hero no-print"><div class="hero-ic">${icon('bank', 52)}<div><h1>بنك الأسئلة</h1><p class="muted">بحث وتصفية وإنشاء أوراق أسئلة لهدف أو درس أو فصل أو اختبار شامل.</p></div></div>
      <div class="actions">${isReviewer() ? (state.supabase
        ? `<button class="btn" data-export="questions">تصدير الأسئلة CSV</button><button class="btn" data-export="objectives">تصدير الأهداف CSV</button>`
        : `<a class="btn" href="api/export/questions.csv">تصدير الأسئلة CSV</a><a class="btn" href="api/export/objectives.csv">تصدير الأهداف CSV</a>`) : ''}</div></div>
    <section class="card no-print">
      <div class="filters">
        ${f('chapter', 'الفصل', chapters.map(c => [c.number, `${c.number}. ${c.title}`]))}
        ${f('lesson', 'الدرس', lessons.map(l => [l.number, `${l.number}. ${l.title}`]))}
        ${f('type', 'نوع السؤال', [['mcq', 'اختيار من متعدد'], ['essay', 'مقالي']])}
        ${f('level', 'مستوى التفكير', LEVEL_OPTS.map(l => [l, l]))}
        ${f('difficulty', 'الصعوبة', [['سهل', 'سهل'], ['متوسط', 'متوسط'], ['صعب', 'صعب']])}
        ${f('status', 'حالة المراجعة', Object.entries(Q_STATUS).map(([k, [t]]) => [k, t]))}
        <div><label for="f-q">بحث بالكلمات</label><input id="f-q" value="${esc(bankFilter.q || '')}" placeholder="مثال: الفوتون"></div>
        <div class="actions"><button type="button" class="primary" id="f-apply">${line('search', 17)}بحث</button><button type="button" id="f-clear">مسح</button></div>
      </div>
    </section>
    <div class="section-title no-print"><h2 id="bank-count">${countText()}</h2>
      <div class="actions">
        <button type="button" id="sel-all">تحديد نتائج البحث</button><button type="button" id="sel-none">إلغاء التحديد</button>
        <button type="button" data-sheet="student">ورقة الطالب</button>
        ${answers ? `<button type="button" data-sheet="teacher">نسخة المعلم (مع الإجابات)</button>` : ''}
        <button type="button" id="similar">اكتشاف المتشابهة</button>
      </div></div>
    <p class="small muted no-print">الورقة تُنشأ من الأسئلة المحددة، وإن لم تحدد شيئًا فمن نتائج البحث الحالية. لإنشاء ورقة هدف أو درس أو فصل اختر التصفية المناسبة.</p>
    <div id="similar-out"></div>
    <div id="bank-list">${res.questions.length ? '' : '<div class="empty">لا توجد أسئلة مطابقة.</div>'}</div>
    <div class="actions no-print bank-more" id="bank-more-wrap" hidden><button type="button" id="bank-more"></button></div>`;
  // العرض على دفعات: أول 60 بطاقة، ثم المزيد عند الاقتراب من نهاية القائمة (رسم 2580 بطاقة دفعة واحدة كان يستغرق ثوانٍ طويلة على الآيباد)
  const list = document.getElementById('bank-list'), moreWrap = document.getElementById('bank-more-wrap'), moreBtn = document.getElementById('bank-more');
  let shown = 0, io = null;
  const renderMore = () => {
    const next = res.questions.slice(shown, shown + BANK_CHUNK);
    list.insertAdjacentHTML('beforeend', next.map(q => bankRow(q)).join(''));
    shown += next.length;
    const left = res.questions.length - shown;
    moreWrap.hidden = left <= 0;
    moreBtn.textContent = `عرض المزيد (${left} متبقيًا)`;
    if (left <= 0 && io) { io.disconnect(); io = null; }
  };
  renderMore();
  moreBtn.onclick = renderMore;
  if ('IntersectionObserver' in window && shown < res.questions.length) {
    io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) renderMore(); }, { rootMargin: '600px' });
    io.observe(moreWrap);
  }
  const rerender = () => pageBank().catch(fail);
  $app.querySelectorAll('[data-f]').forEach(s => s.onchange = () => {
    bankFilter[s.dataset.f] = s.value; if (s.dataset.f === 'chapter') delete bankFilter.lesson; rerender();
  });
  document.getElementById('f-apply').onclick = () => { bankFilter.q = document.getElementById('f-q').value.trim(); rerender(); };
  document.getElementById('f-q').onkeydown = e => { if (e.key === 'Enter') document.getElementById('f-apply').click(); };
  document.getElementById('f-clear').onclick = () => { for (const k in bankFilter) delete bankFilter[k]; rerender(); };
  $app.querySelectorAll('[data-export]').forEach(b => b.onclick = async () => {
    b.disabled = true;
    try { await supa.exportCsv(b.dataset.export); } catch (e) { fail(e); } finally { b.disabled = false; }
  });
  // التحديد دون إعادة بناء الصفحة
  const syncCount = () => { document.getElementById('bank-count').textContent = countText(); };
  document.getElementById('sel-all').onclick = () => {
    res.questions.forEach(q => state.selection.add(q.id));
    list.querySelectorAll('[data-pick]').forEach(c => { c.checked = true; }); syncCount();
  };
  document.getElementById('sel-none').onclick = () => {
    state.selection.clear(); list.querySelectorAll('[data-pick]').forEach(c => { c.checked = false; }); syncCount();
  };
  list.onchange = e => {
    const c = e.target.closest('[data-pick]'); if (!c) return;
    const id = Number(c.dataset.pick); c.checked ? state.selection.add(id) : state.selection.delete(id); syncCount();
  };
  $app.querySelectorAll('[data-sheet]').forEach(b => b.onclick = () => buildSheet(b.dataset.sheet, res.questions));
  document.getElementById('similar').onclick = () => {
    if (res.questions.length > 900) return fail(new Error('اختر فصلًا أو درسًا أولًا: اكتشاف المتشابهة يعمل على 900 سؤال كحد أقصى'));
    const pairs = similarPairs(res.questions);
    document.getElementById('similar-out').innerHTML = `<div class="notice ${pairs.length ? '' : 'ok'}">${pairs.length
      ? 'أزواج متشابهة للمراجعة: ' + pairs.map(p => `#${p.a} و#${p.b} (${p.score}%)`).join('، ')
      : 'لا توجد أسئلة متشابهة بدرجة مرتفعة ضمن النتائج.'}</div>`;
  };
}

function bankRow(q) {
  return `<article class="q" id="q-${q.id}">
    <div class="q-head"><label class="actions" style="margin:0;color:var(--ink)"><input type="checkbox" style="width:auto" data-pick="${q.id}" ${state.selection.has(q.id) ? 'checked' : ''}>
      <span class="q-num">#${q.id} · ${q.type === 'mcq' ? 'اختيار' : 'مقالي'}</span></label>${qMeta(q)}</div>
    <div class="small muted">الفصل ${q.chapter.number} ‹ ${esc(q.lesson.title)} ‹ <a href="#/objective/${encodeURIComponent(q.objectiveCode)}">${esc(q.objectiveCode)}</a>: ${esc(q.objectiveText)}</div>
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
  $app.innerHTML = `<div class="crumbs"><a href="#/course">الرئيسية</a> ‹ التقارير</div>
    <div class="hero"><div class="hero-ic">${icon('reports', 52)}<div><h1>التقارير والمؤشرات</h1>
    <p class="muted">تُحسب كل الأرقام لحظيًا من قاعدة البيانات.</p></div></div></div>
    <div class="grid kpi">${kpi(o.n, 'إجمالي الأهداف', 'objectives')}${kpi(o.reviewed || 0, 'أهداف روجعت', 'shield', 'navy')}${kpi(o.approved || 0, 'أهداف معتمدة', 'check')}
      ${kpi(o.returned || 0, 'أهداف تحتاج إلى تعديل', 'essay')}${kpi(q.mcq || 0, 'أسئلة اختيار', 'mcq')}${kpi(q.essay || 0, 'أسئلة مقالية', 'essay', 'navy')}
      ${kpi(q.approved || 0, 'أسئلة معتمدة', 'check')}${kpi((q.n || 0) - (q.approved || 0), 'أسئلة تحتاج إلى مراجعة', 'bank', 'gold')}</div>
    <div class="grid cards" style="margin-top:1rem">
      <section class="card">${ttl('objectives', 'توزيع الأهداف حسب مستوى التفكير')}<p class="small muted">تصنيف مقترح آليًا حتى يعتمده المراجع.</p>
        <div class="levels">${s.levels.map(l => `<div class="progress-line"><span>${esc(l.level)}</span><span class="muted small">${l.n}</span>${bar(l.n, maxLevel)}</div>`).join('')}</div></section>
      <section class="card">${ttl('reports', 'توزيع الأسئلة حسب الفصول')}
        <div class="levels">${s.byChapter.map(c => `<div class="progress-line"><span>${c.number}. ${esc(c.title)}</span><span class="muted small">${c.questions}</span>${bar(c.questions, maxCh)}</div>`).join('')}</div></section>
      <section class="card">${ttl('pie', 'اكتمال التغطية التقويمية')}<div class="levels">
        ${progress('أهداف لها العدد المطلوب من الأسئلة', s.coverage.complete, o.n)}
        ${progress('أهداف بدأ إنتاج أسئلتها', s.coverage.started, o.n)}
        ${progress('أهداف اكتملت أسئلتها المعتمدة', s.coverage.approved_complete, o.n, 'ok')}</div></section>
    </div>
    ${isReviewer() ? `<section class="card" style="margin-top:1rem">${ttl('history', 'آخر التعديلات')}<div id="revs" class="table-wrap">جارٍ التحميل…</div></section>` : ''}`;
  if (isReviewer()) {
    const rows = await api('/revisions?limit=50');
    document.getElementById('revs').innerHTML = rows.length ? `<table class="list"><thead><tr><th>التاريخ</th><th>المستخدم</th><th>العنصر</th><th>الإجراء</th><th>ملاحظة</th></tr></thead>
      <tbody>${rows.map(r => `<tr><td class="ltr">${esc(r.at)}</td><td>${esc(r.user || '')}</td><td>${esc(r.entity)} #${r.entity_id}</td><td>${esc(r.action)}</td><td>${esc(r.note || '')}</td></tr>`).join('')}</tbody></table>`
      : '<div class="empty">لا توجد تعديلات بعد.</div>';
  }
}

// ---------- تسجيل الدخول ----------
const LOGO = '<img class="login-logo" src="assets/itqan-logo.png" alt="إتقان — بنك أسئلة الكيمياء" width="520" height="513">';

function pageLogin() {
  $app.innerHTML = `<div class="login-wrap"><div class="login-card">
    ${LOGO}
    <h1>${icon('lock', 28)}<span>تسجيل الدخول</span></h1>
    ${state.offline ? '<p class="notice bad">تعذر الاتصال بقاعدة البيانات؛ تحقق من الإنترنت ثم أعد تحميل الصفحة.</p>' : ''}
    <form id="login-form" novalidate>
      <div class="field"><label for="l-user">اسم المستخدم</label>
        <div class="in-ic">${line('key', 19)}<input id="l-user" dir="ltr" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="أدخل اسم المستخدم" required></div></div>
      <div class="field"><label for="l-pass">كلمة المرور</label>
        <div class="pass-wrap in-ic">${line('lock', 19)}<input id="l-pass" type="password" dir="ltr" autocomplete="current-password" placeholder="أدخل كلمة المرور" required>
        <button type="button" class="pass-toggle" id="l-show" aria-pressed="false" aria-label="إظهار كلمة المرور" title="إظهار كلمة المرور">${line('eye', 20)}</button></div></div>
      <button class="primary" type="submit" id="l-submit">دخول</button>
    </form>
    <p class="login-foot">الدخول للحسابات المصرّح لها فقط. للحصول على حساب أو استعادة كلمة المرور تواصل مع المشرف.</p>
  </div></div>`;
  const user = document.getElementById('l-user'), pass = document.getElementById('l-pass'), btn = document.getElementById('l-submit');
  user.focus();
  const eyeBtn = document.getElementById('l-show');
  eyeBtn.onclick = () => {
    const show = pass.type === 'password';
    pass.type = show ? 'text' : 'password';
    const label = show ? 'إخفاء كلمة المرور' : 'إظهار كلمة المرور';
    eyeBtn.innerHTML = line(show ? 'eyeOff' : 'eye', 20);
    eyeBtn.setAttribute('aria-pressed', String(show));
    eyeBtn.setAttribute('aria-label', label); eyeBtn.title = label;
    pass.focus();
  };
  document.getElementById('login-form').onsubmit = async e => {
    e.preventDefault();
    if (!user.value.trim() || !pass.value) { toast('اكتب اسم المستخدم وكلمة المرور', true); return; }
    btn.disabled = true; btn.textContent = 'جارٍ الدخول…';
    try {
      const r = await api('/login', { method: 'POST', body: { username: user.value, password: pass.value } });
      state.user = r.user; renderUserbox();
      if (r.user.role !== 'pending') toast('مرحبًا ' + r.user.displayName);
      location.hash = '#/'; route();
    } catch (err) { fail(err); btn.disabled = false; btn.textContent = 'دخول'; }
  };
}

// حساب أُنشئ ولم يحدد المشرف دوره بعد: لا يرى أي محتوى.
function pagePending() {
  $app.innerHTML = `<div class="login-wrap"><div class="login-card">
    ${LOGO}
    <h1>${icon('history', 28)}<span>حسابك بانتظار التفعيل</span></h1>
    <p class="muted">مرحبًا ${esc(state.user.displayName)}. سيظهر لك المحتوى بعد أن يحدد المشرف صلاحيتك.</p>
    <button type="button" class="primary" id="p-out">تسجيل الخروج</button>
  </div></div>`;
  document.getElementById('p-out').onclick = async () => { state.user = null; await apiRaw('/logout', { method: 'POST' }).catch(() => {}); signedOut(); };
}

// ---------- الموجّه ----------
async function route() {
  const seq = ++routeSeq;
  // نافذة تحرير مفتوحة لا تبقى بعد الانتقال (مثل السحب للرجوع على الآيباد)
  if ($dlg.open) $dlg.close();
  const hash = location.hash.replace(/^#/, '') || '/';
  const [, page, arg] = hash.split('/');
  document.querySelectorAll('[data-nav]').forEach(a => a.classList.toggle('active',
    a.dataset.nav === (page || 'home') || (a.dataset.nav === 'chapters' && ['chapter', 'objective'].includes(page))
    || (a.dataset.nav === 'students' && page === 'team') || (a.dataset.nav === 'home' && page === 'course')));
  document.body.classList.remove('print-student', 'print-teacher', 'exam-printing', 'xprint-student', 'xprint-key', 'xprint-all');
  // المنصة مغلقة: بلا دخول تظهر صفحة الدخول فقط، والحساب غير المفعّل يرى رسالة الانتظار.
  const locked = !state.user || state.user.role === 'pending';
  document.body.classList.toggle('locked', locked);
  document.body.classList.remove('booting');
  if (locked) { if (state.user) pagePending(); else pageLogin(); window.scrollTo(0, 0); return; }
  // القائمة حسب الدور: الطالب يرى «تدرّب» و«سجلي» فقط، و«حسابات الطلاب» للمشرف.
  const role = state.user.role, isStudent = role === 'student';
  document.querySelectorAll('[data-perm]').forEach(a => {
    const p = a.dataset.perm;
    a.hidden = !(p === 'student' ? isStudent : p === 'staff' ? !isStudent : can(p) && (state.supabase || !SUPABASE_ONLY.includes(p)));
  });
  const ctx = { api, esc, fail, toast, $app, state, done: () => route() };
  if (isStudent) {
    try {
      if (!state.user.profileConfirmed) pageStudentConfirm(ctx);
      else if (page === 'history') await pageStudentHistory(ctx);
      else { if (page) location.replace('#/'); await pageStudentHome(ctx); }
    } catch (e) {
      if (e?.status === 401) return fail(e);
      if (!e?.stale && seq === routeSeq) $app.innerHTML = `<div class="notice bad">${esc(e.message)}</div>`;
    }
    window.scrollTo(0, 0);
    return;
  }
  try {
    await ensureCourses();
    if (seq !== routeSeq) return;
    if (!page) pageCourses({ esc, $app, courses: state.courses, current: state.course, isOwner: can('edit'), select: setCourse });
    else if (page === 'course') await pageHome();
    else if (page === 'chapters') await pageChapters();
    else if (page === 'chapter') await pageChapter(arg);
    else if (page === 'objective') { objState.answers = {}; await pageObjective(decodeURIComponent(arg)); }
    else if (page === 'bank') await pageBank();
    else if (page === 'reports') await (state.supabase ? pageDashboard(nctx()) : pageReports());
    else if (page === 'exam' && can('exam')) await pageExam({ api, esc, fail, toast, $app, course: state.course });
    else if (page === 'progress' && can('progress')) await pageTeacherProgress(ctx);
    else if (page === 'notes' && can('notes') && state.supabase) await pageNotes(nctx());
    else if (page === 'students' && can('accounts')) await pageAdminStudents(ctx);
    else if (page === 'team' && can('accounts') && state.supabase) await pageAdminTeam(ctx);
    else if (page === 'login') location.hash = '#/';
    else $app.innerHTML = '<div class="empty">الصفحة غير موجودة أو غير متاحة لدورك.</div>';
  } catch (e) {
    if (e?.stale || seq !== routeSeq) return;
    if (e?.status === 401 && state.user) return fail(e);
    $app.innerHTML = `<div class="notice bad">${esc(e.message)}</div>`;
  }
  window.scrollTo(0, 0);
}

// صفحات تعمل على قاعدة Supabase فقط (لا يوفرها الخادم المحلي القديم)
const SUPABASE_ONLY = ['notes'];
window.addEventListener('hashchange', route);
// رابط إلى الصفحة الحالية نفسها (مثل «بنك الأسئلة» من ورقة الأسئلة) لا يطلق hashchange؛ يُعاد عرض الصفحة
document.addEventListener('click', e => {
  const a = e.target.closest?.('a[href^="#/"]');
  if (a && a.getAttribute('href') === (location.hash || '#/') && !e.defaultPrevented) { e.preventDefault(); route(); }
});
window.addEventListener('afterprint', () => document.body.classList.remove('print-student', 'print-teacher'));
// على الموقع المنشور لا يوجد خادم محلي: نتصل بـ Supabase مباشرة بدل انتظار طلب api/me الفاشل.
// حتى تكتمل معرفة الجلسة تبقى شاشة الانتظار، فلا تظهر المنصة لحظة ثم تُستبدل بصفحة الدخول.
const LOCAL_HOST = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
(async () => {
  if (!LOCAL_HOST) await useSupabase();
  return api('/me');
})().then(r => { state.user = r.user; renderUserbox(); route(); }).catch(() => { renderUserbox(); route(); });

// الرجوع إلى تبويب بقي مفتوحًا طويلًا (مثل الآيباد): قد تكون الجلسة انتهت، فنتحقق منها خلف شاشة الانتظار
// بدل عرض الصفحة القديمة ثم الانتقال فجأة إلى صفحة الدخول.
let hiddenAt = 0;
document.addEventListener('visibilitychange', async () => {
  if (document.hidden) { hiddenAt = Date.now(); return; }
  if (!state.supabase || !state.user || Date.now() - hiddenAt < 10 * 60 * 1000) return;
  document.body.classList.add('locked', 'booting');
  try {
    const r = await supa.supaApi('/me');
    if (!r.user) { state.user = null; signedOut(); return; }
    state.user = r.user; renderUserbox();
  } catch (e) { if (e?.status === 401) { state.user = null; signedOut(); return; } }
  if (!state.user) return;
  // الجلسة سليمة: تبقى الصفحة كما هي (دون إعادة رسم تُضيع اختبارًا قيد الإعداد أو تدريبًا قيد الحل)
  document.body.classList.toggle('locked', state.user.role === 'pending');
  document.body.classList.remove('booting');
});
