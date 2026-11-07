// استبانة الطلاب «itqan-v1»: أداة ثابتة مقتبسة ومعدّلة عن Davis (1989) وPintrich et al. (1991) وRovai et al. (2009).
// 16 عبارة ليكرت خماسية (5 = أوافق بشدة) + عبارة انتباه في الموضع العاشر + سؤالان مفتوحان اختياريان.
// الدوال التحليلية خالصة (لا DOM) وتُختبر في test/survey.test.js؛ وواجهتا الطالب والمعلم في آخر الملف.
import { mean, sd, pearson, fmt } from './impact-stats.js';

export const VERSION = 'itqan-v1';
export const DIMS = {
  A: 'الفائدة المدركة',
  B: 'التعلّم والتحصيل المدرك',
  C: 'الكفاءة الذاتية',
  D: 'عادات المذاكرة وسهولة الاستخدام',
};
// ترتيب العبارات ثابت (للمقارنة بين الفصول). rev: عبارة عكسية تُعاد ترميزها (6 − x). att: عبارة الانتباه (الصحيح «لا أوافق» = 2)
export const ITEMS = [
  { dim: 'A', text: 'ساعدتني منصة إتقان على فهم دروس الكيمياء بشكل أفضل.' },
  { dim: 'A', text: 'جعلت المنصة مذاكرتي للكيمياء أكثر فاعلية.' },
  { dim: 'A', text: 'ساعدتني المنصة على الاستعداد للاختبارات.' },
  { dim: 'A', text: 'التصحيح الفوري والتعليق على الخيار الخاطئ وضّحا لي سبب خطئي.' },
  { dim: 'B', text: 'أشعر أن مستواي في الكيمياء تحسّن بسبب التدريب على المنصة.' },
  { dim: 'B', text: 'صرت أحلّ أسئلة الكيمياء بدقة أكبر مما كنت عليه قبل استخدام المنصة.' },
  { dim: 'B', text: 'ساعدتني المنصة على اكتشاف الموضوعات التي أخطئ فيها ومعالجتها.' },
  { dim: 'B', rev: true, text: 'لا أظن أن مستواي في الكيمياء تغيّر بسبب التدريب على المنصة.' },
  { dim: 'C', text: 'صرت أكثر ثقة بقدرتي على حل أسئلة الكيمياء التي تحتاج تفكيرًا وتحليلًا.' },
  { att: true, text: 'للتأكد من انتباهك، اختر «لا أوافق» لهذه العبارة.' },
  { dim: 'C', text: 'أتوقع أداءً أفضل في اختبارات الكيمياء بعد التدريب على المنصة.' },
  { dim: 'C', text: 'أصبحت أكثر ثقة بقدرتي على حل المسائل الحسابية في الكيمياء.' },
  { dim: 'D', text: 'أستخدم نتائجي في المنصة لأعرف الدروس التي أحتاج مراجعتها.' },
  { dim: 'D', text: 'صرت أراجع الكيمياء بانتظام وليس قبل الاختبار فقط.' },
  { dim: 'D', text: 'كان استخدام المنصة سهلًا وواضحًا.' },
  { dim: 'D', rev: true, text: 'أحيانًا أجيب بسرعة لجمع النقاط أكثر من حرصي على الفهم.' },
  { dim: 'G', text: 'أنصح زملائي باستخدام منصة إتقان.' },
];
export const ATT = ITEMS.findIndex(i => i.att);
export const SCALE = [[5, 'أوافق بشدة'], [4, 'أوافق'], [3, 'محايد'], [2, 'لا أوافق'], [1, 'لا أوافق بشدة']];
export const OPEN = ['ما أكثر شيء في المنصة ساعدك على تعلّم الكيمياء؟ اذكر مثالًا.', 'ما الذي تقترح تغييره أو إضافته لتصبح المنصة أكثر فائدة لك؟'];
export const MIN_SHOW = 5;      // أقل عدد إجابات لعرض أي نتيجة
export const MIN_ALPHA = 15;    // أقل عدد لحساب ثبات ألفا (بين 15 و29 يُعرض تقديرًا أوليًا)
export const ALPHA_STABLE = 30; // من هذا العدد يُعدّ ثبات ألفا مستقرًا
export const MIN_CORR = 15;     // أقل عدد لعرض الارتباطات
export const MIN_SECONDS = 60;  // الإجابة الأسرع من دقيقة تُستبعد

