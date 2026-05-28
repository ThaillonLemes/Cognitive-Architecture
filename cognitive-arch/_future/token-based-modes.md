# _future: Token-based operation modes

BRIEF: Operation modes (economical vs full-token-spend) parameterized by measured token consumption per block. Deferred until token metrics infrastructure exists.

status: deferred
created_at: 2026-05-23
deferred_reason: requires token measurement not yet implemented
originating_brainstorm: v3-evolution-questionnaire (Q12-Q13)
revisit_when: after Phase 14 (mining) generates token consumption patterns OR if/when SDK Python instrumentation lands

---

## Origin

During the v3 brainstorm, a "Modal Operation" phase was proposed (originally Phase 17) with three modes: Quality, Velocity, Discovery. After deeper discussion the design was rejected as immature:

- **Quality and Velocity** ended up being near-identical in proposed behavior
- **Discovery** had nothing meaningful to "disable" (the protocols it would loosen were already minimal in brainstorm/research contexts)
- The user's real intent was a **resource trade-off** (token cost vs depth), not a quality trade-off

The decision was to defer this pattern until proper token metrics infrastructure exists, then revisit with a sharper distinction.

---

## The actual need (as articulated)

> "Era ter um modo econômico e um modo full gasto de [tokens]"
> "Talvez a gente relaxaria mais com o tamanho dos arquivos HOT... só qualidade, não ter que ficar comprimindo eles demais"

Two trade-off axes emerged:

### Axis 1 — Token spend
- **Economical** — minimize tokens per block; compress aggressively; lean retros; minimal context loading
- **Full-spend** — maximize quality; allow large HOT files; verbose retros; load extensive context

### Axis 2 — Speed
- **Throughput** — many blocks per session; reduce per-block ceremony
- **Depth** — few high-quality blocks per session; full ceremony per block

These two axes are partially orthogonal and were conflated in the original design.

---

## Why we defer

To design this correctly we need:

1. **Token consumption per block measured** — currently `tok_in/tok_out` keys exist in `_syntax.md` but are not collected. Need SDK instrumentation or audit-time estimation refined to actual values.

2. **Per-mode cost model** — empirical data on how many tokens different ceremony levels actually consume. Without that, we'd be guessing.

3. **Quality outcome correlation** — does relaxed ceremony actually produce worse outcomes? Currently no metric for "block quality" exists (Phase 17 Brainstorm-v2 includes this as block-110 candidate).

Building modes before having any of these three pieces would produce a feature that's hard to evaluate and easy to misuse.

---

## When to revisit

Revisit this pattern when ALL the following are true:

- Token consumption is measured per block (audit or SDK)
- At least 50 blocks have measured token data (statistical relevance)
- Block quality score exists (from Phase 17 v3 work or follow-up)
- A clear user pain point articulates: "I want to spend less per block" or "I want to spend more for depth"

When those conditions are met, revisit with a fresh brainstorm framed around:
- What does "economical" actually cut?
- What does "full" actually add?
- How does the AI decide which mode for which block?
- Does Master Agent recommend mode based on block kind?

---

## Alternative paths

Instead of binary modes, consider:

- **Continuous dial**: a single `token_budget:` field in manifest that the AI interprets
- **Per-section toggles**: e.g., `retro_depth: minimal|standard|verbose` as independent setting
- **Adaptive**: Master Agent learns user preference from override patterns

These may prove better than binary modes when revisit happens.

---

## Related deferred work

- Token measurement infrastructure (no current home in roadmap)
- Block quality score (Phase 17 candidate)
- Adaptive Master Agent behavior (Phase 15+ future work)

---

End of token-based-modes deferred design.
