---
id: block-179
size: S
importance: normal
kind: implementation
phase: phase-33
scope: phase-bound
status: pending
wip_stage: ~
paused_reason: ~
security: false
dependencies:
  - block-178
files:
  read:
    - sdk/notification_manager.py
    - sdk/session_start.py
    - sdk/block_close.py
    - sdk/phase_manager.py
  modify:
    - sdk/notification_manager.py
    - sdk/block_close.py
    - sdk/phase_manager.py
    - sdk/tests/test_notification_manager.py
  create: []
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-179-surfacing-triggers.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_notification_manager.py -v
    expect: "0 failed"
  - name: triggers-funcionam
    type: manual
    checklist:
      - "Ao fechar uma fase, notificações pendentes são mostradas"
      - "Ao fechar um bloco em mode=corporate, notificações pendentes são mostradas"
      - "Ao completar um scan, notificações pendentes são mostradas"
created_at: 2026-06-01
---

# Block 179 — Surfacing por trigger: phase close, block close (corporate), scan complete

- **Size:** S | **Importance:** normal | **Kind:** implementation
- **Status:** pending

## 1. Purpose

Adicionar `notification_manager.surface(trigger)` e chamá-lo nos três checkpoints decididos no brainstorm: fim de fase, fim de bloco (mode=corporate), e fim de scan.

## 2. Dependencies

`block-178` (integração calendar completa — surfacing deve incluir reuniões)

## 3. Files

- **Read:** `sdk/notification_manager.py`, `sdk/session_start.py`, `sdk/block_close.py`, `sdk/phase_manager.py`
- **Modify:** `sdk/notification_manager.py` — adicionar `surface(trigger, arch_root)` com constantes de trigger; `sdk/block_close.py` — chamar `surface(TRIGGER_BLOCK_CLOSE)` quando mode=corporate; `sdk/phase_manager.py` — chamar `surface(TRIGGER_PHASE_CLOSE)`; `sdk/tests/test_notification_manager.py` — testar surface()

## 4. Triggers (Q3 do brainstorm)

| Constante | Quando chama | Mode |
|-----------|-------------|------|
| `TRIGGER_SESSION_START` | session_start.py (já existe) | todos |
| `TRIGGER_PHASE_CLOSE` | phase_manager.py ao fechar fase | todos |
| `TRIGGER_BLOCK_CLOSE` | block_close.py ao fechar bloco | só corporate |
| `TRIGGER_SCAN_COMPLETE` | codebase_scanner.py ao terminar scan | só corporate |

## 5. Validation

- `python -m pytest sdk/tests/test_notification_manager.py -v` → 0 failed
- Notificações pendentes aparecem ao fechar fase, bloco (corporate), e scan

## 6. Out of Scope

- Triggers mid-block para erros não-críticos
- Notificações por webhook / push externo → futura fase
