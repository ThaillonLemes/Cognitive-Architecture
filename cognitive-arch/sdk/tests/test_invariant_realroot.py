# PURPOSE: Permanent regression guard for Phase 25's exit criterion — the REAL
#          arch-root must always scan to 0 CRITICAL invariant violations, and the
#          block-close gate must return ok=True on it. WARNs (INV2/INV3 historical
#          gaps, documented in governance/known-drift.md) are allowed.
# INPUTS:  the live arch-root (this file's grandparent dir: sdk/tests/ -> sdk/ -> root)
# OUTPUTS: assertions on invariant_check.run_all(REAL_ROOT) + gate_result(REAL_ROOT)
# DEPS:    pytest, pathlib, invariant_check module
# SEE:     sdk/invariant_check.py, governance/known-drift.md, manifests/block-147-backfill-verify.md

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent          # .../cognitive-arch/sdk
REAL_ROOT = _SDK_DIR.parent                                 # .../cognitive-arch
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import invariant_check as ic


# Sanity: we resolved the actual arch-root, not a stray directory.
def test_real_root_is_the_arch_root():
    assert (REAL_ROOT / "blocks" / "BLOCK_LOG.md").exists(), \
        f"REAL_ROOT does not look like the arch-root: {REAL_ROOT}"
    assert (REAL_ROOT / ".integrity.lock").exists(), \
        f"missing .integrity.lock under REAL_ROOT: {REAL_ROOT}"


# ---------------------------------------------------------------------------
# THE Phase-25 exit guard: 0 critical on the real root. If a future change
# reintroduces a critical (e.g. a real immutable file dropped from the lock,
# or a TOOL_RUNNERS key without a registry id), THIS test fails.
# ---------------------------------------------------------------------------

def test_real_root_zero_critical():
    violations = ic.run_all(REAL_ROOT)
    criticals = [v for v in violations if v.severity == "critical"]
    assert criticals == [], (
        "real arch-root must have 0 CRITICAL invariant violations, got "
        + str([f"[{v.invariant_id}] {v.message}" for v in criticals])
    )


def test_real_root_gate_ok():
    ok, criticals = ic.gate_result(REAL_ROOT)
    assert ok is True, (
        "gate_result(REAL_ROOT) must be ok=True (no criticals), got criticals: "
        + str([f"[{v.invariant_id}] {v.message}" for v in criticals])
    )
    assert criticals == []


# INV1 specifically (the block-147 fix target) must be clean on the real root:
# the tightened find_immutable_files removes prose false-positives, so every
# *genuinely* frontmatter-tagged immutable file is present in .integrity.lock.
def test_real_root_inv1_clean():
    assert ic.check_inv1(REAL_ROOT) == [], (
        "INV1 must be clean on the real root (every frontmatter-tagged immutable "
        "file is in .integrity.lock)"
    )


# Guard the property, not the exact count: WARNs are allowed (and documented in
# governance/known-drift.md), but run_all must still return a list (never raise).
def test_real_root_run_all_never_raises_and_returns_list():
    violations = ic.run_all(REAL_ROOT)
    assert isinstance(violations, list)
