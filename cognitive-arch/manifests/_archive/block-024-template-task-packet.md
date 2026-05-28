---
id: block-024
tier: S
kind: doc-only
phase: phase-4
status: planned
dependencies: [block-017]
files:
  read:
    - design/governor-v2.md
    - protocols/task-packet.md
    - _syntax.md
  modify: []
  create:
    - templates/task-packet.md
gates:
  - name: template-exists
    type: file-exists
    paths: [templates/task-packet.md]
  - name: all-required-fields
    type: manual
    description: template has all required task-packet fields as placeholders with comments explaining each
  - name: optional-fields
    type: manual
    description: template includes optional fields section (clearly marked as optional)
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 024 — Template: task-packet

- **Tier:** S
- **Kind:** doc-only
- **Status:** planned
- **Dependencies:** block-017

## 1. Purpose

Create `templates/task-packet.md` — the fill-in-the-blank template for creating task packets, both for manual mode (human fills it out) and automated mode (Governor generates it). Provides a concrete starting point so neither humans nor the Governor have to construct packets from scratch.

## 2. Files

- **Read:** design/governor-v2.md (Section 3), protocols/task-packet.md, _syntax.md
- **Modify:** none
- **Create:** templates/task-packet.md

## 3. Spec

`templates/task-packet.md` content:

```markdown
# Task packet — Block NNN

<!-- Copy this header block as the first message to a sub-agent session -->
<!-- Remove comments before sending -->

b:NNN kind:KIND phase:PHASE-N gov:g-NNN ts:TIMESTAMP
axioms:AXIOM,AXIOM,...  <!-- see protocols/convention-snippet-generation.md -->
scope:closed            <!-- closed = execute manifest as-is; open = scope discovery allowed -->
retro_req:yes           <!-- yes = sub-agent must write retrospective -->
tok_track:yes           <!-- yes = sub-agent must report tok_in/tok_out -->
fread:FILE,FILE,...     <!-- files sub-agent should read (manifest fread section) -->
fmod:FILE,FILE,...      <!-- files sub-agent will modify or create (manifest fmod section) -->

<!-- OPTIONAL fields — include only if relevant -->
<!-- deps:block-NNN,...   completed dependencies -->
<!-- notes:TEXT           Governor notes to sub-agent -->

---
<!-- After header: paste the full content of manifests/block-NNN-*.md -->
<!-- Sub-agent reads this to understand what to implement -->
```

### Usage instructions (in the template file):
1. Copy the header block
2. Fill in all REQUIRED fields (remove <!--comments-->)
3. Add OPTIONAL fields if needed
4. Paste the manifest content after the separator
5. Send as first message to sub-agent session

## 4. Out of scope

- Return package template (→ block-025)
- Governor automation logic
