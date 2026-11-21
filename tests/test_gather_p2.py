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


class MonstersP2(unittest.TestCase):
    def monster(self, ident="M1", pos=None, **kw):
        pos = pos or [50, 20]
        return dict(id=ident, kind="ca_sau", pos=list(pos), waypoints=[list(pos), [pos[0] + 4, pos[1]]], **kw)

    def sim(self, scenario=None, **kw):
        base = {"random_fish": False, "player": {"pos": [50, 20]}, "monsters": [self.monster()]}
        base.update(scenario or {})
        return GatherSim(tuning_p2(), base, Streams(1), IdAllocator(), **kw)

    def test_default_spawns_depend_on_day_and_fixture_replaces_them(self):
        for day, count in ((1, 1), (2, 1), (3, 2), (5, 2)):
            s = GatherSim(tuning_p2(), {"random_fish": False}, Streams(1), IdAllocator(), day=day)
            self.assertEqual(len(s.monsters), count)
        self.assertEqual(self.sim({"monsters": []}).monsters, [])

    def test_hit_loses_floor_half_lifo_and_sets_invulnerability_recoil(self):
        s = self.sim({"hold": ["ca_loc", "bong_sung", "ca_linh", "keo_neo", "ca_keo"]})
        events = s.step(idle())
        self.assertEqual(events, [("monster_hit", {"monster_id": "M1", "hp": 2,
            "lost": ["ca_keo", "keo_neo"], "pos": [50, 20]})])
        self.assertEqual(s.hold, ["ca_loc", "bong_sung", "ca_linh"])
        self.assertEqual(s.invuln_ticks, 90)
        self.assertEqual(s.monsters[0]["state_ticks_left"], 60)
        self.assertEqual(s.monsters[0]["recoil_dir"], [1, 0])
        s.step(idle())
        self.assertAlmostEqual(s.monsters[0]["pos"][0], 50 + 2 / 60)
        self.assertEqual(s.monsters[0]["state_ticks_left"], 59)

    def test_only_one_nearest_hit_and_natural_id_tie(self):
        s = self.sim({"monsters": [self.monster("M10"), self.monster("M2")]})
        events = s.step(idle())
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][1]["monster_id"], "M2")
        self.assertEqual(next(m for m in s.monsters if m["id"] == "M10")["state"], "chase")

    def test_invulnerable_contact_does_not_hit_or_recoil_and_boundary_expires(self):
        s = self.sim({"player": {"pos": [50, 20], "invuln_ticks": 2}})
        self.assertEqual(s.step(idle()), [])
        self.assertEqual(s.monsters[0]["state"], "chase")
        self.assertEqual(s.step(idle())[0][0], "monster_hit")

    def test_choke_precedes_hit_and_does_not_drop_half_hold(self):
        s = self.sim({"player": {"pos": [50, 20], "hp": 3, "oxygen_ticks": 0, "zero_oxy_ticks": 59},
                      "hold": ["ca_loc", "ca_keo", "keo_neo"]})
        events = s.step(idle())
        self.assertEqual([e[0] for e in events], ["choke", "monster_hit"])
        self.assertEqual(s.hp, 1)
        self.assertEqual(events[-1][1]["lost"], ["keo_neo"])

    def test_lethal_hit_has_remaining_losses_then_empty_inventory(self):
        s = self.sim({"player": {"pos": [50, 20], "hp": 1},
                      "hold": ["ca_loc", "bong_sung", "ca_keo"]})
        events = s.step(idle("catch", "interact"))
        self.assertEqual([e[0] for e in events], ["monster_hit", "faint", "gather_end"])
        self.assertEqual(events[0][1]["lost"], ["ca_keo"])
        self.assertEqual(events[1][1], {"cause": "monster", "hp": 0, "lost": ["bong_sung", "ca_loc"]})
        self.assertEqual(events[-1][1]["inventory"], {"items": {}})

    def test_patrol_speed_waypoint_change_then_depth_detection_and_hysteresis(self):
        s = self.sim({"player": {"pos": [50, 0]}})
        m = s.monsters[0]
        m["pos"] = [53.99, 20]
        s.step(idle())
        self.assertEqual(m["pos"], [54, 20])
        self.assertEqual(m["target_idx"], 0)
        s.step(idle())
        self.assertAlmostEqual(m["pos"][0], 54 - 1 / 60)
        s.pos = [44, 20]
        s.step(idle())
        self.assertEqual(m["state"], "chase")
        s.pos = [39, 20]
        s.step(idle())
        self.assertEqual(m["state"], "chase")
        s.pos = [10, 20]
        s.step(idle())
        self.assertEqual(m["state"], "patrol")
        s.pos = [m["pos"][0], 9.9]
        s.step(idle())
        self.assertEqual(m["state"], "patrol")

    def test_recoil_final_tick_cannot_detect_or_hit(self):
        m = self.monster(state="recoil", state_ticks_left=1, recoil_dir=[1, 0])
        s = self.sim({"monsters": [m]})
        self.assertEqual(s.step(idle()), [])
        self.assertEqual(s.monsters[0]["state"], "patrol")
        self.assertEqual(s.step(idle())[0][0], "monster_hit")

    def test_active_upgrade_limits_are_local_and_support_day_integration(self):
        t = tuning_p2()
        t["shop"] = {"upgrades": {"oxygen": [{"level": 1, "oxygen_max_s": 45}],
                                      "hp": [{"level": 2, "hp_max": 5}]}}
        s = GatherSim(t, {"random_fish": False}, Streams(1), IdAllocator(), active_upgrades={"oxygen": 1, "hp": 2})
        self.assertEqual(s.oxygen_max, 2700)
        self.assertEqual(s.hp, 5)
        self.assertEqual(s.snapshot()["player"]["hp_max"], 5)
        self.assertEqual(t["gather"]["hp_max"], 3)
        self.assertEqual(t["gather"]["oxygen_max_s"], 30)


