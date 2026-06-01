---
id: block-171
size: M
importance: critical
kind: implementation
phase: phase-31
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies:
  - block-170
parallel_with:
  - block-172
files:
  read:
    - design/pipeline.md
    - sdk/consistency_checker.py
    - sdk/scanner_profile.py
    - governance/ux-config.yaml
  modify:
    - sdk/block_close.py
    - governance/ux-config.yaml
  create:
    - sdk/review_pipeline.py
    - sdk/tests/test_review_pipeline.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-171-review-pipeline.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_review_pipeline.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 2
---

# Block 171 — Review Pipeline + Quality Reporter

- **Size:** M | **Importance:** critical
- **Kind:** implementation
- **Status:** pending
- **Mode:** corporate

## 1. Purpose

Orquestra o ciclo implementar↔qualidade: executa o consistency checker, verifica cobertura
de testes e Big-O das funções modificadas, gera o HTML de qualidade, e apresenta o prompt
manual de go/no-go ao Piloto. Também atualiza `block_close.py` para integrar o quality
gate no fluxo de fechamento de bloco.

## 2. Dependencies

- block-170 (`ConsistencyReport`, checker funcionando)

## 3. Files

- **Read:** `design/pipeline.md`, `sdk/consistency_checker.py`, `governance/ux-config.yaml`
- **Modify:**
  - `sdk/block_close.py` — adicionar quality gate no fechamento de blocos `kind: ticket`
  - `governance/ux-config.yaml` — adicionar toggles `pipeline_quality_b` e `pipeline_quality_c`
- **Create:**
  - `sdk/review_pipeline.py` — orquestrador + HTML de qualidade + prompt Piloto
  - `sdk/tests/test_review_pipeline.py`

## 4. Validation

- `pytest sdk/tests/test_review_pipeline.py -v` → 0 failed
- `python sdk/review_pipeline.py --block-id block-XXX --arch-root .` → HTML gerado com consistency score, cobertura de testes da área, Big-O das funções novas
- Prompt go/no-go exibido com opções A (retornar) / B (override + razão) / C (ver detalhes)
- Override registra `gate_override_reason` no manifest do bloco
- `pipeline_quality_c: false` → seção de sugestões proativas ausente do HTML
- Export textual gerado separado do HTML

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Big-O analysis imprecisa em funções complexas | Med | Best-effort com aviso "estimativa" no HTML; Piloto valida |
| block_close.py integração quebra floco MMORPG | High | Quality gate condicional: só roda se `kind: ticket`; teste de não-regressão em bloco MMORPG |

## 7. Out of Scope

- Teach mode (block-172)
- Sugestões proativas de refatoração (nível C) são geradas pelo próprio review_pipeline mas desligadas por default

## 8. New Abstraction

**`QualityReport`**: dataclass com `consistency_report`, `test_coverage`, `big_o_findings`,
`suggestions` (opcional, nível C). Entrada para o HTML renderer e para o export textual.
