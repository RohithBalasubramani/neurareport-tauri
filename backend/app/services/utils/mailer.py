from __future__ import annotations

import logging
import mimetypes
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, Sequence

logger = logging.getLogger("neura.mailer")


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("invalid_mail_port", extra={"event": "invalid_mail_port", "env": name, "value": raw})
        return default


@dataclass(frozen=True)
class MailerConfig:
    host: str | None
    port: int
    username: str | None
    password: str | None
    sender: str | None
    use_tls: bool
    enabled: bool


def _load_mailer_config() -> MailerConfig:
    host = os.getenv("NEURA_MAIL_HOST")
    sender = os.getenv("NEURA_MAIL_SENDER")
    username = os.getenv("NEURA_MAIL_USERNAME")
    password = os.getenv("NEURA_MAIL_PASSWORD")
    port = _env_int("NEURA_MAIL_PORT", 587)
    use_tls = _env_bool("NEURA_MAIL_USE_TLS", True)
    enabled = bool(host and sender)
    if not enabled:
        logger.info(
            "mail_disabled",
            extra={"event": "mail_disabled", "reason": "host_or_sender_missing", "host": bool(host), "sender": bool(sender)},
        )
    return MailerConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        sender=sender,
        use_tls=use_tls,
        enabled=enabled,
    )


MAILER_CONFIG = _load_mailer_config()


def refresh_mailer_config() -> MailerConfig:
    global MAILER_CONFIG
    MAILER_CONFIG = _load_mailer_config()
    return MAILER_CONFIG


def _normalize_recipients(recipients: Iterable[str] | None) -> list[str]:
    if not recipients:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in recipients:
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def send_report_email(
    *,
    to_addresses: Sequence[str],
    subject: str,
    body: str,
    attachments: Sequence[Path] | None = None,
) -> bool:
    config = MAILER_CONFIG
    recipients = _normalize_recipients(to_addresses)
    if not recipients:
        return False
    if not config.enabled or not config.host or not config.sender:
        logger.warning(
            "mail_not_configured",
            extra={"event": "mail_not_configured", "recipients": len(recipients)},
        )
        return False

    message = EmailMessage()
    message["From"] = config.sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)

    if attachments:
        for path in attachments:
            if not path:
                continue
            try:
                resolved = Path(path).resolve(strict=True)
            except (FileNotFoundError, OSError):
                logger.warning(
                    "mail_attachment_missing",
                    extra={"event": "mail_attachment_missing", "path": str(path)},
                )
                continue
            mime_type, encoding = mimetypes.guess_type(str(resolved))
            maintype = "application"
            subtype = "octet-stream"
            if mime_type and "/" in mime_type:
                maintype, subtype = mime_type.split("/", 1)
            try:
                data = resolved.read_bytes()
            except OSError:
                logger.warning(
                    "mail_attachment_read_failed",
                    extra={"event": "mail_attachment_read_failed", "path": str(resolved)},
                )
                continue
            message.add_attachment(data, maintype=maintype, subtype=subtype, filename=resolved.name)

    try:
        if config.use_tls:
            with smtplib.SMTP(config.host, config.port, timeout=15) as client:
                context = ssl.create_default_context()
                client.starttls(context=context)
                if config.username and config.password:
                    client.login(config.username, config.password)
                client.send_message(message)
        else:
            with smtplib.SMTP(config.host, config.port, timeout=15) as client:
                if config.username and config.password:
                    client.login(config.username, config.password)
                client.send_message(message)
    except Exception:
        logger.exception(
            "mail_send_failed",
            extra={"event": "mail_send_failed", "recipients": len(recipients)},
        )
        return False

    logger.info(
        "mail_sent",
        extra={"event": "mail_sent", "recipients": len(recipients)},
    )
    return True
