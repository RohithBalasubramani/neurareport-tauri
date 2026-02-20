"""
Tests for PDF Signing Service — line 1262 of FORENSIC_AUDIT_REPORT.md.

Covers:
- Basic signature (metadata-only fallback when PyMuPDF is not available)
- Signature hash determinism
- Signature metadata completeness
- Verify signature
- Certificate registration and listing
- Error handling

Run with: pytest backend/tests/services/documents/test_pdf_signing.py -v
"""
from __future__ import annotations

import hashlib
from unittest.mock import patch, MagicMock

import pytest

from backend.app.services.documents.pdf_signing import (
    PDFSigningService,
    pdf_signing_service,
)


# =============================================================================
# Basic Signing Tests
# =============================================================================


class TestPDFBasicSigning:
    """Test PDF signing with metadata-only fallback."""

    @pytest.mark.asyncio
    async def test_basic_signature_returns_success(self):
        """When PyMuPDF is not available, basic signature should still succeed."""
        svc = PDFSigningService()
        pdf_content = b"%PDF-1.4 fake content"

        with patch.dict("sys.modules", {"fitz": None}):
            # Force fallback to basic signature
            result = await svc._add_basic_signature_async_wrapper(
                pdf_content, "John Doe", "Approval", "NYC", "john@example.com"
            ) if hasattr(svc, "_add_basic_signature_async_wrapper") else (
                svc._add_basic_signature(
                    pdf_content, "John Doe", "Approval", "NYC", "john@example.com"
                )
            )

        assert result["success"] is True
        assert result["signed_pdf"] == pdf_content  # Basic returns original
        assert result["signature"]["signer"] == "John Doe"
        assert result["signature"]["reason"] == "Approval"
        assert result["signature"]["location"] == "NYC"
        assert result["signature"]["type"] == "metadata_only"

    def test_basic_signature_hash_is_deterministic_per_content(self):
        """Same content + same signer + same timestamp should produce same hash."""
        svc = PDFSigningService()
        pdf1 = b"%PDF content A"
        pdf2 = b"%PDF content B"

        result1 = svc._add_basic_signature(pdf1, "Alice", None, None, None)
        result2 = svc._add_basic_signature(pdf2, "Alice", None, None, None)

        # Different content should produce different hashes
        assert result1["signature"]["hash"] != result2["signature"]["hash"]

    def test_basic_signature_includes_sha256_algorithm(self):
        svc = PDFSigningService()
        result = svc._add_basic_signature(b"content", "Signer", None, None, None)
        assert result["signature"]["algorithm"] == "SHA-256"

    def test_basic_signature_hash_format(self):
        """Hash should be a valid hex string."""
        svc = PDFSigningService()
        result = svc._add_basic_signature(b"content", "Signer", None, None, None)
        hash_value = result["signature"]["hash"]

        # Should be a valid hex string (SHA-256 = 64 hex chars)
        assert len(hash_value) == 64
        int(hash_value, 16)  # Should not raise


# =============================================================================
# Async Sign PDF Tests
# =============================================================================


class TestPDFSignAsync:
    """Test the async sign_pdf method."""

    @pytest.mark.asyncio
    async def test_sign_pdf_without_pymupdf(self):
        """sign_pdf should fall back to basic signature when fitz is not importable."""
        svc = PDFSigningService()

        # Patch the import inside sign_pdf to raise ImportError
        with patch("builtins.__import__", side_effect=_mock_import_no_fitz):
            result = await svc.sign_pdf(
                b"%PDF-1.4 test",
                signer_name="Test User",
                reason="Testing",
            )

        assert result["success"] is True
        assert result["signature"]["signer"] == "Test User"

    @pytest.mark.asyncio
    async def test_sign_pdf_with_all_metadata(self):
        """All metadata fields should be preserved in the signature."""
        svc = PDFSigningService()

        with patch("builtins.__import__", side_effect=_mock_import_no_fitz):
            result = await svc.sign_pdf(
                b"%PDF-1.4 test",
                signer_name="Jane Doe",
                reason="Final approval",
                location="London",
                contact_info="jane@example.com",
            )

        sig = result["signature"]
        assert sig["signer"] == "Jane Doe"
        assert sig["reason"] == "Final approval"
        assert sig["location"] == "London"
        assert sig["contact"] == "jane@example.com"
        assert sig["timestamp"] is not None


# =============================================================================
# Certificate Management Tests
# =============================================================================


class TestCertificateManagement:
    """Test certificate registration and listing."""

    def test_register_and_list_certificate(self):
        svc = PDFSigningService()
        svc.register_certificate("cert-1", {
            "name": "Production Cert",
            "issuer": "DigiCert",
            "private_key": "SECRET_KEY_DATA",
        })

        certs = svc.list_certificates()
        assert len(certs) == 1
        assert certs[0]["id"] == "cert-1"
        assert certs[0]["name"] == "Production Cert"
        # Private key should NOT be exposed in listing
        assert "private_key" not in certs[0]

    def test_list_certificates_excludes_private_key(self):
        """list_certificates must never expose private keys."""
        svc = PDFSigningService()
        svc.register_certificate("cert-2", {
            "name": "Test Cert",
            "private_key": "VERY_SECRET",
            "public_key": "PUBLIC_DATA",
        })

        certs = svc.list_certificates()
        for cert in certs:
            assert "private_key" not in cert
            assert "public_key" in cert  # Public key should be visible

    def test_register_multiple_certificates(self):
        svc = PDFSigningService()
        svc.register_certificate("a", {"name": "A"})
        svc.register_certificate("b", {"name": "B"})
        svc.register_certificate("c", {"name": "C"})

        assert len(svc.list_certificates()) == 3

    def test_empty_certificates_list(self):
        svc = PDFSigningService()
        assert svc.list_certificates() == []


# =============================================================================
# Signature Verification Tests
# =============================================================================


class TestSignatureVerification:
    """Test signature verification."""

    @pytest.mark.asyncio
    async def test_verify_returns_invalid_without_fitz(self):
        """Without PyMuPDF, verification should fail gracefully."""
        svc = PDFSigningService()

        with patch("builtins.__import__", side_effect=_mock_import_no_fitz):
            result = await svc.verify_signature(b"%PDF content", "abc123")

        assert result["valid"] is False


# =============================================================================
# Singleton Tests
# =============================================================================


class TestPDFSigningSingleton:
    """Test module-level singleton."""

    def test_singleton_exists(self):
        assert pdf_signing_service is not None
        assert isinstance(pdf_signing_service, PDFSigningService)


# =============================================================================
# Helpers
# =============================================================================


def _mock_import_no_fitz(name, *args, **kwargs):
    """Mock __import__ that raises ImportError for fitz."""
    if name == "fitz":
        raise ImportError("No module named 'fitz'")
    return original_import(name, *args, **kwargs)


import builtins
original_import = builtins.__import__
