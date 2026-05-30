# sdk/pattern_analyzer.py
# PURPOSE: Detect recurring patterns across RetroSignal records using threshold-based rules.
# INPUTS:  list[RetroSignal] (from retro_signals.extract_all)
# OUTPUTS: list[Pattern]
# DEPS:    stdlib only, sdk/retro_signal_schema, sdk/pattern_schema
# SEE:     sdk/retro_signals.py, sdk/patterns_report.py, sdk/recommendation_engine.py

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Callable

from pattern_schema import Pattern
from retro_signal_schema import RetroSignal

# D1 threshold: pattern fires if occurrence count >= THRESHOLD within WINDOW_SIZE blocks
THRESHOLD = 3
WINDOW_SIZE = 30


def _window(signals: list[RetroSignal], size: int | None = WINDOW_SIZE) -> list[RetroSignal]:
    """Return the last `size` signals, or all if size is None.

    Returns [] for size <= 0 (not the full history).
    """
    if size is None:
        return signals
    if size <= 0:
        return []
    return signals[-size:] if len(signals) > size else signals


# ---------------------------------------------------------------------------
# Detection rules — each returns list[Pattern] (may be empty)
# ---------------------------------------------------------------------------

def _rule_axiom_violation(signals: list[RetroSignal]) -> list[Pattern]:
    """R1: Any axiom violated >= THRESHOLD times in window."""
    window = signals
    counts: dict[str, list[str]] = defaultdict(list)
    for s in window:
        for ax in s.axioms_violated:
            counts[ax].append(s.block_id)
    patterns = []
    for axiom, block_ids in counts.items():
        if len(block_ids) >= THRESHOLD:
            patterns.append(Pattern(
                name=f"axiom-{axiom.lower()}-repeated-violation",
                description=f"Axiom {axiom} violated in {len(block_ids)} of last {len(window)} blocks.",
                severity="warn",
                evidence=block_ids,
                first_detected=block_ids[0],
                last_detected=block_ids[-1],
                occurrences=len(block_ids),
                rule_id="R1",
            ))
    return patterns


def _rule_duration_overrun(signals: list[RetroSignal]) -> list[Pattern]:
    """R2: Blocks that took >1.5× their estimate, if >= THRESHOLD in window."""
    window = signals
    overruns = [s.block_id for s in window if s.over_estimate]
    if len(overruns) >= THRESHOLD:
        return [Pattern(
            name="duration-overrun-recurring",
            description=f"{len(overruns)} of last {len(window)} blocks exceeded 1.5× their duration estimate.",
            severity="warn",
            evidence=overruns,
            first_detected=overruns[0],
            last_detected=overruns[-1],
            occurrences=len(overruns),
            rule_id="R2",
        )]
    return []


def _rule_gate_failures(signals: list[RetroSignal]) -> list[Pattern]:
    """R3: Blocks with gate failures >= THRESHOLD in window."""
    window = signals
    failed = [s.block_id for s in window if s.gate_failures > 0]
    if len(failed) >= THRESHOLD:
        return [Pattern(
            name="gate-failures-recurring",
            description=f"{len(failed)} of last {len(window)} blocks had at least one gate failure.",
            severity="warn",
            evidence=failed,
            first_detected=failed[0],
            last_detected=failed[-1],
            occurrences=len(failed),
            rule_id="R3",
        )]
    return []


def _rule_scope_expansion(signals: list[RetroSignal]) -> list[Pattern]:
    """R4: Blocks with scope expansion >= THRESHOLD in window."""
    window = signals
    expanded = [s.block_id for s in window if s.scope_expansion]
    if len(expanded) >= THRESHOLD:
        return [Pattern(
            name="scope-expansion-recurring",
            description=f"{len(expanded)} of last {len(window)} blocks had files added beyond manifest.",
            severity="warn",
            evidence=expanded,
            first_detected=expanded[0],
            last_detected=expanded[-1],
            occurrences=len(expanded),
            rule_id="R4",
        )]
    return []


def _rule_forced_pass(signals: list[RetroSignal]) -> list[Pattern]:
    """R5: Forced passes >= THRESHOLD in window (always critical)."""
    window = signals
    forced = [s.block_id for s in window if s.forced_pass]
    if len(forced) >= THRESHOLD:
        return [Pattern(
            name="forced-pass-clustering",
            description=f"{len(forced)} of last {len(window)} blocks used force-pass on a gate.",
            severity="critical",
            evidence=forced,
            first_detected=forced[0],
            last_detected=forced[-1],
            occurrences=len(forced),
            rule_id="R5",
        )]
    return []


