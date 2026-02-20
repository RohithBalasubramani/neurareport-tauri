"""
Web Clipper Service Tests - Testing web page clipping and conversion.
"""

import os
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


# Check if BeautifulSoup is available
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

requires_bs4 = pytest.mark.skipif(not HAS_BS4, reason="BeautifulSoup (bs4) not installed")

from backend.app.services.ingestion.web_clipper import (
    WebClipperService,
    WebPageMetadata,
    ClippedContent,
)


@pytest.fixture
def service() -> WebClipperService:
    """Create a web clipper service instance."""
    return WebClipperService()


@pytest.fixture
def sample_html() -> str:
    """Sample HTML page content."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Test Article</title>
    <meta name="author" content="John Doe">
    <meta name="description" content="A test article">
    <meta property="og:title" content="Test Article OG">
    <meta property="og:site_name" content="Test Site">
    <meta property="og:image" content="/images/og.jpg">
    <meta property="article:published_time" content="2024-01-15T10:00:00Z">
</head>
<body>
    <nav>Navigation here</nav>
    <article>
        <h1>Main Title</h1>
        <p>This is the main content of the article. It has enough text to be detected.</p>
        <p>Second paragraph with more content that helps identify this as the main content area.</p>
        <a href="/related">Related Link</a>
        <img src="/images/photo.jpg" alt="Photo">
    </article>
    <aside class="sidebar">Sidebar content</aside>
    <footer>Footer here</footer>
</body>
</html>
"""


@pytest.fixture
def sample_selection_html() -> str:
    """Sample HTML selection."""
    return """
<p>This is the <strong>selected</strong> content.</p>
<a href="/link">A link</a>
"""


# =============================================================================
# METADATA EXTRACTION TESTS
# =============================================================================


