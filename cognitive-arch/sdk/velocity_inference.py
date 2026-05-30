# PURPOSE: Infer block implementation duration from git commit timestamps; expose tier from manifest.
# INPUTS:  block_id (CLI positional) + --arch-root; reads manifests/<block_id>-*.md and git log.
# OUTPUTS: (hours: float, source: 'auto-inferred'|'estimated') ; CLI prints "<block>: <h>h (<source>)".
# DEPS:    stdlib only (subprocess, re, argparse, pathlib) + safe_io.
# SEE:     phases/phase-23.md block-138, sdk/health_report.py, blocks/block-086-velocity-activation.md

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from safe_io import force_utf8


TIER_ESTIMATES = {"S": 1.0, "M": 3.0, "L": 7.0}


def _git_timestamps_for_files(files: list[str], arch_root: Path) -> list[float]:
    """Return commit Unix timestamps for any commit touching the given files."""
    if not files:
        return []
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ct", "--"] + files,
            cwd=str(arch_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        return [float(t) for t in result.stdout.splitlines() if t.strip()]
    except Exception:
        return []


def _is_real_file(p: Optional[Path]) -> bool:
    """True iff p is a non-empty Path that points to an existing regular file.

    Guards against Path("") (which resolves to "." on Windows and turns a
    read_text() call into a PermissionError on the current directory).
    """
    if p is None:
        return False
    if str(p) in ("", "."):
        return False
    try:
        return p.is_file()
    except OSError:
        return False


def _files_from_manifest(manifest_path: Path) -> list[str]:
    """Extract files.modify and files.create paths from a manifest YAML frontmatter."""
    if not _is_real_file(manifest_path):
        return []
    text = manifest_path.read_text(encoding="utf-8")
    files: list[str] = []
    in_section = False
    for line in text.splitlines():
        if re.match(r"\s+(modify|create):", line):
            in_section = True
            continue
        if in_section:
            if re.match(r"\s+[a-z_-]+:", line) and not re.match(r"\s+-\s", line):
                in_section = False
                continue
            m = re.match(r"\s+-\s+(.+)", line)
            if m:
                files.append(m.group(1).strip())
    return files


def _tier_from_manifest(manifest_path: Path) -> str:
    """Return tier (S/M/L) from manifest frontmatter, defaulting to 'M'."""
    if not _is_real_file(manifest_path):
        return "M"
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^tier:\s*([SML])", line)
        if m:
            return m.group(1)
    return "M"


def _locate_manifest(block_id: str, arch_root: Path) -> Optional[Path]:
    """Return manifests/<block_id>-*.md if exactly one exists, else None.

    Returns None when zero or multiple matches exist (multiple matches are
    ambiguous; the caller should not silently pick one at random).
    """
    manifests_dir = arch_root / "manifests"
    if not manifests_dir.is_dir():
        return None
    candidates = sorted(manifests_dir.glob(f"{block_id}-*.md"))
    return candidates[0] if len(candidates) == 1 else None


def infer_duration(
    block_id: str,
    arch_root: Optional[Path] = None,
) -> tuple[float, str]:
    """
    Estimate active implementation hours for a block.

    Returns (hours, source) where source is:
      'auto-inferred' — derived from git commit timestamp spread for block files
      'estimated'     — tier-based fallback when git data is unavailable
    """
    if arch_root is None:
        arch_root = Path(__file__).parent.parent

    manifest_path = _locate_manifest(block_id, arch_root)

    files = _files_from_manifest(manifest_path) if manifest_path else []
    timestamps = _git_timestamps_for_files(files, arch_root)

    if len(timestamps) >= 2:
        spread_seconds = max(timestamps) - min(timestamps)
        hours = round(spread_seconds / 3600, 2)
        # Cap at 24h; anything beyond is likely a multi-day gap, not active time
        if 0 < hours <= 24:
            return hours, "auto-inferred"

    tier = _tier_from_manifest(manifest_path) if manifest_path else "M"
    return TIER_ESTIMATES.get(tier, 3.0), "estimated"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="velocity_inference",
        description="Infer a block's active implementation hours from git timestamps.",
    )
    parser.add_argument(
        "block_id",
        nargs="?",
        default="block-086",
        help="Block ID to infer (e.g. block-137). Defaults to block-086 for smoke runs.",
    )
    parser.add_argument(
        "--arch-root",
        metavar="PATH",
        default=".",
        help="Path to the cognitive-arch root directory (default: current directory).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    force_utf8()
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    hours, source = infer_duration(args.block_id, arch_root)
    print(f"{args.block_id}: {hours}h ({source})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
