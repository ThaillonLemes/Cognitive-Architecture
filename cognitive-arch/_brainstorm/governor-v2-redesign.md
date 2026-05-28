# Brainstorm: Governor v2 — SDK-based orchestration redesign

status: draft
created_at: 2026-05-20
author: AI + user (session brainstorm)
synthesis_target: design/governor-v2.md

---

## Context

Phase 1 (v1.1) is complete. Before planning phases 2–5, we are redesigning the execution model to:
1. Introduce Claude Code SDK-based Governor automation
2. Eliminate worktree redundancy (full cognitive-arch copies per agent)
3. Create lean sub-agent task packets (only what the agent needs)
4. Define a clean return package contract (what sub-agent delivers back)
5. Enable cross-phase parallelism (not just intra-phase)

This document captures all design decisions, options, and recommendations before any implementation begins.

---

## Core architectural shift

### Current model (v1.x)
```
Human opens session → reads HOT files → works → closes block manually
Multi-agent: human opens N sessions → N worktrees (full copies) → human integrates
```

### Target model (v2.0)
```
Human triggers Governor → Governor reads project state → spawns sub-agents with task packets
→ sub-agents execute → return packages → Governor integrates → Governor updates state → next
```

Key properties of target model:
- Governor is the **single owner of all shared state** (STATE.md, NEXT.md, board.md, git)
- Sub-agents receive **only what they need** (task packet = manifest + target files + convention snippet)
- Sub-agents **return a structured package** (modified files + retrospective + gate results)
- Sub-agents **never touch state files** (STATE.md, NEXT.md, board.md, BLOCK_LOG.md)
- Worktrees become **optional** (used only if git branch isolation is desired, not for agent isolation)

---

## Decision 1 — Convention snippet: how does sub-agent know the rules?

**Problem:** Sub-agent needs to know conventions (axioms, file format rules, block-close behavior) to act correctly. Currently this is in PROTOCOLS.md (107 lines). Sending full PROTOCOLS.md to every sub-agent is expensive and most of it is irrelevant per block.

### Options

**Option A — Governor generates custom snippet per block** *(recommended)*
- Governor reads PROTOCOLS.md, selects axioms relevant to block's `kind` field
  - `kind: refactor` → C2, C3, C6, Q4, Q6
  - `kind: implementation` → Q1, Q3, Q4, Q5, Q6, C1, C5
  - `kind: gate` → Q4 only
- Generates 10–15 line snippet embedded in task packet
- Snippet is always derived from PROTOCOLS.md (source of truth)
- New protocol needed: `protocols/convention-snippet-generation.md`

**Option B — Fixed mini-PROTOCOLS.md (top rules only)**
- Create `protocols/sub-agent-axioms.md` — 20-line distillation of the 5 most critical axioms
- Every sub-agent gets this same file
- Simpler; no generation logic
- Risk: becomes stale if PROTOCOLS.md changes

**Option C — Sub-agent reads PROTOCOLS.md via Governor reference**
- Task packet contains pointer: "conventions: PROTOCOLS.md"
- Sub-agent fetches it on demand
- No preprocessing; always current
- Cost: sub-agent reads 107 lines even for a 2-line fix

**Option D — No conventions in task packet**
- Sub-agent operates purely from manifest (its contract)
- Manifest is self-describing enough for most blocks
- Risk: sub-agent may violate C2 (no speculation), C6 (facts-only retro), etc. without knowing

**Recommendation: Option A.** The snippet generation is one extra protocol but pays for itself on every block. A refactor block that only needs "don't speculate, write facts" doesn't need Q1 (Rule of Three) at all. Custom snippets = minimal tokens per block.

---

## Decision 2 — Sub-agent codebase access: how much can it read?

**Problem:** For software implementation blocks (not doc blocks), sub-agent may need to read files beyond the task packet to understand context (e.g., "fix the auth bug" requires reading auth.ts, user.model.ts, middleware.ts before knowing what to change).

