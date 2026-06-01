# Design: Scanner de Codebase

status: approved
created_at: 2026-05-31
authors: Thaillon (Piloto) + AI (brainstorm session 2026-05-31)
synthesis_source: `_brainstorm/scanner-v2-redesign.md` (all 12 decisions confirmed 2026-05-31)
phase: phase-30
supersedes: phases/phase-29.md block-162 (original single-block plan)

---

## 0. O que é o Scanner

O scanner é a **fundação do modo corporativo** — e feature compartilhada com o modo pessoal.
Antes de qualquer implementação num codebase desconhecido, o scanner entende o projeto em
profundidade e persiste esse entendimento num perfil. Sem perfil, não há padrão, não há
consistência, não há código que parece escrito pelo mesmo time.

**Filosofia central:** o scan é um brainstorm. Não é uma listagem de arquivos — é leitura e
abstração simultâneas. Numa única passada, o scanner lê o código e extrai significado: arquitetura,
padrões, estilo, coexistências, lógica de domínio. O custo de token de uma leitura profunda é aceito
porque a leitura acontece uma vez e o conhecimento persiste para sempre.

**Propriedades:**
- Feature compartilhada (modo pessoal + corporativo)
- Padrão `input → scan → HTML` obrigatório
- Etapa independente no pipeline: scanner produz HTML → Piloto valida → DEPOIS passa ao intake
- Opera à distância do repo da empresa (`--target-repo <path>`)
- Nunca armazena código real — só metadados, padrões, nomes, contagens

---

## 1. Os níveis de scan (L0–L4)

### L0 — Macro arquitetural + lógica de domínio

**Quando roda:** onboarding — uma vez, salvo. O macro não muda rápido.
**Custo:** aceito explicitamente. Leitura profunda, sem limite artificial de arquivos de lógica.

Extrai:
- Tipo de sistema (web, embarcado, serverless, monolito, microsserviços)
- Stack principal (framework, runtime, versão)
- Infra declarativa: Docker/k8s, CI/CD, cloud provider (lido de arquivos de configuração, nunca de lógica)
- Build system (webpack, vite, gradle, cargo, npm scripts, etc.)
- **Lógica de domínio:** fluxos principais, entidades centrais, como o negócio funciona no código

**Por que lógica de domínio no L0:** "Eu preciso entender como funciona também." Sem entender o
domínio, o Piloto não sabe o que está fazendo nem o que pode impactar. É uma leitura única — vale.

**Não extrai:** dados de equipe, histórico de commits, autores. Risco LGPD confirmado.

---

### L1 — Estrutura e linguagens (automático junto com L0)

Extrai:
- Árvore de diretórios com labels de tipo (components, services, models, controllers, etc.)
- Linguagens presentes + distribuição percentual
- Entry points do projeto
- Dependências principais (package.json, pom.xml, go.mod, requirements.txt, Cargo.toml, etc.)

`.gitignore` do projeto-alvo respeitado por padrão (elimina `node_modules/`, `dist/`, etc.)

---

### L2 — Padrões de arquitetura de software (sob demanda, por ticket)

Extrai o padrão arquitetural em uso na área relevante para o ticket:
Clean Architecture, DDD, Hexagonal/Ports-and-Adapters, MVC, Feature-Sliced, CQRS, etc.

**Algoritmo de detecção:**
1. Checklist de sinais estruturais (nomes de pasta/arquivo) → identifica ~80% dos casos
2. Se inconclusivo: Claude lê 5–10 arquivos-chave e infere o padrão
3. HTML inclui **seção de prova de raciocínio**: "como chegamos a esta conclusão" — evidências usadas

---

### L3 — Estética e convenções de código (sob demanda, por ticket)

