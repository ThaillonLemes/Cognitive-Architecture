# PURPOSE: Tests for block-153 apply guards in sdk/proposal_apply.py (check_guards + _backup)
# INPUTS:  tmp_path synthetic arch-roots (proposals, targets, lock, governor-log); real root for the immutable refusal
# OUTPUTS: assertions on GuardResult shape/verdict for each of the 4 guards, _backup byte-identity, never-raises, zero-write CLI
# DEPS:    pytest, pathlib, proposal_apply module
# SEE:     sdk/proposal_apply.py, manifests/block-153-guard-gates.md, phases/phase-27.md

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from proposal_apply import (
    ProposalApply,
    GuardResult,
    check_guards,
    _has_leading_frontmatter,
)

# Real cognitive-arch root (this test file lives in <root>/sdk/tests/).
_ARCH_ROOT = _SDK_DIR.parent
_REAL_IMMUTABLE = "2026-05-29-scope-expansion-recurring"  # accepted, immutable target, no bump


# ---------------------------------------------------------------------------
# Synthetic arch-root builders
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
"""
    path = pdir / f"{proposal_id}.md"
    path.write_text(body, encoding="utf-8")
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


def _sha16(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _write_lock(root: Path, entries: dict[str, str]) -> Path:
    """Write a minimal .integrity.lock with the given {relpath: sha256hex} entries."""
    lines = ["# .integrity.lock — test", ""]
    for rel, h in entries.items():
        lines.append(f"{rel}  sha256:{h}")
    lines.append("")
    path = root / ".integrity.lock"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _full_sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Guard 1 — immutability
# ---------------------------------------------------------------------------

class TestImmutabilityGuard:
    def test_immutable_target_without_bump_refused(self, tmp_path):
        # An immutable target (protection: immutable frontmatter) with no recorded bump.
        _write_protocols(tmp_path)
        target = "protocols/locked.md"
        _make_target(
            tmp_path, target,
            "---\nprotection: immutable\n---\n\n# Locked\n\nbody\n",
        )
        _write_proposal(tmp_path, "p-immutable", target)
        result = check_guards("p-immutable", tmp_path)

        assert isinstance(result, GuardResult)
        assert result.allowed is False
        assert result.target_file == target
        joined = " ".join(result.reasons)
        assert "immutability guard" in joined
        assert "integrity-bump.md" in joined  # points the human to the gate

    def test_real_immutable_proposal_refused(self):
        # The real scope-expansion proposal targets templates/manifest-medium.md
        # (immutable, locked clean, no bump for it in governor-log) -> REFUSED.
        result = check_guards(_REAL_IMMUTABLE, _ARCH_ROOT)
        assert result.allowed is False
        assert result.target_file == "templates/manifest-medium.md"
        assert any("immutability guard" in r for r in result.reasons)

    def test_immutable_target_with_recorded_bump_allowed(self, tmp_path):
        # Immutable target, lock clean for it, AND a governor-log bump naming it
        # -> the immutability guard does NOT refuse (informational note only).
        _write_protocols(tmp_path)
        target = "protocols/bumped.md"
        tpath = _make_target(
            tmp_path, target,
            "---\nprotection: immutable\n---\n\n# Bumped\n\nbody\n",
        )
        _write_lock(tmp_path, {target: _full_sha(tpath)})  # lock verifies clean
        gdir = tmp_path / "governance"
        gdir.mkdir(parents=True, exist_ok=True)
        (gdir / "governor-log.md").write_text(
            "# --- INTEGRITY BUMP APPROVED ---\n"
            "# file: protocols/bumped.md\n"
            "# reason: approved test change\n"
            "# block: block-XXX\n"
            "# --- END INTEGRITY BUMP ---\n",
            encoding="utf-8",
        )
        _write_proposal(tmp_path, "p-bumped", target)
        result = check_guards("p-bumped", tmp_path)

        assert result.allowed is True
        # The note explains the bump authorized the otherwise-immutable target.
        assert any("immutability note" in r for r in result.reasons)

    def test_unrelated_bump_does_not_satisfy(self, tmp_path):
        # A bump for a DIFFERENT file must NOT clear an immutable target.
        _write_protocols(tmp_path)
        target = "protocols/locked.md"
        _make_target(
            tmp_path, target,
            "---\nprotection: immutable\n---\n\n# Locked\n\nbody\n",
        )
        gdir = tmp_path / "governance"
        gdir.mkdir(parents=True, exist_ok=True)
        (gdir / "governor-log.md").write_text(
            "# --- INTEGRITY BUMP APPROVED ---\n"
            "# file: PROTOCOLS.md\n"
            "# --- END INTEGRITY BUMP ---\n",
            encoding="utf-8",
        )
        _write_proposal(tmp_path, "p-immutable", target)
        result = check_guards("p-immutable", tmp_path)
        assert result.allowed is False
        assert any("immutability guard" in r for r in result.reasons)


# ---------------------------------------------------------------------------
# Happy path — OPEN target, clean structural result -> ALLOWED
# ---------------------------------------------------------------------------

class TestOpenTargetAllowed:
    def test_open_md_target_allowed(self, tmp_path):
        _write_protocols(tmp_path)
        target = "protocols/open.md"
        _make_target(tmp_path, target, "# Open\n\njust a normal markdown file.\n")
        _write_proposal(tmp_path, "p-open", target)
        result = check_guards("p-open", tmp_path)

        assert isinstance(result, GuardResult)
        assert result.allowed is True
        assert result.target_file == target
        # A non-locked, non-immutable target yields a passing confirmation.
        assert result.reasons  # at least the "all guards passed" line

    def test_open_md_with_frontmatter_kept_allowed(self, tmp_path):
        # Append strategy keeps the leading frontmatter intact -> sanity passes.
        _write_protocols(tmp_path)
        target = "protocols/fm.md"
        _make_target(
            tmp_path, target,
            "---\ntitle: Sample\nkind: doc\n---\n\n# Heading\n\nbody\n",
        )
        _write_proposal(tmp_path, "p-fm", target)
        result = check_guards("p-fm", tmp_path)
        assert result.allowed is True

    def test_allowed_has_backup_plan(self, tmp_path):
        _write_protocols(tmp_path)
        target = "protocols/open.md"
        _make_target(tmp_path, target, "# Open\n\nbody\n")
        _write_proposal(tmp_path, "p-open", target)
        result = check_guards("p-open", tmp_path)
        # backup_plan points under _backups/ with a content-hash stamp; no write happens.
        assert result.backup_plan.startswith("_backups/")
        assert result.backup_plan.endswith(".bak")
        assert not (tmp_path / "_backups").exists()  # evaluate-only: nothing written


# ---------------------------------------------------------------------------
# Guard 3 — structural sanity (.py compile)
# ---------------------------------------------------------------------------

class TestStructuralSanity:
    def test_py_target_that_would_not_compile_blocked(self, tmp_path):
        # A .py target whose ORIGINAL is an unterminated string: appending the
        # note section cannot close it, so the post-change won't compile.
        _write_protocols(tmp_path)
        target = "sdk/broken.py"
        _make_target(tmp_path, target, 'x = "unterminated\n')  # SyntaxError when appended-to
        _write_proposal(tmp_path, "p-py", target)
        result = check_guards("p-py", tmp_path)

        assert result.allowed is False
        assert any("structural guard" in r and "compile" in r for r in result.reasons)

    def test_py_target_append_breaks_compile_is_refused(self, tmp_path):
        # Even a syntactically valid .py target is refused: the appended markdown
        # note ('## ...' headings, prose) is not valid Python, so the post-change
        # content fails to compile -> the structural guard correctly refuses. This
        # exercises the compile() success path on the ORIGINAL while the would-be
        # result fails, which is the realistic outcome for the 152 append strategy.
        _write_protocols(tmp_path)
        target = "sdk/ok.py"
        _make_target(tmp_path, target, "y = 1\n")
        _write_proposal(tmp_path, "p-ok-py", target)
        result = check_guards("p-ok-py", tmp_path)
        assert result.allowed is False
        assert any("structural guard" in r for r in result.reasons)

    def test_py_compile_pass_branch_via_helper(self, tmp_path):
        # Exercise the compile-PASS branch of _structural_sanity directly: build a
        # target whose post-change content (original + appended note) is monkey-
        # neutralized to valid Python by making the whole appended note a comment.
        # We do this by pointing the helper at a target+proposal and stubbing the
        # content builder to return valid Python, isolating the OK path.
        _write_protocols(tmp_path)
        target = "sdk/calc.py"
        tpath = _make_target(tmp_path, target, "z = 2\n")
        _write_proposal(tmp_path, "p-calc", target)
        apply = ProposalApply(tmp_path)
        # Force the would-be content to a valid-Python string to hit the pass path.
        apply._build_modified_content = lambda *a, **k: "z = 2\n# only comments appended\n"
        ok, reason = apply._structural_sanity("p-calc", tpath, target)
        assert ok is True
        assert reason == ""

    def test_non_md_non_py_target_allowed(self, tmp_path):
        # A .txt target: only the non-empty invariant applies -> allowed.
        _write_protocols(tmp_path)
        target = "notes/scratch.txt"
        _make_target(tmp_path, target, "some plain notes\n")
        _write_proposal(tmp_path, "p-txt", target)
        result = check_guards("p-txt", tmp_path)
        assert result.allowed is True


# ---------------------------------------------------------------------------
# Guard 2 — integrity (pre-existing lock mismatch blocks apply)
# ---------------------------------------------------------------------------

class TestIntegrityGuard:
    def test_preexisting_mismatch_blocks(self, tmp_path):
        # Target is locked, but the lock hash is wrong -> verify reports MISMATCH.
        _write_protocols(tmp_path)
        target = "protocols/tracked.md"
        _make_target(tmp_path, target, "# Tracked\n\nbody\n")
        _write_lock(tmp_path, {target: "0" * 64})  # deliberately wrong hash
        _write_proposal(tmp_path, "p-mismatch", target)
        result = check_guards("p-mismatch", tmp_path)

        assert result.allowed is False
        assert any("integrity guard" in r and "MISMATCH" in r for r in result.reasons)

    def test_locked_clean_target_passes_integrity(self, tmp_path):
        _write_protocols(tmp_path)
        target = "protocols/tracked.md"
        tpath = _make_target(tmp_path, target, "# Tracked\n\nbody\n")
        _write_lock(tmp_path, {target: _full_sha(tpath)})  # correct hash
        _write_proposal(tmp_path, "p-clean", target)
        result = check_guards("p-clean", tmp_path)
        assert result.allowed is True
        assert not any("integrity guard" in r for r in result.reasons)


# ---------------------------------------------------------------------------
# Guard 4 — acceptance
# ---------------------------------------------------------------------------

class TestAcceptanceGuard:
    def test_pending_proposal_refused(self, tmp_path):
        _write_protocols(tmp_path)
        target = "protocols/open.md"
        _make_target(tmp_path, target, "# Open\n\nbody\n")
        _write_proposal(tmp_path, "p-pending", target, status="pending")
        result = check_guards("p-pending", tmp_path)
        assert result.allowed is False
        assert any("acceptance guard" in r for r in result.reasons)

    def test_rejected_proposal_refused(self, tmp_path):
        _write_protocols(tmp_path)
        target = "protocols/open.md"
        _make_target(tmp_path, target, "# Open\n\nbody\n")
        _write_proposal(tmp_path, "p-rejected", target, status="rejected")
        result = check_guards("p-rejected", tmp_path)
        assert result.allowed is False
        assert any("acceptance guard" in r for r in result.reasons)


# ---------------------------------------------------------------------------
# _backup — byte-identical copy under _backups/
# ---------------------------------------------------------------------------

class TestBackup:
    def test_backup_creates_byte_identical_copy(self, tmp_path):
        target = "protocols/open.md"
        content = "# Open\n\nsome bytes: ünïcödé and a tab\there.\n"
        tpath = _make_target(tmp_path, target, content)
        apply = ProposalApply(tmp_path)

        dest = apply._backup(tpath)

        assert dest.exists()
        assert dest.parent == tmp_path / "_backups"
        assert dest.name.startswith("open.md.")
        assert dest.suffix == ".bak"
        # Byte-for-byte identical to the source.
        assert dest.read_bytes() == tpath.read_bytes()
        # Stamp is the content hash (deterministic, clock/random-free).
        assert _sha16(tpath) in dest.name

    def test_backup_stamp_is_deterministic(self, tmp_path):
        target = "protocols/open.md"
        tpath = _make_target(tmp_path, target, "stable content\n")
        apply = ProposalApply(tmp_path)
        first = apply._backup(tpath)
        second = apply._backup(tpath)
        # Same content -> same stamped filename (idempotent).
        assert first == second


# ---------------------------------------------------------------------------
# Defensive — check_guards never raises on bad input
# ---------------------------------------------------------------------------

class TestNeverRaises:
    def test_unknown_proposal_id(self, tmp_path):
        result = check_guards("does-not-exist-at-all", tmp_path)
        assert isinstance(result, GuardResult)
        assert result.allowed is False

    def test_empty_proposal_id(self, tmp_path):
        result = check_guards("", tmp_path)
        assert isinstance(result, GuardResult)
        assert result.allowed is False

    def test_garbage_frontmatter(self, tmp_path):
        pdir = tmp_path / "governance" / "proposals"
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "p-garbage.md").write_text("not yaml at all\n::::\n", encoding="utf-8")
        result = check_guards("p-garbage", tmp_path)
        assert isinstance(result, GuardResult)
        assert result.allowed is False

    def test_nonexistent_arch_root(self, tmp_path):
        result = check_guards("whatever", tmp_path / "no" / "such" / "root")
        assert isinstance(result, GuardResult)
        assert result.allowed is False

    def test_target_missing_on_disk(self, tmp_path):
        # Accepted proposal, concrete target, but the file does not exist.
        _write_protocols(tmp_path)
        _write_proposal(tmp_path, "p-missing", "protocols/ghost.md")
        result = check_guards("p-missing", tmp_path)
        assert isinstance(result, GuardResult)
        assert result.allowed is False  # acceptance-status becomes target-missing -> refused


# ---------------------------------------------------------------------------
# Frontmatter helper unit checks
# ---------------------------------------------------------------------------

class TestFrontmatterHelper:
    def test_balanced_frontmatter_true(self):
        assert _has_leading_frontmatter("---\ntitle: x\n---\n\nbody\n") is True

    def test_no_frontmatter_false(self):
        assert _has_leading_frontmatter("# Heading\n\nbody\n") is False

    def test_unbalanced_frontmatter_false(self):
        # Opens but never closes -> not balanced.
        assert _has_leading_frontmatter("---\ntitle: x\n\nbody with no close\n") is False


# ---------------------------------------------------------------------------
# CLI — --check-guards exits 0 and writes nothing
# ---------------------------------------------------------------------------

class TestCLI:
    def test_cli_check_guards_refused_on_real_immutable(self, capsys):
        from proposal_apply import main
        rc = main(["--arch-root", str(_ARCH_ROOT), "--proposal", _REAL_IMMUTABLE, "--check-guards"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "REFUSED" in out
        assert "immutability guard" in out
        assert "integrity-bump.md" in out

    def test_cli_check_guards_writes_nothing(self, capsys):
        # The real immutable target must be byte-identical after a guard CLI run,
        # and no _backups/ dir is created at the real root.
        from proposal_apply import main
        target = _ARCH_ROOT / "templates" / "manifest-medium.md"
        before = target.read_bytes()
        backups_existed = (_ARCH_ROOT / "_backups").exists()
        rc = main(["--arch-root", str(_ARCH_ROOT), "--proposal", _REAL_IMMUTABLE, "--check-guards"])
        after = target.read_bytes()
        assert rc == 0
        assert before == after
        # check_guards must not have created _backups/ at the real root.
        assert (_ARCH_ROOT / "_backups").exists() == backups_existed

    def test_cli_check_guards_allowed_on_synthetic_open(self, tmp_path, capsys):
        from proposal_apply import main
        _write_protocols(tmp_path)
        target = "protocols/open.md"
        _make_target(tmp_path, target, "# Open\n\nbody\n")
        _write_proposal(tmp_path, "p-open", target)
        rc = main(["--arch-root", str(tmp_path), "--proposal", "p-open", "--check-guards"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "ALLOWED" in out
        # Evaluate-only: no _backups/ written even on ALLOWED.
        assert not (tmp_path / "_backups").exists()


# ---------------------------------------------------------------------------
# _setup_arch helper for block-156 tests
# ---------------------------------------------------------------------------

def _setup_arch(root):
    """Create the minimal arch structure needed for ProposalApply instantiation."""
    _write_protocols(root)
    lock_path = root / ".integrity.lock"
    if not lock_path.exists():
        lock_path.write_text("# .integrity.lock\n")


# ---- block-156 tests --------------------------------------------------------

def test_integrity_bump_no_basename_collision(tmp_path):
    """A bump for templates/manifest-medium.md must NOT unlock archive/manifest-medium.md."""
    _setup_arch(tmp_path)
    # Two immutable files sharing a basename in different dirs
    (tmp_path / "templates").mkdir(exist_ok=True)
    (tmp_path / "archive").mkdir(exist_ok=True)
    for d in ("templates", "archive"):
        f = tmp_path / d / "manifest-medium.md"
        f.write_text("---\nprotection: immutable\n---\nbody\n")
    # Lock both
    lock_path = tmp_path / ".integrity.lock"
    import hashlib
    for d in ("templates", "archive"):
        p = tmp_path / d / "manifest-medium.md"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        with open(lock_path, "a") as fh:
            fh.write(f"{d}/manifest-medium.md  sha256:{h}\n")
    # Bump names ONLY templates/manifest-medium.md
    log = tmp_path / "governance" / "governor-log.md"
    log.parent.mkdir(exist_ok=True)
    log.write_text(
        "# --- INTEGRITY BUMP APPROVED ---\n"
        "# file: templates/manifest-medium.md\n"
        "# --- END INTEGRITY BUMP ---\n"
    )
    pa = ProposalApply(tmp_path)
    # templates — must be True (exact match)
    assert pa._has_integrity_bump("templates/manifest-medium.md") is True
    # archive — must be False (basename collision must not authorize)
    assert pa._has_integrity_bump("archive/manifest-medium.md") is False


def test_integrity_bump_sticky_flag_reset_on_wrong_end_marker(tmp_path):
    """A bump block closed with --- END APPLY --- must NOT leak to later file: lines."""
    _setup_arch(tmp_path)
    log = tmp_path / "governance" / "governor-log.md"
    log.parent.mkdir(exist_ok=True)
    log.write_text(
        "# --- INTEGRITY BUMP APPROVED ---\n"
        "# file: SOME_OTHER.md\n"
        "# --- END APPLY ---\n"           # wrong end marker
        "\n"
        "# --- APPLY APPLIED ---\n"
        "# file: docs/TOTALLY_UNRELATED.md\n"
        "# --- END APPLY ---\n"
    )
    pa = ProposalApply(tmp_path)
    assert pa._has_integrity_bump("docs/TOTALLY_UNRELATED.md") is False


def test_integrity_ok_unlocked_immutable_refused(tmp_path):
    """An immutable file not in .integrity.lock must be refused, not silently OK."""
    _setup_arch(tmp_path)
    (tmp_path / "docs").mkdir(exist_ok=True)
    guide = tmp_path / "docs" / "GUIDE.md"
    guide.write_text("---\nprotection: immutable\n---\nbody\n")
    # .integrity.lock is empty (file not registered)
    (tmp_path / ".integrity.lock").write_text("")
    pa = ProposalApply(tmp_path)
    ok, reason = pa._integrity_ok("docs/GUIDE.md")
    assert ok is False
    assert "not in .integrity.lock" in reason or "integrity-bump" in reason


def test_integrity_ok_unlocked_non_immutable_passes(tmp_path):
    """A non-immutable file not in the lock must still return OK."""
    _setup_arch(tmp_path)
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "README.md").write_text("# README\n")
    (tmp_path / ".integrity.lock").write_text("")
    pa = ProposalApply(tmp_path)
    ok, reason = pa._integrity_ok("docs/README.md")
    assert ok is True

