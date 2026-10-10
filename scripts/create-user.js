// إنشاء مستخدم: npm run create-user -- <username> <role: admin|reviewer|viewer> "<الاسم>"
// كلمة المرور تُقرأ من المتغير USER_PASSWORD أو تُطلب تفاعليًا، ولا تُخزن إلا مجزأة.
import readline from 'node:readline';
import { createUser } from '../server/auth.js';

const [username, role, displayName] = process.argv.slice(2);
if (!username || !role) {
  console.error('الاستخدام: npm run create-user -- <username> <admin|reviewer|viewer> "<الاسم المعروض>"');
  process.exit(1);
}
async function readPassword() {
  if (process.env.USER_PASSWORD) return process.env.USER_PASSWORD;
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(r => rl.question('كلمة المرور (10 أحرف على الأقل): ', a => { rl.close(); r(a); }));
}
try {
  const id = createUser({ username, role, displayName, password: await readPassword() });
  console.log(`تم إنشاء المستخدم ${username} (${role}) برقم ${id}`);
} catch (e) {
  console.error('تعذر إنشاء المستخدم:', e.message);
  process.exit(1);
}
