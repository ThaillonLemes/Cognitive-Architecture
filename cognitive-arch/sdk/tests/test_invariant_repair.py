# PURPOSE: Tests for block-145 auto-repair — DRY-RUN writes nothing; --apply backs up
#          then fixes INV6; INV1 NEVER writes the immutable lock even with --apply.
# INPUTS:  tmp_path; synthetic arch roots built by test_invariant_check.healthy_arch
# OUTPUTS: assertions on repair_all RepairActions, backup creation, and byte-identity
#          of guarded files (.integrity.lock, registry) under apply.
# DEPS:    pytest, pathlib, hashlib, invariant_check + invariant_schema modules
# SEE:     sdk/invariant_check.py, sdk/invariant_schema.py, manifests/block-145-auto-repair.md

import hashlib
import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))
# Make sibling test modules importable so we can reuse the block-144 builders
# (healthy_arch is the canonical synthetic root — re-deriving it would risk drift).
_TESTS_DIR = Path(__file__).resolve().parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

import invariant_check as ic
from invariant_schema import Invariant, RepairAction

# Reuse the healthy-arch builder + helpers from the block-144 test module.
from test_invariant_check import healthy_arch, _write


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _action(actions, inv_id):
    """All RepairActions for a given invariant id."""
    return [a for a in actions if a.invariant_id == inv_id]


def _backups(root: Path) -> list[Path]:
    bdir = root / ic.BACKUP_DIR
    return sorted(bdir.glob("*")) if bdir.exists() else []


# ===========================================================================
# Driver-level guarantees
# ===========================================================================

class TestRepairAllShape:
    def test_returns_repairactions(self, tmp_path):
        root = healthy_arch(tmp_path)
        actions = ic.repair_all(root)  # dry-run default
        assert isinstance(actions, list)
        assert all(isinstance(a, RepairAction) for a in actions)
        # every repairable invariant is represented (all 6 have a repair fn)
        ids = {a.invariant_id for a in actions}
        assert {"INV1", "INV2", "INV3", "INV4", "INV5", "INV6"} <= ids

    def test_dry_run_is_default(self, tmp_path):
        """repair_all without apply must touch nothing on disk (the safety invariant)."""
        root = healthy_arch(tmp_path)
        before = {p: _sha(p) for p in root.rglob("*") if p.is_file()}
        ic.repair_all(root)  # default apply=False
        after = {p: _sha(p) for p in root.rglob("*") if p.is_file()}
        assert before == after
        assert not (root / ic.BACKUP_DIR).exists()  # no backups dir even

    def test_healthy_arch_all_noop(self, tmp_path):
        root = healthy_arch(tmp_path)
        actions = ic.repair_all(root)
        # A consistent arch has nothing to repair -> every action is a noop.
        assert all(a.kind == "noop" for a in actions), \
            [(a.invariant_id, a.kind, a.description) for a in actions]

    def test_repair_never_raises(self, tmp_path):
        """A repair that raises degrades to a kind='failed' action, never propagates."""
        def boom(_root, *, apply=False):
            raise RuntimeError("kaboom")

        reg = [Invariant(id="INVX", description="raises", severity="critical",
                         check=lambda r: [], repair=boom)]
        actions = ic.repair_all(tmp_path, registry=reg)
        assert len(actions) == 1
        assert actions[0].kind == "failed"
        assert "repair errored" in actions[0].description

    def test_invariant_without_repair_is_skipped(self, tmp_path):
        reg = [Invariant(id="INVN", description="no repair", severity="warn",
                         check=lambda r: ["x"])]  # repair=None
        actions = ic.repair_all(tmp_path, registry=reg)
        assert actions == []


# ===========================================================================
# INV6 — the only invariant that actually auto-writes (and only under --apply)
# ===========================================================================

