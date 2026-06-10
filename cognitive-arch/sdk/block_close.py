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
    """Return {phase, tier, kind, size, importance, wip_stage} from manifest if available.

    Block-164: extended to include v2 fields (size, importance) and wip_stage.
    """
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if not candidates:
        return {}
    import re
    text = candidates[0].read_text(encoding="utf-8", errors="replace")
    meta: dict[str, str] = {}
    for key in ("phase", "tier", "kind", "size", "importance", "wip_stage"):
        m = re.search(rf"^{key}:\s*(\S+)", text, re.MULTILINE)
        if m:
            meta[key] = m.group(1)
    return meta


def _read_phase_mode(arch_root: Path, phase_id: str) -> str:
    """Return mode of a phase (mmorpg|corporate|shared). Default: mmorpg."""
    import re
    phase_file = arch_root / "phases" / f"{phase_id}.md"
    if not phase_file.exists():
        return "mmorpg"
    text = phase_file.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^mode:\s*(\S+)", text, re.MULTILINE)
    return m.group(1) if m else "mmorpg"


def _check_wip_stage_corporate(arch_root: Path, block_id: str, phase_id: str) -> tuple[bool, str]:
    """For corporate blocks, verify wip_stage reached 'teaching' before done.

    Returns (ok, message). Passes if mode is not corporate.
    """
    import re
    mode = _read_phase_mode(arch_root, phase_id)
    if mode not in ("corporate",):
        return True, ""

    # Read retro to find wip_stage_reached
    retros = list((arch_root / "blocks").glob(f"{block_id}-*.md"))
    retros = [r for r in retros if "LOG" not in r.name.upper()]
    if not retros:
        return True, "no_retro_skip"  # retro check will catch this

    text = retros[0].read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^wip_stage_reached:\s*(\S+)", text, re.MULTILINE)
    if not m:
        return False, f"HALT: corporate block must have wip_stage_reached in retro. Add 'wip_stage_reached: teaching'."
    stage = m.group(1)
    if stage != "teaching":
        return False, f"HALT: corporate block wip_stage must reach 'teaching' before done (found: {stage})."
    return True, ""


def _check_code_review_gate(
    arch_root: Path, block_id: str, phase_id: str, force: bool = False
) -> tuple[bool, str]:
    """Run code review (Bugbot) gate. Returns (ok, message).

    Normal mode  : blocks on security/bug findings; quality findings → logged, pass.
    Corporate mode: blocks on any finding.
    force=True   : always passes (findings still logged to bugs.md).
    """
    cr_path = arch_root / "sdk" / "code_review.py"
    if not cr_path.exists():
        return True, "INFO: code_review.py not found — gate skipped"

    mode = _read_phase_mode(arch_root, phase_id)

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("code_review", cr_path)
        cr_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cr_mod)
        result = cr_mod.review_block(block_id, arch_root, mode=mode, force=force)
        if result.blocked and not force:
            return False, f"HALT: {result.block_reason}"
        n = len(result.findings)
        if n == 0:
            return True, ""
        return True, f"INFO: code review: {n} finding(s) logged to governance/bugs.md"
    except Exception as exc:
        return True, f"WARN: code_review gate error ({exc}) — skipped"


