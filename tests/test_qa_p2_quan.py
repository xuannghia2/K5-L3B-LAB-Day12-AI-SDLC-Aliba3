"""QA độc lập (justcoffeee) cho quán Phase 2 (Ticket-02): 2 bếp, 4 bàn, 6 món.

Kiểm sim/quan theo số chuẩn trong game.contract.json và thứ tự xử lý ghi ở docstring
chonoi/sim/quan.py (PRD-0 mục F). Bổ sung kiểm thử muộn sau mốc Phase 2, chạy trên code hiện tại.
"""

import contextlib
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
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim

TUNING = load_contract()["tuning"]
Q = TUNING["quan"]
MENU = TUNING["menu"]
FIRST = Q["first_customer_tick"]
INTERVAL = int(round(Q["customer_interval_s"] * 60))
IDLE = InputState(move=(0.0, 0.0), held={}, edges=set())
PRESS = InputState(move=(0.0, 0.0), held={"interact": True}, edges={"interact"})
PLENTY = {"ca_loc": 20, "ca_linh": 20, "bong_dien_dien": 20, "bong_sung": 20, "ca_keo": 20, "keo_neo": 20}


def make(stock=None, scenario=None, seed=1):
    return QuanSim(TUNING, scenario or {}, Streams(seed), IdAllocator(), inventory=stock)


def run(sim, ticks, inp=IDLE):
    out = []
    for _ in range(ticks):
        out.extend(sim.step(inp))
    return out


def names(events, name):
    return [data for n, data in events if n == name]


def stove(sim, ident):
    return next(s for s in sim.stoves if s["id"] == ident)


class Ticket02Layout(unittest.TestCase):
    def test_contract_has_two_stoves_four_tables_six_dishes(self):
        self.assertEqual([s["id"] for s in Q["stoves"]], ["B1", "B2"])
        self.assertEqual([t["id"] for t in Q["tables"]], ["T1", "T2", "T3", "T4"])
        self.assertEqual(len(MENU), 6)
        kinds = {k for dish in MENU.values() for k in dish["recipe"]}
        self.assertTrue({"ca_keo", "keo_neo"} <= kinds)

    def test_stoves_are_not_both_in_interact_range(self):
        # Nếu hai bếp cùng trong bán kính thì luật "gần nhất rồi id" mới quyết định; kiểm bố cục không chồng.
        b1, b2 = (s["pos"] for s in Q["stoves"])
        self.assertGreater(math.dist(b1, b2), Q["interact_radius"])


class CustomersAndTables(unittest.TestCase):
    def test_spawns_fill_tables_in_id_order(self):
        sim = make(dict(PLENTY))
        arrived = names(run(sim, FIRST + 3 * INTERVAL), "customer_arrived")
        self.assertEqual([a["table_id"] for a in arrived], ["T1", "T2", "T3", "T4"])

    def test_table_freed_by_patience_is_reused_same_tick(self):
        # Kiên nhẫn 60 s = 3600 tick = 4 lượt khách: khách T1 rời ở bước 3 rồi khách thứ 5 vào T1 ở bước 4.
        patience = int(round(Q["patience_s"] * 60))
        self.assertEqual(patience, 4 * INTERVAL)
        sim = make(dict(PLENTY))
        events = run(sim, FIRST + 4 * INTERVAL)
        self.assertEqual([e["table_id"] for e in names(events, "customer_left")], ["T1"])
        self.assertEqual(names(events, "customer_arrived")[-1]["table_id"], "T1")

    def test_full_tables_skip_turn_without_no_dish(self):
        eating = [{"id": f"C{i}", "table_id": f"T{i}", "dish_id": "ca_loc_nuong_trui", "eat_ticks_left": 10 ** 5}
                  for i in range(1, 5)]
        sim = make(scenario={"stock": dict(PLENTY), "customers": eating})
        events = run(sim, FIRST)
        self.assertEqual(names(events, "customer_arrived"), [])
        self.assertEqual(names(events, "no_dish"), [], "bàn đầy thì bỏ lượt, không phát no_dish")

    def test_reserved_stock_blocks_second_order(self):
        sim = make({"ca_loc": 1})
        events = run(sim, FIRST + INTERVAL)
        self.assertEqual([a["dish_id"] for a in names(events, "customer_arrived")], ["ca_loc_nuong_trui"])
        self.assertEqual(len(names(events, "no_dish")), 1, "nguyên liệu đã giữ cho khách 1 không được dùng lại")

    def test_each_dish_is_chosen_when_only_its_recipe_is_in_stock(self):
        for dish, spec in MENU.items():
            with self.subTest(dish=dish):
                sim = make(dict(spec["recipe"]))
                arrived = names(run(sim, FIRST), "customer_arrived")
                # Kho đúng công thức món này vẫn có thể nấu món khác dùng ít nguyên liệu hơn.
                cookable = [d for d, s in MENU.items()
                            if all(spec["recipe"].get(k, 0) >= q for k, q in s["recipe"].items())]
                self.assertEqual(len(arrived), 1)
                self.assertIn(arrived[0]["dish_id"], cookable)

    def test_lau_mam_needs_all_five_ingredients(self):
        recipe = dict(MENU["lau_mam"]["recipe"])
        for missing in recipe:
            with self.subTest(missing=missing):
                stock = {k: q for k, q in recipe.items() if k != missing}
                sim = make(stock)
                arrived = names(run(sim, FIRST), "customer_arrived")
                self.assertNotIn("lau_mam", [a["dish_id"] for a in arrived])


