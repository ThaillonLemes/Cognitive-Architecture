---
id: block-010
manifest: manifests/block-010-protocols-token-budgets.md
status: done
gates_passed: 2/2
completed_at: 2026-05-21T00:00Z
agent: main-session
commit: -
duration_actual_days: 0
tok_estimated: ~250
tok_src: estimated
---

# Block 010 Retrospective — PROTOCOLS.md Q2 token budget estimates

## 1. What was built

- Added one sentence to Q2 in `PROTOCOLS.md` immediately after the existing budget list:
  > "Token estimate (proxy): chars÷4. HOT boot target: **< 4,000 tok total**. Single HOT file soft cap: **1,000 tok**. Run `/token-audit` for breakdown. (SDK-exact measurement: Phase 5.)"
- Q2 now covers both line budgets (existing) and token budgets (new).
- PROTOCOLS.md line count increased by 1 line (within Q2 budget rules).

## 2. Tests added

None (doc-only block).

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| token-budget-in-q2 | ✓ | PROTOCOLS.md Q2 has "chars÷4", "4,000 tok", "/token-audit" |
| files-updated | ✓ | BLOCK_LOG.md updated at phase close |

## 4. Decisions made

- Kept addition to ≤2 lines (manifested ≤3). Single sentence covers all required information.
- Used **bold** for the two numeric targets (4,000 tok, 1,000 tok) to make them scannable.

## 5. Deferred to future blocks

- Token budget enforcement as a hard audit gate → Phase 5 (informational only for now)

## 6. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| PROTOCOLS.md | ~7,500 | ~1,875 |

```
tok_estimated: ~250  tok_src:estimated
```

## 7. Issues / surprises

None.

## 8. Files actually touched

- Modified: PROTOCOLS.md (Q2 section, +1 line)
- Otherwise as manifest.
