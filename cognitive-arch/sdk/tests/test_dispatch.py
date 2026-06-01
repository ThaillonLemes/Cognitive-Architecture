# PURPOSE: Tests for sdk/dispatch.py — dispatch_block(), MockAnthropicClient, DispatchResult
# INPUTS:  pytest fixtures (none needed — stateless module in mock mode)
# OUTPUTS: pass/fail test results
# DEPS:    pytest, dispatch
# SEE:     manifests/block-055-test-dispatch-integration.md, sdk/dispatch.py

import pytest
from dispatch import (
    dispatch_block,
    dispatch_batch,
    DispatchResult,
    MockAnthropicClient,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT_SEC,
    DEFAULT_MAX_RETRIES,
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

    def test_default_max_retries_non_negative(self):
        assert isinstance(DEFAULT_MAX_RETRIES, int)
        assert DEFAULT_MAX_RETRIES >= 0


class TestDispatchTimeoutWired:
    def test_sdk_dispatch_accepts_timeout_param(self):
        import inspect
        from dispatch import _sdk_dispatch
        sig = inspect.signature(_sdk_dispatch)
        assert "timeout_sec" in sig.parameters

    def test_dispatch_block_passes_timeout_to_sdk(self, monkeypatch):
        """dispatch_block with mode=sdk passes timeout_sec to _sdk_dispatch."""
        captured = {}

        def fake_sdk(packet, api_key, model, max_tokens, timeout_sec, max_retries):
            captured["timeout_sec"] = timeout_sec
            return ("b:test status:done ts:2026-01-01T00:00Z gates:- fmod:- fread:- "
                    "scope_exp:- issues:- retro:yes retro_path:- tok_in:0 tok_out:0 tok_src:estimated", 0, 0, 1)

        monkeypatch.setattr("dispatch._sdk_dispatch", fake_sdk)
        from dispatch import dispatch_block
        dispatch_block("b:test", mode="sdk", api_key="fake-key", timeout_sec=42.0)
        assert captured.get("timeout_sec") == 42.0

    def test_sdk_dispatch_accepts_max_retries_param(self):
        import inspect
        from dispatch import _sdk_dispatch
        sig = inspect.signature(_sdk_dispatch)
        assert "max_retries" in sig.parameters

    def test_dispatch_block_passes_max_retries_to_sdk(self, monkeypatch):
        """dispatch_block passes max_retries through to _sdk_dispatch."""
        captured = {}

        def fake_sdk(packet, api_key, model, max_tokens, timeout_sec, max_retries):
            captured["max_retries"] = max_retries
            return ("b:test status:done ts:2026-01-01T00:00Z gates:- fmod:- fread:- "
                    "scope_exp:- issues:- retro:yes retro_path:- tok_in:0 tok_out:0 tok_src:estimated", 0, 0, 1)

        monkeypatch.setattr("dispatch._sdk_dispatch", fake_sdk)
        dispatch_block("b:test", mode="sdk", api_key="fake-key", max_retries=5)
        assert captured.get("max_retries") == 5


class TestDispatchRetry:
    """Verify retry/metadata contract at the dispatch_block interface level."""

    _VALID_RESPONSE = (
        "b:033 sid:s-test01 status:done ts:2026-01-01T00:00Z gates:- fmod:- fread:- "
        "scope_exp:- issues:- retro:yes retro_path:blocks/block-033-retro.md tok_in:0 tok_out:0 tok_src:estimated"
    )

    def test_sdk_metadata_has_attempts_on_success(self, monkeypatch):
        """metadata['attempts'] equals the attempt count returned by _sdk_dispatch."""
        def fake_sdk(packet, api_key, model, max_tokens, timeout_sec, max_retries):
            return (self._VALID_RESPONSE, 10, 50, 2)

        monkeypatch.setattr("dispatch._sdk_dispatch", fake_sdk)
        result = dispatch_block(_SAMPLE_PACKET, mode="sdk", api_key="fake-key")
        assert result.success is True
        assert result.metadata.get("attempts") == 2

    def test_sdk_metadata_has_attempts_on_failure(self, monkeypatch):
        """metadata['attempts'] = max_retries + 1 when all retries are exhausted."""
        def always_fail(packet, api_key, model, max_tokens, timeout_sec, max_retries):
            raise ConnectionError("persistent failure")

        monkeypatch.setattr("dispatch._sdk_dispatch", always_fail)
        result = dispatch_block(_SAMPLE_PACKET, mode="sdk", api_key="fake-key", max_retries=2)
        assert result.success is False
        assert "persistent failure" in result.error
        assert result.metadata.get("attempts") == 3  # max_retries + 1

    def test_mock_mode_has_no_attempts_metadata(self):
        """Mock mode does not set metadata['attempts'] (retry is SDK-only)."""
        result = dispatch_block(_SAMPLE_PACKET, mode="mock")
        assert "attempts" not in result.metadata

    def test_sdk_dispatch_returns_four_tuple(self, monkeypatch):
        """_sdk_dispatch return value is unpacked as (raw, tok_in, tok_out, attempts)."""
        def fake_sdk(packet, api_key, model, max_tokens, timeout_sec, max_retries):
            return (self._VALID_RESPONSE, 100, 200, 1)

        monkeypatch.setattr("dispatch._sdk_dispatch", fake_sdk)
        result = dispatch_block(_SAMPLE_PACKET, mode="sdk", api_key="fake-key")
        assert result.tok_in == 100
        assert result.tok_out == 200
        assert result.metadata.get("attempts") == 1


class TestDispatchBatchRetry:
    """Verify dispatch_batch passes max_retries through to each worker."""

    def test_batch_passes_max_retries_to_workers(self, monkeypatch):
        captured = []

        def fake_block(packet, mode, api_key, model, max_tokens, timeout_sec, max_retries):
            captured.append(max_retries)
            from dispatch import DispatchResult
            return DispatchResult(block_id="033", mode=mode, success=True, metadata={"attempts": 1})

        monkeypatch.setattr("dispatch.dispatch_block", fake_block)
        dispatch_batch([_SAMPLE_PACKET, _SAMPLE_PACKET], mode="mock", max_retries=3)
        assert all(r == 3 for r in captured)
