# PURPOSE: Send task packets to Claude sub-agents via Anthropic SDK; collect return packages
# INPUTS:  task packet string, Anthropic API key (env), governor mode, fallback timeout
# OUTPUTS: DispatchResult (raw_response, validated return package, timing metadata)
# DEPS:    anthropic>=0.25.0, sdk/return_validator, stdlib (os, time, threading, datetime)
# SEE:     protocols/governor-dispatch.md, protocols/governor-failure-handling.md,
#          design/governor-v2.md §6, sdk/task_packet.py, sdk/return_validator.py

"""
Sub-agent dispatch module.

Sends a task packet as the first message to a Claude sub-agent instance via the
Anthropic Python SDK. Collects the response (expected to be a return package) and
validates it. Supports mock mode (no API key) and manual mode (prints packet only).

Token tracking:
    DispatchResult.tok_in / tok_out are populated as follows:
    - SDK mode:   real values from response.usage.input_tokens / output_tokens
    - Mock mode:  realistic placeholders (tok_in=100, tok_out=500)
    - Manual mode: both remain 0 (no dispatch occurred)

Retry / resilience (SDK mode only):
    _sdk_dispatch() retries up to DEFAULT_MAX_RETRIES times on any exception, using
    exponential backoff (2^attempt seconds between attempts). This covers transient
    API errors, network timeouts, and rate-limit bursts without manual intervention.
    The number of attempts used is reported in DispatchResult.metadata["attempts"]
    and logged to governance/dispatch-log.md for benchmark tracking.

Usage (module):
    from sdk.dispatch import dispatch_block, DispatchResult, MockAnthropicClient
    result = dispatch_block(task_packet_str, mode="mock")

Usage (CLI test):
    python sdk/dispatch.py --test
    python sdk/dispatch.py --packet-file manifests/block-033-dispatch-module.md --mode manual
"""

import datetime
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Ensure sdk/ siblings are importable
_SDK_DIR = Path(__file__).resolve().parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from return_validator import validate_package, ValidationResult  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL          = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS     = 4096
DEFAULT_TIMEOUT_SEC    = 300     # 5 minutes per block (fallback timer)
DEFAULT_MAX_RETRIES    = 2       # retries on transient SDK errors (2 = up to 3 total attempts)
ANTHROPIC_API_KEY_ENV  = "ANTHROPIC_API_KEY"

# System prompt Governor sends alongside the task packet
_SYSTEM_PROMPT = """\
You are a sub-agent in the cognitive-arch Governor v2 system.
You will receive a task packet (compressed _syntax.md header + convention snippet + manifest).
Follow the sub-agent contract (protocols/sub-agent-contract.md):
  1. Parse the task packet header.
  2. Read every file listed in fread:.
  3. Execute the block work per the manifest.
  4. Run all declared gates.
  5. Write the block retrospective.
  6. Emit exactly ONE return package as your final message (templates/sub-agent-return.md format).
Do NOT emit STATE.md, NEXT.md, board.md, or BLOCK_LOG.md changes. Governor handles all state.
"""

# Lock for thread-safe appends to governance/dispatch-log.md
_dispatch_log_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class DispatchResult:
    block_id: str
    mode: str                        # sdk | mock | manual
    success: bool
    raw_response: str = ""
    validation: Optional[ValidationResult] = None
    error: Optional[str] = None
    elapsed_sec: float = 0.0
    tok_in: int = 0
    tok_out: int = 0
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Dispatch log (SDK mode instrumentation)
# ---------------------------------------------------------------------------

def _append_dispatch_log(
    block_id: str,
    mode: str,
    attempts: int,
    success: bool,
    error_type: str,
    elapsed_sec: float,
) -> None:
    """Append a structured entry to governance/dispatch-log.md (best-effort, fails silently)."""
    arch_root = _SDK_DIR.parent
    log_path = arch_root / "governance" / "dispatch-log.md"
    if not log_path.parent.exists():
        return
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    row = f"| {ts} | {block_id} | {mode} | {attempts} | {success} | {error_type or '-'} | {elapsed_sec:.2f}s |\n"
    with _dispatch_log_lock:
        try:
            if not log_path.exists():
                header = (
                    "# dispatch-log — SDK dispatch instrumentation\n\n"
                    "| ts | block_id | mode | attempts | success | error_type | elapsed_sec |\n"
                    "|---|---|---|---|---|---|---|\n"
                )
                log_path.write_text(header + row, encoding="utf-8")
            else:
                with log_path.open("a", encoding="utf-8") as f:
                    f.write(row)
        except OSError:
            pass  # log failure must never surface to caller


# ---------------------------------------------------------------------------
# Mock client (no API key required — for testing and dry-run)
# ---------------------------------------------------------------------------

