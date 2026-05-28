# sdk/board_manager.py
# PURPOSE: Read and update board.md agent rows without AI manual editing.
#          Saves ~800 tokens per board update operation.
# INPUTS:  board.md (compact key:value rows per _syntax.md)
# OUTPUTS: Updated board.md in place
# DEPS:    stdlib only (pathlib, re, datetime)
# USAGE:   python sdk/board_manager.py --agent implementer --status done --last-done block-112
#          python sdk/board_manager.py --read
# SEE:     _syntax.md, board.md, protocols/agents.md

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

_BOARD_FILE = "board.md"
_AGENT_PATTERN = re.compile(r"^agent:(\S+)\s+(.+)$")


# ---------------------------------------------------------------------------
# Parse / serialize
# ---------------------------------------------------------------------------

def _parse_agent_row(line: str) -> dict[str, str] | None:
    """Parse 'agent:name key:val ...' into dict. Returns None if not an agent row."""
    m = _AGENT_PATTERN.match(line.strip())
    if not m:
        return None
    data: dict[str, str] = {"agent": m.group(1)}
    for km in re.finditer(r"(\w+):([^\s]+)", m.group(2)):
        data[km.group(1)] = km.group(2)
    return data


def _serialize_agent_row(data: dict[str, str]) -> str:
    """Serialize agent dict back to board.md row."""
    agent = data.pop("agent", "unknown")
    parts = [f"agent:{agent}"]
    for k, v in data.items():
        parts.append(f"{k}:{v}")
    return " ".join(parts)


def read_board(arch_root: Path) -> list[dict[str, str]]:
    """Return list of agent dicts from board.md."""
    path = arch_root / _BOARD_FILE
    if not path.exists():
        return []
    agents = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        row = _parse_agent_row(line)
        if row:
            agents.append(row)
    return agents


def update_agent(arch_root: Path, agent_name: str, updates: dict[str, str]) -> bool:
    """Update a specific agent's row in board.md. Returns True if found and updated."""
    path = arch_root / _BOARD_FILE
    if not path.exists():
        return False

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    new_lines = []
    found = False
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for line in lines:
        row = _parse_agent_row(line)
        if row and row.get("agent") == agent_name:
            # Merge updates
            row.update(updates)
            row["ts"] = ts
            new_lines.append(_serialize_agent_row(row))
            found = True
        else:
            new_lines.append(line)

    if found:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return found


def add_agent(arch_root: Path, agent_name: str, fields: dict[str, str]) -> None:
    """Add a new agent row to board.md if it doesn't exist."""
    path = arch_root / _BOARD_FILE
    agents = read_board(arch_root)
    if any(a.get("agent") == agent_name for a in agents):
        update_agent(arch_root, agent_name, fields)
        return

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    defaults = {"b": "-", "group": "-", "status": "idle", "lock": "ready", "deps": "-", "ts": ts}
    defaults.update(fields)
    row_data = {"agent": agent_name, **defaults}
    row = _serialize_agent_row(row_data)

    if path.exists():
        content = path.read_text(encoding="utf-8", errors="replace").rstrip()
        path.write_text(content + "\n" + row + "\n", encoding="utf-8")
    else:
        path.write_text(f"# board — multi-agent dashboard (AI-only)\n\n{row}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="board.md manager")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--agent", help="Agent name to update")
    parser.add_argument("--status", help="New status value")
    parser.add_argument("--lock", help="New lock value")
    parser.add_argument("--block", help="Current block (b: field)")
    parser.add_argument("--group", help="Group")
    parser.add_argument("--last-done", help="Last completed block")
    parser.add_argument("--deps", help="Dependencies")
    parser.add_argument("--read", action="store_true", help="Print all agents")
    args = parser.parse_args()

    root = Path(args.arch_root).resolve()

    if args.read:
        agents = read_board(root)
        for a in agents:
            print("  " + " ".join(f"{k}:{v}" for k, v in a.items()))

    if args.agent:
        updates: dict[str, str] = {}
        if args.status:
            updates["status"] = args.status
        if args.lock:
            updates["lock"] = args.lock
        if args.block:
            updates["b"] = args.block
        if args.group:
            updates["group"] = args.group
        if args.last_done:
            updates["last_done"] = args.last_done
        if args.deps:
            updates["deps"] = args.deps

        ok = update_agent(root, args.agent, updates)
        if ok:
            print(f"board.md: agent:{args.agent} updated — {updates}")
        else:
            print(f"board.md: agent:{args.agent} not found")