@requires_bs4
class TestMetadataExtraction:
    """Test metadata extraction from HTML."""

    def test_extract_title_from_title_tag(self, service: WebClipperService, sample_html: str):
        """Extract title from title tag."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com")

        # og:title takes precedence
        assert metadata.title == "Test Article OG"

    def test_extract_author(self, service: WebClipperService, sample_html: str):
        """Extract author from meta tag."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com")

        assert metadata.author == "John Doe"

    def test_extract_description(self, service: WebClipperService, sample_html: str):
        """Extract description from meta tag."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com")

        assert metadata.description == "A test article"

    def test_extract_site_name(self, service: WebClipperService, sample_html: str):
        """Extract site name from og:site_name."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com")

        assert metadata.site_name == "Test Site"

    def test_extract_published_date(self, service: WebClipperService, sample_html: str):
        """Extract published date from article:published_time."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com")

        assert metadata.published_date == "2024-01-15T10:00:00Z"

    def test_extract_image_url_absolute(self, service: WebClipperService, sample_html: str):
        """Extract and make image URL absolute."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com/page")

        assert metadata.image_url == "https://example.com/images/og.jpg"

    def test_extract_url_stored(self, service: WebClipperService, sample_html: str):
        """URL is stored in metadata."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com/article")

        assert metadata.url == "https://example.com/article"

    def test_fallback_title_to_domain(self, service: WebClipperService):
        """Fallback to domain when no title found."""
        from bs4 import BeautifulSoup
        html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        metadata = service._extract_metadata(soup, "https://example.com/page")

        assert metadata.title == "example.com"


# =============================================================================
# CONTENT FINDING TESTS
# =============================================================================


@requires_bs4
class TestContentFinding:
    """Test main content element detection."""

    def test_find_article_element(self, service: WebClipperService, sample_html: str):
        """Find article element as main content."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        content = service._find_content_element(soup)

        assert content.name == "article"

    def test_find_main_element(self, service: WebClipperService):
        """Find main element as content."""
        from bs4 import BeautifulSoup
        html = "<html><body><main><p>Content here with lots of text that needs to exceed one hundred characters in total length so the content selector will actually pick it up properly and not fall back to body</p></main></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        content = service._find_content_element(soup)

        assert content.name == "main"

    def test_fallback_to_body(self, service: WebClipperService):
        """Fallback to body when no content element found."""
        from bs4 import BeautifulSoup
        html = "<html><body><p>Just text</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        content = service._find_content_element(soup)

        assert content.name == "body"

    def test_skip_short_content(self, service: WebClipperService):
        """Skip content elements with insufficient text."""
        from bs4 import BeautifulSoup
        html = """
        <html><body>
            <article>Short</article>
            <main>This is the main content with enough text to be detected as the primary content area. It has sufficient characters to exceed the one hundred character minimum threshold for detection.</main>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        content = service._find_content_element(soup)

        # Should skip article (too short) and find main
        assert content.name == "main"


# =============================================================================
# CONTENT CLEANING TESTS
# =============================================================================


@requires_bs4
class TestContentCleaning:
    """Test HTML content cleaning."""

    def test_remove_script_tags(self, service: WebClipperService):
        """Remove script tags from content."""
        from bs4 import BeautifulSoup
        html = "<div><p>Text</p><script>alert('hi')</script></div>"
        soup = BeautifulSoup(html, "html.parser")
        clean = service._clean_content(soup, "https://example.com")

        assert "script" not in clean.lower()
        assert "alert" not in clean

    def test_remove_style_tags(self, service: WebClipperService):
        """Remove style tags from content."""
        from bs4 import BeautifulSoup
        html = "<div><style>.foo { color: red; }</style><p>Text</p></div>"
        soup = BeautifulSoup(html, "html.parser")
        clean = service._clean_content(soup, "https://example.com")

        assert "<style>" not in clean

    def test_remove_nav_elements(self, service: WebClipperService):
        """Remove navigation elements."""
        from bs4 import BeautifulSoup
        html = "<div><nav>Menu</nav><p>Content</p></div>"
        soup = BeautifulSoup(html, "html.parser")
        clean = service._clean_content(soup, "https://example.com")

        assert "<nav>" not in clean
        assert "Menu" not in clean

    def test_fix_relative_links(self, service: WebClipperService):
        """Make relative links absolute."""
        from bs4 import BeautifulSoup
        html = '<div><a href="/page">Link</a></div>'
        soup = BeautifulSoup(html, "html.parser")
        clean = service._clean_content(soup, "https://example.com/article")

        assert 'href="https://example.com/page"' in clean

    def test_fix_relative_images(self, service: WebClipperService):
        """Make relative image URLs absolute."""
        from bs4 import BeautifulSoup
        html = '<div><p>Some article text here</p><img src="/images/photo.jpg"></div>'
        soup = BeautifulSoup(html, "html.parser")
        clean = service._clean_content(soup, "https://example.com/article")

        assert 'src="https://example.com/images/photo.jpg"' in clean


# =============================================================================
# TEXT EXTRACTION TESTS
# =============================================================================


@requires_bs4
class TestTextExtraction:
    """Test plain text extraction from HTML."""

    def test_extract_text_basic(self, service: WebClipperService):
        """Extract basic text from element."""
        from bs4 import BeautifulSoup
        html = "<p>Hello World</p>"
        soup = BeautifulSoup(html, "html.parser")
        text = service._extract_text(soup)

        assert text == "Hello World"

    def test_extract_text_collapses_whitespace(self, service: WebClipperService):
        """Whitespace is collapsed in extracted text."""
        from bs4 import BeautifulSoup
        html = "<p>Hello   \n\n  World</p>"
        soup = BeautifulSoup(html, "html.parser")
        text = service._extract_text(soup)

        assert text == "Hello World"

    def test_extract_text_multiple_elements(self, service: WebClipperService):
        """Extract text from multiple elements."""
        from bs4 import BeautifulSoup
        html = "<div><p>First</p><p>Second</p></div>"
        soup = BeautifulSoup(html, "html.parser")
        text = service._extract_text(soup)

        assert "First" in text
        assert "Second" in text


# =============================================================================
# IMAGE EXTRACTION TESTS
# =============================================================================


@requires_bs4
class TestImageExtraction:
    """Test image URL extraction from content."""

    def test_extract_images(self, service: WebClipperService):
        """Extract image URLs from content."""
        from bs4 import BeautifulSoup
        html = '<div><img src="/img1.jpg"><img src="/img2.jpg"></div>'
        soup = BeautifulSoup(html, "html.parser")
        images = service._extract_images(soup, "https://example.com")

        assert len(images) == 2
        assert "https://example.com/img1.jpg" in images
        assert "https://example.com/img2.jpg" in images

    def test_extract_images_data_src(self, service: WebClipperService):
        """Extract images with data-src attribute."""
        from bs4 import BeautifulSoup
        html = '<div><img data-src="/lazy.jpg"></div>'
        soup = BeautifulSoup(html, "html.parser")
        images = service._extract_images(soup, "https://example.com")

        assert "https://example.com/lazy.jpg" in images

    def test_extract_images_deduplicates(self, service: WebClipperService):
        """Duplicate image URLs are removed."""
        from bs4 import BeautifulSoup
        html = '<div><img src="/img.jpg"><img src="/img.jpg"></div>'
        soup = BeautifulSoup(html, "html.parser")
        images = service._extract_images(soup, "https://example.com")

        assert len(images) == 1

    def test_extract_images_limit(self, service: WebClipperService):
        """Image extraction is limited to 20."""
        from bs4 import BeautifulSoup
        imgs = "".join(f'<img src="/img{i}.jpg">' for i in range(30))
        html = f"<div>{imgs}</div>"
        soup = BeautifulSoup(html, "html.parser")
        images = service._extract_images(soup, "https://example.com")

        assert len(images) == 20


# =============================================================================
# LINK EXTRACTION TESTS
# =============================================================================


@requires_bs4
class TestLinkExtraction:
    """Test link extraction from content."""

    def test_extract_links(self, service: WebClipperService):
        """Extract links from content."""
        from bs4 import BeautifulSoup
        html = '<div><a href="/page1">Link 1</a><a href="/page2">Link 2</a></div>'
        soup = BeautifulSoup(html, "html.parser")
        links = service._extract_links(soup, "https://example.com")

        assert len(links) == 2
        assert links[0]["url"] == "https://example.com/page1"
        assert links[0]["text"] == "Link 1"

    def test_extract_links_skip_javascript(self, service: WebClipperService):
        """Skip javascript: links."""
        from bs4 import BeautifulSoup
        html = '<div><a href="javascript:void(0)">JS Link</a><a href="/page">Real Link</a></div>'
        soup = BeautifulSoup(html, "html.parser")
        links = service._extract_links(soup, "https://example.com")

        assert len(links) == 1
        assert links[0]["url"] == "https://example.com/page"

    def test_extract_links_deduplicates(self, service: WebClipperService):
        """Duplicate links are removed."""
        from bs4 import BeautifulSoup
        html = '<div><a href="/page">Link 1</a><a href="/page">Link 2</a></div>'
        soup = BeautifulSoup(html, "html.parser")
        links = service._extract_links(soup, "https://example.com")

        assert len(links) == 1

    def test_extract_links_limit(self, service: WebClipperService):
        """Link extraction is limited to 50."""
        from bs4 import BeautifulSoup
        anchors = "".join(f'<a href="/page{i}">Link {i}</a>' for i in range(60))
        html = f"<div>{anchors}</div>"
        soup = BeautifulSoup(html, "html.parser")
        links = service._extract_links(soup, "https://example.com")

        assert len(links) == 50

    def test_extract_links_text_truncated(self, service: WebClipperService):
        """Long link text is truncated."""
        from bs4 import BeautifulSoup
        long_text = "A" * 200
        html = f'<div><a href="/page">{long_text}</a></div>'
        soup = BeautifulSoup(html, "html.parser")
        links = service._extract_links(soup, "https://example.com")

        assert len(links[0]["text"]) == 100


# =============================================================================
# CLIP URL TESTS
# =============================================================================


@requires_bs4
class TestClipUrl:
    """Test full URL clipping."""

    @pytest.mark.asyncio
    async def test_clip_url(self, service: WebClipperService, sample_html: str):
        """Clip content from URL."""
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_response.raise_for_status = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_ctx = MagicMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_ctx)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_instance

            result = await service.clip_url("https://example.com/article")

        assert isinstance(result, ClippedContent)
        assert result.url == "https://example.com/article"
        assert result.title == "Test Article OG"
        assert result.document_id is not None

    @pytest.mark.asyncio
    async def test_clip_url_word_count(self, service: WebClipperService, sample_html: str):
        """Word count is calculated correctly."""
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_response.raise_for_status = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_ctx = MagicMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_ctx)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_instance

            result = await service.clip_url("https://example.com/article")

        assert result.metadata.word_count > 0

    @pytest.mark.asyncio
    async def test_clip_url_reading_time(self, service: WebClipperService, sample_html: str):
        """Reading time is estimated."""
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value=sample_html)
        mock_response.raise_for_status = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_ctx = MagicMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_ctx)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_instance

            result = await service.clip_url("https://example.com/article")

        assert result.metadata.reading_time_minutes >= 1


# =============================================================================
# CLIP SELECTION TESTS
# =============================================================================


@requires_bs4
class TestClipSelection:
    """Test user selection clipping."""

    @pytest.mark.asyncio
    async def test_clip_selection(self, service: WebClipperService, sample_selection_html: str):
        """Clip user-selected content."""
        result = await service.clip_selection(
            url="https://example.com/article",
            selected_html=sample_selection_html,
            page_title="Test Page",
        )

        assert isinstance(result, ClippedContent)
        assert result.title == "Test Page"
        assert result.url == "https://example.com/article"
        assert "selected" in result.plain_text.lower()

    @pytest.mark.asyncio
    async def test_clip_selection_default_title(self, service: WebClipperService, sample_selection_html: str):
        """Selection without title uses default."""
        result = await service.clip_selection(
            url="https://example.com/article",
            selected_html=sample_selection_html,
        )

        assert result.title == "Clipped Selection"

    @pytest.mark.asyncio
    async def test_clip_selection_extracts_links(self, service: WebClipperService, sample_selection_html: str):
        """Selection extracts links."""
        result = await service.clip_selection(
            url="https://example.com/article",
            selected_html=sample_selection_html,
        )

        assert len(result.links) > 0


# =============================================================================
# HTML TO MARKDOWN TESTS
# =============================================================================


@requires_bs4
class TestHtmlToMarkdown:
    """Test HTML to Markdown conversion."""

    def test_html_to_markdown_basic(self, service: WebClipperService):
        """Convert basic HTML to Markdown."""
        html = "<p>Hello <strong>World</strong></p>"
        # This may fail if html2text not installed
        try:
            result = service._html_to_markdown(html)
            assert "World" in result
        except ImportError:
            # Fallback should still work
            result = service._html_to_markdown(html)
            assert "World" in result


# =============================================================================
# HTML DOCUMENT WRAPPING TESTS
# =============================================================================


class TestHtmlDocumentWrapping:
    """Test wrapping clipped content as HTML document."""

    def test_wrap_as_html_document(self, service: WebClipperService):
        """Wrap clipped content as complete HTML."""
        clipped = ClippedContent(
            document_id="abc123",
            url="https://example.com/article",
            title="Test Article",
            clean_html="<p>Content here</p>",
            plain_text="Content here",
            metadata=WebPageMetadata(
                title="Test Article",
                url="https://example.com/article",
                author="John Doe",
                site_name="Test Site",
            ),
        )

        html = service._wrap_as_html_document(clipped)

        assert "<!DOCTYPE html>" in html
        assert "<title>Test Article</title>" in html
        assert "Content here" in html
        assert "Test Site" in html
        assert "John Doe" in html

    def test_wrap_includes_source_url(self, service: WebClipperService):
        """Wrapped HTML includes source URL."""
        clipped = ClippedContent(
            document_id="abc123",
            url="https://example.com/article",
            title="Test",
            clean_html="<p>Content</p>",
            plain_text="Content",
            metadata=WebPageMetadata(title="Test", url="https://example.com/article"),
        )

        html = service._wrap_as_html_document(clipped)

        assert "https://example.com/article" in html


# =============================================================================
# FILENAME SANITIZATION TESTS
# =============================================================================


class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_removes_invalid_chars(self, service: WebClipperService):
        """Remove invalid characters from filename."""
        result = service._sanitize_filename('Test: "Article" <1>')
        assert ":" not in result
        assert '"' not in result
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_limits_length(self, service: WebClipperService):
        """Filename is limited to 100 characters."""
        long_name = "A" * 200
        result = service._sanitize_filename(long_name)
        assert len(result) == 100

    def test_sanitize_fallback_empty(self, service: WebClipperService):
        """Empty/invalid name falls back to 'clipped'."""
        result = service._sanitize_filename(':<>"')
        assert result == "clipped"

    def test_sanitize_normal_name(self, service: WebClipperService):
        """Normal filename passes through."""
        result = service._sanitize_filename("My Article Title")
        assert result == "My Article Title"


# =============================================================================
# REMOVE ELEMENTS TESTS
# =============================================================================


class TestRemoveElements:
    """Test element removal configuration."""

    def test_remove_elements_list(self, service: WebClipperService):
        """Service has correct remove elements list."""
        assert "script" in service.REMOVE_ELEMENTS
        assert "style" in service.REMOVE_ELEMENTS
        assert "nav" in service.REMOVE_ELEMENTS
        assert "header" in service.REMOVE_ELEMENTS
        assert "footer" in service.REMOVE_ELEMENTS

    def test_content_selectors_list(self, service: WebClipperService):
        """Service has correct content selectors list."""
        assert "article" in service.CONTENT_SELECTORS
        assert "main" in service.CONTENT_SELECTORS
        assert ".content" in service.CONTENT_SELECTORS
