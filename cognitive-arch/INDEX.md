# INDEX — navigation catalog

BRIEF: catalog of every file/folder with one-line brief. Use this to decide what to read. For large files, use partial-read (`Read(file, limit:30)`) — see `protocols/file-reading-protocol.md`.

## HOT (every session start)

| File | Brief |
|------|-------|
| CLAUDE.md | AI entry point; reading order; flow pointers |
| PROTOCOLS.md | 24 axioms (P/Q/C/S) + Charter; S1-S5 security axioms added Phase 10 |
| STATE.md | Current project state — AI-only, dense |
| NEXT.md | Pointer to next work — AI-only, dense |
| INDEX.md | This catalog |
| board.md | Multi-agent status dashboard — AI-only |
| _syntax.md | Vocabulary for AI-only files |

## WARM (read when relevant)

| File | Brief |
|------|-------|
| PROJECT.md | Project identity (name, type, stack); Phase 6 active |
| BOOTSTRAP.md | Interactive first-session flow (NEW projects); v2.0 updated |
| RETROFIT.md | First-session flow for EXISTING projects; v2.0 updated |
| phase-0/ | Phase 0 onboarding templates |
| design/ | Domain logic docs (user fills) |
| design/governor-v2.md | Governor v2 master spec; 13 decisions, 7 open questions resolved |
| phases/ | Phase roadmap docs (created over time) |
| phases/phase-1.md | Phase 1 — Consistency (v1.1); 6 blocks; complete (retroactive) |
| phases/phase-4.md | Phase 4 — Governor v2 design (v1.4); 12 blocks; complete |
| phases/phase-4-retro.md | Phase 4 retrospective; 6/6 exit criteria met; 1 day actual |
| phases/phase-5.md | Phase 5 — Governor v2: Python SDK (v2.0); 9 blocks; complete |
| phases/phase-5-retro.md | Phase 5 retrospective; 9/9 exit criteria; 8 bugs fixed; 1 day actual |
| phases/phase-6.md | Phase 6 — Retrofit Readiness (v2.0); 13 blocks; complete |
| phases/phase-12.md | Phase 12 — Foundation Fix (v3); 4 blocks; planned; activates dormant features |
| phases/phase-13.md | Phase 13 — Architecture Integrity (v3); 4 blocks; planned; file protection + integrity lock |
| phases/phase-14.md | Phase 14 — Retrospective Mining (v3); 4 blocks; planned; turns retros into data |
| phases/phase-15.md | Phase 15 — Master Agent v1 (v3); 5 blocks; planned; conductor / orchestrator |
| phases/phase-16.md | Phase 16 — Visibility & Dashboard (v3); 5 blocks; planned; HTML reporting layer |
| phases/phase-17.md | Phase 17 — Assertive Brainstorm v2 (v3); 4 blocks; complete; AI-led questionnaires |
| phases/phase-17-retro.md | Phase 17 retrospective; 4/4 exit criteria met; 111 tests added; 3.5h actual; project complete |
| design/arch-v3.md | v3 design document — 15 decisions + 12 defaults from 2026-05-23 brainstorm |
| _future/token-based-modes.md | Deferred: economical vs full-token modes (needs token metrics first) |
| sdk/ | Governor v2 Python package; entry point sdk/governor.py |
| sdk/governor.py | CLI entry point; --dry-run / --block / --test-integration / --mode / --list-tracks / --track |
| sdk/convention_snippet.py | Builds per-block axiom snippet from 19 axioms (P/Q/C sort) |
| sdk/task_packet.py | Assembles task packet from manifest + arch context |
| sdk/return_validator.py | Validates sub-agent return packages against required field schema |
| sdk/dispatch.py | Dispatches packets via Anthropic API or MockAnthropicClient |
| sdk/integration.py | Integrates results: state files, BLOCK_LOG, atomic writes, git |
| sdk/config.py | GovConfig dataclass; env var loader; check_pause() for interruption |
| protocols/stack-addenda/ | Stack-specific convention overlays (Python/FastAPI, React, Node) |
| manifests/ | Block manifests (created per block) |
| blocks/ | Block retrospectives + BLOCK_LOG.md |
| agents/ | AGENT.md per active agent |
| governance/ | Governor state + audit reports |

## COLD (templates, protocols, commands — large)

| Folder | Brief |
|--------|-------|
| templates/ | File templates (phase, manifest, retrospective, AGENT, ADR) |
| templates/agent-roles/ | Pre-built agent role templates |
| protocols/ | Generation rules + behavior protocols |
| commands/ | Operational commands for the AI to follow |
| decisions/ | ADRs (Architectural Decision Records) |
| _brainstorm/ | Scratchpad for questionnaires |
| _future/ | Patterns deferred to later versions |

## Briefs (most important files)

