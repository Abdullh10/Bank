// منشئ نماذج الاختبارات: اختيار الفصول والعدد والمستوى والنوع، ونماذج متعددة، وكليشة المدرسة، وتصدير PDF عبر الطباعة.
const LEVELS = ['تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع'];
const DIFFS = ['سهل', 'متوسط', 'صعب'];
const MODEL_NAMES = ['أ', 'ب', 'ج', 'د'];
const LETTERS = ['أ', 'ب', 'ج'];
const ORDINALS = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس'];
const STORE_KEY = 'chem21.exam.header.v1';

const DEFAULT_HEADER = {
  country: 'المملكة العربية السعودية',
  org: 'الهيئة الملكية بالجبيل',
  dept: 'إدارة التعليم العام',
  school: 'مدرسة العلا الثانوية',
  title: 'اختبار الفصل الدراسي الأول',
  year: '1447هـ',
  subject: 'الكيمياء 2-1',
  grade: 'الثاني الثانوي – مسارات',
  duration: 'ساعتان ونصف',
  date: '..../..../1447هـ',
  teacher: '',
  instructions: 'اقرأ الأسئلة بعناية، وأجب عنها جميعًا بالقلم الأزرق. لا يُسمح باستخدام المصحح السائل. يُسمح باستخدام الآلة الحاسبة غير المبرمجة.',
};

function loadHeader() {
  try { return { ...DEFAULT_HEADER, ...JSON.parse(localStorage.getItem(STORE_KEY) || '{}') }; } catch { return { ...DEFAULT_HEADER }; }
}
function saveHeader(h) { try { localStorage.setItem(STORE_KEY, JSON.stringify(h)); } catch { /* التخزين غير متاح */ } }

// مولد أرقام عشوائية بذرة ثابتة: البذرة نفسها تعيد إنتاج الاختبار نفسه.
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffle(arr, rand) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

// اختيار متوازن: يوزع العدد على الفصول بحسب حجم المتاح فيها، ويتنقل بين الأهداف حتى لا تتكدس أسئلة هدف واحد.
function pick(pool, count, rand) {
  if (count <= 0 || !pool.length) return [];
  count = Math.min(count, pool.length);
  const byCh = new Map();
  for (const q of pool) {
    if (!byCh.has(q.chapter.number)) byCh.set(q.chapter.number, new Map());
    const objs = byCh.get(q.chapter.number);
    if (!objs.has(q.objectiveCode)) objs.set(q.objectiveCode, []);
    objs.get(q.objectiveCode).push(q);
  }
  const chapters = [...byCh.keys()].sort((a, b) => a - b);
  const sizes = chapters.map(c => [...byCh.get(c).values()].reduce((s, l) => s + l.length, 0));
  const total = sizes.reduce((a, b) => a + b, 0);
  // حصص تناسبية مع تقريب بأكبر الباقي
  const raw = sizes.map(s => (s / total) * count);
  const quota = raw.map(Math.floor);
  let left = count - quota.reduce((a, b) => a + b, 0);
  raw.map((r, i) => [r - Math.floor(r), i]).sort((x, y) => y[0] - x[0]).forEach(([, i]) => { if (left > 0 && quota[i] < sizes[i]) { quota[i]++; left--; } });
  const out = [];
  chapters.forEach((c, ci) => {
    const lists = shuffle([...byCh.get(c).values()].map(l => shuffle(l, rand)), rand);
    let k = 0;
    while (out.filter(q => q.chapter.number === c).length < quota[ci] && lists.some(l => l.length)) {
      const l = lists[k % lists.length];
      if (l.length) out.push(l.shift());
      k++;
    }
  });
  return out;
}

const state = { header: loadHeader(), opts: null, exam: null };

