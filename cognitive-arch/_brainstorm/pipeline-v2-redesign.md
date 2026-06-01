# Brainstorm: Pipeline + Consistência — Design Decisions

status: draft
created_at: 2026-05-31
author: AI (design session)
synthesis_target: design/pipeline.md
topic: design do pipeline de trabalho corporativo — consistency checker, review pipeline, teach mode, HTML por etapa

---

## Context

Phase 31 implementa o núcleo operacional do modo corporativo: o pipeline completo de trabalho.
Se o Scanner (Phase 30) é a fundação do conhecimento, o Pipeline é a máquina de entrega.
Cada ticket passa por cinco etapas, produz um HTML por etapa, e só é entregue quando o Piloto
valida. O design de alto nível está aprovado em `design/corporate-mode.md §3.3`.

**Por que brainstorm:** o design define o fluxo e os componentes. O que falta são as decisões
de implementação: regras exatas do checker, thresholds, comportamento do ciclo de qualidade,
formato dos HTMLs das etapas novas (Qualidade e Teach), e granularidade do on/off dial.

---

## O que já está decidido (não são perguntas abertas)

| Decisão | Resolução |
|---------|-----------|
| Estrutura do pipeline | `TICKET → Intake → Scan L2/L3 → Implementar ↔ Qualidade (ciclo) → Teach → ENTREGA` |
| Ciclo implementar↔qualidade | Não é esteira reta — Qualidade detecta discrepância → reabre Implementar |
| Go/no-go | Piloto SEMPRE — IA detecta problemas, Piloto decide se entrega |
| Consistency checker — escopo | Estrutural apenas: naming, organização de arquivos, imports, estilo por linguagem. Sem lógica de negócio. |
| Teach mode — trigger base | Obrigatório para linguagens/frameworks novos; opcional para áreas já conhecidas |
| HTML por etapa | Cada etapa do pipeline tem HTML próprio — produzido e validado antes de avançar |
| Liga/desliga HTML | Usuário pode desligar (confirmado em scanner; vale para todo o pipeline) |
| Big-O no HTML de qualidade | Incluído — "reporte de complexidade de algoritmo (Big-O)" está no design §3.6 |

---

## Core model

### Fluxo atual (sem pipeline)
```
Piloto recebe ticket → implementa manualmente → entrega sem revisão estruturada
→ senior encontra inconsistência → retrabalho → frustração
```

### Fluxo-alvo (com pipeline)
```
[Intake]   ticket → manifest de bloco corporativo (block-165, já implementado)
   ↓
[Scan]     scanner L2/L3 na área do ticket → perfil atualizado, HTML (phase-30, já implementado)
   ↓
[Implementar]  código gerado no padrão do projeto → HTML (opcional por etapa)
   ↓
[Qualidade]    consistency checker + testes + Big-O → HTML de qualidade → Piloto valida
   ↑ ← discrepância detectada? retorna aqui
[Teach]        teach mode → explicação multi-nível → HTML de teach → Piloto valida
   ↓
[ENTREGA]      PR ou código pronto para revisão do senior
```

Propriedades do modelo-alvo:
- Cada etapa produz HTML independente — Piloto pode validar ou pular
- O ciclo Implementar↔Qualidade é o mecanismo de auto-correção antes da entrega
- Teach não é documentação para o senior — é o Piloto confirmando que entende o que fez
- Nenhuma etapa avança automaticamente sem validação do Piloto

---

## Decision 1 — Consistency checker: exatamente o que verifica?

**Problema:** O design diz "estrutural apenas — naming, organização de arquivos, imports, estilo".
Mas isso pode ser muito superficial (só verifica nomes de variáveis) ou muito profundo (verifica
toda a arquitetura de módulos). Qual é o escopo exato para uma v1 útil?

### Option A — Mínimo: só naming e imports
- Verifica: convenção de nomes (camelCase vs. snake_case, PascalCase para classes, etc.)
- Verifica: estilo de imports (default vs. named, ordem, agrupamento)
- Não verifica: onde os arquivos ficam, como os módulos se conectam
- Custo: baixo — análise de texto simples
- Risco: miss na estrutura de pastas, que é onde mais se diverge

### Option B — Standard: naming + imports + organização de arquivos *(recommended)*
- Tudo do Option A +
- Onde novos arquivos foram criados vs. onde o projeto cria arquivos do mesmo tipo
- Naming de arquivos (ex: `UserController.ts` vs. `user-controller.ts` vs. `user.controller.ts`)
- Não verifica: padrões de design dentro dos arquivos (como as funções são organizadas internamente)
- Cobre os erros mais visíveis para um senior revisando um PR

