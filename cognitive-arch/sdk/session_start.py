# sdk/session_start.py
# PURPOSE: Mandatory session initializer. Run at start of EVERY session.
#          Checks tool freshness, runs stale tools, updates registry, prints briefing.
# INPUTS:  governance/tools-registry.yaml, sdk/* tools, STATE.md, NEXT.md
# OUTPUTS: Updated last_run in tools-registry.yaml; console briefing; refreshed governance/
# DEPS:    stdlib only (subprocess, pathlib, datetime, yaml-via-manual-parse)
# USAGE:   python sdk/session_start.py --arch-root .
# SEE:     protocols/dashboard-integration.md, governance/tools-registry.yaml, CLAUDE.md

from __future__ import annotations

import argparse
import io
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# Force UTF-8 output on Windows
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
# Registry helpers (no pyyaml dependency — parse manually)
# ---------------------------------------------------------------------------

def _parse_registry(registry_path: Path) -> list[dict]:
    """Parse tools-registry.yaml into list of tool dicts. Returns [] on error."""
    if not registry_path.exists():
        return []
    text = registry_path.read_text(encoding="utf-8")
    tools = []
    current: dict = {}
    in_tools = False
    for line in text.splitlines():
        if line.strip() == "tools:":
            in_tools = True
            continue
        if not in_tools:
            continue
        if line.startswith("  - id:"):
            if current:
                tools.append(current)
            current = {"id": line.split(":", 1)[1].strip().strip('"')}
        elif line.startswith("    ") and ":" in line and current:
            key, _, val = line.strip().partition(":")
            current[key.strip()] = val.strip().strip('"')
    if current:
        tools.append(current)
    return tools


def _count_pending_proposals(arch_root: Path) -> int:
    """Count proposals with status:pending in governance/proposals/index.md."""
    index_path = arch_root / "governance" / "proposals" / "index.md"
    if not index_path.exists():
        return 0
    try:
        text = index_path.read_text(encoding="utf-8", errors="replace")
        return text.count("| pending |")
    except OSError:
        return 0


def _update_last_run(registry_path: Path, tool_id: str, ts: str) -> None:
    """Update last_run for tool_id in registry file in-place."""
    if not registry_path.exists():
        return
    text = registry_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    inside_tool = False
    updated = []
    for line in lines:
        if re.match(rf"\s+- id:\s+['\"]?{re.escape(tool_id)}['\"]?", line):
            inside_tool = True
        elif inside_tool and re.match(r"\s+- id:", line):
            inside_tool = False
        if inside_tool and re.match(r"\s+last_run:", line):
            indent = len(line) - len(line.lstrip())
            line = " " * indent + f'last_run: "{ts}"'
            inside_tool = False  # only replace first occurrence
        updated.append(line)
    registry_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _is_stale(last_run_str: str, interval_days_str: str, now: datetime) -> bool:
    """Return True if tool is stale (never run or older than interval)."""
    interval_days = float(interval_days_str) if interval_days_str else 1.0
    if interval_days == 0:
        return False  # event-triggered tools — not time-stale
    if last_run_str in ("never", "", "null", "~"):
        return True
    try:
        last = datetime.fromisoformat(last_run_str.replace("Z", "+00:00"))
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return (now - last) > timedelta(days=interval_days)
    except ValueError:
        return True


# ---------------------------------------------------------------------------
# Tool runners
# ---------------------------------------------------------------------------

