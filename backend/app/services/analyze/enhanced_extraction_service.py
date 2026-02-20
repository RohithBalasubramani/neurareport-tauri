# mypy: ignore-errors
"""
Enhanced Extraction Service - Intelligent data extraction from documents.

Features:
1.1 Smart Table Detection & Normalization
1.2 Entity & Metric Extraction
1.3 Form & Invoice Intelligence
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.app.schemas.analyze.enhanced_analysis import (
    DocumentType,
    EnhancedExtractedTable,
    EntityType,
    ExtractedContract,
    ExtractedEntity,
    ExtractedInvoice,
    ExtractedMetric,
    FormField,
    InvoiceLineItem,
    MetricType,
    TableRelationship,
)
from backend.app.services.utils.llm import (
    call_chat_completion,
    extract_json_from_llm_response,
    extract_json_array_from_llm_response,
)
from backend.app.services.llm.client import get_llm_client

logger = logging.getLogger("neura.analyze.extraction")


# =============================================================================
# ENTITY EXTRACTION
# =============================================================================

ENTITY_PATTERNS = {
    EntityType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    EntityType.PHONE: r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
    EntityType.URL: r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\-.?=%&]*',
    EntityType.PERCENTAGE: r'\b\d+(?:\.\d+)?%\b',
    EntityType.MONEY: r'(?:\$|€|£|¥|USD|EUR|GBP)\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|euros?|pounds?|USD|EUR|GBP)\b',
    EntityType.DATE: r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}|Q[1-4]\s*\d{4}|FY\d{2,4})\b',
}


def extract_entities_regex(text: str) -> List[ExtractedEntity]:
    """Extract entities using regex patterns."""
    entities = []
    seen = set()

    for entity_type, pattern in ENTITY_PATTERNS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group().strip()
            key = f"{entity_type}:{value.lower()}"

            if key not in seen:
                seen.add(key)
                entities.append(ExtractedEntity(
                    id=f"ent_{uuid.uuid4().hex[:8]}",
                    type=entity_type,
                    value=value,
                    confidence=0.9,
                    position={"start": match.start(), "end": match.end()},
                    context=text[max(0, match.start() - 50):match.end() + 50],
                ))

    return entities


def extract_entities_llm(text: str, client: Any) -> List[ExtractedEntity]:
    """Extract entities using LLM for named entity recognition."""
    prompt = f"""Extract all named entities from the following text. Identify:
- PERSON: Names of people
- ORGANIZATION: Company names, institutions
- LOCATION: Cities, countries, addresses
- PRODUCT: Product or service names
- DATE: Dates, time periods (normalize to ISO format when possible)
- MONEY: Currency amounts (normalize to number + currency code)
- PERCENTAGE: Percentage values

Text:
{text[:8000]}

Return JSON array:
```json
[
  {{"type": "PERSON", "value": "John Smith", "normalized": "John Smith", "context": "CEO John Smith announced..."}},
  {{"type": "MONEY", "value": "$1.5M", "normalized": 1500000, "currency": "USD", "context": "revenue of $1.5M"}},
  {{"type": "DATE", "value": "Q3 2025", "normalized": "2025-07-01/2025-09-30", "context": "in Q3 2025"}}
]
```

