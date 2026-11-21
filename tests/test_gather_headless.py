"""CLI and inventory evidence for the gather module (xuannghia2)."""

import json
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


class GatherHeadless(unittest.TestCase):
    def run_case(self, w, scenario, inputs, ticks, name="g"):
        sc = write_json(w.path(name + "-scenario.json"), {"gather": scenario})
        inp = write_json(w.path(name + "-inputs.json"), frames(*inputs))
        out, inv = w.path(name + ".jsonl"), w.path(name + "-inventory.json")
        code, err = run_headless("--mode", "gather", "--seed", "7", "--ticks", str(ticks),
                                 "--scenario", sc, "--inputs", inp, "--snapshot-every", "1",
                                 "--inventory-out", inv, "--out", out)
        self.assertEqual(code, 0, err)
        return read_jsonl(out), inv, out

    def test_faint_writes_empty_inventory_and_exact_end_order(self):
        with Workdir() as w:
            rows, inv, _ = self.run_case(w, {"player": {"pos": [20, 5], "hp": 1,
                "oxygen_ticks": 0, "zero_oxy_ticks": 59}, "hold": ["ca_loc"],
                "random_fish": False}, [{"tick": 0, "catch": True, "interact": True}], 5)
            self.assertEqual([r["name"] for r in events(rows)], ["choke", "faint", "gather_end"])
            self.assertTrue(all(r["tick"] == 1 for r in events(rows)))
            self.assertEqual(rows[-1]["reason"], "fainted")
            self.assertEqual(len(events(rows, "gather_end")), 1)
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {}})

    def test_harvest_dock_exports_stock_that_quan_can_read(self):
        with Workdir() as w:
            rows, inv, _ = self.run_case(w, {"player": {"pos": [5.1, 0]}, "hold": ["ca_loc"],
                "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [5.1, 0]}],
                "random_fish": False}, [{"tick": 0, "interact": True},
                {"tick": 1, "interact": False, "move": [-1, 0]},
                {"tick": 16, "move": [0, 0], "interact": True}], 30)
            self.assertEqual([r["name"] for r in events(rows)], ["gather", "gather_end"])
            self.assertEqual(rows[-1]["reason"], "docked")
            expected = {"bong_sung": 1, "ca_loc": 1}
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": expected})
            code, err = run_headless("--mode", "quan", "--seed", "7", "--ticks", "0",
                                     "--inventory", inv, "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertEqual(snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"], expected)

    def test_catch_determinism_includes_nonempty_events_and_inventory(self):
        with Workdir() as w:
            scenario = {"player": {"pos": [20, 5]}, "fish": [
                {"id": "F10", "kind": "ca_linh", "pos": [20, 5]},
                {"id": "F2", "kind": "ca_loc", "pos": [20, 5]}], "time_left_ticks": 35}
            inputs = [{"tick": 0, "catch": True}, {"tick": 1, "catch": False},
                      {"tick": 30, "catch": True}]
            rows, inv1, out1 = self.run_case(w, scenario, inputs, 40, "a")
            _, inv2, out2 = self.run_case(w, scenario, inputs, 40, "b")
            self.assertEqual([e["data"]["fish_id"] for e in events(rows, "fish_caught")], ["F2", "F10"])
            for a, b in ((out1, out2), (inv1, inv2)):
                with open(a, "rb") as fa, open(b, "rb") as fb:
                    self.assertEqual(fa.read(), fb.read())
            with open(inv1, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {"ca_linh": 3, "ca_loc": 1}})

    def test_unfinished_gather_preserves_existing_inventory(self):
        with Workdir() as w:
            inv = w.path("g-inventory.json")
            previous = b'{"items":{"ca_loc":7}}\n'
            with open(inv, "wb") as f:
                f.write(previous)
            rows, _, _ = self.run_case(w, {"player": {"pos": [20, 5]}, "fish": [
                {"id": "F1", "kind": "ca_loc", "pos": [20, 5]}]},
                [{"tick": 0, "catch": True}], 2)
            self.assertEqual(len(events(rows, "fish_caught")), 1)
            self.assertEqual(rows[-1]["reason"], "tick_limit")
            with open(inv, "rb") as f:
                self.assertEqual(f.read(), previous)


if __name__ == "__main__":
    unittest.main()
