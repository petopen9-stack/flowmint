"""
Payment step helpers + policy wallet foundation (v0.1 stubs).

In the next iteration this will talk to:
- a policy wallet contract (function-call key + limits)
- NEAR Intents for actual execution
"""

from __future__ import annotations

from typing import Any


def validate_payment_step(step: dict) -> tuple[bool, str]:
    if step.get("type") != "payment":
        return True, ""
    payment = step.get("payment") or {}
    if "amount" not in payment:
        return False, "payment step requires payment.amount"
    return True, ""


def describe_payment(step: dict) -> str:
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
    # Extremely simple stub rules
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
