# PURPOSE: Canonical, self-explaining project health score — ONE definition every
#          instrument reads (audit.py + health_report.py both report THIS number).
#          Aggregates audit + invariant + HOT-boot signals into a score with a
#          weighted factor breakdown and a ranked top_drags(n) (each factor carries
#          its point cost and a one-line fix).
# INPUTS:  arch root — reuses audit.run_audit (AuditResult), invariant_check.run_all
#          (defensive import), HOT-boot byte totals, and governance/known-drift.md
#          (accepted historical drift); never re-walks source files itself.
# OUTPUTS: HealthScore(score, factors); Factor(key, cost, detail, fix); CLI prints
#          "Health: N/100" + a "Top drags" list. ASCII-safe (force_utf8).
# DEPS:    stdlib only + sibling audit.py, safe_io.py; SOFT invariant_check.py
#          (absent/erroring -> a 0-cost 'invariant.unavailable' factor, never a crash);
#          SOFT governance/known-drift.md (absent -> no exclusion, never a crash).
# SEE:     phases/phase-26.md (collapse audit 32 vs health 100 into one score),
#          manifests/block-148-health-model.md, manifests/block-149-reconcile-health.md,
#          governance/known-drift.md, sdk/audit.py, sdk/invariant_check.py

from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Allow running both as a module and as a script (python sdk/health_model.py).
_SDK_DIR = Path(__file__).resolve().parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import audit  # noqa: E402  (reuse run_audit / AuditResult — never re-implement checks)
from safe_io import force_utf8  # noqa: E402


# ---------------------------------------------------------------------------
# Weighting table — the SINGLE source of "how many points does a signal cost".
# Heavy for hard failures (errors / critical invariants), light for warnings.
# One factor per signal CATEGORY (not per message) so top_drags stays readable;
# a category's cost is count * unit. Audit units mirror sdk/audit.py's historical
# 100 - errors*15 - warnings*2 so the familiar audit number maps onto this model.
# Phase 26 §3: score == max(0, 100 - sum(factor.cost)) — factors are namespaced
# (audit.*, invariant.*, hot.*) to guarantee no double-counting across instruments.
#
# block-149 MEANINGFULNESS RULES (so the score isn't floored at 0 by accepted gaps):
#   (a) ACCEPTED DRIFT IS FREE. Warnings whose block id is documented in
#       governance/known-drift.md are accepted history, not open work — they move to
#       a 0-cost `*.accepted` factor (shown for transparency) and DO NOT drag the
#       score. This applies to BOTH instruments: audit's check-8 "drift" warns and
#       invariant_check's INV2/INV3 warns reference the SAME blocks, so without this
#       the accepted gap is double-counted and alone sinks the score to 0.
#   (b) PER-CATEGORY LIGHT-WARN CAP. A single light-warning category (audit.warnings,
#       invariant.warn) contributes at most WARN_CATEGORY_CAP points, so a pile of
#       minor, non-blocking warns can never alone zero an otherwise-healthy root.
#       Errors/criticals are uncapped — a real failure still tanks the score.
#   The HealthScore invariant `score == max(0, 100 - sum(costs))` stays exactly true:
#   exclusion and capping change a factor's `cost`, never the score arithmetic.
# ---------------------------------------------------------------------------

COST_AUDIT_ERROR = 15        # heavy: a failing audit check (uncapped)
COST_AUDIT_WARN = 2          # light: an audit warning
COST_INVARIANT_CRITICAL = 15  # heavy: a critical invariant violation (mirrors audit error, uncapped)
COST_INVARIANT_WARN = 2      # light: a warn-level invariant violation
COST_HOT_OVER_BUDGET = 10    # one-shot: HOT boot read exceeds the token budget

# Max points any ONE light-warning category may deduct (block-149 rule (b)).
# 30 == 15 unit-2 warns: enough that a real warn pile is visible, capped so it
# can't alone zero a root that has no errors/criticals. None == uncapped.
WARN_CATEGORY_CAP = 30

# HOT boot budget (chars/4 ~= tokens) — mirrors sdk/audit.print_token_estimates.
HOT_BOOT_FILES = ["CLAUDE.md", "PROTOCOLS.md", "STATE.md", "NEXT.md", "INDEX.md", "board.md"]
HOT_BOOT_TOKEN_BUDGET = 4000

