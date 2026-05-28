# PURPOSE: Parse and validate sub-agent return packages (compressed _syntax.md format)
# INPUTS:  return package string emitted by sub-agent as final message
# OUTPUTS: ValidationResult (valid, errors, parsed fields dict)
# DEPS:    stdlib only (re)
# SEE:     templates/sub-agent-return.md, protocols/sub-agent-contract.md,
#          _syntax.md, design/governor-v2.md §5, sdk/dispatch.py

"""
Return package validator.

Parses the compressed key:value return package from a sub-agent and validates
all required fields. Governor uses the result to decide next action.

Usage (module):
    from sdk.return_validator import validate_package, ValidationResult
    result = validate_package(raw_text)
    if result.valid:
        print(result.parsed["status"])
    else:
        print(result.errors)

Usage (CLI test):
    python sdk/return_validator.py --test
"""

import re
import sys
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "b", "sid", "status", "ts", "gates", "fmod", "fread",
    "scope_exp", "issues", "retro", "tok_in", "tok_out", "tok_src",
]

VALID_STATUSES = {"done", "partial", "blocked", "scope-exceeded", "needs-decision"}
VALID_RETRO    = {"yes", "no"}
VALID_TOK_SRC  = {"actual", "estimated"}
VALID_GATE_VAL = {"pass", "fail"}

# Pattern for a single gate entry: "gate-name:pass" or "gate-name:fail"
_GATE_ENTRY_RE = re.compile(r"^[\w\-]+:(pass|fail)$")

# tok_in / tok_out: numeric or ~numeric (estimate prefix)
_TOKEN_RE = re.compile(r"^~?\d+$")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _parse_kv(text: str) -> dict[str, str]:
    """
    Parse a compressed _syntax.md key:value block.

    Handles:
    - Multiple key:value pairs on one line (space-separated)
    - Multiple lines
    - Optional evidence: line (free-text after main block)

    Returns a flat dict of {key: value}. Duplicate keys: last value wins.
    """
    result: dict[str, str] = {}
    # Split into whitespace-delimited tokens; each should match key:value
    # We scan line by line because some values (retro_path) use colons in paths
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("evidence:"):
            # evidence: is free text; store whole line under "evidence" key
            if line.startswith("evidence:"):
                result["evidence"] = line[len("evidence:"):].strip()
            continue
        # Split on spaces; each token should be key:value
        tokens = line.split()
        for token in tokens:
            if ":" not in token:
                continue
            key, _, val = token.partition(":")
            key = key.strip()
            val = val.strip()
            if key and val:
                result[key] = val
    return result


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    parsed: dict[str, str] = field(default_factory=dict)
    evidence: Optional[str] = None


def validate_package(raw_text: str) -> ValidationResult:
    """
    Validate a sub-agent return package.

    Args:
        raw_text: The full return package string.

    Returns:
        ValidationResult with valid=True and parsed fields, or valid=False and errors.
    """
    parsed = _parse_kv(raw_text)
    errors: list[str] = []

    # 1. Required fields present
    for f in REQUIRED_FIELDS:
        if f not in parsed:
            errors.append(f"missing required field: '{f}:'")

    if errors:
        return ValidationResult(valid=False, errors=errors, parsed=parsed)

    # 2. status value
    if parsed["status"] not in VALID_STATUSES:
        errors.append(
            f"invalid status '{parsed['status']}'; expected one of {sorted(VALID_STATUSES)}"
        )

    # 3. gates format: "gate-name:pass|fail,gate-name2:pass|fail"
    gates_raw = parsed.get("gates", "-")
    if gates_raw != "-":
        for entry in gates_raw.split(","):
            if not _GATE_ENTRY_RE.match(entry.strip()):
                errors.append(
                    f"invalid gate entry '{entry}'; expected 'gate-name:pass' or 'gate-name:fail'"
                )

    # 4. retro value
    if parsed.get("retro") not in VALID_RETRO:
        errors.append(f"invalid retro '{parsed.get('retro')}'; expected 'yes' or 'no'")

    # 5. tok_src value
    if parsed.get("tok_src") not in VALID_TOK_SRC:
        errors.append(
            f"invalid tok_src '{parsed.get('tok_src')}'; expected 'actual' or 'estimated'"
        )

    # 6. tok_in / tok_out are numeric (possibly prefixed with ~)
    for tok_field in ("tok_in", "tok_out"):
        val = parsed.get(tok_field, "")
        if not _TOKEN_RE.match(val):
            errors.append(f"invalid {tok_field} '{val}'; expected integer or ~integer")

    # 7. If retro:yes, retro_path must be present and not "-"
    if parsed.get("retro") == "yes":
        rp = parsed.get("retro_path", "-")
        if rp == "-" or not rp:
            errors.append("retro:yes but retro_path is missing or '-'")

    evidence = parsed.pop("evidence", None)
    valid = len(errors) == 0
    return ValidationResult(valid=valid, errors=errors, parsed=parsed, evidence=evidence)


# ---------------------------------------------------------------------------
# Retrospective Rubric (semantic quality check)
# ---------------------------------------------------------------------------

# Keyword sets for each rubric criterion
_RUBRIC_C1_WORDS = {"actually", "instead", "unexpected", "turned out", "different from",
                    "not as expected", "changed", "had to"}
_RUBRIC_C2_WORDS = {"gate", "passed", "failed", "exit 0", "pytest", "test"}
_RUBRIC_C3_TRIGGER = {"fail", "fix", "error", "bug"}
_RUBRIC_C3_EXPLAIN = {"because", "changed", "replaced", "added", "removed",
                      "switched", "updated", "renamed"}
