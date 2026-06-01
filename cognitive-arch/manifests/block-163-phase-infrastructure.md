---
id: block-163
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
files:
  read:
    - design/block-phase-redesign.md
    - design/corporate-mode.md
    - sdk/phase_manager.py
    - sdk/state_manager.py
    - sdk/session_start.py
    - templates/phase.md
  modify:
    - sdk/phase_manager.py
    - sdk/state_manager.py
    - sdk/session_start.py
    - templates/phase.md
  create:
    - sdk/tests/test_phase_infrastructure.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-163-phase-infrastructure.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_phase_infrastructure.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
---

# Block 163 — Phase Infrastructure: Dual-Mode

- **Size:** M | **Importance:** critical
- **Kind:** implementation
- **Status:** pending

## 1. Purpose

Implementa suporte dual-mode nas fases e no STATE. Após este bloco, fases podem ter
`mode: corporate | mmorpg | shared`, `type: feature | workday`, e `client_id`. O STATE.md
ganha estrutura para rastrear o estado cognitivo do Piloto no modo corporativo.

## 2. Dependencies

- block-162 (templates v2 ativos — `phase.md` atualizado usa nova estrutura)

## 3. Files

- **Read:** `design/block-phase-redesign.md`, `design/corporate-mode.md §3.4`, `sdk/phase_manager.py`, `sdk/state_manager.py`
- **Modify:**
  - `sdk/phase_manager.py` — suporte a `mode`, `type`, `client_id`; workday = sem doc (só STATE)
  - `sdk/state_manager.py` — STATE dual: estado do projeto (MMORPG) + estado cognitivo do Piloto (corporativo: entendimento atual, tickets abertos, gaps)
  - `sdk/session_start.py` — detecção de modo no boot; carrega seção correta do STATE
  - `templates/phase.md` — adicionar campos `mode`, `type`, `client_id` ao frontmatter
- **Create:** `sdk/tests/test_phase_infrastructure.py`

## 4. Validation

- `pytest sdk/tests/test_phase_infrastructure.py -v` → 0 failed
- Criar phase de teste com `mode: corporate, type: feature, client_id: visagio` → `phase_manager.py` valida sem erro
- `session_start.py --arch-root .` → carrega STATE sem crash nos dois modos
- Workday (`type: workday`) não gera arquivo de fase — registrado só no STATE

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| STATE dual-mode quebra parsing de sessões existentes | Med | Campos novos são opcionais — seção corporativa só aparece quando mode=corporate |
| `session_start.py` passa por muitas paths de execução | Med | Smoke test em ambos os modos (mmorpg + corporate) |

## 7. Out of Scope

- Scanner (que também usa `client_id` — já planeja consumir o campo)
- Forecast de velocity de tickets (phase-32)

## 8. New Abstraction

**`PilotState`** (em `state_manager.py`): seção do STATE para modo corporativo.
Campos: `current_client`, `tickets_open`, `knowledge_gaps`, `last_scan_at`.
Justificativa: STATE atual é orientado a projeto; o modo corporativo precisa de estado orientado ao Piloto.
