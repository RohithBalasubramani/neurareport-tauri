import os


from backend.app.services.utils.html import sanitize_html  # noqa: E402


def test_sanitizer_strips_disallowed_tags():
    html = '<div><script>alert("x")</script><span onclick="evil()">ok</span></div>'
    sanitized = sanitize_html(html)
    assert "<script" not in sanitized
    assert "onclick" not in sanitized
    assert sanitized.count("<div>") == 1
    assert "</div>" in sanitized


def test_sanitizer_preserves_allowed_attributes():
    html = '<table style="width:100%"><tr><td data-name="val">x</td></tr></table>'
    sanitized = sanitize_html(html)
    assert 'style="width:100%"' in sanitized
    assert 'data-name="val"' in sanitized
    assert "<table" in sanitized and "</table>" in sanitized
