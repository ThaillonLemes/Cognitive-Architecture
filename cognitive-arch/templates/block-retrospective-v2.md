# Template: Block Retrospective v2
# STATUS: RASCUNHO — pendente swap formal de templates/block-retrospective.md (imutável)
# Aprovado em: design/block-phase-redesign.md (2026-06-01)

BRIEF: Escrita no fechamento do bloco. Fatos, sem narrativa. Em `blocks/block-<NNN>-<slug>.md`.
Seções marcadas [corporate] são obrigatórias quando mode=corporate; opcionais em modo mmorpg.

---

```yaml
---
id: block-<NNN>
manifest: manifests/block-<NNN>-<slug>.md
status: done                          # done | failed | forced | reverted
wip_stage_reached: implementing | quality | teaching    # sub-etapa final antes de done
gates_passed: N/M
completed_at: YYYY-MM-DDTHH:MMZ
agent: <agent-id>
commit: <short-hash>
actual_duration_hours: <number>       # tempo ativo de implementação em horas
duration_source: manual | auto-inferred | estimated
tok_estimated: ~<NNN>
tok_src: estimated                    # estimated | actual
---
```

---

# Block <NNN> Retrospective — <Title>

## 1. What was built

Bullets. Fatos. Exemplos:
- Adicionado `<arquivo>` com `<função>` que faz X.
- Modificado `<arquivo>` para tratar Y.
- Criado teste `<arquivo>` cobrindo Z.

## 2. Tests added

| Test | Type | Result |
|------|------|--------|
| `<test_name>` | unit | pass |
| `<test_name>` | integration | pass |

## 3. Gates passed

| Gate | Result | Evidence |
|------|--------|----------|
| files-updated | ✓ | STATE.md, NEXT.md, BLOCK_LOG.md modificados |
| scope-clean | ✓ | fmod_real ≤ fmod_declarado |
| tests-pass | ✓ | `<output snippet>` |
| `[corporate]` functionality-check | ✓ | acceptance_criteria atendido |
| `[corporate]` consistency-check | ✓ | score: 0.87 |
| `[corporate]` teach-ready | ✓ | checklist 3/3 |

## 4. Decisions

*Obrigatório em ambos os modos. Decisões não-óbvias tomadas durante o bloco.*

- "<Decisão concreta: escolhi X em vez de Y porque Z>"
- "<Padrão seguido: mantive o estilo de injeção de dependência do módulo de auth>"

Se nenhuma decisão foi tomada: "Sem decisões arquiteturais — implementação seguiu o manifest."

## 5. Deferred

O que este bloco tocou mas NÃO completou:
- <item> → endereçar em block-<NNN> ou fase futura

Se nada foi deferido: "None."

## 6. Analytics

*Dados estruturados para análise de tendências e melhoria contínua.*

```yaml
analytics:
  complexity_felt: <1|2|3|4|5>          # 1=trivial, 3=esperado, 5=muito mais difícil que o previsto
  estimation_accuracy: <on-track|over|under>  # tempo real vs. size estimado
  blockers:
    - "<o que travou — ex: 'API mal documentada', 'padrão inesperado no módulo X'>"
  rework_in_block: <true|false>          # precisou refazer algo dentro do bloco?
  pattern_learned:
    - "<padrão novo descoberto na codebase — ex: 'injeção via factory, não new direto'>"
```

## 7. Issues / Surprises

Qualquer coisa que divergiu do manifest:
- <descrição>

Se nada divergiu: "None."

## 8. Files actually touched

Se diferente do manifest declarado:
- Adicionado inesperadamente: <lista>
- Modificado inesperadamente: <lista>
- Não tocou como planejado: <lista>

Se exatamente como declarado: "As manifest."

## 9. `[corporate]` Teach Summary

*Como explicar o que foi feito. Preencher antes de qualquer reunião ou review.*

- **Leigo (gestor/cliente):** <1 frase sem jargão — o que mudou no produto?>
- **Técnico (developer):** <1 frase com contexto de código — o que foi implementado e como?>
- **Time (impacto lateral):** <o que outros devs precisam saber — mudou alguma interface, padrão, ou convenção?>

## 10. `[corporate]` Consistency Score

*Resultado do motor de consistência. Preencher se consistency-check foi executado.*

```yaml
consistency_score: 0.87               # 0.0 a 1.0 — alvo: ≥ 0.80
divergences:
  - "<divergência detectada — ex: 'naming de variável não segue o padrão camelCase do time'>"
```

## 11. Token estimate

| File read | Est. chars | tok_estimated |
|-----------|------------|---------------|
| `<file>` | ~NNN | ~NNN |

```
tok_estimated: ~<NNN>  tok_src: estimated
```

---

End of retrospective.
