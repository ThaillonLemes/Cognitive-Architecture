# PURPOSE: Tests for sdk/proposal_resolver.py — accept/reject proposals
# INPUTS:  tmp_path, synthetic proposal files and index.md
# OUTPUTS: assertions on file mutations and return values
# DEPS:    pytest, pathlib, proposal_resolver module
# SEE:     sdk/proposal_resolver.py, templates/proposal.md, phases/phase-20.md block-125

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

from proposal_resolver import (
    ProposalResolver,
    _get_frontmatter_field,
    _is_immutable,
    _update_frontmatter_field,
    _update_index_status,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_PROPOSAL_PENDING = """\
---
id: 2026-05-28-scope-expansion
status: pending
pattern_id: scope-expansion-recurring
target_file: templates/manifest-medium.md
proposed_change: |
  Review the template.
rationale: |
  Pattern detected 4 times.
created_at: 2026-05-28
resolved_at: ~
resolved_by: ~
signal_count_d1: 4
---

# Proposal — scope-expansion-recurring

## 5. Resolution

**Status:** pending
"""

_INDEX_WITH_PENDING = (
    "# Proposals Index\n\n"
    "| Date | ID | Pattern | Target File | Status |\n"
    "|------|----|---------|-------------|--------|\n"
    "| 2026-05-28 | [2026-05-28-scope-expansion](governance/proposals/2026-05-28-scope-expansion.md)"
    " | scope-expansion-recurring | templates/manifest-medium.md | pending |\n"
)


def _make_proposal_env(tmp_path: Path, proposal_content: str = _PROPOSAL_PENDING) -> tuple[Path, Path]:
    """Create a minimal proposals environment. Returns (arch_root, proposal_path)."""
    gov = tmp_path / "governance"
    proposals_dir = gov / "proposals"
    proposals_dir.mkdir(parents=True)

    proposal_path = proposals_dir / "2026-05-28-scope-expansion.md"
    proposal_path.write_text(proposal_content, encoding="utf-8")

    index_path = proposals_dir / "index.md"
    index_path.write_text(_INDEX_WITH_PENDING, encoding="utf-8")

    return tmp_path, proposal_path


# ---------------------------------------------------------------------------
# _update_frontmatter_field
# ---------------------------------------------------------------------------

class TestUpdateFrontmatterField:
    def test_updates_existing_field(self):
        text = "---\nstatus: pending\n---\nbody"
        result = _update_frontmatter_field(text, "status", "accepted")
        assert "status: accepted" in result
        assert "status: pending" not in result

    def test_inserts_missing_field(self):
        text = "---\nid: test\n---\nbody"
        result = _update_frontmatter_field(text, "resolved_at", "2026-05-28")
        assert "resolved_at: 2026-05-28" in result

    def test_existing_field_not_duplicated(self):
        text = "---\nstatus: pending\n---\n"
        result = _update_frontmatter_field(text, "status", "accepted")
        assert result.count("status:") == 1


# ---------------------------------------------------------------------------
# _get_frontmatter_field
# ---------------------------------------------------------------------------

class TestGetFrontmatterField:
    def test_returns_value(self):
        text = "---\nstatus: pending\n---\n"
        assert _get_frontmatter_field(text, "status") == "pending"

    def test_returns_none_when_missing(self):
        text = "---\nid: test\n---\n"
        assert _get_frontmatter_field(text, "status") is None

    def test_strips_quotes(self):
        text = "---\nstatus: \"pending\"\n---\n"
        assert _get_frontmatter_field(text, "status") == "pending"


# ---------------------------------------------------------------------------
# _update_index_status
# ---------------------------------------------------------------------------

class TestUpdateIndexStatus:
    def test_updates_pending_to_accepted(self, tmp_path):
        index = tmp_path / "index.md"
        index.write_text(_INDEX_WITH_PENDING, encoding="utf-8")
        result = _update_index_status(index, "2026-05-28-scope-expansion", "accepted")
        assert result is True
        assert "accepted" in index.read_text(encoding="utf-8")

    def test_returns_false_on_missing_index(self, tmp_path):
        result = _update_index_status(tmp_path / "missing.md", "any-id", "accepted")
        assert result is False

    def test_returns_false_when_id_not_found(self, tmp_path):
        index = tmp_path / "index.md"
        index.write_text(_INDEX_WITH_PENDING, encoding="utf-8")
        result = _update_index_status(index, "nonexistent-id", "accepted")
        assert result is False


# ---------------------------------------------------------------------------
# _is_immutable
# ---------------------------------------------------------------------------

class TestIsImmutable:
    def test_immutable_when_protocols_mentions_it(self, tmp_path):
        (tmp_path / "PROTOCOLS.md").write_text(
            "PROTOCOLS.md: immutable — never modify directly\n", encoding="utf-8"
        )
        assert _is_immutable("PROTOCOLS.md", tmp_path) is True

    def test_not_immutable_when_not_mentioned(self, tmp_path):
        (tmp_path / "PROTOCOLS.md").write_text("normal content\n", encoding="utf-8")
        assert _is_immutable("templates/manifest.md", tmp_path) is False

    def test_immutable_via_file_header(self, tmp_path):
        target = tmp_path / "some-file.md"
        target.write_text("protection: immutable\n\n# Content", encoding="utf-8")
        assert _is_immutable("some-file.md", tmp_path) is True

    def test_no_protocols_file_not_immutable(self, tmp_path):
        assert _is_immutable("any-file.md", tmp_path) is False


# ---------------------------------------------------------------------------
# ProposalResolver.accept
# ---------------------------------------------------------------------------

class TestProposalResolverAccept:
    def test_accept_sets_status_accepted(self, tmp_path):
        root, proposal_path = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        ok, _ = resolver.accept("2026-05-28-scope-expansion")
        assert ok
        text = proposal_path.read_text(encoding="utf-8")
        assert "status: accepted" in text

    def test_accept_sets_resolved_at(self, tmp_path):
        root, proposal_path = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        resolver.accept("2026-05-28-scope-expansion")
        text = proposal_path.read_text(encoding="utf-8")
        assert "resolved_at:" in text
        assert "~" not in text.split("resolved_at:")[1].split("\n")[0]

    def test_accept_updates_index(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        resolver.accept("2026-05-28-scope-expansion")
        index = (root / "governance" / "proposals" / "index.md").read_text(encoding="utf-8")
        assert "accepted" in index

    def test_accept_not_found_returns_false(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        ok, msg = resolver.accept("nonexistent-id")
        assert not ok
        assert "not found" in msg

    def test_accept_already_accepted_returns_false(self, tmp_path):
        content = _PROPOSAL_PENDING.replace("status: pending", "status: accepted")
        root, _ = _make_proposal_env(tmp_path, content)
        resolver = ProposalResolver(root)
        ok, msg = resolver.accept("2026-05-28-scope-expansion")
        assert not ok
        assert "already" in msg


# ---------------------------------------------------------------------------
# ProposalResolver.accept(apply=True)
# ---------------------------------------------------------------------------

class TestProposalResolverAcceptApply:
    def test_apply_creates_bak(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        target = root / "templates" / "manifest-medium.md"
        target.parent.mkdir(parents=True)
        target.write_text("# Manifest\ncontent\n", encoding="utf-8")
        resolver = ProposalResolver(root)
        ok, msg = resolver.accept("2026-05-28-scope-expansion", apply=True)
        assert ok
        assert target.with_suffix(".md.bak").exists()

    def test_apply_annotates_target(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        target = root / "templates" / "manifest-medium.md"
        target.parent.mkdir(parents=True)
        target.write_text("# Manifest\n", encoding="utf-8")
        resolver = ProposalResolver(root)
        resolver.accept("2026-05-28-scope-expansion", apply=True)
        assert "proposal" in target.read_text(encoding="utf-8").lower()

    def test_apply_immutable_aborts(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        # Make target appear immutable
        target = root / "templates" / "manifest-medium.md"
        target.parent.mkdir(parents=True)
        target.write_text("protection: immutable\n# Content\n", encoding="utf-8")
        resolver = ProposalResolver(root)
        ok, msg = resolver.accept("2026-05-28-scope-expansion", apply=True)
        assert not ok
        assert "immutable" in msg

    def test_apply_missing_target_aborts(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        ok, msg = resolver.accept("2026-05-28-scope-expansion", apply=True)
        assert not ok
        assert "not found" in msg or "cannot apply" in msg.lower()

    def test_apply_placeholder_target_aborts(self, tmp_path):
        content = _PROPOSAL_PENDING.replace(
            "target_file: templates/manifest-medium.md",
            "target_file: protocols/<target>.md"
        )
        root, _ = _make_proposal_env(tmp_path, content)
        resolver = ProposalResolver(root)
        ok, msg = resolver.accept("2026-05-28-scope-expansion", apply=True)
        assert not ok
        assert "placeholder" in msg.lower()


# ---------------------------------------------------------------------------
# ProposalResolver.reject
# ---------------------------------------------------------------------------

class TestProposalResolverReject:
    def test_reject_sets_status_rejected(self, tmp_path):
        root, proposal_path = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        ok, _ = resolver.reject("2026-05-28-scope-expansion")
        assert ok
        text = proposal_path.read_text(encoding="utf-8")
        assert "status: rejected" in text

    def test_reject_with_note_appended(self, tmp_path):
        root, proposal_path = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        resolver.reject("2026-05-28-scope-expansion", note="Not actionable at this time")
        text = proposal_path.read_text(encoding="utf-8")
        assert "Not actionable at this time" in text

    def test_reject_updates_index(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        resolver.reject("2026-05-28-scope-expansion")
        index = (root / "governance" / "proposals" / "index.md").read_text(encoding="utf-8")
        assert "rejected" in index

    def test_reject_not_found_returns_false(self, tmp_path):
        root, _ = _make_proposal_env(tmp_path)
        resolver = ProposalResolver(root)
        ok, msg = resolver.reject("nonexistent-id")
        assert not ok
        assert "not found" in msg

    def test_reject_already_rejected_returns_false(self, tmp_path):
        content = _PROPOSAL_PENDING.replace("status: pending", "status: rejected")
        root, _ = _make_proposal_env(tmp_path, content)
        resolver = ProposalResolver(root)
        ok, msg = resolver.reject("2026-05-28-scope-expansion")
        assert not ok
        assert "already" in msg
