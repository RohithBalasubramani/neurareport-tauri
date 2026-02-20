# mypy: ignore-errors
"""
Text-to-SQL Generation Module.

Implements SQLCoder-style prompting for accurate SQL generation:
- Schema-aware prompting
- Query decomposition for complex questions
- DuckDB and SQLite dialect support
- Validation and error correction
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .client import LLMClient, get_llm_client
from .config import LLMConfig, LLMProvider

logger = logging.getLogger("neura.llm.text_to_sql")


@dataclass
class TableSchema:
    """Schema information for a database table."""
    name: str
    columns: List[Dict[str, str]]  # [{"name": "col", "type": "TEXT", "description": "..."}]
    primary_key: Optional[str] = None
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)
    sample_values: Dict[str, List[Any]] = field(default_factory=dict)
    description: Optional[str] = None


@dataclass
class SQLGenerationResult:
    """Result of SQL generation."""
    sql: str
    explanation: str
    confidence: float
    dialect: str
    warnings: List[str] = field(default_factory=list)
    raw_response: str = ""


class TextToSQL:
    """
    Text-to-SQL generation using LLM with SQLCoder-style prompting.

    Supports:
    - Natural language to SQL conversion
    - Schema-aware generation
    - Multi-table joins
    - Aggregations and grouping
    - DuckDB and SQLite dialects
    """

    # Recommended models for SQL generation per provider
    SQL_MODELS = {
        LLMProvider.CLAUDE_CODE: "sonnet",  # Claude Code CLI default
    }

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        dialect: str = "duckdb",
        model: Optional[str] = None,
    ):
        self.client = client or get_llm_client()
        self.dialect = dialect.lower()
        self._model = model
        self._schemas: Dict[str, TableSchema] = {}

    @property
    def model(self) -> str:
        """Get the model for SQL generation."""
        if self._model:
            return self._model
        provider = self.client.config.provider
        return self.SQL_MODELS.get(provider, self.client.config.model)

    def add_table_schema(self, schema: TableSchema) -> None:
        """Add a table schema for context."""
        self._schemas[schema.name] = schema

    def add_schemas_from_catalog(self, catalog: Dict[str, Any]) -> None:
        """Add schemas from a database catalog dictionary."""
        for table_name, table_info in catalog.items():
            columns = []
            for col in table_info.get("columns", []):
                if isinstance(col, dict):
                    columns.append({
                        "name": col.get("name", ""),
                        "type": col.get("type", "TEXT"),
                        "description": col.get("description", ""),
                    })
                elif isinstance(col, str):
                    columns.append({"name": col, "type": "TEXT", "description": ""})

            schema = TableSchema(
                name=table_name,
                columns=columns,
                primary_key=table_info.get("primary_key"),
                foreign_keys=table_info.get("foreign_keys", []),
                sample_values=table_info.get("sample_values", {}),
                description=table_info.get("description"),
            )
            self._schemas[table_name] = schema

    def generate_sql(
        self,
        question: str,
        tables: Optional[List[str]] = None,
        context: Optional[str] = None,
    ) -> SQLGenerationResult:
        """
        Generate SQL from a natural language question.

        Args:
            question: Natural language question
            tables: Optional list of table names to use (uses all if not specified)
            context: Optional additional context

        Returns:
            SQLGenerationResult with generated SQL
        """
        # Build the prompt
        prompt = self._build_sqlcoder_prompt(question, tables, context)

        # Generate SQL
        response = self.client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            description="text_to_sql",
            temperature=0.0,  # Deterministic for SQL
        )

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_sql_response(raw_content)

    def generate_sql_with_decomposition(
        self,
        question: str,
        tables: Optional[List[str]] = None,
    ) -> SQLGenerationResult:
        """
        Generate SQL using query decomposition for complex questions.

        This approach breaks down complex questions into simpler sub-queries
        before combining them.
        """
        # First, analyze the question complexity
        analysis_prompt = f"""Analyze this question and determine if it needs to be decomposed:

Question: {question}

