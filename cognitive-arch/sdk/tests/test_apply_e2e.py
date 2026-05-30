# PURPOSE: Block-155 capstone — end-to-end demonstration of the whole 152-154 pipeline. Proves: an accepted proposal against a NON-immutable synthetic target goes all the way through apply (backup -> atomic write -> REAL pytest+audit verify -> status:applied + governor-log + ADR); a forced-failure goes through rollback (byte-identical restore, no ADR, status untouched); and the REAL repo's immutable proposals are refused read-only with zero writes.
# INPUTS:  tmp_path SYNTHETIC arch-roots (a self-contained mini-arch with a real stub sdk/tests/ + audit.py so the GENUINE _run_verification subprocess passes/fails for real — NO monkeypatch on the headline e2e tests); the REAL repo root for read-only guard/refusal regressions only
# OUTPUTS: assertions on ApplyResult end-to-end (applied path + rollback path) and on the real repo being byte-identical after refusal/guard checks; a hygiene test asserting zero stray _backups/ / *.apply.tmp / *.restore.tmp in the real repo after the suite
# DEPS:    pytest, pathlib, subprocess (indirectly, via proposal_apply._run_verification), proposal_apply module
# SEE:     sdk/proposal_apply.py (blocks 152-154), manifests/block-155-e2e-verify.md, manifests/block-154-apply-rollback.md, governance/proposals/index.md, phases/phase-27.md
#
# SAFETY (block-155 hard constraint): NO real protocol/immutable file is ever written by this suite.
#   * The apply + rollback demonstrations run ENTIRELY inside tmp_path mini-arches whose target is a
#     fresh, non-immutable, unlocked file created by the test — never a real repo file.
#   * The real repo is touched only by READ-ONLY guard evaluation (check_guards) and by a confirm=True
#     apply on a real IMMUTABLE proposal that the guard layer REFUSES before any write — both verified
#     byte-identical before/after.
#   * The genuine _run_verification (real `pytest sdk/tests/` + `audit.py` subprocess) runs with
#     cwd=<tmp mini-arch>, so it collects ONLY the stub test under tmp_path and never re-enters this
#     suite (no recursion) and never shells against the real repo.

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import proposal_apply
from proposal_apply import (
    ProposalApply,
    ApplyResult,
    GuardResult,
    apply_proposal,
    check_guards,
)
from proposal_resolver import _is_immutable

# Real cognitive-arch root (this test file lives in <root>/sdk/tests/).
REAL_ROOT = _SDK_DIR.parent

# Real proposals (governance/proposals/index.md):
#   accepted + immutable target  -> must be REFUSED with no write.
_REAL_IMMUTABLE_SCOPE = "2026-05-29-scope-expansion-recurring"   # -> templates/manifest-medium.md (immutable)
_REAL_IMMUTABLE_GATES = "2026-05-29-gate-failures-recurring"     # -> protocols/block-close-checklist.md (immutable)
#   rejected + NON-immutable target -> guard refuses on ACCEPTANCE, never on immutability.
_REAL_NONIMMUTABLE_REJECTED = "2026-05-29-velocity-data-gap"     # -> protocols/block-complexity-estimator.md (NON-immutable)
_REAL_NONIMMUTABLE_TARGET = "protocols/block-complexity-estimator.md"
_REAL_IMMUTABLE_SCOPE_FILE = "templates/manifest-medium.md"


# ---------------------------------------------------------------------------
# Self-contained synthetic mini-arch builder
#
# Unlike the block-154 unit tests (which monkeypatch _run_verification), the
# headline e2e tests here build a REAL stub sdk/tests/ + audit.py inside the
# tmp arch so the GENUINE verification subprocess runs and decides the outcome.
# That is what makes this an end-to-end demonstration rather than a re-test.
# ---------------------------------------------------------------------------

