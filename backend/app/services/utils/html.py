from __future__ import annotations

import re
from typing import Dict, List

import bleach
from bleach.css_sanitizer import CSSSanitizer

ALLOWED_TAGS = {
    "html",
    "head",
    "body",
    "meta",
    "title",
    "link",
    "style",
    "div",
    "span",
    "section",
    "article",
    "header",
    "footer",
    "main",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "th",
    "td",
    "colgroup",
    "col",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "br",
    "hr",
    "img",
    "canvas",
    "svg",
}

_REPEAT_COMMENT_RE = re.compile(r"^\s*(BEGIN:BLOCK_REPEAT\b.*|END:BLOCK_REPEAT\b.*)\s*$", re.IGNORECASE)

ALLOWED_ATTRS = {
    "*": {
        "class",
        "style",
        "id",
        "colspan",
        "rowspan",
        "align",
        "valign",
        "width",
        "height",
        "data-title",
        "data-index",
        "data-name",
        "data-value",
        "data-label",
    },
    "img": {"src", "alt"},
    "meta": {"charset"},
    "link": {"rel", "href"},
    "svg": {"viewbox", "xmlns"},
    "canvas": {"width", "height"},
}

_CSS_SANITIZER = CSSSanitizer()
_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
_STYLE_ATTR_RE = re.compile(r'style="([^"]*?)"')

# Matches CSS rules that apply position:fixed to footer-like selectors.
# Rewrites them to use normal document flow to prevent overlap with content.
_FIXED_FOOTER_RE = re.compile(
    r"(\.footer[-\w]*|#report-footer|footer)\s*\{([^}]*?)position\s*:\s*fixed\b([^}]*?)\}",
    re.IGNORECASE | re.DOTALL,
)
_FIXED_POS_PROPS_RE = re.compile(
    r"\b(bottom|left|right)\s*:\s*[^;]+;?",
    re.IGNORECASE,
)


def _bleach_attributes() -> Dict[str, List[str]]:
    attrs: Dict[str, List[str]] = {}
    for tag, allowed in ALLOWED_ATTRS.items():
        attrs[tag] = sorted(allowed)
    return attrs


def _filter_comments(html: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        data = match.group(1)
        if _REPEAT_COMMENT_RE.match(data):
            return f"<!--{data}-->"
        return ""

    return _COMMENT_RE.sub(_replace, html)


def _fix_fixed_footers(html: str) -> str:
    """Rewrite ``position: fixed`` footer rules to normal document flow.

    LLM-generated templates sometimes use ``position: fixed`` on footer
    elements.  This causes the footer to overlap table content on long
    reports.  We convert it to a normal-flow footer with a ``@media print``
    rule that uses ``position: fixed`` only in print context (where the
    browser paginates correctly).
    """

    def _rewrite(match: re.Match[str]) -> str:
        selector = match.group(1)
        before = match.group(2)
        after = match.group(3)

        # Remove position:fixed and bottom/left/right from the main rule
        body = before + after
        body = re.sub(r"position\s*:\s*fixed\s*;?", "", body)
        body = _FIXED_POS_PROPS_RE.sub("", body)
        # Clean up stray semicolons, whitespace, and blank lines
        body = re.sub(r";\s*;", ";", body)
        body = re.sub(r"\n\s*\n", "\n", body)
        body = body.strip().strip(";").strip()

        # Build clean flow rule + print-only fixed rule
        if body:
            flow_rule = f"{selector} {{\n  {body};\n  margin-top: 4mm;\n  padding-top: 2mm;\n}}"
        else:
            flow_rule = f"{selector} {{\n  margin-top: 4mm;\n  padding-top: 2mm;\n}}"
        print_rule = (
            f"@media print {{\n"
            f"  {selector} {{ position: fixed; bottom: 0; left: 0; right: 0; }}\n"
            f"}}"
        )
        return f"{flow_rule}\n{print_rule}"

    return _FIXED_FOOTER_RE.sub(_rewrite, html)


def sanitize_html(html: str) -> str:
    cleaned = bleach.clean(
        html or "",
        tags=sorted(ALLOWED_TAGS),
        attributes=_bleach_attributes(),
        protocols=["http", "https", "data"],
        strip=True,
        strip_comments=False,
        css_sanitizer=_CSS_SANITIZER,
    )
    cleaned = _filter_comments(cleaned)

    def _strip_style(match: re.Match[str]) -> str:
        value = match.group(1)
        value = re.sub(r"[;\s]+$", "", value)
        return f'style="{value}"'

    cleaned = _STYLE_ATTR_RE.sub(_strip_style, cleaned)
    cleaned = _fix_fixed_footers(cleaned)
    return cleaned