// مستوى المتوسط على مقياس 1–5: المدى (4) مقسوم على 5 فئات متساوية (0.80)
export function level(m) {
  if (!Number.isFinite(m)) return '—';
  return m <= 1.8 ? 'منخفض جدًا' : m <= 2.6 ? 'منخفض' : m <= 3.4 ? 'متوسط' : m <= 4.2 ? 'مرتفع' : 'مرتفع جدًا';
}
export const alphaLabel = a => (!Number.isFinite(a) ? 'غير كافٍ للحكم' : a > 0.95 ? 'مرتفع جدًا (قد تتكرر العبارات)' : a >= 0.8 ? 'جيد' : a >= 0.7 ? 'مقبول' : a >= 0.6 ? 'مقبول لمقياس قصير (استكشافي)' : 'ضعيف: تُقرأ العبارات منفردة');

// الدرجة بعد إعادة ترميز العكسية
export const scored = (a, i) => (ITEMS[i].rev ? 6 - a[i] : a[i]);
const likert = () => ITEMS.map((it, i) => i).filter(i => !ITEMS[i].att);

/** تنظيف الإجابات: عبارة الانتباه، والإجابة نفسها على كل العبارات، والأسرع من دقيقة */
export function clean(rows) {
  const out = { kept: [], attention: 0, straight: 0, speed: 0 };
  for (const r of rows) {
    const a = r.a, idx = likert();
    if (a[ATT] !== 2) { out.attention++; continue; }
    if (idx.every(i => a[i] === a[idx[0]])) { out.straight++; continue; }
    if (Number.isFinite(r.d) && r.d < MIN_SECONDS) { out.speed++; continue; }
    out.kept.push(r);
  }
  return out;
}

/** ثبات ألفا كرونباخ لمصفوفة (طلاب × عبارات) */
export function cronbach(matrix) {
  const n = matrix.length, k = matrix[0]?.length || 0;
  if (n < 2 || k < 2) return NaN;
  const itemVar = Array.from({ length: k }, (_, j) => sd(matrix.map(r => r[j])) ** 2);
  const totVar = sd(matrix.map(r => r.reduce((s, x) => s + x, 0))) ** 2;
  return totVar ? (k / (k - 1)) * (1 - itemVar.reduce((s, x) => s + x, 0) / totVar) : NaN;
}

export const dimScore = (a, dim) => mean(ITEMS.map((it, i) => i).filter(i => ITEMS[i].dim === dim).map(i => scored(a, i)));

/** التحليل الكامل لإجابات منظَّفة */
export function analyzeSurvey(rows) {
  const items = ITEMS.map((it, i) => {
    if (it.att) return null;
    const v = rows.map(r => scored(r.a, i)), raw = rows.map(r => r.a[i]);
    return { i, ...it, n: v.length, mean: mean(v), sd: sd(v), agree: raw.length ? (100 * raw.filter(x => x >= 4).length) / raw.length : NaN, // موافقة حرفية على نص العبارة
      dist: SCALE.map(([k]) => (raw.length ? (100 * raw.filter(x => x === k).length) / raw.length : 0)) };
  });
  const dims = Object.keys(DIMS).map(dim => {
    const idx = ITEMS.map((it, i) => i).filter(i => ITEMS[i].dim === dim);
    const m = rows.map(r => idx.map(i => scored(r.a, i)));
    const scores = m.map(x => mean(x));
    const alpha = rows.length >= MIN_ALPHA ? cronbach(m) : NaN;
    const itemTotal = idx.map((i, j) => {
      const rest = m.map(x => x.reduce((s, y, jj) => (jj === j ? s : s + y), 0));
      return { i, r: rows.length >= MIN_ALPHA ? pearson(m.map(x => x[j]), rest) : NaN,
        alphaDrop: rows.length >= MIN_ALPHA ? cronbach(m.map(x => x.filter((_, jj) => jj !== j))) : NaN };
    });
    return { dim, label: DIMS[dim], items: idx, n: rows.length, mean: mean(scores), sd: sd(scores), level: level(mean(scores)),
      high: scores.length ? (100 * scores.filter(x => x >= 3.5).length) / scores.length : NaN, alpha, itemTotal };
  });
  return { n: rows.length, items: items.filter(Boolean), dims };
}