class TestINV6Repair:
    def _add_orphan(self, root: Path, name="2026-05-30-bar.md") -> Path:
        f = root / "governance" / "proposals" / name
        _write(f, "---\ncreated_at: 2026-05-30\npattern_id: bar-pattern\nstatus: pending\n---\n# bar\n")
        return f

    def test_dry_run_writes_nothing(self, tmp_path):
        root = healthy_arch(tmp_path)
        self._add_orphan(root)
        idx = root / "governance" / "proposals" / "index.md"
        before = _sha(idx)
        actions = ic.repair_all(root)  # dry-run
        inv6 = _action(actions, "INV6")
        # planned an AUTO-FIX, but nothing applied and the index is untouched
        assert any(a.kind == "apply" and not a.applied for a in inv6)
        assert _sha(idx) == before
        assert not (root / ic.BACKUP_DIR).exists()

    def test_apply_appends_row_and_backs_up_first(self, tmp_path):
        root = healthy_arch(tmp_path)
        self._add_orphan(root)
        idx = root / "governance" / "proposals" / "index.md"
        before_bytes_sha = _sha(idx)  # raw bytes — what the backup must reproduce exactly

        actions = ic.repair_all(root, apply=True)
        inv6_apply = [a for a in _action(actions, "INV6") if a.kind == "apply"]
        assert inv6_apply and inv6_apply[0].applied is True

        # 1) the index now contains a row for the orphan file
        after_text = idx.read_text(encoding="utf-8")
        assert "2026-05-30-bar.md" in after_text
        assert _sha(idx) != before_bytes_sha

        # 2) a backup of the PRIOR index was written FIRST (byte-identical to pre-state)
        backups = _backups(root)
        assert len(backups) == 1, backups
        bkp = backups[0]
        assert bkp.name.startswith("index.md.") and bkp.name.endswith(".bak")
        assert hashlib.sha256(bkp.read_bytes()).hexdigest() == before_bytes_sha
        # and the action recorded that backup path
        assert inv6_apply[0].backup_path == bkp.relative_to(root).as_posix()

        # 3) re-checking INV6 is now clean for that file
        assert not any("2026-05-30-bar.md" in m for m in ic.check_inv6(root))

    def test_apply_flags_ghost_row_but_never_deletes(self, tmp_path):
        root = healthy_arch(tmp_path)
        idx = root / "governance" / "proposals" / "index.md"
        idx.write_text(
            idx.read_text(encoding="utf-8")
            + "| 2026-05-30 | [ghost](governance/proposals/2026-05-30-ghost.md) | x | ~ | pending |\n",
            encoding="utf-8",
        )
        before = idx.read_text(encoding="utf-8")
        actions = ic.repair_all(root, apply=True)
        ghosts = [a for a in _action(actions, "INV6") if a.kind == "manual"]
        assert ghosts and ghosts[0].requires_human
        assert any("2026-05-30-ghost.md" in d for d in ghosts[0].details)
        # The ghost row is FLAGGED, never removed — index still contains it.
        assert "2026-05-30-ghost.md" in idx.read_text(encoding="utf-8")
        # (no orphan present, so the only write that could happen didn't delete anything)
        assert "ghost" in before  # sanity


# ===========================================================================
# INV1 — STAGE ONLY. Must NEVER write the immutable lock, even with --apply.
# ===========================================================================

class TestINV1RepairStageOnly:
    def _add_uncovered_immutable(self, root: Path):
        # A new immutable file not present in the lock -> INV1 fires.
        _write(root / "extra.md", "---\nid: extra\nprotection: immutable\n---\n\n# extra\n")

    def test_lock_byte_identical_after_apply(self, tmp_path):
        """The core safety assertion: repair_all(apply=True) leaves .integrity.lock
        byte-identical even though INV1 is violated."""
        root = healthy_arch(tmp_path)
        self._add_uncovered_immutable(root)
        lock = root / ".integrity.lock"
        before = _sha(lock)

        actions = ic.repair_all(root, apply=True)

        assert _sha(lock) == before, "INV1 repair must NEVER write the immutable lock"
        inv1 = _action(actions, "INV1")
        assert inv1 and inv1[0].kind == "stage"
        assert inv1[0].requires_human is True
        assert inv1[0].applied is False
        # the live lock was not the thing backed up/written; INV1 never reports applied

    def test_apply_stages_proposed_lock_and_emits_bump_command(self, tmp_path):
        root = healthy_arch(tmp_path)
        self._add_uncovered_immutable(root)
        actions = ic.repair_all(root, apply=True)
        inv1 = _action(actions, "INV1")[0]

        # the integrity-bump command is emitted for the human gate
        assert any("integrity_check.py --regenerate" in d for d in inv1.details)
        # the missing file is named
        assert any("extra.md" in d for d in inv1.details)
        # a .proposed staged copy exists in _backups/, and it is NOT the live lock
        staged = root / ic.BACKUP_DIR / ".integrity.lock.proposed"
        assert staged.exists()
        assert staged != (root / ".integrity.lock")
        # staged content lists the new immutable file (so a human can diff before bump)
        assert "extra.md" in staged.read_text(encoding="utf-8")

    def test_dry_run_stages_nothing(self, tmp_path):
        root = healthy_arch(tmp_path)
        self._add_uncovered_immutable(root)
        actions = ic.repair_all(root)  # dry-run
        inv1 = _action(actions, "INV1")[0]
        assert inv1.kind == "stage"
        # dry-run emits the instruction but stages no .proposed file
        assert not (root / ic.BACKUP_DIR).exists()
        assert any("integrity_check.py --regenerate" in d for d in inv1.details)


# ===========================================================================
# INV4 — REPORT/STAGE only. Registry is guarded; never auto-written.
# ===========================================================================

