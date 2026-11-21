"""Unit tests cho Quán Ăn Chợ Nổi (sim/quan)."""

import math
import os
import unittest

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim


def make_quan(scenario=None, inventory=None, seed=42):
    tuning = load_contract()["tuning"]
    return QuanSim(
        tuning=tuning,
        scenario=scenario or {},
        streams=Streams(seed),
        ids=IdAllocator(),
        inventory=inventory,
    )


def make_input(move=(0.0, 0.0), interact=False, catch=False):
    edges = set()
    if interact:
        edges.add("interact")
    if catch:
        edges.add("catch")
    held = {"interact": interact, "catch": catch}
    return InputState(move=move, held=held, edges=edges)


class QuanSimTest(unittest.TestCase):
    def test_quan_init_defaults(self):
        sim = make_quan(inventory={"ca_loc": 2})
        self.assertEqual(sim.mode, "quan")
        self.assertEqual(sim.stock, {"ca_loc": 2})
        self.assertEqual(sim.pos, [8, 5])
        self.assertEqual(sim.reputation, 3.0)
        self.assertEqual(len(sim.stoves), 2)  # Ticket-02 standard data
        self.assertEqual(len(sim.tables), 4)  # Ticket-02 standard data

    def test_customer_spawn_and_no_dish(self):
        # Không có nguyên liệu -> tại tick 120 (first_customer_tick) sẽ phát no_dish
        sim = make_quan(inventory={})
        empty_input = make_input()
        events_all = []
        for _ in range(120):
            events_all.extend(sim.step(empty_input))
        
        no_dish_ev = [e for e in events_all if e[0] == "no_dish"]
        self.assertEqual(len(no_dish_ev), 1)
        self.assertEqual(no_dish_ev[0][1], {})

    def test_customer_arrived_and_reserved(self):
        # Có nguyên liệu -> tại tick 120 sinh khách, bàn T1 có khách, nguyên liệu bị reserved
        sim = make_quan(inventory={"ca_loc": 2})
        empty_input = make_input()
        events_all = []
        for _ in range(120):
            events_all.extend(sim.step(empty_input))

        arrived = [e for e in events_all if e[0] == "customer_arrived"]
        self.assertEqual(len(arrived), 1)
        cust = arrived[0][1]
        self.assertEqual(cust["table_id"], "T1")
        self.assertEqual(cust["dish_id"], "ca_loc_nuong_trui")
        self.assertEqual(cust["order_id"], "C1")
        self.assertEqual(len(sim.customers), 1)
        self.assertEqual(sim.customers[0]["state"], "waiting")
        self.assertEqual(sim.customers[0]["reserved"], {"ca_loc": 1})

    def test_full_cooking_serving_eating_cycle(self):
        # Ticket-02 has more tables: use stock for exactly one order to keep this a single-order cycle.
        sim = make_quan(inventory={"ca_loc": 1})
        empty_input = make_input()
        for _ in range(120):
            sim.step(empty_input)
        self.assertEqual(len(sim.customers), 1)
        
        # 2. Đặt người chơi gần bếp B1 [2, 8] và tương tác
        sim.pos = [2.0, 7.5]
        interact_input = make_input(interact=True)
        ev = sim.step(interact_input)
        cook_ev = [e for e in ev if e[0] == "cook_started"]
        self.assertEqual(len(cook_ev), 1)
        self.assertEqual(cook_ev[0][1]["order_id"], "C1")
        self.assertEqual(cook_ev[0][1]["items"], ["ca_loc"])
        self.assertEqual(sim.stoves[0]["state"], "cooking")
        self.assertEqual(sim.stock["ca_loc"], 0)  # Đã trừ 1 nguyên liệu khỏi kho

        # 3. Chờ nấu xong (ca_loc_nuong_trui nấu trong 6s = 360 ticks)
        for _ in range(360):
            ev = sim.step(empty_input)
            if any(e[0] == "dish_ready" for e in ev):
                break
        self.assertEqual(sim.stoves[0]["state"], "ready")

        # 4. Bốc món lên tay
        ev = sim.step(interact_input)
        self.assertIn("dish_picked", [e[0] for e in ev])
        self.assertIsInstance(sim.hand, dict)
        self.assertEqual(sim.hand["dish_id"], "ca_loc_nuong_trui")
        self.assertEqual(sim.stoves[0]["state"], "idle")

        # 5. Đi đến bàn T1 [9, 2] và phục vụ
        sim.pos = [9.0, 2.5]
        ev = sim.step(interact_input)
        self.assertIn("served", [e[0] for e in ev])
        self.assertIsNone(sim.hand)
        self.assertEqual(sim.customers[0]["state"], "eating")
        self.assertGreater(sim.customers[0]["tip"], 0)  # Phục vụ nhanh nên có tip

        # 6. Khách ăn xong (eat_s = 10s = 600 ticks)
        paid_ev = []
        for _ in range(600):
            ev = sim.step(empty_input)
            paid_ev.extend([e for e in ev if e[0] == "paid"])
        self.assertEqual(len(paid_ev), 1)
        self.assertEqual(paid_ev[0][1]["order_id"], "C1")
        self.assertGreater(sim.money, 60)
        self.assertGreater(sim.reputation, 3.0)
        self.assertEqual(len(sim.customers), 0)

    def test_phase2_six_dishes_and_new_ingredients(self):
        # Kiểm tra 6 món và nguyên liệu mới (ca_keo, keo_neo) theo Ticket-02
        tuning = load_contract()["tuning"]
        menu = tuning["menu"]
        self.assertEqual(len(menu), 6)
        self.assertIn("canh_chua_ca_loc", menu)
        self.assertIn("ca_keo_nuong", menu)
        self.assertIn("lau_mam", menu)

        # Thử nấu món lẩu mắm cần cả 4 loại nguyên liệu
        sim = make_quan(inventory={"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1})
        empty_input = make_input()
        for _ in range(120):
            sim.step(empty_input)
        self.assertEqual(len(sim.customers), 1)
        cust = sim.customers[0]
        self.assertEqual(cust["dish_id"], "lau_mam")
        self.assertEqual(cust["reserved"], {"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1})

    def test_phase2_multi_stoves_and_tables(self):
        # Kiểm tra 2 bếp B1, B2 và 4 bàn T1-T4
        sim = make_quan(inventory={"ca_loc": 5})
        self.assertEqual([s["id"] for s in sim.stoves], ["B1", "B2"])
        self.assertEqual([t["id"] for t in sim.tables], ["T1", "T2", "T3", "T4"])

    def test_phase3_freshness_decay_and_spoil_re_reserve(self):
        # Kiểm tra hao tươi, biến cố spoiled và re-reserve hoặc unfulfillable trong Quan
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        tuning = load_contract()["tuning"]
        tuning["freshness"] = json.loads((root / "data" / "freshness-p3.json").read_text())

        # Tạo kho với 1 cá lóc sắp ươn (fresh = 30.0) và 1 cá lóc tươi (fresh = 100.0)
        items = [
            {"id": "I1", "kind": "ca_loc", "fresh": 30.0},
            {"id": "I2", "kind": "ca_loc", "fresh": 100.0}
        ]
        # Khách C1 giữ I2 (tươi nhất), khách C2 giữ I1 (sắp ươn)
        scenario = {
            "random_customers": False,
            "customers": [
                {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "order_status": "reserved", "reserved_item_ids": ["I2"]},
                {"id": "C2", "table_id": "T2", "dish_id": "ca_loc_nuong_trui", "order_status": "reserved", "reserved_item_ids": ["I1"]}
            ]
        }
        sim = QuanSim(tuning=tuning, scenario=scenario, streams=Streams(1), ids=IdAllocator(), inventory=items)
        # Tick 1: I1 giảm từ 30.0 xuống < 30.0 -> phát spoiled, C2 nhả I1 và thử re-reserve nhưng hết cá lóc -> unfulfillable
        events = sim.step(make_input())
        spoiled_ev = [e for e in events if e[0] == "spoiled"]
        self.assertEqual(len(spoiled_ev), 1)
        self.assertEqual(spoiled_ev[0][1]["item_id"], "I1")
        self.assertEqual(spoiled_ev[0][1]["location"], "stock")
        c2 = next(c for c in sim.customers if c["id"] == "C2")
        self.assertEqual(c2["order_status"], "unfulfillable")

    def test_phase3_pricing_by_freshness(self):
        # Giá niêm yết của ca_loc_nuong_trui là 60.
        # Ở tick 1, cá thể I1 (ban đầu 80.0) bị hao 0.25/60 còn ~79.995833...
        # base_price = floor(60 * 79.995833 / 100) = floor(47.9975) = 47.
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        tuning = load_contract()["tuning"]
        tuning["freshness"] = json.loads((root / "data" / "freshness-p3.json").read_text())

        items = [{"id": "I1", "kind": "ca_loc", "fresh": 80.0}]
        scenario = {
            "player": {"pos": [2.0, 8.0]},  # đứng sát bếp B1
            "random_customers": False,
            "customers": [
                {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "order_status": "reserved", "reserved_item_ids": ["I1"]}
            ]
        }
        sim = QuanSim(tuning=tuning, scenario=scenario, streams=Streams(1), ids=IdAllocator(), inventory=items)
        events = sim.step(make_input(interact=True))
        cook_ev = [e for e in events if e[0] == "cook_started"]
        self.assertEqual(len(cook_ev), 1)
        self.assertEqual(cook_ev[0][1]["base_price"], 47)
        self.assertEqual(cook_ev[0][1]["items"], [{"id": "I1", "kind": "ca_loc", "fresh": 80.0 - 0.25 / 60}])


if __name__ == "__main__":
    unittest.main()
