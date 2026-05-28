---
id: block-037
tier: M
kind: doc-only
phase: phase-5
status: wip
files:
  read:
    - sdk/governor.py
    - sdk/convention_snippet.py
    - sdk/task_packet.py
    - sdk/return_validator.py
    - sdk/dispatch.py
    - sdk/integration.py
    - sdk/config.py
    - design/governor-v2.md
  modify:
    - design/governor-v2.md
  create: []
gates:
  - name: all-sdk-tests-pass
    type: cmd
    cmd: "python cognitive-arch/sdk/convention_snippet.py --test && python cognitive-arch/sdk/task_packet.py --test && python cognitive-arch/sdk/return_validator.py --test && python cognitive-arch/sdk/dispatch.py --test && python cognitive-arch/sdk/integration.py --test && python cognitive-arch/sdk/governor.py --test-integration"
    expect: "exit 0, all 6 module tests pass"
  - name: open-questions-resolved
    type: file-changed
    paths: [design/governor-v2.md]
created_at: 2026-05-22
---

# Block 037 — E2E validation + open questions resolved

- **Tier:** M
- **Kind:** doc-only
- **Status:** wip

## 1. Purpose

Run all 6 module self-tests as a regression suite. Document answers to all 7 open questions from `design/governor-v2.md §11` (marked `resolved:`) based on what was learned during implementation.

## 2. Files

- **Read:** all sdk/ modules, design/governor-v2.md
- **Modify:** `design/governor-v2.md` (update §11 with resolved: answers)
- **Create:** none

## 3. Validation

- All 6 `--test` commands exit 0 chained in one gate
- `design/governor-v2.md §11` has `resolved:` annotation for each of the 7 questions

## 4. Out of scope

- Live API key E2E (requires ANTHROPIC_API_KEY; manual validation by user)
- pytest setup (Phase 6+)