### Options

**Option A — Closed reads (only task packet)**
- Sub-agent can only read files explicitly included in task packet
- If it needs more → reports back to Governor → Governor decides
- Pros: Governor has full visibility; predictable token cost
- Cons: Governor must anticipate all context files; rigid; breaks on discovery

**Option B — Open reads (full codebase read-only)** *(recommended for implementation blocks)*
- Sub-agent can read any file in the project (read-only)
- Can only write files in `manifest.files.modify`
- Sub-agent reports `files_read: [list]` in return package
- Governor uses this to improve future task packets for the same block type
- Pros: realistic for code blocks; sub-agent can resolve its own context questions
- Cons: token cost unknown upfront; sub-agent may "get lost" in large codebases

**Option C — Two-phase execution: discover then execute** *(recommended for complex implementation)*
- Phase 1 (discovery): sub-agent reads freely, reports what it plans to modify
- Governor reviews scope, approves or adjusts manifest
- Phase 2 (execution): sub-agent executes with approved scope
- Pros: prevents surprises; Governor retains control; scope expansion is explicit
- Cons: two SDK calls per block (more overhead)

**Option D — Declared reads + open fallback**
- Task packet includes `files.read` (declared context files)
- If sub-agent needs more, it can read but marks them as "undeclared reads" in return
- Governor audits undeclared reads to improve future manifests

**Recommendation: Option B for doc/refactor blocks; Option C for implementation blocks.** The distinction is the block's `kind` field. Governor selects the execution mode based on kind.

---

## Decision 3 — Scope expansion: sub-agent discovers it needs unauthorized files

**Problem:** Sub-agent is modifying `login.ts` and discovers `auth.middleware.ts` also needs to change. This file is not in `manifest.files.modify`. What should it do?

### Options

**Option A — Halt and report (safest)**
- Sub-agent stops, returns `scope_expansion_needed: [auth.middleware.ts]`
- Governor decides: expand scope and re-dispatch, or create a new block for the remainder
- Pros: no unauthorized modifications; Governor stays informed
- Cons: block may need multiple dispatch cycles

**Option B — Autonomous expansion with audit trail**
- Sub-agent modifies the undeclared file, records it in return package
- Governor validates that the unauthorized modification was actually necessary
- Pros: faster execution; less round-tripping
- Cons: Governor learns about scope after the fact; harder to coordinate with parallel agents

**Option C — Pre-analysis phase (two-pass)** *(recommended)*
- For implementation blocks: mandatory pre-analysis pass before execution
- Discovery pass: sub-agent reads freely, reports `files_to_modify: [list]`
- Governor validates no conflicts with parallel blocks
- Execution pass: sub-agent executes with the fully approved file list
- Pros: clean separation; Governor approves scope upfront; parallel-safe
- Cons: two SDK calls

**Option D — Best-effort completion**
- Sub-agent completes what it can, notes the gap in retrospective
- Next block handles the remainder
- Pros: simple; sub-agent always finishes
- Cons: leaves half-fixed code; retrospective needs to clearly flag this

**Recommendation: Option A for automated pipeline (simplest to implement safely); Option C for complex codebases. Use `kind` field + a new manifest field `scope: open | closed` to select mode.**

---

## Decision 4 — Integration trigger: when does Governor integrate?

**Problem:** With parallel agents, when does Governor merge their work back to main?

### Options

**Option A — Per block (integrate immediately when each block finishes)**
- As soon as block-N returns, Governor integrates before starting block-N+1
- Pros: simple; no branch divergence
- Cons: blocks must be sequential; defeats purpose of parallelism

**Option B — Per sync point (dep-graph driven)** *(recommended)*
- Governor tracks the dependency graph
- Integration happens when all blocks in a "parallel group" complete
- Parallel group = set of blocks with no mutual dependencies
- Pros: maximizes parallelism; integrations are logically correct
- Cons: Governor must implement dep-graph traversal