# Accepted-drift ledger — governance/known-drift.md (block-147). Absent -> no
# exclusion (defensive: a fresh scaffold has no such file and must not crash).
KNOWN_DRIFT_FILE = "governance/known-drift.md"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Factor:
    """One weighted contributor to the health score.

    A factor is a single explainable drag: its `cost` is the points it deducts
    from 100, `detail` says what was observed, and `fix` is a one-line how-to-fix
    (a number with no fix is a bug — Phase 26 §1). Zero-cost factors are allowed
    and kept (e.g. a clean category, or a defensively-unavailable dependency) so
    the breakdown is honest about what was checked.
    """

    key: str           # namespaced id, e.g. "audit.errors", "invariant.critical"
    cost: int          # points deducted from 100 (>= 0)
    detail: str        # what was observed ("3 audit error(s)")
    fix: str           # one-line remedy ("run: python sdk/audit.py --arch-root .")


@dataclass
class HealthScore:
    """A health score plus the weighted factors that produced it.

    INVARIANT (load-bearing, Phase 26 §3): `score == max(0, 100 - sum(costs))`.
    The score is explainable by construction — `top_drags(n)` returns the worst
    factors, each with its point cost and a one-line fix.
    """

    factors: list[Factor] = field(default_factory=list)

    @property
    def total_cost(self) -> int:
        """Sum of every factor's point cost (un-clamped)."""
        return sum(f.cost for f in self.factors)

    @property
    def score(self) -> int:
        """Health in [0, 100] == max(0, 100 - total_cost). Never below zero."""
        return max(0, 100 - self.total_cost)

    def top_drags(self, n: int = 3) -> list[Factor]:
        """The `n` highest-cost factors, sorted by cost descending.

        Only factors that actually cost points are returned — a 0-cost factor is
        not a "drag". Ties keep their original (insertion) order via a stable sort,
        so the breakdown is deterministic. This is what makes the score explain
        itself: "you are at X/100; the top drags are A (-N), B (-M) ...".
        """
        drags = [f for f in self.factors if f.cost > 0]
        return sorted(drags, key=lambda f: f.cost, reverse=True)[:n]


# ---------------------------------------------------------------------------
# Accepted-drift exclusion (block-149) — parse governance/known-drift.md
# ---------------------------------------------------------------------------

# Matches a single block id, e.g. "block-061", capturing its number.
_BLOCK_ID_RE = re.compile(r"block-(\d+)")
# Matches a range with bare numbers, e.g. "061 through 085" / "108 to 111".
_NUM_RANGE_RE = re.compile(r"\b(\d{2,4})\s*(?:through|to|\.\.\.|…|–|—|-)\s*(\d{2,4})\b")
# Matches a range written with ids, e.g. "block-061 … block-085" / "block-061 - block-085".
_ID_RANGE_RE = re.compile(r"block-(\d+)\s*(?:through|to|\.\.\.|…|–|—|-)\s*block-(\d+)")


def _accepted_sections(text: str) -> str:
    """The body of every '## INV...' section — where acceptances are declared.

    known-drift.md's leading metadata ("# Recorded by: block-147") and "## Purpose"
    prose ("After block-147 ... 0 CRITICAL") mention blocks that are NOT accepted
    drift; harvesting ids from the whole file would wrongly excuse them. Each
    accepted gap lives under a '## INVn — ...' header, so we scope parsing to those
    sections. If the ledger uses no '## INV' headers, fall back to the full text
    (a differently-shaped ledger still gets parsed rather than silently ignored).
    """
    lines = text.splitlines()
    in_inv = False
    kept: list[str] = []
    saw_inv = False
    for line in lines:
        if line.startswith("## "):
            in_inv = line.startswith("## INV")
            saw_inv = saw_inv or in_inv
        if in_inv:
            kept.append(line)
    return "\n".join(kept) if saw_inv else text


