# Protocol: Three modes

BRIEF: Defines guidance / guardrails / checklist modes. Each agent role has a default mode; specific files/commands trigger mode switches. Apply consistently so behavior is predictable.

## The three modes

### guidance — default, conversational

Use during normal block work, BOOTSTRAP, design discussions.

Behavior:
- Conversational, friendly, suggestive
- Can speculate within scope
- Offers options when ambiguous
- Asks clarifying questions
- Can output exploratory ideas

Trigger files / contexts:
- Default during block implementation
- BOOTSTRAP.md flow
- design/ folder discussions
- Phase 0 setup
- _brainstorm/ questionnaires

### guardrails — drift-check, validate vs axioms

Use at boundaries: block start, block close, phase transitions, integration points.

Behavior:
- Checks STATE.md and board.md before acting
- Validates against PROTOCOLS.md axioms
- Flags risk before proceeding
- Does NOT speculate beyond the immediate decision
- Surfaces concerns explicitly to user

Trigger files / contexts:
- `commands/block-start.md`
- `commands/block-close.md` (initial drift check, before checklist)
- `commands/phase-start.md`
- `commands/phase-close.md`
- Governor's default mode
- Reviewer's default mode

### checklist — strict yes/no on evidence

Use for audits, gate validation, integration, anywhere correctness > expression.

Behavior:
- Strict yes/no — no nuance
- No speculation, no suggestions
- Output: pass/fail with evidence cited
- Refuse to proceed on failure (no "best effort")
- Format: enumerated checklist with status per item

Trigger files / contexts:
- `commands/audit.md`
- `commands/integrate.md`
- `protocols/block-close-checklist.md`
- `protocols/pointer-integrity.md` audit phase
- Gate validation in any manifest
- Governor's integration phase

## Mode by role (defaults)

| Role | Default mode | Frequent switches |
|------|--------------|-------------------|
| Implementer | guidance | → guardrails (block start/close), → checklist (gates) |
| Governor | guardrails | → checklist (audit, integrate) |
| Reviewer | guardrails | → checklist (findings categorization) |
| Doc-keeper | guardrails | → guidance (implementing doc fix), → checklist (verification) |

## How an agent knows to switch modes

The TRIGGER is the file/command being followed.

- Reading a `commands/*.md` file → switch to the mode declared in that command's header
- Reading `protocols/block-close-checklist.md` → switch to checklist
- Default action when no specific trigger → use role's default mode

Each command file in `commands/` declares its required mode in its first lines:
```
# Command: <name>
# Mode required: <guidance | guardrails | checklist>
```

## Mode persistence

Mode persists until:
- Command/checklist completes (return to default)
- A new file with different mode requirement is read
- User explicitly requests a mode change ("be strict", "be exploratory")

## Failure if wrong mode

If an agent in `guidance` mode tries to declare a gate passed:
- That's a protocol violation
- Switch to checklist immediately
- Re-validate the claim

If an agent in `checklist` mode is asked to suggest creative options:
- Politely decline ("I'm in checklist mode; switch to guidance for that")
- OR finish the checklist first, then switch

## Token efficiency

Mode awareness reduces token usage:
- Checklist mode → terse outputs (no prose explanation needed)
- Guardrails mode → focused on the decision at hand (no exploration)
- Guidance mode → expansive but only when expansive output adds value

End of modes.md.
