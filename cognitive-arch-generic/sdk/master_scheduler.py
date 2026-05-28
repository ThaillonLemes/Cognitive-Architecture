# cognitive-arch / sdk/master_scheduler.py
# purpose: Time-based trigger engine for Master Agent.
#   Reads tools-registry, classifies stale tools by urgency, returns sorted report.
#   Pure function — no side effects; registry updates are the caller's responsibility.
# stdlib-only; no external dependencies (uses zoneinfo, Python ≥3.9)

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

try:
    from zoneinfo import ZoneInfo
    _SAOPAULO = ZoneInfo("America/Sao_Paulo")
except Exception:                           # pragma: no cover — zoneinfo always present in 3.9+
    _SAOPAULO = timezone.utc  # type: ignore[assignment]

# Urgency levels (ordered by severity)
URGENCY_CRITICAL = "critical"    # > 3× interval AND priority == high
URGENCY_VERY_OVERDUE = "very_overdue"  # > 2× interval
URGENCY_OVERDUE = "overdue"      # > 1× interval

_URGENCY_ORDER = {URGENCY_CRITICAL: 0, URGENCY_VERY_OVERDUE: 1, URGENCY_OVERDUE: 2}

# Large sentinel float for "never run" tools (treated as effectively infinite days elapsed)
_NEVER_RUN_DAYS = 999_999.0


@dataclass
class StaleTool:
    tool_id: str
    tool_name: str
    urgency: str        # "overdue" | "very_overdue" | "critical"
    days_overdue: float # days_since_last_run - recommended_interval_days
    days_since_last_run: float  # raw days since last run (or _NEVER_RUN_DAYS)
    recommended_interval_days: float
    priority: str
    command: str
    message: str        # human-readable summary line


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _days_since(last_run_iso: str, now_dt: datetime) -> float:
    """Compute days between last_run and now_dt. Returns _NEVER_RUN_DAYS for 'never'."""
    if last_run_iso == "never":
        return _NEVER_RUN_DAYS
    try:
        last = datetime.fromisoformat(last_run_iso)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return (now_dt - last).total_seconds() / 86400.0
    except ValueError:
        return _NEVER_RUN_DAYS


def _classify_urgency(
    days_since: float,
    interval: float,
    priority: str,
) -> Optional[str]:
    """
    Return urgency string or None if not stale.

    Rules (evaluated in order — first match wins):
    1. critical   — days_since > 3 × interval AND priority == 'high'
    2. very_overdue — days_since > 2 × interval
    3. overdue    — days_since > 1 × interval
    """
    if days_since > 3 * interval and priority == "high":
        return URGENCY_CRITICAL
    if days_since > 2 * interval:
        return URGENCY_VERY_OVERDUE
    if days_since > interval:
        return URGENCY_OVERDUE
    return None


def _make_message(tool_id: str, urgency: str, days_since: float, interval: float) -> str:
    if days_since >= _NEVER_RUN_DAYS:
        age_str = "never run"
    else:
        age_str = f"{days_since:.1f}d since last run"
    label = urgency.replace("_", " ").upper()
    return f"[{label}] {tool_id}: {age_str} (interval: {interval}d)"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_schedule(
    now_dt: Optional[datetime] = None,
    arch_root: Optional[str] = None,
    registry: Optional[list] = None,   # list[ToolEntry] — use ToolEntry from tools_registry
) -> list[StaleTool]:
    """
    Return a list of StaleTool records for all stale/overdue tools.

    Parameters
    ----------
    now_dt : datetime, optional
        The reference time for comparisons. Defaults to current UTC time.
        If naive, treated as UTC.
    arch_root : str, optional
        Root of the cognitive-arch project. Used to read registry if registry is None.
    registry : list[ToolEntry], optional
        Pre-loaded registry entries. If None, reads from arch_root.

    Returns
    -------
    list[StaleTool]
        Sorted by urgency (critical first), then by days_overdue descending.
        Event-triggered tools are always excluded.
    """
    if registry is None:
        # Import here to avoid circular dependency in tests that inject registry
        from tools_registry import read_registry
        registry = read_registry(arch_root)

    if now_dt is None:
        now_dt = _now_utc()
    elif now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)

    stale: list[StaleTool] = []
    for entry in registry:
        if entry.trigger_type == "event":
            continue

        days = _days_since(entry.last_run, now_dt)
        urgency = _classify_urgency(days, entry.recommended_interval_days, entry.priority)
        if urgency is None:
            continue

        days_ov = days - entry.recommended_interval_days if days < _NEVER_RUN_DAYS else _NEVER_RUN_DAYS

        stale.append(StaleTool(
            tool_id=entry.id,
            tool_name=entry.name,
            urgency=urgency,
            days_overdue=days_ov,
            days_since_last_run=days,
            recommended_interval_days=entry.recommended_interval_days,
            priority=entry.priority,
            command=entry.command,
            message=_make_message(entry.id, urgency, days, entry.recommended_interval_days),
        ))

    stale.sort(key=lambda s: (_URGENCY_ORDER.get(s.urgency, 9), -s.days_since_last_run))
    return stale


def now_local() -> datetime:
    """Current time in America/Sao_Paulo (for display purposes)."""
    return datetime.now(_SAOPAULO)


def format_report(stale: list[StaleTool]) -> str:
    """Render stale tools as a markdown summary for Master Agent output."""
    if not stale:
        return "✅ All tools are current. No stale items."

    lines = ["## Master Agent — Stale Tools Report", ""]
    for s in stale:
        emoji = {"critical": "🔴", "very_overdue": "🟠", "overdue": "🟡"}.get(s.urgency, "⚪")
        lines.append(f"{emoji} **{s.tool_id}** — {s.message}")
        lines.append(f"   Command: `{s.command}`")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Master scheduler — check tool freshness")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--report", action="store_true", help="Print markdown report")
    parser.add_argument("--overdue-only", action="store_true", help="Show only overdue/very_overdue/critical")
    args = parser.parse_args()

    stale = check_schedule(arch_root=args.arch_root)
    if args.report:
        print(format_report(stale))
    else:
        if not stale:
            print("All tools current.")
        else:
            for s in stale:
                print(s.message)
    sys.exit(0 if not stale else 1)
