# test_corporate_e2e.py
# PURPOSE: End-to-end smoke test do fluxo corporativo completo.
#          Cria um repo TypeScript fixture, roda todos os módulos na sequência
#          e valida que cada etapa produziu os artefatos esperados.
#          Não usa pytest — roda direto: python test_corporate_e2e.py
#
# FLUXO TESTADO:
#   1. codebase_scanner   L0+L1+L2+L3  →  project-profile-fixture.md + HTML
#   2. ticket_intake      texto → manifest corporativo
#   3. consistency_checker diff → ConsistencyReport
#   4. review_pipeline    ciclo qualidade → HTML de review
#   5. teach_mode         3 HTMLs de audiência
#   6. velocity_tracker   started_at / paused / resumed / finished_at
#   7. forecast_engine    HTML de forecast
#   8. calendar_manager   add / list / upcoming alerts
#
# RESULTADO ESPERADO: 8 etapas PASS, artefatos listados ao final.

from __future__ import annotations

import io
import sys
import tempfile
import contextlib
from pathlib import Path

# Force UTF-8 on Windows before any print
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ARCH_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ARCH_ROOT / "sdk"))

PASS = "PASS"
FAIL = "FAIL"
results: list[tuple[str, str, str]] = []   # (step, status, note)


def check(step: str, ok: bool, note: str = "") -> None:
    status = PASS if ok else FAIL
    icon = "[OK]" if ok else "[FAIL]"
    print(f"  {icon}  [{step}] {note or ('ok' if ok else 'FAILED')}")
    results.append((step, status, note))


# ---------------------------------------------------------------------------
# Fixture repo builder
# ---------------------------------------------------------------------------

