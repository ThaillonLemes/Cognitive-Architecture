# Brainstorm: Cognitive Architecture v3 — Evolution Questionnaire

status: aguardando resposta do usuário
created_at: 2026-05-23
author: AI (gerado após leitura profunda do estado v2.5)
synthesis_target: design/arch-v3.md + próximas fases
topic: o que a arquitetura deve se tornar depois do v2.5

---

## Como usar este arquivo

Responda por **código de referência** (ex: `A1=2`, `B3=própria`, `C1=1+2`).
Pode combinar opções, escrever texto livre, ou dizer "não sei ainda".
Não precisa responder tudo de uma vez — responda o que fizer sentido agora.

Depois das respostas, o AI sintetiza o que está respondido em `design/arch-v3.md`
e propõe as fases concretas.

---

## Contexto que informa as perguntas

O health report de hoje (2026-05-23) revelou três sintomas sérios:
- **85 blocks feitos, velocidade = 0** — `actual_duration_hours` nunca foi preenchido nas retrospectivas. Os dados de medição existem na estrutura mas não na realidade.
- **SDK detectou fase errada** (reportou phase-9 em vez de phase-11) — o SDK está desconectado do projeto real.
- **0 Tracks definidos** — o sistema de Tracks existe mas nunca foi ativado.

Isso não é falha de design das fases — é lacuna entre o que a arquitetura suporta e o que realmente acontece no uso.

---

## Parte A — Uso real hoje

### A1. Como você realmente usa a arquitetura agora?

**Pergunta:** Na prática do dia a dia, o que você faz com a cognitive-arch? O que você abre, lê, consulta?

**Opções:**

1. **Só no início da sessão** — leio CLAUDE.md + STATE.md + NEXT.md para saber onde estou, depois trabalho livremente sem consultar mais nada.
2. **Durante o block** — consulto manifest e protocolos ativamente durante a execução, não só no início.
3. **No fechamento** — uso principalmente o checklist de 8 passos no block-close. O resto é ruído.
4. **Quase nunca** — o AI lê os arquivos, eu só falo o que quero fazer. A arquitetura é mais para o AI do que para mim.

**Por que distinto:** cada opção implica um ponto de fricção diferente. Se você usa só no início, o problema está no HOT boot. Se usa no fechamento, o problema está na checklist. Se o AI usa mas você não, a arquitetura precisa de uma interface humana melhor.

---

### A2. Quem conduz o trabalho?

**Pergunta:** Quando você começa uma sessão para trabalhar em um block, quem está no volante?

1. **Você conduz, o AI executa** — você decide o que fazer, como fazer, o AI escreve o código/docs.
2. **Você dá direção, o AI decide os passos** — você diz "implementa o combat system", o AI desdobra isso em decisões.
3. **O AI conduz, você aprova** — o AI lê STATE/NEXT, propõe o plano, você confirma ou corrige.
4. **Depende do block** — você conduz em blocos estratégicos, o AI conduz em blocos técnicos.

---

### A3. O Governor existe de fato?

**Pergunta:** O papel do Governor (integrar, auditar, atualizar STATE/NEXT, emitir próxima instrução) está sendo feito por quem na prática?

1. **Pelo AI em cada sessão** — a cada sessão, o AI age como Governor e faz os 8 passos.
2. **Por você manualmente** — você faz os git commits, atualiza STATE.md, escolhe o próximo block.
3. **Metade-metade** — o AI faz os passos de escrita, você faz o git e a decisão de próximo block.
4. **O SDK Governor ainda não foi ativado de verdade** — existe o código mas roda no modo manual descrito nos markdowns.

---

### A4. Frequência e ritmo

**Pergunta:** Com que frequência você trabalha ativamente no projeto usando a arquitetura?

1. **Todo dia** — sessão diária, multiple blocks por semana.
2. **Algumas vezes por semana** — sessões concentradas, mas com dias de pausa.
3. **Quando dá** — irregular, às vezes semanas sem sessão.
4. **Rajadas intensas** — períodos de muito trabalho (como construir os 85 blocks), depois silêncio.

**Por que importa:** o ritmo real define se um Governor loop automático vale o custo, se a arquitetura precisa de melhor "onde eu estava?" recovery, e se o risco de STATE.md stale é real.

