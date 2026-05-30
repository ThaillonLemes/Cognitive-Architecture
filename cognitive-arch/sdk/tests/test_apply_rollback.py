# PURPOSE: Tests for block-154 apply-with-rollback + provenance in sdk/proposal_apply.py (apply_proposal / ProposalApply.apply)
# INPUTS:  tmp_path SYNTHETIC arch-roots only (OPEN non-immutable targets + fake accepted proposals); the verification subprocess runner is monkeypatched so the suite NEVER recurses into a real apply
# OUTPUTS: assertions on ApplyResult shape/outcome — happy path writes + records, forced-failure rolls back byte-identical, guard-refusal/dry-run write nothing, never-raises on bad input
# DEPS:    pytest, pathlib, proposal_apply module
# SEE:     sdk/proposal_apply.py, manifests/block-154-apply-rollback.md, manifests/block-153-guard-gates.md, phases/phase-27.md
#
# SAFETY: every apply here targets a file UNDER tmp_path. No test applies a diff to a real
#         protocol/immutable file in the repo, and _run_verification is always monkeypatched
#         (the real one would shell out to pytest and recurse) — see _patch_verify.

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import proposal_apply
from proposal_apply import (
    ProposalApply,
    ApplyResult,
    apply_proposal,
)

# Real cognitive-arch root (this test file lives in <root>/sdk/tests/).
_ARCH_ROOT = _SDK_DIR.parent
_REAL_IMMUTABLE = "2026-05-29-scope-expansion-recurring"  # accepted, immutable target, no bump


# ---------------------------------------------------------------------------
# Synthetic arch-root builders (mirror test_apply_guards.py conventions)
# ---------------------------------------------------------------------------

def _write_proposal(root: Path, proposal_id: str, target_file: str, status: str = "accepted") -> Path:
    pdir = root / "governance" / "proposals"
    pdir.mkdir(parents=True, exist_ok=True)
    body = f"""---
id: {proposal_id}
status: {status}
pattern_id: sample-pattern-recurring
target_file: {target_file}
proposed_change: |
  Add a short clarifying note for the recurring pattern.
  Reviewer should confirm the wording.
rationale: |
  Pattern 'sample-pattern-recurring' detected 7 times, above threshold 3.
created_at: 2026-05-30
---

# Proposal — sample-pattern-recurring

## 5. Resolution

**Status:** accepted
"""
    path = pdir / f"{proposal_id}.md"
    path.write_text(body, encoding="utf-8")
    return path


def _write_index(root: Path, proposal_id: str, status: str = "accepted") -> Path:
    """A minimal proposals/index.md row that _update_index_status can rewrite."""
    pdir = root / "governance" / "proposals"
    pdir.mkdir(parents=True, exist_ok=True)
    text = (
        "# Proposals index\n\n"
        "| Date | Proposal | Pattern | Severity | Status |\n"
        "|------|----------|---------|----------|--------|\n"
        f"| 2026-05-30 | [{proposal_id}]({proposal_id}.md) | sample-pattern-recurring | warn | {status} |\n"
    )
    path = pdir / "index.md"
    path.write_text(text, encoding="utf-8")
    return path


def _make_target(root: Path, target_file: str, content: str) -> Path:
    path = root / target_file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_protocols(root: Path, body: str = "# PROTOCOLS\n\nNo immutable files declared here.\n") -> Path:
    path = root / "PROTOCOLS.md"
    path.write_text(body, encoding="utf-8")
    return path


def _open_arch(tmp_path: Path, proposal_id: str = "p-open", target: str = "protocols/open.md") -> tuple[Path, str]:
    """A synthetic arch with an OPEN (non-immutable, unlocked) md target + accepted proposal."""
    _write_protocols(tmp_path)
    _make_target(tmp_path, target, "# Open\n\njust a normal markdown file.\n")
    _write_proposal(tmp_path, proposal_id, target)
    _write_index(tmp_path, proposal_id)
    return tmp_path, target


def _patch_verify(monkeypatch, *, ok: bool) -> None:
    """Force ProposalApply._run_verification to a deterministic result.

    CRITICAL: the real _run_verification shells out to `pytest sdk/tests/` which
    would re-enter this very test under apply -> recursion. Every apply test that
    reaches the write stage MUST patch it. This keeps the suite hermetic.
    """
    reason = "pytest: passed (exit 0)." if ok else "pytest: FAILED (exit 1); last line: 1 failed"
    monkeypatch.setattr(
        ProposalApply,
        "_run_verification",
        lambda self: (ok, [reason]),
    )