class MockAnthropicClient:
    """Simulates the Anthropic client. Returns a pre-built valid return package."""

    def __init__(self, block_id: str = "???"):
        self._block_id = block_id

    def dispatch(self, task_packet: str) -> str:
        """Return a mock return package for the given task packet."""
        # Extract block ID from packet if possible
        for line in task_packet.splitlines():
            for token in line.split():
                if token.startswith("b:"):
                    self._block_id = token[2:]
                    break

        return (
            f"b:{self._block_id} sid:s-mock01 status:done ts:2026-05-22T12:00Z\n"
            f"gates:mock-gate:pass\n"
            f"fmod:- fread:-\n"
            f"scope_exp:- issues:-\n"
            f"retro:yes retro_path:blocks/block-{self._block_id}-mock.md\n"
            f"tok_in:~500 tok_out:~200 tok_src:estimated\n"
        )


# ---------------------------------------------------------------------------
# SDK client wrapper
# ---------------------------------------------------------------------------

def _sdk_dispatch(
    task_packet: str,
    api_key: str,
    model: str,
    max_tokens: int,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> tuple[str, int, int, int]:
    """
    Send task packet to Claude via Anthropic SDK with automatic retry on transient errors.

    Retries up to max_retries times using exponential backoff (2^attempt seconds between
    retries). Covers transient API errors, network blips, and rate-limit bursts.

    Returns:
        (response_text, input_tokens, output_tokens, attempts_used)
        attempts_used = 1 on first-try success; up to max_retries + 1 on retried success.

    Raises:
        ImportError if anthropic package is not installed.
        Exception (last attempt's exception) after all retries exhausted.
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package not installed. Run: pip install -r sdk/requirements.txt"
        )

    client = anthropic.Anthropic(api_key=api_key, timeout=timeout_sec)
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": task_packet}],
            )
            response_text = message.content[0].text
            tok_in  = message.usage.input_tokens
            tok_out = message.usage.output_tokens
            return response_text, tok_in, tok_out, attempt + 1
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                time.sleep(2 ** attempt)
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def dispatch_block(
    task_packet: str,
    mode: str = "sdk",
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> DispatchResult:
    """
    Dispatch a single block to a sub-agent and collect the return package.

    Args:
        task_packet:  Full task packet string (header + snippet + manifest).
        mode:         "sdk" (real API), "mock" (no API key), "manual" (print only).
        api_key:      Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
        model:        Claude model name.
        max_tokens:   Max tokens for sub-agent response.
        timeout_sec:  Per-block timeout in seconds (SDK mode).
        max_retries:  Max retry attempts on transient SDK errors (SDK mode only).

    Returns:
        DispatchResult with success flag, raw response, validation, and metadata.
        metadata["attempts"] = number of SDK calls made (SDK mode only).
    """
    # Extract block ID for logging
    block_id = "???"
    for line in task_packet.splitlines():
        for token in line.split():
            if token.startswith("b:"):
                block_id = token[2:]
                break

    start = time.monotonic()

    # --- Manual mode: print packet, no dispatch ---
    if mode == "manual":
        print("=== TASK PACKET (manual mode — copy to sub-agent session) ===")
        print(task_packet)
        print("=== END TASK PACKET ===")
        return DispatchResult(
            block_id=block_id,
            mode="manual",
            success=True,
            raw_response="",
            error=None,
            elapsed_sec=time.monotonic() - start,
        )

    # --- Mock mode ---
    if mode == "mock":
        mock = MockAnthropicClient(block_id=block_id)
        raw = mock.dispatch(task_packet)
        validation = validate_package(raw)
        elapsed = time.monotonic() - start
        return DispatchResult(
            block_id=block_id,
            mode="mock",
            success=validation.valid,
            raw_response=raw,
            validation=validation,
            error=None if validation.valid else "; ".join(validation.errors),
            elapsed_sec=elapsed,
            tok_in=100,
            tok_out=500,
        )

    # --- SDK mode ---
    resolved_key = api_key or os.environ.get(ANTHROPIC_API_KEY_ENV, "")
    if not resolved_key:
        return DispatchResult(
            block_id=block_id,
            mode="sdk",
            success=False,
            error=f"No API key. Set {ANTHROPIC_API_KEY_ENV} env var or pass api_key=.",
            elapsed_sec=time.monotonic() - start,
        )

    # Pessimistic default: assume all retries exhausted; overwritten on success
    attempts = max_retries + 1
    try:
        raw, tok_in, tok_out, attempts = _sdk_dispatch(
            task_packet, resolved_key, model, max_tokens, timeout_sec, max_retries
        )
    except Exception as exc:
        elapsed = time.monotonic() - start
        _append_dispatch_log(block_id, "sdk", attempts, False, type(exc).__name__, elapsed)
        return DispatchResult(
            block_id=block_id,
            mode="sdk",
            success=False,
            error=str(exc),
            elapsed_sec=elapsed,
            metadata={"attempts": attempts},
        )

    validation = validate_package(raw)
    elapsed = time.monotonic() - start
    _append_dispatch_log(block_id, "sdk", attempts, validation.valid, "", elapsed)
    return DispatchResult(
        block_id=block_id,
        mode="sdk",
        success=validation.valid,
        raw_response=raw,
        validation=validation,
        error=None if validation.valid else "; ".join(validation.errors),
        elapsed_sec=elapsed,
        tok_in=tok_in,
        tok_out=tok_out,
        metadata={"attempts": attempts},
    )


# ---------------------------------------------------------------------------
# Batch dispatch (parallel via ThreadPoolExecutor)
# ---------------------------------------------------------------------------

def dispatch_batch(
    task_packets: list[str],
    mode: str = "sdk",
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    max_workers: int = 4,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> list[DispatchResult]:
    """
    Dispatch multiple task packets concurrently using ThreadPoolExecutor.

    Integration (state file updates via integrate_group) must be called
    sequentially AFTER this function returns — it is not thread-safe.

    Timeout model:
        timeout_sec     = per-worker timeout (passed to each dispatch_block call).
        timeout_sec * 1.5 = outer wall-clock cap for as_completed(). Workers run in
        parallel, so the wall-clock max is ~timeout_sec, not timeout_sec * n_workers.
        The 1.5× buffer accommodates API slowness without the multi-minute waits that
        timeout_sec × n_workers produced when the API was degraded.

    Args:
        task_packets: List of task packet strings to dispatch.
        mode:         "sdk" | "mock" | "manual" (applied to all packets).
        api_key:      Anthropic API key (SDK mode only).
        model:        Claude model name.
        max_tokens:   Max tokens per sub-agent response.
        timeout_sec:  Per-block timeout (also sets outer cap via × 1.5).
        max_workers:  Thread pool size (capped at len(task_packets)).
        max_retries:  Max retry attempts per worker on transient SDK errors.

    Returns:
        List of DispatchResult objects in the same order as task_packets.
    """
    if not task_packets:
        return []

    n_workers = min(max_workers, len(task_packets))
    results: list[Optional[DispatchResult]] = [None] * len(task_packets)

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = {
            executor.submit(
                dispatch_block,
                packet,
                mode=mode,
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
                timeout_sec=timeout_sec,
                max_retries=max_retries,
            ): idx
            for idx, packet in enumerate(task_packets)
        }
        # Outer cap = 1.5× per-worker timeout (workers run in parallel, not series)
        for future in as_completed(futures, timeout=timeout_sec * 1.5):
            idx = futures[future]
            try:
                results[idx] = future.result(timeout=timeout_sec)
            except Exception as exc:
                results[idx] = DispatchResult(
                    block_id="???",
                    mode=mode,
                    success=False,
                    error=f"thread exception: {exc}",
                )

    return [r for r in results if r is not None]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli_test() -> int:
    """Self-test: mock dispatch for a sample task packet."""
    sample_packet = (
        "b:033 kind:feature phase:phase-5 gov:g-test ts:2026-05-22T12:00Z\n"
        "axioms:Q1,Q2,Q3,Q5,Q6,C2,C4,C6 scope:open retro_req:yes tok_track:yes\n"
        "fread:protocols/governor-dispatch.md fmod:sdk/dispatch.py\n"
        "\n"
        "--- convention snippet ---\n"
        "Q3: Manifests precede work artifacts.\n"
        "\n"
        "--- manifest ---\n"
        "[test manifest content]\n"
    )

    result = dispatch_block(sample_packet, mode="mock")

    errors: list[str] = []
    if not result.success:
        errors.append(f"dispatch returned success=False: {result.error}")
    if result.validation and not result.validation.valid:
        errors.append(f"return package validation failed: {result.validation.errors}")
    if result.mode != "mock":
        errors.append(f"expected mode=mock, got {result.mode}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print("dispatch --test: PASS")
    print(f"  mode    : {result.mode}")
    print(f"  block   : {result.block_id}")
    print(f"  success : {result.success}")
    print(f"  elapsed : {result.elapsed_sec:.3f}s")
    print(f"  status  : {result.validation.parsed.get('status') if result.validation else 'n/a'}")
    return 0


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="dispatch",
        description="Governor v2 sub-agent dispatch module.",
    )
    parser.add_argument("--test", action="store_true", help="Run self-test with mock dispatch.")
    parser.add_argument(
        "--mode",
        choices=["sdk", "mock", "manual"],
        default="mock",
        help="Dispatch mode (default: mock).",
    )
    parser.add_argument(
        "--packet-file",
        metavar="PATH",
        help="Path to a file to use as task packet content (manual mode demo).",
    )

    args = parser.parse_args()

    if args.test:
        sys.exit(_cli_test())
    elif args.packet_file:
        pf = Path(args.packet_file)
        if not pf.exists():
            print(f"ERROR: file not found: {pf}", file=sys.stderr)
            sys.exit(1)
        packet = pf.read_text(encoding="utf-8")
        result = dispatch_block(packet, mode=args.mode)
        print(f"success={result.success} elapsed={result.elapsed_sec:.2f}s")
        if result.error:
            print(f"error: {result.error}", file=sys.stderr)
        sys.exit(0 if result.success else 1)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
