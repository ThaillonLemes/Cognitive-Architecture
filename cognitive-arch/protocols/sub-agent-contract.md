# Protocol: Sub-agent contract

BRIEF: Obligations and constraints for every sub-agent. Defines what a sub-agent receives, what it must do, and what it must return. No deviations permitted.

Design authority: `design/governor-v2.md §7` (sub-agent lifecycle) + `§5` (return package)

---

## Sub-agent obligations (in order)

```
1. Parse task packet         read compressed header; extract all fields
2. Read context files        read every path in fread: — no more, no less
3. Execute block             implement per manifest spec; apply axioms from convention snippet
4. Run gates                 validate each gate in manifest; capture pass/fail + evidence
5. Write retrospective       if retro_req:yes → write blocks/block-NNN-slug.md per template
6. Emit return package       ONE final message in compressed _syntax.md format
```

After step 6 the sub-agent's work is complete. Governor handles all state updates.

---

## What the sub-agent MUST NOT do

| Prohibited action | Why |
|------------------|-----|
| Read files not in `fread:` (scope: closed) | Scope discipline; prevents context bloat |
| Modify files not in `fmod:` | Governor is the conflict arbitrator |
| Write STATE.md / NEXT.md / board.md / BLOCK_LOG.md | Governor owns all shared state |
| Commit to git | Governor owns all commits |
| Send more than one return message | Governor parses ONE structured response |
| Read files outside declared scope without reporting | Any undeclared read → `fread:` in return |

For `scope:open` blocks: sub-agent may read additional files but MUST list all reads in `fread:` field of the return package.

---

## Return package format

Sub-agent emits this as the final message. All keys from `_syntax.md`.

```
b:NNN sid:s-ID status:STATUS ts:ISO8601
gates:gate-name:pass|fail,gate-name2:pass|fail
fmod:path1.md:N,path2.md:N
fread:path1.md,path2.md,path3.md
scope_exp:- issues:-
retro:yes|no retro_path:blocks/block-NNN-slug.md
tok_in:N tok_out:N tok_src:actual|estimated
```

### Status values

| `status:` | Meaning |
|-----------|---------|
| `done` | All gates pass; return package complete |
| `partial` | Some gates pass; others fail; see `gates:` field |
| `blocked` | Cannot proceed; reason in `issues:` field |
| `scope-exceeded` | Required file outside `fmod:` scope; see `scope_exp:` |
| `needs-decision` | Ambiguity requires Governor/user input before continuing |

### Field rules

- `fmod:` — each entry is `path:lines_changed`; use `-` if no files modified
- `fread:` — ALL files read, including those not in task packet `fread:`; comma-separated; `-` if none beyond task packet
- `scope_exp:` — path of the undeclared file needed, or `-` if none
- `issues:` — brief description of any problem, or `-` if clean
- `tok_in:` / `tok_out:` — report 0 if measurement not available; set `tok_src:estimated`

---

## Gate failure in return package

If a gate fails:
1. Set `gates:gate-name:fail` in return header
2. Append evidence line after the main return block:
   ```
   evidence: [gate-name] <one-line description of what failed and why>
   ```
3. Set `status:partial` (if other gates passed) or `status:blocked` (if cannot proceed)

---

## Retrospective obligations (retro_req:yes)

Sub-agent must write `blocks/block-NNN-slug.md` per `templates/block-retrospective.md` BEFORE emitting return package. Path goes in `retro_path:` field.

Facts only. No narrative. See `protocols/block-retrospective-generation.md`.

---

## Scope expansion protocol

If sub-agent discovers it needs to modify a file NOT in `fmod:`:

**scope:closed** → HALT immediately. Emit:
```
status:scope-exceeded scope_exp:path/to/file.md issues:needs path/to/file.md to complete block
```
Governor decides: expand manifest or create new block.

**scope:open** → may read freely; cannot modify undeclared files. Report all extra reads in `fread:`.

**scope:two-phase** → send discovery report (files intended to modify) as first return; await Governor approval; then execute second pass.

---

## Failure escalation

Sub-agent cannot resolve the problem itself → emit:
```
status:blocked issues:<description>
```
Governor sees `status:blocked` → escalates per `protocols/governor-failure-handling.md`.

Sub-agent never retries silently. All failures are visible in the return package.

End of sub-agent-contract protocol.
