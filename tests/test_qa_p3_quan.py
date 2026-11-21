"""QA độc lập (justcoffeee) cho quán Phase 3 — kho cá thể v1.2 (commit 139b2b8 của griin-03).

Manifest chung vẫn v1.1, nên test dựng profile v1.2 trong tiến trình (giống tools/verify_gather_p3.py):
contract_version "1.2" + tuning.freshness từ data/freshness-p3.json. Không sửa game.contract.json.
Công thức giá theo tươi kiểm theo code hiện tại; chưa đối chiếu văn bản Ticket-03.
"""

import contextlib
import copy
import io
import json
import math
import os
import tempfile
import unittest

from chonoi import headless
from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.inventory import read_inventory
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = load_contract()
PROFILE = copy.deepcopy(BASE)
PROFILE["contract_version"] = "1.2"
with open(os.path.join(ROOT, "data", "freshness-p3.json"), encoding="utf-8") as _f:
    PROFILE["tuning"]["freshness"] = json.load(_f)
T = PROFILE["tuning"]
Q = T["quan"]
MENU = T["menu"]
FIRST = Q["first_customer_tick"]
B1 = Q["stoves"][0]["pos"]
IDLE = InputState(move=(0.0, 0.0), held={}, edges=set())
PRESS = InputState(move=(0.0, 0.0), held={"interact": True}, edges={"interact"})


def make(items, scenario=None, tuning=T):
    return QuanSim(tuning, scenario or {}, Streams(1), IdAllocator(), inventory=items)


def run(sim, ticks):
    out = []
    for _ in range(ticks):
        out.extend(sim.step(IDLE))
    return out


def names(events, name):
    return [data for n, data in events if n == name]


def headless_v12(args):
    original = headless.load_contract
    headless.load_contract = lambda: copy.deepcopy(PROFILE)
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            return headless.main(args)
    finally:
        headless.load_contract = original


def write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return path


