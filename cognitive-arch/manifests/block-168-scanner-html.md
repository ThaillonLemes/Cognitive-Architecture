---
id: block-168
size: M
importance: critical
kind: implementation
phase: phase-30
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-167
files:
  read:
    - design/scanner.md
    - sdk/codebase_scanner.py
    - sdk/scanner_profile.py
    - sdk/scanner_deep.py
    - governance/ux-config.yaml
  modify:
    - sdk/codebase_scanner.py
    - governance/ux-config.yaml
  create:
    - sdk/scanner_html.py
    - sdk/tests/test_scanner_html.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-168-scanner-html.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_scanner_html.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
---

# Block 168 — HTML Generator: Full Dossier

- **Size:** M | **Importance:** critical
- **Kind:** implementation
- **Status:** pending
- **Mode:** shared (pessoal + corporativo)

## 1. Purpose

Gerador de HTML full dossier do scanner. Cada scan produz um HTML que o Piloto usa para
validar o entendimento da codebase antes de qualquer implementação. Seções obrigatórias:
mapa arquitetural, grafo de dependências, prova de raciocínio, flags de atenção, custo de tokens.

## 2. Dependencies

- block-167 (`DeepScanResult` com provas de raciocínio + L4 coexistência)

## 3. Files

- **Read:** `design/scanner.md`, `sdk/scanner_deep.py`, `governance/ux-config.yaml`
- **Modify:**
  - `sdk/codebase_scanner.py` — integrar geração de HTML após cada scan
  - `governance/ux-config.yaml` — adicionar campo `html_output: true` (default)
- **Create:**
  - `sdk/scanner_html.py` — gerador HTML com Mermaid inline
  - `sdk/tests/test_scanner_html.py`

## 4. Validation

- `pytest sdk/tests/test_scanner_html.py -v` → 0 failed
- HTML renderiza no browser sem erros; todas as seções presentes
- Diagrama Mermaid (mapa + grafo) renderiza corretamente
- `--no-html` suprime geração; `ux-config.yaml: html_output: false` suprime permanentemente
- Arquivo: `governance/scanner-output-<cliente>-<YYYYMMDD-HHMM>.html`

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mermaid sem CDN não renderiza | Med | Incluir Mermaid JS inline no HTML (sem dependência externa) |

## 7. Out of Scope

- Adaptive mode interativo (block-169)
- Versionamento / diff entre HTMLs anteriores

## 8. New Abstraction

**`ScannerHTMLReport`** (em `scanner_html.py`): recebe `ProjectProfile` + `DeepScanResult` +
custo de tokens → produz HTML completo. Separação facilita testes e permite reuso futuro.
