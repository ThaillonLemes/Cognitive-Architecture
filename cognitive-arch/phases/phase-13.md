---
id: phase-13
status: planned
prev_phase: phase-12
exit_criteria_count: 4
blocks_count: 4
estimated_duration_days: 4
created_at: 2026-05-23
last_updated: 2026-05-23
owner: implementer
---

# Phase 13 — Architecture Integrity

BRIEF: Protect critical templates and protocols against accidental AI modification. Three-tier protection (immutable/guarded/open) + SHA integrity lock + restore command.

## 1. Purpose

Phases 14-17 will introduce significant modifications across protocols, templates, and SDK code. Before doing that, Phase 13 hardens the foundation by declaring which files are critical, locking their integrity via hashes, and giving the AI explicit behavior protocols for handling protected files. This protects against the well-known LLM failure mode where the AI obeys a user request to "simplify" or "rewrite" a template that should not be modified.

## 2. Goals

- Every critical file declares its protection level in frontmatter
- Audit detects integrity violations on `immutable` files via SHA comparison
- AI behavior protocol formalized: refuses immutable modification without override; requires textual confirmation for guarded
- A `/restore` command exists to recover canonical version of any file

## 3. Invariants

- Existing file contents not changed (only frontmatter added on top)
- `audit.sh` remains backward-compatible (new check 9 is `--strict`-gated)
- No file moves to a more restrictive tier without explicit decision

## 4. Dependencies

- Phase 12 complete (audit must be functional)
- `design/arch-v3.md §4` defines the protection tiers and file list

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Adding frontmatter to files breaks parsers expecting clean content | Low | Use standard YAML frontmatter; verify with current audit before commit |
| Hash lock becomes annoying when legitimately evolving architecture | Med | `architecture bump-locks` command + `axiom_override`-style override for one-off changes |
| AI ignores its own behavior protocol | Med | Protocol is read at session boot via CLAUDE.md update; documented in PROTOCOLS.md as new axiom candidate |

## 7. Exit Criteria

1. All 15 files listed in `design/arch-v3.md §4` (Tier `immutable`) carry `protection: immutable` frontmatter; all `guarded` files carry `protection: guarded`. Audit verifies presence.
2. `.integrity.lock` exists at repo root with SHA256 of all `immutable` files. `audit.sh` gains check 9 (`integrity-lock`) that compares hashes; FAIL in `--strict`, WARN in default.
3. `protocols/architecture-integrity.md` exists documenting: protection tiers, AI behavior protocol per tier, override procedure with confirmation phrase, log entry requirement.
4. `commands/restore.md` exists describing the `/restore <file>` procedure: pull canonical from `cognitive-arch/` (or git history), backup current to `_backups/`, require RESTORE confirmation.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-090 | Protection frontmatter | M | planned | `manifests/block-090-protection-frontmatter.md` |
| block-091 | Integrity lock file | M | planned | `manifests/block-091-integrity-lock.md` |
| block-092 | AI guarded modification protocol | M | planned | `manifests/block-092-guarded-modification-protocol.md` |
| block-093 | Restore canonical command | S | planned | `manifests/block-093-restore-command.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 4
  recommended_agents: 1
  groups:
    - id: 13A
      blocks: [block-090]
      type: sequential
      depends_on: []
    - id: 13B
      blocks: [block-091, block-092]
      type: parallel
      depends_on: [13A]
    - id: 13C
      blocks: [block-093]
      type: sequential
      depends_on: [13B]
```

block-090 declares frontmatter first; 091 (lock) and 092 (protocol) consume that declaration in parallel; 093 (restore) uses both as references.

## 10. Out of Scope

- OS-level read-only permissions (`chmod`) — not portable cross-platform
- Template content versioning (deferred to future)
- Multi-user override workflows (single-user system today)
- Asymmetric signing / cryptographic attestation (overkill for solo project)

---

End of phase-13.
