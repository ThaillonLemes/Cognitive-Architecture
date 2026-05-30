# PURPOSE: Tests for the block-146 wiring — gate_result HALT accessor, the
#          session_start.run_invariant_check runner, and the invariant-check
#          registry row that lets the checker run every session.
# INPUTS:  tmp_path; a synthetic-but-consistent arch root (healthy_arch) seeded
#          with/without one critical drift; the REAL governance/tools-registry.yaml.
# OUTPUTS: assertions that gate_result HALTs on criticals + passes when clean,
#          that run_invariant_check returns (bool, count-string), and that the
#          registry now parses an `invariant-check` id.
# DEPS:    pytest, pathlib, invariant_check + session_start modules.
# SEE:     sdk/invariant_check.py (gate_result), sdk/session_start.py
#          (run_invariant_check + TOOL_RUNNERS), manifests/block-146-wire-gate.md

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import invariant_check as ic
import session_start
from invariant_schema import Violation

_ARCH_ROOT = _SDK_DIR.parent  # the real cognitive-arch root


# ---------------------------------------------------------------------------
# Builder — a fully-consistent arch root (every invariant clean). Mirrors the
# builder in test_invariant_check.py; kept local so this file stands alone. The
# registry is generated from the LIVE TOOL_RUNNERS, so it stays INV4-clean even
# as runners (incl. invariant-check) are added.
# ---------------------------------------------------------------------------

def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _immutable_doc(name: str) -> str:
    return f"---\nid: {name}\nprotection: immutable\n---\n\n# {name}\n"


def _retro(block_id: str, *, tier: str = "M", hours: float = 2.0) -> str:
    return (
        f"---\nid: {block_id}\nstatus: done\ntier: {tier}\n"
        f"actual_duration_hours: {hours}\n---\n\n# {block_id} retro\n"
    )


def _manifest(block_id: str, *, tier: str = "M") -> str:
    return f"---\nid: {block_id}\ntier: {tier}\n---\n\n# {block_id} manifest\n"


def healthy_arch(tmp_path: Path) -> Path:
    """A small but fully-consistent arch root — no invariant fires."""
    root = tmp_path / "arch"

    # INV1: one immutable file, present in the lock.
    _write(root / "PROTOCOLS.md", _immutable_doc("PROTOCOLS"))
    _write(root / ".integrity.lock", "# lock\nPROTOCOLS.md  sha256:" + ("a" * 64) + "\n")

    # INV2/INV3/INV5: two done blocks, both with tier+duration retros + manifests.
    _write(
        root / "blocks" / "BLOCK_LOG.md",
        "# BLOCK_LOG\nblock-001 done - 2026-05-20\nblock-002 done - 2026-05-21\n",
    )
    _write(root / "blocks" / "block-001-alpha.md", _retro("block-001"))
    _write(root / "blocks" / "block-002-beta.md", _retro("block-002"))
    _write(root / "manifests" / "block-001-alpha.md", _manifest("block-001"))
    _write(root / "manifests" / "block-002-beta.md", _manifest("block-002"))

    # INV4: registry covers every live TOOL_RUNNERS key (incl. invariant-check).
    reg_lines = ["schema_version: \"1.0\"", "tools:"]
    for tid in session_start.TOOL_RUNNERS:
        reg_lines.append(f"  - id: {tid}")
        reg_lines.append("    name: \"x\"")
    _write(root / "governance" / "tools-registry.yaml", "\n".join(reg_lines) + "\n")

    # INV5: last_block == highest done; next points at an unstarted block.
    _write(root / "STATE.md", "# STATE\np:1 status:active last_block:block-002 next:block-003\n")
    _write(root / "NEXT.md", "# NEXT\nstatus:active next_action:block-003\n")

    # INV6: one proposal, indexed both ways.
    _write(root / "governance" / "proposals" / "2026-05-29-foo.md", "---\nstatus: pending\n---\n# foo\n")
    _write(
        root / "governance" / "proposals" / "index.md",
        "# Proposals Index\n\n| Date | ID | Status |\n|------|----|--------|\n"
        "| 2026-05-29 | [foo](governance/proposals/2026-05-29-foo.md) | pending |\n",
    )
    return root


# ---------------------------------------------------------------------------
# gate_result — the block-close HALT accessor.
# ---------------------------------------------------------------------------