### Option C — Extended: naming + imports + organização + estilo interno
- Tudo do Option B +
- Como funções são organizadas dentro de um arquivo (ex: public methods first)
- Como dependências são injetadas (constructor injection vs. property injection)
- Padrões de comentário e docstrings
- Alto custo de manutenção — mais regras = mais falsos positivos

**Recommendation: Option B (Standard).** Naming + imports + organização de arquivos cobre
o que um senior nota imediatamente num PR. O checker não precisa ser perfeito na v1 — precisa
ser útil. Falsos negativos (checker passa algo errado) são aceitáveis; falsos positivos
(checker bloqueia código correto) destroem a confiança.

---

## Decision 2 — Consistency threshold: score mínimo configurável ou fixo?

**Problema:** O checker retorna um score (0.0–1.0). Mas qual score mínimo para o gate passar?
Se fixo, pode ser muito rígido ou muito frouxo para diferentes projetos. Se configurável, precisa
de setup por projeto.

### Option A — Fixo em 0.80
- Gate passa se `consistency_score >= 0.80`
- Simples, sem configuração necessária
- Pode ser inadequado para projetos com code style muito estritos (0.90+) ou muito relaxados

### Option B — Configurável em `project-profile-<cliente>.md` *(recommended)*
- Threshold declarado no perfil do projeto: `consistency_threshold: 0.80`
- Default: 0.80 se não declarado
- Piloto pode ajustar por cliente conforme aprende o nível de exigência do time
- Permite subir progressivamente (começar em 0.70, subir para 0.85 ao ganhar confiança)

### Option C — Configurável + aviso sem bloqueio abaixo do threshold
- Threshold é aviso, não bloqueio
- Checker sempre passa, mas gera aviso se abaixo do threshold
- Go/no-go final fica totalmente com o Piloto (sem gate automático)
- Mais permissivo, mas perde o mecanismo de auto-correção do ciclo

**Recommendation: Option B.** Threshold no project-profile alinha com a filosofia de que o
perfil concentra as preferências do projeto. Default 0.80 é um bom ponto de partida.
O ciclo implementar↔qualidade já existe para lidar com falhas — o threshold bloquear tem valor:
força o Piloto a conscientemente override quando sabe que a divergência é intencional.

---

## Decision 3 — HTML de qualidade: o que mostra além do consistency check?

**Problema:** O design §3.6 define: "testes, consistência, e reporte de complexidade de algoritmo
(Big-O)". Mas qual é o nível de detalhe de cada item? O que é obrigatório vs. opcional?

### Option A — Mínimo: só consistency score + lista de divergências
- O que o checker retorna, formatado visualmente
- Passa/falha por regra, com exemplos de onde divergiu
- Não inclui testes ou Big-O
- Rápido de gerar; pouco informativo para o Piloto

### Option B — Standard: consistency + testes + Big-O *(recommended)*
- **Consistency score:** breakdown por categoria (naming, imports, organização)
- **Testes:** cobertura da área modificada (quais funções têm teste, quais não têm)
- **Big-O:** análise de complexidade das funções criadas/modificadas — "esta função é O(n²), função de referência do projeto é O(n log n)"
- Big-O é o "detalhe que eleva a qualidade percebida" — design §3.2
- Seções opcionais configuráveis via `ux-config.yaml`

### Option C — Full: tudo do Standard + sugestões proativas
- Tudo do Standard +
- Sugestões de refatoração (funções muito longas, duplicação detectada)
- Links para arquivos de referência no projeto com o padrão correto
- Mais rico, mais tempo de geração, mais difícil de consumir rapidamente

**Recommendation: Option B (Standard).** Big-O é o diferencial real — poucos devs o fazem
naturalmente, e é exatamente o tipo de detalhe que impressiona seniors. Consistency + testes +
Big-O numa view única dá ao Piloto tudo que precisa para decidir se entrega ou volta a implementar.
Sugestões proativas (Option C) ficam para evolução futura.

---

## Decision 4 — Teach mode HTML: dial de abstração ou 3 níveis fixos?

**Problema:** O design original define 3 níveis fixos: técnico (PR description), equipe
(standup/sync), aprendizado (entender o que foi feito). O design §3.6 propõe um "dial de
abstração" (leigo · iniciante · técnico) que atravessa todo o sistema. Qual implementar na v1?

### Option A — 3 níveis fixos: técnico · equipe · aprendizado
- Implementação simples e direta
- Alinhado com o design original de corporate-mode.md §3.3
- Sem configuração adicional
- Menos flexível para o futuro

