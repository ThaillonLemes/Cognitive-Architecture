# Design: Corporate Mode — A Arquitetura como Amplificador Profissional

status: approved
created_at: 2026-05-30
authors: Thaillon (Piloto) + AI (brainstorm v2 session)
synthesis_source: `_brainstorm/corporate-mode-v2-questionnaire.md` + chat decisions
brainstorm_responses_captured: 2026-05-30
supersedes_intent: phases/phase-29.md (draft inicial de 5 blocos — agora reescopado)

---

## 0. A Virada de Norte (a tese central)

Até aqui o objetivo da arquitetura cognitiva era **terminar um projeto** — o MMORPG, um produto, do zero à fase N. A unidade de sucesso era o software pronto.

A partir de agora o objetivo é outro: **transformar o Piloto numa máquina de qualidade, entrega e consistência profissional.** A unidade de sucesso deixa de ser "o produto está pronto" e passa a ser "o Thaillon entregou muito, com qualidade extrema, rápido, e sabe explicar tudo o que entregou."

O projeto deixa de ser o protagonista. **O profissional é o protagonista.** A arquitetura vira um exoesqueleto: não substitui o Piloto, amplifica ele. Simbiose — o Piloto traz contexto, julgamento e autoridade; a IA traz velocidade, memória infinita e execução paralela. Nenhum dos dois faz sozinho o que os dois fazem juntos.

Tudo neste documento deriva dessa virada.

---

## 1. A nova hierarquia organizacional

A correção mais importante da sessão (Q9): **fase não é um agrupamento plano.** A estrutura tem três níveis, e os nomes são intercambiáveis — o que importa é a forma de organizar, não o rótulo.

| Nível | No modo projeto (antigo) | No modo corporativo (novo) | Natureza |
|-------|--------------------------|----------------------------|----------|
| **Agente** | uma instância de trabalho | **um cliente** | O contexto macro. Cada cliente = um agente próprio, isolado. |
| **Fase** | um marco do roadmap | **um workday OU uma feature** | O que você trabalha *dentro* daquele cliente. Escala flexível: pode ser um dia de trabalho, ou uma ficha/feature inteira, ou várias fases para uma feature grande. |
| **Bloco** | uma unidade atômica de progresso | **um ticket / uma tarefa** | A subdivisão executável. Pega um ticket, faz o ticket. |

Princípio que o Piloto cravou: *"se a gente abstrair que os nomes não importam, e as fases são um agrupamento de tarefas que fazem sentido, você pode fazer isso em qualquer nível de quase qualquer coisa — inclusive um artigo científico ou um livro."* A estrutura é fractal e agnóstica de domínio. Só renomeamos as etiquetas; a máquina de organizar é a mesma.

**Decisão derivada:** modo corporativo é **extensão**, não modo novo (Q1 aceito). Não bifurcamos o sistema — adicionamos campos e perfis ao que já existe.

---

## 2. Tabela de decisões

| ID | Questão | Decisão | Origem | Confiança IA |
|----|---------|---------|--------|--------------|
| Q1 | Extensão ou novo modo? | **Extensão** com campos corporativos | ✅ Aceito | 🟡 |
| Q2 | Bloco serve para ticket? | **Sim** + criar Tier **XS e XL** + revisitar a estrutura de bloco/fase | 🔧 Expandido | 🟡 |
| Q3 | Onde ficam os scripts Python? | **Só local, nunca commitado** + capacidade de operar à distância da pasta | 🔧 Expandido | 🟢 |
| Q4 | Nível de scan ao entrar? | **L1 auto + L2 por ticket** + scanner profundo multi-nível com base de conhecimento persistente | 🔧 Muito expandido | 🟡 |
| Q5 | Onde persiste o perfil? | **`governance/`** | ✅ Aceito | 🟢 |
| Q6 | Quem dá go/no-go? | **Piloto sempre** (enquadrado como simbiose, não autoridade) | ✅ Aceito | 🟢 |
| Q7 | Quando roda teach mode? | **Obrigatório em linguagem nova, opcional no resto** + vira etapa de pipeline | 🔧 Expandido | 🔴→✅ |
| Q8 | O que o consistency checker valida? | **Estrutural apenas** + proposta proativa de melhorias como etapa de pipeline | 🔧 Expandido | 🟡 |
| Q9 | Fases fazem sentido? | **Sim, mas como nível dentro do cliente-agente** (não grupo plano) | 🔧 Corrigido | 🔴→🔧 |
| Q10 | O que o STATE rastreia? | **O Piloto** (estado cognitivo), não o produto da empresa | ✅ Aceito | 🟡 |

