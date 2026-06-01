# sdk/phase_manager.py
# PURPOSE: Automate phase start/close mechanical steps.
#          Phase-start: validates blocks done, updates STATE/NEXT/board.
#          Phase-close: generates retrospective scaffold, updates pointers.
#          Saves ~3000 tokens per phase transition.
# INPUTS:  phase_id, phases/*.md, blocks/BLOCK_LOG.md
# OUTPUTS: Updated STATE.md, NEXT.md, board.md; phase retro scaffold
# DEPS:    stdlib only; sdk/state_manager, sdk/board_manager
# USAGE:   python sdk/phase_manager.py --start phase-18 --arch-root .
#          python sdk/phase_manager.py --close phase-17 --arch-root .
# SEE:     commands/phase-start.md, commands/phase-close.md

from __future__ import annotations

import argparse
import io
import re
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


def _import_sdk(arch_root: Path) -> None:
    sdk = str(arch_root / "sdk")
    if sdk not in sys.path:
        sys.path.insert(0, sdk)


# ---------------------------------------------------------------------------
# Phase file reader
# ---------------------------------------------------------------------------

def _read_phase_meta(root: Path, phase_id: str) -> dict[str, str]:
    """Extract frontmatter fields from phases/<phase_id>.md.

    Dual-mode (block-163): also reads mode, type, client_id for corporate phases.
    """
    path = root / "phases" / f"{phase_id}.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    parts = text.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    meta: dict[str, str] = {}
    for key in ("id", "status", "blocks_count", "exit_criteria_count", "prev_phase",
                "mode", "type", "client_id"):
        m = re.search(rf"^{key}:\s*(.+)", fm, re.MULTILINE)
        if m:
            meta[key] = m.group(1).strip()
    # Extract phase number
    m = re.search(r"phase-(\d+)", phase_id)
    if m:
        meta["num"] = m.group(1)
    # Extract block IDs from Block Index section
    blocks = re.findall(r"\|\s*(block-\d+)\s*\|", text)
    meta["blocks"] = ",".join(blocks) if blocks else ""
    return meta


def _load_done_blocks(root: Path) -> set[str]:
    log = root / "blocks" / "BLOCK_LOG.md"
    if not log.exists():
        return set()
    done: set[str] = set()
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(block-\d+)\s+done", line)
        if m:
            done.add(m.group(1))
    return done


# ---------------------------------------------------------------------------
# Phase start
# ---------------------------------------------------------------------------

def start_phase(root: Path, phase_id: str, agent: str = "implementer") -> None:
    _import_sdk(root)
    from state_manager import update_state, update_next
    from board_manager import update_agent

    print(f"\n[phase_manager] Starting {phase_id}")

    meta = _read_phase_meta(root, phase_id)
    phase_num = meta.get("num", "?")
    mode = meta.get("mode", "mmorpg")
    phase_type = meta.get("type", "mmorpg")
    client_id = meta.get("client_id", "")

    # Check phase file exists
    phase_file = root / "phases" / f"{phase_id}.md"
    if not phase_file.exists():
        print(f"  ERROR: phases/{phase_id}.md not found. Create it first.")
        return

    print(f"  Mode: {mode} | Type: {phase_type}" + (f" | Client: {client_id}" if client_id else ""))

    # Workday type: no doc, only STATE entry
    if phase_type == "workday":
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        update_state(root, {
            "p": phase_num,
            "phase": phase_id,
            "status": "active",
            "status_detail": f"workday-{ts}",
            "current_workday": ts,
            "mode": mode,
        })
        print(f"  Workday: no doc generated — STATE updated with current_workday={ts}")
        return

    # Check previous phase done (optional warn)
    prev = meta.get("prev_phase", "")
    if prev:
        print(f"  Prev phase: {prev}")

    print(f"  Blocks in phase: {meta.get('blocks_count', '?')}")
    print(f"  Exit criteria: {meta.get('exit_criteria_count', '?')}")

    # Update STATE.md (includes mode and client_id for corporate)
    state_updates: dict[str, str] = {
        "p": phase_num,
        "phase": phase_id,
        "status": "active",
        "status_detail": f"{phase_id}-started",
        "mode": mode,
    }
    if client_id:
        state_updates["current_client"] = client_id
    update_state(root, state_updates)
    print(f"  STATE.md: p={phase_num} phase={phase_id} status=active mode={mode}")

    # Update NEXT.md
    blocks = meta.get("blocks", "")
    first_block = blocks.split(",")[0].strip() if blocks else "-"
    update_next(root, {
        "phase": phase_id,
        "status": "active",
        "next_action": first_block,
        "manifest": f"manifests/{first_block}-*.md" if first_block != "-" else "-",
        "group": "-",
    })
    print(f"  NEXT.md: next_action={first_block}")

    # Update board.md
    update_agent(root, agent, {"status": "idle", "lock": "ready", "group": "-", "b": "-"})
    print(f"  board.md: agent:{agent} status:idle")

    # block-173: stamp phase_started_at via velocity_tracker
    try:
        vt_path = root / "sdk" / "velocity_tracker.py"
        if vt_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("velocity_tracker", vt_path)
            vt = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vt)
            ts_started = vt.stamp_phase_started(root, phase_id)
            if ts_started:
                print(f"  velocity_tracker: phase_started_at={ts_started}")
    except Exception:
        pass

    print(f"\n  [phase_manager] {phase_id} started. Begin with block-start for {first_block}.")


# ---------------------------------------------------------------------------
# Phase close — generate retro scaffold
# ---------------------------------------------------------------------------

