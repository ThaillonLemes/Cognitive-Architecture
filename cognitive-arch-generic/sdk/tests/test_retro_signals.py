# sdk/tests/test_retro_signals.py
# PURPOSE: Unit tests for retro_signals.py extraction logic.
# DEPS:    pytest, sdk/retro_signals, sdk/retro_signal_schema

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from retro_signal_schema import RetroSignal
from retro_signals import extract_signal, _extract_frontmatter


# ---------------------------------------------------------------------------
# Synthetic retrospective fixtures
# ---------------------------------------------------------------------------

_RETRO_FULL = """\
---
id: block-042
manifest: manifests/block-042-example.md
status: done
gates_passed: 3/4
completed_at: 2026-05-20T10:00Z
agent: implementer
commit: abc1234
duration_actual_days: 1
actual_duration_hours: 3.5
duration_source: manual
tok_estimated: ~800
tok_src: estimated
---

# Block 042 Retrospective — Example

## 7. Issues / surprises

Violated P3 (single source of truth) by duplicating config value.

## 8. Files actually touched

Added unexpectedly: sdk/helper.py
"""

_RETRO_MINIMAL = """\
---
id: block-001
status: done
gates_passed: 2/2
completed_at: 2026-04-01T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 1
duration_source: estimated
tok_estimated: ~100
tok_src: estimated
---
# Block 001 Retrospective

## 8. Files actually touched

As manifest.
"""

_RETRO_NO_HOURS = """\
---
id: block-010
status: done
gates_passed: 4/4
completed_at: 2026-05-01T00:00Z
agent: implementer
commit: -
duration_actual_days: 2
tok_estimated: ~200
tok_src: estimated
---
# Block 010 Retrospective

## 8. Files actually touched

As manifest.
"""

_RETRO_FORCED = """\
---
id: block-020
status: forced
gates_passed: 1/2
completed_at: 2026-05-10T00:00Z
agent: implementer
commit: -
duration_actual_days: 1
actual_duration_hours: 2
duration_source: manual
tok_estimated: ~300
tok_src: estimated
---
# Block 020 — force-pass applied to gate xyz
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _make_tmp_retro(tmp_path, content, filename="block-042-example.md"):
    p = tmp_path / "blocks" / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_extract_frontmatter():
    fm = _extract_frontmatter(_RETRO_FULL)
    assert "id: block-042" in fm
    assert "gates_passed: 3/4" in fm


def test_full_retro_gates(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_FULL)
    sig = extract_signal(p, tmp_path)
    assert sig is not None
    assert sig.block_id == "block-042"
    assert sig.gates_passed_count == 3
    assert sig.gates_total == 4
    assert sig.gate_failures == 1


def test_full_retro_duration(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_FULL)
    sig = extract_signal(p, tmp_path)
    assert sig.duration_actual_h == 3.5
    assert sig.duration_source == "manual"


def test_full_retro_axiom_violation(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_FULL)
    sig = extract_signal(p, tmp_path)
    assert "P3" in sig.axioms_violated


def test_full_retro_scope_expansion(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_FULL)
    sig = extract_signal(p, tmp_path)
    assert sig.scope_expansion is True


def test_minimal_retro_no_scope_expansion(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_MINIMAL, "block-001-foo.md")
    sig = extract_signal(p, tmp_path)
    assert sig is not None
    assert sig.scope_expansion is False
    assert sig.block_id == "block-001"


def test_missing_duration_hours(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_NO_HOURS, "block-010-foo.md")
    sig = extract_signal(p, tmp_path)
    assert sig.duration_actual_h is None
    assert "actual_duration_hours missing" in sig.parse_warnings


def test_forced_pass_detection(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_FORCED, "block-020-foo.md")
    sig = extract_signal(p, tmp_path)
    assert sig.forced_pass is True


def test_retro_signal_duration_delta(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_FULL)
    # No manifest => est_days=None => delta_ratio=None
    sig = extract_signal(p, tmp_path)
    assert sig.duration_delta_ratio is None  # no manifest in tmp_path


def test_duration_delta_ratio_computed():
    sig = RetroSignal(
        block_id="block-999", phase="phase-1", tier="M", kind="implementation",
        duration_actual_h=12.0, duration_estimated_days=1.0, duration_source="manual",
    )
    # 12h actual / (1.0 days * 8h) = 1.5 → ratio correct; over_estimate uses > 1.5 (strict)
    assert abs(sig.duration_delta_ratio - 1.5) < 0.01
    assert sig.over_estimate is False  # 1.5 is not > 1.5 (boundary); use 12.1h to trigger True


def test_closed_at_extraction(tmp_path):
    p = _make_tmp_retro(tmp_path, _RETRO_FULL)
    sig = extract_signal(p, tmp_path)
    assert sig.closed_at == "2026-05-20T10:00Z"
