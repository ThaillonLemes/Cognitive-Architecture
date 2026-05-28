---
id: block-075
tier: M
kind: implementation
phase: phase-9
scope: phase-bound
status: planned
dependencies:
  - block-074
  - block-071
files:
  read:
    - sdk/governor.py
    - sdk/dispatch.py
  modify:
    - sdk/governor.py
  create:
    - sdk/tests/test_track_dispatch.py
gates:
  - name: list-tracks-dry-run-exits-0
    type: cmd
    cmd: "python sdk/governor.py --list-tracks --dry-run"
    expect: exit 0
  - name: pytest-no-regression
    type: cmd
    cmd: "python -m pytest sdk/tests/ -q"
    expect: passed
created_at: 2026-05-23
---

# block-075 — Parallel Track Dispatch

## Purpose

Tracks are only useful if the Governor can dispatch them. Without Governor integration, Tracks are documentation — the executor must manually identify open Track Blocks and dispatch them by hand. This block closes that gap by adding two new flags to `sdk/governor.py`:

- `--track TRACK_NAME` — dispatch open Track Blocks for the named Track. Uses the existing `dispatch_batch` mechanism.
- `--list-tracks` — read `tracks/PRIORITY.md` and print the priority table, ordered by total_priority descending.

Both flags support `--dry-run` (already implemented in the Governor for phase dispatch). The `--dry-run` flag must work correctly for both new flags: it should show what would be dispatched without executing.

This block also serves as the **regression gate** for Phase 9. Block-075 is the last block. Before it can be considered complete, all existing SDK tests must pass. This ensures that the Governor additions do not break any existing phase-dispatch, block-dispatch, or manifest-parsing behaviour.

The deliverable is:
1. Modifications to `sdk/governor.py` adding `--track` and `--list-tracks` flag handling.
2. `sdk/tests/test_track_dispatch.py` with at least 8 tests covering the new functionality.

## Dependencies

- **block-074** must be complete. `tracks/PRIORITY.md` must exist and have a defined structure that the Governor reads.
- **block-071** must be complete (conceptually). Tracks and roadmap are both complete before the final dispatch integration is added. This ensures Phase 9 is architecturally complete before the implementation block runs.

## Files

### Read
- `sdk/governor.py` — to understand existing flag parsing, dispatch_batch call signature, dry-run handling, and exit code conventions.
- `sdk/dispatch.py` — to understand the dispatch_batch function signature (arguments, return value, error handling).

### Modify

**`sdk/governor.py`**

Changes required:

1. **`--list-tracks` flag**

Add to the argument parser:
```python
parser.add_argument(
    "--list-tracks",
    action="store_true",
    default=False,
    help="Read tracks/PRIORITY.md and print the priority table ordered by total_priority descending.",
)
```

Handler logic (in the main dispatch function or a new `handle_list_tracks` function):
- Read `tracks/PRIORITY.md`.
- Parse the priority table (markdown table rows).
- Sort rows by total_priority descending (parse total_priority as integer; treat "—" or missing as 0).
- Print a formatted table:
  ```
  Track Priority Table (as of YYYY-MM-DD)
  ========================================
  Rank  Track ID   System Name          total_priority  current_focus
  1     TRK-001    [system]             [N]             *
  2     TRK-002    [system]             [N]
  ...
  ```
  (Mark current_focus Track with `*`.)
- If tracks/PRIORITY.md does not exist: print "No tracks/PRIORITY.md found. Run protocols/track-generation.md to create Tracks." Exit 0.
- If the priority table has no rows (no Tracks yet): print "No Tracks found in tracks/PRIORITY.md. Create Tracks using protocols/track-generation.md." Exit 0.
- With `--dry-run`: same output. `--dry-run` has no effect on list operations (it only affects dispatch).

2. **`--track TRACK_NAME` flag**

Add to the argument parser:
```python
parser.add_argument(
    "--track",
    metavar="TRACK_NAME",
    default=None,
    help="Dispatch open Track Blocks for the named Track. Use 'current' to dispatch the current_focus Track.",
)
```

Handler logic (in the main dispatch function or a new `handle_track_dispatch` function):
- If TRACK_NAME is "current": read `tracks/PRIORITY.md`, find current_focus Track ID.
- Find the Track file: search tracks/ for a file whose frontmatter id matches TRACK_NAME, or whose system field matches TRACK_NAME (case-insensitive). If not found: print "ERROR: Track '[TRACK_NAME]' not found in tracks/. Run --list-tracks to see available Tracks." Exit 1.
- Read the Track file. Find all Track Block references in the Track Blocks table with status "planned" or "wip".
- For each open Track Block, find the Track Block file (in tracks/blocks/ or alongside the Track file).
- Collect open Track Block file paths.
- If no open Track Blocks: print "Track '[TRACK_NAME]': no open Track Blocks found. Create a new Track Block using templates/track-block.md." Exit 0.
- Call `dispatch_batch(track_blocks, dry_run=args.dry_run)` with the collected Track Block paths.
- Print dispatch summary: "Dispatched [N] Track Block(s) for Track '[TRACK_NAME]'." or "[DRY RUN] Would dispatch [N] Track Block(s) for Track '[TRACK_NAME]'."
- Exit 0.

3. **Error handling rules**

