"""Tests for the Colosseum auditor."""

import json
from pathlib import Path

import pytest

from vigiles_engine.auditor import run_audit
from vigiles_engine.regime import Regime, load_all_regimes

REGIMES_DIR = Path(__file__).parent.parent / "regimes"
REGISTRY_PATH = Path(__file__).parent.parent.parent / "organvm-corpvs-testamentvm" / "registry-v2.json"


@pytest.fixture
def tolkien_regime():
    path = REGIMES_DIR / "tolkien--delegated-authority.yaml"
    if not path.exists():
        pytest.skip("Tolkien regime not found")
    return Regime.from_yaml(path)


@pytest.fixture
def malazan_regime():
    path = REGIMES_DIR / "malazan--pressure-ascendancy.yaml"
    if not path.exists():
        pytest.skip("Malazan regime not found")
    return Regime.from_yaml(path)


class TestRunAudit:
    def test_tolkien_audit_produces_findings(self, tolkien_regime):
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        report = run_audit(tolkien_regime, REGISTRY_PATH)
        assert report.regime_name == "Delegated Authority"
        assert report.regime_cosmology == "tolkien"
        assert report.timestamp
        # Should find SOMETHING in a 116-repo registry
        assert report.summary["total"] > 0

    def test_malazan_audit_produces_findings(self, malazan_regime):
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        report = run_audit(malazan_regime, REGISTRY_PATH)
        assert report.regime_name == "Pressure Ascendancy"
        assert report.summary["total"] > 0

    def test_tolkien_and_malazan_find_different_things(self, tolkien_regime, malazan_regime):
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        tolkien_report = run_audit(tolkien_regime, REGISTRY_PATH)
        malazan_report = run_audit(malazan_regime, REGISTRY_PATH)
        # They should produce different findings
        tolkien_checks = {f.rule_check for f in tolkien_report.findings}
        malazan_checks = {f.rule_check for f in malazan_report.findings}
        # At least some checks should be unique to each
        assert tolkien_checks != malazan_checks, "Regimes should see different things"

    def test_audit_handles_unknown_checks_gracefully(self, tolkien_regime):
        """If a regime has an audit rule we haven't implemented, it should not crash."""
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        # The audit should complete even if some checks are unimplemented
        report = run_audit(tolkien_regime, REGISTRY_PATH)
        unimplemented = [f for f in report.findings if "not yet implemented" in f.description]
        # Just verify it didn't crash — unimplemented checks are logged as low-severity findings
        for f in unimplemented:
            assert f.severity == "low"

    def test_all_nine_regimes_can_audit(self):
        if not REGIMES_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Regimes or registry not found")
        regimes = load_all_regimes(REGIMES_DIR)
        for cosmology, regime in regimes.items():
            report = run_audit(regime, REGISTRY_PATH)
            assert report.regime_cosmology == cosmology
            assert report.timestamp