**Option C — Per phase boundary**
- Integration only at phase close
- All parallel blocks in a phase merge at once
- Pros: simple trigger
- Cons: long-lived branches; big merges; delays unblocking dependent phases

**Option D — Hybrid: per sync point + fallback timer**
- Primary: sync-point triggered
- Fallback: if a sync point is stale for >T minutes (configurable), integrate what's done and log the stragglers
- Pros: resilient to stuck sub-agents; doesn't hold everything up for one slow block
- Cons: slightly more complex logic

**Recommendation: Option D.** Sync points are the right semantic model; the timer fallback is a safety net. The timer should be configurable per phase (tight deadline phases = short fallback timer).

---

## Decision 5 — Block-close responsibility split: sub-agent vs. Governor

**Problem:** Current block-close has 8 steps all done by the agent. In the new model this must be split.

### Current 8 steps:
1. validate_gates
2. write_state
3. write_next
4. append_block_log
5. write_retrospective
6. update_board
7. commit
8. emit_next_instruction

### Proposed split

**Sub-agent does:**
- Step 1: validate_gates (it ran the block; it knows results)
- Step 5: write_retrospective (it built the block; it writes the retro)
- Returns both as part of return package

**Governor does:**
- Step 2: write_state (Governor owns STATE.md)
- Step 3: write_next (Governor owns NEXT.md)
- Step 4: append_block_log (Governor owns BLOCK_LOG.md)
- Step 6: update_board (Governor owns board.md)
- Step 7: commit (Governor owns git)
- Step 8: emit_next_instruction (Governor dispatches next block)

**Recommendation:** This split. Sub-agent does only the evidence it generated; Governor does all state management and coordination. Sub-agent never touches shared state files.

**New protocols needed:**
- `protocols/sub-agent-contract.md` — describes sub-agent's 2 responsibilities
- `protocols/governor-integration.md` — describes Governor's 6 responsibilities

---

## Decision 6 — Governor persistence: continuous process vs. event-driven

**Problem:** Should Governor run continuously (polling for new work) or be invoked only when needed?

### Options

**Option A — Continuous polling loop**
- Governor runs as a persistent process
- Checks board.md / return queue every N seconds
- Pros: responsive; no startup latency
- Cons: expensive (costs tokens even when idle); complex to implement; already designed in `_future/governor-loop.md` and noted as $24-50/month idle cost

**Option B — Event-driven (invoke on trigger)** *(recommended)*
- Governor is invoked when: (a) user starts a phase, (b) a sub-agent returns, (c) a timer fires
- Between invocations, Governor is not running
- Pros: cost-efficient; stateless between invocations; easier to debug
- Cons: latency between sub-agent completion and Governor integration

**Option C — Hybrid: fast loop during active phase, sleep when idle**
- Governor polls fast (10s intervals) when a phase has active blocks
- Governor sleeps (no polling) when all blocks are done or waiting on user
- Uses ScheduleWakeup for the sleep periods

**Recommendation: Option B (event-driven) for the initial implementation; Option C as an optimization once the basic model works. The `_future/governor-loop.md` design (ScheduleWakeup-based) maps to Option C.**

---

## Decision 7 — Worktrees: keep, eliminate, or make optional?

**Problem:** Worktrees provide git branch isolation today. In the new model, agent isolation is provided by task packets. Are worktrees still needed?

### Options

**Option A — Eliminate worktrees**
- Sub-agents work directly on the main filesystem
- File conflict prevention via manifest scope control (no two agents get overlapping files.modify)
- Governor commits atomically after integration
- Pros: simpler; no git complexity; no filesystem duplication
- Cons: no branch history for individual blocks; if sub-agent fails mid-write, files may be partially modified