- All new error paths must print a human-readable message and exit with a non-zero code (exit 1).
- `--dry-run` combined with `--track` must exit 0 even if the Track has no blocks (because dry-run is a no-op).
- `--list-tracks` always exits 0 (it is a read operation).
- `--track` without `--dry-run` and with dispatch errors: propagate the error from dispatch_batch and exit non-zero.

4. **No modifications to existing code paths**

The `--track` and `--list-tracks` handlers must be additive. No existing code paths (phase dispatch, block dispatch, manifest loading) may be modified. Existing flags must behave identically to before.

### Create

**`sdk/tests/test_track_dispatch.py`**

Must contain at least 8 tests. Required test coverage:

Test 1 — `test_list_tracks_no_priority_file`: Call `--list-tracks` when `tracks/PRIORITY.md` does not exist. Assert exit code 0. Assert output contains "No tracks/PRIORITY.md found."

Test 2 — `test_list_tracks_empty_table`: Call `--list-tracks` with a `tracks/PRIORITY.md` that has no Track rows. Assert exit code 0. Assert output contains "No Tracks found."

Test 3 — `test_list_tracks_single_track`: Create a mock `tracks/PRIORITY.md` with one Track row (TRK-001, total_priority 12). Call `--list-tracks`. Assert exit code 0. Assert output contains "TRK-001". Assert output contains "12".

Test 4 — `test_list_tracks_sorted_by_priority`: Create a mock `tracks/PRIORITY.md` with three Track rows at total_priority 5, 15, 8. Call `--list-tracks`. Assert exit code 0. Assert output lists them in order 15, 8, 5 (descending).

Test 5 — `test_list_tracks_dry_run`: Call `--list-tracks --dry-run`. Assert exit code 0. Assert output is identical to `--list-tracks` without `--dry-run` (dry-run has no effect on list).

Test 6 — `test_track_dispatch_missing_track`: Call `--track nonexistent-track-xyz --dry-run`. Assert exit code 1. Assert output contains "not found."

Test 7 — `test_track_dispatch_dry_run_no_blocks`: Create a mock Track file with no open blocks. Call `--track [name] --dry-run`. Assert exit code 0. Assert output contains "no open Track Blocks."

Test 8 — `test_track_dispatch_dry_run_with_blocks`: Create a mock Track file with 2 open Track Block references. Create the corresponding mock Track Block files. Call `--track [name] --dry-run`. Assert exit code 0. Assert output contains "Would dispatch 2 Track Block(s)" or equivalent dry-run language.

Additional recommended tests (optional, increases confidence):

Test 9 — `test_track_current_focus`: Call `--track current --dry-run`. Assert exit code 0. Assert Governor correctly reads current_focus from PRIORITY.md and dispatches that Track's blocks.

Test 10 — `test_existing_phase_dispatch_regression`: Call the Governor with an existing phase-dispatch flag (e.g., `--phase phase-1 --dry-run` or whatever the existing flag is). Assert exit code 0. Assert output does not contain any Track-related language. This is the regression gate — existing behaviour must be unchanged.

**Test infrastructure requirements**:

- Tests must use a temporary directory (`tmp_path` fixture in pytest) for mock files. Do not modify real project files during tests.
- Tests must be isolated. Each test sets up its own mock environment.
- Tests must not depend on network access or any external service.
- The test file must be importable without error even if `tracks/` does not exist in the real project.

## Validation

- `sdk/governor.py` is modified and contains `--list-tracks` and `--track` flag definitions.
- `sdk/governor.py` does not modify any existing argument handlers or dispatch functions.
- `sdk/tests/test_track_dispatch.py` exists with at least 8 tests.
- `python sdk/governor.py --list-tracks --dry-run` exits 0.
- `python sdk/governor.py --track nonexistent-track-xyz --dry-run` exits 1.
- `python -m pytest sdk/tests/ -q` passes with no failures (regression gate).

## Gates

| Gate | Type | Command | Expected |
|------|------|---------|----------|
| list-tracks-dry-run-exits-0 | cmd | `python sdk/governor.py --list-tracks --dry-run` | exit 0 |
| pytest-no-regression | cmd | `python -m pytest sdk/tests/ -q` | passed (0 failures) |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Existing Governor argument parser uses a positional argument that conflicts with the new `--track` flag | Low | High | Read sdk/governor.py before implementing; if conflict exists, use a subcommand pattern instead |
| dispatch_batch signature differs from what block-075 assumes | Medium | Medium | Read sdk/dispatch.py before implementing; align call signature exactly |
| Track Block file discovery fails if Track Blocks are stored in a non-standard location | Medium | Low | Track Block discovery reads the Track file's "Track Blocks" table for file references, falling back to tracks/blocks/ directory scan |
| Regression: `--dry-run` on `--track` dispatches real blocks due to missing dry_run propagation | Low | High | Test 8 specifically tests `--track --dry-run` with blocks; any real dispatch would be caught in CI |
| pytest discovers test files that import Governor at module load time, causing import errors in CI | Low | Medium | test_track_dispatch.py uses subprocess calls to invoke the Governor rather than direct imports, isolating test from runtime import errors |

## Out of Scope

- Governor UI or web interface for Track dispatch.
- Automatic Track Block creation. The Governor dispatches existing blocks; it does not generate new ones.
- Parallel multi-Track dispatch (dispatching two Tracks simultaneously). Only one Track at a time with `--track`.
- Integration with CI/CD systems. Track dispatch is a manual operation.
- Modification of `sdk/dispatch.py`. All changes are in governor.py and the new test file.
