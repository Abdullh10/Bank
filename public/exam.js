// منشئ نماذج الاختبارات: اختيار الفصول والعدد والمستوى والنوع، ونماذج متعددة، وكليشة المدرسة، وتصدير PDF عبر الطباعة.
import { icon } from './icons.js';
const ttl = (ic, html, tag = 'h2', size = 30) => `<${tag} class="ttl">${icon(ic, size)}<span>${html}</span></${tag}>`;
const LEVELS = ['تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع'];
const DIFFS = ['سهل', 'متوسط', 'صعب'];
const MODEL_NAMES = ['أ', 'ب', 'ج', 'د'];
const LETTERS = ['أ', 'ب', 'ج'];
const ORDINALS = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس'];
const STORE_KEY = 'chem21.exam.header.v1';
const HIJRI_MONTHS = ['محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة', 'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'];

// التاريخ الهجري الحالي (تقويم أم القرى) من المتصفح، مع قيمة احتياطية.
function todayHijri() {
  try {
    const parts = new Intl.DateTimeFormat('en-u-ca-islamic-umalqura-nu-latn', { day: 'numeric', month: 'numeric', year: 'numeric' }).formatToParts(new Date());
    const get = t => Number(parts.find(p => p.type === t)?.value);
    const y = get('year'), m = get('month'), d = get('day');
    if (y > 1400 && m >= 1 && m <= 12) return { y, m, d };
  } catch { /* المتصفح لا يدعم التقويم الهجري */ }
  return { y: 1448, m: 4, d: 1 };
}
const HIJRI_NOW = todayHijri();
const yearsAround = () => Array.from({ length: 5 }, (_, i) => `${HIJRI_NOW.y - 1 + i}هـ`);
const CHOICES = {
  title: ['اختبار الفصل الدراسي الأول', 'اختبار الفصل الدراسي الثاني', 'اختبار منتصف الفصل الدراسي', 'اختبار الدور الثاني', 'اختبار قصير', 'اختبار تجريبي', 'ورقة عمل'],
  year: yearsAround(),
  subject: ['الكيمياء 1', 'الكيمياء 2-1', 'الكيمياء 2-2', 'الكيمياء 3', 'الكيمياء 4'],
  grade: ['الأول الثانوي', 'الثاني الثانوي', 'الثالث الثانوي'],
  duration: ['ساعتان ونصف', 'ساعتان', 'ساعة ونصف', 'ساعة واحدة', 'ثلاث ساعات', '45 دقيقة', '30 دقيقة', '20 دقيقة'],
  country: ['المملكة العربية السعودية'],
  org: ['الهيئة الملكية بالجبيل', 'الهيئة الملكية بينبع', 'وزارة التعليم'],
  dept: ['إدارة التعليم العام', 'إدارة التعليم'],
};
// يبني نص التاريخ من الاختيارات؛ ترك اليوم أو الشهر فارغًا يُطبع نقاطًا ليكتبه المعلم يدويًا.
function dateText(h) {
  const d = h.dateDay ? String(h.dateDay) : '....', m = h.dateMonth ? String(h.dateMonth) : '....';
  if (h.dateFormat === 'name' && h.dateDay && h.dateMonth) return `${h.dateDay} ${HIJRI_MONTHS[h.dateMonth - 1]} ${h.dateYear}`;
  return `${d}/${m}/${h.dateYear}`;
}

const DEFAULT_HEADER = {
  country: 'المملكة العربية السعودية',
  org: 'الهيئة الملكية بالجبيل',
  dept: 'إدارة التعليم العام',
  school: 'مدرسة العلا الثانوية',
  title: 'اختبار الفصل الدراسي الأول',
  year: `${HIJRI_NOW.y}هـ`,
  subject: 'الكيمياء 2-1',
  grade: 'الثاني الثانوي',
  duration: 'ساعتان ونصف',
  date: '..../..../1448هـ',
  dateDay: '',
  dateMonth: '',
  dateYear: `${HIJRI_NOW.y}هـ`,
  dateFormat: 'num',
  teacher: '',
  instructions: 'اقرأ الأسئلة بعناية، وأجب عنها جميعًا بالقلم الأزرق. لا يُسمح باستخدام المصحح السائل. يُسمح باستخدام الآلة الحاسبة غير المبرمجة.',
};