**Taxa de acerto da IA:** 5 de 10 aceitos verbatim (50%). Os 5 restantes foram expandidos ou corrigidos pelo Piloto — exatamente o sinal de que ele tinha opinião forte onde a IA estava chutando (Q7 e Q9 eram 🔴 low confidence e foram justamente os mais reformulados). Alinhamento saudável.

---

## 3. Os componentes (decisões + amplificação)

Onde o Piloto pediu "incrementa, deixa supremo", eu amplifico. Marco com 🔬 **[amplificação da IA]** o que é minha adição ao que ele falou.

### 3.1. Scanner de Codebase — a fundação de tudo

O Piloto foi enfático: *"é assim que a gente começa tudo."* O scanner não é só uma feature, é a base de memória confiável que sustenta todo o resto.

**Objetivo:** entender uma codebase alheia em profundidade total e **persistir esse entendimento num banco de dados** — para nunca depender da janela de contexto da IA, e para gerar código sempre no padrão exato do que foi escaneado.

**Por que importa agora:** no MMORPG, estética de código não importa ("só precisa rodar e ser foda"). No corporativo, **estética é a moeda da previsibilidade** — código que parece escrito pelo mesmo time é mais bem-visto, mais fácil de revisar, e constrói confiança. Ser previsível para os superiores vale mais que ser brilhante e estranho.

**Níveis de scan:**

- **L0 — Arquitetural macro** 🔬 *[amplificação]*: que arquitetura de sistema está em jogo? Web, embarcado, serverless, monolito, microsserviços. Infra: AWS, redes, filas. A Visagio é consultoria — vários tipos de sistema. Detectar primeiro o "tipo de mundo" antes de mergulhar.
- **L1 — Estrutura & linguagens (automático no onboarding)**: árvore de diretórios, linguagens, entry points, build system, dependências principais. < 50 arquivos, leitura rasa (headers).
- **L2 — Padrões de arquitetura de software (sob demanda, por ticket)**: identificar o estilo do mercado em uso — Clean Architecture, DDD, Hexagonal/Ports-and-Adapters, MVC, Feature-Sliced, etc. E **a área específica onde o ticket vai mexer.**
- **L3 — Estética & convenções de código** 🔬 *[amplificação]*: naming, organização de arquivos, estilo de imports, formatação, padrões de teste, como erros são tratados, como o estado é gerenciado (Redux? Context? Zustand?). O "dialeto" do time.
- **L4 — Coexistência de padrões** 🔬 *[amplificação]*: detectar quando há **mais de um padrão** no mesmo codebase (legado vs. atual, ou estilos diferentes por pessoa). Hoje, com todo mundo usando IA, o padrão tende a convergir para um "sotaque de IA" — mas ainda há divergência. Reportar qual é o padrão *vigente* (a seguir) vs. o *legado tolerado* (não replicar, não tocar).

**Saída:** `governance/project-profile-<cliente>.md` — a base de conhecimento persistente. Nomeada por cliente (permite múltiplos clientes simultâneos, um por agente). Contém só metadados (padrões, nomes, contagens, decisões arquiteturais) — **nunca trechos de código real do cliente** (ver §5, compliance).

