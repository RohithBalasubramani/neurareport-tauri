import re

STYLE_RE = re.compile(r"(?is)<style\b[^>]*>(.*?)</style>")
HEAD_CLOSE_RE = re.compile(r"(?i)</head>")


def _extract_css(css_patch: str) -> str:
    match = STYLE_RE.search(css_patch)
    if match:
        return match.group(1).strip()
    return css_patch.strip()


def merge_css_into_html(html: str, css_patch: str) -> str:
    """Merge the provided CSS patch into the first <style> block (append to override)."""
    rules = _extract_css(css_patch)
    if not rules:
        return html

    match = STYLE_RE.search(html)
    if match:
        start, end = match.span(1)
        existing = match.group(1).rstrip()
        if existing:
            merged = f"{existing}\n{rules}\n"
        else:
            merged = f"{rules}\n"
        return html[:start] + merged + html[end:]

    injection = f"<style>\n{rules}\n</style>\n"
    head_match = HEAD_CLOSE_RE.search(html)
    if head_match:
        idx = head_match.start()
        return html[:idx] + injection + html[idx:]
    return injection + html


def replace_table_colgroup(html: str, table_id: str, new_colgroup_html: str) -> str:
    """Replace or insert a <colgroup> for the table with the given id."""
    snippet = new_colgroup_html.strip()
    if not table_id or not snippet:
        return html
    if "<colgroup" not in snippet.lower():
        return html

    table_pattern = re.compile(
        rf'(<table\b[^>]*\bid=["\']{re.escape(table_id)}["\'][^>]*>)(?P<body>.*?)(</table>)',
        re.I | re.S,
    )
    match = table_pattern.search(html)
    if not match:
        return html

    start_tag = match.group(1)
    body = match.group("body")
    end_tag = match.group(3)

    colgroup_pattern = re.compile(r"<colgroup\b[^>]*>.*?</colgroup>", re.I | re.S)
    if colgroup_pattern.search(body):
        new_body = colgroup_pattern.sub(snippet, body, count=1)
    else:
        prepend = snippet if snippet.endswith("\n") else snippet + "\n"
        new_body = prepend + body

    new_table = start_tag + new_body + end_tag
    return html[: match.start()] + new_table + html[match.end() :]
