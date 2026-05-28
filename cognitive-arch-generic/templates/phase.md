# Template: Phase doc

BRIEF: Skeleton for a phase roadmap doc. Phase docs go in `phases/phase-N.md`. Fill using `protocols/phase-generation.md`. Sections marked OPTIONAL are AI-decided based on phase complexity.

Copy this file to `phases/phase-<N>.md` and fill in placeholders.

---

```yaml
---
id: phase-<N>
status: planned                       # planned | active | complete
prev_phase: phase-<N-1>               # or "none" if first
exit_criteria_count: <number>
blocks_count: <number>
estimated_duration_minutes: <number>  # optional; Tier S≈15min, Tier M≈40min
created_at: YYYY-MM-DD
last_updated: YYYY-MM-DD
owner: <agent or human>
---
```

---

# Phase <N> — <Title>

BRIEF: 3 lines max — what this phase delivers in plain language.

## 1. Purpose [REQUIRED]

One paragraph. What does this phase accomplish? What is the outcome?

## 2. Goals [REQUIRED]

3-7 bullets. Each concrete and testable.
- Goal 1
- Goal 2
- ...

## 3. Invariants [OPTIONAL — include if phase has cross-cutting properties to preserve]

Properties that must hold true throughout the phase. Examples:
- API X remains backward-compatible
- Performance budget Y is not exceeded
- No new external dependencies

## 4. Dependencies [REQUIRED]

What must be true before this phase starts:
- Phase <N-1> exit criteria all met
- [Other prior phases or external dependencies]
- [Design docs that must be filled]

## 5. Risks [OPTIONAL — include if ≥3 blocks OR cross-system OR new abstraction]

| Risk | Impact | Mitigation |
|------|--------|------------|
| <risk> | <high/med/low> | <plan> |

## 6. Validation [OPTIONAL — include if phase introduces test types beyond unit]

How we know the phase is done. Test types that apply:
- Unit tests
- Integration tests
- End-to-end tests
- Performance benchmarks
- Soak tests
- Security audits

## 7. Exit Criteria [REQUIRED]

Numbered list. Every item AUDITABLE.
1. <criterion 1>
2. <criterion 2>
3. ...

## 8. Block Index [REQUIRED]

| Block | Title | Status | Manifest |
|-------|-------|--------|----------|
| <ID> | <title> | planned | `manifests/block-<ID>-<slug>.md` |

## 9. Dependency Graph & Parallel Execution Plan [OPTIONAL — include if ≥3 blocks with deps]

```yaml
parallel_execution_plan:
  total_blocks: <count>
  recommended_agents: <count>           # AI-computed from DAG
  groups:
    - id: <Na>
      blocks: [<id1>, <id2>]
      type: parallel | sequential
      depends_on: []                    # group IDs
    - id: <Nb>
      blocks: [<id3>]
      type: sequential
      depends_on: [<Na>]
```

## 10. Out of Scope [REQUIRED]

What this phase explicitly does NOT do:
- <deferral 1>
- <deferral 2>

---

End of phase template.
