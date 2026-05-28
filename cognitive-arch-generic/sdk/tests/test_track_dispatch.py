# PURPOSE: Tests for governor.py --list-tracks and --track flags (block-075)
# INPUTS:  pytest tmp_path fixture; subprocess calls to sdk/governor.py
# OUTPUTS: pass/fail test results
# DEPS:    pytest, subprocess, pathlib
# SEE:     manifests/block-075-parallel-track-dispatch.md, sdk/governor.py

import subprocess
import sys
from pathlib import Path

import pytest

# Path to governor.py — sdk/tests/ → sdk/ → cognitive-arch/sdk/governor.py
_SDK_DIR = Path(__file__).resolve().parent.parent
_GOVERNOR = _SDK_DIR / "governor.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(*args, arch_root: Path) -> subprocess.CompletedProcess:
    """Run governor.py with given args and --arch-root override."""
    cmd = [sys.executable, str(_GOVERNOR), "--arch-root", str(arch_root)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)


def _make_priority_md(tracks_dir: Path, rows: list[dict] | None = None) -> None:
    """Write a minimal tracks/PRIORITY.md with optional Track rows."""
    tracks_dir.mkdir(parents=True, exist_ok=True)
    header = (
        "# tracks/PRIORITY.md — Track Priority Table\n\n"
        "## Active Tracks\n\n"
        "| track_id | bottleneck_score | stagnation_count | user_priority | total_priority | notes |\n"
        "|----------|-----------------|-----------------|--------------|----------------|-------|\n"
    )
    body = ""
    if rows:
        for row in rows:
            body += (
                f"| {row['track_id']} | {row.get('bottleneck', 5)} | "
                f"{row.get('stagnation', 0)} | {row.get('user_priority', 5)} | "
                f"{row['total_priority']} | {row.get('notes', '-')} |\n"
            )
    else:
        body = "| _(no tracks yet)_ | — | — | — | — | — |\n"

    current = f"\ncurrent_focus: {rows[0]['track_id'] if rows else 'none'}\n" if rows else "\ncurrent_focus: none\n"
    (tracks_dir / "PRIORITY.md").write_text(header + body + current, encoding="utf-8")


def _make_track_file(tracks_dir: Path, track_id: str) -> None:
    """Write a minimal Track document at tracks/<track_id>.md."""
    tracks_dir.mkdir(parents=True, exist_ok=True)
    content = (
        f"---\n"
        f"id: track/{track_id}\n"
        f"system: {track_id}\n"
        f"description: Test track for {track_id}\n"
        f"benchmark_target: p99 < 10ms\n"
        f"benchmark_unit: ms\n"
        f"priority_score: 25\n"
        f"stagnation_count: 0\n"
        f"---\n\n"
        f"# Track: {track_id}\n\n"
        f"## System Overview\n\nTest track.\n"
    )
    (tracks_dir / f"{track_id}.md").write_text(content, encoding="utf-8")


def _make_track_block(tracks_dir: Path, track_id: str, block_id: str, status: str = "planned") -> None:
    """Write a minimal Track Block file inside tracks/."""
    tracks_dir.mkdir(parents=True, exist_ok=True)
    content = (
        f"---\n"
        f"id: {block_id}\n"
        f"track: track/{track_id}\n"
        f"phase: perpetual\n"
        f"status: {status}\n"
        f"hypothesis: Test hypothesis for {block_id}\n"
        f"benchmark_target: p99 < 10ms\n"
        f"benchmark_before: \"\"\n"
        f"benchmark_after: \"\"\n"
        f"benchmark_unit: ms\n"
        f"result: \"\"\n"
        f"reopened_count: 0\n"
        f"created_at: 2026-05-23\n"
        f"last_updated: 2026-05-23\n"
        f"---\n\n"
        f"# {block_id} — {track_id}: Test hypothesis\n"
    )
    (tracks_dir / f"{block_id}.md").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 1 — --list-tracks with no PRIORITY.md file
# ---------------------------------------------------------------------------

class TestListTracksNoPriorityFile:
    def test_list_tracks_no_priority_file(self, tmp_path):
        """--list-tracks exits 0 and mentions PRIORITY.md not found when file missing."""
        # No tracks/ directory at all
        result = _run("--list-tracks", arch_root=tmp_path)
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "No tracks/PRIORITY.md found" in combined


# ---------------------------------------------------------------------------
# Test 2 — --list-tracks with empty table
# ---------------------------------------------------------------------------

class TestListTracksEmptyTable:
    def test_list_tracks_empty_table(self, tmp_path):
        """--list-tracks exits 0 with 'No Tracks found' when PRIORITY.md has no rows."""
        _make_priority_md(tmp_path / "tracks", rows=None)
        result = _run("--list-tracks", arch_root=tmp_path)
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "No Tracks found" in combined


# ---------------------------------------------------------------------------
# Test 3 — --list-tracks with single Track row
# ---------------------------------------------------------------------------

class TestListTracksSingleTrack:
    def test_list_tracks_single_track(self, tmp_path):
        """--list-tracks exits 0 and prints track_id and total_priority for one Track."""
        _make_priority_md(tmp_path / "tracks", rows=[
            {"track_id": "TRK-001", "total_priority": "12"},
        ])
        result = _run("--list-tracks", arch_root=tmp_path)
        assert result.returncode == 0
        assert "TRK-001" in result.stdout
        assert "12" in result.stdout


# ---------------------------------------------------------------------------
# Test 4 — --list-tracks sorts by total_priority descending
# ---------------------------------------------------------------------------

