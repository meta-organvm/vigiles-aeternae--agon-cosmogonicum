"""Tests for regime loading and validation."""

from pathlib import Path

import pytest

from vigiles_engine.regime import AuditRule, Regime, load_all_regimes

REGIMES_DIR = Path(__file__).parent.parent / "regimes"


class TestAuditRule:
    def test_valid_severity(self):
        rule = AuditRule(check="test", description="test", severity="critical")
        assert rule.severity == "critical"

    def test_invalid_severity_raises(self):
        with pytest.raises(ValueError, match="Invalid severity"):
            AuditRule(check="test", description="test", severity="banana")


class TestRegimeFromYaml:
    def test_load_tolkien(self):
        path = REGIMES_DIR / "tolkien--delegated-authority.yaml"
        if not path.exists():
            pytest.skip("Tolkien regime not found")
        regime = Regime.from_yaml(path)
        assert regime.name == "Delegated Authority"
        assert regime.cosmology == "tolkien"
        assert regime.latin == "Regimen Auctoritatis Delegatae"
        assert len(regime.audit_rules) >= 4
        assert regime.phaethon.corrective_regime == "malazan"

    def test_load_malazan(self):
        path = REGIMES_DIR / "malazan--pressure-ascendancy.yaml"
        if not path.exists():
            pytest.skip("Malazan regime not found")
        regime = Regime.from_yaml(path)
        assert regime.name == "Pressure Ascendancy"
        assert regime.cosmology == "malazan"
        assert regime.phaethon.corrective_regime == "tolkien"

    def test_load_all_nine(self):
        if not REGIMES_DIR.exists():
            pytest.skip("Regimes directory not found")
        regimes = load_all_regimes(REGIMES_DIR)
        assert len(regimes) == 9
        expected = {"tolkien", "malazan", "matrix", "lynch", "zelda", "wot", "one-piece", "lost", "jojo"}
        assert set(regimes.keys()) == expected

    def test_all_regimes_have_phaethon(self):
        if not REGIMES_DIR.exists():
            pytest.skip("Regimes directory not found")
        regimes = load_all_regimes(REGIMES_DIR)
        for cosmology, regime in regimes.items():
            assert regime.phaethon.risk, f"{cosmology} missing phaethon.risk"
            assert regime.phaethon.corrective_regime, f"{cosmology} missing corrective_regime"

    def test_all_regimes_have_audit_rules(self):
        if not REGIMES_DIR.exists():
            pytest.skip("Regimes directory not found")
        regimes = load_all_regimes(REGIMES_DIR)
        for cosmology, regime in regimes.items():
            assert len(regime.audit_rules) >= 3, f"{cosmology} has fewer than 3 audit rules"

    def test_all_regimes_have_narrative(self):
        if not REGIMES_DIR.exists():
            pytest.skip("Regimes directory not found")
        regimes = load_all_regimes(REGIMES_DIR)
        for cosmology, regime in regimes.items():
            assert regime.narrative.voice, f"{cosmology} missing narrative.voice"
            assert regime.narrative.aesthetic, f"{cosmology} missing narrative.aesthetic"
            assert regime.narrative.soundtrack, f"{cosmology} missing narrative.soundtrack"

    def test_corrective_regimes_are_valid(self):
        """Every regime's corrective_regime must be another loaded regime."""
        if not REGIMES_DIR.exists():
            pytest.skip("Regimes directory not found")
        regimes = load_all_regimes(REGIMES_DIR)
        for cosmology, regime in regimes.items():
            corrective = regime.phaethon.corrective_regime
            assert corrective in regimes, (
                f"{cosmology}'s corrective_regime '{corrective}' not found in loaded regimes"
            )
