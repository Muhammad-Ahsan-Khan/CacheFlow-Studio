"""Dependency-free local web server for the CacheFlow Studio dashboard."""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
from urllib.parse import parse_qs, urlparse

from cacheflow_core import CacheEvent, CacheFlowSimulator

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def format_cache(cache: tuple[int | None, ...]) -> str:
    return ", ".join("__" if value is None else str(value) for value in cache)


def log_event(event: CacheEvent) -> None:
    replacement = f" | evicted={event.evicted}" if event.evicted is not None else ""
    print(
        f"[web:{event.step:02}] index={event.index:02} value={event.value:03} "
        f"| {event.outcome:<4} | slot={event.slot}{replacement} "
        f"| cache=[{format_cache(event.cache)}]",
        flush=True,
    )


class CacheFlowRequestHandler(BaseHTTPRequestHandler):
    server_version = "CacheFlowStudio/1.0"

    def log_message(self, format: str, *args: object) -> None:
        if self.path.startswith("/api/stream"):
            return
        super().log_message(format, *args)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        if parsed.path == "/api/stream":
            self._stream_simulation(parse_qs(parsed.query))
            return
        if parsed.path == "/api/health":
            self._send_json({"status": "ok", "service": "CacheFlow Studio"})
            return
        self._serve_static(parsed.path)

    def _stream_simulation(self, query: dict[str, list[str]]) -> None:
        try:
            policy = query.get("policy", ["FIFO"])[0].upper()
            accesses = self._clamp_int(query.get("accesses", ["30"])[0], 1, 100)
            delay_ms = self._clamp_int(query.get("delay", ["500"])[0], 50, 2000)
            seed_text = query.get("seed", [""])[0].strip()
            seed = int(seed_text) if seed_text else None
            simulator = CacheFlowSimulator(policy)
        except (ValueError, TypeError) as error:
            self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        print(
            f"\n--- Dashboard simulation started: policy={policy}, "
            f"accesses={accesses}, seed={seed} ---",
            flush=True,
        )

        try:
            self._send_event(
                "meta",
                {
                    "policy": simulator.policy,
                    "accesses": accesses,
                    "delay": delay_ms,
                    "seed": seed,
                    "memory": list(simulator.memory),
                    "cache_size": len(simulator.cache),
                },
            )

            for event in simulator.run_random(accesses, seed):
                log_event(event)
                self._send_event("access", event.to_dict())
                time.sleep(delay_ms / 1000)

            report = simulator.summary()
            self._send_event("summary", report)
            self._send_event("done", {"message": "Simulation complete"})
            print(
                f"--- Complete: hits={report['hits']}, misses={report['misses']}, "
                f"ratio={report['hit_ratio']:.2f}% ---\n",
                flush=True,
            )
        except (BrokenPipeError, ConnectionResetError):
            print("--- Dashboard client stopped the simulation ---\n", flush=True)

    def _send_event(self, event_name: str, payload: dict) -> None:
        packet = f"event: {event_name}\ndata: {json.dumps(payload)}\n\n"
        self.wfile.write(packet.encode("utf-8"))
        self.wfile.flush()

    def _serve_static(self, path: str) -> None:
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        requested = (STATIC_DIR / relative).resolve()

        try:
            requested.relative_to(STATIC_DIR.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        if not requested.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(requested.name)[0] or "application/octet-stream"
        data = requested.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def _clamp_int(value: str, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, int(value)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CacheFlow Studio web dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--open", action="store_true", help="open the dashboard in a browser")
    args = parser.parse_args()

    try:
        server = ThreadingHTTPServer((args.host, args.port), CacheFlowRequestHandler)
    except OSError as error:
        print(f"Unable to start the server: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    browser_host = "127.0.0.1" if args.host in {"0.0.0.0", "::"} else args.host
    url = f"http://{browser_host}:{args.port}"
    print("\nCacheFlow Studio dashboard is ready.")
    print(f"Open: {url}")
    print("Each browser simulation is also printed in this terminal.")
    print("Press Ctrl+C to stop the server.\n")

    if args.open:
        Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping CacheFlow Studio...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