def accepted_drift_blocks(arch_root: Path) -> set[str]:
    """Zero-padded block numbers documented as ACCEPTED drift in known-drift.md.

    Parses governance/known-drift.md (block-147) for every block the project has
    explicitly accepted as historical, never-back-filled drift. Scoped to the
    '## INV...' sections (see _accepted_sections) so metadata/prose block mentions
    aren't mistaken for acceptances. Recognises three shapes so a human-written
    ledger isn't brittle:
      * explicit ids            -> "block-061", "block-108"
      * id ranges               -> "block-061 … block-085", "block-061 - block-085"
      * bare numeric ranges     -> "061 through 085", "108 to 111"
    Returns a set of zero-padded numbers ({"061", ..., "085", "108".."111"}); the
    numbers are matched against warning messages (which all say "block-NNN").

    DEFENSIVE (block-149 / Phase 26 §2): a missing or unreadable file yields an
    EMPTY set (no exclusion) — never an exception. A fresh scaffold without a
    known-drift.md therefore excludes nothing and still scores normally.
    """
    path = Path(arch_root) / KNOWN_DRIFT_FILE
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return set()

    scoped = _accepted_sections(text)
    nums: set[int] = set()

    # 1) id-form ranges first (consume "block-061 … block-085" as a span).
    for lo, hi in _ID_RANGE_RE.findall(scoped):
        a, b = int(lo), int(hi)
        if a <= b and b - a <= 1000:  # guard against absurd spans
            nums.update(range(a, b + 1))

    # 2) bare numeric ranges ("061 through 085"). Idempotent into the same int set.
    for lo, hi in _NUM_RANGE_RE.findall(scoped):
        a, b = int(lo), int(hi)
        if a <= b and b - a <= 1000:
            nums.update(range(a, b + 1))

    # 3) every explicit "block-NNN" id mentioned within the accepted sections.
    for n in _BLOCK_ID_RE.findall(scoped):
        nums.add(int(n))

    # Re-pad to the width the warning messages use (block-NNN -> >=3 digits).
    return {f"{n:03d}" for n in nums}


def _msg_block_num(message: str) -> str | None:
    """The zero-padded block number a warning message refers to, or None.

    Audit drift warns and INV2/INV3 warns both name their block as 'block-NNN',
    so one matcher serves both instruments.
    """
    m = _BLOCK_ID_RE.search(message)
    return f"{int(m.group(1)):03d}" if m else None


def _split_accepted(messages: list[str], accepted: set[str]) -> tuple[list[str], list[str]]:
    """Partition warning messages into (counted, accepted_as_drift).

    A message is `accepted` iff it names a block in the accepted-drift set; those
    do NOT cost points. Everything else is `counted`. A message with no block id
    is always counted (it can't be matched against the ledger).
    """
    if not accepted:
        return list(messages), []
    counted: list[str] = []
    excused: list[str] = []
    for msg in messages:
        num = _msg_block_num(msg)
        (excused if (num is not None and num in accepted) else counted).append(msg)
    return counted, excused


def _capped(cost: int) -> int:
    """Apply the per-category light-warn cap (block-149 rule (b)). None => uncapped."""
    if WARN_CATEGORY_CAP is None:
        return cost
    return min(cost, WARN_CATEGORY_CAP)


# ---------------------------------------------------------------------------
# Signal collection (each helper NEVER raises — a failure yields a 0-cost factor)
# ---------------------------------------------------------------------------

