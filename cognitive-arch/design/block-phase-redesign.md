# Design: Block & Phase Redesign — Dual-Mode Architecture

status: approved
created_at: 2026-06-01
authors: Thaillon (Piloto) + AI (brainstorm v2 session)
synthesis_source: brainstorm session 2026-06-01 (Track #1 — Bloco & Fase)
supersedes: templates/manifest-{small,medium,large}.md v1, templates/block-retrospective.md v1
pending_swap: true   # os templates imutáveis precisam de bloco formal para serem substituídos
related: design/corporate-mode.md (§3.3, §6B), tracks/bloco-fase.md

---

## 0. Contexto

O redesign de Bloco & Fase é pré-requisito da Fase 29 (Fundação Corporativa). A arquitetura agora opera em dois modos — **MMORPG (modo projeto)** e **Corporativo (Visagio/tickets)** — e o bloco precisa servir a ambos sem bifurcar o sistema.

Taxa de acerto do brainstorm: 11/11 questões decididas. Nenhuma revisão estrutural.

---

## 1. Decisões de Bloco

### 1.1 Dois arquivos por bloco — mantido

Manifest (`manifests/`) = contrato de planejamento, imutável após aprovação.
Retrospectiva (`blocks/`) = registro de resultado, append-only após fechamento.
Justificativa: parsers de audit, velocity, e analytics dependem dessa separação.

### 1.2 Tier → size + importance (dois campos independentes)

**Antes:** `tier: S | M | L` (critério único: quantidade de arquivos)

**Depois:**
```yaml
size: XS | S | M | L | XL        # tamanho técnico
importance: normal | critical     # impacto de negócio ou risco
```

**Definição de size:**
| size | arquivos mod/create | tempo estimado | quando usar |
|------|---------------------|----------------|-------------|
| XS | ≤ 2 | ≤ 1h | micro-fix, doc pontual |
| S | ≤ 4 | 2–4h | small fix, refactor simples |
| M | ≤ 8 | meio-dia | default — implementação típica |
| L | ≤ 12 | 1 dia | feature complexa, cross-module |
| XL | sem limite | multi-dia | feature completa, milestone |

**Definição de importance:**
| importance | quando usar |
|-----------|-------------|
| normal | caminho padrão — bug e features rotineiras |
| critical | toca auth/pagamento/produção/arquitetura; bug visível ao cliente; decisão sem volta |

Gates adicionais disparam quando `importance: critical` — **não** infla o size. Um bloco pode ser `size: XS, importance: critical` (micro-fix em prod).

### 1.3 Mode — herança da fase

O campo `mode` NÃO aparece no manifest do bloco. Ele é declarado na fase e herdado pelos blocos. O governor lê o mode da fase ao construir o task packet.

### 1.4 Campos corporativos — opcionais marcados, obrigatórios quando mode=corporate

Todos vivem no frontmatter do manifest, comentados por padrão:

```yaml
# [corporate — obrigatório quando mode=corporate]
# ticket_id: ~          # ID do Jira/Linear/texto livre
# acceptance_criteria: ~ # o que define done para o cliente/reviewer
# reviewer: ~           # quem vai revisar o PR
# client_id: ~          # herdado da fase — confirma contexto
```

O gate `corporate-fields` valida presença desses campos quando mode=corporate.

### 1.5 Sub-estados do bloco (wip_stage)

Bloco corporativo passa por três sub-etapas antes de `done`. Bloco MMORPG pode usar só `implementing`.

```
pending → wip (wip_stage: implementing) → wip (wip_stage: quality) → wip (wip_stage: teaching) → done
```

**Invariante de entrega:** bloco só vai para `done` quando o Piloto consegue explicar o que foi feito para superiores ou para o time. Se não consegue explicar, não está done — ainda está em `wip:teaching`.

```yaml
status: wip
wip_stage: implementing | quality | teaching    # preencher quando status=wip
```

### 1.6 Status — novo estado `paused`

```yaml
status: pending | wip | paused | done | failed | forced | reverted
paused_reason: ~    # preencher quando status=paused (ex: "ticket deprioritizado por cliente")
```

### 1.7 Kinds — adicionados `ticket` e `intake`

```yaml
kind: implementation | refactor | gate | ticket | intake
```

| kind | quando usar |
|------|-------------|
| implementation | MMORPG — implementação de feature/sistema |
| refactor | qualquer modo — refatoração sem mudança de comportamento |
| gate | qualquer modo — bloco de validação/verificação |
| ticket | corporativo — implementação de um ticket do cliente |
| intake | corporativo — lê o ticket, escaneia a área, **gera o manifest do bloco de ticket** |

**Flow intake → ticket:**
```
[texto do ticket] → intake block → [manifest de ticket gerado] → revisão do Piloto → ticket block
```
O intake é sempre `size: XS` e nunca modifica código do cliente — só lê e gera manifests.

### 1.8 Gates redesenhados

**Gates universais (ambos os modos):**
```yaml
- name: files-updated
  type: file-changed
  paths: [STATE.md, NEXT.md, BLOCK_LOG.md]
- name: scope-clean
  type: fmod-check      # valida que fmod_real ≤ fmod_declared no manifest
```

**Gates MMORPG (quando mode=mmorpg ou mode ausente):**
```yaml
- name: tests-pass
  cmd: <test_cmd>
  expect: "0 failed"
- name: lint-pass
  cmd: <lint_cmd>
  expect: "0 errors"
- name: build-pass
  cmd: <build_cmd>
  expect: "exit 0"
```

**Gates corporativos (quando mode=corporate):**
```yaml
- name: functionality-check
  type: manual
  checklist:
    - "O que o ticket pediu está funcionando conforme o acceptance_criteria?"
- name: consistency-check
  type: script
  cmd: python sdk/consistency_checker.py --profile governance/project-profile-<client_id>.md
  expect: "consistency_score >= 0.80"
- name: teach-ready
  type: manual
  checklist:
    - "Consigo explicar em 3 frases o que foi feito?"
    - "Consigo responder por que escolhi essa abordagem?"
    - "Consigo explicar o impacto para não-técnicos (gestor, cliente)?"
```

Gates são configuráveis por `project-profile` — se o cliente tem CI próprio, o `functionality-check` pode delegar ao CI deles.

### 1.9 Invariantes de bloco — imutáveis

Confirmados como verdade absoluta (Q11):

1. **Manifest precede trabalho** — nenhum bloco começa sem manifest aprovado (Axiom Q3)
2. **Toda mudança tem gate** — nenhum bloco fecha sem gates verificados
3. **Retrospectiva é obrigatória** — nenhum bloco `done` sem retro escrita

---

## 2. Decisões de Retrospectiva

### 2.1 Template unificado com seções por mode

Não há bifurcação. Um template, seções marcadas `[corporate]` são incluídas quando mode=corporate.

### 2.2 Novo campo de frontmatter

```yaml
wip_stage_reached: implementing | quality | teaching   # sub-etapa final antes de done
```

### 2.3 Novas seções obrigatórias (ambos os modos)

**Seção 9 — Decisions** (antes opcional, agora obrigatória):
```yaml
decisions:
  - "Escolhi X em vez de Y porque Z"
  - "Mantive o padrão de injeção de dependência do módulo de auth"
```
Permite auditar decisões arquiteturais sem ler o código. Com o tempo, ferramentas podem cruzar `decisions` com o resultado (foi uma boa decisão?) sem revisão manual de código.

**Seção 10 — Analytics** (ambos os modos):
```yaml
analytics:
  complexity_felt: 1 | 2 | 3 | 4 | 5    # subjetivo pós-bloco: 1=trivial, 5=muito complexo
  estimation_accuracy: on-track | over | under   # size estimado vs. tempo real
  blockers: []                           # o que travou (ex: "entender o padrão do cliente", "API mal documentada")
  rework_in_block: false                 # precisou refazer algo dentro do bloco?
  pattern_learned: []                    # padrões novos descobertos na codebase — alimenta project-profile
```

### 2.4 Novas seções [corporate]

**Seção 11 — Teach Summary** `[corporate]`:
```
Como explicar o que foi feito:
- Leigo: <1 frase sem jargão>
- Técnico: <1 frase com contexto de código>
- Time: <o que impacta o trabalho dos outros devs>
```

**Seção 12 — Consistency Score** `[corporate]`:
```yaml
consistency_score: 0.87    # saída do consistency_checker.py
divergences: []            # lista de divergências detectadas (se houver)
```

---

## 3. Decisões de Fase

### 3.1 Workday não tem documento

Workday = coleção de blocos agrupados por data. Não vira arquivo. Representado no STATE.md:
```
current_workday: 2026-06-02
```
Relatórios diários são gerados dos blocos fechados na data — sem doc extra.

### 3.2 Feature tem documento enxuto (5 seções)

```yaml
---
id: phase-<N>
mode: corporate | mmorpg | shared
type: feature                       # feature | workday (workday = sem doc)
client_id: ~                        # [corporate] — nome do cliente/projeto
status: planned | active | complete
created_at: YYYY-MM-DD
---
```

**5 seções obrigatórias:**
1. **Objetivo** — o que esta fase entrega (1 parágrafo)
2. **Tickets / Blocos** — lista de IDs incluídos
3. **Exit Criteria** — quando a fase está fechada
4. **Out of Scope** — o que não entra
5. **Block Index** — tabela de blocos com status

**Seções opcionais (mmorpg):** Dependencies, Risks, Parallel Execution Plan, Invariants

### 3.3 Retrospectiva de fase

Fase gera retrospectiva ao fechar — análoga à retro de bloco. Permite derivar: tickets/dia, tickets/semana, melhores dias, tendências de velocity. É o nível de dados de forecast do Piloto.

---

## 4. Arquivos a criar / atualizar

| Arquivo | Ação | Imutável? |
|---------|------|-----------|
| `design/block-phase-redesign.md` | ✅ Criado (este arquivo) | Não |
| `templates/manifest-small-v2.md` | ✅ Criado (rascunho) | Não (rascunho) |
| `templates/manifest-medium-v2.md` | ✅ Criado (rascunho) | Não (rascunho) |
| `templates/manifest-large-v2.md` | ✅ Criado (rascunho) | Não (rascunho) |
| `templates/manifest-intake.md` | ✅ Criado (novo) | Não |
| `templates/block-retrospective-v2.md` | ✅ Criado (rascunho) | Não (rascunho) |
| `templates/phase.md` | ✅ Atualizado (dual-mode) | Não |
| `templates/manifest-small.md` | ⏳ Swap pendente (bloco formal) | **Sim** |
| `templates/manifest-medium.md` | ⏳ Swap pendente (bloco formal) | **Sim** |
| `templates/manifest-large.md` | ⏳ Swap pendente (bloco formal) | **Sim** |
| `templates/block-retrospective.md` | ⏳ Swap pendente (bloco formal) | **Sim** |

**Swap formal:** Os templates imutáveis precisam de um bloco de execução (`kind: refactor`, `security: false`) que use `proposal_apply` com confirmação do Piloto. Esse bloco deve ser criado na Fase 29 após aprovação do design.

---

## 5. O que NÃO muda

- A separação manifest/retrospectiva em duas pastas
- O formato de frontmatter YAML delimitado por `---`
- Os axioms de qualidade (Q1, Q2, Q3, etc.) referenciados nos manifests
- O mecanismo de gates (nome + cmd + expect)
- O BLOCK_LOG.md como registro oficial de blocos fechados
- Os 3 invariantes de bloco (§1.9)

---

*Gerado por brainstorm-pattern-v2.md. Todos os campos foram decididos pelo Piloto — nenhuma decisão foi tomada autonomamente pela IA.*