class TwoStoves(unittest.TestCase):
    def test_two_stoves_cook_oldest_orders_in_parallel(self):
        sim = make(dict(PLENTY))
        run(sim, FIRST + INTERVAL)  # khách T1 rồi T2
        self.assertEqual([c["table_id"] for c in sim.customers], ["T1", "T2"])
        sim.pos = list(stove(sim, "B1")["pos"])
        started = names(sim.step(PRESS), "cook_started")
        sim.pos = list(stove(sim, "B2")["pos"])
        started += names(sim.step(PRESS), "cook_started")
        self.assertEqual([(e["stove_id"], e["order_id"]) for e in started],
                         [("B1", sim.customers[0]["order_id"]), ("B2", sim.customers[1]["order_id"])])
        self.assertEqual({stove(sim, "B1")["state"], stove(sim, "B2")["state"]}, {"cooking"})

    def test_cook_consumes_exact_recipe_and_sets_price(self):
        sim = make(dict(MENU["lau_mam"]["recipe"]))
        run(sim, FIRST)
        dish = sim.customers[0]["dish_id"]
        before = dict(sim.stock)
        sim.pos = list(stove(sim, "B1")["pos"])
        started = names(sim.step(PRESS), "cook_started")[0]
        for k, q in MENU[dish]["recipe"].items():
            self.assertEqual(sim.stock.get(k, 0), before[k] - q)
        self.assertEqual(started["base_price"], MENU[dish]["price"])
        self.assertEqual(stove(sim, "B1")["cook_ticks_left"], int(round(MENU[dish]["cook_s"] * 60)))


class Payment(unittest.TestCase):
    def test_full_cycle_tip_is_floor_of_price_times_rate(self):
        sim = make(dict(MENU["lau_mam"]["recipe"]))
        run(sim, FIRST)
        cust = sim.customers[0]
        price = MENU[cust["dish_id"]]["price"]
        sim.pos = list(stove(sim, "B1")["pos"])
        sim.step(PRESS)
        run(sim, int(round(MENU[cust["dish_id"]]["cook_s"] * 60)))
        self.assertEqual(stove(sim, "B1")["state"], "ready")
        sim.step(PRESS)
        self.assertEqual(sim.hand["order_id"], cust["order_id"])
        table = next(t for t in Q["tables"] if t["id"] == cust["table_id"])
        sim.pos = list(table["pos"])
        served = names(sim.step(PRESS), "served")[0]
        self.assertEqual(served["tip"], math.floor(price * Q["tip_rate"]))
        paid = names(run(sim, int(round(Q["eat_s"] * 60))), "paid")
        self.assertEqual(len(paid), 1)
        self.assertEqual(paid[0]["amount"], price + served["tip"])
        self.assertEqual(sim.reputation, Q["reputation_initial"] + Q["tip_reputation"])


