"""
Web Clipper Service
Handles web page capture, cleaning, and conversion to documents.
"""
from __future__ import annotations

import logging
import re
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from pydantic import BaseModel, Field

from backend.app.utils.ssrf_guard import validate_url, SSRFError

logger = logging.getLogger(__name__)


class WebPageMetadata(BaseModel):
    """Metadata extracted from a web page."""
    title: str
    url: str
    author: Optional[str] = None
    published_date: Optional[str] = None
    site_name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    word_count: int = 0
    reading_time_minutes: int = 0


class ClippedContent(BaseModel):
    """Content clipped from a web page."""
    document_id: str
    url: str
    title: str
    clean_html: str
    plain_text: str
    metadata: WebPageMetadata
    images: List[str] = Field(default_factory=list)
    links: List[Dict[str, str]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WebClipperService:
    """
    Service for clipping web pages and converting them to editable documents.
    Supports content extraction, cleaning, and metadata parsing.
    """

    # Elements to remove from content
    REMOVE_ELEMENTS = [
        "script", "style", "nav", "header", "footer", "aside",
        "iframe", "noscript", "form", "button", "input",
        "advertisement", ".ad", ".ads", ".sidebar", ".navigation",
        ".menu", ".social", ".share", ".comments", ".related",
    ]

    # Content containers to prioritize
    CONTENT_SELECTORS = [
        "article", "main", "[role='main']", ".post-content",
        ".article-content", ".entry-content", ".content",
        "#content", ".post", ".article",
    ]

    async def clip_url(
        self,
        url: str,
        include_images: bool = True,
        clean_content: bool = True,
    ) -> ClippedContent:
        """
        Clip content from a URL.

        Args:
            url: URL to clip
            include_images: Whether to download and include images
            clean_content: Whether to clean the HTML

        Returns:
            ClippedContent with extracted content
        """
        import aiohttp
        from bs4 import BeautifulSoup

        validate_url(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; NeuraReport/1.0)"}) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")

        # Extract metadata
        metadata = self._extract_metadata(soup, url)

        # Find main content
        content_element = self._find_content_element(soup)

        if clean_content:
            clean_html = self._clean_content(content_element, url)
        else:
            clean_html = str(content_element)

        # Extract plain text
        plain_text = self._extract_text(content_element)
        metadata.word_count = len(plain_text.split())
        metadata.reading_time_minutes = max(1, metadata.word_count // 200)

        # Extract images
        images = []
        if include_images:
            images = self._extract_images(content_element, url)

        # Extract links
        links = self._extract_links(content_element, url)

        # Generate document ID
        doc_id = hashlib.sha256(f"{url}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16]

        return ClippedContent(
            document_id=doc_id,
            url=url,
            title=metadata.title,
            clean_html=clean_html,
            plain_text=plain_text,
            metadata=metadata,
            images=images,
            links=links,
        )

    async def clip_selection(
        self,
        url: str,
        selected_html: str,
        page_title: Optional[str] = None,
    ) -> ClippedContent:
        """
        Clip a user-selected portion of a page.

        Args:
            url: Source URL
            selected_html: HTML of selected content
            page_title: Optional page title

        Returns:
            ClippedContent with selected content
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(selected_html, "html.parser")

        clean_html = self._clean_content(soup, url)
        plain_text = self._extract_text(soup)

        doc_id = hashlib.sha256(f"{url}:selection:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16]

        metadata = WebPageMetadata(
            title=page_title or "Clipped Selection",
            url=url,
            word_count=len(plain_text.split()),
            reading_time_minutes=max(1, len(plain_text.split()) // 200),
        )

        return ClippedContent(
            document_id=doc_id,
            url=url,
            title=metadata.title,
            clean_html=clean_html,
            plain_text=plain_text,
            metadata=metadata,
            images=self._extract_images(soup, url),
            links=self._extract_links(soup, url),
        )

    async def save_as_document(
        self,
        clipped: ClippedContent,
        format: str = "html",
    ) -> str:
        """
        Save clipped content as a document.

        Args:
            clipped: Clipped content to save
            format: Output format (html, markdown, pdf)

        Returns:
            Document ID
        """
        from .service import ingestion_service

        if format == "markdown":
            content = self._html_to_markdown(clipped.clean_html)
            filename = f"{self._sanitize_filename(clipped.title)}.md"
        elif format == "pdf":
            # Would generate PDF here
            content = self._wrap_as_html_document(clipped)
            filename = f"{self._sanitize_filename(clipped.title)}.html"
        else:
            content = self._wrap_as_html_document(clipped)
            filename = f"{self._sanitize_filename(clipped.title)}.html"

        result = await ingestion_service.ingest_file(
            filename=filename,
            content=content.encode("utf-8"),
            metadata={
                "source": "web_clipper",
                "source_url": clipped.url,
                "clipped_at": clipped.created_at.isoformat(),
                **clipped.metadata.model_dump(),
            },
        )

        return result.document_id

    async def capture_screenshot(
        self,
        url: str,
        full_page: bool = False,
    ) -> bytes:
        """
        Capture screenshot of a web page.

        Args:
            url: URL to capture
            full_page: Whether to capture full page or viewport

        Returns:
            PNG image bytes
        """
        # This would use Playwright or Puppeteer
        # Placeholder implementation
        logger.info(f"Screenshot capture requested for: {url}")
        raise NotImplementedError("Screenshot capture requires browser automation")

    def _extract_metadata(self, soup, url: str) -> WebPageMetadata:
        """Extract metadata from page."""
        # Title
        title = ""
        if soup.title:
            title = soup.title.string or ""

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]

        # Author
        author = None
        author_meta = soup.find("meta", {"name": "author"})
        if author_meta and author_meta.get("content"):
            author = author_meta["content"]

        # Published date
        published_date = None
        date_meta = soup.find("meta", {"property": "article:published_time"})
        if date_meta and date_meta.get("content"):
            published_date = date_meta["content"]

        # Site name
        site_name = None
        site_meta = soup.find("meta", {"property": "og:site_name"})
        if site_meta and site_meta.get("content"):
            site_name = site_meta["content"]

        # Description
        description = None
        desc_meta = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
        if desc_meta and desc_meta.get("content"):
            description = desc_meta["content"]

        # Image
        image_url = None
        img_meta = soup.find("meta", {"property": "og:image"})
        if img_meta and img_meta.get("content"):
            image_url = urljoin(url, img_meta["content"])

        return WebPageMetadata(
            title=title.strip() or urlparse(url).netloc,
            url=url,
            author=author,
            published_date=published_date,
            site_name=site_name,
            description=description,
            image_url=image_url,
        )

    def _find_content_element(self, soup):
        """Find the main content element."""
        # Try priority selectors
        for selector in self.CONTENT_SELECTORS:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 100:
                return element

        # Fall back to body
        return soup.body or soup

    def _clean_content(self, element, base_url: str) -> str:
        """Clean content by removing unwanted elements."""
        from bs4 import BeautifulSoup
        from copy import copy

        # Work on a copy
        soup = BeautifulSoup(str(element), "html.parser")

        # Remove unwanted elements
        for selector in self.REMOVE_ELEMENTS:
            for el in soup.select(selector):
                el.decompose()

        # Fix relative URLs
        for tag in soup.find_all(["a", "img"]):
            if tag.name == "a" and tag.get("href"):
                tag["href"] = urljoin(base_url, tag["href"])
            if tag.name == "img" and tag.get("src"):
                tag["src"] = urljoin(base_url, tag["src"])

        # Remove empty elements
        for el in soup.find_all():
            if not el.get_text(strip=True) and el.name not in ["img", "br", "hr"]:
                el.decompose()

        return str(soup)

    def _extract_text(self, element) -> str:
        """Extract plain text from element."""
        text = element.get_text(separator=" ", strip=True)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_images(self, element, base_url: str) -> List[str]:
        """Extract image URLs from element."""
        images = []
        for img in element.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                full_url = urljoin(base_url, src)
                if full_url not in images:
                    images.append(full_url)
        return images[:20]  # Limit

    def _extract_links(self, element, base_url: str) -> List[Dict[str, str]]:
        """Extract links from element."""
        links = []
        seen = set()
        for a in element.find_all("a", href=True):
            href = urljoin(base_url, a["href"])
            if href not in seen and not href.startswith("javascript:"):
                seen.add(href)
                links.append({
                    "url": href,
                    "text": a.get_text(strip=True)[:100],
                })
        return links[:50]  # Limit

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown."""
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            return h.handle(html)
        except ImportError:
            # Simple fallback
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator="\n\n")

    def _wrap_as_html_document(self, clipped: ClippedContent) -> str:
        """Wrap clipped content as a complete HTML document."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{clipped.title}</title>
    <meta name="source-url" content="{clipped.url}">
    <meta name="clipped-date" content="{clipped.created_at.isoformat()}">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .source-info {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #666;
        }}
        img {{ max-width: 100%; height: auto; }}
        a {{ color: #1976d2; }}
    </style>
</head>
<body>
    <div class="source-info">
        <strong>Source:</strong> <a href="{clipped.url}">{clipped.metadata.site_name or clipped.url}</a><br>
        {f'<strong>Author:</strong> {clipped.metadata.author}<br>' if clipped.metadata.author else ''}
        {f'<strong>Published:</strong> {clipped.metadata.published_date}<br>' if clipped.metadata.published_date else ''}
        <strong>Clipped:</strong> {clipped.created_at.strftime('%B %d, %Y at %I:%M %p')}
    </div>

    <h1>{clipped.title}</h1>

    <div class="content">
        {clipped.clean_html}
    </div>
</body>
</html>"""

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename."""
        sanitized = re.sub(r'[<>:"/\\|?*]', "", name)
        return sanitized[:100] or "clipped"


# Singleton instance
web_clipper_service = WebClipperService()
