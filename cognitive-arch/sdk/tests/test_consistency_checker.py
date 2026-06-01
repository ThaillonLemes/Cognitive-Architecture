# sdk/tests/test_consistency_checker.py
# PURPOSE: Validate consistency checker: B+C levels, threshold dynamics, text export.
# BLOCK:   block-170

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_profile(tmp: str, naming: str = "camelCase", import_style: str = "named imports preferred") -> Path:
    arch = Path(tmp) / "arch"
    (arch / "governance").mkdir(parents=True)
    profile_path = arch / "governance" / "project-profile-acme.md"
    profile_path.write_text(
        f"# Project Profile — acme\n\n"
        f"## L3 — Estética & convenções\n"
        f"_L3_scanned_at: 2026-06-01T00:00Z_\n\n"
        f"naming: variables: {naming} · functions: {naming}\n"
        f"imports: {import_style}\n"
        f"consistency_threshold: 0.80\n",
        encoding="utf-8",
    )
    return profile_path


def _diff_with_snake_case() -> str:
    return """+const my_variable = 1;
+const my_other_var = 2;
+const yet_another = 3;
"""


def _diff_clean() -> str:
    return """+const myVariable = 1;
+import { useState } from 'react';
"""


# ---------------------------------------------------------------------------
# Level B tests
# ---------------------------------------------------------------------------

def test_clean_diff_scores_high():
    with tempfile.TemporaryDirectory() as tmp:
        profile = _make_profile(tmp)
        from consistency_checker import check_consistency
        report = check_consistency(profile, _diff_clean(), level_b=True, level_c=False)
        assert report.score >= 0.80
        assert report.passed is True


def test_snake_case_in_camel_project_detected():
    with tempfile.TemporaryDirectory() as tmp:
        profile = _make_profile(tmp, naming="camelCase")
        from consistency_checker import check_consistency
        report = check_consistency(profile, _diff_with_snake_case(), level_b=True, level_c=False)
        naming_divs = [d for d in report.divergences if d.category == "naming"]
        assert len(naming_divs) > 0


def test_three_divergences_detected():
    with tempfile.TemporaryDirectory() as tmp:
        profile = _make_profile(tmp, naming="camelCase",
                                import_style="named imports preferred")
        diff = (
            "+const my_one = 1;\n"
            "+const my_two = 2;\n"
            "+import DefaultThing from './thing';\n"
        )
        from consistency_checker import check_consistency
        report = check_consistency(profile, diff, level_b=True, level_c=False)
        # Should detect both naming and import divergences
        assert len(report.divergences) >= 2


# ---------------------------------------------------------------------------
# Level C tests
# ---------------------------------------------------------------------------

def test_level_c_off_no_console_log_check():
    with tempfile.TemporaryDirectory() as tmp:
        profile = _make_profile(tmp)
        diff = "+console.log('debug info');\n"
        from consistency_checker import check_consistency
        report = check_consistency(profile, diff, level_b=True, level_c=False)
        console_divs = [d for d in report.divergences if "console" in d.description]
        assert len(console_divs) == 0


def test_level_c_on_detects_console_log():
    with tempfile.TemporaryDirectory() as tmp:
        profile = _make_profile(tmp)
        diff = "+console.log('debug info');\n"
        from consistency_checker import check_consistency
        report = check_consistency(profile, diff, level_b=True, level_c=True)
        console_divs = [d for d in report.divergences if "console" in d.description.lower()]
        assert len(console_divs) >= 1


# ---------------------------------------------------------------------------
# Threshold dynamics
# ---------------------------------------------------------------------------

def test_threshold_rises_with_high_scores():
    from consistency_checker import compute_dynamic_threshold
    history = [0.92, 0.94, 0.91, 0.93, 0.95]
    new_t = compute_dynamic_threshold(history, current_threshold=0.80)
    assert new_t > 0.80


def test_threshold_does_not_fall():
    from consistency_checker import compute_dynamic_threshold
    history = [0.60, 0.65, 0.70, 0.62, 0.68]
    new_t = compute_dynamic_threshold(history, current_threshold=0.80)
    assert new_t == 0.80


def test_threshold_insufficient_history():
    from consistency_checker import compute_dynamic_threshold
    history = [0.95, 0.96]  # only 2 — less than lookback=5
    new_t = compute_dynamic_threshold(history, current_threshold=0.80)
    assert new_t == 0.80


# ---------------------------------------------------------------------------
# Text export
# ---------------------------------------------------------------------------

def test_text_export_slack():
    with tempfile.TemporaryDirectory() as tmp:
        profile = _make_profile(tmp)
        from consistency_checker import check_consistency
        report = check_consistency(profile, _diff_clean())
        slack = report.text_export("slack")
        assert "Consistency" in slack
        import re as _re
        assert _re.search(r"[0-9]\.[0-9]{2}", slack), "score not present in slack export"


def test_no_profile_raises():
    from consistency_checker import check_consistency
    import pytest
    with pytest.raises(FileNotFoundError):
        check_consistency(Path("/nonexistent/profile.md"), "diff text")


if __name__ == "__main__":
    test_clean_diff_scores_high()
    test_snake_case_in_camel_project_detected()
    test_three_divergences_detected()
    test_level_c_off_no_console_log_check()
    test_level_c_on_detects_console_log()
    test_threshold_rises_with_high_scores()
    test_threshold_does_not_fall()
    test_threshold_insufficient_history()
    test_text_export_slack()
    test_no_profile_raises()
    print("All block-170 tests passed.")
