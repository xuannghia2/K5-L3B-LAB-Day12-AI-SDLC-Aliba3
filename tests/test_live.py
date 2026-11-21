"""Test cửa sổ chơi trực tiếp (chonoi.live). Chỉ dành cho starter Python: nhóm đổi ngôn ngữ thì xóa file này."""

import json
import time
import unittest
import urllib.error
import urllib.request

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.status, r.read()


def _post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        e.close()
        return e.code


class LiveServerTest(unittest.TestCase):
    def test_state_input_and_clean_stop(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("gather", tuning, {}, 1), port=0)  # cổng ngẫu nhiên
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            code, body = _get(base + "/state")
            self.assertEqual(code, 200)
            st = json.loads(body)
            self.assertIn("tick", st)
            self.assertEqual(st["mode"], "gather")
            self.assertEqual(st["player"]["pos"], [2, 0])
            self.assertEqual(_post(base + "/input", {"move": [1, 0], "interact": False, "catch": False}), 200)
            self.assertEqual(_post(base + "/input", {"move": [5, 0]}), 400)
            code, html = _get(base + "/")
            self.assertEqual(code, 200)
            self.assertIn(b"<canvas", html)
            self.assertIn(b'id="touch-controls"', html)
            self.assertIn(b'id="connection-status"', html)
            self.assertIn(b'data-action="interact"', html)
            self.assertIn(b'data-action="catch"', html)
            self.assertIn(b'data-action="pause"', html)
            self.assertIn(b"snap.monsters", html)
            self.assertIn(b"itemKind", html)
            self.assertIn(b"itemFresh", html)
            self.assertIn(b'down.delete("catch")', html)
            deadline = time.time() + 3
            while time.time() < deadline:
                st2 = json.loads(_get(base + "/state")[1])
                if st2["tick"] > st["tick"] + 3 and st2["player"]["pos"][0] > st["player"]["pos"][0]:
                    break
                time.sleep(0.05)
            self.assertGreater(st2["tick"], st["tick"], "mô phỏng phải chạy nền")
            self.assertGreater(st2["player"]["pos"][0], st["player"]["pos"][0], "input phải tác động tới sim")
            self.assertEqual(_post(base + "/input", {"pause": True}), 200)
            deadline = time.time() + 1
            paused = None
            while time.time() < deadline:
                paused = json.loads(_get(base + "/state")[1])
                if paused["state"] == "paused":
                    break
                time.sleep(0.02)
            self.assertEqual(paused["state"], "paused")
            self.assertIn("monsters", paused)
        finally:
            server.stop()
        self.assertFalse(server.game._thread.is_alive())
        self.assertFalse(server._thread.is_alive())

    def test_quan_snapshot_exposes_contract_menu(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("quan", tuning, {}, 1), port=0)
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            code, body = _get(base + "/state")
            self.assertEqual(code, 200)
            st = json.loads(body)
            self.assertEqual(st["mode"], "quan")
            self.assertEqual(st["meta"]["menu"], tuning["menu"])
            code, html = _get(base + "/")
            self.assertEqual(code, 200)
            self.assertIn(b"drawMenuPanel", html)
        finally:
            server.stop()

    def test_toggle_pause_immediate_effect(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("gather", tuning, {}, 1), port=0)  # cổng ngẫu nhiên
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            code, body = _get(base + "/state")
            self.assertEqual(code, 200)
            st = json.loads(body)
            self.assertIn("tick", st)
            self.assertEqual(st["mode"], "gather")
            self.assertEqual(st["player"]["pos"], [2, 0])
            self.assertEqual(_post(base + "/input", {"move": [1, 0], "interact": False, "catch": False}), 200)
            self.assertEqual(_post(base + "/input", {"move": [5, 0]}), 400)
            code, html = _get(base + "/")
            self.assertEqual(code, 200)
            self.assertIn(b"<canvas", html)
            self.assertIn(b'id="touch-controls"', html)
            self.assertIn(b'id="connection-status"', html)
            self.assertIn(b'data-action="interact"', html)
            self.assertIn(b'data-action="catch"', html)
            self.assertIn(b'data-action="pause"', html)
            self.assertIn(b"snap.monsters", html)
            self.assertIn(b"itemKind", html)
            self.assertIn(b"itemFresh", html)
            self.assertIn(b'down.delete("catch")', html)
            deadline = time.time() + 3
            while time.time() < deadline:
                st2 = json.loads(_get(base + "/state")[1])
                if st2["tick"] > st["tick"] + 3 and st2["player"]["pos"][0] > st["player"]["pos"][0]:
                    break
                time.sleep(0.05)
            self.assertGreater(st2["tick"], st["tick"], "mô phỏng phải chạy nền")
            self.assertGreater(st2["player"]["pos"][0], st["player"]["pos"][0], "input phải tác động tới sim")
            self.assertEqual(_post(base + "/input", {"toggle_pause": True}), 200)
            deadline = time.time() + 1
            paused = None
            while time.time() < deadline:
                paused = json.loads(_get(base + "/state")[1])
                if paused["state"] == "paused":
                    break
                time.sleep(0.02)
            self.assertEqual(paused["state"], "paused")
            self.assertIn("monsters", paused)
        finally:
            server.stop()
        self.assertFalse(server.game._thread.is_alive())
        self.assertFalse(server._thread.is_alive())

    def test_pause_endpoint_immediate_effect(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("gather", tuning, {}, 1), port=0)
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            self.assertEqual(_post(base + "/pause", {}), 200)
            st = json.loads(_get(base + "/state")[1])
            self.assertEqual(st["state"], "paused")
            self.assertEqual(_post(base + "/pause", {}), 200)
            st = json.loads(_get(base + "/state")[1])
            self.assertEqual(st["state"], "playing")
        finally:
            server.stop()

if __name__ == "__main__":
    unittest.main()
