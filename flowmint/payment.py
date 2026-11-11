"""
Payment step helpers + policy wallet foundation + x402 bridge.

Supports:
- type: payment   → generic / NEAR Intents style transfer
- type: x402      → HTTP 402 agent micropayment (see x402.py)
"""

from __future__ import annotations

from typing import Any

from .x402 import describe_x402_step


def validate_payment_step(step: dict) -> tuple[bool, str]:
    t = step.get("type", "instruction")
    if t == "payment":
        payment = step.get("payment") or {}
        if "amount" not in payment:
            return False, "payment step requires payment.amount"
        return True, ""
    if t == "x402":
        x = step.get("x402") or {}
        if not x.get("url"):
            return False, "x402 step requires x402.url"
        return True, ""
    return True, ""


def describe_payment(step: dict) -> str:
    t = step.get("type", "instruction")
    if t == "x402":
        return describe_x402_step(step)
    p = step.get("payment") or {}
    amount = p.get("amount", "?")
    token = p.get("token", "NEAR")
    recipient = p.get("recipient", "(to be resolved)")
    return f"Pay {amount} {token} → {recipient}"


def policy_check_stub(
    amount: str,
    token: str,
    recipient: str,
    policy: dict | None = None,
) -> dict:
    """
    Placeholder for future on-chain / local policy engine.
    Returns {allowed: bool, reason: str, requires_human: bool}
    """
    policy = policy or {}
    max_per_tx = float(policy.get("max_per_tx", 10.0))
    try:
        amt = float(amount)
    except ValueError:
        return {"allowed": False, "reason": "invalid amount", "requires_human": True}

    if amt > max_per_tx:
        return {
            "allowed": False,
            "reason": f"amount {amt} exceeds max_per_tx {max_per_tx}",
            "requires_human": True,
        }

    allowlist = policy.get("allowlist") or []
    if allowlist and recipient not in allowlist:
        return {
            "allowed": False,
            "reason": "recipient not in allowlist",
            "requires_human": True,
        }

    return {"allowed": True, "reason": "within policy", "requires_human": False}