_RUBRIC_C4_WORDS   = {"next time", "next block", "future", "lesson", "learned",
                      "will ", "should", "recommend", "avoid", "repeat"}


def validate_rubric(retro_text: str, tok_in: int = 0, tok_out: int = 0) -> list[str]:
    """
    Semantic quality check for block retrospectives.

    Evaluates the retrospective text against 5 criteria from
    protocols/retrospective-rubric.md. Returns a list of
    '[RUBRIC WARNING] criterion-N: ...' strings for each failed criterion.

    Warnings are advisory — they do not block block-close but indicate
    a shallow retrospective that may not capture useful learning.

    Args:
        retro_text: Full text of the retrospective file.
        tok_in:     Actual tok_in value (0 if not tracked).
        tok_out:    Actual tok_out value (0 if not tracked).

    Returns:
        List of warning strings (empty list = all criteria passed).
    """
    warnings: list[str] = []
    lower = retro_text.lower()

    # Criterion 1: mention of deviation from plan
    if not any(w in lower for w in _RUBRIC_C1_WORDS):
        warnings.append(
            "[RUBRIC WARNING] criterion-1: no deviation from plan mentioned"
            " — retro may be too generic"
        )

    # Criterion 2: gate result reference
    if not any(w in lower for w in _RUBRIC_C2_WORDS):
        warnings.append(
            "[RUBRIC WARNING] criterion-2: no gate result referenced"
            " — confirm gates actually ran"
        )

    # Criterion 3: if failure/fix mentioned, must also explain what changed
    has_failure = any(w in lower for w in _RUBRIC_C3_TRIGGER)
    has_explain = any(w in lower for w in _RUBRIC_C3_EXPLAIN)
    if has_failure and not has_explain:
        warnings.append(
            "[RUBRIC WARNING] criterion-3: failure/fix mentioned but no explanation"
            " of what changed"
        )

    # Criterion 4: forward-looking lesson
    if not any(w in lower for w in _RUBRIC_C4_WORDS):
        warnings.append(
            "[RUBRIC WARNING] criterion-4: no forward-looking lesson captured"
        )

    # Criterion 5: non-zero token counts
    if tok_in == 0 or tok_out == 0:
        warnings.append(
            "[RUBRIC WARNING] criterion-5: tok_in or tok_out is 0"
            " — token tracking not recorded"
        )

    return warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_VALID_SAMPLE = """\
b:018 sid:s-abc123 status:done ts:2026-05-22T12:00Z
gates:files-created:pass,validator-test:pass
fmod:sdk/return_validator.py:140
fread:templates/sub-agent-return.md,protocols/sub-agent-contract.md,_syntax.md
scope_exp:- issues:-
retro:yes retro_path:blocks/block-032-return-validator-module.md
tok_in:~2000 tok_out:~800 tok_src:estimated
"""

_MALFORMED_MISSING_FIELD = """\
sid:s-abc123 status:done ts:2026-05-22T12:00Z
gates:files-created:pass
fmod:- fread:-
scope_exp:- issues:-
retro:yes retro_path:blocks/block-032-return-validator-module.md
tok_in:~100 tok_out:~50 tok_src:estimated
"""
# Missing: b:

_MALFORMED_BAD_STATUS = """\
b:032 sid:s-abc123 status:running ts:2026-05-22T12:00Z
gates:files-created:pass
fmod:- fread:-
scope_exp:- issues:-
retro:yes retro_path:blocks/block-032-return-validator-module.md
tok_in:~100 tok_out:~50 tok_src:estimated
"""
# Invalid status: "running"

_MALFORMED_BAD_GATE = """\
b:032 sid:s-abc123 status:done ts:2026-05-22T12:00Z
gates:files-created:maybe,other-gate:ok
fmod:- fread:-
scope_exp:- issues:-
retro:yes retro_path:blocks/block-032-return-validator-module.md
tok_in:~100 tok_out:~50 tok_src:estimated
"""
# Invalid gate values: "maybe" and "ok" (not pass|fail)


def _cli_test() -> int:
    cases = [
        ("valid sample",          _VALID_SAMPLE,              True),
        ("missing b: field",      _MALFORMED_MISSING_FIELD,   False),
        ("bad status value",      _MALFORMED_BAD_STATUS,      False),
        ("bad gate format",       _MALFORMED_BAD_GATE,        False),
    ]

    errors_overall: list[str] = []
    for name, text, expect_valid in cases:
        result = validate_package(text)
        ok = result.valid == expect_valid
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}: valid={result.valid}  errors={result.errors or '-'}")
        if not ok:
            errors_overall.append(f"case '{name}': expected valid={expect_valid}, got {result.valid}")

    if errors_overall:
        print(f"\nreturn_validator --test: FAIL ({len(errors_overall)} case(s) wrong)", file=sys.stderr)
        return 1

    print(f"\nreturn_validator --test: PASS")
    print(f"  Cases: {len(cases)} (1 valid accepted, 3 malformed rejected)")
    return 0


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="return_validator",
        description="Validate sub-agent return packages (Governor v2).",
    )
    parser.add_argument("--test", action="store_true", help="Run self-test with sample packages.")
    parser.add_argument("--stdin", action="store_true", help="Read return package from stdin and validate.")

    args = parser.parse_args()

    if args.test:
        sys.exit(_cli_test())
    elif args.stdin:
        raw = sys.stdin.read()
        result = validate_package(raw)
        if result.valid:
            print(f"VALID  status={result.parsed.get('status')} b={result.parsed.get('b')}")
        else:
            print(f"INVALID ({len(result.errors)} error(s)):")
            for e in result.errors:
                print(f"  - {e}")
        sys.exit(0 if result.valid else 1)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
