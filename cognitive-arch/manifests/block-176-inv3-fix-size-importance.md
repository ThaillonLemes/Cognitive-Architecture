---
id: block-176
size: XS
importance: normal
kind: refactor
phase: phase-33
scope: phase-bound
status: pending
wip_stage: ~
paused_reason: ~
security: false
dependencies:
  - block-175
files:
  read:
    - sdk/invariant_check.py
    - sdk/tests/test_invariant_check.py
  modify:
    - sdk/invariant_check.py
    - sdk/tests/test_invariant_check.py
  create: []
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-176-inv3-fix-size-importance.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: python -m pytest sdk/tests/test_invariant_check.py -v
    expect: "0 failed"
  - name: zero-inv3-v2
    type: manual
    checklist:
      - "python sdk/invariant_check.py --arch-root . mostra 0 warnings INV3 para blocos com size: em vez de tier:"
created_at: 2026-06-01
---

# Block 176 — Fix INV3: aceitar `size` + `importance` no lugar de `tier`

- **Size:** XS | **Importance:** normal | **Kind:** refactor
- **Status:** pending

## 1. Purpose

Atualizar `invariant_check.py` para que INV3 aceite `size:` (formato v2) como substituto de `tier:` (formato v1), eliminando os 42 warnings falsos dos blocos 162-175.

## 2. Dependencies

`block-175` (calendar_manager — último bloco da fase 32)

## 3. Files

- **Read:** `sdk/invariant_check.py`, `sdk/tests/test_invariant_check.py`
- **Modify:** `sdk/invariant_check.py` — `_manifest_tier()` e `check_inv3()` aceitam `size:` e `importance:`; `sdk/tests/test_invariant_check.py` — adicionar casos v2

## 4. Validation

- `python -m pytest sdk/tests/test_invariant_check.py -v` → 0 failed
- `python sdk/invariant_check.py --arch-root .` → 0 warnings INV3 para blocos v2

## 5. Out of Scope

- Não migrar retroativamente `tier:` para `size:` em retros antigas — blocos v1 mantêm `tier:` e continuam válidos
- Não remover INV3 — apenas ampliar para aceitar ambos os formatos
