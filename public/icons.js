// أيقونات «إتقان» ثلاثية الأبعاد: بلاطة بتدرّج لوني ولمعة علوية وظل ناعم، ورمز أبيض مائل إلى البيج.
// تُبنى رموزها مرة واحدة داخل «sprite» مخفي، وتُستعمل بـ <use> حتى تبقى الصفحة خفيفة.
// الألوان كلها من متغيرات CSS (أصناف ic-*) فتتبدل تلقائيًا في الوضع الليلي، ولا توجد أنماط مضمّنة (CSP).

const NS = 'http://www.w3.org/2000/svg';

// الرموز في مربع 48×48، والبلاطة من 5 إلى 43. {p} = لون الرمز، {a} = لون التمييز (بيج/ذهبي).
const GLYPHS = {
  home: `<path d="M14 23.5 24 15l10 8.5"/><path d="M17.5 21.5V32h13V21.5"/><path d="M22 32v-5.5h4V32" fill="{a}" stroke="none"/>`,
  chapters: `<rect x="14" y="14" width="6.5" height="19" rx="1.6"/><rect x="22.5" y="14" width="6.5" height="19" rx="1.6"/><path d="m31.3 16.2 4.1 1.2-4.6 15.6-4.1-1.2" /><path d="M14 19h6.5M22.5 19h6.5" stroke="{a}"/>`,
  bank: `<rect x="15" y="13" width="18" height="21" rx="3.2"/><path d="M20.6 20.2a3.5 3.5 0 1 1 4.9 3.2c-1 .45-1.5 1.1-1.5 2.2v.4"/><circle cx="24" cy="29.6" r="1.7" fill="{a}" stroke="none"/>`,
  exam: `<rect x="15" y="14" width="18" height="21" rx="3"/><path d="M20 14v-1.6h8V14" /><path d="m19.6 25 3.1 3.1 6-6.4" stroke="{a}"/>`,
  reports: `<path d="M13 34h22"/><path d="M17.5 30.5v-5M24 30.5v-13M30.5 30.5v-8.5" stroke-width="4.2"/><circle cx="24" cy="17.5" r="2.1" fill="{a}" stroke="none"/>`,
  progress: `<path d="m13.5 31 7-7.2 5 4.2 8.5-9.5"/><path d="M28.5 18.3h5.6v5.6" stroke="{a}"/>`,
  students: `<circle cx="20" cy="19" r="4.2"/><path d="M12.5 33c0-5 3.4-8.2 7.5-8.2s7.5 3.2 7.5 8.2"/><circle cx="30.5" cy="20" r="3.3" stroke="{a}"/><path d="M29.6 25.6c3.2.3 5.9 2.9 5.9 6.9" stroke="{a}"/>`,
  practice: `<path d="M18.4 27.3h11.2l3 5.2a1.7 1.7 0 0 1-1.5 2.5H16.9a1.7 1.7 0 0 1-1.5-2.5z" fill="{a}" stroke="none"/><path d="M20 13h8M21.6 13v7.4l-6.6 11.4a2.3 2.3 0 0 0 2 3.4h14a2.3 2.3 0 0 0 2-3.4l-6.6-11.4V13"/>`,
  history: `<path d="M15 24a9.5 9.5 0 1 0 2.9-6.8"/><path d="M15.2 13.6v4.6h4.6"/><path d="M24.3 18.8v5.6l3.6 2.4" stroke="{a}"/>`,
  lessons: `<path d="M24 17.2c-3-2.4-6.6-3-10-2.5v16c3.4-.5 7 0 10 2.5 3-2.5 6.6-3 10-2.5v-16c-3.4-.5-7 .1-10 2.5z"/><path d="M24 17.2v16" stroke="{a}"/>`,
  objectives: `<circle cx="24" cy="23.5" r="10"/><circle cx="24" cy="23.5" r="5.2"/><circle cx="24" cy="23.5" r="2" fill="{a}" stroke="none"/>`,
  mcq: `<circle cx="16.5" cy="16.5" r="2.4" fill="{a}" stroke="none"/><circle cx="16.5" cy="23.5" r="2.2" stroke-width="2.2"/><circle cx="16.5" cy="30.5" r="2.2" stroke-width="2.2"/><path d="M22 16.5h11M22 23.5h9M22 30.5h10"/>`,
  essay: `<path d="M14 17h10M14 23h7M14 29h5"/><path d="m32.6 15.4 3 3-10.4 10.4-4.3 1.3 1.3-4.3z" stroke="{a}"/>`,
  lock: `<path d="M19 21.2v-3.6a5 5 0 0 1 10 0v3.6"/><rect x="15" y="21.2" width="18" height="13.6" rx="3.2"/><circle cx="24" cy="27" r="1.7" fill="{a}" stroke="none"/><path d="M24 28.2v2.6" stroke="{a}"/>`,
  empty: `<path d="M13.5 26 17.6 15h12.8l4.1 11v6.5a2 2 0 0 1-2 2h-17a2 2 0 0 1-2-2z"/><path d="M13.5 26h6.6l1.6 3h4.6l1.6-3h6.6" stroke="{a}"/>`,
  shield: `<path d="M24 12.5 33 16v7c0 5.6-3.8 9.6-9 11.5-5.2-1.9-9-5.9-9-11.5v-7z"/><path d="m19.6 23.6 3 3 5.6-6" stroke="{a}"/>`,
  pie: `<circle cx="24" cy="23.5" r="10"/><path d="M24 23.5v-10a10 10 0 0 1 9.6 7.2z" fill="{a}" stroke="none"/>`,
  sliders: `<path d="M14 17h20M14 24h20M14 31h20" stroke-width="2.6"/><circle cx="19" cy="17" r="2.8" fill="{a}" stroke="none"/><circle cx="29" cy="24" r="2.8" fill="{a}" stroke="none"/><circle cx="22" cy="31" r="2.8" fill="{a}" stroke="none"/>`,
  trophy: `<path d="M17.5 14h13v6.2a6.5 6.5 0 0 1-13 0z"/><path d="M17.5 16.2h-3v1.6a4 4 0 0 0 4 4M30.5 16.2h3v1.6a4 4 0 0 1-4 4"/><path d="M24 26.8v4"/><path d="M19.5 34h9M21 30.8h6" stroke="{a}"/>`,
  spark: `<path d="M22 13.5c.9 5.4 2.6 7.1 8 8-5.4.9-7.1 2.6-8 8-.9-5.4-2.6-7.1-8-8 5.4-.9 7.1-2.6 8-8z"/><path d="M31.5 25.5c.5 2.6 1.3 3.4 3.9 3.9-2.6.5-3.4 1.3-3.9 3.9-.5-2.6-1.3-3.4-3.9-3.9 2.6-.5 3.4-1.3 3.9-3.9z" fill="{a}" stroke="none"/>`,
  check: `<path d="m16 24 5.5 5.5L32.5 18" stroke-width="3.6"/>`,
  cross: `<path d="m17.5 17 13 13M30.5 17l-13 13" stroke-width="3.6"/>`,
  notes: `<path d="M14.5 15.5h19a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H23l-5.5 4.5V30.5h-3a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2z"/><path d="M18.5 20.5h11M18.5 25h7" stroke="{a}"/>`,
  team: `<circle cx="24" cy="17.5" r="3.8"/><path d="M17 31c0-4.4 3.1-7.2 7-7.2s7 2.8 7 7.2"/><circle cx="14.8" cy="21" r="2.6" stroke="{a}"/><circle cx="33.2" cy="21" r="2.6" stroke="{a}"/><path d="M11 30.5c.3-2.8 1.8-4.6 4-5M37 30.5c-.3-2.8-1.8-4.6-4-5" stroke="{a}"/>`,
  upload: `<path d="M15 28v4a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-4"/><path d="M24 29V14.5" stroke="{a}"/><path d="m18.8 19.5 5.2-5.2 5.2 5.2" stroke="{a}"/>`,
  // رموز فصول المقرر
  atom: `<ellipse cx="24" cy="23.5" rx="11" ry="4.3" stroke-width="2.3"/><ellipse cx="24" cy="23.5" rx="11" ry="4.3" stroke-width="2.3" transform="rotate(60 24 23.5)"/><ellipse cx="24" cy="23.5" rx="11" ry="4.3" stroke-width="2.3" transform="rotate(120 24 23.5)"/><circle cx="24" cy="23.5" r="2.4" fill="{a}" stroke="none"/>`,
  periodic: `<rect x="14" y="14" width="9" height="9" rx="2"/><rect x="25" y="14" width="9" height="9" rx="2" fill="{a}" stroke="{a}"/><rect x="14" y="25" width="9" height="9" rx="2"/><rect x="25" y="25" width="9" height="9" rx="2"/>`,
  crystal: `<path d="M24 24 34 18.6 24 13.2 14 18.6z" fill="{a}" stroke="none"/><path d="m24 13.2 10 5.4v11L24 35l-10-5.4v-11z"/><path d="m14 18.6 10 5.4 10-5.4M24 24v11"/>`,
  molecule: `<path d="m18.5 27.5 4-7M29.5 27.5l-4-7M20 30.5h8" stroke-width="2.4"/><circle cx="16.5" cy="30" r="3.6"/><circle cx="31.5" cy="30" r="3.6"/><circle cx="24" cy="17" r="4.3" fill="{a}" stroke="{a}"/>`,
  calc: `<rect x="15.5" y="12.5" width="17" height="22.5" rx="3"/><rect x="18.5" y="15.5" width="11" height="5" rx="1.2" fill="{a}" stroke="none"/><path d="M19.5 25h.01M24 25h.01M28.5 25h.01M19.5 30h.01M24 30h.01M28.5 30h.01" stroke-width="3.2"/>`,
  drop: `<path d="M24 12.5c4.6 6 8 10 8 14.6a8 8 0 0 1-16 0c0-4.6 3.4-8.6 8-14.6z"/><path d="M20.3 27.4a3.8 3.8 0 0 0 3.2 3.7" stroke="{a}"/>`,
  bubbles: `<circle cx="19.5" cy="27" r="6"/><circle cx="29.5" cy="19" r="4.4"/><circle cx="30.5" cy="31" r="2.8" fill="{a}" stroke="none"/><circle cx="17.6" cy="25" r="1.4" fill="{a}" stroke="none"/>`,
};

