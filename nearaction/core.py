"""Core durable action logic + hash-chained receipts."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from .storage import actions_dir, receipts_dir, load_json, save_json


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_receipt(action: dict, event: str, detail: dict | None = None) -> dict:
    payload = {
        "action_id": action["id"],
        "event": event,
        "ts": _now(),
        "detail": detail or {},
        "prev_hash": action.get("last_hash", "genesis"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(raw.encode()).hexdigest()
    payload["hash"] = h
    return payload


def append_receipt(action: dict, event: str, detail: dict | None = None) -> dict:
    receipt = _make_receipt(action, event, detail)
    action["last_hash"] = receipt["hash"]
    action.setdefault("receipts", []).append(receipt["hash"])
    rpath = receipts_dir() / f"{receipt['hash']}.json"
    save_json(rpath, receipt)
    return receipt


def create_action(
    title: str,
    steps: list[dict],
    description: str = "",
    require_approval: bool = True,
    tags: list[str] | None = None,
) -> dict:
    action_id = str(uuid.uuid4())[:8]
    action = {
        "id": action_id,
        "title": title,
        "description": description,
        "status": "pending",  # pending | running | waiting_approval | paused | completed | failed | cancelled
        "require_approval": require_approval,
        "tags": tags or [],
        "created_at": _now(),
        "updated_at": _now(),
        "current_step": 0,
        "steps": steps,
        "checkpoints": [],
        "receipts": [],
        "last_hash": "genesis",
        "anchor": None,  # will hold NEAR tx hash or account storage info later
        "meta": {},
    }
    for s in action["steps"]:
        s.setdefault("status", "pending")
        s.setdefault("result", None)
        s.setdefault("type", "instruction")  # instruction | payment

    append_receipt(action, "created", {"title": title})
    save_action(action)
    return action


def load_action(action_id: str) -> Optional[dict]:
    path = actions_dir() / f"{action_id}.json"
    return load_json(path)


def save_action(action: dict) -> None:
    path = actions_dir() / f"{action['id']}.json"
    save_json(path, action)


def list_actions(status: str | None = None, limit: int = 50) -> list[dict]:
    results = []
    files = sorted(actions_dir().glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in files:
        a = load_json(p)
        if not a:
            continue
        if status and a.get("status") != status:
            continue
        results.append({
            "id": a["id"],
            "title": a["title"],
            "status": a["status"],
            "current_step": a["current_step"],
            "total_steps": len(a["steps"]),
            "updated_at": a["updated_at"],
            "tags": a.get("tags", []),
        })
        if len(results) >= limit:
            break
    return results


def get_receipt_chain(action_id: str) -> list[dict]:
    a = load_action(action_id)
    if not a:
        return []
    chain = []
    for h in a.get("receipts", []):
        r = load_json(receipts_dir() / f"{h}.json")
        if r:
            chain.append(r)
    return chain


def compute_root_hash(action: dict) -> str:
    """Simple root of the receipt chain (last hash). Ready for on-chain anchor."""
    return action.get("last_hash", "genesis")
