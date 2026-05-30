# PURPOSE: Apply Governor group integration — update state files after a parallel block group completes
# INPUTS:  list of DispatchResult objects, arch_root path, next block pointer
# OUTPUTS: updated STATE.md, NEXT.md, BLOCK_LOG.md, board.md; optional git commit
# DEPS:    sdk/return_validator (ValidationResult), stdlib (pathlib, datetime, subprocess, re)
# SEE:     protocols/governor-integration.md, protocols/governor-dispatch.md §5,
#          design/governor-v2.md §6 step 5, sdk/dispatch.py, sdk/return_validator.py

"""
State integration module.

After a parallel group of sub-agents completes, Governor calls integrate_group() to:
  1. Verify no fmod conflicts between parallel blocks (disjoint check)
  2. Update STATE.md with latest block info
  3. Append BLOCK_LOG.md entries
  4. Update board.md rows to status:done
  5. Update NEXT.md with next block pointer
  6. Attempt git commit (no-op if no git repo)

All file writes are atomic: write to temp path, then rename.

Usage (module):
    from sdk.integration import integrate_group, IntegrationResult
    result = integrate_group(dispatch_results, arch_root, next_block="035")

Usage (CLI test):
    python sdk/integration.py --test
"""

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_SDK_DIR = Path(__file__).resolve().parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

# DispatchResult imported lazily to avoid circular import; used only as type hint.
# integrate_group() accepts any list of objects with .block_id, .success, .validation attrs.


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class IntegrationResult:
    success: bool
    blocks_integrated: list[str] = field(default_factory=list)
    blocks_failed: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    committed: bool = False
    commit_hash: Optional[str] = None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def check_fmod_disjoint(results: list) -> list[str]:
    """
    Verify that no two DispatchResults in a parallel group modify the same file.

    Returns a list of conflict descriptions (empty = no conflicts).
    """
    seen: dict[str, str] = {}  # path → block_id that claimed it
    conflicts: list[str] = []
    for r in results:
        if not r.validation or not r.validation.valid:
            continue
        fmod_raw = r.validation.parsed.get("fmod", "-")
        if fmod_raw == "-":
            continue
        for entry in fmod_raw.split(","):
            path = entry.split(":")[0].strip()
            if path and path != "-":
                if path in seen:
                    conflicts.append(
                        f"conflict: '{path}' claimed by block-{seen[path]} and block-{r.block_id}"
                    )
                else:
                    seen[path] = r.block_id
    return conflicts


