# Training Pipeline

مسیر آموزش ایجنت‌ها از منابع مختلف.

## منابع پشتیبانی‌شده
1. PDF
2. کانال تلگرام
3. ویدیو

## جریان استاندارد
1. دریافت محتوا از منبع
2. وضعیت: `PENDING_USER_APPROVAL`
3. تأیید کاربر
4. ارسال به ایجنت با `receive_training()`
5. بعداً تست کاربر → Experience

## مثال
```python
from training import TrainingPipeline
from agents.technical.workers.tech_nds_01 import TechNDS01

pipeline = TrainingPipeline()
agent = TechNDS01()

# از PDF
item = pipeline.add_from_pdf("docs/lesson1.pdf", title="Lesson 1")
pipeline.approve(item["id"])
pipeline.push_to_agent(item["id"], agent)

# از تلگرام
item = pipeline.add_from_telegram_message(
    channel_id="@my_channel",
    message_id="123",
    text="متن آموزشی...",
)
pipeline.approve(item["id"])
pipeline.push_to_agent(item["id"], agent)

# از ویدیو
item = pipeline.add_from_video(
    video_ref="https://youtube.com/...",
    transcript="متن پیاده‌سازی شده ویدیو...",
)
pipeline.approve(item["id"])
pipeline.push_to_agent(item["id"], agent)
```

## نکات
- بدون تأیید کاربر، آموزش وارد ایجنت نمی‌شود
- مفهوم دامنه از قبل داخل ایجنت hardcode نمی‌شود
- تجربه از تست کاربر ساخته می‌شود و وزن بالاتری دارد