**Integração frontend↔backend (regra do Piloto):** o segundo sempre integra com o primeiro. Se o cliente (frontend) já está pronto antes do backend, ótimo — você já faz o backend integrado. O primeiro tem peso maior. Backend = profundamente performático, pode até ajustar design antes de integrar. Sem briga de ordem: quem chega depois pega o que o primeiro fez e integra.

**Teachability** 🔬 *[amplificação]*: o perfil + a arquitetura são ensináveis. O Piloto pode treinar outras pessoas a operar a IA do jeito dele, sem elas entenderem o código. Funcionários que entregam no mesmo padrão, usando a mesma arquitetura cognitiva. A IA do Piloto pode até integrar o trabalho de terceiros (mesmo de um funcionário dele) mantendo o padrão. → Isso pede um futuro **"operator handbook"** — fora do escopo da primeira fase, mas registrado.

### 3.2. Motor de Consistência

**Valida só estrutura** (Q8): naming, organização de arquivos, estilo de imports, convenções por linguagem — comparando o código gerado/alterado contra o `project-profile`. **Não** analisa lógica de negócio — esse julgamento é do senior, e heurística ali é falsa precisão.

Saída: score de consistência + lista de divergências ("seu código diverge do padrão do time em 3 pontos: X, Y, Z").

🔬 *[amplificação]* — **Modo proativo de melhoria** (ideia do Piloto em Q8, estruturada): se temos acesso à codebase inteira (frontend + backend + análise de requisitos), o motor pode varrer *outras* áreas, detectar melhorias possíveis, e gerar:
- um pull request com a melhoria,
- um **relatório explicando o porquê** (gerado, escrito — vira documentação que dispensa reunião),
- opcionalmente um post de Slack no formato "DevLog" (análogo ao que vocês fazem no Discord do MMORPG).

Isso vira uma **etapa do pipeline de trabalho**. ⚠️ Mas é a etapa que mais exige capital político — ver §6.

### 3.3. Pipeline de Trabalho 🔬 *[a grande amplificação]*

O Piloto disse "dá pra montar um pipeline aqui?" — dá, e é a espinha dorsal do modo corporativo. A ferramenta não só implementa: ela **organiza o trabalho do início ao fim** para entregar com mais qualidade e menos prazo. Acelera o profissional.

```
TICKET → [1 Intake] → [2 Scan L2/L3] → [3 Implementar] → [4 Qualidade/Revisão] → [5 Teach/Report] → ENTREGA
```

1. **Intake** — ticket (texto livre ou Jira-style) vira manifesto de bloco corporativo: `ticket_id`, `acceptance_criteria`, `reviewer`, `scope`, `tier (XS/S/M/L/XL)`.
2. **Scan dirigido** — L2/L3 só na área que o ticket toca. Mesmo código novo precisa se conectar ao resto → escaneia o ponto de integração.
3. **Implementar** — gerar código no padrão do `project-profile`, com testes realísticos.
4. **Qualidade/Revisão** — etapa própria. Checklist objetivo (testes, consistência, arquitetura) + revisão IA↔humano. Go/no-go é do Piloto, sempre. 🔬 Pode virar uma *área inteira* do sistema: "processo de qualidade de código."
5. **Teach/Report** — gera a explicação multi-nível (técnico/equipe/aprendizado) antes da reunião. Um "pré-podcast" do que foi feito. O Piloto sempre consegue explicar tudo, mesmo não tendo digitado as linhas. + Documentação/email/Slack quando aplicável.

### 3.4. Estado centrado no Piloto (Q10)

O `STATE.md` deixa de rastrear o produto e passa a rastrear **o Piloto**: nível de entendimento de cada cliente, tickets em aberto, gaps de conhecimento, padrões de erro, onde ele está no fluxo de cada ticket.