// رمز كل فصل حسب رقمه في المقرر (كيمياء 2-1)
export const CHAPTER_ICONS = { 1: 'atom', 2: 'periodic', 3: 'crystal', 4: 'molecule', 5: 'calc', 6: 'drop', 7: 'bubbles' };

// لون البلاطة الافتراضي لكل رمز
const TONE = { notes: 'gold', team: 'teal', trophy: 'gold', check: 'green', cross: 'rose', spark: 'teal', practice: 'teal', history: 'gold', pie: 'teal', shield: 'green', essay: 'gold', mcq: 'teal' };
const TONES = ['navy', 'teal', 'gold', 'green', 'rose'];

let sprite = null;
const made = new Set();

function ensureSprite() {
  if (sprite && sprite.isConnected) return sprite;
  sprite = document.createElementNS(NS, 'svg');
  sprite.setAttribute('class', 'ic-sprite');
  sprite.setAttribute('aria-hidden', 'true');
  sprite.setAttribute('width', '0');
  sprite.setAttribute('height', '0');
  const tile = t => `<linearGradient id="ic-t-${t}" x1="10" y1="4" x2="38" y2="43" gradientUnits="userSpaceOnUse">
      <stop offset="0" class="ic-${t}-1"/><stop offset="1" class="ic-${t}-2"/></linearGradient>`;
  sprite.innerHTML = `<defs>
    ${TONES.map(tile).join('')}
    <linearGradient id="ic-gl" x1="0" y1="12" x2="0" y2="36" gradientUnits="userSpaceOnUse"><stop offset="0" class="ic-g-1"/><stop offset="1" class="ic-g-2"/></linearGradient>
    <linearGradient id="ic-gd" x1="0" y1="12" x2="0" y2="36" gradientUnits="userSpaceOnUse"><stop offset="0" class="ic-d-1"/><stop offset="1" class="ic-d-2"/></linearGradient>
    <linearGradient id="ic-ac" x1="0" y1="12" x2="0" y2="36" gradientUnits="userSpaceOnUse"><stop offset="0" class="ic-a-1"/><stop offset="1" class="ic-a-2"/></linearGradient>
    <linearGradient id="ic-gloss" x1="0" y1="4" x2="0" y2="24" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <linearGradient id="ic-rim" x1="0" y1="4" x2="0" y2="43" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient>
    <filter id="ic-blur" x="-30%" y="-100%" width="160%" height="300%"><feGaussianBlur stdDeviation="1.4"/></filter>
  </defs>`;
  document.body.prepend(sprite);
  made.clear();
  return sprite;
}