**Option B — Keep worktrees as optional**
- Default: no worktrees (sub-agents work on main)
- Power user option: enable worktrees for git history per block
- Manifest gains a flag: `isolation: worktree | none`
- Pros: backward compatible; flexible
- Cons: extra complexity; two modes to maintain

**Option C — Replace worktrees with temp directories** *(recommended)*
- Sub-agent receives copies of its target files in a temp dir
- Sub-agent writes to temp dir
- Governor reviews diff, merges into main, commits
- Pros: clean isolation without git complexity; rollback is trivial (just discard temp dir); no filesystem duplication of full cognitive-arch
- Cons: Governor must implement file diff/merge logic

**Recommendation: Option C.** Temp dirs give the same isolation as worktrees without the git overhead and without full-repo duplication. This directly solves the user's redundancy concern.

---

## Decision 8 — State split: project state vs. orchestration state

**Problem:** STATE.md today mixes permanent project state (what phase we're in, what's done) with ephemeral session state (what block is running right now). In the new model these should be separate.

### Proposed split

**STATE.md (permanent — survives between sessions):**
```
p:2 phase:2 status:active status_detail:sdk-governor
blocks_done:block-001,...,block-006
last_block:block-006 last_block_status:done
created_at:2026-05-20 last_updated:2026-05-20
```

**governance/governor-state.md (ephemeral — recreated each Governor session):**
```
session_id: gov-2026-05-20-001
started_at: 2026-05-20T10:00Z
active_blocks: block-007,block-008
pending_integration: block-007
sub_agent_sessions: [sdk-session-abc, sdk-session-def]
integration_queue: []
status: running
```

Governor state is NOT committed to git (or committed as a separate "governance" file that gets overwritten each session).

**Recommendation:** This split. STATE.md stays clean and project-scoped. Governor state is operational and ephemeral.

---

## Decision 9 — Token measurement: how to implement

**Problem:** User wants a `/token-audit` command and token tracking per block/session.

### Options

**Option A — Line/char proxy (no SDK needed)**
- Token estimate = file_size_chars / 4 (roughly 1 token per 4 chars)
- Works offline, zero dependencies
- ±30% accuracy
- Implement: bash script or simple calculation in Governor

**Option B — Claude API metadata (requires SDK)**
- Claude API returns `input_tokens` and `output_tokens` in every response
- Governor captures these for each sub-agent session
- Exact measurement; no estimation
- Requires SDK (unavailable in plain markdown sessions)

**Option C — Both: proxy for offline, real for SDK sessions** *(recommended)*
- When running without SDK: proxy (Option A)
- When running with SDK: real measurement (Option B)
- `_syntax.md` gains two new keys: `tokens_estimated:` and `tokens_actual:`
- Retrospective template gains `tokens:` section

**Option D — External token counter tool**
- Use tiktoken (Python) or equivalent to count tokens exactly without making API calls
- Accurate without needing a live SDK session
- Requires Python dependency
- Works offline

**Recommendation: Option C.** The proxy is available immediately (Phase 2); the real measurement comes naturally with Phase 5 (SDK Governor). Design the schema now so both modes write to the same fields.

---

## Decision 10 — Phase design strategy: maximize intra-phase parallelism (REVISED)

**Original problem:** How to parallelize across phases.

**Revised decision (user confirmed):** Do NOT implement inter-phase parallelism machinery. It adds complexity for a case that can be solved by better phase design.

### Strategy: merge non-conflicting themes into one phase

Instead of running phase A and phase B in parallel:
- Analyze block-level file conflicts between the two themes
- If no conflicts → merge all their blocks into a single larger phase
- Governor parallelizes all non-dependent blocks within that phase (existing mechanism)
- Result: same parallelism, zero new machinery

```
Before (cross-phase parallelism): Phase A ║ Phase B → complex Governor logic
After (phase merge):              Phase A+B with parallel block groups → existing mechanism
```

### Phase design rules (new guidance for phase generation)