class TestListTracksOrdering:
    def test_list_tracks_sorted_by_priority(self, tmp_path):
        """--list-tracks prints Tracks ordered by total_priority descending."""
        _make_priority_md(tmp_path / "tracks", rows=[
            {"track_id": "TRK-LOW",  "total_priority": "5"},
            {"track_id": "TRK-HIGH", "total_priority": "15"},
            {"track_id": "TRK-MID",  "total_priority": "8"},
        ])
        result = _run("--list-tracks", arch_root=tmp_path)
        assert result.returncode == 0
        pos_high = result.stdout.find("TRK-HIGH")
        pos_mid  = result.stdout.find("TRK-MID")
        pos_low  = result.stdout.find("TRK-LOW")
        assert pos_high >= 0 and pos_mid >= 0 and pos_low >= 0
        assert pos_high < pos_mid < pos_low, (
            f"Expected order HIGH({pos_high}) < MID({pos_mid}) < LOW({pos_low})"
        )


# ---------------------------------------------------------------------------
# Test 5 — --list-tracks --dry-run identical to without dry-run
# ---------------------------------------------------------------------------

class TestListTracksDryRun:
    def test_list_tracks_dry_run(self, tmp_path):
        """--list-tracks --dry-run exits 0; output is the same as without --dry-run."""
        _make_priority_md(tmp_path / "tracks", rows=[
            {"track_id": "TRK-A", "total_priority": "20"},
        ])
        result_normal  = _run("--list-tracks",             arch_root=tmp_path)
        result_dry_run = _run("--list-tracks", "--dry-run", arch_root=tmp_path)
        assert result_normal.returncode   == 0
        assert result_dry_run.returncode  == 0
        assert result_normal.stdout == result_dry_run.stdout


# ---------------------------------------------------------------------------
# Test 6 — --track with nonexistent Track name exits 1
# ---------------------------------------------------------------------------

class TestTrackDispatchMissingTrack:
    def test_track_dispatch_missing_track(self, tmp_path):
        """--track nonexistent-track-xyz --dry-run exits 1 with 'not found'."""
        _make_priority_md(tmp_path / "tracks", rows=None)
        result = _run("--track", "nonexistent-track-xyz", "--dry-run", arch_root=tmp_path)
        assert result.returncode == 1
        combined = result.stdout + result.stderr
        assert "not found" in combined.lower()


# ---------------------------------------------------------------------------
# Test 7 — --track with Track file but no open blocks exits 0
# ---------------------------------------------------------------------------

class TestTrackDispatchNoOpenBlocks:
    def test_track_dispatch_dry_run_no_blocks(self, tmp_path):
        """--track [name] --dry-run exits 0 with 'no open Track Blocks' when Track has none."""
        track_id = "test-system"
        tracks_dir = tmp_path / "tracks"
        _make_priority_md(tracks_dir, rows=[
            {"track_id": track_id, "total_priority": "25"},
        ])
        _make_track_file(tracks_dir, track_id)
        # No Track Block files created

        result = _run("--track", track_id, "--dry-run", arch_root=tmp_path)
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "no open Track Blocks" in combined


# ---------------------------------------------------------------------------
# Test 8 — --track with 2 open Track Blocks dispatches both (dry-run)
# ---------------------------------------------------------------------------

class TestTrackDispatchWithBlocks:
    def test_track_dispatch_dry_run_with_blocks(self, tmp_path):
        """--track [name] --dry-run exits 0 and lists 2 Track Blocks to dispatch."""
        track_id = "combat"
        tracks_dir = tmp_path / "tracks"
        _make_priority_md(tracks_dir, rows=[
            {"track_id": track_id, "total_priority": "30"},
        ])
        _make_track_file(tracks_dir, track_id)
        _make_track_block(tracks_dir, track_id, "track-block-001", status="planned")
        _make_track_block(tracks_dir, track_id, "track-block-002", status="planned")

        result = _run("--track", track_id, "--dry-run", arch_root=tmp_path)
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "2" in combined
        assert "DRY RUN" in combined or "Would dispatch" in combined


# ---------------------------------------------------------------------------
# Test 9 — --track current resolves to current_focus
# ---------------------------------------------------------------------------

class TestTrackCurrentFocus:
    def test_track_current_focus(self, tmp_path):
        """--track current --dry-run resolves current_focus and dispatches that Track's blocks."""
        track_id = "networking"
        tracks_dir = tmp_path / "tracks"
        _make_priority_md(tracks_dir, rows=[
            {"track_id": track_id, "total_priority": "42"},
        ])
        _make_track_file(tracks_dir, track_id)
        _make_track_block(tracks_dir, track_id, "track-block-net-001", status="planned")

        result = _run("--track", "current", "--dry-run", arch_root=tmp_path)
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        # Should reference the resolved track ID
        assert track_id in combined or "1" in combined


# ---------------------------------------------------------------------------
# Test 10 — Regression: existing --dry-run (phase dispatch) is unchanged
# ---------------------------------------------------------------------------

class TestExistingFlagsRegression:
    def test_dry_run_unaffected(self, tmp_path):
        """Existing --dry-run flag still exits 0 and has no Track-related output."""
        # Copy minimal STATE.md and NEXT.md from real arch (or create minimal versions)
        _sdk_dir = Path(__file__).resolve().parent.parent
        arch_root_real = _sdk_dir.parent
        for fname in ["STATE.md", "NEXT.md"]:
            src = arch_root_real / fname
            if src.exists():
                import shutil
                shutil.copy(src, tmp_path / fname)
            else:
                (tmp_path / fname).write_text(f"# {fname}\n", encoding="utf-8")

        result = _run("--dry-run", arch_root=tmp_path)
        assert result.returncode == 0
        # Should not contain Track-related language introduced by the new flags
        assert "Track Priority Table" not in result.stdout
        assert "Would dispatch" not in result.stdout
