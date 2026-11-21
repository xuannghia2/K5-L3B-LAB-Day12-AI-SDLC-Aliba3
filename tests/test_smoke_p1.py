"""Smoke test Phase 1 (công khai), kiểu HỘP ĐEN: chỉ chạy `headless_cmd` trong game.contract.json và đọc JSONL/file kho.
Vì vậy chạy được với BẤT KỲ ngôn ngữ nào nhóm chọn, miễn đúng Test Contract. Nhóm viết thêm test cho luật của mình.

Chạy: python3 -m unittest discover -s tests -v
"""

import json
import os
import unittest

from helpers import (Workdir, close, events, frames, read_jsonl, run_headless, snapshots, write_json)


def last_pos(rows):
    return snapshots(rows)[-1]["player"]["pos"]


def tuning_gather():
    with open("game.contract.json", encoding="utf-8") as f:
        return json.load(f)["tuning"]["gather"]


class Contract(unittest.TestCase):
    def test_con_01_ticks_zero_and_end_line(self):
        with Workdir() as w:
            for mode in ("gather", "quan"):
                code, err = run_headless("--mode", mode, "--seed", "1", "--ticks", "0", "--out", w.path(f"{mode}.jsonl"))
                self.assertEqual(code, 0, err)
                rows = read_jsonl(w.path(f"{mode}.jsonl"))
                self.assertEqual(rows[0]["type"], "snapshot")
                self.assertEqual(rows[0]["tick"], 0)
                self.assertEqual(rows[-1]["type"], "end")
                self.assertEqual(sum(r["type"] == "end" for r in rows), 1)

    def test_gather_snapshot_has_gather_fields(self):
        with Workdir() as w:
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--out", w.path("g.jsonl"))
            self.assertEqual(code, 0, err)
            s = snapshots(read_jsonl(w.path("g.jsonl")))[0]
            self.assertEqual(s["mode"], "gather")
            self.assertEqual(s["player"]["pos"], [2, 0])
            for key in ("oxygen_ticks", "hp", "oxygen_max_ticks", "hp_max", "at_surface"):
                self.assertIn(key, s["player"])
            self.assertEqual(s["hold_capacity"], tuning_gather()["hold_capacity"])
            # Ticket-02 changes the default from six stationary to eight seeded schools.
            initial = tuning_gather()["fish_initial"]
            self.assertEqual(len(s["fish"]), initial if isinstance(initial, int) else len(initial))
            self.assertTrue(all(n["pos"][1] == 0 for n in s["nodes"]))

    def test_con_02_deterministic_bytes(self):
        with Workdir() as w:
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [1, 1]}, {"tick": 100, "move": [0, 0]}))
            for i in (1, 2):
                code, err = run_headless("--mode", "gather", "--seed", "7", "--ticks", "300", "--inputs", inp,
                                         "--out", w.path(f"o{i}.jsonl"))
                self.assertEqual(code, 0, err)
            with open(w.path("o1.jsonl"), "rb") as a, open(w.path("o2.jsonl"), "rb") as b:
                self.assertEqual(a.read(), b.read())

    def test_con_03_bad_input_exit_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            bad = write_json(w.path("bad.json"), frames({"tick": 5, "move": [0, 1]}, {"tick": 5}))
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "10", "--inputs", bad, "--out", out)[0], 2)
            self.assertFalse(os.path.exists(out), "lỗi đầu vào phải thoát TRƯỚC khi ghi đầu ra")
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "-1", "--out", out)[0], 2)
            for button in ("jump",):  # Ticket-02 accepts attack but ignores it when the extension is disabled
                unk = write_json(w.path("unk.json"), frames({"tick": 0, button: True}))
                self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "10", "--inputs", unk, "--out", out)[0], 2, button)
            self.assertFalse(os.path.exists(out))

    def test_con_03_old_and_future_modes_rejected(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            for mode in ("river", "day"):
                self.assertEqual(run_headless("--mode", mode, "--seed", "1", "--ticks", "0", "--out", out)[0], 2, mode)
            self.assertFalse(os.path.exists(out))
            old = write_json(w.path("old.json"), {"river": {"hold": []}})
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--scenario", old, "--out", out)[0], 2)

    def test_scenario_out_of_domain_exit_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            for block in ({"player": {"pos": [101, 0]}}, {"player": {"pos": [5, -1]}},
                          {"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [5, 3]}]},
                          {"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [5, 0]}, {"id": "N1", "kind": "bong_sung", "pos": [9, 0]}]},
                          {"hold": ["ca_loc"] * (tuning_gather()["hold_capacity"] + 1)}, {"vortices": []}):
                sc = write_json(w.path("sc.json"), {"gather": block})
                self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--scenario", sc, "--out", out)[0], 2, block)


class ScenarioModes(unittest.TestCase):
    def test_khoi_sai_mode_exit_2(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"quan": {"stock": {}}})
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--scenario", sc,
                                          "--out", w.path("o.jsonl"))[0], 2)
            sc = write_json(w.path("sc2.json"), {"gather": {"hold": []}})
            self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--scenario", sc,
                                          "--out", w.path("o.jsonl"))[0], 2)

    def test_quan_fixture_khong_hop_le_exit_2(self):
        with Workdir() as w:
            for block in ({"player": {"pos": [17, 0]}}, {"customers": [{"id": "C1"}]},
                          {"customers": [{"id": "C1", "table_id": "T9"}]}):
                sc = write_json(w.path("sc.json"), {"quan": block})
                self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--scenario", sc,
                                              "--out", w.path("o.jsonl"))[0], 2, block)

    def test_quan_player_vel_hop_le(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"quan": {"player": {"pos": [8, 5], "vel": [0, 0]}}})
            self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "1", "--scenario", sc,
                                          "--out", w.path("o.jsonl"))[0], 0)


