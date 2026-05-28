# cognitive-arch / sdk/dashboard_generator.py
# purpose: Live dashboard HTML generator.
#   Output: governance/dashboard.html (standalone, no CDN, dark theme).
#   Sections: active-agents | next-actions | health-metrics | recent-patterns
#             + timeline (last 7d) + roadmap (phases) + quick commands footer.
# stdlib-only; no external dependencies

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

DASHBOARD_PATH = "governance/dashboard.html"
BLOCK_LOG_PATH = "blocks/BLOCK_LOG.md"
STATE_PATH = "STATE.md"
NEXT_PATH = "NEXT.md"
BOARD_PATH = "board.md"
PATTERNS_PATH = "governance/patterns.md"
STYLES_PATH = "templates/_styles.css"

_TIMELINE_DAYS = 7
_MAX_PATTERNS = 5
_ROADMAP_MAX_PHASE = 17

# ---------------------------------------------------------------------------
# Fallback CSS (mirrors _styles.css; used when the file is not found)
# ---------------------------------------------------------------------------

_FALLBACK_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f0f1a;
       color: #c8d6e5; padding: 2rem; line-height: 1.6; font-size: 14px; }
h1 { color: #a8d8ea; font-size: 1.6rem; margin-bottom: .3rem; }
h2 { color: #f9ca24; font-size: 1rem; text-transform: uppercase;
     letter-spacing: .06em; margin-bottom: .6rem; }
h3 { color: #e0e0e0; font-size: .9rem; font-weight: 600; margin-bottom: .3rem; }
p  { margin-bottom: .5rem; }
:root {
  --bg-card:    #1a1a2e; --bg-accent:  #2a2a4a; --border:     #1e1e3a;
  --purple:     #6c5ce7; --gold:       #f9ca24; --teal:       #a8d8ea;
  --green:      #00b894; --red:        #d63031; --orange:     #e17055;
  --grey:       #636e72; --text:       #c8d6e5; --text-dim:   #7f8c8d;
  --code-bg:    #2a2a4a; --code-color: #a29bfe;
}
.card { background: var(--bg-card); border-radius: 8px; padding: 1rem 1.2rem;
        border-left: 3px solid var(--purple); margin-bottom: 1rem; }
.card-teal  { border-left-color: var(--teal); }
.card-gold  { border-left-color: var(--gold); }
.card-green { border-left-color: var(--green); }
.card-red   { border-left-color: var(--red); }
.badge { display: inline-block; padding: .15em .5em; border-radius: 3px;
         font-size: .75rem; font-weight: 600; text-transform: uppercase; }
.badge-done     { background: var(--green); color: #fff; }
.badge-active   { background: var(--purple); color: #fff; }
.badge-planned  { background: var(--bg-accent); color: var(--text-dim); }
.badge-critical { background: var(--red); color: #fff; }
.badge-warning  { background: var(--orange); color: #fff; }
table { border-collapse: collapse; width: 100%; margin-bottom: .8rem; }
td, th { padding: .35rem .6rem; border-bottom: 1px solid var(--border); }
th { color: var(--text-dim); font-weight: 600; text-align: left; font-size: .8rem; }
td:first-child { color: var(--text-dim); }
strong { color: #e0e0e0; }
ul { padding-left: 1.2rem; }
li { margin: .2rem 0; font-size: .9rem; }
code { background: var(--code-bg); color: var(--code-color); padding: .2em .4em;
       border-radius: 3px; font-size: .85em;
       font-family: 'Consolas', 'Courier New', monospace; }
.meta { color: var(--text-dim); font-size: .8rem; margin-bottom: 1rem; }
.generated { color: var(--grey); font-size: .7rem; margin-top: 2rem; text-align: right; }
.phase-row { display: flex; flex-wrap: wrap; gap: .4rem; margin: .5rem 0; }
.phase-pill { padding: .2em .6em; border-radius: 12px; font-size: .75rem; font-weight: 600; }
.phase-pill.done    { background: var(--green); color: #fff; }
.phase-pill.active  { background: var(--purple); color: #fff; }
.phase-pill.planned { background: var(--bg-accent); color: var(--text-dim);
                      border: 1px solid var(--border); }
.dash-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
             gap: 1rem; margin-bottom: 1.5rem; }
.timeline { list-style: none; padding: 0; }
.timeline li { display: flex; gap: .6rem; margin-bottom: .4rem; font-size: .85rem; }
.timeline .dot { width: 8px; height: 8px; border-radius: 50%;
                 background: var(--purple); margin-top: .4rem; flex-shrink: 0; }
.timeline .dot.done { background: var(--green); }
"""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AgentRow:
    agent_id: str
    block: str      # current block or "-"
    status: str     # idle | wip | wait | done
    group: str
    last_done: str  # last_done field or "-"


@dataclass
class DashboardData:
    generated_at: str
    current_phase: str
    next_action: str
    manifest: str      # manifest path from NEXT.md
    last_block: str

    # Column 1: Active Agents (parsed from board.md)
    agents: list[AgentRow] = field(default_factory=list)

    # Column 3: Health Metrics
    blocks_closed_7d: list[str] = field(default_factory=list)
    velocity_blocks_per_day: Optional[float] = None
    stale_tool_count: int = 0
    critical_tool_ids: list[str] = field(default_factory=list)
    forecast_blocks_next_7d: Optional[int] = None

    # Column 4: Recent Patterns
    recent_patterns: list[str] = field(default_factory=list)

    # Timeline: list of (date_str, block_id) tuples, newest first
    timeline_entries: list = field(default_factory=list)

    # Roadmap
    phases_done: list[str] = field(default_factory=list)
    phases_active: list[str] = field(default_factory=list)
    phases_planned: list[str] = field(default_factory=list)


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


def _parse_board(board_content: str) -> list[AgentRow]:
    """Parse board.md agent rows into AgentRow list."""
    rows = []
    for line in board_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith("agent:"):
            continue
        kv: dict = {}
        for token in line.split():
            if ":" in token:
                k, _, v = token.partition(":")
                kv[k] = v
        if "agent" not in kv:
            continue
        rows.append(AgentRow(
            agent_id=kv.get("agent", "-"),
            block=kv.get("b", "-"),
            status=kv.get("status", "-"),
            group=kv.get("group", "-"),
            last_done=kv.get("last_done", "-"),
        ))
    return rows


def _blocks_in_window(log_content: str, days: int, now_dt: datetime) -> list[str]:
    """Return block IDs with 'done' event within the last `days` days (inclusive)."""
    cutoff = (now_dt - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = now_dt.strftime("%Y-%m-%d")
    blocks = []
    for line in log_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[1] == "done":
            date_str = parts[3]
            if cutoff <= date_str <= end_date:
                blocks.append(parts[0])
    return blocks


def _timeline_entries(log_content: str, days: int, now_dt: datetime) -> list:
    """Return (date, block_id) tuples for last `days` days, newest first."""
    cutoff = (now_dt - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = now_dt.strftime("%Y-%m-%d")
    entries = []
    for line in log_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[1] == "done":
            date_str = parts[3]
            if cutoff <= date_str <= end_date:
                entries.append((date_str, parts[0]))
    entries.sort(key=lambda t: t[0], reverse=True)
    return entries


def _extract_recent_patterns(patterns_content: str, max_count: int = _MAX_PATTERNS) -> list[str]:
    """Extract up to max_count pattern names from governance/patterns.md."""
    _SKIP = {"patterns report", "summary table", "top patterns"}
    names = []
    for line in patterns_content.splitlines():
        m = re.match(r"^#{2,3}\s+(.+)", line.strip())
        if m:
            name = m.group(1).strip()
            if name.lower() not in _SKIP:
                names.append(name)
            if len(names) >= max_count:
                break
    return names


def _build_roadmap(
    current_phase_str: str,
    max_phase: int = _ROADMAP_MAX_PHASE,
) -> tuple[list[str], list[str], list[str]]:
    """
    Return (done, active, planned) phase number lists as strings.

    Phases 1..(cur-1) are done, [cur] is active, (cur+1)..max_phase are planned.
    """
    try:
        cur = int(current_phase_str)
    except (ValueError, TypeError):
        cur = 1

    done = [str(p) for p in range(1, cur)]
    active = [str(cur)]
    planned = [str(p) for p in range(cur + 1, max_phase + 1)]
    return done, active, planned


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

def generate_dashboard(
    arch_root: Optional[str] = None,
    now_ts: Optional[str] = None,
    # Injectable for testing
    log_content: Optional[str] = None,
    state_content: Optional[str] = None,
    next_content: Optional[str] = None,
    board_content: Optional[str] = None,
    patterns_content: Optional[str] = None,
    stale_tools: Optional[list] = None,
) -> DashboardData:
    """
    Generate a DashboardData snapshot from project files.
    All content parameters are injectable for testing (None → read from disk).
    """
    now_dt: datetime
    if now_ts:
        now_dt = datetime.fromisoformat(now_ts)
        if now_dt.tzinfo is None:
            now_dt = now_dt.replace(tzinfo=timezone.utc)
    else:
        now_dt = datetime.now(timezone.utc)

    root = _arch_path(arch_root)

    if log_content is None:
        log_content = _read_file(root / BLOCK_LOG_PATH)
    if state_content is None:
        state_content = _read_file(root / STATE_PATH)
    if next_content is None:
        next_content = _read_file(root / NEXT_PATH)
    if board_content is None:
        board_content = _read_file(root / BOARD_PATH)
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

    current_phase = state.get("phase", "unknown")
    next_action = nxt.get("next_action", state.get("next", "unknown"))
    manifest = nxt.get("manifest", "-")
    last_block = state.get("last_block", "-")

    agents = _parse_board(board_content)

    blocks_7d = _blocks_in_window(log_content, _TIMELINE_DAYS, now_dt)
    velocity = _velocity(len(blocks_7d), _TIMELINE_DAYS)
    forecast = _forecast(velocity)

    from master_scheduler import URGENCY_CRITICAL
    critical_ids = [s.tool_id for s in stale_tools if s.urgency == URGENCY_CRITICAL]

    patterns = _extract_recent_patterns(patterns_content)
    timeline = _timeline_entries(log_content, _TIMELINE_DAYS, now_dt)
    phases_done, phases_active, phases_planned = _build_roadmap(current_phase)

    return DashboardData(
        generated_at=now_dt.isoformat(),
        current_phase=current_phase,
        next_action=next_action,
        manifest=manifest,
        last_block=last_block,
        agents=agents,
        blocks_closed_7d=blocks_7d,
        velocity_blocks_per_day=velocity,
        stale_tool_count=len(stale_tools),
        critical_tool_ids=critical_ids,
        forecast_blocks_next_7d=forecast,
        recent_patterns=patterns,
        timeline_entries=timeline,
        phases_done=phases_done,
        phases_active=phases_active,
        phases_planned=phases_planned,
    )


def render_html(data: DashboardData, css: Optional[str] = None) -> str:
    """Render DashboardData as a standalone HTML page (no CDN, dark theme)."""

    styles = css if css is not None else _FALLBACK_CSS

    def _row(label: str, value: str) -> str:
        return f"<tr><td>{label}</td><td><strong>{value}</strong></td></tr>"

    # -- Column 1: Active Agents --
    def _status_badge(status: str) -> str:
        cls = (
            "badge-active"  if status in ("wip", "wait") else
            "badge-done"    if status == "done" else
            "badge-planned"
        )
        return f'<span class="badge {cls}">{status}</span>'

    if data.agents:
        agent_rows = "\n".join(
            f"<tr><td>{a.agent_id}</td><td>{a.block}</td>"
            f"<td>{_status_badge(a.status)}</td><td>{a.last_done}</td></tr>"
            for a in data.agents
        )
    else:
        agent_rows = "<tr><td colspan='4'><em>no agents</em></td></tr>"

    # -- Column 3: Health Metrics --
    vel = (
        f"{data.velocity_blocks_per_day:.2f}/d"
        if data.velocity_blocks_per_day is not None else "n/a"
    )
    fcast = (
        f"~{data.forecast_blocks_next_7d}"
        if data.forecast_blocks_next_7d is not None else "n/a"
    )
    stale_cls = (
        "badge-critical" if data.critical_tool_ids else
        "badge-warning"  if data.stale_tool_count > 0 else
        "badge-done"
    )
    stale_val = f'<span class="badge {stale_cls}">{data.stale_tool_count}</span>'

    # -- Column 4: Recent Patterns --
    pattern_items = (
        "\n".join(f"<li>{p}</li>" for p in data.recent_patterns)
        if data.recent_patterns
        else "<li><em>none detected</em></li>"
    )

    # -- Timeline --
    if data.timeline_entries:
        tl_items = "\n".join(
            f'<li><span class="dot done"></span>'
            f'<div><strong>{b}</strong>'
            f' <span style="color:var(--text-dim)">{d}</span></div></li>'
            for d, b in data.timeline_entries[:20]
        )
    else:
        tl_items = "<li><em>No activity in last 7 days</em></li>"

    # -- Roadmap --
    def _pill(phase_num: str, cls: str) -> str:
        return f'<span class="phase-pill {cls}">Phase {phase_num}</span>\n'

    roadmap = (
        "".join(_pill(p, "done")    for p in data.phases_done)
        + "".join(_pill(p, "active")  for p in data.phases_active)
        + "".join(_pill(p, "planned") for p in data.phases_planned)
    )

    manifest_name = (
        data.manifest.split("/")[-1]
        if "/" in data.manifest else data.manifest
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cognitive Architecture — Live Dashboard</title>
  <style>
{styles}
  </style>
</head>
<body>
  <h1>&#x1F9E0; Cognitive Architecture — Dashboard</h1>
  <p class="meta">Phase {data.current_phase} &nbsp;&middot;&nbsp;
     Last: {data.last_block} &nbsp;&middot;&nbsp; {data.generated_at[:10]}</p>

  <div class="dash-grid">

    <!-- Column 1: Active Agents -->
    <div class="card card-teal">
      <h2>Active Agents</h2>
      <table>
        <thead><tr><th>Agent</th><th>Block</th><th>Status</th><th>Last Done</th></tr></thead>
        <tbody>{agent_rows}</tbody>
      </table>
    </div>

    <!-- Column 2: Next Actions -->
    <div class="card card-gold">
      <h2>Next Actions</h2>
      <table>
        {_row("Next action", data.next_action)}
        {_row("Manifest", manifest_name)}
        {_row("Last block", data.last_block)}
        {_row("Phase", data.current_phase)}
      </table>
    </div>

    <!-- Column 3: Health Metrics -->
    <div class="card">
      <h2>Health Metrics</h2>
      <table>
        {_row("Blocks (7d)", str(len(data.blocks_closed_7d)))}
        {_row("Velocity", vel)}
        {_row("Forecast (7d)", fcast)}
        {_row("Stale tools", stale_val)}
      </table>
    </div>

    <!-- Column 4: Recent Patterns -->
    <div class="card card-green">
      <h2>Recent Patterns</h2>
      <ul>{pattern_items}</ul>
    </div>

  </div>

  <!-- Timeline -->
  <div class="card">
    <h2>Timeline &mdash; Last 7 Days</h2>
    <ul class="timeline">
      {tl_items}
    </ul>
  </div>

  <!-- Roadmap -->
  <div class="card card-gold">
    <h2>Roadmap</h2>
    <div class="phase-row">
      {roadmap}
    </div>
  </div>

  <!-- Footer: Quick Commands -->
  <div class="card" style="border-left-color:var(--grey)">
    <h2>Quick Commands</h2>
    <table>
      {_row("Regenerate dashboard", "<code>python sdk/dashboard_generator.py --arch-root .</code>")}
      {_row("Weekly report",        "<code>python sdk/weekly_report.py --arch-root .</code>")}
      {_row("Check schedule",       "<code>python sdk/master_scheduler.py --arch-root . --report</code>")}
      {_row("Run audit",            "<code>bash audit.sh</code>")}
    </table>
  </div>

  <p class="generated">Generated {data.generated_at}</p>
</body>
</html>"""


def write_dashboard(
    data: DashboardData,
    arch_root: Optional[str] = None,
) -> Path:
    """
    Write dashboard HTML to governance/dashboard.html.
    Reads templates/_styles.css if available; falls back to embedded CSS.
    Returns the output path.
    """
    root = _arch_path(arch_root)

    # Try to load shared styles for standalone HTML
    css: Optional[str] = None
    try:
        css = (root / STYLES_PATH).read_text(encoding="utf-8")
    except OSError:
        css = None  # render_html will use _FALLBACK_CSS

    out_path = root / DASHBOARD_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_html(data, css=css), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Live dashboard generator")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--stdout", action="store_true", help="Print HTML to stdout instead of writing file")
    args = parser.parse_args()

    data = generate_dashboard(arch_root=args.arch_root)
    if args.stdout:
        print(render_html(data))
    else:
        path = write_dashboard(data, arch_root=args.arch_root)
        print(f"Dashboard written: {path}")
