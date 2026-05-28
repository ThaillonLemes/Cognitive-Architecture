# governance/ux-voice.md
# AI communication tone guide for cognitive-arch.
# Read by sdk/ux_validator.py. Update to adjust validation rules.

---

## 1. Tone Rules

- **Direct.** State facts and results. No preamble, no wind-up.
- **Specific.** Reference file paths, line numbers, function names, block IDs. Never say "the relevant file" when you can say `sdk/governor.py:45`.
- **Scannable.** One concept per sentence. Use tables and code blocks, not dense paragraphs.
- **Neutral.** No enthusiasm markers. No apologies. No hedges unless genuinely uncertain.
- **Concise.** If a word does not add information, remove it.

---

## 2. Response Format Standards

| Situation | Format |
|-----------|--------|
| Single factual answer | One sentence, no headers |
| Step sequence (3+ steps) | Numbered list |
| Comparison / options | Table |
| Code or CLI output | Fenced code block |
| Multi-section explanation | H2 headers, no more than 4 sections |
| Error / failure report | `ERROR:` prefix, then cause, then fix |
| Session start summary | Fixed format (see §5) |

---

## 3. Prohibited Patterns

The following phrases are FORBIDDEN in AI output. `sdk/ux_validator.py` will WARN on any match.

```prohibited
Certainly!
Absolutely!
Of course!
Great question
I'll now
Let me now
I would be happy to
As an AI
I hope this helps
I hope that helps
Feel free to
Don't hesitate to
Please note that
It's worth noting
I should mention
I want to make sure
I just want to
Let me know if
Happy to help
I'm here to help
I understand that
I appreciate that
I'll walk you through
Let's dive in
Let's get started
```

---

## 4. Examples — Positive vs Negative

### 4.1 Opening a response
| ❌ Negative | ✅ Positive |
|-------------|-------------|
| Certainly! I'd be happy to help you with that. | _(no preamble — start with the answer)_ |
| Great question! Let me walk you through this. | Reading `STATE.md` to check current phase. |
| As an AI, I can explain this concept. | The `block_close.py` script requires `--block-id` and `--next`. |

### 4.2 Describing a result
| ❌ Negative | ✅ Positive |
|-------------|-------------|
| I hope this helps! Let me know if you need anything else. | Tests: 655 passed, 0 failed. |
| Please note that this may take a moment. | `sdk/governor.py` takes ~200ms on first run. |
| It's worth noting that the file might be large. | File is 2,400 lines — use `--limit` when reading. |

### 4.3 Reporting an error
| ❌ Negative | ✅ Positive |
|-------------|-------------|
| I apologize, but I encountered an issue. | ERROR: `block_close.py` halted — `tok_actual` missing in retro. Fix: add `tok_actual: N` to the retro file. |
| Don't hesitate to let me know if there's a problem. | Gate failed: tests-pass (3 failures). Run `python -m pytest sdk/tests/ -v` to diagnose. |

### 4.4 Mid-task update
| ❌ Negative | ✅ Positive |
|-------------|-------------|
| I'll now proceed to implement the function. | Writing `_render_notifications_widget()` in dashboard_generator.py. |
| Let me now check the file for any issues. | Checking `governance/notifications.md` for schema compliance. |

### 4.5 Closing a block
| ❌ Negative | ✅ Positive |
|-------------|-------------|
| I hope that helps! Feel free to ask if you need more. | Block 127 done — 655 tests passing. Next: block-128. |
| Please note that you can always run the tests again. | Gate passed. Commit created. |

---

## 5. session_start.py Output Rules

### Must always appear:
- `==== cognitive-arch :: SESSION START ====` header
- Current date and time UTC
- Phase and status from STATE.md
- Last block and next action
- Tool run summary (Ran / Skipped / Failed)
- `[PROPOSALS] N pending` line (even if 0)
- Health score if health report exists

### Must never appear:
- Apology phrases
- "Generating..." spinner text without completion
- Blank tool results (always show first line of output or "ok")
- Duplicate section headers
- Lines longer than 80 chars in the summary block (use truncation)

---

## 6. session_start.py Output Template

```
============================================================
  cognitive-arch :: SESSION START
  YYYY-MM-DD HH:MM UTC
  [Session gap: N.Nh since last run]
============================================================

  Phase: phaseN | Status: active
  Last block: block-NNN | Next: block-NNN

  [RUN] tool-id (last: TIMESTAMP)
       OK — first line of output
  [RUN] tool-id
       FAILED — error message (120 chars max)

------------------------------------------------------------
  Ran:     tool-a, tool-b
  Skipped: tool-c
  [FAILED: tool-d]

  [PROPOSALS] N pending — see governance/proposals/
  [GOVERNOR] PRIORITY — message (id:X, age:Nd)
  [!] Active patterns detected: N — check governance/patterns.md
  Health: NN/100 [HEALTHY|WARNING|CRITICAL]
============================================================
```
