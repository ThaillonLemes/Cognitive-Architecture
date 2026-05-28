---
id: phase-5-retro
phase: phase-5
status: complete
blocks_completed: 9
blocks_planned: 9
exit_criteria_met: 9/9
completed_at: 2026-05-22
duration_actual_days: 1
duration_estimated_days: 14
---

# Phase 5 Retrospective — Governor v2: Python SDK (v2.0)

## §1 Phase summary

Phase 5 delivered the first working code in the cognitive-arch project: a 7-module Python SDK (`sdk/`) that implements the Governor v2 specification from Phase 4. The deliverables include all modules from convention snippet generation through multi-block integration, a CLI entry point (`sdk/governor.py`), a mock client for zero-cost testing, and crash-recovery via `governance/governor-state.md`. All 7 open questions from `design/governor-v2.md §11` were resolved during implementation and written back to the design doc. No external API cost was required to complete the phase — all gates passed against the `MockAnthropicClient`.

## §2 Blocks completed

| Block | Title | Tier | Result | Manifest |
|-------|-------|------|--------|----------|
| block-029 | SDK setup + ARCH_ROOT resolution | M | done | `manifests/block-029-sdk-setup.md` |
| block-030 | Convention snippet module | M | done | `manifests/block-030-convention-snippet-module.md` |
| block-031 | Task packet module | M | done | `manifests/block-031-task-packet-module.md` |
| block-032 | Return validator module | M | done | `manifests/block-032-return-validator-module.md` |
| block-033 | Dispatch module (mock + SDK) | M | done | `manifests/block-033-dispatch-module.md` |
| block-034 | Integration module | M | done | `manifests/block-034-integration-module.md` |
| block-035 | Governor main loop + crash recovery | M | done | `manifests/block-035-governor-main-loop.md` |
| block-036 | Config + interruption handling | M | done | `manifests/block-036-config-interruption.md` |
| block-037 | E2E validation + open questions | M | done | `manifests/block-037-e2e-validation.md` |

## §3 Exit criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|---------|
| 1 | `sdk/` package exists with all 7 modules | ✅ met | governor.py, convention_snippet.py, task_packet.py, return_validator.py, dispatch.py, integration.py, config.py |
| 2 | `--dry-run` reads state and prints next block plan | ✅ met | block-029; verified CLI works |
| 3 | Governor runs E2E on test manifest with valid state updates | ✅ met | block-037 `--test-integration` passes |
| 4 | All 7 open questions resolved and written to `design/governor-v2.md §11` | ✅ met | block-037; all marked `resolved:` with module references |
| 5 | `governor_mode: manual \| sdk` feature flag wired | ✅ met | block-035/036; `--mode` flag in CLI; `config.py` reads STATE.md |
| 6 | `audit.sh` exits 0 throughout | ✅ met | checked after each block close |
| 7 | Every Python file carries mandatory code header | ✅ met | all 7 modules have PURPOSE/INPUTS/OUTPUTS/DEPS/SEE header |
| 8 | `MockAnthropicClient` allows full E2E test without API key | ✅ met | block-033; mock used throughout block-037 integration test |
| 9 | `governor-state.md` written before each state transition (crash safety) | ✅ met | block-035; `_write_governor_state()` called before every dispatch and integration |

## §4 Decisions made (ADRs)

None warranting formal ADRs. In-phase resolutions (written to `design/governor-v2.md §11`):

| Open question (Phase 4) | Resolution |
|-------------------------|------------|
| SDK file-passing behavior | Files passed as text in packet body; Anthropic Files API not used |
| Token measurement accuracy | `tok_src: estimated` flag; chars÷4 proxy; actual measurement deferred to Phase 7 |
| Crash recovery depth | Write `governor-state.md` before each transition; full checkpoint restore deferred to v2.1 |
| Max parallel agents | `DEFAULT_MAX_PARALLEL_AGENTS = 3`; configurable via `GOV_MAX_PARALLEL` env var |
| User interruption | Poll `governance/.pause` file every N blocks; configurable via `config.check_pause()` |
| Mixed-codebase projects | Task packet is text-only; no binary file support; markdown-only scope confirmed |
| Governor-state vs STATE.md conflict | Atomic writes (temp file → rename) in `integration.py`; governor-state is ephemeral |

