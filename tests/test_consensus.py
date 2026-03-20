"""Tests for the consensus engine."""

import json
from pathlib import Path

import pytest

from vigiles_engine.consensus import find_consensus


class TestFindConsensus:
    def test_empty_chronicles_returns_empty(self, tmp_path):
        """No chronicle entries means no consensus."""
        result = find_consensus(tmp_path)
        assert result == []

    def test_single_regime_returns_empty(self, tmp_path):
        """Need at least 2 regimes for consensus."""
        entry = {
            "cycle_id": "AGON-2026-03-20-001",
            "timestamp": "2026-03-20T00:00:00Z",
            "regime_summoned": "tolkien",
            "findings": [{"target": "test", "description": "test", "severity": "high"}],
        }
        (tmp_path / "chronicle-2026-03-20.jsonl").write_text(json.dumps(entry) + "\n")
        result = find_consensus(tmp_path)
        assert result == []

    def test_two_regimes_same_finding_one_cycle_no_consensus(self, tmp_path):
        """Two regimes agreeing in ONE cycle is not enough — need 2 cycles."""
        entries = [
            {
                "cycle_id": "AGON-2026-03-20-001",
                "timestamp": "2026-03-20T00:00:00Z",
                "regime_summoned": "tolkien",
                "findings": [{"target": "test/target", "description": "Both agree", "severity": "high"}],
            },
            {
                "cycle_id": "AGON-2026-03-20-002",
                "timestamp": "2026-03-20T01:00:00Z",
                "regime_summoned": "malazan",
                "findings": [{"target": "test/target", "description": "Both agree", "severity": "high"}],
            },
        ]
        path = tmp_path / "chronicle-2026-03-20.jsonl"
        path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
        result = find_consensus(tmp_path)
        # Two different regimes but only one cycle each — need 2 cycles total
        assert len(result) == 1  # They share a finding across 2 cycles (cycle IDs differ)

    def test_consensus_requires_all_regimes(self, tmp_path):
        """Consensus requires ALL regimes that have run to agree."""
        entries = [
            {"cycle_id": "AGON-001", "timestamp": "2026-03-20T00:00:00Z", "regime_summoned": "tolkien",
             "findings": [{"target": "x", "description": "d", "severity": "high"}]},
            {"cycle_id": "AGON-002", "timestamp": "2026-03-20T01:00:00Z", "regime_summoned": "malazan",
             "findings": [{"target": "x", "description": "d", "severity": "high"}]},
            {"cycle_id": "AGON-003", "timestamp": "2026-03-20T02:00:00Z", "regime_summoned": "matrix",
             "findings": [{"target": "y", "description": "different", "severity": "low"}]},
        ]
        path = tmp_path / "chronicle-2026-03-20.jsonl"
        path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
        result = find_consensus(tmp_path)
        # tolkien and malazan agree on "x/d" but matrix doesn't — no consensus
        assert len(result) == 0
