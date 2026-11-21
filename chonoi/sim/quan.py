"""Buổi tối — Mở Quán. Tuân thủ chính xác PRD-0 và Test Contract v1.0.

Thứ tự xử lý trong một bước (PRD-0 mục F):
  1. Tăng đồng hồ, giảm timer ca, nấu, ăn và kiên nhẫn.
     - Chỉ tăng ready_ticks cho món đã ready ở đầu bước.
     - Món nấu xong chuyển ready với ready_ticks = 0.
  2. Di chuyển rồi xét tối đa một interact (khoảng cách, bếp trước bàn, id).
     - Bếp idle lấy đơn reserved cũ nhất (order_tick rồi id bàn), tiêu nguyên liệu giữ, chốt giá, bắt đầu nấu (cook_started).
     - Bếp ready giao món cho tay trống và về idle (dish_picked).
     - Bàn nhận đúng order_id thì khách ăn với timer đầy (served). Chốt boa = floor(tiền món * tip_rate) nếu kiên nhẫn còn lại sau bước 1 đạt tip_min_patience_ratio.
  3. Theo id bàn, khách ăn xong trả tiền (paid) rồi rời bàn ngay.
     - Ca còn giờ: khách waiting có kiên nhẫn 0 rời (customer_left, reason="patience", trừ uy tín).
     - Hết ca: khách còn ăn trả ngay (closing), khách còn chờ rời (customer_left, reason="closing", không trừ uy tín).
     - Dọn xong phát quan_end. Bỏ món của đơn đang nấu, ready hoặc trên tay khi khách rời.
  4. Nếu còn giờ, xét lượt khách theo first_customer_tick, rồi mỗi customer_interval_s * 60 tick.
     - Bàn trống id nhỏ nhất.
     - Chọn đều theo seed trong các món đủ nguyên liệu khả dụng (stock - reserved). Không đủ -> no_dish.
     - Khách mới: order_id = id khách, order_tick = phase_tick hiện tại, kiên nhẫn đầy, giảm từ bước sau.
"""

import math
from ..ids import sort_by_id
from ..freshness import FreshnessLedger, copy_items
from .ramp import ramp_velocity