def _build_mini_arch(tmp_path: Path, *, stub_tests_pass: bool) -> tuple[Path, str, str]:
    """Create a minimal but REAL arch under tmp_path that proposal_apply can drive
    end-to-end through its own pytest+audit subprocess.

    Returns (arch_root, proposal_id, target_file_relpath).

    The arch contains:
      * PROTOCOLS.md          — declares no immutable files (target stays OPEN).
      * a NON-immutable, unlocked Markdown target with leading frontmatter.
      * governance/proposals/<id>.md (status: accepted) + a matching index.md row.
      * sdk/audit.py          — a stub that prints PASS and exits 0 (the audit gate).
      * sdk/tests/test_stub.py — a stub test that PASSES or FAILS per stub_tests_pass,
                                 so the real `pytest sdk/tests/` gate is genuinely
                                 green (apply path) or red (rollback path).

    Because _run_verification runs `pytest sdk/tests/` and `audit.py` with
    cwd=arch_root, both subprocesses see ONLY this mini-arch — never the real
    repo and never this very suite.
    """
    arch = tmp_path / "mini_arch"
    (arch / "governance" / "proposals").mkdir(parents=True, exist_ok=True)
    (arch / "sdk" / "tests").mkdir(parents=True, exist_ok=True)
    (arch / "protocols").mkdir(parents=True, exist_ok=True)

    # PROTOCOLS.md: no immutable declarations -> the target is freely writable.
    (arch / "PROTOCOLS.md").write_text(
        "# PROTOCOLS\n\nMini-arch for the block-155 e2e demo. No immutable files declared.\n",
        encoding="utf-8",
    )

    # A NON-immutable, unlocked target with real leading frontmatter (so the
    # structural-sanity guard's frontmatter-balance check is genuinely exercised).
    target_file = "protocols/e2e-note-target.md"
    (arch / target_file).write_text(
        "---\n"
        "title: E2E Note Target\n"
        "kind: doc\n"
        "---\n\n"
        "# E2E Note Target\n\n"
        "Original body. The apply engine should append a reviewable section below.\n",
        encoding="utf-8",
    )

    # An accepted proposal pointing at that target.
    proposal_id = "e2e-open-proposal"
    (arch / "governance" / "proposals" / f"{proposal_id}.md").write_text(
        "---\n"
        f"id: {proposal_id}\n"
        "status: accepted\n"
        "pattern_id: e2e-demo-recurring\n"
        f"target_file: {target_file}\n"
        "proposed_change: |\n"
        "  Add a clarifying note that the e2e pipeline appended this section.\n"
        "  A reviewer should refine the wording before merge.\n"
        "rationale: |\n"
        "  Pattern 'e2e-demo-recurring' detected 8 times, above the threshold of 3.\n"
        "created_at: 2026-05-30\n"
        "---\n\n"
        "# Proposal — e2e-demo-recurring\n\n"
        "## 5. Resolution\n\n"
        "**Status:** accepted\n",
        encoding="utf-8",
    )

    # Minimal proposals index row that _update_index_status can rewrite to applied.
    (arch / "governance" / "proposals" / "index.md").write_text(
        "# Proposals index\n\n"
        "| Date | Proposal | Pattern | Severity | Status |\n"
        "|------|----------|---------|----------|--------|\n"
        f"| 2026-05-30 | [{proposal_id}]({proposal_id}.md) | e2e-demo-recurring | warn | accepted |\n",
        encoding="utf-8",
    )

    # Stub audit.py — the audit gate. Prints PASS and exits 0.
    (arch / "sdk" / "audit.py").write_text(
        "import sys\n"
        "print('[audit] mini-arch stub')\n"
        "print('AUDIT RESULT: PASS (0 errors)')\n"
        "sys.exit(0)\n",
        encoding="utf-8",
    )

    # Stub test — the pytest gate. Passes or fails on demand.
    if stub_tests_pass:
        body = "def test_mini_arch_ok():\n    assert True\n"
    else:
        body = (
            "def test_mini_arch_forced_failure():\n"
            "    # Deliberately fails so the post-apply verification gate is RED,\n"
            "    # forcing proposal_apply to roll the change back (block-155 rollback path).\n"
            "    assert False, 'forced e2e rollback'\n"
        )
    (arch / "sdk" / "tests" / "test_stub.py").write_text(body, encoding="utf-8")

    return arch, proposal_id, target_file


