from fastapi import Depends, FastAPI, Header, HTTPException

from .schemas.grafana_webhook import GrafanaWebhookPayload

app = FastAPI(title="AutoOps Agent API", version="0.1.0")


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # MVP: allow running without auth (x-api-key optional). Harden later in Day 13.
    # If you want strict auth now, enforce required header here.
    _ = x_api_key


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/alerts/webhook")
def ingest_grafana_webhook(
    payload: GrafanaWebhookPayload, _: None = Depends(verify_api_key)
) -> dict:
    # Placeholder: Day 6 will normalize + write audit/pending/notify flows.
    return {"received": True, "title": payload.title, "status": payload.status}