🔬 *[amplificações do Piloto em Q10, estruturadas]*:
- **Calendário & reuniões**: notificações de reuniões ("você tem reunião em 2 dias"), e estimativa se ele vai conseguir entregar a tempo.
- **Velocity de tickets**: coletar tempo real por bloco → derivar ritmo (tickets/hora, /dia, /semana) → **forecast de entrega** ("nesse ritmo, você entrega N tickets até sexta"). Mensurar trabalho em tickets e em linhas de código.
- Isso reusa o `velocity_inference` e `phase_forecast` que já existem — só reorientados para o Piloto em vez do projeto.
- **Escalada de paralelismo de tickets** 🔬: começar com **1** ticket por vez (calibrar o tempo real), depois **2** simultâneos, depois **3** — subindo até achar o gargalo, que é **a parte humana do Piloto** (revisão, go/no-go, entendimento). O sistema não força paralelismo cego: mede onde o Piloto vira o gargalo e estaciona ali. O limite é humano, não de máquina.

### 3.5. Operação à distância da pasta 🔬 *[amplificação — ideia do Piloto em Q3]*

A cognitive-arch fica numa pasta separada na máquina local. A IA opera o repo da empresa **de fora** — não precisa estar dentro da pasta do cliente. Vantagem que o Piloto sacou: **imunidade**. Nada da arquitetura toca o repo da empresa; ela roda do território dele. Isso deve ser uma **capacidade deliberada e testada**, não um acidente. (Tecnicamente já funciona — eu alcanço qualquer caminho na máquina; o que falta é formalizar como protocolo + garantir que os scripts aceitam `--target-repo <path>` apontando para fora.)

### 3.6. Camada de Apresentação — HTML por etapa + níveis de abstração 🔬 *[amplificação — ideias do Piloto, 2026-05-30]*

Cada etapa do pipeline produz um **artefato HTML visual** — não um markdown cru, um documento bonito e apresentável. A regra: sempre apresentar da mesma forma, padronizado.

- **Scan → HTML** do entendimento da codebase (arquitetura, padrões, mapa visual).
- **Qualidade → HTML** do controle de qualidade: testes, consistência, e **reporte de complexidade de algoritmo** (Big-O, ex: "esta função é O(n log n), tentei baixar para O(n) mas a estrutura não permite") — os detalhes que elevam a qualidade percebida.
- **Teach → HTML** com criatividade visual: desenhos, geometrias, gráficos, diagramas. Reduz o tempo de entendimento, transforma o complexo em fácil.
- **Implementar** — provavelmente dispensa HTML próprio (o PR/código já é isso), mas opcional.

**Atualizáveis e alimentáveis:** quando o Piloto percebe, durante o trabalho, que faltou uma informação no HTML, ele alimenta o template — e aquela informação passa a estar **sempre** lá nas próximas vezes. O HTML evolui com o uso. *"Sem ter ele não tem como ser bonitão."*

**Níveis de abstração configuráveis** 🔬 *(feature de DX/UX, pensando em outros usuários da arquitetura, não só no Piloto)*: o usuário escolhe o nível em que a IA conversa e apresenta — **leigo · iniciante · técnico**. Regula como você quer aprender/entender. Quem não programa entende o que está acontecendo; quem é técnico vê o detalhe. Hoje o teach mode tem 3 níveis fixos (técnico/equipe/aprendizado) — isto generaliza para um *dial de abstração* que atravessa todo o sistema (scan, qualidade, teach), não só o teach. É também o que torna a arquitetura **vendável/ensinável** a terceiros.

**Geração de código bonito** 🔬: "código bonito" = continuar a estética deles + ser imperceptivelmente elegante, curto, apresentável. Não chamar atenção por ser diferente; chamar atenção por ser limpo. O modelo mental é o "Big Dev" — quem usa IA com excelência e entrega ticket após ticket com qualidade que não admite reparo.

### 3.7. Tracks de auto-melhoria 🔬 *[amplificação — ideia do Piloto em Q2]*

Como no MMORPG existe um sistema de *tracks* para sistemas importantes que estão sempre evoluindo, a cognitive-arch deve ter tracks para suas próprias partes mais críticas. Candidatos que eu proponho:

