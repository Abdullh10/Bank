// التاريخ الهجري (أم القرى) بترتيب ثابت في كل المتصفحات: «4 جمادى الأولى 1448هـ»، ومعه الوقت اختياريًا «… · 8:24 م».
// (تنسيق المتصفح الافتراضي يختلف بين الأجهزة، وفي خلية يسار-يمين يختلط ترتيب اليوم والشهر والسنة و«هـ».)
const dateFmt = new Intl.DateTimeFormat('ar-SA-u-ca-islamic-umalqura-nu-latn', { day: 'numeric', month: 'long', year: 'numeric' });
const timeFmt = new Intl.DateTimeFormat('ar-SA-u-nu-latn', { hour: 'numeric', minute: '2-digit', hour12: true });
export function hijri(d, withTime = false) {
  if (!d) return '—';
  const dt = new Date(d);
  if (Number.isNaN(dt.getTime())) return '—';
  const p = Object.fromEntries(dateFmt.formatToParts(dt).filter(x => x.type !== 'literal').map(x => [x.type, x.value]));
  const s = `${p.day} ${p.month} ${String(p.year).replace(/\D/g, '')}هـ`;
  return withTime ? `${s} · ${timeFmt.format(dt)}` : s;
}
