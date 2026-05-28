# PURPOSE: Assemble Governor v2 task packets from a manifest + Governor metadata
# INPUTS:  manifest path (YAML frontmatter), Governor session ID, timestamp,
#          ARCH_ROOT path, optional scope override
# OUTPUTS: task packet string (header + convention snippet + manifest content)
# DEPS:    sdk/convention_snippet, pyyaml>=6.0, stdlib (pathlib, datetime, re)
# SEE:     protocols/task-packet.md, templates/task-packet.md,
#          design/governor-v2.md §4, sdk/convention_snippet.py

"""
Task packet builder.

Parses a manifest file's YAML frontmatter, generates the axiom convention snippet,
and assembles the full task packet string ready to send as a sub-agent's first message.

Usage (module):
    from sdk.task_packet import build_packet
    packet = build_packet(
        manifest_path="manifests/block-031-task-packet-module.md",
        arch_root=Path("cognitive-arch"),
        gov_id="g-001",
    )

Usage (CLI test):
    python sdk/task_packet.py --test
    python sdk/task_packet.py --manifest manifests/block-031-task-packet-module.md
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

# Convention snippet lives in the same sdk/ directory — add it to path explicitly
_SDK_DIR = Path(__file__).resolve().parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))
from convention_snippet import build_snippet  # noqa: E402

# ---------------------------------------------------------------------------
# Scope mode mapping (design/governor-v2.md §4)
# ---------------------------------------------------------------------------

_SCOPE_MAP: dict[str, str] = {
    "doc-only":       "closed",
    "doc":            "closed",
    "refactor":       "open",
    "enhancement":    "open",
    "implementation": "open",     # complex blocks use two-phase; Governor decides
    "feature":        "open",
    "bugfix":         "open",
    "gate":           "closed",
    "discovery":      "closed",
    "small-fix":      "open",
}


# ---------------------------------------------------------------------------
# Manifest parsing
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> dict:
    """Extract and parse YAML frontmatter from a markdown file."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise ValueError("No YAML frontmatter found (expected --- delimiters at file start)")
    return yaml.safe_load(match.group(1)) or {}


def _paths_from_manifest(fm: dict) -> tuple[list[str], list[str]]:
    """
    Return (fread_paths, fmod_paths) from frontmatter.
    fmod = files.modify + files.create (both are sub-agent write targets).
    """
    files = fm.get("files", {}) or {}
    fread = [p for p in (files.get("read") or []) if p]
    fmod  = [p for p in (files.get("modify") or []) + (files.get("create") or []) if p]
    return fread, fmod


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_CONTENT_LINES = 30  # Number of lines to include per fread file


def build_packet(
    manifest_path: str,
    arch_root: Path,
    gov_id: str = "g-001",
    ts: Optional[str] = None,
    scope_override: Optional[str] = None,
    axiom_override: Optional[list[str]] = None,
    sid: Optional[str] = None,
    include_content: bool = False,
) -> str:
    """
    Assemble a complete task packet string.

    Args:
        manifest_path:   Path to manifest file, relative to arch_root.
        arch_root:       Path to cognitive-arch/ directory.
        gov_id:          Governor session ID (e.g. "g-001").
        ts:              ISO 8601 dispatch timestamp. Defaults to now (UTC).
        scope_override:  Force a specific scope mode ("closed"/"open"/"two-phase").
        axiom_override:  If given, replaces computed axiom list.
        sid:             SDK sub-agent session ID (optional).
        include_content: When True, append first 30 lines of each fread file under
                         a '--- file content ---' section. Missing files are noted
                         as '# (not found: path)' and skipped gracefully.

    Returns:
        Full task packet string ready to send as sub-agent's first message.
    """
    manifest_full = arch_root / manifest_path
    if not manifest_full.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_full}")

    manifest_content = manifest_full.read_text(encoding="utf-8")
    fm = _parse_frontmatter(manifest_content)

    block_id  = str(fm.get("id", "???")).replace("block-", "")
    kind      = str(fm.get("kind", "implementation")).lower()
    phase     = str(fm.get("phase", "phase-?"))
    fread, fmod = _paths_from_manifest(fm)

    # Determine scope
    scope = scope_override or _SCOPE_MAP.get(kind, "open")

    # Convention snippet
    modifies_code = any(
        p.endswith((".py", ".ts", ".js", ".rs", ".go", ".sh")) for p in fmod
    )
    axioms_str, snippet_body = build_snippet(
        kind,
        modifies_code=modifies_code,
        axiom_override=axiom_override,
    )

    # Timestamp
    if ts is None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    # Build header
    fread_str = ",".join(fread) if fread else "-"
    fmod_str  = ",".join(fmod) if fmod else "-"

    header_lines = [
        f"b:{block_id} kind:{kind} phase:{phase} gov:{gov_id} ts:{ts}",
        f"axioms:{axioms_str} scope:{scope} retro_req:yes tok_track:yes",
        f"fread:{fread_str} fmod:{fmod_str}",
    ]
    if sid:
        header_lines.append(f"sid:{sid}")

    # Assemble packet
    parts = [
        "\n".join(header_lines),
        "",
        snippet_body,
        "",
        "--- manifest ---",
        manifest_content.strip(),
    ]

    # Optionally append file content snippets for fread paths
    if include_content and fread:
        parts.append("")
        parts.append("--- file content ---")
        for fread_path in fread:
            parts.append(f"# {fread_path}")
            full_fread = arch_root / fread_path
            if full_fread.exists():
                try:
                    lines = full_fread.read_text(encoding="utf-8").splitlines()
                    parts.append("\n".join(lines[:_CONTENT_LINES]))
                except Exception:
                    parts.append(f"# (unreadable: {fread_path})")
            else:
                parts.append(f"# (not found: {fread_path})")
            parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _find_arch_root() -> Path:
    """Locate cognitive-arch/ relative to this file's location."""
    return Path(__file__).resolve().parent.parent


