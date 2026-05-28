---
id: block-007
tier: S
kind: doc-only
phase: phase-2
status: planned
dependencies: []
files:
  read:
    - PROTOCOLS.md
    - _syntax.md
    - templates/block-retrospective.md
  modify: []
  create:
    - commands/token-audit.md
gates:
  - name: command-exists
    type: file-exists
    paths: [commands/token-audit.md]
  - name: workflow-complete
    type: manual
    description: token-audit.md has step-by-step workflow covering HOT file scan, char/4 estimation, boot cost total, and per-file breakdown
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 007 — Token audit command

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned

## 1. Purpose

Create `commands/token-audit.md` — a step-by-step AI command for estimating token costs across all HOT files. Uses chars/4 proxy (no SDK required). Gives the implementer visibility into boot cost so they can keep the architecture lean.

## 2. Files

- **Read:** PROTOCOLS.md (Q2 budget), _syntax.md (tok_estimated key), templates/block-retrospective.md
- **Modify:** none
- **Create:** commands/token-audit.md

## 3. Spec

`commands/token-audit.md` must include:

1. **Trigger:** `/token-audit` or "how many tokens does the architecture use"
2. **Step 1 — List HOT files:** Read INDEX.md HOT section; collect all file paths
3. **Step 2 — Estimate per file:** For each file: count chars (approximate from line count × avg line length); divide by 4; record as `tok_estimated`
4. **Step 3 — Boot total:** Sum all HOT file estimates; compare to Q2 budget (4,000 tok HOT target)
5. **Step 4 — Report:** Table with columns: file | lines | est_chars | tok_estimated | tier
6. **Step 5 — Flag:** Files exceeding 1,000 tokens each get ⚠ flag
7. **Output format:** Uses _syntax.md keys (tok_estimated, tok_src:estimated)

## 4. Out of scope

- Actual SDK token measurement (Phase 5 / v2.0)
- Per-session token tracking
- Token budget enforcement as a gate
