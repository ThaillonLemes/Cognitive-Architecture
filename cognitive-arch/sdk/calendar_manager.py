# sdk/calendar_manager.py
# PURPOSE: Manage pilot-calendar.yaml: add/list/remove meetings (including recurring).
#          Inject meeting alerts in session_start when meetings are same-day.
# INPUTS:  --add-meeting, --list, --remove, --arch-root
# OUTPUTS: governance/pilot-calendar.yaml; alert strings for session_start
# DEPS:    stdlib only
# USAGE:   python sdk/calendar_manager.py --add-meeting "2026-06-02 14:00 2h sync"
#          python sdk/calendar_manager.py --list --arch-root .
# SEE:     design/forecast-calendar.md §3

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from typing import Optional

def _fix_utf8() -> None:
    import io as _io
    if sys.platform == "win32":
        if hasattr(sys.stdout, "buffer") and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == "utf-8"
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_fix_utf8()


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Meeting:
    date: str           # YYYY-MM-DD
    time: str           # HH:MM
    duration_hours: float
    desc: str
    recurring: str = ""  # "" | "daily" | "weekly" | "biweekly"


# ---------------------------------------------------------------------------
# Calendar YAML helpers (no pyyaml dependency)
# ---------------------------------------------------------------------------

_CAL_HEADER = """\
# governance/pilot-calendar.yaml
# Edited by AI when Piloto dictates meetings.
# Interface: python sdk/calendar_manager.py --add-meeting "YYYY-MM-DD HH:MM <Nh> <desc>"
# See: design/forecast-calendar.md §3

meetings:
"""


def _read_calendar(arch_root: Path) -> list[Meeting]:
    """Parse pilot-calendar.yaml into list of Meeting objects."""
    cal_path = arch_root / "governance" / "pilot-calendar.yaml"
    if not cal_path.exists():
        return []
    text = cal_path.read_text(encoding="utf-8", errors="replace")
    meetings: list[Meeting] = []
    current: dict = {}
    in_meetings = False

    for line in text.splitlines():
        if line.strip() == "meetings:":
            in_meetings = True
            continue
        if not in_meetings:
            continue
        if re.match(r"\s+- date:", line):
            if current:
                meetings.append(_dict_to_meeting(current))
            current = {"date": line.split(":", 1)[1].strip()}
        elif re.match(r"\s+time:", line):
            current["time"] = line.split(":", 1)[1].strip().strip('"')
        elif re.match(r"\s+duration_hours:", line):
            try:
                current["duration_hours"] = float(line.split(":", 1)[1].strip())
            except ValueError:
                current["duration_hours"] = 1.0
        elif re.match(r"\s+desc:", line):
            current["desc"] = line.split(":", 1)[1].strip().strip('"')
        elif re.match(r"\s+recurring:", line):
            current["recurring"] = line.split(":", 1)[1].strip()

    if current:
        meetings.append(_dict_to_meeting(current))
    return meetings


def _dict_to_meeting(d: dict) -> Meeting:
    return Meeting(
        date=d.get("date", ""),
        time=d.get("time", "09:00"),
        duration_hours=float(d.get("duration_hours", 1.0)),
        desc=d.get("desc", "reunião"),
        recurring=d.get("recurring", ""),
    )


def _write_calendar(arch_root: Path, meetings: list[Meeting]) -> None:
    """Write meetings back to pilot-calendar.yaml."""
    cal_path = arch_root / "governance" / "pilot-calendar.yaml"
    lines = [_CAL_HEADER.rstrip() + "\n"]
    for m in meetings:
        lines.append(f'  - date: {m.date}')
        lines.append(f'    time: "{m.time}"')
        lines.append(f'    duration_hours: {m.duration_hours}')
        lines.append(f'    desc: "{m.desc}"')
        if m.recurring:
            lines.append(f'    recurring: {m.recurring}')
    cal_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Recurrence expansion
# ---------------------------------------------------------------------------

def expand_recurring(meetings: list[Meeting], horizon_days: int = 30) -> list[Meeting]:
    """Expand recurring meetings into concrete dates within horizon_days from today."""
    today = date.today()
    result: list[Meeting] = []
    seen_descs: dict[str, list[str]] = {}

    for m in meetings:
        if not m.recurring:
            result.append(m)
            continue

        # Find next occurrences
        try:
            base_date = date.fromisoformat(m.date)
        except ValueError:
            result.append(m)
            continue

        step = {"daily": 1, "weekly": 7, "biweekly": 14}.get(m.recurring, 7)

        current = base_date
        while (current - today).days <= horizon_days:
            if current >= today:
                key = f"{m.desc}_{m.time}"
                dates = seen_descs.get(key, [])
                dt_str = current.isoformat()
                if dt_str not in dates:
                    result.append(Meeting(
                        date=dt_str,
                        time=m.time,
                        duration_hours=m.duration_hours,
                        desc=m.desc,
                        recurring="",  # expanded instances are concrete
                    ))
                    dates.append(dt_str)
                    seen_descs[key] = dates
            current = current + timedelta(days=step)

    return result


# ---------------------------------------------------------------------------
# Alert generation
# ---------------------------------------------------------------------------