class Movement(unittest.TestCase):
    def test_move_ramp_doi_huong_trong_tran(self):
        """Đảo từ +speed sang -speed: vận tốc chạm mục tiêu sau tối đa ramp_max_ticks tick kể từ lúc đổi input."""
        g = tuning_gather()
        ramp = g["ramp_max_ticks"]
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"player": {"pos": [50, 10]}}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [1, 0]}, {"tick": 20, "move": [-1, 0]}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", str(20 + ramp + 2), "--scenario", sc,
                                     "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            s = {r["tick"]: r for r in snapshots(read_jsonl(w.path("o.jsonl")))}
            self.assertTrue(close(s[20 + ramp]["player"]["vel"][0], -g["swim_speed"], 0.01), s[20 + ramp]["player"]["vel"])

    def test_move_mep_vel_ve_0(self):
        with Workdir() as w:
            b = tuning_gather()["bounds"]
            sc = write_json(w.path("sc.json"), {"gather": {"player": {"pos": [b["x"][1] - 1, 10]}}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [1, 0]}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "240", "--scenario", sc,
                                     "--inputs", inp, "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            p = snapshots(read_jsonl(w.path("o.jsonl")))[-1]["player"]
            self.assertEqual(p["pos"][0], b["x"][1])
            self.assertEqual(p["vel"][0], 0)

    def test_move_01_swim_speed_after_ramp(self):
        """Bỏ 6 tick tăng tốc rồi đo 60 tick: quãng ≈ swim_speed × 1 s (±0.1). Ngang, xuống, chéo (không nhanh hơn)."""
        speed = tuning_gather()["swim_speed"]
        for mv in ([1, 0], [0, 1], [1, 1]):
            with Workdir() as w:
                sc = write_json(w.path("sc.json"), {"gather": {"player": {"pos": [20, 5]}}})
                inp = write_json(w.path("in.json"), frames({"tick": 0, "move": mv}))
                code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "66", "--scenario", sc,
                                         "--inputs", inp, "--snapshot-every", "1", "--out", w.path("o.jsonl"))
                self.assertEqual(code, 0, err)
                s = {r["tick"]: r for r in snapshots(read_jsonl(w.path("o.jsonl")))}
                a, b = s[6]["player"]["pos"], s[66]["player"]["pos"]
                self.assertTrue(close(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5, speed), (mv, a, b))

    def test_move_02_heading_positive_is_down(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"player": {"pos": [20, 5]}}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [0, 1]}))
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "30", "--scenario", sc,
                                     "--inputs", inp, "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            last = snapshots(read_jsonl(w.path("o.jsonl")))[-1]["player"]
            self.assertTrue(close(last["heading_deg"], 90, 0.5), last)
            self.assertGreater(last["pos"][1], 5)

    def test_move_03_edge_clamp(self):
        """Chặn từng mép của vùng nước, kể cả d không âm (không bay lên khỏi mặt nước) và đáy d = 30."""
        b = tuning_gather()["bounds"]
        cases = [([98, 10], [1, 0], 0, b["x"][1]), ([3, 10], [-1, 0], 0, b["x"][0]),
                 ([50, 2], [0, -1], 1, b["d"][0]), ([50, 28], [0, 1], 1, b["d"][1])]
        for pos, mv, axis, want in cases:
            with Workdir() as w:
                sc = write_json(w.path("sc.json"), {"gather": {"player": {"pos": pos}}})
                inp = write_json(w.path("in.json"), frames({"tick": 0, "move": mv}))
                g = tuning_gather()
                ticks = int((abs(want - pos[axis]) / g["swim_speed"]) * 60) + g["ramp_max_ticks"] + 30
                code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", str(ticks), "--scenario", sc,
                                         "--inputs", inp, "--out", w.path("o.jsonl"))
                self.assertEqual(code, 0, err)
                self.assertEqual(last_pos(read_jsonl(w.path("o.jsonl")))[axis], want, (pos, mv))

    def test_time_ends_gather_and_keeps_hold(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"hold": ["ca_loc"], "time_left_ticks": 3,
                                                           "player": {"pos": [50, 10]}}})
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "100", "--scenario", sc,
                                     "--inventory-out", inv, "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("o.jsonl"))
            end_ev = events(rows, "gather_end")
            self.assertEqual(len(end_ev), 1)
            self.assertEqual(end_ev[0]["tick"], 3)
            self.assertEqual(end_ev[0]["data"]["reason"], "time")
            self.assertEqual(rows[-1]["reason"], "time")
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {"ca_loc": 1}})


