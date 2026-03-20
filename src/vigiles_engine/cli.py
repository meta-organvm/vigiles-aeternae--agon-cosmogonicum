"""Vigiles Aeternae CLI — the Colosseum command interface.

Usage:
    vigiles colosseum run --regime <name>
    vigiles colosseum compare --regimes <a>,<b>[,c,...]
    vigiles colosseum consensus
    vigiles colosseum chronicle [--date YYYY-MM-DD]
    vigiles orders list
    vigiles orders show <order>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .auditor import run_audit
from .chronicle import read_chronicle, record_cycle
from .consensus import find_consensus
from .divergence import analyze_divergence
from .phaethon import detect_phaethon
from .regime import Regime, load_all_regimes
from .reporter import render_divergence_report, render_report


def _find_paths() -> tuple[Path, Path, Path]:
    """Find regimes dir, registry path, and chronicles dir."""
    # Try relative to this package (when installed in the repo)
    pkg_dir = Path(__file__).parent.parent.parent
    regimes_dir = pkg_dir / "regimes"
    chronicles_dir = pkg_dir / "chronicles"

    # Registry: try standard location
    registry_candidates = [
        Path.home() / "Workspace" / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json",
        pkg_dir.parent / "organvm-corpvs-testamentvm" / "registry-v2.json",
    ]
    registry_path = None
    for candidate in registry_candidates:
        if candidate.exists():
            registry_path = candidate
            break

    if not registry_path:
        print("ERROR: Cannot find registry-v2.json", file=sys.stderr)
        sys.exit(1)

    return regimes_dir, registry_path, chronicles_dir


def cmd_run(args: argparse.Namespace) -> None:
    """Run a single regime's audit."""
    regimes_dir, registry_path, chronicles_dir = _find_paths()
    regimes = load_all_regimes(regimes_dir)

    if args.regime not in regimes:
        print(f"ERROR: Unknown regime '{args.regime}'. Available: {', '.join(sorted(regimes.keys()))}")
        sys.exit(1)

    regime = regimes[args.regime]
    report = run_audit(regime, registry_path)

    # Record in chronicle
    chronicle_path = record_cycle(chronicles_dir, report, summoned_by="cli")

    # Check for Phaethon
    phaethon_warning = detect_phaethon(regime, report)

    if args.json:
        result = {
            "regime": report.regime_cosmology,
            "findings": report.summary,
            "chronicle": str(chronicle_path),
        }
        if phaethon_warning:
            result["phaethon"] = {
                "severity": phaethon_warning.severity,
                "risk": phaethon_warning.risk,
                "corrective": phaethon_warning.corrective_regime,
                "evidence_count": len(phaethon_warning.evidence),
            }
        print(json.dumps(result, indent=2))
    else:
        print(render_report(regime, report))
        if phaethon_warning:
            print(f"\n{'='*60}")
            print(f"PHAETHON WARNING [{phaethon_warning.severity.upper()}]")
            print(f"{'='*60}")
            print(f"This regime's declared blind spot is manifesting.")
            print(f"Risk: {phaethon_warning.risk[:200]}")
            print(f"Evidence: {len(phaethon_warning.evidence)} findings match the symptom pattern")
            print(f"Corrective: summon the {phaethon_warning.corrective_regime} regime")
            print(f"{'='*60}")
        print(f"\nChronicle recorded: {chronicle_path}")


def cmd_compare(args: argparse.Namespace) -> None:
    """Compare multiple regimes."""
    regimes_dir, registry_path, chronicles_dir = _find_paths()
    regimes = load_all_regimes(regimes_dir)

    regime_names = [r.strip() for r in args.regimes.split(",")]
    for name in regime_names:
        if name not in regimes:
            print(f"ERROR: Unknown regime '{name}'")
            sys.exit(1)

    reports = []
    for name in regime_names:
        regime = regimes[name]
        report = run_audit(regime, registry_path)
        record_cycle(chronicles_dir, report, summoned_by="cli")
        reports.append(report)

    divergence = analyze_divergence(reports)

    if args.json:
        print(json.dumps({
            "regimes": regime_names,
            "consensus": len(divergence.consensus),
            "constitutional_candidates": len(divergence.constitutional_candidates),
            "perspective_divergences": len(divergence.perspective_divergences),
            "unique_findings": {k: len(v) for k, v in divergence.unique_findings.items()},
        }, indent=2))
    else:
        print(render_divergence_report(divergence, regimes))