def _rule_missing_duration(signals: list[RetroSignal]) -> list[Pattern]:
    """R6: Blocks missing actual_duration_hours >= THRESHOLD in window (velocity data gap)."""
    window = signals
    missing = [s.block_id for s in window if s.duration_actual_h is None]
    if len(missing) >= THRESHOLD:
        return [Pattern(
            name="velocity-data-gap",
            description=f"{len(missing)} of last {len(window)} blocks are missing actual_duration_hours.",
            severity="info",
            evidence=missing,
            first_detected=missing[0],
            last_detected=missing[-1],
            occurrences=len(missing),
            rule_id="R6",
        )]
    return []


def _rule_tier_l_overrun(signals: list[RetroSignal]) -> list[Pattern]:
    """R7: L-tier blocks consistently overrun (any 2+ in window, lower threshold for severity)."""
    window = signals
    l_overruns = [s.block_id for s in window if s.tier == "L" and s.over_estimate]
    if len(l_overruns) >= 2:
        return [Pattern(
            name="l-tier-systematic-overrun",
            description=f"{len(l_overruns)} L-tier blocks exceeded 1.5× their duration estimate. L-tier estimates may need recalibration.",
            severity="warn",
            evidence=l_overruns,
            first_detected=l_overruns[0],
            last_detected=l_overruns[-1],
            occurrences=len(l_overruns),
            rule_id="R7",
        )]
    return []


# ---------------------------------------------------------------------------
# Token-based detection (Phase 18 — block-116)
# ---------------------------------------------------------------------------

def detect_budget_overrun(
    token_signals: list,
    threshold_pct: float = 20.0,
    d1_min: int = THRESHOLD,
) -> list[Pattern]:
    """R8: budget-overrun-recurring — token delta > threshold_pct in >= d1_min blocks."""
    overruns = [
        s.block_id for s in token_signals
        if s.delta_pct is not None and s.delta_pct > threshold_pct
    ]
    if len(overruns) >= d1_min:
        return [Pattern(
            name="budget-overrun-recurring",
            description=(
                f"tok_actual exceeded tok_estimated by >{threshold_pct:.0f}% "
                f"in {len(overruns)} blocks."
            ),
            severity="warn",
            evidence=overruns,
            first_detected=overruns[0],
            last_detected=overruns[-1],
            occurrences=len(overruns),
            rule_id="R8",
        )]
    return []


# ---------------------------------------------------------------------------
# Main analyzer
# ---------------------------------------------------------------------------

_RULES: list[Callable[[list[RetroSignal]], list[Pattern]]] = [
    _rule_axiom_violation,
    _rule_duration_overrun,
    _rule_gate_failures,
    _rule_scope_expansion,
    _rule_forced_pass,
    _rule_missing_duration,
    _rule_tier_l_overrun,
]


def analyze(
    signals: list[RetroSignal],
    window_size: int | None = WINDOW_SIZE,
) -> list[Pattern]:
    """Run all detection rules over a windowed view of `signals`.

    `window_size=None` disables windowing (full history); default keeps the
    last `WINDOW_SIZE` (30) signals for backwards compatibility.
    """
    window = _window(signals, window_size)
    patterns: list[Pattern] = []
    for rule in _RULES:
        try:
            patterns.extend(rule(window))
        except Exception:
            pass  # rule failure must never crash the pipeline
    return patterns


if __name__ == "__main__":
    import argparse
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from retro_signals import extract_all

    parser = argparse.ArgumentParser(description="Pattern analyzer for cognitive-arch")
    parser.add_argument("--arch-root", default=".", help="Root of the cognitive-arch directory")
    args = parser.parse_args()
    arch_root = Path(args.arch_root).resolve()
    if not arch_root.is_dir():
        print(f"ERROR: arch-root '{arch_root}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    signals = extract_all(arch_root)
    patterns = analyze(signals)
    print(f"Signals: {len(signals)} | Patterns detected: {len(patterns)}")
    for p in patterns:
        print(f"  [{p.severity.upper()}] {p.name}: {p.occurrences} occurrences in {p.evidence}")
