# Template: Audit Report

BRIEF: Written by the Governor (or by `audit.sh`) periodically. Located at `governance/audit-<YYYY-MM-DD>.md`. AI-readable + human-skimmable.

---

```yaml
---
id: audit-<YYYY-MM-DD>
trigger: scheduled | manual | phase-close | block-count
trigger_detail: <e.g., "every 30 blocks", "phase-1 close", "user requested">
ran_at: YYYY-MM-DDTHH:MMZ
ran_by: governor | audit.sh | <agent-id>
errors: <count>
warnings: <count>
result: pass | pass-with-warnings | fail
---
```

---

# Audit Report — <YYYY-MM-DD>

## Summary

- **Errors:** <count>
- **Warnings:** <count>
- **Result:** PASS | PASS WITH WARNINGS | FAIL

## Checks performed

| Check | Result | Detail |
|-------|--------|--------|
| HOT files exist | ✓ | All present |
| File size budgets | ⚠ | INDEX.md exceeded (260 > 250) |
| Pointer integrity | ✓ | All cross-references resolve |
| AI-only file format | ✓ | STATE/NEXT/board conform |
| Manifest schemas | ✓ | All parseable |
| Dependency graph | ✓ | No cycles |
| Lock health | ✓ | No stale in-progress > 1h |
| File-conflict between agents | ✓ | No overlap in files.modify |

## Errors

[List each error with file path and explanation. If none: "None."]

## Warnings

[List each warning. If none: "None."]

## Drift indicators

- Open axiom overrides in last 30 days: <count>
- Blocks closed with `forced` status: <count>
- Manifests modified after closing: <count>
- Pointers added vs removed: <delta>

If drift is significant (overrides > 5, forced > 3, etc.), flag here.

## Action items

What to fix before next audit:
1. <item>
2. <item>

If clean: "None — keep going."

## Comparison to previous audit

| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Errors | <n> | <n> | <Δ> |
| Warnings | <n> | <n> | <Δ> |
| Blocks closed | <n> | <n> | +<n> |
| Phase status | <p> | <p> | <transition or "same"> |

---

End of audit report.