class GatherP2Cli(unittest.TestCase):
    def run_case(self, w, scenario, frames=None, ticks=1, name="p2"):
        from helpers import run_headless, write_json, read_jsonl
        sc = write_json(w.path(name + ".json"), {"gather": scenario})
        inp = write_json(w.path(name + "-inputs.json"), {"frames": frames or []})
        out = w.path(name + ".log")
        inv = w.path(name + "-inventory.json")
        code, err = run_headless("--mode", "gather", "--seed", "9", "--scenario", sc,
            "--inputs", inp, "--ticks", str(ticks), "--snapshot-every", "1", "--out", out, "--inventory-out", inv)
        return code, err, read_jsonl(out) if Path(out).exists() else [], inv

    def test_new_ingredients_export_and_import_unchanged_schema(self):
        from helpers import Workdir, run_headless, read_jsonl
        with Workdir() as w:
            code, err, rows, inv = self.run_case(w, {"hold": ["ca_keo", "keo_neo"],
                "random_fish": False, "monsters": []}, [{"tick": 0, "interact": True}])
            self.assertEqual(code, 0, err)
            self.assertEqual(json.loads(Path(inv).read_text()), {"items": {"ca_keo": 1, "keo_neo": 1}})
            code, err = run_headless("--mode", "quan", "--seed", "9", "--ticks", "0",
                "--inventory", inv, "--out", w.path("quan.log"))
            self.assertEqual(code, 0, err)
            self.assertEqual(read_jsonl(w.path("quan.log"))[0]["stock"], {"ca_keo": 1, "keo_neo": 1})

    def test_pause_freezes_timers_and_resume_runs_same_outer_tick(self):
        from helpers import Workdir
        with Workdir() as w:
            code, err, rows, _ = self.run_case(w, {"player": {"pos": [20, 5], "oxygen_ticks": 10},
                "monsters": [], "fish": []}, [{"tick": 0, "pause": True, "catch": True},
                {"tick": 2, "pause": False}, {"tick": 3, "pause": True}], ticks=4)
            self.assertEqual(code, 0, err)
            snaps = {r["tick"]: r for r in rows if r["type"] == "snapshot"}
            for tick in (1, 2, 3):
                self.assertEqual(snaps[tick]["sim_tick"], 0)
                self.assertEqual(snaps[tick]["phase_tick"], 0)
                self.assertEqual(snaps[tick]["player"]["oxygen_ticks"], 10)
                self.assertEqual(snaps[tick]["state"], "paused")
            self.assertEqual(snaps[4]["sim_tick"], 1)
            self.assertEqual(snaps[4]["player"]["oxygen_ticks"], 9)
            self.assertEqual([(r["name"], r["tick"]) for r in rows if r["type"] == "event"], [("paused", 1), ("resumed", 4)])

    def test_invalid_monster_and_age_exit_2_before_output(self):
        from helpers import Workdir
        valid = {"id": "M1", "kind": "ca_sau", "pos": [50, 20], "waypoints": [[50, 20], [54, 20]]}
        bads = [{"fish": [{"id": "F1", "kind": "ca_keo", "pos": [50, 24], "age_ticks": -1}]},
            {"monsters": [dict(valid, target_idx=2)]}, {"monsters": [dict(valid, state="recoil")]},
            {"monsters": [dict(valid, state="recoil", state_ticks_left=1, recoil_dir=[2, 0])]},
            {"monsters": [dict(valid, pos=[50, 5])]}, {"monsters": [valid, valid]},
            {"player": {"heading_deg": float("nan")}}]
        for scenario in bads:
            with self.subTest(scenario=scenario), Workdir() as w:
                code, _, rows, inv = self.run_case(w, scenario)
                self.assertEqual(code, 2)
                self.assertEqual(rows, [])
                self.assertFalse(Path(inv).exists())

    def test_monster_faint_outputs_remaining_lifo_and_empty_inventory(self):
        from helpers import Workdir
        with Workdir() as w:
            code, err, rows, inv = self.run_case(w, {"player": {"pos": [60, 24], "hp": 1},
                "hold": ["ca_loc", "keo_neo", "ca_keo"], "random_fish": False})
            self.assertEqual(code, 0, err)
            events = [r for r in rows if r["type"] == "event"]
            self.assertEqual([r["name"] for r in events], ["monster_hit", "faint", "gather_end"])
            self.assertEqual(events[0]["data"]["lost"], ["ca_keo"])
            self.assertEqual(events[1]["data"], {"cause": "monster", "hp": 0, "lost": ["keo_neo", "ca_loc"]})
            self.assertEqual(json.loads(Path(inv).read_text()), {"items": {}})

    def test_swimming_and_scheduled_spawn_deterministic_bytes(self):
        from helpers import Workdir
        with Workdir() as w:
            a = self.run_case(w, {"monsters": []}, ticks=720, name="a")
            b = self.run_case(w, {"monsters": []}, ticks=720, name="b")
            self.assertEqual(a[0], 0, a[1])
            self.assertEqual(b[0], 0, b[1])
            self.assertEqual(Path(w.path("a.log")).read_bytes(), Path(w.path("b.log")).read_bytes())
            self.assertEqual([r["tick"] for r in a[2] if r.get("name") == "fish_spawned"], [360, 720])

    def test_inactive_extensions_and_shop_buttons_ignored_in_gather(self):
        from helpers import Workdir
        with Workdir() as w:
            code, err, rows, _ = self.run_case(w, {"random_fish": False, "monsters": []},
                [{"tick": 0, "attack": True, "photo": True, "shop_done": True, "buy": "oxygen"}])
            self.assertEqual(code, 0, err)
            self.assertFalse([r for r in rows if r["type"] == "event"])


if __name__ == "__main__":
    unittest.main()