---

## Parte B — Dores reais

### B1. O que mais te frustra hoje?

**Pergunta:** Se você pudesse remover UMA coisa da fricção atual, qual seria?

1. **Ler muita coisa no início** — o HOT boot é grande demais; leio coisas que não precisava.
2. **Não saber onde parei** — quando retorno a um projeto depois de dias, demora para entender o estado real.
3. **O checklist de 8 passos é pesado** — fechar um block demora mais do que devia.
4. **A arquitetura não me diz o que vem a seguir** — NEXT.md existe mas não tem opinião forte sobre o que é prioritário.
5. **Perco contexto no meio do block** — a sessão acaba e quando retomo, parte do raciocínio se perdeu.

---

### B2. O que o AI faz de errado com frequência?

**Pergunta:** Qual é o erro mais recorrente do AI quando trabalha dentro da arquitetura?

1. **Ignora axiomas** — escreve código/doc sem seguir os protocolos declarados.
2. **Scope creep** — vai além do que o manifest define, faz "enquanto estou aqui" mudanças não autorizadas.
3. **Não atualiza STATE/NEXT corretamente** — fecha o block mas o state fica inconsistente.
4. **Inventa** — quando não sabe algo (um arquivo, um protocolo), chuta em vez de perguntar.
5. **Perde raio de ação** — começa correto mas depois de muitas tool calls, perde o fio do manifest.

---

### B3. O que nunca funcionou?

**Pergunta:** Há alguma parte da arquitetura que foi implementada mas na prática nunca usou ou que não serve?

1. **Tracks** — existe o sistema mas nunca criou um Track real.
2. **Velocity + phase-forecast** — as ferramentas existem mas os dados de entrada (actual_duration_hours) nunca foram preenchidos.
3. **Security-review gate** — o protocolo está lá mas blocos com `security: true` nunca rodaram a revisão formal.
4. **SDK Python Governor** — o código existe mas roda em modo manual; o SDK automático nunca foi ativado.
5. **Retrospectivas completas** — escreve a retro mas não a lê depois; é um log, não um aprendizado.

---

### B4. O pior momento da sessão

**Pergunta:** Qual parte de uma sessão de trabalho você mais teme ou posterga?

1. **O início** — ler os HOT files, re-entender o estado, montar o contexto.
2. **O fechamento** — os 8 passos de block-close, o commit, a atualização do STATE.
3. **Quando tem gate failure** — resolver um gate que falhou sem saber bem o que fazer.
4. **Quando precisa planejar** — escrever o manifest de um novo block (muito protocolo para seguir).
5. **Quando o projeto ficou parado** — retornar depois de uma pausa longa e reconstruir onde estava.

---

### B5. O que a arquitetura não vê?

**Pergunta:** Que tipo de informação importante sobre o projeto NUNCA chega à arquitetura?

1. **Decisões informais** — decisões tomadas em conversa que nunca viraram ADR ou manifest.
2. **Dívida técnica** — código ruim que todos sabem que é ruim mas não tem block para consertar.
3. **O que o usuário final pensa** — nenhum feedback de quem vai usar o produto chega aos design docs.
4. **Dependências externas** — mudanças em bibliotecas, APIs, ferramentas que afetam o projeto.
5. **Erros que você não contou** — blocos que foram forçados (`forced`) sem registro claro do porquê.

---

## Parte C — O que funciona bem (não mexer)

### C1. Qual parte da arquitetura você mais confia?

**Pergunta:** O que você não mudaria de jeito nenhum?

1. **O sistema de manifests** — antes de trabalhar, descrever o que vai ser feito. Isso é inegociável.
2. **O BLOCK_LOG + retrospectivas** — registro de o que foi feito. Simples, append-only, confiável.
3. **Os axiomas P/Q/C/M/S** — as regras são claras e o AI as segue na maioria das vezes.
4. **O audit.sh** — verificação leve que roda rápido e diz se está tudo bem.
5. **A estrutura HOT/WARM/COLD** — a ideia de só ler o que precisa no momento em que precisa.

---

### C2. Qual protocolo o AI segue melhor?

**Pergunta:** Que parte da arquitetura o AI executa de forma mais confiável, sem precisar de correção?

