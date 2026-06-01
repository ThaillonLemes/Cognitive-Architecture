---
id: block-173
size: M
importance: critical
kind: implementation
phase: phase-32
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies: []
files:
  read:
    - design/forecast-calendar.md
    - sdk/block_start.py
    - sdk/block_close.py
    - sdk/phase_manager.py
    - sdk/velocity_inference.py
  modify:
    - sdk/block_start.py
    - sdk/block_close.py
    - sdk/phase_manager.py
    - sdk/velocity_inference.py
    - governance/tools-registry.yaml
  create:
    - sdk/velocity_tracker.py
    - sdk/tests/test_velocity_tracker.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-173-velocity-tracker.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_velocity_tracker.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
finished_at: 2026-06-01T08:55Z
actual_duration_hours: 0.0
---

# Block 173 — Velocity Tracker: Timestamps + Pausa/Retomada

- **Size:** M | **Importance:** critical
- **Kind:** implementation
- **Status:** pending
- **Mode:** shared (MMORPG + corporativo)

## 1. Purpose

Implementa a captura automática de tempo real por bloco e por fase — nos dois modos.
`block_start.py` registra `started_at`; `block_close.py` registra `finished_at` e calcula
`actual_duration_hours`. Suporte a pausa/retomada para descontar reuniões e interrupções.
`phase_manager.py` ganha `phase_started_at`/`phase_finished_at`. `velocity_inference.py`
existente reorientado para usar os campos reais.

## 2. Dependencies

Nenhuma dependência de blocos desta fase.
(Phase 29 completa é pré-requisito — modificamos block_start.py, block_close.py, phase_manager.py.)

## 3. Files

- **Read:** `design/forecast-calendar.md`, módulos existentes acima
- **Modify:**
  - `sdk/block_start.py` — adicionar `started_at: <ISO>` ao manifest ao iniciar bloco
  - `sdk/block_close.py` — adicionar `finished_at`; chamar velocity_tracker para calcular duração
  - `sdk/phase_manager.py` — adicionar `phase_started_at` ao iniciar fase; `phase_finished_at` ao fechar
  - `sdk/velocity_inference.py` — reorientar para ler `actual_duration_hours` dos manifests fechados
  - `governance/tools-registry.yaml` — registrar `velocity_tracker`
- **Create:**
  - `sdk/velocity_tracker.py` — CLI `--pause`/`--resume`/`--status`; cálculo de duração com desconto de pausa
  - `sdk/tests/test_velocity_tracker.py`

## 4. Validation

- `pytest sdk/tests/test_velocity_tracker.py -v` → 0 failed
- Fechar bloco com `started_at` e `finished_at` → `actual_duration_hours` correto
- Pausa + retomada: `paused_duration` descontada → duração real menor que clock time
- `velocity_inference.py --arch-root .` com 5 blocos fechados → retorna velocity real (não "INSUFFICIENT DATA")
- Fase fechada → `phase_duration_hours` calculada no arquivo de fase
- Blocos antigos sem `started_at` → ignorados pelo velocity_inference (não quebra)

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Modificar block_start/block_close quebra blocos MMORPG existentes | High | Campos novos são opcionais; blocos sem timestamp continuam funcionando |
| Pausa esquecida (Piloto saiu sem pausar) | Low | Sem pausa registrada = assume tempo contínuo; aceitável na v1 |

## 7. Out of Scope

- Forecast HTML (block-174)
- Calendar manager (block-175)

## 8. New Abstraction

**`VelocityRecord`** (em `velocity_tracker.py`): lê todos os manifests fechados com `actual_duration_hours`
e computa médias por size, por modo e por período. Consumida pelo `forecast_engine.py` (block-174).
