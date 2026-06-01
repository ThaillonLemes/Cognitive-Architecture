# Template: Manifest v2 — Tier L (Large)
# STATUS: RASCUNHO — pendente swap formal de templates/manifest-large.md (imutável)
# Aprovado em: design/block-phase-redesign.md (2026-06-01)

BRIEF: Para blocos grandes, cross-module, ou de feature completa. ≤ 12 arquivos (L) ou sem limite (XL). Inclui rollout plan quando aplicável.

Copiar para `manifests/block-<NNN>-<slug>.md`.

---

```yaml
---
id: block-<NNN>
size: L                               # L ou XL — escolher conforme tabela em block-phase-redesign.md
importance: normal                    # normal | critical
kind: implementation                  # implementation | refactor | gate | ticket | intake
phase: phase-<N>
scope: independent                    # geralmente independent ou cross-feature em size L/XL
status: pending                       # pending | wip | paused | done | failed | forced | reverted
wip_stage: ~                          # implementing | quality | teaching
paused_reason: ~
security: false
dependencies:
  - block-<NNN>
parallel_with:
  - block-<NNN>                       # blocos que podem rodar em paralelo
files:
  read:
    - <path>
  modify:
    - <path>                          # total modify + create ≤ 12 para size L; sem limite XL
  create:
    - <path>
rollout:
  strategy: feature-flag | direct | phased    # [opcional — include for XL ou prod-impact]
  activation: <when/how to activate>
  rollback: <how to revert if needed>
gates:
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-<NNN>-<slug>.md]
  - name: scope-clean
    type: fmod-check
  - name: tests-pass
    cmd: <test_cmd>
    expect: "0 failed"
  - name: lint-pass
    cmd: <lint_cmd>
    expect: "0 errors"
  - name: build-pass
    cmd: <build_cmd>
    expect: "exit 0"
  - name: integration-tests-pass
    cmd: <integration_test_cmd>
    expect: "0 failed"
  # [corporate]:
  # - name: functionality-check
  #   type: manual
  #   checklist: ["O que o ticket pediu está funcionando conforme o acceptance_criteria?"]
  # - name: consistency-check
  #   type: script
  #   cmd: python sdk/consistency_checker.py --profile governance/project-profile-<client_id>.md
  #   expect: "consistency_score >= 0.80"
  # - name: teach-ready
  #   type: manual
  #   checklist:
  #     - "Consigo explicar em 3 frases o que foi feito?"
  #     - "Consigo responder por que escolhi essa abordagem?"
  #     - "Consigo explicar o impacto para não-técnicos?"
  # - name: corporate-fields
  #   type: frontmatter-check
  #   required: [ticket_id, acceptance_criteria, reviewer, client_id]
# [corporate]:
# ticket_id: ~
# acceptance_criteria: ~
# reviewer: ~
# client_id: ~
created_at: YYYY-MM-DD
estimated_duration_hours: <number>
---
```

---

# Block <NNN> — <Title>

- **Size:** L / XL | **Importance:** normal | critical
- **Kind:** implementation | refactor | gate | ticket | intake
- **Status:** pending
- **Parallel-with:** <IDs que rodam em paralelo, se houver>

## 1. Purpose

Um parágrafo. O que este bloco entrega e por que o tamanho é justificado.

## 2. Dependencies

IDs com status `done`. Por que cada dependência é necessária.

## 3. Files

- **Read:** <lista>
- **Modify:** <lista>
- **Create:** <lista>

## 4. Validation

- Build: `<build_cmd>`
- Testes unitários: `<test_cmd>`
- Testes de integração: `<integration_test_cmd>`
- Lint: `<lint_cmd>`
- `[corporate]` Functionality: o acceptance_criteria está atendido?
- `[corporate]` Consistency: `python sdk/consistency_checker.py --profile ...`

## 5. Gates

Referência aos gates no YAML. Gates adicionais específicos deste bloco.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| <descrição> | high/med/low | <plano> |

## 7. Rollout Plan `[include for XL or prod-impact]`

- Estratégia: feature-flag | direct | phased
- Ativação: <quando e como ativar>
- Rollback: <como reverter se necessário>

## 8. Out of Scope

- <deferral 1>
- <deferral 2>

## 9. New Abstraction

Nome + justificativa (Rule of Three). Se não: "None."

## 10. `[corporate]` Acceptance Criteria Detail

- Happy path: <descrição>
- Edge cases: <lista>
- Definition of done: <critérios mensuráveis>

## 11. Parallel Execution Plan `[OPTIONAL — quando tem sub-blocos]`

```yaml
parallel_execution_plan:
  total_sub_blocks: <count>
  groups:
    - id: <Na>
      blocks: [<id1>, <id2>]
      type: parallel
      depends_on: []
```

## 12. Integration Boundaries

Pontos de toque com outros sistemas. Interfaces públicas que este bloco modifica.

## 13. Benchmarks `[OPTIONAL — performance blocks]`

- `bench_<name>`: p50 < <target>, p99 < <target>

---

Size L: file size target ≤ 10 KB. Size XL: sem limite — scope justifica o tamanho.
