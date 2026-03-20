"""Consensus engine — identifies where ALL regimes agree.

Constitutional law candidates emerge when every regime that has run
confirms the same finding across at least two separate Agon cycles.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .chronicle import read_chronicle


@dataclass
class ConstitutionalCandidate:
    """A finding confirmed by all regimes — candidate for immutable law."""

    target: str
    description: str
    severity_ceiling: str
    regimes_confirming: list[str]
    cycles_confirmed: list[str]  # cycle_ids
    first_seen: str
    last_confirmed: str
    status: str = "candidate"  # candidate | enacted | rejected


def find_consensus(chronicles_dir: Path) -> list[ConstitutionalCandidate]:
    """Scan all chronicle entries for consensus across regimes.

    A finding becomes a Constitutional candidate when:
    - All regimes that have run agree on the same target+description
    - This agreement spans at least 2 separate Agon cycles
    """
    all_entries = read_chronicle(chronicles_dir)
    if not all_entries:
        return []

    # Collect all regimes that have ever run
    all_regimes = set()
    for entry in all_entries:
        all_regimes.add(entry["regime_summoned"])

    if len(all_regimes) < 2:
        return []  # Need at least 2 regimes for consensus

    # Group findings by (target, description) across all regimes
    finding_map: dict[tuple[str, str], dict] = {}
    for entry in all_entries:
        cycle_id = entry["cycle_id"]
        regime = entry["regime_summoned"]
        for f in entry.get("findings", []):
            key = (f["target"], f["description"])
            if key not in finding_map:
                finding_map[key] = {
                    "target": f["target"],
                    "description": f["description"],
                    "severity_max": f["severity"],
                    "regimes": set(),
                    "cycles": set(),
                    "first_seen": entry["timestamp"],
                    "last_seen": entry["timestamp"],
                }
            fm = finding_map[key]
            fm["regimes"].add(regime)
            fm["cycles"].add(cycle_id)
            fm["last_seen"] = entry["timestamp"]
            # Track highest severity
            sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            if sev_rank.get(f["severity"], 0) > sev_rank.get(fm["severity_max"], 0):
                fm["severity_max"] = f["severity"]

    # Find findings where ALL regimes agree
    candidates = []
    for key, fm in finding_map.items():
        if fm["regimes"] == all_regimes and len(fm["cycles"]) >= 2:
            candidates.append(ConstitutionalCandidate(
                target=fm["target"],
                description=fm["description"],
                severity_ceiling=fm["severity_max"],
                regimes_confirming=sorted(fm["regimes"]),
                cycles_confirmed=sorted(fm["cycles"]),
                first_seen=fm["first_seen"],
                last_confirmed=fm["last_seen"],
            ))

    return sorted(candidates, key=lambda c: c.first_seen)
