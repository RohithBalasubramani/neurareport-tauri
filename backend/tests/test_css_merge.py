from backend.app.services.templates.css_merge import (
    merge_css_into_html,
    replace_table_colgroup,
)


def test_merge_css_appends_rules_to_existing_style():
    html = "<html><head><style>.foo{color:red;}</style></head><body></body></html>"
    result = merge_css_into_html(html, ".bar{color:blue;}")
    expected = "<html><head><style>.foo{color:red;}\n" ".bar{color:blue;}\n" "</style></head><body></body></html>"
    assert result == expected


def test_merge_css_inserts_new_style_block_when_missing():
    html = "<html><head></head><body></body></html>"
    result = merge_css_into_html(html, "<style>.foo{}</style>")
    expected = "<html><head><style>\n" ".foo{}\n" "</style>\n" "</head><body></body></html>"
    assert result == expected


def test_replace_table_colgroup_swaps_existing_definition():
    html = "<table id='tbl-1'><colgroup><col style='width:50%'></colgroup><tbody></tbody></table>"
    result = replace_table_colgroup(
        html,
        "tbl-1",
        "<colgroup><col style='width:40%'><col style='width:60%'></colgroup>",
    )
    assert (
        result
        == "<table id='tbl-1'><colgroup><col style='width:40%'><col style='width:60%'></colgroup><tbody></tbody></table>"
    )


def test_replace_table_colgroup_inserts_when_missing():
    html = "<table id='tbl-2'><tbody><tr></tr></tbody></table>"
    result = replace_table_colgroup(html, "tbl-2", "<colgroup><col style='width:50%'></colgroup>")
    assert result == "<table id='tbl-2'><colgroup><col style='width:50%'></colgroup>\n<tbody><tr></tr></tbody></table>"