def _check_consistency_checker_gate(arch_root: Path, block_id: str, phase_id: str) -> tuple[bool, str]:
    """Run consistency-check gate if mode=corporate and checker is available."""
    import re
    mode = _read_phase_mode(arch_root, phase_id)
    if mode != "corporate":
        return True, ""

    checker = arch_root / "sdk" / "consistency_checker.py"
    if not checker.exists():
        return True, "WARN: consistency_checker.py not yet implemented — gate skipped"

    # Find project profile
    import subprocess
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if not candidates:
        return True, ""
    text = candidates[0].read_text(encoding="utf-8", errors="replace")
    client_m = re.search(r"^client_id:\s*(\S+)", text, re.MULTILINE)
    if not client_m:
        return True, "WARN: no client_id in manifest — consistency gate skipped"

    client_id = client_m.group(1)
    profile = arch_root / "governance" / f"project-profile-{client_id}.md"
    if not profile.exists():
        return True, f"WARN: no project-profile for {client_id} — consistency gate skipped"

    result = subprocess.run(
        [sys.executable, str(checker), "--profile", str(profile), "--arch-root", str(arch_root)],
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    if "consistency_score" in result.stdout:
        return True, result.stdout.strip().splitlines()[0] if result.stdout else "ok"
    return result.returncode == 0, result.stdout.strip() or result.stderr.strip()


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


def _check_tok_actual(arch_root: Path, block_id: str, force: bool = False) -> tuple[bool, str]:
    """Check tok_actual field presence in retro. Returns (ok, message).

    Returns (True, '') if field is present and non-empty.
    Returns (False, msg) if missing, empty, or null — unless force=True.
    Returns (True, 'no_retro') if no retro file found (handled by _check_retro).
    """
    import re
    retros = list((arch_root / "blocks").glob(f"{block_id}-*.md"))
    retros = [r for r in retros if "LOG" not in r.name.upper()]
    if not retros:
        return (True, "no_retro")
    text = retros[0].read_text(encoding="utf-8", errors="replace")
    # Accept: tok_actual, tok-actual, tokens_actual variants
    pattern = r"^(?:tok_actual|tok-actual|tokens_actual):\s*(.+)"
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        msg = f"WARN: tok_actual missing in retro for {block_id}. Add tok_actual field or use --force."
        return (False, msg)
    value = m.group(1).strip()
    if value.lower() in ("", "null", "~", "none"):
        msg = f"WARN: tok_actual is null/empty in retro for {block_id}. Set actual token count or use --force."
        return (False, msg)
    return (True, "")


# ---------------------------------------------------------------------------
# Main close function
# ---------------------------------------------------------------------------

def pause_block(arch_root: Path, block_id: str, reason: str = "") -> None:
    """Mark a block as paused (block-164). Does not close it."""
    from state_manager import update_state
    update_state(arch_root, {
        "last_block": block_id,
        "wip_stage": "paused",
        "status": "active",
    })
    print(f"[block_pause] {block_id} paused. Reason: {reason or 'not specified'}")
    # Update manifest paused_reason field if present
    import re
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    if candidates and reason:
        text = candidates[0].read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"^paused_reason:\s*~?\s*$", f"paused_reason: {reason}", text, flags=re.MULTILINE)
        text = re.sub(r"^status:\s*\S+", "status: paused", text, flags=re.MULTILINE)
        candidates[0].write_text(text, encoding="utf-8")


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
        print(f"  HALT: Use --force to bypass retro check.")
        results["retro_check"] = "missing"
        results["halted"] = True
        return results
    else:
        results["retro_check"] = "ok" if has_retro else "missing"

    if has_hours is False:
        print(f"  WARN: actual_duration_hours missing in retro (axiom velocity tracking).")
        results["hours_check"] = "missing"
    elif has_hours is None:
        results["hours_check"] = "no_retro"
    else:
        results["hours_check"] = "ok"

    # tok_actual check (Phase 18 — mandatory token tracking)
    tok_ok, tok_msg = _check_tok_actual(arch_root, block_id, force)
    if not tok_ok:
        print(f"  {tok_msg}")
        results["tok_actual_check"] = "missing"
        if not force:
            print(f"  HALT: Use --force to bypass tok_actual check.")
            results["halted"] = True
            return results
    else:
        results["tok_actual_check"] = tok_msg if tok_msg == "no_retro" else "ok"

    # Manifest meta
    meta = _read_manifest_meta(arch_root, block_id)
    phase = meta.get("phase", read_state(arch_root).get("phase", "unknown"))

    # block-164: corporate wip_stage check (only for kind: ticket)
    if not force and meta.get("kind") in ("ticket",):
        wip_ok, wip_msg = _check_wip_stage_corporate(arch_root, block_id, phase)
        if not wip_ok:
            print(f"  {wip_msg}")
            results["wip_stage_check"] = "failed"
            results["halted"] = True
            return results
        elif wip_msg.startswith("WARN"):
            print(f"  {wip_msg}")

    # block-164: consistency-check gate for corporate tickets
    if not force and meta.get("kind") in ("ticket",):
        con_ok, con_msg = _check_consistency_checker_gate(arch_root, block_id, phase)
        if con_msg.startswith("WARN"):
            print(f"  {con_msg}")
        elif not con_ok:
            print(f"  HALT: consistency-check gate failed: {con_msg}")
            results["consistency_check"] = "failed"
            results["halted"] = True
            return results
        results["consistency_check"] = "ok"

    # block-180: code review gate
    cr_ok, cr_msg = _check_code_review_gate(arch_root, block_id, phase, force)
    if cr_msg.startswith("WARN") or cr_msg.startswith("INFO"):
        print(f"  {cr_msg}")
    elif not cr_ok:
        print(f"  {cr_msg}")
        results["code_review"] = "blocked"
        results["halted"] = True
        return results
    results["code_review"] = "ok" if cr_ok else cr_msg

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

    # block-173: stamp finished_at and compute actual_duration_hours
    try:
        vt_path = arch_root / "sdk" / "velocity_tracker.py"
        if vt_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("velocity_tracker", vt_path)
            vt = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vt)
            fin_ts, act_h = vt.stamp_finished(arch_root, block_id)
            if fin_ts:
                print(f"  velocity_tracker: finished_at={fin_ts} actual_hours={act_h}")
    except Exception:
        pass  # never block close on tracker failure

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

    # block-172: surface teach HTMLs if teach_mode was run
    gov_dir_t = arch_root / "governance"
    if gov_dir_t.exists():
        teach_files = sorted(gov_dir_t.glob(f"teach-{block_id}-*.html"))
        if teach_files:
            print(f"  Teach HTMLs: {', '.join(f.name for f in teach_files)}")

    # block-171: surface quality HTML if review_pipeline was run
    gov_dir = arch_root / "governance"
    if gov_dir.exists():
        review_files = sorted(gov_dir.glob(f"review-{block_id}-*.html"))
        if review_files:
            print(f"  Quality HTML: {review_files[-1].name}")

    # block-179: surface notifications at block close (corporate mode only)
    mode = meta.get("mode", read_state(arch_root).get("mode", "mmorpg"))
    if mode == "corporate":
        try:
            from notification_manager import surface, TRIGGER_BLOCK_CLOSE
            surface(TRIGGER_BLOCK_CLOSE, arch_root)
        except Exception:
            pass

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
