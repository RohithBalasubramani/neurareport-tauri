"""DocAI API Route Tests.

Comprehensive tests for document intelligence endpoints: parsing, classification,
entity extraction, semantic search, comparison, compliance, and summarization.
"""
import base64

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.docai import router
from backend.app.services.docai.service import DocAIService
from backend.app.services.security import require_api_key
from backend.app.schemas.docai import (
    ContractAnalyzeResponse,
    ContractClause,
    ContractClauseType,
    ContractObligation,
    ContractParty,
    InvoiceAddress,
    InvoiceLineItem,
    InvoiceParseResponse,
    ConfidenceLevel,
    ReceiptItem,
    ReceiptScanResponse,
    ResumeParseResponse,
    RiskLevel,
    WorkExperience,
    Education,
)


def _b64(text: str) -> str:
    """Encode a plain-text string to base64 (as the API expects)."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Create a fresh FastAPI app with docai routes."""
    _app = FastAPI()
    _app.dependency_overrides[require_api_key] = lambda: None
    _app.include_router(router, prefix="/docai")
    return _app


@pytest.fixture
def app_no_auth():
    """App WITHOUT auth override - for testing auth enforcement."""
    _app = FastAPI()
    _app.include_router(router, prefix="/docai")
    return _app


@pytest.fixture
def service():
    """Create a fresh DocAIService and patch the module-level singleton.

    Also forces NLP/embeddings flags to False so tests exercise the
    regex/keyword fallback paths without requiring spaCy or sentence-transformers.
    """
    svc = DocAIService.__new__(DocAIService)
    svc._nlp_available = False
    svc._embeddings_available = False

    import backend.app.api.routes.docai as mod
    original = mod.docai_service
    mod.docai_service = svc
    yield svc
    mod.docai_service = original


