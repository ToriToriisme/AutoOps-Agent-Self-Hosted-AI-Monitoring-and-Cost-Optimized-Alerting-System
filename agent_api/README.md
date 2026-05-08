# agent_api (FastAPI backend)

Mục đích: nhận webhook alert từ Grafana, chuẩn hoá payload, triage SMALL/MEDIUM/CRITICAL, lưu audit, (tuỳ) notify/tool execution.

## Run (dev)

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open: `http://localhost:8000/docs`

