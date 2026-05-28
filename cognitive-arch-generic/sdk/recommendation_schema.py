# sdk/recommendation_schema.py
# PURPOSE: Recommendation dataclass — actionable suggestion derived from a Pattern.
# INPUTS:  (imported by recommendation_engine, patterns_report, master_agent)
# OUTPUTS: Recommendation instances
# DEPS:    stdlib only (dataclasses)
# SEE:     sdk/recommendation_engine.py, sdk/patterns_report.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Recommendation:
    """Actionable suggestion derived from a detected Pattern."""

    pattern_name: str           # matches Pattern.name
    title: str                  # short human-readable title
    rationale: str              # why this is recommended (cites pattern evidence)
    priority: str               # "high" | "medium" | "low"
    suggested_action: str       # concrete next step (create block / review file / etc.)
    rule_id: str                # which pattern rule triggered this

    @property
    def priority_rank(self) -> int:
        return {"high": 0, "medium": 1, "low": 2}.get(self.priority, 3)
