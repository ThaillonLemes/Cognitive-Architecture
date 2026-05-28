# PURPOSE: Python helper for audit.sh checks 7+8 (fmod conflict + drift detection)
# INPUTS:  manifests/block-*.md (YAML frontmatter), blocks/BLOCK_LOG.md, blocks/ dir
# OUTPUTS: OK/WARN/ERROR lines to stdout; exit code 0 (clean) or 1 (issues found)
# DEPS:    stdlib only (pathlib, re, argparse, sys)
# SEE:     manifests/block-057-audit-checks-78.md, audit.sh, commands/audit.md

"""
Audit helper functions for cognitive-arch audit.sh.

Provides two script-runnable checks:
  --check conflicts   Check 7: fmod path conflicts across planned manifests
  --check drift       Check 8: BLOCK_LOG done entries with no retrospective file

Called by audit.sh; prints OK:/WARN:/ERROR: prefixed lines; exits 0 (clean) or 1 (issues).
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Check 7 — File-conflict detection
# ---------------------------------------------------------------------------

def _load_done_blocks(arch_root: Path) -> set[str]:
    """Return set of block IDs (e.g. 'block-051') that appear as done in BLOCK_LOG."""
    log_path = arch_root / "blocks" / "BLOCK_LOG.md"
    if not log_path.exists():
        return set()
    content = log_path.read_text(encoding="utf-8")
    return {m.group(1) for m in re.finditer(r"^(block-\d+)\s+done", content, re.MULTILINE)}


def check_conflicts(arch_root: Path) -> int:
    """
    Scan pending (not yet done) manifests for files.modify paths claimed by more than one block.

    A block is considered pending if its ID does NOT appear in blocks/BLOCK_LOG.md as done.
    Done blocks are excluded: they already ran and cannot conflict with future work.

    Returns the number of conflicts found (0 = clean).
    """
    manifests_dir = arch_root / "manifests"
    if not manifests_dir.exists():
        print("OK: file-conflict [7]: no manifests/ directory found (skipped)")
        return 0

    # Load completed block IDs — these are excluded from conflict checking
    done_blocks = _load_done_blocks(arch_root)

    # Map: path → list of block IDs that claim it as files.modify (pending only)
    claimed: dict[str, list[str]] = {}

    for manifest_path in sorted(manifests_dir.glob("block-*.md")):
        content = manifest_path.read_text(encoding="utf-8")

        # Get block ID from frontmatter
        id_match = re.search(r"^id:\s*(\S+)", content, re.MULTILINE)
        block_id = id_match.group(1) if id_match else manifest_path.stem

        # Skip already-done blocks — they can't conflict with pending work
        if block_id in done_blocks:
            continue

        # Extract YAML frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        fm_text = fm_match.group(1)

        # Parse files.modify entries (indent-aware)
        in_files = False
        in_modify = False
        for line in fm_text.splitlines():
            if re.match(r"^files:", line):
                in_files = True
                in_modify = False
                continue
            if in_files and re.match(r"^[a-z]", line):
                # Top-level key — exit files section
                in_files = False
                in_modify = False
                continue
            if in_files and re.match(r"\s+modify:", line):
                in_modify = True
                continue
            if in_files and in_modify:
                if re.match(r"\s+\w+:", line):
                    # New sub-key inside files: — exit modify
                    in_modify = False
                    continue
                item_match = re.match(r"\s+-\s+(.+)", line)
                if item_match:
                    path = item_match.group(1).strip()
                    if path and path not in ("-", "[]"):
                        claimed.setdefault(path, []).append(block_id)

    conflicts = {p: bids for p, bids in claimed.items() if len(bids) > 1}

    if not conflicts:
        print("OK: file-conflict [7]: no planned-manifest fmod conflicts detected")
        return 0

    for path, bids in sorted(conflicts.items()):
        print(f"WARN: file-conflict [7]: '{path}' claimed by {', '.join(sorted(bids))}")
    return len(conflicts)


# ---------------------------------------------------------------------------
# Check 8 — Drift detection
# ---------------------------------------------------------------------------

def check_drift(arch_root: Path) -> int:
    """
    Compare BLOCK_LOG.md 'done' entries against retrospective files in blocks/.

    Returns the number of missing retrospectives (0 = clean).
    """
    log_path = arch_root / "blocks" / "BLOCK_LOG.md"
    blocks_dir = arch_root / "blocks"

    if not log_path.exists():
        print("OK: drift [8]: blocks/BLOCK_LOG.md not found (skipped)")
        return 0

    log_content = log_path.read_text(encoding="utf-8")
    drift_count = 0

    for match in re.finditer(r"^(block-\d+)\s+done", log_content, re.MULTILINE):
        block_id = match.group(1)
        # Look for blocks/block-NNN-*.md (slug wildcard)
        retro_files = list(blocks_dir.glob(f"{block_id}-*.md"))
        if not retro_files:
            print(f"WARN: drift [8]: '{block_id}' in BLOCK_LOG but no retrospective found in blocks/")
            drift_count += 1

    if drift_count == 0:
        print("OK: drift [8]: all done blocks have retrospective files")
    return drift_count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="audit_helpers",
        description="Audit helper: checks 7 (fmod conflicts) and 8 (drift) for audit.sh.",
    )
    parser.add_argument(
        "--check",
        choices=["conflicts", "drift", "all"],
        default="all",
        help="Which check to run (default: all).",
    )
    parser.add_argument(
        "--arch-root",
        default=".",
        metavar="PATH",
        help="Path to cognitive-arch/ root directory (default: current dir).",
    )
    args = parser.parse_args()

    arch_root = Path(args.arch_root).resolve()
    issues = 0

    if args.check in ("conflicts", "all"):
        issues += check_conflicts(arch_root)
    if args.check in ("drift", "all"):
        issues += check_drift(arch_root)

    sys.exit(1 if issues > 0 else 0)


if __name__ == "__main__":
    main()
