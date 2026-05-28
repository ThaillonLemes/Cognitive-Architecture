# Template: ADR (Architectural Decision Record)

BRIEF: One ADR per non-obvious decision. Located at `decisions/ADR-<NNN>-<slug>.md`. Number sequentially. The code references the ADR ID; the ADR carries the rationale.

Copy this file to `decisions/ADR-<NNN>-<slug>.md`.

---

```yaml
---
id: ADR-<NNN>
title: <slug-title>
status: proposed                      # proposed | accepted | superseded | rejected
created_at: YYYY-MM-DD
decided_at: YYYY-MM-DD                # filled when status flips
deciders: [<who>]
supersedes: ADR-<NNN>                 # optional — if this replaces an earlier decision
superseded_by: ADR-<NNN>              # filled later if this ADR is replaced
context_phase: phase-<N>              # optional
context_block: block-<NNN>            # optional
---
```

---

# ADR-<NNN> — <Title>

## 1. Context

What is the issue we are addressing? Why is this decision required now?
Provide enough background that a future reader (or AI) understands the problem without re-discovering it.

## 2. Decision

What did we decide? State it clearly and unambiguously.

## 3. Alternatives considered

What other options did we evaluate?

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| <option A> | ... | ... | ... |
| <option B> | ... | ... | ... |
| <chosen> | ... | ... | ✓ chosen |

## 4. Consequences

What follows from this decision?

- **Positive:** what gets easier or better
- **Negative:** what gets harder or constrained
- **Neutral / Trade-off:** what changes without strict gain or loss

## 5. References

- Phase doc: `phases/phase-<N>.md`
- Block manifest: `manifests/block-<NNN>-<slug>.md`
- Design doc: `design/<doc>.md`
- External: <links if any>

---

End of ADR.
