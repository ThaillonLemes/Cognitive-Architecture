# PURPOSE: Tests for _linkify_path() and _read_ux_config() in dashboard_generator.py (block-131)
# INPUTS:  tmp_path, synthetic ux-config.yaml
# OUTPUTS: assertions on HTML anchor output and config reading
# DEPS:    pytest, pathlib, dashboard_generator module
# SEE:     sdk/dashboard_generator.py, governance/ux-config.yaml, block-131

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from dashboard_generator import _linkify_path, _read_ux_config


# ---------------------------------------------------------------------------
# _linkify_path
# ---------------------------------------------------------------------------

class TestLinkifyPath:
    def test_returns_anchor_tag(self):
        html = _linkify_path("sdk/governor.py", protocol="file")
        assert html.startswith('<a href="file://')
        assert "sdk/governor.py" in html
        assert html.endswith("</a>")

    def test_file_protocol(self):
        html = _linkify_path("governance/patterns.md", protocol="file")
        assert "file://" in html

    def test_vscode_protocol(self):
        html = _linkify_path("governance/patterns.md", protocol="vscode")
        assert "vscode://file" in html

    def test_backslash_normalized(self):
        html = _linkify_path(r"blocks\block-001.md", protocol="file",
                             arch_root=Path(r"C:\projects\myapp"))
        assert "\\" not in html.split('"')[1]  # URL part has no backslashes

    def test_empty_path_returned_as_is(self):
        assert _linkify_path("") == ""

    def test_dash_placeholder_returned_as_is(self):
        assert _linkify_path("-") == "-"

    def test_tilde_returned_as_is(self):
        assert _linkify_path("~") == "~"

    def test_unknown_returned_as_is(self):
        assert _linkify_path("unknown") == "unknown"

    def test_display_text_is_original_path(self):
        html = _linkify_path("sdk/health_report.py")
        assert ">sdk/health_report.py<" in html

    def test_title_attribute_present(self):
        html = _linkify_path("manifests/block-001.md")
        assert 'title="manifests/block-001.md"' in html

    def test_arch_root_used_in_href(self, tmp_path):
        html = _linkify_path("governance/dashboard.html", protocol="file", arch_root=tmp_path)
        expected_fragment = str(tmp_path).replace("\\", "/")
        assert expected_fragment in html

    def test_path_with_question_mark_returned_as_is(self):
        assert _linkify_path("?") == "?"


# ---------------------------------------------------------------------------
# _read_ux_config
# ---------------------------------------------------------------------------

class TestReadUxConfig:
    def test_defaults_on_missing_file(self, tmp_path):
        config = _read_ux_config(str(tmp_path))
        assert config["dashboard_link_protocol"] == "file"
        assert config["dashboard_links_enabled"] is True
        assert config["dashboard_notifications_max"] == 3

    def test_reads_protocol_from_file(self, tmp_path):
        gov = tmp_path / "governance"
        gov.mkdir()
        (gov / "ux-config.yaml").write_text(
            "dashboard_link_protocol: vscode\n", encoding="utf-8"
        )
        config = _read_ux_config(str(tmp_path))
        assert config["dashboard_link_protocol"] == "vscode"

    def test_reads_max_notifications(self, tmp_path):
        gov = tmp_path / "governance"
        gov.mkdir()
        (gov / "ux-config.yaml").write_text(
            "dashboard_notifications_max: 5\n", encoding="utf-8"
        )
        config = _read_ux_config(str(tmp_path))
        assert config["dashboard_notifications_max"] == 5

    def test_links_disabled(self, tmp_path):
        gov = tmp_path / "governance"
        gov.mkdir()
        (gov / "ux-config.yaml").write_text(
            "dashboard_links_enabled: false\n", encoding="utf-8"
        )
        config = _read_ux_config(str(tmp_path))
        assert config["dashboard_links_enabled"] is False

    def test_ignores_comments(self, tmp_path):
        gov = tmp_path / "governance"
        gov.mkdir()
        (gov / "ux-config.yaml").write_text(
            "# this is a comment\ndashboard_link_protocol: vscode\n", encoding="utf-8"
        )
        config = _read_ux_config(str(tmp_path))
        assert config["dashboard_link_protocol"] == "vscode"
