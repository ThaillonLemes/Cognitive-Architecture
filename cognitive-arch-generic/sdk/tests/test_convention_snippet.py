# PURPOSE: Tests for sdk/convention_snippet.py — axiom selection, sort order, edge cases
# INPUTS:  pytest fixtures (none needed — stateless module)
# OUTPUTS: pass/fail test results
# DEPS:    pytest, convention_snippet
# SEE:     manifests/block-052-test-convention-snippet.md, sdk/convention_snippet.py

import pytest
from convention_snippet import build_snippet, AXIOMS, _GROUP_ORDER


class TestAxiomRegistry:
    def test_axiom_count(self):
        """19 axioms must be registered (P1-P6, Q1-Q7, C1-C6)."""
        assert len(AXIOMS) == 19

    def test_all_axiom_ids_present(self):
        """Check that expected axiom IDs all exist."""
        expected = (
            [f"P{i}" for i in range(1, 7)] +
            [f"Q{i}" for i in range(1, 8)] +
            [f"C{i}" for i in range(1, 7)]
        )
        for aid in expected:
            assert aid in AXIOMS, f"Missing axiom: {aid}"

    def test_group_order_values(self):
        """P < Q < C in sort order."""
        assert _GROUP_ORDER["P"] < _GROUP_ORDER["Q"] < _GROUP_ORDER["C"]


class TestBuildSnippet:
    def test_implementation_returns_axioms(self):
        """Implementation kind should return non-empty axiom string and body."""
        axioms_str, body = build_snippet("implementation")
        assert axioms_str
        assert body

    def test_sort_order_p_before_q_before_c(self):
        """Axiom IDs in returned string must be P-group < Q-group < C-group."""
        axioms_str, _ = build_snippet("implementation")
        ids = [a.strip() for a in axioms_str.split(",")]
        groups = [_GROUP_ORDER.get(a[0], 9) for a in ids if a]
        assert groups == sorted(groups), f"Axioms not in P->Q->C order: {ids}"

    def test_doc_only_kind(self):
        axioms_str, body = build_snippet("doc-only")
        assert axioms_str
        assert "P" in axioms_str or "Q" in axioms_str or "C" in axioms_str

    def test_refactor_kind(self):
        axioms_str, body = build_snippet("refactor")
        assert axioms_str

    def test_gate_kind(self):
        axioms_str, body = build_snippet("gate")
        assert axioms_str

    def test_small_fix_kind(self):
        axioms_str, body = build_snippet("small-fix")
        assert axioms_str

    def test_unknown_kind_falls_back(self):
        """Unknown kind should not raise — falls back to a default set."""
        axioms_str, body = build_snippet("nonexistent-kind-xyz")
        assert isinstance(axioms_str, str)
        assert isinstance(body, str)

    def test_axiom_override(self):
        """axiom_override replaces the auto-selected set."""
        axioms_str, body = build_snippet("implementation", axiom_override=["P1", "Q3"])
        assert "P1" in axioms_str
        assert "Q3" in axioms_str

    def test_body_contains_axiom_text(self):
        """Snippet body lines should mention axiom IDs."""
        axioms_str, body = build_snippet("doc-only")
        ids = [a.strip() for a in axioms_str.split(",") if a.strip()]
        # At least one axiom ID should appear in the body
        assert any(aid in body for aid in ids), f"No axiom ID in body:\n{body}"

    def test_modifies_code_param(self):
        """modifies_code=True should include at least one C-group axiom."""
        axioms_str, body = build_snippet("implementation", modifies_code=True)
        assert "C" in axioms_str
