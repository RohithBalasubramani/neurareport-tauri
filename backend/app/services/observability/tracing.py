"""
OpenTelemetry tracing setup for FastAPI.

Configures:
1. TracerProvider with service.name resource
2. BatchSpanProcessor exporting to OTLP endpoint (Tempo/Collector)
3. Automatic FastAPI instrumentation (spans for all HTTP requests)
4. Log correlation (trace_id, span_id injected into log records)

Based on: blueswen/fastapi-observability + opentelemetry-python SDK
"""
from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.types import ASGIApp

logger = logging.getLogger("neura.observability")


def setup_tracing(
    app: ASGIApp,
    service_name: str = "neurareport-backend",
    otlp_endpoint: str = "localhost:4317",
    log_correlation: bool = True,
    service_version: str = "dev",
    deployment_environment: str = "production",
) -> None:
    resource = Resource.create(attributes={
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": deployment_environment,
    })
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    )
    if log_correlation:
        LoggingInstrumentor().instrument(set_logging_format=True)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    logger.info("tracing_configured", extra={"event": "tracing_configured", "endpoint": otlp_endpoint})