1. **Pointer integrity** — referências para outros arquivos raramente quebram.
2. **Code header** — cabeçalho obrigatório em arquivos de código está sempre presente.
3. **BRIEF em arquivos grandes** — arquivos de mais de 100 linhas sempre têm BRIEF.
4. **Manifest antes de trabalho** — o AI nunca pula a criação do manifest.
5. **Retrospectiva estruturada** — as retros seguem o template, não viram prosa livre.

---

## Parte D — Automação e Governor

### D1. Qual é o modelo de operação ideal para você?

**Pergunta:** Como você quer que o Governor opere no futuro ideal?

1. **Manual puro** — você decide quando o Governor age. Zero automação. Controle total.
2. **Cron agendado** — Governor roda automaticamente em horários fixos (ex: ao abrir o computador, ao fechar). Você ainda tem veto.
3. **Evento-triggered** — Governor age quando algo acontece (block marcado `done`, commit feito, X horas sem atividade).
4. **Loop adaptativo** — Governor monitora continuamente, age quando precisa, fica quieto quando não tem nada. ~$24-50/mês.
5. **Híbrido** — loop automático para integração e audit; decisões estratégicas ainda são manuais.

---

### D2. O que o Governor deveria fazer que ainda não faz?

**Pergunta:** Se o Governor fosse mais poderoso, o que ele resolveria por você?

1. **Detectar drift** — perceber que o estado está inconsistente (STATE.md vs. git vs. board.md) antes de você perceber.
2. **Sugerir próximo block** — não só dizer qual é o próximo, mas explicar por quê e se faz sentido agora.
3. **Consolidar contexto pós-pausa** — quando você volta depois de dias, o Governor te dá um briefing do que aconteceu.
4. **Resolver dependências automaticamente** — quando um block fica desbloqueado, notifica e prepara o ambiente.
5. **Medir e reportar** — toda semana, envia um relatório de velocidade, saúde e próximos passos.

---

### D3. Notificações

**Pergunta:** Como você quer ser avisado quando algo acontece no projeto?

1. **Não quero notificação automática** — verifico quando quero.
2. **Push notification quando block fica desbloqueado** — só o que muda o que posso fazer agora.
3. **Resumo diário** — um sumário no início do dia do estado atual.
4. **Alerta quando algo quebra** — só se o audit falhar ou uma dependência crítica mudar.

---

## Parte E — Conhecimento acumulado

### E1. O que fazer com 85+ retrospectivas?

**Pergunta:** Tem 85 retrospectivas escritas. Ninguém as lê. O que deveria acontecer com esse conhecimento?

1. **Nada** — o valor é no registro, não na leitura. São para auditoria futura, não consumo ativo.
2. **Síntese periódica** — a cada fase fechada, o Governor lê todas as retros da fase e gera um "what we learned".
3. **Padrão mining** — o SDK analisa as retros e extrai os axiomas mais violados, os tipos de blocks que demoram mais, os erros recorrentes.
4. **Retrospectiva de retrospectivas** — uma vez por trimestre, revisar as retros com o AI e atualizar os axiomas/protocolos com base no que foi aprendido.

---

### E2. As decisões ADR estão acessíveis?

**Pergunta:** Quando você precisa lembrar "por que tomamos aquela decisão", o que acontece?

1. **Encontro rapidamente** — INDEX.md + `decisions/` organizado, grep fácil.
2. **Demora mas acho** — preciso lembrar qual ADR é relevante e ler alguns antes de achar.
3. **Raramente acho** — a maioria das decisões não virou ADR, ficou em conversa.
4. **Nunca procuro** — não costumo buscar decisões passadas, refaço o raciocínio do zero.

---

### E3. Cross-project learning

**Pergunta:** Você planeja usar cognitive-arch em outros projetos além do MMORPG?

1. **Sim, já tenho outros projetos em mente** — e quero que o que aprendi no MMORPG ajude o próximo.
2. **Talvez, mas não sei como** — parece que cada projeto começa do zero mesmo.
3. **Não, MMORPG é o foco** — não vale a pena pensar em outros agora.
4. **A cognitive-arch em si É o produto** — o objetivo é torná-la reutilizável por outras pessoas, não só por mim.

