# Protocol: Brainstorm pattern v1 (large questionnaires)
# Status: SUPERSEDED — see protocols/brainstorm-pattern-v2.md
# Updated: block-110 (Phase 17) — v1 kept for reference; new sessions must use v2.

> **⚠️ This is Brainstorm v1.** New brainstorm sessions MUST use
> `protocols/brainstorm-pattern-v2.md` (AI-recommended answers + confidence bands).
> This document is retained for historical reference only.

BRIEF: How to conduct large-scale brainstorms for design docs (filling `design/` content). Comprehensive questionnaire → batch user response → synthesis.

## When to use

This pattern fits for:
- Filling a large `design/` doc with many open decisions
- Initial Phase 0 domain exploration (after PROJECT.md is filled)
- Revisiting a design when many decisions need updating
- ADR clusters (multiple related decisions in one session)

NOT for:
- Small clarifying questions (just ask 1-2 things)
- Block-level planning (use manifests instead)
- Code review

## Pattern

### Step 1 — Identify scope

Determine what doc / topic the brainstorm covers. Example:
- "Combat system design" → fills `design/combat.md`
- "Authentication flow" → fills `design/auth.md`
- "Pricing tiers" → fills `design/pricing.md`

### Step 2 — Generate questionnaire to scratchpad

Generate a comprehensive questionnaire file at `_brainstorm/<topic>-questionnaire.md`. Structure:

- Intro: explain workflow to user
- Parts (categorized): Part A (Identity), Part B (...), Part C (...), etc.
- Each part has multiple questions
- Each question:
  - Title
  - The question itself
  - 2-5 distinct suggestions
  - "Why distinct" rationale (explicit reason each suggestion exists separately)

### Step 3 — User responds in batch

User reads questionnaire (file), responds via:
- Code references ("A1=2, A3=own, C5=1+modified to ...")
- Direct edits to the file
- Chat messages referencing IDs

### Step 4 — Synthesize into design doc

Once user responds, synthesize answers into the final `design/<topic>.md`. The questionnaire stays in `_brainstorm/` as artifact; the synthesis is the canonical doc.

### Step 5 — Cleanup

After synthesis is committed:
- Keep questionnaire in `_brainstorm/` for audit trail
- Or delete if you want clean state — decisions are now in `design/` + ADRs

## Question style

Each question:

```markdown
### A1. [Title]

**Question:** [the actual question]

**Suggestions:**

1. **[Title]** — [description]. [Pros / when this fits].
2. **[Title]** — [description]. [Pros / when this fits].
3. **[Title]** — [description].

**Why distinct:** [explicit reason why these are separate, not combinable]
```

## Suggestion rules

- Minimum 2 suggestions per question
- Each suggestion must be DISTINCT from others (not just rewordings)
- Each suggestion has a reason for being separate
- One suggestion can be marked "(Recommended)" if AI has strong preference
- User is expected to override or write their own

## Anti-patterns

- Suggestions that overlap or could be combined (defeats purpose)
- Single suggestion masquerading as a question (just propose, not brainstorm)
- Questions too vague (user can't answer without more context)
- Too few questions to feel comprehensive (5 questions in a doc is shallow)

## Scope sizing

| Doc type | Typical questionnaire size |
|----------|---------------------------|
| Small design doc | 15-25 questions |
| Medium design doc | 30-50 questions |
| Large foundational doc (pillars, combat) | 50-70+ questions |

## Mode

Generation: **guidance** (creative, comprehensive)
Synthesis: **guardrails** (capture user decisions accurately)

## Pointers

- Questionnaire scratchpad: `_brainstorm/`
- Final synthesized docs: `design/`
- Decisions as ADRs: `decisions/`

End of brainstorm-pattern.
