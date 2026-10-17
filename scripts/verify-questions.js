// تحقق آلي عميق من ملفات الأسئلة (يكمّل check-questions.js): node scripts/verify-questions.js --course chem3 [رموز...]
// يعلّم الأسئلة التي تستحق مراجعة بشرية/وكيل: تعارض المفتاح مع التفسير، بدائل متشابهة، موضع الإجابة، وغيرها.
// لا يحكم علميًا؛ يخرج تقريرًا بالأسئلة المشكوك فيها فقط.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { similarity, tokens } from '../public/validate.js';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = process.argv.slice(2);
const ci = args.indexOf('--course');
const course = ci >= 0 ? args.splice(ci, 2)[1] : '';
const dir = path.join(root, 'data', course, 'questions');
const ids = args.length ? args : fs.readdirSync(dir).filter(f => f.endsWith('.json')).map(f => f.slice(0, -5));

const strip = s => String(s || '').replace(/[ً-ْـ]/g, '').replace(/[^\p{L}\p{N}.+\-×⁰-⁹₀-₉]/gu, ' ').replace(/\s+/g, ' ').trim();
const flags = [];
const flag = (id, tag, kind, msg) => flags.push({ id, q: tag, kind, msg });
const nums = s => (String(s).match(/\d+(?:\.\d+)?/g) || []);

for (const id of ids) {
  const d = JSON.parse(fs.readFileSync(path.join(dir, id + '.json'), 'utf8'));
  d.mcq.forEach((q, i) => {
    const tag = `mcq${i + 1}`, k = q.correct_index, key = q.options[k];
    // 1) هل يذكر التفسير نص البديل الصحيح (أو أكثر كلماته)؟ وهل يذكر بديلًا خاطئًا بنصه كاملًا ويرفضه؟
    const ex = strip(q.explanation), ktok = tokens(key);
    const cover = ktok.size ? [...ktok].filter(w => ex.includes(w)).length / ktok.size : 1;
    if (ktok.size >= 4 && cover < 0.34) flag(id, tag, 'key-vs-explanation', `التفسير يغطي ${Math.round(cover * 100)}% من كلمات البديل الصحيح`);
    q.options.forEach((o, j) => {
      if (j === k) return;
      const t = tokens(o);
      const c = t.size ? [...t].filter(w => ex.includes(w)).length / t.size : 0;
      if (t.size >= 3 && c === 1 && cover < 1) flag(id, tag, 'distractor-in-explanation', `التفسير يذكر نص البديل «${'أبجد'[j]}» كاملًا بينما الصحيح «${'أبجد'[k]}»`);
    });
    // 2) أرقام: الأرقام في البديل الصحيح تظهر في التفسير؟
    const kn = nums(key);
    if (kn.length && !kn.every(n => q.explanation.includes(n))) flag(id, tag, 'number-mismatch', `أرقام البديل الصحيح (${kn.join('، ')}) غير مذكورة كلها في التفسير`);
    // 3) ملاحظات البدائل
    const emp = q.distractor_notes.map((n, j) => (String(n).trim() ? -1 : j)).filter(j => j >= 0);
    if (emp.length !== 1 || emp[0] !== k) flag(id, tag, 'notes', 'موضع الملاحظة الفارغة لا يطابق المفتاح');
    // 4) بدائل متشابهة جدًا (قد يكون اثنان صحيحين)
    for (let a = 0; a < q.options.length; a++) for (let b = a + 1; b < q.options.length; b++)
      if (tokens(q.options[a]).size >= 5 && tokens(q.options[b]).size >= 5 && similarity(q.options[a], q.options[b]) >= 0.85) flag(id, tag, 'similar-options', `البديلان ${'أبجد'[a]} و${'أبجد'[b]} متشابهان جدًا`);
    // 5) البديل الصحيح هو الأطول بهامش واضح (تحيز شائع)
    const L = q.options.map(o => strip(o).length), mx = Math.max(...L);
    if (L[k] === mx && L.filter(x => x >= mx * 0.9).length === 1 && mx > 1.6 * (L.reduce((s, x) => s + x, 0) - mx) / (L.length - 1)) flag(id, tag, 'longest-key', 'البديل الصحيح أطول بكثير من البقية');
    // 6) ملاحظات الأخطاء تحتوي «صحيح» عن البديل الخاطئ (احتمال خطأ ترتيب)
    q.distractor_notes.forEach((n, j) => { if (j !== k && /^(هذا|هذه)?\s*(هو|هي)?\s*(الإجابة|البديل)\s*الصحيح/.test(strip(n))) flag(id, tag, 'note-says-correct', `ملاحظة البديل «${'أبجد'[j]}» تصفه بالصحيح`); });
    // 7) نص السؤال يحيل إلى شكل غير ظاهر
    if (/(الشكل|المنحنى|الرسم)\s*(\d|الآتي|المجاور|أعلاه)/.test(q.stem) && !q.stimulus) flag(id, tag, 'invisible-figure', 'يحيل إلى شكل ولا يوجد جدول/معطيات');
  });
  d.essay.forEach((q, i) => {
    const tag = `essay${i + 1}`;
    const total = (q.marks || []).reduce((s, m) => s + Number(m.marks || 0), 0);
    const top = String((q.rubric || [])[0]?.level || '');
    const tn = nums(top)[0];
    if (tn !== undefined && Number(tn) !== total) flag(id, tag, 'marks-vs-rubric', `مجموع الدرجات ${total} والمستوى الأعلى «${top}»`);
    if (!/صفر|0/.test(String((q.rubric || []).at(-1)?.level || ''))) flag(id, tag, 'rubric-last', 'آخر مستوى في سلم التصحيح ليس «صفر»');
    if ((q.answer_elements || []).length < 2) flag(id, tag, 'few-elements', 'عناصر الإجابة أقل من اثنين');
  });
  // 8) توزيع المفاتيح داخل الملف
  const pos = [0, 0, 0, 0]; d.mcq.forEach(q => pos[q.correct_index]++);
  if (Math.max(...pos) > 3 || pos.filter(x => x === 0).length > 0) flag(id, 'file', 'key-spread', `توزيع المفاتيح ${pos.join('/')}`);
}

const byKind = {};
for (const f of flags) byKind[f.kind] = (byKind[f.kind] || 0) + 1;
if (process.env.JSON) { console.log(JSON.stringify(flags, null, 1)); process.exit(0); }
for (const f of flags) console.log(`${f.id} ${f.q} [${f.kind}] ${f.msg}`);
console.log(`\n${ids.length} ملفًا، ${flags.length} تنبيهًا`, byKind);
