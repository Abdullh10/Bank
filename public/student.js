// واجهة الطالب: تدريب فقط. السؤال يُعرض دون إجابته، والتصحيح والتفسير يأتيان من قاعدة البيانات بعد الإجابة عن كل سؤال.
// التصميم مبني على توصيات الوكيل التربوي: جلسات قصيرة (10 أسئلة افتراضيًا)، مستويات بثلاث مجموعات، تدرّج من السهل،
// تغذية راجعة فورية تبدأ بسبب خطأ البديل المختار، ومؤقت اختياري لا يقفل الجلسة، ثم «أعد الأخطاء» بأسئلة من الهدف نفسه.

import { qImages } from './media.js';
import { icon, line, CHAPTER_ICONS } from './icons.js';
import { hijri } from './dates.js';
import { surveyForm } from './survey.js';

const LETTERS = ['أ', 'ب', 'ج', 'د'];
const MEDALS = ['🥇', '🥈', '🥉', '4', '5'];
const ttl = (ic, html, tag = 'h2', size = 30) => `<${tag} class="ttl">${icon(ic, size)}<span>${html}</span></${tag}>`;
const GROUPS = { basic: 'أساسي (تذكر وفهم)', apply: 'تطبيق', higher: 'تفكير عليا' };
const LEVEL_CHOICES = [['graded', 'متدرّج (مستحسن)'], ['basic', GROUPS.basic], ['apply', GROUPS.apply], ['higher', GROUPS.higher]];
const PREFS_KEY = 'itqan.student.prefs.v1';
const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
const loadPrefs = () => { try { return JSON.parse(localStorage.getItem(PREFS_KEY)) || {}; } catch { return {}; } };
const savePrefs = p => { try { localStorage.setItem(PREFS_KEY, JSON.stringify(p)); } catch { /* التخزين غير متاح */ } };
const shuffle = a => { const r = [...a]; for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [r[i], r[j]] = [r[j], r[i]]; } return r; };
// قائمة تحقق مرئية: كل بند حالته ok (✓) أو no (✗ محايد: لم يكتمل بعد) أو bad (✗ يمنع الآن) ومعه شرح قصير وعدّاد اختياري
const CHK_TXT = { ok: 'تحقق', no: 'لم يتحقق بعد', bad: 'غير متحقق' };
const chk = items => `<ul class="chk">${items.filter(Boolean).map(([st, title, hint, meter]) => `<li class="${st}"><span class="chk-mark" aria-hidden="true">${st === 'ok' ? line('check', 16) : line('cross', 16)}</span>
  <div class="chk-body"><b>${title}</b><span class="sr">(${CHK_TXT[st]})</span>${hint ? `<span class="small muted">${hint}</span>` : ''}${meter || ''}</div></li>`).join('')}</ul>`;
const meter = (v, t, label) => `<div class="chk-meter"><div class="bar ${v >= t ? 'ok' : ''}"><span style="width:${Math.min(100, pct(v, t))}%"></span></div><span class="small">${label}</span></div>`;
const chip = (ic, val, label) => `<div class="st-chip">${icon(ic, 30)}<div><b>${val}</b><span class="small muted">${label}</span></div></div>`;
const mmss = s => `${String(Math.floor(Math.max(0, s) / 60)).padStart(2, '0')}:${String(Math.max(0, s) % 60).padStart(2, '0')}`;

// رسائل تمدح الجهد والاستراتيجية لا السرعة ولا المقارنة بالآخرين.
function encouragement(score, total) {
  const p = pct(score, total);
  if (p >= 90) return 'إتقان رائع! جرّب مستوى «تفكير عليا» أو درسًا جديدًا لتحدٍّ أكبر.';
  if (p >= 70) return 'أداء جيد. راجع تفسير الأخطاء ثم جرّب «أعد الأخطاء» لتثبيت الفهم.';
  if (p >= 40) return 'بداية جيدة. اقرأ سبب خطأ كل بديل اخترته؛ فهم الخطأ أهم من حفظ الإجابة.';
  return 'كل محاولة تعلّم. ابدأ بالمستوى «أساسي»، واقرأ التفسير بعد كل سؤال، ثم أعد المحاولة.';
}

let session = null; // { id, questions, idx, answers: {qid: result}, order: {qid: [origIdx...]}, timeLimit, startedAt, timer, summary }

export function pageStudentConfirm(ctx) {
  const { state, esc, $app, api, fail, toast } = ctx;
  $app.innerHTML = `<div class="login-wrap"><div class="login-card">
    <img class="login-logo logo-light" src="assets/itqan-logo.svg" alt="إتقان" width="520" height="517"><img class="login-logo logo-dark" src="assets/itqan-logo-dark.svg" alt="إتقان" width="520" height="517">
    <h1>${icon('spark', 28)}<span>مرحبًا بك في إتقان</span></h1>
    <p class="muted small">تأكد من اسمك وشعبتك. تُثبَّت مرة واحدة، ويعدّلها المشرف فقط.</p>
    <form id="c-form" novalidate>
      <div class="field"><label for="c-name">الاسم</label><input id="c-name" value="${esc(state.user.displayName)}" required></div>
      ${state.user.grade ? `<div class="field"><label>الصف</label><div class="st-readonly">${esc(state.user.grade)}</div></div>` : ''}
      <div class="field"><label for="c-sec">الشعبة</label><input id="c-sec" value="${esc(state.user.section || '')}" placeholder="مثال: 2/1" required ${state.user.section ? 'readonly title="حددها المشرف"' : ''}></div>
      <button class="primary" type="submit">تأكيد والبدء</button>
    </form>
    <p class="login-foot">التدريب لا يدخل في الدرجات، ويرى معلمك تقدّمك فيه.</p>
  </div></div>`;
  document.getElementById('c-form').onsubmit = async e => {
    e.preventDefault();
    const btn = e.currentTarget.querySelector('button[type=submit]');
    if (btn.disabled) return; btn.disabled = true;
    try {
      const name = document.getElementById('c-name').value.trim(), section = document.getElementById('c-sec').value.trim();
      await api('/student/confirm', { method: 'POST', body: { name, section } });
      Object.assign(state.user, { displayName: name, section, profileConfirmed: true });
      toast('تم تثبيت بياناتك'); ctx.done();
    } catch (err) { fail(err); btn.disabled = false; }
  };
}

