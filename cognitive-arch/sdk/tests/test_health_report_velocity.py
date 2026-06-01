# PURPOSE: Regression tests — velocity section must surface >=40 MEASURED samples
#          on the real arch-root via the manifest-tier fallback (was 25 pre-fix).
# INPUTS:  the real arch-root + synthetic retros for the fallback unit test
# OUTPUTS: assertions on _collect_velocity_data, MEASURED/ESTIMATED labels in render
# DEPS:    pytest, pathlib, health_report, project_state
# SEE:     sdk/health_report.py, blocks/block-086-velocity-activation.md, phases/phase-23.md block-138

import re
import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import health_report
import project_state

_ARCH_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Real arch-root: manifest-tier fallback recovers the 086-111 cohort
# ---------------------------------------------------------------------------

def test_velocity_surfaces_many_measured_samples():
    # Pre-fix: 25 measured (12 S + 13 M). Post-fix: ~48 (the 086-111 retros
    # carry actual_duration_hours but no `tier:`, so they were silently dropped).
    ids = project_state.completed_block_ids(_ARCH_ROOT)
    by_tier = health_report._collect_velocity_data(_ARCH_ROOT, ids)
    total = sum(len(v) for v in by_tier.values())
    assert total >= 40, (
        f"velocity collector should surface >=40 samples post-fix; got {total} "
        f"(S={len(by_tier['S'])} M={len(by_tier['M'])} L={len(by_tier['L'])})"
    )


def test_velocity_section_has_measured_label():
    ids = project_state.completed_block_ids(_ARCH_ROOT)
    section, _ = health_report._section_velocity(_ARCH_ROOT, ids)
    assert "MEASURED" in section, f"missing MEASURED label:\n{section}"
    # block-173/174: with enough real history all tiers may be MEASURED (that's correct behavior)
    # Test only requires at least one MEASURED label; ESTIMATED/INSUFFICIENT are acceptable but not required
    assert "MEASURED" in section or "ESTIMATED" in section or "INSUFFICIENT" in section, (
        f"missing any confidence label:\n{section}"
    )


def test_velocity_section_has_source_column_header():
    ids = project_state.completed_block_ids(_ARCH_ROOT)
    section, _ = health_report._section_velocity(_ARCH_ROOT, ids)
    assert "Source" in section, f"missing Source column header:\n{section}"


# ---------------------------------------------------------------------------
# Synthetic fixture: tier-less retro is recovered from the manifest
# ---------------------------------------------------------------------------

def _write_retro_and_manifest(
    arch: Path, block_id: str, tier_in_retro: str, tier_in_manifest: str, dur: float
):
    (arch / "blocks").mkdir(exist_ok=True)
    (arch / "manifests").mkdir(exist_ok=True)
    retro = arch / "blocks" / f"{block_id}-test.md"
    retro_fm = ["---", f"id: {block_id}", "status: done"]
    if tier_in_retro:
        retro_fm.append(f"tier: {tier_in_retro}")
    retro_fm += [f"actual_duration_hours: {dur}", "---", "", "# retro body"]
    retro.write_text("\n".join(retro_fm), encoding="utf-8")
    manifest = arch / "manifests" / f"{block_id}-test.md"
    manifest.write_text(
        f"---\nid: {block_id}\ntier: {tier_in_manifest}\nstatus: done\n---\n",
        encoding="utf-8",
    )


def test_manifest_tier_fallback_recovers_tier_less_retro(tmp_path: Path):
    _write_retro_and_manifest(tmp_path, "block-900", "", "L", 8.5)
    by_tier = health_report._collect_velocity_data(tmp_path, ["block-900"])
    assert by_tier["L"] == [8.5], (
        f"expected fallback to read tier L from manifest, got {by_tier}"
    )


def test_retro_tier_wins_over_manifest_tier(tmp_path: Path):
    # If both set tier, retro is the source of truth.
    _write_retro_and_manifest(tmp_path, "block-901", "S", "L", 0.5)
    by_tier = health_report._collect_velocity_data(tmp_path, ["block-901"])
    assert by_tier["S"] == [0.5] and by_tier["L"] == [], (
        f"expected retro tier S to win, got {by_tier}"
    )


def test_no_manifest_no_retro_tier_silently_drops(tmp_path: Path):
    # Tier-less retro AND no manifest → drop (can't infer).
    (tmp_path / "blocks").mkdir()
    retro = tmp_path / "blocks" / "block-902-test.md"
    retro.write_text(
        "---\nid: block-902\nstatus: done\nactual_duration_hours: 2.0\n---\n",
        encoding="utf-8",
    )
    by_tier = health_report._collect_velocity_data(tmp_path, ["block-902"])
    assert by_tier == {"S": [], "M": [], "L": []}
