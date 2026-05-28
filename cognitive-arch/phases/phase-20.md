---
id: phase-20
status: done
prev_phase: phase-19
exit_criteria_count: 5
blocks_count: 5
estimated_duration_minutes: 125
created_at: 2026-05-28
last_updated: 2026-05-28
owner: implementer
---

# Phase 20 — Learning Loop

BRIEF: The system learns from its own patterns and proposes protocol updates. When pattern_analyzer detects a recurring signal above threshold, sdk/protocol_updater.py drafts a governance/proposals/ entry. Proposals appear at session start and persist until accepted or rejected. Accepted proposals optionally patch the target protocol file.

## 1. Purpose

Pattern mining (Phase 14) detects recurring issues. But detection without action is passive. Phase 20 closes the loop: detected patterns above threshold automatically generate formal proposals to update the protocol that caused them. A proposal is a structured suggestion (what to change, which protocol file, what text, why) that the user reviews at session start. Accepting a proposal triggers sdk/proposal_resolver.py which can patch the target file automatically or present a diff for manual application. This turns the system's self-observation into self-improvement.

## 2. Goals

- governance/proposals/ directory with proposal.md schema (pending|accepted|rejected status)
- sdk/protocol_updater.py generates proposals from patterns with D1 signal count ≥ 3
- session_start.py shows pending proposal count and link at every session start
- Dashboard proposals section: list of pending/accepted/rejected with summary
- sdk/proposal_resolver.py --accept/--reject updates status and optionally patches target protocol file

## 3. Invariants

- Proposals never auto-apply without human --accept; user is always in the loop
- Rejected proposals are archived, not deleted (learning history)
- A proposal references exactly one target file and one specific change
- protocol_updater.py never creates duplicate proposals for the same pattern + target combo
- Accepted proposals that patch files create a backup (.bak) before modification

## 4. Dependencies

- Phase 14 complete (pattern_analyzer.py produces patterns with signal counts)
- Phase 15 complete (session_start.py exists and can be extended)
- governance/patterns.md exists and is current

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Proposals accumulate faster than user acts on them | Med | session_start shows count; proposals older than 14 days auto-escalate to WARN |
| Auto-patch corrupts target protocol file | High | Always creates .bak; dry-run mode default; --apply required for actual write |
| Protocol updates conflict with immutable files | Med | proposal_resolver checks protection field before patching; rejects if immutable |
| Pattern threshold too low → noise proposals | Low | D1 ≥ 3 threshold; configurable in governance/patterns-config.yaml |

## 6. Validation

- Run `python sdk/protocol_updater.py --arch-root . --dry-run` — produces proposals without writing files
- Run `python -m pytest sdk/tests/ -q` — 0 failures
- Verify session_start.py output includes proposal count line
- Accept a test proposal with --apply; verify .bak file created and target file patched correctly

## 7. Exit Criteria

1. `governance/proposals/` directory with `proposal.md` schema; proposals have: id, status (pending|accepted|rejected), pattern_id, target_file, proposed_change (text diff or instruction), rationale, created_at, resolved_at.
2. `sdk/protocol_updater.py` runs after pattern_analyzer, generates a proposal entry for each pattern with `signal_count_d1 ≥ 3`; never creates duplicate proposals for same pattern+target.
3. `session_start.py` shows pending proposal count at every session start: `[PROPOSALS] N pending — see governance/proposals/`; count appears even if N=0 (shows "0 pending — none to review").
4. `sdk/proposal_resolver.py --accept <id> [--apply]` sets status:accepted; with `--apply` patches target file (creates .bak first, aborts if target is immutable). `--reject <id>` sets status:rejected with optional note.
5. Dashboard proposals widget: pending count badge + table of last 5 proposals with status and target_file.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-121 | proposals/ schema | S | planned | `manifests/block-121-proposals-schema.md` |
| block-122 | protocol_updater.py | M | planned | `manifests/block-122-protocol-updater.md` |
| block-123 | session_start proposals | S | planned | `manifests/block-123-session-start-proposals.md` |
| block-124 | dashboard proposals widget | S | planned | `manifests/block-124-dashboard-proposals.md` |
| block-125 | proposal_resolver.py | M | planned | `manifests/block-125-proposal-resolver.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 5
  recommended_agents: 1
  groups:
    - id: 20A
      blocks: [block-121]
      type: sequential
      depends_on: []
    - id: 20B
      blocks: [block-122]
      type: sequential
      depends_on: [20A]
    - id: 20C
      blocks: [block-123, block-124]
      type: parallel
      depends_on: [20B]
    - id: 20D
      blocks: [block-125]
      type: sequential
      depends_on: [20C]
```

Schema first; updater second; session integration and dashboard in parallel; resolver last.

## 10. Out of Scope

- Proposals for non-protocol files (e.g. STATE.md, board.md)
- Multi-step proposals (one change per proposal; complex changes require multiple proposals)
- Proposal voting / multi-agent review
- Auto-applying proposals without human confirmation (always requires --accept --apply)

---

End of phase-20.
