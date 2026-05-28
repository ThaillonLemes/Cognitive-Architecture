# Template: Phase Retrospective

BRIEF: Written at phase close. Synthesizes all blocks in the phase. Located at `phases/phase-<N>-retro.md`. Fill using `protocols/phase-retrospective-generation.md`.

---

```yaml
---
id: phase-<N>-retro
phase: phase-<N>
status: complete
blocks_completed: <count>
blocks_planned: <count>
exit_criteria_met: N/M
completed_at: YYYY-MM-DDTHH:MMZ
duration_actual_days: <number>
duration_estimated_days: <number>
---
```

---

# Phase <N> Retrospective — <Title>

## 1. Phase summary

One paragraph: what was delivered, key outcomes.

## 2. Blocks completed

| Block | Title | Result | Manifest |
|-------|-------|--------|----------|
| <NNN> | <title> | done | `manifests/_archive/block-<NNN>-<slug>.md` |

## 3. Exit criteria

For each numbered criterion from the phase doc:
1. <criterion 1> — ✓ met (evidence: <where>)
2. <criterion 2> — ✓ met
3. ...

If any criterion not met: explain how it was resolved or deferred.

## 4. Decisions made (ADRs)

ADRs introduced during this phase:
- ADR-<NNN>: <title>

## 5. Risks materialized

From the phase doc Risk table — which actually fired and how mitigated:
- Risk: <description> → Result: <fired/avoided>; Mitigation worked: <yes/no>

## 6. Deferrals

What was out-of-scope and where it goes:
- <item> → Phase <N+1> | future | discarded

## 7. Pattern observations

Anything to feed forward to future phases:
- Estimated duration was off by <X%> because <reason>
- Block tier mix: <S/M/L counts>; effort distribution observed
- Bottlenecks: <if any>

## 8. Updates to PROJECT.md / design/

Document any changes to project identity or domain docs during the phase.

---

End of phase retrospective.
