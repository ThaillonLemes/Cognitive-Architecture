# cognitive-arch / sdk/brainstorm_context.py
# purpose: Context loader for Brainstorm v2.
#   Given a topic string, gathers relevant retros, patterns, ADRs, and state.
#   Relevance: keyword match scored by frequency × recency weight.
#   Hard cap on bundle size (max_chars). Degrades gracefully when files are absent.
# stdlib-only; no external dependencies

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from brainstorm_context_schema import (
    AdrEntry, ContextBundle, PatternEntry,
    RecommendationEntry, RetroEntry, StateSnapshot,
)

BLOCKS_DIR = "blocks"
PATTERNS_PATH = "governance/patterns.md"
DECISIONS_DIR = "decisions"
STATE_PATH = "STATE.md"
NEXT_PATH = "NEXT.md"

_MAX_RETROS = 5
_MAX_PATTERNS = 5
_MAX_ADRS = 3
_MAX_CONTENT_CHARS = 500     # per item content trim
_RECENCY_DECAY_DAYS = 30.0   # days over which weight decays from 1.0 → 0.1
_RECENCY_MIN = 0.1


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _arch_path(arch_root: Optional[str]) -> Path:
    return Path(arch_root) if arch_root is not None else Path.cwd()


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_kv(content: str) -> dict:
    """Parse key:value dense format (STATE.md / NEXT.md)."""
    result: dict = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for token in line.split():
            if ":" in token:
                key, _, val = token.partition(":")
                if key and val:
                    result[key] = val
    return result


def _extract_keywords(topic: str) -> list[str]:
    """
    Split topic into lowercase keywords (len > 2).
    Handles spaces, hyphens, underscores as delimiters.
    """
    raw = re.split(r"[\s\-_]+", topic.lower())
    return [w for w in raw if len(w) > 2]


def _score_relevance(text: str, keywords: list[str]) -> int:
    """
    Count keyword occurrences in text (case-insensitive).
    Returns raw hit count.
    """
    if not keywords:
        return 0
    lowered = text.lower()
    return sum(lowered.count(kw) for kw in keywords)


def _recency_weight(date_str: str, now_date: str) -> float:
    """
    Linear decay from 1.0 (today) to _RECENCY_MIN (>= _RECENCY_DECAY_DAYS old).
    date_str and now_date both YYYY-MM-DD.
    """
    if not date_str or not now_date:
        return _RECENCY_MIN
    try:
        d0 = datetime.strptime(date_str, "%Y-%m-%d")
        d1 = datetime.strptime(now_date, "%Y-%m-%d")
        days = max(0.0, (d1 - d0).days)
    except ValueError:
        return _RECENCY_MIN
    fraction = min(1.0, days / _RECENCY_DECAY_DAYS)
    return max(_RECENCY_MIN, 1.0 - fraction * (1.0 - _RECENCY_MIN))


def _extract_frontmatter_value(content: str, key: str) -> str:
    """Extract a YAML frontmatter value from a markdown file."""
    in_fm = False
    for i, line in enumerate(content.splitlines()):
        stripped = line.strip()
        if i == 0 and stripped == "---":
            in_fm = True
            continue
        if in_fm and stripped == "---":
            break
        if in_fm and stripped.startswith(key + ":"):
            _, _, val = stripped.partition(":")
            return val.strip().strip('"').strip("'")
    return ""


def _extract_h1(content: str) -> str:
    """Extract first H1 heading text from markdown."""
    for line in content.splitlines():
        m = re.match(r"^#\s+(.+)", line.strip())
        if m:
            return m.group(1).strip()
    return ""