export async function pageExam(ctx) {
  const { api, esc, fail, toast, $app } = ctx;
  const [chapters, bank] = await Promise.all([api('/chapters'), api('/bank')]);
  const all = bank.questions;
  const hasAnswers = all.some(q => q.type === 'mcq' && Number.isInteger(q.correctIndex));
  state.opts = state.opts || {
    chapters: chapters.map(c => c.number), mcq: 20, essay: 4, levels: [...LEVELS], diffs: [...DIFFS],
    approvedOnly: true, models: 1, shuffleOptions: true, mcqMark: 1, essayMark: 0, answerGrid: true, seed: Math.floor(Math.random() * 1e6),
  };
  const o = state.opts, h = state.header;
  const poolFor = type => all.filter(q => q.type === type && !q.excluded && o.chapters.includes(q.chapter.number)
    && (!q.thinkingLevel || o.levels.includes(q.thinkingLevel)) && (!q.difficulty || o.diffs.includes(q.difficulty))
    && (!o.approvedOnly || q.status === 'approved'));
  const avail = { mcq: poolFor('mcq').length, essay: poolFor('essay').length };
  const field = (k, label, wide) => `<div ${wide ? 'style="grid-column:1/-1"' : ''}><label for="h-${k}">${label}</label><input id="h-${k}" data-h="${k}" value="${esc(h[k])}"></div>`;
  const chk = (name, val, on, label) => `<label class="chk"><input type="checkbox" data-${name}="${esc(val)}" ${on ? 'checked' : ''}> ${esc(label)}</label>`;

  $app.innerHTML = `
    <div class="crumbs no-print"><a href="#/">الرئيسية</a> ‹ منشئ الاختبارات</div>
    <div class="hero no-print"><div><h1>منشئ نماذج الاختبارات</h1>
      <p class="muted">اختر الفصول وعدد الأسئلة ومستواها ونوعها، ثم صدّر الاختبار PDF جاهزًا للطباعة بكليشة المدرسة.</p></div></div>
    <div class="grid exam-setup no-print">
      <section class="card">
        <h2>محتوى الاختبار</h2>
        <h3>الفصول</h3>
        <div class="chk-grid">${chapters.map(c => chk('ch', c.number, o.chapters.includes(c.number), `${c.number}. ${c.title}`)).join('')}</div>
        <div class="form-grid" style="margin-top:.75rem">
          <div><label for="x-mcq">عدد أسئلة الاختيار من متعدد <span class="muted small">(المتاح ${avail.mcq})</span></label><input id="x-mcq" type="number" min="0" max="200" value="${o.mcq}"></div>
          <div><label for="x-essay">عدد الأسئلة المقالية <span class="muted small">(المتاح ${avail.essay})</span></label><input id="x-essay" type="number" min="0" max="50" value="${o.essay}"></div>
        </div>
        <h3 style="margin-top:.75rem">مستوى التفكير</h3>
        <div class="chk-grid">${LEVELS.map(l => chk('lv', l, o.levels.includes(l), l)).join('')}</div>
        <h3 style="margin-top:.75rem">درجة الصعوبة</h3>
        <div class="chk-grid">${DIFFS.map(d => chk('df', d, o.diffs.includes(d), d)).join('')}</div>
      </section>
      <section class="card">
        <h2>إعدادات النماذج والدرجات</h2>
        <div class="form-grid">
          <div><label for="x-models">عدد النماذج</label><select id="x-models">${[1, 2, 3, 4].map(n => `<option ${o.models === n ? 'selected' : ''} value="${n}">${n === 1 ? 'نموذج واحد' : `${n} نماذج (${MODEL_NAMES.slice(0, n).join('، ')})`}</option>`).join('')}</select></div>
          <div><label for="x-mmark">درجة سؤال الاختيار</label><input id="x-mmark" type="number" min="0.25" step="0.25" value="${o.mcqMark}"></div>
          <div><label for="x-emark">درجة السؤال المقالي</label><input id="x-emark" type="number" min="0" step="0.5" value="${o.essayMark}" title="صفر = حسب توزيع الدرجات في السؤال"><span class="small muted">صفر = حسب توزيع الدرجات في سلم التصحيح</span></div>
          <div><label for="x-seed">رقم الاختيار (لإعادة إنتاج الاختبار نفسه)</label><input id="x-seed" type="number" value="${o.seed}"></div>
        </div>
        ${chk('opt', 'shuffleOptions', o.shuffleOptions, 'خلط ترتيب البدائل بين النماذج')}
        ${chk('opt', 'answerGrid', o.answerGrid, 'إضافة جدول إجابة لأسئلة الاختيار في ورقة الطالب')}
        ${chk('opt', 'approvedOnly', o.approvedOnly, 'الأسئلة المعتمدة فقط')}
        <h2 style="margin-top:1rem">بيانات الكليشة</h2>
        <div class="form-grid">
          ${field('country', 'الدولة')}${field('org', 'الجهة')}${field('dept', 'الإدارة')}${field('school', 'المدرسة')}
          ${field('title', 'عنوان الاختبار')}${field('year', 'العام الدراسي')}${field('subject', 'المادة')}${field('grade', 'الصف')}
          ${field('duration', 'الزمن')}${field('date', 'التاريخ')}${field('teacher', 'معلم المادة')}${field('instructions', 'التعليمات', true)}
        </div>
      </section>
    </div>
    <div class="actions no-print" style="margin:1rem 0">
      <button type="button" class="primary" id="x-build">إنشاء الاختبار</button>
      <button type="button" id="x-reroll">اختيار أسئلة أخرى</button>
      <span class="muted small" id="x-status"></span>
    </div>
    <div id="x-output"></div>`;

  const read = () => {
    o.chapters = [...$app.querySelectorAll('[data-ch]:checked')].map(i => Number(i.dataset.ch));
    o.levels = [...$app.querySelectorAll('[data-lv]:checked')].map(i => i.dataset.lv);
    o.diffs = [...$app.querySelectorAll('[data-df]:checked')].map(i => i.dataset.df);
    for (const i of $app.querySelectorAll('[data-opt]')) o[i.dataset.opt] = i.checked;
    o.mcq = Math.max(0, Number($app.querySelector('#x-mcq').value) || 0);
    o.essay = Math.max(0, Number($app.querySelector('#x-essay').value) || 0);
    o.models = Number($app.querySelector('#x-models').value) || 1;
    o.mcqMark = Number($app.querySelector('#x-mmark').value) || 1;
    o.essayMark = Math.max(0, Number($app.querySelector('#x-emark').value) || 0);
    o.seed = Number($app.querySelector('#x-seed').value) || 1;
    for (const i of $app.querySelectorAll('[data-h]')) h[i.dataset.h] = i.value.trim();
    saveHeader(h);
  };

  const build = () => {
    read();
    if (!o.chapters.length) return toast('اختر فصلًا واحدًا على الأقل', true);
    if (!o.mcq && !o.essay) return toast('حدد عدد الأسئلة', true);
    const rand = rng(o.seed);
    const mcqPool = poolFor('mcq'), essayPool = poolFor('essay');
    const mcq = pick(mcqPool, o.mcq, rand), essay = pick(essayPool, o.essay, rand);
    const notes = [];
    if (mcq.length < o.mcq) notes.push(`أسئلة الاختيار المتاحة بهذه الشروط ${mcqPool.length} فقط`);
    if (essay.length < o.essay) notes.push(`الأسئلة المقالية المتاحة بهذه الشروط ${essayPool.length} فقط`);
    // النماذج: الأسئلة نفسها بترتيب مختلف (وبدائل مخلوطة اختياريًا). النموذج (أ) يحافظ على ترتيب الفصول.
    const sortByCh = list => list.slice().sort((a, b) => a.chapter.number - b.chapter.number || a.lesson.number - b.lesson.number);
    const models = MODEL_NAMES.slice(0, o.models).map((name, mi) => {
      const mr = rng(o.seed + 97 * (mi + 1));
      const order = mi === 0 ? sortByCh(mcq) : shuffle(mcq, mr);
      return {
        name,
        mcq: order.map(q => {
          const idx = mi > 0 && o.shuffleOptions ? shuffle([0, 1, 2], mr) : [0, 1, 2];
          return { q, options: idx.map(i => q.options[i]), correct: hasAnswers ? idx.indexOf(q.correctIndex) : -1 };
        }),
        essay: mi === 0 ? sortByCh(essay) : shuffle(essay, mr),
      };
    });
    const essayMarks = q => o.essayMark || (q.marks || []).reduce((s, m) => s + Number(m.marks || 0), 0) || 4;
    const total = mcq.length * o.mcqMark + essay.reduce((s, q) => s + essayMarks(q), 0);
    state.exam = { models, total, essayMarks, notes };
    render();
  };

  const header = (m, kind) => `
    <header class="paper-head">
      <div class="ph-right">
        <div>${esc(h.country)}</div><div>${esc(h.org)}</div><div>${esc(h.dept)}</div><div class="ph-school">${esc(h.school)}</div>
      </div>
      <div class="ph-logo"><img src="assets/org-logo.png" alt="شعار ${esc(h.org)}"></div>
      <div class="ph-left">
        <div class="ph-title">${esc(h.title)}</div>
        <div>العام الدراسي ${esc(h.year)}</div>
        <div>المادة: <b>${esc(h.subject)}</b></div>
        <div>الزمن: ${esc(h.duration)}</div>
      </div>
    </header>
    <table class="paper-info">
      <tr><th>اسم الطالب</th><td colspan="3"></td><th>رقم الجلوس</th><td class="w-num"></td></tr>
      <tr><th>الصف</th><td>${esc(h.grade)}</td><th>الشعبة</th><td class="w-num"></td><th>التاريخ</th><td>${esc(h.date)}</td></tr>
    </table>
    <div class="paper-meta">
      <div class="model-badge">النموذج <b>(${m.name})</b>${kind === 'key' ? ' — مفتاح الإجابة' : ''}</div>
      <table class="paper-score"><tr><th>الدرجة المستحقة</th><td class="score-box"></td><th>من</th><td class="score-total">${fmt(state.exam.total)}</td></tr>
        <tr><th>كتابةً</th><td colspan="3"></td></tr></table>
      <table class="paper-score"><tr><th>المصحح</th><td class="sig"></td></tr><tr><th>المراجع</th><td class="sig"></td></tr></table>
    </div>
    ${kind === 'student' && h.instructions ? `<p class="paper-instr"><b>تعليمات:</b> ${esc(h.instructions)}</p>` : ''}`;

  const fmt = n => (Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/\.?0+$/, ''));
  const stim = s => s ? `<table class="paper-table"><thead><tr>${s.headers.map(x => `<th>${esc(x)}</th>`).join('')}</tr></thead><tbody>${s.rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>` : '';
  const longOpts = opts => opts.some(x => x.length > 28);

  const studentPaper = m => {
    let qn = 0;
    const parts = [];
    if (m.mcq.length) parts.push(`
      <section class="paper-q">
        <h3 class="q-title">السؤال ${ORDINALS[qn++]}: اختر الإجابة الصحيحة لكل مما يأتي <span>(${fmt(m.mcq.length * o.mcqMark)} درجة)</span></h3>
        ${o.answerGrid ? answerGrid(m) : ''}
        <ol class="paper-mcq">${m.mcq.map(({ q, options }, i) => `
          <li class="pq" data-swap="mcq:${q.id}">
            <div class="pq-stem"><span class="pq-n">${i + 1}</span>${esc(q.stem)}</div>${stim(q.stimulus)}
            <div class="pq-opts ${longOpts(options) ? 'stack' : ''}">${options.map((x, k) => `<span><b>${LETTERS[k]})</b> ${esc(x)}</span>`).join('')}</div>
          </li>`).join('')}</ol>
      </section>`);
    if (m.essay.length) parts.push(`
      <section class="paper-q">
        <h3 class="q-title">السؤال ${ORDINALS[qn++]}: أجب عن الأسئلة الآتية <span>(${fmt(m.essay.reduce((s, q) => s + state.exam.essayMarks(q), 0))} درجة)</span></h3>
        <ol class="paper-essay">${m.essay.map((q, i) => `
          <li class="pq" data-swap="essay:${q.id}">
            <div class="pq-stem"><span class="pq-n">${i + 1}</span>${esc(q.stem)} <span class="pq-mark">(${fmt(state.exam.essayMarks(q))} درجات)</span></div>${stim(q.stimulus)}
            <div class="answer-lines">${'<div></div>'.repeat(Math.min(8, 3 + Math.round(state.exam.essayMarks(q))))}</div>
          </li>`).join('')}</ol>
      </section>`);
    return `<article class="paper">${header(m, 'student')}${parts.join('')}
      <footer class="paper-end">انتهت الأسئلة — مع تمنياتنا لكم بالتوفيق والنجاح${h.teacher ? `<span>معلم المادة: ${esc(h.teacher)}</span>` : ''}</footer></article>`;
  };

  const answerGrid = m => {
    const rows = [];
    for (let i = 0; i < m.mcq.length; i += 10) {
      const slice = m.mcq.slice(i, i + 10);
      rows.push(`<tr><th>رقم السؤال</th>${slice.map((_, k) => `<th>${i + k + 1}</th>`).join('')}</tr><tr><th>الإجابة</th>${slice.map(() => '<td></td>').join('')}</tr>`);
    }
    return `<table class="answer-grid">${rows.join('')}</table>`;
  };

  const keyPaper = m => `
    <article class="paper">${header(m, 'key')}
      ${m.mcq.length ? `<h3 class="q-title">مفتاح أسئلة الاختيار من متعدد</h3>
        <table class="answer-grid key">${(() => { const r = []; for (let i = 0; i < m.mcq.length; i += 10) { const s = m.mcq.slice(i, i + 10); r.push(`<tr><th>السؤال</th>${s.map((_, k) => `<th>${i + k + 1}</th>`).join('')}</tr><tr><th>الإجابة</th>${s.map(x => `<td>${x.correct >= 0 ? LETTERS[x.correct] : '؟'}</td>`).join('')}</tr>`); } return r.join(''); })()}</table>
        <ol class="key-list">${m.mcq.map(x => `<li><b>${x.correct >= 0 ? LETTERS[x.correct] + ') ' + esc(x.options[x.correct]) : ''}</b> — ${esc(x.q.explanation || '')}</li>`).join('')}</ol>` : ''}
      ${m.essay.length ? `<h3 class="q-title">الإجابات النموذجية للأسئلة المقالية</h3>
        <ol class="key-list">${m.essay.map(q => `<li><div class="pq-stem">${esc(q.stem)}</div>
          <div><b>الإجابة النموذجية:</b> ${esc(q.modelAnswer || 'غير متاحة (سجّل الدخول لعرض الإجابات)')}</div>
          ${q.marks?.length ? `<div><b>توزيع الدرجات:</b> ${q.marks.map(x => `${esc(x.element)} (${fmt(Number(x.marks))})`).join('، ')}</div>` : ''}</li>`).join('')}</ol>` : ''}
    </article>`;

  const render = () => {
    const ex = state.exam;
    const out = $app.querySelector('#x-output');
    $app.querySelector('#x-status').textContent = `${ex.models[0].mcq.length} اختيار + ${ex.models[0].essay.length} مقالي · الدرجة الكلية ${fmt(ex.total)}${ex.notes.length ? ' · ' + ex.notes.join('، ') : ''}`;
    out.innerHTML = `
      <div class="actions no-print exam-actions">
        <button type="button" class="primary" data-xprint="student">تصدير PDF — نسخة الطالب</button>
        ${hasAnswers ? `<button type="button" data-xprint="key">تصدير PDF — مفتاح الإجابة</button><button type="button" data-xprint="all">تصدير الكل</button>` : '<span class="small muted">مفتاح الإجابة يتطلب تسجيل الدخول</span>'}
        <span class="small muted">في نافذة الطباعة اختر «حفظ بصيغة PDF» والحجم A4.</span>
      </div>
      <p class="small muted no-print">لاستبدال سؤال في النموذج (أ): اضغط عليه في المعاينة.</p>
      <div class="papers">
        <div class="set-student">${ex.models.map(studentPaper).join('')}</div>
        ${hasAnswers ? `<div class="set-key">${ex.models.map(keyPaper).join('')}</div>` : ''}
      </div>`;
    out.querySelectorAll('[data-xprint]').forEach(b => b.onclick = () => {
      document.body.classList.remove('xprint-student', 'xprint-key', 'xprint-all');
      document.body.classList.add('exam-printing', 'xprint-' + b.dataset.xprint);
      window.print();
    });
    out.querySelectorAll('.set-student .paper:first-child [data-swap]').forEach(li => li.onclick = () => swap(li.dataset.swap));
  };

  const swap = key => {
    const [type, id] = key.split(':');
    const ex = state.exam, m0 = ex.models[0];
    const used = new Set([...m0.mcq.map(x => x.q.id), ...m0.essay.map(q => q.id)]);
    const cur = all.find(q => q.id === Number(id));
    const rand = rng(Date.now() % 1e9);
    const cands = poolFor(type).filter(q => !used.has(q.id) && q.chapter.number === cur.chapter.number);
    const alt = shuffle(cands.length ? cands : poolFor(type).filter(q => !used.has(q.id)), rand)[0];
    if (!alt) return toast('لا يوجد سؤال بديل بهذه الشروط', true);
    for (const m of ex.models) {
      if (type === 'mcq') {
        const i = m.mcq.findIndex(x => x.q.id === cur.id);
        const keep = m.mcq[i];
        const idx = keep.options.map(op => cur.options.indexOf(op)); // نحافظ على نمط خلط البدائل للنموذج
        m.mcq[i] = { q: alt, options: idx.map(k => alt.options[k]), correct: hasAnswers ? idx.indexOf(alt.correctIndex) : -1 };
      } else {
        const i = m.essay.findIndex(q => q.id === cur.id);
        m.essay[i] = alt;
      }
    }
    ex.total = m0.mcq.length * o.mcqMark + m0.essay.reduce((s, q) => s + ex.essayMarks(q), 0);
    render();
    toast('تم استبدال السؤال في جميع النماذج');
  };

  $app.querySelector('#x-build').onclick = () => { try { build(); } catch (e) { fail(e); } };
  $app.querySelector('#x-reroll').onclick = () => { $app.querySelector('#x-seed').value = Math.floor(Math.random() * 1e6); build(); };
  if (state.exam) render();
}

window.addEventListener('afterprint', () => document.body.classList.remove('exam-printing', 'xprint-student', 'xprint-key', 'xprint-all'));
