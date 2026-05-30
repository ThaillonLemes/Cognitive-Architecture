# sdk/tests/test_hot_set.py
# PURPOSE: Lock in the Phase-24 HOT-set correction — _syntax.md is WARM, not HOT.
#          Guards against _syntax.md (or any non-boot file) creeping back into the
#          audit HOT cost/budget lists and re-inflating the boot estimate.
# DEPS:    pytest, sdk/audit
# SEE:     blocks/block-142-hot-set-correct.md, sdk/audit.py

import inspect
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import audit


def test_syntax_not_in_size_budgets():
    assert "_syntax.md" not in audit.SIZE_BUDGETS


def test_syntax_not_in_token_estimate_list():
    src = inspect.getsource(audit.print_token_estimates)
    assert "_syntax.md" not in src


def test_hot_cost_list_is_the_six_expected():
    src = inspect.getsource(audit.print_token_estimates)
    for f in ["CLAUDE.md", "PROTOCOLS.md", "STATE.md", "NEXT.md", "INDEX.md", "board.md"]:
        assert f in src


def test_claude_readorder_does_not_number_syntax_as_boot_read():
    # _syntax.md may appear as an inline on-demand pointer, but must NOT be a
    # numbered HOT read-order line like "N. `_syntax.md` ...".
    root = Path(__file__).resolve().parent.parent.parent
    text = (root / "CLAUDE.md").read_text(encoding="utf-8")
    assert not re.search(r"^\s*\d+\.\s*`_syntax\.md`", text, re.MULTILINE)
