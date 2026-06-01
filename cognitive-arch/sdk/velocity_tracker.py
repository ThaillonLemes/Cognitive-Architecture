# sdk/velocity_tracker.py
# PURPOSE: Capture real time per block and phase. Supports pause/resume to exclude
#          meeting time. block_start writes started_at; block_close writes finished_at
#          and calls this to compute actual_duration_hours. phase_manager writes
#          phase_started_at / phase_finished_at.
# INPUTS:  --pause/--resume/--status --block-id, --arch-root
# OUTPUTS: Updates manifest started_at, paused_at, resumed_at, finished_at, actual_duration_hours
# DEPS:    stdlib only
# USAGE:   python sdk/velocity_tracker.py --pause --block-id block-XXX --arch-root .
#          python sdk/velocity_tracker.py --resume --block-id block-XXX --arch-root .
# SEE:     design/forecast-calendar.md §1

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
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

_ISO_FMT = "%Y-%m-%dT%H:%MZ"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime(_ISO_FMT)


def _parse_iso(s: str) -> Optional[datetime]:
    if not s or s in ("~", "null", "none"):
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _find_manifest(arch_root: Path, block_id: str) -> Optional[Path]:
    cands = list((arch_root / "manifests").glob(f"{block_id}-*.md"))
    return cands[0] if cands else None


