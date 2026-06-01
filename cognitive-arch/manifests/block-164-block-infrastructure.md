---
id: block-164
size: M
importance: critical
kind: implementation
phase: phase-29
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-162
parallel_with:
  - block-163
files:
  read:
    - design/block-phase-redesign.md
    - sdk/block_start.py
    - sdk/block_close.py
    - sdk/gates.py
  modify:
    - sdk/block_start.py
    - sdk/block_close.py
    - sdk/gates.py
  create:
    - sdk/tests/test_block_infrastructure.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-164-block-infrastructure.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_block_infrastructure.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
---

# Block 164 — Block Infrastructure: Dual-Mode SDK

- **Size:** M | **Importance:** critical
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Implementa no SDK os novos campos e comportamentos de bloco definidos no redesign:
`size + importance` (dois critérios independentes), `wip_stage` (sub-etapas do bloco),
`paused` status, e os gates corporativos (`functionality-check`, `consistency-check`, `teach-ready`).

## 2. Dependencies

- block-162 (templates v2 ativos com os novos campos no frontmatter)

## 3. Files

- **Read:** `design/block-phase-redesign.md`, `sdk/block_start.py`, `sdk/block_close.py`, `sdk/gates.py`
- **Modify:**
  - `sdk/block_start.py` — ler `size + importance`; inicializar `wip_stage: implementing`
  - `sdk/block_close.py` — validar progressão `implementing → quality → teaching` antes de `done` (só mode=corporate); suportar `paused` com `paused_reason`
  - `sdk/gates.py` — adicionar gates corporativos: `functionality-check`, `consistency-check`, `teach-ready`
- **Create:** `sdk/tests/test_block_infrastructure.py`

## 4. Validation

- `pytest sdk/tests/test_block_infrastructure.py -v` → 0 failed
- Bloco MMORPG (mode=mmorpg): fecha com `wip_stage: implementing` sem exigir `quality` ou `teaching`
- Bloco corporativo (mode=corporate): `block_close.py` rejeita `done` se `wip_stage != teaching`
- `paused` bloco com `paused_reason` não dispara gates
- Gate `teach-ready` exibe checklist de 3 perguntas e aguarda confirmação manual

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `block_close.py` impõe `wip_stage` em blocos MMORPG antigos | High | Check condicional: só exige progressão se `mode == corporate` na fase pai |
| `consistency-check` gate requer `consistency_checker.py` não ainda implementado | Med | Gate verifica se checker existe; se não, produz aviso e passa (checker é phase-31) |

## 7. Out of Scope

- `consistency_checker.py` em si (phase-31)
- `teach_mode.py` em si (phase-31)
- Velocity tracking de `size + importance` (phase-32)

## 8. New Abstraction

**`CorporateGates`** (em `gates.py`): namespace para os três gates corporativos.
`functionality_check`, `consistency_check`, `teach_ready` — cada um com lógica própria mas
interface uniforme com os gates existentes. Justificativa: mantém a extensibilidade do sistema
de gates sem reescrever o core.
