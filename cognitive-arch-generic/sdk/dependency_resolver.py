# cognitive-arch / sdk/dependency_resolver.py
# purpose: Dependency resolution automation (D7).
#   Finds blocks whose dependencies are now satisfied in BLOCK_LOG.
#   Pure function; board.md update is performed by Master Agent on notification.
# stdlib-only; no external dependencies

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

BLOCK_LOG_PATH = "blocks/BLOCK_LOG.md"
MANIFESTS_DIR = "manifests"

# Frontmatter fields we care about
_RE_ID = re.compile(r"^id:\s*(\S+)", re.MULTILINE)
_RE_STATUS = re.compile(r"^status:\s*(\S+)", re.MULTILINE)
_RE_DEPS = re.compile(r"^dependencies:\s*\[([^\]]*)\]", re.MULTILINE)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ManifestEntry:
    block_id: str
    status: str            # "pending" | "planned" | "done" | "wip" etc.
    dependencies: list[str] = field(default_factory=list)


@dataclass
class UnblockedBlock:
    block_id: str
    deps_satisfied: list[str]  # all deps that were satisfied to trigger unblock


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _arch_path(arch_root: Optional[str]) -> Path:
    return Path(arch_root) if arch_root is not None else Path.cwd()


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _extract_frontmatter(content: str) -> str:
    """Extract YAML frontmatter block (between --- delimiters)."""
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    return m.group(1) if m else ""


def _parse_deps(dep_str: str) -> list[str]:
    """
    Parse a YAML list string like "block-095, block-100" or "block-098".
    Returns empty list for empty or whitespace-only strings.
    """
    dep_str = dep_str.strip()
    if not dep_str:
        return []
    # Strip quotes, split on commas
    parts = [p.strip().strip('"').strip("'") for p in dep_str.split(",")]
    return [p for p in parts if p]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_done_blocks(log_content: str) -> set[str]:
    """
    Parse BLOCK_LOG content and return the set of block IDs with 'done' event.
    Format: block-NNN done - YYYY-MM-DD
    """
    done: set[str] = set()
    for line in log_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "done":
            done.add(parts[0])
    return done


def read_manifests(
    arch_root: Optional[str] = None,
    manifest_contents: Optional[list[str]] = None,
) -> list[ManifestEntry]:
    """
    Read all manifests and extract (id, status, dependencies).
    manifest_contents is injectable for testing (list of file content strings).
    """
    if manifest_contents is not None:
        contents = manifest_contents
    else:
        root = _arch_path(arch_root)
        mdir = root / MANIFESTS_DIR
        contents = []
        if mdir.is_dir():
            for path in mdir.glob("block-*.md"):
                contents.append(path.read_text(encoding="utf-8"))

    entries = []
    for content in contents:
        fm = _extract_frontmatter(content)
        if not fm:
            continue
        m_id = _RE_ID.search(fm)
        m_status = _RE_STATUS.search(fm)
        m_deps = _RE_DEPS.search(fm)
        if not m_id:
            continue
        block_id = m_id.group(1)
        status = m_status.group(1) if m_status else "unknown"
        deps = _parse_deps(m_deps.group(1)) if m_deps else []
        entries.append(ManifestEntry(block_id=block_id, status=status, dependencies=deps))

    return entries


def find_unblocked(
    done_blocks: set[str],
    manifests: list[ManifestEntry],
) -> list[UnblockedBlock]:
    """
    Return blocks whose dependencies are all satisfied (all deps in done_blocks).
    Only considers blocks with status 'pending' or 'planned' (not done/wip).
    """
    unblocked = []
    active_statuses = {"pending", "planned", "wait"}
    for entry in manifests:
        if entry.status.lower() not in active_statuses:
            continue
        if not entry.dependencies:
            continue  # no deps → already unblocked by default
        if all(dep in done_blocks for dep in entry.dependencies):
            unblocked.append(UnblockedBlock(
                block_id=entry.block_id,
                deps_satisfied=list(entry.dependencies),
            ))
    return unblocked


def build_notifications(unblocked: list[UnblockedBlock]) -> list[dict]:
    """
    Build AgentMessage notification dicts (kind: notification) for each unblocked block.
    Compatible with sdk/agent_message_schema.py schema.
    """
    now_ts = datetime.now(timezone.utc).isoformat()
    messages = []
    for ub in unblocked:
        messages.append({
            "schema_version": "1.0",
            "from": "master",
            "to": "implementer",
            "kind": "notification",
            "sent_at": now_ts,
            "payload": {
                "event": "dep_unblocked",
                "data": {
                    "block_id": ub.block_id,
                    "deps_satisfied": ub.deps_satisfied,
                },
            },
            "expects_response": False,
        })
    return messages


def run_resolver(
    arch_root: Optional[str] = None,
    log_content: Optional[str] = None,
    manifest_contents: Optional[list[str]] = None,
) -> list[UnblockedBlock]:
    """
    Main entry point: read BLOCK_LOG + manifests, return list of newly-unblocked blocks.

    Parameters
    ----------
    arch_root : str, optional
        Root of cognitive-arch project (for filesystem reads).
    log_content : str, optional
        BLOCK_LOG content string (injectable for testing).
    manifest_contents : list[str], optional
        List of manifest file content strings (injectable for testing).

    Returns
    -------
    list[UnblockedBlock]
        Blocks whose dependencies are now all satisfied. Empty list if none.
    """
    if log_content is None:
        root = _arch_path(arch_root)
        log_content = _read_file(root / BLOCK_LOG_PATH)

    done_blocks = find_done_blocks(log_content)
    manifests = read_manifests(arch_root=arch_root, manifest_contents=manifest_contents)
    return find_unblocked(done_blocks, manifests)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Dependency resolver")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--notify", action="store_true", help="Print notification messages")
    args = parser.parse_args()

    results = run_resolver(arch_root=args.arch_root)
    if not results:
        print("No newly-unblocked blocks.")
        sys.exit(0)

    for ub in results:
        deps_str = ", ".join(ub.deps_satisfied)
        print(f"UNBLOCKED: {ub.block_id}  (deps satisfied: {deps_str})")

    if args.notify:
        import json
        msgs = build_notifications(results)
        for msg in msgs:
            print(json.dumps(msg, indent=2))
