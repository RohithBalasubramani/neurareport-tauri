# mypy: ignore-errors
"""Document analysis service that orchestrates extraction and LLM processing."""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

from backend.app.services.config import get_settings
from backend.app.schemas.analyze.analysis import (
    AnalysisResult,
    AnalysisSuggestChartsPayload,
    ExtractedDataPoint,
    ExtractedTable,
    FieldInfo,
    TimeSeriesCandidate,
)
from backend.app.schemas.generate.charts import ChartSpec
from backend.app.services.prompts.llm_prompts_analysis import (
    build_analysis_prompt,
    build_chart_suggestion_prompt,
    infer_data_type,
    parse_analysis_response,
    strip_code_fences,
)
from backend.app.services.llm.client import get_llm_client
from backend.app.utils.fs import write_json_atomic
from backend.app.services.utils.llm import call_chat_completion, call_chat_completion_async

from .extraction_pipeline import (
    ExtractedContent,
    extract_document_content,
    format_content_for_llm,
)

logger = logging.getLogger("neura.analyze.service")


@dataclass
class CacheEntry:
    """Cache entry with TTL support."""
    value: AnalysisResult
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)


class TTLCache:
    """Thread-safe TTL cache with LRU eviction and size limits."""

    def __init__(self, max_items: int = 100, ttl_seconds: int = 3600):
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._eviction_threshold = max(1, max_items * 8 // 10)  # Evict until at 80% capacity

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry has expired based on TTL from creation time."""
        return time.time() - entry.created_at > self.ttl_seconds

    def _evict_stale(self) -> int:
        """Remove expired entries. Returns number of entries evicted."""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now - entry.created_at > self.ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"Evicted {len(expired_keys)} stale cache entries")
        return len(expired_keys)

    def _evict_lru(self) -> int:
        """
        Evict least recently used entries if at or over capacity.
        Evicts until cache size is below 80% of max_items.
        Returns number of entries evicted.
        """
        if len(self._cache) < self.max_items:
            return 0

        # Sort by last_accessed (least recent first)
        sorted_keys = sorted(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed,
        )

        # Evict until below threshold
        num_to_evict = len(self._cache) - self._eviction_threshold
        num_to_evict = max(1, num_to_evict)  # At least evict 1

        for key in sorted_keys[:num_to_evict]:
            del self._cache[key]

        logger.debug(f"LRU evicted {num_to_evict} cache entries, size now {len(self._cache)}")
        return num_to_evict

    def get(self, key: str) -> Optional[AnalysisResult]:
        """Get value from cache, returns None if not found or expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if self._is_expired(entry):
                del self._cache[key]
                logger.debug(f"Cache entry {key} expired on access")
                return None
            # Update last accessed time
            entry.last_accessed = time.time()
            return entry.value

    def set(self, key: str, value: AnalysisResult) -> None:
        """Set value in cache with automatic eviction."""
        with self._lock:
            # Evict stale entries first
            self._evict_stale()
            # Then evict LRU if still at capacity
            self._evict_lru()
            # Add new entry
            self._cache[key] = CacheEntry(value=value)
            logger.debug(f"Cache set {key}, size now {len(self._cache)}")

    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None

    def size(self) -> int:
        """Return current cache size."""
        with self._lock:
            return len(self._cache)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            logger.debug("Cache cleared")


_ANALYSIS_CACHE: TTLCache | None = None
_ANALYSIS_SEMAPHORE: asyncio.Semaphore | None = None


def _analysis_cache() -> TTLCache:
    global _ANALYSIS_CACHE
    if _ANALYSIS_CACHE is None:
        settings = get_settings()
        _ANALYSIS_CACHE = TTLCache(
            max_items=settings.analysis_cache_max_items,
            ttl_seconds=settings.analysis_cache_ttl_seconds,
        )
    return _ANALYSIS_CACHE


def _analysis_size_limits() -> tuple[int, int]:
    override = os.getenv("ANALYZE_MAX_FILE_SIZE_MB")
    if override:
        try:
            mb = int(override)
        except ValueError:
            mb = None
        if mb and mb > 0:
            return mb * 1024 * 1024, mb
    max_bytes = get_settings().max_upload_bytes
    max_mb = max(1, int(max_bytes / (1024 * 1024)))
    return max_bytes, max_mb


def _analysis_persist_ttl_seconds() -> Optional[int]:
    raw = os.getenv("NEURA_ANALYSIS_PERSIST_TTL_SECONDS")
    if raw is None or raw == "":
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _analysis_store_dir() -> Path:
    base = get_settings().state_dir / "analysis_cache"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _analysis_store_path(analysis_id: str) -> Path:
    safe_id = str(analysis_id or "").strip()
    return _analysis_store_dir() / f"{safe_id}.json"


def _parse_analysis_result(payload: dict[str, Any]) -> AnalysisResult:
    if hasattr(AnalysisResult, "model_validate"):
        return AnalysisResult.model_validate(payload)
    return AnalysisResult.parse_obj(payload)


def _persist_analysis_result(result: AnalysisResult) -> None:
    try:
        path = _analysis_store_path(result.analysis_id)
        write_json_atomic(
            path,
            {
                "analysis_id": result.analysis_id,
                "created_at": time.time(),
                "result": result.model_dump(),
            },
            ensure_ascii=False,
            indent=2,
            step="analysis_store",
        )
    except Exception as exc:
        logger.warning("analysis_persist_failed", extra={"event": "analysis_persist_failed", "error": str(exc)})


def _load_persisted_analysis(analysis_id: str) -> Optional[AnalysisResult]:
    path = _analysis_store_path(analysis_id)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("analysis_persist_read_failed", extra={"event": "analysis_persist_read_failed", "error": str(exc)})
        return None

    created_at = payload.get("created_at") if isinstance(payload, dict) else None
    ttl = _analysis_persist_ttl_seconds()
    if ttl and isinstance(created_at, (int, float)) and time.time() - float(created_at) > ttl:
        with contextlib.suppress(Exception):
            path.unlink(missing_ok=True)
        return None

    result_payload = payload.get("result") if isinstance(payload, dict) else payload
    if not isinstance(result_payload, dict):
        return None
    try:
        return _parse_analysis_result(result_payload)
    except Exception as exc:
        logger.warning("analysis_persist_parse_failed", extra={"event": "analysis_persist_parse_failed", "error": str(exc)})
        return None


def _get_analysis_semaphore() -> asyncio.Semaphore:
    global _ANALYSIS_SEMAPHORE
    if _ANALYSIS_SEMAPHORE is None:
        settings = get_settings()
        _ANALYSIS_SEMAPHORE = asyncio.Semaphore(max(1, int(settings.analysis_max_concurrency or 1)))
    return _ANALYSIS_SEMAPHORE


def _generate_analysis_id() -> str:
    """Generate a unique analysis ID."""
    return f"ana_{uuid.uuid4().hex[:12]}"


def _attach_event_metadata(
    payload: dict[str, Any],
    analysis_id: str,
    correlation_id: Optional[str],
) -> dict[str, Any]:
    payload["analysis_id"] = analysis_id
    if correlation_id:
        payload["correlation_id"] = correlation_id
    return payload


def _convert_llm_tables_to_schema(llm_tables: list[dict[str, Any]]) -> list[ExtractedTable]:
    """Convert LLM-extracted tables to schema objects."""
    result: list[ExtractedTable] = []
    for idx, table in enumerate(llm_tables):
        try:
            result.append(ExtractedTable(
                id=table.get("id", f"table_{idx + 1}"),
                title=table.get("title"),
                headers=table.get("headers", []),
                rows=table.get("rows", []),
                data_types=table.get("data_types"),
                source_page=table.get("source_page"),
                source_sheet=table.get("source_sheet"),
            ))
        except Exception as exc:
            logger.warning(f"Failed to convert table {idx}: {exc}")
    return result


def _convert_llm_metrics_to_schema(llm_metrics: list[dict[str, Any]]) -> list[ExtractedDataPoint]:
    """Convert LLM-extracted metrics to schema objects."""
    result: list[ExtractedDataPoint] = []
    for metric in llm_metrics:
        try:
            result.append(ExtractedDataPoint(
                key=metric.get("name", "Unknown"),
                value=metric.get("value"),
                data_type="numeric" if isinstance(metric.get("value"), (int, float)) else "text",
                unit=metric.get("unit"),
                context=metric.get("context"),
            ))
        except Exception as exc:
            logger.warning(f"Failed to convert metric: {exc}")
    return result


def _convert_llm_time_series_to_schema(llm_ts: list[dict[str, Any]]) -> list[TimeSeriesCandidate]:
    """Convert LLM time series candidates to schema objects."""
    result: list[TimeSeriesCandidate] = []
    for ts in llm_ts:
        try:
            result.append(TimeSeriesCandidate(
                date_column=ts.get("date_column", ""),
                value_columns=ts.get("value_columns", []),
                frequency=ts.get("frequency"),
                table_id=ts.get("table_id"),
            ))
        except Exception as exc:
            logger.warning(f"Failed to convert time series: {exc}")
    return result


def _convert_llm_charts_to_schema(llm_charts: list[dict[str, Any]]) -> list[ChartSpec]:
    """Convert LLM chart recommendations to ChartSpec objects."""
    result: list[ChartSpec] = []
    for idx, chart in enumerate(llm_charts):
        try:
            chart_type = chart.get("type", "bar").lower()
            if chart_type not in ("line", "bar", "pie", "scatter"):
                chart_type = "bar"

            y_fields = chart.get("y_fields") or chart.get("yFields") or []
            if isinstance(y_fields, str):
                y_fields = [y_fields]

            result.append(ChartSpec(
                id=chart.get("id", f"chart_{idx + 1}"),
                type=chart_type,
                xField=chart.get("x_field") or chart.get("xField") or "",
                yFields=y_fields,
                groupField=chart.get("group_field") or chart.get("groupField"),
                aggregation=chart.get("aggregation"),
                title=chart.get("title"),
                description=chart.get("description") or chart.get("rationale"),
            ))
        except Exception as exc:
            logger.warning(f"Failed to convert chart {idx}: {exc}")
    return result


def _build_field_catalog(tables: list[ExtractedTable]) -> list[FieldInfo]:
    """Build field catalog from extracted tables."""
    fields: list[FieldInfo] = []
    seen_names: set[str] = set()

    for table in tables:
        for idx, header in enumerate(table.headers):
            if header in seen_names:
                continue
            seen_names.add(header)

            data_type = "text"
            if table.data_types and idx < len(table.data_types):
                data_type = table.data_types[idx]

            sample_values: list[Any] = []
            for row in table.rows[:5]:
                if idx < len(row):
                    sample_values.append(row[idx])

            fields.append(FieldInfo(
                name=header,
                type=data_type,
                sample_values=sample_values[:3] if sample_values else None,
            ))

    return fields


def _build_raw_data(tables: list[ExtractedTable], max_rows: int = 500) -> list[dict[str, Any]]:
    """Flatten extracted tables into raw data records."""
    raw_data: list[dict[str, Any]] = []

    for table in tables:
        for row in table.rows[:max_rows]:
            record: dict[str, Any] = {}
            for idx, header in enumerate(table.headers):
                if idx < len(row):
                    record[header] = row[idx]
            if record:
                raw_data.append(record)

        if len(raw_data) >= max_rows:
            break

    return raw_data[:max_rows]


def _merge_extracted_tables(
    content_tables: list[dict[str, Any]],
    llm_tables: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge tables from extraction pipeline with LLM-enhanced tables."""
    if not llm_tables:
        return content_tables

    merged_ids = {t.get("id") for t in content_tables}
    merged = list(content_tables)

    for llm_table in llm_tables:
        llm_id = llm_table.get("id")
        if llm_id and llm_id not in merged_ids:
            merged.append(llm_table)
            merged_ids.add(llm_id)

    return merged


async def analyze_document_streaming(
    file_name: str,
    file_bytes: bytes | None = None,
    file_path: Path | str | None = None,
    template_id: Optional[str] = None,
    connection_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Analyze a document with streaming progress updates."""
    analysis_id = _generate_analysis_id()
    started = time.time()
    max_bytes, max_mb = _analysis_size_limits()
    resolved_path = Path(file_path) if file_path else None

    if resolved_path and not file_name:
        file_name = resolved_path.name

    semaphore = _get_analysis_semaphore()
    async with semaphore:
        yield _attach_event_metadata(
            {"event": "stage", "stage": "uploading", "progress": 10},
            analysis_id,
            correlation_id,
        )

        if file_bytes is None and resolved_path is None:
            yield _attach_event_metadata(
                {"event": "error", "detail": "Empty file provided."},
                analysis_id,
                correlation_id,
            )
            return
        if file_bytes is not None:
            if len(file_bytes) > max_bytes:
                yield _attach_event_metadata(
                    {"event": "error", "detail": f"File too large. Maximum size is {max_mb}MB."},
                    analysis_id,
                    correlation_id,
                )
                return
        elif resolved_path is not None:
            try:
                size_bytes = resolved_path.stat().st_size
            except Exception as exc:
                yield _attach_event_metadata(
                    {"event": "error", "detail": f"Failed to read file size: {exc}"},
                    analysis_id,
                    correlation_id,
                )
                return
            if size_bytes > max_bytes:
                yield _attach_event_metadata(
                    {"event": "error", "detail": f"File too large. Maximum size is {max_mb}MB."},
                    analysis_id,
                    correlation_id,
                )
                return

        yield _attach_event_metadata(
            {"event": "stage", "stage": "parsing", "progress": 20, "detail": "Extracting content..."},
            analysis_id,
            correlation_id,
        )

        content = await asyncio.to_thread(
            extract_document_content,
            file_path=resolved_path,
            file_bytes=file_bytes,
            file_name=file_name,
        )

        if content.errors and not content.tables_raw and not content.text_content:
            yield _attach_event_metadata(
                {"event": "error", "detail": f"Failed to extract content: {'; '.join(content.errors)}"},
                analysis_id,
                correlation_id,
            )
            return

        yield _attach_event_metadata(
            {
                "event": "stage",
                "stage": "table_extraction",
                "progress": 40,
                "detail": f"Found {len(content.tables_raw)} tables",
            },
            analysis_id,
            correlation_id,
        )

        yield _attach_event_metadata(
            {"event": "stage", "stage": "llm_analysis", "progress": 60, "detail": "Analyzing with AI..."},
            analysis_id,
            correlation_id,
        )

        llm_result = {"tables": [], "key_metrics": [], "time_series_candidates": [], "chart_recommendations": []}

        try:
            client = get_llm_client()
            formatted_content = format_content_for_llm(content)

            prompt = build_analysis_prompt(
                document_type=content.document_type,
                file_name=content.file_name,
                page_count=content.page_count,
                extracted_content=formatted_content,
            )

            messages = [{"role": "user", "content": prompt}]

            response = await call_chat_completion_async(
                client,
                model=None,
                messages=messages,
                description="document_analysis",
                temperature=0.2,
            )

            raw_text = ""
            if hasattr(response, "choices") and response.choices:
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    raw_text = choice.message.content or ""

            llm_result = parse_analysis_response(raw_text)

        except Exception as exc:
            logger.warning(f"LLM analysis failed: {exc}")
            yield _attach_event_metadata(
                {
                    "event": "stage",
                    "stage": "llm_analysis",
                    "progress": 70,
                    "detail": "AI analysis skipped (using extracted data)",
                },
                analysis_id,
                correlation_id,
            )

        yield _attach_event_metadata(
            {"event": "stage", "stage": "chart_generation", "progress": 80, "detail": "Generating visualizations..."},
            analysis_id,
            correlation_id,
        )

        merged_tables = _merge_extracted_tables(content.tables_raw, llm_result.get("tables", []))
        tables = _convert_llm_tables_to_schema(merged_tables)
        data_points = _convert_llm_metrics_to_schema(llm_result.get("key_metrics", []))
        time_series = _convert_llm_time_series_to_schema(llm_result.get("time_series_candidates", []))
        charts = _convert_llm_charts_to_schema(llm_result.get("chart_recommendations", []))

        if not charts and tables:
            charts = _generate_fallback_charts(tables)

        field_catalog = _build_field_catalog(tables)
        raw_data = _build_raw_data(tables)

        processing_time_ms = int((time.time() - started) * 1000)

        warnings: list[str] = []
        if content.errors:
            warnings.extend(content.errors)

        result = AnalysisResult(
            analysis_id=analysis_id,
            document_name=file_name,
            document_type=content.document_type,
            processing_time_ms=processing_time_ms,
            summary=llm_result.get("summary"),
            tables=tables,
            data_points=data_points,
            time_series_candidates=time_series,
            chart_suggestions=charts,
            raw_data=raw_data,
            field_catalog=field_catalog,
            template_id=template_id,
            warnings=warnings,
        )

        _analysis_cache().set(analysis_id, result)
        _persist_analysis_result(result)

        yield _attach_event_metadata(
            {"event": "stage", "stage": "complete", "progress": 100},
            analysis_id,
            correlation_id,
        )

        result_payload = {"event": "result", **result.model_dump()}
        if correlation_id:
            result_payload["correlation_id"] = correlation_id
        yield result_payload


def _generate_fallback_charts(tables: list[ExtractedTable]) -> list[ChartSpec]:
    """Generate basic chart suggestions when LLM doesn't provide any."""
    charts: list[ChartSpec] = []

    for table in tables[:3]:
        datetime_cols: list[str] = []
        numeric_cols: list[str] = []
        text_cols: list[str] = []

        for idx, header in enumerate(table.headers):
            data_type = table.data_types[idx] if table.data_types and idx < len(table.data_types) else "text"
            if data_type in ("datetime", "date"):
                datetime_cols.append(header)
            elif data_type == "numeric":
                numeric_cols.append(header)
            else:
                text_cols.append(header)

        if datetime_cols and numeric_cols:
            charts.append(ChartSpec(
                id=f"fallback_line_{table.id}",
                type="line",
                xField=datetime_cols[0],
                yFields=numeric_cols[:3],
                title=f"Time Series: {table.title or table.id}",
                description="Numeric values over time",
            ))

        if text_cols and numeric_cols:
            charts.append(ChartSpec(
                id=f"fallback_bar_{table.id}",
                type="bar",
                xField=text_cols[0],
                yFields=numeric_cols[:2],
                title=f"Comparison: {table.title or table.id}",
                description="Numeric values by category",
            ))

    return charts[:5]


def get_analysis(analysis_id: str) -> Optional[AnalysisResult]:
    """Retrieve a cached analysis result."""
    cached = _analysis_cache().get(analysis_id)
    if cached is not None:
        return cached
    persisted = _load_persisted_analysis(analysis_id)
    if persisted is not None:
        _analysis_cache().set(analysis_id, persisted)
    return persisted


def get_analysis_data(analysis_id: str) -> Optional[list[dict[str, Any]]]:
    """Get raw data for an analysis."""
    result = get_analysis(analysis_id)
    if result:
        return result.raw_data
    return None


def suggest_charts_for_analysis(
    analysis_id: str,
    payload: AnalysisSuggestChartsPayload,
) -> list[ChartSpec]:
    """Generate additional chart suggestions for an existing analysis."""
    result = get_analysis(analysis_id)
    if not result:
        return []

    try:
        client = get_llm_client()

        data_summary = f"Document: {result.document_name}\n"
        data_summary += f"Tables: {len(result.tables)}\n"
        for table in result.tables[:5]:
            data_summary += f"  - {table.title or table.id}: {len(table.rows)} rows, columns: {', '.join(table.headers[:5])}\n"

        field_catalog_str = "\n".join([
            f"  - {f.name}: {f.type}" + (f" (samples: {f.sample_values})" if f.sample_values else "")
            for f in result.field_catalog[:20]
        ])

        prompt = build_chart_suggestion_prompt(
            data_summary=data_summary,
            field_catalog=field_catalog_str,
            user_question=payload.question,
        )

        messages = [{"role": "user", "content": prompt}]

        response = call_chat_completion(
            client,
            model=None,
            messages=messages,
            description="chart_suggestion_analysis",
            temperature=0.3,
        )

        raw_text = ""
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                raw_text = choice.message.content or ""

        cleaned = strip_code_fences(raw_text)
        data = json.loads(cleaned)
        charts = data.get("charts", [])
        return _convert_llm_charts_to_schema(charts)

    except Exception as exc:
        logger.warning(f"Chart suggestion failed: {exc}")
        return _generate_fallback_charts(result.tables)


__all__ = [
    "analyze_document_streaming",
    "get_analysis",
    "get_analysis_data",
    "suggest_charts_for_analysis",
]
