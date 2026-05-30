# PURPOSE: Tests for sdk/integrity_check.py — frontmatter-only immutable detection
#          (block-147: a PROSE mention of `protection: immutable` must NOT count;
#          only a real frontmatter field does) + load_lock / verify basics.
# INPUTS:  tmp_path; synthetic .md files (frontmatter-tagged, prose-only, malformed)
# OUTPUTS: assertions on find_immutable_files / is_immutable_text / load_lock / verify
# DEPS:    pytest, pathlib, integrity_check module
# SEE:     sdk/integrity_check.py, sdk/invariant_check.py (INV1), manifests/block-147-backfill-verify.md

import sys
from pathlib import Path

import pytest

_SDK_DIR = Path(__file__).resolve().parent.parent
if str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))

import integrity_check as ic


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# is_immutable_text — the frontmatter-field discriminator (the block-147 fix)
# ---------------------------------------------------------------------------

class TestIsImmutableText:
    def test_frontmatter_tag_counts(self):
        text = "---\nid: foo\nprotection: immutable\n---\n\n# Foo\n"
        assert ic.is_immutable_text(text) is True

    def test_frontmatter_tag_first_line(self):
        text = "---\nprotection: immutable\n---\n# Foo\n"
        assert ic.is_immutable_text(text) is True

    def test_frontmatter_tag_quoted(self):
        assert ic.is_immutable_text('---\nprotection: "immutable"\n---\n') is True
        assert ic.is_immutable_text("---\nprotection: 'immutable'\n---\n") is True

    def test_frontmatter_tag_trailing_comment(self):
        text = "---\nprotection: immutable  # core file\n---\n"
        assert ic.is_immutable_text(text) is True

    def test_prose_mention_does_not_count(self):
        # The exact phrase, but in the BODY (after frontmatter / no frontmatter).
        text = (
            "---\nid: block-144\ntier: M\n---\n\n"
            "# Block 144\n\n"
            "INV1 (critical): every `protection: immutable` file is in the lock.\n"
        )
        assert ic.is_immutable_text(text) is False

    def test_prose_mention_no_frontmatter_at_all(self):
        # A command/protocol doc with NO frontmatter that merely discusses the tag.
        text = (
            "# Protocol: architecture-integrity\n\n"
            "| `protection: immutable` | Core files | refuse to edit |\n"
        )
        assert ic.is_immutable_text(text) is False

    def test_phrase_in_frontmatter_but_other_field_does_not_count(self):
        # Phrase appears as a VALUE of an unrelated field, not the protection field.
        text = "---\nnote: discusses protection: immutable here\nid: x\n---\n"
        assert ic.is_immutable_text(text) is False

    def test_other_protection_value_does_not_count(self):
        text = "---\nprotection: guard\n---\n"
        assert ic.is_immutable_text(text) is False

    def test_empty_and_garbage_never_raise(self):
        assert ic.is_immutable_text("") is False
        assert ic.is_immutable_text("no frontmatter, no phrase") is False
        assert ic.is_immutable_text("---\nunterminated frontmatter\nprotection: immutable\n") is False

    def test_leading_blank_lines_and_bom_tolerated(self):
        assert ic.is_immutable_text("\n\n---\nprotection: immutable\n---\n") is True
        assert ic.is_immutable_text("﻿---\nprotection: immutable\n---\n") is True


# ---------------------------------------------------------------------------
# find_immutable_files — walks the tree, frontmatter-only
# ---------------------------------------------------------------------------

class TestFindImmutableFiles:
    def test_tagged_file_is_found_prose_file_is_not(self, tmp_path):
        root = tmp_path / "arch"
        # Genuinely tagged via frontmatter -> MUST be found.
        _write(root / "PROTOCOLS.md", "---\nprotection: immutable\n---\n# P\n")
        # Prose-only mention (like a manifest discussing INV1) -> MUST NOT be found.
        _write(
            root / "manifests" / "block-144-invariant-engine.md",
            "---\nid: block-144\ntier: M\n---\n\nevery `protection: immutable` file in lock\n",
        )
        # A phase doc discussing it -> MUST NOT be found.
        _write(
            root / "phases" / "phase-25.md",
            "---\nid: phase-25\n---\n\nINV1: every file tagged `protection: immutable`\n",
        )
        found = ic.find_immutable_files(root)
        assert "PROTOCOLS.md" in found
        assert "manifests/block-144-invariant-engine.md" not in found
        assert "phases/phase-25.md" not in found
        assert found == ["PROTOCOLS.md"]

    def test_hidden_dirs_skipped(self, tmp_path):
        root = tmp_path / "arch"
        _write(root / ".git" / "x.md", "---\nprotection: immutable\n---\n")
        _write(root / "ok.md", "---\nprotection: immutable\n---\n")
        found = ic.find_immutable_files(root)
        assert found == ["ok.md"]

    def test_empty_root_returns_empty(self, tmp_path):
        assert ic.find_immutable_files(tmp_path / "nope") == []


# ---------------------------------------------------------------------------
# load_lock / verify — unchanged behaviour, smoke coverage
# ---------------------------------------------------------------------------

class TestLockAndVerify:
    def test_load_lock_parses_entries(self, tmp_path):
        root = tmp_path / "arch"
        _write(
            root / ".integrity.lock",
            "# comment\nPROTOCOLS.md  sha256:" + ("a" * 64) + "\n",
        )
        lock = ic.load_lock(root)
        assert lock == {"PROTOCOLS.md": "a" * 64}

    def test_verify_ok_and_mismatch(self, tmp_path):
        root = tmp_path / "arch"
        _write(root / "PROTOCOLS.md", "---\nprotection: immutable\n---\n# P\n")
        good = ic.sha256_of_file(root / "PROTOCOLS.md")
        _write(root / ".integrity.lock", f"PROTOCOLS.md  sha256:{good}\n")
        assert ic.verify(root) == [("PROTOCOLS.md", "OK")]

        _write(root / ".integrity.lock", "PROTOCOLS.md  sha256:" + ("b" * 64) + "\n")
        assert ic.verify(root) == [("PROTOCOLS.md", "MISMATCH")]

    def test_verify_missing_file(self, tmp_path):
        root = tmp_path / "arch"
        _write(root / ".integrity.lock", "gone.md  sha256:" + ("c" * 64) + "\n")
        assert ic.verify(root) == [("gone.md", "MISSING")]
