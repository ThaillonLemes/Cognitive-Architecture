---
id: block-057
tier: M
kind: implementation
phase: phase-7
scope: phase-bound
status: done
dependencies:
  - block-056
files:
  read:
    - audit.sh
    - sdk/governor.py
  modify:
    - audit.sh
  create:
    - sdk/audit_helpers.py
gates:
  - name: audit-check7
    cmd: bash audit.sh
    expect: "[7/8]"
  - name: audit-check8
    cmd: bash audit.sh
    expect: "[8/8]"
  - name: audit-exits-0
    cmd: bash audit.sh
    expect: "exit 0"
  - name: file-updated
    type: file-changed
    paths: [audit.sh, sdk/audit_helpers.py, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-22
---

# Block 057 — audit.sh checks 7+8: conflict + drift detection

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Implement audit.sh checks 7 and 8 using a Python helper script (`sdk/audit_helpers.py`) called from bash:
- **Check 7** — File-conflict detection: find any `files.modify` path declared in more than one `planned` manifest simultaneously.
- **Check 8** — Drift detection: find `block-NNN done` entries in `blocks/BLOCK_LOG.md` that have no corresponding `blocks/block-NNN-*.md` retrospective file.

## 2. Dependencies

`block-056` — checks 5+6 must be in audit.sh first (insert checks 7+8 after them).

## 3. Files

- **Read:** `audit.sh`, `sdk/governor.py` (for ARCH_ROOT reference)
- **Modify:** `audit.sh` (call sdk/audit_helpers.py for checks 7+8)
- **Create:** `sdk/audit_helpers.py` (Python; two functions: `check_conflicts()`, `check_drift()`)

## 4. Validation

- `bash audit.sh` output contains `[7/8] Checking file conflicts...`
- `bash audit.sh` output contains `[8/8] Checking drift...`
- `bash audit.sh` exits 0 (no conflicts or drift in current project)
- `sdk/audit_helpers.py --check drift` prints OK or WARN lines to stdout (bash reads exit code)

## 5. Gates

All three gates above.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python not in PATH when audit.sh runs | Med | Use `python` or `python3` with fallback; emit WARN (not ERROR) if Python unavailable |
| Block-NNN retro naming convention varies | Low | Glob `blocks/block-{id}-*.md` (wildcard for slug) |

## 7. Out of scope

- Cycle detection in dependency graph (requires topological sort; deferred to v2.2)
- Automatic conflict resolution
