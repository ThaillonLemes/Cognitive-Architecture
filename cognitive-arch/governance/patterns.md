# governance/patterns.md

BRIEF: Auto-generated pattern report. Re-run: `python sdk/patterns_report.py --arch-root .`

**Generated:** 2026-05-30T05:55Z  
**Total patterns:** 3 (🔴 critical: 0 · 🟡 warn: 2 · 🔵 info: 1)

---

## Summary (top patterns by severity)

| Severity | Pattern | Occurrences | Last seen |
|----------|---------|-------------|-----------|
| 🟡 WARN | `gate-failures-recurring` | 4 | block-132 |
| 🟡 WARN | `scope-expansion-recurring` | 9 | block-097 |
| 🔵 INFO | `velocity-data-gap` | 58 | block-060 |

---

## 🟡 WARN — gate-failures-recurring

**Rule:** R3  
**Description:** 4 of last 123 blocks had at least one gate failure.  
**First detected:** block-125  
**Last detected:** block-132  
**Occurrences:** 4

**Evidence blocks:** `block-125`, `block-127`, `block-131`, `block-132`

**Recommendation:** 1. Read the retrospectives of the failing blocks — which gates failed? 2. If the same gate fails repeatedly: revise its 

---

## 🟡 WARN — scope-expansion-recurring

**Rule:** R4  
**Description:** 9 of last 123 blocks had files added beyond manifest.  
**First detected:** block-052  
**Last detected:** block-097  
**Occurrences:** 9

**Evidence blocks:** `block-052`, `block-053`, `block-054`, `block-055`, `block-056`, `block-057`, `block-086`, `block-094`, `block-097`

**Recommendation:** 1. Add a block-start gate: 'has the manifest's files.modify list been finalized?' 2. When a new file is needed mid-block

---

## 🔵 INFO — velocity-data-gap

**Rule:** R6  
**Description:** 58 of last 123 blocks are missing actual_duration_hours.  
**First detected:** block-001  
**Last detected:** block-060  
**Occurrences:** 58

**Evidence blocks:** `block-001`, `block-002`, `block-003`, `block-004`, `block-005`, `block-006`, `block-007`, `block-008`, `block-009`, `block-010`, `block-011`, `block-012`, `block-013`, `block-014`, `block-015`, `block-016`, `block-017`, `block-018`, `block-019`, `block-020`, `block-021`, `block-022`, `block-023`, `block-024`, `block-025`, `block-026`, `block-027`, `block-028`, `block-029`, `block-030`, `block-031`, `block-032`, `block-033`, `block-034`, `block-035`, `block-036`, `block-037`, `block-038`, `block-039`, `block-040`, `block-043`, `block-044`, `block-045`, `block-046`, `block-047`, `block-048`, `block-049`, `block-050`, `block-051`, `block-052`, `block-053`, `block-054`, `block-055`, `block-056`, `block-057`, `block-058`, `block-059`, `block-060`

**Recommendation:** 1. For future blocks: fill actual_duration_hours at block-close (block-close-checklist step 5). 2. For recent missing bl

---

End of patterns.md.