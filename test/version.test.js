// ختم الإصدار محدَّث: أي تعديل على public/*.js أو styles.css دون تشغيل scripts/stamp-version.js يُفشل هذا الاختبار،
// حتى لا يُنشر ملف جديد برابط إصدار قديم فيبقى المتصفح على النسخة المحفوظة.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';

test('index.html و version.json مختومان بإصدار الملفات الحالي', () => {
  assert.doesNotThrow(() => execFileSync(process.execPath, ['scripts/stamp-version.js', '--check'], { stdio: 'pipe' }));
});
