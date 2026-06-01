# PURPOSE: Tests for block_close.py — tok_actual enforcement (block-112) and core close flow
# INPUTS:  tmp_arch fixture, synthetic retro files
# OUTPUTS: pass/fail assertions on _check_tok_actual and close_block
# DEPS:    pytest, pathlib, block_close module
# SEE:     sdk/block_close.py, phases/phase-18.md block-112

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from block_close import _check_tok_actual, _check_retro, _check_actual_hours


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_retro(tmp_path: Path, block_id: str, content: str) -> Path:
    blocks = tmp_path / "blocks"
    blocks.mkdir(exist_ok=True)
    p = blocks / f"{block_id}-test-retro.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _check_tok_actual tests
# ---------------------------------------------------------------------------

class TestCheckTokActual:
    def test_missing_field_returns_false(self, tmp_path):
        _write_retro(tmp_path, "block-999", "---\nactual_duration_hours: 1.0\n---\n# Retro\n")
        ok, msg = _check_tok_actual(tmp_path, "block-999")
        assert ok is False
        assert "tok_actual" in msg.lower()

    def test_present_numeric_returns_true(self, tmp_path):
        _write_retro(tmp_path, "block-999", "---\ntok_actual: 1500\nactual_duration_hours: 1.0\n---\n")
        ok, msg = _check_tok_actual(tmp_path, "block-999")
        assert ok is True
        assert msg == ""

    def test_null_value_returns_false(self, tmp_path):
        _write_retro(tmp_path, "block-999", "---\ntok_actual: null\nactual_duration_hours: 1.0\n---\n")
        ok, msg = _check_tok_actual(tmp_path, "block-999")
        assert ok is False

    def test_tilde_null_returns_false(self, tmp_path):
        _write_retro(tmp_path, "block-999", "---\ntok_actual: ~\nactual_duration_hours: 1.0\n---\n")
        ok, msg = _check_tok_actual(tmp_path, "block-999")
        assert ok is False

    def test_tok_dash_actual_variant_accepted(self, tmp_path):
        _write_retro(tmp_path, "block-999", "---\ntok-actual: 800\n---\n")
        ok, msg = _check_tok_actual(tmp_path, "block-999")
        assert ok is True

    def test_tokens_actual_variant_accepted(self, tmp_path):
        _write_retro(tmp_path, "block-999", "---\ntokens_actual: 2200\n---\n")
        ok, msg = _check_tok_actual(tmp_path, "block-999")
        assert ok is True

    def test_no_retro_returns_no_retro(self, tmp_path):
        (tmp_path / "blocks").mkdir(exist_ok=True)
        ok, msg = _check_tok_actual(tmp_path, "block-nonexistent")
        assert ok is True
        assert msg == "no_retro"

    def test_force_true_is_irrelevant_to_check(self, tmp_path):
        # _check_tok_actual with force=True still returns (False, msg) — caller decides halt
        _write_retro(tmp_path, "block-999", "---\nactual_duration_hours: 1.0\n---\n")
        ok, msg = _check_tok_actual(tmp_path, "block-999", force=True)
        assert ok is False  # check still detects missing; caller skips halt when force=True


# ---------------------------------------------------------------------------
# Smoke test: close_block halts when tok_actual missing (no force)
# ---------------------------------------------------------------------------

class TestCloseBlockTokEnforcement:
    def test_close_halts_without_tok_actual(self, tmp_arch):
        from block_close import close_block
        # Write a retro without tok_actual
        (tmp_arch / "blocks").mkdir(exist_ok=True)
        (tmp_arch / "blocks" / "block-999-retro.md").write_text(
            "---\nactual_duration_hours: 1.0\n---\n# Retro\n", encoding="utf-8"
        )
        (tmp_arch / "manifests").mkdir(exist_ok=True)
        result = close_block(tmp_arch, "block-999", force=False)
        assert result.get("tok_actual_check") == "missing"
        assert result.get("halted") is True

    def test_close_proceeds_with_tok_actual(self, tmp_arch):
        from block_close import close_block
        (tmp_arch / "blocks").mkdir(exist_ok=True)
        (tmp_arch / "blocks" / "block-999-retro.md").write_text(
            "---\ntok_actual: 1500\nactual_duration_hours: 1.0\n---\n# Retro\n", encoding="utf-8"
        )
        (tmp_arch / "manifests").mkdir(exist_ok=True)
        result = close_block(tmp_arch, "block-999", force=False)
        assert result.get("tok_actual_check") == "ok"
        assert result.get("halted") is not True

    def test_close_proceeds_with_force_even_missing(self, tmp_arch):
        from block_close import close_block
        (tmp_arch / "blocks").mkdir(exist_ok=True)
        (tmp_arch / "blocks" / "block-999-retro.md").write_text(
            "---\nactual_duration_hours: 1.0\n---\n# Retro\n", encoding="utf-8"
        )
        (tmp_arch / "manifests").mkdir(exist_ok=True)
        result = close_block(tmp_arch, "block-999", force=True)
        assert result.get("halted") is not True


class TestCloseBlockRetroGate:
    def test_close_halts_without_retro(self, tmp_arch):
        from block_close import close_block
        (tmp_arch / "blocks").mkdir(exist_ok=True)
        (tmp_arch / "manifests").mkdir(exist_ok=True)
        result = close_block(tmp_arch, "block-998", force=False)
        assert result.get("retro_check") == "missing"
        assert result.get("halted") is True

    def test_close_with_force_skips_retro_halt(self, tmp_arch):
        from block_close import close_block
        (tmp_arch / "blocks").mkdir(exist_ok=True)
        (tmp_arch / "manifests").mkdir(exist_ok=True)
        result = close_block(tmp_arch, "block-998", force=True)
        assert result.get("halted") is not True
