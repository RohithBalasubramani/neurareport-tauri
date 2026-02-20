"""
Email Ingestion Service
Handles email-to-document conversion and email inbox monitoring.
"""
from __future__ import annotations

import logging
import email
import imaplib
import hashlib
import re
from datetime import datetime, timezone
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EmailAttachment(BaseModel):
    """Email attachment details."""
    filename: str
    content_type: str
    size_bytes: int
    document_id: Optional[str] = None


class ParsedEmail(BaseModel):
    """Parsed email structure."""
    message_id: str
    subject: str
    from_address: str
    from_name: Optional[str] = None
    to_addresses: List[str] = Field(default_factory=list)
    cc_addresses: List[str] = Field(default_factory=list)
    date: Optional[datetime] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[EmailAttachment] = Field(default_factory=list)
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None


class EmailDocumentResult(BaseModel):
    """Result of converting email to document."""
    document_id: str
    email_subject: str
    from_address: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    attachment_count: int = 0
    attachment_documents: List[str] = Field(default_factory=list)


class EmailInboxConfig(BaseModel):
    """Email inbox configuration."""
    inbox_id: str
    email_address: str
    imap_server: str
    imap_port: int = 993
    username: str
    password: str  # Should be encrypted in practice
    use_ssl: bool = True
    folder: str = "INBOX"
    auto_process: bool = True
    delete_after_process: bool = False


