"""Tests for the divergence analyzer."""

from pathlib import Path

import pytest

from vigiles_engine.auditor import AuditReport, Finding, run_audit
from vigiles_engine.divergence import analyze_divergence
from vigiles_engine.regime import load_all_regimes

REGIMES_DIR = Path(__file__).parent.parent / "regimes"
REGISTRY_PATH = Path(__file__).parent.parent.parent / "organvm-corpvs-testamentvm" / "registry-v2.json"


class TestAnalyzeDivergence:
    def test_requires_at_least_two_reports(self):
        """Should raise if fewer than 2 reports."""
        report = AuditReport("Test", "test", "2026-01-01", [])
        with pytest.raises(ValueError, match="at least 2"):
            analyze_divergence([report])

    def test_identical_reports_produce_consensus(self):
        """Two reports with identical findings should show consensus."""
        finding = Finding("check", "high", "target", "Same description", "")
        r1 = AuditReport("A", "a", "2026-01-01", [Finding("check", "high", "target", "Same description", "a")])
        r2 = AuditReport("B", "b", "2026-01-01", [Finding("check", "high", "target", "Same description", "b")])
        result = analyze_divergence([r1, r2])
        assert len(result.consensus) == 1
        assert result.consensus[0].is_constitutional_candidate

    def test_different_findings_produce_unique(self):
        """Findings only in one report should be unique."""
        r1 = AuditReport("A", "a", "2026-01-01", [
            Finding("check_a", "high", "target/a", "Only A sees this", "a")
        ])
        r2 = AuditReport("B", "b", "2026-01-01", [
            Finding("check_b", "high", "target/b", "Only B sees this", "b")
        ])
        result = analyze_divergence([r1, r2])
        assert len(result.unique_findings["a"]) == 1
        assert len(result.unique_findings["b"]) == 1
        assert len(result.consensus) == 0

    def test_real_tolkien_vs_malazan(self):
        """Real regime comparison should produce meaningful divergence."""
        if not REGIMES_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Regimes or registry not found")
        regimes = load_all_regimes(REGIMES_DIR)
        t_report = run_audit(regimes["tolkien"], REGISTRY_PATH)
        m_report = run_audit(regimes["malazan"], REGISTRY_PATH)
        result = analyze_divergence([t_report, m_report])
        assert result.regimes_compared == ["tolkien", "malazan"]
        # Tolkien should have more unique findings than Malazan
        assert len(result.unique_findings.get("tolkien", [])) > 0
        assert len(result.unique_findings.get("malazan", [])) > 0

    def test_all_nine_regimes_divergence(self):
        """Running all 9 regimes should not crash."""
        if not REGIMES_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Regimes or registry not found")
        regimes = load_all_regimes(REGIMES_DIR)
        reports = [run_audit(r, REGISTRY_PATH) for r in regimes.values()]
        result = analyze_divergence(reports)
        assert len(result.regimes_compared) == 9
