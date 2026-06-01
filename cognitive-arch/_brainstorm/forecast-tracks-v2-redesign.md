# Brainstorm: Forecast, Calendário & Tracks — Design Decisions

status: draft
created_at: 2026-05-31
author: AI (design session)
synthesis_target: design/forecast-tracks.md
topic: velocity de tickets, forecast de entrega, escalada de paralelismo, alertas de reunião, sistema de tracks

---

## Context

Phase 32 fecha o loop do modo corporativo: depois de entregar tickets com qualidade (Phases 29–31),
o Piloto passa a medir e prever. Velocity real de entrega, forecast de quando vai terminar,
capacidade de paralelismo, e alertas de reunião com estimativa de impacto. Mais o sistema de
tracks que mantém os módulos críticos da arquitetura em melhoria contínua.

O design de alto nível está em `design/corporate-mode.md §3.4` e `§7C`. Os módulos de velocity
e forecast JÁ EXISTEM no SDK (`velocity_inference.py`, `phase_forecast.py`) — estão só orientados
ao projeto (MMORPG). Aqui eles são reorientados ao Piloto.

---

## O que já está decidido (não são perguntas abertas)

| Decisão | Resolução |
|---------|-----------|
| Métrica de velocity | Tempo real por bloco → ritmo em tickets/hora, tickets/dia, tickets/semana |
| Forecast output base | "Nesse ritmo, você entrega N tickets até [data]" |
| Escalada de paralelismo | 1→2→3 tickets simultâneos; subir até achar o gargalo humano |
| Gargalo humano | O limite é a parte humana do Piloto (revisão, go/no-go, teach) — não da máquina |
| Tracks benchmark | Qualidade/robustez/consistência (ex: taxa de retrabalho, cobertura) — não latência em ms |
| Tracks existentes | 13 tracks já existem no SDK (`tracks/PRIORITY.md`, templates) — precisam de adaptação |
| Reuso de módulos | `velocity_inference.py` e `phase_forecast.py` existentes são reorientados, não reescritos |

---

## Core model

### Situação atual (sem forecast)
```
Piloto entrega tickets → não sabe quantos entregou → não sabe se vai conseguir entregar no prazo
→ chega numa reunião sem saber o status → surpresa na sexta quando há 3 tickets abertos
```

### Modelo-alvo (com forecast)
```
Piloto entrega tickets → velocity coletada automaticamente
→ forecast: "nesse ritmo, entrega 4 tickets até sexta"
→ reunião cadastrada → alerta: "você tem reunião amanhã — 2h de capacidade perdida"
→ paralelo: "você está pronto para 2 tickets simultâneos"
→ tracks monitorando os módulos críticos → alertas quando algo degrada
```

---

## Decision 1 — Velocity: como medir o tempo real de cada ticket?

**Problema:** `velocity_inference.py` existe mas nunca teve dados reais (`actual_duration_hours`
nunca foi preenchido em 85+ blocos — confirmado no health report de 2026-05-23). O problema não
é o módulo, é como o dado entra. Como capturar o tempo real sem fricção?

### Option A — Input manual pelo Piloto no block-close
- Piloto informa ao fechar: "quanto tempo levou este ticket?"
- Simples, sem automação
- Histórico: o campo existe, ninguém preenche. Fricção real.

### Option B — Timestamps automáticos (block_start / block_close) *(recommended)*
- `block_start.py` registra `started_at: <ISO timestamp>` no manifest ao iniciar
- `block_close.py` registra `finished_at: <ISO timestamp>` ao fechar
- `velocity_inference.py` calcula `actual_duration = finished_at - started_at`
- Zero input manual — o dado existe no manifest depois de qualquer bloco fechado
- Complementar: campo opcional `paused_duration_hours` para descontar pausas longas

### Option C — Estimativa por proxy (linhas de código + arquivos modificados)
- Velocity estimada por volume de mudança, não tempo
- Sem dependência de timestamps
- Impreciso — um bloco de 30min que toca 10 arquivos vs. um de 4h que toca 2 arquivos

**Recommendation: Option B.** Timestamp automático é zero fricção e captura o dado real.
O campo `started_at` em manifests existentes não existe — adicionar é mudança simples em
`block_start.py` (já modificado na Phase 29 para suportar `wip_stage`). O campo `paused_duration_hours`
opcional resolve pausas longas sem obrigar o Piloto a nada.

---

## Decision 2 — Forecast: o que exatamente o Piloto vê?

**Problema:** "Nesse ritmo, entrega N tickets até [data]" é o ponto de partida. Mas qual é o
formato completo do forecast? Só texto? Dashboard? Considera reuniões e feriados?

