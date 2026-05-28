# Readiness Gate Protocol

BRIEF: Pre-flight check that must pass before generating a ROADMAP.md or any new phase. Evaluates whether the project has sufficient human-provided direction to plan coherently. If the gate fails, generates a targeted questionnaire instead of generating phases.

**The AI must never generate phases from incomplete domain knowledge. When in doubt, ask.**

---

## When to run

- Before invoking `protocols/roadmap-generation.md`
- Before generating any new phase via `protocols/phase-generation.md`
- Before running `commands/roadmap-refresh.md`

---

## The 4 Readiness Criteria

### R1 — PROJECT.md is complete

**Check:** Read `PROJECT.md`. Verify:
- All 10 identity fields are filled (name, type, language, framework, build/test/lint commands, description, target users, constraints)
- No field contains `[placeholder]`, `[TBD]`, `[YOUR_PROJECT_NAME]`, or equivalent
- Target users section is specific — names a real user type (e.g., "competitive MMORPG players aged 18–35") not generic ("everyone", "users", "people")

**Fail action:** List which fields are incomplete or too generic.

---

### R2 — Domain has at least 3 documented systems

**Check:** Read `design/02-domain-overview.md` and all other `design/` files. Count distinct named systems, each with:
- A name
- A one-paragraph description
- At least one identified user-facing behavior

**Minimum threshold:** 3 systems.

**Fail action:** List how many systems were found. Provide template for documenting the missing systems.

---

### R3 — Domain has depth beyond the overview

**Check:** At least one `design/` file beyond `design/02-domain-overview.md` must exist and have real content (not just a placeholder).

**Why:** The overview gives breadth; additional files give depth. A roadmap built only on the overview is too shallow for a multi-phase project.

**Fail action:** Identify which system is most important and request a `design/[system].md` for it.

---

### R4 — A concrete MVP endpoint is defined

**Check:** Either `PROJECT.md` or `design/02-domain-overview.md` must contain a statement that defines the Minimum Viable Product — what must work for the first "real" version. This can be:
- An explicit "MVP" section
- A "first user journey" statement
- A "Phase 1 done when..." statement

**Why:** Without an MVP anchor, the roadmap has no natural stopping point. The AI cannot determine how many phases are needed or when the delivery arc is complete.

**Fail action:** Ask: "What does the minimum version of this software look like? What must a user be able to do on day one of the public version?"

---

## Scoring and Action

| Score | Action |
|-------|--------|
| R1+R2+R3+R4 all pass | **PROCEED** — invoke roadmap-generation or phase-generation |
| Any criterion fails | **HALT** — generate readiness questionnaire, do not generate phases |

This gate is binary: all 4 must pass. There is no "conditional" band. The AI never generates phases with a partial pass.

---

## Questionnaire generation (on failure)

When the gate fails, generate `_brainstorm/readiness-questionnaire-YYYY-MM-DD.md` using `templates/readiness-questionnaire.md`. Include:
- Which criteria failed (R1, R2, R3, R4)
- The specific questions for each failed criterion
- Instructions: "Answer these questions to unlock phase generation. The AI will re-run the readiness gate after you fill this file."

Do NOT include all criteria questions — only the ones that failed. Do NOT speculate about answers.

---

## Out of scope

- Evaluating the quality of answers (that is `protocols/domain-phase-bridge.md`'s job).
- Checking block-level readiness (this is phase-level only).
- Running automatically (this is manually invoked before phase generation).

End of readiness-gate.md.
