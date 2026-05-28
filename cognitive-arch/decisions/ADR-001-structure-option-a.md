---
id: ADR-001
title: improvement-process-option-a-dogfood-total
status: accepted
created_at: 2026-05-20
decided_at: 2026-05-20
deciders: [user, AI]
context_phase: phase-1
context_block: block-001
---

# ADR-001 — Improvement process: Option A (dogfood total, Tier S as default)

## 1. Context

Before any phase-1 work could start, the meta-project needed a process decision: how strictly should the cognitive architecture apply its own block methodology to improvements of itself? Four options were evaluated in Session 1.

## 2. Decision

**Option A — dogfood total with Tier S as default.**

Every phase-1 improvement, regardless of size, goes through: manifest → implementation → gates → block-close (8-step). Tier S (≤2 files, doc-only or small-fix) is the default tier. Upgrade to Tier M only when >2 files are modified, an abstraction is introduced, or a gate requires running a script.

## 3. Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| A (dogfood total, Tier S default) | Self-validating; generates real evidence about Tier S overhead | Minor overhead for trivial 1-line fixes | ✓ chosen |
| B (lightweight — skip manifests for doc-only) | Less friction | Can't measure process against itself; no evidence base | Not chosen |
| C (hybrid — Tier S for doc, Tier M for scripts) | Balanced friction | Requires per-block judgment with no evidence; deferred version of same problem | Not chosen |
| D (defer structure decision) | No premature lock-in | Blocks all phase-1 work; defeats the purpose of Session 1 | Not chosen |

## 4. Consequences

- **Positive:** every block generates a retrospective; process is self-consistent; if Tier S overhead is too high, we have evidence to introduce Tier XS via ADR-002.
- **Negative:** single-line corrections carry 4 artifacts (manifest + STATE + NEXT + retrospective). Overhead is deliberately accepted as the measurement cost.
- **Neutral:** after 3–4 blocks, retrospectives will show whether Tier S is right-sized for this work. ADR-002 can adjust.

## 5. References

- Session 1 report: delivered in-conversation 2026-05-20
- Roadmap: `phase-0/03-roadmap-draft.md`

---
