# Ramaz X1 Backend

FastAPI backend for Ramaz X1 Multi-Agent AI System.

## Run

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints

- `GET /` — System status
- `GET /health` — Health check
- `GET /agents` — List all agents
- `GET /agents/{agent_id}` — Get agent details
- `POST /missions` — Create new mission
- `GET /missions` — List missions
- `GET /missions/{mission_id}` — Get mission details
- `GET /logs` — Get logs
