# sdk/state_manager.py
# PURPOSE: Read and update STATE.md and NEXT.md without AI manual editing.
#          Prevents corruption, saves ~1500 tokens per state operation.
# INPUTS:  STATE.md, NEXT.md (key:value compact format per _syntax.md)
# OUTPUTS: Updated STATE.md / NEXT.md in place
# DEPS:    stdlib only (pathlib, re, datetime)
# USAGE:   python sdk/state_manager.py --set-state "last_block:block-112 status:active"
#          python sdk/state_manager.py --set-next "next_action:block-113 phase:phase-18"
#          python sdk/state_manager.py --read-state
# SEE:     _syntax.md, commands/block-close.md

from __future__ import annotations

import argparse
import io
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

def _fix_utf8():
    """Apply UTF-8 stdout fix on Windows — safe to call multiple times."""
    import io as _io
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'buffer') and not (
            isinstance(sys.stdout, _io.TextIOWrapper) and sys.stdout.encoding.lower() == 'utf-8'
        ):
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_fix_utf8()

_STATE_FILE = "STATE.md"
_NEXT_FILE = "NEXT.md"
_COMMENT_PREFIX = "#"


# ---------------------------------------------------------------------------
# Parse / serialize
# ---------------------------------------------------------------------------

def _parse_kv_line(line: str) -> dict[str, str]:
    """Parse a compact key:value line into a dict. Ignores comment lines."""
    result: dict[str, str] = {}
    if line.strip().startswith(_COMMENT_PREFIX):
        return result
    # Match key:value pairs — value ends at next key or end of string
    for m in re.finditer(r"(\w+):([^\s]+)", line):
        result[m.group(1)] = m.group(2)
    return result


def _serialize_kv(data: dict[str, str]) -> str:
    """Serialize dict back to compact key:value string."""
    return " ".join(f"{k}:{v}" for k, v in data.items())


def _read_file(path: Path) -> tuple[list[str], list[str]]:
    """Return (comment_lines, data_lines) from file."""
    if not path.exists():
        return [], []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    comments = [l for l in lines if l.strip().startswith(_COMMENT_PREFIX) or l.strip() == ""]
    data = [l for l in lines if l.strip() and not l.strip().startswith(_COMMENT_PREFIX)]
    return comments, data


def read_state(arch_root: Path) -> dict[str, str]:
    """Return STATE.md as a flat dict."""
    _, data = _read_file(arch_root / _STATE_FILE)
    result: dict[str, str] = {}
    for line in data:
        result.update(_parse_kv_line(line))
    return result


def read_next(arch_root: Path) -> dict[str, str]:
    """Return NEXT.md as a flat dict."""
    _, data = _read_file(arch_root / _NEXT_FILE)
    result: dict[str, str] = {}
    for line in data:
        result.update(_parse_kv_line(line))
    return result


def _update_file(path: Path, updates: dict[str, str], header_comment: str) -> None:
    """Merge updates into file, preserving comment header, updating last_updated."""
    comments, data = _read_file(path)

    # Merge all existing data into one dict
    current: dict[str, str] = {}
    for line in data:
        current.update(_parse_kv_line(line))

    # Apply updates
    current.update(updates)

    # Auto-set last_updated
    current["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Write back: header comment + single data line
    out_lines = []
    if comments:
        out_lines.extend(comments)
    else:
        out_lines.append(header_comment)
    out_lines.append("")
    out_lines.append(_serialize_kv(current))
    out_lines.append("")

    path.write_text("\n".join(out_lines), encoding="utf-8")


def update_state(arch_root: Path, updates: dict[str, str]) -> None:
    """Update STATE.md with given key-value pairs."""
    _update_file(
        arch_root / _STATE_FILE,
        updates,
        "# STATE — AI-only",
    )


def update_next(arch_root: Path, updates: dict[str, str]) -> None:
    """Update NEXT.md with given key-value pairs."""
    _update_file(
        arch_root / _NEXT_FILE,
        updates,
        "# NEXT — AI-only",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_kv_args(args_str: str) -> dict[str, str]:
    """Parse 'key1:val1 key2:val2' string into dict."""
    result = {}
    for m in re.finditer(r"(\w+):([^\s]+)", args_str):
        result[m.group(1)] = m.group(2)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="STATE.md / NEXT.md manager")
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--set-state", metavar="KV", help="Update STATE.md: 'key1:val1 key2:val2'")
    parser.add_argument("--set-next", metavar="KV", help="Update NEXT.md: 'key1:val1 key2:val2'")
    parser.add_argument("--read-state", action="store_true", help="Print STATE.md as key:value")
    parser.add_argument("--read-next", action="store_true", help="Print NEXT.md as key:value")
    args = parser.parse_args()

    root = Path(args.arch_root).resolve()

    if args.set_state:
        update_state(root, _parse_kv_args(args.set_state))
        print(f"STATE.md updated: {args.set_state}")

    if args.set_next:
        update_next(root, _parse_kv_args(args.set_next))
        print(f"NEXT.md updated: {args.set_next}")

    if args.read_state:
        state = read_state(root)
        for k, v in state.items():
            print(f"  {k}: {v}")

    if args.read_next:
        nxt = read_next(root)
        for k, v in nxt.items():
            print(f"  {k}: {v}")
