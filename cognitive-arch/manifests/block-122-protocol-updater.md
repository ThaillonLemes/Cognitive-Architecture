---
id: block-122
tier: M
kind: implementation
phase: phase-20
scope: phase-bound
status: planned
security: false
dependencies:
  - block-121
files:
  read:
    - sdk/pattern_analyzer.py
    - sdk/patterns_report.py
    - governance/patterns.md
    - templates/proposal.md
  modify:
    - sdk/session_start.py
  create:
    - sdk/protocol_updater.py
    - sdk/tests/test_protocol_updater.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/protocol_updater.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-122-protocol-updater.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-121]
created_at: 2026-05-28
---

# Block 122 — protocol_updater.py

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Build sdk/protocol_updater.py: reads governance/patterns.md, identifies patterns with signal_count_d1 ≥ 3, generates a proposal file in governance/proposals/ for each qualifying pattern. Never creates duplicate proposals (checks index.md before creating). Adds itself to session_start.py TOOL_RUNNERS with trigger_type:time, interval:7 days. Outputs count of proposals created to stdout.

## 2. Dependencies

- block-121: proposals/ directory + schema must exist

## 3. Files

- **Read:** sdk/pattern_analyzer.py (pattern schema), sdk/patterns_report.py (patterns.md format), governance/patterns.md, templates/proposal.md
- **Modify:** sdk/session_start.py — add `run_protocol_updater` to TOOL_RUNNERS
- **Create:** sdk/protocol_updater.py, sdk/tests/test_protocol_updater.py

## 4. Validation

- Run with governance/patterns.md containing 1 pattern with d1 ≥ 3 — confirm 1 proposal file created
- Run again — confirm no duplicate created (idempotent)
- Run with patterns below threshold — confirm 0 proposals created
- Check proposal file has valid YAML frontmatter matching templates/proposal.md schema
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pattern format changes break updater | Low | Updater reads patterns.md via regex (same as pattern_analyzer output); version-tolerant |
| Proposals created for false-positive patterns | Low | Human reviews all proposals; auto-apply always requires --accept --apply |
| governance/patterns.md missing | Low | Updater exits cleanly with "patterns.md not found — run pattern_analyzer first" |

## 7. Out of Scope

- Generating proposals from retros directly (pattern pipeline is the intermediary)
- Multi-file proposals (one target_file per proposal)

## 8. New Abstraction

`ProtocolUpdater.run(arch_root, dry_run=False)` → list of created proposal paths. `_make_proposal_id(pattern_id)` → deterministic id to prevent duplicates.