def cmd_consensus(args: argparse.Namespace) -> None:
    """Find constitutional candidates from chronicle history."""
    _, _, chronicles_dir = _find_paths()
    candidates = find_consensus(chronicles_dir)

    if not candidates:
        print("No constitutional candidates yet.")
        print("Run more regime audits to build chronicle history.")
        print("Consensus requires ALL regimes to agree across 2+ cycles.")
        return

    print(f"# Constitutional Law Candidates ({len(candidates)})\n")
    for c in candidates:
        print(f"## {c.target}")
        print(f"**{c.description}**")
        print(f"- Severity ceiling: {c.severity_ceiling}")
        print(f"- Confirmed by: {', '.join(c.regimes_confirming)}")
        print(f"- Cycles: {', '.join(c.cycles_confirmed)}")
        print(f"- First seen: {c.first_seen}")
        print()


def cmd_chronicle(args: argparse.Namespace) -> None:
    """View chronicle entries."""
    _, _, chronicles_dir = _find_paths()
    entries = read_chronicle(chronicles_dir, date=args.date)

    if not entries:
        print("No chronicle entries found.")
        return

    for entry in entries:
        regime = entry["regime_summoned"]
        findings = entry["findings_count"]
        ts = entry["timestamp"][:19]
        cycle = entry["cycle_id"]
        print(f"[{cycle}] {ts} | {regime}: {findings} findings")
        if args.verbose:
            for f in entry.get("findings", [])[:5]:
                print(f"  [{f['severity']}] {f['target']}: {f['description']}")
            if findings > 5:
                print(f"  ... and {findings - 5} more")


def cmd_orders_list(args: argparse.Namespace) -> None:
    """List all Watcher Orders."""
    orders_dir = Path(__file__).parent.parent.parent / "orders"
    for path in sorted(orders_dir.glob("ordo-*.yaml")):
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        order = data["order"]
        print(f"  {order['number']:>3}. {order['name']:<35} {order['symbol']}  {order['domain'][:60]}")


def cmd_orders_show(args: argparse.Namespace) -> None:
    """Show details of a specific Order."""
    import yaml
    orders_dir = Path(__file__).parent.parent.parent / "orders"
    for path in sorted(orders_dir.glob("ordo-*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        order = data["order"]
        if args.order.lower() in order["name"].lower() or args.order.lower() in order["latin"].lower():
            print(f"# {order['name']} — {order['latin']}  {order['symbol']}")
            print(f"\n**Domain:** {order['domain']}")
            print(f"\n**Power:** {order['power']}")
            print(f"\n**Constraint:** {order['constraint']}")
            print(f"\n**Failure Mode:** {order['failure_mode']}")
            print(f"\n**RPG Class:** {order['rpg']['class']} — {order['rpg']['description']}")
            print(f"\n**System Functions:**")
            for fn in order["system_functions"]:
                print(f"  - {fn}")
            print(f"\n**Voice:** {order['narrative']['voice']}")
            print(f"**Aesthetic:** {order['narrative']['aesthetic']}")
            return
    print(f"Order '{args.order}' not found.")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vigiles",
        description="Vigiles Aeternae — The Cosmogonic Contest",
    )
    subparsers = parser.add_subparsers(dest="command")

    # colosseum subcommand
    colosseum = subparsers.add_parser("colosseum", help="The Agon arena")
    col_sub = colosseum.add_subparsers(dest="colosseum_cmd")

    run_p = col_sub.add_parser("run", help="Run a single regime audit")
    run_p.add_argument("--regime", required=True)
    run_p.add_argument("--json", action="store_true")

    compare_p = col_sub.add_parser("compare", help="Compare multiple regimes")
    compare_p.add_argument("--regimes", required=True, help="Comma-separated regime names")
    compare_p.add_argument("--json", action="store_true")

    col_sub.add_parser("consensus", help="Find constitutional candidates")

    chron_p = col_sub.add_parser("chronicle", help="View chronicle")
    chron_p.add_argument("--date", default=None)
    chron_p.add_argument("-v", "--verbose", action="store_true")

    # orders subcommand
    orders = subparsers.add_parser("orders", help="Watcher Orders")
    ord_sub = orders.add_subparsers(dest="orders_cmd")
    ord_sub.add_parser("list", help="List all Orders")
    show_p = ord_sub.add_parser("show", help="Show Order details")
    show_p.add_argument("order")

    args = parser.parse_args()

    if args.command == "colosseum":
        if args.colosseum_cmd == "run":
            cmd_run(args)
        elif args.colosseum_cmd == "compare":
            cmd_compare(args)
        elif args.colosseum_cmd == "consensus":
            cmd_consensus(args)
        elif args.colosseum_cmd == "chronicle":
            cmd_chronicle(args)
        else:
            colosseum.print_help()
    elif args.command == "orders":
        if args.orders_cmd == "list":
            cmd_orders_list(args)
        elif args.orders_cmd == "show":
            cmd_orders_show(args)
        else:
            orders.print_help()
    else:
        parser.print_help()