/** ارتباط سبيرمان (رتب + بيرسون) مع فترة ثقة 95% (فيشر) */
export function spearman(x, y) {
  const rank = a => { const s = a.map((v, i) => [v, i]).sort((p, q) => p[0] - q[0]), r = Array(a.length);
    for (let i = 0; i < s.length;) { let j = i; while (j + 1 < s.length && s[j + 1][0] === s[i][0]) j++; for (let k = i; k <= j; k++) r[s[k][1]] = (i + j) / 2 + 1; i = j + 1; } return r; };
  const n = x.length, rho = pearson(rank(x), rank(y));
  if (!Number.isFinite(rho) || n < 4) return { rho, n, lo: NaN, hi: NaN };
  const z = Math.atanh(Math.max(-0.999999, Math.min(0.999999, rho))), se = 1 / Math.sqrt(n - 3);
  return { rho, n, lo: Math.tanh(z - 1.96 * se), hi: Math.tanh(z + 1.96 * se) };
}
export const rhoLabel = r => (!Number.isFinite(r) ? '—' : Math.abs(r) < 0.1 ? 'لا يُذكر' : Math.abs(r) < 0.3 ? 'ضعيف' : Math.abs(r) < 0.5 ? 'متوسط' : 'قوي');

// ---------- واجهة الطالب: نموذج الاستبانة ----------
const PER_PAGE = 4;
export function surveyForm(ctx, it, done) {
  const { esc, $app, api, fail, toast } = ctx;
  const answers = Array(ITEMS.length).fill(null), open = ['', ''], startedAt = Date.now();
  const pages = []; for (let i = 0; i < ITEMS.length; i += PER_PAGE) pages.push(ITEMS.slice(i, i + PER_PAGE).map((x, j) => i + j));
  pages.push('open');
  let page = -1;
  const draw = () => {
    if (page < 0) {
      $app.innerHTML = `<section class="card sv-wrap"><h1 class="ttl">${esc(it.title)}</h1>
        ${it.body ? `<p>${esc(it.body)}</p>` : ''}
        <div class="notice info"><b>قبل أن تبدأ:</b> لا توجد إجابة صحيحة أو خاطئة، ولن تؤثر إجاباتك على درجاتك أو نقاطك.
          إجاباتك <b>سرية</b>: يرى معلمك نتائج الطلاب مجمّعة فقط، ولا يرى إجابتك باسمك. تحتاج نحو 3 دقائق، وتُرسل مرة واحدة.</div>
        <div class="actions"><button type="button" class="primary" id="sv-go">ابدأ الاستبانة</button><button type="button" id="sv-back">لاحقًا</button></div></section>`;
      document.getElementById('sv-go').onclick = () => { page = 0; draw(); };
      document.getElementById('sv-back').onclick = done;
      return;
    }
    const last = page === pages.length - 1, cur = pages[page];
    $app.innerHTML = `<section class="card sv-wrap">
      <div class="sv-top"><span class="small muted">${page + 1} من ${pages.length}</span><div class="bar"><span style="width:${Math.round((100 * page) / pages.length)}%"></span></div></div>
      ${cur === 'open' ? `<p class="small muted">سؤالان اختياريان (300 حرف لكل منهما). لا تكتب اسمك أو أسماء غيرك.</p>
        ${OPEN.map((q, k) => `<div class="field"><label for="sv-o${k}">${esc(q)}</label><textarea id="sv-o${k}" dir="auto" maxlength="300" rows="3">${esc(open[k])}</textarea></div>`).join('')}`
      : cur.map(i => `<fieldset class="sv-item"><legend>${esc(ITEMS[i].text)}</legend><div class="sv-scale">
          ${SCALE.map(([v, t]) => `<label class="sv-opt"><input type="radio" name="sv${i}" value="${v}" ${answers[i] === v ? 'checked' : ''}><span>${t}</span></label>`).join('')}</div></fieldset>`).join('')}
      <p class="notice bad small" id="sv-err" hidden></p>
      <div class="actions st-nav">${page > 0 ? `<button type="button" id="sv-prev">السابق</button>` : ''}
        <button type="button" class="primary" id="sv-next">${last ? 'إرسال الإجابة' : 'التالي'}</button></div></section>`;
    $app.querySelectorAll('.sv-opt input').forEach(r => r.onchange = () => { answers[Number(r.name.slice(2))] = Number(r.value); });
    const keepOpen = () => { if (cur === 'open') OPEN.forEach((_, k) => { open[k] = document.getElementById('sv-o' + k).value; }); };
    document.getElementById('sv-prev')?.addEventListener('click', () => { keepOpen(); page--; draw(); });
    document.getElementById('sv-next').onclick = async e => {
      keepOpen();
      if (cur !== 'open' && cur.some(i => answers[i] == null)) { const er = document.getElementById('sv-err'); er.textContent = 'اختر إجابة لكل عبارة'; er.hidden = false; return; }
      if (!last) { page++; draw(); return; }
      const b = e.currentTarget; b.disabled = true;
      try {
        await api('/student/survey', { method: 'POST', body: { id: it.id, answers, open1: open[0], open2: open[1], duration: Math.round((Date.now() - startedAt) / 1000) } });
        toast('وصلت إجابتك، شكرًا لك'); done();
      } catch (err) { b.disabled = false; fail(err); }
    };
    window.scrollTo(0, 0);
  };
  draw();
}

