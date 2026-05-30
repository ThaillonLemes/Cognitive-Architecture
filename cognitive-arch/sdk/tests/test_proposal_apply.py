# PURPOSE: Tests for sdk/proposal_apply.py — proposal -> concrete unified diff (dry-run render)
# INPUTS:  tmp_path synthetic proposals + targets; the real repo arch-root for immutable/CLI checks
# OUTPUTS: assertions on DiffResult shape/status, diff content, never-raises, and zero-write CLI
# DEPS:    pytest, pathlib, proposal_apply module
# SEE:     sdk/proposal_apply.py, manifests/block-152-proposal-diff.md, phases/phase-27.md

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from proposal_apply import (
    ProposalApply,
    DiffResult,
    generate_diff,
    _read_block_scalar,
    _build_appended_section,
)

# Real cognitive-arch root (this test file lives in <root>/sdk/tests/).
_ARCH_ROOT = _SDK_DIR.parent
_REAL_ACCEPTED = "2026-05-29-scope-expansion-recurring"   # accepted, immutable target
_REAL_REJECTED = "2026-05-29-velocity-data-gap"           # rejected


# ---------------------------------------------------------------------------
# Helpers — build synthetic proposals + targets under tmp_path
# ---------------------------------------------------------------------------

def _write_proposal(root: Path, proposal_id: str, body: str) -> Path:
    pdir = root / "governance" / "proposals"
    pdir.mkdir(parents=True, exist_ok=True)
    path = pdir / f"{proposal_id}.md"
    path.write_text(body, encoding="utf-8")
    return path


def _accepted_proposal(target_file: str = "protocols/sample.md") -> str:
    return f"""---
id: synthetic-accepted
status: accepted
pattern_id: sample-pattern-recurring
target_file: {target_file}
proposed_change: |
  Add a manifest-scope checklist line to reduce scope expansion.
  Reviewer should confirm the wording.
rationale: |
  Pattern 'sample-pattern-recurring' detected 7 times, above threshold 3.
  Description: synthetic test rationale marker XYZZY.
created_at: 2026-05-30
---

# Proposal — sample-pattern-recurring
"""


def _make_target(root: Path, target_file: str, content: str) -> Path:
    path = root / target_file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Accepted proposal -> concrete unified diff
# ---------------------------------------------------------------------------

class TestAcceptedDiff:
    def test_accepted_yields_unified_diff(self, tmp_path):
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n\nLine one.\nLine two.\n")
        result = generate_diff("synthetic-accepted", tmp_path)

        assert isinstance(result, DiffResult)
        assert result.status == "accepted"
        assert result.unified_diff != ""
        # Unified-diff structural markers.
        assert "--- " in result.unified_diff
        assert "+++ " in result.unified_diff
        assert "@@" in result.unified_diff

    def test_diff_contains_target_path(self, tmp_path):
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n\nbody\n")
        result = generate_diff("synthetic-accepted", tmp_path)
        assert "protocols/sample.md" in result.unified_diff

    def test_diff_contains_proposed_text(self, tmp_path):
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n\nbody\n")
        result = generate_diff("synthetic-accepted", tmp_path)
        # The appended section uses the proposed_change text and a real heading.
        assert "manifest-scope checklist line" in result.unified_diff
        assert "## Note (from proposal synthetic-accepted)" in result.unified_diff
        # Provenance anchor present (machine-readable), but the body is real text.
        assert "<!-- pattern: sample-pattern-recurring -->" in result.unified_diff

    def test_rationale_attached(self, tmp_path):
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n\nbody\n")
        result = generate_diff("synthetic-accepted", tmp_path)
        assert "XYZZY" in result.rationale  # rationale block-scalar was read, not the "|"
        assert result.rationale.lstrip().startswith("Pattern")

    def test_diff_added_lines_only(self, tmp_path):
        # Append strategy: original lines are preserved; only additions appear.
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n\nkeep-me\n")
        result = generate_diff("synthetic-accepted", tmp_path)
        removed = [
            ln for ln in result.unified_diff.splitlines()
            if ln.startswith("-") and not ln.startswith("---")
        ]
        assert removed == []  # nothing removed — pure append


# ---------------------------------------------------------------------------
# Refusals — wrong status / placeholder / missing target
# ---------------------------------------------------------------------------

class TestRefusals:
    def test_rejected_proposal_no_diff(self, tmp_path):
        body = _accepted_proposal().replace("status: accepted", "status: rejected")
        _write_proposal(tmp_path, "synthetic-rejected", body)
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n")
        result = generate_diff("synthetic-rejected", tmp_path)
        assert result.status == "not-accepted"
        assert result.unified_diff == ""

    def test_pending_proposal_no_diff(self, tmp_path):
        body = _accepted_proposal().replace("status: accepted", "status: pending")
        _write_proposal(tmp_path, "synthetic-pending", body)
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n")
        result = generate_diff("synthetic-pending", tmp_path)
        assert result.status == "not-accepted"
        assert result.unified_diff == ""

    def test_placeholder_target_no_diff(self, tmp_path):
        body = _accepted_proposal(target_file="protocols/<target>.md")
        _write_proposal(tmp_path, "synthetic-placeholder", body)
        result = generate_diff("synthetic-placeholder", tmp_path)
        assert result.status == "no-target"
        assert result.unified_diff == ""

    def test_missing_target_file(self, tmp_path):
        # Accepted, concrete target_file, but the file does not exist on disk.
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        result = generate_diff("synthetic-accepted", tmp_path)
        assert result.status == "target-missing"
        assert result.unified_diff == ""


