# Design: Pipeline de Trabalho Corporativo

status: approved
created_at: 2026-05-31
authors: Thaillon (Piloto) + AI (brainstorm session 2026-05-31)
synthesis_source: `_brainstorm/pipeline-v2-redesign.md` (all 7 decisions confirmed 2026-05-31)
phase: phase-31

---

## 0. O que é o Pipeline

O pipeline é a **máquina de entrega corporativa**. Se o Scanner fornece o conhecimento do
projeto, o Pipeline garante que cada ticket seja entregue com qualidade máxima e que o Piloto
entenda completamente o que fez antes de submeter.

**Fluxo completo:**
```
TICKET → [Intake] → [Scan L2/L3] → [Implementar] ↔ [Qualidade] → [Teach] → ENTREGA
```

O ciclo `Implementar ↔ Qualidade` não é uma esteira reta — é um loop controlado pelo Piloto.
O Teach é o ponto de revisão final: o Piloto só entrega quando consegue explicar o que fez.

---

## 1. Etapa: Consistency Checker

### Escopo — B+C com C toggleável

**Nível B (padrão, sempre ativo):**
- Naming conventions (camelCase/PascalCase/snake_case por contexto)
- Estilo de imports (default vs. named, ordem, agrupamento)
- Organização de arquivos (onde novos arquivos foram criados vs. onde o projeto cria arquivos do mesmo tipo)
- Naming de arquivos (ex: `UserController.ts` vs. `user-controller.ts`)

**Nível C (toggleável via `ux-config.yaml`):**
- Organização interna dos arquivos (public methods first, funções agrupadas por responsabilidade)
- Estilo de injeção de dependências
- Padrões de comentário e docstrings
- C gera mais falsos positivos — o toggle existe exatamente para gerenciar isso. Piloto ativa quando quer consistência máxima, desativa quando o projeto é mais relaxado.

**Output:** score numérico (0.0–1.0) + lista de divergências por categoria + HTML visual

### Threshold — dinâmico, baseado em dados

**Configuração base:** `consistency_threshold: 0.80` em `project-profile-<cliente>.md` (default se ausente)

**Dinâmica:**
- O threshold é recalculado automaticamente baseado na média dos últimos N blocos do cliente
- **Tendência de alta** (scores subindo): threshold sobe sozinho — o projeto naturalmente fica mais exigente
- **Tendência de baixa** (scores caindo): threshold NÃO cai automaticamente — Piloto deve aprovar o ajuste e entender o porquê
- Isso garante que a qualidade sempre sobe ou fica estável por decisão explícita, nunca cai por acidente

**Configuração:**
```yaml
# governance/project-profile-<cliente>.md
consistency_threshold: 0.80           # baseline inicial
threshold_dynamic: true               # habilita ajuste automático
threshold_lookback_blocks: 5          # média dos últimos N blocos
threshold_auto_raise: true            # sobe sozinho
threshold_auto_lower: false           # NUNCA baixa sem aprovação do Piloto
```

### Export textual

Além do HTML, o checker gera um relatório em texto puro (markdown simples) para copy-paste:
- Slack: `:white_check_mark: Consistency 0.87 — 2 divergências em naming`
- Reunião: bullet points para apresentar verbalmente
- Configurável por audiência (tech-brief / team-brief)

---

## 2. Etapa: Review Pipeline + Qualidade

### HTML de qualidade — B+C, C toggleável

**Nível B (padrão):**
- Consistency score breakdown por categoria
- Cobertura de testes da área modificada (quais funções têm teste, quais não têm)
- Big-O das funções criadas/modificadas ("esta função é O(n²); referência do projeto é O(n log n)")

**Nível C (toggleável):**
- Sugestões proativas de refatoração (funções longas, duplicação, código morto)
- Links para arquivos de referência no projeto com o padrão correto

**Export textual** (igual ao checker): texto puro para copy-paste, formatado por audiência.

### Ciclo implementar↔qualidade — manual

```
[Qualidade HTML gerado]
>>> Consistency score: 0.72 (abaixo do threshold 0.80)
>>> 3 divergências: naming (2), organização de imports (1)
>>>
>>> [A] Retornar para Implementar — corrigir divergências
>>> [B] Entregar mesmo assim — registrar motivo
>>> [C] Ver detalhes antes de decidir
>>> Sua escolha:
```

**Regras do ciclo:**
- Nenhuma transição automática — Piloto decide em cada iteração
- Override (Option B) registra `gate_override_reason` no manifest
- Sem limite de iterações — o Piloto pode ciclar quantas vezes precisar

---

## 3. Etapa: Teach Mode

### Obrigatoriedade — sempre, em todo ticket

