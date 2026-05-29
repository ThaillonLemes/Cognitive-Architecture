# PURPOSE: Shared UTF-8 stdout/stderr guard so CLI tools never crash on Windows cp1252 consoles.
# INPUTS:  none (operates on sys.stdout/sys.stderr)
# OUTPUTS: reconfigured streams (UTF-8, errors='replace')
# DEPS:    stdlib only (sys, io)
# SEE:     phases/phase-23.md block-136, sdk/tests/test_cli_smoke.py

from __future__ import annotations

import io
import sys


def force_utf8() -> None:
    """
    Force sys.stdout / sys.stderr to UTF-8 with errors='replace'.

    Why errors='replace' matters: on a redirected pipe under a cp1252 locale,
    Python fails to *flush* un-encodable buffered output at interpreter
    shutdown (exit code 120) and raises UnicodeEncodeError mid-run on chars
    like U+2192 (->). 'replace' guarantees encoding can never raise, so neither
    failure mode can occur. Idempotent and safe to call from any CLI entry point.
    """
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None:
            continue
        # Fast path: modern Python streams support reconfigure()
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
            continue
        except (AttributeError, ValueError):
            pass
        # Fallback: wrap the underlying binary buffer
        buffer = getattr(stream, "buffer", None)
        if buffer is not None:
            try:
                setattr(sys, name, io.TextIOWrapper(
                    buffer, encoding="utf-8", errors="replace"
                ))
            except Exception:
                pass  # never let stdout-safety crash the tool
