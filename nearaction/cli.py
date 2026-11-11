"""Simple CLI for NearAction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from . import tools
from .core import load_action


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nearaction", description="Durable agent workflows on NEAR")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # create
    p_create = sub.add_parser("create", help="Create a durable action from a YAML file")
    p_create.add_argument("--file", "-f", required=True, help="Path to workflow YAML")

    # list
    p_list = sub.add_parser("list", help="List actions")
    p_list.add_argument("--status", help="Filter by status")

    # status
    p_status = sub.add_parser("status", help="Show action status")
    p_status.add_argument("action_id")

    # resume
    p_resume = sub.add_parser("resume", help="Resume / get current step")
    p_resume.add_argument("action_id")
    p_resume.add_argument("--note", default="")

    # approve
    p_approve = sub.add_parser("approve", help="Record step result and advance")
    p_approve.add_argument("action_id")
    p_approve.add_argument("--note", default="")
    p_approve.add_argument("--result", default=None, help="Optional JSON result")

    # cancel
    p_cancel = sub.add_parser("cancel", help="Cancel an action")
    p_cancel.add_argument("action_id")
    p_cancel.add_argument("--reason", default="")

    # history
    p_hist = sub.add_parser("history", help="Show receipt chain")
    p_hist.add_argument("action_id")

    # anchor
    p_anchor = sub.add_parser("anchor", help="Prepare on-chain receipt root")
    p_anchor.add_argument("action_id")
    p_anchor.add_argument("--account", help="NEAR account that will hold the anchor")

    args = parser.parse_args(argv)

    if args.cmd == "create":
        path = Path(args.file)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        steps = data.get("steps", [])
        res = tools.tool_create(
            title=data.get("title", path.stem),
            steps=steps,
            description=data.get("description", ""),
            require_approval=data.get("require_approval", True),
            tags=data.get("tags"),
        )
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.cmd == "list":
        res = tools.tool_list(status=args.status)
        print(json.dumps(res, indent=2))
        return 0

    if args.cmd == "status":
        res = tools.tool_status(args.action_id)
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.cmd == "resume":
        res = tools.tool_resume(args.action_id, note=args.note)
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.cmd == "approve":
        result = None
        if args.result:
            result = json.loads(args.result)
        res = tools.tool_approve(args.action_id, result=result, note=args.note)
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.cmd == "cancel":
        res = tools.tool_cancel(args.action_id, reason=args.reason)
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.cmd == "history":
        res = tools.tool_history(args.action_id)
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.cmd == "anchor":
        res = tools.tool_anchor(args.action_id, near_account=args.account)
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