_RETRO_TEMPLATE = """---
id: {phase_id}-retrospective
phase: {phase_id}
status: done
blocks: [{blocks}]
exit_criteria_met: {criteria_count}/{criteria_count}
completed_at: {ts}
duration_actual_days: 1
---

# {phase_title} — Retrospective

## 1. Exit criteria

| # | Criterion | Block | Result |
|---|-----------|-------|--------|
{criteria_rows}

## 2. What was built

{blocks_section}

## 3. Tests added this phase

| Module | Tests |
|--------|-------|
| _fill in_ | _ |
| **Total** | **0** |

## 4. Key decisions

- _fill in_

## 5. Issues / surprises

_None._

---

End of {phase_id} retrospective.
"""


def close_phase(root: Path, phase_id: str, agent: str = "implementer") -> None:
    _import_sdk(root)
    from state_manager import update_state, update_next, read_state
    from board_manager import update_agent

    print(f"\n[phase_manager] Closing {phase_id}")

    meta = _read_phase_meta(root, phase_id)
    phase_num = meta.get("num", "?")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    # Check all blocks done
    blocks_str = meta.get("blocks", "")
    blocks = [b.strip() for b in blocks_str.split(",") if b.strip()]
    done = _load_done_blocks(root)
    undone = [b for b in blocks if b not in done]
    if undone:
        print(f"  WARN: Blocks not yet done: {undone}")
        print(f"  Close all blocks before closing phase.")

    # Determine next phase
    try:
        next_num = int(phase_num) + 1
        next_phase = f"phase-{next_num}"
    except (ValueError, TypeError):
        next_phase = "-"

    # Read phase file for title
    phase_file = root / "phases" / f"{phase_id}.md"
    phase_title = f"Phase {phase_num} Retrospective"
    if phase_file.exists():
        text = phase_file.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^# Phase \d+ — (.+)$", text, re.MULTILINE)
        if m:
            phase_title = f"Phase {phase_num} — {m.group(1)}"

    # Generate retro scaffold
    criteria_count = meta.get("exit_criteria_count", "?")
    criteria_rows = "\n".join(
        f"| {i+1} | _fill in_ | _block_ | ✓ |"
        for i in range(int(criteria_count) if criteria_count.isdigit() else 1)
    )
    blocks_section = "\n".join(
        f"**{b}:** _fill in_\n" for b in blocks
    ) if blocks else "_fill in_"

    retro_content = _RETRO_TEMPLATE.format(
        phase_id=phase_id,
        phase_title=phase_title,
        blocks=", ".join(blocks),
        criteria_count=criteria_count,
        ts=ts,
        criteria_rows=criteria_rows,
        blocks_section=blocks_section,
    )

    # Write retro scaffold
    retro_path = root / "blocks" / f"{phase_id}-retrospective.md"
    if retro_path.exists():
        print(f"  WARN: {retro_path.name} already exists — not overwriting")
    else:
        retro_path.write_text(retro_content, encoding="utf-8")
        print(f"  Created: blocks/{phase_id}-retrospective.md (scaffold — fill in details)")

    # Update STATE.md (preserve mode if set)
    state = read_state(root)
    close_updates: dict[str, str] = {
        "p": phase_num,
        "phase": phase_id,
        "status": "complete",
        "last_phase": phase_id,
        "last_phase_status": "done",
        "status_detail": f"{phase_id}-complete",
    }
    if state.get("mode"):
        close_updates["mode"] = state["mode"]
    update_state(root, close_updates)

    # Stamp phase_finished_at in phase file (block-173 velocity tracking)
    phase_file = root / "phases" / f"{phase_id}.md"
    if phase_file.exists():
        phase_text = phase_file.read_text(encoding="utf-8", errors="replace")
        if "phase_finished_at:" in phase_text:
            phase_text = re.sub(
                r"^phase_finished_at:\s*~?\s*$",
                f"phase_finished_at: {ts}",
                phase_text,
                flags=re.MULTILINE,
            )
            phase_file.write_text(phase_text, encoding="utf-8")

    print(f"  STATE.md: status=complete last_phase={phase_id}")

    # Update NEXT.md
    if (root / "phases" / f"{next_phase}.md").exists():
        update_next(root, {
            "phase": next_phase,
            "status": "phase-start-pending",
            "next_action": f"start-{next_phase}",
            "manifest": "-",
        })
        print(f"  NEXT.md: next phase is {next_phase}")
    else:
        update_next(root, {
            "phase": phase_id,
            "status": "complete",
            "next_action": "-",
            "note": "all-phases-complete",
        })
        print(f"  NEXT.md: no next phase — project complete")

    # Update board
    update_agent(root, agent, {"status": "idle", "lock": "ready", "b": "-", "group": "-"})
    print(f"  board.md: agent:{agent} status:idle")

    # block-173: stamp phase_finished_at via velocity_tracker
    try:
        vt_path = root / "sdk" / "velocity_tracker.py"
        if vt_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("velocity_tracker", vt_path)
            vt = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(vt)
            _, phase_hours = vt.stamp_phase_finished(root, phase_id)
            if phase_hours:
                print(f"  velocity_tracker: phase_duration_hours={phase_hours}")
    except Exception:
        pass

    print(f"\n  [phase_manager] {phase_id} closed. Fill in retro scaffold at blocks/{phase_id}-retrospective.md")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase lifecycle manager")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--start", metavar="PHASE_ID", help="Start a phase (e.g. phase-18)")
    parser.add_argument("--close", metavar="PHASE_ID", help="Close a phase (e.g. phase-17)")
    parser.add_argument("--agent", default="implementer", help="Agent name")
    args = parser.parse_args()

    root = Path(args.arch_root).resolve()

    if args.start:
        start_phase(root, args.start, args.agent)
    elif args.close:
        close_phase(root, args.close, args.agent)
    else:
        parser.print_help()
