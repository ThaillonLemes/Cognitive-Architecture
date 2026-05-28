# Governor v2 — SDK-based orchestration

BRIEF: Authoritative design spec for Governor v2. All Phase 4 protocol files reference this doc. Phase 5 implements it.

created_at: 2026-05-21
source: _brainstorm/governor-v2-redesign.md (13 confirmed decisions)
status: final

---

## §1 Overview

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

**Key shift:** Governor is the single owner of all shared state (STATE.md, NEXT.md, board.md, git). Sub-agents receive only what they need and return a structured package. Sub-agents never touch state files.

### Two-tier architecture (Decision 11)

| Tier | Requires SDK? | Who uses it |
|------|--------------|-------------|
| Core layer: manifests, gates, retros, axioms | No — markdown-only | Everyone |
| Automation layer: SDK Governor, task packets, auto-integration | Optional | Users with SDK access |

Feature flag in STATE.md: `governor_mode: manual | sdk`. Core layer is unchanged and always supported.

---

## §2 Core components

| Component | Owner | Description |
|-----------|-------|-------------|
| **Governor** | — | Single owner of shared state; builds task packets; spawns sub-agents; integrates; commits; writes STATE.md |
| **Sub-agent** | Governor | Stateless executor; receives task packet; implements one block; returns package; never writes STATE.md / NEXT.md / board.md / BLOCK_LOG.md |
| **Task packet** | Governor | Lean context bundle sent to sub-agent: compressed header + manifest + target files + convention snippet |
| **Return package** | Sub-agent | Structured result: compressed _syntax.md header + gate results + retro path + files modified/read |
| **governor-state.md** | Governor | Ephemeral orchestration state (Decision 8); overwritten each session; lives in `governance/`; not committed or separate from project state |
| **Convention snippet** | Governor | 10-15 line block-kind-specific axiom selection (Decision 1); derived from PROTOCOLS.md; embedded in task packet |

---

## §3 Decision record

All 13 decisions from `_brainstorm/governor-v2-redesign.md`. Status: confirmed.

| # | Decision | Chosen option | Rationale |
|---|----------|--------------|-----------|
| 1 | Convention snippet | A — Governor generates custom snippet per block kind | Minimal tokens per block; refactor ≠ implementation conventions |
| 2 | Sub-agent codebase access | B (open reads) for doc/refactor; C (two-phase) for implementation | Realistic for code; discovery pass prevents scope surprises |
| 3 | Scope expansion | A (halt+report) default; C (pre-analysis) for complex blocks | Safety first; pre-analysis for implementation blocks known upfront |
| 4 | Integration trigger | D — sync-point + fallback timer | Dep-graph correctness + resilience against stuck sub-agents |
| 5 | Block-close split | Sub-agent: validate_gates + write_retro. Governor: all state management | Sub-agent writes only evidence it generated; Governor owns shared state |
| 6 | Governor persistence | B — event-driven; Option C (loop) as future optimization | Cost-efficient; stateless between invocations |
| 7 | Worktrees | C — temp dirs; worktrees optional | Isolation without git complexity; no full-repo duplication |
| 8 | State split | STATE.md = permanent project state; governor-state.md = ephemeral session state | Clean separation; STATE.md survives Governor crashes |
| 9 | Token measurement | C — proxy (Phase 2, no SDK); actual via SDK (Phase 5) | Both modes write to same `tok_in`/`tok_out` fields |
| 10 | Phase strategy | No inter-phase parallelism; merge non-conflicting themes into one larger phase | Same parallelism, zero new machinery |
| 11 | Backward compat | B — two-tier; SDK optional | Core stays markdown-only; portability preserved |
| 12 | Return package schema | Compressed _syntax.md format (not verbose YAML) | Consistent with all other agent communication |
| 13 | All agent communication | Compressed _syntax.md vocab for all Governor↔sub-agent messages | Token efficiency; single vocabulary for AI-only files |

---

## §4 Task packet format

Governor builds one per block. See `protocols/task-packet.md` for generation rules.

### Header (compressed _syntax.md)
```
b:NNN kind:implementation|refactor|gate|discovery phase:N gov:g-ID ts:ISO8601
axioms:Q1,Q3,Q4,Q6,C2,C5  scope:open|closed|two-phase  retro_req:yes  tok_track:yes
fread:path1,path2  fmod:path3
```