function addSymbol(name, tone) {
  const id = `ic-${name}-${tone}`;
  if (made.has(id)) return id;
  const s = ensureSprite();
  const glyph = GLYPHS[name] || GLYPHS.spark;
  const paint = tone === 'gold' ? 'url(#ic-gd)' : 'url(#ic-gl)';
  const accent = tone === 'gold' ? 'url(#ic-gl)' : 'url(#ic-ac)';
  const shadowG = glyph.replaceAll('{p}', 'currentColor').replaceAll('{a}', 'currentColor');
  const mainG = glyph.replaceAll('{p}', paint).replaceAll('{a}', accent);
  const sym = document.createElementNS(NS, 'symbol');
  sym.setAttribute('id', id);
  sym.setAttribute('viewBox', '0 0 48 48');
  sym.innerHTML = `
    <ellipse cx="24" cy="43" rx="14" ry="2.6" class="ic-shadow" filter="url(#ic-blur)"/>
    <rect x="5" y="4" width="38" height="38" rx="11.5" fill="url(#ic-t-${tone})"/>
    <path d="M5 16.5A11.5 11.5 0 0 1 16.5 5h15A11.5 11.5 0 0 1 43 16.5v2.2c-10.5 5.6-27.5 5.6-38 0z" fill="url(#ic-gloss)"/>
    <rect x="5.6" y="4.6" width="36.8" height="36.8" rx="10.9" fill="none" stroke="url(#ic-rim)" stroke-width="1.2"/>
    <g class="ic-gs" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" transform="translate(0 1.3)">${shadowG}</g>
    <g fill="none" stroke="${paint}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">${mainG}</g>`;
  s.append(sym);
  made.add(id);
  return id;
}