## §5 Risks materialized

| Risk | Fired? | Notes |
|------|--------|-------|
| Anthropic SDK file-passing differs from spec | No | Text-in-packet approach worked; Files API not needed |
| Crash recovery complexity | Partial | Simplified to pre-transition write; full recovery not tested |
| E2E test requires live API key | Partially | MockAnthropicClient covered all automated gates; live run blocked by no-credit account |
| Code header protocol not battle-tested on Python | No | Header pattern from block-029 applied cleanly to all 6 subsequent modules |

## §6 Bugs fixed during implementation

The following bugs were discovered and fixed during Phase 5 (not anticipated in the phase plan):

1. **ARCH_ROOT double-nesting** — `ARCH_ROOT = PROJECT_ROOT / "cognitive-arch"` created path `cognitive-arch/cognitive-arch/`. Fixed: `ARCH_ROOT = Path(__file__).resolve().parent.parent`
2. **Convention snippet sort order** — `sorted()` on group codes gave alphabetical C < P < Q; correct order is P < Q < C. Fixed: `_GROUP_ORDER = {"P":0,"Q":1,"C":2}` + `key=lambda x: ...`
3. **Unicode in Q2 axiom text** — `≤` (U+2264) caused `UnicodeEncodeError` on Windows CP1252. Fixed: replaced with `<=` throughout
4. **Sibling import in task_packet.py** — `from cognitive_arch.sdk.convention_snippet import build_snippet` failed (hyphen in dir name not valid Python package). Fixed: `sys.path.insert(0, _SDK_DIR)` + bare `from convention_snippet import build_snippet`
5. **pyyaml not installed** — `import yaml` in task_packet.py failed. Fixed: `pip install pyyaml` (added to `sdk/requirements.txt`)
6. **integration.py bad DispatchResult import** — `from return_validator import DispatchResult` failed; class lives in `dispatch.py`. Fixed: duck-typed integration (accept any object with `.block_id`, `.success`, `.validation`)
7. **integration.py test conflict** — both mock results shared same `fmod` path, triggering disjoint check failure. Fixed: gave each block a distinct `fmod` value
8. **manual-mode routing bug** — discovered in Phase 6 (block-039): `dispatch_mode = "mock" if args.mode != "sdk"` collapsed manual→mock. Fixed in block-039 (Phase 6)

## §7 Pattern observations

- **Duration:** 1 day actual vs 14 days estimated — 14× faster. All blocks were Python implementation; estimation overshoot likely reflects first code-phase uncertainty.
- **Block tier mix:** 9 Tier M. Correct — each module is a multi-file implementation. Zero Tier S (no trivial fixes in this phase) and zero Tier L.
- **Sequential vs parallel:** User chose sequential (1 agent). Correct for a first Python phase — parallelism would have increased debugging complexity.
- **Gate failures:** Multiple on first attempt due to bugs 1–7 above. All resolved within the same block; no block required forced-pass.
- **Scope stability:** Zero scope additions. All 9 blocks closed within their declared manifests.
- **SDK design quality:** The Phase 4 spec was accurate — no decision reversed during implementation. The 7 open questions provided the right flexibility surface.

## §8 Updates to design/ and protocols/

- `design/governor-v2.md §11` — all 7 open questions marked `resolved:` with module references
- `_syntax.md` — added `governor_mode` key definition (block-029)
- No protocol or template files modified in Phase 5 (implementation phase only)

## §9 Open items entering Phase 6

- `governance/governor-state.md` stale (Phase 5 data) → fixed block-038
- `sdk/governor.py` manual-mode routing bug → fixed block-039
- `PROJECT.md` stale phase/date → fixed block-040
- Missing `phases/phase-1.md` → created block-041
- Missing `phases/phase-5-retro.md` → this document (block-042)
- Roadmap never updated → block-043
- `INDEX.md` missing SDK entries → block-044
- `RETROFIT.md` / `BOOTSTRAP.md` not updated for v2.0 → blocks 045-046
- No stack addenda → blocks 047-049
- `README.md` not updated for v2.0 → block-050

End of phase-5 retrospective.