# ---------------------------------------------------------------------------
# Happy path — confirm=True writes, verifies, records (status/log/ADR)
# ---------------------------------------------------------------------------

class TestHappyPath:
    def test_apply_writes_change_and_records(self, tmp_path, monkeypatch):
        root, target = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=True)

        result = apply_proposal("p-open", root, confirm=True)

        assert isinstance(result, ApplyResult)
        assert result.applied is True
        assert result.rolled_back is False
        assert result.tests_passed is True
        assert result.target_file == target

        # The target now contains the appended proposal section.
        body = (root / target).read_text(encoding="utf-8")
        assert "# Open" in body  # original preserved
        assert "Note (from proposal p-open)" in body
        assert "clarifying note for the recurring pattern" in body

    def test_apply_takes_backup(self, tmp_path, monkeypatch):
        root, target = _open_arch(tmp_path)
        original = (root / target).read_bytes()
        _patch_verify(monkeypatch, ok=True)

        result = apply_proposal("p-open", root, confirm=True)

        assert result.backup_path.startswith("_backups/")
        assert result.backup_path.endswith(".bak")
        backup = root / result.backup_path
        assert backup.exists()
        # Backup is byte-identical to the PRE-apply original.
        assert backup.read_bytes() == original

    def test_apply_marks_proposal_applied(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=True)

        apply_proposal("p-open", root, confirm=True)

        ptext = (root / "governance" / "proposals" / "p-open.md").read_text(encoding="utf-8")
        assert "status: applied" in ptext
        assert "**Status:** applied" in ptext
        # Index row flipped too.
        itext = (root / "governance" / "proposals" / "index.md").read_text(encoding="utf-8")
        assert "applied" in itext

    def test_apply_appends_governor_log(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=True)

        apply_proposal("p-open", root, confirm=True)

        log = (root / "governance" / "governor-log.md").read_text(encoding="utf-8")
        assert "APPLY APPLIED" in log
        assert "proposal: p-open" in log
        assert "file: protocols/open.md" in log

    def test_apply_creates_adr_stub(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=True)

        result = apply_proposal("p-open", root, confirm=True)

        adrs = list((root / "decisions").glob("ADR-*-apply-*.md"))
        assert len(adrs) == 1
        adr_text = adrs[0].read_text(encoding="utf-8")
        assert "status: accepted" in adr_text
        assert "context_phase: phase-27" in adr_text
        assert "context_block: block-154" in adr_text
        assert "p-open" in adr_text
        # Filename references the chosen number; mentioned in result reasons.
        assert any("ADR stub written" in r for r in result.reasons)

    def test_adr_numbering_starts_at_006_when_005_exists(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)
        # Seed decisions/ with ADR-001..005 so the next must be ADR-006.
        decisions = root / "decisions"
        decisions.mkdir(parents=True, exist_ok=True)
        for n in range(1, 6):
            (decisions / f"ADR-{n:03d}-seed.md").write_text(f"id: ADR-{n:03d}\n", encoding="utf-8")
        _patch_verify(monkeypatch, ok=True)

        apply_proposal("p-open", root, confirm=True)

        assert (decisions / "ADR-006-apply-p-open.md").exists()


# ---------------------------------------------------------------------------
# Rollback path — verification FAILS -> byte-identical restore, not applied
# ---------------------------------------------------------------------------

class TestRollback:
    def test_failed_verify_restores_byte_identical(self, tmp_path, monkeypatch):
        root, target = _open_arch(tmp_path)
        original_bytes = (root / target).read_bytes()
        _patch_verify(monkeypatch, ok=False)  # force post-apply verification failure

        result = apply_proposal("p-open", root, confirm=True)

        assert result.applied is False
        assert result.rolled_back is True
        assert result.tests_passed is False
        # Target restored byte-for-byte to the pre-apply original.
        assert (root / target).read_bytes() == original_bytes

    def test_failed_verify_retains_backup(self, tmp_path, monkeypatch):
        root, target = _open_arch(tmp_path)
        original_bytes = (root / target).read_bytes()
        _patch_verify(monkeypatch, ok=False)

        result = apply_proposal("p-open", root, confirm=True)

        # Backup is retained on failure and equals the original (manifest §4 Risk row).
        backup = root / result.backup_path
        assert backup.exists()
        assert backup.read_bytes() == original_bytes

    def test_failed_verify_does_not_mark_applied(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=False)

        apply_proposal("p-open", root, confirm=True)

        ptext = (root / "governance" / "proposals" / "p-open.md").read_text(encoding="utf-8")
        assert "status: applied" not in ptext
        assert "status: accepted" in ptext  # unchanged

    def test_failed_verify_writes_no_adr(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=False)

        apply_proposal("p-open", root, confirm=True)

        decisions = root / "decisions"
        adrs = list(decisions.glob("ADR-*-apply-*.md")) if decisions.exists() else []
        assert adrs == []

    def test_rollback_reason_mentions_restore(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=False)

        result = apply_proposal("p-open", root, confirm=True)

        joined = " ".join(result.reasons).lower()
        assert "rolled back" in joined
        assert "restored byte-identical" in joined


