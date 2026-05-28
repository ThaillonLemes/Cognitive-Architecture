# Domain Coverage Matrix Protocol

BRIEF: Defines the Coverage Matrix — a structured cross-reference between design/ domain concepts and phases/. Three gap types are detected and classified. Use `commands/coverage-check.md` to build the matrix for a project.

---

## What is the Coverage Matrix?

The Coverage Matrix is a table that maps every domain system (from design/) to the phase(s) that implement it, and every phase to the domain system(s) it covers. It reveals three types of gaps:

| Gap type | Definition | Severity |
|----------|-----------|---------|
| **UNCOVERED** | A system in design/ has no phase implementing it and no Track assigned. | ERROR — work is missing from the plan. |
| **DRIFT** | A phase exists but references no documented design/ concept. | WARN — scope may be undocumented or invented. |
| **STALE** | A phase implements a system, but the design/ file for that system has been updated since the phase was written. | WARN — phase may be out of date with current domain understanding. |

---

## Matrix Format

```
COVERAGE MATRIX — [Project Name]
Generated: YYYY-MM-DD

| System (design/) | Phase(s) | Track? | Status |
|-----------------|---------|--------|--------|
| Combat          | Phase 3  | track/combat.md | COVERED |
| Replication     | Phase 2  | track/replication.md | COVERED |
| Auth            | Phase 1  | — | COVERED |
| Economy         | —        | — | UNCOVERED |

| Phase | Systems covered | Status |
|-------|----------------|--------|
| Phase 1 | Auth, Network | OK |
| Phase 2 | Replication, World | OK |
| Phase 99 | — | DRIFT |

GAPS:
UNCOVERED: Economy (no phase, no track)
DRIFT: Phase 99 (no design/ concept found)
STALE: (none)
```

---

## Detection Algorithm

### Detecting UNCOVERED systems

1. Enumerate all `design/*.md` files (exclude `_placeholder.md`, `README.md`, `governor-v2.md`).
2. For each file, extract the system name (use filename as proxy if no explicit name).
3. Search all `phases/*.md` files for references to that system name (case-insensitive).
4. If no phase references the system AND no Track file (`tracks/*.md`) references it: mark UNCOVERED.

### Detecting DRIFT phases

1. Enumerate all `phases/phase-N.md` files.
2. For each phase, extract the systems it declares to implement (from BRIEF, Goals, or Block Index descriptions).
3. Search all `design/*.md` for those system names.
4. If none of the phase's systems appear in any design/ file: mark DRIFT.

**Note:** A phase that implements a new system not yet documented in design/ is not DRIFT — it is a documentation lag. DRIFT applies only when the phase cannot be connected to ANY design concept after careful reading.

### Detecting STALE phases

1. For each phase that covers a system: find the corresponding design/ file.
2. Compare last-modified dates: if `design/system.md` was modified after `phases/phase-N.md` was created, check if the phase's scope still aligns with the updated design.
3. If the design update added new subsystems or changed assumptions: mark STALE.

**Implementation note:** Date-based detection is approximate. The AI executor should use judgment when design/ files change — a spelling fix is not a STALE trigger; a new subsystem is.

---

## Severity and action

| Gap type | Action required |
|----------|----------------|
| UNCOVERED | For each uncovered system: create a phase, assign a Track, or explicitly defer. Record the decision in ROADMAP.md §7. |
| DRIFT | For each drift phase: either document the corresponding system in design/, or remove the phase from the roadmap. |
| STALE | For each stale phase: review the updated design/ content. Update the phase scope if needed. Record in phase-N.md under a `## Scope Revision` section. |

---

## Out of scope

- Automatically resolving gaps (that is `commands/roadmap-refresh.md`'s job — proposes, never auto-applies).
- Checking block-level coverage (this is phase-level only).
- Coverage of Track Blocks (Tracks are managed by `protocols/track-priority.md`).

End of domain-coverage-matrix.md.
