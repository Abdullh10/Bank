// قسم «الاستعداد للتحصيلي»: المعرفات الثابتة وفحص الأسئلة (يستعمله scripts/build-tahsili-seed.js والاختبارات).
import fs from 'node:fs';
import path from 'node:path';
import { okImage, MAX_IMAGES } from '../public/media.js';

export const COURSE = 5;
// المعرفات (لا تتقاطع مع المقررات الأخرى): الفصل = المادة، والدرس = الوحدة، والهدف = الموضوع
export const subjectId = s => COURSE * 100 + s;                                 // 501…504
export const unitId = (s, u) => COURSE * 10000 + s * 100 + u;                   // 50201…
export const topicId = (s, u, t) => COURSE * 1000000 + s * 10000 + u * 100 + t; // 5020101…
export const topicCode = (s, u, t) => `T-S${s}-U${String(u).padStart(2, '0')}-T${String(t).padStart(2, '0')}`;

const LEVELS = ['تذكر', 'فهم', 'تطبيق', 'تحليل', 'تقويم', 'إبداع'];
const DIFFS = ['سهل', 'متوسط', 'صعب'];
// علامات $ غير المهربة يجب أن تكون أزواجًا (صيغة مفتوحة لم تُغلق تظهر للطالب نصًا خامًا)
const unbalanced = s => ((String(s ?? '').replace(/\\\$/g, '').match(/\$/g) || []).length % 2) === 1;

// أخطاء سؤال واحد (مصفوفة نصوص؛ فارغة = سليم). publicDir للتحقق من وجود صور qimg/.
export function checkQuestion(q, { topics = [1], publicDir = null } = {}) {
  const e = [];
  const str = v => typeof v === 'string' && v.trim() !== '';
  if (!str(q.stem) || q.stem.trim().length < 8) e.push('نص السؤال قصير أو مفقود');
  if (!Array.isArray(q.options) || q.options.length !== 4) e.push('أربعة بدائل مطلوبة');
  else {
    if (!q.options.every(str)) e.push('بديل فارغ');
    if (new Set(q.options.map(o => String(o).trim())).size !== 4) e.push('بديلان متطابقان');
  }
  if (!Number.isInteger(q.correct_index) || q.correct_index < 0 || q.correct_index > 3) e.push('رقم الإجابة الصحيحة بين 0 و3');
  if (!str(q.explanation)) e.push('التفسير مطلوب');
  const dn = q.distractor_notes;
  if (!Array.isArray(dn) || dn.length !== 4) e.push('أربع ملاحظات للبدائل مطلوبة (الصحيح فارغ)');
  else if (Number.isInteger(q.correct_index)) {
    if (str(dn[q.correct_index])) e.push('ملاحظة البديل الصحيح يجب أن تكون فارغة');
    if (dn.some((n, i) => i !== q.correct_index && !str(n))) e.push('سبب خطأ كل بديل خاطئ مطلوب');
  }
  if (!LEVELS.includes(q.thinking_level)) e.push('مستوى التفكير غير صالح');
  if (!DIFFS.includes(q.difficulty)) e.push('درجة الصعوبة غير صالحة');
  if (!topics.includes(q.topic ?? 1)) e.push(`الموضوع ${q.topic} غير موجود في الوحدة`);
  if (q.year != null && !(Number.isInteger(q.year) && q.year >= 2000 && q.year <= 2100)) e.push('سنة الورود رقم بين 2000 و2100 (أو تُترك فارغة)');
  for (const [k, v] of [['نص السؤال', q.stem], ['التفسير', q.explanation], ...(q.options || []).map((o, i) => [`البديل ${i + 1}`, o]),
    ...(dn || []).map((n, i) => [`ملاحظة البديل ${i + 1}`, n])]) if (unbalanced(v)) e.push(`${k}: علامة $ بلا نظير`);
  if (q.images != null) {
    if (!Array.isArray(q.images) || q.images.length > MAX_IMAGES) e.push(`الصور قائمة من ${MAX_IMAGES} على الأكثر`);
    else for (const im of q.images) {
      if (!okImage(im)) e.push(`مصدر صورة غير مسموح: ${im?.src}`);
      else if (publicDir && im.src.startsWith('qimg/') && !fs.existsSync(path.join(publicDir, im.src))) e.push(`ملف الصورة غير موجود: public/${im.src}`);
    }
  }
  return e;
}
