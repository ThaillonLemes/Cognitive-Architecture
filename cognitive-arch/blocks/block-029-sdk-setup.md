---
id: block-029
phase: phase-5
status: done
gates_passed: 3
gates_total: 3
created_at: 2026-05-22
---

# Block 029 Retrospective — Python project setup (`sdk/` skeleton)

## §1 What was built

- `sdk/__init__.py` — package marker with code header
- `sdk/requirements.txt` — `anthropic>=0.25.0`, stdlib only beyond that
- `sdk/governor.py` — functioning CLI with `--help`, `--dry-run`, `--block`, `--test-integration`, `--mode` flags; `--dry-run` correctly reads STATE.md and NEXT.md from ARCH_ROOT
- `governance/governor-state.md` — ephemeral session state template (blank values; crash recovery logic comes in block-035)
- `_syntax.md` — `governor_mode` key added (manual | sdk)

## §2 Gates

| Gate | Result | Evidence |
|------|--------|---------|
| governor-help | ✅ pass | `python sdk/governor.py --help` → exit 0, lists 4 flags |
| governor-dry-run | ✅ pass | `python sdk/governor.py --dry-run` → exit 0, prints STATE.md + NEXT.md content |
| files-created | ✅ pass | all 4 new files confirmed present |

## §3 Decisions / deviations

- **ARCH_ROOT bug fixed mid-block:** initial `governor.py` set `ARCH_ROOT = PROJECT_ROOT / "cognitive-arch"` which double-nested the path. Fixed to `ARCH_ROOT = Path(__file__).resolve().parent.parent`. Gate re-run confirmed fix.
- `governor-state.md` placed in `governance/` (per design/governor-v2.md §2 — "lives in `governance/`"). No `.gitignore` entry added yet — block-035 will decide on commit policy.

## §4 Scope

No scope expansion. All files within manifest declaration.

## §5 Token estimate

tok_in:~3500 tok_out:~1200 tok_src:estimated
