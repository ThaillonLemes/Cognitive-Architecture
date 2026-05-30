---
id: block-146
tier: M
kind: implementation
phase: phase-25
scope: phase-bound
status: pending
security: false
dependencies:
  - block-145
files:
  read:
    - sdk/session_start.py
    - protocols/block-close-checklist.md
    - governance/tools-registry.yaml
    - sdk/invariant_check.py
  modify:
    - sdk/session_start.py
    - governance/tools-registry.yaml
  create:
    - sdk/tests/test_invariant_gate.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: session-start-surfaces-invariants
    type: command
    command: python sdk/session_start.py --arch-root .
    expect: "exits 0; prints an [INVARIANTS] line with critical/warn counts; never a traceback"
  - name: registry-has-invariant-check
    type: file-changed
    paths: [governance/tools-registry.yaml]
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-146-wire-gate.md]
created_at: 2026-05-30
---

# Block 146 — Wire invariant gate into block-close + session_start + registry

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Make drift visible and gating: surface invariant violations in `session_start`,
expose a HALT-worthy result for the block-close flow (critical → blocks the close),
and register an `invariant-check` tool so the checker runs every session.

## 2. Dependencies

- `block-145` (done) — checker + repair API exist.

## 3. Files

- **Read:** `sdk/session_start.py` (TOOL_RUNNERS + summary to extend),
  `protocols/block-close-checklist.md` (8-step gate flow; immutable, so NOT
  edited — see §6), `governance/tools-registry.yaml` (add entry),
  `sdk/invariant_check.py` (`run_all` + a `has_critical` helper).
- **Modify:**
  - `sdk/session_start.py` — add `run_invariant_check(arch_root)` to
    `TOOL_RUNNERS` (calls `invariant_check.run_all`), and a summary block that
    prints `[INVARIANTS] N critical, M warn` (CRITICAL tag when N>0). Wrap in
    try/except so it never blocks session start — like `_display_governor_notifications`.
  - `governance/tools-registry.yaml` — add an `invariant-check` tool
    (`command: python sdk/invariant_check.py --arch-root .`,
    `recommended_interval_days: 1`, `trigger_type: time`, `priority: high`,
    `last_run: "never"`, `mutable_by: master`).
- **Create:** `sdk/tests/test_invariant_gate.py` — gate HALTs (returns a
  critical-bearing result) on a tmp root with synthetic critical drift; passes
  (no critical) on a clean tmp root; `invariant-check` id is parseable from the
  registry; the session-start summary string contains `[INVARIANTS]`.

Block-close integration: `invariant_check` exposes `gate_result(arch_root) ->
(ok: bool, critical: list[Violation])`. `ok is False` ⇒ the close HALTs at
step 1 (validate_gates), consistent with the existing gate-fail flow. Since
`block-close-checklist.md` is `protection: immutable`, this block does NOT
rewrite it — the gate is invoked from close tooling and recorded in the
block-146 retro (DX note).

## 4. Validation

- `python -m pytest sdk/tests/ -q` passes.
- `python sdk/session_start.py --arch-root .` exits 0 and prints an `[INVARIANTS]`
  count line (it will show current criticals until block-147 clears them); no
  traceback even if an invariant errors.
- `tools-registry.yaml` parses via `session_start._parse_registry` and includes
  an `invariant-check` id (asserted in the test and by `test_tools_registry.py`).
- A tmp root seeded with a missing-retro BLOCK_LOG entry makes
  `gate_result()[0]` False; a clean tmp root makes it True.

## 5. Gates

Declared in frontmatter: tests-pass, session-start-surfaces-invariants,
registry-has-invariant-check, files-updated. The HALT behavior itself is proven
by `test_invariant_gate.py` (gate_result False on critical drift).

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Adding the checker to session_start crashes startup | High | `run_invariant_check` is wrapped in try/except (like governor display); a failure prints a warn line and continues — session start never aborts. |
| Editing the immutable block-close-checklist to add the gate | High | Do NOT edit it. The gate is invoked from close tooling and documented in this manifest + retro; the protocol file stays byte-identical (integrity lock unchanged). |
| False critical HALTs before block-147 clears the root | Med | Until block-147 reaches 0 critical, `gate_result` is advisory in the close step; block-147 flips it to enforcing. |
| New registry entry breaks `_parse_registry` | Low | Entry matches existing tools' field shape; `test_tools_registry.py` parses it. |

## 7. Out of Scope

- Rewriting `block-close-checklist.md` (immutable; would need an integrity-bump).
- Backfilling the real root to 0 critical — block-147.
- Auto-running repairs from session_start (checker reports only; repair stays an
  explicit `--repair --apply` call).
- A dashboard widget for invariants.

## 8. New Abstraction

None. Adds one `TOOL_RUNNERS` entry and one registry row, and a thin
`gate_result()` wrapper over the existing `run_all` from block-144. No new type.
