---
id: block-167
size: L
importance: critical
kind: implementation
phase: phase-30
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-166
files:
  read:
    - design/scanner.md
    - sdk/codebase_scanner.py
    - sdk/scanner_profile.py
  modify:
    - sdk/codebase_scanner.py
    - sdk/scanner_profile.py
  create:
    - sdk/scanner_deep.py
    - sdk/tests/test_scanner_deep.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-167-scanner-deep.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_scanner_deep.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 3
---

# Block 167 — Deep Scan: L2 + L3 + L4 + Business Logic

- **Size:** L | **Importance:** critical
- **Kind:** implementation
- **Status:** pending
- **Mode:** shared (pessoal + corporativo)

## 1. Purpose

Implementa os níveis profundos de scan: L2 (padrões de arquitetura), L3 (estética e convenções),
L4 (coexistência de padrões — vigente vs. legado), e leitura de lógica de domínio para o L0.
Cada inferência gera uma prova de raciocínio (evidências usadas) para o HTML (block-168).

## 2. Dependencies

- block-166 (scanner core, `ProjectProfile`, CLI base)

## 3. Files

- **Read:** `design/scanner.md`, `sdk/codebase_scanner.py`, `sdk/scanner_profile.py`
- **Modify:**
  - `sdk/codebase_scanner.py` — integrar chamadas ao `scanner_deep.py`
  - `sdk/scanner_profile.py` — adicionar métodos para seções L2/L3/L4
- **Create:**
  - `sdk/scanner_deep.py` — motor de detecção de padrões + extração de domínio
  - `sdk/tests/test_scanner_deep.py`

## 4. Validation

- `pytest sdk/tests/test_scanner_deep.py -v` → 0 failed
- Smoke test L2: `--level L2` em fixture → seção L2 no perfil com padrão detectado + evidências
- L4: fixture com dois estilos de imports → ambos detectados; um classificado como vigente
- Lógica de domínio: perfil de fixture inclui entidades centrais e fluxos principais

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Checklist L2 não cobre o projeto-alvo | Med | Fallback: Claude lê arquivos-chave; graceful degrade com aviso |
| L4 classifica padrão errado em migração | Med | Override via `--context`; prova de raciocínio no HTML permite correção |

## 7. Out of Scope

- HTML rendering (block-168)
- Adaptive mode (block-169)

## 8. New Abstraction

**`DeepScanResult`** (em `scanner_deep.py`): dataclass com `pattern`, `evidence`, `confidence`,
`vigente`, `legado`, `domain_entities`, `domain_flows`. Consumida pelo HTML generator (block-168).