| Path | Brief |
|------|-------|
| protocols/modes.md | Guidance/guardrails/checklist modes per agent role |
| protocols/phase-generation.md | How to generate a phase doc |
| protocols/manifest-medium-generation.md | How to generate a Tier M block manifest |
| protocols/parallelism.md | How to identify and coordinate parallel blocks |
| protocols/agents.md | Agent lifecycle, naming, spawn workflow |
| protocols/block-close-checklist.md | 8-step protocol at end of every block |
| protocols/file-reading-protocol.md | When and how to use partial reads |
| protocols/code-header-protocol.md | Mandatory header on every code file |
| protocols/pointer-integrity.md | Audit rule for cross-file references |
| commands/run.md | Master command: do everything (leigo-friendly) |
| commands/block-start.md | Protocol to start a new block |
| commands/block-close.md | Protocol to close a block |
| commands/governor.md | Governor agent script (integrate, audit, drift detect) |
| templates/agent-roles/implementer.md | Implementer agent definition |
| templates/agent-roles/governor.md | Governor agent definition |
| templates/agent-roles/master.md | Master agent role (conductor/orchestrator; hybrid posture; no commits) |
| agents/agent-master.md | Master agent identity card; permissions matrix; tool registry protocol |
| governance/tools-registry.yaml | 9-tool registry; last_run + interval + priority per tool; Master reads at session start |
| sdk/tools_registry.py | read_registry / update_last_run / get_stale_tools; ToolEntry dataclass |
| protocols/tools-registry-spec.md | Schema + mutability contract for tools-registry.yaml |
| sdk/master_scheduler.py | Time-based trigger engine; classifies stale tools as overdue/very_overdue/critical |
| protocols/master-scheduler-spec.md | Urgency rules, timezone handling, StaleTool record definition |
| protocols/inter-agent-messages.md | YAML message schema (v1.0) for Master ↔ sub-agent comms; field reference + kind conventions |
| sdk/agent_message_schema.py | AgentMessage dataclass; validate() / is_valid() / create_message() / create_response() |
| templates/agent-message.yaml | Worked examples for request, notification, and response message kinds |
| protocols/master-active-suggestion.md | When/how Master surfaces tool suggestions: session-start, inline, on-demand |
| sdk/master_suggest.py | suggest_at_session_start / suggest_inline / suggest_on_demand; Suggestion dataclass |
| sdk/briefing_generator.py | Post-pause briefing (markdown + HTML); threshold-triggered at session start |
| templates/briefing-post-pause.md | Output template for post-pause briefing; 15-line hard cap |
| sdk/weekly_report.py | Weekly HTML report generator; velocity, blocks, patterns, forecast; writes governance/reports/ |
| templates/weekly-report.html | HTML template for weekly report (dark theme, standalone) |
| sdk/dependency_resolver.py | Finds blocks newly-unblocked after BLOCK_LOG append; pure function; Master Agent handles board update |
| protocols/dependency-resolution.md | Resolver flow, board update rules, notification format |
| sdk/dashboard_generator.py | Live dashboard HTML generator; DashboardData dataclass; generate_dashboard/render_html/write_dashboard; 4-col grid + timeline + roadmap |
| templates/_styles.css | Shared CSS design tokens (dark theme #0f0f1a); card/badge/table/phase-pill/dash-grid/timeline; shared with weekly-report and briefing HTML |
| templates/dashboard.html | Annotated dashboard template with placeholder comments; structure reference for dashboard_generator |
| governance/dashboard.html | Live generated dashboard output; regenerated by sdk/dashboard_generator.py |
| protocols/dashboard-integration.md | When/how Master triggers dashboard refresh, weekly report, post-pause briefing; session start sequence; D11 cache rule |
| sdk/brainstorm_context_schema.py | Data model: RetroEntry, PatternEntry, AdrEntry, StateSnapshot, ContextBundle; consumed by predictor (block-109) and synthesis (block-111) |
| sdk/brainstorm_context.py | Context loader for Brainstorm v2; load_context(topic) → ContextBundle; keyword relevance × recency ranking; degrades gracefully on absent files |
| sdk/prediction_schema.py | Data model: Question, Prediction (confidence_band/score/rationale/evidence_sources), PredictionSet; CONFIDENCE_HIGH/MED/LOW constants (D10) |
| sdk/brainstorm_predictor.py | Rule-based prediction engine; predict(question, context) → Prediction; predict_all() → PredictionSet; confidence per D10 thresholds |
| protocols/brainstorm-pattern.md | Brainstorm v1 pattern (DEPRECATED); kept for reference; new sessions use v2 |
| protocols/brainstorm-pattern-v2.md | Brainstorm v2 spec: 3 principles (always recommend, variable options, open answers); confidence bands; session flow; example rendering |
| templates/brainstorm-v2-questionnaire.md | Annotated template for AI-led brainstorm sessions; placeholder variables; example question with confidence band |
| sdk/brainstorm_synthesis.py | Synthesis automation; synthesize(topic, questions, pset, answers) → SynthesisOutput; write_design_doc() → design/<topic>.md |
| protocols/brainstorm-synthesis.md | Synthesis procedure; answer types; output structure; accuracy rate; CLI usage; invariants |

End of INDEX.md.