- **Track: Bloco & Fase** — as estruturas mais importantes ("é onde tudo acontece"). Revisitar como são geradas, o que compõem, o que poderiam ter de melhor. O Piloto quer essa revisão — é um track natural.
- **Track: Scanner & Project-Profile** — a base de conhecimento melhora a cada cliente.
- **Track: Qualidade de testes** — testes cada vez mais realísticos, mais precisão, IA confirmando que o código está bom.
- **Track: Pipeline de trabalho** — refinar as etapas conforme o trabalho real revela atrito.

---

## 4. O que muda no que já existe (reuso, não reescrita)

A virada é grande, mas o motor é o mesmo. Mapa do reuso:

| Já existe | Reorientação no modo corporativo |
|-----------|----------------------------------|
| `velocity_inference`, `phase_forecast` | Forecast de entrega de tickets do Piloto |
| `health_model`, `audit` | Saúde do *trabalho* do Piloto (consistência, throughput), não do produto |
| `brainstorm_*` | Intake de ticket e decisões de abordagem |
| `proposal_apply` + guards | Aplicar mudanças no repo-alvo externo com segurança |
| Tiers S/M/L | + **XS** (micro-ticket, gates mínimos) e **XL** (feature robusta, gasta mais) |
| `notification_manager` | Alertas de reunião e prazo |
| `governor.py` (orquestração) | Instâncias paralelas (ver §6) |

---

## 5. Compliance & isolamento (decisão Q3, endurecida)

Inegociável (o Piloto: *"precisa funcionar desse jeito, pela morte de Deus"*):

1. Scripts Python e toda a cognitive-arch ficam **só na máquina local**, em pasta separada. **Nunca** commitados no repo da empresa.
2. No repo do cliente, só entra **o código do ticket** — nada mais.
3. O `project-profile` guarda **metadados de padrão**, não código-fonte do cliente. Disposable a qualquer momento.
4. Operação à distância (§3.5) reforça isso: a arquitetura nunca precisa estar dentro do território deles.

---

## 6. Leitura honesta de realismo (você pediu reto — aqui vai)

Você perguntou: *"dá pra chegar nisso? É realista ou estou ficando maluco?"* Resposta dividida em três baldes.

### 🟢 Realista e ao seu alcance hoje
Scanner profundo + base de conhecimento persistente, motor de consistência, pipeline de trabalho, teach mode, forecast de tickets, operação à distância, entrega rápida com testes. **Nada disso é fantasia.** É extensão direta do que já funciona nos seus projetos. Isso te faz, sim, um profissional muito acima da média — entregando mais, com mais consistência, sabendo explicar tudo. Esse cenário é concreto.

### 🟡 Foco confirmado pelo Piloto (2026-05-30): 100% no ticket
Decisão revisada: **não** vamos fazer "software da empresa em paralelo". O foco no trabalho é **só ticket — infinito, na maior qualidade possível** (que é rápida por causa do jeito de trabalhar, não apesar dele). O trabalho paralelo do Piloto no tempo que sobrar é **o MMORPG dele**, não trabalho não-solicitado da empresa. Isso é estrategicamente mais limpo (zero risco de atravessar o processo do time) e eticamente trivial. O "terminar o software solo e mostrar pro cara" sai de cena como meta de trabalho; vira, no máximo, fantasia de longo prazo sem peso de decisão. **Quanto mais tempo investido na própria arquitetura, mais rápido e melhor fica o código entregue no trabalho E o MMORPG nasce mais rápido** — os dois objetivos se alimentam da mesma ferramenta.

