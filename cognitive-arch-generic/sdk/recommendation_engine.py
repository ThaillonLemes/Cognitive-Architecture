# sdk/recommendation_engine.py
# PURPOSE: Map Pattern records to Recommendation records using deterministic rules.
# INPUTS:  list[Pattern] from pattern_analyzer.analyze()
# OUTPUTS: list[Recommendation]; also populates Pattern.recommendation text
# DEPS:    stdlib only, sdk/pattern_schema, sdk/recommendation_schema
# SEE:     sdk/pattern_analyzer.py, sdk/patterns_report.py, sdk/master_scheduler.py

from __future__ import annotations

from pattern_schema import Pattern
from recommendation_schema import Recommendation

# ---------------------------------------------------------------------------
# Mapping rules — one function per rule ID
# ---------------------------------------------------------------------------

def _rec_r1(p: Pattern) -> Recommendation:
    ax = p.name.replace("axiom-", "").replace("-repeated-violation", "").upper()
    return Recommendation(
        pattern_name=p.name,
        title=f"Review axiom {ax} compliance",
        rationale=(
            f"Axiom {ax} was violated in {p.occurrences} of the last 30 blocks "
            f"(first: {p.first_detected}, last: {p.last_detected}). "
            "Repeated violations suggest the axiom is unclear or consistently skipped under pressure."
        ),
        priority="high" if p.occurrences >= 5 else "medium",
        suggested_action=(
            f"1. Read PROTOCOLS.md axiom {ax} and the ADR that introduced it. "
            "2. Check whether wording needs clarification (create an ADR if so). "
            "3. Add a block-start reminder or checklist item for this axiom."
        ),
        rule_id="R1",
    )


def _rec_r2(p: Pattern) -> Recommendation:
    return Recommendation(
        pattern_name=p.name,
        title="Recalibrate block duration estimates",
        rationale=(
            f"{p.occurrences} blocks in the last 30 exceeded 1.5× their duration estimate "
            f"(last: {p.last_detected}). Systematic overrun suggests estimate inflation or scope creep."
        ),
        priority="medium",
        suggested_action=(
            "1. Review last 5 overrun blocks — were estimates set before or after understanding scope? "
            "2. If estimates were pre-scope: add a scoping step to block-start. "
            "3. If scope grew during the block: check axiom Q6 (exhaustive file declaration) compliance."
        ),
        rule_id="R2",
    )


def _rec_r3(p: Pattern) -> Recommendation:
    return Recommendation(
        pattern_name=p.name,
        title="Investigate recurring gate failures",
        rationale=(
            f"{p.occurrences} blocks had gate failures in the last 30 "
            f"(last: {p.last_detected}). Recurring failures may indicate brittle gates or unclear acceptance criteria."
        ),
        priority="high",
        suggested_action=(
            "1. Read the retrospectives of the failing blocks — which gates failed? "
            "2. If the same gate fails repeatedly: revise its acceptance criteria or tooling. "
            "3. If different gates fail: the problem is implementation discipline, not gate design."
        ),
        rule_id="R3",
    )


def _rec_r4(p: Pattern) -> Recommendation:
    return Recommendation(
        pattern_name=p.name,
        title="Enforce manifest exhaustiveness (axiom Q6)",
        rationale=(
            f"{p.occurrences} blocks added files beyond what their manifest declared "
            f"(last: {p.last_detected}). Scope expansion is a Q6 violation."
        ),
        priority="medium",
        suggested_action=(
            "1. Add a block-start gate: 'has the manifest's files.modify list been finalized?' "
            "2. When a new file is needed mid-block: HALT and update the manifest before continuing. "
            "3. Consider adding a Q6 check to audit.sh that detects committed files not in manifest."
        ),
        rule_id="R4",
    )


def _rec_r5(p: Pattern) -> Recommendation:
    return Recommendation(
        pattern_name=p.name,
        title="Audit forced-pass usage — potential quality debt",
        rationale=(
            f"{p.occurrences} blocks used force-pass on a gate in the last 30 "
            f"(last: {p.last_detected}). Critical: force-pass bypasses the quality gate."
        ),
        priority="high",
        suggested_action=(
            "1. List all force-passed blocks and their gate IDs. "
            "2. For each: assess whether the underlying issue was resolved or deferred. "
            "3. Create follow-up blocks for any unresolved gate issues. "
            "4. If force-pass is being used for convenience (not necessity): add friction to the ceremony."
        ),
        rule_id="R5",
    )


def _rec_r6(p: Pattern) -> Recommendation:
    return Recommendation(
        pattern_name=p.name,
        title="Fill velocity data — actual_duration_hours missing",
        rationale=(
            f"{p.occurrences} recent blocks lack actual_duration_hours "
            f"(last: {p.last_detected}). Velocity metrics will be unreliable."
        ),
        priority="low",
        suggested_action=(
            "1. For future blocks: fill actual_duration_hours at block-close (block-close-checklist step 5). "
            "2. For recent missing blocks: retroactively estimate using git log timestamps via "
            "'python sdk/velocity_inference.py <block-id>'."
        ),
        rule_id="R6",
    )


def _rec_r7(p: Pattern) -> Recommendation:
    return Recommendation(
        pattern_name=p.name,
        title="Recalibrate L-tier duration estimates",
        rationale=(
            f"{p.occurrences} L-tier blocks exceeded 1.5× their estimate "
            f"(last: {p.last_detected}). L-tier estimates may systematically undercount."
        ),
        priority="medium",
        suggested_action=(
            "1. Review L-tier blocks' estimated_duration_days vs actual. "
            "2. Increase default L-tier estimate multiplier in manifest generation protocol. "
            "3. Consider splitting large L-tier blocks into M-tier sequences."
        ),
        rule_id="R7",
    )


_RULE_MAP = {
    "R1": _rec_r1,
    "R2": _rec_r2,
    "R3": _rec_r3,
    "R4": _rec_r4,
    "R5": _rec_r5,
    "R6": _rec_r6,
    "R7": _rec_r7,
}


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

def recommend(patterns: list[Pattern]) -> list[Recommendation]:
    """
    Generate Recommendation for each Pattern. Also populates Pattern.recommendation
    with a short summary string for use in patterns_report.
    Returns list sorted by priority (high first).
    """
    recs: list[Recommendation] = []
    for p in patterns:
        fn = _RULE_MAP.get(p.rule_id)
        if fn is None:
            continue
        try:
            r = fn(p)
            p.recommendation = r.suggested_action.split("\n")[0][:120]
            recs.append(r)
        except Exception:
            pass
    return sorted(recs, key=lambda r: r.priority_rank)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from retro_signals import extract_all
    from pattern_analyzer import analyze

    arch_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent
    signals = extract_all(arch_root)
    patterns = analyze(signals)
    recs = recommend(patterns)
    print(f"Patterns: {len(patterns)} → Recommendations: {len(recs)}")
    for r in recs:
        print(f"  [{r.priority.upper()}] {r.title}")
