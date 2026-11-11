# Demo Script (≤ 90 seconds)

## Suggested flow

1. **0–10s** — Hook  
   “Most agents forget everything when they restart. NearAction keeps multi-step work — and x402 payments — alive and auditable.”

2. **10–25s** — Create (with x402 step)  
   ```bash
   nearaction create --file examples/x402-api-call.yaml
   ```
   Show the new action ID and the `type: x402` step.

3. **25–45s** — Resume → 402 challenge  
   ```bash
   nearaction resume <id>
   # (simulate receiving 402, then)
   # agent calls nearaction_x402_challenge(...)
   nearaction status <id>
   ```
   Highlight `waiting_approval` + payment intent in the receipt.

4. **45–60s** — Approve & confirm  
   ```bash
   nearaction approve <id> --note "policy ok"
   # after real sign + retry:
   # nearaction_x402_confirm(...)
   nearaction history <id>
   ```

5. **60–75s** — Receipt + anchor  
   Show the hash chain containing `x402_challenged` → `step_completed`.

6. **75–85s** — Close  
   “Durable workflows. Human / policy gates. Verifiable receipts.  
   Native x402 so agents can pay for APIs without accounts.  
   That’s NearAction for the agent economy on NEAR.”

---

## Caption for X

```
NearAction — durable agent workflows + x402 payments on NEAR.

• checkpoints & resume
• human / policy gates
• hash-chained receipts
• first-class x402 micropayments (HTTP 402 → sign → retry)
• ready for policy wallets & NEAR Intents

Built for #NEARHackathon

https://github.com/petopen9-stack/nearaction
```
