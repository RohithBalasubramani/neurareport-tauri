"""Document AI Schemas.

Pydantic models for document intelligence - parsing, classification, and analysis.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentCategory(str, Enum):
    """Document classification categories."""
    INVOICE = "invoice"
    CONTRACT = "contract"
    RESUME = "resume"
    RECEIPT = "receipt"
    REPORT = "report"
    LETTER = "letter"
    FORM = "form"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    OTHER = "other"


class ConfidenceLevel(str, Enum):
    """Confidence level for extracted data."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Invoice Parsing Schemas


class InvoiceLineItem(BaseModel):
    """Line item from an invoice."""
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: float
    tax: Optional[float] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class InvoiceAddress(BaseModel):
    """Address structure for invoice parties."""
    name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class InvoiceParseRequest(BaseModel):
    """Request to parse an invoice."""
    file_path: Optional[str] = None
    content: Optional[str] = None  # Base64 encoded
    extract_line_items: bool = True
    extract_addresses: bool = True
    language: str = "en"


class InvoiceParseResponse(BaseModel):
    """Parsed invoice data."""
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    vendor: Optional[InvoiceAddress] = None
    bill_to: Optional[InvoiceAddress] = None
    ship_to: Optional[InvoiceAddress] = None
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    subtotal: Optional[float] = None
    tax_total: Optional[float] = None
    discount: Optional[float] = None
    total: Optional[float] = None
    currency: str = "USD"
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    raw_text: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int


# Contract Analysis Schemas


class ContractClauseType(str, Enum):
    """Types of contract clauses."""
    TERMINATION = "termination"
    INDEMNIFICATION = "indemnification"
    LIMITATION_OF_LIABILITY = "limitation_of_liability"
    CONFIDENTIALITY = "confidentiality"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    FORCE_MAJEURE = "force_majeure"
    GOVERNING_LAW = "governing_law"
    DISPUTE_RESOLUTION = "dispute_resolution"
    ASSIGNMENT = "assignment"
    AMENDMENT = "amendment"
    SEVERABILITY = "severability"
    NOTICE = "notice"
    PAYMENT = "payment"
    WARRANTY = "warranty"
    INSURANCE = "insurance"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class ContractClause(BaseModel):
    """Extracted contract clause."""
    clause_type: ContractClauseType
    title: str
    text: str
    page_number: Optional[int] = None
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    risk_level: RiskLevel = RiskLevel.INFORMATIONAL
    risk_explanation: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class ContractParty(BaseModel):
    """Party to a contract."""
    name: str
    role: str  # e.g., "Buyer", "Seller", "Licensor"
    address: Optional[str] = None
    contact: Optional[str] = None


class ContractAnalyzeRequest(BaseModel):
    """Request to analyze a contract."""
    file_path: Optional[str] = None
    content: Optional[str] = None  # Base64 encoded
    analyze_risks: bool = True
    extract_obligations: bool = True
    compare_to_standard: bool = False
    language: str = "en"


class ContractObligation(BaseModel):
    """Obligation extracted from contract."""
    party: str
    obligation: str
    deadline: Optional[str] = None
    penalty: Optional[str] = None
    clause_reference: Optional[str] = None


class ContractAnalyzeResponse(BaseModel):
    """Analyzed contract data."""
    title: Optional[str] = None
    contract_type: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    parties: List[ContractParty] = Field(default_factory=list)
    clauses: List[ContractClause] = Field(default_factory=list)
    obligations: List[ContractObligation] = Field(default_factory=list)
    key_dates: Dict[str, datetime] = Field(default_factory=dict)
    total_value: Optional[float] = None
    currency: Optional[str] = None
    risk_summary: Dict[str, int] = Field(default_factory=dict)
    overall_risk_level: RiskLevel = RiskLevel.INFORMATIONAL
    recommendations: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int


# Resume Parsing Schemas


class Education(BaseModel):
    """Education entry from resume."""
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[float] = None
    honors: Optional[str] = None


class WorkExperience(BaseModel):
    """Work experience entry from resume."""
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class ResumeParseRequest(BaseModel):
    """Request to parse a resume."""
    file_path: Optional[str] = None
    content: Optional[str] = None  # Base64 encoded
    extract_skills: bool = True
    match_job_description: Optional[str] = None
    language: str = "en"


