---
protection: immutable
protection_reason: "S-tier manifest schema. Changing this breaks all existing S-tier manifest validation."
restore_command: "git checkout HEAD -- templates/manifest-small.md"
---

# Template: Manifest Tier S (Small)

BRIEF: For investigation, single-file fix, lint sweep, doc-only changes, or pure refactor ≤ 2 files. Fill before any code change.

Copy to `manifests/block-<NNN>-<slug>.md`.

---

```yaml
---
id: block-<NNN>
tier: S
kind: investigation                   # investigation | refactor | doc-only | small-fix
phase: phase-<N>                      # optional for tier S
status: pending                       # planned | pending | wip | done | failed | forced | reverted
security: false                       # set to true for blocks touching auth, networking, or persistent data
files:
  read:
    - <path>                          # ≥1 path
  modify: []                          # ≤ 2 paths; empty for pure investigation
  create: []
gates:
  - name: tests-pass
    cmd: <test_cmd from PROJECT.md>
    expect: "0 failed"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
created_at: YYYY-MM-DD
# Optional:
# parallel_with: [block-<NNN>]
# axiom_override: "<axiom-id> — justification"
---
```

---

# Block <NNN> — <Title>

- **Tier:** S
- **Kind:** investigation | refactor | doc-only | small-fix
- **Status:** pending

## 1. Purpose

One sentence describing the outcome.

## 2. Files

- **Read:** <list>
- **Modify:** <list — max 2>
- **Create:** <list>

## 3. Validation

How we know it's done:
- `<test_cmd>` passes
- Investigation finding doc committed at `<path>` (if investigation)
- Lint clean (if refactor)

## 4. Out of scope

Things adjacent that are NOT in this block.

---

Total file size target: ≤ 500 bytes.

If the block grows beyond 2 files modified OR introduces an abstraction OR touches cross-system code → upgrade to Tier M before implementation.
