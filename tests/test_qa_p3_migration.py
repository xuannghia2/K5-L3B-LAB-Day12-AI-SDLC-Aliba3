"""QA độc lập (justcoffeee) cho migration kho cá thể v1.2 — Ticket-03 / ADR-0001.

Kiểm trực tiếp adapter (inventory.py) và FreshnessLedger (freshness.py) với số liệu
data/freshness-p3.json, không phụ thuộc gather/quan và không cần python3 trên PATH.
"""

import json
import math
import os
import tempfile
import unittest

from chonoi.errors import BadInput
from chonoi.freshness import FreshnessLedger
from chonoi.ids import IdAllocator
from chonoi.inventory import read_inventory, validate_items, write_inventory

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "data", "freshness-p3.json"), encoding="utf-8") as _f:
    TUNING = {"freshness": json.load(_f)}

# 100 -> 30 là giảm 70. Ở 60 tick/s: giỏ 0.5/s => 70 / (0.5/60) = 8400 tick; kho 0.25/s => 16800 tick.
HOLD_TICKS_TO_30 = 8400
STOCK_TICKS_TO_30 = 16800


def _ledger():
    return FreshnessLedger(TUNING, IdAllocator())


def _decay_until_spoiled(ledger, items, location, limit):
    """Trả về (tick đầu tiên có sự kiện spoiled, tổng số sự kiện spoiled trong limit tick)."""
    first, count = None, 0
    for tick in range(1, limit + 1):
        events = ledger.decay(items, location)
        count += len(events)
        if events and first is None:
            first = tick
    return first, count


class Threshold30(unittest.TestCase):
    def test_hold_reaches_exactly_30_without_spoiling(self):
        ledger = _ledger()
        items = [ledger.new("ca_loc")]
        for _ in range(HOLD_TICKS_TO_30):
            self.assertEqual(ledger.decay(items, "hold"), [])
        self.assertEqual(items[0]["fresh"], 30.0)
        self.assertFalse(ledger.spoiled(items[0]), "fresh == 30 chưa được tính là ươn (spoiled_below)")

    def test_hold_spoils_on_next_tick_exactly_once(self):
        ledger = _ledger()
        items = [ledger.new("ca_loc")]
        first, count = _decay_until_spoiled(ledger, items, "hold", HOLD_TICKS_TO_30 + 500)
        self.assertEqual(first, HOLD_TICKS_TO_30 + 1)
        self.assertEqual(count, 1, "spoiled chỉ phát một lần cho mỗi id")
        self.assertTrue(ledger.spoiled(items[0]))

    def test_stock_decays_at_half_the_hold_rate(self):
        ledger = _ledger()
        items = [ledger.new("ca_linh")]
        first, count = _decay_until_spoiled(ledger, items, "stock", STOCK_TICKS_TO_30 + 10)
        self.assertEqual((first, count), (STOCK_TICKS_TO_30 + 1, 1))

    def test_fresh_floors_at_zero(self):
        ledger = _ledger()
        items = [ledger.new("ca_keo", fresh=0.001)]
        ledger.decay(items, "hold")
        self.assertEqual(items[0]["fresh"], 0.0)


class RoundtripHandoff(unittest.TestCase):
    def test_file_roundtrip_keeps_spoil_tick(self):
        """Ghi kho giữa chừng rồi đọc lại vào ledger mới: tick ươn không bị lệch do làm tròn."""
        for cut in (1, 777, 1234, HOLD_TICKS_TO_30 - 1, HOLD_TICKS_TO_30):
            with self.subTest(cut=cut):
                ledger = _ledger()
                items = [ledger.new("bong_sung")]
                for _ in range(cut):
                    ledger.decay(items, "hold")
                with tempfile.TemporaryDirectory() as d:
                    path = os.path.join(d, "kho.json")
                    write_inventory(path, items, version="1.2")
                    loaded = read_inventory(path, version="1.2")
                fresh_ledger = _ledger()
                loaded = fresh_ledger.attach(loaded)
                first, count = _decay_until_spoiled(fresh_ledger, loaded, "hold", HOLD_TICKS_TO_30)
                self.assertEqual(cut + first, HOLD_TICKS_TO_30 + 1)
                self.assertEqual(count, 1)

    def test_write_sorts_by_id_and_keeps_full_precision(self):
        items = [{"id": "I10", "kind": "ca_keo", "fresh": 100},
                 {"id": "I2", "kind": "keo_neo", "fresh": 29.9999}]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "kho.json")
            write_inventory(path, items, version="1.2")
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
        self.assertEqual([x["id"] for x in raw["items"]], ["I2", "I10"])
        self.assertEqual(raw["items"][0]["fresh"], 29.9999, "fresh không được làm tròn 3 chữ số")


class SchemaV12(unittest.TestCase):
    GOOD = {"id": "I1", "kind": "ca_loc", "fresh": 50}

    def _bad(self, items):
        with self.assertRaises(BadInput):
            validate_items(items, version="1.2")

    def test_accepts_valid_items_and_bounds(self):
        items = [self.GOOD, {"id": "I2", "kind": "ca_keo", "fresh": 0},
                 {"id": "I3", "kind": "keo_neo", "fresh": 100}]
        self.assertEqual(validate_items(items, version="1.2"), items)
        self.assertEqual(validate_items([], version="1.2"), [])

    def test_rejects_count_inventory(self):
        self._bad({"ca_loc": 2})

    def test_rejects_bad_items(self):
        cases = {
            "id trùng": [self.GOOD, dict(self.GOOD)],
            "thiếu fresh": [{"id": "I1", "kind": "ca_loc"}],
            "thừa khóa": [{**self.GOOD, "qty": 1}],
            "id rỗng": [{**self.GOOD, "id": ""}],
            "id không phải chuỗi": [{**self.GOOD, "id": 1}],
            "kind lạ": [{**self.GOOD, "kind": "ca_map"}],
            "fresh âm": [{**self.GOOD, "fresh": -0.001}],
            "fresh > 100": [{**self.GOOD, "fresh": 100.5}],
            "fresh NaN": [{**self.GOOD, "fresh": math.nan}],
            "fresh vô cực": [{**self.GOOD, "fresh": math.inf}],
            "fresh bool": [{**self.GOOD, "fresh": True}],
            "fresh chuỗi": [{**self.GOOD, "fresh": "50"}],
            "cá thể không phải object": ["ca_loc"],
        }
        for label, items in cases.items():
            with self.subTest(label):
                self._bad(items)

    def test_file_root_must_only_have_items(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "kho.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"items": [self.GOOD], "version": "1.2"}, f)
            with self.assertRaises(BadInput):
                read_inventory(path, version="1.2")

    def test_v11_path_still_uses_counts(self):
        self.assertEqual(validate_items({"ca_loc": 2, "ca_linh": 0}), {"ca_loc": 2})
        with self.assertRaises(BadInput):
            validate_items([self.GOOD])


class IdContinuity(unittest.TestCase):
    def test_new_ids_continue_after_loaded_items(self):
        ledger = _ledger()
        ledger.attach([{"id": "I7", "kind": "ca_loc", "fresh": 80},
                       {"id": "I2", "kind": "ca_linh", "fresh": 40}])
        self.assertEqual([ledger.new("ca_keo")["id"] for _ in range(2)], ["I8", "I9"])


if __name__ == "__main__":
    unittest.main()
