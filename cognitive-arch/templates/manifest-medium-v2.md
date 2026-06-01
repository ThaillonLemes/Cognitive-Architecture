# Template: Manifest v2 — Tier M (Medium — default)
# STATUS: ATIVO — swap formal concluído em block-162 (fase 29, 2026-06-01)
# Aprovado em: design/block-phase-redesign.md (2026-06-01)
---
protection: immutable
protection_reason: "M-tier v2 manifest schema. Changing this breaks all M-tier manifest generation."
restore_command: "git checkout HEAD -- templates/manifest-medium-v2.md"
---

BRIEF: Default para blocos de implementação. ≤ 8 arquivos modificados/criados. Campos marcados [corporate] são opcionais no MMORPG e obrigatórios quando mode=corporate.

Copiar para `manifests/block-<NNN>-<slug>.md`.

---

```yaml
---
id: block-<NNN>
size: M                               # XS | S | M | L | XL
importance: normal                    # normal | critical
kind: implementation                  # implementation | refactor | gate | ticket | intake
phase: phase-<N>
scope: phase-bound                    # phase-bound | independent | cross-feature
status: pending                       # pending | wip | paused | done | failed | forced | reverted
wip_stage: ~                          # implementing | quality | teaching  (preencher quando status=wip)
paused_reason: ~                      # preencher quando status=paused
security: false                       # true se toca auth, rede, dados persistentes, ou prod
dependencies:
  - block-<NNN>
files:
  read:
    - <path>
  modify:
    - <path>                          # total modify + create ≤ 8 para size M
  create:
    - <path>
gates:
  # --- Universal (ambos os modos) ---
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-<NNN>-<slug>.md]
  - name: scope-clean
    type: fmod-check                  # valida que fmod_real ≤ fmod_declarado
  # --- MMORPG (incluir quando mode=mmorpg ou mode ausente) ---
  - name: tests-pass
    cmd: <test_cmd from PROJECT.md>
    expect: "0 failed"
  - name: lint-pass
    cmd: <lint_cmd from PROJECT.md>
    expect: "0 errors"
  - name: build-pass
    cmd: <build_cmd from PROJECT.md>
    expect: "exit 0"
  # --- [corporate] (incluir quando mode=corporate) ---
  # - name: functionality-check
  #   type: manual
  #   checklist:
  #     - "O que o ticket pediu está funcionando conforme o acceptance_criteria?"
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
# [corporate — obrigatório quando mode=corporate] ---
# ticket_id: ~                        # ID do Jira/Linear/texto livre
# acceptance_criteria: ~              # o que define done para o cliente/reviewer
# reviewer: ~                         # quem vai revisar o PR (pode ser "to-define")
# client_id: ~                        # herdado da fase — confirma contexto
created_at: YYYY-MM-DD
# Opcional:
# parallel_with: [block-<NNN>]
# estimated_duration_hours: <number>
# axiom_override: "<axiom-id> — justification"
---
```

---

# Block <NNN> — <Title>

- **Size:** M | **Importance:** normal | critical
- **Kind:** implementation | refactor | gate | ticket | intake
- **Status:** pending
- **Mode:** herdado da fase (mmorpg | corporate | shared)

## 1. Purpose

Uma ou duas frases descrevendo o resultado entregue por este bloco.

## 2. Dependencies

IDs de blocos anteriores com status `done`. Formato: `block-<NNN>`.

## 3. Files

- **Read:** <lista de arquivos lidos como contexto>
- **Modify:** <lista de arquivos modificados>
- **Create:** <lista de arquivos criados>

## 4. Validation

Passos concretos de validação:
- Build: `<build_cmd>`
- Testes: `<test_cmd>`
- Lint: `<lint_cmd>`
- `[corporate]` Functionality: o que o ticket pede está funcionando?
- `[corporate]` Consistency: `python sdk/consistency_checker.py --profile ...`

## 5. Gates

Referência aos gates declarados no YAML. Gates adicionais se necessário.

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| <descrição> | high/med/low | <plano> |

## 7. Out of Scope

Deferrals explícitos (previne scope creep):
- <deferral 1>

## 8. New Abstraction

Se introduz nova trait, classe, base, ou utility: nome + justificativa (Rule of Three, Axiom Q1).

Se não: "None."

## 9. `[corporate]` Acceptance Criteria Detail

Expandir o `acceptance_criteria` do frontmatter com exemplos concretos e edge cases:
- Happy path: <descrição>
- Edge case: <descrição>

## 10. Benchmarks `[OPTIONAL — performance blocks]`

- `bench_<name>`: p50 < <target>, p99 < <target>

## 11. Integration Boundaries `[OPTIONAL — cross-module]`

Pontos de toque com outros sistemas.

---

Size M: total file size target ≤ 5 KB.
Se precisar de planejamento de rollout, coordenação cross-repo, ou critérios de ativação → upgrade para size L.