### 🔴 Onde eu te seguro (landmines reais)
- **Ranking de colegas por commits — DECIDIDO: não construir** (Piloto confirmou 2026-05-30: *"está certo, não quero ter imagem ruim"*). No Brasil esbarra em LGPD, em fronteira de RH, e destrói confiança na hora que alguém descobre. O que sobra como legítimo: usar dados de commit para **calibrar as estimativas do próprio Piloto**, agregado e sem nomear ninguém. O scoreboard nomeado está fora — bandeira vermelha fechada.
- **NDA / propriedade intelectual.** Antes de qualquer linha, confirme no contrato o que pode ser processado por ferramenta externa. Mantenha o código deles fora de qualquer arquivo persistente. A base de conhecimento é local e descartável por design — isso já te cobre, mas a verificação do contrato é passo zero.
- **Instâncias paralelas fazendo trabalho "de produto" que ninguém pediu.** Ótimo como exploração sua; arriscado se vira entrega não-solicitada que atravessa o processo do time. Mantenha separado e privado até ter leitura do ambiente.

**Resumo da leitura:** você não está ficando maluco. A máquina de entrega é real e você vai destruir (no bom sentido). O que precisa de cabeça fria é o *timing político* e as *fronteiras éticas/legais* — e é exatamente aí que eu sirvo de contrapeso na simbiose. Você acelera, eu seguro a curva.

---

## 6B. Refinamentos da 2ª rodada de brainstorm (2026-05-30)

Decisões e ideias que o Piloto adicionou depois de ver a visão das fases:

### Bloco & Fase são o coração — e merecem brainstorm próprio
- **O bloco é a estrutura mais importante de todo o sistema.** A qualidade do código entregue vive *dentro* da estrutura do bloco (e da fase). Melhorar o bloco = melhorar tudo.
- Por isso: **dois brainstorms separados** — um para o **design do bloco**, um para o **design da fase**. Cada um gera um documento de design completo. Os **templates de bloco e fase serão refeitos** com base nesses designs. Isso é pré-requisito da Fase 29.

### Tiers por DOIS critérios, não só tamanho
- XS/S/M/L/XL **não** são definidos só pelo tamanho da tarefa — critério muito básico.
- Segundo critério: **nível de importância.** Um ticket pequeno mas importante pode merecer um bloco maior, mais estruturado, gastar mais — para atingir qualidade superior numa tarefa aparentemente simples. Tamanho × Importância = tier.

### Dois modos com sistema de "marca de expansão"
- Confirmado: **modo pessoal/projeto** vs **modo trabalho/corporativo**, possivelmente em agentes separados.
- **Mecanismo de etiquetagem** (analogia de carta de expansão de jogo): tudo que é criado é marcado com sua origem — `corporativo` (exclusivo), `pessoal` (exclusivo), ou `compartilhado` (serve aos dois). Isso torna **trivial arrancar** o modo corporativo inteiro depois, se preciso.
- **Arquivos compartilhados devem ser desacoplados/genéricos** — ferramentas simples que servem às duas linhas. Uma "estante de ferramentas" neutra; algumas features exclusivas de um modo, outras dos dois.
- **Seleção de modo no boot**: a primeira coisa ao abrir é "qual modo? projeto / trabalho". Isso pode **desligar arquivos** (menor leitura/contexto) — mas desligar é desligar, não restitui sozinho fácil.
- A **Fundação (Fase 29) é ramificação compartilhada** — serve aos dois modos. O Scanner também tende a ser compartilhado (ver abaixo).

### Scanner é feature compartilhada, pilotável e dogfoodável
- O scanner **serve aos dois modos** — é praticamente "padrão do software". A pessoa que usa para projeto pessoal também quer scanner. Pode até escanear o **próprio MMORPG**.
- **Pilotável e contextual**: o scanner sempre tem um **input** (você conversa: "quero um scan assim, dessa área"), e **sempre entrega HTML**. Padrão `input → scan → HTML` mantido nos dois modos. Pode escanear um **pedaço** do código em vez de tudo.
- **O scan É um brainstorm**: gera um **dossiê** rico da codebase, com milhares de insights e decisões já tomadas no código. Ler e abstrair **ao mesmo tempo** (mesmo gasto de token: você lê e abstrai vários pontos por arquivo numa passada só — a forma inteligente).
- **Dogfooding**: testar o scanner no MMORPG do Piloto = simular alguém (ou ele) chegando com a arquitetura cognitiva numa codebase real. Simular um ticket (um ticket ≈ uma fase). É **treinamento** para o trabalho real.
- **Decisão Q4 corrigida:** scan macro **profundo uma vez, salvo** (não raso + aprofunda). O macro não muda rápido — escaneia uma vez, salva o dossiê, e depois só acessa os dados salvos. Custo de token **não é problema** para o Piloto (é problema da empresa, e eles vão ver que funciona).

