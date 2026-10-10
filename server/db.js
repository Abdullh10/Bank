// قاعدة البيانات: SQLite عبر الوحدة المدمجة node:sqlite (لا تعتمد على مكتبات أصلية).
import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
export const DB_PATH = process.env.DB_PATH || path.join(root, 'data', 'chem21.db');

const SCHEMA = `
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','reviewer','viewer')),
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
  id INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  grade TEXT NOT NULL,
  term TEXT NOT NULL,
  country TEXT NOT NULL,
  structure_source TEXT,
  content_source TEXT
);

CREATE TABLE IF NOT EXISTS chapters (
  id INTEGER PRIMARY KEY,
  course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  number INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  UNIQUE (course_id, number)
);

CREATE TABLE IF NOT EXISTS lessons (
  id INTEGER PRIMARY KEY,
  chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
  number INTEGER NOT NULL,
  title TEXT NOT NULL,
  summary TEXT,
  source_note TEXT,
  UNIQUE (chapter_id, number)
);

-- الهدف الأصلي لا يُحذف ولا يُعدّل: الصياغة المقترحة والمعتمدة في حقول مستقلة.
CREATE TABLE IF NOT EXISTS objectives (
  id INTEGER PRIMARY KEY,
  lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  code TEXT NOT NULL UNIQUE,
  original_code TEXT,
  number INTEGER NOT NULL,
  original_text TEXT NOT NULL,
  proposed_text TEXT,
  split_into TEXT NOT NULL DEFAULT '[]',
  approved_text TEXT,
  revision_reason TEXT,
  revision_type TEXT,
  ai_review_status TEXT,
  thinking_level TEXT,
  knowledge_type TEXT,
  concepts TEXT NOT NULL DEFAULT '[]',
  source_page INTEGER,
  memo_pages TEXT NOT NULL DEFAULT '[]',
  memo_coverage TEXT,
  memo_note TEXT,
  duplicate_of TEXT,
  review_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (review_status IN ('pending','approved','returned')),
  reviewed_by INTEGER REFERENCES users(id),
  reviewed_at TEXT,
  required_mcq INTEGER NOT NULL DEFAULT 7,
  required_essay INTEGER NOT NULL DEFAULT 3
);

-- محتوى مكمّل للفراغات في المذكرة (من الوكيل الكيميائي التربوي) — يخضع للمراجعة.
CREATE TABLE IF NOT EXISTS supplements (
  objective_id INTEGER PRIMARY KEY REFERENCES objectives(id) ON DELETE CASCADE,
  memo_basis TEXT,
  supplement TEXT NOT NULL,
  key_points TEXT NOT NULL DEFAULT '[]',
  misconceptions TEXT NOT NULL DEFAULT '[]',
  scientific_notes TEXT,
  confidence TEXT,
  origin TEXT NOT NULL DEFAULT 'ai_agent',
  review_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (review_status IN ('pending','approved','returned'))
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY,
  objective_id INTEGER NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('mcq','essay')),
  number INTEGER NOT NULL,
  stem TEXT NOT NULL,
  stimulus TEXT,               -- JSON: جدول بيانات مرفق بالسؤال {headers:[], rows:[[]]}
  options TEXT,                -- JSON: ثلاثة بدائل لأسئلة الاختيار
  correct_index INTEGER,
  explanation TEXT,
  distractor_notes TEXT,       -- JSON: سبب خطأ كل بديل
  model_answer TEXT,
  answer_elements TEXT,        -- JSON
  solution_steps TEXT,         -- JSON
  marks TEXT,                  -- JSON: [{element, marks}]
  rubric TEXT,                 -- JSON: [{level, description}]
  common_errors TEXT,          -- JSON
  thinking_level TEXT,
  question_kind TEXT,
  difficulty TEXT CHECK (difficulty IN ('سهل','متوسط','صعب')),
  source_ref TEXT,
  status TEXT NOT NULL DEFAULT 'generated'
    CHECK (status IN ('generated','in_review','needs_revision','approved')),
  auto_check TEXT,             -- JSON: نتيجة التحقق الآلي (منفصلة عن المراجعة البشرية)
  reviewer_notes TEXT,
  excluded INTEGER NOT NULL DEFAULT 0,
  origin TEXT NOT NULL DEFAULT 'ai_generated',
  reviewed_by INTEGER REFERENCES users(id),
  reviewed_at TEXT,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS revisions (
  id INTEGER PRIMARY KEY,
  entity TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  before_json TEXT,
  after_json TEXT,
  note TEXT,
  user_id INTEGER REFERENCES users(id),
  at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_q_obj ON questions(objective_id);
CREATE INDEX IF NOT EXISTS idx_rev_entity ON revisions(entity, entity_id);
`;

let db;
export function getDb() {
  if (!db) {
    db = new DatabaseSync(DB_PATH);
    db.exec(SCHEMA);
  }
  return db;
}

export function tx(fn) {
  const d = getDb();
  d.exec('BEGIN');
  try {
    const r = fn(d);
    d.exec('COMMIT');
    return r;
  } catch (e) {
    d.exec('ROLLBACK');
    throw e;
  }
}

export const J = {
  parse(v, fallback = null) {
    if (v == null || v === '') return fallback;
    try { return JSON.parse(v); } catch { return fallback; }
  },
  str(v) { return v == null ? null : JSON.stringify(v); },
};
