---
id: block-169
size: M
importance: normal
kind: implementation
phase: phase-30
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-167
parallel_with:
  - block-168
files:
  read:
    - design/scanner.md
    - sdk/codebase_scanner.py
    - sdk/scanner_profile.py
  modify:
    - sdk/codebase_scanner.py
    - sdk/scanner_profile.py
  create:
    - sdk/scanner_adaptive.py
    - sdk/scanner_ticket.py
    - sdk/tests/test_scanner_adaptive.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-169-scanner-adaptive.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_scanner_adaptive.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
---

# Block 169 — Adaptive Mode + Ticket Inference + Profile Mgmt

- **Size:** M | **Importance:** normal
- **Kind:** implementation
- **Status:** pending
- **Mode:** shared (pessoal + corporativo)

## 1. Purpose

Três mecanismos de operação inteligente do scanner:
1. **Adaptive mode:** pré-scan assessment para projetos grandes — conta arquivos, estima custo, apresenta opções ao Piloto, aguarda confirmação antes de qualquer leitura massiva
2. **Ticket inference:** `--ticket <text>` → infere área provável → confirma com Piloto → executa scan parcial
3. **Profile management:** `--refresh-level`, multi-client (`--client`), update granular por seção

## 2. Dependencies

- block-167 (scanner_profile.py com seções L2/L3/L4; codebase_scanner.py com CLI base)

## 3. Files

- **Read:** `design/scanner.md`, `sdk/codebase_scanner.py`, `sdk/scanner_profile.py`
- **Modify:**
  - `sdk/codebase_scanner.py` — integrar adaptive mode e ticket inference
  - `sdk/scanner_profile.py` — `--refresh-level` e `--client` multi-profile
- **Create:**
  - `sdk/scanner_adaptive.py` — pré-scan assessment, estimativa de custo, prompt ao Piloto
  - `sdk/scanner_ticket.py` — inferência de área + confirmação
  - `sdk/tests/test_scanner_adaptive.py`

## 4. Validation

- `pytest sdk/tests/test_scanner_adaptive.py -v` → 0 failed
- Adaptive: repo com 1.000+ arquivos → exibe pré-scan com estimativa antes de qualquer leitura de código
- Ticket: `--ticket "JWT refresh"` → infere `src/auth` → exibe confirmação → após `[y]`, roda scan
- Refresh-level: `--refresh-level L3` → atualiza só L3; timestamps L0/L1/L2 preservados
- Multi-client: `--client clienteB` → `project-profile-clienteB.md` sem tocar `project-profile-clienteA.md`

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `--refresh-level` apaga dados acidentalmente | High | Backup da seção antes de sobrescrever + teste de não-regressão |
| Inferência de área errada para ticket ambíguo | Med | Confirmação obrigatória; Piloto pode corrigir ou usar `--area` direto |

## 7. Out of Scope

- Adaptive mode automático sem confirmação (intencionalmente excluído)
- Auto-detect via git diff (possível evolução futura)

## 8. New Abstraction

**`AdaptiveScanConfig`** (em `scanner_adaptive.py`): dataclass com resultado do pré-scan
(`file_count`, `estimated_tokens`, `estimated_usd`, `options`). Retornada antes de qualquer
leitura massiva — o caller decide se continua.