// ---------- واجهة المعلم: نتائج الاستبانة (مجمّعة ودون أسماء) ----------
const pc = x => (Number.isFinite(x) ? Math.round(x) + '%' : '—');
export function surveyResultsHtml(esc, d) {
  const rate = d.sent ? (100 * d.responses) / d.sent : NaN;
  if (d.open) {
    return `<p class="small">استجاب <b>${d.responses}</b> من ${d.sent} طالبًا (${pc(rate)}) حتى الآن. تظهر النتائج بعد إغلاق الاستبانة (${esc(new Date(d.closesAt).toLocaleDateString('ar-SA-u-ca-islamic-umalqura'))})
      أو حين تغلقها بزر «إغلاق الاستبانة»، حتى لا يُستدل على إجابة طالب بعينه.</p>`;
  }
  if (d.responses < MIN_SHOW) {
    return `<p class="small">استجاب ${d.responses} من ${d.sent} طالبًا (${pc(rate)}). تظهر النتائج بعد ${MIN_SHOW} إجابات على الأقل حفاظًا على سرية الطلاب.</p>`;
  }
  const c = clean(d.rows), a = analyzeSurvey(c.kept);
  const removed = c.attention + c.straight + c.speed;
  const secs = Object.entries(d.sectionsSent || {}).map(([sec, n]) => [sec, n, c.kept.filter(r => (r.s ?? '—') === sec).length]);
  return `<div class="sv-res">
    <p class="small">استجاب <b>${d.responses}</b> من ${d.sent} طالبًا (${pc(rate)})${rate < 50 ? ' <span class="badge warn">نسبة استجابة منخفضة: قد لا تمثل النتائج كل الطلاب</span>' : ''}.
      ${removed ? `استُبعدت ${removed} إجابة غير موثوقة (عبارة الانتباه ${c.attention}، الإجابة نفسها لكل العبارات ${c.straight}، أسرع من دقيقة ${c.speed})، فالتحليل على <b>${a.n}</b> إجابة.` : `التحليل على ${a.n} إجابة.`}</p>
    ${a.n < MIN_SHOW ? '<p class="notice warn small">الإجابات الموثوقة أقل من 5؛ لا تُعرض النتائج.</p>' : `
    <div class="table-wrap"><table class="list"><thead><tr><th>البعد</th><th>المتوسط (من 5)</th><th>المستوى</th><th>نسبة المرتفع (≥ 3.5)</th><th>الثبات (ألفا)</th></tr></thead><tbody>
      ${a.dims.map(x => `<tr><td><b>${esc(x.label)}</b> <span class="small muted">(${x.items.length} عبارات)</span></td><td>${fmt(x.mean, 2)} <span class="small muted">± ${fmt(x.sd, 2)}</span></td>
        <td>${esc(x.level)}</td><td>${pc(x.high)}</td><td>${Number.isFinite(x.alpha) ? fmt(x.alpha, 2) + ' · ' : ''}<span class="small">${esc(alphaLabel(x.alpha))}</span></td></tr>`).join('')}
    </tbody></table></div>
    ${a.n < MIN_ALPHA ? `<p class="small muted">الثبات يُحسب من ${MIN_ALPHA} إجابة فأكثر.</p>` : a.n < ALPHA_STABLE ? `<p class="small muted">الثبات محسوب من ${a.n} إجابة؛ يُقرأ تقديرًا أوليًا لأن العينة أقل من ${ALPHA_STABLE}.</p>` : ''}
    <div class="table-wrap"><table class="list sv-items"><thead><tr><th>العبارة</th><th>المتوسط</th><th>الموافقة</th><th>توزيع الإجابات</th></tr></thead><tbody>
      ${a.items.map(x => { const it = a.dims.flatMap(dd => dd.itemTotal).find(t => t.i === x.i);
        return `<tr><td>${esc(x.text)}${x.rev ? ' <span class="badge">عكسية</span>' : ''}${it && Number.isFinite(it.r) && it.r < 0.3 ? ' <span class="badge warn" title="ارتباطها ضعيف بباقي عبارات بعدها">تراجع صياغتها</span>' : ''}</td>
          <td>${fmt(x.mean, 2)}</td><td>${pc(x.agree)}</td>
          <td><span class="sv-dist" role="img" aria-label="${SCALE.map(([, t], k) => `${t} ${Math.round(x.dist[k])}%`).join('، ')}">${x.dist.map((p, k) => `<i class="sv-d${k}" style="width:${p}%"></i>`).join('')}</span></td></tr>`; }).join('')}
    </tbody></table></div>
    <p class="sv-legend small muted">${SCALE.map(([, t], k) => `<i class="sv-d${k}"></i>${t}`).join(' ')}</p>
    ${secs.length > 1 ? `<p class="small"><b>الاستجابة حسب الشعبة:</b> ${secs.map(([s, n, k]) => `${esc(s)}: ${k >= MIN_SHOW ? `${k} من ${n}` : 'أقل من 5'}`).join(' · ')}</p>` : ''}
    ${[d.open1, d.open2].map((list, k) => list.length ? `<details class="sv-open"><summary>${esc(OPEN[k])} <span class="small muted">(${list.length})</span></summary>
      <ul>${list.map(t => `<li>${esc(t)}</li>`).join('')}</ul></details>` : '').join('')}
    <div class="actions no-print"><button type="button" class="sv-print">طباعة / حفظ PDF</button></div>
    <p class="small muted">الأداة: مقتبسة ومعدّلة عن Davis (1989) وPintrich et al. (1991) وRovai et al. (2009)، ليكرت خماسي. المستوى: 1–1.80 منخفض جدًا، 1.81–2.60 منخفض، 2.61–3.40 متوسط، 3.41–4.20 مرتفع، 4.21–5 مرتفع جدًا. العبارات العكسية أُعيد ترميزها. هذه نتائج إدراك الطلاب وتدعم نتائج الاختبار القبلي والبعدي ولا تحل محلها.</p>`}
  </div>`;
}

