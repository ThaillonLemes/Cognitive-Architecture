# Protocol: Phase retrospective generation

BRIEF: How to fill `templates/phase-retrospective.md`. Written at phase close. Synthesizes the phase's blocks and outcomes.

## Trigger

Generate a phase retrospective when:
- All blocks in the phase have status `done` (or `forced` with rationale)
- All exit criteria in the phase doc are met
- About to flip phase status to `complete`
- Per `commands/phase-close.md`

## Mode

**guardrails** to gather, **checklist** to validate.

## Inputs required

- Phase doc (`phases/phase-<N>.md`)
- All block retrospectives for the phase (`blocks/block-<NNN>-*.md`)
- BLOCK_LOG.md entries for the phase
- ADRs created during the phase (in `decisions/`)
- Audit reports during the phase (in `governance/`)
- STATE.md current

## Filling rules

### YAML frontmatter

- `id`: `phase-<N>-retro`
- `phase`: matches phase ID
- `status`: `complete`
- `blocks_completed`: count of blocks closed
- `blocks_planned`: count from phase doc (compare to detect deferrals)
- `exit_criteria_met`: N/M from phase doc §7
- `completed_at`: today's timestamp
- `duration_actual_days`: wall-clock from phase-start commit to phase-close commit
- `duration_estimated_days`: from phase doc (if estimated; compare for pattern observation)

### Body sections

**§1 Phase summary:**
One paragraph. What was delivered. Key outcomes. NO process narrative.

**§2 Blocks completed:**
Table of every block in the phase: ID | title | result (done/forced) | manifest path (now in `manifests/_archive/`).

**§3 Exit criteria:**
For each numbered criterion from the phase doc §7:
- Mark met / partially met / not met
- Provide evidence pointer (block ID where met, log file, retro section)
- If not fully met: explain how it was resolved or deferred

**§4 Decisions made (ADRs):**
List all ADRs created during the phase. Each: ADR ID, title, status.

**§5 Risks materialized:**
For each risk from phase doc §5:
- Fired? (yes/no)
- If fired: how mitigated (effective? partial?)

This captures pattern data for future phases.

**§6 Deferrals:**
List items that were declared out-of-scope OR moved to future:
- Item description
- Destination (Phase <N+1> | future phase | discarded)

**§7 Pattern observations:**
Forward-looking notes for future phases:
- Duration: actual vs estimated, percentage off
- Block tier mix (S/M/L counts) — was the mix accurate?
- Bottlenecks observed (if any)
- Tools/protocols that worked well
- Tools/protocols that hindered

**§8 Updates to PROJECT.md / design/:**
Any changes to project identity or domain docs during the phase:
- Stack changes
- Constraint updates
- Domain doc additions/changes

## Validation before save

- [ ] All blocks in phase doc §8 Block Index are accounted for (done, forced, or deferred to future)
- [ ] All exit criteria from phase doc §7 are evaluated (met / not met / deferred)
- [ ] §1-§4 always filled
- [ ] §5 filled if phase doc had a Risks section
- [ ] §6 always filled (even if "None")
- [ ] §7 always filled — even if "Estimate was accurate, no surprises"
- [ ] No narrative ramble — facts and evaluations only

## Post-save actions

After saving the phase retrospective:
1. Update phase doc status: `complete`
2. Archive all phase's manifests: `manifests/block-<NNN>-*.md` → `manifests/_archive/`
3. Update STATE.md: `p:<N+1> status:planned` (or `status:complete` if final phase)
4. Update NEXT.md: pointer to next phase or to project completion
5. Update INDEX.md: add brief for the phase retro
6. Trigger phase-close audit (per `commands/audit.md`)

## Output

Save to `phases/phase-<N>-retro.md`.

End of phase-retrospective-generation protocol.
