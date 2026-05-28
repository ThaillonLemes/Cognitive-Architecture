# Protocol: Convention snippet generation

BRIEF: How the Governor selects which axioms to include in a task packet's `axioms:` field. Generates a lean block-kind-specific subset of PROTOCOLS.md — sub-agents receive only what applies to their work.

Design authority: `design/governor-v2.md §3` (Decision 1)
Axiom source: `PROTOCOLS.md` (19 axioms: P1-P6, Q1-Q7, C1-C6)

---

## Why convention snippets

Sending full PROTOCOLS.md (109 lines) to every sub-agent adds ~1,250 tokens per dispatch. Most axioms are irrelevant to any given block kind. A convention snippet is Governor-generated, 10-15 lines, containing only the axioms that apply.

---

## Block-kind to axiom mapping

Governor reads block `kind:` from the task packet and selects axioms from this table.

| Block kind | Core axioms (always include) | Optional axioms (include if relevant) |
|------------|------------------------------|--------------------------------------|
| `doc-only` | Q2, Q3, C2, C3, C6 | P1, P3 |
| `refactor` | Q2, Q3, Q4, C2, C4, C6 | P3, P5, Q6 |
| `enhancement` | Q2, Q3, Q5, Q6, C2, C4, C6 | P1, P4, Q4 |
| `bugfix` | Q3, Q4, Q6, C2, C4 | P5, P6, Q5 |
| `feature` | Q1, Q2, Q3, Q5, Q6, C2, C4, C6 | P1, P4, P6, C5 |
| `gate` | Q4 | P2, C2 |
| `discovery` | Q4, Q6, C2 | P2, P3 |

**Notes:**
- C1 (`[code-only]`) — include ONLY if block modifies source code files
- Q1 (`[code-leaning]`) — include for blocks introducing new protocols, templates, or shared abstractions
- Sorted in output: P-axioms first, then Q-axioms, then C-axioms

---

## Snippet format in task packet

`axioms:` field in compressed header:
```
axioms:Q2,Q3,C2,C3,C6
```

Followed by the convention snippet body (appended after the header, before the manifest):
```
--- convention snippet ---
Q2: File size budgets. HOT files have maximums; audit warns if exceeded.
Q3: Manifests precede work artifacts. No artifact without a manifest.
C2: No speculation. Describe what IS, what WAS, or what WILL DEFINITELY BE.
C3: BRIEF on large markdown files. Files over 100 lines start with BRIEF:.
C6: Retrospectives are facts, not stories. What was built, gates passed, deferred.
```

Snippet body = axiom ID + colon + verbatim PROTOCOLS.md axiom text (condensed to one line each).

---

## Governor generation procedure

```
1. Read block kind from task packet header (kind:)
2. Look up core axioms in mapping table above
3. Check optional axioms — include if:
   - block modifies HOT files (add P5, P6)
   - block creates new protocols/templates (add Q1)
   - block involves source code (add C1 if present)
4. Check manifest for axiom_override: field — adjust list accordingly
5. Sort: P first, then Q, then C (numeric within each group)
6. Write axioms: field (comma-separated, no spaces)
7. Append snippet body: one line per axiom (ID: condensed text)
```

---

## Staleness detection

Governor tracks PROTOCOLS.md content hash in `governance/governor-state.md`:
```
protocols_hash: <sha256-first-8-chars>
```

If hash changes between sessions → regenerate all convention snippet templates. Existing tasks in flight use their original snippets; new dispatches get updated snippets.

---

## Manual fallback (governor_mode: manual)

When no Governor is running, implementer selects axioms manually:
1. Read block `kind:` from manifest
2. Look up core axioms in mapping table above
3. Include optional axioms that apply to the block's context
4. Write `axioms:` in the task packet header by hand

End of convention-snippet-generation protocol.
