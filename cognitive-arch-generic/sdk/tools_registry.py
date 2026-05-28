# cognitive-arch / sdk/tools_registry.py
# purpose: Read/update the tools registry; identify stale/overdue tools for Master Agent.
# stdlib-only; no external dependencies

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REGISTRY_PATH = "governance/tools-registry.yaml"


@dataclass
class ToolEntry:
    id: str
    name: str
    command: str
    description: str
    recommended_interval_days: float
    trigger_type: str   # "time" | "event"
    priority: str       # "high" | "medium" | "low"
    last_run: str       # ISO-8601 timestamp or "never"
    mutable_by: str = "master"

    @property
    def days_since_last_run(self) -> Optional[float]:
        """Days elapsed since last_run. Returns None if never run or event-triggered."""
        if self.last_run == "never" or self.trigger_type == "event":
            return None
        try:
            last = datetime.fromisoformat(self.last_run)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return (now - last).total_seconds() / 86400.0
        except ValueError:
            return None

    @property
    def is_stale(self) -> bool:
        """True if days_since_last_run > recommended_interval_days."""
        if self.trigger_type == "event":
            return False
        days = self.days_since_last_run
        if days is None:
            return True  # never run = stale
        return days > self.recommended_interval_days

    @property
    def is_overdue(self) -> bool:
        """True if days_since_last_run > 2 × recommended_interval_days (Master proactive threshold)."""
        if self.trigger_type == "event":
            return False
        days = self.days_since_last_run
        if days is None:
            return True  # never run = overdue
        return days > 2 * self.recommended_interval_days


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _arch_root_path(arch_root: Optional[str]) -> Path:
    return Path(arch_root) if arch_root is not None else Path.cwd()


def _parse_yaml_tools(content: str) -> list[dict]:
    """
    Minimal YAML parser for the tools-registry list format.
    Parses list items under the 'tools:' key without external dependencies.
    """
    tools_match = re.search(r"^tools:\s*\n(.*)", content, re.DOTALL | re.MULTILINE)
    if not tools_match:
        return []

    tools_section = tools_match.group(1)
    # Split on list item markers
    raw_items = re.split(r"(?m)^  - id:", tools_section)

    tools = []
    for item in raw_items:
        if not item.strip():
            continue
        lines = item.splitlines()
        tool: dict = {}

        # First line is the id value
        tool["id"] = lines[0].strip().strip('"').strip("'")

        for line in lines[1:]:
            m = re.match(r"^\s+([\w_-]+):\s*(.*)", line)
            if not m:
                continue
            key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            # Coerce numeric values
            try:
                val = float(val) if "." in val else int(val)
            except ValueError:
                pass
            tool[key] = val

        if "id" in tool:
            tools.append(tool)

    return tools


def _str(d: dict, key: str, default: str = "") -> str:
    return str(d.get(key, default))


def _float(d: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(d.get(key, default))
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def read_registry(arch_root: Optional[str] = None) -> list[ToolEntry]:
    """Read governance/tools-registry.yaml and return a list of ToolEntry objects."""
    root = _arch_root_path(arch_root)
    content = (root / REGISTRY_PATH).read_text(encoding="utf-8")
    raw = _parse_yaml_tools(content)
    return [
        ToolEntry(
            id=_str(d, "id"),
            name=_str(d, "name"),
            command=_str(d, "command"),
            description=_str(d, "description"),
            recommended_interval_days=_float(d, "recommended_interval_days", 1.0),
            trigger_type=_str(d, "trigger_type", "time"),
            priority=_str(d, "priority", "medium"),
            last_run=_str(d, "last_run", "never"),
            mutable_by=_str(d, "mutable_by", "master"),
        )
        for d in raw
    ]


def update_last_run(
    tool_id: str,
    now_ts: Optional[str] = None,
    arch_root: Optional[str] = None,
) -> None:
    """
    Update the last_run field for the given tool_id in the registry file.
    Only modifies the last_run line within the matching tool block.
    Raises ValueError if tool_id not found.
    """
    root = _arch_root_path(arch_root)
    path = root / REGISTRY_PATH
    if now_ts is None:
        now_ts = datetime.now(timezone.utc).isoformat()

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    in_target = False
    updated = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("- id:"):
            current_id = stripped[len("- id:"):].strip().strip('"').strip("'")
            in_target = current_id == tool_id
            continue
        if in_target and stripped.startswith("last_run:"):
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + f'last_run: "{now_ts}"\n'
            updated = True
            in_target = False

    if not updated:
        raise ValueError(
            f"tool_id '{tool_id}' not found in registry or last_run field missing"
        )

    path.write_text("".join(lines), encoding="utf-8")


def get_stale_tools(
    now_ts: Optional[str] = None,
    threshold_multiplier: float = 1.0,
    arch_root: Optional[str] = None,
) -> list[ToolEntry]:
    """
    Return tools where days_since_last_run > recommended_interval_days * threshold_multiplier.
    Event-triggered tools are always excluded.

    threshold_multiplier=1.0  → stale (past recommended interval)
    threshold_multiplier=2.0  → overdue (Master proactive alert threshold)
    """
    entries = read_registry(arch_root)
    now_dt: Optional[datetime] = None
    if now_ts:
        now_dt = datetime.fromisoformat(now_ts)
        if now_dt.tzinfo is None:
            now_dt = now_dt.replace(tzinfo=timezone.utc)

    stale = []
    for entry in entries:
        if entry.trigger_type == "event":
            continue
        if entry.last_run == "never":
            stale.append(entry)
            continue

        if now_dt is not None:
            try:
                last = datetime.fromisoformat(entry.last_run)
                if last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)
                days = (now_dt - last).total_seconds() / 86400.0
            except ValueError:
                stale.append(entry)
                continue
        else:
            days = entry.days_since_last_run
            if days is None:
                stale.append(entry)
                continue

        if days > entry.recommended_interval_days * threshold_multiplier:
            stale.append(entry)

    return stale


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Tools registry CLI")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--list", action="store_true", help="List all tools with freshness")
    parser.add_argument("--stale", action="store_true", help="List stale tools (>interval)")
    parser.add_argument("--overdue", action="store_true", help="List overdue tools (>2×interval)")
    parser.add_argument("--update", metavar="TOOL_ID", help="Mark tool as run now")
    args = parser.parse_args()

    if args.list:
        for e in read_registry(args.arch_root):
            days = e.days_since_last_run
            age = f"{days:.1f}d" if days is not None else "never"
            flag = "OVERDUE" if e.is_overdue else ("STALE" if e.is_stale else "ok")
            print(
                f"{e.id:<25} interval:{e.recommended_interval_days:>2}d  "
                f"last:{e.last_run[:10]}  age:{age:<8}  {flag}"
            )
    elif args.stale:
        for e in get_stale_tools(threshold_multiplier=1.0, arch_root=args.arch_root):
            print(f"STALE  {e.id}  last_run:{e.last_run}  interval:{e.recommended_interval_days}d")
    elif args.overdue:
        for e in get_stale_tools(threshold_multiplier=2.0, arch_root=args.arch_root):
            print(f"OVERDUE  {e.id}  last_run:{e.last_run}  interval:{e.recommended_interval_days}d")
    elif args.update:
        update_last_run(args.update, arch_root=args.arch_root)
        print(f"Updated last_run for '{args.update}'")
    else:
        parser.print_help()
        sys.exit(1)
