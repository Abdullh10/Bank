// التاريخ الهجري بترتيب ثابت: يوم شهر سنةهـ
import test from 'node:test';
import assert from 'node:assert/strict';
import { hijri } from '../public/dates.js';

test('الترتيب: اليوم ثم اسم الشهر ثم السنة ثم «هـ»', () => {
  assert.match(hijri('2026-10-18T12:00:00Z'), /^\d{1,2} \S+( \S+)? 1448هـ$/);
});
test('مع الوقت', () => {
  assert.match(hijri('2026-10-18T12:00:00Z', true), /^\d{1,2} \S+( \S+)? 1448هـ · \d{1,2}:\d{2}/);
});
test('قيمة فارغة أو غير صالحة', () => {
  assert.equal(hijri(null), '—');
  assert.equal(hijri('xx'), '—');
});
