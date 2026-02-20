# mypy: ignore-errors
"""
Enhanced Analysis Orchestrator - Main service that orchestrates all AI-powered analysis features.

This service coordinates:
- Intelligent Data Extraction
- AI-Powered Analysis Engines
- Intelligent Visualization
- Data Transformation & Export
- Advanced AI Features
- User Experience Features
- Integration Capabilities
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from backend.app.schemas.analyze.enhanced_analysis import (
    AnalysisDepth,
    AnalysisPreferences,
    ChartGenerationRequest,
    DocumentType,
    EnhancedAnalysisResult,
    ExportConfiguration,
    ExportFormat,
    QuestionRequest,
    QuestionResponse,
    SummaryMode,
)
from backend.app.services.analyze.enhanced_extraction_service import (
    EnhancedExtractionService,
)
from backend.app.services.analyze.analysis_engines import (
    AnalysisEngineService,
)
from backend.app.services.analyze.visualization_engine import (
    VisualizationEngine,
)
from backend.app.services.analyze.data_transform_export import (
    DataExportService,
)
from backend.app.services.analyze.advanced_ai_features import (
    AdvancedAIService,
)
from backend.app.services.analyze.user_experience import (
    UserExperienceService,
    StreamingAnalysisSession,
)
from backend.app.services.analyze.integrations import (
    IntegrationService,
)
from backend.app.services.analyze.extraction_pipeline import (
    ExtractedContent,
    extract_document_content,
    format_content_for_llm,
)
from backend.app.services.analyze.enhanced_analysis_store import get_analysis_store
from backend.app.services.llm.rag import RAGRetriever
from backend.app.services.utils.llm import call_chat_completion, call_chat_completion_async
from backend.app.services.llm.client import get_llm_client

logger = logging.getLogger("neura.analyze.orchestrator")


# In-memory cache for analysis results (bounded to prevent memory leaks)
_ANALYSIS_CACHE: Dict[str, EnhancedAnalysisResult] = {}
_ANALYSIS_CACHE_MAX = 500


def _cache_put(analysis_id: str, result: EnhancedAnalysisResult) -> None:
    """Add to cache with eviction when max size exceeded."""
    if len(_ANALYSIS_CACHE) >= _ANALYSIS_CACHE_MAX:
        # Evict oldest entry (first inserted)
        oldest_key = next(iter(_ANALYSIS_CACHE))
        del _ANALYSIS_CACHE[oldest_key]
    _ANALYSIS_CACHE[analysis_id] = result


def _generate_analysis_id() -> str:
    """Generate a unique analysis ID."""
    return f"eana_{uuid.uuid4().hex[:12]}"


def _detect_document_type(file_name: str) -> DocumentType:
    """Detect document type from file name."""
    name = file_name.lower()
    if name.endswith(".pdf"):
        return DocumentType.PDF
    elif name.endswith((".xlsx", ".xls", ".xlsm")):
        return DocumentType.EXCEL
    elif name.endswith(".csv"):
        return DocumentType.CSV
    elif name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        return DocumentType.IMAGE
    elif name.endswith((".doc", ".docx")):
        return DocumentType.WORD
    elif name.endswith(".txt"):
        return DocumentType.TEXT
    return DocumentType.UNKNOWN


class EnhancedAnalysisOrchestrator:
    """
    Main orchestrator for enhanced document analysis.

    Coordinates all AI-powered analysis features and provides
    a unified interface for the API layer.
    """

    def __init__(self):
        self.extraction_service = EnhancedExtractionService()
        self.analysis_engine = AnalysisEngineService()
        self.visualization_engine = VisualizationEngine()
        self.export_service = DataExportService()
        self.advanced_ai = AdvancedAIService()
        self.ux_service = UserExperienceService()
        self.integration_service = IntegrationService()
        self._rag_retrievers: Dict[str, RAGRetriever] = {}
        self._store = get_analysis_store()

    async def analyze_document_streaming(
        self,
        file_bytes: Optional[bytes],
        file_name: str,
        preferences: Optional[AnalysisPreferences] = None,
        correlation_id: Optional[str] = None,
        file_path: Optional[Path] = None,
        analysis_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Perform comprehensive document analysis with streaming progress updates.

        This is the main entry point for document analysis.
        """
        analysis_id = analysis_id or _generate_analysis_id()
        started = time.time()

        # Use default preferences if not provided
        if preferences is None:
            preferences = AnalysisPreferences()

        # Build configuration from preferences
        config = self.ux_service.build_configuration(preferences)

        # Create streaming session
        session = self.ux_service.create_streaming_session()

        warnings_list: List[str] = []

        try:
            # Stage 1: Upload validation
            yield self._event("stage", "Validating document...", 5, analysis_id, correlation_id)

            if not file_bytes and not file_path:
                yield self._event("error", "Empty file provided", 0, analysis_id, correlation_id)
                return

            document_type = _detect_document_type(file_name)

            # Stage 2: Content extraction (PDF/Excel parsing — no LLM)
            yield self._event("stage", "Extracting content from document...", 15, analysis_id, correlation_id)

            content = extract_document_content(
                file_bytes=file_bytes,
                file_path=file_path,
                file_name=file_name,
            )

            if content.errors and not content.tables_raw and not content.text_content:
                yield self._event("error", f"Could not extract content: {'; '.join(content.errors)}", 0, analysis_id, correlation_id)
                return

            if content.errors:
                warnings_list.extend(content.errors)

            text_len = len(content.text_content or "")
            yield self._event("stage", f"Extracted {text_len} chars, {len(content.tables_raw)} tables", 20, analysis_id, correlation_id)

            # Stage 3: Intelligent extraction (1 LLM call — runs in thread with progress ticks)
            yield self._event("stage", "Extracting entities & metrics with AI...", 30, analysis_id, correlation_id)

            try:
                extraction_task = asyncio.create_task(
                    asyncio.to_thread(
                        self.extraction_service.extract_all,
                        text=content.text_content,
                        raw_tables=content.tables_raw,
                    )
                )
                _pct = 30
                while not extraction_task.done():
                    await asyncio.sleep(2.0)
                    if extraction_task.done():
                        break
                    if _pct < 48:
                        _pct += 2
                        yield self._event("stage", "Extracting entities & metrics...", _pct, analysis_id, correlation_id)
                extraction_result = await extraction_task
            except Exception as exc:
                logger.error("Extraction stage failed: %s", exc, exc_info=True)
                yield self._event("stage", f"Extraction partially failed: {exc}", 35, analysis_id, correlation_id)
                warnings_list.append(f"AI extraction failed: {exc}")
                extraction_result = {
                    "tables": [], "entities": [], "metrics": [],
                    "forms": [], "invoices": [], "contracts": [],
                    "table_relationships": [],
                }

            tables = extraction_result["tables"]
            entities = extraction_result["entities"]
            metrics = extraction_result["metrics"]
            forms = extraction_result["forms"]
            invoices = extraction_result["invoices"]
            contracts = extraction_result["contracts"]
            table_relationships = extraction_result["table_relationships"]

            yield self._event("stage", f"Found {len(tables)} tables, {len(metrics)} metrics, {len(entities)} entities", 40, analysis_id, correlation_id)

            # Stage 4: AI Analysis — single consolidated LLM call (runs in thread with progress ticks)
            yield self._event("stage", "Running comprehensive AI analysis...", 50, analysis_id, correlation_id)

            try:
                analysis_task = asyncio.create_task(
                    asyncio.to_thread(
                        self.analysis_engine.run_all_analyses,
                        text=content.text_content,
                        tables=tables,
                        metrics=metrics,
                    )
                )
                _pct = 50
                while not analysis_task.done():
                    await asyncio.sleep(2.0)
                    if analysis_task.done():
                        break
                    if _pct < 63:
                        _pct += 2
                        yield self._event("stage", "Analyzing document...", _pct, analysis_id, correlation_id)
                analysis_results = await analysis_task
            except Exception as exc:
                logger.error("Analysis stage failed: %s", exc, exc_info=True)
                yield self._event("stage", f"AI analysis failed: {exc}", 55, analysis_id, correlation_id)
                warnings_list.append(f"AI analysis failed: {exc}")
                # Provide empty defaults so we can still return partial results
                from backend.app.schemas.analyze.enhanced_analysis import (
                    SentimentLevel, SentimentAnalysis as SA, TextAnalytics as TA,
                    StatisticalAnalysis as StA, FinancialAnalysis as FA,
                )
                analysis_results = {
                    "summaries": {},
                    "sentiment": SA(overall_sentiment=SentimentLevel.NEUTRAL, overall_score=0.0, confidence=0.0),
                    "text_analytics": TA(),
                    "statistical_analysis": StA(),
                    "financial_analysis": FA(metrics_found=len(metrics)),
                    "insights": [], "risks": [], "opportunities": [], "action_items": [],
                }

            summaries = analysis_results["summaries"]
            sentiment = analysis_results["sentiment"]
            text_analytics = analysis_results["text_analytics"]
            statistical_analysis = analysis_results["statistical_analysis"]
            financial_analysis = analysis_results["financial_analysis"]
            insights = analysis_results["insights"]
            risks = analysis_results["risks"]
            opportunities = analysis_results["opportunities"]
            action_items = analysis_results["action_items"]

            yield self._event("stage", f"Generated {len(insights)} insights, {len(risks)} risks", 65, analysis_id, correlation_id)

            # Stage 5: Visualization (no LLM — pattern detection + chart specs)
            yield self._event("stage", "Generating visualizations...", 70, analysis_id, correlation_id)

            try:
                viz_results = self.visualization_engine.generate_all_visualizations(
                    tables=tables,
                    metrics=metrics,
                    max_charts=preferences.max_charts,
                )
                charts = viz_results["charts"]
                viz_suggestions = viz_results["suggestions"]
            except Exception as exc:
                logger.warning("Visualization failed: %s", exc)
                warnings_list.append(f"Chart generation failed: {exc}")
                charts = []
                viz_suggestions = []

            yield self._event("stage", f"Created {len(charts)} charts", 75, analysis_id, correlation_id)

            # Stage 6: Data Quality (no LLM)
            yield self._event("stage", "Assessing data quality...", 80, analysis_id, correlation_id)

            try:
                data_quality = self.export_service.assess_quality(tables)
            except Exception as exc:
                logger.warning("Quality assessment failed: %s", exc)
                data_quality = {}

            # Stage 7: Build RAG index for Q&A (no LLM)
            yield self._event("stage", "Building knowledge index for Q&A...", 88, analysis_id, correlation_id)

            rag = RAGRetriever(use_embeddings=False)
            rag.add_document(
                content=content.text_content,
                doc_id=analysis_id,
                metadata={"file_name": file_name, "analysis_id": analysis_id},
            )
            self._rag_retrievers[analysis_id] = rag

            # Stage 8: Suggested questions (no LLM)
            suggested_questions = self.ux_service.generate_suggested_questions(
                tables=tables,
                metrics=metrics,
                entities=entities,
            )

            # Calculate processing time
            processing_time_ms = int((time.time() - started) * 1000)

            yield self._event("stage", "Finalizing results...", 95, analysis_id, correlation_id)

            # Build final result
            result = EnhancedAnalysisResult(
                analysis_id=analysis_id,
                document_name=file_name,
                document_type=document_type,
                created_at=datetime.now(timezone.utc),
                processing_time_ms=processing_time_ms,

                # Extraction
                tables=tables,
                entities=entities,
                metrics=metrics,
                forms=forms,
                invoices=invoices,
                contracts=contracts,
                table_relationships=table_relationships,

                # Analysis
                summaries=summaries,
                sentiment=sentiment,
                text_analytics=text_analytics,
                financial_analysis=financial_analysis,
                statistical_analysis=statistical_analysis,

                # Visualizations
                chart_suggestions=charts,
                visualization_suggestions=viz_suggestions,

                # Insights
                insights=insights,
                risks=risks,
                opportunities=opportunities,
                action_items=action_items,

                # Quality
                data_quality=data_quality,

                # Metadata
                page_count=content.page_count,
                total_tables=len(tables),
                total_entities=len(entities),
                total_metrics=len(metrics),
                confidence_score=0.85 if not warnings_list else 0.6,

                # Settings
                preferences=preferences,

                # Warnings
                warnings=warnings_list,
            )

            # Cache the result
            _cache_put(analysis_id, result)
            try:
                self._store.save_result(result)
                self._store.save_context(analysis_id, content.text_content)
            except Exception as exc:
                logger.warning(f"Failed to persist analysis result: {exc}")

            yield self._event("stage", "Complete", 100, analysis_id, correlation_id)

            # Final result event (use mode="json" for datetime serialization)
            result_dict = result.model_dump(mode="json")
            result_dict["event"] = "result"
            result_dict["suggested_questions"] = suggested_questions

            if correlation_id:
                result_dict["correlation_id"] = correlation_id

            yield result_dict

        except asyncio.CancelledError:
            yield self._event("cancelled", "Analysis cancelled", 0, analysis_id, correlation_id)
            raise
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            error_detail = str(e)
            if len(error_detail) > 200:
                error_detail = error_detail[:200] + "..."
            yield self._event("error", f"Analysis failed: {error_detail}", 0, analysis_id, correlation_id)

    def _event(
        self,
        event_type: str,
        detail: str,
        progress: int,
        analysis_id: str,
        correlation_id: Optional[str],
    ) -> Dict[str, Any]:
        """Build an event dict."""
        event = {
            "event": event_type if event_type != "stage" else "stage",
            "stage": event_type,
            "detail": detail,
            "progress": progress,
            "analysis_id": analysis_id,
        }
        if correlation_id:
            event["correlation_id"] = correlation_id
        return event

    def get_analysis(self, analysis_id: str) -> Optional[EnhancedAnalysisResult]:
        """Get a cached analysis result."""
        result = _ANALYSIS_CACHE.get(analysis_id)
        if result:
            return result
        stored = self._store.load_result(analysis_id)
        if stored:
            _cache_put(analysis_id, stored)
            if analysis_id not in self._rag_retrievers:
                text_content = self._store.load_context(analysis_id)
                if text_content:
                    rag = RAGRetriever(use_embeddings=False)
                    rag.add_document(
                        content=text_content,
                        doc_id=analysis_id,
                        metadata={"file_name": stored.document_name, "analysis_id": analysis_id},
                    )
                    self._rag_retrievers[analysis_id] = rag
        return stored

    def new_analysis_id(self) -> str:
        """Generate a new analysis ID."""
        return _generate_analysis_id()

    async def ask_question(
        self,
        analysis_id: str,
        question: str,
        include_sources: bool = True,
        max_context_chunks: int = 5,
    ) -> QuestionResponse:
        """Ask a question about the analyzed document."""
        # Get the analysis result
        result = self.get_analysis(analysis_id)
        if not result:
            return QuestionResponse(
                answer="Analysis not found. Please upload and analyze the document first.",
                confidence=0.0,
                sources=[],
                suggested_followups=[],
            )

        # Get RAG retriever
        rag = self._rag_retrievers.get(analysis_id)
        if not rag:
            return QuestionResponse(
                answer="Knowledge index not available. Please re-analyze the document.",
                confidence=0.0,
                sources=[],
                suggested_followups=[],
            )

        # Query with context (runs Claude CLI — must not block event loop)
        rag_result = await asyncio.to_thread(
            rag.query_with_context,
            question=question,
            top_k=max_context_chunks,
            include_sources=include_sources,
        )

        # Generate follow-up questions
        suggested_followups = await self._generate_followup_questions(question, rag_result["answer"])

        return QuestionResponse(
            answer=rag_result["answer"],
            confidence=0.8 if rag_result.get("context_used") else 0.5,
            sources=rag_result.get("sources", []) if include_sources else [],
            suggested_followups=suggested_followups,
        )

    async def _generate_followup_questions(self, question: str, answer: str) -> List[str]:
        """Generate follow-up questions based on Q&A."""
        try:
            client = get_llm_client()
            prompt = f"""Based on this Q&A, suggest 3 relevant follow-up questions.

Question: {question}
Answer: {answer[:500]}

Return JSON array of questions:
["Question 1", "Question 2", "Question 3"]"""

            response = await call_chat_completion_async(
                client,
                model=None,
                messages=[{"role": "user", "content": prompt}],
                description="followup_questions",
                temperature=0.5,
            )

            raw = response.choices[0].message.content or "[]"
            from backend.app.services.utils.llm import extract_json_array_from_llm_response
            result = extract_json_array_from_llm_response(raw, default=[])
            if result:
                return result
        except Exception as e:
            logger.warning(f"Follow-up generation failed: {e}")

        return []

    async def generate_charts_from_query(
        self,
        analysis_id: str,
        query: str,
        include_trends: bool = True,
        include_forecasts: bool = False,
    ) -> Dict[str, Any]:
        """Generate charts from natural language query.

        Returns dict with 'charts' list and optional 'message' string.
        """
        result = self.get_analysis(analysis_id)
        if not result:
            return {"charts": [], "message": "Analysis not found. Please re-analyze the document."}

        if not result.tables:
            return {"charts": [], "message": "No tables were extracted from this document. Chart generation requires tabular data."}

        # Chart generation + intelligence both call Claude CLI — run in thread
        def _generate_sync():
            charts = self.visualization_engine.generate_from_query(
                query=query,
                tables=result.tables,
                metrics=result.metrics,
            )
            if include_trends or include_forecasts:
                charts = [
                    self.visualization_engine.add_intelligence_to_chart(
                        chart,
                        include_forecast=include_forecasts,
                    )
                    for chart in charts
                ]
            return charts

        try:
            charts = await asyncio.to_thread(_generate_sync)
        except Exception as exc:
            logger.error("Chart generation failed: %s", exc, exc_info=True)
            return {"charts": [], "message": f"Chart generation failed: {exc}"}

        if not charts:
            return {"charts": [], "message": "AI could not generate charts for this query. Try rephrasing or be more specific about the data you want to visualize."}

        return {"charts": [c.model_dump() for c in charts]}

    async def export_analysis(
        self,
        analysis_id: str,
        format: ExportFormat,
        include_raw_data: bool = True,
        include_charts: bool = True,
    ) -> tuple[bytes, str]:
        """Export analysis in specified format."""
        result = self.get_analysis(analysis_id)
        if not result:
            raise ValueError(f"Analysis not found: {analysis_id}")

        config = ExportConfiguration(
            format=format,
            include_raw_data=include_raw_data,
            include_charts=include_charts,
            include_analysis=True,
            include_insights=True,
        )

        return await self.export_service.export(result, config)

    async def compare_documents(
        self,
        analysis_id_1: str,
        analysis_id_2: str,
    ) -> Dict[str, Any]:
        """Compare two analyzed documents."""
        result1 = self.get_analysis(analysis_id_1)
        result2 = self.get_analysis(analysis_id_2)

        if not result1 or not result2:
            return {"error": "One or both analyses not found"}

        from backend.app.services.analyze.analysis_engines import compare_documents

        # Get text content from summaries
        text1 = result1.summaries.get("comprehensive", result1.summaries.get("executive"))
        text2 = result2.summaries.get("comprehensive", result2.summaries.get("executive"))

        text1_content = text1.content if text1 else ""
        text2_content = text2.content if text2 else ""

        comparison = compare_documents(
            text1=text1_content,
            text2=text2_content,
            metrics1=result1.metrics,
            metrics2=result2.metrics,
        )

        return comparison.model_dump()

    def get_industry_options(self) -> List[Dict[str, Any]]:
        """Get available industry options."""
        return self.ux_service.get_industry_options()

    def get_export_formats(self) -> List[Dict[str, str]]:
        """Get available export formats."""
        return [
            {"value": f.value, "label": f.value.upper()}
            for f in ExportFormat
        ]


# Singleton instance
_orchestrator: Optional[EnhancedAnalysisOrchestrator] = None


def get_orchestrator() -> EnhancedAnalysisOrchestrator:
    """Get the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EnhancedAnalysisOrchestrator()
    return _orchestrator
