# Brainstorm: Scanner de Codebase — Design Decisions

status: decisions-confirmed
created_at: 2026-05-31
confirmed_at: 2026-05-31
author: AI (design session) + Piloto (confirmed 2026-05-31)
synthesis_target: design/scanner.md
topic: design detalhado do scanner L0–L4, project-profile, HTML, operação à distância, dogfooding

---

## Context

Phase 28 está completa (1067 testes, audit 92/100). A virada de norte de 2026-05-30 transformou o
objetivo da arquitetura: o Piloto vai trabalhar na Visagio recebendo tickets isolados em codebases
que não são seus. O scanner é a **fundação de tudo** no modo corporativo — sem ele, não há
"padrão do projeto", não há consistência, não há código que parece escrito pelo time.

O scanner também é **feature compartilhada**: serve ao modo pessoal (dogfood no MMORPG) e ao modo
corporativo. O design/corporate-mode.md (approved) define os princípios. Este documento define
as decisões de implementação antes de qualquer código.

---

## O que já está decidido (não são perguntas abertas)

Estas decisões foram fechadas em design/corporate-mode.md e não serão reabertas aqui:

| Decisão | Resolução |
|---------|-----------|
| Escopo | Feature compartilhada — modo pessoal + corporativo |
| Padrão de operação | `input → scan → HTML` obrigatório |
| L0 macro | Scan profundo UMA vez, salvo — macro não muda rápido |
| L2/L3 | Sob demanda, direcionado pela área do ticket |
| Saída | `governance/project-profile-<cliente>.md` (metadados, nunca código real) |
| Isolamento | Scripts só na máquina local; opera à distância do repo da empresa |
| Filosofia | O scan É um brainstorm: lê e abstrai na mesma passada |
| HTML | Liga/desliga disponível ao usuário |

---

## Core model

### Situação atual (sem scanner)
```
Piloto entra num projeto → lê arquivos aleatoriamente → tenta inferir padrões manualmente
→ gera código que pode ou não seguir o estilo do time → retrabalho ou aprovação incerta
```

### Modelo-alvo (com scanner)
```
Piloto entra num projeto
  → Scanner L0+L1 (onboarding, uma vez, salvo)
  → project-profile-<cliente>.md criado
  → HTML do dossiê gerado
→ Piloto recebe ticket
  → Scanner L2+L3 (scan parcial, área do ticket)
  → project-profile atualizado com padrões locais
  → HTML atualizado
→ Implementar com código no padrão exato do projeto
  → Motor de consistência valida antes da entrega
```

Propriedades do modelo-alvo:
- Scanner é o **único produtor do project-profile** — nenhum outro módulo escreve nele
- Sub-scans (L2/L3) enriquecem o perfil sem apagar o que L0/L1 já detectou
- HTML é a representação visual do perfil — gerado a cada scan, atualizável
- Operação à distância: scanner recebe `--target-repo <path>` e nunca precisa estar dentro do repo do cliente

---

## Decision 1 — Interface de entrada: como o Piloto aciona o scanner?

**Problema:** O scanner precisa de pelo menos um parâmetro mínimo para rodar (qual projeto, qual nível).
Mas há decisões mais ricas a fazer: qual área do código focar, qual o objetivo do scan, o que o Piloto
já sabe do projeto. Como capturar isso sem criar fricção desnecessária?

### Option A — CLI puro (flags obrigatórias)
```
python codebase_scanner.py --target-repo ../empresa --level L1
```
- Simples, previsível, scriptável
- Sem contexto adicional — scanner age cegamente
- O Piloto não tem como dizer "foca na autenticação" sem um flag específico

### Option B — Conversa guiada (scanner pergunta antes de rodar)
- Scanner faz perguntas: "qual é o objetivo? qual área?" antes de executar
- Mais contextual, mais rico
- Adiciona latência e fricção a scans rotineiros (L2/L3 por ticket são frequentes)

