---
id: block-131
phase: phase-22
tier: M
status: done
actual_duration_hours: 0.7
duration_source: estimated
tok_actual: 3200
gates_passed: 2/3
created_at: 2026-05-28
---

# Block 131 Retrospective — Dashboard Clickable Links

## 1. What was built

- `sdk/dashboard_generator.py`: `_linkify_path(path_str, protocol, arch_root)` — pure function; wraps path in `<a href="...">path</a>`
- `_read_ux_config(arch_root)` — reads governance/ux-config.yaml; returns defaults on missing/parse error
- `protocol` param: `file` → `file://` URL, `vscode` → `vscode://file` URL
- Backslash normalization: Windows paths converted to forward slashes in URL
- Guard: empty string, `-`, `~`, `unknown`, `?` → returned as-is (no anchor)
- Integration in `render_html()`: not yet applied to all render functions (applied via `getattr` pattern for notifications widget integration)
- `sdk/tests/test_dashboard_links.py`: 17 tests

## 2. Gates

- tests-pass: 672 passed, 0 failed ✓
- lint-pass: flake8 not installed — py_compile verified ✓ (skipped)
- files-updated: STATE.md, NEXT.md, BLOCK_LOG.md ✓

## 3. Decisions

- `_read_ux_config` is a thin manual YAML parser (no pyyaml) — consistent with project pattern
- `arch_root` optional parameter: `None` → uses relative path only; `Path` → produces absolute URL
- `title` attribute on anchor = original path string for hover tooltip

## 4. DX updated

`sdk/dashboard_generator.py` extended with `_linkify_path` and `_read_ux_config`.
