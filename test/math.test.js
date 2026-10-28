// الرموز الرياضية (public/math.js) وصور الأسئلة (public/media.js)
import test from 'node:test';
import assert from 'node:assert/strict';
import { hasMath, tokenize, texToText, plainMath, normTex } from '../public/math.js';
import { okImage, qImages } from '../public/media.js';
import { cleanQuestion } from '../public/validate.js';

test('صيغة داخل السطر وصيغة في سطر مستقل', () => {
  assert.deepEqual(tokenize('احسب $x^2$ إذا'), [{ math: false, v: 'احسب ' }, { math: true, v: 'x^2', display: false }, { math: false, v: ' إذا' }]);
  assert.deepEqual(tokenize('$$\\int_0^1 x\\,dx$$'), [{ math: true, v: '\\int_0^1 x\\,dx', display: true }]);
});
test('علامة دولار مفردة أو مهربة ليست صيغة', () => {
  assert.equal(hasMath('السعر 5$ فقط'), false);
  assert.equal(hasMath('من \\$5 إلى \\$9'), false);
  assert.deepEqual(tokenize('من \\$5 إلى \\$9'), [{ math: false, v: 'من $5 إلى $9' }]);
  assert.equal(hasMath('$x$'), true);
});
test('الصيغة داخل السطر لا تمتد عبر سطر جديد', () => {
  assert.equal(tokenize('a $b\nc$ d').some(t => t.math), false);
});
test('تحويل الصيغة إلى نص مقروء (ملف Word)', () => {
  assert.equal(texToText('\\frac{1}{2}'), '(1)/(2)');
  assert.equal(texToText('x^{2} + y_1'), 'x² + y₁');
  assert.equal(texToText('\\sqrt{x-3}'), '√(x-3)');
  assert.equal(texToText('\\int_0^1 f \\, dx'), '∫₀¹ f dx');
  assert.equal(texToText('c = \\frac{Q}{m\\,\\Delta T}'), 'c = (Q)/(m Δ T)');
  assert.equal(texToText('\\sin 135^\\circ'), 'sin 135°');
  assert.equal(texToText('\\lim_{x \\to 2} \\sqrt{x}'), 'lim_(x → 2) √(x)');
  assert.equal(plainMath('قيمة $\\frac{3}{4}$ تقريبًا'), 'قيمة (3)/(4) تقريبًا');
  assert.equal(plainMath('نص عادي'), 'نص عادي');
  assert.equal(plainMath(null), '');
});
test('مصادر الصور المسموحة فقط', () => {
  assert.equal(okImage({ src: 'qimg/tahsili/phys-01.png', alt: 'دائرة' }), true);
  assert.equal(okImage({ src: 'qimg/a.svg' }), true);
  assert.equal(okImage({ src: 'https://znisbyqyygdholobhohu.supabase.co/storage/v1/object/public/question-media/q/1f2e.webp' }), true);
  for (const src of ['https://evil.example/x.png', 'http://znisbyqyygdholobhohu.supabase.co/storage/v1/object/public/question-media/q/a.png',
    'https://x.supabase.co/storage/v1/object/public/question-media/q/a.svg', 'qimg/../config.js', 'qimg/a.png?x=1', 'javascript:alert(1)',
    'data:image/png;base64,AAAA', '/qimg/a.png', 'qimg/a.png" onerror="x'])
    assert.equal(okImage({ src }), false, src);
  assert.equal(okImage({ src: 'qimg/a.png', alt: 'x'.repeat(201) }), false);
});
test('الصور تُعرض مهرّبة، وغير المسموحة لا تُعرض', () => {
  const html = qImages([{ src: 'qimg/a.png', alt: 'وعاء <b>' }, { src: 'https://evil.example/x.png' }]);
  assert.equal((html.match(/<img /g) || []).length, 1);
  assert.ok(html.includes('alt="وعاء &lt;b&gt;"'));
  assert.equal(qImages(null), '');
});
test('التحقق قبل الحفظ يرفض صورة غير مسموحة أو أكثر من أربع', () => {
  const base = { stem: 'ما الشكل المناسب للتجربة؟', options: ['أ', 'ب', 'ج'], correct_index: 0, explanation: 'تفسير' };
  assert.throws(() => cleanQuestion({ ...base, images: [{ src: 'https://evil.example/x.png' }] }, 'mcq'), /مصدر صورة/);
  assert.throws(() => cleanQuestion({ ...base, images: Array(5).fill({ src: 'qimg/a.png' }) }, 'mcq'), /4 على الأكثر/);
  assert.deepEqual(cleanQuestion({ ...base, images: [{ src: 'qimg/a.png', alt: '  شكل  ١ ' }] }, 'mcq').images, [{ src: 'qimg/a.png', alt: 'شكل ١' }]);
  assert.equal('images' in cleanQuestion(base, 'mcq'), false);
});
test('نقطة الضرب داخل الوحدات تصير \\cdot', () => {
  assert.equal(normTex('40\\,\\text{J/(kg·°C)}'), '40\\,\\text{J/(kg}\\cdot\\text{°C)}');
  assert.equal(normTex('a·b'), 'a\\cdot b');
  assert.equal(normTex('\\text{kg}'), '\\text{kg}');
});