---

## Parte F — Escala

### F1. Onde este projeto vai parar?

**Pergunta:** O MMORPG tem 4 sub-repos e ~110+ blocks (server). Onde você imagina que isso vai estar em 1 ano?

1. **Muito maior** — mais sub-repos, mais agents rodando em paralelo, mais complexity.
2. **Mais ou menos este tamanho** — o projeto cresce em profundidade (features), não em estrutura.
3. **Vai simplificar** — conforme o código estabiliza, a necessidade de arquitetura cognitiva diminui.
4. **Não sei** — depende de coisas externas (tempo, dinheiro, time).

---

### F2. O maior risco de escala

**Pergunta:** O que mais te preocupa à medida que o projeto cresce?

1. **HOT files ficarem pesados** — STATE.md de 200 linhas, INDEX.md de 500 linhas, boot lento.
2. **Agents perdendo contexto** — com mais blocks e fases, o AI começa a confundir o que foi feito.
3. **Decisões contraditórias** — ADRs antigos conflitam com novas direções sem que ninguém perceba.
4. **Eu perder o controle** — a arquitetura fica tão automática que não sei mais o que está acontecendo.
5. **Custo de tokens** — projetos grandes = mais contexto = mais caro por sessão.

---

### F3. Multi-agente real

**Pergunta:** Você já rodou múltiplos agents em paralelo de fato?

1. **Sim, regularmente** — múltiplos Claude Code sessions ao mesmo tempo em sub-repos diferentes.
2. **Sim, mas raramente** — tentei algumas vezes, é confuso coordenar.
3. **Não, ainda não** — tudo serial. Um block de cada vez.
4. **Não e não quero** — prefiro controle serial, não quero gerenciar paralelo.

---

## Parte G — Interface humana

### G1. O que você quer ver como humano ao abrir o projeto?

**Pergunta:** Se a arquitetura te mostrasse UMA tela/dashboard ao abrir uma sessão, o que ela deveria conter?

1. **Estado simples** — "estamos em phase X, block Y, próximo é Z". Nada mais.
2. **Saúde geral** — audit score, velocity, se tem algo bloqueado ou quebrado.
3. **O que posso fazer agora** — lista priorizada de ações disponíveis com contexto de por quê cada uma.
4. **O que mudou desde a última sessão** — diff do estado: novos commits, blocks fechados, dependências resolvidas.
5. **Nada** — não quero um dashboard. Prefiro perguntar ao AI o que preciso saber.

---

### G2. Como você quer planejar o próximo mês?

**Pergunta:** Quando você quer decidir quais são os próximos 10 blocks, como isso deveria acontecer?

1. **AI propõe, eu aprovo** — o Governor olha o design e os gaps e sugere uma sequência.
2. **Eu escolho, AI estrutura** — você decide o que quer, o AI escreve os manifests.
3. **Sessão de planejamento** — uma sessão dedicada onde vocês dois revisam o ROADMAP.md e definem as próximas fases.
4. **Emergente** — não planejamos mais de 1-2 blocks à frente. A arquitetura responde ao que aparece.

---

### G3. Documentação para humanos

**Pergunta:** Hoje, se um colega seu entrasse no projeto, o que aconteceria?

1. **Ficaria perdido** — a arquitetura é AI-first, humanos não sabem por onde começar.
2. **Encontraria CLAUDE.md e seguiria** — o onboarding existe mas é mais para o AI do que para ele.
3. **Teria que perguntar** — você teria que explicar o projeto pessoalmente.
4. **Funcionaria bem** — a documentação de PROJECT.md, design/ e phases/ é suficiente para um humano.

---

## Parte H — Medição e calibração

### H1. Você sabe quanto tempo seus blocks realmente levam?

**Pergunta:** O campo `actual_duration_hours` nunca foi preenchido em nenhum dos 85 blocks. Por quê?

1. **Não sabia que existia** — a retrospectiva não pedia isso claramente.
2. **Sabia mas não monitorei** — não prestei atenção no relógio.
3. **A granularidade não faz sentido** — um block pode durar minutos ou horas, difícil medir.
4. **Não me importo com essa métrica** — velocidade não é o problema agora.
5. **Quero medir mas precisa de ajuda** — não sei como fazer isso sem fricção.

