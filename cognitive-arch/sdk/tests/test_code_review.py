# sdk/tests/test_code_review.py
# PURPOSE: Validate code_review.py: rule loading, diff analysis, blocking logic,
#          bugs.md persistence, and mode-based gate decisions.
# BLOCK:   block-180

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))

from code_review import (
    Finding,
    ReviewResult,
    analyze_diff,
    append_bugs,
    build_html_section,
    load_rules,
    review_block,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_arch(tmp: str) -> Path:
    arch = Path(tmp) / "arch"
    (arch / "governance").mkdir(parents=True)
    (arch / "manifests").mkdir()
    (arch / "sdk").mkdir()
    (arch / "STATE.md").write_text("# STATE\n\np:31 status:active mode:normal\n", encoding="utf-8")
    return arch


def _simple_diff(filename: str, lines: list[str]) -> str:
    header = f"+++ b/{filename}\n@@ -0,0 +1,{len(lines)} @@\n"
    body = "\n".join("+" + l for l in lines)
    return header + body + "\n"


# ---------------------------------------------------------------------------
# Tests: rule loading
# ---------------------------------------------------------------------------

def test_load_rules_default():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        rules = load_rules(arch)
        assert len(rules) >= 5
        severities = {r.severity for r in rules}
        assert "security" in severities
        assert "bug" in severities
        assert "quality" in severities


def test_load_rules_custom():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        custom = (
            "| id | severity | category | pattern | message | suggestion | languages | enabled |\n"
            "|----|----------|----------|---------|---------|------------|-----------|--------|\n"
            "| C01 | security | test | eval\\( | eval found | remove it | py | yes |\n"
        )
        (arch / "governance" / "review-rules.md").write_text(custom, encoding="utf-8")
        rules = load_rules(arch)
        assert len(rules) == 1
        assert rules[0].id == "C01"
        assert rules[0].severity == "security"


# ---------------------------------------------------------------------------
# Tests: diff analysis
# ---------------------------------------------------------------------------

def test_no_findings_clean_diff():
    rules = load_rules(Path("."))  # uses defaults
    diff = _simple_diff("src/util.py", ["def add(a, b):", "    return a + b"])
    findings = analyze_diff(diff, rules, "block-999")
    assert findings == []


def test_finds_eval():
    rules = load_rules(Path("."))
    diff = _simple_diff("src/run.py", ["result = eval(user_input)"])
    findings = analyze_diff(diff, rules, "block-999")
    sec = [f for f in findings if f.severity == "security"]
    assert len(sec) >= 1
    assert "eval" in sec[0].message.lower()


def test_finds_hardcoded_secret():
    rules = load_rules(Path("."))
    diff = _simple_diff("config.py", ['api_key = "supersecretkey123"'])
    findings = analyze_diff(diff, rules, "block-999")
    sec = [f for f in findings if f.severity == "security"]
    assert len(sec) >= 1


def test_finds_console_log():
    rules = load_rules(Path("."))
    diff = _simple_diff("app.ts", ["console.log('debug value:', x)"])
    findings = analyze_diff(diff, rules, "block-999")
    quality = [f for f in findings if f.severity == "quality"]
    assert len(quality) >= 1


def test_finds_bare_except():
    rules = load_rules(Path("."))
    diff = _simple_diff("main.py", ["try:", "    do_thing()", "except:", "    pass"])
    findings = analyze_diff(diff, rules, "block-999")
    bugs = [f for f in findings if f.severity == "bug"]
    assert len(bugs) >= 1


# ---------------------------------------------------------------------------
# Tests: blocking logic
# ---------------------------------------------------------------------------

def test_no_findings_not_blocked():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        diff = _simple_diff("src/util.py", ["def add(a, b): return a + b"])
        result = review_block("block-999", arch, diff_text=diff, mode="normal")
        assert not result.blocked
        assert result.findings == []


def test_security_finding_blocks_normal():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        diff = _simple_diff("run.py", ["eval(user_input)"])
        result = review_block("block-999", arch, diff_text=diff, mode="normal")
        assert result.blocked
        assert "block" in result.block_reason.lower() or "halt" in result.block_reason.lower()


def test_quality_finding_does_not_block_normal():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        diff = _simple_diff("app.ts", ["console.log('debug')"])
        result = review_block("block-999", arch, diff_text=diff, mode="normal")
        assert not result.blocked
        assert any(f.severity == "quality" for f in result.findings)


def test_quality_finding_blocks_corporate():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        diff = _simple_diff("app.ts", ["console.log('debug')"])
        result = review_block("block-999", arch, diff_text=diff, mode="corporate")
        assert result.blocked


def test_force_overrides_block():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        diff = _simple_diff("run.py", ["eval(user_input)"])
        result = review_block("block-999", arch, diff_text=diff, mode="normal", force=True)
        assert not result.blocked


# ---------------------------------------------------------------------------
# Tests: bugs.md persistence
# ---------------------------------------------------------------------------

def test_bugs_md_created_and_populated():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        diff = _simple_diff("run.py", ["eval(user_input)"])
        review_block("block-999", arch, diff_text=diff, mode="normal", force=True)
        bugs_path = arch / "governance" / "bugs.md"
        assert bugs_path.exists()
        text = bugs_path.read_text(encoding="utf-8")
        assert "block-999" in text


def test_bugs_md_no_duplicates():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        findings = [
            Finding("block-999-R001", "run.py", 1, "security", "injection", "eval found", "remove"),
        ]
        append_bugs(arch, findings, "block-999")
        append_bugs(arch, findings, "block-999")
        bugs_path = arch / "governance" / "bugs.md"
        text = bugs_path.read_text(encoding="utf-8")
        assert text.count("block-999-R001") == 1


# ---------------------------------------------------------------------------
# Tests: HTML section
# ---------------------------------------------------------------------------

def test_html_no_findings():
    result = ReviewResult(block_id="block-999", findings=[], mode="normal")
    html = build_html_section(result)
    assert "Nenhuma issue" in html
    assert "Bugbot" in html


def test_html_with_findings():
    findings = [
        Finding("b999-R001", "run.py", 5, "security", "injection", "[R01] eval detected", "remove"),
        Finding("b999-R002", "app.ts", 12, "quality", "console", "[R08] console.log", "remove"),
    ]
    result = ReviewResult(block_id="block-999", findings=findings, blocked=True, mode="normal")
    html = build_html_section(result)
    assert "BLOQUEADO" in html
    assert "security" in html
    assert "run.py" in html