# ---------------------------------------------------------------------------
# Defensive — never raises
# ---------------------------------------------------------------------------

class TestNeverRaises:
    def test_unknown_proposal_id(self, tmp_path):
        result = generate_diff("does-not-exist-at-all", tmp_path)
        assert isinstance(result, DiffResult)
        assert result.status == "not-accepted"
        assert result.unified_diff == ""

    def test_empty_proposal_id(self, tmp_path):
        result = generate_diff("", tmp_path)
        assert isinstance(result, DiffResult)
        assert result.unified_diff == ""

    def test_garbage_frontmatter_no_raise(self, tmp_path):
        _write_proposal(tmp_path, "synthetic-garbage", "not yaml at all\n::::\n")
        result = generate_diff("synthetic-garbage", tmp_path)
        assert isinstance(result, DiffResult)
        # No status field -> treated as not-accepted, no diff, no exception.
        assert result.unified_diff == ""

    def test_nonexistent_arch_root(self, tmp_path):
        result = generate_diff("whatever", tmp_path / "no" / "such" / "root")
        assert isinstance(result, DiffResult)
        assert result.unified_diff == ""


# ---------------------------------------------------------------------------
# Immutability flag (informational here; the guard is block-153)
# ---------------------------------------------------------------------------

class TestImmutability:
    def test_immutable_target_flagged_true(self):
        # Real accepted proposal targets templates/manifest-medium.md (immutable).
        result = generate_diff(_REAL_ACCEPTED, _ARCH_ROOT)
        assert result.status == "accepted"
        assert result.is_immutable is True
        assert result.unified_diff != ""
        assert "templates/manifest-medium.md" in result.unified_diff

    def test_non_immutable_target_flagged_false(self, tmp_path):
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        _make_target(tmp_path, "protocols/sample.md", "# Sample\n\nbody\n")
        result = generate_diff("synthetic-accepted", tmp_path)
        assert result.is_immutable is False


# ---------------------------------------------------------------------------
# CRLF handling
# ---------------------------------------------------------------------------

class TestLineEndings:
    def test_crlf_target_produces_lf_diff(self, tmp_path):
        _write_proposal(tmp_path, "synthetic-accepted", _accepted_proposal())
        # Write a CRLF target deliberately.
        path = tmp_path / "protocols" / "sample.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"# Sample\r\n\r\nLine one.\r\nLine two.\r\n")
        result = generate_diff("synthetic-accepted", tmp_path)
        assert result.status == "accepted"
        assert "\r" not in result.unified_diff  # normalized to LF


# ---------------------------------------------------------------------------
# Block-scalar reader unit checks
# ---------------------------------------------------------------------------

class TestBlockScalarReader:
    def test_reads_block_scalar(self):
        text = "id: x\nrationale: |\n  line a\n  line b\nnext: y\n"
        assert _read_block_scalar(text, "rationale") == "line a\nline b"

    def test_reads_inline_scalar(self):
        text = "id: x\ntarget_file: protocols/foo.md\n"
        assert _read_block_scalar(text, "target_file") == "protocols/foo.md"

    def test_missing_field_returns_empty(self):
        assert _read_block_scalar("id: x\n", "rationale") == ""

    def test_appended_section_is_real_text_not_just_comment(self):
        section = _build_appended_section("pid", "pat", "hello body")
        assert "## Note (from proposal pid)" in section
        assert "hello body" in section
        # Provenance comment present but is not the only content.
        assert "<!-- pattern: pat -->" in section


# ---------------------------------------------------------------------------
# CLI — exits 0 and writes NOTHING
# ---------------------------------------------------------------------------

class TestCLI:
    def test_cli_exits_zero_on_accepted(self, capsys):
        from proposal_apply import main
        rc = main(["--arch-root", str(_ARCH_ROOT), "--proposal", _REAL_ACCEPTED])
        out = capsys.readouterr().out
        assert rc == 0
        assert "--- " in out and "+++ " in out and "@@" in out
        assert "IMMUTABLE" in out          # immutable banner shown
        assert "status: accepted" in out

    def test_cli_exits_zero_on_rejected(self, capsys):
        from proposal_apply import main
        rc = main(["--arch-root", str(_ARCH_ROOT), "--proposal", _REAL_REJECTED])
        out = capsys.readouterr().out
        assert rc == 0
        assert "status: not-accepted" in out

    def test_cli_exits_zero_on_unknown(self, capsys):
        from proposal_apply import main
        rc = main(["--arch-root", str(_ARCH_ROOT), "--proposal", "no-such-proposal"])
        assert rc == 0

    def test_cli_writes_nothing_to_target(self, capsys):
        # The real accepted target must be byte-identical after a CLI run.
        from proposal_apply import main
        target = _ARCH_ROOT / "templates" / "manifest-medium.md"
        before = target.read_bytes()
        rc = main(["--arch-root", str(_ARCH_ROOT), "--proposal", _REAL_ACCEPTED])
        after = target.read_bytes()
        assert rc == 0
        assert before == after  # nothing written — pure dry-run render

    def test_cli_writes_no_new_proposal_files(self, capsys):
        # generate_diff/CLI must not create or mutate any proposal file either.
        from proposal_apply import main
        pdir = _ARCH_ROOT / "governance" / "proposals"
        before = {p.name: p.read_bytes() for p in pdir.glob("*.md")}
        main(["--arch-root", str(_ARCH_ROOT), "--proposal", _REAL_ACCEPTED])
        after = {p.name: p.read_bytes() for p in pdir.glob("*.md")}
        assert before == after
