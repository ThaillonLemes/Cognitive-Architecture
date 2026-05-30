# cognitive-arch / sdk/weekly_report.py
# purpose: Weekly HTML report generator (relative 7-day rolling per Q11).
#   Output: governance/reports/weekly-YYYY-MM-DD.html (standalone, no CDN).
#   Sections: blocks closed, velocity, gates pass rate, new patterns, forecast.
# stdlib-only; no external dependencies

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

REPORTS_DIR = "governance/reports"
BLOCK_LOG_PATH = "blocks/BLOCK_LOG.md"
STATE_PATH = "STATE.md"
NEXT_PATH = "NEXT.md"
PATTERNS_PATH = "governance/patterns.md"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class WeeklyReport:
    period_start: str           # YYYY-MM-DD
    period_end: str             # YYYY-MM-DD
    generated_at: str
    current_phase: str
    next_action: str
    blocks_closed: list[str] = field(default_factory=list)
    velocity_blocks_per_day: Optional[float] = None
    gates_pass_rate: Optional[float] = None   # fraction 0.0–1.0; None if no data
    new_pattern_names: list[str] = field(default_factory=list)
    stale_tool_count: int = 0
    critical_tool_ids: list[str] = field(default_factory=list)
    forecast_blocks_next_7d: Optional[int] = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _arch_path(arch_root: Optional[str]) -> Path:
    return Path(arch_root) if arch_root is not None else Path.cwd()


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_kv(content: str) -> dict:
    """Parse key:value dense format (STATE.md / NEXT.md)."""
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


def _blocks_in_period(log_content: str, start_date: str, end_date: str) -> list[str]:
    """
    Extract block IDs from BLOCK_LOG where date is in [start_date, end_date].
    Date format: YYYY-MM-DD (lexicographic comparison valid).
    """
    blocks = []
    for line in log_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[1] == "done":
            date_str = parts[3]
            if start_date <= date_str <= end_date:
                blocks.append(parts[0])
    return blocks


def _extract_pattern_names(patterns_content: str) -> list[str]:
    """
    Extract pattern names from governance/patterns.md.
    Looks for markdown headers (## or ###) that look like pattern names.
    """
    names = []
    for line in patterns_content.splitlines():
        m = re.match(r"^#{2,3}\s+(.+)", line.strip())
        if m:
            name = m.group(1).strip()
            # Exclude known non-pattern headers
            if name.lower() not in {"patterns report", "summary table", "top patterns"}:
                names.append(name)
    return names


def _velocity(block_count: int, days: int) -> Optional[float]:
    if days <= 0:
        return None
    return round(block_count / days, 2)


def _forecast(velocity: Optional[float], days_next: int = 7) -> Optional[int]:
    if velocity is None:
        return None
    return max(0, round(velocity * days_next))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_weekly_report(
    arch_root: Optional[str] = None,
    now_ts: Optional[str] = None,
    days: int = 7,
    # Injectable for testing
    log_content: Optional[str] = None,
    state_content: Optional[str] = None,
    next_content: Optional[str] = None,
    patterns_content: Optional[str] = None,
    stale_tools: Optional[list] = None,
) -> WeeklyReport:
    """
    Generate a WeeklyReport for the last `days` days.
    All content parameters injectable for testing.
    """
    now_dt: datetime
    if now_ts:
        now_dt = datetime.fromisoformat(now_ts)
        if now_dt.tzinfo is None:
            now_dt = now_dt.replace(tzinfo=timezone.utc)
    else:
        now_dt = datetime.now(timezone.utc)

    start_dt = now_dt - timedelta(days=days)
    period_start = start_dt.strftime("%Y-%m-%d")
    period_end = now_dt.strftime("%Y-%m-%d")

    root = _arch_path(arch_root)

    if log_content is None:
        log_content = _read_file(root / BLOCK_LOG_PATH)
    if state_content is None:
        state_content = _read_file(root / STATE_PATH)
    if next_content is None:
        next_content = _read_file(root / NEXT_PATH)
    if patterns_content is None:
        patterns_content = _read_file(root / PATTERNS_PATH)

    if stale_tools is None:
        try:
            from master_scheduler import check_schedule
            stale_tools = check_schedule(now_dt=now_dt, arch_root=arch_root)
        except Exception:
            stale_tools = []

    state = _parse_kv(state_content)
    nxt = _parse_kv(next_content)

    blocks_closed = _blocks_in_period(log_content, period_start, period_end)
    velocity = _velocity(len(blocks_closed), days)
    forecast = _forecast(velocity)
    pattern_names = _extract_pattern_names(patterns_content)

    from master_scheduler import URGENCY_CRITICAL
    critical_ids = [s.tool_id for s in stale_tools if s.urgency == URGENCY_CRITICAL]

    return WeeklyReport(
        period_start=period_start,
        period_end=period_end,
        generated_at=now_dt.isoformat(),
        current_phase=state.get("phase", "unknown"),
        next_action=nxt.get("next_action", state.get("next", "unknown")),
        blocks_closed=blocks_closed,
        velocity_blocks_per_day=velocity,
        gates_pass_rate=None,  # would require parsing retros — deferred to dashboard
        new_pattern_names=pattern_names,
        stale_tool_count=len(stale_tools),
        critical_tool_ids=critical_ids,
        forecast_blocks_next_7d=forecast,
    )


