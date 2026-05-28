# Command: phase-start

Mode required: guardrails

BRIEF: Open a new phase. Generate the phase doc, plan blocks, set up parallel groups if applicable.

## Usage

- Auto-triggered when previous phase closes and a next phase is planned
- Manual: "start phase <N>" or "follow phase-start"

## Pre-flight (guardrails)

### Step 1 — Verify readiness
Check STATE.md:
- Previous phase status: `complete`?
- If first phase: bootstrap is done (PROJECT.md filled)?

If not ready: HALT, address prerequisites.

### Step 2 — Identify next phase
Read `phase-0/03-roadmap-draft.md` (or `phases/MASTER.md` if exists) for the next phase ID and intended scope.

### Step 3 — Confirm scope with user
Output: "Starting phase <N>: <name>. Intended scope: <summary>. Confirm to proceed?"

Wait for user confirmation.

## Phase generation

### Step 4 — Generate phase doc
Per `protocols/phase-generation.md`:
- Read PROJECT.md, prev phase, roadmap, relevant design docs
- Fill `templates/phase.md`
- Identify parallel groups if ≥3 blocks
- Compute `recommended_agents`
- Save to `phases/phase-<N>.md`

### Step 4b — Run Phase Quality Rubric

Before accepting the generated phase, evaluate it against `protocols/phase-quality-rubric.md`.

Score the phase against all 10 criteria. Record the results in the phase file under a `## Rubric Check` comment block using the template provided in the rubric.

- Score ≥ 8/10 → **ACCEPT** — proceed to Step 5.
- Score 6–7 → **CONDITIONAL** — present failures to user; proceed only with explicit sign-off.
- Score ≤ 5 → **REJECT** — revise the phase and re-run rubric before proceeding.

### Step 5 — Generate block stubs (planned status)
For each block in phase doc §8 Block Index:
- Block status is `planned` (no manifest yet)
- Manifests will be created when each block is about to start (per `commands/block-start.md`)

### Step 6 — Update HOT files
- STATE.md: `p:<N> status:planned`
- NEXT.md: pointer to first block of the phase
- INDEX.md: add entry for new phase doc

### Step 7 — Suggest multi-agent setup (if applicable)
If phase doc has `parallel_execution_plan` with `recommended_agents > 1`:
- Output: "Phase <N> has N parallel groups. Spawn N agents for max throughput, or run sequentially with 1 agent. Which?"
- If multi-agent:
  - Follow `protocols/agents.md` spawn workflow
  - Generate AGENT.md files in `agents/`
  - Output boot prompts for user to paste into new sessions

## Phase-start complete

Output to user:
```
✓ Phase <N> started.
  Phase doc: phases/phase-<N>.md
  Planned blocks: <count>
  Parallel groups: <count> (recommended <M> agents)
  Next block: <ID>
  
  To start work: follow commands/block-start.md (or run.md)
```

## Cost

Phase doc generation: ~5K-10K tokens.
Plus reading inputs: ~2K-3K tokens.

End of phase-start command.
