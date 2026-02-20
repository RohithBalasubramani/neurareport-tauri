"""Export tasks - durable via Dramatiq + Redis."""
from __future__ import annotations

import asyncio
import logging

import dramatiq

logger = logging.getLogger("neura.worker.exports")


@dramatiq.actor(
    queue_name="exports",
    max_retries=2,
    min_backoff=3000,
    max_backoff=60000,
    time_limit=300_000,  # 5 min
    store_results=True,
)
def export_document(document_id: str, output_format: str, options: dict | None = None) -> dict:
    """Create an export job for a document.

    Note: The export service currently persists jobs and returns metadata; actual
    export execution can be implemented as a follow-up step without changing the
    task contract.
    """
    from backend.app.services.export.service import export_service

    opts = options or {}
    try:
        return asyncio.run(export_service.create_export_job(document_id=document_id, format=output_format, options=opts))
    except RuntimeError:
        # If already in an event loop (rare in worker context), run synchronously.
        return _run_export_in_loop(export_service, document_id, output_format, opts)


def _run_export_in_loop(export_service, document_id: str, output_format: str, opts: dict) -> dict:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            export_service.create_export_job(document_id=document_id, format=output_format, options=opts)
        )
    finally:
        loop.close()

