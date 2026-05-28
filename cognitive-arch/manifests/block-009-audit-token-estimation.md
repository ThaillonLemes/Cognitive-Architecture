---
id: block-009
tier: S
kind: refactor
phase: phase-2
status: planned
dependencies: []
files:
  read:
    - audit.sh
    - INDEX.md
  modify:
    - audit.sh
  create: []
gates:
  - name: info-section-present
    type: manual
    description: audit.sh has INFO section printing HOT file token estimates (chars/4) and total boot cost
  - name: exit-code-unchanged
    type: manual
    description: audit.sh still exits 0 on clean, non-zero on errors — token INFO does not affect exit code
  - name: files-updated
    type: file-changed
    paths: [audit.sh, STATE.md, NEXT.md, blocks/BLOCK_LOG.md]
created_at: 2026-05-21
---

# Block 009 — audit.sh — token estimation INFO section

- **Tier:** S
- **Kind:** refactor
- **Status:** planned

## 1. Purpose

Extend `audit.sh` with an INFO section (after the existing 4 checks) that prints HOT file token estimates using the chars/4 proxy. This gives the implementer token visibility every time they run the audit without requiring any external tools.

## 2. Files

- **Read:** audit.sh, INDEX.md (to get HOT file list)
- **Modify:** audit.sh (append INFO section)
- **Create:** none

## 3. Spec

After existing checks [1/4] through [4/8], append:

```bash
# [INFO] Token estimates (chars/4 proxy — informational only)
echo ""
echo "[INFO] HOT file token estimates:"
for f in CLAUDE.md PROTOCOLS.md STATE.md NEXT.md INDEX.md _syntax.md; do
  if [ -f "$f" ]; then
    chars=$(wc -c < "$f")
    tokens=$(( chars / 4 ))
    echo "  $f: ~${tokens} tok"
  fi
done
# Sum total
total_chars=$(cat CLAUDE.md PROTOCOLS.md STATE.md NEXT.md INDEX.md _syntax.md 2>/dev/null | wc -c)
total_tok=$(( total_chars / 4 ))
echo "[INFO] Total HOT boot estimate: ~${total_tok} tok (target: <4000)"
```

The INFO section is purely informational — no PASS/FAIL, no exit code impact.

## 4. Validation

- `audit.sh` INFO section prints per-file estimates and a total
- Token total printed with a target reminder (<4000)
- Existing check exit codes unchanged

## 5. Out of scope

- SDK-based exact token count (Phase 5)
- Per-file token budget gates
- WARM/COLD file token reporting
