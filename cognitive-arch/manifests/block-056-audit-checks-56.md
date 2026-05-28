---
id: block-056
tier: M
kind: implementation
phase: phase-7
scope: phase-bound
status: done
dependencies:
  - block-051
files:
  read:
    - audit.sh
    - manifests/block-051-pytest-infra.md
  modify:
    - audit.sh
  create: []
gates:
  - name: audit-runs
    cmd: bash audit.sh
    expect: "[5/8]"
  - name: check5-schema
    cmd: bash audit.sh
    expect: "[6/8]"
  - name: file-updated
    type: file-changed
    paths: [audit.sh, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 056 — audit.sh checks 5+6: schema + dep validation

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Replace the "Governor-only" stub for checks 5 and 6 in `audit.sh` with bash-executable implementations:
- **Check 5** — Manifest schema: for each `manifests/block-*.md`, verify frontmatter contains `id:`, `tier:`, `kind:`, `status:`, and `files:` keys.
- **Check 6** — Dependency validation: for each manifest with `dependencies:`, verify each listed block-ID appears in `blocks/BLOCK_LOG.md`.

## 2. Dependencies

`block-051` — pytest infra (confirms bash environment works; logically grouped in 7A/7D).

## 3. Files

- **Read:** `audit.sh` (full), `manifests/block-051-pytest-infra.md` (sample manifest for testing)
- **Modify:** `audit.sh`
- **Create:** none

## 4. Validation

- `bash audit.sh` output contains `[5/8] Checking manifest schema...`
- `bash audit.sh` output contains `[6/8] Checking dependency validation...`
- No new errors introduced for existing manifests (all have required fields)
- `bash audit.sh` still exits 0

## 5. Gates

- audit.sh prints `[5/8]` and `[6/8]` sections
- audit.sh exits 0

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| awk/sed syntax differs between bash versions | Low | Test on Windows bash (Git Bash); use POSIX-compatible syntax |
| Manifests with `dependencies: []` (empty list) trigger false positive | Low | Skip dep-check if line reads `dependencies: []` |

## 7. Out of scope

- Checks 7+8 (block-057)
- Full YAML parsing (key presence only via grep/awk)
