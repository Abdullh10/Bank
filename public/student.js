// واجهة الطالب: تدريب فقط. السؤال يُعرض دون إجابته، والتصحيح والتفسير يأتيان من قاعدة البيانات بعد الإجابة عن كل سؤال.
// التصميم مبني على توصيات الوكيل التربوي: جلسات قصيرة (10 أسئلة افتراضيًا)، مستويات بثلاث مجموعات، تدرّج من السهل،
// تغذية راجعة فورية تبدأ بسبب خطأ البديل المختار، ومؤقت اختياري لا يقفل الجلسة، ثم «أعد الأخطاء» بأسئلة من الهدف نفسه.

const LETTERS = ['أ', 'ب', 'ج'];
const GROUPS = { basic: 'أساسي (تذكر وفهم)', apply: 'تطبيق', higher: 'تفكير عليا' };
const LEVEL_CHOICES = [['graded', 'متدرّج (مستحسن)'], ['basic', GROUPS.basic], ['apply', GROUPS.apply], ['higher', GROUPS.higher]];
const PREFS_KEY = 'itqan.student.prefs.v1';
const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
const loadPrefs = () => { try { return JSON.parse(localStorage.getItem(PREFS_KEY)) || {}; } catch { return {}; } };
const savePrefs = p => { try { localStorage.setItem(PREFS_KEY, JSON.stringify(p)); } catch { /* التخزين غير متاح */ } };
const shuffle = a => { const r = [...a]; for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [r[i], r[j]] = [r[j], r[i]]; } return r; };
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
    <img class="login-logo" src="assets/itqan-logo.png" alt="إتقان" width="520" height="513">
    <h1>مرحبًا بك في إتقان</h1>
    <p class="muted small">تأكد من اسمك وشعبتك. تُثبَّت مرة واحدة، ويعدّلها المشرف فقط.</p>
    <form id="c-form" novalidate>
      <div class="field"><label for="c-name">الاسم</label><input id="c-name" value="${esc(state.user.displayName)}" required></div>
      <div class="field"><label for="c-sec">الشعبة</label><input id="c-sec" value="${esc(state.user.section || '')}" placeholder="مثال: 2/1" required></div>
      <button class="primary" type="submit">تأكيد والبدء</button>
    </form>
    <p class="login-foot">التدريب لا يدخل في الدرجات، ويرى معلمك تقدّمك فيه.</p>
  </div></div>`;
  document.getElementById('c-form').onsubmit = async e => {
    e.preventDefault();
    try {
      const name = document.getElementById('c-name').value.trim(), section = document.getElementById('c-sec').value.trim();
      await api('/student/confirm', { method: 'POST', body: { name, section } });
      Object.assign(state.user, { displayName: name, section, profileConfirmed: true });
      toast('تم تثبيت بياناتك'); ctx.done();
    } catch (err) { fail(err); }
  };
}

export async function pageStudentHome(ctx) {
  const { state, esc, $app, api, fail } = ctx;
  if (session && !session.summary) return renderQuestion(ctx); // جلسة جارية
  const catalog = await api('/student/catalog');
  const prefs = { count: 10, levels: 'graded', timed: false, lessons: [], ...loadPrefs() };
  const chosen = new Set(prefs.lessons);
  $app.innerHTML = `
    <section class="hero"><div><h1>تدرّب يا ${esc(state.user.displayName.split(' ')[0])}</h1>
      <p class="muted">اختر الدروس وعدد الأسئلة والمستوى. التصحيح والتفسير يظهران بعد كل سؤال.</p></div></section>
    <div class="grid2 st-setup">
      <section class="card"><h2>الدروس</h2>
        ${catalog.map(c => `<details class="st-ch" ${c.lessons.some(l => chosen.has(l.id)) ? 'open' : ''}>
          <summary><b>الفصل ${c.number}:</b> ${esc(c.title)}</summary>
          ${c.lessons.map(l => {
            const n = l.basic + l.apply + l.higher;
            return `<label class="st-lesson"><input type="checkbox" data-lesson="${l.id}" ${chosen.has(l.id) ? 'checked' : ''} ${n ? '' : 'disabled'}>
              <span>${esc(l.title)}</span>
              ${l.answered ? `<span class="st-mastery" title="نسبة إجاباتك الصحيحة في هذا الدرس"><span style="width:${pct(l.correct, l.answered)}%"></span></span><small>${pct(l.correct, l.answered)}%</small>` : '<small class="muted">لم تبدأ</small>'}
            </label>`;
          }).join('')}
        </details>`).join('')}
      </section>
      <section class="card"><h2>إعداد الجلسة</h2>
        <div class="field"><label for="s-count">عدد الأسئلة</label>
          <select id="s-count">${[5, 10, 15, 20].map(n => `<option ${n === prefs.count ? 'selected' : ''}>${n}</option>`).join('')}</select></div>
        <fieldset class="field"><legend>المستوى</legend>
          ${LEVEL_CHOICES.map(([v, t]) => `<label class="st-radio"><input type="radio" name="s-level" value="${v}" ${v === prefs.levels ? 'checked' : ''}> ${t}</label>`).join('')}
          <p class="small muted">«متدرّج»: أسئلة أساسية ثم تطبيق ثم تفكير عليا، من الأسهل إلى الأصعب.</p></fieldset>
        <label class="st-radio"><input type="checkbox" id="s-timed" ${prefs.timed ? 'checked' : ''}> مؤقت للجلسة <span class="small muted">(اختياري: دقيقة لسؤال التذكر والفهم، ونحو دقيقتين لغيره، ولا تُقفل الجلسة بانتهائه)</span></label>
        <button class="primary st-start" id="s-start" type="button">ابدأ التدريب</button>
        <p class="small muted">الأسئلة والبدائل تُخلط في كل جلسة.</p>
      </section>
    </div>`;
  document.getElementById('s-start').onclick = async () => {
    const lessons = [...$app.querySelectorAll('[data-lesson]:checked')].map(i => Number(i.dataset.lesson));
    const p = { lessons, count: Number(document.getElementById('s-count').value),
      levels: $app.querySelector('[name="s-level"]:checked').value, timed: document.getElementById('s-timed').checked };
    if (!lessons.length) return fail(new Error('اختر درسًا واحدًا على الأقل'));
    savePrefs(p);
    await startSession(ctx, p);
  };
}

async function startSession(ctx, p) {
  const { api, fail } = ctx;
  const btn = document.getElementById('s-start');
  if (btn) { btn.disabled = true; btn.textContent = 'جارٍ التحضير…'; }
  try {
    const s = await api('/student/start', { method: 'POST', body: p });
    session = { ...s, idx: 0, answers: {}, order: Object.fromEntries(s.questions.map(q => [q.id, shuffle([0, 1, 2])])), startedAt: Date.now(), summary: null };
    location.hash = '#/';
    renderQuestion(ctx);
  } catch (e) { fail(e); if (btn) { btn.disabled = false; btn.textContent = 'ابدأ التدريب'; } }
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
      <span>${session.retry ? 'إعادة الأخطاء · ' : ''}سؤال ${session.idx + 1} من ${session.questions.length}</span>
      ${session.timeLimit ? '<span class="st-timer" id="st-timer" aria-live="off"></span>' : ''}
      <button type="button" id="st-end">إنهاء الجلسة</button>
    </div>
    <div class="bar"><span style="width:${pct(answeredCount, session.questions.length)}%"></span></div>
    <article class="card st-q">
      <div class="small muted">${esc(q.lesson)} · ${GROUPS[q.group]}</div>
      <p class="st-stem">${esc(q.stem)}</p>
      ${q.stimulus ? `<div class="table-wrap"><table class="data-table"><thead><tr>${q.stimulus.headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead>
        <tbody>${q.stimulus.rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>` : ''}
      <div class="st-opts" role="radiogroup">
        ${order.map((orig, pos) => {
          let cls = '';
          if (res) cls = orig === res.correctIndex ? 'ok' : orig === res.choice ? 'bad' : 'dim';
          return `<button type="button" class="opt st-opt ${cls}" data-orig="${orig}" ${res ? 'disabled' : ''} role="radio" aria-checked="${res && orig === res.choice}">
            <span class="letter">${LETTERS[pos]}</span><span>${esc(q.options[orig])}</span></button>`;
        }).join('')}
      </div>
      ${res ? feedback(res, q, order, esc) : ''}
    </article>
    <div class="actions st-nav">
      ${session.idx > 0 ? '<button type="button" id="st-prev">السابق</button>' : ''}
      ${res ? `<button type="button" class="primary" id="st-next">${last ? 'عرض النتيجة' : 'التالي'}</button>` : ''}
    </div>
  </div>`;
  if (session.timeLimit) tickTimer();
  $app.querySelectorAll('.st-opt:not([disabled])').forEach(b => b.onclick = async () => {
    $app.querySelectorAll('.st-opt').forEach(x => { x.disabled = true; });
    b.classList.add('chosen');
    try {
      const r = await api('/student/answer', { method: 'POST', body: { session: session.id, question: q.id, choice: Number(b.dataset.orig) } });
      session.answers[q.id] = { ...r, choice: Number(b.dataset.orig) };
      renderQuestion(ctx);
    } catch (e) { fail(e); renderQuestion(ctx); }
  });
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
  const otherWrong = [0, 1, 2].filter(o => o !== res.correctIndex && o !== res.choice && notes[o]);
  return `<div class="notice ${res.correct ? 'ok' : 'bad'} st-fb" role="status">
    <strong>${res.correct ? 'إجابة صحيحة ✓' : `إجابة غير صحيحة. الصحيح: (${pos(res.correctIndex)})`}</strong>
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

async function finishSession(ctx) {
  const { api, fail } = ctx;
  stopTimer();
  try {
    session.summary = await api('/student/finish', { method: 'POST', body: { session: session.id } });
    renderSummary(ctx);
  } catch (e) { fail(e); }
}

function renderSummary(ctx) {
  const { esc, $app } = ctx;
  const s = session.summary;
  const usedSec = Math.round((Date.now() - session.startedAt) / 1000);
  $app.innerHTML = `<div class="st-run">
    <section class="card st-result">
      <h1>نتيجة الجلسة</h1>
      <div class="st-score"><b>${s.score}</b> من ${s.total} <span class="muted">(${pct(s.score, s.total)}%)</span></div>
      <p>${encouragement(s.score, s.total)}</p>
      ${session.timeLimit ? `<p class="small muted">الوقت المستغرق ${mmss(usedSec)} من ${mmss(session.timeLimit)} مقترحة.</p>` : ''}
      ${s.answered < s.total ? `<p class="small muted">أجبت عن ${s.answered} من ${s.total}.</p>` : ''}
    </section>
    <div class="grid2">
      <section class="card"><h2>حسب الدرس</h2>${table(s.byLesson.map(r => [r.lesson, r.correct, r.n]), esc)}</section>
      <section class="card"><h2>حسب المستوى</h2>${table(s.byGroup.map(r => [GROUPS[r.group], r.correct, r.n]), esc)}</section>
    </div>
    <div class="actions st-nav">
      ${s.wrong ? '<button type="button" class="primary" id="st-retry">أعد الأخطاء</button>' : ''}
      <button type="button" id="st-new">جلسة جديدة</button>
      <a class="btn" href="#/history">سجلي</a>
    </div>
  </div>`;
  const retry = document.getElementById('st-retry');
  if (retry) retry.onclick = () => startSession(ctx, { retry: s.id });
  document.getElementById('st-new').onclick = () => { session = null; ctx.done(); };
  window.scrollTo(0, 0);
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
  $app.innerHTML = `
    <section class="hero"><div><h1>سجلي</h1><p class="muted">تقدّمك في التدريب. لا يرى زملاؤك بياناتك.</p></div></section>
    <div class="grid2">
      <section class="card"><h2>تقدّمك في الدروس</h2>
        ${lessons.length ? table(lessons.map(l => [`${l.chapter}. ${l.title}`, l.correct, l.answered]), esc) : '<div class="empty">لم تبدأ التدريب بعد.</div>'}
        ${lessons.some(l => pct(l.correct, l.answered) < 70) ? '<p class="small muted">الدروس التي تقل عن 70% تستحق جلسة أخرى.</p>' : ''}
      </section>
      <section class="card"><h2>آخر الجلسات</h2>
        ${hist.length ? `<table class="list"><thead><tr><th>التاريخ</th><th>النتيجة</th><th></th></tr></thead><tbody>
          ${hist.map(h => `<tr><td class="ltr">${esc(new Date(h.createdAt).toLocaleString('ar-SA-u-nu-latn', { dateStyle: 'medium', timeStyle: 'short' }))}</td>
            <td>${h.score}/${h.total} (${pct(h.score, h.total)}%)</td>
            <td>${h.wrong ? `<button type="button" data-retry="${h.id}">أعد أخطاءها</button>` : ''}</td></tr>`).join('')}</tbody></table>`
          : '<div class="empty">لا توجد جلسات بعد.</div>'}
      </section>
    </div>`;
  $app.querySelectorAll('[data-retry]').forEach(b => b.onclick = () => startSession(ctx, { retry: Number(b.dataset.retry) }));
}

export const resetStudentSession = () => { stopTimer(); session = null; };
