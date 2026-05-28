# PURPOSE: Tests for sdk/dispatch.py — dispatch_block(), MockAnthropicClient, DispatchResult
# INPUTS:  pytest fixtures (none needed — stateless module in mock mode)
# OUTPUTS: pass/fail test results
# DEPS:    pytest, dispatch
# SEE:     manifests/block-055-test-dispatch-integration.md, sdk/dispatch.py

import pytest
from dispatch import (
    dispatch_block,
    DispatchResult,
    MockAnthropicClient,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT_SEC,
)


_SAMPLE_PACKET = (
    "b:033 kind:feature phase:phase-5 gov:g-test ts:2026-05-22T12:00Z\n"
    "axioms:Q1,Q2 scope:open retro_req:yes tok_track:yes\n"
    "fread:PROTOCOLS.md fmod:sdk/dispatch.py\n"
    "\n"
    "--- convention snippet ---\n"
    "Q3: Manifests precede work artifacts.\n"
    "\n"
    "--- manifest ---\n"
    "[test manifest]\n"
)


class TestMockAnthropicClient:
    def test_dispatch_returns_string(self):
        client = MockAnthropicClient(block_id="033")
        result = client.dispatch(_SAMPLE_PACKET)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_dispatch_contains_block_id(self):
        client = MockAnthropicClient(block_id="033")
        result = client.dispatch(_SAMPLE_PACKET)
        assert "b:033" in result

    def test_dispatch_extracts_block_id_from_packet(self):
        """MockAnthropicClient should read block ID from packet when not pre-set."""
        client = MockAnthropicClient()
        result = client.dispatch(_SAMPLE_PACKET)
        assert "b:033" in result

    def test_mock_response_contains_required_fields(self):
        """Mock return package should have all fields required by return_validator."""
        client = MockAnthropicClient(block_id="055")
        raw = client.dispatch(_SAMPLE_PACKET)
        for field in ["b:", "sid:", "status:", "ts:", "gates:", "fmod:", "fread:",
                      "scope_exp:", "issues:", "retro:", "tok_in:", "tok_out:", "tok_src:"]:
            assert field in raw, f"Missing field '{field}' in mock response"


class TestDispatchBlock:
    def test_mock_dispatch_returns_dispatch_result(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert isinstance(result, DispatchResult)

    def test_mock_dispatch_success_true(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.success is True

    def test_mock_dispatch_mode_field(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.mode == "mock"

    def test_mock_dispatch_block_id_extracted(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.block_id == "033"

    def test_mock_dispatch_validation_not_none(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.validation is not None

    def test_mock_dispatch_validation_valid(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.validation.valid is True

    def test_mock_dispatch_elapsed_sec_non_negative(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.elapsed_sec >= 0.0

    def test_mock_dispatch_raw_response_non_empty(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.raw_response != ""

    def test_mock_dispatch_error_is_none_on_success(self):
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert result.error is None

    def test_manual_dispatch_success_true(self, capsys):
        result = dispatch_block(_SAMPLE_PACKET, mode="manual")
        assert result.success is True
        assert result.mode == "manual"

    def test_manual_dispatch_validation_is_none(self, capsys):
        """Manual mode prints packet but doesn't validate a response."""
        result = dispatch_block(_SAMPLE_PACKET, mode="manual")
        assert result.validation is None

    def test_sdk_without_api_key_returns_failure(self, monkeypatch):
        """SDK mode without API key must return success=False with an error message."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        result = dispatch_block(_SAMPLE_PACKET, mode="sdk", api_key="")
        assert result.success is False
        assert result.error is not None
        assert "API key" in result.error

    def test_dispatch_result_has_tok_in_tok_out(self):
        """Mock dispatch must return positive tok_in and tok_out (realistic placeholders)."""
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert isinstance(result.tok_in, int)
        assert isinstance(result.tok_out, int)
        assert result.tok_in > 0
        assert result.tok_out > 0


class TestDispatchConstants:
    def test_default_model_set(self):
        assert isinstance(DEFAULT_MODEL, str)
        assert len(DEFAULT_MODEL) > 0

    def test_default_max_tokens_positive(self):
        assert DEFAULT_MAX_TOKENS > 0

    def test_default_timeout_positive(self):
        assert DEFAULT_TIMEOUT_SEC > 0