### Option B — Dial de abstração configurável: leigo · iniciante · técnico *(recommended)*
- Dialeto vai além do Teach — atravessa scan, qualidade e teach
- Configurável: `abstraction_level: leigo | iniciante | tecnico` em `ux-config.yaml`
- Leigo: sem jargão, metáforas visuais, foco no impacto
- Técnico: detalhes de implementação, decisões arquiteturais, trade-offs
- Iniciante: meio-termo — entende código mas não o contexto do projeto
- Isso é o que torna a arquitetura "vendável/ensinável a terceiros" (design §3.6)

### Option C — Ambos: 3 níveis fixos no Teach + dial global separado
- Teach mantém técnico/equipe/aprendizado por semântica corporativa
- Dial leigo/iniciante/técnico é feature separada aplicada ao scan + qualidade
- Evita conflito de nomenclatura, mais complexo de manter dois sistemas

**Recommendation: Option B.** O dial de abstração é mais geral e serve melhor ao objetivo
de longo prazo (teachability, terceiros, o "Big Dev"). Os 3 níveis do design original são
um caso especial do dial — técnico/equipe/leigo mapeia diretamente para técnico/iniciante/leigo.
Implementar o dial agora evita refatoração futura.

---

## Decision 5 — On/off dial: global ou por etapa?

**Problema:** O usuario pode desligar o HTML. Mas o pipeline tem 3 etapas com HTML (Qualidade,
Teach, e opcionalmente Implementar). Desligar tudo de uma vez ou por etapa?

### Option A — Toggle global: desliga todos os HTMLs do pipeline de uma vez
- Um campo em `ux-config.yaml`: `pipeline_html: true/false`
- Simples, mas sem granularidade
- Se o Piloto quer só o HTML de qualidade e não o de teach, não tem como

### Option B — Toggle por etapa *(recommended)*
```yaml
# ux-config.yaml
html_output:
  scanner: true
  pipeline_quality: true
  pipeline_teach: true
  pipeline_implement: false   # opcional — default off
```
- Cada etapa controlável independentemente
- `pipeline_implement` é false por default (implementar não tem HTML fixo no design)
- Piloto pode desligar só o teach se já conhece bem a área

### Option C — Toggle por etapa + CLI override pontual
- Tudo do Option B +
- Flags `--no-html-quality`, `--no-html-teach` para desligar em execuções específicas
- Mais granular, mais flags na CLI

**Recommendation: Option B.** Por etapa sem flags CLI adicionais. O `ux-config.yaml` já existe
como ponto de configuração; adicionar sub-campos por etapa é natural. Flags CLI adicionais
(Option C) adicionam ruído na interface — o ux-config.yaml cobre o caso de uso.

---

## Decision 6 — Ciclo implementar↔qualidade: quem inicia o retorno?

**Problema:** Quando a etapa de Qualidade detecta discrepâncias, o ticket "volta" para
Implementar. Mas como isso acontece mecanicamente? Automático ou manual?

### Option A — Automático: qualidade fecha direto e reabre Implementar se falhar
- Checker detecta falha → automaticamente marca o bloco como `wip_stage: implementing`
- Piloto não precisa fazer nada para iniciar o ciclo
- Risco: o Piloto pode querer entregar mesmo com falha (override intencional)

### Option B — Manual: qualidade apresenta resultado, Piloto decide *(recommended)*
```
[Qualidade HTML gerado]
>>> Score de consistência: 0.72 (abaixo de 0.80)
>>> Opções:
>>> [A] Retornar para Implementar e corrigir
>>> [B] Entregar mesmo assim (override) — registra razão
>>> [C] Pedir revisão manual do Piloto antes de decidir
>>> Sua escolha:
```
- Piloto mantém controle total (padrão do design: "Piloto sempre dá go/no-go")
- Override é documentado no manifest (`gate_override_reason`)
- Nenhum ciclo acontece sem decisão explícita

### Option C — Automático com veto: qualidade reabre automaticamente mas Piloto pode vetar
- Ciclo começa automaticamente em falha
- Piloto pode interromper o ciclo com comando explícito
- Inversão do Option B: default é ciclar, o Piloto para se quiser

**Recommendation: Option B (Manual).** O design é explícito: "go/no-go é do Piloto, sempre."
Automatizar o ciclo (mesmo com veto) viola esse princípio. Option B é o único que mantém o
Piloto como decisor central em cada transição. O custo de um prompt adicional é mínimo
comparado ao valor de ter visibilidade total do fluxo.

---

## Decision 7 — Teach mode: quando é obrigatório?

