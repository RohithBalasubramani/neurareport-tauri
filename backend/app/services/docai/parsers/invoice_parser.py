"""Invoice Parser Service.

Extracts structured data from invoice documents using OCR and pattern matching.
"""
from __future__ import annotations

import base64
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.app.schemas.docai import (
    ConfidenceLevel,
    InvoiceAddress,
    InvoiceLineItem,
    InvoiceParseRequest,
    InvoiceParseResponse,
)


class InvoiceParser:
    """Parser for extracting data from invoice documents."""

    # Common invoice field patterns
    INVOICE_NUMBER_PATTERNS = [
        r"(?:invoice|inv|bill)\s*(?:#|no\.?|number)\s*[:\s]*([A-Z0-9-]+)",
        r"(?:reference|ref)\s*(?:#|no\.?|number)\s*[:\s]*([A-Z0-9-]+)",
    ]

    DATE_PATTERNS = [
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
        r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4})",
    ]

    AMOUNT_PATTERNS = [
        r"(?m)^\s*(?:grand\s+total|total|amount\s+due|balance\s+due)\b\s*[:\s]*(?:[$]|[A-Z]{3})?\s*([\d,]+\.?\d*)",
        r"(?:[$]|[A-Z]{3})\s*([\d,]+\.?\d*)\s*(?:total|due)\b",
    ]

    def __init__(self) -> None:
        """Initialize the invoice parser."""
        self._ocr_available = self._check_ocr()

    def _check_ocr(self) -> bool:
        """Check if OCR libraries are available."""
        try:
            import easyocr  # noqa: F401
            return True
        except ImportError:
            return False

    async def parse(self, request: InvoiceParseRequest) -> InvoiceParseResponse:
        """Parse an invoice document.

        Args:
            request: The parse request with file path or content

        Returns:
            Parsed invoice data
        """
        start_time = time.time()
        text = await self._extract_text(request)

        # Extract fields
        invoice_number = self._extract_invoice_number(text)
        invoice_date, due_date = self._extract_dates(text)
        vendor, bill_to = self._extract_addresses(text) if request.extract_addresses else (None, None)
        line_items = self._extract_line_items(text) if request.extract_line_items else []
        subtotal, tax_total, total = self._extract_amounts(text)
        currency = self._detect_currency(text)
        payment_terms = self._extract_payment_terms(text)

        # Calculate confidence
        confidence = self._calculate_confidence(
            invoice_number, invoice_date, total, line_items
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        return InvoiceParseResponse(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            vendor=vendor,
            bill_to=bill_to,
            line_items=line_items,
            subtotal=subtotal,
            tax_total=tax_total,
            total=total,
            currency=currency,
            payment_terms=payment_terms,
            raw_text=text[:5000] if text else None,
            confidence_score=confidence,
            processing_time_ms=processing_time_ms,
        )

    async def _extract_text(self, request: InvoiceParseRequest) -> str:
        """Extract text from the invoice document."""
        if request.content:
            # Base64 encoded content
            content = base64.b64decode(request.content)
            return await self._extract_from_bytes(content)
        elif request.file_path:
            path = Path(request.file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {request.file_path}")

            suffix = path.suffix.lower()
            if suffix == ".pdf":
                return await self._extract_from_pdf(path)
            elif suffix in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                return await self._extract_from_image(path)
            else:
                return path.read_text(encoding="utf-8")
        return ""

    async def _extract_from_bytes(self, content: bytes) -> str:
        """Extract text from raw bytes."""
        # Try PDF first
        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception:
            pass

        # Try as image with OCR
        if self._ocr_available:
            try:
                import easyocr
                import io
                from PIL import Image

                reader = easyocr.Reader(["en"])
                image = Image.open(io.BytesIO(content))
                results = reader.readtext(image)
                return " ".join([result[1] for result in results])
            except Exception:
                pass

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

    async def _extract_from_image(self, path: Path) -> str:
        """Extract text from an image using OCR."""
        if not self._ocr_available:
            return ""

        try:
            import easyocr
            reader = easyocr.Reader(["en"])
            results = reader.readtext(str(path))
            return " ".join([result[1] for result in results])
        except Exception:
            return ""

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text."""
        text_lower = text.lower()
        for pattern in self.INVOICE_NUMBER_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def _extract_dates(self, text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract invoice date and due date from text."""
        dates: List[datetime] = []

        for pattern in self.DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    date_str = match.group(1)
                    parsed = self._parse_date(date_str)
                    if parsed:
                        dates.append(parsed)
                except Exception:
                    continue

        # Sort dates - typically first is invoice date, later is due date
        dates = sorted(set(dates))

        invoice_date = dates[0] if dates else None
        due_date = dates[-1] if len(dates) > 1 else None

        return invoice_date, due_date

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into datetime."""
        formats = [
            "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
            "%m-%d-%Y", "%d-%m-%Y", "%Y-%m-%d",
            "%B %d, %Y", "%b %d, %Y",
            "%m/%d/%y", "%d/%m/%y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    def _extract_addresses(
        self, text: str
    ) -> Tuple[Optional[InvoiceAddress], Optional[InvoiceAddress]]:
        """Extract vendor and billing addresses."""
        # Simple heuristic: look for address-like blocks
        vendor = None
        bill_to = None

        # Look for "From" or "Vendor" section
        from_match = re.search(
            r"(?:from|vendor|seller|company)[:\s]*\n(.+?)(?:\n\n|bill\s*to|ship\s*to)",
            text, re.IGNORECASE | re.DOTALL
        )
        if from_match:
            vendor = self._parse_address_block(from_match.group(1))

        # Look for "Bill To" section
        bill_match = re.search(
            r"(?:bill\s*to|customer|client)[:\s]*\n(.+?)(?:\n\n|ship\s*to|items|description)",
            text, re.IGNORECASE | re.DOTALL
        )
        if bill_match:
            bill_to = self._parse_address_block(bill_match.group(1))

        return vendor, bill_to

    def _parse_address_block(self, text: str) -> InvoiceAddress:
        """Parse an address text block."""
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

        name = lines[0] if lines else None
        street = lines[1] if len(lines) > 1 else None

        # Extract email
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        email = email_match.group(0) if email_match else None

        # Extract phone
        phone_match = re.search(r"[\d\s\-\+\(\)]{10,}", text)
        phone = phone_match.group(0).strip() if phone_match else None

        return InvoiceAddress(
            name=name,
            street=street,
            email=email,
            phone=phone,
        )

    def _extract_line_items(self, text: str) -> List[InvoiceLineItem]:
        """Extract line items from invoice."""
        items: List[InvoiceLineItem] = []

        # Look for tabular data pattern
        # Description | Qty | Price | Amount
        line_pattern = r"(.+?)\s+(\d+(?:\.\d+)?)\s+\$?([\d,]+\.?\d*)\s+\$?([\d,]+\.?\d*)"

        for match in re.finditer(line_pattern, text):
            try:
                description = match.group(1).strip()
                quantity = float(match.group(2))
                unit_price = float(match.group(3).replace(",", ""))
                amount = float(match.group(4).replace(",", ""))

                if description and len(description) > 2:
                    items.append(InvoiceLineItem(
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price,
                        amount=amount,
                        confidence=ConfidenceLevel.MEDIUM,
                    ))
            except (ValueError, IndexError):
                continue

        return items

    def _extract_amounts(self, text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Extract subtotal, tax, and total amounts."""
        subtotal = None
        tax = None
        total = None

        # Subtotal
        subtotal_match = re.search(
            r"(?:sub\s*total|subtotal)\s*[:\s]*[$€£¥]?\s*([\d,]+\.?\d*)",
            text, re.IGNORECASE
        )
        if subtotal_match:
            subtotal = float(subtotal_match.group(1).replace(",", ""))

        # Tax
        tax_match = re.search(
            r"(?:tax|vat|gst)\s*[:\s]*[$€£¥]?\s*([\d,]+\.?\d*)",
            text, re.IGNORECASE
        )
        if tax_match:
            tax = float(tax_match.group(1).replace(",", ""))

        # Total
        for pattern in self.AMOUNT_PATTERNS:
            total_match = re.search(pattern, text, re.IGNORECASE)
            if total_match:
                total = float(total_match.group(1).replace(",", ""))
                break

        return subtotal, tax, total

    def _detect_currency(self, text: str) -> str:
        """Detect currency from text."""
        text_upper = text.upper()
        if "$" in text or re.search(r"\bUSD\b", text_upper):
            return "USD"
        if re.search(r"\bEUR\b", text_upper):
            return "EUR"
        if re.search(r"\bGBP\b", text_upper):
            return "GBP"
        if re.search(r"\b(?:JPY|CNY)\b", text_upper):
            return "JPY"
        return "USD"
    def _extract_payment_terms(self, text: str) -> Optional[str]:
        """Extract payment terms from invoice."""
        terms_match = re.search(
            r"(?:payment\s*terms?|terms?)[:\s]*(.+?)(?:\n|$)",
            text, re.IGNORECASE
        )
        if terms_match:
            return terms_match.group(1).strip()[:100]

        # Look for "Net XX" patterns
        net_match = re.search(r"(net\s*\d+)", text, re.IGNORECASE)
        if net_match:
            return net_match.group(1)

        return None

    def _calculate_confidence(
        self,
        invoice_number: Optional[str],
        invoice_date: Optional[datetime],
        total: Optional[float],
        line_items: List[InvoiceLineItem],
    ) -> float:
        """Calculate overall confidence score."""
        score = 0.0

        if invoice_number:
            score += 0.25
        if invoice_date:
            score += 0.25
        if total is not None:
            score += 0.25
        if line_items:
            score += 0.25

        return score


# Singleton instance
invoice_parser = InvoiceParser()
