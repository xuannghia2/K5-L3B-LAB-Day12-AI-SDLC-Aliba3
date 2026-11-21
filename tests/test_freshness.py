"""Schema migration and freshness thresholds for Ticket-03."""

import copy
import json
from pathlib import Path
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.freshness import FreshnessLedger
from chonoi.ids import IdAllocator
from chonoi.inventory import read_inventory, validate_fresh_items, write_inventory
from helpers import Workdir


def tuning_p3():
    t = copy.deepcopy(load_contract()["tuning"])
    t["freshness"] = json.loads((Path(__file__).resolve().parents[1] / "data/freshness-p3.json").read_text())
    return t


class FreshnessUnits(unittest.TestCase):
    def test_schema_versions_are_selected_explicitly(self):
        with Workdir() as w:
            p = w.path("inventory.json")
            write_inventory(p, {"ca_loc": 1})
            self.assertEqual(read_inventory(p), {"ca_loc": 1})
            with self.assertRaises(BadInput):
                read_inventory(p, version="1.2")
            write_inventory(p, [{"id": "I10", "kind": "ca_loc", "fresh": 29.9999},
                                {"id": "I2", "kind": "ca_keo", "fresh": 100}], version="1.2")
            rows = read_inventory(p, version="1.2")
            self.assertEqual([i["id"] for i in rows], ["I2", "I10"])
            self.assertEqual(rows[1]["fresh"], 29.9999)
            with self.assertRaises(BadInput):
                read_inventory(p, version="1.1")

    def test_invalid_items_are_rejected(self):
        valid = {"id": "I1", "kind": "ca_linh", "fresh": 100}
        for bad in ({}, [valid, valid], [dict(valid, id="")], [dict(valid, kind="unknown")],
                    [dict(valid, fresh=True)], [dict(valid, fresh=float("nan"))],
                    [dict(valid, fresh=float("inf"))], [dict(valid, fresh=-1)],
                    [dict(valid, fresh=101)], [dict(valid, extra=0)], ["ca_linh"]):
            with self.subTest(bad=bad), self.assertRaises(BadInput):
                validate_fresh_items(bad)

    def test_30_crosses_once_in_id_order_and_already_spoiled_stays_silent(self):
        ledger = FreshnessLedger(tuning_p3(), IdAllocator())
        items = ledger.attach([{"id": "I10", "kind": "ca_linh", "fresh": 30},
                               {"id": "I2", "kind": "ca_loc", "fresh": 30},
                               {"id": "I1", "kind": "ca_loc", "fresh": 29.9999}])
        rows = ledger.decay(items, "hold")
        self.assertEqual([e[1]["item_id"] for e in rows], ["I2", "I10"])
        self.assertEqual(ledger.decay(items, "hold"), [])

    def test_exact_30_boundary_after_many_ticks(self):
        ledger = FreshnessLedger(tuning_p3(), IdAllocator())
        items = ledger.attach([{"id": "I1", "kind": "ca_linh", "fresh": 100}])
        for _ in range(8400):
            self.assertEqual(ledger.decay(items, "hold"), [])
        self.assertEqual(items[0]["fresh"], 30)
        self.assertFalse(ledger.spoiled(items[0]))
        self.assertEqual(len(ledger.decay(items, "hold")), 1)
        self.assertTrue(ledger.spoiled(items[0]))

    def test_roundtrip_to_quan_keeps_exact_grid_threshold(self):
        t = tuning_p3()
        ledger = FreshnessLedger(t, IdAllocator())
        items = ledger.attach([{"id": "I1", "kind": "ca_linh", "fresh": 100}])
        ledger.decay(items, "hold")
        with Workdir() as w:
            p = w.path("inventory.json")
            write_inventory(p, items, version="1.2")
            stock_ledger = FreshnessLedger(t, IdAllocator())
            stock = stock_ledger.attach(read_inventory(p, version="1.2"))
            self.assertEqual(stock[0]["fresh"], items[0]["fresh"])
            for _ in range(16798):
                self.assertEqual(stock_ledger.decay(stock, "stock"), [])
            self.assertEqual(stock[0]["fresh"], 30)
            self.assertEqual(len(stock_ledger.decay(stock, "stock")), 1)

    def test_ids_continue_after_removed_items_with_shared_allocator(self):
        ids = IdAllocator()
        a = FreshnessLedger(tuning_p3(), ids)
        a.attach([{"id": "I20", "kind": "ca_loc", "fresh": 100}])
        self.assertEqual(a.new("ca_keo")["id"], "I21")
        b = FreshnessLedger(tuning_p3(), ids)
        self.assertEqual(b.new("keo_neo")["id"], "I22")

    def test_invalid_write_does_not_replace_previous_inventory(self):
        with Workdir() as w:
            p = w.path("inventory.json")
            Path(p).write_text('previous')
            with self.assertRaises(BadInput):
                write_inventory(p, [{"id": "I1", "kind": "ca_linh", "fresh": 101}], version="1.2")
            self.assertEqual(Path(p).read_text(), 'previous')


if __name__ == "__main__":
    unittest.main()