### Option A — Texto simples no terminal
```
>>> Velocity atual: 2.3 tickets/dia (média últimos 5 blocos)
>>> Tickets abertos: 7
>>> Estimativa: entrega os 7 em ~3 dias úteis (sexta, 06/06)
```
- Rápido de implementar, fácil de ler
- Sem visualização, sem granularidade

### Option B — HTML de forecast com múltiplos sinais *(recommended)*
```
Velocity: 2.3 tickets/dia  |  Paralelo: 1 ticket (recomendado: 2)
Estimativa de entrega: 3 dias úteis
Reuniões impactando: 1 reunião amanhã (2h)
Estimativa ajustada: 3.5 dias úteis
Confidence: médio (5 blocos de histórico)
```
- HTML pequeno — "do tamanho do que precisa dizer"
- Inclui impacto de reuniões cadastradas
- Inclui recomendação de paralelismo
- Confidence band baseado na quantidade de histórico disponível

### Option C — Integração com calendário externo (Google Calendar, Outlook)
- Forecast lê o calendário real do Piloto automaticamente
- Alto valor, alta complexidade de integração
- Autenticação OAuth, dependência externa, possível problema de privacidade

**Recommendation: Option B.** HTML de forecast com os sinais certos. Reuniões via input manual
(Decision 3 resolve como). Confidence band é crítico: com 3 tickets de histórico, o forecast
é uma estimativa; com 20, é confiável. O Piloto precisa saber a diferença.

---

## Decision 3 — Calendário: como o sistema sabe das reuniões do Piloto?

**Problema:** Para ajustar o forecast, o sistema precisa saber quando há reuniões (capacidade
reduzida). Mas integração com calendário externo é complexa. Como capturar isso sem fricção?

### Option A — Input manual: Piloto informa reuniões via CLI
```
python sdk/calendar_manager.py --add-meeting "2026-06-02 14:00 2h" --desc "sync com equipe"
```
- Simples, sem dependência externa
- Piloto tem controle total
- Fricção: precisa lembrar de cadastrar toda reunião

### Option B — Arquivo de calendário local (YAML) *(recommended)*
```yaml
# governance/pilot-calendar.yaml
meetings:
  - date: 2026-06-02
    time: "14:00"
    duration_hours: 2
    desc: "sync semanal com o time"
  - date: 2026-06-03
    time: "10:00"
    duration_hours: 1
    desc: "1:1 com senior"
```
- Piloto edita o arquivo diretamente (ou via CLI helper)
- Forecast lê o arquivo e desconta a capacidade das reuniões nos dias relevantes
- Zero dependência externa; portável; auditável

### Option C — Integração com Google Calendar / Outlook API
- Lê eventos automaticamente do calendário real
- Máxima precisão sem input manual
- OAuth + escopo de leitura de calendário = complexidade + privacidade

**Recommendation: Option B.** Arquivo YAML local é o padrão da arquitetura (tudo é local,
tudo é auditável). A CLI helper para adicionar reuniões (`--add-meeting`) reduz a fricção
de editar YAML diretamente. Option C é a evolução natural quando a arquitetura estiver madura
e a complexidade for justificada pelo volume de reuniões.

---

## Decision 4 — Alerta de reunião: quando e como o Piloto é avisado?

**Problema:** O Piloto tem uma reunião amanhã às 14h. Quando e como deve ser alertado?
O alerta deve conter o impacto no forecast?

### Option A — Alerta no session_start.py (toda sessão)
- Ao iniciar a sessão, `session_start.py` verifica o calendário e exibe reuniões próximas
- "Você tem reunião amanhã às 14h (2h). Capacidade do dia: 6h → 4h"
- Zero interrupção durante o trabalho

### Option B — Alerta proativo + integrado ao forecast *(recommended)*
- `session_start.py` exibe alerta de reuniões em 24–48h
- Forecast já incorpora o impacto automaticamente (estimativa ajustada inclui reuniões)
- Se reunião for hoje: alerta no início da sessão + no forecast atual
- "⚠️ Reunião hoje às 14h (2h). Forecast ajustado: entrega em 4 dias em vez de 3.5"

### Option C — Notificação push (fora da sessão)
- Alerta enviado por email/Slack antes da reunião
- Complexidade de integração + dependência de serviço externo
- A arquitetura opera local-first — notificação push é uma exceção

**Recommendation: Option B.** Alerta em `session_start.py` é o ponto de atenção natural —
o Piloto já lê o briefing ao começar. O impacto integrado no forecast fecha o loop: não é
só "você tem reunião" mas "e por isso o prazo muda X". Simple, local, sem dependência externa.

