---
id: phase-22
status: planned
prev_phase: phase-21
exit_criteria_count: 5
blocks_count: 5
estimated_duration_minutes: 150
created_at: 2026-05-28
last_updated: 2026-05-28
owner: implementer
---

# Phase 22 — UX / Observability

BRIEF: Improve how the system communicates and how users observe its state. governance/ux-voice.md defines communication tone rules. Dashboard gets clickable file links and a governor notifications widget. BOOTSTRAP.md and RETROFIT.md are redesigned with 22 phases of learning. sdk/ux_validator.py validates AI output against ux-voice.md rules.

## 1. Purpose

After 21 phases, the system works well internally but the human-facing layer is still rough: AI output is inconsistent in tone, dashboard file references are not clickable, onboarding (BOOTSTRAP/RETROFIT) reflects early design decisions that 22 phases of iteration have superseded, and governor notifications are buried in session_start.py output. Phase 22 addresses all four: a voice guide codifies how the AI should communicate, the dashboard becomes interactive with clickable links, onboarding files are redesigned from scratch, and a validator ensures the voice guide is followed.

## 2. Goals

- governance/ux-voice.md: tone rules, response format standards, prohibited patterns, positive examples
- dashboard.html: all file path references rendered as clickable links (file:// or vscode:// protocol)
- BOOTSTRAP.md + RETROFIT.md redesigned using all 22 phases of accumulated learning
- Dashboard notifications widget: top 3 pending governor notifications shown inline
- sdk/ux_validator.py: validates session_start.py output and health reports against ux-voice.md rules

## 3. Invariants

- ux-voice.md is a governance file (not a protocol); AI reads it but users can edit it freely
- Clickable links use file:// by default; vscode:// configurable in governance/ux-config.yaml
- BOOTSTRAP.md and RETROFIT.md redesign is additive: all working flows preserved, obsolete steps removed
- ux_validator.py never blocks work; it only reports violations (advisory, not gate)
- Dashboard notifications widget shows maximum 3 items to avoid clutter

## 4. Dependencies

- Phase 21 complete (governor.py + notifications.md exist)
- Phase 15 complete (dashboard_generator.py generates dashboard.html)
- All prior phases complete (BOOTSTRAP/RETROFIT redesign requires full picture)

## 5. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ux-voice.md rules are too prescriptive, stifle AI output | Med | Rules are guidelines not constraints; ux_validator produces WARNs not errors |
| Clickable links don't work on all OSes/editors | Low | file:// works universally; vscode:// optional; links degrade gracefully to plain text |
| BOOTSTRAP/RETROFIT redesign breaks existing user workflows | High | Keep old versions as BOOTSTRAP-v1.md, RETROFIT-v1.md for 1 phase; clear migration note |
| Dashboard notifications widget overloads the page | Low | Max 3 items; "see all" link to full governance/notifications.md |

## 6. Validation

- Open governance/dashboard.html — file links are clickable; notifications widget shows
- Read governance/ux-voice.md — rules are clear, specific, and have examples
- Run through BOOTSTRAP.md flow on a fresh directory — confirms updated flow works
- Run `python sdk/ux_validator.py --check session-output` — report generated
- Run `python -m pytest sdk/tests/ -q` — 0 failures

## 7. Exit Criteria

1. `governance/ux-voice.md` documents: tone (direct, no filler), response format standards (headers, tables, code blocks), prohibited patterns (e.g. "I'll now...", "Certainly!", excessive hedging), and ≥5 positive/negative examples.
2. `governance/dashboard.html` renders all file path strings as clickable links using file:// protocol; link protocol configurable via `governance/ux-config.yaml`; dashboard_generator.py updated to emit `<a href="file://...">` tags.
3. `BOOTSTRAP.md` and `RETROFIT.md` redesigned from scratch incorporating lessons from phases 1–22: streamlined flows, updated tool references (session_start.py, block_start.py, block_close.py, phase_manager.py), removed obsolete manual steps, added governor/notifications awareness. Old versions archived as `BOOTSTRAP-v1.md` and `RETROFIT-v1.md`.
4. Dashboard governor notifications widget shows top 3 pending notifications by priority; each entry has message, priority badge, age, and dismiss link; "view all" links to governance/notifications.md.
5. `sdk/ux_validator.py --check <file>` reads a file and reports violations against ux-voice.md rules; outputs WARN lines only (advisory); exit code 0 always (non-blocking). Integrated into session_start.py as optional post-run check.

## 8. Block Index

| Block | Title | Tier | Status | Manifest |
|-------|-------|------|--------|----------|
| block-130 | ux-voice.md | S | planned | `manifests/block-130-ux-voice.md` |
| block-131 | Dashboard clickable links | M | planned | `manifests/block-131-dashboard-links.md` |
| block-132 | BOOTSTRAP + RETROFIT redesign | M | planned | `manifests/block-132-bootstrap-retrofit-redesign.md` |
| block-133 | Dashboard notifications widget | S | planned | `manifests/block-133-dashboard-notifications.md` |
| block-134 | ux_validator.py | M | planned | `manifests/block-134-ux-validator.md` |

## 9. Dependency Graph & Parallel Execution Plan

```yaml
parallel_execution_plan:
  total_blocks: 5
  recommended_agents: 1
  groups:
    - id: 22A
      blocks: [block-130]
      type: sequential
      depends_on: []
    - id: 22B
      blocks: [block-131, block-132, block-133]
      type: parallel
      depends_on: [22A]
    - id: 22C
      blocks: [block-134]
      type: sequential
      depends_on: [22B]
```

ux-voice.md is the foundation all others reference; dashboard, redesign, and widget can be built in parallel; validator comes last as it validates the outputs of the others.

## 10. Out of Scope

- Interactive dashboard (JavaScript state management, real-time updates) — static HTML only
- AI voice synthesis or multimodal output — text only
- Automated BOOTSTRAP flow execution — human-guided only
- Accessibility audit of dashboard.html — future phase

---

End of phase-22.