# A clearly-marked appended section the apply engine writes (block-152 render).
_APPENDED_HEADING = "Note (from proposal e2e-open-proposal)"
_APPENDED_BODY = "Add a clarifying note that the e2e pipeline appended this section."


# ===========================================================================
# 1. END-TO-END APPLY PATH (synthetic arch, REAL verification subprocess)
# ===========================================================================

class TestEndToEndApply:
    """Drive an accepted proposal against a non-immutable target all the way
    through apply, with the GENUINE pytest+audit subprocess as the gate."""

    @pytest.fixture(scope="class")
    def applied(self, tmp_path_factory):
        # Built once for the class: a real apply through the real verifier is a
        # subprocess (pytest + audit), so we pay that cost a single time and make
        # the individual assertions cheap.
        tmp_path = tmp_path_factory.mktemp("e2e_apply")
        arch, proposal_id, target_file = _build_mini_arch(tmp_path, stub_tests_pass=True)
        before = (arch / target_file).read_bytes()
        result = apply_proposal(proposal_id, arch, confirm=True)
        return {
            "arch": arch,
            "proposal_id": proposal_id,
            "target_file": target_file,
            "before": before,
            "result": result,
        }

    def test_apply_reports_applied_true(self, applied):
        result: ApplyResult = applied["result"]
        assert isinstance(result, ApplyResult)
        assert result.applied is True, f"expected applied; reasons={result.reasons}"
        assert result.rolled_back is False
        assert result.tests_passed is True
        assert result.target_file == applied["target_file"]

    def test_target_contains_appended_section(self, applied):
        body = (applied["arch"] / applied["target_file"]).read_text(encoding="utf-8")
        # Original content preserved...
        assert "# E2E Note Target" in body
        assert "title: E2E Note Target" in body  # frontmatter intact
        # ...and the reviewable section was appended.
        assert _APPENDED_HEADING in body
        assert _APPENDED_BODY in body
        assert "<!-- pattern: e2e-demo-recurring -->" in body

    def test_backup_created_byte_identical_to_pre_apply(self, applied):
        result: ApplyResult = applied["result"]
        assert result.backup_path.startswith("_backups/")
        assert result.backup_path.endswith(".bak")
        backup = applied["arch"] / result.backup_path
        assert backup.exists()
        # The backup captures the PRE-apply original, byte for byte.
        assert backup.read_bytes() == applied["before"]

    def test_proposal_marked_applied(self, applied):
        arch = applied["arch"]
        ptext = (arch / "governance" / "proposals" / "e2e-open-proposal.md").read_text(encoding="utf-8")
        assert "status: applied" in ptext
        assert "**Status:** applied" in ptext
        # The index row flipped too.
        itext = (arch / "governance" / "proposals" / "index.md").read_text(encoding="utf-8")
        assert "| applied |" in itext

    def test_governor_log_got_apply_block(self, applied):
        log = (applied["arch"] / "governance" / "governor-log.md").read_text(encoding="utf-8")
        assert "APPLY APPLIED" in log
        assert "proposal: e2e-open-proposal" in log
        assert f"file: {applied['target_file']}" in log

    def test_adr_stub_written(self, applied):
        arch = applied["arch"]
        adrs = list((arch / "decisions").glob("ADR-*-apply-*.md"))
        assert len(adrs) == 1, f"expected exactly one ADR stub, found {adrs}"
        adr_text = adrs[0].read_text(encoding="utf-8")
        assert "status: accepted" in adr_text
        assert "context_phase: phase-27" in adr_text
        assert "e2e-open-proposal" in adr_text
        # The result reasons advertise the ADR write.
        result: ApplyResult = applied["result"]
        assert any("ADR stub written" in r for r in result.reasons)

    def test_real_verification_subprocess_actually_ran(self, applied):
        # Proof the genuine gate ran (not a monkeypatch): applied=True is only
        # reachable when the REAL `pytest sdk/tests/` + `audit.py` subprocesses
        # both returned green, and the success reason records that gate explicitly.
        # (On success the per-command pass lines are summarized into this line;
        # they surface verbatim only on the rollback path, asserted there.)
        joined = " ".join(applied["result"].reasons).lower()
        assert "verified by pytest + audit" in joined


