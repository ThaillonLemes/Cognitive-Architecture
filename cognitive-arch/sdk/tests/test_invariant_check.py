# PURPOSE: Tests for sdk/invariant_check.py — each invariant fires-on-drift + clean-on-healthy.
# INPUTS:  tmp_path; synthetic arch roots (lock, BLOCK_LOG, retros, manifests, proposals, STATE/NEXT)
# OUTPUTS: assertions on run_all Violations + per-invariant check fns + never-raises guarantee
# DEPS:    pytest, pathlib, invariant_check + invariant_schema modules
# SEE:     sdk/invariant_check.py, sdk/invariant_schema.py, phases/phase-25.md block-144

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import invariant_check as ic
from invariant_schema import Invariant, Violation


# ---------------------------------------------------------------------------
# Builders — assemble a synthetic arch root piece by piece. Everything starts
# healthy; each test introduces exactly one drift.
# ---------------------------------------------------------------------------

def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _immutable_doc(name: str) -> str:
    return f"---\nid: {name}\nprotection: immutable\n---\n\n# {name}\n"


def _retro(block_id: str, *, tier: str | None = "M", hours: float | None = 2.0) -> str:
    lines = ["---", f"id: {block_id}", "status: done"]
    if tier is not None:
        lines.append(f"tier: {tier}")
    if hours is not None:
        lines.append(f"actual_duration_hours: {hours}")
    lines += ["---", "", f"# {block_id} retro", ""]
    return "\n".join(lines)


def _manifest(block_id: str, *, tier: str = "M") -> str:
    return f"---\nid: {block_id}\ntier: {tier}\n---\n\n# {block_id} manifest\n"


def healthy_arch(tmp_path: Path) -> Path:
    """A small but fully-consistent arch root: 2 done blocks, both with retros,
    a complete lock, consistent STATE/NEXT, one proposal indexed both ways."""
    root = tmp_path / "arch"

    # Immutable file + matching lock entry (INV1 clean) — use the real hash so
    # check_inv1's verify() pass also sees OK (not a fake that would MISMATCH).
    import integrity_check as _ic
    _write(root / "PROTOCOLS.md", _immutable_doc("PROTOCOLS"))
    _real_hash = _ic.sha256_of_file(root / "PROTOCOLS.md")
    _write(
        root / ".integrity.lock",
        "# lock\nPROTOCOLS.md  sha256:" + _real_hash + "\n",
    )

    # BLOCK_LOG with two done blocks (INV2/INV5 input).
    _write(
        root / "blocks" / "BLOCK_LOG.md",
        "# BLOCK_LOG\nblock-001 done - 2026-05-20\nblock-002 done - 2026-05-21\n",
    )
    # Retros for both (INV2 clean) with tier+duration (INV3 clean).
    _write(root / "blocks" / "block-001-alpha.md", _retro("block-001"))
    _write(root / "blocks" / "block-002-beta.md", _retro("block-002"))
    # Manifests (tier fallback source for INV3).
    _write(root / "manifests" / "block-001-alpha.md", _manifest("block-001"))
    _write(root / "manifests" / "block-002-beta.md", _manifest("block-002"))

    # tools-registry covering every real TOOL_RUNNERS key (INV4 clean).
    import session_start
    reg_lines = ["schema_version: \"1.0\"", "tools:"]
    for tid in session_start.TOOL_RUNNERS:
        reg_lines.append(f"  - id: {tid}")
        reg_lines.append("    name: \"x\"")
    _write(root / "governance" / "tools-registry.yaml", "\n".join(reg_lines) + "\n")

    # STATE/NEXT consistent (INV5 clean): last_block == highest done; next is unstarted.
    _write(root / "STATE.md", "# STATE\np:1 status:active last_block:block-002 next:block-003\n")
    _write(root / "NEXT.md", "# NEXT\nstatus:active next_action:block-003\n")

    # One proposal, indexed (INV6 clean).
    _write(
        root / "governance" / "proposals" / "2026-05-29-foo.md",
        "---\nstatus: pending\n---\n# foo\n",
    )
    _write(
        root / "governance" / "proposals" / "index.md",
        "# Proposals Index\n\n| Date | ID | Status |\n|------|----|--------|\n"
        "| 2026-05-29 | [foo](governance/proposals/2026-05-29-foo.md) | pending |\n",
    )
    return root


# ---------------------------------------------------------------------------
# Healthy baseline — no invariant fires on a consistent arch.
# ---------------------------------------------------------------------------

class TestHealthyBaseline:
    def test_run_all_clean_on_healthy(self, tmp_path):
        root = healthy_arch(tmp_path)
        violations = ic.run_all(root)
        assert violations == [], f"expected no violations, got {[v.message for v in violations]}"


# ---------------------------------------------------------------------------
# INV1 — immutable file missing from lock
# ---------------------------------------------------------------------------

