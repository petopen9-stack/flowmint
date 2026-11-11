"""Tool functions an agent (or CLI) can call."""

from __future__ import annotations

from typing import Any, Optional

from .core import (
    create_action,
    load_action,
    save_action,
    list_actions,
    append_receipt,
    get_receipt_chain,
    compute_root_hash,
)
from .x402 import (
    parse_402_response,
    select_accept_option,
    prepare_payment_intent,
    build_x402_step,
)


def tool_create(
    title: str,
    steps: list[dict],
    description: str = "",
    require_approval: bool = True,
    tags: list[str] | None = None,
) -> dict:
    if not steps:
        return {"ok": False, "error": "At least one step is required"}
    for i, s in enumerate(steps):
        if "name" not in s or "instruction" not in s:
            return {"ok": False, "error": f"Step {i} must have 'name' and 'instruction'"}

    action = create_action(title, steps, description, require_approval, tags)
    return {
        "ok": True,
        "action_id": action["id"],
        "title": action["title"],
        "status": action["status"],
        "steps": len(action["steps"]),
        "message": f"Durable action '{action['id']}' created. Use nearaction_resume to start.",
    }


def tool_list(status: str | None = None, limit: int = 20) -> dict:
    items = list_actions(status=status, limit=limit)
    return {"ok": True, "count": len(items), "actions": items}


def tool_status(action_id: str) -> dict:
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}
    current = None
    if a["current_step"] < len(a["steps"]):
        current = a["steps"][a["current_step"]]
    return {
        "ok": True,
        "action_id": action_id,
        "title": a["title"],
        "status": a["status"],
        "current_step": a["current_step"],
        "total_steps": len(a["steps"]),
        "current": current,
        "last_hash": a.get("last_hash"),
        "anchor": a.get("anchor"),
    }


def tool_resume(action_id: str, note: str = "") -> dict:
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}
    if a["status"] in ("completed", "cancelled", "failed"):
        return {"ok": False, "error": f"Action already {a['status']}"}

    if a["status"] == "pending":
        a["status"] = "running"
        append_receipt(a, "started", {"note": note})

    idx = a["current_step"]
    if idx >= len(a["steps"]):
        a["status"] = "completed"
        save_action(a)
        return {"ok": True, "action_id": action_id, "status": "completed", "message": "No more steps"}

    current = a["steps"][idx]
    current["status"] = "running"
    from .core import _now
    a["updated_at"] = _now()
    save_action(a)

    return {
        "ok": True,
        "action_id": action_id,
        "status": a["status"],
        "step_index": idx,
        "step_name": current["name"],
        "step_type": current.get("type", "instruction"),
        "instruction": current["instruction"],
        "payment": current.get("payment"),
        "x402": current.get("x402"),
        "message": "Execute this step, then call nearaction_approve with the result.",
    }


def tool_approve(
    action_id: str,
    result: Any = None,
    advance: bool = True,
    note: str = "",
) -> dict:
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}

    idx = a["current_step"]
    if idx >= len(a["steps"]):
        return {"ok": False, "error": "No more steps"}

    step = a["steps"][idx]
    step["status"] = "completed"
    step["result"] = result
    from .core import _now
    step["completed_at"] = _now()
    if note:
        step["note"] = note

    a["updated_at"] = _now()
    append_receipt(a, "step_completed", {
        "step_index": idx,
        "step_name": step["name"],
        "step_type": step.get("type", "instruction"),
        "note": note,
    })

    if advance:
        a["current_step"] = idx + 1
        if a["current_step"] >= len(a["steps"]):
            a["status"] = "completed"
            append_receipt(a, "completed", {})
        else:
            next_step = a["steps"][a["current_step"]]
            if next_step.get("needs_approval") or next_step.get("type") in ("payment", "x402"):
                a["status"] = "waiting_approval"
            else:
                a["status"] = "running"

    save_action(a)
    return {
        "ok": True,
        "action_id": action_id,
        "status": a["status"],
        "current_step": a["current_step"],
        "completed_step": step["name"],
        "message": f"Step '{step['name']}' recorded. Status: {a['status']}",
    }


def tool_cancel(action_id: str, reason: str = "") -> dict:
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}
    if a["status"] in ("completed", "cancelled"):
        return {"ok": False, "error": f"Already {a['status']}"}

    from .core import _now
    a["status"] = "cancelled"
    a["updated_at"] = _now()
    a["cancel_reason"] = reason
    append_receipt(a, "cancelled", {"reason": reason})
    save_action(a)
    return {"ok": True, "action_id": action_id, "status": "cancelled"}