# ===========================================================================
# 2. END-TO-END ROLLBACK PATH (synthetic arch, REAL failing verification)
# ===========================================================================

class TestEndToEndRollback:
    """Same pipeline, but the stub test FAILS, so the genuine post-apply
    verification is RED and the engine must roll the write back."""

    @pytest.fixture(scope="class")
    def rolled(self, tmp_path_factory):
        tmp_path = tmp_path_factory.mktemp("e2e_rollback")
        arch, proposal_id, target_file = _build_mini_arch(tmp_path, stub_tests_pass=False)
        before = (arch / target_file).read_bytes()
        result = apply_proposal(proposal_id, arch, confirm=True)
        return {
            "arch": arch,
            "proposal_id": proposal_id,
            "target_file": target_file,
            "before": before,
            "result": result,
        }

    def test_rollback_reports_not_applied(self, rolled):
        result: ApplyResult = rolled["result"]
        assert isinstance(result, ApplyResult)
        assert result.applied is False, f"expected NOT applied; reasons={result.reasons}"
        assert result.rolled_back is True
        assert result.tests_passed is False

    def test_target_restored_byte_identical(self, rolled):
        after = (rolled["arch"] / rolled["target_file"]).read_bytes()
        assert after == rolled["before"], "target must be restored byte-for-byte"

    def test_proposal_still_accepted(self, rolled):
        ptext = (rolled["arch"] / "governance" / "proposals" / "e2e-open-proposal.md").read_text(encoding="utf-8")
        assert "status: applied" not in ptext
        assert "status: accepted" in ptext  # unchanged by the failed apply

    def test_no_adr_written_on_rollback(self, rolled):
        decisions = rolled["arch"] / "decisions"
        adrs = list(decisions.glob("ADR-*-apply-*.md")) if decisions.exists() else []
        assert adrs == []

    def test_backup_retained_after_rollback(self, rolled):
        result: ApplyResult = rolled["result"]
        backup = rolled["arch"] / result.backup_path
        assert backup.exists()
        # Retained backup equals the pre-apply original.
        assert backup.read_bytes() == rolled["before"]

    def test_rollback_reason_mentions_restore(self, rolled):
        joined = " ".join(rolled["result"].reasons).lower()
        assert "rolled back" in joined
        assert "restored byte-identical" in joined

    def test_real_failing_verification_subprocess_ran(self, rolled):
        # On the rollback path the genuine per-command verify reasons ARE surfaced;
        # the real `pytest sdk/tests/` against the failing stub reports a failure,
        # proving the gate was the real subprocess (not a monkeypatch).
        joined = " ".join(rolled["result"].reasons).lower()
        assert "post-apply verification failed" in joined
        assert "pytest" in joined and "failed" in joined


# ===========================================================================
# 3. REAL-REPO IMMUTABLE REFUSAL REGRESSION (read-only; zero writes)
# ===========================================================================

class TestRealRepoImmutableRefusal:
    """The two repo-accepted proposals both target IMMUTABLE files. Guard layer
    must refuse, and a confirm=True apply must leave the real file untouched."""

    def test_scope_expansion_guard_refuses_immutable(self):
        guard = check_guards(_REAL_IMMUTABLE_SCOPE, REAL_ROOT)
        assert isinstance(guard, GuardResult)
        assert guard.allowed is False
        assert guard.target_file == _REAL_IMMUTABLE_SCOPE_FILE
        assert any("immutability guard" in r for r in guard.reasons)

    def test_gate_failures_guard_refuses_immutable(self):
        guard = check_guards(_REAL_IMMUTABLE_GATES, REAL_ROOT)
        assert guard.allowed is False
        assert guard.target_file == "protocols/block-close-checklist.md"
        assert any("immutability guard" in r for r in guard.reasons)

    def test_confirm_apply_on_immutable_writes_nothing(self):
        # The strongest regression: confirm=True on the real immutable proposal
        # must be refused at the guard with the real target left byte-identical.
        target = REAL_ROOT / _REAL_IMMUTABLE_SCOPE_FILE
        before = target.read_bytes()
        backups_existed = (REAL_ROOT / "_backups").exists()

        result = apply_proposal(_REAL_IMMUTABLE_SCOPE, REAL_ROOT, confirm=True)

        assert result.applied is False
        assert result.rolled_back is False  # refused BEFORE any write -> nothing to roll back
        assert result.backup_path == ""     # no backup taken (no write attempted)
        assert any("immutability guard" in r for r in result.reasons)
        # The real immutable file is byte-identical; no _backups/ was created.
        assert target.read_bytes() == before
        assert (REAL_ROOT / "_backups").exists() == backups_existed