---

## Decision 5 — Escalada de paralelismo: como o sistema sabe que o Piloto está pronto para mais tickets?

**Problema:** O design define escalada 1→2→3 tickets, "subindo até achar o gargalo humano".
Mas quem decide quando subir? E o que mede o gargalo?

### Option A — Piloto decide manualmente quando escalar
- Sistema não sugere nada — Piloto escolhe rodar 2 tickets quando quiser
- Zero automação; máximo controle
- Sem feedback de onde está o gargalo

### Option B — Sistema sugere baseado em métricas de qualidade *(recommended)*
O sistema recomenda subir quando:
- Últimos N blocos fecharam sem quality loopback (qualidade passou na primeira)
- Teach mode sem loopback to implement (Piloto entendeu na primeira)
- Consistency score ≥ threshold nos últimos N blocos
- Velocity estável (sem queda nos últimos N blocos)

Recomendação textual no forecast:
```
Qualidade estável nos últimos 5 tickets (0 loopbacks). Você está pronto para 2 tickets
em paralelo. Quer tentar?  [S] Sim  [N] Não por enquanto
```

### Option C — Escalada automática (sistema ativa paralelismo sem consultar)
- Quando métricas estão boas, sistema automaticamente abre slot para 2º ticket
- Piloto não decide — sistema decide
- Viola o princípio "Piloto decide" do design

**Recommendation: Option B.** Métricas de qualidade (zero loopbacks) são o sinal mais
confiável de que o Piloto tem capacidade para mais. O forecast já tem esses dados
(consistency_score por bloco, teach loopbacks, quality iterations). A sugestão é uma
recomendação — Piloto confirma. Option C viola o princípio de controle do design explicitamente.

---

## Decision 6 — Tracks: quais ativar primeiro e como adaptar o benchmark?

**Problema:** 13 tracks existem no SDK mas nunca foram ativadas. O benchmark atual é orientado
a latência em ms (sistema MMORPG). No corporativo, o benchmark é qualidade/consistência.
Quais ativar primeiro e o que medir?

### Option A — Ativar todas as 13 de uma vez
- Máxima cobertura imediata
- Alto risco: muitas tracks não adaptadas gerando falsos alarmes
- Complexidade de adaptar 13 benchmarks simultaneamente

### Option B — Ativar por prioridade do `design/corporate-mode.md §7C` *(recommended)*

Da tabela de tracks do design (ordenada por `user_priority`):

| # | Track | Prioridade | Primeiro a ativar? |
|---|-------|------------|---------------------|
| 1 | Bloco & Fase | 10 | ✅ Redesign já feito (Phase 29) |
| 14 | Fundação Corporativa | 7 | ✅ Phase 29 em implementação |
| 2 | Orquestração & Paralelismo | 8 | ✅ Phase 32 inicia |
| 3 | Confiabilidade & Notificações | 8 | ✅ Phase 32 inicia |
| 4 | Forecast & Pilotagem | 6 | ✅ Phase 32 (este brainstorm) |
| 5 | UX & Dial de Abstração | 6 | Phase 31 já implementou |
| 6–13 | Demais | 3–5 | Ativar progressivamente |

**Adaptação de benchmark para qualidade:**
- `velocity_inference`: de linhas/hora → tickets/dia com consistency_score
- `phase_forecast`: de ETA de fase → ETA de lote de tickets
- `notification_manager`: de alertas de gate → alertas de reunião + degradação de qualidade

### Option C — Não ativar tracks agora, focar nos módulos novos
- Defer tracks para Phase 33+
- Mais simples para a Phase 32
- Perde o ponto: tracks são o mecanismo de melhoria contínua, não uma feature opcional

**Recommendation: Option B.** Ativar as 4 tracks de maior prioridade na Phase 32 (Orquestração,
Confiabilidade, Forecast, UX). As demais ficam no backlog do track system (auto-gerenciado).
A adaptação de benchmark é a mudança mais importante: substituir "latência em ms" por
"taxa de retrabalho", "consistency_score médio", e "velocity estável".

---

## Decision 7 — Alerta de degradação de track: como o sistema avisa que algo piorou?

**Problema:** Tracks monitoram métricas. Quando uma métrica degrada (ex: consistency_score
médio caindo por 3 blocos seguidos), o sistema avisa o Piloto. Como?

### Option A — Log silencioso (só registra, não alerta)
- Degradação registrada em `governance/tracks-report.md`
- Piloto lê quando quiser
- Pode perder degradação por dias sem notar

