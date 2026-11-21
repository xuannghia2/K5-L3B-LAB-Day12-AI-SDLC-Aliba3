"""Ticket-02 gather regression, including fixed P1 fixture behavior."""

import copy
import json
from pathlib import Path
import unittest

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.fish import FishPopulation, reflect_motion
from chonoi.sim.gather import GatherSim


def tuning_p2():
    tuning = copy.deepcopy(load_contract()["tuning"])
    tuning["gather"] = json.loads((Path(__file__).resolve().parents[1] / "data/gather-p2.json").read_text(encoding="utf-8"))
    return tuning


def idle(*edges):
    return InputState((0, 0), {}, set(edges))


class FishP2(unittest.TestCase):
    def population(self, scenario=None, seed=1):
        return FishPopulation(tuning_p2()["gather"], scenario or {}, Streams(seed), IdAllocator())

    def test_eight_initial_schools_unique_positions_and_seed(self):
        a, b = self.population(), self.population()
        self.assertEqual(len(a.fish), 8)
        self.assertEqual(len({tuple(f["pos"]) for f in a.fish}), 8)
        self.assertEqual(a.fish, b.fish)
        self.assertNotEqual(a.fish, self.population(seed=2).fish)
        self.assertTrue(all(f["age_ticks"] == 0 for f in a.fish))

    def test_speed_and_turn_on_120th_swim_step(self):
        p = self.population({"fish": [{"id": "F4", "kind": "ca_linh", "pos": [50, 5], "heading_deg": 0}]})
        for k in range(1, 120):
            p.step(k, [])
        self.assertAlmostEqual(p.fish[0]["pos"][0], 50 + 119 * 1.5 / 60)
        self.assertEqual(p.fish[0]["heading_deg"], 0)
        p.step(120, [])
        self.assertNotEqual(p.fish[0]["heading_deg"], 0)
        self.assertEqual(p.fish[0]["age_ticks"], 120)

    def test_reflection_keeps_remainder_and_corner_flips_both_axes(self):
        pos, heading = reflect_motion([95.99, 5], 0, 0.025, [4, 96], [3, 12])
        self.assertAlmostEqual(pos[0], 95.985)
        self.assertAlmostEqual(heading, 180)
        pos, heading = reflect_motion([96, 12], 45, 0.025, [4, 96], [3, 12])
        self.assertLess(pos[0], 96)
        self.assertLess(pos[1], 12)
        self.assertAlmostEqual(heading, 225)

    def test_random_false_freezes_fixture_and_disables_spawn(self):
        p = self.population({"random_fish": False, "fish": [{"id": "F1", "kind": "ca_loc", "pos": [20, 5]}]})
        before = copy.deepcopy(p.fish)
        events = []
        for k in range(1, 721):
            p.step(k, events)
        self.assertEqual(p.fish, before)
        self.assertEqual(events, [])
        self.assertEqual(self.population({"random_fish": False}).fish, [])

    def test_scheduled_spawn_age_zero_and_ids_after_fixture(self):
        p = self.population({"fish": [{"id": "F20", "kind": "ca_linh", "pos": [50, 5]}]})
        events = []
        for k in range(1, 360):
            p.step(k, events)
        self.assertEqual(events, [])
        p.step(360, events)
        self.assertEqual(events[0][0], "fish_spawned")
        self.assertEqual(events[0][1]["id"], "F21")
        self.assertEqual(p.fish[-1]["age_ticks"], 0)
        self.assertEqual(events[0][1]["pos"], p.fish[-1]["pos"])

    def test_spawn_cap_and_no_available_point(self):
        p = self.population({"fish": []})
        while p.spawn() is not None:
            pass
        self.assertEqual(len(p.fish), 12)
        self.assertIsNone(p.spawn())
        p = self.population({"fish": []})
        points = {tuple([x, d]) for kind in p.t["fish_spawn_depths"]
                  for x in p.t["fish_spawn_x"] for d in p.t["fish_spawn_depths"][kind]}
        self.assertEqual(len(points), 30)
        p.t = dict(p.t, fish_max=100)
        p.fish = [{"pos": list(pos)} for pos in points]
        self.assertIsNone(p.spawn())

    def test_catch_uses_position_before_fish_swims(self):
        t = tuning_p2()
        s = GatherSim(t, {"player": {"pos": [20, 5]}, "fish": [
            {"id": "F1", "kind": "ca_linh", "pos": [22, 5], "heading_deg": 0}]}, Streams(1), IdAllocator())
        rows = s.step(idle("catch"))
        self.assertEqual(rows[0], ("fish_caught", {"fish_id": "F1", "kind": "ca_linh", "yield": 3}))
        self.assertEqual(s.fish, [])

    def test_no_swim_or_spawn_after_last_tick(self):
        s = GatherSim(tuning_p2(), {"time_left_ticks": 1, "fish": []}, Streams(1), IdAllocator())
        s.phase_tick = 359
        self.assertEqual(s.step(idle())[0][0], "gather_end")
        self.assertEqual(s.fish, [])


if __name__ == "__main__":
    unittest.main()
