# Protocol: Phase generation

BRIEF: How to fill `templates/phase.md` to produce a valid phase doc in `phases/phase-<N>.md`. Read this before generating any phase.

## Step 0 — Readiness Gate (MANDATORY — Phase 9+)

Before generating any phase, run `protocols/readiness-gate.md`. If the gate fails:
- Do NOT generate the phase.
- Generate `_brainstorm/readiness-questionnaire-YYYY-MM-DD.md` from `templates/readiness-questionnaire.md`.
- Ask the user to answer the questionnaire before proceeding.

The AI must never generate phases from insufficient domain knowledge. If in doubt, the gate returns the specific questions that need answers.

## Trigger

Generate a new phase doc when ANY of:
- Phase 0 completes → generate phase-1
- Previous phase (`phase-<N-1>`) has `status:complete` AND roadmap (`phase-0/03-roadmap-draft.md` or `phases/MASTER.md`) declares phase-N exists
- User explicitly requests: "generate phase-<N>"

## Mode

Switch to **guardrails** at start (verify previous phase is complete; verify roadmap supports next phase). After verification, switch to **guidance** for filling the template. Switch to **checklist** for final validation before saving.

## Inputs required

Read in order:
1. `PROJECT.md` — project identity, type, stack, vision
2. `phase-<N-1>.md` if exists, especially exit criteria
3. `phase-0/03-roadmap-draft.md` — envisioned phase outline
4. `design/` — relevant domain docs that affect this phase
5. Existing `phases/` to ensure no duplicate IDs

If any input is missing or contradictory, halt and ask the user.

## Filling rules

### Sections REQUIRED (always include)

- §1 Purpose
- §2 Goals
- §4 Dependencies
- §7 Exit Criteria
- §8 Block Index
- §10 Out of Scope

### Sections OPTIONAL (AI-decided per heuristic)

- **§3 Invariants** — include if phase has properties that must hold cross-block (e.g., "API X backward-compatible", "no new external deps"). Skip for small isolated phases.
- **§5 Risks** — include if (a) ≥3 blocks OR (b) cross-system impact OR (c) introduces a new abstraction. Skip for trivial phases.
- **§6 Validation** — include if phase introduces test types beyond unit (integration, soak, e2e, benchmark). Folded into §7 Exit Criteria for small phases.
- **§9 Dependency Graph & Parallel Execution Plan** — include if (a) ≥3 blocks AND (b) some blocks could run in parallel (per `protocols/parallelism.md`). Skip for 1-2 block linear phases.

### Heuristics for each section

**§1 Purpose:** One paragraph. Answer: "what does this phase accomplish?" Read PROJECT.md vision + previous phase exit + roadmap to determine. Be specific.

**§2 Goals:** 3-7 bullets. Each must be:
- Concrete (not vague)
- Testable (you could write a test or check)
- Distinct (no overlap with other goals)

If fewer than 3, phase is too small; consider merging with adjacent phase or making it a single-block task. If more than 7, phase is too large; split.

**§3 Invariants (optional):** Things that must remain true throughout. Example: "feature flag X stays at Disabled until block-NNN". Distinct from goals (goals are accomplishments; invariants are non-changes).

**§4 Dependencies:** Explicit list. For each:
- Phase ID OR specific exit criterion ID OR external dependency (e.g., "user fills `design/auth.md`")
- Verify each dependency exists or is plausibly resolvable

**§5 Risks (optional):** Table format. Each risk:
- Description (specific, not "things might go wrong")
- Impact (high/med/low)
- Mitigation (concrete plan, not "be careful")
- Owner (which agent/role catches this)

**§6 Validation (optional):** List test types that apply:
- Unit tests
- Integration tests
- E2E tests
- Performance benchmarks
- Soak / endurance tests
- Security audits
- Accessibility audits
- Other project-specific

**§7 Exit Criteria:** Numbered list. Every item AUDITABLE — someone (or audit.sh) can verify YES or NO.
- "Tests pass" is too vague → "All tests in `tests/<phase-N>/` directory pass"
- "Performance OK" is too vague → "p99 latency < 100ms in benchmark `bench-<name>`"

**§8 Block Index:** Table with all blocks IN this phase. Status starts as `planned`. Manifest path follows convention `manifests/block-<NNN>-<slug>.md`.

Block ID numbering: continue from last block in previous phase. Don't restart at 1.

**§9 Dependency Graph & Parallel Execution Plan (optional):**

Identify which blocks can run in parallel. Two blocks can run in parallel IFF:
- Neither depends on the other (no transitive dep either)
- `files.modify` sets are disjoint
- They don't reserve the same external resource

Group blocks into parallel groups. Each group has an ID (1a, 1b, 1c...). Groups have dependencies on other groups, not on individual blocks.

Output YAML:
```yaml
parallel_execution_plan:
  total_blocks: <N>
  recommended_agents: <M>             # max parallel agents needed
  groups:
    - id: 1a
      blocks: [<ID>, <ID>]
      type: parallel                  # parallel | sequential
      depends_on: []
    - id: 1b
      blocks: [<ID>]
      type: sequential
      depends_on: [1a]
```

`recommended_agents` = max width of the DAG (largest parallel group).

**§10 Out of Scope:** Explicit deferrals. What's adjacent but NOT in this phase. Prevents scope creep mid-phase.

## Validation before save

Switch to checklist mode and verify:

- [ ] YAML frontmatter parseable
- [ ] All REQUIRED sections present and filled
- [ ] OPTIONAL sections that AI decided to include are filled (not placeholders)
- [ ] All pointers (`phases/...`, `manifests/...`, `design/...`) resolve to existing files OR are explicitly marked "TBD — to be created"
- [ ] Exit criteria all auditable (each item could pass/fail definitively)
- [ ] Block index has ≥ 1 block
- [ ] If §9 included: all groups have ≥ 1 block; dep graph is acyclic

If any check fails: do not save. Halt and ask the user.

## Output

Save to `phases/phase-<N>.md`. Update INDEX.md to add a brief for the new phase.

Update STATE.md: `p:<N> status:planned`.

Update NEXT.md to point to the first block manifest (which will be generated next, per `commands/block-start.md`).

End of phase-generation protocol.
