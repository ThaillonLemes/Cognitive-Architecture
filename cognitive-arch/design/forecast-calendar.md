# Design: Forecast, Calendário & Velocity

status: approved
created_at: 2026-05-31
authors: Thaillon (Piloto) + AI (brainstorm session 2026-05-31)
synthesis_source: `_brainstorm/forecast-tracks-v2-redesign.md` (all 7 decisions confirmed 2026-05-31)
phase: phase-32
note: Tracks excluídas desta fase — gerenciadas por agente separado

---

## 0. O que é o Forecast + Calendário

O Piloto entrega tickets. Com o tempo, a arquitetura sabe quanto ele demora, quando tem reuniões,
e pode prever quando vai terminar um lote de trabalho. Mais: sugere quando faz sentido abrir
um segundo ticket em paralelo.

**Filosofia:** dados reais, não estimativas. Timestamps capturados automaticamente no `block_start`
e `block_close` — zero input manual para o dado básico. Reuniões: Piloto dita para o AI, que
atualiza o calendário. O forecast é consequência natural dos dados acumulados.

**Escopo desta fase:** velocity tracking, forecast de entrega, calendário local, alertas de reunião.
Tracks ficam com o agente de tracks (arquitetura inteira) — não são escopo da Phase 32.

---

## 1. Velocity Tracking

### Timestamps automáticos — ambos os modos

`block_start.py` e `block_close.py` já foram modificados na Phase 29 para suportar novos campos.
Esta fase adiciona os campos de tempo:

**No manifest (adicionado pelo block_start.py):**
```yaml
started_at: 2026-06-02T09:15Z
paused_at: ~          # preenchido quando Piloto pausa (vai para reunião)
resumed_at: ~         # preenchido quando retoma
finished_at: ~        # preenchido pelo block_close.py
actual_duration_hours: ~   # calculado: finished_at - started_at - paused_duration
```

**No arquivo de fase (adicionado pelo phase_manager.py):**
```yaml
phase_started_at: 2026-06-01T10:00Z
phase_finished_at: ~   # preenchido ao fechar a fase
phase_duration_hours: ~
```

**Por que fases também:** "você deveria ter por fase, lá no MMORPG — quanto está demorando
cada fase, para poder mensurar quanto vai terminar o MMORPG." Timestamps de fase dão o dado
macro que timestamps de bloco não têm. Ambos os modos (MMORPG e corporativo) se beneficiam.

### Pausa e retomada

Quando o Piloto tem uma reunião no meio de um bloco:
```
python sdk/velocity_tracker.py --pause --block-id block-XXX --arch-root .
>>> Bloco pausado às 13:58. Tempo decorrido até agora: 2h15m.

[reunião]

python sdk/velocity_tracker.py --resume --block-id block-XXX --arch-root .
>>> Bloco retomado às 15:10. Pausa: 1h12m (será descontada).
```

Ou via conversa: "pausei para reunião" → AI chama `velocity_tracker.py --pause`.

### Derivação de velocity

`velocity_inference.py` (já existe, reorientado):
- Por bloco: `actual_duration_hours` por ticket
- Por dia: tickets/dia (média móvel dos últimos N blocos)
- Em horas: horas estimadas por próximo ticket similar (baseado em `size × importance`)
- Por fase (MMORPG): horas/fase, forecast de quando a fase atual termina

---

## 2. Forecast de Entrega

### HTML de forecast

```
┌─────────────────────────────────────────────────────┐
│  FORECAST — Visagio Project Alpha                    │
│                                                      │
│  Velocity atual: 2.3 tickets/dia · 3.2h/ticket avg  │
│  Tickets em aberto: 7                               │
│                                                      │
│  Estimativa base:    3.0 dias úteis (sexta 06/06)   │
│  Impacto reuniões:  +0.5 dias (3h de reunião esta   │
│                      semana)                        │
│  Estimativa ajustada: 3.5 dias úteis                │
│                                                      │
│  Confidence: MÉDIO (baseado em 8 tickets)           │
│  ──────────────────────────────────────────────────  │
│  Paralelismo: 1 ticket atual                        │
│  Sugestão: pronto para 2 em paralelo               │
│  (últimos 5 tickets: 0 loopbacks, tempo de          │
│   implementação médio 45min)                        │
└─────────────────────────────────────────────────────┘
```

### Confidence band

| Histórico | Confidence | O que significa |
|-----------|-----------|-----------------|
| < 3 blocos | BAIXO | Estimativa é um chute calibrado |
| 3–10 blocos | MÉDIO | Tendência clara, desvio possível |
| > 10 blocos | ALTO | Dado robusto, forecast confiável |

### Recomendação de paralelismo

