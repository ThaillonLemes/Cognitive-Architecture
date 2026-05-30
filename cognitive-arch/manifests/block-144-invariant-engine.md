---
id: block-144
tier: M
kind: implementation
phase: phase-25
scope: phase-bound
status: pending
security: false
dependencies:
  - block-137
files:
  read:
    - sdk/project_state.py
    - sdk/integrity_check.py
    - sdk/pattern_analyzer.py
    - blocks/BLOCK_LOG.md
    - governance/proposals/index.md
  modify: []
  create:
    - sdk/invariant_schema.py
    - sdk/invariant_check.py
    - sdk/tests/test_invariant_check.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: checker-runs-clean-exit
    type: command
    command: python sdk/invariant_check.py --arch-root .
    expect: "exits 0; prints one line per invariant (id + severity + OK/VIOLATION); never a traceback"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-144-invariant-engine.md]
created_at: 2026-05-30
---

# Block 144 — Invariant registry + checker engine

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Build the declarative invariant layer: an `Invariant` dataclass plus an engine
that registers the six real-drift invariants (INV1–INV6 from phase-25 §2) and
runs them, returning violations. The engine never raises — a failing check is
reported, not propagated (mirrors `pattern_analyzer.analyze`).

## 2. Dependencies

- `block-137` (done) — `project_state.py` is the canonical BLOCK_LOG/phase reader.

## 3. Files

- **Read:** `sdk/project_state.py` (completed_block_ids, current_phase reader),
  `sdk/integrity_check.py` (load_lock / find_immutable_files — reused by INV1),
  `sdk/pattern_analyzer.py` (never-crash style to mirror), `blocks/BLOCK_LOG.md`
  (INV2/INV5 input shape), `governance/proposals/index.md` (INV6 table shape).
- **Modify:** none.
- **Create:**
  - `sdk/invariant_schema.py` — `@dataclass Invariant`: `id: str`,
    `description: str`, `severity: str` ("critical" | "warn"),
    `check: Callable[[Path], list[str]]` (returns violation messages, [] = clean),
    `repair: Callable[[Path, bool], list[str]] | None = None` (reserved for
    block-145; unused here). Also a `Violation` record (`inv_id`, `severity`,
    `message`) the engine emits.
  - `sdk/invariant_check.py` — `REGISTRY: list[Invariant]` with INV1–INV6;
    `run_all(arch_root) -> list[Violation]` wrapping each `check` in try/except
    so one broken invariant degrades to a single `warn`, not a crash; `__main__`
    prints one line per invariant and exits 0 (`--strict` added in block-146).
  - `sdk/tests/test_invariant_check.py` — per-invariant fires-on-drift +
    clean-on-healthy, using `tmp_path` fixtures.

The six seeded checks (read-only here; repairs land in block-145):

- **INV1** (critical): every `protection: immutable` file (via
  `integrity_check.find_immutable_files`) appears in `load_lock` keys.
- **INV2** (critical): every `done` id in `project_state.completed_block_ids`
  has a `blocks/block-<id>-*.md` retro file.
- **INV3** (warn): every retro with `actual_duration_hours` resolves a tier
  (frontmatter `tier:` or manifest fallback).
- **INV4** (warn): every id in `session_start.TOOL_RUNNERS` is a registry id
  or a known event tool (read TOOL_RUNNERS by import, not by re-listing).
- **INV5** (critical): `STATE.last_block` == last `completed_block_ids` entry.
- **INV6** (warn): every `governance/proposals/*.md` file ↔ a row in
  `proposals/index.md`, both directions.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q`.
- `python sdk/invariant_check.py --arch-root .` exits 0 and prints a per-invariant
  status line with no traceback (it WILL report INV2 block-085 + INV1 lock gaps as
  current violations — that is expected; block-147 clears them).
- Inject a synthetic drift (e.g. a temp BLOCK_LOG entry with no retro) in a test
  tmp root → the matching invariant returns a non-empty violation list; a healthy
  tmp root → empty.

## 5. Gates

Declared in frontmatter: tests-pass, checker-runs-clean-exit (proves never-raises +
clean exit), files-updated. No HALT gate yet — wiring is block-146.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A buggy `check` fn crashes the engine | High | `run_all` wraps every check in try/except; a raised check becomes one `warn` Violation (`"<id>: check errored"`), never propagates. Mirrors `pattern_analyzer`. |
| INV4 drifts if it re-lists TOOL_RUNNERS | Med | INV4 imports `session_start.TOOL_RUNNERS` at check time, tracking the real dict, not a copy. |
| Real-root false positives noise the gate later | Med | Severity tuned in block-147; only critical HALTs (block-146). |

## 7. Out of Scope

- Auto-repair functions (`repair` field stays `None`) — block-145.
- Wiring into session_start / block-close / registry — block-146.
- Backfilling the block-085 retro or the lock — block-147.
- New invariants beyond INV1–INV6.

## 8. New Abstraction

`Invariant` dataclass + `Violation` record (Axiom Q1 — Rule of Three satisfied:
six concrete invariants share exactly this shape, and block-145/146 add a 7th+8th
consumer of it). Justified: invariants must be data (a registry entry + a fn), not
code branches, so the engine stays open for extension without modification.