@pytest.fixture
def client(app, service):
    """Create a test client with a fresh service."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helper: mock parser responses
# ---------------------------------------------------------------------------

def _mock_invoice_response(**overrides) -> InvoiceParseResponse:
    defaults = dict(
        invoice_number="INV-001",
        invoice_date=None,
        due_date=None,
        vendor=InvoiceAddress(name="Acme Corp"),
        bill_to=InvoiceAddress(name="Client Inc"),
        line_items=[
            InvoiceLineItem(description="Widget", quantity=2, unit_price=10.0, amount=20.0),
        ],
        subtotal=20.0,
        tax_total=1.60,
        total=21.60,
        currency="USD",
        payment_terms="Net 30",
        raw_text="sample",
        confidence_score=0.75,
        processing_time_ms=42,
    )
    defaults.update(overrides)
    return InvoiceParseResponse(**defaults)


def _mock_contract_response(**overrides) -> ContractAnalyzeResponse:
    defaults = dict(
        title="Service Agreement",
        contract_type="Service Agreement",
        effective_date=None,
        expiration_date=None,
        parties=[
            ContractParty(name="Acme Corp", role="Party A"),
            ContractParty(name="Client Inc", role="Party B"),
        ],
        clauses=[
            ContractClause(
                clause_type=ContractClauseType.TERMINATION,
                title="Termination",
                text="Either party may terminate...",
                risk_level=RiskLevel.LOW,
            ),
        ],
        obligations=[
            ContractObligation(party="Acme Corp", obligation="deliver services"),
        ],
        key_dates={},
        total_value=50000.0,
        currency="USD",
        risk_summary={"critical": 0, "high": 0, "medium": 0, "low": 1, "informational": 0},
        overall_risk_level=RiskLevel.LOW,
        recommendations=["Consider adding a confidentiality clause"],
        summary="This is a Service Agreement between Acme Corp and Client Inc.",
        confidence_score=0.80,
        processing_time_ms=55,
    )
    defaults.update(overrides)
    return ContractAnalyzeResponse(**defaults)


def _mock_resume_response(**overrides) -> ResumeParseResponse:
    defaults = dict(
        name="Jane Doe",
        email="jane@example.com",
        phone="555-123-4567",
        location="San Francisco, CA",
        linkedin_url="https://linkedin.com/in/janedoe",
        github_url="https://github.com/janedoe",
        portfolio_url=None,
        summary="Experienced software engineer.",
        education=[Education(institution="MIT", degree="B.S. Computer Science")],
        experience=[
            WorkExperience(company="Acme Corp", title="Software Engineer",
                           start_date="2020", end_date="present", is_current=True),
        ],
        skills=["Python", "JavaScript", "Docker"],
        certifications=["AWS Certified"],
        languages=["English", "Spanish"],
        total_years_experience=4.0,
        job_match_score=None,
        job_match_details=None,
        raw_text="resume text",
        confidence_score=0.90,
        processing_time_ms=30,
    )
    defaults.update(overrides)
    return ResumeParseResponse(**defaults)


def _mock_receipt_response(**overrides) -> ReceiptScanResponse:
    defaults = dict(
        merchant_name="Corner Store",
        merchant_address=None,
        merchant_phone="555-000-1234",
        date=None,
        time="14:30",
        items=[
            ReceiptItem(name="Milk", quantity=1, total_price=3.99, category="Food"),
            ReceiptItem(name="Bread", quantity=2, total_price=5.00, category="Food"),
        ],
        subtotal=8.99,
        tax=0.72,
        tip=None,
        total=9.71,
        payment_method="Cash",
        card_last_four=None,
        currency="USD",
        category="Groceries",
        raw_text="receipt text",
        confidence_score=0.75,
        processing_time_ms=25,
    )
    defaults.update(overrides)
    return ReceiptScanResponse(**defaults)


# =============================================================================
# INVOICE PARSING
# =============================================================================


class TestInvoiceParse:
    """Tests for POST /docai/parse/invoice."""

    def test_parse_invoice_success(self, client):
        """Valid invoice parse returns 200 with structured data."""
        mock_resp = _mock_invoice_response()
        with patch(
            "backend.app.services.docai.service.invoice_parser.parse",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/invoice", json={
                "content": _b64("Invoice #INV-001\nTotal: $21.60"),
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["invoice_number"] == "INV-001"
        assert data["total"] == 21.60
        assert data["currency"] == "USD"
        assert len(data["line_items"]) == 1
        assert data["confidence_score"] == 0.75
        assert "processing_time_ms" in data

    def test_parse_invoice_with_options(self, client):
        """Options like extract_line_items and extract_addresses are forwarded."""
        mock_resp = _mock_invoice_response(line_items=[], vendor=None, bill_to=None)
        with patch(
            "backend.app.services.docai.service.invoice_parser.parse",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/invoice", json={
                "content": _b64("Invoice #INV-001"),
                "extract_line_items": False,
                "extract_addresses": False,
                "language": "en",
            })
        assert resp.status_code == 200
        assert resp.json()["line_items"] == []

    def test_parse_invoice_empty_content(self, client):
        """Empty content still returns a valid (mostly null) response."""
        mock_resp = _mock_invoice_response(
            invoice_number=None, total=None, line_items=[],
            vendor=None, bill_to=None, subtotal=None, tax_total=None,
            payment_terms=None, raw_text=None, confidence_score=0.0,
        )
        with patch(
            "backend.app.services.docai.service.invoice_parser.parse",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/invoice", json={
                "content": _b64(""),
            })
        assert resp.status_code == 200
        assert resp.json()["confidence_score"] == 0.0

    def test_parse_invoice_no_input_fields(self, client):
        """Request with neither file_path nor content is still accepted (empty text)."""
        mock_resp = _mock_invoice_response(
            invoice_number=None, total=None, confidence_score=0.0,
            line_items=[], vendor=None, bill_to=None, subtotal=None,
            tax_total=None, payment_terms=None, raw_text=None,
        )
        with patch(
            "backend.app.services.docai.service.invoice_parser.parse",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/invoice", json={})
        assert resp.status_code == 200


# =============================================================================
# CONTRACT ANALYSIS
# =============================================================================


class TestContractAnalyze:
    """Tests for POST /docai/parse/contract."""

    def test_analyze_contract_success(self, client):
        mock_resp = _mock_contract_response()
        with patch(
            "backend.app.services.docai.service.contract_analyzer.analyze",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/contract", json={
                "content": _b64("Service Agreement between Acme and Client"),
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Service Agreement"
        assert len(data["parties"]) == 2
        assert data["parties"][0]["name"] == "Acme Corp"
        assert len(data["clauses"]) >= 1
        assert data["overall_risk_level"] == "low"
        assert data["confidence_score"] == 0.80

    def test_analyze_contract_with_risk_analysis(self, client):
        mock_resp = _mock_contract_response(
            overall_risk_level=RiskLevel.HIGH,
            risk_summary={"critical": 0, "high": 2, "medium": 1, "low": 0, "informational": 0},
        )
        with patch(
            "backend.app.services.docai.service.contract_analyzer.analyze",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/contract", json={
                "content": _b64("Agreement with unlimited liability"),
                "analyze_risks": True,
            })
        assert resp.status_code == 200
        assert resp.json()["overall_risk_level"] == "high"

    def test_analyze_contract_empty(self, client):
        mock_resp = _mock_contract_response(
            title=None, parties=[], clauses=[], obligations=[],
            summary="Contract analysis complete.",
            confidence_score=0.0,
        )
        with patch(
            "backend.app.services.docai.service.contract_analyzer.analyze",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/contract", json={})
        assert resp.status_code == 200
        assert resp.json()["confidence_score"] == 0.0


# =============================================================================
# RESUME PARSING
# =============================================================================


class TestResumeParse:
    """Tests for POST /docai/parse/resume."""

    def test_parse_resume_success(self, client):
        mock_resp = _mock_resume_response()
        with patch(
            "backend.app.services.docai.service.resume_parser.parse",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/resume", json={
                "content": _b64("Jane Doe\njane@example.com\nExperience\n..."),
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Jane Doe"
        assert data["email"] == "jane@example.com"
        assert "Python" in data["skills"]
        assert len(data["education"]) == 1
        assert data["confidence_score"] == 0.90

    def test_parse_resume_with_job_match(self, client):
        mock_resp = _mock_resume_response(
            job_match_score=0.72,
            job_match_details={
                "skill_score": 0.8,
                "keyword_score": 0.6,
                "experience_score": 0.7,
            },
        )
        with patch(
            "backend.app.services.docai.service.resume_parser.parse",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/resume", json={
                "content": _b64("Jane Doe resume"),
                "match_job_description": "Looking for Python developer with 3+ years",
            })
        assert resp.status_code == 200
        assert resp.json()["job_match_score"] == 0.72

    def test_parse_resume_no_skills(self, client):
        mock_resp = _mock_resume_response(skills=[])
        with patch(
            "backend.app.services.docai.service.resume_parser.parse",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/resume", json={
                "content": _b64("minimal"),
                "extract_skills": False,
            })
        assert resp.status_code == 200
        assert resp.json()["skills"] == []


# =============================================================================
# RECEIPT SCANNING
# =============================================================================


class TestReceiptScan:
    """Tests for POST /docai/parse/receipt."""

    def test_scan_receipt_success(self, client):
        mock_resp = _mock_receipt_response()
        with patch(
            "backend.app.services.docai.service.receipt_scanner.scan",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/receipt", json={
                "content": _b64("Corner Store\nMilk  $3.99\nTotal: $9.71"),
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["merchant_name"] == "Corner Store"
        assert data["total"] == 9.71
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "Milk"
        assert data["currency"] == "USD"

    def test_scan_receipt_with_payment_info(self, client):
        mock_resp = _mock_receipt_response(
            payment_method="Credit Card", card_last_four="4242",
        )
        with patch(
            "backend.app.services.docai.service.receipt_scanner.scan",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/receipt", json={
                "content": _b64("VISA ****4242\nTotal: $9.71"),
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["payment_method"] == "Credit Card"
        assert data["card_last_four"] == "4242"

    def test_scan_receipt_empty(self, client):
        mock_resp = _mock_receipt_response(
            merchant_name=None, items=[], total=0.0,
            subtotal=None, tax=None, tip=None, payment_method=None,
            confidence_score=0.0, category=None, raw_text=None,
            merchant_phone=None, time=None,
        )
        with patch(
            "backend.app.services.docai.service.receipt_scanner.scan",
            new_callable=AsyncMock,
            return_value=mock_resp,
        ):
            resp = client.post("/docai/parse/receipt", json={})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0.0


# =============================================================================
# DOCUMENT CLASSIFICATION
# =============================================================================


class TestClassifyDocument:
    """Tests for POST /docai/classify.

    These tests exercise the real keyword-based scoring logic in DocAIService
    (no mocking) by providing base64-encoded text containing category keywords.
    """

    def test_classify_invoice(self, client):
        text = (
            "Invoice Number: INV-2024-001\n"
            "Amount Due: $5,000\n"
            "Payment Terms: Net 30\n"
            "Due Date: 2024-12-31\n"
            "Line Item: Widget\n"
            "Subtotal: $4,500\n"
            "Tax: $500\n"
            "Bill to: Customer Corp"
        )
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "invoice"
        assert data["confidence"] > 0.0
        assert "invoice_parser" in data["suggested_parsers"]
        assert "processing_time_ms" in data

    def test_classify_contract(self, client):
        text = (
            "Service Agreement\n"
            "This Agreement is entered by Party A and Party B.\n"
            "WHEREAS, the parties hereby agree to the following terms.\n"
            "The term shall be 12 months.\n"
            "Termination: Either party may terminate with 30 days notice.\n"
            "Governing Law: State of California.\n"
            "Indemnification: Party A shall indemnify Party B.\n"
            "Liability: Neither party shall be liable for indirect damages."
        )
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "contract"
        assert data["confidence"] > 0.3
        assert "contract_analyzer" in data["suggested_parsers"]

    def test_classify_resume(self, client):
        text = (
            "John Smith\n"
            "Experience:\n"
            "Software Engineer at Acme Corp 2018-2023\n"
            "Education:\n"
            "Bachelor of Science, University of Testing\n"
            "Skills: Python, JavaScript, Docker\n"
            "Employment History\n"
            "Profile: Seasoned developer\n"
            "LinkedIn: linkedin.com/in/jsmith"
        )
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "resume"
        assert "resume_parser" in data["suggested_parsers"]

    def test_classify_receipt(self, client):
        text = (
            "Corner Store\n"
            "Receipt\n"
            "Milk        $3.99\n"
            "Total: $4.31\n"
            "Cash Tendered: $5.00\n"
            "Change: $0.69\n"
            "Thank You for your purchase!\n"
            "Transaction #12345\n"
            "Payment: Credit"
        )
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "receipt"
        assert "receipt_scanner" in data["suggested_parsers"]

    def test_classify_report(self, client):
        text = (
            "Annual Report 2024\n"
            "Executive Summary\n"
            "This analysis presents our findings.\n"
            "Methodology: We used mixed methods.\n"
            "Results: Key metrics improved 15%.\n"
            "Conclusion: Performance exceeded targets.\n"
            "Recommendations: Continue current strategy."
        )
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "report"
        # Reports have no dedicated parser
        assert data["suggested_parsers"] == []

    def test_classify_letter(self, client):
        text = (
            "Dear Mr. Johnson,\n\n"
            "I am writing to inform you about our partnership.\n\n"
            "Sincerely,\n"
            "Jane Smith\n"
            "Regards to the team"
        )
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "letter"
        assert data["suggested_parsers"] == []

    def test_classify_returns_all_scores(self, client):
        text = "Some generic document text with no strong keywords."
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        data = resp.json()
        assert "all_scores" in data
        # All defined categories should appear
        for cat in ["invoice", "contract", "resume", "receipt", "report",
                     "letter", "form", "presentation", "spreadsheet", "other"]:
            assert cat in data["all_scores"]

    def test_classify_empty_content(self, client):
        """Empty document should still return a valid classification (likely OTHER)."""
        resp = client.post("/docai/classify", json={"content": _b64("")})
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] in [
            "invoice", "contract", "resume", "receipt", "report",
            "letter", "form", "presentation", "spreadsheet", "other",
        ]


# =============================================================================
# ENTITY EXTRACTION
# =============================================================================


class TestEntityExtraction:
    """Tests for POST /docai/entities.

    Uses the real regex fallback path (no spaCy) built into DocAIService.
    """

    def test_extract_emails(self, client):
        resp = client.post("/docai/entities", json={
            "text": "Contact alice@example.com and bob@test.org for details.",
        })
        assert resp.status_code == 200
        data = resp.json()
        emails = [e for e in data["entities"] if e["entity_type"] == "email"]
        assert len(emails) == 2
        email_texts = {e["text"] for e in emails}
        assert "alice@example.com" in email_texts
        assert "bob@test.org" in email_texts

    def test_extract_urls(self, client):
        resp = client.post("/docai/entities", json={
            "text": "Visit https://example.com and http://test.org/page for info.",
        })
        assert resp.status_code == 200
        data = resp.json()
        urls = [e for e in data["entities"] if e["entity_type"] == "url"]
        assert len(urls) == 2

    def test_extract_money(self, client):
        resp = client.post("/docai/entities", json={
            "text": "The price is $1,500.00 and the discount is $200.00.",
        })
        assert resp.status_code == 200
        data = resp.json()
        money = [e for e in data["entities"] if e["entity_type"] == "money"]
        assert len(money) == 2
        amounts = {e["text"] for e in money}
        assert "$1,500.00" in amounts
        assert "$200.00" in amounts

    def test_extract_dates(self, client):
        resp = client.post("/docai/entities", json={
            "text": "Meeting on 01/15/2025 and deadline 12-31-2024.",
        })
        assert resp.status_code == 200
        data = resp.json()
        dates = [e for e in data["entities"] if e["entity_type"] == "date"]
        assert len(dates) == 2

    def test_extract_phone_numbers(self, client):
        resp = client.post("/docai/entities", json={
            "text": "Call us at (555) 123-4567 or +1-800-555-0199.",
        })
        assert resp.status_code == 200
        data = resp.json()
        phones = [e for e in data["entities"] if e["entity_type"] == "phone"]
        assert len(phones) >= 1

    def test_extract_percentages(self, client):
        resp = client.post("/docai/entities", json={
            "text": "Revenue grew 25% last year and margins improved 3.5%.",
        })
        assert resp.status_code == 200
        data = resp.json()
        pcts = [e for e in data["entities"] if e["entity_type"] == "percentage"]
        assert len(pcts) == 2

    def test_extract_with_type_filter(self, client):
        """Only extract entity types listed in entity_types."""
        resp = client.post("/docai/entities", json={
            "text": "alice@example.com owes $500.00 due 01/01/2025.",
            "entity_types": ["email"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert all(e["entity_type"] == "email" for e in data["entities"])
        assert len(data["entities"]) == 1

    def test_extract_multiple_types(self, client):
        """Mixed content returns entities of several types."""
        text = (
            "Contact: alice@example.com, +1-555-123-4567\n"
            "Visit https://example.com\n"
            "Total: $1,234.56 due 06/15/2025\n"
            "Growth: 42%"
        )
        resp = client.post("/docai/entities", json={"text": text})
        assert resp.status_code == 200
        data = resp.json()
        found_types = {e["entity_type"] for e in data["entities"]}
        assert "email" in found_types
        assert "url" in found_types
        assert "money" in found_types
        assert "date" in found_types
        assert "percentage" in found_types

    def test_entity_counts(self, client):
        text = "alice@a.com, bob@b.com, $100.00"
        resp = client.post("/docai/entities", json={"text": text})
        assert resp.status_code == 200
        data = resp.json()
        assert data["entity_counts"]["email"] == 2
        assert data["entity_counts"]["money"] == 1

    def test_entity_positions(self, client):
        """Entities should have correct start/end offsets."""
        text = "email: alice@example.com"
        resp = client.post("/docai/entities", json={"text": text})
        assert resp.status_code == 200
        entities = resp.json()["entities"]
        assert len(entities) >= 1
        email_entity = entities[0]
        assert email_entity["start"] >= 0
        assert email_entity["end"] > email_entity["start"]
        assert text[email_entity["start"]:email_entity["end"]] == "alice@example.com"

    def test_entity_confidence(self, client):
        """Regex entities should have confidence 0.9."""
        resp = client.post("/docai/entities", json={"text": "$99.99"})
        assert resp.status_code == 200
        for entity in resp.json()["entities"]:
            assert entity["confidence"] == 0.9

    def test_extract_from_base64_content(self, client):
        """When using content (base64), the text is decoded and entities extracted."""
        text = "Reach out to support@corp.com for help."
        resp = client.post("/docai/entities", json={
            "content": _b64(text),
        })
        assert resp.status_code == 200
        emails = [e for e in resp.json()["entities"] if e["entity_type"] == "email"]
        assert len(emails) == 1

    def test_extract_empty_text(self, client):
        resp = client.post("/docai/entities", json={"text": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["entities"] == []
        assert data["entity_counts"] == {}

    def test_extract_no_entities(self, client):
        resp = client.post("/docai/entities", json={
            "text": "Just a plain sentence with no recognizable entities.",
        })
        assert resp.status_code == 200
        assert resp.json()["entities"] == []


# =============================================================================
# SEMANTIC SEARCH
# =============================================================================


class TestSemanticSearch:
    """Tests for POST /docai/search.

    Without embeddings library, results should be empty (keyword fallback returns []).
    """

    def test_search_returns_empty_without_embeddings(self, client):
        resp = client.post("/docai/search", json={
            "query": "revenue report Q4",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "revenue report Q4"
        assert data["results"] == []
        assert data["total_results"] == 0
        assert "processing_time_ms" in data

    def test_search_with_document_ids(self, client):
        resp = client.post("/docai/search", json={
            "query": "machine learning",
            "document_ids": ["doc-1", "doc-2"],
            "top_k": 5,
        })
        assert resp.status_code == 200
        assert resp.json()["total_results"] == 0

    def test_search_with_threshold(self, client):
        resp = client.post("/docai/search", json={
            "query": "quarterly earnings",
            "threshold": 0.8,
        })
        assert resp.status_code == 200
        assert resp.json()["results"] == []

    def test_search_default_parameters(self, client):
        """top_k defaults to 10, threshold to 0.5."""
        resp = client.post("/docai/search", json={"query": "test"})
        assert resp.status_code == 200

    def test_search_validation_top_k(self, client):
        """top_k must be between 1 and 100."""
        resp = client.post("/docai/search", json={
            "query": "test",
            "top_k": 0,
        })
        assert resp.status_code == 422  # validation error

    def test_search_validation_threshold(self, client):
        """threshold must be between 0.0 and 1.0."""
        resp = client.post("/docai/search", json={
            "query": "test",
            "threshold": 1.5,
        })
        assert resp.status_code == 422


# =============================================================================
# DOCUMENT COMPARISON
# =============================================================================


class TestDocumentComparison:
    """Tests for POST /docai/compare.

    Uses the real Jaccard + difflib logic in DocAIService.
    """

    def test_compare_identical_documents(self, client):
        text = "This is a test document with some content."
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64(text),
            "document_b_content": _b64(text),
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["similarity_score"] == 1.0
        assert data["differences"] == []
        assert "nearly identical" in data["summary"]

    def test_compare_different_documents(self, client):
        text_a = "The quick brown fox jumps over the lazy dog"
        text_b = "A completely different document about quantum physics"
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64(text_a),
            "document_b_content": _b64(text_b),
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["similarity_score"] < 0.5
        assert len(data["differences"]) > 0
        assert "processing_time_ms" in data

    def test_compare_similar_documents(self, client):
        text_a = "The project report shows significant revenue growth in Q4"
        text_b = "The project report shows moderate revenue growth in Q3"
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64(text_a),
            "document_b_content": _b64(text_b),
        })
        assert resp.status_code == 200
        data = resp.json()
        # They share many words, so similarity should be moderate-to-high
        assert data["similarity_score"] > 0.3
        assert data["similarity_score"] < 1.0

    def test_compare_summary_levels(self, client):
        """Verify summary wording scales with similarity."""
        # Nearly identical
        text = "word " * 50
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64(text),
            "document_b_content": _b64(text),
        })
        assert "nearly identical" in resp.json()["summary"]

        # Significantly different
        resp2 = client.post("/docai/compare", json={
            "document_a_content": _b64("alpha bravo charlie"),
            "document_b_content": _b64("xray yankee zulu"),
        })
        assert "significantly different" in resp2.json()["summary"]

    def test_compare_diff_types(self, client):
        """Differences should have diff_type of addition or deletion."""
        text_a = "Line one\nLine two\nLine three"
        text_b = "Line one\nModified line\nLine three"
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64(text_a),
            "document_b_content": _b64(text_b),
        })
        assert resp.status_code == 200
        data = resp.json()
        diff_types = {d["diff_type"] for d in data["differences"]}
        # Should have deletions (from A) and additions (from B)
        assert "deletion" in diff_types or "addition" in diff_types

    def test_compare_empty_documents(self, client):
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64(""),
            "document_b_content": _b64(""),
        })
        assert resp.status_code == 200
        data = resp.json()
        # Empty texts: jaccard returns 0.0
        assert data["similarity_score"] == 0.0

    def test_compare_one_empty(self, client):
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64("Some real content here"),
            "document_b_content": _b64(""),
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["similarity_score"] == 0.0
        assert len(data["differences"]) > 0


# =============================================================================
# COMPLIANCE CHECKING
# =============================================================================


class TestComplianceCheck:
    """Tests for POST /docai/compliance.

    Uses the real keyword-based rule checking in DocAIService.
    """

    def test_gdpr_compliant(self, client):
        """Document containing all GDPR keywords passes compliance."""
        text = (
            "Data Processing Agreement\n"
            "Lawful basis for processing is consent.\n"
            "Right to access is guaranteed for every data subject.\n"
            "Right to erasure is available upon request.\n"
            "Data retention period is 5 years, after which records are deleted.\n"
        )
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["GDPR"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is True
        assert data["violations"] == []
        assert data["checked_regulations"] == ["GDPR"]

    def test_gdpr_violations(self, client):
        """Document missing GDPR keywords triggers violations."""
        text = "This is a generic document with no compliance language."
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["GDPR"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is False
        assert len(data["violations"]) == 3  # gdpr_1, gdpr_2, gdpr_3
        for violation in data["violations"]:
            assert violation["rule"]["regulation"] == "GDPR"
            assert violation["severity"] == "medium"
            assert violation["location"] == "Document-wide"
            assert violation["remediation"] != ""

    def test_hipaa_compliant(self, client):
        text = (
            "This agreement covers protected health information (PHI).\n"
            "The business associate shall comply with all HIPAA requirements.\n"
        )
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["HIPAA"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is True
        assert data["violations"] == []

    def test_hipaa_violations(self, client):
        text = "This is a basic document with no relevant compliance language."
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["HIPAA"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is False
        assert len(data["violations"]) == 2  # hipaa_1, hipaa_2

    def test_soc2_compliant(self, client):
        text = (
            "This document outlines our security controls.\n"
            "Regular audits are conducted quarterly.\n"
        )
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["SOC2"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is True

    def test_soc2_violations(self, client):
        text = "Nothing related to compliance or regulations here."
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["SOC2"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is False
        assert len(data["violations"]) == 1

    def test_multiple_regulations(self, client):
        """Check against GDPR, HIPAA, and SOC2 simultaneously."""
        text = "A completely empty compliance document."
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["GDPR", "HIPAA", "SOC2"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is False
        # 3 GDPR + 2 HIPAA + 1 SOC2 = 6
        assert len(data["violations"]) == 6
        assert set(data["checked_regulations"]) == {"GDPR", "HIPAA", "SOC2"}

    def test_multiple_regulations_all_compliant(self, client):
        text = (
            "Lawful basis: consent. Right to access for each data subject. "
            "Data retention policy: delete after 3 years.\n"
            "Protected health information (PHI) is secured. "
            "Business associate agreement included.\n"
            "Security controls are documented. Audit trail maintained.\n"
        )
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["GDPR", "HIPAA", "SOC2"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is True
        assert data["violations"] == []

    def test_compliance_recommendations(self, client):
        text = "Generic document."
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["GDPR"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["recommendations"]) >= 1
        assert any("Review and address" in r for r in data["recommendations"])

    def test_compliance_empty_regulations(self, client):
        """No regulations to check means compliant by default."""
        resp = client.post("/docai/compliance", json={
            "content": _b64("Some document."),
            "regulations": [],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is True
        assert data["violations"] == []

    def test_compliance_unknown_regulation(self, client):
        """Unknown regulation name is silently ignored (no rules matched)."""
        resp = client.post("/docai/compliance", json={
            "content": _b64("Some document."),
            "regulations": ["UNKNOWN_REG"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is True
        assert data["violations"] == []

    def test_compliance_partial_gdpr(self, client):
        """Document satisfying some but not all GDPR rules."""
        text = "This processes data with lawful basis being consent."
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["GDPR"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is False
        # gdpr_1 passes (has "consent" and "lawful basis"), but gdpr_2 and gdpr_3 fail
        assert len(data["violations"]) == 2
        violation_rule_ids = {v["rule"]["rule_id"] for v in data["violations"]}
        assert "gdpr_2" in violation_rule_ids
        assert "gdpr_3" in violation_rule_ids


# =============================================================================
# MULTI-DOCUMENT SUMMARIZATION
# =============================================================================


class TestMultiDocSummarize:
    """Tests for POST /docai/summarize/multi.

    Currently returns a placeholder response.
    """

    def test_summarize_placeholder(self, client):
        resp = client.post("/docai/summarize/multi", json={
            "document_ids": ["doc-1", "doc-2", "doc-3"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert data["document_count"] == 3
        assert data["key_points"] == []
        assert data["common_themes"] == []
        assert data["sources"] == []
        assert "processing_time_ms" in data

    def test_summarize_with_options(self, client):
        resp = client.post("/docai/summarize/multi", json={
            "document_ids": ["doc-a", "doc-b"],
            "max_length": 200,
            "focus_topics": ["revenue", "costs"],
            "include_sources": True,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["document_count"] == 2

    def test_summarize_single_document(self, client):
        resp = client.post("/docai/summarize/multi", json={
            "document_ids": ["only-one"],
        })
        assert resp.status_code == 200
        assert resp.json()["document_count"] == 1

    def test_summarize_validation_max_length(self, client):
        """max_length must be between 100 and 2000."""
        resp = client.post("/docai/summarize/multi", json={
            "document_ids": ["doc-1"],
            "max_length": 50,  # below min
        })
        assert resp.status_code == 422

    def test_summarize_empty_document_ids(self, client):
        """Empty document_ids list should fail validation or return 0 count."""
        resp = client.post("/docai/summarize/multi", json={
            "document_ids": [],
        })
        # Pydantic accepts empty list; service returns document_count=0
        assert resp.status_code == 200
        assert resp.json()["document_count"] == 0


# =============================================================================
# EDGE CASES & CROSS-CUTTING
# =============================================================================


class TestEdgeCases:
    """Cross-cutting edge case tests."""

    def test_classify_missing_both_inputs(self, client):
        """Neither file_path nor content - should return classification of empty text."""
        resp = client.post("/docai/classify", json={})
        assert resp.status_code == 200
        data = resp.json()
        # Empty text has no keyword matches, so 'other' (0.1) wins
        assert data["category"] == "other"

    def test_entity_extract_text_takes_priority(self, client):
        """When both text and content are provided, text should be used first."""
        resp = client.post("/docai/entities", json={
            "text": "alice@direct.com",
            "content": _b64("bob@content.com"),
        })
        assert resp.status_code == 200
        emails = [e["text"] for e in resp.json()["entities"] if e["entity_type"] == "email"]
        # text field takes priority per service logic
        assert "alice@direct.com" in emails

    def test_compare_with_multiline(self, client):
        text_a = "First line\nSecond line\nThird line"
        text_b = "First line\nChanged second\nThird line"
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64(text_a),
            "document_b_content": _b64(text_b),
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["differences"]) >= 1

    def test_compliance_case_insensitive(self, client):
        """Keyword matching should be case-insensitive."""
        text = "LAWFUL BASIS for consent. RIGHT TO ACCESS for every DATA SUBJECT. RETENTION policy."
        resp = client.post("/docai/compliance", json={
            "content": _b64(text),
            "regulations": ["GDPR"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["compliant"] is True

    def test_classify_large_content(self, client):
        """Classification should handle large documents."""
        # Generate a long invoice-like document
        text = "Invoice Number: INV-001\n" + ("Line item description $100.00\n" * 500)
        resp = client.post("/docai/classify", json={"content": _b64(text)})
        assert resp.status_code == 200
        assert resp.json()["category"] == "invoice"

    def test_entity_extract_processing_time(self, client):
        """processing_time_ms should be a non-negative integer."""
        resp = client.post("/docai/entities", json={"text": "test@example.com"})
        assert resp.status_code == 200
        assert resp.json()["processing_time_ms"] >= 0

    def test_compare_processing_time(self, client):
        resp = client.post("/docai/compare", json={
            "document_a_content": _b64("a"),
            "document_b_content": _b64("b"),
        })
        assert resp.status_code == 200
        assert resp.json()["processing_time_ms"] >= 0

    def test_compliance_processing_time(self, client):
        resp = client.post("/docai/compliance", json={
            "content": _b64("test"),
            "regulations": ["GDPR"],
        })
        assert resp.status_code == 200
        assert resp.json()["processing_time_ms"] >= 0

    def test_search_processing_time(self, client):
        resp = client.post("/docai/search", json={"query": "test"})
        assert resp.status_code == 200
        assert resp.json()["processing_time_ms"] >= 0

    def test_summarize_processing_time(self, client):
        resp = client.post("/docai/summarize/multi", json={
            "document_ids": ["doc-1"],
        })
        assert resp.status_code == 200
        assert resp.json()["processing_time_ms"] >= 0


# =============================================================================
# VALIDATION TESTS
# =============================================================================


class TestRequestValidation:
    """Tests for request body validation via Pydantic schemas."""

    def test_search_requires_query(self, client):
        resp = client.post("/docai/search", json={})
        assert resp.status_code == 422

    def test_summarize_requires_document_ids(self, client):
        resp = client.post("/docai/summarize/multi", json={})
        assert resp.status_code == 422

    def test_search_top_k_max(self, client):
        resp = client.post("/docai/search", json={
            "query": "test",
            "top_k": 101,
        })
        assert resp.status_code == 422

    def test_summarize_max_length_too_high(self, client):
        resp = client.post("/docai/summarize/multi", json={
            "document_ids": ["doc-1"],
            "max_length": 3000,
        })
        assert resp.status_code == 422


# =============================================================================
# SECURITY TESTS
# =============================================================================


class TestDocAIAuth:
    """DocAI routes have API key authentication wired up."""

    def test_router_has_auth_dependency(self):
        """Verify the router declares require_api_key as a dependency."""
        from backend.app.api.routes.docai import router as docai_router
        from backend.app.services.security import require_api_key
        dep_callables = [d.dependency for d in docai_router.dependencies]
        assert require_api_key in dep_callables


class TestDocAIErrorHandling:
    """Error handling returns generic messages, not raw exceptions."""

    def test_classify_service_error_returns_500(self, client):
        with patch(
            "backend.app.services.docai.service.DocAIService.classify_document",
            new_callable=AsyncMock,
            side_effect=RuntimeError("internal crash"),
        ):
            resp = client.post("/docai/classify", json={"content": "dGVzdA=="})
            assert resp.status_code == 500
            detail = resp.json()["detail"]
            assert "internal crash" not in detail
            assert "internal error" in detail.lower()

    def test_entities_service_error_returns_500(self, client):
        with patch(
            "backend.app.services.docai.service.DocAIService.extract_entities",
            new_callable=AsyncMock,
            side_effect=RuntimeError("oops"),
        ):
            resp = client.post("/docai/entities", json={"text": "test"})
            assert resp.status_code == 500
            assert "oops" not in resp.json()["detail"]

    def test_compare_service_error_returns_500(self, client):
        with patch(
            "backend.app.services.docai.service.DocAIService.compare_documents",
            new_callable=AsyncMock,
            side_effect=RuntimeError("compare failed"),
        ):
            resp = client.post("/docai/compare", json={
                "document_a_content": "dGVzdA==",
                "document_b_content": "dGVzdA==",
            })
            assert resp.status_code == 500
            assert "compare failed" not in resp.json()["detail"]
