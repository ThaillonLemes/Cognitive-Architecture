# PURPOSE: Tests for sdk/task_packet.py — build_packet() field coverage, edge cases
# INPUTS:  pytest fixtures (sample_manifest_path, sample_manifest_rel, tmp_path, arch_root)
# OUTPUTS: pass/fail test results
# DEPS:    pytest, task_packet
# SEE:     manifests/block-053-test-task-packet.md, sdk/task_packet.py

import pytest
from pathlib import Path
from task_packet import build_packet, _parse_frontmatter, _paths_from_manifest, _SCOPE_MAP


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        text = "---\nid: block-001\nkind: doc-only\n---\n# Body"
        fm = _parse_frontmatter(text)
        assert fm["id"] == "block-001"
        assert fm["kind"] == "doc-only"

    def test_missing_frontmatter_raises(self):
        with pytest.raises(ValueError, match="No YAML frontmatter"):
            _parse_frontmatter("# No frontmatter here")

    def test_no_body_between_delimiters_raises(self):
        """Bare --- / --- with no newline between raises ValueError (regex requires content)."""
        with pytest.raises(ValueError, match="No YAML frontmatter"):
            _parse_frontmatter("---\n---\n# Body")


class TestPathsFromManifest:
    def test_read_and_create_paths(self):
        fm = {
            "files": {
                "read": ["STATE.md", "NEXT.md"],
                "modify": [],
                "create": ["sdk/new_module.py"],
            }
        }
        fread, fmod = _paths_from_manifest(fm)
        assert fread == ["STATE.md", "NEXT.md"]
        assert fmod == ["sdk/new_module.py"]

    def test_modify_and_create_merged_into_fmod(self):
        fm = {
            "files": {
                "read": [],
                "modify": ["sdk/governor.py"],
                "create": ["sdk/helpers.py"],
            }
        }
        fread, fmod = _paths_from_manifest(fm)
        assert "sdk/governor.py" in fmod
        assert "sdk/helpers.py" in fmod

    def test_missing_files_section_returns_empty(self):
        fread, fmod = _paths_from_manifest({})
        assert fread == []
        assert fmod == []


class TestScopeMap:
    def test_doc_only_is_closed(self):
        assert _SCOPE_MAP["doc-only"] == "closed"

    def test_implementation_is_open(self):
        assert _SCOPE_MAP["implementation"] == "open"

    def test_gate_is_closed(self):
        assert _SCOPE_MAP["gate"] == "closed"

    def test_small_fix_is_open(self):
        assert _SCOPE_MAP["small-fix"] == "open"


class TestBuildPacket:
    def test_packet_contains_block_id(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "b:999" in packet

    def test_packet_contains_gov_field(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "gov:g-test" in packet

    def test_packet_contains_fread_field(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "fread:" in packet
        assert "STATE.md" in packet

    def test_packet_contains_fmod_field(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "fmod:" in packet

    def test_packet_contains_axioms_field(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "axioms:" in packet

    def test_packet_contains_scope_field(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        # doc-only kind → scope:closed
        assert "scope:closed" in packet

    def test_packet_contains_manifest_delimiter(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "--- manifest ---" in packet

    def test_packet_contains_manifest_body(self, sample_manifest_path, tmp_path):
        """The manifest's own content must appear in the packet."""
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "block-999" in packet
        assert "Sample" in packet

    def test_packet_contains_ts_field(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "ts:2026-05-22T12:00Z" in packet

    def test_missing_manifest_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            build_packet(
                "manifests/nonexistent-block-000.md",
                arch_root=tmp_path,
                gov_id="g-test",
            )

    def test_scope_override(self, sample_manifest_path, tmp_path):
        """scope_override must appear in packet regardless of kind."""
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            scope_override="two-phase",
        )
        assert "scope:two-phase" in packet

    def test_sid_appears_when_passed(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            sid="s-abc123",
        )
        assert "sid:s-abc123" in packet

    def test_sid_absent_when_not_passed(self, sample_manifest_path, tmp_path):
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "sid:" not in packet

    def test_axiom_override_appears(self, sample_manifest_path, tmp_path):
        """axiom_override list replaces auto-selected axioms."""
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            axiom_override=["P1", "C2"],
        )
        assert "P1" in packet
        assert "C2" in packet

    def test_ts_defaults_to_now(self, sample_manifest_path, tmp_path):
        """When ts is omitted, packet must still contain ts: field."""
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
        )
        assert "ts:" in packet

    def test_retro_req_tok_track_fields(self, sample_manifest_path, tmp_path):
        """retro_req and tok_track must always be present."""
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
        )
        assert "retro_req:yes" in packet
        assert "tok_track:yes" in packet


class TestBuildPacketIncludeContent:
    def test_include_content_false_no_file_section(self, sample_manifest_path, tmp_path):
        """Default (include_content=False) must NOT include file content section."""
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            include_content=False,
        )
        assert "--- file content ---" not in packet

    def test_include_content_true_adds_section(self, sample_manifest_path, tmp_path):
        """include_content=True must add '--- file content ---' section."""
        # Write a real fread file so content can be included
        (tmp_path / "STATE.md").write_text("# STATE\np:7 status:active\n", encoding="utf-8")
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            include_content=True,
        )
        assert "--- file content ---" in packet

    def test_include_content_includes_fread_path_header(self, sample_manifest_path, tmp_path):
        """Each fread file should appear as a comment header in the content section."""
        (tmp_path / "STATE.md").write_text("# STATE\np:7 status:active\n", encoding="utf-8")
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            include_content=True,
        )
        assert "# STATE.md" in packet

    def test_include_content_includes_file_text(self, sample_manifest_path, tmp_path):
        """Actual file content (first 30 lines) must appear in the packet."""
        (tmp_path / "STATE.md").write_text("# STATE HEADER\np:7 status:active\n", encoding="utf-8")
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            include_content=True,
        )
        assert "# STATE HEADER" in packet

    def test_include_content_missing_file_graceful(self, sample_manifest_path, tmp_path):
        """Missing fread file must be noted as '# (not found: ...)' without raising."""
        # Do NOT create STATE.md — it's listed in fread but doesn't exist
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            include_content=True,
        )
        assert "not found" in packet
        assert "STATE.md" in packet

    def test_include_content_does_not_affect_header(self, sample_manifest_path, tmp_path):
        """Enabling include_content must not change the header fields."""
        (tmp_path / "STATE.md").write_text("content\n", encoding="utf-8")
        packet = build_packet(
            "manifests/block-999-sample.md",
            arch_root=tmp_path,
            gov_id="g-test",
            ts="2026-05-22T12:00Z",
            include_content=True,
        )
        assert "b:999" in packet
        assert "gov:g-test" in packet
        assert "retro_req:yes" in packet
