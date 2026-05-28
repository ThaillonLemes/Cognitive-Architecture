# Protocol: Governor failure handling

BRIEF: How the Governor responds to failures during phase orchestration. Covers all failure modes with concrete recovery procedures. Governor auto-resolves where possible; escalates to implementer when it cannot.

Design authority: `design/governor-v2.md §8` (failure handling) + `§3` (Decision 6)

---

## Failure modes and recovery

### Mode 1 — Block blocked (`status:blocked`)

Sub-agent returns: `status:blocked issues:<description>`

**Governor decision tree (in order):**
```
1. Is blocked block a dependency for a subsequent group?
   YES → halt phase; escalate to implementer
   NO  → continue below

2. Retry once:
   - Re-dispatch with same task packet + notes:<issue summary>
   - If retry returns status:done → continue normally
   - If retry still blocked → move to step 3

3. Skip:
   - Mark block status:skipped in governor-state.md
   - Append to BLOCK_LOG.md: block-NNN forced - <ts>  (user did not approve — Governor skip)
   - NOTE: manual-mode skip still requires user approval (Axiom Q4)
   - Continue to next block in group

4. Halt phase (fallback):
   - If 2+ consecutive blocks in a group are blocked → halt; escalate
```

---

### Mode 2 — Scope exceeded (`status:scope-exceeded`)

Sub-agent returns: `status:scope-exceeded scope_exp:<path>`

```
1. Mark block done in governor-state.md (scope discovery ≠ failure)
2. Log discovery: append to governance/governor-state.md:
     scope_discoveries: block-NNN:<discovered-path>
3. Create new block stub for discovered work:
   - Add planned entry in next-group or next-phase backlog
   - Do NOT expand manifest mid-phase
4. Continue phase normally
```

Scope expansion is never resolved mid-phase. The discovered work becomes a new block.

---

### Mode 3 — Sub-agent timeout or crash

Sub-agent returns nothing within the fallback timer window.

```
1. Log in governor-state.md: blocks_timed_out: block-NNN
2. Retry once with identical task packet
3. If second attempt also times out:
   a. Treat as status:blocked (→ Mode 1 recovery)
   b. Log both attempts in governor-state.md
```

SDK timeout is set via `deadline_ts:` in task packet header. Default: derived from phase `estimated_duration_days`. See `protocols/governor-dispatch.md` §Fallback timer.

---

### Mode 4 — Gate failure (`gates:gate-name:fail` in return)

Sub-agent returns `status:partial` or `status:done` with one or more `gates:name:fail`.

```
1. Classify the failing gate:
   a. Transient (test flake, timeout) → retry once
   b. Structural (logic error, missing file) → halt and escalate

2. Transient retry:
   - Re-dispatch with notes: mentioning the gate and the failure output
   - If second attempt passes all gates → continue normally
   - If second attempt still fails → classify as structural

3. Structural failure:
   - Mark block status:failed in governor-state.md
   - Halt and escalate to implementer
   - Implementer decides: (a) revise manifest, (b) force-pass with rationale

4. Force-pass:
   - Requires implementer explicit approval
   - Governor records in BLOCK_LOG.md: block-NNN forced <ts>
   - governor-state.md: forced_blocks: block-NNN:<gate-name>
```

---

### Mode 5 — Return package schema invalid

Governor cannot parse the return package (missing required fields, format error).

```
1. Log raw return in governor-state.md
2. Mark block as needs-decision
3. Escalate to implementer immediately
4. Do NOT retry automatically (schema errors indicate a deeper problem)
```

---

## Governor crash recovery

If Governor process terminates mid-phase (crash, timeout, user kill):

```
1. On next invocation, read governance/governor-state.md
2. Check status field:
   - complete → phase already done; nothing to do
   - in-progress → resume from last checkpoint

3. Recovery from in-progress:
   a. Read groups_done → skip these groups
   b. Read blocks_done → these are integrated; skip
   c. Read blocks_in_flight → these may be partially dispatched:
      - Check return queue; collect any returns that arrived
      - For blocks with no return: re-dispatch (idempotent — manifest scope unchanged)
   d. Resume from first group not in groups_done

4. Update governor-state.md: last_checkpoint:<now>
```

governor-state.md checkpoint fields (updated before each critical step):

```
last_checkpoint: ISO8601
checkpoint_action: dispatched_group_4B | collecting_returns | integrating | advancing
```

---

## Escalation triggers (halt and notify implementer)

Governor halts and surfaces to implementer when:

| Trigger | Action |
|---------|--------|
| 2+ consecutive blocked blocks in one group | Halt; show blocked block list |
| Dependency-required block fails twice | Halt; show dependency graph |
| governor-state.md missing or unreadable | Halt; show recovery instructions |
| Return package schema invalid (any block) | Halt immediately |
| Force-pass required (gate structural failure) | Halt; wait for approval |

Escalation format (Governor output to implementer):
```
GOVERNOR HALT: <reason>
  Phase: phase-N
  Group: <group-id>
  Block: block-NNN
  Failure: <failure mode>
  Options: [a] retry  [b] skip  [c] revise manifest  [d] force-pass
```

---

## Manual fallback (governor_mode: manual)

All failure handling decisions are made by the implementer directly:
- `status:blocked` → implementer decides retry / skip / halt
- `status:scope-exceeded` → implementer creates new block manually
- Timeout → implementer re-runs block manually in new session
- Gate failure → implementer follows `commands/block-close.md` gate failure flow

End of governor-failure-handling protocol.