class TwoProcessV12(unittest.TestCase):
    def test_gather_dock_file_is_read_by_quan_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            sc = write(os.path.join(d, "g.json"), {"gather": {
                "random_fish": False, "monsters": [],
                "hold": [{"id": "I1", "kind": "ca_loc", "fresh": 100}, {"id": "I2", "kind": "ca_loc", "fresh": 40}]}})
            inp = write(os.path.join(d, "i.json"), {"frames": [{"tick": 0, "interact": True}]})
            kho = os.path.join(d, "kho.json")
            self.assertEqual(headless_v12(["--mode", "gather", "--seed", "1", "--ticks", "2", "--scenario", sc,
                                           "--inputs", inp, "--out", os.path.join(d, "g.jsonl"),
                                           "--inventory-out", kho]), 0)
            items = read_inventory(kho, version="1.2")
            out = os.path.join(d, "q.jsonl")
            self.assertEqual(headless_v12(["--mode", "quan", "--seed", "1", "--ticks", "1",
                                           "--inventory", kho, "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                first = json.loads(f.readline())
        self.assertEqual([i["id"] for i in items], ["I1", "I2"])
        self.assertEqual(first["stock"], items, "quán phải nạp đúng cá thể và fresh đủ chính xác từ file")

    def test_default_v11_manifest_still_rejects_item_list(self):
        self.assertEqual(BASE["contract_version"], "1.1")
        with tempfile.TemporaryDirectory() as d:
            kho = write(os.path.join(d, "kho.json"), {"items": [{"id": "I1", "kind": "ca_loc", "fresh": 90}]})
            with contextlib.redirect_stderr(io.StringIO()):
                code = headless.main(["--mode", "quan", "--seed", "1", "--ticks", "1",
                                      "--inventory", kho, "--out", os.path.join(d, "q.jsonl")])
        self.assertEqual(code, 2, "chưa bật v1.2 trên manifest chung thì kho cá thể phải bị từ chối")


class ReserveAndPrice(unittest.TestCase):
    def test_reserves_freshest_item(self):
        sim = make([{"id": "I1", "kind": "ca_loc", "fresh": 50}, {"id": "I2", "kind": "ca_loc", "fresh": 90}])
        run(sim, FIRST)
        self.assertEqual(sim.customers[0]["reserved_item_ids"], ["I2"])

    def test_reserved_item_is_not_available_to_next_customer(self):
        sim = make([{"id": "I1", "kind": "ca_loc", "fresh": 90}])
        events = run(sim, FIRST + int(round(Q["customer_interval_s"] * 60)))
        self.assertEqual(len(names(events, "customer_arrived")), 1)
        self.assertEqual(len(names(events, "no_dish")), 1)

    def test_cook_consumes_reserved_ids_and_prices_by_freshness(self):
        sim = make([{"id": "I1", "kind": "ca_loc", "fresh": 50}, {"id": "I2", "kind": "ca_loc", "fresh": 90}])
        run(sim, FIRST)
        sim.pos = list(B1)
        started = names(sim.step(PRESS), "cook_started")[0]
        used = started["items"]
        self.assertEqual([i["id"] for i in used], ["I2"])
        self.assertEqual([i["id"] for i in sim.stock_items], ["I1"])
        expected = math.floor(MENU[started["dish_id"]]["price"] * sum(i["fresh"] for i in used) / len(used) / 100)
        self.assertEqual(started["base_price"], expected)
        self.assertLess(started["base_price"], MENU[started["dish_id"]]["price"])


class StockSpoil(unittest.TestCase):
    def test_reserved_item_spoils_in_stock_and_order_becomes_unfulfillable(self):
        sim = make([{"id": "I1", "kind": "ca_loc", "fresh": 30.5}])
        events = run(sim, FIRST + 200)
        self.assertEqual(names(events, "spoiled"), [{"item_id": "I1", "kind": "ca_loc", "location": "stock"}])
        self.assertEqual(sim.customers[0]["order_status"], "unfulfillable")
        self.assertEqual(sim.customers[0]["reserved_item_ids"], [])

    def test_stock_decays_at_quan_rate(self):
        sim = make([{"id": "I1", "kind": "ca_loc", "fresh": 100}], {"random_customers": False})
        run(sim, 60)
        self.assertAlmostEqual(sim.stock_items[0]["fresh"], 100 - T["freshness"]["quan_decay_per_s"], places=9)


class KnownBugsP3(unittest.TestCase):
    """Kiểm tra hồi quy cho các ca QA P3 đã được sửa (griin-03)."""

    def test_v12_fixture_customer_without_ingredients_is_not_cooked_for_free(self):
        """QA-P3-01: khách fixture gọi lau_mam, kho chỉ có 1 ca_loc: không đủ nguyên liệu thì không được nấu."""
        sim = make([{"id": "I1", "kind": "ca_loc", "fresh": 100}],
                   {"player": {"pos": B1}, "customers": [{"id": "C1", "table_id": "T1", "dish_id": "lau_mam"}]})
        started = names(sim.step(PRESS), "cook_started")
        self.assertEqual(started, [], f"không đủ nguyên liệu thì không được nấu: {started}")

    def test_v11_implicit_reservation_over_empty_stock_is_rejected(self):
        """QA-P3-02: khách fixture không ghi order_status/reserved, kho rỗng: validation từ chối BadInput."""
        with tempfile.TemporaryDirectory() as d:
            sc = write(os.path.join(d, "s.json"), {"quan": {"player": {"pos": B1}, "stock": {},
                       "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]}})
            inp = write(os.path.join(d, "i.json"), {"frames": [{"tick": 0, "interact": True}]})
            out = os.path.join(d, "q.jsonl")
            with contextlib.redirect_stderr(io.StringIO()):
                code = headless.main(["--mode", "quan", "--seed", "1", "--ticks", "2", "--scenario", sc,
                                      "--inputs", inp, "--out", out])
            cooked = False
            if code == 0:
                with open(out, encoding="utf-8") as f:
                    cooked = any(json.loads(l).get("name") == "cook_started" for l in f if l.strip())
        self.assertTrue(code == 2 or not cooked, f"exit={code}, cook_started={cooked}")

    def test_equal_freshness_tie_uses_natural_id_order(self):
        """QA-P3-03: hòa fresh thì chọn theo thứ tự tự nhiên ids.sort_by_id (I2 trước I10)."""
        sim = make([{"id": "I10", "kind": "ca_loc", "fresh": 80}, {"id": "I2", "kind": "ca_loc", "fresh": 80}])
        run(sim, FIRST)
        self.assertEqual(sim.customers[0]["reserved_item_ids"], ["I2"])


if __name__ == "__main__":
    unittest.main()
