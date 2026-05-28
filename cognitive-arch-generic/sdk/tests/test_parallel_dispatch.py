# PURPOSE: Tests for dispatch_batch() — parallel dispatch via ThreadPoolExecutor
# INPUTS:  pytest fixtures (none needed — stateless mock dispatch)
# OUTPUTS: pass/fail test results
# DEPS:    pytest, dispatch
# SEE:     manifests/block-060-parallel-dispatch.md, sdk/dispatch.py

import pytest
from dispatch import dispatch_batch, dispatch_block, DispatchResult


_PACKET_A = (
    "b:091 kind:doc-only phase:phase-7 gov:g-test ts:2026-05-22T12:00Z\n"
    "axioms:P1,Q1 scope:closed retro_req:yes tok_track:yes\n"
    "fread:STATE.md fmod:-\n"
    "\n--- manifest ---\n[test manifest block-091]\n"
)

_PACKET_B = (
    "b:092 kind:doc-only phase:phase-7 gov:g-test ts:2026-05-22T12:00Z\n"
    "axioms:P1,Q2 scope:closed retro_req:yes tok_track:yes\n"
    "fread:NEXT.md fmod:-\n"
    "\n--- manifest ---\n[test manifest block-092]\n"
)

_PACKET_C = (
    "b:093 kind:gate phase:phase-7 gov:g-test ts:2026-05-22T12:00Z\n"
    "axioms:P3 scope:closed retro_req:yes tok_track:yes\n"
    "fread:board.md fmod:-\n"
    "\n--- manifest ---\n[test manifest block-093]\n"
)


class TestDispatchBatch:
    def test_empty_list_returns_empty(self):
        results = dispatch_batch([], mode="mock")
        assert results == []

    def test_single_packet_returns_one_result(self):
        results = dispatch_batch([_PACKET_A], mode="mock")
        assert len(results) == 1

    def test_two_packets_returns_two_results(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B], mode="mock")
        assert len(results) == 2

    def test_three_packets_returns_three_results(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B, _PACKET_C], mode="mock")
        assert len(results) == 3

    def test_all_results_are_dispatch_result_type(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B], mode="mock")
        for r in results:
            assert isinstance(r, DispatchResult)

    def test_all_results_succeed_in_mock_mode(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B, _PACKET_C], mode="mock")
        for r in results:
            assert r.success is True, f"block {r.block_id} failed: {r.error}"

    def test_block_ids_extracted_from_packets(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B], mode="mock")
        block_ids = {r.block_id for r in results}
        assert "091" in block_ids
        assert "092" in block_ids

    def test_results_order_preserved(self):
        """dispatch_batch must return results in the same order as input packets."""
        results = dispatch_batch([_PACKET_A, _PACKET_B, _PACKET_C], mode="mock")
        assert results[0].block_id == "091"
        assert results[1].block_id == "092"
        assert results[2].block_id == "093"

    def test_max_workers_1_works_sequential(self):
        """max_workers=1 should work correctly (sequential fallback)."""
        results = dispatch_batch([_PACKET_A, _PACKET_B], mode="mock", max_workers=1)
        assert len(results) == 2
        assert all(r.success for r in results)

    def test_max_workers_4_parallel(self):
        """max_workers=4 with 3 packets should still return 3 results."""
        results = dispatch_batch(
            [_PACKET_A, _PACKET_B, _PACKET_C], mode="mock", max_workers=4
        )
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_each_result_has_validation(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B], mode="mock")
        for r in results:
            assert r.validation is not None
            assert r.validation.valid is True

    def test_each_result_has_elapsed_sec(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B], mode="mock")
        for r in results:
            assert r.elapsed_sec >= 0.0

    def test_each_result_has_positive_tok_counts(self):
        results = dispatch_batch([_PACKET_A, _PACKET_B], mode="mock")
        for r in results:
            assert r.tok_in > 0
            assert r.tok_out > 0


class TestGovernorParallelFlag:
    """Integration smoke-test: governor.py CLI with --parallel N --dry-run."""

    def test_parallel_dry_run_prints_parallel_mode(self):
        """governor.py --parallel 2 --dry-run must print 'parallel mode'."""
        import subprocess
        import sys
        from pathlib import Path

        sdk_dir = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            [sys.executable, str(sdk_dir / "governor.py"), "--parallel", "2", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"exit={result.returncode}\n{result.stderr}"
        assert "parallel mode" in result.stdout, (
            f"Expected 'parallel mode' in stdout, got:\n{result.stdout}"
        )

    def test_parallel_dry_run_mentions_worker_count(self):
        """Output must mention the number of workers."""
        import subprocess
        import sys
        from pathlib import Path

        sdk_dir = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            [sys.executable, str(sdk_dir / "governor.py"), "--parallel", "3", "--dry-run"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "3" in result.stdout
