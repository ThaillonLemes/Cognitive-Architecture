# cognitive-arch / sdk/master_suggest.py
# purpose: Master Agent active suggestion logic.
#   Wraps master_scheduler.check_schedule() and produces user-facing Suggestion objects
#   for three trigger types: session-start, inline (block-start), and on-demand.
# stdlib-only; no external dependencies

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from master_scheduler import (
    StaleTool,
    check_schedule,
    URGENCY_CRITICAL,
    URGENCY_VERY_OVERDUE,
    URGENCY_OVERDUE,
    _NEVER_RUN_DAYS,
)

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 emoji-safe (port 2026-06-09)

_EMOJI = {
    URGENCY_CRITICAL: "🔴",
    URGENCY_VERY_OVERDUE: "🟠",
    URGENCY_OVERDUE: "🟡",
}

_INLINE_MAX = 2  # max suggestions shown inline at block-start


# ---------------------------------------------------------------------------
# Suggestion dataclass
# ---------------------------------------------------------------------------

@dataclass
class Suggestion:
    tool_id: str
    tool_name: str
    urgency: str            # "overdue" | "very_overdue" | "critical"
    message: str            # full rendered suggestion text (multi-line)
    action_button_label: str  # e.g., "Run audit now"
    command: str
    source: str             # "session_start" | "inline" | "on_demand"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _render_message(stale: StaleTool, source: str) -> str:
    emoji = _EMOJI.get(stale.urgency, "⚪")
    label = stale.urgency.replace("_", " ").upper()
    if stale.days_since_last_run >= _NEVER_RUN_DAYS:
        age_str = "never run"
    else:
        age_str = f"{stale.days_since_last_run:.1f}d since last run"
    return (
        f"{emoji} **{label}** — {stale.tool_name}: {age_str} "
        f"(interval: {stale.recommended_interval_days}d)\n"
        f"   Run: `{stale.command}`"
    )


def _action_label(tool_id: str) -> str:
    """Human-readable button label for the tool."""
    labels = {
        "audit": "Run audit now",
        "health-report": "Generate health report",
        "pattern-mining": "Run pattern mining",
        "weekly-report": "Generate weekly report",
        "phase-forecast": "Run phase forecast",
        "conflicts-check": "Run conflicts check",
        "security-revalidation": "Run security revalidation",
        "integrity-check": "Run integrity check",
    }
    return labels.get(tool_id, f"Run {tool_id}")


def _to_suggestion(stale: StaleTool, source: str) -> Suggestion:
    return Suggestion(
        tool_id=stale.tool_id,
        tool_name=stale.tool_name,
        urgency=stale.urgency,
        message=_render_message(stale, source),
        action_button_label=_action_label(stale.tool_id),
        command=stale.command,
        source=source,
    )


def _fetch_stale(
    now_dt: Optional[datetime],
    registry: Optional[list],
    arch_root: Optional[str],
) -> list[StaleTool]:
    return check_schedule(now_dt=now_dt, arch_root=arch_root, registry=registry)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def suggest_at_session_start(
    now_dt: Optional[datetime] = None,
    registry: Optional[list] = None,
    arch_root: Optional[str] = None,
) -> list[Suggestion]:
    """
    Return all stale tools (urgency >= overdue) for session-start briefing.
    Results are sorted by urgency (critical first).
    No cap on number of suggestions.
    """
    stale = _fetch_stale(now_dt, registry, arch_root)
    return [_to_suggestion(s, "session_start") for s in stale]


def suggest_inline(
    block_id: Optional[str] = None,
    now_dt: Optional[datetime] = None,
    registry: Optional[list] = None,
    arch_root: Optional[str] = None,
) -> list[Suggestion]:
    """
    Return at most 2 suggestions for inline display at block-start.
    Only critical urgency tools are surfaced inline (to avoid disrupting block flow).
    block_id is accepted for future relevance filtering (currently unused in v1).
    """
    stale = _fetch_stale(now_dt, registry, arch_root)
    critical = [s for s in stale if s.urgency == URGENCY_CRITICAL]
    top = critical[:_INLINE_MAX]
    return [_to_suggestion(s, "inline") for s in top]


def suggest_on_demand(
    now_dt: Optional[datetime] = None,
    registry: Optional[list] = None,
    arch_root: Optional[str] = None,
) -> list[Suggestion]:
    """
    Return all stale tools on explicit user request.
    Same scope as session_start — all urgency levels.
    """
    stale = _fetch_stale(now_dt, registry, arch_root)
    return [_to_suggestion(s, "on_demand") for s in stale]


def render_suggestions(suggestions: list[Suggestion], header: Optional[str] = None) -> str:
    """Render a list of Suggestion objects as a markdown block for conversation output."""
    if not suggestions:
        return "✅ All tools are current. No suggestions."
    lines = []
    if header:
        lines.append(header)
        lines.append("")
    for s in suggestions:
        lines.append(s.message)
    return "\n".join(lines)


def session_start_block(
    now_dt: Optional[datetime] = None,
    registry: Optional[list] = None,
    arch_root: Optional[str] = None,
) -> str:
    """Convenience: full session-start briefing text."""
    suggestions = suggest_at_session_start(now_dt=now_dt, registry=registry, arch_root=arch_root)
    if not suggestions:
        return ""
    return render_suggestions(
        suggestions,
        header="## Master Agent — Session Briefing",
    )


def inline_block(
    block_id: Optional[str] = None,
    now_dt: Optional[datetime] = None,
    registry: Optional[list] = None,
    arch_root: Optional[str] = None,
) -> str:
    """Convenience: inline block-start suggestion text."""
    suggestions = suggest_inline(block_id=block_id, now_dt=now_dt, registry=registry, arch_root=arch_root)
    if not suggestions:
        return ""
    header = f"⚠️ Before starting{' ' + block_id if block_id else ''} — critical tool overdue:"
    return render_suggestions(suggestions, header=header)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).parent))
    from safe_io import force_utf8
    force_utf8()

    parser = argparse.ArgumentParser(description="Master active suggestion CLI")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--session", action="store_true", help="Session-start suggestions")
    parser.add_argument("--inline", metavar="BLOCK_ID", help="Inline suggestions for block")
    parser.add_argument("--demand", action="store_true", help="On-demand suggestions")
    args = parser.parse_args()

    if args.session:
        print(session_start_block(arch_root=args.arch_root) or "✅ All tools current.")
    elif args.inline:
        print(inline_block(block_id=args.inline, arch_root=args.arch_root) or "✅ No critical items.")
    elif args.demand:
        suggs = suggest_on_demand(arch_root=args.arch_root)
        print(render_suggestions(suggs, header="## Master Agent — On-demand Status"))
    else:
        parser.print_help()
        sys.exit(1)
