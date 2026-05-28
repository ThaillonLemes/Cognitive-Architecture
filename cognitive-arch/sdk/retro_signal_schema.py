# sdk/retro_signal_schema.py
# PURPOSE: RetroSignal dataclass — structured extraction of one block retrospective.
# INPUTS:  (imported by retro_signals.py and downstream consumers)
# OUTPUTS: RetroSignal instances
# DEPS:    stdlib only (dataclasses)
# SEE:     sdk/retro_signals.py, sdk/pattern_analyzer.py, sdk/recommendation_engine.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RetroSignal:
    """Structured signal extracted from a single block retrospective."""

    # Identity
    block_id: str                           # e.g. "block-042"
    phase: str                              # e.g. "phase-5"
    tier: str                               # S | M | L | unknown
    kind: str                               # implementation | doc-only | investigation | refactor | unknown

    # Duration
    duration_actual_h: Optional[float]      # actual_duration_hours from frontmatter; None if missing
    duration_estimated_days: Optional[float]  # estimated_duration_days from manifest; None if missing
    duration_source: str                    # manual | auto-inferred | estimated | unknown

    # Quality signals
    axioms_violated: list[str] = field(default_factory=list)  # e.g. ["P3", "Q6"]
    scope_expansion: bool = False           # files added beyond manifest declaration
    gate_failures: int = 0                  # M - N from "gates_passed: N/M"
    gates_total: int = 0
    gates_passed_count: int = 0
    forced_pass: bool = False               # any "force-pass" or "forced_pass" in retro

    # Metadata
    closed_at: Optional[str] = None         # completed_at ISO string
    parse_warnings: list[str] = field(default_factory=list)   # non-fatal parse issues

    @property
    def duration_delta_ratio(self) -> Optional[float]:
        """actual_h / (estimated_days * 8). >1.0 = over-estimate. None if data missing."""
        if self.duration_actual_h is None or self.duration_estimated_days is None:
            return None
        estimated_h = self.duration_estimated_days * 8.0
        if estimated_h <= 0:
            return None
        return self.duration_actual_h / estimated_h

    @property
    def over_estimate(self) -> bool:
        """True if actual took more than 1.5× estimated (after converting days→hours)."""
        ratio = self.duration_delta_ratio
        return ratio is not None and ratio > 1.5
