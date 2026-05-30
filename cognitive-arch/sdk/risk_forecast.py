# PURPOSE: Forward-looking risk forecaster -- read a manifest at block-start and flag
#          resemblance to known-bad clusters via >=3 heuristics. Advisory ONLY: returns
#          flags, never raises, never blocks, always exits 0.
# INPUTS:  a manifest path (CLI positional) OR --block-id, plus --arch-root.
# OUTPUTS: list[RiskFlag]; CLI prints a verdict (LOW/ELEVATED) + per-heuristic rationale.
# DEPS:    stdlib only (re, argparse, pathlib) + safe_io; reuses velocity_inference
#          (tier/files parsing) and pattern_analyzer/retro_signals (live cluster evidence).
# SEE:     phases/phase-26.md sec.2 (forward-looking signals), manifests/block-150-risk-forecast.md,
#          sdk/pattern_analyzer.py (R4 scope-expansion, R7 l-tier-overrun), sdk/velocity_inference.py

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from safe_io import force_utf8
import velocity_inference as vi

# Tier file-count ceilings. M==8 is documented in templates/manifest-medium.md
# ("total modify + create <= 8 paths"); S/L bracket it.
TIER_CEILING = {"S": 4, "M": 8, "L": 20}

# H1 "near the ceiling" trigger: a modify+create list this large resembles the
# scope-expansion cluster even before it overflows the tier budget.
HIGH_FILE_COUNT = 7

# Historical scope-expansion cluster -- the blocks whose retros seeded R4
# (scope-expansion-recurring) in pattern_analyzer. A new block sharing this id
# space resembles a known-bad cluster. (manifests/block-150 sec.4 / pattern_analyzer R4.)
SCOPE_EXPANSION_CLUSTER = frozenset(
    [f"block-{n:03d}" for n in range(52, 58)] + ["block-086", "block-094", "block-097"]
)


@dataclass
class RiskFlag:
    """One heuristic's verdict for a block at start.

    `fired` is the advisory signal; `severity` ranks a fired flag
    ('low'|'med'|'high'); `rationale` cites the evidence so a human can dismiss
    it in seconds. An unfired flag (fired=False) records *why* the heuristic
    could not or did not trigger and is omitted from `assess`'s result.
    """

    heuristic: str
    severity: str          # 'low' | 'med' | 'high' (meaningful only when fired)
    rationale: str         # cites evidence (file count, cluster blocks, tier budget)
    fired: bool = True


# ---------------------------------------------------------------------------
# Live cluster evidence (reused from pattern_analyzer / velocity_inference) --
# each loader degrades to an empty result and NEVER raises.
# ---------------------------------------------------------------------------

def _live_patterns(arch_root: Path) -> list:
    """Run the existing pattern pipeline over real retros; [] on any failure.

    Reuses pattern_analyzer R1-R7 rather than re-deriving cluster membership.
    """
    try:
        from retro_signals import extract_all
        from pattern_analyzer import analyze
        return analyze(extract_all(arch_root), window_size=None)
    except Exception:
        return []


def _pattern_evidence(patterns: list, rule_id: str) -> list[str]:
    """Evidence block-ids for the first pattern matching rule_id, else []."""
    for p in patterns:
        if getattr(p, "rule_id", None) == rule_id:
            return list(getattr(p, "evidence", []) or [])
    return []


def _files_for_block(block_id: str, arch_root: Path) -> set[str]:
    """modify+create files declared by a block's manifest (reuses vi helpers); set()."""
    try:
        mp = vi._locate_manifest(block_id, arch_root)
        if mp is None:
            return set()
        return set(vi._files_from_manifest(mp))
    except Exception:
        return set()


# ---------------------------------------------------------------------------
# Heuristics -- each returns a single RiskFlag (fired or not). Each is wrapped so
# a malformed manifest yields an unfired "could not evaluate" flag, never a raise.
# ---------------------------------------------------------------------------