# ---------------------------------------------------------------------------
# Atomic file write
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, content: str) -> None:
    """Write content to path atomically (write temp → rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# State file updaters
# ---------------------------------------------------------------------------

def _update_state_md(arch_root: Path, last_block: str, next_block: str, blocks_done_extra: list[str]) -> None:
    """Update STATE.md with new last_block and next pointer."""
    state_path = arch_root / "STATE.md"
    if not state_path.exists():
        return

    content = state_path.read_text(encoding="utf-8")
    # Update last_block
    content = re.sub(r"last_block:\S+", f"last_block:block-{last_block}", content)
    content = re.sub(r"last_block_status:\S+", "last_block_status:done", content)
    content = re.sub(r"next:\S+", f"next:block-{next_block}", content)
    content = re.sub(r"last_updated:\S+", f"last_updated:{_now()}", content)
    content = re.sub(r"status_detail:\S+", f"status_detail:block-{last_block}-done", content)

    # blocks_done is no longer maintained inline in STATE.md (block-141): blocks/BLOCK_LOG.md
    # is the single source of truth for the done-set (read via project_state.completed_block_ids).
    # blocks_done_extra is accepted for signature compatibility but intentionally unused.
    _ = blocks_done_extra

    _atomic_write(state_path, content)


def _update_next_md(arch_root: Path, next_block: str, note: str = "") -> None:
    """Update NEXT.md to point to the next block."""
    next_path = arch_root / "NEXT.md"
    if not next_path.exists():
        return
    content = next_path.read_text(encoding="utf-8")
    slug = f"block-{next_block}-start"
    manifest = f"manifests/block-{next_block}-"
    content = re.sub(r"next_action:\S+", f"next_action:{slug}", content)
    content = re.sub(r"manifest:\S+", f"manifest:{manifest}<slug>.md", content)
    if note:
        content = re.sub(r"notes:\S+", f"notes:{note}", content)
    _atomic_write(next_path, content)


def _append_block_log(arch_root: Path, block_ids: list[str]) -> None:
    """Append one line per block to BLOCK_LOG.md."""
    log_path = arch_root / "blocks" / "BLOCK_LOG.md"
    if not log_path.exists():
        return
    today = _now_date()
    lines_to_add = "\n".join(f"block-{bid} done - {today}" for bid in block_ids)
    existing = log_path.read_text(encoding="utf-8")
    _atomic_write(log_path, existing.rstrip() + "\n" + lines_to_add + "\n")


def _update_board(arch_root: Path, block_ids: list[str]) -> None:
    """Update board.md rows to status:done for completed blocks."""
    board_path = arch_root / "board.md"
    if not board_path.exists():
        return
    content = board_path.read_text(encoding="utf-8")
    # Update agent row if it matches any of our block IDs
    for bid in block_ids:
        content = re.sub(
            rf"(agent:\S+\s+b:{bid}\s+\S+\s+)status:\S+\s+lock:\S+",
            rf"\1status:done lock:ready",
            content,
        )
    _atomic_write(board_path, content)


# ---------------------------------------------------------------------------
# Git commit (best-effort)
# ---------------------------------------------------------------------------

def _try_git_commit(arch_root: Path, block_ids: list[str]) -> tuple[bool, Optional[str]]:
    """
    Attempt a git commit. Returns (committed, commit_hash).
    No-op (returns False, None) if no git repo found.
    """
    summary = ",".join(f"block-{b}" for b in block_ids)
    msg = f"integrate {summary}: Governor v2 group integration"
    try:
        result = subprocess.run(
            ["git", "add", "-A"],
            cwd=arch_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return False, None  # No git repo

        result = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=arch_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            # Extract commit hash from output
            hash_match = re.search(r"\[[\w\-]+ ([0-9a-f]{7,})\]", result.stdout)
            commit_hash = hash_match.group(1) if hash_match else None
            return True, commit_hash
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return False, None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _now_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def integrate_group(
    results: list,
    arch_root: Path,
    next_block: str,
    do_commit: bool = True,
) -> IntegrationResult:
    """
    Integrate a completed parallel block group into project state.

    Args:
        results:    List of DispatchResult objects from the group.
        arch_root:  Path to cognitive-arch/ directory.
        next_block: ID of the next block to point NEXT.md at (e.g. "035").
        do_commit:  Whether to attempt git commit (best-effort).

    Returns:
        IntegrationResult with success flag and details.
    """
    ir = IntegrationResult(success=False)

    # Separate successful results
    successful = [r for r in results if r.success and r.validation and r.validation.valid]
    failed     = [r for r in results if not r.success or not (r.validation and r.validation.valid)]

    ir.blocks_failed = [r.block_id for r in failed]

    if not successful:
        ir.errors.append("No successful blocks to integrate")
        return ir

    # 1. Conflict check
    conflicts = check_fmod_disjoint(successful)
    if conflicts:
        ir.conflicts = conflicts
        ir.errors.extend(conflicts)
        # Continue with non-conflicting blocks (best-effort)

    block_ids = [r.block_id for r in successful]
    last_block = block_ids[-1]

    # 2. Update STATE.md
    try:
        _update_state_md(arch_root, last_block, next_block, block_ids)
    except Exception as exc:
        ir.errors.append(f"STATE.md update failed: {exc}")

    # 3. Append BLOCK_LOG.md
    try:
        _append_block_log(arch_root, block_ids)
    except Exception as exc:
        ir.errors.append(f"BLOCK_LOG.md append failed: {exc}")

    # 4. Update board.md
    try:
        _update_board(arch_root, block_ids)
    except Exception as exc:
        ir.errors.append(f"board.md update failed: {exc}")

    # 5. Update NEXT.md
    try:
        _update_next_md(arch_root, next_block)
    except Exception as exc:
        ir.errors.append(f"NEXT.md update failed: {exc}")

    # 6. Git commit (best-effort)
    if do_commit:
        committed, commit_hash = _try_git_commit(arch_root, block_ids)
        ir.committed = committed
        ir.commit_hash = commit_hash

    ir.blocks_integrated = block_ids
    ir.success = len(ir.errors) == 0 or (len(ir.blocks_integrated) > 0 and len(ir.conflicts) == 0)
    return ir


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli_test() -> int:
    """Self-test using a temporary arch_root directory."""
    import shutil

    # Build a minimal temp arch_root
    tmp = Path(tempfile.mkdtemp())
    try:
        # Create minimal STATE.md
        (tmp / "STATE.md").write_text(
            "# STATE — AI-only\n\n"
            "p:5 status:active last_block:block-033 last_block_status:done "
            "next:block-034 last_updated:2026-05-22 status_detail:block-033-done "
            "blocks_done:block-001,block-033\n",
            encoding="utf-8",
        )
        # Create minimal NEXT.md
        (tmp / "NEXT.md").write_text(
            "# NEXT — AI-only\n\nstatus:active next_action:block-034-start "
            "manifest:manifests/block-034-x.md notes:test\n",
            encoding="utf-8",
        )
        # Create minimal BLOCK_LOG.md
        (tmp / "blocks").mkdir()
        (tmp / "blocks" / "BLOCK_LOG.md").write_text(
            "# BLOCK_LOG\nblock-033 done - 2026-05-22\n",
            encoding="utf-8",
        )
        # Create minimal board.md
        (tmp / "board.md").write_text(
            "# board\nagent:implementer b:034 group:5C status:wip lock:in-progress deps:- ts:2026-05-22\n",
            encoding="utf-8",
        )

        # Build mock DispatchResult objects (minimal stand-ins with distinct fmod paths)
        class _MockResult:
            def __init__(self, block_id, fmod_path):
                self.block_id = block_id
                self.success = True

                class _V:
                    valid = True
                    errors = []
                    parsed = {"status": "done", "fmod": fmod_path, "fread": "-"}

                self.validation = _V()

        results = [_MockResult("034", "sdk/integration.py:180"), _MockResult("036", "sdk/config.py:60")]

        # Test 1: normal integration
        ir = integrate_group(results, tmp, next_block="035", do_commit=False)
        errors: list[str] = []

        if not ir.success:
            errors.append(f"integrate_group returned success=False: {ir.errors}")

        state_content = (tmp / "STATE.md").read_text(encoding="utf-8")
        if "block-034" not in state_content:
            errors.append("STATE.md not updated with block-034")

        log_content = (tmp / "blocks" / "BLOCK_LOG.md").read_text(encoding="utf-8")
        if "block-034 done" not in log_content:
            errors.append("BLOCK_LOG.md not appended with block-034")

        # Test 2: conflict detection
        class _ConflictValidation:
            valid = True
            parsed = {"status": "done", "fmod": "sdk/conflict_file.py:50", "fread": "-"}
            errors = []

        class _ConflictResult:
            def __init__(self, block_id):
                self.block_id = block_id
                self.success = True
                self.validation = _ConflictValidation()

        conflict_results = [_ConflictResult("034"), _ConflictResult("035")]
        conflicts = check_fmod_disjoint(conflict_results)
        if not conflicts:
            errors.append("conflict detection failed: expected conflict for same fmod path")

        if errors:
            for e in errors:
                print(f"FAIL: {e}", file=sys.stderr)
            return 1

        print("integration --test: PASS")
        print(f"  Blocks integrated : {ir.blocks_integrated}")
        print(f"  STATE.md updated  : yes (block-034 found)")
        print(f"  BLOCK_LOG appended: yes")
        print(f"  Conflict detection: yes (2-block conflict caught)")
        return 0

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="integration",
        description="Governor v2 state integration module.",
    )
    parser.add_argument("--test", action="store_true", help="Run self-test in temp directory.")
    args = parser.parse_args()

    if args.test:
        sys.exit(_cli_test())
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