### Option C — Híbrido: CLI + `--context` opcional *(recommended)*
```
# Scan mínimo (onboarding automático)
python codebase_scanner.py --target-repo ../empresa --level L1

# Scan dirigido (antes de ticket específico)
python codebase_scanner.py --target-repo ../empresa --level L2 \
  --context "ticket: implementar refresh de JWT; área provável: src/auth"
```
- `--context` é texto livre — o Piloto pode dizer qualquer coisa
- Com `--context`, o scanner orienta o que ler e o que destacar no HTML
- Sem `--context`, funciona com defaults sensatos
- Compatible com a CLI especificada nos exit criteria da phase-29.md

**Recommendation: Option C.** O `--context` é a implementação do "sempre tem um input (você conversa)"
do design §6B sem romper a CLI. Scans automáticos não precisam de contexto; scans dirigidos se beneficiam.

---

## Decision 2 — Profundidade do dossiê: rico ou mínimo por padrão?

**Problema:** O design diz "lê e abstrai ao mesmo tempo" — mas há dois cenários muito diferentes:
o onboarding (custo aceito, faz uma vez) e o scan por ticket (frequente, custo importa).
Dois comportamentos diferentes ou um comportamento único?

### Option A — Dossiê rico sempre
- Cada scan gera insights detalhados: padrões, decisões arquiteturais, sugestões
- Custo de token alto a cada scan parcial (um por ticket = várias vezes por dia)
- Mais valor por scan, mais custo operacional

### Option B — Dossiê mínimo sempre
- Scanner extrai estrutura básica, Piloto pede mais se quiser
- Scan por ticket é rápido e barato
- Perde o valor do "brainstorm" que o design §6B descreve

### Option C — Diferenciado por tipo: rico no macro, mínimo no parcial *(recommended)*
- **Onboarding (L0+L1):** dossiê rico — custo de token aceito explicitamente, acontece uma vez.
  O macro não muda rápido; vale investir na leitura profunda inicial.
- **Scan por ticket (L2/L3):** dossiê focado — extrai só o necessário para a área do ticket.
  Rotineiro; custo acumulado importa.
- Controlado pelo nível passado: `--level L1` → rico; `--level L2 --area src/auth` → focado

**Recommendation: Option C.** Alinha com a decisão Q4 corrigida do design §6B:
"scan macro profundo uma vez, salvo". O comportamento de onboarding e o de scan por ticket
têm filosofias diferentes — faz sentido implementar diferente.

---

## Decision 3 — L0: o que o scan macro arquitetural detecta?

**Problema:** L0 é o scan mais alto nível — "entender o tipo de mundo antes de mergulhar".
Mas o que especificamente isso significa em termos de dados que o scanner extrai e persiste?

### Option A — Mínimo (tipo + linguagens)
- Tipo de sistema (web, embarcado, serverless, monolito, microsserviços)
- Linguagens presentes
- Entry points
- Lê: `package.json`, `pom.xml`, `go.mod`, `Makefile`, `docker-compose.yml` — só o óbvio
- Custo: 5–10 arquivos

### Option B — Standard *(recommended)*
- Tudo do Option A +
- Stack principal (framework, runtime, versões)
- Infra declarativa (Docker/k8s, CI/CD pipeline, cloud provider se declarado)
- Build system (webpack, vite, gradle, cargo...)
- Lê: arquivos de configuração de infra e build, nunca código de lógica
- Custo: 15–25 arquivos

### Option C — Extended (inclui análise de equipe)
- Tudo do Option B +
- Análise de commits para inferir tamanho e ritmo de equipe
- Contribuidores ativos, frequência de push
- **Bandeira vermelha LGPD confirmada** (design §6 landmines) — cria risco de ranking de pessoas
- Custo: alto + risco legal

**Recommendation: Option B (Standard).** O design §3.1 lista explicitamente tipo de sistema + infra.
Option C está descartado pela decisão de não rankear equipe (design §6, confirmado pelo Piloto).
Option A é pouco — infra declarativa (Docker, k8s) é informação crítica para entender o "tipo de mundo"
num contexto de consultoria (Visagio), onde o Piloto vai encontrar de tudo.

---

> **PILOTO (2026-05-31):** Não é a B. É B + lógica de negócio. Leitura macro é uma vez, custo aceito.
> "Eu preciso entender como funciona também." O Piloto quer entender a lógica do negócio implementada
> no código, não só a estrutura. Análise de equipe ainda está fora (LGPD).
>
> **DECISÃO FINAL — Option B+:** Standard completo + leitura de lógica de negócio (como funciona o
> domínio, fluxos principais, entidades centrais). Leitura única, profunda, sem limite artificial de
> arquivos de lógica. O custo de token é aceito explicitamente para o onboarding macro.