Teach mode NÃO é condicional. Todo ticket passa pelo teach antes de fechar.

**Por quê sempre:** o teach é o ponto de revisão final — quando o Piloto explica o código,
ele enxerga coisas que não viu durante a implementação. Isso pode gerar um loopback para
implementar. É também o que garante que o Piloto consegue explicar o que fez para superiores
ou para o time — condição do `wip_stage: teaching` definida na Phase 29.

**Nota sobre o scanner:** o HTML do L0 do scanner é o "teach do projeto" (entender a codebase
completa). O teach mode aqui é especificamente o "teach do ticket" — o que foi feito, por que,
e como.

### Dois sistemas de apresentação

**Sistema 1 — Dial de abstração (setting global persistente):**
```yaml
# governance/ux-config.yaml
abstraction_level: leigo | iniciante | tecnico   # default: tecnico
```
- Afeta como a IA fala em TODAS as etapas (scan, qualidade, teach)
- Leigo: sem jargão, metáforas visuais, foco no impacto
- Iniciante: entende código mas não o contexto do projeto
- Técnico: decisões arquiteturais, trade-offs, detalhes de implementação

**Sistema 2 — 3 HTMLs por audiência (toggleáveis individualmente):**
```yaml
# governance/ux-config.yaml
teach_html:
  technical: true     # PR description — para o senior
  team: true          # standup/reunião — para o time
  learning: true      # revisão pessoal — para o próprio Piloto
```
- Cada HTML tem seu foco: technical para o PR, team para reuniões, learning para o Piloto
- Todos default ON — Piloto desliga o que não usa
- Export textual disponível em cada nível para copy-paste (Slack, apresentações)

### Loopback para implementar

O teach pode gerar um retorno para implementar:
```
[Teach HTML gerado — nível: learning]
>>> Enquanto você revisava, identificou algo a corrigir?
>>> [A] Não — código está bom, avançar para entrega
>>> [B] Sim — retornar para Implementar com nota do que corrigir
```

### Ad-hoc (fora do pipeline)

O Piloto pode chamar o teach mode a qualquer momento, fora do fluxo de ticket:
```
python sdk/teach_mode.py --block-id block-XXX --level learning --arch-root .
```

---

## 4. On/Off por etapa — todos default ON

```yaml
# governance/ux-config.yaml
html_output:
  scanner_l0: true
  scanner_partial: true
  pipeline_implement: true      # começará ligado; Piloto decide se é útil
  pipeline_quality_b: true      # consistency + testes + Big-O
  pipeline_quality_c: false     # sugestões proativas — default OFF (falsos positivos)
  pipeline_teach_technical: true
  pipeline_teach_team: true
  pipeline_teach_learning: true
consistency_checker:
  level_b: true                 # naming + imports + organização
  level_c: false                # estilo interno — default OFF
```

**Filosofia:** tudo começa ON. Piloto descobre o que não está servindo e desliga. Não força
o Piloto a configurar antes de ver o valor.

---

## 5. Módulos a implementar (Phase 31)

| Módulo | Função |
|--------|--------|
| `sdk/consistency_checker.py` | B+C checker, threshold dinâmico, score, export textual |
| `sdk/review_pipeline.py` | Orquestra ciclo implementar↔qualidade, gera HTML de qualidade, prompt manual |
| `sdk/teach_mode.py` | Sempre obrigatório, dial de abstração, 3 HTMLs, export textual, loopback flag |

---

## 6. Integração com módulos existentes

| Módulo | Integração |
|--------|-----------|
| `scanner_profile.py` | Checker lê seções L3/L4 do project-profile como fonte de padrões |
| `ux-config.yaml` | Todos os toggles de HTML e checker residem aqui |
| `block_close.py` (phase-29) | Verificar `wip_stage: teaching` antes de `done` — não fecha sem teach |
| `ticket_intake.py` (phase-29) | Intake gera o manifest; pipeline assume a partir daí |

---

## 7. Histórico de qualidade (dados para Phase 32)

O checker registra `consistency_score` por bloco no manifest (campo `consistency_score`
na retrospectiva, definido em `design/block-phase-redesign.md §2.2`). Esses dados alimentam:
- O threshold dinâmico (media dos últimos N blocos)
- O velocity e forecast de qualidade do Piloto (Phase 32)

---

## 8. Out of Scope

- Integração com Jira/Linear API (Piloto faz copy-paste do ticket por enquanto)
- Paralelismo de tickets (Phase 32)
- Auto-geração de PRs no repo da empresa
- Análise de lógica de negócio no checker (só estrutural)

---

*Brainstorm: `_brainstorm/pipeline-v2-redesign.md`*
*Fase: `phases/phase-31.md`*
*Revisado em: 2026-05-31*
