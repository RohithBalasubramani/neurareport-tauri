"""Webhook delivery tasks - durable via Dramatiq + Redis."""
from __future__ import annotations

import asyncio
import logging

import dramatiq

from backend.app.utils.ssrf_guard import validate_url

logger = logging.getLogger("neura.worker.webhooks")


@dramatiq.actor(
    queue_name="webhooks",
    max_retries=5,
    min_backoff=1000,
    max_backoff=120_000,
    time_limit=30_000,  # 30s
    store_results=True,
)
def send_webhook(url: str, payload: dict, headers: dict | None = None, method: str = "POST") -> dict:
    """Deliver a webhook notification with SSRF protection."""
    validate_url(url)
    from backend.app.services.export.service import distribution_service

    safe_headers = headers or {}
    safe_payload = payload or {}
    try:
        return asyncio.run(
            distribution_service.send_webhook(
                document_id=str(safe_payload.get("document_id") or "unknown"),
                webhook_url=url,
                method=method,
                headers=safe_headers,
                payload=safe_payload,
            )
        )
    except RuntimeError:
        return _run_webhook_in_loop(distribution_service, url, method, safe_headers, safe_payload)


def _run_webhook_in_loop(distribution_service, url: str, method: str, headers: dict, payload: dict) -> dict:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            distribution_service.send_webhook(
                document_id=str(payload.get("document_id") or "unknown"),
                webhook_url=url,
                method=method,
                headers=headers,
                payload=payload,
            )
        )
    finally:
        loop.close()

