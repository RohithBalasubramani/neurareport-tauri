import os
import threading
import time
from pathlib import Path


from backend.app.services.utils.lock import acquire_template_lock  # noqa: E402


def test_acquire_template_lock_non_blocking(tmp_path: Path):
    tdir = tmp_path / "template"
    tdir.mkdir(parents=True, exist_ok=True)

    with acquire_template_lock(tdir, "mapping"):
        with acquire_template_lock(tdir, "mapping"):
            pass
    assert not list(tdir.glob(".lock.*")), "locks are disabled so no files should be created"


def test_acquire_template_lock_allows_release(tmp_path: Path):
    tdir = tmp_path / "template"
    tdir.mkdir(parents=True, exist_ok=True)

    first_ready = threading.Event()
    second_started = threading.Event()
    results = []

    def first():
        with acquire_template_lock(tdir, "run"):
            first_ready.set()
            second_started.wait(timeout=1)
            time.sleep(0.1)
            results.append("first")

    def second():
        first_ready.wait(timeout=1)
        with acquire_template_lock(tdir, "run"):
            results.append("second")
        second_started.set()

    t1 = threading.Thread(target=first)
    t2 = threading.Thread(target=second)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert "first" in results
    assert "second" in results
    assert not list(tdir.glob(".lock.*")), "locks are disabled so no files should be created"
