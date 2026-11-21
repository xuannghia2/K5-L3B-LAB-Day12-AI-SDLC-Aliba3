"""Produce honest opt-in v1.2 gather evidence; do not edit the shared manifest."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chonoi import headless
from chonoi.contract import load_contract
from chonoi.inventory import read_inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    destination = Path(args.out).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    current = load_contract()
    profile = copy.deepcopy(current)
    profile["contract_version"] = "1.2"
    profile["tuning"]["freshness"] = json.loads((root / "data/freshness-p3.json").read_text())
    (destination / "gather-test-profile.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    base = {"random_fish": False, "monsters": []}
    cases = {
        "threshold": ({**base, "hold": [{"id": "I1", "kind": "ca_linh", "fresh": 30}]}, [], 2),
        "dock": ({**base, "hold": [{"id": "I10", "kind": "ca_keo", "fresh": 100},
                                    {"id": "I2", "kind": "keo_neo", "fresh": 29.9999}]},
                 [{"tick": 0, "interact": True}], 1),
        "pickup": ({**base, "player": {"pos": [20, 0]},
                    "hold": [{"id": "I20", "kind": "ca_loc", "fresh": 50}],
                    "nodes": [{"id": "N1", "kind": "keo_neo", "pos": [20, 0]}]},
                   [{"tick": 0, "interact": True}, {"tick": 1, "interact": False}], 2),
        "faint": ({"random_fish": False, "player": {"pos": [60, 24], "hp": 1},
                   "hold": [{"id": "I20", "kind": "ca_loc", "fresh": 100},
                            {"id": "I2", "kind": "keo_neo", "fresh": 50},
                            {"id": "I7", "kind": "ca_keo", "fresh": 30}]}, [], 5),
    }
    cases["pickup-repeat"] = copy.deepcopy(cases["pickup"])
    report = {"shared_manifest_version": current["contract_version"], "test_profile_version": "1.2",
              "note": "Only this verification process selects the v1.2 profile; not a live two-process quan integration.",
              "cases": {}}
    original = headless.load_contract
    try:
        headless.load_contract = lambda: copy.deepcopy(profile)
        for name, (scenario, frames, ticks) in cases.items():
            sc, inp, out, inv = [destination / (name + suffix) for suffix in
                                ("-scenario.json", "-inputs.json", ".log", "-inventory.json")]
            sc.write_text(json.dumps({"gather": scenario}, indent=2) + "\n", encoding="utf-8")
            inp.write_text(json.dumps({"frames": frames}, indent=2) + "\n", encoding="utf-8")
            code = headless.main(["--mode", "gather", "--seed", "7", "--ticks", str(ticks),
                "--scenario", str(sc), "--inputs", str(inp), "--out", str(out),
                "--inventory-out", str(inv), "--snapshot-every", "1"])
            if code != 0:
                raise RuntimeError(f"{name}: exit {code}")
            rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
            report["cases"][name] = {"exit_code": code, "reason": rows[-1]["reason"],
                "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}
            if rows[-1]["reason"] != "tick_limit":
                saved = {"items": read_inventory(inv, version="1.2")}
                end_event = next(r for r in rows if r.get("name") == "gather_end")
                if saved != end_event["data"]["inventory"]:
                    raise AssertionError("inventory/event mismatch")
    finally:
        headless.load_contract = original
    same = (destination / "pickup.log").read_bytes() == (destination / "pickup-repeat.log").read_bytes()
    if not same:
        raise AssertionError("nondeterministic output")
    report["same_seed_identical_bytes"] = same
    (destination / "verification-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cases_passed": len(cases), "same_seed_identical_bytes": same,
                      "shared_manifest_version": current["contract_version"]}))


if __name__ == "__main__":
    main()
