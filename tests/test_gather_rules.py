"""Gather rules owned by xuannghia2; public starter tests remain unchanged."""

import copy
import unittest

from chonoi.contract import load_contract
from chonoi.inputs import InputState
from chonoi.runner import Session


def action(move=(0, 0), *buttons):
    return InputState(move, {}, set(buttons))


class GatherRules(unittest.TestCase):
    def setUp(self):
        self.tuning = copy.deepcopy(load_contract()["tuning"])
        self.g = self.tuning["gather"]

    def session(self, **scenario):
        return Session("gather", self.tuning, dict(random_fish=False, monsters=[], **scenario), 7)

    def names(self, rows):
        return [r["name"] for r in rows]

    def test_oxygen_drains_and_empty_event_is_an_edge(self):
        s = self.session(player={"pos": [20, 5], "oxygen_ticks": 1})
        self.assertEqual(self.names(s.step(action())), ["oxygen_empty"])
        self.assertEqual(s.sim.oxygen_ticks, 0)
        self.assertEqual(s.sim.zero_oxy_ticks, 1)
        self.assertEqual(s.step(action()), [])
        self.assertEqual(s.sim.zero_oxy_ticks, 2)

    def test_choke_interval_reads_tuning_and_ignores_invulnerability(self):
        self.g["choke_interval_ticks"] = 3
        s = self.session(player={"pos": [20, 5], "oxygen_ticks": 0,
                                 "zero_oxy_ticks": 0, "invuln_ticks": 50})
        s.step(action())
        s.step(action())
        self.assertEqual(s.sim.hp, self.g["hp_max"])
        self.assertEqual(self.names(s.step(action())), ["choke"])
        self.assertEqual(s.sim.hp, self.g["hp_max"] - 1)
        self.assertEqual(s.sim.zero_oxy_ticks, 0)

    def test_faint_precedes_actions_and_time_and_clears_inventory(self):
        s = self.session(player={"pos": [20, 5], "oxygen_ticks": 0, "hp": 1,
                                 "zero_oxy_ticks": self.g["choke_interval_ticks"] - 1},
                         hold=["ca_loc"], time_left_ticks=1)
        rows = s.step(action((0, 0), "interact", "catch"))
        self.assertEqual(self.names(rows), ["choke", "faint", "gather_end"])
        self.assertEqual(rows[-1]["data"], {"reason": "fainted", "inventory": {"items": {}}})
        self.assertEqual(s.sim.hp, 0)
        self.assertEqual(s.sim.hold, [])
        self.assertTrue(s.done)
        self.assertEqual(s.sim.step(action()), [])

    def test_surface_boundary_refills_caps_and_resets_choking(self):
        s = self.session(player={"pos": [20, self.g["surface_depth"]], "oxygen_ticks": 1})
        s.step(action())
        self.assertEqual(s.sim.oxygen_ticks, 1 + self.g["oxygen_refill_per_tick"])
        s.sim.oxygen_ticks = s.sim.oxygen_max - 1
        s.step(action())
        self.assertEqual(s.sim.oxygen_ticks, s.sim.oxygen_max)

    def test_crossings_emit_once_and_use_final_position(self):
        self.g["ramp_max_ticks"] = 0
        s = self.session(player={"pos": [20, self.g["surface_depth"]], "oxygen_ticks": 10})
        self.assertEqual(self.names(s.step(action((0, 1)))), ["dive"])
        self.assertEqual(s.sim.oxygen_ticks, 9)
        self.assertEqual(s.step(action((0, 1))), [])
        s.sim.oxygen_ticks = 0
        s.sim.zero_oxy_ticks = self.g["choke_interval_ticks"] - 1
        s.sim.pos[1] = self.g["surface_depth"] + self.g["swim_speed"] / 120
        self.assertEqual(self.names(s.step(action((0, -1)))), ["surface"])
        self.assertEqual(s.sim.oxygen_ticks, self.g["oxygen_refill_per_tick"])
        self.assertEqual(s.sim.zero_oxy_ticks, 0)
        self.assertEqual(s.sim.hp, self.g["hp_max"])


