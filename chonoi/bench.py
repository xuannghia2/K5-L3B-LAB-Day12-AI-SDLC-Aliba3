"""Rendered gather benchmark, Ticket-04. Uses the real live renderer and real rAF intervals."""

import argparse
import copy
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from .contract import load_contract
from .live import LiveGame, LiveServer, _Handler

WEB_DIR = Path(__file__).with_name("web")


def summarize(intervals, measured_s, load_ms):
    if not intervals or not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                and math.isfinite(v) and v > 0 for v in intervals):
        raise ValueError("frame intervals must be finite positive seconds")
    if not math.isfinite(measured_s) or measured_s <= 0 or not math.isfinite(load_ms) or load_ms < 0:
        raise ValueError("invalid measured duration/load time")
    if not math.isclose(sum(intervals), measured_s, abs_tol=0.02):
        raise ValueError("frame intervals do not cover measured duration")
    count = len(intervals)
    slowest = sorted(intervals, reverse=True)[:max(1, math.ceil(count * 0.01))]
    return {"avg_fps": count / measured_s, "p1_low_fps": len(slowest) / sum(slowest),
            "frames": count, "measured_s": measured_s, "load_ms": load_ms}


def validate_render_surface(body):
    if (body.get("canvas") != [1280, 720] or body.get("outer_window") != [1280, 720]
            or body.get("hidden") is not False):
        raise ValueError("render surface and native window must be 1280x720 and visible to rAF")


def browser_binary(explicit=None):
    candidates = [explicit] if explicit else []
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        candidates.append(shutil.which(name))
    candidates.extend([str(Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe"),
                       str(Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe"),
                       "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"])
    return next((str(Path(p)) for p in candidates if p and Path(p).is_file()), None)



def size_windows_browser(process):
    """Restore/size only the dedicated browser PID; never touch user browser windows.

    Chromium may inherit a maximized startup state on Windows, ignoring window-size.
    Other platforms retain Chromium's window-size and the renderer's size check.
    """
    if sys.platform != "win32":
        return
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user32.SetThreadDpiAwarenessContext.argtypes = [ctypes.c_void_p]
    user32.SetThreadDpiAwarenessContext.restype = ctypes.c_void_p
    previous_dpi = user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
    deadline = time.monotonic() + 8
    while process.poll() is None and time.monotonic() < deadline:
        windows = []

        @callback_type
        def collect(hwnd, _):
            owner = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value == process.pid and user32.IsWindowVisible(hwnd):
                windows.append(hwnd)
            return True

        user32.EnumWindows(collect, 0)
        if windows:
            for hwnd in windows:
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE clears maximized state
                user32.SetWindowPos(hwnd, None, 0, 0, 1280, 720, 0x0004 | 0x0010)
            if previous_dpi:
                user32.SetThreadDpiAwarenessContext(previous_dpi)
            return
        time.sleep(0.05)
    if previous_dpi:
        user32.SetThreadDpiAwarenessContext(previous_dpi)


def main(argv=None):
    started_epoch_ms = time.time() * 1000
    parser = argparse.ArgumentParser(prog="chonoi.bench")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--duration", required=True, type=float)
    parser.add_argument("--out", required=True)
    parser.add_argument("--browser", help="path to an installed Chromium browser")
    parser.add_argument("--headless", action="store_true", help="render in Chromium headless mode; recorded in metadata")
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration) or args.duration <= 0:
        parser.error("--duration must be positive and finite")
    binary = browser_binary(args.browser)
    if binary is None:
        print("Install Chrome/Chromium/Edge or pass --browser; no benchmark result was fabricated.", file=sys.stderr)
        return 1
    current = load_contract()
    tuning = copy.deepcopy(current["tuning"])
    injected_freshness = "freshness" not in tuning
    if injected_freshness:
        tuning["freshness"] = json.loads((WEB_DIR.parent.parent / "data/freshness-p3.json").read_text())
    game = LiveGame("gather", tuning, {}, args.seed)
    server = LiveServer(game, port=0)
    finished = threading.Event()
    received = {}
    config = {"seed": args.seed, "duration_s": args.duration, "warmup_s": 3,
              "started_epoch_ms": started_epoch_ms}

    class Handler(_Handler):
        def handle(self):
            try:
                super().handle()
            except (ConnectionResetError, BrokenPipeError):
                pass  # the dedicated browser is closed after submitting the result

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/bench/config":
                self._send(200, json.dumps(config).encode())
            elif path == "/bench.js":
                self._send(200, (WEB_DIR / "bench.js").read_bytes(), "text/javascript; charset=utf-8")
            else:
                super().do_GET()

        def do_POST(self):
            if self.path != "/bench/result":
                return super().do_POST()
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1000000:
                    raise ValueError("invalid result size")
                body = json.loads(self.rfile.read(size))
                if body.get("error"):
                    raise ValueError(body["error"])
                validate_render_surface(body)
                if body["measured_s"] < args.duration:
                    raise ValueError("measurement shorter than requested")
                result = summarize(body["intervals_s"], body["measured_s"], body["first_frame_epoch_ms"] - started_epoch_ms)
                received.update(result=result, metadata={k: v for k, v in body.items() if k != "intervals_s"})
                self._send(200, b'{"ok":true}')
            except (ValueError, KeyError, TypeError) as error:
                received["error"] = str(error)
                self._send(400, json.dumps({"error": str(error)}).encode())
            finally:
                finished.set()

    Handler.game = game
    server.httpd.RequestHandlerClass = Handler
    profile = tempfile.TemporaryDirectory(prefix="chonoi-bench-", ignore_cleanup_errors=True)
    process = None
    try:
        server.start()
        command = [binary, "--no-first-run", "--no-default-browser-check", "--force-device-scale-factor=1",
                   "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
                   "--disable-backgrounding-occluded-windows", "--window-size=1280,720",
                   "--user-data-dir=" + profile.name, "--app=" + server.url + "?bench=1"]
        if args.headless:
            command.insert(1, "--headless=new")
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not args.headless:
            size_windows_browser(process)
        print(f"Rendering gather, seed {args.seed}, warmup 3s + measurement {args.duration:g}s", flush=True)
        if not finished.wait(args.duration + 45):
            print("Benchmark timed out before receiving real rendered frame data.", file=sys.stderr)
            return 1
        if "error" in received:
            print(received["error"], file=sys.stderr)
            return 1
        out = Path(args.out)
        out.write_text(json.dumps(received["result"], indent=2) + "\n", encoding="utf-8")
        metadata = dict(received["metadata"], browser=binary, headless=args.headless,
                        shared_manifest_version=current["contract_version"],
                        benchmark_freshness_profile=injected_freshness,
                        warmup_s=3, seed=args.seed)
        out.with_name(out.stem + "-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(received["result"]), flush=True)
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        server.stop()
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        profile.cleanup()


if __name__ == "__main__":
    sys.exit(main())
