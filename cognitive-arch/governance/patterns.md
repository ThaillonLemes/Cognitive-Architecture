# governance/patterns.md

BRIEF: Auto-generated pattern report. Re-run: `python sdk/patterns_report.py --arch-root .`

**Generated:** 2026-05-28T03:24Z  
**Total patterns:** 2 (🔴 critical: 0 · 🟡 warn: 1 · 🔵 info: 1)

---

## Summary (top patterns by severity)

| Severity | Pattern | Occurrences | Last seen |
|----------|---------|-------------|-----------|
| 🟡 WARN | `scope-expansion-recurring` | 4 | block-097 |
| 🔵 INFO | `velocity-data-gap` | 4 | block-060 |

---

## 🟡 WARN — scope-expansion-recurring

**Rule:** R4  
**Description:** 4 of last 30 blocks had files added beyond manifest.  
**First detected:** block-057  
**Last detected:** block-097  
**Occurrences:** 4

**Evidence blocks:** `block-057`, `block-086`, `block-094`, `block-097`

_No recommendation yet. Run `sdk/recommendation_engine.py` to populate._

---

## 🔵 INFO — velocity-data-gap

**Rule:** R6  
**Description:** 4 of last 30 blocks are missing actual_duration_hours.  
**First detected:** block-057  
**Last detected:** block-060  
**Occurrences:** 4

**Evidence blocks:** `block-057`, `block-058`, `block-059`, `block-060`

_No recommendation yet. Run `sdk/recommendation_engine.py` to populate._

---

End of patterns.md.