class TestGateResult:
    def test_clean_arch_is_ok_with_no_criticals(self, tmp_path):
        root = healthy_arch(tmp_path)
        ok, criticals = ic.gate_result(root)
        assert ok is True
        assert criticals == []

    def test_critical_drift_halts_and_returns_criticals(self, tmp_path):
        root = healthy_arch(tmp_path)
        # Introduce ONE critical drift: a second immutable file absent from the lock
        # (INV1 is severity=critical).
        _write(root / "extra.md", _immutable_doc("extra"))

        ok, criticals = ic.gate_result(root)
        assert ok is False, "a critical violation must make the gate HALT (ok=False)"
        assert criticals, "gate must return the offending critical violation(s)"
        assert all(isinstance(v, Violation) for v in criticals)
        assert all(v.severity == "critical" for v in criticals)
        assert any(v.invariant_id == "INV1" for v in criticals)

    def test_returns_only_criticals_not_warns(self, tmp_path):
        root = healthy_arch(tmp_path)
        # Critical (INV1) + a warn-level drift (INV2: done block with no retro).
        _write(root / "extra.md", _immutable_doc("extra"))
        log = root / "blocks" / "BLOCK_LOG.md"
        log.write_text(
            log.read_text(encoding="utf-8") + "block-003 done - 2026-05-22\n",
            encoding="utf-8",
        )
        ok, criticals = ic.gate_result(root)
        assert ok is False
        # The warn must NOT appear in the critical list returned for the HALT.
        assert all(v.severity == "critical" for v in criticals)
        assert all(v.invariant_id != "INV2" for v in criticals)

    def test_never_raises_on_garbage_root(self, tmp_path):
        # A non-existent / empty root must not throw — gate stays pure.
        ok, criticals = ic.gate_result(tmp_path / "does-not-exist")
        assert isinstance(ok, bool)
        assert isinstance(criticals, list)


# ---------------------------------------------------------------------------
# run_invariant_check — the session_start runner (SURFACE, never abort).
# ---------------------------------------------------------------------------

class TestRunInvariantCheckRunner:
    def test_returns_bool_and_count_string(self, tmp_path):
        root = healthy_arch(tmp_path)
        result = session_start.run_invariant_check(root)
        assert isinstance(result, tuple) and len(result) == 2
        ok, summary = result
        assert isinstance(ok, bool)
        assert isinstance(summary, str)
        # Count summary shape: "N critical, M warn".
        assert "critical" in summary and "warn" in summary

    def test_clean_arch_reports_zero_zero(self, tmp_path):
        root = healthy_arch(tmp_path)
        ok, summary = session_start.run_invariant_check(root)
        assert ok is True
        assert summary.startswith("0 critical, 0 warn")

    def test_registered_in_tool_runners(self):
        assert "invariant-check" in session_start.TOOL_RUNNERS
        assert session_start.TOOL_RUNNERS["invariant-check"] is session_start.run_invariant_check

    def test_runner_on_real_root_completes(self):
        # On the real root (pre-existing drift) the runner still returns ok=True
        # with a count string — it surfaces, it does not fail/abort.
        ok, summary = session_start.run_invariant_check(_ARCH_ROOT)
        assert ok is True
        assert "critical" in summary and "warn" in summary


# ---------------------------------------------------------------------------
# Registry — the invariant-check row is parseable (so the tool runs each session).
# ---------------------------------------------------------------------------

class TestRegistryHasInvariantCheck:
    def test_real_registry_parses_invariant_check_id(self):
        registry_path = _ARCH_ROOT / "governance" / "tools-registry.yaml"
        tools = session_start._parse_registry(registry_path)
        ids = {t.get("id") for t in tools}
        assert "invariant-check" in ids

    def test_invariant_check_row_has_expected_fields(self):
        registry_path = _ARCH_ROOT / "governance" / "tools-registry.yaml"
        tools = session_start._parse_registry(registry_path)
        row = next((t for t in tools if t.get("id") == "invariant-check"), None)
        assert row is not None
        assert "invariant_check.py" in row.get("command", "")
        assert row.get("trigger_type") == "time"
        assert row.get("priority") == "high"

    def test_invariant_check_id_visible_to_inv4(self):
        # INV4's registry scanner must see the new id, so the live runner is
        # considered registered (no self-inflicted INV4 violation on the real root).
        registry_ids = ic._registry_ids(_ARCH_ROOT)
        assert "invariant-check" in registry_ids
