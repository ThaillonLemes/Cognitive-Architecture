---
id: block-148
tier: M
kind: implementation
phase: phase-26
scope: phase-bound
status: pending
security: false
dependencies:
  - block-137
files:
  read:
    - sdk/project_state.py
    - sdk/audit.py
    - sdk/health_report.py
    - sdk/invariant_check.py
  create:
    - sdk/health_model.py
    - sdk/tests/test_health_model.py
gates:
  - name: tests-pass
    type: command
    command: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: health-model-smoke
    type: command
    command: python sdk/health_model.py --arch-root .
    expect: exits 0; prints "Health: <N>/100" and a non-empty "Top drags" list
  - name: breakdown-sums
    type: command
    command: python -m pytest sdk/tests/test_health_model.py -q
    expect: "0 failed" (asserts score == 100 - sum(factor.cost))
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md, blocks/block-148-health-model.md]
created_at: 2026-05-30
---

# Block 148 — Canonical health model + self-explaining top_drags

- **Tier:** M
- **Kind:** implementation
- **Status:** pending
- **Parallel-with:** none (gates blocks 149 & 150)

## 1. Purpose

Create one canonical `HealthScore` (score + weighted factor breakdown) that every
instrument reads, derived from `project_state` + invariants + audit signals — and
make it explain itself: `top_drags(n)` returns the worst factors with point cost and
a one-line fix each. This is the single definition that block-149 wires audit and
health_report onto.

## 2. Dependencies

- `block-137` (project_state — canonical phase/BLOCK_LOG reader).
- Soft: `invariant_check.py` (Phase 25 / block-144). It may not exist yet; the model
  imports it defensively and contributes an `invariants` factor only when present
  (absent → that factor scores 0 cost, never crashes — mirrors `analyze()` resilience).

## 3. Files

- **Read:** `sdk/project_state.py` (phase/block counts), `sdk/audit.py`
  (`run_audit` → `AuditResult.errors/warnings`; reuse, do not re-walk files),
  `sdk/health_report.py` (the duplicate `_section_audit` scorer this model replaces),
  `sdk/invariant_check.py` (invariant results, if present).
- **Create:** `sdk/health_model.py` — `Factor(name, weight, cost, fix)` dataclass;
  `HealthScore(score, factors)` with `top_drags(n)`; `compute(arch_root) -> HealthScore`.
  `sdk/tests/test_health_model.py`.

## 4. Validation

- All tests pass: `python -m pytest sdk/tests/ -q`.
- `python sdk/health_model.py --arch-root .` exits 0, prints `Health: N/100` plus a
  ranked `Top drags` list (each line: factor, −points, one-line fix).
- Unit: synthetic arch-roots (clean → 100; injected errors/warnings → expected cost);
  `top_drags(3)` returns the 3 highest-cost factors sorted descending, each carrying a
  non-empty `fix`; **the invariant `score == 100 - sum(f.cost for f in factors)`** holds
  (no double-counting — Phase 26 §3).

## 5. Gates

Declared in frontmatter: `tests-pass`, `health-model-smoke`, `breakdown-sums`,
`files-updated`. The `breakdown-sums` gate is the load-bearing one — it pins the
"a number with no breakdown is a bug" invariant.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model double-counts audit + invariant signals (an audit WARN that an invariant also flags) | Med | Single weighting table; factors namespaced (`audit.*`, `invariant.*`, `state.*`); `breakdown-sums` test asserts total = sum of parts. |
| `invariant_check` absent (Phase 25 not yet merged) crashes import | High | `try/except ImportError`; absent → `invariants` factor cost 0 with fix "land Phase 25". Model never raises. |
| New score differs from today's familiar 100, alarming a reader | Med | This block only *defines* the model; block-149 documents the mapping and reconciles the surfaces. |

## 7. Out of Scope

- Editing `audit.py` or `health_report.py` to consume the model — that is block-149.
- Risk/forecast factors (blocks 150–151).
- New audit checks or invariants (model aggregates existing signals only).
- Dashboard rendering of the breakdown (dashboard already consumes a score line).

## 8. New Abstraction

`HealthScore` + `Factor` (Axiom Q1 — Rule of Three satisfied: audit.py,
health_report.py, and the future dashboard each currently derive "health" their own
way; this is the one type all three collapse onto). Justified: it is the single
canonical health definition the whole phase is built to enforce.