function loadHeader() {
  let h;
  try { h = { ...DEFAULT_HEADER, ...JSON.parse(localStorage.getItem(STORE_KEY) || '{}') }; } catch { h = { ...DEFAULT_HEADER }; }
  // ترحيل اختيارات محفوظة قديمة: لا «مسارات» ولا «السنة المشتركة» ولا «الفصل الدراسي الثالث»
  h.grade = String(h.grade || '').replace(/\s*[–-]?\s*\(?مسارات\)?/g, '').trim() || DEFAULT_HEADER.grade;
  if (h.grade === 'السنة المشتركة') h.grade = DEFAULT_HEADER.grade;
  if (/الفصل الدراسي الثالث/.test(h.title || '')) h.title = DEFAULT_HEADER.title;
  return h;
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

// مكتبة docx (إصدار مثبت) تُحمَّل من CDN عند أول تصدير Word فقط
const DOCX_URL = 'https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.umd.js';
let docxLoading = null;
function loadDocx() {
  if (window.docx) return Promise.resolve(window.docx);
  docxLoading ||= new Promise((resolve, reject) => {
    const sc = Object.assign(document.createElement('script'), { src: DOCX_URL, onload: () => resolve(window.docx),
      onerror: () => { docxLoading = null; reject(new Error('تعذر تحميل مكتبة Word؛ تحقق من الإنترنت ثم أعد المحاولة')); } });
    document.head.append(sc);
  });
  return docxLoading;
}

// يُستدعى عند الخروج: لا يبقى اختبار المستخدم السابق (ومفتاحه) على الجهاز
export const resetExam = () => { state.exam = null; state.opts = null; };

export async function pageExam(ctx) {
  const { api, esc, fail, toast, $app, course, protectedBank } = ctx;
  // الكليشة تتبع المقرر المختار: المادة والصف وعنوان الفصل الدراسي (مرة عند تغيير المقرر؛ تعديلاتك بعدها تبقى)
  if (course) {
    const prev = state.header.courseId ?? 1;
    if (prev !== course.id) {
      Object.assign(state.header, { subject: course.title || course.code, grade: course.grade,
        title: course.term === 'الثاني' ? 'اختبار الفصل الدراسي الثاني' : 'اختبار الفصل الدراسي الأول' });
    }
    state.header.courseId = course.id; saveHeader(state.header);
  }
  const [chapters, bank] = await Promise.all([api('/chapters'), api('/bank')]);
  const all = bank.questions;
  // البنك المحمي يصل دون إجابات؛ مفتاح الاختبار يُجلب من الخادم للأسئلة المختارة فقط
  const hasAnswers = protectedBank || all.some(q => q.type === 'mcq' && Number.isInteger(q.correctIndex));
  const ensureAnswers = async qs => {
    if (!protectedBank) return;
    const need = qs.filter(q => !q.answersLoaded);
    if (!need.length) return;
    const rows = await api('/exam/answers', { method: 'POST', body: { ids: need.map(q => q.id) }, read: true });
    const byId = new Map(rows.map(r => [r.id, r]));
    for (const q of need) { const r = byId.get(q.id); if (r) Object.assign(q, r, { answersLoaded: true }); }
  };
  state.opts = state.opts || {
    chapters: chapters.map(c => c.number), mcq: 20, essay: 4, levels: [...LEVELS], diffs: [...DIFFS],
    approvedOnly: true, models: 1, shuffleOptions: true, mcqMark: 1, essayMark: 0, answerGrid: true, density: 'auto', seed: Math.floor(Math.random() * 1e6),
  };
  state.opts.density ||= 'auto';
  const o = state.opts, h = state.header;
  const poolFor = type => all.filter(q => q.type === type && !q.excluded && o.chapters.includes(q.chapter.number)
    && (!q.thinkingLevel || o.levels.includes(q.thinkingLevel)) && (!q.difficulty || o.diffs.includes(q.difficulty))
    && (!o.approvedOnly || q.status === 'approved'));
  const avail = { mcq: poolFor('mcq').length, essay: poolFor('essay').length };
  const field = (k, label, wide) => `<div ${wide ? 'style="grid-column:1/-1"' : ''}><label for="h-${k}">${label}</label><input id="h-${k}" data-h="${k}" value="${esc(h[k])}"></div>`;
  // قائمة منسدلة؛ اختيار «أخرى» يُظهر حقلًا لكتابة قيمة غير موجودة في القائمة.
  const sel = (k, label) => {
    const opts = CHOICES[k] || [];
    const other = h[k] && !opts.includes(h[k]);
    return `<div><label for="h-${k}">${label}</label>
      <select id="h-${k}" data-hsel="${k}">${opts.map(v => `<option ${v === h[k] ? 'selected' : ''}>${esc(v)}</option>`).join('')}<option value="__other" ${other ? 'selected' : ''}>أخرى (اكتب)…</option></select>
      <input class="other-input" data-hother="${k}" value="${other ? esc(h[k]) : ''}" placeholder="اكتب ${label}" ${other ? '' : 'hidden'}></div>`;
  };
  const dateField = () => `<div style="grid-column:1/-1"><label>التاريخ (هجري)</label>
    <div class="date-row">
      <select data-hd="dateDay" aria-label="اليوم"><option value="">اليوم: يُكتب يدويًا</option>${Array.from({ length: 30 }, (_, i) => `<option ${String(i + 1) === String(h.dateDay) ? 'selected' : ''}>${i + 1}</option>`).join('')}</select>
      <select data-hd="dateMonth" aria-label="الشهر"><option value="">الشهر: يُكتب يدويًا</option>${HIJRI_MONTHS.map((n, i) => `<option value="${i + 1}" ${String(i + 1) === String(h.dateMonth) ? 'selected' : ''}>${i + 1} – ${n}</option>`).join('')}</select>
      <select data-hd="dateYear" aria-label="السنة">${yearsAround().map(y => `<option ${y === h.dateYear ? 'selected' : ''}>${y}</option>`).join('')}</select>
      <select data-hd="dateFormat" aria-label="صيغة التاريخ"><option value="num" ${h.dateFormat !== 'name' ? 'selected' : ''}>بالأرقام</option><option value="name" ${h.dateFormat === 'name' ? 'selected' : ''}>باسم الشهر</option></select>
      <button type="button" id="h-today">تاريخ اليوم</button>
    </div><div class="small muted" id="h-date-preview">سيُطبع: ${esc(dateText(h))}</div></div>`;
  const chk = (name, val, on, label) => `<label class="chk"><input type="checkbox" data-${name}="${esc(val)}" ${on ? 'checked' : ''}> ${esc(label)}</label>`;

  $app.innerHTML = `
    <div class="crumbs no-print"><a href="#/course">الرئيسية</a> ‹ منشئ الاختبارات</div>
    <div class="hero no-print"><div class="hero-ic">${icon('exam', 52)}<div><h1>منشئ نماذج الاختبارات</h1>
      <p class="muted">اختر الفصول وعدد الأسئلة ومستواها ونوعها، ثم صدّر الاختبار PDF جاهزًا للطباعة بكليشة المدرسة.</p></div></div></div>
    <div class="grid exam-setup no-print">
      <section class="card">
        ${ttl('chapters', 'محتوى الاختبار')}
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
        ${ttl('sliders', 'إعدادات النماذج والدرجات')}
        <div class="form-grid">
          <div><label for="x-models">عدد النماذج</label><select id="x-models">${[1, 2, 3, 4].map(n => `<option ${o.models === n ? 'selected' : ''} value="${n}">${n === 1 ? 'نموذج واحد' : `${n} نماذج (${MODEL_NAMES.slice(0, n).join('، ')})`}</option>`).join('')}</select></div>
          <div><label for="x-mmark">درجة سؤال الاختيار</label><input id="x-mmark" type="number" min="0.25" step="0.25" value="${o.mcqMark}"></div>
          <div><label for="x-emark">درجة السؤال المقالي</label><input id="x-emark" type="number" min="0" step="0.5" value="${o.essayMark}" title="صفر = حسب توزيع الدرجات في السؤال"><span class="small muted">صفر = حسب توزيع الدرجات في سلم التصحيح</span></div>
          <div><label for="x-seed">رقم الاختيار (لإعادة إنتاج الاختبار نفسه)</label><input id="x-seed" type="number" value="${o.seed}"></div>
          <div><label for="x-density">تنسيق الورقة (A4)</label><select id="x-density">${[['auto', 'تلقائي: صفحتان قدر الإمكان'], ['normal', 'عادي'], ['compact', 'مضغوط']]
            .map(([v, t]) => `<option value="${v}" ${o.density === v ? 'selected' : ''}>${t}</option>`).join('')}</select></div>
        </div>
        ${chk('opt', 'shuffleOptions', o.shuffleOptions, 'خلط ترتيب البدائل بين النماذج')}
        ${chk('opt', 'answerGrid', o.answerGrid, 'إضافة جدول إجابة لأسئلة الاختيار في ورقة الطالب')}
        ${chk('opt', 'approvedOnly', o.approvedOnly, 'الأسئلة المعتمدة فقط')}
        ${ttl('exam', 'بيانات الكليشة').replace('class="ttl"', 'class="ttl" style="margin-top:1.2rem"')}
        <div class="form-grid">
          ${sel('country', 'الدولة')}${sel('org', 'الجهة')}${sel('dept', 'الإدارة')}${field('school', 'المدرسة')}
          ${sel('title', 'عنوان الاختبار')}${sel('year', 'العام الدراسي')}${sel('subject', 'المادة')}${sel('grade', 'الصف')}
          ${sel('duration', 'الزمن')}${field('teacher', 'معلم المادة')}
          ${dateField()}
          ${field('instructions', 'التعليمات', true)}
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
    o.density = $app.querySelector('#x-density').value;
    for (const i of $app.querySelectorAll('[data-h]')) h[i.dataset.h] = i.value.trim();
    for (const i of $app.querySelectorAll('[data-hsel]')) {
      const k = i.dataset.hsel;
      h[k] = i.value === '__other' ? $app.querySelector(`[data-hother="${k}"]`).value.trim() : i.value;
    }
    for (const i of $app.querySelectorAll('[data-hd]')) h[i.dataset.hd] = i.value;
    h.date = dateText(h);
    saveHeader(h);
  };

  const build = async () => {
    read();
    if (!o.chapters.length) return toast('اختر فصلًا واحدًا على الأقل', true);
    if (!o.mcq && !o.essay) return toast('حدد عدد الأسئلة', true);
    const rand = rng(o.seed);
    const mcqPool = poolFor('mcq'), essayPool = poolFor('essay');
    const mcq = pick(mcqPool, o.mcq, rand), essay = pick(essayPool, o.essay, rand);
    const notes = [];
    if (mcq.length < o.mcq) notes.push(`أسئلة الاختيار المتاحة بهذه الشروط ${mcqPool.length} فقط`);
    if (essay.length < o.essay) notes.push(`الأسئلة المقالية المتاحة بهذه الشروط ${essayPool.length} فقط`);
    await ensureAnswers([...mcq, ...essay]);
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
      <div class="actions no-print exam-actions">
        <button type="button" data-xword="student">تحميل Word — نسخة الطالب</button>
        ${hasAnswers ? `<button type="button" data-xword="key">Word — مفتاح الإجابة</button><button type="button" data-xword="all">Word — الكل</button>` : ''}
        <span class="small muted">ملف Word قابل للتعديل والتنسيق، وكل سؤال فيه لا ينقسم بين صفحتين.</span>
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
    fitPapers(out);
    out.querySelectorAll('[data-xword]').forEach(b => b.onclick = async () => {
      if (b.disabled) return;
      const label = b.textContent; b.disabled = true; b.textContent = 'جارٍ إنشاء ملف Word…';
      try { await exportWord(b.dataset.xword); toast('تم تحميل ملف Word'); }
      catch (e) { fail(e); } finally { b.disabled = false; b.textContent = label; }
    });
  };

  // ---------- ملاءمة صفحات A4 ----------
  // ارتفاع محتوى صفحة A4 بعد الهوامش (297 − 10 − 14 مم) بالبكسل، مع هامش أمان لأن الأسئلة لا تنقسم بين الصفحات
  const PAGE_PX = (273 * 96) / 25.4 * 0.95;
  const DENSITIES = ['', 'dense-1', 'dense-2'];
  const pagesOf = paper => {
    const cs = getComputedStyle(paper);
    return (paper.scrollHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom)) / PAGE_PX;
  };
  const fitPapers = async out => {
    if (document.fonts?.ready) await document.fonts.ready.catch(() => {});
    const papers = [...out.querySelectorAll('.paper')];
    const setLevel = lv => papers.forEach(p => { p.classList.remove('dense-1', 'dense-2'); if (DENSITIES[lv]) p.classList.add(DENSITIES[lv]); });
    const maxPages = () => Math.max(...papers.filter(p => p.closest('.set-student')).map(pagesOf));
    let level = 0;
    if (o.density === 'compact') level = 2;
    else if (o.density === 'auto') {
      // أخف تنسيق يجعل الورقة صفحتين أو أقل؛ وإن تعذّر يبقى التنسيق الذي يقلل عدد الصفحات أكثر
      const tries = [0, 1, 2].map(lv => { setLevel(lv); return { lv, pages: Math.ceil(maxPages()) }; });
      const fit = tries.find(t => t.pages <= 2);
      level = fit ? fit.lv : tries.reduce((a, b) => (b.pages < a.pages ? b : a)).lv;
    }
    setLevel(level);
    const n = Math.max(1, Math.ceil(maxPages()));
    const st = $app.querySelector('#x-status');
    if (st && !st.textContent.includes('الطباعة:')) st.textContent += ` · الطباعة: ${n === 1 ? 'صفحة واحدة' : n === 2 ? 'صفحتان' : n + ' صفحات'} لكل نموذج${level ? ' (تنسيق مضغوط)' : ''}`;
  };

  // ---------- تصدير Word ----------
  const exportWord = async kind => {
    const [D, { buildExamDocx }, logo] = await Promise.all([loadDocx(), import('./exam-docx.js'),
      fetch('assets/org-logo.png').then(r => (r.ok ? r.arrayBuffer() : null)).catch(() => null)]);
    const doc = buildExamDocx(D, { exam: state.exam, header: h, opts: o, kind, logo, letters: LETTERS, ordinals: ORDINALS, fmt });
    const blob = await D.Packer.toBlob(doc);
    // أسماء ملفات إنجليزية: بعض المتصفحات تتجاهل الأسماء العربية فيُحفظ الملف دون امتداد
    const names = { student: 'student', key: 'answer-key', all: 'full' };
    const stamp = new Date().toISOString().slice(0, 10);
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `itqan-exam-${names[kind]}-${stamp}.docx` });
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  };

  const swap = async key => {
    const [type, id] = key.split(':');
    const ex = state.exam, m0 = ex.models[0];
    const used = new Set([...m0.mcq.map(x => x.q.id), ...m0.essay.map(q => q.id)]);
    const cur = all.find(q => q.id === Number(id));
    if (!cur) { toast('هذا السؤال لم يعد في البنك؛ أعد إنشاء الاختبار', true); return; }
    const rand = rng(Date.now() % 1e9);
    const cands = poolFor(type).filter(q => !used.has(q.id) && q.chapter.number === cur.chapter.number);
    const alt = shuffle(cands.length ? cands : poolFor(type).filter(q => !used.has(q.id)), rand)[0];
    if (!alt) return toast('لا يوجد سؤال بديل بهذه الشروط', true);
    try { await ensureAnswers([alt]); } catch (e) { return fail(e); }
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

  for (const i of $app.querySelectorAll('[data-hsel]')) i.onchange = () => {
    const box = $app.querySelector(`[data-hother="${i.dataset.hsel}"]`);
    box.hidden = i.value !== '__other';
    if (!box.hidden) box.focus();
  };
  const previewDate = () => {
    const t = {};
    for (const i of $app.querySelectorAll('[data-hd]')) t[i.dataset.hd] = i.value;
    $app.querySelector('#h-date-preview').textContent = 'سيُطبع: ' + dateText(t);
  };
  for (const i of $app.querySelectorAll('[data-hd]')) i.onchange = previewDate;
  $app.querySelector('#h-today').onclick = () => {
    $app.querySelector('[data-hd="dateDay"]').value = String(HIJRI_NOW.d);
    $app.querySelector('[data-hd="dateMonth"]').value = String(HIJRI_NOW.m);
    $app.querySelector('[data-hd="dateYear"]').value = `${HIJRI_NOW.y}هـ`;
    previewDate();
  };
  $app.querySelector('#x-build').onclick = () => build().catch(fail);
  $app.querySelector('#x-reroll').onclick = () => { $app.querySelector('#x-seed').value = Math.floor(Math.random() * 1e6); build().catch(fail); };
  if (state.exam) render();
}

window.addEventListener('afterprint', () => document.body.classList.remove('exam-printing', 'xprint-student', 'xprint-key', 'xprint-all'));
