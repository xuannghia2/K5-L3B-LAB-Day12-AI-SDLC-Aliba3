"""Gather P3 runs with a v1.2 test manifest while shared main stays on v1.1 until quan is ready."""

import contextlib
import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from chonoi.contract import load_contract
from chonoi.headless import main
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.runner import Session
from chonoi.sim.gather import GatherSim
from helpers import Workdir, read_jsonl, write_json
from test_freshness import tuning_p3


def idle(*edges):
    return InputState((0, 0), {}, set(edges))


def item(ident="I1", kind="ca_loc", fresh=100):
    return {"id": ident, "kind": kind, "fresh": fresh}


class GatherP3(unittest.TestCase):
    def sim(self, **scenario):
        base = {"random_fish": False, "monsters": [], "player": {"pos": [20, 0]}}
        base.update(scenario)
        return GatherSim(tuning_p3(), base, Streams(1), IdAllocator())

    def test_pickup_gets_new_id_full_freshness_and_decays_next_step(self):
        s = self.sim(hold=[item("I20", fresh=80)], nodes=[{"id": "N1", "kind": "keo_neo", "pos": [20, 0]}])
        events = s.step(idle("interact"))
        self.assertEqual(events[0][0], "gather")
        self.assertEqual(s.hold[1], item("I21", "keo_neo"))
        self.assertAlmostEqual(s.hold[0]["fresh"], 80 - 0.5 / 60)
        s.step(idle())
        self.assertAlmostEqual(s.hold[1]["fresh"], 100 - 0.5 / 60)

    def test_fish_yield_allocates_three_distinct_ids(self):
        s = self.sim(player={"pos": [20, 5]}, fish=[{"id": "F1", "kind": "ca_linh", "pos": [20, 5]}])
        s.step(idle("catch"))
        self.assertEqual(s.hold, [item("I1", "ca_linh"), item("I2", "ca_linh"), item("I3", "ca_linh")])

    def test_spoil_order_before_dock_and_retains_all_spoiled_items(self):
        s = self.sim(player={"pos": [2, 0]}, hold=[item("I10", fresh=30), item("I2", fresh=30)])
        events = s.step(idle("interact"))
        self.assertEqual([e[0] for e in events], ["spoiled", "spoiled", "gather_end"])
        self.assertEqual([e[1]["item_id"] for e in events[:2]], ["I2", "I10"])
        self.assertEqual([i["id"] for i in events[-1][1]["inventory"]["items"]], ["I2", "I10"])
        self.assertTrue(all(i["fresh"] < 30 for i in s.hold))

    def test_monster_loss_and_faint_preserve_pick_order_not_id_order(self):
        s = self.sim(player={"pos": [60, 24], "hp": 1}, monsters=[{
            "id": "M1", "kind": "ca_sau", "pos": [60, 24], "waypoints": [[60, 24], [64, 24]]}],
            hold=[item("I10"), item("I2"), item("I1")])
        events = s.step(idle())
        self.assertEqual([e[0] for e in events], ["monster_hit", "faint", "gather_end"])
        self.assertEqual([i["id"] for i in events[0][1]["lost"]], ["I1"])
        self.assertEqual([i["id"] for i in events[1][1]["lost"]], ["I2", "I10"])
        self.assertAlmostEqual(events[0][1]["lost"][0]["fresh"], 100 - 0.5 / 60)
        self.assertEqual(events[-1][1]["inventory"], {"items": []})
        self.assertEqual(s.hold, [])

    def test_spoil_precedes_choke_faint_and_lost_contains_decayed_items(self):
        s = self.sim(player={"pos": [20, 5], "oxygen_ticks": 0, "zero_oxy_ticks": 59, "hp": 1}, hold=[item(fresh=30)])
        events = s.step(idle())
        self.assertEqual([e[0] for e in events], ["spoiled", "choke", "faint", "gather_end"])
        self.assertEqual(events[2][1]["lost"][0]["id"], "I1")
        self.assertLess(events[2][1]["lost"][0]["fresh"], 30)

    def test_paused_session_does_not_decay_or_spoil_until_resume(self):
        s = Session("gather", tuning_p3(), {"hold": [item(fresh=30)], "random_fish": False, "monsters": []}, 1)
        self.assertEqual(s.step(idle("pause"))[0]["name"], "paused")
        for _ in range(100):
            self.assertEqual(s.step(idle()), [])
        self.assertEqual(s.sim.hold[0]["fresh"], 30)
        events = s.step(idle("pause"))
        self.assertEqual([e["name"] for e in events], ["resumed", "spoiled"])
        self.assertEqual(s.sim_tick, 1)

    def test_spoiled_items_still_occupy_capacity_and_snapshot_is_detached(self):
        s = self.sim(hold=[item(f"I{i}", fresh=0) for i in range(1, 13)],
            nodes=[{"id": "N1", "kind": "keo_neo", "pos": [20, 0]}])
        before = s.snapshot()
        events = s.step(idle("interact"))
        self.assertEqual(events[0][0], "hold_full")
        self.assertEqual(s.snapshot()["hold_count"], 12)
        self.assertEqual(before["hold"], s.snapshot()["hold"])