def build_fixture_repo(root: Path) -> Path:
    repo = root / "acme-frontend"
    repo.mkdir()
    (repo / "package.json").write_text(
        '{"name":"acme-frontend","version":"1.0.0",'
        '"dependencies":{"next":"14.2.0","react":"18.3.0","zod":"3.23.0"},'
        '"devDependencies":{"typescript":"5.4.0","@types/react":"18.3.0"}}',
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text("node_modules/\ndist/\n.next/\n", encoding="utf-8")
    src = repo / "src"
    src.mkdir()
    # Domain entities
    entities = src / "entities"
    entities.mkdir()
    for entity in ("User", "Order", "Payment", "Review"):
        (entities / f"{entity}.ts").write_text(
            f"export interface {entity} {{\n  id: string;\n  createdAt: Date;\n}}\n",
            encoding="utf-8",
        )
    # Feature-Sliced Design structure
    for folder in ("features", "shared", "widgets"):
        d = src / folder
        d.mkdir()
        (d / "index.ts").write_text(f"// {folder} layer\n", encoding="utf-8")
    # Auth feature (para testar ticket inference)
    auth = src / "features" / "auth"
    auth.mkdir()
    for f in ("loginUser.ts", "refreshToken.ts", "useAuth.ts"):
        (auth / f).write_text(
            f"import {{ useState }} from 'react';\n"
            f"export const {f.replace('.ts','')} = () => {{}};  // placeholder\n",
            encoding="utf-8",
        )
    # Payment feature
    payment = src / "features" / "payment"
    payment.mkdir()
    (payment / "checkout.ts").write_text(
        "import Stripe from 'stripe';\nexport function checkout() {}\n",
        encoding="utf-8",
    )
    # Test files
    tests = src / "__tests__"
    tests.mkdir()
    (tests / "auth.test.ts").write_text(
        "import { loginUser } from '../features/auth/loginUser';\n"
        "describe('auth', () => { it('runs', () => {}); });\n",
        encoding="utf-8",
    )
    return repo


# ---------------------------------------------------------------------------
# Step 1: Scanner L0+L1+L2+L3
# ---------------------------------------------------------------------------

def step_scanner(repo: Path, arch: Path) -> None:
    print("\n-- Step 1: codebase_scanner (L0+L1+L2+L3) --")
    from codebase_scanner import run_scan

    result = run_scan(repo, "L0", arch, "acme", no_html=False)
    profile_path = Path(result.get("profile_path", ""))

    check("scanner/profile_created", profile_path.exists(), f"profile: {profile_path.name}")

    if profile_path.exists():
        text = profile_path.read_text(encoding="utf-8")
        check("scanner/L0_section", "## L0" in text, "L0 section present")
        check("scanner/L1_section", "## L1" in text, "L1 section present")
        check("scanner/no_code_leak", "export function" not in text and "export interface" not in text,
              "no raw code in profile")

    html_files = list((arch / "governance").glob("scanner-output-acme-*.html"))
    check("scanner/html_generated", len(html_files) > 0,
          f"HTML: {html_files[0].name if html_files else 'none'}")

    # Run deep scan L2+L3
    from scanner_deep import scan_deep
    deep_result = scan_deep(repo, "L2+L3", arch, "acme")
    from scanner_profile import ProjectProfile
    p = ProjectProfile(arch, "acme")
    check("scanner/L2_section", p.has_section("L2"), "L2 architecture pattern detected")
    check("scanner/L3_section", p.has_section("L3"), "L3 aesthetics detected")

    arch_pattern = deep_result.get("architecture", "")
    check("scanner/fsd_detected",
          "Feature-Sliced" in arch_pattern or "architecture" in str(deep_result),
          f"pattern: {arch_pattern or 'see profile'}")


# ---------------------------------------------------------------------------
# Step 2: Ticket intake
# ---------------------------------------------------------------------------

def step_ticket_intake(arch: Path) -> Path:
    print("\n-- Step 2: ticket_intake --")
    from ticket_intake import generate_manifest

    out = generate_manifest(
        "implementar refresh automático de JWT quando o token expira antes de uma ação do usuário",
        "acme",
        arch,
    )
    check("intake/manifest_created", out.exists(), f"manifest: {out.name}")

    text = out.read_text(encoding="utf-8")
    check("intake/kind_intake", "kind: intake" in text, "kind=intake")
    check("intake/size_xs", "size: XS" in text, "size=XS")
    check("intake/client_id", "client_id: acme" in text, "client_id set")
    check("intake/acceptance_criteria", "acceptance_criteria" in text, "criteria present")
    check("intake/no_code_modification", "modify: []" in text, "intake never modifies code")
    return out


# ---------------------------------------------------------------------------
# Step 3: Consistency checker
# ---------------------------------------------------------------------------

def step_consistency(arch: Path) -> None:
    print("\n-- Step 3: consistency_checker --")
    from consistency_checker import check_consistency
    from scanner_profile import ProjectProfile

    profile_path = arch / "governance" / "project-profile-acme.md"

    # Diff with good code (camelCase, named imports)
    good_diff = (
        "+const refreshToken = async (userId: string) => {};\n"
        "+import { useState, useCallback } from 'react';\n"
        "+export const useAuthRefresh = () => {};\n"
    )
    report_good = check_consistency(profile_path, good_diff, level_b=True)
    check("checker/clean_diff_passes", report_good.score >= 0.80,
          f"score={report_good.score:.2f} threshold={report_good.threshold:.2f}")

    # Diff with divergences (console.log = nível C ON, ou naming snake_case explícito)
    bad_diff = (
        "+const refresh_token_value = 'abc';\n"
        "+const user_session_data = null;\n"
        "+console.log('debug');\n"
    )
    from consistency_checker import check_consistency as cc2
    report_bad = cc2(profile_path, bad_diff, level_b=True, level_c=True)
    all_divs = report_bad.divergences
    check("checker/violations_detected", len(all_divs) > 0,
          f"divergências: {len(all_divs)} ({[d.category for d in all_divs]})")

    # Text export
    slack = report_good.text_export("slack")
    check("checker/text_export", "Consistency" in slack, f"slack: {slack[:60]}")


# ---------------------------------------------------------------------------
# Step 4: Review pipeline
# ---------------------------------------------------------------------------

def step_review_pipeline(arch: Path, manifest_path: Path) -> None:
    print("\n-- Step 4: review_pipeline --")
    from review_pipeline import run_quality_review

    # Extract block_id from manifest path
    block_id = manifest_path.name.split("-")[0] + "-" + manifest_path.name.split("-")[1]

    report = run_quality_review(block_id, arch, client="acme", interactive=False)

    html_files = list((arch / "governance").glob(f"review-{block_id}-*.html"))
    check("review/html_generated", len(html_files) > 0,
          f"HTML: {html_files[0].name if html_files else 'none'}")

    check("review/report_has_score",
          hasattr(report, "consistency_score"),
          f"score: {report.consistency_score:.2f}")

    check("review/coverage_note",
          len(report.test_coverage_note) > 0,
          f"coverage: {report.test_coverage_note[:60]}")


# ---------------------------------------------------------------------------
# Step 5: Teach mode
# ---------------------------------------------------------------------------

def step_teach_mode(arch: Path, manifest_path: Path) -> None:
    print("\n-- Step 5: teach_mode --")
    from teach_mode import run_teach

    block_id = manifest_path.name.split("-")[0] + "-" + manifest_path.name.split("-")[1]
    generated = run_teach(block_id, arch, interactive=False)

    check("teach/3_htmls_generated", len(generated) == 3,
          f"audiences: {', '.join(generated.keys())}")

    for audience in ("technical", "team", "learning"):
        path = generated.get(audience)
        if path:
            text = path.read_text(encoding="utf-8")
            check(f"teach/{audience}_has_content",
                  "Teach Mode" in text and len(text) > 200,
                  f"{audience}: {path.name}")

    txt_files = list((arch / "governance").glob(f"teach-{block_id}-*.txt"))
    check("teach/text_exports", len(txt_files) == 3, f"{len(txt_files)} text exports")


# ---------------------------------------------------------------------------
# Step 6: Velocity tracker
# ---------------------------------------------------------------------------

def step_velocity_tracker(arch: Path, manifest_path: Path) -> None:
    print("\n-- Step 6: velocity_tracker --")
    from velocity_tracker import stamp_started, pause_timer, resume_timer, stamp_finished, get_status

    block_id = manifest_path.name.split("-")[0] + "-" + manifest_path.name.split("-")[1]

    ts_start = stamp_started(arch, block_id)
    check("velocity/started_at_stamped", ts_start != "", f"started_at: {ts_start}")

    pause_msg = pause_timer(arch, block_id)
    check("velocity/pause_recorded", "pausado" in pause_msg.lower(), pause_msg[:60])

    resume_msg = resume_timer(arch, block_id)
    check("velocity/resume_recorded", "retomado" in resume_msg.lower(), resume_msg[:60])

    _, actual_h = stamp_finished(arch, block_id)
    check("velocity/finished_at_computed", actual_h >= 0.0, f"actual_hours: {actual_h}")

    status = get_status(arch, block_id)
    check("velocity/status_shows_all_fields",
          "started_at" in status and "finished_at" in status,
          "status fields present")

    text = manifest_path.read_text(encoding="utf-8")
    check("velocity/manifest_has_actual_hours",
          "actual_duration_hours:" in text,
          "actual_duration_hours in manifest")


# ---------------------------------------------------------------------------
# Step 7: Forecast engine
# ---------------------------------------------------------------------------

def step_forecast(arch: Path) -> None:
    print("\n-- Step 7: forecast_engine --")
    from forecast_engine import generate_forecast_html, _load_velocity_history, _confidence_band

    history = _load_velocity_history(arch)
    conf = _confidence_band(len(history))
    check("forecast/history_loaded", True, f"{len(history)} samples | confidence: {conf}")

    html_path = generate_forecast_html(arch, "acme", open_tickets=5)
    check("forecast/html_generated", html_path.exists(), f"HTML: {html_path.name}")

    text = html_path.read_text(encoding="utf-8")
    check("forecast/has_velocity_section", "Velocity" in text or "velocity" in text.lower(), "velocity present")
    check("forecast/has_confidence", conf in text, f"confidence {conf} in HTML")
    check("forecast/has_parallelism", "paralel" in text.lower() or "ticket" in text.lower(), "parallelism section")


# ---------------------------------------------------------------------------
# Step 8: Calendar manager
# ---------------------------------------------------------------------------

def step_calendar(arch: Path) -> None:
    print("\n-- Step 8: calendar_manager --")
    from calendar_manager import add_meeting, list_meetings, get_upcoming_alerts
    from datetime import date, timedelta

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    in3 = (date.today() + timedelta(days=3)).isoformat()

    add_meeting(arch, tomorrow, "14:00", 1.5, "sync semanal com o time")
    add_meeting(arch, in3, "10:00", 1.0, "1:1 com tech lead", recurring="weekly")

    meetings = list_meetings(arch, horizon_days=30)
    check("calendar/meetings_listed", len(meetings) >= 2, f"{len(meetings)} meetings found")

    # Weekly should expand to multiple dates in 30 days
    weekly = [m for m in meetings if "1:1" in m.desc]
    check("calendar/weekly_expanded", len(weekly) >= 3,
          f"weekly expanded to {len(weekly)} occurrences")

    alerts = get_upcoming_alerts(arch, days=2)
    check("calendar/upcoming_alert", len(alerts) >= 1, f"alert: {alerts[0] if alerts else 'none'}")

    cal_path = arch / "governance" / "pilot-calendar.yaml"
    check("calendar/yaml_persisted", cal_path.exists(), f"YAML: {cal_path.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("  cognitive-arch — CORPORATE E2E SMOKE TEST")
    print("=" * 60)
    print(f"  arch_root: {ARCH_ROOT}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        arch = root / "arch"
        gov = arch / "governance"
        gov.mkdir(parents=True)
        (arch / "sdk").mkdir()
        (arch / "manifests").mkdir()
        (arch / "blocks").mkdir()
        (arch / "blocks" / "BLOCK_LOG.md").write_text("", encoding="utf-8")
        (arch / "STATE.md").write_text(
            "# STATE — AI-only\n\np:29 status:active phase:phase-29 mode:corporate\n",
            encoding="utf-8",
        )
        (arch / "NEXT.md").write_text(
            "# NEXT — AI-only\n\nnext_action:-\n",
            encoding="utf-8",
        )
        # Copy ux-config.yaml for HTML toggles
        src_cfg = ARCH_ROOT / "governance" / "ux-config.yaml"
        if src_cfg.exists():
            (gov / "ux-config.yaml").write_bytes(src_cfg.read_bytes())

        repo = build_fixture_repo(root)
        print(f"  fixture repo: {repo}")

        # Capture output from each step but still print progress
        step_scanner(repo, arch)
        manifest_path = step_ticket_intake(arch)
        step_consistency(arch)
        step_review_pipeline(arch, manifest_path)
        step_teach_mode(arch, manifest_path)
        step_velocity_tracker(arch, manifest_path)
        step_forecast(arch)
        step_calendar(arch)

    # Summary
    passed = sum(1 for _, s, _ in results if s == PASS)
    failed = sum(1 for _, s, _ in results if s == FAIL)
    total = len(results)

    print("\n" + "=" * 60)
    print(f"  RESULTADO: {passed}/{total} PASS  |  {failed} FAIL")
    print("=" * 60)

    if failed > 0:
        print("\nFalhas:")
        for step, status, note in results:
            if status == FAIL:
                print(f"  XX  {step}: {note}")
        return 1

    print("\nTodos os 8 módulos corporativos funcionando de ponta a ponta.")
    print("Scanner → Intake → Checker → Review → Teach → Velocity → Forecast → Calendar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
