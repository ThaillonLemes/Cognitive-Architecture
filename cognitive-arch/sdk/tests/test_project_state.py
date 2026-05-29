# PURPOSE: Tests for sdk/project_state.py (block-137) — the single source of truth.
# INPUTS:  tmp_path with synthetic STATE.md, BLOCK_LOG.md, phases/
# OUTPUTS: assertions on phase/block readers + the lexical-sort regression
# DEPS:    pytest, pathlib, project_state
# SEE:     sdk/project_state.py, phases/phase-23.md block-137

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import project_state


def _make(tmp_path: Path, p: int = 22, blocks=("block-001", "block-002"),
          phase_nums=(1, 9, 22)) -> Path:
    (tmp_path / "STATE.md").write_text(
        f"# STATE\n\np:{p} status:active phase:phase-{p} last_block:block-002\n",
        encoding="utf-8")
    log = "# BLOCK_LOG\n\n" + "".join(
        f"{b} done 2026-05-29 | tier:M\n" for b in blocks)
    (tmp_path / "blocks").mkdir(exist_ok=True)
    (tmp_path / "blocks" / "BLOCK_LOG.md").write_text(log, encoding="utf-8")
    phases = tmp_path / "phases"
    phases.mkdir(exist_ok=True)
    for n in phase_nums:
        (phases / f"phase-{n}.md").write_text(f"# Phase {n}\n", encoding="utf-8")
        (phases / f"phase-{n}-retro.md").write_text(f"# retro {n}\n", encoding="utf-8")
    return tmp_path


class TestCurrentPhase:
    def test_reads_p_field(self, tmp_path):
        _make(tmp_path, p=23)
        assert project_state.current_phase(tmp_path) == 23

    def test_name(self, tmp_path):
        _make(tmp_path, p=23)
        assert project_state.current_phase_name(tmp_path) == "phase-23"

    def test_none_when_missing(self, tmp_path):
        assert project_state.current_phase(tmp_path) is None


class TestCompletedBlocks:
    def test_counts_unique(self, tmp_path):
        _make(tmp_path, blocks=("block-001", "block-002", "block-003"))
        assert project_state.block_count(tmp_path) == 3

    def test_dedupes(self, tmp_path):
        _make(tmp_path, blocks=("block-001", "block-001", "block-002"))
        assert project_state.completed_block_ids(tmp_path) == ["block-001", "block-002"]

    def test_ignores_non_done(self, tmp_path):
        _make(tmp_path, blocks=("block-001",))
        log = tmp_path / "blocks" / "BLOCK_LOG.md"
        log.write_text(log.read_text() + "block-099 planned 2026-05-29\n", encoding="utf-8")
        assert "block-099" not in project_state.completed_block_ids(tmp_path)


class TestPhaseFilesNumericSort:
    def test_excludes_retro_files(self, tmp_path):
        _make(tmp_path, phase_nums=(1, 22))
        stems = [p.stem for p in project_state.phase_files(tmp_path)]
        assert "phase-22-retro" not in stems
        assert "phase-22" in stems

    def test_numeric_not_lexical_order(self, tmp_path):
        # The bug: lexical sort puts phase-9 last (after phase-22).
        _make(tmp_path, phase_nums=(1, 9, 10, 22))
        files = project_state.phase_files(tmp_path)
        assert files[-1].stem == "phase-22"  # numerically highest, NOT phase-9


class TestCurrentPhaseFile:
    def test_resolves_by_state_not_lexical(self, tmp_path):
        # STATE says p:22; lexical sort would wrongly pick phase-9.
        _make(tmp_path, p=22, phase_nums=(1, 9, 22))
        cur = project_state.current_phase_file(tmp_path)
        assert cur is not None and cur.stem == "phase-22"

    def test_falls_back_to_highest_when_state_missing(self, tmp_path):
        _make(tmp_path, phase_nums=(1, 9, 22))
        (tmp_path / "STATE.md").write_text("# STATE\n\nno phase field\n", encoding="utf-8")
        cur = project_state.current_phase_file(tmp_path)
        assert cur is not None and cur.stem == "phase-22"
