# FlowMint — NEAR HACKATHON 2026

## Track
**Primary:** Agent Economy  
**Secondary:** AI Security & Defense · Autonomous Business

## One-liner
Durable agent workflows with human/policy gates, verifiable receipts, and native **x402** micropayments — so agents can pay for APIs without losing state or draining funds.

## Demo for judges (no network)

```bash
git clone https://github.com/petopen9-stack/flowmint.git
cd flowmint
pip install -e .
flowmint demo
```

Expected: create → gates → x402 mock challenge → confirm → receipt chain with `x402_challenged` → anchor root.

Details: [DEMO.md](./DEMO.md)

## Ecosystem alignment ([nearbuilders.org/build](https://nearbuilders.org/build))

- **Agentic Commerce / NEAR Intents** — payment steps designed to plug into Intents + Agent Connect later  
- **x402** — first-class HTTP 402 flow; NEAR already supported in x402 ecosystem  
- **NEAR AI** — tools/skill ready for agents running on NEAR AI Cloud / IronClaw  
- **Security** — money steps default to `waiting_approval`; receipt chain for audit  

## Submission checklist
- [x] Public repo: https://github.com/petopen9-stack/flowmint  
- [ ] Demo post on X (tag @NEARProtocol #NEARHackathon) — use caption in DEMO.md  
- [ ] Submit form with repo + X post + NEAR payout address  
- [ ] Preferred track: Agent Economy  

## Do X, see Y

1. `flowmint demo` → full offline flow completes  
2. `flowmint history <id>` → see `created`, `x402_challenged`, `step_completed`, `completed`  
3. `flowmint anchor <id>` → `root_hash` ready for NEAR  
4. Restart shell, `flowmint status <id>` → state still there (`~/.flowmint/`)  
