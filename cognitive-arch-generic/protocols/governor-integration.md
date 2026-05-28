# Protocol: Governor integration

BRIEF: Defines the integration boundary between manual mode (today) and automated Governor v2 (SDK). Specifies which orchestration steps are human-followable vs. SDK-automated. Architecture remains usable without SDK.

Design authority: `design/governor-v2.md §3` (Decision 11) + `§9` (manual fallback)

---

## Integration principles

1. **Governor is optional.** The core architecture — manifests, gates, retrospectives, axioms — works without Governor or SDK. Governor automates the mechanical orchestration steps; it does not introduce new correctness requirements.
2. **All protocols are human-followable.** Every protocol in this repository can be executed manually by a human + Claude session. Governor adds speed and parallelism; judgment stays with the implementer.
3. **Two-tier architecture.** Feature flag `governor_mode: manual | sdk` in STATE.md selects the tier. Default is `manual`.

---

## Architecture tiers

```
┌─────────────────────────────────────────────────────┐
│  TIER 1 — Core (always active; no SDK required)      │
│                                                       │
│  manifests · gates · axioms · retrospectives          │
│  protocols · templates · phase docs · decisions       │
│  commands/block-start.md · commands/block-close.md    │
└─────────────────────────────────────────────────────┘
         ↓ governor_mode:sdk in STATE.md ↓
┌─────────────────────────────────────────────────────┐
│  TIER 2 — Automation (optional; SDK required)         │
│                                                       │
│  Governor dispatch (protocols/governor-dispatch.md)   │
│  Task packets (protocols/task-packet.md)              │
│  Automated returns (protocols/sub-agent-contract.md)  │
│  governor-state.md · parallel sub-agent execution     │
└─────────────────────────────────────────────────────┘
```

---

## SDK integration points (Phase 5 targets)

Five manual steps that Governor v2 automates via Claude Code SDK:

| # | Manual today | SDK-automated in v2.0 |
|---|-------------|----------------------|
| 1 | Human opens new Claude session, pastes task packet | Governor dispatches sub-agent via `sdk.run(task_packet)` |
| 2 | Human opens N tabs for parallel blocks | Governor calls `sdk.run()` N times simultaneously |
| 3 | Human copies return package from sub-agent session | Governor receives return package as SDK response |
| 4 | Human updates governor-state.md by hand | Governor writes `governance/governor-state.md` programmatically |
| 5 | Human validates gates by reading return package | Governor parses return schema, validates gate fields automatically |

Everything else (file writes, STATE.md updates, BLOCK_LOG.md appends, git commits) remains the same in both modes — Governor executes these as regular file and shell operations.

---

## File ownership

### Governor-owned files (automated mode)

| File | Governor action |
|------|----------------|
| `governance/governor-state.md` | Creates, overwrites each session; deleted on phase close |
| `board.md` | Updates agent rows on dispatch and return |
| `STATE.md` | Updates after each group completes |
| `NEXT.md` | Updates pointer after each group |
| `blocks/BLOCK_LOG.md` | Appends one line per completed block |

### Implementer-owned files (never auto-modified by Governor)

| File | Why |
|------|-----|
| `PROTOCOLS.md` | Architecture definition; human-edited only |
| `CLAUDE.md`, `INDEX.md` | Navigation; human-edited only |
| `design/governor-v2.md` (and all `design/`) | Domain knowledge; human-edited only |
| `decisions/` | ADRs; human-edited only |
| `phases/phase-N.md` | Phase plans; human-edited only |

### Sub-agent-owned files (per block)

| File | Sub-agent action |
|------|----------------|
| Files in `fmod:` | Writes per manifest |
| `blocks/block-NNN-slug.md` | Writes retrospective |

---

## Coexistence rules

- `governance/governor-state.md` is created fresh at phase start; overwritten on each Governor invocation; deleted (or archived) at phase close.
- `STATE.md` is updated by Governor after each group completes — NOT per block. Per-block updates come from block-close's `files-updated` gate validation.
- Retrospectives are always written by sub-agents; Governor never writes retrospectives.
- Governor never modifies manifests (`manifests/`). If scope needs to change, Governor creates a new block or surfaces to user.

---

## Transition path (manual → SDK)

To enable Governor v2 automation:

```
1. Set governor_mode:sdk in STATE.md
2. Ensure governor-state.md initialized (protocols/governor-dispatch.md Step 1)
3. Run Governor via SDK: governor.run(phase="phase-N")
4. Governor handles groups 4A → 4B → 4C automatically
5. User monitors board.md; intervenes only on needs-decision events
```

To revert to manual:
```
1. Set governor_mode:manual in STATE.md
2. Follow manual fallback in each protocol's "Manual fallback" section
```

End of governor-integration protocol.
