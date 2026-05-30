---
id: phase-27
status: done
prev_phase: phase-26
exit_criteria_count: 6
blocks_count: 4
estimated_duration_minutes: 200
created_at: 2026-05-30
last_updated: 2026-05-30
owner: implementer
---

# Phase 27 — Guarded Self-Modification

BRIEF: Today the learning loop ends at a markdown a human reads — `--apply` only
appends an HTML comment. This phase closes the last mile: an accepted proposal
becomes a concrete, reviewable diff that passes the immutability/integrity guards,
runs the tests, and applies with automatic rollback on failure.

## 1. Purpose

The whole architecture observes itself, mines patterns, recommends, and proposes —
but it cannot yet *act* on its own conclusions. `proposal_resolver --accept --apply`
only annotates the target with an HTML comment; the real protocol edit is still
fully manual. This phase gives the system the ability to change itself **safely**:
an accepted proposal generates a concrete diff against its target file, the diff is
gated (immutable targets require the human integrity-bump; everything is backed up),
the change is applied and the test suite run, and any failure triggers an automatic
rollback. It is the offensive half of "an architecture that keeps itself honest," and
the capstone of the self-observation work — built on Phase 25's self-verification so
that self-modification can never bypass the architecture's own guards.

## 2. Goals

- `sdk/proposal_apply.py`: turn an `accepted` proposal into a concrete unified diff
  against its `target_file` (real edit, not an HTML-comment stub), with the rationale
  attached.
- Guard gates before any write: refuse immutable targets unless the
  `commands/integrity-bump.md` human gate is satisfied; back up the target to
  `_backups/`; run a structural/syntax sanity check on the result.
- Apply-with-rollback: write the change, run `sdk/tests/` (and `audit.py`); on any
  failure, restore from backup automatically and mark the proposal `apply-failed`.
- Provenance: every applied change is logged to `governance/governor-log.md` and
  generates an ADR stub in `decisions/`.
- An end-to-end demonstration on one real accepted proposal against a NON-immutable
  target (e.g., the `scope-expansion` recommendation → a manifest-generation
  checklist line), with apply + rollback both exercised.

## 3. Invariants

- No immutable file is ever modified without a recorded integrity-bump approval —
  enforced in code, reusing `proposal_resolver._is_immutable` + the lock.
- Every apply is reversible: backup first, rollback on any test/audit failure, no
  partial writes left behind.
- The test suite is the gate: a change that breaks any test is never kept.
- Acceptance stays human (`proposal_resolver --accept`); this phase automates only the
  *application* of already-accepted proposals.

## 4. Dependencies

- Phase 25 (self-verification + guard infrastructure, `_is_immutable`, integrity gate).
- Phase 26 optional (health model can score "pending applied changes") but not required.
- `proposal_resolver.py` (block-125), `protocol_updater.py` (block-122), `integrity_check.py`.

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A bad auto-applied diff corrupts a protocol | High | Backup-first + full-suite gate + auto-rollback; immutable targets hard-blocked without human bump; dry-run renders the diff for review before apply. |
| Self-modification feels unsafe / loss of control | High | Human still accepts every proposal; apply is opt-in per-proposal (`--apply`), renders the diff first, and is fully reversible. Never auto-applies on accept. |
| Diff generation produces an invalid edit | Med | Structural/syntax sanity check before write; if the diff doesn't apply cleanly, abort with the proposal left `accepted` (unchanged). |
| Rollback itself fails (partial state) | Med | Atomic write pattern (write to temp, swap); backup retained until a clean post-apply verify; test covers the rollback path explicitly. |

## 6. Validation

- Unit: diff generation from a synthetic proposal; immutable-guard refusal; backup
  creation; rollback restores byte-identical.
- Integration: end-to-end on one real accepted proposal against a non-immutable target
  — apply succeeds, tests pass; then a deliberately-breaking diff — apply rolls back.
- Regression: a test asserts an immutable target without a bump is refused.

## 7. Exit Criteria

1. `sdk/proposal_apply.py` turns an accepted proposal into a concrete unified diff against its `target_file`, rendered for review (dry-run), with tests.
2. Guard gates enforced in code: immutable target without integrity-bump → refused; target backed up to `_backups/` before any write; structural sanity check runs.
3. Apply-with-rollback: applies the diff, runs `sdk/tests/` + `audit.py`, and auto-restores from backup on any failure; proposal status reflects applied/apply-failed.
4. Every applied change is recorded in `governance/governor-log.md` and creates an ADR stub in `decisions/`.
5. One real accepted proposal taken end-to-end against a non-immutable target (apply path) AND a forced-failure case (rollback path), both with tests.
6. Full suite green; `sdk/audit.py` PASS, 0 errors; integrity lock all-OK; no immutable file modified without a recorded bump.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-152 | Proposal → concrete unified-diff generator (dry-run render) | M | done | `manifests/block-152-proposal-diff.md` |
| block-153 | Guard gates: immutability + integrity + backup + sanity | M | done | `manifests/block-153-guard-gates.md` |
| block-154 | Apply-with-rollback + provenance (log + ADR stub) | M | done | `manifests/block-154-apply-rollback.md` |
| block-155 | End-to-end demo (apply + forced rollback) + verify | M | done | `manifests/block-155-e2e-verify.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 27A
      blocks: [block-152]
      type: sequential
      depends_on: []
    - id: 27B
      blocks: [block-153, block-154]
      type: sequential        # 154 applies through 153's guards
      depends_on: [27A]
    - id: 27C
      blocks: [block-155]
      type: sequential
      depends_on: [27B]
```

## 10. Out of Scope

- Auto-accepting proposals (acceptance stays human).
- Auto-applying on accept (apply is a separate explicit step per proposal).
- Modifying immutable files without the human integrity-bump (always gated).
- Multi-file / cross-repo refactors driven by a single proposal (one target per proposal).
