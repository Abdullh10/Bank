// صور السؤال: [{src, alt}] تُعرض بعد نص السؤال. المصدر مسار ثابت في الموقع (qimg/…) أو ملف في مخزن Supabase «question-media».
// القاعدة نفسها تفرضها قاعدة البيانات (_validate_question)؛ هنا لعرض ما هو مسموح فقط ولتوضيح الأخطاء مبكرًا.
export const IMG_SRC = /^(qimg\/[A-Za-z0-9._/-]+\.(png|jpe?g|webp|gif|svg)|https:\/\/[a-z0-9]+\.supabase\.co\/storage\/v1\/object\/public\/question-media\/[A-Za-z0-9._/-]+\.(png|jpe?g|webp|gif))$/;
export const MAX_IMAGES = 4;
// الوصف البديل قد يصف المخطط كاملًا (لقارئ الشاشة)؛ القصير يُعرض تعليقًا تحت الصورة والطويل يبقى وصفًا بديلًا فقط
export const MAX_ALT = 1000, CAPTION_MAX = 200;
export const okImage = im => !!im && typeof im.src === 'string' && IMG_SRC.test(im.src) && !im.src.includes('..') && String(im.alt ?? '').length <= MAX_ALT;

const escAttr = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// HTML الصور (cls لتنسيق كل صفحة)؛ الصورة غير المسموحة لا تُعرض
export function qImages(images, cls = 'q-figs') {
  const list = (Array.isArray(images) ? images : []).filter(okImage);
  if (!list.length) return '';
  return `<div class="${cls}">${list.map(im => `<figure class="q-fig"><img src="${escAttr(im.src)}" alt="${escAttr(im.alt || 'شكل مرفق بالسؤال')}" decoding="async">${im.alt && im.alt.length <= CAPTION_MAX ? `<figcaption>${escAttr(im.alt)}</figcaption>` : ''}</figure>`).join('')}</div>`;
}
