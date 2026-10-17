// تعدد المقررات: الصفحة الأولى بعد الدخول (بطاقة لكل مقرر)، وتذكّر المقرر المختار على هذا الجهاز.
// المقرر «قيد الإعداد» يفتحه مالك المشروع فقط ليتابع إعداده؛ ويظهر لغيره باهتًا.
import { icon, line } from './icons.js';

const KEY = 'itqan-course';
const num = n => Number(n || 0).toLocaleString('ar-SA-u-nu-latn');
const pct = (a, b) => (b ? Math.round((100 * (a || 0)) / b) : 0);
// لون بطاقة كل صف
const TONE = { 'الأول الثانوي': 'teal', 'الثاني الثانوي': 'navy', 'الثالث الثانوي': 'gold' };

export const rememberedCourse = () => { try { return Number(localStorage.getItem(KEY)) || null; } catch { return null; } };
export const rememberCourse = id => { try { localStorage.setItem(KEY, String(id)); } catch { /* التخزين غير متاح */ } };

// المقرر الذي يُعرض: المختار سابقًا إن كان متاحًا لهذا الحساب، وإلا أول مقرر جاهز
export function pickCourse(list, wanted, isOwner) {
  const usable = c => c && (c.status === 'ready' || isOwner);
  return [wanted, rememberedCourse()].map(id => list.find(c => c.id === id)).find(usable)
    || list.find(c => c.status === 'ready') || list[0] || null;
}

export const courseLine = c => (c ? `${c.code} · الصف ${c.grade} · الفصل الدراسي ${c.term}` : '');

export function pageCourses(ctx) {
  const { esc, $app, courses, current, isOwner, select } = ctx;
  const card = c => {
    const ready = c.status === 'ready', open = ready || isOwner, isCur = current?.id === c.id;
    return `<article class="course-card ${ready ? '' : 'preparing'} ${isCur ? 'current' : ''}" ${open ? '' : 'aria-disabled="true"'}>
      <div class="cc-head">${icon('chapters', 54, TONE[c.grade] || 'navy')}
        <div><h2>${esc(c.code)}</h2><p>الصف ${esc(c.grade)}<br>الفصل الدراسي ${esc(c.term)}</p></div></div>
      <div class="cc-status">${ready ? `<span class="badge ok">${line('check', 14)} متاح</span>` : `<span class="badge warn">${line('clock', 14)} قيد الإعداد</span>`}
        ${isCur ? '<span class="badge brand">المقرر الحالي</span>' : ''}</div>
      ${ready ? `<dl class="cc-nums"><div><dt>هدفًا</dt><dd>${num(c.objectives)}</dd></div><div><dt>سؤالًا</dt><dd>${num(c.questions)}</dd></div>
          <div><dt>معتمدة</dt><dd>${pct(c.approved, c.questions)}%</dd></div><div><dt>طالبًا</dt><dd>${num(c.students)}</dd></div></dl>`
        : `<p class="small muted cc-note">${c.eta ? `متوقع: ${esc(c.eta)}` : 'يُضاف محتواه قريبًا: الأهداف وبنك الأسئلة والتدريب.'}</p>`}
      ${open ? `<button type="button" class="${ready ? 'primary' : ''}" data-course="${c.id}">${ready ? 'دخول المقرر' : 'متابعة الإعداد (للمالك)'}</button>` : ''}
    </article>`;
  };
  $app.innerHTML = `
    <div class="hero banner courses-hero">
      <div class="hero-ic"><img class="banner-mark" src="assets/itqan-mark.svg" alt="" width="74" height="74">
        <div><span class="eyebrow">${icon('spark', 18)} إتقان · منصة بنك الأسئلة والتدريب في الكيمياء</span><h1>مقررات الكيمياء</h1>
          <p class="muted">اختر المقرر لتصفح أهدافه وبنك أسئلته وإنشاء اختباراته.</p></div></div>
      ${current?.status === 'ready' || (current && isOwner) ? `<div class="actions no-print"><button type="button" class="primary" data-course="${current.id}">${line('next', 17)}متابعة ${esc(current.code)}</button></div>` : ''}
    </div>
    <div class="course-grid">${courses.map(card).join('')}</div>`;
  $app.querySelectorAll('[data-course]').forEach(b => b.onclick = () => select(Number(b.dataset.course), true));
}
