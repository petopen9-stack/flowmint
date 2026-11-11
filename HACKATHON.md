# NearAction — NEAR HACKATHON 2026 notes

## Track preference
- Primary: **Agent Economy**
- Secondary: **AI Security & Defense** / **Autonomous Business**

## What we built
A lightweight but complete durable-execution layer for agents:

1. Local-first durable actions with checkpoints and resume
2. Explicit human-approval gates
3. SHA-256 hash-chained receipts
4. Optional on-chain anchor preparation (receipt root)
5. First-class `type: payment` steps designed to plug into a policy wallet + NEAR Intents

## How to try it (judges)

```bash
git clone https://github.com/petopen9-stack/nearaction.git
cd nearaction
pip install -e .

nearaction create --file examples/research-digest.yaml
# note the action_id

nearaction resume <id>
nearaction status <id>
nearaction approve <id> --note "demo approval"
nearaction history <id>
nearaction anchor <id>
```

Expected results:
- Action is created and stored under `~/.nearaction/actions/`
- Status moves pending → running → waiting_approval → completed
- Every transition has a receipt; `history` shows the chain
- `anchor` prepares a root hash ready for NEAR submission

## Why it matters for the agent economy
Agents that can hold and move money need two things:
1. **Durability** — the workflow itself must not vanish
2. **Policy control** — the agent must not be able to drain funds

NearAction delivers (1) today and is explicitly structured for (2).

## Future (already stubbed)
- Real policy wallet contract (function-call key + limits + velocity)
- Direct NEAR Intents execution inside payment steps
- Full on-chain action state for multi-agent coordination