1. **Maximize intra-phase parallelism:** when designing a phase, group blocks so the maximum number can run in parallel (no file conflicts, no logical deps between them).
2. **Thematic coherence vs. parallelism trade-off:** phases can be larger than "one theme" if combining themes increases parallelism without creating file conflicts.
3. **Sequential blocks go to next phase:** if block X must wait for block Y AND block Y belongs to a different theme, put X in the next phase. Don't force sequential work into a "parallel" phase.
4. **File-conflict check is per-block, not per-phase:** Governor checks `files.modify` overlap between blocks within a phase before spawning them in parallel. This check already exists.

### When themes are truly independent (e.g., MMORPG: combat vs. controls)

If two themes have zero file overlap: merge into one phase with two parallel groups.
```
Phase 3: foundation
  group:A — combat blocks (block-031, block-032, block-033) → parallel
  group:B — controls blocks (block-034, block-035) → parallel
  sync point after A+B complete → Governor integrates
```

**Recommendation:** Remove `protocols/phase-parallelism.md` from the new-files list. Deferred to v3.0+ if ever needed. Update `protocols/phase-generation.md` with the new phase design rules instead.

---

## Decision 11 — Backward compatibility: one architecture or two?

**Problem:** All these changes require Claude Code SDK. But the architecture today works without SDK. Should we maintain a "manual mode"?

### Options

**Option A — Single architecture (SDK required for v2.0+)**
- Clean break: v2.0 requires SDK
- Simpler to design and maintain
- Users without SDK stay on v1.x

**Option B — Two-tier architecture (SDK optional)** *(recommended)*
- Core layer: manifests, gates, retrospectives, axioms — unchanged, work without SDK
- Automation layer: SDK Governor, task packets, automated integration — optional
- v1.x continues to work; v2.0 adds the automation layer on top
- Feature flag in STATE.md: `governor_mode: manual | sdk`

**Option C — Progressive enhancement**
- Same as B, but each individual feature is independently opt-in
- `governor_mode: manual` = today
- `governor_mode: dispatch-only` = Governor spawns agents but integration is manual
- `governor_mode: full-auto` = Governor handles everything

**Recommendation: Option B.** The core architecture must remain markdown-only and SDK-free. The SDK is an enhancement, not a requirement. This preserves portability (works with any LLM, no vendor lock-in on the core) while enabling full automation for users who want it.

---

## Decision 13 — All agent communication uses compressed _syntax.md vocabulary (NEW)

**Decision (user confirmed):** Every message between Governor and sub-agent uses the compressed key:value syntax from `_syntax.md`. No verbose YAML, no English prose in packet headers. The source files (manifests, code) remain as-is; only the communication envelopes are compressed.

### Scope of compression

| Communication | Format |
|--------------|--------|
| Task packet header | `_syntax.md` key:value |
| Return package | `_syntax.md` key:value |
| Convention snippet header | `_syntax.md` key:value |
| Governor state file | `_syntax.md` key:value |
| STATE.md, NEXT.md, board.md | `_syntax.md` key:value (unchanged) |
| Manifest content | Markdown (unchanged — human-readable contract) |
| Retrospective content | Markdown (unchanged — facts record) |
| File contents passed in task packet | Verbatim (unchanged) |

### New keys added to _syntax.md for agent communication

Task packet keys (Governor → sub-agent):
- `axioms:` — comma-separated axiom IDs (e.g., Q3,Q4,C2)
- `gov:` — Governor session ID
- `kind:` — block kind (implementation|refactor|gate|discovery)
- `retro_req:` — retrospective required (yes|no)
- `scope:` — sub-agent scope mode (closed|open|two-phase)
- `sid:` — SDK session ID for sub-agent
- `tok_track:` — token tracking enabled (yes|no)

