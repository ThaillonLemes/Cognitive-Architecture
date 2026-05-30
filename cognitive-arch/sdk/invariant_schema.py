# sdk/invariant_schema.py
# PURPOSE: Invariant + Violation dataclasses — declarative shape for the anti-drift engine.
# INPUTS:  (imported by invariant_check.py and, later, the block-close gate)
# OUTPUTS: Invariant / Violation instances
# DEPS:    stdlib only (dataclasses, pathlib, typing)
# SEE:     sdk/invariant_check.py, phases/phase-25.md, sdk/pattern_schema.py

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# A check returns the list of violation messages it found ([] == clean).
CheckFn = Callable[[Path], list[str]]
# A repair (block-145) takes (arch_root, *, apply) and returns what it did/would do
# as RepairActions. Keyword-only `apply` keeps dry-run the unmistakable default.
RepairFn = Callable[..., "list[RepairAction]"]

SEVERITIES = ("critical", "warn")

# RepairAction.kind — the disposition of a single repair, ordered loosest→strictest:
#   "apply"  — a safe auto-fix the engine performed (or would, in dry-run)
#   "stage"  — a fix staged for a human gate; the engine NEVER writes the live file
#   "manual" — no auto-repair exists; the action describes the hand-fix
#   "halt"   — like manual, but signals work must stop until resolved
#   "noop"   — invariant already clean; nothing to do
#   "failed" — the repair itself errored; degraded, never propagated
REPAIR_KINDS = ("apply", "stage", "manual", "halt", "noop", "failed")


@dataclass
class Invariant:
    """A single architectural invariant: a named, severity-tagged check function.

    Invariants are DATA, not code branches — the engine iterates a registry of
    these, so adding one later is a registry entry + a check fn, never an edit to
    the engine's control flow.
    """

    id: str                                 # short stable id, e.g. "INV1"
    description: str                        # one-line human-readable statement
    severity: str                           # "critical" | "warn"
    check: CheckFn                          # (arch_root) -> list[str]; [] means clean
    repair: Optional[RepairFn] = None       # reserved for block-145; unused here


@dataclass
class Violation:
    """One concrete invariant failure emitted by the engine."""

    invariant_id: str                       # the Invariant.id that produced this
    severity: str                           # mirrors the invariant's severity
    message: str                            # human-readable summary line
    evidence: list[str] = field(default_factory=list)  # offending paths/ids/details


@dataclass
class RepairAction:
    """One thing a repair did, staged, or would do — the unit `repair_all` returns.

    SAFETY: a RepairAction is descriptive, not a promise the engine wrote anything.
    Only kind=="apply" with applied==True touched a file (and only after a backup).
    kind=="stage" means a human gate (e.g. integrity-bump) still owns the live write;
    the engine deliberately leaves the real file byte-identical even under --apply.
    """

    invariant_id: str                       # the Invariant.id this repair belongs to
    kind: str                               # one of REPAIR_KINDS
    description: str                        # human-readable summary of the action
    requires_human: bool = False            # True => a human gate must act (stage/manual/halt)
    applied: bool = False                   # True ONLY if a live file was actually written
    details: list[str] = field(default_factory=list)  # per-target lines / instructions
    backup_path: Optional[str] = None       # relative path of the backup taken (apply only)
