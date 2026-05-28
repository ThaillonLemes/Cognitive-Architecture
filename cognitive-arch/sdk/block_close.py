# sdk/block_close.py
# PURPOSE: Automate the mechanical steps of block-close (steps 2,3,4,6).
#          Step 1 (gates), 5 (retro), 7 (commit), 8 (emit next) stay with AI.
#          Saves ~3500 tokens per block close.
# INPUTS:  block_id, arch_root, optional actual_hours and next_block
# OUTPUTS: Updated STATE.md, NEXT.md, BLOCK_LOG.md, board.md
# DEPS:    stdlib only; sdk/state_manager, sdk/board_manager
# USAGE:   python sdk/block_close.py --block-id block-112 --arch-root .
#          python sdk/block_close.py --block-id block-112 --actual-hours 2.5 --next block-113
# SEE:     commands/block-close.md, protocols/block-close-checklist.md

from __future__ import annotations

import argparse
import io
import sys
from datetime import datetime, timezone
from pathlib import Path

def _fix_utf8():
    """Apply UTF-8 stdout fix on Windows — safe to call multiple times."""
    import io as _io
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'buffer') and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == 'utf-8'
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_fix_utf8()

# ---------------------------------------------------------------------------
# Internal imports (relative to sdk/)
# ---------------------------------------------------------------------------

def _import_sdk(arch_root: Path) -> None:
    sdk = str(arch_root / "sdk")
    if sdk not in sys.path:
        sys.path.insert(0, sdk)


# ---------------------------------------------------------------------------
# BLOCK_LOG append
# ---------------------------------------------------------------------------

def append_block_log(arch_root: Path, block_id: str, event: str = "done") -> None:
    """Append one line to BLOCK_LOG.md: '<block_id> <event> - <date>'"""
    log_path = arch_root / "blocks" / "BLOCK_LOG.md"
    if not log_path.exists():
        return
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    line = f"{block_id} {event} - {date_str}"
    # Avoid duplicates
    existing = log_path.read_text(encoding="utf-8", errors="replace")
    if f"{block_id} {event}" in existing:
        print(f"  BLOCK_LOG: {block_id} already logged — skipping")
        return
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(f"  BLOCK_LOG: appended [{line}]")


# ---------------------------------------------------------------------------
# Manifest reader (for phase + tier info)
# ---------------------------------------------------------------------------

def _read_manifest_meta(arch_root: Path, block_id: str) -> dict[str, str]:
    """Return {phase, tier, next_block} from manifest if available."""
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if not candidates:
        return {}
    import re
    text = candidates[0].read_text(encoding="utf-8", errors="replace")
    meta: dict[str, str] = {}
    for key in ("phase", "tier", "kind"):
        m = re.search(rf"^{key}:\s*(\S+)", text, re.MULTILINE)
        if m:
            meta[key] = m.group(1)
    return meta


# ---------------------------------------------------------------------------
# Retro checker
# ---------------------------------------------------------------------------

def _check_retro(arch_root: Path, block_id: str) -> bool:
    """Return True if a retro file exists for this block."""
    retros = list((arch_root / "blocks").glob(f"{block_id}-*.md"))
    # Exclude BLOCK_LOG.md itself
    retros = [r for r in retros if "LOG" not in r.name.upper()]
    return len(retros) > 0


def _check_actual_hours(arch_root: Path, block_id: str) -> bool | None:
    """Return True if actual_duration_hours is filled in retro, None if retro not found."""
    import re
    retros = list((arch_root / "blocks").glob(f"{block_id}-*.md"))
    retros = [r for r in retros if "LOG" not in r.name.upper()]
    if not retros:
        return None
    text = retros[0].read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^actual_duration_hours:\s*([0-9.]+)", text, re.MULTILINE)
    return m is not None


# ---------------------------------------------------------------------------
# Main close function
# ---------------------------------------------------------------------------

def close_block(
    arch_root: Path,
    block_id: str,
    actual_hours: float | None = None,
    next_block: str | None = None,
    agent: str = "implementer",
    force: bool = False,
) -> dict[str, str | bool]:
    """
    Execute mechanical block-close steps:
      2. update STATE.md
      3. update NEXT.md
      4. append BLOCK_LOG.md
      6. update board.md

    Returns summary dict with results of each step.
    """
    _import_sdk(arch_root)
    from state_manager import update_state, update_next, read_state
    from board_manager import update_agent

    results: dict[str, str | bool] = {}
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block_num = block_id.replace("block-", "")

    print(f"\n[block_close] Closing {block_id}")
    print(f"  agent={agent} | next={next_block or 'TBD'} | hours={actual_hours or 'not set'}")

    # --- Pre-checks ---
    has_retro = _check_retro(arch_root, block_id)
    has_hours = _check_actual_hours(arch_root, block_id)

    if not has_retro and not force:
        print(f"  WARN: No retro file found for {block_id}. Write retro (step 5) before closing.")
        results["retro_check"] = "missing"
    else:
        results["retro_check"] = "ok" if has_retro else "missing"

    if has_hours is False:
        print(f"  WARN: actual_duration_hours missing in retro (axiom velocity tracking).")
        results["hours_check"] = "missing"
    elif has_hours is None:
        results["hours_check"] = "no_retro"
    else:
        results["hours_check"] = "ok"

    # Manifest meta
    meta = _read_manifest_meta(arch_root, block_id)
    phase = meta.get("phase", read_state(arch_root).get("phase", "unknown"))

    # --- Step 2: STATE.md ---
    state_updates = {
        "last_block": block_id,
        "last_block_status": "done",
        "status": "active",
    }
    update_state(arch_root, state_updates)
    print(f"  STATE.md: last_block={block_id} last_block_status=done")
    results["state"] = "ok"

    # --- Step 3: NEXT.md ---
    next_updates: dict[str, str] = {
        "phase": phase,
        "status": "active" if next_block else "phase-close-pending",
    }
    if next_block:
        next_updates["next_action"] = next_block
        next_updates["manifest"] = f"manifests/{next_block}-*.md"
    else:
        next_updates["next_action"] = "phase-close"
        next_updates["manifest"] = "-"
    update_next(arch_root, next_updates)
    print(f"  NEXT.md: next_action={next_updates['next_action']}")
    results["next"] = "ok"

    # --- Step 4: BLOCK_LOG.md ---
    append_block_log(arch_root, block_id)
    results["block_log"] = "ok"

    # --- Step 6: board.md ---
    board_updates = {
        "b": block_num,
        "status": "done",
        "lock": "ready",
        "last_done": block_id,
    }
    ok = update_agent(arch_root, agent, board_updates)
    print(f"  board.md: agent:{agent} status:done last_done:{block_id} — {'ok' if ok else 'agent not found'}")
    results["board"] = "ok" if ok else "agent_not_found"

    print(f"\n  [block_close] Done. Remaining AI steps: 1-gates 5-retro 7-commit 8-emit-next")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate mechanical block-close steps")
    parser.add_argument("--block-id", required=True, help="e.g. block-112")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--actual-hours", type=float, help="Actual duration in hours")
    parser.add_argument("--next", dest="next_block", help="Next block ID (e.g. block-113)")
    parser.add_argument("--agent", default="implementer", help="Agent name in board.md")
    parser.add_argument("--force", action="store_true", help="Skip retro pre-check")
    args = parser.parse_args()

    root = Path(args.arch_root).resolve()
    close_block(
        arch_root=root,
        block_id=args.block_id,
        actual_hours=args.actual_hours,
        next_block=args.next_block,
        agent=args.agent,
        force=args.force,
    )
