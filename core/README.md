# Agent Brain + RAG Memory v2

## ارتقاها
1. Persistent storage با SQLite (`data/rag/<agent_id>.sqlite3`)
2. Embedding قابل تعویض:
   - پیش‌فرض: `local_hash` (بدون وابستگی)
   - اختیاری: OpenAI با `OPENAI_API_KEY`
3. Chunking برای متن‌های بلند/PDF/transcript

## متغیر محیطی
- `RAMAZ_EMBEDDING_PROVIDER=auto|local|openai`
- `OPENAI_API_KEY=...` (اگر openai بخواهید)

## نتیجه
- حافظه با ری‌استارت از بین نمی‌رود
- مدل جدید همان DB را استفاده می‌کند
- فقط top-k مرتبط وارد پرامپت می‌شود