# ===========================================================================
# 4. REAL-REPO NON-IMMUTABLE GUARD CHECK (read-only; immutability does NOT block)
# ===========================================================================

class TestRealRepoNonImmutableGuard:
    """A proposal whose target is the NON-immutable block-complexity-estimator.md.
    The immutability guard must NOT be the thing that blocks it (it is refused for
    being rejected/not-accepted instead). Done WITHOUT applying."""

    def test_target_is_not_immutable(self):
        # Proves the immutability guard could not fire for this target.
        assert _is_immutable(_REAL_NONIMMUTABLE_TARGET, REAL_ROOT) is False

    def test_guard_refuses_for_acceptance_not_immutability(self):
        guard = check_guards(_REAL_NONIMMUTABLE_REJECTED, REAL_ROOT)
        assert guard.allowed is False  # it IS refused...
        assert guard.target_file == _REAL_NONIMMUTABLE_TARGET
        joined = " ".join(guard.reasons)
        # ...but for ACCEPTANCE (status rejected/not-accepted), NOT immutability.
        assert "acceptance guard" in joined
        assert "immutability guard" not in joined

    def test_real_nonimmutable_target_untouched_by_guard_check(self):
        # check_guards is evaluate-only: the real file is byte-identical, no _backups/.
        target = REAL_ROOT / _REAL_NONIMMUTABLE_TARGET
        before = target.read_bytes()
        backups_existed = (REAL_ROOT / "_backups").exists()

        check_guards(_REAL_NONIMMUTABLE_REJECTED, REAL_ROOT)

        assert target.read_bytes() == before
        assert (REAL_ROOT / "_backups").exists() == backups_existed


# ===========================================================================
# 5. REAL-REPO HYGIENE — no stray backup/temp artifacts after the suite
# ===========================================================================

class TestRealRepoHygiene:
    """The whole point of block-155's safety constraint: after exercising the
    pipeline, the REAL repo must carry zero apply byproducts."""

    def test_no_stray_backups_dir(self):
        backups = list(REAL_ROOT.rglob("_backups"))
        assert backups == [], f"unexpected _backups/ in the real repo: {backups}"

    def test_no_stray_apply_or_restore_tmp(self):
        apply_tmps = list(REAL_ROOT.rglob("*.apply.tmp"))
        restore_tmps = list(REAL_ROOT.rglob("*.restore.tmp"))
        assert apply_tmps == [], f"stray *.apply.tmp left behind: {apply_tmps}"
        assert restore_tmps == [], f"stray *.restore.tmp left behind: {restore_tmps}"


# ===========================================================================
# 6. DETERMINISTIC MIRRORS (monkeypatched verifier) — fast, no subprocess
#
# The class-scoped e2e tests above pay a real pytest+audit subprocess. These
# mirror the apply/rollback outcomes deterministically (the established block-154
# convention) so a CI failure can be localized to either the pipeline logic
# (these) or the real verification wiring (the e2e classes above).
# ===========================================================================

def _patch_verify(monkeypatch, *, ok: bool) -> None:
    reason = "pytest: passed (exit 0)." if ok else "pytest: FAILED (exit 1); last line: 1 failed"
    monkeypatch.setattr(ProposalApply, "_run_verification", lambda self: (ok, [reason]))


