// إعدادات الاتصال بقاعدة بيانات Supabase.
// المفتاح هنا هو «المفتاح العام» (publishable) المخصص للواجهات؛ الحماية الفعلية في سياسات RLS والدوال المحمية بقاعدة البيانات.
// لا تضع هنا أبدًا مفتاح service_role / secret ولا كلمة مرور قاعدة البيانات.
// اترك url فارغًا لتعمل المنصة بنسخة العرض الثابتة.
export const SUPABASE = {
  url: 'https://znisbyqyygdholobhohu.supabase.co',
  key: 'sb_publishable_nynp0rDSZ91lCG4xhndULg_EDANOER5',
  // الدخول بالمعرّف (ID): يكتب المستخدم «abdullah» فيُرسل إلى Supabase كبريد شكلي abdullah@chem21.local.
  // الحسابات تُنشأ في Supabase بهذا البريد الشكلي (مع Auto Confirm)، ولا تُرسل إليه أي رسائل.
  loginDomain: 'chem21.local',
};

// الرابط الرسمي للمنصة: يُطبع على بطاقات دخول الطلاب وفي ملفات Excel.
export const SITE_URL = 'https://itqanchem.com';