def render_html(report: WeeklyReport) -> str:
    """Render WeeklyReport as standalone HTML (no CDN, dark theme)."""

    def _row(label: str, value: str) -> str:
        return f"<tr><td>{label}</td><td><strong>{value}</strong></td></tr>"

    block_list = "".join(f"<li>{b}</li>" for b in report.blocks_closed) or "<li><em>none</em></li>"
    pattern_list = "".join(f"<li>{p}</li>" for p in report.new_pattern_names) or "<li><em>none</em></li>"

    vel_str = f"{report.velocity_blocks_per_day:.2f} blocks/day" if report.velocity_blocks_per_day is not None else "n/a"
    gpr_str = f"{report.gates_pass_rate * 100:.0f}%" if report.gates_pass_rate is not None else "n/a"
    fcast_str = f"~{report.forecast_blocks_next_7d}" if report.forecast_blocks_next_7d is not None else "n/a"

    stale_str = str(report.stale_tool_count)
    if report.critical_tool_ids:
        stale_str += f" (🔴 critical: {', '.join(report.critical_tool_ids)})"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Weekly Report — {report.period_start} to {report.period_end}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #c8d6e5;
            padding: 2rem; line-height: 1.6; }}
    h1 {{ color: #a8d8ea; margin-bottom: .5rem; font-size: 1.6rem; }}
    h2 {{ color: #f9ca24; margin: 1.5rem 0 .5rem; font-size: 1.1rem; text-transform: uppercase;
          letter-spacing: .05em; }}
    .meta {{ color: #7f8c8d; font-size: .85rem; margin-bottom: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 640px; margin-bottom: 1rem; }}
    td {{ padding: .4rem .8rem; border-bottom: 1px solid #1e1e3a; }}
    td:first-child {{ color: #95a5a6; width: 200px; }}
    strong {{ color: #e0e0e0; }}
    ul {{ padding-left: 1.2rem; color: #c8d6e5; }}
    li {{ margin: .2rem 0; font-size: .9rem; }}
    .section {{ background: #1a1a2e; border-radius: 6px; padding: 1rem 1.2rem;
                margin-bottom: 1rem; border-left: 3px solid #6c5ce7; }}
    code {{ background: #2a2a4a; padding: .2em .4em; border-radius: 3px;
            font-size: .85em; color: #a29bfe; }}
    .generated {{ color: #636e72; font-size: .75rem; margin-top: 2rem; }}
  </style>
</head>
<body>
  <h1>📊 Weekly Report</h1>
  <p class="meta">{report.period_start} → {report.period_end} &nbsp;·&nbsp;
     Phase {report.current_phase}</p>

  <div class="section">
    <h2>Summary</h2>
    <table>
      {_row("Blocks closed", str(len(report.blocks_closed)))}
      {_row("Velocity", vel_str)}
      {_row("Gates pass rate", gpr_str)}
      {_row("Stale tools", stale_str)}
      {_row("Forecast (next 7d)", fcast_str)}
    </table>
  </div>

  <div class="section">
    <h2>Blocks Closed</h2>
    <ul>{block_list}</ul>
  </div>

  <div class="section">
    <h2>Patterns Detected</h2>
    <ul>{pattern_list}</ul>
  </div>

  <div class="section">
    <h2>Next Action</h2>
    <p><code>{report.next_action}</code></p>
  </div>

  <p class="generated">Generated at {report.generated_at}</p>
</body>
</html>"""
    return html


def write_report(
    report: WeeklyReport,
    arch_root: Optional[str] = None,
) -> Path:
    """Write report HTML to governance/reports/weekly-YYYY-MM-DD.html. Returns output path."""
    root = _arch_path(arch_root)
    out_dir = root / REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"weekly-{report.period_end}.html"
    out_path.write_text(render_html(report), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, sys
    sys.path.insert(0, str(Path(__file__).parent))
    from safe_io import force_utf8
    force_utf8()

    parser = argparse.ArgumentParser(description="Weekly report generator")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--days", type=int, default=7, help="Rolling window in days (default: 7)")
    parser.add_argument("--stdout", action="store_true", help="Print HTML to stdout instead of writing file")
    args = parser.parse_args()

    report = generate_weekly_report(arch_root=args.arch_root, days=args.days)
    if args.stdout:
        print(render_html(report))
    else:
        path = write_report(report, arch_root=args.arch_root)
        print(f"Weekly report written: {path}")
