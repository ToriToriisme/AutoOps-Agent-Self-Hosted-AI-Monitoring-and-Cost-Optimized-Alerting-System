from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GrafanaWebhookPayload(BaseModel):
    # Keep this flexible: Grafana webhook payload can differ by contact point/version.
    title: str = Field(default="")
    message: str | None = None
    status: str | None = None
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    labels: dict[str, Any] = Field(default_factory=dict)
    annotations: dict[str, Any] = Field(default_factory=dict)

