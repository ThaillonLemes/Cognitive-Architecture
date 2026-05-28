# Template: Task packet

BRIEF: Fill-in-the-blank template for creating a task packet. Used in both manual mode (human fills it) and automated mode (Governor generates it). Copy and fill before sending to a sub-agent.

Protocol reference: `protocols/task-packet.md`

---

Copy the block below as the FIRST message to a sub-agent session.
Remove comments (<!-- -->) before sending.

---

```
b:NNN                         <!-- block ID, e.g. b:018 -->
kind:KIND                     <!-- doc-only | refactor | enhancement | bugfix | feature | gate | discovery -->
phase:phase-N                 <!-- e.g. phase:phase-4 -->
gov:g-NNN                     <!-- Governor session ID, e.g. gov:g-001 -->
ts:YYYY-MM-DDTHH:MMZ          <!-- dispatch timestamp (UTC ISO 8601) -->
axioms:AXIOM,AXIOM,...        <!-- see protocols/convention-snippet-generation.md for mapping table -->
scope:closed                  <!-- closed | open | two-phase — see protocols/task-packet.md §Scope modes -->
retro_req:yes                 <!-- yes | no — almost always yes -->
tok_track:yes                 <!-- yes | no — almost always yes -->
fread:path/to/file,...        <!-- context files (from manifest files.read) -->
fmod:path/to/file,...         <!-- files to create/modify (from manifest files.modify + files.create) -->
```

**Optional fields** — add after required fields if relevant:
```
deps:block-NNN,...            <!-- dependencies already completed (informational) -->
notes:TEXT                    <!-- Governor note to sub-agent; use sparingly -->
deadline_ts:YYYY-MM-DDTHH:MMZ <!-- soft deadline for fallback timer -->
sid:s-SESSIONID               <!-- SDK sub-agent session ID (Governor-assigned) -->
```

---

**Convention snippet** — paste after the header:
```
--- convention snippet ---
AXIOM-ID: <verbatim axiom text from PROTOCOLS.md, one line each>
AXIOM-ID: <verbatim axiom text>
...
```

**Manifest** — paste after the convention snippet:
```
--- manifest ---
[paste full content of manifests/block-NNN-slug.md here]
```

---

## Usage (manual mode)

1. Copy the required-fields block above
2. Replace each `NNN` / `KIND` / `TIMESTAMP` / path placeholder
3. Look up axioms from `protocols/convention-snippet-generation.md` mapping table
4. Append convention snippet (selected axiom texts from PROTOCOLS.md)
5. Append full manifest content
6. Send as the first message to a new Claude sub-agent session

## Usage (automated mode — Governor)

Governor generates this programmatically per `protocols/governor-dispatch.md` Step 2.
Template serves as the structural reference; Governor fills fields from phase doc + manifest.

---

## Quick example (block-018)

```
b:018 kind:doc-only phase:phase-4 gov:g-001 ts:2026-05-21T10:00Z
axioms:Q2,Q3,C2,C3,C6 scope:closed retro_req:yes tok_track:yes
fread:design/governor-v2.md,_syntax.md fmod:protocols/task-packet.md

--- convention snippet ---
Q2: File size budgets. HOT files have maximums; audit warns if exceeded.
Q3: Manifests precede work artifacts. No artifact without a manifest.
C2: No speculation. Describe what IS, what WAS, or what WILL DEFINITELY BE.
C3: BRIEF on large markdown files. Files over 100 lines start with BRIEF:.
C6: Retrospectives are facts, not stories. What was built, gates passed, deferred.

--- manifest ---
[content of manifests/block-018-protocol-task-packet.md]
```

End of task-packet template.