def tool_history(action_id: str) -> dict:
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}
    chain = get_receipt_chain(action_id)
    return {
        "ok": True,
        "action_id": action_id,
        "last_hash": a.get("last_hash"),
        "root": compute_root_hash(a),
        "receipt_count": len(chain),
        "receipts": chain,
    }


def tool_anchor(action_id: str, near_account: str | None = None) -> dict:
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}

    root = compute_root_hash(a)
    a["anchor"] = {
        "root_hash": root,
        "prepared_at": a.get("updated_at"),
        "near_account": near_account,
        "status": "prepared",
    }
    from .core import _now
    a["updated_at"] = _now()
    append_receipt(a, "anchor_prepared", {"root_hash": root, "near_account": near_account})
    save_action(a)

    return {
        "ok": True,
        "action_id": action_id,
        "root_hash": root,
        "anchor": a["anchor"],
        "message": "Receipt root prepared. Submit to NEAR for on-chain verifiability.",
    }


def tool_x402_challenge(
    action_id: str,
    status_code: int,
    headers: dict | None = None,
    body: dict | str | None = None,
) -> dict:
    """
    Record a 402 challenge against the current x402 step and prepare a payment intent.
    Call this when the agent receives HTTP 402 while executing an x402 step.
    """
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}

    idx = a["current_step"]
    if idx >= len(a["steps"]):
        return {"ok": False, "error": "No current step"}

    step = a["steps"][idx]
    if step.get("type") != "x402":
        return {"ok": False, "error": "Current step is not type=x402"}

    parsed = parse_402_response(status_code, headers, body)
    if not parsed.get("ok"):
        return parsed

    x = step.setdefault("x402", {})
    option = select_accept_option(
        parsed.get("accepts") or [],
        preferred_network=x.get("preferred_network"),
        preferred_asset=x.get("preferred_asset"),
        max_amount=x.get("max_amount"),
    )
    if not option:
        return {"ok": False, "error": "No acceptable payment option in 402 response"}

    intent = prepare_payment_intent(parsed, option, payer_account=a.get("meta", {}).get("payer"))
    x["status"] = "challenged"
    x["challenge"] = parsed
    x["payment_payload"] = intent
    step["needs_approval"] = True

    from .core import _now
    a["updated_at"] = _now()
    a["status"] = "waiting_approval"
    append_receipt(a, "x402_challenged", {
        "url": x.get("url"),
        "amount": option.get("amount"),
        "network": option.get("network"),
        "pay_to": option.get("pay_to"),
    })
    save_action(a)

    return {
        "ok": True,
        "action_id": action_id,
        "status": a["status"],
        "x402_status": "challenged",
        "payment_intent": intent,
        "message": (
            "402 challenge recorded. Review the payment_intent, sign it with a policy-limited key, "
            "then call nearaction_x402_confirm after the paid request succeeds."
        ),
    }


def tool_x402_confirm(
    action_id: str,
    payment_proof: dict | str | None = None,
    response_summary: dict | None = None,
    note: str = "",
) -> dict:
    """
    Mark the current x402 step as paid + fulfilled and advance the action.
    Call after the agent has signed, retried the request, and received the resource.
    """
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}

    idx = a["current_step"]
    if idx >= len(a["steps"]):
        return {"ok": False, "error": "No current step"}

    step = a["steps"][idx]
    if step.get("type") != "x402":
        return {"ok": False, "error": "Current step is not type=x402"}

    x = step.setdefault("x402", {})
    x["status"] = "fulfilled"
    x["result"] = {
        "payment_proof": payment_proof,
        "response_summary": response_summary,
        "note": note,
    }

    # Re-use the normal approve path so the receipt chain stays consistent
    return tool_approve(
        action_id,
        result={"x402": x["result"], "payment_proof": payment_proof},
        advance=True,
        note=note or "x402 payment fulfilled",
    )


def tool_add_x402_step(
    action_id: str,
    url: str,
    method: str = "GET",
    description: str = "",
    max_amount: str | None = None,
    preferred_network: str | None = None,
) -> dict:
    """Append an x402 payment step to an existing (still running) action."""
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}
    if a["status"] in ("completed", "cancelled", "failed"):
        return {"ok": False, "error": f"Cannot modify {a['status']} action"}

    step = build_x402_step(url, method, description, max_amount, preferred_network)
    a["steps"].append(step)
    from .core import _now
    a["updated_at"] = _now()
    append_receipt(a, "x402_step_added", {"url": url, "method": method})
    save_action(a)

    return {
        "ok": True,
        "action_id": action_id,
        "step_name": step["name"],
        "total_steps": len(a["steps"]),
        "message": f"x402 step added for {url}",
    }