def _read_yaml_field(text: str, field: str) -> str:
    m = re.search(rf"^{field}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _set_yaml_field(text: str, field: str, value: str) -> str:
    """Set a YAML field in manifest text. Inserts after frontmatter header if not present."""
    if re.search(rf"^{field}:", text, re.MULTILINE):
        return re.sub(rf"^{field}:\s*.*$", f"{field}: {value}", text, flags=re.MULTILINE)
    # Insert after first ---...--- block
    parts = text.split("---", 2)
    if len(parts) >= 3:
        parts[1] = parts[1].rstrip() + f"\n{field}: {value}\n"
        return "---".join(parts)
    return text + f"\n{field}: {value}\n"


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def stamp_started(arch_root: Path, block_id: str) -> str:
    """Write started_at to manifest. Called by block_start.py. Returns timestamp."""
    manifest = _find_manifest(arch_root, block_id)
    if not manifest:
        return ""
    ts = _now_iso()
    text = manifest.read_text(encoding="utf-8", errors="replace")
    text = _set_yaml_field(text, "started_at", ts)
    manifest.write_text(text, encoding="utf-8")
    return ts


def pause_timer(arch_root: Path, block_id: str) -> str:
    """Write paused_at to manifest. Returns elapsed time string."""
    manifest = _find_manifest(arch_root, block_id)
    if not manifest:
        return "manifest not found"
    ts = _now_iso()
    text = manifest.read_text(encoding="utf-8", errors="replace")

    started_str = _read_yaml_field(text, "started_at")
    elapsed_msg = ""
    started = _parse_iso(started_str)
    if started:
        elapsed_h = round((datetime.now(timezone.utc) - started).total_seconds() / 3600, 2)
        elapsed_msg = f"Tempo decorrido até agora: {elapsed_h}h"

    text = _set_yaml_field(text, "paused_at", ts)
    manifest.write_text(text, encoding="utf-8")
    return f"Bloco pausado às {ts}. {elapsed_msg}"


def resume_timer(arch_root: Path, block_id: str) -> str:
    """Write resumed_at, compute pause_duration. Returns message."""
    manifest = _find_manifest(arch_root, block_id)
    if not manifest:
        return "manifest not found"
    ts = _now_iso()
    text = manifest.read_text(encoding="utf-8", errors="replace")

    paused_str = _read_yaml_field(text, "paused_at")
    pause_msg = ""
    paused = _parse_iso(paused_str)
    if paused:
        pause_dur = round((datetime.now(timezone.utc) - paused).total_seconds() / 3600, 2)
        pause_msg = f"Pausa: {pause_dur}h (será descontada)"
        text = _set_yaml_field(text, "paused_duration_hours", str(pause_dur))

    text = _set_yaml_field(text, "resumed_at", ts)
    manifest.write_text(text, encoding="utf-8")
    return f"Bloco retomado às {ts}. {pause_msg}"


def stamp_finished(arch_root: Path, block_id: str) -> tuple[str, float]:
    """Write finished_at and compute actual_duration_hours. Returns (ts, hours)."""
    manifest = _find_manifest(arch_root, block_id)
    if not manifest:
        return "", 0.0
    ts = _now_iso()
    text = manifest.read_text(encoding="utf-8", errors="replace")

    started_str = _read_yaml_field(text, "started_at")
    paused_dur_str = _read_yaml_field(text, "paused_duration_hours")

    started = _parse_iso(started_str)
    if started:
        total_h = (datetime.now(timezone.utc) - started).total_seconds() / 3600
        try:
            paused_h = float(paused_dur_str) if paused_dur_str and paused_dur_str not in ("~", "") else 0.0
        except ValueError:
            paused_h = 0.0
        actual_h = round(max(0.0, total_h - paused_h), 2)
    else:
        actual_h = 0.0

    text = _set_yaml_field(text, "finished_at", ts)
    text = _set_yaml_field(text, "actual_duration_hours", str(actual_h))
    manifest.write_text(text, encoding="utf-8")
    return ts, actual_h


def get_status(arch_root: Path, block_id: str) -> str:
    """Return current timer status for a block."""
    manifest = _find_manifest(arch_root, block_id)
    if not manifest:
        return f"Block {block_id}: manifest not found"
    text = manifest.read_text(encoding="utf-8", errors="replace")
    started = _read_yaml_field(text, "started_at")
    paused = _read_yaml_field(text, "paused_at")
    resumed = _read_yaml_field(text, "resumed_at")
    finished = _read_yaml_field(text, "finished_at")
    actual = _read_yaml_field(text, "actual_duration_hours")
    return (
        f"Block {block_id}:\n"
        f"  started_at: {started or 'not set'}\n"
        f"  paused_at:  {paused or 'not set'}\n"
        f"  resumed_at: {resumed or 'not set'}\n"
        f"  finished_at: {finished or 'not set'}\n"
        f"  actual_duration_hours: {actual or 'not computed'}"
    )


# ---------------------------------------------------------------------------
# Phase timestamps
# ---------------------------------------------------------------------------

def stamp_phase_started(arch_root: Path, phase_id: str) -> str:
    """Write phase_started_at to phase file. Called by phase_manager.start_phase."""
    phase_file = arch_root / "phases" / f"{phase_id}.md"
    if not phase_file.exists():
        return ""
    ts = _now_iso()
    text = phase_file.read_text(encoding="utf-8", errors="replace")
    text = _set_yaml_field(text, "phase_started_at", ts)
    phase_file.write_text(text, encoding="utf-8")
    return ts


def stamp_phase_finished(arch_root: Path, phase_id: str) -> tuple[str, float]:
    """Write phase_finished_at, compute phase_duration_hours."""
    phase_file = arch_root / "phases" / f"{phase_id}.md"
    if not phase_file.exists():
        return "", 0.0
    ts = _now_iso()
    text = phase_file.read_text(encoding="utf-8", errors="replace")

    started_str = _read_yaml_field(text, "phase_started_at")
    started = _parse_iso(started_str)
    hours = 0.0
    if started:
        hours = round((datetime.now(timezone.utc) - started).total_seconds() / 3600, 2)

    text = _set_yaml_field(text, "phase_finished_at", ts)
    text = _set_yaml_field(text, "phase_duration_hours", str(hours))
    phase_file.write_text(text, encoding="utf-8")
    return ts, hours


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="velocity_tracker",
                                description="Track real time for blocks and phases.")
    p.add_argument("--block-id", help="Block ID")
    p.add_argument("--arch-root", default=".", help="Cognitive-arch root")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--start", action="store_true", help="Stamp started_at")
    g.add_argument("--pause", action="store_true", help="Stamp paused_at")
    g.add_argument("--resume", action="store_true", help="Stamp resumed_at")
    g.add_argument("--finish", action="store_true", help="Stamp finished_at and compute hours")
    g.add_argument("--status", action="store_true", help="Show current timer status")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()

    if not args.block_id:
        print("ERROR: --block-id required")
        return 1

    if args.start:
        ts = stamp_started(arch_root, args.block_id)
        print(f"started_at: {ts}")
    elif args.pause:
        msg = pause_timer(arch_root, args.block_id)
        print(msg)
    elif args.resume:
        msg = resume_timer(arch_root, args.block_id)
        print(msg)
    elif args.finish:
        ts, hours = stamp_finished(arch_root, args.block_id)
        print(f"finished_at: {ts} | actual_duration_hours: {hours}")
    elif args.status:
        print(get_status(arch_root, args.block_id))
    else:
        print("ERROR: specify --start, --pause, --resume, --finish, or --status")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
