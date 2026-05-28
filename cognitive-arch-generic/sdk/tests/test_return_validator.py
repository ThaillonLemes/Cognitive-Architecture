# PURPOSE: Tests for sdk/return_validator.py — validate_package(), _parse_kv(), edge cases
# INPUTS:  pytest fixtures (none needed — stateless module)
# OUTPUTS: pass/fail test results
# DEPS:    pytest, return_validator
# SEE:     manifests/block-054-test-return-validator.md, sdk/return_validator.py

import pytest
from return_validator import (
    validate_package,
    validate_rubric,
    ValidationResult,
    REQUIRED_FIELDS,
    VALID_STATUSES,
    _parse_kv,
)


# ---------------------------------------------------------------------------
# Minimal valid return package (used across tests)
# ---------------------------------------------------------------------------

_VALID_PKG = """\
b:052 sid:s-abc123 status:done ts:2026-05-22T12:00Z
gates:tests-pass:pass,file-updated:pass
fmod:sdk/tests/test_convention_snippet.py
fread:sdk/convention_snippet.py,sdk/tests/conftest.py
scope_exp:- issues:-
retro:yes retro_path:blocks/block-052-test-convention-snippet.md
tok_in:~2000 tok_out:~800 tok_src:estimated
evidence:All 13 tests pass; axiom_override type bug fixed.
"""


class TestParseKv:
    def test_simple_tokens(self):
        text = "b:052 sid:s-abc status:done"
        kv = _parse_kv(text)
        assert kv["b"] == "052"
        assert kv["sid"] == "s-abc"
        assert kv["status"] == "done"

    def test_multiline_tokens(self):
        text = "b:001 sid:s-x\nstatus:done ts:2026-05-22T00:00Z"
        kv = _parse_kv(text)
        assert kv["b"] == "001"
        assert kv["ts"] == "2026-05-22T00:00Z"

    def test_evidence_line_stored(self):
        text = "b:001 sid:s-x\nevidence:Some free-text explanation here."
        kv = _parse_kv(text)
        assert "evidence" in kv
        assert kv["evidence"] == "Some free-text explanation here."

    def test_empty_string_returns_empty_dict(self):
        assert _parse_kv("") == {}

    def test_duplicate_key_last_value_wins(self):
        text = "b:001 b:002"
        kv = _parse_kv(text)
        assert kv["b"] == "002"


class TestRequiredFields:
    def test_required_fields_count(self):
        """13 fields must be required (per REQUIRED_FIELDS constant)."""
        assert len(REQUIRED_FIELDS) == 13

    def test_b_is_required(self):
        assert "b" in REQUIRED_FIELDS

    def test_status_is_required(self):
        assert "status" in REQUIRED_FIELDS

    def test_gates_is_required(self):
        assert "gates" in REQUIRED_FIELDS

    def test_tok_in_tok_out_required(self):
        assert "tok_in" in REQUIRED_FIELDS
        assert "tok_out" in REQUIRED_FIELDS


