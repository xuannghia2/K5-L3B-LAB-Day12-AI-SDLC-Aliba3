"""Buổi sáng — Lặn & Hái (`gather`). KHUNG: bơi, chặn mép, đồng hồ, cập bến, xuất kho.

Mặt cắt dòng sông nhìn NGANG: vị trí `[x, d]` (x sang phải, `d` độ sâu hướng xuống, d = 0 là mặt nước).
`move = [x, d]`: thành phần thứ hai DƯƠNG = bơi xuống. Hướng mặt là góc từ +x, dương = xuống.

Phase 1: bơi, oxy, ngạt/ngất, giỏ, hái nút, bắt cá, cập bến và hết giờ.
Mọi định lượng đọc từ tuning; danh sách bằng khoảng cách được ưu tiên theo id tự nhiên.
Xem docs/gather-xuannghia2.md cho phạm vi và kết quả đối chiếu PRD-0 mục E/F/G.
Các tính năng của phase sau chưa nằm trong khung này.
"""

import math

from ..ids import sort_by_id
from ..inventory import hold_to_items
from ..freshness import FreshnessLedger, copy_items
from .ramp import ramp_velocity
from .fish import FishPopulation
from .monsters import MonsterPopulation

TICK = 60.0
AXES = ("x", "d")


class GatherSim:
    mode = "gather"
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids, *, day=1, active_upgrades=None):
        t = dict(tuning["gather"])
        for kind, level in (active_upgrades or {}).items():
            if kind not in ("oxygen", "hp") or level == 0:
                continue
            rows = tuning.get("shop", {}).get("upgrades", {}).get(kind, [])
            entry = next((row for row in rows if row["level"] == level), None)
            if entry is None:
                from ..errors import BadInput
                raise BadInput(f"unsupported active upgrade: {kind}={level}")
            key = "oxygen_max_s" if kind == "oxygen" else "hp_max"
            t[key] = entry[key]
        self.t = t
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.heading = float(p.get("heading_deg", t["start_heading_deg"]))
        self.oxygen_max = int(round(t["oxygen_max_s"] * TICK))
        self.oxygen_ticks = p.get("oxygen_ticks", self.oxygen_max)
        self.hp = p.get("hp", t["hp_max"])
        self.zero_oxy_ticks = p.get("zero_oxy_ticks", 0)
        self.invuln_ticks = p.get("invuln_ticks", 0)
        self.catch_cd_ticks = p.get("catch_cd_ticks", 0)
        self.freshness = FreshnessLedger(tuning, ids) if "freshness" in tuning else None
        self.hold = (self.freshness.attach(scenario.get("hold", [])) if self.freshness
                     else list(scenario.get("hold", [])))  # newest pickup is last
        self.phase_tick = 0
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        # nút và đàn cá: scenario THAY THẾ danh sách mặc định; random_fish=false tắt cá mặc định
        src_nodes = scenario["nodes"] if "nodes" in scenario else t["nodes"]
        self.nodes = [{"id": n["id"], "kind": n["kind"], "pos": [float(c) for c in n["pos"]],
                       "regrow_ticks": n.get("regrow_ticks", 0)} for n in src_nodes]
        self.fish_population = None
        if isinstance(t["fish_initial"], int):
            self.fish_population = FishPopulation(t, scenario, streams, ids)
            self.fish = self.fish_population.fish
        else:  # P1 presets remain playable with their stationary schools.
            src_fish = scenario.get("fish", t["fish_initial"] if scenario.get("random_fish", True) else [])
            self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                          "heading_deg": f.get("heading_deg", 0)} for f in src_fish]
        for coll in (self.nodes, self.fish):
            for e in coll:
                ids.reserve(e["id"])
        self.monster_population = MonsterPopulation(t, scenario, ids, day)
        self.monsters = self.monster_population.monsters
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def inventory_items(self):
        return copy_items(self.hold, sorted_ids=True) if self.freshness else hold_to_items(self.hold)

    def _lost_items(self, values):
        return copy_items(values) if self.freshness else list(values)

    def snapshot(self) -> dict:
        return {
            "player": {"pos": self.pos, "vel": self.vel, "heading_deg": self.heading,
                       "oxygen_ticks": self.oxygen_ticks, "oxygen_max_ticks": self.oxygen_max,
                       "hp": self.hp, "hp_max": self.t["hp_max"], "zero_oxy_ticks": self.zero_oxy_ticks,
                       "invuln_ticks": self.invuln_ticks, "catch_cd_ticks": self.catch_cd_ticks,
                       "at_surface": self._at_surface()},
            **({"monsters": [dict(m) for m in sort_by_id(self.monsters)]} if self.monster_population.t else {}),
            "hold": copy_items(self.hold) if self.freshness else list(self.hold), "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [{"id": n["id"], "pos": n["pos"], "kind": n["kind"],
                       "ready": n["regrow_ticks"] == 0, "regrow_ticks": n["regrow_ticks"]}
                      for n in sort_by_id(self.nodes)],
            "fish": [{"id": f["id"], "pos": f["pos"], "kind": f["kind"], "heading_deg": f["heading_deg"],
                      **({"age_ticks": f["age_ticks"]} if "age_ticks" in f else {})}
                     for f in sort_by_id(self.fish)],
        }

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        if self.done:
            return []
        events = []
        # 1. đồng hồ và hàng có sẵn: giảm bộ đếm, nút mọc lại
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.invuln_ticks = max(0, self.invuln_ticks - 1)
        self.catch_cd_ticks = max(0, self.catch_cd_ticks - 1)
        for n in sort_by_id(self.nodes):
            if n["regrow_ticks"] > 0:
                n["regrow_ticks"] -= 1
                if n["regrow_ticks"] == 0:
                    events.append(("node_regrown", {"node_id": n["id"]}))
        if self.freshness:
            events.extend(self.freshness.decay(self.hold, "hold"))
        # 2. bơi, phân vùng, oxy và ngạt (xét vị trí CUỐI bước).
        was_at_surface = self._at_surface()
        self._move(inp)
        at_surface = self._at_surface()
        if was_at_surface != at_surface:
            events.append(("surface" if at_surface else "dive", {"pos": list(self.pos)}))
        if at_surface:
            self.oxygen_ticks = min(self.oxygen_max, self.oxygen_ticks + self.t["oxygen_refill_per_tick"])
            self.zero_oxy_ticks = 0
        else:
            previous_oxygen = self.oxygen_ticks
            self.oxygen_ticks = max(0, self.oxygen_ticks - 1)
            if previous_oxygen > 0 and self.oxygen_ticks == 0:
                events.append(("oxygen_empty", {"oxygen_ticks": 0}))
            if self.oxygen_ticks == 0:
                self.zero_oxy_ticks += 1
                if self.zero_oxy_ticks >= self.t["choke_interval_ticks"]:
                    self.zero_oxy_ticks = 0
                    self.hp = max(0, self.hp - 1)
                    events.append(("choke", {"hp": self.hp}))
                    if self.hp == 0:
                        lost = self._lost_items(reversed(self.hold))
                        self.hold.clear()
                        events.append(("faint", {"cause": "choke", "lost": lost, "hp": 0}))
                        self._finish("fainted", events)
                        return events
            else:
                self.zero_oxy_ticks = 0
        # P2: all monsters move before at most one hit; choking was processed first.
        self.monster_population.step(self.pos)
        monster = self.monster_population.nearest_hit(self.pos)
        if monster is not None and self.invuln_ticks == 0:
            config = self.monster_population.t
            self.hp = max(0, self.hp - 1)
            lost = self._lost_items(self.hold.pop() for _ in range(math.floor(len(self.hold) * config["loss_ratio"])))
            self.invuln_ticks = config["invuln_ticks"]
            self.monster_population.recoil(monster, self.pos)
            events.append(("monster_hit", {"monster_id": monster["id"], "hp": self.hp,
                                           "lost": lost, "pos": list(self.pos)}))
            if self.hp == 0:
                remaining = self._lost_items(reversed(self.hold))
                self.hold.clear()
                events.append(("faint", {"cause": "monster", "lost": remaining, "hp": 0}))
                self._finish("fainted", events)
                return events
        # 3. interact: bến trước, rồi hái
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events
            if self._at_surface():
                node = self._nearest((n for n in self.nodes if n["regrow_ticks"] == 0),
                                     self.t["interact_radius"])
                if node is not None and self._collect(node, self.t["node_yield"], "gather", "node_id", events):
                    node["regrow_ticks"] = int(round(self.t["regrow_s"] * TICK))
        # 4. chỉ bắt một đàn cá gần nhất, dưới nước, khi hết hồi chiêu.
        if inp.pressed("catch") and not self._at_surface() and self.catch_cd_ticks == 0:
            fish = self._nearest(self.fish, self.t["catch_radius"])
            if fish is not None and self._collect(fish, self.t["fish_yield"][fish["kind"]],
                                                 "fish_caught", "fish_id", events):
                self.fish.remove(fish)
                self.catch_cd_ticks = int(round(self.t["catch_cooldown_s"] * TICK))
        # 5. hết giờ
        if self.time_left_ticks <= 0:
            self._finish("time", events)
        elif self.fish_population is not None:
            self.fish_population.step(self.phase_tick, events)
        return events

    # --- tiện ích ---------------------------------------------------------------
    def _nearest(self, entities, radius):
        # min giữ phần tử đầu khi bằng nhau: sắp id trước để F2 thắng F10.
        candidates = [e for e in sort_by_id(entities) if math.dist(self.pos, e["pos"]) <= radius]
        return min(candidates, key=lambda e: math.dist(self.pos, e["pos"]), default=None)

    def _collect(self, entity, quantity, name, id_field, events):
        free = self.t["hold_capacity"] - len(self.hold)
        if quantity > free:
            events.append(("hold_full", {"action": "gather" if name == "gather" else "catch",
                                         id_field: entity["id"], "required": quantity, "free": free}))
            return False
        if self.freshness:
            self.hold.extend(self.freshness.new(entity["kind"]) for _ in range(quantity))
        else:
            self.hold.extend([entity["kind"]] * quantity)
        amount_field = "amount" if name == "gather" else "yield"
        events.append((name, {id_field: entity["id"], "kind": entity["kind"], amount_field: quantity}))
        return True

    def _at_surface(self) -> bool:
        return self.pos[1] <= self.t["surface_depth"]

    def _in_dock(self) -> bool:
        return math.dist(self.pos, self.t["dock_pos"]) <= self.t["dock_radius"]

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("gather_end", {"reason": reason, "inventory": {"items": self.inventory_items()}}))

    def _move(self, inp):
        speed = self.t["swim_speed"]
        mx, md = inp.move
        self.vel = ramp_velocity(self, (mx * speed, md * speed), int(self.t["ramp_max_ticks"]))
        if (mx, md) != (0.0, 0.0):
            self.heading = math.degrees(math.atan2(md, mx)) % 360
        b = self.t["bounds"]
        for i, axis in enumerate(AXES):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i] = lo
                self.vel[i] = max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i] = hi
                self.vel[i] = min(0.0, self.vel[i])
