"""Contract Analyzer Service.

Analyzes contract documents for clauses, risks, and obligations.
"""
from __future__ import annotations

import base64
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.app.schemas.docai import (
    ConfidenceLevel,
    ContractAnalyzeRequest,
    ContractAnalyzeResponse,
    ContractClause,
    ContractClauseType,
    ContractObligation,
    ContractParty,
    RiskLevel,
)


class ContractAnalyzer:
    """Analyzer for extracting data from contract documents."""

    # Clause detection patterns
    CLAUSE_PATTERNS: Dict[ContractClauseType, List[str]] = {
        ContractClauseType.TERMINATION: [
            r"(?:termination|terminate|cancel)",
            r"(?:end\s+of\s+agreement|expir)",
        ],
        ContractClauseType.INDEMNIFICATION: [
            r"(?:indemnif|hold\s+harmless|defend\s+and\s+indemnify)",
        ],
        ContractClauseType.LIMITATION_OF_LIABILITY: [
            r"(?:limitation\s+of\s+liability|limit\s+liability|maximum\s+liability)",
            r"(?:aggregate\s+liability|cap\s+on\s+damages)",
        ],
        ContractClauseType.CONFIDENTIALITY: [
            r"(?:confidential|non-disclosure|nda|proprietary\s+information)",
        ],
        ContractClauseType.INTELLECTUAL_PROPERTY: [
            r"(?:intellectual\s+property|ip\s+rights|patent|trademark|copyright)",
        ],
        ContractClauseType.FORCE_MAJEURE: [
            r"(?:force\s+majeure|act\s+of\s+god|unforeseeable\s+circumstances)",
        ],
        ContractClauseType.GOVERNING_LAW: [
            r"(?:governing\s+law|applicable\s+law|jurisdiction)",
        ],
        ContractClauseType.DISPUTE_RESOLUTION: [
            r"(?:dispute\s+resolution|arbitration|mediation)",
        ],
        ContractClauseType.ASSIGNMENT: [
            r"(?:assignment|transfer\s+of\s+rights|assignable)",
        ],
        ContractClauseType.PAYMENT: [
            r"(?:payment\s+terms|payment\s+schedule|fee|compensation|invoice)",
        ],
        ContractClauseType.WARRANTY: [
            r"(?:warrant|representation|guarantee)",
        ],
        ContractClauseType.INSURANCE: [
            r"(?:insurance|coverage|policy)",
        ],
    }

    # Risk indicators
    RISK_INDICATORS = {
        RiskLevel.CRITICAL: [
            r"(?:unlimited\s+liability|personal\s+guarantee|waive\s+all\s+rights)",
            r"(?:automatic\s+renewal|perpetual\s+license)",
        ],
        RiskLevel.HIGH: [
            r"(?:exclusive\s+rights|non-compete|non-solicitation)",
            r"(?:termination\s+for\s+convenience|terminate\s+at\s+any\s+time)",
        ],
        RiskLevel.MEDIUM: [
            r"(?:change\s+in\s+control|material\s+breach|cure\s+period)",
        ],
    }

    def __init__(self) -> None:
        """Initialize the contract analyzer."""
        self._nlp_available = self._check_nlp()

    def _check_nlp(self) -> bool:
        """Check if NLP libraries are available."""
        try:
            import spacy  # noqa: F401
            return True
        except Exception:
            return False

    async def analyze(self, request: ContractAnalyzeRequest) -> ContractAnalyzeResponse:
        """Analyze a contract document.

        Args:
            request: The analyze request with file path or content

        Returns:
            Analyzed contract data
        """
        start_time = time.time()
        text = await self._extract_text(request)

        # Extract contract metadata
        title = self._extract_title(text)
        contract_type = self._detect_contract_type(text)
        effective_date, expiration_date = self._extract_dates(text)
        parties = self._extract_parties(text)

        # Extract clauses
        clauses = self._extract_clauses(text, request.analyze_risks)

        # Extract obligations
        obligations = (
            self._extract_obligations(text, parties)
            if request.extract_obligations
            else []
        )

        # Extract key dates
        key_dates = self._extract_key_dates(text)

        # Extract monetary values
        total_value, currency = self._extract_value(text)

        # Calculate risk summary
        risk_summary, overall_risk = self._assess_risks(clauses, text)

        # Generate recommendations
        recommendations = self._generate_recommendations(clauses, risk_summary)

        # Generate summary
        summary = self._generate_summary(
            title, contract_type, parties, effective_date, total_value
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            title, parties, clauses, effective_date
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        return ContractAnalyzeResponse(
            title=title,
            contract_type=contract_type,
            effective_date=effective_date,
            expiration_date=expiration_date,
            parties=parties,
            clauses=clauses,
            obligations=obligations,
            key_dates=key_dates,
            total_value=total_value,
            currency=currency,
            risk_summary=risk_summary,
            overall_risk_level=overall_risk,
            recommendations=recommendations,
            summary=summary,
            confidence_score=confidence,
            processing_time_ms=processing_time_ms,
        )

    async def _extract_text(self, request: ContractAnalyzeRequest) -> str:
        """Extract text from the contract document."""
        if request.content:
            content = base64.b64decode(request.content)
            return await self._extract_from_bytes(content)
        elif request.file_path:
            path = Path(request.file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {request.file_path}")

            suffix = path.suffix.lower()
            if suffix == ".pdf":
                return await self._extract_from_pdf(path)
            elif suffix == ".docx":
                return await self._extract_from_docx(path)
            else:
                return path.read_text(encoding="utf-8")
        return ""

    async def _extract_from_bytes(self, content: bytes) -> str:
        """Extract text from raw bytes."""
        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception:
            return content.decode("utf-8", errors="ignore")

    async def _extract_from_pdf(self, path: Path) -> str:
        """Extract text from a PDF file."""
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

    async def _extract_from_docx(self, path: Path) -> str:
        """Extract text from a DOCX file."""
        try:
            from docx import Document
            doc = Document(str(path))
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            return ""

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract contract title."""
        # Look for title in first few lines
        lines = text.strip().split("\n")[:10]

        for line in lines:
            line = line.strip()
            # Look for "Agreement" or "Contract" in line
            if re.search(r"(?:agreement|contract)", line, re.IGNORECASE):
                # Clean up the title
                title = re.sub(r"^\d+[\.\)]\s*", "", line)
                title = title.strip()
                if 10 < len(title) < 200:
                    return title

        return None

    def _detect_contract_type(self, text: str) -> Optional[str]:
        """Detect the type of contract."""
        text_lower = text.lower()

        contract_types = {
            "Employment Agreement": ["employment", "employee", "employer", "hire"],
            "Non-Disclosure Agreement": ["non-disclosure", "nda", "confidential"],
            "Service Agreement": ["service agreement", "services", "contractor"],
            "License Agreement": ["license", "licensing", "licensed"],
            "Sales Agreement": ["sale", "purchase", "buyer", "seller"],
            "Lease Agreement": ["lease", "tenant", "landlord", "rental"],
            "Partnership Agreement": ["partnership", "partners", "joint venture"],
            "Consulting Agreement": ["consulting", "consultant"],
            "Subscription Agreement": ["subscription", "subscriber"],
            "Master Service Agreement": ["master service", "msa"],
        }

        for contract_type, keywords in contract_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return contract_type

        return "General Agreement"

    def _extract_dates(
        self, text: str
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract effective and expiration dates."""
        effective_date = None
        expiration_date = None

        # Effective date patterns
        effective_match = re.search(
            r"(?:effective\s+(?:date|as\s+of)|dated\s+as\s+of|commenc)"
            r"[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})",
            text, re.IGNORECASE
        )
        if effective_match:
            effective_date = self._parse_date(effective_match.group(1))

        # Expiration date patterns
        expiration_match = re.search(
            r"(?:expir|terminat|end\s+date|valid\s+until)"
            r"[:\s]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})",
            text, re.IGNORECASE
        )
        if expiration_match:
            expiration_date = self._parse_date(expiration_match.group(1))

        return effective_date, expiration_date

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into datetime."""
        formats = [
            "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%m-%d-%Y", "%d-%m-%Y", "%Y-%m-%d",
            "%B %d, %Y", "%b %d, %Y", "%B %d %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    def _extract_parties(self, text: str) -> List[ContractParty]:
        """Extract parties to the contract."""
        parties: List[ContractParty] = []

        # Look for party definitions
        party_pattern = r'"([^"]+)"(?:\s*,?\s*a\s+)?(?:(\w+)(?:\s+organized|\s+incorporated)?)?'

        # Also look for "between X and Y" pattern
        between_match = re.search(
            r"between\s+(.+?)\s+(?:and|&)\s+(.+?)(?:\.|,|\n)",
            text[:2000], re.IGNORECASE
        )

        if between_match:
            party1 = between_match.group(1).strip()
            party2 = between_match.group(2).strip()

            # Clean party names
            party1 = re.sub(r'^["\'](.*)["\']$', r"\1", party1)
            party2 = re.sub(r'^["\'](.*)["\']$', r"\1", party2)

            parties.append(ContractParty(name=party1, role="Party A"))
            parties.append(ContractParty(name=party2, role="Party B"))

        return parties

    def _extract_clauses(
        self, text: str, analyze_risks: bool
    ) -> List[ContractClause]:
        """Extract and analyze clauses from the contract."""
        clauses: List[ContractClause] = []

        # Split text into sections by numbered headers
        sections = re.split(r"\n\s*(?:\d+[\.\)]\s*|\(?[a-z]\)\s*)", text)

        for i, section in enumerate(sections):
            if len(section) < 50:
                continue

            # Detect clause type
            clause_type = self._classify_clause(section)
            if clause_type == ContractClauseType.OTHER:
                continue

            # Extract title
            lines = section.strip().split("\n")
            title = lines[0][:100] if lines else f"Section {i}"

            # Analyze risk if requested
            risk_level = RiskLevel.INFORMATIONAL
            risk_explanation = None
            suggestions: List[str] = []

            if analyze_risks:
                risk_level, risk_explanation = self._analyze_clause_risk(section)
                if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    suggestions = self._generate_clause_suggestions(clause_type, section)

            clauses.append(ContractClause(
                clause_type=clause_type,
                title=title,
                text=section[:2000],
                risk_level=risk_level,
                risk_explanation=risk_explanation,
                suggestions=suggestions,
                confidence=ConfidenceLevel.MEDIUM,
            ))

        return clauses

    def _classify_clause(self, text: str) -> ContractClauseType:
        """Classify a clause based on its content."""
        text_lower = text.lower()

        for clause_type, patterns in self.CLAUSE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return clause_type

        return ContractClauseType.OTHER

    def _analyze_clause_risk(
        self, text: str
    ) -> Tuple[RiskLevel, Optional[str]]:
        """Analyze risk level of a clause."""
        text_lower = text.lower()

        for risk_level, patterns in self.RISK_INDICATORS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    return risk_level, f"Contains potentially risky language: '{match.group(0)}'"

        return RiskLevel.INFORMATIONAL, None

    def _generate_clause_suggestions(
        self, clause_type: ContractClauseType, text: str
    ) -> List[str]:
        """Generate improvement suggestions for a clause."""
        suggestions: List[str] = []

        if clause_type == ContractClauseType.LIMITATION_OF_LIABILITY:
            if "unlimited" in text.lower():
                suggestions.append("Consider adding a liability cap")
            suggestions.append("Review whether the limitation scope is appropriate")

        elif clause_type == ContractClauseType.TERMINATION:
            if "convenience" in text.lower():
                suggestions.append("Consider adding notice period requirements")
            suggestions.append("Ensure termination rights are mutual")

        elif clause_type == ContractClauseType.INDEMNIFICATION:
            suggestions.append("Review scope of indemnification obligations")
            suggestions.append("Consider adding carve-outs for negligence")

        return suggestions

    def _extract_obligations(
        self, text: str, parties: List[ContractParty]
    ) -> List[ContractObligation]:
        """Extract obligations from the contract."""
        obligations: List[ContractObligation] = []

        # Look for "shall" and "must" patterns
        obligation_pattern = r"([A-Z][^.]*?)\s+(?:shall|must|agrees?\s+to|is\s+obligated\s+to)\s+([^.]+)"

        for match in re.finditer(obligation_pattern, text):
            subject = match.group(1).strip()
            action = match.group(2).strip()

            # Try to match subject to a party
            party_name = subject
            for party in parties:
                if party.name.lower() in subject.lower():
                    party_name = party.name
                    break

            if len(action) > 10:
                obligations.append(ContractObligation(
                    party=party_name,
                    obligation=action[:500],
                ))

        return obligations[:20]  # Limit to 20 obligations

    def _extract_key_dates(self, text: str) -> Dict[str, datetime]:
        """Extract key dates from the contract."""
        key_dates: Dict[str, datetime] = {}

        date_labels = [
            "effective date",
            "start date",
            "end date",
            "expiration date",
            "termination date",
            "renewal date",
            "payment date",
            "delivery date",
        ]

        for label in date_labels:
            pattern = rf"{label}[:\s]*(\d{{1,2}}[-/]\d{{1,2}}[-/]\d{{2,4}})"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed = self._parse_date(match.group(1))
                if parsed:
                    key_dates[label.replace(" ", "_")] = parsed

        return key_dates

    def _extract_value(self, text: str) -> Tuple[Optional[float], Optional[str]]:
        """Extract monetary value from contract."""
        # Look for total value patterns
        value_pattern = r"(?:total\s+)?(?:value|amount|price|fee|compensation)[:\s]*[$€£]?\s*([\d,]+(?:\.\d{2})?)"
        match = re.search(value_pattern, text, re.IGNORECASE)

        if match:
            value = float(match.group(1).replace(",", ""))
            currency = "USD"
            if "€" in text[:match.start() + 50]:
                currency = "EUR"
            elif "£" in text[:match.start() + 50]:
                currency = "GBP"
            return value, currency

        return None, None

    def _assess_risks(
        self, clauses: List[ContractClause], text: str
    ) -> Tuple[Dict[str, int], RiskLevel]:
        """Assess overall contract risks."""
        risk_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "informational": 0,
        }

        for clause in clauses:
            risk_counts[clause.risk_level.value] += 1

        # Determine overall risk
        if risk_counts["critical"] > 0:
            overall = RiskLevel.CRITICAL
        elif risk_counts["high"] > 2:
            overall = RiskLevel.HIGH
        elif risk_counts["high"] > 0 or risk_counts["medium"] > 3:
            overall = RiskLevel.MEDIUM
        else:
            overall = RiskLevel.LOW

        return risk_counts, overall

    def _generate_recommendations(
        self, clauses: List[ContractClause], risk_summary: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations: List[str] = []

        # Check for missing important clauses
        found_types = {c.clause_type for c in clauses}
        important_types = [
            ContractClauseType.LIMITATION_OF_LIABILITY,
            ContractClauseType.TERMINATION,
            ContractClauseType.CONFIDENTIALITY,
            ContractClauseType.GOVERNING_LAW,
        ]

        for clause_type in important_types:
            if clause_type not in found_types:
                recommendations.append(
                    f"Consider adding a {clause_type.value.replace('_', ' ')} clause"
                )

        # Risk-based recommendations
        if risk_summary.get("critical", 0) > 0:
            recommendations.append("Critical risk items require immediate legal review")

        if risk_summary.get("high", 0) > 0:
            recommendations.append("High risk items should be negotiated before signing")

        return recommendations

    def _generate_summary(
        self,
        title: Optional[str],
        contract_type: Optional[str],
        parties: List[ContractParty],
        effective_date: Optional[datetime],
        total_value: Optional[float],
    ) -> str:
        """Generate a contract summary."""
        parts = []

        if title:
            parts.append(f"This is a {title}")
        elif contract_type:
            parts.append(f"This is a {contract_type}")

        if len(parties) >= 2:
            parts.append(f"between {parties[0].name} and {parties[1].name}")

        if effective_date:
            parts.append(f"effective {effective_date.strftime('%B %d, %Y')}")

        if total_value:
            parts.append(f"with a total value of ${total_value:,.2f}")

        return " ".join(parts) + "." if parts else "Contract analysis complete."

    def _calculate_confidence(
        self,
        title: Optional[str],
        parties: List[ContractParty],
        clauses: List[ContractClause],
        effective_date: Optional[datetime],
    ) -> float:
        """Calculate overall confidence score."""
        score = 0.0

        if title:
            score += 0.2
        if len(parties) >= 2:
            score += 0.3
        if len(clauses) >= 3:
            score += 0.3
        if effective_date:
            score += 0.2

        return min(score, 1.0)


# Singleton instance
contract_analyzer = ContractAnalyzer()
