from backend.app.services.extraction import pdf_extractors
from backend.app.services.extraction.pdf_extractors import ExtractionResult


def test_extract_pdf_tables_cache(monkeypatch, tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%fake\n")

    calls = []

    class FakeExtractor:
        def is_available(self):
            return True

        def extract_tables(self, pdf_path, pages, config=None):
            calls.append(str(pdf_path))
            return ExtractionResult(
                tables=[],
                text="",
                page_count=1,
                method="fake",
                errors=[],
            )

    monkeypatch.setattr(pdf_extractors, "_CACHE_TTL_SECONDS", 60)
    monkeypatch.setattr(pdf_extractors, "_CACHE_MAX_ITEMS", 10)
    monkeypatch.setattr(pdf_extractors, "_CACHE_DEDUPE_ENABLED", True)
    monkeypatch.setattr(pdf_extractors, "_CACHE_WAIT_SECONDS", 0.1)

    pdf_extractors._EXTRACTION_CACHE.clear()
    pdf_extractors._EXTRACTION_INFLIGHT.clear()

    monkeypatch.setattr(pdf_extractors, "EXTRACTORS", {"fake": FakeExtractor})

    first = pdf_extractors.extract_pdf_tables(pdf_path, method="fake")
    second = pdf_extractors.extract_pdf_tables(pdf_path, method="fake")

    assert first.method == "fake"
    assert second.method == "fake"
    assert len(calls) == 1
    assert second.metadata.get("cache_hit") is True
