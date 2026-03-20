"""Divergence analyzer — compares findings across multiple regime audits.

Identifies consensus (all agree), perspective divergence (different
interpretation), priority conflicts (different severity), and
structural contradictions (mutually exclusive claims).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .auditor import AuditReport, Finding


@dataclass
class DivergenceResult:
    """Result of comparing two or more regime audit reports."""

    regimes_compared: list[str]
    consensus: list[ConsensusItem]
    perspective_divergences: list[PerspectiveDivergence]
    priority_conflicts: list[PriorityConflict]
    unique_findings: dict[str, list[Finding]]  # regime -> findings only it produced
    constitutional_candidates: list[ConsensusItem]


@dataclass
class ConsensusItem:
    """A finding where all regimes agree."""

    target: str
    description: str
    severity_ceiling: str  # highest severity any regime assigned
    regimes_agreeing: list[str]
    is_constitutional_candidate: bool = False


@dataclass
class PerspectiveDivergence:
    """Same target, different interpretation."""

    target: str
    interpretations: dict[str, str]  # regime -> its interpretation


@dataclass
class PriorityConflict:
    """Same target, same finding, different severity."""

    target: str
    description: str
    severities: dict[str, str]  # regime -> severity
    ceiling: str  # highest severity


def _severity_rank(s: str) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(s, 0)


def analyze_divergence(reports: list[AuditReport]) -> DivergenceResult:
    """Compare findings across multiple regime audit reports."""
    if len(reports) < 2:
        msg = "Need at least 2 reports to analyze divergence"
        raise ValueError(msg)

    regimes = [r.regime_cosmology for r in reports]

    # Group findings by target
    by_target: dict[str, dict[str, list[Finding]]] = {}
    for report in reports:
        for finding in report.findings:
            by_target.setdefault(finding.target, {})
            by_target[finding.target].setdefault(report.regime_cosmology, [])
            by_target[finding.target][report.regime_cosmology].append(finding)

    consensus_items: list[ConsensusItem] = []
    perspective_divs: list[PerspectiveDivergence] = []
    priority_conflicts: list[PriorityConflict] = []
    unique: dict[str, list[Finding]] = {r: [] for r in regimes}

    for target, regime_findings in by_target.items():
        regimes_that_found = set(regime_findings.keys())

        if regimes_that_found == set(regimes):
            # All regimes flagged this target — potential consensus
            descriptions = {}
            severities = {}
            for regime, findings in regime_findings.items():
                descriptions[regime] = findings[0].description
                severities[regime] = findings[0].severity

            # Check if descriptions are similar enough for consensus
            unique_descriptions = set(descriptions.values())
            if len(unique_descriptions) == 1:
                # True consensus — same finding, same description
                ceiling = max(severities.values(), key=_severity_rank)
                consensus_items.append(ConsensusItem(
                    target=target,
                    description=next(iter(unique_descriptions)),
                    severity_ceiling=ceiling,
                    regimes_agreeing=list(regimes),
                    is_constitutional_candidate=True,
                ))
            else:
                # Same target, different descriptions — perspective divergence
                unique_sevs = set(severities.values())
                if len(unique_sevs) > 1:
                    ceiling = max(severities.values(), key=_severity_rank)
                    priority_conflicts.append(PriorityConflict(
                        target=target,
                        description=f"Multiple interpretations of {target}",
                        severities=severities,
                        ceiling=ceiling,
                    ))
                else:
                    perspective_divs.append(PerspectiveDivergence(
                        target=target,
                        interpretations=descriptions,
                    ))
        else:
            # Only some regimes found this — unique findings
            for regime in regimes_that_found:
                if len(regimes_that_found) == 1:
                    unique[regime].extend(regime_findings[regime])

    return DivergenceResult(
        regimes_compared=regimes,
        consensus=consensus_items,
        perspective_divergences=perspective_divs,
        priority_conflicts=priority_conflicts,
        unique_findings=unique,
        constitutional_candidates=[c for c in consensus_items if c.is_constitutional_candidate],
    )
