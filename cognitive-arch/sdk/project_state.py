# PURPOSE: Single source of truth for "where are we" — current phase, completed blocks, counts.
#          Every tool should read project state through here instead of re-parsing files its own way.
# INPUTS:  STATE.md (p:N field), blocks/BLOCK_LOG.md, phases/phase-N.md
# OUTPUTS: current phase number/name, completed block id list, block count, current phase file
# DEPS:    stdlib only (re, pathlib)
# SEE:     phases/phase-23.md block-137, sdk/health_report.py

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def _read(arch_root: Path, rel: str) -> str:
    p = arch_root / rel
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def current_phase(arch_root: Path) -> Optional[int]:
    """Current phase number from STATE.md `p:N`. Returns None if unknown.

    STATE.md is the canonical record of the active phase — NOT the set of phase
    files on disk (those include future/planned phases and lexical-sort traps).
    """
    m = re.search(r"\bp:(\d+)\b", _read(arch_root, "STATE.md"))
    return int(m.group(1)) if m else None


def current_phase_name(arch_root: Path) -> str:
    n = current_phase(arch_root)
    return f"phase-{n}" if n is not None else "phase-?"


def completed_block_ids(arch_root: Path) -> list[str]:
    """Unique completed block IDs from BLOCK_LOG.md, in first-seen order.

    Matches lines like `block-042 done 2026-... | tier:M`. Deduplicates so a
    block logged twice is counted once.
    """
    seen: set[str] = set()
    out: list[str] = []
    for line in _read(arch_root, "blocks/BLOCK_LOG.md").splitlines():
        s = line.strip()
        m = re.match(r"(block-\d+)\b", s)
        if m and "done" in s.lower():
            bid = m.group(1)
            if bid not in seen:
                seen.add(bid)
                out.append(bid)
    return out


def block_count(arch_root: Path) -> int:
    """Number of unique completed blocks."""
    return len(completed_block_ids(arch_root))


def phase_files(arch_root: Path) -> list[Path]:
    """Phase definition files (phase-N.md, excluding -retro), sorted NUMERICALLY.

    `sorted(glob('phase-[0-9]*.md'))` sorts lexically — 'phase-9' > 'phase-22' —
    which is the bug this function exists to prevent.
    """
    pdir = arch_root / "phases"
    if not pdir.exists():
        return []
    files = [p for p in pdir.glob("phase-[0-9]*.md")
             if re.fullmatch(r"phase-\d+", p.stem)]
    return sorted(files, key=lambda p: int(re.match(r"phase-(\d+)", p.stem).group(1)))


def current_phase_file(arch_root: Path) -> Optional[Path]:
    """The phase file for STATE's current phase; falls back to the highest-numbered."""
    files = phase_files(arch_root)
    if not files:
        return None
    n = current_phase(arch_root)
    if n is not None:
        for f in files:
            if f.stem == f"phase-{n}":
                return f
    return files[-1]  # numerically highest, never lexically-last