Extract ALL entities found. Be thorough."""

    try:
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="entity_extraction",
            temperature=0.1,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_array_from_llm_response(raw_text, default=[])
        if data:
            entities = []
            for item in data:
                entity_type = item.get("type", "").upper()
                try:
                    etype = EntityType[entity_type]
                except KeyError:
                    etype = EntityType.CUSTOM

                entities.append(ExtractedEntity(
                    id=f"ent_{uuid.uuid4().hex[:8]}",
                    type=etype,
                    value=item.get("value", ""),
                    normalized_value=str(item.get("normalized", "")),
                    confidence=0.85,
                    context=item.get("context"),
                    metadata={"currency": item.get("currency")} if item.get("currency") else {},
                ))
            return entities
    except Exception as e:
        logger.warning(f"LLM entity extraction failed: {e}")

    return []


def extract_all_entities(text: str, use_llm: bool = True) -> List[ExtractedEntity]:
    """Extract entities using both regex and LLM."""
    # Start with regex extraction (fast, high precision)
    entities = extract_entities_regex(text)
    entity_values = {e.value.lower() for e in entities}

    # Add LLM extraction for semantic entities
    if use_llm:
        try:
            client = get_llm_client()
            llm_entities = extract_entities_llm(text, client)

            # Merge, avoiding duplicates
            for ent in llm_entities:
                if ent.value.lower() not in entity_values:
                    entities.append(ent)
                    entity_values.add(ent.value.lower())
        except Exception as e:
            logger.warning(f"LLM extraction skipped: {e}")

    return entities


# =============================================================================
# METRIC EXTRACTION
# =============================================================================

def extract_metrics_llm(text: str, tables: List[EnhancedExtractedTable]) -> List[ExtractedMetric]:
    """Extract key metrics and KPIs using LLM."""
    # Build context from tables
    table_context = ""
    for table in tables[:5]:
        table_context += f"\nTable: {table.title or table.id}\n"
        table_context += f"Headers: {', '.join(table.headers[:10])}\n"
        if table.rows:
            table_context += f"Sample row: {table.rows[0][:10]}\n"

    prompt = f"""Analyze this document and extract ALL key metrics, KPIs, and important numerical data.

Text excerpt:
{text[:6000]}

Tables found:
{table_context}

Extract metrics with context. Return JSON array:
```json
[
  {{
    "name": "Revenue",
    "value": 1500000,
    "raw_value": "$1.5M",
    "metric_type": "currency",
    "unit": null,
    "currency": "USD",
    "period": "Q3 2025",
    "change": 15.5,
    "change_direction": "increase",
    "comparison_base": "vs Q3 2024",
    "context": "Revenue reached $1.5M in Q3 2025, up 15.5% YoY",
    "importance": 0.9
  }},
  {{
    "name": "Customer Count",
    "value": 50000,
    "raw_value": "50,000",
    "metric_type": "count",
    "period": "2025",
    "importance": 0.7
  }}
]
```

Metric types: currency, percentage, count, ratio, duration, quantity, score, rate
Extract ALL significant numbers with their context. Focus on KPIs."""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="metric_extraction",
            temperature=0.1,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_array_from_llm_response(raw_text, default=[])
        if data:
            metrics = []
            for item in data:
                try:
                    mtype = MetricType[item.get("metric_type", "count").upper()]
                except KeyError:
                    mtype = MetricType.COUNT

                raw_val = item.get("value")
                if raw_val is None:
                    raw_val = item.get("raw_value", "0")
                metrics.append(ExtractedMetric(
                    id=f"met_{uuid.uuid4().hex[:8]}",
                    name=item.get("name", "Unknown"),
                    value=raw_val if raw_val is not None else "0",
                    raw_value=str(item.get("raw_value", "")),
                    metric_type=mtype,
                    unit=item.get("unit"),
                    currency=item.get("currency"),
                    period=item.get("period"),
                    change=item.get("change"),
                    change_direction=item.get("change_direction"),
                    comparison_base=item.get("comparison_base"),
                    confidence=0.85,
                    context=item.get("context"),
                    importance_score=float(item.get("importance", 0.5)),
                ))
            return metrics
    except Exception as e:
        logger.warning(f"Metric extraction failed: {e}")

    return []


# =============================================================================
# FORM FIELD EXTRACTION
# =============================================================================

def extract_form_fields(text: str, tables: List[EnhancedExtractedTable]) -> List[FormField]:
    """Extract form fields from document."""
    prompt = f"""Analyze this document and identify if it contains a form. If so, extract all form fields.

Text:
{text[:6000]}

If this is a form, return JSON:
```json
{{
  "is_form": true,
  "form_title": "Application Form",
  "fields": [
    {{
      "label": "Full Name",
      "value": "John Doe",
      "type": "text",
      "required": true,
      "section": "Personal Information"
    }},
    {{
      "label": "Date of Birth",
      "value": "1990-05-15",
      "type": "date",
      "required": true
    }},
    {{
      "label": "Agree to Terms",
      "value": "checked",
      "type": "checkbox",
      "required": true
    }}
  ]
}}
```

