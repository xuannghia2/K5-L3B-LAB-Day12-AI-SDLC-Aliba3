"""Nạp và kiểm scenario (Contract D). Trả về dict của đúng khối theo mode.

KHUNG: kiểm cú pháp, id trùng, bộ đếm âm, khoang vượt sức chứa, trường lạ.
TODO(nhóm): bổ sung kiểm mâu thuẫn mức luật mà nhóm cần (khách giữ chỗ quá kho, đơn assigned
phải có đúng một món, khách eating thiếu giá/tip...) — xem PRD-0 mục D và 'Mâu thuẫn -> mã 2'.
"""

import json
import math

from .errors import BadInput
from .inventory import KINDS_P1, validate_items, validate_fresh_items

GATHER_KEYS = {"player", "hold", "nodes", "fish", "random_fish", "time_left_ticks", "monsters"}
GATHER_PLAYER_KEYS = {"pos", "vel", "heading_deg", "hp", "oxygen_ticks", "zero_oxy_ticks",
                      "invuln_ticks", "catch_cd_ticks"}
NODE_KINDS = ("bong_dien_dien", "bong_sung")
FISH_KINDS = ("ca_linh", "ca_loc")
QUAN_PLAYER_KEYS = {"pos", "vel"}
QUAN_KEYS = {"player", "stock", "hand", "stoves", "tables", "customers", "random_customers",
             "reputation", "time_left_ticks"}


def _check_ids(name, arr):
    if not isinstance(arr, list):
        raise BadInput(f"{name} phải là mảng")
    seen = set()
    for e in arr:
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not e["id"]:
            raise BadInput(f"{name}: mỗi phần tử cần id (chuỗi khác rỗng)")
        if e["id"] in seen:
            raise BadInput(f"{name}: id trùng {e['id']}")
        seen.add(e["id"])