// kind: «course» صفحة «تدرّب» للمقرر الدراسي، و«tahsili» قسم «الاستعداد للتحصيلي» (المواد الأربع ووحداتها)؛ لكل منهما دروسه فقط
let homeKind = 'course';
const SUBJECT_ICONS = { 1: 'drop', 2: 'molecule', 3: 'atom', 4: 'calc' };
export async function pageStudentHome(ctx, kind = 'course') {
  const { state, esc, $app, api, fail } = ctx;
  homeKind = kind;
  const tahsili = kind === 'tahsili';
  if (session?.prep) session = null; // جولة الاستعداد محفوظة إجاباتها، ويُكملها الطالب من قسمها
  if (session && !session.summary) return renderQuestion(ctx); // جلسة جارية
  const catalog = (await api('/student/catalog')).filter(c => (c.kind || 'course') === kind);
  if (!catalog.length && tahsili) {
    $app.innerHTML = `<section class="hero banner"><div class="hero-ic">${icon('exam', 64)}<div>
      <h1>الاستعداد للتحصيلي</h1>
      <p class="muted">لم يُفتح لك هذا القسم بعد؛ يفتحه معلمك حين يجهز محتواه.</p></div></div></section>`;
    return;
  }
  if (!catalog.length) {
    $app.innerHTML = `<section class="hero banner"><div class="hero-ic">${icon('practice', 64)}<div>
      <h1>مرحبًا ${esc(state.user.displayName.split(' ')[0])}</h1>
      <p class="muted">لم يُسند لك مقرر بعد؛ راجع معلمك ليسند لك مقررك، ثم أعد تحميل الصفحة.</p></div></div></section>`;
    return;
  }
  const prefs = { count: 10, levels: 'graded', timed: false, lessons: [], ...loadPrefs() };
  const chosen = new Set(prefs.lessons);
  const multi = new Set(catalog.map(c => c.courseId)).size > 1;
  $app.innerHTML = `
    ${tahsili ? `<section class="hero banner"><div class="hero-ic">${icon('exam', 64)}<div>
      <span class="eyebrow">${icon('spark', 18)} أسئلة تدريبية على نمط اختبار التحصيل الدراسي</span>
      <h1>الاستعداد للتحصيلي</h1>
      <p class="muted">الأحياء والكيمياء والفيزياء والرياضيات، لكل مادة 25% من الاختبار. اختر المادة ووحداتها ثم ابدأ؛ التصحيح والتفسير بعد كل سؤال.</p></div></div></section>`
    : `<section class="hero banner"><div class="hero-ic">${icon('practice', 64)}<div>
      <span class="eyebrow">${icon('spark', 18)} تدريب ذاتي لا يدخل في الدرجات</span>
      <h1>تدرّب يا ${esc(state.user.displayName.split(' ')[0])}</h1>
      <p class="muted">اختر الدروس وعدد الأسئلة والمستوى، ثم ابدأ. التصحيح والتفسير يظهران بعد كل سؤال.</p></div></div></section>`}
    <section class="card st-bal" id="st-bal" hidden></section>
    <section class="card st-task" id="st-task" hidden></section>
    <ol class="st-steps"><li><b>١</b> ${tahsili ? 'اختر الوحدات' : 'اختر الدروس'}</li><li><b>٢</b> اضبط الجلسة</li><li><b>٣</b> ابدأ التدريب</li></ol>
    <div class="grid2 st-setup">
      <section class="card">${ttl('lessons', tahsili ? 'المواد والوحدات' : 'الدروس')}
        ${catalog.map(c => `<details class="st-ch" ${c.lessons.some(l => chosen.has(l.id)) ? 'open' : ''}>
          <summary>${tahsili ? `${icon(SUBJECT_ICONS[c.number] || 'chapters', 30)}<span><b>${esc(c.title)}</b></span>`
            : `${icon(CHAPTER_ICONS[c.number] || 'chapters', 30)}<span>${multi && c.course ? `<small class="muted">${esc(c.course)} · </small>` : ''}<b>الفصل ${c.number}:</b> ${esc(c.title)}</span>`}</summary>
          ${c.lessons.map((l, i) => {
            const n = l.basic + l.apply + l.higher;
            // التحصيلي: عنوان الوحدة «الصف · الموضوع»، فتُجمع الوحدات تحت عنوان صفها
            const [grade, title] = tahsili && l.title.includes(' · ') ? l.title.split(' · ') : [null, l.title];
            const prevGrade = i && tahsili ? c.lessons[i - 1].title.split(' · ')[0] : null;
            return `${grade && grade !== prevGrade ? `<div class="st-grade">${esc(grade)}</div>` : ''}<label class="st-lesson"><input type="checkbox" data-lesson="${l.id}" ${chosen.has(l.id) ? 'checked' : ''} ${n ? '' : 'disabled'}>
              <span>${esc(title)}</span>
              ${l.answered ? `<span class="st-mastery" title="نسبة إجاباتك الصحيحة في هذا الدرس"><span style="width:${pct(l.correct, l.answered)}%"></span></span><small>${pct(l.correct, l.answered)}%</small>` : '<small class="muted">لم تبدأ</small>'}
            </label>`;
          }).join('')}
        </details>`).join('')}
      </section>
      <section class="card">${ttl('sliders', 'إعداد الجلسة')}
        <div class="field"><label for="s-count">عدد الأسئلة</label>
          <select id="s-count">${[5, 10, 15, 20].map(n => `<option ${n === prefs.count ? 'selected' : ''}>${n}</option>`).join('')}</select></div>
        <fieldset class="field"><legend>المستوى</legend>
          ${LEVEL_CHOICES.map(([v, t]) => `<label class="st-radio"><input type="radio" name="s-level" value="${v}" ${v === prefs.levels ? 'checked' : ''}> ${t}</label>`).join('')}
          <p class="small muted">«متدرّج»: أسئلة أساسية ثم تطبيق ثم تفكير عليا، من الأسهل إلى الأصعب.</p></fieldset>
        <label class="st-radio"><input type="checkbox" id="s-timed" ${prefs.timed ? 'checked' : ''}> مؤقت للجلسة <span class="small muted">(اختياري: دقيقة لسؤال التذكر والفهم، ونحو دقيقتين لغيره، ولا تُقفل الجلسة بانتهائه)</span></label>
        <p class="small muted">الأسئلة والبدائل تُخلط في كل جلسة.</p>
      </section>
    </div>
    <section class="card st-top5" id="st-top5" hidden></section>
    <div class="st-cta"><span id="st-sum" class="st-sum" aria-live="polite"></span>
      <button class="primary st-start" id="s-start" type="button">${line('next', 18)}ابدأ التدريب</button></div>`;
  const sum = () => {
    const n = $app.querySelectorAll('[data-lesson]:checked').length, c = document.getElementById('s-count').value;
    document.getElementById('st-sum').textContent = n ? `${n === 1 ? (tahsili ? 'وحدة واحدة' : 'درس واحد') : n + (tahsili ? ' وحدات' : ' دروس')} · ${c} سؤالًا` : (tahsili ? 'اختر وحدة واحدة على الأقل' : 'اختر درسًا واحدًا على الأقل');
  };
  $app.querySelectorAll('input, select').forEach(e => { e.onchange = sum; }); sum();
  // بطاقات المقرر الدراسي (التميّز والمهام والرصيد) لا تظهر في قسم التحصيلي: نقاطه منفصلة عن نقاط المقرر
  if (!tahsili) courseCards(ctx);
  document.getElementById('s-start').onclick = async () => {
    const lessons = [...$app.querySelectorAll('[data-lesson]:checked')].map(i => Number(i.dataset.lesson));
    const p = { lessons, count: Number(document.getElementById('s-count').value),
      levels: $app.querySelector('[name="s-level"]:checked').value, timed: document.getElementById('s-timed').checked };
    if (!lessons.length) return fail(new Error(tahsili ? 'اختر وحدة واحدة على الأقل' : 'اختر درسًا واحدًا على الأقل'));
    savePrefs(p);
    await startSession(ctx, p);
  };
}

function courseCards(ctx) {
  const { esc, api } = ctx;
  // المتميزون الخمسة في شعبة الطالب (إن توفّرت قائمة التميّز): يعرفهم زملاؤهم ويقتدون بهم
  cachedApi(api, '/student/rank').then(d => {
    const box = document.getElementById('st-top5');
    eliteCelebrate(ctx, d);
    if (!box || !d?.available || !d.top?.length) return;
    box.innerHTML = `<div class="st-top5-head">${ttl('trophy', 'المتميزون في شعبتك', 'h2', 30)}<a class="btn" href="#/rank">ترتيبي وكيف تُحسب النقاط ←</a></div>
      <ol class="st-top5-list">${d.top.map(t => `<li class="${t.me ? 'me' : ''}"><span aria-hidden="true">${MEDALS[t.rank - 1] || t.rank}</span> ${esc(t.name)}${t.elite ? ELITE_BADGE : ''}${t.me ? ' <span class="badge brand">أنت</span>' : ''}</li>`).join('')}</ol>`;
    box.hidden = false;
  }).catch(() => {});
  // مهمتك الآن: أقرب مهمة مفتوحة من معلمك (استعلام خفيف)
  cachedApi(api, '/student/comms/summary').then(d => {
    const box = document.getElementById('st-task');
    if (!box || (!d?.task && !d?.unread)) return;
    const t = d.task;
    box.innerHTML = `<div class="st-top5-head">${ttl('mail', t ? 'مهمتك الآن' : 'لديك رسائل من معلمك', 'h2', 30)}<a class="btn" href="#/inbox">${d.unread ? `رسائل معلمي (${num(d.unread)} جديدة)` : 'رسائل معلمي'} ←</a></div>
      ${t ? `<p class="bal-ready"><b>${esc(t.title)}</b> · ${num(t.n)} سؤالًا قبل ${esc(hijri(t.dueAt))}</p>` : ''}`;
    box.hidden = false;
  }).catch(() => {});
  // شريط الرصيد: نقاطك المتاحة وما بقي للدرجة القادمة
  cachedApi(api, '/student/balance').then(d => {
    const box = document.getElementById('st-bal');
    if (!box || !d?.available) return;
    const rate = d.settings.rate;
    const frac = d.ready ? 1 : Math.min(1, (d.points - d.ready * rate) / rate);
    box.innerHTML = `<div class="st-top5-head">${ttl('coin', 'أين أنا؟', 'h2', 30)}<a class="btn" href="#/balance">${d.ready ? 'استبدل نقاطك بدرجة ←' : 'فتح الرصيد ←'}</a></div>
      <div class="st-chips">${chip('coin', num(d.points), 'نقطة متاحة')}${chip('spark', `${d.streak ? '🔥 ' : ''}${num(d.streak)}`, 'أيام جادة متتالية')}${chip('trophy', num(d.pending + d.recorded), 'درجات استبدلتها')}</div>
      <p class="bal-ready">${d.ready ? `لديك <b>${num(d.ready)}</b> ${d.ready === 1 ? 'درجة جاهزة' : 'درجات جاهزة'} للاستبدال!` : `باقي <b>${num(Math.max(0.1, d.toNext))}</b> نقطة على درجتك القادمة.`}</p>
      <div class="bar ${d.ready ? 'ok' : ''}"><span style="width:${Math.round(100 * frac)}%"></span></div>`;
    box.hidden = false;
  }).catch(() => {});
}

async function startSession(ctx, p) {
  const { api, fail } = ctx;
  const btn = document.getElementById('s-start');
  if (btn) { btn.disabled = true; btn.textContent = 'جارٍ التحضير…'; }
  try {
    const s = await api('/student/start', { method: 'POST', body: p });
    session = { ...s, idx: 0, answers: {}, order: Object.fromEntries(s.questions.map(q => [q.id, shuffle([...q.options.keys()])])), startedAt: Date.now(), summary: null };
    location.hash = homeKind === 'tahsili' ? '#/tahsili' : '#/';
    renderQuestion(ctx);
  } catch (e) { fail(e); if (btn) { btn.disabled = false; btn.textContent = 'ابدأ التدريب'; } }
}

