## 01 — Stack and tools

BRIEF: Concrete stack and tooling for this meta-project. Most fields are N/A because the deliverable is markdown only; the few real entries are documented below.

## Primary stack

| Layer | Choice | Version |
|-------|--------|---------|
| Language | Markdown (CommonMark + YAML frontmatter) | n/a |
| Runtime | none | n/a |
| Framework | none | n/a |
| Audit script | Bash 4+ (`audit.sh`) — Windows portability gap pending | n/a |
| Editor | Any (architecture is plaintext) | n/a |
| LLM clients (consumers) | Claude Code, Cursor, generic Claude/GPT/Gemini chat | n/a |

## Build / test / lint commands

| Action | Command | Notes |
|--------|---------|-------|
| Install deps | N/A | nothing to install |
| Build | N/A | markdown only |
| Run dev | N/A | no runtime |
| Test all | `bash audit.sh` | structural + size + pointer + drift checks |
| Test unit only | N/A | no code units |
| Test integration | N/A | (future: cross-LLM consistency harness) |
| Test e2e | N/A | (future: full bootstrap/retrofit dry-run) |
| Lint | N/A | (future: markdown-lint + frontmatter schema validator) |
| Type check | N/A | |
| Format | N/A | (proposed: prettier with `--prose-wrap`) |
| Deploy / publish | `git push` (open-source repo on a public host) | |

## Environment

| Setup | Detail |
|-------|--------|
| OS targets | Windows 11 (primary dev — current user), macOS, Linux |
| Required runtimes | Bash 4+ for `audit.sh` (on Windows: git-bash, WSL, or future PowerShell port) |
| Required services | none |
| Required tools | `git` (assumed by RETROFIT, parallelism, integrate flows), text editor |
| Local dev URL | N/A |

## Environment variables

None required. The architecture is entirely file-driven.

## Repository structure

```
./                              ← workspace root (this directory)
└── cognitive-arch/             ← the deliverable (and the workspace)
    ├── CLAUDE.md               ← AI entry point
    ├── PROTOCOLS.md            ← 19 axioms
    ├── STATE.md, NEXT.md, INDEX.md, board.md, _syntax.md ← AI-only HOT
    ├── PROJECT.md              ← project identity
    ├── BOOTSTRAP.md, RETROFIT.md ← first-session flows
    ├── README.md               ← human-facing intro
    ├── audit.sh                ← validation script
    ├── protocols/              ← 13 generation/behavior protocols
    ├── commands/               ← 12 operational commands
    ├── templates/              ← 9 file templates + 4 agent-role templates
    ├── phase-0/                ← onboarding (this folder)
    │   └── discovery/          ← optional pre-project discovery
    ├── design/                 ← (empty — domain docs go here)
    ├── phases/                 ← (created at phase-start)
    ├── manifests/              ← (created per block)
    ├── blocks/                 ← BLOCK_LOG.md + retrospectives
    ├── decisions/              ← ADRs (empty so far)
    ├── agents/                 ← AGENT.md per active agent (empty so far)
    ├── governance/             ← audit reports (empty so far)
    ├── _brainstorm/            ← questionnaire scratchpad
    └── _future/                ← deferred patterns (governor-loop, multi-repo)
```

## Tooling decisions (rationale)

- **Markdown-only over a custom DSL.** Universal, AI-native, version-controllable, no parser to maintain. (Trade-off: weaker formal schema validation.)
- **Bash for `audit.sh`.** Ubiquitous on Unix; deliberately simple. (Trade-off: Windows portability gap — open issue.)
- **No package.json / Cargo.toml at repo root.** The architecture must not advertise a stack it doesn't have. (Consequence: tooling like Renovate / Dependabot has nothing to manage — fine.)

## External dependencies

None. The architecture is self-contained. `git`, `bash`, and an LLM client are the only external requirements, and all three are de-facto standard.

## Open tooling questions

1. Add a PowerShell equivalent of `audit.sh` so Windows users don't need WSL/git-bash? (proposed v1.1 block)
2. Add a `frontmatter-schema/` folder with formal YAML schemas (JSON Schema) for `phase.md`, manifests, ADRs, retrospectives — so structural audits become strict, not regex-based? (proposed v1.2 block)
3. Markdown lint config (`.markdownlint.json`) for consistent style? (low priority)
