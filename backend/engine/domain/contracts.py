"""Contract domain entities.

A Contract defines how data from a database maps to placeholders in a template.
Contracts are the central artifact that enables report generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TokenType(str, Enum):
    """Types of tokens in a contract."""

    SCALAR = "scalar"
    ROW = "row"
    TOTAL = "total"


@dataclass(frozen=True)
class Token:
    """A single token/placeholder in a contract."""

    name: str
    token_type: TokenType
    expression: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Token name cannot be empty")


@dataclass(frozen=True)
class TokenSet:
    """Collection of tokens organized by type."""

    scalars: List[str] = field(default_factory=list)
    row_tokens: List[str] = field(default_factory=list)
    totals: List[str] = field(default_factory=list)

    def all_tokens(self) -> List[str]:
        return [*self.scalars, *self.row_tokens, *self.totals]

    def __contains__(self, token: str) -> bool:
        return token in self.scalars or token in self.row_tokens or token in self.totals


@dataclass(frozen=True)
class Mapping:
    """Mapping from token name to SQL expression."""

    token: str
    expression: str
    source_table: Optional[str] = None
    source_column: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.token.strip():
            raise ValueError("Mapping token cannot be empty")
        if not self.expression.strip():
            raise ValueError(f"Mapping expression for '{self.token}' cannot be empty")


@dataclass(frozen=True)
class ReshapeColumn:
    """A column in a reshape rule."""

    alias: str
    sources: List[str]


@dataclass(frozen=True)
class ReshapeRule:
    """Rule for reshaping/transforming data before rendering."""

    purpose: str
    strategy: str
    columns: List[ReshapeColumn]
    order_by: List[str] = field(default_factory=list)
    filters: Optional[str] = None
    group_by: Optional[List[str]] = None
    explain: Optional[str] = None


@dataclass(frozen=True)
class JoinSpec:
    """Specification for joining tables."""

    parent_table: str
    parent_key: str
    child_table: str
    child_key: str

    def is_valid(self) -> bool:
        return bool(self.parent_table and self.parent_key)


@dataclass(frozen=True)
class OrderSpec:
    """Ordering specification for rows."""

    rows: List[str] = field(default_factory=list)


@dataclass
class Contract:
    """Complete contract for report generation.

    A contract contains:
    - Token definitions (scalars, row tokens, totals)
    - Mappings from tokens to SQL expressions
    - Reshape rules for data transformation
    - Join specifications for multi-table queries
    - Date column mappings for range filters
    - Ordering specifications
    """

    contract_id: str
    template_id: str
    tokens: TokenSet
    mappings: Dict[str, str]
    reshape_rules: List[ReshapeRule] = field(default_factory=list)
    join: Optional[JoinSpec] = None
    date_columns: Dict[str, str] = field(default_factory=dict)
    order_by: OrderSpec = field(default_factory=OrderSpec)
    row_order: List[str] = field(default_factory=lambda: ["ROWID"])
    literals: Dict[str, Any] = field(default_factory=dict)
    totals_math: Dict[str, str] = field(default_factory=dict)
    row_computed: Dict[str, str] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    version: str = "v2"

    # Compatibility aliases
    @property
    def header_tokens(self) -> List[str]:
        return list(self.tokens.scalars)

    @property
    def row_tokens(self) -> List[str]:
        return list(self.tokens.row_tokens)

    @property
    def totals(self) -> Dict[str, str]:
        return {tok: self.mappings.get(tok, "") for tok in self.tokens.totals}

    def get_mapping(self, token: str) -> Optional[str]:
        return self.mappings.get(token)

    def validate(self) -> List[str]:
        """Validate contract and return list of issues."""
        issues = []

        # Check all tokens have mappings
        for token in self.tokens.all_tokens():
            if token not in self.mappings:
                issues.append(f"Token '{token}' has no mapping")

        # Check reshape rules have valid columns
        for rule in self.reshape_rules:
            if not rule.columns:
                issues.append(f"Reshape rule '{rule.purpose}' has no columns")

        # Check join validity if present
        if self.join and not self.join.is_valid():
            issues.append("Join specification is incomplete")

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for persistence."""
        return {
            "contract_id": self.contract_id,
            "template_id": self.template_id,
            "tokens": {
                "scalars": list(self.tokens.scalars),
                "row_tokens": list(self.tokens.row_tokens),
                "totals": list(self.tokens.totals),
            },
            "mapping": self.mappings,
            "reshape_rules": [
                {
                    "purpose": r.purpose,
                    "strategy": r.strategy,
                    "columns": [{"as": c.alias, "from": c.sources} for c in r.columns],
                    "order_by": r.order_by,
                    "filters": r.filters,
                    "group_by": r.group_by,
                    "explain": r.explain,
                }
                for r in self.reshape_rules
            ],
            "join": {
                "parent_table": self.join.parent_table,
                "parent_key": self.join.parent_key,
                "child_table": self.join.child_table,
                "child_key": self.join.child_key,
            }
            if self.join
            else None,
            "date_columns": dict(self.date_columns),
            "order_by": {"rows": list(self.order_by.rows)},
            "row_order": list(self.row_order),
            "literals": self.literals,
            "totals_math": self.totals_math,
            "row_computed": self.row_computed,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], template_id: str) -> Contract:
        """Deserialize from dict."""
        tokens_data = data.get("tokens", {})
        tokens = TokenSet(
            scalars=list(tokens_data.get("scalars", [])),
            row_tokens=list(tokens_data.get("row_tokens", [])),
            totals=list(tokens_data.get("totals", [])),
        )

        reshape_rules = []
        for rule_data in data.get("reshape_rules", []):
            columns = [
                ReshapeColumn(alias=c.get("as", ""), sources=c.get("from", []))
                for c in rule_data.get("columns", [])
            ]
            reshape_rules.append(
                ReshapeRule(
                    purpose=rule_data.get("purpose", ""),
                    strategy=rule_data.get("strategy", "SELECT"),
                    columns=columns,
                    order_by=rule_data.get("order_by", []),
                    filters=rule_data.get("filters"),
                    group_by=rule_data.get("group_by"),
                    explain=rule_data.get("explain"),
                )
            )

        join_data = data.get("join")
        join = None
        if join_data and isinstance(join_data, dict):
            join = JoinSpec(
                parent_table=join_data.get("parent_table", ""),
                parent_key=join_data.get("parent_key", ""),
                child_table=join_data.get("child_table", ""),
                child_key=join_data.get("child_key", ""),
            )

        order_data = data.get("order_by", {})
        order_by = OrderSpec(
            rows=order_data.get("rows", []) if isinstance(order_data, dict) else []
        )
        date_columns_raw = data.get("date_columns", {})
        date_columns = (
            {str(k): str(v) for k, v in date_columns_raw.items()}
            if isinstance(date_columns_raw, dict)
            else {}
        )

        return cls(
            contract_id=data.get("contract_id", f"contract-{template_id}"),
            template_id=template_id,
            tokens=tokens,
            mappings=dict(data.get("mapping", {})),
            reshape_rules=reshape_rules,
            join=join,
            date_columns=date_columns,
            order_by=order_by,
            row_order=list(data.get("row_order", ["ROWID"])),
            literals=dict(data.get("literals", {})),
            totals_math=dict(data.get("totals_math", {})),
            row_computed=dict(data.get("row_computed", {})),
            version=data.get("version", "v2"),
        )