class Integration(unittest.TestCase):
    def test_inv_01_gather_writes_inventory_quan_reads_it(self):
        """Ví dụ smoke test trong PRD-0 mục G: cập bến ở tick 0, quán đọc kho đúng nội dung."""
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"gather": {"hold": ["ca_loc", "bong_sung", "bong_sung"]}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "interact": True}))
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "gather", "--seed", "42", "--ticks", "1", "--scenario", sc,
                                     "--inputs", inp, "--inventory-out", inv, "--out", w.path("r.jsonl"))
            self.assertEqual(code, 0, err)
            with open(inv, encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(saved, {"items": {"bong_sung": 2, "ca_loc": 1}})
            end = events(read_jsonl(w.path("r.jsonl")), "gather_end")[0]["data"]
            self.assertEqual(end["reason"], "docked")
            self.assertEqual(end["inventory"], saved)
            code, err = run_headless("--mode", "quan", "--seed", "42", "--ticks", "0", "--inventory", inv,
                                     "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertEqual(snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"], {"bong_sung": 2, "ca_loc": 1})

    def test_inv_01_not_written_when_tick_limit_first(self):
        with Workdir() as w:
            inv = w.path("inv.json")
            code, _ = run_headless("--mode", "gather", "--seed", "1", "--ticks", "5", "--inventory-out", inv,
                                   "--out", w.path("r.jsonl"))
            self.assertEqual(code, 0)
            self.assertFalse(os.path.exists(inv))
            self.assertEqual(read_jsonl(w.path("r.jsonl"))[-1]["reason"], "tick_limit")

    def test_inv_bad_schema_exit_2(self):
        with Workdir() as w:
            for bad in ({"items": {"ca_la_lung": 1}}, {"items": {"ca_loc": -1}}, {"items": {}, "x": 1}):
                p = write_json(w.path("inv.json"), bad)
                self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", p,
                                              "--out", w.path("q.jsonl"))[0], 2, bad)

    def test_inventory_and_scenario_stock_conflict(self):
        with Workdir() as w:
            inv = write_json(w.path("inv.json"), {"items": {}})
            sc = write_json(w.path("sc.json"), {"quan": {"stock": {"ca_loc": 1}}})
            self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inv,
                                          "--scenario", sc, "--out", w.path("q.jsonl"))[0], 2)

    def test_inventory_flags_mode_mismatch_exit_2(self):
        with Workdir() as w:
            inv = write_json(w.path("inv.json"), {"items": {}})
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--inventory", inv,
                                          "--out", w.path("g.jsonl"))[0], 2)
            self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory-out", w.path("x.json"),
                                          "--out", w.path("q.jsonl"))[0], 2)


if __name__ == "__main__":
    unittest.main()
