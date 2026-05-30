---
id: block-144
phase: phase-25
tier: M
status: done
actual_duration_hours: 0.8
duration_source: estimated
gates_passed: 3/3
created_at: 2026-05-30
---

# Block 144 Retrospective — Invariant registry + checker engine

## 1. What was built

- `sdk/invariant_schema.py` — stdlib dataclasses `Invariant(id, description, severity,
  check, repair=None)` and `Violation(invariant_id, severity, message, evidence)`.
  `repair` reserved for block-145.
- `sdk/invariant_check.py` — engine with a `REGISTRY` of 6 invariants (as data) and
  `run_all(arch_root) -> list[Violation]` that wraps every check in try/except (a
  raising check degrades to one `warn` Violation, never propagates — mirrors
  `pattern_analyzer.analyze`). CLI prints per-invariant status + violations grouped by
  severity, exits 0.
- `sdk/tests/test_invariant_check.py` — 21 tests: fires-on-drift + clean-on-healthy for
  INV1-INV6, never-raises on empty/malformed arch, degrade-to-warn, registry ≥6, CLI.

## 2. The six invariants

- INV1 (critical): every `protection: immutable` file ∈ `.integrity.lock`.
- INV2 (warn): every `block-NNN done` in BLOCK_LOG has a `blocks/block-NNN-*.md` retro.
- INV3 (warn): every retro with `actual_duration_hours` resolves a tier (retro or manifest).
- INV4 (critical): every `session_start.TOOL_RUNNERS` key ∈ `tools-registry.yaml`.
- INV5 (warn): `STATE.last_block` == highest BLOCK_LOG block; `NEXT` not pointing at a done block.
- INV6 (warn): every `proposals/*.md` ↔ a row in `proposals/index.md`.

## 3. Gates

- tests-pass: 819 passed, 0 failed (21 new) ✓
- invariant-cli-clean: `python sdk/invariant_check.py --arch-root .` exits 0, no traceback ✓
- never-raises: `run_all` on the real arch-root returns a list (35 violations), never raises ✓

## 4. Real-arch-root scan — what block-147 must reconcile

- **6 critical (INV1):** immutable-tagged files not in `.integrity.lock`. ⚠️ Mostly
  FALSE POSITIVES — `integrity_check.find_immutable_files` matches the literal substring
  `protection: immutable` ANYWHERE (incl. prose in manifests/phase docs that merely
  discuss it). block-147 should tighten `find_immutable_files` to match the frontmatter
  field only, then re-scan.
- **25 warn (INV2):** blocks **061-085** are `done` with no retro file (the manifest
  only flagged 085 — the real gap is the whole range).
- **4 warn (INV3):** blocks 108-111 have `actual_duration_hours` but no resolvable tier.
- INV4, INV5, INV6: clean.

## 5. Decision (severity source)

Followed the orchestrator's severity assignment (INV2=warn, INV4=critical, INV5=warn)
over the manifest §3 draft; documented inline in `REGISTRY`. Rationale: critical should
gate block-close, and a missing historical retro (INV2) should not HALT work, whereas a
tool-runner/registry mismatch (INV4) or immutable-lock gap (INV1) should.

## 6. Files actually touched

As manifest (sdk/invariant_schema.py, sdk/invariant_check.py, sdk/tests/test_invariant_check.py created).
