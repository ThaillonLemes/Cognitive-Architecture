---
protection: immutable
protection_reason: "AI-only file vocabulary. Changes here invalidate STATE.md, NEXT.md, board.md parsing across all agents."
restore_command: "git checkout HEAD -- _syntax.md"
---

# _syntax — AI-only file vocabulary

BRIEF: dense key:value vocabulary used in ALL agent communication: HOT files (STATE.md, NEXT.md, board.md, AGENT.md, INDEX.md), task packets (Governor → sub-agent), and return packages (sub-agent → Governor). Read once per session. Apply consistently.

## Keys (alphabetical)

```
agent:         agent identifier (e.g., agent-1a, governor, agent-reviewer)
axioms:        comma-separated axiom IDs relevant to block (e.g., Q3,Q4,C2,C6)
b:             block number (numeric, compact; e.g., b:094)
blocked_by:    comma-separated block IDs blocking this work
blocks_done:   comma-separated block IDs completed in current phase
commits:       commits since last sync (numeric)
created_at:    ISO 8601 timestamp
deps:          comma-separated block IDs this depends on
files:         comma-separated file paths (generic; prefer fread:/fmod: in task packets)
fmod:          files modified — path:lines_changed pairs (e.g., fmod:INDEX.md:2,STATE.md:1)
fread:         files read during execution (comma-separated paths)
gates:         N/M (N passed of M total) OR gate-name:pass|fail pairs (e.g., gates:budget:pass,ptrs:fail)
gov:           Governor session identifier (e.g., gov-2026-001)
governor_mode: SDK dispatch mode (manual | sdk); set in STATE.md; default manual
group:         parallel execution group identifier (e.g., 1a, 1b)
issues:        comma-separated issue descriptions or - (none)
kind:          block kind (implementation | refactor | gate | discovery)
last_block:    full ID of last completed block (e.g., block-003)
last_block_status: status of last block at close (done | forced | failed)
last_done:     last completed block for this agent row in board.md
last_updated:  ISO 8601 timestamp
lock:          in-progress | ready | error
manifest:      path to manifest file
next:          next planned block ID or phase (e.g., next:095)
next_action:   specific next action (free text; e.g., next_action:plan_phase_2)
notes:         free-text annotation for human context; no machine parsing
p:             phase number (compact)
phase:         phase number (verbose)
retro:         retrospective written (yes | no)
retro_path:    path to retrospective file (e.g., blocks/block-007-slug.md)
retro_req:     retrospective required for this task packet (yes | no)
role:          agent role (implementer | governor | reviewer | doc-keeper)
scope:         sub-agent scope mode (closed | open | two-phase)
scope_exp:     scope expansion needed — path or - (none)
sid:           SDK sub-agent session identifier (e.g., s-abc123)
status:        block/agent/session status (see Status values below)
status_detail: additional detail/context for status (e.g., improvement-mode)
tip:           short git commit hash (7 chars)
tok_in:        input tokens consumed (numeric; actual or estimated)
tok_out:       output tokens consumed (numeric; actual or estimated)
tok_src:       token measurement source (actual | estimated)
tok_track:     token tracking enabled for this task (yes | no)
ts:            ISO 8601 timestamp (short form)
worktree:      git worktree path (verbose)
wt:            git worktree path (compact)
```

## Status values (reserved)

```
planned        block declared in phase doc; manifest not yet written
pending        manifest written; work not started
wip            work in progress (lock: in-progress)
wait           blocked on dependency (see blocked_by:)
done           all gates passed; ready for integration
failed         gate failed; awaiting user decision
forced         gate failed but user overrode; flag preserved
reverted       rolled back after integration
idle           agent has no active block (governor or implementer between blocks)
needs-decision sub-agent completed but Governor needs user input to proceed
scope-exceeded sub-agent discovered required files outside declared manifest scope
```

## Mode values (reserved)

```
guidance    default conversational mode (during block work)
guardrails  drift-check mode (block transitions, phase transitions)
checklist   strict yes/no mode (audit, integrate, gate validation)
```

## Conventions

- One key:value per line OR space-separated pairs on a single line.
- No prose paragraphs in AI-only files or agent communication packets.
- Timestamps: ISO 8601 (e.g., `2026-05-19T14:22Z`). Use UTC.
- Hashes: 7-character short SHA.
- File paths: relative to project root (NOT absolute).
- Lists: comma-separated, no spaces (e.g., `deps:block-031,block-032`).
- Empty value: literal `-` (e.g., `blocked_by:-`).
- Pairs: colon-separated within a field (e.g., `fmod:INDEX.md:2,STATE.md:1`).

## Example STATE.md line

```
p:8 b:094 status:done next:095 wt:.claude/worktrees/foo tip:3fbc1a3 gates:4/4 last_updated:2026-05-19T14:22Z
```

## Example board.md row

```
agent:1a b:094 group:1a status:wip lock:in-progress deps:- ts:2026-05-19T14:22Z
```

## Example task packet header (Governor → sub-agent)

```
b:007 kind:refactor phase:2 gov:g-001 ts:2026-05-20T10:00Z
axioms:Q3,Q4,Q6,C2,C6 scope:closed retro_req:yes tok_track:yes
fread:PROTOCOLS.md,INDEX.md fmod:INDEX.md
```

## Example return package (sub-agent → Governor)

```
b:007 sid:s-abc123 status:done ts:2026-05-20T10:30Z
gates:files-updated:pass,lines-budget:pass
fmod:INDEX.md:2 fread:PROTOCOLS.md,INDEX.md,_syntax.md
scope_exp:- issues:- retro:yes retro_path:blocks/block-007-slug.md
tok_in:450 tok_out:280 tok_src:actual
```

End of _syntax.md.
