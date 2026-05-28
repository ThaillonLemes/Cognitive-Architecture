# sdk/velocity_inference.py
# Infers block implementation duration from git commit timestamps.
# Callers: block-close prompt, audit check 9, health report generator.
# Returns (hours: float, source: str) where source is 'auto-inferred' or 'estimated'.

from __future__ import annotations

import subprocess
import re
from pathlib import Path
from typing import Optional


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


def _files_from_manifest(manifest_path: Path) -> list[str]:
    """Extract files.modify and files.create paths from a manifest YAML frontmatter."""
    if not manifest_path.exists():
        return []
    text = manifest_path.read_text(encoding="utf-8")
    # Collect lines after 'modify:' or 'create:' until next key
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
    if not manifest_path.exists():
        return "M"
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^tier:\s*([SML])", line)
        if m:
            return m.group(1)
    return "M"


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

    # Locate manifest
    manifests_dir = arch_root / "manifests"
    candidates = list(manifests_dir.glob(f"{block_id}-*.md"))
    manifest_path = candidates[0] if candidates else Path("")

    files = _files_from_manifest(manifest_path)
    timestamps = _git_timestamps_for_files(files, arch_root)

    if len(timestamps) >= 2:
        spread_seconds = max(timestamps) - min(timestamps)
        hours = round(spread_seconds / 3600, 2)
        # Cap at 24h; anything beyond is likely a multi-day gap, not active time
        if 0 < hours <= 24:
            return hours, "auto-inferred"

    # Fallback: tier-based estimate
    tier = _tier_from_manifest(manifest_path)
    return TIER_ESTIMATES.get(tier, 3.0), "estimated"


if __name__ == "__main__":
    import sys

    block = sys.argv[1] if len(sys.argv) > 1 else "block-086"
    hours, source = infer_duration(block)
    print(f"{block}: {hours}h ({source})")
