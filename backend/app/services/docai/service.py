"""Document AI Service.

Main service for document intelligence - parsing, classification, and analysis.
"""
from __future__ import annotations

import base64
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.schemas.docai import (
    ClassifyRequest,
    ClassifyResponse,
    CompareRequest,
    CompareResponse,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ComplianceRule,
    ComplianceViolation,
    ContractAnalyzeRequest,
    ContractAnalyzeResponse,
    DiffType,
    DocumentCategory,
    DocumentDiff,
    EntityExtractRequest,
    EntityExtractResponse,
    EntityType,
    ExtractedEntity,
    InvoiceParseRequest,
    InvoiceParseResponse,
    MultiDocSummarizeRequest,
    MultiDocSummarizeResponse,
    ReceiptScanRequest,
    ReceiptScanResponse,
    ResumeParseRequest,
    ResumeParseResponse,
    RiskLevel,
    SearchResult,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SummarySource,
)
from backend.app.services.docai.parsers.contract_analyzer import contract_analyzer
from backend.app.services.docai.parsers.invoice_parser import invoice_parser
from backend.app.services.docai.parsers.receipt_scanner import receipt_scanner
from backend.app.services.docai.parsers.resume_parser import resume_parser


class DocAIService:
    """Main Document AI service orchestrating all document intelligence features."""

    def __init__(self) -> None:
        """Initialize the DocAI service."""
        self._nlp_available = self._check_nlp()
        self._embeddings_available = self._check_embeddings()

    def _check_nlp(self) -> bool:
        """Check if NLP libraries are available."""
        try:
            import spacy  # noqa: F401
            return True
        except Exception:
            return False

    def _check_embeddings(self) -> bool:
        """Check if embedding libraries are available."""
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
            return True
        except ImportError:
            return False

    # Document Parsing Methods

    async def parse_invoice(self, request: InvoiceParseRequest) -> InvoiceParseResponse:
        """Parse an invoice document."""
        return await invoice_parser.parse(request)

    async def analyze_contract(
        self, request: ContractAnalyzeRequest
    ) -> ContractAnalyzeResponse:
        """Analyze a contract document."""
        return await contract_analyzer.analyze(request)

    async def parse_resume(self, request: ResumeParseRequest) -> ResumeParseResponse:
        """Parse a resume document."""
        return await resume_parser.parse(request)

    async def scan_receipt(self, request: ReceiptScanRequest) -> ReceiptScanResponse:
        """Scan a receipt document."""
        return await receipt_scanner.scan(request)

    # Document Classification

    async def classify_document(self, request: ClassifyRequest) -> ClassifyResponse:
        """Classify a document by type."""
        start_time = time.time()
        text = await self._extract_text(request.file_path, request.content)

        # Calculate scores for each category
        scores = self._calculate_category_scores(text.lower())

        # Find best match
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        # Suggest parsers based on category
        parser_map = {
            DocumentCategory.INVOICE: ["invoice_parser"],
            DocumentCategory.CONTRACT: ["contract_analyzer"],
            DocumentCategory.RESUME: ["resume_parser"],
            DocumentCategory.RECEIPT: ["receipt_scanner"],
        }
        suggested_parsers = parser_map.get(best_category, [])

        processing_time_ms = int((time.time() - start_time) * 1000)

        return ClassifyResponse(
            category=best_category,
            confidence=best_score,
            all_scores={k.value: v for k, v in scores.items()},
            suggested_parsers=suggested_parsers,
            processing_time_ms=processing_time_ms,
        )

    def _calculate_category_scores(self, text: str) -> Dict[DocumentCategory, float]:
        """Calculate classification scores for each category."""
        category_keywords = {
            DocumentCategory.INVOICE: [
                "invoice", "bill", "amount due", "payment terms", "due date",
                "invoice number", "line item", "subtotal", "tax"
            ],
            DocumentCategory.CONTRACT: [
                "agreement", "party", "whereas", "hereby", "shall", "term",
                "termination", "governing law", "indemnif", "liability"
            ],
            DocumentCategory.RESUME: [
                "experience", "education", "skills", "employment", "bachelor",
                "master", "university", "objective", "profile", "linkedin"
            ],
            DocumentCategory.RECEIPT: [
                "receipt", "total", "cash", "credit", "thank you", "store",
                "change", "payment", "transaction"
            ],
            DocumentCategory.REPORT: [
                "report", "analysis", "findings", "conclusion", "executive summary",
                "methodology", "results", "recommendations"
            ],
            DocumentCategory.LETTER: [
                "dear", "sincerely", "regards", "yours truly", "to whom it may concern"
            ],
            DocumentCategory.FORM: [
                "please fill", "required field", "signature", "date of birth",
                "applicant", "checkbox", "form"
            ],
            DocumentCategory.PRESENTATION: [
                "slide", "presentation", "agenda", "overview", "key points"
            ],
            DocumentCategory.SPREADSHEET: [
                "total", "sum", "average", "column", "row", "cell"
            ],
        }

        scores: Dict[DocumentCategory, float] = {}

        for category, keywords in category_keywords.items():
            matches = sum(1 for kw in keywords if kw in text)
            scores[category] = min(matches / len(keywords), 1.0)

        # Add OTHER with default score
        scores[DocumentCategory.OTHER] = 0.1

        return scores

    # Entity Extraction

    async def extract_entities(
        self, request: EntityExtractRequest
    ) -> EntityExtractResponse:
        """Extract named entities from text."""
        start_time = time.time()

        # Get text from various sources
        if request.text:
            text = request.text
        else:
            text = await self._extract_text(request.file_path, request.content)

        entities: List[ExtractedEntity] = []
        entity_counts: Dict[str, int] = {}

        # Use spaCy if available
        if self._nlp_available:
            entities = await self._extract_with_spacy(text, request.entity_types)
        else:
            # Fallback to regex-based extraction
            entities = self._extract_with_regex(text, request.entity_types)

        # Count entities by type
        for entity in entities:
            type_name = entity.entity_type.value
            entity_counts[type_name] = entity_counts.get(type_name, 0) + 1

        processing_time_ms = int((time.time() - start_time) * 1000)

        return EntityExtractResponse(
            entities=entities,
            entity_counts=entity_counts,
            processing_time_ms=processing_time_ms,
        )

    async def _extract_with_spacy(
        self, text: str, entity_types: Optional[List[EntityType]]
    ) -> List[ExtractedEntity]:
        """Extract entities using spaCy."""
        import spacy

        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return self._extract_with_regex(text, entity_types)

        doc = nlp(text)
        entities: List[ExtractedEntity] = []

        # Map spaCy labels to our entity types
        label_map = {
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "GPE": EntityType.LOCATION,
            "LOC": EntityType.LOCATION,
            "DATE": EntityType.DATE,
            "MONEY": EntityType.MONEY,
            "PERCENT": EntityType.PERCENTAGE,
            "PRODUCT": EntityType.PRODUCT,
            "EVENT": EntityType.EVENT,
        }

        for ent in doc.ents:
            entity_type = label_map.get(ent.label_)
            if not entity_type:
                continue

            if entity_types and entity_type not in entity_types:
                continue

            entities.append(ExtractedEntity(
                text=ent.text,
                entity_type=entity_type,
                start=ent.start_char,
                end=ent.end_char,
                confidence=0.85,  # spaCy doesn't provide confidence scores
            ))

        return entities

    def _extract_with_regex(
        self, text: str, entity_types: Optional[List[EntityType]]
    ) -> List[ExtractedEntity]:
        """Extract entities using regex patterns."""
        import re
        entities: List[ExtractedEntity] = []

        patterns = {
            EntityType.EMAIL: r"[\w.+-]+@[\w-]+\.[\w.-]+",
            EntityType.PHONE: r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            EntityType.URL: r"https?://[\w.-]+(?:/[\w./-]*)?",
            EntityType.MONEY: r"\$[\d,]+(?:\.\d{2})?",
            EntityType.PERCENTAGE: r"\d+(?:\.\d+)?%",
            EntityType.DATE: r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
        }

        for entity_type, pattern in patterns.items():
            if entity_types and entity_type not in entity_types:
                continue

            for match in re.finditer(pattern, text):
                entities.append(ExtractedEntity(
                    text=match.group(0),
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9,
                ))

        return entities

    # Semantic Search

    async def semantic_search(
        self, request: SemanticSearchRequest
    ) -> SemanticSearchResponse:
        """Perform semantic search across documents."""
        start_time = time.time()
        results: List[SearchResult] = []

        if not self._embeddings_available:
            # Fallback to keyword search
            results = await self._keyword_search(
                request.query, request.document_ids, request.top_k
            )
        else:
            results = await self._embedding_search(
                request.query, request.document_ids, request.top_k, request.threshold
            )

        processing_time_ms = int((time.time() - start_time) * 1000)

        return SemanticSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            processing_time_ms=processing_time_ms,
        )

    async def _keyword_search(
        self, query: str, document_ids: Optional[List[str]], top_k: int
    ) -> List[SearchResult]:
        """Simple keyword-based search fallback."""
        # This would integrate with the document library
        # For now, return empty results
        return []

    async def _embedding_search(
        self,
        query: str,
        document_ids: Optional[List[str]],
        top_k: int,
        threshold: float,
    ) -> List[SearchResult]:
        """Search using embeddings."""
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(query)

        # This would integrate with the document library and vector store
        # For now, return empty results
        return []

    # Document Comparison

    async def compare_documents(self, request: CompareRequest) -> CompareResponse:
        """Compare two documents for differences."""
        start_time = time.time()

        # Extract text from both documents
        text_a = await self._extract_text(
            request.document_a_path, request.document_a_content
        )
        text_b = await self._extract_text(
            request.document_b_path, request.document_b_content
        )

        # Calculate similarity
        similarity = self._calculate_similarity(text_a, text_b)

        # Find differences
        differences = self._find_differences(text_a, text_b)

        # Generate summary
        summary = self._generate_comparison_summary(
            similarity, len(differences), text_a, text_b
        )

        # Identify significant changes
        significant = [d.modified_text or d.original_text for d in differences
                       if d.significance == "high"][:5]

        processing_time_ms = int((time.time() - start_time) * 1000)

        return CompareResponse(
            similarity_score=similarity,
            differences=differences,
            summary=summary,
            significant_changes=significant,
            processing_time_ms=processing_time_ms,
        )

    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate text similarity using Jaccard index."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0

    def _find_differences(
        self, text_a: str, text_b: str
    ) -> List[DocumentDiff]:
        """Find differences between two texts."""
        import difflib

        differ = difflib.Differ()
        lines_a = text_a.split("\n")
        lines_b = text_b.split("\n")

        diff = list(differ.compare(lines_a, lines_b))
        differences: List[DocumentDiff] = []

        for i, line in enumerate(diff):
            if line.startswith("- "):
                differences.append(DocumentDiff(
                    diff_type=DiffType.DELETION,
                    original_text=line[2:],
                    significance="medium" if len(line) > 50 else "low",
                ))
            elif line.startswith("+ "):
                differences.append(DocumentDiff(
                    diff_type=DiffType.ADDITION,
                    modified_text=line[2:],
                    significance="medium" if len(line) > 50 else "low",
                ))

        return differences[:50]  # Limit to 50 differences

    def _generate_comparison_summary(
        self,
        similarity: float,
        diff_count: int,
        text_a: str,
        text_b: str,
    ) -> str:
        """Generate a summary of document comparison."""
        if similarity > 0.9:
            level = "nearly identical"
        elif similarity > 0.7:
            level = "substantially similar"
        elif similarity > 0.5:
            level = "moderately similar"
        else:
            level = "significantly different"

        return (
            f"Documents are {level} with {similarity:.0%} similarity. "
            f"Found {diff_count} differences between the two versions."
        )

    # Compliance Checking

    async def check_compliance(
        self, request: ComplianceCheckRequest
    ) -> ComplianceCheckResponse:
        """Check document for compliance with regulations."""
        start_time = time.time()
        text = await self._extract_text(request.file_path, request.content)
        text_lower = text.lower()

        violations: List[ComplianceViolation] = []
        warnings: List[str] = []
        recommendations: List[str] = []

        # Define compliance rules for each regulation
        rules = self._get_compliance_rules(request.regulations)

        for rule in rules:
            violation = self._check_rule(text_lower, rule)
            if violation:
                violations.append(violation)

        # Generate recommendations
        if violations:
            recommendations.append("Review and address all violations before proceeding")
            if any(v.severity == RiskLevel.CRITICAL for v in violations):
                recommendations.append("Critical violations require immediate attention")

        processing_time_ms = int((time.time() - start_time) * 1000)

        return ComplianceCheckResponse(
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            checked_regulations=request.regulations,
            processing_time_ms=processing_time_ms,
        )

    def _get_compliance_rules(
        self, regulations: List[str]
    ) -> List[ComplianceRule]:
        """Get compliance rules for specified regulations."""
        all_rules = {
            "GDPR": [
                ComplianceRule(
                    rule_id="gdpr_1",
                    name="Personal Data Processing",
                    description="Must specify lawful basis for processing personal data",
                    regulation="GDPR",
                ),
                ComplianceRule(
                    rule_id="gdpr_2",
                    name="Data Subject Rights",
                    description="Must include provisions for data subject rights",
                    regulation="GDPR",
                ),
                ComplianceRule(
                    rule_id="gdpr_3",
                    name="Data Retention",
                    description="Must specify data retention periods",
                    regulation="GDPR",
                ),
            ],
            "HIPAA": [
                ComplianceRule(
                    rule_id="hipaa_1",
                    name="PHI Protection",
                    description="Must include PHI protection requirements",
                    regulation="HIPAA",
                ),
                ComplianceRule(
                    rule_id="hipaa_2",
                    name="Business Associate",
                    description="Must include Business Associate Agreement for third parties",
                    regulation="HIPAA",
                ),
            ],
            "SOC2": [
                ComplianceRule(
                    rule_id="soc2_1",
                    name="Security Controls",
                    description="Must reference security controls",
                    regulation="SOC2",
                ),
            ],
        }

        rules: List[ComplianceRule] = []
        for reg in regulations:
            rules.extend(all_rules.get(reg.upper(), []))

        return rules

    def _check_rule(
        self, text: str, rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check if a rule is violated in the text."""
        # Simple keyword-based checking
        required_keywords = {
            "gdpr_1": ["lawful basis", "legitimate interest", "consent"],
            "gdpr_2": ["right to access", "right to erasure", "data subject"],
            "gdpr_3": ["retention", "data retention", "delete"],
            "hipaa_1": ["protected health information", "phi", "health information"],
            "hipaa_2": ["business associate", "baa"],
            "soc2_1": ["security", "controls", "audit"],
        }

        keywords = required_keywords.get(rule.rule_id, [])
        has_keywords = any(kw in text for kw in keywords)

        if not has_keywords:
            return ComplianceViolation(
                rule=rule,
                location="Document-wide",
                description=f"Missing required language for {rule.name}",
                severity=RiskLevel.MEDIUM,
                remediation=f"Add language addressing {rule.description}",
            )

        return None

    # Multi-document Summarization

    async def summarize_multiple(
        self, request: MultiDocSummarizeRequest
    ) -> MultiDocSummarizeResponse:
        """Summarize multiple documents."""
        start_time = time.time()

        # This would integrate with the document library
        # For now, return a placeholder response
        summary = "Multi-document summary feature requires document library integration."
        key_points: List[str] = []
        common_themes: List[str] = []
        sources: List[SummarySource] = []

        processing_time_ms = int((time.time() - start_time) * 1000)

        return MultiDocSummarizeResponse(
            summary=summary,
            key_points=key_points,
            common_themes=common_themes,
            sources=sources,
            document_count=len(request.document_ids),
            processing_time_ms=processing_time_ms,
        )

    # Helper Methods

    async def _extract_text(
        self, file_path: Optional[str], content: Optional[str]
    ) -> str:
        """Extract text from file path or content."""
        if content:
            try:
                decoded = base64.b64decode(content)
                # Try to decode as text
                return decoded.decode("utf-8")
            except Exception:
                # Try PDF extraction
                try:
                    import fitz
                    doc = fitz.open(stream=decoded, filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    return text
                except Exception:
                    return ""

        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            suffix = path.suffix.lower()
            if suffix == ".pdf":
                try:
                    import fitz
                    doc = fitz.open(str(path))
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    return text
                except ImportError:
                    return ""
            elif suffix == ".docx":
                try:
                    from docx import Document
                    doc = Document(str(path))
                    return "\n".join([p.text for p in doc.paragraphs])
                except ImportError:
                    return ""
            else:
                return path.read_text(encoding="utf-8")

        return ""


# Singleton instance
docai_service = DocAIService()
