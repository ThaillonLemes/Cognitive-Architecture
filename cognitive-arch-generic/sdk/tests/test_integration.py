# PURPOSE: Tests for sdk/integration.py — integrate_group(), check_fmod_disjoint(), state file updates
# INPUTS:  pytest fixtures (tmp_arch — isolated temp copy of state files)
# OUTPUTS: pass/fail test results
# DEPS:    pytest, integration, pathlib
# SEE:     manifests/block-055-test-dispatch-integration.md, sdk/integration.py

import pytest
from pathlib import Path
from integration import (
    integrate_group,
    check_fmod_disjoint,
    IntegrationResult,
    _update_state_md,
    _append_block_log,
    _update_next_md,
)


# ---------------------------------------------------------------------------
# Helpers — minimal DispatchResult-like objects for testing
# ---------------------------------------------------------------------------

class _MockValidation:
    """Minimal stand-in for ValidationResult."""
    def __init__(self, fmod: str = "-", valid: bool = True):
        self.valid = valid
        self.errors = []
        self.parsed = {
            "status": "done",
            "fmod": fmod,
            "fread": "-",
        }


class _MockResult:
    """Minimal stand-in for DispatchResult."""
    def __init__(self, block_id: str, fmod: str = "-", success: bool = True, valid: bool = True):
        self.block_id = block_id
        self.success = success
        self.validation = _MockValidation(fmod=fmod, valid=valid) if success else None


# ---------------------------------------------------------------------------
# Tests for check_fmod_disjoint
# ---------------------------------------------------------------------------

class TestCheckFmodDisjoint:
    def test_no_conflicts_empty_list(self):
        assert check_fmod_disjoint([]) == []

    def test_no_conflicts_distinct_paths(self):
        results = [
            _MockResult("034", fmod="sdk/dispatch.py"),
            _MockResult("035", fmod="sdk/integration.py"),
        ]
        assert check_fmod_disjoint(results) == []

    def test_conflict_same_path(self):
        results = [
            _MockResult("034", fmod="sdk/shared.py"),
            _MockResult("035", fmod="sdk/shared.py"),
        ]
        conflicts = check_fmod_disjoint(results)
        assert len(conflicts) == 1
        assert "shared.py" in conflicts[0]

    def test_no_conflict_when_fmod_is_dash(self):
        results = [
            _MockResult("034", fmod="-"),
            _MockResult("035", fmod="-"),
        ]
        assert check_fmod_disjoint(results) == []

    def test_invalid_result_skipped(self):
        """Results with valid=False must be skipped in conflict check."""
        results = [
            _MockResult("034", fmod="sdk/shared.py", valid=False),
            _MockResult("035", fmod="sdk/shared.py"),
        ]
        conflicts = check_fmod_disjoint(results)
        assert conflicts == []

    def test_conflict_message_mentions_both_blocks(self):
        results = [
            _MockResult("034", fmod="sdk/conflict.py"),
            _MockResult("036", fmod="sdk/conflict.py"),
        ]
        conflicts = check_fmod_disjoint(results)
        assert "034" in conflicts[0]
        assert "036" in conflicts[0]


# ---------------------------------------------------------------------------
# Tests for integrate_group (uses tmp_arch fixture)
# ---------------------------------------------------------------------------

