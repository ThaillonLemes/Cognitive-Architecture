# cognitive-arch / sdk/brainstorm_context_schema.py
# purpose: Data model for brainstorm context bundles.
#   ContextBundle is the canonical structure consumed by brainstorm_predictor (block-109)
#   and brainstorm_synthesis (block-111).
# stdlib-only; no external dependencies

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RetroEntry:
    """A parsed block retrospective relevant to a brainstorm topic."""
    block_id: str        # e.g. "block-107"
    title: str           # H1 title text (from "# Block NNN Retrospective — ...")
    slug: str            # filename without .md (e.g. "block-107-dependency-resolution")
    date: str            # YYYY-MM-DD from completed_at field or filename inference
    content: str         # trimmed body for context (max _MAX_CONTENT_CHARS chars)


@dataclass
class PatternEntry:
    """A named pattern from governance/patterns.md."""
    name: str            # pattern name (from ## heading)
    content: str         # first paragraph / description lines (trimmed)


@dataclass
class RecommendationEntry:
    """A recommendation entry (from governance/recommendations.md or similar)."""
    title: str
    content: str


@dataclass
class AdrEntry:
    """An Architectural Decision Record."""
    adr_id: str          # e.g. "ADR-001"
    title: str           # from H1
    content: str         # first section trimmed


@dataclass
class StateSnapshot:
    """Current project state summary."""
    current_phase: str
    next_action: str
    last_block: str
    generated_at: str    # ISO timestamp


@dataclass
class ContextBundle:
    """
    Complete context bundle for a brainstorm topic.
    Passed to prediction engine (block-109) and synthesis automation (block-111).

    All list fields are sorted by relevance score (highest first).
    Empty lists are valid — context loader degrades gracefully on sparse projects.
    """
    topic: str
    relevant_retros: list[RetroEntry] = field(default_factory=list)
    applicable_patterns: list[PatternEntry] = field(default_factory=list)
    recommendations: list[RecommendationEntry] = field(default_factory=list)
    related_adrs: list[AdrEntry] = field(default_factory=list)
    state_snapshot: Optional[StateSnapshot] = None
    max_chars: int = 8000   # approximate LLM context budget; loader truncates to this
