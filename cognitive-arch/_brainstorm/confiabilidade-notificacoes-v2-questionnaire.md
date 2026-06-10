# Brainstorm v2 — Confiabilidade & Notificações — Questionnaire
# Generated: 2026-06-01
# Context: diagnóstico ao vivo — notifications.md vazia, 42 INV3 warnings, audit 72/100
# Scope: redesign da arquitetura de notificações para que sejam realmente entregues ao Piloto

---

# Brainstorm v2 — Confiabilidade & Notificações

**Generated:** 2026-06-01
**Diagnóstico base:** fila de notificações = 0 entradas (sempre vazia); 42 invariant warnings (INV3); audit 72/100

> **Como responder:**
> Para cada questão, marque `[x]` na opção escolhida ou escreva no campo "Outro".
> Pode adicionar notas livres abaixo de cada resposta.

---

## Questions

---

### Q1. Quem deve alimentar a fila de notificações?

**Contexto:** Hoje o `notification_manager.py` existe e funciona (testes passam), mas nenhuma ferramenta chama `notification_manager.add()`. A fila está eternamente vazia. Esse é o bug raiz.

🤖 **AI recommends:** `session_start.py` centraliza — roda as ferramentas e cria notificações baseado no output
📊 **Confidence:** 🟡 MEDIUM
💡 **Rationale:** session_start já roda audit, invariant_check, health_report. Centralizar ali evita que cada ferramenta precise conhecer o notification_manager. Uma mudança, não cinco.
🔗 **Evidence:** session_start.py já é o ponto de entrada de todas as ferramentas

**Options:**

- [ ] `session_start.py` centraliza — interpreta output das ferramentas e cria notificações ← AI pick
- [ ] Cada ferramenta chama `notification_manager.add()` diretamente quando detecta problema
- [ ] Event bus: ferramentas publicam eventos, session_start consome e cria notificações
- [ ] Outro (texto livre): _______________

**Your answer:**

**Notes (optional):**

---

### Q2. O que deve gerar uma notificação? (threshold de criação)

**Contexto:** Se tudo gera notificação, vira ruído e o Piloto ignora. Se pouco gera, continua invisível. Hoje temos 42 warnings que teoricamente deveriam ter gerado algo.

🤖 **AI recommends:** Só `critical` e `high` geram notificação — warn só se persistir > 3 sessões
📊 **Confidence:** 🟢 HIGH
💡 **Rationale:** Notification fatigue é o pior inimigo de sistemas de alerta. Ruído constante → Piloto aprende a ignorar. Warns de INV3 são todos do mesmo tipo (schema mismatch) — um único aviso consolidado é suficiente.
🔗 **Evidence:** 42 INV3 todos iguais; audit 72/100 merece notificação, 42 avisos individuais não

**Options:**

- [ ] Só critical/high; warns consolidados (1 notificação por tipo, não por bloco) ← AI pick
- [ ] Tudo gera notificação (máxima visibilidade)
- [ ] Só critical (zero ruído, máxima seleção)
- [ ] Configurável por ferramenta via governance/notification-rules.yaml
- [ ] Outro (texto livre): _______________

**Your answer:**

**Notes (optional):**

---

### Q3. Quando e como as notificações aparecem para o Piloto?

**Contexto:** Você levantou isso — nunca chegou nada fora do que você estava fazendo. O sistema precisa de um momento garantido de surfacing.

🤖 **AI recommends:** Início de sessão (session_start) + comando `/check` a qualquer hora; sem interrupção mid-block
📊 **Confidence:** 🟡 MEDIUM
💡 **Rationale:** Interrupção mid-block quebra o fluxo e pode gerar contexto errado. Melhor: sessão começa com "você tem N alertas, quer ver antes de continuar?" e o Piloto decide. Mid-block apenas para critical.
🔗 **Evidence:** padrão de UX de ferramentas de dev (git, linter) — alertas no checkpoint, não no meio do trabalho

**Options:**

- [ ] Início de sessão obrigatório + `/check` manual; mid-block só para critical ← AI pick
- [ ] Início de cada bloco (antes de começar qualquer bloco, mostra pendentes)
- [ ] Só início de sessão, nada mais
- [ ] Mid-block a qualquer momento que a ferramenta detectar (máxima proatividade)
- [ ] Outro (texto livre): _______________