def _run(cmd: list[str], arch_root: Path, label: str) -> tuple[bool, str]:
    """Run a command. Return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(arch_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        ok = result.returncode == 0
        out = (result.stdout or "") + (result.stderr or "")
        return ok, out.strip()
    except Exception as exc:
        return False, str(exc)


def run_health_report(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/health_report.py", "--arch-root", "."], arch_root, "health-report")


def run_pattern_mining(arch_root: Path) -> tuple[bool, str]:
    """Run full pattern mining pipeline programmatically."""
    try:
        sys.path.insert(0, str(arch_root / "sdk"))
        from retro_signals import extract_all
        from pattern_analyzer import analyze
        from patterns_report import write_report

        signals = extract_all(arch_root)
        patterns = analyze(signals)
        write_report(patterns, arch_root)
        return True, f"Extracted {len(signals)} signals → {len(patterns)} patterns"
    except Exception as exc:
        return False, str(exc)


def run_dashboard(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/dashboard_generator.py", "--arch-root", "."], arch_root, "dashboard")


def run_weekly_report(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/weekly_report.py", "--arch-root", "."], arch_root, "weekly-report")


def run_integrity_check(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/integrity_check.py", "--verify", "--arch-root", "."], arch_root, "integrity-check")


# ---------------------------------------------------------------------------
# Session gap detection
# ---------------------------------------------------------------------------

def _detect_session_gap(arch_root: Path, now: datetime) -> Optional[float]:
    """Return hours since last session, or None if unknown."""
    registry_path = arch_root / "governance" / "tools-registry.yaml"
    tools = _parse_registry(registry_path)
    # Use health-report last_run as proxy for last session
    for t in tools:
        if t.get("id") == "health-report":
            lr = t.get("last_run", "never")
            if lr not in ("never", "", "null"):
                try:
                    last = datetime.fromisoformat(lr.replace("Z", "+00:00"))
                    if last.tzinfo is None:
                        last = last.replace(tzinfo=timezone.utc)
                    return (now - last).total_seconds() / 3600
                except ValueError:
                    pass
    return None


# ---------------------------------------------------------------------------
# State reading
# ---------------------------------------------------------------------------

def _read_state(arch_root: Path) -> dict:
    state_path = arch_root / "STATE.md"
    if not state_path.exists():
        return {}
    text = state_path.read_text(encoding="utf-8", errors="replace")
    data = {}
    for line in text.splitlines():
        for key in ("p", "status", "last_block", "notes"):
            m = re.search(rf"\b{key}:(\S+)", line)
            if m:
                data[key] = m.group(1)
    return data


def _read_next(arch_root: Path) -> str:
    next_path = arch_root / "NEXT.md"
    if not next_path.exists():
        return "-"
    text = next_path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"next_action:(\S+)", text)
    return m.group(1) if m else "-"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_audit_py(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/audit.py", "--arch-root", "."], arch_root, "audit")


def run_protocol_updater(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/protocol_updater.py", "--arch-root", "."], arch_root, "protocol-updater")


TOOL_RUNNERS = {
    "health-report": run_health_report,
    "pattern-mining": run_pattern_mining,
    "dashboard-refresh": run_dashboard,
    "weekly-report": run_weekly_report,
    "integrity-check": run_integrity_check,
    "audit": run_audit_py,
    "protocol-updater": run_protocol_updater,
}


def run_session_start(arch_root: Path, force: bool = False) -> None:
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%dT%H:%MZ")
    registry_path = arch_root / "governance" / "tools-registry.yaml"

    # Detect session gap
    gap_h = _detect_session_gap(arch_root, now)

    # Parse registry
    tools = _parse_registry(registry_path)

    print("=" * 60)
    print("  cognitive-arch :: SESSION START")
    print(f"  {now.strftime('%Y-%m-%d %H:%M UTC')}")
    if gap_h is not None:
        print(f"  Session gap: {gap_h:.1f}h since last run")
    print("=" * 60)

    # Read project state
    state = _read_state(arch_root)
    next_action = _read_next(arch_root)
    print(f"\n  Phase: {state.get('p', '?')} | Status: {state.get('status', '?')}")
    print(f"  Last block: {state.get('last_block', '?')} | Next: {next_action}")
    print()

    # Run stale tools
    ran = []
    skipped = []
    failed = []

    for tool in tools:
        tid = tool.get("id", "")
        trigger = tool.get("trigger_type", "time")
        interval = tool.get("recommended_interval_days", "1")
        last_run = tool.get("last_run", "never")

        if trigger == "event":
            continue  # skip event-triggered (briefing, dependency-check)

        if tid not in TOOL_RUNNERS:
            skipped.append(tid)
            continue

        stale = force or _is_stale(last_run, interval, now)
        if not stale:
            skipped.append(tid)
            continue

        print(f"  [RUN] {tid} (last: {last_run})")
        ok, out = TOOL_RUNNERS[tid](arch_root)
        if ok:
            _update_last_run(registry_path, tid, now_str)
            ran.append(tid)
            # show first line of output
            first_line = out.splitlines()[0] if out else "ok"
            print(f"       OK — {first_line}")
        else:
            failed.append(tid)
            print(f"       FAILED — {out[:120]}")

    # Post-pause briefing
    if gap_h is not None and gap_h >= 24:
        print(f"\n  [BRIEFING] Gap={gap_h:.1f}h — generating post-pause briefing...")
        ok, out = _run(
            [sys.executable, "sdk/briefing_generator.py", "--arch-root", ".",
             "--last-active", (now - timedelta(hours=gap_h)).strftime("%Y-%m-%d")],
            arch_root, "briefing"
        )
        if ok:
            _update_last_run(registry_path, "post-pause-briefing", now_str)
            ran.append("post-pause-briefing")
        else:
            failed.append("post-pause-briefing")

    # Update health-report last_run (always runs at session start)
    _update_last_run(registry_path, "health-report", now_str)
    _update_last_run(registry_path, "dashboard-refresh", now_str)

    # Summary
    print()
    print("-" * 60)
    print(f"  Ran:     {', '.join(ran) if ran else 'none'}")
    print(f"  Skipped: {', '.join(skipped) if skipped else 'none'}")
    if failed:
        print(f"  FAILED:  {', '.join(failed)}")
    print()

    # Proposals summary (Phase 20)
    pending_proposals = _count_pending_proposals(arch_root)
    if pending_proposals > 0:
        print(f"  [PROPOSALS] {pending_proposals} pending — see governance/proposals/")
    else:
        print(f"  [PROPOSALS] 0 pending — none to review")

    # Patterns summary
    patterns_path = arch_root / "governance" / "patterns.md"
    if patterns_path.exists():
        text = patterns_path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\*\*Total patterns:\*\* (\d+)", text)
        if m and int(m.group(1)) > 0:
            print(f"  [!] Active patterns detected: {m.group(1)} — check governance/patterns.md")

    health_path = sorted((arch_root / "governance").glob("health-report-*.md"))
    if health_path:
        text = health_path[-1].read_text(encoding="utf-8", errors="replace")
        m = re.search(r"Score: (\d+)/100", text)
        if m:
            score = int(m.group(1))
            tag = "HEALTHY" if score >= 90 else "WARNING" if score >= 70 else "CRITICAL"
            print(f"  Health: {score}/100 [{tag}]")

    print("=" * 60)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="cognitive-arch session initializer")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--force", action="store_true", help="Force run all tools regardless of freshness")
    args = parser.parse_args()
    run_session_start(Path(args.arch_root).resolve(), force=args.force)
