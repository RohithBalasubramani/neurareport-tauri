"""Document AI API Routes.

REST API endpoints for document intelligence - parsing, classification, and analysis.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from backend.app.schemas.docai import (
    ClassifyRequest,
    ClassifyResponse,
    CompareRequest,
    CompareResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ContractAnalyzeRequest,
    ContractAnalyzeResponse,
    EntityExtractRequest,
    EntityExtractResponse,
    InvoiceParseRequest,
    InvoiceParseResponse,
    MultiDocSummarizeRequest,
    MultiDocSummarizeResponse,
    ReceiptScanRequest,
    ReceiptScanResponse,
    ResumeParseRequest,
    ResumeParseResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from backend.app.services.docai import docai_service
from backend.app.services.security import require_api_key

logger = logging.getLogger("neura.api.docai")

router = APIRouter(tags=["docai"], dependencies=[Depends(require_api_key)])


def _handle_docai_error(exc: Exception, operation: str) -> HTTPException:
    """Map docai service errors to HTTP status codes."""
    logger.error("%s failed: %s", operation, exc, exc_info=True)
    return HTTPException(
        status_code=500,
        detail=f"{operation} failed due to an internal error.",
    )


# Document Parsing Endpoints


@router.post("/parse/invoice", response_model=InvoiceParseResponse)
async def parse_invoice(request: InvoiceParseRequest):
    """Parse an invoice document and extract structured data.

    Extracts invoice number, dates, vendor/billing info, line items,
    and totals from invoice documents (PDF, images, or text).
    """
    try:
        return await docai_service.parse_invoice(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Invoice parsing") from exc


@router.post("/parse/contract", response_model=ContractAnalyzeResponse)
async def analyze_contract(request: ContractAnalyzeRequest):
    """Analyze a contract document.

    Extracts parties, clauses, obligations, key dates, and performs
    risk analysis on contract documents.
    """
    try:
        return await docai_service.analyze_contract(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Contract analysis") from exc


@router.post("/parse/resume", response_model=ResumeParseResponse)
async def parse_resume(request: ResumeParseRequest):
    """Parse a resume/CV document.

    Extracts contact info, education, work experience, skills,
    certifications, and can optionally match against a job description.
    """
    try:
        return await docai_service.parse_resume(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Resume parsing") from exc


@router.post("/parse/receipt", response_model=ReceiptScanResponse)
async def scan_receipt(request: ReceiptScanRequest):
    """Scan a receipt document.

    Extracts merchant info, date/time, line items, totals, and
    payment information from receipt images or PDFs.
    """
    try:
        return await docai_service.scan_receipt(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Receipt scanning") from exc


# Document Classification


@router.post("/classify", response_model=ClassifyResponse)
async def classify_document(request: ClassifyRequest):
    """Classify a document by type.

    Determines document category (invoice, contract, resume, receipt, etc.)
    and suggests appropriate parsers for further processing.
    """
    try:
        return await docai_service.classify_document(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Document classification") from exc


# Entity Extraction


@router.post("/entities", response_model=EntityExtractResponse)
async def extract_entities(request: EntityExtractRequest):
    """Extract named entities from a document.

    Identifies and extracts entities like persons, organizations,
    locations, dates, monetary values, emails, phones, and URLs.
    """
    try:
        return await docai_service.extract_entities(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Entity extraction") from exc


# Semantic Search


@router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search across documents.

    Uses embeddings to find semantically similar content
    rather than exact keyword matches.
    """
    try:
        return await docai_service.semantic_search(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Semantic search") from exc


# Document Comparison


@router.post("/compare", response_model=CompareResponse)
async def compare_documents(request: CompareRequest):
    """Compare two documents.

    Calculates similarity, identifies differences, and optionally
    performs semantic comparison to find meaningful changes.
    """
    try:
        return await docai_service.compare_documents(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Document comparison") from exc


# Compliance Checking


@router.post("/compliance", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """Check document for regulatory compliance.

    Analyzes document against specified regulations (GDPR, HIPAA, SOC2)
    and identifies violations and recommendations.
    """
    try:
        return await docai_service.check_compliance(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Compliance check") from exc


# Multi-document Summary


@router.post("/summarize/multi", response_model=MultiDocSummarizeResponse)
async def summarize_multiple(request: MultiDocSummarizeRequest):
    """Summarize multiple documents.

    Creates a unified summary across multiple documents,
    identifying key points and common themes with source references.
    """
    try:
        return await docai_service.summarize_multiple(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise _handle_docai_error(exc, "Multi-document summarization") from exc
