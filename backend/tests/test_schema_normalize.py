from backend.app.services.templates.TemplateVerify import (
    normalize_schema_for_initial_html,
)


def test_normalize_preserves_legacy_shape():
    legacy = {
        "scalars": {"name": "Name", "date": "Date"},
        "blocks": {"rows": ["row_token"], "headers": ["Row Token"]},
        "notes": "legacy schema",
        "page_tokens_protect": ["page_no"],
    }

    normalized = normalize_schema_for_initial_html(legacy)

    assert normalized == legacy


def test_normalize_handles_enhanced_schema_metadata():
    enhanced = {
        "scalars": {
            "name": {"label": "Name Label", "token": "name", "bbox_mm": [0, 0, 10, 5]},
            "code": {"label": "Code Label", "type": "id"},
        },
        "blocks": {
            "rows": [
                {"token": "item_no"},
                {"name": "qty"},
            ],
            "headers": ["Item No", "Qty"],
            "repeat_regions": [{"kind": "table", "selector": "batch-block"}],
        },
        "notes": "enhanced schema",
        "page_tokens_protect": ["page_no", "page_total"],
    }

    normalized = normalize_schema_for_initial_html(enhanced)

    assert normalized == {
        "scalars": {"name": "Name Label", "code": "Code Label"},
        "blocks": {
            "rows": ["item_no", "qty"],
            "headers": ["Item No", "Qty"],
            "repeat_regions": [{"kind": "table", "selector": "batch-block"}],
        },
        "notes": "enhanced schema",
        "page_tokens_protect": ["page_no", "page_total"],
    }
