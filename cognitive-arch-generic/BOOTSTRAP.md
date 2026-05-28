# BOOTSTRAP — first-session flow (new projects)
# v2 — updated Phase 22. Original archived as BOOTSTRAP-v1.md.

BRIEF: Run on first session of a NEW (empty) project. For existing projects with code, use RETROFIT.md.

## Detection

Run BOOTSTRAP when ALL of:
- No source code outside `cognitive-arch/`
- `STATE.md` has `status:bootstrap` or `STATE.md` is missing
- `PROJECT.md` has unfilled placeholders

Run RETROFIT.md if ANY of: existing `src/`, `app/`, `lib/`; existing README with content; real git history; existing tests or build scripts.

---

## Step 0 — Session init (MANDATORY)

Run before anything else:
```bash
python sdk/session_start.py --arch-root .
```

Read output. Note: health score, active patterns, pending proposals, governor notifications.

---

## Step 1 — Project identity (PROJECT.md)

Ask the user one question at a time. Confirm before writing.

1. Project name?
2. Type? (web app / SaaS / game / CLI / library / mobile / desktop / other)
3. Primary language? (TypeScript / Python / Rust / Go / C++ / other)
4. Framework, if any?
5. Build command?
6. Test command?
7. Lint command?
8. Project description — one paragraph: what does it deliver?
9. Target users — be specific.
10. Key constraints? (performance / security / compliance / latency)

Write `PROJECT.md` with filled values. Then:
```bash
python sdk/state_manager.py --set-state "status:active phase:0"
```

---

## Step 2 — Phase 0 templates

Fill in order (ask user → write file):

1. `phase-0/00-project-overview.md` — expanded overview
2. `phase-0/01-stack-and-tools.md` — stack, env vars, commands
3. `phase-0/02-domain-overview.md` — domain entities and main flows
4. `phase-0/03-roadmap-draft.md` — phases envisioned (high-level)

---

## Step 3 — Generate Phase 1

1. Read `protocols/phase-generation.md`
2. Write `phases/phase-1.md` from user's roadmap
3. Identify parallel groups (see `protocols/parallelism.md`)
4. Update state:
   ```bash
   python sdk/state_manager.py --set-state "p:1 status:planned phase:phase-1"
   python sdk/state_manager.py --set-next "next_action:block-001 phase:phase-1"
   ```
5. Update `INDEX.md` for new files

---

## Step 4 — Governor mode choice

Ask: "Manual (default) or SDK mode for the Governor?"

**Manual** (recommended): no extra setup. AI reads manifests and executes blocks in this session.
```
STATE.md entry: governor_mode:manual
```

**SDK mode**: autonomous sub-agent dispatch. Requires Python 3.9+ and Anthropic API key.
```bash
pip install -r sdk/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python sdk/governor.py --mode sdk --dry-run   # verify
```
Then set `governor_mode:sdk` in STATE.md.

---

## Step 5 — Multi-agent setup (if parallel groups in Phase 1)

If Phase 1 has parallel groups and user wants multi-agent:
- Read `templates/agent-roles/implementer.md` and `protocols/agents.md`
- Generate `agents/agent-1a.md`, `agents/agent-1b.md`, … per group
- Generate `agents/governor.md` from `templates/agent-roles/governor.md`
- Output boot prompts for each session

Otherwise: one agent, sequential execution.

---

## Step 6 — Notifications check

Before handing off, check governor notifications:
```bash
python sdk/notification_manager.py list --pending
```

If any critical/high: surface to user before starting block work.

---

## Step 7 — Hand off

State: `STATE.md` is `status:active`. BOOTSTRAP is complete — not re-read in subsequent sessions.

To start block work: follow `commands/block-start.md`.

To close a block: follow `commands/block-close.md` (uses `sdk/block_close.py`).

---

## After BOOTSTRAP

- `PROJECT.md` filled
- `phase-0/` filled
- `phases/phase-1.md` exists with planned blocks
- `STATE.md`: `status:active phase:1`
- Governor mode set
- Notifications queue checked

Normal flow resumes: read PROTOCOLS → STATE → NEXT → block manifest.

---

## Rules

- Confirm understanding before writing files. Echo user's answer before writing.
- If user is vague, ask follow-up. Never invent values.
- Save incrementally. User can resume at any step.
- BOOTSTRAP runs ONCE per project.
- All file edits via SDK tools (`state_manager.py`, `block_close.py`) — not manual text editing.

---

## SDK tool reference

| Operation | Command |
|-----------|---------|
| Session init | `python sdk/session_start.py --arch-root .` |
| Update state | `python sdk/state_manager.py --set-state "key:val"` |
| Update next | `python sdk/state_manager.py --set-next "key:val"` |
| Close block | `python sdk/block_close.py --block-id X --next Y --actual-hours N` |
| Check notifications | `python sdk/notification_manager.py list --pending` |
| Generate dashboard | `python sdk/dashboard_generator.py --arch-root .` |
| Run health report | `python sdk/health_report.py --arch-root .` |
