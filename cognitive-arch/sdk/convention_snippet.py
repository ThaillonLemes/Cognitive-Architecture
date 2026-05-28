# PURPOSE: Generate block-kind-specific axiom convention snippets for task packets
# INPUTS:  block kind string (doc-only | refactor | implementation | gate | discovery | ...)
#          optional: manifest axiom_override list
# OUTPUTS: axioms string (comma-separated IDs) + snippet body (one line per axiom)
# DEPS:    stdlib only (no external packages)
# SEE:     protocols/convention-snippet-generation.md, PROTOCOLS.md,
#          design/governor-v2.md §3 Decision 1, sdk/task_packet.py

"""
Convention snippet generator.

Reads block kind → selects applicable axioms → formats snippet for task packet.
All axiom text is inline (no PROTOCOLS.md read at runtime) for speed and portability.

Usage (module):
    from sdk.convention_snippet import build_snippet
    axioms_str, body = build_snippet("refactor")

Usage (CLI test):
    python sdk/convention_snippet.py --test
    python sdk/convention_snippet.py --kind refactor
"""

import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Axiom registry — verbatim condensed text from PROTOCOLS.md
# Sorted canonical order: P → Q → C
# ---------------------------------------------------------------------------

AXIOMS: dict[str, str] = {
    "P1": "Determinism over creativity in structure. Templates govern file generation; structure does not vary.",
    "P2": "Evidence over claims. Done = auditable artifacts prove it, not agent assertion.",
    "P3": "Single source of truth. Each fact in exactly one file; others point, do not restate.",
    "P4": "Pointer integrity. Every cross-file reference must resolve. Broken pointers are audit errors.",
    "P5": "Slim boot. HOT files minimal; detail lives in WARM/COLD reached via INDEX.md.",
    "P6": "AI-first format for HOT files. Dense key:value per _syntax.md. No prose where data suffices.",
    "Q1": "Rule of Three for shared abstractions [code-leaning]. Third occurrence justifies a shared abstraction; document in manifest.",
    "Q2": "File size budgets. HOT files have maximums (CLAUDE.md <=60 lines, STATE.md <=60 lines, etc.); audit warns if exceeded.",
    "Q3": "Manifests precede work artifacts. No artifact produced before its manifest exists and validates.",
    "Q4": "Gates pass before commit. No commit unless all declared gates pass or user applies forced_pass with rationale.",
    "Q5": "Dependencies must be complete. Block does not start if any dependency block is not status done.",
    "Q6": "Files declared exhaustively. Manifest files.read/modify/create enumerate every file touched.",
    "Q7": "Out of scope is explicit. Every manifest declares deferrals to prevent scope creep.",
    "C1": "Code header mandatory [code-only]. Every code file begins with PURPOSE/INPUTS/OUTPUTS/DEPS/SEE header.",
    "C2": "No speculation in documentation. Describe what IS, WAS, or WILL DEFINITELY BE.",
    "C3": "BRIEF on large markdown files. Files over 100 lines begin with BRIEF: (1-3 lines).",
    "C4": "AI-only files use _syntax.md vocabulary. STATE.md, NEXT.md, board.md, INDEX.md: dense key:value, no prose.",
    "C5": "ADR for non-obvious decisions. Decisions go in decisions/ADR-NNN.md; code/doc references ADR ID.",
    "C6": "Retrospectives are facts, not stories. List what was built, gates passed, deferred — not narrative.",
}

# Sort order: P first, then Q, then C (per protocol); numeric within each group
_GROUP_ORDER = {"P": 0, "Q": 1, "C": 2}
_SORT_KEY = {aid: (_GROUP_ORDER.get(aid[0], 9), int(aid[1:])) for aid in AXIOMS}

# ---------------------------------------------------------------------------
# Kind → axiom mapping (from protocols/convention-snippet-generation.md)
# "implementation" maps to "feature" (design/governor-v2.md §4 kind vocabulary)
# ---------------------------------------------------------------------------

_CORE: dict[str, list[str]] = {
    "doc-only":       ["Q2", "Q3", "C2", "C3", "C6"],
    "doc":            ["Q2", "Q3", "C2", "C3", "C6"],       # alias
    "refactor":       ["Q2", "Q3", "Q4", "C2", "C4", "C6"],
    "enhancement":    ["Q2", "Q3", "Q5", "Q6", "C2", "C4", "C6"],
    "implementation": ["Q1", "Q2", "Q3", "Q5", "Q6", "C2", "C4", "C6"],  # ≈ feature
    "feature":        ["Q1", "Q2", "Q3", "Q5", "Q6", "C2", "C4", "C6"],
    "bugfix":         ["Q3", "Q4", "Q6", "C2", "C4"],
    "gate":           ["Q4"],
    "discovery":      ["Q4", "Q6", "C2"],
    "small-fix":      ["Q3", "Q4", "Q6", "C2", "C6"],       # alias → bugfix-like
}