### Body (appended after header)
1. **Convention snippet** — axiom selection per block kind (10-15 lines from PROTOCOLS.md)
2. **Manifest** — full content of `manifests/block-NNN-slug.md`
3. **Target files** — verbatim content of `files.read` entries

### Scope modes (by block kind)
| `kind` | `scope` | Execution model |
|--------|---------|----------------|
| `doc` / `refactor` | `open` | Sub-agent reads freely; writes only declared `fmod` |
| `implementation` (simple) | `open` | Same; reports `fread` in return package |
| `implementation` (complex) | `two-phase` | Discovery pass → Governor approves scope → execution pass |
| `gate` | `closed` | Sub-agent reads only declared `fread`; no free reads |

---

## §5 Return package format

Sub-agent emits one per block. See `templates/sub-agent-return.md` for schema.

```
b:NNN sid:s-ID status:done ts:ISO8601
gates:gate-name:pass|fail,gate-name2:pass|fail
fmod:path1.md:N,path2.md:N
fread:path1.md,path2.md,path3.md
scope_exp:- issues:-
retro:yes retro_path:blocks/block-NNN-slug.md
tok_in:N tok_out:N tok_src:actual|estimated
```

If a gate fails, sub-agent appends a freetext `evidence:` line.
If scope expansion needed: `scope_exp:path/to/file.md` (halt+report per Decision 3).

---

## §6 Governor orchestration lifecycle

Event-driven (Decision 6). Governor is invoked on: (a) user starts phase, (b) sub-agent returns, (c) fallback timer fires.

```
1. Read STATE.md + NEXT.md + board.md → identify next block(s) in parallel group
2. For each block to dispatch:
   a. Build convention snippet (protocols/convention-snippet-generation.md)
   b. Assemble task packet (protocols/task-packet.md)
   c. Spawn sub-agent via SDK (protocols/governor-dispatch.md)
   d. Update board.md: status:wip lock:in-progress
3. Await return packages (per sync point — dep-graph driven)
4. On return: validate schema; check gates; check scope_exp
   - gate failed → escalate (protocols/governor-failure-handling.md)
   - scope_exp → expand or create new block
   - all pass → proceed to integration
5. At sync point (all group done OR fallback timer): integrate
   a. Merge modified files to main (protocols/governor-integration.md)
   b. Write STATE.md, NEXT.md, append BLOCK_LOG.md, update board.md
   c. Commit
6. Dispatch next group or emit phase-close signal
```

---

## §7 Sub-agent execution lifecycle

```
1. Receive task packet
2. Read header: b, kind, scope, axioms, fread, fmod
3. Read convention snippet → apply axiom constraints throughout
4. Read manifest (full content)
5. Read fread files (context)
6. [two-phase only] Emit discovery report; await Governor scope approval
7. Execute block work (implement / refactor / validate)
8. Run gates declared in manifest
9. Write retrospective to blocks/block-NNN-slug.md
10. Emit return package (templates/sub-agent-return.md)
```

Sub-agent NEVER touches: STATE.md, NEXT.md, board.md, BLOCK_LOG.md, other blocks' files.

---

## §8 Failure handling overview

See `protocols/governor-failure-handling.md` for full escalation tree.

| Failure | Who detects | Response |
|---------|------------|---------|
| Gate fails | Sub-agent | Report in return package; Governor escalates |
| Scope expansion needed | Sub-agent | `scope_exp:path` in return; Governor creates new block or expands manifest |
| Sub-agent times out | Governor (fallback timer) | Mark `failed` in board.md; re-dispatch or ask user |
| Return package invalid schema | Governor | Log error; mark `needs-decision`; surface to user |
| Integration conflict | Governor | Resolve if possible; else `needs-decision` to user |

Escalation order: Governor auto-resolve → surface to user → block marked `forced` (user override).

---

## §9 Manual fallback (governor_mode: manual)

When SDK is unavailable, all protocols remain usable manually:

| Protocol | Manual equivalent |
|----------|------------------|
| `protocols/task-packet.md` | User copies task packet template, fills manually, pastes to Claude |
| `protocols/sub-agent-contract.md` | Same contract; Claude session is the sub-agent |
| `protocols/governor-dispatch.md` | User opens N Claude sessions manually |
| `protocols/governor-integration.md` | User runs `commands/integrate.md` manually |
| `protocols/governor-failure-handling.md` | User makes the decisions Governor would make |

