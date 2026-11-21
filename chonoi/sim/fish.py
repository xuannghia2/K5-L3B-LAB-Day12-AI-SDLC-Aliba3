"""Seeded swimming/spawning schools for Ticket-02, independent of the renderer."""

import math

from ..ids import sort_by_id


def reflect_motion(pos, heading, distance, x_bounds, depth_bounds):
    """Reflect the remaining travel, including exact-edge/corner arrivals."""
    angle = math.radians(heading)
    velocity = [math.cos(angle), math.sin(angle)]
    result = []
    for coordinate, component, (lo, hi) in zip(pos, velocity, (x_bounds, depth_bounds)):
        value = coordinate + component * distance
        while value < lo or value > hi:
            if value < lo:
                value = 2 * lo - value
                component = -component
            if value > hi:
                value = 2 * hi - value
                component = -component
        if (value == lo and component < 0) or (value == hi and component > 0):
            component = -component
        result.append((value, component))
    return [r[0] for r in result], math.degrees(math.atan2(result[1][1], result[0][1])) % 360


class FishPopulation:
    def __init__(self, tuning, scenario, streams, ids):
        self.t, self.streams, self.ids = tuning, streams, ids
        self.enabled = scenario.get("random_fish", True)
        self.fish = [dict(id=f["id"], kind=f["kind"], pos=list(f["pos"]),
                          heading_deg=f.get("heading_deg", 0), age_ticks=f.get("age_ticks", 0))
                     for f in scenario.get("fish", [])]
        for f in self.fish:
            ids.reserve(f["id"])
        if "fish" not in scenario and self.enabled:
            for _ in range(tuning["fish_initial"]):
                if self.spawn() is None:
                    break

    def spawn(self):
        if len(self.fish) >= self.t["fish_max"]:
            return None
        candidates = {}
        for kind in sorted(self.t["fish_weights"]):
            points = [[x, depth] for x in self.t["fish_spawn_x"]
                      for depth in self.t["fish_spawn_depths"][kind]]
            valid = [p for p in points if all(math.dist(p, f["pos"]) > self.t["fish_spawn_clearance"]
                                              for f in self.fish)]
            if valid:
                candidates[kind] = valid
        if not candidates:
            return None
        rng = self.streams.get("fish_spawn")
        kinds = sorted(candidates)
        kind = rng.choices(kinds, weights=[self.t["fish_weights"][k] for k in kinds], k=1)[0]
        fish = {"id": self.ids.new("F"), "kind": kind, "pos": list(rng.choice(candidates[kind])),
                "heading_deg": rng.uniform(0, 360), "age_ticks": 0}
        self.fish.append(fish)
        return fish

    def step(self, phase_tick, events):
        if not self.enabled:
            return
        for fish in sort_by_id(self.fish):
            fish["age_ticks"] += 1
            if fish["age_ticks"] % self.t["fish_turn_ticks"] == 0:
                fish["heading_deg"] = self.streams.get("fish_turn").uniform(0, 360)
            fish["pos"], fish["heading_deg"] = reflect_motion(
                fish["pos"], fish["heading_deg"], self.t["fish_speed"] / 60,
                self.t["fish_x"], self.t["fish_depths"][fish["kind"]])
        if phase_tick % self.t["fish_spawn_ticks"] == 0:
            fish = self.spawn()
            if fish is not None:
                events.append(("fish_spawned", {"id": fish["id"], "kind": fish["kind"], "pos": list(fish["pos"])}))
