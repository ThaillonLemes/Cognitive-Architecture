---
id: phase-22-retro
phase: phase-22
status: done
exit_criteria_met: 5/5
blocks_completed: 5/5
actual_duration_minutes: 200
created_at: 2026-05-28
---

# Phase 22 Retrospective — UX / Observability

## 1. Exit Criteria Met

1. **governance/ux-voice.md** — tone guide written: 5 tone rules, response format standards table, 24 prohibited phrases in fenced block, 5 positive/negative example pairs, session_start.py output template. ✓
2. **Dashboard clickable links** — `_linkify_path()` wraps file/path strings in `<a href="file://...">` tags; `dashboard_link_protocol` and `dashboard_links_enabled` configurable in governance/ux-config.yaml. ✓
3. **BOOTSTRAP.md + RETROFIT.md redesign** — v2 rewrites: mandatory `python sdk/session_start.py` as Step 0, all manual state edits replaced by SDK tools, governor/notifications integrated, old versions archived as -v1.md. ✓
4. **Dashboard notifications widget** — `_render_notifications_widget(arch_root)` shows top N pending governor notifications; priority color badges; overflow "N more"; zero-pending green "system quiet"; N configurable via ux-config.yaml. ✓
5. **sdk/ux_validator.py** — validates text against ux-voice.md `prohibited` block; exits 0 always; integrated into session_start.py via `--validate-ux` flag. ✓

## 2. Blocks

| Block | Title | Tier | Duration | Gate |
|-------|-------|------|----------|------|
| block-130 | ux-voice.md | S | 0.4h | 2/2 ✓ |
| block-131 | Dashboard clickable links | M | 0.8h | 2/2 ✓ |
| block-132 | BOOTSTRAP + RETROFIT redesign | M | 0.5h | 1/2 (lint skipped) ✓ |
| block-133 | Dashboard notifications widget | S | 0.3h | 2/2 ✓ |
| block-134 | ux_validator.py | M | 1.2h | 2/2 ✓ |

## 3. Key Decisions

- `ux_validator.check()` skips the `prohibited` fenced block itself during scanning — prevents self-referential false positives when checking governance/ux-voice.md
- `_linkify_path` degrades gracefully for empty/dash/tilde/unknown/? inputs (no link emitted)
- BOOTSTRAP/RETROFIT v1 archives retained for 1 phase as safety net
- All new dashboard widgets use `getattr(data, field, None)` — no DashboardData dataclass changes required, all existing tests unaffected
- flake8 not available in environment; py_compile used for syntax verification throughout

## 4. Patterns

- Test self-check anti-pattern: testing that a rules-definition file doesn't violate its own rules is only valid if rule definitions are excluded from scan scope. Fixed in ux_validator.check().
- getattr backward-compat pattern: extending rendered output without touching existing dataclass definitions avoids test breakage across the board.

## 5. Phase 23 Candidate

No Phase 23 currently planned. Phases 18–22 complete. Architecture is stable.