def _audit_factors(arch_root: Path, accepted: set[str] | None = None) -> list[Factor]:
    """Run the real audit checks and turn its error/warn MESSAGES into factors.

    Reuses audit.run_audit (the AuditResult) instead of re-walking files, so the
    model and `sdk/audit.py` see the SAME signals. audit prints a full report as a
    side effect; we redirect that to a throwaway buffer here so the model's own
    output stays clean.

    block-149: audit's check-8 "drift" warns name the same blocks-061..085 that
    known-drift.md accepts, so those warns are split into a 0-cost `audit.accepted`
    factor; the rest (capped) is the real `audit.warnings` drag. Errors are
    uncapped and never excused. `accepted` is parsed from known-drift.md when not
    supplied, so this helper is correct called standalone or from compute().
    """
    if accepted is None:
        accepted = accepted_drift_blocks(arch_root)
    try:
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            # as_json=True skips audit's summary block — we only need the raw
            # error/warn lists here, and (critically) that block calls
            # AuditResult.score(), which re-enters compute() -> infinite recursion.
            result = audit.run_audit(arch_root, as_json=True)
        errors = list(result.errors)
        warnings = list(result.warnings)
    except Exception as exc:  # audit must never crash the model
        return [Factor(
            key="audit.unavailable", cost=0,
            detail=f"audit could not run ({exc})",
            fix="repair sdk/audit.py so health can read audit signals",
        )]

    n_err = len(errors)
    counted_warns, accepted_warns = _split_accepted(warnings, accepted)
    n_warn = len(counted_warns)
    raw_warn_cost = n_warn * COST_AUDIT_WARN
    warn_cost = _capped(raw_warn_cost)
    capped_note = f" (capped at {WARN_CATEGORY_CAP})" if warn_cost != raw_warn_cost else ""

    factors = [
        Factor(
            key="audit.errors",
            cost=n_err * COST_AUDIT_ERROR,
            detail=f"{n_err} audit error(s) x{COST_AUDIT_ERROR}pt",
            fix="run: python sdk/audit.py --arch-root . and clear each ERROR",
        ),
        Factor(
            key="audit.warnings",
            cost=warn_cost,
            detail=f"{n_warn} audit warning(s) x{COST_AUDIT_WARN}pt{capped_note}",
            fix="run: python sdk/audit.py --arch-root . and clear each WARN",
        ),
    ]
    if accepted_warns:
        factors.append(Factor(
            key="audit.accepted",
            cost=0,
            detail=f"{len(accepted_warns)} accepted-drift warning(s) excused (governance/known-drift.md)",
            fix="none — documented historical drift; see governance/known-drift.md",
        ))
    return factors


def _invariant_factors(arch_root: Path, accepted: set[str] | None = None) -> list[Factor]:
    """Run invariant_check.run_all and split violations into critical/warn factors.

    DEFENSIVE IMPORT (Phase 26 §2): invariant_check may not exist yet (Phase 25 not
    merged). If the import fails — or the engine raises — this contributes a single
    0-cost `invariant.unavailable` factor instead of crashing. Mirrors the
    never-crash resilience of pattern_analyzer.analyze().

    block-149: warn-severity violations whose block is in known-drift.md (INV2
    blocks 061-085 with no retro; INV3 blocks 108-111 with no tier) are accepted
    history — they move to a 0-cost `invariant.accepted` factor and do not drag the
    score. Remaining warns are capped; criticals are uncapped and never excused.
    `accepted` is parsed from known-drift.md when not supplied.
    """
    if accepted is None:
        accepted = accepted_drift_blocks(arch_root)
    try:
        import invariant_check  # local import: a missing module degrades gracefully
    except Exception:
        return [Factor(
            key="invariant.unavailable", cost=0,
            detail="invariant_check not available (Phase 25 not yet merged?)",
            fix="land Phase 25 (sdk/invariant_check.py) to fold invariants into health",
        )]

    try:
        violations = invariant_check.run_all(arch_root)
        crit_msgs = [v.message for v in violations if getattr(v, "severity", "") == "critical"]
        warn_msgs = [v.message for v in violations if getattr(v, "severity", "") == "warn"]
    except Exception as exc:  # a buggy engine must never crash the model
        return [Factor(
            key="invariant.unavailable", cost=0,
            detail=f"invariant_check errored ({exc})",
            fix="repair sdk/invariant_check.py so health can read invariants",
        )]

    n_crit = len(crit_msgs)
    counted_warns, accepted_warns = _split_accepted(warn_msgs, accepted)
    n_warn = len(counted_warns)
    raw_warn_cost = n_warn * COST_INVARIANT_WARN
    warn_cost = _capped(raw_warn_cost)
    capped_note = f" (capped at {WARN_CATEGORY_CAP})" if warn_cost != raw_warn_cost else ""

    factors = [
        Factor(
            key="invariant.critical",
            cost=n_crit * COST_INVARIANT_CRITICAL,
            detail=f"{n_crit} critical invariant violation(s) x{COST_INVARIANT_CRITICAL}pt",
            fix="run: python sdk/invariant_check.py --arch-root . and resolve each CRITICAL",
        ),
        Factor(
            key="invariant.warn",
            cost=warn_cost,
            detail=f"{n_warn} warn invariant violation(s) x{COST_INVARIANT_WARN}pt{capped_note}",
            fix="run: python sdk/invariant_check.py --arch-root . and resolve each WARN",
        ),
    ]
    if accepted_warns:
        factors.append(Factor(
            key="invariant.accepted",
            cost=0,
            detail=f"{len(accepted_warns)} accepted-drift violation(s) excused (governance/known-drift.md)",
            fix="none — documented historical drift; see governance/known-drift.md",
        ))
    return factors