class TestValidatePackage:
    def test_valid_package_returns_valid_true(self):
        result = validate_package(_VALID_PKG)
        assert result.valid is True
        assert result.errors == []

    def test_valid_package_parsed_fields(self):
        result = validate_package(_VALID_PKG)
        assert result.parsed["b"] == "052"
        assert result.parsed["status"] == "done"
        assert result.parsed["retro"] == "yes"

    def test_valid_package_evidence_extracted(self):
        result = validate_package(_VALID_PKG)
        assert result.evidence is not None
        assert "13 tests pass" in result.evidence

    def test_missing_b_field_invalid(self):
        pkg = _VALID_PKG.replace("b:052 ", "")
        result = validate_package(pkg)
        assert result.valid is False
        assert any("'b:'" in e for e in result.errors)

    def test_missing_gates_field_invalid(self):
        pkg = _VALID_PKG.replace(
            "gates:tests-pass:pass,file-updated:pass\n", ""
        )
        result = validate_package(pkg)
        assert result.valid is False
        assert any("'gates:'" in e for e in result.errors)

    def test_missing_tok_in_invalid(self):
        pkg = _VALID_PKG.replace("tok_in:~2000 ", "")
        result = validate_package(pkg)
        assert result.valid is False
        assert any("'tok_in:'" in e for e in result.errors)

    def test_missing_multiple_fields_reports_all(self):
        """All missing fields should be reported, not just the first."""
        pkg = "b:001\n"  # Only b: present; most fields missing
        result = validate_package(pkg)
        assert result.valid is False
        assert len(result.errors) > 1

    def test_bad_status_is_invalid(self):
        pkg = _VALID_PKG.replace("status:done", "status:running")
        result = validate_package(pkg)
        assert result.valid is False
        assert any("status" in e for e in result.errors)

    def test_all_valid_statuses_accepted(self):
        for status in VALID_STATUSES:
            pkg = _VALID_PKG.replace("status:done", f"status:{status}")
            result = validate_package(pkg)
            status_errors = [e for e in result.errors if "status" in e]
            assert status_errors == [], f"Status '{status}' was rejected: {status_errors}"

    def test_bad_gate_format_invalid(self):
        pkg = _VALID_PKG.replace(
            "gates:tests-pass:pass,file-updated:pass",
            "gates:tests-pass:maybe",
        )
        result = validate_package(pkg)
        assert result.valid is False
        assert any("gate" in e for e in result.errors)

    def test_gates_dash_accepted(self):
        """gates:- (no gates) is valid."""
        pkg = _VALID_PKG.replace(
            "gates:tests-pass:pass,file-updated:pass",
            "gates:-",
        )
        result = validate_package(pkg)
        gate_errors = [e for e in result.errors if "gate" in e]
        assert gate_errors == []

    def test_tok_in_tilde_integer_accepted(self):
        """~integer format must be accepted for tok_in."""
        pkg = _VALID_PKG.replace("tok_in:~2000", "tok_in:~500")
        result = validate_package(pkg)
        tok_errors = [e for e in result.errors if "tok_in" in e]
        assert tok_errors == []

    def test_tok_out_plain_integer_accepted(self):
        """Plain integer (no ~) must also be accepted for tok_out."""
        pkg = _VALID_PKG.replace("tok_out:~800", "tok_out:800")
        result = validate_package(pkg)
        tok_errors = [e for e in result.errors if "tok_out" in e]
        assert tok_errors == []

    def test_tok_in_non_numeric_invalid(self):
        pkg = _VALID_PKG.replace("tok_in:~2000", "tok_in:lots")
        result = validate_package(pkg)
        assert result.valid is False
        assert any("tok_in" in e for e in result.errors)

    def test_retro_yes_without_retro_path_invalid(self):
        pkg = _VALID_PKG.replace(
            "retro:yes retro_path:blocks/block-052-test-convention-snippet.md",
            "retro:yes",
        )
        result = validate_package(pkg)
        assert result.valid is False
        assert any("retro_path" in e for e in result.errors)

    def test_retro_no_without_retro_path_valid(self):
        pkg = _VALID_PKG.replace(
            "retro:yes retro_path:blocks/block-052-test-convention-snippet.md",
            "retro:no",
        )
        result = validate_package(pkg)
        retro_errors = [e for e in result.errors if "retro" in e]
        assert retro_errors == []

    def test_tok_src_actual_accepted(self):
        pkg = _VALID_PKG.replace("tok_src:estimated", "tok_src:actual")
        result = validate_package(pkg)
        tok_errors = [e for e in result.errors if "tok_src" in e]
        assert tok_errors == []

    def test_tok_src_invalid_value(self):
        pkg = _VALID_PKG.replace("tok_src:estimated", "tok_src:guessed")
        result = validate_package(pkg)
        assert result.valid is False
        assert any("tok_src" in e for e in result.errors)

    def test_returns_validation_result_type(self):
        result = validate_package(_VALID_PKG)
        assert isinstance(result, ValidationResult)

    def test_evidence_not_in_parsed_dict(self):
        """evidence must be lifted out of parsed and placed in result.evidence."""
        result = validate_package(_VALID_PKG)
        assert "evidence" not in result.parsed
        assert result.evidence is not None


# ---------------------------------------------------------------------------
# TestRetrospectiveRubric — validate_rubric() semantic checks (block-065)
# ---------------------------------------------------------------------------

_GOOD_RETRO = """
# Block 061 Retrospective

The implementation actually went differently than expected — had to split the rubric
into two files instead of one because the command update was larger than anticipated.

Gates: all passed. pytest returned exit 0 with no failures.

Fixed a small issue with the grep pattern because the original regex was too strict
and did not match numbered lists starting with double digits.

Lesson learned: next time, pre-check the grep pattern against the actual file format
before writing the gate command. Will do this for all future grep-based gates.

tok_in: 1200
tok_out: 450
"""

_RETRO_NO_DEVIATION = """
Block completed as planned. Gates passed. Tests ran fine.
Lesson learned: next time start earlier.
tok_in: 1200  tok_out: 450
"""

