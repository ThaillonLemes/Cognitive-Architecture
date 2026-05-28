---
id: block-045
tier: M
kind: doc-only
phase: phase-6
scope: phase-bound
status: done
dependencies:
  - block-044
files:
  read:
    - RETROFIT.md
    - design/governor-v2.md
    - sdk/governor.py
    - sdk/config.py
    - STATE.md
  modify:
    - RETROFIT.md
  create: []
gates:
  - name: retrofit-mentions-governor-mode
    type: file-changed
    paths: [RETROFIT.md]
  - name: file-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 045 — RETROFIT.md: add Governor v2 two-tier section

- **Tier:** M
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Update `RETROFIT.md` to document the two-tier Governor v2 architecture. New adopters running the retrofit flow need to know: (a) Governor v2 exists as an optional SDK tier, (b) `governor_mode` in `STATE.md` controls which tier is active, (c) SDK tier requires Python 3.9+ and `pip install -r sdk/requirements.txt`, (d) manual tier works with zero additional dependencies.

## 2. Dependencies

`block-044` — INDEX.md sweep (so RETROFIT.md can reference the SDK files by their indexed paths).

## 3. Files

- **Read:** `RETROFIT.md` (full), `design/governor-v2.md` (two-tier arch summary), `sdk/governor.py` (CLI flags), `sdk/config.py` (env vars), `STATE.md`
- **Modify:** `RETROFIT.md`
- **Create:** none

## 4. Validation

- `RETROFIT.md` contains a section titled "Governor v2 (optional SDK tier)" or equivalent
- Section explains `governor_mode: manual` (default, zero extra deps) vs `governor_mode: sdk` (Python SDK)
- SDK installation step: `pip install -r sdk/requirements.txt`
- `ANTHROPIC_API_KEY` env var mentioned with link to console.anthropic.com
- `audit.sh` still exits 0 (no broken pointers introduced)

## 5. Gates

- `RETROFIT.md` file changed (content gate: contains "governor_mode")
- Standard block-close files updated

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| RETROFIT.md pointer references a file that doesn't exist yet | Low | Read INDEX.md before adding any pointers; only link to existing files |
| Section disrupts existing retrofit step numbering | Low | Add as a new appendix section, not inline in numbered steps |

## 7. Out of scope

- Rewriting the full RETROFIT.md from scratch
- Adding RETROFIT.md checks to audit.sh (Phase 7)
- Documenting Phase 7 async features (don't exist yet)
