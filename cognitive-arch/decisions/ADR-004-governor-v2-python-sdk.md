---
id: ADR-004
title: governor-v2-python-sdk
status: accepted
created_at: 2026-05-23
decided_at: 2026-05-21
deciders: [user, AI]
backfilled: true
original_decision_date: "2026-05-21 (approx. phase-4)"
context_phase: phase-4
context_block: block-017
---

# ADR-004 — Governor v2: Python SDK as orchestration layer

## 1. Context

Governor v1 was a purely manual protocol: a human (or AI in manual mode) followed `commands/governor.md` step-by-step to dispatch blocks, integrate worktrees, and update STATE/board. This worked for single-agent flows but had two failure modes: (a) the human forgot integration steps under time pressure, and (b) there was no programmatic way to check dependency completion across agents. By phase-4, the block corpus included 17+ blocks and the Governor was being skipped in practice.

The v3 brainstorm in `_brainstorm/governor-v2-redesign.md` identified that the Governor needed to be executable, not just readable.

## 2. Decision

**Implement Governor v2 as a Python SDK in `sdk/`.**

Core components:
- `sdk/audit_helpers.py` — conflict detection and drift checking (callable from `audit.sh`)
- `sdk/governor.py` (v2) — programmatic state machine for dispatch/integrate cycle
- All SDK modules: stdlib-only Python (no external dependencies), importable, unit-testable

The Governor remains `governor_mode:manual` until the SDK reaches feature parity (tracked in STATE.md). SDK components are built incrementally: each phase adds the modules it needs, calling them from `audit.sh` where possible.

## 3. Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| Keep manual-only Governor | No new tooling | Skipped in practice; no enforcement | Not chosen |
| TypeScript/Node.js SDK | Matches MMORPG orchestrator | Would diverge canonical arch from MMORPG; Python is universal on this machine | Not chosen |
| Bash-only scripts | Simpler than Python | Complex logic (dep graphs, retry logic) unreadable in Bash | Not chosen |
| **Python SDK (stdlib-only)** | Portable, testable, no install required, readable | Requires Python on PATH | ✓ chosen |
| External orchestration (Temporal, etc.) | Production-grade | Overkill for solo project; adds dependency | Not chosen |

## 4. Consequences

- **Positive:** audit.sh gains Python-backed checks (7 + 8) without shelling out to complex Bash. SDK grows incrementally per phase. No install step — Python stdlib only.
- **Negative:** Requires Python ≥ 3.8 on PATH. MMORPG orchestrator uses TypeScript (`orchestrator/governor.ts`) — the two will diverge but are intentionally independent.
- **Neutral:** `governor_mode:manual` stays in STATE.md until SDK reaches full dispatch capability. Manual and SDK modes coexist; block-close checklist is unchanged.

## 5. References

- Brainstorm: `_brainstorm/governor-v2-redesign.md`
- Phase doc: `phases/phase-4.md`
- Block manifests: `manifests/_archive/block-017-governor-v2-design.md` through `block-028`
- SDK root: `sdk/`

---

End of ADR.
