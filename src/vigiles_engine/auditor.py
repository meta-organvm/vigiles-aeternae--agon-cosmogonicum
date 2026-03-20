"""Colosseum auditor — applies regime audit rules against ORGANVM state.

Each audit rule's `check` field maps to a concrete check function that
reads system state (registry, seeds, metrics) and produces findings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .regime import AuditRule, Regime


@dataclass
class Finding:
    """A single audit finding produced by running a rule against system state."""

    rule_check: str
    severity: str
    target: str  # repo name, organ, or "system"
    description: str
    regime: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    """Complete audit report from one regime's Agon cycle."""

    regime_name: str
    regime_cosmology: str
    timestamp: str
    findings: list[Finding]
    summary: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.summary = {
            "critical": sum(1 for f in self.findings if f.severity == "critical"),
            "high": sum(1 for f in self.findings if f.severity == "high"),
            "medium": sum(1 for f in self.findings if f.severity == "medium"),
            "low": sum(1 for f in self.findings if f.severity == "low"),
            "total": len(self.findings),
        }


# ──────────────────────────────────────────────────────────────
# Check function registry — maps check IDs to implementations
# ──────────────────────────────────────────────────────────────

CHECK_REGISTRY: dict[str, Any] = {}


def register_check(check_id: str):
    """Decorator to register a check function."""
    def decorator(func):
        CHECK_REGISTRY[check_id] = func
        return func
    return decorator


# ──────────────────────────────────────────────────────────────
# Built-in checks (available to all regimes)
# ──────────────────────────────────────────────────────────────


def _load_registry(registry_path: Path) -> dict:
    """Load the ORGANVM registry."""
    with open(registry_path) as f:
        return json.load(f)


def _iter_repos(registry: dict):
    """Yield (organ_key, repo_dict) for all repos in registry."""
    for organ_key, organ_data in registry.get("organs", {}).items():
        for repo in organ_data.get("repositories", []):
            yield organ_key, repo


@register_check("seed_mandate_alignment")
def check_seed_mandate_alignment(
    rule: AuditRule, registry: dict, workspace: Path, **_kwargs
) -> list[Finding]:
    """Check if repos have seed.yaml files matching their registry declaration."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") == "ARCHIVED":
            continue
        # Check if seed.yaml exists in the workspace
        # This is a structural check — does the contract exist?
        repo_name = repo["name"]
        if repo.get("status") != "active":
            continue
        # For now, flag repos without implementation_status as potentially misaligned
        if not repo.get("implementation_status"):
            findings.append(Finding(
                rule_check=rule.check,
                severity=rule.severity,
                target=f"{organ_key}/{repo_name}",
                description=f"No implementation_status declared — mandate unclear",
                regime="",  # filled by caller
            ))
    return findings


@register_check("promotion_readiness_genuine")
def check_promotion_readiness(
    rule: AuditRule, registry: dict, **_kwargs
) -> list[Finding]:
    """Check for repos that may have been promoted without genuine readiness."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        status = repo.get("promotion_status", "")
        if status in ("GRADUATED", "PUBLIC_PROCESS"):
            # Graduated repos should have CI and platinum
            if not repo.get("ci_workflow"):
                findings.append(Finding(
                    rule_check=rule.check,
                    severity=rule.severity,
                    target=f"{organ_key}/{repo['name']}",
                    description=f"Status {status} but no CI workflow — promoted without verification?",
                    regime="",
                ))
            if status == "GRADUATED" and not repo.get("platinum_status"):
                findings.append(Finding(
                    rule_check=rule.check,
                    severity="medium",
                    target=f"{organ_key}/{repo['name']}",
                    description=f"GRADUATED without platinum_status — is this genuinely complete?",
                    regime="",
                ))
    return findings


@register_check("constraint_respect")
def check_constraint_respect(
    rule: AuditRule, registry: dict, **_kwargs
) -> list[Finding]:
    """Check if dependency constraints are being respected."""
    # Simplified: check for repos with dependencies on non-existent repos
    all_repo_names = set()
    for _, repo in _iter_repos(registry):
        all_repo_names.add(repo["name"])

    findings = []
    for organ_key, repo in _iter_repos(registry):
        for dep in repo.get("dependencies", []):
            if dep not in all_repo_names:
                findings.append(Finding(
                    rule_check=rule.check,
                    severity=rule.severity,
                    target=f"{organ_key}/{repo['name']}",
                    description=f"Dependency '{dep}' not found in registry — phantom dependency",
                    regime="",
                ))
    return findings


@register_check("stale_status_without_proof")
def check_stale_status(
    rule: AuditRule, registry: dict, **_kwargs
) -> list[Finding]:
    """Malazan check: do GRADUATED repos still demonstrate fitness?"""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") == "GRADUATED":
            last = repo.get("last_validated", "")
            if last and last < "2026-02-01":
                findings.append(Finding(
                    rule_check=rule.check,
                    severity=rule.severity,
                    target=f"{organ_key}/{repo['name']}",
                    description=f"GRADUATED but last validated {last} — coasting on past status?",
                    regime="",
                ))
    return findings


