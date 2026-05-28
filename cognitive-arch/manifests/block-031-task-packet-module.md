---
id: block-031
tier: M
kind: feature
phase: phase-5
status: wip
files:
  read:
    - protocols/task-packet.md
    - templates/task-packet.md
    - design/governor-v2.md
    - sdk/convention_snippet.py
  modify:
    - sdk/requirements.txt
  create:
    - sdk/task_packet.py
gates:
  - name: packet-test
    type: cmd
    cmd: "python cognitive-arch/sdk/task_packet.py --test"
    expect: "exit 0, packet assembled with all required fields"
  - name: files-created
    type: file-changed
    paths: [sdk/task_packet.py]
created_at: 2026-05-22
---

# Block 031 — Module: task packet builder

- **Tier:** M
- **Kind:** feature
- **Status:** wip

## 1. Purpose

Implement `sdk/task_packet.py` — given a manifest path and Governor metadata, parses the manifest YAML frontmatter, calls `convention_snippet.build_snippet()`, and assembles the full task packet string (header + convention snippet + manifest content) per `protocols/task-packet.md`.

## 2. Files

- **Read:** `protocols/task-packet.md`, `templates/task-packet.md`, `design/governor-v2.md`, `sdk/convention_snippet.py`
- **Modify:** `sdk/requirements.txt` (add pyyaml)
- **Create:** `sdk/task_packet.py`

## 3. Validation

- `python sdk/task_packet.py --test` exits 0
- Output contains all required header fields: b, kind, phase, gov, ts, axioms, scope, retro_req, tok_track, fread, fmod
- Output contains `--- convention snippet ---` and `--- manifest ---` delimiters

## 4. Out of scope

- Actual file content embedding (sub-agents read fread files themselves)
- SDK dispatch call (block-033)
- Two-phase scope negotiation (block-035)