Manual mode is the existing v1.x workflow. Governor v2 adds automation; it does not break the base.

---

## §10 Protocol and template map

All files created in Phase 4 (group 4B blocks 018-025):

| File | Block | Purpose |
|------|-------|---------|
| `protocols/task-packet.md` | block-018 | How Governor builds the task packet |
| `protocols/sub-agent-contract.md` | block-019 | Sub-agent responsibilities; return schema |
| `protocols/convention-snippet-generation.md` | block-020 | Axiom selection per block kind |
| `protocols/governor-dispatch.md` | block-021 | SDK spawn mechanism |
| `protocols/governor-integration.md` | block-022 | Sync-point integration logic |
| `protocols/governor-failure-handling.md` | block-023 | Failure escalation tree |
| `templates/task-packet.md` | block-024 | Task packet format template |
| `templates/sub-agent-return.md` | block-025 | Return package schema template |

Updated in Phase 4 (group 4C blocks 026-028):

| File | Block | Change |
|------|-------|--------|
| `protocols/block-close-checklist.md` | block-026 | Annotate each step: sub-agent vs. Governor ownership |
| `protocols/agents.md` | block-027 | Rewrite for task-packet model; deprecate AGENT.md per sub-agent |
| `protocols/parallelism.md` | block-028 | Add phase design rules (Decision 10) |

---

## §11 Open questions — resolved in Phase 5

All 7 questions resolved during implementation (block-033 through block-037).

1. **SDK file passing:**
   resolved: Anthropic SDK passes task packet as plain text (user message). Sub-agents read `fread:` files directly from the filesystem using their own file-read tools. Temp-dir isolation (Decision 7) is feasible — sub-agent runs in the same filesystem; conceptual separation via `fmod:` declaration is sufficient. No special file-passing API needed. (sdk/dispatch.py)

2. **Token measurement in manual mode:**
   resolved: Manual mode sub-agents use chars÷4 proxy estimate and report `tok_src:estimated`. SDK mode receives exact counts from `message.usage.input_tokens` / `output_tokens` and reports `tok_src:actual`. Both write to the same `tok_in`/`tok_out` fields in the return package. The proxy is adequate for budget tracking; exact measurement is a bonus in SDK mode. (sdk/dispatch.py, sdk/return_validator.py)

3. **Governor crash recovery:**
   resolved: `_write_governor_state()` writes `governance/governor-state.md` before each state transition (before dispatch, before integration). If Governor crashes, restart reads governor-state.md to identify last known group and resume. Full transaction log (write-then-rename for governor-state.md itself) deferred to v2.1 — current implementation provides single-transition rollback. (sdk/governor.py)

4. **Sub-agent identity:**
   resolved: Sub-agents are ephemeral. Governor assigns `sid:s-<ID>` before dispatch; sub-agents include it in return package. No persistent named sub-agent needed. board.md rows track dispatch/return per block, not per sub-agent session. (sdk/dispatch.py, MockAnthropicClient)

5. **Max parallelism:**
   resolved: `max_parallel_agents = 3` default. Configurable via `GOV_MAX_PARALLEL` env var. `GovConfig.max_parallel_agents` enforced in dispatch loop — Governor will not dispatch more concurrent blocks than this limit. (sdk/config.py)

6. **User interruption signal:**
   resolved: Governor polls for `governance/.pause` file before each group dispatch. If file exists, Governor prints "PAUSED — delete governance/.pause to resume." and halts. User creates the file to request pause; deletes it to resume. No daemon process or signal handler needed. (sdk/config.py, GovConfig.check_pause())

7. **Mixed codebase:**
   resolved: No path collision risk. Governor reads `cognitive-arch/` (ARCH_ROOT = sdk/../ = cognitive-arch/). Sub-agent reads project code (paths relative to project root, outside cognitive-arch/). All paths in task packets and return packages are relative; ARCH_ROOT is the single reference point. `fmod:` declarations provide the explicit separation boundary. (sdk/integration.py, check_fmod_disjoint())

End of governor-v2.md.
