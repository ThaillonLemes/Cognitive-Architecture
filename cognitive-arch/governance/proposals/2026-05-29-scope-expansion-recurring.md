---
id: 2026-05-29-scope-expansion-recurring
status: accepted
pattern_id: scope-expansion-recurring
target_file: templates/manifest-medium-v2.md
proposed_change: |
  [AI suggestion] Review and update templates/manifest-medium.md to address the recurring pattern 'scope-expansion-recurring'.
  Pattern detected 9 times. See evidence blocks below.
  Specific change: human should review the pattern and propose a concrete protocol amendment.
rationale: |
  Pattern 'scope-expansion-recurring' (WARN, Rule R4) has been detected 9 time(s),
  exceeding the governance threshold of 3.
  Description: 9 of last 111 blocks had files added beyond manifest.
created_at: 2026-05-29
resolved_at: 2026-05-30
resolved_by: proposal_resolver
signal_count_d1: 9
---

# Proposal — scope-expansion-recurring

## 1. Pattern

**Pattern ID:** `scope-expansion-recurring`
**Signal count (D1):** 9
**Severity:** warn
**Rule:** R4

## 2. Proposed change

> Target file: `templates/manifest-medium.md`

Review and update `templates/manifest-medium.md` to address the recurring pattern. The AI has identified
this pattern is above threshold. A human should propose the specific protocol text change.

## 3. Rationale

9 of last 111 blocks had files added beyond manifest.

This pattern has occurred 9 times, which exceeds the governance threshold (3).
A protocol update may reduce future recurrence.

## 4. Evidence

Blocks affected:
- `block-052`
- `block-053`
- `block-054`
- `block-055`
- `block-056`
- `block-057`
- `block-086`
- `block-094`
- `block-097`

## 5. Resolution

**Status:** accepted

_Human: set status to `accepted` or `rejected`, fill `resolved_at` and `resolved_by`._

_To apply: `python sdk/proposal_resolver.py --accept 2026-05-29-scope-expansion-recurring [--apply]`_
