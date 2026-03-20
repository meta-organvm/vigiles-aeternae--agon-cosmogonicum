"""Tests for the regime report generator."""

from pathlib import Path

import pytest

from vigiles_engine.auditor import AuditReport, Finding, run_audit
from vigiles_engine.divergence import analyze_divergence
from vigiles_engine.regime import Regime, load_all_regimes
from vigiles_engine.reporter import render_divergence_report, render_report

REGIMES_DIR = Path(__file__).parent.parent / "regimes"
REGISTRY_PATH = Path(__file__).parent.parent.parent / "organvm-corpvs-testamentvm" / "registry-v2.json"


class TestRenderReport:
    def test_report_contains_regime_name(self):
        """Report should include the regime's narrative identity."""
        regime = Regime(
            name="Test Regime",
            latin="Regimen Testum",
            cosmology="test",
            version="1.0.0",
            philosophy="Test philosophy.",
            priorities={"test": 5},
            violations=[],
            health_model=type("HM", (), {"healthy": "ok", "stressed": "eh", "critical": "bad"})(),
            phaethon=type("P", (), {"risk": "test risk", "symptom": "test symptom", "corrective_regime": "other"})(),
            audit_rules=[],
            narrative=type("N", (), {"voice": "Test voice.", "aesthetic": "Test aesthetic.", "soundtrack": "Test soundtrack.", "character_archetype": "The Test Being"})(),
        )
        report = AuditReport("Test Regime", "test", "2026-01-01", [])
        md = render_report(regime, report)
        assert "Test Regime" in md
        assert "The Test Being" in md
        assert "test risk" in md

    def test_report_contains_findings(self):
        """Report should list all findings."""
        regime = Regime(
            name="Test", latin="T", cosmology="test", version="1.0.0",
            philosophy="P.", priorities={}, violations=[],
            health_model=type("H", (), {"healthy": "", "stressed": "", "critical": ""})(),
            phaethon=type("P", (), {"risk": "r", "symptom": "s", "corrective_regime": "c"})(),
            audit_rules=[],
            narrative=type("N", (), {"voice": "v.", "aesthetic": "a.", "soundtrack": "s.", "character_archetype": "c"})(),
        )
        findings = [
            Finding("check_a", "critical", "target/a", "Critical finding", "test"),
            Finding("check_b", "low", "target/b", "Low finding", "test"),
        ]
        report = AuditReport("Test", "test", "2026-01-01", findings)
        md = render_report(regime, report)
        assert "Critical finding" in md
        assert "Low finding" in md
        assert "CRITICAL" in md or "critical" in md.lower()

    def test_real_tolkien_report(self):
        """Real Tolkien report should render without errors."""
        if not REGIMES_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Regimes or registry not found")
        regimes = load_all_regimes(REGIMES_DIR)
        report = run_audit(regimes["tolkien"], REGISTRY_PATH)
        md = render_report(regimes["tolkien"], report)
        assert "Delegated Authority" in md
        assert len(md) > 100


class TestRenderDivergenceReport:
    def test_divergence_report_lists_regimes(self):
        """Divergence report should name the compared regimes."""
        if not REGIMES_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Regimes or registry not found")
        regimes = load_all_regimes(REGIMES_DIR)
        t_report = run_audit(regimes["tolkien"], REGISTRY_PATH)
        m_report = run_audit(regimes["malazan"], REGISTRY_PATH)
        div = analyze_divergence([t_report, m_report])
        md = render_divergence_report(div, regimes)
        assert "tolkien" in md
        assert "malazan" in md
        assert "Divergence" in md