Return package keys (sub-agent → Governor):
- `fmod:` — files modified (path:lines pairs)
- `fread:` — files read (comma-separated)
- `issues:` — issues encountered or -
- `retro:` — retrospective written (yes|no)
- `retro_path:` — path to retrospective
- `scope_exp:` — scope expansion needed (path or -)
- `tok_in:` — input tokens
- `tok_out:` — output tokens
- `tok_src:` — measurement source (actual|estimated)

New status values:
- `needs-decision` — sub-agent completed but Governor needs user input
- `scope-exceeded` — sub-agent found required files outside manifest scope

**All new keys documented in `_syntax.md` canonical list.** Done in this session.

---

## Decision 12 — Sub-agent return package: schema

**Problem:** No formal schema exists for what sub-agent returns to Governor.

### Schema (compressed _syntax.md format — see Decision 13)

```
b:NNN sid:s-XYZ status:done ts:2026-05-20T10:30Z
gates:gate-name:pass|fail,gate-name2:pass|fail
fmod:path1.md:N,path2.md:N
fread:path1.md,path2.md,path3.md
scope_exp:- issues:-
retro:yes retro_path:blocks/block-NNN-slug.md
tok_in:N tok_out:N tok_src:actual|estimated
```

**Evidence for gates** (when needed): if a gate fails, sub-agent appends a freetext `evidence:` line after the return package header.

**Recommendation:** Formalize in `templates/sub-agent-return.md` and `protocols/sub-agent-contract.md`. Governor validates this schema on every return before integrating. Format is _syntax.md-compliant — no verbose YAML.

---

## File inventory: what changes

### Files that are ELIMINATED (or deprecated)
| File | Why |
|------|-----|
| `_future/governor-loop.md` | Superseded by this design (governor-v2.md) |
| `templates/AGENT.md` | Sub-agents don't have AGENT.md; replaced by task-packet template |

### Files that CHANGE SIGNIFICANTLY
| File | Change |
|------|--------|
| `STATE.md` | Split: project state only (not session state) |
| `board.md` | Governor-write-only; sub-agents never touch it |
| `protocols/parallelism.md` | Expanded for cross-phase parallelism; SDK-aware |
| `protocols/agents.md` | Rewritten for task-packet model |
| `commands/integrate.md` | Becomes Governor-internal; not human-invoked |
| `commands/block-close.md` | Split: sub-agent part (2 steps) vs Governor part (6 steps) |
| `protocols/block-close-checklist.md` | Annotated with sub-agent vs Governor ownership per step |
| `templates/agent-roles/` | Reduced to implementer (sub-agent) + Governor; others deprecated |
| `agents/` folder | Replaced by governor-state.md tracking sessions |

### Files that STAY UNCHANGED
| File | Why unchanged |
|------|--------------|
| `PROTOCOLS.md` | Axioms are the foundation regardless of execution model |
| `templates/manifest-*.md` | Manifests remain the block contract |
| `templates/block-retrospective.md` | Retrospectives still matter |
| `templates/ADR.md` | ADRs still matter |
| `commands/audit.md` | Governor invokes this; format unchanged |
| `phases/`, `blocks/`, `decisions/`, `governance/` | All survive |
| `_syntax.md` | Extended (new keys) but not redesigned |
| `CLAUDE.md`, `INDEX.md` | Slightly updated; structure unchanged |

### NEW files needed
| File | Purpose |
|------|---------|
| `design/governor-v2.md` | Finalized design doc (synthesized from this brainstorm) |
| `protocols/task-packet.md` | Spec: what goes in a task packet, how Governor builds it |
| `protocols/sub-agent-contract.md` | What sub-agent receives, can do, must return (with compressed return schema) |
| `protocols/convention-snippet-generation.md` | How Governor selects axioms per block kind → compressed `axioms:` field |
| `protocols/governor-dispatch.md` | How Governor spawns sub-agents via SDK |
| `protocols/governor-integration.md` | Sync-point logic; when/how Governor integrates |
| `protocols/governor-failure-handling.md` | Failure escalation tree |
| `templates/task-packet.md` | Template for task packet sent to sub-agent (compressed header format) |
| `templates/sub-agent-return.md` | Schema for return package (compressed _syntax.md format) |
| `governance/governor-state.md` | Ephemeral orchestration state (compressed key:value; overwritten each session) |

