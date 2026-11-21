"""Paused real-simulation fixtures for manually verifying three high-contrast warnings."""

import argparse
import json
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer, _Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    directory = Path(args.out)
    directory.mkdir(parents=True, exist_ok=True)
    tuning = load_contract()["tuning"]
    fixtures = {
        "gather": {"player": {"pos": [60, 24], "oxygen_ticks": 200}, "random_fish": False,
                   "monsters": [{"id": "M1", "kind": "ca_sau", "pos": [61, 24],
                                 "waypoints": [[60, 24], [64, 24]]}]},
        "quan": {"stock": {"ca_loc": 1}, "random_customers": False,
                 "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                "state": "waiting", "order_status": "reserved", "reserved": {"ca_loc": 1},
                                "patience_ticks_left": 40}]},
    }
    stop = threading.Event()

    class Handler(_Handler):
        def do_POST(self):
            if self.path == "/preview/stop":
                self._send(200, b'{"ok":true}')
                stop.set()
            else:
                super().do_POST()

    servers = []
    try:
        urls = {}
        for mode, scenario in fixtures.items():
            (directory / ("warning-" + mode + "-scenario.json")).write_text(json.dumps({mode: scenario}, indent=2) + "\n", encoding="utf-8")
            game = LiveGame(mode, tuning, scenario, 42)
            game.set_input({"pause": True})
            server = LiveServer(game, port=0)
            server.httpd.RequestHandlerClass = type("PreviewHandler", (Handler,), {"game": game})
            server.start()
            servers.append(server)
            urls[mode] = server.url
        (directory / "warning-preview.json").write_text(json.dumps(urls, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(urls), flush=True)
        stop.wait(300)
    finally:
        for server in servers:
            server.stop()


if __name__ == "__main__":
    main()
