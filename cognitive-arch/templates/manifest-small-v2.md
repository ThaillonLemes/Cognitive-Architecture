# Template: Manifest v2 — Tier S (Small)
# STATUS: RASCUNHO — pendente swap formal de templates/manifest-small.md (imutável)
# Aprovado em: design/block-phase-redesign.md (2026-06-01)

BRIEF: Para blocos pequenos. ≤ 4 arquivos modificados/criados. Seções mais curtas — propósito em 1 frase.

Copiar para `manifests/block-<NNN>-<slug>.md`.

---

```yaml
---
id: block-<NNN>
size: S                               # XS | S | M | L | XL
importance: normal                    # normal | critical
kind: implementation                  # implementation | refactor | gate | ticket | intake
phase: phase-<N>
scope: phase-bound
status: pending                       # pending | wip | paused | done | failed | forced | reverted
wip_stage: ~                          # implementing | quality | teaching
paused_reason: ~
security: false
dependencies:
  - block-<NNN>
files:
  read:
    - <path>
  modify:
    - <path>                          # total modify + create ≤ 4 para size S
  create:
    - <path>
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-<NNN>-<slug>.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: <test_cmd>
    expect: "0 failed"
  # [corporate]:
  # - name: functionality-check
  #   type: manual
  #   checklist: ["O que o ticket pediu está funcionando?"]
  # - name: consistency-check
  #   type: script
  #   cmd: python sdk/consistency_checker.py --profile governance/project-profile-<client_id>.md
  # - name: teach-ready
  #   type: manual
  #   checklist: ["Consigo explicar em 3 frases?", "Consigo responder o porquê?", "Consigo explicar para não-técnicos?"]
# [corporate]:
# ticket_id: ~
# acceptance_criteria: ~
# reviewer: ~
# client_id: ~
created_at: YYYY-MM-DD
---
```

---

# Block <NNN> — <Title>

- **Size:** S | **Importance:** normal | critical
- **Kind:** implementation | refactor | gate | ticket | intake
- **Status:** pending

## 1. Purpose

Uma frase.

## 2. Dependencies

`block-<NNN>` (ou "None")

## 3. Files

- **Read:** <lista>
- **Modify/Create:** <lista> (≤ 4 total)

## 4. Validation

- Testes: `<test_cmd>` → 0 failed
- `[corporate]` O acceptance_criteria está atendido?

## 5. Out of Scope

- <deferral>

---

Size S: total file size target ≤ 2 KB.
