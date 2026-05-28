#!/usr/bin/env bash
# audit.sh — lightweight validation for cognitive architecture
# Implements all 8 checks declared in commands/audit.md (script-executable).
# Checks 7+8 delegate to sdk/audit_helpers.py (Python; stdlib only).
# Usage: ./audit.sh
# Exit: 0 if clean, 1 if errors found

set -e
cd "$(dirname "$0")"

errors=0
warnings=0

err()  { echo "ERROR: $1"; errors=$((errors+1)); }
warn() { echo "WARN:  $1"; warnings=$((warnings+1)); }
ok()   { echo "OK:    $1"; }

echo "=== Cognitive Architecture Audit (all 8 checks) ==="
echo ""

# --- Check 1/8: required HOT files exist ---
echo "[1/8] Checking HOT files exist..."
for f in CLAUDE.md PROTOCOLS.md STATE.md NEXT.md INDEX.md board.md _syntax.md PROJECT.md; do
  if [ ! -f "$f" ]; then
    err "missing required HOT file: $f"
  fi
done

# --- Check 2/8: file size budgets ---
echo "[2/8] Checking file size budgets..."
check_size() {
  if [ -f "$1" ]; then
    local n
    n=$(wc -l < "$1" | tr -d ' ')
    if [ "$n" -gt "$2" ]; then
      warn "$1 exceeds budget ($n > $2 lines)"
    fi
  fi
}
check_size CLAUDE.md 60
check_size STATE.md 60
check_size NEXT.md 30
check_size INDEX.md 250
check_size board.md 150
check_size _syntax.md 100

# --- Check 3/8: pointer integrity (markdown links) ---
echo "[3/8] Checking pointer integrity..."
broken_count=0
while IFS= read -r line; do
  # Extract file path and link target from grep output
  file=$(echo "$line" | cut -d: -f1)
  # Extract path from markdown link [text](path)
  while IFS= read -r path; do
    # Skip URLs and anchors
    case "$path" in
      http*|https*|"#"*) continue ;;
    esac
    # Strip query/anchor
    path="${path%%#*}"
    path="${path%%\?*}"
    # Skip empty
    [ -z "$path" ] && continue
    # Resolve relative to file's directory
    dir=$(dirname "$file")
    resolved="$dir/$path"
    if [ ! -e "$resolved" ]; then
      warn "broken pointer in $file: $path"
      broken_count=$((broken_count+1))
    fi
  done < <(echo "$line" | grep -oE '\]\([^)]+\)' | sed -E 's/^\]\(//' | sed -E 's/\)$//')
done < <(grep -rEn '\]\([^)]+\.md[^)]*\)' --include='*.md' . 2>/dev/null || true)