**Your answer:**

**Notes (optional):**

---

### Q4. O que fazer com os 42 warnings INV3 (tier vs size)?

**Contexto:** `invariant_check.py` procura `tier: S/M/L` (formato v1). Os blocos novos usam `size: XS/S/M/L/XL` + `importance` (formato v2). O checker não foi atualizado. Todos os 42 warns são do mesmo bug de schema.

🤖 **AI recommends:** Atualizar `invariant_check.py` para aceitar `size` como substituto de `tier` — 1 fix, 42 warns somem
📊 **Confidence:** 🟢 HIGH
💡 **Rationale:** O INV3 verifica "bloco tem duração mas não tem tier/size para calcular velocidade". Basta aceitar `size` como equivalente. É uma linha de mudança no checker.
🔗 **Evidence:** blocks/block-162 a block-175 todos têm size no frontmatter; invariant_check.py linha ~80 hardcoda "tier"

**Options:**

- [ ] Atualizar `invariant_check.py` para aceitar `size` + `importance` como equivalente a `tier` ← AI pick
- [ ] Adicionar campo `tier` como alias nos templates v2 (retrocompatibilidade)
- [ ] Desativar INV3 e criar INV3_V2 com nova lógica
- [ ] Ignorar — são warnings de blocos históricos, não afetam trabalho atual
- [ ] Outro (texto livre): _______________

**Your answer:**

**Notes (optional):**

---

### Q5. Como medir que o sistema de notificações está funcionando?

**Contexto:** O benchmark atual diz "não medido". Sem métrica, nunca saberemos se melhorou.

🤖 **AI recommends:** `delivery_rate = notificações seen / criadas × 100`; alerta se pending > 2 sessões
📊 **Confidence:** 🟢 HIGH
💡 **Rationale:** Simples, direto. Se uma notificação fica pending por 2 sessões sem o Piloto ver, algo falhou (não foi mostrada, foi ignorada, ou o canal de delivery quebrou).
🔗 **Evidence:** track benchmark_target já define "100% das notificações atingem seen"

**Options:**

- [ ] `delivery_rate = seen/criadas × 100`; staleness alert se pending > 2 sessões ← AI pick
- [ ] Medir apenas taxa de criação (se ferramentas estão gerando)
- [ ] Medir só tempo médio pending → seen
- [ ] Não medir — o Piloto sabe se está recebendo ou não
- [ ] Outro (texto livre): _______________

**Your answer:**

**Notes (optional):**

---

### Q6. Notificação deve bloquear o Piloto ou ser informativa?

**Contexto:** Se o Piloto está no meio de uma tarefa urgente, uma notificação crítica de audit score deve parar tudo? Ou informar e deixar decidir?

🤖 **AI recommends:** Sempre informativa + acknowledge obrigatório; nunca bloqueia execução
📊 **Confidence:** 🟢 HIGH
💡 **Rationale:** Bloqueio causa frustração e leva o Piloto a dismiss sem ler. Informativa com "você precisa confirmar que viu" mantém visibilidade sem forçar parada. Critical pode requerer acknowledge antes do próximo bloco, não mid-block.
🔗 **Evidence:** design/corporate-mode.md §6B — "absolute delivery" significa que chegou, não que bloqueou

**Options:**

- [ ] Sempre informativa; critical requer acknowledge antes do próximo bloco ← AI pick
- [ ] Critical bloqueia execução até o Piloto agir
- [ ] Tudo informativo, dismiss automático após 24h
- [ ] Outro (texto livre): _______________

**Your answer:**

**Notes (optional):**

---

### Q7. (Aberta) O que mais está errado ou faltando no sistema de notificações que não foi coberto acima?

**Contexto:** Você mencionou que tinha outros pontos. Esse é o espaço.

🤖 **AI recommends:** (sem recomendação — resposta livre do Piloto)
📊 **Confidence:** 🔴 LOW — AI não tem visibilidade sobre o que você experimentou na prática

**Your answer (texto livre):**

_______________

---

*Gerado para Track: confiabilidade-notificacoes — sessão 2026-06-01*
*Síntese: após resposta do Piloto → design/notificacoes-redesign.md*