class CollectionRules(unittest.TestCase):
    setUp = GatherRules.setUp
    session = GatherRules.session
    names = GatherRules.names

    def node(self, ident="N1", pos=None, kind="bong_sung", **kw):
        return dict(id=ident, pos=pos or [20, 0], kind=kind, **kw)

    def fish(self, ident="F1", pos=None, kind="ca_linh"):
        return dict(id=ident, pos=pos or [20, 5], kind=kind)

    def test_gather_picks_nearest_then_natural_id_once_per_press(self):
        nodes = [self.node("N1", [21.5, 0]), self.node("N10", [21, 0]),
                 self.node("N2", [19, 0])]
        s = self.session(player={"pos": [20, 0]}, nodes=nodes, hold=["ca_loc"])
        rows = s.step(action((0, 0), "interact"))
        self.assertEqual(self.names(rows), ["gather"])
        self.assertEqual(rows[0]["data"], {"node_id": "N2", "kind": "bong_sung", "amount": self.g["node_yield"]})
        self.assertEqual(s.sim.hold, ["ca_loc"] + ["bong_sung"] * self.g["node_yield"])
        self.assertEqual(next(n for n in s.sim.nodes if n["id"] == "N2")["regrow_ticks"],
                         round(self.g["regrow_s"] * 60))
        self.assertEqual(s.step(action()), [])

    def test_regrowth_happens_before_interaction(self):
        self.g["regrow_s"] = 0.1
        s = self.session(player={"pos": [20, 0]}, nodes=[self.node(regrow_ticks=1)])
        rows = s.step(action((0, 0), "interact"))
        self.assertEqual(self.names(rows), ["node_regrown", "gather"])
        self.assertEqual(s.sim.nodes[0]["regrow_ticks"], 6)
        for _ in range(5):
            self.assertEqual(s.step(action()), [])
        self.assertEqual(self.names(s.step(action())), ["node_regrown"])

    def test_surface_and_range_gate_harvesting(self):
        s = self.session(player={"pos": [20, 5]}, nodes=[self.node()])
        self.assertEqual(s.step(action((0, 0), "interact")), [])
        s = self.session(player={"pos": [20, 0]}, nodes=[self.node(pos=[23, 0])])
        self.assertEqual(s.step(action((0, 0), "interact")), [])
        s = self.session(player={"pos": [20, 0]}, nodes=[self.node(pos=[22, 0])])
        self.assertEqual(self.names(s.step(action((0, 0), "interact"))), ["gather"])

    def test_full_hold_leaves_node_and_cooldown_unchanged(self):
        s = self.session(player={"pos": [20, 0]}, nodes=[self.node()],
                         hold=["ca_loc"] * self.g["hold_capacity"])
        self.assertEqual(self.names(s.step(action((0, 0), "interact"))), ["hold_full"])
        self.assertEqual(s.sim.nodes[0]["regrow_ticks"], 0)
        self.assertEqual(len(s.sim.hold), self.g["hold_capacity"])

    def test_batch_collection_is_atomic_and_reads_yield(self):
        self.g["node_yield"] = 2
        s = self.session(player={"pos": [20, 0]}, nodes=[self.node()],
                         hold=["ca_loc"] * (self.g["hold_capacity"] - 1))
        self.assertEqual(self.names(s.step(action((0, 0), "interact"))), ["hold_full"])
        self.assertEqual(s.sim.nodes[0]["regrow_ticks"], 0)
        s.sim.hold.pop()
        self.assertEqual(self.names(s.step(action((0, 0), "interact"))), ["gather"])
        self.assertEqual(s.sim.hold[-2:], ["bong_sung", "bong_sung"])

    def test_catch_nearest_then_natural_id_removes_one_school(self):
        s = self.session(player={"pos": [20, 5]}, fish=[self.fish("F10"), self.fish("F2")])
        rows = s.step(action((0, 0), "catch"))
        self.assertEqual(self.names(rows), ["fish_caught"])
        self.assertEqual(rows[0]["data"]["fish_id"], "F2")
        self.assertEqual(s.sim.hold, ["ca_linh"] * self.g["fish_yield"]["ca_linh"])
        self.assertEqual([f["id"] for f in s.sim.fish], ["F10"])
        self.assertEqual(s.sim.catch_cd_ticks, round(self.g["catch_cooldown_s"] * 60))

    def test_catch_cooldown_expires_before_action(self):
        self.g["catch_cooldown_s"] = 3 / 60
        s = self.session(player={"pos": [20, 5]}, fish=[self.fish("F1"), self.fish("F2")])
        s.step(action((0, 0), "catch"))
        self.assertEqual(s.step(action((0, 0), "catch")), [])
        self.assertEqual(s.step(action((0, 0), "catch")), [])
        self.assertEqual(self.names(s.step(action((0, 0), "catch"))), ["fish_caught"])
        self.assertEqual(s.sim.fish, [])

    def test_catch_requires_underwater_target_in_range(self):
        for pos in ([20, self.g["surface_depth"]], [20, 10]):
            with self.subTest(pos=pos):
                s = self.session(player={"pos": pos}, fish=[self.fish()])
                self.assertEqual(s.step(action((0, 0), "catch")), [])
                self.assertEqual(s.sim.catch_cd_ticks, 0)
                self.assertEqual(len(s.sim.fish), 1)

    def test_catch_batch_wont_overflow_or_consume_fish(self):
        s = self.session(player={"pos": [20, 5]}, fish=[self.fish()],
                         hold=["bong_sung"] * (self.g["hold_capacity"] - 1))
        self.assertEqual(self.names(s.step(action((0, 0), "catch"))), ["hold_full"])
        self.assertEqual(len(s.sim.fish), 1)
        self.assertEqual(s.sim.catch_cd_ticks, 0)
        self.assertEqual(len(s.sim.hold), self.g["hold_capacity"] - 1)

    def test_dock_precedes_node_catch_and_timeout(self):
        s = self.session(nodes=[self.node(pos=self.g["dock_pos"])],
                         hold=["ca_loc"], time_left_ticks=1)
        rows = s.step(action((0, 0), "interact", "catch"))
        self.assertEqual(self.names(rows), ["gather_end"])
        self.assertEqual(s.sim.reason, "docked")
        self.assertEqual(s.sim.inventory_items(), {"ca_loc": 1})
        self.assertEqual(s.sim.nodes[0]["regrow_ticks"], 0)

    def test_last_tick_collects_before_timeout(self):
        s = self.session(player={"pos": [20, 5]}, fish=[self.fish(kind="ca_loc")], time_left_ticks=1)
        rows = s.step(action((0, 0), "catch"))
        self.assertEqual(self.names(rows), ["fish_caught", "gather_end"])
        self.assertEqual(rows[-1]["data"]["inventory"], {"items": {"ca_loc": 1}})

    def test_hold_keeps_pick_order_for_lifo(self):
        s = self.session(player={"pos": [20, 0]}, nodes=[self.node()], fish=[self.fish(kind="ca_loc")])
        s.step(action((0, 0), "interact"))
        s.sim.pos = [20, 5]
        s.step(action((0, 0), "catch"))
        self.assertEqual(s.sim.hold.pop(), "ca_loc")
        self.assertEqual(s.sim.hold.pop(), "bong_sung")

    def test_real_input_edges_do_not_repeat_harvest(self):
        from chonoi.inputs import InputPlayer
        self.g["regrow_s"] = 0.1
        s = self.session(player={"pos": [20, 0]}, nodes=[self.node()])
        ip = InputPlayer([{"tick": 0, "interact": True}, {"tick": 8, "interact": False},
                          {"tick": 9, "interact": True}])
        rows = []
        for tick in range(10):
            rows.extend(s.step(ip.advance(tick)))
        self.assertEqual(self.names(rows).count("gather"), 2)
        self.assertEqual(s.sim.hold, ["bong_sung"] * 2)


if __name__ == "__main__":
    unittest.main()
