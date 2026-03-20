"""Phaethon detector — flags when a regime's declared blind spot is manifesting.

Every regime declares its own weakness (the phaethon field). This module
monitors audit findings against those declarations and raises warnings
when a regime's philosophy is producing the very harm it predicted.
"""

from __future__ import annotations

from dataclasses import dataclass

from .auditor import AuditReport
from .regime import Regime


@dataclass
class PhaethonWarning:
    """Warning that a regime's blind spot is manifesting."""

    regime: str
    risk: str
    symptom: str
    corrective_regime: str
    evidence: list[str]  # descriptions of findings that match the symptom
    severity: str  # warning | critical


# Keywords extracted from each regime's phaethon.symptom field
# These are matched against audit findings to detect manifestation
_SYMPTOM_KEYWORDS: dict[str, list[str]] = {
    "tolkien": [
        "stuck", "candidate forever", "frozen", "innovation starved",
        "standards so high", "nothing graduates", "rejected",
    ],
    "malazan": [
        "failure rates", "bug count", "technical debt", "accumulating",
        "confuses being stressed", "treated as healthy",
    ],
    "matrix": [
        "unable to evolve", "role definition forbids", "innovation killed",
        "nothing grows", "runs but",
    ],
    "lynch": [
        "no promotions", "every decision deferred", "complex",
        "meetings about meetings", "documents its own uncertainty",
    ],
    "zelda": [
        "left unaddressed", "come back anyway", "reactive-only",
        "no preventive", "known issues",
    ],
    "wot": [
        "either/or", "no room for ambiguity", "rigid",
        "insistence on balance", "paradoxically creates",
    ],
    "one-piece": [
        "many voices", "no coherence", "scattered",
        "no synthesis", "everyone has a piece",
    ],
    "lost": [
        "no clear success", "languish", "still evaluating",
        "permanent state", "nothing graduates",
    ],
    "jojo": [
        "flagship", "all attention", "star developer",
        "depends on one", "brilliant component",
    ],
}


def detect_phaethon(regime: Regime, report: AuditReport) -> PhaethonWarning | None:
    """Check if a regime's own blind spot is manifesting in its audit findings.

    Returns a PhaethonWarning if evidence is found, None otherwise.
    """
    keywords = _SYMPTOM_KEYWORDS.get(regime.cosmology, [])
    if not keywords:
        return None

    evidence = []
    for finding in report.findings:
        desc_lower = finding.description.lower()
        for keyword in keywords:
            if keyword.lower() in desc_lower:
                evidence.append(finding.description)
                break

    if not evidence:
        return None

    # Severity based on evidence count relative to total findings
    ratio = len(evidence) / max(len(report.findings), 1)
    severity = "critical" if ratio > 0.3 else "warning"

    return PhaethonWarning(
        regime=regime.cosmology,
        risk=regime.phaethon.risk.strip(),
        symptom=regime.phaethon.symptom.strip(),
        corrective_regime=regime.phaethon.corrective_regime,
        evidence=evidence,
        severity=severity,
    )
