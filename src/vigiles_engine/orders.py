"""Watcher Order loader and governance layer.

Loads Order YAMLs and provides Order-based audit perspectives.
Each Order can audit the system from its domain-specific viewpoint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .auditor import AuditReport, Finding, _iter_repos, _load_registry


@dataclass
class WatcherOrder:
    """A Watcher Order loaded from YAML."""

    number: str
    name: str
    latin: str
    symbol: str
    domain: str
    power: str
    constraint: str
    failure_mode: str
    system_functions: list[str]
    narrative: dict[str, str]
    rpg: dict[str, Any] = field(default_factory=dict)
    mythological_sources: list[dict] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> WatcherOrder:
        with open(path) as f:
            data = yaml.safe_load(f)
        o = data["order"]
        return cls(
            number=str(o["number"]),
            name=o["name"],
            latin=o["latin"],
            symbol=o["symbol"],
            domain=o["domain"],
            power=o["power"],
            constraint=o["constraint"],
            failure_mode=o["failure_mode"],
            system_functions=o.get("system_functions", []),
            narrative=o.get("narrative", {}),
            rpg=o.get("rpg", {}),
            mythological_sources=o.get("mythological_sources", []),
        )


def load_all_orders(orders_dir: Path) -> dict[str, WatcherOrder]:
    """Load all Order YAML files."""
    orders = {}
    for path in sorted(orders_dir.glob("ordo-*.yaml")):
        order = WatcherOrder.from_yaml(path)
        key = order.name.lower().replace(" ", "-").replace("the-", "")
        orders[key] = order
    return orders


def order_audit(
    order: WatcherOrder,
    registry_path: Path,
) -> list[Finding]:
    """Run an Order-specific audit against system state.

    Each Order sees the system through its domain lens:
    - Architects: schema/structure compliance
    - Oracles: pressure/trajectory
    - Seraphim: protection gaps
    - Psychopomps: transition readiness
    - Smiths: adversarial weaknesses
    - Witnesses: recording completeness
    - Cosmogonists: meta-coherence
    - Nataraja: things that should be dissolved
    """
    registry = _load_registry(registry_path)
    findings: list[Finding] = []

    order_key = order.name.lower()

    if "architect" in order_key:
        findings.extend(_audit_architects(registry))
    elif "oracle" in order_key:
        findings.extend(_audit_oracles(registry))
    elif "seraph" in order_key:
        findings.extend(_audit_seraphim(registry))
    elif "psychopomp" in order_key:
        findings.extend(_audit_psychopomps(registry))
    elif "smith" in order_key:
        findings.extend(_audit_smiths(registry))
    elif "witness" in order_key:
        findings.extend(_audit_witnesses(registry))
    elif "cosmogonist" in order_key:
        findings.extend(_audit_cosmogonists(registry))
    elif "nataraja" in order_key:
        findings.extend(_audit_nataraja(registry))

    for f in findings:
        f.regime = f"order:{order.latin}"

    return findings


def _audit_architects(registry: dict) -> list[Finding]:
    """Architects check: structural completeness."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") == "ARCHIVED":
            continue
        if not repo.get("description") or len(repo.get("description", "")) < 20:
            findings.append(Finding(
                "architect_schema", "high",
                f"{organ_key}/{repo['name']}",
                "Insufficient description — the blueprint is incomplete",
                "",
            ))
    return findings


def _audit_oracles(registry: dict) -> list[Finding]:
    """Oracles check: pressure trajectories."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") in ("LOCAL", "CANDIDATE"):
            if repo.get("implementation_status") == "ACTIVE":
                findings.append(Finding(
                    "oracle_pressure", "medium",
                    f"{organ_key}/{repo['name']}",
                    "Pressure building — active development without promotion path",
                    "",
                ))
    return findings


def _audit_seraphim(registry: dict) -> list[Finding]:
    """Seraphim check: protection gaps."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") in ("GRADUATED", "PUBLIC_PROCESS"):
            if not repo.get("ci_workflow"):
                findings.append(Finding(
                    "seraph_unprotected", "critical",
                    f"{organ_key}/{repo['name']}",
                    "No CI shield — this entity is unprotected",
                    "",
                ))
    return findings


def _audit_psychopomps(registry: dict) -> list[Finding]:
    """Psychopomps check: transition readiness."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        status = repo.get("promotion_status", "")
        if status == "CANDIDATE" and repo.get("implementation_status") == "ACTIVE":
            if repo.get("ci_workflow") and repo.get("platinum_status"):
                findings.append(Finding(
                    "psychopomp_ready", "low",
                    f"{organ_key}/{repo['name']}",
                    "Ready at the gate — meets promotion criteria but has not crossed",
                    "",
                ))
    return findings


def _audit_smiths(registry: dict) -> list[Finding]:
    """Smiths check: adversarial weaknesses."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") == "GRADUATED":
            deps = repo.get("dependencies", [])
            all_names = set()
            for _, r in _iter_repos(registry):
                all_names.add(r["name"])
            for dep in deps:
                if dep not in all_names:
                    findings.append(Finding(
                        "smith_phantom", "critical",
                        f"{organ_key}/{repo['name']}",
                        f"Phantom dependency '{dep}' — a lie in the contract",
                        "",
                    ))
    return findings


def _audit_witnesses(registry: dict) -> list[Finding]:
    """Witnesses check: recording completeness."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") != "ARCHIVED":
            if not repo.get("last_validated"):
                findings.append(Finding(
                    "witness_unrecorded", "medium",
                    f"{organ_key}/{repo['name']}",
                    "No last_validated timestamp — this entity has no witnessed record",
                    "",
                ))
    return findings


def _audit_cosmogonists(registry: dict) -> list[Finding]:
    """Cosmogonists check: meta-coherence."""
    findings = []
    # Check organ-level coherence
    for organ_key, organ_data in registry.get("organs", {}).items():
        repos = organ_data.get("repositories", [])
        active = [r for r in repos if r.get("promotion_status") != "ARCHIVED"]
        if len(active) == 0:
            findings.append(Finding(
                "cosmogonist_empty_organ", "high",
                organ_key,
                "Empty organ — no active entities. Does this organ still serve a purpose?",
                "",
            ))
    return findings


def _audit_nataraja(registry: dict) -> list[Finding]:
    """Nataraja check: things that should be dissolved."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") == "ARCHIVED":
            continue
        note = repo.get("note", "").lower()
        if "dissolved" in note or "deprecated" in note or "superseded" in note:
            if repo.get("promotion_status") != "ARCHIVED":
                findings.append(Finding(
                    "nataraja_undissolved", "high",
                    f"{organ_key}/{repo['name']}",
                    "Marked for dissolution but still active — the Tandava awaits",
                    "",
                ))
        # Flag repos with no activity and old validation
        last = repo.get("last_validated", "")
        if last and last < "2025-06-01":
            findings.append(Finding(
                "nataraja_stale", "medium",
                f"{organ_key}/{repo['name']}",
                f"Last validated {last} — over a year stale. Sacred archival may be needed.",
                "",
            ))
    return findings
