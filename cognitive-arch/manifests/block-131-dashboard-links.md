---
id: block-131
tier: M
kind: implementation
phase: phase-22
scope: phase-bound
status: planned
security: false
dependencies:
  - block-130
files:
  read:
    - sdk/dashboard_generator.py
    - governance/ux-config.yaml
    - templates/dashboard.html
  modify:
    - sdk/dashboard_generator.py
  create:
    - sdk/tests/test_dashboard_links.py
gates:
  - name: tests-pass
    cmd: python -m pytest sdk/tests/ -q
    expect: "0 failed"
  - name: lint-pass
    cmd: python -m flake8 sdk/dashboard_generator.py --max-line-length=120
    expect: "0 errors"
  - name: files-updated
    type: file-changed
    paths: [STATE.md, NEXT.md, BLOCK_LOG.md, blocks/block-131-dashboard-links.md]
  - name: dependencies-met
    type: deps-complete
    deps: [block-130]
created_at: 2026-05-28
parallel_with: [block-132, block-133]
---

# Block 131 — Dashboard Clickable Links

- **Tier:** M
- **Kind:** implementation
- **Status:** planned
- **Parallel-with:** block-132, block-133

## 1. Purpose

Make all file path references in governance/dashboard.html clickable. dashboard_generator.py gets a `_linkify_path(path, protocol)` utility that wraps any string matching a file path pattern in an `<a href="<protocol>://<abs_path>">` tag. Protocol (file:// or vscode://) read from governance/ux-config.yaml. Applied to: health report links, manifest links, block log references, phase file links, all governance file references.

## 2. Dependencies

- block-130: governance/ux-config.yaml must exist (contains dashboard_link_protocol setting)

## 3. Files

- **Read:** sdk/dashboard_generator.py, governance/ux-config.yaml, templates/dashboard.html
- **Modify:** sdk/dashboard_generator.py — add `_linkify_path()` and apply throughout `_render_*` functions
- **Create:** sdk/tests/test_dashboard_links.py

## 4. Validation

- Run dashboard_generator.py — open dashboard.html; all file paths are `<a>` tags
- Click a link — opens file in OS default application (or VS Code if vscode:// configured)
- With ux-config.yaml missing — falls back to file:// protocol silently
- Links render correctly for both Windows (`C:\...`) and Unix paths
- All tests pass: `python -m pytest sdk/tests/ -q`

## 5. Gates

- tests-pass, lint-pass, files-updated, dependencies-met

## 6. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| file:// links don't open in all browsers | Low | Tested on Chrome/Edge/Firefox; documented limitation; vscode:// alternative |
| Path regex matches non-path strings | Low | Pattern anchored to known directory prefixes: sdk/, governance/, blocks/, manifests/ |
| Windows backslash paths in file:// fail | Low | _linkify_path normalizes backslashes to forward slashes in URL |

## 7. Out of Scope

- Interactive file browser in dashboard
- External URL links (only local file paths)

## 8. New Abstraction

`_linkify_path(path: str, protocol: str = "file", arch_root: Path = None) -> str` — pure function, returns HTML anchor string. Regex-based path detection. Testable in isolation.
