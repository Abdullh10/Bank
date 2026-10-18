// عزل الاتجاه (public/bidi.js): الأرقام والصيغ والمعادلات وأشكال المربعات تبقى بترتيبها من اليسار داخل النص العربي.
import test from 'node:test';
import assert from 'node:assert/strict';
import { isolate } from '../public/bidi.js';

const LRI = '⁦', PDI = '⁩';
const wrap = s => LRI + s + PDI;

test('مقطع لاتيني خالص فيه رموز يُعزل كله (خيار «1s [↑↓]  2s [↑]»)', () => {
  assert.equal(isolate('1s [↑↓]  2s [↑]'), wrap('1s [↑↓]  2s [↑]'));
});
test('الأسهم والأقواس والقسمة والجذر والخط العمودي تبقى ضمن مقطع واحد', () => {
  assert.equal(isolate('النسبة = (105 ÷ 300) × 100 = 35% ثم'), `النسبة = ${wrap('(105 ÷ 300) × 100 = 35%')} ثم`);
  assert.equal(isolate('يمتلئ 1s بإلكترونين (↑↓) ثم'), `يمتلئ ${wrap('1s')} بإلكترونين ${wrap('(↑↓)')} ثم`);
  assert.equal(isolate('معدل = √(4 ÷ 28) أي'), `معدل = ${wrap('√(4 ÷ 28)')} أي`);
  assert.equal(isolate('رمز Zn | Zn²⁺(1M) || Cu²⁺(1M) | Cu يفصل'), `رمز ${wrap('Zn | Zn²⁺(1M) || Cu²⁺(1M) | Cu')} يفصل`);
  assert.equal(isolate('n + 2(−1) = 0 ⇒ +2 ثم'), `${wrap('n + 2(−1) = 0 ⇒ +2')} ثم`);
});
test('الأرقام مع وحداتها وصيغ التفاعل', () => {
  assert.equal(isolate('تركيز 0.10 M عند 25 °C'), `تركيز ${wrap('0.10 M')} عند ${wrap('25 °C')}`);
  assert.equal(isolate('2H₂ + O₂ → 2H₂O ينتج'), `${wrap('2H₂ + O₂ → 2H₂O')} ينتج`);
});
test('لا يتغير نص عربي بلا لاتيني، ولا رقم مفرد بلا رموز، ولا نص معزول سابقًا', () => {
  assert.equal(isolate('نص عربي فقط'), 'نص عربي فقط');
  assert.equal(isolate('12'), '12');
  assert.equal(isolate(wrap('x')), wrap('x'));
});

test('قوس بلا نظيره داخل المقطع يبقى خارج العزل (درجات السؤال «(20 درجة)»)', () => {
  assert.equal(isolate('السؤال الأول (20 درجة)'), `السؤال الأول (${wrap('20')} درجة)`);
  assert.equal(isolate('(5 درجات) ثم'), `(${wrap('5')} درجات) ثم`);
  assert.equal(isolate('(طبعة 1447) الكتاب'), `(طبعة ${wrap('1447')}) الكتاب`);
  assert.equal(isolate('(1) و(2) ثم'), `${wrap('(1)')} و${wrap('(2)')} ثم`);
});
