"""
Data-mapping team: SchemaAnalyst + MappingSpecialist + Validator.

Analyses source schemas, creates field mappings to template placeholders, and
validates the mappings for correctness.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ..llm.agents import AgentConfig, Task
from ..llm.client import LLMClient, get_llm_client
from .base_team import BaseTeam, TeamConfig

logger = logging.getLogger("neura.teams.mapping")


class MappingTeam(BaseTeam):
    """Three-agent team for data-to-template mapping.

    Pipeline::

        SchemaAnalyst  ->  MappingSpecialist  ->  Validator
        (analyse)          (create mappings)       (validate)
    """

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        *,
        max_rounds: int = 10,
        timeout: float = 60.0,
        use_autogen: bool = True,
        verbose: bool = False,
    ) -> None:
        config = TeamConfig(
            name="mapping",
            max_rounds=max_rounds,
            timeout=timeout,
            use_autogen=use_autogen,
            verbose=verbose,
        )
        super().__init__(config, client)

    # ------------------------------------------------------------------
    # Agent definitions
    # ------------------------------------------------------------------

    def _define_agents(self) -> List[AgentConfig]:
        return [
            AgentConfig(
                role="schema_analyst",
                goal=(
                    "Analyse source data schemas to understand field types, "
                    "relationships, cardinality, and semantic meaning."
                ),
                backstory=(
                    "You are a data architect who has designed hundreds of schemas "
                    "across financial, healthcare, and enterprise domains.  You can "
                    "quickly identify primary keys, foreign-key relationships, data "
                    "types, and the business meaning behind cryptic column names."
                ),
                temperature=0.2,
            ),
            AgentConfig(
                role="mapping_specialist",
                goal=(
                    "Create precise field-level mappings between source data and "
                    "template placeholders, including any transformations needed."
                ),
                backstory=(
                    "You are an integration engineer specialising in ETL and data "
                    "mapping.  You translate between heterogeneous schemas every day, "
                    "handling type coercions, concatenations, look-up tables, and "
                    "conditional logic with ease."
                ),
                temperature=0.3,
            ),
            AgentConfig(
                role="mapping_validator",
                goal=(
                    "Validate proposed mappings for completeness, type safety, and "
                    "semantic correctness.  Flag any unmapped required fields."
                ),
                backstory=(
                    "You are a QA engineer obsessed with data quality.  You "
                    "systematically verify every mapping against the target schema, "
                    "run edge-case scenarios in your head, and never let an incorrect "
                    "or missing mapping slip through."
                ),
                temperature=0.1,
            ),
        ]

    # ------------------------------------------------------------------
    # Task definitions
    # ------------------------------------------------------------------

    def _define_tasks(self, inputs: Dict[str, Any]) -> List[Task]:
        source_schema = inputs.get("source_schema", {})
        template_fields = inputs.get("template_fields", [])
        extra_context = inputs.get("context", "")

        source_repr = (
            json.dumps(source_schema, indent=2)
            if isinstance(source_schema, (dict, list))
            else str(source_schema)
        )
        template_repr = (
            json.dumps(template_fields, indent=2)
            if isinstance(template_fields, (dict, list))
            else str(template_fields)
        )

        analyse_desc = (
            "Analyse the following source schema and describe each field's type, "
            "semantic meaning, and relationships.\n\n"
            f"SOURCE SCHEMA:\n{source_repr}\n\n"
            f"TEMPLATE FIELDS:\n{template_repr}"
        )

        map_desc = (
            "Using the schema analysis, create a complete set of field mappings "
            "from source to template.  For each template field, specify the source "
            "field(s), any transformation logic, and a confidence score."
        )

        validate_desc = (
            "Validate the proposed mappings.  Check for:\n"
            "- Unmapped required template fields\n"
            "- Type mismatches\n"
            "- Ambiguous or incorrect semantic matches\n"
            "Produce a validation report with pass/fail per mapping."
        )

        return [
            Task(
                description=analyse_desc,
                agent_role="schema_analyst",
                expected_output=(
                    "Structured schema analysis with field descriptions, types, "
                    "and relationships."
                ),
                context={"extra_context": extra_context} if extra_context else {},
            ),
            Task(
                description=map_desc,
                agent_role="mapping_specialist",
                expected_output=(
                    "JSON mapping specification: list of "
                    "{template_field, source_field, transformation, confidence}."
                ),
                dependencies=[analyse_desc[:50]],
            ),
            Task(
                description=validate_desc,
                agent_role="mapping_validator",
                expected_output=(
                    "Validation report with pass/fail per mapping and overall "
                    "completeness score."
                ),
                dependencies=[map_desc[:50]],
            ),
        ]


# ------------------------------------------------------------------
# Convenience function
# ------------------------------------------------------------------


def map_data_to_template(
    source_schema: Any,
    template_fields: Any,
    context: Optional[str] = None,
    client: Optional[LLMClient] = None,
) -> dict:
    """Map source data fields to template placeholders.

    Args:
        source_schema: Source schema (dict, list, or string description).
        template_fields: Target template fields.
        context: Optional extra context about the domain.
        client: Optional pre-configured LLM client.

    Returns:
        Dict with ``results``, ``errors``, and ``execution_summary`` keys.
    """
    team = MappingTeam(client=client)
    return team.run({
        "source_schema": source_schema,
        "template_fields": template_fields,
        "context": context or "",
    })