Respond in JSON format:
```json
{{
  "is_complex": true/false,
  "sub_questions": ["sub-question 1", "sub-question 2"],
  "combination_strategy": "join|union|subquery|none"
}}
```"""

        analysis_response = self.client.complete(
            messages=[{"role": "user", "content": analysis_prompt}],
            model=self.model,
            description="sql_decomposition_analysis",
            temperature=0.0,
        )

        analysis = self._parse_json_response(
            analysis_response["choices"][0]["message"]["content"],
            {"is_complex": False, "sub_questions": [], "combination_strategy": "none"}
        )

        if not analysis.get("is_complex") or not analysis.get("sub_questions"):
            # Simple question, generate directly
            return self.generate_sql(question, tables)

        # Generate SQL for each sub-question
        sub_queries = []
        for sub_q in analysis["sub_questions"]:
            result = self.generate_sql(sub_q, tables)
            sub_queries.append({
                "question": sub_q,
                "sql": result.sql,
            })

        # Combine sub-queries
        combination_prompt = f"""Combine these sub-queries to answer the original question.

Original Question: {question}

Sub-queries:
{json.dumps(sub_queries, indent=2)}

Combination Strategy: {analysis.get('combination_strategy', 'join')}

Generate the final combined SQL query for {self.dialect.upper()}.
Return ONLY the SQL, no explanation."""

        final_response = self.client.complete(
            messages=[{"role": "user", "content": combination_prompt}],
            model=self.model,
            description="sql_combination",
            temperature=0.0,
        )

        final_sql = self._extract_sql(final_response["choices"][0]["message"]["content"])

        return SQLGenerationResult(
            sql=final_sql,
            explanation=f"Combined from {len(sub_queries)} sub-queries",
            confidence=0.8,
            dialect=self.dialect,
            warnings=["Query was decomposed and combined"],
            raw_response=final_response["choices"][0]["message"]["content"],
        )

    def validate_and_fix_sql(
        self,
        sql: str,
        error_message: Optional[str] = None,
    ) -> SQLGenerationResult:
        """
        Validate SQL and attempt to fix any errors.

        Args:
            sql: The SQL to validate
            error_message: Optional error message from previous execution

        Returns:
            SQLGenerationResult with corrected SQL
        """
        schema_context = self._build_schema_context()

        prompt = f"""Review and fix this SQL query.

Schema:
{schema_context}

Original SQL:
```sql
{sql}
```

{f"Error encountered: {error_message}" if error_message else ""}

Tasks:
1. Check for syntax errors
2. Verify table and column names match the schema
3. Fix any issues found
4. Ensure the query is valid {self.dialect.upper()}

Return the corrected SQL in a code block, followed by an explanation of changes made."""

        response = self.client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            description="sql_validation",
            temperature=0.0,
        )

        raw_content = response["choices"][0]["message"]["content"]
        result = self._parse_sql_response(raw_content)

        if error_message:
            result.warnings.append(f"Fixed error: {error_message}")

        return result

    def explain_sql(self, sql: str) -> str:
        """
        Generate a natural language explanation of SQL.

        Args:
            sql: The SQL to explain

        Returns:
            Human-readable explanation
        """
        prompt = f"""Explain this SQL query in simple terms:

```sql
{sql}
```

Provide a clear, non-technical explanation of:
1. What data is being retrieved
2. What filters/conditions are applied
3. How the results are organized
4. Any calculations or aggregations performed"""

        response = self.client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            description="sql_explanation",
            temperature=0.3,
        )

        return response["choices"][0]["message"]["content"]

    def _build_sqlcoder_prompt(
        self,
        question: str,
        tables: Optional[List[str]],
        context: Optional[str],
    ) -> str:
        """Build a SQLCoder-style prompt."""
        schema_context = self._build_schema_context(tables)

        # SQLCoder-style prompt structure
        prompt = f"""### Task
Generate a SQL query to answer [QUESTION]{question}[/QUESTION]

### Database Schema
The query will run on a database with the following schema:
{schema_context}

### SQL Dialect
Use {self.dialect.upper()} syntax.

"""
        if context:
            prompt += f"""### Additional Context
{context}

"""

        prompt += """### Guidelines
