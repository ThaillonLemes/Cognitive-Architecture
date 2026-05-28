# cognitive-arch / sdk/tests/test_tools_registry.py
# purpose: Unit tests for sdk/tools_registry.py
# stdlib-only; no external dependencies

import os
import sys
import tempfile
import textwrap
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools_registry import (
    ToolEntry,
    read_registry,
    update_last_run,
    get_stale_tools,
    REGISTRY_PATH,
)

# ---------------------------------------------------------------------------
# Sample registry YAML used in tests
# ---------------------------------------------------------------------------

SAMPLE_YAML = textwrap.dedent("""
    schema_version: "1.0"
    generated_at: "2026-05-27"
    timezone: America/Sao_Paulo

    tools:
      - id: audit
        name: "Project audit"
        command: "bash audit.sh"
        description: "Full audit"
        recommended_interval_days: 1
        trigger_type: time
        priority: high
        last_run: "never"
        mutable_by: master

      - id: health-report
        name: "Health report"
        command: "python sdk/health_report.py"
        description: "Health snapshot"
        recommended_interval_days: 3
        trigger_type: time
        priority: high
        last_run: "2026-05-20T00:00:00+00:00"
        mutable_by: master

      - id: dependency-check
        name: "Dependency check"
        command: "python sdk/dependency_resolver.py"
        description: "Dep check"
        recommended_interval_days: 0
        trigger_type: event
        priority: high
        last_run: "never"
        mutable_by: master

      - id: pattern-mining
        name: "Pattern mining"
        command: "python sdk/pattern_analyzer.py"
        description: "Pattern scan"
        recommended_interval_days: 7
        trigger_type: time
        priority: medium
        last_run: "never"
        mutable_by: master
""")


@pytest.fixture
def registry_root(tmp_path):
    """Create a temp arch_root with a governance/tools-registry.yaml."""
    gov_dir = tmp_path / "governance"
    gov_dir.mkdir()
    registry_file = gov_dir / "tools-registry.yaml"
    registry_file.write_text(SAMPLE_YAML, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Tests: read_registry
# ---------------------------------------------------------------------------

def test_read_registry_returns_all_tools(registry_root):
    entries = read_registry(str(registry_root))
    assert len(entries) == 4


def test_read_registry_first_tool_id(registry_root):
    entries = read_registry(str(registry_root))
    assert entries[0].id == "audit"


def test_read_registry_interval_parsed_as_float(registry_root):
    entries = read_registry(str(registry_root))
    assert entries[0].recommended_interval_days == 1.0


def test_read_registry_last_run_never(registry_root):
    entries = read_registry(str(registry_root))
    assert entries[0].last_run == "never"


def test_read_registry_last_run_timestamp(registry_root):
    entries = read_registry(str(registry_root))
    health = next(e for e in entries if e.id == "health-report")
    assert "2026-05-20" in health.last_run


def test_read_registry_event_tool(registry_root):
    entries = read_registry(str(registry_root))
    dep = next(e for e in entries if e.id == "dependency-check")
    assert dep.trigger_type == "event"


# ---------------------------------------------------------------------------
# Tests: ToolEntry properties
# ---------------------------------------------------------------------------

def test_days_since_last_run_never():
    entry = ToolEntry(
        id="x", name="x", command="x", description="x",
        recommended_interval_days=1, trigger_type="time",
        priority="high", last_run="never",
    )
    assert entry.days_since_last_run is None


def test_days_since_last_run_event_tool():
    entry = ToolEntry(
        id="x", name="x", command="x", description="x",
        recommended_interval_days=0, trigger_type="event",
        priority="high", last_run="2026-05-01T00:00:00+00:00",
    )
    assert entry.days_since_last_run is None


def test_is_overdue_never_run():
    entry = ToolEntry(
        id="x", name="x", command="x", description="x",
        recommended_interval_days=1, trigger_type="time",
        priority="high", last_run="never",
    )
    assert entry.is_overdue is True


def test_is_stale_never_run():
    entry = ToolEntry(
        id="x", name="x", command="x", description="x",
        recommended_interval_days=1, trigger_type="time",
        priority="high", last_run="never",
    )
    assert entry.is_stale is True


def test_is_stale_recent_tool():
    now = datetime.now(timezone.utc)
    recent_ts = (now - timedelta(hours=6)).isoformat()
    entry = ToolEntry(
        id="x", name="x", command="x", description="x",
        recommended_interval_days=1, trigger_type="time",
        priority="high", last_run=recent_ts,
    )
    assert entry.is_stale is False


def test_is_overdue_event_tool():
    entry = ToolEntry(
        id="x", name="x", command="x", description="x",
        recommended_interval_days=0, trigger_type="event",
        priority="high", last_run="never",
    )
    assert entry.is_overdue is False


# ---------------------------------------------------------------------------
# Tests: update_last_run
# ---------------------------------------------------------------------------

def test_update_last_run_changes_value(registry_root):
    ts = "2026-05-27T12:00:00+00:00"
    update_last_run("audit", now_ts=ts, arch_root=str(registry_root))
    entries = read_registry(str(registry_root))
    audit = next(e for e in entries if e.id == "audit")
    assert audit.last_run == ts


def test_update_last_run_other_tools_unchanged(registry_root):
    ts = "2026-05-27T12:00:00+00:00"
    update_last_run("audit", now_ts=ts, arch_root=str(registry_root))
    entries = read_registry(str(registry_root))
    health = next(e for e in entries if e.id == "health-report")
    assert "2026-05-20" in health.last_run


def test_update_last_run_invalid_id_raises(registry_root):
    with pytest.raises(ValueError):
        update_last_run("nonexistent-tool", arch_root=str(registry_root))


# ---------------------------------------------------------------------------
# Tests: get_stale_tools
# ---------------------------------------------------------------------------

def test_get_stale_tools_includes_never_run(registry_root):
    now_ts = "2026-05-27T12:00:00+00:00"
    stale = get_stale_tools(now_ts=now_ts, arch_root=str(registry_root))
    ids = [e.id for e in stale]
    assert "audit" in ids


def test_get_stale_tools_excludes_event_tools(registry_root):
    now_ts = "2026-05-27T12:00:00+00:00"
    stale = get_stale_tools(now_ts=now_ts, arch_root=str(registry_root))
    ids = [e.id for e in stale]
    assert "dependency-check" not in ids


def test_get_stale_tools_threshold_multiplier_2(registry_root):
    """With 2x multiplier: health-report (7 days old, interval=3) should appear at 2x."""
    now_ts = "2026-05-27T12:00:00+00:00"
    overdue = get_stale_tools(now_ts=now_ts, threshold_multiplier=2.0, arch_root=str(registry_root))
    ids = [e.id for e in overdue]
    # health-report last run 2026-05-20, now 2026-05-27 → 7d > 2*3=6d → overdue
    assert "health-report" in ids


def test_get_stale_tools_fresh_tool_excluded(registry_root):
    """Update audit to just-now, then check that it's not stale."""
    now_ts = "2026-05-27T12:00:00+00:00"
    update_last_run("audit", now_ts="2026-05-27T11:59:00+00:00", arch_root=str(registry_root))
    stale = get_stale_tools(now_ts=now_ts, threshold_multiplier=1.0, arch_root=str(registry_root))
    ids = [e.id for e in stale]
    assert "audit" not in ids