// الإبلاغ عن مشكلة في السؤال: يصل البلاغ إلى المراجع العلمي ومالك المشروع دون اسم الطالب
const REPORT_REASONS = [['answer', 'الإجابة الصحيحة المعتمدة غير صحيحة'], ['wording', 'خطأ في صياغة السؤال أو البدائل'], ['figure', 'خطأ في الجدول أو الشكل'], ['other', 'مشكلة أخرى']];
function reportDialog(ctx, q) {
  const { api, fail, toast } = ctx;
  const dlg = document.createElement('dialog');
  dlg.className = 'bal-dlg';
  dlg.innerHTML = `<form method="dialog"><h2>الإبلاغ عن مشكلة في السؤال</h2>
    <fieldset class="st-rep-opts"><legend class="small muted">ما المشكلة؟</legend>${REPORT_REASONS.map(([v, t], i) => `<label class="st-radio"><input type="radio" name="rr" value="${v}" ${i === 0 ? 'checked' : ''}> ${t}</label>`).join('')}</fieldset>
    <label for="rr-body" class="small">تفاصيل (اختيارية، وإلزامية عند «مشكلة أخرى»)</label>
    <textarea id="rr-body" dir="auto" maxlength="500" rows="3"></textarea>
    <p class="small muted">سيصل بلاغك إلى المراجع العلمي ومالك المشروع للتحقق منه، ولا يظهر اسمك فيه. لن يتأثر تدريبك ولا نقاطك.</p>
    <p class="notice bad small" id="rr-err" hidden></p>
    <div class="actions"><button type="button" class="primary" id="rr-send">تأكيد الإرسال</button><button value="no">إلغاء</button></div></form>`;
  document.body.append(dlg);
  dlg.addEventListener('close', () => dlg.remove());
  dlg.querySelector('#rr-send').onclick = async e => {
    const reason = dlg.querySelector('[name=rr]:checked').value, body = dlg.querySelector('#rr-body').value.trim();
    const err = dlg.querySelector('#rr-err');
    if (reason === 'other' && body.length < 3) { err.textContent = 'اكتب وصف المشكلة'; err.hidden = false; return; }
    const btn = e.currentTarget; btn.disabled = true;
    try { await api('/student/report', { method: 'POST', body: { question: q.id, reason, body }, keep: true }); dlg.close(); toast('وصل بلاغك، شكرًا لك'); }
    catch (x) { btn.disabled = false; err.textContent = x.message; err.hidden = false; }
  };
  dlg.showModal();
}

function stopTimer() { if (session?.timer) { clearInterval(session.timer); session.timer = null; } }

