import pytest

from backend.app.services.mapping.CorrectionsPreview import (
    CorrectionsPreviewError,
    _ensure_invariants,
)

ORIGINAL_HTML = """<!doctype html>
<html>
  <body>
    <h1>{report_title}</h1>
    <!--BEGIN:BLOCK_REPEAT line-->
    <table data-region="rows">
      <tbody>
        <tr><td>{row_value}</td></tr>
      </tbody>
    </table>
    <!--END:BLOCK_REPEAT line-->
  </body>
</html>"""


def test_invariants_allow_constant_removal():
    final_html = ORIGINAL_HTML.replace("{report_title}", "Consumption Report")
    _ensure_invariants(
        original_html=ORIGINAL_HTML,
        final_html=final_html,
        additional_constants=[{"token": "report_title", "value": "Consumption Report"}],
        sample_values={"row_value": "42"},
    )


def test_invariants_fail_token_rename():
    final_html = ORIGINAL_HTML.replace("{report_title}", "{report_title_v2}")
    with pytest.raises(CorrectionsPreviewError):
        _ensure_invariants(
            original_html=ORIGINAL_HTML,
            final_html=final_html,
            additional_constants=[],
            sample_values={},
        )


def test_invariants_fail_sample_leak():
    final_html = ORIGINAL_HTML.replace("{report_title}", "Consumption Report").replace("{row_value}", "42")
    with pytest.raises(CorrectionsPreviewError):
        _ensure_invariants(
            original_html=ORIGINAL_HTML,
            final_html=final_html,
            additional_constants=[{"token": "report_title", "value": "Consumption Report"}],
            sample_values={"row_value": "42"},
        )