class TestINV4Repair:
    def _drop_a_runner(self, root: Path) -> str:
        import session_start
        first_id = next(iter(session_start.TOOL_RUNNERS))
        reg = root / "governance" / "tools-registry.yaml"
        kept = [ln for ln in reg.read_text(encoding="utf-8").splitlines()
                if ln.strip() != f"- id: {first_id}"]
        reg.write_text("\n".join(kept) + "\n", encoding="utf-8")
        return first_id

    def test_apply_does_not_write_registry(self, tmp_path):
        root = healthy_arch(tmp_path)
        missing_id = self._drop_a_runner(root)
        reg = root / "governance" / "tools-registry.yaml"
        before = _sha(reg)
        actions = ic.repair_all(root, apply=True)
        inv4 = _action(actions, "INV4")[0]
        assert inv4.kind == "stage"
        assert inv4.applied is False
        assert _sha(reg) == before, "INV4 must never auto-write the guarded registry"
        # emits a stub mentioning the missing id for a human to complete
        assert any(missing_id in d for d in inv4.details)


# ===========================================================================
# INV2 / INV3 / INV5 — no auto-repair: manual/halt actions only.
# ===========================================================================

class TestManualInvariants:
    def test_inv2_manual_on_missing_retro(self, tmp_path):
        root = healthy_arch(tmp_path)
        log = root / "blocks" / "BLOCK_LOG.md"
        log.write_text(log.read_text(encoding="utf-8") + "block-003 done - 2026-05-22\n", encoding="utf-8")
        actions = ic.repair_all(root, apply=True)
        inv2 = _action(actions, "INV2")[0]
        assert inv2.kind == "manual"
        assert inv2.applied is False
        assert any("block-003" in d for d in inv2.details)

    def test_inv5_halt_on_pointer_drift(self, tmp_path):
        root = healthy_arch(tmp_path)
        _write(root / "STATE.md", "# STATE\np:1 status:active last_block:block-001 next:block-003\n")
        actions = ic.repair_all(root, apply=True)
        inv5 = _action(actions, "INV5")[0]
        assert inv5.kind == "halt"
        assert inv5.requires_human is True
        assert inv5.applied is False

    def test_inv3_manual_on_unresolvable_tier(self, tmp_path):
        root = healthy_arch(tmp_path)
        log = root / "blocks" / "BLOCK_LOG.md"
        log.write_text(log.read_text(encoding="utf-8") + "block-003 done - 2026-05-22\n", encoding="utf-8")
        _write(root / "blocks" / "block-003-gamma.md",
               "---\nid: block-003\nstatus: done\nactual_duration_hours: 3.0\n---\n# block-003 retro\n")
        actions = ic.repair_all(root, apply=True)
        inv3 = _action(actions, "INV3")[0]
        assert inv3.kind == "manual"
        assert any("block-003" in d for d in inv3.details)


# ===========================================================================
# _backup helper — direct unit checks
# ===========================================================================

class TestBackupHelper:
    def test_backup_copies_bytes_and_returns_rel_path(self, tmp_path):
        root = tmp_path / "arch"
        target = root / "governance" / "proposals" / "index.md"
        _write(target, "original content\n")
        rel = ic._backup(target, root)
        assert rel.startswith(ic.BACKUP_DIR + "/")
        backed = root / rel
        assert backed.read_text(encoding="utf-8") == "original content\n"

    def test_stamp_is_content_derived_and_stable(self, tmp_path):
        # Same content -> same stamp (no Date.now/random) -> idempotent backup name.
        s1 = ic._stamp(b"hello")
        s2 = ic._stamp(b"hello")
        s3 = ic._stamp(b"different")
        assert s1 == s2 != s3
        assert len(s1) == 8


# ===========================================================================
# CLI — --repair dry-run exits 0 and writes nothing; --apply still backs up.
# ===========================================================================

class TestRepairCLI:
    def test_repair_dry_run_exits_zero_no_writes(self, tmp_path):
        root = healthy_arch(tmp_path)
        # introduce an orphan so there's something to (not) write
        _write(root / "governance" / "proposals" / "2026-05-30-bar.md",
               "---\ncreated_at: 2026-05-30\nstatus: pending\n---\n# bar\n")
        before = {p: _sha(p) for p in root.rglob("*") if p.is_file()}
        rc = ic.main(["--arch-root", str(root), "--repair"])
        assert rc == 0
        after = {p: _sha(p) for p in root.rglob("*") if p.is_file()}
        assert before == after
        assert not (root / ic.BACKUP_DIR).exists()

    def test_repair_apply_exits_zero_and_writes_backup(self, tmp_path):
        root = healthy_arch(tmp_path)
        _write(root / "governance" / "proposals" / "2026-05-30-bar.md",
               "---\ncreated_at: 2026-05-30\nstatus: pending\n---\n# bar\n")
        rc = ic.main(["--arch-root", str(root), "--repair", "--apply"])
        assert rc == 0
        assert len(_backups(root)) >= 1  # at least the index backup

    def test_apply_without_repair_runs_check_only(self, tmp_path):
        root = healthy_arch(tmp_path)
        before = {p: _sha(p) for p in root.rglob("*") if p.is_file()}
        rc = ic.main(["--arch-root", str(root), "--apply"])  # no --repair
        assert rc == 0
        after = {p: _sha(p) for p in root.rglob("*") if p.is_file()}
        assert before == after