def _h1_scope_expansion(
    block_id: Optional[str], files: list[str], arch_root: Path, patterns: list
) -> RiskFlag:
    """H1: resemblance to the scope-expansion cluster (R4)."""
    name = "scope-expansion-resemblance"
    count = len(files)
    reasons: list[str] = []

    if count >= HIGH_FILE_COUNT:
        reasons.append(
            f"high file count ({count} modify+create, near the tier-M <=8 ceiling)"
        )

    if block_id and block_id in SCOPE_EXPANSION_CLUSTER:
        reasons.append(f"{block_id} is in the historical scope-expansion cluster")

    # Shares >=2 files with any manifest already in R4's live evidence set.
    overlap_blocks: list[str] = []
    overlap_files: set[str] = set()
    fileset = set(files)
    if fileset:
        for ev_bid in _pattern_evidence(patterns, "R4"):
            if ev_bid == block_id:
                continue
            shared = fileset & _files_for_block(ev_bid, arch_root)
            if len(shared) >= 2:
                overlap_blocks.append(ev_bid)
                overlap_files |= shared
    if overlap_blocks:
        reasons.append(
            "shares files "
            + ", ".join(sorted(overlap_files))
            + " with scope-expansion-recurring block(s) "
            + ", ".join(overlap_blocks)
        )

    if reasons:
        severity = "high" if count >= HIGH_FILE_COUNT else "med"
        return RiskFlag(
            heuristic=name,
            severity=severity,
            rationale="high file count -> Q6 scope-expansion risk: " + "; ".join(reasons),
            fired=True,
        )
    return RiskFlag(
        heuristic=name,
        severity="low",
        rationale=f"{count} modify+create files; no scope-expansion-cluster resemblance.",
        fired=False,
    )


def _h2_l_tier_overrun(tier: str, patterns: list) -> RiskFlag:
    """H2: tier L + active l-tier-systematic-overrun history (R7)."""
    name = "l-tier-overrun-history"
    if tier != "L":
        return RiskFlag(
            heuristic=name,
            severity="low",
            rationale=f"tier {tier} is not L; L-tier overrun heuristic N/A.",
            fired=False,
        )
    l_overruns = _pattern_evidence(patterns, "R7")
    if l_overruns:
        return RiskFlag(
            heuristic=name,
            severity="high",
            rationale=(
                "tier L and l-tier-systematic-overrun is active in history: prior "
                "L-tier blocks "
                + ", ".join(l_overruns)
                + " exceeded 1.5x their estimate; L-tier estimates run hot "
                "(velocity_inference TIER_ESTIMATES['L']=7.0h)."
            ),
            fired=True,
        )
    # Tier L but history is thin -- MEASURED/ESTIMATED discipline: do not overclaim.
    return RiskFlag(
        heuristic=name,
        severity="low",
        rationale=(
            "tier L, but no l-tier-systematic-overrun pattern in history yet "
            "(not enough measured L-tier overruns to forecast)."
        ),
        fired=False,
    )


def _h3_oversized_modify(tier: str, files: list[str]) -> RiskFlag:
    """H3: modify+create total exceeds the tier file-count ceiling."""
    name = "oversized-modify-list"
    count = len(files)
    ceiling = TIER_CEILING.get(tier, TIER_CEILING["M"])
    if count > ceiling:
        return RiskFlag(
            heuristic=name,
            severity="high" if count > ceiling + 2 else "med",
            rationale=(
                f"{count} modify+create files exceed the tier-{tier} budget of "
                f"{ceiling}; consider splitting the block."
            ),
            fired=True,
        )
    return RiskFlag(
        heuristic=name,
        severity="low",
        rationale=f"{count} modify+create files within the tier-{tier} budget of {ceiling}.",
        fired=False,
    )


