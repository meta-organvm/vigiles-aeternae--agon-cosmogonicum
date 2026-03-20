"""Chronicle recorder — append-only JSONL history of Agon cycles.

The Witnesses' function in code. Every cycle is immutably recorded.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .auditor import AuditReport
from .divergence import DivergenceResult


def record_cycle(
    chronicles_dir: Path,
    regime_report: AuditReport,
    divergence: DivergenceResult | None = None,
    summoned_by: str = "schedule",
) -> Path:
    """Record a complete Agon cycle to the Chronicle.

    Appends a JSONL entry to the chronicle file for the current date.
    Returns the path to the chronicle file.
    """
    chronicles_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    chronicle_path = chronicles_dir / f"chronicle-{today}.jsonl"

    entry = {
        "cycle_id": f"AGON-{today}-{_next_cycle_number(chronicle_path)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regime_summoned": regime_report.regime_cosmology,
        "regime_name": regime_report.regime_name,
        "summoned_by": summoned_by,
        "findings_summary": regime_report.summary,
        "findings_count": regime_report.summary["total"],
        "findings": [
            {
                "rule_check": f.rule_check,
                "severity": f.severity,
                "target": f.target,
                "description": f.description,
            }
            for f in regime_report.findings
        ],
    }

    if divergence:
        entry["divergence"] = {
            "regimes_compared": divergence.regimes_compared,
            "consensus_count": len(divergence.consensus),
            "constitutional_candidates": len(divergence.constitutional_candidates),
            "perspective_divergences": len(divergence.perspective_divergences),
            "priority_conflicts": len(divergence.priority_conflicts),
            "unique_findings": {
                k: len(v) for k, v in divergence.unique_findings.items()
            },
        }

    with open(chronicle_path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return chronicle_path


def _next_cycle_number(chronicle_path: Path) -> str:
    """Get the next cycle number for today's chronicle file."""
    if not chronicle_path.exists():
        return "001"
    with open(chronicle_path) as f:
        lines = f.readlines()
    return f"{len(lines) + 1:03d}"


def read_chronicle(chronicles_dir: Path, date: str | None = None) -> list[dict]:
    """Read chronicle entries. If date is None, reads all."""
    entries = []
    pattern = f"chronicle-{date}.jsonl" if date else "chronicle-*.jsonl"
    for path in sorted(chronicles_dir.glob(pattern)):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    return entries
