---
id: block-091
tier: M
kind: implementation
phase: phase-13
scope: phase-bound
status: pending
security: false
dependencies: [block-090]
files:
  read:
    - audit.sh
    - design/arch-v3.md
    - PROTOCOLS.md
  modify:
    - audit.sh
  create:
    - .integrity.lock
    - sdk/integrity_check.py
    - commands/integrity-bump.md
gates:
  - name: lock-file-exists
    type: file-changed
    paths: [.integrity.lock]
  - name: audit-check-9
    type: file-changed
    paths: [audit.sh]
  - name: integrity-script
    type: file-changed
    paths: [sdk/integrity_check.py]
  - name: dependencies-met
    type: deps-complete
    deps: [block-090]
  - name: state-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-091-integrity-lock.md]
created_at: 2026-05-23
estimated_duration_days: 1
---

# Block 091 — Integrity lock file

- **Tier:** M
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Create `.integrity.lock` at repo root containing SHA256 hashes of every file tagged `protection: immutable` in block-090. Add check 9 to audit.sh that compares current hashes to lock; FAIL in `--strict` mode, WARN in default (per Q4). Provide `architecture integrity-bump` helper command for legitimate evolution.

## 2. Dependencies

- block-090 (immutable files must be tagged before locking their hashes)

## 3. Files

- **Read:** audit.sh, design/arch-v3.md, PROTOCOLS.md
- **Modify:** audit.sh (add check 9: integrity-lock)
- **Create:** `.integrity.lock` (initial hashes), `sdk/integrity_check.py` (hash logic), `commands/integrity-bump.md` (procedure to regenerate lock when files evolve legitimately)

## 4. Validation

- `.integrity.lock` contains entries for each immutable file as `path  sha256:HASH`
- `audit.sh` check 9 runs, reports OK when hashes match, WARN/FAIL when mismatch
- `sdk/integrity_check.py` exposes `verify()` and `regenerate()` functions
- `commands/integrity-bump.md` documents the human-approval flow for lock regeneration

## 5. Gates

Per frontmatter. Audit must complete successfully after lock creation.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Lock file format breaks if path normalization differs across OS | Med | Use relative POSIX paths in lock; integrity_check.py normalizes |
| Legitimate edit triggers FAIL and blocks user | High | Default is WARN, not FAIL; `--strict` only in explicit CI mode |
| User forgets `integrity-bump` workflow | Med | Audit WARN message points to command |

## 7. Out of Scope

- Cryptographic signing (overkill for solo project per Phase 13 §10)
- Multi-branch lock awareness (single main branch project)
- Auto-bump on detected drift (always human-approved)

## 8. New Abstraction

`sdk/integrity_check.py` — new module. Justification: hash logic used by audit.sh, by `commands/integrity-bump.md`, and potentially by Master Agent in Phase 15. Three callers = Rule of Three met.
