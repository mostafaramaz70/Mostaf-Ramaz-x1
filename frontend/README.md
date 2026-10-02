# Ramaz X1 Frontend

## اتصال به Backend
پیش‌فرض:
```
http://127.0.0.1:8000
```

برای تغییر:
```js
localStorage.setItem('RAMAZ_API_BASE', 'http://127.0.0.1:8000')
```

## قابلیت‌های متصل به API
- وضعیت سیستم: `GET /`
- ذخیره آموزش: `POST /training`
- لیست آموزش/تجربه: `GET /training/{id}` , `GET /experience/{id}`
- انتقال به تجربه با تأیید کاربر: `POST /experience/from-training`
- کشف‌ها: approve/reject
- اتصال و تعویض مدل: `/models/attach` , `/models/switch`
- ورودی دیداری مأموریت: `POST /missions/visual`

## اجرا
1. Backend:
```bash
cd backend
py -m uvicorn main:app --reload
```
2. باز کردن `frontend/index.html` در مرورگر