### Pipeline = ciclo Implementar ↔ Qualidade
- **Decisão confirmada (ponto-chave da Fase 31):** não é esteira reta. Implementar = os blocos (roda 1x, "uma lapada"). Qualidade = etapa separada. Quando a Qualidade acha discrepância, **volta para o estado de Implementar** (re-abre bloco). Ciclo: `Implementar(HTML) → Qualidade(HTML) → discrepância? → Implementar(HTML) → ...`
- **HTMLs pequenos** — do tamanho do que precisam dizer. Melhor para visualizar e para leigos.
- **Liga/desliga HTML**: o usuário pode desligar a geração de HTML (deixar tudo no chat). A função continua existindo, só não gera. Boa feature de DX.

### Tracks = prioridade máxima
- As **notificações de track têm que ser absolutas** — zero tolerância a erro. Crítico.
- Tracks são **prioridade máxima, antes de tudo.** Criar a track já e mexer em paralelo.
- **Revisar o que a arquitetura JÁ TEM** — muita coisa já está pronta (chegou antes das fases). Inventário detalhe-por-detalhe do que existe → o que vira track. (Lista entregue separadamente.)
- Trabalho **em paralelo**: um agente cuidando das tracks (brainstorm + melhoria contínua dos sistemas parados) enquanto o trabalho principal corre aqui.

### Níveis de abstração & código bonito (já em §3.6)
- Dial leigo/iniciante/técnico atravessa o sistema. Vendável a terceiros.
- "Código bonito" = continuar a estética deles + imperceptivelmente elegante, curto, apresentável. Modelo: o "Big Dev".

---

## 7. Próximos passos propostos (você pilota)

Ordem de execução definida pelo Piloto (2026-05-30):

**0. Tracks primeiro (prioridade máxima, em paralelo).** Inventariar o que a arquitetura já tem → criar as tracks → soltar um agente paralelo para brainstorm + melhoria contínua dos sistemas. Roda ao lado de tudo o resto.

**1. Fundação (Fase 29) começa pelo design de bloco e fase:**
   - Brainstorm do **bloco** → refazer design do bloco → atualizar template do bloco.
   - Brainstorm da **fase** → refazer design da fase → atualizar template da fase.
   - Depois: hierarquia (agente=cliente), Tiers por tamanho×importância, campos de ticket, estado centrado no Piloto.

**2. Scanner (Fase 30):** brainstorm do scanner → lançar. L0–L4, dossiê persistente, input→scan→HTML, operação à distância, dogfooding no MMORPG.

**3. Pipeline + Consistência (Fase 31):** intake → scan → implementar ↔ qualidade (ciclo) → teach. (Brainstorm pontual onde necessário — ver §7B.)

**4. Forecast, calendário & tracks (Fase 32):** velocity de tickets, escalada de paralelismo, alertas de reunião, sistema de tracks formalizado.

## 7B. Onde cada fase precisa de brainstorm

- **Bloco** → brainstorm dedicado (sim — é o coração).
- **Fase** → brainstorm dedicado (sim).
- **Scanner** → brainstorm dedicado (sim — é um dossiê rico, decisões de o-que-extrair).
- **Pipeline** → brainstorm **leve/pontual**: o fluxo já está desenhado (ciclo implementar↔qualidade); o que precisa de decisão é o **formato do HTML por etapa** e o **dial liga/desliga** — um mini-brainstorm, não um completo.
- **Tracks** → **sem brainstorm** — a IA abstrai o inventário e propõe o que vira track (lista entregue). O Piloto aprova.