_OPTIONAL: dict[str, list[str]] = {
    "doc-only":       ["P1", "P3"],
    "doc":            ["P1", "P3"],
    "refactor":       ["P3", "P5", "Q6"],
    "enhancement":    ["P1", "P4", "Q4"],
    "implementation": ["P1", "P4", "P6", "C5"],
    "feature":        ["P1", "P4", "P6", "C5"],
    "bugfix":         ["P5", "P6", "Q5"],
    "gate":           ["P2", "C2"],
    "discovery":      ["P2", "P3"],
    "small-fix":      ["P5", "Q5"],
}

# Axioms always added when block touches source code (C1 gating)
_CODE_AXIOMS = ["C1"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_snippet(
    kind: str,
    *,
    modifies_code: bool = False,
    axiom_override: Optional[list[str]] = None,
) -> tuple[str, str]:
    """
    Build a convention snippet for a given block kind.

    Args:
        kind:           Block kind string (e.g. "refactor", "implementation").
        modifies_code:  True if block creates/modifies source code files → adds C1.
        axiom_override: If provided, replaces computed list entirely.

    Returns:
        (axioms_str, snippet_body)
        - axioms_str: comma-separated IDs for task packet header, e.g. "Q2,Q3,C2,C3,C6"
        - snippet_body: multi-line string, one "ID: text" line per axiom
    """
    kind_key = kind.lower().replace("_", "-")

    if axiom_override is not None:
        selected = list(axiom_override)
    else:
        core = list(_CORE.get(kind_key, _CORE["implementation"]))
        selected = core[:]
        if modifies_code and "C1" not in selected:
            selected.extend(_CODE_AXIOMS)

    # Deduplicate while preserving canonical sort
    seen: set[str] = set()
    unique: list[str] = []
    for aid in selected:
        if aid not in seen and aid in AXIOMS:
            seen.add(aid)
            unique.append(aid)

    # Sort: P → Q → C, numeric within group
    unique.sort(key=lambda a: (_SORT_KEY.get(a, ("Z", 99))))

    axioms_str = ",".join(unique)
    snippet_body = "--- convention snippet ---\n"
    snippet_body += "\n".join(f"{aid}: {AXIOMS[aid]}" for aid in unique)

    return axioms_str, snippet_body


def list_kinds() -> list[str]:
    """Return the canonical block kind names (excluding aliases)."""
    return ["doc-only", "refactor", "enhancement", "implementation", "bugfix", "gate", "discovery", "small-fix"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli_test() -> int:
    """Run self-test: generate snippets for all canonical kinds and print results."""
    kinds = ["doc-only", "refactor", "implementation", "gate", "discovery"]
    results: dict[str, tuple[str, str]] = {}
    errors: list[str] = []

    for k in kinds:
        axioms_str, body = build_snippet(k)
        if not axioms_str:
            errors.append(f"FAIL [{k}]: axioms_str is empty")
        if not body or len(body.strip().splitlines()) < 2:
            errors.append(f"FAIL [{k}]: snippet body too short")
        results[k] = (axioms_str, body)

    # Check all are distinct (no two kinds produce identical axiom sets)
    axiom_sets = [v[0] for v in results.values()]
    if len(set(axiom_sets)) < len(kinds):
        errors.append("FAIL: at least two kinds produce identical axiom sets")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print("convention_snippet --test: PASS")
    print(f"  Kinds tested: {len(kinds)}")
    for k, (axioms_str, body) in results.items():
        lines = body.strip().splitlines()
        print(f"  [{k:>14}]  axioms={axioms_str}  lines={len(lines)}")
    return 0


def _cli_kind(kind: str) -> int:
    """Print snippet for a given kind."""
    axioms_str, body = build_snippet(kind)
    print(f"axioms:{axioms_str}")
    print()
    print(body)
    return 0


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="convention_snippet",
        description="Generate axiom convention snippets for Governor v2 task packets.",
    )
    parser.add_argument("--test", action="store_true", help="Run self-test for all block kinds.")
    parser.add_argument("--kind", metavar="KIND", help="Print snippet for a specific block kind.")
    parser.add_argument("--list-kinds", action="store_true", help="List all supported block kinds.")

    args = parser.parse_args()

    if args.test:
        sys.exit(_cli_test())
    elif args.kind:
        sys.exit(_cli_kind(args.kind))
    elif args.list_kinds:
        for k in list_kinds():
            print(k)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
