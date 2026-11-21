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


if __name__ == "__main__":
    unittest.main()
