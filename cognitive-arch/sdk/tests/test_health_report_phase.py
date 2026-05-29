# PURPOSE: Regression test — health_report must report the REAL current phase
#          (>= 22) via project_state, not the lexically-last phase file (phase-9).
# INPUTS:  the real arch-root (this repo), resolved from the test file location
# OUTPUTS: assertions on the rendered Phase Progress section + block count parity
# DEPS:    pytest, pathlib, project_state, health_report
# SEE:     sdk/health_report.py, sdk/project_state.py, phases/phase-23.md block-137

import re
import sys
from pathlib import Path

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import health_report
import project_state

# tests -> sdk -> cognitive-arch (the real arch-root)
_ARCH_ROOT = Path(__file__).resolve().parents[2]


def test_real_arch_root_phase_is_at_least_22():
    # The bug this guards: lexical sort picked phase-9 over phase-22/23.
    assert project_state.current_phase(_ARCH_ROOT) >= 22


def test_health_report_phase_section_not_lexical():
    section = health_report._section_phase_progress(_ARCH_ROOT, {})
    m = re.search(r"Current phase:\s*phase-(\d+)", section)
    assert m, f"no 'Current phase' line in:\n{section}"
    assert int(m.group(1)) >= 22, f"health_report regressed to {m.group(0)}"


def test_health_report_block_count_matches_project_state():
    # The header line "Blocks completed: N" must equal project_state's count.
    report = health_report.generate_report(_ARCH_ROOT)
    m = re.search(r"Blocks completed:\s*(\d+)", report)
    assert m, "no 'Blocks completed' line in report header"
    assert int(m.group(1)) == project_state.block_count(_ARCH_ROOT)
