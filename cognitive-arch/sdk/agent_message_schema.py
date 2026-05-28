# cognitive-arch / sdk/agent_message_schema.py
# purpose: AgentMessage schema validator and factory for inter-agent communication (D4).
# stdlib-only; no external dependencies

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
import uuid

SCHEMA_VERSION = "1.0"
VALID_KINDS = frozenset({"request", "notification", "response"})

REQUIRED_FIELDS = ("schema_version", "from", "to", "kind", "sent_at", "payload")


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class AgentMessage:
    """Structured inter-agent message (v1.0 schema)."""
    from_id: str           # maps to YAML key "from"
    to: str
    kind: str              # "request" | "notification" | "response"
    payload: dict
    expects_response: bool = False
    correlation_id: Optional[str] = None
    deadline: Optional[str] = None
    sent_at: str = ""
    schema_version: str = SCHEMA_VERSION
    extensions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to a plain dict ready for YAML output."""
        d: dict = {
            "schema_version": self.schema_version,
            "from": self.from_id,
            "to": self.to,
            "kind": self.kind,
            "sent_at": self.sent_at or datetime.now(timezone.utc).isoformat(),
            "payload": self.payload,
            "expects_response": self.expects_response,
        }
        if self.correlation_id is not None:
            d["correlation_id"] = self.correlation_id
        if self.deadline is not None:
            d["deadline"] = self.deadline
        if self.extensions:
            d["extensions"] = self.extensions
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AgentMessage":
        """Deserialize from a plain dict. Raises ValueError if invalid."""
        errors = validate(d)
        if errors:
            raise ValueError(f"Invalid AgentMessage: {'; '.join(errors)}")
        return cls(
            from_id=d["from"],
            to=d["to"],
            kind=d["kind"],
            payload=d["payload"],
            expects_response=bool(d.get("expects_response", False)),
            correlation_id=d.get("correlation_id"),
            deadline=d.get("deadline"),
            sent_at=d.get("sent_at", ""),
            schema_version=d.get("schema_version", SCHEMA_VERSION),
            extensions=dict(d.get("extensions") or {}),
        )

    def audit_line(self) -> str:
        """One-line summary for master-log.md."""
        ts = self.sent_at[:19] if self.sent_at else "unknown"
        corr = f" corr:{self.correlation_id}" if self.correlation_id else ""
        return (
            f"[{ts}Z] MSG from:{self.from_id} to:{self.to} "
            f"kind:{self.kind}{corr}"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(d: Any) -> list[str]:
    """
    Validate a message dict against the v1.0 schema.

    Returns a list of error strings. Empty list = valid message.
    """
    errors: list[str] = []

    if not isinstance(d, dict):
        return ["message must be a dict"]

    # Required field presence
    for req in REQUIRED_FIELDS:
        if req not in d:
            errors.append(f"missing required field: '{req}'")

    if errors:
        # Missing required fields make further checks unreliable
        return errors

    # Type and value checks
    if not isinstance(d["schema_version"], str) or not d["schema_version"]:
        errors.append("'schema_version' must be a non-empty string")

    if not isinstance(d["from"], str) or not d["from"].strip():
        errors.append("'from' must be a non-empty string")

    if not isinstance(d["to"], str) or not d["to"].strip():
        errors.append("'to' must be a non-empty string")

    if d["kind"] not in VALID_KINDS:
        errors.append(f"'kind' must be one of {sorted(VALID_KINDS)}; got '{d['kind']}'")

    if not isinstance(d["sent_at"], str) or not d["sent_at"]:
        errors.append("'sent_at' must be a non-empty string")

    if not isinstance(d["payload"], dict):
        errors.append(f"'payload' must be a dict; got {type(d['payload']).__name__}")

    # Optional field type checks (only when present)
    if "expects_response" in d and not isinstance(d["expects_response"], bool):
        errors.append("'expects_response' must be a bool")

    if "correlation_id" in d and d["correlation_id"] is not None:
        if not isinstance(d["correlation_id"], str):
            errors.append("'correlation_id' must be a string or null")

    if "extensions" in d and d["extensions"] is not None:
        if not isinstance(d["extensions"], dict):
            errors.append("'extensions' must be a dict or null")

    return errors


def is_valid(d: Any) -> bool:
    """Return True if the message dict is valid."""
    return len(validate(d)) == 0


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_message(
    from_id: str,
    to: str,
    kind: str,
    payload: dict,
    expects_response: bool = False,
    correlation_id: Optional[str] = None,
    deadline: Optional[str] = None,
    extensions: Optional[dict] = None,
    now_ts: Optional[str] = None,
) -> dict:
    """
    Create a valid message dict.

    Raises ValueError if kind is invalid or from/to are empty.
    """
    if kind not in VALID_KINDS:
        raise ValueError(f"kind must be one of {sorted(VALID_KINDS)}; got '{kind}'")
    if not from_id or not from_id.strip():
        raise ValueError("from_id must be non-empty")
    if not to or not to.strip():
        raise ValueError("to must be non-empty")

    msg: dict = {
        "schema_version": SCHEMA_VERSION,
        "from": from_id,
        "to": to,
        "kind": kind,
        "sent_at": now_ts or datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "expects_response": expects_response,
    }
    if correlation_id is not None:
        msg["correlation_id"] = correlation_id
    if deadline is not None:
        msg["deadline"] = deadline
    if extensions:
        msg["extensions"] = extensions
    return msg


def create_response(
    request_msg: dict,
    from_id: str,
    status: str = "ok",
    result: Any = None,
    error_message: Optional[str] = None,
    now_ts: Optional[str] = None,
) -> dict:
    """Create a response message correlated to a request."""
    payload: dict = {"status": status}
    if result is not None:
        payload["result"] = result
    if error_message is not None:
        payload["error_message"] = error_message
    return create_message(
        from_id=from_id,
        to=request_msg.get("from", ""),
        kind="response",
        payload=payload,
        correlation_id=request_msg.get("correlation_id"),
        now_ts=now_ts,
    )


# ---------------------------------------------------------------------------
# CLI (minimal demo)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json, sys

    ts = "2026-05-27T12:00:00+00:00"

    # Demo: create and validate three message kinds
    req = create_message(
        from_id="master", to="implementer", kind="request",
        payload={"action": "block_status", "args": {"block_id": "block-101"}},
        expects_response=True, now_ts=ts,
    )
    notif = create_message(
        from_id="master", to="implementer", kind="notification",
        payload={"event": "tool_overdue", "data": {"tool_id": "audit", "days_overdue": 3.1}},
        now_ts=ts,
    )
    resp = create_response(request_msg=req, from_id="implementer", result={"status": "wip"}, now_ts=ts)

    for msg in (req, notif, resp):
        errors = validate(msg)
        status = "VALID" if not errors else f"INVALID: {errors}"
        print(f"{msg['kind']:14} {status}")
