# sdk/tests/test_review_pipeline.py
# PURPOSE: Validate review pipeline: HTML generation, go/no-go prompt, override recording.
# BLOCK:   block-171

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sdk"))


def _make_arch(tmp: str, client: str = "acme") -> Path:
    arch = Path(tmp) / "arch"
    gov = arch / "governance"
    gov.mkdir(parents=True)
    (arch / "sdk").mkdir()
    (arch / "STATE.md").write_text("# STATE\n\np:31 status:active\n", encoding="utf-8")
    (arch / "NEXT.md").write_text("# NEXT\n\nnext_action:-\n", encoding="utf-8")
    (arch / "manifests").mkdir()
    (gov / "ux-config.yaml").write_text(
        "pipeline_quality_b: true\nconsistency_checker:\n  level_b: true\n  level_c: false\n",
        encoding="utf-8",
    )
    # Project profile with L3 section
    (gov / f"project-profile-{client}.md").write_text(
        f"# Project Profile — {client}\n\n"
        "## L3 — Estética & convenções\n_L3_scanned_at: 2026-06-01T00:00Z_\n\n"
        "naming: variables: camelCase · functions: camelCase\n"
        "imports: named imports preferred\nconsistency_threshold: 0.80\n",
        encoding="utf-8",
    )
    return arch


def _make_manifest(arch: Path, block_id: str, client: str = "acme") -> None:
    (arch / "manifests" / f"{block_id}-ticket.md").write_text(
        f"---\nid: {block_id}\nsize: S\nimportance: normal\nkind: ticket\n"
        f"client_id: {client}\nphase: phase-31\nstatus: wip\n"
        "files:\n  create:\n    - src/auth/refresh.ts\n---\n",
        encoding="utf-8",
    )


def test_quality_html_generated():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from review_pipeline import run_quality_review
        report = run_quality_review("block-999", arch, interactive=False)

        html_files = list((arch / "governance").glob("review-block-999-*.html"))
        assert len(html_files) == 1
        text = html_files[0].read_text(encoding="utf-8")
        assert "Quality Report" in text
        assert "Consistency" in text


def test_html_has_big_o_section_when_nested_loops():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")
        diff = Path(tmp) / "changes.diff"
        diff.write_text(
            "+for (const item of items) {\n+  for (const sub of item.subs) {\n+    process(sub);\n+  }\n+}\n",
            encoding="utf-8",
        )

        from review_pipeline import run_quality_review
        report = run_quality_review("block-999", arch, diff_path=diff, interactive=False)
        assert len(report.complexity_notes) > 0
        assert "O(n²)" in report.complexity_notes[0].complexity


def test_override_records_reason():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")
        # Diff with divergences to force low score
        diff = Path(tmp) / "changes.diff"
        diff.write_text(
            "+const my_bad_name = 1;\n+const yet_another_bad = 2;\n+const third_bad_one = 3;\n",
            encoding="utf-8",
        )

        from review_pipeline import run_quality_review, _record_override
        _record_override(arch, "block-999", "prazo urgente — aceito divergência naming")

        manifest = arch / "manifests" / "block-999-ticket.md"
        text = manifest.read_text(encoding="utf-8")
        assert "gate_override_reason" in text
        assert "prazo urgente" in text


def test_no_profile_quality_passes():
    """Without a profile, quality gate should pass with warning."""
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp, client="unknown")
        _make_manifest(arch, "block-999", client="noprofile")

        from review_pipeline import run_quality_review
        report = run_quality_review("block-999", arch, interactive=False)
        assert report.overall_passed is True


def test_quality_export_text():
    with tempfile.TemporaryDirectory() as tmp:
        arch = _make_arch(tmp)
        _make_manifest(arch, "block-999")

        from review_pipeline import run_quality_review
        report = run_quality_review("block-999", arch, interactive=False)

        # ConsistencyReport has text_export method
        from consistency_checker import check_consistency
        profile = arch / "governance" / "project-profile-acme.md"
        con = check_consistency(profile, "")
        export = con.text_export("slack")
        assert "Consistency" in export


if __name__ == "__main__":
    test_quality_html_generated()
    test_html_has_big_o_section_when_nested_loops()
    test_override_records_reason()
    test_no_profile_quality_passes()
    test_quality_export_text()
    print("All block-171 tests passed.")