Sistema recomenda abrir 2º ticket quando:
1. Últimos 5 tickets fecharam sem quality loopback (qualidade passou na primeira)
2. Teach mode sem loopback to implement (Piloto entendeu na primeira)
3. Tempo médio de etapas do pipeline > 20 min (a IA demora — vale usar o tempo)

**Filosofia:** o gargalo real é o Piloto, não a máquina. Se o pipeline é rápido (5–10 min por
etapa), não há razão para paralelizar — é mais simples trabalhar serial. O paralelismo só faz
sentido quando a máquina está "pensando" por longos períodos e o Piloto ficaria ocioso.

---

## 3. Calendário e Alertas

### pilot-calendar.yaml

```yaml
# governance/pilot-calendar.yaml
# Editado pelo AI quando Piloto dita reuniões

meetings:
  - date: 2026-06-02
    time: "14:00"
    duration_hours: 2
    desc: "sync semanal com o time"
    recurring: weekly        # opcional — repete toda semana no mesmo horário
  - date: 2026-06-03
    time: "10:00"
    duration_hours: 1
    desc: "1:1 com senior"
```

**Interface natural:** Piloto dita → AI atualiza o arquivo. Nunca edita YAML diretamente.
```
Piloto: "tenho reunião toda segunda às 9h por 1 hora, sync com o time"
AI: → adiciona ao pilot-calendar.yaml com recurring: weekly
```

**Reuniões recorrentes:** suportadas com `recurring: daily | weekly | biweekly`.

### Alertas de reunião — comportamento por timing

**Mesmo dia (reunião hoje):**
- Aparece no INÍCIO de TODA sessão aberta naquele dia
- Aparece no INÍCIO de TODA resposta do AI naquele dia com countdown
- Formato: `⚠️ Reunião em 2h15m — sync semanal às 14:00`
- Piloto nunca vai esquecer de uma reunião por estar no hiperfoco de programação

**Próximos dias:**
- Aparece uma vez no `session_start.py` do início do dia
- "Amanhã: reunião às 10h (1:1 com senior)"

**Integração com forecast:** reuniões do dia impactam diretamente a estimativa de entrega.
A capacidade do dia é reduzida automaticamente (8h hábeis − X horas de reunião).

---

## 4. Módulos (Phase 32)

| Módulo | Função |
|--------|--------|
| `sdk/velocity_tracker.py` | Registra `started_at`, `paused_at`, `resumed_at`, `finished_at`; calcula `actual_duration_hours`. CLI `--pause`/`--resume`. Também adiciona timestamps de fase. |
| `sdk/forecast_engine.py` | Lê velocity history + calendar; gera HTML de forecast com confidence, estimativa ajustada, sugestão de paralelismo |
| `sdk/calendar_manager.py` | Gerencia `pilot-calendar.yaml` (add/edit/list meetings, recorrência); injeta alertas no session_start e nas respostas do dia |

---

## 5. Integração com módulos existentes

| Módulo | Integração |
|--------|-----------|
| `block_start.py` (phase-29) | Adiciona `started_at` ao manifest ao iniciar |
| `block_close.py` (phase-29) | Adiciona `finished_at`; chama `velocity_tracker.py` para calcular `actual_duration_hours` |
| `phase_manager.py` (phase-29) | Adiciona `phase_started_at` ao iniciar fase; `phase_finished_at` ao fechar |
| `session_start.py` | Carrega alertas de reunião do dia; exibe forecast resumido no briefing |
| `velocity_inference.py` (existente) | Reorientado: lê `actual_duration_hours` dos manifests (agora preenchido) e computa velocity real |
| `phase_forecast.py` (existente) | Reorientado: usa velocity real de tickets para MMORPG e velocity de tickets corporativos |

---

## 6. Tracks — fora desta fase

Tracks servem à arquitetura inteira, não só ao modo corporativo. São gerenciadas por um agente
separado (`agent:tracks`) que tem autonomia para propor melhorias nos módulos monitorados.

**O que existe:** `tracks/PRIORITY.md`, `protocols/track-{generation,priority,block-execution}.md`,
`templates/track.md` — tudo já implementado.

**O que falta:** adaptação do benchmark (ms → qualidade) e ativação formal das tracks prioritárias.
Isso é responsabilidade do track agent, não desta fase.

---

## 7. Out of Scope

- Tracks (agente separado)
- Integração com Google Calendar / Outlook API
- Notificação push fora da sessão (email, Slack)
- Relatório semanal automático (já existe como ferramenta no SDK — não precisamos recriar)
- Paralelismo de agentes (o Piloto gerencia manualmente por ora)

---

*Brainstorm: `_brainstorm/forecast-tracks-v2-redesign.md`*
*Fase: `phases/phase-32.md`*
*Revisado em: 2026-05-31*
