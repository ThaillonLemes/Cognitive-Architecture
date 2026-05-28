# RETROFIT — bootstrap for existing projects

BRIEF: Guides the AI through adopting the cognitive architecture in a project that ALREADY has code. Unlike BOOTSTRAP.md (fresh project), RETROFIT analyzes existing code and fills cognitive-arch files from what's already there.

## When to use this (vs BOOTSTRAP.md)

Use RETROFIT when ANY of:
- The project already has source code (`src/`, `app/`, `lib/`, etc.)
- The project has existing docs (README, ARCHITECTURE.md, etc.)
- The project has git history showing real development
- The project has tests, build scripts, dependencies

Use BOOTSTRAP only for brand-new empty projects.

If unsure: ask the user "Is this a brand-new project from zero, or an existing project adding the cognitive architecture?"

## What this flow does

1. Inspects the existing project (read-only; no modifications)
2. Extracts: stack, structure, build/test/lint commands, docs
3. Asks user questions code can't answer (vision, constraints, next phase)
4. Fills `PROJECT.md`, `phase-0/`, `design/`, `phase-1` from inferred + confirmed data
5. Marks inferred content with `(inferred — confirm)` so user can validate

## Mode

Throughout RETROFIT: **guidance** mode (conversational). Switch to **checklist** only for Step 9 (final report).

---

## The flow

### Step 0 — Detect + greet

If user just dropped the cognitive-arch folder + pasted a retrofit prompt:
- Confirm: "Detected existing project. I'll analyze it and fill cognitive-arch from what's already here. I won't modify any project code."
- Read this RETROFIT.md fully

If user said "oi" or similar greeting and the project clearly has existing code:
- Detect; suggest this flow over BOOTSTRAP.md

### Step 1 — Read the cognitive architecture

Read in order:
1. `cognitive-arch/CLAUDE.md`
2. `cognitive-arch/PROTOCOLS.md`
3. `cognitive-arch/PROJECT.md` (template)
4. `cognitive-arch/INDEX.md` (catalog)

Confirm to user that you understand the architecture before proceeding.

### Step 2 — Inspect the project (read-only)

**DO NOT modify anything.** Read/scan only:

