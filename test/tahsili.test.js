// قسم «الاستعداد للتحصيلي»: المعرفات الثابتة وفحص الأسئلة (scripts/tahsili-lib.js)
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { subjectId, unitId, topicId, topicCode, checkQuestion } from '../scripts/tahsili-lib.js';

const good = {
  stem: 'ما طاقة فوتون تردده $5\\times10^{14}$ Hz؟', options: ['$3.3\\times10^{-19}$ J', 'ب', 'ج', 'د'], correct_index: 0,
  explanation: '$E = h\\nu$', distractor_notes: ['', 'س1', 'س2', 'س3'], thinking_level: 'تطبيق', difficulty: 'متوسط',
};

test('المعرفات لا تتقاطع مع المقررات الأخرى وتتسع لـ 99 وحدة', () => {
  assert.equal(subjectId(2), 502);
  assert.equal(unitId(2, 11), 50211);
  assert.equal(unitId(4, 99), 50499);
  assert.equal(topicId(2, 11, 1), 5021101);
  assert.equal(topicCode(2, 11, 1), 'T-S2-U11-T01');
  assert.ok(unitId(1, 1) > 4999 && topicId(1, 1, 1) > 404312); // أكبر من معرفات كيمياء 3
});
test('سؤال سليم بلا أخطاء', () => assert.deepEqual(checkQuestion(good), []));
test('أربعة بدائل مختلفة غير فارغة', () => {
  assert.match(checkQuestion({ ...good, options: ['أ', 'ب', 'ج'] }).join(), /أربعة بدائل/);
  assert.match(checkQuestion({ ...good, options: ['أ', 'ب', 'ب', 'د'] }).join(), /متطابقان/);
  assert.match(checkQuestion({ ...good, options: ['أ', '', 'ج', 'د'] }).join(), /بديل فارغ/);
});
test('مفتاح الإجابة وملاحظات البدائل متسقة', () => {
  assert.match(checkQuestion({ ...good, correct_index: 4 }).join(), /بين 0 و3/);
  assert.match(checkQuestion({ ...good, distractor_notes: ['خطأ', 'س1', 'س2', 'س3'] }).join(), /الصحيح يجب أن تكون فارغة/);
  assert.match(checkQuestion({ ...good, distractor_notes: ['', '', 'س2', 'س3'] }).join(), /سبب خطأ كل بديل/);
  assert.match(checkQuestion({ ...good, explanation: ' ' }).join(), /التفسير مطلوب/);
});
test('المستوى والصعوبة والموضوع', () => {
  assert.match(checkQuestion({ ...good, thinking_level: 'حفظ' }).join(), /مستوى التفكير/);
  assert.match(checkQuestion({ ...good, difficulty: 'صعب جدا' }).join(), /الصعوبة/);
  assert.match(checkQuestion({ ...good, topic: 2 }, { topics: [1] }).join(), /الموضوع 2/);
});
test('صيغة مفتوحة بلا إغلاق تُكتشف، والدولار المهرّب مسموح', () => {
  assert.match(checkQuestion({ ...good, stem: 'إذا كانت $v = \\lambda f فما السرعة؟' }).join(), /نص السؤال: علامة \$/);
  assert.deepEqual(checkQuestion({ ...good, stem: 'سعر الكتاب \\$5 فكم سعر كتابين؟' }), []);
  assert.match(checkQuestion({ ...good, options: ['$1', 'ب', 'ج', 'د'] }).join(), /البديل 1: علامة \$/);
});
test('الصور: المصدر المسموح ووجود الملف', () => {
  assert.match(checkQuestion({ ...good, images: [{ src: 'https://evil.example/a.png' }] }).join(), /غير مسموح/);
  const dir = fs.mkdtempSync('/tmp/tahsili-');
  assert.match(checkQuestion({ ...good, images: [{ src: 'qimg/tahsili/x.png' }] }, { publicDir: dir }).join(), /غير موجود/);
  fs.mkdirSync(`${dir}/qimg/tahsili`, { recursive: true }); fs.writeFileSync(`${dir}/qimg/tahsili/x.png`, '');
  assert.deepEqual(checkQuestion({ ...good, images: [{ src: 'qimg/tahsili/x.png', alt: 'شكل' }] }, { publicDir: dir }), []);
  fs.rmSync(dir, { recursive: true });
});
test('ملف البنية: المواد الأربع بترتيب الدليل وأرقام وحدات صالحة', () => {
  const u = JSON.parse(fs.readFileSync(new URL('../data/tahsili/units.json', import.meta.url)));
  assert.deepEqual(u.subjects.map(s => s.title), ['الأحياء والبيئة', 'الكيمياء', 'الفيزياء', 'الرياضيات']);
  for (const s of u.subjects) {
    const nums = s.units.map(x => x.number);
    assert.equal(new Set(nums).size, nums.length, `${s.title}: رقم وحدة مكرر`);
    assert.ok(nums.every(n => n >= 1 && n <= 99));
    assert.ok(s.units.every(x => x.topics.length >= 1));
  }
});
