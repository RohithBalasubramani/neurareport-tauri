from __future__ import annotations

import zipfile

import pytest

from backend.app.services.utils.zip_tools import extract_zip_to_dir


def _create_zip(zip_path, files):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)


def test_extract_zip_to_dir_enforces_entry_limit(tmp_path):
    zip_path = tmp_path / "test.zip"
    files = {f"file_{i}.txt": b"data" for i in range(3)}
    _create_zip(zip_path, files)

    with pytest.raises(ValueError):
        extract_zip_to_dir(zip_path, tmp_path / "out", max_entries=2)


def test_extract_zip_to_dir_enforces_uncompressed_limit(tmp_path):
    zip_path = tmp_path / "test.zip"
    files = {"big.txt": b"a" * 1024}
    _create_zip(zip_path, files)

    with pytest.raises(ValueError):
        extract_zip_to_dir(zip_path, tmp_path / "out", max_uncompressed_bytes=512)
