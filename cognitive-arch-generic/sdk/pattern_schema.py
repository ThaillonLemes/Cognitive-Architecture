# sdk/pattern_schema.py
# PURPOSE: Pattern dataclass — describes a recurring issue detected across RetroSignals.
# INPUTS:  (imported by pattern_analyzer, patterns_report, recommendation_engine)
# OUTPUTS: Pattern instances
# DEPS:    stdlib only (dataclasses)
# SEE:     sdk/pattern_analyzer.py, sdk/patterns_report.py, sdk/recommendation_engine.py

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Pattern:
    """A recurring issue detected across multiple block retrospectives."""

    name: str                           # short slug, e.g. "axiom-p3-repeated-violation"
    description: str                    # human-readable summary
    severity: str                       # "info" | "warn" | "critical"
    evidence: list[str]                 # block_ids where the pattern was observed
    first_detected: str                 # block_id of first occurrence in window
    last_detected: str                  # block_id of most recent occurrence
    occurrences: int                    # len(evidence)
    recommendation: str = ""            # short actionable suggestion (filled by recommendation_engine)
    rule_id: str = ""                   # which detection rule produced this pattern

    @property
    def is_actionable(self) -> bool:
        return bool(self.recommendation)