// ---------- التقرير المطبوع (A4): وثيقة رسمية بالشعار، تُتاح بعد إغلاق الاستبانة ومن 5 إجابات ----------
const hdate = (v, long) => new Date(v).toLocaleDateString('ar-SA-u-ca-islamic-umalqura-nu-latn', long ? { day: 'numeric', month: 'long', year: 'numeric' } : undefined);
export function printSurveyReport(esc, d, meta = {}) {
  const c = clean(d.rows), a = analyzeSurvey(c.kept), rate = d.sent ? (100 * d.responses) / d.sent : NaN;
  const removed = c.attention + c.straight + c.speed, today = hdate(Date.now(), true);
  const secs = Object.entries(d.sectionsSent || {}).map(([sec, n]) => [sec, n, c.kept.filter(r => (r.s ?? '—') === sec).length]);
  const row = cells => `<tr>${cells.map(x => `<td>${x}</td>`).join('')}</tr>`;
  const table = (heads, rows, cls = '') => `<table class="rp-t ${cls}"><thead><tr>${heads.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table>`;
  const best = [...a.dims].sort((x, y) => y.mean - x.mean)[0], low = [...a.items].sort((x, y) => x.mean - y.mean)[0];
  let n = 0; const sec = t => `<h2 class="rp-h">${++n}. ${esc(t)}</h2>`;
  document.querySelector('.pr-report')?.remove();
  const art = document.createElement('article');
  art.className = 'pr-report sv-report'; art.dir = 'rtl';
  art.innerHTML = `<header class="rp-cover">
    <div class="rp-brand"><img src="assets/itqan-mark.svg" alt="" width="54" height="54"><div><b>منصة إتقان</b><span>بنك الأسئلة والتدريب في الكيمياء</span></div></div>
    <div class="rp-title"><span class="rp-kicker">تقرير نتائج استبانة الطلاب</span><h1>${esc(d.title)}</h1><p>استبانة إدراك الطلاب لأثر التدريب على المنصة في تعلّمهم</p></div>
    <dl class="rp-meta">
      <div><dt>تاريخ الإرسال</dt><dd>${esc(hdate(d.createdAt))}</dd></div><div><dt>تاريخ الإغلاق</dt><dd>${esc(hdate(d.closesAt))}</dd></div><div><dt>تاريخ التقرير</dt><dd>${esc(today)}</dd></div>
      <div><dt>أُرسلت إلى</dt><dd>${d.sent} طالبًا</dd></div><div><dt>الاستجابات</dt><dd>${d.responses} (${pc(rate)})</dd></div><div><dt>الإجابات الموثوقة</dt><dd>${a.n}</dd></div>
    </dl></header>
  ${sec('الخلاصة')}
  <div class="rp-figs">${a.dims.map(x => `<div><b>${fmt(x.mean, 2)}</b><span>${esc(x.label)} · ${esc(x.level)}</span></div>`).join('')}</div>
  <div class="rp-box">استجاب ${d.responses} من ${d.sent} طالبًا (${pc(rate)})${removed ? `، واستُبعدت ${removed} إجابة غير موثوقة (أخطأ في عبارة الانتباه ${c.attention}، والإجابة نفسها لكل العبارات ${c.straight}، وأسرع من دقيقة ${c.speed})` : ''}، فبُني التحليل على ${a.n} إجابة.
    أعلى الأبعاد «${esc(best.label)}» بمتوسط ${fmt(best.mean, 2)} من 5 (${esc(best.level)})، وأدنى العبارات: «${esc(low.text)}» (${fmt(low.mean, 2)}).
    ${rate < 50 ? '<b>تنبيه:</b> نسبة الاستجابة أقل من 50%، فقد لا تمثل النتائج كل الطلاب.' : ''}</div>
  ${sec('نتائج الأبعاد')}
  ${table(['البعد', 'العبارات', 'المتوسط (من 5)', 'الانحراف المعياري', 'المستوى', 'نسبة المرتفع (≥ 3.5)', 'الثبات (ألفا كرونباخ)'],
    a.dims.map(x => row([esc(x.label), x.items.length, fmt(x.mean, 2), fmt(x.sd, 2), esc(x.level), pc(x.high), Number.isFinite(x.alpha) ? `${fmt(x.alpha, 2)} · ${esc(alphaLabel(x.alpha))}` : esc(alphaLabel(x.alpha))])), 'rp-num rp-keep')}
  ${a.n < MIN_ALPHA ? `<p class="rp-small">يُحسب الثبات من ${MIN_ALPHA} إجابة فأكثر.</p>` : a.n < ALPHA_STABLE ? `<p class="rp-small">الثبات محسوب من ${a.n} إجابة موثوقة؛ يُقرأ تقديرًا أوليًا لأن العينة أقل من ${ALPHA_STABLE}.</p>` : ''}
  ${sec('نتائج العبارات')}
  ${table(['م', 'العبارة', 'المتوسط', 'الموافقة', 'توزيع الإجابات'], a.items.map((x, k) => row([k + 1, esc(x.text) + (x.rev ? ' <span class="rp-muted">(عكسية)</span>' : ''), fmt(x.mean, 2), pc(x.agree),
    `<span class="sv-dist">${x.dist.map((p, j) => `<i class="sv-d${j}" style="width:${p}%"></i>`).join('')}</span>`])), 'rp-num')}
  <p class="rp-small">المتوسط بعد إعادة ترميز العبارات العكسية (كلما ارتفع كان أفضل)؛ أما «الموافقة» فهي نسبة من اختار «أوافق» أو «أوافق بشدة» على نص العبارة كما هو، فانخفاضها في العبارة العكسية نتيجة إيجابية.</p>
  <p class="rp-legend">${SCALE.map(([, t], k) => `<i class="sv-d${k} sv-key"></i>${t}`).join(' ')}</p>
  ${secs.length > 1 ? `<p class="rp-small"><b>الاستجابة حسب الشعبة:</b> ${secs.map(([s, nn, k]) => `${esc(s)}: ${k >= MIN_SHOW ? `${k} من ${nn}` : 'أقل من 5'}`).join(' · ')}</p>` : ''}
  ${(d.open1.length || d.open2.length) ? `${sec('الإجابات المفتوحة')}${[d.open1, d.open2].map((list, k) => list.length ? `<p class="rp-small"><b>${esc(OPEN[k])}</b> (${list.length})</p><ul class="rp-list">${list.map(t => `<li>${esc(t)}</li>`).join('')}</ul>` : '').join('')}` : ''}
  ${sec('الأداة والمنهجية')}
  <ul class="rp-list">
    <li><b>الأداة:</b> ${ITEMS.length - 1} عبارة بمقياس ليكرت الخماسي في أربعة أبعاد، وعبارة انتباه، وسؤالان مفتوحان؛ مقتبسة ومعدّلة عن Davis (1989) وPintrich et al. (1991) وRovai et al. (2009).</li>
    <li><b>التطبيق:</b> إلكترونيًا عبر المنصة، إجابة واحدة لكل طالب دون تعديل، وبسرية تامة؛ النتائج مجمّعة دون أسماء.</li>
    <li><b>التنظيف:</b> استبعاد من أخطأ في عبارة الانتباه، ومن أعطى الإجابة نفسها لكل العبارات، ومن أنهى في أقل من دقيقة.</li>
    <li><b>التفسير:</b> العبارات العكسية أُعيد ترميزها؛ المستوى: 1–1.80 منخفض جدًا، 1.81–2.60 منخفض، 2.61–3.40 متوسط، 3.41–4.20 مرتفع، 4.21–5 مرتفع جدًا.</li>
    <li><b>الحدود:</b> نتائج إدراك الطلاب تدعم نتائج الاختبار القبلي والبعدي ولا تحل محلها.</li>
  </ul>
  <footer class="rp-sign">${['معلم المادة', 'المشرف التربوي', 'قائد المدرسة'].map(t => `<div><span>${t}</span><p>الاسم: ............................</p><p>التوقيع: ..........................</p></div>`).join('')}</footer>
  <p class="rp-foot">صدر هذا التقرير من منصة إتقان في ${esc(today)}${meta.sender ? ` · المرسل: ${esc(meta.sender)}` : ''} · رمز الاستبانة ${d.id}</p>`;
  document.body.append(art);
  document.body.classList.add('pr-printing');
  const done = () => { document.body.classList.remove('pr-printing'); art.remove(); window.removeEventListener('afterprint', done); };
  window.addEventListener('afterprint', done);
  window.print();
}
