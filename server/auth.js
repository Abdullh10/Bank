// المصادقة: كلمات مرور مجزأة بـ scrypt، وجلسات في قاعدة البيانات عبر ملف تعريف ارتباط HttpOnly.
import crypto from 'node:crypto';
import { getDb } from './db.js';

const COOKIE = 'chem21_session';
const SESSION_DAYS = 7;

export function hashPassword(password) {
  const salt = crypto.randomBytes(16);
  const hash = crypto.scryptSync(password, salt, 64);
  return `scrypt$${salt.toString('hex')}$${hash.toString('hex')}`;
}

export function verifyPassword(password, stored) {
  const [scheme, saltHex, hashHex] = String(stored).split('$');
  if (scheme !== 'scrypt' || !saltHex || !hashHex) return false;
  const expected = Buffer.from(hashHex, 'hex');
  const actual = crypto.scryptSync(password, Buffer.from(saltHex, 'hex'), expected.length);
  return crypto.timingSafeEqual(expected, actual);
}

export function createUser({ username, displayName, role, password }) {
  if (!/^[a-zA-Z0-9_.-]{3,32}$/.test(username || '')) throw new Error('اسم المستخدم غير صالح');
  if (!['admin', 'reviewer', 'viewer'].includes(role)) throw new Error('الدور غير صالح');
  if (!password || password.length < 10) throw new Error('كلمة المرور يجب ألا تقل عن 10 أحرف');
  const r = getDb()
    .prepare('INSERT INTO users (username, display_name, role, password_hash) VALUES (?, ?, ?, ?)')
    .run(username, displayName || username, role, hashPassword(password));
  return Number(r.lastInsertRowid);
}

function parseCookies(header = '') {
  return Object.fromEntries(
    header.split(';').map(s => s.trim()).filter(Boolean).map(s => {
      const i = s.indexOf('=');
      return [s.slice(0, i), decodeURIComponent(s.slice(i + 1))];
    }),
  );
}

export function login(res, username, password) {
  const db = getDb();
  const u = db.prepare('SELECT * FROM users WHERE username = ?').get(username || '');
  if (!u || !verifyPassword(password || '', u.password_hash)) return null;
  const token = crypto.randomBytes(32).toString('hex');
  const expires = new Date(Date.now() + SESSION_DAYS * 864e5).toISOString();
  db.prepare('DELETE FROM sessions WHERE expires_at < ?').run(new Date().toISOString());
  db.prepare('INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)').run(token, u.id, expires);
  const secure = process.env.COOKIE_SECURE === '1' ? '; Secure' : '';
  res.setHeader('Set-Cookie',
    `${COOKIE}=${token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${SESSION_DAYS * 86400}${secure}`);
  return publicUser(u);
}

export function logout(req, res) {
  const token = parseCookies(req.headers.cookie)[COOKIE];
  if (token) getDb().prepare('DELETE FROM sessions WHERE token = ?').run(token);
  res.setHeader('Set-Cookie', `${COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0`);
}

export function publicUser(u) {
  return u && { id: u.id, username: u.username, displayName: u.display_name, role: u.role };
}

// يضيف req.user إن وُجدت جلسة صالحة.
export function sessionMiddleware(req, _res, next) {
  const token = parseCookies(req.headers.cookie)[COOKIE];
  if (token) {
    const row = getDb().prepare(
      `SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id
       WHERE s.token = ? AND s.expires_at > ?`).get(token, new Date().toISOString());
    if (row) req.user = publicUser(row);
  }
  next();
}

const RANK = { viewer: 1, reviewer: 2, admin: 3 };
export function requireRole(role) {
  return (req, res, next) => {
    if (!req.user) return res.status(401).json({ error: 'يلزم تسجيل الدخول' });
    if (RANK[req.user.role] < RANK[role]) return res.status(403).json({ error: 'لا تملك صلاحية تنفيذ هذا الإجراء' });
    next();
  };
}