Extrai o "dialeto" do time na área do ticket:
- Naming conventions por contexto (variáveis, funções, classes, arquivos)
- Organização de imports e módulos
- Estilo de tratamento de erros
- Gestão de estado (Redux, Zustand, Context, MobX, etc.)
- Padrões de teste (estrutura, naming, mocks)
- Formatação (inferida ou declarada em `.eslintrc`, `prettier.config`, etc.)

---

### L4 — Coexistência de padrões (detectado automaticamente durante L2/L3)

Em projetos reais, coexistem padrões de épocas diferentes. O L4 classifica:

- **Padrão vigente** (a seguir): score alto em frequência × recência
- **Legado tolerado** (não replicar, não tocar): score decaindo

**Algoritmo de classificação:**
- `score = frequência_normalizada × peso_recência`
- Padrão em arquivos novos e numerosos → vigente
- Padrão em arquivos antigos com ocorrências decaindo → legado
- Override manual: `--context "padrão vigente é Zustand, não Redux"`

---

## 2. Project Profile

**Arquivo:** `governance/project-profile-<cliente>.md`

**Formato:** flat MD com seções por nível + timestamp por seção.

```
## L0 — Macro arquitetural
_scanned_at: 2026-05-31T10:00Z_

tipo: web · framework: Next.js 14 · runtime: Node.js 20 · infra: Vercel + Supabase
build: Turbopack · ci: GitHub Actions
domínio: marketplace de serviços profissionais
fluxos: cadastro → match → agendamento → pagamento → avaliação
entidades: User, Provider, Service, Booking, Review, Payment

## L1 — Estrutura
_scanned_at: 2026-05-31T10:05Z_

linguagens: TypeScript (88%), CSS (8%), SQL (4%)
entry_points: src/app/page.tsx · src/app/api/[...route]/route.ts
deps_principais: next@14 · react@18 · @supabase/supabase-js · stripe · zod · tailwindcss

## L2 — Padrões de arquitetura (área: src/auth)
_scanned_at: 2026-05-31T14:30Z_

padrão: Feature-Sliced Design
evidência: pastas features/ · shared/ · entities/ presentes
vigente: FSD (arquivos recentes) · legado: MVC em src/legacy/ (não tocar)
```

**Regras de atualização:**
- `--level L0` adiciona ou substitui só a seção L0
- `--refresh-level L3` re-escaneia e substitui só a seção L3
- Default: usa cache; nunca descarta dados sem instrução explícita
- Nunca armazena trechos de código real — só metadados, padrões, nomes, contagens

**Multi-client:** um arquivo por cliente. Identificado via `--client <nome>`.
Quando há múltiplos perfis ativos, `--client` é obrigatório.

---

## 3. HTML Output

**Regra:** cada scan produz um HTML. Full dossier em todos os níveis.

**Arquivo:** `governance/scanner-output-<cliente>-<YYYYMMDD-HHMM>.html`
Link para o mais recente registrado no project-profile.

**Conteúdo obrigatório em todos os níveis:**

| Seção | Conteúdo | Formato |
|-------|----------|---------|
| Mapa arquitetural | Árvore de diretórios + labels de tipo + diagrama de camadas | Mermaid diagram |
| Padrões detectados | L0 stack · L2 arquitetura · L3 estilo · L4 vigente/legado | Lista estruturada |
| Grafo de dependências | Quem importa quem (entre módulos/pastas) | Mermaid graph |
| Prova de raciocínio | Como a IA chegou a cada inferência (evidências usadas) | Seção expandível |
| Flags de atenção | Coexistências L4 · áreas não escaneadas · dependências críticas | Cards coloridos |
| Relatório de custo | Tokens consumidos · estimativa em USD | Footer |

**Filosofia de tamanho:** o conteúdo é sempre completo. O tamanho é proporcional à área coberta.
Um scan L2 em `src/auth` produz um HTML pequeno por natureza — não porque cortamos conteúdo.

**Liga/desliga:**
- Default: ON
- Configurável: `governance/ux-config.yaml` → `html_output: true/false`
- Override pontual: flag `--no-html`