/** أيقونة ثلاثية الأبعاد: icon('home', 24) أو icon('trophy', 64, 'gold') */
export function icon(name, size = 24, tone = TONE[name] || 'navy', cls = '') {
  const id = addSymbol(name, tone);
  return `<svg class="ic ic-${tone}${cls ? ' ' + cls : ''}" width="${size}" height="${size}" viewBox="0 0 48 48" aria-hidden="true" focusable="false"><use href="#${id}"/></svg>`;
}

// أيقونات خطية صغيرة بلون النص (للأزرار والحقول)
const LINES = {
  trash: '<path d="M4 7h16M10 11v6M14 11v6"/><path d="M6 7l1 13h10l1-13M9 7V4h6v3"/>',
  user: '<circle cx="12" cy="8.5" r="3.8"/><path d="M4.8 20c.6-3.9 3.6-6.4 7.2-6.4s6.6 2.5 7.2 6.4"/>',
  lock: '<rect x="5" y="10.5" width="14" height="10" rx="2.4"/><path d="M8.3 10.5V8a3.7 3.7 0 0 1 7.4 0v2.5"/>',
  key: '<circle cx="7.5" cy="15.5" r="4"/><path d="M10.4 12.6 19.5 3.5M16 7l2.5 2.5M13.8 9.2l2 2"/>',
  eye: '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
  eyeOff: '<path d="M3 3l18 18"/><path d="M10.6 5.6A9.6 9.6 0 0 1 12 5.5c6 0 9.5 6.5 9.5 6.5a17 17 0 0 1-3 3.8M6.6 6.7C4 8.4 2.5 12 2.5 12S6 18.5 12 18.5c1.6 0 3-.4 4.2-1"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
  logout: '<path d="M14 4.5h3.5a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H14"/><path d="M10 8 6 12l4 4M6 12h9.5"/>',
  print: '<path d="M7 9V4h10v5"/><rect x="4" y="9" width="16" height="7.5" rx="2"/><path d="M7 14h10v6H7z"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="6"/><path d="m20 20-4.6-4.6"/>',
  clock: '<circle cx="12" cy="12" r="8"/><path d="M12 7.5V12l3 2"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  cross: '<path d="m6.5 6.5 11 11M17.5 6.5l-11 11"/>',
  close: '<path d="m7 7 10 10M17 7 7 17"/>',
  next: '<path d="m14.5 6-6 6 6 6"/>',
  prev: '<path d="m9.5 6 6 6-6 6"/>',
  download: '<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5M5 19.5h14"/>',
};
export function line(name, size = 18, cls = '') {
  return `<svg class="li${cls ? ' ' + cls : ''}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${LINES[name] || ''}</svg>`;
}

/** يملأ العناصر <i data-icon="home" data-size="22"></i> بالأيقونات (للعناصر الثابتة في index.html) */
export function hydrateIcons(root = document) {
  root.querySelectorAll('i[data-icon]').forEach(el => {
    el.outerHTML = icon(el.dataset.icon, Number(el.dataset.size) || 22, el.dataset.tone || undefined);
  });
}