class GatherP3Headless(unittest.TestCase):
    def run_case(self, w, scenario, frames=None, ticks=1, name="g"):
        contract = copy.deepcopy(load_contract())
        contract["contract_version"] = "1.2"
        contract["tuning"] = tuning_p3()
        sc = write_json(w.path(name + "-scenario.json"), {"gather": scenario})
        inp = write_json(w.path(name + "-inputs.json"), {"frames": frames or []})
        out, inv = w.path(name + ".log"), w.path(name + "-inventory.json")
        args = ["--mode", "gather", "--seed", "7", "--scenario", sc, "--inputs", inp,
                "--ticks", str(ticks), "--snapshot-every", "1", "--out", out, "--inventory-out", inv]
        with patch("chonoi.headless.load_contract", return_value=contract), contextlib.redirect_stderr(io.StringIO()):
            code = main(args)
        return code, read_jsonl(out) if Path(out).exists() else [], inv

    def test_full_precision_export_matches_event_and_final_snapshot(self):
        with Workdir() as w:
            code, rows, inv = self.run_case(w, {"hold": [item()], "random_fish": False, "monsters": []}, [{"tick": 0, "interact": True}])
            self.assertEqual(code, 0)
            saved = json.loads(Path(inv).read_text())
            event = next(r for r in rows if r.get("name") == "gather_end")
            snap = [r for r in rows if r["type"] == "snapshot"][-1]
            self.assertEqual(saved, event["data"]["inventory"])
            self.assertEqual(saved["items"], snap["hold"])
            self.assertEqual(saved["items"][0]["fresh"], 100 - 0.5 / 60)
            self.assertNotEqual(saved["items"][0]["fresh"], round(100 - 0.5 / 60, 3))

    def test_threshold_event_tick_and_invalid_legacy_hold(self):
        with Workdir() as w:
            code, rows, _ = self.run_case(w, {"hold": [item(fresh=30)], "random_fish": False, "monsters": []}, ticks=2)
            self.assertEqual(code, 0)
            self.assertEqual([(r["tick"], r["data"]) for r in rows if r.get("name") == "spoiled"],
                [(1, {"item_id": "I1", "kind": "ca_loc", "location": "hold"})])
        for hold in (["ca_loc"], [item(), item()], [item(fresh=101)]):
            with self.subTest(hold=hold), Workdir() as w:
                code, rows, inv = self.run_case(w, {"hold": hold})
                self.assertEqual(code, 2)
                self.assertEqual(rows, [])
                self.assertFalse(Path(inv).exists())

    def test_limit_does_not_overwrite_v12_inventory(self):
        with Workdir() as w:
            inv = Path(w.path("g-inventory.json"))
            previous = '{"items":[{"id":"I99","kind":"ca_loc","fresh":20}]}'
            inv.write_text(previous)
            code, _, _ = self.run_case(w, {"hold": [item()], "random_fish": False, "monsters": []})
            self.assertEqual(code, 0)
            self.assertEqual(inv.read_text(), previous)


if __name__ == "__main__":
    unittest.main()