def _cli_test() -> int:
    """Self-test: build a packet from this block's own manifest."""
    arch_root = _find_arch_root()
    manifest_path = "manifests/block-031-task-packet-module.md"

    manifest_full = arch_root / manifest_path
    if not manifest_full.exists():
        print(f"SKIP: test manifest not found at {manifest_full}", file=sys.stderr)
        print("  (run from the Arquitetura Cognitiva parent directory)")
        # Use a minimal inline manifest for testing
        return _cli_test_inline(arch_root)

    try:
        packet = build_packet(manifest_path, arch_root, gov_id="g-test", ts="2026-05-22T12:00Z")
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    required_fields = ["b:", "kind:", "phase:", "gov:", "ts:", "axioms:", "scope:",
                       "retro_req:", "tok_track:", "fread:", "fmod:"]
    errors = []
    for field in required_fields:
        if field not in packet:
            errors.append(f"FAIL: required field '{field}' not found in packet")
    if "--- convention snippet ---" not in packet:
        errors.append("FAIL: '--- convention snippet ---' delimiter missing")
    if "--- manifest ---" not in packet:
        errors.append("FAIL: '--- manifest ---' delimiter missing")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print("task_packet --test: PASS")
    print(f"  Packet length : {len(packet)} chars")
    print(f"  Header lines  : 3")
    print(f"  Has snippet   : yes")
    print(f"  Has manifest  : yes")
    return 0


def _cli_test_inline(arch_root: Path) -> int:
    """Fallback test using an in-memory minimal manifest (no file I/O)."""
    import tempfile, os

    minimal_manifest = """\
---
id: block-031
tier: M
kind: feature
phase: phase-5
status: wip
files:
  read:
    - protocols/task-packet.md
  modify: []
  create:
    - sdk/task_packet.py
gates: []
created_at: 2026-05-22
---

# Block 031 — Module: task packet builder (inline test manifest)
"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(minimal_manifest)
        tmp_path = f.name

    try:
        # Build relative to a temp arch_root that contains manifests/
        import shutil
        tmp_arch = Path(tempfile.mkdtemp())
        (tmp_arch / "manifests").mkdir()
        tmp_manifest_rel = "manifests/block-031-test.md"
        shutil.copy(tmp_path, tmp_arch / tmp_manifest_rel)

        packet = build_packet(tmp_manifest_rel, tmp_arch, gov_id="g-test", ts="2026-05-22T12:00Z")
    except Exception as exc:
        print(f"FAIL (inline): {exc}", file=sys.stderr)
        return 1
    finally:
        os.unlink(tmp_path)

    required_fields = ["b:", "kind:", "axioms:", "scope:", "--- convention snippet ---", "--- manifest ---"]
    errors = [f"FAIL: '{f}' missing" for f in required_fields if f not in packet]
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print("task_packet --test: PASS (inline manifest)")
    print(f"  Packet length : {len(packet)} chars")
    return 0


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="task_packet",
        description="Build Governor v2 task packets from manifest files.",
    )
    parser.add_argument("--test", action="store_true", help="Run self-test.")
    parser.add_argument("--manifest", metavar="PATH", help="Manifest path (relative to cognitive-arch/).")
    parser.add_argument("--gov-id", default="g-001", help="Governor session ID (default: g-001).")

    args = parser.parse_args()

    if args.test:
        sys.exit(_cli_test())
    elif args.manifest:
        arch_root = _find_arch_root()
        try:
            packet = build_packet(args.manifest, arch_root, gov_id=args.gov_id)
            print(packet)
            sys.exit(0)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
