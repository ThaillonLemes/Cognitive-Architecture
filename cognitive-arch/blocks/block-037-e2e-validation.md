---
id: block-037
phase: phase-5
status: done
gates_passed: 2
gates_total: 2
created_at: 2026-05-22
---

# Block 037 Retrospective — E2E validation + open questions resolved

## §1 What was built

- Regression suite: 6 module self-tests chained in one gate command — all pass
- `design/governor-v2.md §11` fully updated: each of the 7 open questions marked `resolved:` with one-line answer referencing the implementing module

## §2 Gates

| Gate | Result | Evidence |
|------|--------|---------|
| all-sdk-tests-pass | ✅ pass | 6/6 modules exit 0: convention_snippet, task_packet, return_validator, dispatch, integration, governor --test-integration |
| open-questions-resolved | ✅ pass | design/governor-v2.md §11 updated with resolved: for all 7 questions |

## §3 Open questions summary

| # | Question | Resolved by |
|---|----------|-------------|
| 1 | SDK file passing | sdk/dispatch.py — text only; sub-agent reads fread files itself |
| 2 | Token measurement in manual mode | return_validator + dispatch — estimated proxy is sufficient |
| 3 | Governor crash recovery | sdk/governor.py _write_governor_state() before each transition |
| 4 | Sub-agent identity | dispatch.py — ephemeral; sid assigned by Governor |
| 5 | Max parallelism | sdk/config.py — max_parallel_agents=3, GOV_MAX_PARALLEL env |
| 6 | User interruption | sdk/config.py — governance/.pause file polling |
| 7 | Mixed codebase | sdk/integration.py — ARCH_ROOT + fmod: boundary; no collision |

## §4 Scope

No scope expansion. One file modified (design/governor-v2.md) per manifest.

## §5 Token estimate

tok_in:~3000 tok_out:~800 tok_src:estimated