def load_scenario(path, mode: str, tuning: dict) -> dict:
    if path is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được scenario {path}: {e}")
    if not isinstance(data, dict) or not set(data) <= {"gather", "quan"}:
        raise BadInput("scenario chỉ được có khối 'gather' hoặc 'quan'")
    if set(data) - {mode}:
        raise BadInput(f"khối sai mode: chạy --mode {mode} chỉ nhận khối '{mode}'")
    block = data.get(mode, {})
    if not isinstance(block, dict):
        raise BadInput(f"khối {mode} phải là object")
    allowed = GATHER_KEYS if mode == "gather" else QUAN_KEYS
    extra = set(block) - allowed
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong {mode}: {sorted(extra)}")
    dur = int(round(tuning[mode]["duration_s"] * 60))
    if "time_left_ticks" in block:
        t = block["time_left_ticks"]
        if isinstance(t, bool) or not isinstance(t, int) or not (1 <= t <= dur):
            raise BadInput(f"time_left_ticks phải là số nguyên trong [1, {dur}]")
    if mode == "gather":
        _validate_gather(block, tuning)
    else:
        _validate_quan(block, tuning)
    return block


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _nonneg_int(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise BadInput(f"{name} phải là số nguyên không âm")


def _pos(name, pos, bounds, axes=("x", "d")):
    if not (isinstance(pos, list) and len(pos) == 2 and all(_num(c) for c in pos)):
        raise BadInput(f"{name} phải là [{axes[0]}, {axes[1]}]")
    for c, axis in zip(pos, axes):
        lo, hi = bounds[axis]
        if not (lo <= c <= hi):
            raise BadInput(f"{name} nằm ngoài vùng nước ({axis} ∈ [{lo}, {hi}])")


def _validate_gather(b, tuning):
    g = tuning["gather"]
    bounds = g["bounds"]
    if "monsters" in b and "monsters" not in g:
        raise BadInput("monsters chưa hỗ trợ trong preset P1")
    node_kinds = set(NODE_KINDS) | ({"keo_neo"} if "monsters" in g else set())
    fish_kinds = set(g["fish_yield"])
    hold_kinds = node_kinds | fish_kinds
    for arr in ("nodes", "fish", "monsters"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "random_fish" in b and not isinstance(b["random_fish"], bool):
        raise BadInput("random_fish phải là boolean")
    if "hold" in b:
        h = b["hold"]
        if "freshness" in tuning:
            validate_fresh_items(h, hold_kinds)
        elif not isinstance(h, list) or any(not isinstance(k, str) or k not in hold_kinds for k in h):
            raise BadInput("hold phải là mảng id nguyên liệu hợp lệ")
        if len(h) > g["hold_capacity"]:
            raise BadInput("hold vượt sức chứa")
    p = b.get("player", {})
    if not isinstance(p, dict):
        raise BadInput("player phải là object")
    extra = set(p) - GATHER_PLAYER_KEYS
    if extra:
        raise BadInput(f"trường lạ/chưa hỗ trợ trong gather.player: {sorted(extra)}")
    if "pos" in p:
        _pos("player.pos", p["pos"], bounds)
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, d]")
    if "heading_deg" in p and not _num(p["heading_deg"]):
        raise BadInput("player.heading_deg phải là số")
    for key in ("invuln_ticks", "catch_cd_ticks", "zero_oxy_ticks", "oxygen_ticks", "hp"):
        if key in p:
            _nonneg_int(f"player.{key}", p[key])
    omax = int(round(g["oxygen_max_s"] * 60))
    if "oxygen_ticks" in p and p["oxygen_ticks"] > omax:
        raise BadInput("player.oxygen_ticks vượt oxy tối đa")
    if "hp" in p and not (1 <= p["hp"] <= g["hp_max"]):
        raise BadInput("player.hp phải trong [1, hp_max]")
    if "zero_oxy_ticks" in p:
        pos = p.get("pos", g["start_pos"])
        oxy = p.get("oxygen_ticks", omax)
        if p["zero_oxy_ticks"] > 59:
            raise BadInput("player.zero_oxy_ticks phải trong [0, 59]")
        if p["zero_oxy_ticks"] > 0 and not (oxy == 0 and pos[1] > g["surface_depth"]):
            raise BadInput("player.zero_oxy_ticks > 0 chỉ khi oxy = 0 và đang dưới nước")
    for n in b.get("nodes", []):
        if set(n) - {"id", "kind", "pos", "regrow_ticks"}:
            raise BadInput("trường lạ trong nodes")
        if not isinstance(n.get("kind"), str) or n["kind"] not in node_kinds:
            raise BadInput(f"nodes.{n['id']}: kind phải là một trong {NODE_KINDS}")
        _pos(f"nodes.{n['id']}.pos", n.get("pos"), bounds)
        if n["pos"][1] != 0:
            raise BadInput(f"nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
        if "regrow_ticks" in n:
            _nonneg_int(f"nodes.{n['id']}.regrow_ticks", n["regrow_ticks"])
    for f in b.get("fish", []):
        if not isinstance(f.get("kind"), str) or f["kind"] not in fish_kinds:
            raise BadInput(f"fish.{f['id']}: kind phải là một trong {FISH_KINDS}")
        _pos(f"fish.{f['id']}.pos", f.get("pos"), bounds)
        if f["pos"][1] <= g["surface_depth"]:
            raise BadInput(f"fish.{f['id']}: đàn cá phải ở dưới nước")
        if "heading_deg" in f and not _num(f["heading_deg"]):
            raise BadInput(f"fish.{f['id']}.heading_deg phải là số")

    for f in b.get("fish", []):
        allowed = {"id", "kind", "pos", "heading_deg"} | ({"age_ticks"} if "monsters" in g else set())
        if set(f) - allowed:
            raise BadInput("trường lạ trong fish")
        if "age_ticks" in f:
            _nonneg_int("fish.age_ticks", f["age_ticks"])
    for m in b.get("monsters", []):
        allowed = {"id", "kind", "pos", "waypoints", "target_idx", "state", "state_ticks_left", "recoil_dir"}
        if set(m) - allowed or not isinstance(m.get("kind"), str) or m["kind"] not in g["monsters"]["species"]:
            raise BadInput("monster kind/trường không hợp lệ")
        spec = g["monsters"]["species"][m["kind"]]
        _pos("monster.pos", m.get("pos"), bounds)
        waypoints = m.get("waypoints")
        if not isinstance(waypoints, list) or len(waypoints) != 2:
            raise BadInput("monster cần hai waypoint")
        for point in [m["pos"], *waypoints]:
            _pos("monster waypoint", point, bounds)
            if not spec["depths"][0] <= point[1] <= spec["depths"][1]:
                raise BadInput("monster ngoài độ sâu của loài")
        target = m.get("target_idx", 1)
        if isinstance(target, bool) or not isinstance(target, int) or target not in (0, 1):
            raise BadInput("target_idx phải 0 hoặc 1")
        state, timer = m.get("state", "patrol"), m.get("state_ticks_left", 0)
        _nonneg_int("monster.state_ticks_left", timer)
        if state not in ("patrol", "chase", "recoil"):
            raise BadInput("monster.state không hỗ trợ")
        vector = m.get("recoil_dir")
        if state == "recoil":
            if timer == 0 or not isinstance(vector, list) or len(vector) != 2 or not all(_num(v) and math.isfinite(v) for v in vector) or not math.isclose(math.hypot(*vector), 1, abs_tol=1e-6):
                raise BadInput("recoil cần timer dương và vector đơn vị")
        elif timer != 0 or vector is not None:
            raise BadInput("timer/recoil_dir mâu thuẫn trạng thái")


def _validate_quan(b, tuning):
    for arr in ("stoves", "tables", "customers"):
        if arr in b:
            _check_ids(arr, b[arr])
    if "stock" in b:
        validate_items(b["stock"], version="1.2" if "freshness" in tuning else "1.1")
    p = b.get("player", {})
    if not isinstance(p, dict) or set(p) - QUAN_PLAYER_KEYS:
        raise BadInput("quan.player chỉ có pos và vel")
    qb = tuning["quan"]["bounds"]
    if "pos" in p:
        _pos("player.pos", p["pos"], qb, axes=("x", "z"))
    if "vel" in p and not (isinstance(p["vel"], list) and len(p["vel"]) == 2 and all(_num(c) for c in p["vel"])):
        raise BadInput("player.vel phải là [x, z]")
    table_ids = [c.get("table_id") for c in b.get("customers", [])]
    known = {t["id"] for t in tuning["quan"]["tables"]} | {t.get("id") for t in b.get("tables", [])}
    menu = tuning.get("menu", {})
    for c in b.get("customers", []):
        if not isinstance(c.get("table_id"), str) or c["table_id"] not in known:
            raise BadInput(f"customers.{c['id']}: table_id phải là bàn có thật")
        dish_id = c.get("dish_id")
        if dish_id is not None and dish_id not in menu:
            raise BadInput(f"customers.{c['id']}: món ăn không tồn tại trong menu: {dish_id}")
    if len(table_ids) != len(set(table_ids)):
        raise BadInput("hai khách cùng bàn")

    # Kiểm tra tính nhất quán giữa kho và giữ chỗ nếu có reserved
    stock_input = b.get("stock")
    if stock_input is not None:
        stock_counts = {}
        if isinstance(stock_input, list):
            for item in stock_input:
                stock_counts[item["kind"]] = stock_counts.get(item["kind"], 0) + 1
        elif isinstance(stock_input, dict):
            stock_counts = dict(stock_input)
        
        total_reserved = {}
        for c in b.get("customers", []):
            if c.get("order_status") == "reserved" or c.get("reserved"):
                res = c.get("reserved")
                if res is None and c.get("dish_id") in menu:
                    res = menu[c["dish_id"]]["recipe"]
                if isinstance(res, dict):
                    for k, q in res.items():
                        total_reserved[k] = total_reserved.get(k, 0) + q
                elif isinstance(res, list):
                    # res có thể là list id hoặc items
                    pass
        for k, q in total_reserved.items():
            if stock_counts.get(k, 0) < q:
                raise BadInput(f"kho không đủ cho lượng hàng đã giữ chỗ: {k} cần {q} nhưng kho chỉ có {stock_counts.get(k, 0)}")