@register_check("pressure_accumulation_unresolved")
def check_pressure_accumulation(
    rule: AuditRule, registry: dict, **_kwargs
) -> list[Finding]:
    """Malazan check: repos with accumulating unresolved issues."""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") in ("LOCAL", "CANDIDATE"):
            if repo.get("implementation_status") == "ACTIVE":
                # Active but not promoted — pressure building
                note = repo.get("note", "")
                if "dissolved" not in note.lower() and "archived" not in note.lower():
                    findings.append(Finding(
                        rule_check=rule.check,
                        severity="medium",
                        target=f"{organ_key}/{repo['name']}",
                        description=f"Active at {repo['promotion_status']} — pressure accumulating without promotion path",
                        regime="",
                    ))
    return findings


@register_check("single_point_of_failure")
def check_single_point_of_failure(
    rule: AuditRule, registry: dict, **_kwargs
) -> list[Finding]:
    """Malazan check: disproportionate load on single components."""
    findings = []
    # Check for organs with only 1-2 active repos
    for organ_key, organ_data in registry.get("organs", {}).items():
        active = [
            r for r in organ_data.get("repositories", [])
            if r.get("promotion_status") not in ("ARCHIVED",) and r.get("status") == "active"
        ]
        if 0 < len(active) <= 2:
            findings.append(Finding(
                rule_check=rule.check,
                severity=rule.severity,
                target=organ_key,
                description=f"Only {len(active)} active repo(s) — single point of failure risk",
                regime="",
            ))
    return findings


# Generic checks available to all regimes
@register_check("role_definition_exists")
def check_role_definition(rule: AuditRule, registry: dict, **_kwargs) -> list[Finding]:
    """Matrix check: does every component have a clear function?"""
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") == "ARCHIVED":
            continue
        if not repo.get("description") or len(repo.get("description", "")) < 10:
            findings.append(Finding(
                rule_check=rule.check,
                severity=rule.severity,
                target=f"{organ_key}/{repo['name']}",
                description="No meaningful description — role undefined",
                regime="",
            ))
    return findings


@register_check("documentation_honesty")
def check_documentation_honesty(rule: AuditRule, registry: dict, **_kwargs) -> list[Finding]:
    """Lynch check: does documentation acknowledge unknowns?"""
    # Structural proxy: repos claiming GRADUATED without notes about limitations
    findings = []
    for organ_key, repo in _iter_repos(registry):
        if repo.get("promotion_status") == "GRADUATED" and not repo.get("note"):
            findings.append(Finding(
                rule_check=rule.check,
                severity=rule.severity,
                target=f"{organ_key}/{repo['name']}",
                description="GRADUATED with no notes — does documentation acknowledge limitations?",
                regime="",
            ))
    return findings


@register_check("knowledge_distribution")
def check_knowledge_distribution(rule: AuditRule, registry: dict, **_kwargs) -> list[Finding]:
    """One Piece check: is critical knowledge distributed, not centralized?"""
    findings = []
    # Check for organs where all repos depend on one single repo
    for organ_key, organ_data in registry.get("organs", {}).items():
        repos = organ_data.get("repositories", [])
        dep_counts: dict[str, int] = {}
        for repo in repos:
            for dep in repo.get("dependencies", []):
                dep_counts[dep] = dep_counts.get(dep, 0) + 1
        for dep_name, count in dep_counts.items():
            if count >= 5:
                findings.append(Finding(
                    rule_check=rule.check,
                    severity=rule.severity,
                    target=f"{organ_key}/{dep_name}",
                    description=f"Depended on by {count} repos — knowledge centralized here",
                    regime="",
                ))
    return findings


# ──────────────────────────────────────────────────────────────
# The Auditor — runs a regime's rules against system state
# ──────────────────────────────────────────────────────────────


def run_audit(
    regime: Regime,
    registry_path: Path,
    workspace: Path | None = None,
) -> AuditReport:
    """Run a regime's audit rules against ORGANVM system state."""
    registry = _load_registry(registry_path)
    all_findings: list[Finding] = []

    for rule in regime.audit_rules:
        check_fn = CHECK_REGISTRY.get(rule.check)
        if check_fn is None:
            # Unknown check — record as a finding itself
            all_findings.append(Finding(
                rule_check=rule.check,
                severity="low",
                target="system",
                description=f"Audit check '{rule.check}' not yet implemented",
                regime=regime.cosmology,
            ))
            continue

        findings = check_fn(
            rule=rule,
            registry=registry,
            workspace=workspace or Path.home() / "Workspace",
        )
        for f in findings:
            f.regime = regime.cosmology
        all_findings.extend(findings)

    return AuditReport(
        regime_name=regime.name,
        regime_cosmology=regime.cosmology,
        timestamp=datetime.now(timezone.utc).isoformat(),
        findings=all_findings,
    )
