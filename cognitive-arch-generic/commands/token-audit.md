# Command: /token-audit

BRIEF: Estimates token cost of all HOT files using chars÷4 proxy. Reports boot cost and per-file breakdown. No SDK required.

---

## Trigger

Use when:
- `/token-audit`
- "how many tokens does the architecture use"
- "what is the boot cost"
- "check token budget"

Auto-execute without asking for confirmation.

---

## Step 1 — List HOT files

Read `INDEX.md` and locate the HOT section. Collect all file paths marked HOT.

Standard HOT files (default set):
```
CLAUDE.md
PROTOCOLS.md
STATE.md
NEXT.md
INDEX.md
_syntax.md
```

If `board.md` is active (multi-agent session): add to list.
If `AGENT.md` exists for current agent: add to list.

---

## Step 2 — Estimate per file

For each HOT file:
1. Read the file (or use already-loaded content if in context)
2. Count characters: approximate as `line_count × avg_chars_per_line`
   - Dense key:value files (STATE.md, NEXT.md, _syntax.md): ~60 chars/line
   - Narrative files (PROTOCOLS.md, CLAUDE.md): ~70 chars/line
   - Mixed (INDEX.md): ~65 chars/line
3. Token estimate: `chars ÷ 4`
4. Record as `tok_estimated: ~NNN`

**Shortcut:** If file was already read this session, count actual chars from content.

---

## Step 3 — Calculate boot total

Sum all per-file token estimates.
Compare to Q2 budget targets:
- HOT boot total target: **< 4,000 tok**
- Per-file soft cap: **1,000 tok**

---

## Step 4 — Report

Output a table:

```
=== Token Audit — HOT file estimates ===
tok_src: estimated (chars÷4)

File              Lines   Est.chars   tok_est   Flag
--------------    -----   ---------   -------   ----
CLAUDE.md           58      4,060      ~1,015   ⚠
PROTOCOLS.md       107      7,490      ~1,873
STATE.md             3        160         ~40
NEXT.md              3        120         ~30
INDEX.md           180     11,700      ~2,925   ⚠
_syntax.md          90      5,400      ~1,350   ⚠

TOTAL HOT boot estimate: ~7,233 tok
Target: < 4,000 tok
Status: OVER BUDGET — consider WARM migration for oversized files
```

⚠ flag = file exceeds 1,000 tok individually.

---

## Step 5 — Flag and recommend

If total > 4,000 tok:
- List files exceeding 1,000 tok
- Suggest candidates for WARM migration (move detail to WARM, keep summary in HOT)
- Do NOT automatically move anything — report only

If total ≤ 4,000 tok:
- Report PASS

---

## Output format (_syntax.md)

Emit summary line at end of report:
```
tok_audit_total:~NNNN tok_src:estimated tok_hot_target:4000 status:PASS|OVER
```

---

## Notes

- This is an estimate only. Actual token count depends on model tokenizer.
- chars÷4 is accurate to ±30% for English/markdown text.
- SDK-based exact measurement: Phase 5 / v2.0.
- Run after any significant file change to catch budget overruns early.

End of token-audit command.