---

## Decision 4 — L2: como detectar padrões de arquitetura de software?

**Problema:** Clean Architecture, DDD, Hexagonal, MVC, Feature-Sliced, CQRS... O scanner precisa
identificar qual está em uso num codebase desconhecido. Como fazer isso de forma confiável?

### Option A — Só análise de estrutura de pastas
- Detecta padrões pelos nomes de diretórios:
  `domain/`, `application/`, `infrastructure/` → Clean Arch
  `features/`, `shared/`, `entities/` → Feature-Sliced
  `controllers/`, `models/`, `views/` → MVC
- Rápido, sem custo de leitura de código
- Cobre ~80% dos projetos que seguem convenção de pasta
- Falha em projetos sem convenção clara ou com estrutura customizada

### Option B — Claude lê arquivos-chave e infere
- Scanner lista arquivos candidatos (index.ts, app.ts, main.go, etc.) e os lê
- Claude infere o padrão pelo que vê no código
- Mais preciso para projetos com estrutura não-convencional
- Custo: 10–20 arquivos de lógica por scan L2

### Option C — Checklist de sinais + Claude infere o restante *(recommended)*
- Fase 1: checklist de sinais estruturais (nomes de pasta/arquivo)
  → identifica o padrão em ~80% dos casos diretamente
- Fase 2 (só se checklist for inconclusivo): Claude lê 5–10 arquivos-chave
  → resolve os 20% restantes
- Hybrid que maximiza velocidade no caso comum e precisão nos casos difíceis

### Option D — Piloto indica qual padrão está em uso
- Scanner lista as opções, Piloto escolhe
- Rápido, sem risco de erro
- Perde o ponto central do scanner: reduzir o que o Piloto precisa fazer manualmente

**Recommendation: Option C.** O checklist de sinais é o default; leitura de arquivos é o fallback.
Isso garante que um scan L2 num projeto TypeScript/React com Feature-Sliced seja resolvido
em segundos pelo checklist, sem custo de leitura — e que um projeto com estrutura custom ainda
seja identificado corretamente via leitura.

---

> **PILOTO (2026-05-31):** ✅ Option C. Adição importante: o HTML do scan deve incluir um
> **"estado de prova"** — a IA mostra COMO chegou às conclusões (por que inferiu Clean Architecture,
> por exemplo). Isso permite ao Piloto validar se o raciocínio está correto antes de usar o perfil.
> "Como que ela chegou nessa conclusão?" — o HTML tem que responder essa pergunta.
>
> **DECISÃO FINAL — Option C + prova de raciocínio no HTML:**
> Checklist + Claude infere + HTML inclui seção de raciocínio ("como chegamos a cada inferência").

---

## Decision 5 — L4: como classificar padrão "vigente" vs. "legado tolerado"?

**Problema:** O design §3.1 distingue vigente (a replicar) vs. legado (não tocar, não replicar).
Em codebases reais, coexistem padrões de épocas diferentes. Como detectar qual é qual?

### Option A — Frequência (padrão mais comum = vigente)
- Conta ocorrências de cada padrão (ex: quantos arquivos usam Redux vs. Zustand)
- O mais frequente é o vigente
- Falha em projetos em migração onde o legado ainda domina numericamente

### Option B — Recência (arquivo mais novo = padrão vigente)
- Lê timestamps de criação/modificação dos arquivos
- O padrão dos arquivos mais recentes é o vigente
- Pode ser enganado por arquivos de teste antigos não migrados ainda

### Option C — Score combinado frequência × recência *(recommended)*
- Para cada padrão detectado: `score = frequência_normalizada × peso_recência`
- Padrões em arquivos novos E numerosos → vigente
- Padrões em arquivos antigos com ocorrências decaindo → legado
- Override manual: Piloto pode corrigir via `--context "padrão vigente é Zustand, não Redux"`

### Option D — Piloto classifica sempre
- Scanner lista os padrões encontrados com contagens, Piloto decide qual é vigente
- Zero risco de erro de classificação
- Adiciona passo manual em todo onboarding

