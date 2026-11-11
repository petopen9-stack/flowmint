"""Optional PingPay x402 facilitator adapter.

The adapter never stores keys or signs origin-chain transactions. It handles
capability discovery, quote creation, and settlement reporting; the caller
must provide the approved origin-chain transaction hash for settlement.
"""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any

DEFAULT_PING_URL = "https://pay.pingpay.io/agentpay/x402"


def _request(method: str, url: str, payload: dict | None = None, api_key: str | None = None) -> dict:
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if api_key:
        headers["X-Api-Key"] = api_key
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return {"ok": True, "status_code": response.status, "body": json.loads(raw) if raw else {}}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw}
        return {"ok": False, "status_code": exc.code, "body": body, "error": f"HTTP {exc.code}"}
    except (URLError, TimeoutError) as exc:
        return {"ok": False, "error": str(exc)}


def ping_supported(base_url: str | None = None) -> dict:
    base = (base_url or os.getenv("FLOWMINT_PING_FACILITATOR_URL") or DEFAULT_PING_URL).rstrip("/")
    return _request("GET", f"{base}/supported")


def ping_quote(
    payment_requirements: dict,
    refund_to: str,
    base_url: str | None = None,
    api_key: str | None = None,
) -> dict:
    """Request a quote using Ping's x402 v2 ``payload.type=quote`` flow."""
    key = api_key or os.getenv("FLOWMINT_PING_API_KEY")
    if not key:
        return {"ok": False, "error": "Set FLOWMINT_PING_API_KEY; no key was sent"}
    base = (base_url or os.getenv("FLOWMINT_PING_FACILITATOR_URL") or DEFAULT_PING_URL).rstrip("/")
    payload = {
        "x402Version": 2,
        "paymentPayload": {
            "x402Version": 2,
            "accepted": payment_requirements,
            "payload": {"type": "quote", "refundTo": refund_to},
        },
        "paymentRequirements": payment_requirements,
    }
    return _request("POST", f"{base}/verify", payload, key)


def ping_settle(
    payment_requirements: dict,
    operation_token: str,
    deposit_address: str,
    tx_hash: str,
    base_url: str | None = None,
    api_key: str | None = None,
) -> dict:
    """Report an origin-chain deposit for settlement; never submits the tx."""
    key = api_key or os.getenv("FLOWMINT_PING_API_KEY")
    if not key:
        return {"ok": False, "error": "Set FLOWMINT_PING_API_KEY; no key was sent"}
    base = (base_url or os.getenv("FLOWMINT_PING_FACILITATOR_URL") or DEFAULT_PING_URL).rstrip("/")
    payload = {
        "x402Version": 2,
        "paymentPayload": {
            "x402Version": 2,
            "accepted": payment_requirements,
            "payload": {
                "type": "deposit",
                "operationToken": operation_token,
                "depositAddress": deposit_address,
                "txHash": tx_hash,
            },
        },
        "paymentRequirements": payment_requirements,
    }
    return _request("POST", f"{base}/settle", payload, key)


def load_payment_requirements(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        data: Any = json.load(handle)
    if isinstance(data, dict) and isinstance(data.get("accepts"), list):
        if not data["accepts"]:
            raise ValueError("402 body has no payment options")
        return data["accepts"][0]
    if isinstance(data, dict) and isinstance(data.get("paymentRequirements"), dict):
        return data["paymentRequirements"]
    return data
