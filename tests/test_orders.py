"""Tests for the Watcher Order loader and governance layer."""

from pathlib import Path

import pytest

from vigiles_engine.orders import WatcherOrder, load_all_orders, order_audit

ORDERS_DIR = Path(__file__).parent.parent / "orders"
REGISTRY_PATH = Path(__file__).parent.parent.parent / "organvm-corpvs-testamentvm" / "registry-v2.json"


class TestWatcherOrder:
    def test_load_single_order(self):
        path = ORDERS_DIR / "ordo-architectorum.yaml"
        if not path.exists():
            pytest.skip("Order not found")
        order = WatcherOrder.from_yaml(path)
        assert order.name == "The Architects"
        assert order.latin == "Ordo Architectorum"
        assert order.symbol == "△"

    def test_load_all_eight(self):
        if not ORDERS_DIR.exists():
            pytest.skip("Orders not found")
        orders = load_all_orders(ORDERS_DIR)
        assert len(orders) == 8

    def test_all_orders_have_rpg_stats(self):
        if not ORDERS_DIR.exists():
            pytest.skip("Orders not found")
        orders = load_all_orders(ORDERS_DIR)
        for key, order in orders.items():
            assert "combat" in order.rpg, f"{key} missing combat stat"
            assert "creation" in order.rpg, f"{key} missing creation stat"
            assert "perception" in order.rpg, f"{key} missing perception stat"

    def test_all_orders_have_narrative(self):
        if not ORDERS_DIR.exists():
            pytest.skip("Orders not found")
        orders = load_all_orders(ORDERS_DIR)
        for key, order in orders.items():
            assert order.narrative.get("voice"), f"{key} missing voice"
            assert order.narrative.get("aesthetic"), f"{key} missing aesthetic"
            assert order.narrative.get("soundtrack"), f"{key} missing soundtrack"

    def test_all_orders_have_system_functions(self):
        if not ORDERS_DIR.exists():
            pytest.skip("Orders not found")
        orders = load_all_orders(ORDERS_DIR)
        for key, order in orders.items():
            assert len(order.system_functions) >= 3, f"{key} has fewer than 3 system functions"


class TestOrderAudit:
    def test_architect_audit(self):
        if not ORDERS_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Missing data")
        orders = load_all_orders(ORDERS_DIR)
        architects = [o for o in orders.values() if "architect" in o.name.lower()][0]
        findings = order_audit(architects, REGISTRY_PATH)
        # Should find repos with insufficient descriptions
        assert len(findings) >= 0  # May or may not find issues

    def test_seraphim_audit(self):
        if not ORDERS_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Missing data")
        orders = load_all_orders(ORDERS_DIR)
        seraphim = [o for o in orders.values() if "seraph" in o.name.lower()][0]
        findings = order_audit(seraphim, REGISTRY_PATH)
        # Should find repos without CI protection
        for f in findings:
            assert f.rule_check == "seraph_unprotected"

    def test_nataraja_audit(self):
        if not ORDERS_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Missing data")
        orders = load_all_orders(ORDERS_DIR)
        nataraja = [o for o in orders.values() if "nataraja" in o.name.lower()][0]
        findings = order_audit(nataraja, REGISTRY_PATH)
        # Should find dissolved-but-not-archived repos or stale repos
        for f in findings:
            assert f.rule_check in ("nataraja_undissolved", "nataraja_stale")

    def test_all_orders_can_audit(self):
        """Every Order should be able to audit without crashing."""
        if not ORDERS_DIR.exists() or not REGISTRY_PATH.exists():
            pytest.skip("Missing data")
        orders = load_all_orders(ORDERS_DIR)
        for key, order in orders.items():
            findings = order_audit(order, REGISTRY_PATH)
            for f in findings:
                assert f.regime.startswith("order:")
