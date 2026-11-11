"""
x402 payment support for NearAction.

x402 = open standard that uses HTTP 402 Payment Required so agents can
pay for APIs / data / services with stablecoins (or NEAR) inside the
request itself — no accounts, no API keys, no human checkout.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.parse import urlparse


def parse_402_response(
    status_code: int,
    headers: dict[str, str] | None = None,
    body: dict | str | None = None,
) -> dict:
    if status_code != 402:
        return {"ok": False, "error": f"Expected 402, got {status_code}"}

    headers = {k.lower(): v for k, v in (headers or {}).items()}
    payment_required = headers.get("payment-required") or headers.get("x-payment-required")

    accepts = []
    raw: dict = {}

    if isinstance(body, str):
        try:
            body = json.loads(body)
        except Exception:
            body = {}

    if isinstance(body, dict):
        raw = body
        if "accepts" in body:
            accepts = body["accepts"]
        elif "paymentRequired" in body:
            accepts = body["paymentRequired"].get("accepts", [])

    options = []
    for a in accepts:
        options.append({
            "scheme": a.get("scheme", "exact"),
            "network": a.get("network", ""),
            "asset": a.get("asset", ""),
            "amount": str(a.get("amount", a.get("maxAmountRequired", ""))),
            "pay_to": a.get("payTo", a.get("pay_to", "")),
            "max_timeout_seconds": a.get("maxTimeoutSeconds", a.get("max_timeout_seconds", 300)),
            "extra": {k: v for k, v in a.items() if k not in {
                "scheme", "network", "asset", "amount", "maxAmountRequired",
                "payTo", "pay_to", "maxTimeoutSeconds", "max_timeout_seconds",
            }},
        })

    return {
        "ok": True,
        "payment_required_header": payment_required,
        "accepts": options,
        "raw": raw,
        "preferred": options[0] if options else None,
    }


def build_x402_step(
    url: str,
    method: str = "GET",
    description: str = "",
    max_amount: str | None = None,
    preferred_network: str | None = None,
    preferred_asset: str | None = None,
) -> dict:
    return {
        "name": f"x402-pay-{urlparse(url).netloc or 'resource'}",
        "type": "x402",
        "instruction": description or f"Pay for and fetch {method} {url} via x402",
        "x402": {
            "url": url,
            "method": method.upper(),
            "max_amount": max_amount,
            "preferred_network": preferred_network or "near:mainnet",
            "preferred_asset": preferred_asset,
            "status": "pending",
            "challenge": None,
            "payment_payload": None,
            "result": None,
        },
        "needs_approval": True,
    }


def _amount_ok(option_amount: str, max_amount: str | None) -> bool:
    """Compare amounts; treat large integers as atomic units and skip strict max."""
    if max_amount is None or max_amount == "":
        return True
    try:
        opt = float(option_amount)
        mx = float(max_amount)
    except (ValueError, TypeError):
        return True
    # If option looks atomic (e.g. 2500000 USDC-6) and max looks human (1.00), allow
    if opt >= 1000 and mx < 100:
        return True
    return opt <= mx


def select_accept_option(
    accepts: list[dict],
    preferred_network: str | None = None,
    preferred_asset: str | None = None,
    max_amount: str | None = None,
) -> Optional[dict]:
    if not accepts:
        return None

    candidates = list(accepts)
    if preferred_network:
        filtered = [a for a in candidates if preferred_network in (a.get("network") or "")]
        if filtered:
            candidates = filtered
    if preferred_asset:
        filtered = [
            a for a in candidates
            if preferred_asset.lower() in (a.get("asset") or "").lower()
        ]
        if filtered:
            candidates = filtered

    candidates = [a for a in candidates if _amount_ok(a.get("amount") or "0", max_amount)]
    return candidates[0] if candidates else None


def prepare_payment_intent(
    challenge: dict,
    option: dict,
    payer_account: str | None = None,
) -> dict:
    return {
        "scheme": option.get("scheme", "exact"),
        "network": option.get("network"),
        "asset": option.get("asset"),
        "amount": option.get("amount"),
        "pay_to": option.get("pay_to"),
        "payer": payer_account,
        "max_timeout_seconds": option.get("max_timeout_seconds", 300),
        "source_challenge": challenge.get("raw") or challenge,
        "status": "ready_to_sign",
        "note": (
            "Sign this payment with a NEAR (or EVM/SVM) key that has policy limits, "
            "then attach the resulting X-PAYMENT / PAYMENT-SIGNATURE header and retry the request."
        ),
    }


def describe_x402_step(step: dict) -> str:
    x = step.get("x402") or {}
    status = x.get("status", "pending")
    url = x.get("url", "?")
    if status == "pending":
        return f"x402: request {x.get('method', 'GET')} {url} (will handle 402)"
    if status == "challenged":
        pref = (x.get("challenge") or {}).get("preferred") or {}
        return f"x402: challenged — pay {pref.get('amount')} on {pref.get('network')} to {pref.get('pay_to')}"
    if status == "paid":
        return f"x402: payment prepared/signed for {url}"
    if status == "fulfilled":
        return f"x402: resource obtained from {url}"
    return f"x402: {status} — {url}"
