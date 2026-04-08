"""CrewAI-style role-based workflows.

Each crew defines a sequential pipeline of specialised agents that collaborate
via the internal Crew orchestrator (``backend.app.services.llm.agents.Crew``).
"""
from __future__ import annotations

from .report_crew import ReportCrew
from .content_crew import ContentCrew
from .analysis_crew import AnalysisCrew

__all__ = [
    "ReportCrew",
    "ContentCrew",
    "AnalysisCrew",
]
