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
    """Close the self-observation loop: extract → analyze (full history) →
    recommend → render → propose. New proposals land in governance/proposals/.
    """
    try:
        sys.path.insert(0, str(arch_root / "sdk"))
        from patterns_report import run_pipeline

        summary = run_pipeline(arch_root, window_size=None, propose=True)
        return True, (
            f"Extracted {summary['signals']} signals → {summary['patterns']} patterns "
            f"({summary['recommendations']} with recommendation) → "
            f"{summary['proposals_created']} new proposal(s)"
        )
    except Exception as exc:
        return False, str(exc)


def run_dashboard(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/dashboard_generator.py", "--arch-root", "."], arch_root, "dashboard")


def run_weekly_report(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/weekly_report.py", "--arch-root", "."], arch_root, "weekly-report")


def run_integrity_check(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/integrity_check.py", "--verify", "--strict", "--arch-root", "."], arch_root, "integrity-check")


def run_invariant_check(arch_root: Path) -> tuple[bool, str]:
    """Run the anti-drift engine and return (ok, count-summary).

    SURFACES drift but never aborts the session: `ok` here is just "the runner
    completed" (always True unless the engine itself blew up, which it won't —
    run_all degrades errors to warns). The block-close HALT lives in
    invariant_check.gate_result(), NOT here. Imported in-process (not subprocess)
    so INV4 sees the live TOOL_RUNNERS and the summary needs no output parsing.
    """
    try:
        sys.path.insert(0, str(arch_root / "sdk"))
        import invariant_check
        violations = invariant_check.run_all(arch_root)
        criticals = sum(1 for v in violations if v.severity == "critical")
        warns = sum(1 for v in violations if v.severity == "warn")
        tag = " CRITICAL" if criticals else ""
        return True, f"{criticals} critical, {warns} warn{tag}"
    except Exception as exc:  # never block session start on a checker hiccup
        return False, str(exc)


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
        # Block-163: extended key list includes dual-mode fields
        for key in ("p", "status", "last_block", "notes", "mode", "current_client",
                    "tickets_open", "last_scan_at"):
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


def run_phase_forecast(arch_root: Path) -> tuple[bool, str]:
    return _run([sys.executable, "sdk/phase_forecast.py", "--arch-root", "."], arch_root, "phase-forecast")


# Note: proposal generation is folded into pattern-mining (run_pipeline with
# propose=True) so the loop closes in one tracked tool — no separate
# protocol-updater runner is needed.

TOOL_RUNNERS = {
    "health-report": run_health_report,
    "pattern-mining": run_pattern_mining,
    "dashboard-refresh": run_dashboard,
    "weekly-report": run_weekly_report,
    "integrity-check": run_integrity_check,
    "invariant-check": run_invariant_check,
    "audit": run_audit_py,
    "phase-forecast": run_phase_forecast,
}


_PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
_MAX_GOVERNOR_DISPLAY = 10


def _display_governor_notifications(arch_root: Path) -> None:
    """Display pending+seen governor notifications. Never raises."""
    try:
        sys.path.insert(0, str(arch_root / "sdk"))
        from notification_manager import Governor
        from datetime import date as _date
        gov = Governor(arch_root)
        items = [n for n in gov.list(pending_only=False) if n.status in ("pending", "seen")]
        if not items:
            return
        items.sort(key=lambda n: (_PRIORITY_ORDER.get(n.priority, 9), n.created_at))
        shown = items[:_MAX_GOVERNOR_DISPLAY]
        for n in shown:
            try:
                age = (_date.today() - _date.fromisoformat(n.created_at)).days
            except ValueError:
                age = 0
            tag = n.priority.upper()
            print(f"  [GOVERNOR] {tag} — {n.message} (id:{n.id}, age:{age}d)")
            if n.status == "pending":
                gov.seen(n.id)
        extra = len(items) - len(shown)
        if extra > 0:
            print(f"  [GOVERNOR] {extra} more — run `python sdk/notification_manager.py list`")
    except Exception:
        pass  # governor display never blocks session start


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

    # Read project state — dual-mode (block-163)
    state = _read_state(arch_root)
    next_action = _read_next(arch_root)
    mode = state.get("mode", "mmorpg")
    print(f"\n  Phase: {state.get('p', '?')} | Status: {state.get('status', '?')} | Mode: {mode}")
    print(f"  Last block: {state.get('last_block', '?')} | Next: {next_action}")
    if mode == "corporate":
        client = state.get("current_client", "~")
        tickets = state.get("tickets_open", "0")
        last_scan = state.get("last_scan_at", "never")
        print(f"  Client: {client} | Open tickets: {tickets} | Last scan: {last_scan}")
    print()

    # Run stale tools
    ran = []
    skipped = []
    failed = []
    unrunnable = []

    for tool in tools:
        tid = tool.get("id", "")
        trigger = tool.get("trigger_type", "time")
        interval = tool.get("recommended_interval_days", "1")
        last_run = tool.get("last_run", "never")

        if trigger == "event":
            continue  # skip event-triggered (briefing, dependency-check)

        if tid not in TOOL_RUNNERS:
            unrunnable.append(tid)
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

    # Summary
    print()
    print("-" * 60)
    print(f"  Ran:     {', '.join(ran) if ran else 'none'}")
    print(f"  Skipped: {', '.join(skipped) if skipped else 'none'}")
    if unrunnable:
        print(f"  No runner (stale, needs implementation): {', '.join(unrunnable)}")
    if failed:
        print(f"  FAILED:  {', '.join(failed)}")
    print()

    # Proposals summary (Phase 20)
    pending_proposals = _count_pending_proposals(arch_root)
    if pending_proposals > 0:
        print(f"  [PROPOSALS] {pending_proposals} pending — see governance/proposals/")
    else:
        print(f"  [PROPOSALS] 0 pending — none to review")

    # Invariants summary (Phase 25 / block-146) — SURFACE drift, never abort.
    # Always printed (independent of whether the invariant-check tool was stale),
    # so the count is visible every session. The HALT capability lives only in
    # invariant_check.gate_result() for block-close; here we report and continue.
    try:
        sys.path.insert(0, str(arch_root / "sdk"))
        import invariant_check
        _viol = invariant_check.run_all(arch_root)
        _crit = sum(1 for v in _viol if v.severity == "critical")
        _warn = sum(1 for v in _viol if v.severity == "warn")
        _tag = " [CRITICAL]" if _crit else ""
        print(f"  [INVARIANTS] {_crit} critical, {_warn} warn{_tag} — see sdk/invariant_check.py")
    except Exception:
        pass  # invariant surfacing never blocks session start

    # block-175: Calendar alerts (show before anything else in the day)
    try:
        sys.path.insert(0, str(arch_root / "sdk"))
        from calendar_manager import get_today_alerts, get_upcoming_alerts
        today_alerts = get_today_alerts(arch_root)
        upcoming_alerts = get_upcoming_alerts(arch_root, days=2)
        if today_alerts:
            print()
            for alert in today_alerts:
                print(f"  ⚠️  REUNIÃO: {alert}")
        if upcoming_alerts:
            for alert in upcoming_alerts:
                print(f"  📅  {alert}")
    except Exception:
        pass  # never block session start on calendar failure

    # Governor notifications (Phase 21)
    _display_governor_notifications(arch_root)

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
            try:
                import health_model as _hm
                tag = _hm.label_for(score)
            except Exception:
                tag = "HEALTHY" if score >= 90 else "DEGRADED" if score >= 70 else "CRITICAL"
            print(f"  Health: {score}/100 [{tag}]")

    # Phase-completion forecast (Phase 26 / block-151) — dated estimate next to
    # Health. In-process call (mirrors [INVARIANTS]) so it prints every session;
    # wrapped so a forecast hiccup never aborts session start.
    try:
        sys.path.insert(0, str(arch_root / "sdk"))
        import phase_forecast
        _fc = phase_forecast.forecast(arch_root)
        print(f"  Forecast: {_fc.completion_estimate} ({_fc.confidence})")
    except Exception:
        pass  # forecast surfacing never blocks session start

    print("=" * 60)
    print()


if __name__ == "__main__":
    import io as _io

    parser = argparse.ArgumentParser(description="cognitive-arch session initializer")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--force", action="store_true", help="Force run all tools regardless of freshness")
    parser.add_argument("--validate-ux", action="store_true", help="Run ux_validator on session output after summary")
    args = parser.parse_args()
    arch = Path(args.arch_root).resolve()

    if args.validate_ux:
        buf = _io.StringIO()
        _orig_stdout = sys.stdout
        sys.stdout = buf
        try:
            run_session_start(arch, force=args.force)
        finally:
            sys.stdout = _orig_stdout
        output = buf.getvalue()
        print(output, end="")
        try:
            sys.path.insert(0, str(arch / "sdk"))
            from ux_validator import UxValidator
            v = UxValidator.from_ux_voice(arch)
            violations = v.check(output)
            if violations:
                print(f"\n[ux_validator] {len(violations)} violation(s) in session output:")
                for viol in violations[:10]:
                    print(f"  WARN L{viol.line_num}: {viol.message}")
        except Exception:
            pass
    else:
        run_session_start(arch, force=args.force)