def _hot_boot_factor(arch_root: Path) -> Factor:
    """A drag iff the HOT boot read (CLAUDE/PROTOCOLS/STATE/NEXT/INDEX/board) is
    over the token budget. Token estimate = bytes/4, matching audit's estimate.
    Under budget -> 0 cost (kept so the breakdown shows it was checked)."""
    total_chars = 0
    for name in HOT_BOOT_FILES:
        p = arch_root / name
        try:
            total_chars += len(p.read_bytes())
        except OSError:
            continue
    tokens = total_chars // 4
    over = tokens > HOT_BOOT_TOKEN_BUDGET
    return Factor(
        key="hot.boot_over_budget",
        cost=COST_HOT_OVER_BUDGET if over else 0,
        detail=(f"HOT boot ~{tokens} tok "
                f"({'over' if over else 'within'} {HOT_BOOT_TOKEN_BUDGET} budget)"),
        fix="trim a HOT file (CLAUDE/PROTOCOLS/STATE/NEXT/INDEX/board) under budget",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def label_for(score: int) -> str:
    """Return the canonical severity label for a health score.

    Single source of truth — all tools must call this instead of
    re-implementing the bucket words (block-159 fix for WARNING vs DEGRADED divergence).
    Vocabulary: HEALTHY / DEGRADED / CRITICAL
    """
    if score >= 90:
        return "HEALTHY"
    if score >= 70:
        return "DEGRADED"
    return "CRITICAL"


def compute(arch_root: Path | str) -> HealthScore:
    """Build the canonical HealthScore for `arch_root` from real signals.

    Aggregates (never re-implements) audit errors/warnings, invariant
    criticals/warns, and HOT-boot-over-budget into one weighted breakdown.
    Accepted historical drift (governance/known-drift.md) is excused to 0 cost in
    BOTH the audit and invariant collectors so a documented, never-back-filled gap
    can't sink the score (block-149); a per-category cap keeps a light-warn pile
    from zeroing an otherwise-healthy root.

    Pure read; never raises — every collector degrades a failure to a 0-cost
    factor (and a missing known-drift.md simply excuses nothing) so a missing or
    erroring dependency can't crash a session or block close.
    """
    arch_root = Path(arch_root)
    # Each collector parses known-drift.md itself (one small read) so it stays
    # correct when called standalone or monkeypatched in isolation; compute()
    # passes nothing extra, keeping every collector a single-arg call.
    factors: list[Factor] = []
    factors.extend(_audit_factors(arch_root))
    factors.extend(_invariant_factors(arch_root))
    factors.append(_hot_boot_factor(arch_root))
    return HealthScore(factors=factors)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_report(arch_root: Path, health: HealthScore, n: int = 3) -> None:
    print("=" * 60)
    print("  cognitive-arch :: HEALTH MODEL")
    print(f"  arch-root: {arch_root}")
    print("=" * 60)
    print(f"  Health: {health.score}/100")
    print("-" * 60)

    drags = health.top_drags(n)
    if drags:
        print(f"  Top drags (worst {len(drags)} of {sum(1 for f in health.factors if f.cost > 0)}):")
        for f in drags:
            print(f"    -{f.cost:<3} [{f.key}] {f.detail}")
            print(f"         fix: {f.fix}")
    else:
        print("  Top drags: none — no factor is costing points (100/100).")

    print("-" * 60)
    print("  Full breakdown:")
    for f in health.factors:
        print(f"    -{f.cost:<3} {f.key}: {f.detail}")
    print("-" * 60)
    print(f"  score == max(0, 100 - {health.total_cost}) == {health.score}")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    force_utf8()
    parser = argparse.ArgumentParser(
        prog="health_model",
        description="Canonical, self-explaining project health score (one definition).",
    )
    parser.add_argument("--arch-root", default=".", help="Path to cognitive-arch root")
    parser.add_argument("--top", type=int, default=3,
                        help="How many top drags to show (default: 3)")
    args = parser.parse_args(argv)

    arch_root = Path(args.arch_root).resolve()
    health = compute(arch_root)
    _print_report(arch_root, health, n=args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
