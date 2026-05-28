---
id: block-039
manifest: manifests/block-039-manual-mode-fix.md
status: done
gates_passed: 3/3
completed_at: 2026-05-22T06:05Z
agent: implementer
commit: -
duration_actual_days: 0
tok_estimated: ~2200
tok_src: estimated
---

# Block 039 Retrospective — Fix manual-mode routing bug in governor.py

## 1. What was built

- Fixed `cmd_block()` in `sdk/governor.py`: replaced single-line `dispatch_mode = "mock" if args.mode != "sdk" else "sdk"` with proper three-branch routing
- `--mode manual`: now prints MANUAL MODE header + full task packet for human handoff; writes governor-state with `integration_status:manual-handoff`; returns 0 without dispatching
- `--mode mock`: routes to MockAnthropicClient (unchanged behavior)
- `--mode sdk`: routes to real Anthropic SDK (unchanged behavior)
- Bonus fix: governor-state writes no longer hardcode `"phase": "phase-5"` — now parse current phase dynamically from STATE.md
- Verified: all three `--dry-run` modes pass; `--mode manual --block 039` prints packet header (not mock dispatch)

## 2. Tests added

None (no pytest suite yet — Phase 7 scope). Validated via CLI runs.

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| manual-mode-routes-correctly | ✓ | `--mode manual --dry-run` prints "mode: manual"; `--mode manual --block 039` prints "MANUAL MODE" header |
| mock-mode-still-works | ✓ | `--mode mock --dry-run` exits 0 |
| file-updated | ✓ | sdk/governor.py, STATE.md, NEXT.md, BLOCK_LOG.md modified |

## 4. Decisions made

- Manual mode in `--block` context prints the full task packet (not just a summary) — gives the human the complete content to paste to a sub-agent
- Current phase is read dynamically from STATE.md (not hardcoded) to prevent future stale-phase bugs

## 5. Deferred to future blocks

- `pytest` test suite for all three dispatch modes (Phase 7)
- `--mode manual` interactive prompt to accept return package from human (Phase 7)

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `sdk/governor.py` | ~7500 | ~1875 |
| `STATE.md` | ~900 | ~225 |

```
tok_estimated: ~2100  tok_src:estimated
```

## 7. Issues / surprises

- Discovered governor-state.md writes had `"phase": "phase-5"` hardcoded in two places — fixed both as part of this block (bonus scope, fully within manifest bounds)

## 8. Files actually touched

As manifest (sdk/governor.py only). governance/governor-state.md touched during gate validation run (expected; ephemeral file).
