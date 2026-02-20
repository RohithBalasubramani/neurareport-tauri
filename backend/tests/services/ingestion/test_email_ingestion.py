"""
Email Ingestion Service Tests - Testing email parsing and document conversion.
"""

import os
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


from backend.app.services.ingestion.email_ingestion import (
    EmailIngestionService,
    ParsedEmail,
    EmailAttachment,
    EmailDocumentResult,
    EmailInboxConfig,
)


@pytest.fixture
def service() -> EmailIngestionService:
    """Create an email ingestion service instance."""
    return EmailIngestionService()


@pytest.fixture
def simple_email() -> bytes:
    """Create a simple plain text email."""
    msg = MIMEText("This is the email body content.")
    msg["Subject"] = "Test Subject"
    msg["From"] = "John Doe <john@example.com>"
    msg["To"] = "jane@example.com"
    msg["Cc"] = "bob@example.com"
    msg["Date"] = "Mon, 15 Jan 2024 10:00:00 +0000"
    msg["Message-ID"] = "<test123@example.com>"
    return msg.as_bytes()


@pytest.fixture
def html_email() -> bytes:
    """Create an HTML email."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "HTML Email"
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Message-ID"] = "<html123@example.com>"

    text = MIMEText("Plain text version", "plain")
    html = MIMEText("<html><body><h1>HTML Version</h1><p>Content here</p></body></html>", "html")
    msg.attach(text)
    msg.attach(html)

    return msg.as_bytes()


@pytest.fixture
def email_with_attachment() -> bytes:
    """Create an email with attachment."""
    msg = MIMEMultipart()
    msg["Subject"] = "Email with Attachment"
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Message-ID"] = "<attach123@example.com>"

    # Body
    body = MIMEText("Email body with attachment.")
    msg.attach(body)

    # Attachment
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(b"attachment content here")
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename="document.pdf")
    msg.attach(attachment)

    return msg.as_bytes()


# =============================================================================
# INBOX ADDRESS GENERATION TESTS
# =============================================================================


class TestGenerateInboxAddress:
    """Test unique inbox address generation."""

    def test_generate_inbox_address(self, service: EmailIngestionService):
        """Generate inbox address."""
        address = service.generate_inbox_address("user-123")

        assert address.startswith("ingest+")
        assert address.endswith("@neurareport.io")

    def test_generate_inbox_address_unique(self, service: EmailIngestionService):
        """Each address is unique."""
        addr1 = service.generate_inbox_address("user-1")
        addr2 = service.generate_inbox_address("user-1")
        addr3 = service.generate_inbox_address("user-2")

        assert addr1 != addr2
        assert addr1 != addr3

    def test_generate_inbox_address_with_purpose(self, service: EmailIngestionService):
        """Purpose affects generated address."""
        addr1 = service.generate_inbox_address("user-1", purpose="invoices")
        addr2 = service.generate_inbox_address("user-1", purpose="reports")

        assert addr1 != addr2

    def test_generate_inbox_address_format(self, service: EmailIngestionService):
        """Address has correct format."""
        address = service.generate_inbox_address("user-1")

        # Format: ingest+{12-char-hex}@neurareport.io
        parts = address.split("@")
        assert len(parts) == 2
        assert parts[0].startswith("ingest+")
        assert len(parts[0]) == 7 + 12  # "ingest+" + 12 hex chars


# =============================================================================
# PARSE EMAIL CONTENT TESTS
# =============================================================================


class TestParseEmailContent:
    """Test email content parsing."""

    @pytest.mark.asyncio
    async def test_parse_simple_email(self, service: EmailIngestionService, simple_email: bytes):
        """Parse simple plain text email."""
        result = await service.parse_email_content(simple_email)

        assert isinstance(result, ParsedEmail)
        assert result.subject == "Test Subject"
        assert result.from_address == "john@example.com"
        assert result.from_name == "John Doe"
        assert "jane@example.com" in result.to_addresses
        assert "bob@example.com" in result.cc_addresses

    @pytest.mark.asyncio
    async def test_parse_email_body_text(self, service: EmailIngestionService, simple_email: bytes):
        """Parse email body text."""
        result = await service.parse_email_content(simple_email)

        assert result.body_text is not None
        assert "email body content" in result.body_text

    @pytest.mark.asyncio
    async def test_parse_html_email(self, service: EmailIngestionService, html_email: bytes):
        """Parse HTML email."""
        result = await service.parse_email_content(html_email)

        assert result.body_html is not None
        assert "HTML Version" in result.body_html
        assert result.body_text is not None
        assert "Plain text" in result.body_text

    @pytest.mark.asyncio
    async def test_parse_email_with_attachment(self, service: EmailIngestionService, email_with_attachment: bytes):
        """Parse email with attachment."""
        result = await service.parse_email_content(email_with_attachment)

        assert len(result.attachments) == 1
        assert result.attachments[0].filename == "document.pdf"
        assert result.attachments[0].size_bytes > 0

    @pytest.mark.asyncio
    async def test_parse_email_message_id(self, service: EmailIngestionService, simple_email: bytes):
        """Parse email message ID."""
        result = await service.parse_email_content(simple_email)

        assert result.message_id == "<test123@example.com>"

    @pytest.mark.asyncio
    async def test_parse_email_date(self, service: EmailIngestionService, simple_email: bytes):
        """Parse email date."""
        result = await service.parse_email_content(simple_email)

        assert result.date is not None
        assert result.date.year == 2024
        assert result.date.month == 1
        assert result.date.day == 15

    @pytest.mark.asyncio
    async def test_parse_email_no_date(self, service: EmailIngestionService):
        """Handle email without date."""
        msg = MIMEText("Body")
        msg["Subject"] = "No Date"
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Message-ID"] = "<nodate@example.com>"

        result = await service.parse_email_content(msg.as_bytes())

        assert result.date is None


# =============================================================================
# CONVERT EMAIL TO DOCUMENT TESTS
# =============================================================================


class TestConvertEmailToDocument:
    """Test email to document conversion."""

    @pytest.mark.asyncio
    async def test_convert_email_to_document(self, service: EmailIngestionService, simple_email: bytes):
        """Convert email to document."""
        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "doc-123"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            result = await service.convert_email_to_document(simple_email)

        assert isinstance(result, EmailDocumentResult)
        assert result.email_subject == "Test Subject"
        assert result.from_address == "john@example.com"

    @pytest.mark.asyncio
    async def test_convert_email_processes_attachments(self, service: EmailIngestionService, email_with_attachment: bytes):
        """Convert email with attachments."""
        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "doc-123"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            result = await service.convert_email_to_document(
                email_with_attachment,
                include_attachments=True,
            )

        assert result.attachment_count == 1
        assert len(result.attachment_documents) == 1

    @pytest.mark.asyncio
    async def test_convert_email_skip_attachments(self, service: EmailIngestionService, email_with_attachment: bytes):
        """Convert email without processing attachments."""
        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "doc-123"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            result = await service.convert_email_to_document(
                email_with_attachment,
                include_attachments=False,
            )

        assert result.attachment_count == 0


# =============================================================================
# EMAIL THREAD TO DOCUMENT TESTS
# =============================================================================


class TestCreateDocumentFromThread:
    """Test email thread conversion."""

    @pytest.mark.asyncio
    async def test_create_document_from_thread(self, service: EmailIngestionService):
        """Convert email thread to document."""
        # Create multiple emails
        emails = []
        for i in range(3):
            msg = MIMEText(f"Email {i} content")
            msg["Subject"] = "Thread Subject"
            msg["From"] = f"user{i}@example.com"
            msg["To"] = "recipient@example.com"
            msg["Date"] = f"Mon, {15+i} Jan 2024 10:00:00 +0000"
            msg["Message-ID"] = f"<thread{i}@example.com>"
            emails.append(msg.as_bytes())

        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "thread-doc"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            result = await service.create_document_from_thread(emails)

        assert result.email_subject == "Thread Subject"

    @pytest.mark.asyncio
    async def test_create_document_from_thread_custom_title(self, service: EmailIngestionService):
        """Convert email thread with custom title."""
        msg = MIMEText("Content")
        msg["Subject"] = "Original"
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Message-ID"] = "<single@example.com>"

        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "doc-123"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            result = await service.create_document_from_thread(
                [msg.as_bytes()],
                thread_title="Custom Thread Title",
            )

        assert result.email_subject == "Custom Thread Title"


# =============================================================================
# PARSE INCOMING EMAIL TESTS
# =============================================================================


class TestParseIncomingEmail:
    """Test incoming email parsing with action item extraction."""

    @pytest.mark.asyncio
    async def test_parse_incoming_email(self, service: EmailIngestionService, simple_email: bytes):
        """Parse incoming email."""
        result = await service.parse_incoming_email(simple_email)

        assert "email" in result
        assert "action_items" in result
        assert "links" in result
        assert "mentions" in result

    @pytest.mark.asyncio
    async def test_parse_incoming_email_extracts_links(self, service: EmailIngestionService):
        """Parse email extracts links."""
        msg = MIMEText("Check out https://example.com and https://test.com/page")
        msg["Subject"] = "Links"
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Message-ID"] = "<links@example.com>"

        result = await service.parse_incoming_email(msg.as_bytes())

        assert len(result["links"]) == 2
        assert "https://example.com" in result["links"]

    @pytest.mark.asyncio
    async def test_parse_incoming_email_extracts_mentions(self, service: EmailIngestionService):
        """Parse email extracts @mentions."""
        msg = MIMEText("Hey @john, please review this with @jane")
        msg["Subject"] = "Mentions"
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Message-ID"] = "<mentions@example.com>"

        result = await service.parse_incoming_email(msg.as_bytes())

        assert "john" in result["mentions"]
        assert "jane" in result["mentions"]

    @pytest.mark.asyncio
    async def test_parse_incoming_email_action_items(self, service: EmailIngestionService):
        """Parse email extracts action items."""
        msg = MIMEText("Please review the document. Could you send the report by Friday?")
        msg["Subject"] = "Action Items"
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Message-ID"] = "<actions@example.com>"

        result = await service.parse_incoming_email(msg.as_bytes())

        assert len(result["action_items"]) > 0


# =============================================================================
# HEADER DECODING TESTS
# =============================================================================


class TestHeaderDecoding:
    """Test email header decoding."""

    def test_decode_simple_header(self, service: EmailIngestionService):
        """Decode simple ASCII header."""
        result = service._decode_header("Simple Subject")
        assert result == "Simple Subject"

    def test_decode_empty_header(self, service: EmailIngestionService):
        """Decode empty header."""
        result = service._decode_header("")
        assert result == ""

    def test_decode_none_header(self, service: EmailIngestionService):
        """Decode None header."""
        result = service._decode_header(None)
        assert result == ""


# =============================================================================
# ADDRESS PARSING TESTS
# =============================================================================


class TestAddressParsing:
    """Test email address parsing."""

    def test_parse_single_address(self, service: EmailIngestionService):
        """Parse single email address."""
        result = service._parse_address_list("user@example.com")
        assert result == ["user@example.com"]

    def test_parse_multiple_addresses(self, service: EmailIngestionService):
        """Parse multiple email addresses."""
        result = service._parse_address_list("user1@example.com, user2@example.com")
        assert len(result) == 2
        assert "user1@example.com" in result
        assert "user2@example.com" in result

    def test_parse_named_address(self, service: EmailIngestionService):
        """Parse named email address."""
        result = service._parse_address_list("John Doe <john@example.com>")
        assert result == ["john@example.com"]

    def test_parse_empty_address(self, service: EmailIngestionService):
        """Parse empty address list."""
        result = service._parse_address_list("")
        assert result == []


# =============================================================================
# FILENAME SANITIZATION TESTS
# =============================================================================


class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_normal_name(self, service: EmailIngestionService):
        """Sanitize normal filename."""
        result = service._sanitize_filename("Report 2024")
        assert result == "Report 2024"

    def test_sanitize_removes_invalid_chars(self, service: EmailIngestionService):
        """Sanitize removes invalid characters."""
        result = service._sanitize_filename('Re: "Test" <subject>')
        assert ":" not in result
        assert '"' not in result
        assert "<" not in result

    def test_sanitize_limits_length(self, service: EmailIngestionService):
        """Sanitize limits filename length."""
        long_name = "A" * 200
        result = service._sanitize_filename(long_name)
        assert len(result) == 100

    def test_sanitize_empty_fallback(self, service: EmailIngestionService):
        """Sanitize empty name falls back."""
        result = service._sanitize_filename(':<>"')
        assert result == "untitled"


# =============================================================================
# HTML TO TEXT TESTS
# =============================================================================


class TestHtmlToText:
    """Test HTML to text conversion."""

    def test_html_to_text_basic(self, service: EmailIngestionService):
        """Convert basic HTML to text."""
        html = "<p>Hello World</p>"
        result = service._html_to_text(html)
        assert "Hello World" in result

    def test_html_to_text_removes_tags(self, service: EmailIngestionService):
        """HTML tags are removed."""
        html = "<div><p><strong>Bold</strong> text</p></div>"
        result = service._html_to_text(html)
        assert "<" not in result
        assert ">" not in result
        assert "Bold" in result


# =============================================================================
# EMAIL FORMATTING TESTS
# =============================================================================


class TestEmailFormatting:
    """Test email document formatting."""

    def test_format_email_as_document(self, service: EmailIngestionService):
        """Format email as HTML document."""
        parsed = ParsedEmail(
            message_id="<test@example.com>",
            subject="Test Subject",
            from_address="sender@example.com",
            from_name="John Doe",
            to_addresses=["recipient@example.com"],
            body_text="Email body content",
            date=datetime(2024, 1, 15, 10, 0, 0),
        )

        html = service._format_email_as_document(parsed)

        assert "<!DOCTYPE html>" in html
        assert "Test Subject" in html
        assert "John Doe" in html
        assert "Email body content" in html

    def test_format_email_with_attachments(self, service: EmailIngestionService):
        """Format email with attachments section."""
        parsed = ParsedEmail(
            message_id="<test@example.com>",
            subject="With Attachments",
            from_address="sender@example.com",
            to_addresses=["recipient@example.com"],
            attachments=[
                EmailAttachment(filename="doc.pdf", content_type="application/pdf", size_bytes=1024),
            ],
        )

        html = service._format_email_as_document(parsed)

        assert "doc.pdf" in html
        assert "1,024 bytes" in html


# =============================================================================
# THREAD FORMATTING TESTS
# =============================================================================


class TestThreadFormatting:
    """Test email thread document formatting."""

    def test_format_thread_as_document(self, service: EmailIngestionService):
        """Format email thread as HTML document."""
        emails = [
            ParsedEmail(
                message_id="<msg1@example.com>",
                subject="Thread",
                from_address="user1@example.com",
                from_name="User One",
                to_addresses=["recipient@example.com"],
                body_text="First message",
                date=datetime(2024, 1, 15, 10, 0, 0),
            ),
            ParsedEmail(
                message_id="<msg2@example.com>",
                subject="Re: Thread",
                from_address="user2@example.com",
                from_name="User Two",
                to_addresses=["user1@example.com"],
                body_text="Reply message",
                date=datetime(2024, 1, 15, 11, 0, 0),
            ),
        ]

        html = service._format_thread_as_document(emails, "Thread Title")

        assert "Thread Title" in html
        assert "2 messages" in html
        assert "User One" in html
        assert "User Two" in html


# =============================================================================
# EMAIL INBOX CONFIG TESTS
# =============================================================================


class TestEmailInboxConfig:
    """Test EmailInboxConfig model."""

    def test_config_required_fields(self):
        """Config requires essential fields."""
        config = EmailInboxConfig(
            inbox_id="inbox-1",
            email_address="inbox@example.com",
            imap_server="imap.example.com",
            username="user",
            password="pass",
        )

        assert config.inbox_id == "inbox-1"
        assert config.imap_port == 993  # Default

    def test_config_defaults(self):
        """Config has sensible defaults."""
        config = EmailInboxConfig(
            inbox_id="inbox-1",
            email_address="inbox@example.com",
            imap_server="imap.example.com",
            username="user",
            password="pass",
        )

        assert config.folder == "INBOX"
        assert config.auto_process is True
        assert config.delete_after_process is False


# =============================================================================
# EMAIL ATTACHMENT MODEL TESTS
# =============================================================================


class TestEmailAttachment:
    """Test EmailAttachment model."""

    def test_attachment_required_fields(self):
        """Attachment has required fields."""
        attachment = EmailAttachment(
            filename="document.pdf",
            content_type="application/pdf",
            size_bytes=1024,
        )

        assert attachment.filename == "document.pdf"
        assert attachment.size_bytes == 1024

    def test_attachment_optional_document_id(self):
        """Attachment can have document ID."""
        attachment = EmailAttachment(
            filename="document.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            document_id="doc-123",
        )

        assert attachment.document_id == "doc-123"


# =============================================================================
# PARSED EMAIL MODEL TESTS
# =============================================================================


class TestParsedEmail:
    """Test ParsedEmail model."""

    def test_parsed_email_minimal(self):
        """ParsedEmail with minimal fields."""
        email = ParsedEmail(
            message_id="<test@example.com>",
            subject="Test",
            from_address="sender@example.com",
        )

        assert email.to_addresses == []
        assert email.cc_addresses == []
        assert email.attachments == []

    def test_parsed_email_full(self):
        """ParsedEmail with all fields."""
        email = ParsedEmail(
            message_id="<test@example.com>",
            subject="Full Test",
            from_address="sender@example.com",
            from_name="John Doe",
            to_addresses=["recipient@example.com"],
            cc_addresses=["cc@example.com"],
            date=datetime.now(timezone.utc),
            body_text="Plain text",
            body_html="<p>HTML</p>",
            thread_id="<thread@example.com>",
            in_reply_to="<original@example.com>",
        )

        assert email.from_name == "John Doe"
        assert email.thread_id == "<thread@example.com>"
