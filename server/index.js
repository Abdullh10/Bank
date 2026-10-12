import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { getDb } from './db.js';
import { sessionMiddleware } from './auth.js';
import { api } from './api.js';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

export function createApp() {
  getDb();
  const app = express();
  app.disable('x-powered-by');
  app.use((_req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'same-origin');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Content-Security-Policy',
      "default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self'");
    next();
  });
  app.use(express.json({ limit: '1mb' }));
  app.use(sessionMiddleware);
  // حماية بسيطة من طلبات التعديل القادمة من مواقع أخرى.
  app.use('/api', (req, res, next) => {
    if (req.method !== 'GET' && req.headers.origin && new URL(req.headers.origin).host !== req.headers.host)
      return res.status(403).json({ error: 'طلب مرفوض' });
    next();
  });
  app.use('/api', api);
  // ملفات نسخة العرض الثابتة (تتضمن الإجابات) لا تُقدَّم من الخادم؛ الخادم يحمي الإجابات بالصلاحيات.
  app.use('/static', (_req, res) => res.status(404).end());
  app.use(express.static(path.join(root, 'public'), { index: 'index.html' }));
  app.get(/^\/(?!api\/).*/, (_req, res) => res.sendFile(path.join(root, 'public', 'index.html')));
  return app;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.PORT) || 3000;
  createApp().listen(port, () => console.log(`المنصة تعمل على http://localhost:${port}`));
}