class TestDeterministicMirror:
    def test_apply_path_with_patched_verifier(self, tmp_path, monkeypatch):
        arch, proposal_id, target_file = _build_mini_arch(tmp_path, stub_tests_pass=True)
        _patch_verify(monkeypatch, ok=True)

        result = apply_proposal(proposal_id, arch, confirm=True)

        assert result.applied is True
        assert result.rolled_back is False
        assert _APPENDED_HEADING in (arch / target_file).read_text(encoding="utf-8")
        assert (arch / "decisions").exists()

    def test_rollback_path_with_patched_verifier(self, tmp_path, monkeypatch):
        arch, proposal_id, target_file = _build_mini_arch(tmp_path, stub_tests_pass=True)
        before = (arch / target_file).read_bytes()
        _patch_verify(monkeypatch, ok=False)  # force the gate RED

        result = apply_proposal(proposal_id, arch, confirm=True)

        assert result.applied is False
        assert result.rolled_back is True
        assert (arch / target_file).read_bytes() == before  # byte-identical restore
        decisions = arch / "decisions"
        assert not (decisions.exists() and list(decisions.glob("ADR-*-apply-*.md")))


# ---------------------------------------------------------------------------
# Helper for block-158 unit tests (no real verification subprocess needed)
# ---------------------------------------------------------------------------

def _setup_minimal_arch(tmp_path: Path) -> Path:
    """Create the minimum directory structure ProposalApply needs for guard/mark tests.

    Returns tmp_path (the arch root).  Does NOT create sdk/tests/ or audit.py
    because these tests never reach _run_verification.
    """
    (tmp_path / "governance" / "proposals").mkdir(parents=True, exist_ok=True)
    (tmp_path / "PROTOCOLS.md").write_text(
        "# PROTOCOLS\n\nMinimal stub. No immutable files declared.\n",
        encoding="utf-8",
    )
    return tmp_path


# --- block-158 tests ---------------------------------------------------------

def test_apply_refused_for_non_utf8_target(tmp_path):
    """Apply must be refused (not corrupting) when target contains non-UTF-8 bytes."""
    _setup_minimal_arch(tmp_path)
    # Create a target with valid cp1252 bytes that are invalid UTF-8
    target = tmp_path / "protocols" / "open.md"
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(b"# caf\xe9\n\nsome content.\n")  # 0xE9 = cp1252 e-acute
    # Create a minimal accepted proposal targeting it
    (tmp_path / "governance" / "proposals").mkdir(parents=True, exist_ok=True)
    (tmp_path / "governance" / "proposals" / "p-cp1252.md").write_text(
        "---\nid: p-cp1252\nstatus: accepted\ntarget_file: protocols/open.md\n---\n\n"
        "## Proposed Change\n\nAdd a note.\n"
    )
    idx = tmp_path / "governance" / "proposals" / "index.md"
    idx.write_text("| p-cp1252 | protocols/open.md | accepted |\n")
    pa = ProposalApply(tmp_path)
    result = pa.apply("p-cp1252", confirm=True)
    assert result.applied is False
    assert result.rolled_back is False  # not even attempted
    assert any("UTF-8" in r or "utf-8" in r for r in result.reasons)
    # Original file must be byte-identical (not corrupted)
    assert target.read_bytes() == b"# caf\xe9\n\nsome content.\n"


def test_mark_proposal_applied_only_first_status_line(tmp_path):
    """_mark_proposal_applied must only rewrite the first **Status:** line."""
    _setup_minimal_arch(tmp_path)
    (tmp_path / "governance" / "proposals").mkdir(parents=True, exist_ok=True)
    prop = tmp_path / "governance" / "proposals" / "p-test.md"
    prop.write_text(
        "---\nid: p-test\nstatus: accepted\ntarget_file: dummy.md\n---\n\n"
        "**Status:** accepted\n\n"
        "> Example: **Status:** pending (this must NOT change)\n"
    )
    (tmp_path / "governance" / "proposals" / "index.md").write_text(
        "| p-test | dummy.md | accepted |\n"
    )
    pa = ProposalApply(tmp_path)
    pa._mark_proposal_applied("p-test")
    text = prop.read_text()
    lines_with_status = [l for l in text.splitlines() if "**Status:**" in l]
    # The resolution line should be applied
    assert any("applied" in l for l in lines_with_status)
    # The quoted example line must still say "pending"
    assert any("pending" in l for l in lines_with_status)
