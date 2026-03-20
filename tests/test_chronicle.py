"""Tests for the Chronicle recorder."""

from pathlib import Path

import pytest

from vigiles_engine.auditor import AuditReport, Finding, run_audit
from vigiles_engine.chronicle import read_chronicle, record_cycle
from vigiles_engine.regime import Regime, load_all_regimes

REGIMES_DIR = Path(__file__).parent.parent / "regimes"
REGISTRY_PATH = Path(__file__).parent.parent.parent / "organvm-corpvs-testamentvm" / "registry-v2.json"


class TestRecordCycle:
    def test_creates_chronicle_file(self, tmp_path):
        """Recording a cycle should create a JSONL file."""
        report = AuditReport(
            regime_name="Test",
            regime_cosmology="test",
            timestamp="2026-03-20T00:00:00Z",
            findings=[
                Finding(
                    rule_check="test_check",
                    severity="high",
                    target="test/target",
                    description="A test finding",
                    regime="test",
                )
            ],
        )
        path = record_cycle(tmp_path, report, summoned_by="test")
        assert path.exists()
        assert path.suffix == ".jsonl"

    def test_appends_to_existing_chronicle(self, tmp_path):
        """Multiple cycles on same day should append to same file."""
        report = AuditReport(
            regime_name="Test",
            regime_cosmology="test",
            timestamp="2026-03-20T00:00:00Z",
            findings=[],
        )
        path1 = record_cycle(tmp_path, report, summoned_by="test")
        path2 = record_cycle(tmp_path, report, summoned_by="test")
        assert path1 == path2
        with open(path1) as f:
            lines = f.readlines()
        assert len(lines) == 2

    def test_cycle_ids_increment(self, tmp_path):
        """Each cycle should get an incrementing ID."""
        report = AuditReport(
            regime_name="Test",
            regime_cosmology="test",
            timestamp="2026-03-20T00:00:00Z",
            findings=[],
        )
        record_cycle(tmp_path, report)
        record_cycle(tmp_path, report)
        entries = read_chronicle(tmp_path)
        ids = [e["cycle_id"] for e in entries]
        assert ids[0].endswith("-001")
        assert ids[1].endswith("-002")

    def test_records_findings(self, tmp_path):
        """Chronicle entry should contain all findings."""
        findings = [
            Finding("check_a", "critical", "target/a", "Desc A", "test"),
            Finding("check_b", "low", "target/b", "Desc B", "test"),
        ]
        report = AuditReport(
            regime_name="Test",
            regime_cosmology="test",
            timestamp="2026-03-20T00:00:00Z",
            findings=findings,
        )
        record_cycle(tmp_path, report)
        entries = read_chronicle(tmp_path)
        assert len(entries) == 1
        assert entries[0]["findings_count"] == 2
        assert len(entries[0]["findings"]) == 2

    def test_real_regime_chronicle(self):
        """Chronicle should work with real regime audit data."""
        if not REGIMES_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Regimes or registry not found")
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            regimes = load_all_regimes(REGIMES_DIR)
            report = run_audit(regimes["tolkien"], REGISTRY_PATH)
            path = record_cycle(Path(tmp), report, summoned_by="test")
            entries = read_chronicle(Path(tmp))
            assert len(entries) == 1
            assert entries[0]["regime_summoned"] == "tolkien"
            assert entries[0]["findings_count"] > 0


class TestReadChronicle:
    def test_empty_dir_returns_empty(self, tmp_path):
        """Reading from empty directory should return empty list."""
        entries = read_chronicle(tmp_path)
        assert entries == []

    def test_date_filter(self, tmp_path):
        """Reading with date filter should only return matching entries."""
        report = AuditReport(
            regime_name="Test",
            regime_cosmology="test",
            timestamp="2026-03-20T00:00:00Z",
            findings=[],
        )
        record_cycle(tmp_path, report)
        # Should find entries for today
        import datetime
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        entries = read_chronicle(tmp_path, date=today)
        assert len(entries) >= 1
        # Should not find entries for a different date
        entries_none = read_chronicle(tmp_path, date="1999-01-01")
        assert len(entries_none) == 0