**Problema:** O design diz "obrigatório para linguagens/frameworks novos para o Piloto; opcional
para áreas já conhecidas." Mas quem decide o que é "novo"? E no modo corporativo, onde tudo pode
ser novo no início, quando relaxar?

### Option A — Piloto configura sempre manualmente
- Flag `--teach` ou `--no-teach` em cada execução
- Zero automação — máximo controle, máxima fricção
- Funciona mas não escala (o Piloto vai esquecer de ativar quando seria útil)

### Option B — Baseado no project-profile: novo se não está no perfil *(recommended)*
- Scanner L3 extrai linguagens e frameworks do projeto
- `project-profile` rastreia: `pilot_known: [TypeScript, React, Prisma, ...]`
- Se o ticket toca um framework não na lista `pilot_known` → teach obrigatório
- Piloto atualiza `pilot_known` quando domina a tecnologia
- Opção adicional: `teach_always: true` no `ux-config.yaml` para quem quer sempre

### Option C — Obrigatório sempre no primeiro ticket de cada projeto
- Primeiro ticket de um projeto → teach obrigatório (o Piloto está aprendendo o contexto)
- Tickets subsequentes → opcional
- Simples, mas ignora o nível real de conhecimento do Piloto

**Recommendation: Option B.** Usar o project-profile como fonte da verdade é elegante —
já coletamos `domain_entities` e o stack, só precisamos adicionar `pilot_known` como campo
editável. Isso integra o teach mode com o scanner sem inventar novo mecanismo.

---

## Open questions (não decididas aqui)

1. **Integração Jira/Linear:** o pipeline lê tickets de texto livre. A integração com APIs
   externas está fora de escopo, mas o formato interno deve ser compatível para evolução futura.
   Proposta: campo `ticket_source: jira | linear | free_text` no manifest de intake.

2. **Paralelismo de tickets no pipeline:** o design §3.4 menciona escalada para 2→3 tickets
   simultâneos. Isso é Phase 32 (forecast + paralelismo) — não Phase 31. Registrado aqui para
   não perder.

3. **Histórico de qualidade por projeto:** o checker gera scores por ticket. Agregar esses
   scores ao longo do tempo cria um "quality trend" do Piloto naquele projeto. Feature natural
   para Phase 32 (velocity + forecast).

4. **Formato do HTML de Implementar:** o design §6B diz "Implementar provavelmente dispensa HTML
   próprio (o PR/código já é isso), mas opcional." Confirmado como opcional — não há decisão
   pendente aqui.

---

## Confirmed decisions (Piloto 2026-05-31)

| # | Decisão | Escolha | Nota |
|---|---------|---------|------|
| 1 | Consistency checker — escopo | **B+C, C toggleável** | B=padrão; C (estilo interno) liga/desliga via ux-config. Falsos positivos gerenciados pelo toggle. |
| 2 | Consistency threshold | **B+ dinâmico** | Base: configurável no project-profile (default 0.80). Threshold ajusta automaticamente pela média dos últimos N blocos. Sobe sozinho se tendência alta; cai requer aprovação do Piloto + análise. |
| 3 | HTML de qualidade — conteúdo | **B+C, C toggleável + export textual** | B=padrão (consistency+testes+Big-O); C=proactive suggestions toggleável. Export de texto puro para copy-paste (Slack, TikTok, etc.). |
| 4 | Teach mode HTML | **Ambos: dial global + 3 HTMLs por audiência** | Dial abstração (leigo/iniciante/técnico) = setting global persistente. 3 HTMLs (técnico/equipe/aprendizado) = toggleáveis individualmente. |
| 5 | On/off dial | **B — por etapa, todos default ON** | Piloto descobre o que é inútil e desliga. Implement HTML também começa ligado. |
| 6 | Ciclo qualidade→implementar | **B — manual, Piloto decide sempre** | "Às vezes falhou no checker mas o código está ótimo." Piloto tem controle total. |
| 7 | Teach mode trigger | **Sempre obrigatório em todo ticket** | Não é condicional por linguagem — é obrigatório antes de fechar qualquer bloco de ticket. É o ponto de revisão final. Pode loopback para implementar se Piloto detectar problema. Ad-hoc também permitido fora do pipeline. HTML do L0 do scanner é o "teach do projeto" — teach mode aqui é o "teach do ticket". |

## Recommended synthesis

Após confirmação, gerar:
- `design/pipeline.md` — design doc completo do pipeline
- `phases/phase-31.md` — fase com blocos (a partir de block-170)
- Manifests dos blocos

End of brainstorm.