### Option B — Alerta em session_start.py *(recommended)*
- `session_start.py` verifica as tracks ativas ao iniciar
- Se degradação detectada: exibe alerta no briefing
- "⚠️ Track #3 (Confiabilidade): consistency_score caiu 3 blocos seguidos (0.82→0.79→0.76)"
- Alerta é informativo — Piloto decide o que fazer, não há ação automática

### Option C — Notificação push em tempo real
- Alerta fora da sessão (email/Slack) quando degradação acontece
- Dependência externa; complexidade
- O design menciona `notification_manager` — mas local-first

**Recommendation: Option B.** Session_start.py já é o ponto de briefing — alertas de track
pertencem ali. Alerta informativo (não bloqueante) é consistente com o princípio do Piloto
no controle. Se as notificações forem críticas no futuro, `notification_manager` (Track #3)
pode evoluir para push — mas começa local.

---

## Open questions (não decididas aqui)

1. **Velocity em sessões com múltiplas interrupções:** se o Piloto pausou o ticket por 3h
   por reunião, `finished_at - started_at` superestima o tempo real. O campo `paused_duration_hours`
   resolve se o Piloto preencher — mas é opt-in. Aceitamos essa imprecisão na v1?

2. **Forecast com tickets de sizes diferentes:** um ticket XL tem duração 5× maior que um XS.
   O forecast em "tickets/dia" é enganoso se os tickets variam muito. Proposta: forecast
   em "horas estimadas" além de "tickets/dia" — usa o campo `estimated_duration_hours` do manifest.

3. **Track #2 (Orquestração & Paralelismo):** o agente paralelo mencionado em `design/corporate-mode.md §7C`
   ("CURRENT FOCUS do agente paralelo — começa por aqui") nunca foi iniciado. Phase 32 é o
   momento de ativar formalmente? Ou continua deferido?

4. **Pilot-calendar.yaml privacidade:** o arquivo contém horários de reuniões (dados pessoais).
   Deve ter instrução explícita de não commitar (`governance/pilot-calendar.yaml` no `.gitignore`)?

---

## Confirmed decisions (Piloto 2026-05-31)

| # | Decisão | Escolha | Nota |
|---|---------|---------|------|
| 1 | Velocity — medir tempo real | **B+ ambos os modos** | Timestamps automáticos em block_start/block_close para MMORPG e corporativo. Adicionar também timestamps de FASE (`phase_started_at`, `phase_finished_at`). Mecanismo de pausa/retomada (`paused_at`/`resumed_at`) para descontar reuniões e interrupções. |
| 2 | Forecast — o que o Piloto vê | **B — HTML** | Velocity em tickets/dia E em horas estimadas. Estimativa ajustada por reuniões. Confidence band baseado em quantidade de histórico. Recomendação de paralelismo. |
| 3 | Calendário | **B — pilot-calendar.yaml** | Piloto DITA reuniões para o AI que atualiza o YAML. Suporte a reuniões recorrentes. Sem integração Google Calendar (arquitetura está separada do repo do cliente — não há risco de commit). |
| 4 | Alerta de reunião | **B+ dinâmico por timing** | Mesmo dia: alerta aparece em TODA sessão aberta naquele dia, com countdown ("reunião em X horas"). Dias futuros: só no session_start. |
| 5 | Paralelismo | **B+ com métricas de latência da IA** | Sistema sugere paralelo quando: qualidade estável (sem loopbacks) + etapas do pipeline com tempo de resposta alto (>20min). O gargalo real é o Piloto, não a máquina — paralelismo só faz sentido se a IA demorar. |
| 6 | Tracks | **FORA da Phase 32** | Tracks servem à arquitetura inteira, não só ao corporativo. Gerenciadas por agente separado. Phase 32 não implementa tracks. |
| 7 | Alerta degradação de track | **B** | session_start.py — alerta informativo, não bloqueante. |

## Open questions resolvidas pelo Piloto

| Questão | Resolução |
|---------|-----------|
| Velocity com pausas longas | ✅ Implementar pausa/retomada — `paused_at`/`resumed_at` no manifest |
| Forecast em horas | ✅ Sim — além de tickets/dia, mostrar horas estimadas |
| pilot-calendar.yaml no .gitignore | ✅ Desnecessário — arquitetura nunca está no mesmo repo do cliente |
| Track agent (Orquestração) | ✅ Agente separado cuida disso — Phase 32 não toca |

## Recommended synthesis

Após confirmação, gerar:
- `design/forecast-tracks.md` — design doc
- `phases/phase-32.md` — fase com blocos (a partir de block-173)
- Manifests dos blocos

End of brainstorm.
