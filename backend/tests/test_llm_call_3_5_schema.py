import pytest

from backend.app.services.utils.validation import (
    SchemaValidationError,
    validate_llm_call_3_5,
)


def _sample_payload():
    return {
        "final_template_html": "<html><body><h1>{report_title}</h1></body></html>",
        "page_summary": "Header titled {report_title} followed by a table of {row_value}.",
    }


def test_validate_llm_call_3_5_schema_happy_path():
    payload = _sample_payload()
    validate_llm_call_3_5(payload)


def test_validate_llm_call_3_5_schema_missing_required():
    payload = _sample_payload()
    payload.pop("final_template_html")
    with pytest.raises(SchemaValidationError):
        validate_llm_call_3_5(payload)
