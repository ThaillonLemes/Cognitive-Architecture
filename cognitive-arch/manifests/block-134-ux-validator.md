---
id: block-134
tier: M
kind: implementation
phase: phase-22
scope: phase-bound
status: planned
security: false
dependencies:
  - block-131
  - block-132
  - block-133
files:
  read:
    - governance/ux-voice.md
    - sdk/session_start.py
    - sdk/health_report.py
  modify:
    - sdk/session_start.py
  create:
    - sdk/ux_validator.py
    - sdk/tests/test_ux_validator.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/ux_validator.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-134-ux-validator.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-131, block-132, block-133]
created_at: 2026-05-28
---

# Block 134 — sdk/ux_validator.py

- **Tier:** M
- **Kind:** implementation
- **Status:** planned

## 1. Purpose

Build sdk/ux_validator.py: reads governance/ux-voice.md to extract rules, then scans a target file or string for violations. Reports WARN lines for each violation (never errors; always exit code 0). Violations checked: prohibited phrases (from ux-voice.md prohibited section), missing required format elements, excessive hedge density. Integrate as optional post-run check in session_start.py: `python sdk/ux_validator.py --check session-output --arch-root .`

## 2. Dependencies

- block-131 + block-132 + block-133: all phase-22 features must be working before final validator is added

## 3. Files

- **Read:** governance/ux-voice.md (rule source), sdk/session_start.py (to add optional --validate-ux flag), sdk/health_report.py (sample output for validation target)
- **Modify:** sdk/session_start.py — add optional `--validate-ux` flag that pipes output through ux_validator
- **Create:** sdk/ux_validator.py, sdk/tests/test_ux_validator.py

## 4. Validation

- Run `python sdk/ux_validator.py --check governance/ux-voice.md` (self-check) — no prohibited phrases in the guide itself
- Create a test file with 3 known prohibited phrases — validator reports 3 WARNs
- Run `python sdk/ux_validator.py --check <clean-file>` — 0 WARNs
- Run session_start.py with --validate-ux — validator output appended to session summary
- exit code always 0 regardless of violations
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ux-voice.md prohibited phrases not parseable by regex | Low | ux-voice.md uses a fenced code block for prohibited patterns list; validator reads that section |
| Validator flags legitimate technical text | Low | Prohibited list is narrow and specific; rule of thumb: flag only clear filler/corporate-speak |
| --validate-ux in session_start.py adds latency | Low | Optional flag; not run by default; add to tools-registry.yaml as event-triggered, interval:0 |

## 7. Out of Scope

- ML-based tone analysis
- Validation of non-text files (images, YAML frontmatter)
- Auto-fixing violations (WARN only; human corrects)

## 8. New Abstraction

`UxValidator(rules_path)` class with `.check(text) -> list[Violation]`. `Violation(line_num, rule_id, message, excerpt)` dataclass. `UxValidator.from_ux_voice(arch_root)` factory that reads governance/ux-voice.md and extracts rules automatically.