# --- Check 3b/8: pointer integrity — YAML files.modify paths exist ---
# For each manifest, extract paths under files.modify and verify they exist on disk.
# files.create paths are NOT checked (they don't exist yet by design).
# Severity: WARN (schemas in stabilization — not a hard ERROR yet).
if ls manifests/block-*.md > /dev/null 2>&1; then
  for manifest in manifests/block-*.md; do
    [ -f "$manifest" ] || continue
    # Use awk: enter modify section, collect "  - path" lines, exit on next key
    while IFS= read -r fpath; do
      [ -z "$fpath" ] && continue
      if [ ! -f "$fpath" ] && [ ! -d "$fpath" ]; then
        warn "pointer-integrity [3b]: $(basename "$manifest"): files.modify not found: $fpath"
      fi
    done < <(awk '
      /^[[:space:]]+modify:/ { in_mod=1; next }
      in_mod && /^[[:space:]]+[a-z_]+:/ { in_mod=0 }
      in_mod && /^[[:space:]]+-[[:space:]]/ {
        sub(/^[[:space:]]+-[[:space:]]+/, "")
        if ($0 != "" && $0 != "[]") print
      }
    ' "$manifest")
  done
fi

# --- Check 4/8: AI-only file format + bootstrap consistency ---
echo "[4/8] Checking AI-only file format..."
for ai_file in STATE.md NEXT.md board.md; do
  if [ -f "$ai_file" ]; then
    # AI-only files should have only comment lines, blank lines, or key:value lines
    bad_lines=$(grep -vE '^[[:space:]]*(#|$|.*:)' "$ai_file" | wc -l | tr -d ' ')
    if [ "$bad_lines" -gt 0 ]; then
      warn "$ai_file has $bad_lines non-conforming lines (expected: comments or key:value only)"
    fi
  fi
done
# Sub-check 4b: bootstrap consistency
if [ -f "STATE.md" ] && grep -q "status:bootstrap" STATE.md; then
  if [ -f "PROJECT.md" ] && grep -q "\[PROJECT NAME" PROJECT.md; then
    ok "bootstrap state consistent (PROJECT.md placeholders + STATE.md bootstrap)"
  else
    warn "STATE.md says bootstrap but PROJECT.md has been edited — update STATE.md status"
  fi
fi

# --- Check 5/8: Manifest schema validation ---
echo "[5/8] Checking manifest schema..."
check5_errors=0
if ls manifests/block-*.md > /dev/null 2>&1; then
  for manifest in manifests/block-*.md; do
    [ -f "$manifest" ] || continue
    # Extract frontmatter (lines between first and second ---)
    fm=$(awk 'BEGIN{c=0} /^---/{c++; if(c==2) exit} c==1{print}' "$manifest")
    for key in id tier kind status files; do
      if ! echo "$fm" | grep -qE "^${key}:"; then
        warn "manifest-schema [5]: $(basename "$manifest"): missing '${key}:'"
        check5_errors=$((check5_errors+1))
      fi
    done
  done
  if [ "$check5_errors" -eq 0 ]; then
    ok "manifest schema: all manifests have required keys (id/tier/kind/status/files)"
  fi
else
  ok "manifest schema: no block manifests found (skipped)"
fi

# --- Check 6/8: Dependency validation ---
echo "[6/8] Checking dependency validation..."
check6_errors=0
_log_file="blocks/BLOCK_LOG.md"
if [ ! -f "$_log_file" ]; then
  warn "dep-validation [6]: blocks/BLOCK_LOG.md not found — skipping"
elif ls manifests/block-*.md > /dev/null 2>&1; then
  for manifest in manifests/block-*.md; do
    [ -f "$manifest" ] || continue
    # Only validate deps for completed (done) blocks
    block_id=$(awk '/^id:/{print $2; exit}' "$manifest")
    [ -z "$block_id" ] && continue
    grep -q "^${block_id} done" "$_log_file" 2>/dev/null || continue
    # Extract listed dependency block IDs (format: "  - block-XXX")
    while IFS= read -r dep; do
      [ -z "$dep" ] && continue
      if ! grep -q "^${dep} done" "$_log_file"; then
        warn "dep-validation [6]: $(basename "$manifest"): dep '${dep}' not in BLOCK_LOG"
        check6_errors=$((check6_errors+1))
      fi
    done < <(awk '
      /^dependencies:/ { in_deps=1; next }
      in_deps && /^[a-z_-]+:/ { in_deps=0 }
      in_deps && /^  - / {
        sub(/^  - /, "")
        if ($0 != "[]" && $0 != "") print
      }
    ' "$manifest")
  done
  if [ "$check6_errors" -eq 0 ]; then
    ok "dep-validation: all done-block dependencies confirmed in BLOCK_LOG"
  fi
else
  ok "dep-validation: no block manifests found (skipped)"
fi

# --- Checks 7+8: Python helpers (sdk/audit_helpers.py) ---
_py=""
command -v python3 > /dev/null 2>&1 && _py="python3"
[ -z "$_py" ] && command -v python > /dev/null 2>&1 && _py="python"

# Check 7: fmod conflict detection
echo "[7/8] Checking file conflicts..."
if [ -n "$_py" ] && [ -f "sdk/audit_helpers.py" ]; then
  while IFS= read -r line; do
    case "$line" in
      "OK:"*) ok "${line#OK: }" ;;
      "WARN:"*) warn "${line#WARN: }" ;;
      "ERROR:"*) err "${line#ERROR: }" ;;
    esac
  done < <("$_py" sdk/audit_helpers.py --check conflicts --arch-root . 2>&1)
else
  warn "file-conflict [7]: Python or sdk/audit_helpers.py unavailable — skipping"
fi

# Check 8: Drift detection
echo "[8/8] Checking drift..."
if [ -n "$_py" ] && [ -f "sdk/audit_helpers.py" ]; then
  while IFS= read -r line; do
    case "$line" in
      "OK:"*) ok "${line#OK: }" ;;
      "WARN:"*) warn "${line#WARN: }" ;;
      "ERROR:"*) err "${line#ERROR: }" ;;
    esac
  done < <("$_py" sdk/audit_helpers.py --check drift --arch-root . 2>&1)
