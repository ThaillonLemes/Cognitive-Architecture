---
id: block-031
phase: phase-5
status: done
gates_passed: 2
gates_total: 2
created_at: 2026-05-22
---

# Block 031 Retrospective — Module: task packet builder

## §1 What was built

- `sdk/task_packet.py` — full module with:
  - `_parse_frontmatter(content)` — extracts YAML between `---` delimiters via regex + pyyaml
  - `_paths_from_manifest(fm)` — returns `(fread, fmod)` where fmod = modify + create
  - `_SCOPE_MAP` — kind → scope mode table per design/governor-v2.md §4
  - `build_packet(manifest_path, arch_root, gov_id, ts, scope_override, axiom_override, sid)` → full packet string
  - CLI: `--test` (self-test with real manifest + inline fallback), `--manifest PATH`
- `sdk/requirements.txt` updated — `pyyaml>=6.0` added

## §2 Gates

| Gate | Result | Evidence |
|------|--------|---------|
| packet-test | ✅ pass | All required fields present, both delimiters found, packet=2883 chars |
| files-created | ✅ pass | sdk/task_packet.py exists |

## §3 Decisions / deviations

- **Import fix:** initial import used `from cognitive_arch.sdk.convention_snippet import build_snippet` — failed because "cognitive-arch" has a hyphen (not a valid Python package name). Fixed to `sys.path.insert(0, _SDK_DIR)` + `from convention_snippet import build_snippet`.
- **pyyaml added:** `requirements.txt` updated. `pip install pyyaml` ran on host machine to unblock gate.
- **Inline fallback test:** `_cli_test_inline()` creates a temporary manifest in `tempfile` dir so `--test` works even before block-031's manifest exists on disk.

## §4 Scope

No scope expansion. Files per manifest.

## §5 Token estimate

tok_in:~5000 tok_out:~2000 tok_src:estimated
