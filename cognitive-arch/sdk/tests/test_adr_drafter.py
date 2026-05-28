# PURPOSE: Tests for sdk/adr_drafter.py — ADR scaffold generation from synthesis decisions
# INPUTS:  tmp_path, synthetic synthesis data dicts
# OUTPUTS: assertions on generated ADR files, index updates, slug generation
# DEPS:    pytest, pathlib, adr_drafter module
# SEE:     sdk/adr_drafter.py, templates/ADR-auto.md, phases/phase-19.md block-117

import json
import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from adr_drafter import AdrDrafter, _make_slug, _rebuild_index


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decision(title, significance="high", **kwargs):
    return {
        "title": title,
        "significance": significance,
        "recommended_option": kwargs.get("recommended_option", "Option A"),
        "options_considered": kwargs.get("options_considered", ["Option A", "Option B"]),
        "confidence_band": kwargs.get("confidence_band", "high"),
        "context": kwargs.get("context", "Test context"),
        "synthesis_source": kwargs.get("synthesis_source", "design/test.md"),
    }


# ---------------------------------------------------------------------------
# _make_slug tests
# ---------------------------------------------------------------------------

class TestMakeSlug:
    def test_spaces_to_hyphens(self):
        assert _make_slug("Use FastAPI for REST") == "use-fastapi-for-rest"

    def test_special_chars_stripped(self):
        assert _make_slug("Auth: JWT vs Sessions!") == "auth-jwt-vs-sessions"

    def test_max_50_chars(self):
        long = "a" * 100
        assert len(_make_slug(long)) <= 50

    def test_empty_string(self):
        result = _make_slug("")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# AdrDrafter.generate tests
# ---------------------------------------------------------------------------

class TestAdrDrafter:
    def test_generates_adr_for_high_significance(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate([_decision("Use Redis for caching", significance="high")])
        assert len(created) == 1
        assert created[0].exists()

    def test_generates_adr_for_medium_significance(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate([_decision("Choose ORM", significance="medium")])
        assert len(created) == 1

    def test_skips_low_significance(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate([_decision("Minor config tweak", significance="low")])
        assert len(created) == 0

    def test_skips_missing_significance(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate([{"title": "No sig field", "recommended_option": "X"}])
        assert len(created) == 0

    def test_two_significant_decisions_two_files(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate([
            _decision("Decision Alpha", significance="high"),
            _decision("Decision Beta", significance="medium"),
        ])
        assert len(created) == 2
        # Both files exist
        for p in created:
            assert p.exists()

    def test_no_overwrite_on_duplicate(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        d = _decision("Same Title", significance="high")
        created1 = drafter.generate([d])
        created2 = drafter.generate([d])
        assert created1[0] != created2[0]  # different paths (counter suffix)
        assert created2[0].exists()

    def test_adr_content_has_required_fields(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate([_decision(
            "Use Postgres", significance="high",
            recommended_option="Postgres",
            confidence_band="high",
            synthesis_source="design/db.md",
        )])
        text = created[0].read_text(encoding="utf-8")
        assert "status: draft" in text
        assert "auto_generated: true" in text
        assert "Postgres" in text
        assert "design/db.md" in text
        assert "HUMAN REQUIRED" in text

    def test_accepts_decisions_key_in_dict(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        data = {"decisions": [_decision("Dict Form", significance="high")]}
        created = drafter.generate(data)
        assert len(created) == 1

    def test_empty_list_produces_no_files(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate([])
        assert created == []

    def test_adrs_dir_created_if_missing(self, tmp_path):
        assert not (tmp_path / "design" / "adrs").exists()
        AdrDrafter(tmp_path).generate([_decision("X", significance="high")])
        assert (tmp_path / "design" / "adrs").exists()

    def test_index_updated_on_generate(self, tmp_path):
        drafter = AdrDrafter(tmp_path)
        drafter.generate([_decision("Indexed ADR", significance="high")])
        index = tmp_path / "governance" / "adrs" / "index.md"
        assert index.exists()
        assert "Indexed ADR" in index.read_text(encoding="utf-8")

    def test_generate_from_file(self, tmp_path):
        synth_path = tmp_path / "synthesis.json"
        synth_path.write_text(json.dumps([_decision("From File", significance="high")]), encoding="utf-8")
        drafter = AdrDrafter(tmp_path)
        created = drafter.generate_from_file(synth_path)
        assert len(created) == 1

    def test_rebuild_index(self, tmp_path):
        # Create two ADR files manually
        adrs = tmp_path / "design" / "adrs"
        adrs.mkdir(parents=True)
        (adrs / "2026-05-28-adr-a.md").write_text(
            "---\ntitle: ADR A\nstatus: draft\ncreated_at: 2026-05-28\n---\n", encoding="utf-8")
        (adrs / "2026-05-28-adr-b.md").write_text(
            "---\ntitle: ADR B\nstatus: accepted\ncreated_at: 2026-05-28\n---\n", encoding="utf-8")
        count = _rebuild_index(tmp_path)
        assert count == 2
        index = tmp_path / "governance" / "adrs" / "index.md"
        content = index.read_text(encoding="utf-8")
        assert "ADR A" in content
        assert "ADR B" in content
