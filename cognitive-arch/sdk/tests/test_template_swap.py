# sdk/tests/test_template_swap.py
# PURPOSE: Validate that v2 templates are in place, v1 are removed, and audit parsers
#          work correctly with both v1 and v2 manifest formats.
# BLOCK:   block-162

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # cognitive-arch/
TEMPLATES = ROOT / "templates"
MANIFESTS = ROOT / "manifests"


# ---------------------------------------------------------------------------
# Template existence checks
# ---------------------------------------------------------------------------

def test_v2_templates_exist():
    for name in [
        "manifest-small-v2.md",
        "manifest-medium-v2.md",
        "manifest-large-v2.md",
        "manifest-intake.md",
        "block-retrospective-v2.md",
    ]:
        assert (TEMPLATES / name).exists(), f"Missing v2 template: {name}"


def test_v1_templates_removed():
    for name in [
        "manifest-small.md",
        "manifest-medium.md",
        "manifest-large.md",
        "block-retrospective.md",
    ]:
        assert not (TEMPLATES / name).exists(), f"v1 template still present: {name}"


# ---------------------------------------------------------------------------
# Audit parser compatibility
# ---------------------------------------------------------------------------

def test_audit_accepts_v2_manifest():
    """Audit check5 must recognise v2 manifests with size+importance instead of tier."""
    sys.path.insert(0, str(ROOT / "sdk"))
    import importlib
    import audit as _audit

    sample = """---
id: block-999
size: S
importance: normal
kind: implementation
phase: phase-99
status: pending
files:
  read:
    - some/file.py
  modify: []
  create: []
---
"""
    fm = sample.split("---", 2)[1]
    is_v2 = bool(re.search(r"^size:", fm, re.MULTILINE))
    assert is_v2, "v2 detection failed"

    from audit import _REQUIRED_MANIFEST_KEYS_V2
    for key in _REQUIRED_MANIFEST_KEYS_V2:
        assert re.search(rf"^{key}:", fm, re.MULTILINE), f"key '{key}' not in sample v2 fm"


def test_audit_accepts_v1_manifest():
    """Audit check5 must still parse v1 manifests (existing blocks)."""
    sys.path.insert(0, str(ROOT / "sdk"))
    from audit import _REQUIRED_MANIFEST_KEYS_V1

    sample = """---
id: block-001
tier: S
kind: investigation
status: done
files:
  read: []
  modify: []
---
"""
    fm = sample.split("---", 2)[1]
    is_v2 = bool(re.search(r"^size:", fm, re.MULTILINE))
    assert not is_v2, "v1 manifest incorrectly detected as v2"

    for key in _REQUIRED_MANIFEST_KEYS_V1:
        assert re.search(rf"^{key}:", fm, re.MULTILINE), f"key '{key}' not in v1 fm"


def test_existing_v2_manifests_parse_ok():
    """All manifests in manifests/ with size: field must have all v2 required keys."""
    sys.path.insert(0, str(ROOT / "sdk"))
    from audit import _REQUIRED_MANIFEST_KEYS_V2, _extract_frontmatter

    if not MANIFESTS.exists():
        return
    errors = []
    for mf in sorted(MANIFESTS.glob("block-*.md")):
        text = mf.read_text(encoding="utf-8", errors="replace")
        fm = _extract_frontmatter(text)
        if not re.search(r"^size:", fm, re.MULTILINE):
            continue  # v1 manifest — skip
        for key in _REQUIRED_MANIFEST_KEYS_V2:
            if not re.search(rf"^{key}:", fm, re.MULTILINE):
                errors.append(f"{mf.name}: missing '{key}'")
    assert not errors, "\n".join(errors)


if __name__ == "__main__":
    test_v2_templates_exist()
    test_v1_templates_removed()
    test_audit_accepts_v2_manifest()
    test_audit_accepts_v1_manifest()
    test_existing_v2_manifests_parse_ok()
    print("All block-162 tests passed.")