# ---------------------------------------------------------------------------
# Guard-refused — immutable target -> no write, applied=False
# ---------------------------------------------------------------------------

class TestGuardRefused:
    def test_immutable_target_refused_no_write(self, tmp_path, monkeypatch):
        # If verification were ever called here it would (wrongly) suggest a write
        # happened; patch it to a sentinel that fails the test loudly if invoked.
        def _boom(self):  # pragma: no cover - must never run on a refused apply
            raise AssertionError("verification ran on a guard-refused apply (write happened!)")
        monkeypatch.setattr(ProposalApply, "_run_verification", _boom)

        _write_protocols(tmp_path)
        target = "protocols/locked.md"
        content = "---\nprotection: immutable\n---\n\n# Locked\n\nbody\n"
        _make_target(tmp_path, target, content)
        _write_proposal(tmp_path, "p-immutable", target)
        before = (tmp_path / target).read_bytes()

        result = apply_proposal("p-immutable", tmp_path, confirm=True)

        assert result.applied is False
        assert result.rolled_back is False
        # Nothing written: target unchanged, no backup taken.
        assert (tmp_path / target).read_bytes() == before
        assert not (tmp_path / "_backups").exists()
        assert any("immutability guard" in r for r in result.reasons)

    def test_real_immutable_proposal_refused_via_module(self):
        # The real scope-expansion proposal targets an immutable, locked template.
        # confirm=True still REFUSES at the guard and writes nothing to the repo.
        target = _ARCH_ROOT / "templates" / "manifest-medium.md"
        before = target.read_bytes()
        result = apply_proposal(_REAL_IMMUTABLE, _ARCH_ROOT, confirm=True)
        after = target.read_bytes()

        assert result.applied is False
        assert result.rolled_back is False
        assert before == after  # real immutable file untouched
        assert any("immutability guard" in r for r in result.reasons)


# ---------------------------------------------------------------------------
# Dry-run — confirm=False -> no write
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_writes_nothing(self, tmp_path, monkeypatch):
        # Verification must not run in a dry-run.
        def _boom(self):  # pragma: no cover - must never run in dry-run
            raise AssertionError("verification ran in a dry-run (write happened!)")
        monkeypatch.setattr(ProposalApply, "_run_verification", _boom)

        root, target = _open_arch(tmp_path)
        before = (root / target).read_bytes()

        result = apply_proposal("p-open", root, confirm=False)

        assert result.applied is False
        assert result.rolled_back is False
        assert (root / target).read_bytes() == before  # unchanged
        assert not (root / "_backups").exists()         # no backup written
        # Reports what WOULD happen and names a backup_plan.
        assert any("dry-run" in r.lower() for r in result.reasons)
        assert result.backup_path.startswith("_backups/")

    def test_dry_run_does_not_mark_or_log(self, tmp_path, monkeypatch):
        root, _ = _open_arch(tmp_path)

        apply_proposal("p-open", root, confirm=False)

        ptext = (root / "governance" / "proposals" / "p-open.md").read_text(encoding="utf-8")
        assert "status: applied" not in ptext
        assert not (root / "governance" / "governor-log.md").exists()
        assert not (root / "decisions").exists()


# ---------------------------------------------------------------------------
# Defensive — apply never raises on bad input
# ---------------------------------------------------------------------------

