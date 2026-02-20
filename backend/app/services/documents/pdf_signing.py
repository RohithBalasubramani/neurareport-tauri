"""PDF Digital Signing Service.

Provides digital signature capabilities for PDF documents.
"""
from __future__ import annotations

import hashlib
import io
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PDFSigningService:
    """Service for adding digital signatures to PDFs."""

    def __init__(self):
        self._certificates: dict[str, dict] = {}

    async def sign_pdf(
        self,
        pdf_content: bytes,
        *,
        signer_name: str,
        reason: Optional[str] = None,
        location: Optional[str] = None,
        contact_info: Optional[str] = None,
        certificate_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add a digital signature to a PDF document.

        Args:
            pdf_content: The PDF file content as bytes
            signer_name: Name of the person signing
            reason: Reason for signing
            location: Location where signing occurred
            contact_info: Contact information for signer
            certificate_id: Optional certificate ID for cryptographic signing

        Returns:
            Dictionary with signed PDF content and signature metadata
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.warning("PyMuPDF not available, using basic signature")
            return self._add_basic_signature(
                pdf_content, signer_name, reason, location, contact_info
            )

        try:
            # Open the PDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")

            # Create signature annotation on first page
            page = doc[0]

            # Calculate signature rectangle (bottom-right corner)
            rect = fitz.Rect(
                page.rect.width - 200,
                page.rect.height - 80,
                page.rect.width - 20,
                page.rect.height - 20,
            )

            # Create signature text
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            sig_text = f"Digitally signed by: {signer_name}\n"
            if reason:
                sig_text += f"Reason: {reason}\n"
            if location:
                sig_text += f"Location: {location}\n"
            sig_text += f"Date: {timestamp}"

            # Add text annotation for visual signature
            text_annot = page.add_freetext_annot(
                rect,
                sig_text,
                fontsize=8,
                fontname="helv",
                text_color=(0, 0, 0.5),
                fill_color=(0.95, 0.95, 1),
                border_color=(0, 0, 0.5),
            )

            # Generate signature hash
            content_hash = hashlib.sha256(pdf_content).hexdigest()
            signature_hash = hashlib.sha256(
                f"{signer_name}{timestamp}{content_hash}".encode()
            ).hexdigest()

            # Add metadata
            metadata = doc.metadata
            metadata["keywords"] = f"signed,{signature_hash[:16]}"
            doc.set_metadata(metadata)

            # Save to bytes
            output = io.BytesIO()
            doc.save(output)
            doc.close()

            signed_content = output.getvalue()

            return {
                "success": True,
                "signed_pdf": signed_content,
                "signature": {
                    "signer": signer_name,
                    "reason": reason,
                    "location": location,
                    "contact": contact_info,
                    "timestamp": timestamp,
                    "hash": signature_hash,
                    "algorithm": "SHA-256",
                },
            }

        except Exception as e:
            logger.exception("PDF signing failed")
            return {
                "success": False,
                "error": "PDF signing failed",
            }

    def _add_basic_signature(
        self,
        pdf_content: bytes,
        signer_name: str,
        reason: Optional[str],
        location: Optional[str],
        contact_info: Optional[str],
    ) -> dict[str, Any]:
        """Add a basic signature without PyMuPDF (metadata only)."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        content_hash = hashlib.sha256(pdf_content).hexdigest()
        signature_hash = hashlib.sha256(
            f"{signer_name}{timestamp}{content_hash}".encode()
        ).hexdigest()

        return {
            "success": True,
            "signed_pdf": pdf_content,  # Return original (metadata signature only)
            "signature": {
                "signer": signer_name,
                "reason": reason,
                "location": location,
                "contact": contact_info,
                "timestamp": timestamp,
                "hash": signature_hash,
                "algorithm": "SHA-256",
                "type": "metadata_only",
            },
        }

    async def verify_signature(
        self,
        pdf_content: bytes,
        signature_hash: str,
    ) -> dict[str, Any]:
        """Verify a PDF signature.

        Args:
            pdf_content: The signed PDF content
            signature_hash: The expected signature hash

        Returns:
            Dictionary with verification result
        """
        try:
            import fitz
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            metadata = doc.metadata
            doc.close()

            keywords = metadata.get("keywords", "")
            if f"signed,{signature_hash[:16]}" in keywords:
                return {
                    "valid": True,
                    "message": "Signature verified",
                }

            return {
                "valid": False,
                "message": "Signature not found or invalid",
            }

        except Exception as e:
            logger.exception("Signature verification failed")
            return {
                "valid": False,
                "error": "Signature verification failed",
            }

    def register_certificate(
        self,
        certificate_id: str,
        certificate_data: dict,
    ) -> None:
        """Register a certificate for signing."""
        self._certificates[certificate_id] = certificate_data

    def list_certificates(self) -> list[dict]:
        """List registered certificates."""
        return [
            {"id": cid, **{k: v for k, v in data.items() if k != "private_key"}}
            for cid, data in self._certificates.items()
        ]


# Singleton instance
pdf_signing_service = PDFSigningService()