**Removed from list:** `protocols/phase-parallelism.md` — deferred to v3.0+ (see Decision 10 revised).

---

## Open questions (not decided here)

1. **Claude Code SDK specifics:** Does the SDK allow Governor to pass specific files as context, or only text? Does sub-agent have filesystem access directly, or only via tool calls passed through SDK? This determines whether temp-dir isolation (Decision 7, Option C) is feasible.

2. **Token measurement in manual mode:** In a non-SDK session, how does the AI report tokens consumed? The API metadata is available in Claude's system context sometimes but not always. Need to test.

3. **Governor state persistence across crashes:** If Governor crashes mid-integration, how does it recover? Option: Governor commits governor-state.md to git before each state transition, so it can resume.

4. **Sub-agent identity:** In the SDK model, does each sub-agent have a named identity (for board.md tracking), or are they ephemeral? Recommendation: ephemeral (Governor assigns a session_id, tracks internally).

5. **Max parallelism:** How many sub-agents can Governor run simultaneously? SDK likely has limits. Need to define `max_parallel_agents:` configuration (default: 3).

6. **User interruption:** If user wants to pause or override during automated Governor run, what's the mechanism? Need a "pause signal" that Governor checks periodically.

7. **Mixed codebase: cognitive-arch + project code:** In the new model, the Governor reads cognitive-arch/ and the sub-agent reads the project codebase. Are these the same filesystem? (Yes, in the same repo.) The separation is conceptual, not physical. This is fine.

---

## Confirmed decisions (user-approved)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Convention snippet | A — Governor generates custom snippet per block kind |
| 2 | Codebase access | B (doc/refactor) + C (implementation) |
| 3 | Scope expansion | A (halt+report) default; C (pre-analysis) for complex |
| 4 | Integration trigger | D — sync-point + fallback timer |
| 5 | Block-close split | Sub-agent: validate_gates + write_retro; Governor: all state |
| 6 | Governor persistence | B — event-driven; Option C as future optimization |
| 7 | Worktrees | C — temp dirs for isolation; worktrees optional |
| 8 | State split | Confirmed — STATE.md permanent; governor-state.md ephemeral |
| 9 | Token measurement | C — proxy now (Phase 2); actual via SDK (Phase 5) |
| 10 | Phase strategy | REVISED — no inter-phase parallelism; merge themes into bigger phases |
| 11 | Backward compat | B — two-tier; SDK is optional automation layer |
| 12 | Return package | Compressed _syntax.md format (not verbose YAML) |
| 13 | All comms compressed | YES — all Governor↔sub-agent communication uses _syntax.md vocab |

## Recommended synthesis

Before generating phases 2–5, create `design/governor-v2.md` from this brainstorm.

Phase sequence recommendation (post-brainstorm, user-confirmed direction):
- **Phase 2 (v1.2):** Token metering (proxy-based; no SDK needed) + `_syntax.md` token keys + `/token-audit` command
- **Phase 3 (v1.3):** Formal schema validation + pointer integrity phases 2–5 + manifest schema validator
- **Phase 4 (v1.4):** Governor v2 design finalization → write `design/governor-v2.md` + all new protocol stubs (task-packet, sub-agent-contract, governor-dispatch, governor-integration, governor-failure-handling, convention-snippet-generation)
- **Phase 5 (v2.0):** SDK Governor implementation + task packets + sub-agent contract + automated integration + real token measurement via SDK

**Removed:** cross-phase parallelism phase → deferred to v3.0+ or eliminated (Decision 10 revised).

End of brainstorm.
