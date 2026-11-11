"""Minimal read-only HTTP entrypoint for the Vercel deployment.

FlowMint is primarily a CLI/package. This endpoint gives the linked Vercel
project a deterministic health/status surface without creating or mutating
local workflow state.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler


def _json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


class handler(BaseHTTPRequestHandler):
    """Vercel Python runtime handler."""

    def _send_json(self, status: int, payload: dict) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._send_json(
            200,
            {
                "ok": True,
                "service": "flowmint",
                "status": "healthy",
                "runtime": "vercel-python",
            },
        )

    def do_HEAD(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._send_json(405, {"ok": False, "error": "method_not_allowed"})

    def log_message(self, format: str, *args: object) -> None:
        # Keep Vercel logs focused on application failures.
        return
