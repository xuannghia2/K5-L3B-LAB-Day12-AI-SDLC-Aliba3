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
        return Session("gather", self.tuning, scenario, 7)

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


if __name__ == "__main__":
    unittest.main()
