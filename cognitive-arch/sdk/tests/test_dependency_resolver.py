# cognitive-arch / sdk/tests/test_dependency_resolver.py
# purpose: Unit tests for sdk/dependency_resolver.py
# stdlib-only; no external dependencies

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from dependency_resolver import (
    ManifestEntry,
    UnblockedBlock,
    find_done_blocks,
    read_manifests,
    find_unblocked,
    build_notifications,
    run_resolver,
    _parse_deps,
    _extract_frontmatter,
)

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

_SAMPLE_LOG = """
# BLOCK_LOG
block-098 done - 2026-05-27
block-099 done - 2026-05-27
block-100 done - 2026-05-27
block-102 done - 2026-05-27
"""

# Manifest with all deps satisfied (block-098 + 099 + 100 done)
_MANIFEST_UNBLOCKABLE = """---
id: block-109
tier: M
kind: implementation
status: pending
dependencies: [block-098, block-099, block-100]
---

# Block 109
"""

# Manifest with partial deps (block-111 not done)
_MANIFEST_PARTIAL = """---
id: block-110
tier: M
kind: implementation
status: pending
dependencies: [block-098, block-111]
---

# Block 110
"""

# Manifest with no dependencies
_MANIFEST_NO_DEPS = """---
id: block-103
tier: M
kind: implementation
status: pending
dependencies: []
---

# Block 103
"""

# Already-done manifest (should be excluded)
_MANIFEST_DONE = """---
id: block-001
tier: S
kind: implementation
status: done
dependencies: []
---

# Block 001
"""


# ---------------------------------------------------------------------------
# Tests: find_done_blocks
# ---------------------------------------------------------------------------

def test_find_done_blocks_returns_correct_set():
    done = find_done_blocks(_SAMPLE_LOG)
    assert "block-098" in done
    assert "block-099" in done
    assert "block-100" in done


def test_find_done_blocks_ignores_comments():
    log = "# header\nblock-001 done - 2026-05-20\n"
    done = find_done_blocks(log)
    assert "block-001" in done


def test_find_done_blocks_empty_log():
    assert find_done_blocks("") == set()


def test_find_done_blocks_non_done_event_excluded():
    log = "block-001 integrated - 2026-05-20\nblock-002 done - 2026-05-20\n"
    done = find_done_blocks(log)
    assert "block-001" not in done
    assert "block-002" in done


# ---------------------------------------------------------------------------
# Tests: _parse_deps
# ---------------------------------------------------------------------------

def test_parse_deps_single():
    assert _parse_deps("block-098") == ["block-098"]


def test_parse_deps_multiple():
    result = _parse_deps("block-098, block-099, block-100")
    assert "block-098" in result
    assert len(result) == 3


def test_parse_deps_empty():
    assert _parse_deps("") == []
    assert _parse_deps("  ") == []


# ---------------------------------------------------------------------------
# Tests: read_manifests
# ---------------------------------------------------------------------------

def test_read_manifests_extracts_id():
    entries = read_manifests(manifest_contents=[_MANIFEST_UNBLOCKABLE])
    assert any(e.block_id == "block-109" for e in entries)


def test_read_manifests_extracts_dependencies():
    entries = read_manifests(manifest_contents=[_MANIFEST_UNBLOCKABLE])
    entry = next(e for e in entries if e.block_id == "block-109")
    assert "block-098" in entry.dependencies
    assert "block-099" in entry.dependencies


def test_read_manifests_no_deps_empty_list():
    entries = read_manifests(manifest_contents=[_MANIFEST_NO_DEPS])
    entry = next(e for e in entries if e.block_id == "block-103")
    assert entry.dependencies == []


def test_read_manifests_status_extracted():
    entries = read_manifests(manifest_contents=[_MANIFEST_DONE])
    entry = next(e for e in entries if e.block_id == "block-001")
    assert entry.status == "done"


# ---------------------------------------------------------------------------
# Tests: find_unblocked
# ---------------------------------------------------------------------------

def test_find_unblocked_no_unblocks():
    """Block with partial deps not unblocked."""
    done = {"block-098"}
    entries = [ManifestEntry("block-110", "pending", ["block-098", "block-111"])]
    result = find_unblocked(done, entries)
    assert result == []


def test_find_unblocked_single():
    done = {"block-098", "block-099", "block-100"}
    entries = [ManifestEntry("block-109", "pending", ["block-098", "block-099", "block-100"])]
    result = find_unblocked(done, entries)
    assert len(result) == 1
    assert result[0].block_id == "block-109"


def test_find_unblocked_multiple():
    done = {"block-098", "block-099", "block-100"}
    entries = [
        ManifestEntry("block-109", "pending", ["block-098", "block-099"]),
        ManifestEntry("block-110", "pending", ["block-100"]),
        ManifestEntry("block-111", "pending", ["block-098", "block-999"]),  # 999 not done
    ]
    result = find_unblocked(done, entries)
    ids = [u.block_id for u in result]
    assert "block-109" in ids
    assert "block-110" in ids
    assert "block-111" not in ids


def test_find_unblocked_done_block_excluded():
    """Done blocks should not appear in unblocked list."""
    done = {"block-098"}
    entries = [ManifestEntry("block-001", "done", ["block-098"])]
    result = find_unblocked(done, entries)
    assert result == []


def test_find_unblocked_no_deps_block_excluded():
    """Blocks with no deps are already unblocked; don't re-notify."""
    done = {"block-098"}
    entries = [ManifestEntry("block-103", "pending", [])]
    result = find_unblocked(done, entries)
    assert result == []


# ---------------------------------------------------------------------------
# Tests: build_notifications
# ---------------------------------------------------------------------------

def test_build_notifications_produces_correct_kind():
    unblocked = [UnblockedBlock("block-109", ["block-098"])]
    msgs = build_notifications(unblocked)
    assert msgs[0]["kind"] == "notification"


def test_build_notifications_contains_block_id():
    unblocked = [UnblockedBlock("block-109", ["block-098"])]
    msgs = build_notifications(unblocked)
    assert msgs[0]["payload"]["data"]["block_id"] == "block-109"


def test_build_notifications_from_master():
    unblocked = [UnblockedBlock("block-109", ["block-098"])]
    msgs = build_notifications(unblocked)
    assert msgs[0]["from"] == "master"


def test_build_notifications_empty_input():
    assert build_notifications([]) == []


# ---------------------------------------------------------------------------
# Tests: run_resolver
# ---------------------------------------------------------------------------

def test_run_resolver_no_unblocks():
    result = run_resolver(
        log_content=_SAMPLE_LOG,
        manifest_contents=[_MANIFEST_PARTIAL],
    )
    assert result == []


def test_run_resolver_finds_unblocked():
    result = run_resolver(
        log_content=_SAMPLE_LOG,
        manifest_contents=[_MANIFEST_UNBLOCKABLE],
    )
    assert len(result) == 1
    assert result[0].block_id == "block-109"


def test_run_resolver_empty_log():
    result = run_resolver(
        log_content="",
        manifest_contents=[_MANIFEST_UNBLOCKABLE],
    )
    assert result == []