class EmailIngestionService:
    """
    Service for ingesting documents from emails.
    Supports unique inbox addresses, IMAP monitoring, and attachment extraction.
    """

    def __init__(self):
        self._inbox_configs: Dict[str, EmailInboxConfig] = {}

    async def connect_imap(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
        folder: str = "INBOX",
    ) -> Dict[str, Any]:
        """
        Validate IMAP credentials and register an account configuration.

        Returns a safe account payload without sensitive fields.
        """
        if not host or not username or not password:
            raise ValueError("host, username, and password are required")

        # Validate credentials before storing.
        try:
            client = imaplib.IMAP4_SSL(host, port) if use_ssl else imaplib.IMAP4(host, port)
            client.login(username, password)
            client.select(folder)
            client.logout()
        except imaplib.IMAP4.error as exc:
            raise ValueError("IMAP authentication failed") from exc
        except Exception as exc:
            raise ValueError("Unable to connect to IMAP server") from exc

        account_id = hashlib.sha256(f"{host}:{port}:{username}:{folder}".encode()).hexdigest()[:16]
        cfg = EmailInboxConfig(
            inbox_id=account_id,
            email_address=username,
            imap_server=host,
            imap_port=port,
            username=username,
            password=password,
            use_ssl=use_ssl,
            folder=folder,
        )
        self._inbox_configs[account_id] = cfg

        return {
            "id": account_id,
            "account_id": account_id,
            "email_address": cfg.email_address,
            "host": cfg.imap_server,
            "port": cfg.imap_port,
            "folder": cfg.folder,
            "use_ssl": cfg.use_ssl,
            "status": "connected",
        }

    def list_imap_accounts(self) -> List[Dict[str, Any]]:
        """List registered IMAP accounts (without credentials)."""
        accounts: List[Dict[str, Any]] = []
        for account_id, cfg in self._inbox_configs.items():
            accounts.append({
                "id": account_id,
                "account_id": account_id,
                "email_address": cfg.email_address,
                "host": cfg.imap_server,
                "port": cfg.imap_port,
                "folder": cfg.folder,
                "use_ssl": cfg.use_ssl,
                "status": "connected",
            })
        return accounts

    async def sync_imap_account(self, account_id: str, limit: int = 50) -> Dict[str, Any]:
        """Sync recent messages from a configured IMAP account."""
        cfg = self._inbox_configs.get(account_id)
        if not cfg:
            raise ValueError("IMAP account not found")

        results = await self.fetch_from_imap(cfg, limit=limit, unseen_only=True)
        return {
            "account_id": account_id,
            "status": "completed",
            "synced": len(results),
            "documents": [r.document_id for r in results],
        }

    def generate_inbox_address(self, user_id: str, purpose: str = "default") -> str:
        """
        Generate a unique inbox address for a user.

        Args:
            user_id: User identifier
            purpose: Purpose label for the inbox

        Returns:
            Unique email address for forwarding
        """
        # Generate unique identifier
        unique_part = hashlib.sha256(f"{user_id}:{purpose}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]
        # Format: ingest+{unique}@neurareport.io
        return f"ingest+{unique_part}@neurareport.io"

    async def parse_email_content(self, raw_email: bytes) -> ParsedEmail:
        """
        Parse raw email content into structured format.

        Args:
            raw_email: Raw email bytes (RFC 822 format)

        Returns:
            ParsedEmail with extracted data
        """
        msg = email.message_from_bytes(raw_email)

        # Parse headers
        subject = self._decode_header(msg.get("Subject", ""))
        from_name, from_address = parseaddr(msg.get("From", ""))
        from_name = self._decode_header(from_name) if from_name else None

        to_addresses = self._parse_address_list(msg.get("To", ""))
        cc_addresses = self._parse_address_list(msg.get("Cc", ""))

        # Parse date
        date_str = msg.get("Date")
        date = None
        if date_str:
            try:
                date = parsedate_to_datetime(date_str)
            except Exception:
                pass

        # Get message ID and threading info
        message_id = msg.get("Message-ID", "")
        in_reply_to = msg.get("In-Reply-To")
        thread_id = msg.get("References", "").split()[0] if msg.get("References") else message_id

        # Extract body
        body_text = None
        body_html = None
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                        payload = part.get_payload(decode=True)
                        attachments.append(EmailAttachment(
                            filename=filename,
                            content_type=content_type,
                            size_bytes=len(payload) if payload else 0,
                        ))
                elif content_type == "text/plain" and not body_text:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_text = payload.decode("utf-8", errors="replace")
                elif content_type == "text/html" and not body_html:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_html = payload.decode("utf-8", errors="replace")
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                if content_type == "text/html":
                    body_html = payload.decode("utf-8", errors="replace")
                else:
                    body_text = payload.decode("utf-8", errors="replace")

        return ParsedEmail(
            message_id=message_id,
            subject=subject,
            from_address=from_address,
            from_name=from_name,
            to_addresses=to_addresses,
            cc_addresses=cc_addresses,
            date=date,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            thread_id=thread_id,
            in_reply_to=in_reply_to,
        )

    async def convert_email_to_document(
        self,
        raw_email: bytes,
        include_attachments: bool = True,
    ) -> EmailDocumentResult:
        """
        Convert an email into a document.

        Args:
            raw_email: Raw email bytes
            include_attachments: Whether to process attachments

        Returns:
            EmailDocumentResult with created document
        """
        from .service import ingestion_service

        parsed = await self.parse_email_content(raw_email)

        # Create document content from email
        content = self._format_email_as_document(parsed)

        # Generate document ID
        doc_id = hashlib.sha256(parsed.message_id.encode()).hexdigest()[:16]

        # Save as document
        result = await ingestion_service.ingest_file(
            filename=f"{self._sanitize_filename(parsed.subject)}.html",
            content=content.encode("utf-8"),
            metadata={
                "source": "email",
                "email_from": parsed.from_address,
                "email_subject": parsed.subject,
                "email_date": parsed.date.isoformat() if parsed.date else None,
                "message_id": parsed.message_id,
                "thread_id": parsed.thread_id,
            },
        )

        # Process attachments
        attachment_docs = []
        if include_attachments and parsed.attachments:
            msg = email.message_from_bytes(raw_email)
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                        payload = part.get_payload(decode=True)
                        if payload:
                            att_result = await ingestion_service.ingest_file(
                                filename=filename,
                                content=payload,
                                metadata={
                                    "source": "email_attachment",
                                    "parent_email_id": doc_id,
                                },
                            )
                            attachment_docs.append(att_result.document_id)

        return EmailDocumentResult(
            document_id=doc_id,
            email_subject=parsed.subject,
            from_address=parsed.from_address,
            attachment_count=len(attachment_docs),
            attachment_documents=attachment_docs,
        )

    async def create_document_from_thread(
        self,
        emails: List[bytes],
        thread_title: Optional[str] = None,
    ) -> EmailDocumentResult:
        """
        Create a single document from an email thread.

        Args:
            emails: List of raw email bytes in chronological order
            thread_title: Optional title override

        Returns:
            EmailDocumentResult with created document
        """
        from .service import ingestion_service

        parsed_emails = []
        for raw in emails:
            parsed = await self.parse_email_content(raw)
            parsed_emails.append(parsed)

        # Sort by date
        parsed_emails.sort(key=lambda e: e.date or datetime.min)

        # Build thread document
        if not thread_title and parsed_emails:
            thread_title = parsed_emails[0].subject

        content = self._format_thread_as_document(parsed_emails, thread_title)

        # Generate document
        doc_id = hashlib.sha256(f"thread:{thread_title}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16]

        result = await ingestion_service.ingest_file(
            filename=f"{self._sanitize_filename(thread_title or 'Email Thread')}.html",
            content=content.encode("utf-8"),
            metadata={
                "source": "email_thread",
                "email_count": len(parsed_emails),
                "participants": list(set(e.from_address for e in parsed_emails)),
            },
        )

        return EmailDocumentResult(
            document_id=result.document_id,
            email_subject=thread_title or "Email Thread",
            from_address=parsed_emails[0].from_address if parsed_emails else "",
        )

    async def fetch_from_imap(
        self,
        config: EmailInboxConfig,
        limit: int = 10,
        unseen_only: bool = True,
    ) -> List[EmailDocumentResult]:
        """
        Fetch and process emails from an IMAP inbox.

        Args:
            config: IMAP configuration
            limit: Maximum emails to process
            unseen_only: Only process unread emails

        Returns:
            List of created documents
        """
        results = []

        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
            mail.login(config.username, config.password)
            mail.select(config.folder)

            # Search for emails
            search_criteria = "UNSEEN" if unseen_only else "ALL"
            status, messages = mail.search(None, search_criteria)

            if status != "OK":
                logger.error(f"IMAP search failed: {status}")
                return results

            message_ids = messages[0].split()[-limit:]  # Get latest N

            for msg_id in message_ids:
                try:
                    status, data = mail.fetch(msg_id, "(RFC822)")
                    if status == "OK" and data[0]:
                        raw_email = data[0][1]
                        result = await self.convert_email_to_document(raw_email)
                        results.append(result)

                        # Mark as read or delete
                        if config.delete_after_process:
                            mail.store(msg_id, "+FLAGS", "\\Deleted")
                        else:
                            mail.store(msg_id, "+FLAGS", "\\Seen")

                except Exception as e:
                    logger.error(f"Failed to process email {msg_id}: {e}")

            if config.delete_after_process:
                mail.expunge()

            mail.logout()

        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")

        return results

    async def parse_incoming_email(
        self,
        raw_email: bytes,
        extract_action_items: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse incoming email and extract structured data.

        Args:
            raw_email: Raw email bytes
            extract_action_items: Whether to extract tasks/action items

        Returns:
            Dictionary with parsed data including action items
        """
        parsed = await self.parse_email_content(raw_email)

        result = {
            "email": parsed.model_dump(),
            "action_items": [],
            "mentions": [],
            "links": [],
            "dates": [],
        }

        # Extract from body
        body = parsed.body_text or self._html_to_text(parsed.body_html or "")

        if extract_action_items:
            # Simple action item extraction (would use AI for better results)
            action_patterns = [
                r"(?:please|could you|can you|would you|need to|must|should|will you)\s+(.+?)(?:\.|$)",
                r"(?:action item|todo|task):\s*(.+?)(?:\.|$)",
                r"(?:by|before|due)\s+(\w+\s+\d+|\d+\/\d+)",
            ]
            for pattern in action_patterns:
                matches = re.findall(pattern, body, re.IGNORECASE)
                result["action_items"].extend(matches[:5])

        # Extract links
        url_pattern = r"https?://[^\s<>\"']+"
        result["links"] = re.findall(url_pattern, body)[:10]

        # Extract @mentions
        mention_pattern = r"@(\w+)"
        result["mentions"] = re.findall(mention_pattern, body)

        return result

    def _decode_header(self, value: str) -> str:
        """Decode email header value."""
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                result.append(part)
        return "".join(result)

    def _parse_address_list(self, value: str) -> List[str]:
        """Parse comma-separated email addresses."""
        if not value:
            return []
        addresses = []
        for addr in value.split(","):
            _, email_addr = parseaddr(addr.strip())
            if email_addr:
                addresses.append(email_addr)
        return addresses

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename."""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "", name)
        # Limit length
        return sanitized[:100] or "untitled"

    def _format_email_as_document(self, parsed: ParsedEmail) -> str:
        """Format parsed email as HTML document."""
        date_str = parsed.date.strftime("%B %d, %Y at %I:%M %p") if parsed.date else "Unknown date"

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{parsed.subject}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        .email-header {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .email-meta {{ color: #666; font-size: 14px; margin: 5px 0; }}
        .email-body {{ line-height: 1.6; }}
        .attachments {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="email-header">
        <h1>{parsed.subject}</h1>
        <p class="email-meta"><strong>From:</strong> {parsed.from_name or ''} &lt;{parsed.from_address}&gt;</p>
        <p class="email-meta"><strong>To:</strong> {', '.join(parsed.to_addresses)}</p>
        {f'<p class="email-meta"><strong>CC:</strong> {", ".join(parsed.cc_addresses)}</p>' if parsed.cc_addresses else ''}
        <p class="email-meta"><strong>Date:</strong> {date_str}</p>
    </div>

    <div class="email-body">
        {parsed.body_html or f'<pre>{parsed.body_text or ""}</pre>'}
    </div>

    {self._format_attachments_section(parsed.attachments) if parsed.attachments else ''}
</body>
</html>"""

    def _format_thread_as_document(self, emails: List[ParsedEmail], title: str) -> str:
        """Format email thread as HTML document."""
        emails_html = ""
        for i, email_msg in enumerate(emails):
            date_str = email_msg.date.strftime("%B %d, %Y at %I:%M %p") if email_msg.date else "Unknown date"
            emails_html += f"""
            <div class="email-message" style="border-left: 3px solid #1976d2; padding-left: 20px; margin: 20px 0;">
                <div class="message-header">
                    <strong>{email_msg.from_name or email_msg.from_address}</strong>
                    <span style="color: #666; margin-left: 10px;">{date_str}</span>
                </div>
                <div class="message-body" style="margin-top: 10px;">
                    {email_msg.body_html or f'<pre>{email_msg.body_text or ""}</pre>'}
                </div>
            </div>
            """

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ border-bottom: 2px solid #1976d2; padding-bottom: 10px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p style="color: #666;">{len(emails)} messages in thread</p>
    {emails_html}
</body>
</html>"""

    def _format_attachments_section(self, attachments: List[EmailAttachment]) -> str:
        """Format attachments section."""
        if not attachments:
            return ""
        items = "".join(f"<li>{a.filename} ({a.size_bytes:,} bytes)</li>" for a in attachments)
        return f"""
        <div class="attachments">
            <strong>Attachments ({len(attachments)}):</strong>
            <ul>{items}</ul>
        </div>"""

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text."""
        # Simple HTML to text conversion
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


# Singleton instance
email_ingestion_service = EmailIngestionService()