Field types: text, checkbox, radio, date, signature, dropdown, number, email, phone
If not a form, return {{"is_form": false, "fields": []}}"""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="form_extraction",
            temperature=0.1,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default={})
        if data:
            if data.get("is_form"):
                fields = []
                for item in data.get("fields", []):
                    fields.append(FormField(
                        id=f"field_{uuid.uuid4().hex[:8]}",
                        label=item.get("label", ""),
                        value=item.get("value"),
                        field_type=item.get("type", "text"),
                        required=item.get("required", False),
                        section=item.get("section"),
                        is_filled=bool(item.get("value")),
                        confidence=0.85,
                    ))
                return fields
    except Exception as e:
        logger.warning(f"Form extraction failed: {e}")

    return []


# =============================================================================
# INVOICE EXTRACTION
# =============================================================================

def extract_invoice(text: str, tables: List[EnhancedExtractedTable]) -> Optional[ExtractedInvoice]:
    """Extract invoice data from document."""
    # Build table context
    table_context = ""
    for table in tables[:3]:
        table_context += f"\nTable: {table.title or 'Untitled'}\n"
        for row in table.rows[:10]:
            table_context += f"  {row}\n"

    prompt = f"""Analyze this document and determine if it's an invoice. If so, extract all invoice data.

Text:
{text[:5000]}

Tables:
{table_context}

If this is an invoice, return JSON:
```json
{{
  "is_invoice": true,
  "vendor_name": "Acme Corp",
  "vendor_address": "123 Main St, City, ST 12345",
  "vendor_tax_id": "12-3456789",
  "customer_name": "Client Inc",
  "customer_address": "456 Oak Ave",
  "invoice_number": "INV-2025-001",
  "invoice_date": "2025-01-15",
  "due_date": "2025-02-15",
  "purchase_order": "PO-12345",
  "line_items": [
    {{
      "description": "Consulting Services",
      "quantity": 10,
      "unit_price": 150.00,
      "total": 1500.00,
      "tax": 120.00
    }}
  ],
  "subtotal": 1500.00,
  "tax_total": 120.00,
  "discount_total": 0,
  "grand_total": 1620.00,
  "currency": "USD",
  "payment_terms": "Net 30",
  "notes": "Thank you for your business"
}}
```

If not an invoice, return {{"is_invoice": false}}"""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="invoice_extraction",
            temperature=0.1,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default={})
        if data:
            if data.get("is_invoice"):
                line_items = []
                for item in data.get("line_items", []):
                    line_items.append(InvoiceLineItem(
                        id=f"li_{uuid.uuid4().hex[:8]}",
                        description=item.get("description", ""),
                        quantity=item.get("quantity"),
                        unit_price=item.get("unit_price"),
                        total=item.get("total"),
                        tax=item.get("tax"),
                        discount=item.get("discount"),
                        sku=item.get("sku"),
                        category=item.get("category"),
                    ))

                return ExtractedInvoice(
                    id=f"inv_{uuid.uuid4().hex[:8]}",
                    vendor_name=data.get("vendor_name"),
                    vendor_address=data.get("vendor_address"),
                    vendor_tax_id=data.get("vendor_tax_id"),
                    customer_name=data.get("customer_name"),
                    customer_address=data.get("customer_address"),
                    invoice_number=data.get("invoice_number"),
                    invoice_date=data.get("invoice_date"),
                    due_date=data.get("due_date"),
                    purchase_order=data.get("purchase_order"),
                    line_items=line_items,
                    subtotal=data.get("subtotal"),
                    tax_total=data.get("tax_total"),
                    discount_total=data.get("discount_total"),
                    grand_total=data.get("grand_total"),
                    currency=data.get("currency", "USD"),
                    payment_terms=data.get("payment_terms"),
                    notes=data.get("notes"),
                    confidence=0.85,
                )
    except Exception as e:
        logger.warning(f"Invoice extraction failed: {e}")

    return None


# =============================================================================
# CONTRACT EXTRACTION
# =============================================================================

def extract_contract(text: str) -> Optional[ExtractedContract]:
    """Extract contract data from document."""
    prompt = f"""Analyze this document and determine if it's a contract or legal agreement. If so, extract key information.

