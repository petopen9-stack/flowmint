"""Minimal tests — run with: python -m pytest tests/ -q"""

from nearaction import tools
from nearaction.x402 import parse_402_response, select_accept_option, prepare_payment_intent


def test_create_resume_approve():
    res = tools.tool_create(
        title="test",
        steps=[
            {"name": "a", "instruction": "do a"},
            {"name": "b", "instruction": "do b", "needs_approval": True},
        ],
        require_approval=False,
    )
    assert res["ok"]
    aid = res["action_id"]

    r = tools.tool_resume(aid)
    assert r["ok"] and r["step_name"] == "a"

    r = tools.tool_approve(aid, result={"ok": True})
    assert r["ok"]

    r = tools.tool_resume(aid)
    assert r["step_name"] == "b"

    r = tools.tool_approve(aid, note="approved")
    assert r["ok"]

    st = tools.tool_status(aid)
    assert st["status"] == "completed"


def test_x402_flow():
    res = tools.tool_create(
        title="x402 test",
        steps=[{
            "name": "pay",
            "type": "x402",
            "instruction": "pay api",
            "x402": {
                "url": "https://api.example.com/data",
                "method": "GET",
                "max_amount": "5.00",
                "preferred_network": "near:mainnet",
                "status": "pending",
            },
        }],
    )
    aid = res["action_id"]
    tools.tool_resume(aid)

    ch = tools.tool_x402_challenge(
        aid,
        402,
        headers={"payment-required": "x"},
        body={
            "x402Version": 2,
            "accepts": [{
                "scheme": "exact",
                "network": "near:mainnet",
                "asset": "usdc.near",
                "amount": "1000000",
                "payTo": "payee.near",
            }],
        },
    )
    assert ch["ok"]
    assert ch["x402_status"] == "challenged"
    assert ch["payment_intent"]["amount"] == "1000000"

    conf = tools.tool_x402_confirm(aid, payment_proof={"tx": "abc"}, note="paid")
    assert conf["ok"]

    st = tools.tool_status(aid)
    assert st["status"] == "completed"

    hist = tools.tool_history(aid)
    events = [r["event"] for r in hist["receipts"]]
    assert "x402_challenged" in events
    assert "step_completed" in events


def test_parse_402():
    parsed = parse_402_response(
        402,
        body={
            "accepts": [{
                "scheme": "exact",
                "network": "near:mainnet",
                "asset": "usdc.near",
                "amount": "500000",
                "payTo": "m.near",
            }],
        },
    )
    assert parsed["ok"]
    assert parsed["preferred"]["pay_to"] == "m.near"
    opt = select_accept_option(parsed["accepts"], preferred_network="near")
    assert opt is not None
    intent = prepare_payment_intent(parsed, opt, payer_account="agent.near")
    assert intent["payer"] == "agent.near"