class FixtureCustomers(unittest.TestCase):
    def test_fixture_waiting_customer_can_be_cooked(self):
        """ĐÃ SỬA (QA-P2-01): khách nạp từ scenario được gán order_status='reserved' mặc định nên bếp idle nhận nấu.

        Tái hiện qua headless: scenario quan có customers=[{id C1, table T1, dish ca_loc_nuong_trui}],
        stock ca_loc 1, người chơi đứng ở B1 và nhấn interact -> có cook_started.
        """
        sim = make(scenario={"player": {"pos": Q["stoves"][0]["pos"]}, "stock": {"ca_loc": 1},
                             "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]})
        started = names(sim.step(PRESS), "cook_started")
        self.assertEqual([e["order_id"] for e in started], ["C1"])


def run_quan_headless(scenario, frames=(), ticks=1):
    """Chạy headless trong tiến trình (không cần python3 trên PATH); trả (mã thoát, tên sự kiện, có file output)."""
    with tempfile.TemporaryDirectory() as d:
        sc, inp, out = (os.path.join(d, n) for n in ("scenario.json", "inputs.json", "out.jsonl"))
        with open(sc, "w", encoding="utf-8") as f:
            json.dump({"quan": scenario}, f)
        with open(inp, "w", encoding="utf-8") as f:
            json.dump({"frames": list(frames)}, f)
        with contextlib.redirect_stderr(io.StringIO()):
            code = headless.main(["--mode", "quan", "--seed", "1", "--ticks", str(ticks),
                                  "--scenario", sc, "--inputs", inp, "--out", out])
        if not os.path.exists(out):
            return code, [], False
        with open(out, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        return code, [r["name"] for r in rows if r["type"] == "event"], True


class FixtureValidation(unittest.TestCase):
    """Ba lỗi fixture quán do review xuannghia2 tái hiện (docs/review/github-2026-11-21.md, mục 3, 4, 6).

    QA tái hiện độc lập qua headless; griin-03 sửa ở 139b2b8.
    Giờ là test hồi quy (đã bỏ expectedFailure).
    """

    def test_reserved_beyond_stock_is_rejected_or_not_cooked(self):
        """ĐÃ SỬA QA-P2-02: trước đây kho rỗng, khách fixture đã giữ 1 ca_loc, interact ở B1 vẫn cook_started (kho âm)."""
        scenario = {"player": {"pos": Q["stoves"][0]["pos"]}, "stock": {},
                    "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                   "order_status": "reserved", "reserved": {"ca_loc": 1}}]}
        code, events, _ = run_quan_headless(scenario, [{"tick": 0, "interact": True}], ticks=2)
        self.assertTrue(code == 2 or "cook_started" not in events,
                        f"fixture mâu thuẫn kho phải bị từ chối (exit 2) hoặc không được nấu; exit={code}, events={events}")

    def test_random_customers_false_disables_schedule(self):
        """ĐÃ SỬA QA-P2-03: trước đây random_customers:false vẫn sinh khách ở first_customer_tick."""
        code, events, _ = run_quan_headless({"random_customers": False, "stock": {"ca_loc": 1}},
                                            ticks=FIRST + INTERVAL)
        self.assertEqual(code, 0)
        self.assertNotIn("customer_arrived", events)
        self.assertNotIn("no_dish", events)

    def test_unknown_dish_in_fixture_exits_2(self):
        """ĐÃ SỬA QA-P2-04: trước đây khách fixture dish_id lạ được nhận, exit 0 và ghi output thay vì báo đầu vào sai."""
        code, _, wrote = run_quan_headless({"stock": {"ca_loc": 1},
                                            "customers": [{"id": "C1", "table_id": "T1", "dish_id": "unknown"}]},
                                           ticks=0)
        self.assertEqual(code, 2)
        self.assertFalse(wrote, "đầu vào sai phải báo trước khi ghi output")


if __name__ == "__main__":
    unittest.main()