class TestINV1:
    def test_fires_when_immutable_missing_from_lock(self, tmp_path):
        root = healthy_arch(tmp_path)
        # Add a second immutable file but do NOT add it to the lock.
        _write(root / "extra.md", _immutable_doc("extra"))
        msgs = ic.check_inv1(root)
        assert any("extra.md" in m for m in msgs)
        # And it surfaces as a CRITICAL violation via the engine.
        crit = [v for v in ic.run_all(root) if v.invariant_id == "INV1"]
        assert crit and all(v.severity == "critical" for v in crit)

    def test_clean_when_lock_complete(self, tmp_path):
        root = healthy_arch(tmp_path)
        assert ic.check_inv1(root) == []

    def test_fires_when_immutable_file_has_hash_mismatch(self, tmp_path):
        """INV1 must report a violation when an immutable file is in the lock but tampered."""
        import integrity_check as _ic
        root = healthy_arch(tmp_path)
        # Write a second immutable file with a real lock entry, then tamper it.
        _write(root / "extra.md", _immutable_doc("extra"))
        real_hash = _ic.sha256_of_file(root / "extra.md")
        lock_path = root / ".integrity.lock"
        # Append extra.md with its REAL hash to the lock.
        lock_path.write_text(
            lock_path.read_text(encoding="utf-8") + f"extra.md  sha256:{real_hash}\n",
            encoding="utf-8",
        )
        # Verify it is clean first.
        assert ic.check_inv1(root) == []
        # Now tamper the file — hash no longer matches.
        (root / "extra.md").write_text(_immutable_doc("extra") + "\ntampered\n", encoding="utf-8")
        msgs = ic.check_inv1(root)
        assert any("MISMATCH" in m and "extra.md" in m for m in msgs), (
            f"Expected a MISMATCH violation for extra.md; got: {msgs}"
        )
        # Surfaces as a CRITICAL violation via the engine.
        crit = [v for v in ic.run_all(root) if v.invariant_id == "INV1"]
        assert crit and all(v.severity == "critical" for v in crit)


# ---------------------------------------------------------------------------
# INV2 — done block with no retro
# ---------------------------------------------------------------------------

class TestINV2:
    def test_fires_when_retro_missing(self, tmp_path):
        root = healthy_arch(tmp_path)
        # Log a third done block with no retro file.
        log = root / "blocks" / "BLOCK_LOG.md"
        log.write_text(log.read_text(encoding="utf-8") + "block-003 done - 2026-05-22\n", encoding="utf-8")
        msgs = ic.check_inv2(root)
        assert any("block-003" in m for m in msgs)

    def test_clean_when_all_have_retros(self, tmp_path):
        root = healthy_arch(tmp_path)
        assert ic.check_inv2(root) == []


# ---------------------------------------------------------------------------
# INV3 — retro with duration but no resolvable tier
# ---------------------------------------------------------------------------

class TestINV3:
    def test_fires_when_tier_unresolvable(self, tmp_path):
        root = healthy_arch(tmp_path)
        # block-003: done + retro WITH duration but NO tier, and no manifest.
        log = root / "blocks" / "BLOCK_LOG.md"
        log.write_text(log.read_text(encoding="utf-8") + "block-003 done - 2026-05-22\n", encoding="utf-8")
        _write(root / "blocks" / "block-003-gamma.md", _retro("block-003", tier=None, hours=3.0))
        msgs = ic.check_inv3(root)
        assert any("block-003" in m for m in msgs)

    def test_clean_when_tier_from_manifest(self, tmp_path):
        root = healthy_arch(tmp_path)
        # retro without tier, but a manifest supplies it -> resolvable, no violation.
        log = root / "blocks" / "BLOCK_LOG.md"
        log.write_text(log.read_text(encoding="utf-8") + "block-003 done - 2026-05-22\n", encoding="utf-8")
        _write(root / "blocks" / "block-003-gamma.md", _retro("block-003", tier=None, hours=3.0))
        _write(root / "manifests" / "block-003-gamma.md", _manifest("block-003", tier="L"))
        assert ic.check_inv3(root) == []

    def test_clean_when_no_duration(self, tmp_path):
        root = healthy_arch(tmp_path)
        # retro with neither tier nor duration -> INV3 not applicable.
        log = root / "blocks" / "BLOCK_LOG.md"
        log.write_text(log.read_text(encoding="utf-8") + "block-003 done - 2026-05-22\n", encoding="utf-8")
        _write(root / "blocks" / "block-003-gamma.md", _retro("block-003", tier=None, hours=None))
        assert ic.check_inv3(root) == []


# ---------------------------------------------------------------------------
# INV4 — TOOL_RUNNERS key absent from registry
# ---------------------------------------------------------------------------