---

### H2. Estimativas de fase — importam?

**Pergunta:** O `phase-forecast.md` pode calcular quando uma fase vai terminar. Você usaria isso?

1. **Sim, frequentemente** — quero saber se vou terminar a fase dentro do prazo que me dei.
2. **Às vezes** — quando tem deadline externo (release, demo, contrato).
3. **Raramente** — eu sei intuitivamente como está o progresso.
4. **Não** — não tenho prazos rígidos, forecast não ajuda.

---

### H3. Qualidade de block — você quer saber?

**Pergunta:** Se cada block recebesse uma "nota de qualidade" (baseada em: gates passaram, scope respeitado, retro escrita, axiomas seguidos), você usaria?

1. **Sim** — quero saber quais blocks foram fracos e por quê.
2. **Só para identificar padrões** — não me importo com a nota individual, mas quero saber se estou piorando.
3. **Não** — adiciona burocracia sem valor. Ou passa ou não passa.
4. **Só para blocks críticos** — Tier L e blocos de segurança, sim. Tier S, não.

---

## Parte I — Direção e prioridade

### I1. Qual é o maior gap da arquitetura hoje?

**Pergunta:** Se você tivesse que nomear UMA coisa que a arquitetura claramente não faz e deveria fazer, qual seria?

*(resposta livre — não tem opções aqui, é propositalmente aberto)*

---

### I2. O que vem antes de tudo?

**Pergunta:** Forçando uma prioridade — o que você abordaria primeiro?

1. **Consertar o que está quebrado** — velocity sem dados, SDK com fase errada, Tracks nunca usados. Resolve os bugs da v2.5 antes de construir v3.0.
2. **Automação do Governor** — ativar o SDK de fato, com loop ou cron. Parar de ser manual.
3. **Interface humana** — criar um dashboard/resumo que você (não o AI) consiga ler rapidamente.
4. **Consolidação de conhecimento** — minerar as 85 retros, criar algo útil com elas, melhorar os protocolos com base no que foi aprendido.
5. **Expansão do MMORPG** — parar de melhorar a arquitetura e usar o que tem. Block-111 está desbloqueado.

---

### I3. Qual seria o sinal de sucesso da v3.0?

**Pergunta:** Como você saberia que a cognitive-arch v3.0 é melhor que a v2.5? O que teria que ser verdade?

1. **Eu leio menos** — começo uma sessão e sei o que fazer em menos de 30 segundos, sem ler múltiplos arquivos.
2. **O AI erra menos** — blocos fecham sem eu ter que corrigir scope creep, axiomas ignorados ou STATE.md stale.
3. **Tenho dados reais** — velocity é calculado de verdade, não "INSUFFICIENT DATA".
4. **Posso passar dias sem mexer e retornar facilmente** — a arquitetura me mostra o que perdí sem custo alto.
5. **Outra pessoa consegue usar** — não precisa ser eu — alguém com context zero consegue trabalhar com ela.

---

### I4. O que você NÃO quer?

**Pergunta:** Qual direção a arquitetura NÃO deveria tomar?

1. **Mais arquivos** — já tem muita coisa para ler. Menos é mais.
2. **Mais automação sem controle** — não quero que o AI faça coisas sem eu saber.
3. **Dependência de ferramentas externas** — quanto mais depende de Python/Node/APIs externas, mais pode quebrar.
4. **Virar um produto comercial** — não quero transformar isso em algo para vender; é minha ferramenta pessoal.
5. **Ficar complexa demais para entender** — se eu não consigo explicar em 5 minutos, está grande demais.

---

## Resumo para resposta

Você pode responder assim:

```
A1=4
A2=2+3 (depende)
A3=3 (metade-metade)
A4=4 (rajadas)
B1=5 (perco contexto mid-block)
B2=2 (scope creep)
B3=1+2+4 (tracks, velocity, sdk)
...
I1= [texto livre sobre o maior gap]
I4=1+5
```

Ou pode responder conversando mesmo — referencia as letras/números e eu entendo.

---

*Questionnaire gerado em 2026-05-23. Baseado em análise do health-report, BLOCK_LOG, checklist e _future/ docs.*
