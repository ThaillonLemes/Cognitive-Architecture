---
id: block-006
tier: S
kind: refactor
phase: phase-1
scope: phase-bound
status: done
dependencies: []
files:
  read:
    - _syntax.md
    - STATE.md
    - NEXT.md
    - board.md
  modify:
    - _syntax.md
  create: []
gates:
  - name: keys-added
    type: manual
    description: all 7 missing keys present in _syntax.md canonical list (alphabetical order maintained)
  - name: files-updated
    type: file-changed
    paths: [_syntax.md, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-20
---

# Block 006 — _syntax.md completeness sweep

- **Tier:** S
- **Kind:** refactor
- **Status:** wip

## 1. Purpose

`_syntax.md` canonical key list is missing 7 keys that appear in actual AI-only files (STATE.md, NEXT.md, board.md). Any AI using _syntax.md as a reference would not know these keys exist and might invent inconsistent alternatives.

Missing keys found:
| Key | Used in | Meaning |
|-----|---------|---------|
| `blocks_done:` | STATE.md | comma-separated completed block IDs in phase |
| `last_block:` | STATE.md | full ID of last completed block |
| `last_block_status:` | STATE.md | status of last block at close |
| `last_done:` | board.md | last completed block for this agent |
| `next_action:` | NEXT.md | specific next action (free text; vs `next:` which is a block ID) |
| `notes:` | STATE.md, NEXT.md | free-text annotation for human context |
| `status_detail:` | STATE.md | additional detail/context for status value |

## 2. Files

- **Read:** _syntax.md, STATE.md, NEXT.md, board.md
- **Modify:** _syntax.md
- **Create:** none

## 3. Validation

- _syntax.md canonical list contains all 7 keys above
- Alphabetical order of the list preserved

## 4. Out of Scope

- Changing how existing files use these keys
- Adding validation in audit.sh for these keys (Phase 3 / v1.3)
