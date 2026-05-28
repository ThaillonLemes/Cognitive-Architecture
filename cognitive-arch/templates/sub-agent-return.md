# Template: Sub-agent return package

BRIEF: Fill-in-the-blank template for the final message a sub-agent emits at the end of block execution. Emit ONCE, as the last message. Governor parses this to validate gates and update project state.

Protocol reference: `protocols/sub-agent-contract.md`

---

Emit the block below as your LAST message in the sub-agent session.
Remove comments (<!-- -->) before sending. Send exactly ONE return package.

---

```
b:NNN                              <!-- block ID, e.g. b:018 -->
sid:s-SESSIONID                    <!-- first 6 chars of session hash or any unique ID -->
status:STATUS                      <!-- done | partial | blocked | scope-exceeded | needs-decision -->
ts:YYYY-MM-DDTHH:MMZ               <!-- completion timestamp (UTC ISO 8601) -->
gates:GATE-NAME:pass|fail,...      <!-- one entry per gate declared in manifest; e.g. gates:protocol-exists:pass -->
fmod:path/to/file:LINES,...        <!-- each file modified; format path:lines_changed; use - if none -->
fread:path/to/file,...             <!-- ALL files read (including those not in task packet fread:); use - if none beyond task packet -->
scope_exp:-                        <!-- - | path/to/file (if you needed a file outside fmod:) -->
issues:-                           <!-- - | brief description of any problems encountered -->
retro:yes                          <!-- yes | no (must be yes if retro_req:yes in task packet) -->
retro_path:blocks/block-NNN-SLUG.md <!-- path to retrospective file you wrote -->
tok_in:~NNN                        <!-- input token estimate (chars/4 proxy); use 0 if unavailable -->
tok_out:~NNN                       <!-- output token estimate -->
tok_src:estimated                  <!-- estimated | actual -->
```

---

## Status-specific variations

### status:done — successful block

```
b:018 sid:s-abc123 status:done ts:2026-05-21T11:30Z
gates:protocol-exists:pass,format-spec-complete:pass,references-syntax:pass,files-updated:pass
fmod:protocols/task-packet.md:87
fread:design/governor-v2.md,_syntax.md
scope_exp:- issues:-
retro:yes retro_path:blocks/block-018-protocol-task-packet.md
tok_in:~1200 tok_out:~450 tok_src:estimated
```

### status:partial — some gates failed

```
b:NNN sid:s-ID status:partial ts:TIMESTAMP
gates:gate-a:pass,gate-b:fail,gate-c:pass
fmod:path/to/file:N fread:path,...
scope_exp:- issues:gate-b failed — <reason>
retro:yes retro_path:blocks/block-NNN-slug.md
tok_in:~N tok_out:~N tok_src:estimated
evidence: [gate-b] <one-line description of what failed and why>
```

### status:blocked — cannot complete

```
b:NNN sid:s-ID status:blocked ts:TIMESTAMP
gates:gate-a:fail
fmod:- fread:path,...
scope_exp:- issues:<specific reason you are blocked>
retro:no
tok_in:~N tok_out:~N tok_src:estimated
```

### status:scope-exceeded — needs a file outside fmod

```
b:NNN sid:s-ID status:scope-exceeded ts:TIMESTAMP
gates:gate-a:pass,gate-b:pass
fmod:path/to/declared-file:N fread:path,...
scope_exp:path/to/undeclared-needed-file.md issues:-
retro:yes retro_path:blocks/block-NNN-slug.md
tok_in:~N tok_out:~N tok_src:estimated
```

---

## Field rules

- `fmod:` — list every file you changed; `-` if you changed nothing
- `fread:` — list ALL files you read, including any not in task packet's `fread:`; Governor uses this to improve future task packets
- `scope_exp:` — only for files you needed to MODIFY (not just read); `-` otherwise
- `tok_in:` / `tok_out:` — use `~` prefix for estimates; exact if SDK session metadata available
- `evidence:` line — only append if a gate failed; plain text description of failure

End of sub-agent-return template.
