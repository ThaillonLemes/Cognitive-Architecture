---
id: block-170
size: L
importance: critical
kind: implementation
phase: phase-31
scope: phase-bound
status: pending
wip_stage: ~
security: false
dependencies: []
files:
  read:
    - design/pipeline.md
    - design/scanner.md
    - sdk/scanner_profile.py
    - governance/ux-config.yaml
  modify:
    - governance/ux-config.yaml
    - governance/tools-registry.yaml
  create:
    - sdk/consistency_checker.py
    - sdk/tests/test_consistency_checker.py
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-170-consistency-checker.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: pytest sdk/tests/test_consistency_checker.py -q
    expect: "0 failed"
created_at: 2026-05-31
estimated_duration_hours: 3
---

# Block 170 — Consistency Checker

- **Size:** L | **Importance:** critical
- **Kind:** implementation
- **Status:** pending
- **Mode:** corporate (consome project-profile do cliente)

## 1. Purpose

Implementa o checker que valida se o código gerado/modificado segue os padrões do projeto.
Lê seções L3/L4 do project-profile como fonte de verdade. Dois níveis: B (naming+imports+org,
padrão) e C (estilo interno, toggleável). Threshold dinâmico que sobe com a média histórica
mas nunca cai sem aprovação do Piloto.

## 2. Dependencies

Nenhuma dependência de blocos desta fase.
(Phase 30 completa é pré-requisito — checker requer L3/L4 no project-profile.)

## 3. Files

- **Read:** `design/pipeline.md`, `sdk/scanner_profile.py` (para ler o profile), `governance/ux-config.yaml`
- **Modify:**
  - `governance/ux-config.yaml` — adicionar seção `consistency_checker: {level_b: true, level_c: false}`
  - `governance/tools-registry.yaml` — registrar novo tool
- **Create:**
  - `sdk/consistency_checker.py` — checker com nível B+C, threshold dinâmico, export textual
  - `sdk/tests/test_consistency_checker.py`

## 4. Validation

- `pytest sdk/tests/test_consistency_checker.py -v` → 0 failed
- Diff sintético com 3 divergências conhecidas de naming → checker detecta exatamente 3
- Level C OFF (default) → estilo interno não verificado; Level C ON → detecta organização interna
- Threshold sobe após 5 blocos com score > threshold; threshold não cai sozinho
- Export textual: saída markdown simples copiável separada do HTML
- Checker sem L3/L4 no profile → erro claro com instrução de rodar scanner primeiro

## 5. Gates

- `files-updated`, `scope-clean`, `tests-pass`

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Level C gera falsos positivos em projeto permissivo | Med | C default OFF; ativado conscientemente pelo Piloto |
| Threshold dinâmico com poucos dados (primeiros blocks) | Med | Threshold estático até N=3 blocos; dinâmico só depois |
| Checker lento em diffs grandes | Low | Limite de linhas por diff; alerta se exceder |

## 7. Out of Scope

- HTML de qualidade (block-171)
- Big-O analysis (block-171)
- Cobertura de testes (block-171)

## 8. New Abstraction

**`ConsistencyReport`**: dataclass com `score`, `level_b_violations`, `level_c_violations`,
`threshold_used`, `text_export`. Consumida por `review_pipeline.py` (block-171) para gerar
o HTML de qualidade.