class TestNeverRaises:
    def test_unknown_proposal_id(self, tmp_path):
        result = apply_proposal("does-not-exist-at-all", tmp_path, confirm=True)
        assert isinstance(result, ApplyResult)
        assert result.applied is False

    def test_empty_proposal_id(self, tmp_path):
        result = apply_proposal("", tmp_path, confirm=True)
        assert isinstance(result, ApplyResult)
        assert result.applied is False

    def test_garbage_frontmatter(self, tmp_path):
        pdir = tmp_path / "governance" / "proposals"
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "p-garbage.md").write_text("not yaml at all\n::::\n", encoding="utf-8")
        result = apply_proposal("p-garbage", tmp_path, confirm=True)
        assert isinstance(result, ApplyResult)
        assert result.applied is False

    def test_nonexistent_arch_root(self, tmp_path):
        result = apply_proposal("whatever", tmp_path / "no" / "such" / "root", confirm=True)
        assert isinstance(result, ApplyResult)
        assert result.applied is False

    def test_pending_proposal_refused(self, tmp_path):
        # Not accepted -> guard refuses -> applied False, no write, no raise.
        _write_protocols(tmp_path)
        target = "protocols/open.md"
        _make_target(tmp_path, target, "# Open\n\nbody\n")
        _write_proposal(tmp_path, "p-pending", target, status="pending")
        before = (tmp_path / target).read_bytes()
        result = apply_proposal("p-pending", tmp_path, confirm=True)
        assert result.applied is False
        assert (tmp_path / target).read_bytes() == before


# ---------------------------------------------------------------------------
# Atomic write / restore helpers — direct unit checks
# ---------------------------------------------------------------------------

class TestAtomicHelpers:
    def test_atomic_write_replaces_cleanly(self, tmp_path):
        target = tmp_path / "f.txt"
        target.write_text("old\n", encoding="utf-8")
        ProposalApply._atomic_write(target, "new content\n")
        assert target.read_text(encoding="utf-8") == "new content\n"
        # No stray temp file left behind.
        assert not (tmp_path / "f.txt.apply.tmp").exists()

    def test_restore_returns_true_on_byte_identity(self, tmp_path):
        target = tmp_path / "f.txt"
        original = "original bytes: ünïcödé\there\n".encode("utf-8")
        target.write_bytes(original)
        # Simulate a backup + a corrupting write, then restore.
        backup = tmp_path / "f.bak"
        backup.write_bytes(original)
        target.write_text("corrupted\n", encoding="utf-8")
        ok = ProposalApply._restore(backup, target, original)
        assert ok is True
        assert target.read_bytes() == original
        assert not (tmp_path / "f.txt.restore.tmp").exists()


# ---------------------------------------------------------------------------
# CLI — --apply dry-run on the real immutable proposal exits 0, writes nothing
# ---------------------------------------------------------------------------

class TestCLI:
    def test_cli_apply_dry_run_refused_real_immutable(self, capsys):
        from proposal_apply import main
        target = _ARCH_ROOT / "templates" / "manifest-medium.md"
        before = target.read_bytes()
        backups_existed = (_ARCH_ROOT / "_backups").exists()

        rc = main(["--arch-root", str(_ARCH_ROOT), "--proposal", _REAL_IMMUTABLE, "--apply"])
        out = capsys.readouterr().out

        assert rc == 0
        assert "DRY-RUN" in out
        assert "immutability guard" in out
        # Real immutable file untouched; no _backups/ created at the real root.
        assert target.read_bytes() == before
        assert (_ARCH_ROOT / "_backups").exists() == backups_existed

    def test_cli_apply_confirm_happy_on_synthetic_open(self, tmp_path, monkeypatch, capsys):
        from proposal_apply import main
        root, target = _open_arch(tmp_path)
        _patch_verify(monkeypatch, ok=True)

        rc = main(["--arch-root", str(root), "--proposal", "p-open", "--apply", "--confirm"])
        out = capsys.readouterr().out

        assert rc == 0
        assert "APPLIED" in out
        assert "Note (from proposal p-open)" in (root / target).read_text(encoding="utf-8")

    def test_cli_apply_confirm_rollback_on_synthetic(self, tmp_path, monkeypatch, capsys):
        from proposal_apply import main
        root, target = _open_arch(tmp_path)
        original = (root / target).read_bytes()
        _patch_verify(monkeypatch, ok=False)

        rc = main(["--arch-root", str(root), "--proposal", "p-open", "--apply", "--confirm"])
        out = capsys.readouterr().out

        assert rc == 0
        assert "ROLLED BACK" in out
        assert (root / target).read_bytes() == original  # byte-identical restore
