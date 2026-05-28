---
id: block-046
tier: M
kind: doc-only
phase: phase-6
scope: phase-bound
status: done
dependencies:
  - block-045
files:
  read:
    - BOOTSTRAP.md
    - RETROFIT.md
    - design/governor-v2.md
    - sdk/requirements.txt
  modify:
    - BOOTSTRAP.md
  create: []
gates:
  - name: bootstrap-mentions-governor-mode
    type: file-changed
    paths: [BOOTSTRAP.md]
  - name: file-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 046 — BOOTSTRAP.md: add SDK install + governor_mode

- **Tier:** M
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Update `BOOTSTRAP.md` Phase 0 to include Governor v2 onboarding: SDK installation decision point (`governor_mode` selection), and the `pip install` step for users who choose the SDK tier. The bootstrap flow currently makes no mention of Governor v2 or the SDK.

## 2. Dependencies

`block-045` — RETROFIT.md update done first so language is consistent across both onboarding docs.

## 3. Files

- **Read:** `BOOTSTRAP.md` (full), `RETROFIT.md` (Governor v2 section just written), `design/governor-v2.md`, `sdk/requirements.txt`
- **Modify:** `BOOTSTRAP.md`
- **Create:** none

## 4. Validation

- `BOOTSTRAP.md` Phase 0 (or equivalent early section) contains a decision point: "Governor mode: manual (default) or sdk?"
- `governor_mode` key documented with its valid values (`manual | sdk`)
- SDK path: `pip install -r cognitive-arch/sdk/requirements.txt` included
- Manual path: "no extra steps required" stated explicitly
- `ANTHROPIC_API_KEY` env var mentioned for SDK path
- Language consistent with RETROFIT.md (same flag names, same install command)

## 5. Gates

- `BOOTSTRAP.md` file changed (content gate: contains "governor_mode")
- Standard block-close files updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bootstrap step count changes (disrupts "N-step flow" references) | Low | Add as an optional sub-step within existing Phase 0 structure, not a new numbered step |
| Inconsistency with RETROFIT.md wording | Low | Read RETROFIT.md before writing; copy exact flag names and command |

## 7. Out of scope

- Rewriting the full BOOTSTRAP.md Phase 0 flow
- Adding a "governor_mode" key to STATE.md template (already exists)
- Documenting Phase 7 features (async, file I/O)