class TestINV4:
    def test_fires_when_runner_not_in_registry(self, tmp_path):
        root = healthy_arch(tmp_path)
        # Drop one runner id from the registry the healthy builder wrote.
        import session_start
        first_id = next(iter(session_start.TOOL_RUNNERS))
        reg = root / "governance" / "tools-registry.yaml"
        kept = [ln for ln in reg.read_text(encoding="utf-8").splitlines()
                if ln.strip() != f"- id: {first_id}"]
        reg.write_text("\n".join(kept) + "\n", encoding="utf-8")
        msgs = ic.check_inv4(root)
        assert any(first_id in m for m in msgs)
        crit = [v for v in ic.run_all(root) if v.invariant_id == "INV4"]
        assert crit and all(v.severity == "critical" for v in crit)

    def test_clean_when_all_runners_registered(self, tmp_path):
        root = healthy_arch(tmp_path)
        assert ic.check_inv4(root) == []


# ---------------------------------------------------------------------------
# INV5 — STATE/NEXT pointer drift
# ---------------------------------------------------------------------------

class TestINV5:
    def test_fires_when_last_block_stale(self, tmp_path):
        root = healthy_arch(tmp_path)
        # last_block points at block-001 but highest done is block-002.
        _write(root / "STATE.md", "# STATE\np:1 status:active last_block:block-001 next:block-003\n")
        msgs = ic.check_inv5(root)
        assert any("last_block" in m for m in msgs)

    def test_fires_when_next_points_at_done(self, tmp_path):
        root = healthy_arch(tmp_path)
        # next_action points at block-002 which is already done.
        _write(root / "NEXT.md", "# NEXT\nstatus:active next_action:block-002\n")
        msgs = ic.check_inv5(root)
        assert any("already 'done'" in m for m in msgs)

    def test_clean_when_pointers_consistent(self, tmp_path):
        root = healthy_arch(tmp_path)
        assert ic.check_inv5(root) == []


# ---------------------------------------------------------------------------
# INV6 — proposal file <-> index drift, both directions
# ---------------------------------------------------------------------------

class TestINV6:
    def test_fires_when_file_not_in_index(self, tmp_path):
        root = healthy_arch(tmp_path)
        # Add a proposal file with no index row.
        _write(root / "governance" / "proposals" / "2026-05-30-bar.md", "# bar\n")
        msgs = ic.check_inv6(root)
        assert any("2026-05-30-bar.md" in m and "no row" in m for m in msgs)

    def test_fires_when_index_references_missing_file(self, tmp_path):
        root = healthy_arch(tmp_path)
        idx = root / "governance" / "proposals" / "index.md"
        idx.write_text(
            idx.read_text(encoding="utf-8")
            + "| 2026-05-30 | [ghost](governance/proposals/2026-05-30-ghost.md) | pending |\n",
            encoding="utf-8",
        )
        msgs = ic.check_inv6(root)
        assert any("2026-05-30-ghost.md" in m and "missing" in m for m in msgs)

    def test_clean_when_reconciled(self, tmp_path):
        root = healthy_arch(tmp_path)
        assert ic.check_inv6(root) == []


# ---------------------------------------------------------------------------
# Engine resilience — never raises, even on garbage input.
# ---------------------------------------------------------------------------

class TestEngineNeverRaises:
    def test_empty_arch_does_not_raise(self, tmp_path):
        # Nothing on disk at all.
        violations = ic.run_all(tmp_path / "nonexistent")
        assert isinstance(violations, list)  # no exception, returns a list

    def test_malformed_files_do_not_raise(self, tmp_path):
        root = tmp_path / "broken"
        _write(root / ".integrity.lock", "@@@ not a lock @@@\n\x00\x01")
        _write(root / "blocks" / "BLOCK_LOG.md", "garbage block-XYZ done\n###")
        _write(root / "STATE.md", "no fields here")
        _write(root / "NEXT.md", "")
        _write(root / "governance" / "tools-registry.yaml", ": : : broken yaml")
        _write(root / "governance" / "proposals" / "index.md", "| | |")
        violations = ic.run_all(root)
        assert isinstance(violations, list)

    def test_failing_check_degrades_to_warn(self, tmp_path):
        """A check that raises becomes one warn Violation, never propagates."""
        def boom(_root):
            raise RuntimeError("kaboom")

        reg = [Invariant(id="INVX", description="always raises", severity="critical", check=boom)]
        violations = ic.run_all(tmp_path, registry=reg)
        assert len(violations) == 1
        v = violations[0]
        assert v.invariant_id == "INVX"
        assert v.severity == "warn"          # critical check that errors degrades to warn
        assert "check errored" in v.message

    def test_registry_has_at_least_six_invariants(self):
        assert len(ic.REGISTRY) >= 6
        ids = {inv.id for inv in ic.REGISTRY}
        assert {"INV1", "INV2", "INV3", "INV4", "INV5", "INV6"} <= ids

    def test_main_exits_zero_on_real_root(self, tmp_path):
        # CLI on a healthy synthetic root must exit 0 with no traceback.
        root = healthy_arch(tmp_path)
        assert ic.main(["--arch-root", str(root)]) == 0
