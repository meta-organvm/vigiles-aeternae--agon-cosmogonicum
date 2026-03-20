"""Regime loader and validator.

Loads regime YAML definitions and validates them against the regime schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AuditRule:
    """A single audit rule within a regime."""

    check: str
    description: str
    severity: str  # critical | high | medium | low

    def __post_init__(self) -> None:
        valid = {"critical", "high", "medium", "low"}
        if self.severity not in valid:
            msg = f"Invalid severity '{self.severity}', must be one of {valid}"
            raise ValueError(msg)


@dataclass
class Phaethon:
    """A regime's declared blind spot."""

    risk: str
    symptom: str
    corrective_regime: str


@dataclass
class HealthModel:
    """How a regime defines system health."""

    healthy: str
    stressed: str
    critical: str


@dataclass
class Narrative:
    """A regime's aesthetic and character identity."""

    voice: str
    aesthetic: str
    soundtrack: str
    character_archetype: str


@dataclass
class Regime:
    """A complete governance philosophy derived from a mythological cosmology."""

    name: str
    latin: str
    cosmology: str
    version: str
    philosophy: str
    priorities: dict[str, int]
    violations: list[dict[str, str]]
    health_model: HealthModel
    phaethon: Phaethon
    audit_rules: list[AuditRule]
    narrative: Narrative
    metalaws_acknowledged: list[str] = field(default_factory=list)
    changelog: list[dict[str, Any]] = field(default_factory=list)
    forbidden_fusions: list[str] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> Regime:
        """Load a regime from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        r = data["regime"]

        return cls(
            name=r["name"],
            latin=r["latin"],
            cosmology=r["cosmology"],
            version=r.get("version", "1.0.0"),
            philosophy=r["philosophy"],
            priorities=r["priorities"],
            violations=r["violations"],
            health_model=HealthModel(**r["health_model"]),
            phaethon=Phaethon(**r["phaethon"]),
            audit_rules=[AuditRule(**rule) for rule in r["audit_rules"]],
            narrative=Narrative(**r["narrative"]),
            metalaws_acknowledged=r.get("metalaws_acknowledged", []),
            changelog=r.get("changelog", []),
            forbidden_fusions=r.get("forbidden_fusions", []),
        )


def load_all_regimes(regimes_dir: Path) -> dict[str, Regime]:
    """Load all regime YAML files from a directory."""
    regimes = {}
    for path in sorted(regimes_dir.glob("*.yaml")):
        regime = Regime.from_yaml(path)
        regimes[regime.cosmology] = regime
    return regimes
