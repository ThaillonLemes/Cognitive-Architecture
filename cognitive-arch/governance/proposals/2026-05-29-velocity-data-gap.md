---
id: 2026-05-29-velocity-data-gap
status: rejected
pattern_id: velocity-data-gap
target_file: protocols/block-complexity-estimator.md
proposed_change: |
  [AI suggestion] Review and update protocols/block-complexity-estimator.md to address the recurring pattern 'velocity-data-gap'.
  Pattern detected 58 times. See evidence blocks below.
  Specific change: human should review the pattern and propose a concrete protocol amendment.
rationale: |
  Pattern 'velocity-data-gap' (INFO, Rule R6) has been detected 58 time(s),
  exceeding the governance threshold of 3.
  Description: 58 of last 111 blocks are missing actual_duration_hours.
created_at: 2026-05-29
resolved_at: 2026-05-30
resolved_by: proposal_resolver
signal_count_d1: 58
---

# Proposal — velocity-data-gap

## 1. Pattern

**Pattern ID:** `velocity-data-gap`
**Signal count (D1):** 58
**Severity:** info
**Rule:** R6

## 2. Proposed change

> Target file: `protocols/block-complexity-estimator.md`

Review and update `protocols/block-complexity-estimator.md` to address the recurring pattern. The AI has identified
this pattern is above threshold. A human should propose the specific protocol text change.

## 3. Rationale

58 of last 111 blocks are missing actual_duration_hours.

This pattern has occurred 58 times, which exceeds the governance threshold (3).
A protocol update may reduce future recurrence.

## 4. Evidence

Blocks affected:
- `block-001`
- `block-002`
- `block-003`
- `block-004`
- `block-005`
- `block-006`
- `block-007`
- `block-008`
- `block-009`
- `block-010`
- `block-011`
- `block-012`
- `block-013`
- `block-014`
- `block-015`
- `block-016`
- `block-017`
- `block-018`
- `block-019`
- `block-020`
- `block-021`
- `block-022`
- `block-023`
- `block-024`
- `block-025`
- `block-026`
- `block-027`
- `block-028`
- `block-029`
- `block-030`
- `block-031`
- `block-032`
- `block-033`
- `block-034`
- `block-035`
- `block-036`
- `block-037`
- `block-038`
- `block-039`
- `block-040`
- `block-043`
- `block-044`
- `block-045`
- `block-046`
- `block-047`
- `block-048`
- `block-049`
- `block-050`
- `block-051`
- `block-052`
- `block-053`
- `block-054`
- `block-055`
- `block-056`
- `block-057`
- `block-058`
- `block-059`
- `block-060`

## 5. Resolution

**Status:** rejected

_Human: set status to `accepted` or `rejected`, fill `resolved_at` and `resolved_by`._

_To apply: `python sdk/proposal_resolver.py --accept 2026-05-29-velocity-data-gap [--apply]`_

## Resolution Note

Historico aceito: blocos 001-060 sao anteriores ao campo actual_duration_hours (introduzido no bloco 086). Nao ha dado a recuperar. O bloco 138 ja garante o preenchimento daqui em diante via fallback de manifesto + rotulo MEASURED/ESTIMATED.
