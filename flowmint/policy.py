"""Deterministic payment policy checks for agent security."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _normalise(value: Any) -> str:
    return str(value or "").strip().lower()


def evaluate_payment(policy: dict | None, payment: dict, spent_atomic: int = 0) -> dict:
    """Return a deterministic allow/warn/block decision without signing funds.

    Amounts are compared as atomic units because x402 payment payloads do not
    carry a universal decimal precision. Policy fields ending in ``_atomic``
    use the same units as the payment payload.
    """
    policy = policy or {}
    amount_raw = payment.get("amount", payment.get("amount_atomic", "0"))
    try:
        amount = int(str(amount_raw))
    except (TypeError, ValueError):
        return {"decision": "block", "reasons": ["amount is not a valid integer"], "amount_atomic": 0}

    pay_to = _normalise(payment.get("pay_to", payment.get("payTo")))
    network = _normalise(payment.get("network"))
    reasons: list[str] = []
    hard_blocks: list[str] = []
    warnings: list[str] = []

    blocked = {_normalise(x) for x in policy.get("blocked_recipients", [])}
    allowed = {_normalise(x) for x in policy.get("allowed_recipients", [])}
    networks = {_normalise(x) for x in policy.get("allowed_networks", [])}

    if pay_to in blocked:
        hard_blocks.append(f"recipient {pay_to} is explicitly blocked")
    if allowed and pay_to not in allowed:
        hard_blocks.append(f"recipient {pay_to} is not in allowed_recipients")
    if networks and network not in networks:
        hard_blocks.append(f"network {network} is not in allowed_networks")

    max_per = policy.get("max_per_payment_atomic", policy.get("max_per_payment"))
    max_total = policy.get("max_total_atomic", policy.get("max_total"))
    max_per_dec = _decimal(max_per)
    max_total_dec = _decimal(max_total)
    if max_per_dec is not None and Decimal(amount) > max_per_dec:
        hard_blocks.append(f"amount {amount} exceeds max_per_payment_atomic {max_per_dec}")
    if max_total_dec is not None and Decimal(spent_atomic + amount) > max_total_dec:
        hard_blocks.append(f"total spend {spent_atomic + amount} exceeds max_total_atomic {max_total_dec}")

    if hard_blocks:
        reasons.extend(hard_blocks)
        return {
            "decision": "block",
            "reasons": reasons,
            "amount_atomic": amount,
            "pay_to": pay_to,
            "network": network,
        }

    approval = policy.get("require_approval_above_atomic", policy.get("require_approval_above"))
    approval_dec = _decimal(approval)
    if approval_dec is not None and Decimal(amount) > approval_dec:
        warnings.append(f"amount {amount} requires approval above {approval_dec}")

    decision = "warn" if warnings else "allow"
    return {
        "decision": decision,
        "reasons": warnings or ["payment matches policy"],
        "amount_atomic": amount,
        "pay_to": pay_to,
        "network": network,
    }
