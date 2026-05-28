---
id: block-033
phase: phase-5
status: done
gates_passed: 2
gates_total: 2
created_at: 2026-05-22
---

# Block 033 Retrospective — Module: sub-agent dispatch (Anthropic SDK)

## §1 What was built

- `sdk/dispatch.py` — full module with:
  - `DispatchResult` dataclass (block_id, mode, success, raw_response, validation, error, elapsed, tok_in, tok_out)
  - `MockAnthropicClient` — returns a pre-built valid return package; used in `--test` and dry-run
  - `dispatch_block(task_packet, mode, api_key, model, max_tokens, timeout_sec)` — three modes:
    - `"mock"` — no API key; MockAnthropicClient returns valid package
    - `"manual"` — prints task packet to stdout (human pastes into Claude session)
    - `"sdk"` — real Anthropic API call via `anthropic.Anthropic.messages.create()`
  - `_SYSTEM_PROMPT` — Governor system prompt injected alongside task packet
  - CLI: `--test`, `--mode`, `--packet-file`
  - Open question 1 answered: SDK passes task packet as plain text user message (not file upload); `fread:` paths are listed in packet header and sub-agent reads them itself from the filesystem

## §2 Gates

| Gate | Result | Evidence |
|------|--------|---------|
| dispatch-test | ✅ pass | Mock dispatch returns valid package, validation passes, status=done |
| files-created | ✅ pass | sdk/dispatch.py exists |

## §3 Open questions resolved

- **Open question 1 (SDK file passing):** Confirmed — Anthropic SDK passes task packet as text (user message). Sub-agents read `fread:` files directly from the filesystem. Temp-dir isolation (Decision 7) is feasible — sub-agent runs in same filesystem, conceptual separation is sufficient.
- **Open question 4 (sub-agent identity):** Implemented as ephemeral — Governor assigns `sid:s-<ID>` before dispatch; no persistent named sub-agent identity needed.

## §4 Scope

No scope expansion. Single file created per manifest.

## §5 Token estimate

tok_in:~4500 tok_out:~1800 tok_src:estimated