else
  warn "drift [8]: Python or sdk/audit_helpers.py unavailable — skipping"
fi
echo ""

# --- [INFO] Token estimates (chars÷4 proxy — informational only, no exit code impact) ---
echo "[INFO] HOT file token estimates (chars÷4):"
hot_total_chars=0
for f in CLAUDE.md PROTOCOLS.md STATE.md NEXT.md INDEX.md _syntax.md board.md; do
  if [ -f "$f" ]; then
    chars=$(wc -c < "$f" | tr -d ' ')
    tokens=$(( chars / 4 ))
    hot_total_chars=$(( hot_total_chars + chars ))
    if [ "$tokens" -gt 1000 ]; then
      echo "  ⚠  $f: ~${tokens} tok  (exceeds 1,000 tok soft cap)"
    else
      echo "     $f: ~${tokens} tok"
    fi
  fi
done
hot_total_tok=$(( hot_total_chars / 4 ))
echo ""
if [ "$hot_total_tok" -gt 4000 ]; then
  echo "[INFO] HOT boot total: ~${hot_total_tok} tok  ⚠ OVER BUDGET (target: <4,000 tok)"
  echo "[INFO] Run: /token-audit  for per-file breakdown and migration candidates"
else
  echo "[INFO] HOT boot total: ~${hot_total_tok} tok  ✓ within budget (target: <4,000 tok)"
fi
echo ""

# --- Check 9/9: Velocity — warn if recent closed blocks missing actual_duration_hours ---
echo "[9/9] Checking velocity fields..."
check9_missing=0
if [ -f "blocks/BLOCK_LOG.md" ]; then
  # Get last 30 done block IDs
  while IFS= read -r block_id; do
    [ -z "$block_id" ] && continue
    # Find retro file
    retro_file="blocks/${block_id}-"*".md"
    # shellcheck disable=SC2086
    retro=$(ls $retro_file 2>/dev/null | head -1)
    if [ -z "$retro" ]; then continue; fi
    # Check for actual_duration_hours with a real value (not empty, not placeholder)
    if ! grep -qE '^actual_duration_hours:[[:space:]]+[0-9]' "$retro" 2>/dev/null; then
      warn "velocity [9]: $block_id missing actual_duration_hours in $retro"
      check9_missing=$((check9_missing+1))
    fi
  done < <(grep '^block-' "blocks/BLOCK_LOG.md" | awk '{print $1}' | tail -30)
  if [ "$check9_missing" -eq 0 ]; then
    ok "velocity: all recent closed blocks have actual_duration_hours filled"
  fi
else
  warn "velocity [9]: blocks/BLOCK_LOG.md not found — skipping"
fi
echo ""

# --- Check 10/10: Integrity lock — warn if immutable files have drifted ---
echo "[10/10] Checking integrity lock..."
if [ -f ".integrity.lock" ]; then
  if [ -n "$_py" ] && [ -f "sdk/integrity_check.py" ]; then
    _strict_flag=""
    for arg in "$@"; do
      [ "$arg" = "--strict" ] && _strict_flag="--strict"
    done
    while IFS= read -r line; do
      case "$line" in
        "OK:"*) ok "${line#OK:   }" ;;
        "WARN:"*) warn "${line#WARN: }" ;;
        "ERROR:"*) err "${line#ERROR:}" ;;
        "All "*) ok "$line" ;;
      esac
    done < <("$_py" sdk/integrity_check.py --verify --arch-root . $_strict_flag 2>&1 | grep -v "^$" | grep -v "^Run" | grep -v "^See:" || true)
  else
    warn "integrity-lock [10]: Python or sdk/integrity_check.py unavailable — skipping"
  fi
else
  warn "integrity-lock [10]: .integrity.lock not found — run: python sdk/integrity_check.py --regenerate"
fi
echo ""

# --- Summary ---
echo "=== AUDIT SUMMARY (all 10 checks) ==="
echo "Errors:   $errors"
echo "Warnings: $warnings"
echo ""

if [ "$errors" -gt 0 ]; then
  echo "FAIL — fix errors above before proceeding."
  exit 1
else
  if [ "$warnings" -gt 0 ]; then
    echo "PASS WITH WARNINGS — review warnings above."
  else
    echo "PASS — cognitive architecture healthy (all 8 checks)."
  fi
  exit 0
fi
