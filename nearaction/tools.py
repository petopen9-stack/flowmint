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
from .storage import data_dir


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
    a["updated_at"] = a.get("updated_at")  # will be refreshed on save
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
            if next_step.get("needs_approval") or (a.get("require_approval") and next_step.get("type") == "payment"):
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
    """
    Prepare / record an on-chain anchor of the receipt root.
    In v0.1 this stores the intent locally and returns the data
    a user (or later the agent) can submit to NEAR.
    """
    a = load_action(action_id)
    if not a:
        return {"ok": False, "error": f"Action {action_id} not found"}

    root = compute_root_hash(a)
    anchor_payload = {
        "action_id": action_id,
        "root_hash": root,
        "title": a["title"],
        "status": a["status"],
        "near_account": near_account,
        "note": "Submit this root_hash to NEAR (contract or account storage) for public verifiability",
    }

    a["anchor"] = {
        "root_hash": root,
        "prepared_at": a.get("updated_at"),
        "near_account": near_account,
        "status": "prepared",  # prepared | submitted | confirmed
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
        "hint": "Future versions will auto-submit via NEAR Intents or a dedicated anchor contract.",
    }