class TestIntegrateGroup:
    def test_returns_integration_result_type(self, tmp_arch):
        results = [_MockResult("099")]
        ir = integrate_group(results, tmp_arch, next_block="100", do_commit=False)
        assert isinstance(ir, IntegrationResult)

    def test_successful_integration(self, tmp_arch):
        results = [_MockResult("099")]
        ir = integrate_group(results, tmp_arch, next_block="100", do_commit=False)
        assert ir.success is True

    def test_blocks_integrated_field(self, tmp_arch):
        results = [_MockResult("099"), _MockResult("098")]
        ir = integrate_group(results, tmp_arch, next_block="100", do_commit=False)
        assert "099" in ir.blocks_integrated
        assert "098" in ir.blocks_integrated

    def test_state_md_updated(self, tmp_arch):
        """STATE.md must contain the last block ID after integration."""
        results = [_MockResult("099")]
        integrate_group(results, tmp_arch, next_block="100", do_commit=False)
        state = (tmp_arch / "STATE.md").read_text(encoding="utf-8")
        assert "block-099" in state

    def test_block_log_appended(self, tmp_arch):
        """BLOCK_LOG.md must have a new line for each integrated block."""
        results = [_MockResult("099")]
        integrate_group(results, tmp_arch, next_block="100", do_commit=False)
        log = (tmp_arch / "blocks" / "BLOCK_LOG.md").read_text(encoding="utf-8")
        assert "block-099 done" in log

    def test_two_blocks_both_in_log(self, tmp_arch):
        results = [
            _MockResult("097", fmod="sdk/a.py"),
            _MockResult("098", fmod="sdk/b.py"),
        ]
        integrate_group(results, tmp_arch, next_block="099", do_commit=False)
        log = (tmp_arch / "blocks" / "BLOCK_LOG.md").read_text(encoding="utf-8")
        assert "block-097 done" in log
        assert "block-098 done" in log

    def test_empty_results_returns_failure(self, tmp_arch):
        ir = integrate_group([], tmp_arch, next_block="100", do_commit=False)
        assert ir.success is False
        assert ir.errors

    def test_all_failed_returns_failure(self, tmp_arch):
        results = [_MockResult("099", success=False)]
        ir = integrate_group(results, tmp_arch, next_block="100", do_commit=False)
        assert ir.success is False

    def test_failed_blocks_tracked(self, tmp_arch):
        results = [
            _MockResult("097", fmod="sdk/a.py"),
            _MockResult("098", success=False),
        ]
        ir = integrate_group(results, tmp_arch, next_block="099", do_commit=False)
        assert "098" in ir.blocks_failed

    def test_conflict_detected_in_integrate(self, tmp_arch):
        """integrate_group should report conflicts when two blocks touch same file."""
        results = [
            _MockResult("097", fmod="sdk/shared.py"),
            _MockResult("098", fmod="sdk/shared.py"),
        ]
        ir = integrate_group(results, tmp_arch, next_block="099", do_commit=False)
        assert len(ir.conflicts) > 0

    def test_do_commit_false_committed_is_false(self, tmp_arch):
        results = [_MockResult("099")]
        ir = integrate_group(results, tmp_arch, next_block="100", do_commit=False)
        assert ir.committed is False


# ---------------------------------------------------------------------------
# Tests for individual state-file helpers (direct unit tests)
# ---------------------------------------------------------------------------

class TestUpdateStateMd:
    def test_last_block_updated(self, tmp_arch):
        _update_state_md(tmp_arch, last_block="099", next_block="100", blocks_done_extra=["099"])
        content = (tmp_arch / "STATE.md").read_text(encoding="utf-8")
        assert "last_block:block-099" in content

    def test_next_pointer_updated(self, tmp_arch):
        _update_state_md(tmp_arch, last_block="099", next_block="100", blocks_done_extra=[])
        content = (tmp_arch / "STATE.md").read_text(encoding="utf-8")
        assert "next:block-100" in content


class TestAppendBlockLog:
    def test_log_line_appended(self, tmp_arch):
        _append_block_log(tmp_arch, ["099"])
        log = (tmp_arch / "blocks" / "BLOCK_LOG.md").read_text(encoding="utf-8")
        assert "block-099 done" in log

    def test_multiple_lines_appended(self, tmp_arch):
        _append_block_log(tmp_arch, ["097", "098"])
        log = (tmp_arch / "blocks" / "BLOCK_LOG.md").read_text(encoding="utf-8")
        assert "block-097 done" in log
        assert "block-098 done" in log

    def test_noop_when_log_missing(self, tmp_path):
        """_append_block_log should not crash when BLOCK_LOG.md doesn't exist."""
        empty_arch = tmp_path / "empty_arch"
        empty_arch.mkdir()
        (empty_arch / "blocks").mkdir()
        # No BLOCK_LOG.md — should not raise
        _append_block_log(empty_arch, ["099"])
