# sdk/restore_canonical.py
# PURPOSE: Restore a file to its canonical (HEAD) version with backup and confirmation.
# INPUTS:  relative file path, arch root
# OUTPUTS: backup at _backups/, diff display, writes canonical on RESTORE confirmation
# DEPS:    stdlib only (pathlib, subprocess, datetime, sys, argparse)
# SEE:     commands/restore.md, protocols/architecture-integrity.md

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _git_show_head(rel_path: str, arch_root: Path) -> str | None:
    """Return file content from HEAD, or None if not in git history."""
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=str(arch_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception:
        return None


def _backup(file_path: Path, arch_root: Path) -> Path:
    """Copy current file to _backups/<name>-<ISO-timestamp>.<ext>. Returns backup path."""
    backups_dir = arch_root / "_backups"
    backups_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = file_path.stem
    suffix = file_path.suffix
    backup_path = backups_dir / f"{stem}-{ts}{suffix}"
    backup_path.write_bytes(file_path.read_bytes())
    return backup_path


def _simple_diff(original: str, canonical: str, filename: str) -> str:
    """Return a compact unified-style diff (no external diff tool needed)."""
    orig_lines = original.splitlines(keepends=True)
    canon_lines = canonical.splitlines(keepends=True)
    if orig_lines == canon_lines:
        return f"(no diff — {filename} is already canonical)"
    lines = []
    lines.append(f"--- current/{filename}")
    lines.append(f"+++ canonical/{filename}")
    # Simple line-by-line diff (not full unified diff, but readable)
    max_context = 40
    shown = 0
    for i, (a, b) in enumerate(zip(orig_lines, canon_lines)):
        if a != b:
            lines.append(f"@@ line {i+1} @@")
            lines.append(f"- {a.rstrip()}")
            lines.append(f"+ {b.rstrip()}")
            shown += 1
            if shown >= max_context:
                lines.append(f"... ({len(orig_lines)} lines total; showing first {max_context} diffs)")
                break
    if len(orig_lines) != len(canon_lines):
        lines.append(f"(line count differs: current={len(orig_lines)}, canonical={len(canon_lines)})")
    return "\n".join(lines)


def restore(rel_path: str, arch_root: Path, yes: bool = False) -> int:
    """
    Restore rel_path to its HEAD canonical version.

    Returns exit code: 0=restored, 1=cancelled/error.
    """
    file_path = arch_root / rel_path
    if not file_path.exists():
        print(f"ERROR: {rel_path} does not exist in working directory.")
        return 1

    canonical = _git_show_head(rel_path, arch_root)
    if canonical is None:
        print(f"ERROR: {rel_path} not found in git HEAD. Cannot restore.")
        return 1

    # Step 1: backup
    backup_path = _backup(file_path, arch_root)
    print(f"Backup created: {backup_path.relative_to(arch_root)}")

    # Step 2: show diff
    current = file_path.read_text(encoding="utf-8", errors="replace")
    diff = _simple_diff(current, canonical, rel_path)
    print(f"\n--- DIFF ---\n{diff}\n--- END DIFF ---\n")

    if current == canonical:
        print(f"{rel_path} is already canonical. No changes needed.")
        return 0

    # Step 3: confirmation
    if not yes:
        print(f"To restore, type exactly: RESTORE {rel_path}")
        print("Any other input cancels.")
        try:
            confirm = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            confirm = ""
        if confirm != f"RESTORE {rel_path}":
            print("Restore cancelled. Backup retained.")
            return 1

    # Step 4: write canonical
    file_path.write_text(canonical, encoding="utf-8")
    print(f"Restored: {rel_path}")
    print(f"Note: run 'integrity-bump' if this file is in .integrity.lock.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore a file to its canonical HEAD version")
    parser.add_argument("file", help="Relative path to file (from arch-root)")
    parser.add_argument("--arch-root", default=".", help="Root of the cognitive-arch directory")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt (use in scripts)")
    args = parser.parse_args()

    arch_root = Path(args.arch_root).resolve()
    sys.exit(restore(args.file, arch_root, yes=args.yes))
