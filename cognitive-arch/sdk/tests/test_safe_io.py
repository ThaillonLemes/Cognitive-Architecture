# PURPOSE: Tests for sdk/safe_io.py (block-136)
# INPUTS:  monkeypatched sys.stdout
# OUTPUTS: assertions that force_utf8 is idempotent and never raises
# DEPS:    pytest, io, sys
# SEE:     sdk/safe_io.py, phases/phase-23.md block-136

import io
import sys
from pathlib import Path

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from safe_io import force_utf8


def test_force_utf8_is_idempotent():
    force_utf8()
    force_utf8()  # second call must not raise


def test_force_utf8_sets_utf8_on_wrapped_stream(monkeypatch):
    raw = io.BytesIO()
    wrapper = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", wrapper)
    force_utf8()
    # After force_utf8, writing a non-cp1252 char must not raise
    sys.stdout.write("arrow -> → ok\n")
    sys.stdout.flush()


def test_force_utf8_survives_none_stream(monkeypatch):
    monkeypatch.setattr(sys, "stdout", None)
    force_utf8()  # must not raise even if a stream is None


def test_unencodable_char_does_not_raise(monkeypatch):
    raw = io.BytesIO()
    wrapper = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", wrapper)
    force_utf8()
    # U+2192 is not in cp1252; with errors='replace' (utf-8) it encodes fine
    sys.stdout.write("→")
    sys.stdout.flush()
    raw.seek(0)
    assert raw.read()  # something was written, no exception
