"""
FlowMint — Durable agent workflows on NEAR

Durable, resumable, checkpointed actions with human-approval gates,
verifiable hash-chained receipts, x402 micropayments, and policy-ready
payment steps.
"""

from .core import (
    create_action,
    load_action,
    save_action,
    list_actions,
    append_receipt,
    get_receipt_chain,
)
from .tools import (
    tool_create,
    tool_list,
    tool_status,
    tool_resume,
    tool_approve,
    tool_cancel,
    tool_history,
    tool_anchor,
    tool_x402_challenge,
    tool_x402_confirm,
    tool_add_x402_step,
)

__version__ = "0.1.1"
__all__ = [
    "create_action",
    "load_action",
    "save_action",
    "list_actions",
    "append_receipt",
    "get_receipt_chain",
    "tool_create",
    "tool_list",
    "tool_status",
    "tool_resume",
    "tool_approve",
    "tool_cancel",
    "tool_history",
    "tool_anchor",
    "tool_x402_challenge",
    "tool_x402_confirm",
    "tool_add_x402_step",
]