- Use proper table aliases
- Handle NULL values appropriately
- Use appropriate JOIN types
- Include only necessary columns
- Use appropriate aggregation functions
- Ensure the query is efficient

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{question}[/QUESTION]:
```sql
"""
        return prompt

    def _build_schema_context(
        self,
        tables: Optional[List[str]] = None,
    ) -> str:
        """Build schema context string for the prompt."""
        if not self._schemas:
            return "No schema information available."

        schemas_to_use = (
            {name: self._schemas[name] for name in tables if name in self._schemas}
            if tables
            else self._schemas
        )

        context_parts = []

        for table_name, schema in schemas_to_use.items():
            # Format CREATE TABLE statement
            columns_def = []
            for col in schema.columns:
                col_def = f"  {col['name']} {col.get('type', 'TEXT')}"
                if col.get('description'):
                    col_def += f" -- {col['description']}"
                columns_def.append(col_def)

            table_def = f"CREATE TABLE {table_name} (\n"
            table_def += ",\n".join(columns_def)

            if schema.primary_key:
                table_def += f",\n  PRIMARY KEY ({schema.primary_key})"

            for fk in schema.foreign_keys:
                table_def += f",\n  FOREIGN KEY ({fk.get('column')}) REFERENCES {fk.get('references')}"

            table_def += "\n);"

            if schema.description:
                table_def = f"-- {schema.description}\n{table_def}"

            context_parts.append(table_def)

            # Add sample values if available
            if schema.sample_values:
                samples = []
                for col, values in schema.sample_values.items():
                    if values:
                        samples.append(f"  {col}: {', '.join(str(v) for v in values[:3])}")
                if samples:
                    context_parts.append(f"-- Sample values for {table_name}:\n" + "\n".join(samples))

        return "\n\n".join(context_parts)

    def _parse_sql_response(self, raw_content: str) -> SQLGenerationResult:
        """Parse the LLM response to extract SQL."""
        sql = self._extract_sql(raw_content)

        # Extract explanation (text after the SQL block)
        explanation = ""
        sql_end = raw_content.rfind("```")
        if sql_end != -1:
            explanation = raw_content[sql_end + 3:].strip()

        # Calculate confidence based on response quality
        confidence = 0.9
        warnings = []

        if not sql:
            confidence = 0.0
            warnings.append("No SQL found in response")
        elif "SELECT *" in sql.upper():
            confidence -= 0.1
            warnings.append("Using SELECT * may be inefficient")
        if "-- TODO" in sql or "-- FIXME" in sql:
            confidence -= 0.2
            warnings.append("Query contains TODO/FIXME comments")

        return SQLGenerationResult(
            sql=sql,
            explanation=explanation,
            confidence=min(max(confidence, 0.0), 1.0),
            dialect=self.dialect,
            warnings=warnings,
            raw_response=raw_content,
        )

    def _extract_sql(self, content: str) -> str:
        """Extract SQL from LLM response."""
        # Try to find SQL in code blocks
        sql_match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", content, re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()

        # Try to find SELECT/INSERT/UPDATE/DELETE statement
        statement_match = re.search(
            r"(SELECT|INSERT|UPDATE|DELETE|WITH|CREATE|ALTER|DROP)\b[\s\S]+?(?:;|$)",
            content,
            re.IGNORECASE
        )
        if statement_match:
            return statement_match.group(0).strip().rstrip(";") + ";"

        return content.strip()

    def _parse_json_response(
        self,
        raw_content: str,
        default: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_content)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            json_str = raw_content.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return default


# Convenience functions

def get_text_to_sql(dialect: str = "duckdb") -> TextToSQL:
    """Get a TextToSQL instance."""
    return TextToSQL(dialect=dialect)


def generate_sql(
    question: str,
    schema: Dict[str, Any],
    dialect: str = "duckdb",
) -> str:
    """
    Quick function to generate SQL from a question.

    Args:
        question: Natural language question
        schema: Database schema dictionary
        dialect: SQL dialect (duckdb, sqlite)

    Returns:
        Generated SQL query
    """
    t2sql = TextToSQL(dialect=dialect)
    t2sql.add_schemas_from_catalog(schema)
    result = t2sql.generate_sql(question)
    return result.sql
