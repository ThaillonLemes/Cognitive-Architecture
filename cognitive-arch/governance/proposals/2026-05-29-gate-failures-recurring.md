---
id: 2026-05-29-gate-failures-recurring
status: accepted
pattern_id: gate-failures-recurring
target_file: protocols/block-close-checklist.md
proposed_change: |
  [AI suggestion] Review and update protocols/block-close-checklist.md to address the recurring pattern 'gate-failures-recurring'.
  Pattern detected 4 times. See evidence blocks below.
  Specific change: human should review the pattern and propose a concrete protocol amendment.
rationale: |
  Pattern 'gate-failures-recurring' (WARN, Rule R3) has been detected 4 time(s),
  exceeding the governance threshold of 3.
  Description: 4 of last 111 blocks had at least one gate failure.
created_at: 2026-05-29
resolved_at: 2026-05-30
resolved_by: proposal_resolver
signal_count_d1: 4
---

# Proposal — gate-failures-recurring

## 1. Pattern

**Pattern ID:** `gate-failures-recurring`
**Signal count (D1):** 4
**Severity:** warn
**Rule:** R3

## 2. Proposed change

> Target file: `protocols/block-close-checklist.md`

Review and update `protocols/block-close-checklist.md` to address the recurring pattern. The AI has identified
this pattern is above threshold. A human should propose the specific protocol text change.

## 3. Rationale

4 of last 111 blocks had at least one gate failure.

This pattern has occurred 4 times, which exceeds the governance threshold (3).
A protocol update may reduce future recurrence.

## 4. Evidence

Blocks affected:
- `block-125`
- `block-127`
- `block-131`
- `block-132`

## 5. Resolution

**Status:** accepted

_Human: set status to `accepted` or `rejected`, fill `resolved_at` and `resolved_by`._

_To apply: `python sdk/proposal_resolver.py --accept 2026-05-29-gate-failures-recurring [--apply]`_