---

## 4. Modo Adaptativo (projetos com 500+ arquivos)

Para projetos grandes, o scanner nunca decide sozinho. Pré-scan obrigatório:

```
>>> Inventário do projeto:
>>> Total de arquivos: 3.847
>>> Após .gitignore: 1.203 arquivos relevantes
>>>
>>> Estimativas de custo:
>>> [A] Scan completo (L0+L1+lógica de domínio): ~45.000 tokens · est. $0.13
>>> [B] Scan estrutural (L0+L1 sem lógica)       ~12.000 tokens · est. $0.04
>>> [C] Scan por área (indique a pasta)          ~5.000 tokens  · est. $0.01
>>> [D] Cancelar
>>>
>>> Sua escolha:
```

**Regras do modo adaptativo:**
- Custo estimado SEMPRE exibido antes de qualquer scan grande
- Scanner aguarda confirmação — nunca começa leitura massiva silenciosamente
- Relatório de cobertura ao final: arquivos lidos, arquivos excluídos, razão

---

## 5. Interface CLI

```
python sdk/codebase_scanner.py \
  --target-repo <path>          # repo a escanear (fora da cognitive-arch)
  --level <L0|L1|L2|L3|L4>     # nível de scan
  --context "texto livre"       # opcional — orienta o scan (área, objetivo)
  --ticket "texto do ticket"    # scan parcial: infere área do ticket → confirma
  --area <path>                 # scan parcial: especifica área diretamente
  --refresh-level <L0-L4>       # força re-scan de um nível específico
  --client <nome>               # identifica o cliente (para multi-client)
  --no-html                     # suprime geração de HTML nesta execução
  --arch-root <path>            # raiz da cognitive-arch (default: auto-detect)
```

**Saídas:**
1. `governance/project-profile-<cliente>.md` (atualizado/criado)
2. `governance/scanner-output-<cliente>-<timestamp>.html` (se HTML ativado)
3. Relatório de custo no stdout (sempre)

---

## 6. Custo de tokens — medição obrigatória

Em todo scan, o scanner reporta:
- Tokens de entrada (arquivos lidos)
- Tokens de saída (perfil + HTML gerados)
- Estimativa em USD
- Exibido no stdout + registrado no HTML (seção footer)

**Por quê:** tudo no corporativo tem análise de custo. O scanner é a operação mais cara da
arquitetura. Medir desde o início cria a baseline para decisões futuras.

---

## 7. Interface com o Consistency Checker

O `consistency_checker.py` (phase-29 / block-163) consome o project-profile como input.

**Interface proposta (finalizar no block-163):**
```python
# O checker lê as seções L3 e L4 do profile para comparar com o código gerado
# Retorna: score de consistência (0.0–1.0) + lista de divergências por categoria
```

O scanner garante que L3 e L4 estejam no profile antes de qualquer run do checker.
O campo `scanned_at` por seção permite que o checker detecte perfis desatualizados.

---

## 8. Dogfooding — sequência de validação

1. **Fixture TypeScript/React pequeno** (criado ou clonado) — valida a pipeline, debug fácil
2. **MMORPG** — stress test com oráculo (Piloto sabe o que esperar) — simula ticket real

Ambos produzem profiles + HTMLs que servem como exemplos de output para validação humana.

---

## 9. Out of Scope

- Análise semântica de lógica de negócio (scanner abstrai o que existe — não raciocina se está certo)
- Multi-repo scan — escopo é um único repo por sessão
- Integração com Jira/Linear API
- Análise de autores, commits, métricas de equipe (LGPD — bandeira vermelha)
- Geração automática de PRs no repo da empresa
- GUI / dashboard interativo
- Consistency checking (phase-29 / block-163)

---

*Brainstorm: `_brainstorm/scanner-v2-redesign.md`*
*Fase: `phases/phase-30.md`*
*Revisado em: 2026-05-31*