TICK = 60.0


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.random_customers = scenario.get("random_customers", True)
        self.freshness = FreshnessLedger(tuning, ids) if "freshness" in tuning else None

        # kho: --inventory HOẶC scenario.stock
        raw_inv = inventory if inventory is not None else scenario.get("stock", {})
        if isinstance(raw_inv, list):
            self.is_fresh_inventory = True
            if self.freshness is None:
                self.freshness = FreshnessLedger(tuning, ids)
            self.stock_items = self.freshness.attach(raw_inv)
            self.stock = {}
        elif isinstance(raw_inv, dict):
            self.is_fresh_inventory = False
            self.stock_items = []
            self.stock = dict(raw_inv)
        else:
            self.is_fresh_inventory = False
            self.stock_items = []
            self.stock = {}

        self.hand = scenario.get("hand")  # payload: {order_id, dish_id, base_price} hoặc null
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * 60)))
        self.phase_tick = 0
        self.reputation = float(scenario.get("reputation", t["reputation_initial"]))
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            order_id=s.get("order_id"), base_price=s.get("base_price"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))

        self.customers = []
        for c in scenario.get("customers", []):
            item = dict(c)
            oid = item.get("order_id", item["id"])
            item["order_id"] = oid
            if "state" not in item:
                item["state"] = "eating" if item.get("eat_ticks_left", 0) > 0 else "waiting"
            dish = item.get("dish_id")
            price = self.menu[dish]["price"] if dish in self.menu else 0
            item["base_price"] = item.get("base_price", price)
            if "order_status" not in item and item["state"] == "waiting":
                item["order_status"] = "reserved"
            if "reserved" not in item:
                if dish and dish in self.menu and item["state"] == "waiting":
                    if self.is_fresh_inventory:
                        # Trong kho cá thể, ban đầu để reserved_items
                        item["reserved"] = dict(self.menu[dish]["recipe"])
                    else:
                        item["reserved"] = dict(self.menu[dish]["recipe"])
                else:
                    item["reserved"] = {}
            if "patience_ticks_left" not in item and item["state"] == "waiting":
                item["patience_ticks_left"] = int(round(t["patience_s"] * 60))
            item["patience_max_ticks"] = int(round(t["patience_s"] * 60))
            if "order_tick" not in item:
                item["order_tick"] = 0
            self.customers.append(item)
            ids.reserve(item["id"])

        # Nếu là kho cá thể, phân bổ id cá thể cho các đơn reserved sẵn từ scenario
        if self.is_fresh_inventory:
            for c in self.customers:
                if c.get("state") == "waiting" and c.get("order_status") == "reserved":
                    dish = c.get("dish_id")
                    if dish and dish in self.menu and not c.get("reserved_item_ids"):
                        ok = self._assign_fresh_reserved(c)
                        if not ok:
                            c["order_status"] = "unfulfillable"

        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                from ..errors import BadInput
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        # Sắp mảng thực thể theo id
        stoves_out = []
        for s in sort_by_id(self.stoves):
            st_dict = {
                "id": s["id"],
                "pos": s["pos"],
                "state": s["state"],
                "dish": s.get("dish"),
                "cook_ticks_left": s.get("cook_ticks_left", 0),
                "ready_ticks": s.get("ready_ticks", 0)
            }
            if s.get("order_id"):
                st_dict["order_id"] = s["order_id"]
            if s.get("base_price"):
                st_dict["base_price"] = s["base_price"]
            stoves_out.append(st_dict)

        if self.is_fresh_inventory:
            stock_data = copy_items(self.stock_items, sorted_ids=True)
        else:
            stock_data = {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0}

        return {
            "player": {"pos": [round(c, 3) for c in self.pos], "vel": [round(c, 3) for c in self.vel]},
            "stock": stock_data,
            "hand": self.hand,
            "stoves": stoves_out,
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])}
                       for tb in sort_by_id(self.tables)],
            "customers": sort_by_id(self.customers),
        }

    def _available_stock(self) -> dict:
        if self.is_fresh_inventory:
            reserved_ids = set()
            for c in self.customers:
                for item_id in c.get("reserved_item_ids", []):
                    reserved_ids.add(item_id)
            avail = {}
            for item in self.stock_items:
                if item["id"] not in reserved_ids and not self.freshness.spoiled(item):
                    avail[item["kind"]] = avail.get(item["kind"], 0) + 1
            return avail
        else:
            avail = dict(self.stock)
            for c in self.customers:
                for k, qty in c.get("reserved", {}).items():
                    avail[k] = avail.get(k, 0) - qty
            return avail

    def _can_cook_dish(self, dish_id: str, avail: dict) -> bool:
        recipe = self.menu[dish_id]["recipe"]
        return all(avail.get(k, 0) >= qty for k, qty in recipe.items())

    def _assign_fresh_reserved(self, cust) -> bool:
        dish_id = cust["dish_id"]
        recipe = self.menu[dish_id]["recipe"]
        # Lấy tất cả item khả dụng (chưa reserved bởi khách khác và chưa spoiled)
        other_reserved = set()
        for c in self.customers:
            if c["id"] != cust["id"]:
                for iid in c.get("reserved_item_ids", []):
                    other_reserved.add(iid)

        available_items = [it for it in self.stock_items if it["id"] not in other_reserved and not self.freshness.spoiled(it)]

        selected_ids = []
        for kind, count in recipe.items():
            matching = [it for it in available_items if it["kind"] == kind and it["id"] not in selected_ids]
            if len(matching) < count:
                return False
            # Sắp theo fresh giảm dần, hòa theo id tự nhiên
            matching = sort_by_id(matching)
            matching.sort(key=lambda it: it["fresh"], reverse=True)
            selected_ids.extend([it["id"] for it in matching[:count]])

        cust["reserved_item_ids"] = selected_ids
        cust["reserved"] = dict(recipe)
        return True

    def _clean_customer_dish(self, order_id):
        """Bỏ món của đơn đang nấu, ready hoặc trên tay khi khách rời."""
        # Nhả giữ chỗ nếu khách bị hủy
        for c in self.customers:
            if c.get("order_id") == order_id:
                c["reserved_item_ids"] = []
                c["reserved"] = {}
        for s in self.stoves:
            if s.get("order_id") == order_id:
                s["state"] = "idle"
                s["dish"] = None
                s["order_id"] = None
                s["base_price"] = None
                s["cook_ticks_left"] = 0
                s["ready_ticks"] = 0
        if self.hand and isinstance(self.hand, dict) and self.hand.get("order_id") == order_id:
            self.hand = None
        elif self.hand and isinstance(self.hand, str):
            pass

    def step(self, inp):
        events = []
        self.phase_tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        closing = (self.time_left_ticks == 0)

        # -------------------------------------------------------------
        # 0. Hao tươi trong kho (v1.2) đầu tick trước khi di chuyển / interact
        # -------------------------------------------------------------
        if self.is_fresh_inventory and self.freshness:
            decay_events = self.freshness.decay(self.stock_items, "stock")
            events.extend(decay_events)
            # Kiểm tra nếu có cá thể trong reserved bị ươn
            spoiled_ids = {e[1]["item_id"] for e in decay_events if e[0] == "spoiled"}
            if spoiled_ids:
                # Xử lý các đơn bị ảnh hưởng theo order_tick rồi id bàn
                affected = [c for c in self.customers if c.get("state") == "waiting" and
                            any(iid in spoiled_ids for iid in c.get("reserved_item_ids", []))]
                affected.sort(key=lambda c: (c.get("order_tick", 0), c.get("table_id", "")))
                for c in affected:
                    # Nhả toàn bộ phần giữ của đơn và thử giữ lại đúng một lần
                    c["reserved_item_ids"] = []
                    c["reserved"] = {}
                    ok = self._assign_fresh_reserved(c)
                    if not ok:
                        c["order_status"] = "unfulfillable"

        # -------------------------------------------------------------
        # 1. Tăng đồng hồ, giảm timer ca, nấu, ăn và kiên nhẫn.
        # -------------------------------------------------------------
        # Chỉ tăng ready_ticks cho món đã ready ở đầu bước
        for s in sort_by_id(self.stoves):
            if s["state"] == "ready":
                s["ready_ticks"] = s.get("ready_ticks", 0) + 1
            elif s["state"] == "cooking":
                s["cook_ticks_left"] -= 1
                if s["cook_ticks_left"] <= 0:
                    s["state"] = "ready"
                    s["cook_ticks_left"] = 0
                    s["ready_ticks"] = 0
                    events.append(("dish_ready", {
                        "stove_id": s["id"],
                        "order_id": s["order_id"],
                        "dish_id": s["dish"]
                    }))

        # Giảm kiên nhẫn và timer ăn
        for c in sort_by_id(self.customers):
            if c["state"] == "waiting":
                c["patience_ticks_left"] -= 1
            elif c["state"] == "eating":
                c["eat_ticks_left"] -= 1

        # -------------------------------------------------------------
        # 2. Di chuyển rồi xét tối đa một interact
        # -------------------------------------------------------------
        self._move(inp)

        if inp.pressed("interact"):
            self._handle_interact(events)

        # -------------------------------------------------------------
        # 3. Theo id bàn: xử lý khách ăn xong, hoặc kiên nhẫn 0, hoặc đóng ca
        # -------------------------------------------------------------
        remaining_customers = []
        # Sắp xếp duyệt theo id bàn
        cust_by_table = sorted(self.customers, key=lambda c: c.get("table_id", ""))

        for c in cust_by_table:
            tb_id = c["table_id"]
            oid = c["order_id"]
            dish_id = c["dish_id"]
            base_price = c.get("base_price", self.menu[dish_id]["price"])
            tip = c.get("tip", 0)

            # Trường hợp A: Khách ăn xong (eat_ticks_left <= 0) hoặc hết ca khi đang ăn
            if c["state"] == "eating" and (c["eat_ticks_left"] <= 0 or closing):
                reason = "finished_eating" if c["eat_ticks_left"] <= 0 else "closing"
                amount = base_price + tip
                self.money += amount
                self.earned += amount
                self.shift_earned += amount
                if tip > 0:
                    self.reputation = max(self.t["reputation_min"],
                                          min(self.t["reputation_max"],
                                              self.reputation + self.t["tip_reputation"]))
                events.append(("paid", {
                    "order_id": oid,
                    "table_id": tb_id,
                    "base_price": base_price,
                    "tip": tip,
                    "amount": amount,
                    "reason": reason
                }))
                self._clean_customer_dish(oid)
                continue

            # Trường hợp B: Khách waiting kiên nhẫn = 0 khi ca còn giờ
            if c["state"] == "waiting" and c["patience_ticks_left"] <= 0 and not closing:
                self.reputation = max(self.t["reputation_min"],
                                      min(self.t["reputation_max"],
                                          self.reputation + self.t["left_reputation_delta"]))
                events.append(("customer_left", {
                    "order_id": oid,
                    "table_id": tb_id,
                    "reason": "patience",
                    "reputation": self.reputation
                }))
                # Nhả phần giữ thô và bỏ món liên quan
                self._clean_customer_dish(oid)
                continue

            # Trường hợp C: Hết ca (closing) và khách vẫn đang chờ
            if closing and c["state"] == "waiting":
                events.append(("customer_left", {
                    "order_id": oid,
                    "table_id": tb_id,
                    "reason": "closing",
                    "reputation": self.reputation
                }))
                self._clean_customer_dish(oid)
                continue

            remaining_customers.append(c)

        self.customers = remaining_customers

        # -------------------------------------------------------------
        # 4. Nếu ca hết giờ -> quan_end
        # -------------------------------------------------------------
        if closing:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {
                "reason": "time",
                "money": self.money,
                "earned": self.earned,
                "shift_earned": self.shift_earned,
                "reputation": self.reputation
            }))
            return events

        # -------------------------------------------------------------
        # 5. Khách mới theo lịch nếu ca còn giờ
        # -------------------------------------------------------------
        self._spawn_customer_if_scheduled(events)

        return events

    def _spawn_customer_if_scheduled(self, events):
        if not self.random_customers:
            return

        first_tick = self.t["first_customer_tick"]
        interval = int(round(self.t["customer_interval_s"] * 60))

        # Xét lịch theo phase_tick
        is_spawn_time = False
        if self.phase_tick == first_tick:
            is_spawn_time = True
        elif self.phase_tick > first_tick and interval > 0:
            if (self.phase_tick - first_tick) % interval == 0:
                is_spawn_time = True

        if not is_spawn_time:
            return

        occupied_tables = {c["table_id"] for c in self.customers}
        free_tables = [tb for tb in sort_by_id(self.tables) if tb["id"] not in occupied_tables]
        if not free_tables:
            return  # Không còn bàn thì bỏ lượt

        table = free_tables[0]
        avail = self._available_stock()

        cookable = [d for d in sorted(self.menu.keys()) if self._can_cook_dish(d, avail)]
        if not cookable:
            events.append(("no_dish", {}))
            return

        stream = self.rng.get("customer")
        dish_id = stream.choice(cookable) if len(cookable) > 1 else cookable[0]

        cid = self.ids.new("C")
        recipe = self.menu[dish_id]["recipe"]
        pat_ticks = int(round(self.t["patience_s"] * 60))

        cust = {
            "id": cid,
            "order_id": cid,
            "table_id": table["id"],
            "dish_id": dish_id,
            "order_tick": self.phase_tick,
            "state": "waiting",
            "order_status": "reserved",
            "patience_ticks_left": pat_ticks,
            "patience_max_ticks": pat_ticks,
            "reserved": dict(recipe),
            "base_price": self.menu[dish_id]["price"],
            "tip": 0
        }
        if self.is_fresh_inventory:
            self._assign_fresh_reserved(cust)

        self.customers.append(cust)
        events.append(("customer_arrived", {
            "order_id": cid,
            "table_id": table["id"],
            "dish_id": dish_id
        }))

    def _handle_interact(self, events):
        r = self.t["interact_radius"]
        candidates = []
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d <= r:
                candidates.append((d, 0, s["id"], "stove", s))
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d <= r:
                candidates.append((d, 1, tb["id"], "table", tb))
        if not candidates:
            return

        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        _, _, _, kind, target = candidates[0]

        if kind == "stove":
            s = target
            if s["state"] == "ready":
                if self.hand is None:
                    dish_payload = {
                        "order_id": s["order_id"],
                        "dish_id": s["dish"],
                        "base_price": s["base_price"]
                    }
                    self.hand = dish_payload
                    s["state"] = "idle"
                    s["dish"] = None
                    oid = s["order_id"]
                    dish_name = dish_payload["dish_id"]
                    s["order_id"] = None
                    s["base_price"] = None
                    s["ready_ticks"] = 0
                    events.append(("dish_picked", {
                        "stove_id": s["id"],
                        "order_id": oid,
                        "dish_id": dish_name
                    }))
            elif s["state"] == "idle":
                # Lấy đơn reserved cũ nhất theo order_tick rồi id bàn
                reserved_custs = [c for c in self.customers if c.get("order_status") == "reserved" and c["state"] == "waiting"]
                if reserved_custs:
                    reserved_custs.sort(key=lambda c: (c.get("order_tick", 0), c.get("table_id", "")))
                    chosen_customer = reserved_custs[0]
                    dish_id = chosen_customer["dish_id"]
                    recipe = self.menu[dish_id]["recipe"]

                    cook_ticks = int(round(self.menu[dish_id]["cook_s"] * 60))

                    if self.is_fresh_inventory:
                        # Tiêu đúng các id cá thể đang giữ
                        used_ids = set(chosen_customer.get("reserved_item_ids", []))
                        used_items = [it for it in self.stock_items if it["id"] in used_ids]
                        # Xóa khỏi kho quán
                        self.stock_items = [it for it in self.stock_items if it["id"] not in used_ids]
                        chosen_customer["reserved_item_ids"] = []
                        chosen_customer["reserved"] = {}
                        chosen_customer["order_status"] = "assigned"

                        # Tính giá theo tươi: math.floor(giá niêm yết * trung bình fresh của các cá thể dùng / 100)
                        if used_items:
                            avg_fresh = sum(it["fresh"] for it in used_items) / len(used_items)
                        else:
                            avg_fresh = 100.0
                        base_price = math.floor(self.menu[dish_id]["price"] * avg_fresh / 100)
                        chosen_customer["base_price"] = base_price

                        # items payload trong cook_started: mảng cá thể sắp theo kind rồi id
                        used_items_sorted = sorted(used_items, key=lambda it: (it["kind"], it["id"]))
                        items_consumed = copy_items(used_items_sorted)
                    else:
                        # Tiêu đúng nguyên liệu giữ (kho đếm)
                        for k, qty in recipe.items():
                            self.stock[k] = self.stock.get(k, 0) - qty
                        chosen_customer["reserved"] = {}
                        chosen_customer["order_status"] = "assigned"
                        base_price = self.menu[dish_id]["price"]

                        # cook_started items theo kind đã sắp xếp
                        items_consumed = []
                        for k in sorted(recipe.keys()):
                            items_consumed.extend([k] * recipe[k])

                    s["state"] = "cooking"
                    s["dish"] = dish_id
                    s["order_id"] = chosen_customer["order_id"]
                    s["base_price"] = base_price
                    s["cook_ticks_left"] = cook_ticks
                    s["ready_ticks"] = 0

                    events.append(("cook_started", {
                        "stove_id": s["id"],
                        "order_id": chosen_customer["order_id"],
                        "dish_id": dish_id,
                        "items": items_consumed,
                        "base_price": base_price
                    }))
        elif kind == "table":
            tb = target
            cust = next((c for c in self.customers if c["table_id"] == tb["id"]), None)
            if cust and cust["state"] == "waiting":
                hand_oid = self.hand.get("order_id") if isinstance(self.hand, dict) else None
                if hand_oid == cust["order_id"]:
                    self.hand = None
                    cust["state"] = "eating"
                    cust["order_status"] = "served"
                    cust["eat_ticks_left"] = int(round(self.t["eat_s"] * 60))

                    # Chốt boa bằng floor(tiền món * tip_rate) nếu tỷ lệ kiên nhẫn còn lại sau bước 1 đạt tip_min_patience_ratio
                    pat_ratio = cust["patience_ticks_left"] / cust["patience_max_ticks"]
                    base_price = cust["base_price"]
                    tip = math.floor(base_price * self.t["tip_rate"]) if pat_ratio >= self.t["tip_min_patience_ratio"] else 0
                    cust["tip"] = tip

                    events.append(("served", {
                        "order_id": cust["order_id"],
                        "table_id": tb["id"],
                        "dish_id": cust["dish_id"],
                        "patience_ticks_left": cust["patience_ticks_left"],
                        "base_price": base_price,
                        "tip": tip
                    }))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])