---

## 7C. Inventário de Tracks (2026-05-30)

Todas viram track. As não-prontas ficam registradas com prioridade baixa para **não esquecer** — eventualmente serão construídas. O sistema de tracks já existe (`tracks/PRIORITY.md`, `protocols/track-{generation,priority,block-execution}.md`, `templates/track.md`) — só precisa ser **adaptado**: o benchmark de um sistema de arquitetura não é latência em ms, é **qualidade/robustez/consistência** (ex.: taxa de retrabalho, consistência entre blocos, cobertura de caminho de erro).

| # | Track | Módulos / origem | Pronto? | user_priority | Nota |
|---|-------|------------------|---------|---------------|------|
| 1 | **Bloco & Fase** | block_start, block_close, phase_manager, state_manager, board_manager | ✅ | 10 | Redesign acontece na **sessão principal**, NÃO no agente de track |
| 2 | **Orquestração & Paralelismo** | governor, dispatch, task_packet, integration, return_validator | ✅ | 8 | **CURRENT FOCUS do agente paralelo** — começa por aqui |
| 3 | **Confiabilidade & Notificações** | notification_manager, audit, integrity_check, invariant_check | ✅ | 8 | Notificações de track devem ser **absolutas** (zero erro) |
| 4 | **Forecast & Pilotagem** | velocity_inference, phase_forecast, risk_forecast | ✅ | 6 | Reorientar para tickets do Piloto |
| 5 | **UX & Dial de Abstração** | ux_validator, ux-config.yaml, ux-voice.md | ✅ | 6 | Níveis leigo/iniciante/técnico |
| 6 | **Motor de Brainstorm** | brainstorm_context/predictor/synthesis | ✅ | 5 | Já em uso |
| 7 | **Auto-reparo de Propostas** | proposal_apply, proposal_resolver, protocol_updater | ✅ | 5 | Guards + rollback (fase 27) |
| 8 | **Mineração de Padrões** | pattern_analyzer, recommendation_engine, retro_signals | ✅ | 5 | |
| 9 | **Master Agent** | master_scheduler, master_suggest | ✅ | 4 | Proatividade |
| 10 | **ADR Drafter** | adr_drafter | ✅ | 4 | |
| 11 | **Briefing pós-pausa** | briefing_generator | ✅ | 3 | |
| 12 | **Dashboard & Relatórios** | dashboard_generator, weekly_report | ✅ | 3 | |
| 13 | **Token Tracker** | token_tracker | ✅ | 3 | Token não é gargalo no corporativo |
| 14 | **Fundação Corporativa** | *fase 29 (compartilhada)* | 🔧 em design | 7 | Marcador meta — a ramificação que serve aos dois modos |
| 15 | **Scanner & Dossiê** | *novo (fase 30)* | ❌ | 2 | Lá embaixo — não existe ainda, eventualmente sobe |
| 16 | **Pipeline de Qualidade** | *novo (fase 31)* | ❌ | 2 | Lá embaixo — não existe ainda, eventualmente sobe |

**Divisão de trabalho:** o **agente paralelo** cuida das tracks dos sistemas prontos (começa pela #2 Orquestração). O **redesign de Bloco & Fase (#1) fica na sessão principal** com o Piloto. Scanner (#15) e Qualidade (#16) são construídos nas fases 30/31, não na track.

---

## 8. Out of scope (registrado, não esquecido)

- Operator handbook (ensinar terceiros a operar a IA) — futuro, depois da fundação.
- Integração com Jira/Linear API — intake lê texto livre por enquanto.
- Análise semântica de lógica de negócio — fica com o humano.
- Ranking nomeado de colegas — bandeira vermelha, não construir (§6).
- Deploy/PR automático no repo da empresa sem revisão do Piloto.

---

*Gerado por Brainstorm v2 (protocols/brainstorm-pattern-v2.md) + síntese de chat.
Revisar antes de commitar. As fases 29–32 derivam deste documento.*
