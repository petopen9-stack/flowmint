"""
NearAction — Durable agent workflows on NEAR

Durable, resumable, checkpointed actions with human-approval gates,
verifiable hash-chained receipts, and first-class payment steps
(ready for policy wallets & NEAR Intents).
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
)

__version__ = "0.1.0"
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
]