**Recommendation: Option C.** Score combinado é mais robusto que qualquer critério único.
O override via `--context` (Decision 1, Option C) dá ao Piloto controle quando o auto-detect
erra — que é inevitável em projetos de migração ativos. Option D é safe mas derrota o objetivo
de autonomia do scanner.

---

## Decision 6 — Estrutura do project-profile: como organizar o arquivo?

**Problema:** `governance/project-profile-<cliente>.md` é o artefato central de persistência.
Precisa ser: (a) legível por humano, (b) atualizável por nível sem reescrever tudo,
(c) rastreável no tempo (quando cada seção foi escaneada).

### Option A — Flat MD, arquivo único simples
- Uma seção por nível (## L0, ## L1, etc.)
- Rescan reescreve o arquivo inteiro
- Mais simples; mais difícil de atualizar parcialmente

### Option B — Flat MD com seções por nível + timestamp por seção *(recommended)*
```markdown
## L0 — Macro arquitetural
_scanned_at: 2026-05-31T10:00Z_

tipo: web · framework: Next.js · infra: Vercel + Supabase

## L1 — Estrutura & linguagens
_scanned_at: 2026-05-31T10:05Z_

linguagens: TypeScript (90%), CSS (10%)
...

## L2 — Padrões de arquitetura (área: src/auth)
_scanned_at: 2026-05-31T14:30Z_

padrão: Feature-Sliced Design
...
```
- Cada seção tem seu próprio `scanned_at`
- `--refresh-level L2` atualiza só a seção L2 sem tocar L0/L1
- Consistente com o padrão de `governance/` (patterns.md, known-drift.md)
- Legível por humano e pelo scanner em sessões futuras

### Option C — Arquivos separados por nível
- `project-profile-<cliente>-L0.md`, `project-profile-<cliente>-L1.md`, etc.
- Fácil de atualizar individualmente
- Fragmenta o perfil — o Piloto precisa abrir múltiplos arquivos para ter visão completa
- Multiplica entradas no INDEX.md

### Option D — YAML estruturado
- Mais fácil de parsear por scripts Python
- Menos legível diretamente
- Quebra o padrão de governança em MD do projeto

**Recommendation: Option B.** Timestamp por seção resolve o problema de rescan parcial sem
fragmentar o arquivo. MD é consistente com o resto da governance/ e é legível diretamente
pelo Piloto. Scripts Python leem MD sem dificuldade.

---

> **PILOTO (2026-05-31):** Levantou a questão correta: "se L0/L1 não são relevantes para L2,
> arquivos separados reduzem contexto; se são, flat MD é melhor."
>
> **AI resolve (2026-05-31):** L1 (estrutura de pastas) É sempre necessária para L2/L3 —
> o scanner precisa saber onde estão os arquivos para saber onde ir. L0 também orienta o contexto
> ("esse é um projeto Next.js/Vercel" muda o que esperar em L2). E o perfil contém só metadados
> (sem código real) — uma seção L0 tem ~20–30 linhas. Custo de leitura mínimo.
>
> **DECISÃO FINAL — Option B:** Flat MD com seções + timestamps por seção.

---

## Decision 7 — Rescan: quando atualizar vs. usar o cache?

**Problema:** O macro (L0) foi decidido como "uma vez, salvo". Mas L3 (estilo de código)
pode mudar se o time adotar uma nova convenção. Como o scanner decide o que re-escanear?

### Option A — Rescan total sempre
- Toda chamada ao scanner reescaneia todos os níveis
- Sempre fresco; nunca dados desatualizados
- Custo de token alto — inviável para scans por ticket (frequentes)

### Option B — Nunca sem flag explícita
- Scanner usa o cache por padrão
- `--refresh` ou `--refresh-level <nível>` para atualizar
- Mais manual, mas previsível e barato

### Option C — `--refresh-level <L0|L1|L2|L3|L4>` como interface de controle *(recommended)*
- Default: usa cache para todos os níveis com `scanned_at` presente
- `--level L2` numa área nova **adiciona** ao perfil (não sobrescreve L0/L1)
- `--refresh-level L3` re-escaneia e substitui só a seção L3
- Piloto controla o que re-escanear; scanner nunca descarta dados sem instrução explícita

### Option D — Auto-detect via git diff
- Scanner verifica `git log --since=<last_scanned_at>` para detectar mudanças
- Re-escaneia áreas com commits desde o último scan
- Mais inteligente, mais dependência de estado do git do cliente
- Adiciona complexidade; pode falhar em repos sem histórico limpo

**Recommendation: Option C.** Controle granular por nível é o mais flexível e previsível.
A decisão Q4 corrigida do design §6B confirma: "escaneia uma vez, salva, e depois só acessa
os dados salvos". Option D (auto-detect via git) é elegante mas cria dependência de estado
externo que pode não estar disponível em todo contexto corporativo.

---

## Decision 8 — Scan parcial por ticket: como o scanner sabe onde ir?

**Problema:** Para L2/L3, o scan é dirigido pela área do ticket. Mas como o scanner determina
qual pasta/módulo escanear quando o Piloto passa um ticket em texto livre?

### Option A — `--area <path>` explícito
```
python codebase_scanner.py --level L2 --area src/auth
```
- Piloto indica a pasta exata
- Mais preciso, zero risco de inferência errada
- Adiciona passo manual: Piloto precisa saber a estrutura do projeto antes do scan
  (mas com L1 no cache, o mapa de pastas já está disponível — esse custo é baixo)

### Option B — `--ticket <text>` com inferência *(recommended)*
```
python codebase_scanner.py --level L2 \
  --ticket "implementar refresh de JWT e expiração de sessão"
```
- Scanner usa L1 (estrutura de pastas já no cache) para inferir `src/auth/**` como área provável
- Confirma com o Piloto antes de rodar o scan: "inferi que o ticket afeta src/auth — confirma?"
- Se inferência estiver errada, Piloto corrige antes de gastar tokens em scan da área errada

### Option C — Automático via branch diff
- Scanner detecta arquivos no branch atual vs. main e escaneia a área modificada
- Zero input do Piloto
- Só funciona quando o Piloto já começou a modificar arquivos (scan antes de implementar perde)

### Option D — Integrado ao ticket intake (scan como etapa do pipeline)
- `ticket_intake.py` chama o scanner automaticamente como etapa interna
- Do ponto de vista do Piloto, é transparente — dá o ticket, recebe o scan
- Acoplamento entre módulos: intake depende do scanner
- Mais difícil de testar os dois separadamente

**Recommendation: Option B.** O `--ticket` com inferência é a interface mais natural para o
fluxo real: o Piloto tem o texto do ticket no clipboard ou no terminal. A confirmação antes
de rodar mantém o Piloto no controle (padrão do design: "Piloto sempre dá go/no-go").
Option D é interessante como evolução futura — mas o acoplamento complica o desenvolvimento
inicial e viola a independência dos módulos da phase-29.

---

> **PILOTO (2026-05-31):** ✅ Option B. Rejeitou D explicitamente com argumento claro:
> "O scanner tem que ser uma etapa separada. O Piloto precisa ver o HTML, validar, e SÓ ENTÃO
> passar para frente. Se integrar com o intake, o Piloto nunca vê o HTML antes de avançar."
> Isso é design de UX intencional: scanner → HTML → Piloto valida → intake. Não pipeline automático.

---

## Decision 9 — HTML: o que o output visual deve conter?

**Problema:** O design confirma que o scanner sempre entrega HTML. Mas o que está nesse HTML?
"Arquitetura, padrões, mapa visual" é o que o design §3.6 diz — mas qual é o conteúdo concreto
e como é organizado visualmente?

### Option A — Mínimo: mapa de estrutura
- Árvore de diretórios com anotações de tipo (componentes, services, models)
- Rápido de gerar, fácil de renderizar
- Não entrega os padrões detectados — perde o valor central do L2/L3

### Option B — Standard: mapa + padrões *(recommended)*
- **Seção 1 — Mapa arquitetural:** árvore de diretórios com labels de tipo + diagrama
  de camadas se Clean Arch/DDD detectado (Mermaid ou ASCII art)
- **Seção 2 — Padrões detectados por nível:** L0 stack, L2 arquitetura de software,
  L3 estilo/convenções, L4 vigente vs. legado (com exemplos de nomes, não código)
- **Seção 3 — Flags de atenção:** coexistências L4 detectadas, áreas não escaneadas,
  dependências externas críticas encontradas
- Tamanho: compacto — "HTML pequenos, do tamanho do que precisam dizer" (design §6B)

### Option C — Full dossiê
- Tudo do Standard +
- Timeline de mudanças por área
- Grafo de dependências entre módulos
- Análise de complexidade estimada por arquivo
- Sugestões proativas de melhoria
- Mais rico, mais tempo para gerar, mais difícil de consumir rapidamente

**Recommendation: Option B (Standard).** O design §6B diz explicitamente "HTMLs pequenos —
do tamanho do que precisam dizer". Full dossiê pode ser uma evolução, mas a Seção 3 (flags)
é inegociável: o Piloto precisa saber o que o scanner NÃO viu tão importante quanto o que viu.
Mermaid para diagramas de arquitetura é nativo no HTML e fácil de gerar a partir das inferências
do L2.

---

> **PILOTO (2026-05-31):** Não é B. É Full dossiê em todos os níveis — mas com nuance:
> "Full dossiê de uma área específica já vai ser pequeno por natureza."
> O conteúdo é completo; o tamanho é proporcional à área coberta.
> Grafo de dependências entre módulos é obrigatório — "parece muito importante pra mim saber."
>
> Sobre token: "aqui no corporativo não é hora de perder qualidade pra reduzir token.
> Prefiro ter mais qualidade do que custo de token menor."
>
> **DECISÃO FINAL:**
> - L0+L1 (onboarding): Full dossiê completo — robusto, gerado uma vez.
> - L2/L3 (scan por ticket): Full dossiê da área — completo, mas naturalmente menor.
> - Grafo de dependências: obrigatório em todos os níveis.
> - Seção "como chegamos a esta conclusão": obrigatória (derivada da Decision 4).
> - Custo de token aceito; qualidade não é negociável.

---

## Decision 10 — HTML default: ligado ou desligado?

**Problema:** O design confirma que o usuário pode desligar o HTML. Mas qual é o comportamento
padrão quando nenhuma flag é passada?

### Option A — Default OFF
- HTML só gerado se `--html` for passado explicitamente
- Mais seguro para testes iniciais; menos outputs inesperados
- Vai contra o design §3.6: "Sem ter ele não tem como ser bonitão" — o HTML É o output principal

### Option B — Default ON, sem configuração
- Scanner sempre gera HTML
- Consistente com o design
- Sem como desligar permanentemente sem alterar o código

### Option C — Default ON, configurável em `ux-config.yaml` *(recommended)*
- `ux-config.yaml` já existe como ponto de configuração de preferências de apresentação
- Scanner lê `html_output: true/false` no ux-config.yaml
- Default no ux-config.yaml: `true`
- Não inventa novo arquivo de configuração — reusa o que existe

**Recommendation: Option C.** Consistente com o design ("forma padrão = HTML") e com a
infraestrutura existente (ux-config.yaml). O flag `--no-html` pode também existir como
override de linha de comando para casos pontuais.

---

## Decision 11 — Projetos grandes: estratégia para codebases com 500+ arquivos?

**Problema:** O invariante da phase-29 é "≤50 arquivos por nível sem permissão explícita".
Mas projetos corporativos reais têm facilmente 2000–10000 arquivos.
O scanner não pode ignorar isso silenciosamente nem travar.

### Option A — Limite duro: para em N arquivos
- Scanner lê no máximo N arquivos por nível
- Avisa o Piloto e para
- Simples, previsível
- Pode deixar partes críticas do projeto não escaneadas sem explicação adequada

### Option B — Sampling inteligente por tipo
- Scanner amostra N arquivos mais representativos por tipo/pasta
- Prioriza: entry points, index files, arquivos com mais imports, arquivos mais referenciados
- Mais preciso que limite duro para codebases grandes
- Algoritmo de sampling adiciona complexidade

### Option C — Scan hierárquico + respeita .gitignore *(recommended)*
- Scanner começa pelos roots (entry points, index files, arquivos de configuração)
- Desce hierarquicamente até atingir o limite de N arquivos, priorizando pastas por relevância
- Respeita `.gitignore` por padrão: elimina `node_modules/`, `dist/`, `build/`, `coverage/`
  sem custo adicional (esses diretórios somam sozinhos 90% dos arquivos na maioria dos repos)
- Após o scan: emite relatório explícito de o que foi coberto vs. o que foi excluído
  — NUNCA silencioso

### Option D — Piloto configura exclusões antes de rodar
- Scanner pede (ou lê de config) uma lista de exclusões customizada
- Máxima flexibilidade
- Adiciona setup por projeto — fricção no onboarding

**Recommendation: Option C.** `.gitignore` já existe no projeto e resolve a maioria dos casos
de volume. Scan hierárquico garante cobertura do que importa. O relatório de exclusões é
inegociável — silent truncation (o scanner fez menos do que o Piloto pensa) é o pior resultado.
`--expand-limit N` como flag explícita para superar o limite padrão é complemento útil.

---

> **PILOTO (2026-05-31):** Nenhuma das opções diretamente. A abordagem correta é **adaptativa**:
> 1. Antes de escanear: contar arquivos, estimar custo, perguntar ao Piloto se vale a pena.
> 2. Se o projeto for grande demais para ler tudo: apresentar opções (pular lógica de negócio,
>    amostrar, etc.) — não decidir sozinho.
> 3. O scanner deve ser **adaptável ao tamanho da codebase**.
> 4. Medição de custo de token é OBRIGATÓRIA no scan — o Piloto precisa saber quanto gastou.
>
> **DECISÃO FINAL — Option E (Adaptive):**
> - Fase 0 (pré-scan): inventário rápido (conta arquivos, estima custo em tokens).
> - Se dentro do limite: scan completo incluindo lógica de negócio.
> - Se acima do limite: reporta ao Piloto com opções adaptadas ao tamanho
>   (ex: "projeto tem 3.000 arquivos — scan completo custa ~X tokens. Opções: A, B, C").
> - Scanner **nunca decide sozinho** quando o custo é alto.
> - Medição de custo de token obrigatória: emite relatório de custo após cada scan.
> - `.gitignore` respeitado por padrão em qualquer modo.

---

## Decision 12 — Dogfooding: onde testar o scanner primeiro?

**Problema:** Antes de usar em cliente real (Visagio), o scanner precisa ser validado num
ambiente controlado. Mas qual codebase usar e em que sequência?

### Option A — MMORPG direto
- Projeto familiar — Piloto sabe o que o scanner "deveria" encontrar (valida qualidade)
- Grande e complexo — stress test real (TypeScript + servidor + múltiplos sub-repos)
- Risco: se o scanner tem bugs, é mais difícil isolar no projeto grande

### Option B — Fixture TypeScript/React pequeno + MMORPG *(recommended)*
- **Fase 1 — Fixture:** repositório TypeScript/React simples (criado ou clonado do GitHub)
  com padrão conhecido (ex: Next.js com Feature-Sliced)
  → Valida que a pipeline funciona sem surpresas
  → Fácil de debugar quando algo falha
  → Produz `project-profile-fixture.md` que serve como exemplo de output
- **Fase 2 — MMORPG:** dogfood real no projeto do Piloto
  → Piloto sabe o que esperar → pode validar a qualidade da inferência
  → Simula o cenário corporativo ("chegando numa codebase com a arquitetura cognitiva")
  → "Um ticket ≈ uma fase" do MMORPG: simular ticket de lore ou combat feature

### Option C — Dois projetos em paralelo (dois agentes)
- Fixture + MMORPG simultaneamente, comparar resultados
- Mais informação por rodada de teste
- Mais difícil de coordenar e interpretar divergências

**Recommendation: Option B.** Fixture primeiro dá uma baseline limpa. MMORPG depois é o
"stress test com oráculo" — o Piloto sabe o que o scanner deveria encontrar e pode avaliar
a qualidade. O design §6B confirma o dogfood no MMORPG como "treinamento para o trabalho real".

---

## Open questions (não decididas aqui)

1. **Custo real de tokens por nível:** não temos dados empíricos de quantos tokens um L1
   (50 arquivos, primeiras 20 linhas cada) ou um L2 (área específica) consomem na prática.
   Isso vai calibrar os limites. Resposta: medir na primeira rodada de dogfood (fixture).

2. **Múltiplos projetos simultâneos:** `project-profile-<cliente>.md` permite múltiplos clientes.
   Mas como o scanner sabe qual perfil usar numa sessão com múltiplos clientes ativos?
   Proposta: `--client <nome>` flag explícito; sem default quando há múltiplos perfis.

3. **Integração com consistency_checker.py:** o checker usa o project-profile como input.
   A interface entre scanner e checker precisa ser definida (qual seção, qual formato exato
   o checker espera). Isso é design da phase-29, block-163 — fora do escopo do scanner em si.

4. **Linguagens desconhecidas:** o scanner vai encontrar linguagens que nunca viu
   (Terraform, Bicep, SQL dialetos específicos, DSLs internas). Como graceful-degrade?
   Proposta: L0/L1 funcionam em qualquer linguagem (estrutura de arquivos é universal);
   L2/L3 fazem best-effort com aviso "linguagem não reconhecida para padrão de código".

5. **Frequência de atualização do HTML:** o HTML é gerado a cada scan. Mas se o Piloto
   faz dois scans L2 em áreas diferentes, os HTMLs se acumulam ou o novo substitui o antigo?
   Proposta: `governance/scanner-output-<cliente>-<timestamp>.html` — acumula.
   Um link para o mais recente em `project-profile-<cliente>.md`.

---

## Confirmed decisions (Piloto 2026-05-31)

| # | Decisão | Escolha | Nota |
|---|---------|---------|------|
| 1 | Interface de entrada | **C — Híbrido** | CLI + `--context` opcional |
| 2 | Profundidade do dossiê | **C — Diferenciado** | Rico no macro, focado no parcial |
| 3 | L0 — o que detectar | **B+ — Standard + lógica de negócio** | Sem análise de equipe; leitura única profunda aceita |
| 4 | L2 — detecção de padrões | **C + prova de raciocínio** | Checklist + Claude infere + HTML mostra "como chegamos aqui" |
| 5 | L4 — vigente vs. legado | **C — Score combinado** | Frequência × recência + override do Piloto |
| 6 | Estrutura do project-profile | **B — Flat MD + timestamps** | AI resolve: L1 sempre necessária para L2 context |
| 7 | Rescan — granularidade | **C — `--refresh-level`** | Piloto controla o que re-escanear |
| 8 | Scan parcial por ticket | **B — `--ticket` com inferência** | Scanner é etapa separada; Piloto vê HTML antes do intake |
| 9 | HTML — conteúdo | **Full dossiê em todos os níveis** | Grafo de dependências obrigatório; tamanho proporcional à área |
| 10 | HTML — default | **C — Default ON** | Configurável em `ux-config.yaml` |
| 11 | Projetos grandes | **E — Adaptive** | Pré-scan assessment → estimativa de custo → Piloto decide |
| 12 | Dogfooding | **B — Fixture + MMORPG** | Medição de custo obrigatória desde o início |

## Cross-cutting decisions (confirmadas pelo Piloto 2026-05-31)

| Tema | Decisão |
|------|---------|
| **Custo de token** | Medição obrigatória em TUDO no corporativo. Scanner reporta custo após cada execução. |
| **Qualidade vs. token** | Qualidade não é negociável; custo de token aceito enquanto cliente não reclamar. |
| **Múltiplos projetos** | Gerenciados via agentes/arquiteturas separadas. Nome da arquitetura identifica o projeto. |
| **Consistency checker interface** | AI propõe interface; Piloto finaliza no bloco do checker (phase-29 block-163). |
| **Linguagens desconhecidas** | AI recommendation: graceful degrade. L0/L1 universais; L2/L3 best-effort com aviso. |
| **Acumulação de HTMLs** | `governance/scanner-output-<cliente>-<timestamp>.html`. Link para o mais recente no project-profile. |

## Recommended synthesis

Próximo passo confirmado: gerar `design/scanner.md` + `phases/phase-30.md` com base nestas decisões.

- `design/scanner.md` — design doc completo do scanner (síntese deste brainstorm)
- `phases/phase-30.md` — fase com blocos concretos derivados das decisões
- `manifests/block-162-codebase-scanner.md` — atualizar com as decisões finais

End of brainstorm.