def get_today_alerts(arch_root: Path) -> list[str]:
    """Return alert strings for meetings today."""
    meetings = _read_calendar(arch_root)
    expanded = expand_recurring(meetings)
    today_str = date.today().isoformat()
    now = datetime.now(timezone.utc)
    alerts: list[str] = []

    for m in expanded:
        if m.date != today_str:
            continue
        # Compute time until meeting
        try:
            hour, minute = map(int, m.time.split(":"))
            meeting_dt = datetime.now(timezone.utc).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            diff = meeting_dt - now
            if diff.total_seconds() > 0:
                h = int(diff.total_seconds() // 3600)
                mins = int((diff.total_seconds() % 3600) // 60)
                time_str = f"{h}h{mins:02d}m" if h > 0 else f"{mins}m"
                alerts.append(f"Reunião em {time_str} — {m.desc} às {m.time}")
            else:
                alerts.append(f"Reunião hoje às {m.time} — {m.desc} (passou ou em curso)")
        except ValueError:
            alerts.append(f"Reunião hoje às {m.time} — {m.desc}")

    return alerts


def get_upcoming_alerts(arch_root: Path, days: int = 3) -> list[str]:
    """Return upcoming meeting alerts for the next N days (excluding today)."""
    meetings = _read_calendar(arch_root)
    expanded = expand_recurring(meetings)
    today = date.today()
    alerts: list[str] = []

    for m in expanded:
        try:
            m_date = date.fromisoformat(m.date)
        except ValueError:
            continue
        diff_days = (m_date - today).days
        if 1 <= diff_days <= days:
            label = "Amanhã" if diff_days == 1 else f"Em {diff_days} dias"
            alerts.append(f"{label}: reunião às {m.time} — {m.desc} ({m.duration_hours}h)")

    return alerts


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

def add_meeting(
    arch_root: Path,
    date_str: str,
    time_str: str,
    duration_hours: float,
    desc: str,
    recurring: str = "",
) -> Meeting:
    """Add a meeting to the calendar."""
    meetings = _read_calendar(arch_root)
    m = Meeting(date=date_str, time=time_str, duration_hours=duration_hours,
                desc=desc, recurring=recurring)
    meetings.append(m)
    # Sort by date
    meetings.sort(key=lambda x: x.date)
    _write_calendar(arch_root, meetings)
    return m


def _parse_meeting_str(text: str) -> tuple[str, str, float, str, str]:
    """Parse meeting string: 'YYYY-MM-DD HH:MM Nh desc [recurring:weekly]'"""
    recurring = ""
    # Extract recurring pattern
    rec_m = re.search(r"recurring:(\w+)", text)
    if rec_m:
        recurring = rec_m.group(1)
        text = text.replace(rec_m.group(0), "").strip()

    parts = text.split()
    if len(parts) < 3:
        raise ValueError(f"Invalid meeting format: '{text}'. Expected: YYYY-MM-DD HH:MM Nh desc")

    date_str = parts[0]
    time_str = parts[1]

    # Duration: Nh or N
    dur_m = re.match(r"([0-9.]+)h?", parts[2])
    duration = float(dur_m.group(1)) if dur_m else 1.0

    desc = " ".join(parts[3:]) if len(parts) > 3 else "reunião"
    return date_str, time_str, duration, desc, recurring


def remove_meeting(arch_root: Path, date_str: str, desc: str) -> bool:
    """Remove a meeting by date and description. Returns True if removed."""
    meetings = _read_calendar(arch_root)
    before = len(meetings)
    meetings = [m for m in meetings
                if not (m.date == date_str and (not desc or desc.lower() in m.desc.lower()))]
    if len(meetings) < before:
        _write_calendar(arch_root, meetings)
        return True
    return False


def list_meetings(arch_root: Path, horizon_days: int = 14) -> list[Meeting]:
    """List all meetings in the next horizon_days (including recurring expanded)."""
    meetings = _read_calendar(arch_root)
    expanded = expand_recurring(meetings, horizon_days)
    today = date.today()
    return [m for m in expanded
            if (date.fromisoformat(m.date) - today).days >= 0]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="calendar_manager",
        description="Manage pilot-calendar.yaml and generate meeting alerts.",
    )
    p.add_argument("--arch-root", default=".")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--add-meeting", metavar="STRING",
                   help="Add meeting: 'YYYY-MM-DD HH:MM Nh desc [recurring:weekly]'")
    g.add_argument("--list", action="store_true")
    g.add_argument("--alerts", action="store_true", help="Show today's alerts")
    g.add_argument("--remove", nargs=2, metavar=("DATE", "DESC"),
                   help="Remove meeting by date and description")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    gov = arch_root / "governance"
    gov.mkdir(exist_ok=True)

    if args.add_meeting:
        date_str, time_str, duration, desc, recurring = _parse_meeting_str(args.add_meeting)
        m = add_meeting(arch_root, date_str, time_str, duration, desc, recurring)
        print(f"[calendar] Added: {m.date} {m.time} {m.duration_hours}h — {m.desc}"
              + (f" (recurring: {m.recurring})" if m.recurring else ""))

    elif args.list:
        meetings = list_meetings(arch_root)
        if not meetings:
            print("[calendar] No upcoming meetings.")
        for m in meetings:
            rec_tag = f" ({m.recurring})" if m.recurring else ""
            print(f"  {m.date} {m.time}  {m.duration_hours}h  {m.desc}{rec_tag}")

    elif args.alerts:
        alerts = get_today_alerts(arch_root)
        upcoming = get_upcoming_alerts(arch_root)
        if alerts:
            for a in alerts:
                print(f"  REUNIAO: {a}")
        if upcoming:
            for a in upcoming:
                print(f"  PROXIMA: {a}")
        if not alerts and not upcoming:
            print("[calendar] Sem reuniões próximas.")

    elif args.remove:
        removed = remove_meeting(arch_root, args.remove[0], args.remove[1])
        print(f"[calendar] Removed: {removed}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
