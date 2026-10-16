// تصدير الاختبار إلى Word (.docx) قابل للتعديل: الكليشة بالشعار، والأسئلة من اليمين لليسار، والنماذج، ومفتاح الإجابة.
// المكتبة docx تُمرَّر من الخارج (تُحمَّل من CDN عند الحاجة) حتى يبقى هذا الملف قابلًا للاختبار في Node.
// كل سؤال يبقى في صفحة واحدة: فقراته مربوطة بـ keepNext/keepLines، والجداول لا تنقسم صفوفها.

const FONT = 'Arial';
const NAVY = '1F2D6B';

export function buildExamDocx(D, { exam, header: h, opts: o, kind, logo, letters, ordinals, fmt }) {
  const { Document, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle,
    ImageRun, PageBreak, Footer, PageNumber, ShadingType, VerticalAlign, TableLayoutType } = D;

  // ---------- أدوات ----------
  const run = (text, x = {}) => new TextRun({ text: String(text ?? ''), font: FONT, rightToLeft: true,
    size: x.size || 24, sizeComplexScript: x.size || 24, bold: !!x.bold, boldComplexScript: !!x.bold, color: x.color });
  const para = (children, x = {}) => new Paragraph({
    bidirectional: true, alignment: x.align || AlignmentType.START,
    spacing: { before: x.before ?? 0, after: x.after ?? 60, line: x.line || 276 },
    keepNext: !!x.keepNext, keepLines: true, children: Array.isArray(children) ? children : [children],
    border: x.border, indent: x.indent, shading: x.shading,
  });
  const p = (text, x = {}) => para(run(text, x), x);
  const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
  const line = (c = '222222', size = 6) => ({ style: BorderStyle.SINGLE, size, color: c });
  const allBorders = b => ({ top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b });
  const cell = (children, x = {}) => new TableCell({
    children: (Array.isArray(children) ? children : [children]).map(c => (typeof c === 'string' ? p(c, { align: x.align || AlignmentType.CENTER, size: x.size, bold: x.bold, after: 0 }) : c)),
    columnSpan: x.span, width: x.width ? { size: x.width, type: WidthType.PERCENTAGE } : undefined,
    verticalAlign: VerticalAlign.CENTER, borders: x.borders,
    shading: x.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: x.fill } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
  });
  const table = (rows, x = {}) => new Table({
    visuallyRightToLeft: true, width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED,
    borders: x.borders || allBorders(line()),
    rows: rows.map(r => new TableRow({ children: r, cantSplit: true, height: x.rowHeight ? { value: x.rowHeight, rule: 'atLeast' } : undefined })),
  });
  const th = (t, x = {}) => cell(t, { ...x, bold: true, size: 20, fill: 'EEF1F8' });
  const spacer = (after = 120) => p('', { after });

  // ---------- الكليشة ----------
  const head = (m, isKey) => {
    const right = [h.country, h.org, h.dept, h.school].filter(Boolean)
      .map((t, i, a) => p(t, { size: i === a.length - 1 ? 22 : 20, bold: i === a.length - 1, color: NAVY, after: 0, align: AlignmentType.CENTER }));
    const left = [h.title, h.year && `العام الدراسي ${h.year}`, h.subject && `المادة: ${h.subject}`, h.duration && `الزمن: ${h.duration}`].filter(Boolean)
      .map((t, i) => p(t, { size: i === 0 ? 22 : 20, bold: i === 0, color: NAVY, after: 0, align: AlignmentType.CENTER }));
    const logoCell = logo
      ? [new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ data: logo, transformation: { width: 92, height: 86 } })] })]
      : [p('')];
    const out = [
      table([[cell(right, { width: 38 }), cell(logoCell, { width: 24 }), cell(left, { width: 38 })]],
        { borders: { top: line(NAVY, 12), bottom: line(NAVY, 12), left: line(NAVY, 12), right: line(NAVY, 12), insideHorizontal: none, insideVertical: none } }),
      spacer(80),
      table([
        [th('اسم الطالب', { width: 16 }), cell('', { span: 3, width: 54 }), th('رقم الجلوس', { width: 14 }), cell('', { width: 16 })],
        [th('الصف'), cell(h.grade || ''), th('الشعبة'), cell(''), th('التاريخ'), cell(h.date || '')],
      ]),
      spacer(80),
      table([[
        cell(p(`النموذج (${m.name})${isKey ? ' — مفتاح الإجابة' : ''}`, { bold: true, color: NAVY, align: AlignmentType.CENTER, after: 0 }), { width: 40 }),
        th('الدرجة', { width: 11 }), cell('', { width: 12 }), th('من', { width: 7 }), cell(fmt(exam.total), { width: 8, bold: true }),
        th('المصحح', { width: 10 }), cell('', { width: 12 }),
      ]]),
    ];
    if (!isKey && h.instructions) out.push(spacer(60), para([run('تعليمات: ', { bold: true, size: 22 }), run(h.instructions, { size: 22 })],
      { border: { right: line(NAVY, 18) }, indent: { right: 120 }, after: 100 }));
    return out;
  };

  const sectionTitle = (text, marks) => para([run(text, { bold: true, color: NAVY, size: 24 }), run(marks ? `  (${marks} درجة)` : '', { size: 22 })],
    { keepNext: true, before: 200, after: 100, border: { bottom: line(NAVY, 8) } });

  const stimTable = s => (s ? [table([s.headers.map(x => th(String(x))), ...s.rows.map(r => r.map(c => cell(String(c), { size: 20 })))]), spacer(40)] : []);

  // جدول الإجابات: 10 أعمدة ثابتة في كل صف (الصف الأخير يُكمل بخلايا فارغة حتى لا تتشوه الأعمدة)
  const grid = (count, fill) => {
    const rows = [];
    for (let i = 0; i < count; i += 10) {
      rows.push([th('السؤال', { width: 16 }), ...Array.from({ length: 10 }, (_, k) => (i + k < count ? th(String(i + k + 1), { width: 8.4 }) : cell('', { width: 8.4 })))]);
      rows.push([th('الإجابة'), ...Array.from({ length: 10 }, (_, k) => cell(i + k < count && fill ? fill(i + k) : '', { bold: true }))]);
    }
    return [table(rows), spacer(100)];
  };
  // البدائل في سطر واحد: جدول بلا حدود بثلاثة أعمدة (يحفظ ترتيب أ ب ج مع الرموز الإنجليزية)
  const optsRow = options => table([options.map((x, k) => cell(para([run(`${letters[k]}) `, { bold: true, color: NAVY }), run(x)], { after: 0 }),
    { width: Math.floor(100 / options.length), borders: allBorders(none) }))], { borders: allBorders(none) });
  // أسطر الإجابة: صفوف جدول بخط منقط سفلي، كل صف مربوط بالتالي فلا تنفصل عن السؤال
  const answerLines = n => table(Array.from({ length: n }, (_, k) => [new TableCell({
    children: [new Paragraph({ keepNext: k < n - 1, keepLines: true, children: [run('')] })],
    borders: { top: none, left: none, right: none, bottom: { style: BorderStyle.DOTTED, size: 6, color: '777777' } },
  })]), { borders: allBorders(none), rowHeight: 480 });

  // ---------- ورقة الطالب ----------
  const student = m => {
    const out = [...head(m, false)];
    let qn = 0;
    if (m.mcq.length) {
      out.push(sectionTitle(`السؤال ${ordinals[qn++]}: اختر الإجابة الصحيحة لكل مما يأتي`, fmt(m.mcq.length * o.mcqMark)));
      if (o.answerGrid) out.push(...grid(m.mcq.length));
      m.mcq.forEach(({ q, options }, i) => {
        // أربعة بدائل في سطر واحد تضيق أسرع من ثلاثة
        const long = options.some(x => x.length > (options.length > 3 ? 20 : 28));
        const stim = stimTable(q.stimulus);
        out.push(p(`${i + 1}. ${q.stem}`, { bold: true, keepNext: true, after: 40 }), ...stim);
        if (long) options.forEach((x, k) => out.push(p(`${letters[k]}) ${x}`, { keepNext: k < options.length - 1, indent: { right: 360 }, after: k < options.length - 1 ? 20 : 160 })));
        else out.push(optsRow(options), spacer(80));
      });
    }
    if (m.essay.length) {
      out.push(sectionTitle(`السؤال ${ordinals[qn++]}: أجب عن الأسئلة الآتية`, fmt(m.essay.reduce((s, q) => s + exam.essayMarks(q), 0))));
      m.essay.forEach((q, i) => {
        const lines = Math.min(8, 3 + Math.round(exam.essayMarks(q)));
        out.push(para([run(`${i + 1}. ${q.stem}`, { bold: true }), run(`  (${fmt(exam.essayMarks(q))} درجات)`, { size: 20 })], { keepNext: true, after: 40 }),
          ...stimTable(q.stimulus));
        out.push(answerLines(lines), spacer(100));
      });
    }
    out.push(p(`انتهت الأسئلة — مع تمنياتنا لكم بالتوفيق والنجاح${h.teacher ? `     معلم المادة: ${h.teacher}` : ''}`,
      { align: AlignmentType.CENTER, color: NAVY, size: 22, before: 200, border: { top: line(NAVY, 8) } }));
    return out;
  };

  // ---------- مفتاح الإجابة ----------
  const key = m => {
    const out = [...head(m, true)];
    if (m.mcq.length) {
      out.push(sectionTitle('مفتاح أسئلة الاختيار من متعدد'), ...grid(m.mcq.length, i => (m.mcq[i].correct >= 0 ? letters[m.mcq[i].correct] : '؟')));
      m.mcq.forEach((x, i) => out.push(para([run(`${i + 1}. `, { bold: true }),
        run(x.correct >= 0 ? `${letters[x.correct]}) ${x.options[x.correct]}` : '', { bold: true, color: NAVY }),
        run(x.q.explanation ? ` — ${x.q.explanation}` : '', { size: 22 })], { after: 60 })));
    }
    if (m.essay.length) {
      out.push(sectionTitle('الإجابات النموذجية للأسئلة المقالية'));
      m.essay.forEach((q, i) => {
        out.push(p(`${i + 1}. ${q.stem}`, { bold: true, keepNext: true, after: 20 }),
          para([run('الإجابة النموذجية: ', { bold: true, size: 22 }), run(q.modelAnswer || 'غير متاحة', { size: 22 })], { keepNext: !!q.marks?.length, after: 20 }));
        if (q.marks?.length) out.push(para([run('توزيع الدرجات: ', { bold: true, size: 22 }),
          run(q.marks.map(x => `${x.element} (${fmt(Number(x.marks))})`).join('، '), { size: 22 })], { after: 100 }));
      });
    }
    return out;
  };

  // ---------- المستند ----------
  const pages = [];
  if (kind !== 'key') exam.models.forEach(m => pages.push(student(m)));
  if (kind !== 'student') exam.models.forEach(m => pages.push(key(m)));
  const children = pages.flatMap((pg, i) => (i ? [new Paragraph({ children: [new PageBreak()] }), ...pg] : pg));
  return new Document({
    creator: 'إتقان · بنك أسئلة الكيمياء', title: h.title || 'اختبار', description: 'اختبار مولّد من منصة إتقان',
    styles: { default: { document: { run: { font: FONT, size: 24, sizeComplexScript: 24, rightToLeft: true } } } },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 567, bottom: 794, left: 567, right: 567 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, bidirectional: true,
        children: [run('صفحة ', { size: 18 }), new TextRun({ children: [PageNumber.CURRENT], size: 18 }), run(' من ', { size: 18 }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 })] })] }) },
      children,
    }],
  });
}
