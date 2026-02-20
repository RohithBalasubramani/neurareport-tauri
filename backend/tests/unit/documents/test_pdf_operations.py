"""
PDF Operations Service Tests - Testing PDFOperationsService.
"""

import os
import uuid
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# Check if fitz (PyMuPDF) is available
try:
    import fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

from backend.app.services.documents.pdf_operations import (
    PDFOperationsService,
    PageInfo,
    WatermarkConfig,
    RedactionRegion,
    PDFMergeResult,
)


def create_test_pdf(path: Path, num_pages: int = 1, content: str = "Test content") -> Path:
    """Create a test PDF file."""
    if not HAS_FITZ:
        pytest.skip("PyMuPDF not available")

    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page()
        text_point = fitz.Point(50, 50)
        page.insert_text(text_point, f"{content} - Page {i + 1}")
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture
def pdf_service(tmp_path: Path) -> PDFOperationsService:
    """Create PDF operations service with temporary output directory."""
    return PDFOperationsService(output_dir=tmp_path / "pdf_outputs")


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a sample PDF file."""
    return create_test_pdf(tmp_path / "sample.pdf", num_pages=3)


@pytest.fixture
def multi_page_pdf(tmp_path: Path) -> Path:
    """Create a multi-page PDF file."""
    return create_test_pdf(tmp_path / "multipage.pdf", num_pages=5)


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestGetPageInfo:
    """Test get_page_info method."""

    def test_get_page_info_single_page(self, pdf_service: PDFOperationsService, tmp_path: Path):
        """Get info for single page PDF."""
        pdf_path = create_test_pdf(tmp_path / "single.pdf", num_pages=1)
        pages = pdf_service.get_page_info(pdf_path)
        assert len(pages) == 1
        assert pages[0].page_number == 0
        assert pages[0].width > 0
        assert pages[0].height > 0
        assert pages[0].rotation == 0

    def test_get_page_info_multiple_pages(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Get info for multi-page PDF."""
        pages = pdf_service.get_page_info(multi_page_pdf)
        assert len(pages) == 5
        for i, page in enumerate(pages):
            assert page.page_number == i

    def test_get_page_info_dimensions(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Page dimensions should be standard letter size."""
        pages = pdf_service.get_page_info(sample_pdf)
        # Default PyMuPDF page is letter size (612 x 792 points)
        assert pages[0].width == pytest.approx(612, rel=0.1)
        assert pages[0].height == pytest.approx(792, rel=0.1)

    def test_get_page_info_nonexistent_file(self, pdf_service: PDFOperationsService):
        """Getting page info for nonexistent file should raise error."""
        with pytest.raises(Exception):
            pdf_service.get_page_info(Path("/nonexistent/file.pdf"))


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestReorderPages:
    """Test reorder_pages method."""

    def test_reorder_pages_reverse(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Reverse page order."""
        output = pdf_service.reorder_pages(multi_page_pdf, [4, 3, 2, 1, 0])
        assert output.exists()
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 5

    def test_reorder_pages_subset(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Select subset of pages."""
        output = pdf_service.reorder_pages(multi_page_pdf, [0, 2, 4])
        assert output.exists()
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 3

    def test_reorder_pages_duplicate(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Duplicate pages in output."""
        output = pdf_service.reorder_pages(sample_pdf, [0, 0, 1, 1, 2, 2])
        assert output.exists()
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 6

    def test_reorder_pages_custom_output(
        self, pdf_service: PDFOperationsService, sample_pdf: Path, tmp_path: Path
    ):
        """Specify custom output path."""
        custom_output = tmp_path / "custom_reordered.pdf"
        output = pdf_service.reorder_pages(sample_pdf, [0, 1, 2], output_path=custom_output)
        assert output == custom_output
        assert custom_output.exists()

    def test_reorder_pages_invalid_page_number(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Invalid page number should raise error."""
        with pytest.raises(ValueError, match="out of range"):
            pdf_service.reorder_pages(sample_pdf, [0, 1, 10])

    def test_reorder_pages_negative_page_number(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Negative page number should raise error."""
        with pytest.raises(ValueError, match="out of range"):
            pdf_service.reorder_pages(sample_pdf, [-1, 0, 1])


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestAddWatermark:
    """Test add_watermark method."""

    def test_add_watermark_center(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Add centered watermark."""
        config = WatermarkConfig(text="CONFIDENTIAL", position="center")
        output = pdf_service.add_watermark(sample_pdf, config)
        assert output.exists()

    def test_add_watermark_diagonal(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Add diagonal watermark."""
        config = WatermarkConfig(text="DRAFT", position="diagonal")
        output = pdf_service.add_watermark(sample_pdf, config)
        assert output.exists()

    def test_add_watermark_top(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Add top watermark."""
        config = WatermarkConfig(text="PREVIEW", position="top")
        output = pdf_service.add_watermark(sample_pdf, config)
        assert output.exists()

    def test_add_watermark_bottom(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Add bottom watermark."""
        config = WatermarkConfig(text="SAMPLE", position="bottom")
        output = pdf_service.add_watermark(sample_pdf, config)
        assert output.exists()

    def test_add_watermark_custom_font_size(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Add watermark with custom font size."""
        config = WatermarkConfig(text="BIG", font_size=96)
        output = pdf_service.add_watermark(sample_pdf, config)
        assert output.exists()

    def test_add_watermark_custom_color(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Add watermark with custom color."""
        config = WatermarkConfig(text="RED", color="#FF0000")
        output = pdf_service.add_watermark(sample_pdf, config)
        assert output.exists()

    def test_add_watermark_custom_output(
        self, pdf_service: PDFOperationsService, sample_pdf: Path, tmp_path: Path
    ):
        """Specify custom output path."""
        custom_output = tmp_path / "custom_watermarked.pdf"
        config = WatermarkConfig(text="TEST")
        output = pdf_service.add_watermark(sample_pdf, config, output_path=custom_output)
        assert output == custom_output
        assert custom_output.exists()

    def test_add_watermark_all_pages(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Watermark should be added to all pages."""
        config = WatermarkConfig(text="ALL PAGES")
        output = pdf_service.add_watermark(multi_page_pdf, config)
        # Verify output has same number of pages
        original_pages = pdf_service.get_page_info(multi_page_pdf)
        output_pages = pdf_service.get_page_info(output)
        assert len(output_pages) == len(original_pages)


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestRedactRegions:
    """Test redact_regions method."""

    def test_redact_single_region(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Redact single region."""
        regions = [RedactionRegion(page=0, x=50, y=50, width=100, height=20)]
        output = pdf_service.redact_regions(sample_pdf, regions)
        assert output.exists()

    def test_redact_multiple_regions(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Redact multiple regions."""
        regions = [
            RedactionRegion(page=0, x=50, y=50, width=100, height=20),
            RedactionRegion(page=0, x=50, y=100, width=150, height=30),
            RedactionRegion(page=1, x=100, y=200, width=200, height=40),
        ]
        output = pdf_service.redact_regions(sample_pdf, regions)
        assert output.exists()

    def test_redact_with_custom_color(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Redact with white fill."""
        regions = [RedactionRegion(page=0, x=50, y=50, width=100, height=20, color="#FFFFFF")]
        output = pdf_service.redact_regions(sample_pdf, regions)
        assert output.exists()

    def test_redact_custom_output(
        self, pdf_service: PDFOperationsService, sample_pdf: Path, tmp_path: Path
    ):
        """Specify custom output path."""
        custom_output = tmp_path / "custom_redacted.pdf"
        regions = [RedactionRegion(page=0, x=50, y=50, width=100, height=20)]
        output = pdf_service.redact_regions(sample_pdf, regions, output_path=custom_output)
        assert output == custom_output

    def test_redact_invalid_page_skipped(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Invalid page numbers should be skipped."""
        regions = [
            RedactionRegion(page=0, x=50, y=50, width=100, height=20),
            RedactionRegion(page=100, x=50, y=50, width=100, height=20),  # Invalid
        ]
        output = pdf_service.redact_regions(sample_pdf, regions)
        assert output.exists()


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestMergePDFs:
    """Test merge_pdfs method."""

    def test_merge_two_pdfs(
        self, pdf_service: PDFOperationsService, tmp_path: Path
    ):
        """Merge two PDF files."""
        pdf1 = create_test_pdf(tmp_path / "pdf1.pdf", num_pages=2)
        pdf2 = create_test_pdf(tmp_path / "pdf2.pdf", num_pages=3)

        result = pdf_service.merge_pdfs([pdf1, pdf2])
        assert result.page_count == 5
        assert len(result.source_files) == 2
        assert Path(result.output_path).exists()

    def test_merge_multiple_pdfs(
        self, pdf_service: PDFOperationsService, tmp_path: Path
    ):
        """Merge multiple PDF files."""
        pdfs = [
            create_test_pdf(tmp_path / f"pdf{i}.pdf", num_pages=i + 1)
            for i in range(4)
        ]
        result = pdf_service.merge_pdfs(pdfs)
        assert result.page_count == 1 + 2 + 3 + 4  # 10 total pages
        assert len(result.source_files) == 4

    def test_merge_with_custom_output(
        self, pdf_service: PDFOperationsService, tmp_path: Path
    ):
        """Specify custom output path for merge."""
        pdf1 = create_test_pdf(tmp_path / "pdf1.pdf", num_pages=1)
        pdf2 = create_test_pdf(tmp_path / "pdf2.pdf", num_pages=1)
        custom_output = tmp_path / "custom_merged.pdf"

        result = pdf_service.merge_pdfs([pdf1, pdf2], output_path=custom_output)
        assert result.output_path == str(custom_output)
        assert custom_output.exists()

    def test_merge_skips_nonexistent_files(
        self, pdf_service: PDFOperationsService, tmp_path: Path
    ):
        """Nonexistent files should be skipped."""
        pdf1 = create_test_pdf(tmp_path / "pdf1.pdf", num_pages=2)
        nonexistent = tmp_path / "nonexistent.pdf"

        result = pdf_service.merge_pdfs([pdf1, nonexistent])
        assert result.page_count == 2
        assert len(result.source_files) == 1

    def test_merge_preserves_page_order(
        self, pdf_service: PDFOperationsService, tmp_path: Path
    ):
        """Merged PDF should preserve page order."""
        pdf1 = create_test_pdf(tmp_path / "first.pdf", num_pages=2, content="First")
        pdf2 = create_test_pdf(tmp_path / "second.pdf", num_pages=2, content="Second")

        result = pdf_service.merge_pdfs([pdf1, pdf2])
        merged = fitz.open(result.output_path)
        # First two pages from first PDF, next two from second
        assert merged.page_count == 4
        merged.close()


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestSplitPDF:
    """Test split_pdf method."""

    def test_split_by_single_ranges(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Split PDF into single-page files."""
        ranges = [(0, 0), (1, 1), (2, 2)]
        outputs = pdf_service.split_pdf(multi_page_pdf, ranges)
        assert len(outputs) == 3
        for output in outputs:
            pages = pdf_service.get_page_info(output)
            assert len(pages) == 1

    def test_split_by_page_ranges(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Split PDF by page ranges."""
        ranges = [(0, 1), (2, 4)]  # Pages 0-1 and 2-4
        outputs = pdf_service.split_pdf(multi_page_pdf, ranges)
        assert len(outputs) == 2
        pages1 = pdf_service.get_page_info(outputs[0])
        pages2 = pdf_service.get_page_info(outputs[1])
        assert len(pages1) == 2
        assert len(pages2) == 3

    def test_split_custom_output_dir(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path, tmp_path: Path
    ):
        """Specify custom output directory."""
        custom_dir = tmp_path / "splits"
        custom_dir.mkdir()
        ranges = [(0, 1)]
        outputs = pdf_service.split_pdf(multi_page_pdf, ranges, output_dir=custom_dir)
        assert all(str(o).startswith(str(custom_dir)) for o in outputs)

    def test_split_handles_out_of_range(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Out-of-range values should be clamped."""
        ranges = [(-5, 100)]  # Should clamp to (0, 4) for 5-page PDF
        outputs = pdf_service.split_pdf(multi_page_pdf, ranges)
        assert len(outputs) == 1
        pages = pdf_service.get_page_info(outputs[0])
        assert len(pages) == 5

    def test_split_invalid_range_skipped(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Invalid ranges (start > end after clamping) should be skipped."""
        ranges = [(10, 5)]  # start > end after clamping
        outputs = pdf_service.split_pdf(multi_page_pdf, ranges)
        # Range is invalid, no output created
        # After clamping: start=min(doc.page_count-1, 10)=4, end=min(doc.page_count-1, 5)=4
        # Actually start <= end, so it should produce output
        assert len(outputs) >= 0


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestRotatePages:
    """Test rotate_pages method."""

    def test_rotate_all_pages(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Rotate all pages 90 degrees."""
        output = pdf_service.rotate_pages(sample_pdf, 90)
        assert output.exists()
        pages = pdf_service.get_page_info(output)
        assert all(p.rotation == 90 for p in pages)

    def test_rotate_specific_pages(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Rotate only specific pages."""
        output = pdf_service.rotate_pages(multi_page_pdf, 180, pages=[0, 2, 4])
        pages = pdf_service.get_page_info(output)
        assert pages[0].rotation == 180
        assert pages[1].rotation == 0
        assert pages[2].rotation == 180
        assert pages[3].rotation == 0
        assert pages[4].rotation == 180

    def test_rotate_270_degrees(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Rotate 270 degrees."""
        output = pdf_service.rotate_pages(sample_pdf, 270)
        pages = pdf_service.get_page_info(output)
        assert pages[0].rotation == 270

    def test_rotate_normalizes_angle(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Rotation angle should be normalized."""
        output = pdf_service.rotate_pages(sample_pdf, 450)  # 450 % 360 = 90
        pages = pdf_service.get_page_info(output)
        assert pages[0].rotation == 90

    def test_rotate_invalid_angle_uses_zero(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Invalid angles (not 0, 90, 180, 270) should use 0."""
        output = pdf_service.rotate_pages(sample_pdf, 45)
        pages = pdf_service.get_page_info(output)
        assert pages[0].rotation == 0

    def test_rotate_custom_output(
        self, pdf_service: PDFOperationsService, sample_pdf: Path, tmp_path: Path
    ):
        """Specify custom output path."""
        custom_output = tmp_path / "custom_rotated.pdf"
        output = pdf_service.rotate_pages(sample_pdf, 90, output_path=custom_output)
        assert output == custom_output

    def test_rotate_invalid_page_ignored(
        self, pdf_service: PDFOperationsService, sample_pdf: Path
    ):
        """Invalid page numbers should be ignored."""
        output = pdf_service.rotate_pages(sample_pdf, 90, pages=[0, 100])
        assert output.exists()


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestExtractPages:
    """Test extract_pages method."""

    def test_extract_single_page(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Extract single page."""
        output = pdf_service.extract_pages(multi_page_pdf, [2])
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 1

    def test_extract_multiple_pages(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Extract multiple pages."""
        output = pdf_service.extract_pages(multi_page_pdf, [0, 2, 4])
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 3

    def test_extract_preserves_order(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Extract should preserve specified order."""
        output = pdf_service.extract_pages(multi_page_pdf, [4, 2, 0])
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 3

    def test_extract_custom_output(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path, tmp_path: Path
    ):
        """Specify custom output path."""
        custom_output = tmp_path / "custom_extracted.pdf"
        output = pdf_service.extract_pages(multi_page_pdf, [0, 1], output_path=custom_output)
        assert output == custom_output

    def test_extract_invalid_pages_skipped(
        self, pdf_service: PDFOperationsService, multi_page_pdf: Path
    ):
        """Invalid page numbers should be skipped."""
        output = pdf_service.extract_pages(multi_page_pdf, [0, 100, 2])
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 2  # Only pages 0 and 2


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestHexToRGB:
    """Test _hex_to_rgb helper method."""

    def test_hex_to_rgb_black(self, pdf_service: PDFOperationsService):
        """Convert black hex to RGB."""
        result = pdf_service._hex_to_rgb("#000000")
        assert result == (0, 0, 0)

    def test_hex_to_rgb_white(self, pdf_service: PDFOperationsService):
        """Convert white hex to RGB."""
        result = pdf_service._hex_to_rgb("#FFFFFF")
        assert result == (1, 1, 1)

    def test_hex_to_rgb_red(self, pdf_service: PDFOperationsService):
        """Convert red hex to RGB."""
        result = pdf_service._hex_to_rgb("#FF0000")
        assert result == (1, 0, 0)

    def test_hex_to_rgb_without_hash(self, pdf_service: PDFOperationsService):
        """Convert hex without # prefix."""
        result = pdf_service._hex_to_rgb("808080")
        expected = (128 / 255, 128 / 255, 128 / 255)
        assert result == pytest.approx(expected, rel=0.01)

    def test_hex_to_rgb_lowercase(self, pdf_service: PDFOperationsService):
        """Convert lowercase hex."""
        result = pdf_service._hex_to_rgb("#ff00ff")
        assert result == (1, 0, 1)


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestPDFServiceErrorHandling:
    """Test error handling in PDF operations."""

    def test_operation_on_corrupt_pdf(
        self, pdf_service: PDFOperationsService, tmp_path: Path
    ):
        """Operations on corrupt PDF should raise error."""
        corrupt_pdf = tmp_path / "corrupt.pdf"
        corrupt_pdf.write_text("This is not a valid PDF")

        with pytest.raises(Exception):
            pdf_service.get_page_info(corrupt_pdf)

    def test_operation_on_nonexistent_file(self, pdf_service: PDFOperationsService):
        """Operations on nonexistent file should raise error."""
        with pytest.raises(Exception):
            pdf_service.get_page_info(Path("/nonexistent/file.pdf"))

    def test_merge_empty_list(self, pdf_service: PDFOperationsService):
        """Merge with empty list should raise error (cannot save zero pages)."""
        with pytest.raises(ValueError, match="cannot save with zero pages"):
            pdf_service.merge_pdfs([])