1. **Root layout:** list folders + files at project root (excluding `cognitive-arch/`)
2. **Stack manifest files:** look for `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `pom.xml`, `CMakeLists.txt`, `Gemfile`, `composer.json`, `*.csproj`, `*.sln`, `mix.exs`, `pubspec.yaml`, etc. Determine language(s) + framework(s).
3. **Build/test/lint commands:** extract from `package.json` scripts, `Makefile`, `justfile`, `taskfile.yml`, README quickstart sections, CI workflow files.
4. **Existing docs:** scan for `README.md`, `docs/`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, ADRs (`docs/decisions/` or `adr/` or `decisions/`), design docs (`design/`, `docs/design/`).
5. **Code structure:** `src/`, `lib/`, `app/`, `components/`, `pkg/`, `cmd/`, `internal/`, etc. Record the layout.
6. **Tests:** location, naming convention, approximate count (via Glob like `**/*test*.{js,ts,py,rs,go}`).
7. **CI/CD:** `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`.
8. **Git activity:** run `git log --oneline -20` and `git branch -a` to see recent activity + current branch.
9. **Other workspace files:** `LICENSE`, `.editorconfig`, `.gitignore`, `Dockerfile`, `docker-compose.yml`, `.env.example`, IDE config.

Report findings concisely to the user:

```
Detected project context:
- Language: <X>
- Framework: <Y>
- Build cmd: <cmd>
- Test cmd: <cmd>
- Lint cmd: <cmd>
- Code in: <folders>
- Tests in: <folders>
- Docs in: <folders>
- CI: <system or "none">
- Recent git activity: <pattern>
- Approx file count: <number>
- License: <if found>
```

### Step 3 — Ask clarifying questions

Code can't tell you the WHY. Ask the user (conversationally — one at a time OR small groups, not all 7 at once):

1. **Vision:** what does this project deliver? (1-2 sentences)
2. **Target users:** who uses it?
3. **Type:** web app / SaaS / game / CLI / library / mobile / desktop / other?
4. **Current status:** early dev / MVP / beta / production stable / maintenance?
5. **Key constraints:** performance, security, compliance, latency, accessibility?
6. **Next phase:** immediate next work direction (next 2-4 weeks)?
7. **Ambiguities:** anything in the code that needs your interpretation? (e.g., naming conventions that look intentional but unclear, modules that seem orphaned, etc.)

### Step 4 — Fill PROJECT.md

With Step 2 (inferred) + Step 3 (user confirmed):

- Open `cognitive-arch/PROJECT.md`
- Fill frontmatter with REAL values (no placeholders)
- Fill body sections (Vision, Target users, Constraints, Pointers)
- Mark inferred content: `(inferred — please confirm)` or `(user confirmed)`

Save. Update `STATE.md`: `status:active phase:0-retrofitted` (not bootstrap).

### Step 5 — Fill phase-0/ templates

Fill each in order:

- `phase-0/00-project-overview.md` — expanded vision + scope + risks
- `phase-0/01-stack-and-tools.md` — exact stack, commands, env vars, dependencies
- `phase-0/02-domain-overview.md` — high-level domain entities and flows
- `phase-0/03-roadmap-draft.md` — proposed phases based on user's "next phase" answer + git history

For `02-domain-overview.md`: scan source briefly for:
- Main entities (User, Order, Player, Item — project-specific)
- Main flows (auth, payment, game-tick, etc.)
- Obvious business rules (permission rules, pricing rules)

Mark each: `(inferred from code — confirm)` or `(user confirmed)`.

### Step 6 — Populate design/ from code (if applicable)

If domain logic is clear in the code, extract:

- `design/entities.md` — main entities (data shapes + relationships)
- `design/api-contracts.md` (if service) — API surface
- `design/<domain-specific>.md` — other topics specific to the project type

Each doc uses the structure from `design/README.md`: Why / Vision / Decisions / Mechanics / Open questions / Acceptance / References.

**DO NOT INVENT.** If code doesn't say, mark `TBD — confirm with user`. Be conservative — better to leave 20 TBDs than to assume 1 wrong thing.

### Step 7 — Generate phase-1

Based on:
- User's answer to "next phase" (Step 3.6)
- Recent git activity (Step 2.8)
- Inferred current focus

Create `cognitive-arch/phases/phase-1.md` using `cognitive-arch/templates/phase.md` + `cognitive-arch/protocols/phase-generation.md`.

Phase 1 = the FIRST phase DEFINED under cognitive-arch (not the first phase of the project's life). It's "current work + immediate next steps."

Identify 3-7 immediate blocks that make sense with the current state. Mark them `planned`. Manifests for these come later (per `commands/block-start.md`).

### Step 8 — Update HOT files

- `STATE.md`: `phase:1 status:active retrofitted_from:<date>`
- `NEXT.md`: pointer to first block of phase-1
- `INDEX.md`: catalog updated if new `design/` docs added

### Step 9 — Final report (checklist mode)

Switch to checklist. Give user:

```
=== RETROFIT COMPLETE ===

Discovered:
- <summary of what was found>

Filled:
- PROJECT.md (with N inferred markers)
- phase-0/* (4 files, with M TBDs)
- design/* (K new docs, with L TBDs)
- phases/phase-1.md (planned with N blocks)

Open TBDs to confirm:
1. <list>

Recommended next step:
- Review the above, confirm or correct TBDs
- Then start block-1 via commands/block-start.md
```

---

## Rules (strict)

- ❌ NEVER modify any file OUTSIDE `cognitive-arch/`
- ❌ NEVER presume intent — ask if ambiguous
- ❌ NEVER invent domain logic not in code
- ✅ Use `(inferred — confirm)` and `TBD` markers liberally
- ✅ Be conservative — incomplete > wrong
- ✅ Confirm before each major step (esp. Step 4 onward) — don't auto-fill without user awareness

## After RETROFIT

Once Step 9 is delivered:
- User reviews inferred content
- User answers remaining TBDs (this can take multiple sessions)
- `STATE.md` is `active`
- Normal cognitive-arch flow resumes (`commands/block-start.md`, etc.)

RETROFIT runs ONCE per project (like BOOTSTRAP). Don't re-run unless user explicitly wants a re-analysis.

## Difference from BOOTSTRAP.md

| Aspect | BOOTSTRAP | RETROFIT |
|--------|-----------|----------|
| Project state | Empty / new | Existing code |
| Source of truth | User answers (10 questions) | Code inspection + user answers |
| Output speed | Fast (template-driven) | Slower (analysis + iteration) |
| TBD markers | None expected | Many expected (user confirms over time) |
| Risk | Low (no code to corrupt) | Higher (must not modify existing) |
| Domain population | User describes from scratch | Extracted from code, marked inferred |

---

## Appendix A — Governor v2 (optional SDK tier)

> Added in v2.0 (Phase 6). This section applies after RETROFIT Steps 0–9 are complete.

The cognitive architecture ships with a two-tier Governor:

| Tier | Mode | Requirement | What it does |
|------|------|-------------|--------------|
| **1 — Manual** | `governor_mode: manual` | None (default) | AI reads manifests and executes blocks in the current session; no sub-agents dispatched automatically |
| **2 — SDK** | `governor_mode: sdk` | Python 3.9+, Anthropic API key | Governor spawns Claude sub-agents automatically via the Anthropic Python SDK; handles dispatch, validation, and state integration |

### Choosing a mode

**Start with manual** (the default). It requires no extra setup and works in any editor or LLM session. Add SDK when:
- You want automated multi-block execution without per-block human prompting
- You are comfortable managing an API key and Python environment
- You have API credits and want to see blocks complete autonomously

### Enabling SDK mode

1. **Install SDK dependencies:**
   ```bash
   pip install -r cognitive-arch/sdk/requirements.txt
   ```
   _(Requires `anthropic>=0.25.0` and `pyyaml>=6.0`.)_

2. **Set your API key:**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   Get your key at [console.anthropic.com/settings/api-keys](https://console.anthropic.com/settings/api-keys). Note: the Anthropic API is billed separately from Claude Max.

3. **Update STATE.md:**
   Change `governor_mode:manual` to `governor_mode:sdk`.

4. **Run dry-run to verify:**
   ```bash
   python cognitive-arch/sdk/governor.py --mode sdk --dry-run
   ```

### Staying in manual mode

No additional steps required. The architecture is fully functional in manual mode — the AI reads manifests, executes blocks, and updates all state files within the current session. Manual mode is the recommended starting point.

### Environment variables (SDK mode)

| Var | Default | Description |
|-----|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | API key for Anthropic SDK dispatch |
| `GOV_MODEL` | `claude-opus-4-5` | Claude model for sub-agents |
| `GOV_MAX_TOKENS` | `8192` | Max tokens per sub-agent call |
| `GOV_TIMEOUT_SEC` | `300` | Sub-agent timeout in seconds |
| `GOV_MAX_PARALLEL` | `3` | Max concurrent sub-agents |

See `sdk/config.py` and `design/governor-v2.md` for full details.

End of RETROFIT.md.
