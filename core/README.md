# Agent Brain + RAG + Model Router

## Persistence
- RAG memory: `data/rag/<agent_id>.sqlite3`
- Model/API configs: `data/models/agent_models.sqlite3`

## Model switching
- Attach multiple APIs/models per agent
- User switch: `/models/switch`
- Auto failover on RATE_LIMITED / QUOTA_EXCEEDED / ERROR
- Active model persisted in DB

## Note
API secrets should be referenced by `api_key_ref` (env/secret manager), not stored as raw keys in DB.