_RETRO_NO_GATES = """
The implementation actually went differently — had to add an extra file.
No issues encountered. Next time will plan better.
tok_in: 800 tok_out: 200
"""

_RETRO_FAILURE_NO_EXPLAIN = """
Actually the gate failed. Fixed the bug. Next time will test earlier.
pytest passed. tok_in: 500 tok_out: 150
"""

_RETRO_NO_LESSON = """
Block went well. Actually took longer than expected.
Gates passed — pytest exit 0.
tok_in: 300 tok_out: 100
"""

_RETRO_ZERO_TOKENS = """
Actually went differently than planned.
Gates passed, pytest exit 0.
Fixed the issue because the pattern was wrong — changed the regex.
Next time will double-check patterns. Will remember this.
tok_in: 0  tok_out: 0
"""


class TestRetrospectiveRubric:
    """Tests for validate_rubric() — 5-criterion semantic quality check."""

    def test_perfect_retro_no_warnings(self):
        """A retro meeting all 5 criteria returns an empty warning list."""
        warnings = validate_rubric(_GOOD_RETRO, tok_in=1200, tok_out=450)
        assert warnings == []

    def test_criterion1_no_deviation_triggers_warning(self):
        """Missing deviation mention triggers criterion-1 warning."""
        warnings = validate_rubric(_RETRO_NO_DEVIATION, tok_in=1200, tok_out=450)
        c1_warnings = [w for w in warnings if "criterion-1" in w]
        assert len(c1_warnings) == 1
        assert "criterion-1" in c1_warnings[0]

    def test_criterion2_no_gate_reference_triggers_warning(self):
        """Missing gate result reference triggers criterion-2 warning."""
        warnings = validate_rubric(_RETRO_NO_GATES, tok_in=800, tok_out=200)
        c2_warnings = [w for w in warnings if "criterion-2" in w]
        assert len(c2_warnings) == 1

    def test_criterion3_failure_without_explanation_triggers_warning(self):
        """Mentioning failure without 'because/changed/etc' triggers criterion-3 warning."""
        # _RETRO_FAILURE_NO_EXPLAIN has 'failed' and 'fixed' but not a clear explanation token
        retro = "Actually gate failed. Fixed it. Next time will test earlier. pytest ran."
        warnings = validate_rubric(retro, tok_in=500, tok_out=150)
        c3_warnings = [w for w in warnings if "criterion-3" in w]
        assert len(c3_warnings) == 1

    def test_criterion3_failure_with_explanation_no_warning(self):
        """Failure mention WITH explanation does not trigger criterion-3 warning."""
        warnings = validate_rubric(_GOOD_RETRO, tok_in=1200, tok_out=450)
        c3_warnings = [w for w in warnings if "criterion-3" in w]
        assert len(c3_warnings) == 0

    def test_criterion4_no_lesson_triggers_warning(self):
        """Missing forward-looking lesson triggers criterion-4 warning."""
        warnings = validate_rubric(_RETRO_NO_LESSON, tok_in=300, tok_out=100)
        c4_warnings = [w for w in warnings if "criterion-4" in w]
        assert len(c4_warnings) == 1

    def test_criterion5_zero_tokens_triggers_warning(self):
        """tok_in=0 or tok_out=0 triggers criterion-5 warning."""
        warnings = validate_rubric(_RETRO_ZERO_TOKENS, tok_in=0, tok_out=0)
        c5_warnings = [w for w in warnings if "criterion-5" in w]
        assert len(c5_warnings) == 1

    def test_criterion5_nonzero_tokens_no_warning(self):
        """Non-zero tok_in and tok_out do not trigger criterion-5 warning."""
        warnings = validate_rubric(_GOOD_RETRO, tok_in=1200, tok_out=450)
        c5_warnings = [w for w in warnings if "criterion-5" in w]
        assert len(c5_warnings) == 0

    def test_all_warnings_prefixed(self):
        """All returned warnings start with '[RUBRIC WARNING]'."""
        warnings = validate_rubric("minimal retro text", tok_in=0, tok_out=0)
        for w in warnings:
            assert w.startswith("[RUBRIC WARNING]"), f"Warning not prefixed: {w}"

    def test_empty_retro_returns_multiple_warnings(self):
        """An empty retro string triggers multiple warnings (at least 3)."""
        warnings = validate_rubric("", tok_in=0, tok_out=0)
        assert len(warnings) >= 3