Text:
{text[:8000]}

If this is a contract, return JSON:
```json
{{
  "is_contract": true,
  "contract_type": "Service Agreement",
  "parties": [
    {{"name": "Company A", "role": "Provider"}},
    {{"name": "Company B", "role": "Client"}}
  ],
  "effective_date": "2025-01-01",
  "expiration_date": "2026-01-01",
  "auto_renewal": true,
  "renewal_terms": "Automatically renews for 1-year periods",
  "key_terms": [
    "Monthly payment of $5,000",
    "30-day termination notice required"
  ],
  "obligations": [
    {{"party": "Provider", "obligation": "Deliver services monthly"}},
    {{"party": "Client", "obligation": "Pay within 30 days"}}
  ],
  "termination_clauses": [
    "Either party may terminate with 30 days written notice",
    "Immediate termination for material breach"
  ],
  "governing_law": "State of California",
  "signatures": [
    {{"name": "John Doe", "title": "CEO", "date": "2025-01-01", "signed": true}}
  ]
}}
```

If not a contract, return {{"is_contract": false}}"""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="contract_extraction",
            temperature=0.1,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default={})
        if data:
            if data.get("is_contract"):
                return ExtractedContract(
                    id=f"con_{uuid.uuid4().hex[:8]}",
                    contract_type=data.get("contract_type"),
                    parties=data.get("parties", []),
                    effective_date=data.get("effective_date"),
                    expiration_date=data.get("expiration_date"),
                    auto_renewal=data.get("auto_renewal", False),
                    renewal_terms=data.get("renewal_terms"),
                    key_terms=data.get("key_terms", []),
                    obligations=data.get("obligations", []),
                    termination_clauses=data.get("termination_clauses", []),
                    governing_law=data.get("governing_law"),
                    signatures=data.get("signatures", []),
                    confidence=0.8,
                )
    except Exception as e:
        logger.warning(f"Contract extraction failed: {e}")

    return None


# =============================================================================
# TABLE ENHANCEMENT
# =============================================================================

def enhance_table(table: Dict[str, Any], all_tables: List[Dict[str, Any]]) -> EnhancedExtractedTable:
    """Enhance a table with additional metadata and analysis."""
    headers = table.get("headers", [])
    rows = table.get("rows", [])

    # Infer data types
    data_types = []
    for col_idx in range(len(headers)):
        col_values = [row[col_idx] for row in rows if col_idx < len(row)]
        data_types.append(_infer_column_type(col_values))

    # Calculate statistics for numeric columns
    statistics = {}
    for col_idx, dtype in enumerate(data_types):
        if dtype == "numeric":
            values = []
            for row in rows:
                if col_idx < len(row):
                    try:
                        val = float(str(row[col_idx]).replace(",", "").replace("$", "").replace("%", ""))
                        values.append(val)
                    except (ValueError, TypeError):
                        pass

            if values:
                statistics[headers[col_idx]] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "count": len(values),
                }

    # Check for totals row
    has_totals = False
    if rows:
        last_row = rows[-1]
        if any("total" in str(cell).lower() for cell in last_row):
            has_totals = True

    return EnhancedExtractedTable(
        id=table.get("id", f"table_{uuid.uuid4().hex[:8]}"),
        title=table.get("title"),
        headers=headers,
        rows=rows,
        data_types=data_types,
        source_page=table.get("source_page"),
        source_sheet=table.get("source_sheet"),
        confidence=table.get("confidence", 0.9),
        row_count=len(rows),
        column_count=len(headers),
        has_totals_row=has_totals,
        has_header_row=True,
        statistics=statistics,
    )


def detect_table_relationships(tables: List[EnhancedExtractedTable]) -> List[TableRelationship]:
    """Detect relationships between tables (e.g., continuation across pages)."""
    relationships = []

    for i, table1 in enumerate(tables):
        for j, table2 in enumerate(tables):
            if i >= j:
                continue

            # Check for continuation (same headers)
            if table1.headers == table2.headers:
                # Check if on consecutive pages
                if (table1.source_page and table2.source_page and
                        abs(table1.source_page - table2.source_page) == 1):
                    relationships.append(TableRelationship(
                        table1_id=table1.id,
                        table2_id=table2.id,
                        relationship_type="continuation",
                        confidence=0.9,
                    ))
            # Check for related tables (shared columns)
            elif set(table1.headers) & set(table2.headers):
                shared = len(set(table1.headers) & set(table2.headers))
                total = len(set(table1.headers) | set(table2.headers))
                if shared / total > 0.3:
                    relationships.append(TableRelationship(
                        table1_id=table1.id,
                        table2_id=table2.id,
                        relationship_type="related",
                        confidence=shared / total,
                    ))

    return relationships


def stitch_continuation_tables(
    tables: List[EnhancedExtractedTable],
    relationships: List[TableRelationship]
) -> List[EnhancedExtractedTable]:
    """Merge tables that are continuations of each other."""
    continuations = {r.table1_id: r.table2_id for r in relationships if r.relationship_type == "continuation"}

    if not continuations:
        return tables

    merged_ids = set()
    result = []

    for table in tables:
        if table.id in merged_ids:
            continue

        # Find all continuations
        current_id = table.id
        all_rows = list(table.rows)

        while current_id in continuations:
            next_id = continuations[current_id]
            merged_ids.add(next_id)

            # Find the continuation table
            for t in tables:
                if t.id == next_id:
                    all_rows.extend(t.rows)
                    break

            current_id = next_id

        # Create merged table
        merged = EnhancedExtractedTable(
            id=table.id,
            title=table.title,
            headers=table.headers,
            rows=all_rows,
            data_types=table.data_types,
            source_page=table.source_page,
            confidence=table.confidence,
            row_count=len(all_rows),
            column_count=len(table.headers),
            has_totals_row=table.has_totals_row,
            has_header_row=True,
            statistics=table.statistics,
            related_tables=list(merged_ids) if merged_ids else [],
        )
        result.append(merged)

    return result


def _infer_column_type(values: List[Any]) -> str:
    """Infer the data type of a column."""
    if not values:
        return "text"

    numeric_count = 0
    date_count = 0
    total_valid = 0

    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',
        r'^\d{1,2}/\d{1,2}/\d{2,4}$',
        r'^\d{1,2}-\d{1,2}-\d{2,4}$',
    ]

    for value in values:
        value_str = str(value).strip()
        if not value_str:
            continue

        total_valid += 1

        # Check numeric
        try:
            cleaned = re.sub(r'[$,% ]', '', value_str)
            float(cleaned)
            numeric_count += 1
            continue
        except (ValueError, TypeError):
            pass

        # Check date
        for pattern in date_patterns:
            if re.match(pattern, value_str):
                date_count += 1
                break

    if total_valid == 0:
        return "text"

    if numeric_count / total_valid >= 0.7:
        return "numeric"
    if date_count / total_valid >= 0.7:
        return "datetime"

    return "text"


# =============================================================================
# MAIN EXTRACTION ORCHESTRATOR
# =============================================================================

class EnhancedExtractionService:
    """Orchestrates all intelligent extraction operations."""

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    def extract_all(
        self,
        text: str,
        raw_tables: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Perform all extraction operations.

        Uses regex for fast entity extraction + ONE consolidated LLM call
        for semantic extraction (entities, metrics) instead of 5 separate calls.
        """
        # Enhance tables (no LLM)
        enhanced_tables = [enhance_table(t, raw_tables) for t in raw_tables]

        # Detect relationships and stitch (no LLM)
        relationships = detect_table_relationships(enhanced_tables)
        stitched_tables = stitch_continuation_tables(enhanced_tables, relationships)

        # Fast regex-based entity extraction (no LLM)
        entities = extract_entities_regex(text)

        metrics: List[ExtractedMetric] = []
        forms: List[FormField] = []
        invoices: List[ExtractedInvoice] = []
        contracts: List[ExtractedContract] = []

        if self.use_llm:
            try:
                llm_result = self._extract_with_llm(text, stitched_tables)

                # Merge LLM entities with regex entities (dedup)
                entity_values = {e.value.lower() for e in entities}
                for ent in llm_result.get("entities", []):
                    if ent.value.lower() not in entity_values:
                        entities.append(ent)
                        entity_values.add(ent.value.lower())

                metrics = llm_result.get("metrics", [])
                forms = llm_result.get("forms", [])
                invoices = llm_result.get("invoices", [])
                contracts = llm_result.get("contracts", [])

            except Exception as e:
                logger.error("LLM extraction failed: %s", e, exc_info=True)
                raise RuntimeError(f"Intelligent extraction failed: {e}") from e

        return {
            "tables": stitched_tables,
            "table_relationships": relationships,
            "entities": entities,
            "metrics": metrics,
            "forms": forms,
            "invoices": invoices,
            "contracts": contracts,
        }

    def _extract_with_llm(
        self,
        text: str,
        tables: List[EnhancedExtractedTable],
    ) -> Dict[str, Any]:
        """
        Single consolidated LLM call for semantic extraction.

        Combines entity NER + metric extraction + document type detection.
        """
        table_context = ""
        for table in tables[:5]:
            table_context += f"- {table.title or table.id}: columns={', '.join(table.headers[:8])}"
            if table.rows:
                table_context += f", sample={table.rows[0][:6]}"
            table_context += "\n"
        table_context = table_context or "(no tables)"

        prompt = f"""Extract structured data from this document in ONE JSON response.

DOCUMENT TEXT:
{text[:8000]}

TABLES:
{table_context}

Return a JSON object:
{{
  "entities": [
    {{"type": "PERSON|ORGANIZATION|LOCATION|PRODUCT|DATE|MONEY|PERCENTAGE", "value": "...", "context": "surrounding text"}}
  ],
  "metrics": [
    {{
      "name": "Metric name",
      "value": 1500000,
      "raw_value": "$1.5M",
      "metric_type": "currency|percentage|count|ratio|duration|other",
      "currency": "USD",
      "period": "Q3 2025",
      "change": 15.5,
      "change_direction": "increase|decrease|stable",
      "context": "Brief context sentence",
      "importance": 0.9
    }}
  ],
  "document_type": "invoice|contract|form|report|letter|other"
}}

RULES:
- Extract ALL named entities (people, companies, locations, products)
- Extract ALL key metrics, KPIs, and numerical data with context
- Be thorough - don't miss important data points
- Return ONLY valid JSON"""

        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="consolidated_extraction",
            temperature=0.1,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default={})

        result: Dict[str, Any] = {"entities": [], "metrics": [], "forms": [],
                                   "invoices": [], "contracts": []}

        # Parse entities
        for item in data.get("entities", []):
            if isinstance(item, dict):
                entity_type = str(item.get("type", "")).upper()
                try:
                    etype = EntityType[entity_type]
                except KeyError:
                    etype = EntityType.CUSTOM
                result["entities"].append(ExtractedEntity(
                    id=f"ent_{uuid.uuid4().hex[:8]}",
                    type=etype,
                    value=item.get("value", ""),
                    confidence=0.85,
                    context=item.get("context"),
                ))

        # Parse metrics
        for item in data.get("metrics", []):
            if isinstance(item, dict):
                mtype_map = {
                    "currency": MetricType.CURRENCY, "percentage": MetricType.PERCENTAGE,
                    "count": MetricType.COUNT, "ratio": MetricType.RATIO,
                    "duration": MetricType.DURATION, "quantity": MetricType.QUANTITY,
                    "score": MetricType.SCORE, "rate": MetricType.RATE,
                }
                raw_val = item.get("value")
                if raw_val is None:
                    raw_val = item.get("raw_value", "0")
                result["metrics"].append(ExtractedMetric(
                    id=f"met_{uuid.uuid4().hex[:8]}",
                    name=item.get("name", ""),
                    value=raw_val if raw_val is not None else "0",
                    raw_value=str(item.get("raw_value", "")),
                    metric_type=mtype_map.get(str(item.get("metric_type", "count")).lower(), MetricType.COUNT),
                    currency=item.get("currency"),
                    period=item.get("period"),
                    change=item.get("change"),
                    change_direction=item.get("change_direction"),
                    context=item.get("context"),
                    importance_score=float(item.get("importance", 0.5)),
                ))

        return result