class ResumeParseResponse(BaseModel):
    """Parsed resume data."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    education: List[Education] = Field(default_factory=list)
    experience: List[WorkExperience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    total_years_experience: Optional[float] = None
    job_match_score: Optional[float] = None
    job_match_details: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int


# Receipt Scanning Schemas


class ReceiptItem(BaseModel):
    """Item from a receipt."""
    name: str
    quantity: float = 1.0
    unit_price: Optional[float] = None
    total_price: float
    category: Optional[str] = None


class ReceiptScanRequest(BaseModel):
    """Request to scan a receipt."""
    file_path: Optional[str] = None
    content: Optional[str] = None  # Base64 encoded
    categorize_items: bool = True
    language: str = "en"


class ReceiptScanResponse(BaseModel):
    """Scanned receipt data."""
    merchant_name: Optional[str] = None
    merchant_address: Optional[str] = None
    merchant_phone: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    items: List[ReceiptItem] = Field(default_factory=list)
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    tip: Optional[float] = None
    total: float
    payment_method: Optional[str] = None
    card_last_four: Optional[str] = None
    currency: str = "USD"
    category: Optional[str] = None
    raw_text: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int


# Document Classification Schemas


class ClassifyRequest(BaseModel):
    """Request to classify a document."""
    file_path: Optional[str] = None
    content: Optional[str] = None  # Base64 encoded
    categories: Optional[List[str]] = None  # Custom categories


class ClassifyResponse(BaseModel):
    """Document classification result."""
    category: DocumentCategory
    confidence: float = Field(ge=0.0, le=1.0)
    all_scores: Dict[str, float] = Field(default_factory=dict)
    suggested_parsers: List[str] = Field(default_factory=list)
    processing_time_ms: int


# Entity Extraction Schemas


class EntityType(str, Enum):
    """Named entity types."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    ADDRESS = "address"
    PRODUCT = "product"
    EVENT = "event"


class ExtractedEntity(BaseModel):
    """An extracted named entity."""
    text: str
    entity_type: EntityType
    start: int
    end: int
    confidence: float = Field(ge=0.0, le=1.0)
    normalized_value: Optional[str] = None


class EntityExtractRequest(BaseModel):
    """Request to extract entities."""
    file_path: Optional[str] = None
    content: Optional[str] = None
    text: Optional[str] = None
    entity_types: Optional[List[EntityType]] = None


class EntityExtractResponse(BaseModel):
    """Entity extraction result."""
    entities: List[ExtractedEntity] = Field(default_factory=list)
    entity_counts: Dict[str, int] = Field(default_factory=dict)
    processing_time_ms: int


# Semantic Search Schemas


class SemanticSearchRequest(BaseModel):
    """Request for semantic search."""
    query: str
    document_ids: Optional[List[str]] = None
    top_k: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """A semantic search result."""
    document_id: str
    chunk_text: str
    score: float
    page_number: Optional[int] = None
    section: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SemanticSearchResponse(BaseModel):
    """Semantic search results."""
    query: str
    results: List[SearchResult] = Field(default_factory=list)
    total_results: int
    processing_time_ms: int


# Document Comparison Schemas


class DiffType(str, Enum):
    """Types of differences in document comparison."""
    ADDITION = "addition"
    DELETION = "deletion"
    MODIFICATION = "modification"


class DocumentDiff(BaseModel):
    """A difference between documents."""
    diff_type: DiffType
    section: Optional[str] = None
    original_text: Optional[str] = None
    modified_text: Optional[str] = None
    page_number: Optional[int] = None
    significance: str = "low"  # low, medium, high


class CompareRequest(BaseModel):
    """Request to compare documents."""
    document_a_path: Optional[str] = None
    document_a_content: Optional[str] = None
    document_b_path: Optional[str] = None
    document_b_content: Optional[str] = None
    highlight_changes: bool = True
    semantic_comparison: bool = False


class CompareResponse(BaseModel):
    """Document comparison result."""
    similarity_score: float = Field(ge=0.0, le=1.0)
    differences: List[DocumentDiff] = Field(default_factory=list)
    summary: str
    significant_changes: List[str] = Field(default_factory=list)
    processing_time_ms: int


# Compliance Check Schemas


class ComplianceRule(BaseModel):
    """A compliance rule."""
    rule_id: str
    name: str
    description: str
    regulation: str  # e.g., "GDPR", "HIPAA", "SOC2"


class ComplianceViolation(BaseModel):
    """A compliance violation."""
    rule: ComplianceRule
    location: str
    description: str
    severity: RiskLevel
    remediation: str


class ComplianceCheckRequest(BaseModel):
    """Request to check compliance."""
    file_path: Optional[str] = None
    content: Optional[str] = None
    regulations: List[str] = Field(default_factory=list)  # e.g., ["GDPR", "HIPAA"]


class ComplianceCheckResponse(BaseModel):
    """Compliance check result."""
    compliant: bool
    violations: List[ComplianceViolation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    checked_regulations: List[str] = Field(default_factory=list)
    processing_time_ms: int


# Multi-document Summary Schemas


class MultiDocSummarizeRequest(BaseModel):
    """Request to summarize multiple documents."""
    document_ids: List[str]
    max_length: int = Field(default=500, ge=100, le=2000)
    focus_topics: Optional[List[str]] = None
    include_sources: bool = True


class SummarySource(BaseModel):
    """Source reference in summary."""
    document_id: str
    document_title: Optional[str] = None
    page_number: Optional[int] = None
    excerpt: str


class MultiDocSummarizeResponse(BaseModel):
    """Multi-document summary result."""
    summary: str
    key_points: List[str] = Field(default_factory=list)
    common_themes: List[str] = Field(default_factory=list)
    sources: List[SummarySource] = Field(default_factory=list)
    document_count: int
    processing_time_ms: int
