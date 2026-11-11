# NearAction — NEAR HACKATHON 2026 notes

## Track preference
- Primary: **Agent Economy**
- Secondary: **AI Security & Defense** / **Autonomous Business**

## What we built
A lightweight but complete durable-execution layer for agents:

1. Local-first durable actions with checkpoints and resume
2. Explicit human-approval gates
3. SHA-256 hash-chained receipts + optional NEAR anchor
4. First-class `type: payment` steps
5. **Native x402 support** (`nearaction_x402_challenge` / `confirm`) so agents can pay for HTTP resources under policy

## How to try it (judges)

```bash
git clone https://github.com/petopen9-stack/nearaction.git
cd nearaction
pip install -e .

nearaction create --file examples/x402-api-call.yaml
nearaction resume <id>
nearaction status <id>
nearaction history <id>
```

Simulate a 402 by calling the tool layer with a sample challenge body (see `nearaction/x402.py` and the tools).  
Every transition is written into the receipt chain under `~/.nearaction/`.

## Why it matters
Agents that can hold and move money need:
1. **Durability** — the workflow must not vanish
2. **Policy control** — the agent must not be able to drain funds
3. **Standard payment rails** — x402 is the emerging open standard for agent micropayments over HTTP

NearAction delivers (1) + (3) today and is explicitly structured for (2).

NEAR already participates in the x402 ecosystem (`@x402/near`, market.near.ai, …).  
This project makes those payments **durable, gated, and auditable**.
