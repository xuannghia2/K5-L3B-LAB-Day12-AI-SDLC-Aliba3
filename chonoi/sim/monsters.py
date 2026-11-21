"""Ticket-02 crocodiles: movement, hit eligibility and recoil timers."""

import math

from ..ids import sort_by_id


class MonsterPopulation:
    def __init__(self, tuning, scenario, ids, day=1):
        self.t = tuning.get("monsters")
        self.monsters = []
        self.can_hit = []
        if self.t is None:
            return
        source = scenario.get("monsters", [m for m in self.t["spawns"] if m["from_day"] <= day])
        for m in source:
            entry = {"id": m["id"], "kind": m["kind"], "pos": list(m["pos"]),
                     "waypoints": [list(p) for p in m["waypoints"]], "target_idx": m.get("target_idx", 1),
                     "state": m.get("state", "patrol"), "state_ticks_left": m.get("state_ticks_left", 0),
                     "recoil_dir": list(m["recoil_dir"]) if m.get("recoil_dir") is not None else None}
            self.monsters.append(entry)
            ids.reserve(m["id"])
        self.bounds = tuning["bounds"]

    def _clamp(self, m, spec):
        for i, axis in enumerate(("x", "d")):
            lo, hi = self.bounds[axis]
            if axis == "d":
                lo, hi = max(lo, spec["depths"][0]), min(hi, spec["depths"][1])
            m["pos"][i] = max(lo, min(hi, m["pos"][i]))

    def _toward(self, m, target, speed):
        distance = math.dist(m["pos"], target)
        if distance == 0:
            return True
        ratio = min(1, speed / 60 / distance)
        m["pos"] = [p + (q - p) * ratio for p, q in zip(m["pos"], target)]
        return ratio == 1

    def step(self, player_pos):
        self.can_hit = []
        if self.t is None:
            return
        for m in sort_by_id(self.monsters):
            spec = self.t["species"][m["kind"]]
            if m["state"] == "recoil":
                step_dist = spec["recoil_dist"] / spec["recoil_ticks"]
                m["pos"] = [p + v * step_dist for p, v in zip(m["pos"], m["recoil_dir"])]
                self._clamp(m, spec)
                m["state_ticks_left"] -= 1
                if m["state_ticks_left"] == 0:
                    m["state"], m["recoil_dir"] = "patrol", None
                continue  # even the final recoil step cannot detect or hit
            distance = math.dist(m["pos"], player_pos)
            deep = player_pos[1] >= spec["depths"][0]
            if m["state"] == "chase" and (not deep or distance > spec["exit_radius"]):
                m["state"] = "patrol"
            elif m["state"] == "patrol" and deep and distance <= spec["detect_radius"]:
                m["state"] = "chase"
            if m["state"] == "chase":
                self._toward(m, player_pos, spec["chase_speed"])
            else:
                if self._toward(m, m["waypoints"][m["target_idx"]], spec["patrol_speed"]):
                    m["target_idx"] = 1 - m["target_idx"]
            self._clamp(m, spec)
            if deep and math.dist(m["pos"], player_pos) <= spec["hit_radius"]:
                self.can_hit.append(m)

    def nearest_hit(self, player_pos):
        return min(self.can_hit, key=lambda m: math.dist(m["pos"], player_pos), default=None)

    def recoil(self, monster, player_pos):
        vector = [a - b for a, b in zip(monster["pos"], player_pos)]
        norm = math.hypot(*vector)
        monster["recoil_dir"] = [v / norm for v in vector] if norm else [1.0, 0.0]
        monster["state"] = "recoil"
        monster["state_ticks_left"] = self.t["species"][monster["kind"]]["recoil_ticks"]
