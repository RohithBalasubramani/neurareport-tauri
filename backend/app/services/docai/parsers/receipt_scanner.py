"""Receipt Scanner Service.

Extracts structured data from receipt images and documents.
"""
from __future__ import annotations

import base64
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from backend.app.schemas.docai import (
    ReceiptItem,
    ReceiptScanRequest,
    ReceiptScanResponse,
)


class ReceiptScanner:
    """Scanner for extracting data from receipt documents."""

    # Common receipt categories
    CATEGORY_KEYWORDS = {
        "Groceries": ["grocery", "supermarket", "food", "produce", "dairy", "meat"],
        "Restaurant": ["restaurant", "cafe", "diner", "bar", "grill", "pizza", "sushi"],
        "Gas Station": ["gas", "fuel", "petroleum", "shell", "exxon", "chevron", "bp"],
        "Retail": ["store", "shop", "mart", "outlet", "boutique"],
        "Pharmacy": ["pharmacy", "drug", "cvs", "walgreens", "rite aid"],
        "Electronics": ["electronics", "best buy", "apple", "tech"],
        "Office Supplies": ["office", "staples", "depot"],
        "Hardware": ["hardware", "home depot", "lowes", "ace"],
    }

    # Item category keywords
    ITEM_CATEGORIES = {
        "Food": ["milk", "bread", "eggs", "cheese", "meat", "chicken", "beef", "fish",
                 "fruit", "vegetable", "rice", "pasta", "cereal"],
        "Beverage": ["water", "soda", "juice", "coffee", "tea", "beer", "wine"],
        "Household": ["paper", "towel", "soap", "detergent", "cleaner", "tissue"],
        "Personal Care": ["shampoo", "toothpaste", "deodorant", "lotion"],
        "Snacks": ["chips", "candy", "cookies", "chocolate", "snack"],
    }

    def __init__(self) -> None:
        """Initialize the receipt scanner."""
        self._ocr_available = self._check_ocr()

    def _check_ocr(self) -> bool:
        """Check if OCR libraries are available."""
        try:
            import easyocr  # noqa: F401
            return True
        except ImportError:
            return False

    async def scan(self, request: ReceiptScanRequest) -> ReceiptScanResponse:
        """Scan a receipt document.

        Args:
            request: The scan request with file path or content

        Returns:
            Scanned receipt data
        """
        start_time = time.time()
        text = await self._extract_text(request)

        # Extract merchant information
        merchant_name = self._extract_merchant_name(text)
        merchant_address = self._extract_merchant_address(text)
        merchant_phone = self._extract_merchant_phone(text)

        # Extract date and time
        date, time_str = self._extract_datetime(text)

        # Extract line items
        items = self._extract_items(text, request.categorize_items)

        # Extract amounts
        subtotal = self._extract_subtotal(text)
        tax = self._extract_tax(text)
        tip = self._extract_tip(text)
        total = self._extract_total(text, subtotal, tax, tip, items)

        # Extract payment info
        payment_method, card_last_four = self._extract_payment_info(text)

        # Detect currency
        currency = self._detect_currency(text)

        # Categorize receipt
        category = self._categorize_receipt(text, merchant_name)

        # Calculate confidence
        confidence = self._calculate_confidence(
            merchant_name, date, total, items
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        return ReceiptScanResponse(
            merchant_name=merchant_name,
            merchant_address=merchant_address,
            merchant_phone=merchant_phone,
            date=date,
            time=time_str,
            items=items,
            subtotal=subtotal,
            tax=tax,
            tip=tip,
            total=total,
            payment_method=payment_method,
            card_last_four=card_last_four,
            currency=currency,
            category=category,
            raw_text=text[:3000] if text else None,
            confidence_score=confidence,
            processing_time_ms=processing_time_ms,
        )

    async def _extract_text(self, request: ReceiptScanRequest) -> str:
        """Extract text from the receipt document."""
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
            if text.strip():
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
                return "\n".join([result[1] for result in results])
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
            return "\n".join([result[1] for result in results])
        except Exception:
            return ""

    def _extract_merchant_name(self, text: str) -> Optional[str]:
        """Extract merchant name from receipt."""
        # Usually the merchant name is in the first few lines
        lines = text.strip().split("\n")[:5]

        for line in lines:
            line = line.strip()
            # Skip lines that look like addresses or phone numbers
            if "@" in line or re.search(r"\d{3}[-.\s]?\d{3}", line):
                continue
            if re.search(r"\d+\s+\w+\s+(?:st|ave|rd|blvd|dr|ln)", line, re.IGNORECASE):
                continue

            # Take first substantial line
            if 3 < len(line) < 50:
                return line

        return None

    def _extract_merchant_address(self, text: str) -> Optional[str]:
        """Extract merchant address from receipt."""
        # Look for address pattern
        address_match = re.search(
            r"(\d+\s+[\w\s]+(?:st|street|ave|avenue|rd|road|blvd|boulevard|dr|drive|ln|lane)[.,]?\s*"
            r"[\w\s]*,?\s*[A-Z]{2}\s*\d{5})",
            text, re.IGNORECASE
        )
        if address_match:
            return address_match.group(1)

        return None

    def _extract_merchant_phone(self, text: str) -> Optional[str]:
        """Extract merchant phone from receipt."""
        phone_match = re.search(
            r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            text
        )
        if phone_match:
            return phone_match.group(0)

        return None

    def _extract_datetime(
        self, text: str
    ) -> Tuple[Optional[datetime], Optional[str]]:
        """Extract date and time from receipt."""
        date_obj = None
        time_str = None

        # Date patterns
        date_patterns = [
            (r"(\d{1,2})/(\d{1,2})/(\d{2,4})", "%m/%d/%Y"),
            (r"(\d{1,2})-(\d{1,2})-(\d{2,4})", "%m-%d-%Y"),
            (r"(\w{3})\s+(\d{1,2}),?\s+(\d{4})", "%b %d %Y"),
        ]

        for pattern, fmt in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0)
                    # Handle 2-digit years
                    if len(date_str.split("/")[-1]) == 2:
                        fmt = fmt.replace("%Y", "%y")
                    date_obj = datetime.strptime(date_str.replace(",", ""), fmt)
                    break
                except ValueError:
                    continue

        # Time pattern
        time_match = re.search(r"(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)", text, re.IGNORECASE)
        if time_match:
            time_str = time_match.group(1)

        return date_obj, time_str

    def _extract_items(
        self, text: str, categorize: bool
    ) -> List[ReceiptItem]:
        """Extract line items from receipt."""
        items: List[ReceiptItem] = []

        # Look for patterns like:
        # ITEM NAME          $9.99
        # ITEM NAME    2@$1.50    $3.00
        item_patterns = [
            # Name followed by price
            r"([A-Z][A-Z\s]{2,30})\s+\$?([\d]+\.[\d]{2})\s*$",
            # Name with quantity and price
            r"([A-Z][A-Z\s]{2,30})\s+(\d+)\s*@\s*\$?([\d]+\.[\d]{2})\s+\$?([\d]+\.[\d]{2})",
            # Simple name and price on same line
            r"^([^$\d]{3,30})\s+\$?([\d]+\.[\d]{2})",
        ]

        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # Skip header/footer lines
            if any(skip in line.lower() for skip in
                   ["subtotal", "total", "tax", "cash", "credit", "change", "thank you"]):
                continue

            for pattern in item_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()

                    if len(groups) >= 4:
                        # With quantity
                        name = groups[0].strip()
                        quantity = float(groups[1])
                        unit_price = float(groups[2])
                        total_price = float(groups[3])
                    elif len(groups) >= 2:
                        # Without quantity
                        name = groups[0].strip()
                        quantity = 1.0
                        total_price = float(groups[1])
                        unit_price = total_price
                    else:
                        continue

                    # Categorize if requested
                    category = None
                    if categorize:
                        category = self._categorize_item(name)

                    items.append(ReceiptItem(
                        name=name,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        category=category,
                    ))
                    break

        return items

    def _categorize_item(self, name: str) -> Optional[str]:
        """Categorize an item based on its name."""
        name_lower = name.lower()

        for category, keywords in self.ITEM_CATEGORIES.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category

        return None

    def _extract_subtotal(self, text: str) -> Optional[float]:
        """Extract subtotal from receipt."""
        subtotal_match = re.search(
            r"(?:sub\s*total|subtotal)\s*:?\s*\$?([\d,]+\.[\d]{2})",
            text, re.IGNORECASE
        )
        if subtotal_match:
            return float(subtotal_match.group(1).replace(",", ""))

        return None

    def _extract_tax(self, text: str) -> Optional[float]:
        """Extract tax from receipt."""
        tax_match = re.search(
            r"(?:tax|sales\s+tax|vat)\s*:?\s*\$?([\d,]+\.[\d]{2})",
            text, re.IGNORECASE
        )
        if tax_match:
            return float(tax_match.group(1).replace(",", ""))

        return None

    def _extract_tip(self, text: str) -> Optional[float]:
        """Extract tip from receipt."""
        tip_match = re.search(
            r"(?:tip|gratuity)\s*:?\s*\$?([\d,]+\.[\d]{2})",
            text, re.IGNORECASE
        )
        if tip_match:
            return float(tip_match.group(1).replace(",", ""))

        return None

    def _extract_total(
        self,
        text: str,
        subtotal: Optional[float],
        tax: Optional[float],
        tip: Optional[float],
        items: List[ReceiptItem],
    ) -> float:
        """Extract or calculate total from receipt."""
        # Try to find total directly
        total_patterns = [
            r"(?m)^\s*(?:grand\s+)?total\b\s*:?\s*\$?([\d,]+\.[\d]{2})",
            r"(?m)^\s*amount\s+due\b\s*:?\s*\$?([\d,]+\.[\d]{2})",
            r"(?m)^\s*balance\s+due\b\s*:?\s*\$?([\d,]+\.[\d]{2})",
        ]

        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", ""))

        # Calculate from components
        if subtotal:
            total = subtotal
            if tax:
                total += tax
            if tip:
                total += tip
            return total

        # Sum items
        if items:
            return sum(item.total_price for item in items)

        return 0.0

    def _extract_payment_info(
        self, text: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract payment method and card info."""
        payment_method = None
        card_last_four = None

        # Payment method
        if re.search(r"(?:visa|mastercard|amex|american\s+express|discover)", text, re.IGNORECASE):
            payment_method = "Credit Card"
        elif re.search(r"(?:debit|debit\s+card)", text, re.IGNORECASE):
            payment_method = "Debit Card"
        elif re.search(r"(?:cash|cash\s+payment)", text, re.IGNORECASE):
            payment_method = "Cash"
        elif re.search(r"(?:apple\s+pay|google\s+pay|paypal)", text, re.IGNORECASE):
            payment_method = "Digital Payment"

        # Card last four digits
        card_match = re.search(r"(?:\*+|x+)(\d{4})", text, re.IGNORECASE)
        if card_match:
            card_last_four = card_match.group(1)

        return payment_method, card_last_four

    def _detect_currency(self, text: str) -> str:
        """Detect currency from receipt."""
        text_upper = text.upper()
        if "$" in text or re.search(r"\bUSD\b", text_upper):
            return "USD"
        if re.search(r"\bEUR\b", text_upper):
            return "EUR"
        if re.search(r"\bGBP\b", text_upper):
            return "GBP"
        if re.search(r"\bJPY\b", text_upper):
            return "JPY"
        if re.search(r"\bCAD\b", text_upper) or "C$" in text:
            return "CAD"
        return "USD"
    def _categorize_receipt(
        self, text: str, merchant_name: Optional[str]
    ) -> Optional[str]:
        """Categorize the receipt based on content."""
        text_lower = text.lower()
        merchant_lower = (merchant_name or "").lower()

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower or keyword in merchant_lower:
                    return category

        return None

    def _calculate_confidence(
        self,
        merchant_name: Optional[str],
        date: Optional[datetime],
        total: float,
        items: List[ReceiptItem],
    ) -> float:
        """Calculate overall confidence score."""
        score = 0.0

        if merchant_name:
            score += 0.25
        if date:
            score += 0.25
        if total > 0:
            score += 0.25
        if items:
            score += 0.25

        return score


# Singleton instance
receipt_scanner = ReceiptScanner()
