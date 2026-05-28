# cognitive-arch / sdk/tests/test_agent_messages.py
# purpose: Unit tests for sdk/agent_message_schema.py
# stdlib-only; no external dependencies

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_message_schema import (
    AgentMessage,
    validate,
    is_valid,
    create_message,
    create_response,
    VALID_KINDS,
    SCHEMA_VERSION,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TS = "2026-05-27T12:00:00+00:00"


def _valid_request(**overrides) -> dict:
    base = {
        "schema_version": SCHEMA_VERSION,
        "from": "master",
        "to": "implementer",
        "kind": "request",
        "sent_at": _TS,
        "payload": {"action": "block_status", "args": {"block_id": "block-101"}},
        "expects_response": True,
    }
    base.update(overrides)
    return base


def _valid_notification(**overrides) -> dict:
    base = {
        "schema_version": SCHEMA_VERSION,
        "from": "master",
        "to": "implementer",
        "kind": "notification",
        "sent_at": _TS,
        "payload": {"event": "tool_overdue", "data": {"tool_id": "audit"}},
        "expects_response": False,
    }
    base.update(overrides)
    return base


def _valid_response(**overrides) -> dict:
    base = {
        "schema_version": SCHEMA_VERSION,
        "from": "implementer",
        "to": "master",
        "kind": "response",
        "sent_at": _TS,
        "payload": {"status": "ok", "result": {"block": "wip"}},
        "expects_response": False,
        "correlation_id": "req-001",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Tests: validate — happy paths
# ---------------------------------------------------------------------------

def test_valid_request_message():
    assert validate(_valid_request()) == []


def test_valid_notification_message():
    assert validate(_valid_notification()) == []


def test_valid_response_message():
    assert validate(_valid_response()) == []


def test_is_valid_returns_true_for_valid():
    assert is_valid(_valid_request()) is True


# ---------------------------------------------------------------------------
# Tests: validate — malformed messages (5 cases)
# ---------------------------------------------------------------------------

def test_missing_from_field():
    msg = _valid_request()
    del msg["from"]
    errors = validate(msg)
    assert any("from" in e for e in errors)


def test_missing_to_field():
    msg = _valid_request()
    del msg["to"]
    errors = validate(msg)
    assert any("to" in e for e in errors)


def test_invalid_kind():
    msg = _valid_request(kind="broadcast")
    errors = validate(msg)
    assert any("kind" in e for e in errors)


def test_empty_from_string():
    msg = _valid_request(**{"from": "  "})
    errors = validate(msg)
    assert any("from" in e for e in errors)


def test_payload_not_dict():
    msg = _valid_request(payload=["item1", "item2"])
    errors = validate(msg)
    assert any("payload" in e for e in errors)


def test_not_a_dict_input():
    errors = validate("this is not a dict")
    assert len(errors) == 1
    assert "dict" in errors[0]


def test_is_valid_returns_false_for_invalid():
    assert is_valid(_valid_request(kind="INVALID")) is False


# ---------------------------------------------------------------------------
# Tests: create_message
# ---------------------------------------------------------------------------

def test_create_message_produces_valid_output():
    msg = create_message(
        from_id="master", to="implementer", kind="request",
        payload={"action": "ping"}, now_ts=_TS,
    )
    assert is_valid(msg)


def test_create_message_sets_schema_version():
    msg = create_message("master", "implementer", "notification", {}, now_ts=_TS)
    assert msg["schema_version"] == SCHEMA_VERSION


def test_create_message_invalid_kind_raises():
    with pytest.raises(ValueError):
        create_message("master", "implementer", "broadcast", {})


def test_create_message_empty_from_raises():
    with pytest.raises(ValueError):
        create_message("", "implementer", "request", {})


def test_create_message_includes_correlation_id():
    msg = create_message(
        "master", "implementer", "request", {},
        correlation_id="corr-001", now_ts=_TS,
    )
    assert msg.get("correlation_id") == "corr-001"


def test_create_message_extensions_included():
    msg = create_message(
        "master", "implementer", "notification", {},
        extensions={"custom": "value"}, now_ts=_TS,
    )
    assert msg.get("extensions") == {"custom": "value"}


# ---------------------------------------------------------------------------
# Tests: create_response
# ---------------------------------------------------------------------------

def test_create_response_correlated_to_request():
    req = create_message(
        "master", "implementer", "request",
        {"action": "check"}, expects_response=True,
        correlation_id="req-abc", now_ts=_TS,
    )
    resp = create_response(req, from_id="implementer", status="ok", result=42, now_ts=_TS)
    assert resp["kind"] == "response"
    assert resp["correlation_id"] == "req-abc"
    assert resp["to"] == "master"
    assert resp["payload"]["status"] == "ok"
    assert resp["payload"]["result"] == 42


def test_create_response_is_valid():
    req = create_message("master", "agent-1", "request", {"action": "status"}, now_ts=_TS)
    resp = create_response(req, from_id="agent-1", now_ts=_TS)
    assert is_valid(resp)


# ---------------------------------------------------------------------------
# Tests: AgentMessage dataclass
# ---------------------------------------------------------------------------

def test_agent_message_from_dict_valid():
    msg_dict = _valid_request()
    msg = AgentMessage.from_dict(msg_dict)
    assert msg.from_id == "master"
    assert msg.to == "implementer"
    assert msg.kind == "request"


def test_agent_message_from_dict_invalid_raises():
    with pytest.raises(ValueError):
        AgentMessage.from_dict({"from": "master"})  # missing required fields


def test_agent_message_to_dict_round_trip():
    orig = _valid_notification()
    msg = AgentMessage.from_dict(orig)
    result = msg.to_dict()
    assert result["from"] == "master"
    assert result["kind"] == "notification"


def test_agent_message_audit_line():
    msg = AgentMessage.from_dict(_valid_request())
    line = msg.audit_line()
    assert "master" in line
    assert "implementer" in line
    assert "request" in line
