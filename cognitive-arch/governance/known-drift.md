# governance/known-drift.md
# Accepted historical invariant drift — cognitive-arch
# Recorded by: block-147 (Phase 25 capstone)
# Date: 2026-05-30
# Scope: WARN-severity violations reported by `sdk/invariant_check.py` on the real arch-root

---

## Purpose

The invariant checker (`sdk/invariant_check.py`, INV1–INV6) runs on every block
close and at session start. After block-147 the real arch-root has **0 CRITICAL**
violations — the Phase 25 exit criterion. The WARN-severity violations below are
**accepted historical gaps**, not open action items. They predate the conventions
that would have prevented them, and back-filling them would mean fabricating
history (invented retros, invented tiers) rather than recording real data.

These are documented here so that:

- A reviewer reading the non-zero WARN total knows the gaps are known and accepted.
- Future drift (a *new* WARN beyond these baselines) stands out against a known baseline.
- The criticals-only block-close gate (`gate_result`) is unaffected — it HALTs on
  CRITICAL only; these WARNs never gate.

This file is descriptive. It introduces no whitelist and no code change — the
checker still reports these WARNs honestly; we simply accept them.

---

## INV2 — done blocks without a retro file (25 blocks: block-061 … block-085)

**Invariant:** every block marked `done` in `blocks/BLOCK_LOG.md` has a
`blocks/block-NNN-*.md` retro file.

**Accepted gap:** blocks **061 through 085** (inclusive, 25 blocks) are `done`
in BLOCK_LOG but have no retro file. These were completed in the **pre-retro-template
era** — before `templates/block-retrospective.md` and the block-close checklist made
a retro a required close artifact. The work shipped and is captured in BLOCK_LOG and
the codebase; the per-block retro document was simply never written at the time.

**Why not back-fill:** reconstructing 25 retros would fabricate durations, token
counts, and "what went well / what surprised us" narratives that nobody recorded.
That invents history rather than documenting the gap. Per Phase 25's risk note we
record the gap here instead of manufacturing 25 fake retros.

**Status:** ACCEPTED / HISTORICAL. Not an action item. From the retro-template era
onward, every `done` block has a retro, so this range does not grow.

---

## INV3 — retros with a duration but no resolvable tier (4 blocks: block-108 … block-111)

**Invariant:** every retro that records `actual_duration_hours` resolves a `tier:`
from either its own frontmatter or its matching manifest.

**Accepted gap:** blocks **108, 109, 110, 111** have retros carrying
`actual_duration_hours` but no `tier:` resolvable in the retro frontmatter or the
matching manifest. They were authored before `tier:` was consistently required on
both the retro and its manifest, so the duration is present but the tier is missing.

**Why not back-fill:** assigning a tier after the fact would guess at the
classification the block was sized under, polluting the velocity dataset with a
fabricated value. The honest record is "tier unknown for these four," which is what
this entry preserves.

**Status:** ACCEPTED / HISTORICAL. Not an action item. Newer retros carry an
explicit tier (in the retro or its manifest), so INV3 stays clean going forward.

---

## Not listed here

INV1 (immutable ⊆ `.integrity.lock`), INV4 (TOOL_RUNNERS ⊆ registry), INV5
(STATE/NEXT pointer consistency), and INV6 (proposals ↔ index) report **clean** on
the real root and have **no** accepted drift. Any violation they raise in the future
is real and must be handled — INV1/INV4 are CRITICAL and will HALT a block close.
