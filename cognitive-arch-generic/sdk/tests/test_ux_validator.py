# PURPOSE: Tests for sdk/ux_validator.py (block-134)
# INPUTS:  tmp_path, synthetic ux-voice.md content and target text
# OUTPUTS: assertions on violation detection and reporting
# DEPS:    pytest, pathlib, ux_validator module
# SEE:     sdk/ux_validator.py, governance/ux-voice.md, phases/phase-22.md block-134

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from ux_validator import UxValidator, Violation, _extract_prohibited, _format_violations


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_UX_VOICE_WITH_PROHIBITED = """\
# ux-voice.md
## 3. Prohibited Patterns

```prohibited
Certainly!
I'll now
Great question
I hope this helps
```
"""

_CLEAN_TEXT = "The gate passed. Tests: 655 passed, 0 failed.\nBlock 134 done — next: phase-22-close."

_DIRTY_TEXT = "Certainly! I'll now walk you through this. Great question!\nI hope this helps!"


def _make_ux_voice(tmp_path: Path, content: str = _UX_VOICE_WITH_PROHIBITED) -> Path:
    gov = tmp_path / "governance"
    gov.mkdir(exist_ok=True)
    path = gov / "ux-voice.md"
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# _extract_prohibited
# ---------------------------------------------------------------------------

class TestExtractProhibited:
    def test_extracts_phrases(self):
        phrases = _extract_prohibited(_UX_VOICE_WITH_PROHIBITED)
        assert "Certainly!" in phrases
        assert "I'll now" in phrases

    def test_empty_on_missing_block(self):
        assert _extract_prohibited("# no fenced block here") == []

    def test_strips_blank_lines(self):
        text = "```prohibited\nCertainly!\n\nHello\n```"
        phrases = _extract_prohibited(text)
        assert "" not in phrases
        assert "Certainly!" in phrases
        assert "Hello" in phrases


# ---------------------------------------------------------------------------
# UxValidator.from_ux_voice
# ---------------------------------------------------------------------------

class TestUxValidatorFactory:
    def test_loads_rules_from_ux_voice(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        assert "Certainly!" in v.prohibited_phrases

    def test_empty_on_missing_file(self, tmp_path):
        v = UxValidator.from_ux_voice(tmp_path)
        assert v.prohibited_phrases == []


# ---------------------------------------------------------------------------
# UxValidator.check — clean text
# ---------------------------------------------------------------------------

class TestUxValidatorCheckClean:
    def test_no_violations_on_clean_text(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        assert v.check(_CLEAN_TEXT) == []

    def test_self_check_ux_voice_has_no_violations(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        ux_text = (tmp_path / "governance" / "ux-voice.md").read_text(encoding="utf-8")
        violations = v.check(ux_text)
        assert violations == []


# ---------------------------------------------------------------------------
# UxValidator.check — dirty text
# ---------------------------------------------------------------------------

class TestUxValidatorCheckDirty:
    def test_detects_prohibited_phrase(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        violations = v.check("Certainly! This is great.")
        assert len(violations) >= 1
        assert any(viol.rule_id == "UX-PROHIBITED" for viol in violations)

    def test_detects_multiple_violations(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        violations = v.check(_DIRTY_TEXT)
        assert len(violations) >= 3

    def test_violation_has_correct_line_number(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        text = "Line 1 clean\nLine 2 has Certainly!\nLine 3 clean"
        violations = v.check(text)
        assert any(viol.line_num == 2 for viol in violations)

    def test_violation_excerpt_is_truncated(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        long_line = "Certainly! " + "x" * 200
        violations = v.check(long_line)
        assert any(len(viol.excerpt) <= 80 for viol in violations)

    def test_case_insensitive_match(self, tmp_path):
        _make_ux_voice(tmp_path)
        v = UxValidator.from_ux_voice(tmp_path)
        violations = v.check("certainly! this is fine")
        assert len(violations) >= 1


# ---------------------------------------------------------------------------
# _format_violations
# ---------------------------------------------------------------------------

class TestFormatViolations:
    def test_ok_message_on_empty(self):
        output = _format_violations([])
        assert "0 violations" in output

    def test_warn_lines_present(self):
        v = Violation(line_num=3, rule_id="UX-PROHIBITED",
                      message='Prohibited phrase: "Certainly!"', excerpt="Certainly! great.")
        output = _format_violations([v])
        assert "WARN" in output
        assert "L3" in output
        assert "Certainly!" in output

    def test_truncation_at_max(self):
        violations = [
            Violation(line_num=i, rule_id="UX-PROHIBITED", message=f"phrase {i}", excerpt="x")
            for i in range(25)
        ]
        output = _format_violations(violations, max_display=5)
        assert "20 more" in output


# ---------------------------------------------------------------------------
# Exit code
# ---------------------------------------------------------------------------

class TestExitCodeAlwaysZero:
    def test_main_with_violations_exits_zero(self, tmp_path):
        _make_ux_voice(tmp_path)
        dirty = tmp_path / "dirty.txt"
        dirty.write_text(_DIRTY_TEXT, encoding="utf-8")
        from ux_validator import main
        code = main(["--arch-root", str(tmp_path), "--check", str(dirty)])
        assert code == 0

    def test_main_with_clean_file_exits_zero(self, tmp_path):
        _make_ux_voice(tmp_path)
        clean = tmp_path / "clean.txt"
        clean.write_text(_CLEAN_TEXT, encoding="utf-8")
        from ux_validator import main
        code = main(["--arch-root", str(tmp_path), "--check", str(clean)])
        assert code == 0

    def test_main_missing_file_exits_zero(self, tmp_path):
        _make_ux_voice(tmp_path)
        from ux_validator import main
        code = main(["--arch-root", str(tmp_path), "--check", str(tmp_path / "nonexistent.txt")])
        assert code == 0
