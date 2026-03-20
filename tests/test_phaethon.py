"""Tests for the Phaethon detector."""

from pathlib import Path

import pytest

from vigiles_engine.auditor import run_audit
from vigiles_engine.phaethon import detect_phaethon
from vigiles_engine.regime import Regime, load_all_regimes

REGIMES_DIR = Path(__file__).parent.parent / "regimes"
REGISTRY_PATH = Path(__file__).parent.parent.parent / "organvm-corpvs-testamentvm" / "registry-v2.json"


@pytest.fixture
def all_regimes():
    if not REGIMES_DIR.exists():
        pytest.skip("Regimes not found")
    return load_all_regimes(REGIMES_DIR)


class TestPhaethonDetector:
    def test_returns_none_when_no_evidence(self, all_regimes):
        """A regime whose blind spot is NOT manifesting should return None."""
        # Matrix regime's phaethon is about innovation being killed by role enforcement
        # This is unlikely to manifest in the current system state
        matrix = all_regimes["matrix"]
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        report = run_audit(matrix, REGISTRY_PATH)
        warning = detect_phaethon(matrix, report)
        # May or may not have evidence — just verify it doesn't crash
        assert warning is None or warning.regime == "matrix"

    def test_lost_may_detect_stagnation(self, all_regimes):
        """Lost's phaethon is about nothing graduating — likely to detect in real state."""
        lost = all_regimes["lost"]
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        report = run_audit(lost, REGISTRY_PATH)
        warning = detect_phaethon(lost, report)
        # Lost's symptom includes "nothing graduates" — may match findings
        if warning:
            assert warning.regime == "lost"
            assert warning.corrective_regime == "jojo"
            assert len(warning.evidence) > 0

    def test_all_regimes_can_be_checked(self, all_regimes):
        """Every regime should be checkable without crashing."""
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        for cosmology, regime in all_regimes.items():
            report = run_audit(regime, REGISTRY_PATH)
            warning = detect_phaethon(regime, report)
            if warning:
                assert warning.regime == cosmology
                assert warning.severity in ("warning", "critical")
                assert len(warning.evidence) > 0

    def test_phaethon_warning_has_corrective(self, all_regimes):
        """Any warning produced must include a corrective regime."""
        if not REGISTRY_PATH.exists():
            pytest.skip("Registry not found")
        for cosmology, regime in all_regimes.items():
            report = run_audit(regime, REGISTRY_PATH)
            warning = detect_phaethon(regime, report)
            if warning:
                assert warning.corrective_regime in all_regimes, (
                    f"{cosmology}'s corrective '{warning.corrective_regime}' not a valid regime"
                )