def _h4_immutable_touch(files: list[str], arch_root: Path) -> RiskFlag:
    """H4: the block modifies files protected as immutable (a HOT/locked surface)."""
    name = "immutable-file-touch"
    hits: list[str] = []
    for rel in files:
        try:
            p = arch_root / rel
            if not vi._is_real_file(p):
                continue
            head = p.read_text(encoding="utf-8", errors="ignore")[:600]
            if re.search(r"^\s*protection:\s*immutable", head, re.MULTILINE):
                hits.append(rel)
        except Exception:
            continue
    if hits:
        return RiskFlag(
            heuristic=name,
            severity="high",
            rationale=(
                "touches immutable file(s) "
                + ", ".join(hits)
                + " -- requires a recorded version bump; high regression/lock risk."
            ),
            fired=True,
        )
    return RiskFlag(
        heuristic=name,
        severity="low",
        rationale="no immutable/locked files in the modify+create list.",
        fired=False,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def assess(manifest_path, arch_root) -> list[RiskFlag]:
    """Advisory risk assessment for a manifest at block-start.

    Returns the list of *fired* RiskFlags (empty == no risk flagged). NEVER
    raises and NEVER blocks -- every heuristic is guarded so a malformed or
    missing manifest yields no fired flags rather than an exception (Phase 26
    sec.3/sec.5; mirrors pattern_analyzer.analyze()).
    """
    try:
        manifest_path = Path(manifest_path) if manifest_path is not None else None
    except Exception:
        manifest_path = None
    try:
        arch_root = Path(arch_root)
    except Exception:
        arch_root = Path(".")

    # Parse manifest shape via the reused velocity_inference helpers (each is
    # already guarded against empty/missing paths and never raises).
    try:
        files = vi._files_from_manifest(manifest_path) if manifest_path else []
    except Exception:
        files = []
    try:
        tier = vi._tier_from_manifest(manifest_path) if manifest_path else "M"
    except Exception:
        tier = "M"

    block_id: Optional[str] = None
    if manifest_path is not None:
        m = re.match(r"(block-\d+)", manifest_path.name)
        if m:
            block_id = m.group(1)

    patterns = _live_patterns(arch_root)

    flags: list[RiskFlag] = []
    for fn in (
        lambda: _h1_scope_expansion(block_id, files, arch_root, patterns),
        lambda: _h2_l_tier_overrun(tier, patterns),
        lambda: _h3_oversized_modify(tier, files),
        lambda: _h4_immutable_touch(files, arch_root),
    ):
        try:
            flag = fn()
        except Exception as exc:  # advisory contract: degrade, never raise
            flag = RiskFlag(
                heuristic="heuristic-error",
                severity="low",
                rationale=f"could not evaluate ({type(exc).__name__}).",
                fired=False,
            )
        if flag.fired:
            flags.append(flag)
    return flags


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="risk_forecast",
        description="Flag block-start risk from a manifest (advisory; always exits 0).",
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        default=None,
        help="Path to the manifest to assess (e.g. manifests/block-150-risk-forecast.md).",
    )
    parser.add_argument(
        "--block-id",
        metavar="ID",
        default=None,
        help="Assess by block id (resolves manifests/<id>-*.md). Alternative to a path.",
    )
    parser.add_argument(
        "--arch-root",
        metavar="PATH",
        default=".",
        help="Path to the cognitive-arch root (default: current directory).",
    )
    return parser


def _resolve_manifest(args, arch_root: Path) -> Optional[Path]:
    """manifest positional wins; else resolve --block-id; else None."""
    if args.manifest:
        return Path(args.manifest)
    if args.block_id:
        try:
            return vi._locate_manifest(args.block_id, arch_root)
        except Exception:
            return None
    return None


def main(argv: Optional[list[str]] = None) -> int:
    force_utf8()
    args = build_parser().parse_args(argv)
    arch_root = Path(args.arch_root).resolve()
    manifest_path = _resolve_manifest(args, arch_root)

    label = args.manifest or args.block_id or "(no manifest given)"
    flags = assess(manifest_path, arch_root)

    verdict = "ELEVATED" if flags else "LOW"
    print(f"Risk forecast for {label}: {verdict}")
    if not flags:
        print("  no risks flagged")
    else:
        for f in flags:
            print(f"  [{f.severity.upper()}] {f.heuristic}: {f.rationale}")
    return 0  # advisory: ALWAYS exit 0


if __name__ == "__main__":
    sys.exit(main())
