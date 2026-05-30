# sdk/tests/test_boot_budget.py
# PURPOSE: Permanent regression guard — the HOT boot must stay under 4000 tok.
#          Computes the total the SAME way as sdk/audit.py::print_token_estimates
#          (sum of len(read_bytes()) over the HOT file list, then // 4) so the test
#          cannot silently diverge from the audit's own measurement.
# DEPS:    pytest, subprocess, sdk/audit
# SEE:     blocks/block-143-budget-gate.md, phases/phase-24.md, sdk/audit.py

import inspect
import subprocess
import sys
from pathlib import Path

_SDK = Path(__file__).resolve().parent.parent
_ROOT = _SDK.parent
sys.path.insert(0, str(_SDK))

import audit

# Mirrors the HOT cost list inside audit.print_token_estimates. The coupling test
# below fails if audit's list ever diverges from this one.
HOT_FILES = ["CLAUDE.md", "PROTOCOLS.md", "STATE.md", "NEXT.md", "INDEX.md", "board.md"]
BUDGET_TOK = 4000
HEADROOM_TOK = 200  # phase-24 targets >=200 tok of slack below the budget


def _hot_boot_tokens(root: Path) -> int:
    """Same arithmetic as audit.print_token_estimates: sum of byte-lengths // 4."""
    total = 0
    for f in HOT_FILES:
        p = root / f
        if p.exists():
            total += len(p.read_bytes())
    return total // 4


def test_hot_boot_under_budget():
    tok = _hot_boot_tokens(_ROOT)
    assert tok < BUDGET_TOK, f"HOT boot {tok} tok >= {BUDGET_TOK} budget"


def test_hot_boot_keeps_headroom():
    tok = _hot_boot_tokens(_ROOT)
    assert tok <= BUDGET_TOK - HEADROOM_TOK, (
        f"HOT boot {tok} tok leaves < {HEADROOM_TOK} tok headroom under {BUDGET_TOK}"
    )


def test_list_matches_audit_measurement():
    # Coupling guard: this test's HOT_FILES must equal audit's cost list, and
    # _syntax.md must stay reclassified out (block-142).
    src = inspect.getsource(audit.print_token_estimates)
    for f in HOT_FILES:
        assert f in src, f"{f} missing from audit.print_token_estimates list"
    assert "_syntax.md" not in src


def test_audit_run_not_over_budget():
    proc = subprocess.run(
        [sys.executable, "sdk/audit.py", "--arch-root", "."],
        cwd=str(_ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert proc.returncode == 0, f"audit.py exited {proc.returncode}"
    assert "OVER BUDGET" not in out, "audit reports HOT boot OVER BUDGET"