def _trim_content(content: str) -> str:
    """Return content trimmed to _MAX_CONTENT_CHARS, excluding YAML frontmatter."""
    # Skip frontmatter
    lines = content.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                start = i + 1
                break
    body = "\n".join(lines[start:]).strip()
    return body[:_MAX_CONTENT_CHARS]


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_retros(blocks_dir: Path) -> list[RetroEntry]:
    """Scan blocks/ for block retrospective files and parse them."""
    retros = []
    if not blocks_dir.is_dir():
        return retros

    for path in sorted(blocks_dir.glob("block-[0-9]*-*.md")):
        # Exclude BLOCK_LOG.md, phase retrospectives
        if "BLOCK_LOG" in path.name or path.name.startswith("phase-"):
            continue

        content = _read_file(path)
        if not content:
            continue

        slug = path.stem  # e.g. "block-107-dependency-resolution"
        # Extract block_id from stem: "block-NNN"
        m = re.match(r"(block-\d+)", slug)
        block_id = m.group(1) if m else slug

        title = _extract_h1(content) or slug
        date = _extract_frontmatter_value(content, "completed_at")
        if date and "T" in date:
            date = date[:10]  # strip time component

        retros.append(RetroEntry(
            block_id=block_id,
            title=title,
            slug=slug,
            date=date,
            content=_trim_content(content),
        ))

    return retros


def _load_patterns(patterns_path: Path) -> list[PatternEntry]:
    """Parse governance/patterns.md into PatternEntry list."""
    content = _read_file(patterns_path)
    if not content:
        return []

    _SKIP = {"patterns report", "summary table", "top patterns"}
    patterns = []
    current_name: Optional[str] = None
    current_lines: list[str] = []

    def _flush():
        if current_name:
            patterns.append(PatternEntry(
                name=current_name,
                content="\n".join(current_lines).strip()[:_MAX_CONTENT_CHARS],
            ))

    for line in content.splitlines():
        m = re.match(r"^#{2,3}\s+(.+)", line.strip())
        if m:
            _flush()
            current_name = m.group(1).strip()
            if current_name.lower() in _SKIP:
                current_name = None
            current_lines = []
        elif current_name:
            current_lines.append(line)

    _flush()
    return patterns


def _load_adrs(decisions_dir: Path) -> list[AdrEntry]:
    """Scan decisions/ for ADR-*.md files."""
    adrs = []
    if not decisions_dir.is_dir():
        return adrs

    for path in sorted(decisions_dir.glob("ADR-*.md")):
        content = _read_file(path)
        if not content:
            continue

        stem = path.stem  # e.g. "ADR-001-structure-option-a"
        m = re.match(r"(ADR-\d+)", stem)
        adr_id = m.group(1) if m else stem
        title = _extract_h1(content) or stem

        adrs.append(AdrEntry(
            adr_id=adr_id,
            title=title,
            content=_trim_content(content),
        ))

    return adrs


