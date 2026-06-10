# cognitive-arch / sdk/briefing_generator.py
# purpose: Post-pause briefing generator.
#   Produces a concise summary (markdown + HTML) when session resumes after ≥24h.
#   Consumes BLOCK_LOG, STATE.md, NEXT.md, and master_scheduler stale list.
# stdlib-only; no external dependencies

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 emoji-safe (port 2026-06-09)

DEFAULT_PAUSE_THRESHOLD_HOURS = 24
MAX_BRIEFING_LINES = 15  # hard cap on markdown output lines

_BLOCK_LOG_PATH = "blocks/BLOCK_LOG.md"
_STATE_PATH = "STATE.md"
_NEXT_PATH = "NEXT.md"


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class PostPauseBriefing:
    pause_hours: float
    last_active_ts: str
    generated_at: str
    current_phase: str
    next_action: str
    last_block: str
    blocks_closed_since: list[str] = field(default_factory=list)
    stale_tools_count: int = 0
    critical_tools: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal parsers
# ---------------------------------------------------------------------------

def _arch_path(arch_root: Optional[str]) -> Path:
    return Path(arch_root) if arch_root is not None else Path.cwd()


def _now_utc(now_ts: Optional[str] = None) -> datetime:
    if now_ts is None:
        return datetime.now(timezone.utc)
    dt = datetime.fromisoformat(now_ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_kv(content: str) -> dict:
    """
    Parse AI-only key:value dense format (STATE.md / NEXT.md style).
    Splits each line into tokens; splits each token on first ':'.
    """
    result: dict = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for token in line.split():
            if ":" in token:
                key, _, val = token.partition(":")
                if key and val:
                    result[key] = val
    return result


def _parse_block_log_since(log_content: str, since_date: str) -> list[str]:
    """
    Parse BLOCK_LOG and return block IDs with date >= since_date (YYYY-MM-DD string compare).
    Format: block-NNN done - YYYY-MM-DD
    """
    blocks = []
    for line in log_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[1] == "done":
            block_id = parts[0]
            date_str = parts[3]
            if date_str >= since_date:
                blocks.append(block_id)
    return blocks


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def should_brief(
    last_active_ts: str,
    threshold_hours: float = DEFAULT_PAUSE_THRESHOLD_HOURS,
    now_dt: Optional[datetime] = None,
) -> bool:
    """Return True if the pause since last_active_ts exceeds threshold_hours."""
    if now_dt is None:
        now_dt = datetime.now(timezone.utc)
    try:
        last = datetime.fromisoformat(last_active_ts)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        pause_hours = (now_dt - last).total_seconds() / 3600.0
        return pause_hours > threshold_hours
    except ValueError:
        return False


def generate_briefing(
    last_active_ts: str,
    arch_root: Optional[str] = None,
    now_ts: Optional[str] = None,
    threshold_hours: float = DEFAULT_PAUSE_THRESHOLD_HOURS,
    # Injectable for testing
    state_content: Optional[str] = None,
    next_content: Optional[str] = None,
    log_content: Optional[str] = None,
    stale_tools: Optional[list] = None,  # list[StaleTool] from master_scheduler
) -> Optional[PostPauseBriefing]:
    """
    Generate a PostPauseBriefing if pause since last_active_ts exceeds threshold.
    Returns None if pause is below threshold.

    Parameters injectable for testing: state_content, next_content, log_content, stale_tools.
    """
    now_dt = _now_utc(now_ts)
    if not should_brief(last_active_ts, threshold_hours=threshold_hours, now_dt=now_dt):
        return None

    last = datetime.fromisoformat(last_active_ts)
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    pause_hours = (now_dt - last).total_seconds() / 3600.0
    since_date = last.strftime("%Y-%m-%d")

    root = _arch_path(arch_root)

    if state_content is None:
        state_content = _read_file(root / _STATE_PATH)
    if next_content is None:
        next_content = _read_file(root / _NEXT_PATH)
    if log_content is None:
        log_content = _read_file(root / _BLOCK_LOG_PATH)

    state = _parse_kv(state_content)
    nxt = _parse_kv(next_content)

    blocks_since = _parse_block_log_since(log_content, since_date)

    if stale_tools is None:
        try:
            from master_scheduler import check_schedule
            stale_tools = check_schedule(now_dt=now_dt, arch_root=arch_root)
        except Exception:
            stale_tools = []

    from master_scheduler import URGENCY_CRITICAL
    critical_ids = [s.tool_id for s in stale_tools if s.urgency == URGENCY_CRITICAL]

    return PostPauseBriefing(
        pause_hours=round(pause_hours, 1),
        last_active_ts=last_active_ts,
        generated_at=now_dt.isoformat(),
        current_phase=state.get("phase", "unknown"),
        next_action=nxt.get("next_action", state.get("next", "unknown")),
        last_block=state.get("last_block", "unknown"),
        blocks_closed_since=blocks_since,
        stale_tools_count=len(stale_tools),
        critical_tools=critical_ids,
    )


def render_markdown(briefing: PostPauseBriefing) -> str:
    """Render briefing as markdown, hard-capped at MAX_BRIEFING_LINES."""
    lines: list[str] = []

    # Header
    hours = briefing.pause_hours
    if hours >= 168:
        pause_str = f"{hours / 168:.1f} weeks"
    elif hours >= 24:
        pause_str = f"{hours / 24:.1f} days"
    else:
        pause_str = f"{hours:.1f}h"

    lines.append(f"## 📋 Briefing — Resuming after {pause_str}")
    lines.append("")

    # Blocks closed
    if briefing.blocks_closed_since:
        count = len(briefing.blocks_closed_since)
        recent = briefing.blocks_closed_since[-3:]  # last 3
        lines.append(f"**Blocks closed since your last session:** {count}")
        lines.append(f"  Recent: {', '.join(recent)}")
    else:
        lines.append("**No blocks closed during your absence.**")
    lines.append("")

    # Current state
    lines.append(f"**Phase:** {briefing.current_phase}  **Last block:** {briefing.last_block}")
    lines.append(f"**Next action:** `{briefing.next_action}`")
    lines.append("")

    # Stale tools
    if briefing.stale_tools_count > 0:
        lines.append(f"**Stale tools:** {briefing.stale_tools_count}")
        if briefing.critical_tools:
            lines.append(f"  🔴 Critical: {', '.join(briefing.critical_tools)}")
    else:
        lines.append("**All tools current.**")

    # Enforce hard cap
    if len(lines) > MAX_BRIEFING_LINES:
        lines = lines[:MAX_BRIEFING_LINES - 1]
        lines.append("_... see governance/dashboard.html for full details._")

    return "\n".join(lines)


def render_html(briefing: PostPauseBriefing) -> str:
    """Render briefing as a minimal standalone HTML snippet (no CDN)."""
    md = render_markdown(briefing)
    # Convert markdown to very basic HTML (bold, code, headers)
    import re
    html = md
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
    html = re.sub(r"_(.+?)_", r"<em>\1</em>", html)
    # Wrap lines in <p>
    paras = []
    for line in html.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("<h2>"):
            paras.append(line)
        else:
            paras.append(f"<p>{line}</p>")
    body = "\n".join(paras)
    return (
        "<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'>"
        "<title>Post-pause Briefing</title>"
        "<style>body{font-family:sans-serif;max-width:720px;margin:2rem auto;"
        "padding:1rem;background:#1a1a2e;color:#e0e0e0}"
        "h2{color:#a8d8ea}code{background:#2a2a4a;padding:.2em .4em;border-radius:3px}"
        "strong{color:#f9ca24}</style></head>\n<body>\n"
        + body
        + "\n</body></html>"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Post-pause briefing generator")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--last-active", required=True, help="ISO-8601 timestamp of last session")
    parser.add_argument("--threshold", type=float, default=DEFAULT_PAUSE_THRESHOLD_HOURS,
                        help="Pause threshold in hours (default: 24)")
    parser.add_argument("--html", action="store_true", help="Output HTML instead of markdown")
    args = parser.parse_args()

    briefing = generate_briefing(
        last_active_ts=args.last_active,
        arch_root=args.arch_root,
        threshold_hours=args.threshold,
    )
    if briefing is None:
        print("No briefing needed (pause below threshold).")
        sys.exit(0)

    if args.html:
        print(render_html(briefing))
    else:
        print(render_markdown(briefing))