function renderQuestion(ctx) {
  const { esc, $app, api, fail } = ctx;
  const q = session.questions[session.idx];
  const res = session.answers[q.id];
  const order = session.order[q.id];
  const answeredCount = Object.keys(session.answers).length;
  const last = session.idx === session.questions.length - 1;
  $app.innerHTML = `<div class="st-run">
    <div class="st-top">
      <span>${icon(session.retry || session.mode === 'wrong' ? 'history' : session.prep ? 'objectives' : 'practice', 28)}${session.prep ? `${esc(session.prep.title)} · ${session.mode === 'wrong' ? 'مراجعة الأخطاء · ' : ''}` : session.retry ? 'إعادة الأخطاء · ' : ''}سؤال ${session.idx + 1} من ${session.questions.length}</span>
      ${session.timeLimit ? '<span class="st-timer" id="st-timer" aria-live="off"></span>' : ''}
      <button type="button" id="st-end">إنهاء الجلسة</button>
    </div>
    <div class="bar"><span style="width:${pct(answeredCount, session.questions.length)}%"></span></div>
    <article class="card st-q">
      <div class="st-qhead"><div class="st-meta">${esc(q.lesson.includes(' · ') ? q.lesson.split(' · ')[1] : q.lesson)} · ${GROUPS[q.group]}${q.examYear ? ` <span class="badge year" title="سنة ورود السؤال في اختبار التحصيل الدراسي">ورد في تحصيلي ${q.examYear}</span>` : ''}</div><button type="button" class="st-report" id="st-report" title="الإبلاغ عن مشكلة في السؤال">${line('flag', 15)}الإبلاغ عن مشكلة في السؤال</button></div>
      <p class="st-stem">${esc(q.stem)}</p>
      ${qImages(q.images, 'q-figs st-figs')}
      ${q.stimulus ? `<div class="table-wrap"><table class="data-table"><thead><tr>${q.stimulus.headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead>
        <tbody>${q.stimulus.rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>` : ''}
      <div class="st-opts" role="radiogroup">
        ${order.map((orig, pos) => {
          let cls = '';
          if (res) cls = orig === res.correctIndex ? 'ok' : orig === res.choice ? 'bad' : 'dim';
          return `<button type="button" class="opt st-opt ${cls}" data-orig="${orig}" ${res ? 'disabled' : ''} role="radio" aria-checked="${res && orig === res.choice}">
            <span class="letter">${LETTERS[pos]}</span><span>${esc(q.options[orig])}</span>${cls === 'ok' ? `<span class="st-mark">${line('check', 16)}</span>` : cls === 'bad' ? `<span class="st-mark">${line('cross', 16)}</span>` : ''}</button>`;
        }).join('')}
      </div>
      ${res ? feedback(res, q, order, esc) : ''}
    </article>
    <div class="actions st-nav">
      ${session.idx > 0 ? `<button type="button" id="st-prev">${line('prev', 17)}السابق</button>` : ''}
      ${res ? `<button type="button" class="primary" id="st-next">${last ? 'عرض النتيجة' : 'التالي'}${line('next', 17)}</button>` : ''}
    </div>
  </div>`;
  if (session.timeLimit) tickTimer();
  $app.querySelectorAll('.st-opt:not([disabled])').forEach(b => b.onclick = async () => {
    $app.querySelectorAll('.st-opt').forEach(x => { x.disabled = true; });
    b.classList.add('chosen');
    const sess = session;
    try {
      // keep: تُحفظ نتيجة الإجابة حتى لو انتقل الطالب إلى «سجلي» قبل وصول الرد
      const r = sess.prep
        ? await api('/student/prep/answer', { method: 'POST', body: { set: sess.prep.id, question: q.id, choice: Number(b.dataset.orig) }, keep: true })
        : await api('/student/answer', { method: 'POST', body: { session: sess.id, question: q.id, choice: Number(b.dataset.orig) }, keep: true });
      sess.answers[q.id] = { ...r, choice: Number(b.dataset.orig) };
      if (session === sess && document.querySelector('.st-run')) renderQuestion(ctx);
    } catch (e) {
      fail(e);
      // أخفى المعلم المجموعة أثناء الجولة: نعود إلى صفحة القسم
      if (sess.prep && e.status === 403) { session = null; location.hash = '#/prep'; ctx.done(); return; }
      if (session === sess && document.querySelector('.st-run')) renderQuestion(ctx);
    }
  });
  document.getElementById('st-report').onclick = () => reportDialog(ctx, q);
  const others = document.getElementById('st-others');
  if (others) others.onclick = () => { document.getElementById('st-others-list').hidden = false; others.remove(); };
  const next = document.getElementById('st-next');
  if (next) next.onclick = () => (last ? finishSession(ctx) : (session.idx++, renderQuestion(ctx)));
  const prev = document.getElementById('st-prev');
  if (prev) prev.onclick = () => { session.idx--; renderQuestion(ctx); };
  document.getElementById('st-end').onclick = () => {
    const left = session.questions.length - Object.keys(session.answers).length;
    if (left && !confirm(`بقي ${left} سؤالًا دون إجابة. إنهاء الجلسة الآن؟`)) return;
    finishSession(ctx);
  };
  window.scrollTo(0, 0);
}

// التغذية الراجعة: سبب خطأ البديل المختار أولًا، ثم التفسير، ثم بقية البدائل عند الطلب.
function feedback(res, q, order, esc) {
  const notes = res.distractorNotes || [];
  const pos = o => LETTERS[order.indexOf(o)];
  const otherWrong = [...q.options.keys()].filter(o => o !== res.correctIndex && o !== res.choice && notes[o]);
  return `<div class="notice ${res.correct ? 'ok' : 'bad'} st-fb" role="status">
    <strong>${icon(res.correct ? 'check' : 'cross', 30)}<span>${res.correct ? 'إجابة صحيحة ✓' : `إجابة غير صحيحة. الصحيح: (${pos(res.correctIndex)})`}</span></strong>
    ${!res.correct && notes[res.choice] ? `<p><b>لماذا (${pos(res.choice)}) خطأ؟</b> ${esc(notes[res.choice])}</p>` : ''}
    ${res.explanation ? `<p><b>التفسير:</b> ${esc(res.explanation)}</p>` : ''}
    ${otherWrong.length ? `<button type="button" class="linklike" id="st-others">اعرض سبب خطأ البدائل الأخرى</button>
      <ul id="st-others-list" hidden>${otherWrong.map(o => `<li><b>(${pos(o)})</b> ${esc(notes[o])}</li>`).join('')}</ul>` : ''}
  </div>`;
}

function tickTimer() {
  stopTimer();
  const el = () => document.getElementById('st-timer');
  const draw = () => {
    const left = session.timeLimit - Math.floor((Date.now() - session.startedAt) / 1000);
    const t = el(); if (!t) return stopTimer();
    t.textContent = left > 0 ? `الوقت المتبقي ${mmss(left)}` : 'انتهى الوقت المقترح، يمكنك الإكمال';
    t.classList.toggle('over', left <= 0);
  };
  draw();
  session.timer = setInterval(draw, 1000);
}

let finishing = false;
async function finishSession(ctx) {
  const { api, fail } = ctx;
  if (finishing || !session) return;
  if (session.prep) { session.summary = prepSummary(session); homeCache.clear(); if (document.querySelector('.st-run')) renderSummary(ctx); return; }
  finishing = true;
  try {
    const sum = await api('/student/finish', { method: 'POST', body: { session: session.id }, keep: true });
    homeCache.clear();
    stopTimer(); // يتوقف المؤقت بعد نجاح الإنهاء فقط
    if (!session) return;
    session.summary = sum;
    if (document.querySelector('.st-run')) renderSummary(ctx);
  } catch (e) { fail(e); } finally { finishing = false; }
}

function renderSummary(ctx) {
  const { esc, $app } = ctx;
  const s = session.summary;
  const usedSec = Math.round((Date.now() - session.startedAt) / 1000);
  $app.innerHTML = `<div class="st-run">
    <section class="card st-result">
      <h1>نتيجة الجلسة</h1>
      ${ring(pct(s.score, s.total) / 100, `<b>${pct(s.score, s.total)}%</b><span class="small muted">نسبة الصحة</span>`, 'نسبة إجاباتك الصحيحة')}
      <div class="st-score"><b>${s.score}</b> من ${s.total}</div>
      <div class="st-chips c2">${chip('check', num(s.score), 'إجابة صحيحة')}${chip('cross', num(Math.max(0, s.answered - s.score)), 'إجابة خاطئة')}</div>
      <p class="st-enc">${encouragement(s.score, s.total)}</p>
      ${session.timeLimit ? `<p class="small muted">الوقت المستغرق ${mmss(usedSec)} من ${mmss(session.timeLimit)} مقترحة.</p>` : ''}
      ${s.answered < s.total ? `<p class="small muted">أجبت عن ${s.answered} من ${s.total}.</p>` : ''}
    </section>
    <div class="grid2">
      <section class="card">${ttl('lessons', 'حسب الدرس')}${table(s.byLesson.map(r => [r.lesson, r.correct, r.n]), esc)}</section>
      <section class="card">${ttl('reports', 'حسب المستوى')}${table(s.byGroup.map(r => [GROUPS[r.group], r.correct, r.n]), esc)}</section>
    </div>
    ${session.prep ? `<div class="actions st-nav st-after">
      <button type="button" class="primary" id="st-prep-next">${line('next', 17)}الجولة التالية</button>
      ${s.wrong ? `<button type="button" id="st-prep-wrong">${icon('history', 22, 'navy')}راجع أخطائي</button>` : ''}
      <button type="button" id="st-prep-back">${line('prev', 17)}الاستعداد للاختبار</button>
    </div>` : `<div class="actions st-nav st-after">
      ${s.wrong ? `<button type="button" class="primary" id="st-retry">${icon('history', 22, 'navy')}أعد الأخطاء</button>` : ''}
      <button type="button" id="st-new">${line('plus', 17)}جلسة جديدة</button>
      <a class="btn" href="#/history">${line('clock', 17)}سجلي</a>
    </div>`}
  </div>`;
  if (session.prep) {
    const set = session.prep;
    document.getElementById('st-prep-next').onclick = () => startPrep(ctx, set, 'next');
    document.getElementById('st-prep-wrong')?.addEventListener('click', () => startPrep(ctx, set, 'wrong'));
    document.getElementById('st-prep-back').onclick = () => { session = null; ctx.done(); };
    window.scrollTo(0, 0);
    return;
  }
  const retry = document.getElementById('st-retry');
  if (retry) retry.onclick = () => startSession(ctx, { retry: s.id });
  document.getElementById('st-new').onclick = () => { session = null; ctx.done(); };
  window.scrollTo(0, 0);
}

// ---------- الاستعداد للاختبار: أسئلة يحددها المعلم، تدريب بلا نقاط ----------
// النتيجة تُحسب هنا من إجابات الجولة (لا جلسة تدريب في الخادم، فلا تدخل النقاط ولا السجل)
function prepSummary(sess) {
  const ans = sess.questions.filter(q => sess.answers[q.id]);
  const groupBy = (key, label) => Object.values(ans.reduce((m, q) => {
    const k = key(q); m[k] ||= { [label]: k, n: 0, correct: 0 }; m[k].n++; if (sess.answers[q.id].correct) m[k].correct++; return m;
  }, {}));
  const score = ans.filter(q => sess.answers[q.id].correct).length;
  return { total: sess.questions.length, answered: ans.length, score, wrong: ans.length - score,
    byLesson: groupBy(q => q.lesson, 'lesson'), byGroup: groupBy(q => q.group, 'group') };
}
async function startPrep(ctx, set, mode) {
  const { api, fail } = ctx;
  try {
    const s = await api('/student/prep/start', { method: 'POST', body: { set: set.id, mode } });
    session = { ...s, prep: s.set, idx: 0, answers: {}, order: Object.fromEntries(s.questions.map(q => [q.id, shuffle([...q.options.keys()])])), startedAt: Date.now(), summary: null };
    if (location.hash !== '#/prep') location.hash = '#/prep';
    renderQuestion(ctx);
  } catch (e) { fail(e); }
}
export async function pageStudentPrep(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  if (session?.prep && !session.summary) return renderQuestion(ctx); // جولة جارية
  if (session?.prep && session.summary) return renderSummary(ctx);
  const sets = await api('/student/prep');
  const multi = new Set(sets.map(s => s.courseId)).size > 1;
  $app.innerHTML = `<section class="hero banner"><div class="hero-ic">${icon('objectives', 64)}<div>
      <span class="eyebrow">${icon('spark', 18)} تدريب للمراجعة: لا يُحتسب في النقاط ولا الترتيب</span>
      <h1>الاستعداد للاختبار</h1>
      <p class="muted">أسئلة حددها معلمك لاختبارك القادم. تمرّ عليها كلها على جولات من 20 سؤالًا، والتصحيح والتفسير بعد كل سؤال، ثم تراجع ما أخطأت فيه.</p></div></div></section>
    ${sets.length ? `<div class="grid cards">${sets.map(s => {
      const done = s.n && s.covered >= s.n;
      return `<section class="card pr-card">
        <h2 class="ttl">${icon('objectives', 30)}<span>${esc(s.title)}</span></h2>
        ${multi ? `<p class="small muted">${esc(s.course)}</p>` : ''}
        ${s.note ? `<p class="small">${esc(s.note)}</p>` : ''}
        <p class="small muted">${esc(s.lessonTitles.join('، '))}</p>
        <div class="pr-prog"><div class="bar ${done ? 'ok' : ''}"><span style="width:${pct(s.covered, s.n)}%"></span></div>
          <span class="small"><b>أجبت عن ${num(s.covered)} من ${num(s.n)}</b>${s.covered ? ` · صحيح ${num(s.correct)} (${pct(s.correct, s.covered)}%)` : ''}${s.cycle > 1 ? ` · الجولة ${num(s.cycle)}` : ''}</span></div>
        <div class="actions">
          ${done ? '' : `<button type="button" class="primary" data-go="${s.id}">${line('next', 17)}${s.covered ? 'تابع' : 'ابدأ'}</button>`}
          ${s.wrong ? `<button type="button" data-wrong="${s.id}">${icon('history', 20, 'navy')}راجع أخطائي (${num(s.wrong)})</button>` : ''}
          ${s.covered ? `<button type="button" data-restart="${s.id}">${line('plus', 17)}ابدأ من جديد</button>` : ''}
        </div>
        ${done && !s.wrong ? '<p class="notice ok small">أنهيت كل الأسئلة دون أخطاء متبقية. أحسنت!</p>' : ''}
      </section>`; }).join('')}</div>`
    : `<div class="empty">${icon('empty', 56)}<p>لا توجد أسئلة استعداد مفتوحة لك الآن؛ يفتحها معلمك قبل الاختبار.</p></div>`}`;
  const byId = id => sets.find(s => String(s.id) === id);
  $app.querySelectorAll('[data-go]').forEach(b => b.onclick = () => startPrep(ctx, byId(b.dataset.go), 'next'));
  $app.querySelectorAll('[data-wrong]').forEach(b => b.onclick = () => startPrep(ctx, byId(b.dataset.wrong), 'wrong'));
  $app.querySelectorAll('[data-restart]').forEach(b => b.onclick = async () => {
    if (!confirm('تبدأ المرور على كل الأسئلة من جديد ويُصفَّر عدّاد تقدمك (تبقى إجاباتك السابقة محفوظة). متابعة؟')) return;
    try { await api('/student/prep/restart', { method: 'POST', body: { set: b.dataset.restart } }); toast('بدأت جولة جديدة'); pageStudentPrep(ctx).catch(fail); } catch (e) { fail(e); }
  });
}

function table(rows, esc) {
  if (!rows.length) return '<div class="empty">لا توجد إجابات.</div>';
  return `<table class="list"><tbody>${rows.map(([name, c, n]) => `<tr><td>${esc(name)}</td><td class="ltr">${c}/${n}</td>
    <td style="width:40%"><div class="bar ${pct(c, n) >= 70 ? 'ok' : ''}"><span style="width:${pct(c, n)}%"></span></div></td></tr>`).join('')}</tbody></table>`;
}

export async function pageStudentHistory(ctx) {
  const { esc, $app, api } = ctx;
  const [hist, catalog] = await Promise.all([api('/student/history'), api('/student/catalog')]);
  const lessons = catalog.flatMap(c => c.lessons.filter(l => l.answered).map(l => ({ ...l, chapter: c.number })));
  const tot = hist.reduce((a, h) => ({ s: a.s + h.score, t: a.t + h.total }), { s: 0, t: 0 });
  $app.innerHTML = `
    <section class="hero"><div class="hero-ic">${icon('history', 52)}<div><h1>سجلي</h1><p class="muted">تقدّمك في التدريب. لا يرى زملاؤك تفاصيل تدريبك؛ يظهر اسمك ونقاطك فقط إن دخلت قائمة التميّز.</p></div></div></section>
    ${hist.length ? `<div class="st-chips">${chip('practice', num(hist.length), 'جلسة أخيرة')}${chip('check', `${num(pct(tot.s, tot.t))}%`, 'نسبة الصحة فيها')}${chip('lessons', num(lessons.length), 'دروس تدرّبت عليها')}</div>` : `<section class="card st-empty">${icon('practice', 56)}<p>لم تبدأ التدريب بعد. جلسة قصيرة من 10 أسئلة تكفي للبداية.</p><a class="btn primary" href="#/">ابدأ التدريب</a></section>`}
    <div class="grid2">
      <section class="card">${ttl('progress', 'تقدّمك في الدروس')}
        ${lessons.length ? table(lessons.map(l => [`${l.chapter}. ${l.title}`, l.correct, l.answered]), esc) : '<div class="empty">لم تبدأ التدريب بعد.</div>'}
        ${lessons.some(l => pct(l.correct, l.answered) < 70) ? '<p class="small muted">الدروس التي تقل عن 70% تستحق جلسة أخرى.</p>' : ''}
      </section>
      <section class="card">${ttl('history', 'آخر الجلسات')}
        ${hist.length ? `<table class="list"><thead><tr><th>التاريخ</th><th>النتيجة</th><th></th></tr></thead><tbody>
          ${hist.map(h => `<tr><td class="small">${esc(hijri(h.createdAt, true))}</td>
            <td>${h.score}/${h.total} (${pct(h.score, h.total)}%)</td>
            <td>${h.wrong ? `<button type="button" data-retry="${h.id}">أعد أخطاءها</button>` : ''}</td></tr>`).join('')}</tbody></table>`
          : '<div class="empty">لا توجد جلسات بعد.</div>'}
      </section>
    </div>`;
  $app.querySelectorAll('[data-retry]').forEach(b => b.onclick = () => startSession(ctx, { retry: Number(b.dataset.retry) }));
}

// ---------- التميّز: ترتيب المتدربين في الشعبة ----------
// نتائج شريطي الصفحة الرئيسية (المتميزون والرصيد) تُحفظ نصف دقيقة: العودة المتكررة للرئيسية لا تضاعف الحمل على قاعدة البيانات
const homeCache = new Map();
const cachedApi = (api, path, ttl = 30000) => {
  const hit = homeCache.get(path);
  if (hit && Date.now() - hit.at < ttl) return Promise.resolve(hit.data);
  return api(path).then(data => { homeCache.set(path, { at: Date.now(), data }); return data; });
};
const num = n => Number(n || 0).toLocaleString('ar-SA-u-nu-latn');
const ELITE_BADGE = ' <span class="badge elite" title="حلّ أغلب أسئلة المقرر">النخبة</span>';

// بطاقة «النخبة»: من حلّ 95% من أسئلة المقرر يُكافأ على مراجعة ما حلّه (كل 250 إجابة = 100 نقطة)
function eliteCard(m, r) {
  if (!m.eliteNeed) return '';
  if (!m.elite) {
    if (m.eliteHave < m.eliteNeed * 0.5) return '';
    return `<section class="card elite-card">${ttl('trophy', 'الطريق إلى النخبة')}
      <p class="muted">حين تحلّ ${num(r.elitePct)}% من أسئلة المقرر تدخل مستوى «النخبة»، وتُكافأ بعدها على مراجعة ما حللته.</p>
      ${meter(m.eliteHave, m.eliteNeed, `حللت ${num(Math.min(m.eliteHave, m.eliteNeed))} من ${num(m.eliteNeed)} سؤالًا مختلفًا`)}</section>`;
  }
  const cur = m.eliteN % r.eliteBlock, done = Math.floor(m.eliteN / r.eliteBlock), got = m.eliteBonus / r.eliteReward;
  const acc = cur ? Math.round(100 * m.eliteCurK / cur) : null;
  return `<section class="card elite-card">${ttl('trophy', 'أنت في مستوى النخبة')}
    <p>حللت أغلب أسئلة المقرر، فصار لك مستوى خاص: كل <b>${num(r.eliteBlock)}</b> إجابة مراجعة محتسبة تضيف <b>${num(r.eliteReward)}</b> نقطة إن كانت صحتها ${num(r.eliteAcc)}% فأكثر.</p>
    ${meter(cur, r.eliteBlock, `${num(cur)} من ${num(r.eliteBlock)} حتى المكافأة القادمة${acc != null ? ` · صحتك فيها ${num(acc)}%` : ''}`)}
    <p class="small muted">مكافآتك حتى الآن: ${num(m.eliteBonus)} نقطة (${num(got)} من ${num(done)} دفعة مكتملة).
      المراجعة المحتسبة: سؤال سبق أن حللته ومضى على آخر محاولة فيه ${num(r.eliteGapDays)} أيام فأكثر، وبتأنٍّ (لا أسرع من ${num(r.rushSecs)} ثوانٍ)، وأول ${num(r.eliteDailyCap)} في اليوم.</p></section>`;
}
export async function pageStudentRank(ctx) {
  const { esc, $app, api } = ctx;
  const d = await api('/student/rank');
  const hero = `<section class="hero"><div class="hero-ic">${icon('trophy', 52)}<div><h1>التميّز</h1>
    <p class="muted">ترتيب المتدربين في شعبتك خلال هذا الفصل الدراسي. النقاط تكافئ التدريب الجاد والمنتظم، لا التخمين ولا السرعة.</p></div></div></section>`;
  if (!d.available) {
    $app.innerHTML = `${hero}<section class="card"><div class="empty">${d.reason === 'section' ? 'لم تُحدَّد شعبتك بعد؛ راجع معلمك ليظهر لك الترتيب.' : 'لم يُسند لك مقرر جاهز بعد.'}</div></section>`;
    return;
  }
  const m = d.me, r = d.rules;
  eliteCelebrate(ctx, d);
  const bandText = { q3: 'الربع الثالث', q4: 'الربع الرابع' };
  let mine;
  if (m.eligible && m.rank) {
    mine = `<div class="rank-me"><div class="rank-big" aria-label="ترتيبك">${num(m.rank)}</div>
      <div><strong>ترتيبك في شعبتك</strong> <span class="small muted">(الشعبة ${esc(d.section)})</span><div class="muted">من ${num(d.n)} طالبًا دخلوا الترتيب · نقاطك ${num(m.score)}</div>
      <div class="small muted">${m.rank <= 3 ? 'أداء متميز، حافظ على انتظامك.' : 'أنت في النصف الأول من شعبتك؛ واصل التدريب المنتظم.'}</div></div></div>`;
  } else if (m.eligible) {
    mine = `<div class="rank-me"><div class="rank-big small-band">${bandText[m.band]}</div>
      <div><strong>أنت في ${bandText[m.band]} من شعبتك</strong><div class="muted">نقاطك ${num(m.score)}${m.pointsToMedian ? ` · تحتاج ${num(m.pointsToMedian)} نقطة لتبلغ منتصف الترتيب` : ''}</div>
      <div class="small muted">كل يوم تدريب جاد يضيف ${r.dayBonus} نقاط، وتصحيح أخطائك السابقة يضيف نقطة لكل سؤال. تقدّمك مستمر، واصل.</div></div></div>`;
  } else {
    mine = `<div><strong>لم تدخل الترتيب بعد</strong>
      <p class="muted">أكمل هذه الشروط الثلاثة لتظهر في الترتيب:</p>
      ${chk([
        [m.valid >= r.minValid ? 'ok' : 'no', `${num(r.minValid)} إجابة محتسبة`, 'المحتسبة: ما أجبت عنه بتأنٍّ، أي بعد قراءة السؤال.', meter(m.valid, r.minValid, `${num(Math.min(m.valid, r.minValid))} من ${num(r.minValid)} إجابة`)],
        [m.activeDays >= r.minDays ? 'ok' : 'no', `${num(r.minDays)} أيام تدريب مختلفة`, 'الانتظام أهم من التدريب الكثيف في يوم واحد.', meter(m.activeDays, r.minDays, `${num(Math.min(m.activeDays, r.minDays))} من ${num(r.minDays)} أيام`)],
        [m.fast ? 'bad' : 'ok', 'إجاباتك غير متسرّعة', `ألا تزيد الإجابات الأسرع من ${num(r.rushSecs)} ثوانٍ على ${num(r.rushMaxPct)}% من إجاباتك.`]])}
      ${m.fast ? `<p class="notice warn small">بعض إجاباتك أسرع من ${num(r.rushSecs)} ثوانٍ ولا تُحتسب. اقرأ السؤال ثم الإجابة ثم التفسير، ففهم الخطأ أهم من السرعة.</p>` : ''}
      <p class="st-enc">أنت في الطريق. كل جلسة جادة تقرّبك من الترتيب.</p></div>`;
  }
  $app.innerHTML = `${hero}
    <div class="grid2">
      <section class="card">${ttl('trophy', 'ترتيبك')}${mine}</section>
      <section class="card">${ttl('trophy', 'أفضل 5 في شعبتك')}
        ${d.top.length ? `<ol class="rank-top">${d.top.map(t => `<li class="${t.me ? 'me' : ''}"><span class="rank-medal" aria-hidden="true">${MEDALS[t.rank - 1] || t.rank}</span>
          <span class="rank-name">${esc(t.name)}${t.elite ? ELITE_BADGE : ''}${t.me ? ' <span class="badge brand">أنت</span>' : ''}</span><span class="ltr small muted">${num(t.score)}</span></li>`).join('')}</ol>`
          : '<div class="empty">لم يدخل أحد الترتيب بعد؛ كن أول من يدخله بتدريب جاد ومنتظم.</div>'}
        <p class="small muted">يظهر لزملاء شعبتك اسمك ونقاطك إن دخلت أفضل 5.</p>
      </section>
    </div>
    ${eliteCard(m, r)}
    <section class="card">${ttl('spark', 'كيف تُحسب نقاطي؟')}
      <ul class="rank-rules earn">
        <li><span class="earn-v">+1 / −½</span><span><b>الصافي:</b> +1 لكل إجابة صحيحة، ويُخصم لكل خاطئة ½ في السؤال ذي البدائل الثلاثة و⅓ في ذي الأربعة (أول محاولة لكل سؤال). التخمين العشوائي يعطي صفرًا في المتوسط.</span></li>
        <li><span class="earn-v">×1.1 / ×1.2</span><span><b>مستوى السؤال:</b> الصافي يُضرب في 1.1 لأسئلة التطبيق وفي 1.2 لأسئلة التفكير العليا، مكافأةً للجهد الأكبر؛ والأساسي ×1.</span></li>
        <li><span class="earn-v off">⏱</span><span><b>الإجابات السريعة:</b> الأسرع من ${num(r.rushSecs)} ثوانٍ لا تُحتسب.</span></li>
        <li><span class="earn-v off">${num(r.dailyCap)}</span><span><b>سقف يومي:</b> تُحتسب أول ${num(r.dailyCap)} إجابة صالحة في اليوم، فالانتظام أفضل من التدريب الكثيف يومًا واحدًا.</span></li>
        <li><span class="earn-v">+${num(r.dayBonus)}</span><span><b>يوم تدريب جاد:</b> ${num(r.dayMin)} إجابات صالحة فأكثر بصحة ${num(r.dayAcc)}% فأكثر (حتى ${num(r.dayCap)} يومًا).</span></li>
        <li><span class="earn-v">+½ / −½</span><span><b>السؤال المكرر:</b> إن ظهر لك سؤال أجبت عنه من قبل، تُحتسب محاولتك الثانية فيه +½ للصحيحة و−½ للخاطئة، وما بعدها لا يُحتسب. والأسئلة التي لم تُجب عنها تظهر لك أولًا.</span></li>
        <li><span class="earn-v">+${num(r.weekBonus)}</span><span><b>المحافظة على التميّز:</b> كل أسبوع (من الأحد) تجيب فيه ${num(r.weekValid)} إجابة محتسبة في ${num(r.weekDays)} أيام على الأقل وبصحة فوق ${num(r.guessFloor ?? 30)}%.</span></li>
        <li><span class="earn-v">+${num(r.eliteReward)}</span><span><b>النخبة:</b> من حلّ ${num(r.elitePct)}% من أسئلة المقرر يُكافأ بـ ${num(r.eliteReward)} نقطة عن كل ${num(r.eliteBlock)} إجابة مراجعة محتسبة بصحة ${num(r.eliteAcc)}% فأكثر (سؤال مضى على آخر محاولة فيه ${num(r.eliteGapDays)} أيام، وحتى ${num(r.eliteDailyCap)} في اليوم).</span></li>
        <li><span class="earn-v off">↺</span><span>تبدأ النقاط من الصفر مع كل فصل دراسي جديد، وعند انتقالك إلى صف آخر.</span></li>
      </ul>
    </section>`;
}


// ---------- الرصيد: استبدال نقاط التميّز بدرجات ----------
const BADGES = [[1, 'برونزي', 'أول درجة تكسبها بتدريبك', 'bronze'], [3, 'فضي', '3 درجات من تدريب جاد', 'silver'], [6, 'ذهبي', '6 درجات: مثابرة تستحق التقدير', 'gilt']];
const BLOCK_TEXT = {
  disabled: d => `الاستبدال متوقف مؤقتًا${d.settings.reason ? `: ${d.settings.reason}` : ''}.`,
  watch: () => 'تدريبك يحتاج متابعة: تأنَّ في قراءة السؤال ثم الإجابة، ويعود الاستبدال حين يتحسن تدريبك.',
  weeklyCap: d => `بلغت سقف الاستبدال لهذا الأسبوع (${num(d.settings.weeklyCap)} درجات). يتجدد السقف يوم الأحد.`,
};
const RING = 2 * Math.PI * 52;
const ring = (frac, inner, label = 'تقدمك نحو الدرجة القادمة') => `<div class="bal-ring" role="img" aria-label="${label}"><svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="52" class="bal-track"/>
  <circle cx="60" cy="60" r="52" class="bal-fill" style="stroke-dasharray:${RING.toFixed(1)};stroke-dashoffset:${(RING * (1 - Math.min(1, Math.max(0, frac)))).toFixed(1)}"/></svg><div class="bal-ring-in">${inner}</div></div>`;

function celebrate(title, text, opt = {}) {
  const esc = t => String(t ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  const o = document.createElement('div');
  o.className = 'bal-cele' + (opt.cls ? ' ' + opt.cls : '');
  o.setAttribute('role', opt.dialog ? 'dialog' : 'status');
  if (opt.dialog) { o.setAttribute('aria-modal', 'true'); o.setAttribute('aria-label', title); }
  o.innerHTML = `<div class="bal-cele-card"><div class="bal-coin" aria-hidden="true">${icon(opt.icon || 'coin', 84, opt.tone)}</div>
    <h2>${esc(title)}</h2><p class="muted">${esc(text)}</p>${opt.extra || ''}
    <button type="button" class="primary">${esc(opt.btn || 'رائع')}</button></div>${'<i></i>'.repeat(opt.confetti || 14)}`;
  document.body.append(o);
  const close = () => { o.remove(); opt.onClose?.(); };
  o.querySelector('button').onclick = close;
  if (opt.dialog) o.querySelector('button').focus();
  o.addEventListener('click', e => { if (e.target === o) close(); });
  if (!opt.dialog) setTimeout(close, 6000);
}

// تهنئة دخول «النخبة»: مرة واحدة (تُسجَّل في الحساب فلا تتكرر على جهاز آخر)
let eliteShown = false;
function eliteCelebrate(ctx, d) {
  if (eliteShown || !d?.available || !d.me?.eliteNew) return;
  eliteShown = true;
  const r = d.rules;
  celebrate('مبروك! دخلت مستوى النخبة', `حللت ${num(r.elitePct)}% من أسئلة المقرر، وهذا إنجاز لا يبلغه إلا المثابرون. من الآن كل ${num(r.eliteBlock)} إجابة مراجعة متقنة تضيف لك ${num(r.eliteReward)} نقطة.`, {
    cls: 'elite-cele', icon: 'trophy', tone: 'gilt', btn: 'انطلق', dialog: true,
    extra: `<div class="elite-cele-badge">النخبة</div><p class="small">راجع الأسئلة التي حللتها قبل أسبوع فأكثر، بتأنٍّ وصحة ${num(r.eliteAcc)}% فأكثر.</p>`,
    onClose: () => { homeCache.delete('/student/rank'); ctx.api('/student/elite-seen', { method: 'POST' }).catch(() => {}); } });
}

export async function pageStudentBalance(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const d = await api('/student/balance');
  const hero = `<section class="hero"><div class="hero-ic">${icon('coin', 52)}<div><h1>الرصيد</h1>
    <p class="muted">حوّل نقاط تدريبك إلى درجات: كل ${num(d.settings?.rate || 50)} نقطة تكسبها بتدريب جاد تُستبدل بدرجة تضاف إلى رصيدك ويرصدها لك معلمك.</p></div></div></section>`;
  if (!d.available) { $app.innerHTML = `${hero}<section class="card"><div class="empty">لم يُسند لك مقرر جاهز بعد.</div></section>`; return; }
  const rate = d.settings.rate, inRing = d.points - d.ready * rate;
  const maxNow = Math.min(d.ready, d.weekLeft, 10);
  const total = d.pending + d.recorded;
  const why = d.blocked === 'insufficient' ? `تحتاج ${num(Math.max(0.1, d.toNext))} نقطة أخرى لتبلغ ${num(rate)} نقطة.` : (BLOCK_TEXT[d.blocked]?.(d) || '');
  const nextBadge = BADGES.find(([n]) => total < n);
  const buy = [1, ...(maxNow > 1 ? [maxNow] : [])];
  const status = { pending: ['بانتظار رصد المعلم', 'warn'], recorded: ['تم رصدها', 'ok'], cancelled: ['أُلغيت وعادت النقاط', ''] };
  $app.innerHTML = `${hero}
    <div class="grid2">
      <section class="card bal-main">${ttl('coin', 'رصيد نقاطك')}
        <div class="bal-top">${ring(maxNow ? 1 : inRing / rate, `<b>${num(d.points)}</b><span class="small muted">نقطة متاحة</span>`)}
          <div class="bal-info">
            ${maxNow ? `<p class="bal-ready"><b>${num(maxNow)}</b> ${maxNow === 1 ? 'درجة جاهزة' : 'درجات جاهزة'} للاستبدال</p>
              <div class="actions">${buy.map(k => `<button type="button" class="primary" data-redeem="${k}">استبدل ${num(k * rate)} نقطة بـ ${k === 1 ? 'درجة' : num(k) + ' درجات'}</button>`).join('')}</div>`
            : `<p class="bal-ready">${d.blocked === 'insufficient' ? `باقي <b>${num(Math.max(0.1, d.toNext))}</b> نقطة على درجتك القادمة` : 'نقاطك تتجمع باستمرار'}</p>
              <div class="bar"><span style="width:${Math.round(100 * Math.min(1, inRing / rate))}%"></span></div>`}
            <p class="small muted">نقاطك في قائمة التميّز ${num(d.score)}؛ ما تستبدله لا ينقص ترتيبك.${d.bonus ? ` ومعها ${num(d.bonus)} نقطة من كوبونات المكافأة (لا تدخل الترتيب).` : ''}</p>
          </div></div>
        <div class="bal-cond"><h3>شروط الاستبدال</h3>
          ${chk([
            [d.ready >= 1 ? 'ok' : 'no', `${num(rate)} نقطة متاحة على الأقل`, '', meter(Math.min(d.points, rate), rate, `${num(Math.min(d.points, rate))} من ${num(rate)} نقطة`)],
            [d.blocked === 'watch' ? 'bad' : 'ok', 'تدريبك لا «يحتاج متابعة»', 'الإجابات السريعة جدًا أو القريبة من التخمين توقف الاستبدال مؤقتًا.'],
            [d.weekLeft > 0 ? 'ok' : 'bad', 'لم تبلغ سقف الأسبوع', `استبدلت ${num(d.weekUsed)} من ${num(d.settings.weeklyCap)} درجات هذا الأسبوع، ويتجدد السقف يوم الأحد.`],
            d.blocked === 'disabled' ? ['bad', 'الاستبدال متاح الآن', d.settings.reason || 'متوقف مؤقتًا من الإدارة.'] : null])}
          ${maxNow ? '<p class="bal-why ok"><b>كل الشروط متحققة.</b> يمكنك الاستبدال الآن.</p>'
            : `<div class="bal-why" role="note"><h4>لماذا لا أستطيع الاستبدال الآن؟</h4><p>${esc(why)}</p></div>`}
        </div>
      </section>
      <section class="card">${ttl('spark', 'مهمتك اليوم')}
        ${d.today.done ? `<p class="bal-mission ok"><b>أنجزتها!</b> أجبت ${num(d.today.valid)} سؤالًا بتأنٍّ وصحتك ${num(pct(d.today.correct, d.today.valid))}%؛ كسبت +3 نقاط ليوم تدريب جاد.</p>`
          : `<p class="bal-mission">أجب ${num(10)} أسئلة بتأنٍّ وبصحة ${num(50)}% فأكثر تكسب +3 نقاط إضافية.</p>
             ${chk([
               [d.today.valid >= 10 ? 'ok' : 'no', '10 إجابات محتسبة اليوم', '', meter(d.today.valid, 10, `${num(Math.min(d.today.valid, 10))} من ${num(10)} إجابات`)],
               [d.today.valid && 2 * d.today.correct >= d.today.valid ? 'ok' : (d.today.valid >= 10 ? 'bad' : 'no'), 'صحة 50% فأكثر', d.today.valid >= 10 && 2 * d.today.correct < d.today.valid ? 'أتممت العدد لكن الصحة أقل من 50%؛ راجع تفسير الأخطاء وأجب عن أسئلة إضافية.' : (d.today.valid ? `صحتك الآن ${num(pct(d.today.correct, d.today.valid))}%.` : 'تُحسب بعد أن تبدأ الإجابة.')]])}
             <a class="btn primary" href="#/">ابدأ التدريب</a>`}
        <div class="bal-week ${d.week.kept ? 'ok' : ''}"><b>${d.week.kept ? '✅ حافظت على تميّزك هذا الأسبوع (+2 نقطة)' : '⭐ حافظ على تميّزك هذا الأسبوع تكسب +2 نقطة'}</b>
          ${chk([
            [d.week.valid >= 30 ? 'ok' : 'no', '30 إجابة محتسبة هذا الأسبوع', '', meter(d.week.valid, 30, `${num(Math.min(d.week.valid, 30))} من 30 إجابة`)],
            [d.week.days >= 3 ? 'ok' : 'no', 'في 3 أيام تدريب مختلفة', '', meter(d.week.days, 3, `${num(Math.min(d.week.days, 3))} من 3 أيام`)],
            [d.week.valid === 0 ? 'no' : d.week.accuracy > (d.week.floor ?? 30) ? 'ok' : 'bad', `صحة فوق ${num(d.week.floor ?? 30)}%`, d.week.valid ? `صحتك هذا الأسبوع ${num(d.week.accuracy)}%${d.week.accuracy > (d.week.floor ?? 30) ? '' : '؛ تأنَّ واقرأ التفسير لترفعها'}. الأسبوع يبدأ من الأحد.` : 'تُحسب بعد أن تبدأ الإجابة. الأسبوع يبدأ من الأحد.']])}
          ${d.weeksKept ? `<span class="small muted">أسابيع التميّز التي حافظت عليها: ${num(d.weeksKept)}</span>` : ''}</div>
        <div class="bal-stats">
          <div><b>${d.streak ? '🔥 ' : ''}${num(d.streak)}</b><span class="small muted">أيام جادة متتالية</span></div>
          <div><b>${num(d.weekUsed)}/${num(d.settings.weeklyCap)}</b><span class="small muted">درجات هذا الأسبوع</span></div>
        </div>
      </section>
    </div>
    <section class="card bal-coupon">${ttl('spark', 'لديك كود مكافأة؟')}
      <p class="small muted">يعطيك معلمك كودًا مكافأةً على تميّزك، فتزيد نقاطك المتاحة للاستبدال. الكود يُستخدم مرة واحدة ولا يدخل في نقاط الترتيب.</p>
      <div class="bal-coupon-row"><input id="cp-code" class="ltr" dir="ltr" maxlength="12" autocomplete="off" placeholder="XXXX-XXXX" aria-label="كود المكافأة">
        <button type="button" class="primary" id="cp-go">تفعيل الكود</button></div>
      <p class="notice bad small" id="cp-err" hidden></p>
    </section>
    <section class="card">${ttl('trophy', 'درجاتك')}
      <div class="bal-grades">
        <div class="bal-gbox"><b>${num(d.pending)}</b><span class="small muted">بانتظار رصد المعلم</span></div>
        <div class="bal-gbox ok"><b>${num(d.recorded)}</b><span class="small muted">تم رصدها</span></div>
      </div>
      ${nextBadge ? `<p class="small muted bal-next">باقي ${num(nextBadge[0] - total)} ${nextBadge[0] - total === 1 ? 'درجة' : 'درجات'} للوسام ال${nextBadge[1]}.</p>` : '<p class="small muted bal-next">حصلت على كل الأوسمة، مثابرة رائعة!</p>'}
      <ul class="bal-badges">${BADGES.map(([n, t, tip, tone]) => `<li class="${total >= n ? 'on' : ''}"><span aria-hidden="true">${total >= n ? icon('medal', 44, tone) : icon('lock', 44, 'navy')}</span><b>${t}</b><span class="small muted">${tip}</span></li>`).join('')}</ul>
    </section>
    <section class="card">${ttl('history', 'سجل الاستبدال')}
      ${d.history.length ? `<div class="table-wrap"><table class="list"><thead><tr><th>التاريخ</th><th>الدرجات</th><th>النقاط</th><th>الحالة</th></tr></thead><tbody>
        ${d.history.map(h => { const [t, k] = status[h.status] || ['—', '']; return `<tr><td class="small">${esc(hijri(h.at, true))}</td><td>${num(h.grades)}</td><td>${num(h.points)}</td>
          <td><span class="badge ${k}">${t}</span>${h.status === 'cancelled' && h.reason ? ` <span class="small muted">${esc(h.reason)}</span>` : ''}</td></tr>`; }).join('')}
      </tbody></table></div>` : '<div class="empty">لم تستبدل نقاطًا بعد. حين تبلغ ' + num(rate) + ' نقطة تظهر لك درجتك الأولى هنا.</div>'}
    </section>
    <section class="card">${ttl('spark', 'كيف يعمل الرصيد؟')}
      <ul class="rank-rules">
        <li>كل <b>${num(rate)}</b> نقطة من نقاط التميّز تُستبدل بدرجة تُضاف إلى رصيدك، ويرصدها لك معلمك.</li>
        <li>تُخصم النقاط المستبدلة من «نقاطك المتاحة» فقط، وترتيبك في التميّز لا ينقص. ولا يُشترط دخول قائمة التميّز.</li>
        <li>للمعلم أن يُلغي استبدالًا لم يرصده بسبب مكتوب، وتعود نقاطك إليك.</li>
        <li>مع بدء فصل دراسي جديد تبدأ النقاط من الصفر، أما الدرجات التي استبدلتها فتبقى لك.</li>
      </ul></section>`;
  const cpGo = document.getElementById('cp-go'), cpErr = document.getElementById('cp-err'), cpIn = document.getElementById('cp-code');
  const useCoupon = async () => {
    if (cpIn.value.trim().length < 8) { cpErr.textContent = 'اكتب الكود كاملًا (8 خانات)'; cpErr.hidden = false; return; }
    cpGo.disabled = true; cpErr.hidden = true;
    try {
      const r = await api('/student/coupon', { method: 'POST', body: { code: cpIn.value } });
      if (!r.ok) { cpErr.textContent = r.error; cpErr.hidden = false; cpGo.disabled = false; return; }
      homeCache.clear();
      celebrate(`حصلت على ${num(r.points)} نقطة مكافأة!`, `${r.note ? r.note + ' · ' : ''}أصبحت نقاطك المتاحة ${num(r.balance.points)}.`);
      pageStudentBalance(ctx).catch(fail);
    } catch (e) { cpGo.disabled = false; fail(e); }
  };
  cpGo.onclick = useCoupon;
  cpIn.onkeydown = e => { if (e.key === 'Enter') useCoupon(); };
  $app.querySelectorAll('[data-redeem]').forEach(b => b.onclick = () => {
    const k = Number(b.dataset.redeem), cost = k * rate;
    const dlg = document.createElement('dialog');
    dlg.className = 'bal-dlg';
    dlg.innerHTML = `<form method="dialog"><h2>تأكيد الاستبدال</h2>
      <p>ستستبدل <b>${num(cost)}</b> نقطة بـ <b>${k === 1 ? 'درجة واحدة' : num(k) + ' درجات'}</b>، ويبقى لك <b>${num(Math.round((d.points - cost) * 10) / 10)}</b> نقطة.</p>
      <p class="small muted">تُخصم النقاط فورًا ويرصد المعلم الدرجة، وله أن يُلغيها بسبب فتعود نقاطك.</p>
      <div class="actions"><button class="primary" value="ok">استبدل الآن</button><button value="no">إلغاء</button></div></form>`;
    document.body.append(dlg);
    dlg.addEventListener('close', async () => {
      const ok = dlg.returnValue === 'ok'; dlg.remove();
      if (!ok) return;
      try {
        const r = await api('/student/redeem', { method: 'POST', body: { grades: k } });
        homeCache.clear();
        celebrate(`مبروك! أضفت ${k === 1 ? 'درجة' : num(k) + ' درجات'} إلى رصيدك`, `سيرصدها لك معلمك. بقي لك ${num(r.points)} نقطة، فواصل التدريب لتكسب الدرجة القادمة.`);
        pageStudentBalance(ctx).catch(fail);
      } catch (e) { fail(e); }
    });
    dlg.showModal();
  });
}

// ---------- رسائل معلمي: رسائل ومهام المعلم ----------
export async function pageStudentInbox(ctx) {
  const { esc, $app, api, fail, toast } = ctx;
  const d = await api('/student/inbox');
  api('/student/comms/read', { method: 'POST', keep: true }).then(() => homeCache.clear()).catch(() => {});
  const days = at => Math.ceil((new Date(at) - Date.now()) / 86400000);
  const TS = { open: ['جارية', 'warn'], done: ['أنجزتها ✓', 'ok'], missed: ['انتهى الموعد', ''] };
  const card = it => {
    const t = it.task;
    let inner;
    if (it.survey) {
      inner = `<p class="in-body">${esc(it.body || 'استبانة قصيرة عن تجربتك في المنصة (نحو 3 دقائق). إجاباتك سرية ولا تؤثر على درجاتك أو نقاطك.')}</p>
        <div class="actions">${it.survey.done ? '<span class="badge ok">أرسلت إجابتك، شكرًا لك</span>'
          : `<button type="button" class="primary" data-survey="${it.id}">ابدأ الاستبانة</button><span class="small muted">تُغلق ${esc(hijri(it.survey.closesAt))}</span>`}</div>`;
    } else if (t) {
      const acc = t.valid ? Math.round(100 * t.correct / t.valid) : 0, left = Math.max(0, t.n - t.valid), [st, k] = TS[t.status] || ['—', ''];
      inner = `<div class="in-task"><div class="small">الدرس: <b>${esc(t.lesson || '')}</b></div>
        <div class="small">المطلوب: ${num(t.n)} سؤالًا${t.minAccuracy ? ` بصحة ${num(t.minAccuracy)}% فأكثر` : ''}</div>
        ${t.reward ? `<div class="small in-reward ${t.rewardGot ? 'got' : ''}">${t.rewardGot ? `🎁 حصلت على ${num(t.rewardGot)} نقطة مكافأة، وهي في رصيدك` : t.status === 'missed' ? `كانت المكافأة ${num(t.reward)} نقطة لمن ينجز قبل الموعد` : `🎁 مكافأة ${num(t.reward)} نقطة لمن ينجزها قبل الموعد`}</div>` : ''}
        <div class="bar ${t.status === 'done' ? 'ok' : ''}"><span style="width:${Math.min(100, Math.round(100 * t.valid / t.n))}%"></span></div>
        <div class="small muted">${t.status === 'done' ? `أنجزت ${num(t.valid)} سؤالًا بصحة ${num(acc)}%` : t.status === 'missed' ? `أجبت ${num(t.valid)} من ${num(t.n)}${t.valid ? ` بصحة ${num(acc)}%` : ''}. ما زال بإمكانك التدرّب على الدرس.`
          : `أجبت ${num(t.valid)} من ${num(t.n)}${t.valid ? ` · صحتك ${num(acc)}%` : ''} · باقي ${num(left)} سؤالًا · ${days(t.dueAt) > 0 ? `باقي ${num(days(t.dueAt))} ${days(t.dueAt) === 1 ? 'يوم' : 'أيام'}` : 'ينتهي اليوم'} (${esc(hijri(t.dueAt))})`}</div>
        <span class="badge ${k}">${st}</span>
        ${t.status !== 'done' ? `<button type="button" class="primary" data-go="${t.lessonId}">ابدأ التدريب على الدرس</button>` : ''}</div>`;
    } else inner = `<p class="in-body">${esc(it.body || '')}</p>
      <div class="actions in-reply">${it.reply ? `<span class="badge ${it.reply === 2 ? 'warn' : 'ok'}">${it.reply === 2 ? 'أخبرت معلمك أنك تحتاج مساعدة' : 'أخبرت معلمك أنك فهمت'}</span>`
        : `<button type="button" data-reply="1:${it.id}">فهمت</button><button type="button" data-reply="2:${it.id}">أحتاج مساعدة</button>`}</div>`;
    return `<li class="in-item ${it.read ? '' : 'new'} ${it.task || it.survey ? 'is-task' : ''}"><div class="in-head"><b>${esc(it.title)}</b>${it.read ? '' : ' <span class="badge brand">جديدة</span>'}
      <span class="small muted">${esc(it.sender || 'معلمك')} · ${esc(hijri(it.createdAt))}</span></div>${inner}</li>`;
  };
  $app.innerHTML = `<section class="hero"><div class="hero-ic">${icon('mail', 52)}<div><h1>رسائل معلمي</h1>
    <p class="muted">رسائل معلمك ومهامه واستباناته لك. المهام تُحتسب تلقائيًا من تدريبك، فلا تحتاج لتسليم شيء.</p></div></div></section>
    <section class="card">${d.items.length ? `<ul class="in-list">${d.items.map(card).join('')}</ul>` : '<div class="empty">لا توجد رسائل أو مهام الآن. حين يرسل لك معلمك شيئًا يظهر هنا.</div>'}</section>`;
  $app.querySelectorAll('[data-go]').forEach(b => b.onclick = () => { savePrefs({ ...loadPrefs(), lessons: [Number(b.dataset.go)] }); location.hash = '#/'; });
  $app.querySelectorAll('[data-survey]').forEach(b => b.onclick = () => {
    const it = d.items.find(x => String(x.id) === b.dataset.survey);
    surveyForm(ctx, it, () => pageStudentInbox(ctx).catch(fail));
  });
  $app.querySelectorAll('[data-reply]').forEach(b => b.onclick = async () => {
    const [code, id] = b.dataset.reply.split(':').map(Number);
    b.disabled = true;
    try { await api('/student/comms/reply', { method: 'POST', body: { id, code } }); toast(code === 2 ? 'وصل طلبك لمعلمك' : 'وصل ردّك'); pageStudentInbox(ctx).catch(fail); }
    catch (e) { b.disabled = false; fail(e); }
  });
}

export const resetStudentSession = () => { stopTimer(); session = null; homeCache.clear(); };