def _load_state(arch_root: Path) -> StateSnapshot:
    """Read STATE.md and NEXT.md and return a StateSnapshot."""
    state = _parse_kv(_read_file(arch_root / STATE_PATH))
    nxt = _parse_kv(_read_file(arch_root / NEXT_PATH))

    return StateSnapshot(
        current_phase=state.get("phase", "unknown"),
        next_action=nxt.get("next_action", state.get("next", "unknown")),
        last_block=state.get("last_block", "-"),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def _rank_retros(
    retros: list[RetroEntry],
    keywords: list[str],
    now_date: str,
    max_count: int = _MAX_RETROS,
) -> list[RetroEntry]:
    """Score retros by relevance × recency; return top max_count."""
    def _score(r: RetroEntry) -> float:
        text = r.title + " " + r.slug + " " + r.content
        kw_score = _score_relevance(text, keywords)
        rw = _recency_weight(r.date, now_date)
        return kw_score * rw

    scored = [(r, _score(r)) for r in retros]
    scored.sort(key=lambda t: t[1], reverse=True)
    # Include items with score > 0 preferentially; fall back to most-recent if empty
    result = [r for r, s in scored if s > 0][:max_count]
    if not result:
        # Return the most-recent max_count retros
        result = sorted(retros, key=lambda r: r.date, reverse=True)[:max_count]
    return result


def _rank_patterns(
    patterns: list[PatternEntry],
    keywords: list[str],
    max_count: int = _MAX_PATTERNS,
) -> list[PatternEntry]:
    """Score patterns by keyword match; return top max_count."""
    def _score(p: PatternEntry) -> int:
        return _score_relevance(p.name + " " + p.content, keywords)

    scored = sorted(patterns, key=_score, reverse=True)
    result = [p for p in scored if _score_relevance(p.name + " " + p.content, keywords) > 0]
    if not result:
        result = patterns
    return result[:max_count]


def _rank_adrs(
    adrs: list[AdrEntry],
    keywords: list[str],
    max_count: int = _MAX_ADRS,
) -> list[AdrEntry]:
    """Score ADRs by keyword match; return top max_count."""
    def _score(a: AdrEntry) -> int:
        return _score_relevance(a.adr_id + " " + a.title + " " + a.content, keywords)

    scored = sorted(adrs, key=_score, reverse=True)
    result = [a for a in scored if _score(a) > 0]
    return result[:max_count]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_context(
    topic: str,
    arch_root: Optional[str] = None,
    now_date: Optional[str] = None,
    # Injectable for testing
    retros: Optional[list[RetroEntry]] = None,
    patterns: Optional[list[PatternEntry]] = None,
    adrs: Optional[list[AdrEntry]] = None,
    state: Optional[StateSnapshot] = None,
) -> ContextBundle:
    """
    Load a ContextBundle for the given topic.

    Parameters
    ----------
    topic : str
        Brainstorm topic (e.g. "dependency management" or "dashboard-design").
    arch_root : str, optional
        Root of the cognitive-arch project. Used when content is not injected.
    now_date : str, optional
        Reference date (YYYY-MM-DD) for recency weighting. Defaults to today UTC.
    retros, patterns, adrs, state : optional
        Injectable for testing. None → read from disk.

    Returns
    -------
    ContextBundle
        Sorted by relevance (highest first). Empty lists valid.
    """
    if not now_date:
        now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    root = _arch_path(arch_root)
    keywords = _extract_keywords(topic)

    if retros is None:
        retros = _load_retros(root / BLOCKS_DIR)
    if patterns is None:
        patterns = _load_patterns(root / PATTERNS_PATH)
    if adrs is None:
        adrs = _load_adrs(root / DECISIONS_DIR)
    if state is None:
        state = _load_state(root)

    ranked_retros = _rank_retros(retros, keywords, now_date)
    ranked_patterns = _rank_patterns(patterns, keywords)
    ranked_adrs = _rank_adrs(adrs, keywords)

    return ContextBundle(
        topic=topic,
        relevant_retros=ranked_retros,
        applicable_patterns=ranked_patterns,
        recommendations=[],   # reserved for governance/recommendations.md (future)
        related_adrs=ranked_adrs,
        state_snapshot=state,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Brainstorm context loader")
    parser.add_argument("topic", help="Brainstorm topic (e.g. 'dependency management')")
    parser.add_argument("--arch-root", default=".", help="Root of cognitive-arch project")
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    args = parser.parse_args()

    bundle = load_context(args.topic, arch_root=args.arch_root)

    if args.json:
        summary = {
            "topic": bundle.topic,
            "retros": [r.block_id for r in bundle.relevant_retros],
            "patterns": [p.name for p in bundle.applicable_patterns],
            "adrs": [a.adr_id for a in bundle.related_adrs],
            "state": {
                "phase": bundle.state_snapshot.current_phase if bundle.state_snapshot else "?",
                "next": bundle.state_snapshot.next_action if bundle.state_snapshot else "?",
            },
        }
        print(json.dumps(summary, indent=2))
    else:
        print(f"Topic: {bundle.topic}")
        print(f"Retros ({len(bundle.relevant_retros)}): {[r.block_id for r in bundle.relevant_retros]}")
        print(f"Patterns ({len(bundle.applicable_patterns)}): {[p.name for p in bundle.applicable_patterns]}")
        print(f"ADRs ({len(bundle.related_adrs)}): {[a.adr_id for a in bundle.related_adrs]}")
